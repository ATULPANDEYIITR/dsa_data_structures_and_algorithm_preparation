/*
===============================================================================
BELLman-FORD SHORTEST PATH ANALYSIS
===============================================================================

Database: PostgreSQL 14+

Implements:
1. Directed weighted graph storage.
2. Vertices and weighted edges.
3. Bellman-Ford shortest-path computation.
4. Edge relaxation.
5. Negative-edge support.
6. Reachable negative-cycle detection.
7. Propagation of negative-cycle influence.
8. Shortest-path reporting.
9. Dijkstra eligibility validation.
10. Graph-analysis history.

Distance values use NUMERIC to avoid fixed-width integer overflow.

A NULL distance represents an unreachable vertex.
A negative-cycle-affected vertex has an undefined shortest distance.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_analysis;

SET search_path TO graph_analysis, public;

-- ---------------------------------------------------------------------------
-- 1. DOMAIN TYPES
-- ---------------------------------------------------------------------------

DO $$
BEGIN
    CREATE TYPE graph_analysis.algorithm_type AS ENUM (
        'BELLMAN_FORD',
        'DIJKSTRA'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

DO $$
BEGIN
    CREATE TYPE graph_analysis.analysis_status AS ENUM (
        'COMPLETED',
        'NEGATIVE_CYCLE_DETECTED',
        'FAILED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

-- ---------------------------------------------------------------------------
-- 2. GRAPH TABLES
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS repositories (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(graph_name)) > 0)
);

CREATE TABLE IF NOT EXISTS vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES repositories(graph_id)
        ON DELETE CASCADE,

    vertex_name VARCHAR(150) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_vertex_name_per_graph
        UNIQUE (graph_id, vertex_name),

    CONSTRAINT uq_vertex_graph_pair
        UNIQUE (graph_id, vertex_id),

    CHECK (length(trim(vertex_name)) > 0)
);

CREATE TABLE IF NOT EXISTS edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex BIGINT NOT NULL,

    destination_vertex BIGINT NOT NULL,

    weight NUMERIC(30, 0) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_edge_source
        FOREIGN KEY (graph_id, source_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_edge_destination
        FOREIGN KEY (graph_id, destination_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (weight BETWEEN -100000000000000000000000000000
                      AND  100000000000000000000000000000)
);

-- Parallel edges are permitted because distinct edges can have
-- different weights between the same pair of vertices.

CREATE INDEX IF NOT EXISTS idx_edges_graph_source
    ON edges(graph_id, source_vertex);

CREATE INDEX IF NOT EXISTS idx_edges_graph_destination
    ON edges(graph_id, destination_vertex);

CREATE INDEX IF NOT EXISTS idx_edges_graph_source_destination
    ON edges(graph_id, source_vertex, destination_vertex);

CREATE INDEX IF NOT EXISTS idx_edges_negative_weights
    ON edges(graph_id)
    WHERE weight < 0;

CREATE INDEX IF NOT EXISTS idx_vertices_graph
    ON vertices(graph_id);

-- ---------------------------------------------------------------------------
-- 3. ANALYSIS HISTORY
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS analysis_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES repositories(graph_id)
        ON DELETE CASCADE,

    source_vertex BIGINT NOT NULL,

    algorithm algorithm_type NOT NULL,

    status analysis_status NOT NULL DEFAULT 'COMPLETED',

    iterations INTEGER NOT NULL DEFAULT 0,

    negative_cycle_detected BOOLEAN NOT NULL DEFAULT FALSE,

    execution_time_ms NUMERIC(15, 3),

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (iterations >= 0),

    CHECK (
        execution_time_ms IS NULL
        OR execution_time_ms >= 0
    ),

    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES vertices(graph_id, vertex_id)
);

CREATE INDEX IF NOT EXISTS idx_analysis_graph_date
    ON analysis_runs(graph_id, executed_at DESC);

-- ---------------------------------------------------------------------------
-- 4. SHORTEST-PATH RESULTS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS shortest_path_results (
    run_id BIGINT NOT NULL
        REFERENCES analysis_runs(run_id)
        ON DELETE CASCADE,

    vertex_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id)
        ON DELETE CASCADE,

    distance NUMERIC(50, 0),

    predecessor_vertex BIGINT,

    is_reachable BOOLEAN NOT NULL,

    negative_cycle_affected BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (run_id, vertex_id),

    CHECK (
        (is_reachable = FALSE AND distance IS NULL)
        OR
        (is_reachable = TRUE AND distance IS NOT NULL)
    ),

    CHECK (
        NOT negative_cycle_affected
        OR is_reachable
    )
);

CREATE INDEX IF NOT EXISTS idx_results_run_distance
    ON shortest_path_results(run_id, distance)
    WHERE is_reachable AND NOT negative_cycle_affected;

-- ---------------------------------------------------------------------------
-- 5. GRAPH VALIDATION
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_source(
    p_graph_id BIGINT,
    p_source BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_source
    ) THEN
        RAISE EXCEPTION
            'Source vertex % does not belong to graph %',
            p_source,
            p_graph_id;
    END IF;

    RETURN TRUE;
END;
$$;

-- Dijkstra must not be executed on graphs containing negative edges.

CREATE OR REPLACE FUNCTION validate_dijkstra_eligibility(
    p_graph_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM repositories
        WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Unknown graph: %', p_graph_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM edges
        WHERE graph_id = p_graph_id
          AND weight < 0
    ) THEN
        RAISE EXCEPTION
            'Dijkstra is not valid for graphs containing negative edges';
    END IF;

    RETURN TRUE;
END;
$$;

-- ---------------------------------------------------------------------------
-- 6. BELLMAN-FORD COMPUTATION
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION bellman_ford(
    p_graph_id BIGINT,
    p_source BIGINT
)
RETURNS TABLE (
    result_vertex BIGINT,
    shortest_distance NUMERIC,
    predecessor BIGINT,
    reachable BOOLEAN,
    negative_cycle_affected BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
    v_pass INTEGER := 0;
    v_changed BOOLEAN;
    v_edge RECORD;
    v_candidate NUMERIC;
    v_current NUMERIC;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM repositories
        WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Unknown graph: %', p_graph_id;
    END IF;

    PERFORM validate_graph_source(p_graph_id, p_source);

    SELECT COUNT(*)::INTEGER
    INTO v_count
    FROM vertices
    WHERE graph_id = p_graph_id;

    /*
       Temporary tables are isolated by database session.
       They are truncated for repeated calls within one session.
    */

    CREATE TEMP TABLE IF NOT EXISTS bf_distance (
        vertex_id BIGINT PRIMARY KEY,
        distance NUMERIC,
        predecessor BIGINT
    ) ON COMMIT PRESERVE ROWS;

    CREATE TEMP TABLE IF NOT EXISTS bf_affected (
        vertex_id BIGINT PRIMARY KEY
    ) ON COMMIT PRESERVE ROWS;

    TRUNCATE TABLE bf_distance;
    TRUNCATE TABLE bf_affected;

    INSERT INTO bf_distance (
        vertex_id,
        distance,
        predecessor
    )
    SELECT
        vertex_id,
        CASE
            WHEN vertex_id = p_source THEN 0::NUMERIC
            ELSE NULL::NUMERIC
        END,
        NULL::BIGINT
    FROM vertices
    WHERE graph_id = p_graph_id;

    /*
       Relaxation:

       If distance[u] + weight(u,v) < distance[v],
       update distance[v] and predecessor[v].

       The implementation performs ordered in-place relaxation.
       This can propagate through several edges in one pass.
       V-1 complete passes are still sufficient for graphs without
       reachable negative cycles.
    */

    FOR v_pass IN 1..GREATEST(v_count - 1, 0)
    LOOP
        v_changed := FALSE;

        FOR v_edge IN
            SELECT
                source_vertex,
                destination_vertex,
                weight
            FROM edges
            WHERE graph_id = p_graph_id
            ORDER BY edge_id
        LOOP
            SELECT distance
            INTO v_current
            FROM bf_distance
            WHERE vertex_id = v_edge.source_vertex;

            IF v_current IS NULL THEN
                CONTINUE;
            END IF;

            v_candidate := v_current + v_edge.weight;

            IF EXISTS (
                SELECT 1
                FROM bf_distance
                WHERE vertex_id = v_edge.destination_vertex
                  AND (
                      distance IS NULL
                      OR v_candidate < distance
                  )
            ) THEN
                UPDATE bf_distance
                SET distance = v_candidate,
                    predecessor = v_edge.source_vertex
                WHERE vertex_id = v_edge.destination_vertex;

                v_changed := TRUE;
            END IF;
        END LOOP;

        -- Early termination when no edge can improve a distance.
        EXIT WHEN NOT v_changed;
    END LOOP;

    /*
       Negative-cycle detection:

       After V-1 passes, an additional improvement indicates
       a reachable negative-weight cycle.
    */

    FOR v_edge IN
        SELECT
            source_vertex,
            destination_vertex,
            weight
        FROM edges
        WHERE graph_id = p_graph_id
        ORDER BY edge_id
    LOOP
        SELECT distance
        INTO v_current
        FROM bf_distance
        WHERE vertex_id = v_edge.source_vertex;

        IF v_current IS NULL THEN
            CONTINUE;
        END IF;

        v_candidate := v_current + v_edge.weight;

        IF EXISTS (
            SELECT 1
            FROM bf_distance
            WHERE vertex_id = v_edge.destination_vertex
              AND (
                  distance IS NULL
                  OR v_candidate < distance
              )
        ) THEN
            INSERT INTO bf_affected(vertex_id)
            VALUES (v_edge.destination_vertex)
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;

    /*
       Propagate negative-cycle influence.

       A vertex reachable from an affected vertex also has
       no finite shortest distance.
    */

    LOOP
        INSERT INTO bf_affected(vertex_id)
        SELECT DISTINCT e.destination_vertex
        FROM edges e
        INNER JOIN bf_affected a
            ON a.vertex_id = e.source_vertex
        WHERE e.graph_id = p_graph_id
        ON CONFLICT DO NOTHING;

        GET DIAGNOSTICS v_count = ROW_COUNT;

        EXIT WHEN v_count = 0;
    END LOOP;

    RETURN QUERY
    SELECT
        d.vertex_id,
        CASE
            WHEN a.vertex_id IS NOT NULL THEN NULL::NUMERIC
            ELSE d.distance
        END,
        d.predecessor,
        d.distance IS NOT NULL,
        a.vertex_id IS NOT NULL
    FROM bf_distance d
    LEFT JOIN bf_affected a
        ON a.vertex_id = d.vertex_id
    ORDER BY d.vertex_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- 7. ANALYSIS EXECUTION AND RESULT PERSISTENCE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION execute_bellman_ford(
    p_graph_id BIGINT,
    p_source BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_run_id BIGINT;
    v_started TIMESTAMPTZ;
    v_elapsed NUMERIC(15, 3);
    v_cycle BOOLEAN;
    v_iterations INTEGER;
BEGIN
    v_started := clock_timestamp();

    PERFORM validate_graph_source(p_graph_id, p_source);

    -- A new execution starts inside the caller's transaction.
    INSERT INTO analysis_runs (
        graph_id,
        source_vertex,
        algorithm,
        status
    )
    VALUES (
        p_graph_id,
        p_source,
        'BELLMAN_FORD',
        'COMPLETED'
    )
    RETURNING run_id INTO v_run_id;

    CREATE TEMP TABLE IF NOT EXISTS bf_output (
        result_vertex BIGINT,
        shortest_distance NUMERIC,
        predecessor BIGINT,
        reachable BOOLEAN,
        negative_cycle_affected BOOLEAN
    ) ON COMMIT PRESERVE ROWS;

    TRUNCATE TABLE bf_output;

    INSERT INTO bf_output
    SELECT *
    FROM bellman_ford(p_graph_id, p_source);

    SELECT EXISTS (
        SELECT 1
        FROM bf_output
        WHERE negative_cycle_affected
    )
    INTO v_cycle;

    SELECT COUNT(*)::INTEGER
    INTO v_iterations
    FROM bf_output;

    INSERT INTO shortest_path_results (
        run_id,
        vertex_id,
        distance,
        predecessor_vertex,
        is_reachable,
        negative_cycle_affected
    )
    SELECT
        v_run_id,
        result_vertex,
        shortest_distance,
        predecessor,
        reachable,
        negative_cycle_affected
    FROM bf_output;

    v_elapsed :=
        EXTRACT(EPOCH FROM (
            clock_timestamp() - v_started
        )) * 1000;

    UPDATE analysis_runs
    SET negative_cycle_detected = v_cycle,
        iterations = v_iterations,
        execution_time_ms = v_elapsed,
        status = CASE
            WHEN v_cycle THEN 'NEGATIVE_CYCLE_DETECTED'
            ELSE 'COMPLETED'
        END
    WHERE run_id = v_run_id;

    RETURN v_run_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- 8. REPORTING VIEWS
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW shortest_path_report AS
SELECT
    ar.run_id,
    r.graph_name,
    ar.source_vertex,
    ar.algorithm,
    ar.status,
    ar.executed_at,
    v.vertex_name AS destination,
    spr.distance,
    spr.predecessor_vertex,
    spr.is_reachable,
    spr.negative_cycle_affected
FROM analysis_runs ar
JOIN repositories r
    ON r.graph_id = ar.graph_id
JOIN shortest_path_results spr
    ON spr.run_id = ar.run_id
JOIN vertices v
    ON v.vertex_id = spr.vertex_id;

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    r.graph_id,
    r.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    COUNT(DISTINCT e.edge_id)
        FILTER (WHERE e.weight < 0) AS negative_edge_count,
    COUNT(DISTINCT e.edge_id)
        FILTER (WHERE e.weight >= 0) AS nonnegative_edge_count
FROM repositories r
LEFT JOIN vertices v
    ON v.graph_id = r.graph_id
LEFT JOIN edges e
    ON e.graph_id = r.graph_id
GROUP BY r.graph_id, r.graph_name;

-- ---------------------------------------------------------------------------
-- 9. SAMPLE GRAPH A: NEGATIVE EDGES WITHOUT NEGATIVE CYCLES
-- ---------------------------------------------------------------------------

INSERT INTO repositories(graph_name, description)
VALUES (
    'negative_edges_example',
    'Directed graph with negative edges and finite shortest paths.'
)
ON CONFLICT (graph_name) DO NOTHING;

INSERT INTO vertices(graph_id, vertex_name)
SELECT r.graph_id, names.vertex_name
FROM repositories r
CROSS JOIN (
    VALUES
        ('A'),
        ('B'),
        ('C'),
        ('D'),
        ('E'),
        ('F')
) AS names(vertex_name)
WHERE r.graph_name = 'negative_edges_example'
ON CONFLICT (graph_id, vertex_name) DO NOTHING;

INSERT INTO edges (
    graph_id,
    source_vertex,
    destination_vertex,
    weight
)
SELECT
    r.graph_id,
    source.vertex_id,
    destination.vertex_id,
    data.weight
FROM repositories r
CROSS JOIN (
    VALUES
        ('A', 'B', 4::NUMERIC),
        ('A', 'C', 5::NUMERIC),
        ('B', 'C', -2::NUMERIC),
        ('B', 'D', 6::NUMERIC),
        ('C', 'D', 3::NUMERIC),
        ('D', 'E', 2::NUMERIC),
        ('E', 'B', 1::NUMERIC)
) AS data(source_name, destination_name, weight)
JOIN vertices source
    ON source.graph_id = r.graph_id
   AND source.vertex_name = data.source_name
JOIN vertices destination
    ON destination.graph_id = r.graph_id
   AND destination.vertex_name = data.destination_name
WHERE r.graph_name = 'negative_edges_example'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = r.graph_id
      AND existing.source_vertex = source.vertex_id
      AND existing.destination_vertex = destination.vertex_id
      AND existing.weight = data.weight
);

-- ---------------------------------------------------------------------------
-- 10. SAMPLE GRAPH B: REACHABLE NEGATIVE CYCLE
-- ---------------------------------------------------------------------------

INSERT INTO repositories(graph_name, description)
VALUES (
    'negative_cycle_example',
    'Graph containing a reachable negative cycle and an isolated cycle.'
)
ON CONFLICT (graph_name) DO NOTHING;

INSERT INTO vertices(graph_id, vertex_name)
SELECT r.graph_id, names.vertex_name
FROM repositories r
CROSS JOIN (
    VALUES
        ('A'),
        ('B'),
        ('C'),
        ('D'),
        ('E'),
        ('F')
) AS names(vertex_name)
WHERE r.graph_name = 'negative_cycle_example'
ON CONFLICT (graph_id, vertex_name) DO NOTHING;

INSERT INTO edges (
    graph_id,
    source_vertex,
    destination_vertex,
    weight
)
SELECT
    r.graph_id,
    source.vertex_id,
    destination.vertex_id,
    data.weight
FROM repositories r
CROSS JOIN (
    VALUES
        ('A', 'B', 2::NUMERIC),
        ('B', 'C', 2::NUMERIC),
        ('C', 'D', -5::NUMERIC),
        ('D', 'B', 1::NUMERIC),
        ('D', 'E', 3::NUMERIC),
        ('F', 'F', -1::NUMERIC)
) AS data(source_name, destination_name, weight)
JOIN vertices source
    ON source.graph_id = r.graph_id
   AND source.vertex_name = data.source_name
JOIN vertices destination
    ON destination.graph_id = r.graph_id
   AND destination.vertex_name = data.destination_name
WHERE r.graph_name = 'negative_cycle_example'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = r.graph_id
      AND existing.source_vertex = source.vertex_id
      AND existing.destination_vertex = destination.vertex_id
      AND existing.weight = data.weight
);

-- ---------------------------------------------------------------------------
-- 11. TRANSACTIONAL ANALYSIS EXECUTION
-- ---------------------------------------------------------------------------

DO $$
DECLARE
    v_graph_id BIGINT;
    v_source BIGINT;
    v_run_id BIGINT;
BEGIN
    SELECT r.graph_id, v.vertex_id
    INTO v_graph_id, v_source
    FROM repositories r
    JOIN vertices v
        ON v.graph_id = r.graph_id
    WHERE r.graph_name = 'negative_edges_example'
      AND v.vertex_name = 'A';

    v_run_id := execute_bellman_ford(v_graph_id, v_source);

    RAISE NOTICE 'Negative-edge analysis run: %', v_run_id;

    SELECT r.graph_id, v.vertex_id
    INTO v_graph_id, v_source
    FROM repositories r
    JOIN vertices v
        ON v.graph_id = r.graph_id
    WHERE r.graph_name = 'negative_cycle_example'
      AND v.vertex_name = 'A';

    v_run_id := execute_bellman_ford(v_graph_id, v_source);

    RAISE NOTICE 'Negative-cycle analysis run: %', v_run_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- 12. RETRIEVAL AND REPORTING QUERIES
-- ---------------------------------------------------------------------------

-- A. All graph characteristics.

SELECT *
FROM graph_statistics
ORDER BY graph_name;

-- B. Shortest-path results across all analysis runs.

SELECT
    run_id,
    graph_name,
    source_vertex,
    destination,
    distance,
    is_reachable,
    negative_cycle_affected,
    status
FROM shortest_path_report
ORDER BY run_id, destination;

-- C. Reachable vertices with valid finite shortest distances.

SELECT
    run_id,
    destination,
    distance
FROM shortest_path_report
WHERE is_reachable
  AND NOT negative_cycle_affected
ORDER BY run_id, distance;

-- D. Unreachable vertices.

SELECT
    run_id,
    graph_name,
    destination
FROM shortest_path_report
WHERE NOT is_reachable;

-- E. Vertices affected by reachable negative cycles.

SELECT
    run_id,
    graph_name,
    destination
FROM shortest_path_report
WHERE negative_cycle_affected;

-- F. Analysis performance report.

SELECT
    graph_name,
    algorithm,
    COUNT(*) AS executions,
    AVG(execution_time_ms) AS average_execution_ms,
    MAX(execution_time_ms) AS maximum_execution_ms,
    COUNT(*) FILTER (
        WHERE negative_cycle_detected
    ) AS negative_cycle_runs
FROM analysis_runs ar
JOIN repositories r
    ON r.graph_id = ar.graph_id
GROUP BY graph_name, algorithm;

-- G. Dijkstra eligibility report.

SELECT
    r.graph_name,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM edges e
            WHERE e.graph_id = r.graph_id
              AND e.weight < 0
        )
        THEN 'NOT ELIGIBLE'
        ELSE 'ELIGIBLE'
    END AS dijkstra_eligibility
FROM repositories r;

-- H. Validate Dijkstra on the nonnegative graph.
-- This succeeds because the graph contains no negative edges.

DO $$
DECLARE
    v_graph_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM repositories
    WHERE graph_name = 'negative_cycle_example';

    -- This graph contains negative edges, so validation must fail.
    BEGIN
        PERFORM validate_dijkstra_eligibility(v_graph_id);
        RAISE EXCEPTION
            'Expected Dijkstra validation to reject this graph.';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE '%Dijkstra is not valid%' THEN
                RAISE;
            END IF;

            RAISE NOTICE 'Dijkstra rejection verified: %', SQLERRM;
    END;
END;
$$;

-- ---------------------------------------------------------------------------
-- 13. INTEGRITY VALIDATION
-- ---------------------------------------------------------------------------

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM shortest_path_report
    WHERE graph_name = 'negative_edges_example'
      AND destination = 'E'
      AND distance = 7
      AND NOT negative_cycle_affected;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Negative-edge shortest-path validation failed.';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM shortest_path_report
    WHERE graph_name = 'negative_cycle_example'
      AND destination IN ('B', 'C', 'D', 'E')
      AND negative_cycle_affected;

    IF v_count <> 4 THEN
        RAISE EXCEPTION
            'Negative-cycle propagation validation failed.';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM shortest_path_report
    WHERE graph_name = 'negative_cycle_example'
      AND destination = 'F'
      AND NOT negative_cycle_affected
      AND NOT is_reachable;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Unreachable negative-cycle validation failed.';
    END IF;

    RAISE NOTICE 'All database validation checks passed.';
END;
$$;

COMMIT;
