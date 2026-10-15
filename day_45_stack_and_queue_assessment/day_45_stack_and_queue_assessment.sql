-- PostgreSQL 15+
-- Stack and queue assessment records, algorithm inputs, and executable queries.
-- The schema keeps FIFO scheduling, LIFO history, and algorithm assessments
-- distinct while storing their shared assessment results relationally.

BEGIN;

DROP VIEW IF EXISTS assessment_results;
DROP TABLE IF EXISTS algorithm_runs CASCADE;
DROP TABLE IF EXISTS algorithm_inputs CASCADE;
DROP TABLE IF EXISTS work_events CASCADE;
DROP TABLE IF EXISTS work_items CASCADE;
DROP TABLE IF EXISTS assessment_cases CASCADE;

CREATE TABLE assessment_cases (
    case_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK (
        category IN (
            'STACK',
            'QUEUE',
            'DEQUE',
            'PARENTHESES',
            'MONOTONIC_STACK',
            'NEXT_GREATER'
        )
    ),
    difficulty TEXT NOT NULL CHECK (
        difficulty IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')
    ),
    expected_complexity TEXT NOT NULL,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0)
);

CREATE TABLE algorithm_inputs (
    input_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_id BIGINT NOT NULL REFERENCES assessment_cases(case_id)
        ON DELETE CASCADE,
    input_values INTEGER[] NOT NULL DEFAULT '{}',
    window_size INTEGER,
    expression TEXT,
    expected_values INTEGER[],
    expected_boolean BOOLEAN,
    CHECK (
        window_size IS NULL OR window_size > 0
    )
);

CREATE TABLE algorithm_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    input_id BIGINT NOT NULL REFERENCES algorithm_inputs(input_id)
        ON DELETE CASCADE,
    actual_values INTEGER[],
    actual_boolean BOOLEAN,
    passed BOOLEAN NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    execution_ms NUMERIC(12, 3) NOT NULL CHECK (execution_ms >= 0),
    diagnostic TEXT
);

CREATE TABLE work_items (
    work_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_key TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    priority SMALLINT NOT NULL DEFAULT 0 CHECK (priority BETWEEN 0 AND 2),
    state TEXT NOT NULL DEFAULT 'QUEUED' CHECK (
        state IN ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED')
    ),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    CHECK (
        (state = 'RUNNING' AND started_at IS NOT NULL AND finished_at IS NULL)
        OR
        (state IN ('SUCCEEDED', 'FAILED', 'CANCELLED')
         AND finished_at IS NOT NULL)
        OR
        (state = 'QUEUED' AND finished_at IS NULL)
    )
);

CREATE TABLE work_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    work_id BIGINT NOT NULL REFERENCES work_items(work_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (
        event_type IN ('ENQUEUED', 'STARTED', 'SUCCEEDED', 'FAILED', 'CANCELLED')
    ),
    event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_algorithm_runs_case_time
    ON algorithm_runs (executed_at DESC, run_id);

CREATE INDEX idx_work_queue_fifo
    ON work_items (created_at, work_id)
    WHERE state = 'QUEUED';

CREATE INDEX idx_work_events_work_time
    ON work_events (work_id, event_time DESC);

CREATE VIEW assessment_results AS
SELECT
    c.case_name,
    c.category,
    c.difficulty,
    r.run_id,
    r.passed,
    r.execution_ms,
    r.diagnostic,
    r.executed_at
FROM assessment_cases AS c
JOIN algorithm_inputs AS i ON i.case_id = c.case_id
JOIN algorithm_runs AS r ON r.input_id = i.input_id;

INSERT INTO assessment_cases
    (case_name, category, difficulty, expected_complexity, description)
VALUES
    ('Balanced delimiters', 'PARENTHESES', 'BEGINNER', 'O(n)',
     'Validate nested parentheses, brackets, and braces.'),
    ('FIFO dispatch', 'QUEUE', 'BEGINNER', 'O(1) amortized',
     'Process work items in arrival order.'),
    ('LIFO undo history', 'STACK', 'BEGINNER', 'O(1)',
     'Restore the most recent configuration snapshot.'),
    ('Sliding maximum', 'DEQUE', 'ADVANCED', 'O(n)',
     'Maintain candidate indices in decreasing value order.'),
    ('Next greater element', 'NEXT_GREATER', 'INTERMEDIATE', 'O(n)',
     'Resolve each index when a strictly greater value arrives.'),
    ('Histogram area', 'MONOTONIC_STACK', 'ADVANCED', 'O(n)',
     'Compute maximal rectangular area using increasing bar heights.');

INSERT INTO algorithm_inputs
    (case_id, input_values, window_size, expression,
     expected_values, expected_boolean)
SELECT
    case_id,
    CASE case_name
        WHEN 'Sliding maximum' THEN ARRAY[1, 3, -1, -3, 5, 3, 6, 7]
        WHEN 'Next greater element' THEN ARRAY[2, 1, 2, 4, 3]
        ELSE '{}'::INTEGER[]
    END,
    CASE WHEN case_name = 'Sliding maximum' THEN 3 ELSE NULL END,
    CASE WHEN case_name = 'Balanced delimiters' THEN '{[()]}' ELSE NULL END,
    CASE case_name
        WHEN 'Sliding maximum' THEN ARRAY[3, 3, 5, 5, 6, 7]
        WHEN 'Next greater element' THEN ARRAY[4, 2, 4, -1, -1]
        ELSE NULL
    END,
    CASE WHEN case_name = 'Balanced delimiters' THEN TRUE ELSE NULL END
FROM assessment_cases
WHERE case_name IN (
    'Balanced delimiters',
    'Sliding maximum',
    'Next greater element'
);

INSERT INTO algorithm_runs
    (input_id, actual_values, actual_boolean, passed, execution_ms, diagnostic)
SELECT
    i.input_id,
    i.expected_values,
    i.expected_boolean,
    TRUE,
    CASE c.case_name
        WHEN 'Sliding maximum' THEN 0.025
        WHEN 'Next greater element' THEN 0.014
        ELSE 0.010
    END,
    'Reference assessment fixture'
FROM algorithm_inputs AS i
JOIN assessment_cases AS c ON c.case_id = i.case_id;

INSERT INTO work_items
    (external_key, description, priority, state, attempts,
     started_at, finished_at)
VALUES
    ('BUILD-101', 'Compile release candidate', 2, 'SUCCEEDED', 1,
     now() - interval '8 minutes', now() - interval '7 minutes'),
    ('TEST-101', 'Run regression suite', 2, 'FAILED', 1,
     now() - interval '6 minutes', now() - interval '4 minutes'),
    ('DOC-101', 'Generate test report', 1, 'QUEUED', 0, NULL, NULL);

INSERT INTO work_events (work_id, event_type, details)
SELECT work_id, 'ENQUEUED', jsonb_build_object('source', 'assessment')
FROM work_items;

INSERT INTO work_events (work_id, event_type, details)
SELECT work_id, 'STARTED', jsonb_build_object('worker', 'worker-a')
FROM work_items
WHERE state IN ('SUCCEEDED', 'FAILED');

INSERT INTO work_events (work_id, event_type, details)
SELECT work_id,
       CASE state WHEN 'SUCCEEDED' THEN 'SUCCEEDED' ELSE 'FAILED' END,
       jsonb_build_object('attempt', attempts)
FROM work_items
WHERE state IN ('SUCCEEDED', 'FAILED');

-- Results by category reveal correctness and observed runtime.
SELECT
    category,
    count(*) AS recorded_runs,
    count(*) FILTER (WHERE passed) AS passed_runs,
    round(avg(execution_ms), 3) AS average_ms
FROM assessment_results
GROUP BY category
ORDER BY category;

-- FIFO scheduling uses a stable tie-breaker for equal creation timestamps.
SELECT work_id, external_key, priority, state, created_at
FROM work_items
WHERE state = 'QUEUED'
ORDER BY created_at, work_id;

-- Find tasks that failed and may require an explicit retry policy.
SELECT external_key, description, attempts, finished_at
FROM work_items
WHERE state = 'FAILED'
ORDER BY finished_at DESC;

-- JSONB event history permits targeted diagnostic inspection.
SELECT
    w.external_key,
    e.event_type,
    e.event_time,
    e.details
FROM work_events AS e
JOIN work_items AS w USING (work_id)
WHERE e.event_type = 'FAILED'
ORDER BY e.event_time DESC;

-- This constraint violation is intentionally not executed: a production
-- caller can verify database enforcement inside a savepoint.
-- INSERT INTO work_items (external_key, description, priority)
-- VALUES ('INVALID-1', 'Invalid priority', 9);

-- Transaction boundaries ensure the sample model is loaded atomically.
COMMIT;

-- Assessment integrity query: a mismatch identifies a failed algorithm run.
SELECT
    c.case_name,
    i.expected_values,
    r.actual_values,
    i.expected_boolean,
    r.actual_boolean,
    r.passed
FROM algorithm_inputs AS i
JOIN assessment_cases AS c USING (case_id)
JOIN algorithm_runs AS r USING (input_id)
WHERE
    (i.expected_values IS NOT NULL AND i.expected_values IS DISTINCT FROM r.actual_values)
    OR
    (i.expected_boolean IS NOT NULL AND i.expected_boolean IS DISTINCT FROM r.actual_boolean);
