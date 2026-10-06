DROP SCHEMA IF EXISTS linked_list_reversal CASCADE;
CREATE SCHEMA linked_list_reversal;

SET search_path TO linked_list_reversal;

-- A linked list has an ordered sequence of nodes. The position is stored
-- explicitly because SQL tables do not inherently preserve row order.
CREATE TABLE linked_lists (
    list_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    list_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE list_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    list_id BIGINT NOT NULL REFERENCES linked_lists(list_id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    value INTEGER NOT NULL,
    CONSTRAINT uq_list_position UNIQUE (list_id, position),
    CONSTRAINT ck_positive_position CHECK (position > 0)
);

CREATE INDEX idx_list_nodes_list_position
    ON list_nodes (list_id, position);

CREATE TABLE reversal_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    list_id BIGINT NOT NULL REFERENCES linked_lists(list_id) ON DELETE CASCADE,
    algorithm TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'started',
    CONSTRAINT ck_algorithm
        CHECK (algorithm IN ('iterative', 'recursive')),
    CONSTRAINT ck_run_status
        CHECK (status IN ('started', 'completed', 'failed'))
);

CREATE TABLE reversal_snapshots (
    run_id BIGINT NOT NULL REFERENCES reversal_runs(run_id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    value INTEGER NOT NULL,
    PRIMARY KEY (run_id, sequence_number),
    CONSTRAINT ck_snapshot_sequence CHECK (sequence_number > 0)
);

INSERT INTO linked_lists (list_name)
VALUES
    ('customer-processing-order'),
    ('empty-list'),
    ('single-node-list');

INSERT INTO list_nodes (list_id, position, value)
SELECT list_id, position, value
FROM linked_lists
JOIN (
    VALUES
        ('customer-processing-order', 1, 101),
        ('customer-processing-order', 2, 205),
        ('customer-processing-order', 3, 309),
        ('customer-processing-order', 4, 412),
        ('customer-processing-order', 5, 518),
        ('single-node-list', 1, 42)
) AS seed(list_name, position, value)
    USING (list_name);

-- The relational representation exposes the current logical order.
SELECT
    l.list_name,
    n.position,
    n.value
FROM linked_lists AS l
LEFT JOIN list_nodes AS n
    ON n.list_id = l.list_id
ORDER BY l.list_name, n.position;

-- Demonstrate the logical result of iterative reversal without changing
-- physical row ownership. The descending position produces the reversed
-- sequence because position represents the linked-list ordering.
SELECT
    l.list_name,
    n.position,
    n.value
FROM linked_lists AS l
JOIN list_nodes AS n
    ON n.list_id = l.list_id
WHERE l.list_name = 'customer-processing-order'
ORDER BY n.position DESC;

-- Recursive reversal is naturally expressed as a recursive CTE when the
-- database is being asked to traverse a predecessor/successor relationship.
-- This CTE demonstrates reverse ordering of the stored sequence.
WITH RECURSIVE reversed_positions AS (
    SELECT
        n.list_id,
        n.position,
        n.value,
        1 AS reverse_position
    FROM list_nodes AS n
    JOIN linked_lists AS l
        ON l.list_id = n.list_id
    WHERE l.list_name = 'customer-processing-order'
      AND n.position = (
          SELECT MAX(position)
          FROM list_nodes
          WHERE list_id = n.list_id
      )

    UNION ALL

    SELECT
        n.list_id,
        n.position,
        n.value,
        rp.reverse_position + 1
    FROM reversed_positions AS rp
    JOIN list_nodes AS n
        ON n.list_id = rp.list_id
       AND n.position = rp.position - 1
)
SELECT
    reverse_position,
    value
FROM reversed_positions
ORDER BY reverse_position;

-- Capture an iterative reversal as a database-level operation. The
-- transaction ensures that either every position is rewritten or no position
-- is changed.
BEGIN;

INSERT INTO reversal_runs (list_id, algorithm)
SELECT list_id, 'iterative'
FROM linked_lists
WHERE list_name = 'customer-processing-order'
RETURNING run_id;

-- PostgreSQL's transaction snapshot makes the following update atomic with
-- respect to this transaction. The new position is calculated from the old
-- maximum position.
WITH bounds AS (
    SELECT
        list_id,
        MAX(position) AS max_position
    FROM list_nodes
    WHERE list_id = (
        SELECT list_id
        FROM linked_lists
        WHERE list_name = 'customer-processing-order'
    )
    GROUP BY list_id
),
reordered AS (
    SELECT
        n.node_id,
        b.max_position - n.position + 1 AS new_position
    FROM list_nodes AS n
    JOIN bounds AS b
        ON b.list_id = n.list_id
)
UPDATE list_nodes AS n
SET position = r.new_position
FROM reordered AS r
WHERE n.node_id = r.node_id;

COMMIT;

UPDATE reversal_runs
SET status = 'completed'
WHERE algorithm = 'iterative'
  AND status = 'started'
  AND list_id = (
      SELECT list_id
      FROM linked_lists
      WHERE list_name = 'customer-processing-order'
  );

SELECT
    l.list_name,
    n.position,
    n.value
FROM linked_lists AS l
JOIN list_nodes AS n
    ON n.list_id = l.list_id
WHERE l.list_name = 'customer-processing-order'
ORDER BY n.position;

-- Database constraints prevent two nodes from occupying the same logical
-- position in one list.
DO $$
BEGIN
    BEGIN
        INSERT INTO list_nodes (list_id, position, value)
        SELECT list_id, 1, 999
        FROM linked_lists
        WHERE list_name = 'single-node-list';

        RAISE EXCEPTION 'Expected unique-position constraint was not enforced';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Duplicate list position correctly rejected.';
    END;
END
$$;

-- The empty list has no rows in list_nodes. A reversal is therefore a
-- no-op rather than a special row-level operation.
SELECT
    l.list_name,
    COUNT(n.node_id) AS node_count
FROM linked_lists AS l
LEFT JOIN list_nodes AS n
    ON n.list_id = l.list_id
GROUP BY l.list_id, l.list_name
ORDER BY l.list_name;

-- Reversing twice restores the logical ordering. This query provides the
-- ordering expression needed to compare a list against its original sequence.
SELECT
    l.list_name,
    STRING_AGG(n.value::TEXT, ' -> ' ORDER BY n.position) AS current_order
FROM linked_lists AS l
JOIN list_nodes AS n
    ON n.list_id = l.list_id
WHERE l.list_name = 'customer-processing-order'
GROUP BY l.list_name;

-- The relational model represents links indirectly through ordered
-- positions. An in-memory linked list can redirect pointers directly;
-- PostgreSQL instead enforces ordering with keys, constraints, and
-- transactional updates.
