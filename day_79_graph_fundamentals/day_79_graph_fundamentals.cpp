#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

/*
 * Graph Fundamentals: Repository-Scale Network Governance Model.
 *
 * Demonstrates:
 * - Vertex and edge representation
 * - Directed and undirected graphs
 * - Weighted and unweighted graphs
 * - Degree calculations
 * - Adjacency lists and matrices
 * - BFS and DFS
 * - Connected components
 * - Cycle detection
 * - Dijkstra shortest paths
 * - Graph integrity validation
 */

enum class GraphType {
    Directed,
    Undirected
};

struct Edge {
    string source;
    string target;
    double weight;
};

class Graph {
private:
    map<string, map<string, double>> adjacency;
    GraphType type;
    bool weighted;
    size_t edgeCount = 0;

    void requireVertex(const string& vertex) const {
        if (adjacency.find(vertex) == adjacency.end()) {
            throw out_of_range("Unknown vertex: " + vertex);
        }
    }

public:
    explicit Graph(
        GraphType graphType = GraphType::Undirected,
        bool isWeighted = false
    ) : type(graphType), weighted(isWeighted) {}

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t getEdgeCount() const {
        return edgeCount;
    }

    bool isDirected() const {
        return type == GraphType::Directed;
    }

    void addVertex(const string& vertex) {
        if (vertex.empty()) {
            throw invalid_argument("Vertex identifier cannot be empty.");
        }

        adjacency.try_emplace(vertex);
    }

    void addEdge(
        const string& source,
        const string& target,
        double weight = 1.0
    ) {
        if (!isfinite(weight)) {
            throw invalid_argument("Weight must be finite.");
        }

        if (!weighted && weight != 1.0) {
            throw invalid_argument(
                "Unweighted graph requires edge weight 1."
            );
        }

        addVertex(source);
        addVertex(target);

        bool exists = adjacency[source].count(target) > 0;

        adjacency[source][target] = weight;

        if (!isDirected()) {
            adjacency[target][source] = weight;
        }

        if (!exists) {
            ++edgeCount;
        }

        validate();
    }

    void removeEdge(
        const string& source,
        const string& target
    ) {
        requireVertex(source);
        requireVertex(target);

        if (!adjacency[source].count(target)) {
            throw invalid_argument("Edge does not exist.");
        }

        adjacency[source].erase(target);

        if (!isDirected()) {
            adjacency[target].erase(source);
        }

        --edgeCount;
    }

    void removeVertex(const string& vertex) {
        requireVertex(vertex);

        if (isDirected()) {
            size_t outgoing = adjacency[vertex].size();
            size_t incoming = 0;

            for (auto& [source, neighbors] : adjacency) {
                if (neighbors.erase(vertex)) {
                    ++incoming;
                }
            }

            edgeCount -= outgoing + incoming;
        } else {
            edgeCount -= adjacency[vertex].size();

            for (auto& [other, neighbors] : adjacency) {
                neighbors.erase(vertex);
            }
        }

        adjacency.erase(vertex);
    }

    size_t degree(const string& vertex) const {
        requireVertex(vertex);

        if (isDirected()) {
            throw logic_error(
                "Directed graphs require inDegree/outDegree."
            );
        }

        return adjacency.at(vertex).size();
    }

    size_t inDegree(const string& vertex) const {
        requireVertex(vertex);

        if (!isDirected()) {
            throw logic_error("In-degree requires directed graph.");
        }

        size_t count = 0;

        for (const auto& [source, neighbors] : adjacency) {
            if (neighbors.count(vertex)) {
                ++count;
            }
        }

        return count;
    }

    size_t outDegree(const string& vertex) const {
        requireVertex(vertex);

        if (!isDirected()) {
            throw logic_error("Out-degree requires directed graph.");
        }

        return adjacency.at(vertex).size();
    }

    vector<string> bfs(const string& start) const {
        requireVertex(start);

        unordered_set<string> visited;
        queue<string> pending;
        vector<string> result;

        visited.insert(start);
        pending.push(start);

        while (!pending.empty()) {
            string current = pending.front();
            pending.pop();

            result.push_back(current);

            for (const auto& [neighbor, weight] : adjacency.at(current)) {
                if (visited.insert(neighbor).second) {
                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    vector<string> dfs(const string& start) const {
        requireVertex(start);

        unordered_set<string> visited;
        vector<string> stack;
        vector<string> result;

        stack.push_back(start);

        while (!stack.empty()) {
            string current = stack.back();
            stack.pop_back();

            if (!visited.insert(current).second) {
                continue;
            }

            result.push_back(current);

            const auto& neighbors = adjacency.at(current);

            for (
                auto iterator = neighbors.rbegin();
                iterator != neighbors.rend();
                ++iterator
            ) {
                if (!visited.count(iterator->first)) {
                    stack.push_back(iterator->first);
                }
            }
        }

        return result;
    }

    vector<vector<string>> connectedComponents() const {
        if (isDirected()) {
            throw logic_error(
                "Connected components require an undirected graph."
            );
        }

        unordered_set<string> visited;
        vector<vector<string>> components;

        for (const auto& [vertex, neighbors] : adjacency) {
            if (!visited.count(vertex)) {
                vector<string> component = bfs(vertex);

                for (const string& member : component) {
                    visited.insert(member);
                }

                components.push_back(component);
            }
        }

        return components;
    }

    bool hasCycle() const {
        if (!isDirected()) {
            unordered_set<string> visited;

            function<bool(const string&, const string&)> dfsVisit =
                [&](const string& vertex, const string& parent) {
                    visited.insert(vertex);

                    for (
                        const auto& [neighbor, weight]
                        : adjacency.at(vertex)
                    ) {
                        if (!visited.count(neighbor)) {
                            if (dfsVisit(neighbor, vertex)) {
                                return true;
                            }
                        } else if (neighbor != parent) {
                            return true;
                        }
                    }

                    return false;
                };

            for (const auto& [vertex, neighbors] : adjacency) {
                if (
                    !visited.count(vertex) &&
                    dfsVisit(vertex, "")
                ) {
                    return true;
                }
            }

            return false;
        }

        // 0 = unvisited, 1 = active, 2 = completed.
        map<string, int> color;

        for (const auto& [vertex, neighbors] : adjacency) {
            color[vertex] = 0;
        }

        function<bool(const string&)> dfsVisit =
            [&](const string& vertex) {
                color[vertex] = 1;

                for (
                    const auto& [neighbor, weight]
                    : adjacency.at(vertex)
                ) {
                    if (color[neighbor] == 1) {
                        return true;
                    }

                    if (
                        color[neighbor] == 0 &&
                        dfsVisit(neighbor)
                    ) {
                        return true;
                    }
                }

                color[vertex] = 2;
                return false;
            };

        for (const auto& [vertex, neighbors] : adjacency) {
            if (color[vertex] == 0 && dfsVisit(vertex)) {
                return true;
            }
        }

        return false;
    }

    map<string, double> dijkstra(const string& start) const {
        requireVertex(start);

        for (const auto& [vertex, neighbors] : adjacency) {
            for (const auto& [neighbor, weight] : neighbors) {
                if (weight < 0) {
                    throw invalid_argument(
                        "Dijkstra cannot process negative weights."
                    );
                }
            }
        }

        const double INF = numeric_limits<double>::infinity();

        map<string, double> distances;

        for (const auto& [vertex, neighbors] : adjacency) {
            distances[vertex] = INF;
        }

        using QueueEntry = pair<double, string>;

        priority_queue<
            QueueEntry,
            vector<QueueEntry>,
            greater<QueueEntry>
        > pending;

        distances[start] = 0;
        pending.push({0, start});

        while (!pending.empty()) {
            auto [distance, current] = pending.top();
            pending.pop();

            if (distance != distances[current]) {
                continue;
            }

            for (
                const auto& [neighbor, weight]
                : adjacency.at(current)
            ) {
                double candidate = distance + weight;

                if (candidate < distances[neighbor]) {
                    distances[neighbor] = candidate;
                    pending.push({candidate, neighbor});
                }
            }
        }

        return distances;
    }

    vector<vector<double>> adjacencyMatrix(
        vector<string>& vertices
    ) const {
        vertices.clear();

        for (const auto& [vertex, neighbors] : adjacency) {
            vertices.push_back(vertex);
        }

        const size_t n = vertices.size();

        vector<vector<double>> matrix(
            n,
            vector<double>(n, numeric_limits<double>::infinity())
        );

        map<string, size_t> indices;

        for (size_t i = 0; i < n; ++i) {
            indices[vertices[i]] = i;
            matrix[i][i] = 0;
        }

        for (const auto& [source, neighbors] : adjacency) {
            for (const auto& [target, weight] : neighbors) {
                matrix[indices[source]][indices[target]] = weight;
            }
        }

        return matrix;
    }

    void validate() const {
        size_t calculatedEdges = 0;

        for (const auto& [source, neighbors] : adjacency) {
            for (const auto& [target, weight] : neighbors) {
                if (!isfinite(weight)) {
                    throw logic_error("Invalid stored edge weight.");
                }

                if (!adjacency.count(target)) {
                    throw logic_error("Edge references missing vertex.");
                }

                if (!isDirected()) {
                    auto reverse = adjacency.at(target).find(source);

                    if (reverse == adjacency.at(target).end()) {
                        throw logic_error(
                            "Undirected edge is missing its reverse."
                        );
                    }

                    if (reverse->second != weight) {
                        throw logic_error(
                            "Undirected edge weights are inconsistent."
                        );
                    }

                    if (source <= target) {
                        ++calculatedEdges;
                    }
                } else {
                    ++calculatedEdges;
                }
            }
        }

        if (calculatedEdges != edgeCount) {
            throw logic_error("Edge count invariant violated.");
        }
    }

    void print() const {
        cout << "\nAdjacency List:\n";

        for (const auto& [vertex, neighbors] : adjacency) {
            cout << vertex << " -> ";

            for (const auto& [neighbor, weight] : neighbors) {
                cout << neighbor;

                if (weighted) {
                    cout << "(" << weight << ")";
                }

                cout << " ";
            }

            cout << "\n";
        }
    }
};

void printTraversal(
    const string& label,
    const vector<string>& traversal
) {
    cout << label;

    for (const string& vertex : traversal) {
        cout << vertex << " ";
    }

    cout << "\n";
}

void demonstrateUndirectedGraph() {
    cout << "\n=== UNDIRECTED GRAPH ===\n";

    Graph graph(GraphType::Undirected);

    graph.addEdge("A", "B");
    graph.addEdge("A", "C");
    graph.addEdge("B", "D");
    graph.addEdge("C", "D");
    graph.addEdge("D", "E");
    graph.addVertex("F");

    graph.print();

    cout << "Vertices: " << graph.vertexCount() << "\n";
    cout << "Edges: " << graph.getEdgeCount() << "\n";
    cout << "Degree of A: " << graph.degree("A") << "\n";
    cout << "Degree of D: " << graph.degree("D") << "\n";

    printTraversal("BFS: ", graph.bfs("A"));
    printTraversal("DFS: ", graph.dfs("A"));

    cout << "Contains cycle: "
         << boolalpha << graph.hasCycle() << "\n";

    auto components = graph.connectedComponents();

    cout << "Connected components: " << components.size() << "\n";

    for (const auto& component : components) {
        printTraversal("Component: ", component);
    }
}

void demonstrateDirectedGraph() {
    cout << "\n=== DIRECTED GRAPH ===\n";

    Graph graph(GraphType::Directed);

    graph.addEdge("Frontend", "API");
    graph.addEdge("API", "Database");
    graph.addEdge("API", "Cache");
    graph.addEdge("Database", "Backup");
    graph.addEdge("Cache", "Database");

    graph.print();

    for (
        const string& vertex :
        {"Frontend", "API", "Database", "Cache", "Backup"}
    ) {
        cout << vertex
             << " | in-degree=" << graph.inDegree(vertex)
             << " | out-degree=" << graph.outDegree(vertex)
             << "\n";
    }

    cout << "Contains cycle: "
         << graph.hasCycle() << "\n";
}

void demonstrateWeightedGraph() {
    cout << "\n=== WEIGHTED GRAPH ===\n";

    Graph graph(GraphType::Undirected, true);

    graph.addEdge("A", "B", 4);
    graph.addEdge("A", "C", 2);
    graph.addEdge("C", "B", 1);
    graph.addEdge("B", "D", 5);
    graph.addEdge("C", "D", 8);
    graph.addEdge("D", "E", 2);

    graph.print();

    auto distances = graph.dijkstra("A");

    cout << "\nShortest distances from A:\n";

    for (const auto& [vertex, distance] : distances) {
        cout << vertex << ": " << distance << "\n";
    }
}

void demonstrateMatrix() {
    cout << "\n=== ADJACENCY MATRIX ===\n";

    Graph graph(GraphType::Undirected);

    graph.addEdge("A", "B");
    graph.addEdge("A", "C");
    graph.addEdge("B", "C");

    vector<string> vertices;
    auto matrix = graph.adjacencyMatrix(vertices);

    cout << "    ";

    for (const string& vertex : vertices) {
        cout << setw(5) << vertex;
    }

    cout << "\n";

    for (size_t i = 0; i < matrix.size(); ++i) {
        cout << setw(4) << vertices[i];

        for (double value : matrix[i]) {
            if (isinf(value)) {
                cout << setw(5) << "-";
            } else {
                cout << setw(5) << value;
            }
        }

        cout << "\n";
    }
}

void testGraph() {
    Graph graph;

    graph.addEdge("1", "2");
    graph.addEdge("2", "3");

    if (graph.vertexCount() != 3 ||
        graph.getEdgeCount() != 2 ||
        graph.degree("2") != 2 ||
        graph.hasCycle()) {
        throw runtime_error("Basic graph tests failed.");
    }

    graph.addEdge("3", "1");

    if (!graph.hasCycle()) {
        throw runtime_error("Cycle detection test failed.");
    }

    Graph directed(GraphType::Directed);

    directed.addEdge("A", "B");
    directed.addEdge("A", "C");
    directed.addEdge("C", "B");

    if (directed.inDegree("B") != 2 ||
        directed.outDegree("A") != 2) {
        throw runtime_error("Directed degree test failed.");
    }

    Graph weighted(GraphType::Undirected, true);

    weighted.addEdge("A", "B", 3);
    weighted.addEdge("B", "C", 2);

    if (weighted.dijkstra("A").at("C") != 5) {
        throw runtime_error("Shortest-path test failed.");
    }

    cout << "\nAll graph tests passed.\n";
}

int main() {
    try {
        demonstrateUndirectedGraph();
        demonstrateDirectedGraph();
        demonstrateWeightedGraph();
        demonstrateMatrix();
        testGraph();

    } catch (const exception& error) {
        cerr << "Graph execution error: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
