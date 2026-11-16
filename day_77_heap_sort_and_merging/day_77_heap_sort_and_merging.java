import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class HeapMergeEnterprise {

    enum MergeStrategy {
        HEAP,
        PAIRWISE
    }

    enum OperationStatus {
        CREATED,
        SOURCES_REGISTERED,
        VALIDATED,
        MERGED,
        FAILED
    }

    record MergePolicy(
        int maximumSources,
        long maximumElements,
        boolean requireSortedSources,
        boolean rejectDuplicateSourceIds
    ) {
        MergePolicy {
            if (maximumSources <= 0 || maximumElements <= 0) {
                throw new IllegalArgumentException(
                    "Merge limits must be positive."
                );
            }
        }
    }

    record Source(
        String sourceId,
        List<Integer> values,
        String owner
    ) {
        Source {
            if (sourceId == null || sourceId.isBlank()) {
                throw new IllegalArgumentException(
                    "Source ID is required."
                );
            }

            if (owner == null || owner.isBlank()) {
                throw new IllegalArgumentException(
                    "Source owner is required."
                );
            }

            Objects.requireNonNull(values, "Source values are required.");

            values = List.copyOf(values);
        }
    }

    record MergeStatistics(
        int sourceCount,
        long totalElements,
        long comparisonEstimate,
        double elapsedMilliseconds
    ) {}

    record MergeResult(
        List<Integer> values,
        MergeStatistics statistics,
        Instant completedAt
    ) {
        MergeResult {
            values = List.copyOf(values);
        }
    }

    record MergeEvent(
        String operationId,
        OperationStatus status,
        String message,
        Instant timestamp
    ) {}

    static final class MergeException extends RuntimeException {
        MergeException(String message) {
            super(message);
        }
    }

    static final class SourceValidationException extends RuntimeException {
        SourceValidationException(String message) {
            super(message);
        }
    }

    /*
     * Min-heap entries identify both the value and its source position.
     * This avoids storing all remaining source values in the heap.
     */
    record HeapEntry(
        int value,
        int sourceIndex,
        int elementIndex
    ) {}

    static final class HeapAlgorithms {

        private static void validateSorted(List<Integer> values) {
            Objects.requireNonNull(values, "Values cannot be null.");

            for (int i = 0; i < values.size(); i++) {
                if (values.get(i) == null) {
                    throw new SourceValidationException(
                        "Null element at index " + i
                    );
                }

                if (
                    i > 0 &&
                    values.get(i - 1) > values.get(i)
                ) {
                    throw new SourceValidationException(
                        "Input is not sorted at index " + i
                    );
                }
            }
        }

        /*
         * In-place max-heap sorting.
         * The input is copied to preserve caller-owned state.
         */
        public static List<Integer> heapSort(
            List<Integer> input,
            boolean descending
        ) {
            Objects.requireNonNull(input);

            List<Integer> values = new ArrayList<>(input);

            for (Integer value : values) {
                if (value == null) {
                    throw new IllegalArgumentException(
                        "Heap sort does not accept null elements."
                    );
                }
            }

            int n = values.size();

            for (int root = n / 2 - 1; root >= 0; root--) {
                siftDown(values, root, n);
            }

            for (int end = n - 1; end > 0; end--) {
                swap(values, 0, end);
                siftDown(values, 0, end);
            }

            if (descending) {
                java.util.Collections.reverse(values);
            }

            return List.copyOf(values);
        }

        private static void siftDown(
            List<Integer> values,
            int root,
            int heapSize
        ) {
            int current = root;

            while (true) {
                int largest = current;
                int left = current * 2 + 1;
                int right = current * 2 + 2;

                if (
                    left < heapSize &&
                    values.get(left) > values.get(largest)
                ) {
                    largest = left;
                }

                if (
                    right < heapSize &&
                    values.get(right) > values.get(largest)
                ) {
                    largest = right;
                }

                if (largest == current) {
                    break;
                }

                swap(values, current, largest);
                current = largest;
            }
        }

        private static void swap(
            List<Integer> values,
            int i,
            int j
        ) {
            Integer temporary = values.get(i);
            values.set(i, values.get(j));
            values.set(j, temporary);
        }

        public static List<Integer> mergeTwo(
            List<Integer> left,
            List<Integer> right
        ) {
            validateSorted(left);
            validateSorted(right);

            List<Integer> output = new ArrayList<>(
                left.size() + right.size()
            );

            int i = 0;
            int j = 0;

            while (i < left.size() && j < right.size()) {
                if (left.get(i) <= right.get(j)) {
                    output.add(left.get(i++));
                } else {
                    output.add(right.get(j++));
                }
            }

            while (i < left.size()) {
                output.add(left.get(i++));
            }

            while (j < right.size()) {
                output.add(right.get(j++));
            }

            return List.copyOf(output);
        }

        public static List<Integer> mergeKHeap(
            List<Source> sources
        ) {
            validateSources(sources);

            Comparator<HeapEntry> comparator =
                Comparator.comparingInt(HeapEntry::value)
                    .thenComparingInt(HeapEntry::sourceIndex)
                    .thenComparingInt(HeapEntry::elementIndex);

            PriorityQueue<HeapEntry> heap =
                new PriorityQueue<>(comparator);

            long total = 0;

            for (int source = 0; source < sources.size(); source++) {
                List<Integer> values = sources.get(source).values();

                total += values.size();

                if (!values.isEmpty()) {
                    heap.offer(
                        new HeapEntry(values.get(0), source, 0)
                    );
                }
            }

            if (total > Integer.MAX_VALUE) {
                throw new MergeException(
                    "Result exceeds Java List capacity."
                );
            }

            List<Integer> output = new ArrayList<>((int) total);

            while (!heap.isEmpty()) {
                HeapEntry entry = heap.poll();

                output.add(entry.value());

                int nextIndex = entry.elementIndex() + 1;

                List<Integer> source =
                    sources.get(entry.sourceIndex()).values();

                if (nextIndex < source.size()) {
                    heap.offer(
                        new HeapEntry(
                            source.get(nextIndex),
                            entry.sourceIndex(),
                            nextIndex
                        )
                    );
                }
            }

            if (output.size() != total) {
                throw new MergeException(
                    "Element conservation invariant failed."
                );
            }

            return List.copyOf(output);
        }

        public static List<Integer> mergeKPairwise(
            List<Source> sources
        ) {
            validateSources(sources);

            List<List<Integer>> current = sources.stream()
                .map(Source::values)
                .collect(Collectors.toCollection(ArrayList::new));

            if (current.isEmpty()) {
                return List.of();
            }

            while (current.size() > 1) {
                List<List<Integer>> next = new ArrayList<>();

                for (int i = 0; i < current.size(); i += 2) {
                    if (i + 1 < current.size()) {
                        next.add(
                            mergeTwo(current.get(i), current.get(i + 1))
                        );
                    } else {
                        next.add(current.get(i));
                    }
                }

                current = next;
            }

            return current.get(0);
        }

        private static void validateSources(List<Source> sources) {
            Objects.requireNonNull(sources, "Sources cannot be null.");

            for (Source source : sources) {
                Objects.requireNonNull(source);
                validateSorted(source.values());
            }
        }
    }

    interface MergeObserver {
        void onEvent(MergeEvent event);
    }

    static final class MergeService {

        private final MergePolicy policy;
        private final List<Source> sources = new ArrayList<>();
        private final Set<String> sourceIds = new HashSet<>();
        private final List<MergeObserver> observers = new ArrayList<>();

        private final AtomicLong sequence = new AtomicLong(0);

        private OperationStatus status = OperationStatus.CREATED;
        private long totalElements = 0;

        private final String operationId;

        MergeService(MergePolicy policy) {
            this.policy = Objects.requireNonNull(policy);

            this.operationId = "MERGE-" +
                sequence.incrementAndGet();
        }

        public void addObserver(MergeObserver observer) {
            observers.add(Objects.requireNonNull(observer));
        }

        private void publish(
            OperationStatus newStatus,
            String message
        ) {
            status = newStatus;

            MergeEvent event = new MergeEvent(
                operationId,
                newStatus,
                message,
                Instant.now()
            );

            // Observer failures must not corrupt merge state.
            for (MergeObserver observer : observers) {
                try {
                    observer.onEvent(event);
                } catch (RuntimeException exception) {
                    System.err.println(
                        "Observer failure: " + exception.getMessage()
                    );
                }
            }
        }

        public void registerSource(Source source) {
            if (
                status == OperationStatus.MERGED ||
                status == OperationStatus.FAILED
            ) {
                throw new MergeException(
                    "Operation does not accept new sources."
                );
            }

            Objects.requireNonNull(source);

            if (
                sources.size() >= policy.maximumSources()
            ) {
                throw new MergeException(
                    "Maximum source count exceeded."
                );
            }

            if (
                policy.rejectDuplicateSourceIds() &&
                sourceIds.contains(source.sourceId())
            ) {
                throw new MergeException(
                    "Duplicate source identifier: " + source.sourceId()
                );
            }

            if (policy.requireSortedSources()) {
                HeapAlgorithms.validateSorted(source.values());
            }

            if (
                source.values().size() >
                policy.maximumElements() - totalElements
            ) {
                throw new MergeException(
                    "Maximum element limit exceeded."
                );
            }

            sources.add(source);
            sourceIds.add(source.sourceId());
            totalElements += source.values().size();

            publish(
                OperationStatus.SOURCES_REGISTERED,
                "Registered source " + source.sourceId()
            );
        }

        public MergeResult execute(MergeStrategy strategy) {
            if (sources.isEmpty()) {
                throw new MergeException(
                    "At least one source must be registered."
                );
            }

            if (
                status == OperationStatus.MERGED ||
                status == OperationStatus.FAILED
            ) {
                throw new MergeException(
                    "Operation has already terminated."
                );
            }

            long started = System.nanoTime();

            try {
                publish(
                    OperationStatus.VALIDATED,
                    "All registered sources passed validation."
                );

                List<Integer> output;

                if (strategy == MergeStrategy.HEAP) {
                    output = HeapAlgorithms.mergeKHeap(sources);
                } else {
                    output = HeapAlgorithms.mergeKPairwise(sources);
                }

                double elapsed =
                    (System.nanoTime() - started) / 1_000_000.0;

                long estimate = totalElements *
                    Math.max(1, 32 - Integer.numberOfLeadingZeros(
                        sources.size()
                    ));

                MergeStatistics statistics = new MergeStatistics(
                    sources.size(),
                    totalElements,
                    estimate,
                    elapsed
                );

                publish(
                    OperationStatus.MERGED,
                    "Multiway merge completed."
                );

                return new MergeResult(
                    output,
                    statistics,
                    Instant.now()
                );

            } catch (RuntimeException exception) {
                publish(
                    OperationStatus.FAILED,
                    exception.getMessage()
                );

                throw exception;
            }
        }

        public OperationStatus getStatus() {
            return status;
        }
    }

    /*
     * A file output service using a temporary file and atomic replacement
     * where supported by the underlying filesystem.
     */
    static final class ResultExporter {

        public static void export(
            MergeResult result,
            Path destination
        ) throws IOException {
            String values = result.values().stream()
                .map(String::valueOf)
                .collect(Collectors.joining(","));

            String document =
                "operation=heap-and-multiway-merge\n" +
                "completed_at=" + result.completedAt() + "\n" +
                "source_count=" + result.statistics().sourceCount() + "\n" +
                "element_count=" + result.statistics().totalElements() + "\n" +
                "values=" + values + "\n";

            Path absolute = destination.toAbsolutePath();
            Path parent = absolute.getParent();

            if (parent != null) {
                Files.createDirectories(parent);
            }

            Path temporary = Files.createTempFile(
                parent,
                "merge-",
                ".tmp"
            );

            try {
                Files.writeString(
                    temporary,
                    document,
                    StandardCharsets.UTF_8
                );

                try {
                    Files.move(
                        temporary,
                        absolute,
                        StandardCopyOption.REPLACE_EXISTING,
                        StandardCopyOption.ATOMIC_MOVE
                    );
                } catch (java.nio.file.AtomicMoveNotSupportedException e) {
                    Files.move(
                        temporary,
                        absolute,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                }
            } finally {
                Files.deleteIfExists(temporary);
            }
        }
    }

    private static void runTests() throws IOException {
        System.out.println("HEAP SORT");

        List<Integer> input = List.of(
            45, 12, 89, 3, 67, 21, 90, 4, 45
        );

        List<Integer> sorted =
            HeapAlgorithms.heapSort(input, false);

        System.out.println("Original: " + input);
        System.out.println("Sorted: " + sorted);

        List<Integer> expected = input.stream()
            .sorted()
            .toList();

        if (!sorted.equals(expected)) {
            throw new AssertionError("Heap sort failed.");
        }

        System.out.println("\nENTERPRISE MULTIWAY MERGE");

        MergePolicy policy = new MergePolicy(
            100,
            1_000_000,
            true,
            true
        );

        MergeService service = new MergeService(policy);

        service.addObserver(event ->
            System.out.println(
                event.status() + ": " + event.message()
            )
        );

        service.registerSource(
            new Source("database-A", List.of(1, 4, 7, 10), "Team-A")
        );

        service.registerSource(
            new Source("database-B", List.of(2, 5, 8, 11), "Team-B")
        );

        service.registerSource(
            new Source("database-C", List.of(3, 6, 9, 12), "Team-C")
        );

        MergeResult result = service.execute(MergeStrategy.HEAP);

        System.out.println("Merged: " + result.values());
        System.out.println("Statistics: " + result.statistics());

        List<Source> pairwiseSources = List.of(
            new Source("P1", List.of(1, 4, 7), "Operations"),
            new Source("P2", List.of(2, 5, 8), "Operations"),
            new Source("P3", List.of(3, 6, 9), "Operations")
        );

        List<Integer> pairwise =
            HeapAlgorithms.mergeKPairwise(pairwiseSources);

        System.out.println("Pairwise result: " + pairwise);

        if (!pairwise.equals(List.of(1, 2, 3, 4, 5, 6, 7, 8, 9))) {
            throw new AssertionError("Pairwise merge failed.");
        }

        System.out.println("\nEDGE CASES");

        List<List<Integer>> edgeCases = List.of(
            List.of(),
            List.of(List.of()),
            List.of(List.of(), List.of(), List.of()),
            List.of(
                List.of(1, 1, 1),
                List.of(1, 1),
                List.of(1)
            ),
            List.of(
                List.of(-10, -5),
                List.of(-8, 0),
                List.of(2, 3)
            )
        );

        for (List<List<Integer>> test : edgeCases) {
            List<Source> testSources = new ArrayList<>();

            for (int i = 0; i < test.size(); i++) {
                testSources.add(
                    new Source("edge-" + i, test.get(i), "Testing")
                );
            }

            System.out.println(
                HeapAlgorithms.mergeKHeap(testSources)
            );
        }

        try {
            HeapAlgorithms.validateSorted(List.of(1, 5, 3));
            throw new AssertionError("Unsorted source was accepted.");
        } catch (SourceValidationException expectedFailure) {
            System.out.println(
                "Unsorted input rejected: " +
                expectedFailure.getMessage()
            );
        }

        ResultExporter.export(
            result,
            Path.of("heap_merge_enterprise_result.txt")
        );

        System.out.println("\nAll Java 17 checks passed.");
    }

    public static void main(String[] args) {
        try {
            runTests();
        } catch (Exception exception) {
            System.err.println(
                "Application failed: " + exception.getMessage()
            );

            exception.printStackTrace(System.err);
            System.exit(1);
        }
    }
}
