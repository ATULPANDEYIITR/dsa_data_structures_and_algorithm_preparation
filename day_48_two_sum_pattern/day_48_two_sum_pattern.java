import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.TreeMap;

/**
 * Two-sum pattern in an enterprise transaction matching service.
 *
 * Compile: javac TwoSumPatterns.java
 * Run:     java TwoSumPatterns
 */
public class TwoSumPatterns {

    public record Transaction(String reference, long amountCents) {
        public Transaction {
            if (reference == null || reference.isBlank()) {
                throw new IllegalArgumentException(
                    "Transaction reference must not be blank"
                );
            }
        }
    }

    public record IndexPair(int left, int right) {
        public IndexPair {
            if (left < 0 || right < 0 || left == right) {
                throw new IllegalArgumentException(
                    "Pair indices must be distinct and nonnegative"
                );
            }
        }
    }

    public record TransactionPair(
        Transaction left,
        Transaction right
    ) {
        public TransactionPair {
            Objects.requireNonNull(left);
            Objects.requireNonNull(right);
        }

        public long combinedCents() {
            return Math.addExact(left.amountCents(), right.amountCents());
        }
    }

    public static final class TransactionMatcher {

        /**
         * Find the first two distinct records whose amounts match the target.
         * Map lookup gives expected O(n) time and O(n) auxiliary space.
         */
        public Optional<IndexPair> findTwoSum(
            List<Transaction> transactions,
            long targetCents
        ) {
            Objects.requireNonNull(transactions, "transactions");

            Map<Long, Integer> earliestIndex = new HashMap<>();

            for (int right = 0; right < transactions.size(); right++) {
                Transaction transaction = Objects.requireNonNull(
                    transactions.get(right),
                    "transaction at index " + right
                );

                long complement;
                try {
                    complement = Math.subtractExact(
                        targetCents,
                        transaction.amountCents()
                    );
                } catch (ArithmeticException overflow) {
                    // An unrepresentable complement cannot equal a stored long.
                    earliestIndex.putIfAbsent(transaction.amountCents(), right);
                    continue;
                }

                Integer left = earliestIndex.get(complement);
                if (left != null) {
                    return Optional.of(new IndexPair(left, right));
                }

                earliestIndex.putIfAbsent(transaction.amountCents(), right);
            }

            return Optional.empty();
        }

        /**
         * Count every pair of distinct transaction records, not just
         * distinct amounts. The running frequency counts earlier records.
         */
        public long countPairs(
            List<Transaction> transactions,
            long targetCents
        ) {
            Objects.requireNonNull(transactions, "transactions");

            Map<Long, Long> frequency = new HashMap<>();
            long pairCount = 0;

            for (Transaction transaction : transactions) {
                Objects.requireNonNull(transaction, "transaction");

                long complement;
                try {
                    complement = Math.subtractExact(
                        targetCents,
                        transaction.amountCents()
                    );
                } catch (ArithmeticException overflow) {
                    complement = Long.MIN_VALUE;
                }

                if (complement != Long.MIN_VALUE ||
                    targetCents - transaction.amountCents()
                        == Long.MIN_VALUE) {
                    pairCount = Math.addExact(
                        pairCount,
                        frequency.getOrDefault(complement, 0L)
                    );
                }

                frequency.merge(
                    transaction.amountCents(),
                    1L,
                    Math::addExact
                );
            }

            return pairCount;
        }

        /**
         * Return every matching pair of original record positions.
         * The result may be quadratic when the input contains many matches.
         */
        public List<IndexPair> findAllPairs(
            List<Transaction> transactions,
            long targetCents
        ) {
            Objects.requireNonNull(transactions, "transactions");

            Map<Long, List<Integer>> indicesByAmount = new HashMap<>();
            List<IndexPair> result = new ArrayList<>();

            for (int right = 0; right < transactions.size(); right++) {
                Transaction transaction = Objects.requireNonNull(
                    transactions.get(right)
                );

                long complement;
                try {
                    complement = Math.subtractExact(
                        targetCents,
                        transaction.amountCents()
                    );
                } catch (ArithmeticException overflow) {
                    indicesByAmount.computeIfAbsent(
                        transaction.amountCents(),
                        ignored -> new ArrayList<>()
                    ).add(right);
                    continue;
                }

                for (int left : indicesByAmount.getOrDefault(
                    complement,
                    Collections.emptyList()
                )) {
                    result.add(new IndexPair(left, right));
                }

                indicesByAmount.computeIfAbsent(
                    transaction.amountCents(),
                    ignored -> new ArrayList<>()
                ).add(right);
            }

            return List.copyOf(result);
        }

        /**
         * Return distinct amount combinations in ascending order.
         * Equal amounts require at least two distinct transaction records.
         */
        public List<List<Long>> uniqueAmountPairs(
            List<Transaction> transactions,
            long targetCents
        ) {
            Objects.requireNonNull(transactions, "transactions");

            Map<Long, Long> frequencies = new TreeMap<>();

            for (Transaction transaction : transactions) {
                Objects.requireNonNull(transaction);
                frequencies.merge(
                    transaction.amountCents(),
                    1L,
                    Math::addExact
                );
            }

            List<List<Long>> result = new ArrayList<>();

            for (Map.Entry<Long, Long> entry : frequencies.entrySet()) {
                long amount = entry.getKey();
                long complement;

                try {
                    complement = Math.subtractExact(targetCents, amount);
                } catch (ArithmeticException overflow) {
                    continue;
                }

                if (complement < amount || !frequencies.containsKey(complement)) {
                    continue;
                }

                if (complement == amount && entry.getValue() < 2) {
                    continue;
                }

                result.add(List.of(amount, complement));
            }

            return List.copyOf(result);
        }

        /**
         * Find an ordered pair where right.amount - left.amount = difference.
         * A negative difference is valid and reverses the numeric direction.
         */
        public Optional<IndexPair> findSignedDifference(
            List<Transaction> transactions,
            long difference
        ) {
            Objects.requireNonNull(transactions, "transactions");
            Map<Long, Integer> earliestIndex = new LinkedHashMap<>();

            for (int right = 0; right < transactions.size(); right++) {
                long value = Objects.requireNonNull(
                    transactions.get(right)
                ).amountCents();

                long required;
                try {
                    required = Math.subtractExact(value, difference);
                } catch (ArithmeticException overflow) {
                    earliestIndex.putIfAbsent(value, right);
                    continue;
                }

                Integer left = earliestIndex.get(required);
                if (left != null) {
                    return Optional.of(new IndexPair(left, right));
                }

                earliestIndex.putIfAbsent(value, right);
            }

            return Optional.empty();
        }

        /**
         * Find a pair whose absolute amount difference equals a nonnegative
         * threshold. Both directional complements must be checked.
         */
        public Optional<IndexPair> findAbsoluteDifference(
            List<Transaction> transactions,
            long difference
        ) {
            Objects.requireNonNull(transactions, "transactions");

            if (difference < 0) {
                throw new IllegalArgumentException(
                    "Absolute difference must be nonnegative"
                );
            }

            Map<Long, Integer> earliestIndex = new HashMap<>();

            for (int right = 0; right < transactions.size(); right++) {
                long value = Objects.requireNonNull(
                    transactions.get(right)
                ).amountCents();

                long lower = 0;
                long upper = 0;
                boolean lowerValid = true;
                boolean upperValid = true;

                try {
                    lower = Math.subtractExact(value, difference);
                } catch (ArithmeticException overflow) {
                    lowerValid = false;
                }

                try {
                    upper = Math.addExact(value, difference);
                } catch (ArithmeticException overflow) {
                    upperValid = false;
                }

                if (difference == 0) {
                    Integer left = earliestIndex.get(value);
                    if (left != null) {
                        return Optional.of(new IndexPair(left, right));
                    }
                } else {
                    if (lowerValid && earliestIndex.containsKey(lower)) {
                        return Optional.of(
                            new IndexPair(earliestIndex.get(lower), right)
                        );
                    }

                    if (upperValid && earliestIndex.containsKey(upper)) {
                        return Optional.of(
                            new IndexPair(earliestIndex.get(upper), right)
                        );
                    }
                }

                earliestIndex.putIfAbsent(value, right);
            }

            return Optional.empty();
        }
    }

    private static List<Transaction> sampleTransactions() {
        return List.of(
            new Transaction("TX-104", 12500),
            new Transaction("TX-105", 27500),
            new Transaction("TX-106", 8000),
            new Transaction("TX-107", 20000),
            new Transaction("TX-108", 12500)
        );
    }

    private static void printPair(
        String label,
        Optional<IndexPair> pair,
        List<Transaction> transactions
    ) {
        if (pair.isEmpty()) {
            System.out.println(label + ": no matching records");
            return;
        }

        IndexPair indices = pair.get();
        Transaction left = transactions.get(indices.left());
        Transaction right = transactions.get(indices.right());

        System.out.printf(
            "%s: %s (%d) + %s (%d)%n",
            label,
            left.reference(),
            left.amountCents(),
            right.reference(),
            right.amountCents()
        );
    }

    private static void runTests(TransactionMatcher matcher) {
        List<Transaction> duplicates = List.of(
            new Transaction("A", 200),
            new Transaction("B", 200),
            new Transaction("C", 200),
            new Transaction("D", 200)
        );

        if (matcher.countPairs(duplicates, 400) != 6) {
            throw new AssertionError("Duplicate pair count is incorrect");
        }

        if (matcher.findTwoSum(
            List.of(new Transaction("ONLY", 100)),
            200
        ).isPresent()) {
            throw new AssertionError("A record must not pair with itself");
        }

        if (matcher.findAbsoluteDifference(
            List.of(new Transaction("A", 5)),
            0
        ).isPresent()) {
            throw new AssertionError("Zero difference needs two records");
        }

        if (matcher.findAbsoluteDifference(
            List.of(
                new Transaction("A", 5),
                new Transaction("B", 5)
            ),
            0
        ).isEmpty()) {
            throw new AssertionError("Duplicate amounts should match");
        }

        if (matcher.findAllPairs(duplicates, 400).size() != 6) {
            throw new AssertionError("All-pairs enumeration failed");
        }

        try {
            matcher.findAbsoluteDifference(duplicates, -1);
            throw new AssertionError("Negative absolute difference accepted");
        } catch (IllegalArgumentException expected) {
            // The API rejects an invalid threshold before processing records.
        }

        System.out.println("All Java transaction-matching tests passed.");
    }

    public static void main(String[] args) {
        TransactionMatcher matcher = new TransactionMatcher();
        List<Transaction> transactions = sampleTransactions();

        printPair(
            "Pair matching 40000 cents",
            matcher.findTwoSum(transactions, 40000),
            transactions
        );

        System.out.println(
            "All matching record pairs: "
                + matcher.findAllPairs(transactions, 40000)
        );

        System.out.println(
            "Number of pairs matching 40000 cents: "
                + matcher.countPairs(transactions, 40000)
        );

        System.out.println(
            "Unique amount pairs: "
                + matcher.uniqueAmountPairs(transactions, 40000)
        );

        printPair(
            "Signed difference of 7500 cents",
            matcher.findSignedDifference(transactions, 7500),
            transactions
        );

        printPair(
            "Absolute difference of 7500 cents",
            matcher.findAbsoluteDifference(transactions, 7500),
            transactions
        );

        runTests(matcher);
    }
}
