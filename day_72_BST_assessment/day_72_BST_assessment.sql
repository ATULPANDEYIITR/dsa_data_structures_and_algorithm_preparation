/*
 * Binary Search Tree Assessment and Practice
 * PostgreSQL 15+
 *
 * Relational representation of a BST:
 * - Assessment sessions
 * - Tree nodes
 * - Parent-child relationships
 * - Unique keys within each tree
 * - Structural integrity
 * - Search, insertion, deletion
 * - Minimum and maximum
 * - LCA
 * - Successor and predecessor
 * - Inorder traversal
 * - Range queries
 * - Height and balance
 * - Assessment reporting
 *
 * Each tree is an independent assessment instance.
 *
 * Duplicate keys are rejected.
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS bst_lab;

SET search_path TO bst_lab, public;

DROP VIEW IF EXISTS bst_assessment_report CASCADE;
DROP VIEW IF EXISTS bst_inorder_values CASCADE;
DROP TABLE IF EXISTS bst_operations CASCADE;
DROP TABLE IF EXISTS bst_nodes CASCADE;
DROP TABLE IF EXISTS bst_sessions CASCADE;

DROP FUNCTION IF EXISTS bst_insert(BIGINT, INTEGER);
DROP FUNCTION IF EXISTS bst_search(BIGINT, INTEGER);
DROP FUNCTION IF EXISTS bst_delete(BIGINT, INTEGER);
DROP FUNCTION IF EXISTS bst_minimum(BIGINT);
DROP FUNCTION IF EXISTS bst_maximum(BIGINT);
DROP FUNCTION IF EXISTS bst_successor(BIGINT, INTEGER);
DROP FUNCTION IF EXISTS bst_predecessor(BIGINT, INTEGER);
DROP FUNCTION IF EXISTS bst_lca(BIGINT, INTEGER, INTEGER);
DROP FUNCTION IF EXISTS bst_validate(BIGINT);
DROP FUNCTION IF EXISTS bst_height(BIGINT);
DROP FUNCTION IF EXISTS bst_is_balanced(BIGINT);
DROP FUNCTION IF EXISTS bst_inorder(BIGINT);
DROP FUNCTION IF EXISTS bst_range(BIGINT, INTEGER, INTEGER);
DROP FUNCTION IF EXISTS bst_node_integrity();
DROP FUNCTION IF EXISTS bst_node_count(BIGINT);
DROP PROCEDURE IF EXISTS bst_create_session(TEXT, INTEGER[]);

CREATE TABLE bst_sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_name VARCHAR(120) NOT NULL UNIQUE,

    root_node_id BIGINT,

    expected_node_count INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_expected_count
        CHECK (expected_node_count >= 0)
);

CREATE TABLE bst_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id BIGINT NOT NULL
        REFERENCES bst_sessions(session_id)
        ON DELETE CASCADE,

    node_key INTEGER NOT NULL,

    parent_node_id BIGINT,

    left_child_id BIGINT,

    right_child_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_key_per_session
        UNIQUE (session_id, node_key),

    CONSTRAINT unique_parent_reference
        UNIQUE (parent_node_id),

    CONSTRAINT unique_left_reference
        UNIQUE (left_child_id),

    CONSTRAINT unique_right_reference
        UNIQUE (right_child_id),

    CONSTRAINT no_self_parent
        CHECK (parent_node_id IS DISTINCT FROM node_id),

    CONSTRAINT no_self_left
        CHECK (left_child_id IS DISTINCT FROM node_id),

    CONSTRAINT no_self_right
        CHECK (right_child_id IS DISTINCT FROM node_id),

    CONSTRAINT different_children
        CHECK (
            left_child_id IS NULL
            OR right_child_id IS NULL
            OR left_child_id <> right_child_id
        ),

    CONSTRAINT no_self_child
        CHECK (
            (parent_node_id IS NULL OR parent_node_id <> node_id)
            AND
            (left_child_id IS NULL OR left_child_id <> node_id)
            AND
            (right_child_id IS NULL OR right_child_id <> node_id)
        ),

    CONSTRAINT unique_node_reference
        UNIQUE (node_id, session_id)
);

ALTER TABLE bst_sessions
ADD CONSTRAINT session_root_reference
FOREIGN KEY (root_node_id, session_id)
REFERENCES bst_nodes(node_id, session_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bst_nodes
ADD CONSTRAINT parent_same_session
FOREIGN KEY (parent_node_id, session_id)
REFERENCES bst_nodes(node_id, session_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bst_nodes
ADD CONSTRAINT left_child_same_session
FOREIGN KEY (left_child_id, session_id)
REFERENCES bst_nodes(node_id, session_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE bst_nodes
ADD CONSTRAINT right_child_same_session
FOREIGN KEY (right_child_id, session_id)
REFERENCES bst_nodes(node_id, session_id)
DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX idx_bst_nodes_session_key
ON bst_nodes(session_id, node_key);

CREATE INDEX idx_bst_nodes_parent
ON bst_nodes(session_id, parent_node_id);

CREATE INDEX idx_bst_nodes_left
ON bst_nodes(session_id, left_child_id);

CREATE INDEX idx_bst_nodes_right
ON bst_nodes(session_id, right_child_id);

CREATE TABLE bst_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_id BIGINT NOT NULL
        REFERENCES bst_sessions(session_id)
        ON DELETE CASCADE,

    operation_type VARCHAR(20) NOT NULL,

    requested_key INTEGER,

    second_key INTEGER,

    successful BOOLEAN NOT NULL,

    details TEXT NOT NULL,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_operation_type
        CHECK (
            operation_type IN (
                'INSERT',
                'SEARCH',
                'DELETE',
                'VALIDATE',
                'LCA',
                'MINIMUM',
                'MAXIMUM',
                'SUCCESSOR',
                'PREDECESSOR'
            )
        )
);

CREATE INDEX idx_bst_operations_session_time
ON bst_operations(session_id, executed_at DESC);


/* Maintain the expected node count transactionally. */

CREATE OR REPLACE FUNCTION bst_node_count(
    p_session_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM bst_nodes
    WHERE session_id = p_session_id;
$$;


/*
 * Insert a key using iterative BST traversal.
 * FOR UPDATE serializes modifications to the same session.
 */

CREATE OR REPLACE FUNCTION bst_insert(
    p_session_id BIGINT,
    p_key INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_current BIGINT;
    v_parent BIGINT;
    v_value INTEGER;
    v_new_node BIGINT;
BEGIN
    IF p_key IS NULL THEN
        RAISE EXCEPTION 'BST key cannot be NULL';
    END IF;

    SELECT root_node_id
    INTO v_root
    FROM bst_sessions
    WHERE session_id = p_session_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session: %', p_session_id;
    END IF;

    v_current := v_root;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key
        INTO v_value
        FROM bst_nodes
        WHERE node_id = v_current
          AND session_id = p_session_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Broken tree reference';
        END IF;

        IF p_key = v_value THEN
            INSERT INTO bst_operations (
                session_id,
                operation_type,
                requested_key,
                successful,
                details
            )
            VALUES (
                p_session_id,
                'INSERT',
                p_key,
                FALSE,
                'Duplicate key rejected'
            );

            RETURN FALSE;
        END IF;

        v_parent := v_current;

        IF p_key < v_value THEN
            SELECT left_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        ELSE
            SELECT right_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        END IF;
    END LOOP;

    INSERT INTO bst_nodes (
        session_id,
        node_key,
        parent_node_id
    )
    VALUES (
        p_session_id,
        p_key,
        v_parent
    )
    RETURNING node_id INTO v_new_node;

    IF v_parent IS NULL THEN
        UPDATE bst_sessions
        SET root_node_id = v_new_node,
            expected_node_count = expected_node_count + 1
        WHERE session_id = p_session_id;
    ELSIF p_key < (
        SELECT node_key
        FROM bst_nodes
        WHERE node_id = v_parent
    ) THEN
        UPDATE bst_nodes
        SET left_child_id = v_new_node
        WHERE node_id = v_parent;
    ELSE
        UPDATE bst_nodes
        SET right_child_id = v_new_node
        WHERE node_id = v_parent;
    END IF;

    IF v_parent IS NOT NULL THEN
        UPDATE bst_sessions
        SET expected_node_count = expected_node_count + 1
        WHERE session_id = p_session_id;
    END IF;

    INSERT INTO bst_operations (
        session_id,
        operation_type,
        requested_key,
        successful,
        details
    )
    VALUES (
        p_session_id,
        'INSERT',
        p_key,
        TRUE,
        'Node inserted'
    );

    RETURN TRUE;
END;
$$;


/* Search by following the BST ordering rule. */

CREATE OR REPLACE FUNCTION bst_search(
    p_session_id BIGINT,
    p_key INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_value INTEGER;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key
        INTO v_value
        FROM bst_nodes
        WHERE node_id = v_current
          AND session_id = p_session_id;

        IF v_value = p_key THEN
            RETURN v_current;
        END IF;

        IF p_key < v_value THEN
            SELECT left_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        ELSE
            SELECT right_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$;


/* Minimum and maximum. */

CREATE OR REPLACE FUNCTION bst_minimum(
    p_session_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_value INTEGER;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    IF v_current IS NULL THEN
        RETURN NULL;
    END IF;

    LOOP
        SELECT node_key, left_child_id
        INTO v_value, v_current
        FROM bst_nodes
        WHERE node_id = v_current;

        EXIT WHEN v_current IS NULL;
    END LOOP;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION bst_maximum(
    p_session_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_value INTEGER;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    IF v_current IS NULL THEN
        RETURN NULL;
    END IF;

    LOOP
        SELECT node_key, right_child_id
        INTO v_value, v_current
        FROM bst_nodes
        WHERE node_id = v_current;

        EXIT WHEN v_current IS NULL;
    END LOOP;

    RETURN v_value;
END;
$$;


/* Successor: smallest key strictly greater than the requested key. */

CREATE OR REPLACE FUNCTION bst_successor(
    p_session_id BIGINT,
    p_key INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_value INTEGER;
    v_candidate INTEGER := NULL;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key
        INTO v_value
        FROM bst_nodes
        WHERE node_id = v_current;

        IF p_key < v_value THEN
            v_candidate := v_value;

            SELECT left_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        ELSE
            SELECT right_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        END IF;
    END LOOP;

    RETURN v_candidate;
END;
$$;


/* Predecessor: largest key strictly smaller than the requested key. */

CREATE OR REPLACE FUNCTION bst_predecessor(
    p_session_id BIGINT,
    p_key INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_value INTEGER;
    v_candidate INTEGER := NULL;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key
        INTO v_value
        FROM bst_nodes
        WHERE node_id = v_current;

        IF p_key > v_value THEN
            v_candidate := v_value;

            SELECT right_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        ELSE
            SELECT left_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;
        END IF;
    END LOOP;

    RETURN v_candidate;
END;
$$;


/* LCA requires both keys to exist. */

CREATE OR REPLACE FUNCTION bst_lca(
    p_session_id BIGINT,
    p_first INTEGER,
    p_second INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_value INTEGER;
BEGIN
    IF bst_search(p_session_id, p_first) IS NULL
       OR bst_search(p_session_id, p_second) IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT root_node_id
    INTO v_current
    FROM bst_sessions
    WHERE session_id = p_session_id;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key
        INTO v_value
        FROM bst_nodes
        WHERE node_id = v_current;

        IF p_first < v_value AND p_second < v_value THEN
            SELECT left_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;

        ELSIF p_first > v_value AND p_second > v_value THEN
            SELECT right_child_id
            INTO v_current
            FROM bst_nodes
            WHERE node_id = v_current;

        ELSE
            RETURN v_value;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$;


/* Recursive inorder traversal. */

CREATE OR REPLACE FUNCTION bst_inorder(
    p_session_id BIGINT
)
RETURNS TABLE(node_key INTEGER)
LANGUAGE SQL
STABLE
AS $$
    WITH RECURSIVE traversal AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_child_id,
            n.right_child_id,
            0 AS depth,
            ARRAY[n.node_id] AS visited
        FROM bst_sessions s
        JOIN bst_nodes n
          ON n.node_id = s.root_node_id
         AND n.session_id = s.session_id
        WHERE s.session_id = p_session_id

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.left_child_id,
            child.right_child_id,
            parent.depth + 1,
            parent.visited || child.node_id
        FROM traversal parent
        JOIN bst_nodes child
          ON child.node_id IN (
              parent.left_child_id,
              parent.right_child_id
          )
         AND child.session_id = p_session_id
        WHERE NOT child.node_id = ANY(parent.visited)
    )
    SELECT t.node_key
    FROM traversal t
    ORDER BY t.node_key;
$$;


/* Range query using indexed key filtering. */

CREATE OR REPLACE FUNCTION bst_range(
    p_session_id BIGINT,
    p_low INTEGER,
    p_high INTEGER
)
RETURNS TABLE(node_key INTEGER)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_low > p_high THEN
        RAISE EXCEPTION 'Lower bound exceeds upper bound';
    END IF;

    RETURN QUERY
    SELECT n.node_key
    FROM bst_nodes n
    WHERE n.session_id = p_session_id
      AND n.node_key BETWEEN p_low AND p_high
    ORDER BY n.node_key;
END;
$$;


/*
 * Structural validation.
 * Checks:
 * - One root for a nonempty tree.
 * - Root has no parent.
 * - Parent-child references agree.
 * - Strict ordering.
 * - No cycles or repeated reachability.
 * - All nodes are reachable.
 * - Expected count matches actual count.
 */

CREATE OR REPLACE FUNCTION bst_validate(
    p_session_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_root BIGINT;
    v_expected INTEGER;
    v_actual INTEGER;
    v_reached INTEGER;
    v_invalid INTEGER;
BEGIN
    SELECT root_node_id, expected_node_count
    INTO v_root, v_expected
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    SELECT COUNT(*)
    INTO v_actual
    FROM bst_nodes
    WHERE session_id = p_session_id;

    IF v_actual <> v_expected THEN
        RETURN FALSE;
    END IF;

    IF v_actual = 0 THEN
        RETURN v_root IS NULL;
    END IF;

    IF v_root IS NULL THEN
        RETURN FALSE;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM bst_nodes
        WHERE node_id = v_root
          AND parent_node_id IS NOT NULL
    ) THEN
        RETURN FALSE;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM bst_nodes parent
        JOIN bst_nodes child
          ON child.node_id = parent.left_child_id
         AND child.session_id = parent.session_id
        WHERE parent.session_id = p_session_id
          AND (
              child.parent_node_id <> parent.node_id
              OR child.node_key >= parent.node_key
          )
    ) THEN
        RETURN FALSE;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM bst_nodes parent
        JOIN bst_nodes child
          ON child.node_id = parent.right_child_id
         AND child.session_id = parent.session_id
        WHERE parent.session_id = p_session_id
          AND (
              child.parent_node_id <> parent.node_id
              OR child.node_key <= parent.node_key
          )
    ) THEN
        RETURN FALSE;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM bst_nodes child
        LEFT JOIN bst_nodes parent
          ON parent.node_id = child.parent_node_id
         AND parent.session_id = child.session_id
        WHERE child.session_id = p_session_id
          AND child.node_id <> v_root
          AND (
              parent.node_id IS NULL
              OR (
                  parent.left_child_id IS DISTINCT FROM child.node_id
                  AND parent.right_child_id IS DISTINCT FROM child.node_id
              )
          )
    ) THEN
        RETURN FALSE;
    END IF;

    WITH RECURSIVE reachable(node_id, visited) AS (
        SELECT v_root, ARRAY[v_root]

        UNION ALL

        SELECT child.node_id, r.visited || child.node_id
        FROM reachable r
        JOIN bst_nodes parent
          ON parent.node_id = r.node_id
        JOIN bst_nodes child
          ON child.node_id IN (
              parent.left_child_id,
              parent.right_child_id
          )
         AND child.session_id = p_session_id
        WHERE NOT child.node_id = ANY(r.visited)
    )
    SELECT COUNT(*)
    INTO v_reached
    FROM reachable;

    IF v_reached <> v_actual THEN
        RETURN FALSE;
    END IF;

    SELECT COUNT(*)
    INTO v_invalid
    FROM bst_nodes n
    WHERE n.session_id = p_session_id
      AND n.node_id <> v_root
      AND n.parent_node_id IS NULL;

    RETURN v_invalid = 0;
END;
$$;


/* Calculate height in edges. */

CREATE OR REPLACE FUNCTION bst_height(
    p_session_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_root BIGINT;
    v_height INTEGER;
BEGIN
    SELECT root_node_id
    INTO v_root
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    IF v_root IS NULL THEN
        RETURN -1;
    END IF;

    WITH RECURSIVE levels(node_id, depth, visited) AS (
        SELECT v_root, 0, ARRAY[v_root]

        UNION ALL

        SELECT child.node_id,
               parent.depth + 1,
               parent.visited || child.node_id
        FROM levels parent
        JOIN bst_nodes n
          ON n.node_id = parent.node_id
        JOIN bst_nodes child
          ON child.node_id IN (
              n.left_child_id,
              n.right_child_id
          )
         AND child.session_id = p_session_id
        WHERE NOT child.node_id = ANY(parent.visited)
    )
    SELECT MAX(depth)
    INTO v_height
    FROM levels;

    RETURN v_height;
END;
$$;


/* Check AVL-style height balance without modifying the tree. */

CREATE OR REPLACE FUNCTION bst_is_balanced(
    p_session_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_root BIGINT;
    v_unbalanced BOOLEAN;
BEGIN
    SELECT root_node_id
    INTO v_root
    FROM bst_sessions
    WHERE session_id = p_session_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    IF v_root IS NULL THEN
        RETURN TRUE;
    END IF;

    WITH RECURSIVE subtree_height AS (
        SELECT
            n.node_id,
            n.left_child_id,
            n.right_child_id,
            0 AS height
        FROM bst_nodes n
        WHERE n.node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.left_child_id,
            child.right_child_id,
            parent.height + 1
        FROM subtree_height parent
        JOIN bst_nodes child
          ON child.node_id IN (
              parent.left_child_id,
              parent.right_child_id
          )
         AND child.session_id = p_session_id
    ),
    node_depths AS (
        SELECT
            node_id,
            left_child_id,
            right_child_id,
            height AS depth
        FROM subtree_height
    ),
    balance_data AS (
        SELECT
            parent.node_id,
            COALESCE(left_data.depth, -1) AS left_depth,
            COALESCE(right_data.depth, -1) AS right_depth
        FROM node_depths parent
        LEFT JOIN node_depths left_data
          ON left_data.node_id = parent.left_child_id
        LEFT JOIN node_depths right_data
          ON right_data.node_id = parent.right_child_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM balance_data
        WHERE ABS(left_depth - right_depth) > 1
    )
    INTO v_unbalanced;

    RETURN NOT v_unbalanced;
END;
$$;


/*
 * Deletion uses the inorder successor.
 * The session row lock prevents concurrent modifications
 * to the same tree during the operation.
 */

CREATE OR REPLACE FUNCTION bst_delete(
    p_session_id BIGINT,
    p_key INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_target BIGINT;
    v_parent BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_child BIGINT;
    v_successor BIGINT;
    v_successor_parent BIGINT;
    v_value INTEGER;
BEGIN
    PERFORM 1
    FROM bst_sessions
    WHERE session_id = p_session_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown BST session';
    END IF;

    v_target := bst_search(p_session_id, p_key);

    IF v_target IS NULL THEN
        INSERT INTO bst_operations (
            session_id,
            operation_type,
            requested_key,
            successful,
            details
        )
        VALUES (
            p_session_id,
            'DELETE',
            p_key,
            FALSE,
            'Key not found'
        );

        RETURN FALSE;
    END IF;

    SELECT parent_node_id,
           left_child_id,
           right_child_id
    INTO v_parent, v_left, v_right
    FROM bst_nodes
    WHERE node_id = v_target;

    IF v_left IS NOT NULL AND v_right IS NOT NULL THEN
        v_successor := v_right;

        LOOP
            SELECT left_child_id
            INTO v_child
            FROM bst_nodes
            WHERE node_id = v_successor;

            EXIT WHEN v_child IS NULL;

            v_successor := v_child;
        END LOOP;

        SELECT node_key, parent_node_id
        INTO v_value, v_successor_parent
        FROM bst_nodes
        WHERE node_id = v_successor;

        UPDATE bst_nodes
        SET node_key = v_value
        WHERE node_id = v_target;

        v_target := v_successor;
        v_parent := v_successor_parent;

        SELECT left_child_id, right_child_id
        INTO v_left, v_right
        FROM bst_nodes
        WHERE node_id = v_target;
    END IF;

    v_child := COALESCE(v_left, v_right);

    IF v_parent IS NULL THEN
        UPDATE bst_sessions
        SET root_node_id = v_child
        WHERE session_id = p_session_id;

    ELSIF EXISTS (
        SELECT 1
        FROM bst_nodes
        WHERE node_id = v_parent
          AND left_child_id = v_target
    ) THEN
        UPDATE bst_nodes
        SET left_child_id = v_child
        WHERE node_id = v_parent;

    ELSE
        UPDATE bst_nodes
        SET right_child_id = v_child
        WHERE node_id = v_parent;
    END IF;

    IF v_child IS NOT NULL THEN
        UPDATE bst_nodes
        SET parent_node_id = v_parent
        WHERE node_id = v_child;
    END IF;

    DELETE FROM bst_nodes
    WHERE node_id = v_target;

    UPDATE bst_sessions
    SET expected_node_count = expected_node_count - 1
    WHERE session_id = p_session_id;

    INSERT INTO bst_operations (
        session_id,
        operation_type,
        requested_key,
        successful,
        details
    )
    VALUES (
        p_session_id,
        'DELETE',
        p_key,
        TRUE,
        'Node deleted'
    );

    RETURN TRUE;
END;
$$;


/* Assessment reporting view. */

CREATE OR REPLACE VIEW bst_inorder_values AS
SELECT
    s.session_id,
    s.session_name,
    ARRAY(
        SELECT i.node_key
        FROM bst_inorder(s.session_id) i
    ) AS inorder_values
FROM bst_sessions s;

CREATE OR REPLACE VIEW bst_assessment_report AS
SELECT
    s.session_id,
    s.session_name,
    s.expected_node_count,
    bst_node_count(s.session_id) AS actual_node_count,
    bst_minimum(s.session_id) AS minimum_key,
    bst_maximum(s.session_id) AS maximum_key,
    bst_height(s.session_id) AS tree_height,
    bst_is_balanced(s.session_id) AS is_balanced,
    bst_validate(s.session_id) AS is_valid,
    i.inorder_values,
    CASE
        WHEN bst_validate(s.session_id)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS assessment_status
FROM bst_sessions s
JOIN bst_inorder_values i
  ON i.session_id = s.session_id;


/* Transactional procedure for creating and populating a tree. */

CREATE OR REPLACE PROCEDURE bst_create_session(
    p_name TEXT,
    p_values INTEGER[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_session_id BIGINT;
    v_key INTEGER;
BEGIN
    IF p_name IS NULL OR LENGTH(TRIM(p_name)) = 0 THEN
        RAISE EXCEPTION 'Session name is required';
    END IF;

    IF p_values IS NULL THEN
        RAISE EXCEPTION 'Values array cannot be NULL';
    END IF;

    INSERT INTO bst_sessions(session_name)
    VALUES (p_name)
    RETURNING session_id INTO v_session_id;

    FOREACH v_key IN ARRAY p_values LOOP
        IF v_key IS NULL THEN
            RAISE EXCEPTION 'NULL keys are not permitted';
        END IF;

        IF NOT bst_insert(v_session_id, v_key) THEN
            RAISE EXCEPTION 'Duplicate key encountered: %', v_key;
        END IF;
    END LOOP;
END;
$$;


/*
 * Sample data.
 * All sample operations execute in a single transaction.
 */

CALL bst_create_session(
    'Primary BST Assessment',
    ARRAY[50, 30, 70, 20, 40, 60, 80]
);

CALL bst_create_session(
    'Balanced BST Assessment',
    ARRAY[40, 20, 60, 10, 30, 50, 70]
);

CALL bst_create_session(
    'Skewed BST Assessment',
    ARRAY[10, 20, 30, 40, 50]
);

CALL bst_create_session(
    'Empty BST Assessment',
    ARRAY[]::INTEGER[]
);


/* Demonstrate duplicate handling without aborting the main transaction. */

DO $$
DECLARE
    v_session BIGINT;
    v_result BOOLEAN;
BEGIN
    SELECT session_id
    INTO v_session
    FROM bst_sessions
    WHERE session_name = 'Primary BST Assessment';

    v_result := bst_insert(v_session, 50);

    RAISE NOTICE 'Duplicate insertion accepted: %', v_result;
END;
$$;


/* Retrieval and search. */

SELECT
    s.session_name,
    bst_search(s.session_id, 40) AS matching_node_id
FROM bst_sessions s
WHERE s.session_name = 'Primary BST Assessment';


/* Minimum and maximum. */

SELECT
    session_name,
    bst_minimum(session_id) AS minimum_key,
    bst_maximum(session_id) AS maximum_key
FROM bst_sessions;


/* Successor and predecessor. */

SELECT
    session_name,
    bst_successor(session_id, 40) AS successor_of_40,
    bst_predecessor(session_id, 60) AS predecessor_of_60
FROM bst_sessions
WHERE session_name = 'Primary BST Assessment';


/* Lowest common ancestor. */

SELECT
    bst_lca(
        session_id,
        20,
        40
    ) AS lca_20_40,
    bst_lca(
        session_id,
        20,
        80
    ) AS lca_20_80
FROM bst_sessions
WHERE session_name = 'Primary BST Assessment';


/* Inorder traversal. */

SELECT *
FROM bst_inorder_values
ORDER BY session_id;


/* Inclusive range query. */

SELECT *
FROM bst_range(
    (
        SELECT session_id
        FROM bst_sessions
        WHERE session_name = 'Primary BST Assessment'
    ),
    30,
    70
);


/* Structural validation. */

SELECT
    session_name,
    bst_validate(session_id) AS valid
FROM bst_sessions;


/* Height and balance evaluation. */

SELECT
    session_name,
    bst_height(session_id) AS height,
    bst_is_balanced(session_id) AS balanced
FROM bst_sessions;


/* Aggregated assessment report. */

SELECT *
FROM bst_assessment_report
ORDER BY session_id;


/*
 * Transactional deletion example.
 * The two-child root is deleted using its inorder successor.
 */

DO $$
DECLARE
    v_session BIGINT;
    v_deleted BOOLEAN;
BEGIN
    SELECT session_id
    INTO v_session
    FROM bst_sessions
    WHERE session_name = 'Primary BST Assessment';

    v_deleted := bst_delete(v_session, 50);

    RAISE NOTICE 'Root deletion successful: %', v_deleted;

    IF NOT bst_validate(v_session) THEN
        RAISE EXCEPTION 'BST integrity failed after deletion';
    END IF;
END;
$$;


/* Verify post-deletion structure. */

SELECT
    session_name,
    expected_node_count,
    bst_node_count(session_id) AS actual_count,
    bst_inorder(session_id) AS inorder_values,
    bst_validate(session_id) AS valid
FROM bst_sessions
WHERE session_name = 'Primary BST Assessment';


/* Operation audit history. */

SELECT
    session_id,
    operation_type,
    requested_key,
    successful,
    details,
    executed_at
FROM bst_operations
ORDER BY operation_id;


/*
 * Deliberate failure cases:
 *
 * 1. Duplicate insertion returns FALSE.
 * 2. Searching for a nonexistent key returns NULL.
 * 3. Deleting a nonexistent key returns FALSE.
 * 4. LCA returns NULL when either key is absent.
 * 5. Empty-tree minimum and maximum return NULL.
 * 6. Invalid range bounds raise an exception.
 *
 * Uncomment the following statement to test exception handling:
 *
 * SELECT * FROM bst_range(1, 100, 10);
 */

COMMIT;
