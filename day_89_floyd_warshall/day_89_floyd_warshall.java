import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/*
 * Floyd-Warshall Algorithm
 *
 * Enterprise-oriented all-pairs route optimization.
 *
 * Java version: 17
 *
 * Capabilities:
 * - Explicit domain types
 * - Weighted directed graph
 * - Dynamic programming
 * - Intermediate vertex processing
 * - Shortest-path reconstruction
 * - Negative cycle detection
 * - Validation and custom exceptions
 * - Route-planning service
 * - Immutable query results
 */

public class FloydWarshall {

    enum ComputationStatus {
        NOT_COMPUTED,
        COMPUTED,
        FAILED
    }

    record Edge(int source, int destination, double weight) {

        Edge {
            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Edge weight must be finite."
                );
            }
        }
    }

    record RouteResult(
        int source,
        int destination,
        double distance,
        List<Integer> path
    ) {
        RouteResult {
            path = List.copyOf(path);
        }

        boolean reachable() {
            return Double.isFinite(distance);
        }
    }

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class NegativeCycleException extends GraphException {
        NegativeCycleException(String message) {
            super(message);
        }
    }

    static class WeightedGraph {

        private final int vertexCount;

        private final double[][] distance;
        private final int[][] nextVertex;

        private ComputationStatus status =
            ComputationStatus.NOT_COMPUTED;

        private long version = 0;

        WeightedGraph(int vertexCount) {
            if (vertexCount <= 0) {
                throw new IllegalArgumentException(
                    "Vertex count must be positive."
                );
            }

            this.vertexCount = vertexCount;

            distance = new double[vertexCount][vertexCount];
            nextVertex = new int[vertexCount][vertexCount];

            for (int i = 0; i < vertexCount; i++) {
                for (int j = 0; j < vertexCount; j++) {
                    distance[i][j] = Double.POSITIVE_INFINITY;
                    nextVertex[i][j] = -1;
                }

                distance[i][i] = 0;
                nextVertex[i][i] = i;
            }
        }

        int getVertexCount() {
            return vertexCount;
        }

        long getVersion() {
            return version;
        }

        private void validateVertex(int vertex) {
            if (vertex < 0 || vertex >= vertexCount) {
                throw new GraphException(
                    "Invalid vertex: " + vertex
                );
            }
        }

        void addEdge(Edge edge) {
            validateVertex(edge.source());
            validateVertex(edge.destination());

            int source = edge.source();
            int destination = edge.destination();

            if (edge.weight() < distance[source][destination]) {
                distance[source][destination] = edge.weight();
                nextVertex[source][destination] = destination;

                version++;

                status = ComputationStatus.NOT_COMPUTED;
            }
        }

        double[][] copyDistanceMatrix() {
            double[][] copy = new double[vertexCount][vertexCount];

            for (int i = 0; i < vertexCount; i++) {
                System.arraycopy(
                    distance[i],
                    0,
                    copy[i],
                    0,
                    vertexCount
                );
            }

            return copy;
        }

        int[][] copyNextMatrix() {
            int[][] copy = new int[vertexCount][vertexCount];

            for (int i = 0; i < vertexCount; i++) {
                System.arraycopy(
                    nextVertex[i],
                    0,
                    copy[i],
                    0,
                    vertexCount
                );
            }

            return copy;
        }

        void updateMatrices(
            double[][] newDistance,
            int[][] newNext
        ) {
            for (int i = 0; i < vertexCount; i++) {
                System.arraycopy(
                    newDistance[i],
                    0,
                    distance[i],
                    0,
                    vertexCount
                );

                System.arraycopy(
                    newNext[i],
                    0,
                    nextVertex[i],
                    0,
                    vertexCount
                );
            }
        }

        void setStatus(ComputationStatus status) {
            this.status = status;
        }

        ComputationStatus getStatus() {
            return status;
        }
    }

    static class FloydWarshallService {

        private final WeightedGraph graph;

        private long computedVersion = -1;

        FloydWarshallService(WeightedGraph graph) {
            this.graph = graph;
        }

        /*
         * Each iteration introduces one additional permitted
         * intermediate vertex.
         *
         * Recurrence:
         *
         * D_k(i,j) = min(
         *     D_(k-1)(i,j),
         *     D_(k-1)(i,k) + D_(k-1)(k,j)
         * )
         */
        void compute() {

            int n = graph.getVertexCount();

            long startingVersion = graph.getVersion();

            graph.setStatus(ComputationStatus.NOT_COMPUTED);

            double[][] distance = graph.copyDistanceMatrix();
            int[][] next = graph.copyNextMatrix();

            try {
                for (int k = 0; k < n; k++) {

                    for (int i = 0; i < n; i++) {

                        if (Double.isInfinite(distance[i][k])) {
                            continue;
                        }

                        for (int j = 0; j < n; j++) {

                            if (Double.isInfinite(distance[k][j])) {
                                continue;
                            }

                            double candidate =
                                distance[i][k] + distance[k][j];

                            if (candidate < distance[i][j]) {
                                distance[i][j] = candidate;
                                next[i][j] = next[i][k];
                            }
                        }
                    }
                }

                for (int i = 0; i < n; i++) {
                    if (distance[i][i] < 0) {
                        throw new NegativeCycleException(
                            "Negative cycle detected at vertex " + i
                        );
                    }
                }

                if (graph.getVersion() != startingVersion) {
                    throw new GraphException(
                        "Graph changed during computation."
                    );
                }

                graph.updateMatrices(distance, next);

                computedVersion = startingVersion;

                graph.setStatus(ComputationStatus.COMPUTED);

            } catch (RuntimeException exception) {
                computedVersion = -1;

                graph.setStatus(ComputationStatus.FAILED);

                throw exception;
            }
        }

        private void validateComputedState() {
            if (graph.getStatus() != ComputationStatus.COMPUTED) {
                throw new GraphException(
                    "Shortest paths have not been computed."
                );
            }

            if (computedVersion != graph.getVersion()) {
                throw new GraphException(
                    "Shortest-path results are stale."
                );
            }
        }

        RouteResult getRoute(int source, int destination) {
            validateComputedState();

            int n = graph.getVertexCount();

            if (source < 0 || source >= n ||
                destination < 0 || destination >= n) {
                throw new GraphException("Invalid route endpoints.");
            }

            double[][] distance = graph.copyDistanceMatrix();
            int[][] next = graph.copyNextMatrix();

            double totalDistance = distance[source][destination];

            if (Double.isInfinite(totalDistance)) {
                return new RouteResult(
                    source,
                    destination,
                    totalDistance,
                    List.of()
                );
            }

            List<Integer> path = new ArrayList<>();

            int current = source;
            path.add(current);

            for (int step = 0; step < n; step++) {

                if (current == destination) {
                    return new RouteResult(
                        source,
                        destination,
                        totalDistance,
                        path
                    );
                }

                current = next[current][destination];

                if (current == -1) {
                    throw new GraphException(
                        "Invalid path reconstruction state."
                    );
                }

                path.add(current);
            }

            throw new GraphException(
                "Path reconstruction exceeded graph size."
            );
        }

        void printDistanceMatrix() {
            validateComputedState();

            double[][] distance = graph.copyDistanceMatrix();

            System.out.println("\nAll-Pairs Distance Matrix");

            for (double[] row : distance) {
                for (double value : row) {
                    String output = Double.isInfinite(value)
                        ? "INF"
                        : String.format("%.2f", value);

                    System.out.printf("%10s", output);
                }

                System.out.println();
            }
        }
    }

    static class RoutePlanningApplication {

        private final WeightedGraph graph;

        private final FloydWarshallService service;

        RoutePlanningApplication(int vertexCount) {
            graph = new WeightedGraph(vertexCount);
            service = new FloydWarshallService(graph);
        }

        void registerRoutes(List<Edge> edges) {
            for (Edge edge : edges) {
                graph.addEdge(edge);
            }
        }

        void optimizeRoutes() {
            service.compute();
        }

        void displayRoute(int source, int destination) {
            RouteResult result = service.getRoute(
                source,
                destination
            );

            if (!result.reachable()) {
                System.out.println(
                    source + " -> " + destination + ": Unreachable"
                );

                return;
            }

            String path = result.path().stream()
                .map(String::valueOf)
                .collect(Collectors.joining(" -> "));

            System.out.println(
                source + " -> " + destination +
                " | Distance: " + result.distance() +
                " | Path: " + path
            );
        }

        void displayMatrix() {
            service.printDistanceMatrix();
        }
    }

    public static void main(String[] args) {

        System.out.println("FLOYD-WARSHALL ALGORITHM");
        System.out.println("========================");

        RoutePlanningApplication application =
            new RoutePlanningApplication(5);

        List<Edge> routes = List.of(
            new Edge(0, 1, 3),
            new Edge(0, 2, 8),
            new Edge(0, 4, -4),
            new Edge(1, 3, 1),
            new Edge(1, 4, 7),
            new Edge(2, 1, 4),
            new Edge(3, 0, 2),
            new Edge(3, 2, -5),
            new Edge(4, 3, 6)
        );

        application.registerRoutes(routes);
        application.optimizeRoutes();

        application.displayMatrix();

        System.out.println("\nEnterprise Route Queries");

        application.displayRoute(0, 2);
        application.displayRoute(0, 3);
        application.displayRoute(1, 2);
        application.displayRoute(2, 4);

        System.out.println("\nEdge Case Validation");

        // A separate graph with disconnected vertices.
        WeightedGraph disconnected = new WeightedGraph(3);

        disconnected.addEdge(new Edge(0, 1, 5));

        FloydWarshallService disconnectedService =
            new FloydWarshallService(disconnected);

        disconnectedService.compute();

        RouteResult unreachable =
            disconnectedService.getRoute(0, 2);

        if (unreachable.reachable()) {
            throw new AssertionError(
                "Disconnected route should be unreachable."
            );
        }

        System.out.println("Disconnected route validated.");

        // Negative cycle handling.
        WeightedGraph cyclic = new WeightedGraph(3);

        cyclic.addEdge(new Edge(0, 1, 1));
        cyclic.addEdge(new Edge(1, 2, -3));
        cyclic.addEdge(new Edge(2, 0, 1));

        FloydWarshallService cyclicService =
            new FloydWarshallService(cyclic);

        try {
            cyclicService.compute();

            throw new AssertionError(
                "Negative cycle was not detected."
            );

        } catch (NegativeCycleException exception) {
            System.out.println(exception.getMessage());
        }

        // A graph update invalidates computed results.
        application.registerRoutes(
            List.of(new Edge(0, 3, 2))
        );

        try {
            application.displayRoute(0, 3);

            throw new AssertionError(
                "Stale result was not rejected."
            );

        } catch (GraphException exception) {
            System.out.println(
                "Stale result correctly rejected: " +
                exception.getMessage()
            );
        }
    }
}
