-- ============================================================
-- PRIORITY QUEUES: POSTGRESQL SCHEDULING AND SELECTION SYSTEM
-- PostgreSQL 15+
--
-- Features:
-- 1. Min-priority and max-priority queue retrieval.
-- 2. Stable priority-based scheduling.
-- 3. Task lifecycle management.
-- 4. Priority updates and cancellation.
-- 5. Concurrent task claiming with SKIP LOCKED.
-- 6. Retry and failure handling.
-- 7. Priority policies and queue reporting.
-- 8. Top-K and K-th element selection.
-- 9. Running median through ordered-set calculations.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS priority_lab;

SET search_path TO priority_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE task_status AS ENUM (
    'pending',
    'running',
    'completed',
    'cancelled',
    'failed'
);

CREATE TYPE priority_mode AS ENUM (
    'min',
    'max'
);

CREATE TYPE task_category AS ENUM (
    'build',
    'test',
    'security_scan',
    'deployment',
    'report'
);

-- ------------------------------------------------------------
-- 2. REPOSITORY AND WORKER TABLES
-- ------------------------------------------------------------

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name VARCHAR(150) NOT NULL UNIQUE,
    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(default_branch)) > 0)
);

CREATE TABLE workers (
    worker_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    worker_name VARCHAR(100) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    max_concurrent_tasks INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(worker_name)) > 0),
    CHECK (max_concurrent_tasks > 0)
);

-- ------------------------------------------------------------
-- 3. PRIORITY POLICY
-- ------------------------------------------------------------

CREATE TABLE scheduling_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL UNIQUE,
    mode priority_mode NOT NULL,
    minimum_priority INTEGER NOT NULL DEFAULT 0,
    maximum_priority INTEGER NOT NULL DEFAULT 100,
    maximum_attempts INTEGER NOT NULL DEFAULT 3,
    retry_delay_seconds INTEGER NOT NULL DEFAULT 30,
    allow_deployment BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (minimum_priority <= maximum_priority),
    CHECK (maximum_attempts > 0),
    CHECK (retry_delay_seconds >= 0)
);

-- ------------------------------------------------------------
-- 4. TASK QUEUE
-- ------------------------------------------------------------

CREATE TABLE tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id),

    policy_id BIGINT NOT NULL
        REFERENCES scheduling_policies(policy_id),

    category task_category NOT NULL,

    task_name VARCHAR(200) NOT NULL,

    priority INTEGER NOT NULL,

    status task_status NOT NULL DEFAULT 'pending',

    retry_count INTEGER NOT NULL DEFAULT 0,

    max_attempts INTEGER NOT NULL DEFAULT 3,

    available_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    claimed_by BIGINT REFERENCES workers(worker_id),

    version INTEGER NOT NULL DEFAULT 0,

    last_error TEXT,

    CHECK (length(trim(task_name)) > 0),
    CHECK (retry_count >= 0),
    CHECK (max_attempts > 0),
    CHECK (version >= 0),

    CHECK (
        (status = 'running' AND claimed_by IS NOT NULL)
        OR
        (status <> 'running' AND claimed_by IS NULL)
    ),

    CHECK (
        (status IN ('completed', 'failed')
            AND completed_at IS NOT NULL)
        OR
        (status NOT IN ('completed', 'failed'))
    )
);

-- ------------------------------------------------------------
-- 5. TASK EXECUTION HISTORY
-- ------------------------------------------------------------

CREATE TABLE task_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    task_id BIGINT NOT NULL REFERENCES tasks(task_id),

    event_type VARCHAR(50) NOT NULL,

    worker_id BIGINT REFERENCES workers(worker_id),

    event_details JSONB NOT NULL DEFAULT '{}'::JSONB,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(event_type)) > 0)
);

-- ------------------------------------------------------------
-- 6. TASK VALUE SAMPLES FOR SELECTION PROBLEMS
-- ------------------------------------------------------------

CREATE TABLE numeric_samples (
    sample_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sample_group VARCHAR(100) NOT NULL,
    sample_value NUMERIC(18, 4) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(sample_group)) > 0)
);

-- ------------------------------------------------------------
-- 7. PERFORMANCE INDEXES
-- ------------------------------------------------------------

-- Max-priority scheduling: highest priority first.
CREATE INDEX idx_tasks_max_priority
ON tasks (
    priority DESC,
    submitted_at ASC,
    task_id ASC
)
WHERE status = 'pending';

-- Min-priority scheduling: lowest priority first.
CREATE INDEX idx_tasks_min_priority
ON tasks (
    priority ASC,
    submitted_at ASC,
    task_id ASC
)
WHERE status = 'pending';

-- Queue filtering by repository and state.
CREATE INDEX idx_tasks_repository_status
ON tasks(repository_id, status);

-- Efficient delayed-task retrieval.
CREATE INDEX idx_tasks_available
ON tasks(available_at)
WHERE status = 'pending';

-- Worker execution history.
CREATE INDEX idx_task_events_history
ON task_events(task_id, occurred_at DESC);

CREATE INDEX idx_numeric_samples_group_value
ON numeric_samples(sample_group, sample_value);

-- ------------------------------------------------------------
-- 8. AUTOMATIC TASK EVENT RECORDING
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION record_task_state_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO task_events(
            task_id,
            event_type,
            event_details
        )
        VALUES (
            NEW.task_id,
            'submitted',
            jsonb_build_object(
                'priority', NEW.priority,
                'category', NEW.category,
                'task_name', NEW.task_name
            )
        );

        RETURN NEW;
    END IF;

    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO task_events(
            task_id,
            event_type,
            worker_id,
            event_details
        )
        VALUES (
            NEW.task_id,
            'status_changed',
            NEW.claimed_by,
            jsonb_build_object(
                'old_status', OLD.status,
                'new_status', NEW.status,
                'priority', NEW.priority
            )
        );
    END IF;

    IF OLD.priority IS DISTINCT FROM NEW.priority THEN
        INSERT INTO task_events(
            task_id,
            event_type,
            event_details
        )
        VALUES (
            NEW.task_id,
            'priority_updated',
            jsonb_build_object(
                'old_priority', OLD.priority,
                'new_priority', NEW.priority
            )
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_task_events
AFTER INSERT OR UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION record_task_state_change();

-- ------------------------------------------------------------
-- 9. TASK VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_task_policy()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    selected_policy scheduling_policies%ROWTYPE;
    selected_repository_active BOOLEAN;
BEGIN
    SELECT *
    INTO selected_policy
    FROM scheduling_policies
    WHERE policy_id = NEW.policy_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Scheduling policy does not exist';
    END IF;

    IF NEW.priority < selected_policy.minimum_priority
       OR NEW.priority > selected_policy.maximum_priority THEN
        RAISE EXCEPTION
            'Priority % is outside policy limits [% - %]',
            NEW.priority,
            selected_policy.minimum_priority,
            selected_policy.maximum_priority;
    END IF;

    SELECT active
    INTO selected_repository_active
    FROM repositories
    WHERE repository_id = NEW.repository_id;

    IF NOT FOUND OR NOT selected_repository_active THEN
        RAISE EXCEPTION 'Repository does not exist or is inactive';
    END IF;

    IF NEW.category = 'deployment'
       AND NOT selected_policy.allow_deployment THEN
        RAISE EXCEPTION 'Deployment tasks are disabled by policy';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_task_policy
BEFORE INSERT OR UPDATE OF
    priority,
    policy_id,
    repository_id,
    category
ON tasks
FOR EACH ROW
EXECUTE FUNCTION validate_task_policy();

-- ------------------------------------------------------------
-- 10. POLICY-AWARE QUEUE RETRIEVAL
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_priority_queue(
    requested_policy BIGINT,
    requested_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    result_task_id BIGINT,
    result_task_name VARCHAR,
    result_priority INTEGER,
    result_status task_status,
    result_category task_category
)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_mode priority_mode;
BEGIN
    IF requested_limit <= 0 OR requested_limit > 10000 THEN
        RAISE EXCEPTION 'Limit must be between 1 and 10000';
    END IF;

    SELECT mode
    INTO selected_mode
    FROM scheduling_policies
    WHERE policy_id = requested_policy;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown scheduling policy';
    END IF;

    IF selected_mode = 'min' THEN
        RETURN QUERY
        SELECT
            t.task_id,
            t.task_name::VARCHAR,
            t.priority,
            t.status,
            t.category
        FROM tasks t
        WHERE t.policy_id = requested_policy
          AND t.status = 'pending'
          AND t.available_at <= CURRENT_TIMESTAMP
        ORDER BY
            t.priority ASC,
            t.submitted_at ASC,
            t.task_id ASC
        LIMIT requested_limit;
    ELSE
        RETURN QUERY
        SELECT
            t.task_id,
            t.task_name::VARCHAR,
            t.priority,
            t.status,
            t.category
        FROM tasks t
        WHERE t.policy_id = requested_policy
          AND t.status = 'pending'
          AND t.available_at <= CURRENT_TIMESTAMP
        ORDER BY
            t.priority DESC,
            t.submitted_at ASC,
            t.task_id ASC
        LIMIT requested_limit;
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 11. ATOMIC TASK CLAIMING
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION claim_next_task(
    requested_policy BIGINT,
    requested_worker BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    selected_mode priority_mode;
    selected_task BIGINT;
BEGIN
    -- Lock policy and worker rows against concurrent changes.
    SELECT mode
    INTO selected_mode
    FROM scheduling_policies
    WHERE policy_id = requested_policy
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown policy';
    END IF;

    PERFORM 1
    FROM workers
    WHERE worker_id = requested_worker
      AND active = TRUE
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Worker is unavailable';
    END IF;

    IF selected_mode = 'min' THEN
        SELECT task_id
        INTO selected_task
        FROM tasks
        WHERE policy_id = requested_policy
          AND status = 'pending'
          AND available_at <= CURRENT_TIMESTAMP
        ORDER BY
            priority ASC,
            submitted_at ASC,
            task_id ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED;
    ELSE
        SELECT task_id
        INTO selected_task
        FROM tasks
        WHERE policy_id = requested_policy
          AND status = 'pending'
          AND available_at <= CURRENT_TIMESTAMP
        ORDER BY
            priority DESC,
            submitted_at ASC,
            task_id ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED;
    END IF;

    IF selected_task IS NULL THEN
        RETURN NULL;
    END IF;

    UPDATE tasks
    SET
        status = 'running',
        claimed_by = requested_worker,
        started_at = CURRENT_TIMESTAMP,
        completed_at = NULL
    WHERE task_id = selected_task;

    RETURN selected_task;
END;
$$;

-- ------------------------------------------------------------
-- 12. TASK COMPLETION
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE finish_task(
    requested_task BIGINT,
    execution_success BOOLEAN,
    failure_message TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_task tasks%ROWTYPE;
    selected_policy scheduling_policies%ROWTYPE;
BEGIN
    SELECT *
    INTO selected_task
    FROM tasks
    WHERE task_id = requested_task
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown task';
    END IF;

    IF selected_task.status <> 'running' THEN
        RAISE EXCEPTION 'Task is not running';
    END IF;

    SELECT *
    INTO selected_policy
    FROM scheduling_policies
    WHERE policy_id = selected_task.policy_id;

    IF execution_success THEN
        UPDATE tasks
        SET
            status = 'completed',
            claimed_by = NULL,
            completed_at = CURRENT_TIMESTAMP,
            last_error = NULL
        WHERE task_id = requested_task;
    ELSE
        IF selected_task.retry_count + 1
           < LEAST(
                selected_task.max_attempts,
                selected_policy.maximum_attempts
           ) THEN

            UPDATE tasks
            SET
                status = 'pending',
                claimed_by = NULL,
                retry_count = retry_count + 1,
                available_at = CURRENT_TIMESTAMP
                    + make_interval(
                        secs => selected_policy.retry_delay_seconds
                    ),
                last_error = failure_message
            WHERE task_id = requested_task;
        ELSE
            UPDATE tasks
            SET
                status = 'failed',
                claimed_by = NULL,
                completed_at = CURRENT_TIMESTAMP,
                retry_count = retry_count + 1,
                last_error = failure_message
            WHERE task_id = requested_task;
        END IF;
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 13. TOP-K AND K-TH ELEMENT QUERIES
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_top_k_values(
    requested_group VARCHAR,
    requested_k INTEGER
)
RETURNS TABLE (
    selected_value NUMERIC,
    selection_rank BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF requested_k <= 0 THEN
        RAISE EXCEPTION 'k must be positive';
    END IF;

    RETURN QUERY
    SELECT
        s.sample_value,
        ROW_NUMBER() OVER (
            ORDER BY s.sample_value DESC, s.sample_id ASC
        )
    FROM numeric_samples s
    WHERE s.sample_group = requested_group
    ORDER BY s.sample_value DESC, s.sample_id ASC
    LIMIT requested_k;
END;
$$;

CREATE OR REPLACE FUNCTION get_kth_smallest(
    requested_group VARCHAR,
    requested_k INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    selected_value NUMERIC;
BEGIN
    IF requested_k <= 0 THEN
        RAISE EXCEPTION 'k must be positive';
    END IF;

    SELECT sample_value
    INTO selected_value
    FROM numeric_samples
    WHERE sample_group = requested_group
    ORDER BY sample_value ASC, sample_id ASC
    OFFSET requested_k - 1
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'k exceeds available observations';
    END IF;

    RETURN selected_value;
END;
$$;

-- ------------------------------------------------------------
-- 14. REPORTING VIEWS
-- ------------------------------------------------------------

CREATE VIEW queue_summary AS
SELECT
    r.repository_name,
    p.policy_name,
    p.mode,
    t.status,
    COUNT(*) AS task_count,
    AVG(t.priority)::NUMERIC(10, 2) AS average_priority
FROM tasks t
JOIN repositories r
    ON r.repository_id = t.repository_id
JOIN scheduling_policies p
    ON p.policy_id = t.policy_id
GROUP BY
    r.repository_name,
    p.policy_name,
    p.mode,
    t.status;

CREATE VIEW worker_activity AS
SELECT
    w.worker_id,
    w.worker_name,
    COUNT(t.task_id) AS total_claimed,
    COUNT(*) FILTER (
        WHERE t.status = 'completed'
    ) AS completed,
    COUNT(*) FILTER (
        WHERE t.status = 'failed'
    ) AS failed,
    COUNT(*) FILTER (
        WHERE t.status = 'running'
    ) AS running
FROM workers w
LEFT JOIN tasks t
    ON t.claimed_by = w.worker_id
    OR EXISTS (
        SELECT 1
        FROM task_events e
        WHERE e.task_id = t.task_id
          AND e.worker_id = w.worker_id
    )
GROUP BY w.worker_id, w.worker_name;

-- ------------------------------------------------------------
-- 15. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO repositories(repository_name, default_branch)
VALUES
    ('portfolio-manager', 'main'),
    ('security-platform', 'main'),
    ('analytics-engine', 'develop');

INSERT INTO workers(worker_name, max_concurrent_tasks)
VALUES
    ('worker-build-01', 3),
    ('worker-security-01', 2),
    ('worker-deployment-01', 1);

INSERT INTO scheduling_policies(
    policy_name,
    mode,
    minimum_priority,
    maximum_priority,
    maximum_attempts,
    retry_delay_seconds,
    allow_deployment
)
VALUES
    ('Production High First', 'max', 0, 100, 3, 10, TRUE),
    ('Maintenance Low First', 'min', 0, 100, 2, 5, FALSE);

INSERT INTO tasks(
    repository_id,
    policy_id,
    category,
    task_name,
    priority
)
VALUES
    (1, 1, 'build', 'Compile portfolio manager', 50),
    (1, 1, 'security_scan', 'Dependency vulnerability scan', 95),
    (1, 1, 'test', 'Integration test suite', 70),
    (1, 1, 'deployment', 'Production deployment', 90),
    (2, 1, 'security_scan', 'Security compliance audit', 100),
    (2, 1, 'report', 'Generate security report', 30),
    (3, 2, 'report', 'Generate analytics report', 10),
    (3, 2, 'test', 'Run analytics regression tests', 20);

INSERT INTO numeric_samples(sample_group, sample_value)
VALUES
    ('latency', 17),
    ('latency', 4),
    ('latency', 29),
    ('latency', 11),
    ('latency', 8),
    ('latency', 35),
    ('latency', 21),
    ('latency', 3),
    ('latency', 29);

-- ------------------------------------------------------------
-- 16. RETRIEVAL EXAMPLES
-- ------------------------------------------------------------

-- Max-priority queue.
SELECT *
FROM get_priority_queue(1, 10);

-- Min-priority queue.
SELECT *
FROM get_priority_queue(2, 10);

-- Highest-priority tasks.
SELECT
    task_id,
    task_name,
    priority
FROM tasks
WHERE status = 'pending'
ORDER BY priority DESC, submitted_at ASC
LIMIT 5;

-- Lowest-priority tasks.
SELECT
    task_id,
    task_name,
    priority
FROM tasks
WHERE status = 'pending'
ORDER BY priority ASC, submitted_at ASC
LIMIT 5;

-- ------------------------------------------------------------
-- 17. TRANSACTIONAL WORKFLOW
-- ------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    claimed_task BIGINT;
BEGIN
    claimed_task := claim_next_task(1, 2);

    IF claimed_task IS NOT NULL THEN
        RAISE NOTICE 'Claimed task: %', claimed_task;

        CALL finish_task(
            claimed_task,
            TRUE,
            NULL
        );
    ELSE
        RAISE NOTICE 'No eligible task available';
    END IF;
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- 18. FAILURE AND RETRY EXAMPLE
-- ------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    claimed_task BIGINT;
BEGIN
    claimed_task := claim_next_task(1, 1);

    IF claimed_task IS NOT NULL THEN
        CALL finish_task(
            claimed_task,
            FALSE,
            'Simulated build infrastructure failure'
        );
    END IF;
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- 19. AGGREGATION AND REPORTING
-- ------------------------------------------------------------

SELECT *
FROM queue_summary
ORDER BY repository_name, policy_name, status;

SELECT *
FROM worker_activity
ORDER BY worker_name;

SELECT
    status,
    COUNT(*) AS total_tasks,
    AVG(priority)::NUMERIC(10, 2) AS average_priority,
    MAX(priority) AS highest_priority,
    MIN(priority) AS lowest_priority
FROM tasks
GROUP BY status
ORDER BY status;

-- ------------------------------------------------------------
-- 20. TOP-K SELECTION
-- ------------------------------------------------------------

SELECT *
FROM get_top_k_values('latency', 3);

SELECT get_kth_smallest('latency', 3)
AS third_smallest_latency;

-- ------------------------------------------------------------
-- 21. RUNNING MEDIAN AND DISTRIBUTION
-- ------------------------------------------------------------

SELECT
    sample_group,
    percentile_cont(0.5)
        WITHIN GROUP (ORDER BY sample_value) AS median_value,
    AVG(sample_value) AS average_value,
    MIN(sample_value) AS minimum_value,
    MAX(sample_value) AS maximum_value,
    COUNT(*) AS observation_count
FROM numeric_samples
GROUP BY sample_group;

-- ------------------------------------------------------------
-- 22. VALIDATION QUERIES
-- ------------------------------------------------------------

-- Tasks with excessive retries.
SELECT
    task_id,
    task_name,
    retry_count,
    max_attempts
FROM tasks
WHERE retry_count >= max_attempts;

-- Pending tasks that are delayed.
SELECT
    task_id,
    task_name,
    available_at
FROM tasks
WHERE status = 'pending'
  AND available_at > CURRENT_TIMESTAMP
ORDER BY available_at;

-- Failed tasks requiring investigation.
SELECT
    task_id,
    task_name,
    last_error
FROM tasks
WHERE status = 'failed';

-- Execution event history.
SELECT
    t.task_name,
    e.event_type,
    e.event_details,
    e.occurred_at
FROM task_events e
JOIN tasks t ON t.task_id = e.task_id
ORDER BY e.occurred_at DESC;

COMMIT;
