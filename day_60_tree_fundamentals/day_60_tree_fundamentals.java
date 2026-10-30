import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Enterprise-style binary-tree domain model with explicit node ownership,
 * structural validation, and a separate metrics/reporting service.
 *
 * Height is measured in edges. A leaf has height 0.
 * Depth is measured in edges. The root has depth 0.
 * Level is depth + 1. The root is on level 1.
 */
public class TreeFundamentals {

    enum Side {
        LEFT,
        RIGHT
    }

    static final class TreeException extends IllegalArgumentException {
        TreeException(String message) {
            super(message);
        }
    }

    static final class Node {
        private final String id;
        private final String value;
        private Node parent;
        private Node left;
        private Node right;

        private Node(String id, String value) {
            if (id == null || id.isBlank()) {
                throw new TreeException("Node ID cannot be blank.");
            }
            if (value == null || value.isBlank()) {
                throw new TreeException("Node value cannot be blank.");
            }

            this.id = id;
            this.value = value;
        }

        String id() {
            return id;
        }

        String value() {
            return value;
        }

        Node parent() {
            return parent;
        }

        Node left() {
            return left;
        }

        Node right() {
            return right;
        }

        boolean isLeaf() {
            return left == null && right == null;
        }
    }

    /**
     * A registry distinguishes nodes known to a tree from nodes currently
     * reachable from its root. This permits detached subtrees to be assembled
     * before they are attached.
     */
    static final class BinaryTree {
        private final Node root;
        private final Map<String, Node> knownNodes = new LinkedHashMap<>();
        private final Set<Node> ownedNodes =
            Collections.newSetFromMap(new IdentityHashMap<>());

        BinaryTree(String rootId, String rootValue) {
            this.root = new Node(rootId, rootValue);
            knownNodes.put(rootId, root);
            ownedNodes.add(root);
        }

        Node root() {
            return root;
        }

        Node createNode(String id, String value) {
            if (knownNodes.containsKey(id)) {
                throw new TreeException("Duplicate node ID: " + id);
            }

            Node node = new Node(id, value);
            knownNodes.put(id, node);
            return node;
        }

        private List<Node> collectSubtree(Node start) {
            if (start == null) {
                throw new TreeException("Cannot inspect a null subtree.");
            }
            if (start.parent != null) {
                throw new TreeException("Subtree root must not have a parent.");
            }

            List<Node> nodes = new ArrayList<>();
            Set<Node> visited =
                Collections.newSetFromMap(new IdentityHashMap<>());

            Deque<Node> stack = new ArrayDeque<>();
            stack.push(start);

            while (!stack.isEmpty()) {
                Node current = stack.pop();

                if (!visited.add(current)) {
                    throw new TreeException(
                        "Cycle or shared child detected at " + current.id
                    );
                }

                nodes.add(current);

                if (current.right != null) {
                    if (current.right.parent != current) {
                        throw new TreeException(
                            "Invalid parent reference at " + current.right.id
                        );
                    }
                    stack.push(current.right);
                }

                if (current.left != null) {
                    if (current.left.parent != current) {
                        throw new TreeException(
                            "Invalid parent reference at " + current.left.id
                        );
                    }
                    stack.push(current.left);
                }
            }

            return nodes;
        }

        void attach(Node parent, Node child, Side side) {
            if (!ownedNodes.contains(parent)) {
                throw new TreeException("Parent is not connected to this tree.");
            }
            if (child == null || !knownNodes.containsValue(child)) {
                throw new TreeException("Child was not registered by this tree.");
            }
            if (ownedNodes.contains(child)) {
                throw new TreeException("Child already belongs to this tree.");
            }
            if (child.parent != null) {
                throw new TreeException("Incoming subtree root is not detached.");
            }
            if (side == null) {
                throw new TreeException("A child side must be specified.");
            }

            List<Node> incoming = collectSubtree(child);

            for (Node node : incoming) {
                if (ownedNodes.contains(node)) {
                    throw new TreeException("Subtree overlaps existing nodes.");
                }
            }

            if (side == Side.LEFT) {
                if (parent.left != null) {
                    throw new TreeException("Left child slot is occupied.");
                }
                parent.left = child;
            } else {
                if (parent.right != null) {
                    throw new TreeException("Right child slot is occupied.");
                }
                parent.right = child;
            }

            child.parent = parent;
            ownedNodes.addAll(incoming);
        }

        boolean contains(Node node) {
            return ownedNodes.contains(node);
        }

        void validate() {
            List<Node> reachable = collectSubtree(root);

            if (reachable.size() != ownedNodes.size()) {
                throw new TreeException(
                    "Some registered nodes are not connected to the root."
                );
            }

            for (Node node : reachable) {
                if (!knownNodes.containsValue(node)) {
                    throw new TreeException("Unregistered node in tree.");
                }
            }
        }

        int depth(Node node) {
            requireMember(node);

            int depth = 0;
            Node current = node;
            Set<Node> visited =
                Collections.newSetFromMap(new IdentityHashMap<>());

            while (current.parent != null) {
                if (!visited.add(current)) {
                    throw new TreeException("Cycle in parent references.");
                }

                current = current.parent;
                depth++;
            }

            if (current != root) {
                throw new TreeException("Node is disconnected from root.");
            }

            return depth;
        }

        int level(Node node) {
            return depth(node) + 1;
        }

        private void requireMember(Node node) {
            if (node == null || !ownedNodes.contains(node)) {
                throw new TreeException("Node does not belong to this tree.");
            }
        }

        int height(Node node) {
            requireMember(node);

            record Visit(Node node, boolean expanded) {}

            Deque<Visit> stack = new ArrayDeque<>();
            Map<Node, Integer> heights = new IdentityHashMap<>();
            stack.push(new Visit(node, false));

            // Postorder evaluation computes the child values before each parent.
            while (!stack.isEmpty()) {
                Visit visit = stack.pop();
                Node current = visit.node();

                if (!visit.expanded()) {
                    stack.push(new Visit(current, true));

                    if (current.right != null) {
                        stack.push(new Visit(current.right, false));
                    }
                    if (current.left != null) {
                        stack.push(new Visit(current.left, false));
                    }
                } else {
                    int leftHeight = current.left == null
                        ? -1
                        : heights.get(current.left);

                    int rightHeight = current.right == null
                        ? -1
                        : heights.get(current.right);

                    heights.put(current, 1 + Math.max(leftHeight, rightHeight));
                }
            }

            return heights.get(node);
        }

        int treeHeight() {
            return height(root);
        }

        int subtreeSize(Node node) {
            requireMember(node);
            return collectSubtree(node).size();
        }

        List<List<String>> levels() {
            List<List<String>> result = new ArrayList<>();
            Deque<Node> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                int levelSize = queue.size();
                List<String> currentLevel = new ArrayList<>();

                for (int i = 0; i < levelSize; i++) {
                    Node node = queue.remove();
                    currentLevel.add(node.id);

                    if (node.left != null) queue.add(node.left);
                    if (node.right != null) queue.add(node.right);
                }

                result.add(List.copyOf(currentLevel));
            }

            return List.copyOf(result);
        }

        List<Node> preorderNodes() {
            List<Node> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                result.add(node);

                if (node.right != null) stack.push(node.right);
                if (node.left != null) stack.push(node.left);
            }

            return List.copyOf(result);
        }

        List<String> preorder() {
            return preorderNodes().stream().map(Node::id).toList();
        }

        List<String> inorder() {
            List<String> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();
            Node current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();
                result.add(current.id);
                current = current.right;
            }

            return List.copyOf(result);
        }

        List<String> postorder() {
            record Visit(Node node, boolean expanded) {}

            List<String> result = new ArrayList<>();
            Deque<Visit> stack = new ArrayDeque<>();
            stack.push(new Visit(root, false));

            while (!stack.isEmpty()) {
                Visit visit = stack.pop();
                Node node = visit.node();

                if (visit.expanded()) {
                    result.add(node.id);
                    continue;
                }

                stack.push(new Visit(node, true));

                if (node.right != null) {
                    stack.push(new Visit(node.right, false));
                }
                if (node.left != null) {
                    stack.push(new Visit(node.left, false));
                }
            }

            return List.copyOf(result);
        }
    }

    record NodeMetrics(
        String id,
        String value,
        String parentId,
        String leftId,
        String rightId,
        int depth,
        int level,
        int height,
        boolean leaf,
        int subtreeSize
    ) {}

    /**
     * Reporting is separate from structural mutation.
     * This service computes one report after the tree is assembled.
     */
    static final class TreeMetricsService {
        List<NodeMetrics> createReport(BinaryTree tree) {
            tree.validate();

            List<NodeMetrics> report = new ArrayList<>();

            for (Node node : tree.preorderNodes()) {
                report.add(new NodeMetrics(
                    node.id,
                    node.value,
                    node.parent == null ? null : node.parent.id,
                    node.left == null ? null : node.left.id,
                    node.right == null ? null : node.right.id,
                    tree.depth(node),
                    tree.level(node),
                    tree.height(node),
                    node.isLeaf(),
                    tree.subtreeSize(node)
                ));
            }

            return List.copyOf(report);
        }
    }

    private static BinaryTree buildExampleTree() {
        /*
         *              A
         *             / \
         *            B   C
         *           / \   \
         *          D   E   F
         *             /
         *            G
         */
        BinaryTree tree = new BinaryTree("A", "Root");
        Node a = tree.root();

        Node b = tree.createNode("B", "Left child of A");
        Node c = tree.createNode("C", "Right child of A");
        Node d = tree.createNode("D", "Left child of B");
        Node e = tree.createNode("E", "Right child of B");
        Node f = tree.createNode("F", "Right child of C");
        Node g = tree.createNode("G", "Left child of E");

        tree.attach(a, b, Side.LEFT);
        tree.attach(a, c, Side.RIGHT);
        tree.attach(b, d, Side.LEFT);
        tree.attach(b, e, Side.RIGHT);
        tree.attach(c, f, Side.RIGHT);
        tree.attach(e, g, Side.LEFT);

        return tree;
    }

    public static void main(String[] args) {
        try {
            BinaryTree tree = buildExampleTree();
            TreeMetricsService metricsService = new TreeMetricsService();

            tree.validate();

            System.out.println("BINARY TREE FUNDAMENTALS");
            System.out.println("Node count: " + tree.preorder().size());
            System.out.println("Tree height: " + tree.treeHeight());
            System.out.println("Levels: " + tree.levels());
            System.out.println("Preorder: " + tree.preorder());
            System.out.println("Inorder: " + tree.inorder());
            System.out.println("Postorder: " + tree.postorder());

            System.out.println("\nNODE METRICS");
            for (NodeMetrics metrics : metricsService.createReport(tree)) {
                System.out.println(metrics);
            }

            Node b = tree.root().left;
            System.out.println("\nSUBTREE ROOTED AT B");
            System.out.println("Height: " + tree.height(b));
            System.out.println("Size: " + tree.subtreeSize(b));

            System.out.println("\nINVALID ATTACHMENT TEST");
            try {
                tree.attach(tree.root().right, tree.root(), Side.LEFT);
            } catch (TreeException error) {
                System.out.println("Rejected: " + error.getMessage());
            }

            if (tree.treeHeight() != 3 ||
                tree.depth(tree.root().right.right) != 2 ||
                tree.subtreeSize(b) != 4) {
                throw new TreeException("Tree metric assertion failed.");
            }

            System.out.println("\nAll structural checks passed.");
        } catch (TreeException error) {
            System.err.println("Tree operation failed: " + error.getMessage());
            System.exit(1);
        }
    }
}
