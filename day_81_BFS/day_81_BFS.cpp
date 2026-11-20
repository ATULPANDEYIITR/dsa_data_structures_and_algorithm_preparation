#include <algorithm>
#include <cassert>
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

/*
 * Breadth-First Search and Graph Governance Engine
 *
 * Features:
 * - Adjacency-list graph representation
 * - Directed and undirected graphs
 * - BFS traversal
 * - Shortest paths
 * - Level processing
 * - Multi-source BFS
 * - Grid shortest paths
 * - Connected components
 * - Input validation
 */

enum class GraphType {
    DIRECTED,
    UNDIRECTED
};

struct BFSResult {
    unordered_map<int, int> distance;
    unordered_map<int, int> parent;
    map<int, vector<int>> levels;

    vector<int> shortestPath(int target) const {
        if (distance.find(target) == distance.end()) {
            return {};
        }

        vector<int> path;
        int current = target;

        while (true) {
            path.push_back(current);

            auto it = parent.find(current);

            if (it == parent.end() || it->second == -1) {
                break;
            }

            current = it->second;
        }

        reverse(path.begin(), path.end());
        return path;
    }
};


class Graph {
private:
    GraphType type;
    unordered_map<int, vector<int>> adjacency;

public:
    explicit Graph(GraphType graphType = GraphType::UNDIRECTED)
        : type(graphType) {}

    void addVertex(int vertex) {
        adjacency.try_emplace(vertex);
    }

    void addEdge(int source, int destination) {
        addVertex(source);
        addVertex(destination);

        adjacency[source].push_back(destination);

        if (type == GraphType::UNDIRECTED) {
            adjacency[destination].push_back(source);
        }
    }

    bool contains(int vertex) const {
        return adjacency.find(vertex) != adjacency.end();
    }

    void validateSource(int source) const {
        if (!contains(source)) {
            throw invalid_argument("Unknown source vertex");
        }
    }

    BFSResult multiSourceBFS(const vector<int>& sources) const {
        if (sources.empty()) {
            throw invalid_argument("At least one source is required");
        }

        BFSResult result;
        queue<int> pending;

        unordered_set<int> initialized;

        for (int source : sources) {
            validateSource(source);

            if (initialized.insert(source).second) {
                pending.push(source);
                result.distance[source] = 0;
                result.parent[source] = -1;
                result.levels[0].push_back(source);
            }
        }

        while (!pending.empty()) {
            int current = pending.front();
            pending.pop();

            for (int neighbor : adjacency.at(current)) {
                if (result.distance.find(neighbor) !=
                    result.distance.end()) {
                    continue;
                }

                int nextDistance = result.distance.at(current) + 1;

                result.distance[neighbor] = nextDistance;
                result.parent[neighbor] = current;
                result.levels[nextDistance].push_back(neighbor);

                pending.push(neighbor);
            }
        }

        return result;
    }

    BFSResult bfs(int source) const {
        return multiSourceBFS({source});
    }

    vector<vector<int>> connectedComponents() const {
        if (type == GraphType::DIRECTED) {
            throw logic_error(
                "Connected components require an undirected graph"
            );
        }

        unordered_set<int> visited;
        vector<vector<int>> components;

        for (const auto& entry : adjacency) {
            int start = entry.first;

            if (visited.count(start)) {
                continue;
            }

            vector<int> component;
            queue<int> pending;

            pending.push(start);
            visited.insert(start);

            while (!pending.empty()) {
                int current = pending.front();
                pending.pop();

                component.push_back(current);

                for (int neighbor : adjacency.at(current)) {
                    if (visited.insert(neighbor).second) {
                        pending.push(neighbor);
                    }
                }
            }

            components.push_back(move(component));
        }

        return components;
    }

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t edgeEntryCount() const {
        size_t count = 0;

        for (const auto& entry : adjacency) {
            count += entry.second.size();
        }

        return count;
    }
};


struct GridPoint {
    int row;
    int col;

    bool operator==(const GridPoint& other) const {
        return row == other.row && col == other.col;
    }
};


vector<GridPoint> shortestGridPath(
    const vector<vector<int>>& grid,
    GridPoint start,
    GridPoint target
) {
    if (grid.empty() || grid[0].empty()) {
        throw invalid_argument("Grid cannot be empty");
    }

    const int rows = static_cast<int>(grid.size());
    const int cols = static_cast<int>(grid[0].size());

    for (const auto& row : grid) {
        if (static_cast<int>(row.size()) != cols) {
            throw invalid_argument("Grid must be rectangular");
        }

        for (int cell : row) {
            if (cell != 0 && cell != 1) {
                throw invalid_argument("Grid cells must be 0 or 1");
            }
        }
    }

    auto valid = [&](GridPoint point) {
        return point.row >= 0 &&
               point.row < rows &&
               point.col >= 0 &&
               point.col < cols &&
               grid[point.row][point.col] == 0;
    };

    if (!valid(start) || !valid(target)) {
        return {};
    }

    vector<vector<bool>> visited(
        rows, vector<bool>(cols, false)
    );

    vector<vector<GridPoint>> parent(
        rows,
        vector<GridPoint>(cols, {-1, -1})
    );

    queue<GridPoint> pending;

    pending.push(start);
    visited[start.row][start.col] = true;

    const int dr[] = {-1, 1, 0, 0};
    const int dc[] = {0, 0, -1, 1};

    while (!pending.empty()) {
        GridPoint current = pending.front();
        pending.pop();

        if (current == target) {
            break;
        }

        for (int i = 0; i < 4; i++) {
            GridPoint next{
                current.row + dr[i],
                current.col + dc[i]
            };

            if (valid(next) && !visited[next.row][next.col]) {
                visited[next.row][next.col] = true;
                parent[next.row][next.col] = current;
                pending.push(next);
            }
        }
    }

    if (!visited[target.row][target.col]) {
        return {};
    }

    vector<GridPoint> path;
    GridPoint current = target;

    while (!(current == GridPoint{-1, -1})) {
        path.push_back(current);

        if (current == start) {
            break;
        }

        current = parent[current.row][current.col];
    }

    reverse(path.begin(), path.end());
    return path;
}


void printResult(const BFSResult& result) {
    cout << "Distances:\n";

    vector<pair<int, int>> ordered(
        result.distance.begin(),
        result.distance.end()
    );

    sort(ordered.begin(), ordered.end());

    for (const auto& [vertex, distance] : ordered) {
        cout << vertex << " -> " << distance << '\n';
    }

    cout << "\nBFS Levels:\n";

    for (const auto& [level, vertices] : result.levels) {
        cout << "Level " << level << ": ";

        for (int vertex : vertices) {
            cout << vertex << " ";
        }

        cout << '\n';
    }
}


int main() {
    try {
        Graph graph(GraphType::UNDIRECTED);

        const vector<pair<int, int>> edges = {
            {0, 1}, {0, 2},
            {1, 3}, {1, 4},
            {2, 5}, {2, 6},
            {4, 7}, {5, 7}
        };

        for (const auto& [u, v] : edges) {
            graph.addEdge(u, v);
        }

        cout << "=== BFS Traversal ===\n";

        BFSResult result = graph.bfs(0);
        printResult(result);

        cout << "\nShortest path 0 -> 7: ";

        for (int vertex : result.shortestPath(7)) {
            cout << vertex << " ";
        }

        cout << "\n\n=== Multi-Source BFS ===\n";

        BFSResult multi = graph.multiSourceBFS({0, 7});
        printResult(multi);

        cout << "\n=== Connected Components ===\n";

        graph.addEdge(10, 11);

        auto components = graph.connectedComponents();

        for (const auto& component : components) {
            for (int vertex : component) {
                cout << vertex << " ";
            }

            cout << '\n';
        }

        cout << "\n=== Grid Shortest Path ===\n";

        vector<vector<int>> grid = {
            {0, 0, 0, 1},
            {1, 0, 0, 0},
            {0, 0, 1, 0},
            {0, 0, 0, 0}
        };

        auto path = shortestGridPath(
            grid, {0, 0}, {3, 3}
        );

        for (const auto& point : path) {
            cout << "(" << point.row
                 << "," << point.col << ") ";
        }

        cout << "\n\n=== Automated Tests ===\n";

        assert(result.distance.at(0) == 0);
        assert(result.distance.at(7) == 3);

        assert(
            result.shortestPath(7) ==
            vector<int>({0, 1, 4, 7})
        );

        assert(result.shortestPath(999).empty());

        assert(multi.distance.at(0) == 0);
        assert(multi.distance.at(7) == 0);

        assert(components.size() == 2);

        assert(
            shortestGridPath(
                {{0, 1}, {1, 0}},
                {0, 0},
                {1, 1}
            ).empty()
        );

        bool invalidRejected = false;

        try {
            graph.bfs(999);
        } catch (const invalid_argument&) {
            invalidRejected = true;
        }

        assert(invalidRejected);

        cout << "All tests passed.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
