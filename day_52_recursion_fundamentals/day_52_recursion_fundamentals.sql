BEGIN;

DROP VIEW IF EXISTS recursion_calculation_report;
DROP TABLE IF EXISTS recursion_run CASCADE;
DROP FUNCTION IF EXISTS recursive_factorial(INTEGER);
DROP FUNCTION IF EXISTS recursive_fibonacci(INTEGER);
DROP FUNCTION IF EXISTS recursive_power(BIGINT, INTEGER);
DROP FUNCTION IF EXISTS recursive_sum(INTEGER);
DROP FUNCTION IF EXISTS recursive_reverse(TEXT);
DROP FUNCTION IF EXISTS recursive_array_sum(INTEGER[]);

CREATE TABLE recursion_run (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation TEXT NOT NULL CHECK (
        operation IN (
            'factorial',
            'fibonacci',
            'power',
            'sum',
            'reverse',
            'array_sum'
        )
    ),
    input_value TEXT NOT NULL,
    result_value TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'success', 'rejected')),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    CHECK (
        (status = 'success' AND result_value IS NOT NULL
            AND error_message IS NULL AND completed_at IS NOT NULL)
        OR
        (status = 'rejected' AND error_message IS NOT NULL
            AND completed_at IS NOT NULL)
        OR
        (status = 'pending' AND completed_at IS NULL)
    )
);

CREATE INDEX recursion_run_operation_time_idx
    ON recursion_run (operation, created_at DESC);

-- PL/pgSQL functions use explicit base cases to stop recursion.
CREATE OR REPLACE FUNCTION recursive_factorial(n INTEGER)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF n < 0 THEN
        RAISE EXCEPTION 'Factorial requires n >= 0';
    END IF;
    IF n > 500 THEN
        RAISE EXCEPTION 'Factorial input exceeds demonstration limit';
    END IF;
    IF n <= 1 THEN
        RETURN 1;
    END IF;
    RETURN n::NUMERIC * recursive_factorial(n - 1);
END;
$$;

CREATE OR REPLACE FUNCTION recursive_fibonacci(n INTEGER)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF n < 0 THEN
        RAISE EXCEPTION 'Fibonacci requires n >= 0';
    END IF;
    IF n > 40 THEN
        RAISE EXCEPTION 'Fibonacci input exceeds demonstration limit';
    END IF;
    IF n <= 1 THEN
        RETURN n;
    END IF;
    RETURN recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2);
END;
$$;

CREATE OR REPLACE FUNCTION recursive_power(base_value BIGINT, exponent INTEGER)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    half_power NUMERIC;
    squared NUMERIC;
BEGIN
    IF exponent < 0 THEN
        RAISE EXCEPTION 'Exponent must be non-negative';
    END IF;
    IF exponent > 1000 THEN
        RAISE EXCEPTION 'Exponent exceeds demonstration limit';
    END IF;
    IF exponent = 0 THEN
        RETURN 1;
    END IF;

    half_power := recursive_power(base_value, exponent / 2);
    squared := half_power * half_power;

    IF exponent % 2 = 0 THEN
        RETURN squared;
    END IF;
    RETURN base_value::NUMERIC * squared;
END;
$$;

CREATE OR REPLACE FUNCTION recursive_sum(n INTEGER)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF n < 0 THEN
        RAISE EXCEPTION 'Sum requires n >= 0';
    END IF;
    IF n > 100000 THEN
        RAISE EXCEPTION 'Sum input exceeds demonstration limit';
    END IF;
    IF n = 0 THEN
        RETURN 0;
    END IF;
    RETURN n::BIGINT + recursive_sum(n - 1);
END;
$$;

CREATE OR REPLACE FUNCTION recursive_reverse(value TEXT)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF char_length(value) <= 1 THEN
        RETURN value;
    END IF;
    RETURN recursive_reverse(substr(value, 2))
        || substr(value, 1, 1);
END;
$$;

CREATE OR REPLACE FUNCTION recursive_array_sum(values INTEGER[], idx INTEGER DEFAULT 1)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    current_value INTEGER;
BEGIN
    IF values IS NULL THEN
        RAISE EXCEPTION 'Array must not be NULL';
    END IF;
    IF idx < 1 OR idx > cardinality(values) + 1 THEN
        RAISE EXCEPTION 'Index is outside the array';
    END IF;
    IF idx = cardinality(values) + 1 THEN
        RETURN 0;
    END IF;

    current_value := values[idx];
    IF current_value IS NULL THEN
        RAISE EXCEPTION 'Array elements must not be NULL';
    END IF;

    RETURN current_value::BIGINT
        + recursive_array_sum(values, idx + 1);
END;
$$;

CREATE OR REPLACE VIEW recursion_calculation_report AS
SELECT
    operation,
    status,
    COUNT(*) AS run_count,
    MIN(created_at) AS first_run,
    MAX(created_at) AS latest_run
FROM recursion_run
GROUP BY operation, status;

-- Record successful results using a single insert per calculation.
INSERT INTO recursion_run
    (operation, input_value, result_value, status, completed_at)
VALUES
    ('factorial', '5', recursive_factorial(5)::TEXT,
        'success', CURRENT_TIMESTAMP),
    ('fibonacci', '10', recursive_fibonacci(10)::TEXT,
        'success', CURRENT_TIMESTAMP),
    ('power', '2^10', recursive_power(2, 10)::TEXT,
        'success', CURRENT_TIMESTAMP),
    ('sum', '10', recursive_sum(10)::TEXT,
        'success', CURRENT_TIMESTAMP),
    ('reverse', 'recursion', recursive_reverse('recursion'),
        'success', CURRENT_TIMESTAMP),
    ('array_sum', '{7,2,9,4,1}',
        recursive_array_sum(ARRAY[7,2,9,4,1])::TEXT,
        'success', CURRENT_TIMESTAMP);

-- A PL/pgSQL block demonstrates isolated rejection without aborting the script.
DO $$
DECLARE
    rejected_message TEXT;
BEGIN
    BEGIN
        PERFORM recursive_factorial(-1);
    EXCEPTION WHEN OTHERS THEN
        rejected_message := SQLERRM;
    END;

    INSERT INTO recursion_run
        (operation, input_value, status, error_message, completed_at)
    VALUES
        ('factorial', '-1', 'rejected',
            rejected_message, CURRENT_TIMESTAMP);
END;
$$;

-- A recursive CTE exposes call depth and pending recursive state.
WITH RECURSIVE factorial_frames(n, depth) AS (
    SELECT 4, 0
    UNION ALL
    SELECT n - 1, depth + 1
    FROM factorial_frames
    WHERE n > 1
)
SELECT n, depth, repeat('  ', depth) || 'factorial(' || n || ')' AS call_frame
FROM factorial_frames
ORDER BY depth;

-- CTE-based sequence evaluation provides an independent sum calculation.
WITH RECURSIVE integer_sequence(n) AS (
    SELECT 0
    UNION ALL
    SELECT n + 1
    FROM integer_sequence
    WHERE n < 10
)
SELECT SUM(n) AS verified_sum
FROM integer_sequence;

SELECT * FROM recursion_run ORDER BY run_id;
SELECT * FROM recursion_calculation_report ORDER BY operation, status;

-- Demonstrate atomic rollback using a savepoint.
SAVEPOINT before_optional_calculation;
INSERT INTO recursion_run
    (operation, input_value, result_value, status, completed_at)
VALUES
    ('sum', '3', recursive_sum(3)::TEXT, 'success', CURRENT_TIMESTAMP);
ROLLBACK TO SAVEPOINT before_optional_calculation;
RELEASE SAVEPOINT before_optional_calculation;

COMMIT;
