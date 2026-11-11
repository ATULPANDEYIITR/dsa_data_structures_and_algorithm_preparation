import java.util.*;
import java.util.function.Consumer;
import java.util.stream.Collectors;

/**
 * Binary Search Tree Enterprise Assessment
 *
 * Java 17
 *
 * Includes:
 * - Explicit domain types
 * - BST operations
 * - Validation and structural integrity
 * - Search, insertion, deletion
 * - LCA, minimum, maximum
 * - Successor and predecessor
 * - Traversal and range queries
 * - Assessment policies
 * - Event listeners
 * - Custom exceptions
 * - Deterministic and randomized tests
 *
 * Duplicate keys are rejected.
 */
public class BSTAssessment {

    enum ReviewStatus {
        NOT_EVALUATED,
        PASSED,
        FAILED
    }

    enum Operation {
        SEARCH,
        INSERT,
        DELETE,
        VALIDATE,
        LCA,
        MINIMUM,
        MAXIMUM,
        SUCCESSOR,
        PREDECESSOR
    }

    record AssessmentPolicy(
        boolean requireValidStructure,
        boolean requireSortedTraversal,
        boolean requireCorrectSize
    ) {}

    record AssessmentReport(
        int nodeCount,
        int height,
        boolean balanced,
        boolean valid,
        List<Integer> inorder,
        ReviewStatus status,
        List<String> findings
    ) {
        public AssessmentReport {
            inorder = List.copyOf(inorder);
            findings = List.copyOf(findings);
        }
    }

    record OperationEvent(
        Operation operation,
        int key,
        boolean successful,
        long timestamp
    ) {}

    static class BSTException extends RuntimeException {
        BSTException(String message) {
            super(message);
        }
    }

    static class InvalidTreeException extends BSTException {
        InvalidTreeException(String message) {
            super(message);
        }
    }

    static final class Node {
        private int key;
        private Node left;
        private Node right;

        Node(int key) {
            this.key = key;
        }
    }

    interface AssessmentListener {
        void onOperation(OperationEvent event);
    }

    static final class BinarySearchTree {

        private Node root;
        private int size;

        private final List<AssessmentListener> listeners =
            new ArrayList<>();

        public int size() {
            return size;
        }

        public void addListener(AssessmentListener listener) {
            listeners.add(Objects.requireNonNull(listener));
        }

        private void notifyListeners(
            Operation operation,
            int key,
            boolean successful
        ) {
            OperationEvent event = new OperationEvent(
                operation,
                key,
                successful,
                System.currentTimeMillis()
            );

            for (AssessmentListener listener :
                    List.copyOf(listeners)) {
                listener.onOperation(event);
            }
        }

        public boolean insert(int key) {
            if (root == null) {
                root = new Node(key);
                size++;
                notifyListeners(Operation.INSERT, key, true);
                return true;
            }

            Node current = root;

            while (true) {
                if (key == current.key) {
                    notifyListeners(Operation.INSERT, key, false);
                    return false;
                }

                if (key < current.key) {
                    if (current.left == null) {
                        current.left = new Node(key);
                        size++;
                        notifyListeners(Operation.INSERT, key, true);
                        return true;
                    }

                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node(key);
                        size++;
                        notifyListeners(Operation.INSERT, key, true);
                        return true;
                    }

                    current = current.right;
                }
            }
        }

        public OptionalInt search(int key) {
            Node current = root;

            while (current != null) {
                if (key == current.key) {
                    notifyListeners(Operation.SEARCH, key, true);
                    return OptionalInt.of(current.key);
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            notifyListeners(Operation.SEARCH, key, false);
            return OptionalInt.empty();
        }

        public boolean contains(int key) {
            return search(key).isPresent();
        }

        public OptionalInt minimum() {
            Node current = root;

            if (current == null) {
                notifyListeners(
                    Operation.MINIMUM, 0, false
                );
                return OptionalInt.empty();
            }

            while (current.left != null) {
                current = current.left;
            }

            notifyListeners(
                Operation.MINIMUM, current.key, true
            );

            return OptionalInt.of(current.key);
        }

        public OptionalInt maximum() {
            Node current = root;

            if (current == null) {
                notifyListeners(
                    Operation.MAXIMUM, 0, false
                );
                return OptionalInt.empty();
            }

            while (current.right != null) {
                current = current.right;
            }

            notifyListeners(
                Operation.MAXIMUM, current.key, true
            );

            return OptionalInt.of(current.key);
        }

        public boolean delete(int key) {
            Node parent = null;
            Node current = root;

            while (current != null && current.key != key) {
                parent = current;

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            if (current == null) {
                notifyListeners(Operation.DELETE, key, false);
                return false;
            }

            // Replace a two-child node with its inorder successor.
            if (current.left != null && current.right != null) {
                Node successorParent = current;
                Node successor = current.right;

                while (successor.left != null) {
                    successorParent = successor;
                    successor = successor.left;
                }

                current.key = successor.key;

                parent = successorParent;
                current = successor;
            }

            Node child = current.left != null
                ? current.left
                : current.right;

            if (parent == null) {
                root = child;
            } else if (parent.left == current) {
                parent.left = child;
            } else {
                parent.right = child;
            }

            size--;
            notifyListeners(Operation.DELETE, key, true);

            return true;
        }

        private boolean validateNode(
            Node node,
            Long lower,
            Long upper,
            Set<Node> visited
        ) {
            if (node == null) return true;

            if (!visited.add(node)) return false;

            if (lower != null && node.key <= lower) {
                return false;
            }

            if (upper != null && node.key >= upper) {
                return false;
            }

            return validateNode(
                node.left, lower, (long) node.key, visited
            ) && validateNode(
                node.right, (long) node.key, upper, visited
            );
        }

        public boolean validate() {
            Set<Node> visited =
                Collections.newSetFromMap(
                    new IdentityHashMap<>()
                );

            boolean valid = validateNode(
                root, null, null, visited
            );

            valid = valid && visited.size() == size;

            notifyListeners(
                Operation.VALIDATE, 0, valid
            );

            return valid;
        }

        public OptionalInt lowestCommonAncestor(
            int first,
            int second
        ) {
            if (!contains(first) || !contains(second)) {
                notifyListeners(Operation.LCA, 0, false);
                return OptionalInt.empty();
            }

            Node current = root;

            while (current != null) {
                if (first < current.key && second < current.key) {
                    current = current.left;
                } else if (
                    first > current.key && second > current.key
                ) {
                    current = current.right;
                } else {
                    notifyListeners(
                        Operation.LCA, current.key, true
                    );

                    return OptionalInt.of(current.key);
                }
            }

            return OptionalInt.empty();
        }

        public OptionalInt successor(int key) {
            Node current = root;
            Integer candidate = null;

            while (current != null) {
                if (key < current.key) {
                    candidate = current.key;
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            boolean found = candidate != null;

            notifyListeners(
                Operation.SUCCESSOR,
                found ? candidate : key,
                found
            );

            return found
                ? OptionalInt.of(candidate)
                : OptionalInt.empty();
        }

        public OptionalInt predecessor(int key) {
            Node current = root;
            Integer candidate = null;

            while (current != null) {
                if (key > current.key) {
                    candidate = current.key;
                    current = current.right;
                } else {
                    current = current.left;
                }
            }

            boolean found = candidate != null;

            notifyListeners(
                Operation.PREDECESSOR,
                found ? candidate : key,
                found
            );

            return found
                ? OptionalInt.of(candidate)
                : OptionalInt.empty();
        }

        public List<Integer> inorder() {
            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            Node current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();
                result.add(current.key);
                current = current.right;
            }

            return List.copyOf(result);
        }

        public List<Integer> preorder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                result.add(node.key);

                if (node.right != null) stack.push(node.right);
                if (node.left != null) stack.push(node.left);
            }

            return List.copyOf(result);
        }

        public List<Integer> postorder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();
            Deque<Node> output = new ArrayDeque<>();

            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                output.push(node);

                if (node.left != null) stack.push(node.left);
                if (node.right != null) stack.push(node.right);
            }

            while (!output.isEmpty()) {
                result.add(output.pop().key);
            }

            return List.copyOf(result);
        }

        public List<Integer> levelOrder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Queue<Node> queue = new ArrayDeque<>();

            queue.offer(root);

            while (!queue.isEmpty()) {
                Node node = queue.poll();
                result.add(node.key);

                if (node.left != null) queue.offer(node.left);
                if (node.right != null) queue.offer(node.right);
            }

            return List.copyOf(result);
        }

        public List<Integer> rangeQuery(int low, int high) {
            if (low > high) {
                throw new IllegalArgumentException(
                    "Invalid range."
                );
            }

            return inorder().stream()
                .filter(value -> value >= low && value <= high)
                .collect(Collectors.toUnmodifiableList());
        }

        public int height() {
            if (root == null) return -1;

            Queue<Node> queue = new ArrayDeque<>();
            Queue<Integer> depths = new ArrayDeque<>();

            queue.offer(root);
            depths.offer(0);

            int maximum = 0;

            while (!queue.isEmpty()) {
                Node node = queue.poll();
                int depth = depths.poll();

                maximum = Math.max(maximum, depth);

                if (node.left != null) {
                    queue.offer(node.left);
                    depths.offer(depth + 1);
                }

                if (node.right != null) {
                    queue.offer(node.right);
                    depths.offer(depth + 1);
                }
            }

            return maximum;
        }

        public boolean isBalanced() {
            return balanceHeight(root) != -1;
        }

        private int balanceHeight(Node node) {
            if (node == null) return 0;

            int left = balanceHeight(node.left);
            if (left == -1) return -1;

            int right = balanceHeight(node.right);
            if (right == -1) return -1;

            if (Math.abs(left - right) > 1) return -1;

            return 1 + Math.max(left, right);
        }
    }

    static final class AssessmentService {

        private final AssessmentPolicy policy;

        AssessmentService(AssessmentPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public AssessmentReport assess(
            BinarySearchTree tree
        ) {
            Objects.requireNonNull(tree);

            List<String> findings = new ArrayList<>();

            boolean valid = tree.validate();

            if (policy.requireValidStructure() && !valid) {
                findings.add("BST ordering or structural integrity failed.");
            }

            List<Integer> inorder = tree.inorder();

            boolean sorted = true;

            for (int i = 1; i < inorder.size(); i++) {
                if (inorder.get(i - 1) >= inorder.get(i)) {
                    sorted = false;
                    break;
                }
            }

            if (policy.requireSortedTraversal() && !sorted) {
                findings.add("Inorder traversal is not strictly increasing.");
            }

            if (
                policy.requireCorrectSize() &&
                inorder.size() != tree.size()
            ) {
                findings.add("Node count does not match traversal count.");
            }

            boolean passed = findings.isEmpty();

            return new AssessmentReport(
                tree.size(),
                tree.height(),
                tree.isBalanced(),
                valid,
                inorder,
                passed
                    ? ReviewStatus.PASSED
                    : ReviewStatus.FAILED,
                findings
            );
        }
    }

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    static void runTests() {
        BinarySearchTree tree = new BinarySearchTree();

        List<OperationEvent> events = new ArrayList<>();

        tree.addListener(events::add);

        for (int key : List.of(
            50, 30, 70, 20, 40, 60, 80
        )) {
            require(tree.insert(key), "Insertion failed.");
        }

        require(!tree.insert(50), "Duplicate accepted.");
        require(tree.contains(40), "Search failed.");
        require(!tree.contains(999), "Unexpected search result.");

        require(tree.minimum().orElseThrow() == 20, "Minimum failed.");
        require(tree.maximum().orElseThrow() == 80, "Maximum failed.");

        require(
            tree.lowestCommonAncestor(20, 40).orElseThrow() == 30,
            "LCA failed."
        );

        require(
            tree.lowestCommonAncestor(20, 80).orElseThrow() == 50,
            "LCA across subtrees failed."
        );

        require(
            tree.lowestCommonAncestor(20, 999).isEmpty(),
            "Missing LCA should be empty."
        );

        require(tree.successor(40).orElseThrow() == 50,
            "Successor failed.");

        require(tree.predecessor(60).orElseThrow() == 50,
            "Predecessor failed.");

        require(tree.successor(80).isEmpty(),
            "Maximum should not have a successor.");

        require(tree.predecessor(20).isEmpty(),
            "Minimum should not have a predecessor.");

        require(
            tree.inorder().equals(
                List.of(20, 30, 40, 50, 60, 70, 80)
            ),
            "Inorder traversal failed."
        );

        require(
            tree.rangeQuery(30, 70).equals(
                List.of(30, 40, 50, 60, 70)
            ),
            "Range query failed."
        );

        require(tree.delete(50), "Two-child deletion failed.");
        require(tree.delete(20), "Leaf deletion failed.");
        require(!tree.delete(999), "Missing deletion failed.");

        require(tree.validate(), "Tree validation failed.");
        require(tree.size() == 5, "Incorrect node count.");

        AssessmentService service = new AssessmentService(
            new AssessmentPolicy(true, true, true)
        );

        AssessmentReport report = service.assess(tree);

        require(
            report.status() == ReviewStatus.PASSED,
            "Assessment failed."
        );

        require(!events.isEmpty(), "Events were not recorded.");

        BinarySearchTree empty = new BinarySearchTree();

        require(empty.validate(), "Empty tree should be valid.");
        require(empty.height() == -1, "Empty height incorrect.");
        require(empty.minimum().isEmpty(), "Empty minimum incorrect.");

        boolean invalidRangeDetected = false;

        try {
            tree.rangeQuery(100, 10);
        } catch (IllegalArgumentException expected) {
            invalidRangeDetected = true;
        }

        require(invalidRangeDetected, "Invalid range was accepted.");

        // Compare randomized operations with a sorted reference set.
        BinarySearchTree randomTree = new BinarySearchTree();
        TreeSet<Integer> reference = new TreeSet<>();
        Random random = new Random(42);

        for (int i = 0; i < 1000; i++) {
            int value = random.nextInt(201) - 100;

            if (random.nextBoolean()) {
                require(
                    randomTree.insert(value) == reference.add(value),
                    "Random insertion mismatch."
                );
            } else {
                require(
                    randomTree.delete(value) == reference.remove(value),
                    "Random deletion mismatch."
                );
            }

            require(
                randomTree.inorder().equals(
                    new ArrayList<>(reference)
                ),
                "Random traversal mismatch."
            );

            require(
                randomTree.validate(),
                "Random tree invariant failure."
            );
        }
    }

    public static void main(String[] args) {
        try {
            runTests();

            BinarySearchTree tree = new BinarySearchTree();

            for (int key : List.of(
                50, 30, 70, 20, 40, 60, 80, 65
            )) {
                tree.insert(key);
            }

            AssessmentService service = new AssessmentService(
                new AssessmentPolicy(true, true, true)
            );

            AssessmentReport report = service.assess(tree);

            System.out.println("BINARY SEARCH TREE ASSESSMENT");
            System.out.println("=============================");
            System.out.println("Tests: PASSED");
            System.out.println("Status: " + report.status());
            System.out.println("Size: " + report.nodeCount());
            System.out.println("Height: " + report.height());
            System.out.println("Balanced: " + report.balanced());
            System.out.println("Valid: " + report.valid());
            System.out.println("Inorder: " + report.inorder());

            System.out.println(
                "LCA(20, 40): " +
                tree.lowestCommonAncestor(20, 40).orElseThrow()
            );

            System.out.println(
                "Successor(60): " +
                tree.successor(60).orElseThrow()
            );

            System.out.println(
                "Predecessor(60): " +
                tree.predecessor(60).orElseThrow()
            );

            tree.delete(50);

            System.out.println(
                "After deleting 50: " + tree.inorder()
            );

        } catch (RuntimeException | AssertionError error) {
            System.err.println(
                "Assessment failure: " + error.getMessage()
            );
            System.exit(1);
        }
    }
}
