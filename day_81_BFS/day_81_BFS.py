#!/usr/bin/env python3
"""
Breadth-First Search (BFS)

Covers:
- Graph representation using adjacency lists
- Queue-based graph traversal
- Visited-node tracking
- Shortest paths in unweighted graphs
- Level-order processing
- Multi-source BFS
- Connected components
- Grid traversal
- Cycle-safe traversal
- Input validation and automated tests

Run:
    python bfs.py
"""

from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class BFSResult:
    distances: dict[int, int]
    parents: dict[int, Optional[int]]
    levels: dict[int, list[int]]

    def shortest_path(self, target: int) -> Optional[list[int]]:
        if target not in self.distances:
            return None

        path = []
        current = target

        while current is not None:
            path.append(current)
            current = self.parents[current]

        return path[::-1]


class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self.adjacency: dict[int, list[int]] = {}

    def add_vertex(self, vertex: int) -> None:
        self.adjacency.setdefault(vertex, [])

    def add_edge(self, source: int, destination: int) -> None:
        self.add_vertex(source)
        self.add_vertex(destination)

        self.adjacency[source].append(destination)

        if not self.directed:
            self.adjacency[destination].append(source)

    def validate_vertex(self, vertex: int) -> None:
        if vertex not in self.adjacency:
            raise ValueError(f"Unknown vertex: {vertex}")

    def bfs(self, start: int) -> BFSResult:
        """Perform BFS from one starting vertex."""

        self.validate_vertex(start)

        queue = deque([start])
        distances = {start: 0}
        parents = {start: None}
        levels: dict[int, list[int]] = {0: [start]}

        while queue:
            current = queue.popleft()

            for neighbor in self.adjacency[current]:
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    parents[neighbor] = current

                    level = distances[neighbor]
                    levels.setdefault(level, []).append(neighbor)

                    queue.append(neighbor)

        return BFSResult(distances, parents, levels)

    def multi_source_bfs(self, sources: list[int]) -> BFSResult:
        """
        Perform BFS from multiple starting vertices.

        Each source begins at distance zero.
        """

        if not sources:
            raise ValueError("At least one source is required")

        for source in sources:
            self.validate_vertex(source)

        unique_sources = list(dict.fromkeys(sources))

        queue = deque(unique_sources)
        distances = {source: 0 for source in unique_sources}
        parents = {source: None for source in unique_sources}
        levels: dict[int, list[int]] = {0: unique_sources.copy()}

        while queue:
            current = queue.popleft()

            for neighbor in self.adjacency[current]:
                if neighbor not in distances:
                    distance = distances[current] + 1

                    distances[neighbor] = distance
                    parents[neighbor] = current
                    levels.setdefault(distance, []).append(neighbor)

                    queue.append(neighbor)

        return BFSResult(distances, parents, levels)

    def connected_components(self) -> list[list[int]]:
        """Find connected components in an undirected graph."""

        if self.directed:
            raise ValueError(
                "Connected components require an undirected graph"
            )

        visited = set()
        components = []

        for vertex in self.adjacency:
            if vertex in visited:
                continue

            component = []
            queue = deque([vertex])
            visited.add(vertex)

            while queue:
                current = queue.popleft()
                component.append(current)

                for neighbor in self.adjacency[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

        return components

    def level_order(self, start: int) -> list[list[int]]:
        """Return vertices grouped by BFS level."""

        return self.bfs(start).levels.values() and [
            self.bfs(start).levels[level]
            for level in sorted(self.bfs(start).levels)
        ]


def shortest_path_grid(
    grid: list[list[int]],
    start: tuple[int, int],
    target: tuple[int, int]
) -> Optional[list[tuple[int, int]]]:
    """
    Find the shortest path in a binary grid.

    0 = traversable cell
    1 = blocked cell
    Movement: up, down, left, right.
    """

    if not grid or not grid[0]:
        raise ValueError("Grid cannot be empty")

    rows = len(grid)
    cols = len(grid[0])

    if any(len(row) != cols for row in grid):
        raise ValueError("Grid must be rectangular")

    if any(cell not in (0, 1) for row in grid for cell in row):
        raise ValueError("Grid cells must contain only 0 or 1")

    def valid(position):
        r, c = position
        return (
            0 <= r < rows
            and 0 <= c < cols
            and grid[r][c] == 0
        )

    if not valid(start) or not valid(target):
        return None

    queue = deque([start])
    parents = {start: None}

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    while queue:
        current = queue.popleft()

        if current == target:
            break

        r, c = current

        for dr, dc in directions:
            neighbor = (r + dr, c + dc)

            if valid(neighbor) and neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)

    if target not in parents:
        return None

    path = []
    current = target

    while current is not None:
        path.append(current)
        current = parents[current]

    return path[::-1]


def demonstrate_bfs():
    graph = Graph(directed=False)

    edges = [
        (0, 1), (0, 2),
        (1, 3), (1, 4),
        (2, 5), (2, 6),
        (4, 7), (5, 7)
    ]

    for source, destination in edges:
        graph.add_edge(source, destination)

    print("=== BFS Traversal ===")
    result = graph.bfs(0)

    print("Distances:", result.distances)
    print("Parents:", result.parents)
    print("Levels:", result.levels)
    print("Traversal:", [
        vertex
        for level in result.levels.values()
        for vertex in level
    ])

    print("\n=== Shortest Path ===")
    print("0 to 7:", result.shortest_path(7))

    print("\n=== Multi-Source BFS ===")
    multi = graph.multi_source_bfs([0, 7])
    print("Distances:", multi.distances)
    print("Levels:", multi.levels)

    print("\n=== Connected Components ===")
    graph.add_edge(10, 11)
    print(graph.connected_components())

    print("\n=== Grid BFS ===")
    grid = [
        [0, 0, 0, 1],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0]
    ]

    path = shortest_path_grid(grid, (0, 0), (3, 3))
    print("Grid path:", path)

    print("\n=== Automated Tests ===")

    assert result.distances[0] == 0
    assert result.distances[7] == 3
    assert result.shortest_path(7) is not None
    assert result.shortest_path(99) is None

    assert multi.distances[0] == 0
    assert multi.distances[7] == 0

    assert len(graph.connected_components()) == 2

    assert shortest_path_grid(
        [[0, 0], [0, 0]], (0, 0), (1, 1)
    ) is not None

    assert shortest_path_grid(
        [[0, 1], [1, 0]], (0, 0), (1, 1)
    ) is None

    try:
        graph.bfs(999)
        raise AssertionError("Invalid vertex was accepted")
    except ValueError:
        pass

    try:
        graph.multi_source_bfs([])
        raise AssertionError("Empty sources were accepted")
    except ValueError:
        pass

    print("All tests passed.")


if __name__ == "__main__":
    demonstrate_bfs()
