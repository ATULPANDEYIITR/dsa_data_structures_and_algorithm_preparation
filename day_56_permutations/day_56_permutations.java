import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class PermutationPractice {

    enum GenerationMethod {
        USED_ARRAY,
        SWAP
    }

    record PermutationReport(
            GenerationMethod method,
            int inputSize,
            long expectedCount,
            int generatedCount
    ) {}

    static class PermutationException extends RuntimeException {
        PermutationException(String message) {
            super(message);
        }
    }

    interface PermutationGenerator {
        List<List<String>> generate(List<String> input);
    }

    static final class UsedArrayGenerator implements PermutationGenerator {

        @Override
        public List<List<String>> generate(List<String> input) {
            validate(input);

            List<String> values = new ArrayList<>(input);
            Collections.sort(values);

            boolean[] used = new boolean[values.size()];
            List<String> current = new ArrayList<>();
            List<List<String>> result = new ArrayList<>();

            backtrack(values, used, current, result);
            return result;
        }

        private void backtrack(
                List<String> values,
                boolean[] used,
                List<String> current,
                List<List<String>> result
        ) {
            if (current.size() == values.size()) {
                result.add(List.copyOf(current));
                return;
            }

            Set<String> usedAtLevel = new HashSet<>();

            for (int i = 0; i < values.size(); i++) {
                if (used[i] || !usedAtLevel.add(values.get(i))) {
                    continue;
                }

                used[i] = true;
                current.add(values.get(i));

                backtrack(values, used, current, result);

                current.remove(current.size() - 1);
                used[i] = false;
            }
        }
    }

    static final class SwapGenerator implements PermutationGenerator {

        @Override
        public List<List<String>> generate(List<String> input) {
            validate(input);

            List<String> values = new ArrayList<>(input);
            Collections.sort(values);

            List<List<String>> result = new ArrayList<>();
            backtrack(values, 0, result);
            return result;
        }

        private void backtrack(
                List<String> values,
                int start,
                List<List<String>> result
        ) {
            if (start == values.size()) {
                result.add(List.copyOf(values));
                return;
            }

            Set<String> usedAtLevel = new HashSet<>();

            for (int i = start; i < values.size(); i++) {
                if (!usedAtLevel.add(values.get(i))) {
                    continue;
                }

                Collections.swap(values, start, i);

                backtrack(values, start + 1, result);

                Collections.swap(values, start, i);
            }
        }
    }

    static final class PermutationService {

        private static final int MAX_INPUT_SIZE = 9;

        private final List<PermutationGenerator> generators = List.of(
                new UsedArrayGenerator(),
                new SwapGenerator()
        );

        List<PermutationReport> evaluate(List<String> input) {
            validate(input);

            long expected = uniquePermutationCount(input);
            List<PermutationReport> reports = new ArrayList<>();

            for (PermutationGenerator generator : generators) {
                List<List<String>> permutations = generator.generate(input);

                validateResult(permutations, expected);

                GenerationMethod method =
                        generator instanceof SwapGenerator
                                ? GenerationMethod.SWAP
                                : GenerationMethod.USED_ARRAY;

                reports.add(new PermutationReport(
                        method,
                        input.size(),
                        expected,
                        permutations.size()
                ));
            }

            return reports;
        }

        private static long uniquePermutationCount(List<String> input) {
            validate(input);

            List<String> sorted = new ArrayList<>(input);
            Collections.sort(sorted);

            long result = factorial(sorted.size());

            for (int i = 0; i < sorted.size();) {
                int j = i + 1;

                while (j < sorted.size()
                        && sorted.get(j).equals(sorted.get(i))) {
                    j++;
                }

                result /= factorial(j - i);
                i = j;
            }

            return result;
        }

        private static long factorial(int n) {
            long result = 1;

            for (int i = 2; i <= n; i++) {
                if (result > Long.MAX_VALUE / i) {
                    throw new PermutationException(
                            "Permutation count exceeds long range."
                    );
                }
                result *= i;
            }

            return result;
        }

        private static void validate(List<String> input) {
            if (input == null) {
                throw new PermutationException("Input must not be null.");
            }

            if (input.size() > MAX_INPUT_SIZE) {
                throw new PermutationException(
                        "Input size cannot exceed " + MAX_INPUT_SIZE + "."
                );
            }

            for (String value : input) {
                if (value == null) {
                    throw new PermutationException(
                            "Null values are not supported."
                    );
                }
            }
        }

        private static void validateResult(
                List<List<String>> permutations,
                long expected
        ) {
            if (permutations.size() != expected) {
                throw new PermutationException(
                        "Generated count does not match expected count."
                );
            }

            Set<List<String>> unique = new HashSet<>(permutations);

            if (unique.size() != expected) {
                throw new PermutationException(
                        "Duplicate permutations were generated."
                );
            }
        }
    }

    private static void printReports(List<PermutationReport> reports) {
        for (PermutationReport report : reports) {
            System.out.printf(
                    "%s: inputSize=%d, expected=%d, generated=%d%n",
                    report.method(),
                    report.inputSize(),
                    report.expectedCount(),
                    report.generatedCount()
            );
        }
    }

    public static void main(String[] args) {
        PermutationService service = new PermutationService();

        List<List<String>> examples = List.of(
                List.of("A", "B", "C"),
                List.of("A", "A", "B"),
                List.of("1", "2", "3", "4")
        );

        for (List<String> input : examples) {
            System.out.println("\nInput: " + input);

            List<PermutationReport> reports = service.evaluate(input);
            printReports(reports);
        }

        System.out.println("\nEmpty input:");
        List<PermutationReport> emptyReport =
                service.evaluate(Collections.emptyList());
        printReports(emptyReport);

        System.out.println("\nFailure state:");

        try {
            service.evaluate(List.of(
                    "1", "2", "3", "4", "5",
                    "6", "7", "8", "9", "10"
            ));
        } catch (PermutationException exception) {
            System.out.println("Rejected correctly: "
                    + exception.getMessage());
        }

        System.out.println("\nDesign characteristics:");
        System.out.println(
                "Used-array generation makes selection state explicit."
        );
        System.out.println(
                "Swap generation reduces auxiliary selection storage."
        );
        System.out.println(
                "Duplicate values are skipped once per recursion depth."
        );
        System.out.println(
                "Exhaustive generation has O(n * n!) output complexity."
        );
    }
}
