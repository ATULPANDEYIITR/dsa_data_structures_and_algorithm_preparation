-- PostgreSQL 15+
-- Monotonic-stack study: store ordered observations and persist next-element
-- answers for reproducible analysis. A recursive CTE computes the reference
-- answer; a windowed query exposes nearest qualifying future observations.
-- For high-volume workloads, compute the full monotonic stack in an
-- application or a dedicated procedural routine rather than repeated scans.

BEGIN;

DROP VIEW IF EXISTS next_smaller_reading;
DROP VIEW IF EXISTS next_greater_reading;
DROP TABLE IF EXISTS monotonic_query_result;
DROP TABLE IF EXISTS sensor_reading;
DROP TABLE IF EXISTS sensor;

CREATE TABLE sensor (
    sensor_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_name     TEXT NOT NULL UNIQUE,
    measurement_unit TEXT NOT NULL,
    CHECK (btrim(sensor_name) <> ''),
    CHECK (btrim(measurement_unit) <> '')
);

CREATE TABLE sensor_reading (
    reading_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id       BIGINT NOT NULL REFERENCES sensor(sensor_id)
                    ON DELETE CASCADE,
    observed_at     TIMESTAMPTZ NOT NULL,
    sequence_no     INTEGER NOT NULL CHECK (sequence_no >= 0),
    reading_value   NUMERIC(14, 4) NOT NULL,
    UNIQUE (sensor_id, sequence_no),
    UNIQUE (sensor_id, observed_at)
);

-- The index supports ordered scans per sensor and makes future-reading
-- lookups efficient when a query is restricted to one sensor.
CREATE INDEX sensor_reading_order_idx
    ON sensor_reading (sensor_id, sequence_no, reading_value);

CREATE TABLE monotonic_query_result (
    result_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id       BIGINT NOT NULL REFERENCES sensor(sensor_id)
                    ON DELETE CASCADE,
    source_reading_id BIGINT NOT NULL REFERENCES sensor_reading(reading_id)
                    ON DELETE CASCADE,
    query_kind      TEXT NOT NULL
                    CHECK (query_kind IN ('NEXT_GREATER', 'NEXT_SMALLER')),
    target_reading_id BIGINT REFERENCES sensor_reading(reading_id)
                    ON DELETE SET NULL,
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_reading_id, query_kind)
);

INSERT INTO sensor (sensor_name, measurement_unit)
VALUES
    ('compressor-pressure', 'kPa'),
    ('cooling-temperature', 'Celsius');

INSERT INTO sensor_reading
    (sensor_id, observed_at, sequence_no, reading_value)
SELECT s.sensor_id,
       TIMESTAMPTZ '2026-10-12 09:00:00+05:30'
           + sample.sequence_no * INTERVAL '5 minutes',
       sample.sequence_no,
       sample.reading_value
FROM sensor AS s
JOIN (
    VALUES
        ('compressor-pressure', 0, 42.0::NUMERIC),
        ('compressor-pressure', 1, 38.0::NUMERIC),
        ('compressor-pressure', 2, 38.0::NUMERIC),
        ('compressor-pressure', 3, 51.0::NUMERIC),
        ('compressor-pressure', 4, 45.0::NUMERIC),
        ('compressor-pressure', 5, 60.0::NUMERIC),
        ('compressor-pressure', 6, 33.0::NUMERIC),
        ('cooling-temperature', 0, 18.0::NUMERIC),
        ('cooling-temperature', 1, 20.0::NUMERIC),
        ('cooling-temperature', 2, 19.0::NUMERIC),
        ('cooling-temperature', 3, 24.0::NUMERIC)
) AS sample(sensor_name, sequence_no, reading_value)
    ON sample.sensor_name = s.sensor_name;

-- DISTINCT ON chooses the first qualifying future observation because
-- sequence_no is ordered ascending. Strict comparisons intentionally do
-- not treat duplicate values as greater or smaller.
CREATE VIEW next_greater_reading AS
SELECT
    source.reading_id AS source_reading_id,
    source.sensor_id,
    source.sequence_no AS source_sequence,
    source.reading_value AS source_value,
    target.reading_id AS target_reading_id,
    target.sequence_no AS target_sequence,
    target.reading_value AS target_value
FROM sensor_reading AS source
LEFT JOIN LATERAL (
    SELECT candidate.reading_id,
           candidate.sequence_no,
           candidate.reading_value
    FROM sensor_reading AS candidate
    WHERE candidate.sensor_id = source.sensor_id
      AND candidate.sequence_no > source.sequence_no
      AND candidate.reading_value > source.reading_value
    ORDER BY candidate.sequence_no
    LIMIT 1
) AS target ON TRUE;

CREATE VIEW next_smaller_reading AS
SELECT
    source.reading_id AS source_reading_id,
    source.sensor_id,
    source.sequence_no AS source_sequence,
    source.reading_value AS source_value,
    target.reading_id AS target_reading_id,
    target.sequence_no AS target_sequence,
    target.reading_value AS target_value
FROM sensor_reading AS source
LEFT JOIN LATERAL (
    SELECT candidate.reading_id,
           candidate.sequence_no,
           candidate.reading_value
    FROM sensor_reading AS candidate
    WHERE candidate.sensor_id = source.sensor_id
      AND candidate.sequence_no > source.sequence_no
      AND candidate.reading_value < source.reading_value
    ORDER BY candidate.sequence_no
    LIMIT 1
) AS target ON TRUE;

-- Store the derived results in one transaction. The database constraints
-- ensure each source has at most one stored answer of each query type.
INSERT INTO monotonic_query_result
    (sensor_id, source_reading_id, query_kind, target_reading_id)
SELECT sensor_id, source_reading_id, 'NEXT_GREATER', target_reading_id
FROM next_greater_reading
ON CONFLICT (source_reading_id, query_kind)
DO UPDATE SET
    target_reading_id = EXCLUDED.target_reading_id,
    computed_at = CURRENT_TIMESTAMP;

INSERT INTO monotonic_query_result
    (sensor_id, source_reading_id, query_kind, target_reading_id)
SELECT sensor_id, source_reading_id, 'NEXT_SMALLER', target_reading_id
FROM next_smaller_reading
ON CONFLICT (source_reading_id, query_kind)
DO UPDATE SET
    target_reading_id = EXCLUDED.target_reading_id,
    computed_at = CURRENT_TIMESTAMP;

COMMIT;

-- Inspect next-greater answers. A NULL target means no qualifying future
-- reading exists.
SELECT
    s.sensor_name,
    source.sequence_no AS source_sequence,
    source.reading_value AS source_value,
    target.sequence_no AS target_sequence,
    target.reading_value AS target_value
FROM next_greater_reading AS result
JOIN sensor AS s USING (sensor_id)
JOIN sensor_reading AS source
    ON source.reading_id = result.source_reading_id
LEFT JOIN sensor_reading AS target
    ON target.reading_id = result.target_reading_id
ORDER BY s.sensor_name, source.sequence_no;

-- Inspect next-smaller answers independently.
SELECT
    s.sensor_name,
    source.sequence_no AS source_sequence,
    source.reading_value AS source_value,
    target.sequence_no AS target_sequence,
    target.reading_value AS target_value
FROM next_smaller_reading AS result
JOIN sensor AS s USING (sensor_id)
JOIN sensor_reading AS source
    ON source.reading_id = result.source_reading_id
LEFT JOIN sensor_reading AS target
    ON target.reading_id = result.target_reading_id
ORDER BY s.sensor_name, source.sequence_no;

-- The query below computes the maximum value among observations that are
-- strictly greater than the current observation, for diagnostic comparison.
-- It is not a next-greater query: it does not preserve nearest-position
-- semantics, which is why ordering by sequence_no matters.
SELECT
    source.sensor_id,
    source.sequence_no,
    source.reading_value,
    MIN(candidate.sequence_no) FILTER (
        WHERE candidate.reading_value > source.reading_value
    ) AS first_greater_sequence
FROM sensor_reading AS source
LEFT JOIN sensor_reading AS candidate
    ON candidate.sensor_id = source.sensor_id
   AND candidate.sequence_no > source.sequence_no
GROUP BY source.sensor_id, source.sequence_no, source.reading_value
ORDER BY source.sensor_id, source.sequence_no;

-- Edge-case audit: equal values do not resolve strict next-greater or
-- next-smaller queries. This query identifies duplicate adjacent readings.
SELECT
    current.sensor_id,
    current.sequence_no,
    current.reading_value,
    following.sequence_no AS following_sequence
FROM sensor_reading AS current
JOIN sensor_reading AS following
    ON following.sensor_id = current.sensor_id
   AND following.sequence_no = current.sequence_no + 1
   AND following.reading_value = current.reading_value
ORDER BY current.sensor_id, current.sequence_no;

-- Database-level integrity demonstration. The invalid insert is isolated
-- in a PL/pgSQL exception block so the remainder of the script stays usable.
DO $$
BEGIN
    BEGIN
        INSERT INTO sensor_reading
            (sensor_id, observed_at, sequence_no, reading_value)
        VALUES
            (
                (SELECT sensor_id FROM sensor
                 WHERE sensor_name = 'compressor-pressure'),
                TIMESTAMPTZ '2026-10-12 12:00:00+05:30',
                -1,
                99.0
            );

        RAISE EXCEPTION
            'Expected CHECK constraint to reject a negative sequence number';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Expected behavior: negative sequence number rejected';
    END;
END;
$$;

-- The lateral-query views are clear reference implementations but may
-- perform repeated searches. A procedural monotonic stack processes each
-- ordered sensor stream in O(n) time, whereas these reference queries can
-- require O(n^2) comparisons without a suitable execution plan.
