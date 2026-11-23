#!/usr/bin/env python3
"""
Bipartite Graphs: Two-Coloring, BFS/DFS Coloring, and Bipartite Condition.

Demonstrates:
- Undirected graph representation using adjacency lists.
- Bipartite graph validation using BFS and DFS.
- Two-coloring with colors 0 and 1.
- Detection and reconstruction of odd-length cycles.
- Disconnected graph handling.
- Self-loop and parallel-edge handling.
- Graph construction and validation.
- Complexity analysis and executable assertions.

Run:
    python bipartite_graphs.py
"""

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Color(Enum):
    UNCOLORED = -1
    RED = 0
    BLUE = 1


@dataclass
class BipartiteResult:
    is_bipartite: bool
    colors: list[int]
    odd_cycle: Optional[list[int]]
    algorithm: str

    def describe(self) -> str:
        if self.is_bipartite:
            groups = {
                "RED": [i for i, c in enumerate(self.colors) if c == 0],
                "BLUE": [i for i, c in enumerate(self.colors) if c == 1],
            }
            return (
                f"{self.algorithm}: Bipartite\n"
                f"Two color groups: {groups}"
            )

        return (
            f"{self.algorithm}: Not bipartite\n"
            f"Odd cycle: {self.odd_cycle}"
        )


class Graph:
    """Undirected graph with integer vertices from 0 to V-1."""

    def __init__(self, vertices: int):
        if not isinstance(vertices, int) or isinstance(vertices, bool):
            raise TypeError("Vertex count must be an integer.")
        if vertices < 0:
            raise ValueError("Vertex count cannot be negative.")

        self.vertices = vertices
        self.adjacency: list[list[int]] = [
            [] for _ in range(vertices)
        ]
        self.edge_count = 0

    def _validate_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise TypeError("Vertex must be an integer.")
        if not 0 <= vertex < self.vertices:
            raise ValueError(f"Invalid vertex: {vertex}")

    def add_edge(self, u: int, v: int) -> None:
        """Add an undirected edge."""
        self._validate_vertex(u)
        self._validate_vertex(v)

        self.adjacency[u].append(v)

        if u != v:
            self.adjacency[v].append(u)

        self.edge_count += 1

    def bfs_coloring(self) -> BipartiteResult:
        """
        BFS two-coloring.

        Every uncolored connected component gets a new starting color.
        An edge connecting equally colored vertices proves that the
        graph is not bipartite.
        """
        colors = [Color.UNCOLOR​ED.value if False else -1
                  for _ in range(self.vertices)]
        parent = [-1] * self.vertices
        depth = [0] * self.vertices

        for start in range(self.vertices):
            if colors[start] != -1:
                continue

            colors[start] = 0
            queue = deque([start])

            while queue:
                u = queue.popleft()

                for v in self.adjacency[u]:
                    if colors[v] == -1:
                        colors[v] = 1 - colors[u]
                        parent[v] = u
                        depth[v] = depth[u] + 1
                        queue.append(v)

                    elif colors[v] == colors[u]:
                        cycle = self._reconstruct_odd_cycle(
                            u, v, parent, depth
                        )
                        return BipartiteResult(
                            False, colors, cycle, "BFS"
                        )

        return BipartiteResult(True, colors, None, "BFS")

    @staticmethod
    def _reconstruct_odd_cycle(
        u: int,
        v: int,
        parent: list[int],
        depth: list[int],
    ) -> list[int]:
        """
        Reconstruct a cycle using the BFS parent forest.

        The returned sequence starts and ends at the same vertex.
        """
        a, b = u, v
        path_a = [a]
        path_b = [b]

        while depth[a] > depth[b]:
            a = parent[a]
            path_a.append(a)

        while depth[b] > depth[a]:
            b = parent[b]
            path_b.append(b)

        while a != b:
            a = parent[a]
            b = parent[b]
            path_a.append(a)
            path_b.append(b)

        return path_a + path_b[-2::-1] + [u]

    def dfs_coloring(self) -> BipartiteResult:
        """
        Iterative DFS two-coloring.

        Iterative traversal avoids Python recursion-depth failures.
        """
        colors = [-1] * self.vertices
        parent = [-1] * self.vertices
        depth = [0] * self.vertices

        for start in range(self.vertices):
            if colors[start] != -1:
                continue

            colors[start] = 0
            stack = [start]

            while stack:
                u = stack.pop()

                for v in self.adjacency[u]:
                    if colors[v] == -1:
                        colors[v] = 1 - colors[u]
                        parent[v] = u
                        depth[v] = depth[u] + 1
                        stack.append(v)

                    elif colors[v] == colors[u]:
                        cycle = self._reconstruct_odd_cycle(
                            u, v, parent, depth
                        )
                        return BipartiteResult(
                            False, colors, cycle, "DFS"
                        )

        return BipartiteResult(True, colors, None, "DFS")

    def is_bipartite(self) -> bool:
        """Return the bipartite condition using BFS."""
        return self.bfs_coloring().is_bipartite

    def display(self) -> None:
        print(f"Vertices: {self.vertices}")
        print(f"Edges: {self.edge_count}")
        for vertex, neighbors in enumerate(self.adjacency):
            print(f"{vertex}: {neighbors}")


def demonstrate(name: str, graph: Graph) -> None:
    print(f"\n{'=' * 55}")
    print(name)
    print("=" * 55)

    graph.display()

    bfs = graph.bfs_coloring()
    dfs = graph.dfs_coloring()

    print("\nBFS result:")
    print(bfs.describe())

    print("\nDFS result:")
    print(dfs.describe())

    assert bfs.is_bipartite == dfs.is_bipartite

    if bfs.is_bipartite:
        for u in range(graph.vertices):
            for v in graph.adjacency[u]:
                assert bfs.colors[u] != bfs.colors[v]

    print("\nBFS and DFS agree.")


def run_tests() -> None:
    # Even cycle: 0-1-2-3-0.
    even_cycle = Graph(4)
    for edge in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        even_cycle.add_edge(*edge)

    assert even_cycle.is_bipartite()

    # Odd cycle: triangle.
    odd_cycle = Graph(3)
    for edge in [(0, 1), (1, 2), (2, 0)]:
        odd_cycle.add_edge(*edge)

    assert not odd_cycle.is_bipartite()

    # Disconnected graph with isolated vertices.
    disconnected = Graph(7)
    for edge in [(0, 1), (1, 2), (3, 4)]:
        disconnected.add_edge(*edge)

    assert disconnected.is_bipartite()

    # Self-loop: an immediate odd cycle of length one.
    self_loop = Graph(2)
    self_loop.add_edge(0, 0)

    assert not self_loop.is_bipartite()

    # Tree: every tree is bipartite.
    tree = Graph(6)
    for edge in [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]:
        tree.add_edge(*edge)

    assert tree.is_bipartite()

    # Empty graph.
    empty = Graph(0)
    assert empty.is_bipartite()

    # Parallel edges do not invalidate bipartiteness.
    parallel = Graph(2)
    parallel.add_edge(0, 1)
    parallel.add_edge(0, 1)
    assert parallel.is_bipartite()

    print("\nAll assertions passed.")


def main() -> None:
    print("BIPARTITE GRAPH ANALYSIS")
    print("Two-Coloring | BFS | DFS | Odd-Cycle Detection")

    even = Graph(6)
    for edge in [
        (0, 1), (1, 2), (2, 3),
        (3, 4), (4, 5), (5, 0)
    ]:
        even.add_edge(*edge)

    odd = Graph(5)
    for edge in [
        (0, 1), (1, 2), (2, 0),
        (2, 3), (3, 4)
    ]:
        odd.add_edge(*edge)

    disconnected = Graph(8)
    for edge in [
        (0, 1), (1, 2), (2, 3),
        (4, 5), (5, 6)
    ]:
        disconnected.add_edge(*edge)

    demonstrate("EVEN CYCLE", even)
    demonstrate("ODD CYCLE", odd)
    demonstrate("DISCONNECTED GRAPH", disconnected)

    run_tests()


if __name__ == "__main__":
    main()
