-- ============================================================
-- HEAP FUNDAMENTALS
-- PostgreSQL implementation of array-backed binary heaps.
--
-- Demonstrates:
-- 1. Complete binary tree relationships.
-- 2. Min heap and max heap.
-- 3. Parent, left child and right child indexes.
-- 4. Heap construction and insertion.
-- 5. Root extraction and heap restoration.
-- 6. Heap validation.
-- 7. Heap operation history and reporting.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS heap_lab;

SET search_path TO heap_lab, public;

-- ------------------------------------------------------------
-- Domain types
-- ------------------------------------------------------------

DO $$
BEGIN
    CREATE TYPE heap_mode AS ENUM ('MIN', 'MAX');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

DO $$
BEGIN
    CREATE TYPE operation_type AS ENUM (
        'BUILD',
        'INSERT',
        'EXTRACT'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

-- ------------------------------------------------------------
-- Heap storage
--
-- position is a one-based array index.
--
-- For a node at position p:
-- Parent       = floor(p / 2)
-- Left child   = 2 * p
-- Right child  = 2 * p + 1
--
-- This differs from the zero-based programming-language
-- representation.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS heaps (
    heap_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    heap_name VARCHAR(100) NOT NULL UNIQUE,
    mode heap_mode NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS heap_nodes (
    heap_id BIGINT NOT NULL
        REFERENCES heaps(heap_id) ON DELETE CASCADE,

    position INTEGER NOT NULL CHECK (position > 0),

    node_value INTEGER NOT NULL,

    PRIMARY KEY (heap_id, position)
);

CREATE INDEX IF NOT EXISTS idx_heap_nodes_value
    ON heap_nodes(heap_id, node_value);

CREATE TABLE IF NOT EXISTS heap_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    heap_id BIGINT NOT NULL
        REFERENCES heaps(heap_id) ON DELETE CASCADE,

    operation operation_type NOT NULL,

    affected_value INTEGER,

    operation_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Parent-child relationship view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW heap_relationships AS
SELECT
    child.heap_id,
    child.position,
    child.node_value,

    parent.node_value AS parent_value,

    left_node.node_value AS left_child_value,

    right_node.node_value AS right_child_value

FROM heap_nodes child

LEFT JOIN heap_nodes parent
    ON parent.heap_id = child.heap_id
   AND parent.position = child.position / 2

LEFT JOIN heap_nodes left_node
    ON left_node.heap_id = child.heap_id
   AND left_node.position = child.position * 2

LEFT JOIN heap_nodes right_node
    ON right_node.heap_id = child.heap_id
   AND right_node.position = child.position * 2 + 1;

-- ------------------------------------------------------------
-- Create heap
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_heap(
    p_name VARCHAR,
    p_mode heap_mode
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_heap_id BIGINT;
BEGIN
    IF p_name IS NULL OR LENGTH(TRIM(p_name)) = 0 THEN
        RAISE EXCEPTION 'Heap name cannot be empty.';
    END IF;

    INSERT INTO heaps(heap_name, mode)
    VALUES (p_name, p_mode)
    RETURNING heap_id INTO v_heap_id;

    RETURN v_heap_id;
END;
$$;

-- ------------------------------------------------------------
-- Heap priority comparison
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION higher_priority(
    p_mode heap_mode,
    p_a INTEGER,
    p_b INTEGER
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE
        WHEN p_mode = 'MIN' THEN p_a < p_b
        WHEN p_mode = 'MAX' THEN p_a > p_b
    END;
$$;

-- ------------------------------------------------------------
-- Swap two nodes
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE swap_nodes(
    p_heap_id BIGINT,
    p_first INTEGER,
    p_second INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_first INTEGER;
    v_second INTEGER;
BEGIN
    SELECT node_value
    INTO v_first
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = p_first;

    SELECT node_value
    INTO v_second
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = p_second;

    IF NOT FOUND AND v_second IS NULL THEN
        RAISE EXCEPTION 'Cannot swap missing heap nodes.';
    END IF;

    IF v_first IS NULL OR v_second IS NULL THEN
        RAISE EXCEPTION 'Cannot swap missing heap nodes.';
    END IF;

    UPDATE heap_nodes
    SET node_value = CASE
        WHEN position = p_first THEN v_second
        WHEN position = p_second THEN v_first
    END
    WHERE heap_id = p_heap_id
      AND position IN (p_first, p_second);
END;
$$;

-- ------------------------------------------------------------
-- Sift upward after insertion.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE sift_up(
    p_heap_id BIGINT,
    p_position INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_position INTEGER := p_position;
    v_parent INTEGER;
    v_value INTEGER;
    v_parent_value INTEGER;
    v_mode heap_mode;
BEGIN
    SELECT mode
    INTO v_mode
    FROM heaps
    WHERE heap_id = p_heap_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist.';
    END IF;

    WHILE v_position > 1 LOOP
        v_parent := v_position / 2;

        SELECT node_value
        INTO v_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_position;

        SELECT node_value
        INTO v_parent_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_parent;

        IF NOT higher_priority(
            v_mode,
            v_value,
            v_parent_value
        ) THEN
            EXIT;
        END IF;

        CALL swap_nodes(
            p_heap_id,
            v_position,
            v_parent
        );

        v_position := v_parent;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- Sift downward after root replacement.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE sift_down(
    p_heap_id BIGINT,
    p_position INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_position INTEGER := p_position;
    v_left INTEGER;
    v_right INTEGER;
    v_best INTEGER;
    v_size INTEGER;
    v_value INTEGER;
    v_best_value INTEGER;
    v_mode heap_mode;
BEGIN
    SELECT mode
    INTO v_mode
    FROM heaps
    WHERE heap_id = p_heap_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist.';
    END IF;

    SELECT COUNT(*)::INTEGER
    INTO v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    LOOP
        v_best := v_position;
        v_left := 2 * v_position;
        v_right := 2 * v_position + 1;

        SELECT node_value
        INTO v_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_best;

        IF v_left <= v_size THEN
            SELECT node_value
            INTO v_best_value
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_left;

            IF higher_priority(
                v_mode,
                v_best_value,
                v_value
            ) THEN
                v_best := v_left;
                v_value := v_best_value;
            END IF;
        END IF;

        IF v_right <= v_size THEN
            SELECT node_value
            INTO v_best_value
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_right;

            IF higher_priority(
                v_mode,
                v_best_value,
                v_value
            ) THEN
                v_best := v_right;
            END IF;
        END IF;

        EXIT WHEN v_best = v_position;

        CALL swap_nodes(
            p_heap_id,
            v_position,
            v_best
        );

        v_position := v_best;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- Validate heap-order and complete-array representation.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_heap(
    p_heap_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_mode heap_mode;
    v_size INTEGER;
    v_count INTEGER;
    v_invalid INTEGER;
BEGIN
    SELECT mode
    INTO v_mode
    FROM heaps
    WHERE heap_id = p_heap_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT COUNT(*)::INTEGER,
           COALESCE(MAX(position), 0)
    INTO v_count, v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    -- A complete tree must occupy consecutive positions.
    IF v_count <> v_size THEN
        RETURN FALSE;
    END IF;

    SELECT COUNT(*)
    INTO v_invalid
    FROM heap_nodes child
    JOIN heap_nodes parent
      ON parent.heap_id = child.heap_id
     AND parent.position = child.position / 2
    WHERE child.heap_id = p_heap_id
      AND higher_priority(
          v_mode,
          child.node_value,
          parent.node_value
      );

    RETURN v_invalid = 0;
END;
$$;

-- ------------------------------------------------------------
-- Insert a value.
--
-- Advisory transaction locks serialize modifications to the
-- same heap. Database transactions protect intermediate states.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE heap_insert(
    p_heap_id BIGINT,
    p_value INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_position INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(p_heap_id);

    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist.';
    END IF;

    SELECT COALESCE(MAX(position), 0) + 1
    INTO v_position
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    INSERT INTO heap_nodes(
        heap_id,
        position,
        node_value
    )
    VALUES (
        p_heap_id,
        v_position,
        p_value
    );

    CALL sift_up(p_heap_id, v_position);

    IF NOT validate_heap(p_heap_id) THEN
        RAISE EXCEPTION 'Heap invariant failed after insertion.';
    END IF;

    INSERT INTO heap_operations(
        heap_id,
        operation,
        affected_value
    )
    VALUES (
        p_heap_id,
        'INSERT',
        p_value
    );
END;
$$;

-- ------------------------------------------------------------
-- Extract the root element.
-- Returns the removed value.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_extract(
    p_heap_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_root INTEGER;
    v_last INTEGER;
    v_size INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(p_heap_id);

    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist.';
    END IF;

    SELECT COUNT(*)::INTEGER
    INTO v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    IF v_size = 0 THEN
        RAISE EXCEPTION 'Cannot extract from an empty heap.';
    END IF;

    SELECT node_value
    INTO v_root
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = 1;

    IF v_size = 1 THEN
        DELETE FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = 1;
    ELSE
        SELECT node_value
        INTO v_last
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_size;

        UPDATE heap_nodes
        SET node_value = v_last
        WHERE heap_id = p_heap_id
          AND position = 1;

        DELETE FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_size;

        CALL sift_down(p_heap_id, 1);
    END IF;

    IF NOT validate_heap(p_heap_id) THEN
        RAISE EXCEPTION 'Heap invariant failed after extraction.';
    END IF;

    INSERT INTO heap_operations(
        heap_id,
        operation,
        affected_value
    )
    VALUES (
        p_heap_id,
        'EXTRACT',
        v_root
    );

    RETURN v_root;
END;
$$;

-- ------------------------------------------------------------
-- Bottom-up heap construction.
--
-- Input is an integer array. Internal nodes are processed
-- from the final parent to the root.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE heap_build(
    p_heap_id BIGINT,
    p_values INTEGER[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_size INTEGER;
    v_index INTEGER;
BEGIN
    PERFORM pg_advisory_xact_lock(p_heap_id);

    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist.';
    END IF;

    IF p_values IS NULL THEN
        RAISE EXCEPTION 'Input array cannot be NULL.';
    END IF;

    IF array_position(p_values, NULL) IS NOT NULL THEN
        RAISE EXCEPTION 'Heap values cannot contain NULL.';
    END IF;

    DELETE FROM heap_nodes
    WHERE heap_id = p_heap_id;

    v_size := cardinality(p_values);

    IF v_size > 0 THEN
        FOR v_index IN 1..v_size LOOP
            INSERT INTO heap_nodes(
                heap_id,
                position,
                node_value
            )
            VALUES (
                p_heap_id,
                v_index,
                p_values[v_index]
            );
        END LOOP;

        FOR v_index IN REVERSE (v_size / 2)..1 LOOP
            CALL sift_down(p_heap_id, v_index);
        END LOOP;
    END IF;

    IF NOT validate_heap(p_heap_id) THEN
        RAISE EXCEPTION 'Heap construction validation failed.';
    END IF;

    INSERT INTO heap_operations(
        heap_id,
        operation,
        affected_value
    )
    VALUES (
        p_heap_id,
        'BUILD',
        NULL
    );
END;
$$;

-- ------------------------------------------------------------
-- Reporting views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW heap_summary AS
SELECT
    h.heap_id,
    h.heap_name,
    h.mode,
    COUNT(n.position)::INTEGER AS node_count,
    COALESCE(MAX(n.position), 0) AS last_position,
    CASE
        WHEN h.mode = 'MIN' THEN MIN(n.node_value)
        WHEN h.mode = 'MAX' THEN MAX(n.node_value)
    END AS root_priority
FROM heaps h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id
GROUP BY
    h.heap_id,
    h.heap_name,
    h.mode;

-- ------------------------------------------------------------
-- Sample workflow
-- ------------------------------------------------------------

DO $$
DECLARE
    v_min BIGINT;
    v_max BIGINT;
    v_removed INTEGER;
BEGIN
    v_min := create_heap('min_heap_example', 'MIN');
    v_max := create_heap('max_heap_example', 'MAX');

    -- Build a min heap from unsorted input.
    CALL heap_build(
        v_min,
        ARRAY[40, 10, 30, 50, 20, 60, 15]
    );

    -- Build a max heap from the same input.
    CALL heap_build(
        v_max,
        ARRAY[40, 10, 30, 50, 20, 60, 15]
    );

    -- Insert new elements.
    CALL heap_insert(v_min, 5);
    CALL heap_insert(v_max, 75);

    -- Extract roots.
    v_removed := heap_extract(v_min);
    RAISE NOTICE 'Removed min value: %', v_removed;

    v_removed := heap_extract(v_max);
    RAISE NOTICE 'Removed max value: %', v_removed;

    -- Verify invariants.
    IF NOT validate_heap(v_min) THEN
        RAISE EXCEPTION 'Min heap validation failed.';
    END IF;

    IF NOT validate_heap(v_max) THEN
        RAISE EXCEPTION 'Max heap validation failed.';
    END IF;

    RAISE NOTICE 'Both heaps are valid.';
END;
$$;

-- ------------------------------------------------------------
-- Retrieval
-- ------------------------------------------------------------

SELECT *
FROM heap_summary
ORDER BY heap_id;

SELECT
    h.heap_name,
    r.position,
    r.node_value,
    r.parent_value,
    r.left_child_value,
    r.right_child_value
FROM heap_relationships r
JOIN heaps h
    ON h.heap_id = r.heap_id
ORDER BY h.heap_id, r.position;

-- ------------------------------------------------------------
-- Validation report
-- ------------------------------------------------------------

SELECT
    h.heap_name,
    h.mode,
    validate_heap(h.heap_id) AS is_valid
FROM heaps h;

-- ------------------------------------------------------------
-- Aggregation
-- ------------------------------------------------------------

SELECT
    h.heap_name,
    h.mode,
    COUNT(n.position) AS total_nodes,
    MIN(n.node_value) AS minimum_value,
    MAX(n.node_value) AS maximum_value,
    AVG(n.node_value) AS average_value
FROM heaps h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id
GROUP BY h.heap_id, h.heap_name, h.mode;

-- ------------------------------------------------------------
-- Operation history
-- ------------------------------------------------------------

SELECT
    h.heap_name,
    o.operation,
    o.affected_value,
    o.operation_time
FROM heap_operations o
JOIN heaps h
    ON h.heap_id = o.heap_id
ORDER BY o.operation_id;

-- ------------------------------------------------------------
-- Eligibility determination:
-- Identify the root according to each heap's ordering mode.
-- ------------------------------------------------------------

SELECT
    h.heap_name,
    h.mode,
    root.node_value AS next_priority_element
FROM heaps h
LEFT JOIN heap_nodes root
    ON root.heap_id = h.heap_id
   AND root.position = 1
ORDER BY h.heap_id;

-- ------------------------------------------------------------
-- Transaction demonstration.
-- The operation is rolled back, preserving the original heap.
-- ------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    v_heap_id BIGINT;
BEGIN
    SELECT heap_id
    INTO v_heap_id
    FROM heaps
    WHERE heap_name = 'min_heap_example';

    CALL heap_insert(v_heap_id, -999);

    RAISE NOTICE 'Temporary insertion performed.';
END;
$$;

ROLLBACK;

-- Final integrity verification.
SELECT
    heap_name,
    mode,
    node_count,
    root_priority
FROM heap_summary
ORDER BY heap_id;
