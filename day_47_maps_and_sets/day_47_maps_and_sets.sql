-- PostgreSQL 15+
-- Relational model for map/set operations and repository governance.
-- A normalized relational design preserves event history while queries
-- construct frequencies, distinct memberships, intersections, and merge decisions.

BEGIN;

DROP SCHEMA IF EXISTS map_set_governance CASCADE;
CREATE SCHEMA map_set_governance;
SET search_path TO map_set_governance, public;

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    UNIQUE (owner_name, repository_name),
    CHECK (length(trim(owner_name)) > 0),
    CHECK (length(trim(repository_name)) > 0)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) > 0)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'open'
        CHECK (state IN ('open', 'draft', 'closed', 'merged')),
    head_commit TEXT NOT NULL,
    base_commit TEXT NOT NULL,
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    conversations_resolved BOOLEAN NOT NULL DEFAULT TRUE,
    linear_history_satisfied BOOLEAN NOT NULL DEFAULT TRUE,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    merged_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(head_commit)) > 0),
    CHECK (length(trim(base_commit)) > 0),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL)
        OR (state <> 'merged' AND merged_at IS NULL)
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_sha TEXT NOT NULL,
    parent_sha TEXT,
    author_name TEXT NOT NULL,
    subject TEXT NOT NULL,
    PRIMARY KEY (pull_request_id, commit_sha),
    CHECK (length(trim(commit_sha)) > 0),
    CHECK (length(trim(author_name)) > 0),
    CHECK (length(trim(subject)) > 0)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE eligible_reviewers (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    PRIMARY KEY (policy_id, reviewer_id)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    state TEXT NOT NULL
        CHECK (state IN ('approved', 'changes_requested', 'commented', 'dismissed')),
    reviewed_commit TEXT NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    file_path TEXT,
    line_number INTEGER,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (length(trim(body)) > 0),
    CHECK ((file_path IS NULL AND line_number IS NULL)
        OR (file_path IS NOT NULL AND line_number IS NOT NULL))
);

CREATE TABLE status_check_runs (
    check_run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    conclusion TEXT NOT NULL
        CHECK (conclusion IN ('success', 'failure', 'cancelled', 'pending')),
    completed_at TIMESTAMPTZ,
    CHECK (
        (conclusion = 'pending' AND completed_at IS NULL)
        OR (conclusion <> 'pending' AND completed_at IS NOT NULL)
    )
);

CREATE TABLE pull_request_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    actor TEXT NOT NULL,
    event_type TEXT NOT NULL
        CHECK (event_type IN (
            'opened', 'synchronized', 'review_requested', 'approved',
            'changes_requested', 'conversation_resolved', 'closed', 'merged'
        )),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(actor)) > 0)
);

CREATE INDEX idx_pull_requests_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_latest_per_reviewer
    ON reviews(pull_request_id, reviewer_id, submitted_at DESC, review_id DESC);

CREATE INDEX idx_status_checks_latest
    ON status_check_runs(pull_request_id, check_name, check_run_id DESC);

CREATE INDEX idx_review_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

CREATE INDEX idx_pull_request_events_type_time
    ON pull_request_events(event_type, occurred_at DESC);

INSERT INTO repositories(owner_name, repository_name, default_branch)
VALUES ('engineering', 'identity-service', 'main');

INSERT INTO branches(repository_id, branch_name, is_protected)
VALUES
    (1, 'main', TRUE),
    (1, 'feature/token-validation', FALSE),
    (1, 'feature/session-fix', FALSE),
    (1, 'feature/authorization', FALSE);

INSERT INTO reviewers(username)
VALUES ('mira'), ('dev'), ('anika'), ('rohan'), ('external-contributor');

INSERT INTO branch_protection_policies(
    branch_id, required_approvals, require_resolved_conversations,
    require_linear_history, allow_direct_push, allow_force_push,
    allow_deletion, administrator_bypass
)
VALUES (1, 2, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE);

INSERT INTO eligible_reviewers(policy_id, reviewer_id)
SELECT 1, reviewer_id
FROM reviewers
WHERE username IN ('mira', 'dev', 'anika', 'rohan');

INSERT INTO required_status_checks(policy_id, check_name)
VALUES
    (1, 'build'),
    (1, 'unit-tests'),
    (1, 'security-scan');

INSERT INTO pull_requests(
    repository_id, source_branch_id, target_branch_id, title,
    state, head_commit, base_commit, has_conflicts,
    conversations_resolved, linear_history_satisfied
)
VALUES
    (1, 2, 1, 'Validate access tokens', 'open', 'head-a', 'base-0',
     FALSE, TRUE, TRUE),
    (1, 3, 1, 'Repair session expiry', 'open', 'head-b', 'base-0',
     FALSE, TRUE, TRUE),
    (1, 4, 1, 'Strengthen authorization rules', 'draft', 'head-c', 'base-0',
     TRUE, FALSE, FALSE);

INSERT INTO pull_request_commits(
    pull_request_id, commit_sha, parent_sha, author_name, subject
)
VALUES
    (1, 'head-a', 'base-0', 'Mira', 'Validate signed access tokens'),
    (1, 'head-b', 'base-0', 'Dev', 'Handle expired sessions'),
    (2, 'head-b', 'base-0', 'Dev', 'Handle expired sessions'),
    (3, 'head-c', 'base-0', 'Anika', 'Restrict privileged endpoints');

INSERT INTO reviews(
    pull_request_id, reviewer_id, state, reviewed_commit, submitted_at
)
SELECT 1, reviewer_id, state, commit_sha, submitted_at
FROM (
    VALUES
        ('mira', 'approved', 'head-a', TIMESTAMPTZ '2026-10-17 08:00:00+00'),
        ('dev', 'approved', 'head-a', TIMESTAMPTZ '2026-10-17 08:05:00+00'),
        ('anika', 'commented', 'head-a', TIMESTAMPTZ '2026-10-17 08:10:00+00')
) AS sample(username, state, commit_sha, submitted_at)
JOIN reviewers USING (username);

-- A later dismissal invalidates the same reviewer's earlier approval.
INSERT INTO reviews(pull_request_id, reviewer_id, state, reviewed_commit, submitted_at)
SELECT 2, reviewer_id, state, commit_sha, submitted_at
FROM (
    VALUES
        ('mira', 'approved', 'head-b', TIMESTAMPTZ '2026-10-17 08:00:00+00'),
        ('mira', 'dismissed', 'head-b', TIMESTAMPTZ '2026-10-17 08:20:00+00'),
        ('dev', 'approved', 'head-b', TIMESTAMPTZ '2026-10-17 08:25:00+00')
) AS sample(username, state, commit_sha, submitted_at)
JOIN reviewers USING (username);

INSERT INTO reviews(pull_request_id, reviewer_id, state, reviewed_commit)
SELECT 3, reviewer_id, 'approved', 'head-c'
FROM reviewers
WHERE username IN ('mira', 'external-contributor');

INSERT INTO status_check_runs(
    pull_request_id, check_name, commit_sha, conclusion, completed_at
)
VALUES
    (1, 'build', 'head-a', 'success', now()),
    (1, 'unit-tests', 'head-a', 'success', now()),
    (1, 'security-scan', 'head-a', 'success', now()),
    (2, 'build', 'head-b', 'success', now()),
    (2, 'unit-tests', 'head-b', 'success', now()),
    (2, 'security-scan', 'head-b', 'success', now()),
    (3, 'build', 'head-c', 'success', now()),
    (3, 'unit-tests', 'head-c', 'failure', now());

INSERT INTO review_comments(review_id, file_path, line_number, body, resolved)
SELECT review_id, 'src/auth/token.py', 42,
       'Reject tokens with an invalid issuer.', FALSE
FROM reviews
WHERE pull_request_id = 1 AND state = 'commented';

INSERT INTO pull_request_events(pull_request_id, actor, event_type)
VALUES
    (1, 'mira', 'opened'),
    (1, 'dev', 'review_requested'),
    (1, 'dev', 'approved'),
    (2, 'mira', 'approved'),
    (2, 'mira', 'changes_requested'),
    (3, 'anika', 'opened');

-- Map-like frequency counting: GROUP BY computes frequencies from event rows.
SELECT event_type, count(*) AS occurrence_count
FROM pull_request_events
GROUP BY event_type
ORDER BY occurrence_count DESC, event_type;

-- Duplicate detection: identify source files mentioned by multiple comments.
SELECT file_path, count(*) AS comment_count
FROM review_comments
WHERE file_path IS NOT NULL
GROUP BY file_path
HAVING count(*) > 1;

-- Distinct reviewers use relational set semantics rather than counting reviews.
SELECT DISTINCT r.username
FROM reviews rv
JOIN reviewers r USING (reviewer_id)
WHERE rv.pull_request_id = 1
ORDER BY r.username;

-- Intersection: reviewers who participated in both selected pull requests.
SELECT r.username
FROM reviews rv
JOIN reviewers r USING (reviewer_id)
WHERE rv.pull_request_id IN (1, 2)
GROUP BY r.reviewer_id, r.username
HAVING count(DISTINCT rv.pull_request_id) = 2
ORDER BY r.username;

-- Union: all reviewers who participated in either pull request.
SELECT username
FROM (
    SELECT DISTINCT r.username
    FROM reviews rv
    JOIN reviewers r USING (reviewer_id)
    WHERE rv.pull_request_id = 1
    UNION
    SELECT DISTINCT r.username
    FROM reviews rv
    JOIN reviewers r USING (reviewer_id)
    WHERE rv.pull_request_id = 2
) AS reviewer_union
ORDER BY username;

-- The latest review per reviewer is determined by submission time and review ID.
-- Eligibility also requires an active, policy-authorized reviewer and a review
-- against the current head commit. DISTINCT ON is PostgreSQL-specific.
CREATE VIEW latest_reviewer_decisions AS
SELECT DISTINCT ON (rv.pull_request_id, rv.reviewer_id)
    rv.pull_request_id,
    rv.reviewer_id,
    rv.state,
    rv.reviewed_commit,
    rv.submitted_at,
    rv.review_id
FROM reviews rv
ORDER BY
    rv.pull_request_id,
    rv.reviewer_id,
    rv.submitted_at DESC,
    rv.review_id DESC;

CREATE VIEW pull_request_merge_eligibility AS
WITH latest_checks AS (
    SELECT DISTINCT ON (scr.pull_request_id, scr.check_name)
        scr.pull_request_id,
        scr.check_name,
        scr.commit_sha,
        scr.conclusion
    FROM status_check_runs scr
    ORDER BY scr.pull_request_id, scr.check_name, scr.check_run_id DESC
),
approval_counts AS (
    SELECT
        pr.pull_request_id,
        count(DISTINCT lrd.reviewer_id) FILTER (
            WHERE lrd.state = 'approved'
              AND lrd.reviewed_commit = pr.head_commit
              AND er.reviewer_id IS NOT NULL
              AND reviewer.active
        ) AS effective_approvals
    FROM pull_requests pr
    LEFT JOIN latest_reviewer_decisions lrd
        ON lrd.pull_request_id = pr.pull_request_id
    LEFT JOIN branch_protection_policies bp
        ON bp.branch_id = pr.target_branch_id
    LEFT JOIN eligible_reviewers er
        ON er.policy_id = bp.policy_id
       AND er.reviewer_id = lrd.reviewer_id
    LEFT JOIN reviewers reviewer
        ON reviewer.reviewer_id = lrd.reviewer_id
    GROUP BY pr.pull_request_id
),
check_counts AS (
    SELECT
        pr.pull_request_id,
        count(*) FILTER (
            WHERE lsc.check_name IS NULL
               OR lsc.conclusion <> 'success'
               OR lsc.commit_sha <> pr.head_commit
        ) AS failing_or_missing_checks
    FROM pull_requests pr
    JOIN branch_protection_policies bp
        ON bp.branch_id = pr.target_branch_id
    LEFT JOIN required_status_checks required
        ON required.policy_id = bp.policy_id
    LEFT JOIN latest_checks lsc
        ON lsc.pull_request_id = pr.pull_request_id
       AND lsc.check_name = required.check_name
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    coalesce(ac.effective_approvals, 0) AS effective_approvals,
    bp.required_approvals,
    coalesce(cc.failing_or_missing_checks, 0) AS failing_or_missing_checks,
    (
        pr.state = 'open'
        AND NOT pr.has_conflicts
        AND (
            NOT bp.require_resolved_conversations
            OR pr.conversations_resolved
        )
        AND (
            NOT bp.require_linear_history
            OR pr.linear_history_satisfied
        )
        AND coalesce(ac.effective_approvals, 0) >= bp.required_approvals
        AND coalesce(cc.failing_or_missing_checks, 0) = 0
    ) AS merge_eligible
FROM pull_requests pr
JOIN branch_protection_policies bp
    ON bp.branch_id = pr.target_branch_id
LEFT JOIN approval_counts ac
    ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_counts cc
    ON cc.pull_request_id = pr.pull_request_id;

SELECT *
FROM pull_request_merge_eligibility
ORDER BY pull_request_id;

-- Report unresolved inline discussions separately from merge decisions.
SELECT
    pr.pull_request_id,
    pr.title,
    count(rc.comment_id) AS unresolved_discussions
FROM pull_requests pr
JOIN reviews rv USING (pull_request_id)
JOIN review_comments rc USING (review_id)
WHERE rc.resolved = FALSE
GROUP BY pr.pull_request_id, pr.title
ORDER BY pr.pull_request_id;

-- A failed or absent required check blocks a merge even if review approval
-- requirements are met. The eligibility view evaluates the latest check result
-- for the current head commit rather than accepting a stale successful run.
-- The policy's bypass flag is recorded explicitly; authorization to bypass
-- should be audited separately and should not be silently inferred.

-- Constraint demonstration: the following transaction intentionally violates
-- the nonnegative approval rule. The savepoint allows the script to continue.
SAVEPOINT invalid_policy_test;

DO $$
BEGIN
    BEGIN
        INSERT INTO branch_protection_policies(
            branch_id, required_approvals
        )
        VALUES (2, -1);
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'Rejected invalid negative approval requirement.';
    END;
END;
$$;

RELEASE SAVEPOINT invalid_policy_test;

COMMIT;
