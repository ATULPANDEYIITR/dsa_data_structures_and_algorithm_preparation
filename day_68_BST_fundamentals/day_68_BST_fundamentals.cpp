#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

struct InventoryNode {
    int productId;
    string productName;
    int quantity;
    unique_ptr<InventoryNode> left;
    unique_ptr<InventoryNode> right;

    InventoryNode(int id, string name, int stock)
        : productId(id),
          productName(move(name)),
          quantity(stock) {}
};

class InventoryBST {
private:
    unique_ptr<InventoryNode> root;
    size_t nodeCount = 0;

    static const InventoryNode* minimumNode(
        const InventoryNode* node
    ) {
        if (!node) return nullptr;

        while (node->left) {
            node = node->left.get();
        }

        return node;
    }

    static const InventoryNode* maximumNode(
        const InventoryNode* node
    ) {
        if (!node) return nullptr;

        while (node->right) {
            node = node->right.get();
        }

        return node;
    }

    static bool validate(
        const InventoryNode* node,
        optional<int> lower,
        optional<int> upper
    ) {
        if (!node) return true;

        if (lower && node->productId <= *lower) return false;
        if (upper && node->productId >= *upper) return false;

        return validate(node->left.get(), lower, node->productId)
            && validate(node->right.get(), node->productId, upper);
    }

    static int calculateHeight(const InventoryNode* node) {
        if (!node) return -1;

        return 1 + max(
            calculateHeight(node->left.get()),
            calculateHeight(node->right.get())
        );
    }

    static void inorderTraversal(
        const InventoryNode* node,
        vector<pair<int, string>>& result
    ) {
        if (!node) return;

        inorderTraversal(node->left.get(), result);

        result.emplace_back(
            node->productId,
            node->productName
        );

        inorderTraversal(node->right.get(), result);
    }

    static void preorderTraversal(
        const InventoryNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        result.push_back(node->productId);
        preorderTraversal(node->left.get(), result);
        preorderTraversal(node->right.get(), result);
    }

    static void postorderTraversal(
        const InventoryNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        postorderTraversal(node->left.get(), result);
        postorderTraversal(node->right.get(), result);
        result.push_back(node->productId);
    }

    static unique_ptr<InventoryNode> buildBalanced(
        const vector<pair<int, string>>& entries,
        int start,
        int end
    ) {
        if (start > end) return nullptr;

        int middle = start + (end - start) / 2;
        const auto& entry = entries[middle];

        auto node = make_unique<InventoryNode>(
            entry.first,
            entry.second,
            0
        );

        node->left = buildBalanced(entries, start, middle - 1);
        node->right = buildBalanced(entries, middle + 1, end);

        return node;
    }

public:
    bool insert(int id, const string& name, int stock) {
        if (id <= 0) {
            throw invalid_argument("Product ID must be positive.");
        }

        if (name.empty()) {
            throw invalid_argument("Product name cannot be empty.");
        }

        if (stock < 0) {
            throw invalid_argument("Stock cannot be negative.");
        }

        auto* current = &root;

        while (*current) {
            if (id == (*current)->productId) {
                return false;
            }

            if (id < (*current)->productId) {
                current = &((*current)->left);
            } else {
                current = &((*current)->right);
            }
        }

        *current = make_unique<InventoryNode>(id, name, stock);
        ++nodeCount;

        return true;
    }

    const InventoryNode* search(int id) const {
        const InventoryNode* current = root.get();

        while (current) {
            if (id == current->productId) return current;

            current = id < current->productId
                ? current->left.get()
                : current->right.get();
        }

        return nullptr;
    }

    bool deleteProduct(int id) {
        function<bool(unique_ptr<InventoryNode>&)> remove =
            [&](unique_ptr<InventoryNode>& node) -> bool {

            if (!node) return false;

            if (id < node->productId) {
                return remove(node->left);
            }

            if (id > node->productId) {
                return remove(node->right);
            }

            if (!node->left) {
                node = move(node->right);
                return true;
            }

            if (!node->right) {
                node = move(node->left);
                return true;
            }

            // Two children: copy successor data and remove successor.
            const InventoryNode* successor =
                minimumNode(node->right.get());

            node->productId = successor->productId;
            node->productName = successor->productName;
            node->quantity = successor->quantity;

            function<void(unique_ptr<InventoryNode>&)> removeMin =
                [&](unique_ptr<InventoryNode>& subtree) {
                    if (!subtree->left) {
                        subtree = move(subtree->right);
                        return;
                    }
                    removeMin(subtree->left);
                };

            removeMin(node->right);
            return true;
        };

        bool deleted = remove(root);

        if (deleted) --nodeCount;

        return deleted;
    }

    optional<int> minimum() const {
        auto node = minimumNode(root.get());

        if (!node) return nullopt;

        return node->productId;
    }

    optional<int> maximum() const {
        auto node = maximumNode(root.get());

        if (!node) return nullopt;

        return node->productId;
    }

    vector<pair<int, string>> inorder() const {
        vector<pair<int, string>> result;
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

    vector<vector<int>> levelOrder() const {
        vector<vector<int>> result;

        if (!root) return result;

        queue<const InventoryNode*> nodes;
        nodes.push(root.get());

        while (!nodes.empty()) {
            size_t levelSize = nodes.size();
            vector<int> level;

            for (size_t i = 0; i < levelSize; ++i) {
                const InventoryNode* node = nodes.front();
                nodes.pop();

                level.push_back(node->productId);

                if (node->left) nodes.push(node->left.get());
                if (node->right) nodes.push(node->right.get());
            }

            result.push_back(move(level));
        }

        return result;
    }

    int height() const {
        return calculateHeight(root.get());
    }

    optional<int> kthSmallest(int k) const {
        if (k < 1 || static_cast<size_t>(k) > nodeCount) {
            return nullopt;
        }

        vector<const InventoryNode*> stack;
        const InventoryNode* current = root.get();

        int count = 0;

        while (current || !stack.empty()) {
            while (current) {
                stack.push_back(current);
                current = current->left.get();
            }

            current = stack.back();
            stack.pop_back();

            if (++count == k) return current->productId;

            current = current->right.get();
        }

        return nullopt;
    }

    bool isValid() const {
        return validate(root.get(), nullopt, nullopt);
    }

    size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return root == nullptr;
    }

    InventoryBST balancedCopy() const {
        InventoryBST balanced;
        auto entries = inorder();

        balanced.root = buildBalanced(
            entries,
            0,
            static_cast<int>(entries.size()) - 1
        );

        balanced.nodeCount = entries.size();

        return balanced;
    }

    void printInorder() const {
        for (const auto& [id, name] : inorder()) {
            cout << id << " : " << name << '\n';
        }
    }
};

int main() {
    try {
        cout << "INVENTORY BINARY SEARCH TREE\n";
        cout << "============================\n\n";

        InventoryBST inventory;

        vector<tuple<int, string, int>> products = {
            {500, "Laptop", 12},
            {300, "Keyboard", 30},
            {700, "Monitor", 8},
            {200, "Mouse", 45},
            {400, "Headphones", 20},
            {600, "Webcam", 15},
            {800, "Printer", 5}
        };

        cout << "INSERTION\n";

        for (const auto& [id, name, stock] : products) {
            cout << id << ": "
                 << (inventory.insert(id, name, stock)
                     ? "Inserted" : "Duplicate") << '\n';
        }

        cout << "\nDuplicate insertion: "
             << inventory.insert(500, "Replacement", 1) << '\n';

        cout << "\nSEARCH\n";

        auto product = inventory.search(400);

        if (product) {
            cout << product->productName
                 << ", stock=" << product->quantity << '\n';
        }

        cout << "Missing product: "
             << (inventory.search(999) != nullptr) << '\n';

        cout << "\nINORDER\n";
        inventory.printInorder();

        cout << "\nPREORDER: ";
        for (int id : inventory.preorder()) cout << id << ' ';

        cout << "\nPOSTORDER: ";
        for (int id : inventory.postorder()) cout << id << ' ';

        cout << "\nLEVEL ORDER\n";

        for (const auto& level : inventory.levelOrder()) {
            for (int id : level) cout << id << ' ';
            cout << '\n';
        }

        cout << "\nMINIMUM: " << *inventory.minimum();
        cout << "\nMAXIMUM: " << *inventory.maximum();
        cout << "\nHEIGHT: " << inventory.height();

        cout << "\nTHIRD SMALLEST: "
             << *inventory.kthSmallest(3) << '\n';

        cout << "\nDELETION\n";

        cout << "Delete leaf 200: "
             << inventory.deleteProduct(200) << '\n';

        cout << "Delete node 300: "
             << inventory.deleteProduct(300) << '\n';

        cout << "Delete missing 999: "
             << inventory.deleteProduct(999) << '\n';

        cout << "\nVALID BST: " << inventory.isValid();
        cout << "\nNODE COUNT: " << inventory.size() << '\n';

        InventoryBST balanced = inventory.balancedCopy();

        cout << "\nBALANCED COPY\n";
        cout << "Height: " << balanced.height() << '\n';
        balanced.printInorder();

        cout << "\nEDGE CASES\n";

        InventoryBST empty;

        cout << "Empty tree: " << empty.empty() << '\n';
        cout << "Empty height: " << empty.height() << '\n';
        cout << "Empty minimum exists: "
             << empty.minimum().has_value() << '\n';

        InventoryBST single;
        single.insert(10, "Single Product", 1);
        single.deleteProduct(10);

        cout << "Single-node tree after deletion: "
             << single.empty() << '\n';

        bool invalidRejected = false;

        try {
            inventory.insert(-1, "Invalid", 10);
        } catch (const invalid_argument&) {
            invalidRejected = true;
        }

        assert(invalidRejected);
        assert(inventory.isValid());
        assert(balanced.isValid());
        assert(inventory.size() == 5);
        assert(inventory.kthSmallest(1).has_value());
        assert(!inventory.kthSmallest(100).has_value());

        cout << "\nAll C++ assertions passed.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
