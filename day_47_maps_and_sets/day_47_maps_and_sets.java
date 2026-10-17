import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

public class MapsAndSets {
    enum ReviewState {
        APPROVED,
        CHANGES_REQUESTED,
        COMMENTED,
        DISMISSED
    }

    enum PullRequestState {
        OPEN,
        DRAFT,
        CLOSED,
        MERGED
    }

    enum MergeStrategy {
        MERGE_COMMIT,
        SQUASH,
        REBASE
    }

    record Review(String reviewer, ReviewState state, String commitId) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            Objects.requireNonNull(state, "Review state is required.");
            if (commitId == null || commitId.isBlank()) {
                throw new IllegalArgumentException("Reviewed commit is required.");
            }
        }
    }

    record StatusCheck(String name, boolean passed, String commitId) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required.");
            }
            if (commitId == null || commitId.isBlank()) {
                throw new IllegalArgumentException("Check commit is required.");
            }
        }
    }

    record PullRequest(
            int id,
            String sourceBranch,
            String targetBranch,
            PullRequestState state,
            String headCommit,
            boolean hasConflicts,
            boolean conversationsResolved,
            List<Review> reviews,
            List<StatusCheck> checks
    ) {
        PullRequest {
            if (id <= 0) {
                throw new IllegalArgumentException("Pull request ID must be positive.");
            }
            if (sourceBranch == null || sourceBranch.isBlank()
                    || targetBranch == null || targetBranch.isBlank()) {
                throw new IllegalArgumentException("Both branches are required.");
            }
            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Source and target must differ.");
            }
            if (headCommit == null || headCommit.isBlank()) {
                throw new IllegalArgumentException("Head commit is required.");
            }

            Objects.requireNonNull(state, "Pull request state is required.");
            reviews = List.copyOf(reviews);
            checks = List.copyOf(checks);
        }
    }

    record BranchPolicy(
            String branch,
            int requiredApprovals,
            Set<String> eligibleReviewers,
            Set<String> requiredChecks,
            boolean requireResolvedConversations,
            boolean requireLinearHistory,
            boolean allowDirectPush,
            boolean allowForcePush,
            boolean allowDeletion,
            boolean administratorBypass
    ) {
        BranchPolicy {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException("Approval requirement cannot be negative.");
            }
            eligibleReviewers = Set.copyOf(eligibleReviewers);
            requiredChecks = Set.copyOf(requiredChecks);

            if (requiredApprovals > eligibleReviewers.size()) {
                throw new IllegalArgumentException(
                    "Approval requirement exceeds eligible reviewer count."
                );
            }
        }
    }

    record MergeDecision(
            boolean eligible,
            Set<String> approvers,
            List<String> blockers
    ) {
        MergeDecision {
            approvers = Set.copyOf(approvers);
            blockers = List.copyOf(blockers);
        }
    }

    static final class FrequencyIndex<K> {
        private final Map<K, Integer> counts = new HashMap<>();

        void record(K value) {
            counts.merge(value, 1, Integer::sum);
        }

        int count(K value) {
            return counts.getOrDefault(value, 0);
        }

        Set<K> duplicatedValues() {
            return counts.entrySet().stream()
                    .filter(entry -> entry.getValue() > 1)
                    .map(Map.Entry::getKey)
                    .collect(Collectors.toCollection(LinkedHashSet::new));
        }

        Map<K, Integer> snapshot() {
            return Map.copyOf(counts);
        }
    }

    static final class MergeEligibilityService {
        MergeDecision evaluate(
                PullRequest pullRequest,
                BranchPolicy policy,
                MergeStrategy strategy,
                boolean commitsSatisfyLinearHistory
        ) {
            List<String> blockers = new ArrayList<>();

            if (!pullRequest.targetBranch().equals(policy.branch())) {
                blockers.add("Pull request targets a different branch.");
            }

            if (pullRequest.state() != PullRequestState.OPEN) {
                blockers.add("Pull request must be open and ready for review.");
            }

            if (pullRequest.hasConflicts()) {
                blockers.add("Merge conflicts remain unresolved.");
            }

            if (policy.requireResolvedConversations()
                    && !pullRequest.conversationsResolved()) {
                blockers.add("Review conversations are unresolved.");
            }

            if (policy.requireLinearHistory()
                    && (!commitsSatisfyLinearHistory
                    || strategy == MergeStrategy.MERGE_COMMIT)) {
                blockers.add("Selected merge strategy violates linear-history policy.");
            }

            // LinkedHashMap records each reviewer's latest submitted decision.
            // Approval of an old commit becomes stale when the PR head changes.
            Map<String, Review> latestReviews = new LinkedHashMap<>();
            for (Review review : pullRequest.reviews()) {
                latestReviews.put(review.reviewer(), review);
            }

            Set<String> effectiveApprovers = new TreeSet<>();

            for (Review review : latestReviews.values()) {
                if (review.state() == ReviewState.APPROVED
                        && policy.eligibleReviewers().contains(review.reviewer())
                        && review.commitId().equals(pullRequest.headCommit())) {
                    effectiveApprovers.add(review.reviewer());
                }
            }

            if (effectiveApprovers.size() < policy.requiredApprovals()) {
                blockers.add(
                    "Effective approvals: " + effectiveApprovers.size()
                    + "; required: " + policy.requiredApprovals() + "."
                );
            }

            // A later result for a named check replaces its earlier result.
            Map<String, StatusCheck> latestChecks = new HashMap<>();
            for (StatusCheck check : pullRequest.checks()) {
                latestChecks.put(check.name(), check);
            }

            for (String required : policy.requiredChecks()) {
                StatusCheck check = latestChecks.get(required);

                if (check == null) {
                    blockers.add("Missing required check: " + required + ".");
                } else if (!check.passed()) {
                    blockers.add("Failed required check: " + required + ".");
                } else if (!check.commitId().equals(pullRequest.headCommit())) {
                    blockers.add("Required check is stale: " + required + ".");
                }
            }

            return new MergeDecision(
                blockers.isEmpty(),
                effectiveApprovers,
                blockers
            );
        }
    }

    static void printDecision(PullRequest pr, MergeDecision decision) {
        System.out.println("\nPull Request #" + pr.id() + " "
                + pr.sourceBranch() + " -> " + pr.targetBranch());
        System.out.println("Effective approvers: " + decision.approvers());
        System.out.println("Merge eligible: " + decision.eligible());

        for (String blocker : decision.blockers()) {
            System.out.println("  - " + blocker);
        }
    }

    public static void main(String[] args) {
        FrequencyIndex<String> changedFiles = new FrequencyIndex<>();
        changedFiles.record("src/security/TokenService.java");
        changedFiles.record("src/api/SessionController.java");
        changedFiles.record("src/security/TokenService.java");

        System.out.println("Changed-file frequencies: " + changedFiles.snapshot());
        System.out.println("Repeated file paths: " + changedFiles.duplicatedValues());

        Set<String> securityTeam = Set.of("Mira", "Dev", "Anika");
        Set<String> platformTeam = Set.of("Anika", "Rohan", "Mira");

        Set<String> sharedReviewers = new TreeSet<>(securityTeam);
        sharedReviewers.retainAll(platformTeam);

        Set<String> allReviewers = new TreeSet<>(securityTeam);
        allReviewers.addAll(platformTeam);

        System.out.println("\nShared reviewers: " + sharedReviewers);
        System.out.println("Combined reviewer pool: " + allReviewers);

        BranchPolicy policy = new BranchPolicy(
            "main",
            2,
            Set.of("Mira", "Dev", "Anika", "Rohan"),
            Set.of("build", "unit-tests", "security-scan"),
            true,
            true,
            false,
            false,
            false,
            false
        );

        PullRequest ready = new PullRequest(
            91,
            "feature/token-hardening",
            "main",
            PullRequestState.OPEN,
            "commit-b7",
            false,
            true,
            List.of(
                new Review("Mira", ReviewState.APPROVED, "commit-b7"),
                new Review("Dev", ReviewState.APPROVED, "commit-b7"),
                new Review("Anika", ReviewState.COMMENTED, "commit-b7")
            ),
            List.of(
                new StatusCheck("build", true, "commit-b7"),
                new StatusCheck("unit-tests", true, "commit-b7"),
                new StatusCheck("security-scan", true, "commit-b7")
            )
        );

        PullRequest stale = new PullRequest(
            92,
            "feature/session-fix",
            "main",
            PullRequestState.OPEN,
            "commit-c9",
            false,
            true,
            List.of(
                new Review("Mira", ReviewState.APPROVED, "commit-c8"),
                new Review("Dev", ReviewState.APPROVED, "commit-c9")
            ),
            List.of(
                new StatusCheck("build", true, "commit-c9"),
                new StatusCheck("unit-tests", true, "commit-c9"),
                new StatusCheck("security-scan", true, "commit-c9")
            )
        );

        MergeEligibilityService service = new MergeEligibilityService();

        printDecision(
            ready,
            service.evaluate(ready, policy, MergeStrategy.SQUASH, true)
        );

        printDecision(
            stale,
            service.evaluate(stale, policy, MergeStrategy.SQUASH, true)
        );

        // Direct pushes, force pushes, branch deletion, and bypass privileges
        // are repository controls distinct from the merge decision itself.
        System.out.println("\nProtected branch: " + policy.branch());
        System.out.println("Direct pushes allowed: " + policy.allowDirectPush());
        System.out.println("Force pushes allowed: " + policy.allowForcePush());
        System.out.println("Branch deletion allowed: " + policy.allowDeletion());
        System.out.println("Administrator bypass enabled: " + policy.administratorBypass());

        EnumMap<ReviewState, Integer> reviewDistribution =
                new EnumMap<>(ReviewState.class);

        for (ReviewState state : ReviewState.values()) {
            reviewDistribution.put(state, 0);
        }

        for (Review review : ready.reviews()) {
            reviewDistribution.merge(review.state(), 1, Integer::sum);
        }

        System.out.println("Review-state distribution: " + reviewDistribution);

        try {
            new BranchPolicy(
                "release",
                3,
                Set.of("Mira", "Dev"),
                Set.of("build"),
                true,
                true,
                false,
                false,
                false,
                false
            );
        } catch (IllegalArgumentException exception) {
            System.out.println("Invalid policy rejected: " + exception.getMessage());
        }
    }
}
