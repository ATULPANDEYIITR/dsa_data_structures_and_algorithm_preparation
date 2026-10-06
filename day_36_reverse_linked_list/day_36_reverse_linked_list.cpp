#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

class LinkedList {
private:
    struct Node {
        int value;
        std::unique_ptr<Node> next;

        explicit Node(int value) : value(value), next(nullptr) {}
    };

    std::unique_ptr<Node> head_;
    Node* tail_ = nullptr;
    std::size_t size_ = 0;

public:
    LinkedList() = default;

    explicit LinkedList(const std::vector<int>& values) {
        for (int value : values) {
            append(value);
        }
    }

    void append(int value) {
        auto new_node = std::make_unique<Node>(value);
        Node* raw_node = new_node.get();

        if (!head_) {
            head_ = std::move(new_node);
            tail_ = raw_node;
        } else {
            tail_->next = std::move(new_node);
            tail_ = raw_node;
        }

        ++size_;
    }

    std::size_t size() const {
        return size_;
    }

    std::vector<int> values() const {
        std::vector<int> result;
        result.reserve(size_);

        const Node* current = head_.get();
        std::unordered_set<const Node*> visited;

        while (current != nullptr) {
            if (!visited.insert(current).second) {
                throw std::logic_error(
                    "Cycle detected while traversing linked list."
                );
            }

            result.push_back(current->value);
            current = current->next.get();
        }

        return result;
    }

    std::string toString() const {
        const auto data = values();

        if (data.empty()) {
            return "EMPTY";
        }

        std::string output;

        for (std::size_t i = 0; i < data.size(); ++i) {
            if (i > 0) {
                output += " -> ";
            }
            output += std::to_string(data[i]);
        }

        return output;
    }

    /*
     * unique_ptr makes ownership explicit. During reversal, ownership of the
     * next node is moved into a temporary before the current node's ownership
     * is redirected to the already reversed prefix.
     *
     * The algorithm remains O(n) in time and O(1) auxiliary pointer storage.
     */
    void reverseIterative() {
        std::unique_ptr<Node> previous = nullptr;
        std::unique_ptr<Node> current = std::move(head_);

        Node* old_head = current.get();

        while (current) {
            std::unique_ptr<Node> following = std::move(current->next);
            current->next = std::move(previous);
            previous = std::move(current);
            current = std::move(following);
        }

        head_ = std::move(previous);
        tail_ = old_head;
    }

private:
    /*
     * Recursive reversal uses ownership moves rather than raw-pointer
     * manipulation. The base case returns the last node as the new head.
     */
    std::unique_ptr<Node> reverseRecursiveImpl(std::unique_ptr<Node> node) {
        if (!node || !node->next) {
            return node;
        }

        std::unique_ptr<Node> successor = std::move(node->next);
        std::unique_ptr<Node> new_head = reverseRecursiveImpl(
            std::move(successor)
        );

        /*
         * At this point, node has no next owner. The recursive suffix is
         * represented by new_head, whose tail is the successor of node.
         * Locate that tail so it can take ownership of node.
         */
        Node* suffix_tail = new_head.get();

        while (suffix_tail->next) {
            suffix_tail = suffix_tail->next.get();
        }

        suffix_tail->next = std::move(node);
        return new_head;
    }

public:
    /*
     * This implementation is intentionally recursive, but walking to the
     * suffix tail during each unwind makes it O(n^2). It is useful as a
     * contrast with the standard raw-pointer recursive formulation.
     */
    void reverseRecursiveEducational() {
        if (size_ == 0 || size_ == 1) {
            return;
        }

        Node* old_head = head_.get();
        head_ = reverseRecursiveImpl(std::move(head_));
        tail_ = old_head;
    }

    /*
     * Efficient recursive reversal using raw non-owning pointers.
     *
     * The unique_ptr ownership stays anchored at head_. The recursive helper
     * only changes links through non-owning pointers. This preserves O(n)
     * time and O(n) call-stack space.
     */
    Node* reverseRecursivePointers(Node* current) {
        if (current == nullptr || current->next == nullptr) {
            return current;
        }

        Node* new_head = reverseRecursivePointers(current->next.get());

        current->next->next.reset(current);
        current->next.release();

        return new_head;
    }

    /*
     * The efficient recursive operation above cannot safely transfer
     * unique_ptr ownership through a raw pointer without restructuring the
     * ownership model. This version uses an explicit owner reference to
     * perform the standard recursive algorithm safely.
     */
    void reverseRecursive() {
        if (size_ <= 1) {
            return;
        }

        Node* old_head = head_.get();

        reverseRecursiveOwnership(head_);

        tail_ = old_head;
    }

private:
    /*
     * The recursion operates on unique_ptr references. At every level,
     * current->next is detached before ownership of current is transferred
     * to the successor's next pointer.
     */
    Node* reverseRecursiveOwnership(std::unique_ptr<Node>& current) {
        if (!current || !current->next) {
            return current.get();
        }

        Node* current_raw = current.get();
        std::unique_ptr<Node> successor = std::move(current->next);

        Node* new_head = reverseRecursiveOwnership(successor);

        /*
         * successor now owns the reversed suffix. Its tail is found by
         * following the already reversed chain. The traversal is required
         * by this ownership representation, so this educational version has
         * O(n^2) worst-case time.
         */
        Node* suffix_tail = new_head;

        while (suffix_tail->next) {
            suffix_tail = suffix_tail->next.get();
        }

        suffix_tail->next = std::move(current);
        current.reset();

        return new_head;
    }

public:
    void demonstrateInvariantChecks(const std::vector<int>& original) {
        const auto current_values = values();

        if (current_values.size() != original.size()) {
            throw std::logic_error("Node-count invariant failed.");
        }

        if (tail_ != nullptr && tail_->next != nullptr) {
            throw std::logic_error("Tail invariant failed.");
        }
    }
};

static void printVector(const std::vector<int>& values) {
    std::cout << "[";

    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            std::cout << ", ";
        }
        std::cout << values[i];
    }

    std::cout << "]";
}

static void runIterativeCaseStudy() {
    std::cout << "ITERATIVE REVERSAL CASE STUDY\n";
    std::cout << "============================\n";

    LinkedList list({101, 205, 309, 412, 518});

    std::cout << "Original: " << list.toString() << "\n";
    list.reverseIterative();
    std::cout << "Reversed: " << list.toString() << "\n";
    std::cout << "Nodes: " << list.size() << "\n\n";
}

static void runRecursiveCaseStudy() {
    std::cout << "RECURSIVE REVERSAL CASE STUDY\n";
    std::cout << "=============================\n";

    LinkedList list({7, 14, 21, 28});

    std::cout << "Original: " << list.toString() << "\n";

    /*
     * This implementation emphasizes the recursive state transition. Its
     * ownership representation performs a suffix-tail scan during unwinding,
     * so it is intentionally not presented as the performance-optimal
     * production implementation.
     */
    list.reverseRecursiveEducational();

    std::cout << "Reversed: " << list.toString() << "\n\n";
}

static void runEdgeCases() {
    std::cout << "EDGE CASES\n";
    std::cout << "----------\n";

    for (const std::vector<int>& values : {
             std::vector<int>{},
             std::vector<int>{42},
             std::vector<int>{1, 2}
         }) {
        LinkedList iterative(values);
        LinkedList recursive(values);

        iterative.reverseIterative();
        recursive.reverseRecursiveEducational();

        std::cout << "Input: ";
        printVector(values);
        std::cout << "\nIterative: " << iterative.toString();
        std::cout << "\nRecursive: " << recursive.toString() << "\n\n";
    }
}

static void runInvariantTest() {
    const std::vector<int> original{3, 6, 9, 12, 15};

    LinkedList list(original);

    list.reverseIterative();

    const std::vector<int> expected_reversed{15, 12, 9, 6, 3};

    if (list.values() != expected_reversed) {
        throw std::logic_error("Iterative reversal produced an invalid list.");
    }

    list.reverseIterative();

    if (list.values() != original) {
        throw std::logic_error(
            "Second iterative reversal did not restore original order."
        );
    }

    list.demonstrateInvariantChecks(original);

    std::cout << "Invariant test passed.\n\n";
}

static void explainTradeoffs() {
    std::cout << "ALGORITHM TRADE-OFFS\n";
    std::cout << "--------------------\n";
    std::cout << "Iterative reversal: O(n) time, O(1) auxiliary space.\n";
    std::cout << "Recursive reversal: O(n) call-stack space.\n";
    std::cout << "The iterative approach is preferable for very long lists.\n";
    std::cout << "Recursive implementations must also account for stack depth.\n";
    std::cout << "\n";
}

int main() {
    try {
        runIterativeCaseStudy();
        runRecursiveCaseStudy();
        runEdgeCases();
        runInvariantTest();
        explainTradeoffs();
    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
