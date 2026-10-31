DROP SCHEMA IF EXISTS dfs_traversal CASCADE;
CREATE SCHEMA dfs_traversal;

SET search_path = dfs_traversal, public;

CREATE TABLE tree (
    tree_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tree_node (
    node_id BIGSERIAL PRIMARY KEY,
    tree_id BIGINT NOT NULL REFERENCES tree(tree_id) ON DELETE CASCADE,
    value INTEGER NOT NULL,
    left_node_id BIGINT REFERENCES tree_node(node_id) ON DELETE RESTRICT,
    right_node_id BIGINT REFERENCES tree_node(node_id) ON DELETE RESTRICT,
    UNIQUE (tree_id, node_id)
);

CREATE INDEX idx_tree_node_tree
    ON tree_node(tree_id);

CREATE INDEX idx_tree_node_children
    ON tree_node(left_node_id, right_node_id);

CREATE TABLE traversal_run (
    traversal_id BIGSERIAL PRIMARY KEY,
    tree_id BIGINT NOT NULL REFERENCES tree(tree_id) ON DELETE CASCADE,
    traversal_type TEXT NOT NULL CHECK (
        traversal_type IN ('PREORDER', 'INORDER', 'POSTORDER')
    ),
    implementation TEXT NOT NULL CHECK (
        implementation IN ('RECURSIVE', 'ITERATIVE')
    ),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'RUNNING' CHECK (
        status IN ('RUNNING', 'COMPLETED', 'FAILED')
    )
);

CREATE TABLE traversal_result (
    traversal_id BIGINT NOT NULL
        REFERENCES traversal_run(traversal_id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    node_id BIGINT NOT NULL REFERENCES tree_node(node_id) ON DELETE RESTRICT,
    node_value INTEGER NOT NULL,
    PRIMARY KEY (traversal_id, position)
);

CREATE OR REPLACE FUNCTION validate_node_tree_consistency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    left_tree BIGINT;
    right_tree BIGINT;
BEGIN
    IF NEW.left_node_id IS NOT NULL THEN
        SELECT tree_id
        INTO left_tree
        FROM tree_node
        WHERE node_id = NEW.left_node_id;

        IF left_tree IS NULL OR left_tree <> NEW.tree_id THEN
            RAISE EXCEPTION
                'Left child % must belong to tree %',
                NEW.left_node_id, NEW.tree_id;
        END IF;

        IF NEW.left_node_id = NEW.node_id THEN
            RAISE EXCEPTION 'A node cannot be its own left child';
        END IF;
    END IF;

    IF NEW.right_node_id IS NOT NULL THEN
        SELECT tree_id
        INTO right_tree
        FROM tree_node
        WHERE node_id = NEW.right_node_id;

        IF right_tree IS NULL OR right_tree <> NEW.tree_id THEN
            RAISE EXCEPTION
                'Right child % must belong to tree %',
                NEW.right_node_id, NEW.tree_id;
        END IF;

        IF NEW.right_node_id = NEW.node_id THEN
            RAISE EXCEPTION 'A node cannot be its own right child';
        END IF;
    END IF;

    IF NEW.left_node_id IS NOT NULL
       AND NEW.left_node_id = NEW.right_node_id THEN
        RAISE EXCEPTION 'Left and right child cannot be the same node';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_node_tree
BEFORE INSERT OR UPDATE OF tree_id, left_node_id, right_node_id
ON tree_node
FOR EACH ROW
EXECUTE FUNCTION validate_node_tree_consistency();

CREATE OR REPLACE FUNCTION validate_tree_structure(p_tree_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    root_count INTEGER;
    node_count INTEGER;
    reachable_count INTEGER;
BEGIN
    /*
     * A root is a node that is never referenced as a child.
     * A valid non-empty binary tree has exactly one root.
     */
    SELECT COUNT(*)
    INTO root_count
    FROM tree_node n
    WHERE n.tree_id = p_tree_id
      AND NOT EXISTS (
          SELECT 1
          FROM tree_node parent
          WHERE parent.tree_id = p_tree_id
            AND (
                parent.left_node_id = n.node_id
                OR parent.right_node_id = n.node_id
            )
      );

    SELECT COUNT(*)
    INTO node_count
    FROM tree_node
    WHERE tree_id = p_tree_id;

    IF node_count = 0 THEN
        RETURN TRUE;
    END IF;

    IF root_count <> 1 THEN
        RETURN FALSE;
    END IF;

    /*
     * Recursive reachability detects disconnected components and,
     * because recursive CTEs use UNION rather than UNION ALL here,
     * terminates when a node has already been reached.
     */
    WITH RECURSIVE roots AS (
        SELECT n.node_id
        FROM tree_node n
        WHERE n.tree_id = p_tree_id
          AND NOT EXISTS (
              SELECT 1
              FROM tree_node parent
              WHERE parent.tree_id = p_tree_id
                AND (
                    parent.left_node_id = n.node_id
                    OR parent.right_node_id = n.node_id
                )
          )
    ),
    reachable(node_id) AS (
        SELECT node_id
        FROM roots

        UNION

        SELECT child_id
        FROM (
            SELECT r.node_id, n.left_node_id AS child_id
            FROM reachable r
            JOIN tree_node n ON n.node_id = r.node_id
            WHERE n.left_node_id IS NOT NULL

            UNION

            SELECT r.node_id, n.right_node_id
            FROM reachable r
            JOIN tree_node n ON n.node_id = r.node_id
            WHERE n.right_node_id IS NOT NULL
        ) children
    )
    SELECT COUNT(DISTINCT node_id)
    INTO reachable_count
    FROM reachable;

    RETURN reachable_count = node_count;
END;
$$;

CREATE OR REPLACE FUNCTION record_dfs_traversal(
    p_tree_id BIGINT,
    p_type TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_traversal_id BIGINT;
BEGIN
    IF p_type NOT IN ('PREORDER', 'INORDER', 'POSTORDER') THEN
        RAISE EXCEPTION 'Unsupported traversal type: %', p_type;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM tree
        WHERE tree_id = p_tree_id
    ) THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    IF NOT validate_tree_structure(p_tree_id) THEN
        RAISE EXCEPTION 'Tree % is not a valid connected binary tree',
            p_tree_id;
    END IF;

    INSERT INTO traversal_run (
        tree_id,
        traversal_type,
        implementation,
        status
    )
    VALUES (
        p_tree_id,
        p_type,
        'ITERATIVE',
        'RUNNING'
    )
    RETURNING traversal_id INTO v_traversal_id;

    /*
     * PostgreSQL's recursive CTE can construct a root-to-node path.
     * Ordering by the path gives a deterministic depth-first ordering.
     * The path includes node IDs rather than values so duplicate values
     * do not affect traversal order.
     */
    IF p_type = 'PREORDER' THEN
        INSERT INTO traversal_result (
            traversal_id,
            position,
            node_id,
            node_value
        )
        WITH RECURSIVE walk AS (
            SELECT
                n.node_id,
                n.value,
                ARRAY[n.node_id]::BIGINT[] AS path
            FROM tree_node n
            WHERE n.tree_id = p_tree_id
              AND NOT EXISTS (
                  SELECT 1
                  FROM tree_node p
                  WHERE p.tree_id = p_tree_id
                    AND (
                        p.left_node_id = n.node_id
                        OR p.right_node_id = n.node_id
                    )
              )

            UNION ALL

            SELECT
                c.node_id,
                c.value,
                w.path || c.node_id
            FROM walk w
            JOIN tree_node parent ON parent.node_id = w.node_id
            CROSS JOIN LATERAL (
                VALUES
                    (parent.left_node_id),
                    (parent.right_node_id)
            ) AS child(child_id)
            JOIN tree_node c ON c.node_id = child.child_id
            WHERE NOT c.node_id = ANY(w.path)
        )
        SELECT
            v_traversal_id,
            ROW_NUMBER() OVER (ORDER BY path)::INTEGER - 1,
            node_id,
            value
        FROM walk;

    ELSIF p_type = 'INORDER' THEN
        /*
         * Each node receives a sortable positional key derived from the
         * path. PostgreSQL arrays compare lexicographically, so a binary
         * encoding distinguishes left, root, and right placement.
         */
        INSERT INTO traversal_result (
            traversal_id,
            position,
            node_id,
            node_value
        )
        WITH RECURSIVE walk AS (
            SELECT
                n.node_id,
                n.value,
                ARRAY[1::INTEGER] AS path
            FROM tree_node n
            WHERE n.tree_id = p_tree_id
              AND NOT EXISTS (
                  SELECT 1
                  FROM tree_node p
                  WHERE p.tree_id = p_tree_id
                    AND (
                        p.left_node_id = n.node_id
                        OR p.right_node_id = n.node_id
                    )
              )

            UNION ALL

            SELECT
                c.node_id,
                c.value,
                CASE
                    WHEN c.node_id = parent.left_node_id
                        THEN w.path || 0
                    ELSE w.path || 2
                END
            FROM walk w
            JOIN tree_node parent ON parent.node_id = w.node_id
            JOIN tree_node c
              ON c.node_id = parent.left_node_id
              OR c.node_id = parent.right_node_id
            WHERE NOT c.node_id = ANY(
                ARRAY(
                    SELECT node_id
                    FROM walk
                    WHERE false
                )
            )
        ),
        ordered AS (
            SELECT
                node_id,
                value,
                path
            FROM walk
        )
        SELECT
            v_traversal_id,
            ROW_NUMBER() OVER (ORDER BY path)::INTEGER - 1,
            node_id,
            value
        FROM ordered;
    ELSE
        /*
         * Postorder is represented with a recursive path and reversed
         * depth-first ordering. This SQL model is intended as a relational
         * workflow representation rather than a replacement for a native
         * in-memory traversal implementation.
         */
        INSERT INTO traversal_result (
            traversal_id,
            position,
            node_id,
            node_value
        )
        WITH RECURSIVE walk AS (
            SELECT
                n.node_id,
                n.value,
                ARRAY[n.node_id]::BIGINT[] AS path
            FROM tree_node n
            WHERE n.tree_id = p_tree_id
              AND NOT EXISTS (
                  SELECT 1
                  FROM tree_node p
                  WHERE p.tree_id = p_tree_id
                    AND (
                        p.left_node_id = n.node_id
                        OR p.right_node_id = n.node_id
                    )
              )

            UNION ALL

            SELECT
                c.node_id,
                c.value,
                w.path || c.node_id
            FROM walk w
            JOIN tree_node parent ON parent.node_id = w.node_id
            JOIN tree_node c
              ON c.node_id = parent.left_node_id
              OR c.node_id = parent.right_node_id
            WHERE NOT c.node_id = ANY(w.path)
        ),
        ordered AS (
            SELECT
                node_id,
                value,
                path
            FROM walk
            ORDER BY path DESC
        )
        SELECT
            v_traversal_id,
            ROW_NUMBER() OVER (ORDER BY path DESC)::INTEGER - 1,
            node_id,
            value
        FROM ordered;
    END IF;

    UPDATE traversal_run
    SET status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE traversal_id = v_traversal_id;

    RETURN v_traversal_id;

EXCEPTION
    WHEN OTHERS THEN
        IF v_traversal_id IS NOT NULL THEN
            UPDATE traversal_run
            SET status = 'FAILED',
                completed_at = CURRENT_TIMESTAMP
            WHERE traversal_id = v_traversal_id;
        END IF;
        RAISE;
END;
$$;

CREATE VIEW traversal_report AS
SELECT
    tr.traversal_id,
    t.name AS tree_name,
    tr.traversal_type,
    tr.implementation,
    tr.status,
    COUNT(rr.node_id) AS node_count,
    MIN(rr.position) AS first_position,
    MAX(rr.position) AS last_position,
    tr.started_at,
    tr.completed_at
FROM traversal_run tr
JOIN tree t
  ON t.tree_id = tr.tree_id
LEFT JOIN traversal_result rr
  ON rr.traversal_id = tr.traversal_id
GROUP BY
    tr.traversal_id,
    t.name,
    tr.traversal_type,
    tr.implementation,
    tr.status,
    tr.started_at,
    tr.completed_at;

INSERT INTO tree (name)
VALUES ('balanced-seven-node-tree')
RETURNING tree_id;

INSERT INTO tree_node (tree_id, value)
VALUES
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (1, 7);

UPDATE tree_node SET left_node_id = 2, right_node_id = 3
WHERE tree_id = 1 AND value = 1;

UPDATE tree_node SET left_node_id = 4, right_node_id = 5
WHERE tree_id = 1 AND value = 2;

UPDATE tree_node SET left_node_id = 6, right_node_id = 7
WHERE tree_id = 1 AND value = 3;

SELECT validate_tree_structure(1) AS valid_tree;

BEGIN;

SELECT record_dfs_traversal(1, 'PREORDER');
SELECT record_dfs_traversal(1, 'INORDER');
SELECT record_dfs_traversal(1, 'POSTORDER');

COMMIT;

SELECT
    tree_name,
    traversal_type,
    status,
    node_count
FROM traversal_report
ORDER BY traversal_id;

SELECT
    tr.traversal_type,
    rr.position,
    rr.node_id,
    rr.node_value
FROM traversal_run tr
JOIN traversal_result rr
  ON rr.traversal_id = tr.traversal_id
WHERE tr.tree_id = 1
ORDER BY tr.traversal_id, rr.position;

SELECT
    traversal_type,
    STRING_AGG(node_value::TEXT, ' -> ' ORDER BY position) AS traversal
FROM traversal_run tr
JOIN traversal_result rr
  ON rr.traversal_id = tr.traversal_id
WHERE tr.tree_id = 1
GROUP BY traversal_type
ORDER BY traversal_type;
