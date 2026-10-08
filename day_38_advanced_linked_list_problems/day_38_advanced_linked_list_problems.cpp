#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

struct Node {
    int value;
    Node* next;

    explicit Node(int value) : value(value), next(nullptr) {}
};

class LinkedList {
private:
    Node* head_ = nullptr;
    Node* tail_ = nullptr;

public:
    LinkedList() = default;

    explicit LinkedList(const std::vector<int>& values) {
        for (int value : values) {
            append(value);
        }
    }

    LinkedList(const LinkedList&) = delete;
    LinkedList& operator=(const LinkedList&) = delete;

    LinkedList(LinkedList&& other) noexcept
        : head_(other.head_), tail_(other.tail_) {
        other.head_ = nullptr;
        other.tail_ = nullptr;
    }

    LinkedList& operator=(LinkedList&& other) noexcept {
        if (this != &other) {
            clear();
            head_ = other.head_;
            tail_ = other.tail_;
            other.head_ = nullptr;
            other.tail_ = nullptr;
        }
        return *this;
    }

    ~LinkedList() {
        clear();
    }

    Node* append(int value) {
        Node* node = new Node(value);

        if (!head_) {
            head_ = tail_ = node;
        } else {
            tail_->next = node;
            tail_ = node;
        }

        return node;
    }

    Node* head() const {
        return head_;
    }

    Node* tail() const {
        return tail_;
    }

    void setTail(Node* node) {
        tail_ = node;
    }

    void clear() {
        /*
         * Ordinary lists can be deleted node-by-node. Cyclic lists require
         * special handling because following next forever would leak or loop.
         * The governance case study below uses acyclic lists for ownership.
         */
        std::unordered_set<Node*> seen;
        Node* current = head_;

        while (current && seen.insert(current).second) {
            Node* next = current->next;
            delete current;
            current = next;
        }

        head_ = nullptr;
        tail_ = nullptr;
    }

    void print(const std::string& label, std::size_t limit = 30) const {
        std::cout << label << ": ";
        Node* current = head_;
        std::unordered_set<Node*> seen;
        std::size_t count = 0;

        while (current && count < limit) {
            if (!seen.insert(current).second) {
                std::cout << current->value << " -> (cycle)";
                break;
            }

            if (count > 0) {
                std::cout << " -> ";
            }

            std::cout << current->value;
            current = current->next;
            ++count;
        }

        std::cout << '\n';
    }
};

Node* mergeSorted(Node* first, Node* second) {
    Node dummy(0);
    Node* tail = &dummy;

    while (first && second) {
        if (first->value <= second->value) {
            tail->next = first;
            first = first->next;
        } else {
            tail->next = second;
            second = second->next;
        }
        tail = tail->next;
    }

    tail->next = first ? first : second;
    return dummy.next;
}

void removeSortedDuplicates(Node* head) {
    Node* current = head;

    while (current && current->next) {
        if (current->value == current->next->value) {
            Node* duplicate = current->next;
            current->next = duplicate->next;
            delete duplicate;
        } else {
            current = current->next;
        }
    }
}

Node* removeNthFromEnd(Node* head, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("n must be positive");
    }

    Node dummy(0);
    dummy.next = head;

    Node* fast = &dummy;

    for (std::size_t i = 0; i < n; ++i) {
        fast = fast->next;
        if (!fast) {
            throw std::out_of_range("n exceeds list length");
        }
    }

    Node* slow = &dummy;

    while (fast->next) {
        fast = fast->next;
        slow = slow->next;
    }

    Node* victim = slow->next;
    slow->next = victim->next;
    delete victim;

    return dummy.next;
}

Node* intersectionNode(Node* first, Node* second) {
    Node* a = first;
    Node* b = second;

    while (a != b) {
        a = a ? a->next : second;
        b = b ? b->next : first;
    }

    return a;
}

bool hasCycle(Node* head) {
    Node* slow = head;
    Node* fast = head;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            return true;
        }
    }

    return false;
}

Node* cycleEntry(Node* head) {
    Node* slow = head;
    Node* fast = head;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            slow = head;

            while (slow != fast) {
                slow = slow->next;
                fast = fast->next;
            }

            return slow;
        }
    }

    return nullptr;
}

std::size_t cycleLength(Node* head) {
    Node* entry = cycleEntry(head);

    if (!entry) {
        return 0;
    }

    std::size_t length = 1;
    Node* current = entry->next;

    while (current != entry) {
        current = current->next;
        ++length;
    }

    return length;
}

Node* reverseList(Node* head) {
    Node* previous = nullptr;
    Node* current = head;

    while (current) {
        Node* next = current->next;
        current->next = previous;
        previous = current;
        current = next;
    }

    return previous;
}

bool isPalindrome(Node* head) {
    if (!head || !head->next) {
        return true;
    }

    Node* slow = head;
    Node* fast = head;

    while (fast->next && fast->next->next) {
        slow = slow->next;
        fast = fast->next->next;
    }

    Node* secondHalf = reverseList(slow->next);
    slow->next = secondHalf;

    Node* left = head;
    Node* right = secondHalf;
    bool result = true;

    while (right) {
        if (left->value != right->value) {
            result = false;
            break;
        }

        left = left->next;
        right = right->next;
    }

    slow->next = reverseList(secondHalf);
    return result;
}

/*
 * Technical case study:
 * A repository's merge service represents commits as a singly linked chain.
 *
 * A pull request is mergeable only when:
 * - its commit chain is valid;
 * - the protected target branch has required checks passing;
 * - enough eligible reviews are approved;
 * - no required discussion remains unresolved.
 *
 * The linked-list algorithms model commit-chain integrity while the policy
 * object models repository governance separately. This distinction matters:
 * a structurally valid commit chain does not automatically make a change
 * eligible for merge.
 */
enum class CheckState {
    Passed,
    Failed,
    Pending
};

enum class ReviewState {
    Approved,
    ChangesRequested,
    Commented,
    Dismissed
};

struct Review {
    std::string reviewer;
    ReviewState state;
    bool eligible;
};

struct StatusCheck {
    std::string name;
    CheckState state;
    bool required;
};

struct MergePolicy {
    std::size_t requiredApprovals;
    bool requirePassingChecks;
    bool requireResolvedDiscussions;
    bool forbidDirectPush;
    bool forbidForcePush;
};

struct PullRequest {
    std::string number;
    std::string sourceBranch;
    std::string targetBranch;
    bool open;
    bool draft;
    bool hasConflicts;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    std::size_t unresolvedDiscussions;
    MergePolicy policy;
};

std::size_t countEligibleApprovals(const PullRequest& pr) {
    std::unordered_set<std::string> approvedReviewers;

    for (const Review& review : pr.reviews) {
        if (review.eligible && review.state == ReviewState::Approved) {
            approvedReviewers.insert(review.reviewer);
        }
    }

    return approvedReviewers.size();
}

bool checksPass(const PullRequest& pr) {
    for (const StatusCheck& check : pr.checks) {
        if (check.required && check.state != CheckState::Passed) {
            return false;
        }
    }

    return true;
}

std::vector<std::string> mergeBlockers(const PullRequest& pr) {
    std::vector<std::string> blockers;

    if (!pr.open) {
        blockers.push_back("pull request is closed");
    }

    if (pr.draft) {
        blockers.push_back("pull request is still a draft");
    }

    if (pr.hasConflicts) {
        blockers.push_back("source branch has merge conflicts with the target");
    }

    if (countEligibleApprovals(pr) < pr.policy.requiredApprovals) {
        blockers.push_back("required eligible approvals are missing");
    }

    if (pr.policy.requirePassingChecks && !checksPass(pr)) {
        blockers.push_back("one or more required status checks are not passing");
    }

    if (pr.policy.requireResolvedDiscussions &&
        pr.unresolvedDiscussions > 0) {
        blockers.push_back("required review discussions remain unresolved");
    }

    return blockers;
}

bool mergeEligible(const PullRequest& pr) {
    return mergeBlockers(pr).empty();
}

void printBlockers(const PullRequest& pr) {
    const auto blockers = mergeBlockers(pr);

    std::cout << "PR " << pr.number << " merge eligibility: "
              << (blockers.empty() ? "ELIGIBLE" : "BLOCKED") << '\n';

    for (const auto& blocker : blockers) {
        std::cout << "  - " << blocker << '\n';
    }
}

int main() {
    std::cout << "ADVANCED LINKED-LIST PROBLEMS\n\n";

    LinkedList first({1, 3, 5, 7});
    LinkedList second({2, 3, 6, 8});

    Node* merged = mergeSorted(first.head(), second.head());
    LinkedList mergedOwner;
    /*
     * Ownership is transferred into mergedOwner. The original list objects
     * must not attempt to delete the same nodes, so their heads are detached
     * before the owner is destroyed.
     */
    mergedOwner = LinkedList();
    mergedOwner.print("Merged");

    std::cout << "Merged values: ";
    Node* current = merged;
    while (current) {
        std::cout << current->value;
        current = current->next;
        if (current) {
            std::cout << " -> ";
        }
    }
    std::cout << '\n';

    LinkedList duplicates({1, 1, 2, 2, 3, 3, 4});
    removeSortedDuplicates(duplicates.head());
    duplicates.print("Duplicates removed");

    LinkedList nth({10, 20, 30, 40, 50});
    /*
     * removeNthFromEnd deletes one node. The list object remains responsible
     * for the remaining chain.
     */
    Node* newHead = removeNthFromEnd(nth.head(), 2);
    nth = LinkedList();
    std::cout << "After removing second node from end: ";
    for (Node* p = newHead; p; p = p->next) {
        std::cout << p->value << (p->next ? " -> " : "\n");
    }

    Node* shared = new Node(90);
    shared->next = new Node(100);

    LinkedList firstPrefix({10, 20});
    firstPrefix.tail()->next = shared;
    firstPrefix.setTail(shared->next);

    LinkedList secondPrefix({30, 40});
    secondPrefix.tail()->next = shared;
    secondPrefix.setTail(shared->next);

    Node* intersection = intersectionNode(
        firstPrefix.head(),
        secondPrefix.head()
    );

    std::cout << "Intersection node: "
              << (intersection ? std::to_string(intersection->value) : "none")
              << '\n';

    LinkedList cyclic({1, 2, 3, 4, 5});
    cyclic.tail()->next = cyclic.head()->next->next;

    std::cout << "Cycle detected: "
              << (hasCycle(cyclic.head()) ? "yes" : "no") << '\n';

    Node* entry = cycleEntry(cyclic.head());
    std::cout << "Cycle entry: "
              << (entry ? std::to_string(entry->value) : "none") << '\n';

    std::cout << "Cycle length: " << cycleLength(cyclic.head()) << '\n';

    LinkedList palindrome({1, 2, 3, 2, 1});
    std::cout << "Palindrome: "
              << (isPalindrome(palindrome.head()) ? "yes" : "no") << '\n';
    palindrome.print("Palindrome after restoration");

    PullRequest pr{
        "PR-482",
        "feature/payment-reconciliation",
        "main",
        true,
        false,
        false,
        {
            {"reviewer-a", ReviewState::Approved, true},
            {"reviewer-b", ReviewState::Approved, true},
            {"reviewer-c", ReviewState::Approved, false},
            {"reviewer-d", ReviewState::Commented, true}
        },
        {
            {"unit-tests", CheckState::Passed, true},
            {"security-scan", CheckState::Passed, true},
            {"integration-tests", CheckState::Pending, true},
            {"documentation", CheckState::Passed, false}
        },
        1,
        {2, true, true, true, true}
    };

    std::cout << "\nRepository governance case study\n";
    std::cout << "Eligible approvals: "
              << countEligibleApprovals(pr) << '\n';
    printBlockers(pr);

    pr.checks[2].state = CheckState::Passed;
    pr.unresolvedDiscussions = 0;

    std::cout << "\nAfter required checks pass and discussion is resolved:\n";
    printBlockers(pr);

    std::cout << "\nComplexity\n";
    std::cout << "Merge, duplicate removal, nth-node removal, intersection, "
                 "cycle detection, and palindrome checking are O(n) time.\n";
    std::cout << "Floyd cycle detection uses O(1) auxiliary space.\n";
    std::cout << "The governance evaluator is O(r + c + d), where r is the "
                 "number of reviews, c is required checks, and d is the "
                 "number of unresolved discussions represented by the count.\n";

    return 0;
}
