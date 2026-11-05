-- ============================================================
-- BALANCED TREES
-- PostgreSQL demonstration of:
-- 1. Binary search tree structure
-- 2. Height calculation
-- 3. Height-balance evaluation
-- 4. Skewed versus balanced tree performance
-- 5. Recursive tree validation and reporting
--
-- PostgreSQL 15+
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS balanced_trees;

DROP VIEW IF EXISTS balanced_trees.tree_health_report CASCADE;
DROP FUNCTION IF EXISTS balanced_trees.inspect_tree(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS balanced_trees.calculate_tree_height(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS balanced_trees.insert_node(INTEGER, INTEGER, INTEGER) CASCADE;
DROP TABLE IF EXISTS balanced_trees.tree_nodes CASCADE;
DROP TABLE IF EXISTS balanced_trees.tree_registry CASCADE;

CREATE TABLE balanced_trees.tree_registry (
    tree_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(100) NOT NULL UNIQUE,
    tree_type VARCHAR(20) NOT NULL
        CHECK (tree_type IN ('BALANCED', 'UNBALANCED')),
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE balanced_trees.tree_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id INTEGER NOT NULL
        REFERENCES balanced_trees.tree_registry(tree_id)
        ON DELETE CASCADE,

    node_key INTEGER NOT NULL,

    parent_node_id BIGINT,

    FOREIGN KEY (parent_node_id)
        REFERENCES balanced_trees.tree_nodes(node_id)
        DEFERRABLE INITIALLY DEFERRED,

    UNIQUE (tree_id, node_key),

    UNIQUE (tree_id, node_id),

    CHECK (parent_node_id IS NULL OR parent_node_id <> node_id)
);

CREATE INDEX idx_tree_nodes_parent
    ON balanced_trees.tree_nodes(tree_id, parent_node_id);

CREATE INDEX idx_tree_nodes_key
    ON balanced_trees.tree_nodes(tree_id, node_key);

-- A parent may have no more than two children.
CREATE OR REPLACE FUNCTION balanced_trees.enforce_child_limit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    child_count INTEGER;
    parent_tree INTEGER;
BEGIN
    IF NEW.parent_node_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT tree_id
    INTO parent_tree
    FROM balanced_trees.tree_nodes
    WHERE node_id = NEW.parent_node_id
    FOR UPDATE;

    IF parent_tree IS NULL THEN
        RAISE EXCEPTION 'Parent node does not exist.';
    END IF;

    IF parent_tree <> NEW.tree_id THEN
        RAISE EXCEPTION 'Parent must belong to the same tree.';
    END IF;

    IF TG_OP = 'INSERT' THEN
        SELECT COUNT(*)
        INTO child_count
        FROM balanced_trees.tree_nodes
        WHERE tree_id = NEW.tree_id
          AND parent_node_id = NEW.parent_node_id;

    ELSE
        SELECT COUNT(*)
        INTO child_count
        FROM balanced_trees.tree_nodes
        WHERE tree_id = NEW.tree_id
          AND parent_node_id = NEW.parent_node_id
          AND node_id <> OLD.node_id;
    END IF;

    IF child_count >= 2 THEN
        RAISE EXCEPTION
            'Binary tree parent cannot have more than two children.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_child_limit
BEFORE INSERT OR UPDATE OF parent_node_id
ON balanced_trees.tree_nodes
FOR EACH ROW
EXECUTE FUNCTION balanced_trees.enforce_child_limit();

-- Prevent parent cycles and preserve the tree's root.
CREATE OR REPLACE FUNCTION balanced_trees.prevent_tree_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    IF NEW.parent_node_id IS NULL THEN
        RETURN NEW;
    END IF;

    IF TG_OP = 'UPDATE' AND NEW.node_id = NEW.parent_node_id THEN
        RAISE EXCEPTION 'A node cannot be its own parent.';
    END IF;

    WITH RECURSIVE ancestors(node_id, parent_node_id) AS (
        SELECT node_id, parent_node_id
        FROM balanced_trees.tree_nodes
        WHERE node_id = NEW.parent_node_id
          AND tree_id = NEW.tree_id

        UNION ALL

        SELECT n.node_id, n.parent_node_id
        FROM balanced_trees.tree_nodes n
        JOIN ancestors a
          ON n.node_id = a.parent_node_id
        WHERE n.tree_id = NEW.tree_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM ancestors
        WHERE node_id = NEW.node_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION 'Parent assignment would create a cycle.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_tree_cycle
BEFORE INSERT OR UPDATE OF parent_node_id
ON balanced_trees.tree_nodes
FOR EACH ROW
EXECUTE FUNCTION balanced_trees.prevent_tree_cycle();

-- Calculate actual tree height using a recursive CTE.
-- Empty tree height = 0.
CREATE OR REPLACE FUNCTION balanced_trees.calculate_tree_height(
    p_tree_id INTEGER
)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE depths(node_id, depth) AS (
        SELECT node_id, 1
        FROM balanced_trees.tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_node_id IS NULL

        UNION ALL

        SELECT child.node_id, parent.depth + 1
        FROM balanced_trees.tree_nodes child
        JOIN depths parent
          ON child.parent_node_id = parent.node_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT COALESCE(MAX(depth), 0)::INTEGER
    FROM depths;
$$;

-- Return per-node subtree heights and balance factors.
CREATE OR REPLACE FUNCTION balanced_trees.inspect_tree(
    p_tree_id INTEGER
)
RETURNS TABLE (
    node_id BIGINT,
    node_key INTEGER,
    subtree_height INTEGER,
    left_height INTEGER,
    right_height INTEGER,
    balance_factor INTEGER,
    locally_balanced BOOLEAN
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE subtree_heights(node_id, height) AS (
        SELECT n.node_id, 1
        FROM balanced_trees.tree_nodes n
        WHERE n.tree_id = p_tree_id
          AND NOT EXISTS (
              SELECT 1
              FROM balanced_trees.tree_nodes child
              WHERE child.parent_node_id = n.node_id
                AND child.tree_id = p_tree_id
          )

        UNION ALL

        SELECT parent.node_id,
               1 + MAX(child.height)::INTEGER
        FROM balanced_trees.tree_nodes parent
        JOIN balanced_trees.tree_nodes child
          ON child.parent_node_id = parent.node_id
         AND child.tree_id = p_tree_id
        JOIN subtree_heights child
          ON child.node_id = child.node_id
        WHERE parent.tree_id = p_tree_id
        GROUP BY parent.node_id
    ),
    child_heights AS (
        SELECT
            parent.node_id,
            COALESCE(MAX(sh.height) FILTER (
                WHERE child.node_key < parent.node_key
            ), 0)::INTEGER AS lh,
            COALESCE(MAX(sh.height) FILTER (
                WHERE child.node_key > parent.node_key
            ), 0)::INTEGER AS rh
        FROM balanced_trees.tree_nodes parent
        LEFT JOIN balanced_trees.tree_nodes child
          ON child.parent_node_id = parent.node_id
         AND child.tree_id = p_tree_id
        LEFT JOIN subtree_heights sh
          ON sh.node_id = child.node_id
        WHERE parent.tree_id = p_tree_id
        GROUP BY parent.node_id
    )
    SELECT
        n.node_id,
        n.node_key,
        COALESCE(sh.height, 1)::INTEGER,
        ch.lh,
        ch.rh,
        ch.lh - ch.rh,
        ABS(ch.lh - ch.rh) <= 1
    FROM balanced_trees.tree_nodes n
    JOIN child_heights ch
      ON ch.node_id = n.node_id
    LEFT JOIN subtree_heights sh
      ON sh.node_id = n.node_id
    WHERE n.tree_id = p_tree_id;
$$;

-- Tree-level health report.
CREATE VIEW balanced_trees.tree_health_report AS
SELECT
    r.tree_id,
    r.tree_name,
    r.tree_type,
    COUNT(n.node_id)::INTEGER AS node_count,
    balanced_trees.calculate_tree_height(r.tree_id) AS tree_height,
    COALESCE(
        BOOL_AND(i.locally_balanced),
        TRUE
    ) AS locally_balanced
FROM balanced_trees.tree_registry r
LEFT JOIN balanced_trees.tree_nodes n
    ON n.tree_id = r.tree_id
LEFT JOIN LATERAL balanced_trees.inspect_tree(r.tree_id) i
    ON i.node_id = n.node_id
GROUP BY r.tree_id, r.tree_name, r.tree_type;

-- Insert a node into a BST by finding its parent.
CREATE OR REPLACE FUNCTION balanced_trees.insert_node(
    p_tree_id INTEGER,
    p_key INTEGER,
    p_parent_node_id INTEGER DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    current_node BIGINT;
    current_key INTEGER;
    child_node BIGINT;
    new_node BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM balanced_trees.tree_registry
        WHERE tree_id = p_tree_id
    ) THEN
        RAISE EXCEPTION 'Tree does not exist.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM balanced_trees.tree_nodes
        WHERE tree_id = p_tree_id
          AND node_key = p_key
    ) THEN
        RAISE EXCEPTION 'Duplicate key: %', p_key;
    END IF;

    SELECT node_id
    INTO current_node
    FROM balanced_trees.tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_node_id IS NULL;

    IF current_node IS NULL THEN
        IF p_parent_node_id IS NOT NULL THEN
            RAISE EXCEPTION 'First node must be the root.';
        END IF;

        INSERT INTO balanced_trees.tree_nodes(
            tree_id, node_key, parent_node_id
        )
        VALUES (p_tree_id, p_key, NULL)
        RETURNING node_id INTO new_node;

        RETURN new_node;
    END IF;

    IF p_parent_node_id IS NOT NULL THEN
        RAISE EXCEPTION
            'Explicit parent assignment is not supported by BST insertion.';
    END IF;

    LOOP
        SELECT node_key
        INTO current_key
        FROM balanced_trees.tree_nodes
        WHERE node_id = current_node;

        IF p_key < current_key THEN
            SELECT node_id
            INTO child_node
            FROM balanced_trees.tree_nodes
            WHERE parent_node_id = current_node
              AND tree_id = p_tree_id
              AND node_key < current_key;

        ELSE
            SELECT node_id
            INTO child_node
            FROM balanced_trees.tree_nodes
            WHERE parent_node_id = current_node
              AND tree_id = p_tree_id
              AND node_key > current_key;
        END IF;

        IF child_node IS NULL THEN
            INSERT INTO balanced_trees.tree_nodes(
                tree_id, node_key, parent_node_id
            )
            VALUES (p_tree_id, p_key, current_node)
            RETURNING node_id INTO new_node;

            RETURN new_node;
        END IF;

        current_node := child_node;
    END LOOP;
END;
$$;

-- Create demonstration trees.
INSERT INTO balanced_trees.tree_registry(
    tree_name, tree_type, description
)
VALUES
(
    'balanced_sample',
    'BALANCED',
    'A manually constructed height-balanced binary search tree.'
),
(
    'skewed_sample',
    'UNBALANCED',
    'A BST receiving monotonically increasing keys.'
),
(
    'empty_sample',
    'BALANCED',
    'An empty tree used for boundary testing.'
);

-- Balanced tree:
--               40
--             /    \
--           20      60
--          /  \    /  \
--        10   30  50   70
--
--                5
--               / \
--              2   8
--
-- The sample uses a balanced tree with seven nodes.

DO $$
DECLARE
    balanced_id INTEGER;
    skewed_id INTEGER;
    value INTEGER;
BEGIN
    SELECT tree_id INTO balanced_id
    FROM balanced_trees.tree_registry
    WHERE tree_name = 'balanced_sample';

    SELECT tree_id INTO skewed_id
    FROM balanced_trees.tree_registry
    WHERE tree_name = 'skewed_sample';

    INSERT INTO balanced_trees.tree_nodes(
        tree_id, node_key, parent_node_id
    )
    VALUES (balanced_id, 40, NULL);

    PERFORM balanced_trees.insert_node(balanced_id, 20);
    PERFORM balanced_trees.insert_node(balanced_id, 60);
    PERFORM balanced_trees.insert_node(balanced_id, 10);
    PERFORM balanced_trees.insert_node(balanced_id, 30);
    PERFORM balanced_trees.insert_node(balanced_id, 50);
    PERFORM balanced_trees.insert_node(balanced_id, 70);

    -- Increasing keys produce a right-skewed BST.
    FOR value IN 1..15 LOOP
        PERFORM balanced_trees.insert_node(skewed_id, value);
    END LOOP;
END;
$$;

-- ============================================================
-- RETRIEVAL
-- ============================================================

SELECT *
FROM balanced_trees.tree_nodes
ORDER BY tree_id, node_key;

-- ============================================================
-- HEIGHT AND BALANCE EVALUATION
-- ============================================================

SELECT *
FROM balanced_trees.tree_health_report
ORDER BY tree_id;

SELECT *
FROM balanced_trees.inspect_tree(
    (
        SELECT tree_id
        FROM balanced_trees.tree_registry
        WHERE tree_name = 'balanced_sample'
    )
)
ORDER BY node_key;

-- ============================================================
-- AGGREGATION
-- ============================================================

SELECT
    tree_type,
    COUNT(*) AS number_of_trees,
    SUM(node_count) AS total_nodes,
    ROUND(AVG(tree_height), 2) AS average_height,
    MAX(tree_height) AS maximum_height
FROM balanced_trees.tree_health_report
GROUP BY tree_type;

-- ============================================================
-- VALIDATION
-- ============================================================

-- A tree with no nodes has height zero.
SELECT
    tree_name,
    tree_height,
    node_count,
    locally_balanced
FROM balanced_trees.tree_health_report
WHERE tree_name = 'empty_sample';

-- Detect locally unbalanced nodes.
SELECT
    r.tree_name,
    i.node_key,
    i.left_height,
    i.right_height,
    i.balance_factor
FROM balanced_trees.tree_registry r
JOIN LATERAL balanced_trees.inspect_tree(r.tree_id) i
    ON TRUE
WHERE NOT i.locally_balanced;

-- ============================================================
-- WORKFLOW PROCESSING
-- ============================================================

-- Insert a key into the balanced sample using BST insertion.
SELECT balanced_trees.insert_node(
    (
        SELECT tree_id
        FROM balanced_trees.tree_registry
        WHERE tree_name = 'balanced_sample'
    ),
    25
);

-- Verify the updated tree.
SELECT *
FROM balanced_trees.tree_health_report
WHERE tree_name = 'balanced_sample';

-- ============================================================
-- PERFORMANCE COMPARISON
-- ============================================================

SELECT
    tree_name,
    node_count,
    tree_height,
    CASE
        WHEN node_count = 0 THEN 0
        ELSE tree_height
    END AS worst_case_search_depth,
    CASE
        WHEN tree_height <= CEIL(
            2.0 * LN(node_count + 1) / LN(2.0)
        )
        THEN 'WITHIN_REFERENCE_BOUND'
        ELSE 'EXCEEDS_REFERENCE_BOUND'
    END AS height_assessment
FROM balanced_trees.tree_health_report
ORDER BY tree_height;

-- ============================================================
-- FAILURE HANDLING
-- ============================================================

-- The following operations are intentionally executed inside
-- exception blocks so the complete script remains executable.

DO $$
DECLARE
    sample_id INTEGER;
BEGIN
    SELECT tree_id INTO sample_id
    FROM balanced_trees.tree_registry
    WHERE tree_name = 'balanced_sample';

    BEGIN
        PERFORM balanced_trees.insert_node(sample_id, 40);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected duplicate-key failure: %',
            SQLERRM;
    END;

    BEGIN
        INSERT INTO balanced_trees.tree_nodes(
            tree_id, node_key, parent_node_id
        )
        VALUES (sample_id, 999, -1);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected invalid-parent failure: %',
            SQLERRM;
    END;
END;
$$;

-- ============================================================
-- FINAL REPORT
-- ============================================================

SELECT
    tree_name,
    tree_type,
    node_count,
    tree_height,
    locally_balanced,
    CASE
        WHEN node_count = 0 THEN 'EMPTY'
        WHEN locally_balanced THEN 'HEIGHT_BALANCED'
        ELSE 'UNBALANCED'
    END AS health_status
FROM balanced_trees.tree_health_report
ORDER BY tree_name;

COMMIT;
