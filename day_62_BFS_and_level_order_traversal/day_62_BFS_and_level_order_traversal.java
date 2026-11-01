import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Enterprise-oriented hierarchical analytics service.
 *
 * The hierarchy represents an organizational structure.
 * BFS processes departments in increasing hierarchical depth.
 */
public class BFSLevelOrderEnterprise {

    enum TraversalMode {
        STANDARD,
        ZIGZAG,
        BOTTOM_UP
    }

    enum ProcessingStatus {
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED
    }

    record Department(
        String departmentId,
        String name,
        int workload
    ) {
        Department {
            if (departmentId == null || departmentId.isBlank()) {
                throw new IllegalArgumentException(
                    "Department ID is required."
                );
            }

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Department name is required."
                );
            }

            if (workload < 0) {
                throw new IllegalArgumentException(
                    "Workload cannot be negative."
                );
            }
        }
    }

    record LevelMetrics(
        int depth,
        int departmentCount,
        long totalWorkload,
        double averageWorkload,
        int maximumWorkload,
        int minimumWorkload
    ) {}

    record ProcessingResult(
        List<List<Department>> levels,
        List<LevelMetrics> metrics,
        ProcessingStatus status
    ) {
        ProcessingResult {
            levels = levels.stream()
                .map(List::copyOf)
                .toList();

            metrics = List.copyOf(metrics);
            Objects.requireNonNull(status);
        }
    }

    static final class HierarchyNode {
        private final Department department;
        private final List<HierarchyNode> children = new ArrayList<>();

        HierarchyNode(Department department) {
            this.department = Objects.requireNonNull(department);
        }

        Department department() {
            return department;
        }

        List<HierarchyNode> children() {
            return Collections.unmodifiableList(children);
        }

        void addChild(HierarchyNode child) {
            Objects.requireNonNull(child);

            if (child == this) {
                throw new IllegalArgumentException(
                    "A node cannot be its own child."
                );
            }

            children.add(child);
        }
    }

    /**
     * Repository for constructing and validating an organizational tree.
     */
    static final class HierarchyRepository {
        private final HierarchyNode root;
        private final Set<String> departmentIds = new HashSet<>();

        HierarchyRepository(HierarchyNode root) {
            this.root = Objects.requireNonNull(root);
            validateUniqueIds(root);
        }

        private void validateUniqueIds(HierarchyNode node) {
            Set<HierarchyNode> visited =
                Collections.newSetFromMap(
                    new java.util.IdentityHashMap<>()
                );

            Deque<HierarchyNode> queue = new ArrayDeque<>();
            queue.add(node);

            while (!queue.isEmpty()) {
                HierarchyNode current = queue.removeFirst();

                if (!visited.add(current)) {
                    throw new IllegalArgumentException(
                        "Cycle or shared node detected."
                    );
                }

                String id = current.department().departmentId();

                if (!departmentIds.add(id)) {
                    throw new IllegalArgumentException(
                        "Duplicate department ID: " + id
                    );
                }

                queue.addAll(current.children());
            }
        }

        HierarchyNode root() {
            return root;
        }

        int size() {
            return departmentIds.size();
        }
    }

    /**
     * BFS service with explicit level boundaries.
     */
    static final class HierarchyAnalyticsService {

        List<List<Department>> levelOrder(HierarchyNode root) {
            if (root == null) {
                return List.of();
            }

            List<List<Department>> result = new ArrayList<>();
            Deque<HierarchyNode> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                int levelSize = queue.size();
                List<Department> level = new ArrayList<>(levelSize);

                for (int i = 0; i < levelSize; i++) {
                    HierarchyNode current = queue.removeFirst();
                    level.add(current.department());

                    for (HierarchyNode child : current.children()) {
                        queue.addLast(child);
                    }
                }

                result.add(List.copyOf(level));
            }

            return List.copyOf(result);
        }

        List<LevelMetrics> calculateMetrics(
            List<List<Department>> levels
        ) {
            List<LevelMetrics> metrics = new ArrayList<>();

            for (int depth = 0; depth < levels.size(); depth++) {
                List<Department> level = levels.get(depth);

                long total = level.stream()
                    .mapToLong(Department::workload)
                    .sum();

                int maximum = level.stream()
                    .mapToInt(Department::workload)
                    .max()
                    .orElse(0);

                int minimum = level.stream()
                    .mapToInt(Department::workload)
                    .min()
                    .orElse(0);

                metrics.add(new LevelMetrics(
                    depth,
                    level.size(),
                    total,
                    (double) total / level.size(),
                    maximum,
                    minimum
                ));
            }

            return List.copyOf(metrics);
        }

        List<List<Department>> zigzag(
            List<List<Department>> levels
        ) {
            List<List<Department>> result = new ArrayList<>();

            for (int i = 0; i < levels.size(); i++) {
                List<Department> level =
                    new ArrayList<>(levels.get(i));

                if (i % 2 == 1) {
                    Collections.reverse(level);
                }

                result.add(List.copyOf(level));
            }

            return List.copyOf(result);
        }

        List<List<Department>> bottomUp(
            List<List<Department>> levels
        ) {
            List<List<Department>> result =
                new ArrayList<>(levels);

            Collections.reverse(result);

            return List.copyOf(result);
        }

        List<Department> find(
            HierarchyNode root,
            Predicate<Department> condition
        ) {
            Objects.requireNonNull(condition);

            if (root == null) {
                return List.of();
            }

            List<Department> result = new ArrayList<>();
            Deque<HierarchyNode> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                HierarchyNode current = queue.removeFirst();

                if (condition.test(current.department())) {
                    result.add(current.department());
                }

                queue.addAll(current.children());
            }

            return List.copyOf(result);
        }

        ProcessingResult process(HierarchyNode root) {
            try {
                List<List<Department>> levels = levelOrder(root);
                List<LevelMetrics> metrics = calculateMetrics(levels);

                return new ProcessingResult(
                    levels,
                    metrics,
                    ProcessingStatus.COMPLETED
                );
            } catch (RuntimeException exception) {
                return new ProcessingResult(
                    List.of(),
                    List.of(),
                    ProcessingStatus.FAILED
                );
            }
        }
    }

    static final class HierarchyWorkflow {
        private ProcessingStatus status = ProcessingStatus.PENDING;

        ProcessingResult execute(
            HierarchyAnalyticsService service,
            HierarchyRepository repository
        ) {
            if (status != ProcessingStatus.PENDING) {
                throw new IllegalStateException(
                    "Workflow has already been executed."
                );
            }

            status = ProcessingStatus.PROCESSING;

            try {
                ProcessingResult result =
                    service.process(repository.root());

                if (result.status() == ProcessingStatus.FAILED) {
                    status = ProcessingStatus.FAILED;
                } else {
                    status = ProcessingStatus.COMPLETED;
                }

                return result;

            } catch (RuntimeException exception) {
                status = ProcessingStatus.FAILED;
                throw exception;
            }
        }

        ProcessingStatus status() {
            return status;
        }
    }

    private static HierarchyRepository createOrganization() {
        HierarchyNode ceo = new HierarchyNode(
            new Department("D001", "Executive Office", 100)
        );

        HierarchyNode technology = new HierarchyNode(
            new Department("D002", "Technology", 250)
        );

        HierarchyNode operations = new HierarchyNode(
            new Department("D003", "Operations", 180)
        );

        HierarchyNode security = new HierarchyNode(
            new Department("D004", "Security", 220)
        );

        HierarchyNode engineering = new HierarchyNode(
            new Department("D005", "Engineering", 300)
        );

        HierarchyNode analytics = new HierarchyNode(
            new Department("D006", "Analytics", 150)
        );

        HierarchyNode infrastructure = new HierarchyNode(
            new Department("D007", "Infrastructure", 200)
        );

        HierarchyNode support = new HierarchyNode(
            new Department("D008", "Support", 90)
        );

        ceo.addChild(technology);
        ceo.addChild(operations);
        ceo.addChild(security);

        technology.addChild(engineering);
        technology.addChild(analytics);

        operations.addChild(infrastructure);
        operations.addChild(support);

        return new HierarchyRepository(ceo);
    }

    private static void display(
        String heading,
        List<List<Department>> levels
    ) {
        System.out.println("\n" + heading);

        for (int depth = 0; depth < levels.size(); depth++) {
            System.out.println(
                "Level " + depth + ": " +
                levels.get(depth).stream()
                    .map(Department::name)
                    .collect(Collectors.joining(" | "))
            );
        }
    }

    private static void runTests(
        HierarchyAnalyticsService service,
        HierarchyRepository repository
    ) {
        List<List<Department>> levels =
            service.levelOrder(repository.root());

        if (levels.size() != 3) {
            throw new AssertionError("Incorrect hierarchy depth.");
        }

        if (levels.get(0).size() != 1 ||
            levels.get(1).size() != 3 ||
            levels.get(2).size() != 4) {
            throw new AssertionError("Incorrect level separation.");
        }

        List<List<Department>> zigzag = service.zigzag(levels);

        if (!zigzag.get(1).get(0).name().equals("Security")) {
            throw new AssertionError("Zigzag traversal failed.");
        }

        if (repository.size() != 8) {
            throw new AssertionError("Node count failed.");
        }

        List<Department> highWorkload = service.find(
            repository.root(),
            department -> department.workload() >= 200
        );

        if (highWorkload.size() != 4) {
            throw new AssertionError("Department filtering failed.");
        }

        HierarchyWorkflow workflow = new HierarchyWorkflow();
        ProcessingResult result = workflow.execute(service, repository);

        if (result.status() != ProcessingStatus.COMPLETED) {
            throw new AssertionError("Workflow failed.");
        }

        try {
            workflow.execute(service, repository);
            throw new AssertionError("Repeated execution was accepted.");
        } catch (IllegalStateException expected) {
            // The workflow must not execute twice.
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            HierarchyRepository repository = createOrganization();
            HierarchyAnalyticsService service =
                new HierarchyAnalyticsService();

            HierarchyWorkflow workflow = new HierarchyWorkflow();

            ProcessingResult result = workflow.execute(
                service,
                repository
            );

            System.out.println(
                "ENTERPRISE HIERARCHY ANALYTICS"
            );

            System.out.println(
                "Departments: " + repository.size()
            );

            System.out.println(
                "Workflow status: " + workflow.status()
            );

            display("Standard BFS", result.levels());

            display(
                "Zigzag traversal",
                service.zigzag(result.levels())
            );

            display(
                "Bottom-up traversal",
                service.bottomUp(result.levels())
            );

            System.out.println("\nLEVEL METRICS");

            for (LevelMetrics metric : result.metrics()) {
                System.out.printf(
                    "Depth=%d | Count=%d | Total=%d | " +
                    "Average=%.2f | Min=%d | Max=%d%n",
                    metric.depth(),
                    metric.departmentCount(),
                    metric.totalWorkload(),
                    metric.averageWorkload(),
                    metric.minimumWorkload(),
                    metric.maximumWorkload()
                );
            }

            System.out.println("\nHIGH-WORKLOAD DEPARTMENTS");

            service.find(
                repository.root(),
                department -> department.workload() >= 200
            ).forEach(department ->
                System.out.println(
                    department.name() +
                    " : " + department.workload()
                )
            );

            runTests(service, repository);

        } catch (Exception exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
