DROP SCHEMA IF EXISTS linked_list_practice CASCADE;

CREATE SCHEMA linked_list_practice;

SET search_path TO linked_list_practice;

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'commented',
    'approved',
    'changes_requested',
    'dismissed'
);

CREATE TYPE check_state AS ENUM (
    'pending',
    'passing',
    'failing'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit',
    'squash',
    'rebase'
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'draft',
    is_draft BOOLEAN NOT NULL DEFAULT TRUE,
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    merge_strategy merge_strategy,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (state = 'draft' AND is_draft = TRUE)
        OR state <> 'draft'
    ),
    CHECK (
        state <> 'merged'
        OR merged_at IS NOT NULL
    )
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    commit_hash CHAR(40) NOT NULL,
    parent_commit_id BIGINT REFERENCES commits(commit_id),
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, commit_hash)
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id)
        ON DELETE RESTRICT,
    position INTEGER NOT NULL CHECK (position > 0),
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id)
        ON DELETE CASCADE,
    eligible_for_approval BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (repository_id, user_id)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    state review_state NOT NULL,
    body TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    commit_id BIGINT REFERENCES commits(commit_id)
        ON DELETE SET NULL,
    file_path TEXT,
    line_number INTEGER CHECK (line_number > 0),
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    state check_state NOT NULL DEFAULT 'pending',
    required BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0
        CHECK (required_approvals >= 0),
    require_passing_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_pull_requests_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, state);

CREATE INDEX idx_status_checks_pr_required
    ON status_checks(pull_request_id, required, state);

CREATE INDEX idx_review_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

CREATE INDEX idx_pr_commits_position
    ON pull_request_commits(pull_request_id, position);

CREATE OR REPLACE FUNCTION enforce_protected_branch_target()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    protected BOOLEAN;
BEGIN
    SELECT is_protected
    INTO protected
    FROM branches
    WHERE branch_id = NEW.target_branch_id;

    IF protected IS DISTINCT FROM TRUE THEN
        RETURN NEW;
    END IF;

    IF NEW.is_draft = FALSE AND NEW.state = 'open' THEN
        RETURN NEW;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_protected_branch_target
BEFORE INSERT OR UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION enforce_protected_branch_target();

INSERT INTO repositories (repository_name, default_branch)
VALUES ('payments-platform', 'main');

INSERT INTO users (username, display_name)
VALUES
    ('alice', 'Alice Reviewer'),
    ('bob', 'Bob Reviewer'),
    ('carol', 'Carol Security Reviewer'),
    ('contractor', 'External Contractor'),
    ('developer', 'Feature Developer');

INSERT INTO branches (repository_id, branch_name, is_protected)
SELECT repository_id, 'main', TRUE
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO branches (repository_id, branch_name, is_protected)
SELECT repository_id, 'feature/payment-reconciliation', FALSE
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO reviewers (
    repository_id,
    user_id,
    eligible_for_approval
)
SELECT r.repository_id, u.user_id, TRUE
FROM repositories r
JOIN users u
    ON u.username IN ('alice', 'bob', 'carol')
WHERE r.repository_name = 'payments-platform';

INSERT INTO reviewers (
    repository_id,
    user_id,
    eligible_for_approval
)
SELECT r.repository_id, u.user_id, FALSE
FROM repositories r
JOIN users u
    ON u.username = 'contractor'
WHERE r.repository_name = 'payments-platform';

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_passing_checks,
    require_resolved_conversations,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion,
    require_linear_history,
    dismiss_stale_approvals
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    TRUE,
    TRUE
FROM branches
WHERE branch_name = 'main';

INSERT INTO pull_requests (
    repository_id,
    author_id,
    source_branch_id,
    target_branch_id,
    title,
    state,
    is_draft,
    has_conflicts,
    opened_at
)
SELECT
    r.repository_id,
    author.user_id,
    source_branch.branch_id,
    target_branch.branch_id,
    'Reconcile payment settlement records',
    'open',
    FALSE,
    FALSE,
    CURRENT_TIMESTAMP
FROM repositories r
JOIN users author ON author.username = 'developer'
JOIN branches source_branch
    ON source_branch.repository_id = r.repository_id
   AND source_branch.branch_name = 'feature/payment-reconciliation'
JOIN branches target_branch
    ON target_branch.repository_id = r.repository_id
   AND target_branch.branch_name = 'main'
WHERE r.repository_name = 'payments-platform';

INSERT INTO commits (
    repository_id,
    commit_hash,
    parent_commit_id,
    author_id,
    message
)
SELECT
    r.repository_id,
    repeat('a', 40),
    NULL,
    u.user_id,
    'Add settlement reconciliation'
FROM repositories r
JOIN users u ON u.username = 'developer'
WHERE r.repository_name = 'payments-platform';

INSERT INTO commits (
    repository_id,
    commit_hash,
    parent_commit_id,
    author_id,
    message
)
SELECT
    r.repository_id,
    repeat('b', 40),
    c.commit_id,
    u.user_id,
    'Add reconciliation validation'
FROM repositories r
JOIN users u ON u.username = 'developer'
JOIN commits c
    ON c.repository_id = r.repository_id
   AND c.commit_hash = repeat('a', 40)
WHERE r.repository_name = 'payments-platform';

INSERT INTO pull_request_commits (
    pull_request_id,
    commit_id,
    position
)
SELECT
    pr.pull_request_id,
    c.commit_id,
    CASE c.commit_hash
        WHEN repeat('a', 40) THEN 1
        WHEN repeat('b', 40) THEN 2
    END
FROM pull_requests pr
JOIN commits c
    ON c.repository_id = pr.repository_id
WHERE pr.title = 'Reconcile payment settlement records';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    state,
    body
)
SELECT
    pr.pull_request_id,
    rv.reviewer_id,
    CASE u.username
        WHEN 'alice' THEN 'approved'
        WHEN 'bob' THEN 'approved'
        WHEN 'contractor' THEN 'approved'
    END,
    'Review decision recorded for repository governance.'
FROM pull_requests pr
JOIN reviewers rv
    ON rv.repository_id = pr.repository_id
JOIN users u
    ON u.user_id = rv.user_id
WHERE pr.title = 'Reconcile payment settlement records'
  AND u.username IN ('alice', 'bob', 'contractor');

INSERT INTO review_comments (
    review_id,
    body,
    resolved
)
SELECT
    review_id,
    'Clarify settlement reconciliation edge case.',
    FALSE
FROM reviews
WHERE state = 'approved'
ORDER BY review_id
LIMIT 1;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    state,
    required
)
SELECT
    pr.pull_request_id,
    check_name,
    state,
    TRUE
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('unit-tests', 'passing'::check_state),
        ('security-scan', 'passing'::check_state),
        ('integration-tests', 'pending'::check_state)
) AS checks(check_name, state)
WHERE pr.title = 'Reconcile payment settlement records';

CREATE OR REPLACE VIEW merge_eligibility AS
WITH approval_counts AS (
    SELECT
        rv.pull_request_id,
        COUNT(DISTINCT rv.reviewer_id)
            FILTER (
                WHERE rv.state = 'approved'
                  AND reviewer.eligible_for_approval
            ) AS eligible_approvals
    FROM reviews rv
    JOIN reviewers reviewer
        ON reviewer.reviewer_id = rv.reviewer_id
    GROUP BY rv.pull_request_id
),
check_results AS (
    SELECT
        pull_request_id,
        BOOL_AND(
            NOT required OR state = 'passing'
        ) AS required_checks_passing
    FROM status_checks
    GROUP BY pull_request_id
),
conversation_results AS (
    SELECT
        rv.pull_request_id,
        COUNT(*) FILTER (
            WHERE comment.resolved = FALSE
        ) AS unresolved_conversations
    FROM reviews rv
    LEFT JOIN review_comments comment
        ON comment.review_id = rv.review_id
    GROUP BY rv.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    pr.is_draft,
    pr.has_conflicts,
    COALESCE(ac.eligible_approvals, 0) AS eligible_approvals,
    policy.required_approvals,
    COALESCE(cr.required_checks_passing, TRUE)
        AS required_checks_passing,
    COALESCE(conv.unresolved_conversations, 0)
        AS unresolved_conversations,
    (
        pr.state = 'open'
        AND NOT pr.is_draft
        AND NOT pr.has_conflicts
        AND COALESCE(ac.eligible_approvals, 0)
            >= policy.required_approvals
        AND (
            NOT policy.require_passing_checks
            OR COALESCE(cr.required_checks_passing, FALSE)
        )
        AND (
            NOT policy.require_resolved_conversations
            OR COALESCE(conv.unresolved_conversations, 0) = 0
        )
    ) AS merge_eligible
FROM pull_requests pr
JOIN branch_protection_policies policy
    ON policy.branch_id = pr.target_branch_id
LEFT JOIN approval_counts ac
    ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_results cr
    ON cr.pull_request_id = pr.pull_request_id
LEFT JOIN conversation_results conv
    ON conv.pull_request_id = pr.pull_request_id;

SELECT *
FROM merge_eligibility;

SELECT
    pr.pull_request_id,
    pr.title,
    reviewer_user.username,
    review.state,
    reviewer.eligible_for_approval
FROM pull_requests pr
JOIN reviews review
    ON review.pull_request_id = pr.pull_request_id
JOIN reviewers reviewer
    ON reviewer.reviewer_id = review.reviewer_id
JOIN users reviewer_user
    ON reviewer_user.user_id = reviewer.user_id
ORDER BY pr.pull_request_id, review.review_id;

SELECT
    pr.title,
    status.check_name,
    status.state,
    status.required
FROM pull_requests pr
JOIN status_checks status
    ON status.pull_request_id = pr.pull_request_id
WHERE status.required = TRUE
ORDER BY pr.title, status.check_name;

BEGIN;

UPDATE status_checks
SET
    state = 'passing',
    updated_at = CURRENT_TIMESTAMP
WHERE pull_request_id = (
    SELECT pull_request_id
    FROM pull_requests
    WHERE title = 'Reconcile payment settlement records'
)
AND check_name = 'integration-tests';

UPDATE review_comments
SET resolved = TRUE
WHERE comment_id = (
    SELECT MIN(comment_id)
    FROM review_comments
);

COMMIT;

SELECT
    pull_request_id,
    title,
    eligible_approvals,
    required_approvals,
    required_checks_passing,
    unresolved_conversations,
    merge_eligible
FROM merge_eligibility;

UPDATE pull_requests
SET
    state = 'merged',
    is_draft = FALSE,
    merged_at = CURRENT_TIMESTAMP,
    merge_strategy = 'squash'
WHERE pull_request_id = (
    SELECT pull_request_id
    FROM merge_eligibility
    WHERE merge_eligible = TRUE
    LIMIT 1
)
AND EXISTS (
    SELECT 1
    FROM merge_eligibility
    WHERE merge_eligibility.pull_request_id =
          pull_requests.pull_request_id
      AND merge_eligibility.merge_eligible = TRUE
);

SELECT
    pull_request_id,
    title,
    state,
    merged_at,
    merge_strategy
FROM pull_requests
WHERE state = 'merged';
