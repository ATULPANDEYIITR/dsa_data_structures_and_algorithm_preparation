-- PostgreSQL hash-table learning lab.
-- The schema models hash-table entries, bucket placement, collisions,
-- lookup history, resizing, and workload measurements.

BEGIN;

DROP SCHEMA IF EXISTS hash_table_lab CASCADE;
CREATE SCHEMA hash_table_lab;
SET search_path TO hash_table_lab, public;

CREATE TABLE hash_tables (
    table_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name TEXT NOT NULL UNIQUE,
    bucket_count INTEGER NOT NULL CHECK (bucket_count > 0),
    entry_count BIGINT NOT NULL DEFAULT 0 CHECK (entry_count >= 0),
    max_load_factor NUMERIC(6, 3) NOT NULL DEFAULT 0.750
        CHECK (max_load_factor > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hash_entries (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_id BIGINT NOT NULL
        REFERENCES hash_tables(table_id) ON DELETE CASCADE,
    key_text TEXT NOT NULL,
    value_text TEXT NOT NULL,
    hash_value BIGINT NOT NULL CHECK (hash_value >= 0),
    bucket_index INTEGER NOT NULL CHECK (bucket_index >= 0),
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_key_per_table UNIQUE (table_id, key_text)
);

CREATE INDEX hash_entries_bucket_lookup_idx
    ON hash_entries(table_id, bucket_index);

CREATE INDEX hash_entries_updated_idx
    ON hash_entries(table_id, updated_at DESC);

CREATE TABLE lookup_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_id BIGINT NOT NULL
        REFERENCES hash_tables(table_id) ON DELETE CASCADE,
    key_text TEXT NOT NULL,
    operation TEXT NOT NULL
        CHECK (operation IN ('LOOKUP', 'INSERT', 'UPDATE', 'DELETE')),
    found BOOLEAN NOT NULL,
    examined_entries INTEGER NOT NULL DEFAULT 0
        CHECK (examined_entries >= 0),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX lookup_events_table_time_idx
    ON lookup_events(table_id, occurred_at DESC);

-- The database uses a deterministic demonstration hash, not a cryptographic
-- hash. PostgreSQL's hash indexes and hash partitioning are different
-- mechanisms from this explicitly stored bucket model.
CREATE FUNCTION demo_hash_key(input_key TEXT)
RETURNS BIGINT
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT (
        (
            SUM(
                ASCII(SUBSTRING(input_key FROM position FOR 1))::BIGINT
                * position::BIGINT
            ) % 2147483647
        ) + 2147483647
    ) % 2147483647
    FROM generate_series(1, LENGTH(input_key)) AS position
$$;

CREATE FUNCTION bucket_for_key(input_key TEXT, capacity INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF capacity <= 0 THEN
        RAISE EXCEPTION 'Bucket capacity must be positive';
    END IF;

    RETURN (demo_hash_key(input_key) % capacity)::INTEGER;
END;
$$;

-- INSERT and UPDATE operations maintain entry counts and bucket placement.
-- Entry movement during resizing is performed by resize_hash_table().
CREATE FUNCTION maintain_hash_entry()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    configured_capacity INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT bucket_count INTO configured_capacity
        FROM hash_tables
        WHERE table_id = NEW.table_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Unknown hash table %', NEW.table_id;
        END IF;

        NEW.hash_value := demo_hash_key(NEW.key_text);
        NEW.bucket_index :=
            bucket_for_key(NEW.key_text, configured_capacity);

        UPDATE hash_tables
        SET entry_count = entry_count + 1
        WHERE table_id = NEW.table_id;

        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.table_id <> OLD.table_id THEN
            RAISE EXCEPTION
                'Moving entries between hash tables requires explicit migration';
        END IF;

        SELECT bucket_count INTO configured_capacity
        FROM hash_tables
        WHERE table_id = NEW.table_id
        FOR UPDATE;

        NEW.hash_value := demo_hash_key(NEW.key_text);
        NEW.bucket_index :=
            bucket_for_key(NEW.key_text, configured_capacity);
        NEW.updated_at := CURRENT_TIMESTAMP;

        RETURN NEW;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER hash_entry_insert_update
BEFORE INSERT OR UPDATE ON hash_entries
FOR EACH ROW
EXECUTE FUNCTION maintain_hash_entry();

CREATE FUNCTION maintain_hash_entry_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE hash_tables
        SET entry_count = entry_count - 1
        WHERE table_id = OLD.table_id;

        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER hash_entry_delete_count
AFTER DELETE ON hash_entries
FOR EACH ROW
EXECUTE FUNCTION maintain_hash_entry_count();

-- The primary key is table_id plus key_text, not the hash value.
-- Hash collisions are expected and do not imply key equality.
CREATE VIEW bucket_statistics AS
SELECT
    t.table_id,
    t.table_name,
    t.bucket_count,
    t.entry_count,
    ROUND(t.entry_count::NUMERIC / t.bucket_count, 3) AS load_factor,
    COUNT(DISTINCT e.bucket_index) AS occupied_buckets,
    COALESCE(MAX(bucket_sizes.entries_in_bucket), 0) AS largest_bucket
FROM hash_tables t
LEFT JOIN hash_entries e ON e.table_id = t.table_id
LEFT JOIN (
    SELECT table_id, bucket_index, COUNT(*) AS entries_in_bucket
    FROM hash_entries
    GROUP BY table_id, bucket_index
) bucket_sizes
    ON bucket_sizes.table_id = t.table_id
    AND bucket_sizes.bucket_index = e.bucket_index
GROUP BY t.table_id, t.table_name, t.bucket_count, t.entry_count;

CREATE VIEW bucket_occupancy AS
SELECT
    t.table_id,
    t.table_name,
    bucket_number.bucket_index,
    COUNT(e.entry_id) AS entries_in_bucket
FROM hash_tables t
CROSS JOIN LATERAL
    generate_series(0, t.bucket_count - 1) AS bucket_number(bucket_index)
LEFT JOIN hash_entries e
    ON e.table_id = t.table_id
    AND e.bucket_index = bucket_number.bucket_index
GROUP BY t.table_id, t.table_name, bucket_number.bucket_index;

CREATE FUNCTION record_lookup(
    selected_table BIGINT,
    searched_key TEXT
)
RETURNS TABLE(found BOOLEAN, stored_value TEXT, examined INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_capacity INTEGER;
    selected_bucket INTEGER;
    observed_count INTEGER;
    matching_value TEXT;
BEGIN
    SELECT bucket_count INTO selected_capacity
    FROM hash_tables
    WHERE table_id = selected_table;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown hash table %', selected_table;
    END IF;

    selected_bucket := bucket_for_key(searched_key, selected_capacity);

    SELECT COUNT(*)::INTEGER
    INTO observed_count
    FROM hash_entries
    WHERE table_id = selected_table
      AND bucket_index = selected_bucket;

    SELECT value_text INTO matching_value
    FROM hash_entries
    WHERE table_id = selected_table
      AND bucket_index = selected_bucket
      AND key_text = searched_key;

    found := FOUND;
    stored_value := matching_value;
    examined := observed_count;

    INSERT INTO lookup_events (
        table_id, key_text, operation, found, examined_entries
    )
    VALUES (
        selected_table, searched_key, 'LOOKUP', found, examined
    );

    RETURN NEXT;
END;
$$;

CREATE FUNCTION resize_hash_table(
    selected_table BIGINT,
    new_capacity INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF new_capacity <= 0 THEN
        RAISE EXCEPTION 'New capacity must be positive';
    END IF;

    PERFORM 1
    FROM hash_tables
    WHERE table_id = selected_table
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown hash table %', selected_table;
    END IF;

    UPDATE hash_tables
    SET bucket_count = new_capacity
    WHERE table_id = selected_table;

    -- All existing entries must be redistributed after capacity changes.
    UPDATE hash_entries
    SET bucket_index = 0
    WHERE table_id = selected_table;

    UPDATE hash_entries
    SET bucket_index = bucket_for_key(key_text, new_capacity)
    WHERE table_id = selected_table;
END;
$$;

INSERT INTO hash_tables (table_name, bucket_count, max_load_factor)
VALUES
    ('service_registry', 4, 0.750),
    ('collision_lab', 4, 0.750);

INSERT INTO hash_entries (table_id, key_text, value_text, hash_value, bucket_index)
SELECT table_id, sample.key_text, sample.value_text, 0, 0
FROM hash_tables t
CROSS JOIN (
    VALUES
        ('payments@production', '3.4.1'),
        ('identity@production', '2.8.0'),
        ('search@staging', '1.9.2'),
        ('billing@production', '4.1.0'),
        ('payments@staging', '3.5.0-rc1')
) AS sample(key_text, value_text)
WHERE t.table_name = 'service_registry';

-- Deliberately choose keys with identical demonstration hash values.
INSERT INTO hash_entries (table_id, key_text, value_text, hash_value, bucket_index)
SELECT
    t.table_id,
    sample.key_text,
    sample.value_text,
    0,
    0
FROM hash_tables t
CROSS JOIN (
    VALUES
        ('Aa', 'collision-A'),
        ('BB', 'collision-B'),
        ('Aa ', 'collision-C')
) AS sample(key_text, value_text)
WHERE t.table_name = 'collision_lab';

-- Lookup evaluates a bucket and then compares the actual key.
SELECT * FROM record_lookup(
    (SELECT table_id FROM hash_tables
     WHERE table_name = 'service_registry'),
    'payments@production'
);

SELECT * FROM record_lookup(
    (SELECT table_id FROM hash_tables
     WHERE table_name = 'service_registry'),
    'unknown@production'
);

-- Bucket occupancy includes empty buckets, making load distribution visible.
SELECT table_name, bucket_index, entries_in_bucket
FROM bucket_occupancy
ORDER BY table_name, bucket_index;

SELECT *
FROM bucket_statistics
ORDER BY table_name;

-- Resizing changes bucket placement but does not change logical entries.
SELECT resize_hash_table(
    (SELECT table_id FROM hash_tables
     WHERE table_name = 'service_registry'),
    16
);

SELECT *
FROM bucket_statistics
WHERE table_name = 'service_registry';

-- Upsert updates an existing key rather than creating a duplicate.
INSERT INTO hash_entries (table_id, key_text, value_text, hash_value, bucket_index)
VALUES (
    (SELECT table_id FROM hash_tables
     WHERE table_name = 'service_registry'),
    'payments@production',
    '3.4.2',
    0,
    0
)
ON CONFLICT (table_id, key_text)
DO UPDATE SET value_text = EXCLUDED.value_text;

SELECT key_text, value_text, hash_value, bucket_index
FROM hash_entries
WHERE table_id = (
    SELECT table_id FROM hash_tables
    WHERE table_name = 'service_registry'
)
ORDER BY key_text;

-- DELETE decrements the entry count through the trigger.
DELETE FROM hash_entries
WHERE table_id = (
    SELECT table_id FROM hash_tables
    WHERE table_name = 'service_registry'
)
AND key_text = 'payments@staging';

SELECT table_name, entry_count, bucket_count
FROM hash_tables
ORDER BY table_name;

SELECT operation, found, COUNT(*) AS event_count,
       AVG(examined_entries)::NUMERIC(10, 2) AS average_bucket_scan
FROM lookup_events
GROUP BY operation, found
ORDER BY operation, found;

-- Demonstrate transactional rollback without leaving an invalid entry behind.
SAVEPOINT before_invalid_insert;

DO $$
BEGIN
    BEGIN
        INSERT INTO hash_entries (
            table_id, key_text, value_text, hash_value, bucket_index
        )
        VALUES (
            (SELECT table_id FROM hash_tables
             WHERE table_name = 'service_registry'),
            'payments@production',
            'duplicate',
            0,
            0
        );
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Duplicate key correctly rejected by unique constraint';
    END;
END;
$$;

ROLLBACK TO SAVEPOINT before_invalid_insert;

COMMIT;
