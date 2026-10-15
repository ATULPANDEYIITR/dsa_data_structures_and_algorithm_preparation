#include <algorithm>
#include <deque>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

/*
 * Repository-independent case study: an event-processing service uses
 * stack-based undo history and queue-based FIFO task scheduling.
 * The assessment algorithms are integrated into diagnostic processing.
 */

enum class TaskState {
    Queued,
    Running,
    Completed,
    Failed
};

struct Task {
    int id;
    string name;
    TaskState state = TaskState::Queued;
    int attempts = 0;
};

class TaskScheduler {
private:
    deque<int> pending;
    unordered_map<int, Task> tasks;

public:
    void submit(int id, string name) {
        if (id <= 0 || name.empty()) {
            throw invalid_argument("Task ID must be positive and name non-empty");
        }
        if (tasks.count(id)) {
            throw invalid_argument("Duplicate task ID");
        }

        tasks.emplace(id, Task{id, move(name), TaskState::Queued, 0});
        pending.push_back(id);
    }

    optional<Task> dispatch() {
        if (pending.empty()) {
            return nullopt;
        }

        int id = pending.front();
        pending.pop_front();

        Task& task = tasks.at(id);
        if (task.state != TaskState::Queued) {
            throw logic_error("Only queued tasks may be dispatched");
        }

        task.state = TaskState::Running;
        ++task.attempts;
        return task;
    }

    void finish(int id, bool success) {
        auto iterator = tasks.find(id);
        if (iterator == tasks.end()) {
            throw out_of_range("Unknown task ID");
        }

        Task& task = iterator->second;
        if (task.state != TaskState::Running) {
            throw logic_error("Only running tasks may finish");
        }

        task.state = success ? TaskState::Completed : TaskState::Failed;
    }

    const unordered_map<int, Task>& allTasks() const {
        return tasks;
    }
};

class UndoableConfiguration {
private:
    string current;
    vector<string> history;

public:
    explicit UndoableConfiguration(string initial)
        : current(move(initial)) {
        if (current.empty()) {
            throw invalid_argument("Initial configuration cannot be empty");
        }
    }

    void update(string next) {
        if (next.empty()) {
            throw invalid_argument("Configuration cannot be empty");
        }

        history.push_back(current);
        current = move(next);
    }

    bool undo() {
        if (history.empty()) {
            return false;
        }

        current = history.back();
        history.pop_back();
        return true;
    }

    const string& value() const {
        return current;
    }
};

vector<int> nextGreaterValues(const vector<int>& values) {
    vector<int> result(values.size(), -1);
    vector<size_t> unresolved;

    for (size_t i = 0; i < values.size(); ++i) {
        while (!unresolved.empty() &&
               values[unresolved.back()] < values[i]) {
            result[unresolved.back()] = values[i];
            unresolved.pop_back();
        }
        unresolved.push_back(i);
    }

    return result;
}

vector<int> slidingMaximum(const vector<int>& values, size_t window) {
    if (window == 0 || window > values.size()) {
        throw invalid_argument("Window must be in the range [1, n]");
    }

    deque<size_t> candidates;
    vector<int> result;

    for (size_t i = 0; i < values.size(); ++i) {
        while (!candidates.empty() && candidates.front() + window <= i) {
            candidates.pop_front();
        }

        while (!candidates.empty() &&
               values[candidates.back()] <= values[i]) {
            candidates.pop_back();
        }

        candidates.push_back(i);

        if (i + 1 >= window) {
            result.push_back(values[candidates.front()]);
        }
    }

    return result;
}

bool balancedDelimiters(const string& expression) {
    vector<char> stack;
    unordered_map<char, char> matching = {
        {')', '('}, {']', '['}, {'}', '{'}
    };

    for (char character : expression) {
        if (character == '(' || character == '[' || character == '{') {
            stack.push_back(character);
        } else if (matching.count(character)) {
            if (stack.empty() || stack.back() != matching.at(character)) {
                return false;
            }
            stack.pop_back();
        }
    }

    return stack.empty();
}

void printVector(const string& label, const vector<int>& values) {
    cout << label;
    for (int value : values) {
        cout << value << ' ';
    }
    cout << '\n';
}

int main() {
    try {
        cout << "Task scheduling case study\n";

        TaskScheduler scheduler;
        scheduler.submit(101, "Validate incoming build");
        scheduler.submit(102, "Run integration tests");
        scheduler.submit(103, "Publish test report");

        while (auto task = scheduler.dispatch()) {
            cout << "Running task " << task->id << ": " << task->name << '\n';

            // Simulate a retry-free execution result. Real systems would
            // capture the worker's exit status and persist diagnostics.
            scheduler.finish(task->id, task->id != 102);
        }

        for (const auto& [id, task] : scheduler.allTasks()) {
            string state;
            switch (task.state) {
                case TaskState::Queued: state = "QUEUED"; break;
                case TaskState::Running: state = "RUNNING"; break;
                case TaskState::Completed: state = "COMPLETED"; break;
                case TaskState::Failed: state = "FAILED"; break;
            }
            cout << id << " -> " << state
                 << ", attempts=" << task.attempts << '\n';
        }

        cout << "\nUndoable configuration\n";
        UndoableConfiguration configuration("max_workers=4");
        configuration.update("max_workers=8");
        cout << "Current: " << configuration.value() << '\n';
        configuration.undo();
        cout << "After undo: " << configuration.value() << '\n';

        cout << "\nMonotonic stack and deque assessment\n";
        const vector<int> measurements = {2, 1, 2, 4, 3};
        printVector("Next greater values: ", nextGreaterValues(measurements));

        const vector<int> latencies = {18, 12, 31, 25, 40, 16, 42};
        printVector("Window maxima: ", slidingMaximum(latencies, 3));

        cout << "Balanced delimiters: "
             << boolalpha << balancedDelimiters("{[()]}") << '\n';
        cout << "Malformed delimiters: "
             << balancedDelimiters("([)]") << '\n';

        // Empty queues and illegal transitions are explicit failures,
        // not silent state changes.
        try {
            scheduler.finish(101, true);
        } catch (const logic_error& error) {
            cout << "Invalid transition rejected: " << error.what() << '\n';
        }

        try {
            slidingMaximum(latencies, 0);
        } catch (const invalid_argument& error) {
            cout << "Invalid window rejected: " << error.what() << '\n';
        }

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal assessment error: " << error.what() << '\n';
        return 1;
    }
}
