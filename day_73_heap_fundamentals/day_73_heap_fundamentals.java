import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Heap Fundamentals
 *
 * Enterprise workload management using:
 * - Complete binary tree principles
 * - Min and max heaps
 * - Array-backed heap representation
 * - Parent-child index relationships
 * - PriorityQueue
 * - Immutable job records
 * - Service-layer validation
 * - Job state transitions
 * - Failure handling
 */

public class Main {

    enum HeapMode {
        MIN,
        MAX
    }

    enum JobStatus {
        QUEUED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    record Job(
        String id,
        String name,
        int priority,
        int duration
    ) {
        Job {
            Objects.requireNonNull(id, "Job ID is required.");
            Objects.requireNonNull(name, "Job name is required.");

            if (id.isBlank() || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Job ID and name cannot be blank."
                );
            }

            if (duration < 0) {
                throw new IllegalArgumentException(
                    "Duration cannot be negative."
                );
            }
        }
    }

    record JobResult(
        Job job,
        JobStatus status,
        String message
    ) {}

    static class HeapException extends RuntimeException {
        HeapException(String message) {
            super(message);
        }
    }

    static class BinaryHeap<T> {

        private final List<T> data = new ArrayList<>();
        private final Comparator<T> comparator;

        BinaryHeap(Comparator<T> comparator) {
            this.comparator = Objects.requireNonNull(comparator);
        }

        BinaryHeap(
            List<T> values,
            Comparator<T> comparator
        ) {
            this.comparator = Objects.requireNonNull(comparator);
            data.addAll(values);
            heapify();
        }

        private int parent(int index) {
            return (index - 1) / 2;
        }

        private int left(int index) {
            return 2 * index + 1;
        }

        private int right(int index) {
            return 2 * index + 2;
        }

        int size() {
            return data.size();
        }

        boolean isEmpty() {
            return data.isEmpty();
        }

        private void swap(int a, int b) {
            T temporary = data.get(a);
            data.set(a, data.get(b));
            data.set(b, temporary);
        }

        private void siftUp(int index) {
            while (index > 0) {
                int p = parent(index);

                if (
                    comparator.compare(
                        data.get(index),
                        data.get(p)
                    ) >= 0
                ) {
                    break;
                }

                swap(index, p);
                index = p;
            }
        }

        private void siftDown(int index) {
            while (true) {
                int best = index;
                int left = left(index);
                int right = right(index);

                if (
                    left < size() &&
                    comparator.compare(
                        data.get(left),
                        data.get(best)
                    ) < 0
                ) {
                    best = left;
                }

                if (
                    right < size() &&
                    comparator.compare(
                        data.get(right),
                        data.get(best)
                    ) < 0
                ) {
                    best = right;
                }

                if (best == index) {
                    break;
                }

                swap(index, best);
                index = best;
            }
        }

        private void heapify() {
            for (int i = size() / 2 - 1; i >= 0; i--) {
                siftDown(i);
            }

            if (!validate()) {
                throw new HeapException(
                    "Heap construction failed."
                );
            }
        }

        void insert(T value) {
            Objects.requireNonNull(value);

            data.add(value);
            siftUp(size() - 1);

            if (!validate()) {
                throw new HeapException(
                    "Heap invariant violated after insertion."
                );
            }
        }

        T peek() {
            if (isEmpty()) {
                throw new HeapException(
                    "Cannot inspect an empty heap."
                );
            }

            return data.get(0);
        }

        T extract() {
            if (isEmpty()) {
                throw new HeapException(
                    "Cannot extract from an empty heap."
                );
            }

            T result = data.get(0);
            T last = data.remove(size() - 1);

            if (!isEmpty()) {
                data.set(0, last);
                siftDown(0);
            }

            if (!validate()) {
                throw new HeapException(
                    "Heap invariant violated after extraction."
                );
            }

            return result;
        }

        boolean validate() {
            for (int i = 0; i < size(); i++) {
                int left = left(i);
                int right = right(i);

                if (
                    left < size() &&
                    comparator.compare(
                        data.get(left),
                        data.get(i)
                    ) < 0
                ) {
                    return false;
                }

                if (
                    right < size() &&
                    comparator.compare(
                        data.get(right),
                        data.get(i)
                    ) < 0
                ) {
                    return false;
                }
            }

            return true;
        }

        List<T> snapshot() {
            return List.copyOf(data);
        }

        List<T> extractAll() {
            BinaryHeap<T> copy = new BinaryHeap<>(
                data,
                comparator
            );

            List<T> result = new ArrayList<>();

            while (!copy.isEmpty()) {
                result.add(copy.extract());
            }

            return List.copyOf(result);
        }

        List<String> relationships() {
            List<String> result = new ArrayList<>();

            for (int i = 0; i < size(); i++) {
                int p = parent(i);
                int l = left(i);
                int r = right(i);

                result.add(
                    "Index=" + i +
                    ", Value=" + data.get(i) +
                    ", Parent=" +
                    (i == 0 ? "None" : data.get(p)) +
                    ", Left=" +
                    (l < size() ? data.get(l) : "None") +
                    ", Right=" +
                    (r < size() ? data.get(r) : "None")
                );
            }

            return List.copyOf(result);
        }
    }

    static class JobService {

        private final BinaryHeap<Job> queue;
        private final List<JobResult> history = new ArrayList<>();
        private final java.util.Set<String> knownIds =
            new java.util.HashSet<>();

        JobService(HeapMode mode) {
            Comparator<Job> ordering = Comparator
                .comparingInt(Job::priority)
                .thenComparing(Job::id);

            if (mode == HeapMode.MAX) {
                ordering = Comparator
                    .comparingInt(Job::priority)
                    .reversed()
                    .thenComparing(Job::id);
            }

            queue = new BinaryHeap<>(ordering);
        }

        void submit(Job job) {
            Objects.requireNonNull(job);

            if (!knownIds.add(job.id())) {
                throw new HeapException(
                    "Duplicate job ID: " + job.id()
                );
            }

            queue.insert(job);

            history.add(
                new JobResult(
                    job,
                    JobStatus.QUEUED,
                    "Accepted into priority queue."
                )
            );
        }

        JobResult processNext() {
            if (queue.isEmpty()) {
                throw new HeapException(
                    "No queued jobs are available."
                );
            }

            Job job = queue.extract();

            history.add(
                new JobResult(
                    job,
                    JobStatus.RUNNING,
                    "Execution started."
                )
            );

            JobResult result;

            try {
                if (job.name().equals("failed-job")) {
                    throw new IllegalStateException(
                        "Execution rejected by service."
                    );
                }

                result = new JobResult(
                    job,
                    JobStatus.COMPLETED,
                    "Execution completed."
                );

            } catch (RuntimeException error) {
                result = new JobResult(
                    job,
                    JobStatus.FAILED,
                    error.getMessage()
                );
            }

            history.add(result);
            return result;
        }

        BinaryHeap<Job> getQueue() {
            return queue;
        }

        List<JobResult> getHistory() {
            return List.copyOf(history);
        }
    }

    public static void main(String[] args) {

        Comparator<Job> minOrdering = Comparator
            .comparingInt(Job::priority)
            .thenComparing(Job::id);

        Comparator<Job> maxOrdering = Comparator
            .comparingInt(Job::priority)
            .reversed()
            .thenComparing(Job::id);

        List<Job> jobs = List.of(
            new Job("J101", "database-backup", 4, 20),
            new Job("J102", "security-scan", 10, 15),
            new Job("J103", "report", 3, 10),
            new Job("J104", "monitoring", 8, 5),
            new Job("J105", "deployment", 6, 25),
            new Job("J106", "failed-job", 12, 8)
        );

        System.out.println("MIN HEAP");

        BinaryHeap<Job> minHeap = new BinaryHeap<>(
            jobs,
            minOrdering
        );

        System.out.println(minHeap.snapshot());
        System.out.println("MINIMUM: " + minHeap.peek());

        System.out.println("\nTREE RELATIONSHIPS");

        minHeap.relationships().forEach(System.out::println);

        System.out.println("\nMIN HEAP EXTRACTION");

        minHeap.extractAll().forEach(System.out::println);

        System.out.println("\nMAX HEAP");

        BinaryHeap<Job> maxHeap = new BinaryHeap<>(
            jobs,
            maxOrdering
        );

        System.out.println(maxHeap.snapshot());
        System.out.println("MAXIMUM: " + maxHeap.peek());

        System.out.println("\nMAX HEAP EXTRACTION");

        maxHeap.extractAll().forEach(System.out::println);

        System.out.println("\nENTERPRISE JOB SERVICE");

        JobService service = new JobService(HeapMode.MAX);

        jobs.forEach(service::submit);

        while (!service.getQueue().isEmpty()) {
            JobResult result = service.processNext();

            System.out.println(
                result.job().id() + " -> " +
                result.status() + " -> " +
                result.message()
            );
        }

        System.out.println("\nSTATUS AGGREGATION");

        service.getHistory()
            .stream()
            .collect(
                Collectors.groupingBy(
                    JobResult::status,
                    Collectors.counting()
                )
            )
            .forEach((status, count) ->
                System.out.println(status + ": " + count)
            );

        System.out.println("\nEDGE CASES");

        BinaryHeap<Integer> empty = new BinaryHeap<>(
            Integer::compare
        );

        try {
            empty.extract();
        } catch (HeapException error) {
            System.out.println("Expected: " + error.getMessage());
        }

        BinaryHeap<Integer> single = new BinaryHeap<>(
            Integer::compare
        );

        single.insert(42);
        System.out.println("Single element: " + single.extract());

        System.out.println("\nALL CHECKS COMPLETED.");
    }
}
