-- Binary tree fundamentals: relational adjacency-list model.
-- Target: PostgreSQL 14 or later.
--
-- Height is measured in edges: a leaf has height 0.
-- Depth is measured in edges: the root has depth 0.
-- Level is depth + 1: the root is on level 1.
--
-- The adjacency-list representation stores each node's parent and whether
-- it occupies that parent's left or right child position.

DROP SCHEMA IF EXISTS tree_lab CASCADE;
CREATE SCHEMA tree_lab;

SET search_path = tree_lab, public;

CREATE TABLE binary_trees (
    tree_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name     VARCHAR(120) NOT NULL UNIQUE,
    description   TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_tree_name
        CHECK (length(btrim(tree_name)) BETWEEN 1 AND 120)
);

CREATE TABLE tree_nodes (
    node_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id          BIGINT NOT NULL,
    node_key         VARCHAR(80) NOT NULL,
    node_value       VARCHAR(200) NOT NULL,
    parent_node_id   BIGINT,
    child_side       VARCHAR(5),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_node_tree
        FOREIGN KEY (tree_id)
        REFERENCES binary_trees(tree_id)
        ON DELETE CASCADE,

    -- This composite key permits a parent reference only within the same tree.
    CONSTRAINT uq_tree_node_identity
        UNIQUE (tree_id, node_id),

    CONSTRAINT fk_node_parent_same_tree
        FOREIGN KEY (tree_id, parent_node_id)
        REFERENCES tree_nodes(tree_id, node_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_node_key_per_tree
        UNIQUE (tree_id, node_key),

    CONSTRAINT valid_node_key
        CHECK (length(btrim(node_key)) BETWEEN 1 AND 80),

    CONSTRAINT valid_node_value
        CHECK (length(btrim(node_value)) BETWEEN 1 AND 200),

    CONSTRAINT valid_child_position
        CHECK (
            (parent_node_id IS NULL AND child_side IS NULL)
            OR
            (
                parent_node_id IS NOT NULL
                AND child_side IN ('left', 'right')
            )
        ),

    CONSTRAINT node_cannot_parent_itself
        CHECK (parent_node_id IS DISTINCT FROM node_id)
);

-- A tree can have at most one root. An empty tree is allowed while it is
-- being constructed.
CREATE UNIQUE INDEX uq_one_root_per_tree
    ON tree_nodes(tree_id)
    WHERE parent_node_id IS NULL;

-- A parent can have at most one left child and one right child.
CREATE UNIQUE INDEX uq_one_child_per_side
    ON tree_nodes(tree_id, parent_node_id, child_side)
    WHERE parent_node_id IS NOT NULL;

-- This trigger prevents cycles during reparenting and protects node identity.
-- Foreign keys and unique indexes enforce same-tree parents and child slots.
CREATE OR REPLACE FUNCTION validate_tree_node_structure()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cycle_found BOOLEAN := FALSE;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF NEW.node_id <> OLD.node_id OR NEW.tree_id <> OLD.tree_id THEN
            RAISE EXCEPTION 'Node identity and tree ownership are immutable.'
                USING ERRCODE = '23514';
        END IF;

        -- Moving a root under another node is prohibited. A tree has one
        -- designated root, and changing it requires a controlled rebuild.
        IF OLD.parent_node_id IS NULL
           AND NEW.parent_node_id IS NOT NULL THEN
            RAISE EXCEPTION 'The root cannot be reparented.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.parent_node_id IS NOT NULL THEN
        -- Walk upward from the proposed parent. If the node being updated
        -- appears among its ancestors, the proposed change creates a cycle.
        WITH RECURSIVE ancestors(node_id, parent_node_id) AS (
            SELECT n.node_id, n.parent_node_id
            FROM tree_nodes AS n
            WHERE n.tree_id = NEW.tree_id
              AND n.node_id = NEW.parent_node_id

            UNION

            SELECT p.node_id, p.parent_node_id
            FROM tree_nodes AS p
            JOIN ancestors AS a
              ON p.tree_id = NEW.tree_id
             AND p.node_id = a.parent_node_id
        )
        SELECT EXISTS (
            SELECT 1
            FROM ancestors
            WHERE node_id = NEW.node_id
        )
        INTO v_cycle_found;

        IF v_cycle_found THEN
            RAISE EXCEPTION
                'Attachment rejected: it would create a cycle.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_tree_node_structure
BEFORE INSERT OR UPDATE OF node_id, tree_id, parent_node_id
ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION validate_tree_node_structure();

-- All node insertion passes through this function. Database constraints and
-- the trigger remain the final protection against invalid relationships.
CREATE OR REPLACE FUNCTION add_tree_node(
    p_tree_id BIGINT,
    p_node_key VARCHAR,
    p_node_value VARCHAR,
    p_parent_node_id BIGINT DEFAULT NULL,
    p_child_side VARCHAR DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_node_id BIGINT;
BEGIN
    IF p_parent_node_id IS NULL AND p_child_side IS NOT NULL THEN
        RAISE EXCEPTION
            'A root must not specify a child position.'
            USING ERRCODE = '23514';
    END IF;

    IF p_parent_node_id IS NOT NULL
       AND p_child_side NOT IN ('left', 'right') THEN
        RAISE EXCEPTION
            'A non-root node requires a left or right position.'
            USING ERRCODE = '23514';
    END IF;

    INSERT INTO tree_nodes (
        tree_id,
        node_key,
        node_value,
        parent_node_id,
        child_side
    )
    VALUES (
        p_tree_id,
        p_node_key,
        p_node_value,
        p_parent_node_id,
        p_child_side
    )
    RETURNING node_id INTO v_node_id;

    RETURN v_node_id;
END;
$$;

-- The recursive view starts at each root and follows parent-to-child links.
-- The path array is a defensive guard against accidental recursive repetition.
CREATE OR REPLACE VIEW v_tree_node_metrics AS
WITH RECURSIVE walk AS (
    SELECT
        n.tree_id,
        n.node_id,
        n.node_key,
        n.node_value,
        n.parent_node_id,
        n.child_side,
        0::INTEGER AS depth,
        ARRAY[n.node_id]::BIGINT[] AS path
    FROM tree_nodes AS n
    WHERE n.parent_node_id IS NULL

    UNION ALL

    SELECT
        child.tree_id,
        child.node_id,
        child.node_key,
        child.node_value,
        child.parent_node_id,
        child.child_side,
        parent.depth + 1,
        parent.path || child.node_id
    FROM walk AS parent
    JOIN tree_nodes AS child
      ON child.tree_id = parent.tree_id
     AND child.parent_node_id = parent.node_id
    WHERE NOT child.node_id = ANY(parent.path)
),
metrics AS (
    SELECT
        w.tree_id,
        w.node_id,
        w.node_key,
        w.node_value,
        w.parent_node_id,
        w.child_side,
        w.depth,
        w.depth + 1 AS level,

        NOT EXISTS (
            SELECT 1
            FROM tree_nodes AS child
            WHERE child.tree_id = w.tree_id
              AND child.parent_node_id = w.node_id
        ) AS is_leaf,

        COALESCE(
            (
                SELECT MAX(descendant.depth - w.depth)
                FROM walk AS descendant
                WHERE descendant.tree_id = w.tree_id
                  AND descendant.path @> ARRAY[w.node_id]::BIGINT[]
            ),
            0
        )::INTEGER AS node_height,

        (
            SELECT COUNT(*)::INTEGER
            FROM walk AS descendant
            WHERE descendant.tree_id = w.tree_id
              AND descendant.path @> ARRAY[w.node_id]::BIGINT[]
        ) AS subtree_size
    FROM walk AS w
)
SELECT
    tree_id,
    node_id,
    node_key,
    node_value,
    parent_node_id,
    child_side,
    depth,
    level,
    node_height,
    is_leaf,
    subtree_size
FROM metrics;

CREATE OR REPLACE VIEW v_tree_summary AS
SELECT
    t.tree_id,
    t.tree_name,
    COUNT(m.node_id)::INTEGER AS node_count,
    COALESCE(
        MAX(m.node_height) FILTER (WHERE m.parent_node_id IS NULL),
        -1
    )::INTEGER AS tree_height,
    COALESCE(MAX(m.depth), -1)::INTEGER AS maximum_depth,
    COUNT(*) FILTER (WHERE m.is_leaf)::INTEGER AS leaf_count
FROM binary_trees AS t
LEFT JOIN v_tree_node_metrics AS m
  ON m.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name;

CREATE OR REPLACE FUNCTION tree_height(p_tree_id BIGINT)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(
        MAX(node_height) FILTER (WHERE parent_node_id IS NULL),
        -1
    )::INTEGER
    FROM v_tree_node_metrics
    WHERE tree_id = p_tree_id;
$$;

-- ---------------------------------------------------------------------
-- Manual construction of a sample tree.
--
--              A
--             / \
--            B   C
--           / \   \
--          D   E   F
--             /
--            G
-- ---------------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    v_tree_id BIGINT;
    v_a BIGINT;
    v_b BIGINT;
    v_c BIGINT;
    v_d BIGINT;
    v_e BIGINT;
    v_f BIGINT;
    v_g BIGINT;
BEGIN
    INSERT INTO binary_trees(tree_name, description)
    VALUES (
        'Binary Tree Fundamentals',
        'A manually constructed seven-node binary tree.'
    )
    RETURNING tree_id INTO v_tree_id;

    v_a := add_tree_node(
        v_tree_id, 'A', 'Root', NULL, NULL
    );

    v_b := add_tree_node(
        v_tree_id, 'B', 'Left child of A', v_a, 'left'
    );

    v_c := add_tree_node(
        v_tree_id, 'C', 'Right child of A', v_a, 'right'
    );

    v_d := add_tree_node(
        v_tree_id, 'D', 'Left child of B', v_b, 'left'
    );

    v_e := add_tree_node(
        v_tree_id, 'E', 'Right child of B', v_b, 'right'
    );

    v_f := add_tree_node(
        v_tree_id, 'F', 'Right child of C', v_c, 'right'
    );

    v_g := add_tree_node(
        v_tree_id, 'G', 'Left child of E', v_e, 'left'
    );

    -- Duplicate child-side test. The unique index must reject a second
    -- left child of B. The exception block keeps the demonstration usable.
    BEGIN
        PERFORM add_tree_node(
            v_tree_id,
            'X',
            'Invalid second left child',
            v_b,
            'left'
        );

        RAISE EXCEPTION 'Expected duplicate child-side rejection.';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Correctly rejected a second left child of B.';
    END;

    -- Cycle test: B is moved below G, even though G is already a descendant
    -- of B. The trigger must reject the update.
    BEGIN
        UPDATE tree_nodes
        SET parent_node_id = v_g,
            child_side = 'right'
        WHERE node_id = v_b;

        RAISE EXCEPTION 'Expected cycle rejection.';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Correctly rejected a cycle-producing update.';
    END;
END;
$$;

COMMIT;

-- ---------------------------------------------------------------------
-- Retrieval: display each node and its direct relationships.
-- ---------------------------------------------------------------------

SELECT
    n.node_key,
    n.node_value,
    parent.node_key AS parent_key,
    left_child.node_key AS left_child_key,
    right_child.node_key AS right_child_key
FROM tree_nodes AS n
LEFT JOIN tree_nodes AS parent
  ON parent.tree_id = n.tree_id
 AND parent.node_id = n.parent_node_id
LEFT JOIN tree_nodes AS left_child
  ON left_child.tree_id = n.tree_id
 AND left_child.parent_node_id = n.node_id
 AND left_child.child_side = 'left'
LEFT JOIN tree_nodes AS right_child
  ON right_child.tree_id = n.tree_id
 AND right_child.parent_node_id = n.node_id
 AND right_child.child_side = 'right'
ORDER BY n.node_id;

-- ---------------------------------------------------------------------
-- Validation and evaluation: depth, level, height, leaf, subtree size.
-- ---------------------------------------------------------------------

SELECT
    node_key,
    parent_node_id,
    child_side,
    depth,
    level,
    node_height,
    is_leaf,
    subtree_size
FROM v_tree_node_metrics
ORDER BY depth, node_key;

-- The root has depth 0, level 1, and height 3.
-- G has depth 3 and level 4.
SELECT
    node_key,
    depth,
    level,
    node_height,
    is_leaf
FROM v_tree_node_metrics
WHERE node_key IN ('A', 'B', 'D', 'G', 'F')
ORDER BY node_key;

-- ---------------------------------------------------------------------
-- Aggregation: number of nodes at each level.
-- ---------------------------------------------------------------------

SELECT
    tree_id,
    level,
    COUNT(*) AS nodes_at_level
FROM v_tree_node_metrics
GROUP BY tree_id, level
ORDER BY tree_id, level;

-- Tree-level counts and height.
SELECT *
FROM v_tree_summary
ORDER BY tree_id;

-- ---------------------------------------------------------------------
-- Subtree evaluation: inspect the subtree rooted at B.
-- ---------------------------------------------------------------------

SELECT
    node_key AS subtree_root,
    node_height AS subtree_height,
    subtree_size
FROM v_tree_node_metrics
WHERE node_key = 'B';

-- Return all nodes whose root-to-node path passes through B.
-- The view does not expose paths, so the subtree can also be reconstructed
-- by a recursive traversal that starts at B.
WITH RECURSIVE subtree AS (
    SELECT
        n.node_id,
        n.tree_id,
        n.node_key,
        n.parent_node_id,
        0 AS relative_depth
    FROM tree_nodes AS n
    WHERE n.node_key = 'B'

    UNION ALL

    SELECT
        child.node_id,
        child.tree_id,
        child.node_key,
        child.parent_node_id,
        parent.relative_depth + 1
    FROM subtree AS parent
    JOIN tree_nodes AS child
      ON child.tree_id = parent.tree_id
     AND child.parent_node_id = parent.node_id
)
SELECT node_key, relative_depth
FROM subtree
ORDER BY relative_depth, node_key;

-- ---------------------------------------------------------------------
-- Eligibility and structural validation.
-- A valid non-empty binary tree has exactly one root and no node may occupy
-- more than one child position. Constraints and the trigger enforce these
-- invariants during insertion and updates.
-- ---------------------------------------------------------------------

SELECT
    t.tree_id,
    t.tree_name,
    COUNT(n.node_id) FILTER (
        WHERE n.parent_node_id IS NULL
    ) AS root_count,
    COUNT(n.node_id) AS stored_node_count,
    COALESCE(s.node_count, 0) AS reachable_node_count,
    CASE
        WHEN COUNT(n.node_id) = 0 THEN 'EMPTY'
        WHEN COUNT(n.node_id) FILTER (
            WHERE n.parent_node_id IS NULL
        ) <> 1 THEN 'INVALID_ROOT_COUNT'
        WHEN COUNT(n.node_id) <> COALESCE(s.node_count, 0)
            THEN 'DISCONNECTED_NODES'
        ELSE 'STRUCTURALLY_VALID'
    END AS validation_status
FROM binary_trees AS t
LEFT JOIN tree_nodes AS n
  ON n.tree_id = t.tree_id
LEFT JOIN v_tree_summary AS s
  ON s.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name, s.node_count
ORDER BY t.tree_id;

-- Function-based height lookup. An empty tree has height -1.
SELECT
    tree_id,
    tree_name,
    tree_height(tree_id) AS measured_height
FROM binary_trees
ORDER BY tree_id;

-- ---------------------------------------------------------------------
-- Operational considerations:
-- - Parent references use composite foreign keys to prevent cross-tree links.
-- - Partial unique indexes enforce one root and one child per side.
-- - The trigger prevents cycle-producing reparenting.
-- - Recursive metrics are computed from roots; deep trees can make recursive
--   reporting expensive, so large workloads may cache derived metrics.
-- ---------------------------------------------------------------------
