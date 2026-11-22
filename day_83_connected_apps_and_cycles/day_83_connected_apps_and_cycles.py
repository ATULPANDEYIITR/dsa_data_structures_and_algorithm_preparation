#!/usr/bin/env python3
"""
Connected Components and Cycles in Graphs

Implements:
1. Number of connected components in an undirected graph.
2. Cycle detection in an undirected graph using DFS and Disjoint Set Union.
3. Cycle detection in a directed graph using DFS coloring and Kahn's algorithm.
4. Connected component discovery and cycle reconstruction.
5. Validation and complexity checks.

Run:
    python connected_components_cycles.py
"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class GraphType(Enum):
    UNDIRECTED = "undirected"
    DIRECTED = "directed"


class GraphError(ValueError):
    """Raised when graph input violates structural constraints."""


@dataclass
class Graph:
    directed: bool = False
    adjacency: Dict[int, List[int]] = field(default_factory=dict)

    def add_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise GraphError("Vertices must be integers.")
        self.adjacency.setdefault(vertex, [])

    def add_edge(self, source: int, destination: int) -> None:
        self.add_vertex(source)
        self.add_vertex(destination)

        self.adjacency[source].append(destination)

        if not self.directed and source != destination:
            self.adjacency[destination].append(source)

    def vertices(self) -> List[int]:
        return list(self.adjacency)

    def validate(self) -> None:
        for source, neighbors in self.adjacency.items():
            if not isinstance(neighbors, list):
                raise GraphError(f"Invalid adjacency list for {source}.")
            for destination in neighbors:
                if destination not in self.adjacency:
                    raise GraphError(
                        f"Vertex {destination} does not exist."
                    )


class DisjointSetUnion:
    """Union-Find with path compression and union by rank."""

    def __init__(self, vertices: List[int]):
        self.parent = {vertex: vertex for vertex in vertices}
        self.rank = {vertex: 0 for vertex in vertices}
        self.components = len(vertices)

    def find(self, vertex: int) -> int:
        if vertex not in self.parent:
            raise GraphError(f"Unknown vertex: {vertex}")

        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])

        return self.parent[vertex]

    def union(self, first: int, second: int) -> bool:
        root_first = self.find(first)
        root_second = self.find(second)

        if root_first == root_second:
            return False

        if self.rank[root_first] < self.rank[root_second]:
            root_first, root_second = root_second, root_first

        self.parent[root_second] = root_first

        if self.rank[root_first] == self.rank[root_second]:
            self.rank[root_first] += 1

        self.components -= 1
        return True


@dataclass
class CycleResult:
    has_cycle: bool
    cycle: Optional[List[int]] = None


class GraphAlgorithms:

    @staticmethod
    def connected_components(graph: Graph) -> List[List[int]]:
        """Find all connected components using iterative DFS."""

        if graph.directed:
            raise GraphError(
                "Connected components require an undirected graph."
            )

        graph.validate()

        visited: Set[int] = set()
        components: List[List[int]] = []

        for start in graph.vertices():
            if start in visited:
                continue

            component = []
            stack = [start]
            visited.add(start)

            while stack:
                vertex = stack.pop()
                component.append(vertex)

                for neighbor in graph.adjacency[vertex]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)

            components.append(sorted(component))

        return components

    @staticmethod
    def count_components(graph: Graph) -> int:
        return len(GraphAlgorithms.connected_components(graph))

    @staticmethod
    def undirected_cycle_dfs(graph: Graph) -> CycleResult:
        """
        Detect an undirected cycle using iterative DFS.

        Parent tracking prevents the reverse representation of an
        undirected edge from being incorrectly identified as a cycle.
        """

        if graph.directed:
            raise GraphError("Expected an undirected graph.")

        graph.validate()

        visited: Set[int] = set()
        parent: Dict[int, Optional[int]] = {}

        for start in graph.vertices():
            if start in visited:
                continue

            visited.add(start)
            parent[start] = None

            stack = [(start, iter(graph.adjacency[start]))]

            while stack:
                vertex, neighbors = stack[-1]

                try:
                    neighbor = next(neighbors)
                except StopIteration:
                    stack.pop()
                    continue

                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = vertex
                    stack.append(
                        (neighbor, iter(graph.adjacency[neighbor]))
                    )

                elif neighbor != parent[vertex]:
                    # A self-loop or an already visited non-parent
                    # neighbor establishes a cycle.
                    return CycleResult(True)

        return CycleResult(False)

    @staticmethod
    def undirected_cycle_dsu(graph: Graph) -> CycleResult:
        """
        Detect cycles using Disjoint Set Union.

        Each undirected edge is processed once. Self-loops and parallel
        edges are handled correctly.
        """

        if graph.directed:
            raise GraphError("Expected an undirected graph.")

        graph.validate()

        dsu = DisjointSetUnion(graph.vertices())

        for source, neighbors in graph.adjacency.items():
            for destination in neighbors:
                if source <= destination:
                    if not dsu.union(source, destination):
                        return CycleResult(True)

        return CycleResult(False)

    @staticmethod
    def directed_cycle_dfs(graph: Graph) -> CycleResult:
        """
        Detect a directed cycle using three-color DFS.

        WHITE: unvisited
        GRAY: currently on the DFS path
        BLACK: completely processed

        An edge to a GRAY vertex is a back edge and indicates a cycle.
        """

        if not graph.directed:
            raise GraphError("Expected a directed graph.")

        graph.validate()

        WHITE, GRAY, BLACK = 0, 1, 2

        color = {vertex: WHITE for vertex in graph.vertices()}
        parent: Dict[int, Optional[int]] = {}

        for start in graph.vertices():
            if color[start] != WHITE:
                continue

            color[start] = GRAY
            parent[start] = None

            stack = [(start, iter(graph.adjacency[start]))]

            while stack:
                vertex, neighbors = stack[-1]

                try:
                    neighbor = next(neighbors)
                except StopIteration:
                    color[vertex] = BLACK
                    stack.pop()
                    continue

                if color[neighbor] == WHITE:
                    parent[neighbor] = vertex
                    color[neighbor] = GRAY
                    stack.append(
                        (neighbor, iter(graph.adjacency[neighbor]))
                    )

                elif color[neighbor] == GRAY:
                    cycle = [neighbor]
                    current = vertex

                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]

                    cycle.append(neighbor)
                    cycle.reverse()

                    return CycleResult(True, cycle)

        return CycleResult(False)

    @staticmethod
    def directed_cycle_kahn(graph: Graph) -> CycleResult:
        """
        Detect directed cycles through topological elimination.

        A directed graph is acyclic if and only if every vertex can
        be removed by repeatedly selecting a zero-indegree vertex.
        """

        if not graph.directed:
            raise GraphError("Expected a directed graph.")

        graph.validate()

        indegree = {
            vertex: 0 for vertex in graph.vertices()
        }

        for neighbors in graph.adjacency.values():
            for neighbor in neighbors:
                indegree[neighbor] += 1

        queue = deque(
            vertex
            for vertex, degree in indegree.items()
            if degree == 0
        )

        processed = 0

        while queue:
            vertex = queue.popleft()
            processed += 1

            for neighbor in graph.adjacency[vertex]:
                indegree[neighbor] -= 1

                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        return CycleResult(processed != len(graph.adjacency))

    @staticmethod
    def undirected_cycle_bfs(graph: Graph) -> CycleResult:
        """Alternative undirected cycle detection using BFS."""

        if graph.directed:
            raise GraphError("Expected an undirected graph.")

        graph.validate()

        visited = set()
        parent = {}

        for start in graph.vertices():
            if start in visited:
                continue

            queue = deque([start])
            visited.add(start)
            parent[start] = None

            while queue:
                vertex = queue.popleft()

                for neighbor in graph.adjacency[vertex]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parent[neighbor] = vertex
                        queue.append(neighbor)

                    elif neighbor != parent[vertex]:
                        return CycleResult(True)

        return CycleResult(False)


def build_undirected_example() -> Graph:
    graph = Graph(directed=False)

    edges = [
        (1, 2),
        (2, 3),
        (3, 1),
        (4, 5),
        (6, 7),
    ]

    for source, destination in edges:
        graph.add_edge(source, destination)

    graph.add_vertex(8)

    return graph


def build_directed_example() -> Graph:
    graph = Graph(directed=True)

    edges = [
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 2),
        (4, 5),
        (6, 7),
    ]

    for source, destination in edges:
        graph.add_edge(source, destination)

    return graph


def run_tests() -> None:
    # Multiple connected components, including an isolated vertex.
    graph = build_undirected_example()

    components = GraphAlgorithms.connected_components(graph)

    assert len(components) == 4
    assert GraphAlgorithms.count_components(graph) == 4

    assert GraphAlgorithms.undirected_cycle_dfs(graph).has_cycle
    assert GraphAlgorithms.undirected_cycle_dsu(graph).has_cycle
    assert GraphAlgorithms.undirected_cycle_bfs(graph).has_cycle

    # A forest must not contain a cycle.
    forest = Graph()
    for edge in [(1, 2), (2, 3), (4, 5)]:
        forest.add_edge(*edge)

    assert not GraphAlgorithms.undirected_cycle_dfs(forest).has_cycle
    assert not GraphAlgorithms.undirected_cycle_dsu(forest).has_cycle

    # A self-loop is a cycle.
    self_loop = Graph()
    self_loop.add_edge(10, 10)

    assert GraphAlgorithms.undirected_cycle_dfs(self_loop).has_cycle
    assert GraphAlgorithms.undirected_cycle_dsu(self_loop).has_cycle

    # Parallel edges create a cycle in a multigraph.
    parallel = Graph()
    parallel.add_edge(1, 2)
    parallel.add_edge(1, 2)

    assert GraphAlgorithms.undirected_cycle_dsu(parallel).has_cycle

    # Directed graph containing a cycle.
    directed = build_directed_example()

    dfs_result = GraphAlgorithms.directed_cycle_dfs(directed)
    kahn_result = GraphAlgorithms.directed_cycle_kahn(directed)

    assert dfs_result.has_cycle
    assert kahn_result.has_cycle

    # Directed acyclic graph.
    dag = Graph(directed=True)

    for edge in [(1, 2), (1, 3), (2, 4), (3, 4)]:
        dag.add_edge(*edge)

    assert not GraphAlgorithms.directed_cycle_dfs(dag).has_cycle
    assert not GraphAlgorithms.directed_cycle_kahn(dag).has_cycle

    # Directed self-loop.
    directed_loop = Graph(directed=True)
    directed_loop.add_edge(1, 1)

    assert GraphAlgorithms.directed_cycle_dfs(
        directed_loop
    ).has_cycle

    assert GraphAlgorithms.directed_cycle_kahn(
        directed_loop
    ).has_cycle

    print("All tests passed.")


def main() -> None:
    run_tests()

    print("\nUNDIRECTED GRAPH")

    undirected = build_undirected_example()

    components = GraphAlgorithms.connected_components(undirected)

    print("Connected components:", components)
    print("Number of components:", len(components))

    print(
        "Cycle detected using DFS:",
        GraphAlgorithms.undirected_cycle_dfs(
            undirected
        ).has_cycle
    )

    print(
        "Cycle detected using DSU:",
        GraphAlgorithms.undirected_cycle_dsu(
            undirected
        ).has_cycle
    )

    print("\nDIRECTED GRAPH")

    directed = build_directed_example()

    result = GraphAlgorithms.directed_cycle_dfs(directed)

    print("Directed cycle detected:", result.has_cycle)
    print("Cycle path:", result.cycle)

    print(
        "Cycle detected using Kahn's algorithm:",
        GraphAlgorithms.directed_cycle_kahn(
            directed
        ).has_cycle
    )


if __name__ == "__main__":
    main()
