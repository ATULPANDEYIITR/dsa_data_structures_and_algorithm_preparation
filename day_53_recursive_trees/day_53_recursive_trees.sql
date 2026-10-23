DROP SCHEMA IF EXISTS recursive_trees CASCADE;
CREATE SCHEMA recursive_trees;
SET search_path TO recursive_trees;

-- The relational model stores the actual recursion-tree nodes.
-- parent_id represents the recursive caller -> recursive child relationship.
CREATE TABLE recursion_trees (
    tree_id BIGSERIAL PRIMARY KEY,
    tree_type TEXT NOT NULL CHECK (
        tree_type IN (
            'fibonacci',
            'subsets',
            'binary_choice',
            'divide_and_conquer'
        )
    ),
    input_description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recursion_nodes (
    node_id BIGSERIAL PRIMARY KEY,
    tree_id BIGINT NOT NULL
        REFERENCES recursion_trees(tree_id)
        ON DELETE CASCADE,
    parent_id BIGINT REFERENCES recursion_nodes(node_id)
        ON DELETE CASCADE,
    depth INTEGER NOT NULL CHECK (depth >= 0),
    node_label TEXT NOT NULL,
    branch_label TEXT,
    child_order INTEGER NOT NULL CHECK (child_order >= 0),
    CHECK (parent_id IS NULL OR child_order >= 0)
);

CREATE INDEX idx_recursion_nodes_tree_depth
    ON recursion_nodes(tree_id, depth);

CREATE INDEX idx_recursion_nodes_parent
    ON recursion_nodes(parent_id);

CREATE TABLE recursion_examples (
    example_id BIGSERIAL PRIMARY KEY,
    tree_id BIGINT NOT NULL
        REFERENCES recursion_trees(tree_id)
        ON DELETE CASCADE,
    expected_leaf_count BIGINT NOT NULL CHECK (expected_leaf_count >= 1),
    expected_growth_class TEXT NOT NULL,
    notes TEXT NOT NULL
);

-- Generic tree insertion function. Recursive children are inserted
-- through the parent_id relationship.
CREATE OR REPLACE FUNCTION add_recursion_node(
    p_tree_id BIGINT,
    p_parent_id BIGINT,
    p_depth INTEGER,
    p_label TEXT,
    p_branch TEXT,
    p_child_order INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_node_id BIGINT;
BEGIN
    IF p_depth < 0 THEN
        RAISE EXCEPTION 'Depth cannot be negative';
    END IF;

    IF p_child_order < 0 THEN
        RAISE EXCEPTION 'Child order cannot be negative';
    END IF;

    INSERT INTO recursion_nodes (
        tree_id,
        parent_id,
        depth,
        node_label,
        branch_label,
        child_order
    )
    VALUES (
        p_tree_id,
        p_parent_id,
        p_depth,
        p_label,
        p_branch,
        p_child_order
    )
    RETURNING node_id INTO new_node_id;

    RETURN new_node_id;
END;
$$;

-- Fibonacci: F(5) produces a branching recursion tree.
INSERT INTO recursion_trees (
    tree_type,
    input_description
)
VALUES (
    'fibonacci',
    'fib(5)'
);

-- Subsets: each item produces exclude/include branches.
INSERT INTO recursion_trees (
    tree_type,
    input_description
)
VALUES (
    'subsets',
    'subsets of {A,B,C}'
);

-- Binary choices: three binary decisions create 2^3 leaves.
INSERT INTO recursion_trees (
    tree_type,
    input_description
)
VALUES (
    'binary_choice',
    'three binary decisions'
);

-- Merge sort: every non-singleton input is divided into two halves.
INSERT INTO recursion_trees (
    tree_type,
    input_description
)
VALUES (
    'divide_and_conquer',
    'merge sort of [8,3,7,4,2,6]'
);

INSERT INTO recursion_examples (
    tree_id,
    expected_leaf_count,
    expected_growth_class,
    notes
)
SELECT tree_id, 8, 'exponential', 'Three independent include/exclude decisions.'
FROM recursion_trees
WHERE tree_type = 'subsets';

INSERT INTO recursion_examples (
    tree_id,
    expected_leaf_count,
    expected_growth_class,
    notes
)
SELECT tree_id, 8, 'exponential', 'Three binary choices produce eight outcomes.'
FROM recursion_trees
WHERE tree_type = 'binary_choice';

INSERT INTO recursion_examples (
    tree_id,
    expected_leaf_count,
    expected_growth_class,
    notes
)
SELECT tree_id, 6, 'linear-leaf / logarithmic-depth',
       'Merge sort reaches six singleton input leaves.'
FROM recursion_trees
WHERE tree_type = 'divide_and_conquer';

INSERT INTO recursion_examples (
    tree_id,
    expected_leaf_count,
    expected_growth_class,
    notes
)
SELECT tree_id, 8, 'exponential',
       'Naive Fibonacci repeatedly recomputes overlapping subproblems.'
FROM recursion_trees
WHERE tree_type = 'fibonacci';

-- Populate a small Fibonacci tree using the database function.
DO $$
DECLARE
    tree BIGINT;
    root BIGINT;
    fib5 BIGINT;
    fib4 BIGINT;
    fib3a BIGINT;
    fib3b BIGINT;
    fib2a BIGINT;
    fib2b BIGINT;
BEGIN
    SELECT tree_id
    INTO tree
    FROM recursion_trees
    WHERE tree_type = 'fibonacci';

    root := add_recursion_node(
        tree, NULL, 0, 'fib(5)', NULL, 0
    );

    fib5 := add_recursion_node(
        tree, root, 1, 'fib(4)', 'n-1', 0
    );

    PERFORM add_recursion_node(
        tree, root, 1, 'fib(3)', 'n-2', 1
    );

    fib4 := fib5;

    fib3a := add_recursion_node(
        tree, fib4, 2, 'fib(3)', 'n-1', 0
    );

    PERFORM add_recursion_node(
        tree, fib4, 2, 'fib(2)', 'n-2', 1
    );

    fib3b := fib3a;

    fib2a := add_recursion_node(
        tree, fib3b, 3, 'fib(2)', 'n-1', 0
    );

    PERFORM add_recursion_node(
        tree, fib3b, 3, 'fib(1)', 'n-2', 1
    );

    fib2b := fib2a;

    PERFORM add_recursion_node(
        tree, fib2b, 4, 'fib(1)', 'n-1', 0
    );

    PERFORM add_recursion_node(
        tree, fib2b, 4, 'fib(0)', 'n-2', 1
    );
END;
$$;

-- Populate a complete binary-choice tree of depth three.
DO $$
DECLARE
    tree BIGINT;
    root BIGINT;
    level_one_zero BIGINT;
    level_one_one BIGINT;
    node_id BIGINT;
BEGIN
    SELECT tree_id
    INTO tree
    FROM recursion_trees
    WHERE tree_type = 'binary_choice';

    root := add_recursion_node(
        tree, NULL, 0, 'level 0: empty', NULL, 0
    );

    level_one_zero := add_recursion_node(
        tree, root, 1, 'choice 0', '0', 0
    );

    level_one_one := add_recursion_node(
        tree, root, 1, 'choice 1', '1', 1
    );

    FOR node_id IN
        SELECT add_recursion_node(
            tree,
            level_one_zero,
            2,
            'choice 00',
            '0',
            0
        )
    LOOP
        PERFORM add_recursion_node(
            tree, node_id, 3, 'choice 000', '0', 0
        );
        PERFORM add_recursion_node(
            tree, node_id, 3, 'choice 001', '1', 1
        );
    END LOOP;

    PERFORM add_recursion_node(
        tree, level_one_zero, 2, 'choice 01', '1', 1
    );

    PERFORM add_recursion_node(
        tree,
        level_one_one,
        2,
        'choice 10',
        '0',
        0
    );

    PERFORM add_recursion_node(
        tree,
        level_one_one,
        2,
        'choice 11',
        '1',
        1
    );
END;
$$;

-- A recursive CTE is the natural SQL equivalent of walking a tree.
CREATE OR REPLACE VIEW recursion_tree_report AS
WITH RECURSIVE tree_walk AS (
    SELECT
        n.node_id,
        n.tree_id,
        n.parent_id,
        n.depth,
        n.node_label,
        n.branch_label,
        n.child_order,
        n.node_label::TEXT AS path
    FROM recursion_nodes n
    WHERE n.parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.tree_id,
        child.parent_id,
        child.depth,
        child.node_label,
        child.branch_label,
        child.child_order,
        tree_walk.path || ' -> ' || child.node_label
    FROM recursion_nodes child
    JOIN tree_walk
      ON child.parent_id = tree_walk.node_id
)
SELECT
    tree_walk.tree_id,
    t.tree_type,
    t.input_description,
    tree_walk.node_id,
    tree_walk.parent_id,
    tree_walk.depth,
    tree_walk.node_label,
    tree_walk.branch_label,
    tree_walk.child_order,
    tree_walk.path
FROM tree_walk
JOIN recursion_trees t
  ON t.tree_id = tree_walk.tree_id;

-- Inspect every recursion tree in depth-first structural order.
SELECT
    tree_type,
    depth,
    repeat('  ', depth) || node_label AS visual_node,
    path
FROM recursion_tree_report
ORDER BY tree_id, path;

-- Count recursive calls represented by each stored tree.
SELECT
    t.tree_type,
    COUNT(n.node_id) AS recursive_calls,
    MAX(n.depth) + 1 AS tree_levels
FROM recursion_trees t
LEFT JOIN recursion_nodes n
  ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_type
ORDER BY t.tree_id;

-- Identify leaf nodes. A leaf represents a base case or completed choice.
SELECT
    r.tree_type,
    COUNT(*) AS leaf_count
FROM recursion_tree_report r
WHERE NOT EXISTS (
    SELECT 1
    FROM recursion_nodes child
    WHERE child.parent_id = r.node_id
)
GROUP BY r.tree_type
ORDER BY r.tree_type;

-- Compare branching behavior.
SELECT
    t.tree_type,
    n.depth,
    COUNT(*) AS nodes_at_depth
FROM recursion_nodes n
JOIN recursion_trees t
  ON t.tree_id = n.tree_id
GROUP BY t.tree_type, n.depth
ORDER BY t.tree_type, n.depth;

-- Transactional validation example:
-- an invalid negative depth is rejected by the CHECK constraint.
BEGIN;

DO $$
BEGIN
    BEGIN
        PERFORM add_recursion_node(
            (SELECT tree_id
             FROM recursion_trees
             WHERE tree_type = 'subsets'),
            NULL,
            -1,
            'invalid node',
            NULL,
            0
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected validation failure: %', SQLERRM;
    END;
END;
$$;

ROLLBACK;

-- Recursive CTE aggregation gives the number of nodes reachable
-- from each root without requiring procedural tree traversal.
WITH RECURSIVE descendants AS (
    SELECT
        node_id,
        tree_id,
        node_id AS root_id
    FROM recursion_nodes
    WHERE parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.tree_id,
        descendants.root_id
    FROM recursion_nodes child
    JOIN descendants
      ON child.parent_id = descendants.node_id
)
SELECT
    t.tree_type,
    d.root_id,
    COUNT(*) AS reachable_nodes
FROM descendants d
JOIN recursion_trees t
  ON t.tree_id = d.tree_id
GROUP BY t.tree_type, d.root_id
ORDER BY t.tree_type;
