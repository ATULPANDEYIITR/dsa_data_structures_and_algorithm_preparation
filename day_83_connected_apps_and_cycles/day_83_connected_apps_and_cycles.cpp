#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

enum class GraphType {
    UNDIRECTED,
    DIRECTED
};

struct CycleResult {
    bool hasCycle = false;
    vector<int> cycle;
};

class Graph {
private:
    map<int, vector<int>> adjacency;

public:
    GraphType type;

    explicit Graph(GraphType graphType)
        : type(graphType) {}

    void addVertex(int vertex) {
        adjacency.try_emplace(vertex);
    }

    void addEdge(int source, int destination) {
        addVertex(source);
        addVertex(destination);

        adjacency[source].push_back(destination);

        if (type == GraphType::UNDIRECTED &&
            source != destination) {
            adjacency[destination].push_back(source);
        }
    }

    const map<int, vector<int>>& getAdjacency() const {
        return adjacency;
    }

    const vector<int>& neighbors(int vertex) const {
        auto it = adjacency.find(vertex);

        if (it == adjacency.end()) {
            throw invalid_argument("Unknown vertex.");
        }

        return it->second;
    }

    size_t size() const {
        return adjacency.size();
    }

    void validate() const {
        for (const auto& [vertex, neighbors] : adjacency) {
            for (int neighbor : neighbors) {
                if (adjacency.find(neighbor) == adjacency.end()) {
                    throw invalid_argument(
                        "Adjacency references an unknown vertex."
                    );
                }
            }
        }
    }
};

class DisjointSet {
private:
    unordered_map<int, int> parent;
    unordered_map<int, int> rank;

public:
    explicit DisjointSet(const vector<int>& vertices) {
        for (int vertex : vertices) {
            parent[vertex] = vertex;
            rank[vertex] = 0;
        }
    }

    int find(int vertex) {
        if (!parent.count(vertex)) {
            throw invalid_argument("Unknown vertex in DSU.");
        }

        if (parent[vertex] != vertex) {
            parent[vertex] = find(parent[vertex]);
        }

        return parent[vertex];
    }

    bool unite(int first, int second) {
        int rootA = find(first);
        int rootB = find(second);

        if (rootA == rootB) {
            return false;
        }

        if (rank[rootA] < rank[rootB]) {
            swap(rootA, rootB);
        }

        parent[rootB] = rootA;

        if (rank[rootA] == rank[rootB]) {
            rank[rootA]++;
        }

        return true;
    }
};

class GraphGovernanceEngine {
private:
    static void requireType(
        const Graph& graph,
        GraphType expected
    ) {
        if (graph.type != expected) {
            throw invalid_argument("Incorrect graph type.");
        }

        graph.validate();
    }

public:
    static vector<vector<int>> connectedComponents(
        const Graph& graph
    ) {
        requireType(graph, GraphType::UNDIRECTED);

        unordered_set<int> visited;
        vector<vector<int>> components;

        for (const auto& [start, neighbors] :
             graph.getAdjacency()) {

            if (visited.count(start)) {
                continue;
            }

            vector<int> component;
            vector<int> stack = {start};

            visited.insert(start);

            while (!stack.empty()) {
                int vertex = stack.back();
                stack.pop_back();

                component.push_back(vertex);

                for (int neighbor : graph.neighbors(vertex)) {
                    if (visited.insert(neighbor).second) {
                        stack.push_back(neighbor);
                    }
                }
            }

            sort(component.begin(), component.end());
            components.push_back(move(component));
        }

        return components;
    }

    static CycleResult undirectedCycleDFS(
        const Graph& graph
    ) {
        requireType(graph, GraphType::UNDIRECTED);

        unordered_set<int> visited;
        unordered_map<int, int> parent;

        for (const auto& [start, neighbors] :
             graph.getAdjacency()) {

            if (visited.count(start)) {
                continue;
            }

            visited.insert(start);
            parent[start] = start;

            vector<pair<int, size_t>> stack;
            stack.push_back({start, 0});

            while (!stack.empty()) {
                int vertex = stack.back().first;
                size_t& index = stack.back().second;

                const auto& adjacent = graph.neighbors(vertex);

                if (index == adjacent.size()) {
                    stack.pop_back();
                    continue;
                }

                int neighbor = adjacent[index++];

                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);
                    parent[neighbor] = vertex;
                    stack.push_back({neighbor, 0});
                } else if (neighbor != parent[vertex]) {
                    return {true, {}};
                }
            }
        }

        return {false, {}};
    }

    static CycleResult undirectedCycleDSU(
        const Graph& graph
    ) {
        requireType(graph, GraphType::UNDIRECTED);

        vector<int> vertices;

        for (const auto& [vertex, neighbors] :
             graph.getAdjacency()) {
            vertices.push_back(vertex);
        }

        DisjointSet dsu(vertices);

        // The map representation contains each undirected edge
        // in both directions, so process only one representation.
        for (const auto& [source, neighbors] :
             graph.getAdjacency()) {

            for (int destination : neighbors) {
                if (source <= destination) {
                    if (!dsu.unite(source, destination)) {
                        return {true, {}};
                    }
                }
            }
        }

        return {false, {}};
    }

    static CycleResult directedCycleDFS(
        const Graph& graph
    ) {
        requireType(graph, GraphType::DIRECTED);

        enum class Color {
            WHITE,
            GRAY,
            BLACK
        };

        unordered_map<int, Color> color;
        unordered_map<int, int> parent;

        for (const auto& [vertex, neighbors] :
             graph.getAdjacency()) {
            color[vertex] = Color::WHITE;
        }

        for (const auto& [start, neighbors] :
             graph.getAdjacency()) {

            if (color[start] != Color::WHITE) {
                continue;
            }

            color[start] = Color::GRAY;
            parent[start] = start;

            vector<pair<int, size_t>> stack;
            stack.push_back({start, 0});

            while (!stack.empty()) {
                int vertex = stack.back().first;
                size_t& index = stack.back().second;

                const auto& adjacent = graph.neighbors(vertex);

                if (index == adjacent.size()) {
                    color[vertex] = Color::BLACK;
                    stack.pop_back();
                    continue;
                }

                int neighbor = adjacent[index++];

                if (color[neighbor] == Color::WHITE) {
                    color[neighbor] = Color::GRAY;
                    parent[neighbor] = vertex;
                    stack.push_back({neighbor, 0});
                } else if (color[neighbor] == Color::GRAY) {
                    vector<int> cycle = {neighbor};
                    int current = vertex;

                    while (current != neighbor) {
                        cycle.push_back(current);
                        current = parent[current];
                    }

                    cycle.push_back(neighbor);
                    reverse(cycle.begin(), cycle.end());

                    return {true, cycle};
                }
            }
        }

        return {false, {}};
    }

    static CycleResult directedCycleKahn(
        const Graph& graph
    ) {
        requireType(graph, GraphType::DIRECTED);

        unordered_map<int, int> indegree;

        for (const auto& [vertex, neighbors] :
             graph.getAdjacency()) {
            indegree[vertex] = 0;
        }

        for (const auto& [vertex, neighbors] :
             graph.getAdjacency()) {
            for (int neighbor : neighbors) {
                indegree[neighbor]++;
            }
        }

        queue<int> ready;

        for (const auto& [vertex, degree] : indegree) {
            if (degree == 0) {
                ready.push(vertex);
            }
        }

        size_t processed = 0;

        while (!ready.empty()) {
            int vertex = ready.front();
            ready.pop();

            processed++;

            for (int neighbor : graph.neighbors(vertex)) {
                indegree[neighbor]--;

                if (indegree[neighbor] == 0) {
                    ready.push(neighbor);
                }
            }
        }

        return {
            processed != graph.size(),
            {}
        };
    }
};

void printComponents(const vector<vector<int>>& components) {
    cout << "Connected components:\n";

    for (size_t i = 0; i < components.size(); i++) {
        cout << "Component " << i + 1 << ": ";

        for (int vertex : components[i]) {
            cout << vertex << " ";
        }

        cout << '\n';
    }

    cout << "Component count: " << components.size() << '\n';
}

void printCycle(const string& label, const CycleResult& result) {
    cout << label << ": "
         << (result.hasCycle ? "YES" : "NO") << '\n';

    if (!result.cycle.empty()) {
        cout << "Cycle path: ";

        for (size_t i = 0; i < result.cycle.size(); i++) {
            if (i > 0) cout << " -> ";
            cout << result.cycle[i];
        }

        cout << '\n';
    }
}

void runTests() {
    Graph graph(GraphType::UNDIRECTED);

    graph.addEdge(1, 2);
    graph.addEdge(2, 3);
    graph.addEdge(3, 1);
    graph.addEdge(4, 5);
    graph.addEdge(6, 7);
    graph.addVertex(8);

    auto components =
        GraphGovernanceEngine::connectedComponents(graph);

    if (components.size() != 4) {
        throw runtime_error("Incorrect component count.");
    }

    if (!GraphGovernanceEngine::undirectedCycleDFS(graph).hasCycle) {
        throw runtime_error("Undirected DFS failed.");
    }

    if (!GraphGovernanceEngine::undirectedCycleDSU(graph).hasCycle) {
        throw runtime_error("Undirected DSU failed.");
    }

    Graph forest(GraphType::UNDIRECTED);

    forest.addEdge(1, 2);
    forest.addEdge(2, 3);
    forest.addEdge(4, 5);

    if (GraphGovernanceEngine::undirectedCycleDFS(forest).hasCycle) {
        throw runtime_error("Forest incorrectly classified.");
    }

    Graph selfLoop(GraphType::UNDIRECTED);
    selfLoop.addEdge(10, 10);

    if (!GraphGovernanceEngine::undirectedCycleDSU(selfLoop).hasCycle) {
        throw runtime_error("Self-loop was not detected.");
    }

    Graph parallel(GraphType::UNDIRECTED);
    parallel.addEdge(1, 2);
    parallel.addEdge(1, 2);

    if (!GraphGovernanceEngine::undirectedCycleDSU(parallel).hasCycle) {
        throw runtime_error("Parallel-edge cycle was not detected.");
    }

    Graph directed(GraphType::DIRECTED);

    directed.addEdge(1, 2);
    directed.addEdge(2, 3);
    directed.addEdge(3, 4);
    directed.addEdge(4, 2);
    directed.addEdge(4, 5);

    if (!GraphGovernanceEngine::directedCycleDFS(directed).hasCycle) {
        throw runtime_error("Directed DFS failed.");
    }

    if (!GraphGovernanceEngine::directedCycleKahn(directed).hasCycle) {
        throw runtime_error("Kahn cycle detection failed.");
    }

    Graph dag(GraphType::DIRECTED);

    dag.addEdge(1, 2);
    dag.addEdge(1, 3);
    dag.addEdge(2, 4);
    dag.addEdge(3, 4);

    if (GraphGovernanceEngine::directedCycleDFS(dag).hasCycle) {
        throw runtime_error("DAG incorrectly classified.");
    }

    if (GraphGovernanceEngine::directedCycleKahn(dag).hasCycle) {
        throw runtime_error("Kahn incorrectly classified DAG.");
    }

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        runTests();

        cout << "\nUNDIRECTED GRAPH ANALYSIS\n";

        Graph undirected(GraphType::UNDIRECTED);

        undirected.addEdge(1, 2);
        undirected.addEdge(2, 3);
        undirected.addEdge(3, 1);
        undirected.addEdge(4, 5);
        undirected.addEdge(6, 7);
        undirected.addVertex(8);

        printComponents(
            GraphGovernanceEngine::connectedComponents(undirected)
        );

        printCycle(
            "Undirected DFS cycle",
            GraphGovernanceEngine::undirectedCycleDFS(undirected)
        );

        printCycle(
            "Undirected DSU cycle",
            GraphGovernanceEngine::undirectedCycleDSU(undirected)
        );

        cout << "\nDIRECTED GRAPH ANALYSIS\n";

        Graph directed(GraphType::DIRECTED);

        directed.addEdge(1, 2);
        directed.addEdge(2, 3);
        directed.addEdge(3, 4);
        directed.addEdge(4, 2);
        directed.addEdge(4, 5);

        printCycle(
            "Directed DFS cycle",
            GraphGovernanceEngine::directedCycleDFS(directed)
        );

        printCycle(
            "Directed Kahn cycle",
            GraphGovernanceEngine::directedCycleKahn(directed)
        );

    } catch (const exception& error) {
        cerr << "Graph analysis failed: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
