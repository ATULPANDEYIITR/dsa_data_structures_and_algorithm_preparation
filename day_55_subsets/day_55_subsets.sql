BEGIN;

DROP SCHEMA IF EXISTS subset_lab CASCADE;
CREATE SCHEMA subset_lab;
SET search_path TO subset_lab, public;

CREATE TABLE subset_jobs (
    job_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_name text NOT NULL UNIQUE,
    target_sum bigint,
    min_size integer NOT NULL DEFAULT 0 CHECK (min_size >= 0),
    max_size integer NOT NULL CHECK (max_size >= 0),
    min_sum bigint,
    max_sum bigint,
    unique_values boolean NOT NULL DEFAULT true,
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (min_size <= max_size),
    CHECK (min_sum IS NULL OR max_sum IS NULL OR min_sum <= max_sum)
);

CREATE TABLE subset_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id bigint NOT NULL REFERENCES subset_jobs(job_id) ON DELETE CASCADE,
    position integer NOT NULL CHECK (position >= 0),
    item_value integer NOT NULL,
    UNIQUE (job_id, position)
);

CREATE TABLE subset_results (
    result_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id bigint NOT NULL REFERENCES subset_jobs(job_id) ON DELETE CASCADE,
    ordinal integer NOT NULL CHECK (ordinal >= 0),
    subset_values integer[] NOT NULL,
    subset_size integer NOT NULL CHECK (subset_size >= 0),
    subset_sum bigint NOT NULL,
    UNIQUE (job_id, ordinal),
    CHECK (cardinality(subset_values) = subset_size)
);

CREATE INDEX subset_items_job_position_idx
    ON subset_items(job_id, position);

CREATE INDEX subset_results_job_sum_idx
    ON subset_results(job_id, subset_sum);

CREATE INDEX subset_results_job_size_idx
    ON subset_results(job_id, subset_size);

-- Each job can be processed only from pending or failed state.
CREATE FUNCTION validate_job_transition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        IF NOT (
            (OLD.status IN ('pending', 'failed') AND NEW.status = 'running')
            OR (OLD.status = 'running' AND NEW.status IN ('completed', 'failed'))
        ) THEN
            RAISE EXCEPTION 'Invalid job transition: % -> %',
                OLD.status, NEW.status;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER subset_job_transition_trigger
BEFORE UPDATE OF status ON subset_jobs
FOR EACH ROW EXECUTE FUNCTION validate_job_transition();

-- Prevent results from violating size and sum constraints.
CREATE FUNCTION validate_subset_result()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    job subset_jobs%ROWTYPE;
    calculated_sum bigint;
    calculated_size integer;
BEGIN
    SELECT * INTO STRICT job
    FROM subset_jobs
    WHERE job_id = NEW.job_id;

    IF job.status <> 'running' THEN
        RAISE EXCEPTION 'Results can only be written while a job is running';
    END IF;

    calculated_size := cardinality(NEW.subset_values);

    SELECT COALESCE(sum(value::bigint), 0)
    INTO calculated_sum
    FROM unnest(NEW.subset_values) AS item(value);

    IF calculated_size <> NEW.subset_size THEN
        RAISE EXCEPTION 'Subset size does not match its values';
    END IF;

    IF calculated_sum <> NEW.subset_sum THEN
        RAISE EXCEPTION 'Subset sum does not match its values';
    END IF;

    IF calculated_size < job.min_size OR calculated_size > job.max_size THEN
        RAISE EXCEPTION 'Subset violates size constraints';
    END IF;

    IF job.min_sum IS NOT NULL AND calculated_sum < job.min_sum THEN
        RAISE EXCEPTION 'Subset is below the minimum sum';
    END IF;

    IF job.max_sum IS NOT NULL AND calculated_sum > job.max_sum THEN
        RAISE EXCEPTION 'Subset exceeds the maximum sum';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER subset_result_validation_trigger
BEFORE INSERT OR UPDATE ON subset_results
FOR EACH ROW EXECUTE FUNCTION validate_subset_result();

-- Enumerate subsets using recursive decisions for each input position.
-- This implementation is intended for small inputs because enumeration is exponential.
CREATE PROCEDURE enumerate_subsets(p_job_id bigint)
LANGUAGE plpgsql
AS $$
DECLARE
    job subset_jobs%ROWTYPE;
    item_count integer;
BEGIN
    SELECT * INTO STRICT job
    FROM subset_jobs
    WHERE job_id = p_job_id
    FOR UPDATE;

    IF job.status NOT IN ('pending', 'failed') THEN
        RAISE EXCEPTION 'Job % is not eligible to run', p_job_id;
    END IF;

    SELECT count(*) INTO item_count
    FROM subset_items
    WHERE job_id = p_job_id;

    IF job.max_size > item_count THEN
        RAISE EXCEPTION 'max_size exceeds input element count';
    END IF;

    UPDATE subset_jobs SET status = 'running'
    WHERE job_id = p_job_id;

    DELETE FROM subset_results WHERE job_id = p_job_id;

    INSERT INTO subset_results (
        job_id, ordinal, subset_values, subset_size, subset_sum
    )
    WITH RECURSIVE choices AS (
        SELECT
            0 AS step,
            ARRAY[]::integer[] AS chosen,
            0::bigint AS total
        UNION ALL
        SELECT
            c.step + 1,
            CASE WHEN decision.include_item
                THEN c.chosen || i.item_value
                ELSE c.chosen
            END,
            c.total + CASE WHEN decision.include_item
                THEN i.item_value::bigint ELSE 0::bigint END
        FROM choices c
        JOIN subset_items i
          ON i.job_id = p_job_id
         AND i.position = c.step
        CROSS JOIN (VALUES (false), (true)) AS decision(include_item)
        WHERE c.step < item_count
    ),
    candidates AS (
        SELECT chosen, total
        FROM choices
        WHERE step = item_count
          AND cardinality(chosen) BETWEEN job.min_size AND job.max_size
          AND (job.min_sum IS NULL OR total >= job.min_sum)
          AND (job.max_sum IS NULL OR total <= job.max_sum)
          AND (job.target_sum IS NULL OR total = job.target_sum)
    ),
    deduplicated AS (
        SELECT DISTINCT chosen, total
        FROM candidates
        WHERE job.unique_values
        UNION ALL
        SELECT chosen, total
        FROM candidates
        WHERE NOT job.unique_values
    ),
    numbered AS (
        SELECT
            row_number() OVER (ORDER BY chosen, total)::integer - 1 AS ordinal,
            chosen,
            total
        FROM deduplicated
    )
    SELECT
        p_job_id,
        ordinal,
        chosen,
        cardinality(chosen),
        total
    FROM numbered;

    UPDATE subset_jobs SET status = 'completed'
    WHERE job_id = p_job_id;

EXCEPTION
    WHEN OTHERS THEN
        UPDATE subset_jobs
        SET status = 'failed'
        WHERE job_id = p_job_id AND status = 'running';
        RAISE;
END;
$$;

-- The DISTINCT policy deduplicates equal arrays. It preserves a single empty subset.
INSERT INTO subset_jobs (
    job_name, target_sum, min_size, max_size, min_sum, max_sum, unique_values
) VALUES
    ('target-four', 4, 0, 4, NULL, NULL, true),
    ('bounded-subsets', NULL, 2, 3, 4, 6, true),
    ('zero-target', 0, 0, 2, NULL, NULL, true);

INSERT INTO subset_items(job_id, position, item_value)
SELECT j.job_id, i.position, i.item_value
FROM (VALUES
    ('target-four', 0, 1),
    ('target-four', 1, 2),
    ('target-four', 2, 2),
    ('target-four', 3, 3),
    ('bounded-subsets', 0, 1),
    ('bounded-subsets', 1, 2),
    ('bounded-subsets', 2, 2),
    ('bounded-subsets', 3, 3),
    ('zero-target', 0, 0),
    ('zero-target', 1, 0)
) AS i(job_name, position, item_value)
JOIN subset_jobs j USING (job_name);

CALL enumerate_subsets(
    (SELECT job_id FROM subset_jobs WHERE job_name = 'target-four')
);

CALL enumerate_subsets(
    (SELECT job_id FROM subset_jobs WHERE job_name = 'bounded-subsets')
);

CALL enumerate_subsets(
    (SELECT job_id FROM subset_jobs WHERE job_name = 'zero-target')
);

-- Retrieval: enumerate the actual subsets, not only their totals.
SELECT j.job_name, r.ordinal, r.subset_values, r.subset_size, r.subset_sum
FROM subset_results r
JOIN subset_jobs j USING (job_id)
ORDER BY j.job_name, r.ordinal;

-- Aggregation: measure the result space for each job.
SELECT
    j.job_name,
    j.status,
    count(r.result_id) AS result_count,
    min(r.subset_sum) AS smallest_sum,
    max(r.subset_sum) AS largest_sum,
    avg(r.subset_size)::numeric(10, 2) AS average_size
FROM subset_jobs j
LEFT JOIN subset_results r USING (job_id)
GROUP BY j.job_id, j.job_name, j.status
ORDER BY j.job_id;

-- Eligibility report: every stored result has passed trigger validation.
SELECT
    job_name,
    count(*) FILTER (WHERE subset_size = 0) AS empty_subsets,
    count(*) FILTER (WHERE subset_sum = 0) AS zero_sum_subsets,
    count(*) FILTER (WHERE subset_sum = 4) AS target_four_subsets
FROM subset_jobs
JOIN subset_results USING (job_id)
GROUP BY job_name
ORDER BY job_name;

-- Demonstrate database-level rejection without aborting the complete script.
DO $$
DECLARE
    job_id_value bigint;
BEGIN
    SELECT job_id INTO job_id_value
    FROM subset_jobs WHERE job_name = 'target-four';

    BEGIN
        INSERT INTO subset_results(
            job_id, ordinal, subset_values, subset_size, subset_sum
        ) VALUES (
            job_id_value, 999999, ARRAY[100], 1, 100
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected invalid-result rejection: %', SQLERRM;
    END;
END;
$$;

COMMIT;
