from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Optional, Iterable


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    parent: Optional["TreeNode"] = field(default=None, repr=False)

    def attach_left(self, child: Optional["TreeNode"]) -> None:
        self._attach(child, "left")

    def attach_right(self, child: Optional["TreeNode"]) -> None:
        self._attach(child, "right")

    def _attach(self, child: Optional["TreeNode"], side: str) -> None:
        if child is self:
            raise ValueError("A node cannot be its own child.")

        if child is not None:
            current = self
            while current is not None:
                if current is child:
                    raise ValueError("Attaching this node would create a cycle.")
                current = current.parent

            if child.parent is not None:
                raise ValueError("Child already belongs to another parent.")

        previous = getattr(self, side)
        if previous is not None:
            previous.parent = None

        setattr(self, side, child)

        if child is not None:
            child.parent = self


class LowestCommonAncestor:
    """LCA operations for a validated binary tree."""

    @staticmethod
    def validate_tree(root: Optional[TreeNode]) -> set[int]:
        if root is None:
            return set()

        visited = set()
        stack = [(root, None)]

        while stack:
            node, expected_parent = stack.pop()
            identity = id(node)

            if identity in visited:
                raise ValueError("Tree contains a cycle or shared child.")

            visited.add(identity)

            if node.parent is not expected_parent:
                raise ValueError("Inconsistent parent reference.")

            if node.left is not None:
                stack.append((node.left, node))

            if node.right is not None:
                stack.append((node.right, node))

        return visited

    @staticmethod
    def recursive_lca(
        root: Optional[TreeNode],
        first: TreeNode,
        second: TreeNode
    ) -> Optional[TreeNode]:
        """Recursive binary-tree LCA. Both targets must exist."""

        def search(node: Optional[TreeNode]) -> Optional[TreeNode]:
            if node is None:
                return None

            if node is first or node is second:
                return node

            left_result = search(node.left)
            right_result = search(node.right)

            if left_result is not None and right_result is not None:
                return node

            return left_result if left_result is not None else right_result

        identities = LowestCommonAncestor.validate_tree(root)

        if id(first) not in identities or id(second) not in identities:
            return None

        return search(root)

    @staticmethod
    def parent_based_lca(
        first: TreeNode,
        second: TreeNode
    ) -> Optional[TreeNode]:
        """Find LCA using parent pointers and ancestor sets."""

        def ancestors(node: TreeNode) -> set[int]:
            result = set()
            current = node

            while current is not None:
                identity = id(current)

                if identity in result:
                    raise ValueError("Cycle detected in parent references.")

                result.add(identity)
                current = current.parent

            return result

        second_ancestors = ancestors(second)
        current = first

        while current is not None:
            if id(current) in second_ancestors:
                return current
            current = current.parent

        return None

    @staticmethod
    def binary_tree_lca_by_value(
        root: Optional[TreeNode],
        first_value: int,
        second_value: int
    ) -> Optional[TreeNode]:
        """Value-based lookup requires unique values."""

        nodes = {}
        stack = [root] if root is not None else []

        while stack:
            node = stack.pop()

            if node.value in nodes:
                raise ValueError("Duplicate values make lookup ambiguous.")

            nodes[node.value] = node

            if node.left:
                stack.append(node.left)

            if node.right:
                stack.append(node.right)

        first = nodes.get(first_value)
        second = nodes.get(second_value)

        if first is None or second is None:
            return None

        return LowestCommonAncestor.recursive_lca(root, first, second)

    @staticmethod
    def distance_between(
        ancestor: TreeNode,
        descendant: TreeNode
    ) -> Optional[int]:
        """Return edge distance if ancestor is on descendant's path."""

        distance = 0
        current = descendant

        while current is not None:
            if current is ancestor:
                return distance

            current = current.parent
            distance += 1

        return None

    @staticmethod
    def lowest_common_ancestor_many(
        root: Optional[TreeNode],
        targets: Iterable[TreeNode]
    ) -> Optional[TreeNode]:
        """Find the lowest node containing every target in its subtree."""

        target_ids = {id(node) for node in targets}

        if not target_ids:
            return None

        identities = LowestCommonAncestor.validate_tree(root)

        if not target_ids.issubset(identities):
            return None

        counts = {}

        def visit(node: Optional[TreeNode]) -> tuple[int, Optional[TreeNode]]:
            if node is None:
                return 0, None

            left_count, left_lca = visit(node.left)
            right_count, right_lca = visit(node.right)

            count = left_count + right_count + (
                1 if id(node) in target_ids else 0
            )

            if left_lca is not None:
                candidate = left_lca
            elif right_lca is not None:
                candidate = right_lca
            elif count == len(target_ids):
                candidate = node
            else:
                candidate = None

            counts[id(node)] = count
            return count, candidate

        count, result = visit(root)

        return result if count == len(target_ids) else None


def build_sample_tree() -> dict[int, TreeNode]:
    nodes = {i: TreeNode(i) for i in range(1, 11)}

    nodes[1].attach_left(nodes[2])
    nodes[1].attach_right(nodes[3])

    nodes[2].attach_left(nodes[4])
    nodes[2].attach_right(nodes[5])

    nodes[3].attach_left(nodes[6])
    nodes[3].attach_right(nodes[7])

    nodes[5].attach_left(nodes[8])
    nodes[5].attach_right(nodes[9])

    nodes[7].attach_right(nodes[10])

    return nodes


def run_tests() -> None:
    nodes = build_sample_tree()
    root = nodes[1]

    assert LowestCommonAncestor.recursive_lca(
        root, nodes[4], nodes[5]
    ).value == 2

    assert LowestCommonAncestor.recursive_lca(
        root, nodes[4], nodes[6]
    ).value == 1

    assert LowestCommonAncestor.recursive_lca(
        root, nodes[8], nodes[9]
    ).value == 5

    assert LowestCommonAncestor.recursive_lca(
        root, nodes[8], nodes[8]
    ).value == 8

    assert LowestCommonAncestor.parent_based_lca(
        nodes[8], nodes[9]
    ).value == 5

    assert LowestCommonAncestor.parent_based_lca(
        nodes[4], nodes[10]
    ).value == 1

    assert LowestCommonAncestor.binary_tree_lca_by_value(
        root, 8, 10
    ).value == 1

    assert LowestCommonAncestor.binary_tree_lca_by_value(
        root, 4, 100
    ) is None

    assert LowestCommonAncestor.distance_between(
        nodes[2], nodes[8]
    ) == 2

    assert LowestCommonAncestor.distance_between(
        nodes[3], nodes[8]
    ) is None

    assert LowestCommonAncestor.lowest_common_ancestor_many(
        root, [nodes[8], nodes[9], nodes[5]]
    ).value == 5

    assert LowestCommonAncestor.lowest_common_ancestor_many(
        root, [nodes[4], nodes[6], nodes[10]]
    ).value == 1

    assert LowestCommonAncestor.recursive_lca(
        root, nodes[4], TreeNode(99)
    ) is None

    assert LowestCommonAncestor.recursive_lca(
        None, nodes[4], nodes[5]
    ) is None

    try:
        nodes[8].attach_left(root)
        raise AssertionError("Cycle validation failed.")
    except ValueError:
        pass

    print("All LCA tests passed.")


def display_results() -> None:
    nodes = build_sample_tree()
    root = nodes[1]

    print("Lowest Common Ancestor Demonstration")
    print("------------------------------------")

    cases = [
        (4, 5),
        (4, 6),
        (8, 9),
        (8, 10),
        (2, 8),
    ]

    for first_value, second_value in cases:
        first = nodes[first_value]
        second = nodes[second_value]

        result = LowestCommonAncestor.recursive_lca(
            root, first, second
        )

        print(
            f"LCA({first_value}, {second_value}) = "
            f"{result.value if result else 'Not found'}"
        )

    print("\nParent-based lookup:")
    result = LowestCommonAncestor.parent_based_lca(
        nodes[8], nodes[10]
    )
    print(f"LCA(8, 10) = {result.value}")

    print("\nDistance:")
    print(
        "Distance from node 2 to node 8:",
        LowestCommonAncestor.distance_between(nodes[2], nodes[8])
    )

    print("\nMultiple targets:")
    result = LowestCommonAncestor.lowest_common_ancestor_many(
        root, [nodes[8], nodes[9], nodes[10]]
    )
    print(f"LCA(8, 9, 10) = {result.value}")


if __name__ == "__main__":
    run_tests()
    display_results()
