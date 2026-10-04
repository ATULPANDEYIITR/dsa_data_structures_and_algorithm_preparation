#include <algorithm>
#include <functional>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Singly Linked List Case Study
 *
 * Scenario:
 * A repository governance service maintains an ordered chain of validation
 * stages for a change request. The implementation uses a manually managed
 * singly linked list rather than std::list so that node ownership, head
 * replacement, traversal, insertion, deletion, and pointer manipulation
 * remain explicit.
 *
 * The program demonstrates:
 * - Node and head representation
 * - Traversal
 * - Head and indexed insertion
 * - Head and indexed deletion
 * - Searching
 * - In-place reversal
 * - Cycle detection
 * - Integrity validation
 * - A realistic ordered processing workflow
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic singly_linked_list.cpp -o linked_list
 */

template <typename T>
class SinglyLinkedList {
private:
    struct Node {
        T data;
        Node* next;

        explicit Node(const T& value)
            : data(value), next(nullptr) {}
    };

    Node* head_;
    std::size_t size_;

    Node* nodeAt(std::size_t index) const {
        if (index >= size_) {
            throw std::out_of_range("node index is outside the list");
        }

        Node* current = head_;

        for (std::size_t position = 0; position < index; ++position) {
            current = current->next;
        }

        return current;
    }

public:
    SinglyLinkedList()
        : head_(nullptr), size_(0) {}

    ~SinglyLinkedList() {
        clear();
    }

    SinglyLinkedList(const SinglyLinkedList&) = delete;
    SinglyLinkedList& operator=(const SinglyLinkedList&) = delete;

    SinglyLinkedList(SinglyLinkedList&& other) noexcept
        : head_(other.head_), size_(other.size_) {
        other.head_ = nullptr;
        other.size_ = 0;
    }

    SinglyLinkedList& operator=(SinglyLinkedList&& other) noexcept {
        if (this != &other) {
            clear();

            head_ = other.head_;
            size_ = other.size_;

            other.head_ = nullptr;
            other.size_ = 0;
        }

        return *this;
    }

    bool empty() const noexcept {
        return head_ == nullptr;
    }

    std::size_t size() const noexcept {
        return size_;
    }

    const T& front() const {
        if (head_ == nullptr) {
            throw std::out_of_range("cannot access head of empty list");
        }

        return head_->data;
    }

    void insertAtHead(const T& value) {
        Node* newNode = new Node(value);

        // The new node takes ownership of the old head link before the
        // list changes its head pointer.
        newNode->next = head_;
        head_ = newNode;

        ++size_;
    }

    void insertAtEnd(const T& value) {
        Node* newNode = new Node(value);

        if (head_ == nullptr) {
            head_ = newNode;
            ++size_;
            return;
        }

        Node* current = head_;

        while (current->next != nullptr) {
            current = current->next;
        }

        current->next = newNode;
        ++size_;
    }

    void insertAt(std::size_t index, const T& value) {
        if (index > size_) {
            throw std::out_of_range("insertion index is outside the list");
        }

        if (index == 0) {
            insertAtHead(value);
            return;
        }

        if (index == size_) {
            insertAtEnd(value);
            return;
        }

        Node* previous = nodeAt(index - 1);
        Node* newNode = new Node(value);

        newNode->next = previous->next;
        previous->next = newNode;

        ++size_;
    }

    void insertAfterFirst(const T& target, const T& value) {
        Node* current = head_;

        while (current != nullptr) {
            if (current->data == target) {
                Node* newNode = new Node(value);

                newNode->next = current->next;
                current->next = newNode;

                ++size_;
                return;
            }

            current = current->next;
        }

        throw std::invalid_argument("target value was not found");
    }

    bool contains(const T& value) const {
        Node* current = head_;

        while (current != nullptr) {
            if (current->data == value) {
                return true;
            }

            current = current->next;
        }

        return false;
    }

    T deleteHead() {
        if (head_ == nullptr) {
            throw std::out_of_range("cannot delete head from an empty list");
        }

        Node* removed = head_;
        head_ = removed->next;

        T value = removed->data;
        delete removed;

        --size_;

        return value;
    }

    T deleteAt(std::size_t index) {
        if (index >= size_) {
            throw std::out_of_range("deletion index is outside the list");
        }

        if (index == 0) {
            return deleteHead();
        }

        Node* previous = nodeAt(index - 1);
        Node* removed = previous->next;

        previous->next = removed->next;

        T value = removed->data;
        delete removed;

        --size_;

        return value;
    }

    T deleteFirst(const T& value) {
        if (head_ == nullptr) {
            throw std::out_of_range("cannot delete from an empty list");
        }

        if (head_->data == value) {
            return deleteHead();
        }

        Node* previous = head_;
        Node* current = head_->next;

        while (current != nullptr) {
            if (current->data == value) {
                previous->next = current->next;

                T removedValue = current->data;
                delete current;

                --size_;
                return removedValue;
            }

            previous = current;
            current = current->next;
        }

        throw std::invalid_argument("value was not found");
    }

    std::size_t deleteAll(const T& value) {
        std::size_t removedCount = 0;

        while (head_ != nullptr && head_->data == value) {
            deleteHead();
            ++removedCount;
        }

        if (head_ == nullptr) {
            return removedCount;
        }

        Node* previous = head_;
        Node* current = head_->next;

        while (current != nullptr) {
            if (current->data == value) {
                previous->next = current->next;
                delete current;

                current = previous->next;
                --size_;
                ++removedCount;
            } else {
                previous = current;
                current = current->next;
            }
        }

        return removedCount;
    }

    void reverse() noexcept {
        Node* previous = nullptr;
        Node* current = head_;

        while (current != nullptr) {
            Node* nextNode = current->next;

            // Reverse exactly one edge. Saving nextNode first prevents the
            // remainder of the chain from becoming unreachable.
            current->next = previous;
            previous = current;
            current = nextNode;
        }

        head_ = previous;
    }

    bool detectCycle() const noexcept {
        Node* slow = head_;
        Node* fast = head_;

        while (fast != nullptr && fast->next != nullptr) {
            slow = slow->next;
            fast = fast->next->next;

            if (slow == fast) {
                return true;
            }
        }

        return false;
    }

    void validateIntegrity() const {
        if (detectCycle()) {
            throw std::logic_error("list contains a cycle");
        }

        std::size_t counted = 0;
        Node* current = head_;

        while (current != nullptr) {
            ++counted;
            current = current->next;
        }

        if (counted != size_) {
            throw std::logic_error(
                "node count does not match the maintained list size"
            );
        }
    }

    void clear() noexcept {
        Node* current = head_;

        while (current != nullptr) {
            Node* nextNode = current->next;
            delete current;
            current = nextNode;
        }

        head_ = nullptr;
        size_ = 0;
    }

    std::vector<T> values() const {
        std::vector<T> result;
        result.reserve(size_);

        Node* current = head_;

        while (current != nullptr) {
            result.push_back(current->data);
            current = current->next;
        }

        return result;
    }

    void print(const std::string& label) const {
        std::cout << label << "HEAD";

        Node* current = head_;

        while (current != nullptr) {
            std::cout << " -> " << current->data;
            current = current->next;
        }

        std::cout << " -> NULL"
                  << " | size=" << size_
                  << '\n';
    }

    /*
     * Test-only helper used to demonstrate cycle detection.
     *
     * It deliberately corrupts the structure and therefore must never be
     * exposed as a normal mutation operation in production code.
     */
    void createCycleForDemonstration() {
        if (head_ == nullptr) {
            return;
        }

        Node* tail = head_;

        while (tail->next != nullptr) {
            tail = tail->next;
        }

        tail->next = head_;
    }

    /*
     * Repairs the deliberately created demonstration cycle by locating the
     * node whose next pointer returns to head.
     */
    void repairDemonstrationCycle() {
        if (head_ == nullptr) {
            return;
        }

        Node* current = head_;

        while (current->next != nullptr && current->next != head_) {
            current = current->next;
        }

        if (current->next == head_) {
            current->next = nullptr;
        }
    }
};

void demonstrateNodeAndHead() {
    std::cout << "\n=== Node and Head ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtHead("first");
    list.insertAtHead("second");
    list.insertAtHead("third");

    list.print("Head-managed chain: ");
}

void demonstrateTraversal() {
    std::cout << "\n=== Traversal ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtEnd("change-request");
    list.insertAtEnd("review");
    list.insertAtEnd("approval");
    list.insertAtEnd("merge");

    list.print("Traversal: ");

    std::cout << "Contains approval: "
              << std::boolalpha
              << list.contains("approval")
              << '\n';

    std::cout << "Contains rejected: "
              << list.contains("rejected")
              << '\n';
}

void demonstrateInsertion() {
    std::cout << "\n=== Insertion ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtHead("review");
    list.insertAtHead("changes");
    list.insertAtEnd("merge");
    list.insertAt(1, "approval");
    list.insertAfterFirst("approval", "status-check");

    list.print("After insertion operations: ");
    list.validateIntegrity();
}

void demonstrateDeletion() {
    std::cout << "\n=== Deletion ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtEnd("pull-request");
    list.insertAtEnd("code-review");
    list.insertAtEnd("approval");
    list.insertAtEnd("approval");
    list.insertAtEnd("merge");

    list.print("Initial: ");

    std::cout << "Deleted head: "
              << list.deleteHead()
              << '\n';

    std::cout << "Deleted index 1: "
              << list.deleteAt(1)
              << '\n';

    std::cout << "Deleted first approval: "
              << list.deleteFirst("approval")
              << '\n';

    std::cout << "Deleted approval count: "
              << list.deleteAll("approval")
              << '\n';

    list.print("After deletion operations: ");
    list.validateIntegrity();
}

void demonstrateReverse() {
    std::cout << "\n=== In-place Reversal ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtEnd("A");
    list.insertAtEnd("B");
    list.insertAtEnd("C");
    list.insertAtEnd("D");

    list.print("Before reverse: ");

    list.reverse();

    list.print("After reverse: ");
    list.validateIntegrity();
}

void demonstrateCycleDetection() {
    std::cout << "\n=== Cycle Detection ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtEnd("node-A");
    list.insertAtEnd("node-B");
    list.insertAtEnd("node-C");

    std::cout << "Cycle before corruption: "
              << std::boolalpha
              << list.detectCycle()
              << '\n';

    list.createCycleForDemonstration();

    std::cout << "Cycle after deliberate corruption: "
              << list.detectCycle()
              << '\n';

    list.repairDemonstrationCycle();

    std::cout << "Cycle after repair: "
              << list.detectCycle()
              << '\n';

    list.validateIntegrity();
}

void demonstrateRealisticCaseStudy() {
    std::cout << "\n=== Repository Validation Pipeline Case Study ===\n";

    /*
     * The repository service represents ordered processing stages as a
     * singly linked chain. Removing the head models completing the current
     * stage and advancing directly to the next stage.
     */
    SinglyLinkedList<std::string> pipeline;

    pipeline.insertAtEnd("validate-change");
    pipeline.insertAtEnd("run-status-checks");
    pipeline.insertAtEnd("collect-review");
    pipeline.insertAtEnd("verify-merge-policy");
    pipeline.insertAtEnd("merge-change");

    pipeline.print("Initial pipeline: ");

    while (!pipeline.empty()) {
        const std::string currentStage = pipeline.deleteHead();

        std::cout << "Completed stage: "
                  << currentStage
                  << '\n';

        pipeline.print("Remaining stages: ");
    }

    std::cout << "Pipeline complete.\n";
}

void demonstrateFailureHandling() {
    std::cout << "\n=== Failure Handling ===\n";

    SinglyLinkedList<std::string> list;

    list.insertAtEnd("alpha");
    list.insertAtEnd("beta");

    try {
        list.deleteAt(10);
    } catch (const std::out_of_range& error) {
        std::cout << "Invalid deletion rejected: "
                  << error.what()
                  << '\n';
    }

    try {
        list.insertAt(10, "gamma");
    } catch (const std::out_of_range& error) {
        std::cout << "Invalid insertion rejected: "
                  << error.what()
                  << '\n';
    }

    try {
        list.deleteFirst("missing");
    } catch (const std::invalid_argument& error) {
        std::cout << "Missing value rejected: "
                  << error.what()
                  << '\n';
    }

    SinglyLinkedList<std::string> empty;

    try {
        empty.deleteHead();
    } catch (const std::out_of_range& error) {
        std::cout << "Empty-list deletion rejected: "
                  << error.what()
                  << '\n';
    }
}

void demonstrateEdgeCases() {
    std::cout << "\n=== Edge Cases ===\n";

    SinglyLinkedList<int> empty;
    empty.validateIntegrity();

    std::cout << "Empty list size: "
              << empty.size()
              << '\n';

    SinglyLinkedList<int> single;
    single.insertAtHead(42);
    single.validateIntegrity();

    std::cout << "Single-node list: ";
    single.print("");

    single.reverse();
    single.validateIntegrity();

    SinglyLinkedList<int> duplicates;
    duplicates.insertAtEnd(7);
    duplicates.insertAtEnd(7);
    duplicates.insertAtEnd(7);

    std::cout << "Removed duplicates: "
              << duplicates.deleteAll(7)
              << '\n';

    duplicates.validateIntegrity();
    duplicates.print("After duplicate deletion: ");
}

void demonstrateComplexity() {
    std::cout << "\n=== Complexity ===\n";

    std::cout << "Head insertion: O(1)\n";
    std::cout << "Head deletion: O(1)\n";
    std::cout << "Traversal: O(n)\n";
    std::cout << "Search: O(n)\n";
    std::cout << "Indexed access: O(n)\n";
    std::cout << "Indexed insertion: O(n)\n";
    std::cout << "Indexed deletion: O(n)\n";
    std::cout << "Tail insertion without a tail pointer: O(n)\n";
    std::cout << "In-place reversal: O(n) time, O(1) auxiliary space\n";
    std::cout << "Floyd cycle detection: O(n) time, O(1) auxiliary space\n";
}

int main() {
    try {
        demonstrateNodeAndHead();
        demonstrateTraversal();
        demonstrateInsertion();
        demonstrateDeletion();
        demonstrateReverse();
        demonstrateCycleDetection();
        demonstrateRealisticCaseStudy();
        demonstrateFailureHandling();
        demonstrateEdgeCases();
        demonstrateComplexity();

        std::cout << "\nAll C++ demonstrations completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Unexpected failure: "
                  << error.what()
                  << '\n';

        return 1;
    }
}
