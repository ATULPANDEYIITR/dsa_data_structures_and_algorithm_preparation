-- PostgreSQL 14+
-- Stack fundamentals represented as a persistent LIFO work history.
--
-- Each stack is identified by stack_id. Its elements receive monotonically
-- increasing positions. The highest position is the top of the stack.
-- The schema records operations so the state and operation history can
-- be inspected independently.

BEGIN;

DROP VIEW IF EXISTS stack_top;
DROP TABLE IF EXISTS stack_operations;
DROP TABLE IF EXISTS stack_items;
DROP TABLE IF EXISTS stack_registry;

CREATE TABLE stack_registry (
    stack_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stack_name TEXT NOT NULL UNIQUE,
    implementation TEXT NOT NULL
        CHECK (implementation IN ('array_model', 'linked_list_model')),
    capacity INTEGER CHECK (capacity IS NULL OR capacity >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stack_items (
    stack_id BIGINT NOT NULL
        REFERENCES stack_registry(stack_id) ON DELETE CASCADE,
    position BIGINT NOT NULL CHECK (position >= 1),
    item_value TEXT NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (stack_id, position)
);

CREATE TABLE stack_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stack_id BIGINT NOT NULL
        REFERENCES stack_registry(stack_id) ON DELETE CASCADE,
    operation_type TEXT NOT NULL
        CHECK (operation_type IN ('push', 'pop', 'peek', 'is_empty')),
    item_value TEXT,
    operation_succeeded BOOLEAN NOT NULL,
    detail TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- This index supports finding the most recent element without scanning
-- every element belonging to a stack.
CREATE INDEX stack_items_top_lookup
    ON stack_items (stack_id, position DESC);

CREATE INDEX stack_operations_recent
    ON stack_operations (stack_id, occurred_at DESC);

CREATE VIEW stack_top AS
SELECT
    r.stack_id,
    r.stack_name,
    r.implementation,
    i.position AS top_position,
    i.item_value AS top_value
FROM stack_registry AS r
LEFT JOIN LATERAL (
    SELECT position, item_value
    FROM stack_items
    WHERE stack_id = r.stack_id
    ORDER BY position DESC
    LIMIT 1
) AS i ON TRUE;

INSERT INTO stack_registry (stack_name, implementation, capacity)
VALUES
    ('array_demo', 'array_model', 5),
    ('linked_demo', 'linked_list_model', NULL);

-- Atomic push: lock the stack record, determine the next position,
-- enforce capacity, and insert the item in the same transaction.
CREATE OR REPLACE FUNCTION stack_push(
    p_stack_id BIGINT,
    p_value TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_capacity INTEGER;
    v_count BIGINT;
    v_position BIGINT;
BEGIN
    IF p_value IS NULL THEN
        RAISE EXCEPTION 'Stack elements cannot be NULL';
    END IF;

    SELECT capacity
    INTO v_capacity
    FROM stack_registry
    WHERE stack_id = p_stack_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown stack ID: %', p_stack_id;
    END IF;

    SELECT COUNT(*), COALESCE(MAX(position), 0) + 1
    INTO v_count, v_position
    FROM stack_items
    WHERE stack_id = p_stack_id;

    IF v_capacity IS NOT NULL AND v_count >= v_capacity THEN
        INSERT INTO stack_operations (
            stack_id, operation_type, item_value,
            operation_succeeded, detail
        )
        VALUES (
            p_stack_id, 'push', p_value,
            FALSE, 'Capacity limit reached'
        );
        RETURN NULL;
    END IF;

    INSERT INTO stack_items (stack_id, position, item_value)
    VALUES (p_stack_id, v_position, p_value);

    INSERT INTO stack_operations (
        stack_id, operation_type, item_value,
        operation_succeeded, detail
    )
    VALUES (
        p_stack_id, 'push', p_value,
        TRUE, 'Element added at top position'
    );

    RETURN v_position;
END;
$$;

-- Pop removes and returns the item at the highest position.
-- Empty-stack behavior is explicit: return NULL and record the failure.
CREATE OR REPLACE FUNCTION stack_pop(p_stack_id BIGINT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_position BIGINT;
    v_value TEXT;
BEGIN
    PERFORM 1
    FROM stack_registry
    WHERE stack_id = p_stack_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown stack ID: %', p_stack_id;
    END IF;

    SELECT position, item_value
    INTO v_position, v_value
    FROM stack_items
    WHERE stack_id = p_stack_id
    ORDER BY position DESC
    LIMIT 1
    FOR UPDATE;

    IF NOT FOUND THEN
        INSERT INTO stack_operations (
            stack_id, operation_type, item_value,
            operation_succeeded, detail
        )
        VALUES (
            p_stack_id, 'pop', NULL,
            FALSE, 'Underflow: stack is empty'
        );
        RETURN NULL;
    END IF;

    DELETE FROM stack_items
    WHERE stack_id = p_stack_id AND position = v_position;

    INSERT INTO stack_operations (
        stack_id, operation_type, item_value,
        operation_succeeded, detail
    )
    VALUES (
        p_stack_id, 'pop', v_value,
        TRUE, 'Top element removed'
    );

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION stack_peek(p_stack_id BIGINT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_value TEXT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM stack_registry WHERE stack_id = p_stack_id
    ) THEN
        RAISE EXCEPTION 'Unknown stack ID: %', p_stack_id;
    END IF;

    SELECT item_value
    INTO v_value
    FROM stack_items
    WHERE stack_id = p_stack_id
    ORDER BY position DESC
    LIMIT 1;

    INSERT INTO stack_operations (
        stack_id, operation_type, item_value,
        operation_succeeded, detail
    )
    VALUES (
        p_stack_id, 'peek', v_value,
        v_value IS NOT NULL,
        CASE
            WHEN v_value IS NULL THEN 'Underflow: stack is empty'
            ELSE 'Top element inspected without removal'
        END
    );

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION stack_is_empty(p_stack_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_empty BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM stack_registry WHERE stack_id = p_stack_id
    ) THEN
        RAISE EXCEPTION 'Unknown stack ID: %', p_stack_id;
    END IF;

    SELECT NOT EXISTS (
        SELECT 1 FROM stack_items WHERE stack_id = p_stack_id
    )
    INTO v_empty;

    INSERT INTO stack_operations (
        stack_id, operation_type, item_value,
        operation_succeeded, detail
    )
    VALUES (
        p_stack_id, 'is_empty', NULL,
        TRUE, CASE WHEN v_empty THEN 'Stack is empty'
                   ELSE 'Stack contains elements' END
    );

    RETURN v_empty;
END;
$$;

-- Seed both stack models with distinct operational data.
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo'),
    'Receive order'
);
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo'),
    'Validate payment'
);
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo'),
    'Reserve inventory'
);

SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'linked_demo'),
    'Read configuration'
);
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'linked_demo'),
    'Initialize service'
);

-- Inspect the top of every stack.
SELECT * FROM stack_top ORDER BY stack_name;

-- Peek does not remove the current top element.
SELECT stack_peek(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo')
) AS current_top;

-- Pop demonstrates LIFO: the most recently pushed item is returned first.
SELECT stack_pop(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo')
) AS removed_item;

-- Test the capacity boundary. Five total items are allowed in array_demo.
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo'),
    'Dispatch order'
);
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo'),
    'Archive order'
);
SELECT stack_push(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'array_demo'),
    'This item exceeds capacity'
);

-- Remove all items from linked_demo and expose the empty-stack behavior.
SELECT stack_pop(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'linked_demo')
);
SELECT stack_pop(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'linked_demo')
);
SELECT stack_pop(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'linked_demo')
);

SELECT stack_is_empty(
    (SELECT stack_id FROM stack_registry WHERE stack_name = 'linked_demo')
) AS linked_stack_is_empty;

-- Audit successful and unsuccessful operations separately.
SELECT
    r.stack_name,
    o.operation_type,
    o.operation_succeeded,
    o.item_value,
    o.detail,
    o.occurred_at
FROM stack_operations AS o
JOIN stack_registry AS r USING (stack_id)
ORDER BY o.operation_id;

-- The persistent relational model emulates stack behavior. It is not a
-- replacement for in-memory stacks in latency-sensitive algorithms.
-- For concurrent use, stack mutations must serialize on the registry row.
COMMIT;
