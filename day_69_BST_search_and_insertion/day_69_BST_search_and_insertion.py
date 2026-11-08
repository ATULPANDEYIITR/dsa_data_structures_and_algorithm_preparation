#!/usr/bin/env python3
"""
Binary Search Tree: Search, Insert, Minimum, Maximum.

Demonstrates an unbalanced BST, duplicate handling, iterative operations,
tree traversal, height measurement, validation, and performance comparison.
"""

from __future__ import annotations

import json
import logging
import random
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("bst")


@dataclass
class Node:
    key: int
    left: Optional[Node] = None
    right: Optional[Node] = None


class BinarySearchTree:
    """Unbalanced BST with unique integer keys."""

    def __init__(self) -> None:
        self.root: Optional[Node] = None
        self.size = 0
        self.comparisons = 0

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise TypeError("BST keys must be integers.")

    def insert(self, key: int) -> bool:
        """Insert a key. Return False when it already exists."""
        self._validate_key(key)

        new_node = Node(key)

        if self.root is None:
            self.root = new_node
            self.size += 1
            return True

        current = self.root

        while True:
            if key == current.key:
                return False

            if key < current.key:
                if current.left is None:
                    current.left = new_node
                    self.size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    self.size += 1
                    return True
                current = current.right

    def search(self, key: int) -> bool:
        """Search for a key using iterative traversal."""
        self._validate_key(key)
        self.comparisons = 0

        current = self.root

        while current is not None:
            self.comparisons += 1

            if key == current.key:
                return True

            current = (
                current.left if key < current.key else current.right
            )

        return False

    def minimum(self) -> Optional[int]:
        """Return the smallest key, or None for an empty tree."""
        if self.root is None:
            return None

        current = self.root

        while current.left is not None:
            current = current.left

        return current.key

    def maximum(self) -> Optional[int]:
        """Return the largest key, or None for an empty tree."""
        if self.root is None:
            return None

        current = self.root

        while current.right is not None:
            current = current.right

        return current.key

    def inorder(self) -> list[int]:
        """Return keys in ascending order without recursion."""
        result = []
        stack = []
        current = self.root

        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append(current.key)
            current = current.right

        return result

    def height(self) -> int:
        """Return tree height measured in edges. Empty tree is -1."""
        if self.root is None:
            return -1

        queue = [(self.root, 0)]
        maximum_depth = 0

        for node, depth in queue:
            maximum_depth = max(maximum_depth, depth)

            if node.left is not None:
                queue.append((node.left, depth + 1))

            if node.right is not None:
                queue.append((node.right, depth + 1))

        return maximum_depth

    def validate(self) -> bool:
        """Verify the strict BST ordering property."""
        stack = [(self.root, None, None)]
        visited = 0

        while stack:
            node, lower, upper = stack.pop()

            if node is None:
                continue

            if lower is not None and node.key <= lower:
                return False

            if upper is not None and node.key >= upper:
                return False

            visited += 1
            stack.append((node.left, lower, node.key))
            stack.append((node.right, node.key, upper))

        return visited == self.size

    def export_json(self, filename: str) -> None:
        """Export an ordered representation of the tree."""
        path = Path(filename)
        if path.suffix.lower() != ".json":
            raise ValueError("Export filename must end in .json")

        payload = {
            "keys": self.inorder(),
            "size": self.size,
            "height": self.height(),
            "minimum": self.minimum(),
            "maximum": self.maximum(),
        }

        path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8"
        )

    @classmethod
    def from_values(cls, values: list[int]) -> BinarySearchTree:
        tree = cls()

        for value in values:
            tree.insert(value)

        return tree


def demonstrate_basic_operations() -> BinarySearchTree:
    print("\n=== BST Operations ===")

    values = [50, 30, 70, 20, 40, 60, 80, 35, 45]
    tree = BinarySearchTree.from_values(values)

    print("Inserted:", values)
    print("Duplicate insertion (50):", tree.insert(50))
    print("Search 40:", tree.search(40))
    print("Search 100:", tree.search(100))
    print("Minimum:", tree.minimum())
    print("Maximum:", tree.maximum())
    print("Inorder:", tree.inorder())
    print("Height:", tree.height())
    print("Node count:", tree.size)
    print("BST valid:", tree.validate())

    assert tree.inorder() == [20, 30, 35, 40, 45, 50, 60, 70, 80]
    assert tree.minimum() == 20
    assert tree.maximum() == 80
    assert tree.search(40)
    assert not tree.search(100)
    assert tree.validate()

    return tree


def demonstrate_edge_cases() -> None:
    print("\n=== Edge Cases ===")

    empty = BinarySearchTree()

    assert empty.search(10) is False
    assert empty.minimum() is None
    assert empty.maximum() is None
    assert empty.height() == -1

    single = BinarySearchTree()
    single.insert(42)

    assert single.minimum() == 42
    assert single.maximum() == 42
    assert single.height() == 0

    try:
        single.insert(True)
    except TypeError as exc:
        print("Invalid key rejected:", exc)

    print("Empty tree handled.")
    print("Single-node tree handled.")


def benchmark() -> None:
    print("\n=== Performance Comparison ===")

    count = 2000
    random_values = random.Random(42).sample(
        range(count * 10), count
    )

    balanced_order = sorted(random_values)

    # Median-first insertion produces a relatively balanced BST.
    def median_first(values: list[int]) -> list[int]:
        result = []
        stack = [(0, len(values) - 1)]

        while stack:
            low, high = stack.pop()

            if low > high:
                continue

            middle = (low + high) // 2
            result.append(values[middle])

            stack.append((middle + 1, high))
            stack.append((low, middle - 1))

        return result

    balanced_tree = BinarySearchTree.from_values(
        median_first(balanced_order)
    )
    skewed_tree = BinarySearchTree.from_values(
        sorted(random_values)
    )

    target = random_values[-1]

    for label, tree in [
        ("Median-first insertion", balanced_tree),
        ("Sorted insertion", skewed_tree),
    ]:
        start = time.perf_counter()
        found = tree.search(target)
        elapsed = time.perf_counter() - start

        print(
            f"{label}: found={found}, "
            f"height={tree.height()}, "
            f"comparisons={tree.comparisons}, "
            f"time={elapsed:.8f}s"
        )

    print(
        "Balanced tree height:",
        balanced_tree.height()
    )
    print(
        "Skewed tree height:",
        skewed_tree.height()
    )


def main() -> None:
    tree = demonstrate_basic_operations()
    demonstrate_edge_cases()

    print("\n=== Export ===")
    try:
        tree.export_json("bst_report.json")
        print("Report saved to bst_report.json")
    except (OSError, ValueError) as exc:
        logger.error("Export failed: %s", exc)

    benchmark()

    print("\nAll BST assertions passed.")


if __name__ == "__main__":
    main()
