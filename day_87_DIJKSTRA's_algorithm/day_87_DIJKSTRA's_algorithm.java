import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

/**
 * Dijkstra's Algorithm: Enterprise Route Management
 *
 * Features:
 * - Immutable edge and route representations
 * - Directed and undirected graph support
 * - Priority queue optimization
 * - Single-source shortest-path computation
 * - Route reconstruction
 * - Validation and domain-specific exceptions
 * - Enterprise-oriented service layer
 *
 * Time complexity: O((V + E) log V)
 * Space complexity: O(V + E)
 */
public class DijkstraAlgorithm {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    record Edge(String destination, double weight) {
        Edge {
            if (destination == null || destination.isBlank()) {
                throw new IllegalArgumentException(
                    "Destination cannot be empty"
                );
            }

            if (!Double.isFinite(weight) || weight < 0) {
                throw new IllegalArgumentException(
                    "Weight must be finite and non-negative"
                );
            }
        }
    }

    record QueueEntry(String vertex, double distance) {}

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class UnknownVertexException extends GraphException {
        UnknownVertexException(String vertex) {
            super("Unknown vertex: " + vertex);
        }
    }

    static class NegativeWeightException extends GraphException {
        NegativeWeightException() {
            super("Negative weights are not supported");
        }
    }

    static class Route {
        private final String source;
        private final String destination;
        private final double distance;
        private final List<String> path;

        Route(
            String source,
            String destination,
            double distance,
            List<String> path
        ) {
            this.source = source;
            this.destination = destination;
            this.distance = distance;
            this.path = List.copyOf(path);
        }

        public String source() {
            return source;
        }

        public String destination() {
            return destination;
        }

        public double distance() {
            return distance;
        }

        public List<String> path() {
            return path;
        }

        @Override
        public String toString() {
            return "Route{" +
                "source='" + source + '\'' +
                ", destination='" + destination + '\'' +
                ", distance=" + distance +
                ", path=" + path +
                '}';
        }
    }

    static class WeightedGraph {
        private final GraphType type;

        private final Map<String, List<Edge>> adjacency =
            new HashMap<>();

        WeightedGraph(GraphType type) {
            this.type = type;
        }

        public void addVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex cannot be empty"
                );
            }

            adjacency.computeIfAbsent(
                vertex,
                key -> new ArrayList<>()
            );
        }

        public void addEdge(
            String source,
            String destination,
            double weight
        ) {
            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Weight must be finite"
                );
            }

            if (weight < 0) {
                throw new NegativeWeightException();
            }

            addVertex(source);
            addVertex(destination);

            adjacency.get(source).add(
                new Edge(destination, weight)
            );

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(destination).add(
                    new Edge(source, weight)
                );
            }
        }

        public Set<String> vertices() {
            return Collections.unmodifiableSet(
                adjacency.keySet()
            );
        }

        public Map<String, List<Edge>> snapshot() {
            Map<String, List<Edge>> copy = new HashMap<>();

            adjacency.forEach((vertex, edges) ->
                copy.put(vertex, List.copyOf(edges))
            );

            return Collections.unmodifiableMap(copy);
        }
    }

    record ShortestPathResult(
        String source,
        Map<String, Double> distances,
        Map<String, String> predecessors
    ) {
        ShortestPathResult {
            distances = Map.copyOf(distances);
            predecessors = Map.copyOf(predecessors);
        }

        public List<String> pathTo(String destination) {
            if (!distances.containsKey(destination)) {
                throw new UnknownVertexException(destination);
            }

            if (Double.isInfinite(distances.get(destination))) {
                return List.of();
            }

            List<String> path = new ArrayList<>();

            String current = destination;

            while (current != null) {
                path.add(current);

                if (current.equals(source)) {
                    break;
                }

                current = predecessors.get(current);

                if (current == null) {
                    throw new GraphException(
                        "Invalid predecessor chain"
                    );
                }
            }

            Collections.reverse(path);

            return List.copyOf(path);
        }
    }

    static class ShortestPathService {

        public ShortestPathResult calculate(
            WeightedGraph graph,
            String source
        ) {
            if (graph == null) {
                throw new IllegalArgumentException(
                    "Graph cannot be null"
                );
            }

            Map<String, List<Edge>> adjacency =
                graph.snapshot();

            if (!adjacency.containsKey(source)) {
                throw new UnknownVertexException(source);
            }

            Map<String, Double> distances = new HashMap<>();
            Map<String, String> predecessors = new HashMap<>();

            for (String vertex : adjacency.keySet()) {
                distances.put(
                    vertex,
                    Double.POSITIVE_INFINITY
                );
            }

            distances.put(source, 0.0);

            PriorityQueue<QueueEntry> queue =
                new PriorityQueue<>(
                    Comparator.comparingDouble(
                        QueueEntry::distance
                    )
                );

            queue.offer(new QueueEntry(source, 0.0));

            while (!queue.isEmpty()) {
                QueueEntry current = queue.poll();

                String vertex = current.vertex();

                // Ignore outdated queue entries.
                if (
                    current.distance() >
                    distances.get(vertex)
                ) {
                    continue;
                }

                for (Edge edge : adjacency.get(vertex)) {
                    double candidate =
                        current.distance() + edge.weight();

                    if (!Double.isFinite(candidate)) {
                        throw new ArithmeticException(
                            "Distance overflow"
                        );
                    }

                    if (
                        candidate <
                        distances.get(edge.destination())
                    ) {
                        distances.put(
                            edge.destination(),
                            candidate
                        );

                        predecessors.put(
                            edge.destination(),
                            vertex
                        );

                        queue.offer(
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
                predecessors
            );
        }

        public Route findRoute(
            WeightedGraph graph,
            String source,
            String destination
        ) {
            ShortestPathResult result =
                calculate(graph, source);

            if (!result.distances().containsKey(destination)) {
                throw new UnknownVertexException(destination);
            }

            double distance =
                result.distances().get(destination);

            if (Double.isInfinite(distance)) {
                return new Route(
                    source,
                    destination,
                    distance,
                    List.of()
                );
            }

            return new Route(
                source,
                destination,
                distance,
                result.pathTo(destination)
            );
        }
    }

    static class RouteGovernanceService {

        private final ShortestPathService shortestPathService;

        RouteGovernanceService(
            ShortestPathService shortestPathService
        ) {
            this.shortestPathService = shortestPathService;
        }

        public Route validateAndCalculate(
            WeightedGraph graph,
            String source,
            String destination,
            double maximumAllowedDistance
        ) {
            if (
                !Double.isFinite(maximumAllowedDistance) ||
                maximumAllowedDistance < 0
            ) {
                throw new IllegalArgumentException(
                    "Invalid maximum distance"
                );
            }

            Route route = shortestPathService.findRoute(
                graph,
                source,
                destination
            );

            if (Double.isInfinite(route.distance())) {
                return route;
            }

            if (route.distance() > maximumAllowedDistance) {
                throw new GraphException(
                    "Route exceeds permitted distance"
                );
            }

            return route;
        }
    }

    private static void runTests() {
        WeightedGraph graph =
            new WeightedGraph(GraphType.DIRECTED);

        graph.addEdge("S", "A", 10);
        graph.addEdge("S", "B", 3);
        graph.addEdge("B", "A", 2);
        graph.addEdge("A", "T", 4);
        graph.addEdge("B", "T", 8);

        graph.addVertex("Z");

        ShortestPathService service =
            new ShortestPathService();

        ShortestPathResult result =
            service.calculate(graph, "S");

        assert result.distances().get("A") == 5.0;
        assert result.distances().get("T") == 9.0;

        assert result.pathTo("T").equals(
            List.of("S", "B", "A", "T")
        );

        assert Double.isInfinite(
            result.distances().get("Z")
        );

        // Zero-weight edges.
        WeightedGraph zeroGraph =
            new WeightedGraph(GraphType.DIRECTED);

        zeroGraph.addEdge("X", "Y", 0);
        zeroGraph.addEdge("Y", "Z", 0);

        assert service.calculate(zeroGraph, "X")
            .distances().get("Z") == 0.0;

        // Negative weight validation.
        boolean rejected = false;

        try {
            graph.addEdge("S", "Z", -1);
        } catch (NegativeWeightException exception) {
            rejected = true;
        }

        assert rejected;

        // Unknown source validation.
        rejected = false;

        try {
            service.calculate(graph, "UNKNOWN");
        } catch (UnknownVertexException exception) {
            rejected = true;
        }

        assert rejected;

        // Enterprise distance policy.
        RouteGovernanceService governance =
            new RouteGovernanceService(service);

        Route route = governance.validateAndCalculate(
            graph,
            "S",
            "T",
            10
        );

        assert route.distance() == 9.0;

        System.out.println("All tests passed.");
    }

    public static void main(String[] args) {
        WeightedGraph graph =
            new WeightedGraph(GraphType.UNDIRECTED);

        graph.addEdge("A", "B", 4);
        graph.addEdge("A", "C", 2);
        graph.addEdge("B", "C", 1);
        graph.addEdge("B", "D", 5);
        graph.addEdge("C", "D", 8);
        graph.addEdge("C", "E", 10);
        graph.addEdge("D", "E", 2);
        graph.addEdge("D", "F", 6);
        graph.addEdge("E", "F", 3);

        graph.addVertex("G");

        ShortestPathService service =
            new ShortestPathService();

        ShortestPathResult result =
            service.calculate(graph, "A");

        System.out.println(
            "DIJKSTRA ENTERPRISE ROUTE MANAGEMENT"
        );

        System.out.println("\nShortest paths from A:");

        result.distances().entrySet()
            .stream()
            .sorted(Map.Entry.comparingByKey())
            .forEach(entry -> {
                String vertex = entry.getKey();
                double distance = entry.getValue();

                if (Double.isInfinite(distance)) {
                    System.out.println(
                        vertex + ": Unreachable"
                    );
                } else {
                    System.out.println(
                        vertex +
                        ": distance=" + distance +
                        ", path=" + result.pathTo(vertex)
                    );
                }
            });

        RouteGovernanceService governance =
            new RouteGovernanceService(service);

        System.out.println("\nValidated route:");

        Route route = governance.validateAndCalculate(
            graph,
            "A",
            "F",
            20
        );

        System.out.println(route);

        System.out.println("\nRunning tests...");

        runTests();
    }
}
