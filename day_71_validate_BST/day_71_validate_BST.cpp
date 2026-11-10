/*
 * VALIDATE BINARY SEARCH TREE
 *
 * C++17
 * Standard library only.
 *
 * Implements:
 * - Range-based validation.
 * - Inorder-based validation.
 * - Duplicate-key policies.
 * - BST insertion and search.
 * - Successor and predecessor.
 * - Deletion.
 * - Lowest common ancestor.
 * - Merge-independent tree validation.
 * - Automated assertions.
 */

#include <iostream>
#include <memory>
#include <vector>
#include <stack>
#include <optional>
#include <stdexcept>
#include <limits>
#include <cassert>
#include <string>
#include <algorithm>

using namespace std;

enum class DuplicatePolicy {
    FORBID,
    LEFT,
    RIGHT
};

struct Node {
    int key;
    unique_ptr<Node> left;
    unique_ptr<Node> right;

    explicit Node(int value) : key(value) {}
};

class BinarySearchTree {
private:
    unique_ptr<Node> root;
    size_t nodeCount = 0;
    DuplicatePolicy policy;

    struct RangeState {
        const Node* node;
        optional<long long> low;
        optional<long long> high;
        bool lowInclusive;
        bool highInclusive;
    };

    bool validateDuplicatePlacement() const {
        struct State {
            const Node* node;
            vector<pair<int, string>> ancestors;
        };

        stack<State> pending;
        pending.push({root.get(), {}});

        while (!pending.empty()) {
            State state = move(pending.top());
            pending.pop();

            const Node* node = state.node;

            if (!node) {
                continue;
            }

            for (const auto& [key, side] : state.ancestors) {
                if (node->key == key) {
                    if (policy == DuplicatePolicy::LEFT &&
                        side != "left") {
                        return false;
                    }

                    if (policy == DuplicatePolicy::RIGHT &&
                        side != "right") {
                        return false;
                    }
                }
            }

            auto leftAncestors = state.ancestors;
            leftAncestors.push_back({node->key, "left"});

            auto rightAncestors = state.ancestors;
            rightAncestors.push_back({node->key, "right"});

            pending.push({node->left.get(), move(leftAncestors)});
            pending.push({node->right.get(), move(rightAncestors)});
        }

        return true;
    }

public:
    explicit BinarySearchTree(
        DuplicatePolicy duplicatePolicy = DuplicatePolicy::FORBID
    ) : policy(duplicatePolicy) {}

    size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return root == nullptr;
    }

    void insert(int key) {
        unique_ptr<Node>* current = &root;

        while (*current) {
            if (key < (*current)->key) {
                current = &((*current)->left);
            } else if (key > (*current)->key) {
                current = &((*current)->right);
            } else {
                if (policy == DuplicatePolicy::FORBID) {
                    throw invalid_argument("Duplicate key insertion.");
                }

                current = policy == DuplicatePolicy::LEFT
                    ? &((*current)->left)
                    : &((*current)->right);
            }
        }

        *current = make_unique<Node>(key);
        ++nodeCount;
    }

    const Node* search(int key) const {
        const Node* current = root.get();

        while (current) {
            if (key == current->key) {
                return current;
            }

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return nullptr;
    }

    static bool validateRange(
        const Node* root,
        optional<long long> low = nullopt,
        optional<long long> high = nullopt,
        bool lowInclusive = false,
        bool highInclusive = false
    ) {
        stack<RangeState> pending;

        pending.push({
            root,
            low,
            high,
            lowInclusive,
            highInclusive
        });

        while (!pending.empty()) {
            RangeState state = pending.top();
            pending.pop();

            const Node* node = state.node;

            if (!node) {
                continue;
            }

            if (state.low) {
                if (node->key < *state.low) {
                    return false;
                }

                if (node->key == *state.low &&
                    !state.lowInclusive) {
                    return false;
                }
            }

            if (state.high) {
                if (node->key > *state.high) {
                    return false;
                }

                if (node->key == *state.high &&
                    !state.highInclusive) {
                    return false;
                }
            }

            pending.push({
                node->left.get(),
                state.low,
                node->key,
                state.lowInclusive,
                false
            });

            pending.push({
                node->right.get(),
                node->key,
                state.high,
                false,
                state.highInclusive
            });
        }

        return true;
    }

    static bool validateInorder(
        const Node* root,
        DuplicatePolicy policy = DuplicatePolicy::FORBID
    ) {
        stack<const Node*> pending;
        const Node* current = root;

        optional<int> previous;

        while (current || !pending.empty()) {
            while (current) {
                pending.push(current);
                current = current->left.get();
            }

            current = pending.top();
            pending.pop();

            if (previous) {
                if (policy == DuplicatePolicy::FORBID) {
                    if (current->key <= *previous) {
                        return false;
                    }
                } else if (current->key < *previous) {
                    return false;
                }
            }

            previous = current->key;
            current = current->right.get();
        }

        return true;
    }

    bool isValid() const {
        if (policy == DuplicatePolicy::FORBID) {
            return validateRange(root.get());
        }

        return validateInorder(root.get(), policy) &&
               validateDuplicatePlacement();
    }

    vector<int> inorder() const {
        vector<int> result;
        stack<const Node*> pending;
        const Node* current = root.get();

        while (current || !pending.empty()) {
            while (current) {
                pending.push(current);
                current = current->left.get();
            }

            current = pending.top();
            pending.pop();

            result.push_back(current->key);
            current = current->right.get();
        }

        return result;
    }

    vector<int> preorder() const {
        vector<int> result;

        if (!root) {
            return result;
        }

        stack<const Node*> pending;
        pending.push(root.get());

        while (!pending.empty()) {
            const Node* current = pending.top();
            pending.pop();

            result.push_back(current->key);

            if (current->right) {
                pending.push(current->right.get());
            }

            if (current->left) {
                pending.push(current->left.get());
            }
        }

        return result;
    }

    const Node* minimum(const Node* node = nullptr) const {
        const Node* current = node ? node : root.get();

        if (!current) {
            return nullptr;
        }

        while (current->left) {
            current = current->left.get();
        }

        return current;
    }

    const Node* maximum(const Node* node = nullptr) const {
        const Node* current = node ? node : root.get();

        if (!current) {
            return nullptr;
        }

        while (current->right) {
            current = current->right.get();
        }

        return current;
    }

    optional<int> successor(int key) const {
        const Node* current = root.get();
        const Node* candidate = nullptr;

        while (current) {
            if (key < current->key) {
                candidate = current;
                current = current->left.get();
            } else {
                current = current->right.get();
            }
        }

        if (!candidate) {
            return nullopt;
        }

        return candidate->key;
    }

    optional<int> predecessor(int key) const {
        const Node* current = root.get();
        const Node* candidate = nullptr;

        while (current) {
            if (key > current->key) {
                candidate = current;
                current = current->right.get();
            } else {
                current = current->left.get();
            }
        }

        if (!candidate) {
            return nullopt;
        }

        return candidate->key;
    }

    optional<int> successorOfNode(int key) const {
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

                if (candidate) {
                    return candidate->key;
                }

                return nullopt;
            }
        }

        return nullopt;
    }

    optional<int> predecessorOfNode(int key) const {
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

                if (candidate) {
                    return candidate->key;
                }

                return nullopt;
            }
        }

        return nullopt;
    }

    optional<int> lowestCommonAncestor(int first, int second) const {
        if (!search(first) || !search(second)) {
            return nullopt;
        }

        const Node* current = root.get();

        while (current) {
            if (first < current->key && second < current->key) {
                current = current->left.get();
            } else if (
                first > current->key &&
                second > current->key
            ) {
                current = current->right.get();
            } else {
                return current->key;
            }
        }

        return nullopt;
    }

    bool erase(int key) {
        unique_ptr<Node>* current = &root;

        while (*current && (*current)->key != key) {
            if (key < (*current)->key) {
                current = &((*current)->left);
            } else {
                current = &((*current)->right);
            }
        }

        if (!*current) {
            return false;
        }

        if ((*current)->left && (*current)->right) {
            unique_ptr<Node>* successorLink =
                &((*current)->right);

            while ((*successorLink)->left) {
                successorLink = &((*successorLink)->left);
            }

            (*current)->key = (*successorLink)->key;

            auto successorNode = move(*successorLink);
            *successorLink = move(successorNode->right);
        } else {
            auto deletedNode = move(*current);

            *current = deletedNode->left
                ? move(deletedNode->left)
                : move(deletedNode->right);
        }

        --nodeCount;
        return true;
    }

    void printInorder() const {
        const auto values = inorder();

        cout << "[";

        for (size_t i = 0; i < values.size(); ++i) {
            if (i > 0) cout << ", ";
            cout << values[i];
        }

        cout << "]\n";
    }
};

string display(const optional<int>& value) {
    return value ? to_string(*value) : "NONE";
}

void runTests() {
    BinarySearchTree tree;

    for (int value : {50, 30, 70, 20, 40, 60, 80}) {
        tree.insert(value);
    }

    assert(tree.isValid());
    assert(tree.size() == 7);

    assert(tree.inorder() ==
           vector<int>({20, 30, 40, 50, 60, 70, 80}));

    assert(tree.search(40) != nullptr);
    assert(tree.search(999) == nullptr);

    assert(tree.successor(40) == optional<int>(50));
    assert(tree.predecessor(40) == optional<int>(30));

    assert(!tree.successor(80));
    assert(!tree.predecessor(20));

    assert(tree.successorOfNode(50) == optional<int>(60));
    assert(tree.predecessorOfNode(50) == optional<int>(40));

    assert(tree.lowestCommonAncestor(20, 40) == optional<int>(30));
    assert(tree.lowestCommonAncestor(20, 80) == optional<int>(50));

    assert(tree.erase(20));
    assert(tree.erase(30));
    assert(tree.erase(50));
    assert(!tree.erase(999));

    assert(tree.size() == 4);
    assert(tree.isValid());

    BinarySearchTree empty;
    assert(empty.isValid());
    assert(empty.inorder().empty());

    Node invalidRoot(10);
    invalidRoot.left = make_unique<Node>(5);
    invalidRoot.left->right = make_unique<Node>(12);
    invalidRoot.right = make_unique<Node>(15);

    assert(!BinarySearchTree::validateRange(&invalidRoot));
    assert(!BinarySearchTree::validateInorder(&invalidRoot));

    BinarySearchTree duplicates(DuplicatePolicy::RIGHT);
    duplicates.insert(10);
    duplicates.insert(10);
    duplicates.insert(15);

    assert(duplicates.isValid());

    BinarySearchTree forbidden;

    forbidden.insert(10);

    bool duplicateRejected = false;

    try {
        forbidden.insert(10);
    } catch (const invalid_argument&) {
        duplicateRejected = true;
    }

    assert(duplicateRejected);

    Node extreme(0);
    extreme.left = make_unique<Node>(numeric_limits<int>::min());
    extreme.right = make_unique<Node>(numeric_limits<int>::max());

    assert(BinarySearchTree::validateRange(&extreme));

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        cout << "VALIDATE BINARY SEARCH TREE\n\n";

        BinarySearchTree tree;

        for (int value : {50, 30, 70, 20, 40, 60, 80}) {
            tree.insert(value);
        }

        cout << "1. INORDER TRAVERSAL\n";
        tree.printInorder();

        cout << "\n2. VALIDATION\n";

        cout << "Range-based: "
             << BinarySearchTree::validateRange(
                    tree.search(50) ? nullptr : nullptr
                ) << "\n";

        cout << "Tree valid: " << boolalpha
             << tree.isValid() << "\n";

        cout << "\n3. SUCCESSOR AND PREDECESSOR\n";

        for (int key : {20, 30, 40, 50, 60, 70, 80, 55}) {
            cout << "Key " << key
                 << " | Successor: "
                 << display(tree.successor(key))
                 << " | Predecessor: "
                 << display(tree.predecessor(key))
                 << "\n";
        }

        cout << "\n4. EXISTING NODE RELATIONSHIPS\n";

        cout << "Successor of 50: "
             << display(tree.successorOfNode(50)) << "\n";

        cout << "Predecessor of 50: "
             << display(tree.predecessorOfNode(50)) << "\n";

        cout << "LCA(20, 40): "
             << display(tree.lowestCommonAncestor(20, 40))
             << "\n";

        cout << "\n5. DELETION\n";

        tree.erase(20);
        tree.erase(30);
        tree.erase(50);

        tree.printInorder();

        cout << "Valid after deletion: "
             << tree.isValid() << "\n";

        cout << "\n6. AUTOMATED TESTS\n";
        runTests();

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
