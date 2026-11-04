-- ============================================================
-- LOWEST COMMON ANCESTOR
-- PostgreSQL 14+
--
-- Models an enterprise organizational hierarchy represented
-- as a binary tree.
--
-- Includes:
--   1. Recursive LCA using recursive CTEs.
--   2. Parent-based LCA using ancestor paths.
--   3. Binary-tree hierarchy validation.
--   4. Ancestor-distance calculation.
--   5. Multiple-node common ancestor retrieval.
--   6. Cycle prevention and transactional integrity.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS hierarchy;

DROP VIEW IF EXISTS hierarchy.employee_hierarchy_report CASCADE;
DROP FUNCTION IF EXISTS hierarchy.find_lca(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS hierarchy.find_lca_parent_based(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS hierarchy.find_lca_many(INTEGER[]) CASCADE;
DROP FUNCTION IF EXISTS hierarchy.get_ancestor_distance(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS hierarchy.validate_hierarchy() CASCADE;
DROP FUNCTION IF EXISTS hierarchy.prevent_hierarchy_cycle() CASCADE;
DROP TABLE IF EXISTS hierarchy.hierarchy_audit CASCADE;
DROP TABLE IF EXISTS hierarchy.employee_relationship CASCADE;
DROP TABLE IF EXISTS hierarchy.employee CASCADE;
DROP TABLE IF EXISTS hierarchy.department CASCADE;

-- ------------------------------------------------------------
-- 1. Domain tables
-- ------------------------------------------------------------

CREATE TABLE hierarchy.department (
    department_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hierarchy.employee (
    employee_id INTEGER PRIMARY KEY,
    employee_name VARCHAR(120) NOT NULL,
    department_id INTEGER NOT NULL
        REFERENCES hierarchy.department(department_id),
    employment_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (
            employment_status IN (
                'ACTIVE',
                'INACTIVE',
                'ON_LEAVE'
            )
        ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Each employee has at most one manager and at most two direct
-- reports in this binary-tree representation.
CREATE TABLE hierarchy.employee_relationship (
    employee_id INTEGER PRIMARY KEY
        REFERENCES hierarchy.employee(employee_id)
        ON DELETE CASCADE,

    manager_id INTEGER
        REFERENCES hierarchy.employee(employee_id)
        ON DELETE RESTRICT,

    child_position VARCHAR(5)
        CHECK (child_position IN ('LEFT', 'RIGHT')),

    CONSTRAINT no_self_management
        CHECK (manager_id IS NULL OR manager_id <> employee_id),

    CONSTRAINT root_has_no_position
        CHECK (
            (manager_id IS NULL AND child_position IS NULL)
            OR
            (manager_id IS NOT NULL AND child_position IS NOT NULL)
        ),

    CONSTRAINT unique_manager_position
        UNIQUE (manager_id, child_position)
);

CREATE TABLE hierarchy.hierarchy_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    previous_manager_id INTEGER,
    new_manager_id INTEGER,
    previous_position VARCHAR(5),
    new_position VARCHAR(5),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT NOT NULL DEFAULT CURRENT_USER
);

CREATE INDEX idx_employee_department
    ON hierarchy.employee(department_id);

CREATE INDEX idx_employee_status
    ON hierarchy.employee(employment_status);

CREATE INDEX idx_relationship_manager
    ON hierarchy.employee_relationship(manager_id);

CREATE INDEX idx_relationship_manager_position
    ON hierarchy.employee_relationship(manager_id, child_position);

-- ------------------------------------------------------------
-- 2. Prevent cycles and multiple roots
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.prevent_hierarchy_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_node INTEGER;
BEGIN
    IF NEW.manager_id IS NULL THEN
        IF EXISTS (
            SELECT 1
            FROM hierarchy.employee_relationship er
            WHERE er.employee_id <> NEW.employee_id
              AND er.manager_id IS NULL
        ) THEN
            RAISE EXCEPTION
                'Only one root employee is permitted.';
        END IF;

        RETURN NEW;
    END IF;

    IF NEW.manager_id = NEW.employee_id THEN
        RAISE EXCEPTION 'An employee cannot manage themselves.';
    END IF;

    -- Walk upward from the proposed manager. If the employee being
    -- moved is encountered, the proposed relationship creates a cycle.
    WITH RECURSIVE ancestors(employee_id, manager_id) AS (
        SELECT er.employee_id, er.manager_id
        FROM hierarchy.employee_relationship er
        WHERE er.employee_id = NEW.manager_id

        UNION ALL

        SELECT parent.employee_id, parent.manager_id
        FROM hierarchy.employee_relationship parent
        JOIN ancestors a
          ON parent.employee_id = a.manager_id
        WHERE a.manager_id IS NOT NULL
    )
    SELECT employee_id
    INTO current_node
    FROM ancestors
    WHERE employee_id = NEW.employee_id
    LIMIT 1;

    IF current_node IS NOT NULL THEN
        RAISE EXCEPTION
            'Hierarchy cycle detected for employee %.',
            NEW.employee_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_hierarchy_cycle
BEFORE INSERT OR UPDATE OF manager_id, child_position
ON hierarchy.employee_relationship
FOR EACH ROW
EXECUTE FUNCTION hierarchy.prevent_hierarchy_cycle();

-- ------------------------------------------------------------
-- 3. Audit relationship modifications
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.audit_relationship_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO hierarchy.hierarchy_audit (
            employee_id,
            new_manager_id,
            new_position
        )
        VALUES (
            NEW.employee_id,
            NEW.manager_id,
            NEW.child_position
        );

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO hierarchy.hierarchy_audit (
            employee_id,
            previous_manager_id,
            new_manager_id,
            previous_position,
            new_position
        )
        VALUES (
            NEW.employee_id,
            OLD.manager_id,
            NEW.manager_id,
            OLD.child_position,
            NEW.child_position
        );

        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_audit_relationship_change
AFTER INSERT OR UPDATE
ON hierarchy.employee_relationship
FOR EACH ROW
EXECUTE FUNCTION hierarchy.audit_relationship_change();

-- ------------------------------------------------------------
-- 4. Sample enterprise organization
-- ------------------------------------------------------------

INSERT INTO hierarchy.department (
    department_name,
    description
)
VALUES
    ('Executive Office', 'Organization leadership'),
    ('Technology', 'Technology and engineering'),
    ('Operations', 'Business and operational services'),
    ('Platform Engineering', 'Platform infrastructure'),
    ('Security Engineering', 'Application and cloud security'),
    ('Operations Research', 'Operational analytics'),
    ('Infrastructure', 'Network and infrastructure');

INSERT INTO hierarchy.employee (
    employee_id,
    employee_name,
    department_id,
    employment_status
)
VALUES
    (1, 'Executive Director',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Executive Office'), 'ACTIVE'),

    (2, 'Technology Director',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Technology'), 'ACTIVE'),

    (3, 'Operations Director',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Operations'), 'ACTIVE'),

    (4, 'Platform Manager',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Platform Engineering'), 'ACTIVE'),

    (5, 'Security Manager',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Security Engineering'), 'ACTIVE'),

    (6, 'Research Manager',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Operations Research'), 'ACTIVE'),

    (7, 'Infrastructure Manager',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Infrastructure'), 'ACTIVE'),

    (8, 'Application Security Engineer',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Security Engineering'), 'ACTIVE'),

    (9, 'Cloud Security Engineer',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Security Engineering'), 'ACTIVE'),

    (10, 'Network Engineer',
        (SELECT department_id FROM hierarchy.department
         WHERE department_name = 'Infrastructure'), 'INACTIVE');

INSERT INTO hierarchy.employee_relationship (
    employee_id,
    manager_id,
    child_position
)
VALUES
    (1, NULL, NULL),
    (2, 1, 'LEFT'),
    (3, 1, 'RIGHT'),
    (4, 2, 'LEFT'),
    (5, 2, 'RIGHT'),
    (6, 3, 'LEFT'),
    (7, 3, 'RIGHT'),
    (8, 5, 'LEFT'),
    (9, 5, 'RIGHT'),
    (10, 7, 'RIGHT');

-- ------------------------------------------------------------
-- 5. Recursive binary-tree LCA
-- ------------------------------------------------------------
--
-- A recursive traversal builds root-to-node paths.
-- The common prefix of the two paths ends at the LCA.
--
-- The query also validates that both target employees exist.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.find_lca(
    p_first INTEGER,
    p_second INTEGER
)
RETURNS TABLE (
    ancestor_id INTEGER,
    ancestor_name VARCHAR(120),
    ancestor_depth INTEGER
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE tree_paths AS (
        SELECT
            e.employee_id,
            e.employee_name,
            er.manager_id,
            ARRAY[e.employee_id]::INTEGER[] AS path,
            0 AS depth
        FROM hierarchy.employee e
        JOIN hierarchy.employee_relationship er
          ON er.employee_id = e.employee_id
        WHERE er.manager_id IS NULL

        UNION ALL

        SELECT
            child.employee_id,
            child.employee_name,
            relationship.manager_id,
            parent.path || child.employee_id,
            parent.depth + 1
        FROM tree_paths parent
        JOIN hierarchy.employee_relationship relationship
          ON relationship.manager_id = parent.employee_id
        JOIN hierarchy.employee child
          ON child.employee_id = relationship.employee_id
    ),
    first_path AS (
        SELECT path
        FROM tree_paths
        WHERE employee_id = p_first
    ),
    second_path AS (
        SELECT path
        FROM tree_paths
        WHERE employee_id = p_second
    ),
    common_nodes AS (
        SELECT
            first_path.path[position] AS employee_id,
            position AS depth
        FROM first_path
        CROSS JOIN second_path
        CROSS JOIN LATERAL
            generate_subscripts(first_path.path, 1) AS positions(position)
        WHERE position <= cardinality(second_path.path)
          AND first_path.path[position] = second_path.path[position]
    )
    SELECT
        employee.employee_id,
        employee.employee_name,
        common_nodes.depth - 1
    FROM common_nodes
    JOIN hierarchy.employee employee
      ON employee.employee_id = common_nodes.employee_id
    ORDER BY common_nodes.depth DESC
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 6. Parent-based LCA
-- ------------------------------------------------------------
--
-- First collect the ancestors of the first employee.
-- Then walk upward from the second employee until a match occurs.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.find_lca_parent_based(
    p_first INTEGER,
    p_second INTEGER
)
RETURNS TABLE (
    ancestor_id INTEGER,
    ancestor_name VARCHAR(120)
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE first_ancestors AS (
        SELECT
            e.employee_id,
            er.manager_id,
            0 AS distance
        FROM hierarchy.employee e
        JOIN hierarchy.employee_relationship er
          ON er.employee_id = e.employee_id
        WHERE e.employee_id = p_first

        UNION ALL

        SELECT
            parent.employee_id,
            parent.manager_id,
            child.distance + 1
        FROM first_ancestors child
        JOIN hierarchy.employee_relationship parent
          ON parent.employee_id = child.manager_id
    ),
    second_ancestors AS (
        SELECT
            e.employee_id,
            er.manager_id,
            0 AS distance
        FROM hierarchy.employee e
        JOIN hierarchy.employee_relationship er
          ON er.employee_id = e.employee_id
        WHERE e.employee_id = p_second

        UNION ALL

        SELECT
            parent.employee_id,
            parent.manager_id,
            child.distance + 1
        FROM second_ancestors child
        JOIN hierarchy.employee_relationship parent
          ON parent.employee_id = child.manager_id
    )
    SELECT
        employee.employee_id,
        employee.employee_name
    FROM first_ancestors first
    JOIN second_ancestors second
      ON second.employee_id = first.employee_id
    JOIN hierarchy.employee employee
      ON employee.employee_id = first.employee_id
    ORDER BY
        first.distance + second.distance ASC,
        first.distance ASC
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 7. LCA for multiple target employees
-- ------------------------------------------------------------
--
-- The lowest common ancestor is the deepest node that appears
-- in every target's root-to-node path.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.find_lca_many(
    p_employee_ids INTEGER[]
)
RETURNS TABLE (
    ancestor_id INTEGER,
    ancestor_name VARCHAR(120),
    ancestor_depth INTEGER
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE tree_paths AS (
        SELECT
            e.employee_id,
            ARRAY[e.employee_id]::INTEGER[] AS path,
            0 AS depth
        FROM hierarchy.employee e
        JOIN hierarchy.employee_relationship er
          ON er.employee_id = e.employee_id
        WHERE er.manager_id IS NULL

        UNION ALL

        SELECT
            child.employee_id,
            parent.path || child.employee_id,
            parent.depth + 1
        FROM tree_paths parent
        JOIN hierarchy.employee_relationship relationship
          ON relationship.manager_id = parent.employee_id
        JOIN hierarchy.employee child
          ON child.employee_id = relationship.employee_id
    ),
    targets AS (
        SELECT DISTINCT unnest(p_employee_ids) AS employee_id
    ),
    target_count AS (
        SELECT COUNT(*) AS total FROM targets
    ),
    candidate_ancestors AS (
        SELECT
            paths.employee_id,
            paths.depth,
            COUNT(*) AS matched_targets
        FROM tree_paths paths
        JOIN targets target
          ON paths.employee_id = ANY (
              ARRAY(
                  SELECT path_element
                  FROM unnest(paths.path) AS path_element
              )
          )
        GROUP BY paths.employee_id, paths.depth
    ),
    valid_candidates AS (
        SELECT candidate.employee_id, candidate.depth
        FROM candidate_ancestors candidate
        CROSS JOIN target_count
        WHERE candidate.matched_targets = target_count.total
    )
    SELECT
        employee.employee_id,
        employee.employee_name,
        candidate.depth
    FROM valid_candidates candidate
    JOIN hierarchy.employee employee
      ON employee.employee_id = candidate.employee_id
    ORDER BY candidate.depth DESC
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 8. Ancestor distance
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.get_ancestor_distance(
    p_ancestor INTEGER,
    p_descendant INTEGER
)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE upward AS (
        SELECT
            employee_id,
            manager_id,
            0 AS distance
        FROM hierarchy.employee_relationship
        WHERE employee_id = p_descendant

        UNION ALL

        SELECT
            parent.employee_id,
            parent.manager_id,
            child.distance + 1
        FROM upward child
        JOIN hierarchy.employee_relationship parent
          ON parent.employee_id = child.manager_id
    )
    SELECT distance
    FROM upward
    WHERE employee_id = p_ancestor
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 9. Complete hierarchy validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION hierarchy.validate_hierarchy()
RETURNS TABLE (
    validation_name TEXT,
    is_valid BOOLEAN,
    details TEXT
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE reachable AS (
        SELECT
            employee_id,
            manager_id,
            ARRAY[employee_id]::INTEGER[] AS path,
            false AS cycle_detected
        FROM hierarchy.employee_relationship
        WHERE manager_id IS NULL

        UNION ALL

        SELECT
            child.employee_id,
            child.manager_id,
            parent.path || child.employee_id,
            child.employee_id = ANY(parent.path)
        FROM reachable parent
        JOIN hierarchy.employee_relationship child
          ON child.manager_id = parent.employee_id
        WHERE NOT parent.cycle_detected
    ),
    statistics AS (
        SELECT
            (SELECT COUNT(*) FROM hierarchy.employee) AS employee_count,
            (SELECT COUNT(*) FROM hierarchy.employee_relationship)
                AS relationship_count,
            (SELECT COUNT(*) FROM reachable) AS reachable_count,
            (SELECT COUNT(*) FROM hierarchy.employee_relationship
             WHERE manager_id IS NULL) AS root_count,
            (SELECT COUNT(*) FROM reachable
             WHERE cycle_detected) AS cycle_count
    )
    SELECT
        'ROOT_COUNT',
        root_count = 1,
        format('Detected roots: %s', root_count)
    FROM statistics

    UNION ALL

    SELECT
        'RELATIONSHIP_COVERAGE',
        employee_count = relationship_count,
        format(
            'Employees: %s, relationships: %s',
            employee_count,
            relationship_count
        )
    FROM statistics

    UNION ALL

    SELECT
        'REACHABILITY',
        employee_count = reachable_count,
        format(
            'Employees: %s, reachable: %s',
            employee_count,
            reachable_count
        )
    FROM statistics

    UNION ALL

    SELECT
        'CYCLE_CHECK',
        cycle_count = 0,
        format('Detected cycles: %s', cycle_count)
    FROM statistics;
$$;

-- ------------------------------------------------------------
-- 10. Reporting view
-- ------------------------------------------------------------

CREATE VIEW hierarchy.employee_hierarchy_report AS
WITH RECURSIVE hierarchy_walk AS (
    SELECT
        e.employee_id,
        e.employee_name,
        e.department_id,
        e.employment_status,
        er.manager_id,
        0 AS hierarchy_level,
        ARRAY[e.employee_id]::INTEGER[] AS employee_path
    FROM hierarchy.employee e
    JOIN hierarchy.employee_relationship er
      ON er.employee_id = e.employee_id
    WHERE er.manager_id IS NULL

    UNION ALL

    SELECT
        child.employee_id,
        child.employee_name,
        child.department_id,
        child.employment_status,
        relationship.manager_id,
        parent.hierarchy_level + 1,
        parent.employee_path || child.employee_id
    FROM hierarchy_walk parent
    JOIN hierarchy.employee_relationship relationship
      ON relationship.manager_id = parent.employee_id
    JOIN hierarchy.employee child
      ON child.employee_id = relationship.employee_id
)
SELECT
    hierarchy_walk.employee_id,
    hierarchy_walk.employee_name,
    department.department_name,
    hierarchy_walk.employment_status,
    hierarchy_walk.manager_id,
    manager.employee_name AS manager_name,
    hierarchy_walk.hierarchy_level,
    hierarchy_walk.employee_path
FROM hierarchy_walk
JOIN hierarchy.department department
  ON department.department_id = hierarchy_walk.department_id
LEFT JOIN hierarchy.employee manager
  ON manager.employee_id = hierarchy_walk.manager_id;

-- ------------------------------------------------------------
-- 11. Query examples: retrieval and evaluation
-- ------------------------------------------------------------

-- Direct and indirect reporting relationships.
SELECT *
FROM hierarchy.employee_hierarchy_report
ORDER BY hierarchy_level, employee_id;

-- Recursive LCA.
SELECT *
FROM hierarchy.find_lca(8, 9);

-- Parent-based LCA.
SELECT *
FROM hierarchy.find_lca_parent_based(8, 10);

-- Same node as both targets.
SELECT *
FROM hierarchy.find_lca(8, 8);

-- LCA for several employees.
SELECT *
FROM hierarchy.find_lca_many(ARRAY[8, 9, 10]);

-- Distance from a manager to a descendant.
SELECT hierarchy.get_ancestor_distance(2, 8)
    AS manager_to_employee_distance;

-- Non-ancestor relationship returns NULL.
SELECT hierarchy.get_ancestor_distance(3, 8)
    AS invalid_ancestor_distance;

-- Hierarchy integrity report.
SELECT *
FROM hierarchy.validate_hierarchy();

-- Aggregate hierarchy size by department.
SELECT
    department_name,
    COUNT(*) AS employee_count,
    AVG(hierarchy_level)::NUMERIC(10, 2) AS average_depth,
    MAX(hierarchy_level) AS maximum_depth
FROM hierarchy.employee_hierarchy_report
GROUP BY department_name
ORDER BY employee_count DESC;

-- ------------------------------------------------------------
-- 12. Transactional hierarchy update
-- ------------------------------------------------------------
--
-- Moving employee 10 from employee 7 to employee 6 is valid.
-- If any constraint or trigger rejects the change, the entire
-- transaction is rolled back.
-- ------------------------------------------------------------

SAVEPOINT before_hierarchy_change;

UPDATE hierarchy.employee_relationship
SET
    manager_id = 6,
    child_position = 'RIGHT'
WHERE employee_id = 10;

SELECT *
FROM hierarchy.find_lca(10, 6);

ROLLBACK TO SAVEPOINT before_hierarchy_change;

-- ------------------------------------------------------------
-- 13. Demonstrate invalid relationships safely
-- ------------------------------------------------------------

SAVEPOINT before_invalid_cycle;

-- Employee 1 cannot become a subordinate of employee 8 because
-- this would create a cycle.
DO $$
BEGIN
    BEGIN
        UPDATE hierarchy.employee_relationship
        SET
            manager_id = 8,
            child_position = 'LEFT'
        WHERE employee_id = 1;

        RAISE EXCEPTION
            'Expected cycle validation to reject this update.';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected hierarchy validation failure: %',
                SQLERRM;
    END;
END;
$$;

ROLLBACK TO SAVEPOINT before_invalid_cycle;

-- A missing target produces no LCA row.
SELECT *
FROM hierarchy.find_lca(8, 999);

-- A second root is rejected.
SAVEPOINT before_second_root;

DO $$
BEGIN
    BEGIN
        INSERT INTO hierarchy.employee_relationship (
            employee_id,
            manager_id,
            child_position
        )
        VALUES (10, NULL, NULL);

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected root validation failure: %',
                SQLERRM;
    END;
END;
$$;

ROLLBACK TO SAVEPOINT before_second_root;

-- ------------------------------------------------------------
-- 14. Final state and audit report
-- ------------------------------------------------------------

SELECT
    employee_id,
    employee_name,
    manager_name,
    hierarchy_level,
    employee_path
FROM hierarchy.employee_hierarchy_report
ORDER BY employee_id;

SELECT *
FROM hierarchy.hierarchy_audit
ORDER BY audit_id;

COMMIT;
