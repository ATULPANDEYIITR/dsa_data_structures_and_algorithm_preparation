#!/usr/bin/env python3
"""
Graph Fundamentals: Vertices, Edges, Graph Types, and Degree.

Demonstrates:
- Vertices and edges
- Directed and undirected graphs
- Weighted and unweighted graphs
- Adjacency lists and adjacency matrices
- In-degree, out-degree, and undirected degree
- Graph traversal using BFS and DFS
- Connected components
- Cycle detection
- Weighted shortest paths using Dijkstra's algorithm
- Graph validation and serialization

Python 3.10+
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import heapq
import json
from typing import Any, Hashable


Vertex = Hashable


class GraphError(Exception):
    """Base exception for graph-related errors."""


class VertexNotFoundError(GraphError):
    """Raised when an operation references a missing vertex."""


class InvalidEdgeError(GraphError):
    """Raised when an edge has invalid attributes."""


class GraphType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


@dataclass(frozen=True)
class Edge:
    source: Vertex
    target: Vertex
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.weight, (int, float)):
            raise InvalidEdgeError("Edge weight must be numeric.")
        if not float("-inf") < self.weight < float("inf"):
            raise InvalidEdgeError("Edge weight must be finite.")


class Graph:
    """Graph implementation using an adjacency dictionary."""

    def __init__(
        self,
        graph_type: GraphType = GraphType.UNDIRECTED,
        weighted: bool = False,
    ) -> None:
        self.graph_type = graph_type
        self.weighted = weighted
        self._adjacency: dict[Vertex, dict[Vertex, float]] = {}
        self._edge_count = 0

    @property
    def vertices(self) -> tuple[Vertex, ...]:
        return tuple(self._adjacency)

    @property
    def vertex_count(self) -> int:
        return len(self._adjacency)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    def add_vertex(self, vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise GraphError("Vertices must be hashable.") from exc

        if vertex not in self._adjacency:
            self._adjacency[vertex] = {}

    def _require_vertex(self, vertex: Vertex) -> None:
        if vertex not in self._adjacency:
            raise VertexNotFoundError(f"Unknown vertex: {vertex!r}")

    def add_edge(
        self,
        source: Vertex,
        target: Vertex,
        weight: float = 1.0,
    ) -> None:
        edge = Edge(source, target, weight)

        if not self.weighted and edge.weight != 1.0:
            raise InvalidEdgeError(
                "Unweighted graphs only support the default edge weight."
            )

        self.add_vertex(source)
        self.add_vertex(target)

        source_exists = target in self._adjacency[source]

        self._adjacency[source][target] = float(edge.weight)

        if self.graph_type == GraphType.UNDIRECTED:
            self._adjacency[target][source] = float(edge.weight)

        if not source_exists:
            self._edge_count += 1

    def remove_edge(self, source: Vertex, target: Vertex) -> None:
        self._require_vertex(source)
        self._require_vertex(target)

        if target not in self._adjacency[source]:
            raise InvalidEdgeError("Edge does not exist.")

        del self._adjacency[source][target]

        if self.graph_type == GraphType.UNDIRECTED:
            del self._adjacency[target][source]

        self._edge_count -= 1

    def remove_vertex(self, vertex: Vertex) -> None:
        self._require_vertex(vertex)

        outgoing = list(self._adjacency[vertex])

        if self.graph_type == GraphType.DIRECTED:
            incoming = sum(
                vertex in neighbors
                for neighbors in self._adjacency.values()
            )
            self._edge_count -= len(outgoing) + incoming
        else:
            self._edge_count -= len(outgoing)

        del self._adjacency[vertex]

        for neighbors in self._adjacency.values():
            neighbors.pop(vertex, None)

    def neighbors(self, vertex: Vertex) -> dict[Vertex, float]:
        self._require_vertex(vertex)
        return self._adjacency[vertex].copy()

    def degree(self, vertex: Vertex) -> int:
        self._require_vertex(vertex)

        if self.graph_type == GraphType.DIRECTED:
            raise GraphError(
                "Directed graphs require in_degree or out_degree."
            )

        return len(self._adjacency[vertex])

    def in_degree(self, vertex: Vertex) -> int:
        self._require_vertex(vertex)

        if self.graph_type != GraphType.DIRECTED:
            raise GraphError("In-degree applies to directed graphs.")

        return sum(
            vertex in neighbors
            for neighbors in self._adjacency.values()
        )

    def out_degree(self, vertex: Vertex) -> int:
        self._require_vertex(vertex)

        if self.graph_type != GraphType.DIRECTED:
            raise GraphError("Out-degree applies to directed graphs.")

        return len(self._adjacency[vertex])

    def bfs(self, start: Vertex) -> list[Vertex]:
        self._require_vertex(start)

        visited = {start}
        queue = deque([start])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in self._adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def dfs(self, start: Vertex) -> list[Vertex]:
        self._require_vertex(start)

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
                list(self._adjacency[current])
            ):
                if neighbor not in visited:
                    stack.append(neighbor)

        return result

    def connected_components(self) -> list[list[Vertex]]:
        if self.graph_type != GraphType.UNDIRECTED:
            raise GraphError(
                "Connected components require an undirected graph."
            )

        visited = set()
        components = []

        for vertex in self._adjacency:
            if vertex not in visited:
                component = self.bfs(vertex)
                visited.update(component)
                components.append(component)

        return components

    def has_cycle(self) -> bool:
        if self.graph_type == GraphType.UNDIRECTED:
            visited = set()

            def visit(vertex: Vertex, parent: Vertex | None) -> bool:
                visited.add(vertex)

                for neighbor in self._adjacency[vertex]:
                    if neighbor not in visited:
                        if visit(neighbor, vertex):
                            return True
                    elif neighbor != parent:
                        return True

                return False

            for vertex in self._adjacency:
                if vertex not in visited and visit(vertex, None):
                    return True

            return False

        colors: dict[Vertex, int] = {
            vertex: 0 for vertex in self._adjacency
        }

        def visit_directed(vertex: Vertex) -> bool:
            colors[vertex] = 1

            for neighbor in self._adjacency[vertex]:
                if colors[neighbor] == 1:
                    return True

                if colors[neighbor] == 0:
                    if visit_directed(neighbor):
                        return True

            colors[vertex] = 2
            return False

        return any(
            colors[vertex] == 0 and visit_directed(vertex)
            for vertex in self._adjacency
        )

    def dijkstra(
        self,
        start: Vertex,
    ) -> dict[Vertex, float]:
        self._require_vertex(start)

        if any(
            weight < 0
            for neighbors in self._adjacency.values()
            for weight in neighbors.values()
        ):
            raise GraphError(
                "Dijkstra's algorithm does not support negative weights."
            )

        distances = {
            vertex: float("inf")
            for vertex in self._adjacency
        }

        distances[start] = 0.0
        priority_queue = [(0.0, 0, start)]
        sequence = 1

        while priority_queue:
            distance, _, current = heapq.heappop(priority_queue)

            if distance != distances[current]:
                continue

            for neighbor, weight in self._adjacency[current].items():
                new_distance = distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(
                        priority_queue,
                        (new_distance, sequence, neighbor),
                    )
                    sequence += 1

        return distances

    def adjacency_matrix(self) -> tuple[list[Vertex], list[list[float | None]]]:
        vertices = list(self._adjacency)
        index = {vertex: i for i, vertex in enumerate(vertices)}

        matrix = [
            [None] * len(vertices)
            for _ in vertices
        ]

        for source, neighbors in self._adjacency.items():
            for target, weight in neighbors.items():
                matrix[index[source]][index[target]] = weight

        return vertices, matrix

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.graph_type.value,
            "weighted": self.weighted,
            "vertices": list(self._adjacency),
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "weight": weight,
                }
                for source, neighbors in self._adjacency.items()
                for target, weight in neighbors.items()
                if (
                    self.graph_type == GraphType.DIRECTED
                    or repr(source) <= repr(target)
                )
            ],
        }


def demonstrate_undirected_graph() -> None:
    print("\n=== UNDIRECTED UNWEIGHTED GRAPH ===")

    graph = Graph(GraphType.UNDIRECTED)

    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("D", "E"),
    ]

    for source, target in edges:
        graph.add_edge(source, target)

    graph.add_vertex("F")

    print("Vertices:", graph.vertices)
    print("Edges:", graph.edge_count)
    print("Degree of A:", graph.degree("A"))
    print("Degree of D:", graph.degree("D"))
    print("BFS:", graph.bfs("A"))
    print("DFS:", graph.dfs("A"))
    print("Connected components:", graph.connected_components())
    print("Contains cycle:", graph.has_cycle())


def demonstrate_directed_graph() -> None:
    print("\n=== DIRECTED UNWEIGHTED GRAPH ===")

    graph = Graph(GraphType.DIRECTED)

    for source, target in [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("D", "A"),
    ]:
        graph.add_edge(source, target)

    print("Vertices:", graph.vertices)
    print("Edges:", graph.edge_count)

    for vertex in graph.vertices:
        print(
            f"{vertex}: "
            f"in-degree={graph.in_degree(vertex)}, "
            f"out-degree={graph.out_degree(vertex)}"
        )

    print("BFS:", graph.bfs("A"))
    print("Contains cycle:", graph.has_cycle())


def demonstrate_weighted_graph() -> None:
    print("\n=== WEIGHTED UNDIRECTED GRAPH ===")

    graph = Graph(GraphType.UNDIRECTED, weighted=True)

    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("C", "B", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("D", "E", 2),
        ("B", "E", 10),
    ]

    for source, target, weight in edges:
        graph.add_edge(source, target, weight)

    distances = graph.dijkstra("A")

    for vertex, distance in distances.items():
        print(f"Shortest distance A -> {vertex}: {distance}")


def demonstrate_edge_cases() -> None:
    print("\n=== EDGE CASES ===")

    graph = Graph()
    graph.add_vertex("isolated")

    print("Isolated vertex degree:", graph.degree("isolated"))
    print("Isolated vertex traversal:", graph.bfs("isolated"))

    graph.add_edge("X", "Y")
    graph.add_edge("X", "Y")

    print("Duplicate edge count:", graph.edge_count)

    try:
        graph.degree("unknown")
    except VertexNotFoundError as error:
        print("Validation:", error)

    try:
        weighted = Graph(GraphType.DIRECTED, weighted=True)
        weighted.add_edge("A", "B", -5)
        weighted.dijkstra("A")
    except GraphError as error:
        print("Shortest-path validation:", error)


def run_assertions() -> None:
    graph = Graph(GraphType.UNDIRECTED)

    graph.add_edge(1, 2)
    graph.add_edge(2, 3)

    assert graph.vertex_count == 3
    assert graph.edge_count == 2
    assert graph.degree(2) == 2
    assert graph.bfs(1) == [1, 2, 3]
    assert graph.connected_components() == [[1, 2, 3]]
    assert not graph.has_cycle()

    graph.add_edge(3, 1)
    assert graph.has_cycle()

    directed = Graph(GraphType.DIRECTED)
    directed.add_edge("A", "B")
    directed.add_edge("A", "C")
    directed.add_edge("C", "B")

    assert directed.out_degree("A") == 2
    assert directed.in_degree("B") == 2

    weighted = Graph(GraphType.UNDIRECTED, weighted=True)
    weighted.add_edge("A", "B", 3)
    weighted.add_edge("B", "C", 2)

    assert weighted.dijkstra("A")["C"] == 5.0

    print("\nAll assertions passed.")


def main() -> None:
    demonstrate_undirected_graph()
    demonstrate_directed_graph()
    demonstrate_weighted_graph()
    demonstrate_edge_cases()
    run_assertions()

    graph = Graph(GraphType.UNDIRECTED)
    graph.add_edge("server", "database")
    graph.add_edge("server", "cache")

    print("\n=== SERIALIZED GRAPH ===")
    print(json.dumps(graph.to_dict(), indent=2))


if __name__ == "__main__":
    main()
