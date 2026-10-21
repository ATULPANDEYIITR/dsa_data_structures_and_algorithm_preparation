import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class HashingAssessment {

    record IndexPair(int first, int second) {
        IndexPair {
            if (first < 0 || second <= first) {
                throw new IllegalArgumentException("Indices must be distinct and ordered");
            }
        }
    }

    record AssessmentResult(String name, boolean passed, String detail) {}

    enum CheckStatus {
        PASS, FAIL
    }

    static final class HashingService {
        Map<Long, Integer> frequencyCounts(List<Long> values) {
            Map<Long, Integer> frequencies = new LinkedHashMap<>();
            for (long value : values) {
                frequencies.merge(value, 1, Integer::sum);
            }
            return frequencies;
        }

        List<Long> findDuplicates(List<Long> values) {
            Set<Long> seen = new HashSet<>();
            Set<Long> reported = new HashSet<>();
            List<Long> duplicates = new ArrayList<>();

            for (long value : values) {
                if (seen.contains(value) && reported.add(value)) {
                    duplicates.add(value);
                }
                seen.add(value);
            }
            return duplicates;
        }

        IndexPair twoSum(long[] values, long target) {
            Map<Long, Integer> earliestIndex = new HashMap<>();

            for (int index = 0; index < values.length; index++) {
                long value = values[index];

                // Math.subtractExact detects overflow instead of corrupting the lookup.
                final long complement;
                try {
                    complement = Math.subtractExact(target, value);
                } catch (ArithmeticException overflow) {
                    earliestIndex.putIfAbsent(value, index);
                    continue;
                }

                Integer match = earliestIndex.get(complement);
                if (match != null) {
                    return new IndexPair(match, index);
                }
                earliestIndex.putIfAbsent(value, index);
            }

            return null;
        }

        long countSubarraysWithSum(long[] values, long target) {
            Map<Long, Long> prefixFrequency = new HashMap<>();
            prefixFrequency.put(0L, 1L);

            long prefixSum = 0;
            long total = 0;

            for (long value : values) {
                prefixSum = Math.addExact(prefixSum, value);

                final long wanted;
                try {
                    wanted = Math.subtractExact(prefixSum, target);
                } catch (ArithmeticException overflow) {
                    prefixFrequency.merge(prefixSum, 1L, Math::addExact);
                    continue;
                }

                total = Math.addExact(total, prefixFrequency.getOrDefault(wanted, 0L));
                prefixFrequency.merge(prefixSum, 1L, Math::addExact);
            }
            return total;
        }

        int longestConsecutiveSequence(long[] values) {
            Set<Long> unique = new HashSet<>();
            for (long value : values) unique.add(value);

            int longest = 0;
            for (long value : unique) {
                if (value != Long.MIN_VALUE && unique.contains(value - 1)) {
                    continue;
                }

                int length = 1;
                long current = value;

                while (current != Long.MAX_VALUE && unique.contains(current + 1)) {
                    current++;
                    length = Math.incrementExact(length);
                }
                longest = Math.max(longest, length);
            }
            return longest;
        }

        List<List<String>> groupAnagrams(List<String> words) {
            Map<String, List<String>> groups = new LinkedHashMap<>();

            for (String word : words) {
                Objects.requireNonNull(word, "Word must not be null");
                if (!word.matches("[a-zA-Z]+")) {
                    throw new IllegalArgumentException(
                        "Words must contain ASCII alphabetic characters: " + word);
                }

                int[] counts = new int[26];
                for (char character : word.toLowerCase(java.util.Locale.ROOT).toCharArray()) {
                    counts[character - 'a']++;
                }

                StringBuilder signature = new StringBuilder();
                for (int count : counts) {
                    signature.append(count).append(',');
                }

                groups.computeIfAbsent(signature.toString(), key -> new ArrayList<>())
                      .add(word);
            }
            return new ArrayList<>(groups.values());
        }

        int longestUniqueSubstring(String text) {
            Objects.requireNonNull(text, "Text must not be null");

            // Code points avoid splitting supplementary Unicode characters.
            int[] codePoints = text.codePoints().toArray();
            Map<Integer, Integer> lastSeen = new HashMap<>();
            int left = 0;
            int longest = 0;

            for (int right = 0; right < codePoints.length; right++) {
                int character = codePoints[right];
                Integer previous = lastSeen.put(character, right);
                if (previous != null) {
                    left = Math.max(left, previous + 1);
                }
                longest = Math.max(longest, right - left + 1);
            }
            return longest;
        }

        long polynomialStringHash(String text) {
            Objects.requireNonNull(text, "Text must not be null");
            final long base = 257L;
            final long modulus = 1_000_000_007L;
            long hash = 0;

            for (int codePoint : text.codePoints().toArray()) {
                hash = (hash * base + codePoint) % modulus;
            }
            return hash;
        }

        List<List<String>> groupStringsByVerifiedHash(List<String> strings) {
            Map<Long, List<List<String>>> buckets = new HashMap<>();

            for (String text : strings) {
                long hash = polynomialStringHash(text);
                List<List<String>> groups =
                    buckets.computeIfAbsent(hash, key -> new ArrayList<>());

                List<String> matching = null;
                for (List<String> group : groups) {
                    if (group.get(0).equals(text)) {
                        matching = group;
                        break;
                    }
                }

                if (matching == null) {
                    groups.add(new ArrayList<>(List.of(text)));
                } else {
                    matching.add(text);
                }
            }

            List<List<String>> result = new ArrayList<>();
            for (List<List<String>> groups : buckets.values()) {
                result.addAll(groups);
            }
            return result;
        }
    }

    @FunctionalInterface
    interface TestAction {
        void run() throws Exception;
    }

    private static AssessmentResult evaluate(String name, TestAction action) {
        try {
            action.run();
            return new AssessmentResult(name, true, "passed");
        } catch (Exception error) {
            return new AssessmentResult(name, false,
                error.getClass().getSimpleName() + ": " + error.getMessage());
        }
    }

    public static void main(String[] args) {
        HashingService service = new HashingService();
        List<AssessmentResult> results = new ArrayList<>();

        results.add(evaluate("frequency counting", () -> {
            Map<Long, Integer> expected = Map.of(1L, 2, 2L, 3, 3L, 1);
            if (!service.frequencyCounts(List.of(1L, 2L, 2L, 3L, 1L, 2L))
                    .equals(expected)) {
                throw new AssertionError("Incorrect frequencies");
            }
        }));

        results.add(evaluate("duplicate detection", () -> {
            if (!service.findDuplicates(List.of(4L, 2L, 4L, 2L, 4L))
                    .equals(List.of(4L, 2L))) {
                throw new AssertionError("Incorrect duplicate order");
            }
        }));

        results.add(evaluate("two-sum lookup", () -> {
            if (!Objects.equals(service.twoSum(new long[]{3, -2, 7, 5}, 3),
                    new IndexPair(1, 2))) {
                throw new AssertionError("Incorrect indices");
            }
        }));

        results.add(evaluate("missing pair", () -> {
            if (service.twoSum(new long[]{1, 2}, 9) != null) {
                throw new AssertionError("Unexpected pair");
            }
        }));

        results.add(evaluate("prefix sums with negatives", () -> {
            if (service.countSubarraysWithSum(new long[]{1, -1, 0}, 0) != 3) {
                throw new AssertionError("Incorrect subarray count");
            }
        }));

        results.add(evaluate("empty prefix input", () -> {
            if (service.countSubarraysWithSum(new long[]{}, 0) != 0) {
                throw new AssertionError("Expected zero");
            }
        }));

        results.add(evaluate("longest consecutive sequence", () -> {
            if (service.longestConsecutiveSequence(new long[]{100, 4, 200, 1, 3, 2}) != 4) {
                throw new AssertionError("Incorrect sequence length");
            }
        }));

        results.add(evaluate("anagram grouping", () -> {
            List<List<String>> groups =
                service.groupAnagrams(List.of("eat", "tea", "ate", "bat"));
            if (groups.size() != 2) throw new AssertionError("Incorrect group count");
        }));

        results.add(evaluate("Unicode substring", () -> {
            if (service.longestUniqueSubstring("😀a😀") != 2) {
                throw new AssertionError("Incorrect substring length");
            }
        }));

        results.add(evaluate("string hash determinism", () -> {
            if (service.polynomialStringHash("branch") !=
                service.polynomialStringHash("branch")) {
                throw new AssertionError("Hash must be deterministic");
            }
        }));

        results.add(evaluate("hash equality verification", () -> {
            List<List<String>> groups =
                service.groupStringsByVerifiedHash(List.of("cat", "dog", "cat"));
            int catCount = groups.stream()
                .filter(group -> group.get(0).equals("cat"))
                .mapToInt(List::size).sum();

            if (catCount != 2) throw new AssertionError("Incorrect collision-safe grouping");
        }));

        int passed = 0;
        for (AssessmentResult result : results) {
            CheckStatus status = result.passed() ? CheckStatus.PASS : CheckStatus.FAIL;
            System.out.println(status + " | " + result.name() + ": " + result.detail());
            if (result.passed()) passed++;
        }

        System.out.printf("%nScore: %d/%d%n", passed, results.size());
        if (passed != results.size()) System.exit(1);
    }
}
