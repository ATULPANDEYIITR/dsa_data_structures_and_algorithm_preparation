-- ============================================================
-- BINARY SEARCH TREE FUNDAMENTALS
-- PostgreSQL relational implementation using adjacency lists.
--
-- Each node stores its parent and whether it is a left or
-- right child. The root has no parent and no child position.
-- ============================================================

BEGIN;

DROP SCHEMA IF EXISTS bst_fundamentals CASCADE;

CREATE SCHEMA bst_fundamentals;

SET search_path TO bst_fundamentals, public;

-- ------------------------------------------------------------
-- 1. TREE AND NODE TABLES
-- ------------------------------------------------------------

CREATE TABLE bst_tree (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bst_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES bst_tree(tree_id)
        ON DELETE CASCADE,

    node_key INTEGER NOT NULL,

    parent_id BIGINT,

    position CHAR(1),

    CONSTRAINT uq_tree_key
        UNIQUE (tree_id, node_key),

    CONSTRAINT uq_tree_node
        UNIQUE (tree_id, node_id),

    CONSTRAINT fk_parent_same_tree
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT ck_position
        CHECK (position IN ('L', 'R') OR position IS NULL),

    CONSTRAINT ck_root_position
        CHECK (
            (parent_id IS NULL AND position IS NULL)
            OR
            (parent_id IS NOT NULL AND position IS NOT NULL)
        )
);

-- One root per tree.
CREATE UNIQUE INDEX uq_bst_root
ON bst_node(tree_id)
WHERE parent_id IS NULL;

-- One left child and one right child per parent.
CREATE UNIQUE INDEX uq_bst_child_position
ON bst_node(tree_id, parent_id, position)
WHERE parent_id IS NOT NULL;

CREATE INDEX idx_bst_parent
ON bst_node(tree_id, parent_id);

CREATE INDEX idx_bst_key
ON bst_node(tree_id, node_key);

-- ------------------------------------------------------------
-- 2. ROOT CREATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_tree(
    p_tree_name VARCHAR
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_tree_id BIGINT;
BEGIN
    IF p_tree_name IS NULL OR BTRIM(p_tree_name) = '' THEN
        RAISE EXCEPTION 'Tree name cannot be empty.';
    END IF;

    INSERT INTO bst_tree(tree_name)
    VALUES (p_tree_name)
    RETURNING tree_id INTO v_tree_id;

    RETURN v_tree_id;
END;
$$;

-- ------------------------------------------------------------
-- 3. BST INSERTION
-- Concurrent insertions for the same tree are serialized
-- using a transaction-level advisory lock.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION insert_node(
    p_tree_id BIGINT,
    p_key INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_current bst_node%ROWTYPE;
    v_new_id BIGINT;
    v_position CHAR(1);
BEGIN
    IF p_key IS NULL THEN
        RAISE EXCEPTION 'BST key cannot be NULL.';
    END IF;

    -- Lock the logical tree before traversing or inserting.
    PERFORM pg_advisory_xact_lock(p_tree_id);

    PERFORM 1
    FROM bst_tree
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist.', p_tree_id;
    END IF;

    SELECT *
    INTO v_current
    FROM bst_node
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    IF NOT FOUND THEN
        INSERT INTO bst_node(tree_id, node_key)
        VALUES (p_tree_id, p_key)
        RETURNING node_id INTO v_new_id;

        RETURN v_new_id;
    END IF;

    LOOP
        IF p_key = v_current.node_key THEN
            RAISE EXCEPTION 'Duplicate BST key: %', p_key
                USING ERRCODE = '23505';
        ELSIF p_key < v_current.node_key THEN
            v_position := 'L';
        ELSE
            v_position := 'R';
        END IF;

        SELECT *
        INTO v_current
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND parent_id = v_current.node_id
          AND position = v_position;

        IF NOT FOUND THEN
            EXIT;
        END IF;
    END LOOP;

    INSERT INTO bst_node(
        tree_id,
        node_key,
        parent_id,
        position
    )
    VALUES (
        p_tree_id,
        p_key,
        v_current.node_id,
        v_position
    )
    RETURNING node_id INTO v_new_id;

    RETURN v_new_id;
END;
$$;

-- ------------------------------------------------------------
-- 4. SEARCH
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION search_node(
    p_tree_id BIGINT,
    p_key INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_current bst_node%ROWTYPE;
BEGIN
    SELECT *
    INTO v_current
    FROM bst_node
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    LOOP
        IF p_key = v_current.node_key THEN
            RETURN v_current.node_id;
        END IF;

        IF p_key < v_current.node_key THEN
            SELECT *
            INTO v_current
            FROM bst_node
            WHERE tree_id = p_tree_id
              AND parent_id = v_current.node_id
              AND position = 'L';
        ELSE
            SELECT *
            INTO v_current
            FROM bst_node
            WHERE tree_id = p_tree_id
              AND parent_id = v_current.node_id
              AND position = 'R';
        END IF;

        IF NOT FOUND THEN
            RETURN NULL;
        END IF;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 5. INORDER TRAVERSAL
-- Recursive CTE produces sorted keys for a valid BST.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION inorder_keys(
    p_tree_id BIGINT
)
RETURNS TABLE(node_key INTEGER)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE traversal AS (
        SELECT
            n.node_id,
            n.node_key,
            n.parent_id,
            n.position,
            0 AS depth,
            ARRAY[n.node_id] AS visited
        FROM bst_node n
        WHERE n.tree_id = p_tree_id
          AND n.parent_id IS NULL

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.parent_id,
            child.position,
            parent.depth + 1,
            parent.visited || child.node_id
        FROM traversal parent
        JOIN bst_node child
          ON child.parent_id = parent.node_id
         AND child.tree_id = p_tree_id
        WHERE NOT child.node_id = ANY(parent.visited)
    )
    SEARCH DEPTH FIRST BY position SET traversal_order
    CYCLE node_id SET is_cycle USING cycle_path
    SELECT t.node_key
    FROM traversal t
    WHERE NOT t.is_cycle
    ORDER BY t.traversal_order;
$$;

-- ------------------------------------------------------------
-- 6. MINIMUM AND MAXIMUM
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION minimum_key(
    p_tree_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_key INTEGER;
BEGIN
    SELECT node_key
    INTO v_key
    FROM inorder_keys(p_tree_id)
    ORDER BY node_key
    LIMIT 1;

    RETURN v_key;
END;
$$;

CREATE OR REPLACE FUNCTION maximum_key(
    p_tree_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_key INTEGER;
BEGIN
    SELECT node_key
    INTO v_key
    FROM inorder_keys(p_tree_id)
    ORDER BY node_key DESC
    LIMIT 1;

    RETURN v_key;
END;
$$;

-- ------------------------------------------------------------
-- 7. TREE REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW tree_statistics AS
SELECT
    t.tree_id,
    t.tree_name,
    COUNT(n.node_id) AS node_count,
    MIN(n.node_key) AS minimum_key,
    MAX(n.node_key) AS maximum_key
FROM bst_tree t
LEFT JOIN bst_node n
    ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name;

-- ------------------------------------------------------------
-- 8. BST INTEGRITY VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_bst(
    p_tree_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_invalid INTEGER;
    v_count BIGINT;
    v_reachable BIGINT;
BEGIN
    -- Check that every child respects its direct parent.
    SELECT COUNT(*)
    INTO v_invalid
    FROM bst_node child
    JOIN bst_node parent
      ON parent.tree_id = child.tree_id
     AND parent.node_id = child.parent_id
    WHERE child.tree_id = p_tree_id
      AND (
          (child.position = 'L'
              AND child.node_key >= parent.node_key)
          OR
          (child.position = 'R'
              AND child.node_key <= parent.node_key)
      );

    IF v_invalid > 0 THEN
        RETURN FALSE;
    END IF;

    -- Verify the full ancestor-based BST ordering.
    WITH RECURSIVE bounds AS (
        SELECT
            node_id,
            node_key,
            NULL::BIGINT AS parent_id,
            NULL::INTEGER AS lower_bound,
            NULL::INTEGER AS upper_bound,
            ARRAY[node_id] AS visited
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND parent_id IS NULL

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.parent_id,
            CASE
                WHEN child.position = 'R' THEN parent.node_key
                ELSE parent.lower_bound
            END,
            CASE
                WHEN child.position = 'L' THEN parent.node_key
                ELSE parent.upper_bound
            END,
            parent.visited || child.node_id
        FROM bounds parent
        JOIN bst_node child
          ON child.parent_id = parent.node_id
         AND child.tree_id = p_tree_id
        WHERE NOT child.node_id = ANY(parent.visited)
    )
    SELECT COUNT(*)
    INTO v_invalid
    FROM bounds
    WHERE (lower_bound IS NOT NULL AND node_key <= lower_bound)
       OR (upper_bound IS NOT NULL AND node_key >= upper_bound);

    IF v_invalid > 0 THEN
        RETURN FALSE;
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM bst_node
    WHERE tree_id = p_tree_id;

    WITH RECURSIVE reachable AS (
        SELECT node_id
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND parent_id IS NULL

        UNION

        SELECT child.node_id
        FROM bst_node child
        JOIN reachable parent
          ON child.parent_id = parent.node_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT COUNT(*)
    INTO v_reachable
    FROM reachable;

    RETURN v_count = v_reachable;
END;
$$;

-- ------------------------------------------------------------
-- 9. SAMPLE TREE
-- ------------------------------------------------------------

INSERT INTO bst_tree(tree_name)
VALUES ('Product Inventory Index');

INSERT INTO bst_node(tree_id, node_key)
SELECT tree_id, 50
FROM bst_tree
WHERE tree_name = 'Product Inventory Index';

-- Insert remaining keys using the actual insertion function.
DO $$
DECLARE
    v_tree_id BIGINT;
    v_key INTEGER;
BEGIN
    SELECT tree_id
    INTO v_tree_id
    FROM bst_tree
    WHERE tree_name = 'Product Inventory Index';

    FOREACH v_key IN ARRAY ARRAY[
        30, 70, 20, 40, 60, 80, 35, 45
    ]
    LOOP
        PERFORM insert_node(v_tree_id, v_key);
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 10. RETRIEVAL QUERIES
-- ------------------------------------------------------------

SELECT *
FROM tree_statistics;

SELECT node_key
FROM inorder_keys(1);

SELECT search_node(1, 40) AS found_node_id;

SELECT minimum_key(1) AS smallest_key;

SELECT maximum_key(1) AS largest_key;

-- ------------------------------------------------------------
-- 11. VALIDATION AND REPORTING
-- ------------------------------------------------------------

SELECT validate_bst(1) AS is_valid_bst;

SELECT
    tree_id,
    tree_name,
    node_count,
    minimum_key,
    maximum_key,
    CASE
        WHEN node_count = 0 THEN 'EMPTY'
        WHEN node_count = 1 THEN 'SINGLE NODE'
        ELSE 'POPULATED'
    END AS tree_state
FROM tree_statistics;

-- Verify duplicate protection.
DO $$
BEGIN
    BEGIN
        PERFORM insert_node(1, 50);
        RAISE EXCEPTION 'Duplicate key was unexpectedly accepted.';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Duplicate key correctly rejected.';
    END;
END;
$$;

-- ------------------------------------------------------------
-- 12. TRANSACTION AND FAILURE HANDLING
-- A failed insertion is rolled back without affecting
-- previously committed tree data.
-- ------------------------------------------------------------

SAVEPOINT before_test_insertion;

SELECT insert_node(1, 90);

ROLLBACK TO SAVEPOINT before_test_insertion;

-- ------------------------------------------------------------
-- 13. ELIGIBILITY AND AGGREGATION
-- Identify keys greater than the current root.
-- ------------------------------------------------------------

WITH root_node AS (
    SELECT node_key
    FROM bst_node
    WHERE tree_id = 1
      AND parent_id IS NULL
)
SELECT
    n.node_key,
    CASE
        WHEN n.node_key < r.node_key THEN 'LEFT OF ROOT'
        WHEN n.node_key > r.node_key THEN 'RIGHT OF ROOT'
        ELSE 'ROOT'
    END AS position
FROM bst_node n
CROSS JOIN root_node r
WHERE n.tree_id = 1
ORDER BY n.node_key;

SELECT
    tree_id,
    COUNT(*) AS total_nodes,
    COUNT(*) FILTER (WHERE position = 'L') AS left_children,
    COUNT(*) FILTER (WHERE position = 'R') AS right_children
FROM bst_node
GROUP BY tree_id;

-- ------------------------------------------------------------
-- 14. EMPTY TREE EDGE CASE
-- ------------------------------------------------------------

INSERT INTO bst_tree(tree_name)
VALUES ('Empty Test Tree');

SELECT *
FROM tree_statistics
WHERE tree_name = 'Empty Test Tree';

SELECT validate_bst(
    (
        SELECT tree_id
        FROM bst_tree
        WHERE tree_name = 'Empty Test Tree'
    )
) AS empty_tree_valid;

-- ------------------------------------------------------------
-- 15. DATABASE SECURITY AND OPERATIONAL NOTES
-- ------------------------------------------------------------
-- Production deployments should:
-- 1. Restrict DDL and write privileges to authorized roles.
-- 2. Grant read-only access separately.
-- 3. Use parameterized queries from application code.
-- 4. Keep tree mutations inside transactions.
-- 5. Use consistent advisory-lock conventions.
-- 6. Monitor tree height and rebuild unbalanced trees.
-- 7. Apply resource limits to recursive queries.
--
-- Direct modifications to parent_id or position should be
-- restricted because they can violate global BST ordering.
--
-- The adjacency-list model enforces structural uniqueness
-- and parent references. Application-level mutation functions
-- enforce ordering during normal insertions.

COMMIT;
