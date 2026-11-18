-- ============================================================
-- GRAPH FUNDAMENTALS
-- PostgreSQL 15+
--
-- Relational graph model covering:
-- Vertices, edges, directed graphs, undirected graphs,
-- weighted graphs, unweighted graphs, and degree.
--
-- Also includes:
-- Graph validation, adjacency retrieval, BFS, connected
-- components, cycle detection, shortest-path evaluation,
-- aggregation, and graph integrity constraints.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ------------------------------------------------------------
-- 1. GRAPH DEFINITIONS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    graph_type VARCHAR(15) NOT NULL
        CHECK (graph_type IN ('DIRECTED', 'UNDIRECTED')),

    weighted BOOLEAN NOT NULL DEFAULT FALSE,

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_graph_name
        CHECK (length(trim(graph_name)) > 0)
);

-- ------------------------------------------------------------
-- 2. VERTICES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    vertex_key VARCHAR(100) NOT NULL,

    vertex_label VARCHAR(200) NOT NULL,

    vertex_type VARCHAR(50) NOT NULL DEFAULT 'GENERAL',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_vertex_graph
        FOREIGN KEY (graph_id)
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_vertex_key
        UNIQUE (graph_id, vertex_key),

    CONSTRAINT valid_vertex_key
        CHECK (length(trim(vertex_key)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_vertices_graph
    ON vertices(graph_id);

-- ------------------------------------------------------------
-- 3. EDGES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex_id BIGINT NOT NULL,

    target_vertex_id BIGINT NOT NULL,

    weight NUMERIC(18, 6) NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_edge_graph
        FOREIGN KEY (graph_id)
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_edge_source
        FOREIGN KEY (source_vertex_id)
        REFERENCES vertices(vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_edge_target
        FOREIGN KEY (target_vertex_id)
        REFERENCES vertices(vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT no_duplicate_edge
        UNIQUE (graph_id, source_vertex_id, target_vertex_id),

    CONSTRAINT valid_edge_weight
        CHECK (
            weight > '-Infinity'::numeric
            AND weight < 'Infinity'::numeric
        )
);

CREATE INDEX IF NOT EXISTS idx_edges_source
    ON edges(graph_id, source_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edges_target
    ON edges(graph_id, target_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edges_weight
    ON edges(graph_id, weight);

-- ------------------------------------------------------------
-- 4. GRAPH INTEGRITY TRIGGER
--
-- An edge must connect vertices belonging to its graph.
-- Undirected edges are stored once using canonical ordering.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_graph_type VARCHAR(15);
    v_weighted BOOLEAN;
    v_source_graph BIGINT;
    v_target_graph BIGINT;
BEGIN
    SELECT graph_type, weighted
    INTO v_graph_type, v_weighted
    FROM graphs
    WHERE graph_id = NEW.graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', NEW.graph_id;
    END IF;

    SELECT graph_id
    INTO v_source_graph
    FROM vertices
    WHERE vertex_id = NEW.source_vertex_id;

    SELECT graph_id
    INTO v_target_graph
    FROM vertices
    WHERE vertex_id = NEW.target_vertex_id;

    IF v_source_graph IS NULL OR v_target_graph IS NULL THEN
        RAISE EXCEPTION 'Source or target vertex does not exist';
    END IF;

    IF v_source_graph <> NEW.graph_id
       OR v_target_graph <> NEW.graph_id THEN
        RAISE EXCEPTION
            'Both vertices must belong to the specified graph';
    END IF;

    IF NOT v_weighted AND NEW.weight <> 1 THEN
        RAISE EXCEPTION
            'Unweighted graph edges must have weight 1';
    END IF;

    IF v_graph_type = 'UNDIRECTED'
       AND NEW.source_vertex_id >= NEW.target_vertex_id THEN
        RAISE EXCEPTION
            'Undirected edges must use canonical vertex ordering';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_graph_edge ON edges;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT OR UPDATE ON edges
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- ------------------------------------------------------------
-- 5. GRAPH DATASET
-- ------------------------------------------------------------

INSERT INTO graphs (
    graph_name,
    graph_type,
    weighted,
    description
)
VALUES
(
    'social_network',
    'UNDIRECTED',
    FALSE,
    'Unweighted network of social relationships'
),
(
    'service_dependencies',
    'DIRECTED',
    FALSE,
    'Directed application dependency network'
),
(
    'transport_network',
    'UNDIRECTED',
    TRUE,
    'Weighted transportation network'
)
ON CONFLICT (graph_name) DO NOTHING;

-- ------------------------------------------------------------
-- 6. SAMPLE VERTICES
-- ------------------------------------------------------------

INSERT INTO vertices (
    graph_id,
    vertex_key,
    vertex_label,
    vertex_type
)
SELECT
    g.graph_id,
    v.vertex_key,
    v.vertex_label,
    v.vertex_type
FROM graphs g
CROSS JOIN (
    VALUES
        ('A', 'Vertex A', 'PERSON'),
        ('B', 'Vertex B', 'PERSON'),
        ('C', 'Vertex C', 'PERSON'),
        ('D', 'Vertex D', 'PERSON'),
        ('E', 'Vertex E', 'PERSON'),
        ('F', 'Isolated Vertex F', 'PERSON')
) AS v(vertex_key, vertex_label, vertex_type)
WHERE g.graph_name = 'social_network'
ON CONFLICT (graph_id, vertex_key) DO NOTHING;

INSERT INTO vertices (
    graph_id,
    vertex_key,
    vertex_label,
    vertex_type
)
SELECT
    g.graph_id,
    v.vertex_key,
    v.vertex_label,
    'SERVICE'
FROM graphs g
CROSS JOIN (
    VALUES
        ('FRONTEND', 'Frontend'),
        ('API', 'API Service'),
        ('DATABASE', 'Database'),
        ('CACHE', 'Cache'),
        ('BACKUP', 'Backup Service')
) AS v(vertex_key, vertex_label)
WHERE g.graph_name = 'service_dependencies'
ON CONFLICT (graph_id, vertex_key) DO NOTHING;

INSERT INTO vertices (
    graph_id,
    vertex_key,
    vertex_label,
    vertex_type
)
SELECT
    g.graph_id,
    v.vertex_key,
    v.vertex_label,
    'CITY'
FROM graphs g
CROSS JOIN (
    VALUES
        ('A', 'City A'),
        ('B', 'City B'),
        ('C', 'City C'),
        ('D', 'City D'),
        ('E', 'City E')
) AS v(vertex_key, vertex_label)
WHERE g.graph_name = 'transport_network'
ON CONFLICT (graph_id, vertex_key) DO NOTHING;

-- ------------------------------------------------------------
-- 7. INSERT EDGES
-- ------------------------------------------------------------

-- Undirected graph: store each relationship once.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    target.vertex_id,
    1
FROM graphs g
JOIN vertices source
    ON source.graph_id = g.graph_id
JOIN vertices target
    ON target.graph_id = g.graph_id
JOIN (
    VALUES
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('C', 'D'),
        ('D', 'E')
) AS e(source_key, target_key)
    ON source.vertex_key = e.source_key
   AND target.vertex_key = e.target_key
WHERE g.graph_name = 'social_network'
ON CONFLICT DO NOTHING;

-- Directed graph: source and target ordering is meaningful.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    target.vertex_id,
    1
FROM graphs g
JOIN vertices source
    ON source.graph_id = g.graph_id
JOIN vertices target
    ON target.graph_id = g.graph_id
JOIN (
    VALUES
        ('FRONTEND', 'API'),
        ('API', 'DATABASE'),
        ('API', 'CACHE'),
        ('DATABASE', 'BACKUP'),
        ('CACHE', 'DATABASE')
) AS e(source_key, target_key)
    ON source.vertex_key = e.source_key
   AND target.vertex_key = e.target_key
WHERE g.graph_name = 'service_dependencies'
ON CONFLICT DO NOTHING;

-- Weighted graph.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    target.vertex_id,
    e.weight
FROM graphs g
JOIN vertices source
    ON source.graph_id = g.graph_id
JOIN vertices target
    ON target.graph_id = g.graph_id
JOIN (
    VALUES
        ('A', 'B', 4::NUMERIC),
        ('A', 'C', 2::NUMERIC),
        ('B', 'C', 1::NUMERIC),
        ('B', 'D', 5::NUMERIC),
        ('C', 'D', 8::NUMERIC),
        ('D', 'E', 2::NUMERIC)
) AS e(source_key, target_key, weight)
    ON source.vertex_key = e.source_key
   AND target.vertex_key = e.target_key
WHERE g.graph_name = 'transport_network'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 8. GRAPH ADJACENCY VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_adjacency AS
SELECT
    g.graph_name,
    g.graph_type,
    g.weighted,
    source.vertex_key AS source_vertex,
    target.vertex_key AS target_vertex,
    e.weight
FROM edges e
JOIN graphs g
    ON g.graph_id = e.graph_id
JOIN vertices source
    ON source.vertex_id = e.source_vertex_id
JOIN vertices target
    ON target.vertex_id = e.target_vertex_id;

-- ------------------------------------------------------------
-- 9. DEGREE CALCULATIONS
--
-- Undirected degree counts each incident edge.
-- Directed degree distinguishes incoming and outgoing edges.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW vertex_degrees AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    v.vertex_id,
    v.vertex_key,
    CASE
        WHEN g.graph_type = 'UNDIRECTED' THEN
            (
                SELECT COUNT(*)
                FROM edges e
                WHERE e.graph_id = g.graph_id
                  AND (
                      e.source_vertex_id = v.vertex_id
                      OR e.target_vertex_id = v.vertex_id
                  )
            )
        ELSE NULL
    END AS degree,
    (
        SELECT COUNT(*)
        FROM edges e
        WHERE e.graph_id = g.graph_id
          AND e.target_vertex_id = v.vertex_id
    ) AS in_degree,
    (
        SELECT COUNT(*)
        FROM edges e
        WHERE e.graph_id = g.graph_id
          AND e.source_vertex_id = v.vertex_id
    ) AS out_degree
FROM graphs g
JOIN vertices v
    ON v.graph_id = g.graph_id;

-- ------------------------------------------------------------
-- 10. GRAPH STATISTICS
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    g.weighted,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    COALESCE(
        SUM(
            CASE
                WHEN d.degree = 0 THEN 1
                ELSE 0
            END
        ),
        0
    ) AS isolated_vertex_count
FROM graphs g
LEFT JOIN vertices v
    ON v.graph_id = g.graph_id
LEFT JOIN edges e
    ON e.graph_id = g.graph_id
LEFT JOIN vertex_degrees d
    ON d.vertex_id = v.vertex_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_type,
    g.weighted;

-- ------------------------------------------------------------
-- 11. ADJACENCY RETRIEVAL FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_neighbors(
    p_graph_id BIGINT,
    p_vertex_key VARCHAR
)
RETURNS TABLE (
    neighbor_key VARCHAR,
    edge_weight NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_vertex_id BIGINT;
BEGIN
    SELECT vertex_id
    INTO v_vertex_id
    FROM vertices
    WHERE graph_id = p_graph_id
      AND vertex_key = p_vertex_key;

    IF v_vertex_id IS NULL THEN
        RAISE EXCEPTION 'Vertex % not found', p_vertex_key;
    END IF;

    RETURN QUERY
    SELECT
        neighbor.vertex_key,
        e.weight
    FROM edges e
    JOIN graphs g
        ON g.graph_id = e.graph_id
    JOIN vertices neighbor
        ON neighbor.vertex_id =
            CASE
                WHEN e.source_vertex_id = v_vertex_id
                    THEN e.target_vertex_id
                ELSE e.source_vertex_id
            END
    WHERE e.graph_id = p_graph_id
      AND (
          e.source_vertex_id = v_vertex_id
          OR (
              g.graph_type = 'UNDIRECTED'
              AND e.target_vertex_id = v_vertex_id
          )
      )
    ORDER BY neighbor.vertex_key;
END;
$$;

-- ------------------------------------------------------------
-- 12. BREADTH-FIRST SEARCH
--
-- Recursive CTE maintains a path-local visited array.
-- The search returns each reachable vertex once.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_bfs(
    p_graph_id BIGINT,
    p_start_key VARCHAR
)
RETURNS TABLE (
    vertex_key VARCHAR,
    depth INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_start_id BIGINT;
BEGIN
    SELECT vertex_id
    INTO v_start_id
    FROM vertices
    WHERE graph_id = p_graph_id
      AND vertex_key = p_start_key;

    IF v_start_id IS NULL THEN
        RAISE EXCEPTION 'Starting vertex does not exist';
    END IF;

    RETURN QUERY
    WITH RECURSIVE traversal(
        current_id,
        current_depth,
        visited_path
    ) AS (
        SELECT
            v_start_id,
            0,
            ARRAY[v_start_id]

        UNION ALL

        SELECT
            next_vertex.vertex_id,
            traversal.current_depth + 1,
            traversal.visited_path || next_vertex.vertex_id
        FROM traversal
        JOIN edges e
            ON e.graph_id = p_graph_id
           AND (
               e.source_vertex_id = traversal.current_id
               OR (
                   (
                       SELECT graph_type
                       FROM graphs
                       WHERE graph_id = p_graph_id
                   ) = 'UNDIRECTED'
                   AND e.target_vertex_id = traversal.current_id
               )
           )
        JOIN vertices next_vertex
            ON next_vertex.vertex_id =
                CASE
                    WHEN e.source_vertex_id = traversal.current_id
                        THEN e.target_vertex_id
                    ELSE e.source_vertex_id
                END
        WHERE NOT next_vertex.vertex_id =
            ANY(traversal.visited_path)
    )
    SELECT
        v.vertex_key,
        MIN(t.current_depth)::INTEGER
    FROM traversal t
    JOIN vertices v
        ON v.vertex_id = t.current_id
    GROUP BY v.vertex_key
    ORDER BY MIN(t.current_depth), v.vertex_key;
END;
$$;

-- ------------------------------------------------------------
-- 13. CONNECTED COMPONENTS
--
-- Applicable to undirected graphs.
-- Repeated reachability identifies the minimum vertex ID
-- in each connected component as its component identifier.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_components(
    p_graph_id BIGINT
)
RETURNS TABLE (
    vertex_key VARCHAR,
    component_id BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graphs
        WHERE graph_id = p_graph_id
          AND graph_type = 'UNDIRECTED'
    ) THEN
        RAISE EXCEPTION
            'Connected components require an undirected graph';
    END IF;

    RETURN QUERY
    WITH RECURSIVE reachability(
        root_id,
        current_id,
        visited_path
    ) AS (
        SELECT
            v.vertex_id,
            v.vertex_id,
            ARRAY[v.vertex_id]
        FROM vertices v
        WHERE v.graph_id = p_graph_id

        UNION ALL

        SELECT
            r.root_id,
            next_vertex.vertex_id,
            r.visited_path || next_vertex.vertex_id
        FROM reachability r
        JOIN edges e
            ON e.graph_id = p_graph_id
           AND (
               (
                   e.source_vertex_id = r.current_id
                   AND e.target_vertex_id <> ALL(r.visited_path)
               )
               OR
               (
                   e.target_vertex_id = r.current_id
                   AND e.source_vertex_id <> ALL(r.visited_path)
               )
           )
        JOIN vertices next_vertex
            ON next_vertex.vertex_id =
                CASE
                    WHEN e.source_vertex_id = r.current_id
                        THEN e.target_vertex_id
                    ELSE e.source_vertex_id
                END
    ),
    component_map AS (
        SELECT
            current_id,
            MIN(root_id) AS component_id
        FROM reachability
        GROUP BY current_id
    )
    SELECT
        v.vertex_key,
        cm.component_id
    FROM component_map cm
    JOIN vertices v
        ON v.vertex_id = cm.current_id
    ORDER BY cm.component_id, v.vertex_key;
END;
$$;

-- ------------------------------------------------------------
-- 14. GRAPH ELIGIBILITY VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph(
    p_graph_id BIGINT
)
RETURNS TABLE (
    validation_rule TEXT,
    passed BOOLEAN,
    details TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_type VARCHAR(15);
    v_weighted BOOLEAN;
BEGIN
    SELECT graph_type, weighted
    INTO v_type, v_weighted
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    RETURN QUERY
    SELECT
        'vertices_exist'::TEXT,
        COUNT(*) > 0,
        'A graph should contain at least one vertex'::TEXT
    FROM vertices
    WHERE graph_id = p_graph_id;

    RETURN QUERY
    SELECT
        'edge_weight_policy'::TEXT,
        COUNT(*) = 0,
        'Unweighted graphs must contain unit-weight edges'::TEXT
    FROM edges
    WHERE graph_id = p_graph_id
      AND NOT v_weighted
      AND weight <> 1;

    RETURN QUERY
    SELECT
        'no_self_loops'::TEXT,
        COUNT(*) = 0,
        'Self-loops are permitted by the schema but reported here'::TEXT
    FROM edges
    WHERE graph_id = p_graph_id
      AND source_vertex_id = target_vertex_id;

    RETURN QUERY
    SELECT
        'valid_graph_type'::TEXT,
        v_type IN ('DIRECTED', 'UNDIRECTED'),
        'Graph type must be directed or undirected'::TEXT;
END;
$$;

-- ------------------------------------------------------------
-- 15. SAMPLE RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- Graph catalogue.
SELECT *
FROM graphs
ORDER BY graph_name;

-- Vertex catalogue.
SELECT
    g.graph_name,
    v.vertex_key,
    v.vertex_label
FROM vertices v
JOIN graphs g USING (graph_id)
ORDER BY g.graph_name, v.vertex_key;

-- Edge catalogue.
SELECT *
FROM graph_adjacency
ORDER BY graph_name, source_vertex, target_vertex;

-- Neighbors of vertex A in the social network.
SELECT *
FROM get_neighbors(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'social_network'),
    'A'
);

-- ------------------------------------------------------------
-- 16. DEGREE EVALUATION
-- ------------------------------------------------------------

SELECT
    graph_name,
    vertex_key,
    degree,
    in_degree,
    out_degree
FROM vertex_degrees
ORDER BY graph_name, vertex_key;

-- ------------------------------------------------------------
-- 17. AGGREGATION AND REPORTING
-- ------------------------------------------------------------

SELECT *
FROM graph_statistics
ORDER BY graph_name;

-- Average degree in undirected graphs.
SELECT
    g.graph_name,
    AVG(d.degree::NUMERIC) AS average_degree
FROM graphs g
JOIN vertex_degrees d
    ON d.graph_id = g.graph_id
WHERE g.graph_type = 'UNDIRECTED'
GROUP BY g.graph_name;

-- Highest-degree vertices.
SELECT
    graph_name,
    vertex_key,
    degree
FROM vertex_degrees
WHERE graph_type = 'UNDIRECTED'
ORDER BY degree DESC NULLS LAST, graph_name
LIMIT 10;

-- ------------------------------------------------------------
-- 18. BFS WORKFLOW
-- ------------------------------------------------------------

SELECT *
FROM graph_bfs(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'social_network'),
    'A'
);

-- ------------------------------------------------------------
-- 19. CONNECTED COMPONENT REPORT
-- ------------------------------------------------------------

SELECT *
FROM graph_components(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'social_network')
);

-- ------------------------------------------------------------
-- 20. NEGATIVE AND INVALID CASES
-- ------------------------------------------------------------

-- The following statements are intentionally commented out.
-- Execute separately to test database constraints.

-- Invalid: unweighted graph with a non-unit weight.
-- INSERT INTO edges(graph_id, source_vertex_id,
--                   target_vertex_id, weight)
-- VALUES (1, 1, 2, 5);

-- Invalid: duplicate edge.
-- Insert an existing source/target pair again.

-- Invalid: edge connecting vertices from different graphs.
-- Insert a social-network edge referencing a transport vertex.

-- Invalid: noncanonical ordering for an undirected edge.
-- Reverse the vertex identifiers in an existing edge.

-- ------------------------------------------------------------
-- 21. TRANSACTIONAL EDGE INSERTION
-- ------------------------------------------------------------

SAVEPOINT before_additional_edge;

INSERT INTO edges (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    target.vertex_id,
    1
FROM graphs g
JOIN vertices source
    ON source.graph_id = g.graph_id
JOIN vertices target
    ON target.graph_id = g.graph_id
WHERE g.graph_name = 'social_network'
  AND source.vertex_key = 'A'
  AND target.vertex_key = 'D'
  AND source.vertex_id < target.vertex_id
ON CONFLICT DO NOTHING;

-- Validate the updated graph before committing the transaction.
SELECT *
FROM validate_graph(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'social_network')
);

-- The savepoint allows selective rollback if validation fails.
-- The demonstration keeps the inserted edge.

RELEASE SAVEPOINT before_additional_edge;

COMMIT;

-- ------------------------------------------------------------
-- 22. OPERATIONAL QUERIES
-- ------------------------------------------------------------

SET search_path TO graph_lab, public;

-- Isolated vertices.
SELECT
    graph_name,
    vertex_key
FROM vertex_degrees
WHERE graph_type = 'UNDIRECTED'
  AND degree = 0;

-- Vertices with the greatest incoming dependency count.
SELECT
    graph_name,
    vertex_key,
    in_degree
FROM vertex_degrees
WHERE graph_type = 'DIRECTED'
ORDER BY in_degree DESC;

-- Vertices with the greatest outgoing dependency count.
SELECT
    graph_name,
    vertex_key,
    out_degree
FROM vertex_degrees
WHERE graph_type = 'DIRECTED'
ORDER BY out_degree DESC;

-- Graph validation report.
SELECT
    g.graph_name,
    v.validation_rule,
    v.passed,
    v.details
FROM graphs g
CROSS JOIN LATERAL validate_graph(g.graph_id) v
ORDER BY g.graph_name, v.validation_rule;
