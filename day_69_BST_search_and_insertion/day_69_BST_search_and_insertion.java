import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.OptionalInt;
import java.util.concurrent.atomic.AtomicLong;

/*
 * Enterprise Asset Registry using a Binary Search Tree.
 *
 * Java 17 implementation featuring:
 * - Generic BST
 * - Unique integer identifiers
 * - Search, insertion, minimum, maximum
 * - Immutable operation records
 * - Service-level validation
 * - Integrity checks
 * - Reporting
 * - Performance comparison
 */

public class Main {

    enum OperationType {
        INSERT,
        SEARCH,
        MINIMUM,
        MAXIMUM
    }

    record OperationResult(
        OperationType operation,
        int key,
        boolean successful,
        int comparisons
    ) {}

    record Asset(int id, String description) {
        public Asset {
            if (id <= 0) {
                throw new IllegalArgumentException(
                    "Asset ID must be positive."
                );
            }

            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Asset description is required."
                );
            }

            description = description.trim();
        }
    }

    interface SearchableTree<T extends Comparable<T>> {
        boolean insert(T key);
        boolean search(T key);
        OptionalInt minimum();
        OptionalInt maximum();
        List<T> inorder();
        int height();
    }

    static final class Node<T> {
        final T key;
        Node<T> left;
        Node<T> right;

        Node(T key) {
            this.key = key;
        }
    }

    static class BinarySearchTree<T extends Comparable<T>>
            implements SearchableTree<T> {

        private Node<T> root;
        private int size;
        private int lastComparisons;

        private final AtomicLong totalOperations =
            new AtomicLong();

        @Override
        public boolean insert(T key) {
            validate(key);

            if (root == null) {
                root = new Node<>(key);
                size++;
                totalOperations.incrementAndGet();
                return true;
            }

            Node<T> current = root;

            while (true) {
                int comparison = key.compareTo(current.key);

                if (comparison == 0) {
                    return false;
                }

                if (comparison < 0) {
                    if (current.left == null) {
                        current.left = new Node<>(key);
                        size++;
                        totalOperations.incrementAndGet();
                        return true;
                    }

                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node<>(key);
                        size++;
                        totalOperations.incrementAndGet();
                        return true;
                    }

                    current = current.right;
                }
            }
        }

        @Override
        public boolean search(T key) {
            validate(key);

            lastComparisons = 0;
            Node<T> current = root;

            while (current != null) {
                lastComparisons++;

                int comparison = key.compareTo(current.key);

                if (comparison == 0) {
                    return true;
                }

                current = comparison < 0
                    ? current.left
                    : current.right;
            }

            return false;
        }

        @Override
        public OptionalInt minimum() {
            if (root == null) {
                return OptionalInt.empty();
            }

            Node<T> current = root;

            while (current.left != null) {
                current = current.left;
            }

            if (current.key instanceof Integer value) {
                return OptionalInt.of(value);
            }

            throw new UnsupportedOperationException(
                "Minimum OptionalInt requires Integer keys."
            );
        }

        @Override
        public OptionalInt maximum() {
            if (root == null) {
                return OptionalInt.empty();
            }

            Node<T> current = root;

            while (current.right != null) {
                current = current.right;
            }

            if (current.key instanceof Integer value) {
                return OptionalInt.of(value);
            }

            throw new UnsupportedOperationException(
                "Maximum OptionalInt requires Integer keys."
            );
        }

        @Override
        public List<T> inorder() {
            List<T> result = new ArrayList<>();
            ArrayDeque<Node<T>> stack = new ArrayDeque<>();

            Node<T> current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();
                result.add(current.key);
                current = current.right;
            }

            return Collections.unmodifiableList(result);
        }

        @Override
        public int height() {
            if (root == null) {
                return -1;
            }

            record DepthNode<T>(Node<T> node, int depth) {}

            ArrayDeque<DepthNode<T>> queue = new ArrayDeque<>();
            queue.add(new DepthNode<>(root, 0));

            int maxDepth = 0;

            while (!queue.isEmpty()) {
                DepthNode<T> entry = queue.remove();

                maxDepth = Math.max(maxDepth, entry.depth());

                if (entry.node().left != null) {
                    queue.add(new DepthNode<>(
                        entry.node().left,
                        entry.depth() + 1
                    ));
                }

                if (entry.node().right != null) {
                    queue.add(new DepthNode<>(
                        entry.node().right,
                        entry.depth() + 1
                    ));
                }
            }

            return maxDepth;
        }

        boolean validate() {
            record Frame<T>(
                Node<T> node,
                T lower,
                T upper
            ) {}

            ArrayDeque<Frame<T>> stack = new ArrayDeque<>();
            stack.push(new Frame<>(root, null, null));

            int visited = 0;

            while (!stack.isEmpty()) {
                Frame<T> frame = stack.pop();
                Node<T> node = frame.node();

                if (node == null) {
                    continue;
                }

                if (
                    frame.lower() != null &&
                    node.key.compareTo(frame.lower()) <= 0
                ) {
                    return false;
                }

                if (
                    frame.upper() != null &&
                    node.key.compareTo(frame.upper()) >= 0
                ) {
                    return false;
                }

                visited++;

                stack.push(new Frame<>(
                    node.left,
                    frame.lower(),
                    node.key
                ));

                stack.push(new Frame<>(
                    node.right,
                    node.key,
                    frame.upper()
                ));
            }

            return visited == size;
        }

        int size() {
            return size;
        }

        int lastComparisons() {
            return lastComparisons;
        }

        long totalOperations() {
            return totalOperations.get();
        }

        private void validate(T key) {
            if (key == null) {
                throw new IllegalArgumentException(
                    "Null keys are not permitted."
                );
            }
        }

        void exportReport(Path path) throws IOException {
            if (!path.getFileName().toString().endsWith(".json")) {
                throw new IllegalArgumentException(
                    "Report must use the .json extension."
                );
            }

            String json = """
                {
                  "size": %d,
                  "height": %d,
                  "minimum": %s,
                  "maximum": %s,
                  "keys": %s,
                  "valid": %s
                }
                """.formatted(
                    size,
                    height(),
                    minimum().isPresent()
                        ? minimum().getAsInt() : "null",
                    maximum().isPresent()
                        ? maximum().getAsInt() : "null",
                    inorder(),
                    validate()
                );

            Files.writeString(
                path,
                json,
                StandardCharsets.UTF_8
            );
        }
    }

    static final class AssetRegistryService {

        private final BinarySearchTree<Integer> index =
            new BinarySearchTree<>();

        private final List<Asset> assets = new ArrayList<>();

        boolean registerAsset(Asset asset) {
            if (asset == null) {
                throw new IllegalArgumentException(
                    "Asset cannot be null."
                );
            }

            // Insert the index entry only when the ID is unique.
            boolean inserted = index.insert(asset.id());

            if (!inserted) {
                return false;
            }

            assets.add(asset);
            return true;
        }

        OptionalInt findAsset(int id) {
            return index.search(id)
                ? OptionalInt.of(id)
                : OptionalInt.empty();
        }

        List<Asset> registeredAssets() {
            return assets.stream()
                .sorted(Comparator.comparingInt(Asset::id))
                .toList();
        }

        BinarySearchTree<Integer> index() {
            return index;
        }
    }

    static List<Integer> medianFirstOrder(List<Integer> sorted) {
        record Range(int low, int high) {}

        List<Integer> result = new ArrayList<>();
        ArrayDeque<Range> stack = new ArrayDeque<>();

        stack.push(new Range(0, sorted.size() - 1));

        while (!stack.isEmpty()) {
            Range range = stack.pop();

            if (range.low() > range.high()) {
                continue;
            }

            int middle = range.low() +
                (range.high() - range.low()) / 2;

            result.add(sorted.get(middle));

            stack.push(new Range(
                middle + 1,
                range.high()
            ));

            stack.push(new Range(
                range.low(),
                middle - 1
            ));
        }

        return result;
    }

    static void benchmark() {
        final int count = 2000;

        List<Integer> values = new ArrayList<>();

        for (int i = 1; i <= count; i++) {
            values.add(i);
        }

        BinarySearchTree<Integer> balanced =
            new BinarySearchTree<>();

        BinarySearchTree<Integer> skewed =
            new BinarySearchTree<>();

        for (int value : medianFirstOrder(values)) {
            balanced.insert(value);
        }

        for (int value : values) {
            skewed.insert(value);
        }

        for (BinarySearchTree<Integer> tree :
                List.of(balanced, skewed)) {

            long start = System.nanoTime();

            boolean found = tree.search(count);

            long elapsed = System.nanoTime() - start;

            System.out.printf(
                "Found=%s, height=%d, comparisons=%d, time=%d ns%n",
                found,
                tree.height(),
                tree.lastComparisons(),
                elapsed
            );
        }
    }

    public static void main(String[] args) {
        try {
            AssetRegistryService service =
                new AssetRegistryService();

            System.out.println("=== Enterprise Asset Registry ===");

            List<Asset> records = List.of(
                new Asset(500, "Network Router"),
                new Asset(300, "Application Server"),
                new Asset(700, "Storage System"),
                new Asset(200, "Firewall"),
                new Asset(400, "Database Server"),
                new Asset(600, "Backup Appliance"),
                new Asset(800, "Load Balancer"),
                new Asset(350, "Security Gateway"),
                new Asset(450, "Monitoring Server")
            );

            for (Asset asset : records) {
                System.out.println(
                    "Register " + asset.id() + ": " +
                    service.registerAsset(asset)
                );
            }

            System.out.println(
                "Duplicate registration: " +
                service.registerAsset(
                    new Asset(500, "Duplicate Router")
                )
            );

            BinarySearchTree<Integer> index = service.index();

            System.out.println(
                "Search 400: " + service.findAsset(400)
            );

            System.out.println(
                "Search 999: " + service.findAsset(999)
            );

            System.out.println(
                "Minimum: " + index.minimum()
            );

            System.out.println(
                "Maximum: " + index.maximum()
            );

            System.out.println(
                "Sorted IDs: " + index.inorder()
            );

            System.out.println(
                "Height: " + index.height()
            );

            System.out.println(
                "Integrity: " + index.validate()
            );

            System.out.println("\nRegistered Assets:");

            service.registeredAssets().forEach(
                asset -> System.out.println(
                    asset.id() + " | " + asset.description()
                )
            );

            if (!index.validate()) {
                throw new IllegalStateException(
                    "Index integrity failure."
                );
            }

            if (!index.search(400)) {
                throw new IllegalStateException(
                    "Search test failed."
                );
            }

            if (
                index.minimum().orElseThrow() != 200 ||
                index.maximum().orElseThrow() != 800
            ) {
                throw new IllegalStateException(
                    "Boundary test failed."
                );
            }

            BinarySearchTree<Integer> empty =
                new BinarySearchTree<>();

            if (
                empty.minimum().isPresent() ||
                empty.maximum().isPresent() ||
                empty.search(10)
            ) {
                throw new IllegalStateException(
                    "Empty tree test failed."
                );
            }

            index.exportReport(Path.of("bst_report.json"));

            System.out.println("\nReport exported.");

            benchmark();

            System.out.println("\nAll tests passed.");

        } catch (IOException | IllegalArgumentException |
                 IllegalStateException exception) {

            System.err.println(
                "Application failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
