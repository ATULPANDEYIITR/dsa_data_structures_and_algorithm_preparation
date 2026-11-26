#include <algorithm>
#include <cmath>
#include <cstddef>
#include <functional>
#include <iomanip>
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

class GraphError : public runtime_error {
public:
    explicit GraphError(const string& message)
        : runtime_error(message) {}
};

class NegativeWeightError : public GraphError {
public:
    NegativeWeightError()
        : GraphError(
            "Dijkstra's algorithm does not support negative weights"
        ) {}
};

struct Edge {
    string destination;
    double weight;
};

struct QueueEntry {
    double distance;
    string vertex;
};

// Priority queue orders entries by minimum distance.
struct CompareDistance {
    bool operator()(
        const QueueEntry& a,
        const QueueEntry& b
    ) const {
        return a.distance > b.distance;
    }
};

struct ShortestPathResult {
    string source;

    unordered_map<string, double> distances;

    unordered_map<string, string> predecessors;

    vector<string> pathTo(const string& destination) const {
        auto it = distances.find(destination);

        if (it == distances.end()) {
            throw GraphError("Destination vertex does not exist");
        }

        if (it->second == numeric_limits<double>::infinity()) {
            return {};
        }

        vector<string> path;
        string current = destination;

        while (current != source) {
            path.push_back(current);

            auto predecessor = predecessors.find(current);

            if (predecessor == predecessors.end()) {
                throw GraphError("Invalid predecessor chain");
            }

            current = predecessor->second;
        }

        path.push_back(source);

        reverse(path.begin(), path.end());

        return path;
    }
};

class WeightedGraph {
private:
    unordered_map<string, vector<Edge>> adjacency;
    bool directed;

public:
    explicit WeightedGraph(bool isDirected = false)
        : directed(isDirected) {}

    void addVertex(const string& vertex) {
        if (vertex.empty()) {
            throw GraphError("Vertex cannot be empty");
        }

        adjacency.try_emplace(vertex);
    }

    void addEdge(
        const string& source,
        const string& destination,
        double weight
    ) {
        if (!isfinite(weight)) {
            throw GraphError("Weight must be finite");
        }

        if (weight < 0) {
            throw NegativeWeightError();
        }

        addVertex(source);
        addVertex(destination);

        adjacency[source].push_back({
            destination,
            weight
        });

        if (!directed) {
            adjacency[destination].push_back({
                source,
                weight
            });
        }
    }

    ShortestPathResult dijkstra(const string& source) const {
        if (adjacency.find(source) == adjacency.end()) {
            throw GraphError("Source vertex does not exist");
        }

        const double INF =
            numeric_limits<double>::infinity();

        ShortestPathResult result;
        result.source = source;

        for (const auto& entry : adjacency) {
            result.distances[entry.first] = INF;
        }

        result.distances[source] = 0.0;

        priority_queue<
            QueueEntry,
            vector<QueueEntry>,
            CompareDistance
        > frontier;

        frontier.push({0.0, source});

        while (!frontier.empty()) {
            QueueEntry current = frontier.top();
            frontier.pop();

            const string& vertex = current.vertex;

            // Lazy deletion: discard outdated queue entries.
            if (
                current.distance >
                result.distances.at(vertex)
            ) {
                continue;
            }

            for (const Edge& edge : adjacency.at(vertex)) {
                double candidate =
                    current.distance + edge.weight;

                if (!isfinite(candidate)) {
                    throw overflow_error(
                        "Shortest-path distance overflow"
                    );
                }

                if (
                    candidate <
                    result.distances.at(edge.destination)
                ) {
                    result.distances[edge.destination] =
                        candidate;

                    result.predecessors[edge.destination] =
                        vertex;

                    frontier.push({
                        candidate,
                        edge.destination
                    });
                }
            }
        }

        return result;
    }

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t edgeCount() const {
        size_t total = 0;

        for (const auto& entry : adjacency) {
            total += entry.second.size();
        }

        return directed ? total : total / 2;
    }
};

void printResult(const ShortestPathResult& result) {
    vector<string> vertices;

    for (const auto& entry : result.distances) {
        vertices.push_back(entry.first);
    }

    sort(vertices.begin(), vertices.end());

    cout << "\nShortest paths from "
         << result.source << "\n";

    cout << left
         << setw(12) << "Vertex"
         << setw(15) << "Distance"
         << "Path\n";

    cout << string(55, '-') << "\n";

    for (const string& vertex : vertices) {
        double distance = result.distances.at(vertex);

        cout << left << setw(12) << vertex;

        if (isinf(distance)) {
            cout << setw(15) << "Unreachable";
        } else {
            cout << setw(15) << distance;

            vector<string> path = result.pathTo(vertex);

            for (size_t i = 0; i < path.size(); ++i) {
                if (i > 0) {
                    cout << " -> ";
                }

                cout << path[i];
            }
        }

        cout << "\n";
    }
}

void runTests() {
    WeightedGraph graph(true);

    graph.addEdge("S", "A", 10);
    graph.addEdge("S", "B", 3);
    graph.addEdge("B", "A", 2);
    graph.addEdge("A", "T", 4);
    graph.addEdge("B", "T", 8);

    auto result = graph.dijkstra("S");

    if (result.distances.at("A") != 5.0) {
        throw GraphError("Test failed: distance to A");
    }

    if (result.distances.at("T") != 9.0) {
        throw GraphError("Test failed: distance to T");
    }

    vector<string> expected = {"S", "B", "A", "T"};

    if (result.pathTo("T") != expected) {
        throw GraphError("Test failed: path reconstruction");
    }

    graph.addVertex("Z");

    result = graph.dijkstra("S");

    if (!isinf(result.distances.at("Z"))) {
        throw GraphError("Test failed: unreachable vertex");
    }

    // Zero-weight edges.
    WeightedGraph zeroGraph(true);

    zeroGraph.addEdge("X", "Y", 0);
    zeroGraph.addEdge("Y", "Z", 0);

    auto zeroResult = zeroGraph.dijkstra("X");

    if (zeroResult.distances.at("Z") != 0) {
        throw GraphError("Test failed: zero-weight edges");
    }

    // Negative weights must be rejected.
    bool negativeRejected = false;

    try {
        graph.addEdge("S", "Z", -1);
    } catch (const NegativeWeightError&) {
        negativeRejected = true;
    }

    if (!negativeRejected) {
        throw GraphError("Test failed: negative weight validation");
    }

    // Unknown source must be rejected.
    bool unknownRejected = false;

    try {
        graph.dijkstra("UNKNOWN");
    } catch (const GraphError&) {
        unknownRejected = true;
    }

    if (!unknownRejected) {
        throw GraphError("Test failed: unknown source validation");
    }

    cout << "\nAll tests passed.\n";
}

int main() {
    try {
        WeightedGraph graph(false);

        vector<tuple<string, string, double>> roads = {
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

        for (const auto& road : roads) {
            graph.addEdge(
                get<0>(road),
                get<1>(road),
                get<2>(road)
            );
        }

        graph.addVertex("G");

        cout << "DIJKSTRA SHORTEST-PATH ENGINE\n";

        cout << "Vertices: "
             << graph.vertexCount() << "\n";

        cout << "Edges: "
             << graph.edgeCount() << "\n";

        auto result = graph.dijkstra("A");

        printResult(result);

        cout << "\nRunning validation tests...\n";

        runTests();

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
