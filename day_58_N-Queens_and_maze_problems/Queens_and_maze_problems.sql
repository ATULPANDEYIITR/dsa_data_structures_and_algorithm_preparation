DROP SCHEMA IF EXISTS puzzle_lab CASCADE;
CREATE SCHEMA puzzle_lab;

SET search_path = puzzle_lab, public;

CREATE TYPE puzzle_type AS ENUM ('N_QUEENS', 'MAZE');
CREATE TYPE cell_type AS ENUM ('OPEN', 'BLOCKED');
CREATE TYPE search_status AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED');

CREATE TABLE puzzles (
    puzzle_id BIGSERIAL PRIMARY KEY,
    puzzle_type puzzle_type NOT NULL,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(name)) >= 3)
);

CREATE TABLE n_queens_boards (
    board_id BIGSERIAL PRIMARY KEY,
    puzzle_id BIGINT NOT NULL REFERENCES puzzles(puzzle_id) ON DELETE CASCADE,
    board_size INTEGER NOT NULL,
    solution_count INTEGER,
    CHECK (board_size BETWEEN 1 AND 14),
    CHECK (solution_count IS NULL OR solution_count >= 0),
    UNIQUE (puzzle_id, board_size)
);

CREATE TABLE mazes (
    maze_id BIGSERIAL PRIMARY KEY,
    puzzle_id BIGINT NOT NULL REFERENCES puzzles(puzzle_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    rows_count INTEGER NOT NULL,
    cols_count INTEGER NOT NULL,
    CHECK (rows_count > 0),
    CHECK (cols_count > 0)
);

CREATE TABLE maze_cells (
    maze_id BIGINT NOT NULL REFERENCES mazes(maze_id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    col_index INTEGER NOT NULL,
    cell cell_type NOT NULL,
    PRIMARY KEY (maze_id, row_index, col_index),
    CHECK (row_index >= 0),
    CHECK (col_index >= 0)
);

CREATE TABLE positions (
    position_id BIGSERIAL PRIMARY KEY,
    maze_id BIGINT NOT NULL REFERENCES mazes(maze_id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    col_index INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('START', 'TARGET')),
    UNIQUE (maze_id, role),
    UNIQUE (maze_id, row_index, col_index)
);

CREATE TABLE n_queens_solutions (
    solution_id BIGSERIAL PRIMARY KEY,
    board_id BIGINT NOT NULL REFERENCES n_queens_boards(board_id) ON DELETE CASCADE,
    solution_number INTEGER NOT NULL,
    placement INTEGER[] NOT NULL,
    UNIQUE (board_id, solution_number),
    CHECK (solution_number > 0),
    CHECK (cardinality(placement) = (
        SELECT board_size
        FROM n_queens_boards b
        WHERE b.board_id = board_id
    ))
);

CREATE TABLE search_runs (
    run_id BIGSERIAL PRIMARY KEY,
    puzzle_id BIGINT NOT NULL REFERENCES puzzles(puzzle_id) ON DELETE CASCADE,
    status search_status NOT NULL DEFAULT 'PENDING',
    paths_found INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error_message TEXT,
    CHECK (paths_found >= 0),
    CHECK (
        (status = 'PENDING' AND started_at IS NULL)
        OR
        (status <> 'PENDING' AND started_at IS NOT NULL)
    )
);

CREATE TABLE maze_paths (
    path_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES search_runs(run_id) ON DELETE CASCADE,
    path_number INTEGER NOT NULL,
    path_cells JSONB NOT NULL,
    path_length INTEGER NOT NULL,
    is_shortest BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (run_id, path_number),
    CHECK (path_number > 0),
    CHECK (path_length > 0),
    CHECK (jsonb_typeof(path_cells) = 'array')
);

CREATE INDEX idx_maze_cells_open
    ON maze_cells (maze_id, row_index, col_index)
    WHERE cell = 'OPEN';

CREATE INDEX idx_search_runs_puzzle_status
    ON search_runs (puzzle_id, status);

CREATE INDEX idx_maze_paths_shortest
    ON maze_paths (run_id, path_length)
    WHERE is_shortest;

CREATE OR REPLACE FUNCTION validate_n_queens_placement(
    p_placement INTEGER[],
    p_n INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    r INTEGER;
    c INTEGER;
    i INTEGER;
    j INTEGER;
BEGIN
    IF p_n < 1 OR cardinality(p_placement) <> p_n THEN
        RETURN FALSE;
    END IF;

    FOR i IN 1..p_n LOOP
        c := p_placement[i];

        IF c < 0 OR c >= p_n THEN
            RETURN FALSE;
        END IF;

        FOR j IN 1..i - 1 LOOP
            IF p_placement[j] = c THEN
                RETURN FALSE;
            END IF;

            IF abs((j - 1) - p_placement[j])
               = abs((i - 1) - c) THEN
                RETURN FALSE;
            END IF;
        END LOOP;
    END LOOP;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION validate_queen_solution_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    board_size INTEGER;
BEGIN
    SELECT board_size
    INTO board_size
    FROM n_queens_boards
    WHERE board_id = NEW.board_id;

    IF board_size IS NULL THEN
        RAISE EXCEPTION 'Board % does not exist', NEW.board_id;
    END IF;

    IF NOT validate_n_queens_placement(
        NEW.placement,
        board_size
    ) THEN
        RAISE EXCEPTION
            'Invalid N-Queens placement for board %',
            NEW.board_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_queen_solution
BEFORE INSERT OR UPDATE ON n_queens_solutions
FOR EACH ROW
EXECUTE FUNCTION validate_queen_solution_trigger();

CREATE OR REPLACE FUNCTION validate_maze_position_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    maze_rows INTEGER;
    maze_cols INTEGER;
    current_cell cell_type;
BEGIN
    SELECT rows_count, cols_count
    INTO maze_rows, maze_cols
    FROM mazes
    WHERE maze_id = NEW.maze_id;

    IF maze_rows IS NULL THEN
        RAISE EXCEPTION 'Maze % does not exist', NEW.maze_id;
    END IF;

    IF NEW.row_index < 0 OR NEW.row_index >= maze_rows
       OR NEW.col_index < 0 OR NEW.col_index >= maze_cols THEN
        RAISE EXCEPTION
            'Position (%) is outside maze %',
            format('%s,%s', NEW.row_index, NEW.col_index),
            NEW.maze_id;
    END IF;

    SELECT cell
    INTO current_cell
    FROM maze_cells
    WHERE maze_id = NEW.maze_id
      AND row_index = NEW.row_index
      AND col_index = NEW.col_index;

    IF current_cell IS DISTINCT FROM 'OPEN' THEN
        RAISE EXCEPTION
            'Start or target must reference an open maze cell';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_maze_position
BEFORE INSERT OR UPDATE ON positions
FOR EACH ROW
EXECUTE FUNCTION validate_maze_position_trigger();

CREATE OR REPLACE FUNCTION calculate_n_queens_status(
    p_board_id BIGINT
)
RETURNS TABLE (
    board_size INTEGER,
    stored_solutions BIGINT,
    valid_solutions BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        b.board_size,
        COUNT(s.solution_id) AS stored_solutions,
        COUNT(s.solution_id) FILTER (
            WHERE validate_n_queens_placement(
                s.placement,
                b.board_size
            )
        ) AS valid_solutions
    FROM n_queens_boards b
    LEFT JOIN n_queens_solutions s
        ON s.board_id = b.board_id
    WHERE b.board_id = p_board_id
    GROUP BY b.board_id, b.board_size;
$$;

CREATE OR REPLACE VIEW v_maze_open_cells AS
SELECT
    m.maze_id,
    m.name,
    c.row_index,
    c.col_index
FROM mazes m
JOIN maze_cells c
    ON c.maze_id = m.maze_id
WHERE c.cell = 'OPEN';

CREATE OR REPLACE VIEW v_merge_style_search_report AS
SELECT
    sr.run_id,
    p.name AS puzzle_name,
    sr.status,
    sr.paths_found,
    sr.started_at,
    sr.finished_at,
    CASE
        WHEN sr.status = 'COMPLETED'
             AND sr.paths_found > 0 THEN 'REACHABLE'
        WHEN sr.status = 'COMPLETED' THEN 'NO_PATH'
        WHEN sr.status = 'FAILED' THEN 'FAILED'
        ELSE 'IN_PROGRESS'
    END AS outcome
FROM search_runs sr
JOIN puzzles p
    ON p.puzzle_id = sr.puzzle_id;

BEGIN;

INSERT INTO puzzles (puzzle_type, name)
VALUES
    ('N_QUEENS', 'Four Queens'),
    ('N_QUEENS', 'Eight Queens'),
    ('MAZE', 'Pruned Grid Maze');

INSERT INTO n_queens_boards (puzzle_id, board_size)
SELECT puzzle_id, 4
FROM puzzles
WHERE name = 'Four Queens';

INSERT INTO n_queens_boards (puzzle_id, board_size)
SELECT puzzle_id, 8
FROM puzzles
WHERE name = 'Eight Queens';

INSERT INTO n_queens_solutions (
    board_id,
    solution_number,
    placement
)
SELECT
    board_id,
    1,
    ARRAY[1, 3, 0, 2]
FROM n_queens_boards
WHERE board_size = 4
  AND board_id = (
      SELECT board_id
      FROM n_queens_boards
      WHERE board_size = 4
      ORDER BY board_id
      LIMIT 1
  );

INSERT INTO n_queens_solutions (
    board_id,
    solution_number,
    placement
)
SELECT
    board_id,
    2,
    ARRAY[2, 0, 3, 1]
FROM n_queens_boards
WHERE board_size = 4
  AND board_id = (
      SELECT board_id
      FROM n_queens_boards
      WHERE board_size = 4
      ORDER BY board_id
      LIMIT 1
  );

INSERT INTO mazes (
    puzzle_id,
    name,
    rows_count,
    cols_count
)
SELECT
    puzzle_id,
    'Pruned Grid Maze',
    5,
    5
FROM puzzles
WHERE name = 'Pruned Grid Maze';

INSERT INTO maze_cells (maze_id, row_index, col_index, cell)
SELECT
    m.maze_id,
    r,
    c,
    CASE
        WHEN substring(v.grid, c + 1, 1) = '#'
            THEN 'BLOCKED'::cell_type
        ELSE 'OPEN'::cell_type
    END
FROM mazes m
CROSS JOIN (
    VALUES
        (0, '...#.'),
        (1, '.#...'),
        (2, '...#.'),
        (3, '#....'),
        (4, '.....')
) AS v(r, grid)
CROSS JOIN LATERAL generate_series(0, 4) AS c(c)
WHERE m.name = 'Pruned Grid Maze';

INSERT INTO positions (
    maze_id,
    row_index,
    col_index,
    role
)
SELECT maze_id, 0, 0, 'START'
FROM mazes
WHERE name = 'Pruned Grid Maze';

INSERT INTO positions (
    maze_id,
    row_index,
    col_index,
    role
)
SELECT maze_id, 4, 4, 'TARGET'
FROM mazes
WHERE name = 'Pruned Grid Maze';

INSERT INTO search_runs (
    puzzle_id,
    status,
    paths_found,
    started_at,
    finished_at
)
SELECT
    puzzle_id,
    'COMPLETED',
    3,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM puzzles
WHERE name = 'Pruned Grid Maze';

INSERT INTO maze_paths (
    run_id,
    path_number,
    path_cells,
    path_length,
    is_shortest
)
SELECT
    sr.run_id,
    v.path_number,
    v.path_cells::jsonb,
    v.path_length,
    v.is_shortest
FROM search_runs sr
CROSS JOIN (
    VALUES
    (
        1,
        '[[0,0],[1,0],[2,0],[2,1],[2,2],[1,2],[0,2],[0,1],[0,0]]',
        9,
        FALSE
    ),
    (
        2,
        '[[0,0],[1,0],[2,0],[2,1],[2,2],[2,3],[1,3],[0,3]]',
        8,
        TRUE
    ),
    (
        3,
        '[[0,0],[1,0],[2,0],[2,1],[2,2],[3,2],[3,3],[4,3],[4,4]]',
        9,
        FALSE
    )
) AS v(path_number, path_cells, path_length, is_shortest)
WHERE sr.puzzle_id = (
    SELECT puzzle_id
    FROM puzzles
    WHERE name = 'Pruned Grid Maze'
)
AND sr.run_id = (
    SELECT MAX(run_id)
    FROM search_runs
    WHERE puzzle_id = sr.puzzle_id
);

COMMIT;

-- Retrieval: show every open cell in the maze.
SELECT *
FROM v_maze_open_cells
ORDER BY maze_id, row_index, col_index;

-- Validation: confirm that stored N-Queens placements satisfy
-- column and diagonal constraints.
SELECT *
FROM calculate_n_queens_status(
    (
        SELECT board_id
        FROM n_queens_boards
        WHERE board_size = 4
        ORDER BY board_id
        LIMIT 1
    )
);

-- Aggregation: count paths and identify shortest paths.
SELECT
    run_id,
    COUNT(*) AS stored_paths,
    MIN(path_length) AS minimum_path_length,
    COUNT(*) FILTER (WHERE is_shortest) AS marked_shortest_paths
FROM maze_paths
GROUP BY run_id
ORDER BY run_id;

-- Evaluation: determine whether every stored path is structurally valid
-- as a JSON array of coordinate pairs.
SELECT
    path_id,
    path_number,
    path_length,
    jsonb_typeof(path_cells) = 'array' AS valid_path_container,
    jsonb_array_length(path_cells) = path_length AS length_matches
FROM maze_paths
ORDER BY path_id;

-- Workflow-state report.
SELECT *
FROM v_merge_style_search_report
ORDER BY run_id;

-- Failure-case query: locate blocked cells and verify that positions
-- cannot be assigned to them by the database trigger.
SELECT
    maze_id,
    row_index,
    col_index
FROM maze_cells
WHERE cell = 'BLOCKED'
ORDER BY maze_id, row_index, col_index;

-- Relational reconstruction of a maze's board representation.
SELECT
    m.name,
    string_agg(
        CASE WHEN c.cell = 'OPEN' THEN '.' ELSE '#' END,
        '' ORDER BY c.col_index
    ) AS row_text
FROM mazes m
JOIN maze_cells c
    ON c.maze_id = m.maze_id
GROUP BY m.maze_id, m.name, c.row_index
ORDER BY m.maze_id, c.row_index;

-- Transactional failure demonstration is intentionally isolated in a
-- savepoint so the invalid write cannot corrupt valid puzzle data.
BEGIN;

SAVEPOINT invalid_queen_test;

DO $$
DECLARE
    target_board BIGINT;
BEGIN
    SELECT board_id
    INTO target_board
    FROM n_queens_boards
    WHERE board_size = 4
    ORDER BY board_id
    LIMIT 1;

    BEGIN
        INSERT INTO n_queens_solutions (
            board_id,
            solution_number,
            placement
        )
        VALUES (
            target_board,
            999,
            ARRAY[0, 1, 2, 3]
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Rejected invalid queen placement: %', SQLERRM;
    END;
END;
$$;

ROLLBACK TO SAVEPOINT invalid_queen_test;
COMMIT;
