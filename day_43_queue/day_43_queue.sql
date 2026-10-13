-- PostgreSQL 15+
-- Queue operations and an auditable FIFO work-processing model.
--
-- The queue order is represented by monotonically increasing queue_sequence.
-- A sequence provides unique ordering values, but sequence gaps are normal:
-- PostgreSQL sequences are not rolled back when a transaction aborts.
-- FOR UPDATE SKIP LOCKED is used by workers to avoid claiming the same
-- pending job concurrently.

BEGIN;

DROP VIEW IF EXISTS queue_overview;
DROP TABLE IF EXISTS queue_event CASCADE;
DROP TABLE IF EXISTS queue_job CASCADE;
DROP SEQUENCE IF EXISTS queue_order_sequence;

CREATE SEQUENCE queue_order_sequence AS BIGINT START WITH 1;

CREATE TABLE queue_job (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    queue_sequence BIGINT NOT NULL
        DEFAULT nextval('queue_order_sequence'),
    job_type TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    source_branch TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failure_reason TEXT,

    CONSTRAINT queue_job_sequence_unique UNIQUE (queue_sequence),
    CONSTRAINT queue_job_type_nonempty CHECK (length(trim(job_type)) > 0),
    CONSTRAINT queue_repository_nonempty CHECK (
        length(trim(repository_name)) > 0
    ),
    CONSTRAINT queue_branch_nonempty CHECK (
        length(trim(source_branch)) > 0
    ),
    CONSTRAINT queue_commit_nonempty CHECK (
        length(trim(commit_sha)) > 0
    ),
    CONSTRAINT queue_status_valid CHECK (
        status IN ('queued', 'running', 'completed', 'failed')
    ),
    CONSTRAINT queue_completion_consistent CHECK (
        (status IN ('queued', 'running') AND completed_at IS NULL)
        OR
        (status IN ('completed', 'failed') AND completed_at IS NOT NULL)
    ),
    CONSTRAINT queue_start_consistent CHECK (
        status = 'queued' OR started_at IS NOT NULL
    ),
    CONSTRAINT queue_failure_consistent CHECK (
        (status = 'failed' AND failure_reason IS NOT NULL)
        OR
        (status <> 'failed' AND failure_reason IS NULL)
    )
);

CREATE TABLE queue_event (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES queue_job(job_id),
    event_type TEXT NOT NULL,
    old_status TEXT,
    new_status TEXT,
    event_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    details TEXT,

    CONSTRAINT queue_event_type_nonempty CHECK (
        length(trim(event_type)) > 0
    )
);

-- This partial index supports FIFO dequeue queries without scanning
-- completed work. queue_sequence gives deterministic ordering.
CREATE INDEX queue_pending_fifo_idx
    ON queue_job (queue_sequence)
    WHERE status = 'queued';

CREATE INDEX queue_event_job_time_idx
    ON queue_event (job_id, event_at DESC);

CREATE OR REPLACE FUNCTION record_queue_event()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO queue_event (
            job_id, event_type, old_status, new_status, details
        )
        VALUES (
            NEW.job_id, 'enqueued', NULL, NEW.status,
            NEW.job_type || ' for ' || NEW.repository_name
        );

        RETURN NEW;
    END IF;

    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO queue_event (
            job_id, event_type, old_status, new_status, details
        )
        VALUES (
            NEW.job_id,
            'status_changed',
            OLD.status,
            NEW.status,
            COALESCE(NEW.failure_reason, 'State transition')
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER queue_job_audit_trigger
AFTER INSERT OR UPDATE OF status ON queue_job
FOR EACH ROW
EXECUTE FUNCTION record_queue_event();

CREATE OR REPLACE FUNCTION enqueue_job(
    p_job_type TEXT,
    p_repository_name TEXT,
    p_source_branch TEXT,
    p_commit_sha TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_job_id BIGINT;
BEGIN
    INSERT INTO queue_job (
        job_type, repository_name, source_branch, commit_sha
    )
    VALUES (
        p_job_type, p_repository_name, p_source_branch, p_commit_sha
    )
    RETURNING job_id INTO new_job_id;

    RETURN new_job_id;
END;
$$;

CREATE OR REPLACE FUNCTION dequeue_job()
RETURNS TABLE (
    claimed_job_id BIGINT,
    claimed_job_type TEXT,
    claimed_repository TEXT,
    claimed_branch TEXT,
    claimed_commit TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Claim the oldest queued job atomically. SKIP LOCKED lets another
    -- worker claim a different job instead of waiting on this row.
    RETURN QUERY
    WITH next_job AS (
        SELECT q.job_id
        FROM queue_job AS q
        WHERE q.status = 'queued'
        ORDER BY q.queue_sequence
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    UPDATE queue_job AS q
    SET status = 'running',
        started_at = clock_timestamp()
    FROM next_job
    WHERE q.job_id = next_job.job_id
    RETURNING q.job_id, q.job_type, q.repository_name,
              q.source_branch, q.commit_sha;
END;
$$;

CREATE OR REPLACE FUNCTION complete_job(
    p_job_id BIGINT,
    p_succeeded BOOLEAN,
    p_failure_reason TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    IF p_succeeded IS NULL THEN
        RAISE EXCEPTION 'Success flag cannot be NULL';
    END IF;

    IF NOT p_succeeded
       AND NULLIF(trim(p_failure_reason), '') IS NULL THEN
        RAISE EXCEPTION 'A failure reason is required for failed jobs';
    END IF;

    UPDATE queue_job
    SET status = CASE WHEN p_succeeded THEN 'completed' ELSE 'failed' END,
        completed_at = clock_timestamp(),
        failure_reason = CASE
            WHEN p_succeeded THEN NULL
            ELSE trim(p_failure_reason)
        END
    WHERE job_id = p_job_id
      AND status = 'running';

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    IF affected_rows = 0 THEN
        RAISE EXCEPTION
            'Job % does not exist or is not running', p_job_id;
    END IF;
END;
$$;

CREATE VIEW queue_overview AS
SELECT
    COUNT(*) FILTER (WHERE status = 'queued') AS queued_count,
    COUNT(*) FILTER (WHERE status = 'running') AS running_count,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_count,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_count,
    MIN(queue_sequence) FILTER (WHERE status = 'queued') AS front_sequence,
    MAX(queue_sequence) FILTER (WHERE status = 'queued') AS rear_sequence
FROM queue_job;

-- Enqueue realistic repository validation jobs.
SELECT enqueue_job(
    'compile', 'payments-service', 'feature/retry-policy', 'a13f9c2'
);
SELECT enqueue_job(
    'unit-tests', 'payments-service', 'feature/retry-policy', 'a13f9c2'
);
SELECT enqueue_job(
    'security-scan', 'payments-service', 'feature/retry-policy', 'a13f9c2'
);

-- Front and Rear inspect the oldest and newest queued jobs without removing
-- them. Ordering by queue_sequence is explicit and deterministic.
SELECT job_id, job_type, queue_sequence
FROM queue_job
WHERE status = 'queued'
ORDER BY queue_sequence
LIMIT 1;

SELECT job_id, job_type, queue_sequence
FROM queue_job
WHERE status = 'queued'
ORDER BY queue_sequence DESC
LIMIT 1;

-- Inspect current counts before processing.
SELECT * FROM queue_overview;

-- Dequeue claims the oldest pending job and changes its state to running.
SELECT * FROM dequeue_job();

-- Complete a running job successfully.
SELECT complete_job(1, TRUE);

-- Claim and fail the next job with a meaningful failure reason.
SELECT * FROM dequeue_job();
SELECT complete_job(2, FALSE, 'Unit tests reported a regression.');

-- Inspect remaining jobs in FIFO order.
SELECT job_id, queue_sequence, job_type, status, failure_reason
FROM queue_job
ORDER BY queue_sequence;

-- Audit history shows enqueues and state transitions.
SELECT e.job_id, e.event_type, e.old_status, e.new_status,
       e.event_at, e.details
FROM queue_event AS e
ORDER BY e.event_id;

-- A job cannot be completed twice because complete_job requires running state.
-- To observe the rejection, run this statement separately:
-- SELECT complete_job(1, TRUE);

-- Database constraints reject invalid status values and inconsistent
-- completion timestamps. Application code should still validate inputs.
-- Direct production access to queue_job should be restricted so callers use
-- the functions and workers receive only the privileges they require.

COMMIT;
