import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.stream.Collectors;

/*
 * Enterprise product catalog indexed using a Binary Search Tree.
 * Unique product IDs are used as ordering keys.
 */
public class Main {

    enum OperationStatus {
        INSERTED,
        DUPLICATE,
        DELETED,
        NOT_FOUND
    }

    record Product(int id, String name, int stock) {
        Product {
            if (id <= 0) {
                throw new IllegalArgumentException(
                    "Product ID must be positive."
                );
            }

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Product name is required."
                );
            }

            if (stock < 0) {
                throw new IllegalArgumentException(
                    "Stock cannot be negative."
                );
            }
        }
    }

    static final class Node {
        Product product;
        Node left;
        Node right;

        Node(Product product) {
            this.product = product;
        }
    }

    static final class CatalogException extends RuntimeException {
        CatalogException(String message) {
            super(message);
        }
    }

    interface CatalogIndex {
        boolean insert(Product product);
        Optional<Product> search(int id);
        boolean delete(int id);
        List<Product> inorder();
        boolean isValid();
    }

    static final class BinarySearchTree
            implements CatalogIndex {

        private Node root;
        private int size;

        @Override
        public boolean insert(Product product) {
            Objects.requireNonNull(product, "Product is required.");

            if (root == null) {
                root = new Node(product);
                size++;
                return true;
            }

            Node current = root;

            while (true) {
                int comparison = Integer.compare(
                    product.id(),
                    current.product.id()
                );

                if (comparison == 0) return false;

                if (comparison < 0) {
                    if (current.left == null) {
                        current.left = new Node(product);
                        size++;
                        return true;
                    }
                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node(product);
                        size++;
                        return true;
                    }
                    current = current.right;
                }
            }
        }

        @Override
        public Optional<Product> search(int id) {
            Node current = root;

            while (current != null) {
                if (id == current.product.id()) {
                    return Optional.of(current.product);
                }

                current = id < current.product.id()
                    ? current.left
                    : current.right;
            }

            return Optional.empty();
        }

        private Node minimumNode(Node node) {
            if (node == null) return null;

            while (node.left != null) {
                node = node.left;
            }

            return node;
        }

        @Override
        public boolean delete(int id) {
            if (search(id).isEmpty()) return false;

            root = deleteNode(root, id);
            size--;

            return true;
        }

        private Node deleteNode(Node node, int id) {
            if (node == null) return null;

            if (id < node.product.id()) {
                node.left = deleteNode(node.left, id);
            } else if (id > node.product.id()) {
                node.right = deleteNode(node.right, id);
            } else {
                if (node.left == null) return node.right;
                if (node.right == null) return node.left;

                // Inorder successor replaces a two-child node.
                Node successor = minimumNode(node.right);

                node.product = successor.product;
                node.right = deleteNode(
                    node.right,
                    successor.product.id()
                );
            }

            return node;
        }

        @Override
        public List<Product> inorder() {
            List<Product> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            Node current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();
                result.add(current.product);
                current = current.right;
            }

            return Collections.unmodifiableList(result);
        }

        List<Integer> preorder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                result.add(node.product.id());

                if (node.right != null) stack.push(node.right);
                if (node.left != null) stack.push(node.left);
            }

            return List.copyOf(result);
        }

        List<Integer> postorder() {
            if (root == null) return List.of();

            Deque<Node> first = new ArrayDeque<>();
            Deque<Integer> second = new ArrayDeque<>();

            first.push(root);

            while (!first.isEmpty()) {
                Node node = first.pop();
                second.push(node.product.id());

                if (node.left != null) first.push(node.left);
                if (node.right != null) first.push(node.right);
            }

            return List.copyOf(second);
        }

        List<List<Integer>> levelOrder() {
            if (root == null) return List.of();

            List<List<Integer>> result = new ArrayList<>();
            Deque<Node> queue = new ArrayDeque<>();

            queue.add(root);

            while (!queue.isEmpty()) {
                int levelSize = queue.size();
                List<Integer> level = new ArrayList<>();

                for (int i = 0; i < levelSize; i++) {
                    Node node = queue.remove();

                    level.add(node.product.id());

                    if (node.left != null) queue.add(node.left);
                    if (node.right != null) queue.add(node.right);
                }

                result.add(List.copyOf(level));
            }

            return List.copyOf(result);
        }

        OptionalInt minimum() {
            Node node = minimumNode(root);

            return node == null
                ? OptionalInt.empty()
                : OptionalInt.of(node.product.id());
        }

        OptionalInt maximum() {
            Node node = root;

            if (node == null) return OptionalInt.empty();

            while (node.right != null) {
                node = node.right;
            }

            return OptionalInt.of(node.product.id());
        }

        int height() {
            if (root == null) return -1;

            Deque<Node> queue = new ArrayDeque<>();
            queue.add(root);

            int height = -1;

            while (!queue.isEmpty()) {
                int levelSize = queue.size();
                height++;

                for (int i = 0; i < levelSize; i++) {
                    Node node = queue.remove();

                    if (node.left != null) queue.add(node.left);
                    if (node.right != null) queue.add(node.right);
                }
            }

            return height;
        }

        OptionalInt kthSmallest(int k) {
            if (k < 1 || k > size) {
                return OptionalInt.empty();
            }

            Deque<Node> stack = new ArrayDeque<>();
            Node current = root;
            int count = 0;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();

                if (++count == k) {
                    return OptionalInt.of(current.product.id());
                }

                current = current.right;
            }

            return OptionalInt.empty();
        }

        @Override
        public boolean isValid() {
            return validate(root, Long.MIN_VALUE, Long.MAX_VALUE)
                && inorder().size() == size;
        }

        private boolean validate(
            Node node,
            long lower,
            long upper
        ) {
            if (node == null) return true;

            int key = node.product.id();

            if (key <= lower || key >= upper) return false;

            return validate(node.left, lower, key)
                && validate(node.right, key, upper);
        }

        int size() {
            return size;
        }

        BinarySearchTree balancedCopy() {
            List<Product> products = inorder();
            BinarySearchTree balanced = new BinarySearchTree();

            balanced.root = buildBalanced(
                products,
                0,
                products.size() - 1
            );

            balanced.size = products.size();

            return balanced;
        }

        private Node buildBalanced(
            List<Product> products,
            int start,
            int end
        ) {
            if (start > end) return null;

            int middle = start + (end - start) / 2;
            Node node = new Node(products.get(middle));

            node.left = buildBalanced(products, start, middle - 1);
            node.right = buildBalanced(products, middle + 1, end);

            return node;
        }
    }

    static final class CatalogService {
        private final BinarySearchTree index;

        CatalogService(BinarySearchTree index) {
            this.index = Objects.requireNonNull(index);
        }

        OperationStatus register(Product product) {
            return index.insert(product)
                ? OperationStatus.INSERTED
                : OperationStatus.DUPLICATE;
        }

        OperationStatus remove(int id) {
            return index.delete(id)
                ? OperationStatus.DELETED
                : OperationStatus.NOT_FOUND;
        }

        Optional<Product> getProduct(int id) {
            return index.search(id);
        }

        List<Product> productsInIdOrder() {
            return index.inorder();
        }

        List<Product> productsWithStock(int minimumStock) {
            if (minimumStock < 0) {
                throw new IllegalArgumentException(
                    "Minimum stock cannot be negative."
                );
            }

            return index.inorder()
                .stream()
                .filter(product -> product.stock() >= minimumStock)
                .collect(Collectors.toUnmodifiableList());
        }
    }

    public static void main(String[] args) {
        System.out.println("ENTERPRISE PRODUCT CATALOG BST");
        System.out.println("================================");

        BinarySearchTree index = new BinarySearchTree();
        CatalogService service = new CatalogService(index);

        List<Product> products = List.of(
            new Product(500, "Laptop", 12),
            new Product(300, "Keyboard", 30),
            new Product(700, "Monitor", 8),
            new Product(200, "Mouse", 45),
            new Product(400, "Headphones", 20),
            new Product(600, "Webcam", 15),
            new Product(800, "Printer", 5)
        );

        System.out.println("\nREGISTRATION");

        for (Product product : products) {
            System.out.println(
                product.id() + ": " + service.register(product)
            );
        }

        System.out.println(
            "Duplicate: " + service.register(
                new Product(500, "Duplicate Laptop", 1)
            )
        );

        System.out.println("\nSEARCH");
        System.out.println(service.getProduct(400));
        System.out.println(service.getProduct(999));

        System.out.println("\nINORDER");
        service.productsInIdOrder().forEach(System.out::println);

        System.out.println("\nPREORDER");
        System.out.println(index.preorder());

        System.out.println("\nPOSTORDER");
        System.out.println(index.postorder());

        System.out.println("\nLEVEL ORDER");
        System.out.println(index.levelOrder());

        System.out.println("\nMINIMUM: " + index.minimum());
        System.out.println("MAXIMUM: " + index.maximum());
        System.out.println("HEIGHT: " + index.height());
        System.out.println("THIRD SMALLEST: " + index.kthSmallest(3));

        System.out.println("\nSTOCK FILTER");
        System.out.println(service.productsWithStock(15));

        System.out.println("\nDELETION");
        System.out.println(service.remove(200));
        System.out.println(service.remove(300));
        System.out.println(service.remove(999));

        System.out.println("\nVALIDATION");
        System.out.println("Valid: " + index.isValid());
        System.out.println("Size: " + index.size());

        BinarySearchTree balanced = index.balancedCopy();

        System.out.println("\nBALANCED COPY");
        System.out.println("Height: " + balanced.height());
        System.out.println("Preorder: " + balanced.preorder());

        // Boundary and failure tests.
        BinarySearchTree empty = new BinarySearchTree();

        if (empty.minimum().isPresent()
                || empty.kthSmallest(1).isPresent()
                || empty.height() != -1) {
            throw new CatalogException("Empty-tree test failed.");
        }

        try {
            new Product(0, "Invalid", 5);
            throw new CatalogException("Invalid product was accepted.");
        } catch (IllegalArgumentException expected) {
            System.out.println("Invalid product rejected.");
        }

        assert index.isValid();
        assert balanced.isValid();
        assert index.size() == 5;
        assert index.kthSmallest(1).orElseThrow() == 400;
        assert index.kthSmallest(100).isEmpty();

        System.out.println("\nAll Java assertions passed.");
    }
}
