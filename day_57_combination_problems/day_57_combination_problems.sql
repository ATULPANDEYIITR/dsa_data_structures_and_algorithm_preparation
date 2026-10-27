DROP SCHEMA IF EXISTS combination_lab CASCADE;
CREATE SCHEMA combination_lab;

SET search_path = combination_lab, public;

-- Candidate values represent selectable components in a constrained
-- combinatorial planning problem.
CREATE TABLE candidate_values (
    candidate_id BIGSERIAL PRIMARY KEY,
    value INTEGER NOT NULL CHECK (value > 0),
    label TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE combination_problems (
    problem_id BIGSERIAL PRIMARY KEY,
    problem_name TEXT NOT NULL UNIQUE,
    target_sum INTEGER NOT NULL CHECK (target_sum >= 0),
    combination_size INTEGER CHECK (combination_size >= 0),
    allow_reuse BOOLEAN NOT NULL DEFAULT FALSE,
    minimum_sum INTEGER,
    maximum_sum INTEGER,
    CHECK (
        minimum_sum IS NULL
        OR maximum_sum IS NULL
        OR minimum_sum <= maximum_sum
    )
);

CREATE TABLE problem_candidates (
    problem_id BIGINT NOT NULL
        REFERENCES combination_problems(problem_id)
        ON DELETE CASCADE,
    candidate_id BIGINT NOT NULL
        REFERENCES candidate_values(candidate_id),
    PRIMARY KEY (problem_id, candidate_id)
);

CREATE TABLE generated_combinations (
    combination_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL
        REFERENCES combination_problems(problem_id)
        ON DELETE CASCADE,
    combination_key TEXT NOT NULL,
    total_sum INTEGER NOT NULL,
    combination_size INTEGER NOT NULL CHECK (combination_size >= 0),
    UNIQUE (problem_id, combination_key)
);

CREATE TABLE combination_members (
    combination_id BIGINT NOT NULL
        REFERENCES generated_combinations(combination_id)
        ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 1),
    candidate_id BIGINT NOT NULL
        REFERENCES candidate_values(candidate_id),
    PRIMARY KEY (combination_id, position)
);

CREATE INDEX idx_problem_candidates_candidate
    ON problem_candidates(candidate_id);

CREATE INDEX idx_generated_combinations_problem_sum
    ON generated_combinations(problem_id, total_sum);

CREATE TABLE evaluation_runs (
    run_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL
        REFERENCES combination_problems(problem_id),
    status TEXT NOT NULL CHECK (
        status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')
    ),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failure_reason TEXT
);

INSERT INTO candidate_values (value, label) VALUES
    (2, 'two'),
    (3, 'three'),
    (5, 'five'),
    (7, 'seven'),
    (11, 'eleven'),
    (13, 'thirteen');

INSERT INTO combination_problems (
    problem_name,
    target_sum,
    combination_size,
    allow_reuse,
    minimum_sum,
    maximum_sum
) VALUES
    ('fixed-size review set', 12, 3, FALSE, 12, 18),
    ('unique target sum', 10, NULL, FALSE, 10, 10),
    ('reusable target sum', 8, NULL, TRUE, 8, 8),
    ('impossible constraint', 5, 4, FALSE, 30, 20);

-- Prevent invalid combinations from being recorded at the database layer.
CREATE OR REPLACE FUNCTION validate_combination_size()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    expected_size INTEGER;
    actual_size INTEGER;
BEGIN
    SELECT combination_size
    INTO expected_size
    FROM combination_problems
    WHERE problem_id = NEW.problem_id;

    SELECT COUNT(*)
    INTO actual_size
    FROM combination_members
    WHERE combination_id = NEW.combination_id;

    IF expected_size IS NOT NULL
       AND actual_size > expected_size THEN
        RAISE EXCEPTION
            'combination % exceeds required size %',
            NEW.combination_id,
            expected_size;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_combination_size
AFTER INSERT ON combination_members
FOR EACH ROW
EXECUTE FUNCTION validate_combination_size();

-- Demonstrate transactional creation of a valid generated combination.
BEGIN;

INSERT INTO generated_combinations (
    problem_id,
    combination_key,
    total_sum,
    combination_size
)
SELECT
    p.problem_id,
    '2+3+7',
    12,
    3
FROM combination_problems AS p
WHERE p.problem_name = 'fixed-size review set'
RETURNING combination_id;

-- The returned ID from the previous statement is intentionally obtained
-- again through the natural key to keep the transaction self-contained.
INSERT INTO combination_members (
    combination_id,
    position,
    candidate_id
)
SELECT
    gc.combination_id,
    members.position,
    cv.candidate_id
FROM generated_combinations AS gc
CROSS JOIN LATERAL (
    VALUES
        (1, 'two'),
        (2, 'three'),
        (3, 'seven')
) AS members(position, label)
JOIN candidate_values AS cv
    ON cv.label = members.label
WHERE gc.combination_key = '2+3+7'
  AND gc.problem_id = (
      SELECT problem_id
      FROM combination_problems
      WHERE problem_name = 'fixed-size review set'
  );

COMMIT;

-- Basic retrieval.
SELECT
    p.problem_name,
    gc.combination_key,
    gc.total_sum,
    gc.combination_size
FROM combination_problems AS p
JOIN generated_combinations AS gc
    ON gc.problem_id = p.problem_id
ORDER BY p.problem_name, gc.combination_key;

-- Evaluate whether stored combinations satisfy their problem.
SELECT
    p.problem_name,
    gc.combination_key,
    gc.total_sum,
    gc.total_sum = p.target_sum AS reaches_target,
    (
        p.minimum_sum IS NULL
        OR gc.total_sum >= p.minimum_sum
    ) AS satisfies_minimum,
    (
        p.maximum_sum IS NULL
        OR gc.total_sum <= p.maximum_sum
    ) AS satisfies_maximum
FROM combination_problems AS p
JOIN generated_combinations AS gc
    ON gc.problem_id = p.problem_id;

-- Aggregate members into a deterministic representation.
SELECT
    gc.combination_id,
    p.problem_name,
    string_agg(
        cv.label,
        ' + '
        ORDER BY cm.position
    ) AS members,
    SUM(cv.value) AS calculated_sum
FROM generated_combinations AS gc
JOIN combination_problems AS p
    ON p.problem_id = gc.problem_id
JOIN combination_members AS cm
    ON cm.combination_id = gc.combination_id
JOIN candidate_values AS cv
    ON cv.candidate_id = cm.candidate_id
GROUP BY
    gc.combination_id,
    p.problem_name
ORDER BY gc.combination_id;

-- Recursive CTE: generate combinations from candidate values without reuse.
WITH RECURSIVE combination_search AS (
    SELECT
        ARRAY[cv.candidate_id]::BIGINT[] AS ids,
        cv.value AS total_sum,
        1 AS depth,
        cv.candidate_id AS last_candidate
    FROM candidate_values AS cv
    WHERE cv.active

    UNION ALL

    SELECT
        cs.ids || cv.candidate_id,
        cs.total_sum + cv.value,
        cs.depth + 1,
        cv.candidate_id
    FROM combination_search AS cs
    JOIN candidate_values AS cv
        ON cv.candidate_id > cs.last_candidate
    WHERE cs.total_sum + cv.value <= 18
      AND cs.depth < 3
)
SELECT
    ids,
    total_sum,
    depth
FROM combination_search
WHERE depth = 3
  AND total_sum BETWEEN 12 AND 18
ORDER BY total_sum, ids;

-- Validation report identifying problems with no suitable stored result.
SELECT
    p.problem_name,
    p.target_sum,
    COUNT(gc.combination_id) AS stored_results,
    CASE
        WHEN COUNT(gc.combination_id) = 0 THEN 'NO_RESULT'
        ELSE 'RESULT_AVAILABLE'
    END AS evaluation
FROM combination_problems AS p
LEFT JOIN generated_combinations AS gc
    ON gc.problem_id = p.problem_id
GROUP BY
    p.problem_id,
    p.problem_name,
    p.target_sum
ORDER BY p.problem_id;

-- Workflow state example.
INSERT INTO evaluation_runs (
    problem_id,
    status,
    started_at,
    completed_at
)
SELECT
    problem_id,
    'COMPLETED',
    clock_timestamp(),
    clock_timestamp()
FROM combination_problems
WHERE problem_name = 'fixed-size review set';

-- Report completed evaluations.
SELECT
    p.problem_name,
    er.status,
    er.started_at,
    er.completed_at
FROM evaluation_runs AS er
JOIN combination_problems AS p
    ON p.problem_id = er.problem_id
ORDER BY er.run_id;

-- A failed evaluation is represented explicitly rather than being
-- confused with a mathematically valid empty result.
INSERT INTO evaluation_runs (
    problem_id,
    status,
    started_at,
    completed_at,
    failure_reason
)
SELECT
    problem_id,
    'FAILED',
    clock_timestamp(),
    clock_timestamp(),
    'Requested minimum exceeds maximum'
FROM combination_problems
WHERE problem_name = 'impossible constraint';

SELECT
    p.problem_name,
    er.status,
    er.failure_reason
FROM evaluation_runs AS er
JOIN combination_problems AS p
    ON p.problem_id = er.problem_id
ORDER BY er.run_id;
