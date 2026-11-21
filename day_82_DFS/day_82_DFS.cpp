#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <set>
#include <stack>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

struct TraversalResult {
    int start;
    vector<int> order;
    unordered_map<int, int> parent;
    unordered_map<int, int> depth;
};

class Graph {
private:
    map<int, set<int>> adjacency;

public:
    void addVertex(int vertex) {
        adjacency.try_emplace(vertex);
    }

    void addEdge(int u, int v) {
        if (u == v) {
            throw invalid_argument("Self-loops are not supported.");
        }

        addVertex(u);
        addVertex(v);

        adjacency[u].insert(v);
        adjacency[v].insert(u);
    }

    void removeEdge(int u, int v) {
        if (!adjacency.count(u) || !adjacency.count(v)) {
            throw invalid_argument("Unknown vertex.");
        }

        if (!adjacency[u].count(v)) {
            throw invalid_argument("Edge does not exist.");
        }

        adjacency[u].erase(v);
        adjacency[v].erase(u);
    }

    void validateStart(int start) const {
        if (!adjacency.count(start)) {
            throw invalid_argument("Starting vertex does not exist.");
        }
    }

    /*
     * Recursive DFS.
     *
     * Sorted adjacency sets provide deterministic traversal.
     *
     * Time: O(V + E), excluding container iteration overhead.
     * Space: O(V) plus recursive call-stack consumption.
     */
    TraversalResult recursiveDFS(int start) const {
        validateStart(start);

        TraversalResult result;
        result.start = start;
        result.parent[start] = -1;
        result.depth[start] = 0;

        unordered_set<int> visited;

        function<void(int)> visit = [&](int vertex) {
            visited.insert(vertex);
            result.order.push_back(vertex);

            for (int neighbor : adjacency.at(vertex)) {
                if (!visited.count(neighbor)) {
                    result.parent[neighbor] = vertex;
                    result.depth[neighbor] = result.depth[vertex] + 1;
                    visit(neighbor);
                }
            }
        };

        visit(start);
        return result;
    }

    /*
     * Iterative DFS.
     *
     * Explicit stack avoids recursive call-stack limitations.
     * Vertices are marked when pushed.
     */
    TraversalResult iterativeDFS(int start) const {
        validateStart(start);

        TraversalResult result;
        result.start = start;

        unordered_set<int> visited;
        stack<int> pending;

        visited.insert(start);
        pending.push(start);

        result.parent[start] = -1;
        result.depth[start] = 0;

        while (!pending.empty()) {
            int vertex = pending.top();
            pending.pop();

            result.order.push_back(vertex);

            for (auto it = adjacency.at(vertex).rbegin();
                 it != adjacency.at(vertex).rend(); ++it) {

                int neighbor = *it;

                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);

                    result.parent[neighbor] = vertex;
                    result.depth[neighbor] =
                        result.depth[vertex] + 1;

                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    /*
     * Connected component detection.
     *
     * Every vertex is processed exactly once.
     * Isolated vertices are included.
     */
    vector<vector<int>> connectedComponents() const {
        unordered_set<int> visited;
        vector<vector<int>> components;

        for (const auto& [start, neighbors] : adjacency) {
            if (visited.count(start)) {
                continue;
            }

            vector<int> component;
            stack<int> pending;

            pending.push(start);
            visited.insert(start);

            while (!pending.empty()) {
                int vertex = pending.top();
                pending.pop();

                component.push_back(vertex);

                for (int neighbor : adjacency.at(vertex)) {
                    if (!visited.count(neighbor)) {
                        visited.insert(neighbor);
                        pending.push(neighbor);
                    }
                }
            }

            sort(component.begin(), component.end());
            components.push_back(move(component));
        }

        return components;
    }

    vector<int> reconstructPath(
        const TraversalResult& result,
        int destination
    ) const {
        if (!result.parent.count(destination)) {
            return {};
        }

        vector<int> path;
        int current = destination;

        while (current != -1) {
            path.push_back(current);
            current = result.parent.at(current);
        }

        reverse(path.begin(), path.end());
        return path;
    }

    bool hasCycle() const {
        unordered_set<int> visited;

        function<bool(int, int)> visit =
            [&](int vertex, int parent) -> bool {

            visited.insert(vertex);

            for (int neighbor : adjacency.at(vertex)) {
                if (!visited.count(neighbor)) {
                    if (visit(neighbor, vertex)) {
                        return true;
                    }
                } else if (neighbor != parent) {
                    return true;
                }
            }

            return false;
        };

        for (const auto& [vertex, neighbors] : adjacency) {
            if (!visited.count(vertex)) {
                if (visit(vertex, -1)) {
                    return true;
                }
            }
        }

        return false;
    }

    void display() const {
        cout << "\nAdjacency List\n";

        for (const auto& [vertex, neighbors] : adjacency) {
            cout << vertex << ": ";

            for (int neighbor : neighbors) {
                cout << neighbor << " ";
            }

            cout << '\n';
        }
    }
};

void printVector(const vector<int>& values) {
    for (int value : values) {
        cout << value << " ";
    }
    cout << '\n';
}

int main() {
    try {
        Graph graph;

        for (int vertex = 1; vertex <= 10; ++vertex) {
            graph.addVertex(vertex);
        }

        vector<pair<int, int>> edges = {
            {1, 2}, {1, 3},
            {2, 4}, {2, 5},
            {3, 6}, {3, 7},
            {5, 8}, {6, 8},
            {9, 10}
        };

        for (const auto& [u, v] : edges) {
            graph.addEdge(u, v);
        }

        graph.display();

        cout << "\n1. Recursive DFS\n";

        TraversalResult recursive = graph.recursiveDFS(1);
        printVector(recursive.order);

        cout << "\n2. Iterative DFS\n";

        TraversalResult iterative = graph.iterativeDFS(1);
        printVector(iterative.order);

        assert(recursive.order == iterative.order);

        cout << "\n3. Parent relationships\n";

        for (const auto& [vertex, parent] : recursive.parent) {
            cout << "Vertex " << vertex
                 << ", Parent " << parent << '\n';
        }

        cout << "\n4. Path reconstruction\n";

        printVector(graph.reconstructPath(recursive, 8));

        cout << "\n5. Unreachable vertex\n";

        vector<int> missing = graph.reconstructPath(recursive, 10);

        if (missing.empty()) {
            cout << "No path exists from 1 to 10.\n";
        }

        cout << "\n6. Connected components\n";

        auto components = graph.connectedComponents();

        for (size_t i = 0; i < components.size(); ++i) {
            cout << "Component " << i + 1 << ": ";
            printVector(components[i]);
        }

        cout << "\n7. Cycle detection\n";
        cout << boolalpha << graph.hasCycle() << '\n';

        cout << "\n8. Isolated vertices\n";

        Graph isolated;
        isolated.addVertex(100);
        isolated.addVertex(200);
        isolated.addVertex(300);
        isolated.addEdge(100, 200);

        auto isolatedComponents = isolated.connectedComponents();

        for (const auto& component : isolatedComponents) {
            printVector(component);
        }

        cout << "\n9. Edge removal\n";

        graph.removeEdge(5, 8);

        auto updatedComponents = graph.connectedComponents();

        for (const auto& component : updatedComponents) {
            printVector(component);
        }

        cout << "\n10. Validation\n";

        try {
            graph.iterativeDFS(999);
        } catch (const invalid_argument& error) {
            cout << "Expected error: " << error.what() << '\n';
        }

        try {
            graph.addEdge(1, 1);
        } catch (const invalid_argument& error) {
            cout << "Expected error: " << error.what() << '\n';
        }

        cout << "\nAll assertions passed.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
