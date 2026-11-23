import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/**
 * Bipartite Graphs: Enterprise Conflict Assignment System.
 *
 * Models:
 * - Two-coloring.
 * - BFS and DFS graph traversal.
 * - Bipartite condition.
 * - Odd-cycle reconstruction.
 * - Connected components.
 * - Assignment policy validation.
 * - Immutable analysis results.
 * - Explicit domain validation and state transitions.
 *
 * Compile:
 *   javac BipartiteGraphEnterprise.java
 *
 * Run:
 *   java BipartiteGraphEnterprise
 */

public class BipartiteGraphEnterprise {

    enum Color {
        RED,
        BLUE;

        public Color opposite() {
            return this == RED ? BLUE : RED;
        }
    }

    enum Algorithm {
        BFS,
        DFS
    }

    enum AssignmentStatus {
        APPROVED,
        REJECTED
    }

    record Edge(int source, int target) {
        Edge {
            if (source < 0 || target < 0) {
                throw new IllegalArgumentException(
                    "Vertex identifiers cannot be negative."
                );
            }
        }
    }

    record AnalysisResult(
        boolean bipartite,
        List<Color> colors,
        List<Integer> oddCycle,
        int components,
        Algorithm algorithm
    ) {
        AnalysisResult {
            colors = Collections.unmodifiableList(
                new ArrayList<>(colors)
            );

            oddCycle = Collections.unmodifiableList(
                new ArrayList<>(oddCycle)
            );

            Objects.requireNonNull(algorithm);
        }
    }

    record AssignmentDecision(
        AssignmentStatus status,
        String reason,
        AnalysisResult analysis
    ) {}

    static class GraphValidationException extends RuntimeException {
        GraphValidationException(String message) {
            super(message);
        }
    }

    static class BipartiteGraph {
        private final int vertexCount;
        private final List<Set<Integer>> adjacency;

        BipartiteGraph(int vertexCount) {
            if (vertexCount < 0) {
                throw new IllegalArgumentException(
                    "Vertex count cannot be negative."
                );
            }

            this.vertexCount = vertexCount;
            this.adjacency = new ArrayList<>();

            for (int i = 0; i < vertexCount; i++) {
                adjacency.add(new HashSet<>());
            }
        }

        private void validateVertex(int vertex) {
            if (vertex < 0 || vertex >= vertexCount) {
                throw new GraphValidationException(
                    "Invalid vertex: " + vertex
                );
            }
        }

        void addEdge(int u, int v) {
            validateVertex(u);
            validateVertex(v);

            adjacency.get(u).add(v);

            if (u != v) {
                adjacency.get(v).add(u);
            }
        }

        boolean removeEdge(int u, int v) {
            validateVertex(u);
            validateVertex(v);

            boolean removed = adjacency.get(u).remove(v);

            if (u != v) {
                adjacency.get(v).remove(u);
            }

            return removed;
        }

        private List<Integer> reconstructCycle(
            int u,
            int v,
            int[] parent,
            int[] depth
        ) {
            int a = u;
            int b = v;

            List<Integer> pathA = new ArrayList<>();
            List<Integer> pathB = new ArrayList<>();

            pathA.add(a);
            pathB.add(b);

            while (depth[a] > depth[b]) {
                a = parent[a];
                pathA.add(a);
            }

            while (depth[b] > depth[a]) {
                b = parent[b];
                pathB.add(b);
            }

            while (a != b) {
                a = parent[a];
                b = parent[b];

                pathA.add(a);
                pathB.add(b);
            }

            for (int i = pathB.size() - 2; i >= 0; i--) {
                pathA.add(pathB.get(i));
            }

            pathA.add(u);

            return pathA;
        }

        AnalysisResult analyzeBFS() {
            List<Color> colors = new ArrayList<>(
                Collections.nCopies(vertexCount, null)
            );

            int[] parent = new int[vertexCount];
            int[] depth = new int[vertexCount];

            java.util.Arrays.fill(parent, -1);

            int components = 0;

            for (int start = 0; start < vertexCount; start++) {
                if (colors.get(start) != null) {
                    continue;
                }

                components++;
                colors.set(start, Color.RED);

                Deque<Integer> queue = new ArrayDeque<>();
                queue.addLast(start);

                while (!queue.isEmpty()) {
                    int u = queue.removeFirst();

                    for (int v : adjacency.get(u)) {
                        Color current = colors.get(u);
                        Color neighbor = colors.get(v);

                        if (neighbor == null) {
                            colors.set(v, current.opposite());
                            parent[v] = u;
                            depth[v] = depth[u] + 1;
                            queue.addLast(v);
                        } else if (neighbor == current) {
                            return new AnalysisResult(
                                false,
                                colors,
                                reconstructCycle(
                                    u, v, parent, depth
                                ),
                                components,
                                Algorithm.BFS
                            );
                        }
                    }
                }
            }

            return new AnalysisResult(
                true, colors, List.of(), components, Algorithm.BFS
            );
        }

        AnalysisResult analyzeDFS() {
            List<Color> colors = new ArrayList<>(
                Collections.nCopies(vertexCount, null)
            );

            int[] parent = new int[vertexCount];
            int[] depth = new int[vertexCount];

            java.util.Arrays.fill(parent, -1);

            int components = 0;

            for (int start = 0; start < vertexCount; start++) {
                if (colors.get(start) != null) {
                    continue;
                }

                components++;
                colors.set(start, Color.RED);

                Deque<Integer> stack = new ArrayDeque<>();
                stack.push(start);

                while (!stack.isEmpty()) {
                    int u = stack.pop();

                    for (int v : adjacency.get(u)) {
                        Color current = colors.get(u);
                        Color neighbor = colors.get(v);

                        if (neighbor == null) {
                            colors.set(v, current.opposite());
                            parent[v] = u;
                            depth[v] = depth[u] + 1;
                            stack.push(v);
                        } else if (neighbor == current) {
                            return new AnalysisResult(
                                false,
                                colors,
                                reconstructCycle(
                                    u, v, parent, depth
                                ),
                                components,
                                Algorithm.DFS
                            );
                        }
                    }
                }
            }

            return new AnalysisResult(
                true, colors, List.of(), components, Algorithm.DFS
            );
        }

        int vertexCount() {
            return vertexCount;
        }
    }

    interface AssignmentPolicy {
        AssignmentDecision evaluate(BipartiteGraph graph);
    }

    static class TwoSlotAssignmentPolicy implements AssignmentPolicy {

        @Override
        public AssignmentDecision evaluate(BipartiteGraph graph) {
            AnalysisResult result = graph.analyzeBFS();

            if (result.bipartite()) {
                return new AssignmentDecision(
                    AssignmentStatus.APPROVED,
                    "All conflict constraints can be satisfied using "
                        + "two distinct assignment groups.",
                    result
                );
            }

            return new AssignmentDecision(
                AssignmentStatus.REJECTED,
                "An odd cycle makes a two-group assignment impossible.",
                result
            );
        }
    }

    static class AssignmentService {
        private final AssignmentPolicy policy;

        AssignmentService(AssignmentPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        AssignmentDecision validate(BipartiteGraph graph) {
            Objects.requireNonNull(graph);

            return policy.evaluate(graph);
        }

        void printDecision(AssignmentDecision decision) {
            System.out.println(
                "\nAssignment status: " + decision.status()
            );

            System.out.println("Reason: " + decision.reason());

            AnalysisResult result = decision.analysis();

            System.out.println("Algorithm: " + result.algorithm());
            System.out.println("Components: " + result.components());

            if (result.bipartite()) {
                List<Integer> red = new ArrayList<>();
                List<Integer> blue = new ArrayList<>();

                for (int i = 0; i < result.colors().size(); i++) {
                    if (result.colors().get(i) == Color.RED) {
                        red.add(i);
                    } else if (result.colors().get(i) == Color.BLUE) {
                        blue.add(i);
                    }
                }

                System.out.println("RED: " + red);
                System.out.println("BLUE: " + blue);
            } else {
                System.out.println(
                    "Odd cycle: " + result.oddCycle()
                );
            }
        }
    }

    private static void runTests() {
        BipartiteGraph even = new BipartiteGraph(4);

        even.addEdge(0, 1);
        even.addEdge(1, 2);
        even.addEdge(2, 3);
        even.addEdge(3, 0);

        if (!even.analyzeBFS().bipartite()) {
            throw new AssertionError("Even cycle should be bipartite.");
        }

        if (!even.analyzeDFS().bipartite()) {
            throw new AssertionError("DFS even cycle test failed.");
        }

        BipartiteGraph odd = new BipartiteGraph(3);

        odd.addEdge(0, 1);
        odd.addEdge(1, 2);
        odd.addEdge(2, 0);

        if (odd.analyzeBFS().bipartite()) {
            throw new AssertionError("Triangle must be rejected.");
        }

        BipartiteGraph selfLoop = new BipartiteGraph(1);
        selfLoop.addEdge(0, 0);

        if (selfLoop.analyzeDFS().bipartite()) {
            throw new AssertionError("Self-loop must be rejected.");
        }

        BipartiteGraph disconnected = new BipartiteGraph(7);

        disconnected.addEdge(0, 1);
        disconnected.addEdge(1, 2);
        disconnected.addEdge(3, 4);

        AnalysisResult result = disconnected.analyzeBFS();

        if (!result.bipartite() || result.components() != 4) {
            throw new AssertionError(
                "Disconnected graph validation failed."
            );
        }

        BipartiteGraph empty = new BipartiteGraph(0);

        if (!empty.analyzeBFS().bipartite()) {
            throw new AssertionError("Empty graph must be bipartite.");
        }

        System.out.println("\nAll Java tests passed.");
    }

    public static void main(String[] args) {
        System.out.println(
            "ENTERPRISE BIPARTITE GRAPH ASSIGNMENT SYSTEM"
        );

        BipartiteGraph graph = new BipartiteGraph(6);

        graph.addEdge(0, 1);
        graph.addEdge(1, 2);
        graph.addEdge(2, 3);
        graph.addEdge(3, 4);
        graph.addEdge(4, 5);
        graph.addEdge(5, 0);

        AssignmentService service = new AssignmentService(
            new TwoSlotAssignmentPolicy()
        );

        System.out.println("\nInitial assignment network:");

        AssignmentDecision initial = service.validate(graph);
        service.printDecision(initial);

        if (initial.status() != AssignmentStatus.APPROVED) {
            throw new IllegalStateException(
                "Expected valid assignment."
            );
        }

        System.out.println("\nIntroducing an additional conflict:");

        graph.addEdge(0, 2);

        AssignmentDecision updated = service.validate(graph);
        service.printDecision(updated);

        if (updated.status() != AssignmentStatus.REJECTED) {
            throw new IllegalStateException(
                "Odd cycle must prevent approval."
            );
        }

        System.out.println("\nRemoving the additional conflict:");

        graph.removeEdge(0, 2);

        AssignmentDecision restored = service.validate(graph);
        service.printDecision(restored);

        if (restored.status() != AssignmentStatus.APPROVED) {
            throw new IllegalStateException(
                "Valid assignment should be restored."
            );
        }

        runTests();
    }
}
