import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class Main {
    public record Analysis(long target, boolean exists, long count,
                           long totalSubsequences) {}

    public enum ReviewState {
        PENDING, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    public static final class SubsequenceException extends RuntimeException {
        public SubsequenceException(String message) {
            super(message);
        }
    }

    public static final class SubsequenceService {
        public List<List<Integer>> generate(List<Integer> values) {
            validate(values);

            if (values.size() >= 31) {
                throw new SubsequenceException(
                    "Materializing more than 2^30 subsequences is not supported."
                );
            }

            List<List<Integer>> result = new ArrayList<>();
            generateAt(values, 0, new ArrayList<>(), result);
            return Collections.unmodifiableList(result);
        }

        private void generateAt(List<Integer> values, int index,
                                List<Integer> current,
                                List<List<Integer>> result) {
            if (index == values.size()) {
                result.add(List.copyOf(current));
                return;
            }

            generateAt(values, index + 1, current, result);

            current.add(values.get(index));
            generateAt(values, index + 1, current, result);
            current.remove(current.size() - 1);
        }

        public Map<Long, Long> sumCounts(List<Integer> values) {
            validate(values);
            Map<Long, Long> counts = new HashMap<>();
            counts.put(0L, 1L);

            for (int value : values) {
                Map<Long, Long> updated = new HashMap<>(counts);
                for (Map.Entry<Long, Long> entry : counts.entrySet()) {
                    long next;
                    try {
                        next = Math.addExact(entry.getKey(), value);
                        updated.merge(next, entry.getValue(), Math::addExact);
                    } catch (ArithmeticException exception) {
                        throw new SubsequenceException(
                            "Sum or count overflow."
                        );
                    }
                }
                counts = updated;
            }

            return Collections.unmodifiableMap(counts);
        }

        public Analysis analyze(List<Integer> values, long target) {
            Map<Long, Long> counts = sumCounts(values);
            long count = counts.getOrDefault(target, 0L);
            long total;

            try {
                total = 1L << values.size();
                if (values.size() >= 63) {
                    throw new ArithmeticException("Subsequence count overflow.");
                }
            } catch (ArithmeticException exception) {
                throw new SubsequenceException(
                    "Total subsequences cannot be represented as a long."
                );
            }

            return new Analysis(target, count > 0, count, total);
        }

        private void validate(List<Integer> values) {
            Objects.requireNonNull(values, "Input list is required.");
            for (Integer value : values) {
                if (value == null) {
                    throw new SubsequenceException(
                        "Input elements cannot be null."
                    );
                }
            }
        }
    }

    public record RepositoryPolicy(
        boolean requireChecks,
        boolean requireApproval,
        int minimumApprovals
    ) {
        public RepositoryPolicy {
            if (minimumApprovals < 0) {
                throw new IllegalArgumentException(
                    "Minimum approvals cannot be negative."
                );
            }
            if (requireApproval && minimumApprovals == 0) {
                throw new IllegalArgumentException(
                    "Approval policy requires at least one approval."
                );
            }
        }
    }

    public record PullRequest(
        String id,
        List<Integer> changes,
        long requiredChangeSum,
        boolean checksPassed,
        ReviewState reviewState
    ) {
        public PullRequest {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Pull request ID is required.");
            }
            changes = List.copyOf(changes);
            Objects.requireNonNull(reviewState, "Review state is required.");
        }
    }

    public static final class MergeEligibilityService {
        private final SubsequenceService subsequences;

        public MergeEligibilityService(SubsequenceService subsequences) {
            this.subsequences = Objects.requireNonNull(subsequences);
        }

        public boolean isEligible(PullRequest request, RepositoryPolicy policy) {
            Objects.requireNonNull(request);
            Objects.requireNonNull(policy);

            if (policy.requireChecks() && !request.checksPassed()) {
                return false;
            }

            if (policy.requireApproval() &&
                request.reviewState() != ReviewState.APPROVED) {
                return false;
            }

            return subsequences.analyze(
                request.changes(), request.requiredChangeSum()
            ).exists();
        }
    }

    public static void main(String[] args) {
        SubsequenceService service = new SubsequenceService();

        System.out.println("Subsequences:");
        service.generate(List.of(1, 2, 3)).forEach(System.out::println);

        System.out.println("Target sum analysis:");
        System.out.println(service.analyze(List.of(1, 2, 3), 3));
        System.out.println(service.analyze(List.of(0, 0), 0));

        RepositoryPolicy policy = new RepositoryPolicy(true, true, 1);
        MergeEligibilityService eligibility =
            new MergeEligibilityService(service);

        PullRequest approved = new PullRequest(
            "PR-201", List.of(1, 2, 3), 3, true, ReviewState.APPROVED
        );
        PullRequest changesRequested = new PullRequest(
            "PR-202", List.of(1, 2, 3), 3, true,
            ReviewState.CHANGES_REQUESTED
        );

        System.out.println(
            approved.id() + " eligible: " +
            eligibility.isEligible(approved, policy)
        );
        System.out.println(
            changesRequested.id() + " eligible: " +
            eligibility.isEligible(changesRequested, policy)
        );

        if (service.analyze(List.of(), 0).count() != 1) {
            throw new IllegalStateException("Empty-input test failed.");
        }
        if (service.analyze(List.of(1, 2, 3), 3).count() != 2) {
            throw new IllegalStateException("Counting test failed.");
        }
    }
}
