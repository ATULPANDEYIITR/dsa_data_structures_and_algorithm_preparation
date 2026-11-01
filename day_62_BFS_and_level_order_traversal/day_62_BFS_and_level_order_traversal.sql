BEGIN;

CREATE SCHEMA IF NOT EXISTS bfs_learning;

SET search_path TO bfs_learning, public;

-- Remove dependent objects so the script can be executed repeatedly.
DROP VIEW IF EXISTS department_level_statistics CASCADE;
DROP VIEW IF EXISTS department_hierarchy_report CASCADE;
DROP FUNCTION IF EXISTS calculate_level_metrics(BIGINT) CASCADE;
DROP FUNCTION IF EXISTS get_hierarchy_levels(BIGINT) CASCADE;
DROP FUNCTION IF EXISTS validate_department_parent() CASCADE;
DROP FUNCTION IF EXISTS update_department_timestamp() CASCADE;
DROP TABLE IF EXISTS traversal_audit CASCADE;
DROP TABLE IF EXISTS traversal_results CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE departments (
    department_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,

    parent_department_id BIGINT,
    department_code VARCHAR(30) NOT NULL,
    department_name VARCHAR(150) NOT NULL,
    workload INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_or_zero_workload
        CHECK (workload >= 0),

    CONSTRAINT department_code_unique
        UNIQUE (organization_id, department_code),

    CONSTRAINT department_parent_fk
        FOREIGN KEY (parent_department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT,

    CONSTRAINT no_direct_self_parent
        CHECK (
            parent_department_id IS NULL
            OR parent_department_id <> department_id
        ),

    CONSTRAINT department_unique_identity
        UNIQUE (department_id, organization_id)
);

-- Parent lookups are fundamental to recursive hierarchy traversal.
CREATE INDEX idx_departments_parent
    ON departments(parent_department_id);

CREATE INDEX idx_departments_organization
    ON departments(organization_id);

CREATE TABLE traversal_results (
    traversal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,

    traversal_type VARCHAR(30) NOT NULL
        CHECK (
            traversal_type IN (
                'LEVEL_ORDER',
                'ZIGZAG',
                'BOTTOM_UP'
            )
        ),

    traversal_status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED'
        CHECK (
            traversal_status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        ),

    total_nodes INTEGER NOT NULL DEFAULT 0
        CHECK (total_nodes >= 0),

    maximum_depth INTEGER NOT NULL DEFAULT 0
        CHECK (maximum_depth >= 0),

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CHECK (
        completed_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE TABLE traversal_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    traversal_id BIGINT NOT NULL
        REFERENCES traversal_results(traversal_id)
        ON DELETE CASCADE,

    department_id BIGINT NOT NULL
        REFERENCES departments(department_id)
        ON DELETE RESTRICT,

    level_depth INTEGER NOT NULL CHECK (level_depth >= 0),
    position_in_level INTEGER NOT NULL
        CHECK (position_in_level >= 0),

    processed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (traversal_id, department_id),
    UNIQUE (traversal_id, level_depth, position_in_level)
);

CREATE INDEX idx_traversal_audit_level
    ON traversal_audit(traversal_id, level_depth, position_in_level);

CREATE OR REPLACE FUNCTION update_department_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER departments_update_timestamp
BEFORE UPDATE ON departments
FOR EACH ROW
EXECUTE FUNCTION update_department_timestamp();

-- A parent must belong to the same organization.
-- Recursive checking prevents indirect cycles.
CREATE OR REPLACE FUNCTION validate_department_parent()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_org BIGINT;
    creates_cycle BOOLEAN;
BEGIN
    IF NEW.parent_department_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT organization_id
    INTO parent_org
    FROM departments
    WHERE department_id = NEW.parent_department_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Parent department % does not exist',
            NEW.parent_department_id;
    END IF;

    IF parent_org <> NEW.organization_id THEN
        RAISE EXCEPTION
            'Parent department must belong to the same organization';
    END IF;

    IF NEW.department_id IS NOT NULL THEN
        WITH RECURSIVE descendants(id) AS (
            SELECT department_id
            FROM departments
            WHERE parent_department_id = NEW.department_id

            UNION

            SELECT d.department_id
            FROM departments d
            JOIN descendants x
                ON d.parent_department_id = x.id
        )
        SELECT EXISTS (
            SELECT 1
            FROM descendants
            WHERE id = NEW.parent_department_id
        )
        INTO creates_cycle;

        IF creates_cycle THEN
            RAISE EXCEPTION
                'Hierarchy cycle detected for department %',
                NEW.department_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER departments_parent_validation
BEFORE INSERT OR UPDATE OF parent_department_id, organization_id
ON departments
FOR EACH ROW
EXECUTE FUNCTION validate_department_parent();

INSERT INTO organizations (organization_name)
VALUES
    ('Technology Enterprise'),
    ('Operations Enterprise');

-- Organization 1: an eight-node hierarchy.
INSERT INTO departments (
    organization_id,
    parent_department_id,
    department_code,
    department_name,
    workload
)
VALUES
    (1, NULL, 'D001', 'Executive Office', 100);

INSERT INTO departments (
    organization_id,
    parent_department_id,
    department_code,
    department_name,
    workload
)
VALUES
    (1, 1, 'D002', 'Technology', 250),
    (1, 1, 'D003', 'Operations', 180),
    (1, 1, 'D004', 'Security', 220);

INSERT INTO departments (
    organization_id,
    parent_department_id,
    department_code,
    department_name,
    workload
)
VALUES
    (1, 2, 'D005', 'Engineering', 300),
    (1, 2, 'D006', 'Analytics', 150),
    (1, 3, 'D007', 'Infrastructure', 200),
    (1, 3, 'D008', 'Support', 90);

-- Organization 2: independent hierarchy.
INSERT INTO departments (
    organization_id,
    parent_department_id,
    department_code,
    department_name,
    workload
)
VALUES
    (2, NULL, 'O001', 'Operations Headquarters', 120);

INSERT INTO departments (
    organization_id,
    parent_department_id,
    department_code,
    department_name,
    workload
)
VALUES
    (2, 9, 'O002', 'Field Operations', 180),
    (2, 9, 'O003', 'Planning', 140);

-- Recursive CTE: identify hierarchy depth and ordering.
CREATE OR REPLACE FUNCTION get_hierarchy_levels(
    p_organization_id BIGINT
)
RETURNS TABLE (
    department_id BIGINT,
    department_name VARCHAR,
    parent_department_id BIGINT,
    level_depth INTEGER,
    workload INTEGER,
    path BIGINT[]
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM organizations
        WHERE organization_id = p_organization_id
    ) THEN
        RAISE EXCEPTION
            'Organization % does not exist',
            p_organization_id;
    END IF;

    RETURN QUERY
    WITH RECURSIVE hierarchy AS (
        SELECT
            d.department_id,
            d.department_name,
            d.parent_department_id,
            0 AS level_depth,
            d.workload,
            ARRAY[d.department_id]::BIGINT[] AS path
        FROM departments d
        WHERE d.organization_id = p_organization_id
          AND d.parent_department_id IS NULL

        UNION ALL

        SELECT
            child.department_id,
            child.department_name,
            child.parent_department_id,
            parent.level_depth + 1,
            child.workload,
            parent.path || child.department_id
        FROM departments child
        JOIN hierarchy parent
            ON child.parent_department_id = parent.department_id
        WHERE child.organization_id = p_organization_id
          AND NOT child.department_id = ANY(parent.path)
    )
    SELECT
        h.department_id,
        h.department_name,
        h.parent_department_id,
        h.level_depth,
        h.workload,
        h.path
    FROM hierarchy h
    ORDER BY h.level_depth, h.path;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_level_metrics(
    p_organization_id BIGINT
)
RETURNS TABLE (
    level_depth INTEGER,
    department_count BIGINT,
    total_workload BIGINT,
    average_workload NUMERIC,
    minimum_workload INTEGER,
    maximum_workload INTEGER
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        h.level_depth,
        COUNT(*)::BIGINT,
        SUM(h.workload)::BIGINT,
        ROUND(AVG(h.workload), 2),
        MIN(h.workload),
        MAX(h.workload)
    FROM get_hierarchy_levels(p_organization_id) h
    GROUP BY h.level_depth
    ORDER BY h.level_depth;
$$;

CREATE OR REPLACE VIEW department_hierarchy_report AS
WITH RECURSIVE hierarchy AS (
    SELECT
        d.department_id,
        d.organization_id,
        d.department_name,
        d.department_code,
        d.parent_department_id,
        0 AS level_depth,
        ARRAY[d.department_id]::BIGINT[] AS path
    FROM departments d
    WHERE d.parent_department_id IS NULL

    UNION ALL

    SELECT
        child.department_id,
        child.organization_id,
        child.department_name,
        child.department_code,
        child.parent_department_id,
        parent.level_depth + 1,
        parent.path || child.department_id
    FROM departments child
    JOIN hierarchy parent
        ON child.parent_department_id = parent.department_id
    WHERE child.organization_id = parent.organization_id
      AND NOT child.department_id = ANY(parent.path)
)
SELECT
    o.organization_name,
    h.department_id,
    h.department_code,
    h.department_name,
    h.parent_department_id,
    h.level_depth,
    d.workload,
    h.path
FROM hierarchy h
JOIN organizations o
    ON o.organization_id = h.organization_id
JOIN departments d
    ON d.department_id = h.department_id;

CREATE OR REPLACE VIEW department_level_statistics AS
SELECT
    organization_id,
    level_depth,
    COUNT(*) AS department_count,
    SUM(workload) AS total_workload,
    ROUND(AVG(workload), 2) AS average_workload,
    MIN(workload) AS minimum_workload,
    MAX(workload) AS maximum_workload
FROM (
    SELECT
        d.organization_id,
        h.level_depth,
        d.workload
    FROM departments d
    JOIN LATERAL get_hierarchy_levels(d.organization_id) h
        ON h.department_id = d.department_id
) hierarchy_data
GROUP BY organization_id, level_depth;

-- Transactional traversal execution.
CREATE OR REPLACE PROCEDURE execute_bfs_traversal(
    p_organization_id BIGINT,
    p_traversal_type VARCHAR DEFAULT 'LEVEL_ORDER'
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_traversal_id BIGINT;
    maximum_level INTEGER;
    total_departments INTEGER;
BEGIN
    IF p_traversal_type NOT IN (
        'LEVEL_ORDER',
        'ZIGZAG',
        'BOTTOM_UP'
    ) THEN
        RAISE EXCEPTION
            'Unsupported traversal type: %',
            p_traversal_type;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM organizations
        WHERE organization_id = p_organization_id
    ) THEN
        RAISE EXCEPTION
            'Organization does not exist';
    END IF;

    INSERT INTO traversal_results (
        organization_id,
        traversal_type,
        traversal_status
    )
    VALUES (
        p_organization_id,
        p_traversal_type,
        'PROCESSING'
    )
    RETURNING traversal_id INTO new_traversal_id;

    WITH hierarchy AS (
        SELECT *
        FROM get_hierarchy_levels(p_organization_id)
    ),
    ordered_nodes AS (
        SELECT
            h.department_id,
            h.level_depth,
            ROW_NUMBER() OVER (
                PARTITION BY h.level_depth
                ORDER BY
                    CASE
                        WHEN p_traversal_type = 'ZIGZAG'
                         AND h.level_depth % 2 = 1
                        THEN h.path[1]
                    END NULLS FIRST,
                    CASE
                        WHEN p_traversal_type = 'ZIGZAG'
                         AND h.level_depth % 2 = 1
                        THEN h.path
                    END DESC NULLS LAST,
                    CASE
                        WHEN p_traversal_type <> 'ZIGZAG'
                          OR h.level_depth % 2 = 0
                        THEN h.path
                    END ASC NULLS LAST
            ) - 1 AS position_in_level
        FROM hierarchy h
    )
    INSERT INTO traversal_audit (
        traversal_id,
        department_id,
        level_depth,
        position_in_level
    )
    SELECT
        new_traversal_id,
        department_id,
        level_depth,
        position_in_level
    FROM ordered_nodes;

    SELECT
        COALESCE(MAX(level_depth) + 1, 0),
        COUNT(*)
    INTO maximum_level, total_departments
    FROM get_hierarchy_levels(p_organization_id);

    UPDATE traversal_results
    SET
        traversal_status = 'COMPLETED',
        total_nodes = total_departments,
        maximum_depth = maximum_level,
        completed_at = CURRENT_TIMESTAMP
    WHERE traversal_id = new_traversal_id;
END;
$$;

-- Example 1: retrieve the complete hierarchy.
SELECT *
FROM department_hierarchy_report
WHERE organization_name = 'Technology Enterprise'
ORDER BY level_depth, path;

-- Example 2: calculate level statistics.
SELECT *
FROM calculate_level_metrics(1);

-- Example 3: run different traversal modes.
CALL execute_bfs_traversal(1, 'LEVEL_ORDER');
CALL execute_bfs_traversal(1, 'ZIGZAG');
CALL execute_bfs_traversal(1, 'BOTTOM_UP');

-- Example 4: retrieve recorded traversal positions.
SELECT
    tr.traversal_id,
    tr.traversal_type,
    tr.traversal_status,
    ta.level_depth,
    ta.position_in_level,
    d.department_name
FROM traversal_results tr
JOIN traversal_audit ta
    ON ta.traversal_id = tr.traversal_id
JOIN departments d
    ON d.department_id = ta.department_id
WHERE tr.organization_id = 1
ORDER BY
    tr.traversal_id,
    CASE
        WHEN tr.traversal_type = 'BOTTOM_UP'
        THEN -ta.level_depth
        ELSE ta.level_depth
    END,
    ta.position_in_level;

-- Example 5: aggregate workload at each depth.
SELECT
    o.organization_name,
    s.level_depth,
    s.department_count,
    s.total_workload,
    s.average_workload
FROM department_level_statistics s
JOIN organizations o
    ON o.organization_id = s.organization_id
ORDER BY o.organization_name, s.level_depth;

-- Example 6: find high-workload departments.
SELECT
    department_name,
    workload
FROM departments
WHERE organization_id = 1
  AND workload >= 200
ORDER BY workload DESC;

-- Example 7: validate hierarchy depth.
SELECT
    organization_name,
    MAX(level_depth) AS maximum_depth,
    COUNT(*) AS total_departments
FROM department_hierarchy_report
GROUP BY organization_name;

-- Example 8: demonstrate empty organization traversal.
CALL execute_bfs_traversal(2, 'LEVEL_ORDER');

-- Example 9: verify that invalid workload is rejected.
DO $$
BEGIN
    BEGIN
        INSERT INTO departments (
            organization_id,
            department_code,
            department_name,
            workload
        )
        VALUES (1, 'INVALID', 'Invalid Department', -10);

        RAISE EXCEPTION
            'Negative workload unexpectedly accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Validation successful: negative workload rejected';
    END;
END;
$$;

-- Example 10: verify that an indirect hierarchy cycle is rejected.
DO $$
BEGIN
    BEGIN
        UPDATE departments
        SET parent_department_id = 5
        WHERE department_id = 1;

        RAISE EXCEPTION
            'Circular hierarchy unexpectedly accepted';

    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM LIKE 'Circular hierarchy unexpectedly accepted' THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Validation successful: circular hierarchy rejected';
    END;
END;
$$;

-- Final traversal summary.
SELECT
    traversal_id,
    organization_id,
    traversal_type,
    traversal_status,
    total_nodes,
    maximum_depth,
    started_at,
    completed_at
FROM traversal_results
ORDER BY traversal_id;

COMMIT;
