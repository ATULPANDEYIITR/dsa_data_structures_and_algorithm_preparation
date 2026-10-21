BEGIN;

DROP SCHEMA IF EXISTS hashing_assessment CASCADE;
CREATE SCHEMA hashing_assessment;
SET search_path TO hashing_assessment, public;

CREATE TABLE assessment_cases (
    case_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category TEXT NOT NULL CHECK (
        category IN ('frequency', 'duplicate', 'pair', 'prefix_sum',
                     'set_map', 'string_hash')
    ),
    case_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    expected_result JSONB NOT NULL
);

CREATE TABLE integer_inputs (
    case_id BIGINT NOT NULL REFERENCES assessment_cases(case_id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    value BIGINT NOT NULL,
    PRIMARY KEY (case_id, position)
);

CREATE TABLE string_inputs (
    case_id BIGINT NOT NULL REFERENCES assessment_cases(case_id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    value TEXT NOT NULL,
    PRIMARY KEY (case_id, position)
);

INSERT INTO assessment_cases (category, case_name, description, expected_result)
VALUES
    ('frequency', 'frequency-basic', 'Count each integer occurrence',
     '{"1":2,"2":3,"3":1}'::jsonb),
    ('duplicate', 'duplicates-basic', 'Report repeated values in order of second appearance',
     '[4,2]'::jsonb),
    ('pair', 'two-sum-basic', 'Find distinct positions summing to target 3',
     '{"target":3,"indices":[1,2]}'::jsonb),
    ('prefix_sum', 'subarray-zero', 'Count contiguous subarrays summing to zero',
     '{"target":0,"count":3}'::jsonb),
    ('set_map', 'consecutive-run', 'Find the longest consecutive integer run',
     '{"length":4}'::jsonb),
    ('string_hash', 'strings-basic', 'Group identical strings without trusting hash equality',
     '{"cat":2,"dog":1}'::jsonb);

INSERT INTO integer_inputs (case_id, position, value)
SELECT c.case_id, i.position, i.value
FROM (VALUES
    ('frequency-basic', ARRAY[1,2,2,3,1,2]::BIGINT[]),
    ('duplicates-basic', ARRAY[4,2,4,2,4,3]::BIGINT[]),
    ('two-sum-basic', ARRAY[3,-2,7,5]::BIGINT[]),
    ('subarray-zero', ARRAY[1,-1,0]::BIGINT[]),
    ('consecutive-run', ARRAY[100,4,200,1,3,2]::BIGINT[])
) AS source(case_name, values_array)
JOIN assessment_cases c USING (case_name)
CROSS JOIN LATERAL unnest(source.values_array) WITH ORDINALITY AS i(value, position);

INSERT INTO string_inputs (case_id, position, value)
SELECT c.case_id, i.position, i.value
FROM (VALUES
    ('strings-basic', ARRAY['cat','dog','cat']::TEXT[])
) AS source(case_name, values_array)
JOIN assessment_cases c USING (case_name)
CROSS JOIN LATERAL unnest(source.values_array) WITH ORDINALITY AS i(value, position);

CREATE INDEX integer_inputs_value_idx ON integer_inputs (value, case_id);
CREATE INDEX assessment_cases_category_idx ON assessment_cases (category);

-- Frequency queries group identical integer values within an assessment case.
CREATE VIEW frequency_report AS
SELECT c.case_name, i.value, COUNT(*) AS occurrences
FROM integer_inputs i
JOIN assessment_cases c USING (case_id)
WHERE c.category = 'frequency'
GROUP BY c.case_name, i.value;

-- A value is duplicated when it has more than one occurrence.
CREATE VIEW duplicate_report AS
SELECT c.case_name, i.value, COUNT(*) AS occurrences,
       MIN(i.position) AS first_position
FROM integer_inputs i
JOIN assessment_cases c USING (case_id)
WHERE c.category = 'duplicate'
GROUP BY c.case_name, i.value
HAVING COUNT(*) > 1;

-- Prefix sums count target-sum subarrays, including arrays with negative values.
CREATE FUNCTION count_subarrays_with_sum(p_case_id BIGINT, p_target BIGINT)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    current_prefix NUMERIC := 0;
    target_prefix NUMERIC;
    total_count BIGINT := 0;
    current_value BIGINT;
    prefix_counts JSONB := '{"0":1}'::jsonb;
    count_for_prefix BIGINT;
BEGIN
    FOR current_value IN
        SELECT value
        FROM integer_inputs
        WHERE case_id = p_case_id
        ORDER BY position
    LOOP
        current_prefix := current_prefix + current_value;
        target_prefix := current_prefix - p_target;

        -- JSONB object keys represent exact decimal prefix values.
        count_for_prefix := COALESCE(
            (prefix_counts ->> target_prefix::TEXT)::BIGINT, 0
        );
        total_count := total_count + count_for_prefix;

        prefix_counts := jsonb_set(
            prefix_counts,
            ARRAY[current_prefix::TEXT],
            to_jsonb(COALESCE(
                (prefix_counts ->> current_prefix::TEXT)::BIGINT, 0
            ) + 1),
            TRUE
        );
    END LOOP;

    RETURN total_count;
END;
$$;

-- Two-sum returns the first match encountered while scanning the right endpoint.
CREATE FUNCTION find_two_sum(p_case_id BIGINT, p_target BIGINT)
RETURNS TABLE(first_position INTEGER, second_position INTEGER)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    current_row RECORD;
    prior_row RECORD;
BEGIN
    FOR current_row IN
        SELECT position, value
        FROM integer_inputs
        WHERE case_id = p_case_id
        ORDER BY position
    LOOP
        SELECT i.position
        INTO first_position
        FROM integer_inputs i
        WHERE i.case_id = p_case_id
          AND i.position < current_row.position
          AND i.value::NUMERIC = p_target::NUMERIC - current_row.value::NUMERIC
        ORDER BY i.position
        LIMIT 1;

        IF FOUND THEN
            second_position := current_row.position;
            RETURN NEXT;
            RETURN;
        END IF;
    END LOOP;
END;
$$;

-- Consecutive-run calculation uses a distinct ordered set and breaks at gaps.
CREATE FUNCTION longest_consecutive_run(p_case_id BIGINT)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    WITH unique_values AS (
        SELECT DISTINCT value
        FROM integer_inputs
        WHERE case_id = p_case_id
    ),
    marked AS (
        SELECT value,
               CASE WHEN value::NUMERIC - 1 = LAG(value) OVER (ORDER BY value)
                    THEN 0 ELSE 1 END AS starts_run
        FROM unique_values
    ),
    numbered AS (
        SELECT value, SUM(starts_run) OVER (ORDER BY value) AS run_id
        FROM marked
    )
    SELECT COALESCE(MAX(run_length), 0)::INTEGER
    FROM (
        SELECT COUNT(*) AS run_length
        FROM numbered
        GROUP BY run_id
    ) runs;
$$;

-- A deterministic rolling hash is useful for bucket selection, not identity proof.
CREATE FUNCTION polynomial_string_hash(p_text TEXT)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result_hash BIGINT := 0;
    character_code BIGINT;
    index_position INTEGER;
BEGIN
    IF length(p_text) > 100000 THEN
        RAISE EXCEPTION 'String exceeds the 100000-character limit';
    END IF;

    FOR index_position IN 1..length(p_text) LOOP
        character_code := ascii(substr(p_text, index_position, 1));
        result_hash := mod(result_hash * 257 + character_code, 1000000007);
    END LOOP;

    RETURN result_hash;
END;
$$;

CREATE VIEW string_hash_report AS
SELECT case_id, value, polynomial_string_hash(value) AS hash_value,
       COUNT(*) AS occurrences
FROM string_inputs
GROUP BY case_id, value;

-- Execute reporting queries.
SELECT case_name, value, occurrences
FROM frequency_report
ORDER BY case_name, value;

SELECT case_name, value, occurrences
FROM duplicate_report
ORDER BY case_name, first_position;

SELECT count_subarrays_with_sum(
    (SELECT case_id FROM assessment_cases WHERE case_name = 'subarray-zero'),
    0
) AS zero_sum_subarray_count;

SELECT longest_consecutive_run(
    (SELECT case_id FROM assessment_cases WHERE case_name = 'consecutive-run')
) AS longest_run;

SELECT first_position, second_position
FROM find_two_sum(
    (SELECT case_id FROM assessment_cases WHERE case_name = 'two-sum-basic'),
    3
);

SELECT value, hash_value, occurrences
FROM string_hash_report
ORDER BY value;

-- This query groups by original text, so collisions cannot merge distinct strings.
SELECT value, COUNT(*) AS occurrences
FROM string_inputs
WHERE case_id = (SELECT case_id FROM assessment_cases WHERE case_name = 'strings-basic')
GROUP BY value
ORDER BY value;

-- Transactional validation ensures the seeded prefix-sum case returns three.
DO $$
DECLARE
    case_identifier BIGINT;
    result_count BIGINT;
BEGIN
    SELECT case_id INTO case_identifier
    FROM assessment_cases
    WHERE case_name = 'subarray-zero';

    result_count := count_subarrays_with_sum(case_identifier, 0);

    IF result_count <> 3 THEN
        RAISE EXCEPTION 'Prefix-sum assessment failed: expected 3, got %',
            result_count;
    END IF;
END;
$$;

COMMIT;
