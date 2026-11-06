#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
#include <queue>
#include <stdexcept>
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

    TreeNode(int value,
             unique_ptr<TreeNode> left,
             unique_ptr<TreeNode> right)
        : value(value),
          left(move(left)),
          right(move(right)) {}
};

class TreeAssessment {
private:
    unique_ptr<TreeNode> root;

    static int heightRecursive(const TreeNode* node) {
        if (!node) return -1;

        return 1 + max(
            heightRecursive(node->left.get()),
            heightRecursive(node->right.get())
        );
    }

    static int diameterRecursive(
        const TreeNode* node,
        int& diameter
    ) {
        if (!node) return -1;

        int left = diameterRecursive(node->left.get(), diameter);
        int right = diameterRecursive(node->right.get(), diameter);

        diameter = max(diameter, left + right + 2);

        return max(left, right) + 1;
    }

    static int balancedHeight(const TreeNode* node) {
        if (!node) return 0;

        int left = balancedHeight(node->left.get());
        if (left == -1) return -1;

        int right = balancedHeight(node->right.get());
        if (right == -1) return -1;

        if (abs(left - right) > 1) return -1;

        return max(left, right) + 1;
    }

    static bool pathSumRecursive(
        const TreeNode* node,
        long long remaining
    ) {
        if (!node) return false;

        remaining -= node->value;

        if (!node->left && !node->right) {
            return remaining == 0;
        }

        return pathSumRecursive(node->left.get(), remaining)
            || pathSumRecursive(node->right.get(), remaining);
    }

    static const TreeNode* lcaRecursive(
        const TreeNode* node,
        int first,
        int second
    ) {
        if (!node) return nullptr;

        if (node->value == first || node->value == second) {
            return node;
        }

        const TreeNode* left = lcaRecursive(
            node->left.get(), first, second
        );

        const TreeNode* right = lcaRecursive(
            node->right.get(), first, second
        );

        if (left && right) return node;

        return left ? left : right;
    }

    static bool contains(const TreeNode* node, int value) {
        if (!node) return false;

        return node->value == value
            || contains(node->left.get(), value)
            || contains(node->right.get(), value);
    }

    static void collectPaths(
        const TreeNode* node,
        long long remaining,
        vector<int>& path,
        vector<vector<int>>& result
    ) {
        if (!node) return;

        path.push_back(node->value);
        remaining -= node->value;

        if (!node->left && !node->right) {
            if (remaining == 0) result.push_back(path);
        } else {
            collectPaths(node->left.get(), remaining, path, result);
            collectPaths(node->right.get(), remaining, path, result);
        }

        path.pop_back();
    }

    static long long maximumPathGain(
        const TreeNode* node,
        long long& maximum
    ) {
        if (!node) return 0;

        long long left = max(
            0LL,
            maximumPathGain(node->left.get(), maximum)
        );

        long long right = max(
            0LL,
            maximumPathGain(node->right.get(), maximum)
        );

        long long throughNode = node->value + left + right;

        maximum = max(maximum, throughNode);

        return node->value + max(left, right);
    }

    static void validateStructure(const TreeNode* root) {
        if (!root) return;

        unordered_set<const TreeNode*> visited;
        vector<const TreeNode*> stack{root};

        while (!stack.empty()) {
            const TreeNode* node = stack.back();
            stack.pop_back();

            if (!visited.insert(node).second) {
                throw invalid_argument(
                    "Cycle or shared child detected."
                );
            }

            if (node->right) stack.push_back(node->right.get());
            if (node->left) stack.push_back(node->left.get());
        }
    }

public:
    explicit TreeAssessment(unique_ptr<TreeNode> root)
        : root(move(root)) {
        validateStructure(this->root.get());
    }

    const TreeNode* getRoot() const {
        return root.get();
    }

    vector<int> preorder() const {
        vector<int> result;
        vector<const TreeNode*> stack;

        if (root) stack.push_back(root.get());

        while (!stack.empty()) {
            const TreeNode* node = stack.back();
            stack.pop_back();

            result.push_back(node->value);

            if (node->right) stack.push_back(node->right.get());
            if (node->left) stack.push_back(node->left.get());
        }

        return result;
    }

    vector<int> inorder() const {
        vector<int> result;
        vector<const TreeNode*> stack;
        const TreeNode* current = root.get();

        while (current || !stack.empty()) {
            while (current) {
                stack.push_back(current);
                current = current->left.get();
            }

            current = stack.back();
            stack.pop_back();

            result.push_back(current->value);
            current = current->right.get();
        }

        return result;
    }

    vector<int> postorder() const {
        vector<int> result;
        vector<pair<const TreeNode*, bool>> stack;

        if (root) stack.push_back({root.get(), false});

        while (!stack.empty()) {
            auto [node, visited] = stack.back();
            stack.pop_back();

            if (visited) {
                result.push_back(node->value);
            } else {
                stack.push_back({node, true});

                if (node->right) {
                    stack.push_back({node->right.get(), false});
                }

                if (node->left) {
                    stack.push_back({node->left.get(), false});
                }
            }
        }

        return result;
    }

    vector<vector<int>> levelOrder() const {
        vector<vector<int>> result;

        if (!root) return result;

        queue<const TreeNode*> pending;
        pending.push(root.get());

        while (!pending.empty()) {
            size_t count = pending.size();
            vector<int> level;

            while (count--) {
                const TreeNode* node = pending.front();
                pending.pop();

                level.push_back(node->value);

                if (node->left) pending.push(node->left.get());
                if (node->right) pending.push(node->right.get());
            }

            result.push_back(move(level));
        }

        return result;
    }

    vector<vector<int>> zigzagLevelOrder() const {
        auto result = levelOrder();

        for (size_t i = 1; i < result.size(); i += 2) {
            reverse(result[i].begin(), result[i].end());
        }

        return result;
    }

    int height() const {
        return heightRecursive(root.get());
    }

    int diameter() const {
        int result = 0;
        diameterRecursive(root.get(), result);
        return result;
    }

    bool isBalanced() const {
        return balancedHeight(root.get()) != -1;
    }

    bool hasPathSum(long long target) const {
        return pathSumRecursive(root.get(), target);
    }

    vector<vector<int>> allPathSums(long long target) const {
        vector<vector<int>> result;
        vector<int> path;

        collectPaths(root.get(), target, path, result);

        return result;
    }

    const TreeNode* lowestCommonAncestor(
        int first,
        int second
    ) const {
        if (!contains(root.get(), first)
            || !contains(root.get(), second)) {
            return nullptr;
        }

        return lcaRecursive(root.get(), first, second);
    }

    vector<int> rightSideView() const {
        vector<int> result;
        auto levels = levelOrder();

        for (const auto& level : levels) {
            result.push_back(level.back());
        }

        return result;
    }

    int minimumDepth() const {
        if (!root) return 0;

        queue<pair<const TreeNode*, int>> pending;
        pending.push({root.get(), 1});

        while (!pending.empty()) {
            auto [node, depth] = pending.front();
            pending.pop();

            if (!node->left && !node->right) return depth;

            if (node->left) {
                pending.push({node->left.get(), depth + 1});
            }

            if (node->right) {
                pending.push({node->right.get(), depth + 1});
            }
        }

        return 0;
    }

    size_t countNodes() const {
        return preorder().size();
    }

    long long maximumPathSum() const {
        if (!root) {
            throw logic_error("Empty tree has no non-empty path.");
        }

        long long maximum = numeric_limits<long long>::lowest();

        maximumPathGain(root.get(), maximum);

        return maximum;
    }
};

unique_ptr<TreeNode> sampleTree() {
    auto root = make_unique<TreeNode>(10);

    root->left = make_unique<TreeNode>(5);
    root->right = make_unique<TreeNode>(15);

    root->left->left = make_unique<TreeNode>(3);
    root->left->right = make_unique<TreeNode>(7);

    root->left->left->left = make_unique<TreeNode>(1);
    root->left->left->right = make_unique<TreeNode>(4);

    root->left->right->right = make_unique<TreeNode>(8);
    root->right->right = make_unique<TreeNode>(20);

    return root;
}

void printVector(const vector<int>& values) {
    cout << "[";

    for (size_t i = 0; i < values.size(); ++i) {
        if (i) cout << ", ";
        cout << values[i];
    }

    cout << "]\n";
}

void printLevels(const vector<vector<int>>& levels) {
    for (const auto& level : levels) {
        printVector(level);
    }
}

int main() {
    try {
        TreeAssessment tree(sampleTree());

        cout << "TREE ASSESSMENT\n";
        cout << "============================\n";

        cout << "Preorder: ";
        printVector(tree.preorder());

        cout << "Inorder: ";
        printVector(tree.inorder());

        cout << "Postorder: ";
        printVector(tree.postorder());

        cout << "Level order:\n";
        printLevels(tree.levelOrder());

        cout << "Zigzag:\n";
        printLevels(tree.zigzagLevelOrder());

        cout << "Height: " << tree.height() << '\n';
        cout << "Diameter: " << tree.diameter() << '\n';
        cout << "Balanced: " << boolalpha
             << tree.isBalanced() << '\n';

        cout << "Has path sum 19: "
             << tree.hasPathSum(19) << '\n';

        cout << "Matching paths:\n";

        for (const auto& path : tree.allPathSums(19)) {
            printVector(path);
        }

        const TreeNode* ancestor =
            tree.lowestCommonAncestor(1, 8);

        cout << "LCA(1, 8): "
             << (ancestor ? ancestor->value : -1) << '\n';

        cout << "Right view: ";
        printVector(tree.rightSideView());

        cout << "Minimum depth: "
             << tree.minimumDepth() << '\n';

        cout << "Node count: "
             << tree.countNodes() << '\n';

        cout << "Maximum path sum: "
             << tree.maximumPathSum() << '\n';

        assert(tree.height() == 3);
        assert(tree.diameter() == 6);
        assert(tree.isBalanced());
        assert(tree.hasPathSum(19));
        assert(!tree.hasPathSum(100));
        assert(ancestor && ancestor->value == 5);
        assert(tree.maximumPathSum() == 54);

        TreeAssessment empty(nullptr);

        assert(empty.height() == -1);
        assert(empty.diameter() == 0);
        assert(empty.isBalanced());
        assert(empty.minimumDepth() == 0);

        TreeAssessment negative(
            make_unique<TreeNode>(-5)
        );

        assert(negative.maximumPathSum() == -5);
        assert(negative.hasPathSum(-5));

        TreeAssessment unbalanced(
            make_unique<TreeNode>(
                1,
                make_unique<TreeNode>(
                    2,
                    make_unique<TreeNode>(
                        3,
                        make_unique<TreeNode>(4),
                        nullptr
                    ),
                    nullptr
                ),
                nullptr
            )
        );

        assert(!unbalanced.isBalanced());

        cout << "\nAll C++17 tree tests passed.\n";

    } catch (const exception& error) {
        cerr << "Tree assessment error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
