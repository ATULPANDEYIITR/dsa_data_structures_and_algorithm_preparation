import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class RecursiveTrees {

    static final class TreeNode {
        private final String label;
        private final List<TreeNode> children = new ArrayList<>();

        TreeNode(String label) {
            this.label = Objects.requireNonNull(label);
        }

        void addChild(TreeNode child) {
            children.add(Objects.requireNonNull(child));
        }

        String label() {
            return label;
        }

        List<TreeNode> children() {
            return List.copyOf(children);
        }
    }

    static TreeNode fibonacciTree(int n) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "Fibonacci index cannot be negative"
            );
        }

        TreeNode node = new TreeNode("fib(" + n + ")");

        if (n <= 1) {
            return node;
        }

        node.addChild(fibonacciTree(n - 1));
        node.addChild(fibonacciTree(n - 2));

        return node;
    }

    static TreeNode subsetTree(List<String> items) {
        Objects.requireNonNull(items);

        if (items.stream().anyMatch(Objects::isNull)) {
            throw new IllegalArgumentException(
                "Subset items cannot contain null values"
            );
        }

        return buildSubsetTree(items, 0, List.of());
    }

    private static TreeNode buildSubsetTree(
        List<String> items,
        int index,
        List<String> selected
    ) {
        if (index == items.size()) {
            return new TreeNode(
                "subset {" + String.join(", ", selected) + "}"
            );
        }

        String item = items.get(index);
        TreeNode node = new TreeNode("item=" + item);

        TreeNode excluded = buildSubsetTree(
            items,
            index + 1,
            selected
        );

        TreeNode excludedLabel = new TreeNode(
            "exclude " + item + " -> " + excluded.label()
        );

        List<String> includedValues = new ArrayList<>(selected);
        includedValues.add(item);

        TreeNode included = buildSubsetTree(
            items,
            index + 1,
            List.copyOf(includedValues)
        );

        TreeNode includedLabel = new TreeNode(
            "include " + item + " -> " + included.label()
        );

        node.addChild(excludedLabel);
        node.addChild(includedLabel);

        return node;
    }

    static TreeNode binaryChoiceTree(int depth) {
        if (depth < 0) {
            throw new IllegalArgumentException(
                "Depth cannot be negative"
            );
        }

        return buildBinaryTree(depth, 0, "");
    }

    private static TreeNode buildBinaryTree(
        int depth,
        int level,
        String choices
    ) {
        TreeNode node = new TreeNode(
            "level=" + level +
            ", choices=" +
            (choices.isEmpty() ? "empty" : choices)
        );

        if (level == depth) {
            return node;
        }

        node.addChild(
            buildBinaryTree(depth, level + 1, choices + "0")
        );

        node.addChild(
            buildBinaryTree(depth, level + 1, choices + "1")
        );

        return node;
    }

    static TreeNode mergeSortTree(List<Integer> values) {
        Objects.requireNonNull(values);

        if (values.stream().anyMatch(Objects::isNull)) {
            throw new IllegalArgumentException(
                "Merge-sort values cannot contain null"
            );
        }

        TreeNode node = new TreeNode(
            "sort(" + values + ")"
        );

        if (values.size() <= 1) {
            return node;
        }

        int midpoint = values.size() / 2;

        List<Integer> left = List.copyOf(
            values.subList(0, midpoint)
        );

        List<Integer> right = List.copyOf(
            values.subList(midpoint, values.size())
        );

        node.addChild(mergeSortTree(left));
        node.addChild(mergeSortTree(right));

        return node;
    }

    static void printTree(
        TreeNode node,
        String prefix,
        boolean isLast
    ) {
        System.out.println(
            prefix +
            (isLast ? "└── " : "├── ") +
            node.label()
        );

        String childPrefix =
            prefix + (isLast ? "    " : "│   ");

        List<TreeNode> children = node.children();

        for (int i = 0; i < children.size(); i++) {
            printTree(
                children.get(i),
                childPrefix,
                i == children.size() - 1
            );
        }
    }

    static long countNodes(TreeNode node) {
        long total = 1;

        for (TreeNode child : node.children()) {
            total += countNodes(child);
        }

        return total;
    }

    static int treeHeight(TreeNode node) {
        if (node.children().isEmpty()) {
            return 1;
        }

        int maxHeight = 0;

        for (TreeNode child : node.children()) {
            maxHeight = Math.max(
                maxHeight,
                treeHeight(child)
            );
        }

        return maxHeight + 1;
    }

    static long fibonacciIterative(int n) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "n cannot be negative"
            );
        }

        long previous = 0;
        long current = 1;

        for (int i = 0; i < n; i++) {
            long next = previous + current;
            previous = current;
            current = next;
        }

        return previous;
    }

    public static void main(String[] args) {
        try {
            System.out.println("FIBONACCI RECURSION TREE");
            TreeNode fib = fibonacciTree(5);
            printTree(fib, "", true);
            System.out.println(
                "Recursive calls: " + countNodes(fib)
            );
            System.out.println(
                "Tree height: " + treeHeight(fib)
            );
            System.out.println(
                "Fibonacci(5): " + fibonacciIterative(5)
            );

            System.out.println("\nSUBSET RECURSION TREE");
            TreeNode subsets = subsetTree(
                List.of("A", "B", "C")
            );
            printTree(subsets, "", true);

            System.out.println(
                "Subset count: " + (1L << 3)
            );

            System.out.println("\nBINARY CHOICE RECURSION TREE");
            TreeNode binary = binaryChoiceTree(3);
            printTree(binary, "", true);
            System.out.println("Leaf count: 8");

            System.out.println(
                "\nDIVIDE-AND-CONQUER RECURSION TREE"
            );

            TreeNode merge = mergeSortTree(
                List.of(8, 3, 7, 4, 2, 6)
            );

            printTree(merge, "", true);

            System.out.println(
                "Recursive calls: " + countNodes(merge)
            );
            System.out.println(
                "Tree height: " + treeHeight(merge)
            );
        } catch (RuntimeException ex) {
            System.err.println(
                "Execution failure: " + ex.getMessage()
            );
        }
    }
}
