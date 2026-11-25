-- ============================================================
-- GRAPH ASSESSMENT DATABASE
-- PostgreSQL 14+
--
-- Models:
--   Graphs
--   Vertices
--   Edges
--   Algorithm assessments
--   Traversal results
--   Connected components
--   Cycle assessments
--   Bipartite assessments
--   Topological assessments
--
-- Algorithms are demonstrated through relational queries and
-- recursive CTEs. Procedural algorithms remain more suitable
-- for large graph workloads than repeated SQL recursion.
-- ============================================================

DROP SCHEMA IF EXISTS graph_lab CASCADE;

CREATE SCHEMA graph_lab;

SET search_path TO graph_lab, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE graph_type AS ENUM (
    'DIRECTED',
    'UNDIRECTED'
);

CREATE TYPE algorithm_type AS ENUM (
    'BFS',
    'DFS',
    'CONNECTED_COMPONENTS',
    'CYCLE_DETECTION',
    'BIPARTITE',
    'TOPOLOGICAL_SORT',
    'SHORTEST_PATH'
);

CREATE TYPE assessment_status AS ENUM (
    'PENDING',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);

-- ============================================================
-- 2. GRAPH TABLE
-- ============================================================

CREATE TABLE graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    graph_kind graph_type NOT NULL,

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_graph_name
        CHECK (
            length(trim(graph_name)) BETWEEN 1 AND 150
        )
);

-- ============================================================
-- 3. VERTEX TABLE
-- ============================================================

CREATE TABLE vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    vertex_label VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_vertex_label
        UNIQUE (graph_id, vertex_label),

    -- Enables composite foreign keys to enforce graph ownership.
    CONSTRAINT unique_vertex_graph_pair
        UNIQUE (graph_id, vertex_id),

    CONSTRAINT valid_vertex_label
        CHECK (length(trim(vertex_label)) > 0)
);

CREATE INDEX idx_vertices_graph
    ON vertices(graph_id, vertex_id);

-- ============================================================
-- 4. EDGE TABLE
-- ============================================================

CREATE TABLE edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex_id BIGINT NOT NULL,

    target_vertex_id BIGINT NOT NULL,

    weight NUMERIC(12, 4) NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT source_vertex_belongs_to_graph
        FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT target_vertex_belongs_to_graph
        FOREIGN KEY (graph_id, target_vertex_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT valid_edge_weight
        CHECK (weight >= 0),

    CONSTRAINT unique_directed_edge
        UNIQUE (
            graph_id,
            source_vertex_id,
            target_vertex_id
        )
);

CREATE INDEX idx_edges_source
    ON edges(graph_id, source_vertex_id);

CREATE INDEX idx_edges_target
    ON edges(graph_id, target_vertex_id);

CREATE INDEX idx_edges_graph_source_target
    ON edges(
        graph_id,
        source_vertex_id,
        target_vertex_id
    );

-- ============================================================
-- 5. EDGE INSERTION FUNCTION
-- ============================================================

-- Undirected edges are stored in canonical vertex-ID order.
-- This prevents storing both A-B and B-A as separate edges.
-- Directed edges preserve their original orientation.

CREATE OR REPLACE FUNCTION add_graph_edge(
    p_graph_id BIGINT,
    p_source BIGINT,
    p_target BIGINT,
    p_weight NUMERIC DEFAULT 1
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_type graph_type;
    v_edge_id BIGINT;
    v_source BIGINT := p_source;
    v_target BIGINT := p_target;
BEGIN
    IF p_weight IS NULL OR p_weight < 0 THEN
        RAISE EXCEPTION 'Edge weight must be non-negative.';
    END IF;

    SELECT graph_kind
    INTO v_type
    FROM graphs
    WHERE graph_id = p_graph_id
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist.', p_graph_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_source
    ) THEN
        RAISE EXCEPTION 'Source vertex does not belong to graph.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_target
    ) THEN
        RAISE EXCEPTION 'Target vertex does not belong to graph.';
    END IF;

    IF v_type = 'UNDIRECTED'
       AND v_source > v_target THEN

        v_source := p_target;
        v_target := p_source;
    END IF;

    INSERT INTO edges (
        graph_id,
        source_vertex_id,
        target_vertex_id,
        weight
    )
    VALUES (
        p_graph_id,
        v_source,
        v_target,
        p_weight
    )
    ON CONFLICT (
        graph_id,
        source_vertex_id,
        target_vertex_id
    )
    DO UPDATE SET weight = EXCLUDED.weight
    RETURNING edge_id INTO v_edge_id;

    RETURN v_edge_id;
END;
$$;

-- ============================================================
-- 6. ASSESSMENT RUNS
-- ============================================================

CREATE TABLE assessment_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    algorithm algorithm_type NOT NULL,

    status assessment_status NOT NULL DEFAULT 'PENDING',

    start_vertex_id BIGINT,

    target_vertex_id BIGINT,

    result_data JSONB NOT NULL DEFAULT '{}'::JSONB,

    error_message TEXT,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, start_vertex_id)
        REFERENCES vertices(graph_id, vertex_id),

    FOREIGN KEY (graph_id, target_vertex_id)
        REFERENCES vertices(graph_id, vertex_id),

    CONSTRAINT valid_run_dates
        CHECK (
            completed_at IS NULL
            OR started_at IS NULL
            OR completed_at >= started_at
        ),

    CONSTRAINT valid_completed_run
        CHECK (
            status <> 'COMPLETED'
            OR completed_at IS NOT NULL
        ),

    CONSTRAINT valid_failed_run
        CHECK (
            status <> 'FAILED'
            OR error_message IS NOT NULL
        )
);

CREATE INDEX idx_assessment_graph_time
    ON assessment_runs(graph_id, created_at DESC);

CREATE INDEX idx_assessment_status
    ON assessment_runs(status, created_at);

-- ============================================================
-- 7. TRAVERSAL RESULT TABLE
-- ============================================================

CREATE TABLE traversal_results (
    run_id BIGINT NOT NULL
        REFERENCES assessment_runs(run_id)
        ON DELETE CASCADE,

    vertex_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id)
        ON DELETE CASCADE,

    traversal_position INTEGER NOT NULL,

    parent_vertex_id BIGINT
        REFERENCES vertices(vertex_id),

    distance INTEGER NOT NULL,

    PRIMARY KEY (run_id, vertex_id),

    UNIQUE (run_id, traversal_position),

    CONSTRAINT valid_traversal_position
        CHECK (traversal_position > 0),

    CONSTRAINT valid_distance
        CHECK (distance >= 0)
);

CREATE INDEX idx_traversal_position
    ON traversal_results(run_id, traversal_position);

-- ============================================================
-- 8. COMPONENT RESULT TABLE
-- ============================================================

CREATE TABLE component_results (
    run_id BIGINT NOT NULL
        REFERENCES assessment_runs(run_id)
        ON DELETE CASCADE,

    vertex_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id)
        ON DELETE CASCADE,

    component_number INTEGER NOT NULL,

    PRIMARY KEY (run_id, vertex_id),

    CONSTRAINT valid_component_number
        CHECK (component_number > 0)
);

CREATE INDEX idx_component_number
    ON component_results(run_id, component_number);

-- ============================================================
-- 9. GRAPH VIEWS
-- ============================================================

CREATE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_kind,

    COUNT(DISTINCT v.vertex_id) AS vertex_count,

    COUNT(DISTINCT e.edge_id) AS edge_count,

    CASE
        WHEN COUNT(DISTINCT v.vertex_id) = 0 THEN 0
        WHEN g.graph_kind = 'UNDIRECTED'
            THEN COUNT(DISTINCT e.edge_id)
        ELSE COUNT(DISTINCT e.edge_id)
    END AS stored_edge_count

FROM graphs g

LEFT JOIN vertices v
    ON v.graph_id = g.graph_id

LEFT JOIN edges e
    ON e.graph_id = g.graph_id

GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_kind;


CREATE VIEW graph_adjacency AS
SELECT
    e.graph_id,
    e.source_vertex_id,
    e.target_vertex_id,
    e.weight

FROM edges e

UNION ALL

SELECT
    g.graph_id,
    e.target_vertex_id,
    e.source_vertex_id,
    e.weight

FROM edges e

JOIN graphs g
    ON g.graph_id = e.graph_id

WHERE g.graph_kind = 'UNDIRECTED'
  AND e.source_vertex_id <> e.target_vertex_id;


-- ============================================================
-- 10. REACHABILITY USING RECURSIVE CTE
-- ============================================================

CREATE OR REPLACE FUNCTION reachable_vertices(
    p_graph_id BIGINT,
    p_start BIGINT
)
RETURNS TABLE (
    vertex_id BIGINT,
    minimum_distance INTEGER
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE reach(vertex_id, distance, path) AS (

        SELECT
            p_start,
            0,
            ARRAY[p_start]::BIGINT[]

        UNION ALL

        SELECT
            a.target_vertex_id,
            r.distance + 1,
            r.path || a.target_vertex_id

        FROM reach r

        JOIN graph_adjacency a
            ON a.graph_id = p_graph_id
           AND a.source_vertex_id = r.vertex_id

        WHERE NOT a.target_vertex_id = ANY(r.path)
    )

    SELECT
        r.vertex_id,
        MIN(r.distance)::INTEGER

    FROM reach r

    GROUP BY r.vertex_id;
$$;

-- The path array prevents revisiting a vertex within a single
-- recursive path. GROUP BY selects the minimum hop count.
-- This query can enumerate many simple paths on dense graphs.


-- ============================================================
-- 11. BFS ASSESSMENT PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE execute_bfs(
    p_graph_id BIGINT,
    p_start BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_run_id BIGINT;
    v_type graph_type;
BEGIN
    SELECT graph_kind
    INTO v_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_start
    ) THEN
        RAISE EXCEPTION 'Starting vertex does not exist.';
    END IF;

    INSERT INTO assessment_runs (
        graph_id,
        algorithm,
        status,
        start_vertex_id,
        started_at
    )
    VALUES (
        p_graph_id,
        'BFS',
        'RUNNING',
        p_start,
        clock_timestamp()
    )
    RETURNING run_id INTO v_run_id;

    BEGIN
        INSERT INTO traversal_results (
            run_id,
            vertex_id,
            traversal_position,
            parent_vertex_id,
            distance
        )
        SELECT
            v_run_id,
            r.vertex_id,
            ROW_NUMBER() OVER (
                ORDER BY r.minimum_distance, r.vertex_id
            )::INTEGER,
            NULL,
            r.minimum_distance

        FROM reachable_vertices(p_graph_id, p_start) r;

        UPDATE assessment_runs
        SET
            status = 'COMPLETED',
            completed_at = clock_timestamp(),
            result_data = jsonb_build_object(
                'reachable_vertices',
                (
                    SELECT COUNT(*)
                    FROM traversal_results
                    WHERE run_id = v_run_id
                )
            )
        WHERE run_id = v_run_id;

    EXCEPTION WHEN OTHERS THEN
        UPDATE assessment_runs
        SET
            status = 'FAILED',
            completed_at = clock_timestamp(),
            error_message = SQLERRM
        WHERE run_id = v_run_id;

        RAISE;
    END;
END;
$$;

-- Note: The recursive CTE calculates shortest distances.
-- Its ordering by distance and vertex ID is deterministic,
-- but it is not a strict simulation of FIFO BFS discovery order.
-- Parent pointers are not reconstructed by this procedure.


-- ============================================================
-- 12. SAMPLE GRAPH DATA
-- ============================================================

INSERT INTO graphs (
    graph_name,
    graph_kind,
    description
)
VALUES
(
    'social_network',
    'UNDIRECTED',
    'Undirected user relationship graph.'
),
(
    'course_dependencies',
    'DIRECTED',
    'Course prerequisite dependency graph.'
),
(
    'bipartite_matching',
    'UNDIRECTED',
    'Employee-to-project relationship graph.'
),
(
    'cyclic_dependencies',
    'DIRECTED',
    'Directed graph containing a dependency cycle.'
),
(
    'isolated_network',
    'UNDIRECTED',
    'Graph containing isolated vertices.'
);

-- ============================================================
-- 13. SOCIAL NETWORK VERTICES
-- ============================================================

INSERT INTO vertices (graph_id, vertex_label)
SELECT
    g.graph_id,
    v.label
FROM graphs g
CROSS JOIN (
    VALUES
        ('Alice'),
        ('Bob'),
        ('Charlie'),
        ('David'),
        ('Eva'),
        ('Frank'),
        ('George'),
        ('Helen')
) AS v(label)
WHERE g.graph_name = 'social_network';

-- ============================================================
-- 14. SOCIAL NETWORK EDGES
-- ============================================================

DO $$
DECLARE
    v_graph BIGINT;
    v_a BIGINT;
    v_b BIGINT;
    pair RECORD;
BEGIN
    SELECT graph_id
    INTO v_graph
    FROM graphs
    WHERE graph_name = 'social_network';

    FOR pair IN
        SELECT *
        FROM (
            VALUES
                ('Alice', 'Bob'),
                ('Alice', 'Charlie'),
                ('Bob', 'David'),
                ('Charlie', 'David'),
                ('Eva', 'Frank'),
                ('George', 'Helen')
        ) AS relationships(person_a, person_b)
    LOOP
        SELECT vertex_id INTO v_a
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.person_a;

        SELECT vertex_id INTO v_b
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.person_b;

        PERFORM add_graph_edge(v_graph, v_a, v_b, 1);
    END LOOP;
END;
$$;

-- ============================================================
-- 15. COURSE DEPENDENCY GRAPH
-- ============================================================

INSERT INTO vertices (graph_id, vertex_label)
SELECT
    g.graph_id,
    v.label
FROM graphs g
CROSS JOIN (
    VALUES
        ('Programming'),
        ('Data Structures'),
        ('Algorithms'),
        ('Databases'),
        ('Graph Theory'),
        ('Advanced Algorithms')
) AS v(label)
WHERE g.graph_name = 'course_dependencies';


DO $$
DECLARE
    v_graph BIGINT;
    pair RECORD;
    v_a BIGINT;
    v_b BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph
    FROM graphs
    WHERE graph_name = 'course_dependencies';

    FOR pair IN
        SELECT *
        FROM (
            VALUES
                ('Programming', 'Data Structures'),
                ('Data Structures', 'Algorithms'),
                ('Programming', 'Databases'),
                ('Algorithms', 'Graph Theory'),
                ('Databases', 'Graph Theory'),
                ('Graph Theory', 'Advanced Algorithms')
        ) AS dependencies(prerequisite, dependent)
    LOOP
        SELECT vertex_id INTO v_a
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.prerequisite;

        SELECT vertex_id INTO v_b
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.dependent;

        PERFORM add_graph_edge(v_graph, v_a, v_b, 1);
    END LOOP;
END;
$$;

-- ============================================================
-- 16. BIPARTITE GRAPH DATA
-- ============================================================

INSERT INTO vertices (graph_id, vertex_label)
SELECT
    g.graph_id,
    v.label
FROM graphs g
CROSS JOIN (
    VALUES
        ('Employee_A'),
        ('Employee_B'),
        ('Project_X'),
        ('Project_Y'),
        ('Project_Z')
) AS v(label)
WHERE g.graph_name = 'bipartite_matching';


DO $$
DECLARE
    v_graph BIGINT;
    pair RECORD;
    v_a BIGINT;
    v_b BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph
    FROM graphs
    WHERE graph_name = 'bipartite_matching';

    FOR pair IN
        SELECT *
        FROM (
            VALUES
                ('Employee_A', 'Project_X'),
                ('Employee_A', 'Project_Y'),
                ('Employee_B', 'Project_Y'),
                ('Employee_B', 'Project_Z')
        ) AS assignments(employee_name, project_name)
    LOOP
        SELECT vertex_id INTO v_a
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.employee_name;

        SELECT vertex_id INTO v_b
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.project_name;

        PERFORM add_graph_edge(v_graph, v_a, v_b, 1);
    END LOOP;
END;
$$;

-- ============================================================
-- 17. DIRECTED CYCLE DATA
-- ============================================================

INSERT INTO vertices (graph_id, vertex_label)
SELECT
    g.graph_id,
    v.label
FROM graphs g
CROSS JOIN (
    VALUES
        ('Service_A'),
        ('Service_B'),
        ('Service_C')
) AS v(label)
WHERE g.graph_name = 'cyclic_dependencies';


DO $$
DECLARE
    v_graph BIGINT;
    v_a BIGINT;
    v_b BIGINT;
    pair RECORD;
BEGIN
    SELECT graph_id
    INTO v_graph
    FROM graphs
    WHERE graph_name = 'cyclic_dependencies';

    FOR pair IN
        SELECT *
        FROM (
            VALUES
                ('Service_A', 'Service_B'),
                ('Service_B', 'Service_C'),
                ('Service_C', 'Service_A')
        ) AS dependencies(source_name, target_name)
    LOOP
        SELECT vertex_id INTO v_a
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.source_name;

        SELECT vertex_id INTO v_b
        FROM vertices
        WHERE graph_id = v_graph
          AND vertex_label = pair.target_name;

        PERFORM add_graph_edge(v_graph, v_a, v_b, 1);
    END LOOP;
END;
$$;

-- ============================================================
-- 18. ISOLATED VERTEX DATA
-- ============================================================

INSERT INTO vertices (graph_id, vertex_label)
SELECT
    g.graph_id,
    v.label
FROM graphs g
CROSS JOIN (
    VALUES
        ('Node_100'),
        ('Node_200'),
        ('Node_300')
) AS v(label)
WHERE g.graph_name = 'isolated_network';

-- ============================================================
-- 19. GRAPH RETRIEVAL
-- ============================================================

SELECT *
FROM graph_statistics
ORDER BY graph_id;

SELECT
    g.graph_name,
    v.vertex_label
FROM graphs g
JOIN vertices v
    ON v.graph_id = g.graph_id
ORDER BY g.graph_name, v.vertex_label;

-- ============================================================
-- 20. ADJACENCY LIST RETRIEVAL
-- ============================================================

SELECT
    g.graph_name,
    source.vertex_label AS source,
    target.vertex_label AS target,
    a.weight

FROM graph_adjacency a

JOIN graphs g
    ON g.graph_id = a.graph_id

JOIN vertices source
    ON source.vertex_id = a.source_vertex_id

JOIN vertices target
    ON target.vertex_id = a.target_vertex_id

ORDER BY
    g.graph_name,
    source.vertex_label,
    target.vertex_label;

-- ============================================================
-- 21. BFS REACHABILITY
-- ============================================================

SELECT
    g.graph_name,
    v.vertex_label,
    r.minimum_distance

FROM graphs g

JOIN vertices start_vertex
    ON start_vertex.graph_id = g.graph_id

CROSS JOIN LATERAL reachable_vertices(
    g.graph_id,
    start_vertex.vertex_id
) r

JOIN vertices v
    ON v.vertex_id = r.vertex_id

WHERE g.graph_name = 'social_network'
  AND start_vertex.vertex_label = 'Alice'

ORDER BY
    r.minimum_distance,
    v.vertex_label;

-- ============================================================
-- 22. CONNECTED COMPONENTS
-- ============================================================

-- A recursive reachability calculation is performed from every
-- vertex. Vertices belong to the same component if they can
-- reach each other in the undirected graph.

WITH RECURSIVE reach(start_vertex, current_vertex, path) AS (

    SELECT
        v.vertex_id,
        v.vertex_id,
        ARRAY[v.vertex_id]::BIGINT[]

    FROM vertices v

    JOIN graphs g
        ON g.graph_id = v.graph_id

    WHERE g.graph_name = 'social_network'

    UNION ALL

    SELECT
        r.start_vertex,
        a.target_vertex_id,
        r.path || a.target_vertex_id

    FROM reach r

    JOIN graph_adjacency a
        ON a.source_vertex_id = r.current_vertex

    JOIN graphs g
        ON g.graph_id = a.graph_id

    WHERE g.graph_name = 'social_network'
      AND NOT a.target_vertex_id = ANY(r.path)
),

component_labels AS (
    SELECT
        start_vertex,
        MIN(current_vertex) AS component_id

    FROM reach

    GROUP BY start_vertex
)

SELECT
    cl.component_id,
    v.vertex_label

FROM component_labels cl

JOIN vertices v
    ON v.vertex_id = cl.start_vertex

ORDER BY
    cl.component_id,
    v.vertex_label;

-- ============================================================
-- 23. UNDIRECTED CYCLE INDICATOR
-- ============================================================

-- A connected undirected component is acyclic if E = V - 1.
-- For a graph with C components, the entire graph is a forest
-- if E = V - C.
--
-- A self-loop contributes one stored edge and is correctly
-- classified as a cycle.

WITH component_count AS (

    WITH RECURSIVE reach(start_vertex, current_vertex, path) AS (

        SELECT
            v.vertex_id,
            v.vertex_id,
            ARRAY[v.vertex_id]::BIGINT[]

        FROM vertices v

        JOIN graphs g
            ON g.graph_id = v.graph_id

        WHERE g.graph_name = 'social_network'

        UNION ALL

        SELECT
            r.start_vertex,
            a.target_vertex_id,
            r.path || a.target_vertex_id

        FROM reach r

        JOIN graph_adjacency a
            ON a.source_vertex_id = r.current_vertex

        WHERE a.graph_id = (
            SELECT graph_id
            FROM graphs
            WHERE graph_name = 'social_network'
        )

        AND NOT a.target_vertex_id = ANY(r.path)
    )

    SELECT COUNT(
        DISTINCT (
            SELECT MIN(r2.current_vertex)
            FROM reach r2
            WHERE r2.start_vertex = r.start_vertex
        )
    ) AS components

    FROM reach r
),

statistics AS (
    SELECT
        g.graph_id,
        COUNT(DISTINCT v.vertex_id) AS vertex_count,
        COUNT(DISTINCT e.edge_id) AS edge_count

    FROM graphs g

    LEFT JOIN vertices v
        ON v.graph_id = g.graph_id

    LEFT JOIN edges e
        ON e.graph_id = g.graph_id

    WHERE g.graph_name = 'social_network'

    GROUP BY g.graph_id
)

SELECT
    s.vertex_count,
    s.edge_count,
    c.components,

    (
        s.edge_count >
        s.vertex_count - c.components
    ) AS contains_cycle

FROM statistics s
CROSS JOIN component_count c;

-- ============================================================
-- 24. BIPARTITE VALIDATION
-- ============================================================

-- A graph is bipartite if and only if it has no odd-length cycle.
-- This recursive query enumerates simple paths and identifies
-- odd cycles. It is suitable for small assessment datasets,
-- not unrestricted large production graphs.

WITH RECURSIVE paths(
    graph_id,
    start_vertex,
    current_vertex,
    path,
    depth
) AS (

    SELECT
        g.graph_id,
        v.vertex_id,
        v.vertex_id,
        ARRAY[v.vertex_id]::BIGINT[],
        0

    FROM graphs g

    JOIN vertices v
        ON v.graph_id = g.graph_id

    WHERE g.graph_name = 'bipartite_matching'

    UNION ALL

    SELECT
        p.graph_id,
        p.start_vertex,
        a.target_vertex_id,
        p.path || a.target_vertex_id,
        p.depth + 1

    FROM paths p

    JOIN graph_adjacency a
        ON a.graph_id = p.graph_id
       AND a.source_vertex_id = p.current_vertex

    WHERE (
        NOT a.target_vertex_id = ANY(p.path)
        OR (
            a.target_vertex_id = p.start_vertex
            AND p.depth >= 2
        )
    )

    AND p.depth < 100
),

odd_cycles AS (
    SELECT DISTINCT graph_id

    FROM paths

    WHERE current_vertex = start_vertex
      AND depth >= 3
      AND depth % 2 = 1
)

SELECT
    g.graph_name,

    NOT EXISTS (
        SELECT 1
        FROM odd_cycles o
        WHERE o.graph_id = g.graph_id
    ) AS is_bipartite

FROM graphs g

WHERE g.graph_name IN (
    'bipartite_matching',
    'social_network'
);

-- ============================================================
-- 25. TOPOLOGICAL SORT USING KAHN'S ALGORITHM
-- ============================================================

-- Each iteration selects currently available zero-indegree
-- vertices. The query demonstrates dependency processing.
-- It is intended for the supplied small dependency graph.

CREATE TEMP TABLE IF NOT EXISTS topo_work (
    graph_id BIGINT NOT NULL,
    vertex_id BIGINT NOT NULL,
    indegree INTEGER NOT NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processing_order INTEGER,
    PRIMARY KEY (graph_id, vertex_id)
) ON COMMIT PRESERVE ROWS;


CREATE OR REPLACE PROCEDURE execute_topological_sort(
    p_graph_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type graph_type;
    v_vertex BIGINT;
    v_position INTEGER := 0;
    v_remaining INTEGER;
BEGIN
    SELECT graph_kind
    INTO v_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist.';
    END IF;

    IF v_type <> 'DIRECTED' THEN
        RAISE EXCEPTION
            'Topological sorting requires a directed graph.';
    END IF;

    DELETE FROM topo_work
    WHERE graph_id = p_graph_id;

    INSERT INTO topo_work (
        graph_id,
        vertex_id,
        indegree
    )
    SELECT
        v.graph_id,
        v.vertex_id,
        COUNT(a.source_vertex_id)::INTEGER

    FROM vertices v

    LEFT JOIN graph_adjacency a
        ON a.graph_id = v.graph_id
       AND a.target_vertex_id = v.vertex_id

    WHERE v.graph_id = p_graph_id

    GROUP BY v.graph_id, v.vertex_id;

    LOOP
        SELECT vertex_id
        INTO v_vertex
        FROM topo_work
        WHERE graph_id = p_graph_id
          AND indegree = 0
          AND NOT processed
        ORDER BY vertex_id
        LIMIT 1;

        EXIT WHEN NOT FOUND;

        v_position := v_position + 1;

        UPDATE topo_work
        SET
            processed = TRUE,
            processing_order = v_position
        WHERE graph_id = p_graph_id
          AND vertex_id = v_vertex;

        -- Decrease the indegree of unprocessed outgoing neighbors.
        UPDATE topo_work tw
        SET indegree = tw.indegree - 1

        FROM graph_adjacency a

        WHERE a.graph_id = p_graph_id
          AND a.source_vertex_id = v_vertex
          AND tw.graph_id = p_graph_id
          AND tw.vertex_id = a.target_vertex_id
          AND NOT tw.processed;
    END LOOP;

    SELECT COUNT(*)
    INTO v_remaining
    FROM topo_work
    WHERE graph_id = p_graph_id
      AND NOT processed;

    IF v_remaining > 0 THEN
        RAISE NOTICE
            'Directed cycle detected. % vertices remain.',
            v_remaining;
    ELSE
        RAISE NOTICE 'Topological ordering completed.';
    END IF;
END;
$$;


CALL execute_topological_sort(
    (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'course_dependencies'
    )
);

SELECT
    v.vertex_label,
    tw.processing_order,
    tw.processed

FROM topo_work tw

JOIN vertices v
    ON v.vertex_id = tw.vertex_id

WHERE tw.graph_id = (
    SELECT graph_id
    FROM graphs
    WHERE graph_name = 'course_dependencies'
)

ORDER BY tw.processing_order NULLS LAST, v.vertex_label;

-- ============================================================
-- 26. DIRECTED CYCLE VALIDATION
-- ============================================================

-- Kahn's algorithm detects a directed cycle if some vertices
-- remain after all zero-indegree vertices are processed.

CALL execute_topological_sort(
    (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'cyclic_dependencies'
    )
);

SELECT
    g.graph_name,

    COUNT(*) FILTER (
        WHERE tw.processed
    ) AS processed_vertices,

    COUNT(*) FILTER (
        WHERE NOT tw.processed
    ) AS unprocessed_vertices,

    BOOL_OR(NOT tw.processed) AS cycle_detected

FROM topo_work tw

JOIN graphs g
    ON g.graph_id = tw.graph_id

WHERE g.graph_name = 'cyclic_dependencies'

GROUP BY g.graph_name;

-- ============================================================
-- 27. EXECUTE BFS ASSESSMENT
-- ============================================================

CALL execute_bfs(
    (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'social_network'
    ),
    (
        SELECT v.vertex_id
        FROM vertices v
        JOIN graphs g
            ON g.graph_id = v.graph_id
        WHERE g.graph_name = 'social_network'
          AND v.vertex_label = 'Alice'
    )
);

SELECT
    ar.run_id,
    ar.algorithm,
    ar.status,
    ar.result_data,
    ar.started_at,
    ar.completed_at

FROM assessment_runs ar

ORDER BY ar.run_id DESC;

-- ============================================================
-- 28. ASSESSMENT RESULT RETRIEVAL
-- ============================================================

SELECT
    ar.run_id,
    g.graph_name,
    ar.algorithm,
    v.vertex_label,
    tr.traversal_position,
    tr.distance

FROM traversal_results tr

JOIN assessment_runs ar
    ON ar.run_id = tr.run_id

JOIN graphs g
    ON g.graph_id = ar.graph_id

JOIN vertices v
    ON v.vertex_id = tr.vertex_id

ORDER BY
    ar.run_id,
    tr.traversal_position;

-- ============================================================
-- 29. GRAPH PERFORMANCE REPORT
-- ============================================================

SELECT
    g.graph_name,
    g.graph_kind,
    COUNT(DISTINCT v.vertex_id) AS vertices,
    COUNT(DISTINCT e.edge_id) AS edges,

    ROUND(
        COUNT(DISTINCT e.edge_id)::NUMERIC
        /
        NULLIF(COUNT(DISTINCT v.vertex_id), 0),
        3
    ) AS edges_per_vertex

FROM graphs g

LEFT JOIN vertices v
    ON v.graph_id = g.graph_id

LEFT JOIN edges e
    ON e.graph_id = g.graph_id

GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_kind

ORDER BY g.graph_name;

-- ============================================================
-- 30. TRANSACTION AND FAILURE HANDLING
-- ============================================================

-- Demonstrate transactional insertion and rollback.
-- The savepoint prevents an invalid operation from leaving
-- a partial graph update.

BEGIN;

SAVEPOINT before_invalid_edge;

DO $$
DECLARE
    v_graph BIGINT;
    v_vertex BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph
    FROM graphs
    WHERE graph_name = 'social_network';

    SELECT vertex_id
    INTO v_vertex
    FROM vertices
    WHERE graph_id = v_graph
      AND vertex_label = 'Alice';

    -- A duplicate edge is handled idempotently.
    PERFORM add_graph_edge(
        v_graph,
        v_vertex,
        v_vertex,
        1
    );
END;
$$;

COMMIT;

-- ============================================================
-- 31. VALIDATION QUERIES
-- ============================================================

-- Check for invalid cross-graph relationships.
SELECT
    e.edge_id

FROM edges e

LEFT JOIN vertices s
    ON s.vertex_id = e.source_vertex_id
   AND s.graph_id = e.graph_id

LEFT JOIN vertices t
    ON t.vertex_id = e.target_vertex_id
   AND t.graph_id = e.graph_id

WHERE s.vertex_id IS NULL
   OR t.vertex_id IS NULL;

-- Check graph records without vertices.
SELECT
    g.graph_name

FROM graphs g

LEFT JOIN vertices v
    ON v.graph_id = g.graph_id

GROUP BY g.graph_id, g.graph_name

HAVING COUNT(v.vertex_id) = 0;

-- Check completed assessments with no traversal output.
SELECT
    ar.run_id,
    ar.algorithm

FROM assessment_runs ar

WHERE ar.status = 'COMPLETED'
  AND ar.algorithm = 'BFS'

  AND NOT EXISTS (
      SELECT 1
      FROM traversal_results tr
      WHERE tr.run_id = ar.run_id
  );

-- ============================================================
-- 32. QUERY PLANNING
-- ============================================================

EXPLAIN ANALYZE
SELECT
    source_vertex_id,
    target_vertex_id

FROM edges

WHERE graph_id = (
    SELECT graph_id
    FROM graphs
    WHERE graph_name = 'social_network'
)
AND source_vertex_id > 0;

-- ============================================================
-- END OF GRAPH ASSESSMENT DATABASE
-- ============================================================
