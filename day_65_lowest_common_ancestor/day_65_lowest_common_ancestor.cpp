#include <iostream>
#include <vector>
#include <memory>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <stdexcept>
#include <algorithm>
#include <string>
#include <limits>
#include <cmath>

using namespace std;

struct TreeNode {
    int id;
    string department;
    TreeNode* left = nullptr;
    TreeNode* right = nullptr;
    TreeNode* parent = nullptr;

    TreeNode(int identifier, string name)
        : id(identifier), department(std::move(name)) {}
};

class BinaryTree {
private:
    vector<unique_ptr<TreeNode>> storage;
    unordered_map<int, TreeNode*> nodes;
    TreeNode* root = nullptr;

public:
    TreeNode* createNode(int id, const string& department) {
        if (nodes.count(id)) {
            throw invalid_argument("Duplicate employee ID.");
        }

        storage.push_back(make_unique<TreeNode>(id, department));
        TreeNode* node = storage.back().get();
        nodes[id] = node;

        if (!root) root = node;

        return node;
    }

    TreeNode* getNode(int id) const {
        auto it = nodes.find(id);
        return it == nodes.end() ? nullptr : it->second;
    }

    TreeNode* getRoot() const {
        return root;
    }

    void setRoot(TreeNode* node) {
        if (!node || !nodes.count(node->id)) {
            throw invalid_argument("Invalid root node.");
        }

        if (node->parent) {
            throw invalid_argument("Root cannot have a parent.");
        }

        root = node;
    }

    void attach(int parentId, int childId, bool leftSide) {
        TreeNode* parent = getNode(parentId);
        TreeNode* child = getNode(childId);

        if (!parent || !child) {
            throw invalid_argument("Unknown employee ID.");
        }

        if (parent == child || child->parent) {
            throw invalid_argument("Invalid tree attachment.");
        }

        TreeNode* current = parent;

        while (current) {
            if (current == child) {
                throw invalid_argument("Attachment creates a cycle.");
            }
            current = current->parent;
        }

        TreeNode*& position = leftSide ? parent->left : parent->right;

        if (position) {
            throw invalid_argument("Child position is occupied.");
        }

        position = child;
        child->parent = parent;
    }

    void validate() const {
        if (!root) {
            if (!nodes.empty()) {
                throw logic_error("Nonempty tree has no root.");
            }
            return;
        }

        unordered_set<TreeNode*> visited;
        vector<pair<TreeNode*, TreeNode*>> stack;
        stack.push_back({root, nullptr});

        while (!stack.empty()) {
            auto [node, expectedParent] = stack.back();
            stack.pop_back();

            if (!visited.insert(node).second) {
                throw logic_error("Cycle or shared child detected.");
            }

            if (node->parent != expectedParent) {
                throw logic_error("Parent pointer inconsistency.");
            }

            if (node->left) {
                stack.push_back({node->left, node});
            }

            if (node->right) {
                stack.push_back({node->right, node});
            }
        }

        if (visited.size() != nodes.size()) {
            throw logic_error("Tree contains unreachable nodes.");
        }
    }

    size_t size() const {
        return nodes.size();
    }
};

class LCAEngine {
private:
    const BinaryTree& tree;

    bool contains(TreeNode* target) const {
        if (!target) return false;

        vector<TreeNode*> stack{tree.getRoot()};

        while (!stack.empty()) {
            TreeNode* node = stack.back();
            stack.pop_back();

            if (node == target) return true;

            if (node->left) stack.push_back(node->left);
            if (node->right) stack.push_back(node->right);
        }

        return false;
    }

public:
    explicit LCAEngine(const BinaryTree& inputTree) : tree(inputTree) {
        tree.validate();
    }

    TreeNode* recursiveLCA(
        TreeNode* first,
        TreeNode* second
    ) const {
        if (!first || !second ||
            !contains(first) || !contains(second)) {
            return nullptr;
        }

        function<TreeNode*(TreeNode*)> search =
            [&](TreeNode* node) -> TreeNode* {
                if (!node || node == first || node == second) {
                    return node;
                }

                TreeNode* left = search(node->left);
                TreeNode* right = search(node->right);

                if (left && right) return node;

                return left ? left : right;
            };

        return search(tree.getRoot());
    }

    TreeNode* parentBasedLCA(
        TreeNode* first,
        TreeNode* second
    ) const {
        if (!first || !second ||
            !contains(first) || !contains(second)) {
            return nullptr;
        }

        unordered_set<TreeNode*> ancestors;
        TreeNode* current = first;

        while (current) {
            if (!ancestors.insert(current).second) {
                throw logic_error("Cycle in parent chain.");
            }

            current = current->parent;
        }

        current = second;

        while (current) {
            if (ancestors.count(current)) return current;
            current = current->parent;
        }

        return nullptr;
    }

    TreeNode* iterativeLCA(
        TreeNode* first,
        TreeNode* second
    ) const {
        if (!first || !second) return nullptr;

        unordered_map<TreeNode*, TreeNode*> parentMap;
        queue<TreeNode*> pending;

        TreeNode* root = tree.getRoot();
        if (!root) return nullptr;

        pending.push(root);
        parentMap[root] = nullptr;

        while (!pending.empty()) {
            TreeNode* node = pending.front();
            pending.pop();

            if (node->left) {
                parentMap[node->left] = node;
                pending.push(node->left);
            }

            if (node->right) {
                parentMap[node->right] = node;
                pending.push(node->right);
            }
        }

        if (!parentMap.count(first) || !parentMap.count(second)) {
            return nullptr;
        }

        unordered_set<TreeNode*> ancestors;
        TreeNode* current = first;

        while (current) {
            ancestors.insert(current);
            current = parentMap[current];
        }

        current = second;

        while (current) {
            if (ancestors.count(current)) return current;
            current = parentMap[current];
        }

        return nullptr;
    }
};

/**
 * Governance hierarchy index using binary lifting.
 * Suitable for repeated ancestor queries on a static tree.
 */
class BinaryLiftingIndex {
private:
    vector<vector<int>> up;
    vector<int> depth;
    unordered_map<int, int> position;
    int levels;

public:
    explicit BinaryLiftingIndex(const BinaryTree& tree) {
        tree.validate();

        int n = static_cast<int>(tree.size());

        if (n == 0) {
            throw invalid_argument("Cannot index an empty tree.");
        }

        levels = 1;

        while ((1LL << levels) <= n) {
            ++levels;
        }

        up.assign(n, vector<int>(levels, -1));
        depth.assign(n, 0);

        vector<TreeNode*> nodes;
        queue<TreeNode*> pending;
        pending.push(tree.getRoot());

        while (!pending.empty()) {
            TreeNode* node = pending.front();
            pending.pop();

            position[node->id] = static_cast<int>(nodes.size());
            nodes.push_back(node);

            if (node->left) pending.push(node->left);
            if (node->right) pending.push(node->right);
        }

        for (TreeNode* node : nodes) {
            int current = position[node->id];

            if (node->parent) {
                int parent = position[node->parent->id];
                up[current][0] = parent;
                depth[current] = depth[parent] + 1;
            }
        }

        for (int k = 1; k < levels; ++k) {
            for (int v = 0; v < n; ++v) {
                int middle = up[v][k - 1];

                if (middle != -1) {
                    up[v][k] = up[middle][k - 1];
                }
            }
        }
    }

    int query(int firstId, int secondId) const {
        if (!position.count(firstId) || !position.count(secondId)) {
            return -1;
        }

        int a = position.at(firstId);
        int b = position.at(secondId);

        if (depth[a] < depth[b]) swap(a, b);

        int difference = depth[a] - depth[b];

        for (int k = 0; k < levels; ++k) {
            if (difference & (1 << k)) {
                a = up[a][k];
            }
        }

        if (a == b) return a;

        for (int k = levels - 1; k >= 0; --k) {
            if (up[a][k] != up[b][k]) {
                a = up[a][k];
                b = up[b][k];
            }
        }

        return up[a][0];
    }
};

void printResult(
    const string& method,
    TreeNode* result,
    int first,
    int second
) {
    cout << method << ": LCA(" << first << ", " << second << ") = ";

    if (result) {
        cout << result->id << " [" << result->department << "]";
    } else {
        cout << "Not found";
    }

    cout << '\n';
}

void runTests(const BinaryTree& tree, const LCAEngine& engine) {
    const vector<tuple<int, int, int>> cases = {
        {4, 5, 2},
        {4, 6, 1},
        {8, 9, 5},
        {8, 10, 1},
        {2, 8, 2},
        {7, 10, 7}
    };

    for (const auto& [a, b, expected] : cases) {
        TreeNode* first = tree.getNode(a);
        TreeNode* second = tree.getNode(b);

        TreeNode* recursive = engine.recursiveLCA(first, second);
        TreeNode* parent = engine.parentBasedLCA(first, second);
        TreeNode* iterative = engine.iterativeLCA(first, second);

        if (!recursive || recursive->id != expected ||
            !parent || parent->id != expected ||
            !iterative || iterative->id != expected) {
            throw runtime_error("LCA test failed.");
        }
    }

    if (engine.recursiveLCA(
        tree.getNode(4), nullptr
    ) != nullptr) {
        throw runtime_error("Null-target test failed.");
    }

    cout << "All C++17 LCA tests passed.\n";
}

int main() {
    try {
        BinaryTree organization;

        organization.createNode(1, "Chief Executive Officer");
        organization.createNode(2, "Technology Division");
        organization.createNode(3, "Operations Division");
        organization.createNode(4, "Platform Engineering");
        organization.createNode(5, "Security Engineering");
        organization.createNode(6, "Operations Research");
        organization.createNode(7, "Infrastructure");
        organization.createNode(8, "Application Security");
        organization.createNode(9, "Cloud Security");
        organization.createNode(10, "Network Engineering");

        organization.attach(1, 2, true);
        organization.attach(1, 3, false);
        organization.attach(2, 4, true);
        organization.attach(2, 5, false);
        organization.attach(3, 6, true);
        organization.attach(3, 7, false);
        organization.attach(5, 8, true);
        organization.attach(5, 9, false);
        organization.attach(7, 10, false);

        organization.validate();

        LCAEngine engine(organization);
        BinaryLiftingIndex index(organization);

        runTests(organization, engine);

        cout << "\nOrganization hierarchy queries\n";
        cout << "--------------------------------\n";

        const vector<pair<int, int>> requests = {
            {4, 5},
            {4, 6},
            {8, 9},
            {8, 10},
            {7, 10}
        };

        for (const auto& [first, second] : requests) {
            TreeNode* a = organization.getNode(first);
            TreeNode* b = organization.getNode(second);

            printResult(
                "Recursive",
                engine.recursiveLCA(a, b),
                first,
                second
            );

            printResult(
                "Parent-based",
                engine.parentBasedLCA(a, b),
                first,
                second
            );

            int indexed = index.query(first, second);

            cout << "Binary lifting: LCA("
                 << first << ", " << second << ") = "
                 << indexed << "\n\n";
        }

        cout << "Missing node query: "
             << index.query(4, 999) << '\n';

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
