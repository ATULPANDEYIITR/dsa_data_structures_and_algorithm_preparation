DROP SCHEMA IF EXISTS tree_analysis CASCADE;
CREATE SCHEMA tree_analysis;

SET search_path TO tree_analysis, public;

CREATE TABLE binary_trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(tree_name)) BETWEEN 1 AND 100)
);

CREATE TABLE tree_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id BIGINT NOT NULL REFERENCES binary_trees(tree_id) ON DELETE CASCADE,
    parent_node_id BIGINT REFERENCES tree_nodes(node_id) ON DELETE CASCADE,
    node_value INTEGER NOT NULL,
    child_position CHAR(1),
    CHECK (child_position IN ('L', 'R') OR child_position IS NULL),
    UNIQUE (tree_id, node_id)
);

CREATE UNIQUE INDEX one_left_child_per_parent
ON tree_nodes(tree_id, parent_node_id)
WHERE child_position = 'L';

CREATE UNIQUE INDEX one_right_child_per_parent
ON tree_nodes(tree_id, parent_node_id)
WHERE child_position = 'R';

CREATE UNIQUE INDEX one_root_per_tree
ON tree_nodes(tree_id)
WHERE parent_node_id IS NULL;

CREATE INDEX tree_nodes_parent_idx
ON tree_nodes(tree_id, parent_node_id);

CREATE TABLE tree_metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id BIGINT NOT NULL REFERENCES binary_trees(tree_id) ON DELETE CASCADE,
    maximum_depth INTEGER NOT NULL CHECK (maximum_depth >= 0),
    minimum_depth INTEGER NOT NULL CHECK (minimum_depth >= 0),
    leaf_count INTEGER NOT NULL CHECK (leaf_count >= 0),
    balanced BOOLEAN NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tree_id)
);

CREATE OR REPLACE FUNCTION validate_tree_node_relationship()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_tree_id BIGINT;
BEGIN
    IF NEW.parent_node_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT tree_id
    INTO parent_tree_id
    FROM tree_nodes
    WHERE node_id = NEW.parent_node_id;

    IF parent_tree_id IS NULL THEN
        RAISE EXCEPTION 'Parent node % does not exist', NEW.parent_node_id;
    END IF;

    IF parent_tree_id <> NEW.tree_id THEN
        RAISE EXCEPTION
            'Parent node % belongs to tree %, not tree %',
            NEW.parent_node_id,
            parent_tree_id,
            NEW.tree_id;
    END IF;

    IF NEW.parent_node_id = NEW.node_id THEN
        RAISE EXCEPTION 'A node cannot be its own parent';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER tree_node_relationship_trigger
BEFORE INSERT OR UPDATE ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION validate_tree_node_relationship();

CREATE OR REPLACE FUNCTION calculate_tree_metrics(p_tree_id BIGINT)
RETURNS TABLE (
    maximum_depth INTEGER,
    minimum_depth INTEGER,
    leaf_count INTEGER,
    balanced BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    root_id BIGINT;
BEGIN
    SELECT node_id
    INTO root_id
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_node_id IS NULL;

    IF root_id IS NULL THEN
        RETURN QUERY
        SELECT 0, 0, 0, TRUE;
        RETURN;
    END IF;

    RETURN QUERY
    WITH RECURSIVE tree_walk AS (
        SELECT
            n.node_id,
            n.parent_node_id,
            n.node_value,
            1 AS depth
        FROM tree_nodes n
        WHERE n.node_id = root_id

        UNION ALL

        SELECT
            child.node_id,
            child.parent_node_id,
            child.node_value,
            parent.depth + 1
        FROM tree_walk parent
        JOIN tree_nodes child
          ON child.parent_node_id = parent.node_id
         AND child.tree_id = p_tree_id
    ),
    children AS (
        SELECT
            tw.node_id,
            tw.depth,
            COUNT(child.node_id)::INTEGER AS child_count
        FROM tree_walk tw
        LEFT JOIN tree_nodes child
          ON child.parent_node_id = tw.node_id
         AND child.tree_id = p_tree_id
        GROUP BY tw.node_id, tw.depth
    ),
    leaf_depths AS (
        SELECT depth
        FROM children
        WHERE child_count = 0
    ),
    subtree_heights AS (
        SELECT
            tw.node_id,
            tw.depth,
            COALESCE(
                MAX(descendant.depth) - tw.depth + 1,
                1
            )::INTEGER AS height
        FROM tree_walk tw
        LEFT JOIN tree_walk descendant
          ON descendant.node_id = tw.node_id
          OR descendant.parent_node_id = tw.node_id
        GROUP BY tw.node_id, tw.depth
    )
    SELECT
        (SELECT MAX(depth)::INTEGER FROM tree_walk),
        (SELECT MIN(depth)::INTEGER FROM leaf_depths),
        (SELECT COUNT(*)::INTEGER FROM leaf_depths),
        TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION refresh_tree_metrics(p_tree_id BIGINT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    metrics RECORD;
BEGIN
    SELECT *
    INTO metrics
    FROM calculate_tree_metrics(p_tree_id);

    INSERT INTO tree_metrics (
        tree_id,
        maximum_depth,
        minimum_depth,
        leaf_count,
        balanced
    )
    VALUES (
        p_tree_id,
        metrics.maximum_depth,
        metrics.minimum_depth,
        metrics.leaf_count,
        metrics.balanced
    )
    ON CONFLICT (tree_id)
    DO UPDATE SET
        maximum_depth = EXCLUDED.maximum_depth,
        minimum_depth = EXCLUDED.minimum_depth,
        leaf_count = EXCLUDED.leaf_count,
        balanced = EXCLUDED.balanced,
        calculated_at = CURRENT_TIMESTAMP;
END;
$$;

INSERT INTO binary_trees (tree_name, description)
VALUES
    ('balanced_example', 'Balanced binary tree'),
    ('unbalanced_example', 'Tree with excessive height on one side'),
    ('single_node', 'Single-node tree'),
    ('skewed_example', 'Mostly one-sided tree'),
    ('empty_example', 'Tree with no nodes');

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT tree_id, NULL, 3, NULL
FROM binary_trees
WHERE tree_name = 'balanced_example';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT tree_id, root.node_id, child.value, child.position
FROM binary_trees t
JOIN tree_nodes root
  ON root.tree_id = t.tree_id
 AND root.parent_node_id IS NULL
CROSS JOIN (
    VALUES
        (9, 'L'::CHAR(1)),
        (20, 'R'::CHAR(1))
) AS child(value, position)
WHERE t.tree_name = 'balanced_example';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, child.value, child.position
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
CROSS JOIN (
    VALUES
        (15, 'L'::CHAR(1)),
        (7, 'R'::CHAR(1))
) AS child(value, position)
WHERE t.tree_name = 'balanced_example'
  AND parent.node_value = 20;

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT tree_id, NULL, 1, NULL
FROM binary_trees
WHERE tree_name = 'unbalanced_example';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, root.node_id, 2, 'L'
FROM binary_trees t
JOIN tree_nodes root
  ON root.tree_id = t.tree_id
 AND root.parent_node_id IS NULL
WHERE t.tree_name = 'unbalanced_example';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, 2, 'R'
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
WHERE t.tree_name = 'unbalanced_example'
  AND parent.node_value = 1;

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, child.value, child.position
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
CROSS JOIN (
    VALUES
        (3, 'L'::CHAR(1)),
        (3, 'R'::CHAR(1))
) AS child(value, position)
WHERE t.tree_name = 'unbalanced_example'
  AND parent.node_value = 2
  AND parent.child_position = 'L';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, child.value, child.position
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
CROSS JOIN (
    VALUES
        (4, 'L'::CHAR(1)),
        (4, 'R'::CHAR(1))
) AS child(value, position)
WHERE t.tree_name = 'unbalanced_example'
  AND parent.node_value = 3
  AND parent.child_position = 'L';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT tree_id, NULL, 42, NULL
FROM binary_trees
WHERE tree_name = 'single_node';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT tree_id, NULL, 1, NULL
FROM binary_trees
WHERE tree_name = 'skewed_example';

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, 2, 'L'
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
WHERE t.tree_name = 'skewed_example'
  AND parent.parent_node_id IS NULL;

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, 3, 'L'
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
WHERE t.tree_name = 'skewed_example'
  AND parent.node_value = 2;

INSERT INTO tree_nodes (tree_id, parent_node_id, node_value, child_position)
SELECT t.tree_id, parent.node_id, 4, 'L'
FROM binary_trees t
JOIN tree_nodes parent
  ON parent.tree_id = t.tree_id
WHERE t.tree_name = 'skewed_example'
  AND parent.node_value = 3;

DO $$
DECLARE
    tree RECORD;
BEGIN
    FOR tree IN SELECT tree_id FROM binary_trees LOOP
        PERFORM refresh_tree_metrics(tree.tree_id);
    END LOOP;
END;
$$;

CREATE OR REPLACE VIEW tree_analysis_report AS
SELECT
    t.tree_id,
    t.tree_name,
    t.description,
    COALESCE(m.maximum_depth, 0) AS maximum_depth,
    COALESCE(m.minimum_depth, 0) AS minimum_depth,
    COALESCE(m.leaf_count, 0) AS leaf_count,
    COALESCE(m.balanced, TRUE) AS balanced,
    m.calculated_at
FROM binary_trees t
LEFT JOIN tree_metrics m
    ON m.tree_id = t.tree_id;

-- Retrieval and reporting.
SELECT *
FROM tree_analysis_report
ORDER BY tree_id;

-- Leaf-level validation.
SELECT
    t.tree_name,
    n.node_id,
    n.node_value
FROM binary_trees t
JOIN tree_nodes n
  ON n.tree_id = t.tree_id
LEFT JOIN tree_nodes child
  ON child.parent_node_id = n.node_id
 AND child.tree_id = n.tree_id
WHERE child.node_id IS NULL
ORDER BY t.tree_name, n.node_id;

-- Aggregation by balance state.
SELECT
    balanced,
    COUNT(*) AS tree_count,
    AVG(maximum_depth)::NUMERIC(10,2) AS average_maximum_depth,
    SUM(leaf_count) AS total_leaves
FROM tree_analysis_report
GROUP BY balanced
ORDER BY balanced DESC;

-- Workflow-style evaluation of tree quality.
SELECT
    tree_name,
    maximum_depth,
    minimum_depth,
    leaf_count,
    balanced,
    CASE
        WHEN maximum_depth = 0 THEN 'EMPTY'
        WHEN balanced AND maximum_depth <= 4 THEN 'HEALTHY'
        WHEN balanced THEN 'BALANCED_DEEP'
        ELSE 'UNBALANCED'
    END AS evaluation
FROM tree_analysis_report
ORDER BY tree_id;

-- Transactional metric refresh after a controlled node insertion.
BEGIN;

WITH target AS (
    SELECT tree_id
    FROM binary_trees
    WHERE tree_name = 'single_node'
)
INSERT INTO tree_nodes (
    tree_id,
    parent_node_id,
    node_value,
    child_position
)
SELECT
    target.tree_id,
    root.node_id,
    21,
    'L'
FROM target
JOIN tree_nodes root
  ON root.tree_id = target.tree_id
 AND root.parent_node_id IS NULL;

SELECT refresh_tree_metrics(tree_id)
FROM binary_trees
WHERE tree_name = 'single_node';

COMMIT;

SELECT *
FROM tree_analysis_report
WHERE tree_name = 'single_node';

-- The following validation query identifies any node that violates
-- the binary-tree child-count invariant.
SELECT
    tree_id,
    parent_node_id,
    COUNT(*) AS child_count
FROM tree_nodes
WHERE parent_node_id IS NOT NULL
GROUP BY tree_id, parent_node_id
HAVING COUNT(*) > 2;

-- The following query identifies trees without a root.
SELECT
    t.tree_id,
    t.tree_name
FROM binary_trees t
LEFT JOIN tree_nodes n
  ON n.tree_id = t.tree_id
 AND n.parent_node_id IS NULL
WHERE n.node_id IS NULL
  AND EXISTS (
      SELECT 1
      FROM tree_nodes child
      WHERE child.tree_id = t.tree_id
  )
ORDER BY t.tree_id;
