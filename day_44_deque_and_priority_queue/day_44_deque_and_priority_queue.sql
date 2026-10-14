-- PostgreSQL 14+.
-- Model deque intake, stable min/max priority queues, and queue processing.

DROP SCHEMA IF EXISTS queue_lab CASCADE;
CREATE SCHEMA queue_lab;
SET search_path TO queue_lab, public;

CREATE TYPE work_status AS ENUM (
    'queued',
    'in_progress',
    'completed',
    'cancelled'
);

CREATE TYPE queue_direction AS ENUM (
    'min_priority_first',
    'max_priority_first',
    'deque_front',
    'deque_back'
);

CREATE TABLE work_item (
    work_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket VARCHAR(30) NOT NULL UNIQUE,
    repository_name VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL CHECK (priority BETWEEN 0 AND 100),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status work_status NOT NULL DEFAULT 'queued',
    CHECK (length(trim(ticket)) > 0),
    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(description)) > 0)
);

CREATE TABLE queue_entry (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    work_id BIGINT NOT NULL REFERENCES work_item(work_id),
    direction queue_direction NOT NULL,
    enqueue_sequence BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE,
    enqueued_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

-- The same work item can be represented in different queue policies.
-- Within one queue, a work item can have only one active entry.
CREATE UNIQUE INDEX uq_active_work_queue
    ON queue_entry(work_id, direction)
    WHERE active;

CREATE INDEX ix_active_queue_sequence
    ON queue_entry(direction, enqueue_sequence)
    WHERE active;

CREATE INDEX ix_work_queued_priority
    ON work_item(priority, submitted_at, work_id)
    WHERE status = 'queued';

CREATE TABLE queue_event (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    work_id BIGINT NOT NULL REFERENCES work_item(work_id),
    event_type TEXT NOT NULL CHECK (
        event_type IN (
            'submitted', 'enqueued_front', 'enqueued_back',
            'dispatched', 'cancelled'
        )
    ),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION validate_work_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = OLD.status THEN
        RETURN NEW;
    END IF;

    IF OLD.status = 'queued'
       AND NEW.status IN ('in_progress', 'cancelled') THEN
        RETURN NEW;
    END IF;

    IF OLD.status = 'in_progress'
       AND NEW.status IN ('completed', 'cancelled') THEN
        RETURN NEW;
    END IF;

    RAISE EXCEPTION 'Invalid work status transition: % -> %',
        OLD.status, NEW.status;
END;
$$;

CREATE TRIGGER trg_validate_work_status_transition
BEFORE UPDATE OF status ON work_item
FOR EACH ROW
EXECUTE FUNCTION validate_work_status_transition();

CREATE OR REPLACE FUNCTION log_work_submission()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO queue_event(work_id, event_type, details)
    VALUES (
        NEW.work_id,
        'submitted',
        jsonb_build_object(
            'ticket', NEW.ticket,
            'priority', NEW.priority,
            'repository', NEW.repository_name
        )
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_log_work_submission
AFTER INSERT ON work_item
FOR EACH ROW
EXECUTE FUNCTION log_work_submission();

CREATE OR REPLACE FUNCTION enqueue_work(
    p_ticket VARCHAR,
    p_direction queue_direction
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_work_id BIGINT;
    v_event_type TEXT;
BEGIN
    SELECT work_id
      INTO v_work_id
      FROM work_item
     WHERE ticket = p_ticket
       AND status = 'queued'
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Ticket % does not exist or is not queued', p_ticket;
    END IF;

    INSERT INTO queue_entry(work_id, direction)
    VALUES (v_work_id, p_direction);

    v_event_type := CASE p_direction
        WHEN 'deque_front' THEN 'enqueued_front'
        WHEN 'deque_back' THEN 'enqueued_back'
        ELSE 'submitted'
    END;

    INSERT INTO queue_event(work_id, event_type, details)
    VALUES (
        v_work_id,
        v_event_type,
        jsonb_build_object('direction', p_direction)
    );

    RETURN v_work_id;
END;
$$;

CREATE OR REPLACE FUNCTION dispatch_next(
    p_direction queue_direction
)
RETURNS TABLE (
    dispatched_work_id BIGINT,
    dispatched_ticket VARCHAR,
    dispatched_priority INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_entry_id BIGINT;
    v_work_id BIGINT;
    v_ticket VARCHAR(30);
    v_priority INTEGER;
BEGIN
    IF p_direction NOT IN (
        'min_priority_first', 'max_priority_first',
        'deque_front', 'deque_back'
    ) THEN
        RAISE EXCEPTION 'Unsupported queue direction: %', p_direction;
    END IF;

    -- FOR UPDATE SKIP LOCKED lets concurrent workers claim different entries.
    -- Queue ordering and row locking occur in the same transaction.
    SELECT qe.entry_id, wi.work_id, wi.ticket, wi.priority
      INTO v_entry_id, v_work_id, v_ticket, v_priority
      FROM queue_entry qe
      JOIN work_item wi ON wi.work_id = qe.work_id
     WHERE qe.direction = p_direction
       AND qe.active
       AND wi.status = 'queued'
     ORDER BY
       CASE
         WHEN p_direction = 'min_priority_first' THEN wi.priority
         ELSE NULL
       END ASC,
       CASE
         WHEN p_direction = 'max_priority_first' THEN wi.priority
         ELSE NULL
       END DESC,
       CASE
         WHEN p_direction = 'deque_front' THEN qe.enqueue_sequence
         ELSE NULL
       END ASC,
       CASE
         WHEN p_direction = 'deque_back' THEN qe.enqueue_sequence
         ELSE NULL
       END DESC,
       qe.enqueue_sequence ASC
     FOR UPDATE OF qe, wi SKIP LOCKED
     LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No queued work available in %', p_direction;
    END IF;

    UPDATE queue_entry
       SET active = FALSE
     WHERE entry_id = v_entry_id;

    UPDATE work_item
       SET status = 'in_progress'
     WHERE work_id = v_work_id;

    INSERT INTO queue_event(work_id, event_type, details)
    VALUES (
        v_work_id,
        'dispatched',
        jsonb_build_object(
            'direction', p_direction,
            'priority', v_priority
        )
    );

    dispatched_work_id := v_work_id;
    dispatched_ticket := v_ticket;
    dispatched_priority := v_priority;
    RETURN NEXT;
END;
$$;

INSERT INTO work_item(ticket, repository_name, description, priority)
VALUES
    ('PR-501', 'payment-service', 'Investigate payment outage', 100),
    ('PR-502', 'identity-service', 'Repair token validation', 85),
    ('PR-503', 'documentation', 'Clarify deployment guide', 10),
    ('PR-504', 'database-service', 'Investigate connection saturation', 85),
    ('PR-505', 'platform', 'Rotate service credentials', 95);

-- Populate independent queue representations for policy comparisons.
SELECT enqueue_work('PR-501', 'deque_back');
SELECT enqueue_work('PR-502', 'deque_back');
SELECT enqueue_work('PR-503', 'deque_front');
SELECT enqueue_work('PR-504', 'deque_back');
SELECT enqueue_work('PR-505', 'deque_back');

SELECT enqueue_work('PR-501', 'min_priority_first');
SELECT enqueue_work('PR-502', 'min_priority_first');
SELECT enqueue_work('PR-503', 'min_priority_first');
SELECT enqueue_work('PR-504', 'min_priority_first');
SELECT enqueue_work('PR-505', 'min_priority_first');

SELECT enqueue_work('PR-501', 'max_priority_first');
SELECT enqueue_work('PR-502', 'max_priority_first');
SELECT enqueue_work('PR-503', 'max_priority_first');
SELECT enqueue_work('PR-504', 'max_priority_first');
SELECT enqueue_work('PR-505', 'max_priority_first');

-- Inspect priority order without consuming any entries.
SELECT wi.ticket, wi.priority, qe.direction, qe.enqueue_sequence
FROM queue_entry qe
JOIN work_item wi ON wi.work_id = qe.work_id
WHERE qe.active
ORDER BY qe.direction, wi.priority DESC, qe.enqueue_sequence;

-- A min-priority queue treats the lowest numeric value as the first item.
SELECT wi.ticket, wi.priority
FROM queue_entry qe
JOIN work_item wi ON wi.work_id = qe.work_id
WHERE qe.direction = 'min_priority_first'
  AND qe.active
ORDER BY wi.priority ASC, qe.enqueue_sequence ASC;

-- A max-priority queue dispatches the highest numeric value first.
SELECT wi.ticket, wi.priority
FROM queue_entry qe
JOIN work_item wi ON wi.work_id = qe.work_id
WHERE qe.direction = 'max_priority_first'
  AND qe.active
ORDER BY wi.priority DESC, qe.enqueue_sequence ASC;

-- Deque ordering is determined by the selected end, not by work priority.
SELECT wi.ticket, wi.priority, qe.enqueue_sequence
FROM queue_entry qe
JOIN work_item wi ON wi.work_id = qe.work_id
WHERE qe.direction = 'deque_front'
  AND qe.active
ORDER BY qe.enqueue_sequence ASC;

BEGIN;
SELECT * FROM dispatch_next('max_priority_first');
COMMIT;

-- The trigger rejects illegal transitions, such as returning completed work
-- to the queued state. Execute separately to observe the expected error.
-- UPDATE work_item SET status = 'queued' WHERE ticket = 'PR-501';

-- The unique partial index prevents duplicate active entries for the same
-- work item and queue policy. The check constraint rejects priority 101.
-- Both are database-level integrity rules, not application conventions.

SELECT event_type, count(*) AS event_count
FROM queue_event
GROUP BY event_type
ORDER BY event_type;

CREATE OR REPLACE VIEW active_queue_summary AS
SELECT
    qe.direction,
    count(*) AS active_entries,
    min(wi.priority) AS minimum_priority,
    max(wi.priority) AS maximum_priority,
    avg(wi.priority)::numeric(8, 2) AS average_priority
FROM queue_entry qe
JOIN work_item wi ON wi.work_id = qe.work_id
WHERE qe.active
GROUP BY qe.direction;

SELECT * FROM active_queue_summary ORDER BY direction;
