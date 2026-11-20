import java.util.*;

/*
 * Breadth-First Search (BFS)
 *
 * Enterprise-oriented graph traversal engine.
 *
 * Features:
 * - Immutable BFS results
 * - Graph domain modeling
 * - Directed and undirected graphs
 * - Queue-based traversal
 * - Shortest paths
 * - Level processing
 * - Multi-source BFS
 * - Grid shortest paths
 * - Connected components
 * - Validation and custom exceptions
 *
 * Java version: 17
 */

public class Main {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    record GridPoint(int row, int col) {}

    record Level(int number, List<Integer> vertices) {
        Level {
            vertices = List.copyOf(vertices);
        }
    }

    static final class BFSResult {
        private final Map<Integer, Integer> distances;
        private final Map<Integer, Integer> parents;
        private final Map<Integer, List<Integer>> levels;

        BFSResult(
            Map<Integer, Integer> distances,
            Map<Integer, Integer> parents,
            Map<Integer, List<Integer>> levels
        ) {
            this.distances = Collections.unmodifiableMap(
                new LinkedHashMap<>(distances)
            );

            this.parents = Collections.unmodifiableMap(
                new LinkedHashMap<>(parents)
            );

            Map<Integer, List<Integer>> copy = new LinkedHashMap<>();

            levels.forEach(
                (level, vertices) ->
                    copy.put(level, List.copyOf(vertices))
            );

            this.levels = Collections.unmodifiableMap(copy);
        }

        public Map<Integer, Integer> distances() {
            return distances;
        }

        public Map<Integer, Integer> parents() {
            return parents;
        }

        public Map<Integer, List<Integer>> levels() {
            return levels;
        }

        public Optional<List<Integer>> shortestPath(int target) {
            if (!distances.containsKey(target)) {
                return Optional.empty();
            }

            List<Integer> path = new ArrayList<>();
            int current = target;

            while (true) {
                path.add(current);

                Integer parent = parents.get(current);

                if (parent == null) {
                    break;
                }

                current = parent;
            }

            Collections.reverse(path);

            return Optional.of(List.copyOf(path));
        }
    }


    static final class Graph {
        private final GraphType type;

        private final Map<Integer, List<Integer>> adjacency =
            new LinkedHashMap<>();

        Graph(GraphType type) {
            this.type = Objects.requireNonNull(type);
        }

        public void addVertex(int vertex) {
            adjacency.putIfAbsent(vertex, new ArrayList<>());
        }

        public void addEdge(int source, int destination) {
            addVertex(source);
            addVertex(destination);

            adjacency.get(source).add(destination);

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(destination).add(source);
            }
        }

        private void validateSources(List<Integer> sources) {
            if (sources == null || sources.isEmpty()) {
                throw new GraphException(
                    "At least one source is required"
                );
            }

            for (Integer source : sources) {
                if (source == null || !adjacency.containsKey(source)) {
                    throw new GraphException(
                        "Unknown or null source vertex"
                    );
                }
            }
        }

        public BFSResult bfs(int source) {
            return multiSourceBfs(List.of(source));
        }

        public BFSResult multiSourceBfs(List<Integer> sources) {
            validateSources(sources);

            LinkedHashSet<Integer> uniqueSources =
                new LinkedHashSet<>(sources);

            Queue<Integer> queue = new ArrayDeque<>();

            Map<Integer, Integer> distances = new LinkedHashMap<>();
            Map<Integer, Integer> parents = new LinkedHashMap<>();
            Map<Integer, List<Integer>> levels = new LinkedHashMap<>();

            List<Integer> initialLevel = new ArrayList<>();

            for (int source : uniqueSources) {
                queue.add(source);
                distances.put(source, 0);
                parents.put(source, null);
                initialLevel.add(source);
            }

            levels.put(0, initialLevel);

            while (!queue.isEmpty()) {
                int current = queue.remove();

                for (int neighbor : adjacency.get(current)) {
                    if (distances.containsKey(neighbor)) {
                        continue;
                    }

                    int distance = distances.get(current) + 1;

                    distances.put(neighbor, distance);
                    parents.put(neighbor, current);

                    levels.computeIfAbsent(
                        distance,
                        ignored -> new ArrayList<>()
                    ).add(neighbor);

                    queue.add(neighbor);
                }
            }

            return new BFSResult(distances, parents, levels);
        }

        public List<List<Integer>> connectedComponents() {
            if (type == GraphType.DIRECTED) {
                throw new GraphException(
                    "Connected components require an undirected graph"
                );
            }

            Set<Integer> visited = new HashSet<>();
            List<List<Integer>> components = new ArrayList<>();

            for (int start : adjacency.keySet()) {
                if (!visited.add(start)) {
                    continue;
                }

                Queue<Integer> queue = new ArrayDeque<>();
                List<Integer> component = new ArrayList<>();

                queue.add(start);

                while (!queue.isEmpty()) {
                    int current = queue.remove();
                    component.add(current);

                    for (int neighbor : adjacency.get(current)) {
                        if (visited.add(neighbor)) {
                            queue.add(neighbor);
                        }
                    }
                }

                components.add(List.copyOf(component));
            }

            return List.copyOf(components);
        }
    }


    static Optional<List<GridPoint>> shortestGridPath(
        int[][] grid,
        GridPoint start,
        GridPoint target
    ) {
        if (grid == null || grid.length == 0 || grid[0].length == 0) {
            throw new GraphException("Grid cannot be empty");
        }

        int rows = grid.length;
        int cols = grid[0].length;

        for (int[] row : grid) {
            if (row == null || row.length != cols) {
                throw new GraphException("Grid must be rectangular");
            }

            for (int cell : row) {
                if (cell != 0 && cell != 1) {
                    throw new GraphException(
                        "Grid cells must be 0 or 1"
                    );
                }
            }
        }

        Objects.requireNonNull(start);
        Objects.requireNonNull(target);

        java.util.function.Predicate<GridPoint> valid = point ->
            point.row() >= 0 &&
            point.row() < rows &&
            point.col() >= 0 &&
            point.col() < cols &&
            grid[point.row()][point.col()] == 0;

        if (!valid.test(start) || !valid.test(target)) {
            return Optional.empty();
        }

        boolean[][] visited = new boolean[rows][cols];

        GridPoint[][] parent = new GridPoint[rows][cols];

        Queue<GridPoint> queue = new ArrayDeque<>();

        queue.add(start);
        visited[start.row()][start.col()] = true;

        int[][] directions = {
            {-1, 0},
            {1, 0},
            {0, -1},
            {0, 1}
        };

        while (!queue.isEmpty()) {
            GridPoint current = queue.remove();

            if (current.equals(target)) {
                break;
            }

            for (int[] direction : directions) {
                GridPoint next = new GridPoint(
                    current.row() + direction[0],
                    current.col() + direction[1]
                );

                if (
                    valid.test(next) &&
                    !visited[next.row()][next.col()]
                ) {
                    visited[next.row()][next.col()] = true;
                    parent[next.row()][next.col()] = current;
                    queue.add(next);
                }
            }
        }

        if (!visited[target.row()][target.col()]) {
            return Optional.empty();
        }

        List<GridPoint> path = new ArrayList<>();
        GridPoint current = target;

        while (current != null) {
            path.add(current);

            if (current.equals(start)) {
                break;
            }

            current = parent[current.row()][current.col()];
        }

        Collections.reverse(path);

        return Optional.of(List.copyOf(path));
    }


    static void printResult(BFSResult result) {
        System.out.println("Distances: " + result.distances());

        System.out.println("Parents: " + result.parents());

        result.levels().forEach(
            (level, vertices) ->
                System.out.println(
                    "Level " + level + ": " + vertices
                )
        );
    }


    public static void main(String[] args) {
        try {
            Graph graph = new Graph(GraphType.UNDIRECTED);

            int[][] edges = {
                {0, 1}, {0, 2},
                {1, 3}, {1, 4},
                {2, 5}, {2, 6},
                {4, 7}, {5, 7}
            };

            for (int[] edge : edges) {
                graph.addEdge(edge[0], edge[1]);
            }

            System.out.println("=== BFS Traversal ===");

            BFSResult result = graph.bfs(0);
            printResult(result);

            System.out.println("\nShortest path 0 -> 7:");

            System.out.println(
                result.shortestPath(7).orElse(List.of())
            );

            System.out.println("\n=== Multi-Source BFS ===");

            BFSResult multi = graph.multiSourceBfs(
                List.of(0, 7)
            );

            printResult(multi);

            System.out.println("\n=== Connected Components ===");

            graph.addEdge(10, 11);

            System.out.println(graph.connectedComponents());

            System.out.println("\n=== Grid BFS ===");

            int[][] grid = {
                {0, 0, 0, 1},
                {1, 0, 0, 0},
                {0, 0, 1, 0},
                {0, 0, 0, 0}
            };

            System.out.println(
                shortestGridPath(
                    grid,
                    new GridPoint(0, 0),
                    new GridPoint(3, 3)
                )
            );

            System.out.println("\n=== Automated Tests ===");

            assert result.distances().get(0) == 0;
            assert result.distances().get(7) == 3;

            assert result.shortestPath(7).orElseThrow()
                .equals(List.of(0, 1, 4, 7));

            assert result.shortestPath(999).isEmpty();

            assert multi.distances().get(0) == 0;
            assert multi.distances().get(7) == 0;

            assert graph.connectedComponents().size() == 2;

            assert shortestGridPath(
                new int[][]{{0, 1}, {1, 0}},
                new GridPoint(0, 0),
                new GridPoint(1, 1)
            ).isEmpty();

            try {
                graph.bfs(999);
                throw new AssertionError("Invalid vertex accepted");
            } catch (GraphException expected) {
                System.out.println("Invalid vertex rejected.");
            }

            System.out.println("All tests passed.");

        } catch (GraphException error) {
            System.err.println(
                "Graph execution failed: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
