/*
 * Connected Components and Cycles in Graphs
 *
 * PostgreSQL relational graph model.
 *
 * Features:
 * - Graph and vertex management.
 * - Directed and undirected edge storage.
 * - Referential and structural constraints.
 * - Connected component computation using recursive CTEs.
 * - Undirected cycle detection.
 * - Directed cycle detection.
 * - Cycle reporting and graph validation.
 * - Indexed adjacency retrieval.
 *
 * Target: PostgreSQL 14+
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

DROP VIEW IF EXISTS graph_cycle_report CASCADE;
DROP VIEW IF EXISTS graph_component_report CASCADE;
DROP TABLE IF EXISTS graph_edges CASCADE;
DROP TABLE IF EXISTS graph_vertices CASCADE;
DROP TABLE IF EXISTS graphs CASCADE;

CREATE TABLE graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    graph_type VARCHAR(15) NOT NULL
        CHECK (graph_type IN ('DIRECTED', 'UNDIRECTED')),

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(graph_name)) > 0)
);

CREATE TABLE graph_vertices (
    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    vertex_id BIGINT NOT NULL,

    vertex_label VARCHAR(150),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (graph_id, vertex_id)
);

CREATE TABLE graph_edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex BIGINT NOT NULL,

    destination_vertex BIGINT NOT NULL,

    weight NUMERIC(12, 4) NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_source_vertex
        FOREIGN KEY (graph_id, source_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_destination_vertex
        FOREIGN KEY (graph_id, destination_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (weight >= 0)
);

-- Adjacency retrieval is a frequent graph operation.
CREATE INDEX idx_graph_edges_source
    ON graph_edges(graph_id, source_vertex);

CREATE INDEX idx_graph_edges_destination
    ON graph_edges(graph_id, destination_vertex);

CREATE INDEX idx_graph_vertices_graph
    ON graph_vertices(graph_id, vertex_id);

CREATE INDEX idx_graph_edges_pair
    ON graph_edges(graph_id, source_vertex, destination_vertex);

-- Validate graph identity before accepting an edge.
CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    selected_type VARCHAR(15);
BEGIN
    SELECT graph_type
    INTO selected_type
    FROM graphs
    WHERE graph_id = NEW.graph_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Graph % does not exist.',
            NEW.graph_id;
    END IF;

    IF selected_type = 'UNDIRECTED'
       AND NEW.source_vertex > NEW.destination_vertex THEN

        RAISE EXCEPTION
            'Undirected edges must use canonical vertex ordering.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT OR UPDATE ON graph_edges
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- Prevent duplicate edge representations.
CREATE UNIQUE INDEX uq_graph_edge
ON graph_edges (
    graph_id,
    source_vertex,
    destination_vertex
);

-- Register a graph and return its generated identifier.
CREATE OR REPLACE FUNCTION create_graph(
    p_name VARCHAR,
    p_type VARCHAR,
    p_description TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_graph_id BIGINT;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Graph name cannot be empty.';
    END IF;

    IF p_type NOT IN ('DIRECTED', 'UNDIRECTED') THEN
        RAISE EXCEPTION 'Invalid graph type: %', p_type;
    END IF;

    INSERT INTO graphs (
        graph_name,
        graph_type,
        description
    )
    VALUES (
        p_name,
        p_type,
        p_description
    )
    RETURNING graph_id INTO new_graph_id;

    RETURN new_graph_id;
END;
$$;

-- Add an edge. Undirected edges use canonical ordering.
CREATE OR REPLACE FUNCTION add_graph_edge(
    p_graph_id BIGINT,
    p_source BIGINT,
    p_destination BIGINT,
    p_weight NUMERIC DEFAULT 1
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    selected_type VARCHAR(15);
    normalized_source BIGINT;
    normalized_destination BIGINT;
    new_edge_id BIGINT;
BEGIN
    IF p_weight < 0 THEN
        RAISE EXCEPTION 'Negative edge weights are not permitted.';
    END IF;

    SELECT graph_type
    INTO selected_type
    FROM graphs
    WHERE graph_id = p_graph_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph %', p_graph_id;
    END IF;

    IF selected_type = 'UNDIRECTED' THEN
        normalized_source := LEAST(p_source, p_destination);
        normalized_destination := GREATEST(p_source, p_destination);
    ELSE
        normalized_source := p_source;
        normalized_destination := p_destination;
    END IF;

    INSERT INTO graph_edges (
        graph_id,
        source_vertex,
        destination_vertex,
        weight
    )
    VALUES (
        p_graph_id,
        normalized_source,
        normalized_destination,
        p_weight
    )
    RETURNING edge_id INTO new_edge_id;

    RETURN new_edge_id;
END;
$$;

-- Expand undirected edges in both directions.
CREATE OR REPLACE VIEW graph_adjacency AS
SELECT
    graph_id,
    source_vertex AS source,
    destination_vertex AS destination
FROM graph_edges

UNION ALL

SELECT
    e.graph_id,
    e.destination_vertex,
    e.source_vertex
FROM graph_edges e
JOIN graphs g USING (graph_id)
WHERE g.graph_type = 'UNDIRECTED'
  AND e.source_vertex <> e.destination_vertex;

-- Recursive reachability for each possible starting vertex.
-- The visited path prevents infinite recursion in cyclic graphs.
CREATE OR REPLACE VIEW graph_component_report AS
WITH RECURSIVE reachability (
    graph_id,
    root_vertex,
    current_vertex,
    visited
) AS (
    SELECT
        v.graph_id,
        v.vertex_id,
        v.vertex_id,
        ARRAY[v.vertex_id]::BIGINT[]
    FROM graph_vertices v
    JOIN graphs g USING (graph_id)
    WHERE g.graph_type = 'UNDIRECTED'

    UNION ALL

    SELECT
        r.graph_id,
        r.root_vertex,
        a.destination,
        r.visited || a.destination
    FROM reachability r
    JOIN graph_adjacency a
      ON a.graph_id = r.graph_id
     AND a.source = r.current_vertex
    WHERE NOT a.destination = ANY(r.visited)
),
representatives AS (
    SELECT
        graph_id,
        current_vertex AS vertex_id,
        MIN(root_vertex) AS component_id
    FROM reachability
    GROUP BY graph_id, current_vertex
)
SELECT
    graph_id,
    component_id,
    COUNT(*) AS component_size,
    ARRAY_AGG(vertex_id ORDER BY vertex_id) AS vertices
FROM representatives
GROUP BY graph_id, component_id;

-- Count components, including isolated vertices.
CREATE OR REPLACE FUNCTION count_connected_components(
    p_graph_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    selected_type VARCHAR(15);
    result_count BIGINT;
BEGIN
    SELECT graph_type
    INTO selected_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph %', p_graph_id;
    END IF;

    IF selected_type <> 'UNDIRECTED' THEN
        RAISE EXCEPTION
            'Connected components require an undirected graph.';
    END IF;

    SELECT COUNT(*)
    INTO result_count
    FROM graph_component_report
    WHERE graph_id = p_graph_id;

    RETURN result_count;
END;
$$;

-- Undirected cycle detection through a recursive traversal.
-- Each traversal maintains a path and checks for revisited vertices.
CREATE OR REPLACE FUNCTION has_undirected_cycle(
    p_graph_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    selected_type VARCHAR(15);
    result BOOLEAN;
BEGIN
    SELECT graph_type
    INTO selected_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph %', p_graph_id;
    END IF;

    IF selected_type <> 'UNDIRECTED' THEN
        RAISE EXCEPTION
            'Undirected cycle detection requires an undirected graph.';
    END IF;

    WITH RECURSIVE traversal (
        start_vertex,
        current_vertex,
        parent_vertex,
        visited,
        found_cycle
    ) AS (
        SELECT
            v.vertex_id,
            v.vertex_id,
            NULL::BIGINT,
            ARRAY[v.vertex_id]::BIGINT[],
            FALSE
        FROM graph_vertices v
        WHERE v.graph_id = p_graph_id

        UNION ALL

        SELECT
            t.start_vertex,
            a.destination,
            t.current_vertex,
            t.visited || a.destination,
            a.destination = ANY(t.visited)
                AND a.destination <> COALESCE(
                    t.parent_vertex,
                    -9223372036854775808::BIGINT
                )
        FROM traversal t
        JOIN graph_adjacency a
          ON a.graph_id = p_graph_id
         AND a.source = t.current_vertex
        WHERE NOT t.found_cycle
          AND (
              NOT a.destination = ANY(t.visited)
              OR (
                  a.destination = ANY(t.visited)
                  AND a.destination <> COALESCE(
                      t.parent_vertex,
                      -9223372036854775808::BIGINT
                  )
              )
          )
    )
    SELECT COALESCE(BOOL_OR(found_cycle), FALSE)
    INTO result
    FROM traversal;

    RETURN result;
END;
$$;

-- Directed cycle detection using recursive path traversal.
-- Revisiting a vertex on the current path establishes a cycle.
CREATE OR REPLACE FUNCTION has_directed_cycle(
    p_graph_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    selected_type VARCHAR(15);
    result BOOLEAN;
BEGIN
    SELECT graph_type
    INTO selected_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph %', p_graph_id;
    END IF;

    IF selected_type <> 'DIRECTED' THEN
        RAISE EXCEPTION
            'Directed cycle detection requires a directed graph.';
    END IF;

    WITH RECURSIVE traversal (
        start_vertex,
        current_vertex,
        visited,
        found_cycle
    ) AS (
        SELECT
            v.vertex_id,
            v.vertex_id,
            ARRAY[v.vertex_id]::BIGINT[],
            FALSE
        FROM graph_vertices v
        WHERE v.graph_id = p_graph_id

        UNION ALL

        SELECT
            t.start_vertex,
            a.destination,
            t.visited || a.destination,
            a.destination = ANY(t.visited)
        FROM traversal t
        JOIN graph_adjacency a
          ON a.graph_id = p_graph_id
         AND a.source = t.current_vertex
        WHERE NOT t.found_cycle
          AND (
              NOT a.destination = ANY(t.visited)
              OR a.destination = ANY(t.visited)
          )
    )
    SELECT COALESCE(BOOL_OR(found_cycle), FALSE)
    INTO result
    FROM traversal;

    RETURN result;
END;
$$;

-- Consolidated cycle report.
CREATE OR REPLACE VIEW graph_cycle_report AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    CASE
        WHEN g.graph_type = 'UNDIRECTED'
            THEN has_undirected_cycle(g.graph_id)
        ELSE has_directed_cycle(g.graph_id)
    END AS has_cycle
FROM graphs g;

-- Insert representative graph datasets.
DO $$
DECLARE
    undirected_id BIGINT;
    forest_id BIGINT;
    directed_id BIGINT;
    dag_id BIGINT;
    empty_id BIGINT;
BEGIN
    undirected_id := create_graph(
        'undirected_network',
        'UNDIRECTED',
        'Three connected groups and one cycle.'
    );

    forest_id := create_graph(
        'acyclic_undirected_network',
        'UNDIRECTED',
        'Undirected forest.'
    );

    directed_id := create_graph(
        'directed_dependency_network',
        'DIRECTED',
        'Directed dependency graph containing a cycle.'
    );

    dag_id := create_graph(
        'acyclic_dependency_network',
        'DIRECTED',
        'Directed acyclic dependency graph.'
    );

    empty_id := create_graph(
        'empty_network',
        'UNDIRECTED',
        'Empty graph.'
    );

    -- Undirected graph vertices.
    INSERT INTO graph_vertices (
        graph_id,
        vertex_id,
        vertex_label
    )
    VALUES
        (undirected_id, 1, 'A'),
        (undirected_id, 2, 'B'),
        (undirected_id, 3, 'C'),
        (undirected_id, 4, 'D'),
        (undirected_id, 5, 'E'),
        (undirected_id, 6, 'F'),
        (undirected_id, 7, 'G'),
        (undirected_id, 8, 'Isolated');

    PERFORM add_graph_edge(undirected_id, 1, 2);
    PERFORM add_graph_edge(undirected_id, 2, 3);
    PERFORM add_graph_edge(undirected_id, 3, 1);
    PERFORM add_graph_edge(undirected_id, 4, 5);
    PERFORM add_graph_edge(undirected_id, 6, 7);

    INSERT INTO graph_vertices (graph_id, vertex_id)
    VALUES
        (forest_id, 1),
        (forest_id, 2),
        (forest_id, 3),
        (forest_id, 4),
        (forest_id, 5);

    PERFORM add_graph_edge(forest_id, 1, 2);
    PERFORM add_graph_edge(forest_id, 2, 3);
    PERFORM add_graph_edge(forest_id, 4, 5);

    INSERT INTO graph_vertices (graph_id, vertex_id)
    VALUES
        (directed_id, 1),
        (directed_id, 2),
        (directed_id, 3),
        (directed_id, 4),
        (directed_id, 5),
        (directed_id, 6);

    PERFORM add_graph_edge(directed_id, 1, 2);
    PERFORM add_graph_edge(directed_id, 2, 3);
    PERFORM add_graph_edge(directed_id, 3, 4);
    PERFORM add_graph_edge(directed_id, 4, 2);
    PERFORM add_graph_edge(directed_id, 4, 5);

    INSERT INTO graph_vertices (graph_id, vertex_id)
    VALUES
        (dag_id, 1),
        (dag_id, 2),
        (dag_id, 3),
        (dag_id, 4),
        (dag_id, 5);

    PERFORM add_graph_edge(dag_id, 1, 2);
    PERFORM add_graph_edge(dag_id, 1, 3);
    PERFORM add_graph_edge(dag_id, 2, 4);
    PERFORM add_graph_edge(dag_id, 3, 4);
    PERFORM add_graph_edge(dag_id, 4, 5);
END;
$$;

-- Retrieval: all vertices and edges.
SELECT
    g.graph_name,
    g.graph_type,
    v.vertex_id,
    v.vertex_label
FROM graphs g
LEFT JOIN graph_vertices v USING (graph_id)
ORDER BY g.graph_name, v.vertex_id;

-- Component reporting.
SELECT
    g.graph_name,
    c.component_id,
    c.component_size,
    c.vertices
FROM graph_component_report c
JOIN graphs g USING (graph_id)
ORDER BY g.graph_name, c.component_id;

-- Component counts.
SELECT
    graph_name,
    count_connected_components(graph_id) AS component_count
FROM graphs
WHERE graph_type = 'UNDIRECTED'
ORDER BY graph_name;

-- Cycle evaluation.
SELECT
    graph_name,
    graph_type,
    has_cycle
FROM graph_cycle_report
ORDER BY graph_name;

-- Validate graph-type-specific cycle evaluation.
SELECT
    graph_name,
    CASE
        WHEN graph_type = 'UNDIRECTED'
            THEN has_undirected_cycle(graph_id)
        ELSE has_directed_cycle(graph_id)
    END AS cycle_detected
FROM graphs;

-- Aggregation: vertices and edges per graph.
SELECT
    g.graph_name,
    g.graph_type,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count
FROM graphs g
LEFT JOIN graph_vertices v USING (graph_id)
LEFT JOIN graph_edges e USING (graph_id)
GROUP BY g.graph_id, g.graph_name, g.graph_type
ORDER BY g.graph_name;

-- Demonstrate invalid edge insertion inside a savepoint.
-- The failure is caught without aborting the main transaction.
DO $$
DECLARE
    target_graph BIGINT;
BEGIN
    SELECT graph_id
    INTO target_graph
    FROM graphs
    WHERE graph_name = 'undirected_network';

    BEGIN
        PERFORM add_graph_edge(target_graph, 1, 999);
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'Invalid edge rejected because vertex 999 does not exist.';
    END;
END;
$$;

COMMIT;
