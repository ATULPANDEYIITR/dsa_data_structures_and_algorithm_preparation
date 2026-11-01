#include <algorithm>
#include <cmath>
#include <cstddef>
#include <deque>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

struct TreeNode {
    int value;
    unique_ptr<TreeNode> left;
    unique_ptr<TreeNode> right;

    explicit TreeNode(int value)
        : value(value), left(nullptr), right(nullptr) {}
};

enum class TraversalMode {
    LEFT_TO_RIGHT,
    ZIGZAG
};

struct LevelReport {
    size_t depth;
    size_t nodeCount;
    long long sum;
    int minimum;
    int maximum;
    double average;
};

class BinaryTree {
private:
    unique_ptr<TreeNode> root;

public:
    BinaryTree() = default;

    explicit BinaryTree(unique_ptr<TreeNode> root)
        : root(std::move(root)) {}

    /*
     * Build a tree from level-order values.
     * nullopt represents a missing child.
     *
     * The queue contains only actual nodes, avoiding unnecessary
     * storage for missing descendants.
     */
    static BinaryTree fromLevelOrder(
        const vector<optional<int>>& values
    ) {
        if (values.empty()) {
            return BinaryTree();
        }

        if (!values[0].has_value()) {
            for (size_t i = 1; i < values.size(); ++i) {
                if (values[i].has_value()) {
                    throw invalid_argument(
                        "A tree cannot have descendants without a root."
                    );
                }
            }

            return BinaryTree();
        }

        auto newRoot = make_unique<TreeNode>(*values[0]);
        queue<TreeNode*> nodes;
        nodes.push(newRoot.get());

        size_t index = 1;

        while (!nodes.empty() && index < values.size()) {
            TreeNode* current = nodes.front();
            nodes.pop();

            if (index < values.size()) {
                if (values[index].has_value()) {
                    current->left = make_unique<TreeNode>(
                        *values[index]
                    );
                    nodes.push(current->left.get());
                }
                ++index;
            }

            if (index < values.size()) {
                if (values[index].has_value()) {
                    current->right = make_unique<TreeNode>(
                        *values[index]
                    );
                    nodes.push(current->right.get());
                }
                ++index;
            }
        }

        if (index < values.size()) {
            throw invalid_argument(
                "Invalid level-order representation."
            );
        }

        return BinaryTree(std::move(newRoot));
    }

    /*
     * Standard BFS traversal.
     * Capturing queue.size() before processing a level prevents
     * newly discovered children from entering the current level.
     */
    vector<vector<int>> levelOrder() const {
        vector<vector<int>> result;

        if (!root) {
            return result;
        }

        queue<const TreeNode*> nodes;
        nodes.push(root.get());

        while (!nodes.empty()) {
            const size_t levelSize = nodes.size();
            vector<int> level;
            level.reserve(levelSize);

            for (size_t i = 0; i < levelSize; ++i) {
                const TreeNode* current = nodes.front();
                nodes.pop();

                level.push_back(current->value);

                if (current->left) {
                    nodes.push(current->left.get());
                }

                if (current->right) {
                    nodes.push(current->right.get());
                }
            }

            result.push_back(std::move(level));
        }

        return result;
    }

    vector<int> flatTraversal() const {
        vector<int> result;

        if (!root) {
            return result;
        }

        queue<const TreeNode*> nodes;
        nodes.push(root.get());

        while (!nodes.empty()) {
            const TreeNode* current = nodes.front();
            nodes.pop();

            result.push_back(current->value);

            if (current->left) nodes.push(current->left.get());
            if (current->right) nodes.push(current->right.get());
        }

        return result;
    }

    vector<double> levelAverages() const {
        vector<double> result;
        const auto levels = levelOrder();

        for (const auto& level : levels) {
            long double sum = 0;

            for (int value : level) {
                sum += value;
            }

            result.push_back(
                static_cast<double>(sum / level.size())
            );
        }

        return result;
    }

    vector<vector<int>> zigzagTraversal() const {
        vector<vector<int>> result;

        if (!root) {
            return result;
        }

        queue<const TreeNode*> nodes;
        nodes.push(root.get());

        bool leftToRight = true;

        while (!nodes.empty()) {
            size_t levelSize = nodes.size();
            vector<int> level(levelSize);

            for (size_t i = 0; i < levelSize; ++i) {
                const TreeNode* current = nodes.front();
                nodes.pop();

                const size_t position = leftToRight
                    ? i
                    : levelSize - 1 - i;

                level[position] = current->value;

                if (current->left) nodes.push(current->left.get());
                if (current->right) nodes.push(current->right.get());
            }

            result.push_back(std::move(level));
            leftToRight = !leftToRight;
        }

        return result;
    }

    vector<LevelReport> statistics() const {
        vector<LevelReport> result;
        const auto levels = levelOrder();

        for (size_t depth = 0; depth < levels.size(); ++depth) {
            const auto& level = levels[depth];

            long long sum = 0;
            int minimum = numeric_limits<int>::max();
            int maximum = numeric_limits<int>::min();

            for (int value : level) {
                sum += value;
                minimum = min(minimum, value);
                maximum = max(maximum, value);
            }

            result.push_back({
                depth,
                level.size(),
                sum,
                minimum,
                maximum,
                static_cast<double>(sum) / level.size()
            });
        }

        return result;
    }

    vector<int> rightSideView() const {
        vector<int> result;

        if (!root) return result;

        queue<const TreeNode*> nodes;
        nodes.push(root.get());

        while (!nodes.empty()) {
            size_t levelSize = nodes.size();

            for (size_t i = 0; i < levelSize; ++i) {
                const TreeNode* current = nodes.front();
                nodes.pop();

                if (i == levelSize - 1) {
                    result.push_back(current->value);
                }

                if (current->left) nodes.push(current->left.get());
                if (current->right) nodes.push(current->right.get());
            }
        }

        return result;
    }

    optional<int> find(int target) const {
        if (!root) return nullopt;

        queue<const TreeNode*> nodes;
        nodes.push(root.get());

        while (!nodes.empty()) {
            const TreeNode* current = nodes.front();
            nodes.pop();

            if (current->value == target) {
                return current->value;
            }

            if (current->left) nodes.push(current->left.get());
            if (current->right) nodes.push(current->right.get());
        }

        return nullopt;
    }

    size_t nodeCount() const {
        size_t count = 0;

        if (!root) return count;

        queue<const TreeNode*> nodes;
        nodes.push(root.get());

        while (!nodes.empty()) {
            const TreeNode* current = nodes.front();
            nodes.pop();
            ++count;

            if (current->left) nodes.push(current->left.get());
            if (current->right) nodes.push(current->right.get());
        }

        return count;
    }

    size_t maximumDepth() const {
        return levelOrder().size();
    }

    void display(const string& title,
                 const vector<vector<int>>& levels) const {
        cout << "\n" << title << "\n";

        for (size_t i = 0; i < levels.size(); ++i) {
            cout << "Level " << i << ": ";

            for (int value : levels[i]) {
                cout << value << " ";
            }

            cout << "\n";
        }
    }
};

void runTests() {
    BinaryTree tree = BinaryTree::fromLevelOrder({
        1, 2, 3, 4, 5, 6, 7
    });

    const vector<vector<int>> expected = {
        {1},
        {2, 3},
        {4, 5, 6, 7}
    };

    if (tree.levelOrder() != expected) {
        throw runtime_error("Level-order test failed.");
    }

    const vector<vector<int>> expectedZigzag = {
        {1},
        {3, 2},
        {4, 5, 6, 7}
    };

    if (tree.zigzagTraversal() != expectedZigzag) {
        throw runtime_error("Zigzag test failed.");
    }

    const auto averages = tree.levelAverages();

    if (averages.size() != 3 ||
        abs(averages[1] - 2.5) > 1e-9 ||
        abs(averages[2] - 5.5) > 1e-9) {
        throw runtime_error("Average test failed.");
    }

    if (tree.nodeCount() != 7) {
        throw runtime_error("Node-count test failed.");
    }

    if (tree.maximumDepth() != 3) {
        throw runtime_error("Depth test failed.");
    }

    if (!tree.find(5).has_value() || tree.find(100).has_value()) {
        throw runtime_error("Search test failed.");
    }

    BinaryTree empty;

    if (!empty.levelOrder().empty()) {
        throw runtime_error("Empty-tree test failed.");
    }

    BinaryTree sparse = BinaryTree::fromLevelOrder({
        1, nullopt, 2, 3
    });

    if (sparse.levelOrder() != vector<vector<int>>{
        {1}, {2}, {3}
    }) {
        throw runtime_error("Sparse-tree test failed.");
    }

    bool invalidRejected = false;

    try {
        BinaryTree::fromLevelOrder({
            nullopt, 10
        });
    } catch (const invalid_argument&) {
        invalidRejected = true;
    }

    if (!invalidRejected) {
        throw runtime_error("Invalid tree was accepted.");
    }

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        BinaryTree tree = BinaryTree::fromLevelOrder({
            10, 20, 30, 40, 50, 60, 70,
            80, 90
        });

        cout << "BFS AND LEVEL-ORDER TRAVERSAL\n";
        cout << "====================================\n";

        tree.display("Level-order traversal", tree.levelOrder());

        tree.display("Zigzag traversal", tree.zigzagTraversal());

        cout << "\nLevel averages:\n";
        const auto averages = tree.levelAverages();

        for (size_t i = 0; i < averages.size(); ++i) {
            cout << "Level " << i << ": "
                 << fixed << setprecision(2)
                 << averages[i] << "\n";
        }

        cout << "\nLevel statistics:\n";

        for (const auto& report : tree.statistics()) {
            cout << "Depth=" << report.depth
                 << " Nodes=" << report.nodeCount
                 << " Sum=" << report.sum
                 << " Min=" << report.minimum
                 << " Max=" << report.maximum
                 << " Average=" << fixed << setprecision(2)
                 << report.average << "\n";
        }

        cout << "\nRight-side view: ";

        for (int value : tree.rightSideView()) {
            cout << value << " ";
        }

        cout << "\nTotal nodes: " << tree.nodeCount();
        cout << "\nMaximum depth: " << tree.maximumDepth();

        cout << "\n\nSearching for 60: ";

        const auto found = tree.find(60);

        if (found) {
            cout << "Found " << *found;
        } else {
            cout << "Not found";
        }

        cout << "\n\n";
        runTests();

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
