import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Main {

    record Position(int row, int col) {}

    enum Cell {
        OPEN('.'),
        BLOCKED('#');

        private final char symbol;

        Cell(char symbol) {
            this.symbol = symbol;
        }

        char symbol() {
            return symbol;
        }
    }

    interface SearchPolicy {
        List<Position> find(Maze maze, Position start, Position target);
    }

    static final class InvalidBoardException extends RuntimeException {
        InvalidBoardException(String message) {
            super(message);
        }
    }

    static final class NQueensSolver {
        private final int n;
        private final List<int[]> solutions = new ArrayList<>();

        NQueensSolver(int n) {
            if (n < 1 || n > 14) {
                throw new InvalidBoardException(
                    "n must be between 1 and 14"
                );
            }
            this.n = n;
        }

        List<int[]> solve() {
            solutions.clear();

            int[] placement = new int[n];
            java.util.Arrays.fill(placement, -1);

            boolean[] columns = new boolean[n];
            boolean[] descending = new boolean[2 * n - 1];
            boolean[] ascending = new boolean[2 * n - 1];

            backtrack(
                0,
                placement,
                columns,
                descending,
                ascending
            );

            return List.copyOf(solutions);
        }

        private void backtrack(
            int row,
            int[] placement,
            boolean[] columns,
            boolean[] descending,
            boolean[] ascending
        ) {
            if (row == n) {
                solutions.add(placement.clone());
                return;
            }

            for (int col = 0; col < n; col++) {
                int down = row - col + n - 1;
                int up = row + col;

                if (columns[col] ||
                    descending[down] ||
                    ascending[up]) {
                    continue;
                }

                placement[row] = col;
                columns[col] = true;
                descending[down] = true;
                ascending[up] = true;

                backtrack(
                    row + 1,
                    placement,
                    columns,
                    descending,
                    ascending
                );

                placement[row] = -1;
                columns[col] = false;
                descending[down] = false;
                ascending[up] = false;
            }
        }

        String render(int[] solution) {
            if (solution.length != n) {
                throw new InvalidBoardException("invalid solution length");
            }

            StringBuilder output = new StringBuilder();

            for (int row = 0; row < n; row++) {
                if (solution[row] < 0 || solution[row] >= n) {
                    throw new InvalidBoardException("invalid queen column");
                }

                for (int col = 0; col < n; col++) {
                    output.append(solution[row] == col ? 'Q' : '.');
                    if (col + 1 < n) {
                        output.append(' ');
                    }
                }

                if (row + 1 < n) {
                    output.append('\n');
                }
            }

            return output.toString();
        }
    }

    static final class Maze {
        private final List<String> grid;
        private final int rows;
        private final int cols;

        Maze(List<String> input) {
            if (input == null || input.isEmpty()) {
                throw new InvalidBoardException("maze cannot be empty");
            }

            int width = input.get(0).length();
            if (width == 0) {
                throw new InvalidBoardException("maze rows cannot be empty");
            }

            for (String row : input) {
                if (row.length() != width ||
                    !row.matches("[.#]+")) {
                    throw new InvalidBoardException(
                        "maze must be rectangular and contain only . and #"
                    );
                }
            }

            this.grid = List.copyOf(input);
            this.rows = input.size();
            this.cols = width;
        }

        boolean isOpen(Position p) {
            return p.row() >= 0 &&
                   p.row() < rows &&
                   p.col() >= 0 &&
                   p.col() < cols &&
                   grid.get(p.row()).charAt(p.col()) == '.';
        }

        List<List<Position>> allPaths(
            Position start,
            Position target,
            int maxPaths
        ) {
            if (maxPaths < 1) {
                throw new IllegalArgumentException(
                    "maxPaths must be positive"
                );
            }

            if (!isOpen(start) || !isOpen(target)) {
                return List.of();
            }

            List<List<Position>> result = new ArrayList<>();
            List<Position> current = new ArrayList<>();
            Set<Position> visited = new HashSet<>();

            current.add(start);
            visited.add(start);

            generate(
                start,
                target,
                maxPaths,
                current,
                visited,
                result
            );

            return List.copyOf(result);
        }

        private void generate(
            Position current,
            Position target,
            int maxPaths,
            List<Position> path,
            Set<Position> visited,
            List<List<Position>> result
        ) {
            if (result.size() >= maxPaths) {
                return;
            }

            if (current.equals(target)) {
                result.add(List.copyOf(path));
                return;
            }

            int[][] directions = {
                {-1, 0},
                {1, 0},
                {0, -1},
                {0, 1}
            };

            for (int[] direction : directions) {
                Position next = new Position(
                    current.row() + direction[0],
                    current.col() + direction[1]
                );

                if (!isOpen(next) || visited.contains(next)) {
                    continue;
                }

                visited.add(next);
                path.add(next);

                generate(
                    next,
                    target,
                    maxPaths,
                    path,
                    visited,
                    result
                );

                path.remove(path.size() - 1);
                visited.remove(next);
            }
        }

        String renderPath(List<Position> path) {
            Set<Position> cells = new HashSet<>(path);
            StringBuilder output = new StringBuilder();

            for (int r = 0; r < rows; r++) {
                for (int c = 0; c < cols; c++) {
                    Position p = new Position(r, c);
                    char value = cells.contains(p)
                        ? '*'
                        : grid.get(r).charAt(c);

                    output.append(value);
                    if (c + 1 < cols) {
                        output.append(' ');
                    }
                }

                if (r + 1 < rows) {
                    output.append('\n');
                }
            }

            return output.toString();
        }

        List<Position> shortestPath(Position start, Position target) {
            if (!isOpen(start) || !isOpen(target)) {
                return null;
            }

            ArrayDeque<Position> queue = new ArrayDeque<>();
            Set<Position> visited = new HashSet<>();
            Map<Position, Position> previous = new HashMap<>();

            queue.add(start);
            visited.add(start);

            while (!queue.isEmpty()) {
                Position current = queue.remove();

                if (current.equals(target)) {
                    List<Position> path = new ArrayList<>();
                    Position node = target;

                    path.add(node);

                    while (!node.equals(start)) {
                        node = previous.get(node);
                        path.add(node);
                    }

                    Collections.reverse(path);
                    return List.copyOf(path);
                }

                int[][] directions = {
                    {-1, 0},
                    {1, 0},
                    {0, -1},
                    {0, 1}
                };

                for (int[] direction : directions) {
                    Position next = new Position(
                        current.row() + direction[0],
                        current.col() + direction[1]
                    );

                    if (!isOpen(next) || visited.contains(next)) {
                        continue;
                    }

                    visited.add(next);
                    previous.put(next, current);
                    queue.add(next);
                }
            }

            return null;
        }
    }

    static final class BreadthFirstPolicy implements SearchPolicy {
        @Override
        public List<Position> find(
            Maze maze,
            Position start,
            Position target
        ) {
            List<Position> result = maze.shortestPath(start, target);
            return result == null ? List.of() : result;
        }
    }

    static boolean validQueensSolution(int[] solution) {
        int n = solution.length;

        if (n == 0) {
            return false;
        }

        Set<Integer> columns = new HashSet<>();
        Set<Integer> down = new HashSet<>();
        Set<Integer> up = new HashSet<>();

        for (int row = 0; row < n; row++) {
            int col = solution[row];

            if (col < 0 || col >= n) {
                return false;
            }

            if (!columns.add(col) ||
                !down.add(row - col) ||
                !up.add(row + col)) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        try {
            System.out.println("=== N-Queens ===");

            NQueensSolver solver = new NQueensSolver(4);
            List<int[]> solutions = solver.solve();

            if (solutions.size() != 2) {
                throw new IllegalStateException(
                    "4-Queens must have two solutions"
                );
            }

            for (int i = 0; i < solutions.size(); i++) {
                int[] solution = solutions.get(i);

                if (!validQueensSolution(solution)) {
                    throw new IllegalStateException(
                        "invalid N-Queens solution"
                    );
                }

                System.out.println("\nSolution " + (i + 1));
                System.out.println(solver.render(solution));
            }

            System.out.println("\n=== Maze Path Generation ===");

            Maze maze = new Maze(List.of(
                "...#.",
                ".#...",
                "...#.",
                "#....",
                "....."
            ));

            Position start = new Position(0, 0);
            Position target = new Position(4, 4);

            List<List<Position>> paths =
                maze.allPaths(start, target, 5);

            System.out.println("Generated paths: " + paths.size());

            for (int i = 0; i < paths.size(); i++) {
                System.out.println(
                    "\nPath " + (i + 1) +
                    ", length=" + paths.get(i).size()
                );
                System.out.println(
                    maze.renderPath(paths.get(i))
                );
            }

            SearchPolicy shortestPathPolicy =
                new BreadthFirstPolicy();

            List<Position> shortest =
                shortestPathPolicy.find(maze, start, target);

            if (shortest.isEmpty()) {
                throw new IllegalStateException(
                    "target should be reachable"
                );
            }

            System.out.println(
                "\nShortest path length: " + shortest.size()
            );
            System.out.println(maze.renderPath(shortest));

            if (new NQueensSolver(1).solve().size() != 1 ||
                !new NQueensSolver(2).solve().isEmpty() ||
                !new NQueensSolver(3).solve().isEmpty()) {
                throw new IllegalStateException(
                    "N-Queens edge-case validation failed"
                );
            }

            Maze blocked = new Maze(List.of(
                ".#",
                "#."
            ));

            if (!blocked.allPaths(
                new Position(0, 0),
                new Position(1, 1),
                5
            ).isEmpty()) {
                throw new IllegalStateException(
                    "blocked-maze validation failed"
                );
            }

            System.out.println("\nAll validation checks passed.");
        } catch (RuntimeException ex) {
            System.err.println("Failure: " + ex.getMessage());
            System.exit(1);
        }
    }
}
