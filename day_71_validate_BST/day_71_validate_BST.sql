/*
===============================================================================
VALIDATE BINARY SEARCH TREE
PostgreSQL 15+

Topics:
1. BST node storage and relational modeling.
2. Range-based validation.
3. Inorder-based validation.
4. Duplicate-key policies.
5. BST insertion and structural constraints.
6. Successor and predecessor.
7. Minimum and maximum.
8. Search and lowest common ancestor.
9. Deletion.
10. Recursive and iterative SQL operations.
11. Transactional validation.
12. Integrity enforcement and indexing.

The database stores individual trees and their nodes.
Each node belongs to exactly one tree.
Parent-child relationships are represented through self-referencing
foreign keys.
===============================================================================
*/

DROP SCHEMA IF EXISTS bst_lab CASCADE;

CREATE SCHEMA bst_lab;

SET search_path TO bst_lab, public;

-- ============================================================================
-- 1. DOMAIN TYPES
-- ============================================================================

CREATE TYPE duplicate_policy AS ENUM (
    'FORBID',
    'LEFT',
    'RIGHT'
);

CREATE TYPE validation_method AS ENUM (
    'RANGE',
    'INORDER'
);

CREATE TYPE validation_status AS ENUM (
    'VALID',
    'INVALID'
);

-- ============================================================================
-- 2. TREE METADATA
-- ============================================================================

CREATE TABLE bst_trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_name VARCHAR(120) NOT NULL UNIQUE,

    duplicate_rule duplicate_policy NOT NULL DEFAULT 'FORBID',

    root_node_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT tree_name_not_empty
        CHECK (length(trim(tree_name)) > 0)
);

-- ============================================================================
-- 3. NODE STORAGE
-- ============================================================================

CREATE TABLE bst_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL,

    node_key BIGINT NOT NULL,

    parent_node_id BIGINT,

    left_node_id BIGINT,

    right_node_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT node_tree_fk
        FOREIGN KEY (tree_id)
        REFERENCES bst_trees(tree_id)
        ON DELETE CASCADE,

    CONSTRAINT node_parent_fk
        FOREIGN KEY (parent_node_id)
        REFERENCES bst_nodes(node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT node_left_fk
        FOREIGN KEY (left_node_id)
        REFERENCES bst_nodes(node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT node_right_fk
        FOREIGN KEY (right_node_id)
        REFERENCES bst_nodes(node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT node_not_own_parent
        CHECK (parent_node_id IS DISTINCT FROM node_id),

    CONSTRAINT node_not_own_left_child
        CHECK (left_node_id IS DISTINCT FROM node_id),

    CONSTRAINT node_not_own_right_child
        CHECK (right_node_id IS DISTINCT FROM node_id),

    CONSTRAINT node_distinct_children
        CHECK (
            left_node_id IS NULL
            OR right_node_id IS NULL
            OR left_node_id <> right_node_id
        ),

    CONSTRAINT node_tree_node_unique
        UNIQUE (tree_id, node_id)
);

-- Ensure tree roots belong to the corresponding tree.
ALTER TABLE bst_trees
ADD CONSTRAINT tree_root_fk
FOREIGN KEY (tree_id, root_node_id)
REFERENCES bst_nodes(tree_id, node_id)
DEFERRABLE INITIALLY DEFERRED;

-- A node can have only one parent.
CREATE UNIQUE INDEX uq_bst_parent_node
ON bst_nodes(parent_node_id)
WHERE parent_node_id IS NOT NULL;

CREATE UNIQUE INDEX uq_bst_left_child
ON bst_nodes(left_node_id)
WHERE left_node_id IS NOT NULL;

CREATE UNIQUE INDEX uq_bst_right_child
ON bst_nodes(right_node_id)
WHERE right_node_id IS NOT NULL;

CREATE INDEX idx_bst_tree_key
ON bst_nodes(tree_id, node_key);

CREATE INDEX idx_bst_tree_parent
ON bst_nodes(tree_id, parent_node_id);

-- ============================================================================
-- 4. VALIDATION AUDIT
-- ============================================================================

CREATE TABLE validation_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES bst_trees(tree_id)
        ON DELETE CASCADE,

    method validation_method NOT NULL,

    status validation_status NOT NULL,

    node_count INTEGER NOT NULL CHECK (node_count >= 0),

    details TEXT NOT NULL,

    validated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bst_validation_history
ON validation_audit(tree_id, validated_at DESC);

-- ============================================================================
-- 5. NODE COUNT FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_node_count(
    p_tree_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM bst_nodes
    WHERE tree_id = p_tree_id;
$$;

-- ============================================================================
-- 6. RANGE-BASED VALIDATION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_bst_range(
    p_tree_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_root BIGINT;
    v_policy duplicate_policy;
    v_total INTEGER;
    v_reached INTEGER;
    v_valid BOOLEAN;
BEGIN
    SELECT root_node_id, duplicate_rule
    INTO v_root, v_policy
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    SELECT COUNT(*)::INTEGER
    INTO v_total
    FROM bst_nodes
    WHERE tree_id = p_tree_id;

    IF v_total = 0 THEN
        RETURN v_root IS NULL;
    END IF;

    IF v_root IS NULL THEN
        RETURN FALSE;
    END IF;

    /*
     * Carry lower and upper bounds through every recursive branch.
     * Numeric bounds prevent overflow when node_key is BIGINT.
     *
     * The path also detects cycles.
     */
    WITH RECURSIVE validation AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_node_id,
            n.right_node_id,
            NULL::NUMERIC AS lower_bound,
            NULL::NUMERIC AS upper_bound,
            FALSE AS lower_inclusive,
            FALSE AS upper_inclusive,
            ARRAY[n.node_id] AS path,
            TRUE AS valid
        FROM bst_nodes n
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.left_node_id,
            child.right_node_id,
            parent.lower_bound,
            parent.node_key::NUMERIC,
            parent.lower_inclusive,
            (v_policy = 'LEFT'),
            parent.path || child.node_id,
            (
                CASE
                    WHEN child.node_key < parent.node_key THEN TRUE
                    WHEN child.node_key = parent.node_key
                         AND v_policy = 'LEFT' THEN TRUE
                    ELSE FALSE
                END
            )
        FROM validation parent
        JOIN bst_nodes child
          ON child.node_id = parent.left_node_id
         AND child.tree_id = p_tree_id

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.left_node_id,
            child.right_node_id,
            parent.node_key::NUMERIC,
            parent.upper_bound,
            (v_policy = 'RIGHT'),
            parent.upper_inclusive,
            parent.path || child.node_id,
            (
                CASE
                    WHEN child.node_key > parent.node_key THEN TRUE
                    WHEN child.node_key = parent.node_key
                         AND v_policy = 'RIGHT' THEN TRUE
                    ELSE FALSE
                END
            )
        FROM validation parent
        JOIN bst_nodes child
          ON child.node_id = parent.right_node_id
         AND child.tree_id = p_tree_id
    )
    SELECT
        COUNT(*)::INTEGER,
        COALESCE(
            BOOL_AND(
                valid
                AND (
                    lower_bound IS NULL
                    OR node_key::NUMERIC > lower_bound
                    OR (
                        lower_inclusive
                        AND node_key::NUMERIC = lower_bound
                    )
                )
                AND (
                    upper_bound IS NULL
                    OR node_key::NUMERIC < upper_bound
                    OR (
                        upper_inclusive
                        AND node_key::NUMERIC = upper_bound
                    )
                )
                AND NOT (node_id = ANY(path[1:cardinality(path)-1])
                         IS TRUE)
            ),
            FALSE
        )
    INTO v_reached, v_valid
    FROM validation;

    RETURN v_valid AND v_reached = v_total;
END;
$$;

-- ============================================================================
-- 7. INORDER-BASED VALIDATION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_bst_inorder(
    p_tree_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_root BIGINT;
    v_policy duplicate_policy;
    v_total INTEGER;
    v_reached INTEGER;
    v_valid BOOLEAN;
BEGIN
    SELECT root_node_id, duplicate_rule
    INTO v_root, v_policy
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    SELECT COUNT(*)::INTEGER
    INTO v_total
    FROM bst_nodes
    WHERE tree_id = p_tree_id;

    IF v_total = 0 THEN
        RETURN v_root IS NULL;
    END IF;

    IF v_root IS NULL THEN
        RETURN FALSE;
    END IF;

    /*
     * First construct the inorder sequence.
     * The path detects cycles and the final count detects disconnected nodes.
     */
    WITH RECURSIVE traversal AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_node_id,
            n.right_node_id,
            ARRAY[n.node_id] AS path,
            1 AS depth
        FROM bst_nodes n
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.left_node_id,
            child.right_node_id,
            parent.path || child.node_id,
            parent.depth + 1
        FROM traversal parent
        JOIN bst_nodes child
          ON child.node_id IN (
              parent.left_node_id,
              parent.right_node_id
          )
         AND child.tree_id = p_tree_id
        WHERE NOT child.node_id = ANY(parent.path)
    ),
    ordered_nodes AS (
        SELECT
            node_id,
            node_key,
            ROW_NUMBER() OVER (
                ORDER BY
                    (
                        SELECT COUNT(*)
                        FROM bst_nodes ancestors
                        WHERE ancestors.tree_id = p_tree_id
                          AND ancestors.node_id = traversal.node_id
                    ),
                    node_key,
                    node_id
            ) AS sequence_number
        FROM traversal
    )
    SELECT COUNT(*)::INTEGER
    INTO v_reached
    FROM traversal;

    /*
     * A separate ordered recursive inorder traversal.
     * Position values encode the path using binary fractions.
     */
    WITH RECURSIVE inorder_nodes AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_node_id,
            n.right_node_id,
            0::NUMERIC AS position,
            1::BIGINT AS depth
        FROM bst_nodes n
        WHERE n.tree_id = p_tree_id
          AND n.node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.left_node_id,
            child.right_node_id,
            parent.position
                + CASE
                    WHEN child.node_id = parent.left_node_id
                    THEN -1::NUMERIC / power(2::NUMERIC, parent.depth)
                    ELSE 1::NUMERIC / power(2::NUMERIC, parent.depth)
                  END,
            parent.depth + 1
        FROM inorder_nodes parent
        JOIN bst_nodes child
          ON child.node_id IN (
              parent.left_node_id,
              parent.right_node_id
          )
         AND child.tree_id = p_tree_id
        WHERE parent.depth < 60
    ),
    sequence AS (
        SELECT
            node_key,
            LAG(node_key) OVER (
                ORDER BY position, node_key, node_id
            ) AS previous_key
        FROM inorder_nodes
    )
    SELECT COALESCE(
        BOOL_AND(
            CASE
                WHEN previous_key IS NULL THEN TRUE
                WHEN v_policy = 'FORBID'
                    THEN node_key > previous_key
                ELSE node_key >= previous_key
            END
        ),
        TRUE
    )
    INTO v_valid
    FROM sequence;

    RETURN v_valid AND v_reached = v_total;
END;
$$;

-- ============================================================================
-- 8. VALIDATION REPORTING PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE record_bst_validation(
    p_tree_id BIGINT,
    p_method validation_method
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_valid BOOLEAN;
    v_count INTEGER;
BEGIN
    v_valid := CASE p_method
        WHEN 'RANGE' THEN validate_bst_range(p_tree_id)
        WHEN 'INORDER' THEN validate_bst_inorder(p_tree_id)
    END;

    v_count := bst_node_count(p_tree_id);

    INSERT INTO validation_audit (
        tree_id,
        method,
        status,
        node_count,
        details
    )
    VALUES (
        p_tree_id,
        p_method,
        CASE WHEN v_valid THEN 'VALID' ELSE 'INVALID' END,
        v_count,
        CASE
            WHEN v_valid
            THEN 'BST ordering and structural reachability verified.'
            ELSE 'BST ordering or structural reachability failed.'
        END
    );
END;
$$;

-- ============================================================================
-- 9. MINIMUM AND MAXIMUM
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_minimum(
    p_tree_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_left BIGINT;
    v_key BIGINT;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_node_id
        INTO v_key, v_left
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF NOT FOUND THEN
            RETURN NULL;
        END IF;

        IF v_left IS NULL THEN
            RETURN v_key;
        END IF;

        v_current := v_left;
    END LOOP;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION bst_maximum(
    p_tree_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_right BIGINT;
    v_key BIGINT;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, right_node_id
        INTO v_key, v_right
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF NOT FOUND THEN
            RETURN NULL;
        END IF;

        IF v_right IS NULL THEN
            RETURN v_key;
        END IF;

        v_current := v_right;
    END LOOP;

    RETURN NULL;
END;
$$;

-- ============================================================================
-- 10. SEARCH
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_search(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_node_id, right_node_id
        INTO v_key, v_left, v_right
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF NOT FOUND THEN
            RETURN NULL;
        END IF;

        IF p_key = v_key THEN
            RETURN v_current;
        END IF;

        v_current := CASE
            WHEN p_key < v_key THEN v_left
            ELSE v_right
        END;
    END LOOP;

    RETURN NULL;
END;
$$;

-- ============================================================================
-- 11. SUCCESSOR
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_successor(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_candidate BIGINT;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_node_id, right_node_id
        INTO v_key, v_left, v_right
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF p_key < v_key THEN
            v_candidate := v_key;
            v_current := v_left;
        ELSE
            v_current := v_right;
        END IF;
    END LOOP;

    RETURN v_candidate;
END;
$$;

-- ============================================================================
-- 12. PREDECESSOR
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_predecessor(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_candidate BIGINT;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_node_id, right_node_id
        INTO v_key, v_left, v_right
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF p_key > v_key THEN
            v_candidate := v_key;
            v_current := v_right;
        ELSE
            v_current := v_left;
        END IF;
    END LOOP;

    RETURN v_candidate;
END;
$$;

-- ============================================================================
-- 13. LOWEST COMMON ANCESTOR
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_lca(
    p_tree_id BIGINT,
    p_first BIGINT,
    p_second BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
BEGIN
    IF bst_search(p_tree_id, p_first) IS NULL
       OR bst_search(p_tree_id, p_second) IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT root_node_id
    INTO v_current
    FROM bst_trees
    WHERE tree_id = p_tree_id;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_node_id, right_node_id
        INTO v_key, v_left, v_right
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id;

        IF p_first < v_key AND p_second < v_key THEN
            v_current := v_left;
        ELSIF p_first > v_key AND p_second > v_key THEN
            v_current := v_right;
        ELSE
            RETURN v_key;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$;

-- ============================================================================
-- 14. NODE INSERTION
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_insert(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_parent BIGINT;
    v_current_key BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_policy duplicate_policy;
    v_new_node BIGINT;
    v_go_left BOOLEAN;
BEGIN
    SELECT root_node_id, duplicate_rule
    INTO v_current, v_policy
    FROM bst_trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    IF v_current IS NULL THEN
        INSERT INTO bst_nodes(tree_id, node_key)
        VALUES (p_tree_id, p_key)
        RETURNING node_id INTO v_new_node;

        UPDATE bst_trees
        SET root_node_id = v_new_node,
            updated_at = CURRENT_TIMESTAMP
        WHERE tree_id = p_tree_id;

        RETURN v_new_node;
    END IF;

    LOOP
        v_parent := v_current;

        SELECT node_key, left_node_id, right_node_id
        INTO v_current_key, v_left, v_right
        FROM bst_nodes
        WHERE node_id = v_current
          AND tree_id = p_tree_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Broken node reference in tree %', p_tree_id;
        END IF;

        IF p_key < v_current_key THEN
            v_go_left := TRUE;
        ELSIF p_key > v_current_key THEN
            v_go_left := FALSE;
        ELSE
            IF v_policy = 'FORBID' THEN
                RAISE EXCEPTION 'Duplicate key: %', p_key;
            END IF;

            v_go_left := v_policy = 'LEFT';
        END IF;

        v_current := CASE
            WHEN v_go_left THEN v_left
            ELSE v_right
        END;

        IF v_current IS NULL THEN
            EXIT;
        END IF;
    END LOOP;

    INSERT INTO bst_nodes(
        tree_id,
        node_key,
        parent_node_id
    )
    VALUES (
        p_tree_id,
        p_key,
        v_parent
    )
    RETURNING node_id INTO v_new_node;

    IF v_go_left THEN
        UPDATE bst_nodes
        SET left_node_id = v_new_node
        WHERE node_id = v_parent;
    ELSE
        UPDATE bst_nodes
        SET right_node_id = v_new_node
        WHERE node_id = v_parent;
    END IF;

    UPDATE bst_trees
    SET updated_at = CURRENT_TIMESTAMP
    WHERE tree_id = p_tree_id;

    RETURN v_new_node;
END;
$$;

-- ============================================================================
-- 15. DELETION
-- ============================================================================

CREATE OR REPLACE FUNCTION bst_delete(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_target BIGINT;
    v_parent BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_successor BIGINT;
    v_successor_parent BIGINT;
    v_successor_right BIGINT;
    v_child BIGINT;
BEGIN
    PERFORM 1
    FROM bst_trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    v_target := bst_search(p_tree_id, p_key);

    IF v_target IS NULL THEN
        RETURN FALSE;
    END IF;

    SELECT parent_node_id, left_node_id, right_node_id
    INTO v_parent, v_left, v_right
    FROM bst_nodes
    WHERE node_id = v_target
    FOR UPDATE;

    IF v_left IS NOT NULL AND v_right IS NOT NULL THEN
        v_successor := v_right;

        LOOP
            SELECT left_node_id
            INTO v_child
            FROM bst_nodes
            WHERE node_id = v_successor
              AND tree_id = p_tree_id
            FOR UPDATE;

            EXIT WHEN v_child IS NULL;

            v_successor := v_child;
        END LOOP;

        SELECT parent_node_id, right_node_id
        INTO v_successor_parent, v_successor_right
        FROM bst_nodes
        WHERE node_id = v_successor;

        UPDATE bst_nodes
        SET node_key = (
            SELECT node_key
            FROM bst_nodes
            WHERE node_id = v_successor
        )
        WHERE node_id = v_target;

        IF v_successor_parent = v_target THEN
            UPDATE bst_nodes
            SET right_node_id = v_successor_right
            WHERE node_id = v_target;
        ELSE
            UPDATE bst_nodes
            SET left_node_id = v_successor_right
            WHERE node_id = v_successor_parent;
        END IF;

        IF v_successor_right IS NOT NULL THEN
            UPDATE bst_nodes
            SET parent_node_id = v_successor_parent
            WHERE node_id = v_successor_right;
        END IF;

        DELETE FROM bst_nodes
        WHERE node_id = v_successor;

    ELSE
        v_child := COALESCE(v_left, v_right);

        IF v_parent IS NULL THEN
            UPDATE bst_trees
            SET root_node_id = v_child,
                updated_at = CURRENT_TIMESTAMP
            WHERE tree_id = p_tree_id;
        ELSE
            UPDATE bst_nodes
            SET left_node_id = CASE
                    WHEN left_node_id = v_target THEN v_child
                    ELSE left_node_id
                END,
                right_node_id = CASE
                    WHEN right_node_id = v_target THEN v_child
                    ELSE right_node_id
                END
            WHERE node_id = v_parent;
        END IF;

        IF v_child IS NOT NULL THEN
            UPDATE bst_nodes
            SET parent_node_id = v_parent
            WHERE node_id = v_child;
        END IF;

        DELETE FROM bst_nodes
        WHERE node_id = v_target;
    END IF;

    UPDATE bst_trees
    SET updated_at = CURRENT_TIMESTAMP
    WHERE tree_id = p_tree_id;

    RETURN TRUE;
END;
$$;

-- ============================================================================
-- 16. REPORTING VIEW
-- ============================================================================

CREATE OR REPLACE VIEW bst_tree_report AS
SELECT
    t.tree_id,
    t.tree_name,
    t.duplicate_rule,
    t.root_node_id,
    COUNT(n.node_id)::INTEGER AS node_count,
    MIN(n.node_key) AS minimum_key,
    MAX(n.node_key) AS maximum_key,
    t.created_at,
    t.updated_at
FROM bst_trees t
LEFT JOIN bst_nodes n
    ON n.tree_id = t.tree_id
GROUP BY
    t.tree_id,
    t.tree_name,
    t.duplicate_rule,
    t.root_node_id,
    t.created_at,
    t.updated_at;

-- ============================================================================
-- 17. SAMPLE TREES
-- ============================================================================

INSERT INTO bst_trees(tree_name, duplicate_rule)
VALUES
    ('primary-index', 'FORBID'),
    ('duplicate-right-index', 'RIGHT'),
    ('empty-index', 'FORBID'),
    ('invalid-order-index', 'FORBID');

-- Primary BST:
--
--             50
--           /    \
--         30      70
--        /  \    /  \
--       20  40  60  80

SELECT bst_insert(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'primary-index'),
    value
)
FROM unnest(
    ARRAY[50, 30, 70, 20, 40, 60, 80]::BIGINT[]
) AS value;

-- Duplicate policy demonstration.

SELECT bst_insert(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'duplicate-right-index'),
    10
);

SELECT bst_insert(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'duplicate-right-index'),
    10
);

SELECT bst_insert(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'duplicate-right-index'),
    15
);

-- Construct an intentionally invalid tree using direct structural updates.
-- This represents corrupted or externally imported data.

DO $$
DECLARE
    v_tree BIGINT;
    v_root BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_invalid BIGINT;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_trees
    WHERE tree_name = 'invalid-order-index';

    INSERT INTO bst_nodes(tree_id, node_key)
    VALUES (v_tree, 10)
    RETURNING node_id INTO v_root;

    INSERT INTO bst_nodes(tree_id, node_key, parent_node_id)
    VALUES (v_tree, 5, v_root)
    RETURNING node_id INTO v_left;

    INSERT INTO bst_nodes(tree_id, node_key, parent_node_id)
    VALUES (v_tree, 15, v_root)
    RETURNING node_id INTO v_right;

    INSERT INTO bst_nodes(tree_id, node_key, parent_node_id)
    VALUES (v_tree, 12, v_left)
    RETURNING node_id INTO v_invalid;

    UPDATE bst_nodes
    SET left_node_id = v_left,
        right_node_id = v_right
    WHERE node_id = v_root;

    UPDATE bst_nodes
    SET right_node_id = v_invalid
    WHERE node_id = v_left;

    UPDATE bst_trees
    SET root_node_id = v_root
    WHERE tree_id = v_tree;
END;
$$;

-- ============================================================================
-- 18. RETRIEVAL QUERIES
-- ============================================================================

-- Tree metadata and node counts.

SELECT *
FROM bst_tree_report
ORDER BY tree_id;

-- Individual nodes.

SELECT
    node_id,
    node_key,
    parent_node_id,
    left_node_id,
    right_node_id
FROM bst_nodes
WHERE tree_id = (
    SELECT tree_id
    FROM bst_trees
    WHERE tree_name = 'primary-index'
)
ORDER BY node_key;

-- ============================================================================
-- 19. VALIDATION QUERIES
-- ============================================================================

SELECT
    tree_name,
    validate_bst_range(tree_id) AS range_valid,
    validate_bst_inorder(tree_id) AS inorder_valid
FROM bst_trees
ORDER BY tree_id;

CALL record_bst_validation(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'primary-index'),
    'RANGE'
);

CALL record_bst_validation(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'primary-index'),
    'INORDER'
);

CALL record_bst_validation(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'invalid-order-index'),
    'RANGE'
);

-- ============================================================================
-- 20. SUCCESSOR AND PREDECESSOR QUERIES
-- ============================================================================

SELECT
    bst_successor(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index'),
        40
    ) AS successor_of_40,

    bst_predecessor(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index'),
        40
    ) AS predecessor_of_40;

-- Boundary behavior.

SELECT
    bst_successor(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index'),
        80
    ) AS successor_of_maximum,

    bst_predecessor(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index'),
        20
    ) AS predecessor_of_minimum;

-- ============================================================================
-- 21. SEARCH, MINIMUM, MAXIMUM AND LCA
-- ============================================================================

SELECT
    bst_search(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index'),
        40
    ) AS found_node_id;

SELECT
    bst_minimum(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index')
    ) AS minimum_key,

    bst_maximum(
        (SELECT tree_id FROM bst_trees
         WHERE tree_name = 'primary-index')
    ) AS maximum_key;

SELECT bst_lca(
    (SELECT tree_id FROM bst_trees
     WHERE tree_name = 'primary-index'),
    20,
    40
) AS lowest_common_ancestor;

-- ============================================================================
-- 22. AGGREGATION AND AUDIT REPORTING
-- ============================================================================

SELECT
    t.tree_name,
    a.method,
    a.status,
    COUNT(*) AS validation_runs,
    MAX(a.validated_at) AS latest_validation
FROM validation_audit a
JOIN bst_trees t
    ON t.tree_id = a.tree_id
GROUP BY
    t.tree_name,
    a.method,
    a.status
ORDER BY t.tree_name, a.method, a.status;

-- Trees with failed validations.

SELECT DISTINCT
    t.tree_name,
    a.details
FROM validation_audit a
JOIN bst_trees t
    ON t.tree_id = a.tree_id
WHERE a.status = 'INVALID';

-- ============================================================================
-- 23. TRANSACTIONAL WORKFLOW
-- ============================================================================

BEGIN;

DO $$
DECLARE
    v_tree BIGINT;
    v_valid BOOLEAN;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_trees
    WHERE tree_name = 'primary-index'
    FOR UPDATE;

    -- Add a new key.
    PERFORM bst_insert(v_tree, 55);

    -- Validate before committing.
    v_valid := validate_bst_range(v_tree);

    IF NOT v_valid THEN
        RAISE EXCEPTION
            'BST validation failed; transaction must roll back';
    END IF;

    INSERT INTO validation_audit(
        tree_id,
        method,
        status,
        node_count,
        details
    )
    VALUES (
        v_tree,
        'RANGE',
        'VALID',
        bst_node_count(v_tree),
        'Transactional insertion passed validation.'
    );
END;
$$;

COMMIT;

-- ============================================================================
-- 24. TRANSACTIONAL DELETION
-- ============================================================================

BEGIN;

DO $$
DECLARE
    v_tree BIGINT;
    v_valid BOOLEAN;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_trees
    WHERE tree_name = 'primary-index'
    FOR UPDATE;

    PERFORM bst_delete(v_tree, 55);

    v_valid := validate_bst_range(v_tree);

    IF NOT v_valid THEN
        RAISE EXCEPTION 'Deletion produced an invalid BST';
    END IF;
END;
$$;

COMMIT;

-- ============================================================================
-- 25. FINAL REPORT
-- ============================================================================

SELECT
    tree_name,
    duplicate_rule,
    node_count,
    minimum_key,
    maximum_key
FROM bst_tree_report
ORDER BY tree_name;

SELECT
    tree_name,
    method,
    status,
    node_count,
    validated_at
FROM validation_audit a
JOIN bst_trees t
    ON t.tree_id = a.tree_id
ORDER BY validated_at DESC;

-- ============================================================================
-- 26. OPERATIONAL NOTES
-- ============================================================================
--
-- 1. A BST's ordering rules are not guaranteed by foreign keys alone.
--    The validation functions verify the actual tree structure.
--
-- 2. The node table stores structural references. Cross-tree relationships
--    require additional enforcement in production systems.
--
-- 3. bst_insert serializes modifications to one tree using FOR UPDATE.
--
-- 4. Range validation detects violations that a parent-child local
--    comparison cannot detect.
--
-- 5. Inorder validation checks the global sorted-order property.
--
-- 6. Duplicate policies must remain consistent across insertion,
--    validation, deletion and lookup.
--
-- 7. The database functions assume a valid, acyclic tree when executing
--    operations such as search, insertion and successor.
--
-- 8. Production deployments should restrict direct writes to bst_nodes.
--    Grant application users execution permissions on controlled routines.
--
-- 9. A normal unbalanced BST can degrade to O(n) operations.
--    For large production indexes, use PostgreSQL B-tree indexes or
--    a self-balancing tree implementation.
--
-- 10. Concurrent applications should use transactions and an appropriate
--     isolation level when performing multiple structural modifications.
-- ============================================================================
