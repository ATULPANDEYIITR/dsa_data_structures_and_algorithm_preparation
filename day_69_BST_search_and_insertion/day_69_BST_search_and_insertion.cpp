#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <memory>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

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
    size_t comparisons = 0;

public:
    BinarySearchTree() = default;

    BinarySearchTree(const BinarySearchTree&) = delete;
    BinarySearchTree& operator=(const BinarySearchTree&) = delete;

    bool insert(int key) {
        unique_ptr<Node>* current = &root;

        while (*current != nullptr) {
            if (key == (*current)->key) {
                return false;
            }

            current = key < (*current)->key
                ? &(*current)->left
                : &(*current)->right;
        }

        *current = make_unique<Node>(key);
        ++nodeCount;

        return true;
    }

    bool search(int key) {
        comparisons = 0;
        const Node* current = root.get();

        while (current != nullptr) {
            ++comparisons;

            if (current->key == key) {
                return true;
            }

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    optional<int> minimum() const {
        if (!root) {
            return nullopt;
        }

        const Node* current = root.get();

        while (current->left) {
            current = current->left.get();
        }

        return current->key;
    }

    optional<int> maximum() const {
        if (!root) {
            return nullopt;
        }

        const Node* current = root.get();

        while (current->right) {
            current = current->right.get();
        }

        return current->key;
    }

    vector<int> inorder() const {
        vector<int> result;
        vector<const Node*> stack;
        const Node* current = root.get();

        while (current != nullptr || !stack.empty()) {
            while (current != nullptr) {
                stack.push_back(current);
                current = current->left.get();
            }

            current = stack.back();
            stack.pop_back();

            result.push_back(current->key);
            current = current->right.get();
        }

        return result;
    }

    int height() const {
        if (!root) {
            return -1;
        }

        vector<pair<const Node*, int>> queue;
        queue.emplace_back(root.get(), 0);

        int maximumDepth = 0;

        for (size_t i = 0; i < queue.size(); ++i) {
            auto [node, depth] = queue[i];

            maximumDepth = max(maximumDepth, depth);

            if (node->left) {
                queue.emplace_back(node->left.get(), depth + 1);
            }

            if (node->right) {
                queue.emplace_back(node->right.get(), depth + 1);
            }
        }

        return maximumDepth;
    }

    bool validate() const {
        struct Frame {
            const Node* node;
            optional<int> lower;
            optional<int> upper;
        };

        vector<Frame> stack;
        stack.push_back({root.get(), nullopt, nullopt});

        size_t visited = 0;

        while (!stack.empty()) {
            Frame frame = stack.back();
            stack.pop_back();

            if (frame.node == nullptr) {
                continue;
            }

            int key = frame.node->key;

            if (frame.lower && key <= *frame.lower) {
                return false;
            }

            if (frame.upper && key >= *frame.upper) {
                return false;
            }

            ++visited;

            stack.push_back({
                frame.node->left.get(),
                frame.lower,
                key
            });

            stack.push_back({
                frame.node->right.get(),
                key,
                frame.upper
            });
        }

        return visited == nodeCount;
    }

    size_t size() const {
        return nodeCount;
    }

    size_t lastComparisons() const {
        return comparisons;
    }

    void exportReport(const string& filename) const {
        if (filename.size() < 5 ||
            filename.substr(filename.size() - 5) != ".json") {
            throw invalid_argument("Report filename must end in .json");
        }

        ofstream output(filename);

        if (!output) {
            throw runtime_error("Unable to open report file.");
        }

        output << "{\n";
        output << "  \"size\": " << nodeCount << ",\n";
        output << "  \"height\": " << height() << ",\n";

        auto minValue = minimum();
        auto maxValue = maximum();

        output << "  \"minimum\": ";

        if (minValue) {
            output << *minValue;
        } else {
            output << "null";
        }

        output << ",\n  \"maximum\": ";

        if (maxValue) {
            output << *maxValue;
        } else {
            output << "null";
        }

        output << ",\n  \"keys\": [";

        vector<int> values = inorder();

        for (size_t i = 0; i < values.size(); ++i) {
            if (i > 0) {
                output << ", ";
            }

            output << values[i];
        }

        output << "]\n}\n";

        if (!output.good()) {
            throw runtime_error("Failed while writing report.");
        }
    }
};

void display(const string& label, const optional<int>& value) {
    cout << label;

    if (value) {
        cout << *value;
    } else {
        cout << "Not available";
    }

    cout << '\n';
}

vector<int> medianFirstOrder(const vector<int>& sorted) {
    vector<int> result;

    vector<pair<int, int>> ranges;
    ranges.emplace_back(0, static_cast<int>(sorted.size()) - 1);

    while (!ranges.empty()) {
        auto [low, high] = ranges.back();
        ranges.pop_back();

        if (low > high) {
            continue;
        }

        int middle = low + (high - low) / 2;
        result.push_back(sorted[middle]);

        ranges.emplace_back(middle + 1, high);
        ranges.emplace_back(low, middle - 1);
    }

    return result;
}

void benchmark() {
    constexpr int N = 2000;

    vector<int> values(N);

    for (int i = 0; i < N; ++i) {
        values[i] = i + 1;
    }

    BinarySearchTree balanced;
    BinarySearchTree skewed;

    for (int key : medianFirstOrder(values)) {
        balanced.insert(key);
    }

    for (int key : values) {
        skewed.insert(key);
    }

    cout << "\n=== Benchmark ===\n";

    for (auto* tree : {&balanced, &skewed}) {
        auto start = chrono::steady_clock::now();

        bool found = tree->search(N);

        auto end = chrono::steady_clock::now();

        auto elapsed = chrono::duration<double, milli>(
            end - start
        ).count();

        cout << "Found: " << boolalpha << found
             << ", height: " << tree->height()
             << ", comparisons: " << tree->lastComparisons()
             << ", milliseconds: " << elapsed << '\n';
    }
}

int main() {
    try {
        cout << "=== Asset Registry BST ===\n";

        BinarySearchTree registry;

        vector<int> assetIds = {
            500, 300, 700, 200, 400, 600, 800, 350, 450
        };

        for (int id : assetIds) {
            cout << "Insert " << id << ": "
                 << boolalpha << registry.insert(id) << '\n';
        }

        cout << "Duplicate 500: "
             << registry.insert(500) << '\n';

        cout << "Search 400: "
             << registry.search(400)
             << ", comparisons: "
             << registry.lastComparisons() << '\n';

        cout << "Search 999: "
             << registry.search(999)
             << ", comparisons: "
             << registry.lastComparisons() << '\n';

        display("Minimum asset ID: ", registry.minimum());
        display("Maximum asset ID: ", registry.maximum());

        cout << "Sorted asset IDs: ";

        for (int id : registry.inorder()) {
            cout << id << ' ';
        }

        cout << "\nHeight: " << registry.height();
        cout << "\nNode count: " << registry.size();
        cout << "\nBST integrity: "
             << registry.validate() << '\n';

        if (!registry.validate()) {
            throw runtime_error("BST integrity check failed.");
        }

        if (!registry.search(400)) {
            throw runtime_error("Search test failed.");
        }

        if (registry.minimum() != optional<int>(200) ||
            registry.maximum() != optional<int>(800)) {
            throw runtime_error("Boundary test failed.");
        }

        BinarySearchTree empty;

        if (empty.minimum().has_value() ||
            empty.maximum().has_value() ||
            empty.search(10)) {
            throw runtime_error("Empty tree test failed.");
        }

        registry.exportReport("bst_report.json");

        cout << "\nJSON report exported successfully.\n";

        benchmark();

        cout << "\nAll tests passed.\n";
    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
