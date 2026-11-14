#include <algorithm>
#include <cassert>
#include <cstdint>
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

/*
 * Priority Queues: Repository Job Scheduling Engine.
 *
 * Models:
 * - Min-priority and max-priority heaps.
 * - Stable task scheduling.
 * - Task lifecycle and cancellation.
 * - Priority updates through versioned heap entries.
 * - Protected execution rules.
 * - Top-K selection.
 * - Running median.
 *
 * Compile: g++ -std=c++17 -O2 -Wall -Wextra main.cpp -o priority
 */

enum class TaskState {
    PENDING,
    RUNNING,
    COMPLETED,
    CANCELLED,
    FAILED
};

enum class JobType {
    BUILD,
    SECURITY_SCAN,
    TEST,
    DEPLOYMENT,
    REPORT
};

string toString(TaskState state) {
    switch (state) {
        case TaskState::PENDING: return "PENDING";
        case TaskState::RUNNING: return "RUNNING";
        case TaskState::COMPLETED: return "COMPLETED";
        case TaskState::CANCELLED: return "CANCELLED";
        case TaskState::FAILED: return "FAILED";
    }

    throw logic_error("Invalid task state");
}

struct Job {
    int id;
    string name;
    JobType type;
    int priority;
    TaskState state = TaskState::PENDING;
    int attempts = 0;
};

template<typename T, typename Compare = less<T>>
class BinaryPriorityQueue {
private:
    priority_queue<T, vector<T>, Compare> heap;

public:
    void push(const T& value) {
        heap.push(value);
    }

    T pop() {
        if (heap.empty()) {
            throw underflow_error("Priority queue is empty");
        }

        T value = heap.top();
        heap.pop();
        return value;
    }

    const T& top() const {
        if (heap.empty()) {
            throw underflow_error("Priority queue is empty");
        }

        return heap.top();
    }

    bool empty() const {
        return heap.empty();
    }

    size_t size() const {
        return heap.size();
    }
};

struct HeapEntry {
    int priority;
    uint64_t sequence;
    int taskId;
    uint64_t version;
};

// priority_queue places the entry considered greatest at its top.
// Higher priorities and earlier sequence numbers are preferred.
struct SchedulingOrder {
    bool operator()(const HeapEntry& a, const HeapEntry& b) const {
        if (a.priority != b.priority) {
            return a.priority < b.priority;
        }

        return a.sequence > b.sequence;
    }
};

class Scheduler {
private:
    priority_queue<
        HeapEntry,
        vector<HeapEntry>,
        SchedulingOrder
    > queue;

    unordered_map<int, Job> jobs;
    unordered_map<int, uint64_t> versions;

    uint64_t sequence = 0;

    void enqueue(const Job& job) {
        queue.push({
            job.priority,
            sequence++,
            job.id,
            versions.at(job.id)
        });
    }

public:
    void submit(const Job& job) {
        if (job.id <= 0) {
            throw invalid_argument("Job ID must be positive");
        }

        if (job.name.empty()) {
            throw invalid_argument("Job name cannot be empty");
        }

        if (jobs.count(job.id)) {
            throw invalid_argument("Duplicate job ID");
        }

        if (job.state != TaskState::PENDING) {
            throw invalid_argument("New jobs must be pending");
        }

        jobs.emplace(job.id, job);
        versions[job.id] = 0;

        enqueue(jobs.at(job.id));
    }

    void updatePriority(int id, int priority) {
        auto it = jobs.find(id);

        if (it == jobs.end()) {
            throw out_of_range("Unknown job");
        }

        if (it->second.state != TaskState::PENDING) {
            throw logic_error("Only pending jobs can be updated");
        }

        it->second.priority = priority;
        ++versions[id];

        enqueue(it->second);
    }

    void cancel(int id) {
        auto it = jobs.find(id);

        if (it == jobs.end()) {
            throw out_of_range("Unknown job");
        }

        if (it->second.state != TaskState::PENDING) {
            throw logic_error("Job cannot be cancelled");
        }

        it->second.state = TaskState::CANCELLED;
        ++versions[id];
    }

    bool executeNext(Job& output) {
        while (!queue.empty()) {
            HeapEntry entry = queue.top();
            queue.pop();

            auto it = jobs.find(entry.taskId);

            if (it == jobs.end()) {
                continue;
            }

            Job& job = it->second;

            if (entry.version != versions.at(entry.taskId)) {
                continue;
            }

            if (job.state != TaskState::PENDING) {
                continue;
            }

            job.state = TaskState::RUNNING;
            ++job.attempts;

            output = job;
            return true;
        }

        return false;
    }

    void complete(int id, bool success) {
        auto it = jobs.find(id);

        if (it == jobs.end()) {
            throw out_of_range("Unknown job");
        }

        if (it->second.state != TaskState::RUNNING) {
            throw logic_error("Job is not running");
        }

        it->second.state = success
            ? TaskState::COMPLETED
            : TaskState::FAILED;
    }

    vector<int> processAll() {
        vector<int> executionOrder;
        Job current;

        while (executeNext(current)) {
            executionOrder.push_back(current.id);

            // A simulated build or deployment can fail independently.
            bool success = current.id != 4;

            complete(current.id, success);
        }

        return executionOrder;
    }

    void printReport() const {
        unordered_map<string, int> counts;

        for (const auto& pair : jobs) {
            counts[toString(pair.second.state)]++;
        }

        cout << "\nJOB REPORT\n";

        for (const auto& state : {
            "PENDING",
            "RUNNING",
            "COMPLETED",
            "CANCELLED",
            "FAILED"
        }) {
            cout << state << ": " << counts[state] << '\n';
        }
    }

    const Job& get(int id) const {
        auto it = jobs.find(id);

        if (it == jobs.end()) {
            throw out_of_range("Unknown job");
        }

        return it->second;
    }
};

vector<int> topKLargest(const vector<int>& values, size_t k) {
    if (k > values.size()) {
        throw invalid_argument("k exceeds collection size");
    }

    priority_queue<int, vector<int>, greater<int>> heap;

    for (int value : values) {
        if (heap.size() < k) {
            heap.push(value);
        } else if (k > 0 && value > heap.top()) {
            heap.pop();
            heap.push(value);
        }
    }

    vector<int> result;

    while (!heap.empty()) {
        result.push_back(heap.top());
        heap.pop();
    }

    sort(result.rbegin(), result.rend());
    return result;
}

int kthSmallest(const vector<int>& values, size_t k) {
    if (k == 0 || k > values.size()) {
        throw invalid_argument("Invalid k");
    }

    priority_queue<int> heap;

    for (int value : values) {
        heap.push(value);

        if (heap.size() > k) {
            heap.pop();
        }
    }

    return heap.top();
}

class RunningMedian {
private:
    priority_queue<int> lower;
    priority_queue<int, vector<int>, greater<int>> upper;

public:
    void add(int value) {
        if (lower.empty() || value <= lower.top()) {
            lower.push(value);
        } else {
            upper.push(value);
        }

        if (lower.size() > upper.size() + 1) {
            upper.push(lower.top());
            lower.pop();
        } else if (upper.size() > lower.size()) {
            lower.push(upper.top());
            upper.pop();
        }
    }

    double median() const {
        if (lower.empty()) {
            throw underflow_error("No elements available");
        }

        if (lower.size() == upper.size()) {
            return (
                static_cast<double>(lower.top()) +
                static_cast<double>(upper.top())
            ) / 2.0;
        }

        return static_cast<double>(lower.top());
    }
};

void demonstrateBasicHeaps() {
    cout << "MIN-HEAP\n";

    BinaryPriorityQueue<int, greater<int>> minHeap;

    for (int value : {40, 10, 30, 5, 20}) {
        minHeap.push(value);
    }

    while (!minHeap.empty()) {
        cout << minHeap.pop() << ' ';
    }

    cout << "\n\nMAX-HEAP\n";

    BinaryPriorityQueue<int> maxHeap;

    for (int value : {40, 10, 30, 5, 20}) {
        maxHeap.push(value);
    }

    while (!maxHeap.empty()) {
        cout << maxHeap.pop() << ' ';
    }

    cout << '\n';
}

void demonstrateScheduler() {
    Scheduler scheduler;

    scheduler.submit({
        1, "Compile application", JobType::BUILD, 5
    });

    scheduler.submit({
        2, "Security vulnerability scan",
        JobType::SECURITY_SCAN, 10
    });

    scheduler.submit({
        3, "Run unit tests", JobType::TEST, 6
    });

    scheduler.submit({
        4, "Deploy production release",
        JobType::DEPLOYMENT, 8
    });

    scheduler.submit({
        5, "Generate build report", JobType::REPORT, 2
    });

    scheduler.updatePriority(5, 7);
    scheduler.cancel(1);

    cout << "\nSCHEDULER EXECUTION\n";

    for (int id : scheduler.processAll()) {
        cout << "Executed job: " << id << '\n';
    }

    scheduler.printReport();
}

void demonstrateSelection() {
    vector<int> values = {
        17, 4, 29, 11, 8, 35, 21, 3, 29
    };

    cout << "\nSELECTION\n";

    cout << "Top 3: ";

    for (int value : topKLargest(values, 3)) {
        cout << value << ' ';
    }

    cout << "\nThird smallest: "
         << kthSmallest(values, 3) << '\n';
}

void demonstrateMedian() {
    RunningMedian tracker;

    cout << "\nRUNNING MEDIAN\n";

    for (int value : {12, 4, 5, 3, 8, 7, 15, 20}) {
        tracker.add(value);

        cout << "Inserted " << value
             << ", median = " << tracker.median() << '\n';
    }
}

void runTests() {
    BinaryPriorityQueue<int, greater<int>> minHeap;

    minHeap.push(8);
    minHeap.push(2);
    minHeap.push(5);

    assert(minHeap.pop() == 2);
    assert(minHeap.pop() == 5);
    assert(minHeap.pop() == 8);

    BinaryPriorityQueue<int> maxHeap;

    maxHeap.push(8);
    maxHeap.push(2);
    maxHeap.push(5);

    assert(maxHeap.pop() == 8);

    assert((topKLargest({4, 9, 1, 7, 3}, 2)
        == vector<int>{9, 7}));

    assert(kthSmallest({5, 1, 3, 2}, 2) == 2);

    RunningMedian median;
    median.add(1);
    median.add(3);
    median.add(2);
    median.add(4);

    assert(median.median() == 2.5);

    Scheduler scheduler;

    scheduler.submit({1, "Normal", JobType::TEST, 1});
    scheduler.submit({2, "Urgent", JobType::TEST, 2});

    scheduler.updatePriority(1, 5);

    vector<int> order = scheduler.processAll();

    assert((order == vector<int>{1, 2}));

    bool caught = false;

    try {
        topKLargest({1, 2}, 3);
    } catch (const invalid_argument&) {
        caught = true;
    }

    assert(caught);

    cout << "\nAll tests passed.\n";
}

int main() {
    try {
        demonstrateBasicHeaps();
        demonstrateScheduler();
        demonstrateSelection();
        demonstrateMedian();
        runTests();
    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
