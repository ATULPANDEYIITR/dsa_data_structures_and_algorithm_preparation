#!/usr/bin/env python3
"""
Binary Search Tree (BST) Assessment and Practice
Python 3.10+

Operations:
- Search
- Insert
- Delete
- Validate BST
- Lowest Common Ancestor (LCA)
- Minimum and maximum
- Inorder successor and predecessor
- Traversals
- Height and balance assessment
- JSON serialization and restoration
- Automated correctness tests

Duplicate policy: duplicate keys are rejected.
"""

from __future__ import annotations

import json
import random
import unittest

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable, Any


@dataclass
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


class BSTError(Exception):
    """Base exception for BST operations."""


class InvalidBSTError(BSTError):
    """Raised when a tree violates BST ordering."""


class BinarySearchTree:
    def __init__(self, values: Optional[Iterable[int]] = None):
        self.root: Optional[Node] = None
        self._size = 0

        if values is not None:
            for value in values:
                self.insert(value)

    @property
    def size(self) -> int:
        return self._size

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise TypeError("BST keys must be integers.")

    def insert(self, key: int) -> bool:
        """Insert a key. Return False if it already exists."""
        self._validate_key(key)

        if self.root is None:
            self.root = Node(key)
            self._size = 1
            return True

        current = self.root

        while True:
            if key == current.key:
                return False

            if key < current.key:
                if current.left is None:
                    current.left = Node(key)
                    self._size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(key)
                    self._size += 1
                    return True
                current = current.right

    def search(self, key: int) -> Optional[Node]:
        self._validate_key(key)
        current = self.root

        while current is not None:
            if key == current.key:
                return current

            current = (
                current.left if key < current.key else current.right
            )

        return None

    def contains(self, key: int) -> bool:
        return self.search(key) is not None

    def minimum(self, node: Optional[Node] = None) -> Optional[int]:
        current = self.root if node is None else node

        if current is None:
            return None

        while current.left is not None:
            current = current.left

        return current.key

    def maximum(self, node: Optional[Node] = None) -> Optional[int]:
        current = self.root if node is None else node

        if current is None:
            return None

        while current.right is not None:
            current = current.right

        return current.key

    def _find_parent(self, key: int):
        parent = None
        current = self.root

        while current is not None and current.key != key:
            parent = current
            current = (
                current.left if key < current.key else current.right
            )

        return parent, current

    def delete(self, key: int) -> bool:
        """
        Delete a key using the three standard BST deletion cases.

        Case 1: Leaf node.
        Case 2: Node with one child.
        Case 3: Node with two children.
        """
        self._validate_key(key)

        parent, node = self._find_parent(key)

        if node is None:
            return False

        # A node with two children is replaced by its inorder successor.
        if node.left is not None and node.right is not None:
            successor_parent = node
            successor = node.right

            while successor.left is not None:
                successor_parent = successor
                successor = successor.left

            node.key = successor.key

            parent = successor_parent
            node = successor

        # At this point, the node has at most one child.
        child = node.left if node.left is not None else node.right

        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child

        self._size -= 1
        return True

    def inorder(self) -> list[int]:
        result = []

        def traverse(node):
            if node is None:
                return

            traverse(node.left)
            result.append(node.key)
            traverse(node.right)

        traverse(self.root)
        return result

    def preorder(self) -> list[int]:
        result = []

        def traverse(node):
            if node is None:
                return

            result.append(node.key)
            traverse(node.left)
            traverse(node.right)

        traverse(self.root)
        return result

    def postorder(self) -> list[int]:
        result = []

        def traverse(node):
            if node is None:
                return

            traverse(node.left)
            traverse(node.right)
            result.append(node.key)

        traverse(self.root)
        return result

    def level_order(self) -> list[int]:
        if self.root is None:
            return []

        queue = [self.root]
        result = []
        index = 0

        while index < len(queue):
            node = queue[index]
            index += 1

            result.append(node.key)

            if node.left:
                queue.append(node.left)

            if node.right:
                queue.append(node.right)

        return result

    def validate(self) -> bool:
        """Validate strict BST ordering using lower and upper bounds."""

        def check(node, lower, upper):
            if node is None:
                return True

            if lower is not None and node.key <= lower:
                return False

            if upper is not None and node.key >= upper:
                return False

            return (
                check(node.left, lower, node.key)
                and check(node.right, node.key, upper)
            )

        return check(self.root, None, None)

    def lowest_common_ancestor(
        self, first: int, second: int
    ) -> Optional[int]:
        """
        Return the LCA only when both requested keys exist.
        """
        self._validate_key(first)
        self._validate_key(second)

        if not self.contains(first) or not self.contains(second):
            return None

        current = self.root

        while current is not None:
            if first < current.key and second < current.key:
                current = current.left
            elif first > current.key and second > current.key:
                current = current.right
            else:
                return current.key

        return None

    def successor(self, key: int) -> Optional[int]:
        """Find the smallest existing key greater than key."""
        self._validate_key(key)

        current = self.root
        candidate = None

        while current is not None:
            if key < current.key:
                candidate = current.key
                current = current.left
            else:
                current = current.right

        return candidate

    def predecessor(self, key: int) -> Optional[int]:
        """Find the largest existing key smaller than key."""
        self._validate_key(key)

        current = self.root
        candidate = None

        while current is not None:
            if key > current.key:
                candidate = current.key
                current = current.right
            else:
                current = current.left

        return candidate

    def height(self) -> int:
        """Height measured in edges. Empty tree has height -1."""

        def calculate(node):
            if node is None:
                return -1

            return 1 + max(
                calculate(node.left),
                calculate(node.right)
            )

        return calculate(self.root)

    def is_balanced(self) -> bool:
        """Check AVL-style height balance without repeated traversal."""

        def check(node):
            if node is None:
                return 0

            left_height = check(node.left)

            if left_height == -1:
                return -1

            right_height = check(node.right)

            if right_height == -1:
                return -1

            if abs(left_height - right_height) > 1:
                return -1

            return 1 + max(left_height, right_height)

        return check(self.root) != -1

    def range_query(self, low: int, high: int) -> list[int]:
        """Return keys within an inclusive range."""
        self._validate_key(low)
        self._validate_key(high)

        if low > high:
            raise ValueError("Lower bound cannot exceed upper bound.")

        result = []

        def traverse(node):
            if node is None:
                return

            if node.key > low:
                traverse(node.left)

            if low <= node.key <= high:
                result.append(node.key)

            if node.key < high:
                traverse(node.right)

        traverse(self.root)
        return result

    def to_dict(self) -> Optional[dict[str, Any]]:
        def serialize(node):
            if node is None:
                return None

            return {
                "key": node.key,
                "left": serialize(node.left),
                "right": serialize(node.right)
            }

        return serialize(self.root)

    def save_json(self, filename: str) -> None:
        path = Path(filename)

        if path.suffix.lower() != ".json":
            raise ValueError("Only JSON files are supported.")

        payload = {
            "version": 1,
            "size": self.size,
            "root": self.to_dict()
        }

        path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8"
        )

    @classmethod
    def from_dict(cls, data):
        tree = cls()

        def restore(item, lower, upper):
            if item is None:
                return None

            if not isinstance(item, dict):
                raise InvalidBSTError("Invalid node representation.")

            if set(item) != {"key", "left", "right"}:
                raise InvalidBSTError("Unexpected node fields.")

            key = item["key"]
            cls._validate_key(key)

            if lower is not None and key <= lower:
                raise InvalidBSTError("Lower-bound violation.")

            if upper is not None and key >= upper:
                raise InvalidBSTError("Upper-bound violation.")

            node = Node(key)
            tree._size += 1

            node.left = restore(item["left"], lower, key)
            node.right = restore(item["right"], key, upper)

            return node

        tree.root = restore(data, None, None)
        return tree

    @classmethod
    def load_json(cls, filename: str):
        payload = json.loads(
            Path(filename).read_text(encoding="utf-8")
        )

        if not isinstance(payload, dict):
            raise InvalidBSTError("Invalid JSON document.")

        if payload.get("version") != 1:
            raise InvalidBSTError("Unsupported file version.")

        tree = cls.from_dict(payload.get("root"))

        if payload.get("size") != tree.size:
            raise InvalidBSTError("Stored size does not match tree.")

        return tree


class BSTTests(unittest.TestCase):
    def setUp(self):
        self.tree = BinarySearchTree(
            [50, 30, 70, 20, 40, 60, 80]
        )

    def test_search(self):
        self.assertTrue(self.tree.contains(40))
        self.assertFalse(self.tree.contains(99))

    def test_insert(self):
        self.assertTrue(self.tree.insert(45))
        self.assertFalse(self.tree.insert(45))
        self.assertEqual(self.tree.size, 8)

    def test_delete_leaf(self):
        self.assertTrue(self.tree.delete(20))
        self.assertEqual(
            self.tree.inorder(),
            [30, 40, 50, 60, 70, 80]
        )

    def test_delete_one_child(self):
        self.tree.insert(65)
        self.assertTrue(self.tree.delete(60))
        self.assertTrue(self.tree.validate())

    def test_delete_two_children(self):
        self.assertTrue(self.tree.delete(50))
        self.assertEqual(
            self.tree.inorder(),
            [20, 30, 40, 60, 70, 80]
        )

    def test_missing_delete(self):
        self.assertFalse(self.tree.delete(999))

    def test_validation(self):
        self.assertTrue(self.tree.validate())

    def test_lca(self):
        self.assertEqual(
            self.tree.lowest_common_ancestor(20, 40), 30
        )
        self.assertEqual(
            self.tree.lowest_common_ancestor(20, 80), 50
        )
        self.assertIsNone(
            self.tree.lowest_common_ancestor(20, 999)
        )

    def test_minimum_maximum(self):
        self.assertEqual(self.tree.minimum(), 20)
        self.assertEqual(self.tree.maximum(), 80)

    def test_successor_predecessor(self):
        self.assertEqual(self.tree.successor(40), 50)
        self.assertEqual(self.tree.predecessor(60), 50)
        self.assertIsNone(self.tree.successor(80))
        self.assertIsNone(self.tree.predecessor(20))

    def test_traversals(self):
        self.assertEqual(
            self.tree.inorder(),
            [20, 30, 40, 50, 60, 70, 80]
        )

    def test_range(self):
        self.assertEqual(
            self.tree.range_query(30, 70),
            [30, 40, 50, 60, 70]
        )

    def test_random_operations(self):
        tree = BinarySearchTree()
        reference = set()
        generator = random.Random(42)

        for _ in range(500):
            value = generator.randint(-100, 100)

            if generator.random() < 0.55:
                self.assertEqual(
                    tree.insert(value),
                    value not in reference
                )
                reference.add(value)
            else:
                self.assertEqual(
                    tree.delete(value),
                    value in reference
                )
                reference.discard(value)

            self.assertTrue(tree.validate())
            self.assertEqual(tree.inorder(), sorted(reference))
            self.assertEqual(tree.size, len(reference))

    def test_serialization(self):
        restored = BinarySearchTree.from_dict(
            self.tree.to_dict()
        )

        self.assertEqual(
            restored.inorder(),
            self.tree.inorder()
        )

    def test_invalid_key(self):
        with self.assertRaises(TypeError):
            self.tree.insert(True)


def demonstration():
    tree = BinarySearchTree(
        [50, 30, 70, 20, 40, 60, 80]
    )

    print("BST ASSESSMENT")
    print("==============")
    print("Inorder:", tree.inorder())
    print("Preorder:", tree.preorder())
    print("Postorder:", tree.postorder())
    print("Level order:", tree.level_order())

    print("\nSearch 40:", tree.contains(40))
    print("Search 99:", tree.contains(99))

    print("\nInsert 65:", tree.insert(65))
    print("Minimum:", tree.minimum())
    print("Maximum:", tree.maximum())

    print("\nLCA(20, 40):", tree.lowest_common_ancestor(20, 40))
    print("Successor(40):", tree.successor(40))
    print("Predecessor(60):", tree.predecessor(60))

    print("\nRange 30-70:", tree.range_query(30, 70))
    print("Height:", tree.height())
    print("Balanced:", tree.is_balanced())
    print("Valid BST:", tree.validate())

    print("\nDelete 50:", tree.delete(50))
    print("After deletion:", tree.inorder())
    print("Valid after deletion:", tree.validate())


if __name__ == "__main__":
    demonstration()
    print("\nRUNNING AUTOMATED TESTS")
    unittest.main(argv=["bst.py"], exit=False)
