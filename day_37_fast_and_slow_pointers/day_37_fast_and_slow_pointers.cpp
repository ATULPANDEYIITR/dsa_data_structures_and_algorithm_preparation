#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <unordered_set>
#include <vector>

/*
 * Fast and Slow Pointers
 *
 * Technical case study:
 * A stream-processing service stores events in a singly linked structure.
 * A corrupted event chain may accidentally point backward, creating a cycle.
 *
 * The service needs to:
 * - locate the midpoint for partitioning work,
 * - detect cycles without allocating a visited-node table,
 * - identify the first node in the cycle,
 * - measure the cycle,
 * - compare the constant-space Floyd algorithm with a hash-set approach.
 *
 * C++17 is sufficient.
 */

struct EventNode {
    int sequence;
    std::string event;
    EventNode* next = nullptr;
};

class EventChain {
public:
    explicit EventChain(const std::vector<std::string>& events) {
        EventNode* previous = nullptr;

        for (std::size_t index = 0; index < events.size(); ++index) {
            nodes_.push_back(
                std::make_unique<EventNode>(
                    EventNode{
                        static_cast<int>(index + 1),
                        events[index],
                        nullptr
                    }
                )
            );

            EventNode* current = nodes_.back().get();

            if (previous != nullptr) {
                previous->next = current;
            } else {
                head_ = current;
            }

            previous = current;
        }
    }

    EventNode* head() const {
        return head_;
    }

    EventNode* nodeAt(std::size_t index) const {
        if (index >= nodes_.size()) {
            return nullptr;
        }

        return nodes_[index].get();
    }

    std::size_t size() const {
        return nodes_.size();
    }

    void connectTailTo(std::size_t index) {
        if (head_ == nullptr) {
            throw std::invalid_argument("Cannot create a cycle in an empty chain.");
        }

        EventNode* target = nodeAt(index);

        if (target == nullptr) {
            throw std::out_of_range("Cycle target is outside the chain.");
        }

        EventNode* tail = head_;

        while (tail->next != nullptr) {
            tail = tail->next;
        }

        tail->next = target;
    }

private:
    std::vector<std::unique_ptr<EventNode>> nodes_;
    EventNode* head_ = nullptr;
};

EventNode* findSecondMiddle(EventNode* head) {
    EventNode* slow = head;
    EventNode* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    return slow;
}

EventNode* findFirstMiddle(EventNode* head) {
    if (head == nullptr) {
        return nullptr;
    }

    EventNode* slow = head;
    EventNode* fast = head;

    while (fast->next != nullptr && fast->next->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    return slow;
}

EventNode* floydMeetingPoint(EventNode* head) {
    EventNode* slow = head;
    EventNode* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            return slow;
        }
    }

    return nullptr;
}

bool hasCycle(EventNode* head) {
    return floydMeetingPoint(head) != nullptr;
}

EventNode* findCycleEntry(EventNode* head) {
    EventNode* meeting = floydMeetingPoint(head);

    if (meeting == nullptr) {
        return nullptr;
    }

    /*
     * Floyd's second phase:
     * one pointer starts at the head while the other starts at the meeting
     * point. Equal one-step movement causes them to meet at the cycle entry.
     */
    EventNode* left = head;
    EventNode* right = meeting;

    while (left != right) {
        left = left->next;
        right = right->next;
    }

    return left;
}

std::size_t cycleLength(EventNode* head) {
    EventNode* entry = findCycleEntry(head);

    if (entry == nullptr) {
        return 0;
    }

    std::size_t length = 1;
    EventNode* current = entry->next;

    while (current != entry) {
        current = current->next;
        ++length;
    }

    return length;
}

std::optional<std::size_t> distanceToCycleEntry(EventNode* head) {
    EventNode* entry = findCycleEntry(head);

    if (entry == nullptr) {
        return std::nullopt;
    }

    std::size_t distance = 0;
    EventNode* current = head;

    while (current != entry) {
        current = current->next;
        ++distance;
    }

    return distance;
}

/*
 * This detector is intentionally included as a comparison.
 * It is straightforward, but every visited pointer must be retained.
 * Therefore it uses O(n) auxiliary memory instead of Floyd's O(1).
 */
bool hasCycleWithVisitedSet(EventNode* head) {
    std::unordered_set<EventNode*> visited;

    EventNode* current = head;

    while (current != nullptr) {
        if (!visited.insert(current).second) {
            return true;
        }

        current = current->next;
    }

    return false;
}

std::string preview(EventNode* head, std::size_t limit = 12) {
    std::string result;
    EventNode* current = head;

    for (std::size_t count = 0; count < limit; ++count) {
        if (current == nullptr) {
            break;
        }

        if (!result.empty()) {
            result += " -> ";
        }

        result += std::to_string(current->sequence);
        result += ":";
        result += current->event;

        current = current->next;
    }

    if (current != nullptr) {
        result += " -> ...";
    }

    return result.empty() ? "empty" : result;
}

void demonstrateMiddleDetection() {
    std::cout << "\n=== Middle Detection ===\n";

    EventChain chain({
        "login",
        "validate",
        "authorize",
        "load",
        "transform",
        "persist",
        "audit"
    });

    EventNode* firstMiddle = findFirstMiddle(chain.head());
    EventNode* secondMiddle = findSecondMiddle(chain.head());

    std::cout << "Chain: " << preview(chain.head()) << "\n";
    std::cout << "First middle: "
              << firstMiddle->event << "\n";
    std::cout << "Second middle: "
              << secondMiddle->event << "\n";

    /*
     * The second-middle convention is useful when recursively splitting a
     * linked list because it leaves the later half starting at slow.
     */
}

void demonstrateCycleGovernanceCase() {
    std::cout << "\n=== Event Chain Integrity Case Study ===\n";

    EventChain healthy({
        "ingest",
        "validate",
        "normalize",
        "enrich",
        "persist"
    });

    std::cout << "Healthy chain: " << preview(healthy.head()) << "\n";
    std::cout << "Floyd detects cycle: "
              << std::boolalpha
              << hasCycle(healthy.head()) << "\n";

    EventChain corrupted({
        "ingest",
        "validate",
        "normalize",
        "enrich",
        "persist",
        "publish"
    });

    /*
     * The last event accidentally points back to "normalize".
     * The resulting structure contains a tail followed by a cycle.
     */
    corrupted.connectTailTo(2);

    std::cout << "Corrupted chain preview: "
              << preview(corrupted.head()) << "\n";

    EventNode* meeting = floydMeetingPoint(corrupted.head());
    EventNode* entry = findCycleEntry(corrupted.head());

    std::cout << "Cycle detected: "
              << hasCycle(corrupted.head()) << "\n";
    std::cout << "Floyd meeting node: "
              << meeting->event << "\n";
    std::cout << "Cycle entry: "
              << entry->event << "\n";
    std::cout << "Cycle length: "
              << cycleLength(corrupted.head()) << "\n";

    const auto distance = distanceToCycleEntry(corrupted.head());

    if (distance.has_value()) {
        std::cout << "Nodes before cycle: "
                  << *distance << "\n";
    }

    std::cout << "Hash-set detector agrees: "
              << hasCycleWithVisitedSet(corrupted.head()) << "\n";
}

void demonstrateSelfCycle() {
    std::cout << "\n=== Self-Cycle Edge Case ===\n";

    EventNode node{
        99,
        "retry",
        nullptr
    };

    node.next = &node;

    std::cout << "Cycle detected: "
              << hasCycle(&node) << "\n";

    EventNode* entry = findCycleEntry(&node);

    std::cout << "Cycle entry: "
              << entry->event << "\n";

    std::cout << "Cycle length: "
              << cycleLength(&node) << "\n";
}

void demonstrateDuplicateValues() {
    std::cout << "\n=== Pointer Identity Versus Equal Data ===\n";

    EventNode first{1, "duplicate", nullptr};
    EventNode second{2, "duplicate", nullptr};

    first.next = &second;
    second.next = &first;

    /*
     * The two nodes contain equal event names, but they are different
     * objects. Floyd compares addresses/pointers, not payload equality.
     */
    std::cout << "Payloads equal: "
              << (first.event == second.event) << "\n";
    std::cout << "Node addresses equal: "
              << (&first == &second) << "\n";
    std::cout << "Cycle detected: "
              << hasCycle(&first) << "\n";
    std::cout << "Entry sequence: "
              << findCycleEntry(&first)->sequence << "\n";
}

void demonstrateComplexity() {
    std::cout << "\n=== Complexity and Design Trade-Off ===\n";

    std::cout << "Middle detection: O(n) time, O(1) auxiliary space.\n";
    std::cout << "Floyd cycle detection: O(n) time, O(1) auxiliary space.\n";
    std::cout << "Cycle-entry detection: O(n) time, O(1) auxiliary space.\n";
    std::cout << "Visited-set detection: O(n) time, O(n) auxiliary space.\n";

    /*
     * Floyd is particularly useful when the linked structure can be large
     * and memory consumption must not grow with the number of visited nodes.
     */
}

void runAssertions() {
    EventChain chain({
        "A",
        "B",
        "C",
        "D"
    });

    assert(findFirstMiddle(chain.head())->event == "B");
    assert(findSecondMiddle(chain.head())->event == "C");
    assert(!hasCycle(chain.head()));

    EventChain cyclic({
        "A",
        "B",
        "C",
        "D",
        "E"
    });

    cyclic.connectTailTo(2);

    EventNode* expectedEntry = cyclic.nodeAt(2);

    assert(hasCycle(cyclic.head()));
    assert(findCycleEntry(cyclic.head()) == expectedEntry);
    assert(cycleLength(cyclic.head()) == 3);
    assert(distanceToCycleEntry(cyclic.head()).value() == 2);

    EventNode single{
        1,
        "single",
        nullptr
    };

    assert(findSecondMiddle(&single) == &single);
    assert(!hasCycle(&single));

    single.next = &single;

    assert(hasCycle(&single));
    assert(findCycleEntry(&single) == &single);
    assert(cycleLength(&single) == 1);

    std::cout << "\nAll C++ assertions passed.\n";
}

int main() {
    std::cout << "FAST AND SLOW POINTERS\n";
    std::cout << "=====================\n";

    demonstrateMiddleDetection();
    demonstrateCycleGovernanceCase();
    demonstrateSelfCycle();
    demonstrateDuplicateValues();
    demonstrateComplexity();
    runAssertions();

    return 0;
}
