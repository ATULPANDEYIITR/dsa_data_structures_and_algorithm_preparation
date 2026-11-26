-- ============================================================
-- DIJKSTRA'S ALGORITHM
-- PostgreSQL shortest-path database implementation
--
-- Features:
-- 1. Directed and undirected weighted graphs
-- 2. Vertex and edge integrity
-- 3. Non-negative weight enforcement
-- 4. Single-source shortest paths
-- 5. Priority selection of the next unsettled vertex
-- 6. Distance relaxation
-- 7. Predecessor tracking
-- 8. Path reconstruction
-- 9. Unreachable vertex reporting
-- 10. Graph analytics and validation
--
-- Database implementation uses a relational representation.
-- The procedural shortest-path function uses an indexed
-- temporary distance table instead of a binary heap.
-- ============================================================

BEGIN;

DROP SCHEMA IF EXISTS dijkstra_lab CASCADE;

CREATE SCHEMA dijkstra_lab;

SET search_path TO dijkstra_lab, public;

-- ============================================================
-- 1. DOMAIN TABLES
-- ============================================================

CREATE TABLE graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    graph_type VARCHAR(15) NOT NULL
        CHECK (graph_type IN ('DIRECTED', 'UNDIRECTED')),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vertex (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graph(graph_id) ON DELETE CASCADE,
    vertex_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (graph_id, vertex_name),
    UNIQUE (graph_id, vertex_id)
);

CREATE TABLE edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,
    weight NUMERIC(18, 4) NOT NULL
        CHECK (
            weight >= 0
            AND weight < 'Infinity'::NUMERIC
        ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (source_vertex_id <> destination_vertex_id),

    UNIQUE (
        graph_id,
        source_vertex_id,
        destination_vertex_id
    )
);

-- ============================================================
-- 2. PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_vertex_graph
    ON vertex(graph_id);

CREATE INDEX idx_edge_source
    ON edge(graph_id, source_vertex_id);

CREATE INDEX idx_edge_destination
    ON edge(graph_id, destination_vertex_id);

CREATE INDEX idx_edge_weight
    ON edge(graph_id, weight);

-- ============================================================
-- 3. SAMPLE GRAPH
-- ============================================================

INSERT INTO graph (
    graph_name,
    graph_type,
    description
)
VALUES (
    'City Road Network',
    'UNDIRECTED',
    'Weighted road network for shortest-route calculation'
);

INSERT INTO vertex (
    graph_id,
    vertex_name
)
SELECT
    g.graph_id,
    v.vertex_name
FROM graph g
CROSS JOIN (
    VALUES
        ('A'),
        ('B'),
        ('C'),
        ('D'),
        ('E'),
        ('F'),
        ('G')
) AS v(vertex_name)
WHERE g.graph_name = 'City Road Network';

-- ============================================================
-- 4. INSERT EDGE DATA
-- ============================================================

INSERT INTO edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source_vertex.vertex_id,
    destination_vertex.vertex_id,
    roads.weight
FROM graph g
JOIN (
    VALUES
        ('A', 'B', 4.0::NUMERIC),
        ('A', 'C', 2.0::NUMERIC),
        ('B', 'C', 1.0::NUMERIC),
        ('B', 'D', 5.0::NUMERIC),
        ('C', 'D', 8.0::NUMERIC),
        ('C', 'E', 10.0::NUMERIC),
        ('D', 'E', 2.0::NUMERIC),
        ('D', 'F', 6.0::NUMERIC),
        ('E', 'F', 3.0::NUMERIC)
) AS roads(source_name, destination_name, weight)
    ON TRUE
JOIN vertex source_vertex
    ON source_vertex.graph_id = g.graph_id
    AND source_vertex.vertex_name = roads.source_name
JOIN vertex destination_vertex
    ON destination_vertex.graph_id = g.graph_id
    AND destination_vertex.vertex_name = roads.destination_name
WHERE g.graph_name = 'City Road Network';

-- ============================================================
-- 5. GRAPH INTEGRITY TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION validate_edge_graph_type()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph
        WHERE graph_id = NEW.graph_id
    ) THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_edge
BEFORE INSERT OR UPDATE ON edge
FOR EACH ROW
EXECUTE FUNCTION validate_edge_graph_type();

-- ============================================================
-- 6. EDGE INSERTION PROCEDURE
-- Automatically creates reverse edges for undirected graphs.
-- ============================================================

CREATE OR REPLACE PROCEDURE add_graph_edge(
    p_graph_id BIGINT,
    p_source_name VARCHAR,
    p_destination_name VARCHAR,
    p_weight NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_id BIGINT;
    v_destination_id BIGINT;
    v_graph_type VARCHAR(15);
BEGIN
    IF p_weight IS NULL OR
       p_weight < 0 OR
       p_weight >= 'Infinity'::NUMERIC THEN
        RAISE EXCEPTION 'Invalid edge weight';
    END IF;

    SELECT graph_type
    INTO v_graph_type
    FROM graph
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    SELECT vertex_id
    INTO v_source_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_source_name;

    SELECT vertex_id
    INTO v_destination_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_destination_name;

    IF v_source_id IS NULL OR v_destination_id IS NULL THEN
        RAISE EXCEPTION 'Source or destination vertex not found';
    END IF;

    IF v_source_id = v_destination_id THEN
        RAISE EXCEPTION 'Self-loops are not permitted';
    END IF;

    INSERT INTO edge (
        graph_id,
        source_vertex_id,
        destination_vertex_id,
        weight
    )
    VALUES (
        p_graph_id,
        v_source_id,
        v_destination_id,
        p_weight
    );

    IF v_graph_type = 'UNDIRECTED' THEN
        INSERT INTO edge (
            graph_id,
            source_vertex_id,
            destination_vertex_id,
            weight
        )
        VALUES (
            p_graph_id,
            v_destination_id,
            v_source_id,
            p_weight
        );
    END IF;
END;
$$;

-- ============================================================
-- 7. GRAPH RETRIEVAL VIEW
-- ============================================================

CREATE OR REPLACE VIEW graph_edges AS
SELECT
    g.graph_name,
    g.graph_type,
    source.vertex_name AS source_vertex,
    destination.vertex_name AS destination_vertex,
    e.weight
FROM edge e
JOIN graph g
    ON g.graph_id = e.graph_id
JOIN vertex source
    ON source.vertex_id = e.source_vertex_id
JOIN vertex destination
    ON destination.vertex_id = e.destination_vertex_id;

-- ============================================================
-- 8. SINGLE-SOURCE DIJKSTRA FUNCTION
--
-- Algorithm:
-- a. Initialize all distances to NULL (unreachable).
-- b. Set source distance to zero.
-- c. Select the unsettled vertex with minimum distance.
-- d. Relax outgoing edges.
-- e. Record predecessor when a shorter path is discovered.
-- f. Repeat until no reachable unsettled vertex remains.
--
-- NULL represents infinity.
--
-- This SQL implementation uses indexed minimum-distance
-- selection rather than a binary heap.
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_shortest_paths(
    p_graph_id BIGINT,
    p_source_name VARCHAR
)
RETURNS TABLE (
    vertex_id BIGINT,
    vertex_name VARCHAR,
    shortest_distance NUMERIC,
    predecessor_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_id BIGINT;
    v_current_id BIGINT;
    v_current_distance NUMERIC;
    v_neighbor_id BIGINT;
    v_weight NUMERIC;
    v_candidate NUMERIC;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph
        WHERE graph.graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    SELECT v.vertex_id
    INTO v_source_id
    FROM vertex v
    WHERE v.graph_id = p_graph_id
      AND v.vertex_name = p_source_name;

    IF v_source_id IS NULL THEN
        RAISE EXCEPTION 'Source vertex does not exist';
    END IF;

    -- Remove temporary tables from an earlier call in
    -- the same transaction.
    DROP TABLE IF EXISTS pg_temp.dijkstra_distance;
    DROP TABLE IF EXISTS pg_temp.dijkstra_settled;

    CREATE TEMP TABLE dijkstra_distance (
        vertex_id BIGINT PRIMARY KEY,
        distance NUMERIC,
        predecessor_id BIGINT
    ) ON COMMIT DROP;

    CREATE TEMP TABLE dijkstra_settled (
        vertex_id BIGINT PRIMARY KEY
    ) ON COMMIT DROP;

    CREATE INDEX idx_dijkstra_distance_min
        ON dijkstra_distance(distance, vertex_id);

    INSERT INTO dijkstra_distance (
        vertex_id,
        distance,
        predecessor_id
    )
    SELECT
        v.vertex_id,
        CASE
            WHEN v.vertex_id = v_source_id THEN 0
            ELSE NULL
        END,
        NULL
    FROM vertex v
    WHERE v.graph_id = p_graph_id;

    LOOP
        -- Extract the minimum unsettled reachable vertex.
        SELECT
            d.vertex_id,
            d.distance
        INTO
            v_current_id,
            v_current_distance
        FROM dijkstra_distance d
        WHERE d.distance IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM dijkstra_settled s
              WHERE s.vertex_id = d.vertex_id
          )
        ORDER BY
            d.distance,
            d.vertex_id
        LIMIT 1;

        EXIT WHEN NOT FOUND;

        INSERT INTO dijkstra_settled(vertex_id)
        VALUES (v_current_id);

        -- Relax every outgoing edge.
        FOR v_neighbor_id, v_weight IN
            SELECT
                e.destination_vertex_id,
                e.weight
            FROM edge e
            WHERE e.graph_id = p_graph_id
              AND e.source_vertex_id = v_current_id
            ORDER BY e.destination_vertex_id
        LOOP
            IF EXISTS (
                SELECT 1
                FROM dijkstra_settled s
                WHERE s.vertex_id = v_neighbor_id
            ) THEN
                CONTINUE;
            END IF;

            v_candidate := v_current_distance + v_weight;

            UPDATE dijkstra_distance d
            SET
                distance = v_candidate,
                predecessor_id = v_current_id
            WHERE d.vertex_id = v_neighbor_id
              AND (
                  d.distance IS NULL
                  OR v_candidate < d.distance
              );
        END LOOP;
    END LOOP;

    RETURN QUERY
    SELECT
        v.vertex_id,
        v.vertex_name,
        d.distance,
        predecessor.vertex_name
    FROM vertex v
    JOIN dijkstra_distance d
        ON d.vertex_id = v.vertex_id
    LEFT JOIN vertex predecessor
        ON predecessor.vertex_id = d.predecessor_id
    WHERE v.graph_id = p_graph_id
    ORDER BY v.vertex_name;
END;
$$;

-- ============================================================
-- 9. SHORTEST-PATH REPORT
-- ============================================================

CREATE OR REPLACE FUNCTION get_shortest_path(
    p_graph_id BIGINT,
    p_source_name VARCHAR,
    p_destination_name VARCHAR
)
RETURNS TABLE (
    step_number INTEGER,
    vertex_name VARCHAR,
    cumulative_distance NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_id BIGINT;
    v_destination_id BIGINT;
    v_current_id BIGINT;
    v_distance NUMERIC;
    v_predecessor_id BIGINT;
    v_step INTEGER := 0;
    v_path BIGINT[] := ARRAY[]::BIGINT[];
BEGIN
    SELECT vertex_id
    INTO v_source_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_source_name;

    SELECT vertex_id
    INTO v_destination_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_destination_name;

    IF v_source_id IS NULL OR v_destination_id IS NULL THEN
        RAISE EXCEPTION 'Source or destination not found';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS dijkstra_path_result (
        vertex_id BIGINT,
        distance NUMERIC,
        predecessor_id BIGINT
    ) ON COMMIT DROP;

    TRUNCATE TABLE dijkstra_path_result;

    INSERT INTO dijkstra_path_result
    SELECT
        r.vertex_id,
        r.shortest_distance,
        (
            SELECT p.vertex_id
            FROM vertex p
            WHERE p.graph_id = p_graph_id
              AND p.vertex_name = r.predecessor_name
        )
    FROM calculate_shortest_paths(
        p_graph_id,
        p_source_name
    ) r;

    SELECT distance
    INTO v_distance
    FROM dijkstra_path_result
    WHERE vertex_id = v_destination_id;

    IF v_distance IS NULL THEN
        RETURN;
    END IF;

    v_current_id := v_destination_id;

    -- Reconstruct destination-to-source predecessor chain.
    WHILE v_current_id IS NOT NULL LOOP
        IF v_current_id = ANY(v_path) THEN
            RAISE EXCEPTION 'Predecessor cycle detected';
        END IF;

        v_path := array_append(v_path, v_current_id);

        IF v_current_id = v_source_id THEN
            EXIT;
        END IF;

        SELECT predecessor_id
        INTO v_predecessor_id
        FROM dijkstra_path_result
        WHERE vertex_id = v_current_id;

        IF v_predecessor_id IS NULL THEN
            RAISE EXCEPTION 'Invalid predecessor chain';
        END IF;

        v_current_id := v_predecessor_id;
    END LOOP;

    IF v_path[array_length(v_path, 1)] <> v_source_id THEN
        RAISE EXCEPTION 'Source not reached during reconstruction';
    END IF;

    FOR v_step IN REVERSE array_length(v_path, 1)..1 LOOP
        RETURN QUERY
        SELECT
            (array_length(v_path, 1) - v_step + 1)::INTEGER,
            v.vertex_name,
            p.distance
        FROM vertex v
        JOIN dijkstra_path_result p
            ON p.vertex_id = v.vertex_id
        WHERE v.vertex_id = v_path[v_step];
    END LOOP;
END;
$$;

-- ============================================================
-- 10. GRAPH STATISTICS
-- ============================================================

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    COALESCE(MIN(e.weight), 0) AS minimum_weight,
    COALESCE(MAX(e.weight), 0) AS maximum_weight,
    COALESCE(AVG(e.weight), 0) AS average_weight
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_type;

-- ============================================================
-- 11. VALIDATION REPORT
-- ============================================================

CREATE OR REPLACE VIEW graph_validation AS
SELECT
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertices,
    COUNT(DISTINCT e.edge_id) AS edges,
    COUNT(e.edge_id) FILTER (
        WHERE e.weight < 0
    ) AS negative_edges,
    COUNT(e.edge_id) FILTER (
        WHERE e.source_vertex_id = e.destination_vertex_id
    ) AS self_loops,
    CASE
        WHEN COUNT(e.edge_id) FILTER (
            WHERE e.weight < 0
        ) = 0
        THEN 'VALID'
        ELSE 'INVALID'
    END AS validation_status
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name;

-- ============================================================
-- 12. TRANSACTIONAL EDGE INSERTION EXAMPLE
-- A duplicate edge fails the unique constraint.
-- ============================================================

SAVEPOINT before_test_edge;

-- The sample network already contains A -> B.
-- The following commented statement demonstrates the failure:
-- CALL add_graph_edge(1, 'A', 'B', 12);

ROLLBACK TO SAVEPOINT before_test_edge;

RELEASE SAVEPOINT before_test_edge;

-- ============================================================
-- 13. RETRIEVAL QUERIES
-- ============================================================

SELECT *
FROM graph_edges
ORDER BY source_vertex, destination_vertex;

SELECT *
FROM graph_statistics;

SELECT *
FROM graph_validation;

-- ============================================================
-- 14. SHORTEST DISTANCE QUERY
-- ============================================================

SELECT *
FROM calculate_shortest_paths(
    (
        SELECT graph_id
        FROM graph
        WHERE graph_name = 'City Road Network'
    ),
    'A'
);

-- ============================================================
-- 15. SHORTEST ROUTE QUERY
-- ============================================================

SELECT *
FROM get_shortest_path(
    (
        SELECT graph_id
        FROM graph
        WHERE graph_name = 'City Road Network'
    ),
    'A',
    'F'
)
ORDER BY step_number;

-- ============================================================
-- 16. UNREACHABLE VERTEX EVALUATION
-- ============================================================

SELECT
    vertex_name,
    shortest_distance,
    CASE
        WHEN shortest_distance IS NULL THEN 'UNREACHABLE'
        ELSE 'REACHABLE'
    END AS reachability
FROM calculate_shortest_paths(
    (
        SELECT graph_id
        FROM graph
        WHERE graph_name = 'City Road Network'
    ),
    'A'
)
ORDER BY vertex_name;

-- ============================================================
-- 17. AGGREGATION REPORT
-- ============================================================

WITH shortest_paths AS (
    SELECT *
    FROM calculate_shortest_paths(
        (
            SELECT graph_id
            FROM graph
            WHERE graph_name = 'City Road Network'
        ),
        'A'
    )
)
SELECT
    COUNT(*) AS total_vertices,
    COUNT(shortest_distance) AS reachable_vertices,
    COUNT(*) - COUNT(shortest_distance) AS unreachable_vertices,
    MAX(shortest_distance) AS maximum_reachable_distance,
    AVG(shortest_distance) AS average_reachable_distance
FROM shortest_paths;

-- ============================================================
-- 18. ELIGIBILITY DETERMINATION
-- Example: operational routes must not exceed 15 distance units.
-- ============================================================

WITH shortest_paths AS (
    SELECT *
    FROM calculate_shortest_paths(
        (
            SELECT graph_id
            FROM graph
            WHERE graph_name = 'City Road Network'
        ),
        'A'
    )
)
SELECT
    vertex_name,
    shortest_distance,
    CASE
        WHEN shortest_distance IS NULL THEN 'INELIGIBLE'
        WHEN shortest_distance <= 15 THEN 'ELIGIBLE'
        ELSE 'DISTANCE_LIMIT_EXCEEDED'
    END AS route_eligibility
FROM shortest_paths
ORDER BY vertex_name;

-- ============================================================
-- 19. CTE-BASED EDGE ANALYSIS
-- ============================================================

WITH edge_analysis AS (
    SELECT
        source_vertex,
        destination_vertex,
        weight,
        AVG(weight) OVER () AS network_average
    FROM graph_edges
    WHERE graph_name = 'City Road Network'
)
SELECT
    source_vertex,
    destination_vertex,
    weight,
    network_average,
    CASE
        WHEN weight > network_average THEN 'ABOVE_AVERAGE'
        ELSE 'AT_OR_BELOW_AVERAGE'
    END AS edge_classification
FROM edge_analysis
ORDER BY weight DESC;

COMMIT;

-- ============================================================
-- IMPLEMENTATION NOTES
--
-- The procedural SQL implementation uses:
-- - Indexed distance records
-- - Minimum unsettled-distance selection
-- - Edge relaxation
-- - Predecessor tracking
--
-- Unlike the Python, C++, and Java binary-heap implementations,
-- this relational implementation performs minimum selection
-- through SQL ordering and indexing.
--
-- Its execution cost can be higher for large graphs.
-- The binary-heap implementations are generally preferable
-- for large sparse graphs.
--
-- Numeric distance storage avoids floating-point accumulation
-- differences for decimal-weighted networks.
-- ============================================================
