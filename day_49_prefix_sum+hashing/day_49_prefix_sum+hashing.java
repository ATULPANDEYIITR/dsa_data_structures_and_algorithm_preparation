import java.util.*;

public class PrefixHashingGovernance {

    static long countSubarraySum(int[] values, long target) {
        Map<Long, Long> frequency = new HashMap<>();
        frequency.put(0L, 1L);

        long prefix = 0;
        long result = 0;

        for (int value : values) {
            prefix += value;
            result += frequency.getOrDefault(prefix - target, 0L);
            frequency.merge(prefix, 1L, Long::sum);
        }

        return result;
    }

    static long countZeroSum(int[] values) {
        return countSubarraySum(values, 0);
    }

    static long countEqualBinary(int[] values) {
        Map<Integer, Long> frequency = new HashMap<>();
        frequency.put(0, 1L);

        int balance = 0;
        long result = 0;

        for (int value : values) {
            if (value != 0 && value != 1) {
                throw new IllegalArgumentException(
                    "Equal-binary-frequency analysis accepts only 0 and 1."
                );
            }

            balance += value == 1 ? 1 : -1;
            result += frequency.getOrDefault(balance, 0L);
            frequency.merge(balance, 1L, Long::sum);
        }

        return result;
    }

    record FrequencyState(List<Integer> differences) {
        FrequencyState {
            differences = List.copyOf(differences);
        }
    }

    static long countEqualFrequency(
        List<String> values,
        List<String> symbols
    ) {
        if (symbols.size() < 2 || new HashSet<>(symbols).size() != symbols.size()) {
            throw new IllegalArgumentException("Symbols must be distinct and contain at least two values.");
        }

        String reference = symbols.get(symbols.size() - 1);
        int[] differences = new int[symbols.size() - 1];

        Map<FrequencyState, Long> frequency = new HashMap<>();
        frequency.put(new FrequencyState(toList(differences)), 1L);

        long result = 0;

        for (String value : values) {
            int symbolIndex = symbols.indexOf(value);
            if (symbolIndex < 0) {
                throw new IllegalArgumentException("Unexpected symbol: " + value);
            }

            if (value.equals(reference)) {
                for (int i = 0; i < differences.length; i++) {
                    differences[i]--;
                }
            } else {
                differences[symbolIndex]++;
            }

            FrequencyState state =
                new FrequencyState(toList(differences));

            result += frequency.getOrDefault(state, 0L);
            frequency.merge(state, 1L, Long::sum);
        }

        return result;
    }

    private static List<Integer> toList(int[] values) {
        List<Integer> result = new ArrayList<>(values.length);
        for (int value : values) {
            result.add(value);
        }
        return result;
    }

    enum ReviewState {
        COMMENTED,
        APPROVED,
        CHANGES_REQUESTED
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        CLOSED,
        MERGED
    }

    record Review(String reviewer, ReviewState state, String commitId) {}

    record BranchProtectionPolicy(
        int requiredApprovals,
        Set<String> requiredStatusChecks,
        boolean requireConversationResolution,
        boolean allowDirectPush,
        boolean allowForcePush
    ) {}

    static final class PullRequest {
        private final int number;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, Boolean> statusChecks = new HashMap<>();

        private PullRequestState state;
        private String headCommit;
        private String baseCommit;
        private boolean mergeConflict;
        private int unresolvedConversations;

        PullRequest(
            int number,
            String sourceBranch,
            String targetBranch,
            String baseCommit,
            String headCommit
        ) {
            this.number = number;
            this.sourceBranch = Objects.requireNonNull(sourceBranch);
            this.targetBranch = Objects.requireNonNull(targetBranch);
            this.baseCommit = Objects.requireNonNull(baseCommit);
            this.headCommit = Objects.requireNonNull(headCommit);
            this.state = PullRequestState.DRAFT;
        }

        void markReadyForReview() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Only a draft Pull Request can become ready for review.");
            }
            state = PullRequestState.OPEN;
        }

        void updateHead(String newCommit) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Only open Pull Requests can receive updates.");
            }

            headCommit = Objects.requireNonNull(newCommit);

            // New commits can invalidate an earlier review because the reviewer
            // approved an older snapshot of the proposed change.
            reviews.replaceAll(review ->
                new Review(review.reviewer(), review.state(), headCommit)
            );
        }

        void synchronizeBase(String newBaseCommit, boolean conflict) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Base synchronization requires an open Pull Request.");
            }

            baseCommit = Objects.requireNonNull(newBaseCommit);
            mergeConflict = conflict;
        }

        void resolveConflict() {
            if (!mergeConflict) {
                return;
            }
            mergeConflict = false;
        }

        void addReview(Review review) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Reviews require an open Pull Request.");
            }
            reviews.add(Objects.requireNonNull(review));
        }

        void setStatusCheck(String name, boolean passed) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Status checks belong to an active Pull Request.");
            }
            statusChecks.put(Objects.requireNonNull(name), passed);
        }

        void setUnresolvedConversations(int count) {
            if (count < 0) {
                throw new IllegalArgumentException("Conversation count cannot be negative.");
            }
            unresolvedConversations = count;
        }

        boolean mergeEligible(BranchProtectionPolicy policy) {
            if (state != PullRequestState.OPEN || mergeConflict) {
                return false;
            }

            if (policy.requireConversationResolution && unresolvedConversations > 0) {
                return false;
            }

            Set<String> approvedReviewers = new HashSet<>();

            for (Review review : reviews) {
                // Approval is evaluated against the current head commit.
                // An approval for a different commit does not satisfy the policy.
                if (review.state() == ReviewState.APPROVED
                    && review.commitId().equals(headCommit)) {
                    approvedReviewers.add(review.reviewer());
                }
            }

            if (approvedReviewers.size() < policy.requiredApprovals) {
                return false;
            }

            for (String check : policy.requiredStatusChecks) {
                if (!Boolean.TRUE.equals(statusChecks.get(check))) {
                    return false;
                }
            }

            return true;
        }

        void merge(BranchProtectionPolicy policy) {
            if (!mergeEligible(policy)) {
                throw new IllegalStateException(
                    "Pull Request does not satisfy branch protection requirements."
                );
            }

            state = PullRequestState.MERGED;
        }

        String describe() {
            return "PR #" + number
                + " " + sourceBranch
                + " -> " + targetBranch
                + " [" + state + "]"
                + " head=" + headCommit
                + " base=" + baseCommit;
        }
    }

    static final class RepositoryGovernanceService {
        private final BranchProtectionPolicy policy;

        RepositoryGovernanceService(BranchProtectionPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        boolean canDirectPush(String branch) {
            return !branch.equals("main") || policy.allowDirectPush();
        }

        boolean canForcePush(String branch) {
            return !branch.equals("main") || policy.allowForcePush();
        }

        void merge(PullRequest pullRequest) {
            pullRequest.merge(policy);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Prefix Sum + Hashing ===");

        int[] values = {3, -1, -2, 4, -4, 2};
        System.out.println("Subarrays summing to 0: " + countZeroSum(values));
        System.out.println("Subarrays summing to 2: " + countSubarraySum(values, 2));

        int[] binary = {0, 1, 0, 1, 1, 0};
        System.out.println("Equal 0/1 subarrays: " + countEqualBinary(binary));

        List<String> symbols = List.of("A", "B", "A", "C", "B", "C", "A", "B", "C");
        System.out.println(
            "Equal A/B/C frequency subarrays: "
            + countEqualFrequency(symbols, List.of("A", "B", "C"))
        );

        System.out.println("\n=== Enterprise Repository Governance ===");

        BranchProtectionPolicy policy = new BranchProtectionPolicy(
            2,
            Set.of("unit-tests", "security-scan"),
            true,
            false,
            false
        );

        RepositoryGovernanceService service =
            new RepositoryGovernanceService(policy);

        PullRequest pullRequest = new PullRequest(
            73,
            "feature/prefix-state",
            "main",
            "main-184",
            "feature-229"
        );

        pullRequest.markReadyForReview();

        pullRequest.addReview(
            new Review("reviewer-a", ReviewState.APPROVED, "feature-229")
        );
        pullRequest.addReview(
            new Review("reviewer-b", ReviewState.APPROVED, "feature-229")
        );

        pullRequest.setStatusCheck("unit-tests", true);
        pullRequest.setStatusCheck("security-scan", true);
        pullRequest.setUnresolvedConversations(0);

        System.out.println(pullRequest.describe());
        System.out.println("Direct push to main: " + service.canDirectPush("main"));
        System.out.println("Force push to main: " + service.canForcePush("main"));
        System.out.println("Merge eligible: " + pullRequest.mergeEligible(policy));

        service.merge(pullRequest);
        System.out.println(pullRequest.describe());
    }
}
