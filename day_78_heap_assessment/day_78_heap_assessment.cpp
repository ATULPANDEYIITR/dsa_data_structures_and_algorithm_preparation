#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

class HeapError : public runtime_error {
public:
    explicit HeapError(const string& message)
        : runtime_error(message) {}
};

enum class Priority {
    Critical = 0,
    High = 1,
    Normal = 2,
    Low = 3
};

enum class ReviewState {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled
};

struct StatusCheck {
    string name;
    bool required;
    bool passed;
};

struct Review {
    string reviewer;
    bool eligible;
    bool approved;
    bool stale;
    bool dismissed;
    bool conversationResolved;
};

struct PullRequest {
    int id;
    string title;
    string sourceBranch;
    string targetBranch;

    bool draft = false;
    bool merged = false;
    bool closed = false;
    bool hasMergeConflict = false;
    bool baseSynchronized = true;

    vector<Review> reviews;
    vector<StatusCheck> checks;
};

struct BranchProtection {
    string branch;

    int requiredApprovals = 2;
    bool requireStatusChecks = true;
    bool requireResolvedConversations = true;
    bool requireLinearHistory = true;
    bool allowDirectPush = false;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool administratorBypass = false;
};

struct MergeDecision {
    bool eligible;
    vector<string> reasons;
};

class GovernanceEngine {
private:
    unordered_map<string, BranchProtection> policies;

public:
    void addPolicy(const BranchProtection& policy) {
        if (policy.branch.empty()) {
            throw HeapError("Branch name cannot be empty.");
        }

        if (policy.requiredApprovals < 0) {
            throw HeapError("Invalid approval requirement.");
        }

        policies[policy.branch] = policy;
    }

    MergeDecision evaluate(const PullRequest& pr) const {
        MergeDecision decision{true, {}};

        if (pr.merged || pr.closed) {
            decision.reasons.push_back(
                "Pull Request is already closed or merged."
            );
        }

        if (pr.draft) {
            decision.reasons.push_back(
                "Draft Pull Requests cannot be merged."
            );
        }

        if (pr.hasMergeConflict) {
            decision.reasons.push_back(
                "Merge conflicts must be resolved."
            );
        }

        if (!pr.baseSynchronized) {
            decision.reasons.push_back(
                "Source branch must be synchronized."
            );
        }

        auto policyIterator = policies.find(pr.targetBranch);

        if (policyIterator == policies.end()) {
            decision.reasons.push_back(
                "No target branch protection policy exists."
            );

            decision.eligible = false;
            return decision;
        }

        const BranchProtection& policy = policyIterator->second;

        unordered_set<string> approvedReviewers;

        int approvalCount = 0;

        for (const auto& review : pr.reviews) {
            if (
                review.eligible &&
                review.approved &&
                !review.stale &&
                !review.dismissed
            ) {
                approvedReviewers.insert(review.reviewer);
            }
        }

        approvalCount = static_cast<int>(
            approvedReviewers.size()
        );

        if (approvalCount < policy.requiredApprovals) {
            decision.reasons.push_back(
                "Insufficient valid approvals."
            );
        }

        if (policy.requireStatusChecks) {
            for (const auto& check : pr.checks) {
                if (check.required && !check.passed) {
                    decision.reasons.push_back(
                        "Required status check failed: " + check.name
                    );
                }
            }

            bool hasRequiredCheck = any_of(
                pr.checks.begin(),
                pr.checks.end(),
                [](const StatusCheck& check) {
                    return check.required;
                }
            );

            if (!hasRequiredCheck) {
                decision.reasons.push_back(
                    "Required status checks are not configured."
                );
            }
        }

        if (policy.requireResolvedConversations) {
            for (const auto& review : pr.reviews) {
                if (!review.conversationResolved) {
                    decision.reasons.push_back(
                        "Unresolved review conversation: " +
                        review.reviewer
                    );
                }
            }
        }

        decision.eligible = decision.reasons.empty();

        return decision;
    }

    bool merge(PullRequest& pr) const {
        const MergeDecision decision = evaluate(pr);

        if (!decision.eligible) {
            return false;
        }

        pr.merged = true;
        pr.closed = true;

        return true;
    }

    bool directPushAllowed(const string& branch) const {
        auto iterator = policies.find(branch);

        return iterator != policies.end() &&
               iterator->second.allowDirectPush;
    }

    bool forcePushAllowed(const string& branch) const {
        auto iterator = policies.find(branch);

        return iterator != policies.end() &&
               iterator->second.allowForcePush;
    }
};

struct Task {
    int id;
    Priority priority;
    string description;
    int sequence;
};

struct TaskComparator {
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority) {
            return static_cast<int>(a.priority) >
                   static_cast<int>(b.priority);
        }

        return a.sequence > b.sequence;
    }
};

class TaskScheduler {
private:
    priority_queue<
        Task,
        vector<Task>,
        TaskComparator
    > tasks;

    unordered_set<int> identifiers;
    int sequence = 0;

public:
    void submit(int id, Priority priority, const string& description) {
        if (id < 0 || identifiers.count(id)) {
            throw HeapError("Invalid or duplicate task ID.");
        }

        if (description.empty()) {
            throw HeapError("Task description is required.");
        }

        identifiers.insert(id);

        tasks.push({
            id,
            priority,
            description,
            sequence++
        });
    }

    Task executeNext() {
        if (tasks.empty()) {
            throw HeapError("No pending tasks.");
        }

        Task result = tasks.top();
        tasks.pop();

        return result;
    }

    bool empty() const {
        return tasks.empty();
    }
};

class HeapAlgorithms {
public:
    static int kthLargest(const vector<int>& nums, int k) {
        if (k < 1 || k > static_cast<int>(nums.size())) {
            throw HeapError("Invalid k.");
        }

        priority_queue<
            int,
            vector<int>,
            greater<int>
        > heap;

        for (int value : nums) {
            heap.push(value);

            if (static_cast<int>(heap.size()) > k) {
                heap.pop();
            }
        }

        return heap.top();
    }

    static vector<int> topKFrequent(
        const vector<int>& nums,
        int k
    ) {
        unordered_map<int, int> frequencies;

        for (int value : nums) {
            frequencies[value]++;
        }

        if (k < 0 || k > static_cast<int>(frequencies.size())) {
            throw HeapError("Invalid k.");
        }

        using Entry = pair<int, int>;

        priority_queue<
            Entry,
            vector<Entry>,
            greater<Entry>
        > heap;

        for (const auto& [value, frequency] : frequencies) {
            heap.push({frequency, -value});

            if (static_cast<int>(heap.size()) > k) {
                heap.pop();
            }
        }

        vector<int> result;

        while (!heap.empty()) {
            result.push_back(-heap.top().second);
            heap.pop();
        }

        sort(
            result.begin(),
            result.end(),
            [&](int a, int b) {
                if (frequencies[a] != frequencies[b]) {
                    return frequencies[a] > frequencies[b];
                }

                return a < b;
            }
        );

        return result;
    }

    static vector<int> mergeKSortedArrays(
        const vector<vector<int>>& arrays
    ) {
        using Entry = tuple<int, int, int>;

        priority_queue<
            Entry,
            vector<Entry>,
            greater<Entry>
        > heap;

        for (int i = 0; i < static_cast<int>(arrays.size()); i++) {
            const auto& array = arrays[i];

            if (!is_sorted(array.begin(), array.end())) {
                throw HeapError("Input array is not sorted.");
            }

            if (!array.empty()) {
                heap.push({array[0], i, 0});
            }
        }

        vector<int> result;

        while (!heap.empty()) {
            auto [value, arrayIndex, elementIndex] = heap.top();
            heap.pop();

            result.push_back(value);

            int nextIndex = elementIndex + 1;

            if (nextIndex < static_cast<int>(arrays[arrayIndex].size())) {
                heap.push({
                    arrays[arrayIndex][nextIndex],
                    arrayIndex,
                    nextIndex
                });
            }
        }

        return result;
    }

    static long long connectRopes(vector<int> lengths) {
        if (any_of(
            lengths.begin(),
            lengths.end(),
            [](int value) { return value < 0; }
        )) {
            throw HeapError("Negative rope length.");
        }

        priority_queue<
            long long,
            vector<long long>,
            greater<long long>
        > heap(lengths.begin(), lengths.end());

        long long cost = 0;

        while (heap.size() > 1) {
            long long combined = heap.top();
            heap.pop();

            combined += heap.top();
            heap.pop();

            if (
                cost > numeric_limits<long long>::max() - combined
            ) {
                throw HeapError("Rope cost overflow.");
            }

            cost += combined;
            heap.push(combined);
        }

        return cost;
    }

    static int minimumMeetingRooms(
        vector<pair<int, int>> meetings
    ) {
        for (const auto& meeting : meetings) {
            if (
                meeting.first < 0 ||
                meeting.second <= meeting.first
            ) {
                throw HeapError("Invalid meeting interval.");
            }
        }

        sort(meetings.begin(), meetings.end());

        priority_queue<
            int,
            vector<int>,
            greater<int>
        > active;

        int maximumRooms = 0;

        for (const auto& [start, end] : meetings) {
            while (!active.empty() && active.top() <= start) {
                active.pop();
            }

            active.push(end);

            maximumRooms = max(
                maximumRooms,
                static_cast<int>(active.size())
            );
        }

        return maximumRooms;
    }
};

int main() {
    try {
        cout << "HEAP AND PRIORITY QUEUE ASSESSMENT\n\n";

        vector<int> values = {7, 10, 4, 3, 20, 15};

        cout << "Kth largest: "
             << HeapAlgorithms::kthLargest(values, 3)
             << '\n';

        cout << "Top frequent: ";

        for (int value : HeapAlgorithms::topKFrequent(
            {1, 1, 1, 2, 2, 3}, 2
        )) {
            cout << value << ' ';
        }

        cout << "\nMerged arrays: ";

        auto merged = HeapAlgorithms::mergeKSortedArrays({
            {1, 4, 7},
            {2, 5, 8},
            {3, 6, 9}
        });

        for (int value : merged) {
            cout << value << ' ';
        }

        cout << "\nMinimum rope cost: "
             << HeapAlgorithms::connectRopes({4, 3, 2, 6})
             << '\n';

        cout << "Meeting rooms: "
             << HeapAlgorithms::minimumMeetingRooms({
                 {0, 30},
                 {5, 10},
                 {15, 20}
             })
             << "\n\n";

        TaskScheduler scheduler;

        scheduler.submit(1, Priority::Low, "Generate report");
        scheduler.submit(2, Priority::Critical, "Security incident");
        scheduler.submit(3, Priority::High, "Deploy application");
        scheduler.submit(4, Priority::Normal, "Database backup");

        cout << "Task scheduling:\n";

        while (!scheduler.empty()) {
            Task task = scheduler.executeNext();

            cout << task.id << " - "
                 << task.description << '\n';
        }

        BranchProtection policy;

        policy.branch = "main";
        policy.requiredApprovals = 2;
        policy.requireStatusChecks = true;
        policy.requireResolvedConversations = true;

        GovernanceEngine engine;
        engine.addPolicy(policy);

        PullRequest pr;

        pr.id = 101;
        pr.title = "Implement heap-based scheduling";
        pr.sourceBranch = "feature/heap-scheduler";
        pr.targetBranch = "main";

        pr.reviews = {
            {"reviewer-1", true, true, false, false, true},
            {"reviewer-2", true, true, false, false, true}
        };

        pr.checks = {
            {"unit-tests", true, true},
            {"static-analysis", true, true},
            {"performance-tests", true, true}
        };

        MergeDecision decision = engine.evaluate(pr);

        cout << "\nPull Request merge eligibility: "
             << (decision.eligible ? "ELIGIBLE" : "BLOCKED")
             << '\n';

        for (const auto& reason : decision.reasons) {
            cout << "- " << reason << '\n';
        }

        assert(decision.eligible);
        assert(engine.merge(pr));

        assert(HeapAlgorithms::kthLargest(
            {3, 2, 1, 5, 6, 4}, 2
        ) == 5);

        assert(HeapAlgorithms::connectRopes(
            {4, 3, 2, 6}
        ) == 29);

        assert(HeapAlgorithms::minimumMeetingRooms(
            {{0, 30}, {5, 10}, {15, 20}}
        ) == 2);

        cout << "\nAll assessment checks passed.\n";

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
