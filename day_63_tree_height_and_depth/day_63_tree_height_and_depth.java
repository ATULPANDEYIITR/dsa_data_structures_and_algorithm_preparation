import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class TreeDepthAnalysis {

    enum BalanceState {
        BALANCED,
        UNBALANCED
    }

    static final class TreeNode {
        final int value;
        TreeNode left;
        TreeNode right;

        TreeNode(int value) {
            this.value = value;
        }
    }

    record TreeMetrics(
            int maximumDepth,
            int minimumDepth,
            int leafCount,
            BalanceState balance,
            List<Integer> shortestPath
    ) {
        TreeMetrics {
            shortestPath = List.copyOf(shortestPath);
        }

        boolean isBalanced() {
            return balance == BalanceState.BALANCED;
        }
    }

    static final class InvalidTreeException extends IllegalArgumentException {
        InvalidTreeException(String message) {
            super(message);
        }
    }

    interface TreeAnalyzer {
        TreeMetrics analyze(TreeNode root);
    }

    static final class BinaryTreeAnalyzer implements TreeAnalyzer {

        @Override
        public TreeMetrics analyze(TreeNode root) {
            int maximumDepth = maximumDepth(root);
            ShortestPath shortest = shortestPath(root);
            int leaves = countLeaves(root);
            BalanceState balance =
                    balancedHeight(root) >= 0
                            ? BalanceState.BALANCED
                            : BalanceState.UNBALANCED;

            return new TreeMetrics(
                    maximumDepth,
                    shortest.depth(),
                    leaves,
                    balance,
                    shortest.path()
            );
        }

        private int maximumDepth(TreeNode node) {
            if (node == null) {
                return 0;
            }

            return 1 + Math.max(
                    maximumDepth(node.left),
                    maximumDepth(node.right)
            );
        }

        private int balancedHeight(TreeNode node) {
            if (node == null) {
                return 0;
            }

            int leftHeight = balancedHeight(node.left);
            if (leftHeight == -1) {
                return -1;
            }

            int rightHeight = balancedHeight(node.right);
            if (rightHeight == -1) {
                return -1;
            }

            if (Math.abs(leftHeight - rightHeight) > 1) {
                return -1;
            }

            return 1 + Math.max(leftHeight, rightHeight);
        }

        private int countLeaves(TreeNode root) {
            if (root == null) {
                return 0;
            }

            int count = 0;
            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode node = stack.pop();

                if (node.left == null && node.right == null) {
                    count++;
                    continue;
                }

                if (node.right != null) {
                    stack.push(node.right);
                }

                if (node.left != null) {
                    stack.push(node.left);
                }
            }

            return count;
        }

        private ShortestPath shortestPath(TreeNode root) {
            if (root == null) {
                return new ShortestPath(0, List.of());
            }

            record QueueEntry(TreeNode node, List<Integer> path) {}

            Deque<QueueEntry> queue = new ArrayDeque<>();
            queue.add(new QueueEntry(root, List.of(root.value)));

            while (!queue.isEmpty()) {
                QueueEntry current = queue.removeFirst();
                TreeNode node = current.node();

                if (node.left == null && node.right == null) {
                    return new ShortestPath(
                            current.path().size(),
                            current.path()
                    );
                }

                if (node.left != null) {
                    List<Integer> path = new ArrayList<>(current.path());
                    path.add(node.left.value);
                    queue.addLast(new QueueEntry(node.left, List.copyOf(path)));
                }

                if (node.right != null) {
                    List<Integer> path = new ArrayList<>(current.path());
                    path.add(node.right.value);
                    queue.addLast(new QueueEntry(node.right, List.copyOf(path)));
                }
            }

            throw new IllegalStateException("No leaf found.");
        }
    }

    record ShortestPath(int depth, List<Integer> path) {}

    static final class TreeFactory {

        static TreeNode fromLevelOrder(List<Integer> values) {
            Objects.requireNonNull(values, "Tree values cannot be null");

            if (values.isEmpty() || values.get(0) == null) {
                return null;
            }

            TreeNode root = new TreeNode(values.get(0));
            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.add(root);

            int index = 1;

            while (!queue.isEmpty() && index < values.size()) {
                TreeNode node = queue.removeFirst();

                if (index < values.size()) {
                    Integer value = values.get(index++);
                    if (value != null) {
                        node.left = new TreeNode(value);
                        queue.addLast(node.left);
                    }
                }

                if (index < values.size()) {
                    Integer value = values.get(index++);
                    if (value != null) {
                        node.right = new TreeNode(value);
                        queue.addLast(node.right);
                    }
                }
            }

            if (index < values.size()) {
                throw new InvalidTreeException(
                        "Input contains unreachable nodes."
                );
            }

            return root;
        }

        private TreeFactory() {
        }
    }

    static final class GovernanceService {
        private final TreeAnalyzer analyzer;

        GovernanceService(TreeAnalyzer analyzer) {
            this.analyzer = Objects.requireNonNull(analyzer);
        }

        TreeMetrics evaluate(List<Integer> values) {
            validate(values);
            return analyzer.analyze(TreeFactory.fromLevelOrder(values));
        }

        private void validate(List<Integer> values) {
            if (values.size() > 100_000) {
                throw new InvalidTreeException(
                        "Tree exceeds the supported size."
                );
            }

            if (!values.isEmpty() && values.get(0) == null) {
                boolean hasReachableData = values.stream()
                        .skip(1)
                        .anyMatch(value -> value != null);

                if (hasReachableData) {
                    throw new InvalidTreeException(
                            "A null root cannot contain reachable nodes."
                    );
                }
            }
        }
    }

    private static void print(String name, TreeMetrics metrics) {
        System.out.println("\n[" + name + "]");
        System.out.println("Maximum depth: " + metrics.maximumDepth());
        System.out.println("Minimum depth: " + metrics.minimumDepth());
        System.out.println("Leaf count: " + metrics.leafCount());
        System.out.println("Balanced: " + metrics.isBalanced());
        System.out.println("Shortest path: " + metrics.shortestPath());
    }

    private static void writeReport(TreeMetrics metrics) throws IOException {
        String path = """
                {
                  "maximumDepth": %d,
                  "minimumDepth": %d,
                  "leafCount": %d,
                  "balanced": %s,
                  "shortestPath": %s
                }
                """.formatted(
                metrics.maximumDepth(),
                metrics.minimumDepth(),
                metrics.leafCount(),
                metrics.isBalanced(),
                metrics.shortestPath()
        );

        Files.writeString(
                Path.of("tree_analysis_report.json"),
                path
        );
    }

    public static void main(String[] args) {
        try {
            GovernanceService service =
                    new GovernanceService(new BinaryTreeAnalyzer());

            Map<String, List<Integer>> examples = Map.of(
                    "balanced",
                    List.of(3, 9, 20, null, null, 15, 7),
                    "unbalanced",
                    List.of(1, 2, 2, 3, 3, null, null, 4, 4),
                    "single",
                    List.of(42),
                    "skewed",
                    List.of(1, 2, null, 3, null, 4),
                    "empty",
                    List.of()
            );

            examples.forEach((name, values) ->
                    print(name, service.evaluate(values))
            );

            List<Integer> production = List.of(
                    10, 5, 15, 3, 7, 12, 18,
                    1, 4, 6, 8, null, 13, 17, 20
            );

            TreeMetrics result = service.evaluate(production);

            if (result.maximumDepth() != 4
                    || result.minimumDepth() != 3
                    || result.leafCount() != 7
                    || !result.isBalanced()) {
                throw new IllegalStateException(
                        "Production assertions failed."
                );
            }

            writeReport(result);

            System.out.println("\nProduction example validated successfully.");
            System.out.println(
                    "Report written to tree_analysis_report.json"
            );
        } catch (IOException | RuntimeException error) {
            System.err.println("Error: " + error.getMessage());
            System.exit(1);
        }
    }
}
