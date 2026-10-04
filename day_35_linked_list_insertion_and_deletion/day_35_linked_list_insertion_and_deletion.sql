-- PostgreSQL 15+ compatible.
-- The schema models a practical ordered work queue whose records can be
-- inserted or deleted at the beginning, end, or a specific logical position.
--
-- SQL tables do not normally expose pointer manipulation like an in-memory
-- linked list.  The ordering is therefore represented explicitly with
-- position_no, while foreign keys and constraints protect relational integrity.

DROP SCHEMA IF EXISTS linked_list_practice CASCADE;
CREATE SCHEMA linked_list_practice;

SET search_path TO linked_list_practice;

CREATE TABLE work_queue (
    queue_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_code     TEXT NOT NULL,
    description   TEXT NOT NULL,
    priority      SMALLINT NOT NULL DEFAULT 3,
    position_no   INTEGER NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT work_queue_item_code_unique UNIQUE (item_code),
    CONSTRAINT work_queue_description_nonempty
        CHECK (length(trim(description)) > 0),
    CONSTRAINT work_queue_priority_valid
        CHECK (priority BETWEEN 1 AND 5),
    CONSTRAINT work_queue_position_valid
        CHECK (position_no >= 0),
    CONSTRAINT work_queue_position_unique
        UNIQUE (position_no)
);

CREATE INDEX work_queue_position_idx
    ON work_queue (position_no);

CREATE INDEX work_queue_priority_idx
    ON work_queue (priority, position_no);

CREATE TABLE queue_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_type TEXT NOT NULL,
    item_code TEXT,
    position_no INTEGER,
    operation_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT queue_operations_type_valid
        CHECK (
            operation_type IN (
                'INSERT_BEGINNING',
                'INSERT_END',
                'INSERT_POSITION',
                'DELETE_FIRST',
                'DELETE_LAST',
                'DELETE_VALUE',
                'DELETE_POSITION'
            )
        )
);

-- Initial ordered state.
INSERT INTO work_queue (item_code, description, priority, position_no)
VALUES
    ('JOB-100', 'Security validation', 5, 0),
    ('JOB-101', 'Unit test execution', 4, 1),
    ('JOB-102', 'Integration test execution', 4, 2),
    ('JOB-103', 'Package creation', 3, 3);

-- Insert at beginning.
--
-- Existing positions are shifted right first.  The unique constraint on
-- position_no makes the two statements deliberately transactional.
BEGIN;

UPDATE work_queue
SET position_no = position_no + 1
WHERE position_no >= 0;

INSERT INTO work_queue (
    item_code,
    description,
    priority,
    position_no
)
VALUES (
    'JOB-099',
    'Emergency validation',
    5,
    0
);

INSERT INTO queue_operations (operation_type, item_code, position_no)
VALUES ('INSERT_BEGINNING', 'JOB-099', 0);

COMMIT;

-- Insert at end.
INSERT INTO work_queue (
    item_code,
    description,
    priority,
    position_no
)
SELECT
    'JOB-104',
    'Deployment preparation',
    3,
    COALESCE(MAX(position_no) + 1, 0)
FROM work_queue;

INSERT INTO queue_operations (operation_type, item_code, position_no)
SELECT
    'INSERT_END',
    'JOB-104',
    MAX(position_no)
FROM work_queue
WHERE item_code = 'JOB-104';

-- Insert at a specific position.
-- This operation inserts JOB-100A at position 2 and shifts positions
-- 2 and above before the new row is created.
BEGIN;

UPDATE work_queue
SET position_no = position_no + 1
WHERE position_no >= 2;

INSERT INTO work_queue (
    item_code,
    description,
    priority,
    position_no
)
VALUES (
    'JOB-100A',
    'Additional verification',
    4,
    2
);

INSERT INTO queue_operations (operation_type, item_code, position_no)
VALUES ('INSERT_POSITION', 'JOB-100A', 2);

COMMIT;

-- Delete first.
-- Remove the row at position zero, then close the gap.
BEGIN;

DELETE FROM work_queue
WHERE position_no = 0;

UPDATE work_queue
SET position_no = position_no - 1
WHERE position_no > 0;

INSERT INTO queue_operations (operation_type, position_no)
VALUES ('DELETE_FIRST', 0);

COMMIT;

-- Delete last.
BEGIN;

WITH last_item AS (
    SELECT queue_id, position_no
    FROM work_queue
    ORDER BY position_no DESC
    LIMIT 1
)
DELETE FROM work_queue
WHERE queue_id IN (SELECT queue_id FROM last_item);

INSERT INTO queue_operations (operation_type, position_no)
SELECT
    'DELETE_LAST',
    MAX(position_no)
FROM work_queue;

COMMIT;

-- Delete by value.
-- item_code acts as the stable value/key for this relational model.
DELETE FROM work_queue
WHERE item_code = 'JOB-100A';

INSERT INTO queue_operations (operation_type, item_code)
VALUES ('DELETE_VALUE', 'JOB-100A');

-- Close the position gap after value deletion.
WITH ordered AS (
    SELECT
        queue_id,
        ROW_NUMBER() OVER (ORDER BY position_no) - 1 AS new_position
    FROM work_queue
)
UPDATE work_queue AS q
SET position_no = ordered.new_position
FROM ordered
WHERE q.queue_id = ordered.queue_id
  AND q.position_no <> ordered.new_position;

-- Delete by position.
BEGIN;

DELETE FROM work_queue
WHERE position_no = 1;

UPDATE work_queue
SET position_no = position_no - 1
WHERE position_no > 1;

INSERT INTO queue_operations (operation_type, position_no)
VALUES ('DELETE_POSITION', 1);

COMMIT;

-- Current queue ordered by logical position.
SELECT
    position_no,
    item_code,
    description,
    priority
FROM work_queue
ORDER BY position_no;

-- Find an item by its value.
SELECT
    position_no,
    item_code,
    description,
    priority
FROM work_queue
WHERE item_code = 'JOB-102';

-- Count and verify contiguous positions.
--
-- A valid position-based representation should have exactly one row at
-- every integer position from zero through COUNT(*) - 1.
WITH expected AS (
    SELECT
        COUNT(*) AS row_count,
        COALESCE(MAX(position_no), -1) AS max_position
    FROM work_queue
),
duplicates AS (
    SELECT position_no, COUNT(*) AS occurrences
    FROM work_queue
    GROUP BY position_no
    HAVING COUNT(*) > 1
)
SELECT
    expected.row_count,
    expected.max_position,
    CASE
        WHEN expected.max_position = expected.row_count - 1
             AND NOT EXISTS (SELECT 1 FROM duplicates)
        THEN 'VALID'
        ELSE 'INVALID'
    END AS position_integrity
FROM expected;

-- Show operation history.
SELECT
    operation_id,
    operation_type,
    item_code,
    position_no,
    operation_time
FROM queue_operations
ORDER BY operation_id;

-- Demonstrate a failed integrity operation.
-- PostgreSQL rejects negative positions because of the CHECK constraint.
DO $$
BEGIN
    BEGIN
        INSERT INTO work_queue (
            item_code,
            description,
            priority,
            position_no
        )
        VALUES (
            'INVALID-NEGATIVE',
            'This row violates position rules',
            3,
            -1
        );
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected failure: negative position rejected';
    END;
END;
$$;

-- Demonstrate a duplicate-value failure.
-- item_code is unique, so a value that already exists cannot create a
-- second row accidentally.
DO $$
BEGIN
    BEGIN
        INSERT INTO work_queue (
            item_code,
            description,
            priority,
            position_no
        )
        SELECT
            item_code,
            'Duplicate value rejected',
            priority,
            (SELECT COALESCE(MAX(position_no) + 1, 0) FROM work_queue)
        FROM work_queue
        LIMIT 1;
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected failure: duplicate item_code rejected';
    END;
END;
$$;

-- A view provides a stable read interface without exposing the internal
-- identity column used to store physical rows.
CREATE OR REPLACE VIEW ordered_work_queue AS
SELECT
    position_no,
    item_code,
    description,
    priority,
    created_at
FROM work_queue
ORDER BY position_no;

SELECT * FROM ordered_work_queue;

-- The final state can be checked with an aggregate query.
SELECT
    COUNT(*) AS queue_size,
    MIN(position_no) AS first_position,
    MAX(position_no) AS last_position,
    COUNT(DISTINCT item_code) AS distinct_item_codes
FROM work_queue;
