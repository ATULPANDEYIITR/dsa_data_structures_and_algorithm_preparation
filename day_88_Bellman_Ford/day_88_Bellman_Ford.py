#!/usr/bin/env python3
"""
Bellman-Ford Shortest Path Algorithm
------------------------------------
Demonstrates:
1. Edge relaxation
2. Negative edge weights
3. Negative-cycle detection
4. Shortest-path reconstruction
5. Unreachable vertices
6. Early termination
7. Comparison with Dijkstra's algorithm

Python standard library only.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import heapq


class GraphError(ValueError):
    """Raised when graph input is invalid."""


class Algorithm(Enum):
    BELLMAN_FORD = "Bellman-Ford"
    DIJKSTRA = "Dijkstra"


@dataclass(frozen=True)
class Edge:
    source: int
    destination: int
    weight: int


@dataclass
class ShortestPathResult:
    source: int
    distances: dict[int, Optional[int]]
    predecessors: dict[int, Optional[int]]
    negative_cycle: bool
    affected_vertices: set[int]
    iterations: int
    algorithm: Algorithm

    def path_to(self, destination: int) -> Optional[list[int]]:
        """Reconstruct a shortest path when one is well-defined."""
        if destination not in self.distances:
            raise GraphError(f"Unknown destination: {destination}")

        if self.distances[destination] is None:
            return None

        if destination in self.affected_vertices:
            raise GraphError(
                "Shortest path is undefined because a reachable "
                "negative cycle affects this vertex."
            )

        path = []
        current = destination
        visited = set()

        while current is not None:
            if current in visited:
                raise GraphError("Predecessor cycle detected.")

            visited.add(current)
            path.append(current)
            current = self.predecessors[current]

        path.reverse()

        if not path or path[0] != self.source:
            return None

        return path


class WeightedGraph:
    """Directed weighted graph using an adjacency list and edge list."""

    def __init__(self, vertices: list[int]):
        if not vertices:
            raise GraphError("A graph must contain at least one vertex.")

        if len(vertices) != len(set(vertices)):
            raise GraphError("Duplicate vertex identifiers are not allowed.")

        self.vertices = list(vertices)
        self.vertex_set = set(vertices)
        self.edges: list[Edge] = []
        self.adjacency: dict[int, list[tuple[int, int]]] = {
            vertex: [] for vertex in vertices
        }

    def add_edge(self, source: int, destination: int, weight: int) -> None:
        if source not in self.vertex_set:
            raise GraphError(f"Unknown source vertex: {source}")

        if destination not in self.vertex_set:
            raise GraphError(f"Unknown destination vertex: {destination}")

        if isinstance(weight, bool) or not isinstance(weight, int):
            raise GraphError("Edge weights must be integers.")

        edge = Edge(source, destination, weight)

        self.edges.append(edge)
        self.adjacency[source].append((destination, weight))

    def _validate_source(self, source: int) -> None:
        if source not in self.vertex_set:
            raise GraphError(f"Unknown source vertex: {source}")

    def bellman_ford(self, source: int) -> ShortestPathResult:
        """
        Calculate shortest distances using V-1 relaxation passes.

        Complexity:
            Time: O(V * E)
            Space: O(V + E)

        Negative-cycle detection only considers cycles reachable
        from the specified source.
        """
        self._validate_source(source)

        distances: dict[int, Optional[int]] = {
            vertex: None for vertex in self.vertices
        }

        predecessors: dict[int, Optional[int]] = {
            vertex: None for vertex in self.vertices
        }

        distances[source] = 0
        iterations = 0

        # Relax every edge at most V-1 times.
        for _ in range(len(self.vertices) - 1):
            changed = False
            iterations += 1

            for edge in self.edges:
                current_distance = distances[edge.source]

                if current_distance is None:
                    continue

                candidate = current_distance + edge.weight
                old_distance = distances[edge.destination]

                if old_distance is None or candidate < old_distance:
                    distances[edge.destination] = candidate
                    predecessors[edge.destination] = edge.source
                    changed = True

            # No improvement means all reachable shortest paths
            # have already converged.
            if not changed:
                break

        # Identify vertices whose distances can still improve.
        affected = set()

        for edge in self.edges:
            current_distance = distances[edge.source]

            if current_distance is None:
                continue

            candidate = current_distance + edge.weight
            old_distance = distances[edge.destination]

            if old_distance is None or candidate < old_distance:
                affected.add(edge.destination)

        # Propagate negative-cycle influence to every downstream vertex.
        queue = list(affected)

        while queue:
            current = queue.pop()

            for neighbor, _ in self.adjacency[current]:
                if neighbor not in affected:
                    affected.add(neighbor)
                    queue.append(neighbor)

        return ShortestPathResult(
            source=source,
            distances=distances,
            predecessors=predecessors,
            negative_cycle=bool(affected),
            affected_vertices=affected,
            iterations=iterations,
            algorithm=Algorithm.BELLMAN_FORD,
        )

    def dijkstra(self, source: int) -> ShortestPathResult:
        """
        Calculate shortest paths using a min-priority queue.

        Negative weights are rejected because Dijkstra's greedy
        finalization strategy requires nonnegative edge weights.

        Complexity:
            Time: O((V + E) log V)
            Space: O(V + E)
        """
        self._validate_source(source)

        if any(edge.weight < 0 for edge in self.edges):
            raise GraphError(
                "Dijkstra cannot safely process negative edge weights. "
                "Use Bellman-Ford instead."
            )

        distances: dict[int, Optional[int]] = {
            vertex: None for vertex in self.vertices
        }

        predecessors: dict[int, Optional[int]] = {
            vertex: None for vertex in self.vertices
        }

        distances[source] = 0
        priority_queue = [(0, source)]
        iterations = 0

        while priority_queue:
            current_distance, current = heapq.heappop(priority_queue)
            iterations += 1

            # Ignore outdated priority-queue entries.
            if current_distance != distances[current]:
                continue

            for neighbor, weight in self.adjacency[current]:
                candidate = current_distance + weight
                old_distance = distances[neighbor]

                if old_distance is None or candidate < old_distance:
                    distances[neighbor] = candidate
                    predecessors[neighbor] = current

                    heapq.heappush(
                        priority_queue,
                        (candidate, neighbor)
                    )

        return ShortestPathResult(
            source=source,
            distances=distances,
            predecessors=predecessors,
            negative_cycle=False,
            affected_vertices=set(),
            iterations=iterations,
            algorithm=Algorithm.DIJKSTRA,
        )


def display_result(graph: WeightedGraph, result: ShortestPathResult) -> None:
    print(f"\nAlgorithm: {result.algorithm.value}")
    print(f"Source vertex: {result.source}")
    print(f"Iterations: {result.iterations}")
    print(f"Reachable negative cycle: {result.negative_cycle}")

    print("\nShortest path results:")
    print("-" * 65)
    print(f"{'Vertex':<12}{'Distance':<18}{'Path'}")
    print("-" * 65)

    for vertex in graph.vertices:
        if vertex in result.affected_vertices:
            distance = "Undefined (-cycle)"
            path = "Undefined"
        elif result.distances[vertex] is None:
            distance = "Unreachable"
            path = "None"
        else:
            distance = str(result.distances[vertex])
            path = " -> ".join(
                map(str, result.path_to(vertex) or [])
            )

        print(f"{vertex:<12}{distance:<18}{path}")

    print("-" * 65)


def demonstrate_negative_edges() -> None:
    print("\n========== NEGATIVE EDGE EXAMPLE ==========")

    graph = WeightedGraph([0, 1, 2, 3, 4, 5])

    edges = [
        (0, 1, 4),
        (0, 2, 5),
        (1, 2, -2),
        (1, 3, 6),
        (2, 3, 3),
        (3, 4, 2),
        (4, 1, 1),
    ]

    for edge in edges:
        graph.add_edge(*edge)

    result = graph.bellman_ford(0)
    display_result(graph, result)

    assert result.distances[0] == 0
    assert result.distances[1] == 4
    assert result.distances[2] == 2
    assert result.distances[3] == 5
    assert result.distances[4] == 7
    assert result.distances[5] is None
    assert not result.negative_cycle

    print("Negative-edge validation passed.")

    try:
        graph.dijkstra(0)
    except GraphError as error:
        print(f"Dijkstra correctly rejected the graph: {error}")


def demonstrate_negative_cycle() -> None:
    print("\n========== NEGATIVE CYCLE EXAMPLE ==========")

    graph = WeightedGraph([0, 1, 2, 3, 4, 5])

    edges = [
        (0, 1, 2),
        (1, 2, 2),
        (2, 3, -5),
        (3, 1, 1),
        (3, 4, 3),
        (5, 5, -1),
    ]

    for edge in edges:
        graph.add_edge(*edge)

    result = graph.bellman_ford(0)
    display_result(graph, result)

    assert result.negative_cycle
    assert {1, 2, 3, 4}.issubset(result.affected_vertices)
    assert 5 not in result.affected_vertices

    print("Reachable negative-cycle detection passed.")
    print("Unreachable negative cycle correctly ignored.")


def demonstrate_dijkstra_comparison() -> None:
    print("\n========== DIJKSTRA COMPARISON ==========")

    graph = WeightedGraph([0, 1, 2, 3, 4])

    edges = [
        (0, 1, 10),
        (0, 2, 3),
        (2, 1, 2),
        (1, 3, 4),
        (2, 3, 8),
        (2, 4, 2),
        (4, 3, 1),
    ]

    for edge in edges:
        graph.add_edge(*edge)

    bellman_result = graph.bellman_ford(0)
    dijkstra_result = graph.dijkstra(0)

    display_result(graph, bellman_result)
    display_result(graph, dijkstra_result)

    assert bellman_result.distances == dijkstra_result.distances

    print("Both algorithms produced identical distances.")


def demonstrate_validation() -> None:
    print("\n========== INPUT VALIDATION ==========")

    try:
        graph = WeightedGraph([0, 1])
        graph.add_edge(0, 2, 5)
    except GraphError as error:
        print(f"Invalid vertex detected: {error}")

    try:
        graph = WeightedGraph([0, 1])
        graph.add_edge(0, 1, 2.5)
    except GraphError as error:
        print(f"Invalid weight detected: {error}")

    try:
        WeightedGraph([0, 1]).bellman_ford(9)
    except GraphError as error:
        print(f"Invalid source detected: {error}")


def main() -> None:
    demonstrate_negative_edges()
    demonstrate_negative_cycle()
    demonstrate_dijkstra_comparison()
    demonstrate_validation()

    print("\nAll Bellman-Ford demonstrations completed successfully.")


if __name__ == "__main__":
    main()
