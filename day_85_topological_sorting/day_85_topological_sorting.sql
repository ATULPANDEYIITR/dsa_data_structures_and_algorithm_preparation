-- ============================================================
-- TOPOLOGICAL SORTING AND DEPENDENCY SCHEDULING
-- PostgreSQL 15+
-- ============================================================

DROP SCHEMA IF EXISTS dependency_lab CASCADE;

CREATE SCHEMA dependency_lab;

SET search_path TO dependency_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE task_status AS ENUM (
    'pending',
    'ready',
    'running',
    'completed',
    'failed',
    'blocked'
);

CREATE TYPE dependency_type AS ENUM (
    'finish_to_start',
    'logical'
);

-- ------------------------------------------------------------
-- 2. TASKS
-- ------------------------------------------------------------

CREATE TABLE tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task_code VARCHAR(30) NOT NULL UNIQUE,
    task_name VARCHAR(200) NOT NULL,
    description TEXT,
    duration INTEGER NOT NULL DEFAULT 1,
    status task_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT task_code_not_blank
        CHECK (length(trim(task_code)) > 0),

    CONSTRAINT task_name_not_blank
        CHECK (length(trim(task_name)) > 0),

    CONSTRAINT positive_duration
        CHECK (duration > 0)
);

-- ------------------------------------------------------------
-- 3. DEPENDENCY RELATIONSHIPS
--
-- prerequisite_id -> dependent_id
--
-- A dependent task cannot execute until its prerequisite
-- has completed.
-- ------------------------------------------------------------

CREATE TABLE task_dependencies (
    prerequisite_id BIGINT NOT NULL,
    dependent_id BIGINT NOT NULL,
    relationship dependency_type NOT NULL DEFAULT 'finish_to_start',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (prerequisite_id, dependent_id),

    FOREIGN KEY (prerequisite_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE,

    FOREIGN KEY (dependent_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE,

    CONSTRAINT no_self_dependency
        CHECK (prerequisite_id <> dependent_id)
);

CREATE INDEX idx_dependencies_dependent
    ON task_dependencies(dependent_id);

CREATE INDEX idx_tasks_status
    ON tasks(status);

CREATE INDEX idx_tasks_created
    ON tasks(created_at DESC);

-- ------------------------------------------------------------
-- 4. CYCLE PREVENTION TRIGGER
--
-- Adding A -> B is invalid when B already reaches A.
-- The existing edge is excluded during an UPDATE.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION prevent_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    old_parent BIGINT := NULL;
    old_child BIGINT := NULL;
    creates_cycle BOOLEAN;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        old_parent := OLD.prerequisite_id;
        old_child := OLD.dependent_id;
    END IF;

    WITH RECURSIVE reachable(node_id) AS (
        SELECT NEW.dependent_id

        UNION

        SELECT d.dependent_id
        FROM task_dependencies d
        JOIN reachable r
          ON d.prerequisite_id = r.node_id
        WHERE old_parent IS NULL
           OR d.prerequisite_id <> old_parent
           OR d.dependent_id <> old_child
    )
    SELECT EXISTS (
        SELECT 1
        FROM reachable
        WHERE node_id = NEW.prerequisite_id
    )
    INTO creates_cycle;

    IF creates_cycle THEN
        RAISE EXCEPTION
            'Dependency cycle rejected: % -> %',
            NEW.prerequisite_id,
            NEW.dependent_id
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_dependency_cycle
BEFORE INSERT OR UPDATE ON task_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_dependency_cycle();

-- ------------------------------------------------------------
-- 5. STATUS TRANSITION VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_task_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    dependencies_complete BOOLEAN;
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;

    IF NEW.status = OLD.status THEN
        RETURN NEW;
    END IF;

    IF OLD.status = 'pending'
       AND NEW.status NOT IN ('ready', 'blocked') THEN
        RAISE EXCEPTION
            'Invalid transition: pending -> %',
            NEW.status;
    END IF;

    IF OLD.status = 'ready'
       AND NEW.status NOT IN ('running', 'blocked') THEN
        RAISE EXCEPTION
            'Invalid transition: ready -> %',
            NEW.status;
    END IF;

    IF OLD.status = 'running'
       AND NEW.status NOT IN ('completed', 'failed') THEN
        RAISE EXCEPTION
            'Invalid transition: running -> %',
            NEW.status;
    END IF;

    IF NEW.status = 'ready' THEN
        SELECT NOT EXISTS (
            SELECT 1
            FROM task_dependencies d
            JOIN tasks prerequisite
              ON prerequisite.task_id = d.prerequisite_id
            WHERE d.dependent_id = NEW.task_id
              AND prerequisite.status <> 'completed'
        )
        INTO dependencies_complete;

        IF NOT dependencies_complete THEN
            RAISE EXCEPTION
                'Task % cannot become ready: prerequisites incomplete',
                NEW.task_code;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_task_transition
BEFORE UPDATE OF status ON tasks
FOR EACH ROW
EXECUTE FUNCTION validate_task_status_transition();

-- ------------------------------------------------------------
-- 6. TOPOLOGICAL SORTING FUNCTION
--
-- Kahn's algorithm:
-- 1. Calculate indegrees.
-- 2. Select a zero-indegree task.
-- 3. Record it.
-- 4. Decrease the indegree of its dependents.
-- 5. Repeat until all tasks are processed.
--
-- A missing zero-indegree task with remaining nodes means
-- that the graph contains a cycle.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION topological_order()
RETURNS TABLE (
    ordered_task_id BIGINT,
    ordered_task_code VARCHAR(30),
    ordered_task_name VARCHAR(200),
    execution_position INTEGER,
    execution_level INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_task BIGINT;
    current_level INTEGER;
    total_tasks INTEGER;
    processed_tasks INTEGER := 0;
BEGIN
    DROP TABLE IF EXISTS pg_temp.topo_work;
    DROP TABLE IF EXISTS pg_temp.topo_result;

    CREATE TEMP TABLE topo_work (
        task_id BIGINT PRIMARY KEY,
        indegree INTEGER NOT NULL,
        execution_level INTEGER NOT NULL DEFAULT 0,
        processed BOOLEAN NOT NULL DEFAULT FALSE
    ) ON COMMIT DROP;

    CREATE TEMP TABLE topo_result (
        task_id BIGINT PRIMARY KEY,
        execution_position INTEGER NOT NULL,
        execution_level INTEGER NOT NULL
    ) ON COMMIT DROP;

    INSERT INTO topo_work (
        task_id,
        indegree
    )
    SELECT
        t.task_id,
        COUNT(d.prerequisite_id)::INTEGER
    FROM tasks t
    LEFT JOIN task_dependencies d
      ON d.dependent_id = t.task_id
    GROUP BY t.task_id;

    SELECT COUNT(*)::INTEGER
    INTO total_tasks
    FROM topo_work;

    WHILE processed_tasks < total_tasks LOOP

        -- Deterministic selection among currently available tasks.
        SELECT w.task_id, w.execution_level
        INTO current_task, current_level
        FROM topo_work w
        WHERE w.indegree = 0
          AND NOT w.processed
        ORDER BY w.task_id
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Topological sorting failed: dependency cycle detected'
                USING ERRCODE = '23514';
        END IF;

        processed_tasks := processed_tasks + 1;

        UPDATE topo_work
        SET processed = TRUE
        WHERE task_id = current_task;

        INSERT INTO topo_result (
            task_id,
            execution_position,
            execution_level
        )
        VALUES (
            current_task,
            processed_tasks,
            current_level
        );

        -- Remove the completed prerequisite from each dependent.
        UPDATE topo_work w
        SET
            indegree = w.indegree - 1,
            execution_level = GREATEST(
                w.execution_level,
                current_level + 1
            )
        FROM task_dependencies d
        WHERE d.prerequisite_id = current_task
          AND d.dependent_id = w.task_id
          AND NOT w.processed;

    END LOOP;

    RETURN QUERY
    SELECT
        t.task_id,
        t.task_code,
        t.task_name,
        r.execution_position,
        r.execution_level
    FROM topo_result r
    JOIN tasks t
      ON t.task_id = r.task_id
    ORDER BY r.execution_position;
END;
$$;

-- ------------------------------------------------------------
-- 7. CRITICAL PATH FUNCTION
--
-- Uses the topological order and dynamic programming.
-- Duration is measured as the sum of task durations along
-- the longest dependency path.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_critical_path()
RETURNS TABLE (
    task_code VARCHAR(30),
    earliest_finish INTEGER,
    predecessor_code VARCHAR(30)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE ordered AS (
        SELECT *
        FROM topological_order()
    ),
    path_values AS (
        SELECT
            o.ordered_task_id,
            o.ordered_task_code,
            t.duration,
            0::INTEGER AS start_time,
            NULL::VARCHAR(30) AS predecessor
        FROM ordered o
        JOIN tasks t
          ON t.task_id = o.ordered_task_id
        WHERE o.execution_position = 1

        UNION ALL

        SELECT
            o.ordered_task_id,
            o.ordered_task_code,
            t.duration,
            COALESCE(
                (
                    SELECT MAX(p.earliest_finish)
                    FROM path_values p
                    JOIN task_dependencies d
                      ON d.prerequisite_id = p.ordered_task_id
                    WHERE d.dependent_id = o.ordered_task_id
                ),
                0
            ),
            (
                SELECT p.ordered_task_code
                FROM path_values p
                JOIN task_dependencies d
                  ON d.prerequisite_id = p.ordered_task_id
                WHERE d.dependent_id = o.ordered_task_id
                ORDER BY p.earliest_finish DESC,
                         p.ordered_task_code
                LIMIT 1
            )
        FROM ordered o
        JOIN tasks t
          ON t.task_id = o.ordered_task_id
        WHERE o.execution_position > 1
    )
    SELECT
        p.ordered_task_code,
        p.start_time + p.duration,
        p.predecessor
    FROM path_values p;
END;
$$;

-- ------------------------------------------------------------
-- 8. REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW dependency_report AS
SELECT
    t.task_id,
    t.task_code,
    t.task_name,
    t.duration,
    t.status,
    COUNT(DISTINCT d.prerequisite_id) AS prerequisite_count,
    COUNT(DISTINCT child.dependent_id) AS dependent_count,
    COALESCE(
        array_agg(DISTINCT parent.task_code)
            FILTER (WHERE parent.task_code IS NOT NULL),
        ARRAY[]::VARCHAR[]
    ) AS prerequisites
FROM tasks t
LEFT JOIN task_dependencies d
    ON d.dependent_id = t.task_id
LEFT JOIN tasks parent
    ON parent.task_id = d.prerequisite_id
LEFT JOIN task_dependencies child
    ON child.prerequisite_id = t.task_id
GROUP BY
    t.task_id,
    t.task_code,
    t.task_name,
    t.duration,
    t.status;

-- ------------------------------------------------------------
-- 9. SAMPLE PROJECT
-- ------------------------------------------------------------

INSERT INTO tasks (
    task_code,
    task_name,
    description,
    duration
)
VALUES
(
    'T1',
    'Gather requirements',
    'Collect business and technical requirements.',
    2
),
(
    'T2',
    'Design architecture',
    'Define application architecture.',
    3
),
(
    'T3',
    'Design database',
    'Design relational database structures.',
    2
),
(
    'T4',
    'Implement backend',
    'Implement APIs and business logic.',
    5
),
(
    'T5',
    'Implement frontend',
    'Implement user interface.',
    4
),
(
    'T6',
    'Integrate application',
    'Integrate frontend and backend.',
    2
),
(
    'T7',
    'Execute testing',
    'Perform functional and integration testing.',
    3
),
(
    'T8',
    'Security assessment',
    'Perform application security validation.',
    2
),
(
    'T9',
    'Production deployment',
    'Release the approved application.',
    1
);

INSERT INTO task_dependencies (
    prerequisite_id,
    dependent_id
)
SELECT parent.task_id, child.task_id
FROM (
    VALUES
        ('T1', 'T2'),
        ('T1', 'T3'),
        ('T2', 'T4'),
        ('T3', 'T4'),
        ('T2', 'T5'),
        ('T4', 'T6'),
        ('T5', 'T6'),
        ('T6', 'T7'),
        ('T6', 'T8'),
        ('T7', 'T9'),
        ('T8', 'T9')
) AS edges(parent_code, child_code)
JOIN tasks parent
  ON parent.task_code = edges.parent_code
JOIN tasks child
  ON child.task_code = edges.child_code;

-- ------------------------------------------------------------
-- 10. RETRIEVAL
-- ------------------------------------------------------------

SELECT *
FROM dependency_report
ORDER BY task_code;

-- Retrieve direct prerequisites.
SELECT
    dependent.task_code AS dependent_task,
    prerequisite.task_code AS prerequisite_task
FROM task_dependencies d
JOIN tasks dependent
    ON dependent.task_id = d.dependent_id
JOIN tasks prerequisite
    ON prerequisite.task_id = d.prerequisite_id
ORDER BY dependent.task_code, prerequisite.task_code;

-- Retrieve direct dependents.
SELECT
    prerequisite.task_code,
    dependent.task_code
FROM task_dependencies d
JOIN tasks prerequisite
    ON prerequisite.task_id = d.prerequisite_id
JOIN tasks dependent
    ON dependent.task_id = d.dependent_id
ORDER BY prerequisite.task_code, dependent.task_code;

-- ------------------------------------------------------------
-- 11. TOPOLOGICAL ORDERING
-- ------------------------------------------------------------

SELECT *
FROM topological_order();

-- ------------------------------------------------------------
-- 12. EXECUTION LEVELS
--
-- Tasks in the same level have no dependency path between
-- them and can be considered for parallel execution.
-- ------------------------------------------------------------

SELECT
    execution_level,
    array_agg(ordered_task_code ORDER BY ordered_task_code)
        AS parallel_tasks,
    COUNT(*) AS task_count
FROM topological_order()
GROUP BY execution_level
ORDER BY execution_level;

-- ------------------------------------------------------------
-- 13. VALIDATION
-- ------------------------------------------------------------

-- Verify every dependency respects the calculated order.
WITH ordering AS (
    SELECT *
    FROM topological_order()
)
SELECT
    parent.ordered_task_code AS prerequisite,
    child.ordered_task_code AS dependent,
    parent.execution_position < child.execution_position
        AS dependency_valid
FROM task_dependencies d
JOIN ordering parent
    ON parent.ordered_task_id = d.prerequisite_id
JOIN ordering child
    ON child.ordered_task_id = d.dependent_id
ORDER BY prerequisite, dependent;

-- Detect tasks without prerequisites.
SELECT
    t.task_code,
    t.task_name
FROM tasks t
WHERE NOT EXISTS (
    SELECT 1
    FROM task_dependencies d
    WHERE d.dependent_id = t.task_id
)
ORDER BY t.task_code;

-- Detect tasks without dependents.
SELECT
    t.task_code,
    t.task_name
FROM tasks t
WHERE NOT EXISTS (
    SELECT 1
    FROM task_dependencies d
    WHERE d.prerequisite_id = t.task_id
)
ORDER BY t.task_code;

-- ------------------------------------------------------------
-- 14. CRITICAL PATH REPORT
-- ------------------------------------------------------------

SELECT *
FROM calculate_critical_path()
ORDER BY earliest_finish;

-- ------------------------------------------------------------
-- 15. WORKFLOW ELIGIBILITY
-- ------------------------------------------------------------

-- A task is eligible when all direct prerequisites are complete.
SELECT
    t.task_code,
    t.status,
    NOT EXISTS (
        SELECT 1
        FROM task_dependencies d
        JOIN tasks parent
            ON parent.task_id = d.prerequisite_id
        WHERE d.dependent_id = t.task_id
          AND parent.status <> 'completed'
    ) AS dependency_eligible
FROM tasks t
ORDER BY t.task_code;

-- ------------------------------------------------------------
-- 16. TRANSACTIONAL EXECUTION
--
-- Demonstrate a valid sequence:
-- T1 becomes ready, starts, and completes.
-- T2 then becomes eligible.
-- ------------------------------------------------------------

BEGIN;

UPDATE tasks
SET status = 'ready'
WHERE task_code = 'T1';

UPDATE tasks
SET status = 'running'
WHERE task_code = 'T1';

UPDATE tasks
SET status = 'completed'
WHERE task_code = 'T1';

UPDATE tasks
SET status = 'ready'
WHERE task_code = 'T2';

COMMIT;

-- Confirm execution state.
SELECT task_code, status
FROM tasks
ORDER BY task_code;

-- ------------------------------------------------------------
-- 17. FAILURE CASE: INVALID TRANSITION
--
-- The following statement is intentionally isolated.
-- It demonstrates the trigger rejecting a transition from
-- pending directly to completed.
--
-- Execute separately if testing the failure:
--
-- UPDATE tasks
-- SET status = 'completed'
-- WHERE task_code = 'T3';
--
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- 18. FAILURE CASE: CYCLE PREVENTION
--
-- T9 -> T1 would introduce a cycle because T1 reaches T9.
-- Execute separately to observe the trigger exception:
--
-- INSERT INTO task_dependencies (
--     prerequisite_id,
--     dependent_id
-- )
-- SELECT
--     parent.task_id,
--     child.task_id
-- FROM tasks parent, tasks child
-- WHERE parent.task_code = 'T9'
--   AND child.task_code = 'T1';
--
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- 19. AGGREGATION AND PROJECT REPORTING
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_tasks,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_tasks,
    COUNT(*) FILTER (
        WHERE status = 'pending'
    ) AS pending_tasks,
    COUNT(*) FILTER (
        WHERE status = 'failed'
    ) AS failed_tasks,
    COUNT(*) FILTER (
        WHERE status = 'blocked'
    ) AS blocked_tasks,
    SUM(duration) AS total_task_duration,
    AVG(duration)::NUMERIC(10, 2) AS average_task_duration
FROM tasks;

-- Dependency complexity report.
SELECT
    t.task_code,
    COUNT(d.prerequisite_id) AS incoming_dependencies
FROM tasks t
LEFT JOIN task_dependencies d
    ON d.dependent_id = t.task_id
GROUP BY t.task_id, t.task_code
ORDER BY incoming_dependencies DESC, t.task_code;

-- ------------------------------------------------------------
-- 20. TRANSITIVE DEPENDENCY ANALYSIS
--
-- Find every task reachable from T1.
-- UNION prevents repeated nodes in the recursive traversal.
-- ------------------------------------------------------------

WITH RECURSIVE dependency_tree AS (
    SELECT
        d.prerequisite_id,
        d.dependent_id,
        1 AS depth
    FROM task_dependencies d
    JOIN tasks t
        ON t.task_id = d.prerequisite_id
    WHERE t.task_code = 'T1'

    UNION

    SELECT
        d.prerequisite_id,
        d.dependent_id,
        tree.depth + 1
    FROM dependency_tree tree
    JOIN task_dependencies d
        ON d.prerequisite_id = tree.dependent_id
    WHERE tree.depth < 100
)
SELECT DISTINCT
    parent.task_code AS prerequisite,
    child.task_code AS dependent,
    depth
FROM dependency_tree tree
JOIN tasks parent
    ON parent.task_id = tree.prerequisite_id
JOIN tasks child
    ON child.task_id = tree.dependent_id
ORDER BY depth, prerequisite, dependent;

-- ------------------------------------------------------------
-- 21. FINAL PROJECT STATUS
-- ------------------------------------------------------------

SELECT
    CASE
        WHEN COUNT(*) FILTER (
            WHERE status = 'failed'
        ) > 0
            THEN 'FAILED'
        WHEN COUNT(*) FILTER (
            WHERE status = 'blocked'
        ) > 0
            THEN 'BLOCKED'
        WHEN COUNT(*) FILTER (
            WHERE status <> 'completed'
        ) = 0
            THEN 'COMPLETED'
        ELSE 'IN PROGRESS'
    END AS project_status,
    COUNT(*) AS total_tasks
FROM tasks;
