-- ============================================================
-- HEAP SORT AND MULTIWAY MERGING
-- PostgreSQL 15+
--
-- Models:
--   1. Sorting jobs
--   2. Sorted data sources
--   3. Source elements
--   4. Heap-based K-way merge
--   5. Pairwise multiway merge
--   6. Merge execution records
--   7. Validation and integrity enforcement
--
-- Heap algorithms are implemented through indexed working tables
-- and PL/pgSQL procedures/functions.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS heap_merge;

SET search_path TO heap_merge, public;

-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

CREATE TYPE job_status AS ENUM (
    'CREATED',
    'VALIDATING',
    'READY',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);

CREATE TYPE merge_strategy AS ENUM (
    'HEAP',
    'PAIRWISE'
);

CREATE TYPE source_status AS ENUM (
    'REGISTERED',
    'VALIDATED',
    'REJECTED'
);

-- ============================================================
-- 2. CORE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS merge_jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_name VARCHAR(150) NOT NULL,

    strategy merge_strategy NOT NULL,

    status job_status NOT NULL DEFAULT 'CREATED',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    maximum_elements BIGINT NOT NULL DEFAULT 1000000,

    error_message TEXT,

    CONSTRAINT valid_job_name
        CHECK (length(trim(job_name)) > 0),

    CONSTRAINT positive_maximum_elements
        CHECK (maximum_elements > 0),

    CONSTRAINT valid_job_timestamps
        CHECK (
            completed_at IS NULL
            OR started_at IS NOT NULL
        )
);

CREATE TABLE IF NOT EXISTS merge_sources (
    source_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES merge_jobs(job_id)
        ON DELETE CASCADE,

    source_name VARCHAR(150) NOT NULL,

    source_owner VARCHAR(100) NOT NULL,

    source_position INTEGER NOT NULL,

    status source_status NOT NULL DEFAULT 'REGISTERED',

    element_count BIGINT NOT NULL DEFAULT 0,

    registered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_source_position
        UNIQUE (job_id, source_position),

    CONSTRAINT unique_source_name
        UNIQUE (job_id, source_name),

    CONSTRAINT positive_source_position
        CHECK (source_position >= 0),

    CONSTRAINT nonnegative_element_count
        CHECK (element_count >= 0),

    CONSTRAINT valid_source_name
        CHECK (length(trim(source_name)) > 0)
);

CREATE TABLE IF NOT EXISTS source_elements (
    element_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_id BIGINT NOT NULL
        REFERENCES merge_sources(source_id)
        ON DELETE CASCADE,

    element_position BIGINT NOT NULL,

    element_value BIGINT NOT NULL,

    CONSTRAINT unique_source_element_position
        UNIQUE (source_id, element_position),

    CONSTRAINT nonnegative_element_position
        CHECK (element_position >= 0)
);

CREATE TABLE IF NOT EXISTS merge_executions (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES merge_jobs(job_id)
        ON DELETE CASCADE,

    strategy merge_strategy NOT NULL,

    total_sources INTEGER NOT NULL,

    total_elements BIGINT NOT NULL,

    result_checksum TEXT,

    elapsed_microseconds BIGINT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT nonnegative_execution_counts
        CHECK (
            total_sources >= 0
            AND total_elements >= 0
        ),

    CONSTRAINT nonnegative_elapsed_time
        CHECK (
            elapsed_microseconds IS NULL
            OR elapsed_microseconds >= 0
        )
);

CREATE TABLE IF NOT EXISTS merge_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    execution_id BIGINT NOT NULL
        REFERENCES merge_executions(execution_id)
        ON DELETE CASCADE,

    result_position BIGINT NOT NULL,

    result_value BIGINT NOT NULL,

    CONSTRAINT unique_result_position
        UNIQUE (execution_id, result_position),

    CONSTRAINT nonnegative_result_position
        CHECK (result_position >= 0)
);

-- ============================================================
-- 3. INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_jobs_status_created
    ON merge_jobs(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sources_job_position
    ON merge_sources(job_id, source_position);

CREATE INDEX IF NOT EXISTS idx_sources_job_status
    ON merge_sources(job_id, status);

CREATE INDEX IF NOT EXISTS idx_elements_source_position
    ON source_elements(source_id, element_position);

CREATE INDEX IF NOT EXISTS idx_elements_source_value
    ON source_elements(source_id, element_value);

CREATE INDEX IF NOT EXISTS idx_executions_job_time
    ON merge_executions(job_id, executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_results_execution_value
    ON merge_results(execution_id, result_value);

-- ============================================================
-- 4. SOURCE ELEMENT VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_source_element()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    previous_value BIGINT;
    next_value BIGINT;
    source_limit BIGINT;
    current_count BIGINT;
BEGIN
    -- Lock the source row to serialize concurrent modifications.
    SELECT element_count
    INTO current_count
    FROM merge_sources
    WHERE source_id = NEW.source_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source % does not exist', NEW.source_id;
    END IF;

    IF TG_OP = 'UPDATE' AND
       OLD.source_id <> NEW.source_id THEN
        RAISE EXCEPTION
            'Moving elements between sources is not supported';
    END IF;

    SELECT j.maximum_elements
    INTO source_limit
    FROM merge_sources s
    JOIN merge_jobs j ON j.job_id = s.job_id
    WHERE s.source_id = NEW.source_id;

    IF TG_OP = 'INSERT' AND current_count >= source_limit THEN
        RAISE EXCEPTION 'Source element limit exceeded';
    END IF;

    SELECT element_value
    INTO previous_value
    FROM source_elements
    WHERE source_id = NEW.source_id
      AND element_position = NEW.element_position - 1;

    SELECT element_value
    INTO next_value
    FROM source_elements
    WHERE source_id = NEW.source_id
      AND element_position = NEW.element_position + 1;

    IF previous_value IS NOT NULL
       AND previous_value > NEW.element_value THEN
        RAISE EXCEPTION
            'Element violates ascending order: previous value % > new value %',
            previous_value,
            NEW.element_value;
    END IF;

    IF next_value IS NOT NULL
       AND NEW.element_value > next_value THEN
        RAISE EXCEPTION
            'Element violates ascending order: new value % > next value %',
            NEW.element_value,
            next_value;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_source_element
    ON source_elements;

CREATE TRIGGER trg_validate_source_element
BEFORE INSERT OR UPDATE
ON source_elements
FOR EACH ROW
EXECUTE FUNCTION validate_source_element();

-- ============================================================
-- 5. MAINTAIN SOURCE COUNTS
-- ============================================================

CREATE OR REPLACE FUNCTION maintain_source_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE merge_sources
        SET element_count = element_count + 1
        WHERE source_id = NEW.source_id;

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE merge_sources
        SET element_count = element_count - 1
        WHERE source_id = OLD.source_id;

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_maintain_source_count
    ON source_elements;

CREATE TRIGGER trg_maintain_source_count
AFTER INSERT OR DELETE
ON source_elements
FOR EACH ROW
EXECUTE FUNCTION maintain_source_count();

-- ============================================================
-- 6. JOB STATE VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_job_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = 'COMPLETED'
       AND NEW.status <> 'COMPLETED' THEN
        RAISE EXCEPTION 'Completed jobs cannot be reopened';
    END IF;

    IF OLD.status = 'FAILED'
       AND NEW.status <> 'FAILED' THEN
        RAISE EXCEPTION 'Failed jobs are terminal';
    END IF;

    IF NEW.status = 'RUNNING'
       AND OLD.status <> 'READY' THEN
        RAISE EXCEPTION
            'Only READY jobs can enter RUNNING state';
    END IF;

    IF NEW.status = 'COMPLETED'
       AND OLD.status <> 'RUNNING' THEN
        RAISE EXCEPTION
            'Only RUNNING jobs can be completed';
    END IF;

    IF NEW.status = 'FAILED'
       AND OLD.status NOT IN (
           'CREATED',
           'VALIDATING',
           'READY',
           'RUNNING'
       ) THEN
        RAISE EXCEPTION 'Invalid failure transition';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_job_transition
    ON merge_jobs;

CREATE TRIGGER trg_validate_job_transition
BEFORE UPDATE OF status
ON merge_jobs
FOR EACH ROW
EXECUTE FUNCTION validate_job_transition();

-- ============================================================
-- 7. JOB SOURCE VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_merge_job(
    p_job_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    source_count INTEGER;
    total_elements BIGINT;
    maximum_elements BIGINT;
    invalid_sources INTEGER;
BEGIN
    SELECT maximum_elements
    INTO maximum_elements
    FROM merge_jobs
    WHERE job_id = p_job_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Job % not found', p_job_id;
    END IF;

    UPDATE merge_jobs
    SET status = 'VALIDATING'
    WHERE job_id = p_job_id
      AND status = 'CREATED';

    SELECT
        COUNT(*),
        COALESCE(SUM(element_count), 0)
    INTO source_count, total_elements
    FROM merge_sources
    WHERE job_id = p_job_id;

    IF source_count = 0 THEN
        RAISE EXCEPTION 'Merge job has no sources';
    END IF;

    IF total_elements > maximum_elements THEN
        RAISE EXCEPTION
            'Job element limit exceeded: % > %',
            total_elements,
            maximum_elements;
    END IF;

    SELECT COUNT(*)
    INTO invalid_sources
    FROM merge_sources s
    WHERE s.job_id = p_job_id
      AND (
          s.status = 'REJECTED'
          OR s.element_count <> (
              SELECT COUNT(*)
              FROM source_elements e
              WHERE e.source_id = s.source_id
          )
      );

    IF invalid_sources > 0 THEN
        RAISE EXCEPTION
            'Invalid or inconsistent source records: %',
            invalid_sources;
    END IF;

    UPDATE merge_sources
    SET status = 'VALIDATED'
    WHERE job_id = p_job_id;

    UPDATE merge_jobs
    SET status = 'READY',
        error_message = NULL
    WHERE job_id = p_job_id;

    RETURN TRUE;
END;
$$;

-- ============================================================
-- 8. WORKING HEAP TABLE
-- ============================================================

CREATE TEMP TABLE IF NOT EXISTS merge_heap_work (
    heap_position INTEGER PRIMARY KEY,
    element_value BIGINT NOT NULL,
    source_id BIGINT NOT NULL,
    element_position BIGINT NOT NULL
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE IF NOT EXISTS merge_output_work (
    result_position BIGINT PRIMARY KEY,
    result_value BIGINT NOT NULL
) ON COMMIT PRESERVE ROWS;

-- ============================================================
-- 9. HEAP OPERATIONS
-- ============================================================

CREATE OR REPLACE FUNCTION heap_entry_less(
    p_value_a BIGINT,
    p_source_a BIGINT,
    p_position_a BIGINT,
    p_value_b BIGINT,
    p_source_b BIGINT,
    p_position_b BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT ROW(p_value_a, p_source_a, p_position_a)
         < ROW(p_value_b, p_source_b, p_position_b);
$$;

CREATE OR REPLACE PROCEDURE heap_push(
    p_value BIGINT,
    p_source BIGINT,
    p_position BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    heap_size INTEGER;
    current_position INTEGER;
    parent_position INTEGER;
    parent_value BIGINT;
    parent_source BIGINT;
    parent_element_position BIGINT;
    current_value BIGINT;
    current_source BIGINT;
    current_element_position BIGINT;
BEGIN
    SELECT COALESCE(MAX(heap_position), 0) + 1
    INTO heap_size
    FROM merge_heap_work;

    current_position := heap_size;

    INSERT INTO merge_heap_work
    VALUES (
        current_position,
        p_value,
        p_source,
        p_position
    );

    -- Bubble the new entry upward.
    WHILE current_position > 1 LOOP
        parent_position := current_position / 2;

        SELECT element_value, source_id, element_position
        INTO parent_value, parent_source, parent_element_position
        FROM merge_heap_work
        WHERE heap_position = parent_position;

        SELECT element_value, source_id, element_position
        INTO current_value, current_source, current_element_position
        FROM merge_heap_work
        WHERE heap_position = current_position;

        IF NOT heap_entry_less(
            current_value,
            current_source,
            current_element_position,
            parent_value,
            parent_source,
            parent_element_position
        ) THEN
            EXIT;
        END IF;

        UPDATE merge_heap_work
        SET heap_position = -1
        WHERE heap_position = current_position;

        UPDATE merge_heap_work
        SET heap_position = current_position
        WHERE heap_position = parent_position;

        UPDATE merge_heap_work
        SET heap_position = parent_position
        WHERE heap_position = -1;

        current_position := parent_position;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE heap_pop(
    OUT p_value BIGINT,
    OUT p_source BIGINT,
    OUT p_position BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    heap_size INTEGER;
    current_position INTEGER;
    left_position INTEGER;
    right_position INTEGER;
    smallest_position INTEGER;

    root_value BIGINT;
    root_source BIGINT;
    root_element_position BIGINT;

    child_value BIGINT;
    child_source BIGINT;
    child_element_position BIGINT;

    current_value BIGINT;
    current_source BIGINT;
    current_element_position BIGINT;

    last_value BIGINT;
    last_source BIGINT;
    last_element_position BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO heap_size
    FROM merge_heap_work;

    IF heap_size = 0 THEN
        RAISE EXCEPTION 'Cannot pop an empty heap';
    END IF;

    SELECT element_value, source_id, element_position
    INTO p_value, p_source, p_position
    FROM merge_heap_work
    WHERE heap_position = 1;

    IF heap_size = 1 THEN
        DELETE FROM merge_heap_work;
        RETURN;
    END IF;

    SELECT element_value, source_id, element_position
    INTO last_value, last_source, last_element_position
    FROM merge_heap_work
    WHERE heap_position = heap_size;

    DELETE FROM merge_heap_work
    WHERE heap_position = heap_size;

    UPDATE merge_heap_work
    SET element_value = last_value,
        source_id = last_source,
        element_position = last_element_position
    WHERE heap_position = 1;

    current_position := 1;

    LOOP
        left_position := current_position * 2;
        right_position := left_position + 1;
        smallest_position := current_position;

        SELECT element_value, source_id, element_position
        INTO current_value, current_source, current_element_position
        FROM merge_heap_work
        WHERE heap_position = current_position;

        IF EXISTS (
            SELECT 1
            FROM merge_heap_work
            WHERE heap_position = left_position
        ) THEN
            SELECT element_value, source_id, element_position
            INTO child_value, child_source, child_element_position
            FROM merge_heap_work
            WHERE heap_position = left_position;

            IF heap_entry_less(
                child_value,
                child_source,
                child_element_position,
                current_value,
                current_source,
                current_element_position
            ) THEN
                smallest_position := left_position;
            END IF;
        END IF;

        IF EXISTS (
            SELECT 1
            FROM merge_heap_work
            WHERE heap_position = right_position
        ) THEN
            SELECT element_value, source_id, element_position
            INTO child_value, child_source, child_element_position
            FROM merge_heap_work
            WHERE heap_position = right_position;

            SELECT element_value, source_id, element_position
            INTO current_value, current_source, current_element_position
            FROM merge_heap_work
            WHERE heap_position = smallest_position;

            IF heap_entry_less(
                child_value,
                child_source,
                child_element_position,
                current_value,
                current_source,
                current_element_position
            ) THEN
                smallest_position := right_position;
            END IF;
        END IF;

        EXIT WHEN smallest_position = current_position;

        SELECT element_value, source_id, element_position
        INTO root_value, root_source, root_element_position
        FROM merge_heap_work
        WHERE heap_position = current_position;

        SELECT element_value, source_id, element_position
        INTO child_value, child_source, child_element_position
        FROM merge_heap_work
        WHERE heap_position = smallest_position;

        UPDATE merge_heap_work
        SET element_value = child_value,
            source_id = child_source,
            element_position = child_element_position
        WHERE heap_position = current_position;

        UPDATE merge_heap_work
        SET element_value = root_value,
            source_id = root_source,
            element_position = root_element_position
        WHERE heap_position = smallest_position;

        current_position := smallest_position;
    END LOOP;
END;
$$;

-- ============================================================
-- 10. HEAP-BASED K-WAY MERGE
-- ============================================================

CREATE OR REPLACE FUNCTION execute_heap_merge(
    p_job_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    source_record RECORD;
    current_value BIGINT;
    current_source BIGINT;
    current_position BIGINT;
    next_value BIGINT;

    result_index BIGINT := 0;
    total_elements BIGINT := 0;
    source_count INTEGER := 0;
    started_at TIMESTAMPTZ;
    execution_id BIGINT;
BEGIN
    started_at := clock_timestamp();

    PERFORM validate_merge_job(p_job_id);

    UPDATE merge_jobs
    SET status = 'RUNNING',
        started_at = started_at
    WHERE job_id = p_job_id;

    TRUNCATE merge_heap_work;
    TRUNCATE merge_output_work;

    FOR source_record IN
        SELECT s.source_id, e.element_value, e.element_position
        FROM merge_sources s
        JOIN source_elements e
          ON e.source_id = s.source_id
        WHERE s.job_id = p_job_id
          AND e.element_position = 0
        ORDER BY s.source_position
    LOOP
        CALL heap_push(
            source_record.element_value,
            source_record.source_id,
            source_record.element_position
        );
    END LOOP;

    SELECT COUNT(*)
    INTO source_count
    FROM merge_sources
    WHERE job_id = p_job_id;

    SELECT COALESCE(SUM(element_count), 0)
    INTO total_elements
    FROM merge_sources
    WHERE job_id = p_job_id;

    WHILE EXISTS (
        SELECT 1 FROM merge_heap_work
    ) LOOP
        CALL heap_pop(
            current_value,
            current_source,
            current_position
        );

        INSERT INTO merge_output_work
        VALUES (result_index, current_value);

        result_index := result_index + 1;

        SELECT element_value
        INTO next_value
        FROM source_elements
        WHERE source_id = current_source
          AND element_position = current_position + 1;

        IF FOUND THEN
            CALL heap_push(
                next_value,
                current_source,
                current_position + 1
            );
        END IF;
    END LOOP;

    IF result_index <> total_elements THEN
        RAISE EXCEPTION
            'Merge invariant failed: expected %, produced %',
            total_elements,
            result_index;
    END IF;

    INSERT INTO merge_executions (
        job_id,
        strategy,
        total_sources,
        total_elements,
        elapsed_microseconds
    )
    VALUES (
        p_job_id,
        'HEAP',
        source_count,
        total_elements,
        (
            EXTRACT(EPOCH FROM (
                clock_timestamp() - started_at
            )) * 1000000
        )::BIGINT
    )
    RETURNING merge_executions.execution_id
    INTO execution_id;

    INSERT INTO merge_results (
        execution_id,
        result_position,
        result_value
    )
    SELECT
        execution_id,
        result_position,
        result_value
    FROM merge_output_work
    ORDER BY result_position;

    UPDATE merge_jobs
    SET status = 'COMPLETED',
        completed_at = clock_timestamp()
    WHERE job_id = p_job_id;

    RETURN execution_id;

EXCEPTION WHEN OTHERS THEN
    UPDATE merge_jobs
    SET status = 'FAILED',
        error_message = SQLERRM
    WHERE job_id = p_job_id
      AND status NOT IN ('COMPLETED', 'FAILED');

    RAISE;
END;
$$;

-- ============================================================
-- 11. PAIRWISE MULTIWAY MERGE
-- ============================================================

CREATE OR REPLACE FUNCTION execute_pairwise_merge(
    p_job_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    source_record RECORD;
    current_round INTEGER := 0;
    current_source_count INTEGER;
    execution_id BIGINT;
    total_elements BIGINT;
    source_count INTEGER;
    started_at TIMESTAMPTZ;
BEGIN
    started_at := clock_timestamp();

    PERFORM validate_merge_job(p_job_id);

    UPDATE merge_jobs
    SET status = 'RUNNING',
        started_at = started_at
    WHERE job_id = p_job_id;

    -- Use arrays for each sorted run.
    CREATE TEMP TABLE IF NOT EXISTS pairwise_runs (
        run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        round_number INTEGER NOT NULL,
        values_array BIGINT[] NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE pairwise_runs RESTART IDENTITY;

    INSERT INTO pairwise_runs(round_number, values_array)
    SELECT
        0,
        COALESCE(
            array_agg(e.element_value ORDER BY e.element_position),
            ARRAY[]::BIGINT[]
        )
    FROM merge_sources s
    LEFT JOIN source_elements e
      ON e.source_id = s.source_id
    WHERE s.job_id = p_job_id
    GROUP BY s.source_id
    ORDER BY s.source_id;

    LOOP
        SELECT COUNT(*)
        INTO current_source_count
        FROM pairwise_runs
        WHERE round_number = current_round;

        EXIT WHEN current_source_count <= 1;

        INSERT INTO pairwise_runs(round_number, values_array)
        SELECT
            current_round + 1,
            CASE
                WHEN second_run.run_id IS NULL
                    THEN first_run.values_array
                ELSE (
                    SELECT array_agg(value ORDER BY value)
                    FROM unnest(
                        first_run.values_array ||
                        second_run.values_array
                    ) AS value
                )
            END
        FROM (
            SELECT
                run_id,
                values_array,
                row_number() OVER (ORDER BY run_id) AS rn
            FROM pairwise_runs
            WHERE round_number = current_round
        ) first_run
        LEFT JOIN (
            SELECT
                run_id,
                values_array,
                row_number() OVER (ORDER BY run_id) AS rn
            FROM pairwise_runs
            WHERE round_number = current_round
        ) second_run
        ON second_run.rn = first_run.rn + 1
        WHERE first_run.rn % 2 = 1;

        current_round := current_round + 1;
    END LOOP;

    SELECT COALESCE(SUM(element_count), 0)
    INTO total_elements
    FROM merge_sources
    WHERE job_id = p_job_id;

    SELECT COUNT(*)
    INTO source_count
    FROM merge_sources
    WHERE job_id = p_job_id;

    INSERT INTO merge_executions (
        job_id,
        strategy,
        total_sources,
        total_elements,
        elapsed_microseconds
    )
    VALUES (
        p_job_id,
        'PAIRWISE',
        source_count,
        total_elements,
        (
            EXTRACT(EPOCH FROM (
                clock_timestamp() - started_at
            )) * 1000000
        )::BIGINT
    )
    RETURNING merge_executions.execution_id
    INTO execution_id;

    INSERT INTO merge_results (
        execution_id,
        result_position,
        result_value
    )
    SELECT
        execution_id,
        (entry.ordinality - 1)::BIGINT,
        entry.value
    FROM pairwise_runs r
    CROSS JOIN LATERAL
        unnest(r.values_array)
        WITH ORDINALITY AS entry(value, ordinality)
    WHERE r.round_number = current_round
    ORDER BY entry.ordinality;

    UPDATE merge_jobs
    SET status = 'COMPLETED',
        completed_at = clock_timestamp()
    WHERE job_id = p_job_id;

    RETURN execution_id;

EXCEPTION WHEN OTHERS THEN
    UPDATE merge_jobs
    SET status = 'FAILED',
        error_message = SQLERRM
    WHERE job_id = p_job_id
      AND status NOT IN ('COMPLETED', 'FAILED');

    RAISE;
END;
$$;

-- ============================================================
-- 12. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW job_source_summary AS
SELECT
    j.job_id,
    j.job_name,
    j.status,
    j.strategy,
    COUNT(s.source_id) AS source_count,
    COALESCE(SUM(s.element_count), 0) AS total_elements,
    COUNT(s.source_id) FILTER (
        WHERE s.status = 'VALIDATED'
    ) AS validated_sources,
    j.created_at
FROM merge_jobs j
LEFT JOIN merge_sources s
    ON s.job_id = j.job_id
GROUP BY j.job_id;

CREATE OR REPLACE VIEW merge_execution_report AS
SELECT
    e.execution_id,
    e.job_id,
    j.job_name,
    e.strategy,
    e.total_sources,
    e.total_elements,
    e.elapsed_microseconds,
    e.executed_at,
    e.result_checksum
FROM merge_executions e
JOIN merge_jobs j
    ON j.job_id = e.job_id;

CREATE OR REPLACE VIEW result_order_validation AS
SELECT
    execution_id,
    COUNT(*) AS element_count,
    BOOL_AND(
        previous_value IS NULL
        OR previous_value <= result_value
    ) AS ascending_order_valid
FROM (
    SELECT
        execution_id,
        result_value,
        LAG(result_value) OVER (
            PARTITION BY execution_id
            ORDER BY result_position
        ) AS previous_value
    FROM merge_results
) ordered_results
GROUP BY execution_id;

-- ============================================================
-- 13. SAMPLE JOBS AND DATA
-- ============================================================

INSERT INTO merge_jobs (
    job_name,
    strategy,
    maximum_elements
)
VALUES
    ('Regional Database Consolidation', 'HEAP', 100000),
    ('Financial Record Consolidation', 'PAIRWISE', 100000),
    ('Empty Source Validation Example', 'HEAP', 1000);

INSERT INTO merge_sources (
    job_id,
    source_name,
    source_owner,
    source_position
)
VALUES
    (1, 'database-A', 'Data Engineering', 0),
    (1, 'database-B', 'Analytics', 1),
    (1, 'database-C', 'Operations', 2),
    (1, 'database-D', 'Research', 3),
    (2, 'financial-A', 'Finance', 0),
    (2, 'financial-B', 'Finance', 1),
    (2, 'financial-C', 'Audit', 2);

INSERT INTO source_elements (
    source_id,
    element_position,
    element_value
)
VALUES
    -- Job 1, database A
    (1, 0, 1),
    (1, 1, 4),
    (1, 2, 7),
    (1, 3, 10),

    -- Job 1, database B
    (2, 0, 2),
    (2, 1, 5),
    (2, 2, 8),
    (2, 3, 11),

    -- Job 1, database C
    (3, 0, 3),
    (3, 1, 6),
    (3, 2, 9),
    (3, 3, 12),

    -- Job 1, database D
    (4, 0, 0),
    (4, 1, 13),
    (4, 2, 15),

    -- Job 2, financial A
    (5, 0, 100),
    (5, 1, 200),
    (5, 2, 300),

    -- Job 2, financial B
    (6, 0, 150),
    (6, 1, 250),
    (6, 2, 350),

    -- Job 2, financial C
    (7, 0, 50),
    (7, 1, 275),
    (7, 2, 400);

-- ============================================================
-- 14. RETRIEVAL QUERIES
-- ============================================================

SELECT *
FROM job_source_summary
ORDER BY job_id;

SELECT
    s.source_name,
    s.source_owner,
    e.element_position,
    e.element_value
FROM merge_sources s
JOIN source_elements e
    ON e.source_id = s.source_id
WHERE s.job_id = 1
ORDER BY s.source_position, e.element_position;

-- ============================================================
-- 15. VALIDATION QUERIES
-- ============================================================

SELECT
    s.source_id,
    s.source_name,
    s.element_count,
    COUNT(e.element_id) AS actual_count,
    s.element_count = COUNT(e.element_id) AS count_valid
FROM merge_sources s
LEFT JOIN source_elements e
    ON e.source_id = s.source_id
GROUP BY s.source_id
ORDER BY s.source_id;

SELECT
    source_id,
    element_position,
    element_value,
    LAG(element_value) OVER (
        PARTITION BY source_id
        ORDER BY element_position
    ) AS previous_value,
    CASE
        WHEN LAG(element_value) OVER (
            PARTITION BY source_id
            ORDER BY element_position
        ) IS NULL THEN TRUE
        ELSE element_value >= LAG(element_value) OVER (
            PARTITION BY source_id
            ORDER BY element_position
        )
    END AS order_valid
FROM source_elements
ORDER BY source_id, element_position;

-- ============================================================
-- 16. EXECUTE HEAP MERGE
-- ============================================================

DO $$
DECLARE
    execution_id BIGINT;
BEGIN
    execution_id := execute_heap_merge(1);

    RAISE NOTICE 'Heap execution ID: %', execution_id;
END;
$$;

-- ============================================================
-- 17. EXECUTE PAIRWISE MERGE
-- ============================================================

DO $$
DECLARE
    execution_id BIGINT;
BEGIN
    execution_id := execute_pairwise_merge(2);

    RAISE NOTICE 'Pairwise execution ID: %', execution_id;
END;
$$;

-- ============================================================
-- 18. RESULT RETRIEVAL
-- ============================================================

SELECT
    e.execution_id,
    j.job_name,
    e.strategy,
    r.result_position,
    r.result_value
FROM merge_executions e
JOIN merge_jobs j
    ON j.job_id = e.job_id
JOIN merge_results r
    ON r.execution_id = e.execution_id
ORDER BY e.execution_id, r.result_position;

-- ============================================================
-- 19. AGGREGATION AND EVALUATION
-- ============================================================

SELECT
    strategy,
    COUNT(*) AS execution_count,
    SUM(total_elements) AS processed_elements,
    AVG(elapsed_microseconds) AS average_elapsed_microseconds,
    MAX(elapsed_microseconds) AS maximum_elapsed_microseconds
FROM merge_executions
GROUP BY strategy
ORDER BY strategy;

SELECT *
FROM result_order_validation
ORDER BY execution_id;

-- ============================================================
-- 20. COMPARE BOTH MERGE STRATEGIES
-- ============================================================

WITH execution_results AS (
    SELECT
        e.job_id,
        e.execution_id,
        e.strategy,
        ARRAY_AGG(
            r.result_value
            ORDER BY r.result_position
        ) AS merged_values
    FROM merge_executions e
    JOIN merge_results r
        ON r.execution_id = e.execution_id
    GROUP BY e.job_id, e.execution_id, e.strategy
)
SELECT
    job_id,
    strategy,
    merged_values,
    cardinality(merged_values) AS result_size
FROM execution_results
ORDER BY job_id, strategy;

-- ============================================================
-- 21. DEMONSTRATE TRANSACTION ROLLBACK
-- ============================================================

-- The invalid insertion is deliberately isolated so that the
-- transaction rolls back without affecting the valid sample data.

DO $$
BEGIN
    BEGIN
        INSERT INTO source_elements (
            source_id,
            element_position,
            element_value
        )
        VALUES (1, 4, 2);

        RAISE EXCEPTION 'Expected ordering validation failure';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Invalid insertion rejected and rolled back: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 22. FAILURE AND STATE REPORTING
-- ============================================================

SELECT
    job_id,
    job_name,
    status,
    error_message,
    created_at,
    started_at,
    completed_at
FROM merge_jobs
ORDER BY job_id;

SELECT
    execution_id,
    job_id,
    strategy,
    total_sources,
    total_elements,
    elapsed_microseconds
FROM merge_executions
ORDER BY executed_at DESC;

-- ============================================================
-- 23. CLEANUP AND COMMIT
-- ============================================================

COMMIT;
