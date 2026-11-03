#!/usr/bin/env python3
"""
Tree Diameter Practice Project

Implements and compares:
- Tree height from a selected root
- Diameter using bottom-up dynamic programming
- Longest path through every node
- Diameter using two BFS traversals
- Brute-force diameter verification for small trees

All distances are measured in edges. The number of nodes on a path
is always its edge count plus one.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Tuple, TypeVar


Node = TypeVar("Node", bound=Hashable)


class TreeValidationError(ValueError):
    """Raised when the supplied graph is not a valid tree."""


@dataclass(frozen=True)
class DiameterResult(Generic[Node]):
    root: Node
    height_edges: int
    diameter_edges: int
    endpoint_a: Node
    endpoint_b: Node
    longest_path: Tuple[Node, ...]
    diameter_through_node: Mapping[Node, int]

    @property
    def diameter_nodes(self) -> int:
        return self.diameter_edges + 1


class Tree(Generic[Node]):
    """An immutable-in-structure, undirected, unweighted tree."""

    def __init__(
        self,
        nodes: Iterable[Node],
        edges: Iterable[Tuple[Node, Node]],
    ) -> None:
        self.nodes: List[Node] = list(nodes)

        if not self.nodes:
            raise TreeValidationError("A tree must contain at least one node.")

        if any(node is None for node in self.nodes):
            raise TreeValidationError("Node identifiers cannot be None.")

        try:
            self.node_set = set(self.nodes)
        except TypeError as exc:
            raise TreeValidationError("Every node identifier must be hashable.") from exc

        if len(self.node_set) != len(self.nodes):
            raise TreeValidationError("Node identifiers must be unique.")

        self.adjacency: Dict[Node, List[Node]] = {
            node: [] for node in self.nodes
        }

        edge_count = 0

        for edge in edges:
            try:
                if len(edge) != 2:
                    raise TreeValidationError("Every edge must contain two nodes.")
                first, second = edge
            except (TypeError, ValueError) as exc:
                raise TreeValidationError(
                    "Every edge must be a pair of node identifiers."
                ) from exc

            if first not in self.node_set or second not in self.node_set:
                raise TreeValidationError(
                    f"Edge references an unknown node: {edge!r}"
                )

            if first == second:
                raise TreeValidationError("Self-loops are not allowed.")

            if second in self.adjacency[first]:
                raise TreeValidationError(f"Duplicate edge: {edge!r}")

            self.adjacency[first].append(second)
            self.adjacency[second].append(first)
            edge_count += 1

        if edge_count != len(self.nodes) - 1:
            raise TreeValidationError(
                "A tree with n nodes must contain exactly n - 1 edges."
            )

        self._validate_connectivity_and_acyclicity()

    def _validate_connectivity_and_acyclicity(self) -> None:
        """Iterative traversal avoids recursion-depth failures on long trees."""
        start = self.nodes[0]
        visited = {start}
        stack = [(start, None)]

        while stack:
            current, parent = stack.pop()

            for neighbor in self.adjacency[current]:
                if neighbor == parent:
                    continue

                if neighbor in visited:
                    raise TreeValidationError("The graph contains a cycle.")

                visited.add(neighbor)
                stack.append((neighbor, current))

        if len(visited) != len(self.nodes):
            raise TreeValidationError("The graph is disconnected.")

    def _rooted_order(
        self, root: Node
    ) -> Tuple[Dict[Node, Optional[Node]], Dict[Node, int], List[Node]]:
        if root not in self.node_set:
            raise TreeValidationError(f"Unknown root node: {root!r}")

        parent: Dict[Node, Optional[Node]] = {root: None}
        depth: Dict[Node, int] = {root: 0}
        order: List[Node] = []
        stack = [root]

        while stack:
            current = stack.pop()
            order.append(current)

            for neighbor in self.adjacency[current]:
                if neighbor == parent[current]:
                    continue

                if neighbor in parent:
                    raise TreeValidationError("Unexpected cycle during traversal.")

                parent[neighbor] = current
                depth[neighbor] = depth[current] + 1
                stack.append(neighbor)

        if len(order) != len(self.nodes):
            raise TreeValidationError("The selected root cannot reach every node.")

        return parent, depth, order

    def _dynamic_programming_metrics(
        self, root: Node
    ) -> Tuple[int, int, Dict[Node, int]]:
        """
        Calculate height and longest paths through every node.

        down[u] is the greatest distance from u into its rooted subtree.
        up[u] is the greatest distance from u to a node outside that subtree.

        A path through u uses the two longest branches in distinct
        directions. With one available branch, the path may end at u.
        """
        parent, depth, order = self._rooted_order(root)

        down: Dict[Node, int] = {}
        up: Dict[Node, int] = {root: 0}
        through: Dict[Node, int] = {}

        # Bottom-up pass: calculate the two longest child branches.
        child_first: Dict[Node, int] = {}
        child_second: Dict[Node, int] = {}
        best_child: Dict[Node, Optional[Node]] = {}

        for node in reversed(order):
            first_height = 0
            second_height = 0
            first_child: Optional[Node] = None

            for child in self.adjacency[node]:
                if parent[child] != node:
                    continue

                branch_height = 1 + down[child]

                if branch_height > first_height:
                    second_height = first_height
                    first_height = branch_height
                    first_child = child
                elif branch_height > second_height:
                    second_height = branch_height

            down[node] = first_height
            child_first[node] = first_height
            child_second[node] = second_height
            best_child[node] = first_child

        # Top-down pass: calculate the best path outside each child subtree.
        for node in order:
            branches: List[int] = []

            if parent[node] is not None:
                branches.append(up[node])

            for child in self.adjacency[node]:
                if parent[child] == node:
                    branches.append(1 + down[child])

            branches.sort(reverse=True)
            first = branches[0] if branches else 0
            second = branches[1] if len(branches) > 1 else 0
            through[node] = first + second

            for child in self.adjacency[node]:
                if parent[child] != node:
                    continue

                sibling_height = (
                    child_second[node]
                    if best_child[node] == child
                    else child_first[node]
                )

                # The route from child to an outside node first reaches node.
                up[child] = 1 + max(0, up[node], sibling_height)

        height_edges = max(depth.values())
        diameter_edges = max(through.values())

        return height_edges, diameter_edges, through

    def _bfs(
        self, start: Node
    ) -> Tuple[Dict[Node, int], Dict[Node, Optional[Node]]]:
        distances = {start: 0}
        parent: Dict[Node, Optional[Node]] = {start: None}
        queue = deque([start])

        while queue:
            current = queue.popleft()

            for neighbor in self.adjacency[current]:
                if neighbor in distances:
                    continue

                distances[neighbor] = distances[current] + 1
                parent[neighbor] = current
                queue.append(neighbor)

        return distances, parent

    def diameter_two_sweep(
        self, start: Optional[Node] = None
    ) -> Tuple[int, Node, Node, Tuple[Node, ...]]:
        """
        Find a diameter using two BFS traversals.

        In a tree, a farthest node from any starting node is a diameter
        endpoint. A second BFS from that endpoint finds the diameter.
        """
        if start is None:
            start = self.nodes[0]

        if start not in self.node_set:
            raise TreeValidationError(f"Unknown starting node: {start!r}")

        first_distances, _ = self._bfs(start)
        endpoint_a = max(first_distances, key=first_distances.get)

        second_distances, second_parent = self._bfs(endpoint_a)
        endpoint_b = max(second_distances, key=second_distances.get)

        reverse_path: List[Node] = []
        current: Optional[Node] = endpoint_b

        while current is not None:
            reverse_path.append(current)
            current = second_parent[current]

        path = tuple(reversed(reverse_path))
        return second_distances[endpoint_b], endpoint_a, endpoint_b, path

    def diameter_bruteforce(self) -> int:
        """
        Check every source node with BFS.

        This method is intentionally slower and is useful for verifying
        optimized implementations on small practice trees.
        """
        maximum_distance = 0

        for source in self.nodes:
            distances, _ = self._bfs(source)
            maximum_distance = max(maximum_distance, max(distances.values()))

        return maximum_distance

    def analyze(self, root: Node) -> DiameterResult[Node]:
        height, dp_diameter, through = self._dynamic_programming_metrics(root)

        sweep_diameter, endpoint_a, endpoint_b, path = (
            self.diameter_two_sweep(root)
        )

        if dp_diameter != sweep_diameter:
            raise RuntimeError(
                "Diameter implementations disagree: "
                f"dynamic programming={dp_diameter}, "
                f"two-sweep={sweep_diameter}"
            )

        return DiameterResult(
            root=root,
            height_edges=height,
            diameter_edges=dp_diameter,
            endpoint_a=endpoint_a,
            endpoint_b=endpoint_b,
            longest_path=path,
            diameter_through_node=dict(through),
        )


def run_tests() -> None:
    # A chain has its two end nodes as diameter endpoints.
    chain = Tree(
        nodes=[1, 2, 3, 4, 5],
        edges=[(1, 2), (2, 3), (3, 4), (4, 5)],
    )
    result = chain.analyze(1)
    assert result.height_edges == 4
    assert result.diameter_edges == 4
    assert result.diameter_nodes == 5
    assert chain.diameter_bruteforce() == 4

    # A star has a diameter of two edges when it has at least two leaves.
    star = Tree(
        nodes=["center", "A", "B", "C", "D"],
        edges=[
            ("center", "A"),
            ("center", "B"),
            ("center", "C"),
            ("center", "D"),
        ],
    )
    assert star.analyze("center").diameter_edges == 2
    assert star.analyze("A").diameter_through_node["A"] == 2

    # A single-node tree has zero edges and one node on its diameter.
    singleton = Tree(nodes=["only"], edges=[])
    result = singleton.analyze("only")
    assert result.height_edges == 0
    assert result.diameter_edges == 0
    assert result.diameter_nodes == 1
    assert result.longest_path == ("only",)

    # A balanced tree tests paths passing through an internal node.
    balanced = Tree(
        nodes=[1, 2, 3, 4, 5, 6, 7],
        edges=[
            (1, 2), (1, 3),
            (2, 4), (2, 5),
            (3, 6), (3, 7),
        ],
    )
    result = balanced.analyze(1)
    assert result.height_edges == 2
    assert result.diameter_edges == 4
    assert result.diameter_through_node[1] == 4

    # Invalid structures must be rejected.
    invalid_cases = [
        (["A", "B", "C"], [("A", "B")]),
        (["A", "B", "C"], [("A", "B"), ("B", "C"), ("C", "A")]),
        (["A", "B"], [("A", "A")]),
        (["A", "B"], [("A", "B"), ("A", "B")]),
    ]

    for nodes, edges in invalid_cases:
        try:
            Tree(nodes, edges)
        except TreeValidationError:
            pass
        else:
            raise AssertionError("An invalid tree was accepted.")

    try:
        chain.analyze(999)
    except TreeValidationError:
        pass
    else:
        raise AssertionError("An unknown root was accepted.")


def main() -> None:
    run_tests()

    # Example: organizational escalation hierarchy.
    nodes = [
        "Headquarters",
        "North",
        "South",
        "North-East",
        "North-West",
        "South-Central",
        "South-East",
        "South-West",
    ]

    edges = [
        ("Headquarters", "North"),
        ("Headquarters", "South"),
        ("North", "North-East"),
        ("North", "North-West"),
        ("South", "South-Central"),
        ("South-Central", "South-East"),
        ("South-Central", "South-West"),
    ]

    tree = Tree(nodes, edges)
    result = tree.analyze("Headquarters")

    print("TREE DIAMETER ANALYSIS")
    print("----------------------")
    print(f"Root: {result.root}")
    print(f"Height: {result.height_edges} edges")
    print(
        f"Diameter: {result.diameter_edges} edges, "
        f"{result.diameter_nodes} nodes"
    )
    print(f"Endpoint A: {result.endpoint_a}")
    print(f"Endpoint B: {result.endpoint_b}")
    print("Longest path: " + " -> ".join(result.longest_path))

    print("\nLongest path through each node:")
    for node in nodes:
        print(
            f"{node:18} "
            f"{result.diameter_through_node[node]} edges"
        )

    brute_force = tree.diameter_bruteforce()
    print(f"\nBrute-force verification: {brute_force} edges")
    print("All tests passed.")


if __name__ == "__main__":
    main()
