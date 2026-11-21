-- ============================================================
-- DEPTH-FIRST SEARCH AND CONNECTED COMPONENTS
-- PostgreSQL 15+
--
-- Models:
--   Graphs
--   Vertices
--   Undirected edges
--   Recursive DFS
--   Iterative DFS
--   Connected components
--   Traversal history
--   Cycle detection
--   Graph integrity
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS dfs_lab;

SET search_path TO dfs_lab, public;

-- ------------------------------------------------------------
-- 1. Graph definitions
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(graph_name)) > 0)
);

CREATE TABLE IF NOT EXISTS vertices (
    graph_id BIGINT NOT NULL REFERENCES graphs(graph_id)
        ON DELETE CASCADE,
    vertex_id INTEGER NOT NULL,
    vertex_label VARCHAR(150),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (graph_id, vertex_id)
);

CREATE TABLE IF NOT EXISTS edges (
    graph_id BIGINT NOT NULL,
    source_vertex INTEGER NOT NULL,
    destination_vertex INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        graph_id,
        source_vertex,
        destination_vertex
    ),

    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (source_vertex < destination_vertex)
);

CREATE INDEX IF NOT EXISTS idx_edges_destination
    ON edges(graph_id, destination_vertex);

-- ------------------------------------------------------------
-- 2. Traversal execution history
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS traversal_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graphs(graph_id)
        ON DELETE CASCADE,
    start_vertex INTEGER NOT NULL,
    traversal_type VARCHAR(20) NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, start_vertex)
        REFERENCES vertices(graph_id, vertex_id),

    CHECK (
        traversal_type IN (
            'RECURSIVE',
            'ITERATIVE',
            'COMPONENTS'
        )
    )
);

CREATE TABLE IF NOT EXISTS traversal_results (
    run_id BIGINT NOT NULL REFERENCES traversal_runs(run_id)
        ON DELETE CASCADE,
    vertex_id INTEGER NOT NULL,
    parent_vertex INTEGER,
    depth INTEGER NOT NULL,
    visit_order INTEGER NOT NULL,

    PRIMARY KEY (run_id, vertex_id),
    UNIQUE (run_id, visit_order),

    CHECK (depth >= 0),
    CHECK (visit_order >= 1)
);

CREATE TABLE IF NOT EXISTS component_results (
    graph_id BIGINT NOT NULL REFERENCES graphs(graph_id)
        ON DELETE CASCADE,
    vertex_id INTEGER NOT NULL,
    component_id INTEGER NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (graph_id, vertex_id),
    CHECK (component_id > 0)
);

-- ------------------------------------------------------------
-- 3. Maintain undirected edge normalization
--
-- An undirected edge is stored once:
--   (2, 5)
-- not:
--   (2, 5) and (5, 2)
--
-- The CHECK constraint enforces canonical ordering.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION add_undirected_edge(
    p_graph_id BIGINT,
    p_source INTEGER,
    p_destination INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_source INTEGER;
    v_destination INTEGER;
BEGIN
    IF p_source IS NULL OR p_destination IS NULL THEN
        RAISE EXCEPTION 'Edge endpoints cannot be NULL';
    END IF;

    IF p_source = p_destination THEN
        RAISE EXCEPTION 'Self-loops are not supported';
    END IF;

    v_source := LEAST(p_source, p_destination);
    v_destination := GREATEST(p_source, p_destination);

    INSERT INTO edges (
        graph_id,
        source_vertex,
        destination_vertex
    )
    VALUES (
        p_graph_id,
        v_source,
        v_destination
    )
    ON CONFLICT DO NOTHING;
END;
$$;

-- ------------------------------------------------------------
-- 4. Recursive DFS
--
-- Recursive CTE tracks:
--   current vertex
--   parent vertex
--   depth
--   visited path
--
-- Cycle prevention is implemented with ANY(path).
-- DFS-like output ordering is obtained by sorting the
-- generated traversal paths.
--
-- PostgreSQL evaluates recursive CTE iterations internally;
-- the final ORDER BY establishes depth-first presentation.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION recursive_dfs(
    p_graph_id BIGINT,
    p_start_vertex INTEGER
)
RETURNS TABLE (
    vertex_id INTEGER,
    parent_vertex INTEGER,
    depth INTEGER,
    traversal_path INTEGER[]
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vertices v
        WHERE v.graph_id = p_graph_id
          AND v.vertex_id = p_start_vertex
    ) THEN
        RAISE EXCEPTION 'Starting vertex % does not exist',
            p_start_vertex;
    END IF;

    RETURN QUERY
    WITH RECURSIVE walk(
        current_vertex,
        parent,
        current_depth,
        path
    ) AS (
        SELECT
            p_start_vertex,
            NULL::INTEGER,
            0,
            ARRAY[p_start_vertex]::INTEGER[]

        UNION ALL

        SELECT
            neighbor.vertex_id,
            walk.current_vertex,
            walk.current_depth + 1,
            walk.path || neighbor.vertex_id
        FROM walk

        CROSS JOIN LATERAL (
            SELECT e.destination_vertex AS vertex_id
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.source_vertex = walk.current_vertex

            UNION

            SELECT e.source_vertex AS vertex_id
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.destination_vertex = walk.current_vertex
        ) AS neighbor

        WHERE NOT neighbor.vertex_id = ANY(walk.path)
    )
    SELECT
        walk.current_vertex,
        walk.parent,
        walk.current_depth,
        walk.path
    FROM walk
    ORDER BY walk.path;
END;
$$;

-- ------------------------------------------------------------
-- 5. Iterative DFS
--
-- An explicit temporary stack models recursive call state.
-- The temporary visited table prevents duplicate processing.
--
-- The function returns traversal order, parent and depth.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION iterative_dfs(
    p_graph_id BIGINT,
    p_start_vertex INTEGER
)
RETURNS TABLE (
    vertex_id INTEGER,
    parent_vertex INTEGER,
    depth INTEGER,
    visit_order INTEGER
)
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    v_current INTEGER;
    v_parent INTEGER;
    v_depth INTEGER;
    v_neighbor INTEGER;
    v_order INTEGER := 0;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vertices v
        WHERE v.graph_id = p_graph_id
          AND v.vertex_id = p_start_vertex
    ) THEN
        RAISE EXCEPTION 'Starting vertex % does not exist',
            p_start_vertex;
    END IF;

    DROP TABLE IF EXISTS pg_temp.dfs_stack;
    DROP TABLE IF EXISTS pg_temp.dfs_visited;

    CREATE TEMP TABLE dfs_stack (
        stack_id BIGINT GENERATED ALWAYS AS IDENTITY,
        vertex INTEGER NOT NULL,
        parent INTEGER,
        depth INTEGER NOT NULL
    ) ON COMMIT DROP;

    CREATE TEMP TABLE dfs_visited (
        vertex INTEGER PRIMARY KEY,
        parent INTEGER,
        depth INTEGER,
        visit_order INTEGER
    ) ON COMMIT DROP;

    INSERT INTO dfs_stack(vertex, parent, depth)
    VALUES (p_start_vertex, NULL, 0);

    WHILE EXISTS (SELECT 1 FROM dfs_stack)
    LOOP
        SELECT
            s.vertex,
            s.parent,
            s.depth
        INTO
            v_current,
            v_parent,
            v_depth
        FROM dfs_stack s
        ORDER BY s.stack_id DESC
        LIMIT 1;

        DELETE FROM dfs_stack
        WHERE stack_id = (
            SELECT MAX(stack_id)
            FROM dfs_stack
        );

        IF EXISTS (
            SELECT 1
            FROM dfs_visited
            WHERE vertex = v_current
        ) THEN
            CONTINUE;
        END IF;

        v_order := v_order + 1;

        INSERT INTO dfs_visited (
            vertex,
            parent,
            depth,
            visit_order
        )
        VALUES (
            v_current,
            v_parent,
            v_depth,
            v_order
        );

        -- Reverse insertion order makes the smallest
        -- available neighbor the next vertex popped.
        FOR v_neighbor IN
            SELECT neighbors.vertex_id
            FROM (
                SELECT e.destination_vertex AS vertex_id
                FROM edges e
                WHERE e.graph_id = p_graph_id
                  AND e.source_vertex = v_current

                UNION

                SELECT e.source_vertex AS vertex_id
                FROM edges e
                WHERE e.graph_id = p_graph_id
                  AND e.destination_vertex = v_current
            ) AS neighbors
            WHERE NOT EXISTS (
                SELECT 1
                FROM dfs_visited visited
                WHERE visited.vertex = neighbors.vertex_id
            )
            ORDER BY neighbors.vertex_id DESC
        LOOP
            INSERT INTO dfs_stack(vertex, parent, depth)
            VALUES (
                v_neighbor,
                v_current,
                v_depth + 1
            );
        END LOOP;
    END LOOP;

    RETURN QUERY
    SELECT
        visited.vertex,
        visited.parent,
        visited.depth,
        visited.visit_order
    FROM dfs_visited visited
    ORDER BY visited.visit_order;
END;
$$;

-- ------------------------------------------------------------
-- 6. Connected components
--
-- Label propagation:
-- Every vertex begins with its own identifier.
-- Each iteration propagates the smallest known label across
-- adjacent vertices.
-- The procedure stops when no labels change.
--
-- This is an iterative relational algorithm, not DFS.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE calculate_components(
    p_graph_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_changed INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM graphs WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Graph does not exist: %', p_graph_id;
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS component_work (
        vertex_id INTEGER PRIMARY KEY,
        component_id INTEGER NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE TABLE component_work;

    INSERT INTO component_work(vertex_id, component_id)
    SELECT vertex_id, vertex_id
    FROM vertices
    WHERE graph_id = p_graph_id;

    LOOP
        WITH neighbor_labels AS (
            SELECT
                e.source_vertex AS vertex_id,
                cw.component_id
            FROM edges e
            JOIN component_work cw
              ON cw.vertex_id = e.destination_vertex
            WHERE e.graph_id = p_graph_id

            UNION ALL

            SELECT
                e.destination_vertex AS vertex_id,
                cw.component_id
            FROM edges e
            JOIN component_work cw
              ON cw.vertex_id = e.source_vertex
            WHERE e.graph_id = p_graph_id
        ),
        minimum_labels AS (
            SELECT
                vertex_id,
                MIN(component_id) AS new_component_id
            FROM neighbor_labels
            GROUP BY vertex_id
        )
        UPDATE component_work cw
        SET component_id = LEAST(
            cw.component_id,
            ml.new_component_id
        )
        FROM minimum_labels ml
        WHERE ml.vertex_id = cw.vertex_id
          AND cw.component_id > ml.new_component_id;

        GET DIAGNOSTICS v_changed = ROW_COUNT;

        EXIT WHEN v_changed = 0;
    END LOOP;

    DELETE FROM component_results
    WHERE graph_id = p_graph_id;

    INSERT INTO component_results(
        graph_id,
        vertex_id,
        component_id
    )
    SELECT
        p_graph_id,
        vertex_id,
        component_id
    FROM component_work;
END;
$$;

-- ------------------------------------------------------------
-- 7. Cycle detection using DFS
--
-- A visited neighbor other than the current vertex's parent
-- indicates an undirected cycle.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_has_cycle(
    p_graph_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_has_cycle BOOLEAN;
BEGIN
    WITH RECURSIVE walk(
        current_vertex,
        parent_vertex,
        path,
        cycle_found
    ) AS (
        SELECT
            vertex_id,
            NULL::INTEGER,
            ARRAY[vertex_id]::INTEGER[],
            FALSE
        FROM vertices
        WHERE graph_id = p_graph_id

        UNION ALL

        SELECT
            neighbor.vertex_id,
            walk.current_vertex,
            walk.path || neighbor.vertex_id,
            neighbor.vertex_id = ANY(walk.path)
                AND neighbor.vertex_id <> walk.parent_vertex
        FROM walk

        CROSS JOIN LATERAL (
            SELECT e.destination_vertex AS vertex_id
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.source_vertex = walk.current_vertex

            UNION

            SELECT e.source_vertex AS vertex_id
            FROM edges e
            WHERE e.graph_id = p_graph_id
              AND e.destination_vertex = walk.current_vertex
        ) AS neighbor

        WHERE NOT walk.cycle_found
          AND (
              NOT neighbor.vertex_id = ANY(walk.path)
              OR (
                  neighbor.vertex_id = ANY(walk.path)
                  AND neighbor.vertex_id <> walk.parent_vertex
              )
          )
    )
    SELECT COALESCE(BOOL_OR(cycle_found), FALSE)
    INTO v_has_cycle
    FROM walk;

    RETURN v_has_cycle;
END;
$$;

-- ------------------------------------------------------------
-- 8. Sample graph
--
-- Components:
--   {1,2,3,4,5,6,7,8}
--   {9,10}
--   {11}
--
-- The first component contains a cycle.
-- Vertex 11 is isolated.
-- ------------------------------------------------------------

INSERT INTO graphs(graph_name, description)
VALUES (
    'DFS_DEMONSTRATION',
    'Undirected graph for recursive DFS, iterative DFS and components'
)
ON CONFLICT (graph_name) DO NOTHING;

DO $$
DECLARE
    v_graph_id BIGINT;
    v_vertex INTEGER;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION';

    FOR v_vertex IN 1..11
    LOOP
        INSERT INTO vertices(graph_id, vertex_id, vertex_label)
        VALUES (
            v_graph_id,
            v_vertex,
            'Vertex ' || v_vertex
        )
        ON CONFLICT DO NOTHING;
    END LOOP;

    PERFORM add_undirected_edge(v_graph_id, 1, 2);
    PERFORM add_undirected_edge(v_graph_id, 1, 3);
    PERFORM add_undirected_edge(v_graph_id, 2, 4);
    PERFORM add_undirected_edge(v_graph_id, 2, 5);
    PERFORM add_undirected_edge(v_graph_id, 3, 6);
    PERFORM add_undirected_edge(v_graph_id, 3, 7);
    PERFORM add_undirected_edge(v_graph_id, 5, 8);
    PERFORM add_undirected_edge(v_graph_id, 6, 8);
    PERFORM add_undirected_edge(v_graph_id, 9, 10);
END;
$$;

-- ------------------------------------------------------------
-- 9. Store recursive traversal results
-- ------------------------------------------------------------

DO $$
DECLARE
    v_graph_id BIGINT;
    v_run_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION';

    INSERT INTO traversal_runs(
        graph_id,
        start_vertex,
        traversal_type
    )
    VALUES (
        v_graph_id,
        1,
        'RECURSIVE'
    )
    RETURNING run_id INTO v_run_id;

    INSERT INTO traversal_results(
        run_id,
        vertex_id,
        parent_vertex,
        depth,
        visit_order
    )
    SELECT
        v_run_id,
        result.vertex_id,
        result.parent_vertex,
        result.depth,
        ROW_NUMBER() OVER (
            ORDER BY result.traversal_path
        )::INTEGER
    FROM recursive_dfs(v_graph_id, 1) result;
END;
$$;

-- ------------------------------------------------------------
-- 10. Store iterative traversal results
-- ------------------------------------------------------------

DO $$
DECLARE
    v_graph_id BIGINT;
    v_run_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION';

    INSERT INTO traversal_runs(
        graph_id,
        start_vertex,
        traversal_type
    )
    VALUES (
        v_graph_id,
        1,
        'ITERATIVE'
    )
    RETURNING run_id INTO v_run_id;

    INSERT INTO traversal_results(
        run_id,
        vertex_id,
        parent_vertex,
        depth,
        visit_order
    )
    SELECT
        v_run_id,
        result.vertex_id,
        result.parent_vertex,
        result.depth,
        result.visit_order
    FROM iterative_dfs(v_graph_id, 1) result;
END;
$$;

-- ------------------------------------------------------------
-- 11. Calculate connected components
-- ------------------------------------------------------------

CALL calculate_components(
    (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'DFS_DEMONSTRATION'
    )
);

-- ------------------------------------------------------------
-- 12. Reporting views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW component_summary AS
SELECT
    cr.graph_id,
    cr.component_id,
    COUNT(*) AS vertex_count,
    ARRAY_AGG(cr.vertex_id ORDER BY cr.vertex_id) AS vertices
FROM component_results cr
GROUP BY cr.graph_id, cr.component_id;

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.source_vertex, e.destination_vertex)
        AS edge_count
FROM graphs g
LEFT JOIN vertices v
    ON v.graph_id = g.graph_id
LEFT JOIN edges e
    ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name;

-- ------------------------------------------------------------
-- 13. Retrieval queries
-- ------------------------------------------------------------

SELECT *
FROM graph_statistics
WHERE graph_name = 'DFS_DEMONSTRATION';

SELECT
    vertex_id,
    parent_vertex,
    depth,
    visit_order
FROM traversal_results
WHERE run_id = (
    SELECT run_id
    FROM traversal_runs
    WHERE traversal_type = 'ITERATIVE'
      AND graph_id = (
          SELECT graph_id
          FROM graphs
          WHERE graph_name = 'DFS_DEMONSTRATION'
      )
    ORDER BY run_id DESC
    LIMIT 1
)
ORDER BY visit_order;

-- ------------------------------------------------------------
-- 14. Component evaluation and aggregation
-- ------------------------------------------------------------

SELECT
    component_id,
    vertex_count,
    vertices
FROM component_summary
WHERE graph_id = (
    SELECT graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION'
)
ORDER BY component_id;

SELECT
    COUNT(*) AS total_components,
    SUM(vertex_count) AS total_vertices,
    MAX(vertex_count) AS largest_component,
    MIN(vertex_count) AS smallest_component
FROM component_summary
WHERE graph_id = (
    SELECT graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION'
);

-- ------------------------------------------------------------
-- 15. Eligibility and validation queries
--
-- A start vertex is eligible when it exists in the graph.
-- A destination is reachable when it appears in the DFS result.
-- ------------------------------------------------------------

SELECT EXISTS (
    SELECT 1
    FROM vertices
    WHERE graph_id = (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'DFS_DEMONSTRATION'
    )
    AND vertex_id = 1
) AS valid_start_vertex;

SELECT EXISTS (
    SELECT 1
    FROM traversal_results tr
    JOIN traversal_runs run
      ON run.run_id = tr.run_id
    JOIN graphs g
      ON g.graph_id = run.graph_id
    WHERE g.graph_name = 'DFS_DEMONSTRATION'
      AND run.start_vertex = 1
      AND run.traversal_type = 'ITERATIVE'
      AND tr.vertex_id = 10
) AS destination_10_reachable;

-- ------------------------------------------------------------
-- 16. Cycle evaluation
-- ------------------------------------------------------------

SELECT graph_has_cycle(
    (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'DFS_DEMONSTRATION'
    )
) AS contains_cycle;

-- ------------------------------------------------------------
-- 17. Compare recursive and iterative traversal
-- ------------------------------------------------------------

WITH latest_runs AS (
    SELECT
        run_id,
        traversal_type
    FROM traversal_runs
    WHERE graph_id = (
        SELECT graph_id
        FROM graphs
        WHERE graph_name = 'DFS_DEMONSTRATION'
    )
    AND traversal_type IN ('RECURSIVE', 'ITERATIVE')
),
recursive_order AS (
    SELECT
        tr.visit_order,
        tr.vertex_id
    FROM traversal_results tr
    JOIN latest_runs lr
      ON lr.run_id = tr.run_id
    WHERE lr.traversal_type = 'RECURSIVE'
),
iterative_order AS (
    SELECT
        tr.visit_order,
        tr.vertex_id
    FROM traversal_results tr
    JOIN latest_runs lr
      ON lr.run_id = tr.run_id
    WHERE lr.traversal_type = 'ITERATIVE'
)
SELECT
    r.visit_order,
    r.vertex_id AS recursive_vertex,
    i.vertex_id AS iterative_vertex,
    r.vertex_id = i.vertex_id AS matching
FROM recursive_order r
FULL OUTER JOIN iterative_order i
    ON i.visit_order = r.visit_order
ORDER BY COALESCE(r.visit_order, i.visit_order);

-- ------------------------------------------------------------
-- 18. Failure-case demonstration
--
-- The following block intentionally catches invalid operations.
-- The transaction remains usable after each caught exception.
-- ------------------------------------------------------------

DO $$
DECLARE
    v_graph_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION';

    BEGIN
        PERFORM recursive_dfs(v_graph_id, 999);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected invalid-start failure: %',
                SQLERRM;
    END;

    BEGIN
        PERFORM add_undirected_edge(v_graph_id, 1, 1);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected self-loop failure: %',
                SQLERRM;
    END;

    BEGIN
        INSERT INTO edges(
            graph_id,
            source_vertex,
            destination_vertex
        )
        VALUES (v_graph_id, 5, 2);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected normalized-edge failure: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 19. Transactional graph modification example
--
-- The savepoint demonstrates how a graph modification can
-- be rolled back without discarding earlier work.
-- ------------------------------------------------------------

SAVEPOINT before_graph_change;

DO $$
DECLARE
    v_graph_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graphs
    WHERE graph_name = 'DFS_DEMONSTRATION';

    PERFORM add_undirected_edge(v_graph_id, 10, 11);
END;
$$;

ROLLBACK TO SAVEPOINT before_graph_change;

-- ------------------------------------------------------------
-- 20. Final integrity report
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertices,
    COUNT(DISTINCT e.source_vertex, e.destination_vertex) AS edges,
    COUNT(DISTINCT cr.component_id) AS components
FROM graphs g
LEFT JOIN vertices v
    ON v.graph_id = g.graph_id
LEFT JOIN edges e
    ON e.graph_id = g.graph_id
LEFT JOIN component_results cr
    ON cr.graph_id = g.graph_id
   AND cr.vertex_id = v.vertex_id
WHERE g.graph_name = 'DFS_DEMONSTRATION'
GROUP BY g.graph_name;

COMMIT;
