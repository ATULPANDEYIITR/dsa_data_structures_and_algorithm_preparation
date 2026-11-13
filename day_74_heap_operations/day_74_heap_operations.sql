-- ============================================================
-- HEAP OPERATIONS: POSTGRESQL IMPLEMENTATION
-- ============================================================
--
-- Operations:
--   1. Insert
--   2. Extract minimum
--   3. Extract maximum
--   4. Heapify
--
-- Uses a relational representation of a binary heap.
-- Each node has a stable array position.
--
-- PostgreSQL 14+
--
-- IMPORTANT:
-- Array-backed relational storage provides database integrity
-- and transactional operations. It is not equivalent to the
-- asymptotic performance of an in-memory binary heap.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS heap_lab;

SET search_path TO heap_lab, public;

-- ------------------------------------------------------------
-- DOMAIN MODEL
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS heap_instances (
    heap_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    heap_name VARCHAR(100) NOT NULL UNIQUE,
    heap_type VARCHAR(10) NOT NULL
        CHECK (heap_type IN ('MIN', 'MAX')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS heap_nodes (
    heap_id BIGINT NOT NULL
        REFERENCES heap_instances(heap_id) ON DELETE CASCADE,

    position INTEGER NOT NULL CHECK (position >= 1),

    node_value BIGINT NOT NULL,

    PRIMARY KEY (heap_id, position)
);

CREATE INDEX IF NOT EXISTS idx_heap_nodes_value
    ON heap_nodes(heap_id, node_value);

CREATE TABLE IF NOT EXISTS heap_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    heap_id BIGINT NOT NULL
        REFERENCES heap_instances(heap_id) ON DELETE CASCADE,

    operation_type VARCHAR(20) NOT NULL
        CHECK (
            operation_type IN (
                'INSERT',
                'EXTRACT_MIN',
                'EXTRACT_MAX',
                'HEAPIFY'
            )
        ),

    operation_value BIGINT,

    operation_status VARCHAR(15) NOT NULL DEFAULT 'SUCCESS'
        CHECK (
            operation_status IN ('SUCCESS', 'FAILED')
        ),

    details TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_heap_operations_history
    ON heap_operations(heap_id, executed_at DESC);

-- ------------------------------------------------------------
-- HEAP CREATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_heap(
    p_name VARCHAR,
    p_type VARCHAR
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_heap_id BIGINT;
BEGIN
    IF p_name IS NULL OR BTRIM(p_name) = '' THEN
        RAISE EXCEPTION 'Heap name cannot be empty.';
    END IF;

    IF p_type NOT IN ('MIN', 'MAX') THEN
        RAISE EXCEPTION 'Heap type must be MIN or MAX.';
    END IF;

    INSERT INTO heap_instances(heap_name, heap_type)
    VALUES (p_name, p_type)
    RETURNING heap_id INTO v_heap_id;

    RETURN v_heap_id;
END;
$$;

-- ------------------------------------------------------------
-- INTERNAL SWAP OPERATION
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE swap_heap_nodes(
    p_heap_id BIGINT,
    p_position_a INTEGER,
    p_position_b INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_value_a BIGINT;
    v_value_b BIGINT;
BEGIN
    IF p_position_a = p_position_b THEN
        RETURN;
    END IF;

    SELECT node_value
    INTO STRICT v_value_a
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = p_position_a
    FOR UPDATE;

    SELECT node_value
    INTO STRICT v_value_b
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = p_position_b
    FOR UPDATE;

    UPDATE heap_nodes
    SET node_value = v_value_b
    WHERE heap_id = p_heap_id
      AND position = p_position_a;

    UPDATE heap_nodes
    SET node_value = v_value_a
    WHERE heap_id = p_heap_id
      AND position = p_position_b;
END;
$$;

-- ------------------------------------------------------------
-- INSERT
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE heap_insert(
    p_heap_id BIGINT,
    p_value BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(10);
    v_position INTEGER;
    v_parent INTEGER;
    v_parent_value BIGINT;
    v_current_value BIGINT;
    v_swap BOOLEAN;
BEGIN
    SELECT heap_type
    INTO STRICT v_type
    FROM heap_instances
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    SELECT COALESCE(MAX(position), 0) + 1
    INTO v_position
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    INSERT INTO heap_nodes(heap_id, position, node_value)
    VALUES (p_heap_id, v_position, p_value);

    WHILE v_position > 1 LOOP
        v_parent := v_position / 2;

        SELECT node_value
        INTO v_current_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_position;

        SELECT node_value
        INTO v_parent_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_parent;

        v_swap := CASE
            WHEN v_type = 'MIN'
                THEN v_current_value < v_parent_value
            ELSE v_current_value > v_parent_value
        END;

        EXIT WHEN NOT v_swap;

        CALL swap_heap_nodes(
            p_heap_id,
            v_position,
            v_parent
        );

        v_position := v_parent;
    END LOOP;

    UPDATE heap_instances
    SET updated_at = CURRENT_TIMESTAMP
    WHERE heap_id = p_heap_id;

    INSERT INTO heap_operations(
        heap_id,
        operation_type,
        operation_value,
        details
    )
    VALUES (
        p_heap_id,
        'INSERT',
        p_value,
        'Node inserted and sifted upward.'
    );
END;
$$;

-- ------------------------------------------------------------
-- EXTRACT ROOT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_extract(
    p_heap_id BIGINT,
    p_expected_type VARCHAR DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(10);
    v_result BIGINT;
    v_last_value BIGINT;
    v_size INTEGER;
    v_left INTEGER;
    v_right INTEGER;
    v_best INTEGER;
    v_best_value BIGINT;
    v_child_value BIGINT;
    v_root_value BIGINT;
    v_operation VARCHAR(20);
    v_swap BOOLEAN;
BEGIN
    SELECT heap_type
    INTO STRICT v_type
    FROM heap_instances
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF p_expected_type IS NOT NULL
       AND p_expected_type NOT IN ('MIN', 'MAX') THEN
        RAISE EXCEPTION 'Invalid extraction type.';
    END IF;

    IF p_expected_type IS NOT NULL
       AND p_expected_type <> v_type THEN
        RAISE EXCEPTION
            'Requested % extraction from a % heap.',
            p_expected_type,
            v_type;
    END IF;

    SELECT COUNT(*)
    INTO v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    IF v_size = 0 THEN
        RAISE EXCEPTION 'Cannot extract from empty heap.';
    END IF;

    SELECT node_value
    INTO v_result
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = 1;

    IF v_size = 1 THEN
        DELETE FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = 1;
    ELSE
        SELECT node_value
        INTO v_last_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_size;

        UPDATE heap_nodes
        SET node_value = v_last_value
        WHERE heap_id = p_heap_id
          AND position = 1;

        DELETE FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_size;

        -- Restore heap ordering from the root.
        v_size := v_size - 1;
        v_root_value := v_last_value;
        v_left := 2;

        LOOP
            EXIT WHEN v_left > v_size;

            v_right := v_left + 1;
            v_best := v_left;

            SELECT node_value
            INTO v_best_value
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_left;

            IF v_right <= v_size THEN
                SELECT node_value
                INTO v_child_value
                FROM heap_nodes
                WHERE heap_id = p_heap_id
                  AND position = v_right;

                IF (
                    (v_type = 'MIN' AND v_child_value < v_best_value)
                    OR
                    (v_type = 'MAX' AND v_child_value > v_best_value)
                ) THEN
                    v_best := v_right;
                    v_best_value := v_child_value;
                END IF;
            END IF;

            v_swap := CASE
                WHEN v_type = 'MIN'
                    THEN v_best_value < v_root_value
                ELSE v_best_value > v_root_value
            END;

            EXIT WHEN NOT v_swap;

            CALL swap_heap_nodes(
                p_heap_id,
                v_best,
                v_left / 2
            );

            v_root_value := v_best_value;
            v_left := v_best * 2;
        END LOOP;
    END IF;

    v_operation := CASE
        WHEN v_type = 'MIN' THEN 'EXTRACT_MIN'
        ELSE 'EXTRACT_MAX'
    END;

    INSERT INTO heap_operations(
        heap_id,
        operation_type,
        operation_value,
        details
    )
    VALUES (
        p_heap_id,
        v_operation,
        v_result,
        'Root extracted and heap ordering restored.'
    );

    UPDATE heap_instances
    SET updated_at = CURRENT_TIMESTAMP
    WHERE heap_id = p_heap_id;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- HEAPIFY
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE heapify_values(
    p_heap_id BIGINT,
    p_values BIGINT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(10);
    v_size INTEGER;
    v_index INTEGER;
    v_left INTEGER;
    v_right INTEGER;
    v_best INTEGER;
    v_root_value BIGINT;
    v_best_value BIGINT;
    v_child_value BIGINT;
    v_swap BOOLEAN;
BEGIN
    SELECT heap_type
    INTO STRICT v_type
    FROM heap_instances
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF p_values IS NULL THEN
        RAISE EXCEPTION 'Input array cannot be NULL.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM unnest(p_values) AS item
        WHERE item IS NULL
    ) THEN
        RAISE EXCEPTION 'Heap values cannot contain NULL.';
    END IF;

    DELETE FROM heap_nodes
    WHERE heap_id = p_heap_id;

    INSERT INTO heap_nodes(heap_id, position, node_value)
    SELECT
        p_heap_id,
        item.position::INTEGER,
        item.value
    FROM unnest(p_values) WITH ORDINALITY
        AS item(value, position);

    v_size := cardinality(p_values);

    -- Floyd's bottom-up construction.
    FOR v_index IN REVERSE (v_size / 2)..1 LOOP

        v_left := v_index;

        SELECT node_value
        INTO v_root_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_left;

        LOOP
            v_left := 2 * v_left;
            EXIT WHEN v_left > v_size;

            v_right := v_left + 1;
            v_best := v_left;

            SELECT node_value
            INTO v_best_value
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_left;

            IF v_right <= v_size THEN
                SELECT node_value
                INTO v_child_value
                FROM heap_nodes
                WHERE heap_id = p_heap_id
                  AND position = v_right;

                IF (
                    (v_type = 'MIN' AND v_child_value < v_best_value)
                    OR
                    (v_type = 'MAX' AND v_child_value > v_best_value)
                ) THEN
                    v_best := v_right;
                    v_best_value := v_child_value;
                END IF;
            END IF;

            v_swap := CASE
                WHEN v_type = 'MIN'
                    THEN v_best_value < v_root_value
                ELSE v_best_value > v_root_value
            END;

            EXIT WHEN NOT v_swap;

            CALL swap_heap_nodes(
                p_heap_id,
                v_best,
                v_best / 2
            );

            v_root_value := v_best_value;
            v_left := v_best;
        END LOOP;
    END LOOP;

    UPDATE heap_instances
    SET updated_at = CURRENT_TIMESTAMP
    WHERE heap_id = p_heap_id;

    INSERT INTO heap_operations(
        heap_id,
        operation_type,
        details
    )
    VALUES (
        p_heap_id,
        'HEAPIFY',
        'Existing nodes replaced and bottom-up heapification completed.'
    );
END;
$$;

-- ------------------------------------------------------------
-- VALIDATION VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW heap_integrity_report AS
SELECT
    h.heap_id,
    h.heap_name,
    h.heap_type,
    COUNT(n.position) AS node_count,

    COUNT(*) FILTER (
        WHERE
            (
                h.heap_type = 'MIN'
                AND parent.node_value > n.node_value
            )
            OR
            (
                h.heap_type = 'MAX'
                AND parent.node_value < n.node_value
            )
    ) AS ordering_violations

FROM heap_instances h

LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id

LEFT JOIN heap_nodes parent
    ON parent.heap_id = n.heap_id
   AND parent.position = n.position / 2

GROUP BY h.heap_id, h.heap_name, h.heap_type;

-- ------------------------------------------------------------
-- ROOT RETRIEVAL
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW heap_roots AS
SELECT
    h.heap_id,
    h.heap_name,
    h.heap_type,
    n.node_value AS root_value
FROM heap_instances h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id
   AND n.position = 1;

-- ------------------------------------------------------------
-- SAMPLE HEAPS
-- ------------------------------------------------------------

DO $$
DECLARE
    v_min BIGINT;
    v_max BIGINT;
    v_heap BIGINT;
BEGIN
    v_min := create_heap('integer_min_heap', 'MIN');
    v_max := create_heap('integer_max_heap', 'MAX');
    v_heap := create_heap('priority_min_heap', 'MIN');

    CALL heapify_values(
        v_min,
        ARRAY[45, 12, 30, 8, 25, 60, 18, 8]::BIGINT[]
    );

    CALL heapify_values(
        v_max,
        ARRAY[45, 12, 30, 8, 25, 60, 18, 8]::BIGINT[]
    );

    CALL heapify_values(
        v_heap,
        ARRAY[20, 90, 45, 70, 10, 85]::BIGINT[]
    );

    CALL heap_insert(v_min, 5);
    CALL heap_insert(v_max, 75);

    RAISE NOTICE 'Minimum extraction: %',
        heap_extract(v_min, 'MIN');

    RAISE NOTICE 'Maximum extraction: %',
        heap_extract(v_max, 'MAX');

END;
$$;

-- ------------------------------------------------------------
-- TRANSACTIONAL OPERATION EXAMPLE
-- ------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    v_heap BIGINT;
BEGIN
    SELECT heap_id
    INTO STRICT v_heap
    FROM heap_instances
    WHERE heap_name = 'integer_min_heap';

    CALL heap_insert(v_heap, 100);
    CALL heap_insert(v_heap, 200);

    RAISE NOTICE 'Inserted two values transactionally.';
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- Current heap roots.
SELECT *
FROM heap_roots
ORDER BY heap_name;

-- All heap elements.
SELECT
    h.heap_name,
    h.heap_type,
    n.position,
    n.node_value,
    FLOOR(n.position / 2.0) AS parent_position,
    FLOOR(n.position * 2) AS left_child_position,
    FLOOR(n.position * 2 + 1) AS right_child_position
FROM heap_instances h
JOIN heap_nodes n
    ON n.heap_id = h.heap_id
ORDER BY h.heap_name, n.position;

-- ------------------------------------------------------------
-- VALIDATION QUERY
-- ------------------------------------------------------------

SELECT *
FROM heap_integrity_report
ORDER BY heap_id;

-- ------------------------------------------------------------
-- AGGREGATION AND REPORTING
-- ------------------------------------------------------------

SELECT
    h.heap_name,
    h.heap_type,
    COUNT(n.position) AS total_elements,
    MIN(n.node_value) AS smallest_value,
    MAX(n.node_value) AS largest_value,
    AVG(n.node_value) AS average_value
FROM heap_instances h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id
GROUP BY h.heap_id, h.heap_name, h.heap_type
ORDER BY h.heap_name;

-- Operation history.
SELECT
    h.heap_name,
    o.operation_type,
    o.operation_value,
    o.operation_status,
    o.executed_at
FROM heap_operations o
JOIN heap_instances h
    ON h.heap_id = o.heap_id
ORDER BY o.executed_at DESC;

-- ------------------------------------------------------------
-- CTE: RANK HEAP VALUES
-- ------------------------------------------------------------

WITH ranked_values AS (
    SELECT
        h.heap_name,
        n.node_value,
        ROW_NUMBER() OVER (
            PARTITION BY h.heap_id
            ORDER BY n.node_value ASC
        ) AS ascending_rank
    FROM heap_instances h
    JOIN heap_nodes n
        ON n.heap_id = h.heap_id
)
SELECT *
FROM ranked_values
ORDER BY heap_name, ascending_rank;

-- ------------------------------------------------------------
-- ELIGIBILITY: HEAPS READY FOR EXTRACTION
-- ------------------------------------------------------------

SELECT
    h.heap_name,
    h.heap_type,
    CASE
        WHEN COUNT(n.position) = 0
            THEN 'NOT_ELIGIBLE'
        WHEN COUNT(n.position) > 0
            THEN 'ELIGIBLE'
    END AS extraction_status
FROM heap_instances h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id
GROUP BY h.heap_id, h.heap_name, h.heap_type;

-- ------------------------------------------------------------
-- EDGE CASES
-- ------------------------------------------------------------

-- Empty heap extraction raises an exception.
-- Invalid heap types are rejected by CHECK constraints.
-- Duplicate values are supported through distinct positions.
-- Failed transactions roll back structural modifications.

-- Demonstrate duplicate insertion.
DO $$
DECLARE
    v_heap BIGINT;
BEGIN
    SELECT heap_id
    INTO STRICT v_heap
    FROM heap_instances
    WHERE heap_name = 'integer_min_heap';

    CALL heap_insert(v_heap, 8);
    CALL heap_insert(v_heap, 8);

    RAISE NOTICE 'Duplicate values inserted successfully.';
END;
$$;

-- Final integrity report.
SELECT *
FROM heap_integrity_report
ORDER BY heap_id;
