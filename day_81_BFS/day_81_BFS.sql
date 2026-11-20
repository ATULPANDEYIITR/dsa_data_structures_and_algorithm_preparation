-- ============================================================
-- BREADTH-FIRST SEARCH: POSTGRESQL GRAPH ENGINE
-- ============================================================
--
-- Features:
--   1. Graph and vertex management
--   2. Directed and undirected edges
--   3. BFS shortest distances
--   4. Parent tracking and shortest-path reconstruction
--   5. Multi-source BFS
--   6. Level processing
--   7. Connected-component reporting
--   8. Grid-independent relational graph traversal
--   9. Integrity constraints and indexes
--  10. Transactional graph updates
--
-- Requires PostgreSQL 15 or later.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ------------------------------------------------------------
-- GRAPH DOMAIN
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    graph_type VARCHAR(15) NOT NULL
        CHECK (graph_type IN ('DIRECTED', 'UNDIRECTED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id) ON DELETE CASCADE,
    vertex_label VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (graph_id, vertex_id),
    UNIQUE (graph_id, vertex_label)
);

CREATE TABLE IF NOT EXISTS edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex BIGINT NOT NULL,
    destination_vertex BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (source_vertex <> destination_vertex),

    UNIQUE (graph_id, source_vertex, destination_vertex)
);

CREATE INDEX IF NOT EXISTS idx_vertices_graph
    ON vertices(graph_id);

CREATE INDEX IF NOT EXISTS idx_edges_source
    ON edges(graph_id, source_vertex);

CREATE INDEX IF NOT EXISTS idx_edges_destination
    ON edges(graph_id, destination_vertex);

-- ------------------------------------------------------------
-- BFS EXECUTION HISTORY
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bfs_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id) ON DELETE CASCADE,
    run_type VARCHAR(20) NOT NULL
        CHECK (run_type IN ('SINGLE_SOURCE', 'MULTI_SOURCE')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    execution_status VARCHAR(20) NOT NULL DEFAULT 'RUNNING'
        CHECK (
            execution_status IN ('RUNNING', 'COMPLETED', 'FAILED')
        ),

    CHECK (
        completed_at IS NULL OR completed_at >= started_at
    )
);

CREATE TABLE IF NOT EXISTS bfs_sources (
    run_id BIGINT NOT NULL
        REFERENCES bfs_runs(run_id) ON DELETE CASCADE,
    vertex_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id) ON DELETE CASCADE,

    PRIMARY KEY (run_id, vertex_id)
);

CREATE TABLE IF NOT EXISTS bfs_results (
    run_id BIGINT NOT NULL
        REFERENCES bfs_runs(run_id) ON DELETE CASCADE,
    vertex_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id) ON DELETE CASCADE,
    distance INTEGER NOT NULL CHECK (distance >= 0),
    parent_vertex BIGINT
        REFERENCES vertices(vertex_id) ON DELETE SET NULL,

    PRIMARY KEY (run_id, vertex_id),

    CHECK (
        parent_vertex IS NULL OR parent_vertex <> vertex_id
    )
);

CREATE INDEX IF NOT EXISTS idx_bfs_results_distance
    ON bfs_results(run_id, distance);

CREATE INDEX IF NOT EXISTS idx_bfs_results_parent
    ON bfs_results(run_id, parent_vertex);

-- ------------------------------------------------------------
-- VALIDATE EDGE DIRECTION AND GRAPH OWNERSHIP
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(15);
BEGIN
    SELECT graph_type
    INTO v_type
    FROM graphs
    WHERE graph_id = NEW.graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', NEW.graph_id;
    END IF;

    IF NEW.source_vertex = NEW.destination_vertex THEN
        RAISE EXCEPTION 'Self-loops are not supported';
    END IF;

    IF v_type = 'UNDIRECTED' THEN
        IF EXISTS (
            SELECT 1
            FROM edges
            WHERE graph_id = NEW.graph_id
              AND source_vertex = NEW.destination_vertex
              AND destination_vertex = NEW.source_vertex
        ) THEN
            RAISE EXCEPTION
                'Undirected edge already exists in reverse direction';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_graph_edge ON edges;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT ON edges
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- ------------------------------------------------------------
-- BFS FUNCTION
-- ------------------------------------------------------------
--
-- The function uses a queue represented by an indexed array.
-- Each vertex is visited at most once.
--
-- Undirected edges are expanded in both directions.
-- Directed edges are expanded only from source to destination.
--
-- Multi-source BFS initializes every source at distance zero.
-- The first discovered path is shortest because BFS processes
-- vertices in nondecreasing distance order.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION run_bfs(
    p_graph_id BIGINT,
    p_sources BIGINT[]
)
RETURNS TABLE (
    vertex_id BIGINT,
    distance INTEGER,
    parent_vertex BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(15);
    v_source BIGINT;
    v_current BIGINT;
    v_neighbor BIGINT;
    v_distance INTEGER;

    v_queue BIGINT[];
    v_head INTEGER := 1;
    v_tail INTEGER := 0;

    v_run_id BIGINT;
    v_run_type VARCHAR(20);
BEGIN
    IF p_sources IS NULL OR cardinality(p_sources) = 0 THEN
        RAISE EXCEPTION 'At least one source is required';
    END IF;

    SELECT graph_type
    INTO v_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', p_graph_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM unnest(p_sources) AS s(vertex_id)
        WHERE s.vertex_id IS NULL
    ) THEN
        RAISE EXCEPTION 'Source identifiers cannot be NULL';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM unnest(p_sources) AS s(vertex_id)
        LEFT JOIN vertices v
          ON v.graph_id = p_graph_id
         AND v.vertex_id = s.vertex_id
        WHERE v.vertex_id IS NULL
    ) THEN
        RAISE EXCEPTION 'One or more sources do not belong to graph';
    END IF;

    v_run_type := CASE
        WHEN cardinality(ARRAY(
            SELECT DISTINCT x
            FROM unnest(p_sources) AS x
        )) > 1
        THEN 'MULTI_SOURCE'
        ELSE 'SINGLE_SOURCE'
    END;

    INSERT INTO bfs_runs (
        graph_id,
        run_type
    )
    VALUES (
        p_graph_id,
        v_run_type
    )
    RETURNING run_id INTO v_run_id;

    -- Temporary state is isolated to this database session.
    CREATE TEMP TABLE IF NOT EXISTS bfs_work (
        vertex_id BIGINT PRIMARY KEY,
        distance INTEGER NOT NULL,
        parent_vertex BIGINT
    ) ON COMMIT DROP;

    TRUNCATE TABLE pg_temp.bfs_work;

    INSERT INTO bfs_sources(run_id, vertex_id)
    SELECT v_run_id, source_id
    FROM (
        SELECT DISTINCT unnest(p_sources) AS source_id
    ) sources;

    -- Initialize all unique sources.
    FOR v_source IN
        SELECT DISTINCT unnest(p_sources)
    LOOP
        INSERT INTO pg_temp.bfs_work(
            vertex_id,
            distance,
            parent_vertex
        )
        VALUES (
            v_source,
            0,
            NULL
        )
        ON CONFLICT (vertex_id) DO NOTHING;

        v_tail := v_tail + 1;
        v_queue[v_tail] := v_source;
    END LOOP;

    -- Standard FIFO BFS.
    WHILE v_head <= v_tail LOOP
        v_current := v_queue[v_head];
        v_head := v_head + 1;

        SELECT distance
        INTO v_distance
        FROM pg_temp.bfs_work
        WHERE bfs_work.vertex_id = v_current;

        FOR v_neighbor IN
            SELECT e.destination_vertex
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.source_vertex = v_current

            UNION

            SELECT e.source_vertex
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.destination_vertex = v_current
              AND v_type = 'UNDIRECTED'
        LOOP
            INSERT INTO pg_temp.bfs_work(
                vertex_id,
                distance,
                parent_vertex
            )
            VALUES (
                v_neighbor,
                v_distance + 1,
                v_current
            )
            ON CONFLICT (vertex_id) DO NOTHING;

            IF FOUND THEN
                v_tail := v_tail + 1;
                v_queue[v_tail] := v_neighbor;
            END IF;
        END LOOP;
    END LOOP;

    INSERT INTO bfs_results(
        run_id,
        vertex_id,
        distance,
        parent_vertex
    )
    SELECT
        v_run_id,
        w.vertex_id,
        w.distance,
        w.parent_vertex
    FROM pg_temp.bfs_work w;

    UPDATE bfs_runs
    SET
        execution_status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE run_id = v_run_id;

    RETURN QUERY
    SELECT
        w.vertex_id,
        w.distance,
        w.parent_vertex
    FROM pg_temp.bfs_work w
    ORDER BY w.distance, w.vertex_id;

EXCEPTION
    WHEN OTHERS THEN
        IF v_run_id IS NOT NULL THEN
            UPDATE bfs_runs
            SET
                execution_status = 'FAILED',
                completed_at = CURRENT_TIMESTAMP
            WHERE run_id = v_run_id;
        END IF;

        RAISE;
END;
$$;

-- ------------------------------------------------------------
-- SHORTEST PATH RECONSTRUCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION reconstruct_path(
    p_run_id BIGINT,
    p_target BIGINT
)
RETURNS TABLE (
    sequence_number INTEGER,
    vertex_id BIGINT,
    distance INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT := p_target;
    v_parent BIGINT;
    v_distance INTEGER;
    v_sequence INTEGER := 0;
    v_path BIGINT[] := ARRAY[]::BIGINT[];
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM bfs_results
        WHERE run_id = p_run_id
          AND vertex_id = p_target
    ) THEN
        RAISE EXCEPTION
            'Target % was not reached in BFS run %',
            p_target,
            p_run_id;
    END IF;

    LOOP
        SELECT r.parent_vertex, r.distance
        INTO v_parent, v_distance
        FROM bfs_results r
        WHERE r.run_id = p_run_id
          AND r.vertex_id = v_current;

        EXIT WHEN NOT FOUND;

        v_path := array_append(v_path, v_current);

        EXIT WHEN v_parent IS NULL;

        v_current := v_parent;
    END LOOP;

    RETURN QUERY
    SELECT
        (array_length(v_path, 1) - position + 1)::INTEGER,
        v_path[array_length(v_path, 1) - position + 1],
        r.distance
    FROM generate_series(
        1,
        array_length(v_path, 1)
    ) AS position
    JOIN bfs_results r
      ON r.run_id = p_run_id
     AND r.vertex_id =
        v_path[array_length(v_path, 1) - position + 1]
    ORDER BY position;
END;
$$;

-- ------------------------------------------------------------
-- LEVEL REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW bfs_level_report AS
SELECT
    run_id,
    distance AS bfs_level,
    COUNT(*) AS vertex_count,
    ARRAY_AGG(vertex_id ORDER BY vertex_id) AS vertices
FROM bfs_results
GROUP BY run_id, distance;

-- ------------------------------------------------------------
-- CONNECTED COMPONENT REPORTING
-- ------------------------------------------------------------
--
-- Undirected connected components are obtained by assigning
-- each vertex the minimum vertex identifier in its component.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION connected_component_report(
    p_graph_id BIGINT
)
RETURNS TABLE (
    vertex_id BIGINT,
    component_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(15);
    v_vertex BIGINT;
    v_component BIGINT;
    v_result RECORD;
    v_run BIGINT;
BEGIN
    SELECT graph_type
    INTO v_type
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    IF v_type <> 'UNDIRECTED' THEN
        RAISE EXCEPTION
            'Connected components require an undirected graph';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS component_work (
        vertex_id BIGINT PRIMARY KEY,
        component_id BIGINT NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE TABLE pg_temp.component_work;

    FOR v_vertex IN
        SELECT v.vertex_id
        FROM vertices v
        WHERE v.graph_id = p_graph_id
        ORDER BY v.vertex_id
    LOOP
        IF EXISTS (
            SELECT 1
            FROM pg_temp.component_work
            WHERE component_work.vertex_id = v_vertex
        ) THEN
            CONTINUE;
        END IF;

        SELECT COALESCE(MAX(component_id), 0) + 1
        INTO v_component
        FROM pg_temp.component_work;

        INSERT INTO pg_temp.component_work
        VALUES (v_vertex, v_component);

        CREATE TEMP TABLE IF NOT EXISTS component_queue (
            vertex_id BIGINT PRIMARY KEY
        ) ON COMMIT DROP;

        TRUNCATE TABLE pg_temp.component_queue;

        INSERT INTO pg_temp.component_queue
        VALUES (v_vertex);

        LOOP
            SELECT q.vertex_id
            INTO v_result
            FROM pg_temp.component_queue q
            ORDER BY q.vertex_id
            LIMIT 1;

            EXIT WHEN NOT FOUND;

            DELETE FROM pg_temp.component_queue
            WHERE component_queue.vertex_id = v_result.vertex_id;

            INSERT INTO pg_temp.component_work(
                vertex_id,
                component_id
            )
            SELECT
                e.destination_vertex,
                v_component
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.source_vertex = v_result.vertex_id
              AND NOT EXISTS (
                  SELECT 1
                  FROM pg_temp.component_work w
                  WHERE w.vertex_id = e.destination_vertex
              )
            ON CONFLICT DO NOTHING;

            INSERT INTO pg_temp.component_queue(vertex_id)
            SELECT w.vertex_id
            FROM pg_temp.component_work w
            WHERE w.component_id = v_component
              AND w.vertex_id <> v_vertex
              AND NOT EXISTS (
                  SELECT 1
                  FROM pg_temp.component_queue q
                  WHERE q.vertex_id = w.vertex_id
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM edges e
                  WHERE e.graph_id = p_graph_id
                    AND e.source_vertex = w.vertex_id
              )
            ON CONFLICT DO NOTHING;
        END LOOP;
    END LOOP;

    RETURN QUERY
    SELECT w.vertex_id, w.component_id
    FROM pg_temp.component_work w
    ORDER BY w.component_id, w.vertex_id;
END;
$$;

-- ------------------------------------------------------------
-- SAMPLE GRAPH
-- ------------------------------------------------------------

INSERT INTO graphs(graph_name, graph_type)
VALUES
    ('learning_network', 'UNDIRECTED'),
    ('dependency_network', 'DIRECTED')
ON CONFLICT (graph_name) DO NOTHING;

INSERT INTO vertices(graph_id, vertex_label)
SELECT g.graph_id, v.vertex_label
FROM graphs g
CROSS JOIN (
    VALUES
        ('A'), ('B'), ('C'), ('D'),
        ('E'), ('F'), ('G'), ('H'),
        ('ISLAND_1'), ('ISLAND_2')
) AS v(vertex_label)
WHERE g.graph_name = 'learning_network'
ON CONFLICT (graph_id, vertex_label) DO NOTHING;

INSERT INTO vertices(graph_id, vertex_label)
SELECT g.graph_id, v.vertex_label
FROM graphs g
CROSS JOIN (
    VALUES
        ('SERVICE_A'), ('SERVICE_B'),
        ('SERVICE_C'), ('SERVICE_D')
) AS v(vertex_label)
WHERE g.graph_name = 'dependency_network'
ON CONFLICT (graph_id, vertex_label) DO NOTHING;

-- Insert undirected graph edges once.
INSERT INTO edges(
    graph_id,
    source_vertex,
    destination_vertex
)
SELECT
    g.graph_id,
    source_v.vertex_id,
    destination_v.vertex_id
FROM graphs g
JOIN (
    VALUES
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('B', 'E'),
        ('C', 'F'),
        ('C', 'G'),
        ('E', 'H'),
        ('F', 'H')
) AS pair(source_label, destination_label)
ON TRUE
JOIN vertices source_v
  ON source_v.graph_id = g.graph_id
 AND source_v.vertex_label = pair.source_label
JOIN vertices destination_v
  ON destination_v.graph_id = g.graph_id
 AND destination_v.vertex_label = pair.destination_label
WHERE g.graph_name = 'learning_network'
ON CONFLICT DO NOTHING;

-- Insert directed dependency edges.
INSERT INTO edges(
    graph_id,
    source_vertex,
    destination_vertex
)
SELECT
    g.graph_id,
    source_v.vertex_id,
    destination_v.vertex_id
FROM graphs g
JOIN (
    VALUES
        ('SERVICE_A', 'SERVICE_B'),
        ('SERVICE_A', 'SERVICE_C'),
        ('SERVICE_B', 'SERVICE_D'),
        ('SERVICE_C', 'SERVICE_D')
) AS pair(source_label, destination_label)
ON TRUE
JOIN vertices source_v
  ON source_v.graph_id = g.graph_id
 AND source_v.vertex_label = pair.source_label
JOIN vertices destination_v
  ON destination_v.graph_id = g.graph_id
 AND destination_v.vertex_label = pair.destination_label
WHERE g.graph_name = 'dependency_network'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- SINGLE-SOURCE BFS
-- ------------------------------------------------------------

SELECT *
FROM run_bfs(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'learning_network'),
    ARRAY[
        (SELECT vertex_id FROM vertices WHERE vertex_label = 'A')
    ]::BIGINT[]
);

-- ------------------------------------------------------------
-- MULTI-SOURCE BFS
-- ------------------------------------------------------------

SELECT *
FROM run_bfs(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'learning_network'),
    ARRAY[
        (SELECT vertex_id FROM vertices WHERE vertex_label = 'A'),
        (SELECT vertex_id FROM vertices WHERE vertex_label = 'H')
    ]::BIGINT[]
);

-- ------------------------------------------------------------
-- LEVEL AGGREGATION
-- ------------------------------------------------------------

SELECT *
FROM bfs_level_report
ORDER BY run_id DESC, bfs_level;

-- ------------------------------------------------------------
-- SHORTEST PATH RECONSTRUCTION
-- ------------------------------------------------------------

SELECT reconstruct_path(
    (SELECT MAX(run_id) FROM bfs_runs
     WHERE graph_id = (
         SELECT graph_id FROM graphs
         WHERE graph_name = 'learning_network'
     )),
    (SELECT vertex_id FROM vertices
     WHERE vertex_label = 'H')
);

-- ------------------------------------------------------------
-- RETRIEVAL AND EVALUATION
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    v.vertex_label,
    r.distance,
    parent.vertex_label AS parent_label
FROM bfs_results r
JOIN bfs_runs br ON br.run_id = r.run_id
JOIN graphs g ON g.graph_id = br.graph_id
JOIN vertices v ON v.vertex_id = r.vertex_id
LEFT JOIN vertices parent ON parent.vertex_id = r.parent_vertex
ORDER BY br.run_id DESC, r.distance, v.vertex_label;

-- Reachability evaluation.
SELECT
    r.run_id,
    COUNT(*) AS reachable_vertices,
    MAX(r.distance) AS maximum_distance,
    AVG(r.distance)::NUMERIC(10, 2) AS average_distance
FROM bfs_results r
GROUP BY r.run_id
ORDER BY r.run_id;

-- Connected-component reporting.
SELECT *
FROM connected_component_report(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'learning_network')
);

-- ------------------------------------------------------------
-- DIRECTED GRAPH TRAVERSAL
-- ------------------------------------------------------------

SELECT *
FROM run_bfs(
    (SELECT graph_id FROM graphs
     WHERE graph_name = 'dependency_network'),
    ARRAY[
        (SELECT vertex_id FROM vertices
         WHERE vertex_label = 'SERVICE_A')
    ]::BIGINT[]
);

-- ------------------------------------------------------------
-- VALIDATION QUERIES
-- ------------------------------------------------------------

-- Unreachable vertices are absent from BFS results.
SELECT
    v.vertex_label,
    CASE
        WHEN r.vertex_id IS NULL THEN 'UNREACHABLE'
        ELSE 'REACHABLE'
    END AS reachability
FROM vertices v
LEFT JOIN bfs_results r
  ON r.vertex_id = v.vertex_id
 AND r.run_id = (
     SELECT MAX(run_id)
     FROM bfs_runs
     WHERE graph_id = v.graph_id
 )
WHERE v.graph_id = (
    SELECT graph_id
    FROM graphs
    WHERE graph_name = 'learning_network'
)
ORDER BY v.vertex_label;

-- Detect inconsistent parent-distance relationships.
SELECT
    child.vertex_id,
    child.distance AS child_distance,
    parent.distance AS parent_distance
FROM bfs_results child
JOIN bfs_results parent
  ON parent.run_id = child.run_id
 AND parent.vertex_id = child.parent_vertex
WHERE child.distance <> parent.distance + 1;

-- Verify that every completed run has result records.
SELECT
    br.run_id,
    br.execution_status,
    COUNT(r.vertex_id) AS visited_vertices
FROM bfs_runs br
LEFT JOIN bfs_results r ON r.run_id = br.run_id
GROUP BY br.run_id, br.execution_status
ORDER BY br.run_id;

-- ------------------------------------------------------------
-- TRANSACTIONAL GRAPH UPDATE
-- ------------------------------------------------------------

SAVEPOINT graph_update;

-- Example of an atomic vertex and edge insertion.
WITH new_vertex AS (
    INSERT INTO vertices(graph_id, vertex_label)
    SELECT graph_id, 'I'
    FROM graphs
    WHERE graph_name = 'learning_network'
    ON CONFLICT (graph_id, vertex_label) DO NOTHING
    RETURNING graph_id, vertex_id
)
INSERT INTO edges(
    graph_id,
    source_vertex,
    destination_vertex
)
SELECT
    nv.graph_id,
    nv.vertex_id,
    existing.vertex_id
FROM new_vertex nv
JOIN vertices existing
  ON existing.graph_id = nv.graph_id
 AND existing.vertex_label = 'H'
ON CONFLICT DO NOTHING;

-- Keep the demonstration update.
RELEASE SAVEPOINT graph_update;

-- ------------------------------------------------------------
-- FINAL EXECUTION REPORT
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    br.run_id,
    br.run_type,
    br.execution_status,
    br.started_at,
    br.completed_at,
    COUNT(r.vertex_id) AS visited_vertices,
    MAX(r.distance) AS maximum_distance
FROM bfs_runs br
JOIN graphs g ON g.graph_id = br.graph_id
LEFT JOIN bfs_results r ON r.run_id = br.run_id
GROUP BY
    g.graph_name,
    br.run_id,
    br.run_type,
    br.execution_status,
    br.started_at,
    br.completed_at
ORDER BY br.run_id;

COMMIT;
