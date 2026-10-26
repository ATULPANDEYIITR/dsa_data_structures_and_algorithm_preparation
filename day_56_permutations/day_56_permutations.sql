DROP SCHEMA IF EXISTS permutation_lab CASCADE;
CREATE SCHEMA permutation_lab;

SET search_path = permutation_lab, public;

-- Input values are stored by position so duplicate values remain meaningful.
CREATE TABLE permutation_input (
    input_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    values_text TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (cardinality(values_text) <= 9),
    CHECK (cardinality(values_text) >= 0)
);

CREATE TABLE permutation_result (
    result_id BIGSERIAL PRIMARY KEY,
    input_id BIGINT NOT NULL
        REFERENCES permutation_input(input_id) ON DELETE CASCADE,
    method TEXT NOT NULL
        CHECK (method IN ('used_array', 'swap')),
    permutation TEXT[] NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_permutation_result_input_method
    ON permutation_result(input_id, method);

-- Factorial is intentionally implemented with bigint because the sample
-- workload is restricted to at most nine input elements.
CREATE OR REPLACE FUNCTION factorial_bigint(n INTEGER)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result BIGINT := 1;
    i INTEGER;
BEGIN
    IF n < 0 THEN
        RAISE EXCEPTION 'Factorial input cannot be negative: %', n;
    END IF;

    FOR i IN 2..n LOOP
        result := result * i;
    END LOOP;

    RETURN result;
END;
$$;

-- Returns n! divided by the factorial of every duplicate-value frequency.
CREATE OR REPLACE FUNCTION unique_permutation_count(input_values TEXT[])
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    n INTEGER := cardinality(input_values);
    result BIGINT;
    frequency RECORD;
BEGIN
    IF n > 9 THEN
        RAISE EXCEPTION
            'Exhaustive permutation generation supports at most 9 values';
    END IF;

    result := factorial_bigint(n);

    FOR frequency IN
        SELECT value, COUNT(*)::INTEGER AS frequency
        FROM unnest(input_values) AS value
        GROUP BY value
    LOOP
        result := result / factorial_bigint(frequency.frequency);
    END LOOP;

    RETURN result;
END;
$$;

-- Recursive CTE using a used-position array.
CREATE OR REPLACE FUNCTION generate_used_array_permutations(
    p_values TEXT[]
)
RETURNS TABLE(permutation TEXT[])
LANGUAGE sql
AS $$
    WITH RECURSIVE permutations AS (
        SELECT
            ARRAY[]::TEXT[] AS permutation,
            ARRAY[]::INTEGER[] AS used_positions

        UNION ALL

        SELECT
            p.permutation || v.value,
            p.used_positions || v.position
        FROM permutations p
        CROSS JOIN LATERAL (
            SELECT
                value,
                position
            FROM unnest(p_values)
                WITH ORDINALITY AS u(value, position)
            WHERE NOT (position::INTEGER = ANY(p.used_positions))
        ) v
        WHERE cardinality(p.permutation) < cardinality(p_values)
    )
    SELECT DISTINCT p.permutation
    FROM permutations p
    WHERE cardinality(p.permutation) = cardinality(p_values);
$$;

-- The swap algorithm is represented relationally by recursive prefix
-- construction. PostgreSQL has no native array-swap recursion primitive,
-- so the database representation focuses on the same permutation state:
-- a prefix plus the remaining values.
CREATE OR REPLACE FUNCTION generate_remaining_value_permutations(
    p_values TEXT[]
)
RETURNS TABLE(permutation TEXT[])
LANGUAGE sql
AS $$
    WITH RECURSIVE permutations AS (
        SELECT
            ARRAY[]::TEXT[] AS prefix,
            p_values AS remaining

        UNION ALL

        SELECT
            p.prefix || chosen.value,
            ARRAY(
                SELECT value
                FROM unnest(p.remaining) WITH ORDINALITY AS r(value, ord)
                WHERE r.ord <> chosen.ord
            )
        FROM permutations p
        CROSS JOIN LATERAL (
            SELECT value, ord
            FROM unnest(p.remaining) WITH ORDINALITY AS r(value, ord)
        ) chosen
        WHERE cardinality(p.remaining) > 0
    )
    SELECT DISTINCT prefix
    FROM permutations
    WHERE cardinality(prefix) = cardinality(p_values);
$$;

-- Sample inputs.
INSERT INTO permutation_input (name, values_text)
VALUES
    ('distinct_abc', ARRAY['A', 'B', 'C']),
    ('duplicate_aab', ARRAY['A', 'A', 'B']),
    ('four_values', ARRAY['1', '2', '3', '4']),
    ('empty_input', ARRAY[]::TEXT[]);

-- Generate and store used-array results.
INSERT INTO permutation_result (input_id, method, permutation)
SELECT
    i.input_id,
    'used_array',
    p.permutation
FROM permutation_input i
CROSS JOIN LATERAL generate_used_array_permutations(i.values_text) p
WHERE i.name IN ('distinct_abc', 'duplicate_aab');

-- Generate and store the relational remaining-value results as the
-- database counterpart of swap-style recursive generation.
INSERT INTO permutation_result (input_id, method, permutation)
SELECT
    i.input_id,
    'swap',
    p.permutation
FROM permutation_input i
CROSS JOIN LATERAL generate_remaining_value_permutations(i.values_text) p
WHERE i.name IN ('distinct_abc', 'duplicate_aab');

-- Basic retrieval.
SELECT
    i.name,
    r.method,
    r.permutation
FROM permutation_result r
JOIN permutation_input i
    ON i.input_id = r.input_id
ORDER BY i.name, r.method, r.permutation;

-- Expected cardinality versus generated cardinality.
SELECT
    i.name,
    unique_permutation_count(i.values_text) AS expected_count,
    COUNT(r.result_id) FILTER (WHERE r.method = 'used_array')
        AS used_array_count,
    COUNT(r.result_id) FILTER (WHERE r.method = 'swap')
        AS swap_count
FROM permutation_input i
LEFT JOIN permutation_result r
    ON r.input_id = i.input_id
GROUP BY i.input_id, i.name, i.values_text
ORDER BY i.name;

-- Verify that duplicate permutations are not present within a method.
SELECT
    i.name,
    r.method,
    COUNT(*) AS rows_generated,
    COUNT(DISTINCT r.permutation) AS distinct_permutations
FROM permutation_result r
JOIN permutation_input i
    ON i.input_id = r.input_id
GROUP BY i.name, r.method
ORDER BY i.name, r.method;

-- Show the mathematical count for every input, including the empty input.
SELECT
    name,
    cardinality(values_text) AS input_size,
    unique_permutation_count(values_text) AS unique_permutations
FROM permutation_input
ORDER BY input_id;

-- Validation query: a result set is correct only when its number of unique
-- rows equals the mathematical number of unique permutations.
WITH validation AS (
    SELECT
        i.name,
        r.method,
        unique_permutation_count(i.values_text) AS expected_count,
        COUNT(DISTINCT r.permutation) AS actual_count
    FROM permutation_input i
    LEFT JOIN permutation_result r
        ON r.input_id = i.input_id
    GROUP BY i.name, i.values_text, r.method
)
SELECT
    name,
    method,
    expected_count,
    actual_count,
    expected_count = actual_count AS valid
FROM validation
ORDER BY name, method;

-- Transactional demonstration. The temporary records are rolled back,
-- proving that permutation persistence can participate in normal database
-- transaction semantics.
BEGIN;

INSERT INTO permutation_input (name, values_text)
VALUES ('transaction_test', ARRAY['X', 'Y']);

INSERT INTO permutation_result (input_id, method, permutation)
SELECT
    input_id,
    'used_array',
    p.permutation
FROM permutation_input
CROSS JOIN LATERAL generate_used_array_permutations(values_text) p
WHERE name = 'transaction_test';

ROLLBACK;

SELECT COUNT(*) AS rolled_back_rows
FROM permutation_input
WHERE name = 'transaction_test';
