-- ============================================================
-- FLOYD-WARSHALL ALGORITHM
-- PostgreSQL All-Pairs Shortest Paths Implementation
--
-- Features:
--   Directed weighted graphs
--   Vertex and edge management
--   Dynamic programming
--   Intermediate vertex processing
--   Shortest-distance matrix
--   Negative edge weights
--   Negative cycle detection
--   Path reconstruction
--   Relational integrity
--   Reporting and validation
--
-- PostgreSQL 14+
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    directed BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vertices (
    graph_id BIGINT NOT NULL REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    vertex_id INTEGER NOT NULL CHECK (vertex_id >= 0),

    vertex_name VARCHAR(150) NOT NULL,

    PRIMARY KEY (graph_id, vertex_id),

    UNIQUE (graph_id, vertex_name)
);

CREATE TABLE IF NOT EXISTS edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,

    weight DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (
        weight > '-Infinity'::DOUBLE PRECISION
        AND weight < 'Infinity'::DOUBLE PRECISION
    )
);

CREATE INDEX IF NOT EXISTS idx_edges_graph_source
    ON edges(graph_id, source_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph_destination
    ON edges(graph_id, destination_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph_source_destination
    ON edges(graph_id, source_id, destination_id);

-- ------------------------------------------------------------
-- 2. COMPUTED SHORTEST-PATH RESULTS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS all_pairs_shortest_paths (
    graph_id BIGINT NOT NULL,

    source_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,

    distance DOUBLE PRECISION NOT NULL,

    next_vertex INTEGER,

    computed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (graph_id, source_id, destination_id),

    FOREIGN KEY (graph_id, source_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, next_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_shortest_paths_destination
    ON all_pairs_shortest_paths(graph_id, destination_id);

CREATE INDEX IF NOT EXISTS idx_shortest_paths_distance
    ON all_pairs_shortest_paths(graph_id, distance);

-- ------------------------------------------------------------
-- 3. GRAPH REGISTRATION
-- ------------------------------------------------------------

INSERT INTO graphs (graph_name, directed)
VALUES ('transport_network', TRUE)
ON CONFLICT (graph_name) DO NOTHING;

INSERT INTO graphs (graph_name, directed)
VALUES ('negative_edge_test', TRUE)
ON CONFLICT (graph_name) DO NOTHING;

INSERT INTO graphs (graph_name, directed)
VALUES ('negative_cycle_test', TRUE)
ON CONFLICT (graph_name) DO NOTHING;

-- ------------------------------------------------------------
-- 4. VERTEX REGISTRATION
-- ------------------------------------------------------------

INSERT INTO vertices (graph_id, vertex_id, vertex_name)
SELECT g.graph_id, v.vertex_id, v.vertex_name
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 'A'),
        (1, 'B'),
        (2, 'C'),
        (3, 'D'),
        (4, 'E')
) AS v(vertex_id, vertex_name)
WHERE g.graph_name = 'transport_network'
ON CONFLICT DO NOTHING;

INSERT INTO vertices (graph_id, vertex_id, vertex_name)
SELECT g.graph_id, v.vertex_id, v.vertex_name
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 'Source'),
        (1, 'Intermediate'),
        (2, 'Destination')
) AS v(vertex_id, vertex_name)
WHERE g.graph_name = 'negative_edge_test'
ON CONFLICT DO NOTHING;

INSERT INTO vertices (graph_id, vertex_id, vertex_name)
SELECT g.graph_id, v.vertex_id, v.vertex_name
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 'CycleA'),
        (1, 'CycleB'),
        (2, 'CycleC')
) AS v(vertex_id, vertex_name)
WHERE g.graph_name = 'negative_cycle_test'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 5. EDGE REGISTRATION
-- ------------------------------------------------------------

INSERT INTO edges (
    graph_id,
    source_id,
    destination_id,
    weight
)
SELECT
    g.graph_id,
    e.source_id,
    e.destination_id,
    e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 3.0::DOUBLE PRECISION),
        (0, 2, 8.0),
        (0, 4, -4.0),
        (1, 3, 1.0),
        (1, 4, 7.0),
        (2, 1, 4.0),
        (3, 0, 2.0),
        (3, 2, -5.0),
        (4, 3, 6.0)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'transport_network'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_id = e.source_id
      AND existing.destination_id = e.destination_id
);

INSERT INTO edges (
    graph_id,
    source_id,
    destination_id,
    weight
)
SELECT
    g.graph_id,
    e.source_id,
    e.destination_id,
    e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 4.0::DOUBLE PRECISION),
        (1, 2, -6.0),
        (0, 2, 3.0)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'negative_edge_test'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_id = e.source_id
      AND existing.destination_id = e.destination_id
);

INSERT INTO edges (
    graph_id,
    source_id,
    destination_id,
    weight
)
SELECT
    g.graph_id,
    e.source_id,
    e.destination_id,
    e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 1.0::DOUBLE PRECISION),
        (1, 2, -3.0),
        (2, 0, 1.0)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'negative_cycle_test'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_id = e.source_id
      AND existing.destination_id = e.destination_id
);

-- ------------------------------------------------------------
-- 6. EDGE VALIDATION VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW edge_validation_report AS
SELECT
    g.graph_name,
    e.source_id,
    source_vertex.vertex_name AS source_name,
    e.destination_id,
    destination_vertex.vertex_name AS destination_name,
    e.weight,
    CASE
        WHEN e.weight < 0 THEN 'NEGATIVE_WEIGHT'
        WHEN e.weight = 0 THEN 'ZERO_WEIGHT'
        ELSE 'POSITIVE_WEIGHT'
    END AS weight_category
FROM edges e
JOIN graphs g
    ON g.graph_id = e.graph_id
JOIN vertices source_vertex
    ON source_vertex.graph_id = e.graph_id
   AND source_vertex.vertex_id = e.source_id
JOIN vertices destination_vertex
    ON destination_vertex.graph_id = e.graph_id
   AND destination_vertex.vertex_id = e.destination_id;

-- ------------------------------------------------------------
-- 7. FLOYD-WARSHALL COMPUTATION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE compute_all_pairs(
    p_graph_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
    v_k INTEGER;
    v_has_negative_cycle BOOLEAN;
BEGIN

    IF NOT EXISTS (
        SELECT 1
        FROM graphs
        WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Graph % does not exist.', p_graph_id;
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM vertices
    WHERE graph_id = p_graph_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'Graph contains no vertices.';
    END IF;

    -- The implementation uses vertex identifiers from 0 to V-1.
    -- This ensures the intermediate-vertex loop is deterministic.
    IF (
        SELECT MIN(vertex_id)
        FROM vertices
        WHERE graph_id = p_graph_id
    ) <> 0
    OR (
        SELECT MAX(vertex_id)
        FROM vertices
        WHERE graph_id = p_graph_id
    ) <> v_count - 1
    THEN
        RAISE EXCEPTION
            'Vertex identifiers must be contiguous from 0 to V-1.';
    END IF;

    -- Session-local distance matrix.
    CREATE TEMP TABLE IF NOT EXISTS fw_distance (
        source_id INTEGER NOT NULL,
        destination_id INTEGER NOT NULL,
        distance DOUBLE PRECISION NOT NULL,
        next_vertex INTEGER,
        PRIMARY KEY (source_id, destination_id)
    ) ON COMMIT DROP;

    TRUNCATE TABLE fw_distance;

    -- Initialize every source-destination pair.
    INSERT INTO fw_distance (
        source_id,
        destination_id,
        distance,
        next_vertex
    )
    SELECT
        source.vertex_id,
        destination.vertex_id,
        CASE
            WHEN source.vertex_id = destination.vertex_id THEN 0
            ELSE 'Infinity'::DOUBLE PRECISION
        END,
        CASE
            WHEN source.vertex_id = destination.vertex_id
            THEN source.vertex_id
            ELSE NULL
        END
    FROM vertices source
    CROSS JOIN vertices destination
    WHERE source.graph_id = p_graph_id
      AND destination.graph_id = p_graph_id;

    -- Initialize direct edges.
    -- MIN handles multiple edges between the same vertices.
    WITH minimum_edges AS (
        SELECT
            source_id,
            destination_id,
            MIN(weight) AS minimum_weight
        FROM edges
        WHERE graph_id = p_graph_id
        GROUP BY source_id, destination_id
    )
    UPDATE fw_distance d
    SET
        distance = e.minimum_weight,
        next_vertex = e.destination_id
    FROM minimum_edges e
    WHERE d.source_id = e.source_id
      AND d.destination_id = e.destination_id
      AND e.minimum_weight < d.distance;

    -- Floyd-Warshall dynamic programming.
    --
    -- At iteration k, paths may use vertices 0 through k
    -- as intermediate vertices.
    --
    -- D(i,j) = MIN(D(i,j), D(i,k) + D(k,j))

    FOR v_k IN 0..v_count - 1 LOOP

        UPDATE fw_distance AS current
        SET
            distance = left_path.distance + right_path.distance,
            next_vertex = left_path.next_vertex
        FROM
            fw_distance AS left_path,
            fw_distance AS right_path
        WHERE current.source_id = left_path.source_id
          AND left_path.destination_id = v_k
          AND right_path.source_id = v_k
          AND right_path.destination_id = current.destination_id
          AND left_path.distance < 'Infinity'::DOUBLE PRECISION
          AND right_path.distance < 'Infinity'::DOUBLE PRECISION
          AND left_path.distance + right_path.distance
              < current.distance;

    END LOOP;

    -- A negative diagonal indicates a negative-weight cycle.
    SELECT EXISTS (
        SELECT 1
        FROM fw_distance
        WHERE source_id = destination_id
          AND distance < 0
    )
    INTO v_has_negative_cycle;

    IF v_has_negative_cycle THEN
        RAISE EXCEPTION
            'Negative-weight cycle detected. Results not published.';
    END IF;

    -- Publish only validated results.
    DELETE FROM all_pairs_shortest_paths
    WHERE graph_id = p_graph_id;

    INSERT INTO all_pairs_shortest_paths (
        graph_id,
        source_id,
        destination_id,
        distance,
        next_vertex
    )
    SELECT
        p_graph_id,
        source_id,
        destination_id,
        distance,
        next_vertex
    FROM fw_distance;

END;
$$;

-- ------------------------------------------------------------
-- 8. COMPUTE RESULTS
-- ------------------------------------------------------------

SELECT graph_id, graph_name
FROM graphs
ORDER BY graph_id;

CALL compute_all_pairs(
    (SELECT graph_id
     FROM graphs
     WHERE graph_name = 'transport_network')
);

CALL compute_all_pairs(
    (SELECT graph_id
     FROM graphs
     WHERE graph_name = 'negative_edge_test')
);

-- The negative-cycle graph is intentionally excluded from
-- successful computation because it must raise an exception.
-- Run its validation independently using a savepoint.

-- ------------------------------------------------------------
-- 9. SHORTEST-DISTANCE REPORT
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW shortest_distance_report AS
SELECT
    g.graph_name,
    source_vertex.vertex_name AS source,
    destination_vertex.vertex_name AS destination,
    result.distance,
    CASE
        WHEN result.distance = 'Infinity'::DOUBLE PRECISION
            THEN 'UNREACHABLE'
        ELSE 'REACHABLE'
    END AS reachability
FROM all_pairs_shortest_paths result
JOIN graphs g
    ON g.graph_id = result.graph_id
JOIN vertices source_vertex
    ON source_vertex.graph_id = result.graph_id
   AND source_vertex.vertex_id = result.source_id
JOIN vertices destination_vertex
    ON destination_vertex.graph_id = result.graph_id
   AND destination_vertex.vertex_id = result.destination_id;

-- ------------------------------------------------------------
-- 10. PATH RECONSTRUCTION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_shortest_path(
    p_graph_id BIGINT,
    p_source INTEGER,
    p_destination INTEGER
)
RETURNS TABLE (
    step_number INTEGER,
    vertex_id INTEGER,
    vertex_name VARCHAR(150)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current INTEGER;
    v_next INTEGER;
    v_step INTEGER := 0;
    v_distance DOUBLE PRECISION;
    v_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO v_count
    FROM vertices
    WHERE graph_id = p_graph_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'Graph does not exist or has no vertices.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_source
    ) OR NOT EXISTS (
        SELECT 1 FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_destination
    ) THEN
        RAISE EXCEPTION 'Invalid source or destination.';
    END IF;

    SELECT distance
    INTO v_distance
    FROM all_pairs_shortest_paths
    WHERE graph_id = p_graph_id
      AND source_id = p_source
      AND destination_id = p_destination;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Shortest paths have not been computed for this graph.';
    END IF;

    IF v_distance = 'Infinity'::DOUBLE PRECISION THEN
        RETURN;
    END IF;

    v_current := p_source;

    LOOP

        RETURN QUERY
        SELECT
            v_step,
            vertex.vertex_id,
            vertex.vertex_name
        FROM vertices vertex
        WHERE vertex.graph_id = p_graph_id
          AND vertex.vertex_id = v_current;

        EXIT WHEN v_current = p_destination;

        SELECT next_vertex
        INTO v_next
        FROM all_pairs_shortest_paths
        WHERE graph_id = p_graph_id
          AND source_id = v_current
          AND destination_id = p_destination;

        IF v_next IS NULL THEN
            RAISE EXCEPTION 'Invalid next-hop state.';
        END IF;

        v_current := v_next;
        v_step := v_step + 1;

        IF v_step >= v_count THEN
            RAISE EXCEPTION
                'Path reconstruction exceeded vertex count.';
        END IF;

    END LOOP;

END;
$$;

-- ------------------------------------------------------------
-- 11. RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- Complete shortest-distance matrix.
SELECT
    source_id,
    destination_id,
    distance
FROM all_pairs_shortest_paths
WHERE graph_id = (
    SELECT graph_id
    FROM graphs
    WHERE graph_name = 'transport_network'
)
ORDER BY source_id, destination_id;

-- Named route report.
SELECT *
FROM shortest_distance_report
WHERE graph_name = 'transport_network'
ORDER BY source, destination;

-- ------------------------------------------------------------
-- 12. PATH RECONSTRUCTION QUERY
-- ------------------------------------------------------------

SELECT *
FROM get_shortest_path(
    (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'transport_network'
    ),
    0,
    2
);

-- ------------------------------------------------------------
-- 13. AGGREGATION AND REPORTING
-- ------------------------------------------------------------

SELECT
    graph_name,
    COUNT(*) AS total_pairs,
    COUNT(*) FILTER (
        WHERE distance < 'Infinity'::DOUBLE PRECISION
    ) AS reachable_pairs,
    COUNT(*) FILTER (
        WHERE distance = 'Infinity'::DOUBLE PRECISION
    ) AS unreachable_pairs,
    MIN(distance) FILTER (
        WHERE distance < 'Infinity'::DOUBLE PRECISION
    ) AS minimum_distance,
    MAX(distance) FILTER (
        WHERE distance < 'Infinity'::DOUBLE PRECISION
    ) AS maximum_distance
FROM shortest_distance_report
GROUP BY graph_name;

-- ------------------------------------------------------------
-- 14. NEGATIVE EDGE VALIDATION
-- ------------------------------------------------------------

SELECT *
FROM edge_validation_report
ORDER BY graph_name, source_id, destination_id;

-- ------------------------------------------------------------
-- 15. NEGATIVE CYCLE FAILURE TEST
-- ------------------------------------------------------------

SAVEPOINT negative_cycle_validation;

DO $$
DECLARE
    v_graph_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graphs
    WHERE graph_name = 'negative_cycle_test';

    BEGIN
        CALL compute_all_pairs(v_graph_id);

        RAISE NOTICE 'Unexpected result: negative cycle not detected.';

    EXCEPTION
        WHEN raise_exception THEN
            RAISE NOTICE
                'Expected negative-cycle validation: %',
                SQLERRM;
    END;
END;
$$;

ROLLBACK TO SAVEPOINT negative_cycle_validation;

RELEASE SAVEPOINT negative_cycle_validation;

-- ------------------------------------------------------------
-- 16. TRANSACTIONAL INTEGRITY
-- ------------------------------------------------------------

-- Graph modifications and shortest-path computation should
-- be performed within a controlled transaction.
--
-- If an edge changes, previously calculated shortest paths
-- must not be treated as current.
--
-- Example of explicit invalidation after an edge modification:

-- DELETE FROM all_pairs_shortest_paths
-- WHERE graph_id = (
--     SELECT graph_id
--     FROM graphs
--     WHERE graph_name = 'transport_network'
-- );

-- The caller must recompute shortest paths after modifications.

COMMIT;
