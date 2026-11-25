#include <algorithm>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <utility>

using namespace std;

enum class GraphType {
    Directed,
    Undirected
};

struct TraversalResult {
    vector<int> order;
    unordered_map<int, int> parent;
    unordered_map<int, int> distance;
};

struct TopologicalResult {
    vector<int> order;
    bool hasCycle;
};

class GraphAssessment {
private:
    GraphType type;

    unordered_map<int, vector<int>> adjacency;
    vector<int> vertices;

    // A canonical edge representation prevents duplicate
    // undirected edges.
    unordered_set<string> edges;

    string edgeKey(int u, int v) const {
        if (type == GraphType::Undirected && u > v) {
            swap(u, v);
        }

        return to_string(u) + ":" + to_string(v);
    }

    void validateVertex(int vertex) const {
        if (adjacency.find(vertex) == adjacency.end()) {
            throw invalid_argument(
                "Unknown vertex: " + to_string(vertex)
            );
        }
    }

public:
    explicit GraphAssessment(
        const vector<int>& input,
        GraphType graphType = GraphType::Undirected
    ) : type(graphType) {

        unordered_set<int> uniqueVertices;

        for (int vertex : input) {
            if (!uniqueVertices.insert(vertex).second) {
                throw invalid_argument("Duplicate vertex.");
            }

            vertices.push_back(vertex);
            adjacency[vertex] = {};
        }
    }

    void addEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);

        string key = edgeKey(u, v);

        if (edges.count(key)) {
            return;
        }

        edges.insert(key);
        adjacency[u].push_back(v);

        if (type == GraphType::Undirected && u != v) {
            adjacency[v].push_back(u);
        }
    }

    void removeEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);

        string key = edgeKey(u, v);

        if (!edges.count(key)) {
            return;
        }

        edges.erase(key);

        auto& first = adjacency[u];
        first.erase(
            remove(first.begin(), first.end(), v),
            first.end()
        );

        if (type == GraphType::Undirected && u != v) {
            auto& second = adjacency[v];

            second.erase(
                remove(second.begin(), second.end(), u),
                second.end()
            );
        }
    }

    void display() const {
        cout << "\nAdjacency list:\n";

        for (int vertex : vertices) {
            cout << vertex << ": ";

            for (int neighbor : adjacency.at(vertex)) {
                cout << neighbor << " ";
            }

            cout << "\n";
        }
    }

    TraversalResult bfs(int start) const {
        validateVertex(start);

        TraversalResult result;

        unordered_set<int> visited;
        queue<int> pending;

        visited.insert(start);
        result.parent[start] = -1;
        result.distance[start] = 0;

        pending.push(start);

        while (!pending.empty()) {
            int vertex = pending.front();
            pending.pop();

            result.order.push_back(vertex);

            for (int neighbor : adjacency.at(vertex)) {
                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);

                    result.parent[neighbor] = vertex;
                    result.distance[neighbor] =
                        result.distance[vertex] + 1;

                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    TraversalResult dfs(int start) const {
        validateVertex(start);

        TraversalResult result;

        unordered_set<int> visited;

        vector<pair<int, int>> stack;

        visited.insert(start);
        result.parent[start] = -1;
        result.distance[start] = 0;

        stack.push_back({start, 0});

        while (!stack.empty()) {
            int vertex = stack.back().first;
            stack.pop_back();

            result.order.push_back(vertex);

            const auto& neighbors = adjacency.at(vertex);

            for (auto it = neighbors.rbegin();
                 it != neighbors.rend(); ++it) {

                int neighbor = *it;

                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);

                    result.parent[neighbor] = vertex;
                    result.distance[neighbor] =
                        result.distance[vertex] + 1;

                    stack.push_back({neighbor, 0});
                }
            }
        }

        return result;
    }

    vector<vector<int>> connectedComponents() const {
        if (type != GraphType::Undirected) {
            throw logic_error(
                "Connected components require an undirected graph."
            );
        }

        unordered_set<int> visited;
        vector<vector<int>> components;

        for (int start : vertices) {
            if (visited.count(start)) {
                continue;
            }

            vector<int> component;
            queue<int> pending;

            visited.insert(start);
            pending.push(start);

            while (!pending.empty()) {
                int vertex = pending.front();
                pending.pop();

                component.push_back(vertex);

                for (int neighbor : adjacency.at(vertex)) {
                    if (!visited.count(neighbor)) {
                        visited.insert(neighbor);
                        pending.push(neighbor);
                    }
                }
            }

            components.push_back(move(component));
        }

        return components;
    }

    bool hasUndirectedCycle() const {
        if (type != GraphType::Undirected) {
            throw logic_error("Expected an undirected graph.");
        }

        unordered_set<int> visited;

        for (int start : vertices) {
            if (visited.count(start)) {
                continue;
            }

            queue<pair<int, int>> pending;

            visited.insert(start);
            pending.push({start, -1});

            while (!pending.empty()) {
                auto [vertex, parent] = pending.front();
                pending.pop();

                for (int neighbor : adjacency.at(vertex)) {
                    if (!visited.count(neighbor)) {
                        visited.insert(neighbor);
                        pending.push({neighbor, vertex});
                    } else if (neighbor != parent) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    bool hasDirectedCycle() const {
        if (type != GraphType::Directed) {
            throw logic_error("Expected a directed graph.");
        }

        // 0 = unvisited, 1 = active, 2 = completed.
        unordered_map<int, int> state;

        for (int vertex : vertices) {
            state[vertex] = 0;
        }

        for (int start : vertices) {
            if (state[start] != 0) {
                continue;
            }

            vector<pair<int, size_t>> stack;

            state[start] = 1;
            stack.push_back({start, 0});

            while (!stack.empty()) {
                int vertex = stack.back().first;
                size_t& index = stack.back().second;

                const auto& neighbors = adjacency.at(vertex);

                if (index == neighbors.size()) {
                    state[vertex] = 2;
                    stack.pop_back();
                    continue;
                }

                int neighbor = neighbors[index++];

                if (state[neighbor] == 1) {
                    return true;
                }

                if (state[neighbor] == 0) {
                    state[neighbor] = 1;
                    stack.push_back({neighbor, 0});
                }
            }
        }

        return false;
    }

    pair<bool, unordered_map<int, int>> isBipartite() const {
        if (type != GraphType::Undirected) {
            throw logic_error("Expected an undirected graph.");
        }

        unordered_map<int, int> color;

        for (int start : vertices) {
            if (color.count(start)) {
                continue;
            }

            queue<int> pending;
            color[start] = 0;
            pending.push(start);

            while (!pending.empty()) {
                int vertex = pending.front();
                pending.pop();

                for (int neighbor : adjacency.at(vertex)) {
                    if (!color.count(neighbor)) {
                        color[neighbor] = 1 - color[vertex];
                        pending.push(neighbor);
                    } else if (color[neighbor] == color[vertex]) {
                        return {false, color};
                    }
                }
            }
        }

        return {true, color};
    }

    TopologicalResult topologicalSort() const {
        if (type != GraphType::Directed) {
            throw logic_error(
                "Topological sorting requires a directed graph."
            );
        }

        unordered_map<int, int> indegree;

        for (int vertex : vertices) {
            indegree[vertex] = 0;
        }

        for (int vertex : vertices) {
            for (int neighbor : adjacency.at(vertex)) {
                indegree[neighbor]++;
            }
        }

        queue<int> pending;

        for (int vertex : vertices) {
            if (indegree[vertex] == 0) {
                pending.push(vertex);
            }
        }

        TopologicalResult result;
        result.hasCycle = false;

        while (!pending.empty()) {
            int vertex = pending.front();
            pending.pop();

            result.order.push_back(vertex);

            for (int neighbor : adjacency.at(vertex)) {
                indegree[neighbor]--;

                if (indegree[neighbor] == 0) {
                    pending.push(neighbor);
                }
            }
        }

        result.hasCycle =
            result.order.size() != vertices.size();

        return result;
    }

    vector<int> shortestPath(int start, int target) const {
        validateVertex(start);
        validateVertex(target);

        TraversalResult result = bfs(start);

        if (!result.parent.count(target)) {
            return {};
        }

        vector<int> path;

        int current = target;

        while (current != -1) {
            path.push_back(current);
            current = result.parent.at(current);
        }

        reverse(path.begin(), path.end());

        return path;
    }
};


void printVector(const vector<int>& values) {
    for (int value : values) {
        cout << value << " ";
    }

    cout << "\n";
}

void printComponents(const vector<vector<int>>& components) {
    for (size_t i = 0; i < components.size(); ++i) {
        cout << "Component " << i + 1 << ": ";
        printVector(components[i]);
    }
}


int main() {
    try {
        cout << "GRAPH ASSESSMENT ENGINE\n";
        cout << "=======================\n";

        GraphAssessment graph(
            {1, 2, 3, 4, 5, 6, 7, 8},
            GraphType::Undirected
        );

        for (auto edge : vector<pair<int, int>>{
            {1, 2}, {1, 3}, {2, 4},
            {3, 4}, {5, 6}, {7, 8}
        }) {
            graph.addEdge(edge.first, edge.second);
        }

        graph.display();

        cout << "\nBFS from 1: ";
        printVector(graph.bfs(1).order);

        cout << "DFS from 1: ";
        printVector(graph.dfs(1).order);

        cout << "\nConnected components:\n";
        printComponents(graph.connectedComponents());

        cout << "Undirected cycle: "
             << boolalpha
             << graph.hasUndirectedCycle()
             << "\n";

        auto [bipartite, colors] = graph.isBipartite();

        cout << "Bipartite: " << bipartite << "\n";

        cout << "Colors:\n";

        for (const auto& [vertex, color] : colors) {
            cout << vertex << " -> " << color << "\n";
        }

        cout << "Shortest path 1 -> 4: ";
        printVector(graph.shortestPath(1, 4));

        cout << "Shortest path 1 -> 8: ";
        printVector(graph.shortestPath(1, 8));

        // Self-loops are valid graph edges and form cycles.
        graph.addEdge(8, 8);

        cout << "\nAfter adding self-loop:\n";

        cout << "Undirected cycle: "
             << graph.hasUndirectedCycle()
             << "\n";

        cout << "Bipartite: "
             << graph.isBipartite().first
             << "\n";

        // Directed dependency graph.
        cout << "\nDIRECTED DEPENDENCY GRAPH\n";

        GraphAssessment dag(
            {1, 2, 3, 4, 5, 6},
            GraphType::Directed
        );

        for (auto edge : vector<pair<int, int>>{
            {1, 3}, {2, 3}, {3, 4},
            {3, 5}, {4, 6}, {5, 6}
        }) {
            dag.addEdge(edge.first, edge.second);
        }

        cout << "Topological ordering: ";

        TopologicalResult result = dag.topologicalSort();

        printVector(result.order);

        cout << "Directed cycle: "
             << dag.hasDirectedCycle()
             << "\n";

        // A back edge invalidates the DAG.
        dag.addEdge(6, 3);

        result = dag.topologicalSort();

        cout << "After adding edge 6 -> 3:\n";
        cout << "Directed cycle: "
             << dag.hasDirectedCycle()
             << "\n";

        cout << "Topological sort possible: "
             << !result.hasCycle
             << "\n";

        // Automated assertions.
        GraphAssessment test(
            {10, 20, 30, 40},
            GraphType::Undirected
        );

        test.addEdge(10, 20);
        test.addEdge(20, 30);

        if (test.connectedComponents().size() != 2) {
            throw runtime_error("Component test failed.");
        }

        if (test.hasUndirectedCycle()) {
            throw runtime_error("Acyclic graph test failed.");
        }

        if (!test.isBipartite().first) {
            throw runtime_error("Bipartite test failed.");
        }

        test.addEdge(30, 10);

        if (!test.hasUndirectedCycle()) {
            throw runtime_error("Cycle detection test failed.");
        }

        if (test.isBipartite().first) {
            throw runtime_error("Odd-cycle test failed.");
        }

        GraphAssessment empty({});

        if (!empty.connectedComponents().empty()) {
            throw runtime_error("Empty graph test failed.");
        }

        cout << "\nAll graph assessment tests passed.\n";

    } catch (const exception& error) {
        cerr << "Graph assessment error: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
