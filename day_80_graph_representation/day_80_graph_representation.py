#!/usr/bin/env python3
"""
Graph Representation: Adjacency Matrix and Adjacency List

Demonstrates:
- Directed and undirected graphs
- Weighted and unweighted edges
- Adjacency matrix representation
- Adjacency list representation
- Vertex and edge operations
- BFS and DFS
- Degree calculations
- Memory estimation
- Representation comparison
- Validation and error handling

Runtime: Python 3.10+
Dependencies: Python standard library only
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from sys import getsizeof
from typing import Optional


class GraphError(Exception):
    """Base exception for graph operations."""


class VertexNotFoundError(GraphError):
    """Raised when a requested vertex does not exist."""


class Representation(Enum):
    MATRIX = "adjacency_matrix"
    LIST = "adjacency_list"


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    weight: float = 1.0


class Graph:
    def __init__(
        self,
        directed: bool = False,
        weighted: bool = False,
    ) -> None:
        self.directed = directed
        self.weighted = weighted
        self.vertices: list[str] = []
        self.matrix: list[list[Optional[float]]] = []
        self.adjacency: dict[str, dict[str, float]] = {}

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex must be a non-empty string.")

        if vertex in self.adjacency:
            return

        self.vertices.append(vertex)
        self.adjacency[vertex] = {}

        for row in self.matrix:
            row.append(None)

        self.matrix.append([None] * len(self.vertices))

    def _validate_vertex(self, vertex: str) -> None:
        if vertex not in self.adjacency:
            raise VertexNotFoundError(f"Unknown vertex: {vertex}")

    def add_edge(
        self,
        source: str,
        target: str,
        weight: float = 1.0,
    ) -> None:
        self._validate_vertex(source)
        self._validate_vertex(target)

        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise ValueError("Edge weight must be numeric.")

        if not float("-inf") < float(weight) < float("inf"):
            raise ValueError("Edge weight must be finite.")

        if not self.weighted and weight != 1:
            raise ValueError("Unweighted graphs only accept weight 1.")

        weight = float(weight)

        self.adjacency[source][target] = weight
        self.matrix[self.vertices.index(source)][
            self.vertices.index(target)
        ] = weight

        if not self.directed:
            self.adjacency[target][source] = weight
            self.matrix[self.vertices.index(target)][
                self.vertices.index(source)
            ] = weight

    def remove_edge(self, source: str, target: str) -> bool:
        self._validate_vertex(source)
        self._validate_vertex(target)

        existed = target in self.adjacency[source]

        self.adjacency[source].pop(target, None)

        i = self.vertices.index(source)
        j = self.vertices.index(target)
        self.matrix[i][j] = None

        if not self.directed:
            self.adjacency[target].pop(source, None)
            self.matrix[j][i] = None

        return existed

    def remove_vertex(self, vertex: str) -> None:
        self._validate_vertex(vertex)

        index = self.vertices.index(vertex)

        del self.adjacency[vertex]

        for neighbors in self.adjacency.values():
            neighbors.pop(vertex, None)

        self.vertices.remove(vertex)
        self.matrix.pop(index)

        for row in self.matrix:
            row.pop(index)

    def has_edge(self, source: str, target: str) -> bool:
        self._validate_vertex(source)
        self._validate_vertex(target)

        return self.matrix[
            self.vertices.index(source)
        ][self.vertices.index(target)] is not None

    def get_weight(
        self,
        source: str,
        target: str,
    ) -> Optional[float]:
        self._validate_vertex(source)
        self._validate_vertex(target)

        return self.matrix[
            self.vertices.index(source)
        ][self.vertices.index(target)]

    def neighbors(self, vertex: str) -> list[str]:
        self._validate_vertex(vertex)
        return list(self.adjacency[vertex])

    def degree(self, vertex: str) -> int:
        self._validate_vertex(vertex)

        if not self.directed:
            return len(self.adjacency[vertex])

        return (
            self.in_degree(vertex)
            + self.out_degree(vertex)
        )

    def in_degree(self, vertex: str) -> int:
        self._validate_vertex(vertex)

        return sum(
            vertex in neighbors
            for neighbors in self.adjacency.values()
        )

    def out_degree(self, vertex: str) -> int:
        self._validate_vertex(vertex)
        return len(self.adjacency[vertex])

    def edge_count(self) -> int:
        total = sum(
            len(neighbors)
            for neighbors in self.adjacency.values()
        )

        return total if self.directed else total // 2 + sum(
            1 for v in self.vertices
            if v in self.adjacency[v]
        ) // 2

    def bfs(self, start: str) -> list[str]:
        self._validate_vertex(start)

        visited = {start}
        queue = deque([start])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in self.adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def dfs(self, start: str) -> list[str]:
        self._validate_vertex(start)

        visited = set()
        result = []
        stack = [start]

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            result.append(current)

            for neighbor in reversed(
                list(self.adjacency[current])
            ):
                if neighbor not in visited:
                    stack.append(neighbor)

        return result

    def to_matrix(self) -> list[list[Optional[float]]]:
        return [row.copy() for row in self.matrix]

    def to_adjacency_list(self) -> dict[str, dict[str, float]]:
        return {
            vertex: neighbors.copy()
            for vertex, neighbors in self.adjacency.items()
        }

    def display_matrix(self) -> None:
        print("\nADJACENCY MATRIX")

        print("     " + " ".join(
            f"{v:>8}" for v in self.vertices
        ))

        for vertex, row in zip(self.vertices, self.matrix):
            values = [
                "-" if value is None else str(value)
                for value in row
            ]

            print(
                f"{vertex:>5} "
                + " ".join(f"{value:>8}" for value in values)
            )

    def display_list(self) -> None:
        print("\nADJACENCY LIST")

        for vertex, neighbors in self.adjacency.items():
            connections = [
                f"{neighbor}({weight})"
                for neighbor, weight in neighbors.items()
            ]

            print(f"{vertex}: {', '.join(connections) or 'None'}")

    def matrix_memory_estimate(self) -> int:
        """Estimate shallow Python container memory, not process RSS."""
        total = getsizeof(self.matrix)

        for row in self.matrix:
            total += getsizeof(row)

        return total

    def list_memory_estimate(self) -> int:
        """Estimate shallow container memory for adjacency dictionaries."""
        total = getsizeof(self.adjacency)

        for vertex, neighbors in self.adjacency.items():
            total += getsizeof(vertex)
            total += getsizeof(neighbors)

            for neighbor, weight in neighbors.items():
                total += getsizeof(neighbor)
                total += getsizeof(weight)

        return total

    def statistics(self) -> dict[str, int | float]:
        vertex_count = len(self.vertices)
        edges = self.edge_count()

        return {
            "vertices": vertex_count,
            "edges": edges,
            "matrix_cells": vertex_count ** 2,
            "list_entries": sum(
                len(neighbors)
                for neighbors in self.adjacency.values()
            ),
            "density": (
                edges / (
                    vertex_count * (vertex_count - 1)
                    if self.directed
                    else vertex_count * (vertex_count - 1) / 2
                )
                if vertex_count > 1
                else 0.0
            ),
        }


def compare_representations(graph: Graph) -> None:
    stats = graph.statistics()

    print("\nREPRESENTATION COMPARISON")
    print("-" * 48)

    print(f"Vertices: {stats['vertices']}")
    print(f"Edges: {stats['edges']}")
    print(f"Matrix cells: {stats['matrix_cells']}")
    print(f"Adjacency-list entries: {stats['list_entries']}")
    print(f"Graph density: {stats['density']:.4f}")

    print(
        "Matrix shallow memory estimate:",
        graph.matrix_memory_estimate(),
        "bytes",
    )

    print(
        "List shallow memory estimate:",
        graph.list_memory_estimate(),
        "bytes",
    )

    print("\nTHEORETICAL COMPLEXITY")
    print("Operation             Matrix       List")
    print("Space                 O(V^2)       O(V + E)")
    print("Check edge            O(1)         O(degree)")
    print("Find neighbors        O(V)         O(1) + O(degree)")
    print("Add edge              O(1)         O(1) average")
    print("Remove edge           O(1)         O(1) average")
    print("Iterate neighbors     O(V)         O(degree)")
    print("BFS / DFS             O(V^2)       O(V + E)")


def build_sample_graph() -> Graph:
    graph = Graph(directed=False, weighted=True)

    for vertex in ["A", "B", "C", "D", "E", "F"]:
        graph.add_vertex(vertex)

    edges = [
        Edge("A", "B", 4),
        Edge("A", "C", 2),
        Edge("B", "C", 1),
        Edge("B", "D", 5),
        Edge("C", "D", 8),
        Edge("C", "E", 10),
        Edge("D", "E", 2),
        Edge("D", "F", 6),
        Edge("E", "F", 3),
    ]

    for edge in edges:
        graph.add_edge(
            edge.source,
            edge.target,
            edge.weight,
        )

    return graph


def run_tests() -> None:
    graph = Graph()

    for vertex in ["A", "B", "C"]:
        graph.add_vertex(vertex)

    graph.add_edge("A", "B")

    assert graph.has_edge("A", "B")
    assert graph.has_edge("B", "A")
    assert not graph.has_edge("A", "C")
    assert graph.degree("A") == 1
    assert graph.edge_count() == 1

    assert graph.remove_edge("A", "B")
    assert not graph.has_edge("A", "B")

    directed = Graph(directed=True)

    directed.add_vertex("X")
    directed.add_vertex("Y")
    directed.add_edge("X", "Y")

    assert directed.out_degree("X") == 1
    assert directed.in_degree("Y") == 1
    assert not directed.has_edge("Y", "X")

    directed.remove_vertex("Y")
    assert directed.vertices == ["X"]

    try:
        graph.add_edge("A", "UNKNOWN")
    except VertexNotFoundError:
        pass
    else:
        raise AssertionError("Unknown vertex validation failed.")

    try:
        graph.add_vertex("")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty vertex validation failed.")

    print("All tests passed.")


def main() -> None:
    run_tests()

    graph = build_sample_graph()

    graph.display_matrix()
    graph.display_list()

    print("\nGRAPH TRAVERSALS")
    print("BFS from A:", graph.bfs("A"))
    print("DFS from A:", graph.dfs("A"))

    print("\nVERTEX INFORMATION")

    for vertex in graph.vertices:
        print(
            f"{vertex}: neighbors={graph.neighbors(vertex)}, "
            f"degree={graph.degree(vertex)}"
        )

    compare_representations(graph)

    print("\nEDGE REMOVAL")
    print("Removed C-E:", graph.remove_edge("C", "E"))
    print("C neighbors after removal:", graph.neighbors("C"))

    print("\nVERTEX REMOVAL")
    graph.remove_vertex("F")
    print("Remaining vertices:", graph.vertices)


if __name__ == "__main__":
    main()
