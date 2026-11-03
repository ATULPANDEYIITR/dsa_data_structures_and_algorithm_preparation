import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class TreeDiameterEnterprise {

    enum MeasurementUnit {
        EDGES,
        NODES
    }

    record Site(String id, String displayName) {
        Site {
            if (id == null || id.isBlank()) {
                throw new TreeValidationException(
                    "Site ID cannot be blank."
                );
            }

            if (displayName == null || displayName.isBlank()) {
                throw new TreeValidationException(
                    "Site display name cannot be blank."
                );
            }
        }
    }

    record Link(String firstSiteId, String secondSiteId) {
        Link {
            if (firstSiteId == null || secondSiteId == null) {
                throw new TreeValidationException(
                    "Link endpoints cannot be null."
                );
            }
        }
    }

    record DiameterPolicy(
        int maximumSites,
        MeasurementUnit outputUnit
    ) {
        DiameterPolicy {
            if (maximumSites < 1) {
                throw new IllegalArgumentException(
                    "Maximum site count must be positive."
                );
            }

            Objects.requireNonNull(outputUnit, "Output unit is required.");
        }
    }

    record DpMetrics(
        int heightEdges,
        int diameterEdges,
        Map<String, Integer> diameterThroughNode
    ) {}

    record SweepMetrics(
        int diameterEdges,
        String endpointA,
        String endpointB,
        List<String> longestPath
    ) {}

    record AnalysisResult(
        String rootId,
        int heightEdges,
        int diameterEdges,
        int diameterNodes,
        int reportedDiameter,
        MeasurementUnit reportedUnit,
        String endpointA,
        String endpointB,
        List<String> longestPath,
        Map<String, Integer> diameterThroughNode
    ) {
        AnalysisResult {
            longestPath = List.copyOf(longestPath);
            diameterThroughNode = Map.copyOf(diameterThroughNode);
        }
    }

    static final class TreeValidationException
        extends IllegalArgumentException {

        TreeValidationException(String message) {
            super(message);
        }
    }

    static final class DisjointSet {
        private final int[] parent;
        private final int[] rank;

        DisjointSet(int size) {
            parent = new int[size];
            rank = new int[size];
            for (int i = 0; i < size; i++) {
                parent[i] = i;
            }
        }

        int find(int node) {
            if (parent[node] != node) {
                parent[node] = find(parent[node]);
            }
            return parent[node];
        }

        boolean union(int first, int second) {
            first = find(first);
            second = find(second);

            if (first == second) {
                return false;
            }

            if (rank[first] < rank[second]) {
                int temp = first;
                first = second;
                second = temp;
            }

            parent[second] = first;

            if (rank[first] == rank[second]) {
                rank[first]++;
            }

            return true;
        }
    }

    static final class TreeGraph {
        private final List<Site> sites;
        private final List<List<Integer>> adjacency;
        private final Map<String, Integer> indexById;

        TreeGraph(List<Site> inputSites, List<Link> links) {
            if (inputSites == null || inputSites.isEmpty()) {
                throw new TreeValidationException(
                    "A tree must contain at least one site."
                );
            }

            Objects.requireNonNull(links, "Links cannot be null.");

            this.sites = List.copyOf(inputSites);
            this.indexById = new HashMap<>();

            List<List<Integer>> mutableAdjacency = new ArrayList<>();

            for (int i = 0; i < sites.size(); i++) {
                Site site = Objects.requireNonNull(
                    sites.get(i),
                    "Site cannot be null."
                );

                if (indexById.putIfAbsent(site.id(), i) != null) {
                    throw new TreeValidationException(
                        "Duplicate site ID: " + site.id()
                    );
                }

                mutableAdjacency.add(new ArrayList<>());
            }

            if (links.size() != sites.size() - 1) {
                throw new TreeValidationException(
                    "A tree with n sites must have n - 1 links."
                );
            }

            DisjointSet sets = new DisjointSet(sites.size());

            for (Link link : links) {
                Objects.requireNonNull(link, "Link cannot be null.");

                Integer first = indexById.get(link.firstSiteId());
                Integer second = indexById.get(link.secondSiteId());

                if (first == null || second == null) {
                    throw new TreeValidationException(
                        "A link references an unknown site."
                    );
                }

                if (first.equals(second)) {
                    throw new TreeValidationException(
                        "Self-links are not allowed."
                    );
                }

                if (!sets.union(first, second)) {
                    throw new TreeValidationException(
                        "The graph contains a cycle or duplicate link."
                    );
                }

                mutableAdjacency.get(first).add(second);
                mutableAdjacency.get(second).add(first);
            }

            int representative = sets.find(0);

            for (int i = 1; i < sites.size(); i++) {
                if (sets.find(i) != representative) {
                    throw new TreeValidationException(
                        "The graph is disconnected."
                    );
                }
            }

            List<List<Integer>> immutableAdjacency = new ArrayList<>();

            for (List<Integer> neighbors : mutableAdjacency) {
                immutableAdjacency.add(List.copyOf(neighbors));
            }

            this.adjacency = List.copyOf(immutableAdjacency);
        }

        int size() {
            return sites.size();
        }

        Site site(int index) {
            return sites.get(index);
        }

        List<Integer> neighbors(int index) {
            return adjacency.get(index);
        }

        int indexOf(String id) {
            Integer index = indexById.get(id);

            if (index == null) {
                throw new TreeValidationException(
                    "Unknown root site: " + id
                );
            }

            return index;
        }
    }

    static final class DynamicProgrammingStrategy {

        DpMetrics analyze(TreeGraph graph, int root) {
            int n = graph.size();

            int[] parent = new int[n];
            int[] depth = new int[n];
            Arrays.fill(parent, -2);

            List<Integer> order = new ArrayList<>();
            ArrayDeque<Integer> stack = new ArrayDeque<>();

            parent[root] = -1;
            stack.push(root);

            // Iterative traversal avoids stack overflow on deep trees.
            while (!stack.isEmpty()) {
                int current = stack.pop();
                order.add(current);

                for (int neighbor : graph.neighbors(current)) {
                    if (neighbor == parent[current]) {
                        continue;
                    }

                    if (parent[neighbor] != -2) {
                        throw new TreeValidationException(
                            "Cycle encountered during analysis."
                        );
                    }

                    parent[neighbor] = current;
                    depth[neighbor] = depth[current] + 1;
                    stack.push(neighbor);
                }
            }

            if (order.size() != n) {
                throw new TreeValidationException(
                    "Root cannot reach every site."
                );
            }

            int[] down = new int[n];
            int[] up = new int[n];
            int[] childFirst = new int[n];
            int[] childSecond = new int[n];
            int[] bestChild = new int[n];
            int[] through = new int[n];

            Arrays.fill(bestChild, -1);

            // Bottom-up pass stores the two largest child branches.
            for (int position = n - 1; position >= 0; position--) {
                int node = order.get(position);

                int first = 0;
                int second = 0;
                int firstChild = -1;

                for (int child : graph.neighbors(node)) {
                    if (parent[child] != node) {
                        continue;
                    }

                    int branch = 1 + down[child];

                    if (branch > first) {
                        second = first;
                        first = branch;
                        firstChild = child;
                    } else if (branch > second) {
                        second = branch;
                    }
                }

                down[node] = first;
                childFirst[node] = first;
                childSecond[node] = second;
                bestChild[node] = firstChild;
            }

            int heightEdges = 0;

            // Top-down pass calculates the branch through the parent side.
            for (int node : order) {
                heightEdges = Math.max(heightEdges, depth[node]);

                int first = 0;
                int second = 0;

                if (parent[node] != -1) {
                    int value = up[node];
                    if (value > first) {
                        second = first;
                        first = value;
                    } else if (value > second) {
                        second = value;
                    }
                }

                for (int child : graph.neighbors(node)) {
                    if (parent[child] != node) {
                        continue;
                    }

                    int value = 1 + down[child];

                    if (value > first) {
                        second = first;
                        first = value;
                    } else if (value > second) {
                        second = value;
                    }
                }

                through[node] = first + second;

                for (int child : graph.neighbors(node)) {
                    if (parent[child] != node) {
                        continue;
                    }

                    int siblingHeight =
                        bestChild[node] == child
                            ? childSecond[node]
                            : childFirst[node];

                    up[child] = 1 + Math.max(
                        0,
                        Math.max(up[node], siblingHeight)
                    );
                }
            }

            int diameterEdges = 0;
            Map<String, Integer> throughBySite = new LinkedHashMap<>();

            for (int i = 0; i < n; i++) {
                diameterEdges = Math.max(diameterEdges, through[i]);
                throughBySite.put(graph.site(i).id(), through[i]);
            }

            return new DpMetrics(
                heightEdges,
                diameterEdges,
                Map.copyOf(throughBySite)
            );
        }
    }

    static final class TwoSweepStrategy {

        private record BfsState(
            int farthest,
            int[] distance,
            int[] parent
        ) {}

        private BfsState bfs(TreeGraph graph, int start) {
            int n = graph.size();

            int[] distance = new int[n];
            int[] parent = new int[n];

            Arrays.fill(distance, -1);
            Arrays.fill(parent, -1);

            ArrayDeque<Integer> queue = new ArrayDeque<>();
            distance[start] = 0;
            queue.add(start);

            int farthest = start;

            while (!queue.isEmpty()) {
                int current = queue.remove();

                if (distance[current] > distance[farthest]) {
                    farthest = current;
                }

                for (int neighbor : graph.neighbors(current)) {
                    if (distance[neighbor] != -1) {
                        continue;
                    }

                    distance[neighbor] = distance[current] + 1;
                    parent[neighbor] = current;
                    queue.add(neighbor);
                }
            }

            return new BfsState(farthest, distance, parent);
        }

        SweepMetrics analyze(TreeGraph graph, int root) {
            BfsState first = bfs(graph, root);
            int endpointA = first.farthest();

            BfsState second = bfs(graph, endpointA);
            int endpointB = second.farthest();

            List<Integer> reversePath = new ArrayList<>();
            int current = endpointB;

            while (current != -1) {
                reversePath.add(current);
                current = second.parent()[current];
            }

            Collections.reverse(reversePath);

            List<String> path = reversePath.stream()
                .map(index -> graph.site(index).id())
                .toList();

            return new SweepMetrics(
                second.distance()[endpointB],
                graph.site(endpointA).id(),
                graph.site(endpointB).id(),
                path
            );
        }
    }

    static final class TreeAnalysisService {
        private final DiameterPolicy policy;
        private final DynamicProgrammingStrategy dpStrategy;
        private final TwoSweepStrategy sweepStrategy;

        TreeAnalysisService(DiameterPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
            this.dpStrategy = new DynamicProgrammingStrategy();
            this.sweepStrategy = new TwoSweepStrategy();
        }

        AnalysisResult analyze(TreeGraph graph, String rootId) {
            Objects.requireNonNull(graph, "Tree graph is required.");

            if (graph.size() > policy.maximumSites()) {
                throw new TreeValidationException(
                    "The tree exceeds the policy site limit of "
                    + policy.maximumSites()
                );
            }

            int root = graph.indexOf(rootId);

            DpMetrics dp = dpStrategy.analyze(graph, root);
            SweepMetrics sweep = sweepStrategy.analyze(graph, root);

            if (dp.diameterEdges() != sweep.diameterEdges()) {
                throw new IllegalStateException(
                    "Diameter strategies produced different results."
                );
            }

            int diameterNodes = dp.diameterEdges() + 1;

            int reportedDiameter =
                policy.outputUnit() == MeasurementUnit.EDGES
                    ? dp.diameterEdges()
                    : diameterNodes;

            return new AnalysisResult(
                rootId,
                dp.heightEdges(),
                dp.diameterEdges(),
                diameterNodes,
                reportedDiameter,
                policy.outputUnit(),
                sweep.endpointA(),
                sweep.endpointB(),
                sweep.longestPath(),
                dp.diameterThroughNode()
            );
        }
    }

    private static TreeGraph createExampleTree() {
        List<Site> sites = List.of(
            new Site("HQ", "Headquarters"),
            new Site("N", "North"),
            new Site("S", "South"),
            new Site("NE", "North-East"),
            new Site("NW", "North-West"),
            new Site("SC", "South-Central"),
            new Site("SE", "South-East"),
            new Site("SW", "South-West")
        );

        List<Link> links = List.of(
            new Link("HQ", "N"),
            new Link("HQ", "S"),
            new Link("N", "NE"),
            new Link("N", "NW"),
            new Link("S", "SC"),
            new Link("SC", "SE"),
            new Link("SC", "SW")
        );

        return new TreeGraph(sites, links);
    }

    private static void runTests() {
        TreeGraph chain = new TreeGraph(
            List.of(
                new Site("A", "A"),
                new Site("B", "B"),
                new Site("C", "C"),
                new Site("D", "D"),
                new Site("E", "E")
            ),
            List.of(
                new Link("A", "B"),
                new Link("B", "C"),
                new Link("C", "D"),
                new Link("D", "E")
            )
        );

        AnalysisResult chainResult = new TreeAnalysisService(
            new DiameterPolicy(10, MeasurementUnit.EDGES)
        ).analyze(chain, "A");

        if (chainResult.diameterEdges() != 4 ||
            chainResult.heightEdges() != 4) {
            throw new AssertionError("Chain test failed.");
        }

        TreeGraph singleton = new TreeGraph(
            List.of(new Site("ONLY", "Single site")),
            List.of()
        );

        AnalysisResult singleResult = new TreeAnalysisService(
            new DiameterPolicy(1, MeasurementUnit.NODES)
        ).analyze(singleton, "ONLY");

        if (singleResult.diameterEdges() != 0 ||
            singleResult.diameterNodes() != 1 ||
            singleResult.reportedDiameter() != 1) {
            throw new AssertionError("Single-node test failed.");
        }

        boolean cycleRejected = false;

        try {
            new TreeGraph(
                List.of(
                    new Site("A", "A"),
                    new Site("B", "B"),
                    new Site("C", "C")
                ),
                List.of(
                    new Link("A", "B"),
                    new Link("B", "C"),
                    new Link("C", "A")
                )
            );
        } catch (TreeValidationException expected) {
            cycleRejected = true;
        }

        if (!cycleRejected) {
            throw new AssertionError("Cycle validation test failed.");
        }

        boolean policyRejected = false;

        try {
            new TreeAnalysisService(
                new DiameterPolicy(3, MeasurementUnit.EDGES)
            ).analyze(chain, "A");
        } catch (TreeValidationException expected) {
            policyRejected = true;
        }

        if (!policyRejected) {
            throw new AssertionError("Policy limit test failed.");
        }
    }

    public static void main(String[] args) {
        try {
            runTests();

            TreeGraph graph = createExampleTree();

            DiameterPolicy policy = new DiameterPolicy(
                1000,
                MeasurementUnit.EDGES
            );

            TreeAnalysisService service = new TreeAnalysisService(policy);
            AnalysisResult result = service.analyze(graph, "HQ");

            System.out.println("ENTERPRISE TREE DIAMETER ANALYSIS");
            System.out.println("---------------------------------");
            System.out.println("Root: " + result.rootId());
            System.out.println("Height: " + result.heightEdges() + " edges");
            System.out.println(
                "Diameter: " + result.diameterEdges() + " edges"
            );
            System.out.println(
                "Diameter node count: " + result.diameterNodes()
            );
            System.out.println(
                "Policy measurement: " + result.reportedDiameter()
                + " " + result.reportedUnit()
            );
            System.out.println(
                "Endpoint A: " + result.endpointA()
            );
            System.out.println(
                "Endpoint B: " + result.endpointB()
            );
            System.out.println(
                "Longest path: " + String.join(" -> ", result.longestPath())
            );

            System.out.println("\nLongest path through each site:");
            result.diameterThroughNode().forEach(
                (site, distance) ->
                    System.out.println(site + ": " + distance + " edges")
            );

            System.out.println("\nAll tests passed.");
        } catch (RuntimeException error) {
            System.err.println(
                error.getClass().getSimpleName() + ": " + error.getMessage()
            );
            System.exitCode = 1;
        }
    }
}
