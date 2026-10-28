from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Cell(str, Enum):
    OPEN = "."
    BLOCKED = "#"


@dataclass(frozen=True)
class Position:
    row: int
    col: int


@dataclass
class NQueensSolver:
    n: int
    solutions: list[list[int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.n, int) or isinstance(self.n, bool):
            raise TypeError("n must be an integer")
        if self.n < 1 or self.n > 14:
            raise ValueError("n must be between 1 and 14")

    def solve(self) -> list[list[int]]:
        self.solutions.clear()

        columns: set[int] = set()
        diagonals_down: set[int] = set()  # row - col
        diagonals_up: set[int] = set()    # row + col
        placement = [-1] * self.n

        def backtrack(row: int) -> None:
            if row == self.n:
                self.solutions.append(placement.copy())
                return

            for col in range(self.n):
                if col in columns:
                    continue
                if row - col in diagonals_down:
                    continue
                if row + col in diagonals_up:
                    continue

                placement[row] = col
                columns.add(col)
                diagonals_down.add(row - col)
                diagonals_up.add(row + col)

                backtrack(row + 1)

                placement[row] = -1
                columns.remove(col)
                diagonals_down.remove(row - col)
                diagonals_up.remove(row + col)

        backtrack(0)
        return self.solutions

    def count(self) -> int:
        columns: set[int] = set()
        diagonals_down: set[int] = set()
        diagonals_up: set[int] = set()
        count = 0

        def backtrack(row: int) -> None:
            nonlocal count

            if row == self.n:
                count += 1
                return

            for col in range(self.n):
                if (
                    col in columns
                    or row - col in diagonals_down
                    or row + col in diagonals_up
                ):
                    continue

                columns.add(col)
                diagonals_down.add(row - col)
                diagonals_up.add(row + col)

                backtrack(row + 1)

                columns.remove(col)
                diagonals_down.remove(row - col)
                diagonals_up.remove(row + col)

        backtrack(0)
        return count

    def render(self, solution: list[int]) -> str:
        if len(solution) != self.n:
            raise ValueError("solution length does not match board size")

        lines = []
        for row, queen_col in enumerate(solution):
            if not 0 <= queen_col < self.n:
                raise ValueError("invalid queen column")
            lines.append(" ".join("Q" if c == queen_col else "." for c in range(self.n)))
        return "\n".join(lines)


@dataclass
class Maze:
    grid: list[str]

    def __post_init__(self) -> None:
        if not self.grid:
            raise ValueError("maze cannot be empty")

        width = len(self.grid[0])
        if width == 0:
            raise ValueError("maze rows cannot be empty")

        for row in self.grid:
            if len(row) != width:
                raise ValueError("maze must be rectangular")
            if any(ch not in {Cell.OPEN.value, Cell.BLOCKED.value} for ch in row):
                raise ValueError("maze may contain only '.' and '#'")

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0])

    def valid(self, p: Position) -> bool:
        return (
            0 <= p.row < self.rows
            and 0 <= p.col < self.cols
            and self.grid[p.row][p.col] == Cell.OPEN.value
        )

    def all_paths(
        self,
        start: Position,
        target: Position,
        max_paths: int = 10_000,
    ) -> list[list[Position]]:
        if max_paths < 1:
            raise ValueError("max_paths must be positive")
        if not self.valid(start) or not self.valid(target):
            return []

        paths: list[list[Position]] = []
        path: list[Position] = [start]
        visited: set[Position] = {start}

        # Four-way movement. The visited set prevents cycles within one path.
        directions = (
            Position(-1, 0),
            Position(1, 0),
            Position(0, -1),
            Position(0, 1),
        )

        def backtrack(current: Position) -> None:
            if len(paths) >= max_paths:
                return

            if current == target:
                paths.append(path.copy())
                return

            for direction in directions:
                nxt = Position(
                    current.row + direction.row,
                    current.col + direction.col,
                )

                if not self.valid(nxt) or nxt in visited:
                    continue

                visited.add(nxt)
                path.append(nxt)

                backtrack(nxt)

                path.pop()
                visited.remove(nxt)

        backtrack(start)
        return paths

    def shortest_path(
        self,
        start: Position,
        target: Position,
    ) -> list[Position] | None:
        """Breadth-first search gives the shortest path in an unweighted maze."""
        from collections import deque

        if not self.valid(start) or not self.valid(target):
            return None

        queue = deque([start])
        previous: dict[Position, Position | None] = {start: None}
        directions = (
            Position(-1, 0),
            Position(1, 0),
            Position(0, -1),
            Position(0, 1),
        )

        while queue:
            current = queue.popleft()

            if current == target:
                path: list[Position] = []
                node: Position | None = current

                while node is not None:
                    path.append(node)
                    node = previous[node]

                path.reverse()
                return path

            for direction in directions:
                nxt = Position(
                    current.row + direction.row,
                    current.col + direction.col,
                )

                if not self.valid(nxt) or nxt in previous:
                    continue

                previous[nxt] = current
                queue.append(nxt)

        return None

    def render_path(self, path: Iterable[Position]) -> str:
        cells = {p for p in path}

        lines = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                p = Position(r, c)
                if p in cells:
                    row.append("*")
                else:
                    row.append(self.grid[r][c])
            lines.append(" ".join(row))
        return "\n".join(lines)


def validate_n_queens_solution(solution: list[int]) -> bool:
    n = len(solution)
    if n == 0:
        return False

    if any(col < 0 or col >= n for col in solution):
        return False

    if len(set(solution)) != n:
        return False

    down = [row - col for row, col in enumerate(solution)]
    up = [row + col for row, col in enumerate(solution)]

    return len(set(down)) == n and len(set(up)) == n


def demo() -> None:
    print("=== N-Queens ===")
    solver = NQueensSolver(4)
    solutions = solver.solve()

    print(f"4x4 solutions: {len(solutions)}")
    assert len(solutions) == 2
    assert all(validate_n_queens_solution(s) for s in solutions)

    for index, solution in enumerate(solutions, start=1):
        print(f"\nSolution {index}")
        print(solver.render(solution))

    print("\n=== Maze Path Generation ===")
    maze = Maze(
        [
            "...#.",
            ".#...",
            "...#.",
            "#....",
            ".....",
        ]
    )

    start = Position(0, 0)
    target = Position(4, 4)

    paths = maze.all_paths(start, target, max_paths=5)
    print(f"Generated paths: {len(paths)}")

    for index, path in enumerate(paths, start=1):
        print(f"\nPath {index}, length={len(path)}")
        print(maze.render_path(path))

    shortest = maze.shortest_path(start, target)
    if shortest is None:
        print("\nNo shortest path exists.")
    else:
        print(f"\nShortest path length: {len(shortest)}")
        print(maze.render_path(shortest))

    assert shortest is not None
    assert shortest[0] == start
    assert shortest[-1] == target

    print("\n=== Edge Cases ===")
    assert NQueensSolver(1).count() == 1
    assert NQueensSolver(2).count() == 0
    assert NQueensSolver(3).count() == 0

    blocked = Maze([".#", "#."])
    assert blocked.all_paths(Position(0, 0), Position(1, 1)) == []

    print("Validation and edge-case checks passed.")


if __name__ == "__main__":
    demo()
