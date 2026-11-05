import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

public class Main {

    enum OperationStatus {
        INSERTED,
        DUPLICATE,
        DELETED,
        NOT_FOUND
    }

    record TreeMetrics(
        int height,
        int nodeCount,
        boolean balanced,
        boolean valid
    ) {}

    record SearchResult(
        boolean found,
        int comparisons
    ) {}

    record TreeAudit(
        long version,
        TreeMetrics metrics
    ) {}

    static class TreeValidationException extends RuntimeException {
        public TreeValidationException(String message) {
            super(message);
        }
    }

    static final class Node {
        int key;
        int height = 1;
        Node left;
        Node right;

        Node(int key) {
            this.key = key;
        }
    }

    interface SearchableTree {
        SearchResult search(int key);
        int height();
    }

    static final class AVLTree implements SearchableTree {

        private Node root;
        private int size;
        private final AtomicLong version = new AtomicLong();

        private int heightOf(Node node) {
            return node == null ? 0 : node.height;
        }

        private int balanceFactor(Node node) {
            return node == null
                ? 0
                : heightOf(node.left) - heightOf(node.right);
        }

        private void updateHeight(Node node) {
            node.height = 1 + Math.max(
                heightOf(node.left),
                heightOf(node.right)
            );
        }

        private Node rotateRight(Node y) {
            if (y == null || y.left == null) {
                throw new TreeValidationException(
                    "Invalid right rotation."
                );
            }

            Node x = y.left;
            Node middle = x.right;

            x.right = y;
            y.left = middle;

            updateHeight(y);
            updateHeight(x);

            return x;
        }

        private Node rotateLeft(Node x) {
            if (x == null || x.right == null) {
                throw new TreeValidationException(
                    "Invalid left rotation."
                );
            }

            Node y = x.right;
            Node middle = y.left;

            y.left = x;
            x.right = middle;

            updateHeight(x);
            updateHeight(y);

            return y;
        }

        private Node rebalance(Node node) {
            updateHeight(node);

            int factor = balanceFactor(node);

            if (factor > 1) {
                if (balanceFactor(node.left) < 0) {
                    node.left = rotateLeft(node.left);
                }

                return rotateRight(node);
            }

            if (factor < -1) {
                if (balanceFactor(node.right) > 0) {
                    node.right = rotateRight(node.right);
                }

                return rotateLeft(node);
            }

            return node;
        }

        private Node insertNode(Node node, int key) {
            if (node == null) {
                return new Node(key);
            }

            if (key < node.key) {
                node.left = insertNode(node.left, key);
            } else if (key > node.key) {
                node.right = insertNode(node.right, key);
            } else {
                return node;
            }

            return rebalance(node);
        }

        public OperationStatus insert(int key) {
            if (search(key).found()) {
                return OperationStatus.DUPLICATE;
            }

            root = insertNode(root, key);
            size++;
            version.incrementAndGet();

            return OperationStatus.INSERTED;
        }

        private Node minimum(Node node) {
            while (node.left != null) {
                node = node.left;
            }

            return node;
        }

        private Node deleteNode(Node node, int key) {
            if (node == null) {
                return null;
            }

            if (key < node.key) {
                node.left = deleteNode(node.left, key);
            } else if (key > node.key) {
                node.right = deleteNode(node.right, key);
            } else {
                if (node.left == null) {
                    return node.right;
                }

                if (node.right == null) {
                    return node.left;
                }

                Node successor = minimum(node.right);
                node.key = successor.key;

                node.right = deleteNode(
                    node.right,
                    successor.key
                );
            }

            return rebalance(node);
        }

        public OperationStatus delete(int key) {
            if (!search(key).found()) {
                return OperationStatus.NOT_FOUND;
            }

            root = deleteNode(root, key);
            size--;
            version.incrementAndGet();

            return OperationStatus.DELETED;
        }

        @Override
        public SearchResult search(int key) {
            Node current = root;
            int comparisons = 0;

            while (current != null) {
                comparisons++;

                if (key == current.key) {
                    return new SearchResult(true, comparisons);
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return new SearchResult(false, comparisons);
        }

        @Override
        public int height() {
            return heightOf(root);
        }

        public List<Integer> inorder() {
            List<Integer> result = new ArrayList<>();
            inorderTraversal(root, result);
            return List.copyOf(result);
        }

        private void inorderTraversal(
            Node node,
            List<Integer> result
        ) {
            if (node == null) return;

            inorderTraversal(node.left, result);
            result.add(node.key);
            inorderTraversal(node.right, result);
        }

        private TreeMetrics inspect(
            Node node,
            Optional<Integer> lower,
            Optional<Integer> upper
        ) {
            if (node == null) {
                return new TreeMetrics(0, 0, true, true);
            }

            if (
                (lower.isPresent() && node.key <= lower.get()) ||
                (upper.isPresent() && node.key >= upper.get())
            ) {
                return new TreeMetrics(0, 0, false, false);
            }

            TreeMetrics left = inspect(
                node.left,
                lower,
                Optional.of(node.key)
            );

            TreeMetrics right = inspect(
                node.right,
                Optional.of(node.key),
                upper
            );

            int expectedHeight = 1 + Math.max(
                left.height(),
                right.height()
            );

            boolean heightValid =
                node.height == expectedHeight;

            boolean locallyBalanced =
                Math.abs(left.height() - right.height()) <= 1;

            boolean valid =
                left.valid() &&
                right.valid() &&
                heightValid;

            boolean balanced =
                left.balanced() &&
                right.balanced() &&
                locallyBalanced;

            return new TreeMetrics(
                expectedHeight,
                left.nodeCount() + right.nodeCount() + 1,
                balanced,
                valid
            );
        }

        public TreeAudit audit() {
            TreeMetrics metrics = inspect(
                root,
                Optional.empty(),
                Optional.empty()
            );

            if (!metrics.valid()) {
                throw new TreeValidationException(
                    "BST ordering or stored height is invalid."
                );
            }

            if (metrics.nodeCount() != size) {
                throw new TreeValidationException(
                    "Tree node count mismatch."
                );
            }

            return new TreeAudit(version.get(), metrics);
        }
    }

    static final class RepositoryIndex implements SearchableTree {

        private static final class Entry {
            final int id;
            Entry left;
            Entry right;

            Entry(int id) {
                this.id = id;
            }
        }

        private Entry root;
        private int size;

        public OperationStatus register(int repositoryId) {
            Entry entry = new Entry(repositoryId);

            if (root == null) {
                root = entry;
                size++;
                return OperationStatus.INSERTED;
            }

            Entry current = root;

            while (true) {
                if (repositoryId == current.id) {
                    return OperationStatus.DUPLICATE;
                }

                if (repositoryId < current.id) {
                    if (current.left == null) {
                        current.left = entry;
                        size++;
                        return OperationStatus.INSERTED;
                    }

                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = entry;
                        size++;
                        return OperationStatus.INSERTED;
                    }

                    current = current.right;
                }
            }
        }

        @Override
        public SearchResult search(int id) {
            Entry current = root;
            int comparisons = 0;

            while (current != null) {
                comparisons++;

                if (current.id == id) {
                    return new SearchResult(true, comparisons);
                }

                current = id < current.id
                    ? current.left
                    : current.right;
            }

            return new SearchResult(false, comparisons);
        }

        private int calculateHeight(Entry node) {
            if (node == null) return 0;

            return 1 + Math.max(
                calculateHeight(node.left),
                calculateHeight(node.right)
            );
        }

        @Override
        public int height() {
            return calculateHeight(root);
        }

        public int size() {
            return size;
        }
    }

    static final class RepositoryIndexService {

        private final AVLTree index = new AVLTree();

        public void registerRepository(int id) {
            if (id <= 0) {
                throw new TreeValidationException(
                    "Repository ID must be positive."
                );
            }

            OperationStatus result = index.insert(id);

            if (result == OperationStatus.DUPLICATE) {
                throw new TreeValidationException(
                    "Repository ID already exists."
                );
            }

            index.audit();
        }

        public boolean repositoryExists(int id) {
            return index.search(id).found();
        }

        public TreeAudit getAudit() {
            return index.audit();
        }

        public List<Integer> getRepositoryIds() {
            return index.inorder();
        }
    }

    public static void main(String[] args) {
        try {
            System.out.println("ENTERPRISE BALANCED TREE INDEX");
            System.out.println("================================");

            RepositoryIndexService service =
                new RepositoryIndexService();

            int[] repositoryIds = {
                500, 300, 700, 200, 400,
                600, 800, 100, 250, 350, 450
            };

            for (int id : repositoryIds) {
                service.registerRepository(id);
            }

            System.out.println("\nAVL REPOSITORY INDEX");

            TreeAudit audit = service.getAudit();

            System.out.println("Version: " + audit.version());
            System.out.println("Nodes: " +
                audit.metrics().nodeCount());
            System.out.println("Height: " +
                audit.metrics().height());
            System.out.println("Balanced: " +
                audit.metrics().balanced());
            System.out.println("Valid: " +
                audit.metrics().valid());

            System.out.println("Repository IDs: " +
                service.getRepositoryIds());

            System.out.println(
                "Repository 400 exists: " +
                service.repositoryExists(400)
            );

            System.out.println("\nDELETION");

            AVLTree deletionTree = new AVLTree();

            for (int id : repositoryIds) {
                deletionTree.insert(id);
            }

            System.out.println(
                "Delete 500: " + deletionTree.delete(500)
            );

            System.out.println(
                "Post-deletion audit: " + deletionTree.audit()
            );

            System.out.println("\nUNBALANCED INDEX");

            RepositoryIndex ordinary = new RepositoryIndex();

            for (int id = 1; id <= 100; id++) {
                ordinary.register(id);
            }

            SearchResult result = ordinary.search(100);

            System.out.println("Nodes: " + ordinary.size());
            System.out.println("Height: " + ordinary.height());
            System.out.println("Search comparisons: " +
                result.comparisons());

            System.out.println("\nEDGE CASES");

            AVLTree empty = new AVLTree();

            System.out.println(
                "Empty tree height: " + empty.height()
            );

            System.out.println(
                "Empty tree audit: " + empty.audit()
            );

            AVLTree single = new AVLTree();

            single.insert(10);
            single.insert(10);

            System.out.println(
                "Duplicate insertion: " +
                single.audit().metrics().nodeCount()
            );

            single.delete(10);

            System.out.println(
                "After deleting final node: " + single.audit()
            );

            try {
                service.registerRepository(-10);
            } catch (TreeValidationException error) {
                System.out.println(
                    "Expected validation error: " +
                    error.getMessage()
                );
            }

            System.out.println("\nAll checks completed.");

        } catch (RuntimeException error) {
            System.err.println(
                "Repository index failure: " +
                error.getMessage()
            );

            System.exit(1);
        }
    }
}
