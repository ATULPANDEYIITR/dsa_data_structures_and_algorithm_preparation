DROP SCHEMA IF EXISTS sudoku_assessment CASCADE;
CREATE SCHEMA sudoku_assessment;

SET search_path TO sudoku_assessment;

CREATE TABLE puzzles (
    puzzle_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE,
    difficulty text NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    status text NOT NULL CHECK (status IN ('pending', 'solved', 'unsolvable')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE puzzle_cells (
    puzzle_id bigint NOT NULL REFERENCES puzzles(puzzle_id) ON DELETE CASCADE,
    row_number smallint NOT NULL CHECK (row_number BETWEEN 1 AND 9),
    column_number smallint NOT NULL CHECK (column_number BETWEEN 1 AND 9),
    given_value smallint CHECK (given_value BETWEEN 1 AND 9),
    solved_value smallint CHECK (solved_value BETWEEN 1 AND 9),
    PRIMARY KEY (puzzle_id, row_number, column_number),
    CHECK (
        given_value IS NULL
        OR solved_value IS NULL
        OR given_value = solved_value
    )
);

CREATE TABLE solving_runs (
    run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    puzzle_id bigint NOT NULL REFERENCES puzzles(puzzle_id) ON DELETE CASCADE,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    decisions integer NOT NULL DEFAULT 0 CHECK (decisions >= 0),
    backtracks integer NOT NULL DEFAULT 0 CHECK (backtracks >= 0),
    result text CHECK (result IN ('solved', 'unsolvable', 'failed')),
    CHECK (finished_at IS NULL OR finished_at >= started_at)
);

CREATE TABLE backtracking_steps (
    step_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id bigint NOT NULL REFERENCES solving_runs(run_id) ON DELETE CASCADE,
    depth integer NOT NULL CHECK (depth >= 0),
    row_number smallint NOT NULL CHECK (row_number BETWEEN 1 AND 9),
    column_number smallint NOT NULL CHECK (column_number BETWEEN 1 AND 9),
    candidate smallint NOT NULL CHECK (candidate BETWEEN 1 AND 9),
    action text NOT NULL CHECK (action IN ('choice', 'reject', 'undo')),
    constraint_valid boolean NOT NULL
);

CREATE INDEX idx_puzzle_cells_puzzle
    ON puzzle_cells (puzzle_id, row_number, column_number);

CREATE INDEX idx_solving_runs_puzzle_result
    ON solving_runs (puzzle_id, result);

CREATE INDEX idx_backtracking_steps_run_depth
    ON backtracking_steps (run_id, depth);

CREATE OR REPLACE FUNCTION validate_sudoku_givens()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    conflicts integer;
BEGIN
    SELECT count(*)
    INTO conflicts
    FROM (
        SELECT row_number, given_value
        FROM puzzle_cells
        WHERE puzzle_id = NEW.puzzle_id
          AND given_value IS NOT NULL
        GROUP BY row_number, given_value
        HAVING count(*) > 1

        UNION ALL

        SELECT column_number, given_value
        FROM puzzle_cells
        WHERE puzzle_id = NEW.puzzle_id
          AND given_value IS NOT NULL
        GROUP BY column_number, given_value
        HAVING count(*) > 1
    ) conflict_rows;

    IF conflicts > 0 THEN
        RAISE EXCEPTION
            'Sudoku givens contain a row or column conflict for puzzle %',
            NEW.puzzle_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER trg_validate_sudoku_givens
AFTER INSERT OR UPDATE ON puzzle_cells
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION validate_sudoku_givens();

CREATE OR REPLACE FUNCTION complete_run(
    p_run_id bigint,
    p_result text,
    p_decisions integer,
    p_backtracks integer
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_result NOT IN ('solved', 'unsolvable', 'failed') THEN
        RAISE EXCEPTION 'Invalid solving result: %', p_result;
    END IF;

    IF p_decisions < 0 OR p_backtracks < 0 THEN
        RAISE EXCEPTION 'Search counters cannot be negative';
    END IF;

    UPDATE solving_runs
    SET finished_at = now(),
        result = p_result,
        decisions = p_decisions,
        backtracks = p_backtracks
    WHERE run_id = p_run_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Solving run % does not exist', p_run_id;
    END IF;
END;
$$;

CREATE VIEW puzzle_completion AS
SELECT
    p.puzzle_id,
    p.name,
    p.difficulty,
    p.status,
    count(pc.*) AS cells,
    count(pc.given_value) AS givens,
    count(pc.solved_value) AS solved_cells,
    count(*) FILTER (
        WHERE pc.solved_value IS NULL
    ) AS unresolved_cells
FROM puzzles p
LEFT JOIN puzzle_cells pc
    ON pc.puzzle_id = p.puzzle_id
GROUP BY p.puzzle_id, p.name, p.difficulty, p.status;

CREATE VIEW run_performance AS
SELECT
    p.name,
    sr.run_id,
    sr.result,
    sr.decisions,
    sr.backtracks,
    EXTRACT(EPOCH FROM (sr.finished_at - sr.started_at)) * 1000
        AS elapsed_ms,
    CASE
        WHEN sr.decisions = 0 THEN 0
        ELSE round(sr.backtracks::numeric / sr.decisions, 4)
    END AS backtrack_ratio
FROM solving_runs sr
JOIN puzzles p ON p.puzzle_id = sr.puzzle_id
WHERE sr.finished_at IS NOT NULL;

INSERT INTO puzzles (name, difficulty, status)
VALUES
    ('Classic Assessment', 'easy', 'pending'),
    ('Conflict Example', 'medium', 'unsolvable');

INSERT INTO puzzle_cells (
    puzzle_id, row_number, column_number, given_value
)
SELECT
    1,
    r.row_number,
    c.column_number,
    CASE
        WHEN r.row_number = 1 AND c.column_number = 1 THEN 5
        WHEN r.row_number = 1 AND c.column_number = 2 THEN 3
        WHEN r.row_number = 1 AND c.column_number = 5 THEN 7
        WHEN r.row_number = 2 AND c.column_number = 1 THEN 6
        WHEN r.row_number = 2 AND c.column_number = 4 THEN 1
        WHEN r.row_number = 2 AND c.column_number = 5 THEN 9
        WHEN r.row_number = 2 AND c.column_number = 6 THEN 5
        WHEN r.row_number = 3 AND c.column_number = 2 THEN 9
        WHEN r.row_number = 3 AND c.column_number = 3 THEN 8
        WHEN r.row_number = 3 AND c.column_number = 8 THEN 6
        WHEN r.row_number = 4 AND c.column_number = 1 THEN 8
        WHEN r.row_number = 4 AND c.column_number = 5 THEN 6
        WHEN r.row_number = 4 AND c.column_number = 9 THEN 3
        WHEN r.row_number = 5 AND c.column_number = 1 THEN 4
        WHEN r.row_number = 5 AND c.column_number = 4 THEN 8
        WHEN r.row_number = 5 AND c.column_number = 6 THEN 3
        WHEN r.row_number = 5 AND c.column_number = 9 THEN 1
        WHEN r.row_number = 6 AND c.column_number = 1 THEN 7
        WHEN r.row_number = 6 AND c.column_number = 5 THEN 2
        WHEN r.row_number = 6 AND c.column_number = 9 THEN 6
        WHEN r.row_number = 7 AND c.column_number = 2 THEN 6
        WHEN r.row_number = 7 AND c.column_number = 7 THEN 2
        WHEN r.row_number = 7 AND c.column_number = 8 THEN 8
        WHEN r.row_number = 8 AND c.column_number = 4 THEN 4
        WHEN r.row_number = 8 AND c.column_number = 5 THEN 1
        WHEN r.row_number = 8 AND c.column_number = 6 THEN 9
        WHEN r.row_number = 8 AND c.column_number = 9 THEN 5
        WHEN r.row_number = 9 AND c.column_number = 5 THEN 8
        WHEN r.row_number = 9 AND c.column_number = 8 THEN 7
        WHEN r.row_number = 9 AND c.column_number = 9 THEN 9
        ELSE NULL
    END
FROM generate_series(1, 9) AS r(row_number)
CROSS JOIN generate_series(1, 9) AS c(column_number);

INSERT INTO puzzle_cells (puzzle_id, row_number, column_number, given_value)
VALUES (2, 1, 1, 5), (2, 1, 2, 5);

BEGIN;

INSERT INTO solving_runs (
    puzzle_id,
    decisions,
    backtracks,
    result
)
VALUES (1, 0, 0, 'solved');

UPDATE puzzle_cells
SET solved_value = given_value
WHERE puzzle_id = 1
  AND given_value IS NOT NULL;

UPDATE puzzles
SET status = 'solved'
WHERE puzzle_id = 1;

COMMIT;

INSERT INTO backtracking_steps (
    run_id,
    depth,
    row_number,
    column_number,
    candidate,
    action,
    constraint_valid
)
SELECT
    currval('solving_runs_run_id_seq'),
    0,
    1,
    3,
    4,
    'choice',
    true
WHERE EXISTS (
    SELECT 1 FROM solving_runs
    WHERE run_id = currval('solving_runs_run_id_seq')
);

INSERT INTO solving_runs (
    puzzle_id,
    decisions,
    backtracks,
    result,
    finished_at
)
VALUES (
    2,
    1,
    1,
    'unsolvable',
    now()
);

-- Retrieval and state reporting.
SELECT *
FROM puzzle_completion
ORDER BY puzzle_id;

-- Search-performance reporting.
SELECT *
FROM run_performance
ORDER BY run_id;

-- Unresolved cells are useful for identifying incomplete solving workflows.
SELECT
    p.name,
    pc.row_number,
    pc.column_number,
    pc.given_value,
    pc.solved_value
FROM puzzle_cells pc
JOIN puzzles p ON p.puzzle_id = pc.puzzle_id
WHERE pc.solved_value IS NULL
ORDER BY p.puzzle_id, pc.row_number, pc.column_number;

-- Backtracking action distribution.
SELECT
    sr.run_id,
    bs.action,
    count(*) AS action_count
FROM backtracking_steps bs
JOIN solving_runs sr ON sr.run_id = bs.run_id
GROUP BY sr.run_id, bs.action
ORDER BY sr.run_id, bs.action;

-- Eligibility-style evaluation: a completed Sudoku has no unresolved cells.
WITH puzzle_state AS (
    SELECT
        puzzle_id,
        count(*) AS cells,
        count(solved_value) AS solved
    FROM puzzle_cells
    GROUP BY puzzle_id
)
SELECT
    p.name,
    p.status,
    ps.cells,
    ps.solved,
    (ps.cells = 81 AND ps.solved = 81 AND p.status = 'solved')
        AS completion_eligible
FROM puzzles p
JOIN puzzle_state ps USING (puzzle_id)
ORDER BY p.puzzle_id;
