import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiFunction;
import java.util.stream.Collectors;

public class LowestCommonAncestorApp {

    enum QueryStrategy {
        RECURSIVE,
        PARENT_BASED,
        ITERATIVE,
        BINARY_LIFTING
    }

    enum NodeStatus {
        ACTIVE,
        INACTIVE
    }

    record EmployeeRecord(
        int employeeId,
        String department,
        NodeStatus status
    ) {
        EmployeeRecord {
            if (employeeId <= 0) {
                throw new IllegalArgumentException(
                    "Employee ID must be positive."
                );
            }

            if (department == null || department.isBlank()) {
                throw new IllegalArgumentException(
                    "Department is required."
                );
            }

            Objects.requireNonNull(status, "Status is required.");
        }
    }

    static final class TreeNode {
        private final EmployeeRecord employee;
        private TreeNode left;
        private TreeNode right;
        private TreeNode parent;

        TreeNode(EmployeeRecord employee) {
            this.employee = Objects.requireNonNull(employee);
        }

        EmployeeRecord employee() {
            return employee;
        }

        TreeNode left() {
            return left;
        }

        TreeNode right() {
            return right;
        }

        TreeNode parent() {
            return parent;
        }
    }

    static final class BinaryTree {
        private final Map<Integer, TreeNode> nodes = new HashMap<>();
        private TreeNode root;

        TreeNode add(EmployeeRecord employee) {
            Objects.requireNonNull(employee);

            if (nodes.containsKey(employee.employeeId())) {
                throw new IllegalArgumentException(
                    "Duplicate employee ID."
                );
            }

            TreeNode node = new TreeNode(employee);
            nodes.put(employee.employeeId(), node);

            if (root == null) {
                root = node;
            }

            return node;
        }

        TreeNode get(int employeeId) {
            return nodes.get(employeeId);
        }

        TreeNode root() {
            return root;
        }

        int size() {
            return nodes.size();
        }

        void attach(int parentId, int childId, boolean leftSide) {
            TreeNode parent = get(parentId);
            TreeNode child = get(childId);

            if (parent == null || child == null) {
                throw new IllegalArgumentException(
                    "Employee does not exist."
                );
            }

            if (parent == child || child.parent != null) {
                throw new IllegalStateException(
                    "Invalid parent-child relationship."
                );
            }

            TreeNode current = parent;

            while (current != null) {
                if (current == child) {
                    throw new IllegalStateException(
                        "Attachment would create a cycle."
                    );
                }

                current = current.parent;
            }

            if (leftSide) {
                if (parent.left != null) {
                    throw new IllegalStateException(
                        "Left position already occupied."
                    );
                }

                parent.left = child;
            } else {
                if (parent.right != null) {
                    throw new IllegalStateException(
                        "Right position already occupied."
                    );
                }

                parent.right = child;
            }

            child.parent = parent;
        }

        void validate() {
            if (root == null) {
                if (!nodes.isEmpty()) {
                    throw new IllegalStateException(
                        "Nodes exist without a root."
                    );
                }
                return;
            }

            Set<TreeNode> visited = new HashSet<>();
            Deque<TreeNode> stack = new ArrayDeque<>();
            Map<TreeNode, TreeNode> expectedParents = new HashMap<>();

            stack.push(root);
            expectedParents.put(root, null);

            while (!stack.isEmpty()) {
                TreeNode node = stack.pop();

                if (!visited.add(node)) {
                    throw new IllegalStateException(
                        "Cycle or shared child detected."
                    );
                }

                if (node.parent != expectedParents.get(node)) {
                    throw new IllegalStateException(
                        "Parent pointer inconsistency."
                    );
                }

                if (node.left != null) {
                    expectedParents.put(node.left, node);
                    stack.push(node.left);
                }

                if (node.right != null) {
                    expectedParents.put(node.right, node);
                    stack.push(node.right);
                }
            }

            if (visited.size() != nodes.size()) {
                throw new IllegalStateException(
                    "Unreachable employees detected."
                );
            }
        }

        List<TreeNode> breadthFirst() {
            if (root == null) return List.of();

            List<TreeNode> result = new ArrayList<>();
            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                TreeNode current = queue.removeFirst();
                result.add(current);

                if (current.left != null) queue.add(current.left);
                if (current.right != null) queue.add(current.right);
            }

            return Collections.unmodifiableList(result);
        }
    }

    static final class LCAService {
        private final BinaryTree tree;

        LCAService(BinaryTree tree) {
            this.tree = Objects.requireNonNull(tree);
            tree.validate();
        }

        private void validateTargets(TreeNode first, TreeNode second) {
            if (first == null || second == null) {
                throw new IllegalArgumentException(
                    "Both target employees are required."
                );
            }

            if (!contains(first) || !contains(second)) {
                throw new IllegalArgumentException(
                    "Target employee is outside this hierarchy."
                );
            }
        }

        private boolean contains(TreeNode target) {
            return tree.breadthFirst().contains(target);
        }

        Optional<TreeNode> recursive(
            TreeNode first,
            TreeNode second
        ) {
            validateTargets(first, second);

            return Optional.ofNullable(
                search(tree.root(), first, second)
            );
        }

        private TreeNode search(
            TreeNode node,
            TreeNode first,
            TreeNode second
        ) {
            if (node == null || node == first || node == second) {
                return node;
            }

            TreeNode left = search(node.left, first, second);
            TreeNode right = search(node.right, first, second);

            if (left != null && right != null) {
                return node;
            }

            return left != null ? left : right;
        }

        Optional<TreeNode> parentBased(
            TreeNode first,
            TreeNode second
        ) {
            validateTargets(first, second);

            Set<TreeNode> ancestors = new HashSet<>();
            TreeNode current = first;

            while (current != null) {
                if (!ancestors.add(current)) {
                    throw new IllegalStateException(
                        "Parent cycle detected."
                    );
                }

                current = current.parent;
            }

            current = second;

            while (current != null) {
                if (ancestors.contains(current)) {
                    return Optional.of(current);
                }

                current = current.parent;
            }

            return Optional.empty();
        }

        Optional<TreeNode> iterative(
            TreeNode first,
            TreeNode second
        ) {
            validateTargets(first, second);

            Map<TreeNode, TreeNode> parents = new HashMap<>();
            Deque<TreeNode> stack = new ArrayDeque<>();

            parents.put(tree.root(), null);
            stack.push(tree.root());

            while (!stack.isEmpty()) {
                TreeNode current = stack.pop();

                if (current.left != null) {
                    parents.put(current.left, current);
                    stack.push(current.left);
                }

                if (current.right != null) {
                    parents.put(current.right, current);
                    stack.push(current.right);
                }
            }

            Set<TreeNode> ancestors = new HashSet<>();
            TreeNode current = first;

            while (current != null) {
                ancestors.add(current);
                current = parents.get(current);
            }

            current = second;

            while (current != null) {
                if (ancestors.contains(current)) {
                    return Optional.of(current);
                }

                current = parents.get(current);
            }

            return Optional.empty();
        }
    }

    /**
     * Precomputed binary lifting index for repeated queries.
     * The index is immutable after construction.
     */
    static final class BinaryLiftingIndex {
        private final Map<TreeNode, Integer> positions = new HashMap<>();
        private final List<TreeNode> nodes;
        private final int[][] ancestors;
        private final int[] depth;
        private final int levels;

        BinaryLiftingIndex(BinaryTree tree) {
            tree.validate();

            nodes = tree.breadthFirst();

            if (nodes.isEmpty()) {
                throw new IllegalArgumentException(
                    "Cannot index an empty hierarchy."
                );
            }

            int n = nodes.size();
            levels = 32 - Integer.numberOfLeadingZeros(n);

            ancestors = new int[n][levels];
            depth = new int[n];

            for (int[] row : ancestors) {
                java.util.Arrays.fill(row, -1);
            }

            for (int i = 0; i < n; i++) {
                positions.put(nodes.get(i), i);
            }

            for (int i = 0; i < n; i++) {
                TreeNode node = nodes.get(i);

                if (node.parent != null) {
                    int parentPosition = positions.get(node.parent);
                    ancestors[i][0] = parentPosition;
                    depth[i] = depth[parentPosition] + 1;
                }
            }

            for (int k = 1; k < levels; k++) {
                for (int v = 0; v < n; v++) {
                    int middle = ancestors[v][k - 1];

                    if (middle != -1) {
                        ancestors[v][k] = ancestors[middle][k - 1];
                    }
                }
            }
        }

        Optional<TreeNode> query(TreeNode first, TreeNode second) {
            Integer firstPosition = positions.get(first);
            Integer secondPosition = positions.get(second);

            if (firstPosition == null || secondPosition == null) {
                return Optional.empty();
            }

            int a = firstPosition;
            int b = secondPosition;

            if (depth[a] < depth[b]) {
                int temp = a;
                a = b;
                b = temp;
            }

            int difference = depth[a] - depth[b];

            for (int k = 0; k < levels; k++) {
                if ((difference & (1 << k)) != 0) {
                    a = ancestors[a][k];
                }
            }

            if (a == b) {
                return Optional.of(nodes.get(a));
            }

            for (int k = levels - 1; k >= 0; k--) {
                if (ancestors[a][k] != ancestors[b][k]) {
                    a = ancestors[a][k];
                    b = ancestors[b][k];
                }
            }

            return Optional.of(nodes.get(ancestors[a][0]));
        }
    }

    record QueryResult(
        int firstEmployee,
        int secondEmployee,
        int ancestorEmployee,
        String ancestorDepartment,
        QueryStrategy strategy
    ) {}

    static final class HierarchyQueryService {
        private final BinaryTree tree;
        private final LCAService service;
        private final BinaryLiftingIndex index;

        HierarchyQueryService(BinaryTree tree) {
            this.tree = Objects.requireNonNull(tree);
            this.service = new LCAService(tree);
            this.index = new BinaryLiftingIndex(tree);
        }

        QueryResult execute(
            int firstId,
            int secondId,
            QueryStrategy strategy
        ) {
            Objects.requireNonNull(strategy);

            TreeNode first = tree.get(firstId);
            TreeNode second = tree.get(secondId);

            if (first == null || second == null) {
                throw new IllegalArgumentException(
                    "Employee ID not found."
                );
            }

            Optional<TreeNode> result = switch (strategy) {
                case RECURSIVE -> service.recursive(first, second);
                case PARENT_BASED -> service.parentBased(first, second);
                case ITERATIVE -> service.iterative(first, second);
                case BINARY_LIFTING -> index.query(first, second);
            };

            TreeNode ancestor = result.orElseThrow(
                () -> new IllegalStateException(
                    "No common ancestor exists."
                )
            );

            return new QueryResult(
                firstId,
                secondId,
                ancestor.employee.employeeId(),
                ancestor.employee.department(),
                strategy
            );
        }
    }

    private static BinaryTree buildOrganization() {
        BinaryTree tree = new BinaryTree();

        tree.add(new EmployeeRecord(1, "Executive Office", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(2, "Technology", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(3, "Operations", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(4, "Platform Engineering", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(5, "Security Engineering", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(6, "Operations Research", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(7, "Infrastructure", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(8, "Application Security", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(9, "Cloud Security", NodeStatus.ACTIVE));
        tree.add(new EmployeeRecord(10, "Network Engineering", NodeStatus.INACTIVE));

        tree.attach(1, 2, true);
        tree.attach(1, 3, false);
        tree.attach(2, 4, true);
        tree.attach(2, 5, false);
        tree.attach(3, 6, true);
        tree.attach(3, 7, false);
        tree.attach(5, 8, true);
        tree.attach(5, 9, false);
        tree.attach(7, 10, false);

        tree.validate();

        return tree;
    }

    private static void runTests(HierarchyQueryService service) {
        Map<List<Integer>, Integer> expected = Map.of(
            List.of(4, 5), 2,
            List.of(4, 6), 1,
            List.of(8, 9), 5,
            List.of(8, 10), 1,
            List.of(2, 8), 2,
            List.of(7, 10), 7
        );

        for (var entry : expected.entrySet()) {
            int first = entry.getKey().get(0);
            int second = entry.getKey().get(1);

            for (QueryStrategy strategy : QueryStrategy.values()) {
                QueryResult result = service.execute(
                    first, second, strategy
                );

                if (result.ancestorEmployee() != entry.getValue()) {
                    throw new AssertionError("LCA test failed.");
                }
            }
        }

        System.out.println("All Java 17 LCA tests passed.");
    }

    public static void main(String[] args) {
        BinaryTree tree = buildOrganization();
        HierarchyQueryService service = new HierarchyQueryService(tree);

        runTests(service);

        System.out.println("\nEnterprise hierarchy queries");
        System.out.println("----------------------------");

        List<List<Integer>> requests = List.of(
            List.of(4, 5),
            List.of(4, 6),
            List.of(8, 9),
            List.of(8, 10),
            List.of(7, 10)
        );

        for (List<Integer> request : requests) {
            QueryResult result = service.execute(
                request.get(0),
                request.get(1),
                QueryStrategy.BINARY_LIFTING
            );

            System.out.printf(
                "LCA(%d, %d) = %d (%s)%n",
                result.firstEmployee(),
                result.secondEmployee(),
                result.ancestorEmployee(),
                result.ancestorDepartment()
            );
        }

        System.out.println("\nMultiple strategy verification:");

        for (QueryStrategy strategy : QueryStrategy.values()) {
            QueryResult result = service.execute(8, 10, strategy);

            System.out.printf(
                "%s -> Employee %d%n",
                strategy,
                result.ancestorEmployee()
            );
        }

        System.out.println("\nHierarchy size: " + tree.size());
        System.out.println(
            "Active employees: " +
            tree.breadthFirst().stream()
                .filter(node ->
                    node.employee().status() == NodeStatus.ACTIVE
                )
                .count()
        );

        try {
            service.execute(4, 999, QueryStrategy.RECURSIVE);
        } catch (IllegalArgumentException exception) {
            System.out.println(
                "Expected validation failure: " + exception.getMessage()
            );
        }
    }
}
