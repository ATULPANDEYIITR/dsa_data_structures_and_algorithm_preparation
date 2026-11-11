#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using namespace std;

enum class Operation {
    Search,
    Insert,
    Delete,
    Validate,
    LCA,
    Minimum,
    Maximum,
    Successor,
    Predecessor
};

struct Node {
    int key;
    unique_ptr<Node> left;
    unique_ptr<Node> right;

    explicit Node(int value) : key(value) {}
};

struct AssessmentResult {
    Operation operation;
    bool success;
    optional<int> value;
    string message;
};

class BinarySearchTree {
private:
    unique_ptr<Node> root;
    size_t nodeCount = 0;

    static bool validateNode(
        const Node* node,
        optional<long long> lower,
        optional<long long> upper,
        unordered_set<const Node*>& visited
    ) {
        if (node == nullptr) return true;

        if (!visited.insert(node).second) return false;

        if (lower && node->key <= *lower) return false;
        if (upper && node->key >= *upper) return false;

        return validateNode(
            node->left.get(), lower, node->key, visited
        ) && validateNode(
            node->right.get(), node->key, upper, visited
        );
    }

    static void inorderTraversal(
        const Node* node,
        vector<int>& result
    ) {
        if (!node) return;

        inorderTraversal(node->left.get(), result);
        result.push_back(node->key);
        inorderTraversal(node->right.get(), result);
    }

    static void preorderTraversal(
        const Node* node,
        vector<int>& result
    ) {
        if (!node) return;

        result.push_back(node->key);
        preorderTraversal(node->left.get(), result);
        preorderTraversal(node->right.get(), result);
    }

    static void postorderTraversal(
        const Node* node,
        vector<int>& result
    ) {
        if (!node) return;

        postorderTraversal(node->left.get(), result);
        postorderTraversal(node->right.get(), result);
        result.push_back(node->key);
    }

public:
    BinarySearchTree() = default;

    BinarySearchTree(const BinarySearchTree&) = delete;
    BinarySearchTree& operator=(const BinarySearchTree&) = delete;

    size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return root == nullptr;
    }

    bool insert(int key) {
        unique_ptr<Node>* current = &root;

        while (*current) {
            if (key == (*current)->key) return false;

            current = key < (*current)->key
                ? &(*current)->left
                : &(*current)->right;
        }

        *current = make_unique<Node>(key);
        ++nodeCount;

        return true;
    }

    bool search(int key) const {
        const Node* current = root.get();

        while (current) {
            if (key == current->key) return true;

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    optional<int> minimum() const {
        const Node* current = root.get();

        if (!current) return nullopt;

        while (current->left) {
            current = current->left.get();
        }

        return current->key;
    }

    optional<int> maximum() const {
        const Node* current = root.get();

        if (!current) return nullopt;

        while (current->right) {
            current = current->right.get();
        }

        return current->key;
    }

    bool remove(int key) {
        unique_ptr<Node>* current = &root;

        while (*current && (*current)->key != key) {
            current = key < (*current)->key
                ? &(*current)->left
                : &(*current)->right;
        }

        if (!*current) return false;

        Node* target = current->get();

        if (target->left && target->right) {
            unique_ptr<Node>* successor = &target->right;

            while ((*successor)->left) {
                successor = &(*successor)->left;
            }

            // Copy the successor key, then remove its original node.
            target->key = (*successor)->key;
            current = successor;
        }

        // Zero-child and one-child cases.
        unique_ptr<Node> oldNode = move(*current);

        if (oldNode->left) {
            *current = move(oldNode->left);
        } else {
            *current = move(oldNode->right);
        }

        --nodeCount;
        return true;
    }

    bool validate() const {
        unordered_set<const Node*> visited;

        if (!validateNode(
            root.get(), nullopt, nullopt, visited
        )) {
            return false;
        }

        return visited.size() == nodeCount;
    }

    optional<int> lowestCommonAncestor(
        int first,
        int second
    ) const {
        if (!search(first) || !search(second)) {
            return nullopt;
        }

        const Node* current = root.get();

        while (current) {
            if (first < current->key && second < current->key) {
                current = current->left.get();
            } else if (
                first > current->key && second > current->key
            ) {
                current = current->right.get();
            } else {
                return current->key;
            }
        }

        return nullopt;
    }

    optional<int> successor(int key) const {
        const Node* current = root.get();
        optional<int> candidate;

        while (current) {
            if (key < current->key) {
                candidate = current->key;
                current = current->left.get();
            } else {
                current = current->right.get();
            }
        }

        return candidate;
    }

    optional<int> predecessor(int key) const {
        const Node* current = root.get();
        optional<int> candidate;

        while (current) {
            if (key > current->key) {
                candidate = current->key;
                current = current->right.get();
            } else {
                current = current->left.get();
            }
        }

        return candidate;
    }

    vector<int> inorder() const {
        vector<int> result;
        inorderTraversal(root.get(), result);
        return result;
    }

    vector<int> preorder() const {
        vector<int> result;
        preorderTraversal(root.get(), result);
        return result;
    }

    vector<int> postorder() const {
        vector<int> result;
        postorderTraversal(root.get(), result);
        return result;
    }

    vector<int> levelOrder() const {
        vector<int> result;

        if (!root) return result;

        queue<const Node*> pending;
        pending.push(root.get());

        while (!pending.empty()) {
            const Node* node = pending.front();
            pending.pop();

            result.push_back(node->key);

            if (node->left) pending.push(node->left.get());
            if (node->right) pending.push(node->right.get());
        }

        return result;
    }

    vector<int> rangeQuery(int low, int high) const {
        if (low > high) {
            throw invalid_argument("Invalid query range.");
        }

        vector<int> result;
        vector<const Node*> stack;
        const Node* current = root.get();

        while (current || !stack.empty()) {
            while (current) {
                if (current->key >= low) {
                    stack.push_back(current);
                    current = current->left.get();
                } else {
                    current = current->right.get();
                }
            }

            if (stack.empty()) break;

            current = stack.back();
            stack.pop_back();

            if (current->key > high) break;

            result.push_back(current->key);
            current = current->right.get();
        }

        return result;
    }

    int height() const {
        if (!root) return -1;

        queue<pair<const Node*, int>> pending;
        pending.push({root.get(), 0});

        int maximumDepth = 0;

        while (!pending.empty()) {
            auto [node, depth] = pending.front();
            pending.pop();

            maximumDepth = max(maximumDepth, depth);

            if (node->left) {
                pending.push({node->left.get(), depth + 1});
            }

            if (node->right) {
                pending.push({node->right.get(), depth + 1});
            }
        }

        return maximumDepth;
    }

    bool isBalanced() const {
        function<int(const Node*)> check =
            [&](const Node* node) -> int {
                if (!node) return 0;

                int left = check(node->left.get());
                if (left == -1) return -1;

                int right = check(node->right.get());
                if (right == -1) return -1;

                if (abs(left - right) > 1) return -1;

                return 1 + max(left, right);
            };

        return check(root.get()) != -1;
    }
};

class BSTAssessmentEngine {
private:
    BinarySearchTree tree;

public:
    bool add(int key) {
        return tree.insert(key);
    }

    bool find(int key) const {
        return tree.search(key);
    }

    bool erase(int key) {
        return tree.remove(key);
    }

    AssessmentResult evaluate(Operation operation, int key = 0) const {
        switch (operation) {
            case Operation::Search:
                return {
                    operation,
                    tree.search(key),
                    tree.search(key) ? optional<int>(key) : nullopt,
                    "Search evaluated"
                };

            case Operation::Minimum:
                return {
                    operation,
                    tree.minimum().has_value(),
                    tree.minimum(),
                    "Minimum evaluated"
                };

            case Operation::Maximum:
                return {
                    operation,
                    tree.maximum().has_value(),
                    tree.maximum(),
                    "Maximum evaluated"
                };

            case Operation::Successor:
                return {
                    operation,
                    tree.successor(key).has_value(),
                    tree.successor(key),
                    "Successor evaluated"
                };

            case Operation::Predecessor:
                return {
                    operation,
                    tree.predecessor(key).has_value(),
                    tree.predecessor(key),
                    "Predecessor evaluated"
                };

            case Operation::Validate:
                return {
                    operation,
                    tree.validate(),
                    nullopt,
                    "BST invariant evaluated"
                };

            default:
                return {
                    operation,
                    false,
                    nullopt,
                    "Operation requires additional arguments"
                };
        }
    }

    optional<int> lca(int first, int second) const {
        return tree.lowestCommonAncestor(first, second);
    }

    void report() const {
        cout << "Size: " << tree.size() << '\n';
        cout << "Valid: " << boolalpha << tree.validate() << '\n';
        cout << "Height: " << tree.height() << '\n';
        cout << "Balanced: " << tree.isBalanced() << '\n';

        cout << "Inorder: ";

        for (int value : tree.inorder()) {
            cout << value << ' ';
        }

        cout << '\n';
    }

    const BinarySearchTree& getTree() const {
        return tree;
    }
};

void runTests() {
    BSTAssessmentEngine engine;

    vector<int> values = {
        50, 30, 70, 20, 40, 60, 80
    };

    for (int value : values) {
        assert(engine.add(value));
    }

    assert(!engine.add(50));
    assert(engine.find(40));
    assert(!engine.find(999));

    const auto& tree = engine.getTree();

    assert(tree.minimum() == 20);
    assert(tree.maximum() == 80);

    assert(engine.lca(20, 40) == 30);
    assert(engine.lca(20, 80) == 50);
    assert(!engine.lca(20, 999).has_value());

    assert(tree.successor(40) == 50);
    assert(tree.predecessor(60) == 50);
    assert(!tree.successor(80).has_value());
    assert(!tree.predecessor(20).has_value());

    assert((tree.inorder() == vector<int>{
        20, 30, 40, 50, 60, 70, 80
    }));

    assert((tree.rangeQuery(30, 70) == vector<int>{
        30, 40, 50, 60, 70
    }));

    assert(engine.erase(50));
    assert(!engine.erase(999));

    assert(tree.validate());
    assert(tree.size() == 6);

    BinarySearchTree empty;
    assert(empty.validate());
    assert(!empty.minimum());
    assert(!empty.maximum());
    assert(empty.height() == -1);

    bool rangeFailed = false;

    try {
        tree.rangeQuery(80, 20);
    } catch (const invalid_argument&) {
        rangeFailed = true;
    }

    assert(rangeFailed);

    // Randomized comparison against an ordered reference set.
    BinarySearchTree randomTree;
    unordered_set<int> reference;
    mt19937 generator(42);
    uniform_int_distribution<int> distribution(-100, 100);
    uniform_int_distribution<int> action(0, 1);

    for (int i = 0; i < 1000; ++i) {
        int value = distribution(generator);

        if (action(generator) == 0) {
            bool expected = reference.insert(value).second;
            assert(randomTree.insert(value) == expected);
        } else {
            bool expected = reference.erase(value) > 0;
            assert(randomTree.remove(value) == expected);
        }

        vector<int> expected(
            reference.begin(), reference.end()
        );

        sort(expected.begin(), expected.end());

        assert(randomTree.inorder() == expected);
        assert(randomTree.validate());
        assert(randomTree.size() == reference.size());
    }
}

int main() {
    try {
        runTests();

        cout << "All BST tests passed.\n\n";

        BSTAssessmentEngine engine;

        for (int value : {
            50, 30, 70, 20, 40, 60, 80, 65
        }) {
            engine.add(value);
        }

        cout << "BINARY SEARCH TREE ASSESSMENT\n";
        cout << "=============================\n";

        engine.report();

        const auto& tree = engine.getTree();

        cout << "\nSearch 40: "
             << boolalpha << tree.search(40) << '\n';

        cout << "LCA(20, 40): "
             << *engine.lca(20, 40) << '\n';

        cout << "Successor(60): "
             << *tree.successor(60) << '\n';

        cout << "Predecessor(60): "
             << *tree.predecessor(60) << '\n';

        cout << "Delete 50: "
             << engine.erase(50) << '\n';

        engine.report();

    } catch (const exception& error) {
        cerr << "BST assessment error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
