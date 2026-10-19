DROP SCHEMA IF EXISTS prefix_hashing_governance CASCADE;
CREATE SCHEMA prefix_hashing_governance;
SET search_path = prefix_hashing_governance;

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main'
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id) ON DELETE CASCADE,
    sha TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, sha)
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id) ON DELETE CASCADE,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    title TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'OPEN'
        CHECK (state IN ('OPEN', 'CLOSED', 'MERGED')),
    is_draft BOOLEAN NOT NULL DEFAULT TRUE,
    head_commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    base_commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    merge_conflict BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (closed_at IS NULL OR state IN ('CLOSED', 'MERGED'))
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, sequence_no)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(user_id),
    reviewed_commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    review_state TEXT NOT NULL
        CHECK (review_state IN ('COMMENTED', 'APPROVED', 'CHANGES_REQUESTED')),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name, commit_id)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0 CHECK (required_approvals >= 0),
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    prevent_branch_deletion BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name)
);

CREATE INDEX idx_pr_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, review_state);

CREATE INDEX idx_reviews_current_commit
    ON reviews(pull_request_id, reviewed_commit_id);

CREATE INDEX idx_status_checks_pr
    ON status_checks(pull_request_id, check_name, commit_id);

CREATE INDEX idx_review_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

INSERT INTO repositories (repository_name)
VALUES ('prefix-hashing-platform');

INSERT INTO branches (repository_id, branch_name, protected)
VALUES
    (1, 'main', TRUE),
    (1, 'feature/prefix-state', FALSE);

INSERT INTO users (username)
VALUES
    ('atul'),
    ('reviewer_a'),
    ('reviewer_b'),
    ('security_team');

INSERT INTO commits (repository_id, sha)
VALUES
    (1, 'main-100'),
    (1, 'feature-201'),
    (1, 'feature-202');

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    author_id,
    title,
    state,
    is_draft,
    head_commit_id,
    base_commit_id
)
VALUES (
    1,
    2,
    1,
    1,
    'Implement prefix-state analytics',
    'OPEN',
    FALSE,
    3,
    1
);

INSERT INTO pull_request_commits (pull_request_id, commit_id, sequence_no)
VALUES
    (1, 2, 1),
    (1, 3, 2);

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_conversation_resolution,
    allow_direct_push,
    allow_force_push,
    require_linear_history,
    prevent_branch_deletion
)
VALUES (
    1,
    2,
    TRUE,
    FALSE,
    FALSE,
    TRUE,
    TRUE
);

INSERT INTO required_status_checks (policy_id, check_name)
VALUES
    (1, 'unit-tests'),
    (1, 'security-scan');

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    reviewed_commit_id,
    review_state
)
VALUES
    (1, 2, 3, 'APPROVED'),
    (1, 3, 3, 'APPROVED');

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
VALUES
    (1, 'prefix_state.py', 42, 'Validate the binary-state transformation.', TRUE),
    (2, 'prefix_state.py', 77, 'Hash tuple state consistently.', TRUE);

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    commit_id,
    passed,
    completed_at
)
VALUES
    (1, 'unit-tests', 3, TRUE, CURRENT_TIMESTAMP),
    (1, 'security-scan', 3, TRUE, CURRENT_TIMESTAMP);

CREATE VIEW pull_request_merge_eligibility AS
WITH policy AS (
    SELECT
        bp.policy_id,
        bp.branch_id,
        bp.required_approvals,
        bp.require_conversation_resolution
    FROM branch_protection_policies bp
),
approval_counts AS (
    SELECT
        r.pull_request_id,
        COUNT(DISTINCT r.reviewer_id)
            FILTER (
                WHERE r.review_state = 'APPROVED'
                  AND r.reviewed_commit_id = pr.head_commit_id
            ) AS approvals
    FROM pull_requests pr
    LEFT JOIN reviews r
        ON r.pull_request_id = pr.pull_request_id
    GROUP BY r.pull_request_id
),
required_checks AS (
    SELECT
        pr.pull_request_id,
        COUNT(rsc.check_name) AS required_count,
        COUNT(sc.check_name)
            FILTER (WHERE sc.passed = TRUE AND sc.commit_id = pr.head_commit_id)
            AS passed_count
    FROM pull_requests pr
    JOIN policy p
        ON p.branch_id = pr.target_branch_id
    LEFT JOIN required_status_checks rsc
        ON rsc.policy_id = p.policy_id
    LEFT JOIN status_checks sc
        ON sc.pull_request_id = pr.pull_request_id
       AND sc.check_name = rsc.check_name
    GROUP BY pr.pull_request_id
),
unresolved AS (
    SELECT
        pr.pull_request_id,
        COUNT(rc.comment_id)
            FILTER (WHERE rc.resolved = FALSE) AS unresolved_comments
    FROM pull_requests pr
    LEFT JOIN reviews r
        ON r.pull_request_id = pr.pull_request_id
    LEFT JOIN review_comments rc
        ON rc.review_id = r.review_id
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    pr.is_draft,
    pr.merge_conflict,
    COALESCE(ac.approvals, 0) AS approvals,
    p.required_approvals,
    COALESCE(rc.required_count, 0) AS required_checks,
    COALESCE(rc.passed_count, 0) AS passed_checks,
    COALESCE(u.unresolved_comments, 0) AS unresolved_comments,
    (
        pr.state = 'OPEN'
        AND pr.is_draft = FALSE
        AND pr.merge_conflict = FALSE
        AND COALESCE(ac.approvals, 0) >= p.required_approvals
        AND COALESCE(rc.passed_count, 0) = COALESCE(rc.required_count, 0)
        AND (
            NOT p.require_conversation_resolution
            OR COALESCE(u.unresolved_comments, 0) = 0
        )
    ) AS merge_eligible
FROM pull_requests pr
JOIN policy p
    ON p.branch_id = pr.target_branch_id
LEFT JOIN approval_counts ac
    ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN required_checks rc
    ON rc.pull_request_id = pr.pull_request_id
LEFT JOIN unresolved u
    ON u.pull_request_id = pr.pull_request_id;

SELECT *
FROM pull_request_merge_eligibility;

SELECT
    pr.pull_request_id,
    pr.title,
    r.reviewer_id,
    r.review_state,
    r.reviewed_commit_id,
    pr.head_commit_id,
    CASE
        WHEN r.reviewed_commit_id = pr.head_commit_id
        THEN 'CURRENT_HEAD'
        ELSE 'STALE_REVIEW'
    END AS approval_freshness
FROM pull_requests pr
JOIN reviews r
    ON r.pull_request_id = pr.pull_request_id
ORDER BY r.review_id;

SELECT
    repository_name,
    branch_name,
    protected,
    bp.required_approvals,
    bp.allow_direct_push,
    bp.allow_force_push,
    bp.require_linear_history
FROM repositories r
JOIN branches b
    ON b.repository_id = r.repository_id
LEFT JOIN branch_protection_policies bp
    ON bp.branch_id = b.branch_id
WHERE b.branch_name = 'main';

BEGIN;

UPDATE pull_requests
SET merge_conflict = TRUE
WHERE pull_request_id = 1;

SELECT *
FROM pull_request_merge_eligibility
WHERE pull_request_id = 1;

ROLLBACK;

BEGIN;

UPDATE status_checks
SET passed = FALSE
WHERE pull_request_id = 1
  AND check_name = 'security-scan'
  AND commit_id = 3;

SELECT *
FROM pull_request_merge_eligibility
WHERE pull_request_id = 1;

ROLLBACK;

BEGIN;

UPDATE pull_requests
SET state = 'MERGED',
    closed_at = CURRENT_TIMESTAMP
WHERE pull_request_id = 1
  AND pull_request_id IN (
      SELECT pull_request_id
      FROM pull_request_merge_eligibility
      WHERE merge_eligible = TRUE
  );

COMMIT;

SELECT
    pull_request_id,
    title,
    state,
    merge_eligible
FROM pull_request_merge_eligibility;
