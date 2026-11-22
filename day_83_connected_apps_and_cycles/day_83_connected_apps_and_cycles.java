import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Queue;
import java.util.Set;

/**
 * Connected Components and Cycles in Graphs.
 *
 * Enterprise-oriented graph analysis with:
 * - Explicit graph domain types.
 * - Connected component discovery.
 * - Undirected cycle detection using Union-Find.
 * - Directed cycle detection using DFS coloring.
 * - Directed cycle detection using Kahn's algorithm.
 * - Immutable analysis results.
 * - Validation and service-layer separation.
 *
 * Compile:
 * javac ConnectedComponentsCycles.java
 *
 * Run:
 * java ConnectedComponentsCycles
 */
public class ConnectedComponentsCycles {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    enum VertexColor {
        WHITE,
        GRAY,
        BLACK
    }

    static final class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    record Edge(int source, int destination) {}

    record CycleResult(
        boolean hasCycle,
        List<Integer> cycle
    ) {
        CycleResult {
            cycle = List.copyOf(cycle);
        }

        static CycleResult noCycle() {
            return new CycleResult(false, List.of());
        }
    }

    record ComponentReport(
        List<List<Integer>> components,
        int componentCount
    ) {
        ComponentReport {
            List<List<Integer>> copy = new ArrayList<>();

            for (List<Integer> component : components) {
                copy.add(List.copyOf(component));
            }

            components = List.copyOf(copy);

            if (componentCount != components.size()) {
                throw new IllegalArgumentException(
                    "Component count does not match component data."
                );
            }
        }
    }

    static final class Graph {
        private final GraphType type;

        private final Map<Integer, List<Integer>> adjacency =
            new LinkedHashMap<>();

        Graph(GraphType type) {
            this.type = Objects.requireNonNull(
                type,
                "Graph type is required."
            );
        }

        GraphType getType() {
            return type;
        }

        void addVertex(int vertex) {
            adjacency.computeIfAbsent(
                vertex,
                ignored -> new ArrayList<>()
            );
        }

        void addEdge(int source, int destination) {
            addVertex(source);
            addVertex(destination);

            adjacency.get(source).add(destination);

            if (
                type == GraphType.UNDIRECTED &&
                source != destination
            ) {
                adjacency.get(destination).add(source);
            }
        }

        List<Integer> vertices() {
            return List.copyOf(adjacency.keySet());
        }

        List<Integer> neighbors(int vertex) {
            List<Integer> result = adjacency.get(vertex);

            if (result == null) {
                throw new GraphException(
                    "Unknown vertex: " + vertex
                );
            }

            return Collections.unmodifiableList(result);
        }

        int size() {
            return adjacency.size();
        }

        void validate() {
            for (Map.Entry<Integer, List<Integer>> entry :
                 adjacency.entrySet()) {

                if (entry.getValue() == null) {
                    throw new GraphException(
                        "Null adjacency list."
                    );
                }

                for (int neighbor : entry.getValue()) {
                    if (!adjacency.containsKey(neighbor)) {
                        throw new GraphException(
                            "Unknown neighboring vertex: " + neighbor
                        );
                    }
                }
            }
        }
    }

    static final class DisjointSet {
        private final Map<Integer, Integer> parent =
            new HashMap<>();

        private final Map<Integer, Integer> rank =
            new HashMap<>();

        private int components;

        DisjointSet(List<Integer> vertices) {
            components = vertices.size();

            for (int vertex : vertices) {
                parent.put(vertex, vertex);
                rank.put(vertex, 0);
            }
        }

        int find(int vertex) {
            Integer p = parent.get(vertex);

            if (p == null) {
                throw new GraphException(
                    "Unknown DSU vertex: " + vertex
                );
            }

            if (p != vertex) {
                parent.put(vertex, find(p));
            }

            return parent.get(vertex);
        }

        boolean union(int first, int second) {
            int rootA = find(first);
            int rootB = find(second);

            if (rootA == rootB) {
                return false;
            }

            int rankA = rank.get(rootA);
            int rankB = rank.get(rootB);

            if (rankA < rankB) {
                int temporary = rootA;
                rootA = rootB;
                rootB = temporary;
            }

            parent.put(rootB, rootA);

            if (rankA == rankB) {
                rank.put(rootA, rank.get(rootA) + 1);
            }

            components--;

            return true;
        }

        int componentCount() {
            return components;
        }
    }

    static final class GraphValidationService {

        void requireType(Graph graph, GraphType expected) {
            Objects.requireNonNull(graph, "Graph is required.");

            if (graph.getType() != expected) {
                throw new GraphException(
                    "Expected graph type: " + expected
                );
            }

            graph.validate();
        }
    }

    static final class GraphAnalysisService {
        private final GraphValidationService validator;

        GraphAnalysisService(GraphValidationService validator) {
            this.validator = Objects.requireNonNull(validator);
        }

        ComponentReport connectedComponents(Graph graph) {
            validator.requireType(graph, GraphType.UNDIRECTED);

            Set<Integer> visited = new HashSet<>();
            List<List<Integer>> components = new ArrayList<>();

            for (int start : graph.vertices()) {
                if (visited.contains(start)) {
                    continue;
                }

                List<Integer> component = new ArrayList<>();
                ArrayDeque<Integer> stack = new ArrayDeque<>();

                visited.add(start);
                stack.push(start);

                while (!stack.isEmpty()) {
                    int vertex = stack.pop();
                    component.add(vertex);

                    for (int neighbor : graph.neighbors(vertex)) {
                        if (visited.add(neighbor)) {
                            stack.push(neighbor);
                        }
                    }
                }

                component.sort(Integer::compareTo);
                components.add(component);
            }

            return new ComponentReport(
                components,
                components.size()
            );
        }

        CycleResult undirectedCycleDSU(Graph graph) {
            validator.requireType(graph, GraphType.UNDIRECTED);

            DisjointSet dsu = new DisjointSet(graph.vertices());

            for (int source : graph.vertices()) {
                for (int destination : graph.neighbors(source)) {
                    if (source <= destination) {
                        if (!dsu.union(source, destination)) {
                            return new CycleResult(
                                true,
                                List.of()
                            );
                        }
                    }
                }
            }

            return CycleResult.noCycle();
        }

        CycleResult directedCycleDFS(Graph graph) {
            validator.requireType(graph, GraphType.DIRECTED);

            Map<Integer, VertexColor> colors =
                new HashMap<>();

            Map<Integer, Integer> parent =
                new HashMap<>();

            for (int vertex : graph.vertices()) {
                colors.put(vertex, VertexColor.WHITE);
            }

            for (int start : graph.vertices()) {
                if (colors.get(start) != VertexColor.WHITE) {
                    continue;
                }

                colors.put(start, VertexColor.GRAY);
                parent.put(start, null);

                class Frame {
                    final int vertex;
                    int index;

                    Frame(int vertex) {
                        this.vertex = vertex;
                        this.index = 0;
                    }
                }

                ArrayDeque<Frame> stack = new ArrayDeque<>();
                stack.push(new Frame(start));

                while (!stack.isEmpty()) {
                    Frame frame = stack.peek();

                    List<Integer> neighbors =
                        graph.neighbors(frame.vertex);

                    if (frame.index >= neighbors.size()) {
                        colors.put(
                            frame.vertex,
                            VertexColor.BLACK
                        );

                        stack.pop();
                        continue;
                    }

                    int neighbor = neighbors.get(frame.index++);

                    VertexColor color = colors.get(neighbor);

                    if (color == VertexColor.WHITE) {
                        parent.put(neighbor, frame.vertex);

                        colors.put(
                            neighbor,
                            VertexColor.GRAY
                        );

                        stack.push(new Frame(neighbor));

                    } else if (color == VertexColor.GRAY) {
                        List<Integer> cycle = new ArrayList<>();

                        cycle.add(neighbor);

                        int current = frame.vertex;

                        while (current != neighbor) {
                            cycle.add(current);
                            current = parent.get(current);
                        }

                        cycle.add(neighbor);
                        Collections.reverse(cycle);

                        return new CycleResult(true, cycle);
                    }
                }
            }

            return CycleResult.noCycle();
        }

        CycleResult directedCycleKahn(Graph graph) {
            validator.requireType(graph, GraphType.DIRECTED);

            Map<Integer, Integer> indegree = new HashMap<>();

            for (int vertex : graph.vertices()) {
                indegree.put(vertex, 0);
            }

            for (int vertex : graph.vertices()) {
                for (int neighbor : graph.neighbors(vertex)) {
                    indegree.put(
                        neighbor,
                        indegree.get(neighbor) + 1
                    );
                }
            }

            Queue<Integer> queue = new ArrayDeque<>();

            for (Map.Entry<Integer, Integer> entry :
                 indegree.entrySet()) {

                if (entry.getValue() == 0) {
                    queue.add(entry.getKey());
                }
            }

            int processed = 0;

            while (!queue.isEmpty()) {
                int vertex = queue.remove();
                processed++;

                for (int neighbor : graph.neighbors(vertex)) {
                    int degree = indegree.get(neighbor) - 1;

                    indegree.put(neighbor, degree);

                    if (degree == 0) {
                        queue.add(neighbor);
                    }
                }
            }

            return new CycleResult(
                processed != graph.size(),
                List.of()
            );
        }
    }

    static final class GraphReportService {
        private final GraphAnalysisService analysisService;

        GraphReportService(GraphAnalysisService analysisService) {
            this.analysisService = analysisService;
        }

        void printUndirectedReport(Graph graph) {
            ComponentReport report =
                analysisService.connectedComponents(graph);

            System.out.println("Connected components:");

            for (int i = 0; i < report.components().size(); i++) {
                System.out.println(
                    "Component " + (i + 1) + ": " +
                    report.components().get(i)
                );
            }

            System.out.println(
                "Component count: " + report.componentCount()
            );

            CycleResult cycle =
                analysisService.undirectedCycleDSU(graph);

            System.out.println(
                "Undirected cycle: " + cycle.hasCycle()
            );
        }

        void printDirectedReport(Graph graph) {
            CycleResult dfs =
                analysisService.directedCycleDFS(graph);

            CycleResult kahn =
                analysisService.directedCycleKahn(graph);

            if (dfs.hasCycle() != kahn.hasCycle()) {
                throw new GraphException(
                    "Cycle detection methods disagree."
                );
            }

            System.out.println(
                "Directed cycle: " + dfs.hasCycle()
            );

            if (!dfs.cycle().isEmpty()) {
                System.out.println(
                    "Cycle path: " + dfs.cycle()
                );
            }
        }
    }

    private static void runTests(
        GraphAnalysisService service
    ) {
        Graph undirected = new Graph(GraphType.UNDIRECTED);

        undirected.addEdge(1, 2);
        undirected.addEdge(2, 3);
        undirected.addEdge(3, 1);
        undirected.addEdge(4, 5);
        undirected.addEdge(6, 7);
        undirected.addVertex(8);

        ComponentReport components =
            service.connectedComponents(undirected);

        if (components.componentCount() != 4) {
            throw new AssertionError(
                "Incorrect component count."
            );
        }

        if (!service.undirectedCycleDSU(undirected).hasCycle()) {
            throw new AssertionError(
                "Undirected cycle not detected."
            );
        }

        Graph forest = new Graph(GraphType.UNDIRECTED);

        forest.addEdge(1, 2);
        forest.addEdge(2, 3);
        forest.addEdge(4, 5);

        if (service.undirectedCycleDSU(forest).hasCycle()) {
            throw new AssertionError(
                "Forest incorrectly classified."
            );
        }

        Graph selfLoop = new Graph(GraphType.UNDIRECTED);
        selfLoop.addEdge(9, 9);

        if (!service.undirectedCycleDSU(selfLoop).hasCycle()) {
            throw new AssertionError(
                "Self-loop not detected."
            );
        }

        Graph directed = new Graph(GraphType.DIRECTED);

        directed.addEdge(1, 2);
        directed.addEdge(2, 3);
        directed.addEdge(3, 4);
        directed.addEdge(4, 2);
        directed.addEdge(4, 5);

        if (!service.directedCycleDFS(directed).hasCycle()) {
            throw new AssertionError(
                "Directed DFS failed."
            );
        }

        if (!service.directedCycleKahn(directed).hasCycle()) {
            throw new AssertionError(
                "Kahn algorithm failed."
            );
        }

        Graph dag = new Graph(GraphType.DIRECTED);

        dag.addEdge(1, 2);
        dag.addEdge(1, 3);
        dag.addEdge(2, 4);
        dag.addEdge(3, 4);

        if (service.directedCycleDFS(dag).hasCycle()) {
            throw new AssertionError(
                "DAG incorrectly classified."
            );
        }

        if (service.directedCycleKahn(dag).hasCycle()) {
            throw new AssertionError(
                "Kahn algorithm incorrectly classified DAG."
            );
        }

        Graph empty = new Graph(GraphType.UNDIRECTED);

        if (service.connectedComponents(empty).componentCount() != 0) {
            throw new AssertionError(
                "Empty graph must have zero components."
            );
        }

        Graph parallel = new Graph(GraphType.UNDIRECTED);

        parallel.addEdge(1, 2);
        parallel.addEdge(1, 2);

        if (!service.undirectedCycleDSU(parallel).hasCycle()) {
            throw new AssertionError(
                "Parallel edges must produce a cycle."
            );
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        GraphValidationService validator =
            new GraphValidationService();

        GraphAnalysisService analysis =
            new GraphAnalysisService(validator);

        GraphReportService reports =
            new GraphReportService(analysis);

        runTests(analysis);

        Graph undirected = new Graph(GraphType.UNDIRECTED);

        undirected.addEdge(1, 2);
        undirected.addEdge(2, 3);
        undirected.addEdge(3, 1);
        undirected.addEdge(4, 5);
        undirected.addEdge(6, 7);
        undirected.addVertex(8);

        System.out.println("\nUNDIRECTED GRAPH");

        reports.printUndirectedReport(undirected);

        Graph directed = new Graph(GraphType.DIRECTED);

        directed.addEdge(1, 2);
        directed.addEdge(2, 3);
        directed.addEdge(3, 4);
        directed.addEdge(4, 2);
        directed.addEdge(4, 5);

        System.out.println("\nDIRECTED GRAPH");

        reports.printDirectedReport(directed);
    }
}
