from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from enum import Enum
from pathlib import Path
from typing import Optional
import json
import sys


class BalanceState(Enum):
    BALANCED = "balanced"
    UNBALANCED = "unbalanced"


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


class InvalidTreeError(ValueError):
    pass


class BinaryTreeAnalyzer:
    """Analyze a binary tree using recursive and iterative algorithms."""

    def __init__(self, root: Optional[TreeNode]) -> None:
        self.root = root

    @staticmethod
    def from_level_order(values: list[Optional[int]]) -> Optional[TreeNode]:
        """
        Build a binary tree from level-order values.
        None represents a missing child.
        """
        if not values or values[0] is None:
            return None

        root = TreeNode(values[0])
        queue: deque[TreeNode] = deque([root])
        index = 1

        while queue and index < len(values):
            node = queue.popleft()

            if index < len(values):
                left_value = values[index]
                index += 1
                if left_value is not None:
                    node.left = TreeNode(left_value)
                    queue.append(node.left)

            if index < len(values):
                right_value = values[index]
                index += 1
                if right_value is not None:
                    node.right = TreeNode(right_value)
                    queue.append(node.right)

        if index < len(values):
            raise InvalidTreeError("Level-order input contains unreachable nodes.")

        return root

    def maximum_depth(self) -> int:
        """Return the number of nodes on the longest root-to-leaf path."""

        def depth(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + max(depth(node.left), depth(node.right))

        return depth(self.root)

    def minimum_depth(self) -> int:
        """
        Return the number of nodes on the shortest root-to-leaf path.
        A missing child cannot be treated as a zero-length path for a
        node that has another child.
        """
        if self.root is None:
            return 0

        queue: deque[tuple[TreeNode, int]] = deque([(self.root, 1)])

        while queue:
            node, depth = queue.popleft()

            if node.left is None and node.right is None:
                return depth

            if node.left is not None:
                queue.append((node.left, depth + 1))

            if node.right is not None:
                queue.append((node.right, depth + 1))

        raise RuntimeError("A non-empty tree did not produce a leaf.")

    def leaf_count(self) -> int:
        if self.root is None:
            return 0

        count = 0
        stack = [self.root]

        while stack:
            node = stack.pop()

            if node.left is None and node.right is None:
                count += 1
                continue

            if node.right is not None:
                stack.append(node.right)

            if node.left is not None:
                stack.append(node.left)

        return count

    def balance_state(self) -> BalanceState:
        """
        Check whether the tree is height-balanced.

        A node is balanced when the height difference between its
        subtrees is at most one. -1 is propagated as an early failure
        marker, avoiding repeated height calculations.
        """

        def height_or_failure(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0

            left_height = height_or_failure(node.left)
            if left_height == -1:
                return -1

            right_height = height_or_failure(node.right)
            if right_height == -1:
                return -1

            if abs(left_height - right_height) > 1:
                return -1

            return 1 + max(left_height, right_height)

        return (
            BalanceState.BALANCED
            if height_or_failure(self.root) != -1
            else BalanceState.UNBALANCED
        )

    def minimum_depth_with_path(self) -> tuple[int, list[int]]:
        """Return both minimum depth and one shortest root-to-leaf path."""
        if self.root is None:
            return 0, []

        queue: deque[tuple[TreeNode, list[int]]] = deque(
            [(self.root, [self.root.value])]
        )

        while queue:
            node, path = queue.popleft()

            if node.left is None and node.right is None:
                return len(path), path

            if node.left is not None:
                queue.append((node.left, path + [node.left.value]))

            if node.right is not None:
                queue.append((node.right, path + [node.right.value]))

        raise RuntimeError("No leaf was found.")

    def statistics(self) -> dict[str, object]:
        minimum, path = self.minimum_depth_with_path()
        return {
            "maximum_depth": self.maximum_depth(),
            "minimum_depth": minimum,
            "minimum_depth_path": path,
            "leaf_count": self.leaf_count(),
            "balanced": self.balance_state().value == BalanceState.BALANCED.value,
        }


def validate_values(values: list[Optional[int]]) -> None:
    if not isinstance(values, list):
        raise TypeError("Tree input must be a list.")

    if len(values) > 100_000:
        raise ValueError("Tree input exceeds the supported node representation size.")

    for value in values:
        if value is not None and not isinstance(value, int):
            raise TypeError("Every tree value must be an integer or None.")


def run_examples() -> None:
    examples = {
        "balanced": [3, 9, 20, None, None, 15, 7],
        "unbalanced": [1, 2, 2, 3, 3, None, None, 4, 4],
        "single_node": [42],
        "skewed": [1, 2, None, 3, None, 4],
        "empty": [],
    }

    for name, values in examples.items():
        validate_values(values)
        tree = BinaryTreeAnalyzer.from_level_order(values)
        analyzer = BinaryTreeAnalyzer(tree)

        print(f"\n{name}")
        print(json.dumps(analyzer.statistics(), indent=2))


def save_report(path: Path, report: dict[str, object]) -> None:
    """
    Write only generated analysis data.
    The path is supplied by the program and is not interpreted as
    executable content.
    """
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    run_examples()

    production_values = [
        10,
        5,
        15,
        3,
        7,
        12,
        18,
        1,
        4,
        6,
        8,
        None,
        13,
        17,
        20,
    ]

    validate_values(production_values)
    analyzer = BinaryTreeAnalyzer(
        BinaryTreeAnalyzer.from_level_order(production_values)
    )

    report = analyzer.statistics()
    output_path = Path("tree_analysis_report.json")
    save_report(output_path, report)

    assert report["maximum_depth"] == 4
    assert report["minimum_depth"] == 3
    assert report["leaf_count"] == 7
    assert report["balanced"] is True

    print("\nValidated production example.")
    print(f"Report written to: {output_path.resolve()}")

    if "--stdin" in sys.argv:
        raw = sys.stdin.read().strip()
        if raw:
            values = json.loads(raw)
            validate_values(values)
            result = BinaryTreeAnalyzer(
                BinaryTreeAnalyzer.from_level_order(values)
            ).statistics()
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
