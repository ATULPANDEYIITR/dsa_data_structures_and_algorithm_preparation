from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from statistics import mean
from typing import Optional, Iterable
import json
import logging
import unittest


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("bfs")


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


class BinaryTree:
    """Binary tree with queue-based BFS and level-order operations."""

    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root

    @classmethod
    def from_level_order(cls, values: Iterable[Optional[int]]) -> "BinaryTree":
        """Construct a binary tree from level-order values using None for gaps."""
        values = list(values)

        if not values:
            return cls()

        if values[0] is None:
            if any(value is not None for value in values[1:]):
                raise ValueError("A tree cannot have descendants without a root.")
            return cls()

        root = TreeNode(values[0])
        queue = deque([root])
        index = 1

        while queue and index < len(values):
            current = queue.popleft()

            if index < len(values):
                value = values[index]
                index += 1
                if value is not None:
                    current.left = TreeNode(value)
                    queue.append(current.left)

            if index < len(values):
                value = values[index]
                index += 1
                if value is not None:
                    current.right = TreeNode(value)
                    queue.append(current.right)

        if index < len(values):
            raise ValueError("Invalid level-order representation.")

        return cls(root)

    def level_order(self) -> list[list[int]]:
        """Return node values grouped by tree depth."""
        if self.root is None:
            return []

        result = []
        queue = deque([self.root])

        while queue:
            level_size = len(queue)
            current_level = []

            for _ in range(level_size):
                node = queue.popleft()
                current_level.append(node.value)

                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

            result.append(current_level)

        return result

    def flat_level_order(self) -> list[int]:
        """Return BFS traversal without level separation."""
        return [
            value
            for level in self.level_order()
            for value in level
        ]

    def level_averages(self) -> list[float]:
        """Calculate the average value at every depth."""
        return [
            mean(level)
            for level in self.level_order()
        ]

    def zigzag_traversal(self) -> list[list[int]]:
        """Alternate left-to-right and right-to-left level ordering."""
        if self.root is None:
            return []

        result = []
        queue = deque([self.root])
        left_to_right = True

        while queue:
            level_size = len(queue)
            level = deque()

            for _ in range(level_size):
                node = queue.popleft()

                if left_to_right:
                    level.append(node.value)
                else:
                    level.appendleft(node.value)

                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

            result.append(list(level))
            left_to_right = not left_to_right

        return result

    def level_statistics(self) -> list[dict]:
        """Produce detailed statistics for each tree level."""
        levels = self.level_order()
        statistics = []

        for depth, values in enumerate(levels):
            statistics.append({
                "depth": depth,
                "node_count": len(values),
                "minimum": min(values),
                "maximum": max(values),
                "average": round(mean(values), 2),
                "sum": sum(values)
            })

        return statistics

    def maximum_depth(self) -> int:
        return len(self.level_order())

    def node_count(self) -> int:
        return sum(len(level) for level in self.level_order())

    def find(self, target: int) -> Optional[TreeNode]:
        """Search for a value using BFS."""
        if self.root is None:
            return None

        queue = deque([self.root])

        while queue:
            node = queue.popleft()

            if node.value == target:
                return node

            if node.left:
                queue.append(node.left)

            if node.right:
                queue.append(node.right)

        return None

    def right_side_view(self) -> list[int]:
        """Return the last visible node at each depth."""
        if self.root is None:
            return []

        result = []
        queue = deque([self.root])

        while queue:
            level_size = len(queue)

            for index in range(level_size):
                node = queue.popleft()

                if index == level_size - 1:
                    result.append(node.value)

                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

        return result

    def bottom_up_level_order(self) -> list[list[int]]:
        return list(reversed(self.level_order()))

    def serialize(self) -> str:
        """Serialize the tree as a compact level-order JSON array."""
        if self.root is None:
            return "[]"

        result = []
        queue = deque([self.root])

        while queue:
            node = queue.popleft()

            if node is None:
                result.append(None)
                continue

            result.append(node.value)
            queue.append(node.left)
            queue.append(node.right)

        while result and result[-1] is None:
            result.pop()

        return json.dumps(result)

    @classmethod
    def deserialize(cls, data: str) -> "BinaryTree":
        try:
            values = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid tree JSON.") from exc

        if not isinstance(values, list):
            raise ValueError("Tree representation must be a JSON array.")

        for value in values:
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int)
            ):
                raise ValueError("Tree nodes must contain integers or null.")

        return cls.from_level_order(values)


def demonstrate():
    tree = BinaryTree.from_level_order([
        10, 20, 30, 40, 50, 60, 70, 80, 90
    ])

    print("\nBFS AND LEVEL-ORDER TRAVERSAL")
    print("=" * 45)

    print("Level-order traversal:")
    print(tree.level_order())

    print("\nFlat BFS traversal:")
    print(tree.flat_level_order())

    print("\nLevel averages:")
    print(tree.level_averages())

    print("\nZigzag traversal:")
    print(tree.zigzag_traversal())

    print("\nLevel statistics:")
    for statistics in tree.level_statistics():
        print(statistics)

    print("\nRight-side view:")
    print(tree.right_side_view())

    print("\nBottom-up traversal:")
    print(tree.bottom_up_level_order())

    print("\nTree depth:", tree.maximum_depth())
    print("Total nodes:", tree.node_count())

    print("\nSearching for 60:")
    print(tree.find(60))

    serialized = tree.serialize()
    print("\nSerialized tree:")
    print(serialized)

    restored = BinaryTree.deserialize(serialized)
    print("Restored tree:")
    print(restored.level_order())


class TestBinaryTree(unittest.TestCase):

    def setUp(self):
        self.tree = BinaryTree.from_level_order([
            1, 2, 3, 4, 5, 6, 7
        ])

    def test_level_order(self):
        self.assertEqual(
            self.tree.level_order(),
            [[1], [2, 3], [4, 5, 6, 7]]
        )

    def test_flat_traversal(self):
        self.assertEqual(
            self.tree.flat_level_order(),
            [1, 2, 3, 4, 5, 6, 7]
        )

    def test_level_averages(self):
        self.assertEqual(
            self.tree.level_averages(),
            [1, 2.5, 5.5]
        )

    def test_zigzag(self):
        self.assertEqual(
            self.tree.zigzag_traversal(),
            [[1], [3, 2], [4, 5, 6, 7]]
        )

    def test_empty_tree(self):
        tree = BinaryTree()
        self.assertEqual(tree.level_order(), [])
        self.assertEqual(tree.zigzag_traversal(), [])
        self.assertEqual(tree.maximum_depth(), 0)

    def test_single_node(self):
        tree = BinaryTree.from_level_order([42])
        self.assertEqual(tree.level_order(), [[42]])

    def test_sparse_tree(self):
        tree = BinaryTree.from_level_order([1, None, 2, 3])
        self.assertEqual(tree.level_order(), [[1], [2], [3]])

    def test_search(self):
        self.assertEqual(self.tree.find(5).value, 5)
        self.assertIsNone(self.tree.find(100))

    def test_serialization(self):
        restored = BinaryTree.deserialize(self.tree.serialize())
        self.assertEqual(restored.level_order(), self.tree.level_order())

    def test_invalid_root(self):
        with self.assertRaises(ValueError):
            BinaryTree.from_level_order([None, 1])

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            BinaryTree.deserialize("{invalid}")


if __name__ == "__main__":
    demonstrate()
    print("\nRUNNING TESTS")
    unittest.main(argv=["bfs.py"], exit=False)
