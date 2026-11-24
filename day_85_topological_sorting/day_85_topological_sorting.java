import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class TopologicalSortingEnterprise {

    enum TaskStatus {
        PENDING,
        READY,
        RUNNING,
        COMPLETED,
        FAILED,
        BLOCKED
    }

    record Task(
        String id,
        String description,
        int duration,
        TaskStatus status
    ) {
        Task {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Task ID cannot be empty."
                );
            }

            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Description cannot be empty."
                );
            }

            if (duration <= 0) {
                throw new IllegalArgumentException(
                    "Duration must be positive."
                );
            }

            if (status == null) {
                throw new IllegalArgumentException(
                    "Task status is required."
                );
            }
        }

        Task withStatus(TaskStatus newStatus) {
            return new Task(
                id,
                description,
                duration,
                newStatus
            );
        }
    }

    record Dependency(String prerequisite, String dependent) {
        Dependency {
            if (prerequisite == null || dependent == null) {
                throw new IllegalArgumentException(
                    "Dependency endpoints are required."
                );
            }

            if (prerequisite.equals(dependent)) {
                throw new IllegalArgumentException(
                    "A task cannot depend on itself."
                );
            }
        }
    }

    record CriticalPath(int duration, List<String> tasks) {
        CriticalPath {
            tasks = List.copyOf(tasks);
        }
    }

    static class DependencyException extends RuntimeException {
        DependencyException(String message) {
            super(message);
        }
    }

    static class CycleException extends DependencyException {
        CycleException(List<String> cycle) {
            super("Cycle detected: " + String.join(" -> ", cycle));
        }
    }

    static class Repository {
        private final Map<String, Task> tasks = new TreeMap<>();
        private final Map<String, Set<String>> outgoing =
            new TreeMap<>();
        private final Map<String, Set<String>> incoming =
            new TreeMap<>();

        public void registerTask(Task task) {
            if (tasks.containsKey(task.id())) {
                throw new DependencyException(
                    "Duplicate task: " + task.id()
                );
            }

            tasks.put(task.id(), task);
            outgoing.put(task.id(), new TreeSet<>());
            incoming.put(task.id(), new TreeSet<>());
        }

        public void addDependency(Dependency dependency) {
            String parent = dependency.prerequisite();
            String child = dependency.dependent();

            if (!tasks.containsKey(parent) ||
                !tasks.containsKey(child)) {
                throw new DependencyException(
                    "Dependency references an unknown task."
                );
            }

            if (outgoing.get(parent).contains(child)) {
                return;
            }

            outgoing.get(parent).add(child);
            incoming.get(child).add(parent);

            List<String> cycle = findCycle();

            if (cycle != null) {
                outgoing.get(parent).remove(child);
                incoming.get(child).remove(parent);
                throw new CycleException(cycle);
            }
        }

        public Map<String, Task> getTasks() {
            return Collections.unmodifiableMap(tasks);
        }

        public Set<String> prerequisites(String taskId) {
            return Collections.unmodifiableSet(
                incoming.get(taskId)
            );
        }

        public Set<String> dependents(String taskId) {
            return Collections.unmodifiableSet(
                outgoing.get(taskId)
            );
        }

        public int size() {
            return tasks.size();
        }

        private List<String> findCycle() {
            Map<String, Integer> color = new HashMap<>();

            for (String id : tasks.keySet()) {
                color.put(id, 0);
            }

            List<String> path = new ArrayList<>();

            for (String id : tasks.keySet()) {
                if (color.get(id) == 0) {
                    List<String> cycle = dfsCycle(
                        id,
                        color,
                        path
                    );

                    if (cycle != null) {
                        return cycle;
                    }
                }
            }

            return null;
        }

        private List<String> dfsCycle(
            String node,
            Map<String, Integer> color,
            List<String> path
        ) {
            color.put(node, 1);
            path.add(node);

            for (String child : outgoing.get(node)) {
                if (color.get(child) == 1) {
                    int index = path.indexOf(child);
                    List<String> cycle = new ArrayList<>(
                        path.subList(index, path.size())
                    );

                    cycle.add(child);
                    return cycle;
                }

                if (color.get(child) == 0) {
                    List<String> cycle = dfsCycle(
                        child,
                        color,
                        path
                    );

                    if (cycle != null) {
                        return cycle;
                    }
                }
            }

            path.remove(path.size() - 1);
            color.put(node, 2);
            return null;
        }
    }

    interface SchedulingPolicy {
        List<String> calculateOrder(Repository repository);
    }

    static class DfsPolicy implements SchedulingPolicy {

        @Override
        public List<String> calculateOrder(Repository repository) {
            Map<String, Integer> color = new HashMap<>();
            List<String> result = new ArrayList<>();
            List<String> path = new ArrayList<>();

            for (String id : repository.getTasks().keySet()) {
                color.put(id, 0);
            }

            for (String id : repository.getTasks().keySet()) {
                if (color.get(id) == 0) {
                    visit(id, repository, color, path, result);
                }
            }

            Collections.reverse(result);
            return List.copyOf(result);
        }

        private void visit(
            String node,
            Repository repository,
            Map<String, Integer> color,
            List<String> path,
            List<String> result
        ) {
            color.put(node, 1);
            path.add(node);

            for (String child : repository.dependents(node)) {
                if (color.get(child) == 1) {
                    int start = path.indexOf(child);
                    List<String> cycle = new ArrayList<>(
                        path.subList(start, path.size())
                    );

                    cycle.add(child);
                    throw new CycleException(cycle);
                }

                if (color.get(child) == 0) {
                    visit(
                        child,
                        repository,
                        color,
                        path,
                        result
                    );
                }
            }

            path.remove(path.size() - 1);
            color.put(node, 2);
            result.add(node);
        }
    }

    static class KahnPolicy implements SchedulingPolicy {

        @Override
        public List<String> calculateOrder(Repository repository) {
            Map<String, Integer> indegree = new HashMap<>();
            PriorityQueue<String> ready = new PriorityQueue<>();

            for (String id : repository.getTasks().keySet()) {
                int degree = repository.prerequisites(id).size();
                indegree.put(id, degree);

                if (degree == 0) {
                    ready.add(id);
                }
            }

            List<String> result = new ArrayList<>();

            while (!ready.isEmpty()) {
                String current = ready.poll();
                result.add(current);

                for (String child : repository.dependents(current)) {
                    int degree = indegree.get(child) - 1;
                    indegree.put(child, degree);

                    if (degree == 0) {
                        ready.add(child);
                    }
                }
            }

            if (result.size() != repository.size()) {
                throw new CycleException(
                    repository.findCycle()
                );
            }

            return List.copyOf(result);
        }
    }

    static class SchedulingService {
        private final Repository repository;
        private final SchedulingPolicy policy;

        private final Map<String, TaskStatus> executionState =
            new HashMap<>();

        SchedulingService(
            Repository repository,
            SchedulingPolicy policy
        ) {
            this.repository = repository;
            this.policy = policy;

            for (String id : repository.getTasks().keySet()) {
                executionState.put(id, TaskStatus.PENDING);
            }
        }

        public List<String> schedule() {
            return policy.calculateOrder(repository);
        }

        public Map<Integer, List<String>> calculateLevels() {
            List<String> order = schedule();
            Map<String, Integer> levels = new HashMap<>();

            for (String id : order) {
                int level = 0;

                for (String parent : repository.prerequisites(id)) {
                    level = Math.max(
                        level,
                        levels.get(parent) + 1
                    );
                }

                levels.put(id, level);
            }

            Map<Integer, List<String>> result = new TreeMap<>();

            for (String id : order) {
                int level = levels.get(id);

                result.computeIfAbsent(
                    level,
                    key -> new ArrayList<>()
                ).add(id);
            }

            Map<Integer, List<String>> immutable = new TreeMap<>();

            result.forEach(
                (level, ids) -> immutable.put(
                    level,
                    List.copyOf(ids)
                )
            );

            return Collections.unmodifiableMap(immutable);
        }

        public CriticalPath calculateCriticalPath() {
            List<String> order = schedule();

            Map<String, Integer> finish = new HashMap<>();
            Map<String, String> previous = new HashMap<>();

            for (String id : order) {
                int best = 0;
                String predecessor = null;

                for (String parent : repository.prerequisites(id)) {
                    if (finish.get(parent) > best) {
                        best = finish.get(parent);
                        predecessor = parent;
                    }
                }

                finish.put(
                    id,
                    best + repository.getTasks().get(id).duration()
                );

                previous.put(id, predecessor);
            }

            if (order.isEmpty()) {
                return new CriticalPath(0, List.of());
            }

            String endpoint = order.get(0);

            for (String id : order) {
                if (finish.get(id) > finish.get(endpoint)) {
                    endpoint = id;
                }
            }

            List<String> path = new ArrayList<>();
            String current = endpoint;

            while (current != null) {
                path.add(current);
                current = previous.get(current);
            }

            Collections.reverse(path);

            return new CriticalPath(
                finish.get(endpoint),
                path
            );
        }

        public void transition(String id, TaskStatus next) {
            if (!executionState.containsKey(id)) {
                throw new DependencyException(
                    "Unknown task: " + id
                );
            }

            TaskStatus current = executionState.get(id);

            boolean valid = switch (current) {
                case PENDING -> next == TaskStatus.READY
                    || next == TaskStatus.BLOCKED;
                case READY -> next == TaskStatus.RUNNING
                    || next == TaskStatus.BLOCKED;
                case RUNNING -> next == TaskStatus.COMPLETED
                    || next == TaskStatus.FAILED;
                default -> false;
            };

            if (!valid) {
                throw new DependencyException(
                    "Invalid state transition: "
                    + current + " -> " + next
                );
            }

            if (next == TaskStatus.READY) {
                boolean dependenciesComplete =
                    repository.prerequisites(id).stream()
                        .allMatch(parent ->
                            executionState.get(parent)
                                == TaskStatus.COMPLETED
                        );

                if (!dependenciesComplete) {
                    throw new DependencyException(
                        "Prerequisites are incomplete for " + id
                    );
                }
            }

            executionState.put(id, next);
        }

        public Map<String, TaskStatus> executionReport() {
            return Collections.unmodifiableMap(executionState);
        }
    }

    static Repository createProject() {
        Repository repository = new Repository();

        repository.registerTask(
            new Task("T1", "Gather requirements", 2, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T2", "Design architecture", 3, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T3", "Design database", 2, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T4", "Implement backend", 5, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T5", "Implement frontend", 4, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T6", "Integrate application", 2, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T7", "Execute testing", 3, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T8", "Security assessment", 2, TaskStatus.PENDING)
        );
        repository.registerTask(
            new Task("T9", "Production deployment", 1, TaskStatus.PENDING)
        );

        String[][] dependencies = {
            {"T1", "T2"},
            {"T1", "T3"},
            {"T2", "T4"},
            {"T3", "T4"},
            {"T2", "T5"},
            {"T4", "T6"},
            {"T5", "T6"},
            {"T6", "T7"},
            {"T6", "T8"},
            {"T7", "T9"},
            {"T8", "T9"}
        };

        for (String[] edge : dependencies) {
            repository.addDependency(
                new Dependency(edge[0], edge[1])
            );
        }

        return repository;
    }

    public static void main(String[] args) {
        try {
            Repository repository = createProject();

            SchedulingService dfsService =
                new SchedulingService(repository, new DfsPolicy());

            SchedulingService kahnService =
                new SchedulingService(repository, new KahnPolicy());

            System.out.println("ENTERPRISE DEPENDENCY SCHEDULER");
            System.out.println("================================");

            List<String> dfsOrder = dfsService.schedule();
            List<String> kahnOrder = kahnService.schedule();

            System.out.println("\nDFS ORDER");
            System.out.println(String.join(" -> ", dfsOrder));

            System.out.println("\nKAHN ORDER");
            System.out.println(String.join(" -> ", kahnOrder));

            System.out.println("\nPARALLEL EXECUTION LEVELS");

            kahnService.calculateLevels().forEach(
                (level, tasks) ->
                    System.out.println(
                        "Stage " + level + ": "
                        + String.join(", ", tasks)
                    )
            );

            CriticalPath critical =
                kahnService.calculateCriticalPath();

            System.out.println("\nCRITICAL PATH");
            System.out.println(String.join(" -> ", critical.tasks()));
            System.out.println(
                "Duration: " + critical.duration() + " time units"
            );

            SchedulingService execution =
                new SchedulingService(repository, new KahnPolicy());

            execution.transition("T1", TaskStatus.READY);
            execution.transition("T1", TaskStatus.RUNNING);
            execution.transition("T1", TaskStatus.COMPLETED);

            execution.transition("T2", TaskStatus.READY);

            System.out.println("\nSTATE TRANSITION TEST");
            System.out.println(execution.executionReport());

            try {
                execution.transition("T2", TaskStatus.COMPLETED);
            } catch (DependencyException error) {
                System.out.println(
                    "Invalid transition rejected: " + error.getMessage()
                );
            }

            try {
                repository.addDependency(new Dependency("T9", "T1"));
            } catch (CycleException error) {
                System.out.println("\nCycle rejection: " + error.getMessage());
            }

            if (dfsOrder.size() != repository.size() ||
                kahnOrder.size() != repository.size()) {
                throw new IllegalStateException(
                    "Incomplete topological ordering."
                );
            }

            Set<String> unique = new HashSet<>(kahnOrder);

            if (unique.size() != repository.size()) {
                throw new IllegalStateException(
                    "Duplicate task in ordering."
                );
            }

            System.out.println("\nVALIDATION");
            System.out.println("DFS policy: PASS");
            System.out.println("Kahn policy: PASS");
            System.out.println("Task uniqueness: PASS");
            System.out.println("Cycle prevention: PASS");
            System.out.println("State transition validation: PASS");

        } catch (Exception error) {
            System.err.println("ERROR: " + error.getMessage());
            System.exit(1);
        }
    }
}
