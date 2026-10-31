from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass
class TreeNode:
    value: Any
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


class TraversalError(ValueError):
    """Raised when a traversal input is invalid."""


def validate_tree(root: Optional[TreeNode]) -> None:
    """Reject cyclic structures so DFS cannot recurse or iterate forever."""
    if root is None:
        return

    active: set[int] = set()
    visited: set[int] = set()

    def check(node: Optional[TreeNode]) -> None:
        if node is None:
            return

        node_id = id(node)
        if node_id in active:
            raise TraversalError("Cycle detected in tree structure")
        if node_id in visited:
            raise TraversalError("A node has multiple parents; input is not a tree")

        active.add(node_id)
        check(node.left)
        check(node.right)
        active.remove(node_id)
        visited.add(node_id)

    check(root)


def preorder_recursive(root: Optional[TreeNode]) -> list[Any]:
    """Root -> Left -> Right."""
    validate_tree(root)
    result: list[Any] = []

    def visit(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        result.append(node.value)
        visit(node.left)
        visit(node.right)

    visit(root)
    return result


def inorder_recursive(root: Optional[TreeNode]) -> list[Any]:
    """Left -> Root -> Right."""
    validate_tree(root)
    result: list[Any] = []

    def visit(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        visit(node.left)
        result.append(node.value)
        visit(node.right)

    visit(root)
    return result


def postorder_recursive(root: Optional[TreeNode]) -> list[Any]:
    """Left -> Right -> Root."""
    validate_tree(root)
    result: list[Any] = []

    def visit(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        visit(node.left)
        visit(node.right)
        result.append(node.value)

    visit(root)
    return result


def preorder_iterative(root: Optional[TreeNode]) -> list[Any]:
    """Stack-based preorder traversal."""
    validate_tree(root)
    if root is None:
        return []

    result: list[Any] = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.value)

        # Push right first so left is processed first.
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)

    return result


def inorder_iterative(root: Optional[TreeNode]) -> list[Any]:
    """Stack-based inorder traversal."""
    validate_tree(root)
    result: list[Any] = []
    stack: list[TreeNode] = []
    current = root

    while current is not None or stack:
        while current is not None:
            stack.append(current)
            current = current.left

        current = stack.pop()
        result.append(current.value)
        current = current.right

    return result


def postorder_iterative(root: Optional[TreeNode]) -> list[Any]:
    """Two-stack postorder traversal."""
    validate_tree(root)
    if root is None:
        return []

    first = [root]
    second: list[TreeNode] = []

    while first:
        node = first.pop()
        second.append(node)

        if node.left is not None:
            first.append(node.left)
        if node.right is not None:
            first.append(node.right)

    return [node.value for node in reversed(second)]


def postorder_iterative_one_stack(root: Optional[TreeNode]) -> list[Any]:
    """One-stack postorder traversal using the previously visited node."""
    validate_tree(root)
    result: list[Any] = []
    stack: list[TreeNode] = []
    current = root
    previous: Optional[TreeNode] = None

    while current is not None or stack:
        if current is not None:
            stack.append(current)
            current = current.left
            continue

        peek = stack[-1]
        if peek.right is not None and previous is not peek.right:
            current = peek.right
        else:
            result.append(peek.value)
            previous = stack.pop()

    return result


def build_sample_tree() -> TreeNode:
    #                 1
    #               /   \
    #              2     3
    #             / \   / \
    #            4   5 6   7
    return TreeNode(
        1,
        TreeNode(2, TreeNode(4), TreeNode(5)),
        TreeNode(3, TreeNode(6), TreeNode(7)),
    )


def demonstrate() -> None:
    tree = build_sample_tree()

    expected = {
        "preorder": [1, 2, 4, 5, 3, 6, 7],
        "inorder": [4, 2, 5, 1, 6, 3, 7],
        "postorder": [4, 5, 2, 6, 7, 3, 1],
    }

    traversals = {
        "preorder_recursive": preorder_recursive(tree),
        "preorder_iterative": preorder_iterative(tree),
        "inorder_recursive": inorder_recursive(tree),
        "inorder_iterative": inorder_iterative(tree),
        "postorder_recursive": postorder_recursive(tree),
        "postorder_iterative": postorder_iterative(tree),
        "postorder_iterative_one_stack": postorder_iterative_one_stack(tree),
    }

    assert traversals["preorder_recursive"] == expected["preorder"]
    assert traversals["preorder_iterative"] == expected["preorder"]
    assert traversals["inorder_recursive"] == expected["inorder"]
    assert traversals["inorder_iterative"] == expected["inorder"]
    assert traversals["postorder_recursive"] == expected["postorder"]
    assert traversals["postorder_iterative"] == expected["postorder"]
    assert traversals["postorder_iterative_one_stack"] == expected["postorder"]

    for name, values in traversals.items():
        print(f"{name:32}: {values}")

    # Empty-tree behavior.
    assert preorder_recursive(None) == []
    assert inorder_iterative(None) == []
    assert postorder_iterative(None) == []

    # Single-node behavior.
    single = TreeNode(42)
    assert preorder_iterative(single) == [42]
    assert inorder_iterative(single) == [42]
    assert postorder_iterative(single) == [42]

    # Degenerate tree validates iterative traversal without recursion depth
    # being proportional to tree height.
    deep_root = TreeNode(0)
    current = deep_root
    for value in range(1, 5001):
        current.right = TreeNode(value)
        current = current.right

    assert preorder_iterative(deep_root) == list(range(5001))
    assert inorder_iterative(deep_root) == list(range(5001))
    assert postorder_iterative(deep_root) == list(range(4999, -1, -1))

    # Cycle detection prevents infinite traversal.
    cyclic = TreeNode("A")
    cyclic.left = cyclic
    try:
        preorder_iterative(cyclic)
    except TraversalError:
        pass
    else:
        raise AssertionError("Expected cycle detection to reject cyclic input")

    print("\nAll traversal assertions passed.")


if __name__ == "__main__":
    demonstrate()
