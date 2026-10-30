#!/usr/bin/env python3
"""Manual binary-tree construction and analysis using Python's standard library."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Literal
import json


Side = Literal["left", "right"]


class TreeError(ValueError):
    """Raised when a binary-tree operation violates a structural rule."""


@dataclass(eq=False, slots=True)
class Node:
    """A binary-tree node with non-owning parent and child references."""

    node_id: str
    value: str
    left: Node | None = field(default=None, repr=False)
    right: Node | None = field(default=None, repr=False)
    parent: Node | None = field(default=None, repr=False)

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class BinaryTree:
    """
    A manually constructed binary tree.

    Height is measured in edges: a leaf has height 0.
    Depth is measured in edges: the root has depth 0.
    Level is depth + 1: the root is on level 1.
    """

    def __init__(self, root: Node) -> None:
        if root.parent is not None:
            raise TreeError("The root cannot have a parent.")

        self.root = root
        self._nodes = self._collect_subtree(root)

    @staticmethod
    def create_node(node_id: str, value: str) -> Node:
        if not node_id.strip():
            raise TreeError("Node ID cannot be empty.")
        if not value.strip():
            raise TreeError("Node value cannot be empty.")
        return Node(node_id=node_id, value=value)

    @staticmethod
    def _collect_subtree(start: Node) -> set[Node]:
        """Collect nodes while detecting cycles, shared children, and bad links."""
        collected: set[Node] = set()
        stack: list[tuple[Node, Node | None]] = [(start, None)]

        while stack:
            current, expected_parent = stack.pop()

            if current in collected:
                raise TreeError(
                    f"Cycle or shared child detected at node {current.node_id}."
                )

            if current.parent is not expected_parent:
                raise TreeError(
                    f"Inconsistent parent reference at node {current.node_id}."
                )

            collected.add(current)

            if current.right is not None:
                stack.append((current.right, current))

            if current.left is not None:
                stack.append((current.left, current))

        return collected

    def _require_member(self, node: Node) -> None:
        if node not in self._nodes:
            raise TreeError(f"Node {node.node_id} does not belong to this tree.")

    def attach(self, parent: Node, child: Node, side: Side) -> None:
        """
        Attach a standalone subtree to an available left or right child slot.

        The incoming subtree must be detached and must not contain nodes
        already owned by this tree.
        """
        self._require_member(parent)

        if side not in ("left", "right"):
            raise TreeError("Side must be 'left' or 'right'.")

        if child in self._nodes:
            raise TreeError("The child already belongs to this tree.")

        if child.parent is not None:
            raise TreeError("The incoming subtree root already has a parent.")

        incoming_nodes = self._collect_subtree(child)

        if self._nodes.intersection(incoming_nodes):
            raise TreeError("The incoming subtree overlaps the existing tree.")

        if side == "left":
            if parent.left is not None:
                raise TreeError(f"Node {parent.node_id} already has a left child.")
            parent.left = child
        else:
            if parent.right is not None:
                raise TreeError(f"Node {parent.node_id} already has a right child.")
            parent.right = child

        child.parent = parent
        self._nodes.update(incoming_nodes)

    def contains(self, node: Node) -> bool:
        return node in self._nodes

    def node_count(self) -> int:
        return len(self._nodes)

    def depth(self, node: Node) -> int:
        """Count edges between the root and the specified node."""
        self._require_member(node)

        depth = 0
        current = node
        visited: set[Node] = set()

        while current.parent is not None:
            if current in visited:
                raise TreeError("Cycle detected in parent references.")

            visited.add(current)
            current = current.parent
            depth += 1

        if current is not self.root:
            raise TreeError("Node is disconnected from the root.")

        return depth

    def level(self, node: Node) -> int:
        return self.depth(node) + 1

    def height(self, node: Node | None = None) -> int:
        """
        Return the longest downward path in edges.

        An empty subtree has height -1; a leaf has height 0.
        """
        start = self.root if node is None else node
        self._require_member(start)

        heights: dict[Node, int] = {}
        stack: list[tuple[Node, bool]] = [(start, False)]

        # Iterative postorder avoids recursion-depth failures on deep trees.
        while stack:
            current, expanded = stack.pop()

            if not expanded:
                stack.append((current, True))
                if current.right is not None:
                    stack.append((current.right, False))
                if current.left is not None:
                    stack.append((current.left, False))
                continue

            left_height = heights.get(current.left, -1)
            right_height = heights.get(current.right, -1)
            heights[current] = 1 + max(left_height, right_height)

        return heights[start]

    def subtree_size(self, node: Node) -> int:
        self._require_member(node)
        return len(self._collect_subtree(node))

    def is_leaf(self, node: Node) -> bool:
        self._require_member(node)
        return node.is_leaf()

    def levels(self) -> list[list[str]]:
        """Return node IDs grouped by level using breadth-first traversal."""
        result: list[list[str]] = []
        queue: deque[Node] = deque([self.root])

        while queue:
            level_size = len(queue)
            current_level: list[str] = []

            for _ in range(level_size):
                node = queue.popleft()
                current_level.append(node.node_id)

                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)

            result.append(current_level)

        return result

    def preorder(self) -> list[str]:
        result: list[str] = []
        stack = [self.root]

        while stack:
            node = stack.pop()
            result.append(node.node_id)

            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)

        return result

    def inorder(self) -> list[str]:
        result: list[str] = []
        stack: list[Node] = []
        current: Node | None = self.root

        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append(current.node_id)
            current = current.right

        return result

    def postorder(self) -> list[str]:
        result: list[str] = []
        stack: list[tuple[Node, bool]] = [(self.root, False)]

        while stack:
            node, visited = stack.pop()

            if visited:
                result.append(node.node_id)
                continue

            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))

        return result

    def validate(self) -> bool:
        reachable = self._collect_subtree(self.root)
        if reachable != self._nodes:
            raise TreeError("The registered nodes do not match the reachable tree.")
        return True

    def report(self) -> dict[str, object]:
        nodes: list[dict[str, object]] = []

        for node_id in self.preorder():
            node = next(n for n in self._nodes if n.node_id == node_id)
            nodes.append(
                {
                    "id": node.node_id,
                    "value": node.value,
                    "parent": node.parent.node_id if node.parent else None,
                    "left": node.left.node_id if node.left else None,
                    "right": node.right.node_id if node.right else None,
                    "depth": self.depth(node),
                    "level": self.level(node),
                    "height": self.height(node),
                    "is_leaf": self.is_leaf(node),
                    "subtree_size": self.subtree_size(node),
                }
            )

        return {
            "node_count": self.node_count(),
            "tree_height": self.height(),
            "levels": self.levels(),
            "preorder": self.preorder(),
            "inorder": self.inorder(),
            "postorder": self.postorder(),
            "nodes": nodes,
        }


def build_example_tree() -> tuple[BinaryTree, dict[str, Node]]:
    """
    Construct this tree manually:

              A
             / \\
            B   C
           / \\   \\
          D   E   F
             /
            G
    """
    root = Node("A", "Root")
    tree = BinaryTree(root)

    nodes = {
        "A": root,
        "B": tree.create_node("B", "Left child of A"),
        "C": tree.create_node("C", "Right child of A"),
        "D": tree.create_node("D", "Left child of B"),
        "E": tree.create_node("E", "Right child of B"),
        "F": tree.create_node("F", "Right child of C"),
        "G": tree.create_node("G", "Left child of E"),
    }

    tree.attach(nodes["A"], nodes["B"], "left")
    tree.attach(nodes["A"], nodes["C"], "right")
    tree.attach(nodes["B"], nodes["D"], "left")
    tree.attach(nodes["B"], nodes["E"], "right")
    tree.attach(nodes["C"], nodes["F"], "right")
    tree.attach(nodes["E"], nodes["G"], "left")

    return tree, nodes


def main() -> None:
    tree, nodes = build_example_tree()
    assert tree.validate()

    print("BINARY TREE FUNDAMENTALS")
    print(json.dumps(tree.report(), indent=2))

    print("\nSELECTED NODE RELATIONSHIPS")
    for node_id in ("A", "B", "D", "G", "F"):
        node = nodes[node_id]
        print(
            f"{node.node_id}: "
            f"parent={node.parent.node_id if node.parent else None}, "
            f"depth={tree.depth(node)}, "
            f"level={tree.level(node)}, "
            f"height={tree.height(node)}, "
            f"leaf={tree.is_leaf(node)}"
        )

    print("\nSUBTREE ROOTED AT B")
    print(f"Height: {tree.height(nodes['B'])}")
    print(f"Size: {tree.subtree_size(nodes['B'])}")

    print("\nEDGE-CASE VALIDATION")
    try:
        tree.attach(nodes["G"], nodes["A"], "left")
    except TreeError as error:
        print(f"Rejected invalid attachment: {error}")

    try:
        tree.attach(nodes["A"], tree.create_node("X", "Duplicate slot"), "left")
    except TreeError as error:
        print(f"Rejected occupied child slot: {error}")

    assert tree.node_count() == 7
    assert tree.height() == 3
    assert tree.depth(nodes["G"]) == 3
    assert tree.level(nodes["G"]) == 4
    assert tree.height(nodes["B"]) == 2
    assert tree.subtree_size(nodes["B"]) == 4
    assert {node.node_id for node in nodes.values() if tree.is_leaf(node)} == {
        "D", "F", "G"
    }

    print("\nAll structural checks passed.")


if __name__ == "__main__":
    main()
