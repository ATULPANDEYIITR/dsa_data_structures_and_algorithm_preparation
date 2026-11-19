/*
    GRAPH REPRESENTATION DATABASE
    PostgreSQL 15+

    Models:
    - Graphs
    - Vertices
    - Edges
    - Directed and undirected relationships
    - Weighted and unweighted graphs
    - Adjacency matrix queries
    - Adjacency list queries
    - BFS reachability
    - Graph statistics
    - Integrity enforcement
    - Graph mutation
    - Representation comparison

    Execute as a database user authorized to create schemas.
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- -----------------------------------------------------
-- 1. DOMAIN TYPES
-- -----------------------------------------------------

CREATE TYPE graph_lab.graph_direction AS ENUM (
    'DIRECTED',
    'UNDIRECTED'
);

CREATE TYPE graph_lab.graph_weight_mode AS ENUM (
    'WEIGHTED',
    'UNWEIGHTED'
);

-- -----------------------------------------------------
-- 2. GRAPH TABLE
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS graph_lab.graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    direction graph_lab.graph_direction NOT NULL,

    weight_mode graph_lab.graph_weight_mode NOT NULL,

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT graph_name_nonempty
        CHECK (length(trim(graph_name)) > 0)
);

-- -----------------------------------------------------
-- 3. VERTEX TABLE
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS graph_lab.vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    vertex_key VARCHAR(150) NOT NULL,

    vertex_label VARCHAR(200),

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_vertex_graph
        FOREIGN KEY (graph_id)
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_vertex_per_graph
        UNIQUE (graph_id, vertex_key),

    CONSTRAINT vertex_key_nonempty
        CHECK (length(trim(vertex_key)) > 0),

    CONSTRAINT metadata_object
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_vertices_graph
    ON graph_lab.vertices(graph_id);

-- -----------------------------------------------------
-- 4. EDGE TABLE
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS graph_lab.edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex_id BIGINT NOT NULL,

    target_vertex_id BIGINT NOT NULL,

    weight NUMERIC(18, 6) NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_edge_graph
        FOREIGN KEY (graph_id)
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_edge_source
        FOREIGN KEY (source_vertex_id)
        REFERENCES graph_lab.vertices(vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_edge_target
        FOREIGN KEY (target_vertex_id)
        REFERENCES graph_lab.vertices(vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT edge_weight_finite
        CHECK (
            weight > '-Infinity'::NUMERIC
            AND weight < 'Infinity'::NUMERIC
        ),

    CONSTRAINT unique_directed_edge
        UNIQUE (
            graph_id,
            source_vertex_id,
            target_vertex_id
        )
);

CREATE INDEX IF NOT EXISTS idx_edges_source
    ON graph_lab.edges(graph_id, source_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edges_target
    ON graph_lab.edges(graph_id, target_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph_weight
    ON graph_lab.edges(graph_id, weight);

-- -----------------------------------------------------
-- 5. GRAPH INTEGRITY TRIGGER
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.validate_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    graph_direction_value graph_lab.graph_direction;
    graph_weight_mode_value graph_lab.graph_weight_mode;
    source_graph_id BIGINT;
    target_graph_id BIGINT;
BEGIN
    SELECT direction, weight_mode
    INTO graph_direction_value, graph_weight_mode_value
    FROM graph_lab.graphs
    WHERE graph_id = NEW.graph_id
    FOR KEY SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Graph % does not exist',
            NEW.graph_id;
    END IF;

    SELECT graph_id
    INTO source_graph_id
    FROM graph_lab.vertices
    WHERE vertex_id = NEW.source_vertex_id;

    SELECT graph_id
    INTO target_graph_id
    FROM graph_lab.vertices
    WHERE vertex_id = NEW.target_vertex_id;

    IF source_graph_id IS DISTINCT FROM NEW.graph_id
       OR target_graph_id IS DISTINCT FROM NEW.graph_id THEN
        RAISE EXCEPTION
            'Both endpoints must belong to graph %',
            NEW.graph_id;
    END IF;

    IF graph_weight_mode_value = 'UNWEIGHTED'
       AND NEW.weight <> 1 THEN
        RAISE EXCEPTION
            'Unweighted graphs only accept weight 1';
    END IF;

    IF graph_direction_value = 'UNDIRECTED'
       AND NEW.source_vertex_id > NEW.target_vertex_id THEN
        RAISE EXCEPTION
            'Undirected edges must use canonical endpoint ordering';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_edge
    ON graph_lab.edges;

CREATE TRIGGER trg_validate_edge
BEFORE INSERT OR UPDATE
ON graph_lab.edges
FOR EACH ROW
EXECUTE FUNCTION graph_lab.validate_edge();

-- -----------------------------------------------------
-- 6. ADJACENCY LIST VIEW
-- -----------------------------------------------------

CREATE OR REPLACE VIEW graph_lab.adjacency_list AS
SELECT
    v.graph_id,
    v.vertex_id,
    v.vertex_key AS vertex,
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'vertex_id', target.vertex_id,
                'vertex', target.vertex_key,
                'weight', e.weight
            )
            ORDER BY target.vertex_key
        ) FILTER (WHERE e.edge_id IS NOT NULL),
        '[]'::jsonb
    ) AS neighbors
FROM graph_lab.vertices v
LEFT JOIN graph_lab.edges e
    ON e.graph_id = v.graph_id
   AND e.source_vertex_id = v.vertex_id
LEFT JOIN graph_lab.vertices target
    ON target.vertex_id = e.target_vertex_id
GROUP BY
    v.graph_id,
    v.vertex_id,
    v.vertex_key;

-- -----------------------------------------------------
-- 7. ADJACENCY MATRIX FUNCTION
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.get_adjacency_matrix(
    p_graph_id BIGINT
)
RETURNS TABLE (
    source_vertex VARCHAR,
    target_vertex VARCHAR,
    edge_weight NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        source.vertex_key,
        target.vertex_key,
        e.weight
    FROM graph_lab.vertices source
    CROSS JOIN graph_lab.vertices target
    LEFT JOIN graph_lab.edges e
        ON e.graph_id = source.graph_id
       AND e.source_vertex_id = source.vertex_id
       AND e.target_vertex_id = target.vertex_id
    WHERE source.graph_id = p_graph_id
      AND target.graph_id = p_graph_id
    ORDER BY
        source.vertex_key,
        target.vertex_key;
$$;

-- -----------------------------------------------------
-- 8. GRAPH STATISTICS
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.get_graph_statistics(
    p_graph_id BIGINT
)
RETURNS TABLE (
    vertex_count BIGINT,
    edge_count BIGINT,
    matrix_cells BIGINT,
    adjacency_entries BIGINT,
    density NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    WITH counts AS (
        SELECT
            g.direction,
            (
                SELECT COUNT(*)
                FROM graph_lab.vertices v
                WHERE v.graph_id = g.graph_id
            ) AS vertex_total,
            (
                SELECT COUNT(*)
                FROM graph_lab.edges e
                WHERE e.graph_id = g.graph_id
            ) AS edge_total
        FROM graph_lab.graphs g
        WHERE g.graph_id = p_graph_id
    )
    SELECT
        vertex_total,
        edge_total,
        vertex_total * vertex_total,
        CASE
            WHEN direction = 'UNDIRECTED'
                THEN edge_total * 2
            ELSE edge_total
        END,
        CASE
            WHEN direction = 'DIRECTED'
                 AND vertex_total > 1
                THEN edge_total::NUMERIC /
                    (vertex_total * (vertex_total - 1))
            WHEN direction = 'UNDIRECTED'
                 AND vertex_total > 1
                THEN edge_total::NUMERIC /
                    (vertex_total * (vertex_total - 1) / 2)
            ELSE 0
        END
    FROM counts;
$$;

-- -----------------------------------------------------
-- 9. EDGE INSERTION FUNCTION
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.add_edge(
    p_graph_id BIGINT,
    p_source_key VARCHAR,
    p_target_key VARCHAR,
    p_weight NUMERIC DEFAULT 1
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    source_id BIGINT;
    target_id BIGINT;
    direction_value graph_lab.graph_direction;
    new_edge_id BIGINT;
BEGIN
    SELECT direction
    INTO direction_value
    FROM graph_lab.graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph: %', p_graph_id;
    END IF;

    SELECT vertex_id
    INTO source_id
    FROM graph_lab.vertices
    WHERE graph_id = p_graph_id
      AND vertex_key = p_source_key;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Unknown source vertex: %',
            p_source_key;
    END IF;

    SELECT vertex_id
    INTO target_id
    FROM graph_lab.vertices
    WHERE graph_id = p_graph_id
      AND vertex_key = p_target_key;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Unknown target vertex: %',
            p_target_key;
    END IF;

    IF direction_value = 'UNDIRECTED'
       AND source_id > target_id THEN
        new_edge_id := source_id;
        source_id := target_id;
        target_id := new_edge_id;
    END IF;

    INSERT INTO graph_lab.edges (
        graph_id,
        source_vertex_id,
        target_vertex_id,
        weight
    )
    VALUES (
        p_graph_id,
        source_id,
        target_id,
        p_weight
    )
    ON CONFLICT (
        graph_id,
        source_vertex_id,
        target_vertex_id
    )
    DO UPDATE SET
        weight = EXCLUDED.weight
    RETURNING edge_id INTO new_edge_id;

    RETURN new_edge_id;
END;
$$;

-- -----------------------------------------------------
-- 10. BREADTH-FIRST REACHABILITY
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.bfs(
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
    start_id BIGINT;
BEGIN
    SELECT vertex_id
    INTO start_id
    FROM graph_lab.vertices
    WHERE graph_id = p_graph_id
      AND vertex_key = p_start_key;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Starting vertex % does not exist',
            p_start_key;
    END IF;

    RETURN QUERY
    WITH RECURSIVE traversal AS (
        SELECT
            start_id AS current_id,
            0 AS current_depth,
            ARRAY[start_id]::BIGINT[] AS visited

        UNION ALL

        SELECT
            next_vertex.vertex_id,
            traversal.current_depth + 1,
            traversal.visited || next_vertex.vertex_id
        FROM traversal
        JOIN graph_lab.edges e
            ON e.graph_id = p_graph_id
           AND e.source_vertex_id = traversal.current_id
        JOIN graph_lab.vertices next_vertex
            ON next_vertex.vertex_id = e.target_vertex_id
           AND next_vertex.graph_id = p_graph_id
        WHERE NOT (
            next_vertex.vertex_id = ANY(traversal.visited)
        )

        UNION ALL

        SELECT
            previous_vertex.vertex_id,
            traversal.current_depth + 1,
            traversal.visited || previous_vertex.vertex_id
        FROM traversal
        JOIN graph_lab.graphs g
            ON g.graph_id = p_graph_id
           AND g.direction = 'UNDIRECTED'
        JOIN graph_lab.edges e
            ON e.graph_id = p_graph_id
           AND e.target_vertex_id = traversal.current_id
        JOIN graph_lab.vertices previous_vertex
            ON previous_vertex.vertex_id = e.source_vertex_id
           AND previous_vertex.graph_id = p_graph_id
        WHERE NOT (
            previous_vertex.vertex_id = ANY(traversal.visited)
        )
    )
    SELECT
        v.vertex_key,
        MIN(t.current_depth)::INTEGER
    FROM traversal t
    JOIN graph_lab.vertices v
        ON v.vertex_id = t.current_id
    GROUP BY v.vertex_key
    ORDER BY MIN(t.current_depth), v.vertex_key;
END;
$$;

-- -----------------------------------------------------
-- 11. SAMPLE GRAPHS
-- -----------------------------------------------------

INSERT INTO graph_lab.graphs (
    graph_name,
    direction,
    weight_mode,
    description
)
VALUES
(
    'CITY_NETWORK',
    'UNDIRECTED',
    'WEIGHTED',
    'Weighted transportation network'
),
(
    'SERVICE_DEPENDENCIES',
    'DIRECTED',
    'UNWEIGHTED',
    'Enterprise service dependency network'
),
(
    'SOCIAL_NETWORK',
    'UNDIRECTED',
    'UNWEIGHTED',
    'Undirected relationship network'
)
ON CONFLICT (graph_name) DO NOTHING;

-- -----------------------------------------------------
-- 12. SAMPLE VERTICES
-- -----------------------------------------------------

INSERT INTO graph_lab.vertices (
    graph_id,
    vertex_key,
    vertex_label,
    metadata
)
SELECT
    g.graph_id,
    vertex_data.vertex_key,
    vertex_data.vertex_label,
    vertex_data.metadata::jsonb
FROM graph_lab.graphs g
CROSS JOIN (
    VALUES
        ('CITY_NETWORK', 'A', 'City A', '{"region":"North"}'),
        ('CITY_NETWORK', 'B', 'City B', '{"region":"North"}'),
        ('CITY_NETWORK', 'C', 'City C', '{"region":"West"}'),
        ('CITY_NETWORK', 'D', 'City D', '{"region":"East"}'),
        ('CITY_NETWORK', 'E', 'City E', '{"region":"South"}'),
        ('CITY_NETWORK', 'F', 'City F', '{"region":"South"}'),

        ('SERVICE_DEPENDENCIES', 'API', 'API Gateway', '{}'),
        ('SERVICE_DEPENDENCIES', 'AUTH', 'Authentication', '{}'),
        ('SERVICE_DEPENDENCIES', 'DB', 'Database', '{}'),
        ('SERVICE_DEPENDENCIES', 'CACHE', 'Cache Service', '{}'),
        ('SERVICE_DEPENDENCIES', 'QUEUE', 'Message Queue', '{}'),

        ('SOCIAL_NETWORK', 'USER_A', 'User A', '{}'),
        ('SOCIAL_NETWORK', 'USER_B', 'User B', '{}'),
        ('SOCIAL_NETWORK', 'USER_C', 'User C', '{}')
) AS vertex_data(
    graph_name,
    vertex_key,
    vertex_label,
    metadata
)
WHERE g.graph_name = vertex_data.graph_name
ON CONFLICT (graph_id, vertex_key) DO NOTHING;

-- -----------------------------------------------------
-- 13. SAMPLE EDGES
-- -----------------------------------------------------

DO $$
DECLARE
    city_id BIGINT;
    service_id BIGINT;
    social_id BIGINT;
BEGIN
    SELECT graph_id INTO city_id
    FROM graph_lab.graphs
    WHERE graph_name = 'CITY_NETWORK';

    PERFORM graph_lab.add_edge(city_id, 'A', 'B', 4);
    PERFORM graph_lab.add_edge(city_id, 'A', 'C', 2);
    PERFORM graph_lab.add_edge(city_id, 'B', 'C', 1);
    PERFORM graph_lab.add_edge(city_id, 'B', 'D', 5);
    PERFORM graph_lab.add_edge(city_id, 'C', 'D', 8);
    PERFORM graph_lab.add_edge(city_id, 'C', 'E', 10);
    PERFORM graph_lab.add_edge(city_id, 'D', 'E', 2);
    PERFORM graph_lab.add_edge(city_id, 'D', 'F', 6);
    PERFORM graph_lab.add_edge(city_id, 'E', 'F', 3);

    SELECT graph_id INTO service_id
    FROM graph_lab.graphs
    WHERE graph_name = 'SERVICE_DEPENDENCIES';

    PERFORM graph_lab.add_edge(service_id, 'API', 'AUTH');
    PERFORM graph_lab.add_edge(service_id, 'API', 'CACHE');
    PERFORM graph_lab.add_edge(service_id, 'AUTH', 'DB');
    PERFORM graph_lab.add_edge(service_id, 'CACHE', 'DB');
    PERFORM graph_lab.add_edge(service_id, 'API', 'QUEUE');

    SELECT graph_id INTO social_id
    FROM graph_lab.graphs
    WHERE graph_name = 'SOCIAL_NETWORK';

    PERFORM graph_lab.add_edge(social_id, 'USER_A', 'USER_B');
    PERFORM graph_lab.add_edge(social_id, 'USER_B', 'USER_C');
END;
$$;

-- -----------------------------------------------------
-- 14. RETRIEVAL: GRAPH CATALOG
-- -----------------------------------------------------

SELECT
    g.graph_id,
    g.graph_name,
    g.direction,
    g.weight_mode,
    COUNT(DISTINCT v.vertex_id) AS vertices,
    COUNT(DISTINCT e.edge_id) AS edges
FROM graph_lab.graphs g
LEFT JOIN graph_lab.vertices v
    ON v.graph_id = g.graph_id
LEFT JOIN graph_lab.edges e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.direction,
    g.weight_mode
ORDER BY g.graph_name;

-- -----------------------------------------------------
-- 15. RETRIEVAL: ADJACENCY LIST
-- -----------------------------------------------------

SELECT
    g.graph_name,
    a.vertex,
    a.neighbors
FROM graph_lab.adjacency_list a
JOIN graph_lab.graphs g
    ON g.graph_id = a.graph_id
WHERE g.graph_name = 'CITY_NETWORK'
ORDER BY a.vertex;

-- -----------------------------------------------------
-- 16. RETRIEVAL: ADJACENCY MATRIX
-- -----------------------------------------------------

SELECT
    source_vertex,
    target_vertex,
    edge_weight
FROM graph_lab.get_adjacency_matrix(
    (
        SELECT graph_id
        FROM graph_lab.graphs
        WHERE graph_name = 'CITY_NETWORK'
    )
);

-- -----------------------------------------------------
-- 17. AGGREGATION: DEGREE DISTRIBUTION
-- -----------------------------------------------------

WITH outgoing AS (
    SELECT
        v.vertex_id,
        v.vertex_key,
        COUNT(e.edge_id) AS out_degree
    FROM graph_lab.vertices v
    LEFT JOIN graph_lab.edges e
        ON e.source_vertex_id = v.vertex_id
       AND e.graph_id = v.graph_id
    WHERE v.graph_id = (
        SELECT graph_id
        FROM graph_lab.graphs
        WHERE graph_name = 'CITY_NETWORK'
    )
    GROUP BY v.vertex_id, v.vertex_key
)
SELECT
    vertex_key,
    out_degree
FROM outgoing
ORDER BY out_degree DESC, vertex_key;

-- -----------------------------------------------------
-- 18. STATISTICS AND REPRESENTATION COMPARISON
-- -----------------------------------------------------

SELECT
    g.graph_name,
    s.vertex_count,
    s.edge_count,
    s.matrix_cells,
    s.adjacency_entries,
    ROUND(s.density, 4) AS density
FROM graph_lab.graphs g
CROSS JOIN LATERAL
    graph_lab.get_graph_statistics(g.graph_id) s
ORDER BY g.graph_name;

-- -----------------------------------------------------
-- 19. BREADTH-FIRST SEARCH
-- -----------------------------------------------------

SELECT
    vertex_key,
    depth
FROM graph_lab.bfs(
    (
        SELECT graph_id
        FROM graph_lab.graphs
        WHERE graph_name = 'CITY_NETWORK'
    ),
    'A'
);

-- -----------------------------------------------------
-- 20. ELIGIBILITY AND VALIDATION REPORT
-- -----------------------------------------------------

SELECT
    g.graph_name,
    v.vertex_key,
    CASE
        WHEN v.vertex_key IS NOT NULL THEN 'VALID'
        ELSE 'INVALID'
    END AS vertex_status,
    CASE
        WHEN COUNT(e.edge_id) >= 0 THEN 'CONSISTENT'
        ELSE 'INCONSISTENT'
    END AS relationship_status,
    COUNT(e.edge_id) AS outgoing_edges
FROM graph_lab.graphs g
JOIN graph_lab.vertices v
    ON v.graph_id = g.graph_id
LEFT JOIN graph_lab.edges e
    ON e.graph_id = v.graph_id
   AND e.source_vertex_id = v.vertex_id
GROUP BY
    g.graph_name,
    v.vertex_key
ORDER BY
    g.graph_name,
    v.vertex_key;

-- -----------------------------------------------------
-- 21. INVALID EDGE DEMONSTRATION
-- -----------------------------------------------------

DO $$
DECLARE
    city_id BIGINT;
BEGIN
    SELECT graph_id INTO city_id
    FROM graph_lab.graphs
    WHERE graph_name = 'CITY_NETWORK';

    BEGIN
        PERFORM graph_lab.add_edge(
            city_id,
            'A',
            'UNKNOWN',
            5
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected invalid endpoint rejection: %',
                SQLERRM;
    END;

    BEGIN
        PERFORM graph_lab.add_edge(
            city_id,
            'A',
            'B',
            5
        );
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'Unexpected duplicate handling failure';
    END;

    BEGIN
        INSERT INTO graph_lab.edges (
            graph_id,
            source_vertex_id,
            target_vertex_id,
            weight
        )
        SELECT
            g.graph_id,
            source.vertex_id,
            target.vertex_id,
            5
        FROM graph_lab.graphs g
        JOIN graph_lab.vertices source
            ON source.graph_id = g.graph_id
           AND source.vertex_key = 'API'
        JOIN graph_lab.vertices target
            ON target.graph_id = g.graph_id
           AND target.vertex_key = 'AUTH'
        WHERE g.graph_name = 'SERVICE_DEPENDENCIES';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Validation failure: %',
                SQLERRM;
    END;
END;
$$;

-- -----------------------------------------------------
-- 22. TRANSACTIONAL GRAPH MUTATION
-- -----------------------------------------------------

BEGIN;

DO $$
DECLARE
    city_id BIGINT;
BEGIN
    SELECT graph_id INTO city_id
    FROM graph_lab.graphs
    WHERE graph_name = 'CITY_NETWORK';

    PERFORM graph_lab.add_edge(
        city_id,
        'A',
        'F',
        12
    );
END;
$$;

-- Confirm the transactional edge.
SELECT
    source.vertex_key,
    target.vertex_key,
    e.weight
FROM graph_lab.edges e
JOIN graph_lab.vertices source
    ON source.vertex_id = e.source_vertex_id
JOIN graph_lab.vertices target
    ON target.vertex_id = e.target_vertex_id
WHERE e.graph_id = (
    SELECT graph_id
    FROM graph_lab.graphs
    WHERE graph_name = 'CITY_NETWORK'
)
AND (
    source.vertex_key = 'A'
    AND target.vertex_key = 'F'
);

COMMIT;

-- -----------------------------------------------------
-- 23. EDGE REMOVAL
-- -----------------------------------------------------

DELETE FROM graph_lab.edges e
USING graph_lab.graphs g,
      graph_lab.vertices source,
      graph_lab.vertices target
WHERE e.graph_id = g.graph_id
  AND e.source_vertex_id = source.vertex_id
  AND e.target_vertex_id = target.vertex_id
  AND g.graph_name = 'CITY_NETWORK'
  AND source.vertex_key = 'A'
  AND target.vertex_key = 'F';

-- -----------------------------------------------------
-- 24. FINAL REPORT
-- -----------------------------------------------------

SELECT
    g.graph_name,
    g.direction,
    g.weight_mode,
    s.vertex_count,
    s.edge_count,
    s.matrix_cells,
    s.adjacency_entries,
    ROUND(s.density, 4) AS density
FROM graph_lab.graphs g
CROSS JOIN LATERAL
    graph_lab.get_graph_statistics(g.graph_id) s
ORDER BY g.graph_name;

COMMIT;
