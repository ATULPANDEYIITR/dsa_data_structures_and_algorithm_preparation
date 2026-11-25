#!/usr/bin/env python3
"""
GRAPH ASSESSMENT
BFS, DFS, Connected Components, Cycle Detection,
Bipartite Graphs, and Topological Sorting.

Runtime: Python 3.10+
Dependencies: Python standard library only.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional


class GraphType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


@dataclass(frozen=True)
class TraversalResult:
    order: tuple[int, ...]
    parent: dict[int, Optional[int]]
    distance: dict[int, int]


@dataclass(frozen=True)
class TopologicalResult:
    order: tuple[int, ...]
    has_cycle: bool


class Graph:
    def __init__(
        self,
        vertices: Iterable[int],
        graph_type: GraphType = GraphType.UNDIRECTED
    ):
        self.vertices = list(vertices)

        if len(self.vertices) != len(set(self.vertices)):
            raise ValueError("Duplicate vertices are not allowed.")

        if not all(isinstance(v, int) and not isinstance(v, bool)
                   for v in self.vertices):
            raise TypeError("Vertices must be integers.")

        self.graph_type = graph_type
        self.adj: dict[int, list[int]] = {
            vertex: [] for vertex in self.vertices
        }
        self.edges: set[tuple[int, int]] = set()

    def _validate_vertex(self, vertex: int) -> None:
        if vertex not in self.adj:
            raise ValueError(f"Unknown vertex: {vertex}")

    def add_edge(self, u: int, v: int) -> None:
        self._validate_vertex(u)
        self._validate_vertex(v)

        edge = (u, v)

        if self.graph_type == GraphType.UNDIRECTED:
            edge = (min(u, v), max(u, v))

        if edge in self.edges:
            return

        self.edges.add(edge)
        self.adj[u].append(v)

        if self.graph_type == GraphType.UNDIRECTED and u != v:
            self.adj[v].append(u)

    def remove_edge(self, u: int, v: int) -> None:
        self._validate_vertex(u)
        self._validate_vertex(v)

        edge = (u, v)

        if self.graph_type == GraphType.UNDIRECTED:
            edge = (min(u, v), max(u, v))

        if edge not in self.edges:
            return

        self.edges.remove(edge)
        self.adj[u].remove(v)

        if self.graph_type == GraphType.UNDIRECTED and u != v:
            self.adj[v].remove(u)

    def bfs(self, start: int) -> TraversalResult:
        """Breadth-first traversal with shortest unweighted distances."""
        self._validate_vertex(start)

        visited = {start}
        parent = {start: None}
        distance = {start: 0}
        order = []

        queue = deque([start])

        while queue:
            vertex = queue.popleft()
            order.append(vertex)

            for neighbor in self.adj[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = vertex
                    distance[neighbor] = distance[vertex] + 1
                    queue.append(neighbor)

        return TraversalResult(
            tuple(order), parent, distance
        )

    def bfs_all(self) -> list[list[int]]:
        """BFS forest covering every connected or reachable region."""
        visited = set()
        groups = []

        for start in self.vertices:
            if start in visited:
                continue

            component = []
            queue = deque([start])
            visited.add(start)

            while queue:
                vertex = queue.popleft()
                component.append(vertex)

                for neighbor in self.adj[vertex]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            groups.append(component)

        return groups

    def dfs(self, start: int) -> TraversalResult:
        """Iterative DFS avoids recursion-depth limitations."""
        self._validate_vertex(start)

        visited = {start}
        parent = {start: None}
        distance = {start: 0}
        order = []

        stack = [start]

        while stack:
            vertex = stack.pop()
            order.append(vertex)

            # Reverse insertion order gives deterministic traversal.
            for neighbor in reversed(self.adj[vertex]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = vertex
                    distance[neighbor] = distance[vertex] + 1
                    stack.append(neighbor)

        return TraversalResult(
            tuple(order), parent, distance
        )

    def connected_components(self) -> list[list[int]]:
        """Connected components are defined for undirected graphs."""
        if self.graph_type != GraphType.UNDIRECTED:
            raise ValueError(
                "Connected components require an undirected graph. "
                "Use strongly connected components for directed graphs."
            )

        return self.bfs_all()

    def has_undirected_cycle(self) -> bool:
        """Detect cycles using DFS and parent tracking."""
        if self.graph_type != GraphType.UNDIRECTED:
            raise ValueError("Undirected cycle detection requires an undirected graph.")

        visited = set()

        for start in self.vertices:
            if start in visited:
                continue

            stack = [(start, None)]
            visited.add(start)

            while stack:
                vertex, parent = stack.pop()

                for neighbor in self.adj[vertex]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append((neighbor, vertex))
                    elif neighbor != parent:
                        return True

        return False

    def has_directed_cycle(self) -> bool:
        """Detect directed cycles using three DFS states."""
        if self.graph_type != GraphType.DIRECTED:
            raise ValueError("Directed cycle detection requires a directed graph.")

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {v: WHITE for v in self.vertices}

        for start in self.vertices:
            if color[start] != WHITE:
                continue

            color[start] = GRAY
            stack = [(start, iter(self.adj[start]))]

            while stack:
                vertex, neighbors = stack[-1]

                try:
                    neighbor = next(neighbors)

                    if color[neighbor] == GRAY:
                        return True

                    if color[neighbor] == WHITE:
                        color[neighbor] = GRAY
                        stack.append(
                            (neighbor, iter(self.adj[neighbor]))
                        )

                except StopIteration:
                    color[vertex] = BLACK
                    stack.pop()

        return False

    def is_bipartite(self) -> tuple[bool, dict[int, int]]:
        """
        Check whether an undirected graph can be colored
        using two colors without adjacent vertices sharing a color.
        """
        if self.graph_type != GraphType.UNDIRECTED:
            raise ValueError("Bipartite checking requires an undirected graph.")

        color: dict[int, int] = {}

        for start in self.vertices:
            if start in color:
                continue

            color[start] = 0
            queue = deque([start])

            while queue:
                vertex = queue.popleft()

                for neighbor in self.adj[vertex]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[vertex]
                        queue.append(neighbor)

                    elif color[neighbor] == color[vertex]:
                        return False, color

        return True, color

    def topological_sort(self) -> TopologicalResult:
        """
        Kahn's algorithm.
        A complete ordering exists only for a directed acyclic graph.
        """
        if self.graph_type != GraphType.DIRECTED:
            raise ValueError("Topological sorting requires a directed graph.")

        indegree = {v: 0 for v in self.vertices}

        for vertex in self.vertices:
            for neighbor in self.adj[vertex]:
                indegree[neighbor] += 1

        queue = deque(
            v for v in self.vertices if indegree[v] == 0
        )

        order = []

        while queue:
            vertex = queue.popleft()
            order.append(vertex)

            for neighbor in self.adj[vertex]:
                indegree[neighbor] -= 1

                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        return TopologicalResult(
            tuple(order),
            len(order) != len(self.vertices)
        )

    def shortest_path(self, start: int, target: int) -> Optional[list[int]]:
        """Recover a shortest path in an unweighted graph."""
        self._validate_vertex(start)
        self._validate_vertex(target)

        result = self.bfs(start)

        if target not in result.parent:
            return None

        path = []
        current = target

        while current is not None:
            path.append(current)
            current = result.parent[current]

        return path[::-1]

    def display(self) -> None:
        print(f"\nGraph type: {self.graph_type.value}")

        for vertex in self.vertices:
            print(f"{vertex}: {self.adj[vertex]}")


def demonstrate_undirected_graph() -> None:
    print("\n" + "=" * 65)
    print("UNDIRECTED GRAPH ASSESSMENT")
    print("=" * 65)

    graph = Graph(range(1, 9))

    edges = [
        (1, 2), (1, 3), (2, 4),
        (3, 4), (5, 6), (7, 8)
    ]

    for u, v in edges:
        graph.add_edge(u, v)

    graph.display()

    bfs = graph.bfs(1)
    print("\nBFS:", bfs.order)
    print("BFS distances:", bfs.distance)

    dfs = graph.dfs(1)
    print("\nDFS:", dfs.order)

    print("\nShortest path 1 -> 4:", graph.shortest_path(1, 4))
    print("Connected components:", graph.connected_components())
    print("Contains cycle:", graph.has_undirected_cycle())

    bipartite, colors = graph.is_bipartite()
    print("Bipartite:", bipartite)
    print("Color assignment:", colors)

    # A self-loop is a cycle and violates bipartiteness.
    graph.add_edge(8, 8)

    print("\nAfter adding self-loop (8, 8):")
    print("Contains cycle:", graph.has_undirected_cycle())
    print("Bipartite:", graph.is_bipartite()[0])


def demonstrate_directed_graph() -> None:
    print("\n" + "=" * 65)
    print("DIRECTED GRAPH ASSESSMENT")
    print("=" * 65)

    graph = Graph(range(1, 7), GraphType.DIRECTED)

    edges = [
        (1, 3), (2, 3), (3, 4),
        (3, 5), (4, 6), (5, 6)
    ]

    for u, v in edges:
        graph.add_edge(u, v)

    graph.display()

    print("\nBFS from 1:", graph.bfs(1).order)
    print("DFS from 1:", graph.dfs(1).order)

    result = graph.topological_sort()

    print("Topological ordering:", result.order)
    print("Contains directed cycle:", result.has_cycle)

    # Adding a back edge creates a directed cycle.
    graph.add_edge(6, 3)

    result = graph.topological_sort()

    print("\nAfter adding edge 6 -> 3:")
    print("Contains directed cycle:", graph.has_directed_cycle())
    print("Topological ordering possible:", not result.has_cycle)


def run_tests() -> None:
    # Undirected graph with two components.
    graph = Graph([1, 2, 3, 4, 5])
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(4, 5)

    assert graph.bfs(1).order == (1, 2, 3)
    assert len(graph.connected_components()) == 2
    assert not graph.has_undirected_cycle()
    assert graph.is_bipartite()[0]
    assert graph.shortest_path(1, 3) == [1, 2, 3]
    assert graph.shortest_path(1, 5) is None

    graph.add_edge(3, 1)
    assert graph.has_undirected_cycle()

    # A triangle is not bipartite.
    assert not graph.is_bipartite()[0]

    # Directed acyclic graph.
    dag = Graph([1, 2, 3, 4], GraphType.DIRECTED)
    dag.add_edge(1, 2)
    dag.add_edge(1, 3)
    dag.add_edge(2, 4)
    dag.add_edge(3, 4)

    topo = dag.topological_sort()

    assert not topo.has_cycle
    position = {v: i for i, v in enumerate(topo.order)}

    for u, v in dag.edges:
        assert position[u] < position[v]

    # Directed cycle.
    dag.add_edge(4, 1)
    assert dag.has_directed_cycle()
    assert dag.topological_sort().has_cycle

    # Isolated vertices.
    isolated = Graph([10, 20, 30])
    assert len(isolated.connected_components()) == 3
    assert isolated.bfs(10).order == (10,)

    # Invalid vertex.
    try:
        graph.bfs(100)
        raise AssertionError("Invalid vertex was accepted.")
    except ValueError:
        pass

    # Invalid operation for graph type.
    try:
        dag.connected_components()
        raise AssertionError("Directed components were accepted.")
    except ValueError:
        pass

    print("\nAll graph assessment tests passed.")


def main() -> None:
    demonstrate_undirected_graph()
    demonstrate_directed_graph()
    run_tests()


if __name__ == "__main__":
    main()
