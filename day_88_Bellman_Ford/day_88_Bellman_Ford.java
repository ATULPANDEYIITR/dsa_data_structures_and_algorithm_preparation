import java.math.BigInteger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.Set;

/**
 * Bellman-Ford and Dijkstra enterprise graph analysis.
 *
 * Java 17 features:
 * - Records
 * - Enums
 * - Immutable domain objects
 * - Collections and streams
 * - Service-oriented design
 * - Explicit validation
 * - Custom exceptions
 * - State and policy modeling
 *
 * Compile:
 * javac Main.java
 *
 * Run:
 * java Main
 */
public class Main {

    private static final BigInteger ZERO = BigInteger.ZERO;

    enum Algorithm {
        BELLMAN_FORD,
        DIJKSTRA
    }

    enum GraphStatus {
        VALID,
        NEGATIVE_EDGES_PRESENT
    }

    enum AnalysisStatus {
        COMPLETED,
        NEGATIVE_CYCLE_DETECTED
    }

    record Edge(int source, int destination, BigInteger weight) {
        Edge {
            if (weight == null) {
                throw new IllegalArgumentException(
                    "Edge weight cannot be null."
                );
            }
        }
    }

    record QueueEntry(int vertex, BigInteger distance) {}

    record AnalysisPolicy(
        boolean allowNegativeWeights,
        boolean detectNegativeCycles
    ) {}

    static class GraphValidationException extends RuntimeException {
        GraphValidationException(String message) {
            super(message);
        }
    }

    static class AlgorithmPolicyException extends RuntimeException {
        AlgorithmPolicyException(String message) {
            super(message);
        }
    }

    static class ShortestPathResult {
        private final int source;

        private final Map<Integer, BigInteger> distances;
        private final Map<Integer, Integer> predecessors;

        private final Set<Integer> affectedVertices;

        private final int iterations;
        private final Algorithm algorithm;
        private final AnalysisStatus status;

        ShortestPathResult(
            int source,
            Map<Integer, BigInteger> distances,
            Map<Integer, Integer> predecessors,
            Set<Integer> affectedVertices,
            int iterations,
            Algorithm algorithm
        ) {
            this.source = source;

            this.distances = Map.copyOf(distances);
            this.predecessors = Map.copyOf(predecessors);

            this.affectedVertices = Set.copyOf(affectedVertices);

            this.iterations = iterations;
            this.algorithm = algorithm;

            this.status = affectedVertices.isEmpty()
                ? AnalysisStatus.COMPLETED
                : AnalysisStatus.NEGATIVE_CYCLE_DETECTED;
        }

        int source() {
            return source;
        }

        BigInteger distanceTo(int destination) {
            if (affectedVertices.contains(destination)) {
                throw new AlgorithmPolicyException(
                    "Distance is undefined due to a reachable negative cycle."
                );
            }

            return distances.get(destination);
        }

        List<Integer> pathTo(int destination) {
            if (!distances.containsKey(destination)) {
                throw new GraphValidationException(
                    "Unknown destination vertex."
                );
            }

            if (affectedVertices.contains(destination)) {
                throw new AlgorithmPolicyException(
                    "Path is undefined due to a reachable negative cycle."
                );
            }

            if (distances.get(destination) == null) {
                return List.of();
            }

            List<Integer> path = new ArrayList<>();
            Set<Integer> visited = new HashSet<>();

            Integer current = destination;

            while (current != null) {
                if (!visited.add(current)) {
                    throw new IllegalStateException(
                        "Predecessor cycle detected."
                    );
                }

                path.add(current);
                current = predecessors.get(current);
            }

            java.util.Collections.reverse(path);

            if (path.isEmpty() || path.get(0) != source) {
                return List.of();
            }

            return List.copyOf(path);
        }

        Map<Integer, BigInteger> distances() {
            return distances;
        }

        Set<Integer> affectedVertices() {
            return affectedVertices;
        }

        int iterations() {
            return iterations;
        }

        Algorithm algorithm() {
            return algorithm;
        }

        AnalysisStatus status() {
            return status;
        }
    }

    static final class DirectedGraph {
        private final Set<Integer> vertices = new HashSet<>();

        private final List<Edge> edges = new ArrayList<>();

        private final Map<Integer, List<Edge>> adjacency =
            new HashMap<>();

        DirectedGraph(List<Integer> inputVertices) {
            if (inputVertices == null || inputVertices.isEmpty()) {
                throw new GraphValidationException(
                    "Graph must contain at least one vertex."
                );
            }

            for (int vertex : inputVertices) {
                if (!vertices.add(vertex)) {
                    throw new GraphValidationException(
                        "Duplicate vertex identifier."
                    );
                }

                adjacency.put(vertex, new ArrayList<>());
            }
        }

        void addEdge(int source, int destination, long weight) {
            if (!vertices.contains(source) ||
                !vertices.contains(destination)) {
                throw new GraphValidationException(
                    "Edge references an unknown vertex."
                );
            }

            Edge edge = new Edge(
                source,
                destination,
                BigInteger.valueOf(weight)
            );

            edges.add(edge);
            adjacency.get(source).add(edge);
        }

        void validateSource(int source) {
            if (!vertices.contains(source)) {
                throw new GraphValidationException(
                    "Unknown source vertex: " + source
                );
            }
        }

        List<Integer> vertices() {
            return List.copyOf(vertices);
        }

        List<Edge> edges() {
            return List.copyOf(edges);
        }

        List<Edge> outgoingEdges(int vertex) {
            return List.copyOf(adjacency.get(vertex));
        }

        boolean hasNegativeEdges() {
            return edges.stream()
                .anyMatch(edge -> edge.weight().signum() < 0);
        }
    }

    static final class BellmanFordService {

        private final AnalysisPolicy policy;

        BellmanFordService(AnalysisPolicy policy) {
            this.policy = policy;
        }

        ShortestPathResult analyze(
            DirectedGraph graph,
            int source
        ) {
            graph.validateSource(source);

            if (!policy.allowNegativeWeights() &&
                graph.hasNegativeEdges()) {
                throw new AlgorithmPolicyException(
                    "Policy prohibits negative edge weights."
                );
            }

            Map<Integer, BigInteger> distances = new HashMap<>();
            Map<Integer, Integer> predecessors = new HashMap<>();

            for (int vertex : graph.vertices()) {
                distances.put(vertex, null);
                predecessors.put(vertex, null);
            }

            distances.put(source, ZERO);

            int iterations = 0;

            // Relax all edges at most V-1 times.
            for (int pass = 1; pass < graph.vertices().size(); pass++) {
                boolean changed = false;
                iterations++;

                for (Edge edge : graph.edges()) {
                    BigInteger current = distances.get(edge.source());

                    if (current == null) {
                        continue;
                    }

                    BigInteger candidate = current.add(edge.weight());

                    BigInteger previous =
                        distances.get(edge.destination());

                    if (previous == null ||
                        candidate.compareTo(previous) < 0) {

                        distances.put(edge.destination(), candidate);
                        predecessors.put(
                            edge.destination(),
                            edge.source()
                        );

                        changed = true;
                    }
                }

                if (!changed) {
                    break;
                }
            }

            Set<Integer> affected = new HashSet<>();

            if (policy.detectNegativeCycles()) {
                // Detect additional improvements after V-1 passes.
                for (Edge edge : graph.edges()) {
                    BigInteger current = distances.get(edge.source());

                    if (current == null) {
                        continue;
                    }

                    BigInteger candidate = current.add(edge.weight());
                    BigInteger previous =
                        distances.get(edge.destination());

                    if (previous == null ||
                        candidate.compareTo(previous) < 0) {
                        affected.add(edge.destination());
                    }
                }

                // Mark all downstream vertices as affected.
                Queue<Integer> queue = new ArrayDeque<>(affected);

                while (!queue.isEmpty()) {
                    int current = queue.remove();

                    for (Edge edge : graph.outgoingEdges(current)) {
                        if (affected.add(edge.destination())) {
                            queue.add(edge.destination());
                        }
                    }
                }
            }

            return new ShortestPathResult(
                source,
                distances,
                predecessors,
                affected,
                iterations,
                Algorithm.BELLMAN_FORD
            );
        }
    }

    static final class DijkstraService {

        ShortestPathResult analyze(
            DirectedGraph graph,
            int source
        ) {
            graph.validateSource(source);

            if (graph.hasNegativeEdges()) {
                throw new AlgorithmPolicyException(
                    "Dijkstra requires nonnegative edge weights."
                );
            }

            Map<Integer, BigInteger> distances = new HashMap<>();
            Map<Integer, Integer> predecessors = new HashMap<>();

            for (int vertex : graph.vertices()) {
                distances.put(vertex, null);
                predecessors.put(vertex, null);
            }

            PriorityQueue<QueueEntry> queue =
                new PriorityQueue<>(
                    Comparator.comparing(QueueEntry::distance)
                );

            Set<Integer> settled = new HashSet<>();

            distances.put(source, ZERO);

            queue.add(new QueueEntry(source, ZERO));

            int iterations = 0;

            while (!queue.isEmpty()) {
                QueueEntry current = queue.poll();
                iterations++;

                if (!current.distance().equals(
                    distances.get(current.vertex())
                )) {
                    continue;
                }

                if (!settled.add(current.vertex())) {
                    continue;
                }

                for (Edge edge :
                    graph.outgoingEdges(current.vertex())) {

                    BigInteger candidate =
                        current.distance().add(edge.weight());

                    BigInteger previous =
                        distances.get(edge.destination());

                    if (previous == null ||
                        candidate.compareTo(previous) < 0) {

                        distances.put(edge.destination(), candidate);

                        predecessors.put(
                            edge.destination(),
                            current.vertex()
                        );

                        queue.add(
                            new QueueEntry(
                                edge.destination(),
                                candidate
                            )
                        );
                    }
                }
            }

            return new ShortestPathResult(
                source,
                distances,
                predecessors,
                Set.of(),
                iterations,
                Algorithm.DIJKSTRA
            );
        }
    }

    static void printResult(
        ShortestPathResult result,
        List<Integer> vertices
    ) {
        System.out.println("\nAlgorithm: " + result.algorithm());
        System.out.println("Source: " + result.source());
        System.out.println("Status: " + result.status());
        System.out.println("Iterations: " + result.iterations());

        System.out.printf(
            "%-12s %-22s %s%n",
            "Vertex",
            "Distance",
            "Path"
        );

        for (int vertex : vertices) {
            if (result.affectedVertices().contains(vertex)) {
                System.out.printf(
                    "%-12d %-22s %s%n",
                    vertex,
                    "Undefined",
                    "Negative cycle"
                );

                continue;
            }

            BigInteger distance = result.distances().get(vertex);

            if (distance == null) {
                System.out.printf(
                    "%-12d %-22s %s%n",
                    vertex,
                    "Unreachable",
                    "None"
                );

                continue;
            }

            System.out.printf(
                "%-12d %-22s %s%n",
                vertex,
                distance,
                result.pathTo(vertex)
            );
        }
    }

    static void demonstrateNegativeEdges() {
        System.out.println("\n========== NEGATIVE EDGES ==========");

        DirectedGraph graph = new DirectedGraph(
            List.of(0, 1, 2, 3, 4, 5)
        );

        graph.addEdge(0, 1, 4);
        graph.addEdge(0, 2, 5);
        graph.addEdge(1, 2, -2);
        graph.addEdge(1, 3, 6);
        graph.addEdge(2, 3, 3);
        graph.addEdge(3, 4, 2);
        graph.addEdge(4, 1, 1);

        AnalysisPolicy policy = new AnalysisPolicy(true, true);

        BellmanFordService service =
            new BellmanFordService(policy);

        ShortestPathResult result = service.analyze(graph, 0);

        printResult(result, graph.vertices());

        assert result.distances().get(1).equals(BigInteger.valueOf(4));
        assert result.distances().get(2).equals(BigInteger.valueOf(2));
        assert result.distances().get(4).equals(BigInteger.valueOf(7));
        assert !result.status().equals(
            AnalysisStatus.NEGATIVE_CYCLE_DETECTED
        );

        try {
            new DijkstraService().analyze(graph, 0);
        } catch (AlgorithmPolicyException exception) {
            System.out.println(
                "\nDijkstra rejected: " + exception.getMessage()
            );
        }
    }

    static void demonstrateNegativeCycle() {
        System.out.println("\n========== NEGATIVE CYCLE ==========");

        DirectedGraph graph = new DirectedGraph(
            List.of(0, 1, 2, 3, 4, 5)
        );

        graph.addEdge(0, 1, 2);
        graph.addEdge(1, 2, 2);
        graph.addEdge(2, 3, -5);
        graph.addEdge(3, 1, 1);
        graph.addEdge(3, 4, 3);
        graph.addEdge(5, 5, -1);

        BellmanFordService service =
            new BellmanFordService(
                new AnalysisPolicy(true, true)
            );

        ShortestPathResult result = service.analyze(graph, 0);

        printResult(result, graph.vertices());

        assert result.affectedVertices().containsAll(
            Set.of(1, 2, 3, 4)
        );

        assert !result.affectedVertices().contains(5);
    }

    static void demonstrateComparison() {
        System.out.println("\n========== DIJKSTRA COMPARISON ==========");

        DirectedGraph graph = new DirectedGraph(
            List.of(0, 1, 2, 3, 4)
        );

        graph.addEdge(0, 1, 10);
        graph.addEdge(0, 2, 3);
        graph.addEdge(2, 1, 2);
        graph.addEdge(1, 3, 4);
        graph.addEdge(2, 3, 8);
        graph.addEdge(2, 4, 2);
        graph.addEdge(4, 3, 1);

        ShortestPathResult bellman =
            new BellmanFordService(
                new AnalysisPolicy(true, true)
            ).analyze(graph, 0);

        ShortestPathResult dijkstra =
            new DijkstraService().analyze(graph, 0);

        printResult(bellman, graph.vertices());
        printResult(dijkstra, graph.vertices());

        assert bellman.distances().equals(dijkstra.distances());

        System.out.println("\nBoth algorithms agree.");
    }

    static void demonstratePolicyValidation() {
        System.out.println("\n========== POLICY VALIDATION ==========");

        DirectedGraph graph = new DirectedGraph(
            List.of(0, 1)
        );

        graph.addEdge(0, 1, -5);

        try {
            new BellmanFordService(
                new AnalysisPolicy(false, true)
            ).analyze(graph, 0);
        } catch (AlgorithmPolicyException exception) {
            System.out.println(exception.getMessage());
        }
    }

    public static void main(String[] args) {
        try {
            demonstrateNegativeEdges();
            demonstrateNegativeCycle();
            demonstrateComparison();
            demonstratePolicyValidation();

            System.out.println("\nAll Java 17 tests passed.");
        } catch (RuntimeException exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
