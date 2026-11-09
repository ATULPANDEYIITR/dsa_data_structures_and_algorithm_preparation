import java.util.*;

/*
 * Binary Search Tree Deletion
 *
 * Java 17
 *
 * Enterprise-oriented implementation:
 * - Explicit node and operation domain types.
 * - Immutable deletion results.
 * - Successor and predecessor strategies.
 * - Centralized tree service.
 * - Structural validation.
 * - Operation audit records.
 * - Safe handling of invalid and missing keys.
 */

public class Main {

    enum DeletionCase {
        LEAF,
        ONE_CHILD,
        TWO_CHILDREN,
        NOT_FOUND
    }

    enum ReplacementStrategy {
        SUCCESSOR,
        PREDECESSOR
    }

    record DeletionResult(
        int requestedKey,
        boolean deleted,
        DeletionCase deletionCase,
        Integer replacementKey,
        int remainingNodes
    ) {}

    record AuditEvent(
        String operation,
        int key,
        boolean successful,
        String details
    ) {}

    static final class Node {
        final int key;
        Node left;
        Node right;

        Node(int key) {
            this.key = key;
        }
    }

    static final class TreeValidationException
            extends RuntimeException {

        TreeValidationException(String message) {
            super(message);
        }
    }

    interface ReplacementPolicy {
        Node select(Node subtree);
    }

    static final class SuccessorPolicy
            implements ReplacementPolicy {

        @Override
        public Node select(Node subtree) {
            if (subtree == null) {
                throw new IllegalArgumentException(
                    "Replacement subtree cannot be null."
                );
            }

            Node current = subtree;

            while (current.left != null) {
                current = current.left;
            }

            return current;
        }
    }

    static final class PredecessorPolicy
            implements ReplacementPolicy {

        @Override
        public Node select(Node subtree) {
            if (subtree == null) {
                throw new IllegalArgumentException(
                    "Replacement subtree cannot be null."
                );
            }

            Node current = subtree;

            while (current.right != null) {
                current = current.right;
            }

            return current;
        }
    }

    static final class BinarySearchTree {
        private Node root;
        private int size;

        private final List<AuditEvent> auditLog =
            new ArrayList<>();

        private final ReplacementPolicy successorPolicy =
            new SuccessorPolicy();

        private final ReplacementPolicy predecessorPolicy =
            new PredecessorPolicy();

        public int size() {
            return size;
        }

        public boolean isEmpty() {
            return root == null;
        }

        public List<AuditEvent> auditLog() {
            return List.copyOf(auditLog);
        }

        public boolean insert(int key) {
            if (root == null) {
                root = new Node(key);
                size++;
                record("INSERT", key, true, "Root created");
                return true;
            }

            Node current = root;

            while (true) {
                if (key == current.key) {
                    record(
                        "INSERT",
                        key,
                        false,
                        "Duplicate rejected"
                    );
                    return false;
                }

                if (key < current.key) {
                    if (current.left == null) {
                        current.left = new Node(key);
                        break;
                    }
                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node(key);
                        break;
                    }
                    current = current.right;
                }
            }

            size++;
            record("INSERT", key, true, "Node inserted");
            return true;
        }

        public OptionalInt search(int key) {
            Node current = root;

            while (current != null) {
                if (key == current.key) {
                    return OptionalInt.of(current.key);
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return OptionalInt.empty();
        }

        private Node minimum(Node node) {
            while (node != null && node.left != null) {
                node = node.left;
            }

            return node;
        }

        private Node maximum(Node node) {
            while (node != null && node.right != null) {
                node = node.right;
            }

            return node;
        }

        public OptionalInt successor(int key) {
            Node current = root;
            Node candidate = null;

            while (current != null) {
                if (key < current.key) {
                    candidate = current;
                    current = current.left;
                } else if (key > current.key) {
                    current = current.right;
                } else {
                    if (current.right != null) {
                        return OptionalInt.of(
                            minimum(current.right).key
                        );
                    }

                    return candidate == null
                        ? OptionalInt.empty()
                        : OptionalInt.of(candidate.key);
                }
            }

            return OptionalInt.empty();
        }

        public OptionalInt predecessor(int key) {
            Node current = root;
            Node candidate = null;

            while (current != null) {
                if (key > current.key) {
                    candidate = current;
                    current = current.right;
                } else if (key < current.key) {
                    current = current.left;
                } else {
                    if (current.left != null) {
                        return OptionalInt.of(
                            maximum(current.left).key
                        );
                    }

                    return candidate == null
                        ? OptionalInt.empty()
                        : OptionalInt.of(candidate.key);
                }
            }

            return OptionalInt.empty();
        }

        public DeletionResult delete(
            int key,
            ReplacementStrategy strategy
        ) {
            Objects.requireNonNull(
                strategy,
                "Replacement strategy is required."
            );

            Node existing = findNode(key);

            if (existing == null) {
                DeletionResult result = new DeletionResult(
                    key,
                    false,
                    DeletionCase.NOT_FOUND,
                    null,
                    size
                );

                record("DELETE", key, false, "Key not found");
                return result;
            }

            DeletionCase deletionCase;
            Integer replacementKey = null;

            if (existing.left == null && existing.right == null) {
                deletionCase = DeletionCase.LEAF;
            } else if (
                existing.left == null || existing.right == null
            ) {
                deletionCase = DeletionCase.ONE_CHILD;
            } else {
                deletionCase = DeletionCase.TWO_CHILDREN;

                ReplacementPolicy policy =
                    strategy == ReplacementStrategy.SUCCESSOR
                        ? successorPolicy
                        : predecessorPolicy;

                Node replacement = policy.select(
                    strategy == ReplacementStrategy.SUCCESSOR
                        ? existing.right
                        : existing.left
                );

                replacementKey = replacement.key;
            }

            root = deleteRecursive(root, key, strategy);
            size--;

            if (!validate()) {
                throw new TreeValidationException(
                    "BST invariant violated after deletion."
                );
            }

            DeletionResult result = new DeletionResult(
                key,
                true,
                deletionCase,
                replacementKey,
                size
            );

            record(
                "DELETE",
                key,
                true,
                "Case: " + deletionCase +
                ", strategy: " + strategy
            );

            return result;
        }

        private Node findNode(int key) {
            Node current = root;

            while (current != null) {
                if (key == current.key) return current;

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return null;
        }

        private Node deleteRecursive(
            Node node,
            int key,
            ReplacementStrategy strategy
        ) {
            if (node == null) return null;

            if (key < node.key) {
                node.left = deleteRecursive(
                    node.left, key, strategy
                );
                return node;
            }

            if (key > node.key) {
                node.right = deleteRecursive(
                    node.right, key, strategy
                );
                return node;
            }

            if (node.left == null) {
                return node.right;
            }

            if (node.right == null) {
                return node.left;
            }

            if (strategy == ReplacementStrategy.SUCCESSOR) {
                Node successor = minimum(node.right);

                node.right = deleteRecursive(
                    node.right,
                    successor.key,
                    strategy
                );

                return newReplacementNode(
                    successor.key,
                    node.left,
                    node.right
                );
            }

            Node predecessor = maximum(node.left);

            node.left = deleteRecursive(
                node.left,
                predecessor.key,
                strategy
            );

            return newReplacementNode(
                predecessor.key,
                node.left,
                node.right
            );
        }

        private Node newReplacementNode(
            int key,
            Node left,
            Node right
        ) {
            Node replacement = new Node(key);
            replacement.left = left;
            replacement.right = right;
            return replacement;
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

        public List<List<Integer>> levelOrder() {
            if (root == null) return List.of();

            List<List<Integer>> result = new ArrayList<>();
            Queue<Node> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                int count = queue.size();
                List<Integer> level = new ArrayList<>();

                for (int i = 0; i < count; i++) {
                    Node node = queue.remove();
                    level.add(node.key);

                    if (node.left != null) queue.add(node.left);
                    if (node.right != null) queue.add(node.right);
                }

                result.add(List.copyOf(level));
            }

            return List.copyOf(result);
        }

        private boolean validateNode(
            Node node,
            Long lower,
            Long upper,
            int[] count
        ) {
            if (node == null) return true;

            if (lower != null && node.key <= lower) return false;
            if (upper != null && node.key >= upper) return false;

            count[0]++;

            return validateNode(
                node.left, lower, (long) node.key, count
            ) && validateNode(
                node.right, (long) node.key, upper, count
            );
        }

        public boolean validate() {
            int[] count = {0};

            return validateNode(
                root, null, null, count
            ) && count[0] == size;
        }

        private void record(
            String operation,
            int key,
            boolean success,
            String details
        ) {
            auditLog.add(
                new AuditEvent(operation, key, success, details)
            );
        }
    }

    private static void printTree(BinarySearchTree tree) {
        System.out.println("Inorder: " + tree.inorder());
        System.out.println("Preorder: " + tree.preorder());
        System.out.println("Levels: " + tree.levelOrder());
        System.out.println("Size: " + tree.size());
        System.out.println("Valid: " + tree.validate());
    }

    public static void main(String[] args) {
        BinarySearchTree tree = new BinarySearchTree();

        int[] values = {
            50, 30, 70, 20, 40, 60, 80, 35, 45, 65
        };

        for (int value : values) {
            if (!tree.insert(value)) {
                throw new IllegalStateException(
                    "Unexpected duplicate."
                );
            }
        }

        System.out.println("INITIAL TREE");
        printTree(tree);

        System.out.println("\nORDER STATISTICS");
        System.out.println("Successor 50: " + tree.successor(50));
        System.out.println("Predecessor 50: " + tree.predecessor(50));

        System.out.println("\nLEAF DELETION");
        System.out.println(
            tree.delete(20, ReplacementStrategy.SUCCESSOR)
        );

        System.out.println("\nONE-CHILD DELETION");
        System.out.println(
            tree.delete(60, ReplacementStrategy.SUCCESSOR)
        );

        System.out.println("\nTWO-CHILD DELETION");
        System.out.println(
            tree.delete(70, ReplacementStrategy.SUCCESSOR)
        );

        System.out.println("\nROOT DELETION");
        System.out.println(
            tree.delete(50, ReplacementStrategy.SUCCESSOR)
        );

        System.out.println("\nPREDECESSOR-BASED DELETION");
        System.out.println(
            tree.delete(40, ReplacementStrategy.PREDECESSOR)
        );

        printTree(tree);

        // Missing key.
        assert !tree.delete(
            999, ReplacementStrategy.SUCCESSOR
        ).deleted();

        // Duplicate key.
        assert !tree.insert(35);

        // Invalid strategy.
        try {
            tree.delete(35, null);
            throw new AssertionError("Null strategy accepted.");
        } catch (NullPointerException expected) {
            System.out.println("Null strategy rejected.");
        }

        // Empty and single-node trees.
        BinarySearchTree single = new BinarySearchTree();
        assert !single.delete(
            1, ReplacementStrategy.SUCCESSOR
        ).deleted();

        assert single.insert(10);
        assert single.delete(
            10, ReplacementStrategy.SUCCESSOR
        ).deleted();

        assert single.isEmpty();
        assert single.validate();

        System.out.println("\nAUDIT RECORDS");

        tree.auditLog().forEach(System.out::println);

        System.out.println("\nALL TESTS PASSED.");
    }
}
