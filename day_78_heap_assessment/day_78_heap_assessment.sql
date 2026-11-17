-- ============================================================
-- HEAP ASSESSMENT AND PRIORITY QUEUE MANAGEMENT
-- PostgreSQL 14+
--
-- Relational workflow:
-- Assessment -> Problems -> Attempts -> Submissions
-- -> Results -> Priority Queue -> Processing
--
-- PostgreSQL tables use relational storage. This schema
-- implements logical priority-queue behavior using indexed
-- rows and transactional row locking.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS heap_assessment;

SET search_path TO heap_assessment, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE problem_category AS ENUM (
    'MIN_HEAP',
    'MAX_HEAP',
    'TOP_K',
    'KTH_ELEMENT',
    'MERGE_K_SORTED',
    'RUNNING_MEDIAN',
    'SLIDING_WINDOW',
    'SCHEDULING',
    'ADVANCED'
);

CREATE TYPE submission_status AS ENUM (
    'PENDING',
    'RUNNING',
    'ACCEPTED',
    'WRONG_ANSWER',
    'TIME_LIMIT_EXCEEDED',
    'RUNTIME_ERROR',
    'CANCELLED'
);

CREATE TYPE queue_priority AS ENUM (
    'CRITICAL',
    'HIGH',
    'NORMAL',
    'LOW'
);

CREATE TYPE queue_state AS ENUM (
    'QUEUED',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

CREATE TYPE difficulty_level AS ENUM (
    'EASY',
    'MEDIUM',
    'HARD'
);

-- ------------------------------------------------------------
-- 2. CORE TABLES
-- ------------------------------------------------------------

CREATE TABLE learners (
    learner_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_username
        CHECK (length(trim(username)) >= 3)
);

CREATE TABLE assessments (
    assessment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    maximum_score NUMERIC(8,2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_duration
        CHECK (duration_minutes BETWEEN 1 AND 600),

    CONSTRAINT valid_maximum_score
        CHECK (maximum_score > 0)
);

CREATE TABLE problems (
    problem_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assessment_id BIGINT NOT NULL
        REFERENCES assessments(assessment_id),
    title VARCHAR(200) NOT NULL,
    category problem_category NOT NULL,
    difficulty difficulty_level NOT NULL,
    maximum_score NUMERIC(8,2) NOT NULL,
    time_limit_ms INTEGER NOT NULL,
    memory_limit_mb INTEGER NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_problem_score
        CHECK (maximum_score > 0),

    CONSTRAINT valid_time_limit
        CHECK (time_limit_ms > 0),

    CONSTRAINT valid_memory_limit
        CHECK (memory_limit_mb > 0),

    UNIQUE (assessment_id, title)
);

CREATE TABLE assessment_attempts (
    attempt_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    learner_id BIGINT NOT NULL REFERENCES learners(learner_id),
    assessment_id BIGINT NOT NULL
        REFERENCES assessments(assessment_id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    completed BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT valid_attempt_dates
        CHECK (
            submitted_at IS NULL OR
            submitted_at >= started_at
        )
);

CREATE INDEX idx_attempts_learner
    ON assessment_attempts(learner_id, started_at DESC);

CREATE TABLE submissions (
    submission_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    attempt_id BIGINT NOT NULL
        REFERENCES assessment_attempts(attempt_id),
    problem_id BIGINT NOT NULL REFERENCES problems(problem_id),
    source_code TEXT NOT NULL,
    language VARCHAR(30) NOT NULL,
    status submission_status NOT NULL DEFAULT 'PENDING',
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    score NUMERIC(8,2) NOT NULL DEFAULT 0,
    execution_time_ms INTEGER,
    memory_used_mb INTEGER,
    failure_message TEXT,

    CONSTRAINT valid_submission_score
        CHECK (score >= 0),

    CONSTRAINT valid_execution_time
        CHECK (
            execution_time_ms IS NULL OR
            execution_time_ms >= 0
        ),

    CONSTRAINT valid_memory_usage
        CHECK (
            memory_used_mb IS NULL OR
            memory_used_mb >= 0
        ),

    CONSTRAINT valid_processed_date
        CHECK (
            processed_at IS NULL OR
            processed_at >= submitted_at
        )
);

CREATE INDEX idx_submissions_attempt
    ON submissions(attempt_id, submitted_at DESC);

CREATE INDEX idx_submissions_status
    ON submissions(status, submitted_at);

CREATE TABLE test_results (
    test_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    submission_id BIGINT NOT NULL
        REFERENCES submissions(submission_id),
    test_case_number INTEGER NOT NULL,
    passed BOOLEAN NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    memory_used_mb INTEGER NOT NULL,
    error_type VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (test_case_number > 0),
    CHECK (execution_time_ms >= 0),
    CHECK (memory_used_mb >= 0),

    UNIQUE (submission_id, test_case_number)
);

CREATE TABLE priority_jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    submission_id BIGINT NOT NULL UNIQUE
        REFERENCES submissions(submission_id),
    priority queue_priority NOT NULL DEFAULT 'NORMAL',
    state queue_state NOT NULL DEFAULT 'QUEUED',
    sequence_number BIGINT GENERATED ALWAYS AS IDENTITY,
    attempts INTEGER NOT NULL DEFAULT 0,
    maximum_attempts INTEGER NOT NULL DEFAULT 3,
    available_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failure_message TEXT,

    CHECK (attempts >= 0),
    CHECK (maximum_attempts > 0),
    CHECK (attempts <= maximum_attempts)
);

CREATE INDEX idx_priority_jobs_pending
    ON priority_jobs(
        priority,
        available_at,
        sequence_number
    )
    WHERE state = 'QUEUED';

CREATE INDEX idx_priority_jobs_state
    ON priority_jobs(state, created_at);

CREATE TABLE heap_operation_metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    submission_id BIGINT NOT NULL
        REFERENCES submissions(submission_id),
    operation_name VARCHAR(100) NOT NULL,
    input_size INTEGER NOT NULL,
    operation_count BIGINT NOT NULL,
    elapsed_microseconds BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (input_size >= 0),
    CHECK (operation_count >= 0),
    CHECK (elapsed_microseconds >= 0)
);

-- ------------------------------------------------------------
-- 3. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO learners (username, email)
VALUES
    ('learner_01', 'learner01@example.com'),
    ('learner_02', 'learner02@example.com'),
    ('learner_03', 'learner03@example.com');

INSERT INTO assessments (
    title,
    description,
    duration_minutes,
    maximum_score
)
VALUES (
    'Mixed Heap Assessment',
    'Heap construction, priority queues and heap-based algorithms.',
    120,
    100
);

INSERT INTO problems (
    assessment_id,
    title,
    category,
    difficulty,
    maximum_score,
    time_limit_ms,
    memory_limit_mb
)
VALUES
    (
        1,
        'Kth Largest Element',
        'KTH_ELEMENT',
        'MEDIUM',
        15,
        1000,
        128
    ),
    (
        1,
        'Top K Frequent Elements',
        'TOP_K',
        'MEDIUM',
        15,
        1500,
        128
    ),
    (
        1,
        'Merge K Sorted Arrays',
        'MERGE_K_SORTED',
        'HARD',
        20,
        2000,
        256
    ),
    (
        1,
        'Running Median',
        'RUNNING_MEDIAN',
        'HARD',
        20,
        2000,
        256
    ),
    (
        1,
        'Priority-Based Scheduling',
        'SCHEDULING',
        'HARD',
        30,
        3000,
        256
    );

INSERT INTO assessment_attempts (
    learner_id,
    assessment_id
)
VALUES
    (1, 1),
    (2, 1),
    (3, 1);

INSERT INTO submissions (
    attempt_id,
    problem_id,
    source_code,
    language,
    status,
    score,
    execution_time_ms,
    memory_used_mb,
    processed_at
)
VALUES
    (
        1,
        1,
        'heap-based kth largest implementation',
        'Python',
        'ACCEPTED',
        15,
        120,
        32,
        NOW()
    ),
    (
        1,
        2,
        'frequency map and bounded heap',
        'Python',
        'ACCEPTED',
        15,
        180,
        40,
        NOW()
    ),
    (
        2,
        3,
        'merge k sorted sequences',
        'Java',
        'WRONG_ANSWER',
        5,
        450,
        80,
        NOW()
    ),
    (
        2,
        4,
        'two heap running median',
        'Java',
        'PENDING',
        0,
        NULL,
        NULL,
        NULL
    ),
    (
        3,
        5,
        'priority-based scheduling',
        'C++17',
        'TIME_LIMIT_EXCEEDED',
        0,
        3000,
        120,
        NOW()
    );

INSERT INTO test_results (
    submission_id,
    test_case_number,
    passed,
    execution_time_ms,
    memory_used_mb,
    error_type
)
VALUES
    (1, 1, TRUE, 20, 12, NULL),
    (1, 2, TRUE, 30, 14, NULL),
    (1, 3, TRUE, 70, 20, NULL),
    (2, 1, TRUE, 50, 20, NULL),
    (2, 2, TRUE, 60, 22, NULL),
    (3, 1, TRUE, 100, 35, NULL),
    (3, 2, FALSE, 350, 60, 'WRONG_OUTPUT');

INSERT INTO priority_jobs (
    submission_id,
    priority,
    state
)
VALUES
    (4, 'HIGH', 'QUEUED'),
    (5, 'CRITICAL', 'QUEUED');

INSERT INTO heap_operation_metrics (
    submission_id,
    operation_name,
    input_size,
    operation_count,
    elapsed_microseconds
)
VALUES
    (1, 'HEAP_INSERT', 10000, 10000, 8500),
    (1, 'HEAP_EXTRACT', 10000, 10000, 12000),
    (2, 'HEAPIFY', 50000, 50000, 4500),
    (4, 'MEDIAN_INSERT', 100000, 100000, 15000);

-- ------------------------------------------------------------
-- 4. VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_submission_problem()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_assessment_id BIGINT;
BEGIN
    SELECT assessment_id
    INTO v_assessment_id
    FROM problems
    WHERE problem_id = NEW.problem_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Problem is missing or inactive.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM assessment_attempts a
        WHERE a.attempt_id = NEW.attempt_id
          AND a.assessment_id = v_assessment_id
          AND a.completed = FALSE
    ) THEN
        RAISE EXCEPTION
            'Problem does not belong to the active assessment attempt.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_submission
BEFORE INSERT OR UPDATE OF attempt_id, problem_id
ON submissions
FOR EACH ROW
EXECUTE FUNCTION validate_submission_problem();

-- ------------------------------------------------------------
-- 5. SCORE VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_submission_score()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_maximum NUMERIC(8,2);
BEGIN
    SELECT maximum_score
    INTO v_maximum
    FROM problems
    WHERE problem_id = NEW.problem_id;

    IF NEW.score > v_maximum THEN
        RAISE EXCEPTION
            'Score % exceeds maximum score %.',
            NEW.score,
            v_maximum;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_score
BEFORE INSERT OR UPDATE OF score, problem_id
ON submissions
FOR EACH ROW
EXECUTE FUNCTION validate_submission_score();

-- ------------------------------------------------------------
-- 6. PRIORITY QUEUE PROCESSING
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION claim_next_job()
RETURNS TABLE (
    claimed_job_id BIGINT,
    claimed_submission_id BIGINT,
    claimed_priority queue_priority
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH next_job AS (
        SELECT j.job_id
        FROM priority_jobs j
        WHERE j.state = 'QUEUED'
          AND j.available_at <= NOW()
          AND j.attempts < j.maximum_attempts
        ORDER BY
            CASE j.priority
                WHEN 'CRITICAL' THEN 0
                WHEN 'HIGH' THEN 1
                WHEN 'NORMAL' THEN 2
                WHEN 'LOW' THEN 3
            END,
            j.sequence_number
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    UPDATE priority_jobs j
    SET
        state = 'RUNNING',
        attempts = attempts + 1,
        started_at = NOW()
    FROM next_job n
    WHERE j.job_id = n.job_id
    RETURNING
        j.job_id,
        j.submission_id,
        j.priority;
END;
$$;

-- Concurrent workers can execute claim_next_job().
-- SKIP LOCKED prevents two workers from claiming the same job.

CREATE OR REPLACE PROCEDURE complete_job(
    p_job_id BIGINT,
    p_success BOOLEAN,
    p_failure_message TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE priority_jobs
    SET
        state = CASE
            WHEN p_success THEN 'COMPLETED'::queue_state
            WHEN attempts < maximum_attempts THEN 'QUEUED'::queue_state
            ELSE 'FAILED'::queue_state
        END,
        completed_at = CASE
            WHEN p_success OR attempts >= maximum_attempts
            THEN NOW()
            ELSE NULL
        END,
        available_at = CASE
            WHEN NOT p_success AND attempts < maximum_attempts
            THEN NOW() + INTERVAL '30 seconds'
            ELSE available_at
        END,
        failure_message = p_failure_message
    WHERE job_id = p_job_id
      AND state = 'RUNNING';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Job does not exist or is not running.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 7. ASSESSMENT REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW assessment_performance AS
SELECT
    l.learner_id,
    l.username,
    a.assessment_id,
    a.title AS assessment_title,
    COUNT(DISTINCT s.submission_id) AS submission_count,
    COALESCE(SUM(s.score), 0) AS earned_score,
    COALESCE(SUM(p.maximum_score), 0) AS possible_score,
    ROUND(
        100.0 * COALESCE(SUM(s.score), 0) /
        NULLIF(SUM(p.maximum_score), 0),
        2
    ) AS percentage_score,
    COUNT(*) FILTER (
        WHERE s.status = 'ACCEPTED'
    ) AS accepted_submissions,
    COUNT(*) FILTER (
        WHERE s.status = 'WRONG_ANSWER'
    ) AS wrong_answers,
    COUNT(*) FILTER (
        WHERE s.status = 'TIME_LIMIT_EXCEEDED'
    ) AS time_limit_failures
FROM learners l
JOIN assessment_attempts at
    ON at.learner_id = l.learner_id
JOIN assessments a
    ON a.assessment_id = at.assessment_id
LEFT JOIN submissions s
    ON s.attempt_id = at.attempt_id
LEFT JOIN problems p
    ON p.problem_id = s.problem_id
GROUP BY
    l.learner_id,
    l.username,
    a.assessment_id,
    a.title;

-- ------------------------------------------------------------
-- 8. ELIGIBILITY DETERMINATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION submission_eligibility(
    p_submission_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_submission submissions%ROWTYPE;
    v_problem problems%ROWTYPE;
    v_failed_tests BIGINT;
BEGIN
    SELECT *
    INTO v_submission
    FROM submissions
    WHERE submission_id = p_submission_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT FALSE, 'Submission does not exist.';
        RETURN;
    END IF;

    SELECT *
    INTO v_problem
    FROM problems
    WHERE problem_id = v_submission.problem_id;

    IF v_submission.status <> 'ACCEPTED' THEN
        RETURN QUERY
        SELECT FALSE, 'Submission is not accepted.';
        RETURN;
    END IF;

    IF v_submission.execution_time_ms IS NULL
       OR v_submission.execution_time_ms > v_problem.time_limit_ms
    THEN
        RETURN QUERY
        SELECT FALSE, 'Execution time requirement not satisfied.';
        RETURN;
    END IF;

    IF v_submission.memory_used_mb IS NULL
       OR v_submission.memory_used_mb > v_problem.memory_limit_mb
    THEN
        RETURN QUERY
        SELECT FALSE, 'Memory requirement not satisfied.';
        RETURN;
    END IF;

    SELECT COUNT(*)
    INTO v_failed_tests
    FROM test_results
    WHERE submission_id = p_submission_id
      AND passed = FALSE;

    IF v_failed_tests > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'One or more test cases failed.';
        RETURN;
    END IF;

    RETURN QUERY
    SELECT TRUE, 'Submission satisfies eligibility conditions.';
END;
$$;

-- ------------------------------------------------------------
-- 9. PERFORMANCE REPORT
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW heap_category_performance AS
SELECT
    p.category,
    p.difficulty,
    COUNT(s.submission_id) AS total_submissions,
    COUNT(*) FILTER (
        WHERE s.status = 'ACCEPTED'
    ) AS accepted_count,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE s.status = 'ACCEPTED'
        ) / NULLIF(COUNT(s.submission_id), 0),
        2
    ) AS acceptance_percentage,
    ROUND(AVG(s.execution_time_ms), 2) AS average_execution_ms,
    ROUND(AVG(s.memory_used_mb), 2) AS average_memory_mb
FROM problems p
LEFT JOIN submissions s
    ON s.problem_id = p.problem_id
GROUP BY p.category, p.difficulty;

-- ------------------------------------------------------------
-- 10. RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- All heap problems in difficulty order.
SELECT
    problem_id,
    title,
    category,
    difficulty,
    maximum_score,
    time_limit_ms
FROM problems
WHERE active = TRUE
ORDER BY
    CASE difficulty
        WHEN 'EASY' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'HARD' THEN 3
    END,
    problem_id;

-- Most frequently submitted problems.
SELECT
    p.title,
    COUNT(s.submission_id) AS submission_count
FROM problems p
LEFT JOIN submissions s
    ON s.problem_id = p.problem_id
GROUP BY p.problem_id, p.title
ORDER BY submission_count DESC, p.title;

-- ------------------------------------------------------------
-- 11. AGGREGATION AND EVALUATION
-- ------------------------------------------------------------

SELECT *
FROM assessment_performance
ORDER BY percentage_score DESC NULLS LAST;

SELECT *
FROM heap_category_performance
ORDER BY acceptance_percentage DESC NULLS LAST;

-- Failed test-case analysis.
SELECT
    s.submission_id,
    p.title,
    tr.test_case_number,
    tr.error_type,
    tr.execution_time_ms
FROM test_results tr
JOIN submissions s
    ON s.submission_id = tr.submission_id
JOIN problems p
    ON p.problem_id = s.problem_id
WHERE tr.passed = FALSE
ORDER BY s.submission_id, tr.test_case_number;

-- Heap operation performance.
SELECT
    operation_name,
    input_size,
    SUM(operation_count) AS total_operations,
    ROUND(AVG(elapsed_microseconds), 2) AS average_microseconds
FROM heap_operation_metrics
GROUP BY operation_name, input_size
ORDER BY input_size DESC;

-- ------------------------------------------------------------
-- 12. WORKFLOW TRANSACTION
-- ------------------------------------------------------------

-- Claim one available job.
-- Run this block in an application transaction.

DO $$
DECLARE
    v_job RECORD;
BEGIN
    SELECT *
    INTO v_job
    FROM claim_next_job();

    IF v_job.claimed_job_id IS NOT NULL THEN
        RAISE NOTICE
            'Claimed job %, submission %, priority %',
            v_job.claimed_job_id,
            v_job.claimed_submission_id,
            v_job.claimed_priority;
    ELSE
        RAISE NOTICE 'No jobs available.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 13. QUEUE STATE INSPECTION
-- ------------------------------------------------------------

SELECT
    job_id,
    submission_id,
    priority,
    state,
    attempts,
    maximum_attempts,
    available_at
FROM priority_jobs
ORDER BY
    CASE priority
        WHEN 'CRITICAL' THEN 0
        WHEN 'HIGH' THEN 1
        WHEN 'NORMAL' THEN 2
        WHEN 'LOW' THEN 3
    END,
    sequence_number;

-- ------------------------------------------------------------
-- 14. VALIDATION EXAMPLES
-- ------------------------------------------------------------

SELECT
    s.submission_id,
    eligibility.eligible,
    eligibility.reason
FROM submissions s
CROSS JOIN LATERAL
    submission_eligibility(s.submission_id) eligibility
ORDER BY s.submission_id;

-- ------------------------------------------------------------
-- 15. OPERATIONAL INDEX INSPECTION
-- ------------------------------------------------------------

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'heap_assessment'
ORDER BY tablename, indexname;

COMMIT;

-- ============================================================
-- OPERATIONAL NOTES
--
-- 1. Priority ordering is represented by an explicit CASE
--    expression rather than alphabetical enum ordering.
--
-- 2. sequence_number provides stable FIFO ordering within
--    each priority class.
--
-- 3. FOR UPDATE SKIP LOCKED supports concurrent workers.
--
-- 4. The partial index targets queued jobs only.
--
-- 5. The database models queue state; heap operations such
--    as sift-up and sift-down belong in application memory.
--
-- 6. Application workers must use transactions when claiming
--    and completing jobs.
--
-- 7. Source code storage requires access controls and retention
--    policies in a production deployment.
-- ============================================================
