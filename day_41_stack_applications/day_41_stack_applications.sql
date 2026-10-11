-- PostgreSQL stack applications: repository workflow and expression processing.
-- This schema models Pull Requests, code reviews, approvals, branch protection,
-- status checks, and database-enforced merge eligibility.

BEGIN;

DROP VIEW IF EXISTS merge_eligibility CASCADE;
DROP TABLE IF EXISTS merge_events CASCADE;
DROP TABLE IF EXISTS review_comments CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS status_checks CASCADE;
DROP TABLE IF EXISTS pull_request_commits CASCADE;
DROP TABLE IF EXISTS pull_requests CASCADE;
DROP TABLE IF EXISTS branch_protection CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS repository_members CASCADE;
DROP TABLE IF EXISTS repositories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    UNIQUE (owner_name, repository_name)
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id)
        ON DELETE CASCADE,
    can_review BOOLEAN NOT NULL DEFAULT FALSE,
    can_bypass_protection BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (repository_id, user_id)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    head_commit TEXT NOT NULL,
    deleted_at TIMESTAMPTZ,
    UNIQUE (repository_id, branch_name),
    CHECK (length(btrim(branch_name)) > 0),
    CHECK (length(btrim(head_commit)) > 0)
);

CREATE TABLE branch_protection (
    protection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    required_checks TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    require_resolved_discussions BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    restrict_direct_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT TRUE,
    require_latest_push_approval BOOLEAN NOT NULL DEFAULT FALSE,
    administrators_must_comply BOOLEAN NOT NULL DEFAULT TRUE,
    allow_bypass BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    title TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'open'
        CHECK (state IN ('draft', 'open', 'merged', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    source_head_commit TEXT NOT NULL,
    base_head_commit TEXT NOT NULL,
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    discussions_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    proposed_merge_is_linear BOOLEAN NOT NULL DEFAULT TRUE,
    merge_strategy TEXT
        CHECK (merge_strategy IN ('merge_commit', 'squash', 'rebase')),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (length(btrim(title)) > 0),
    CHECK (
        (state = 'merged' AND merged_at IS NOT NULL AND merge_strategy IS NOT NULL)
        OR
        (state <> 'merged' AND merged_at IS NULL AND merge_strategy IS NULL)
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_sha TEXT NOT NULL,
    parent_sha TEXT,
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    PRIMARY KEY (pull_request_id, commit_sha),
    CHECK (length(btrim(commit_sha)) > 0),
    CHECK (length(btrim(message)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'success', 'failure', 'cancelled')),
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name, commit_sha),
    CHECK (
        (state = 'pending' AND completed_at IS NULL)
        OR
        (state <> 'pending')
    )
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(user_id),
    state TEXT NOT NULL CHECK (
        state IN ('commented', 'approved', 'changes_requested', 'dismissed')
    ),
    commit_sha TEXT NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ,
    summary TEXT NOT NULL DEFAULT '',
    CHECK (
        (state = 'dismissed' AND dismissed_at IS NOT NULL)
        OR
        (state <> 'dismissed' AND dismissed_at IS NULL)
    )
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    comment_body TEXT NOT NULL,
    parent_comment_id BIGINT REFERENCES review_comments(comment_id),
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (length(btrim(file_path)) > 0),
    CHECK (length(btrim(comment_body)) > 0),
    CHECK (
        (is_resolved AND resolved_at IS NOT NULL)
        OR
        (NOT is_resolved AND resolved_at IS NULL)
    )
);

CREATE TABLE merge_events (
    merge_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id),
    actor_id BIGINT NOT NULL REFERENCES users(user_id),
    merge_strategy TEXT NOT NULL
        CHECK (merge_strategy IN ('merge_commit', 'squash', 'rebase')),
    merged_commit_sha TEXT NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(btrim(merged_commit_sha)) > 0)
);

CREATE INDEX idx_pull_requests_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pull_request_time
    ON reviews(pull_request_id, submitted_at DESC);

CREATE INDEX idx_status_checks_current
    ON status_checks(pull_request_id, commit_sha, check_name, state);

CREATE INDEX idx_unresolved_review_comments
    ON review_comments(review_id)
    WHERE is_resolved = FALSE;

-- Only repository members with review permission can be recorded as reviewers.
CREATE OR REPLACE FUNCTION validate_review_submission()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    request_author BIGINT;
    request_repository BIGINT;
    reviewer_active BOOLEAN;
    reviewer_authorized BOOLEAN;
BEGIN
    SELECT pr.author_id, pr.repository_id
      INTO request_author, request_repository
      FROM pull_requests AS pr
     WHERE pr.pull_request_id = NEW.pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request does not exist';
    END IF;

    IF request_author = NEW.reviewer_id THEN
        RAISE EXCEPTION 'Pull Request authors cannot review their own changes';
    END IF;

    SELECT u.active, COALESCE(rm.can_review, FALSE)
      INTO reviewer_active, reviewer_authorized
      FROM users AS u
      LEFT JOIN repository_members AS rm
        ON rm.user_id = u.user_id
       AND rm.repository_id = request_repository
     WHERE u.user_id = NEW.reviewer_id;

    IF NOT FOUND OR NOT reviewer_active OR NOT reviewer_authorized THEN
        RAISE EXCEPTION 'Reviewer is inactive or lacks repository review permission';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_submission
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW EXECUTE FUNCTION validate_review_submission();

-- Merge eligibility is derived from current data rather than a manually
-- maintained Boolean that could become stale when a commit or review changes.
CREATE VIEW merge_eligibility AS
WITH latest_review AS (
    SELECT DISTINCT ON (r.pull_request_id, r.reviewer_id)
           r.pull_request_id,
           r.reviewer_id,
           r.state,
           r.commit_sha,
           r.submitted_at
      FROM reviews AS r
     ORDER BY r.pull_request_id, r.reviewer_id, r.submitted_at DESC, r.review_id DESC
),
eligible_approvals AS (
    SELECT lr.pull_request_id,
           COUNT(DISTINCT lr.reviewer_id) AS approval_count
      FROM latest_review AS lr
      JOIN pull_requests AS pr
        ON pr.pull_request_id = lr.pull_request_id
      JOIN repository_members AS rm
        ON rm.repository_id = pr.repository_id
       AND rm.user_id = lr.reviewer_id
       AND rm.can_review = TRUE
      JOIN users AS u
        ON u.user_id = lr.reviewer_id
       AND u.active = TRUE
      JOIN branches AS target
        ON target.branch_id = pr.target_branch_id
      JOIN branch_protection AS bp
        ON bp.branch_id = target.branch_id
     WHERE lr.state = 'approved'
       AND (
           NOT bp.dismiss_stale_approvals
           OR lr.commit_sha = pr.source_head_commit
       )
       AND (
           NOT bp.require_latest_push_approval
           OR lr.commit_sha = pr.source_head_commit
       )
     GROUP BY lr.pull_request_id
),
required_check_results AS (
    SELECT pr.pull_request_id,
           CASE
               WHEN cardinality(bp.required_checks) = 0 THEN TRUE
               ELSE NOT EXISTS (
                   SELECT 1
                     FROM unnest(bp.required_checks) AS required(check_name)
                    WHERE NOT EXISTS (
                        SELECT 1
                          FROM status_checks AS sc
                         WHERE sc.pull_request_id = pr.pull_request_id
                           AND sc.check_name = required.check_name
                           AND sc.commit_sha = pr.source_head_commit
                           AND sc.state = 'success'
                    )
               )
           END AS all_required_checks_pass
      FROM pull_requests AS pr
      JOIN branch_protection AS bp
        ON bp.branch_id = pr.target_branch_id
)
SELECT pr.pull_request_id,
       pr.title,
       pr.state,
       source.branch_name AS source_branch,
       target.branch_name AS target_branch,
       COALESCE(ea.approval_count, 0) AS approval_count,
       bp.required_approvals,
       COALESCE(cr.all_required_checks_pass, FALSE) AS checks_pass,
       pr.has_conflicts,
       pr.discussions_resolved,
       pr.proposed_merge_is_linear,
       (
           pr.state = 'open'
           AND source.deleted_at IS NULL
           AND target.deleted_at IS NULL
           AND source.head_commit = pr.source_head_commit
           AND target.head_commit = pr.base_head_commit
           AND NOT pr.has_conflicts
           AND COALESCE(ea.approval_count, 0) >= bp.required_approvals
           AND COALESCE(cr.all_required_checks_pass, FALSE)
           AND (
               NOT bp.require_resolved_discussions
               OR pr.discussions_resolved
           )
           AND (
               NOT bp.require_linear_history
               OR pr.proposed_merge_is_linear
           )
       ) AS eligible_to_merge
  FROM pull_requests AS pr
  JOIN branches AS source
    ON source.branch_id = pr.source_branch_id
  JOIN branches AS target
    ON target.branch_id = pr.target_branch_id
  JOIN branch_protection AS bp
    ON bp.branch_id = target.branch_id
  LEFT JOIN eligible_approvals AS ea
    ON ea.pull_request_id = pr.pull_request_id
  LEFT JOIN required_check_results AS cr
    ON cr.pull_request_id = pr.pull_request_id;

-- Seed a realistic review workflow.
INSERT INTO users (username) VALUES
    ('author'),
    ('reviewer_alex'),
    ('reviewer_blair'),
    ('inactive_reviewer');

UPDATE users
   SET active = FALSE
 WHERE username = 'inactive_reviewer';

INSERT INTO repositories (owner_name, repository_name)
VALUES ('engineering', 'repository-governance');

INSERT INTO repository_members (repository_id, user_id, can_review, can_bypass_protection)
SELECT repo.repository_id, u.user_id,
       u.username IN ('reviewer_alex', 'reviewer_blair', 'inactive_reviewer'),
       FALSE
  FROM repositories AS repo
 CROSS JOIN users AS u
 WHERE repo.repository_name = 'repository-governance';

INSERT INTO branches (repository_id, branch_name, head_commit)
SELECT repository_id, 'main', 'base-001'
  FROM repositories
 WHERE repository_name = 'repository-governance';

INSERT INTO branches (repository_id, branch_name, head_commit)
SELECT repository_id, 'feature/approval-policy', 'feature-003'
  FROM repositories
 WHERE repository_name = 'repository-governance';

INSERT INTO branch_protection (
    branch_id,
    required_approvals,
    required_checks,
    require_resolved_discussions,
    require_linear_history,
    dismiss_stale_approvals,
    require_latest_push_approval
)
SELECT branch_id, 2,
       ARRAY['unit-tests', 'security-scan']::TEXT[],
       TRUE, TRUE, TRUE, TRUE
  FROM branches
 WHERE branch_name = 'main';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    author_id,
    title,
    state,
    source_head_commit,
    base_head_commit,
    has_conflicts,
    discussions_resolved,
    proposed_merge_is_linear
)
SELECT repo.repository_id,
       source.branch_id,
       target.branch_id,
       author.user_id,
       'Enforce repository approval policy',
       'open',
       source.head_commit,
       target.head_commit,
       FALSE,
       TRUE,
       TRUE
  FROM repositories AS repo
  JOIN branches AS source ON source.repository_id = repo.repository_id
  JOIN branches AS target ON target.repository_id = repo.repository_id
  JOIN users AS author ON author.username = 'author'
 WHERE repo.repository_name = 'repository-governance'
   AND source.branch_name = 'feature/approval-policy'
   AND target.branch_name = 'main';

INSERT INTO pull_request_commits (
    pull_request_id, commit_sha, parent_sha, author_id, message
)
SELECT pr.pull_request_id, 'feature-003', 'feature-002', u.user_id,
       'Add repository approval policy'
  FROM pull_requests AS pr
  JOIN users AS u ON u.username = 'author';

INSERT INTO status_checks (
    pull_request_id, check_name, commit_sha, state, completed_at
)
SELECT pr.pull_request_id, checks.check_name, 'feature-003',
       'success', CURRENT_TIMESTAMP
  FROM pull_requests AS pr
 CROSS JOIN (
     VALUES ('unit-tests'), ('security-scan')
 ) AS checks(check_name);

INSERT INTO reviews (
    pull_request_id, reviewer_id, state, commit_sha, summary
)
SELECT pr.pull_request_id, u.user_id, 'approved', 'feature-003',
       'Reviewed implementation and policy boundaries.'
  FROM pull_requests AS pr
 CROSS JOIN users AS u
 WHERE u.username IN ('reviewer_alex', 'reviewer_blair');

INSERT INTO reviews (
    pull_request_id, reviewer_id, state, commit_sha, summary
)
SELECT pr.pull_request_id, u.user_id, 'commented', 'feature-003',
       'The inactive reviewer cannot contribute an eligible approval.'
  FROM pull_requests AS pr
 CROSS JOIN users AS u
 WHERE u.username = 'inactive_reviewer';

INSERT INTO review_comments (
    review_id, file_path, line_number, comment_body, is_resolved, resolved_at
)
SELECT r.review_id, 'src/governance.py', 87,
       'Verify that a stale approval is excluded after a new commit.',
       TRUE, CURRENT_TIMESTAMP
  FROM reviews AS r
  JOIN users AS u ON u.user_id = r.reviewer_id
 WHERE u.username = 'reviewer_alex'
   AND r.state = 'approved'
   AND r.pull_request_id = (
       SELECT MIN(pull_request_id) FROM pull_requests
   );

-- This query exposes each Pull Request's computed blockers and eligibility.
SELECT pull_request_id, title, source_branch, target_branch,
       approval_count, required_approvals, checks_pass,
       has_conflicts, discussions_resolved, eligible_to_merge
  FROM merge_eligibility
 ORDER BY pull_request_id;

-- Aggregate unresolved inline discussions by Pull Request.
SELECT pr.pull_request_id,
       pr.title,
       COUNT(rc.comment_id) FILTER (WHERE NOT rc.is_resolved)
           AS unresolved_comments
  FROM pull_requests AS pr
  LEFT JOIN reviews AS r
    ON r.pull_request_id = pr.pull_request_id
  LEFT JOIN review_comments AS rc
    ON rc.review_id = r.review_id
 GROUP BY pr.pull_request_id, pr.title;

-- Simulate a new source commit. Old status checks and approvals become stale
-- under this policy, so the eligibility view must change without cached state.
BEGIN;

UPDATE branches
   SET head_commit = 'feature-004'
 WHERE branch_name = 'feature/approval-policy';

UPDATE pull_requests
   SET source_head_commit = 'feature-004'
 WHERE title = 'Enforce repository approval policy';

SELECT pull_request_id, approval_count, checks_pass, eligible_to_merge
  FROM merge_eligibility;

ROLLBACK;

-- Confirm the original seed state remains intact after the demonstration.
SELECT pull_request_id, title, eligible_to_merge
  FROM merge_eligibility;

COMMIT;
