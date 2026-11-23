#include <algorithm>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

/*
 * Bipartite Graph Governance Engine
 *
 * Models graph partition validation for an assignment network.
 * Vertices represent entities and edges represent incompatibility.
 * Connected entities must receive different colors.
 *
 * Implements:
 * - BFS and DFS two-coloring.
 * - Odd-cycle reconstruction.
 * - Disconnected components.
 * - Merge-style validation of proposed graph updates.
 * - Self-loop and parallel-edge handling.
 */

enum class Color {
    Uncolored = -1,
    Red = 0,
    Blue = 1
};

enum class Algorithm {
    BFS,
    DFS
};

struct AnalysisResult {
    bool bipartite = true;
    vector<int> colors;
    vector<int> oddCycle;
    int components = 0;
    Algorithm algorithm = Algorithm::BFS;
};

class BipartiteGraph {
private:
    int vertexCount;
    vector<vector<int>> adjacency;

    void validateVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertexCount) {
            throw out_of_range("Vertex outside graph boundaries.");
        }
    }

    static vector<int> reconstructCycle(
        int u,
        int v,
        const vector<int>& parent,
        const vector<int>& depth
    ) {
        int a = u;
        int b = v;

        vector<int> pathA{a};
        vector<int> pathB{b};

        while (depth[a] > depth[b]) {
            a = parent[a];
            pathA.push_back(a);
        }

        while (depth[b] > depth[a]) {
            b = parent[b];
            pathB.push_back(b);
        }

        while (a != b) {
            a = parent[a];
            b = parent[b];

            pathA.push_back(a);
            pathB.push_back(b);
        }

        for (int i = static_cast<int>(pathB.size()) - 2; i >= 0; --i) {
            pathA.push_back(pathB[i]);
        }

        pathA.push_back(u);
        return pathA;
    }

public:
    explicit BipartiteGraph(int vertices)
        : vertexCount(vertices), adjacency(vertices) {
        if (vertices < 0) {
            throw invalid_argument("Vertex count cannot be negative.");
        }
    }

    int size() const {
        return vertexCount;
    }

    void addEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);

        adjacency[u].push_back(v);

        if (u != v) {
            adjacency[v].push_back(u);
        }
    }

    void removeEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);

        auto eraseOne = [](vector<int>& neighbors, int target) {
            auto it = find(neighbors.begin(), neighbors.end(), target);
            if (it == neighbors.end()) {
                return false;
            }
            neighbors.erase(it);
            return true;
        };

        if (!eraseOne(adjacency[u], v)) {
            return;
        }

        if (u != v) {
            eraseOne(adjacency[v], u);
        }
    }

    AnalysisResult analyzeBFS() const {
        AnalysisResult result;
        result.algorithm = Algorithm::BFS;
        result.colors.assign(vertexCount, -1);

        vector<int> parent(vertexCount, -1);
        vector<int> depth(vertexCount, 0);

        for (int start = 0; start < vertexCount; ++start) {
            if (result.colors[start] != -1) {
                continue;
            }

            result.components++;
            result.colors[start] = 0;

            queue<int> q;
            q.push(start);

            while (!q.empty()) {
                int u = q.front();
                q.pop();

                for (int v : adjacency[u]) {
                    if (result.colors[v] == -1) {
                        result.colors[v] = 1 - result.colors[u];
                        parent[v] = u;
                        depth[v] = depth[u] + 1;
                        q.push(v);
                    } else if (result.colors[v] == result.colors[u]) {
                        result.bipartite = false;
                        result.oddCycle = reconstructCycle(
                            u, v, parent, depth
                        );
                        return result;
                    }
                }
            }
        }

        return result;
    }

    AnalysisResult analyzeDFS() const {
        AnalysisResult result;
        result.algorithm = Algorithm::DFS;
        result.colors.assign(vertexCount, -1);

        vector<int> parent(vertexCount, -1);
        vector<int> depth(vertexCount, 0);

        for (int start = 0; start < vertexCount; ++start) {
            if (result.colors[start] != -1) {
                continue;
            }

            result.components++;
            result.colors[start] = 0;

            vector<int> stack{start};

            while (!stack.empty()) {
                int u = stack.back();
                stack.pop_back();

                for (int v : adjacency[u]) {
                    if (result.colors[v] == -1) {
                        result.colors[v] = 1 - result.colors[u];
                        parent[v] = u;
                        depth[v] = depth[u] + 1;
                        stack.push_back(v);
                    } else if (result.colors[v] == result.colors[u]) {
                        result.bipartite = false;
                        result.oddCycle = reconstructCycle(
                            u, v, parent, depth
                        );
                        return result;
                    }
                }
            }
        }

        return result;
    }

    void print(const AnalysisResult& result) const {
        cout << "\nAlgorithm: "
             << (result.algorithm == Algorithm::BFS ? "BFS" : "DFS")
             << "\n";

        cout << "Bipartite: "
             << (result.bipartite ? "YES" : "NO") << "\n";

        if (result.bipartite) {
            cout << "Red group: ";
            for (int i = 0; i < vertexCount; ++i) {
                if (result.colors[i] == 0) {
                    cout << i << " ";
                }
            }

            cout << "\nBlue group: ";
            for (int i = 0; i < vertexCount; ++i) {
                if (result.colors[i] == 1) {
                    cout << i << " ";
                }
            }
            cout << "\n";
        } else {
            cout << "Odd cycle: ";
            for (int vertex : result.oddCycle) {
                cout << vertex << " ";
            }
            cout << "\n";
        }

        cout << "Connected components: "
             << result.components << "\n";
    }
};

/*
 * Simulates an assignment network.
 *
 * Vertices are departments.
 * Edges represent pairs that cannot share a scheduling slot.
 * Red and blue represent two available time slots.
 */
class AssignmentGovernance {
private:
    BipartiteGraph graph;

public:
    explicit AssignmentGovernance(int departments)
        : graph(departments) {}

    void addConflict(int departmentA, int departmentB) {
        graph.addEdge(departmentA, departmentB);
    }

    bool canAssignTwoSlots() const {
        return graph.analyzeBFS().bipartite;
    }

    void evaluate() const {
        const AnalysisResult bfs = graph.analyzeBFS();
        const AnalysisResult dfs = graph.analyzeDFS();

        graph.print(bfs);

        if (bfs.bipartite != dfs.bipartite) {
            throw logic_error("BFS and DFS results disagree.");
        }
    }

    void updateConflict(int a, int b) {
        graph.addEdge(a, b);
    }

    void removeConflict(int a, int b) {
        graph.removeEdge(a, b);
    }
};

void runTests() {
    BipartiteGraph even(4);
    even.addEdge(0, 1);
    even.addEdge(1, 2);
    even.addEdge(2, 3);
    even.addEdge(3, 0);

    if (!even.analyzeBFS().bipartite) {
        throw runtime_error("Even cycle test failed.");
    }

    BipartiteGraph odd(3);
    odd.addEdge(0, 1);
    odd.addEdge(1, 2);
    odd.addEdge(2, 0);

    if (odd.analyzeDFS().bipartite) {
        throw runtime_error("Odd cycle test failed.");
    }

    BipartiteGraph selfLoop(2);
    selfLoop.addEdge(0, 0);

    if (selfLoop.analyzeBFS().bipartite) {
        throw runtime_error("Self-loop test failed.");
    }

    BipartiteGraph disconnected(7);
    disconnected.addEdge(0, 1);
    disconnected.addEdge(1, 2);
    disconnected.addEdge(3, 4);

    const auto result = disconnected.analyzeBFS();

    if (!result.bipartite || result.components != 4) {
        throw runtime_error("Disconnected graph test failed.");
    }

    BipartiteGraph empty(0);

    if (!empty.analyzeBFS().bipartite) {
        throw runtime_error("Empty graph test failed.");
    }

    cout << "\nAll C++ tests passed.\n";
}

int main() {
    try {
        cout << "BIPARTITE GRAPH GOVERNANCE ENGINE\n";

        AssignmentGovernance schedule(6);

        schedule.addConflict(0, 1);
        schedule.addConflict(1, 2);
        schedule.addConflict(2, 3);
        schedule.addConflict(3, 4);
        schedule.addConflict(4, 5);
        schedule.addConflict(5, 0);

        cout << "\nInitial scheduling network:";
        schedule.evaluate();

        cout << "\nAdding a conflicting assignment:";
        schedule.updateConflict(0, 2);
        schedule.evaluate();

        if (schedule.canAssignTwoSlots()) {
            throw logic_error("Odd cycle was not detected.");
        }

        cout << "\nRemoving conflicting assignment:";
        schedule.removeConflict(0, 2);
        schedule.evaluate();

        if (!schedule.canAssignTwoSlots()) {
            throw logic_error("Valid schedule was rejected.");
        }

        runTests();
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
