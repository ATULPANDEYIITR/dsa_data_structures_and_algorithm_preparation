-- ============================================================
-- TOP-K SELECTION AND ANALYTICS DATABASE
-- PostgreSQL 15+
--
-- Covers:
--   1. Kth largest and smallest
--   2. Top-K frequent values
--   3. K closest values
--   4. Ranking and tie-breaking
--   5. Dataset management
--   6. Request validation and execution auditing
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS topk;

CREATE TABLE IF NOT EXISTS topk.datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topk.dataset_values (
    value_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES topk.datasets(dataset_id)
        ON DELETE CASCADE,
    value INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (dataset_id, position)
);

CREATE INDEX IF NOT EXISTS idx_dataset_values_dataset_value
    ON topk.dataset_values(dataset_id, value);

CREATE INDEX IF NOT EXISTS idx_dataset_values_dataset_position
    ON topk.dataset_values(dataset_id, position);

CREATE TABLE IF NOT EXISTS topk.selection_requests (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES topk.datasets(dataset_id),
    operation VARCHAR(30) NOT NULL
        CHECK (operation IN (
            'KTH_LARGEST',
            'KTH_SMALLEST',
            'TOP_K_FREQUENT',
            'K_CLOSEST'
        )),
    k INTEGER NOT NULL CHECK (k >= 0),
    target_value INTEGER,
    request_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (request_status IN (
            'PENDING',
            'RUNNING',
            'COMPLETED',
            'FAILED'
        )),
    result_values INTEGER[],
    error_message TEXT,
    execution_time_ms NUMERIC(14, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CHECK (
        (operation = 'K_CLOSEST' AND target_value IS NOT NULL)
        OR
        (operation <> 'K_CLOSEST' AND target_value IS NULL)
    ),

    CHECK (
        request_status <> 'COMPLETED'
        OR completed_at IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_selection_requests_status
    ON topk.selection_requests(request_status, created_at DESC);

CREATE TABLE IF NOT EXISTS topk.selection_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id BIGINT NOT NULL
        REFERENCES topk.selection_requests(request_id)
        ON DELETE CASCADE,
    event_type VARCHAR(30) NOT NULL,
    event_details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_selection_audit_request_time
    ON topk.selection_audit(request_id, occurred_at DESC);


-- ------------------------------------------------------------
-- Dataset creation and sample values
-- ------------------------------------------------------------

INSERT INTO topk.datasets (dataset_name, description)
VALUES
    ('basic_selection', 'General integer selection dataset'),
    ('frequency_analysis', 'Frequency ranking dataset'),
    ('closest_analysis', 'Sorted values for proximity selection'),
    ('duplicate_analysis', 'Duplicate-heavy selection dataset')
ON CONFLICT (dataset_name) DO NOTHING;


INSERT INTO topk.dataset_values (dataset_id, value, position)
SELECT d.dataset_id, v.value, v.position
FROM topk.datasets d
JOIN (
    VALUES
        ('basic_selection', 3, 0),
        ('basic_selection', 2, 1),
        ('basic_selection', 1, 2),
        ('basic_selection', 5, 3),
        ('basic_selection', 6, 4),
        ('basic_selection', 4, 5),

        ('frequency_analysis', 1, 0),
        ('frequency_analysis', 1, 1),
        ('frequency_analysis', 1, 2),
        ('frequency_analysis', 2, 3),
        ('frequency_analysis', 2, 4),
        ('frequency_analysis', 3, 5),
        ('frequency_analysis', 4, 6),
        ('frequency_analysis', 4, 7),
        ('frequency_analysis', 4, 8),
        ('frequency_analysis', 4, 9),

        ('closest_analysis', 1, 0),
        ('closest_analysis', 2, 1),
        ('closest_analysis', 3, 2),
        ('closest_analysis', 4, 3),
        ('closest_analysis', 5, 4),

        ('duplicate_analysis', 5, 0),
        ('duplicate_analysis', 5, 1),
        ('duplicate_analysis', 5, 2),
        ('duplicate_analysis', 2, 3),
        ('duplicate_analysis', 2, 4),
        ('duplicate_analysis', 8, 5)
) AS v(dataset_name, value, position)
ON v.dataset_name = d.dataset_name
ON CONFLICT (dataset_id, position) DO NOTHING;


-- ------------------------------------------------------------
-- Validation helper
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION topk.validate_selection_request(
    p_dataset_id BIGINT,
    p_operation VARCHAR,
    p_k INTEGER,
    p_target INTEGER DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
    v_distinct_count INTEGER;
    v_is_sorted BOOLEAN;
BEGIN
    SELECT
        COUNT(*),
        COUNT(DISTINCT value)
    INTO v_count, v_distinct_count
    FROM topk.dataset_values
    WHERE dataset_id = p_dataset_id;

    IF NOT FOUND OR v_count = 0 THEN
        RAISE EXCEPTION 'Dataset is empty or unavailable';
    END IF;

    IF p_operation NOT IN (
        'KTH_LARGEST',
        'KTH_SMALLEST',
        'TOP_K_FREQUENT',
        'K_CLOSEST'
    ) THEN
        RAISE EXCEPTION 'Unsupported operation: %', p_operation;
    END IF;

    IF p_k < 0 THEN
        RAISE EXCEPTION 'k cannot be negative';
    END IF;

    IF p_operation IN ('KTH_LARGEST', 'KTH_SMALLEST')
       AND p_k NOT BETWEEN 1 AND v_count THEN
        RAISE EXCEPTION 'k must be between 1 and %', v_count;
    END IF;

    IF p_operation = 'TOP_K_FREQUENT'
       AND p_k > v_distinct_count THEN
        RAISE EXCEPTION 'k exceeds distinct value count';
    END IF;

    IF p_operation = 'K_CLOSEST' THEN
        IF p_k > v_count THEN
            RAISE EXCEPTION 'k exceeds dataset size';
        END IF;

        IF p_target IS NULL THEN
            RAISE EXCEPTION 'Target is required';
        END IF;

        SELECT NOT EXISTS (
            SELECT 1
            FROM topk.dataset_values a
            JOIN topk.dataset_values b
              ON b.dataset_id = a.dataset_id
             AND b.position = a.position + 1
            WHERE a.dataset_id = p_dataset_id
              AND a.value > b.value
        )
        INTO v_is_sorted;

        IF NOT v_is_sorted THEN
            RAISE EXCEPTION 'K_CLOSEST requires sorted input';
        END IF;
    END IF;

    RETURN TRUE;
END;
$$;


-- ------------------------------------------------------------
-- Selection execution function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION topk.execute_selection(
    p_dataset_id BIGINT,
    p_operation VARCHAR,
    p_k INTEGER,
    p_target INTEGER DEFAULT NULL
)
RETURNS INTEGER[]
LANGUAGE plpgsql
AS $$
DECLARE
    v_result INTEGER[];
BEGIN
    PERFORM topk.validate_selection_request(
        p_dataset_id,
        p_operation,
        p_k,
        p_target
    );

    IF p_operation = 'KTH_LARGEST' THEN
        SELECT ARRAY_AGG(value ORDER BY value DESC)
        INTO v_result
        FROM (
            SELECT value
            FROM topk.dataset_values
            WHERE dataset_id = p_dataset_id
            ORDER BY value DESC
            OFFSET p_k - 1
            LIMIT 1
        ) selected;

    ELSIF p_operation = 'KTH_SMALLEST' THEN
        SELECT ARRAY_AGG(value ORDER BY value)
        INTO v_result
        FROM (
            SELECT value
            FROM topk.dataset_values
            WHERE dataset_id = p_dataset_id
            ORDER BY value
            OFFSET p_k - 1
            LIMIT 1
        ) selected;

    ELSIF p_operation = 'TOP_K_FREQUENT' THEN
        WITH frequencies AS (
            SELECT
                value,
                COUNT(*) AS frequency
            FROM topk.dataset_values
            WHERE dataset_id = p_dataset_id
            GROUP BY value
        ),
        ranked AS (
            SELECT
                value,
                frequency,
                ROW_NUMBER() OVER (
                    ORDER BY frequency DESC, value ASC
                ) AS ranking
            FROM frequencies
        )
        SELECT COALESCE(
            ARRAY_AGG(value ORDER BY ranking),
            ARRAY[]::INTEGER[]
        )
        INTO v_result
        FROM ranked
        WHERE ranking <= p_k;

    ELSIF p_operation = 'K_CLOSEST' THEN
        SELECT COALESCE(
            ARRAY_AGG(value ORDER BY value),
            ARRAY[]::INTEGER[]
        )
        INTO v_result
        FROM (
            SELECT value
            FROM topk.dataset_values
            WHERE dataset_id = p_dataset_id
            ORDER BY ABS(value::BIGINT - p_target), value
            LIMIT p_k
        ) selected;

    END IF;

    RETURN COALESCE(v_result, ARRAY[]::INTEGER[]);
END;
$$;


-- ------------------------------------------------------------
-- Request creation procedure
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE topk.submit_selection_request(
    p_dataset_id BIGINT,
    p_operation VARCHAR,
    p_k INTEGER,
    p_target INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_request_id BIGINT;
    v_started TIMESTAMPTZ;
    v_result INTEGER[];
BEGIN
    PERFORM topk.validate_selection_request(
        p_dataset_id,
        p_operation,
        p_k,
        p_target
    );

    INSERT INTO topk.selection_requests (
        dataset_id,
        operation,
        k,
        target_value,
        request_status
    )
    VALUES (
        p_dataset_id,
        p_operation,
        p_k,
        p_target,
        'RUNNING'
    )
    RETURNING request_id INTO v_request_id;

    v_started := clock_timestamp();

    INSERT INTO topk.selection_audit (
        request_id,
        event_type,
        event_details
    )
    VALUES (
        v_request_id,
        'REQUEST_STARTED',
        jsonb_build_object(
            'operation', p_operation,
            'k', p_k
        )
    );

    v_result := topk.execute_selection(
        p_dataset_id,
        p_operation,
        p_k,
        p_target
    );

    UPDATE topk.selection_requests
    SET
        request_status = 'COMPLETED',
        result_values = v_result,
        execution_time_ms =
            EXTRACT(EPOCH FROM clock_timestamp() - v_started) * 1000,
        completed_at = clock_timestamp()
    WHERE request_id = v_request_id;

    INSERT INTO topk.selection_audit (
        request_id,
        event_type,
        event_details
    )
    VALUES (
        v_request_id,
        'REQUEST_COMPLETED',
        jsonb_build_object('result', v_result)
    );

EXCEPTION
    WHEN OTHERS THEN
        IF v_request_id IS NOT NULL THEN
            UPDATE topk.selection_requests
            SET
                request_status = 'FAILED',
                error_message = SQLERRM,
                completed_at = clock_timestamp()
            WHERE request_id = v_request_id;

            INSERT INTO topk.selection_audit (
                request_id,
                event_type,
                event_details
            )
            VALUES (
                v_request_id,
                'REQUEST_FAILED',
                jsonb_build_object('error', SQLERRM)
            );
        END IF;

        RAISE;
END;
$$;


-- ------------------------------------------------------------
-- Reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW topk.selection_report AS
SELECT
    r.request_id,
    d.dataset_name,
    r.operation,
    r.k,
    r.target_value,
    r.request_status,
    r.result_values,
    r.error_message,
    r.execution_time_ms,
    r.created_at,
    r.completed_at
FROM topk.selection_requests r
JOIN topk.datasets d
    ON d.dataset_id = r.dataset_id;


-- ------------------------------------------------------------
-- Sample request execution
-- ------------------------------------------------------------

DO $$
DECLARE
    v_basic BIGINT;
    v_frequency BIGINT;
    v_closest BIGINT;
    v_duplicate BIGINT;
BEGIN
    SELECT dataset_id INTO v_basic
    FROM topk.datasets
    WHERE dataset_name = 'basic_selection';

    SELECT dataset_id INTO v_frequency
    FROM topk.datasets
    WHERE dataset_name = 'frequency_analysis';

    SELECT dataset_id INTO v_closest
    FROM topk.datasets
    WHERE dataset_name = 'closest_analysis';

    SELECT dataset_id INTO v_duplicate
    FROM topk.datasets
    WHERE dataset_name = 'duplicate_analysis';

    CALL topk.submit_selection_request(
        v_basic, 'KTH_LARGEST', 2
    );

    CALL topk.submit_selection_request(
        v_basic, 'KTH_SMALLEST', 3
    );

    CALL topk.submit_selection_request(
        v_frequency, 'TOP_K_FREQUENT', 2
    );

    CALL topk.submit_selection_request(
        v_closest, 'K_CLOSEST', 4, 3
    );

    CALL topk.submit_selection_request(
        v_duplicate, 'KTH_LARGEST', 3
    );
END;
$$;


-- ------------------------------------------------------------
-- Retrieval query
-- ------------------------------------------------------------

SELECT
    dataset_name,
    value,
    position
FROM topk.dataset_values v
JOIN topk.datasets d USING (dataset_id)
WHERE d.dataset_name = 'basic_selection'
ORDER BY position;


-- ------------------------------------------------------------
-- Validation query: detect duplicate values
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    v.value,
    COUNT(*) AS occurrences
FROM topk.dataset_values v
JOIN topk.datasets d USING (dataset_id)
GROUP BY d.dataset_name, v.value
HAVING COUNT(*) > 1
ORDER BY d.dataset_name, occurrences DESC;


-- ------------------------------------------------------------
-- Ranking query: top frequent values
-- ------------------------------------------------------------

WITH frequency_data AS (
    SELECT
        value,
        COUNT(*) AS frequency
    FROM topk.dataset_values
    WHERE dataset_id = (
        SELECT dataset_id
        FROM topk.datasets
        WHERE dataset_name = 'frequency_analysis'
    )
    GROUP BY value
),
ranked_values AS (
    SELECT
        value,
        frequency,
        DENSE_RANK() OVER (
            ORDER BY frequency DESC
        ) AS frequency_rank
    FROM frequency_data
)
SELECT *
FROM ranked_values
WHERE frequency_rank <= 2
ORDER BY frequency_rank, value;


-- ------------------------------------------------------------
-- Aggregation query
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    COUNT(*) AS total_values,
    COUNT(DISTINCT v.value) AS distinct_values,
    MIN(v.value) AS minimum_value,
    MAX(v.value) AS maximum_value,
    AVG(v.value)::NUMERIC(12, 2) AS average_value
FROM topk.datasets d
JOIN topk.dataset_values v USING (dataset_id)
GROUP BY d.dataset_name
ORDER BY d.dataset_name;


-- ------------------------------------------------------------
-- Eligibility evaluation
-- ------------------------------------------------------------

SELECT
    r.request_id,
    r.operation,
    r.k,
    CASE
        WHEN r.operation IN ('KTH_LARGEST', 'KTH_SMALLEST')
             AND r.k BETWEEN 1 AND counts.total_count
            THEN TRUE
        WHEN r.operation = 'TOP_K_FREQUENT'
             AND r.k <= counts.distinct_count
            THEN TRUE
        WHEN r.operation = 'K_CLOSEST'
             AND r.k <= counts.total_count
             AND r.target_value IS NOT NULL
            THEN TRUE
        ELSE FALSE
    END AS structurally_eligible
FROM topk.selection_requests r
CROSS JOIN LATERAL (
    SELECT
        COUNT(*) AS total_count,
        COUNT(DISTINCT value) AS distinct_count
    FROM topk.dataset_values v
    WHERE v.dataset_id = r.dataset_id
) counts;


-- ------------------------------------------------------------
-- Execution report
-- ------------------------------------------------------------

SELECT
    operation,
    request_status,
    COUNT(*) AS request_count,
    ROUND(AVG(execution_time_ms), 4) AS average_ms
FROM topk.selection_requests
GROUP BY operation, request_status
ORDER BY operation, request_status;


-- ------------------------------------------------------------
-- Audit retrieval
-- ------------------------------------------------------------

SELECT
    a.audit_id,
    a.request_id,
    a.event_type,
    a.event_details,
    a.occurred_at
FROM topk.selection_audit a
ORDER BY a.occurred_at DESC;


COMMIT;

-- ============================================================
-- Operational notes:
--
-- 1. Ranking queries use SQL sorting and window functions.
-- 2. PostgreSQL does not automatically turn ORDER BY LIMIT
--    into a bounded application-level heap.
-- 3. For repeated high-volume requests, indexes, statistics,
--    dataset cardinality, and query plans must be evaluated.
-- 4. ABS(value::BIGINT - target) avoids integer subtraction
--    overflow for INTEGER input values.
-- 5. Failed procedure calls roll back their statement-level
--    effects when the exception is re-raised. A caller requiring
--    durable failure auditing should record failures in a
--    separate transaction.
-- ============================================================
