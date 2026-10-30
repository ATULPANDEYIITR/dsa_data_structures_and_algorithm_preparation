#include <algorithm>
#include <iostream>
#include <memory>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Binary tree with explicit ownership.
 *
 * Each parent uniquely owns its children through std::unique_ptr.
 * Parent pointers are non-owning observers.
 *
 * Height: longest downward path measured in edges.
 * Depth: path from root measured in edges.
 * Level: depth + 1.
 * A leaf has height 0.
 */

struct Node {
    std::string id;
    std::string value;
    Node* parent = nullptr;
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;

    Node(std::string nodeId, std::string nodeValue)
        : id(std::move(nodeId)), value(std::move(nodeValue)) {
        if (id.empty() || value.empty()) {
            throw std::invalid_argument("Node ID and value cannot be empty.");
        }
    }

    bool isLeaf() const {
        return !left && !right;
    }
};

class BinaryTree {
public:
    explicit BinaryTree(std::unique_ptr<Node> root)
        : root_(std::move(root)) {
        if (!root_) {
            throw std::invalid_argument("A binary tree requires a root.");
        }
        if (root_->parent != nullptr) {
            throw std::invalid_argument("The root cannot have a parent.");
        }

        // Verify the initial structure before accepting ownership.
        collectSubtree(root_.get());
    }

    Node& root() {
        return *root_;
    }

    const Node& root() const {
        return *root_;
    }

    static std::unique_ptr<Node> makeNode(
        const std::string& id,
        const std::string& value
    ) {
        return std::make_unique<Node>(id, value);
    }

    void attachLeft(Node& parent, std::unique_ptr<Node> child) {
        attach(parent, std::move(child), Side::Left);
    }

    void attachRight(Node& parent, std::unique_ptr<Node> child) {
        attach(parent, std::move(child), Side::Right);
    }

    bool contains(const Node* target) const {
        if (target == nullptr) return false;

        const auto existing = collectSubtree(root_.get());
        return std::find(existing.begin(), existing.end(), target) != existing.end();
    }

    int depth(const Node& node) const {
        requireMember(&node);

        int result = 0;
        const Node* current = &node;
        std::unordered_set<const Node*> visited;

        while (current->parent != nullptr) {
            if (!visited.insert(current).second) {
                throw std::logic_error("Cycle in parent references.");
            }

            current = current->parent;
            ++result;
        }

        if (current != root_.get()) {
            throw std::logic_error("Node is disconnected from the root.");
        }

        return result;
    }

    int level(const Node& node) const {
        return depth(node) + 1;
    }

    int height(const Node& node) const {
        requireMember(&node);

        // Iterative postorder avoids dependence on the call-stack size.
        std::vector<std::pair<const Node*, bool>> stack;
        std::unordered_map<const Node*, int> heights;
        stack.emplace_back(&node, false);

        while (!stack.empty()) {
            const auto [current, expanded] = stack.back();
            stack.pop_back();

            if (!expanded) {
                stack.emplace_back(current, true);

                if (current->right) {
                    stack.emplace_back(current->right.get(), false);
                }
                if (current->left) {
                    stack.emplace_back(current->left.get(), false);
                }
            } else {
                const int leftHeight = current->left
                    ? heights.at(current->left.get())
                    : -1;

                const int rightHeight = current->right
                    ? heights.at(current->right.get())
                    : -1;

                heights[current] = 1 + std::max(leftHeight, rightHeight);
            }
        }

        return heights.at(&node);
    }

    int treeHeight() const {
        return height(*root_);
    }

    std::size_t subtreeSize(const Node& node) const {
        requireMember(&node);
        return collectSubtree(const_cast<Node*>(&node)).size();
    }

    std::size_t nodeCount() const {
        return collectSubtree(root_.get()).size();
    }

    std::vector<std::vector<std::string>> levels() const {
        std::vector<std::vector<std::string>> result;
        std::queue<const Node*> pending;
        pending.push(root_.get());

        while (!pending.empty()) {
            const std::size_t count = pending.size();
            std::vector<std::string> currentLevel;
            currentLevel.reserve(count);

            for (std::size_t i = 0; i < count; ++i) {
                const Node* node = pending.front();
                pending.pop();

                currentLevel.push_back(node->id);

                if (node->left) pending.push(node->left.get());
                if (node->right) pending.push(node->right.get());
            }

            result.push_back(std::move(currentLevel));
        }

        return result;
    }

    std::vector<std::string> preorder() const {
        std::vector<std::string> result;
        std::vector<const Node*> stack{root_.get()};

        while (!stack.empty()) {
            const Node* node = stack.back();
            stack.pop_back();
            result.push_back(node->id);

            if (node->right) stack.push_back(node->right.get());
            if (node->left) stack.push_back(node->left.get());
        }

        return result;
    }

    std::vector<std::string> inorder() const {
        std::vector<std::string> result;
        std::vector<const Node*> stack;
        const Node* current = root_.get();

        while (current != nullptr || !stack.empty()) {
            while (current != nullptr) {
                stack.push_back(current);
                current = current->left.get();
            }

            current = stack.back();
            stack.pop_back();

            result.push_back(current->id);
            current = current->right.get();
        }

        return result;
    }

    std::vector<std::string> postorder() const {
        std::vector<std::string> result;
        std::vector<std::pair<const Node*, bool>> stack;
        stack.emplace_back(root_.get(), false);

        while (!stack.empty()) {
            const auto [node, expanded] = stack.back();
            stack.pop_back();

            if (expanded) {
                result.push_back(node->id);
                continue;
            }

            stack.emplace_back(node, true);

            if (node->right) {
                stack.emplace_back(node->right.get(), false);
            }
            if (node->left) {
                stack.emplace_back(node->left.get(), false);
            }
        }

        return result;
    }

    void validate() const {
        const auto nodes = collectSubtree(root_.get());

        if (nodes.empty() || root_->parent != nullptr) {
            throw std::logic_error("Invalid tree root.");
        }
    }

private:
    enum class Side {
        Left,
        Right
    };

    std::unique_ptr<Node> root_;

    static std::vector<Node*> collectSubtree(Node* start) {
        if (start == nullptr) {
            throw std::invalid_argument("Cannot inspect a null subtree.");
        }

        std::vector<Node*> result;
        std::unordered_set<Node*> visited;
        std::vector<std::pair<Node*, Node*>> stack;
        stack.emplace_back(start, nullptr);

        while (!stack.empty()) {
            const auto [current, expectedParent] = stack.back();
            stack.pop_back();

            if (!visited.insert(current).second) {
                throw std::logic_error("Cycle or shared child detected.");
            }

            if (current->parent != expectedParent) {
                throw std::logic_error("Inconsistent parent reference.");
            }

            result.push_back(current);

            if (current->right) {
                stack.emplace_back(current->right.get(), current);
            }
            if (current->left) {
                stack.emplace_back(current->left.get(), current);
            }
        }

        return result;
    }

    void requireMember(const Node* node) const {
        if (!contains(node)) {
            throw std::invalid_argument("Node does not belong to this tree.");
        }
    }

    void attach(
        Node& parent,
        std::unique_ptr<Node> child,
        Side side
    ) {
        requireMember(&parent);

        if (!child) {
            throw std::invalid_argument("Cannot attach a null subtree.");
        }
        if (child->parent != nullptr) {
            throw std::invalid_argument("Incoming subtree must be detached.");
        }

        auto existing = collectSubtree(root_.get());
        auto incoming = collectSubtree(child.get());

        std::unordered_set<Node*> existingSet(existing.begin(), existing.end());

        for (Node* node : incoming) {
            if (existingSet.count(node) != 0) {
                throw std::logic_error("Incoming subtree overlaps this tree.");
            }
        }

        std::unique_ptr<Node>& slot =
            (side == Side::Left) ? parent.left : parent.right;

        if (slot) {
            throw std::logic_error(
                side == Side::Left
                    ? "Left child slot is already occupied."
                    : "Right child slot is already occupied."
            );
        }

        // Ownership transfer happens only after every validation succeeds.
        child->parent = &parent;
        slot = std::move(child);
    }
};

void printList(
    const std::string& label,
    const std::vector<std::string>& values
) {
    std::cout << label << ": ";
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i > 0) std::cout << " ";
        std::cout << values[i];
    }
    std::cout << '\n';
}

int main() {
    try {
        // Manual construction:
        //
        //              A
        //             / \
        //            B   C
        //           / \   \
        //          D   E   F
        //             /
        //            G

        BinaryTree tree(BinaryTree::makeNode("A", "Root"));

        Node& a = tree.root();

        tree.attachLeft(
            a,
            BinaryTree::makeNode("B", "Left child of A")
        );
        tree.attachRight(
            a,
            BinaryTree::makeNode("C", "Right child of A")
        );

        Node& b = *a.left;
        Node& c = *a.right;

        tree.attachLeft(
            b,
            BinaryTree::makeNode("D", "Left child of B")
        );
        tree.attachRight(
            b,
            BinaryTree::makeNode("E", "Right child of B")
        );
        tree.attachRight(
            c,
            BinaryTree::makeNode("F", "Right child of C")
        );

        Node& e = *b.right;
        tree.attachLeft(
            e,
            BinaryTree::makeNode("G", "Left child of E")
        );

        tree.validate();

        std::cout << "BINARY TREE FUNDAMENTALS\n";
        std::cout << "Node count: " << tree.nodeCount() << '\n';
        std::cout << "Tree height: " << tree.treeHeight() << '\n';

        printList("Preorder", tree.preorder());
        printList("Inorder", tree.inorder());
        printList("Postorder", tree.postorder());

        std::cout << "\nLEVELS\n";
        const auto levelGroups = tree.levels();

        for (std::size_t i = 0; i < levelGroups.size(); ++i) {
            std::cout << "Level " << (i + 1) << ": ";
            for (const auto& id : levelGroups[i]) {
                std::cout << id << " ";
            }
            std::cout << '\n';
        }

        std::cout << "\nNODE METRICS\n";
        const std::vector<const Node*> selected = {
            &a, &b, &*b.left, &*e.left, &c
        };

        for (const Node* node : selected) {
            std::cout
                << node->id
                << ": parent="
                << (node->parent ? node->parent->id : "none")
                << ", depth=" << tree.depth(*node)
                << ", level=" << tree.level(*node)
                << ", height=" << tree.height(*node)
                << ", leaf=" << (node->isLeaf() ? "yes" : "no")
                << ", subtree_size=" << tree.subtreeSize(*node)
                << '\n';
        }

        std::cout << "\nSUBTREE ROOTED AT B\n";
        std::cout << "Height: " << tree.height(b) << '\n';
        std::cout << "Size: " << tree.subtreeSize(b) << '\n';

        std::cout << "\nINVALID ATTACHMENT TEST\n";
        try {
            tree.attachLeft(
                *e.left,
                BinaryTree::makeNode("X", "Invalid attachment")
            );
            throw std::logic_error("Expected occupied-slot rejection.");
        } catch (const std::logic_error& error) {
            std::cout << "Rejected: " << error.what() << '\n';
        }

        if (tree.treeHeight() != 3 ||
            tree.depth(*e.left) != 3 ||
            tree.subtreeSize(b) != 4) {
            throw std::logic_error("Tree metric assertion failed.");
        }

        std::cout << "\nAll structural checks passed.\n";
    } catch (const std::exception& error) {
        std::cerr << "Tree operation failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
