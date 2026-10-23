#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

class TreeNode {
public:
    explicit TreeNode(std::string label)
        : label_(std::move(label)) {}

    void addChild(std::unique_ptr<TreeNode> child) {
        children_.push_back(std::move(child));
    }

    const std::string& label() const {
        return label_;
    }

    const std::vector<std::unique_ptr<TreeNode>>& children() const {
        return children_;
    }

private:
    std::string label_;
    std::vector<std::unique_ptr<TreeNode>> children_;
};

std::unique_ptr<TreeNode> fibonacciTree(int n) {
    if (n < 0) {
        throw std::invalid_argument("Fibonacci index cannot be negative");
    }

    auto node = std::make_unique<TreeNode>("fib(" + std::to_string(n) + ")");

    if (n <= 1) {
        return node;
    }

    node->addChild(fibonacciTree(n - 1));
    node->addChild(fibonacciTree(n - 2));

    return node;
}

std::unique_ptr<TreeNode> binaryChoiceTree(
    int depth,
    int level = 0,
    const std::string& choices = ""
) {
    if (depth < 0) {
        throw std::invalid_argument("Tree depth cannot be negative");
    }

    auto node = std::make_unique<TreeNode>(
        "level=" + std::to_string(level) +
        ", choices=" + (choices.empty() ? "empty" : choices)
    );

    if (level == depth) {
        return node;
    }

    node->addChild(
        binaryChoiceTree(depth, level + 1, choices + "0")
    );
    node->addChild(
        binaryChoiceTree(depth, level + 1, choices + "1")
    );

    return node;
}

std::unique_ptr<TreeNode> subsetTree(
    const std::vector<std::string>& items,
    std::size_t index = 0,
    const std::vector<std::string>& selected = {}
) {
    if (index == items.size()) {
        std::string label = "subset {";

        for (std::size_t i = 0; i < selected.size(); ++i) {
            if (i > 0) {
                label += ", ";
            }
            label += selected[i];
        }

        label += "}";
        return std::make_unique<TreeNode>(label);
    }

    const std::string& item = items[index];

    auto node = std::make_unique<TreeNode>(
        "item=" + item
    );

    auto excluded = subsetTree(items, index + 1, selected);
    excluded = std::make_unique<TreeNode>(
        "exclude " + item + " -> " + excluded->label()
    );

    auto includedSelection = selected;
    includedSelection.push_back(item);

    auto included = subsetTree(
        items,
        index + 1,
        includedSelection
    );

    included = std::make_unique<TreeNode>(
        "include " + item + " -> " + included->label()
    );

    node->addChild(std::move(excluded));
    node->addChild(std::move(included));

    return node;
}

std::unique_ptr<TreeNode> mergeSortTree(
    const std::vector<int>& values
) {
    std::string label = "sort([";

    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            label += ", ";
        }
        label += std::to_string(values[i]);
    }

    label += "])";

    auto node = std::make_unique<TreeNode>(label);

    if (values.size() <= 1) {
        return node;
    }

    const std::size_t midpoint = values.size() / 2;

    std::vector<int> left(
        values.begin(),
        values.begin() + static_cast<std::ptrdiff_t>(midpoint)
    );

    std::vector<int> right(
        values.begin() + static_cast<std::ptrdiff_t>(midpoint),
        values.end()
    );

    node->addChild(mergeSortTree(left));
    node->addChild(mergeSortTree(right));

    return node;
}

void printTree(
    const TreeNode& node,
    const std::string& prefix = "",
    bool isLast = true
) {
    std::cout
        << prefix
        << (isLast ? "└── " : "├── ")
        << node.label()
        << '\n';

    const std::string childPrefix =
        prefix + (isLast ? "    " : "│   ");

    const auto& children = node.children();

    for (std::size_t i = 0; i < children.size(); ++i) {
        printTree(
            *children[i],
            childPrefix,
            i + 1 == children.size()
        );
    }
}

std::size_t countNodes(const TreeNode& node) {
    std::size_t total = 1;

    for (const auto& child : node.children()) {
        total += countNodes(*child);
    }

    return total;
}

std::size_t treeHeight(const TreeNode& node) {
    if (node.children().empty()) {
        return 1;
    }

    std::size_t height = 0;

    for (const auto& child : node.children()) {
        height = std::max(height, treeHeight(*child));
    }

    return height + 1;
}

long long fibonacciIterative(int n) {
    if (n < 0) {
        throw std::invalid_argument("n cannot be negative");
    }

    long long a = 0;
    long long b = 1;

    for (int i = 0; i < n; ++i) {
        long long next = a + b;
        a = b;
        b = next;
    }

    return a;
}

int main() {
    try {
        std::cout << "FIBONACCI RECURSION TREE\n";
        auto fib = fibonacciTree(5);
        printTree(*fib);
        std::cout << "Recursive calls: "
                  << countNodes(*fib) << '\n';
        std::cout << "Tree height: "
                  << treeHeight(*fib) << '\n';
        std::cout << "Fibonacci(5): "
                  << fibonacciIterative(5) << "\n\n";

        std::cout << "SUBSET RECURSION TREE\n";
        const std::vector<std::string> items{
            "A", "B", "C"
        };

        auto subsets = subsetTree(items);
        printTree(*subsets);

        std::cout << "\nBINARY CHOICE RECURSION TREE\n";
        auto binary = binaryChoiceTree(3);
        printTree(*binary);

        std::cout << "Leaf count: "
                  << static_cast<std::size_t>(std::pow(2, 3))
                  << "\n\n";

        std::cout << "DIVIDE-AND-CONQUER RECURSION TREE\n";
        const std::vector<int> values{
            8, 3, 7, 4, 2, 6
        };

        auto merge = mergeSortTree(values);
        printTree(*merge);

        std::cout << "Recursive calls: "
                  << countNodes(*merge) << '\n';
        std::cout << "Tree height: "
                  << treeHeight(*merge) << '\n';
    }
    catch (const std::exception& ex) {
        std::cerr << "Failure: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
