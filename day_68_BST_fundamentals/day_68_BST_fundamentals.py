from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterator


@dataclass
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


class BinarySearchTree:
    """
    Binary Search Tree with unique integer keys.

    Ordering invariant:
        Every key in the left subtree is smaller.
        Every key in the right subtree is larger.
    """

    def __init__(self) -> None:
        self.root: Optional[Node] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    def insert(self, key: int) -> bool:
        if not isinstance(key, int) or isinstance(key, bool):
            raise TypeError("BST keys must be integers.")

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

    def search(self, key: int) -> bool:
        current = self.root

        while current is not None:
            if key == current.key:
                return True
            current = current.left if key < current.key else current.right

        return False

    def find_min_node(self, node: Optional[Node]) -> Optional[Node]:
        if node is None:
            return None

        while node.left is not None:
            node = node.left

        return node

    def find_max_node(self, node: Optional[Node]) -> Optional[Node]:
        if node is None:
            return None

        while node.right is not None:
            node = node.right

        return node

    def minimum(self) -> Optional[int]:
        node = self.find_min_node(self.root)
        return node.key if node else None

    def maximum(self) -> Optional[int]:
        node = self.find_max_node(self.root)
        return node.key if node else None

    def delete(self, key: int) -> bool:
        if not isinstance(key, int) or isinstance(key, bool):
            raise TypeError("BST keys must be integers.")

        self.root, deleted = self._delete(self.root, key)

        if deleted:
            self._size -= 1

        return deleted

    def _delete(
        self,
        node: Optional[Node],
        key: int
    ) -> tuple[Optional[Node], bool]:

        if node is None:
            return None, False

        if key < node.key:
            node.left, deleted = self._delete(node.left, key)
            return node, deleted

        if key > node.key:
            node.right, deleted = self._delete(node.right, key)
            return node, deleted

        # Case 1: Leaf node.
        if node.left is None and node.right is None:
            return None, True

        # Case 2: Only right child.
        if node.left is None:
            return node.right, True

        # Case 2: Only left child.
        if node.right is None:
            return node.left, True

        # Case 3: Two children.
        # Replace with the smallest key in the right subtree.
        successor = self.find_min_node(node.right)
        assert successor is not None

        node.key = successor.key
        node.right, _ = self._delete(node.right, successor.key)

        return node, True

    def inorder(self) -> list[int]:
        result = []

        def traverse(node: Optional[Node]) -> None:
            if node is None:
                return

            traverse(node.left)
            result.append(node.key)
            traverse(node.right)

        traverse(self.root)
        return result

    def preorder(self) -> list[int]:
        result = []

        def traverse(node: Optional[Node]) -> None:
            if node is None:
                return

            result.append(node.key)
            traverse(node.left)
            traverse(node.right)

        traverse(self.root)
        return result

    def postorder(self) -> list[int]:
        result = []

        def traverse(node: Optional[Node]) -> None:
            if node is None:
                return

            traverse(node.left)
            traverse(node.right)
            result.append(node.key)

        traverse(self.root)
        return result

    def level_order(self) -> list[list[int]]:
        if self.root is None:
            return []

        queue = [self.root]
        result = []

        while queue:
            level = []
            next_level = []

            for node in queue:
                level.append(node.key)

                if node.left:
                    next_level.append(node.left)

                if node.right:
                    next_level.append(node.right)

            result.append(level)
            queue = next_level

        return result

    def height(self) -> int:
        def calculate(node: Optional[Node]) -> int:
            if node is None:
                return -1

            return 1 + max(
                calculate(node.left),
                calculate(node.right)
            )

        return calculate(self.root)

    def depth(self, key: int) -> Optional[int]:
        current = self.root
        depth = 0

        while current is not None:
            if current.key == key:
                return depth

            current = current.left if key < current.key else current.right
            depth += 1

        return None

    def is_valid(self) -> bool:
        def validate(
            node: Optional[Node],
            lower: Optional[int],
            upper: Optional[int]
        ) -> bool:

            if node is None:
                return True

            if lower is not None and node.key <= lower:
                return False

            if upper is not None and node.key >= upper:
                return False

            return (
                validate(node.left, lower, node.key)
                and validate(node.right, node.key, upper)
            )

        return validate(self.root, None, None)

    def kth_smallest(self, k: int) -> int:
        if not isinstance(k, int) or isinstance(k, bool):
            raise TypeError("k must be an integer.")

        if k < 1 or k > self._size:
            raise ValueError("k is outside the valid range.")

        stack = []
        current = self.root
        count = 0

        # Iterative inorder traversal avoids recursive traversal depth.
        while stack or current is not None:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            count += 1

            if count == k:
                return current.key

            current = current.right

        raise RuntimeError("BST structure is inconsistent.")

    def to_balanced_bst(self) -> "BinarySearchTree":
        """Create a balanced BST from the sorted inorder values."""
        values = self.inorder()
        balanced = BinarySearchTree()

        def build(start: int, end: int) -> Optional[Node]:
            if start > end:
                return None

            middle = (start + end) // 2
            node = Node(values[middle])

            node.left = build(start, middle - 1)
            node.right = build(middle + 1, end)

            return node

        balanced.root = build(0, len(values) - 1)
        balanced._size = len(values)

        return balanced

    def __iter__(self) -> Iterator[int]:
        return iter(self.inorder())


def demonstrate() -> None:
    print("BINARY SEARCH TREE FUNDAMENTALS")
    print("=" * 45)

    tree = BinarySearchTree()

    values = [50, 30, 70, 20, 40, 60, 80, 35, 45]

    print("\n1. INSERTION")
    for value in values:
        print(f"Insert {value}: {tree.insert(value)}")

    print("Duplicate insertion:", tree.insert(50))

    print("\n2. TREE TRAVERSALS")
    print("Inorder:    ", tree.inorder())
    print("Preorder:   ", tree.preorder())
    print("Postorder:  ", tree.postorder())
    print("Level order:", tree.level_order())

    print("\n3. SEARCH")
    print("Search 40:", tree.search(40))
    print("Search 99:", tree.search(99))

    print("\n4. MINIMUM AND MAXIMUM")
    print("Minimum:", tree.minimum())
    print("Maximum:", tree.maximum())

    print("\n5. HEIGHT AND DEPTH")
    print("Height:", tree.height())
    print("Depth of 40:", tree.depth(40))
    print("Depth of 99:", tree.depth(99))

    print("\n6. KTH SMALLEST")
    print("3rd smallest:", tree.kth_smallest(3))
    print("5th smallest:", tree.kth_smallest(5))

    print("\n7. DELETION")
    for value in [20, 30, 70, 999]:
        print(f"Delete {value}: {tree.delete(value)}")
        print("Current inorder:", tree.inorder())

    print("\n8. VALIDATION")
    print("Valid BST:", tree.is_valid())

    print("\n9. BALANCED TREE")
    balanced = tree.to_balanced_bst()
    print("Original height:", tree.height())
    print("Balanced height:", balanced.height())
    print("Balanced inorder:", balanced.inorder())
    print("Balanced preorder:", balanced.preorder())

    print("\n10. ITERATION")
    print(list(balanced))

    print("\n11. EDGE CASES")
    empty = BinarySearchTree()
    print("Empty tree:", empty.is_empty())
    print("Empty inorder:", empty.inorder())
    print("Empty minimum:", empty.minimum())

    single = BinarySearchTree()
    single.insert(10)
    print("Single-node deletion:", single.delete(10))
    print("Empty after deletion:", single.is_empty())

    try:
        balanced.kth_smallest(100)
    except ValueError as error:
        print("Invalid k:", error)

    try:
        balanced.insert(3.14)
    except TypeError as error:
        print("Invalid key:", error)

    print("\n12. AUTOMATED ASSERTIONS")

    test = BinarySearchTree()

    for value in [8, 4, 12, 2, 6, 10, 14]:
        assert test.insert(value)

    assert not test.insert(8)
    assert test.search(6)
    assert not test.search(100)
    assert test.inorder() == [2, 4, 6, 8, 10, 12, 14]
    assert test.minimum() == 2
    assert test.maximum() == 14
    assert test.kth_smallest(4) == 8
    assert test.delete(4)
    assert test.inorder() == [2, 6, 8, 10, 12, 14]
    assert test.is_valid()
    assert len(test) == 6

    print("All assertions passed.")


if __name__ == "__main__":
    demonstrate()
