import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise repository governance model.
 *
 * Compile and run:
 *   javac StackApplications.java
 *   java StackApplications
 *
 * The stack-based editor maintains immutable document snapshots.
 * A separate governance service evaluates pull-request eligibility from
 * explicit review, approval, branch, and status-check policies.
 */
public class StackApplications {

    enum ReviewState {
        COMMENTED,
        APPROVED,
        CHANGES_REQUESTED,
        DISMISSED
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        MERGED,
        CLOSED
    }

    enum CheckState {
        PENDING,
        SUCCESS,
        FAILURE,
        CANCELLED
    }

    enum MergeStrategy {
        MERGE_COMMIT,
        SQUASH,
        REBASE
    }

    record Reviewer(String id, boolean active, boolean canReview) {
        Reviewer {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Reviewer ID is required.");
            }
        }
    }

    record Review(
            String reviewerId,
            ReviewState state,
            String commitId,
            boolean eligibleForApproval
    ) {
        Review {
            Objects.requireNonNull(reviewerId);
            Objects.requireNonNull(state);
            Objects.requireNonNull(commitId);
            if (commitId.isBlank()) {
                throw new IllegalArgumentException("Review commit ID is required.");
            }
        }
    }

    record StatusCheck(String name, CheckState state, String commitId) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required.");
            }
            Objects.requireNonNull(state);
            Objects.requireNonNull(commitId);
        }
    }

    record BranchProtection(
            String branchName,
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireResolvedDiscussions,
            boolean requireLinearHistory,
            boolean restrictDirectPushes,
            boolean prohibitForcePushes,
            boolean prohibitDeletion,
            boolean dismissStaleApprovals,
            boolean requireLatestPushApproval,
            boolean administratorsMustComply
    ) {
        BranchProtection {
            if (branchName == null || branchName.isBlank()) {
                throw new IllegalArgumentException("Protected branch name is required.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException("Approval count cannot be negative.");
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    static final class PullRequest {
        private final String id;
        private final String sourceBranch;
        private final String targetBranch;
        private final String authorId;
        private final List<String> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, StatusCheck> checks = new HashMap<>();
        private PullRequestState state;
        private boolean conflicts;
        private boolean discussionsResolved;
        private boolean linearMerge;
        private String currentHead;
        private String lastPushedHead;
        private MergeStrategy mergeStrategy;

        PullRequest(
                String id,
                String sourceBranch,
                String targetBranch,
                String authorId,
                boolean draft,
                boolean linearMerge
        ) {
            if (id == null || id.isBlank() ||
                    sourceBranch == null || sourceBranch.isBlank() ||
                    targetBranch == null || targetBranch.isBlank() ||
                    authorId == null || authorId.isBlank()) {
                throw new IllegalArgumentException("Pull Request identifiers are required.");
            }
            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Source and target branches must differ.");
            }

            this.id = id;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.authorId = authorId;
            this.state = draft ? PullRequestState.DRAFT : PullRequestState.OPEN;
            this.linearMerge = linearMerge;
            this.discussionsResolved = true;
        }

        void addCommit(String commitId) {
            requireOpenForChanges();
            if (commitId == null || commitId.isBlank()) {
                throw new IllegalArgumentException("Commit ID is required.");
            }
            if (commits.contains(commitId)) {
                throw new IllegalArgumentException("Duplicate commit in Pull Request.");
            }

            commits.add(commitId);
            currentHead = commitId;

            // Any new head may invalidate prior approvals and check results.
            checks.clear();
            lastPushedHead = commitId;
        }

        void synchronizeBase(String resultingHead, boolean hasConflicts) {
            requireOpenForChanges();
            if (resultingHead == null || resultingHead.isBlank()) {
                throw new IllegalArgumentException("Synchronized head is required.");
            }
            currentHead = resultingHead;
            conflicts = hasConflicts;
            checks.clear();
        }

        void setConflicts(boolean conflicts) {
            requireOpenForChanges();
            this.conflicts = conflicts;
        }

        void setDiscussionsResolved(boolean resolved) {
            requireOpenForChanges();
            discussionsResolved = resolved;
        }

        void addReview(Review review) {
            requireOpenForChanges();
            if (review.reviewerId().equals(authorId)) {
                throw new IllegalArgumentException("Authors cannot approve their own Pull Request.");
            }
            reviews.add(review);
        }

        void publishCheck(StatusCheck check) {
            requireOpenForChanges();
            if (!Objects.equals(check.commitId(), currentHead)) {
                throw new IllegalArgumentException(
                        "Status check does not belong to the current Pull Request head.");
            }
            checks.put(check.name(), check);
        }

        void markReadyForReview() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Only a draft can be marked ready.");
            }
            state = PullRequestState.OPEN;
        }

        void close() {
            if (state == PullRequestState.MERGED) {
                throw new IllegalStateException("A merged Pull Request cannot be closed again.");
            }
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException("Only a closed Pull Request can be reopened.");
            }
            state = PullRequestState.OPEN;
        }

        void merge(MergeStrategy strategy) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Only an open Pull Request can be merged.");
            }
            state = PullRequestState.MERGED;
            mergeStrategy = Objects.requireNonNull(strategy);
        }

        private void requireOpenForChanges() {
            if (state != PullRequestState.OPEN && state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Pull Request is not editable.");
            }
        }

        String id() {
            return id;
        }

        String sourceBranch() {
            return sourceBranch;
        }

        String targetBranch() {
            return targetBranch;
        }

        String authorId() {
            return authorId;
        }

        String currentHead() {
            return currentHead;
        }

        String lastPushedHead() {
            return lastPushedHead;
        }

        PullRequestState state() {
            return state;
        }

        boolean hasConflicts() {
            return conflicts;
        }

        boolean discussionsResolved() {
            return discussionsResolved;
        }

        boolean linearMerge() {
            return linearMerge;
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        Map<String, StatusCheck> checks() {
            return Map.copyOf(checks);
        }

        MergeStrategy mergeStrategy() {
            return mergeStrategy;
        }
    }

    record Eligibility(boolean eligible, List<String> blockers) {
        Eligibility {
            blockers = List.copyOf(blockers);
        }
    }

    static final class GovernanceService {
        private final Map<String, Reviewer> reviewers;
        private final BranchProtection protection;

        GovernanceService(
                Map<String, Reviewer> reviewers,
                BranchProtection protection
        ) {
            this.reviewers = Map.copyOf(reviewers);
            this.protection = Objects.requireNonNull(protection);
        }

        Eligibility evaluate(PullRequest pullRequest) {
            List<String> blockers = new ArrayList<>();

            if (pullRequest.state() == PullRequestState.DRAFT) {
                blockers.add("Draft Pull Request is not mergeable.");
            }
            if (pullRequest.state() != PullRequestState.OPEN &&
                    pullRequest.state() != PullRequestState.DRAFT) {
                blockers.add("Pull Request is not open.");
            }
            if (!pullRequest.targetBranch().equals(protection.branchName())) {
                blockers.add("Pull Request does not target the governed branch.");
            }
            if (pullRequest.hasConflicts()) {
                blockers.add("Merge conflicts remain.");
            }
            if (protection.requireResolvedDiscussions() &&
                    !pullRequest.discussionsResolved()) {
                blockers.add("Review discussions remain unresolved.");
            }
            if (protection.requireLinearHistory() && !pullRequest.linearMerge()) {
                blockers.add("Proposed merge violates linear-history policy.");
            }

            Map<String, Review> latestByReviewer = new HashMap<>();
            for (Review review : pullRequest.reviews()) {
                Review previous = latestByReviewer.get(review.reviewerId());
                if (previous == null ||
                        review.commitId().equals(pullRequest.currentHead()) ||
                        !previous.commitId().equals(pullRequest.currentHead())) {
                    latestByReviewer.put(review.reviewerId(), review);
                }
            }

            Set<String> approvedReviewerIds = new java.util.HashSet<>();

            for (Review review : latestByReviewer.values()) {
                Reviewer reviewer = reviewers.get(review.reviewerId());

                if (review.state() != ReviewState.APPROVED ||
                        !review.eligibleForApproval() ||
                        reviewer == null ||
                        !reviewer.active() ||
                        !reviewer.canReview()) {
                    continue;
                }

                if (protection.dismissStaleApprovals() &&
                        !review.commitId().equals(pullRequest.currentHead())) {
                    continue;
                }

                if (protection.requireLatestPushApproval() &&
                        !review.commitId().equals(pullRequest.lastPushedHead())) {
                    continue;
                }

                approvedReviewerIds.add(review.reviewerId());
            }

            if (approvedReviewerIds.size() < protection.requiredApprovals()) {
                blockers.add(
                        "Insufficient eligible approvals: " + approvedReviewerIds.size() +
                        " of " + protection.requiredApprovals() + ".");
            }

            Map<String, StatusCheck> checks = pullRequest.checks();
            for (String requiredCheck : protection.requiredChecks()) {
                StatusCheck check = checks.get(requiredCheck);
                if (check == null ||
                        check.state() != CheckState.SUCCESS ||
                        !check.commitId().equals(pullRequest.currentHead())) {
                    blockers.add("Required check is missing, stale, or unsuccessful: " +
                            requiredCheck + ".");
                }
            }

            return new Eligibility(blockers.isEmpty(), blockers);
        }
    }

    static final class SnapshotEditor {
        private String document;
        private final Deque<String> undo = new ArrayDeque<>();
        private final Deque<String> redo = new ArrayDeque<>();
        private final int historyLimit;

        SnapshotEditor(String initialDocument, int historyLimit) {
            if (historyLimit < 1) {
                throw new IllegalArgumentException("History limit must be positive.");
            }
            document = Objects.requireNonNull(initialDocument);
            this.historyLimit = historyLimit;
        }

        String document() {
            return document;
        }

        void insert(int position, String text) {
            if (position < 0 || position > document.length()) {
                throw new IndexOutOfBoundsException("Invalid insertion position.");
            }
            saveSnapshot();
            document = document.substring(0, position) + text + document.substring(position);
        }

        String delete(int start, int end) {
            if (start < 0 || start > end || end > document.length()) {
                throw new IndexOutOfBoundsException("Invalid deletion range.");
            }
            if (start == end) return "";

            String removed = document.substring(start, end);
            saveSnapshot();
            document = document.substring(0, start) + document.substring(end);
            return removed;
        }

        boolean undo() {
            if (undo.isEmpty()) return false;
            redo.push(document);
            document = undo.pop();
            return true;
        }

        boolean redo() {
            if (redo.isEmpty()) return false;
            saveRedoDestination();
            document = redo.pop();
            return true;
        }

        private void saveSnapshot() {
            undo.push(document);
            while (undo.size() > historyLimit) {
                // ArrayDeque has no efficient oldest-item operation, so retain
                // bounded history through a temporary ordered copy.
                List<String> snapshots = new ArrayList<>(undo);
                undo.clear();
                for (int index = snapshots.size() - 1;
                     index >= 0 && undo.size() < historyLimit; index--) {
                    undo.push(snapshots.get(index));
                }
            }
            redo.clear();
        }

        private void saveRedoDestination() {
            undo.push(document);
            while (undo.size() > historyLimit) {
                List<String> snapshots = new ArrayList<>(undo);
                undo.clear();
                for (int index = snapshots.size() - 1;
                     index >= 0 && undo.size() < historyLimit; index--) {
                    undo.push(snapshots.get(index));
                }
            }
        }
    }

    static String reverse(String input) {
        Deque<Character> stack = new ArrayDeque<>();
        for (char character : input.toCharArray()) {
            stack.push(character);
        }

        StringBuilder reversed = new StringBuilder();
        while (!stack.isEmpty()) {
            reversed.append(stack.pop());
        }
        return reversed.toString();
    }

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) {
        System.out.println("Stack-based document editing");
        SnapshotEditor editor = new SnapshotEditor("Branch protection", 10);
        editor.insert(editor.document().length(), " enabled");
        System.out.println("Edited: " + editor.document());
        editor.undo();
        System.out.println("Undo: " + editor.document());
        editor.redo();
        System.out.println("Redo: " + editor.document());

        System.out.println("\nRepository governance evaluation");

        Map<String, Reviewer> reviewers = Map.of(
                "reviewer-a", new Reviewer("reviewer-a", true, true),
                "reviewer-b", new Reviewer("reviewer-b", true, true),
                "reviewer-c", new Reviewer("reviewer-c", false, true)
        );

        BranchProtection policy = new BranchProtection(
                "main",
                2,
                Set.of("unit-tests", "security-scan"),
                true,
                true,
                true,
                true,
                true,
                true,
                true,
                true
        );

        GovernanceService governance = new GovernanceService(reviewers, policy);
        PullRequest pullRequest = new PullRequest(
                "PR-301",
                "feature/approval-workflow",
                "main",
                "author",
                false,
                true
        );

        pullRequest.addCommit("commit-001");
        pullRequest.addReview(new Review(
                "reviewer-a", ReviewState.APPROVED, "commit-001", true));
        pullRequest.addReview(new Review(
                "reviewer-b", ReviewState.APPROVED, "commit-001", true));
        pullRequest.publishCheck(new StatusCheck(
                "unit-tests", CheckState.SUCCESS, "commit-001"));
        pullRequest.publishCheck(new StatusCheck(
                "security-scan", CheckState.SUCCESS, "commit-001"));

        Eligibility eligibility = governance.evaluate(pullRequest);
        System.out.println("Eligible before discussion changes: " + eligibility.eligible());

        pullRequest.setDiscussionsResolved(false);
        eligibility = governance.evaluate(pullRequest);
        System.out.println("Eligible with unresolved discussion: " + eligibility.eligible());
        eligibility.blockers().forEach(blocker -> System.out.println("- " + blocker));

        pullRequest.setDiscussionsResolved(true);
        pullRequest.addCommit("commit-002");
        eligibility = governance.evaluate(pullRequest);
        System.out.println("\nEligible after a new commit: " + eligibility.eligible());
        eligibility.blockers().forEach(blocker -> System.out.println("- " + blocker));

        System.out.println("\nReversal: " + reverse("repository"));

        require(reverse("stack").equals("kcats"), "Reversal failed.");
        require(!governance.evaluate(pullRequest).eligible(),
                "Stale checks should prevent merging.");
        System.out.println("Assertions passed.");
    }
}
