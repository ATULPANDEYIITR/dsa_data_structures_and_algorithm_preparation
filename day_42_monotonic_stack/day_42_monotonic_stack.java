import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise case study: an observability platform evaluates metric streams
 * for the next strictly greater or smaller reading. It uses explicit domain
 * types, immutable results, policy configuration, and validation.
 *
 * Compile and run:
 *   javac MonotonicStackGovernance.java
 *   java MonotonicStackGovernance
 */
public class MonotonicStackGovernance {

    enum QueryDirection {
        NEXT_GREATER,
        NEXT_SMALLER
    }

    enum StackOrder {
        NON_DECREASING,
        NON_INCREASING
    }

    record Metric(String name, long timestamp, int value) {
        Metric {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Metric name must not be blank"
                );
            }
            if (timestamp < 0) {
                throw new IllegalArgumentException(
                    "Timestamp must not be negative"
                );
            }
        }
    }

    record Match(
        int sourceIndex,
        Metric source,
        Integer targetIndex,
        Metric target
    ) {
        Match {
            Objects.requireNonNull(source, "source");

            if ((targetIndex == null) != (target == null)) {
                throw new IllegalArgumentException(
                    "Target index and target metric must both be present "
                    + "or both be absent"
                );
            }

            if (targetIndex != null && targetIndex <= sourceIndex) {
                throw new IllegalArgumentException(
                    "Target must occur after the source"
                );
            }
        }

        boolean resolved() {
            return target != null;
        }
    }

    record QueryPolicy(
        QueryDirection direction,
        boolean strict,
        boolean circular
    ) {
        QueryPolicy {
            Objects.requireNonNull(direction, "direction");
        }
    }

    static final class MonotonicAnalyzer {

        /*
         * The stack contains unresolved positions. The comparator decides
         * which incoming value resolves the top position.
         */
        List<Match> analyze(
            List<Metric> metrics,
            QueryPolicy policy
        ) {
            Objects.requireNonNull(metrics, "metrics");
            Objects.requireNonNull(policy, "policy");

            List<Metric> input = List.copyOf(metrics);
            List<Match> results = new ArrayList<>(input.size());
            Integer[] targetIndices = new Integer[input.size()];
            Deque<Integer> unresolved = new ArrayDeque<>();

            int n = input.size();
            int iterations = policy.circular() ? 2 * n : n;

            for (int step = 0; step < iterations; step++) {
                int index = step % n;
                int current = input.get(index).value();

                while (!unresolved.isEmpty()) {
                    int previousIndex = unresolved.peekLast();
                    int previous = input.get(previousIndex).value();

                    boolean qualifies = qualifies(
                        previous, current, policy
                    );

                    if (!qualifies) {
                        break;
                    }

                    targetIndices[previousIndex] = index;
                    unresolved.removeLast();
                }

                if (step < n) {
                    unresolved.addLast(index);
                }
            }

            for (int i = 0; i < n; i++) {
                Integer targetIndex = targetIndices[i];
                Metric target = targetIndex == null
                    ? null
                    : input.get(targetIndex);

                results.add(new Match(
                    i,
                    input.get(i),
                    targetIndex,
                    target
                ));
            }

            return Collections.unmodifiableList(results);
        }

        private boolean qualifies(
            int previous,
            int current,
            QueryPolicy policy
        ) {
            if (policy.direction() == QueryDirection.NEXT_GREATER) {
                return policy.strict()
                    ? previous < current
                    : previous <= current;
            }

            return policy.strict()
                ? previous > current
                : previous >= current;
        }

        /*
         * Return a monotonic stack snapshot. This method is useful for
         * diagnostics because it exposes values without exposing a mutable
         * internal stack.
         */
        List<Integer> buildStack(
            List<Integer> values,
            StackOrder order
        ) {
            Objects.requireNonNull(values, "values");
            Objects.requireNonNull(order, "order");

            Deque<Integer> stack = new ArrayDeque<>();

            for (Integer value : values) {
                if (value == null) {
                    throw new IllegalArgumentException(
                        "Metric values must not be null"
                    );
                }

                if (order == StackOrder.NON_DECREASING) {
                    while (!stack.isEmpty() &&
                           stack.peekLast() > value) {
                        stack.removeLast();
                    }
                } else {
                    while (!stack.isEmpty() &&
                           stack.peekLast() < value) {
                        stack.removeLast();
                    }
                }

                stack.addLast(value);
            }

            return List.copyOf(stack);
        }
    }

    static final class MetricAlertService {
        private final MonotonicAnalyzer analyzer =
            new MonotonicAnalyzer();

        /*
         * Alert thresholds are explicit service policy, separate from the
         * algorithm that determines the next qualifying observation.
         */
        List<Match> findThresholdCrossings(
            List<Metric> metrics,
            int threshold
        ) {
            List<Metric> input = List.copyOf(metrics);
            List<Metric> filtered = new ArrayList<>();

            for (Metric metric : input) {
                if (metric.value() >= threshold) {
                    filtered.add(metric);
                }
            }

            if (filtered.isEmpty()) {
                return List.of();
            }

            return analyzer.analyze(
                filtered,
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    false
                )
            );
        }
    }

    private static void printMatches(
        String heading,
        List<Match> matches
    ) {
        System.out.println("\n" + heading);

        for (Match match : matches) {
            System.out.printf(
                "index=%d value=%d -> ",
                match.sourceIndex(),
                match.source().value()
            );

            if (match.resolved()) {
                System.out.printf(
                    "index=%d value=%d%n",
                    match.targetIndex(),
                    match.target().value()
                );
            } else {
                System.out.println("no qualifying reading");
            }
        }
    }

    private static void require(
        boolean condition,
        String message
    ) {
        if (!condition) {
            throw new IllegalStateException(
                "Test failed: " + message
            );
        }
    }

    public static void main(String[] args) {
        MonotonicAnalyzer analyzer = new MonotonicAnalyzer();

        List<Integer> rawValues = List.of(42, 38, 38, 51, 45, 60, 33);

        List<Metric> metrics = new ArrayList<>();
        for (int i = 0; i < rawValues.size(); i++) {
            metrics.add(new Metric(
                "pressure-kPa",
                1_800_000_000L + i * 5L,
                rawValues.get(i)
            ));
        }

        printMatches(
            "Next strictly greater reading",
            analyzer.analyze(
                metrics,
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    false
                )
            )
        );

        printMatches(
            "Next strictly smaller reading",
            analyzer.analyze(
                metrics,
                new QueryPolicy(
                    QueryDirection.NEXT_SMALLER,
                    true,
                    false
                )
            )
        );

        printMatches(
            "Circular next-greater reading",
            analyzer.analyze(
                metrics,
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    true
                )
            )
        );

        System.out.println(
            "\nNon-decreasing stack: "
            + analyzer.buildStack(
                rawValues,
                StackOrder.NON_DECREASING
            )
        );

        System.out.println(
            "Non-increasing stack: "
            + analyzer.buildStack(
                rawValues,
                StackOrder.NON_INCREASING
            )
        );

        MetricAlertService alertService = new MetricAlertService();
        System.out.println(
            "\nThreshold-crossing analysis for readings >= 40:"
        );
        printMatches(
            "Filtered metric stream",
            alertService.findThresholdCrossings(metrics, 40)
        );

        require(
            analyzer.analyze(
                List.of(
                    new Metric("x", 1, 2),
                    new Metric("x", 2, 1),
                    new Metric("x", 3, 3)
                ),
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    false
                )
            ).get(0).target().value() == 3,
            "next greater"
        );

        require(
            analyzer.analyze(
                List.of(
                    new Metric("x", 1, 5),
                    new Metric("x", 2, 5)
                ),
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    false
                )
            ).stream().noneMatch(Match::resolved),
            "strict comparisons must ignore equal values"
        );

        require(
            analyzer.analyze(
                List.of(
                    new Metric("x", 1, 1),
                    new Metric("x", 2, 2),
                    new Metric("x", 3, 1)
                ),
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    true
                )
            ).get(2).target().value() == 2,
            "circular lookup"
        );

        require(
            analyzer.analyze(
                List.of(),
                new QueryPolicy(
                    QueryDirection.NEXT_GREATER,
                    true,
                    true
                )
            ).isEmpty(),
            "empty input"
        );

        Set<String> metricNames = new HashSet<>();
        for (Metric metric : metrics) {
            metricNames.add(metric.name());
        }
        require(metricNames.contains("pressure-kPa"), "metric identity");

        System.out.println("\nAll Java tests passed.");
    }
}
