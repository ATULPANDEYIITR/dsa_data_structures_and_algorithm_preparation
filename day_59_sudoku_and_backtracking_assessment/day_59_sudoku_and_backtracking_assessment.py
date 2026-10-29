from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional
import copy
import time


class SolveStatus(Enum):
    SOLVED = "solved"
    UNSOLVABLE = "unsolvable"


@dataclass
class SolveResult:
    status: SolveStatus
    board: list[list[int]]
    decisions: int
    backtracks: int
    elapsed_ms: float


class SudokuError(ValueError):
    pass


class SudokuSolver:
    SIZE = 9
    BOX = 3
    EMPTY = 0

    def __init__(self, board: list[list[int]]):
        self._validate_shape(board)
        self.board = copy.deepcopy(board)
        self.rows = [set() for _ in range(self.SIZE)]
        self.cols = [set() for _ in range(self.SIZE)]
        self.boxes = [set() for _ in range(self.SIZE)]
        self.decisions = 0
        self.backtracks = 0
        self._load_constraints()

    @classmethod
    def _validate_shape(cls, board: list[list[int]]) -> None:
        if len(board) != cls.SIZE:
            raise SudokuError("Sudoku board must contain exactly 9 rows.")
        if any(len(row) != cls.SIZE for row in board):
            raise SudokuError("Every Sudoku row must contain exactly 9 values.")
        for row in board:
            for value in row:
                if not isinstance(value, int) or not 0 <= value <= 9:
                    raise SudokuError("Each cell must be an integer from 0 through 9.")

    @staticmethod
    def _box_index(row: int, col: int) -> int:
        return (row // 3) * 3 + col // 3

    def _load_constraints(self) -> None:
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                value = self.board[row][col]
                if value == self.EMPTY:
                    continue
                box = self._box_index(row, col)
                if (
                    value in self.rows[row]
                    or value in self.cols[col]
                    or value in self.boxes[box]
                ):
                    raise SudokuError(
                        f"Invalid puzzle: duplicate value {value} at ({row}, {col})."
                    )
                self.rows[row].add(value)
                self.cols[col].add(value)
                self.boxes[box].add(value)

    def candidates(self, row: int, col: int) -> set[int]:
        if self.board[row][col] != self.EMPTY:
            return set()
        used = self.rows[row] | self.cols[col] | self.boxes[self._box_index(row, col)]
        return set(range(1, 10)) - used

    def _find_most_constrained_cell(self) -> Optional[tuple[int, int, set[int]]]:
        best: Optional[tuple[int, int, set[int]]] = None

        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.board[row][col] != self.EMPTY:
                    continue

                options = self.candidates(row, col)

                if not options:
                    return row, col, set()

                if best is None or len(options) < len(best[2]):
                    best = (row, col, options)

                if len(options) == 1:
                    return best

        return best

    def _place(self, row: int, col: int, value: int) -> None:
        box = self._box_index(row, col)
        self.board[row][col] = value
        self.rows[row].add(value)
        self.cols[col].add(value)
        self.boxes[box].add(value)

    def _undo(self, row: int, col: int, value: int) -> None:
        box = self._box_index(row, col)
        self.board[row][col] = self.EMPTY
        self.rows[row].remove(value)
        self.cols[col].remove(value)
        self.boxes[box].remove(value)

    def _backtrack(self) -> bool:
        cell = self._find_most_constrained_cell()

        if cell is None:
            return True

        row, col, options = cell

        if not options:
            return False

        # Choice -> constraint check -> recursive call -> undo choice.
        for value in sorted(options):
            self.decisions += 1
            self._place(row, col, value)

            if self._backtrack():
                return True

            self._undo(row, col, value)
            self.backtracks += 1

        return False

    def solve(self) -> SolveResult:
        started = time.perf_counter()
        solved = self._backtrack()
        elapsed_ms = (time.perf_counter() - started) * 1000

        return SolveResult(
            status=SolveStatus.SOLVED if solved else SolveStatus.UNSOLVABLE,
            board=copy.deepcopy(self.board),
            decisions=self.decisions,
            backtracks=self.backtracks,
            elapsed_ms=elapsed_ms,
        )


def print_board(board: list[list[int]]) -> None:
    for row_index, row in enumerate(board):
        if row_index and row_index % 3 == 0:
            print("------+-------+------")
        print(
            " ".join(
                "." if value == 0 else str(value)
                for value in row[:3]
            )
            + " | "
            + " ".join(
                "." if value == 0 else str(value)
                for value in row[3:6]
            )
            + " | "
            + " ".join(
                "." if value == 0 else str(value)
                for value in row[6:]
            )
        )


def is_valid_sudoku(board: list[list[int]]) -> bool:
    try:
        solver = SudokuSolver(board)
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    continue
                # Construction already validates all fixed constraints.
                if board[row][col] not in solver.rows[row]:
                    return False
        return True
    except SudokuError:
        return False


def subsets_with_target(values: list[int], target: int) -> list[list[int]]:
    """Mixed backtracking example: choose each value at most once."""
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path.copy())
            return

        if remaining < 0:
            return

        for index in range(start, len(values)):
            if index > start and values[index] == values[index - 1]:
                continue

            value = values[index]
            if value > remaining:
                break

            path.append(value)              # Choice
            backtrack(index + 1, remaining - value)  # Recursive call
            path.pop()                      # Undo choice

    values = sorted(values)
    backtrack(0, target)
    return result


def generate_parentheses(pairs: int) -> list[str]:
    if pairs < 0:
        raise ValueError("pairs must be non-negative")

    result: list[str] = []
    path: list[str] = []

    def backtrack(opened: int, closed: int) -> None:
        if opened == pairs and closed == pairs:
            result.append("".join(path))
            return

        if opened < pairs:
            path.append("(")                # Choice
            backtrack(opened + 1, closed)   # Recursive call
            path.pop()                      # Undo choice

        if closed < opened:
            path.append(")")                # Choice
            backtrack(opened, closed + 1)   # Recursive call
            path.pop()                      # Undo choice

    backtrack(0, 0)
    return result


def main() -> None:
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    print("Original Sudoku:")
    print_board(puzzle)

    solver = SudokuSolver(puzzle)
    result = solver.solve()

    print("\nSolved Sudoku:")
    print_board(result.board)
    print(
        f"\nStatus={result.status.value}, "
        f"decisions={result.decisions}, "
        f"backtracks={result.backtracks}, "
        f"time={result.elapsed_ms:.3f} ms"
    )

    assert result.status is SolveStatus.SOLVED
    assert all(0 not in row for row in result.board)
    assert is_valid_sudoku(result.board)

    print("\nSubset-sum backtracking:")
    print(subsets_with_target([2, 3, 5, 6, 8], 10))

    print("\nParentheses backtracking:")
    print(generate_parentheses(3))

    invalid = [
        [5, 5, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    try:
        SudokuSolver(invalid)
    except SudokuError as exc:
        print(f"\nValidation correctly rejected invalid input: {exc}")


if __name__ == "__main__":
    main()
