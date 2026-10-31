#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

struct TreeNode {
    int value;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int value) : value(value) {}
};

class TraversalError : public std::runtime_error {
public:
    explicit TraversalError(const std::string& message)
        : std::runtime_error(message) {}
};

/*
 * A binary tree owns each child through unique_ptr. The validator still
 * checks for malformed graphs because callers can construct aliasing
 * structures by using raw pointers or custom ownership outside this model.
 */
void validateTree(const TreeNode* root) {
    std::unordered_set<const TreeNode*> active;
    std::unordered_set<const TreeNode*> visited;

    std::function<void(const TreeNode*)> check =
        [&](const TreeNode* node) {
            if (node == nullptr) return;

            if (active.contains(node)) {
                throw TraversalError("Cycle detected");
            }
            if (visited.contains(node)) {
                throw TraversalError("Node has multiple parents");
            }

            active.insert(node);
            check(node->left.get());
            check(node->right.get());
            active.erase(node);
            visited.insert(node);
        };

    check(root);
}

void preorderRecursiveImpl(const TreeNode* node, std::vector<int>& result) {
    if (node == nullptr) return;
    result.push_back(node->value);
    preorderRecursiveImpl(node->left.get(), result);
    preorderRecursiveImpl(node->right.get(), result);
}

void inorderRecursiveImpl(const TreeNode* node, std::vector<int>& result) {
    if (node == nullptr) return;
    inorderRecursiveImpl(node->left.get(), result);
    result.push_back(node->value);
    inorderRecursiveImpl(node->right.get(), result);
}

void postorderRecursiveImpl(const TreeNode* node, std::vector<int>& result) {
    if (node == nullptr) return;
    postorderRecursiveImpl(node->left.get(), result);
    postorderRecursiveImpl(node->right.get(), result);
    result.push_back(node->value);
}

std::vector<int> preorderRecursive(const TreeNode* root) {
    validateTree(root);
    std::vector<int> result;
    preorderRecursiveImpl(root, result);
    return result;
}

std::vector<int> inorderRecursive(const TreeNode* root) {
    validateTree(root);
    std::vector<int> result;
    inorderRecursiveImpl(root, result);
    return result;
}

std::vector<int> postorderRecursive(const TreeNode* root) {
    validateTree(root);
    std::vector<int> result;
    postorderRecursiveImpl(root, result);
    return result;
}

std::vector<int> preorderIterative(const TreeNode* root) {
    validateTree(root);
    if (root == nullptr) return {};

    std::vector<const TreeNode*> stack{root};
    std::vector<int> result;

    while (!stack.empty()) {
        const TreeNode* node = stack.back();
        stack.pop_back();

        result.push_back(node->value);

        if (node->right) stack.push_back(node->right.get());
        if (node->left) stack.push_back(node->left.get());
    }

    return result;
}

std::vector<int> inorderIterative(const TreeNode* root) {
    validateTree(root);

    std::vector<const TreeNode*> stack;
    std::vector<int> result;
    const TreeNode* current = root;

    while (current != nullptr || !stack.empty()) {
        while (current != nullptr) {
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

std::vector<int> postorderIterative(const TreeNode* root) {
    validateTree(root);
    if (root == nullptr) return {};

    std::vector<const TreeNode*> first{root};
    std::vector<const TreeNode*> second;

    while (!first.empty()) {
        const TreeNode* node = first.back();
        first.pop_back();
        second.push_back(node);

        if (node->left) first.push_back(node->left.get());
        if (node->right) first.push_back(node->right.get());
    }

    std::vector<int> result;
    result.reserve(second.size());

    while (!second.empty()) {
        result.push_back(second.back()->value);
        second.pop_back();
    }

    return result;
}

std::vector<int> postorderIterativeOneStack(const TreeNode* root) {
    validateTree(root);

    std::vector<const TreeNode*> stack;
    std::vector<int> result;
    const TreeNode* current = root;
    const TreeNode* previous = nullptr;

    while (current != nullptr || !stack.empty()) {
        if (current != nullptr) {
            stack.push_back(current);
            current = current->left.get();
            continue;
        }

        const TreeNode* node = stack.back();

        if (node->right && previous != node->right.get()) {
            current = node->right.get();
        } else {
            result.push_back(node->value);
            previous = node;
            stack.pop_back();
        }
    }

    return result;
}

std::unique_ptr<TreeNode> sampleTree() {
    auto root = std::make_unique<TreeNode>(1);
    root->left = std::make_unique<TreeNode>(2);
    root->right = std::make_unique<TreeNode>(3);

    root->left->left = std::make_unique<TreeNode>(4);
    root->left->right = std::make_unique<TreeNode>(5);
    root->right->left = std::make_unique<TreeNode>(6);
    root->right->right = std::make_unique<TreeNode>(7);

    return root;
}

void printVector(const std::vector<int>& values) {
    std::cout << "[";
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) std::cout << ", ";
        std::cout << values[i];
    }
    std::cout << "]";
}

int main() {
    try {
        auto tree = sampleTree();

        const std::vector<int> expectedPre{1, 2, 4, 5, 3, 6, 7};
        const std::vector<int> expectedIn{4, 2, 5, 1, 6, 3, 7};
        const std::vector<int> expectedPost{4, 5, 2, 6, 7, 3, 1};

        const auto pr = preorderRecursive(tree.get());
        const auto pi = preorderIterative(tree.get());
        const auto ir = inorderRecursive(tree.get());
        const auto ii = inorderIterative(tree.get());
        const auto por = postorderRecursive(tree.get());
        const auto poi = postorderIterative(tree.get());
        const auto pois = postorderIterativeOneStack(tree.get());

        assert(pr == expectedPre);
        assert(pi == expectedPre);
        assert(ir == expectedIn);
        assert(ii == expectedIn);
        assert(por == expectedPost);
        assert(poi == expectedPost);
        assert(pois == expectedPost);

        std::cout << "Preorder recursive:   ";
        printVector(pr);
        std::cout << "\nPreorder iterative:   ";
        printVector(pi);
        std::cout << "\nInorder recursive:    ";
        printVector(ir);
        std::cout << "\nInorder iterative:    ";
        printVector(ii);
        std::cout << "\nPostorder recursive:  ";
        printVector(por);
        std::cout << "\nPostorder iterative:  ";
        printVector(poi);
        std::cout << "\nPostorder one-stack:  ";
        printVector(pois);
        std::cout << "\n";

        assert(preorderIterative(nullptr).empty());
        assert(inorderIterative(nullptr).empty());
        assert(postorderIterative(nullptr).empty());

        auto single = std::make_unique<TreeNode>(42);
        assert(inorderRecursive(single.get()) == std::vector<int>{42});

        /*
         * A right-skewed tree with 5,000 nodes demonstrates why explicit
         * stacks are useful when tree height can exceed safe recursion depth.
         */
        auto deep = std::make_unique<TreeNode>(0);
        TreeNode* current = deep.get();

        for (int i = 1; i <= 5000; ++i) {
            current->right = std::make_unique<TreeNode>(i);
            current = current->right.get();
        }

        const auto deepPre = preorderIterative(deep.get());
        const auto deepIn = inorderIterative(deep.get());
        const auto deepPost = postorderIterative(deep.get());

        assert(deepPre.size() == 5001);
        assert(deepPre.front() == 0 && deepPre.back() == 5000);
        assert(deepIn.front() == 0 && deepIn.back() == 5000);
        assert(deepPost.front() == 5000 && deepPost.back() == 0);

        std::cout << "All traversal assertions passed.\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Traversal failure: " << ex.what() << '\n';
        return 1;
    }
}
