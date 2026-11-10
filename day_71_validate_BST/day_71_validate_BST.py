"""
VALIDATE BINARY SEARCH TREE (BST)
=================================

Concepts:
1. Range-based BST validation.
2. Inorder-based BST validation.
3. Duplicate-key policies.
4. Minimum and maximum node.
5. Inorder successor and predecessor.
6. Search, insertion, and deletion.
7. Lowest common ancestor.
8. BST construction and traversal.
9. Edge-case validation and automated tests.

Runtime: Python 3.10+
Dependencies: Python standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterable
import json


class DuplicatePolicy(Enum):
    FORBID = "forbid"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


class BSTError(Exception):
    """Base exception for BST operations."""


class DuplicateKeyError(BSTError):
    """Raised when insertion violates the duplicate policy."""


class InvalidBSTError(BSTError):
    """Raised when an operation requires a valid BST."""


class BinarySearchTree:
    def __init__(
        self,
        duplicate_policy: DuplicatePolicy = DuplicatePolicy.FORBID
    ):
        self.root: Optional[Node] = None
        self.duplicate_policy = duplicate_policy
        self.size = 0

    def insert(self, key: int) -> None:
        if not isinstance(key, int) or isinstance(key, bool):
            raise TypeError("BST keys must be integers.")

        if self.root is None:
            self.root = Node(key)
            self.size = 1
            return

        current = self.root

        while True:
            if key < current.key:
                if current.left is None:
                    current.left = Node(key)
                    self.size += 1
                    return
                current = current.left

            elif key > current.key:
                if current.right is None:
                    current.right = Node(key)
                    self.size += 1
                    return
                current = current.right

            else:
                if self.duplicate_policy == DuplicatePolicy.FORBID:
                    raise DuplicateKeyError(f"Duplicate key: {key}")

                if self.duplicate_policy == DuplicatePolicy.LEFT:
                    if current.left is None:
                        current.left = Node(key)
                        self.size += 1
                        return
                    current = current.left

                else:
                    if current.right is None:
                        current.right = Node(key)
                        self.size += 1
                        return
                    current = current.right

    def search(self, key: int) -> Optional[Node]:
        current = self.root

        while current:
            if key == current.key:
                return current
            current = current.left if key < current.key else current.right

        return None

    @staticmethod
    def validate_range(
        root: Optional[Node],
        low: Optional[int] = None,
        high: Optional[int] = None,
        low_inclusive: bool = False,
        high_inclusive: bool = False
    ) -> bool:
        """
        Validate every node against its permitted ancestor-derived range.

        None represents an unbounded side, so integer boundary values
        do not require special handling.
        """
        if root is None:
            return True

        if low is not None:
            if root.key < low:
                return False
            if root.key == low and not low_inclusive:
                return False

        if high is not None:
            if root.key > high:
                return False
            if root.key == high and not high_inclusive:
                return False

        allow_equal_left = low_inclusive
        allow_equal_right = high_inclusive

        return (
            BinarySearchTree.validate_range(
                root.left,
                low,
                root.key,
                allow_equal_left,
                False
            )
            and
            BinarySearchTree.validate_range(
                root.right,
                root.key,
                high,
                False,
                allow_equal_right
            )
        )

    @staticmethod
    def validate_inorder(
        root: Optional[Node],
        duplicate_policy: DuplicatePolicy = DuplicatePolicy.FORBID
    ) -> bool:
        """
        An inorder traversal must produce a nondecreasing sequence.

        Strictly increasing order is required when duplicates are forbidden.
        """
        stack = []
        current = root
        previous = None
        has_previous = False

        while current or stack:
            while current:
                stack.append(current)
                current = current.left

            current = stack.pop()

            if has_previous:
                if duplicate_policy == DuplicatePolicy.FORBID:
                    if current.key <= previous:
                        return False
                elif current.key < previous:
                    return False

            previous = current.key
            has_previous = True
            current = current.right

        return True

    def is_valid(self) -> bool:
        if self.duplicate_policy == DuplicatePolicy.FORBID:
            return self.validate_range(self.root)

        if self.duplicate_policy == DuplicatePolicy.LEFT:
            return self.validate_range(
                self.root,
                low_inclusive=False,
                high_inclusive=False
            ) and self._validate_duplicate_policy()

        return self.validate_inorder(
            self.root,
            self.duplicate_policy
        ) and self._validate_duplicate_policy()

    def _validate_duplicate_policy(self) -> bool:
        """
        Validate the structural duplicate-placement convention.

        A duplicate must be in the permitted subtree of an equal ancestor.
        """
        stack = [(self.root, [])]

        while stack:
            node, ancestors = stack.pop()

            if node is None:
                continue

            for ancestor_key, side in ancestors:
                if node.key == ancestor_key:
                    if self.duplicate_policy == DuplicatePolicy.LEFT:
                        if side != "left":
                            return False
                    elif self.duplicate_policy == DuplicatePolicy.RIGHT:
                        if side != "right":
                            return False

            stack.append(
                (node.left, ancestors + [(node.key, "left")])
            )
            stack.append(
                (node.right, ancestors + [(node.key, "right")])
            )

        return True

    def inorder(self) -> list[int]:
        result = []
        stack = []
        current = self.root

        while current or stack:
            while current:
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append(current.key)
            current = current.right

        return result

    def preorder(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        stack = [self.root]

        while stack:
            node = stack.pop()
            result.append(node.key)

            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)

        return result

    def postorder(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        stack = [(self.root, False)]

        while stack:
            node, visited = stack.pop()

            if visited:
                result.append(node.key)
                continue

            stack.append((node, True))

            if node.right:
                stack.append((node.right, False))
            if node.left:
                stack.append((node.left, False))

        return result

    def minimum(self, node: Optional[Node] = None) -> Optional[Node]:
        current = node if node is not None else self.root

        if current is None:
            return None

        while current.left:
            current = current.left

        return current

    def maximum(self, node: Optional[Node] = None) -> Optional[Node]:
        current = node if node is not None else self.root

        if current is None:
            return None

        while current.right:
            current = current.right

        return current

    def successor(self, key: int) -> Optional[int]:
        """
        Find the smallest key strictly greater than the supplied key.
        The key need not be present in the tree.
        """
        current = self.root
        candidate = None

        while current:
            if key < current.key:
                candidate = current
                current = current.left
            else:
                current = current.right

        return candidate.key if candidate else None

    def predecessor(self, key: int) -> Optional[int]:
        """
        Find the largest key strictly smaller than the supplied key.
        The key need not be present in the tree.
        """
        current = self.root
        candidate = None

        while current:
            if key > current.key:
                candidate = current
                current = current.right
            else:
                current = current.left

        return candidate.key if candidate else None

    def successor_of_node(self, key: int) -> Optional[int]:
        """
        Find the inorder successor of an existing node.

        If a right subtree exists, its minimum is the successor.
        Otherwise, the lowest ancestor reached from its left subtree
        is the successor.
        """
        current = self.root
        successor_node = None

        while current:
            if key < current.key:
                successor_node = current
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                if current.right:
                    return self.minimum(current.right).key
                return (
                    successor_node.key
                    if successor_node else None
                )

        return None

    def predecessor_of_node(self, key: int) -> Optional[int]:
        current = self.root
        predecessor_node = None

        while current:
            if key > current.key:
                predecessor_node = current
                current = current.right
            elif key < current.key:
                current = current.left
            else:
                if current.left:
                    return self.maximum(current.left).key
                return (
                    predecessor_node.key
                    if predecessor_node else None
                )

        return None

    def lowest_common_ancestor(
        self,
        first: int,
        second: int
    ) -> Optional[int]:
        if not self.search(first) or not self.search(second):
            return None

        current = self.root

        while current:
            if first < current.key and second < current.key:
                current = current.left
            elif first > current.key and second > current.key:
                current = current.right
            else:
                return current.key

        return None

    def delete(self, key: int) -> bool:
        """
        Delete one matching node.

        Handles:
        - Leaf nodes.
        - Nodes with one child.
        - Nodes with two children.
        """
        parent = None
        current = self.root

        while current and current.key != key:
            parent = current
            current = current.left if key < current.key else current.right

        if current is None:
            return False

        if current.left and current.right:
            successor_parent = current
            successor_node = current.right

            while successor_node.left:
                successor_parent = successor_node
                successor_node = successor_node.left

            current.key = successor_node.key

            if successor_parent == current:
                successor_parent.right = successor_node.right
            else:
                successor_parent.left = successor_node.right

        else:
            child = current.left or current.right

            if parent is None:
                self.root = child
            elif parent.left == current:
                parent.left = child
            else:
                parent.right = child

        self.size -= 1
        return True

    @classmethod
    def from_iterable(
        cls,
        values: Iterable[int],
        duplicate_policy: DuplicatePolicy = DuplicatePolicy.FORBID
    ) -> "BinarySearchTree":
        tree = cls(duplicate_policy)

        for value in values:
            tree.insert(value)

        return tree

    def to_dict(self) -> Optional[dict]:
        """Export the tree as nested JSON-compatible dictionaries."""

        def serialize(node):
            if node is None:
                return None

            return {
                "key": node.key,
                "left": serialize(node.left),
                "right": serialize(node.right)
            }

        return serialize(self.root)


def demonstrate_validation() -> None:
    print("\n1. RANGE-BASED VALIDATION")

    valid = Node(
        10,
        Node(5, Node(2), Node(8)),
        Node(15, Node(12), Node(20))
    )

    invalid = Node(
        10,
        Node(5, None, Node(12)),
        Node(15)
    )

    print("Valid tree:", BinarySearchTree.validate_range(valid))
    print("Invalid tree:", BinarySearchTree.validate_range(invalid))

    print("\n2. INORDER-BASED VALIDATION")

    print("Valid tree:", BinarySearchTree.validate_inorder(valid))
    print("Invalid tree:", BinarySearchTree.validate_inorder(invalid))

    print("\n3. DUPLICATE KEY VALIDATION")

    duplicate_tree = Node(
        10,
        Node(10),
        Node(15)
    )

    print(
        "Duplicates forbidden:",
        BinarySearchTree.validate_inorder(
            duplicate_tree,
            DuplicatePolicy.FORBID
        )
    )

    print(
        "Nondecreasing inorder:",
        BinarySearchTree.validate_inorder(
            duplicate_tree,
            DuplicatePolicy.LEFT
        )
    )


def demonstrate_operations() -> None:
    print("\n4. BST OPERATIONS")

    tree = BinarySearchTree.from_iterable(
        [50, 30, 70, 20, 40, 60, 80]
    )

    print("Inorder:", tree.inorder())
    print("Preorder:", tree.preorder())
    print("Postorder:", tree.postorder())

    minimum = tree.minimum()
    maximum = tree.maximum()

    print("Minimum:", minimum.key if minimum else None)
    print("Maximum:", maximum.key if maximum else None)

    print("\n5. SUCCESSOR AND PREDECESSOR")

    for key in [20, 30, 40, 50, 60, 70, 80, 55]:
        print(
            f"Key {key}: "
            f"successor={tree.successor(key)}, "
            f"predecessor={tree.predecessor(key)}"
        )

    print("\nExisting-node successor of 50:",
          tree.successor_of_node(50))

    print("Existing-node predecessor of 50:",
          tree.predecessor_of_node(50))

    print("\n6. LOWEST COMMON ANCESTOR")

    print("LCA(20, 40):", tree.lowest_common_ancestor(20, 40))
    print("LCA(20, 80):", tree.lowest_common_ancestor(20, 80))

    print("\n7. DELETION")

    print("Delete 20:", tree.delete(20))
    print("Delete 30:", tree.delete(30))
    print("Delete 50:", tree.delete(50))
    print("After deletion:", tree.inorder())
    print("Tree size:", tree.size)

    print("\n8. SERIALIZATION")

    print(json.dumps(tree.to_dict(), indent=2))


def run_tests() -> None:
    print("\n9. AUTOMATED TESTS")

    tree = BinarySearchTree.from_iterable(
        [50, 30, 70, 20, 40, 60, 80]
    )

    assert tree.is_valid()
    assert tree.search(40) is not None
    assert tree.search(100) is None

    assert tree.inorder() == [20, 30, 40, 50, 60, 70, 80]

    assert tree.successor(40) == 50
    assert tree.predecessor(40) == 30

    assert tree.successor(80) is None
    assert tree.predecessor(20) is None

    assert tree.successor_of_node(50) == 60
    assert tree.predecessor_of_node(50) == 40

    assert tree.lowest_common_ancestor(20, 40) == 30
    assert tree.lowest_common_ancestor(20, 80) == 50

    assert tree.delete(20)
    assert tree.delete(30)
    assert tree.delete(50)
    assert not tree.delete(999)

    assert tree.is_valid()
    assert tree.size == 4

    empty = BinarySearchTree()
    assert empty.is_valid()
    assert empty.inorder() == []
    assert empty.successor(10) is None

    single = BinarySearchTree()
    single.insert(42)

    assert single.inorder() == [42]
    assert single.successor(42) is None
    assert single.predecessor(42) is None

    extreme = Node(
        0,
        Node(-10**100),
        Node(10**100)
    )
    assert BinarySearchTree.validate_range(extreme)

    invalid_global = Node(
        10,
        Node(5, None, Node(12)),
        Node(15)
    )
    assert not BinarySearchTree.validate_range(invalid_global)

    try:
        tree.insert(40)
        raise AssertionError("Duplicate insertion should fail.")
    except DuplicateKeyError:
        pass

    try:
        tree.insert(True)
        raise AssertionError("Boolean key should fail.")
    except TypeError:
        pass

    print("All tests passed.")


def main() -> None:
    demonstrate_validation()
    demonstrate_operations()
    run_tests()


if __name__ == "__main__":
    main()
