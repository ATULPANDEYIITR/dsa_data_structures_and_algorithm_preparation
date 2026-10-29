import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class BacktrackingAssessment {

    enum CellState {
        EMPTY,
        FIXED,
        GENERATED
    }

    record Position(int row, int column) {}

    record SearchChoice(Position position, Set<Integer> candidates) {}

    record SolveMetrics(int decisions, int backtracks, long elapsedNanos) {}

    record SolveResult(boolean solved, int[][] board, SolveMetrics metrics) {}

    static final class SudokuException extends RuntimeException {
        SudokuException(String message) {
            super(message);
        }
    }

    static final class Sudoku {
        private final int[][] board;
        private final Set<Integer>[] rows;
        private final Set<Integer>[] columns;
        private final Set<Integer>[] boxes;
        private int decisions;
        private int backtracks;

        @SuppressWarnings("unchecked")
        Sudoku(int[][] input) {
            validateShape(input);
            this.board = deepCopy(input);

            rows = new Set[9];
            columns = new Set[9];
            boxes = new Set[9];

            for (int i = 0; i < 9; i++) {
                rows[i] = new HashSet<>();
                columns[i] = new HashSet<>();
                boxes[i] = new HashSet<>();
            }

            initializeConstraints();
        }

        private static void validateShape(int[][] input) {
            if (input == null || input.length != 9) {
                throw new SudokuException("A Sudoku requires exactly nine rows.");
            }

            for (int[] row : input) {
                if (row == null || row.length != 9) {
                    throw new SudokuException("Every row must contain nine cells.");
                }

                for (int value : row) {
                    if (value < 0 || value > 9) {
                        throw new SudokuException("Cells must contain values from 0 through 9.");
                    }
                }
            }
        }

        private static int[][] deepCopy(int[][] source) {
            int[][] copy = new int[source.length][];
            for (int i = 0; i < source.length; i++) {
                copy[i] = Arrays.copyOf(source[i], source[i].length);
            }
            return copy;
        }

        private static int boxIndex(int row, int column) {
            return (row / 3) * 3 + column / 3;
        }

        private void initializeConstraints() {
            for (int row = 0; row < 9; row++) {
                for (int column = 0; column < 9; column++) {
                    int value = board[row][column];

                    if (value == 0) {
                        continue;
                    }

                    int box = boxIndex(row, column);

                    if (rows[row].contains(value)
                            || columns[column].contains(value)
                            || boxes[box].contains(value)) {
                        throw new SudokuException(
                                "Initial puzzle violates Sudoku constraints."
                        );
                    }

                    rows[row].add(value);
                    columns[column].add(value);
                    boxes[box].add(value);
                }
            }
        }

        private Set<Integer> candidates(int row, int column) {
            if (board[row][column] != 0) {
                return Set.of();
            }

            Set<Integer> candidates = new HashSet<>();

            for (int value = 1; value <= 9; value++) {
                int box = boxIndex(row, column);

                if (!rows[row].contains(value)
                        && !columns[column].contains(value)
                        && !boxes[box].contains(value)) {
                    candidates.add(value);
                }
            }

            return candidates;
        }

        private SearchChoice selectCell() {
            SearchChoice best = null;

            for (int row = 0; row < 9; row++) {
                for (int column = 0; column < 9; column++) {
                    if (board[row][column] != 0) {
                        continue;
                    }

                    Set<Integer> candidates = candidates(row, column);

                    if (candidates.isEmpty()) {
                        return new SearchChoice(
                                new Position(row, column),
                                Set.of()
                        );
                    }

                    SearchChoice current = new SearchChoice(
                            new Position(row, column),
                            candidates
                    );

                    if (best == null
                            || current.candidates().size() < best.candidates().size()) {
                        best = current;
                    }

                    if (best.candidates().size() == 1) {
                        return best;
                    }
                }
            }

            return best;
        }

        private void place(Position position, int value) {
            int row = position.row();
            int column = position.column();
            int box = boxIndex(row, column);

            board[row][column] = value;
            rows[row].add(value);
            columns[column].add(value);
            boxes[box].add(value);
        }

        private void undo(Position position, int value) {
            int row = position.row();
            int column = position.column();
            int box = boxIndex(row, column);

            board[row][column] = 0;
            rows[row].remove(value);
            columns[column].remove(value);
            boxes[box].remove(value);
        }

        private boolean search() {
            SearchChoice choice = selectCell();

            if (choice == null) {
                return true;
            }

            if (choice.candidates().isEmpty()) {
                return false;
            }

            for (int value : choice.candidates().stream()
                    .sorted()
                    .toList()) {

                decisions++;
                place(choice.position(), value);

                if (search()) {
                    return true;
                }

                undo(choice.position(), value);
                backtracks++;
            }

            return false;
        }

        SolveResult solve() {
            long started = System.nanoTime();
            boolean solved = search();
            long elapsed = System.nanoTime() - started;

            return new SolveResult(
                    solved,
                    deepCopy(board),
                    new SolveMetrics(decisions, backtracks, elapsed)
            );
        }
    }

    interface SearchProblem<S, R> {
        R solve(S input);
    }

    static final class CombinationSearch
            implements SearchProblem<List<Integer>, List<List<Integer>>> {

        private final int target;
        private final List<List<Integer>> results = new ArrayList<>();
        private final List<Integer> path = new ArrayList<>();

        CombinationSearch(int target) {
            if (target < 0) {
                throw new IllegalArgumentException("Target cannot be negative.");
            }
            this.target = target;
        }

        @Override
        public List<List<Integer>> solve(List<Integer> input) {
            List<Integer> values = new ArrayList<>(input);
            values.sort(Comparator.naturalOrder());
            search(values, 0, target);
            return List.copyOf(results);
        }

        private void search(List<Integer> values, int start, int remaining) {
            if (remaining == 0) {
                results.add(List.copyOf(path));
                return;
            }

            if (remaining < 0) {
                return;
            }

            for (int index = start; index < values.size(); index++) {
                if (index > start
                        && values.get(index).equals(values.get(index - 1))) {
                    continue;
                }

                int value = values.get(index);

                if (value > remaining) {
                    break;
                }

                path.add(value);                       // Choice
                search(values, index + 1, remaining - value); // Recursive call
                path.remove(path.size() - 1);          // Undo choice
            }
        }
    }

    static void printBoard(int[][] board) {
        for (int row = 0; row < 9; row++) {
            if (row > 0 && row % 3 == 0) {
                System.out.println("------+-------+------");
            }

            for (int column = 0; column < 9; column++) {
                if (column > 0 && column % 3 == 0) {
                    System.out.print("| ");
                }

                int value = board[row][column];
                System.out.print(value == 0 ? "." : value);

                if (column < 8) {
                    System.out.print(" ");
                }
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        int[][] puzzle = {
                {5, 3, 0, 0, 7, 0, 0, 0, 0},
                {6, 0, 0, 1, 9, 5, 0, 0, 0},
                {0, 9, 8, 0, 0, 0, 0, 6, 0},
                {8, 0, 0, 0, 6, 0, 0, 0, 3},
                {4, 0, 0, 8, 0, 3, 0, 0, 1},
                {7, 0, 0, 0, 2, 0, 0, 0, 6},
                {0, 6, 0, 0, 0, 0, 2, 8, 0},
                {0, 0, 0, 4, 1, 9, 0, 0, 5},
                {0, 0, 0, 0, 8, 0, 0, 7, 9}
        };

        Sudoku sudoku = new Sudoku(puzzle);

        System.out.println("Original Sudoku:");
        printBoard(puzzle);

        SolveResult result = sudoku.solve();

        System.out.println("\nSolved Sudoku:");
        printBoard(result.board());

        System.out.printf(
                "%nSolved=%s, decisions=%d, backtracks=%d, time=%.3f ms%n",
                result.solved(),
                result.metrics().decisions(),
                result.metrics().backtracks(),
                result.metrics().elapsedNanos() / 1_000_000.0
        );

        if (!result.solved()) {
            throw new IllegalStateException("Expected the assessment puzzle to be solvable.");
        }

        CombinationSearch combinationSearch = new CombinationSearch(10);
        List<List<Integer>> combinations =
                combinationSearch.solve(List.of(2, 3, 5, 6, 8));

        System.out.println("\nSubset-sum backtracking:");
        combinations.forEach(System.out::println);
    }
}
