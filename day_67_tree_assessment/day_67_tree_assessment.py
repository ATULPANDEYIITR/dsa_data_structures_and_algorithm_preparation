from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional, Iterator


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


class TreeValidationError(ValueError):
    pass


class BinaryTree:
    """
    Binary tree assessment toolkit.

    Height and diameter are measured in edges.
    An empty tree has height -1 and diameter 0.
    """

    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root
        self.validate()

    def validate(self) -> None:
        """Reject cycles and nodes shared by multiple parents."""
        if self.root is None:
            return

        visited = set()
        stack = [(self.root, False)]

        while stack:
            node, exiting = stack.pop()
            identity = id(node)

            if exiting:
                continue

            if identity in visited:
                raise TreeValidationError(
                    "Cycle or shared child detected."
                )

            visited.add(identity)

            if not isinstance(node.value, int):
                raise TreeValidationError(
                    "Every node must contain an integer."
                )

            stack.append((node, True))

            if node.right:
                stack.append((node.right, False))

            if node.left:
                stack.append((node.left, False))

    def preorder(self) -> list[int]:
        """Root, left, right."""
        result = []
        stack = [self.root] if self.root else []

        while stack:
            node = stack.pop()
            result.append(node.value)

            if node.right:
                stack.append(node.right)

            if node.left:
                stack.append(node.left)

        return result

    def inorder(self) -> list[int]:
        """Left, root, right."""
        result = []
        stack = []
        current = self.root

        while current or stack:
            while current:
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append(current.value)
            current = current.right

        return result

    def postorder(self) -> list[int]:
        """Left, right, root."""
        result = []
        stack = [(self.root, False)] if self.root else []

        while stack:
            node, visited = stack.pop()

            if visited:
                result.append(node.value)
            else:
                stack.append((node, True))

                if node.right:
                    stack.append((node.right, False))

                if node.left:
                    stack.append((node.left, False))

        return result

    def level_order(self) -> list[list[int]]:
        """Breadth-first traversal grouped by level."""
        if not self.root:
            return []

        result = []
        queue = deque([self.root])

        while queue:
            level = []

            for _ in range(len(queue)):
                node = queue.popleft()
                level.append(node.value)

                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

            result.append(level)

        return result

    def zigzag_level_order(self) -> list[list[int]]:
        levels = self.level_order()

        for index in range(1, len(levels), 2):
            levels[index].reverse()

        return levels

    def height(self) -> int:
        """Maximum number of edges from root to a leaf."""
        if not self.root:
            return -1

        queue = deque([(self.root, 0)])
        maximum = 0

        while queue:
            node, depth = queue.popleft()
            maximum = max(maximum, depth)

            if node.left:
                queue.append((node.left, depth + 1))

            if node.right:
                queue.append((node.right, depth + 1))

        return maximum

    def diameter(self) -> int:
        """
        Longest path between any two nodes.
        Runs in O(n) time using one postorder traversal.
        """
        diameter = 0

        def calculate(node: Optional[TreeNode]) -> int:
            nonlocal diameter

            if not node:
                return -1

            left_height = calculate(node.left)
            right_height = calculate(node.right)

            diameter = max(
                diameter,
                left_height + right_height + 2
            )

            return max(left_height, right_height) + 1

        calculate(self.root)
        return diameter

    def is_balanced(self) -> bool:
        """Check whether every node has subtree heights differing by at most one."""

        def check(node: Optional[TreeNode]) -> int:
            if not node:
                return 0

            left = check(node.left)
            if left == -1:
                return -1

            right = check(node.right)
            if right == -1:
                return -1

            if abs(left - right) > 1:
                return -1

            return max(left, right) + 1

        return check(self.root) != -1

    def has_path_sum(self, target: int) -> bool:
        """Check whether a root-to-leaf path has the target sum."""
        if not self.root:
            return False

        stack = [(self.root, self.root.value)]

        while stack:
            node, total = stack.pop()

            if not node.left and not node.right:
                if total == target:
                    return True

            if node.right:
                stack.append(
                    (node.right, total + node.right.value)
                )

            if node.left:
                stack.append(
                    (node.left, total + node.left.value)
                )

        return False

    def all_path_sums(self, target: int) -> list[list[int]]:
        """Return every root-to-leaf path matching the target."""
        result = []
        path = []

        def search(node: Optional[TreeNode], remaining: int):
            if not node:
                return

            path.append(node.value)
            remaining -= node.value

            if not node.left and not node.right:
                if remaining == 0:
                    result.append(path.copy())
            else:
                search(node.left, remaining)
                search(node.right, remaining)

            path.pop()

        search(self.root, target)
        return result

    def lowest_common_ancestor(
        self,
        first: int,
        second: int
    ) -> Optional[TreeNode]:
        """
        Find LCA in a general binary tree.
        Returns None if either value is absent.
        Values must be unique.
        """
        if not self.root:
            return None

        def find(node):
            if not node:
                return None

            if node.value in (first, second):
                return node

            left = find(node.left)
            right = find(node.right)

            if left and right:
                return node

            return left or right

        ancestor = find(self.root)

        def contains(node, value):
            if not node:
                return False

            return (
                node.value == value
                or contains(node.left, value)
                or contains(node.right, value)
            )

        if (
            ancestor is None
            or not contains(self.root, first)
            or not contains(self.root, second)
        ):
            return None

        return ancestor

    def right_side_view(self) -> list[int]:
        """Visible node values when viewed from the right."""
        levels = self.level_order()
        return [level[-1] for level in levels]

    def minimum_depth(self) -> int:
        """Shortest root-to-leaf path measured in nodes."""
        if not self.root:
            return 0

        queue = deque([(self.root, 1)])

        while queue:
            node, depth = queue.popleft()

            if not node.left and not node.right:
                return depth

            if node.left:
                queue.append((node.left, depth + 1))

            if node.right:
                queue.append((node.right, depth + 1))

        return 0

    def count_nodes(self) -> int:
        return len(self.preorder())

    def maximum_path_sum(self) -> Optional[int]:
        """Maximum sum over any non-empty path."""
        if not self.root:
            return None

        maximum = float("-inf")

        def calculate(node):
            nonlocal maximum

            if not node:
                return 0

            left = max(0, calculate(node.left))
            right = max(0, calculate(node.right))

            maximum = max(
                maximum,
                node.value + left + right
            )

            return node.value + max(left, right)

        calculate(self.root)
        return int(maximum)


def build_sample_tree() -> BinaryTree:
    root = TreeNode(
        10,
        TreeNode(
            5,
            TreeNode(3, TreeNode(1), TreeNode(4)),
            TreeNode(7, None, TreeNode(8))
        ),
        TreeNode(
            15,
            None,
            TreeNode(20)
        )
    )

    return BinaryTree(root)


def run_tests():
    tree = build_sample_tree()

    assert tree.preorder() == [
        10, 5, 3, 1, 4, 7, 8, 15, 20
    ]

    assert tree.inorder() == [
        1, 3, 4, 5, 7, 8, 10, 15, 20
    ]

    assert tree.postorder() == [
        1, 4, 3, 8, 7, 5, 20, 15, 10
    ]

    assert tree.level_order() == [
        [10], [5, 15], [3, 7, 20],
        [1, 4, 8]
    ]

    assert tree.height() == 3
    assert tree.diameter() == 6
    assert tree.is_balanced()
    assert tree.has_path_sum(19)
    assert not tree.has_path_sum(100)

    assert tree.all_path_sums(19) == [
        [10, 5, 3, 1]
    ]

    assert tree.lowest_common_ancestor(1, 8).value == 5
    assert tree.lowest_common_ancestor(1, 20).value == 10
    assert tree.lowest_common_ancestor(1, 999) is None

    assert tree.right_side_view() == [10, 15, 20, 8]
    assert tree.minimum_depth() == 3
    assert tree.count_nodes() == 9
    assert tree.maximum_path_sum() == 54

    empty = BinaryTree()
    assert empty.height() == -1
    assert empty.diameter() == 0
    assert empty.is_balanced()
    assert empty.level_order() == []
    assert not empty.has_path_sum(0)
    assert empty.minimum_depth() == 0
    assert empty.maximum_path_sum() is None

    single = BinaryTree(TreeNode(-5))
    assert single.height() == 0
    assert single.diameter() == 0
    assert single.has_path_sum(-5)
    assert single.maximum_path_sum() == -5

    unbalanced = BinaryTree(
        TreeNode(
            1,
            TreeNode(
                2,
                TreeNode(3, TreeNode(4))
            )
        )
    )

    assert not unbalanced.is_balanced()

    try:
        shared = TreeNode(2)
        BinaryTree(TreeNode(1, shared, shared))
        raise AssertionError("Shared child should be rejected.")
    except TreeValidationError:
        pass

    try:
        cyclic = TreeNode(1)
        cyclic.left = cyclic
        BinaryTree(cyclic)
        raise AssertionError("Cycle should be rejected.")
    except TreeValidationError:
        pass

    print("All tree assessment tests passed.")


def display_assessment(tree: BinaryTree):
    print("\nTREE ASSESSMENT")
    print("=" * 45)
    print("Preorder:", tree.preorder())
    print("Inorder:", tree.inorder())
    print("Postorder:", tree.postorder())
    print("Level order:", tree.level_order())
    print("Zigzag:", tree.zigzag_level_order())
    print("Height:", tree.height())
    print("Diameter:", tree.diameter())
    print("Balanced:", tree.is_balanced())
    print("Minimum depth:", tree.minimum_depth())
    print("Node count:", tree.count_nodes())
    print("Right view:", tree.right_side_view())
    print("Maximum path sum:", tree.maximum_path_sum())
    print("Path sum 19:", tree.has_path_sum(19))
    print("Matching paths:", tree.all_path_sums(19))

    ancestor = tree.lowest_common_ancestor(1, 8)
    print(
        "LCA of 1 and 8:",
        ancestor.value if ancestor else None
    )


if __name__ == "__main__":
    run_tests()
    display_assessment(build_sample_tree())
