import java.util.*;
import java.util.function.Consumer;

/**
 * GraphAssessment.java
 *
 * Enterprise-oriented graph assessment engine.
 *
 * Java version: 17
 * Dependencies: Java standard library.
 *
 * Supports:
 * BFS, DFS, Connected Components, Cycle Detection,
 * Bipartite Graphs, Topological Sorting and Shortest Paths.
 */
public class GraphAssessment {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    enum Algorithm {
        BFS,
        DFS,
        COMPONENTS,
        CYCLE,
        BIPARTITE,
        TOPOLOGICAL
    }

    record TraversalResult(
        List<Integer> order,
        Map<Integer, Integer> parent,
        Map<Integer, Integer> distance
    ) {
        TraversalResult {
            order = List.copyOf(order);
            parent = Collections.unmodifiableMap(
                new LinkedHashMap<>(parent)
            );
            distance = Collections.unmodifiableMap(
                new LinkedHashMap<>(distance)
            );
        }
    }

    record TopologicalResult(
        List<Integer> order,
        boolean hasCycle
    ) {
        TopologicalResult {
            order = List.copyOf(order);
        }
    }

    record BipartiteResult(
        boolean bipartite,
        Map<Integer, Integer> colors
    ) {
        BipartiteResult {
            colors = Collections.unmodifiableMap(
                new LinkedHashMap<>(colors)
            );
        }
    }

    record AssessmentRecord(
        long id,
        Algorithm algorithm,
        String timestamp,
        String outcome
    ) {}

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class Graph {
        private final GraphType type;

        private final List<Integer> vertices;

        private final Map<Integer, LinkedHashSet<Integer>> adjacency;

        private final Set<String> edges = new HashSet<>();

        Graph(Collection<Integer> input, GraphType type) {
            Objects.requireNonNull(input);
            this.type = Objects.requireNonNull(type);

            if (new HashSet<>(input).size() != input.size()) {
                throw new GraphException(
                    "Duplicate vertices are not permitted."
                );
            }

            if (input.stream().anyMatch(Objects::isNull)) {
                throw new GraphException(
                    "Null vertices are not permitted."
                );
            }

            this.vertices = List.copyOf(input);

            this.adjacency = new LinkedHashMap<>();

            for (int vertex : vertices) {
                adjacency.put(vertex, new LinkedHashSet<>());
            }
        }

        private void validateVertex(int vertex) {
            if (!adjacency.containsKey(vertex)) {
                throw new GraphException(
                    "Unknown vertex: " + vertex
                );
            }
        }

        private String edgeKey(int u, int v) {
            if (type == GraphType.UNDIRECTED && u > v) {
                return v + ":" + u;
            }

            return u + ":" + v;
        }

        synchronized void addEdge(int u, int v) {
            validateVertex(u);
            validateVertex(v);

            String key = edgeKey(u, v);

            if (!edges.add(key)) {
                return;
            }

            adjacency.get(u).add(v);

            if (type == GraphType.UNDIRECTED && u != v) {
                adjacency.get(v).add(u);
            }
        }

        synchronized void removeEdge(int u, int v) {
            validateVertex(u);
            validateVertex(v);

            if (!edges.remove(edgeKey(u, v))) {
                return;
            }

            adjacency.get(u).remove(v);

            if (type == GraphType.UNDIRECTED && u != v) {
                adjacency.get(v).remove(u);
            }
        }

        private void requireUndirected() {
            if (type != GraphType.UNDIRECTED) {
                throw new GraphException(
                    "Operation requires an undirected graph."
                );
            }
        }

        private void requireDirected() {
            if (type != GraphType.DIRECTED) {
                throw new GraphException(
                    "Operation requires a directed graph."
                );
            }
        }

        TraversalResult bfs(int start) {
            validateVertex(start);

            List<Integer> order = new ArrayList<>();

            Map<Integer, Integer> parent = new LinkedHashMap<>();
            Map<Integer, Integer> distance = new LinkedHashMap<>();

            Queue<Integer> queue = new ArrayDeque<>();

            parent.put(start, null);
            distance.put(start, 0);

            queue.offer(start);

            while (!queue.isEmpty()) {
                int vertex = queue.poll();
                order.add(vertex);

                for (int neighbor : adjacency.get(vertex)) {
                    if (!parent.containsKey(neighbor)) {
                        parent.put(neighbor, vertex);

                        distance.put(
                            neighbor,
                            distance.get(vertex) + 1
                        );

                        queue.offer(neighbor);
                    }
                }
            }

            return new TraversalResult(
                order, parent, distance
            );
        }

        TraversalResult dfs(int start) {
            validateVertex(start);

            List<Integer> order = new ArrayList<>();

            Map<Integer, Integer> parent = new LinkedHashMap<>();
            Map<Integer, Integer> distance = new LinkedHashMap<>();

            Deque<Integer> stack = new ArrayDeque<>();

            parent.put(start, null);
            distance.put(start, 0);

            stack.push(start);

            while (!stack.isEmpty()) {
                int vertex = stack.pop();
                order.add(vertex);

                List<Integer> neighbors = new ArrayList<>(
                    adjacency.get(vertex)
                );

                Collections.reverse(neighbors);

                for (int neighbor : neighbors) {
                    if (!parent.containsKey(neighbor)) {
                        parent.put(neighbor, vertex);

                        distance.put(
                            neighbor,
                            distance.get(vertex) + 1
                        );

                        stack.push(neighbor);
                    }
                }
            }

            return new TraversalResult(
                order, parent, distance
            );
        }

        List<List<Integer>> connectedComponents() {
            requireUndirected();

            Set<Integer> visited = new HashSet<>();

            List<List<Integer>> components = new ArrayList<>();

            for (int start : vertices) {
                if (visited.contains(start)) {
                    continue;
                }

                List<Integer> component = new ArrayList<>();

                Queue<Integer> queue = new ArrayDeque<>();

                visited.add(start);
                queue.offer(start);

                while (!queue.isEmpty()) {
                    int vertex = queue.poll();

                    component.add(vertex);

                    for (int neighbor : adjacency.get(vertex)) {
                        if (visited.add(neighbor)) {
                            queue.offer(neighbor);
                        }
                    }
                }

                components.add(List.copyOf(component));
            }

            return List.copyOf(components);
        }

        boolean hasUndirectedCycle() {
            requireUndirected();

            Set<Integer> visited = new HashSet<>();

            for (int start : vertices) {
                if (!visited.add(start)) {
                    continue;
                }

                Deque<int[]> stack = new ArrayDeque<>();

                stack.push(new int[]{start, Integer.MIN_VALUE});

                while (!stack.isEmpty()) {
                    int[] current = stack.pop();

                    int vertex = current[0];
                    int parent = current[1];

                    for (int neighbor : adjacency.get(vertex)) {
                        if (!visited.contains(neighbor)) {
                            visited.add(neighbor);

                            stack.push(
                                new int[]{neighbor, vertex}
                            );
                        } else if (neighbor != parent) {
                            return true;
                        }
                    }
                }
            }

            return false;
        }

        boolean hasDirectedCycle() {
            requireDirected();

            Map<Integer, Integer> state = new HashMap<>();

            for (int vertex : vertices) {
                state.put(vertex, 0);
            }

            for (int start : vertices) {
                if (state.get(start) != 0) {
                    continue;
                }

                Deque<Frame> stack = new ArrayDeque<>();

                state.put(start, 1);

                stack.push(new Frame(start));

                while (!stack.isEmpty()) {
                    Frame frame = stack.peek();

                    if (!frame.iterator.hasNext()) {
                        state.put(frame.vertex, 2);
                        stack.pop();
                        continue;
                    }

                    int neighbor = frame.iterator.next();

                    if (state.get(neighbor) == 1) {
                        return true;
                    }

                    if (state.get(neighbor) == 0) {
                        state.put(neighbor, 1);
                        stack.push(new Frame(neighbor));
                    }
                }
            }

            return false;
        }

        private class Frame {
            final int vertex;
            final Iterator<Integer> iterator;

            Frame(int vertex) {
                this.vertex = vertex;
                this.iterator = adjacency.get(vertex).iterator();
            }
        }

        BipartiteResult isBipartite() {
            requireUndirected();

            Map<Integer, Integer> colors = new LinkedHashMap<>();

            for (int start : vertices) {
                if (colors.containsKey(start)) {
                    continue;
                }

                Queue<Integer> queue = new ArrayDeque<>();

                colors.put(start, 0);
                queue.offer(start);

                while (!queue.isEmpty()) {
                    int vertex = queue.poll();

                    for (int neighbor : adjacency.get(vertex)) {
                        if (!colors.containsKey(neighbor)) {
                            colors.put(
                                neighbor,
                                1 - colors.get(vertex)
                            );

                            queue.offer(neighbor);

                        } else if (
                            colors.get(neighbor).equals(
                                colors.get(vertex)
                            )
                        ) {
                            return new BipartiteResult(
                                false, colors
                            );
                        }
                    }
                }
            }

            return new BipartiteResult(true, colors);
        }

        TopologicalResult topologicalSort() {
            requireDirected();

            Map<Integer, Integer> indegree = new LinkedHashMap<>();

            for (int vertex : vertices) {
                indegree.put(vertex, 0);
            }

            for (int vertex : vertices) {
                for (int neighbor : adjacency.get(vertex)) {
                    indegree.merge(neighbor, 1, Integer::sum);
                }
            }

            Queue<Integer> queue = new ArrayDeque<>();

            for (int vertex : vertices) {
                if (indegree.get(vertex) == 0) {
                    queue.offer(vertex);
                }
            }

            List<Integer> order = new ArrayList<>();

            while (!queue.isEmpty()) {
                int vertex = queue.poll();

                order.add(vertex);

                for (int neighbor : adjacency.get(vertex)) {
                    int updated = indegree.merge(
                        neighbor, -1, Integer::sum
                    );

                    if (updated == 0) {
                        queue.offer(neighbor);
                    }
                }
            }

            return new TopologicalResult(
                order,
                order.size() != vertices.size()
            );
        }

        List<Integer> shortestPath(int start, int target) {
            validateVertex(start);
            validateVertex(target);

            TraversalResult result = bfs(start);

            if (!result.parent().containsKey(target)) {
                return List.of();
            }

            List<Integer> path = new ArrayList<>();

            Integer current = target;

            while (current != null) {
                path.add(current);
                current = result.parent().get(current);
            }

            Collections.reverse(path);

            return List.copyOf(path);
        }

        List<Integer> getVertices() {
            return vertices;
        }

        Map<Integer, Set<Integer>> adjacencySnapshot() {
            Map<Integer, Set<Integer>> snapshot =
                new LinkedHashMap<>();

            adjacency.forEach((vertex, neighbors) ->
                snapshot.put(
                    vertex,
                    Collections.unmodifiableSet(
                        new LinkedHashSet<>(neighbors)
                    )
                )
            );

            return Collections.unmodifiableMap(snapshot);
        }
    }


    /**
     * Repository-style assessment service.
     * Graph algorithms produce results; the service handles
     * execution history and event notification.
     */
    static class AssessmentService {
        private final Graph graph;

        private final List<AssessmentRecord> history =
            new ArrayList<>();

        private final List<Consumer<AssessmentRecord>> listeners =
            new ArrayList<>();

        private long sequence = 0;

        AssessmentService(Graph graph) {
            this.graph = Objects.requireNonNull(graph);
        }

        void addListener(
            Consumer<AssessmentRecord> listener
        ) {
            listeners.add(Objects.requireNonNull(listener));
        }

        private AssessmentRecord record(
            Algorithm algorithm,
            String outcome
        ) {
            AssessmentRecord record = new AssessmentRecord(
                ++sequence,
                algorithm,
                java.time.Instant.now().toString(),
                outcome
            );

            history.add(record);

            // Listener failures must not invalidate a completed
            // graph assessment.
            for (Consumer<AssessmentRecord> listener : listeners) {
                try {
                    listener.accept(record);
                } catch (RuntimeException exception) {
                    System.err.println(
                        "Assessment listener failed: "
                        + exception.getMessage()
                    );
                }
            }

            return record;
        }

        AssessmentRecord assess(
            Algorithm algorithm,
            Integer start
        ) {
            Objects.requireNonNull(algorithm);

            String outcome;

            switch (algorithm) {
                case BFS -> {
                    Objects.requireNonNull(start);
                    outcome = graph.bfs(start).order().toString();
                }

                case DFS -> {
                    Objects.requireNonNull(start);
                    outcome = graph.dfs(start).order().toString();
                }

                case COMPONENTS ->
                    outcome = graph.connectedComponents().toString();

                case CYCLE -> {
                    boolean cycle =
                        graph.type == GraphType.DIRECTED
                        ? graph.hasDirectedCycle()
                        : graph.hasUndirectedCycle();

                    outcome = Boolean.toString(cycle);
                }

                case BIPARTITE ->
                    outcome = Boolean.toString(
                        graph.isBipartite().bipartite()
                    );

                case TOPOLOGICAL -> {
                    TopologicalResult result =
                        graph.topologicalSort();

                    outcome = result.hasCycle()
                        ? "CYCLE DETECTED"
                        : result.order().toString();
                }

                default ->
                    throw new GraphException(
                        "Unsupported algorithm."
                    );
            }

            return record(algorithm, outcome);
        }

        List<AssessmentRecord> history() {
            return List.copyOf(history);
        }
    }


    private static void verify(
        boolean condition,
        String message
    ) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }


    public static void main(String[] args) {
        try {
            System.out.println("GRAPH ASSESSMENT ENGINE");
            System.out.println("=======================\n");

            Graph undirected = new Graph(
                List.of(1, 2, 3, 4, 5, 6, 7, 8),
                GraphType.UNDIRECTED
            );

            int[][] edges = {
                {1, 2}, {1, 3}, {2, 4},
                {3, 4}, {5, 6}, {7, 8}
            };

            for (int[] edge : edges) {
                undirected.addEdge(edge[0], edge[1]);
            }

            AssessmentService service =
                new AssessmentService(undirected);

            service.addListener(record ->
                System.out.println(
                    "[EVENT] " + record.algorithm()
                    + " completed. Outcome: " + record.outcome()
                )
            );

            System.out.println(
                "\nBFS: "
                + undirected.bfs(1).order()
            );

            System.out.println(
                "DFS: "
                + undirected.dfs(1).order()
            );

            System.out.println(
                "Components: "
                + undirected.connectedComponents()
            );

            System.out.println(
                "Undirected cycle: "
                + undirected.hasUndirectedCycle()
            );

            System.out.println(
                "Bipartite: "
                + undirected.isBipartite().bipartite()
            );

            System.out.println(
                "Shortest path: "
                + undirected.shortestPath(1, 4)
            );

            service.assess(Algorithm.BFS, 1);
            service.assess(Algorithm.COMPONENTS, null);
            service.assess(Algorithm.BIPARTITE, null);

            // Odd cycle.
            undirected.addEdge(4, 1);

            System.out.println(
                "\nAfter adding edge 4 -> 1:"
            );

            System.out.println(
                "Cycle: "
                + undirected.hasUndirectedCycle()
            );

            System.out.println(
                "Bipartite: "
                + undirected.isBipartite().bipartite()
            );

            // Directed dependency graph.
            System.out.println("\nDIRECTED DEPENDENCY GRAPH");

            Graph directed = new Graph(
                List.of(1, 2, 3, 4, 5, 6),
                GraphType.DIRECTED
            );

            int[][] dependencies = {
                {1, 3}, {2, 3}, {3, 4},
                {3, 5}, {4, 6}, {5, 6}
            };

            for (int[] edge : dependencies) {
                directed.addEdge(edge[0], edge[1]);
            }

            TopologicalResult result =
                directed.topologicalSort();

            System.out.println(
                "Topological order: " + result.order()
            );

            System.out.println(
                "Directed cycle: " + directed.hasDirectedCycle()
            );

            directed.addEdge(6, 3);

            result = directed.topologicalSort();

            System.out.println(
                "After adding edge 6 -> 3:"
            );

            System.out.println(
                "Cycle: " + directed.hasDirectedCycle()
            );

            System.out.println(
                "Topological ordering valid: "
                + !result.hasCycle()
            );

            // Automated validation.
            Graph test = new Graph(
                List.of(10, 20, 30, 40),
                GraphType.UNDIRECTED
            );

            test.addEdge(10, 20);
            test.addEdge(20, 30);

            verify(
                test.connectedComponents().size() == 2,
                "Connected components"
            );

            verify(
                test.isBipartite().bipartite(),
                "Bipartite graph"
            );

            verify(
                test.shortestPath(10, 30).equals(
                    List.of(10, 20, 30)
                ),
                "Shortest path"
            );

            test.addEdge(30, 10);

            verify(
                test.hasUndirectedCycle(),
                "Undirected cycle"
            );

            verify(
                !test.isBipartite().bipartite(),
                "Odd cycle"
            );

            Graph empty = new Graph(
                List.of(),
                GraphType.UNDIRECTED
            );

            verify(
                empty.connectedComponents().isEmpty(),
                "Empty graph"
            );

            System.out.println(
                "\nAll graph assessment tests passed."
            );

            System.out.println(
                "Recorded assessments: "
                + service.history().size()
            );

        } catch (RuntimeException | AssertionError exception) {
            System.err.println(
                "Assessment failure: "
                + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
