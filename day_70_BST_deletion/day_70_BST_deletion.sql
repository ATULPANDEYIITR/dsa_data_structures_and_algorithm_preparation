-- ============================================================
-- BINARY SEARCH TREE DELETION
-- PostgreSQL 15+
--
-- Models:
--   Trees
--   Nodes
--   Parent-child relationships
--   Insertion
--   Leaf deletion
--   One-child deletion
--   Two-child deletion
--   Successor and predecessor
--   Structural validation
--   Operation auditing
--
-- Duplicate keys are prohibited within a tree.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS bst_lab;

DROP SCHEMA bst_lab CASCADE;
CREATE SCHEMA bst_lab;

SET search_path TO bst_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES trees(tree_id) ON DELETE CASCADE,

    node_key INTEGER NOT NULL,

    parent_id BIGINT,

    CONSTRAINT uq_tree_node_key
        UNIQUE (tree_id, node_key),

    CONSTRAINT uq_node_tree_pair
        UNIQUE (tree_id, node_id),

    CONSTRAINT fk_node_parent
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT chk_not_own_parent
        CHECK (parent_id IS NULL OR parent_id <> node_id)
);

CREATE INDEX idx_nodes_tree_parent
    ON nodes(tree_id, parent_id);

CREATE INDEX idx_nodes_tree_key
    ON nodes(tree_id, node_key);

-- A tree has exactly one root when nonempty.
CREATE TABLE tree_roots (
    tree_id BIGINT PRIMARY KEY
        REFERENCES trees(tree_id) ON DELETE CASCADE,

    root_node_id BIGINT NOT NULL,

    CONSTRAINT fk_tree_root
        FOREIGN KEY (tree_id, root_node_id)
        REFERENCES nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE deletion_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES trees(tree_id) ON DELETE CASCADE,

    requested_key INTEGER NOT NULL,

    deletion_case VARCHAR(20) NOT NULL
        CHECK (
            deletion_case IN (
                'LEAF',
                'ONE_CHILD',
                'TWO_CHILDREN',
                'NOT_FOUND'
            )
        ),

    replacement_strategy VARCHAR(15)
        CHECK (
            replacement_strategy IN (
                'SUCCESSOR',
                'PREDECESSOR'
            )
        ),

    replacement_key INTEGER,

    deleted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deletion_audit_tree_date
    ON deletion_audit(tree_id, deleted_at DESC);

-- ------------------------------------------------------------
-- 2. INSERTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE insert_node(
    p_tree_id BIGINT,
    p_key INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_current BIGINT;
    v_parent BIGINT;
    v_current_key INTEGER;
    v_new_id BIGINT;
BEGIN
    IF p_key IS NULL THEN
        RAISE EXCEPTION 'Node key cannot be NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM trees WHERE tree_id = p_tree_id
    ) THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM nodes
        WHERE tree_id = p_tree_id
          AND node_key = p_key
    ) THEN
        RAISE EXCEPTION 'Duplicate key %', p_key;
    END IF;

    -- Serialize mutations of a particular tree.
    PERFORM 1
    FROM trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    SELECT root_node_id
    INTO v_root
    FROM tree_roots
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF v_root IS NULL THEN
        INSERT INTO nodes(tree_id, node_key)
        VALUES (p_tree_id, p_key)
        RETURNING node_id INTO v_new_id;

        INSERT INTO tree_roots(tree_id, root_node_id)
        VALUES (p_tree_id, v_new_id);

        RETURN;
    END IF;

    v_current := v_root;

    LOOP
        SELECT node_key
        INTO v_current_key
        FROM nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF p_key = v_current_key THEN
            RAISE EXCEPTION 'Duplicate key %', p_key;
        END IF;

        v_parent := v_current;

        -- Determine whether the selected child exists.
        SELECT node_id
        INTO v_current
        FROM nodes
        WHERE tree_id = p_tree_id
          AND parent_id = v_parent
          AND (
              (p_key < v_current_key AND node_key < v_current_key)
              OR
              (p_key > v_current_key AND node_key > v_current_key)
          )
        ORDER BY
            CASE
                WHEN p_key < v_current_key THEN node_key DESC
                ELSE node_key ASC
            END
        LIMIT 1;

        -- The previous query is not used for navigation because
        -- a parent may have two children. Resolve direct child
        -- using the actual BST boundary.
        IF v_current IS NULL THEN
            EXIT;
        END IF;
    END LOOP;

    -- Find the correct insertion parent using recursive traversal.
    v_current := v_root;

    LOOP
        SELECT node_key
        INTO v_current_key
        FROM nodes
        WHERE node_id = v_current;

        v_parent := v_current;

        SELECT node_id
        INTO v_current
        FROM nodes
        WHERE tree_id = p_tree_id
          AND parent_id = v_parent
          AND (
              (p_key < v_current_key AND node_key < v_current_key)
              OR
              (p_key > v_current_key AND node_key > v_current_key)
          )
        ORDER BY
            CASE
                WHEN p_key < v_current_key THEN node_key DESC
                ELSE node_key ASC
            END
        LIMIT 1;

        IF v_current IS NULL THEN
            EXIT;
        END IF;
    END LOOP;

    -- Determine whether the parent already has a child on
    -- the required side. A node has at most one child on each side.
    IF EXISTS (
        SELECT 1
        FROM nodes
        WHERE tree_id = p_tree_id
          AND parent_id = v_parent
          AND (
              (p_key < v_current_key AND node_key < v_current_key)
              OR
              (p_key > v_current_key AND node_key > v_current_key)
          )
    ) THEN
        RAISE EXCEPTION 'Insertion navigation conflict';
    END IF;

    INSERT INTO nodes(tree_id, node_key, parent_id)
    VALUES (p_tree_id, p_key, v_parent);

END;
$$;

-- ------------------------------------------------------------
-- 3. TREE VALIDATION
--
-- Each node must have exactly one parent except the root.
-- Descendants must obey strict BST ordering.
-- Cycles and disconnected nodes are rejected.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_tree(
    p_tree_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_total BIGINT;
    v_reachable BIGINT;
    v_invalid BIGINT;
    v_roots BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_total
    FROM nodes
    WHERE tree_id = p_tree_id;

    SELECT COUNT(*)
    INTO v_roots
    FROM nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    IF v_total = 0 THEN
        RETURN NOT EXISTS (
            SELECT 1 FROM tree_roots
            WHERE tree_id = p_tree_id
        );
    END IF;

    IF v_roots <> 1 THEN
        RETURN FALSE;
    END IF;

    SELECT root_node_id
    INTO v_root
    FROM tree_roots
    WHERE tree_id = p_tree_id;

    IF v_root IS NULL THEN
        RETURN FALSE;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM nodes
        WHERE tree_id = p_tree_id
          AND node_id = v_root
          AND parent_id IS NOT NULL
    ) THEN
        RETURN FALSE;
    END IF;

    WITH RECURSIVE traversal AS (
        SELECT
            node_id,
            node_key,
            parent_id,
            NULL::INTEGER AS lower_bound,
            NULL::INTEGER AS upper_bound,
            ARRAY[node_id] AS visited
        FROM nodes
        WHERE tree_id = p_tree_id
          AND node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.parent_id,
            CASE
                WHEN child.node_key < parent.node_key
                    THEN parent.lower_bound
                ELSE parent.node_key
            END,
            CASE
                WHEN child.node_key > parent.node_key
                    THEN parent.upper_bound
                ELSE parent.node_key
            END,
            parent.visited || child.node_id
        FROM traversal parent
        JOIN nodes child
          ON child.tree_id = p_tree_id
         AND child.parent_id = parent.node_id
        WHERE NOT child.node_id = ANY(parent.visited)
    )
    SELECT
        COUNT(*),
        COUNT(*) FILTER (
            WHERE
                (lower_bound IS NOT NULL
                    AND node_key <= lower_bound)
                OR
                (upper_bound IS NOT NULL
                    AND node_key >= upper_bound)
        )
    INTO v_reachable, v_invalid
    FROM traversal;

    RETURN v_reachable = v_total
       AND v_invalid = 0;
END;
$$;

-- ------------------------------------------------------------
-- 4. SUCCESSOR AND PREDECESSOR
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION find_successor(
    p_tree_id BIGINT,
    p_key INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_node BIGINT;
    v_candidate INTEGER;
    v_current_key INTEGER;
    v_parent BIGINT;
    v_result INTEGER;
BEGIN
    SELECT node_id
    INTO v_node
    FROM nodes
    WHERE tree_id = p_tree_id
      AND node_key = p_key;

    IF v_node IS NULL THEN
        RETURN NULL;
    END IF;

    -- If right subtree exists, choose its minimum.
    SELECT node_id
    INTO v_node
    FROM nodes
    WHERE tree_id = p_tree_id
      AND parent_id = v_node
      AND node_key > p_key;

    IF v_node IS NOT NULL THEN
        LOOP
            SELECT node_id
            INTO v_parent
            FROM nodes
            WHERE tree_id = p_tree_id
              AND parent_id = v_node
              AND node_key < (
                  SELECT node_key FROM nodes
                  WHERE node_id = v_node
              );

            IF v_parent IS NULL THEN
                EXIT;
            END IF;

            v_node := v_parent;
        END LOOP;

        SELECT node_key INTO v_result
        FROM nodes WHERE node_id = v_node;

        RETURN v_result;
    END IF;

    -- No right subtree: search ancestors.
    SELECT parent_id INTO v_parent
    FROM nodes
    WHERE node_id = (
        SELECT node_id FROM nodes
        WHERE tree_id = p_tree_id AND node_key = p_key
    );

    v_current_key := p_key;

    WHILE v_parent IS NOT NULL LOOP
        SELECT node_key, parent_id
        INTO v_result, v_node
        FROM nodes
        WHERE node_id = v_parent;

        IF v_result > v_current_key THEN
            RETURN v_result;
        END IF;

        v_parent := v_node;
    END LOOP;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION find_predecessor(
    p_tree_id BIGINT,
    p_key INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_node BIGINT;
    v_parent BIGINT;
    v_current_key INTEGER;
    v_result INTEGER;
BEGIN
    SELECT node_id
    INTO v_node
    FROM nodes
    WHERE tree_id = p_tree_id
      AND node_key = p_key;

    IF v_node IS NULL THEN
        RETURN NULL;
    END IF;

    -- Left subtree maximum.
    SELECT node_id
    INTO v_node
    FROM nodes
    WHERE tree_id = p_tree_id
      AND parent_id = v_node
      AND node_key < p_key;

    IF v_node IS NOT NULL THEN
        LOOP
            SELECT node_id
            INTO v_parent
            FROM nodes
            WHERE tree_id = p_tree_id
              AND parent_id = v_node
              AND node_key > (
                  SELECT node_key FROM nodes
                  WHERE node_id = v_node
              );

            IF v_parent IS NULL THEN
                EXIT;
            END IF;

            v_node := v_parent;
        END LOOP;

        SELECT node_key INTO v_result
        FROM nodes WHERE node_id = v_node;

        RETURN v_result;
    END IF;

    SELECT parent_id INTO v_parent
    FROM nodes
    WHERE tree_id = p_tree_id
      AND node_key = p_key;

    v_current_key := p_key;

    WHILE v_parent IS NOT NULL LOOP
        SELECT node_key, parent_id
        INTO v_result, v_node
        FROM nodes
        WHERE node_id = v_parent;

        IF v_result < v_current_key THEN
            RETURN v_result;
        END IF;

        v_parent := v_node;
    END LOOP;

    RETURN NULL;
END;
$$;

-- ------------------------------------------------------------
-- 5. DELETION PROCEDURE
--
-- Parent pointers define child relationships.
-- Left and right children are determined by key ordering.
--
-- Two-child deletion:
--   Find successor or predecessor.
--   Move its parent relationship.
--   Reattach the deleted node's remaining subtrees.
--   Remove the original target.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE delete_node(
    p_tree_id BIGINT,
    p_key INTEGER,
    p_strategy VARCHAR DEFAULT 'SUCCESSOR'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_target BIGINT;
    v_parent BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_replacement BIGINT;
    v_replacement_parent BIGINT;
    v_replacement_child BIGINT;
    v_case VARCHAR(20);
    v_replacement_key INTEGER;
    v_root BIGINT;
BEGIN
    IF p_strategy NOT IN ('SUCCESSOR', 'PREDECESSOR') THEN
        RAISE EXCEPTION 'Invalid replacement strategy: %',
            p_strategy;
    END IF;

    PERFORM 1
    FROM trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    SELECT node_id
    INTO v_target
    FROM nodes
    WHERE tree_id = p_tree_id
      AND node_key = p_key;

    IF v_target IS NULL THEN
        INSERT INTO deletion_audit(
            tree_id,
            requested_key,
            deletion_case,
            replacement_strategy
        )
        VALUES (
            p_tree_id,
            p_key,
            'NOT_FOUND',
            p_strategy
        );

        RETURN;
    END IF;

    SELECT parent_id
    INTO v_parent
    FROM nodes
    WHERE node_id = v_target;

    SELECT node_id
    INTO v_left
    FROM nodes
    WHERE tree_id = p_tree_id
      AND parent_id = v_target
      AND node_key < p_key;

    SELECT node_id
    INTO v_right
    FROM nodes
    WHERE tree_id = p_tree_id
      AND parent_id = v_target
      AND node_key > p_key;

    IF v_left IS NULL AND v_right IS NULL THEN
        v_case := 'LEAF';

    ELSIF v_left IS NULL OR v_right IS NULL THEN
        v_case := 'ONE_CHILD';

    ELSE
        v_case := 'TWO_CHILDREN';
    END IF;

    -- Leaf and one-child replacement.
    IF v_case IN ('LEAF', 'ONE_CHILD') THEN
        v_replacement := COALESCE(v_left, v_right);

        IF v_parent IS NULL THEN
            DELETE FROM tree_roots
            WHERE tree_id = p_tree_id;

            IF v_replacement IS NOT NULL THEN
                UPDATE nodes
                SET parent_id = NULL
                WHERE node_id = v_replacement;

                INSERT INTO tree_roots(tree_id, root_node_id)
                VALUES (p_tree_id, v_replacement);
            END IF;
        ELSIF v_replacement IS NOT NULL THEN
            UPDATE nodes
            SET parent_id = v_parent
            WHERE node_id = v_replacement;
        END IF;

    ELSE
        -- Find the inorder successor or predecessor.
        IF p_strategy = 'SUCCESSOR' THEN
            v_replacement := v_right;

            LOOP
                SELECT node_id
                INTO v_replacement_child
                FROM nodes
                WHERE tree_id = p_tree_id
                  AND parent_id = v_replacement
                  AND node_key < (
                      SELECT node_key
                      FROM nodes
                      WHERE node_id = v_replacement
                  );

                EXIT WHEN v_replacement_child IS NULL;

                v_replacement := v_replacement_child;
            END LOOP;

        ELSE
            v_replacement := v_left;

            LOOP
                SELECT node_id
                INTO v_replacement_child
                FROM nodes
                WHERE tree_id = p_tree_id
                  AND parent_id = v_replacement
                  AND node_key > (
                      SELECT node_key
                      FROM nodes
                      WHERE node_id = v_replacement
                  );

                EXIT WHEN v_replacement_child IS NULL;

                v_replacement := v_replacement_child;
            END LOOP;
        END IF;

        SELECT node_key, parent_id
        INTO v_replacement_key, v_replacement_parent
        FROM nodes
        WHERE node_id = v_replacement;

        -- The successor has no left child.
        -- The predecessor has no right child.
        IF p_strategy = 'SUCCESSOR' THEN
            SELECT node_id
            INTO v_replacement_child
            FROM nodes
            WHERE tree_id = p_tree_id
              AND parent_id = v_replacement
              AND node_key > v_replacement_key;
        ELSE
            SELECT node_id
            INTO v_replacement_child
            FROM nodes
            WHERE tree_id = p_tree_id
              AND parent_id = v_replacement
              AND node_key < v_replacement_key;
        END IF;

        -- Remove replacement from its original location.
        IF v_replacement_parent <> v_target THEN
            IF v_replacement_child IS NOT NULL THEN
                UPDATE nodes
                SET parent_id = v_replacement_parent
                WHERE node_id = v_replacement_child;
            END IF;
        END IF;

        -- Transfer the target's parent relationship.
        UPDATE nodes
        SET parent_id = v_parent
        WHERE node_id = v_replacement;

        -- Reattach the target's left and right children.
        -- The replacement may already own one of these subtrees.
        UPDATE nodes
        SET parent_id = v_replacement
        WHERE node_id IN (v_left, v_right)
          AND node_id <> v_replacement;

        IF v_parent IS NULL THEN
            UPDATE tree_roots
            SET root_node_id = v_replacement
            WHERE tree_id = p_tree_id;
        END IF;
    END IF;

    DELETE FROM nodes
    WHERE node_id = v_target;

    INSERT INTO deletion_audit(
        tree_id,
        requested_key,
        deletion_case,
        replacement_strategy,
        replacement_key
    )
    VALUES (
        p_tree_id,
        p_key,
        v_case,
        p_strategy,
        v_replacement_key
    );

    IF NOT validate_tree(p_tree_id) THEN
        RAISE EXCEPTION
            'BST integrity violation after deleting key %', p_key;
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 6. INORDER VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW inorder_tree AS
SELECT
    tree_id,
    node_key,
    parent_id
FROM nodes
ORDER BY tree_id, node_key;

-- ------------------------------------------------------------
-- 7. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO trees(tree_name)
VALUES
    ('DELETION_DEMO'),
    ('PREDECESSOR_DEMO'),
    ('EMPTY_DEMO');

-- Main tree:
--                 50
--              /      \
--            30        70
--           /  \      /  \
--         20   40    60   80
--             /  \     \
--            35  45    65

CALL insert_node(1, 50);
CALL insert_node(1, 30);
CALL insert_node(1, 70);
CALL insert_node(1, 20);
CALL insert_node(1, 40);
CALL insert_node(1, 60);
CALL insert_node(1, 80);
CALL insert_node(1, 35);
CALL insert_node(1, 45);
CALL insert_node(1, 65);

-- Second tree supports predecessor-based deletion.
CALL insert_node(2, 50);
CALL insert_node(2, 30);
CALL insert_node(2, 70);
CALL insert_node(2, 20);
CALL insert_node(2, 40);
CALL insert_node(2, 60);
CALL insert_node(2, 80);

COMMIT;

-- ------------------------------------------------------------
-- 8. RETRIEVAL
-- ------------------------------------------------------------

SELECT *
FROM inorder_tree
WHERE tree_id = 1;

-- ------------------------------------------------------------
-- 9. SUCCESSOR AND PREDECESSOR
-- ------------------------------------------------------------

SELECT
    find_successor(1, 50) AS successor_of_50,
    find_predecessor(1, 50) AS predecessor_of_50;

SELECT
    find_successor(1, 80) AS successor_of_maximum,
    find_predecessor(1, 20) AS predecessor_of_minimum;

-- ------------------------------------------------------------
-- 10. DELETION WORKFLOW
-- ------------------------------------------------------------

-- Leaf node.
CALL delete_node(1, 20, 'SUCCESSOR');

-- One-child node.
CALL delete_node(1, 60, 'SUCCESSOR');

-- Two-child node.
CALL delete_node(1, 70, 'SUCCESSOR');

-- Root node.
CALL delete_node(1, 50, 'SUCCESSOR');

-- Two-child deletion using predecessor.
CALL delete_node(2, 50, 'PREDECESSOR');

-- Missing key.
CALL delete_node(1, 999, 'SUCCESSOR');

-- ------------------------------------------------------------
-- 11. VALIDATION AND REPORTING
-- ------------------------------------------------------------

SELECT
    tree_id,
    tree_name,
    validate_tree(tree_id) AS is_valid
FROM trees
ORDER BY tree_id;

-- Node counts.
SELECT
    t.tree_name,
    COUNT(n.node_id) AS node_count
FROM trees t
LEFT JOIN nodes n USING (tree_id)
GROUP BY t.tree_id, t.tree_name
ORDER BY t.tree_name;

-- Deletion-case aggregation.
SELECT
    deletion_case,
    replacement_strategy,
    COUNT(*) AS operation_count
FROM deletion_audit
GROUP BY deletion_case, replacement_strategy
ORDER BY deletion_case, replacement_strategy;

-- Complete audit history.
SELECT
    tree_id,
    requested_key,
    deletion_case,
    replacement_strategy,
    replacement_key,
    deleted_at
FROM deletion_audit
ORDER BY audit_id;

-- ------------------------------------------------------------
-- 12. TRANSACTION AND FAILURE HANDLING
-- ------------------------------------------------------------

-- This transaction demonstrates rollback on a failed operation.
-- The original tree remains unchanged.

DO $$
BEGIN
    BEGIN
        CALL delete_node(1, 9999, 'SUCCESSOR');
        RAISE EXCEPTION 'Demonstration rollback';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Transaction failure handled: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 13. FINAL INTEGRITY REPORT
-- ------------------------------------------------------------

SELECT
    tree_name,
    validate_tree(tree_id) AS integrity_valid,
    (
        SELECT COUNT(*)
        FROM nodes n
        WHERE n.tree_id = t.tree_id
    ) AS remaining_nodes
FROM trees t
ORDER BY tree_id;
