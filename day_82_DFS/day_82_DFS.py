from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TraversalResult:
    start: int
    order: tuple[int, ...]
    parents: dict[int, int | None]
    depth: dict[int, int]

    @property
    def visited_count(self) -> int:
        return len(self.order)


class Graph:
    """
    Undirected graph implemented using an adjacency list.

    Supports:
    - Recursive Depth-First Search
    - Iterative Depth-First Search
    - Connected component detection
    - Path reconstruction
    - Cycle detection
    - Graph validation
    """

    def __init__(self, vertices: Iterable[int] = ()):
        self.adjacency: dict[int, set[int]] = {}

        for vertex in vertices:
            self.add_vertex(vertex)

    def add_vertex(self, vertex: int) -> None:
        if isinstance(vertex, bool) or not isinstance(vertex, int):
            raise TypeError("Vertex identifiers must be integers.")

        self.adjacency.setdefault(vertex, set())

    def add_edge(self, u: int, v: int) -> None:
        self.add_vertex(u)
        self.add_vertex(v)

        if u == v:
            raise ValueError("Self-loops are not supported.")

        self.adjacency[u].add(v)
        self.adjacency[v].add(u)

    def remove_edge(self, u: int, v: int) -> None:
        if u not in self.adjacency or v not in self.adjacency:
            raise KeyError("Both vertices must exist.")

        if v not in self.adjacency[u]:
            raise ValueError("Edge does not exist.")

        self.adjacency[u].remove(v)
        self.adjacency[v].remove(u)

    def validate_start(self, start: int) -> None:
        if start not in self.adjacency:
            raise ValueError(f"Unknown starting vertex: {start}")

    def recursive_dfs(self, start: int) -> TraversalResult:
        """
        Recursive DFS.

        Time: O(V + E)
        Space: O(V) including recursion and traversal state.
        """

        self.validate_start(start)

        visited = set()
        order = []
        parents = {start: None}
        depth = {start: 0}

        def visit(vertex: int) -> None:
            visited.add(vertex)
            order.append(vertex)

            for neighbor in sorted(self.adjacency[vertex]):
                if neighbor not in visited:
                    parents[neighbor] = vertex
                    depth[neighbor] = depth[vertex] + 1
                    visit(neighbor)

        visit(start)

        return TraversalResult(
            start=start,
            order=tuple(order),
            parents=parents,
            depth=depth,
        )

    def iterative_dfs(self, start: int) -> TraversalResult:
        """
        Iterative DFS using an explicit stack.

        Neighbors are pushed in reverse sorted order so that
        the visitation order matches recursive DFS.

        Time: O(V + E) excluding neighbor sorting.
        Space: O(V).
        """

        self.validate_start(start)

        visited = {start}
        stack = [start]
        order = []
        parents = {start: None}
        depth = {start: 0}

        while stack:
            vertex = stack.pop()
            order.append(vertex)

            for neighbor in sorted(
                self.adjacency[vertex], reverse=True
            ):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parents[neighbor] = vertex
                    depth[neighbor] = depth[vertex] + 1
                    stack.append(neighbor)

        return TraversalResult(
            start=start,
            order=tuple(order),
            parents=parents,
            depth=depth,
        )

    def connected_components(self) -> list[list[int]]:
        """
        Finds every connected component.

        Each component contains vertices reachable from one another.
        Isolated vertices form components of size one.

        Time: O(V + E), excluding sorting.
        """

        visited = set()
        components = []

        for start in sorted(self.adjacency):
            if start in visited:
                continue

            component = []
            stack = [start]
            visited.add(start)

            while stack:
                vertex = stack.pop()
                component.append(vertex)

                for neighbor in sorted(
                    self.adjacency[vertex], reverse=True
                ):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)

            components.append(sorted(component))

        return components

    def reconstruct_path(
        self,
        result: TraversalResult,
        destination: int,
    ) -> list[int] | None:
        if destination not in result.parents:
            return None

        path = []
        current = destination

        while current is not None:
            path.append(current)
            current = result.parents[current]

        return path[::-1]

    def has_cycle(self) -> bool:
        """
        Detects an undirected cycle using DFS and parent tracking.

        A visited neighbor other than the current vertex's parent
        indicates a cycle.
        """

        visited = set()

        def visit(vertex: int, parent: int | None) -> bool:
            visited.add(vertex)

            for neighbor in self.adjacency[vertex]:
                if neighbor not in visited:
                    if visit(neighbor, vertex):
                        return True
                elif neighbor != parent:
                    return True

            return False

        for vertex in self.adjacency:
            if vertex not in visited:
                if visit(vertex, None):
                    return True

        return False

    def display(self) -> None:
        print("\nGraph adjacency list")

        for vertex in sorted(self.adjacency):
            neighbors = sorted(self.adjacency[vertex])
            print(f"{vertex}: {neighbors}")


def demonstrate_graph_traversal() -> None:
    graph = Graph(range(1, 11))

    edges = [
        (1, 2),
        (1, 3),
        (2, 4),
        (2, 5),
        (3, 6),
        (3, 7),
        (5, 8),
        (6, 8),
        (9, 10),
    ]

    for u, v in edges:
        graph.add_edge(u, v)

    graph.display()

    print("\n1. Recursive DFS")

    recursive = graph.recursive_dfs(1)

    print("Traversal:", recursive.order)
    print("Parents:", recursive.parents)
    print("Depth:", recursive.depth)

    print("\n2. Iterative DFS")

    iterative = graph.iterative_dfs(1)

    print("Traversal:", iterative.order)
    print("Parents:", iterative.parents)
    print("Depth:", iterative.depth)

    assert recursive.order == iterative.order

    print("\n3. Path reconstruction")

    path = graph.reconstruct_path(recursive, 8)
    print("Path from 1 to 8:", path)

    print("\n4. Unreachable destination")

    print("Path from 1 to 10:", graph.reconstruct_path(recursive, 10))

    print("\n5. Connected components")

    components = graph.connected_components()

    for index, component in enumerate(components, start=1):
        print(f"Component {index}: {component}")

    print("\n6. Cycle detection")
    print("Contains cycle:", graph.has_cycle())

    print("\n7. Isolated vertex")

    isolated_graph = Graph([100, 200, 300])
    isolated_graph.add_edge(100, 200)

    print("Components:", isolated_graph.connected_components())

    print("\n8. Edge removal")

    graph.remove_edge(5, 8)
    print("Components after removing edge (5, 8):")
    print(graph.connected_components())

    print("\n9. Validation")

    try:
        graph.recursive_dfs(999)
    except ValueError as error:
        print("Expected validation error:", error)

    try:
        graph.add_edge(1, 1)
    except ValueError as error:
        print("Expected edge error:", error)

    print("\n10. Deep graph considerations")

    print(
        "Recursive DFS uses the Python call stack. "
        "For deep graphs, iterative DFS avoids recursion-depth limits."
    )


if __name__ == "__main__":
    demonstrate_graph_traversal()
