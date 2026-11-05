#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <vector>
#include <optional>
#include <string>

using namespace std;

struct Node {
    int key;
    int height;
    unique_ptr<Node> left;
    unique_ptr<Node> right;

    explicit Node(int value)
        : key(value), height(1) {}
};

struct TreeMetrics {
    int height;
    int nodes;
    bool balanced;
    bool valid;
};

class AVLTree {
private:
    unique_ptr<Node> root;
    int nodeCount = 0;

    static int getHeight(const unique_ptr<Node>& node) {
        return node ? node->height : 0;
    }

    static int balanceFactor(const unique_ptr<Node>& node) {
        if (!node) return 0;

        return getHeight(node->left) -
               getHeight(node->right);
    }

    static void updateHeight(Node* node) {
        if (!node) return;

        node->height = 1 + max(
            getHeight(node->left),
            getHeight(node->right)
        );
    }

    static unique_ptr<Node> rotateRight(
        unique_ptr<Node> y
    ) {
        if (!y || !y->left) {
            throw logic_error("Invalid right rotation.");
        }

        auto x = move(y->left);
        auto middle = move(x->right);

        y->left = move(middle);
        updateHeight(y.get());

        x->right = move(y);
        updateHeight(x.get());

        return x;
    }

    static unique_ptr<Node> rotateLeft(
        unique_ptr<Node> x
    ) {
        if (!x || !x->right) {
            throw logic_error("Invalid left rotation.");
        }

        auto y = move(x->right);
        auto middle = move(y->left);

        x->right = move(middle);
        updateHeight(x.get());

        y->left = move(x);
        updateHeight(y.get());

        return y;
    }

    static unique_ptr<Node> rebalance(
        unique_ptr<Node> node
    ) {
        if (!node) return nullptr;

        updateHeight(node.get());

        int factor = balanceFactor(node);

        if (factor > 1) {
            if (balanceFactor(node->left) < 0) {
                node->left = rotateLeft(move(node->left));
            }

            return rotateRight(move(node));
        }

        if (factor < -1) {
            if (balanceFactor(node->right) > 0) {
                node->right = rotateRight(
                    move(node->right)
                );
            }

            return rotateLeft(move(node));
        }

        return node;
    }

    static unique_ptr<Node> insertNode(
        unique_ptr<Node> node,
        int key,
        bool& inserted
    ) {
        if (!node) {
            inserted = true;
            return make_unique<Node>(key);
        }

        if (key < node->key) {
            node->left = insertNode(
                move(node->left), key, inserted
            );
        } else if (key > node->key) {
            node->right = insertNode(
                move(node->right), key, inserted
            );
        } else {
            return node;
        }

        return inserted ? rebalance(move(node)) : move(node);
    }

    static const Node* minimum(const Node* node) {
        while (node && node->left) {
            node = node->left.get();
        }

        return node;
    }

    static unique_ptr<Node> deleteNode(
        unique_ptr<Node> node,
        int key,
        bool& deleted
    ) {
        if (!node) return nullptr;

        if (key < node->key) {
            node->left = deleteNode(
                move(node->left), key, deleted
            );
        } else if (key > node->key) {
            node->right = deleteNode(
                move(node->right), key, deleted
            );
        } else {
            deleted = true;

            if (!node->left) return move(node->right);
            if (!node->right) return move(node->left);

            const Node* successor = minimum(
                node->right.get()
            );

            node->key = successor->key;

            bool successorDeleted = false;

            node->right = deleteNode(
                move(node->right),
                successor->key,
                successorDeleted
            );
        }

        return deleted ? rebalance(move(node)) : move(node);
    }

    static void inorder(
        const Node* node,
        vector<int>& result
    ) {
        if (!node) return;

        inorder(node->left.get(), result);
        result.push_back(node->key);
        inorder(node->right.get(), result);
    }

    static TreeMetrics inspect(
        const Node* node,
        optional<int> lower,
        optional<int> upper
    ) {
        if (!node) {
            return {0, 0, true, true};
        }

        if (
            (lower && node->key <= *lower) ||
            (upper && node->key >= *upper)
        ) {
            return {0, 0, false, false};
        }

        auto left = inspect(
            node->left.get(), lower, node->key
        );

        auto right = inspect(
            node->right.get(), node->key, upper
        );

        int expectedHeight = 1 + max(
            left.height, right.height
        );

        bool heightCorrect = node->height == expectedHeight;

        bool balanced =
            abs(left.height - right.height) <= 1;

        bool valid =
            left.valid && right.valid && heightCorrect;

        return {
            expectedHeight,
            left.nodes + right.nodes + 1,
            left.balanced && right.balanced && balanced,
            valid
        };
    }

public:
    void insert(int key) {
        bool inserted = false;

        root = insertNode(
            move(root), key, inserted
        );

        if (inserted) nodeCount++;
    }

    bool erase(int key) {
        bool deleted = false;

        root = deleteNode(
            move(root), key, deleted
        );

        if (deleted) nodeCount--;

        return deleted;
    }

    bool search(int key, int& comparisons) const {
        const Node* current = root.get();
        comparisons = 0;

        while (current) {
            comparisons++;

            if (current->key == key) {
                return true;
            }

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    vector<int> getInorder() const {
        vector<int> result;
        inorder(root.get(), result);
        return result;
    }

    TreeMetrics validate() const {
        auto result = inspect(root.get(), nullopt, nullopt);

        if (result.nodes != nodeCount) {
            throw logic_error("Node count mismatch.");
        }

        if (!result.valid) {
            throw logic_error("BST or height invariant violated.");
        }

        return result;
    }
};

class UnbalancedBST {
private:
    struct BasicNode {
        int key;
        unique_ptr<BasicNode> left;
        unique_ptr<BasicNode> right;

        explicit BasicNode(int value) : key(value) {}
    };

    unique_ptr<BasicNode> root;
    int count = 0;

    static int calculateHeight(const BasicNode* node) {
        if (!node) return 0;

        return 1 + max(
            calculateHeight(node->left.get()),
            calculateHeight(node->right.get())
        );
    }

public:
    void insert(int key) {
        if (!root) {
            root = make_unique<BasicNode>(key);
            count++;
            return;
        }

        BasicNode* current = root.get();

        while (true) {
            if (key == current->key) return;

            if (key < current->key) {
                if (!current->left) {
                    current->left = make_unique<BasicNode>(key);
                    count++;
                    return;
                }

                current = current->left.get();
            } else {
                if (!current->right) {
                    current->right = make_unique<BasicNode>(key);
                    count++;
                    return;
                }

                current = current->right.get();
            }
        }
    }

    int height() const {
        return calculateHeight(root.get());
    }

    int size() const {
        return count;
    }
};

void printVector(const vector<int>& values) {
    for (int value : values) {
        cout << value << " ";
    }
    cout << '\n';
}

int main() {
    try {
        cout << "BALANCED TREE ENGINEERING\n";
        cout << "=========================\n";

        AVLTree avl;

        vector<int> values = {
            40, 20, 60, 10, 30, 50, 70,
            5, 15, 25, 35, 45, 55
        };

        for (int value : values) {
            avl.insert(value);

            auto metrics = avl.validate();

            if (!metrics.balanced) {
                throw logic_error("AVL balance failed.");
            }
        }

        auto metrics = avl.validate();

        cout << "\nAVL TREE\n";
        cout << "Nodes: " << metrics.nodes << '\n';
        cout << "Height: " << metrics.height << '\n';
        cout << "Balanced: "
             << boolalpha << metrics.balanced << '\n';

        cout << "Inorder: ";
        printVector(avl.getInorder());

        int comparisons = 0;

        cout << "Search 55: "
             << avl.search(55, comparisons)
             << ", comparisons: " << comparisons << '\n';

        cout << "\nDELETION\n";

        avl.erase(40);
        avl.erase(10);

        metrics = avl.validate();

        cout << "Nodes after deletion: "
             << metrics.nodes << '\n';

        cout << "Height after deletion: "
             << metrics.height << '\n';

        cout << "Balanced after deletion: "
             << metrics.balanced << '\n';

        cout << "\nUNBALANCED BST\n";

        UnbalancedBST ordinary;

        for (int i = 1; i <= 100; i++) {
            ordinary.insert(i);
        }

        cout << "Nodes: " << ordinary.size() << '\n';
        cout << "Height: " << ordinary.height() << '\n';

        cout << "\nPERFORMANCE ANALYSIS\n";
        cout << "AVL search: O(log n)\n";
        cout << "Unbalanced BST worst case: O(n)\n";
        cout << "AVL insertion: O(log n)\n";
        cout << "AVL deletion: O(log n)\n";

        // Edge cases.
        AVLTree empty;
        auto emptyMetrics = empty.validate();

        if (emptyMetrics.height != 0) {
            throw logic_error("Empty tree validation failed.");
        }

        AVLTree single;
        single.insert(100);
        single.insert(100);

        if (single.validate().nodes != 1) {
            throw logic_error("Duplicate handling failed.");
        }

        single.erase(100);

        if (single.validate().height != 0) {
            throw logic_error("Single-node deletion failed.");
        }

        cout << "\nAll validation checks passed.\n";

    } catch (const exception& error) {
        cerr << "Execution error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
