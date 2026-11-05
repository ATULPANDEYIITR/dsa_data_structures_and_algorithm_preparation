from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable
import random


class TreeValidationError(ValueError):
    pass


@dataclass
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    height: int = 1


def height(node: Optional[Node]) -> int:
    return node.height if node else 0


def balance_factor(node: Optional[Node]) -> int:
    if node is None:
        return 0
    return height(node.left) - height(node.right)


def update_height(node: Node) -> None:
    node.height = 1 + max(height(node.left), height(node.right))


def rotate_right(y: Node) -> Node:
    x = y.left
    if x is None:
        raise TreeValidationError("Right rotation requires a left child.")

    middle = x.right
    x.right = y
    y.left = middle

    update_height(y)
    update_height(x)
    return x


def rotate_left(x: Node) -> Node:
    y = x.right
    if y is None:
        raise TreeValidationError("Left rotation requires a right child.")

    middle = y.left
    y.left = x
    x.right = middle

    update_height(x)
    update_height(y)
    return y


class AVLTree:
    """Self-balancing binary search tree."""

    def __init__(self):
        self.root: Optional[Node] = None
        self.size = 0

    def insert(self, key: int) -> None:
        if not isinstance(key, int) or isinstance(key, bool):
            raise TreeValidationError("Keys must be integers.")

        self.root, inserted = self._insert(self.root, key)

        if inserted:
            self.size += 1

    def _insert(self, node, key):
        if node is None:
            return Node(key), True

        if key == node.key:
            return node, False

        if key < node.key:
            node.left, inserted = self._insert(node.left, key)
        else:
            node.right, inserted = self._insert(node.right, key)

        if not inserted:
            return node, False

        update_height(node)
        factor = balance_factor(node)

        # Left-left imbalance.
        if factor > 1 and key < node.left.key:
            return rotate_right(node), True

        # Right-right imbalance.
        if factor < -1 and key > node.right.key:
            return rotate_left(node), True

        # Left-right imbalance.
        if factor > 1 and key > node.left.key:
            node.left = rotate_left(node.left)
            return rotate_right(node), True

        # Right-left imbalance.
        if factor < -1 and key < node.right.key:
            node.right = rotate_right(node.right)
            return rotate_left(node), True

        return node, True

    def search(self, key: int) -> bool:
        current = self.root

        while current:
            if key == current.key:
                return True
            current = current.left if key < current.key else current.right

        return False

    def delete(self, key: int) -> bool:
        if not isinstance(key, int) or isinstance(key, bool):
            raise TreeValidationError("Keys must be integers.")

        self.root, deleted = self._delete(self.root, key)

        if deleted:
            self.size -= 1

        return deleted

    def _delete(self, node, key):
        if node is None:
            return None, False

        if key < node.key:
            node.left, deleted = self._delete(node.left, key)
        elif key > node.key:
            node.right, deleted = self._delete(node.right, key)
        else:
            deleted = True

            if node.left is None:
                return node.right, True

            if node.right is None:
                return node.left, True

            # Replace with the smallest key in the right subtree.
            successor = node.right
            while successor.left:
                successor = successor.left

            node.key = successor.key
            node.right, _ = self._delete(node.right, successor.key)

        if not deleted or node is None:
            return node, deleted

        update_height(node)
        factor = balance_factor(node)

        if factor > 1:
            if balance_factor(node.left) < 0:
                node.left = rotate_left(node.left)
            return rotate_right(node), True

        if factor < -1:
            if balance_factor(node.right) > 0:
                node.right = rotate_right(node.right)
            return rotate_left(node), True

        return node, True

    def inorder(self) -> list[int]:
        result = []

        def visit(node):
            if node:
                visit(node.left)
                result.append(node.key)
                visit(node.right)

        visit(self.root)
        return result

    def validate(self) -> dict:
        """Check ordering, stored heights, and AVL balance."""

        def inspect(node, low=None, high=None):
            if node is None:
                return 0, 0

            if low is not None and node.key <= low:
                raise TreeValidationError("BST ordering violation.")

            if high is not None and node.key >= high:
                raise TreeValidationError("BST ordering violation.")

            left_height, left_count = inspect(
                node.left, low, node.key
            )
            right_height, right_count = inspect(
                node.right, node.key, high
            )

            expected_height = 1 + max(left_height, right_height)

            if node.height != expected_height:
                raise TreeValidationError(
                    f"Incorrect height at key {node.key}."
                )

            difference = left_height - right_height

            if abs(difference) > 1:
                raise TreeValidationError(
                    f"AVL violation at key {node.key}: {difference}"
                )

            return expected_height, left_count + right_count + 1

        tree_height, count = inspect(self.root)

        if count != self.size:
            raise TreeValidationError("Tree size mismatch.")

        return {
            "valid": True,
            "height": tree_height,
            "nodes": count,
            "balanced": True,
        }


class BinarySearchTree:
    """Ordinary BST without automatic balancing."""

    def __init__(self):
        self.root: Optional[Node] = None
        self.size = 0

    def insert(self, key: int) -> None:
        if not isinstance(key, int) or isinstance(key, bool):
            raise TreeValidationError("Keys must be integers.")

        if self.root is None:
            self.root = Node(key)
            self.size = 1
            return

        current = self.root

        while True:
            if key == current.key:
                return

            if key < current.key:
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

    def search_with_comparisons(self, key: int) -> tuple[bool, int]:
        comparisons = 0
        current = self.root

        while current:
            comparisons += 1

            if key == current.key:
                return True, comparisons

            current = current.left if key < current.key else current.right

        return False, comparisons

    def height(self) -> int:
        def calculate(node):
            if node is None:
                return 0
            return 1 + max(calculate(node.left), calculate(node.right))

        return calculate(self.root)


def demonstrate():
    print("BALANCED TREES: HEIGHT AND PERFORMANCE")
    print("=" * 55)

    # Fundamental example: balanced AVL insertion.
    avl = AVLTree()

    values = [30, 20, 10, 25, 28, 27, 40, 50, 45]

    for value in values:
        avl.insert(value)
        avl.validate()

    print("\nAVL TREE")
    print("Inserted:", values)
    print("Inorder:", avl.inorder())
    print("Properties:", avl.validate())
    print("Search 28:", avl.search(28))

    # Deletion must preserve AVL balance.
    avl.delete(30)
    print("After deleting 30:", avl.inorder())
    print("Validation:", avl.validate())

    # Demonstrate why an ordinary BST can become inefficient.
    ordinary = BinarySearchTree()

    sorted_values = list(range(1, 16))

    for value in sorted_values:
        ordinary.insert(value)

    found, comparisons = ordinary.search_with_comparisons(15)

    print("\nUNBALANCED BST")
    print("Inserted sorted values:", sorted_values)
    print("Height:", ordinary.height())
    print("Search result:", found)
    print("Comparisons required:", comparisons)

    # Compare search costs using identical key sets.
    random.seed(42)
    shuffled = list(range(1, 101))
    random.shuffle(shuffled)

    balanced = AVLTree()
    skewed = BinarySearchTree()

    for value in shuffled:
        balanced.insert(value)
        skewed.insert(value)

    avl_found = balanced.search(100)
    bst_found, bst_comparisons = skewed.search_with_comparisons(100)

    print("\nPERFORMANCE COMPARISON")
    print("Number of nodes:", len(shuffled))
    print("AVL height:", balanced.validate()["height"])
    print("Ordinary BST height:", skewed.height())
    print("AVL search successful:", avl_found)
    print("Ordinary BST search comparisons:", bst_comparisons)

    # Edge cases.
    empty = AVLTree()
    assert empty.validate()["height"] == 0
    assert not empty.delete(10)

    single = AVLTree()
    single.insert(10)
    single.insert(10)
    assert single.size == 1
    assert single.validate()["height"] == 1
    assert single.delete(10)
    assert single.size == 0

    try:
        avl.insert(True)
    except TreeValidationError as error:
        print("\nExpected validation error:", error)

    print("\nAll assertions passed.")


if __name__ == "__main__":
    demonstrate()
