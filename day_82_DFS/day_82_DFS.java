import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class Main {

    enum TraversalStrategy {
        RECURSIVE,
        ITERATIVE
    }

    record Edge(int source, int destination) {}

    record TraversalResult(
        int start,
        List<Integer> order,
        Map<Integer, Integer> parents,
        Map<Integer, Integer> depths,
        long graphVersion
    ) {
        TraversalResult {
            order = List.copyOf(order);
            parents = Map.copyOf(parents);
            depths = Map.copyOf(depths);
        }
    }

    record ComponentReport(
        int componentNumber,
        List<Integer> vertices,
        int edgeCount
    ) {
        ComponentReport {
            vertices = List.copyOf(vertices);
        }

        int vertexCount() {
            return vertices.size();
        }
    }

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    /*
     * Repository-style graph service.
     *
     * TreeMap and TreeSet provide deterministic ordering.
     * The graph is undirected and does not support self-loops.
     */
    static final class Graph {
        private final Map<Integer, Set<Integer>> adjacency =
            new TreeMap<>();

        private long version = 0;

        public void addVertex(int vertex) {
            if (adjacency.putIfAbsent(vertex, new TreeSet<>()) == null) {
                version++;
            }
        }

        public void addEdge(int u, int v) {
            if (u == v) {
                throw new GraphException("Self-loops are prohibited.");
            }

            addVertex(u);
            addVertex(v);

            if (adjacency.get(u).add(v)) {
                adjacency.get(v).add(u);
                version++;
            }
        }

        public void removeEdge(int u, int v) {
            if (!adjacency.containsKey(u) || !adjacency.containsKey(v)) {
                throw new GraphException("Unknown vertex.");
            }

            if (!adjacency.get(u).remove(v)) {
                throw new GraphException("Edge does not exist.");
            }

            adjacency.get(v).remove(u);
            version++;
        }

        private void validateStart(int start) {
            if (!adjacency.containsKey(start)) {
                throw new GraphException(
                    "Starting vertex does not exist: " + start
                );
            }
        }

        public TraversalResult traverse(
            int start,
            TraversalStrategy strategy
        ) {
            Objects.requireNonNull(strategy, "Strategy is required.");

            return switch (strategy) {
                case RECURSIVE -> recursiveDFS(start);
                case ITERATIVE -> iterativeDFS(start);
            };
        }

        private TraversalResult recursiveDFS(int start) {
            validateStart(start);

            List<Integer> order = new ArrayList<>();
            Map<Integer, Integer> parents = new LinkedHashMap<>();
            Map<Integer, Integer> depths = new LinkedHashMap<>();
            Set<Integer> visited = new HashSet<>();

            parents.put(start, null);
            depths.put(start, 0);

            recursiveVisit(
                start,
                visited,
                order,
                parents,
                depths
            );

            return new TraversalResult(
                start, order, parents, depths, version
            );
        }

        private void recursiveVisit(
            int vertex,
            Set<Integer> visited,
            List<Integer> order,
            Map<Integer, Integer> parents,
            Map<Integer, Integer> depths
        ) {
            visited.add(vertex);
            order.add(vertex);

            for (int neighbor : adjacency.get(vertex)) {
                if (!visited.contains(neighbor)) {
                    parents.put(neighbor, vertex);
                    depths.put(neighbor, depths.get(vertex) + 1);

                    recursiveVisit(
                        neighbor,
                        visited,
                        order,
                        parents,
                        depths
                    );
                }
            }
        }

        private TraversalResult iterativeDFS(int start) {
            validateStart(start);

            List<Integer> order = new ArrayList<>();
            Map<Integer, Integer> parents = new LinkedHashMap<>();
            Map<Integer, Integer> depths = new LinkedHashMap<>();

            Set<Integer> visited = new HashSet<>();
            Deque<Integer> stack = new ArrayDeque<>();

            visited.add(start);
            parents.put(start, null);
            depths.put(start, 0);
            stack.push(start);

            while (!stack.isEmpty()) {
                int vertex = stack.pop();
                order.add(vertex);

                List<Integer> neighbors =
                    new ArrayList<>(adjacency.get(vertex));

                Collections.reverse(neighbors);

                for (int neighbor : neighbors) {
                    if (visited.add(neighbor)) {
                        parents.put(neighbor, vertex);
                        depths.put(
                            neighbor,
                            depths.get(vertex) + 1
                        );

                        stack.push(neighbor);
                    }
                }
            }

            return new TraversalResult(
                start, order, parents, depths, version
            );
        }

        public List<ComponentReport> analyzeComponents() {
            Set<Integer> visited = new HashSet<>();
            List<ComponentReport> reports = new ArrayList<>();

            int componentNumber = 1;

            for (int start : adjacency.keySet()) {
                if (!visited.add(start)) {
                    continue;
                }

                List<Integer> component = new ArrayList<>();
                Deque<Integer> stack = new ArrayDeque<>();

                stack.push(start);

                while (!stack.isEmpty()) {
                    int vertex = stack.pop();
                    component.add(vertex);

                    for (int neighbor : adjacency.get(vertex)) {
                        if (visited.add(neighbor)) {
                            stack.push(neighbor);
                        }
                    }
                }

                Collections.sort(component);

                int degreeSum = 0;

                for (int vertex : component) {
                    degreeSum += adjacency.get(vertex).size();
                }

                // Each undirected edge contributes two to degree sum.
                int edgeCount = degreeSum / 2;

                reports.add(new ComponentReport(
                    componentNumber++,
                    component,
                    edgeCount
                ));
            }

            return List.copyOf(reports);
        }

        public List<Integer> reconstructPath(
            TraversalResult result,
            int destination
        ) {
            if (!result.parents().containsKey(destination)) {
                return List.of();
            }

            List<Integer> path = new ArrayList<>();
            Integer current = destination;

            while (current != null) {
                path.add(current);
                current = result.parents().get(current);
            }

            Collections.reverse(path);
            return List.copyOf(path);
        }

        public boolean hasCycle() {
            Set<Integer> visited = new HashSet<>();

            for (int vertex : adjacency.keySet()) {
                if (!visited.contains(vertex)) {
                    if (cycleVisit(vertex, null, visited)) {
                        return true;
                    }
                }
            }

            return false;
        }

        private boolean cycleVisit(
            int vertex,
            Integer parent,
            Set<Integer> visited
        ) {
            visited.add(vertex);

            for (int neighbor : adjacency.get(vertex)) {
                if (!visited.contains(neighbor)) {
                    if (cycleVisit(neighbor, vertex, visited)) {
                        return true;
                    }
                } else if (!Objects.equals(neighbor, parent)) {
                    return true;
                }
            }

            return false;
        }

        public long getVersion() {
            return version;
        }

        public void printGraph() {
            System.out.println("\nGraph adjacency list:");

            adjacency.forEach((vertex, neighbors) ->
                System.out.println(vertex + " -> " + neighbors)
            );
        }
    }

    /*
     * Enterprise analysis service.
     *
     * Validates traversal results before using them for reports.
     */
    static final class GraphAnalysisService {

        public void verifyTraversal(
            Graph graph,
            TraversalResult result
        ) {
            if (result.graphVersion() != graph.getVersion()) {
                throw new GraphException(
                    "Traversal result is stale because the graph changed."
                );
            }

            if (result.order().size() != result.parents().size()) {
                throw new GraphException(
                    "Traversal metadata is inconsistent."
                );
            }

            if (new HashSet<>(result.order()).size()
                    != result.order().size()) {
                throw new GraphException(
                    "Traversal contains duplicate vertices."
                );
            }
        }

        public void printComponentReport(Graph graph) {
            System.out.println("\nConnected component report:");

            for (ComponentReport report : graph.analyzeComponents()) {
                System.out.println(
                    "Component " + report.componentNumber()
                    + " | Vertices: " + report.vertices()
                    + " | Vertex count: " + report.vertexCount()
                    + " | Edges: " + report.edgeCount()
                );
            }
        }
    }

    public static void main(String[] args) {
        try {
            Graph graph = new Graph();

            for (int vertex = 1; vertex <= 10; vertex++) {
                graph.addVertex(vertex);
            }

            List<Edge> edges = List.of(
                new Edge(1, 2),
                new Edge(1, 3),
                new Edge(2, 4),
                new Edge(2, 5),
                new Edge(3, 6),
                new Edge(3, 7),
                new Edge(5, 8),
                new Edge(6, 8),
                new Edge(9, 10)
            );

            for (Edge edge : edges) {
                graph.addEdge(edge.source(), edge.destination());
            }

            graph.printGraph();

            GraphAnalysisService service =
                new GraphAnalysisService();

            System.out.println("\nRecursive DFS:");

            TraversalResult recursive = graph.traverse(
                1,
                TraversalStrategy.RECURSIVE
            );

            System.out.println(recursive.order());

            System.out.println("\nIterative DFS:");

            TraversalResult iterative = graph.traverse(
                1,
                TraversalStrategy.ITERATIVE
            );

            System.out.println(iterative.order());

            service.verifyTraversal(graph, recursive);
            service.verifyTraversal(graph, iterative);

            if (!recursive.order().equals(iterative.order())) {
                throw new GraphException(
                    "Traversal strategies produced different orders."
                );
            }

            System.out.println("\nPath reconstruction:");

            System.out.println(graph.reconstructPath(iterative, 8));

            System.out.println("\nUnreachable destination:");

            System.out.println(graph.reconstructPath(iterative, 10));

            service.printComponentReport(graph);

            System.out.println("\nCycle detection:");
            System.out.println(graph.hasCycle());

            System.out.println("\nGraph mutation:");

            graph.removeEdge(5, 8);

            try {
                service.verifyTraversal(graph, iterative);
            } catch (GraphException exception) {
                System.out.println(
                    "Expected stale-result rejection: "
                    + exception.getMessage()
                );
            }

            service.printComponentReport(graph);

            System.out.println("\nIsolated vertex test:");

            Graph isolated = new Graph();
            isolated.addVertex(100);
            isolated.addVertex(200);
            isolated.addVertex(300);
            isolated.addEdge(100, 200);

            service.printComponentReport(isolated);

            System.out.println("\nValidation test:");

            try {
                graph.traverse(999, TraversalStrategy.ITERATIVE);
            } catch (GraphException exception) {
                System.out.println(exception.getMessage());
            }

            System.out.println("\nAll checks completed.");

        } catch (RuntimeException exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
