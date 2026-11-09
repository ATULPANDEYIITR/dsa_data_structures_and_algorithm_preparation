#!/usr/bin/env python3
"""
Binary Search Tree Deletion
===========================

Demonstrates:
1. Deleting a leaf node.
2. Deleting a node with one child.
3. Deleting a node with two children.
4. Inorder successor and predecessor.
5. Recursive and iterative traversal.
6. BST invariant validation.
7. Edge cases and automated assertions.

Duplicate keys are rejected.
Python 3.10+
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterator


@dataclass
class Node:
    key: int
    left: Optional[Node] = None
    right: Optional[Node] = None


class BinarySearchTree:
    def __init__(self) -> None:
        self.root: Optional[Node] = None
        self.size = 0

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise TypeError("BST keys must be integers.")

    def insert(self, key: int) -> bool:
        """Insert a unique key using iterative traversal."""
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
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    break
                current = current.right

        self.size += 1
        return True

    def search(self, key: int) -> Optional[Node]:
        self._validate_key(key)
        current = self.root

        while current is not None:
            if key == current.key:
                return current
            current = current.left if key < current.key else current.right

        return None

    @staticmethod
    def minimum(node: Optional[Node]) -> Optional[Node]:
        """Find the smallest key in a subtree."""
        if node is None:
            return None

        while node.left is not None:
            node = node.left

        return node

    @staticmethod
    def maximum(node: Optional[Node]) -> Optional[Node]:
        """Find the largest key in a subtree."""
        if node is None:
            return None

        while node.right is not None:
            node = node.right

        return node

    def successor(self, key: int) -> Optional[int]:
        """
        Find the inorder successor.

        If a right subtree exists, its minimum is the successor.
        Otherwise, the successor is the lowest ancestor greater
        than the requested key.
        """
        self._validate_key(key)

        current = self.root
        candidate = None

        while current is not None:
            if key < current.key:
                candidate = current.key
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                if current.right is not None:
                    return self.minimum(current.right).key
                return candidate

        return None

    def predecessor(self, key: int) -> Optional[int]:
        """
        Find the inorder predecessor.

        If a left subtree exists, its maximum is the predecessor.
        Otherwise, use the lowest ancestor smaller than the key.
        """
        self._validate_key(key)

        current = self.root
        candidate = None

        while current is not None:
            if key > current.key:
                candidate = current.key
                current = current.right
            elif key < current.key:
                current = current.left
            else:
                if current.left is not None:
                    return self.maximum(current.left).key
                return candidate

        return None

    def delete(self, key: int) -> bool:
        """
        Delete a key using the inorder successor.

        Case 1: Leaf node.
        Case 2: Node with one child.
        Case 3: Node with two children.

        Returns False if the key does not exist.
        """

        self._validate_key(key)

        self.root, deleted = self._delete_recursive(self.root, key)

        if deleted:
            self.size -= 1

        return deleted

    def _delete_recursive(
        self,
        node: Optional[Node],
        key: int
    ) -> tuple[Optional[Node], bool]:

        if node is None:
            return None, False

        if key < node.key:
            node.left, deleted = self._delete_recursive(node.left, key)
            return node, deleted

        if key > node.key:
            node.right, deleted = self._delete_recursive(node.right, key)
            return node, deleted

        # Case 1: Leaf node.
        if node.left is None and node.right is None:
            return None, True

        # Case 2a: Only right child.
        if node.left is None:
            return node.right, True

        # Case 2b: Only left child.
        if node.right is None:
            return node.left, True

        # Case 3: Two children.
        # Copy the inorder successor's key.
        successor = self.minimum(node.right)
        node.key = successor.key

        # Remove the original successor node.
        node.right, _ = self._delete_recursive(
            node.right,
            successor.key
        )

        return node, True

    def delete_using_predecessor(self, key: int) -> bool:
        """Alternative two-child deletion using inorder predecessor."""
        self._validate_key(key)

        self.root, deleted = self._delete_predecessor_recursive(
            self.root, key
        )

        if deleted:
            self.size -= 1

        return deleted

    def _delete_predecessor_recursive(
        self,
        node: Optional[Node],
        key: int
    ) -> tuple[Optional[Node], bool]:

        if node is None:
            return None, False

        if key < node.key:
            node.left, deleted = self._delete_predecessor_recursive(
                node.left, key
            )
            return node, deleted

        if key > node.key:
            node.right, deleted = self._delete_predecessor_recursive(
                node.right, key
            )
            return node, deleted

        if node.left is None:
            return node.right, True

        if node.right is None:
            return node.left, True

        predecessor = self.maximum(node.left)
        node.key = predecessor.key

        node.left, _ = self._delete_predecessor_recursive(
            node.left, predecessor.key
        )

        return node, True

    def inorder(self) -> list[int]:
        """Return sorted keys using an iterative traversal."""
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

    def level_order(self) -> list[list[int]]:
        if self.root is None:
            return []

        queue = [self.root]
        result = []
        index = 0

        while index < len(queue):
            level_size = len(queue) - index
            level = []

            for _ in range(level_size):
                node = queue[index]
                index += 1

                level.append(node.key)

                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

            result.append(level)

        return result

    def height(self) -> int:
        """Calculate height iteratively. Empty tree has height zero."""
        if self.root is None:
            return 0

        queue = [(self.root, 1)]
        maximum_height = 0
        index = 0

        while index < len(queue):
            node, depth = queue[index]
            index += 1

            maximum_height = max(maximum_height, depth)

            if node.left:
                queue.append((node.left, depth + 1))

            if node.right:
                queue.append((node.right, depth + 1))

        return maximum_height

    def validate(self) -> bool:
        """Verify strict BST ordering and node count."""
        count = 0
        stack = [(self.root, None, None)]

        while stack:
            node, lower, upper = stack.pop()

            if node is None:
                continue

            if lower is not None and node.key <= lower:
                return False

            if upper is not None and node.key >= upper:
                return False

            count += 1

            stack.append((node.left, lower, node.key))
            stack.append((node.right, node.key, upper))

        return count == self.size

    def display(self) -> None:
        print("Inorder:   ", self.inorder())
        print("Preorder:  ", self.preorder())
        print("Postorder: ", self.postorder())
        print("Levels:    ", self.level_order())
        print("Height:    ", self.height())
        print("Size:      ", self.size)
        print("Valid BST: ", self.validate())


def demonstrate_deletion() -> None:
    tree = BinarySearchTree()

    values = [50, 30, 70, 20, 40, 60, 80, 35, 45, 65]

    for value in values:
        assert tree.insert(value)

    print("\nINITIAL TREE")
    tree.display()

    print("\nSUCCESSOR AND PREDECESSOR")
    for key in [20, 30, 40, 50, 60, 70, 80]:
        print(
            f"{key}: predecessor={tree.predecessor(key)}, "
            f"successor={tree.successor(key)}"
        )

    # Leaf deletion.
    print("\nCASE 1: DELETE LEAF NODE 20")
    assert tree.delete(20)
    assert tree.inorder() == [30, 35, 40, 45, 50, 60, 65, 70, 80]
    tree.display()

    # One-child deletion.
    print("\nCASE 2: DELETE NODE 60 WITH ONE CHILD")
    assert tree.delete(60)
    assert tree.inorder() == [30, 35, 40, 45, 50, 65, 70, 80]
    tree.display()

    # Two-child deletion.
    print("\nCASE 3: DELETE NODE 70 WITH TWO CHILDREN")
    assert tree.delete(70)
    assert tree.inorder() == [30, 35, 40, 45, 50, 65, 80]
    tree.display()

    # Root deletion.
    print("\nCASE 4: DELETE ROOT NODE 50")
    assert tree.delete(50)
    assert tree.inorder() == [30, 35, 40, 45, 65, 80]
    tree.display()

    # Alternative predecessor deletion.
    print("\nCASE 5: DELETE USING PREDECESSOR")
    assert tree.delete_using_predecessor(40)
    assert tree.validate()
    tree.display()

    # Missing key.
    print("\nCASE 6: DELETE MISSING KEY")
    assert not tree.delete(999)
    assert tree.validate()

    # Duplicate insertion.
    print("\nCASE 7: DUPLICATE INSERTION")
    assert not tree.insert(35)

    # Empty tree.
    print("\nCASE 8: DELETE ALL NODES")
    for key in tree.inorder():
        assert tree.delete(key)

    assert tree.root is None
    assert tree.size == 0
    assert tree.validate()
    assert tree.delete(100) is False
    print("Empty tree handled correctly.")

    # Single-node tree.
    print("\nCASE 9: SINGLE NODE")
    assert tree.insert(10)
    assert tree.delete(10)
    assert tree.root is None

    # Invalid input.
    print("\nCASE 10: INPUT VALIDATION")
    try:
        tree.insert(True)
    except TypeError as error:
        print("Expected validation error:", error)

    print("\nALL ASSERTIONS PASSED.")


if __name__ == "__main__":
    demonstrate_deletion()
