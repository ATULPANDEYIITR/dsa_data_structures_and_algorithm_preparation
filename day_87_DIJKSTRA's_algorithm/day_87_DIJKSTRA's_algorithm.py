#!/usr/bin/env python3
"""
Dijkstra's Algorithm: Single-Source Shortest Paths

Features:
- Weighted directed and undirected graphs
- Non-negative edge-weight validation
- Priority queue optimization using heapq
- Shortest-distance calculation
- Shortest-path reconstruction
- Unreachable vertex handling
- Multiple shortest paths
- Complexity analysis and executable tests

Time complexity: O((V + E) log V) with a binary heap.
Space complexity: O(V + E).
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Hashable, Optional


Vertex = Hashable


class GraphError(Exception):
    """Base exception for graph-related errors."""


class NegativeWeightError(GraphError):
    """Raised when an edge has a negative weight."""


class VertexNotFoundError(GraphError):
    """Raised when a requested vertex does not exist."""


@dataclass
class ShortestPathResult:
    source: Vertex
    distances: dict[Vertex, float]
    predecessors: dict[Vertex, Optional[Vertex]]

    def path_to(self, destination: Vertex) -> Optional[list[Vertex]]:
        if destination not in self.distances:
            raise VertexNotFoundError(
                f"Unknown destination: {destination}"
            )

        if math.isinf(self.distances[destination]):
            return None

        path = []
        current = destination

        while current is not None:
            path.append(current)
            current = self.predecessors[current]

        path.reverse()
        return path

    def distance_to(self, destination: Vertex) -> float:
        if destination not in self.distances:
            raise VertexNotFoundError(
                f"Unknown destination: {destination}"
            )

        return self.distances[destination]


@dataclass
class WeightedGraph:
    directed: bool = False
    adjacency: dict[Vertex, list[tuple[Vertex, float]]] = field(
        default_factory=dict
    )

    def add_vertex(self, vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise GraphError("Vertices must be hashable") from exc

        self.adjacency.setdefault(vertex, [])

    def add_edge(
        self,
        source: Vertex,
        destination: Vertex,
        weight: float
    ) -> None:
        if isinstance(weight, bool) or not isinstance(
            weight, (int, float)
        ):
            raise ValueError("Edge weight must be numeric")

        weight = float(weight)

        if not math.isfinite(weight):
            raise ValueError("Edge weight must be finite")

        if weight < 0:
            raise NegativeWeightError(
                "Dijkstra's algorithm requires non-negative weights"
            )

        self.add_vertex(source)
        self.add_vertex(destination)

        self.adjacency[source].append((destination, weight))

        if not self.directed:
            self.adjacency[destination].append((source, weight))

    def dijkstra(self, source: Vertex) -> ShortestPathResult:
        if source not in self.adjacency:
            raise VertexNotFoundError(
                f"Unknown source vertex: {source}"
            )

        distances = {
            vertex: math.inf for vertex in self.adjacency
        }

        predecessors = {
            vertex: None for vertex in self.adjacency
        }

        distances[source] = 0.0

        # Entries contain (distance, insertion_counter, vertex).
        # The counter avoids comparing arbitrary vertex objects.
        counter = 0
        priority_queue = [(0.0, counter, source)]

        while priority_queue:
            current_distance, _, current = heapq.heappop(
                priority_queue
            )

            # Ignore outdated entries left by earlier relaxations.
            if current_distance > distances[current]:
                continue

            for neighbor, weight in self.adjacency[current]:
                new_distance = current_distance + weight

                if not math.isfinite(new_distance):
                    raise OverflowError(
                        "Path distance exceeded floating-point range"
                    )

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current

                    counter += 1
                    heapq.heappush(
                        priority_queue,
                        (new_distance, counter, neighbor)
                    )

        return ShortestPathResult(
            source=source,
            distances=distances,
            predecessors=predecessors
        )

    def shortest_path(
        self,
        source: Vertex,
        destination: Vertex
    ) -> tuple[Optional[list[Vertex]], float]:

        result = self.dijkstra(source)

        return (
            result.path_to(destination),
            result.distance_to(destination)
        )


def display_result(
    result: ShortestPathResult
) -> None:
    print(f"\nShortest paths from {result.source}")
    print("-" * 55)

    for vertex, distance in result.distances.items():
        if math.isinf(distance):
            print(f"{vertex}: unreachable")
        else:
            print(
                f"{vertex}: distance={distance:.2f}, "
                f"path={result.path_to(vertex)}"
            )


def build_road_network() -> WeightedGraph:
    graph = WeightedGraph(directed=False)

    roads = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
        ("D", "F", 6),
        ("E", "F", 3),
    ]

    for source, destination, distance in roads:
        graph.add_edge(source, destination, distance)

    graph.add_vertex("G")
    return graph


def run_tests() -> None:
    graph = WeightedGraph(directed=True)

    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 3)
    graph.add_edge("C", "B", 2)
    graph.add_edge("B", "D", 4)
    graph.add_edge("C", "D", 8)

    result = graph.dijkstra("A")

    assert result.distance_to("A") == 0
    assert result.distance_to("B") == 5
    assert result.distance_to("C") == 3
    assert result.distance_to("D") == 9

    assert result.path_to("D") == ["A", "C", "B", "D"]

    # Unreachable vertex.
    graph.add_vertex("Z")
    result = graph.dijkstra("A")

    assert math.isinf(result.distance_to("Z"))
    assert result.path_to("Z") is None

    # Zero-weight edges are valid.
    zero_graph = WeightedGraph(directed=True)
    zero_graph.add_edge("X", "Y", 0)
    zero_graph.add_edge("Y", "Z", 0)

    zero_result = zero_graph.dijkstra("X")

    assert zero_result.distance_to("Z") == 0

    # Negative weights must be rejected.
    try:
        graph.add_edge("A", "Z", -1)
        raise AssertionError("Negative edge was accepted")
    except NegativeWeightError:
        pass

    # Unknown source must be rejected.
    try:
        graph.dijkstra("UNKNOWN")
        raise AssertionError("Unknown source was accepted")
    except VertexNotFoundError:
        pass

    print("All tests passed.")


def main() -> None:
    graph = build_road_network()

    result = graph.dijkstra("A")
    display_result(result)

    print("\nSpecific route:")
    path, distance = graph.shortest_path("A", "F")

    print(f"Route: {path}")
    print(f"Total distance: {distance}")

    print("\nRunning validation tests...")
    run_tests()


if __name__ == "__main__":
    main()
