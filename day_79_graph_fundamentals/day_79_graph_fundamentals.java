import java.util.*;

/*
 * Graph Fundamentals: Enterprise Network Modeling.
 *
 * Java 17 implementation covering:
 * - Vertices and edges
 * - Directed and undirected graphs
 * - Weighted and unweighted graphs
 * - Degree calculations
 * - Adjacency lists
 * - BFS and DFS
 * - Connected components
 * - Cycle detection
 * - Dijkstra shortest paths
 * - Immutable result records
 * - Graph integrity and state validation
 */

public class GraphFundamentals {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    record Edge(
        String source,
        String target,
        double weight
    ) {
        Edge {
            if (source == null || source.isBlank()) {
                throw new IllegalArgumentException(
                    "Source vertex is required."
                );
            }

            if (target == null || target.isBlank()) {
                throw new IllegalArgumentException(
                    "Target vertex is required."
                );
            }

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Edge weight must be finite."
                );
            }
        }
    }

    record DegreeInformation(
        int degree,
        int inDegree,
        int outDegree
    ) {}

    record GraphStatistics(
        int vertices,
        int edges,
        double averageDegree,
        int isolatedVertices,
        boolean containsCycle
    ) {}

    record PathResult(
        String source,
        Map<String, Double> distances
    ) {
        PathResult {
            distances = Collections.unmodifiableMap(
                new LinkedHashMap<>(distances)
            );
        }
    }

    static final class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static final class VertexNotFoundException
        extends GraphException {

        VertexNotFoundException(String vertex) {
            super("Unknown vertex: " + vertex);
        }
    }

    static final class Graph {

        private final GraphType type;
        private final boolean weighted;

        private final Map<String, Map<String, Double>> adjacency =
            new LinkedHashMap<>();

        private int edgeCount;

        Graph(GraphType type, boolean weighted) {
            this.type = Objects.requireNonNull(type);
            this.weighted = weighted;
        }

        int vertexCount() {
            return adjacency.size();
        }

        int edgeCount() {
            return edgeCount;
        }

        GraphType type() {
            return type;
        }

        boolean weighted() {
            return weighted;
        }

        private void validateVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex identifier cannot be blank."
                );
            }
        }

        private void requireVertex(String vertex) {
            if (!adjacency.containsKey(vertex)) {
                throw new VertexNotFoundException(vertex);
            }
        }

        void addVertex(String vertex) {
            validateVertex(vertex);

            adjacency.putIfAbsent(vertex, new LinkedHashMap<>());
        }

        void addEdge(Edge edge) {
            Objects.requireNonNull(edge);

            if (!weighted && edge.weight() != 1.0) {
                throw new GraphException(
                    "Unweighted graph requires weight 1."
                );
            }

            addVertex(edge.source());
            addVertex(edge.target());

            boolean exists = adjacency
                .get(edge.source())
                .containsKey(edge.target());

            adjacency
                .get(edge.source())
                .put(edge.target(), edge.weight());

            if (type == GraphType.UNDIRECTED) {
                adjacency
                    .get(edge.target())
                    .put(edge.source(), edge.weight());
            }

            if (!exists) {
                edgeCount++;
            }

            validateIntegrity();
        }

        void removeEdge(String source, String target) {
            requireVertex(source);
            requireVertex(target);

            if (!adjacency.get(source).containsKey(target)) {
                throw new GraphException("Edge does not exist.");
            }

            adjacency.get(source).remove(target);

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(target).remove(source);
            }

            edgeCount--;
            validateIntegrity();
        }

        void removeVertex(String vertex) {
            requireVertex(vertex);

            if (type == GraphType.DIRECTED) {
                int outgoing = adjacency.get(vertex).size();
                int incoming = 0;

                for (Map<String, Double> neighbors :
                     adjacency.values()) {

                    if (neighbors.remove(vertex) != null) {
                        incoming++;
                    }
                }

                edgeCount -= outgoing + incoming;

            } else {
                edgeCount -= adjacency.get(vertex).size();

                for (Map<String, Double> neighbors :
                     adjacency.values()) {

                    neighbors.remove(vertex);
                }
            }

            adjacency.remove(vertex);
            validateIntegrity();
        }

        List<String> vertices() {
            return List.copyOf(adjacency.keySet());
        }

        Map<String, Double> neighbors(String vertex) {
            requireVertex(vertex);

            return Collections.unmodifiableMap(
                new LinkedHashMap<>(adjacency.get(vertex))
            );
        }

        int degree(String vertex) {
            requireVertex(vertex);

            if (type == GraphType.DIRECTED) {
                throw new GraphException(
                    "Use inDegree and outDegree for directed graphs."
                );
            }

            return adjacency.get(vertex).size();
        }

        int inDegree(String vertex) {
            requireVertex(vertex);

            if (type != GraphType.DIRECTED) {
                throw new GraphException(
                    "In-degree requires a directed graph."
                );
            }

            int count = 0;

            for (Map<String, Double> neighbors :
                 adjacency.values()) {

                if (neighbors.containsKey(vertex)) {
                    count++;
                }
            }

            return count;
        }

        int outDegree(String vertex) {
            requireVertex(vertex);

            if (type != GraphType.DIRECTED) {
                throw new GraphException(
                    "Out-degree requires a directed graph."
                );
            }

            return adjacency.get(vertex).size();
        }

        DegreeInformation degreeInformation(String vertex) {
            if (type == GraphType.DIRECTED) {
                return new DegreeInformation(
                    -1,
                    inDegree(vertex),
                    outDegree(vertex)
                );
            }

            return new DegreeInformation(
                degree(vertex),
                -1,
                -1
            );
        }

        List<String> bfs(String start) {
            requireVertex(start);

            Set<String> visited = new LinkedHashSet<>();
            Queue<String> queue = new ArrayDeque<>();
            List<String> result = new ArrayList<>();

            visited.add(start);
            queue.offer(start);

            while (!queue.isEmpty()) {
                String current = queue.poll();
                result.add(current);

                for (String neighbor :
                     adjacency.get(current).keySet()) {

                    if (visited.add(neighbor)) {
                        queue.offer(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        List<String> dfs(String start) {
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

                List<String> neighbors = new ArrayList<>(
                    adjacency.get(current).keySet()
                );

                Collections.reverse(neighbors);

                for (String neighbor : neighbors) {
                    if (!visited.contains(neighbor)) {
                        stack.push(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        List<List<String>> connectedComponents() {
            if (type != GraphType.UNDIRECTED) {
                throw new GraphException(
                    "Connected components require undirected graph."
                );
            }

            Set<String> visited = new HashSet<>();
            List<List<String>> components = new ArrayList<>();

            for (String vertex : adjacency.keySet()) {
                if (!visited.contains(vertex)) {
                    List<String> component = bfs(vertex);

                    visited.addAll(component);
                    components.add(component);
                }
            }

            return components.stream()
                .map(List::copyOf)
                .toList();
        }

        boolean hasCycle() {
            if (type == GraphType.UNDIRECTED) {
                Set<String> visited = new HashSet<>();

                for (String vertex : adjacency.keySet()) {
                    if (
                        !visited.contains(vertex) &&
                        undirectedCycle(vertex, null, visited)
                    ) {
                        return true;
                    }
                }

                return false;
            }

            Map<String, Integer> colors = new HashMap<>();

            for (String vertex : adjacency.keySet()) {
                colors.put(vertex, 0);
            }

            for (String vertex : adjacency.keySet()) {
                if (
                    colors.get(vertex) == 0 &&
                    directedCycle(vertex, colors)
                ) {
                    return true;
                }
            }

            return false;
        }

        private boolean undirectedCycle(
            String vertex,
            String parent,
            Set<String> visited
        ) {
            visited.add(vertex);

            for (String neighbor :
                 adjacency.get(vertex).keySet()) {

                if (!visited.contains(neighbor)) {
                    if (
                        undirectedCycle(
                            neighbor,
                            vertex,
                            visited
                        )
                    ) {
                        return true;
                    }
                } else if (!neighbor.equals(parent)) {
                    return true;
                }
            }

            return false;
        }

        private boolean directedCycle(
            String vertex,
            Map<String, Integer> colors
        ) {
            colors.put(vertex, 1);

            for (String neighbor :
                 adjacency.get(vertex).keySet()) {

                if (colors.get(neighbor) == 1) {
                    return true;
                }

                if (
                    colors.get(neighbor) == 0 &&
                    directedCycle(neighbor, colors)
                ) {
                    return true;
                }
            }

            colors.put(vertex, 2);
            return false;
        }

        PathResult dijkstra(String start) {
            requireVertex(start);

            for (Map<String, Double> neighbors :
                 adjacency.values()) {

                for (double weight : neighbors.values()) {
                    if (weight < 0) {
                        throw new GraphException(
                            "Dijkstra requires non-negative weights."
                        );
                    }
                }
            }

            Map<String, Double> distances = new LinkedHashMap<>();

            for (String vertex : adjacency.keySet()) {
                distances.put(
                    vertex,
                    Double.POSITIVE_INFINITY
                );
            }

            distances.put(start, 0.0);

            record QueueNode(
                String vertex,
                double distance
            ) {}

            PriorityQueue<QueueNode> queue =
                new PriorityQueue<>(
                    Comparator.comparingDouble(QueueNode::distance)
                );

            queue.offer(new QueueNode(start, 0.0));

            while (!queue.isEmpty()) {
                QueueNode current = queue.poll();

                if (
                    current.distance() !=
                    distances.get(current.vertex())
                ) {
                    continue;
                }

                for (
                    Map.Entry<String, Double> edge :
                    adjacency.get(current.vertex()).entrySet()
                ) {
                    String neighbor = edge.getKey();

                    double candidate =
                        current.distance() + edge.getValue();

                    if (candidate < distances.get(neighbor)) {
                        distances.put(neighbor, candidate);

                        queue.offer(
                            new QueueNode(neighbor, candidate)
                        );
                    }
                }
            }

            return new PathResult(start, distances);
        }

        GraphStatistics statistics() {
            int isolated = 0;
            long degreeSum = 0;

            for (Map.Entry<String, Map<String, Double>> entry :
                 adjacency.entrySet()) {

                int degree = entry.getValue().size();

                if (degree == 0) {
                    isolated++;
                }

                degreeSum += degree;
            }

            double averageDegree = vertexCount() == 0
                ? 0.0
                : (double) degreeSum / vertexCount();

            return new GraphStatistics(
                vertexCount(),
                edgeCount,
                averageDegree,
                isolated,
                hasCycle()
            );
        }

        private void validateIntegrity() {
            int calculatedEdges = 0;

            for (
                Map.Entry<String, Map<String, Double>> entry :
                adjacency.entrySet()
            ) {
                String source = entry.getKey();

                for (
                    Map.Entry<String, Double> edge :
                    entry.getValue().entrySet()
                ) {
                    String target = edge.getKey();
                    double weight = edge.getValue();

                    if (!adjacency.containsKey(target)) {
                        throw new GraphException(
                            "Edge references missing vertex."
                        );
                    }

                    if (!Double.isFinite(weight)) {
                        throw new GraphException(
                            "Invalid stored edge weight."
                        );
                    }

                    if (type == GraphType.UNDIRECTED) {
                        Double reverse =
                            adjacency.get(target).get(source);

                        if (
                            reverse == null ||
                            Double.compare(reverse, weight) != 0
                        ) {
                            throw new GraphException(
                                "Undirected edge symmetry violated."
                            );
                        }

                        if (source.compareTo(target) <= 0) {
                            calculatedEdges++;
                        }
                    } else {
                        calculatedEdges++;
                    }
                }
            }

            if (calculatedEdges != edgeCount) {
                throw new GraphException(
                    "Edge count integrity violation."
                );
            }
        }
    }

    interface GraphReport {
        void generate(Graph graph);
    }

    static final class NetworkReport implements GraphReport {

        @Override
        public void generate(Graph graph) {
            System.out.println("\nNetwork Report");

            System.out.println(
                "Vertices: " + graph.vertexCount()
            );

            System.out.println(
                "Edges: " + graph.edgeCount()
            );

            System.out.println(
                "Statistics: " + graph.statistics()
            );

            for (String vertex : graph.vertices()) {
                System.out.println(
                    vertex + " -> " + graph.neighbors(vertex)
                );
            }
        }
    }

    private static void demonstrateUndirected() {
        System.out.println("\n=== UNDIRECTED GRAPH ===");

        Graph graph = new Graph(
            GraphType.UNDIRECTED,
            false
        );

        graph.addEdge(new Edge("A", "B", 1));
        graph.addEdge(new Edge("A", "C", 1));
        graph.addEdge(new Edge("B", "D", 1));
        graph.addEdge(new Edge("C", "D", 1));
        graph.addEdge(new Edge("D", "E", 1));
        graph.addVertex("F");

        System.out.println("Vertices: " + graph.vertices());
        System.out.println("Edges: " + graph.edgeCount());

        System.out.println("Degree of A: " + graph.degree("A"));
        System.out.println("Degree of D: " + graph.degree("D"));

        System.out.println("BFS: " + graph.bfs("A"));
        System.out.println("DFS: " + graph.dfs("A"));

        System.out.println(
            "Components: " + graph.connectedComponents()
        );

        System.out.println(
            "Cycle exists: " + graph.hasCycle()
        );

        new NetworkReport().generate(graph);
    }

    private static void demonstrateDirected() {
        System.out.println("\n=== DIRECTED GRAPH ===");

        Graph graph = new Graph(
            GraphType.DIRECTED,
            false
        );

        graph.addEdge(new Edge("Frontend", "API", 1));
        graph.addEdge(new Edge("API", "Database", 1));
        graph.addEdge(new Edge("API", "Cache", 1));
        graph.addEdge(new Edge("Cache", "Database", 1));

        for (String vertex : graph.vertices()) {
            System.out.println(
                vertex + " | in=" + graph.inDegree(vertex)
                + " | out=" + graph.outDegree(vertex)
            );
        }

        System.out.println(
            "Cycle exists: " + graph.hasCycle()
        );
    }

    private static void demonstrateWeighted() {
        System.out.println("\n=== WEIGHTED GRAPH ===");

        Graph graph = new Graph(
            GraphType.UNDIRECTED,
            true
        );

        graph.addEdge(new Edge("A", "B", 4));
        graph.addEdge(new Edge("A", "C", 2));
        graph.addEdge(new Edge("C", "B", 1));
        graph.addEdge(new Edge("B", "D", 5));
        graph.addEdge(new Edge("D", "E", 2));

        PathResult result = graph.dijkstra("A");

        result.distances().forEach(
            (vertex, distance) ->
                System.out.println(
                    "A -> " + vertex + ": " + distance
                )
        );
    }

    private static void runTests() {
        Graph graph = new Graph(
            GraphType.UNDIRECTED,
            false
        );

        graph.addEdge(new Edge("1", "2", 1));
        graph.addEdge(new Edge("2", "3", 1));

        if (graph.vertexCount() != 3 ||
            graph.edgeCount() != 2 ||
            graph.degree("2") != 2 ||
            graph.hasCycle()) {

            throw new AssertionError("Undirected tests failed.");
        }

        graph.addEdge(new Edge("3", "1", 1));

        if (!graph.hasCycle()) {
            throw new AssertionError("Cycle detection failed.");
        }

        Graph directed = new Graph(
            GraphType.DIRECTED,
            false
        );

        directed.addEdge(new Edge("A", "B", 1));
        directed.addEdge(new Edge("A", "C", 1));
        directed.addEdge(new Edge("C", "B", 1));

        if (directed.inDegree("B") != 2 ||
            directed.outDegree("A") != 2) {

            throw new AssertionError("Degree tests failed.");
        }

        Graph weighted = new Graph(
            GraphType.UNDIRECTED,
            true
        );

        weighted.addEdge(new Edge("A", "B", 3));
        weighted.addEdge(new Edge("B", "C", 2));

        if (weighted.dijkstra("A").distances().get("C") != 5.0) {
            throw new AssertionError("Shortest-path test failed.");
        }

        System.out.println("\nAll tests passed.");
    }

    public static void main(String[] args) {
        try {
            demonstrateUndirected();
            demonstrateDirected();
            demonstrateWeighted();
            runTests();

        } catch (GraphException | IllegalArgumentException error) {
            System.err.println(
                "Graph processing failed: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
