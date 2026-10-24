-- PostgreSQL 14+
-- Subsequence generation, sum counting, and repository-change analysis.

BEGIN;

CREATE SCHEMA IF NOT EXISTS subsequence_lab;
SET search_path TO subsequence_lab, public;

CREATE TABLE IF NOT EXISTS exercises (
    exercise_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE,
    description text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS exercise_values (
    exercise_id bigint NOT NULL REFERENCES exercises(exercise_id)
        ON DELETE CASCADE,
    position integer NOT NULL CHECK (position >= 1),
    value bigint NOT NULL,
    PRIMARY KEY (exercise_id, position)
);

CREATE TABLE IF NOT EXISTS targets (
    exercise_id bigint NOT NULL REFERENCES exercises(exercise_id)
        ON DELETE CASCADE,
    target_sum bigint NOT NULL,
    PRIMARY KEY (exercise_id, target_sum)
);

CREATE TABLE IF NOT EXISTS repository_changes (
    change_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name text NOT NULL,
    pull_request_number integer NOT NULL CHECK (pull_request_number > 0),
    change_position integer NOT NULL CHECK (change_position >= 1),
    change_value bigint NOT NULL,
    checks_passed boolean NOT NULL DEFAULT false,
    approved boolean NOT NULL DEFAULT false,
    closed boolean NOT NULL DEFAULT false,
    UNIQUE (repository_name, pull_request_number, change_position)
);

CREATE INDEX IF NOT EXISTS idx_exercise_values_position
    ON exercise_values (exercise_id, position);

CREATE INDEX IF NOT EXISTS idx_repository_changes_pr
    ON repository_changes (repository_name, pull_request_number);

INSERT INTO exercises (name, description)
VALUES
    ('basic', 'Generate subsequences for a short integer sequence'),
    ('zeros', 'Count index-distinct subsequences containing zero values'),
    ('negative', 'Verify subsequence sums with negative values')
ON CONFLICT (name) DO NOTHING;

INSERT INTO exercise_values (exercise_id, position, value)
SELECT e.exercise_id, v.position, v.value
FROM exercises e
JOIN (VALUES
    ('basic', 1, 1::bigint),
    ('basic', 2, 2::bigint),
    ('basic', 3, 3::bigint),
    ('zeros', 1, 0::bigint),
    ('zeros', 2, 0::bigint),
    ('negative', 1, -2::bigint),
    ('negative', 2, 5::bigint)
) AS v(exercise_name, position, value)
ON e.name = v.exercise_name
ON CONFLICT (exercise_id, position) DO NOTHING;

INSERT INTO targets (exercise_id, target_sum)
SELECT e.exercise_id, t.target_sum
FROM exercises e
JOIN (VALUES
    ('basic', 3::bigint),
    ('basic', 6::bigint),
    ('zeros', 0::bigint),
    ('negative', 3::bigint)
) AS t(exercise_name, target_sum)
ON e.name = t.exercise_name
ON CONFLICT DO NOTHING;

INSERT INTO repository_changes (
    repository_name, pull_request_number, change_position, change_value,
    checks_passed, approved, closed
)
VALUES
    ('operations-platform', 104, 1, 1, true, true, false),
    ('operations-platform', 104, 2, 2, true, true, false),
    ('operations-platform', 104, 3, 3, true, true, false),
    ('operations-platform', 105, 1, 5, true, true, false),
    ('operations-platform', 105, 2, 7, true, true, false),
    ('operations-platform', 106, 1, 1, false, false, false)
ON CONFLICT (repository_name, pull_request_number, change_position)
DO NOTHING;

-- A recursive CTE enumerates include/exclude choices by input position.
-- Each row is one index-based subsequence, including the empty subsequence.
CREATE OR REPLACE FUNCTION generate_subsequences(p_exercise_id bigint)
RETURNS TABLE (selected_values bigint[], subsequence_sum numeric)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE input_values AS (
        SELECT position, value
        FROM exercise_values
        WHERE exercise_id = p_exercise_id
    ),
    choices(position, selected_values, subsequence_sum) AS (
        SELECT 0, ARRAY[]::bigint[], 0::numeric
        UNION ALL
        SELECT
            c.position + 1,
            c.selected_values,
            c.subsequence_sum
        FROM choices c
        WHERE c.position < (
            SELECT count(*) FROM input_values
        )
        UNION ALL
        SELECT
            c.position + 1,
            c.selected_values || v.value,
            c.subsequence_sum + v.value::numeric
        FROM choices c
        JOIN input_values v
          ON v.position = c.position + 1
        WHERE c.position < (
            SELECT count(*) FROM input_values
        )
    )
    SELECT selected_values, subsequence_sum
    FROM choices
    WHERE position = (SELECT count(*) FROM input_values)
$$;

-- The dynamic-programming implementation stores one count per reachable sum.
-- Numeric avoids overflow when subsequence counts exceed bigint capacity.
CREATE OR REPLACE FUNCTION count_subsequences_with_sum(
    p_exercise_id bigint,
    p_target bigint
)
RETURNS numeric
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    current_value bigint;
    current_counts jsonb := '{"0": 1}';
    next_counts jsonb;
    item record;
    new_sum text;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM exercises WHERE exercise_id = p_exercise_id
    ) THEN
        RAISE EXCEPTION 'Unknown exercise ID: %', p_exercise_id;
    END IF;

    FOR current_value IN
        SELECT value
        FROM exercise_values
        WHERE exercise_id = p_exercise_id
        ORDER BY position
    LOOP
        next_counts := current_counts;

        FOR item IN
            SELECT key, value::text::numeric AS count
            FROM jsonb_each(current_counts)
        LOOP
            new_sum := (item.key::numeric + current_value)::text;

            next_counts := jsonb_set(
                next_counts,
                ARRAY[new_sum],
                to_jsonb(
                    COALESCE((next_counts ->> new_sum)::numeric, 0)
                    + item.count
                ),
                true
            );
        END LOOP;

        current_counts := next_counts;
    END LOOP;

    RETURN COALESCE((current_counts ->> p_target::text)::numeric, 0);
END;
$$;

CREATE OR REPLACE VIEW target_sum_report AS
SELECT
    e.name AS exercise,
    t.target_sum,
    count_subsequences_with_sum(e.exercise_id, t.target_sum) AS matching_count,
    (count_subsequences_with_sum(e.exercise_id, t.target_sum) > 0) AS exists
FROM exercises e
JOIN targets t ON t.exercise_id = e.exercise_id;

CREATE OR REPLACE VIEW pull_request_sum_report AS
SELECT
    repository_name,
    pull_request_number,
    count(*) AS change_count,
    sum(change_value::numeric) AS total_change_value,
    bool_and(checks_passed) AS all_checks_passed,
    bool_and(approved) AS all_approved,
    bool_and(NOT closed) AS remains_open
FROM repository_changes
GROUP BY repository_name, pull_request_number;

-- Eligibility is a demonstration policy: checks and approval must pass,
-- and at least one subsequence of change values must sum to the requested target.
CREATE OR REPLACE FUNCTION evaluate_pull_request(
    p_repository text,
    p_pr integer,
    p_target bigint
)
RETURNS TABLE (
    repository text,
    pull_request integer,
    target_sum bigint,
    matching_subsequences numeric,
    checks_pass boolean,
    approval_pass boolean,
    is_open boolean,
    merge_eligible boolean
)
LANGUAGE sql
STABLE
AS $$
    WITH pr AS (
        SELECT
            c.repository_name,
            c.pull_request_number,
            bool_and(c.checks_passed) AS checks_pass,
            bool_and(c.approved) AS approval_pass,
            bool_and(NOT c.closed) AS is_open,
            array_agg(c.change_value ORDER BY c.change_position) AS values
        FROM repository_changes c
        WHERE c.repository_name = p_repository
          AND c.pull_request_number = p_pr
        GROUP BY c.repository_name, c.pull_request_number
    ),
    counts AS (
        SELECT count(*)::numeric AS matching_subsequences
        FROM pr
        CROSS JOIN LATERAL unnest(
            ARRAY(
                SELECT 0::bigint
                UNION ALL
                SELECT unnest(pr.values)
            )
        ) AS ignored(value)
    )
    SELECT
        pr.repository_name,
        pr.pull_request_number,
        p_target,
        (
            SELECT count(*)::numeric
            FROM generate_subsequences_for_array(pr.values) s
            WHERE s.subsequence_sum = p_target::numeric
        ),
        pr.checks_pass,
        pr.approval_pass,
        pr.is_open,
        pr.checks_pass AND pr.approval_pass AND pr.is_open
          AND EXISTS (
              SELECT 1
              FROM generate_subsequences_for_array(pr.values) s
              WHERE s.subsequence_sum = p_target::numeric
          )
    FROM pr
$$;

-- Array-based counterpart used for repository changes.
CREATE OR REPLACE FUNCTION generate_subsequences_for_array(p_values bigint[])
RETURNS TABLE (selected_values bigint[], subsequence_sum numeric)
LANGUAGE sql
IMMUTABLE
AS $$
    WITH RECURSIVE choices(position, selected_values, subsequence_sum) AS (
        SELECT 0, ARRAY[]::bigint[], 0::numeric
        UNION ALL
        SELECT
            c.position + 1,
            c.selected_values,
            c.subsequence_sum
        FROM choices c
        WHERE c.position < cardinality(p_values)
        UNION ALL
        SELECT
            c.position + 1,
            c.selected_values || p_values[c.position + 1],
            c.subsequence_sum + p_values[c.position + 1]::numeric
        FROM choices c
        WHERE c.position < cardinality(p_values)
    )
    SELECT selected_values, subsequence_sum
    FROM choices
    WHERE position = cardinality(p_values)
$$;

-- The view and functions can be queried after this transaction commits.
COMMIT;

SELECT * FROM target_sum_report ORDER BY exercise, target_sum;

SELECT
    exercise,
    selected_values,
    subsequence_sum
FROM generate_subsequences(
    (SELECT exercise_id FROM exercises WHERE name = 'basic')
)
ORDER BY cardinality(selected_values), selected_values;

SELECT *
FROM pull_request_sum_report
ORDER BY repository_name, pull_request_number;

SELECT *
FROM evaluate_pull_request('operations-platform', 104, 3);

SELECT *
FROM evaluate_pull_request('operations-platform', 105, 3);

SELECT *
FROM evaluate_pull_request('operations-platform', 106, 3);
