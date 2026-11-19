import java.util.*;
import java.util.function.Consumer;

/*
 * Graph Representation and Enterprise Network Model
 *
 * Java 17
 *
 * Implements:
 * - Adjacency matrix
 * - Adjacency list
 * - Directed and undirected graphs
 * - Weighted connections
 * - Immutable graph snapshots
 * - BFS and DFS
 * - Graph validation
 * - Event listeners
 * - Representation analysis
 * - Enterprise dependency network
 */

public class GraphRepresentation {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    enum RepresentationType {
        MATRIX,
        LIST
    }

    record Edge(
        String source,
        String target,
        double weight
    ) {
        Edge {
            if (source == null || source.isBlank()) {
                throw new IllegalArgumentException(
                    "Source cannot be empty."
                );
            }

            if (target == null || target.isBlank()) {
                throw new IllegalArgumentException(
                    "Target cannot be empty."
                );
            }

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Weight must be finite."
                );
            }
        }
    }

    record GraphSnapshot(
        long version,
        List<String> vertices,
        List<Edge> edges
    ) {
        GraphSnapshot {
            vertices = List.copyOf(vertices);
            edges = List.copyOf(edges);
        }
    }

    record GraphStatistics(
        int vertices,
        int edges,
        long matrixCells,
        int adjacencyEntries,
        double density
    ) {}

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class Graph {

        private final GraphType type;
        private final boolean weighted;

        private final List<String> vertices = new ArrayList<>();

        private final Map<String, Integer> indices =
            new LinkedHashMap<>();

        private final List<List<Double>> matrix =
            new ArrayList<>();

        private final Map<String, Map<String, Double>> adjacency =
            new LinkedHashMap<>();

        private final List<Consumer<String>> listeners =
            new ArrayList<>();

        private long version = 0;

        Graph(GraphType type, boolean weighted) {
            this.type = Objects.requireNonNull(type);
            this.weighted = weighted;
        }

        private void validateVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex must be non-empty."
                );
            }
        }

        private void requireVertex(String vertex) {
            if (!indices.containsKey(vertex)) {
                throw new GraphException(
                    "Unknown vertex: " + vertex
                );
            }
        }

        private void validateWeight(double weight) {
            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Weight must be finite."
                );
            }

            if (!weighted && weight != 1.0) {
                throw new IllegalArgumentException(
                    "Unweighted graph requires weight 1."
                );
            }
        }

        private void publish(String event) {
            version++;

            for (Consumer<String> listener :
                 List.copyOf(listeners)) {
                listener.accept(event);
            }
        }

        public void addListener(Consumer<String> listener) {
            listeners.add(
                Objects.requireNonNull(listener)
            );
        }

        public boolean addVertex(String vertex) {
            validateVertex(vertex);

            if (indices.containsKey(vertex)) {
                return false;
            }

            indices.put(vertex, vertices.size());
            vertices.add(vertex);

            for (List<Double> row : matrix) {
                row.add(null);
            }

            matrix.add(
                new ArrayList<>(
                    Collections.nCopies(vertices.size(), null)
                )
            );

            adjacency.put(vertex, new LinkedHashMap<>());

            publish("VERTEX_ADDED:" + vertex);

            return true;
        }

        public void addEdge(
            String source,
            String target,
            double weight
        ) {
            requireVertex(source);
            requireVertex(target);
            validateWeight(weight);

            int i = indices.get(source);
            int j = indices.get(target);

            matrix.get(i).set(j, weight);
            adjacency.get(source).put(target, weight);

            if (type == GraphType.UNDIRECTED) {
                matrix.get(j).set(i, weight);
                adjacency.get(target).put(source, weight);
            }

            publish("EDGE_ADDED:" + source + "->" + target);
        }

        public boolean removeEdge(
            String source,
            String target
        ) {
            requireVertex(source);
            requireVertex(target);

            int i = indices.get(source);
            int j = indices.get(target);

            boolean existed = matrix.get(i).get(j) != null;

            matrix.get(i).set(j, null);
            adjacency.get(source).remove(target);

            if (type == GraphType.UNDIRECTED) {
                matrix.get(j).set(i, null);
                adjacency.get(target).remove(source);
            }

            if (existed) {
                publish("EDGE_REMOVED:" + source + "->" + target);
            }

            return existed;
        }

        public void removeVertex(String vertex) {
            requireVertex(vertex);

            int position = indices.get(vertex);

            vertices.remove(position);
            matrix.remove(position);

            for (List<Double> row : matrix) {
                row.remove(position);
            }

            adjacency.remove(vertex);

            for (Map<String, Double> neighbors :
                 adjacency.values()) {
                neighbors.remove(vertex);
            }

            indices.clear();

            for (int i = 0; i < vertices.size(); i++) {
                indices.put(vertices.get(i), i);
            }

            publish("VERTEX_REMOVED:" + vertex);
        }

        public boolean hasEdge(
            String source,
            String target
        ) {
            requireVertex(source);
            requireVertex(target);

            return matrix.get(indices.get(source))
                .get(indices.get(target)) != null;
        }

        public OptionalDouble getWeight(
            String source,
            String target
        ) {
            requireVertex(source);
            requireVertex(target);

            Double value = matrix.get(indices.get(source))
                .get(indices.get(target));

            return value == null
                ? OptionalDouble.empty()
                : OptionalDouble.of(value);
        }

        public List<String> neighbors(String vertex) {
            requireVertex(vertex);

            return List.copyOf(
                adjacency.get(vertex).keySet()
            );
        }

        public int outDegree(String vertex) {
            requireVertex(vertex);
            return adjacency.get(vertex).size();
        }

        public int inDegree(String vertex) {
            requireVertex(vertex);

            int count = 0;

            for (Map<String, Double> neighbors :
                 adjacency.values()) {
                if (neighbors.containsKey(vertex)) {
                    count++;
                }
            }

            return count;
        }

        public int degree(String vertex) {
            requireVertex(vertex);

            if (type == GraphType.UNDIRECTED) {
                return outDegree(vertex);
            }

            return inDegree(vertex) + outDegree(vertex);
        }

        public int edgeCount() {
            int count = 0;
            int selfLoops = 0;

            for (Map.Entry<String, Map<String, Double>> entry :
                 adjacency.entrySet()) {

                count += entry.getValue().size();

                if (entry.getValue().containsKey(entry.getKey())) {
                    selfLoops++;
                }
            }

            return type == GraphType.DIRECTED
                ? count
                : (count + selfLoops) / 2;
        }

        public List<String> bfs(String start) {
            requireVertex(start);

            Set<String> visited = new LinkedHashSet<>();
            Queue<String> queue = new ArrayDeque<>();
            List<String> result = new ArrayList<>();

            visited.add(start);
            queue.add(start);

            while (!queue.isEmpty()) {
                String current = queue.remove();

                result.add(current);

                for (String neighbor : neighbors(current)) {
                    if (visited.add(neighbor)) {
                        queue.add(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        public List<String> dfs(String start) {
            requireVertex(start);

            Set<String> visited = new HashSet<>();
            Deque<String> stack = new ArrayDeque<>();
            List<String> result = new ArrayList<>();

            stack.push(start);

            while (!stack.isEmpty()) {
                String current = stack.pop();

                if (!visited.add(current)) {
                    continue;
                }

                result.add(current);

                List<String> adjacent =
                    new ArrayList<>(neighbors(current));

                Collections.reverse(adjacent);

                for (String neighbor : adjacent) {
                    if (!visited.contains(neighbor)) {
                        stack.push(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        public GraphSnapshot snapshot() {
            List<Edge> edges = new ArrayList<>();

            for (String source : vertices) {
                for (Map.Entry<String, Double> entry :
                     adjacency.get(source).entrySet()) {

                    String target = entry.getKey();

                    if (type == GraphType.UNDIRECTED &&
                        source.compareTo(target) > 0) {
                        continue;
                    }

                    edges.add(
                        new Edge(
                            source,
                            target,
                            entry.getValue()
                        )
                    );
                }
            }

            return new GraphSnapshot(
                version,
                vertices,
                edges
            );
        }

        public GraphStatistics statistics() {
            int v = vertices.size();
            int e = edgeCount();

            int entries = adjacency.values()
                .stream()
                .mapToInt(Map::size)
                .sum();

            double possible = type == GraphType.DIRECTED
                ? (double) v * (v - 1)
                : (double) v * (v - 1) / 2.0;

            double density = possible == 0
                ? 0.0
                : e / possible;

            return new GraphStatistics(
                v,
                e,
                (long) v * v,
                entries,
                density
            );
        }

        public void displayMatrix() {
            System.out.println("\nADJACENCY MATRIX");

            System.out.printf("%8s", "");

            for (String vertex : vertices) {
                System.out.printf("%8s", vertex);
            }

            System.out.println();

            for (int i = 0; i < vertices.size(); i++) {
                System.out.printf("%8s", vertices.get(i));

                for (Double value : matrix.get(i)) {
                    System.out.printf(
                        "%8s",
                        value == null ? "-" : value
                    );
                }

                System.out.println();
            }
        }

        public void displayList() {
            System.out.println("\nADJACENCY LIST");

            for (String vertex : vertices) {
                System.out.println(
                    vertex + " -> " + adjacency.get(vertex)
                );
            }
        }
    }

    static class GraphAnalysisService {

        public static void compare(Graph graph) {
            GraphStatistics stats = graph.statistics();

            System.out.println("\nGRAPH STATISTICS");
            System.out.println(stats);

            System.out.println("\nCOMPLEXITY COMPARISON");

            System.out.printf(
                "%-25s %-20s %s%n",
                "Operation",
                "Matrix",
                "List"
            );

            System.out.printf(
                "%-25s %-20s %s%n",
                "Space",
                "O(V^2)",
                "O(V + E)"
            );

            System.out.printf(
                "%-25s %-20s %s%n",
                "Edge lookup",
                "O(1)",
                "O(degree)"
            );

            System.out.printf(
                "%-25s %-20s %s%n",
                "Neighbor iteration",
                "O(V)",
                "O(degree)"
            );

            System.out.printf(
                "%-25s %-20s %s%n",
                "BFS / DFS",
                "O(V^2)",
                "O(V + E)"
            );
        }
    }

    static class EnterpriseDependencyService {

        private final Graph dependencies;

        EnterpriseDependencyService() {
            dependencies = new Graph(
                GraphType.DIRECTED,
                true
            );
        }

        public Graph graph() {
            return dependencies;
        }

        public boolean canReach(
            String service,
            String dependency
        ) {
            return dependencies.bfs(service)
                .contains(dependency);
        }

        public List<String> dependencyPath(String service) {
            return dependencies.bfs(service);
        }
    }

    private static void runTests() {
        Graph graph = new Graph(
            GraphType.UNDIRECTED,
            false
        );

        graph.addVertex("A");
        graph.addVertex("B");
        graph.addVertex("C");

        graph.addEdge("A", "B", 1);

        if (!graph.hasEdge("B", "A")) {
            throw new AssertionError(
                "Undirected symmetry failed."
            );
        }

        if (graph.edgeCount() != 1) {
            throw new AssertionError(
                "Edge counting failed."
            );
        }

        graph.removeEdge("A", "B");

        if (graph.hasEdge("A", "B")) {
            throw new AssertionError(
                "Edge removal failed."
            );
        }

        Graph directed = new Graph(
            GraphType.DIRECTED,
            false
        );

        directed.addVertex("X");
        directed.addVertex("Y");
        directed.addEdge("X", "Y", 1);

        if (directed.inDegree("Y") != 1 ||
            directed.outDegree("X") != 1 ||
            directed.hasEdge("Y", "X")) {
            throw new AssertionError(
                "Directed graph validation failed."
            );
        }

        directed.removeVertex("Y");

        if (directed.snapshot().vertices().size() != 1) {
            throw new AssertionError(
                "Vertex removal failed."
            );
        }

        System.out.println("All tests passed.");
    }

    private static Graph buildSampleGraph() {
        Graph graph = new Graph(
            GraphType.UNDIRECTED,
            true
        );

        for (String vertex :
             List.of("A", "B", "C", "D", "E", "F")) {
            graph.addVertex(vertex);
        }

        List<Edge> edges = List.of(
            new Edge("A", "B", 4),
            new Edge("A", "C", 2),
            new Edge("B", "C", 1),
            new Edge("B", "D", 5),
            new Edge("C", "D", 8),
            new Edge("C", "E", 10),
            new Edge("D", "E", 2),
            new Edge("D", "F", 6),
            new Edge("E", "F", 3)
        );

        edges.forEach(edge ->
            graph.addEdge(
                edge.source(),
                edge.target(),
                edge.weight()
            )
        );

        return graph;
    }

    public static void main(String[] args) {
        runTests();

        Graph graph = buildSampleGraph();

        graph.addListener(event ->
            System.out.println("EVENT: " + event)
        );

        graph.displayMatrix();
        graph.displayList();

        System.out.println("\nGRAPH TRAVERSALS");

        System.out.println("BFS: " + graph.bfs("A"));
        System.out.println("DFS: " + graph.dfs("A"));

        System.out.println("\nDEGREES");

        for (String vertex :
             graph.snapshot().vertices()) {
            System.out.println(
                vertex + ": " + graph.degree(vertex)
            );
        }

        GraphAnalysisService.compare(graph);

        System.out.println("\nENTERPRISE DEPENDENCY MODEL");

        EnterpriseDependencyService service =
            new EnterpriseDependencyService();

        Graph dependencyGraph = service.graph();

        for (String name :
             List.of(
                 "API",
                 "AUTH",
                 "DATABASE",
                 "CACHE",
                 "MESSAGE_QUEUE"
             )) {
            dependencyGraph.addVertex(name);
        }

        dependencyGraph.addEdge("API", "AUTH", 1);
        dependencyGraph.addEdge("API", "CACHE", 1);
        dependencyGraph.addEdge("AUTH", "DATABASE", 1);
        dependencyGraph.addEdge("CACHE", "DATABASE", 1);
        dependencyGraph.addEdge("API", "MESSAGE_QUEUE", 1);

        System.out.println(
            "API can reach DATABASE: "
            + service.canReach("API", "DATABASE")
        );

        System.out.println(
            "API dependency traversal: "
            + service.dependencyPath("API")
        );

        System.out.println("\nGRAPH MUTATION");

        graph.removeEdge("C", "E");
        graph.removeVertex("F");

        System.out.println(
            "Final graph snapshot: " + graph.snapshot()
        );
    }
}
