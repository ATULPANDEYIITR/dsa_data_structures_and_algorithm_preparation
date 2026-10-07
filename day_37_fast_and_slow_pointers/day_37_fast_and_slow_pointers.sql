DROP SCHEMA IF EXISTS fast_slow_pointer_demo CASCADE;
CREATE SCHEMA fast_slow_pointer_demo;
SET search_path TO fast_slow_pointer_demo;

-- The relational model records linked-list nodes explicitly. The next_node_id
-- foreign key represents the pointer from one node to another node.
CREATE TABLE pointer_chain (
    chain_id BIGSERIAL PRIMARY KEY,
    chain_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE chain_node (
    node_id BIGSERIAL PRIMARY KEY,
    chain_id BIGINT NOT NULL
        REFERENCES pointer_chain(chain_id)
        ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL,
    payload TEXT NOT NULL,
    next_node_id BIGINT NULL,
    CONSTRAINT uq_chain_sequence
        UNIQUE (chain_id, sequence_no),
    CONSTRAINT uq_chain_node
        UNIQUE (chain_id, node_id),
    CONSTRAINT ck_positive_sequence
        CHECK (sequence_no > 0)
);

-- This index supports traversal-oriented lookups from a chain to its nodes.
CREATE INDEX idx_chain_node_chain_sequence
    ON chain_node (chain_id, sequence_no);

-- This index supports reverse pointer lookups when inspecting which nodes
-- point to a particular node.
CREATE INDEX idx_chain_node_next
    ON chain_node (next_node_id);

ALTER TABLE chain_node
    ADD CONSTRAINT fk_next_node_same_chain
    FOREIGN KEY (chain_id, next_node_id)
    REFERENCES chain_node (chain_id, node_id)
    DEFERRABLE INITIALLY DEFERRED;

-- A node with NULL next_node_id is a terminal node. A non-NULL value points
-- to another node in the same chain. PostgreSQL's deferred foreign key lets
-- a transaction construct a complete cyclic structure before validation.
INSERT INTO pointer_chain (chain_name, description)
VALUES
    (
        'healthy_pipeline',
        'A finite event-processing chain with a terminal node.'
    ),
    (
        'cyclic_pipeline',
        'A chain whose final node points back into the chain.'
    ),
    (
        'self_cycle',
        'A single node whose next pointer points to itself.'
    );

INSERT INTO chain_node (chain_id, sequence_no, payload, next_node_id)
SELECT chain_id, sequence_no, payload, NULL
FROM (
    SELECT
        (SELECT chain_id
         FROM pointer_chain
         WHERE chain_name = 'healthy_pipeline') AS chain_id,
        *
    FROM (
        VALUES
            (1, 'ingest'),
            (2, 'validate'),
            (3, 'normalize'),
            (4, 'persist'),
            (5, 'audit')
    ) AS values_table(sequence_no, payload)
) AS healthy;

INSERT INTO chain_node (chain_id, sequence_no, payload, next_node_id)
SELECT chain_id, sequence_no, payload, NULL
FROM (
    SELECT
        (SELECT chain_id
         FROM pointer_chain
         WHERE chain_name = 'cyclic_pipeline') AS chain_id,
        *
    FROM (
        VALUES
            (1, 'ingest'),
            (2, 'validate'),
            (3, 'transform'),
            (4, 'persist'),
            (5, 'publish'),
            (6, 'notify')
    ) AS values_table(sequence_no, payload)
) AS cyclic;

INSERT INTO chain_node (chain_id, sequence_no, payload, next_node_id)
SELECT chain_id, sequence_no, payload, NULL
FROM (
    SELECT
        (SELECT chain_id
         FROM pointer_chain
         WHERE chain_name = 'self_cycle') AS chain_id,
        1,
        'retry'
) AS self_cycle(chain_id, sequence_no, payload);

-- Establish the ordinary edges. A recursive traversal query later exposes
-- the actual path represented by these relationships.
UPDATE chain_node current_node
SET next_node_id = next_node.node_id
FROM chain_node next_node
WHERE current_node.chain_id =
      (SELECT chain_id FROM pointer_chain
       WHERE chain_name = 'healthy_pipeline')
  AND next_node.chain_id = current_node.chain_id
  AND next_node.sequence_no = current_node.sequence_no + 1;

UPDATE chain_node current_node
SET next_node_id = next_node.node_id
FROM chain_node next_node
WHERE current_node.chain_id =
      (SELECT chain_id FROM pointer_chain
       WHERE chain_name = 'cyclic_pipeline')
  AND next_node.chain_id = current_node.chain_id
  AND next_node.sequence_no = current_node.sequence_no + 1;

-- The last cyclic node points back to sequence 3, producing:
-- 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 3 ...
UPDATE chain_node tail
SET next_node_id = entry.node_id
FROM chain_node entry
WHERE tail.chain_id =
      (SELECT chain_id FROM pointer_chain
       WHERE chain_name = 'cyclic_pipeline')
  AND tail.sequence_no = 6
  AND entry.chain_id = tail.chain_id
  AND entry.sequence_no = 3;

-- The single-node example points to itself.
UPDATE chain_node self_node
SET next_node_id = self_node.node_id
WHERE self_node.chain_id =
      (SELECT chain_id FROM pointer_chain
       WHERE chain_name = 'self_cycle');

-- A recursive CTE can expose a finite prefix of the linked structure.
-- The path array is also a SQL-native way to identify repeated node IDs.
WITH RECURSIVE traversal AS (
    SELECT
        n.chain_id,
        n.node_id,
        n.sequence_no,
        n.payload,
        n.next_node_id,
        1 AS depth,
        ARRAY[n.node_id]::BIGINT[] AS visited_path,
        false AS repeated
    FROM chain_node n
    WHERE n.sequence_no = 1

    UNION ALL

    SELECT
        next_node.chain_id,
        next_node.node_id,
        next_node.sequence_no,
        next_node.payload,
        next_node.next_node_id,
        traversal.depth + 1,
        traversal.visited_path || next_node.node_id,
        next_node.node_id = ANY(traversal.visited_path)
    FROM traversal
    JOIN chain_node next_node
      ON next_node.node_id = traversal.next_node_id
     AND next_node.chain_id = traversal.chain_id
    WHERE traversal.depth < 20
      AND NOT traversal.repeated
)
SELECT
    pc.chain_name,
    traversal.depth,
    traversal.sequence_no,
    traversal.payload,
    traversal.repeated
FROM traversal
JOIN pointer_chain pc
  ON pc.chain_id = traversal.chain_id
ORDER BY pc.chain_name, traversal.depth;

-- The following query detects whether a chain has a repeated node in its
-- recursive traversal. This is conceptually different from Floyd's algorithm:
-- SQL is using recursive set processing and an explicit visited path, while
-- Floyd uses two moving pointers and constant auxiliary memory.
WITH RECURSIVE traversal AS (
    SELECT
        n.chain_id,
        n.node_id,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS visited_path,
        false AS cycle_detected,
        1 AS depth
    FROM chain_node n
    WHERE n.sequence_no = 1

    UNION ALL

    SELECT
        next_node.chain_id,
        next_node.node_id,
        next_node.next_node_id,
        traversal.visited_path || next_node.node_id,
        next_node.node_id = ANY(traversal.visited_path),
        traversal.depth + 1
    FROM traversal
    JOIN chain_node next_node
      ON next_node.chain_id = traversal.chain_id
     AND next_node.node_id = traversal.next_node_id
    WHERE traversal.depth < 100
      AND NOT traversal.cycle_detected
)
SELECT
    pc.chain_name,
    COALESCE(bool_or(traversal.cycle_detected), false) AS has_cycle
FROM pointer_chain pc
LEFT JOIN traversal
  ON traversal.chain_id = pc.chain_id
GROUP BY pc.chain_name
ORDER BY pc.chain_name;

-- A recursive query can identify the repeated node and therefore expose the
-- cycle entry. The first occurrence of the repeated ID is retained in the
-- visited path, while the current row identifies the repeated node.
WITH RECURSIVE traversal AS (
    SELECT
        n.chain_id,
        n.node_id,
        n.sequence_no,
        n.payload,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS visited_path,
        1 AS depth,
        false AS repeated
    FROM chain_node n
    WHERE n.sequence_no = 1

    UNION ALL

    SELECT
        next_node.chain_id,
        next_node.node_id,
        next_node.sequence_no,
        next_node.payload,
        next_node.next_node_id,
        traversal.visited_path || next_node.node_id,
        traversal.depth + 1,
        next_node.node_id = ANY(traversal.visited_path)
    FROM traversal
    JOIN chain_node next_node
      ON next_node.chain_id = traversal.chain_id
     AND next_node.node_id = traversal.next_node_id
    WHERE traversal.depth < 100
      AND NOT traversal.repeated
)
SELECT
    pc.chain_name,
    traversal.node_id AS repeated_node_id,
    traversal.sequence_no AS cycle_entry_sequence,
    traversal.payload AS cycle_entry_payload,
    traversal.depth
FROM traversal
JOIN pointer_chain pc
  ON pc.chain_id = traversal.chain_id
WHERE traversal.repeated
ORDER BY pc.chain_name;

-- This view exposes the logical classification of each chain.
CREATE VIEW chain_integrity AS
WITH RECURSIVE traversal AS (
    SELECT
        n.chain_id,
        n.node_id,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS visited_path,
        false AS repeated,
        1 AS depth
    FROM chain_node n
    WHERE n.sequence_no = 1

    UNION ALL

    SELECT
        next_node.chain_id,
        next_node.node_id,
        next_node.next_node_id,
        traversal.visited_path || next_node.node_id,
        next_node.node_id = ANY(traversal.visited_path),
        traversal.depth + 1
    FROM traversal
    JOIN chain_node next_node
      ON next_node.chain_id = traversal.chain_id
     AND next_node.node_id = traversal.next_node_id
    WHERE traversal.depth < 100
      AND NOT traversal.repeated
)
SELECT
    pc.chain_id,
    pc.chain_name,
    CASE
        WHEN COUNT(traversal.node_id) = 0 THEN 'EMPTY'
        WHEN bool_or(traversal.repeated) THEN 'CYCLIC'
        ELSE 'ACYCLIC'
    END AS integrity_status
FROM pointer_chain pc
LEFT JOIN traversal
  ON traversal.chain_id = pc.chain_id
GROUP BY pc.chain_id, pc.chain_name;

SELECT *
FROM chain_integrity
ORDER BY chain_name;

-- PostgreSQL does not naturally encode Floyd's two moving cursors in a
-- relational query. The following PL/pgSQL function mirrors the algorithm:
-- slow advances by one edge, fast advances by two edges, and node IDs are
-- compared for identity.
CREATE OR REPLACE FUNCTION floyd_has_cycle(
    requested_chain_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    slow_id BIGINT;
    fast_id BIGINT;
    fast_next_id BIGINT;
BEGIN
    SELECT node_id
    INTO slow_id
    FROM chain_node
    WHERE chain_id = requested_chain_id
      AND sequence_no = 1;

    IF slow_id IS NULL THEN
        RETURN FALSE;
    END IF;

    fast_id := slow_id;

    LOOP
        SELECT next_node_id
        INTO fast_id
        FROM chain_node
        WHERE chain_id = requested_chain_id
          AND node_id = fast_id;

        IF fast_id IS NULL THEN
            RETURN FALSE;
        END IF;

        SELECT next_node_id
        INTO fast_next_id
        FROM chain_node
        WHERE chain_id = requested_chain_id
          AND node_id = fast_id;

        IF fast_next_id IS NULL THEN
            RETURN FALSE;
        END IF;

        SELECT next_node_id
        INTO slow_id
        FROM chain_node
        WHERE chain_id = requested_chain_id
          AND node_id = slow_id;

        IF slow_id IS NULL THEN
            RETURN FALSE;
        END IF;

        fast_id := fast_next_id;

        IF slow_id = fast_id THEN
            RETURN TRUE;
        END IF;
    END LOOP;
END;
$$;

SELECT
    chain_name,
    floyd_has_cycle(chain_id) AS floyd_detects_cycle
FROM pointer_chain
ORDER BY chain_name;

-- The database constraints reject pointers to nodes belonging to another
-- chain, preventing an invalid cross-chain pointer from masquerading as a
-- valid linked-list edge.
DO $$
DECLARE
    first_chain BIGINT;
    second_chain BIGINT;
    source_node BIGINT;
    foreign_node BIGINT;
BEGIN
    SELECT chain_id
    INTO first_chain
    FROM pointer_chain
    WHERE chain_name = 'healthy_pipeline';

    SELECT chain_id
    INTO second_chain
    FROM pointer_chain
    WHERE chain_name = 'cyclic_pipeline';

    SELECT node_id
    INTO source_node
    FROM chain_node
    WHERE chain_id = first_chain
      AND sequence_no = 1;

    SELECT node_id
    INTO foreign_node
    FROM chain_node
    WHERE chain_id = second_chain
      AND sequence_no = 1;

    BEGIN
        UPDATE chain_node
        SET next_node_id = foreign_node
        WHERE chain_id = first_chain
          AND node_id = source_node;

        RAISE EXCEPTION
            'Expected the same-chain foreign key to reject the cross-chain pointer';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'Correctly rejected cross-chain pointer.';
            ROLLBACK;
    END;
END;
$$;

-- A transactional example demonstrates that pointer changes can be validated
-- as one unit. The savepoint makes the demonstration non-destructive.
BEGIN;

SAVEPOINT before_pointer_test;

UPDATE chain_node source
SET next_node_id = target.node_id
FROM chain_node target
WHERE source.chain_id =
      (SELECT chain_id FROM pointer_chain
       WHERE chain_name = 'healthy_pipeline')
  AND target.chain_id = source.chain_id
  AND source.sequence_no = 5
  AND target.sequence_no = 3;

SELECT
    pc.chain_name,
    floyd_has_cycle(pc.chain_id) AS cycle_after_temporary_change
FROM pointer_chain pc
WHERE pc.chain_name = 'healthy_pipeline';

ROLLBACK TO SAVEPOINT before_pointer_test;
COMMIT;

-- Middle-node computation in SQL is naturally expressed by ranking or
-- counting positions. This query shows the two conventions used by the
-- procedural implementations: first middle and second middle.
WITH ordered_nodes AS (
    SELECT
        n.*,
        COUNT(*) OVER (
            PARTITION BY n.chain_id
        ) AS node_count
    FROM chain_node n
)
SELECT
    pc.chain_name,
    MAX(
        CASE
            WHEN sequence_no = floor((node_count + 1) / 2.0)
            THEN payload
        END
    ) AS first_middle_payload,
    MAX(
        CASE
            WHEN sequence_no = floor(node_count / 2.0) + 1
            THEN payload
        END
    ) AS second_middle_payload
FROM ordered_nodes n
JOIN pointer_chain pc
  ON pc.chain_id = n.chain_id
GROUP BY pc.chain_name
ORDER BY pc.chain_name;
