import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class DfsTraversals {

    static final class TreeNode {
        final int value;
        TreeNode left;
        TreeNode right;

        TreeNode(int value) {
            this.value = value;
        }
    }

    static final class TraversalException extends RuntimeException {
        TraversalException(String message) {
            super(message);
        }
    }

    private static void validateTree(TreeNode root) {
        Set<TreeNode> active = new HashSet<>();
        Set<TreeNode> visited = new HashSet<>();

        validate(root, active, visited);
    }

    private static void validate(
            TreeNode node,
            Set<TreeNode> active,
            Set<TreeNode> visited) {

        if (node == null) {
            return;
        }

        if (!active.add(node)) {
            throw new TraversalException("Cycle detected");
        }

        if (visited.contains(node)) {
            throw new TraversalException("Node has multiple parents");
        }

        validate(node.left, active, visited);
        validate(node.right, active, visited);

        active.remove(node);
        visited.add(node);
    }

    private static void preorderRecursiveVisit(
            TreeNode node,
            List<Integer> result) {

        if (node == null) return;

        result.add(node.value);
        preorderRecursiveVisit(node.left, result);
        preorderRecursiveVisit(node.right, result);
    }

    static List<Integer> preorderRecursive(TreeNode root) {
        validateTree(root);
        List<Integer> result = new ArrayList<>();
        preorderRecursiveVisit(root, result);
        return result;
    }

    private static void inorderRecursiveVisit(
            TreeNode node,
            List<Integer> result) {

        if (node == null) return;

        inorderRecursiveVisit(node.left, result);
        result.add(node.value);
        inorderRecursiveVisit(node.right, result);
    }

    static List<Integer> inorderRecursive(TreeNode root) {
        validateTree(root);
        List<Integer> result = new ArrayList<>();
        inorderRecursiveVisit(root, result);
        return result;
    }

    private static void postorderRecursiveVisit(
            TreeNode node,
            List<Integer> result) {

        if (node == null) return;

        postorderRecursiveVisit(node.left, result);
        postorderRecursiveVisit(node.right, result);
        result.add(node.value);
    }

    static List<Integer> postorderRecursive(TreeNode root) {
        validateTree(root);
        List<Integer> result = new ArrayList<>();
        postorderRecursiveVisit(root, result);
        return result;
    }

    static List<Integer> preorderIterative(TreeNode root) {
        validateTree(root);

        List<Integer> result = new ArrayList<>();
        if (root == null) return result;

        Deque<TreeNode> stack = new ArrayDeque<>();
        stack.push(root);

        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            result.add(node.value);

            if (node.right != null) stack.push(node.right);
            if (node.left != null) stack.push(node.left);
        }

        return result;
    }

    static List<Integer> inorderIterative(TreeNode root) {
        validateTree(root);

        List<Integer> result = new ArrayList<>();
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode current = root;

        while (current != null || !stack.isEmpty()) {
            while (current != null) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.add(current.value);
            current = current.right;
        }

        return result;
    }

    static List<Integer> postorderIterative(TreeNode root) {
        validateTree(root);

        List<Integer> result = new ArrayList<>();
        if (root == null) return result;

        Deque<TreeNode> first = new ArrayDeque<>();
        Deque<TreeNode> second = new ArrayDeque<>();

        first.push(root);

        while (!first.isEmpty()) {
            TreeNode node = first.pop();
            second.push(node);

            if (node.left != null) first.push(node.left);
            if (node.right != null) first.push(node.right);
        }

        while (!second.isEmpty()) {
            result.add(second.pop().value);
        }

        return result;
    }

    static List<Integer> postorderIterativeOneStack(TreeNode root) {
        validateTree(root);

        List<Integer> result = new ArrayList<>();
        Deque<TreeNode> stack = new ArrayDeque<>();

        TreeNode current = root;
        TreeNode previous = null;

        while (current != null || !stack.isEmpty()) {
            if (current != null) {
                stack.push(current);
                current = current.left;
                continue;
            }

            TreeNode node = stack.peek();

            if (node.right != null && previous != node.right) {
                current = node.right;
            } else {
                result.add(node.value);
                previous = stack.pop();
            }
        }

        return result;
    }

    static TreeNode sampleTree() {
        TreeNode root = new TreeNode(1);

        root.left = new TreeNode(2);
        root.right = new TreeNode(3);

        root.left.left = new TreeNode(4);
        root.left.right = new TreeNode(5);

        root.right.left = new TreeNode(6);
        root.right.right = new TreeNode(7);

        return root;
    }

    private static void require(
            boolean condition,
            String message) {

        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) {
        try {
            TreeNode tree = sampleTree();

            List<Integer> preorder =
                    List.of(1, 2, 4, 5, 3, 6, 7);
            List<Integer> inorder =
                    List.of(4, 2, 5, 1, 6, 3, 7);
            List<Integer> postorder =
                    List.of(4, 5, 2, 6, 7, 3, 1);

            require(preorderRecursive(tree).equals(preorder),
                    "Recursive preorder failed");
            require(preorderIterative(tree).equals(preorder),
                    "Iterative preorder failed");

            require(inorderRecursive(tree).equals(inorder),
                    "Recursive inorder failed");
            require(inorderIterative(tree).equals(inorder),
                    "Iterative inorder failed");

            require(postorderRecursive(tree).equals(postorder),
                    "Recursive postorder failed");
            require(postorderIterative(tree).equals(postorder),
                    "Iterative postorder failed");
            require(postorderIterativeOneStack(tree).equals(postorder),
                    "One-stack postorder failed");

            require(preorderIterative(null).isEmpty(),
                    "Empty preorder failed");
            require(inorderIterative(null).isEmpty(),
                    "Empty inorder failed");
            require(postorderIterative(null).isEmpty(),
                    "Empty postorder failed");

            TreeNode single = new TreeNode(42);
            require(inorderRecursive(single).equals(List.of(42)),
                    "Single-node traversal failed");

            /*
             * The iterative implementation is suitable when tree height
             * can be large enough to make recursive stack depth unsafe.
             */
            TreeNode deepRoot = new TreeNode(0);
            TreeNode current = deepRoot;

            for (int i = 1; i <= 5000; i++) {
                current.right = new TreeNode(i);
                current = current.right;
            }

            List<Integer> deepPre = preorderIterative(deepRoot);
            List<Integer> deepIn = inorderIterative(deepRoot);
            List<Integer> deepPost = postorderIterative(deepRoot);

            require(deepPre.size() == 5001,
                    "Deep preorder size failed");
            require(deepIn.get(0) == 0 && deepIn.get(5000) == 5000,
                    "Deep inorder values failed");
            require(deepPost.get(0) == 5000 && deepPost.get(5000) == 0,
                    "Deep postorder values failed");

            TreeNode cyclic = new TreeNode(10);
            cyclic.left = cyclic;

            try {
                preorderIterative(cyclic);
                throw new AssertionError("Cycle was not rejected");
            } catch (TraversalException expected) {
                System.out.println("Cycle validation passed.");
            }

            System.out.println("Preorder recursive:  " + preorderRecursive(tree));
            System.out.println("Preorder iterative:  " + preorderIterative(tree));
            System.out.println("Inorder recursive:   " + inorderRecursive(tree));
            System.out.println("Inorder iterative:   " + inorderIterative(tree));
            System.out.println("Postorder recursive: " + postorderRecursive(tree));
            System.out.println("Postorder iterative: " + postorderIterative(tree));
            System.out.println("Postorder one-stack: " +
                    postorderIterativeOneStack(tree));
            System.out.println("All traversal assertions passed.");

        } catch (RuntimeException | AssertionError ex) {
            System.err.println("Traversal failure: " + ex.getMessage());
            System.exit(1);
        }
    }
}
