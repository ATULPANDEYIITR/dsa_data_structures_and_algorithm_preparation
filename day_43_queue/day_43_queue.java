import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise repository queue and validation workflow.
 *
 * Java 17 or later.
 *
 * Save as QueueGovernance.java
 * Compile: javac QueueGovernance.java
 * Run: java QueueGovernance
 */

public class QueueGovernance {

    static class QueueEmptyException extends IllegalStateException {
        QueueEmptyException(String message) {
            super(message);
        }
    }

    static class QueueFullException extends IllegalStateException {
        QueueFullException(String message) {
            super(message);
        }
    }

    static final class Queue<T> {
        private final Deque<T> items = new ArrayDeque<>();

        public void enqueue(T item) {
            items.addLast(Objects.requireNonNull(item, "Queue item cannot be null."));
        }

        public T dequeue() {
            if (items.isEmpty()) {
                throw new QueueEmptyException("Cannot dequeue from an empty queue.");
            }
            return items.removeFirst();
        }

        public T front() {
            if (items.isEmpty()) {
                throw new QueueEmptyException("Cannot inspect an empty queue.");
            }
            return items.getFirst();
        }

        public T rear() {
            if (items.isEmpty()) {
                throw new QueueEmptyException("Cannot inspect an empty queue.");
            }
            return items.getLast();
        }

        public boolean isEmpty() {
            return items.isEmpty();
        }

        public int size() {
            return items.size();
        }

        public List<T> snapshot() {
            return List.copyOf(items);
        }
    }

    static final class BoundedQueue<T> {
        private final int capacity;
        private final Queue<T> queue = new Queue<>();

        BoundedQueue(int capacity) {
            if (capacity <= 0) {
                throw new IllegalArgumentException("Capacity must be positive.");
            }
            this.capacity = capacity;
        }

        public void enqueue(T item) {
            if (queue.size() >= capacity) {
                throw new QueueFullException("Queue capacity has been reached.");
            }
            queue.enqueue(item);
        }

        public T dequeue() {
            return queue.dequeue();
        }

        public T front() {
            return queue.front();
        }

        public T rear() {
            return queue.rear();
        }

        public boolean isFull() {
            return queue.size() == capacity;
        }

        public int size() {
            return queue.size();
        }
    }

    enum CheckState {
        QUEUED,
        RUNNING,
        PASSED,
        FAILED
    }

    record ValidationJob(
            long id,
            String repository,
            String branch,
            String commit,
            String checkName) {

        ValidationJob {
            if (id <= 0) {
                throw new IllegalArgumentException("Job ID must be positive.");
            }

            repository = requireText(repository, "Repository");
            branch = requireText(branch, "Branch");
            commit = requireText(commit, "Commit");
            checkName = requireText(checkName, "Check name");
        }

        private static String requireText(String value, String field) {
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException(field + " cannot be blank.");
            }
            return value;
        }
    }

    static final class ValidationService {
        private final BoundedQueue<ValidationJob> pending;
        private final Map<Long, CheckState> states = new HashMap<>();
        private final Set<Long> knownIds = new HashSet<>();

        ValidationService(int capacity) {
            pending = new BoundedQueue<>(capacity);
        }

        public void submit(ValidationJob job) {
            Objects.requireNonNull(job, "Job cannot be null.");

            if (knownIds.contains(job.id())) {
                throw new IllegalArgumentException("Duplicate job ID: " + job.id());
            }

            // Reserve the identifier only after successful queue insertion.
            // A full queue therefore does not leave a false registration.
            pending.enqueue(job);
            knownIds.add(job.id());
            states.put(job.id(), CheckState.QUEUED);
        }

        public ValidationJob startNext() {
            ValidationJob job = pending.dequeue();

            if (states.get(job.id()) != CheckState.QUEUED) {
                throw new IllegalStateException("Job is not in QUEUED state.");
            }

            states.put(job.id(), CheckState.RUNNING);
            return job;
        }

        public void complete(long jobId, boolean passed) {
            CheckState current = states.get(jobId);

            if (current == null) {
                throw new IllegalArgumentException("Unknown job ID: " + jobId);
            }

            if (current != CheckState.RUNNING) {
                throw new IllegalStateException(
                        "Only RUNNING jobs can be completed: " + jobId);
            }

            states.put(jobId, passed ? CheckState.PASSED : CheckState.FAILED);
        }

        public CheckState stateOf(long jobId) {
            CheckState state = states.get(jobId);

            if (state == null) {
                throw new IllegalArgumentException("Unknown job ID: " + jobId);
            }

            return state;
        }

        public int pendingCount() {
            return pending.size();
        }

        public boolean hasPendingJobs() {
            return pending.size() > 0;
        }

        public List<ValidationJob> pendingSnapshot() {
            return pending.queue.snapshot();
        }
    }

    private static void demonstrateQueue() {
        System.out.println("Core queue operations");

        Queue<String> queue = new Queue<>();
        queue.enqueue("compile");
        queue.enqueue("unit-test");
        queue.enqueue("dependency-audit");

        System.out.println("Front: " + queue.front());
        System.out.println("Rear: " + queue.rear());
        System.out.println("Dequeue: " + queue.dequeue());
        System.out.println("Remaining: " + queue.snapshot());
    }

    private static void demonstrateValidationService() {
        System.out.println("\nEnterprise validation service");

        ValidationService service = new ValidationService(4);

        service.submit(new ValidationJob(
                501, "inventory-api", "feature/cache", "c10fa82", "compile"));
        service.submit(new ValidationJob(
                502, "inventory-api", "feature/cache", "c10fa82", "unit-tests"));
        service.submit(new ValidationJob(
                503, "inventory-api", "feature/cache", "c10fa82", "security-audit"));

        System.out.println("Pending checks: " + service.pendingCount());
        System.out.println("Queue front: " + service.pendingSnapshot().getFirst().checkName());
        System.out.println("Queue rear: " + service.pendingSnapshot().getLast().checkName());

        while (service.hasPendingJobs()) {
            ValidationJob job = service.startNext();
            boolean passed = !job.checkName().equals("security-audit");

            service.complete(job.id(), passed);

            System.out.println(
                    job.id() + " " + job.checkName() + " -> "
                            + service.stateOf(job.id()));
        }

        try {
            service.complete(501, true);
        } catch (IllegalStateException error) {
            System.out.println("Invalid state transition: " + error.getMessage());
        }

        try {
            service.submit(new ValidationJob(
                    501, "inventory-api", "main", "d83e901", "compile"));
        } catch (IllegalArgumentException error) {
            System.out.println("Duplicate rejected: " + error.getMessage());
        }

        try {
            service.startNext();
        } catch (QueueEmptyException error) {
            System.out.println("Empty queue protection: " + error.getMessage());
        }
    }

    private static void demonstrateCapacityLimit() {
        System.out.println("\nBounded queue");

        BoundedQueue<String> queue = new BoundedQueue<>(2);
        queue.enqueue("deployment-A");
        queue.enqueue("deployment-B");

        System.out.println("Full: " + queue.isFull());

        try {
            queue.enqueue("deployment-C");
        } catch (QueueFullException error) {
            System.out.println("Rejected: " + error.getMessage());
        }

        System.out.println("Removed: " + queue.dequeue());
        queue.enqueue("deployment-C");
        System.out.println("New rear: " + queue.rear());
    }

    public static void main(String[] args) {
        demonstrateQueue();
        demonstrateCapacityLimit();
        demonstrateValidationService();
    }
}
