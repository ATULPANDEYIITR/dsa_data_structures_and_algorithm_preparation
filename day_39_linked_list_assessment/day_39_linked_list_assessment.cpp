#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

/*
 * Case study: a telemetry ingestion service stores ordered event records in
 * linked queues. It must detect accidental cycles, combine sorted event
 * streams, and restructure queues without copying event nodes.
 *
 * The same pointer operations are useful in memory-sensitive streaming
 * systems, intrusive collections, and queue-processing infrastructure.
 */

struct Node {
    int timestamp;
    string event;
    Node* next;

    Node(int time, string label)
        : timestamp(time), event(std::move(label)), next(nullptr) {}
};

Node* buildList(const vector<pair<int, string>>& records) {
    Node dummy(0, "");
    Node* tail = &dummy;

    for (const auto& record : records) {
        tail->next = new Node(record.first, record.second);
        tail = tail->next;
    }
    return dummy.next;
}

bool hasCycle(const Node* head) {
    const Node* slow = head;
    const Node* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;
}

void requireAcyclic(const Node* head) {
    if (hasCycle(head)) {
        throw invalid_argument("Operation requires an acyclic queue.");
    }
}

vector<pair<int, string>> snapshot(const Node* head) {
    requireAcyclic(head);
    vector<pair<int, string>> records;

    for (const Node* current = head; current != nullptr;
         current = current->next) {
        records.emplace_back(current->timestamp, current->event);
    }
    return records;
}

void destroyList(Node* head) {
    // Never call this on a cyclic list; callers must repair or break cycles.
    while (head != nullptr) {
        Node* following = head->next;
        delete head;
        head = following;
    }
}

void requireDisjoint(const Node* first, const Node* second) {
    unordered_set<const Node*> addresses;

    for (const Node* current = first; current != nullptr;
         current = current->next) {
        addresses.insert(current);
    }

    for (const Node* current = second; current != nullptr;
         current = current->next) {
        if (addresses.count(current)) {
            throw invalid_argument("Input queues share a node.");
        }
    }
}

Node* reverseList(Node* head) {
    requireAcyclic(head);

    Node* previous = nullptr;
    Node* current = head;

    while (current != nullptr) {
        Node* following = current->next;
        current->next = previous;
        previous = current;
        current = following;
    }
    return previous;
}

Node* mergeTwoSorted(Node* first, Node* second) {
    requireAcyclic(first);
    requireAcyclic(second);
    requireDisjoint(first, second);

    Node dummy(0, "");
    Node* tail = &dummy;

    while (first != nullptr && second != nullptr) {
        if (first->timestamp <= second->timestamp) {
            tail->next = first;
            first = first->next;
        } else {
            tail->next = second;
            second = second->next;
        }
        tail = tail->next;
    }

    tail->next = first != nullptr ? first : second;
    return dummy.next;
}

Node* removeNthFromEnd(Node* head, size_t n) {
    if (n == 0) throw invalid_argument("n must be positive.");
    requireAcyclic(head);

    Node dummy(0, "");
    dummy.next = head;
    Node* fast = &dummy;
    Node* slow = &dummy;

    for (size_t i = 0; i < n; ++i) {
        fast = fast->next;
        if (fast == nullptr) {
            throw out_of_range("n exceeds queue length.");
        }
    }

    while (fast->next != nullptr) {
        fast = fast->next;
        slow = slow->next;
    }

    Node* removed = slow->next;
    slow->next = removed->next;
    removed->next = nullptr;
    delete removed;
    return dummy.next;
}

Node* intersectionNode(Node* first, Node* second) {
    requireAcyclic(first);
    requireAcyclic(second);

    Node* left = first;
    Node* right = second;

    while (left != right) {
        left = left == nullptr ? second : left->next;
        right = right == nullptr ? first : right->next;
    }
    return left;
}

bool isPalindrome(Node* head) {
    requireAcyclic(head);
    if (head == nullptr || head->next == nullptr) return true;

    Node* slow = head;
    Node* fast = head;

    while (fast->next != nullptr && fast->next->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    Node* reversed = reverseList(slow->next);
    slow->next = reversed;

    bool matches = true;
    Node* left = head;
    Node* right = reversed;

    while (right != nullptr) {
        if (left->timestamp != right->timestamp ||
            left->event != right->event) {
            matches = false;
            break;
        }
        left = left->next;
        right = right->next;
    }

    // Restore the input queue before returning.
    slow->next = reverseList(reversed);
    return matches;
}

Node* reorderList(Node* head) {
    requireAcyclic(head);
    if (head == nullptr || head->next == nullptr) return head;

    Node* slow = head;
    Node* fast = head;

    while (fast->next != nullptr && fast->next->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    Node* second = slow->next;
    slow->next = nullptr;
    second = reverseList(second);

    Node* first = head;
    while (second != nullptr) {
        Node* firstNext = first->next;
        Node* secondNext = second->next;
        first->next = second;
        second->next = firstNext;
        first = firstNext;
        second = secondNext;
    }

    return head;
}

Node* mergeKSorted(vector<Node*> lists) {
    struct Entry {
        int timestamp;
        size_t sequence;
        Node* node;
    };

    struct Later {
        bool operator()(const Entry& left, const Entry& right) const {
            if (left.timestamp != right.timestamp) {
                return left.timestamp > right.timestamp;
            }
            return left.sequence > right.sequence;
        }
    };

    unordered_set<Node*> seen;
    for (Node* head : lists) {
        requireAcyclic(head);
        for (Node* current = head; current != nullptr;
             current = current->next) {
            if (!seen.insert(current).second) {
                throw invalid_argument("Input queues share a node.");
            }
        }
    }

    priority_queue<Entry, vector<Entry>, Later> heap;
    size_t sequence = 0;

    for (Node* head : lists) {
        if (head != nullptr) {
            heap.push({head->timestamp, sequence++, head});
        }
    }

    Node dummy(0, "");
    Node* tail = &dummy;

    while (!heap.empty()) {
        Entry entry = heap.top();
        heap.pop();

        Node* current = entry.node;
        Node* following = current->next;

        tail->next = current;
        tail = current;

        if (following != nullptr) {
            heap.push({following->timestamp, sequence++, following});
        }
    }

    tail->next = nullptr;
    return dummy.next;
}

void printQueue(const string& title, const Node* head) {
    cout << title << ": ";
    for (const auto& record : snapshot(head)) {
        cout << "(" << record.first << ", " << record.second << ") ";
    }
    cout << '\n';
}

int main() {
    try {
        Node* reversed = reverseList(buildList({
            {10, "received"}, {20, "validated"}, {30, "stored"}
        }));
        printQueue("Reverse operation", reversed);
        destroyList(reversed);

        Node* merged = mergeTwoSorted(
            buildList({{10, "A"}, {30, "C"}}),
            buildList({{20, "B"}, {40, "D"}})
        );
        printQueue("Two-stream merge", merged);
        destroyList(merged);

        Node* removal = buildList({
            {10, "A"}, {20, "B"}, {30, "C"}, {40, "D"}
        });
        removal = removeNthFromEnd(removal, 2);
        printQueue("After removal", removal);
        destroyList(removal);

        Node* palindrome = buildList({
            {1, "event"}, {2, "event"}, {1, "event"}
        });
        cout << "Symmetric queue: "
             << (isPalindrome(palindrome) ? "yes" : "no") << '\n';
        destroyList(palindrome);

        Node* reordered = reorderList(buildList({
            {1, "first"}, {2, "second"}, {3, "third"},
            {4, "fourth"}, {5, "fifth"}
        }));
        printQueue("Reordered queue", reordered);
        destroyList(reordered);

        Node* kMerged = mergeKSorted({
            buildList({{1, "A1"}, {4, "A4"}, {7, "A7"}}),
            buildList({{2, "B2"}, {5, "B5"}, {8, "B8"}}),
            buildList({{3, "C3"}, {6, "C6"}, {9, "C9"}})
        });
        printQueue("K-stream merge", kMerged);
        destroyList(kMerged);

        Node* cycle = buildList({{1, "X"}, {2, "Y"}, {3, "Z"}});
        Node* tail = cycle;
        while (tail->next != nullptr) tail = tail->next;
        tail->next = cycle->next;

        cout << "Cycle detected: " << (hasCycle(cycle) ? "yes" : "no")
             << '\n';

        // Break the deliberately created cycle before releasing its memory.
        tail->next = nullptr;
        destroyList(cycle);

        Node* shared = buildList({{90, "shared"}, {100, "shared"}});
        Node first(10, "left");
        Node second(20, "right");
        first.next = shared;
        second.next = shared;

        assert(intersectionNode(&first, &second) == shared);
        cout << "Intersection identified by node address: yes\n";

        // The stack nodes own no memory; only the shared heap chain is freed.
        first.next = nullptr;
        second.next = nullptr;
        destroyList(shared);

        cout << "Case study completed successfully.\n";
    } catch (const exception& error) {
        cerr << "Processing failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
