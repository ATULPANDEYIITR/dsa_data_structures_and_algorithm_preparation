import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Priority Queues: Enterprise Job Scheduling.
 *
 * Features:
 * - Min-priority and max-priority queues.
 * - Stable scheduling.
 * - Immutable domain records.
 * - Priority updates and cancellation.
 * - Approval of high-impact deployment jobs.
 * - Merge-ready scheduling decisions.
 * - Top-K selection.
 * - Running median.
 *
 * Runtime: Java 17
 * Compile: javac Main.java
 * Execute: java Main
 */

public class Main {

    enum PriorityMode {
        MIN,
        MAX
    }

    enum JobStatus {
        PENDING,
        RUNNING,
        COMPLETED,
        CANCELLED,
        FAILED
    }

    enum JobCategory {
        BUILD,
        TEST,
        SECURITY_SCAN,
        DEPLOYMENT,
        REPORT
    }

    record Job(
        String id,
        String description,
        JobCategory category,
        int priority,
        JobStatus status,
        long sequence,
        long version
    ) {
        Job {
            Objects.requireNonNull(id);
            Objects.requireNonNull(description);
            Objects.requireNonNull(category);
            Objects.requireNonNull(status);

            if (id.isBlank() || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Job identifiers and descriptions cannot be empty"
                );
            }
        }

        Job withPriority(int value) {
            return new Job(
                id, description, category, value,
                status, sequence, version + 1
            );
        }

        Job withStatus(JobStatus value) {
            return new Job(
                id, description, category, priority,
                value, sequence, version
            );
        }
    }

    record QueueEntry(
        int priority,
        long sequence,
        String jobId,
        long version
    ) {}

    static class PriorityQueueService<T> {

        private final PriorityQueue<T> queue;

        PriorityQueueService(PriorityMode mode, Comparator<T> comparator) {
            Objects.requireNonNull(mode);
            Objects.requireNonNull(comparator);

            Comparator<T> effective = mode == PriorityMode.MIN
                ? comparator
                : comparator.reversed();

            queue = new PriorityQueue<>(effective);
        }

        void add(T value) {
            queue.add(value);
        }

        T remove() {
            if (queue.isEmpty()) {
                throw new IllegalStateException("Queue is empty");
            }

            return queue.remove();
        }

        T peek() {
            if (queue.isEmpty()) {
                throw new IllegalStateException("Queue is empty");
            }

            return queue.element();
        }

        int size() {
            return queue.size();
        }
    }

    static class SchedulingPolicy {

        private final int minimumDeploymentPriority;
        private final boolean requireSecurityScan;

        SchedulingPolicy(
            int minimumDeploymentPriority,
            boolean requireSecurityScan
        ) {
            if (minimumDeploymentPriority < 0) {
                throw new IllegalArgumentException(
                    "Deployment priority threshold cannot be negative"
                );
            }

            this.minimumDeploymentPriority =
                minimumDeploymentPriority;

            this.requireSecurityScan = requireSecurityScan;
        }

        boolean isEligible(
            Job job,
            boolean securityScanPassed,
            boolean deploymentApproved
        ) {
            if (job.category() != JobCategory.DEPLOYMENT) {
                return true;
            }

            if (job.priority() < minimumDeploymentPriority) {
                return false;
            }

            if (requireSecurityScan && !securityScanPassed) {
                return false;
            }

            return deploymentApproved;
        }
    }

    static class Scheduler {

        private final PriorityQueue<QueueEntry> queue =
            new PriorityQueue<>(
                Comparator
                    .comparingInt(QueueEntry::priority)
                    .reversed()
                    .thenComparingLong(QueueEntry::sequence)
            );

        private final Map<String, Job> jobs = new HashMap<>();

        private long nextSequence = 0;

        private final SchedulingPolicy policy;

        Scheduler(SchedulingPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        synchronized String submit(
            String description,
            JobCategory category,
            int priority
        ) {
            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Description is required"
                );
            }

            Objects.requireNonNull(category);

            String id = UUID.randomUUID().toString();

            Job job = new Job(
                id,
                description,
                category,
                priority,
                JobStatus.PENDING,
                nextSequence++,
                0
            );

            jobs.put(id, job);
            enqueue(job);

            return id;
        }

        private void enqueue(Job job) {
            queue.add(
                new QueueEntry(
                    job.priority(),
                    job.sequence(),
                    job.id(),
                    job.version()
                )
            );
        }

        synchronized void updatePriority(String id, int priority) {
            Job job = requireJob(id);

            if (job.status() != JobStatus.PENDING) {
                throw new IllegalStateException(
                    "Only pending jobs can be reprioritized"
                );
            }

            Job updated = job.withPriority(priority);

            jobs.put(id, updated);
            enqueue(updated);
        }

        synchronized void cancel(String id) {
            Job job = requireJob(id);

            if (job.status() != JobStatus.PENDING) {
                throw new IllegalStateException(
                    "Only pending jobs can be cancelled"
                );
            }

            jobs.put(id, job.withStatus(JobStatus.CANCELLED));
        }

        synchronized Job claimNext(
            boolean securityScanPassed,
            boolean deploymentApproved
        ) {
            while (!queue.isEmpty()) {
                QueueEntry entry = queue.poll();

                Job job = jobs.get(entry.jobId());

                if (job == null) {
                    continue;
                }

                // Ignore outdated priority-update entries.
                if (entry.version() != job.version()) {
                    continue;
                }

                if (job.status() != JobStatus.PENDING) {
                    continue;
                }

                if (!policy.isEligible(
                    job,
                    securityScanPassed,
                    deploymentApproved
                )) {
                    // The job remains pending. A production system
                    // may use a separate blocked-job queue.
                    continue;
                }

                Job running = job.withStatus(JobStatus.RUNNING);
                jobs.put(job.id(), running);

                return running;
            }

            return null;
        }

        synchronized void finish(String id, boolean success) {
            Job job = requireJob(id);

            if (job.status() != JobStatus.RUNNING) {
                throw new IllegalStateException(
                    "Job is not running"
                );
            }

            jobs.put(
                id,
                job.withStatus(
                    success
                        ? JobStatus.COMPLETED
                        : JobStatus.FAILED
                )
            );
        }

        synchronized Job requireJob(String id) {
            Job job = jobs.get(id);

            if (job == null) {
                throw new IllegalArgumentException("Unknown job: " + id);
            }

            return job;
        }

        synchronized Map<JobStatus, Long> report() {
            return jobs.values()
                .stream()
                .collect(
                    Collectors.groupingBy(
                        Job::status,
                        Collectors.counting()
                    )
                );
        }

        synchronized List<Job> allJobs() {
            return List.copyOf(jobs.values());
        }
    }

    static List<Integer> topKLargest(
        List<Integer> values,
        int k
    ) {
        if (k < 0 || k > values.size()) {
            throw new IllegalArgumentException("Invalid k");
        }

        PriorityQueue<Integer> heap = new PriorityQueue<>();

        for (Integer value : values) {
            Objects.requireNonNull(value);

            if (heap.size() < k) {
                heap.add(value);
            } else if (k > 0 && value > heap.peek()) {
                heap.poll();
                heap.add(value);
            }
        }

        List<Integer> result = new ArrayList<>(heap);
        result.sort(Comparator.reverseOrder());

        return result;
    }

    static int kthSmallest(List<Integer> values, int k) {
        if (k <= 0 || k > values.size()) {
            throw new IllegalArgumentException("Invalid k");
        }

        PriorityQueue<Integer> heap =
            new PriorityQueue<>(Comparator.reverseOrder());

        for (Integer value : values) {
            Objects.requireNonNull(value);
            heap.add(value);

            if (heap.size() > k) {
                heap.poll();
            }
        }

        return heap.peek();
    }

    static class RunningMedian {

        private final PriorityQueue<Integer> lower =
            new PriorityQueue<>(Comparator.reverseOrder());

        private final PriorityQueue<Integer> upper =
            new PriorityQueue<>();

        void add(int value) {
            if (lower.isEmpty() || value <= lower.peek()) {
                lower.add(value);
            } else {
                upper.add(value);
            }

            if (lower.size() > upper.size() + 1) {
                upper.add(lower.poll());
            } else if (upper.size() > lower.size()) {
                lower.add(upper.poll());
            }
        }

        double median() {
            if (lower.isEmpty()) {
                throw new IllegalStateException(
                    "Median is undefined for an empty collection"
                );
            }

            if (lower.size() == upper.size()) {
                return (
                    (long) lower.peek() + (long) upper.peek()
                ) / 2.0;
            }

            return lower.peek();
        }
    }

    static void demonstrateBasicQueues() {
        System.out.println("MIN-PRIORITY QUEUE");

        PriorityQueueService<Integer> min =
            new PriorityQueueService<>(
                PriorityMode.MIN,
                Comparator.naturalOrder()
            );

        for (int value : List.of(40, 10, 30, 5, 20)) {
            min.add(value);
        }

        while (min.size() > 0) {
            System.out.print(min.remove() + " ");
        }

        System.out.println("\n\nMAX-PRIORITY QUEUE");

        PriorityQueueService<Integer> max =
            new PriorityQueueService<>(
                PriorityMode.MAX,
                Comparator.naturalOrder()
            );

        for (int value : List.of(40, 10, 30, 5, 20)) {
            max.add(value);
        }

        while (max.size() > 0) {
            System.out.print(max.remove() + " ");
        }

        System.out.println();
    }

    static void demonstrateScheduler() {
        SchedulingPolicy policy =
            new SchedulingPolicy(7, true);

        Scheduler scheduler = new Scheduler(policy);

        String build = scheduler.submit(
            "Compile application",
            JobCategory.BUILD,
            5
        );

        scheduler.submit(
            "Run security scan",
            JobCategory.SECURITY_SCAN,
            10
        );

        String tests = scheduler.submit(
            "Execute test suite",
            JobCategory.TEST,
            6
        );

        String deployment = scheduler.submit(
            "Deploy production release",
            JobCategory.DEPLOYMENT,
            9
        );

        scheduler.submit(
            "Generate engineering report",
            JobCategory.REPORT,
            2
        );

        scheduler.updatePriority(tests, 8);
        scheduler.cancel(build);

        System.out.println("\nENTERPRISE SCHEDULER");

        Job job;

        while ((job = scheduler.claimNext(true, true)) != null) {
            System.out.println(
                "Executing: " + job.description()
                + " | priority=" + job.priority()
            );

            boolean success = !job.id().equals(deployment);

            scheduler.finish(job.id(), success);
        }

        System.out.println("Final states:");

        scheduler.allJobs().forEach(
            j -> System.out.println(
                j.description() + " -> " + j.status()
            )
        );

        System.out.println("Report: " + scheduler.report());
    }

    static void demonstrateSelection() {
        List<Integer> values =
            List.of(17, 4, 29, 11, 8, 35, 21, 3, 29);

        System.out.println("\nSELECTION");
        System.out.println("Top 3: " + topKLargest(values, 3));
        System.out.println(
            "Third smallest: " + kthSmallest(values, 3)
        );
    }

    static void demonstrateMedian() {
        RunningMedian tracker = new RunningMedian();

        System.out.println("\nRUNNING MEDIAN");

        for (int value : List.of(12, 4, 5, 3, 8, 7, 15, 20)) {
            tracker.add(value);

            System.out.println(
                "Inserted " + value + " -> " + tracker.median()
            );
        }
    }

    static void runTests() {
        if (!topKLargest(List.of(4, 9, 1, 7, 3), 2)
            .equals(List.of(9, 7))) {
            throw new AssertionError("Top-K test failed");
        }

        if (kthSmallest(List.of(5, 1, 3, 2), 2) != 2) {
            throw new AssertionError("K-th smallest test failed");
        }

        RunningMedian median = new RunningMedian();

        for (int value : List.of(1, 3, 2, 4)) {
            median.add(value);
        }

        if (median.median() != 2.5) {
            throw new AssertionError("Median test failed");
        }

        PriorityQueueService<Integer> queue =
            new PriorityQueueService<>(
                PriorityMode.MIN,
                Comparator.naturalOrder()
            );

        queue.add(8);
        queue.add(2);
        queue.add(5);

        if (queue.remove() != 2) {
            throw new AssertionError("Min-heap test failed");
        }

        Scheduler scheduler = new Scheduler(
            new SchedulingPolicy(5, false)
        );

        String first = scheduler.submit(
            "Normal job", JobCategory.TEST, 1
        );

        scheduler.submit(
            "Urgent job", JobCategory.TEST, 2
        );

        scheduler.updatePriority(first, 5);

        Job next = scheduler.claimNext(true, true);

        if (!next.id().equals(first)) {
            throw new AssertionError("Reprioritization failed");
        }

        System.out.println("\nAll tests passed.");
    }

    public static void main(String[] args) {
        demonstrateBasicQueues();
        demonstrateScheduler();
        demonstrateSelection();
        demonstrateMedian();
        runTests();
    }
}
