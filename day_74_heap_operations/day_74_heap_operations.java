import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Comparator;
import java.util.Objects;
import java.util.stream.Collectors;

/**
 * HEAP OPERATIONS
 *
 * Enterprise-oriented task scheduling with binary heaps.
 *
 * Operations:
 * - Insert
 * - Extract minimum
 * - Extract maximum
 * - Heapify
 *
 * Java 17 compatible.
 */
public class HeapOperations {

    enum HeapType {
        MIN_HEAP,
        MAX_HEAP
    }

    enum TaskState {
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED
    }

    record Task(
        String taskId,
        int priority,
        String description
    ) {
        Task {
            if (taskId == null || taskId.isBlank()) {
                throw new IllegalArgumentException(
                    "Task ID cannot be empty."
                );
            }

            if (priority < 1 || priority > 100) {
                throw new IllegalArgumentException(
                    "Priority must be between 1 and 100."
                );
            }

            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Description cannot be empty."
                );
            }
        }
    }

    record ProcessingResult(
        String taskId,
        int priority,
        TaskState state
    ) {}

    static class HeapException extends RuntimeException {
        HeapException(String message) {
            super(message);
        }
    }

    static class BinaryHeap<T> {

        private final List<T> data = new ArrayList<>();
        private final Comparator<? super T> comparator;
        private final HeapType type;

        BinaryHeap(
            Comparator<? super T> comparator,
            HeapType type
        ) {
            this.comparator = Objects.requireNonNull(comparator);
            this.type = Objects.requireNonNull(type);
        }

        private int compare(T first, T second) {
            int result = comparator.compare(first, second);

            return type == HeapType.MIN_HEAP
                ? result
                : -Integer.signum(result);
        }

        int size() {
            return data.size();
        }

        boolean isEmpty() {
            return data.isEmpty();
        }

        void insert(T value) {
            Objects.requireNonNull(value, "Null heap values are forbidden.");

            data.add(value);
            siftUp(data.size() - 1);
        }

        T peek() {
            if (isEmpty()) {
                throw new HeapException("Heap is empty.");
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
            T last = data.remove(data.size() - 1);

            if (!data.isEmpty()) {
                data.set(0, last);
                siftDown(0);
            }

            return result;
        }

        private void siftUp(int index) {
            while (index > 0) {
                int parent = (index - 1) / 2;

                if (
                    compare(data.get(index), data.get(parent)) >= 0
                ) {
                    break;
                }

                Collections.swap(data, index, parent);
                index = parent;
            }
        }

        private void siftDown(int index) {
            int size = data.size();

            while (true) {
                int best = index;
                int left = 2 * index + 1;
                int right = 2 * index + 2;

                if (
                    left < size &&
                    compare(data.get(left), data.get(best)) < 0
                ) {
                    best = left;
                }

                if (
                    right < size &&
                    compare(data.get(right), data.get(best)) < 0
                ) {
                    best = right;
                }

                if (best == index) {
                    break;
                }

                Collections.swap(data, index, best);
                index = best;
            }
        }

        // Floyd's O(n) bottom-up heap construction.
        void heapify(List<T> values) {
            Objects.requireNonNull(values);

            if (values.stream().anyMatch(Objects::isNull)) {
                throw new IllegalArgumentException(
                    "Heap cannot contain null values."
                );
            }

            data.clear();
            data.addAll(values);

            for (int i = data.size() / 2 - 1; i >= 0; i--) {
                siftDown(i);
            }
        }

        boolean validate() {
            for (int i = 1; i < data.size(); i++) {
                int parent = (i - 1) / 2;

                if (
                    compare(data.get(i), data.get(parent)) < 0
                ) {
                    return false;
                }
            }

            return true;
        }

        List<T> snapshot() {
            return List.copyOf(data);
        }
    }

    static class TaskScheduler {

        private final BinaryHeap<Task> urgentTasks;
        private final BinaryHeap<Task> lowPriorityTasks;

        private final List<ProcessingResult> history =
            new ArrayList<>();

        TaskScheduler() {
            Comparator<Task> byPriority =
                Comparator.comparingInt(Task::priority)
                    .thenComparing(Task::taskId);

            urgentTasks = new BinaryHeap<>(
                byPriority,
                HeapType.MAX_HEAP
            );

            lowPriorityTasks = new BinaryHeap<>(
                byPriority,
                HeapType.MIN_HEAP
            );
        }

        void submit(Task task) {
            Objects.requireNonNull(task);

            urgentTasks.insert(task);
            lowPriorityTasks.insert(task);
        }

        ProcessingResult processMostUrgent() {
            Task task = urgentTasks.extract();

            ProcessingResult result = new ProcessingResult(
                task.taskId(),
                task.priority(),
                TaskState.COMPLETED
            );

            history.add(result);
            return result;
        }

        ProcessingResult processLeastUrgent() {
            Task task = lowPriorityTasks.extract();

            ProcessingResult result = new ProcessingResult(
                task.taskId(),
                task.priority(),
                TaskState.COMPLETED
            );

            history.add(result);
            return result;
        }

        void rebuild(List<Task> tasks) {
            urgentTasks.heapify(tasks);
            lowPriorityTasks.heapify(tasks);
        }

        List<ProcessingResult> history() {
            return List.copyOf(history);
        }

        void display() {
            System.out.println(
                "Urgent heap: " + urgentTasks.snapshot()
            );

            System.out.println(
                "Low-priority heap: " + lowPriorityTasks.snapshot()
            );
        }

        void verify() {
            if (
                !urgentTasks.validate() ||
                !lowPriorityTasks.validate()
            ) {
                throw new IllegalStateException(
                    "Heap invariant violation."
                );
            }
        }
    }

    static void demonstrateBasicOperations() {
        System.out.println("\n=== BASIC HEAP OPERATIONS ===");

        BinaryHeap<Integer> minHeap = new BinaryHeap<>(
            Comparator.naturalOrder(),
            HeapType.MIN_HEAP
        );

        BinaryHeap<Integer> maxHeap = new BinaryHeap<>(
            Comparator.naturalOrder(),
            HeapType.MAX_HEAP
        );

        List<Integer> values = List.of(
            45, 12, 30, 8, 25, 60, 18, 8
        );

        minHeap.heapify(values);
        maxHeap.heapify(values);

        System.out.println("Minimum: " + minHeap.peek());
        System.out.println("Maximum: " + maxHeap.peek());

        minHeap.insert(5);
        maxHeap.insert(75);

        System.out.println(
            "Extract minimum: " + minHeap.extract()
        );

        System.out.println(
            "Extract maximum: " + maxHeap.extract()
        );

        if (!minHeap.validate() || !maxHeap.validate()) {
            throw new IllegalStateException(
                "Invalid heap structure."
            );
        }
    }

    static void demonstrateScheduling() {
        System.out.println("\n=== ENTERPRISE TASK SCHEDULING ===");

        TaskScheduler scheduler = new TaskScheduler();

        List<Task> tasks = List.of(
            new Task("TASK-101", 90, "Critical security patch"),
            new Task("TASK-102", 30, "Documentation update"),
            new Task("TASK-103", 75, "Production deployment"),
            new Task("TASK-104", 50, "Database optimization"),
            new Task("TASK-105", 95, "Service outage recovery")
        );

        tasks.forEach(scheduler::submit);

        scheduler.display();
        scheduler.verify();

        System.out.println(
            "Most urgent: " + scheduler.processMostUrgent()
        );

        System.out.println(
            "Least urgent: " + scheduler.processLeastUrgent()
        );

        System.out.println(
            "Processing history: " + scheduler.history()
        );

        scheduler.verify();
    }

    static void demonstrateHeapSort() {
        System.out.println("\n=== HEAP SORT ===");

        List<Integer> values = List.of(
            34, 12, 5, 78, 23, 9, 56
        );

        BinaryHeap<Integer> heap = new BinaryHeap<>(
            Comparator.naturalOrder(),
            HeapType.MIN_HEAP
        );

        heap.heapify(values);

        List<Integer> sorted = new ArrayList<>();

        while (!heap.isEmpty()) {
            sorted.add(heap.extract());
        }

        System.out.println("Sorted: " + sorted);

        if (!sorted.equals(
            values.stream().sorted().collect(Collectors.toList())
        )) {
            throw new IllegalStateException("Sorting failed.");
        }
    }

    static void demonstrateFailures() {
        System.out.println("\n=== FAILURE HANDLING ===");

        BinaryHeap<Integer> heap = new BinaryHeap<>(
            Comparator.naturalOrder(),
            HeapType.MIN_HEAP
        );

        try {
            heap.extract();
        } catch (HeapException error) {
            System.out.println(error.getMessage());
        }

        try {
            new Task(
                "TASK-INVALID",
                150,
                "Invalid priority task"
            );
        } catch (IllegalArgumentException error) {
            System.out.println(error.getMessage());
        }
    }

    public static void main(String[] args) {
        demonstrateBasicOperations();
        demonstrateScheduling();
        demonstrateHeapSort();
        demonstrateFailures();

        System.out.println("\nAll tests completed.");
    }
}
