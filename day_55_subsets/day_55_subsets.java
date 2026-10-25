import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.function.Predicate;

public class Main {
    public record SubsetResult(List<Integer> values, long sum) {
        public SubsetResult {
            values = List.copyOf(values);
        }
    }

    public record SizeConstraint(int minimum, int maximum) {
        public SizeConstraint {
            if (minimum < 0 || maximum < minimum) {
                throw new IllegalArgumentException("Invalid size constraint.");
            }
        }

        public boolean accepts(int size) {
            return size >= minimum && size <= maximum;
        }
    }

    public record SumConstraint(Long minimum, Long maximum) {
        public SumConstraint {
            if (minimum != null && maximum != null && minimum > maximum) {
                throw new IllegalArgumentException("Minimum sum exceeds maximum.");
            }
        }

        public boolean accepts(long sum) {
            return (minimum == null || sum >= minimum)
                && (maximum == null || sum <= maximum);
        }
    }

    public static final class SubsetService {
        public List<List<Integer>> generate(List<Integer> input) {
            validate(input);

            List<List<Integer>> result = new ArrayList<>();
            result.add(new ArrayList<>());

            for (int value : input) {
                int previousSize = result.size();

                for (int i = 0; i < previousSize; i++) {
                    List<Integer> next = new ArrayList<>(result.get(i));
                    next.add(value);
                    result.add(next);
                }
            }

            return immutableNested(result);
        }

        public List<List<Integer>> uniqueSubsets(List<Integer> input) {
            validate(input);

            List<Integer> sorted = new ArrayList<>(input);
            Collections.sort(sorted);

            List<List<Integer>> result = new ArrayList<>();
            backtrackUnique(sorted, 0, new ArrayList<>(), result);
            return immutableNested(result);
        }

        private void backtrackUnique(
            List<Integer> values,
            int start,
            List<Integer> path,
            List<List<Integer>> result
        ) {
            result.add(new ArrayList<>(path));

            for (int i = start; i < values.size(); i++) {
                if (i > start && values.get(i).equals(values.get(i - 1))) {
                    continue;
                }

                path.add(values.get(i));
                backtrackUnique(values, i + 1, path, result);
                path.remove(path.size() - 1);
            }
        }

        public List<List<Integer>> subsetSum(List<Integer> input, long target) {
            validate(input);

            List<Integer> sorted = new ArrayList<>(input);
            Collections.sort(sorted);

            List<List<Integer>> result = new ArrayList<>();
            searchSum(sorted, 0, target, new ArrayList<>(), result);
            return immutableNested(result);
        }

        private void searchSum(
            List<Integer> values,
            int start,
            long remaining,
            List<Integer> path,
            List<List<Integer>> result
        ) {
            if (remaining == 0) {
                result.add(new ArrayList<>(path));
            }

            for (int i = start; i < values.size(); i++) {
                if (i > start && values.get(i).equals(values.get(i - 1))) {
                    continue;
                }

                path.add(values.get(i));
                searchSum(
                    values,
                    i + 1,
                    Math.subtractExact(remaining, values.get(i)),
                    path,
                    result
                );
                path.remove(path.size() - 1);
            }
        }

        public List<SubsetResult> constrained(
            List<Integer> input,
            SizeConstraint sizeConstraint,
            SumConstraint sumConstraint,
            Predicate<List<Integer>> policy
        ) {
            validate(input);
            Objects.requireNonNull(sizeConstraint);
            Objects.requireNonNull(sumConstraint);
            Objects.requireNonNull(policy);

            if (sizeConstraint.maximum() > input.size()) {
                throw new IllegalArgumentException(
                    "Maximum size exceeds the number of input elements."
                );
            }

            List<SubsetResult> result = new ArrayList<>();
            constrainedSearch(
                input, 0, 0L, new ArrayList<>(),
                sizeConstraint, sumConstraint, policy, result
            );

            return List.copyOf(result);
        }

        private void constrainedSearch(
            List<Integer> values,
            int index,
            long sum,
            List<Integer> path,
            SizeConstraint sizeConstraint,
            SumConstraint sumConstraint,
            Predicate<List<Integer>> policy,
            List<SubsetResult> result
        ) {
            if (path.size() > sizeConstraint.maximum()) return;

            if (index == values.size()) {
                if (sizeConstraint.accepts(path.size())
                    && sumConstraint.accepts(sum)) {
                    List<Integer> candidate = List.copyOf(path);
                    if (policy.test(candidate)) {
                        result.add(new SubsetResult(candidate, sum));
                    }
                }
                return;
            }

            constrainedSearch(
                values, index + 1, sum, path,
                sizeConstraint, sumConstraint, policy, result
            );

            path.add(values.get(index));
            constrainedSearch(
                values, index + 1,
                Math.addExact(sum, values.get(index)), path,
                sizeConstraint, sumConstraint, policy, result
            );
            path.remove(path.size() - 1);
        }

        public boolean subsetSumExists(List<Integer> input, long target) {
            validate(input);

            Set<Long> reachable = new HashSet<>();
            reachable.add(0L);

            for (int value : input) {
                Set<Long> next = new HashSet<>(reachable);

                for (long sum : reachable) {
                    next.add(Math.addExact(sum, value));
                }

                reachable = next;
            }

            return reachable.contains(target);
        }

        private void validate(List<Integer> input) {
            Objects.requireNonNull(input, "Input cannot be null.");
            if (input.stream().anyMatch(Objects::isNull)) {
                throw new IllegalArgumentException("Input cannot contain null.");
            }
        }

        private List<List<Integer>> immutableNested(List<List<Integer>> input) {
            return input.stream().map(List::copyOf).toList();
        }
    }

    public static void main(String[] args) {
        SubsetService service = new SubsetService();
        List<Integer> values = Arrays.asList(1, 2, 2, 3);

        System.out.println("All subsets:");
        service.generate(values).forEach(System.out::println);

        System.out.println("\nUnique subsets:");
        service.uniqueSubsets(values).forEach(System.out::println);

        System.out.println("\nSubsets summing to 4:");
        service.subsetSum(values, 4).forEach(System.out::println);

        System.out.println("\nPolicy-constrained subsets:");
        service.constrained(
            values,
            new SizeConstraint(2, 3),
            new SumConstraint(4L, 6L),
            subset -> subset.stream().mapToInt(Integer::intValue).sum() % 2 == 0
        ).forEach(System.out::println);

        System.out.println(
            "\nTarget 7 reachable: " + service.subsetSumExists(values, 7)
        );

        if (service.uniqueSubsets(List.of(1, 1)).size() != 3) {
            throw new IllegalStateException("Duplicate handling test failed.");
        }

        if (!service.subsetSum(List.of(0, 0), 0).equals(
            List.of(List.of(), List.of(0), List.of(0, 0)))) {
            throw new IllegalStateException("Zero-sum enumeration test failed.");
        }

        System.out.println("All checks passed.");
    }
}
