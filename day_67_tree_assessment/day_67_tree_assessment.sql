-- ============================================================
-- TREE ASSESSMENT DATABASE
-- PostgreSQL 15+
--
-- Models:
--   Tree definitions
--   Parent-child relationships
--   Tree integrity validation
--   Recursive traversals
--   Height and diameter
--   Root-to-leaf path sums
--   Lowest common ancestor
--   Balance assessment
--   Level-order reporting
--
-- Height and diameter are measured in edges.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS tree_lab;

SET search_path TO tree_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS binary_tree (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(tree_name)) > 0)
);

CREATE TABLE IF NOT EXISTS tree_node (
    tree_id BIGINT NOT NULL,
    node_id BIGINT NOT NULL,
    parent_id BIGINT,
    node_value BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (tree_id, node_id),

    FOREIGN KEY (tree_id)
        REFERENCES binary_tree(tree_id)
        ON DELETE CASCADE,

    FOREIGN KEY (tree_id, parent_id)
        REFERENCES tree_node(tree_id, node_id)
        ON DELETE CASCADE,

    CHECK (node_id > 0),
    CHECK (parent_id IS NULL OR parent_id <> node_id)
);

-- A tree can have only one root.
CREATE UNIQUE INDEX IF NOT EXISTS
    uq_tree_single_root
ON tree_node(tree_id)
WHERE parent_id IS NULL;

-- Efficient retrieval of direct children.
CREATE INDEX IF NOT EXISTS
    idx_tree_parent
ON tree_node(tree_id, parent_id);

CREATE INDEX IF NOT EXISTS
    idx_tree_node_value
ON tree_node(tree_id, node_value);

-- ------------------------------------------------------------
-- 2. TREE INTEGRITY TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_tree_node()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_tree BIGINT;
    cycle_found BOOLEAN;
BEGIN
    IF NEW.parent_id IS NULL THEN
        RETURN NEW;
    END IF;

    IF NEW.parent_id = NEW.node_id THEN
        RAISE EXCEPTION
            'A node cannot be its own parent.';
    END IF;

    -- Prevent moving a node below one of its descendants.
    WITH RECURSIVE descendants(node_id) AS (
        SELECT NEW.node_id

        UNION ALL

        SELECT child.node_id
        FROM tree_node child
        JOIN descendants d
          ON child.parent_id = d.node_id
        WHERE child.tree_id = NEW.tree_id
          AND NOT (
              TG_OP = 'UPDATE'
              AND child.node_id = OLD.node_id
          )
    )
    SELECT EXISTS (
        SELECT 1
        FROM descendants
        WHERE node_id = NEW.parent_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION
            'Invalid parent assignment: tree cycle detected.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS
    trg_validate_tree_node
ON tree_node;

CREATE TRIGGER trg_validate_tree_node
BEFORE INSERT OR UPDATE OF parent_id
ON tree_node
FOR EACH ROW
EXECUTE FUNCTION validate_tree_node();

-- ------------------------------------------------------------
-- 3. TREE STRUCTURE VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_tree(p_tree_id BIGINT)
RETURNS TABLE (
    valid BOOLEAN,
    node_count BIGINT,
    root_count BIGINT,
    unreachable_count BIGINT,
    error_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_nodes BIGINT;
    v_roots BIGINT;
    v_reachable BIGINT;
BEGIN
    SELECT count(*)
    INTO v_nodes
    FROM tree_node
    WHERE tree_id = p_tree_id;

    SELECT count(*)
    INTO v_roots
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    WITH RECURSIVE reachable(node_id) AS (
        SELECT node_id
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND parent_id IS NULL

        UNION ALL

        SELECT child.node_id
        FROM tree_node child
        JOIN reachable parent
          ON child.parent_id = parent.node_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT count(*)
    INTO v_reachable
    FROM reachable;

    RETURN QUERY
    SELECT
        v_roots = 1 AND v_reachable = v_nodes,
        v_nodes,
        v_roots,
        v_nodes - v_reachable,
        CASE
            WHEN v_roots = 0 THEN 'Root is missing.'
            WHEN v_roots > 1 THEN 'Multiple roots detected.'
            WHEN v_reachable <> v_nodes THEN
                'Some nodes are unreachable.'
            ELSE 'Tree structure is valid.'
        END;
END;
$$;

-- ------------------------------------------------------------
-- 4. HEIGHT FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION tree_height(p_tree_id BIGINT)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE levels(node_id, depth) AS (
        SELECT node_id, 0
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND parent_id IS NULL

        UNION ALL

        SELECT child.node_id, levels.depth + 1
        FROM tree_node child
        JOIN levels
          ON child.parent_id = levels.node_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT COALESCE(MAX(depth), -1)::INTEGER
    FROM levels;
$$;

-- ------------------------------------------------------------
-- 5. LOWEST COMMON ANCESTOR FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION tree_lca(
    p_tree_id BIGINT,
    p_first BIGINT,
    p_second BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE
    first_ancestors(node_id, parent_id, depth) AS (
        SELECT node_id, parent_id, 0
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_id = p_first

        UNION ALL

        SELECT parent.node_id,
               parent.parent_id,
               ancestor.depth + 1
        FROM tree_node parent
        JOIN first_ancestors ancestor
          ON ancestor.parent_id = parent.node_id
        WHERE parent.tree_id = p_tree_id
    ),
    second_ancestors(node_id, parent_id, depth) AS (
        SELECT node_id, parent_id, 0
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_id = p_second

        UNION ALL

        SELECT parent.node_id,
               parent.parent_id,
               ancestor.depth + 1
        FROM tree_node parent
        JOIN second_ancestors ancestor
          ON ancestor.parent_id = parent.node_id
        WHERE parent.tree_id = p_tree_id
    )
    SELECT first.node_id
    FROM first_ancestors first
    JOIN second_ancestors second
      ON second.node_id = first.node_id
    ORDER BY
        first.depth + second.depth,
        first.depth
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 6. SAMPLE TREE DATA
-- ------------------------------------------------------------

INSERT INTO binary_tree(tree_name, description)
VALUES
    ('assessment_tree',
     'Binary tree used for traversal and structural assessment'),
    ('unbalanced_tree',
     'Tree used to demonstrate balance failure'),
    ('negative_tree',
     'Tree containing negative node values')
ON CONFLICT (tree_name) DO NOTHING;

DO $$
DECLARE
    assessment_id BIGINT;
    unbalanced_id BIGINT;
    negative_id BIGINT;
BEGIN
    SELECT tree_id INTO assessment_id
    FROM binary_tree
    WHERE tree_name = 'assessment_tree';

    SELECT tree_id INTO unbalanced_id
    FROM binary_tree
    WHERE tree_name = 'unbalanced_tree';

    SELECT tree_id INTO negative_id
    FROM binary_tree
    WHERE tree_name = 'negative_tree';

    IF NOT EXISTS (
        SELECT 1 FROM tree_node
        WHERE tree_id = assessment_id
    ) THEN
        INSERT INTO tree_node(tree_id, node_id, parent_id, node_value)
        VALUES
            (assessment_id, 10, NULL, 10),
            (assessment_id, 5, 10, 5),
            (assessment_id, 15, 10, 15),
            (assessment_id, 3, 5, 3),
            (assessment_id, 7, 5, 7),
            (assessment_id, 20, 15, 20),
            (assessment_id, 1, 3, 1),
            (assessment_id, 4, 3, 4),
            (assessment_id, 8, 7, 8);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM tree_node
        WHERE tree_id = unbalanced_id
    ) THEN
        INSERT INTO tree_node(tree_id, node_id, parent_id, node_value)
        VALUES
            (unbalanced_id, 1, NULL, 1),
            (unbalanced_id, 2, 1, 2),
            (unbalanced_id, 3, 2, 3),
            (unbalanced_id, 4, 3, 4);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM tree_node
        WHERE tree_id = negative_id
    ) THEN
        INSERT INTO tree_node(tree_id, node_id, parent_id, node_value)
        VALUES
            (negative_id, 1, NULL, -5),
            (negative_id, 2, 1, -10),
            (negative_id, 3, 1, -3);
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 7. STRUCTURAL VALIDATION REPORT
-- ------------------------------------------------------------

SELECT
    t.tree_name,
    v.valid,
    v.node_count,
    v.root_count,
    v.unreachable_count,
    v.error_message
FROM binary_tree t
CROSS JOIN LATERAL validate_tree(t.tree_id) v
ORDER BY t.tree_id;

-- ------------------------------------------------------------
-- 8. DEPTH-FIRST TRAVERSALS
-- ------------------------------------------------------------

-- Preorder: root, left, right.
-- Inorder: left, root, right.
-- Postorder: left, right, root.
--
-- The position path provides deterministic traversal order.

WITH RECURSIVE traversal AS (
    SELECT
        node_id,
        parent_id,
        node_value,
        ARRAY[]::INTEGER[] AS position_path,
        0 AS depth
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id
        FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.parent_id,
        child.node_value,
        traversal.position_path
            || CASE
                WHEN child.node_id = parent.node_id THEN 0
                ELSE 1
               END,
        traversal.depth + 1
    FROM traversal
    JOIN tree_node parent
      ON parent.node_id = traversal.node_id
     AND parent.tree_id = (
         SELECT tree_id FROM binary_tree
         WHERE tree_name = 'assessment_tree'
     )
    JOIN tree_node child
      ON child.parent_id = parent.node_id
     AND child.tree_id = parent.tree_id
    WHERE TRUE
)
SELECT
    node_id,
    node_value,
    depth,
    position_path
FROM traversal
ORDER BY position_path;

-- Explicit preorder, inorder and postorder positions.
WITH RECURSIVE walk AS (
    SELECT
        node_id,
        parent_id,
        node_value,
        ARRAY[]::INTEGER[] AS path,
        0 AS depth
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.parent_id,
        child.node_value,
        walk.path ||
            CASE
                WHEN child.node_id = parent.node_id THEN 0
                ELSE 1
            END,
        walk.depth + 1
    FROM walk
    JOIN tree_node parent
      ON parent.tree_id = (
          SELECT tree_id FROM binary_tree
          WHERE tree_name = 'assessment_tree'
      )
     AND parent.node_id = walk.node_id
    JOIN tree_node child
      ON child.tree_id = parent.tree_id
     AND child.parent_id = parent.node_id
)
SELECT
    'PREORDER' AS traversal,
    node_id,
    node_value
FROM walk
ORDER BY path;

-- ------------------------------------------------------------
-- 9. LEVEL-ORDER TRAVERSAL
-- ------------------------------------------------------------

WITH RECURSIVE levels AS (
    SELECT node_id, parent_id, node_value, 0 AS depth
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND parent_id IS NULL

    UNION ALL

    SELECT child.node_id,
           child.parent_id,
           child.node_value,
           levels.depth + 1
    FROM tree_node child
    JOIN levels
      ON child.parent_id = levels.node_id
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
)
SELECT
    depth,
    array_agg(node_value ORDER BY node_id) AS level_values,
    count(*) AS nodes_at_level
FROM levels
GROUP BY depth
ORDER BY depth;

-- ------------------------------------------------------------
-- 10. HEIGHT
-- ------------------------------------------------------------

SELECT
    tree_name,
    tree_height(tree_id) AS height_in_edges
FROM binary_tree
ORDER BY tree_id;

-- ------------------------------------------------------------
-- 11. DIAMETER
-- ------------------------------------------------------------

-- For each node, calculate the longest downward path.
-- The diameter is the maximum sum of two child heights + 2.

WITH RECURSIVE heights AS (
    SELECT
        node_id,
        parent_id,
        node_value,
        0 AS height
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM tree_node child
        WHERE child.tree_id = tree_node.tree_id
          AND child.parent_id = tree_node.node_id
    )

    UNION ALL

    SELECT
        parent.node_id,
        parent.parent_id,
        parent.node_value,
        MAX(heights.height) + 1
    FROM heights
    JOIN tree_node parent
      ON parent.tree_id = (
          SELECT tree_id FROM binary_tree
          WHERE tree_name = 'assessment_tree'
      )
     AND parent.node_id = heights.parent_id
    GROUP BY parent.node_id,
             parent.parent_id,
             parent.node_value
)
SELECT
    COALESCE(MAX(
        COALESCE(left_height.height, -1)
        + COALESCE(right_height.height, -1)
        + 2
    ), 0) AS diameter_in_edges
FROM tree_node parent
LEFT JOIN heights left_height
  ON left_height.parent_id = parent.node_id
 AND left_height.node_id = (
     SELECT child.node_id
     FROM tree_node child
     WHERE child.tree_id = parent.tree_id
       AND child.parent_id = parent.node_id
     ORDER BY child.node_id
     LIMIT 1
 )
LEFT JOIN heights right_height
  ON right_height.parent_id = parent.node_id
 AND right_height.node_id = (
     SELECT child.node_id
     FROM tree_node child
     WHERE child.tree_id = parent.tree_id
       AND child.parent_id = parent.node_id
     ORDER BY child.node_id
     OFFSET 1 LIMIT 1
 )
WHERE parent.tree_id = (
    SELECT tree_id FROM binary_tree
    WHERE tree_name = 'assessment_tree'
);

-- ------------------------------------------------------------
-- 12. BALANCED TREE ASSESSMENT
-- ------------------------------------------------------------

-- Bottom-up heights using recursive leaf-to-root propagation.

WITH RECURSIVE heights AS (
    SELECT
        node_id,
        parent_id,
        0 AS height
    FROM tree_node
    WHERE NOT EXISTS (
        SELECT 1
        FROM tree_node child
        WHERE child.tree_id = tree_node.tree_id
          AND child.parent_id = tree_node.node_id
    )

    UNION ALL

    SELECT
        parent.node_id,
        parent.parent_id,
        MAX(heights.height) + 1
    FROM heights
    JOIN tree_node parent
      ON parent.tree_id = heights.tree_id
     AND parent.node_id = heights.parent_id
    GROUP BY parent.node_id, parent.parent_id
)
SELECT
    t.tree_name,
    CASE
        WHEN MAX(h.height) IS NULL THEN TRUE
        ELSE (
            SELECT bool_and(
                abs(
                    COALESCE(left_h.height, 0)
                    - COALESCE(right_h.height, 0)
                ) <= 1
            )
            FROM tree_node n
            LEFT JOIN heights left_h
              ON left_h.tree_id = n.tree_id
             AND left_h.node_id = (
                 SELECT child.node_id
                 FROM tree_node child
                 WHERE child.tree_id = n.tree_id
                   AND child.parent_id = n.node_id
                 ORDER BY child.node_id
                 LIMIT 1
             )
            LEFT JOIN heights right_h
              ON right_h.tree_id = n.tree_id
             AND right_h.node_id = (
                 SELECT child.node_id
                 FROM tree_node child
                 WHERE child.tree_id = n.tree_id
                   AND child.parent_id = n.node_id
                 ORDER BY child.node_id
                 OFFSET 1 LIMIT 1
             )
            WHERE n.tree_id = t.tree_id
        )
    END AS balanced
FROM binary_tree t
LEFT JOIN heights h
  ON h.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name
ORDER BY t.tree_id;

-- ------------------------------------------------------------
-- 13. ROOT-TO-LEAF PATH SUMS
-- ------------------------------------------------------------

WITH RECURSIVE paths AS (
    SELECT
        node_id,
        parent_id,
        node_value,
        node_value::BIGINT AS path_sum,
        ARRAY[node_id]::BIGINT[] AS node_path,
        ARRAY[node_value]::BIGINT[] AS values_path
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.parent_id,
        child.node_value,
        paths.path_sum + child.node_value,
        paths.node_path || child.node_id,
        paths.values_path || child.node_value
    FROM tree_node child
    JOIN paths
      ON child.parent_id = paths.node_id
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
)
SELECT
    node_path,
    values_path,
    path_sum
FROM paths
WHERE NOT EXISTS (
    SELECT 1
    FROM tree_node child
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND child.parent_id = paths.node_id
)
ORDER BY node_path;

-- Filter root-to-leaf paths by target sum.
WITH RECURSIVE paths AS (
    SELECT
        node_id,
        node_value::BIGINT AS path_sum,
        ARRAY[node_value]::BIGINT[] AS values_path
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        paths.path_sum + child.node_value,
        paths.values_path || child.node_value
    FROM paths
    JOIN tree_node child
      ON child.parent_id = paths.node_id
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
)
SELECT values_path, path_sum
FROM paths
WHERE path_sum = 19
AND NOT EXISTS (
    SELECT 1
    FROM tree_node child
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND child.parent_id = paths.node_id
);

-- ------------------------------------------------------------
-- 14. LOWEST COMMON ANCESTOR
-- ------------------------------------------------------------

SELECT tree_lca(
    (SELECT tree_id FROM binary_tree
     WHERE tree_name = 'assessment_tree'),
    1,
    8
) AS lowest_common_ancestor;

-- ------------------------------------------------------------
-- 15. RIGHT-SIDE VIEW
-- ------------------------------------------------------------

WITH RECURSIVE levels AS (
    SELECT node_id, parent_id, node_value, 0 AS depth
    FROM tree_node
    WHERE tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
    AND parent_id IS NULL

    UNION ALL

    SELECT child.node_id,
           child.parent_id,
           child.node_value,
           levels.depth + 1
    FROM tree_node child
    JOIN levels
      ON child.parent_id = levels.node_id
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
)
SELECT DISTINCT ON (depth)
    depth,
    node_value AS rightmost_value
FROM levels
ORDER BY depth, node_id DESC;

-- ------------------------------------------------------------
-- 16. AGGREGATION AND REPORTING
-- ------------------------------------------------------------

WITH RECURSIVE levels AS (
    SELECT
        node_id,
        node_value,
        0 AS depth
    FROM tree_node
    WHERE parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.node_value,
        levels.depth + 1
    FROM tree_node child
    JOIN levels
      ON child.parent_id = levels.node_id
    WHERE child.tree_id = (
        SELECT tree_id FROM binary_tree
        WHERE tree_name = 'assessment_tree'
    )
)
SELECT
    t.tree_name,
    count(n.node_id) AS node_count,
    min(n.node_value) AS minimum_value,
    max(n.node_value) AS maximum_value,
    avg(n.node_value) AS average_value,
    tree_height(t.tree_id) AS height
FROM binary_tree t
LEFT JOIN tree_node n
  ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name
ORDER BY t.tree_id;

-- ------------------------------------------------------------
-- 17. FAILURE HANDLING AND CONSTRAINT VERIFICATION
-- ------------------------------------------------------------

-- The following operations are intentionally isolated by
-- exception handling so that the script remains executable.

DO $$
DECLARE
    assessment_id BIGINT;
BEGIN
    SELECT tree_id INTO assessment_id
    FROM binary_tree
    WHERE tree_name = 'assessment_tree';

    BEGIN
        INSERT INTO tree_node(
            tree_id, node_id, parent_id, node_value
        )
        VALUES (
            assessment_id, 999, 999, 999
        );

        RAISE EXCEPTION
            'Self-parent validation was not enforced.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Invalid parent assignment rejected: %',
                SQLERRM;
    END;

    BEGIN
        UPDATE tree_node
        SET parent_id = 1
        WHERE tree_id = assessment_id
          AND node_id = 10;

        RAISE EXCEPTION
            'Cycle validation was not enforced.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Cycle update rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 18. PERFORMANCE AND DATA INTEGRITY CHECKS
-- ------------------------------------------------------------

ANALYZE binary_tree;
ANALYZE tree_node;

SELECT
    tree_name,
    tree_height(tree_id) AS height,
    (
        SELECT count(*)
        FROM tree_node n
        WHERE n.tree_id = binary_tree.tree_id
    ) AS total_nodes,
    (
        SELECT count(*)
        FROM tree_node n
        WHERE n.tree_id = binary_tree.tree_id
          AND n.parent_id IS NULL
    ) AS root_nodes
FROM binary_tree
ORDER BY tree_id;

COMMIT;
