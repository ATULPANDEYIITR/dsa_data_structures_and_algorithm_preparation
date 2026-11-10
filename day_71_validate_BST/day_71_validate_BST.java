/*
 * VALIDATE BINARY SEARCH TREE
 *
 * Java 17
 * No third-party dependencies.
 *
 * Enterprise-oriented BST implementation:
 * - Immutable policy configuration.
 * - Explicit domain types.
 * - Range-based validation.
 * - Inorder validation.
 * - Duplicate-key policy.
 * - Successor and predecessor.
 * - Search and deletion.
 * - Lowest common ancestor.
 * - Validation service.
 * - Custom exceptions.
 * - Automated tests.
 */

import java.util.*;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class ValidateBST {

    enum DuplicatePolicy {
        FORBID,
        LEFT,
        RIGHT
    }

    record ValidationResult(
        boolean valid,
        int nodeCount,
        String method,
        String message
    ) {}

    static class BSTException extends RuntimeException {
        BSTException(String message) {
            super(message);
        }
    }

    static class DuplicateKeyException extends BSTException {
        DuplicateKeyException(int key) {
            super("Duplicate key is not permitted: " + key);
        }
    }

    static class MissingNodeException extends BSTException {
        MissingNodeException(int key) {
            super("Node does not exist: " + key);
        }
    }

    static final class Node {
        private int key;
        private Node left;
        private Node right;

        Node(int key) {
            this.key = key;
        }

        int key() {
            return key;
        }
    }

    record RangeState(
        Node node,
        Long low,
        Long high,
        boolean lowInclusive,
        boolean highInclusive
    ) {}

    static final class BinarySearchTree {

        private Node root;
        private int size;

        private final DuplicatePolicy duplicatePolicy;

        BinarySearchTree() {
            this(DuplicatePolicy.FORBID);
        }

        BinarySearchTree(DuplicatePolicy policy) {
            this.duplicatePolicy = Objects.requireNonNull(policy);
        }

        int size() {
            return size;
        }

        boolean isEmpty() {
            return root == null;
        }

        void insert(int key) {
            if (root == null) {
                root = new Node(key);
                size++;
                return;
            }

            Node current = root;

            while (true) {
                if (key < current.key) {
                    if (current.left == null) {
                        current.left = new Node(key);
                        size++;
                        return;
                    }

                    current = current.left;

                } else if (key > current.key) {
                    if (current.right == null) {
                        current.right = new Node(key);
                        size++;
                        return;
                    }

                    current = current.right;

                } else {
                    if (duplicatePolicy == DuplicatePolicy.FORBID) {
                        throw new DuplicateKeyException(key);
                    }

                    if (duplicatePolicy == DuplicatePolicy.LEFT) {
                        if (current.left == null) {
                            current.left = new Node(key);
                            size++;
                            return;
                        }

                        current = current.left;
                    } else {
                        if (current.right == null) {
                            current.right = new Node(key);
                            size++;
                            return;
                        }

                        current = current.right;
                    }
                }
            }
        }

        Optional<Node> search(int key) {
            Node current = root;

            while (current != null) {
                if (key == current.key) {
                    return Optional.of(current);
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return Optional.empty();
        }

        static boolean validateRange(Node root) {
            Deque<RangeState> stack = new ArrayDeque<>();

            if (root == null) {
                return true;
            }

            stack.push(new RangeState(
                root, null, null, false, false
            ));

            while (!stack.isEmpty()) {
                RangeState state = stack.pop();
                Node node = state.node();

                if (node == null) {
                    continue;
                }

                if (state.low() != null) {
                    if (node.key < state.low()) {
                        return false;
                    }

                    if (
                        node.key == state.low() &&
                        !state.lowInclusive()
                    ) {
                        return false;
                    }
                }

                if (state.high() != null) {
                    if (node.key > state.high()) {
                        return false;
                    }

                    if (
                        node.key == state.high() &&
                        !state.highInclusive()
                    ) {
                        return false;
                    }
                }

                stack.push(new RangeState(
                    node.left,
                    state.low(),
                    (long) node.key,
                    state.lowInclusive(),
                    false
                ));

                stack.push(new RangeState(
                    node.right,
                    (long) node.key,
                    state.high(),
                    false,
                    state.highInclusive()
                ));
            }

            return true;
        }

        static boolean validateInorder(
            Node root,
            DuplicatePolicy policy
        ) {
            Deque<Node> stack = new ArrayDeque<>();

            Node current = root;
            Integer previous = null;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();

                if (previous != null) {
                    if (policy == DuplicatePolicy.FORBID) {
                        if (current.key <= previous) {
                            return false;
                        }
                    } else if (current.key < previous) {
                        return false;
                    }
                }

                previous = current.key;
                current = current.right;
            }

            return true;
        }

        private boolean validateDuplicatePlacement() {
            record Ancestor(int key, String side) {}
            record State(Node node, List<Ancestor> ancestors) {}

            Deque<State> stack = new ArrayDeque<>();

            if (root != null) {
                stack.push(new State(root, List.of()));
            }

            while (!stack.isEmpty()) {
                State state = stack.pop();
                Node node = state.node();

                for (Ancestor ancestor : state.ancestors()) {
                    if (node.key == ancestor.key()) {
                        String expected =
                            duplicatePolicy == DuplicatePolicy.LEFT
                                ? "left"
                                : "right";

                        if (!ancestor.side().equals(expected)) {
                            return false;
                        }
                    }
                }

                List<Ancestor> leftAncestors =
                    new ArrayList<>(state.ancestors());

                leftAncestors.add(new Ancestor(node.key, "left"));

                List<Ancestor> rightAncestors =
                    new ArrayList<>(state.ancestors());

                rightAncestors.add(new Ancestor(node.key, "right"));

                if (node.left != null) {
                    stack.push(new State(
                        node.left,
                        List.copyOf(leftAncestors)
                    ));
                }

                if (node.right != null) {
                    stack.push(new State(
                        node.right,
                        List.copyOf(rightAncestors)
                    ));
                }
            }

            return true;
        }

        boolean isValid() {
            if (duplicatePolicy == DuplicatePolicy.FORBID) {
                return validateRange(root);
            }

            return validateInorder(root, duplicatePolicy)
                && validateDuplicatePlacement();
        }

        List<Integer> inorder() {
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

        List<Integer> preorder() {
            if (root == null) {
                return List.of();
            }

            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                result.add(node.key);

                if (node.right != null) {
                    stack.push(node.right);
                }

                if (node.left != null) {
                    stack.push(node.left);
                }
            }

            return List.copyOf(result);
        }

        Optional<Node> minimum(Node node) {
            if (node == null) {
                return Optional.empty();
            }

            while (node.left != null) {
                node = node.left;
            }

            return Optional.of(node);
        }

        Optional<Node> maximum(Node node) {
            if (node == null) {
                return Optional.empty();
            }

            while (node.right != null) {
                node = node.right;
            }

            return Optional.of(node);
        }

        Optional<Integer> minimum() {
            return minimum(root).map(Node::key);
        }

        Optional<Integer> maximum() {
            return maximum(root).map(Node::key);
        }

        Optional<Integer> successor(int key) {
            Node current = root;
            Node candidate = null;

            while (current != null) {
                if (key < current.key) {
                    candidate = current;
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            return candidate == null
                ? Optional.empty()
                : Optional.of(candidate.key);
        }

        Optional<Integer> predecessor(int key) {
            Node current = root;
            Node candidate = null;

            while (current != null) {
                if (key > current.key) {
                    candidate = current;
                    current = current.right;
                } else {
                    current = current.left;
                }
            }

            return candidate == null
                ? Optional.empty()
                : Optional.of(candidate.key);
        }

        Optional<Integer> successorOfNode(int key) {
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
                        return minimum(current.right)
                            .map(Node::key);
                    }

                    return candidate == null
                        ? Optional.empty()
                        : Optional.of(candidate.key);
                }
            }

            return Optional.empty();
        }

        Optional<Integer> predecessorOfNode(int key) {
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
                        return maximum(current.left)
                            .map(Node::key);
                    }

                    return candidate == null
                        ? Optional.empty()
                        : Optional.of(candidate.key);
                }
            }

            return Optional.empty();
        }

        Optional<Integer> lowestCommonAncestor(
            int first,
            int second
        ) {
            if (
                search(first).isEmpty() ||
                search(second).isEmpty()
            ) {
                return Optional.empty();
            }

            Node current = root;

            while (current != null) {
                if (first < current.key && second < current.key) {
                    current = current.left;
                } else if (
                    first > current.key &&
                    second > current.key
                ) {
                    current = current.right;
                } else {
                    return Optional.of(current.key);
                }
            }

            return Optional.empty();
        }

        boolean delete(int key) {
            Node parent = null;
            Node current = root;

            while (current != null && current.key != key) {
                parent = current;

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            if (current == null) {
                return false;
            }

            if (current.left != null && current.right != null) {
                Node successorParent = current;
                Node successor = current.right;

                while (successor.left != null) {
                    successorParent = successor;
                    successor = successor.left;
                }

                current.key = successor.key;

                if (successorParent == current) {
                    successorParent.right = successor.right;
                } else {
                    successorParent.left = successor.right;
                }
            } else {
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
            }

            size--;
            return true;
        }
    }

    static final class BSTValidationService {

        ValidationResult validate(
            BinarySearchTree tree,
            String method
        ) {
            Objects.requireNonNull(tree);
            Objects.requireNonNull(method);

            boolean valid = tree.isValid();

            return new ValidationResult(
                valid,
                tree.size(),
                method,
                valid
                    ? "BST invariants satisfied."
                    : "BST ordering violation detected."
            );
        }

        List<ValidationResult> validateBatch(
            Map<String, BinarySearchTree> trees
        ) {
            return trees.entrySet()
                .stream()
                .map(entry -> validate(
                    entry.getValue(),
                    entry.getKey()
                ))
                .toList();
        }
    }

    static void runTests() {
        BinarySearchTree tree = new BinarySearchTree();

        for (int key : new int[]{
            50, 30, 70, 20, 40, 60, 80
        }) {
            tree.insert(key);
        }

        assert tree.isValid();
        assert tree.size() == 7;

        assert tree.inorder().equals(
            List.of(20, 30, 40, 50, 60, 70, 80)
        );

        assert tree.preorder().equals(
            List.of(50, 30, 20, 40, 70, 60, 80)
        );

        assert tree.successor(40).orElseThrow() == 50;
        assert tree.predecessor(40).orElseThrow() == 30;

        assert tree.successorOfNode(50).orElseThrow() == 60;
        assert tree.predecessorOfNode(50).orElseThrow() == 40;

        assert tree.successor(80).isEmpty();
        assert tree.predecessor(20).isEmpty();

        assert tree.lowestCommonAncestor(20, 40)
            .orElseThrow() == 30;

        assert tree.delete(20);
        assert tree.delete(30);
        assert tree.delete(50);

        assert !tree.delete(999);
        assert tree.size() == 4;
        assert tree.isValid();

        BinarySearchTree empty = new BinarySearchTree();

        assert empty.isValid();
        assert empty.inorder().isEmpty();
        assert empty.minimum().isEmpty();

        Node invalid = new Node(10);
        invalid.left = new Node(5);
        invalid.left.right = new Node(12);
        invalid.right = new Node(15);

        assert !BinarySearchTree.validateRange(invalid);
        assert !BinarySearchTree.validateInorder(
            invalid,
            DuplicatePolicy.FORBID
        );

        BinarySearchTree duplicateTree =
            new BinarySearchTree(DuplicatePolicy.RIGHT);

        duplicateTree.insert(10);
        duplicateTree.insert(10);
        duplicateTree.insert(15);

        assert duplicateTree.isValid();

        boolean rejected = false;

        try {
            BinarySearchTree strict = new BinarySearchTree();
            strict.insert(10);
            strict.insert(10);
        } catch (DuplicateKeyException exception) {
            rejected = true;
        }

        assert rejected;

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        System.out.println("VALIDATE BINARY SEARCH TREE\n");

        BinarySearchTree tree = new BinarySearchTree();

        for (int key : new int[]{
            50, 30, 70, 20, 40, 60, 80
        }) {
            tree.insert(key);
        }

        System.out.println("1. TREE TRAVERSALS");
        System.out.println("Inorder: " + tree.inorder());
        System.out.println("Preorder: " + tree.preorder());

        System.out.println("\n2. VALIDATION");

        BSTValidationService service =
            new BSTValidationService();

        System.out.println(
            service.validate(tree, "range-and-inorder")
        );

        System.out.println("\n3. SUCCESSOR AND PREDECESSOR");

        for (int key : new int[]{
            20, 30, 40, 50, 60, 70, 80, 55
        }) {
            System.out.printf(
                "Key %d | Successor: %s | Predecessor: %s%n",
                key,
                tree.successor(key),
                tree.predecessor(key)
            );
        }

        System.out.println("\n4. NODE RELATIONSHIPS");

        System.out.println(
            "Successor of node 50: " +
            tree.successorOfNode(50)
        );

        System.out.println(
            "Predecessor of node 50: " +
            tree.predecessorOfNode(50)
        );

        System.out.println(
            "LCA(20, 40): " +
            tree.lowestCommonAncestor(20, 40)
        );

        System.out.println("\n5. BATCH VALIDATION");

        Map<String, BinarySearchTree> repository =
            new LinkedHashMap<>();

        repository.put("primary-index", tree);

        BinarySearchTree secondary = new BinarySearchTree();

        for (int key : new int[]{100, 90, 110}) {
            secondary.insert(key);
        }

        repository.put("secondary-index", secondary);

        service.validateBatch(repository)
            .forEach(System.out::println);

        System.out.println("\n6. DELETION");

        tree.delete(20);
        tree.delete(30);
        tree.delete(50);

        System.out.println("After deletion: " + tree.inorder());
        System.out.println("Valid: " + tree.isValid());

        System.out.println("\n7. AUTOMATED TESTS");
        runTests();
    }
}
