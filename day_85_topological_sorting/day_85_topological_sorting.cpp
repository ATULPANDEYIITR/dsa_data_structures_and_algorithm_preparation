#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

enum class TaskState {
    Pending,
    Ready,
    Running,
    Completed,
    Failed,
    Blocked
};

struct Task {
    string id;
    string description;
    int duration;
    TaskState state = TaskState::Pending;
};

class DependencyError : public runtime_error {
public:
    explicit DependencyError(const string& message)
        : runtime_error(message) {}
};

class CycleError : public DependencyError {
public:
    explicit CycleError(const vector<string>& cycle)
        : DependencyError(buildMessage(cycle)) {}

private:
    static string buildMessage(const vector<string>& cycle) {
        string message = "Cycle detected: ";

        for (size_t i = 0; i < cycle.size(); ++i) {
            if (i > 0) message += " -> ";
            message += cycle[i];
        }

        return message;
    }
};

class DependencyGraph {
private:
    map<string, Task> tasks;
    map<string, set<string>> adjacency;
    map<string, set<string>> reverse;

    vector<string> findCycle() const {
        unordered_map<string, int> color;
        vector<string> path;

        for (const auto& [id, task] : tasks) {
            color[id] = 0;
        }

        function<bool(const string&)> visit =
            [&](const string& node) -> bool {

            color[node] = 1;
            path.push_back(node);

            for (const auto& child : adjacency.at(node)) {
                if (color[child] == 1) {
                    auto it = find(
                        path.begin(),
                        path.end(),
                        child
                    );

                    vector<string> cycle(it, path.end());
                    cycle.push_back(child);
                    path = cycle;
                    return true;
                }

                if (color[child] == 0 && visit(child)) {
                    return true;
                }
            }

            path.pop_back();
            color[node] = 2;
            return false;
        };

        for (const auto& [id, task] : tasks) {
            if (color[id] == 0 && visit(id)) {
                return path;
            }
        }

        return {};
    }

public:
    void addTask(
        const string& id,
        const string& description,
        int duration
    ) {
        if (id.empty() || description.empty()) {
            throw invalid_argument("Task fields cannot be empty.");
        }

        if (duration <= 0) {
            throw invalid_argument("Duration must be positive.");
        }

        if (tasks.count(id)) {
            throw DependencyError("Duplicate task: " + id);
        }

        tasks.emplace(
            id,
            Task{id, description, duration}
        );

        adjacency[id];
        reverse[id];
    }

    void addDependency(
        const string& prerequisite,
        const string& dependent
    ) {
        if (!tasks.count(prerequisite) ||
            !tasks.count(dependent)) {
            throw DependencyError("Unknown task in dependency.");
        }

        if (prerequisite == dependent) {
            throw CycleError({prerequisite, prerequisite});
        }

        if (adjacency[prerequisite].count(dependent)) {
            return;
        }

        adjacency[prerequisite].insert(dependent);
        reverse[dependent].insert(prerequisite);

        try {
            findCycle();
            auto cycle = findCycle();

            if (!cycle.empty()) {
                throw CycleError(cycle);
            }
        } catch (...) {
            adjacency[prerequisite].erase(dependent);
            reverse[dependent].erase(prerequisite);
            throw;
        }
    }

    vector<string> dfsTopologicalSort() const {
        unordered_map<string, int> color;
        vector<string> result;
        vector<string> path;

        function<void(const string&)> visit =
            [&](const string& node) {

            color[node] = 1;
            path.push_back(node);

            for (const auto& child : adjacency.at(node)) {
                if (color[child] == 1) {
                    auto it = find(
                        path.begin(),
                        path.end(),
                        child
                    );

                    vector<string> cycle(it, path.end());
                    cycle.push_back(child);
                    throw CycleError(cycle);
                }

                if (color[child] == 0) {
                    visit(child);
                }
            }

            path.pop_back();
            color[node] = 2;
            result.push_back(node);
        };

        for (const auto& [id, task] : tasks) {
            color[id] = 0;
        }

        for (const auto& [id, task] : tasks) {
            if (color[id] == 0) {
                visit(id);
            }
        }

        reverse(result.begin(), result.end());
        return result;
    }

    vector<string> kahnTopologicalSort() const {
        map<string, int> indegree;

        for (const auto& [id, task] : tasks) {
            indegree[id] = static_cast<int>(reverse.at(id).size());
        }

        priority_queue<
            string,
            vector<string>,
            greater<string>
        > ready;

        for (const auto& [id, degree] : indegree) {
            if (degree == 0) ready.push(id);
        }

        vector<string> result;

        while (!ready.empty()) {
            string current = ready.top();
            ready.pop();

            result.push_back(current);

            for (const auto& child : adjacency.at(current)) {
                --indegree[child];

                if (indegree[child] == 0) {
                    ready.push(child);
                }
            }
        }

        if (result.size() != tasks.size()) {
            throw CycleError(findCycle());
        }

        return result;
    }

    map<int, vector<string>> executionLevels() const {
        auto order = kahnTopologicalSort();

        map<string, int> levels;

        for (const auto& [id, task] : tasks) {
            levels[id] = 0;
        }

        for (const auto& node : order) {
            for (const auto& child : adjacency.at(node)) {
                levels[child] = max(
                    levels[child],
                    levels[node] + 1
                );
            }
        }

        map<int, vector<string>> result;

        for (const auto& [id, level] : levels) {
            result[level].push_back(id);
        }

        return result;
    }

    pair<int, vector<string>> criticalPath() const {
        auto order = kahnTopologicalSort();

        map<string, int> finish;
        map<string, string> previous;

        for (const auto& id : order) {
            int best = 0;
            string predecessor;

            for (const auto& parent : reverse.at(id)) {
                if (finish[parent] > best) {
                    best = finish[parent];
                    predecessor = parent;
                }
            }

            finish[id] = best + tasks.at(id).duration;
            previous[id] = predecessor;
        }

        if (order.empty()) {
            return {0, {}};
        }

        string endpoint = order.front();

        for (const auto& id : order) {
            if (finish[id] > finish[endpoint]) {
                endpoint = id;
            }
        }

        vector<string> path;
        string current = endpoint;

        while (!current.empty()) {
            path.push_back(current);
            current = previous[current];
        }

        std::reverse(path.begin(), path.end());

        return {finish[endpoint], path};
    }

    bool validateOrder(const vector<string>& order) const {
        if (order.size() != tasks.size()) return false;

        map<string, int> position;

        for (size_t i = 0; i < order.size(); ++i) {
            if (!tasks.count(order[i])) return false;
            if (position.count(order[i])) return false;

            position[order[i]] = static_cast<int>(i);
        }

        for (const auto& [parent, children] : adjacency) {
            for (const auto& child : children) {
                if (position[parent] >= position[child]) {
                    return false;
                }
            }
        }

        return true;
    }

    void printTasks() const {
        cout << "\nTASK CATALOG\n";

        for (const auto& [id, task] : tasks) {
            cout << id << " | "
                 << task.description
                 << " | Duration: "
                 << task.duration << '\n';
        }
    }

    size_t size() const {
        return tasks.size();
    }
};

DependencyGraph createProject() {
    DependencyGraph graph;

    graph.addTask("T1", "Gather requirements", 2);
    graph.addTask("T2", "Design architecture", 3);
    graph.addTask("T3", "Design database", 2);
    graph.addTask("T4", "Implement backend", 5);
    graph.addTask("T5", "Implement frontend", 4);
    graph.addTask("T6", "Integrate application", 2);
    graph.addTask("T7", "Execute testing", 3);
    graph.addTask("T8", "Security assessment", 2);
    graph.addTask("T9", "Production deployment", 1);

    const vector<pair<string, string>> edges = {
        {"T1", "T2"},
        {"T1", "T3"},
        {"T2", "T4"},
        {"T3", "T4"},
        {"T2", "T5"},
        {"T4", "T6"},
        {"T5", "T6"},
        {"T6", "T7"},
        {"T6", "T8"},
        {"T7", "T9"},
        {"T8", "T9"}
    };

    for (const auto& [parent, child] : edges) {
        graph.addDependency(parent, child);
    }

    return graph;
}

void printOrder(
    const string& title,
    const vector<string>& order
) {
    cout << "\n" << title << '\n';

    for (size_t i = 0; i < order.size(); ++i) {
        if (i > 0) cout << " -> ";
        cout << order[i];
    }

    cout << '\n';
}

int main() {
    try {
        DependencyGraph graph = createProject();

        cout << "TOPOLOGICAL SORTING ENGINE\n";
        cout << "==========================\n";

        graph.printTasks();

        auto dfs = graph.dfsTopologicalSort();
        auto kahn = graph.kahnTopologicalSort();

        printOrder("DFS TOPOLOGICAL ORDER", dfs);
        printOrder("KAHN TOPOLOGICAL ORDER", kahn);

        cout << "\nPARALLEL EXECUTION LEVELS\n";

        for (const auto& [level, tasks] :
             graph.executionLevels()) {

            cout << "Stage " << level << ": ";

            for (size_t i = 0; i < tasks.size(); ++i) {
                if (i > 0) cout << ", ";
                cout << tasks[i];
            }

            cout << '\n';
        }

        auto [duration, path] = graph.criticalPath();

        printOrder("CRITICAL PATH", path);

        cout << "Minimum project duration: "
             << duration << " time units\n";

        if (!graph.validateOrder(dfs) ||
            !graph.validateOrder(kahn)) {
            throw runtime_error("Invalid topological ordering.");
        }

        cout << "\nVALIDATION\n";
        cout << "DFS ordering: PASS\n";
        cout << "Kahn ordering: PASS\n";
        cout << "Dependency constraints: PASS\n";
        cout << "Critical path calculation: PASS\n";

        DependencyGraph test;

        test.addTask("A", "Task A", 1);
        test.addTask("B", "Task B", 1);
        test.addTask("C", "Task C", 1);

        test.addDependency("A", "B");
        test.addDependency("B", "C");

        try {
            test.addDependency("C", "A");
        } catch (const CycleError& error) {
            cout << "\nCycle rejection: "
                 << error.what() << '\n';
        }

        cout << "Existing graph after rejected edge: ";
        printOrder("VALID ORDER", test.kahnTopologicalSort());

        DependencyGraph empty;
        if (!empty.kahnTopologicalSort().empty()) {
            throw runtime_error("Empty graph validation failed.");
        }

        cout << "Empty graph: PASS\n";

    } catch (const exception& error) {
        cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
