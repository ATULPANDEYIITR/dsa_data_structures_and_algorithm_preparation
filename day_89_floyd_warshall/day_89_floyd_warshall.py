#!/usr/bin/env python3
"""
Floyd-Warshall Algorithm
All-Pairs Shortest Paths using Dynamic Programming.

Features:
- Directed and undirected weighted graphs
- All-pairs shortest paths
- Intermediate vertex processing
- Distance matrix
- Path reconstruction
- Negative edge weights
- Negative cycle detection
- Input validation
- Complexity analysis through implementation
- Unit-style assertions
"""

from dataclasses import dataclass
from math import inf
from typing import Optional


@dataclass
class Graph:
    vertices: int
    directed: bool = True

    def __post_init__(self):
        if not isinstance(self.vertices, int) or isinstance(self.vertices, bool):
            raise TypeError("Vertex count must be an integer.")

        if self.vertices <= 0:
            raise ValueError("A graph must contain at least one vertex.")

        self.distance = [
            [inf] * self.vertices for _ in range(self.vertices)
        ]

        self.next_vertex = [
            [None] * self.vertices for _ in range(self.vertices)
        ]

        for vertex in range(self.vertices):
            self.distance[vertex][vertex] = 0
            self.next_vertex[vertex][vertex] = vertex

        self.computed = False

    def add_edge(self, source: int, destination: int, weight: float):
        if not isinstance(source, int) or isinstance(source, bool):
            raise TypeError("Source must be an integer.")

        if not isinstance(destination, int) or isinstance(destination, bool):
            raise TypeError("Destination must be an integer.")

        if not 0 <= source < self.vertices:
            raise ValueError("Invalid source vertex.")

        if not 0 <= destination < self.vertices:
            raise ValueError("Invalid destination vertex.")

        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise TypeError("Edge weight must be numeric.")

        if not float("-inf") < weight < float("inf"):
            raise ValueError("Edge weight must be finite.")

        weight = float(weight)

        # Retain the minimum weight when parallel edges exist.
        if weight < self.distance[source][destination]:
            self.distance[source][destination] = weight
            self.next_vertex[source][destination] = destination

        if not self.directed:
            if weight < self.distance[destination][source]:
                self.distance[destination][source] = weight
                self.next_vertex[destination][source] = source

        self.computed = False

    def floyd_warshall(self):
        """
        Dynamic programming recurrence:

        D[k][i][j] = min(
            D[k-1][i][j],
            D[k-1][i][k] + D[k-1][k][j]
        )

        The intermediate vertex k is progressively allowed
        in shortest paths.

        Time complexity: O(V^3)
        Space complexity: O(V^2)
        """

        n = self.vertices

        for k in range(n):
            for i in range(n):

                # An unreachable i -> k path cannot improve i -> j.
                if self.distance[i][k] == inf:
                    continue

                for j in range(n):
                    if self.distance[k][j] == inf:
                        continue

                    candidate = (
                        self.distance[i][k] +
                        self.distance[k][j]
                    )

                    if candidate < self.distance[i][j]:
                        self.distance[i][j] = candidate
                        self.next_vertex[i][j] = (
                            self.next_vertex[i][k]
                        )

        self.computed = True

        self.detect_negative_cycles()

        return self.distance

    def detect_negative_cycles(self):
        if not self.computed:
            raise RuntimeError("Run Floyd-Warshall first.")

        negative_vertices = [
            vertex
            for vertex in range(self.vertices)
            if self.distance[vertex][vertex] < 0
        ]

        if negative_vertices:
            raise ValueError(
                f"Negative-weight cycle detected at vertices: "
                f"{negative_vertices}"
            )

        return False

    def shortest_distance(self, source: int, destination: int):
        self._validate_vertex(source)
        self._validate_vertex(destination)

        if not self.computed:
            raise RuntimeError("Run Floyd-Warshall first.")

        return self.distance[source][destination]

    def shortest_path(self, source: int, destination: int):
        self._validate_vertex(source)
        self._validate_vertex(destination)

        if not self.computed:
            raise RuntimeError("Run Floyd-Warshall first.")

        if self.distance[source][destination] == inf:
            return None

        path = [source]
        current = source

        # A simple shortest path contains at most V vertices
        # when no negative cycle exists.
        for _ in range(self.vertices):
            if current == destination:
                return path

            current = self.next_vertex[current][destination]

            if current is None:
                return None

            path.append(current)

        raise RuntimeError("Path reconstruction exceeded graph size.")

    def _validate_vertex(self, vertex):
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise TypeError("Vertex must be an integer.")

        if not 0 <= vertex < self.vertices:
            raise ValueError("Vertex outside graph boundaries.")

    def print_matrix(self):
        if not self.computed:
            raise RuntimeError("Run Floyd-Warshall first.")

        print("\nAll-Pairs Shortest Distance Matrix")

        print("     " + " ".join(
            f"{i:>7}" for i in range(self.vertices)
        ))

        for i, row in enumerate(self.distance):
            values = [
                "INF" if value == inf else f"{value:g}"
                for value in row
            ]

            print(f"{i:>4} " + " ".join(
                f"{value:>7}" for value in values
            ))


def demonstrate_dynamic_programming():
    print("FLOYD-WARSHALL ALGORITHM")
    print("=" * 50)

    graph = Graph(5, directed=True)

    edges = [
        (0, 1, 3),
        (0, 2, 8),
        (0, 4, -4),
        (1, 3, 1),
        (1, 4, 7),
        (2, 1, 4),
        (3, 0, 2),
        (3, 2, -5),
        (4, 3, 6),
    ]

    for source, destination, weight in edges:
        graph.add_edge(source, destination, weight)

    print("\nInitial distance matrix:")
    for row in graph.distance:
        print(row)

    graph.floyd_warshall()

    graph.print_matrix()

    print("\nShortest Path Queries")

    queries = [
        (0, 2),
        (0, 3),
        (1, 2),
        (2, 4),
        (4, 2),
    ]

    for source, destination in queries:
        distance = graph.shortest_distance(source, destination)
        path = graph.shortest_path(source, destination)

        if path is None:
            print(f"{source} -> {destination}: Unreachable")
        else:
            print(
                f"{source} -> {destination}: "
                f"Distance = {distance:g}, "
                f"Path = {' -> '.join(map(str, path))}"
            )


def demonstrate_edge_cases():
    print("\nEDGE CASE TESTS")
    print("=" * 50)

    # Single vertex.
    single = Graph(1)
    single.floyd_warshall()
    assert single.shortest_distance(0, 0) == 0

    # Disconnected vertices.
    disconnected = Graph(3)
    disconnected.add_edge(0, 1, 5)
    disconnected.floyd_warshall()

    assert disconnected.shortest_distance(0, 2) == inf
    assert disconnected.shortest_path(0, 2) is None

    # Negative edge without a negative cycle.
    negative = Graph(3)
    negative.add_edge(0, 1, 4)
    negative.add_edge(1, 2, -6)
    negative.add_edge(0, 2, 3)
    negative.floyd_warshall()

    assert negative.shortest_distance(0, 2) == -2
    assert negative.shortest_path(0, 2) == [0, 1, 2]

    # Parallel edges.
    parallel = Graph(2)
    parallel.add_edge(0, 1, 10)
    parallel.add_edge(0, 1, 3)
    parallel.floyd_warshall()

    assert parallel.shortest_distance(0, 1) == 3

    # Negative cycle detection.
    negative_cycle = Graph(3)
    negative_cycle.add_edge(0, 1, 1)
    negative_cycle.add_edge(1, 2, -3)
    negative_cycle.add_edge(2, 0, 1)

    try:
        negative_cycle.floyd_warshall()
        raise AssertionError("Negative cycle was not detected.")
    except ValueError as error:
        print(f"Expected negative-cycle error: {error}")

    print("All edge-case assertions passed.")


def main():
    demonstrate_dynamic_programming()
    demonstrate_edge_cases()


if __name__ == "__main__":
    main()
