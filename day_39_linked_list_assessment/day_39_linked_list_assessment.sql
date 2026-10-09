-- PostgreSQL 15+ compatible linked-list assessment laboratory.
-- The schema records assessment runs, linked-list nodes, and observed
-- outcomes. Pointer manipulation remains an application responsibility;
-- SQL constraints enforce ownership and structural integrity of the records.

BEGIN;

DROP VIEW IF EXISTS linked_list_assessment_summary;
DROP TABLE IF EXISTS assessment_result;
DROP TABLE IF EXISTS list_node;
DROP TABLE IF EXISTS assessment_case;

CREATE TABLE assessment_case (
    case_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    problem_name TEXT NOT NULL UNIQUE,
    difficulty TEXT NOT NULL
        CHECK (difficulty IN ('Easy', 'Medium', 'Difficult')),
    technique TEXT NOT NULL,
    expected_complexity TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE list_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_id BIGINT NOT NULL REFERENCES assessment_case(case_id)
        ON DELETE CASCADE,
    list_label TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 0),
    node_value INTEGER NOT NULL,
    next_position INTEGER,
    CONSTRAINT unique_list_position UNIQUE (case_id, list_label, position),
    CONSTRAINT valid_next_position CHECK (
        next_position IS NULL OR next_position >= 0
    ),
    CONSTRAINT next_position_not_self CHECK (
        next_position IS NULL OR next_position <> position
    )
);

CREATE INDEX idx_list_node_traversal
    ON list_node (case_id, list_label, position);

CREATE TABLE assessment_result (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_id BIGINT NOT NULL REFERENCES assessment_case(case_id)
        ON DELETE CASCADE,
    run_label TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    elapsed_microseconds BIGINT CHECK (elapsed_microseconds >= 0),
    observed_output JSONB NOT NULL DEFAULT '{}'::jsonb,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT failure_reason_consistency CHECK (
        (passed AND failure_reason IS NULL)
        OR (NOT passed AND failure_reason IS NOT NULL)
    )
);

CREATE INDEX idx_result_case_created
    ON assessment_result (case_id, created_at DESC);

INSERT INTO assessment_case
    (problem_name, difficulty, technique, expected_complexity, description)
VALUES
    ('Reverse a Linked List', 'Easy', 'Iterative pointer reversal',
     'O(n) time, O(1) auxiliary space',
     'Reverse every next pointer without allocating replacement nodes.'),
    ('Detect a Cycle', 'Easy', 'Floyd tortoise and hare',
     'O(n) time, O(1) auxiliary space',
     'Detect a repeated node reachable through next pointers.'),
    ('Merge Two Sorted Lists', 'Easy', 'Two-pointer merge',
     'O(n+m) time, O(1) auxiliary space',
     'Merge two sorted, disjoint linked lists.'),
    ('Remove Nth Node From End', 'Medium', 'Two-pointer gap',
     'O(n) time, O(1) auxiliary space',
     'Remove the Nth node from the end and validate N.'),
    ('Intersection of Two Lists', 'Medium', 'Pointer switching',
     'O(n+m) time, O(1) auxiliary space',
     'Find a shared node by identity rather than equal value.'),
    ('Palindrome Linked List', 'Medium', 'Reverse and compare halves',
     'O(n) time, O(1) auxiliary space',
     'Compare values while restoring the original list.'),
    ('Reorder List', 'Medium', 'Split, reverse, interleave',
     'O(n) time, O(1) auxiliary space',
     'Interleave nodes from the start and end of the list.'),
    ('Merge K Sorted Lists', 'Difficult', 'Min-heap',
     'O(N log K) time, O(K) heap space',
     'Merge K sorted disjoint lists in ascending order.');

-- Record the node layouts used by the sorted two-list merge example.
INSERT INTO list_node
    (case_id, list_label, position, node_value, next_position)
SELECT c.case_id, sample.list_label, sample.position,
       sample.node_value, sample.next_position
FROM assessment_case c
CROSS JOIN (
    VALUES
        ('left', 0, 1, 1),
        ('left', 1, 3, 2),
        ('left', 2, 5, NULL),
        ('right', 0, 2, 1),
        ('right', 1, 4, 2),
        ('right', 2, 6, NULL)
) AS sample(list_label, position, node_value, next_position)
WHERE c.problem_name = 'Merge Two Sorted Lists';

-- Record the values for a valid and an invalid removal request.
INSERT INTO assessment_result
    (case_id, run_label, passed, elapsed_microseconds, observed_output,
     failure_reason)
SELECT case_id, 'remove-n-valid', TRUE, 14,
       '{"input":[1,2,3,4,5],"n":2,"output":[1,2,3,5]}'::jsonb,
       NULL
FROM assessment_case
WHERE problem_name = 'Remove Nth Node From End';

INSERT INTO assessment_result
    (case_id, run_label, passed, elapsed_microseconds, observed_output,
     failure_reason)
SELECT case_id, 'remove-n-too-large', FALSE, 8,
       '{"input":[1,2],"n":3}'::jsonb,
       'Requested position exceeds list length.'
FROM assessment_case
WHERE problem_name = 'Remove Nth Node From End';

INSERT INTO assessment_result
    (case_id, run_label, passed, elapsed_microseconds, observed_output,
     failure_reason)
SELECT case_id, 'merge-k-equal-values', TRUE, 29,
       '{"input_lists":[[1,3],[1,2]],"output":[1,1,2,3]}'::jsonb,
       NULL
FROM assessment_case
WHERE problem_name = 'Merge K Sorted Lists';

CREATE VIEW linked_list_assessment_summary AS
SELECT
    c.case_id,
    c.problem_name,
    c.difficulty,
    c.technique,
    c.expected_complexity,
    COUNT(r.result_id) AS total_runs,
    COUNT(r.result_id) FILTER (WHERE r.passed) AS passed_runs,
    COUNT(r.result_id) FILTER (WHERE NOT r.passed) AS failed_runs,
    ROUND(
        100.0 * COUNT(r.result_id) FILTER (WHERE r.passed)
        / NULLIF(COUNT(r.result_id), 0),
        2
    ) AS pass_percentage
FROM assessment_case c
LEFT JOIN assessment_result r ON r.case_id = c.case_id
GROUP BY c.case_id, c.problem_name, c.difficulty,
         c.technique, c.expected_complexity;

-- Inspect algorithm coverage and measured assessment outcomes.
SELECT problem_name, difficulty, technique, expected_complexity
FROM assessment_case
ORDER BY
    CASE difficulty
        WHEN 'Easy' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END,
    problem_name;

SELECT *
FROM linked_list_assessment_summary
ORDER BY
    CASE difficulty
        WHEN 'Easy' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END,
    problem_name;

-- A recursive CTE follows the recorded next_position links from each head.
-- A visited path prevents infinite recursion if corrupted data contains a
-- multi-node cycle. SQL storage does not automatically guarantee acyclicity.
WITH RECURSIVE traversal AS (
    SELECT
        n.case_id,
        n.list_label,
        n.position AS current_position,
        n.node_value,
        n.next_position,
        ARRAY[n.position] AS visited_positions,
        FALSE AS cycle_detected
    FROM list_node n
    WHERE n.position = 0

    UNION ALL

    SELECT
        t.case_id,
        t.list_label,
        next_node.position,
        next_node.node_value,
        next_node.next_position,
        t.visited_positions || next_node.position,
        next_node.position = ANY(t.visited_positions)
    FROM traversal t
    JOIN list_node next_node
      ON next_node.case_id = t.case_id
     AND next_node.list_label = t.list_label
     AND next_node.position = t.next_position
    WHERE NOT t.cycle_detected
)
SELECT case_id, list_label, current_position, node_value, cycle_detected
FROM traversal
ORDER BY case_id, list_label, cardinality(visited_positions);

-- This integrity query identifies links pointing to missing positions.
-- A foreign key on (case_id, list_label, next_position) would be another
-- option, but NULL termination and the chosen identity model are explicit.
SELECT
    n.case_id,
    n.list_label,
    n.position,
    n.next_position
FROM list_node n
LEFT JOIN list_node target
  ON target.case_id = n.case_id
 AND target.list_label = n.list_label
 AND target.position = n.next_position
WHERE n.next_position IS NOT NULL
  AND target.node_id IS NULL;

COMMIT;
