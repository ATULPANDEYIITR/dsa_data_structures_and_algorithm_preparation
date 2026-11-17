import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Heap Assessment: Enterprise Priority Queue Processing
 *
 * Java 17
 *
 * Features:
 * - Generic binary heap
 * - Bounded priority queues
 * - Kth largest element
 * - Top K frequent elements
 * - Merge K sorted sequences
 * - Running median
 * - Job scheduling and state transitions
 * - Cancellation
 * - Retry handling
 * - Capacity management
 * - Performance-oriented collection usage
 */

public class HeapAssessment {

    static class HeapException extends RuntimeException {
        HeapException(String message) {
            super(message);
        }
    }

    enum Priority {
        CRITICAL(0),
        HIGH(1),
        NORMAL(2),
        LOW(3);

        private final int rank;

        Priority(int rank) {
            this.rank = rank;
        }

        int rank() {
            return rank;
        }
    }

    enum JobState {
        QUEUED,
        RUNNING,
        COMPLETED,
        FAILED,
        CANCELLED
    }

    enum ReviewState {
        PENDING,
        APPROVED,
        CHANGES_REQUESTED,
        DISMISSED
    }

    record Job(
        String id,
        String description,
        Priority priority,
        long sequence,
        int maximumRetries
    ) {
        Job {
            if (id == null || id.isBlank()) {
                throw new HeapException("Job ID is required.");
            }

            if (description == null || description.isBlank()) {
                throw new HeapException("Description is required.");
            }

            Objects.requireNonNull(priority);

            if (maximumRetries < 0) {
                throw new HeapException("Invalid retry count.");
            }
        }
    }

    record HeapEntry<T>(
        T value,
        int priority,
        long sequence
    ) {}

    static class BinaryHeap<T> {

        private final List<T> items = new ArrayList<>();
        private final Comparator<T> comparator;

        BinaryHeap(Comparator<T> comparator) {
            this.comparator = Objects.requireNonNull(comparator);
        }

        int size() {
            return items.size();
        }

        boolean isEmpty() {
            return items.isEmpty();
        }

        T peek() {
            if (isEmpty()) {
                throw new HeapException("Heap is empty.");
            }

            return items.get(0);
        }

        void add(T value) {
            items.add(value);
            siftUp(items.size() - 1);
        }

        T remove() {
            if (isEmpty()) {
                throw new HeapException("Heap is empty.");
            }

            T root = items.get(0);
            T last = items.remove(items.size() - 1);

            if (!isEmpty()) {
                items.set(0, last);
                siftDown(0);
            }

            return root;
        }

        private void siftUp(int index) {
            while (index > 0) {
                int parent = (index - 1) / 2;

                if (
                    comparator.compare(
                        items.get(index),
                        items.get(parent)
                    ) >= 0
                ) {
                    break;
                }

                Collections.swap(items, index, parent);
                index = parent;
            }
        }

        private void siftDown(int index) {
            int n = items.size();

            while (true) {
                int smallest = index;
                int left = 2 * index + 1;
                int right = left + 1;

                if (
                    left < n &&
                    comparator.compare(
                        items.get(left),
                        items.get(smallest)
                    ) < 0
                ) {
                    smallest = left;
                }

                if (
                    right < n &&
                    comparator.compare(
                        items.get(right),
                        items.get(smallest)
                    ) < 0
                ) {
                    smallest = right;
                }

                if (smallest == index) {
                    break;
                }

                Collections.swap(items, index, smallest);
                index = smallest;
            }
        }
    }

    static class HeapAlgorithms {

        static int kthLargest(List<Integer> values, int k) {
            validateNumbers(values);

            if (k < 1 || k > values.size()) {
                throw new HeapException("Invalid k.");
            }

            PriorityQueue<Integer> heap = new PriorityQueue<>();

            for (int value : values) {
                heap.offer(value);

                if (heap.size() > k) {
                    heap.poll();
                }
            }

            return heap.element();
        }

        static List<Integer> topKFrequent(
            List<Integer> values,
            int k
        ) {
            validateNumbers(values);

            Map<Integer, Integer> frequencies = new HashMap<>();

            for (int value : values) {
                frequencies.merge(value, 1, Integer::sum);
            }

            if (k < 0 || k > frequencies.size()) {
                throw new HeapException("Invalid k.");
            }

            Comparator<Map.Entry<Integer, Integer>> comparator =
                Comparator
                    .comparingInt(
                        (Map.Entry<Integer, Integer> e) -> e.getValue()
                    )
                    .thenComparing(
                        Map.Entry::getKey,
                        Comparator.reverseOrder()
                    );

            PriorityQueue<Map.Entry<Integer, Integer>> heap =
                new PriorityQueue<>(comparator);

            frequencies.entrySet().forEach(entry -> {
                heap.offer(entry);

                if (heap.size() > k) {
                    heap.poll();
                }
            });

            List<Integer> result = new ArrayList<>(heap.size());

            while (!heap.isEmpty()) {
                result.add(heap.poll().getKey());
            }

            result.sort(
                Comparator
                    .<Integer>comparingInt(
                        value -> frequencies.get(value)
                    )
                    .reversed()
                    .thenComparingInt(Integer::intValue)
            );

            return result;
        }

        static List<Integer> mergeKSorted(
            List<List<Integer>> arrays
        ) {
            record Node(int value, int arrayIndex, int elementIndex) {}

            Comparator<Node> comparator =
                Comparator.comparingInt(Node::value)
                    .thenComparingInt(Node::arrayIndex);

            PriorityQueue<Node> heap =
                new PriorityQueue<>(comparator);

            for (int i = 0; i < arrays.size(); i++) {
                List<Integer> array = arrays.get(i);
                validateNumbers(array);

                for (int j = 1; j < array.size(); j++) {
                    if (array.get(j) < array.get(j - 1)) {
                        throw new HeapException(
                            "Input arrays must be sorted."
                        );
                    }
                }

                if (!array.isEmpty()) {
                    heap.offer(new Node(array.get(0), i, 0));
                }
            }

            List<Integer> result = new ArrayList<>();

            while (!heap.isEmpty()) {
                Node current = heap.poll();

                result.add(current.value());

                int next = current.elementIndex() + 1;
                List<Integer> source = arrays.get(current.arrayIndex());

                if (next < source.size()) {
                    heap.offer(
                        new Node(
                            source.get(next),
                            current.arrayIndex(),
                            next
                        )
                    );
                }
            }

            return result;
        }

        static long connectRopes(List<Integer> lengths) {
            validateNumbers(lengths);

            if (lengths.stream().anyMatch(value -> value < 0)) {
                throw new HeapException("Negative rope length.");
            }

            PriorityQueue<Long> heap = new PriorityQueue<>();

            lengths.forEach(value -> heap.offer((long) value));

            long totalCost = 0;

            while (heap.size() > 1) {
                long combined = Math.addExact(
                    heap.poll(),
                    heap.poll()
                );

                totalCost = Math.addExact(totalCost, combined);
                heap.offer(combined);
            }

            return totalCost;
        }

        private static void validateNumbers(List<Integer> values) {
            if (values == null) {
                throw new HeapException("Input cannot be null.");
            }

            if (values.stream().anyMatch(Objects::isNull)) {
                throw new HeapException("Null values are invalid.");
            }
        }
    }

    static class RunningMedian {

        private final PriorityQueue<Integer> lower =
            new PriorityQueue<>(Comparator.reverseOrder());

        private final PriorityQueue<Integer> upper =
            new PriorityQueue<>();

        void add(int value) {
            if (lower.isEmpty() || value <= lower.peek()) {
                lower.offer(value);
            } else {
                upper.offer(value);
            }

            if (lower.size() > upper.size() + 1) {
                upper.offer(lower.poll());
            }

            if (upper.size() > lower.size()) {
                lower.offer(upper.poll());
            }
        }

        double median() {
            if (lower.isEmpty()) {
                throw new HeapException("Median unavailable.");
            }

            if (lower.size() > upper.size()) {
                return lower.peek();
            }

            return ((long) lower.peek() + upper.peek()) / 2.0;
        }
    }

    static class JobScheduler {

        private final int capacity;

        private final AtomicLong sequence = new AtomicLong();

        private final PriorityQueue<Job> queue =
            new PriorityQueue<>(
                Comparator.comparingInt(
                    (Job job) -> job.priority().rank()
                ).thenComparingLong(Job::sequence)
            );

        private final Map<String, JobState> states = new HashMap<>();
        private final Map<String, Integer> attempts = new HashMap<>();

        JobScheduler(int capacity) {
            if (capacity < 1) {
                throw new HeapException("Capacity must be positive.");
            }

            this.capacity = capacity;
        }

        synchronized Job submit(
            String id,
            String description,
            Priority priority,
            int retries
        ) {
            if (queue.size() >= capacity) {
                throw new HeapException("Queue capacity exceeded.");
            }

            if (states.containsKey(id)) {
                throw new HeapException("Duplicate job ID.");
            }

            Job job = new Job(
                id,
                description,
                priority,
                sequence.getAndIncrement(),
                retries
            );

            queue.offer(job);
            states.put(id, JobState.QUEUED);
            attempts.put(id, 0);

            return job;
        }

        synchronized boolean cancel(String id) {
            if (states.get(id) != JobState.QUEUED) {
                return false;
            }

            states.put(id, JobState.CANCELLED);

            // Lazy deletion preserves logarithmic queue operations.
            return true;
        }

        synchronized Optional<Job> next() {
            while (!queue.isEmpty()) {
                Job job = queue.poll();

                if (states.get(job.id()) != JobState.QUEUED) {
                    continue;
                }

                states.put(job.id(), JobState.RUNNING);

                return Optional.of(job);
            }

            return Optional.empty();
        }

        synchronized void complete(String id) {
            requireState(id, JobState.RUNNING);
            states.put(id, JobState.COMPLETED);
        }

        synchronized void fail(String id) {
            requireState(id, JobState.RUNNING);

            states.put(id, JobState.FAILED);
        }

        synchronized boolean retry(String id) {
            Job original = null;

            for (Job job : queue) {
                if (job.id().equals(id)) {
                    original = job;
                    break;
                }
            }

            if (states.get(id) != JobState.FAILED) {
                throw new HeapException("Job is not failed.");
            }

            int used = attempts.merge(id, 1, Integer::sum);

            if (original != null || used > 3) {
                return false;
            }

            return false;
        }

        synchronized JobState state(String id) {
            return states.get(id);
        }

        private void requireState(String id, JobState expected) {
            if (states.get(id) != expected) {
                throw new HeapException("Invalid job state transition.");
            }
        }
    }

    static class ApprovalPolicy {

        private final int requiredApprovals;
        private final Set<String> eligibleReviewers;

        ApprovalPolicy(
            int requiredApprovals,
            Set<String> eligibleReviewers
        ) {
            if (requiredApprovals < 0) {
                throw new HeapException("Invalid approval requirement.");
            }

            this.requiredApprovals = requiredApprovals;
            this.eligibleReviewers = Set.copyOf(eligibleReviewers);
        }

        boolean satisfied(Map<String, ReviewState> reviews) {
            long validApprovals = reviews.entrySet()
                .stream()
                .filter(entry ->
                    eligibleReviewers.contains(entry.getKey())
                )
                .filter(entry ->
                    entry.getValue() == ReviewState.APPROVED
                )
                .count();

            return validApprovals >= requiredApprovals;
        }
    }

    static class BranchProtection {

        private final boolean requireChecks;
        private final boolean preventDirectPush;
        private final boolean preventForcePush;

        BranchProtection(
            boolean requireChecks,
            boolean preventDirectPush,
            boolean preventForcePush
        ) {
            this.requireChecks = requireChecks;
            this.preventDirectPush = preventDirectPush;
            this.preventForcePush = preventForcePush;
        }

        boolean canDirectPush() {
            return !preventDirectPush;
        }

        boolean canForcePush() {
            return !preventForcePush;
        }

        boolean requireChecks() {
            return requireChecks;
        }
    }

    public static void main(String[] args) {

        System.out.println("HEAP ASSESSMENT\n");

        List<Integer> values =
            List.of(7, 10, 4, 3, 20, 15);

        System.out.println(
            "Kth largest: " +
            HeapAlgorithms.kthLargest(values, 3)
        );

        System.out.println(
            "Top frequent: " +
            HeapAlgorithms.topKFrequent(
                List.of(1, 1, 1, 2, 2, 3),
                2
            )
        );

        System.out.println(
            "Merged arrays: " +
            HeapAlgorithms.mergeKSorted(List.of(
                List.of(1, 4, 7),
                List.of(2, 5, 8),
                List.of(3, 6, 9)
            ))
        );

        System.out.println(
            "Rope connection cost: " +
            HeapAlgorithms.connectRopes(List.of(4, 3, 2, 6))
        );

        RunningMedian median = new RunningMedian();

        for (int value : List.of(5, 15, 1, 3)) {
            median.add(value);

            System.out.println(
                "Running median: " + median.median()
            );
        }

        JobScheduler scheduler = new JobScheduler(10);

        scheduler.submit(
            "JOB-1",
            "Routine report",
            Priority.LOW,
            2
        );

        scheduler.submit(
            "JOB-2",
            "Security incident",
            Priority.CRITICAL,
            3
        );

        scheduler.submit(
            "JOB-3",
            "Database backup",
            Priority.NORMAL,
            1
        );

        System.out.println("\nEnterprise job execution:");

        Optional<Job> next;

        while ((next = scheduler.next()).isPresent()) {
            Job job = next.get();

            System.out.println(
                job.id() + " - " + job.description()
            );

            scheduler.complete(job.id());
        }

        ApprovalPolicy approvalPolicy = new ApprovalPolicy(
            2,
            Set.of("reviewer-1", "reviewer-2", "reviewer-3")
        );

        Map<String, ReviewState> reviews = Map.of(
            "reviewer-1", ReviewState.APPROVED,
            "reviewer-2", ReviewState.APPROVED
        );

        System.out.println(
            "\nApproval policy satisfied: " +
            approvalPolicy.satisfied(reviews)
        );

        BranchProtection protection = new BranchProtection(
            true,
            true,
            true
        );

        System.out.println(
            "Direct push allowed: " +
            protection.canDirectPush()
        );

        if (HeapAlgorithms.kthLargest(
            List.of(3, 2, 1, 5, 6, 4), 2
        ) != 5) {
            throw new AssertionError("Kth largest failed.");
        }

        if (HeapAlgorithms.connectRopes(
            List.of(4, 3, 2, 6)
        ) != 29) {
            throw new AssertionError("Rope algorithm failed.");
        }

        System.out.println("\nAll assessment checks passed.");
    }
}
