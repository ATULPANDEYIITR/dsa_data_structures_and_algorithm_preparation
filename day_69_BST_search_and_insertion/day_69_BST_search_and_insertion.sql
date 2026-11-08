-- ============================================================
-- Binary Search Tree: PostgreSQL Implementation
-- ============================================================
-- Domain: Enterprise asset registry.
--
-- The application-level implementations use pointer-based BSTs.
-- PostgreSQL's relational implementation uses an indexed
-- self-referencing node table to represent BST relationships.
--
-- This script supports:
--   1. Node insertion
--   2. Search
--   3. Minimum
--   4. Maximum
--   5. Inorder traversal
--   6. Integrity validation
--   7. Performance comparison
--
-- PostgreSQL 14+
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS bst_lab;

SET search_path TO bst_lab, public;

-- ------------------------------------------------------------
-- 1. Enterprise domain tables
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS asset (
    asset_id BIGINT PRIMARY KEY,
    asset_name TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT asset_positive_id CHECK (asset_id > 0),
    CONSTRAINT asset_name_nonempty CHECK (
        length(trim(asset_name)) > 0
    )
);

CREATE TABLE IF NOT EXISTS bst_tree (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name TEXT NOT NULL UNIQUE,
    root_node_id BIGINT,
    node_count BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT tree_name_nonempty CHECK (
        length(trim(tree_name)) > 0
    ),

    CONSTRAINT tree_nonnegative_count CHECK (
        node_count >= 0
    )
);

CREATE TABLE IF NOT EXISTS bst_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES bst_tree(tree_id)
        ON DELETE CASCADE,

    asset_id BIGINT NOT NULL
        REFERENCES asset(asset_id),

    parent_node_id BIGINT,
    left_node_id BIGINT,
    right_node_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT node_unique_asset UNIQUE(tree_id, asset_id),

    CONSTRAINT node_unique_parent UNIQUE(tree_id, node_id),

    CONSTRAINT node_not_own_parent CHECK (
        parent_node_id IS NULL OR parent_node_id <> node_id
    ),

    CONSTRAINT node_not_own_left CHECK (
        left_node_id IS NULL OR left_node_id <> node_id
    ),

    CONSTRAINT node_not_own_right CHECK (
        right_node_id IS NULL OR right_node_id <> node_id
    ),

    CONSTRAINT node_distinct_children CHECK (
        left_node_id IS NULL
        OR right_node_id IS NULL
        OR left_node_id <> right_node_id
    ),

    CONSTRAINT node_parent_fk
        FOREIGN KEY(tree_id, parent_node_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT node_left_fk
        FOREIGN KEY(tree_id, left_node_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT node_right_fk
        FOREIGN KEY(tree_id, right_node_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

ALTER TABLE bst_tree
    DROP CONSTRAINT IF EXISTS tree_root_fk;

ALTER TABLE bst_tree
    ADD CONSTRAINT tree_root_fk
    FOREIGN KEY(tree_id, root_node_id)
    REFERENCES bst_node(tree_id, node_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE IF NOT EXISTS bst_operation_log (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id BIGINT NOT NULL
        REFERENCES bst_tree(tree_id)
        ON DELETE CASCADE,

    operation_type TEXT NOT NULL,
    search_key BIGINT,
    operation_success BOOLEAN NOT NULL,
    comparison_count INTEGER NOT NULL DEFAULT 0,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT operation_type_valid CHECK (
        operation_type IN (
            'INSERT',
            'SEARCH',
            'MINIMUM',
            'MAXIMUM'
        )
    ),

    CONSTRAINT operation_comparisons_nonnegative CHECK (
        comparison_count >= 0
    )
);

-- ------------------------------------------------------------
-- 2. Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_bst_node_tree_asset
    ON bst_node(tree_id, asset_id);

CREATE INDEX IF NOT EXISTS idx_bst_node_parent
    ON bst_node(tree_id, parent_node_id);

CREATE INDEX IF NOT EXISTS idx_bst_operation_history
    ON bst_operation_log(tree_id, executed_at DESC);

-- ------------------------------------------------------------
-- 3. Tree creation
-- ------------------------------------------------------------

INSERT INTO bst_tree(tree_name)
VALUES ('ENTERPRISE_ASSET_INDEX')
ON CONFLICT(tree_name) DO NOTHING;

-- ------------------------------------------------------------
-- 4. BST insertion function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_insert(
    p_tree_id BIGINT,
    p_asset_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_current BIGINT;
    v_current_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_comparisons INTEGER := 0;
    v_new_node BIGINT;
BEGIN
    -- Serialize writes to the same tree to prevent concurrent
    -- insertion from attaching nodes to stale parent positions.
    SELECT root_node_id
    INTO v_root
    FROM bst_tree
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM asset
        WHERE asset_id = p_asset_id
    ) THEN
        RAISE EXCEPTION 'Asset % does not exist', p_asset_id;
    END IF;

    IF v_root IS NULL THEN
        INSERT INTO bst_node(tree_id, asset_id)
        VALUES (p_tree_id, p_asset_id)
        RETURNING node_id INTO v_new_node;

        UPDATE bst_tree
        SET root_node_id = v_new_node,
            node_count = node_count + 1
        WHERE tree_id = p_tree_id;

        INSERT INTO bst_operation_log(
            tree_id, operation_type, search_key,
            operation_success, comparison_count
        )
        VALUES (
            p_tree_id, 'INSERT', p_asset_id, TRUE, 0
        );

        RETURN TRUE;
    END IF;

    v_current := v_root;

    LOOP
        SELECT a.asset_id, n.left_node_id, n.right_node_id
        INTO v_current_key, v_left, v_right
        FROM bst_node n
        JOIN asset a ON a.asset_id = n.asset_id
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_current
        FOR UPDATE OF n;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Tree contains an invalid node reference';
        END IF;

        v_comparisons := v_comparisons + 1;

        IF p_asset_id = v_current_key THEN
            INSERT INTO bst_operation_log(
                tree_id, operation_type, search_key,
                operation_success, comparison_count
            )
            VALUES (
                p_tree_id, 'INSERT', p_asset_id,
                FALSE, v_comparisons
            );

            RETURN FALSE;
        END IF;

        IF p_asset_id < v_current_key THEN
            IF v_left IS NULL THEN
                INSERT INTO bst_node(
                    tree_id, asset_id, parent_node_id
                )
                VALUES (
                    p_tree_id, p_asset_id, v_current
                )
                RETURNING node_id INTO v_new_node;

                UPDATE bst_node
                SET left_node_id = v_new_node
                WHERE node_id = v_current
                  AND tree_id = p_tree_id;

                EXIT;
            END IF;

            v_current := v_left;
        ELSE
            IF v_right IS NULL THEN
                INSERT INTO bst_node(
                    tree_id, asset_id, parent_node_id
                )
                VALUES (
                    p_tree_id, p_asset_id, v_current
                )
                RETURNING node_id INTO v_new_node;

                UPDATE bst_node
                SET right_node_id = v_new_node
                WHERE node_id = v_current
                  AND tree_id = p_tree_id;

                EXIT;
            END IF;

            v_current := v_right;
        END IF;
    END LOOP;

    UPDATE bst_tree
    SET node_count = node_count + 1
    WHERE tree_id = p_tree_id;

    INSERT INTO bst_operation_log(
        tree_id, operation_type, search_key,
        operation_success, comparison_count
    )
    VALUES (
        p_tree_id, 'INSERT', p_asset_id,
        TRUE, v_comparisons
    );

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 5. Search function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_search(
    p_tree_id BIGINT,
    p_asset_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_current_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_comparisons INTEGER := 0;
    v_found BOOLEAN := FALSE;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_tree
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT a.asset_id, n.left_node_id, n.right_node_id
        INTO v_current_key, v_left, v_right
        FROM bst_node n
        JOIN asset a ON a.asset_id = n.asset_id
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_current;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Invalid tree structure';
        END IF;

        v_comparisons := v_comparisons + 1;

        IF p_asset_id = v_current_key THEN
            v_found := TRUE;
            EXIT;
        ELSIF p_asset_id < v_current_key THEN
            v_current := v_left;
        ELSE
            v_current := v_right;
        END IF;
    END LOOP;

    INSERT INTO bst_operation_log(
        tree_id, operation_type, search_key,
        operation_success, comparison_count
    )
    VALUES (
        p_tree_id, 'SEARCH', p_asset_id,
        v_found, v_comparisons
    );

    RETURN v_found;
END;
$$;

-- ------------------------------------------------------------
-- 6. Minimum function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_minimum(p_tree_id BIGINT)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_left BIGINT;
    v_result BIGINT;
    v_comparisons INTEGER := 0;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_tree
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT n.left_node_id, a.asset_id
        INTO v_left, v_result
        FROM bst_node n
        JOIN asset a ON a.asset_id = n.asset_id
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_current;

        v_comparisons := v_comparisons + 1;

        IF v_left IS NULL THEN
            EXIT;
        END IF;

        v_current := v_left;
    END LOOP;

    INSERT INTO bst_operation_log(
        tree_id, operation_type, search_key,
        operation_success, comparison_count
    )
    VALUES (
        p_tree_id, 'MINIMUM', v_result,
        v_result IS NOT NULL, v_comparisons
    );

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 7. Maximum function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_maximum(p_tree_id BIGINT)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_right BIGINT;
    v_result BIGINT;
    v_comparisons INTEGER := 0;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_tree
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT n.right_node_id, a.asset_id
        INTO v_right, v_result
        FROM bst_node n
        JOIN asset a ON a.asset_id = n.asset_id
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_current;

        v_comparisons := v_comparisons + 1;

        IF v_right IS NULL THEN
            EXIT;
        END IF;

        v_current := v_right;
    END LOOP;

    INSERT INTO bst_operation_log(
        tree_id, operation_type, search_key,
        operation_success, comparison_count
    )
    VALUES (
        p_tree_id, 'MAXIMUM', v_result,
        v_result IS NOT NULL, v_comparisons
    );

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 8. Inorder traversal
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_inorder(p_tree_id BIGINT)
RETURNS TABLE(asset_id BIGINT)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE traversal(node_id, asset_id, left_node_id,
                             right_node_id) AS (
        SELECT n.node_id, a.asset_id,
               n.left_node_id, n.right_node_id
        FROM bst_tree t
        JOIN bst_node n
          ON n.node_id = t.root_node_id
         AND n.tree_id = t.tree_id
        JOIN asset a ON a.asset_id = n.asset_id
        WHERE t.tree_id = p_tree_id

        UNION ALL

        SELECT child.node_id, a.asset_id,
               child.left_node_id, child.right_node_id
        FROM traversal parent
        JOIN bst_node child
          ON child.node_id IN (
              parent.left_node_id,
              parent.right_node_id
          )
        JOIN asset a ON a.asset_id = child.asset_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT traversal.asset_id
    FROM traversal
    ORDER BY asset_id;
$$;

-- ------------------------------------------------------------
-- 9. Integrity validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_validate(p_tree_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_expected BIGINT;
    v_actual BIGINT;
    v_root BIGINT;
BEGIN
    SELECT node_count, root_node_id
    INTO v_expected, v_root
    FROM bst_tree
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT COUNT(*)
    INTO v_actual
    FROM bst_node
    WHERE tree_id = p_tree_id;

    IF v_actual <> v_expected THEN
        RETURN FALSE;
    END IF;

    IF v_expected = 0 THEN
        RETURN v_root IS NULL;
    END IF;

    IF v_root IS NULL THEN
        RETURN FALSE;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND node_id = v_root
          AND parent_node_id IS NULL
    ) THEN
        RETURN FALSE;
    END IF;

    -- Every non-root node must be reachable from the root.
    RETURN (
        SELECT COUNT(*) = v_expected
        FROM (
            WITH RECURSIVE reachable(node_id) AS (
                SELECT v_root

                UNION

                SELECT child_id
                FROM reachable r
                JOIN bst_node n
                  ON n.tree_id = p_tree_id
                 AND n.node_id = r.node_id
                CROSS JOIN LATERAL (
                    VALUES
                        (n.left_node_id),
                        (n.right_node_id)
                ) children(child_id)
                WHERE child_id IS NOT NULL
            )
            SELECT DISTINCT node_id
            FROM reachable
        ) visited
    );
END;
$$;

-- ------------------------------------------------------------
-- 10. Reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW bst_tree_report AS
SELECT
    t.tree_id,
    t.tree_name,
    t.node_count,
    bst_minimum(t.tree_id) AS minimum_asset_id,
    bst_maximum(t.tree_id) AS maximum_asset_id,
    bst_validate(t.tree_id) AS structurally_valid
FROM bst_tree t;

-- ------------------------------------------------------------
-- 11. Sample asset records
-- ------------------------------------------------------------

INSERT INTO asset(asset_id, asset_name, category)
VALUES
    (500, 'Network Router', 'NETWORK'),
    (300, 'Application Server', 'COMPUTE'),
    (700, 'Storage System', 'STORAGE'),
    (200, 'Firewall', 'SECURITY'),
    (400, 'Database Server', 'DATABASE'),
    (600, 'Backup Appliance', 'STORAGE'),
    (800, 'Load Balancer', 'NETWORK'),
    (350, 'Security Gateway', 'SECURITY'),
    (450, 'Monitoring Server', 'COMPUTE')
ON CONFLICT(asset_id) DO NOTHING;

-- ------------------------------------------------------------
-- 12. Populate tree transactionally
-- ------------------------------------------------------------

DO $$
DECLARE
    v_tree_id BIGINT;
    v_asset_id BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree_id
    FROM bst_tree
    WHERE tree_name = 'ENTERPRISE_ASSET_INDEX';

    FOR v_asset_id IN
        SELECT asset_id
        FROM asset
        WHERE asset_id IN (
            500, 300, 700, 200, 400, 600, 800, 350, 450
        )
        ORDER BY CASE asset_id
            WHEN 500 THEN 1
            WHEN 300 THEN 2
            WHEN 700 THEN 3
            WHEN 200 THEN 4
            WHEN 400 THEN 5
            WHEN 600 THEN 6
            WHEN 800 THEN 7
            WHEN 350 THEN 8
            WHEN 450 THEN 9
        END
    LOOP
        PERFORM bst_insert(v_tree_id, v_asset_id);
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 13. Retrieval and validation
-- ------------------------------------------------------------

SELECT
    t.tree_name,
    t.node_count,
    bst_search(t.tree_id, 400) AS found_400,
    bst_search(t.tree_id, 999) AS found_999,
    bst_minimum(t.tree_id) AS minimum_key,
    bst_maximum(t.tree_id) AS maximum_key,
    bst_validate(t.tree_id) AS valid
FROM bst_tree t
WHERE t.tree_name = 'ENTERPRISE_ASSET_INDEX';

-- Inorder traversal.
SELECT *
FROM bst_inorder(
    (
        SELECT tree_id
        FROM bst_tree
        WHERE tree_name = 'ENTERPRISE_ASSET_INDEX'
    )
);

-- Detailed node structure.
SELECT
    n.node_id,
    a.asset_id,
    a.asset_name,
    parent.asset_id AS parent_asset_id,
    left_child.asset_id AS left_asset_id,
    right_child.asset_id AS right_asset_id
FROM bst_node n
JOIN asset a ON a.asset_id = n.asset_id
LEFT JOIN bst_node parent
    ON parent.node_id = n.parent_node_id
LEFT JOIN bst_node left_child
    ON left_child.node_id = n.left_node_id
LEFT JOIN bst_node right_child
    ON right_child.node_id = n.right_node_id
WHERE n.tree_id = (
    SELECT tree_id
    FROM bst_tree
    WHERE tree_name = 'ENTERPRISE_ASSET_INDEX'
)
ORDER BY a.asset_id;

-- ------------------------------------------------------------
-- 14. Aggregation and operation reporting
-- ------------------------------------------------------------

SELECT
    operation_type,
    COUNT(*) AS total_operations,
    AVG(comparison_count)::NUMERIC(10, 2) AS average_comparisons,
    MAX(comparison_count) AS maximum_comparisons,
    COUNT(*) FILTER (
        WHERE operation_success
    ) AS successful_operations,
    COUNT(*) FILTER (
        WHERE NOT operation_success
    ) AS unsuccessful_operations
FROM bst_operation_log
WHERE tree_id = (
    SELECT tree_id
    FROM bst_tree
    WHERE tree_name = 'ENTERPRISE_ASSET_INDEX'
)
GROUP BY operation_type
ORDER BY operation_type;

-- ------------------------------------------------------------
-- 15. Failure-case demonstration
-- ------------------------------------------------------------

DO $$
DECLARE
    v_tree_id BIGINT;
    v_duplicate BOOLEAN;
BEGIN
    SELECT tree_id
    INTO v_tree_id
    FROM bst_tree
    WHERE tree_name = 'ENTERPRISE_ASSET_INDEX';

    v_duplicate := bst_insert(v_tree_id, 500);

    RAISE NOTICE 'Duplicate insertion accepted: %',
        v_duplicate;

    RAISE NOTICE 'Missing asset search: %',
        bst_search(v_tree_id, 999);
END;
$$;

-- ------------------------------------------------------------
-- 16. Transaction safety demonstration
-- ------------------------------------------------------------

SAVEPOINT before_test_insertion;

DO $$
DECLARE
    v_tree_id BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree_id
    FROM bst_tree
    WHERE tree_name = 'ENTERPRISE_ASSET_INDEX';

    PERFORM bst_insert(v_tree_id, 900);
END;
$$;

-- Remove the test insertion and its operation log.
ROLLBACK TO SAVEPOINT before_test_insertion;

-- ------------------------------------------------------------
-- 17. Final reporting
-- ------------------------------------------------------------

SELECT *
FROM bst_tree_report;

SELECT
    operation_type,
    search_key,
    operation_success,
    comparison_count,
    executed_at
FROM bst_operation_log
ORDER BY operation_id;

COMMIT;
