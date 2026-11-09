#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Binary Search Tree Deletion
 * C++17
 *
 * Engineering perspective:
 * - Unique integer keys.
 * - Ownership managed through unique_ptr.
 * - No manual memory allocation.
 * - Subtree ownership transferred during deletion.
 * - Successor and predecessor implementations.
 * - Recursive deletion with explicit ownership changes.
 */

class BinarySearchTree {
private:
    struct Node {
        int key;
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;

        explicit Node(int value) : key(value) {}
    };

    std::unique_ptr<Node> root;
    std::size_t nodeCount = 0;

    static Node* minimum(Node* node) {
        if (!node) return nullptr;

        while (node->left) {
            node = node->left.get();
        }

        return node;
    }

    static Node* maximum(Node* node) {
        if (!node) return nullptr;

        while (node->right) {
            node = node->right.get();
        }

        return node;
    }

    static void inorderHelper(
        const Node* node,
        std::vector<int>& result
    ) {
        if (!node) return;

        inorderHelper(node->left.get(), result);
        result.push_back(node->key);
        inorderHelper(node->right.get(), result);
    }

    static void preorderHelper(
        const Node* node,
        std::vector<int>& result
    ) {
        if (!node) return;

        result.push_back(node->key);
        preorderHelper(node->left.get(), result);
        preorderHelper(node->right.get(), result);
    }

    static void postorderHelper(
        const Node* node,
        std::vector<int>& result
    ) {
        if (!node) return;

        postorderHelper(node->left.get(), result);
        postorderHelper(node->right.get(), result);
        result.push_back(node->key);
    }

    static bool validateNode(
        const Node* node,
        std::optional<int> lower,
        std::optional<int> upper,
        std::size_t& count
    ) {
        if (!node) return true;

        if (lower && node->key <= *lower) return false;
        if (upper && node->key >= *upper) return false;

        ++count;

        return validateNode(
            node->left.get(), lower, node->key, count
        ) && validateNode(
            node->right.get(), node->key, upper, count
        );
    }

    /*
     * Remove the minimum node from a subtree.
     * Its right child replaces it because a minimum node
     * cannot have a left child.
     */
    static std::unique_ptr<Node> extractMinimum(
        std::unique_ptr<Node>& subtree
    ) {
        if (!subtree->left) {
            auto minimumNode = std::move(subtree);
            subtree = std::move(minimumNode->right);
            return minimumNode;
        }

        return extractMinimum(subtree->left);
    }

    static bool deleteRecursive(
        std::unique_ptr<Node>& node,
        int key
    ) {
        if (!node) return false;

        if (key < node->key) {
            return deleteRecursive(node->left, key);
        }

        if (key > node->key) {
            return deleteRecursive(node->right, key);
        }

        // Case 1: Leaf node.
        if (!node->left && !node->right) {
            node.reset();
            return true;
        }

        // Case 2: Only right child.
        if (!node->left) {
            node = std::move(node->right);
            return true;
        }

        // Case 2: Only left child.
        if (!node->right) {
            node = std::move(node->left);
            return true;
        }

        // Case 3: Two children.
        // Extract the minimum node from the right subtree.
        auto replacement = extractMinimum(node->right);

        replacement->left = std::move(node->left);
        replacement->right = std::move(node->right);

        node = std::move(replacement);

        return true;
    }

public:
    BinarySearchTree() = default;

    BinarySearchTree(const BinarySearchTree&) = delete;
    BinarySearchTree& operator=(const BinarySearchTree&) = delete;

    BinarySearchTree(BinarySearchTree&&) noexcept = default;
    BinarySearchTree& operator=(BinarySearchTree&&) noexcept = default;

    std::size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return root == nullptr;
    }

    bool insert(int key) {
        auto* current = &root;

        while (*current) {
            if (key == (*current)->key) {
                return false;
            }

            if (key < (*current)->key) {
                current = &((*current)->left);
            } else {
                current = &((*current)->right);
            }
        }

        *current = std::make_unique<Node>(key);
        ++nodeCount;

        return true;
    }

    bool contains(int key) const {
        const Node* current = root.get();

        while (current) {
            if (key == current->key) return true;

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    bool erase(int key) {
        bool deleted = deleteRecursive(root, key);

        if (deleted) {
            --nodeCount;
        }

        return deleted;
    }

    std::optional<int> successor(int key) const {
        const Node* current = root.get();
        const Node* candidate = nullptr;

        while (current) {
            if (key < current->key) {
                candidate = current;
                current = current->left.get();
            } else if (key > current->key) {
                current = current->right.get();
            } else {
                if (current->right) {
                    return minimum(current->right.get())->key;
                }

                return candidate
                    ? std::optional<int>(candidate->key)
                    : std::nullopt;
            }
        }

        return std::nullopt;
    }

    std::optional<int> predecessor(int key) const {
        const Node* current = root.get();
        const Node* candidate = nullptr;

        while (current) {
            if (key > current->key) {
                candidate = current;
                current = current->right.get();
            } else if (key < current->key) {
                current = current->left.get();
            } else {
                if (current->left) {
                    return maximum(current->left.get())->key;
                }

                return candidate
                    ? std::optional<int>(candidate->key)
                    : std::nullopt;
            }
        }

        return std::nullopt;
    }

    std::vector<int> inorder() const {
        std::vector<int> result;
        inorderHelper(root.get(), result);
        return result;
    }

    std::vector<int> preorder() const {
        std::vector<int> result;
        preorderHelper(root.get(), result);
        return result;
    }

    std::vector<int> postorder() const {
        std::vector<int> result;
        postorderHelper(root.get(), result);
        return result;
    }

    std::vector<std::vector<int>> levelOrder() const {
        std::vector<std::vector<int>> result;

        if (!root) return result;

        std::queue<const Node*> pending;
        pending.push(root.get());

        while (!pending.empty()) {
            std::size_t count = pending.size();
            std::vector<int> level;

            while (count--) {
                const Node* node = pending.front();
                pending.pop();

                level.push_back(node->key);

                if (node->left) pending.push(node->left.get());
                if (node->right) pending.push(node->right.get());
            }

            result.push_back(std::move(level));
        }

        return result;
    }

    bool validate() const {
        std::size_t actualCount = 0;

        bool valid = validateNode(
            root.get(), std::nullopt, std::nullopt, actualCount
        );

        return valid && actualCount == nodeCount;
    }

    void display() const {
        auto print = [](const std::vector<int>& values) {
            for (int value : values) {
                std::cout << value << ' ';
            }
            std::cout << '\n';
        };

        std::cout << "Inorder: ";
        print(inorder());

        std::cout << "Preorder: ";
        print(preorder());

        std::cout << "Postorder: ";
        print(postorder());

        std::cout << "Levels:\n";

        for (const auto& level : levelOrder()) {
            print(level);
        }

        std::cout << "Size: " << size() << '\n';
        std::cout << "Valid: "
                  << std::boolalpha << validate() << '\n';
    }
};

static void printOptional(
    const std::string& label,
    std::optional<int> value
) {
    std::cout << label;

    if (value) {
        std::cout << *value;
    } else {
        std::cout << "None";
    }

    std::cout << '\n';
}

int main() {
    try {
        BinarySearchTree tree;

        const std::vector<int> values = {
            50, 30, 70, 20, 40, 60, 80, 35, 45, 65
        };

        for (int value : values) {
            assert(tree.insert(value));
        }

        std::cout << "INITIAL TREE\n";
        tree.display();

        std::cout << "\nSUCCESSOR AND PREDECESSOR\n";

        printOptional("Successor of 50: ", tree.successor(50));
        printOptional("Predecessor of 50: ", tree.predecessor(50));
        printOptional("Successor of 80: ", tree.successor(80));
        printOptional("Predecessor of 20: ", tree.predecessor(20));

        // Case 1: Leaf.
        std::cout << "\nCASE 1: LEAF DELETION\n";
        assert(tree.erase(20));
        assert(tree.validate());
        tree.display();

        // Case 2: One child.
        std::cout << "\nCASE 2: ONE-CHILD DELETION\n";
        assert(tree.erase(60));
        assert(tree.validate());
        tree.display();

        // Case 3: Two children.
        std::cout << "\nCASE 3: TWO-CHILD DELETION\n";
        assert(tree.erase(70));
        assert(tree.validate());
        tree.display();

        // Root deletion.
        std::cout << "\nROOT DELETION\n";
        assert(tree.erase(50));
        assert(tree.validate());
        tree.display();

        // Missing key.
        assert(!tree.erase(999));

        // Duplicate insertion.
        assert(!tree.insert(35));

        // Empty-tree deletion.
        BinarySearchTree emptyTree;
        assert(!emptyTree.erase(10));
        assert(emptyTree.validate());

        // Single-node deletion.
        BinarySearchTree singleTree;
        assert(singleTree.insert(10));
        assert(singleTree.erase(10));
        assert(singleTree.empty());

        // Complete cleanup.
        for (int key : tree.inorder()) {
            assert(tree.erase(key));
        }

        assert(tree.empty());
        assert(tree.size() == 0);
        assert(tree.validate());

        // Integer boundaries.
        BinarySearchTree boundaryTree;
        assert(boundaryTree.insert(-2147483647));
        assert(boundaryTree.insert(2147483647));
        assert(boundaryTree.validate());

        std::cout << "\nALL TESTS PASSED.\n";

    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
