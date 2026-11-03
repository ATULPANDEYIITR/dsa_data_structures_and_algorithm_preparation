#include <algorithm>
#include <iostream>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

struct Site {
    string id;
    string name;
};

struct Link {
    string first;
    string second;
};

class DisjointSet {
private:
    vector<int> parent;
    vector<int> rankValue;

public:
    explicit DisjointSet(int size)
        : parent(size), rankValue(size, 0) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int node) {
        if (parent[node] != node) {
            parent[node] = find(parent[node]);
        }
        return parent[node];
    }

    bool unite(int first, int second) {
        first = find(first);
        second = find(second);

        if (first == second) {
            return false;
        }

        if (rankValue[first] < rankValue[second]) {
            swap(first, second);
        }

        parent[second] = first;

        if (rankValue[first] == rankValue[second]) {
            ++rankValue[first];
        }

        return true;
    }
};

struct BfsResult {
    int farthest;
    vector<int> distance;
    vector<int> parent;
};

struct TreeAnalysis {
    int root;
    int heightEdges;
    int diameterEdges;
    int endpointA;
    int endpointB;
    vector<int> longestPath;
    vector<int> diameterThroughNode;
};

class CampusNetworkTree {
private:
    vector<Site> sites;
    unordered_map<string, int> indexById;
    vector<vector<int>> adjacency;

    void validateRoot(int root) const {
        if (root < 0 || root >= static_cast<int>(sites.size())) {
            throw invalid_argument("Invalid root index.");
        }
    }

    BfsResult bfs(int start) const {
        const int n = static_cast<int>(sites.size());
        vector<int> distance(n, -1);
        vector<int> parent(n, -1);
        queue<int> pending;

        distance[start] = 0;
        pending.push(start);

        int farthest = start;

        while (!pending.empty()) {
            int current = pending.front();
            pending.pop();

            if (distance[current] > distance[farthest]) {
                farthest = current;
            }

            for (int neighbor : adjacency[current]) {
                if (distance[neighbor] != -1) {
                    continue;
                }

                distance[neighbor] = distance[current] + 1;
                parent[neighbor] = current;
                pending.push(neighbor);
            }
        }

        return {farthest, move(distance), move(parent)};
    }

    void validateConstruction(const vector<Link>& links) const {
        const int n = static_cast<int>(sites.size());

        if (links.size() != static_cast<size_t>(n - 1)) {
            throw invalid_argument(
                "A tree with n sites must contain exactly n - 1 links."
            );
        }

        DisjointSet sets(n);

        for (const Link& link : links) {
            auto firstIt = indexById.find(link.first);
            auto secondIt = indexById.find(link.second);

            if (firstIt == indexById.end() ||
                secondIt == indexById.end()) {
                throw invalid_argument(
                    "A link references an unknown site."
                );
            }

            int first = firstIt->second;
            int second = secondIt->second;

            if (first == second) {
                throw invalid_argument("Self-links are not allowed.");
            }

            if (!sets.unite(first, second)) {
                throw invalid_argument(
                    "The network contains a cycle or duplicate link."
                );
            }

            adjacency[first].push_back(second);
            adjacency[second].push_back(first);
        }

        const int representative = sets.find(0);

        for (int i = 1; i < n; ++i) {
            if (sets.find(i) != representative) {
                throw invalid_argument("The network is disconnected.");
            }
        }
    }

public:
    CampusNetworkTree(
        vector<Site> inputSites,
        const vector<Link>& links
    ) : sites(move(inputSites)) {
        if (sites.empty()) {
            throw invalid_argument(
                "A tree must contain at least one site."
            );
        }

        adjacency.resize(sites.size());

        for (int i = 0; i < static_cast<int>(sites.size()); ++i) {
            const string& id = sites[i].id;

            if (id.empty()) {
                throw invalid_argument("Site IDs cannot be empty.");
            }

            if (!indexById.emplace(id, i).second) {
                throw invalid_argument("Duplicate site ID: " + id);
            }
        }

        validateConstruction(links);
    }

    int getIndex(const string& siteId) const {
        auto it = indexById.find(siteId);

        if (it == indexById.end()) {
            throw invalid_argument("Unknown site: " + siteId);
        }

        return it->second;
    }

    const Site& getSite(int index) const {
        return sites.at(index);
    }

    TreeAnalysis analyze(const string& rootId) const {
        const int n = static_cast<int>(sites.size());
        const int root = getIndex(rootId);

        // Iterative traversal builds a parent-before-child ordering.
        vector<int> parent(n, -2);
        vector<int> depth(n, 0);
        vector<int> order;
        vector<int> stack;

        parent[root] = -1;
        stack.push_back(root);

        while (!stack.empty()) {
            int current = stack.back();
            stack.pop_back();
            order.push_back(current);

            for (int neighbor : adjacency[current]) {
                if (neighbor == parent[current]) {
                    continue;
                }

                if (parent[neighbor] != -2) {
                    throw logic_error("Cycle found during analysis.");
                }

                parent[neighbor] = current;
                depth[neighbor] = depth[current] + 1;
                stack.push_back(neighbor);
            }
        }

        if (static_cast<int>(order.size()) != n) {
            throw logic_error("The selected root cannot reach every site.");
        }

        vector<int> down(n, 0);
        vector<int> up(n, 0);
        vector<int> childFirst(n, 0);
        vector<int> childSecond(n, 0);
        vector<int> bestChild(n, -1);
        vector<int> through(n, 0);

        // Bottom-up dynamic programming.
        for (int position = n - 1; position >= 0; --position) {
            int node = order[position];

            int first = 0;
            int second = 0;
            int firstChild = -1;

            for (int child : adjacency[node]) {
                if (parent[child] != node) {
                    continue;
                }

                int branchHeight = 1 + down[child];

                if (branchHeight > first) {
                    second = first;
                    first = branchHeight;
                    firstChild = child;
                } else if (branchHeight > second) {
                    second = branchHeight;
                }
            }

            down[node] = first;
            childFirst[node] = first;
            childSecond[node] = second;
            bestChild[node] = firstChild;
        }

        int heightEdges = 0;

        // Rerooting pass adds the parent-side branch for each node.
        for (int node : order) {
            heightEdges = max(heightEdges, depth[node]);

            int first = 0;
            int second = 0;

            auto considerBranch = [&](int value) {
                if (value > first) {
                    second = first;
                    first = value;
                } else if (value > second) {
                    second = value;
                }
            };

            if (parent[node] != -1) {
                considerBranch(up[node]);
            }

            for (int child : adjacency[node]) {
                if (parent[child] == node) {
                    considerBranch(1 + down[child]);
                }
            }

            // Two distinct directions form the longest path through node.
            through[node] = first + second;

            for (int child : adjacency[node]) {
                if (parent[child] != node) {
                    continue;
                }

                int siblingHeight =
                    (bestChild[node] == child)
                        ? childSecond[node]
                        : childFirst[node];

                up[child] = 1 + max({
                    0,
                    up[node],
                    siblingHeight
                });
            }
        }

        int diameterDP = *max_element(through.begin(), through.end());

        // Independent diameter calculation using two BFS traversals.
        BfsResult firstSweep = bfs(root);
        int endpointA = firstSweep.farthest;

        BfsResult secondSweep = bfs(endpointA);
        int endpointB = secondSweep.farthest;

        int diameterSweep = secondSweep.distance[endpointB];

        if (diameterDP != diameterSweep) {
            throw logic_error(
                "Dynamic programming and two-sweep results disagree."
            );
        }

        vector<int> reversePath;
        int current = endpointB;

        while (current != -1) {
            reversePath.push_back(current);
            current = secondSweep.parent[current];
        }

        reverse(reversePath.begin(), reversePath.end());

        return {
            root,
            heightEdges,
            diameterDP,
            endpointA,
            endpointB,
            move(reversePath),
            move(through)
        };
    }

    int siteCount() const {
        return static_cast<int>(sites.size());
    }
};

void runTests() {
    CampusNetworkTree chain(
        {
            {"A", "A"},
            {"B", "B"},
            {"C", "C"},
            {"D", "D"},
            {"E", "E"}
        },
        {
            {"A", "B"},
            {"B", "C"},
            {"C", "D"},
            {"D", "E"}
        }
    );

    TreeAnalysis chainResult = chain.analyze("A");
    if (chainResult.diameterEdges != 4 ||
        chainResult.heightEdges != 4) {
        throw runtime_error("Chain test failed.");
    }

    CampusNetworkTree star(
        {
            {"C", "Central office"},
            {"N", "North office"},
            {"S", "South office"},
            {"E", "East office"},
            {"W", "West office"}
        },
        {
            {"C", "N"},
            {"C", "S"},
            {"C", "E"},
            {"C", "W"}
        }
    );

    TreeAnalysis starResult = star.analyze("C");
    if (starResult.diameterEdges != 2 ||
        starResult.diameterThroughNode[1] != 2) {
        throw runtime_error("Star test failed.");
    }

    CampusNetworkTree singleton(
        {{"ONLY", "Single site"}},
        {}
    );

    TreeAnalysis singletonResult = singleton.analyze("ONLY");
    if (singletonResult.diameterEdges != 0 ||
        singletonResult.heightEdges != 0) {
        throw runtime_error("Single-node test failed.");
    }

    bool invalidRejected = false;

    try {
        CampusNetworkTree invalid(
            {
                {"A", "A"},
                {"B", "B"},
                {"C", "C"}
            },
            {
                {"A", "B"},
                {"B", "C"},
                {"C", "A"}
            }
        );
    } catch (const invalid_argument&) {
        invalidRejected = true;
    }

    if (!invalidRejected) {
        throw runtime_error("Invalid-cycle test failed.");
    }
}

int main() {
    try {
        runTests();

        // Example: campus fiber network with an organizational hierarchy.
        vector<Site> sites = {
            {"HQ", "Headquarters"},
            {"N", "North"},
            {"S", "South"},
            {"NE", "North-East"},
            {"NW", "North-West"},
            {"SC", "South-Central"},
            {"SE", "South-East"},
            {"SW", "South-West"}
        };

        vector<Link> links = {
            {"HQ", "N"},
            {"HQ", "S"},
            {"N", "NE"},
            {"N", "NW"},
            {"S", "SC"},
            {"SC", "SE"},
            {"SC", "SW"}
        };

        CampusNetworkTree network(sites, links);
        TreeAnalysis result = network.analyze("HQ");

        cout << "TREE DIAMETER ANALYSIS\n";
        cout << "----------------------\n";
        cout << "Root: "
             << network.getSite(result.root).name << '\n';
        cout << "Height: " << result.heightEdges << " edges\n";
        cout << "Diameter: " << result.diameterEdges << " edges\n";
        cout << "Nodes on diameter: "
             << result.diameterEdges + 1 << '\n';

        cout << "Endpoint A: "
             << network.getSite(result.endpointA).name << '\n';
        cout << "Endpoint B: "
             << network.getSite(result.endpointB).name << '\n';

        cout << "Longest path:\n";
        for (size_t i = 0; i < result.longestPath.size(); ++i) {
            if (i > 0) {
                cout << " -> ";
            }
            cout << network.getSite(result.longestPath[i]).name;
        }
        cout << '\n';

        cout << "\nLongest path through each site:\n";
        for (int i = 0; i < network.siteCount(); ++i) {
            cout << network.getSite(i).name
                 << ": " << result.diameterThroughNode[i]
                 << " edges\n";
        }

        cout << "\nAll tests passed.\n";
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
