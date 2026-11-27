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
#include <vector>

using namespace std;

using Vertex = int;
using Weight = long long;

struct Edge {
    Vertex source;
    Vertex destination;
    Weight weight;
};

enum class Algorithm {
    BELLMAN_FORD,
    DIJKSTRA
};

struct ShortestPathResult {
    Vertex source;

    unordered_map<Vertex, Weight> distances;
    unordered_map<Vertex, Vertex> predecessors;

    unordered_set<Vertex> affected;
    bool negativeCycle = false;

    int iterations = 0;
    Algorithm algorithm = Algorithm::BELLMAN_FORD;
};

class GraphError : public runtime_error {
public:
    explicit GraphError(const string& message)
        : runtime_error(message) {}
};

class WeightedGraph {
private:
    vector<Vertex> vertices;
    unordered_set<Vertex> vertexSet;

    vector<Edge> edges;

    unordered_map<Vertex, vector<pair<Vertex, Weight>>> adjacency;

    static constexpr Weight INF =
        numeric_limits<Weight>::max() / 4;

    void validateSource(Vertex source) const {
        if (!vertexSet.count(source)) {
            throw GraphError("Unknown source vertex.");
        }
    }

    static Weight safeAdd(Weight first, Weight second) {
        // __int128 prevents intermediate signed integer overflow.
        __int128 result =
            static_cast<__int128>(first) + second;

        if (result >= INF || result <= -INF) {
            throw GraphError("Distance exceeds supported numeric range.");
        }

        return static_cast<Weight>(result);
    }

public:
    explicit WeightedGraph(const vector<Vertex>& inputVertices) {
        if (inputVertices.empty()) {
            throw GraphError("Graph cannot be empty.");
        }

        for (Vertex vertex : inputVertices) {
            if (!vertexSet.insert(vertex).second) {
                throw GraphError("Duplicate vertex identifier.");
            }

            vertices.push_back(vertex);
            adjacency[vertex] = {};
        }
    }

    void addEdge(Vertex source, Vertex destination, Weight weight) {
        if (!vertexSet.count(source) ||
            !vertexSet.count(destination)) {
            throw GraphError("Edge references an unknown vertex.");
        }

        edges.push_back({source, destination, weight});

        adjacency[source].push_back({destination, weight});
    }

    ShortestPathResult bellmanFord(Vertex source) const {
        validateSource(source);

        ShortestPathResult result;
        result.source = source;
        result.algorithm = Algorithm::BELLMAN_FORD;

        for (Vertex vertex : vertices) {
            result.distances[vertex] = INF;
            result.predecessors[vertex] = -1;
        }

        result.distances[source] = 0;

        const size_t V = vertices.size();

        // V-1 relaxation passes.
        for (size_t pass = 1; pass < V; ++pass) {
            bool changed = false;
            result.iterations++;

            for (const Edge& edge : edges) {
                Weight current = result.distances[edge.source];

                if (current == INF) {
                    continue;
                }

                Weight candidate = safeAdd(current, edge.weight);

                if (candidate < result.distances[edge.destination]) {
                    result.distances[edge.destination] = candidate;

                    result.predecessors[edge.destination] =
                        edge.source;

                    changed = true;
                }
            }

            // Early termination when no relaxation succeeds.
            if (!changed) {
                break;
            }
        }

        // An edge that remains relaxable indicates a reachable
        // negative-weight cycle.
        for (const Edge& edge : edges) {
            Weight current = result.distances[edge.source];

            if (current == INF) {
                continue;
            }

            Weight candidate = safeAdd(current, edge.weight);

            if (candidate < result.distances[edge.destination]) {
                result.affected.insert(edge.destination);
            }
        }

        // Every vertex reachable from a negative-cycle-affected
        // vertex also has an undefined shortest distance.
        queue<Vertex> pending;

        for (Vertex vertex : result.affected) {
            pending.push(vertex);
        }

        while (!pending.empty()) {
            Vertex current = pending.front();
            pending.pop();

            for (const auto& [neighbor, weight] : adjacency.at(current)) {
                if (result.affected.insert(neighbor).second) {
                    pending.push(neighbor);
                }
            }
        }

        result.negativeCycle = !result.affected.empty();

        return result;
    }

    ShortestPathResult dijkstra(Vertex source) const {
        validateSource(source);

        for (const Edge& edge : edges) {
            if (edge.weight < 0) {
                throw GraphError(
                    "Dijkstra cannot process negative edge weights."
                );
            }
        }

        ShortestPathResult result;
        result.source = source;
        result.algorithm = Algorithm::DIJKSTRA;

        for (Vertex vertex : vertices) {
            result.distances[vertex] = INF;
            result.predecessors[vertex] = -1;
        }

        using QueueEntry = pair<Weight, Vertex>;

        priority_queue<
            QueueEntry,
            vector<QueueEntry>,
            greater<QueueEntry>
        > pending;

        result.distances[source] = 0;
        pending.push({0, source});

        unordered_set<Vertex> settled;

        while (!pending.empty()) {
            auto [distance, current] = pending.top();
            pending.pop();

            result.iterations++;

            if (distance != result.distances[current]) {
                continue;
            }

            if (!settled.insert(current).second) {
                continue;
            }

            for (const auto& [neighbor, weight] : adjacency.at(current)) {
                Weight candidate = safeAdd(distance, weight);

                if (candidate < result.distances[neighbor]) {
                    result.distances[neighbor] = candidate;
                    result.predecessors[neighbor] = current;

                    pending.push({candidate, neighbor});
                }
            }
        }

        return result;
    }

    vector<Vertex> reconstructPath(
        const ShortestPathResult& result,
        Vertex destination
    ) const {
        if (!vertexSet.count(destination)) {
            throw GraphError("Unknown destination vertex.");
        }

        if (result.affected.count(destination)) {
            throw GraphError(
                "Shortest path is undefined due to a negative cycle."
            );
        }

        if (result.distances.at(destination) == INF) {
            return {};
        }

        vector<Vertex> path;
        unordered_set<Vertex> visited;

        Vertex current = destination;

        while (current != -1) {
            if (!visited.insert(current).second) {
                throw GraphError("Predecessor cycle detected.");
            }

            path.push_back(current);
            current = result.predecessors.at(current);
        }

        reverse(path.begin(), path.end());

        if (path.empty() || path.front() != result.source) {
            return {};
        }

        return path;
    }

    void display(const ShortestPathResult& result) const {
        cout << "\nAlgorithm: "
             << (result.algorithm == Algorithm::BELLMAN_FORD
                     ? "Bellman-Ford"
                     : "Dijkstra")
             << "\n";

        cout << "Source: " << result.source << "\n";
        cout << "Iterations: " << result.iterations << "\n";
        cout << "Negative cycle: "
             << (result.negativeCycle ? "Yes" : "No") << "\n\n";

        cout << "Vertex\tDistance\tPath\n";

        for (Vertex vertex : vertices) {
            cout << vertex << "\t";

            if (result.affected.count(vertex)) {
                cout << "Undefined\tNegative cycle\n";
                continue;
            }

            if (result.distances.at(vertex) == INF) {
                cout << "Unreachable\tNone\n";
                continue;
            }

            cout << result.distances.at(vertex) << "\t\t";

            vector<Vertex> path = reconstructPath(result, vertex);

            for (size_t i = 0; i < path.size(); ++i) {
                if (i > 0) {
                    cout << " -> ";
                }

                cout << path[i];
            }

            cout << "\n";
        }
    }

    const vector<Vertex>& getVertices() const {
        return vertices;
    }
};

void demonstrateNegativeEdges() {
    cout << "\n========== NEGATIVE EDGES ==========\n";

    WeightedGraph graph({0, 1, 2, 3, 4, 5});

    graph.addEdge(0, 1, 4);
    graph.addEdge(0, 2, 5);
    graph.addEdge(1, 2, -2);
    graph.addEdge(1, 3, 6);
    graph.addEdge(2, 3, 3);
    graph.addEdge(3, 4, 2);
    graph.addEdge(4, 1, 1);

    auto result = graph.bellmanFord(0);

    graph.display(result);

    assert(result.distances.at(1) == 4);
    assert(result.distances.at(2) == 2);
    assert(result.distances.at(3) == 5);
    assert(result.distances.at(4) == 7);
    assert(!result.negativeCycle);

    try {
        graph.dijkstra(0);
        assert(false);
    } catch (const GraphError& error) {
        cout << "\nDijkstra rejected: " << error.what() << "\n";
    }
}

void demonstrateNegativeCycle() {
    cout << "\n========== NEGATIVE CYCLE ==========\n";

    WeightedGraph graph({0, 1, 2, 3, 4, 5});

    graph.addEdge(0, 1, 2);
    graph.addEdge(1, 2, 2);
    graph.addEdge(2, 3, -5);
    graph.addEdge(3, 1, 1);
    graph.addEdge(3, 4, 3);
    graph.addEdge(5, 5, -1);

    auto result = graph.bellmanFord(0);

    graph.display(result);

    assert(result.negativeCycle);
    assert(result.affected.count(1));
    assert(result.affected.count(2));
    assert(result.affected.count(3));
    assert(result.affected.count(4));

    // The negative self-loop at vertex 5 is unreachable.
    assert(!result.affected.count(5));
}

void demonstrateDijkstraComparison() {
    cout << "\n========== DIJKSTRA COMPARISON ==========\n";

    WeightedGraph graph({0, 1, 2, 3, 4});

    graph.addEdge(0, 1, 10);
    graph.addEdge(0, 2, 3);
    graph.addEdge(2, 1, 2);
    graph.addEdge(1, 3, 4);
    graph.addEdge(2, 3, 8);
    graph.addEdge(2, 4, 2);
    graph.addEdge(4, 3, 1);

    auto bellman = graph.bellmanFord(0);
    auto dijkstra = graph.dijkstra(0);

    graph.display(bellman);
    graph.display(dijkstra);

    for (Vertex vertex : graph.getVertices()) {
        assert(
            bellman.distances.at(vertex) ==
            dijkstra.distances.at(vertex)
        );
    }

    cout << "\nBoth algorithms returned identical distances.\n";
}

void demonstrateValidation() {
    cout << "\n========== VALIDATION ==========\n";

    try {
        WeightedGraph graph({0, 1});
        graph.addEdge(0, 5, 10);
    } catch (const GraphError& error) {
        cout << error.what() << "\n";
    }

    try {
        WeightedGraph graph({0, 1});
        graph.bellmanFord(9);
    } catch (const GraphError& error) {
        cout << error.what() << "\n";
    }
}

int main() {
    try {
        demonstrateNegativeEdges();
        demonstrateNegativeCycle();
        demonstrateDijkstraComparison();
        demonstrateValidation();

        cout << "\nAll C++17 tests passed.\n";
    } catch (const exception& error) {
        cerr << "Execution failed: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
