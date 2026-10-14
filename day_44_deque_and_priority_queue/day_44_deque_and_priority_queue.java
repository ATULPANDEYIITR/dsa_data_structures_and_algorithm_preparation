import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;

public class RepositoryWorkScheduler {

    enum WorkState {
        QUEUED,
        IN_PROGRESS,
        COMPLETED,
        CANCELLED
    }

    enum QueuePolicy {
        LOWEST_PRIORITY_NUMBER_FIRST,
        HIGHEST_PRIORITY_NUMBER_FIRST
    }

    record WorkItem(
            String id,
            String repository,
            String description,
            int priority,
            long submittedAt
    ) {
        WorkItem {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Work ID is required.");
            }
            if (repository == null || repository.isBlank()) {
                throw new IllegalArgumentException("Repository is required.");
            }
            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException("Description is required.");
            }
            if (priority < 0 || priority > 100) {
                throw new IllegalArgumentException(
                        "Priority must be between 0 and 100.");
            }
            if (submittedAt < 0) {
                throw new IllegalArgumentException("Submission time cannot be negative.");
            }
        }
    }

    static final class ScheduledWork {
        private final WorkItem item;
        private WorkState state = WorkState.QUEUED;

        ScheduledWork(WorkItem item) {
            this.item = Objects.requireNonNull(item);
        }

        WorkItem item() {
            return item;
        }

        WorkState state() {
            return state;
        }

        void transitionTo(WorkState next) {
            boolean allowed = switch (state) {
                case QUEUED ->
                        next == WorkState.IN_PROGRESS || next == WorkState.CANCELLED;
                case IN_PROGRESS ->
                        next == WorkState.COMPLETED || next == WorkState.CANCELLED;
                case COMPLETED, CANCELLED -> false;
            };

            if (!allowed) {
                throw new IllegalStateException(
                        "Invalid transition from " + state + " to " + next
                                + " for " + item.id());
            }
            state = next;
        }
    }

    static final class WorkScheduler {
        private final Deque<ScheduledWork> urgent = new ArrayDeque<>();
        private final PriorityQueue<ScheduledWork> priorityQueue;
        private final Set<String> activeIds = new HashSet<>();
        private final QueuePolicy policy;

        WorkScheduler(QueuePolicy policy) {
            this.policy = Objects.requireNonNull(policy);

            Comparator<ScheduledWork> comparator = Comparator
                    .comparingInt((ScheduledWork work) -> work.item().priority())
                    .thenComparingLong(work -> work.item().submittedAt())
                    .thenComparing(work -> work.item().id());

            if (policy == QueuePolicy.HIGHEST_PRIORITY_NUMBER_FIRST) {
                comparator = Comparator
                        .comparingInt(
                                (ScheduledWork work) -> work.item().priority())
                        .reversed()
                        .thenComparingLong(work -> work.item().submittedAt())
                        .thenComparing(work -> work.item().id());
            }

            priorityQueue = new PriorityQueue<>(comparator);
        }

        void submit(WorkItem item, boolean urgentWork) {
            Objects.requireNonNull(item, "Work item is required.");
            if (!activeIds.add(item.id())) {
                throw new IllegalArgumentException(
                        "Duplicate active work ID: " + item.id());
            }

            ScheduledWork scheduled = new ScheduledWork(item);
            if (urgentWork) {
                // addFirst makes urgent intake a double-ended queue operation.
                urgent.addFirst(scheduled);
            }
            priorityQueue.add(scheduled);
        }

        ScheduledWork takeUrgent() {
            ScheduledWork work = urgent.pollFirst();
            if (work == null) {
                throw new IllegalStateException("No urgent work is waiting.");
            }
            activeIds.remove(work.item().id());
            return work;
        }

        ScheduledWork dispatchByPriority() {
            ScheduledWork work = priorityQueue.poll();
            if (work == null) {
                throw new IllegalStateException("No scheduled work is waiting.");
            }
            activeIds.remove(work.item().id());
            return work;
        }

        QueuePolicy policy() {
            return policy;
        }

        int scheduledCount() {
            return priorityQueue.size();
        }
    }

    private static WorkItem work(
            String id, String repository, String description,
            int priority, long time) {
        return new WorkItem(id, repository, description, priority, time);
    }

    public static void main(String[] args) {
        WorkScheduler scheduler =
                new WorkScheduler(QueuePolicy.HIGHEST_PRIORITY_NUMBER_FIRST);

        scheduler.submit(work(
                "PR-881", "payment-service",
                "Investigate failed release", 100, 120), true);

        scheduler.submit(work(
                "PR-882", "identity-service",
                "Update token validation", 80, 130), true);

        scheduler.submit(work(
                "PR-883", "documentation",
                "Clarify deployment instructions", 20, 140), false);

        scheduler.submit(work(
                "PR-884", "database-service",
                "Resolve connection pool saturation", 90, 150), false);

        System.out.println("Immediate intake");
        ScheduledWork urgentWork = scheduler.takeUrgent();
        urgentWork.transitionTo(WorkState.IN_PROGRESS);
        System.out.println(urgentWork.item().id() + " " + urgentWork.state());

        urgentWork.transitionTo(WorkState.COMPLETED);
        System.out.println("Finished " + urgentWork.item().id());

        System.out.println("\nPriority dispatch using "
                + scheduler.policy());

        List<ScheduledWork> dispatched = new ArrayList<>();
        while (scheduler.scheduledCount() > 0) {
            ScheduledWork next = scheduler.dispatchByPriority();
            next.transitionTo(WorkState.IN_PROGRESS);
            dispatched.add(next);
            System.out.println(
                    next.item().id() + " priority=" + next.item().priority());
        }

        try {
            urgentWork.transitionTo(WorkState.QUEUED);
        } catch (IllegalStateException error) {
            System.out.println("Rejected invalid state transition: "
                    + error.getMessage());
        }

        try {
            work("PR-885", "payment-service", "Invalid priority", 101, 160);
        } catch (IllegalArgumentException error) {
            System.out.println("Rejected work item: " + error.getMessage());
        }

        // A min-priority policy changes ordering without changing the domain model.
        WorkScheduler maintenanceScheduler =
                new WorkScheduler(QueuePolicy.LOWEST_PRIORITY_NUMBER_FIRST);

        maintenanceScheduler.submit(work(
                "PR-886", "docs", "Low numeric priority", 10, 200), false);
        maintenanceScheduler.submit(work(
                "PR-887", "security", "Higher numeric priority", 90, 210), false);

        System.out.println("\nMin-priority policy dispatch");
        while (maintenanceScheduler.scheduledCount() > 0) {
            ScheduledWork next = maintenanceScheduler.dispatchByPriority();
            System.out.println(
                    next.item().id() + " priority=" + next.item().priority());
        }
    }
}
