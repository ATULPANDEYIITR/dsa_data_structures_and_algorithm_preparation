import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class CombinationGovernanceApp {

    enum Decision {
        CHOOSE,
        SKIP
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        CHANGES_REQUESTED,
        APPROVED,
        MERGED,
        CLOSED
    }

    record PullRequest(
        String id,
        String sourceBranch,
        String targetBranch,
        List<Integer> changedComponents,
        int riskScore,
        PullRequestState state
    ) {
        PullRequest {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("id is required");
            }
            if (sourceBranch == null || sourceBranch.isBlank()) {
                throw new IllegalArgumentException("source branch is required");
            }
            if (targetBranch == null || targetBranch.isBlank()) {
                throw new IllegalArgumentException("target branch is required");
            }
            if (riskScore < 0 || riskScore > 100) {
                throw new IllegalArgumentException(
                    "riskScore must be between 0 and 100"
                );
            }

            changedComponents = List.copyOf(changedComponents);
        }
    }

    record Review(
        String reviewer,
        Decision decision,
        boolean eligible
    ) {}

    record ApprovalPolicy(
        int requiredApprovals,
        int maximumRisk,
        boolean requirePassingChecks,
        boolean forbidSelfApproval
    ) {
        ApprovalPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "requiredApprovals cannot be negative"
                );
            }
            if (maximumRisk < 0 || maximumRisk > 100) {
                throw new IllegalArgumentException(
                    "maximumRisk must be between 0 and 100"
                );
            }
        }
    }

    record StatusCheck(String name, boolean passed) {}

    static final class InvalidTransitionException
        extends RuntimeException {

        InvalidTransitionException(String message) {
            super(message);
        }
    }

    static final class CombinationService {
        private final List<Integer> candidates;
        private final Map<String, List<List<Integer>>> cache =
            new HashMap<>();

        CombinationService(List<Integer> candidates) {
            if (candidates == null || candidates.isEmpty()) {
                throw new IllegalArgumentException(
                    "candidates cannot be empty"
                );
            }

            if (candidates.stream().anyMatch(value -> value <= 0)) {
                throw new IllegalArgumentException(
                    "candidates must be positive"
                );
            }

            this.candidates = candidates.stream()
                .distinct()
                .sorted()
                .toList();
        }

        List<List<Integer>> chooseOrSkip() {
            List<List<Integer>> result = new ArrayList<>();
            chooseOrSkip(0, new ArrayList<>(), result);
            return List.copyOf(result);
        }

        private void chooseOrSkip(
            int index,
            List<Integer> path,
            List<List<Integer>> result
        ) {
            if (index == candidates.size()) {
                result.add(List.copyOf(path));
                return;
            }

            path.add(candidates.get(index));
            chooseOrSkip(index + 1, path, result);
            path.remove(path.size() - 1);

            chooseOrSkip(index + 1, path, result);
        }

        List<List<Integer>> fixedSize(int size) {
            if (size < 0) {
                throw new IllegalArgumentException(
                    "size cannot be negative"
                );
            }

            if (size == 0) {
                return List.of(List.of());
            }

            if (size > candidates.size()) {
                return List.of();
            }

            List<List<Integer>> result = new ArrayList<>();
            fixedSize(0, size, new ArrayList<>(), result);
            return List.copyOf(result);
        }

        private void fixedSize(
            int start,
            int size,
            List<Integer> path,
            List<List<Integer>> result
        ) {
            if (path.size() == size) {
                result.add(List.copyOf(path));
                return;
            }

            int remaining = size - path.size();

            if (candidates.size() - start < remaining) {
                return;
            }

            for (int index = start; index < candidates.size(); index++) {
                path.add(candidates.get(index));
                fixedSize(index + 1, size, path, result);
                path.remove(path.size() - 1);
            }
        }

        List<List<Integer>> combinationSum(
            int target,
            boolean reuse
        ) {
            if (target < 0) {
                throw new IllegalArgumentException(
                    "target cannot be negative"
                );
            }

            String cacheKey = target + ":" + reuse;
            if (cache.containsKey(cacheKey)) {
                return cache.get(cacheKey);
            }

            List<List<Integer>> result = new ArrayList<>();
            combinationSum(
                0,
                target,
                reuse,
                new ArrayList<>(),
                result
            );

            List<List<Integer>> immutable = List.copyOf(result);
            cache.put(cacheKey, immutable);
            return immutable;
        }

        private void combinationSum(
            int start,
            int remaining,
            boolean reuse,
            List<Integer> path,
            List<List<Integer>> result
        ) {
            if (remaining == 0) {
                result.add(List.copyOf(path));
                return;
            }

            for (int index = start; index < candidates.size(); index++) {
                int value = candidates.get(index);

                if (value > remaining) {
                    break;
                }

                path.add(value);

                combinationSum(
                    reuse ? index : index + 1,
                    remaining - value,
                    reuse,
                    path,
                    result
                );

                path.remove(path.size() - 1);
            }
        }

        List<List<Integer>> constrained(
            int size,
            int minimum,
            int maximum
        ) {
            if (size < 0 || minimum > maximum) {
                throw new IllegalArgumentException(
                    "invalid constraints"
                );
            }

            List<List<Integer>> result = new ArrayList<>();

            if (size == 0) {
                if (minimum <= 0 && 0 <= maximum) {
                    return List.of(List.of());
                }
                return List.of();
            }

            constrained(
                0,
                size,
                0,
                minimum,
                maximum,
                new ArrayList<>(),
                result
            );

            return List.copyOf(result);
        }

        private void constrained(
            int start,
            int size,
            int currentSum,
            int minimum,
            int maximum,
            List<Integer> path,
            List<List<Integer>> result
        ) {
            int remaining = size - path.size();

            if (remaining == 0) {
                if (
                    currentSum >= minimum &&
                    currentSum <= maximum
                ) {
                    result.add(List.copyOf(path));
                }
                return;
            }

            if (candidates.size() - start < remaining) {
                return;
            }

            int lowerBound = 0;
            for (
                int index = start;
                index < start + remaining;
                index++
            ) {
                lowerBound += candidates.get(index);
            }

            if (currentSum + lowerBound > maximum) {
                return;
            }

            for (int index = start; index < candidates.size(); index++) {
                int nextSum =
                    currentSum + candidates.get(index);

                if (nextSum > maximum) {
                    break;
                }

                path.add(candidates.get(index));

                constrained(
                    index + 1,
                    size,
                    nextSum,
                    minimum,
                    maximum,
                    path,
                    result
                );

                path.remove(path.size() - 1);
            }
        }
    }

    static final class MergeEligibilityService {
        boolean eligible(
            PullRequest pullRequest,
            List<Review> reviews,
            List<StatusCheck> checks,
            ApprovalPolicy policy
        ) {
            if (
                pullRequest.state() == PullRequestState.DRAFT ||
                pullRequest.state() == PullRequestState.CLOSED ||
                pullRequest.state() == PullRequestState.MERGED
            ) {
                return false;
            }

            if (pullRequest.riskScore() > policy.maximumRisk()) {
                return false;
            }

            if (
                policy.requirePassingChecks() &&
                checks.stream().anyMatch(check -> !check.passed())
            ) {
                return false;
            }

            Set<String> eligibleApprovers = new HashSet<>();

            for (Review review : reviews) {
                if (
                    review.eligible() &&
                    review.decision() == Decision.CHOOSE
                ) {
                    eligibleApprovers.add(review.reviewer());
                }
            }

            return eligibleApprovers.size() >=
                policy.requiredApprovals();
        }
    }

    static void print(
        String title,
        List<List<Integer>> values
    ) {
        System.out.println(title);
        values.forEach(System.out::println);
    }

    public static void main(String[] args) {
        CombinationService service =
            new CombinationService(List.of(2, 3, 5, 7));

        print(
            "Choose/not choose:",
            service.chooseOrSkip()
        );

        print(
            "\nFixed-size combinations:",
            service.fixedSize(2)
        );

        print(
            "\nCombination sum without reuse:",
            service.combinationSum(10, false)
        );

        print(
            "\nCombination sum with reuse:",
            service.combinationSum(8, true)
        );

        print(
            "\nConstraint-based combinations:",
            service.constrained(3, 12, 18)
        );

        PullRequest pullRequest = new PullRequest(
            "PR-1042",
            "feature/combinations",
            "main",
            List.of(2, 3, 5),
            25,
            PullRequestState.OPEN
        );

        List<Review> reviews = List.of(
            new Review("reviewer-a", Decision.CHOOSE, true),
            new Review("reviewer-b", Decision.CHOOSE, true),
            new Review("author", Decision.CHOOSE, false)
        );

        List<StatusCheck> checks = List.of(
            new StatusCheck("unit-tests", true),
            new StatusCheck("static-analysis", true)
        );

        ApprovalPolicy policy = new ApprovalPolicy(
            2,
            50,
            true,
            true
        );

        MergeEligibilityService eligibility =
            new MergeEligibilityService();

        System.out.println(
            "\nMerge eligible: " +
            eligibility.eligible(
                pullRequest,
                reviews,
                checks,
                policy
            )
        );

        try {
            new CombinationService(List.of(1, 0, 2));
        } catch (IllegalArgumentException error) {
            System.out.println(
                "Validation failure: " + error.getMessage()
            );
        }

        /*
         * The recursive search has exponential worst-case behavior.
         * The sorted candidate list enables early stopping.
         * Cached target/reuse combinations avoid repeated identical
         * searches inside a longer enterprise workflow.
         */
    }
}
