#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * Graph Representation Engine
 *
 * C++17 implementation of:
 * - Adjacency matrix
 * - Adjacency list
 * - Directed and undirected graphs
 * - Weighted edges
 * - BFS and DFS
 * - Vertex and edge mutation
 * - Graph statistics
 * - Representation comparison
 */

class GraphException : public runtime_error {
public:
    explicit GraphException(const string& message)
        : runtime_error(message) {}
};

struct Edge {
    string source;
    string target;
    double weight;
};

class Graph {
private:
    bool directed;
    bool weighted;

    vector<string> vertices;
    unordered_map<string, size_t> index;

    vector<vector<optional<double>>> matrix;

    unordered_map<
        string,
        unordered_map<string, double>
    > adjacency;

    void validateVertex(const string& vertex) const {
        if (index.find(vertex) == index.end()) {
            throw GraphException(
                "Unknown vertex: " + vertex
            );
        }
    }

    void validateWeight(double weight) const {
        if (!isfinite(weight)) {
            throw GraphException(
                "Edge weight must be finite."
            );
        }

        if (!weighted && weight != 1.0) {
            throw GraphException(
                "Unweighted graphs require weight 1."
            );
        }
    }

    void rebuildIndices() {
        index.clear();

        for (size_t i = 0; i < vertices.size(); ++i) {
            index[vertices[i]] = i;
        }
    }

public:
    explicit Graph(
        bool isDirected = false,
        bool isWeighted = false
    )
        : directed(isDirected), weighted(isWeighted) {}

    void addVertex(const string& vertex) {
        if (vertex.empty()) {
            throw GraphException(
                "Vertex cannot be empty."
            );
        }

        if (index.count(vertex)) {
            return;
        }

        index[vertex] = vertices.size();
        vertices.push_back(vertex);

        for (auto& row : matrix) {
            row.push_back(nullopt);
        }

        matrix.emplace_back(vertices.size(), nullopt);
        adjacency[vertex] = {};
    }

    void addEdge(
        const string& source,
        const string& target,
        double weight = 1.0
    ) {
        validateVertex(source);
        validateVertex(target);
        validateWeight(weight);

        size_t i = index.at(source);
        size_t j = index.at(target);

        matrix[i][j] = weight;
        adjacency[source][target] = weight;

        if (!directed) {
            matrix[j][i] = weight;
            adjacency[target][source] = weight;
        }
    }

    bool removeEdge(
        const string& source,
        const string& target
    ) {
        validateVertex(source);
        validateVertex(target);

        size_t i = index.at(source);
        size_t j = index.at(target);

        bool existed = matrix[i][j].has_value();

        matrix[i][j] = nullopt;
        adjacency[source].erase(target);

        if (!directed) {
            matrix[j][i] = nullopt;
            adjacency[target].erase(source);
        }

        return existed;
    }

    void removeVertex(const string& vertex) {
        validateVertex(vertex);

        size_t position = index.at(vertex);

        vertices.erase(vertices.begin() + position);
        matrix.erase(matrix.begin() + position);

        for (auto& row : matrix) {
            row.erase(row.begin() + position);
        }

        adjacency.erase(vertex);

        for (auto& [name, neighbors] : adjacency) {
            neighbors.erase(vertex);
        }

        rebuildIndices();
    }

    bool hasEdge(
        const string& source,
        const string& target
    ) const {
        validateVertex(source);
        validateVertex(target);

        return matrix[index.at(source)][index.at(target)]
            .has_value();
    }

    optional<double> getWeight(
        const string& source,
        const string& target
    ) const {
        validateVertex(source);
        validateVertex(target);

        return matrix[index.at(source)][index.at(target)];
    }

    vector<string> neighbors(const string& vertex) const {
        validateVertex(vertex);

        vector<string> result;

        for (const auto& [neighbor, weight] :
             adjacency.at(vertex)) {
            result.push_back(neighbor);
        }

        sort(result.begin(), result.end());

        return result;
    }

    size_t outDegree(const string& vertex) const {
        validateVertex(vertex);
        return adjacency.at(vertex).size();
    }

    size_t inDegree(const string& vertex) const {
        validateVertex(vertex);

        size_t count = 0;

        for (const auto& [name, neighbors] : adjacency) {
            if (neighbors.count(vertex)) {
                ++count;
            }
        }

        return count;
    }

    size_t degree(const string& vertex) const {
        validateVertex(vertex);

        if (!directed) {
            return outDegree(vertex);
        }

        return inDegree(vertex) + outDegree(vertex);
    }

    size_t vertexCount() const {
        return vertices.size();
    }

    size_t edgeCount() const {
        size_t count = 0;
        size_t selfLoops = 0;

        for (const auto& [vertex, neighbors] : adjacency) {
            count += neighbors.size();

            if (neighbors.count(vertex)) {
                ++selfLoops;
            }
        }

        return directed
            ? count
            : (count + selfLoops) / 2;
    }

    vector<string> bfs(const string& start) const {
        validateVertex(start);

        unordered_set<string> visited;
        queue<string> pending;

        vector<string> result;

        visited.insert(start);
        pending.push(start);

        while (!pending.empty()) {
            string current = pending.front();
            pending.pop();

            result.push_back(current);

            for (const auto& [neighbor, weight] :
                 adjacency.at(current)) {
                if (visited.insert(neighbor).second) {
                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    vector<string> dfs(const string& start) const {
        validateVertex(start);

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

            vector<string> adjacent = neighbors(current);

            for (
                auto it = adjacent.rbegin();
                it != adjacent.rend();
                ++it
            ) {
                if (!visited.count(*it)) {
                    stack.push_back(*it);
                }
            }
        }

        return result;
    }

    void displayMatrix() const {
        cout << "\nADJACENCY MATRIX\n";

        cout << setw(8) << " ";

        for (const auto& vertex : vertices) {
            cout << setw(8) << vertex;
        }

        cout << '\n';

        for (size_t i = 0; i < vertices.size(); ++i) {
            cout << setw(8) << vertices[i];

            for (size_t j = 0; j < vertices.size(); ++j) {
                if (matrix[i][j].has_value()) {
                    cout << setw(8) << *matrix[i][j];
                } else {
                    cout << setw(8) << "-";
                }
            }

            cout << '\n';
        }
    }

    void displayList() const {
        cout << "\nADJACENCY LIST\n";

        for (const auto& vertex : vertices) {
            cout << vertex << ": ";

            auto adjacent = neighbors(vertex);

            if (adjacent.empty()) {
                cout << "None";
            }

            for (size_t i = 0; i < adjacent.size(); ++i) {
                cout << adjacent[i]
                     << "("
                     << adjacency.at(vertex).at(adjacent[i])
                     << ")";

                if (i + 1 < adjacent.size()) {
                    cout << ", ";
                }
            }

            cout << '\n';
        }
    }

    void compare() const {
        size_t V = vertexCount();
        size_t E = edgeCount();

        size_t listEntries = 0;

        for (const auto& [vertex, neighbors] : adjacency) {
            listEntries += neighbors.size();
        }

        double possibleEdges = directed
            ? static_cast<double>(V) * (V - 1)
            : static_cast<double>(V) * (V - 1) / 2.0;

        double density = possibleEdges == 0
            ? 0.0
            : static_cast<double>(E) / possibleEdges;

        cout << "\nGRAPH STATISTICS\n";
        cout << "Vertices: " << V << '\n';
        cout << "Edges: " << E << '\n';
        cout << "Matrix cells: " << V * V << '\n';
        cout << "Adjacency entries: " << listEntries << '\n';

        cout << fixed << setprecision(4);
        cout << "Density: " << density << '\n';

        cout << "\nTHEORETICAL COMPLEXITY\n";
        cout << left
             << setw(25) << "Operation"
             << setw(20) << "Matrix"
             << "List\n";

        cout << setw(25) << "Space"
             << setw(20) << "O(V^2)"
             << "O(V + E)\n";

        cout << setw(25) << "Edge lookup"
             << setw(20) << "O(1)"
             << "O(degree)\n";

        cout << setw(25) << "Neighbor iteration"
             << setw(20) << "O(V)"
             << "O(degree)\n";

        cout << setw(25) << "Edge insertion"
             << setw(20) << "O(1)"
             << "O(1) average\n";

        cout << setw(25) << "BFS / DFS"
             << setw(20) << "O(V^2)"
             << "O(V + E)\n";
    }

    const vector<string>& getVertices() const {
        return vertices;
    }
};

void runTests() {
    Graph graph(false, false);

    graph.addVertex("A");
    graph.addVertex("B");
    graph.addVertex("C");

    graph.addEdge("A", "B");

    if (!graph.hasEdge("A", "B")) {
        throw GraphException("Edge insertion test failed.");
    }

    if (!graph.hasEdge("B", "A")) {
        throw GraphException("Undirected symmetry test failed.");
    }

    if (graph.edgeCount() != 1) {
        throw GraphException("Edge count test failed.");
    }

    if (graph.degree("A") != 1) {
        throw GraphException("Degree test failed.");
    }

    graph.removeEdge("A", "B");

    if (graph.hasEdge("A", "B")) {
        throw GraphException("Edge removal test failed.");
    }

    Graph directed(true, false);

    directed.addVertex("X");
    directed.addVertex("Y");
    directed.addEdge("X", "Y");

    if (directed.outDegree("X") != 1 ||
        directed.inDegree("Y") != 1 ||
        directed.hasEdge("Y", "X")) {
        throw GraphException("Directed graph test failed.");
    }

    directed.removeVertex("Y");

    if (directed.vertexCount() != 1) {
        throw GraphException("Vertex removal test failed.");
    }

    cout << "All tests passed.\n";
}

Graph buildSampleGraph() {
    Graph graph(false, true);

    for (const string& vertex :
         {"A", "B", "C", "D", "E", "F"}) {
        graph.addVertex(vertex);
    }

    vector<Edge> edges = {
        {"A", "B", 4},
        {"A", "C", 2},
        {"B", "C", 1},
        {"B", "D", 5},
        {"C", "D", 8},
        {"C", "E", 10},
        {"D", "E", 2},
        {"D", "F", 6},
        {"E", "F", 3}
    };

    for (const auto& edge : edges) {
        graph.addEdge(
            edge.source,
            edge.target,
            edge.weight
        );
    }

    return graph;
}

int main() {
    try {
        runTests();

        Graph graph = buildSampleGraph();

        graph.displayMatrix();
        graph.displayList();

        cout << "\nGRAPH TRAVERSALS\n";

        cout << "BFS: ";

        for (const auto& vertex : graph.bfs("A")) {
            cout << vertex << " ";
        }

        cout << "\nDFS: ";

        for (const auto& vertex : graph.dfs("A")) {
            cout << vertex << " ";
        }

        cout << '\n';

        cout << "\nVERTEX DEGREES\n";

        for (const auto& vertex : graph.getVertices()) {
            cout << vertex
                 << ": "
                 << graph.degree(vertex)
                 << '\n';
        }

        graph.compare();

        cout << "\nGRAPH MUTATIONS\n";

        cout << "Removed C-E: "
             << boolalpha
             << graph.removeEdge("C", "E")
             << '\n';

        graph.removeVertex("F");

        cout << "Vertices after removing F: ";

        for (const auto& vertex : graph.getVertices()) {
            cout << vertex << " ";
        }

        cout << '\n';

        try {
            graph.addEdge("A", "UNKNOWN");
        } catch (const GraphException& error) {
            cout << "Expected validation error: "
                 << error.what()
                 << '\n';
        }

    } catch (const exception& error) {
        cerr << "Execution failed: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
