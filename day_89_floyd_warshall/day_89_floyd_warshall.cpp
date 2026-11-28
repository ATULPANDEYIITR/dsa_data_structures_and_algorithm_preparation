#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

class NegativeCycleException : public runtime_error {
public:
    explicit NegativeCycleException(const string& message)
        : runtime_error(message) {}
};

class WeightedGraph {
private:
    int vertices;

    vector<vector<double>> distance;
    vector<vector<int>> nextVertex;

    bool computed = false;

    const double INF = numeric_limits<double>::infinity();

public:
    explicit WeightedGraph(int vertexCount) : vertices(vertexCount) {
        if (vertexCount <= 0) {
            throw invalid_argument(
                "Vertex count must be positive."
            );
        }

        distance.assign(
            vertices,
            vector<double>(vertices, INF)
        );

        nextVertex.assign(
            vertices,
            vector<int>(vertices, -1)
        );

        for (int i = 0; i < vertices; i++) {
            distance[i][i] = 0;
            nextVertex[i][i] = i;
        }
    }

    int size() const {
        return vertices;
    }

    void validateVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertices) {
            throw out_of_range("Invalid vertex index.");
        }
    }

    void addEdge(int source, int destination, double weight) {
        validateVertex(source);
        validateVertex(destination);

        if (!isfinite(weight)) {
            throw invalid_argument("Edge weight must be finite.");
        }

        // Parallel edges retain their minimum weight.
        if (weight < distance[source][destination]) {
            distance[source][destination] = weight;
            nextVertex[source][destination] = destination;
            computed = false;
        }
    }

    void floydWarshall() {
        /*
         * Dynamic programming state:
         *
         * distance[i][j] represents the shortest known distance
         * from i to j using currently permitted intermediate vertices.
         *
         * At iteration k:
         *
         * distance[i][j] =
         * min(distance[i][j],
         *     distance[i][k] + distance[k][j])
         */

        for (int k = 0; k < vertices; k++) {
            for (int i = 0; i < vertices; i++) {

                if (!isfinite(distance[i][k])) {
                    continue;
                }

                for (int j = 0; j < vertices; j++) {
                    if (!isfinite(distance[k][j])) {
                        continue;
                    }

                    const double candidate =
                        distance[i][k] + distance[k][j];

                    if (candidate < distance[i][j]) {
                        distance[i][j] = candidate;
                        nextVertex[i][j] = nextVertex[i][k];
                    }
                }
            }
        }

        computed = true;

        detectNegativeCycle();
    }

    void detectNegativeCycle() const {
        if (!computed) {
            throw logic_error("Shortest paths are not computed.");
        }

        for (int i = 0; i < vertices; i++) {
            if (distance[i][i] < 0) {
                throw NegativeCycleException(
                    "Negative-weight cycle detected."
                );
            }
        }
    }

    double getDistance(int source, int destination) const {
        validateVertex(source);
        validateVertex(destination);

        if (!computed) {
            throw logic_error("Run Floyd-Warshall first.");
        }

        return distance[source][destination];
    }

    optional<vector<int>> getPath(
        int source,
        int destination
    ) const {
        validateVertex(source);
        validateVertex(destination);

        if (!computed) {
            throw logic_error("Run Floyd-Warshall first.");
        }

        if (!isfinite(distance[source][destination])) {
            return nullopt;
        }

        vector<int> path;
        path.push_back(source);

        int current = source;

        for (int step = 0; step < vertices; step++) {
            if (current == destination) {
                return path;
            }

            current = nextVertex[current][destination];

            if (current == -1) {
                return nullopt;
            }

            path.push_back(current);
        }

        throw logic_error(
            "Path reconstruction exceeded graph size."
        );
    }

    void printMatrix() const {
        if (!computed) {
            throw logic_error("Run Floyd-Warshall first.");
        }

        cout << "\nAll-Pairs Shortest Distance Matrix\n";

        cout << setw(8) << " ";

        for (int j = 0; j < vertices; j++) {
            cout << setw(10) << j;
        }

        cout << '\n';

        for (int i = 0; i < vertices; i++) {
            cout << setw(8) << i;

            for (int j = 0; j < vertices; j++) {
                if (isinf(distance[i][j])) {
                    cout << setw(10) << "INF";
                } else {
                    cout << setw(10) << fixed
                         << setprecision(2)
                         << distance[i][j];
                }
            }

            cout << '\n';
        }
    }
};

void demonstrateGraph() {
    cout << "FLOYD-WARSHALL ALGORITHM\n";
    cout << "========================\n";

    WeightedGraph graph(5);

    vector<tuple<int, int, double>> edges = {
        {0, 1, 3},
        {0, 2, 8},
        {0, 4, -4},
        {1, 3, 1},
        {1, 4, 7},
        {2, 1, 4},
        {3, 0, 2},
        {3, 2, -5},
        {4, 3, 6}
    };

    for (const auto& [source, destination, weight] : edges) {
        graph.addEdge(source, destination, weight);
    }

    graph.floydWarshall();

    graph.printMatrix();

    cout << "\nShortest Path Queries\n";

    vector<pair<int, int>> queries = {
        {0, 2},
        {0, 3},
        {1, 2},
        {2, 4},
        {4, 2}
    };

    for (const auto& [source, destination] : queries) {
        double distance = graph.getDistance(
            source,
            destination
        );

        auto path = graph.getPath(source, destination);

        cout << source << " -> " << destination << ": ";

        if (!path.has_value()) {
            cout << "Unreachable\n";
            continue;
        }

        cout << "Distance = " << distance << ", Path = ";

        const auto& vertices = path.value();

        for (size_t i = 0; i < vertices.size(); i++) {
            if (i > 0) {
                cout << " -> ";
            }

            cout << vertices[i];
        }

        cout << '\n';
    }
}

void demonstrateEdgeCases() {
    cout << "\nEDGE CASE TESTS\n";

    // Disconnected graph.
    WeightedGraph disconnected(3);

    disconnected.addEdge(0, 1, 5);
    disconnected.floydWarshall();

    if (!isinf(disconnected.getDistance(0, 2))) {
        throw runtime_error("Disconnected graph test failed.");
    }

    // Negative edge without a negative cycle.
    WeightedGraph negative(3);

    negative.addEdge(0, 1, 4);
    negative.addEdge(1, 2, -6);
    negative.addEdge(0, 2, 3);

    negative.floydWarshall();

    if (negative.getDistance(0, 2) != -2) {
        throw runtime_error("Negative edge test failed.");
    }

    // Negative cycle.
    WeightedGraph cyclic(3);

    cyclic.addEdge(0, 1, 1);
    cyclic.addEdge(1, 2, -3);
    cyclic.addEdge(2, 0, 1);

    try {
        cyclic.floydWarshall();

        throw runtime_error(
            "Negative cycle was not detected."
        );
    } catch (const NegativeCycleException& error) {
        cout << error.what() << '\n';
    }

    // Single vertex.
    WeightedGraph single(1);
    single.floydWarshall();

    if (single.getDistance(0, 0) != 0) {
        throw runtime_error("Single vertex test failed.");
    }

    cout << "All edge-case tests passed.\n";
}

int main() {
    try {
        demonstrateGraph();
        demonstrateEdgeCases();
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
