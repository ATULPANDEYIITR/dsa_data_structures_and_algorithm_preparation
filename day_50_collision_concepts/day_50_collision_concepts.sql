-- PostgreSQL 14+
-- Collision concepts: hash distribution, chaining, open addressing,
-- load-factor measurements, and reproducible performance analysis.
-- This schema models the logical behavior of a hash table; PostgreSQL's
-- native hash indexes have implementation details beyond this simulation.

BEGIN;

DROP VIEW IF EXISTS hash_collision_report;
DROP TABLE IF EXISTS hash_operation_log CASCADE;
DROP TABLE IF EXISTS hash_entries CASCADE;
DROP TABLE IF EXISTS hash_buckets CASCADE;
DROP TABLE IF EXISTS hash_table_configs CASCADE;

CREATE TABLE hash_table_configs (
    table_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name TEXT NOT NULL UNIQUE,
    resolution_strategy TEXT NOT NULL
        CHECK (resolution_strategy IN ('separate_chaining', 'open_addressing')),
    capacity INTEGER NOT NULL CHECK (capacity >= 4),
    maximum_load_factor NUMERIC(5,4) NOT NULL
        CHECK (maximum_load_factor > 0 AND maximum_load_factor < 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hash_buckets (
    table_id BIGINT NOT NULL REFERENCES hash_table_configs(table_id)
        ON DELETE CASCADE,
    bucket_index INTEGER NOT NULL CHECK (bucket_index >= 0),
    occupied BOOLEAN NOT NULL DEFAULT FALSE,
    tombstone BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (table_id, bucket_index),
    CHECK (NOT (occupied AND tombstone))
);

CREATE TABLE hash_entries (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_id BIGINT NOT NULL REFERENCES hash_table_configs(table_id)
        ON DELETE CASCADE,
    entry_key TEXT NOT NULL,
    entry_value JSONB NOT NULL,
    hash_code BIGINT NOT NULL,
    bucket_index INTEGER NOT NULL CHECK (bucket_index >= 0),
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (table_id, entry_key),
    FOREIGN KEY (table_id, bucket_index)
        REFERENCES hash_buckets(table_id, bucket_index)
        ON DELETE RESTRICT
);

CREATE INDEX idx_hash_entries_bucket
    ON hash_entries (table_id, bucket_index);

CREATE INDEX idx_hash_entries_hash
    ON hash_entries (table_id, hash_code);

CREATE TABLE hash_operation_log (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_id BIGINT NOT NULL REFERENCES hash_table_configs(table_id)
        ON DELETE CASCADE,
    operation_type TEXT NOT NULL
        CHECK (operation_type IN ('insert', 'lookup', 'delete', 'resize')),
    entry_key TEXT,
    probes INTEGER NOT NULL DEFAULT 0 CHECK (probes >= 0),
    collision_count INTEGER NOT NULL DEFAULT 0 CHECK (collision_count >= 0),
    succeeded BOOLEAN NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- The stable hash is for reproducible analysis, not cryptographic use.
-- It avoids dependence on session-specific hash functions.
CREATE OR REPLACE FUNCTION demo_hash_key(p_key TEXT)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result BIGINT := 0;
    position INTEGER;
BEGIN
    IF length(p_key) > 10000 THEN
        RAISE EXCEPTION 'Key exceeds the 10000-character limit';
    END IF;

    FOR position IN 1..length(p_key) LOOP
        result := mod(result * 31 + ascii(substr(p_key, position, 1)), 2147483647);
    END LOOP;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION create_hash_table(
    p_name TEXT,
    p_strategy TEXT,
    p_capacity INTEGER,
    p_threshold NUMERIC
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_table_id BIGINT;
    bucket_number INTEGER;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Table name cannot be empty';
    END IF;

    IF p_capacity < 4 THEN
        RAISE EXCEPTION 'Capacity must be at least four';
    END IF;

    IF p_strategy NOT IN ('separate_chaining', 'open_addressing') THEN
        RAISE EXCEPTION 'Unsupported collision-resolution strategy';
    END IF;

    IF p_threshold <= 0 OR p_threshold >= 1 THEN
        RAISE EXCEPTION 'Load-factor threshold must be between zero and one';
    END IF;

    INSERT INTO hash_table_configs (
        table_name, resolution_strategy, capacity, maximum_load_factor
    )
    VALUES (p_name, p_strategy, p_capacity, p_threshold)
    RETURNING table_id INTO new_table_id;

    FOR bucket_number IN 0..p_capacity - 1 LOOP
        INSERT INTO hash_buckets (table_id, bucket_index)
        VALUES (new_table_id, bucket_number);
    END LOOP;

    RETURN new_table_id;
END;
$$;

CREATE OR REPLACE FUNCTION insert_hash_entry(
    p_table_id BIGINT,
    p_key TEXT,
    p_value JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    config hash_table_configs%ROWTYPE;
    key_hash BIGINT;
    target_bucket INTEGER;
    occupied_count INTEGER;
    bucket_occupancy INTEGER;
    existing_entry BIGINT;
    collision_count INTEGER := 0;
    probe_count INTEGER := 0;
    attempt INTEGER;
BEGIN
    IF p_key IS NULL OR length(p_key) = 0 THEN
        RAISE EXCEPTION 'Key cannot be empty';
    END IF;
    IF length(p_key) > 10000 THEN
        RAISE EXCEPTION 'Key exceeds the 10000-character limit';
    END IF;
    IF p_value IS NULL THEN
        RAISE EXCEPTION 'Value cannot be SQL NULL';
    END IF;

    SELECT * INTO config
    FROM hash_table_configs
    WHERE table_id = p_table_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown hash table ID %', p_table_id;
    END IF;

    SELECT entry_id INTO existing_entry
    FROM hash_entries
    WHERE table_id = p_table_id AND entry_key = p_key;

    IF FOUND THEN
        UPDATE hash_entries
        SET entry_value = p_value,
            hash_code = demo_hash_key(p_key)
        WHERE entry_id = existing_entry;

        INSERT INTO hash_operation_log (
            table_id, operation_type, entry_key, probes, succeeded
        ) VALUES (p_table_id, 'insert', p_key, 1, TRUE);

        RETURN existing_entry;
    END IF;

    key_hash := demo_hash_key(p_key);
    target_bucket := mod(key_hash, config.capacity)::INTEGER;

    IF config.resolution_strategy = 'separate_chaining' THEN
        SELECT count(*) INTO bucket_occupancy
        FROM hash_entries
        WHERE table_id = p_table_id AND bucket_index = target_bucket;

        probe_count := bucket_occupancy;
        collision_count := CASE WHEN bucket_occupancy > 0 THEN 1 ELSE 0 END;
    ELSE
        -- Linear probing checks successive buckets until it finds an empty
        -- slot. A full-cycle search terminates rather than looping forever.
        target_bucket := -1;

        FOR attempt IN 0..config.capacity - 1 LOOP
            DECLARE
                candidate INTEGER := mod(
                    mod(key_hash, config.capacity) + attempt,
                    config.capacity
                )::INTEGER;
                bucket_row hash_buckets%ROWTYPE;
            BEGIN
                SELECT * INTO bucket_row
                FROM hash_buckets
                WHERE table_id = p_table_id AND bucket_index = candidate
                FOR UPDATE;

                probe_count := probe_count + 1;

                IF NOT bucket_row.occupied OR bucket_row.tombstone THEN
                    target_bucket := candidate;
                    EXIT;
                END IF;

                collision_count := collision_count + 1;
            END;
        END LOOP;

        IF target_bucket < 0 THEN
            RAISE EXCEPTION 'Open-addressing table is full';
        END IF;
    END IF;

    SELECT count(*) INTO occupied_count
    FROM hash_entries
    WHERE table_id = p_table_id;

    -- Chaining grows when its entry-to-bucket ratio crosses the configured
    -- threshold. This SQL model records that condition; it does not silently
    -- change the capacity and redistribute existing entries.
    IF config.resolution_strategy = 'separate_chaining'
       AND (occupied_count + 1)::NUMERIC / config.capacity
           > config.maximum_load_factor THEN
        RAISE NOTICE 'Load factor will exceed configured threshold for table %',
            config.table_name;
    END IF;

    INSERT INTO hash_entries (
        table_id, entry_key, entry_value, hash_code, bucket_index
    )
    VALUES (p_table_id, p_key, p_value, key_hash, target_bucket)
    RETURNING entry_id INTO existing_entry;

    UPDATE hash_buckets
    SET occupied = TRUE, tombstone = FALSE
    WHERE table_id = p_table_id AND bucket_index = target_bucket;

    INSERT INTO hash_operation_log (
        table_id, operation_type, entry_key, probes,
        collision_count, succeeded
    )
    VALUES (
        p_table_id, 'insert', p_key, probe_count,
        collision_count, TRUE
    );

    RETURN existing_entry;
END;
$$;

CREATE OR REPLACE FUNCTION lookup_hash_entry(
    p_table_id BIGINT,
    p_key TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    result JSONB;
    entry_hash BIGINT;
    config hash_table_configs%ROWTYPE;
    start_bucket INTEGER;
    attempt INTEGER;
    target_bucket INTEGER;
    probes INTEGER := 0;
    collisions INTEGER := 0;
    found_entry BOOLEAN := FALSE;
BEGIN
    SELECT * INTO config
    FROM hash_table_configs
    WHERE table_id = p_table_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown hash table ID %', p_table_id;
    END IF;

    entry_hash := demo_hash_key(p_key);
    start_bucket := mod(entry_hash, config.capacity)::INTEGER;

    IF config.resolution_strategy = 'separate_chaining' THEN
        SELECT entry_value INTO result
        FROM hash_entries
        WHERE table_id = p_table_id
          AND bucket_index = start_bucket
          AND entry_key = p_key;

        probes := 1;

        SELECT count(*) INTO collisions
        FROM hash_entries
        WHERE table_id = p_table_id
          AND bucket_index = start_bucket
          AND entry_key <> p_key;
        found_entry := result IS NOT NULL;
    ELSE
        FOR attempt IN 0..config.capacity - 1 LOOP
            target_bucket := mod(start_bucket + attempt, config.capacity);

            SELECT entry_value INTO result
            FROM hash_entries
            WHERE table_id = p_table_id
              AND bucket_index = target_bucket
              AND entry_key = p_key;

            probes := probes + 1;

            IF FOUND THEN
                found_entry := TRUE;
                EXIT;
            END IF;

            SELECT EXISTS (
                SELECT 1 FROM hash_buckets
                WHERE table_id = p_table_id
                  AND bucket_index = target_bucket
                  AND NOT occupied
                  AND NOT tombstone
            ) INTO found_entry;

            IF found_entry THEN
                found_entry := FALSE;
                EXIT;
            END IF;

            collisions := collisions + 1;
        END LOOP;
    END IF;

    INSERT INTO hash_operation_log (
        table_id, operation_type, entry_key, probes,
        collision_count, succeeded
    )
    VALUES (
        p_table_id, 'lookup', p_key, probes, collisions, found_entry
    );

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION delete_hash_entry(
    p_table_id BIGINT,
    p_key TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    config hash_table_configs%ROWTYPE;
    target_entry hash_entries%ROWTYPE;
    next_entry_exists BOOLEAN;
BEGIN
    SELECT * INTO config
    FROM hash_table_configs
    WHERE table_id = p_table_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown hash table ID %', p_table_id;
    END IF;

    SELECT * INTO target_entry
    FROM hash_entries
    WHERE table_id = p_table_id AND entry_key = p_key
    FOR UPDATE;

    IF NOT FOUND THEN
        INSERT INTO hash_operation_log (
            table_id, operation_type, entry_key, succeeded
        ) VALUES (p_table_id, 'delete', p_key, FALSE);
        RETURN FALSE;
    END IF;

    DELETE FROM hash_entries WHERE entry_id = target_entry.entry_id;

    IF config.resolution_strategy = 'open_addressing' THEN
        -- A tombstone is needed when later keys depend on this probe chain.
        UPDATE hash_buckets
        SET occupied = FALSE, tombstone = TRUE
        WHERE table_id = p_table_id
          AND bucket_index = target_entry.bucket_index;

        SELECT EXISTS (
            SELECT 1 FROM hash_entries
            WHERE table_id = p_table_id
              AND bucket_index = target_entry.bucket_index
        ) INTO next_entry_exists;

        IF next_entry_exists THEN
            RAISE EXCEPTION 'Bucket model violates open-addressing uniqueness';
        END IF;
    ELSE
        UPDATE hash_buckets
        SET occupied = EXISTS (
            SELECT 1 FROM hash_entries
            WHERE table_id = p_table_id
              AND bucket_index = target_entry.bucket_index
        )
        WHERE table_id = p_table_id
          AND bucket_index = target_entry.bucket_index;
    END IF;

    INSERT INTO hash_operation_log (
        table_id, operation_type, entry_key, succeeded
    ) VALUES (p_table_id, 'delete', p_key, TRUE);

    RETURN TRUE;
END;
$$;

CREATE VIEW hash_collision_report AS
SELECT
    config.table_name,
    config.resolution_strategy,
    config.capacity,
    count(entries.entry_id)::BIGINT AS entry_count,
    round(
        count(entries.entry_id)::NUMERIC / config.capacity, 4
    ) AS load_factor,
    count(DISTINCT entries.bucket_index)::BIGINT AS occupied_bucket_count,
    count(entries.entry_id) -
        count(DISTINCT entries.bucket_index) AS excess_chain_entries
FROM hash_table_configs config
LEFT JOIN hash_entries entries ON entries.table_id = config.table_id
GROUP BY config.table_id, config.table_name,
         config.resolution_strategy, config.capacity;

-- Use a larger chaining threshold for a controlled demonstration of collisions.
INSERT INTO hash_table_configs (
    table_name, resolution_strategy, capacity, maximum_load_factor
)
VALUES
    ('inventory_chain', 'separate_chaining', 8, 0.9000),
    ('inventory_probe', 'open_addressing', 8, 0.6500);

INSERT INTO hash_buckets (table_id, bucket_index)
SELECT config.table_id, bucket_number
FROM hash_table_configs config
CROSS JOIN LATERAL generate_series(0, config.capacity - 1) AS bucket_number;

-- These keys intentionally share a bucket under the reproducible hash.
SELECT insert_hash_entry(
    (SELECT table_id FROM hash_table_configs
     WHERE table_name = 'inventory_chain'),
    key_value,
    jsonb_build_object('asset', key_value, 'status', 'active')
)
FROM unnest(ARRAY['1', '9', '17', '25']) AS key_value;

SELECT insert_hash_entry(
    (SELECT table_id FROM hash_table_configs
     WHERE table_name = 'inventory_probe'),
    key_value,
    jsonb_build_object('asset', key_value, 'status', 'active')
)
FROM unnest(ARRAY['1', '9', '17', '25']) AS key_value;

-- Retrieval uses the same logical key and returns a JSON value.
SELECT lookup_hash_entry(
    (SELECT table_id FROM hash_table_configs
     WHERE table_name = 'inventory_chain'),
    '17'
);

-- Deletion preserves a tombstone for open addressing.
SELECT delete_hash_entry(
    (SELECT table_id FROM hash_table_configs
     WHERE table_name = 'inventory_probe'),
    '9'
);

-- A subsequent colliding key can occupy a valid available slot.
SELECT insert_hash_entry(
    (SELECT table_id FROM hash_table_configs
     WHERE table_name = 'inventory_probe'),
    '33',
    '{"asset":"33","status":"active"}'::JSONB
);

-- Capacity and distribution reporting.
SELECT * FROM hash_collision_report ORDER BY table_name;

-- Operation-level performance measurements.
SELECT
    config.table_name,
    log.operation_type,
    count(*) AS operation_count,
    round(avg(log.probes), 2) AS average_probes,
    sum(log.collision_count) AS collisions,
    count(*) FILTER (WHERE NOT log.succeeded) AS unsuccessful_operations
FROM hash_operation_log log
JOIN hash_table_configs config USING (table_id)
GROUP BY config.table_name, log.operation_type
ORDER BY config.table_name, log.operation_type;

-- The unique constraint rejects duplicate logical keys. This exception block
-- demonstrates failure handling without aborting the rest of the script.
DO $$
DECLARE
    chain_id BIGINT;
BEGIN
    SELECT table_id INTO chain_id
    FROM hash_table_configs
    WHERE table_name = 'inventory_chain';

    BEGIN
        INSERT INTO hash_entries (
            table_id, entry_key, entry_value, hash_code, bucket_index
        )
        VALUES (chain_id, '1', '{"asset":"duplicate"}', 1, 1);
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Duplicate key correctly rejected';
    END;
END;
$$;

COMMIT;
