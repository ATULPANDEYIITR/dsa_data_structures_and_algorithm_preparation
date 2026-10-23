from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class TreeNode:
    label: str
    children: list["TreeNode"]

    def __init__(self, label: str) -> None:
        self.label = label
        self.children = []


def fibonacci_tree(n: int) -> TreeNode:
    """Build the recursion tree for the naive recursive Fibonacci algorithm."""
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")

    node = TreeNode(f"fib({n})")

    if n <= 1:
        return node

    node.children.append(fibonacci_tree(n - 1))
    node.children.append(fibonacci_tree(n - 2))
    return node


def subset_tree(items: list[str]) -> TreeNode:
    """
    Build the binary recursion tree used to enumerate all subsets.

    At each level:
      - exclude the current item
      - include the current item
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    def build(index: int, selected: tuple[str, ...]) -> TreeNode:
        if index == len(items):
            suffix = "{" + ", ".join(selected) + "}"
            return TreeNode(f"subset {suffix}")

        item = items[index]
        node = TreeNode(f"item={item}")

        exclude_node = build(index + 1, selected)
        exclude_node.label = f"exclude {item} -> {exclude_node.label}"

        include_node = build(index + 1, selected + (item,))
        include_node.label = f"include {item} -> {include_node.label}"

        node.children.extend([exclude_node, include_node])
        return node

    return build(0, ())


def binary_choice_tree(depth: int) -> TreeNode:
    """Build a generic binary-choice recursion tree of a given depth."""
    if not isinstance(depth, int):
        raise TypeError("depth must be an integer")
    if depth < 0:
        raise ValueError("depth must be non-negative")

    def build(level: int, choices: str) -> TreeNode:
        node = TreeNode(
            f"level={level}, choices={choices or '∅'}"
        )

        if level == depth:
            return node

        node.children.append(build(level + 1, choices + "0"))
        node.children.append(build(level + 1, choices + "1"))
        return node

    return build(0, "")


def merge_sort_tree(values: list[int]) -> TreeNode:
    """
    Build the recursion tree for merge sort.

    This illustrates divide-and-conquer:
      divide -> recursively solve halves -> combine.
    """
    if not isinstance(values, list):
        raise TypeError("values must be a list")
    if not all(isinstance(value, int) for value in values):
        raise TypeError("all values must be integers")

    def build(data: list[int]) -> TreeNode:
        node = TreeNode(f"sort({data})")

        if len(data) <= 1:
            return node

        midpoint = len(data) // 2
        left = data[:midpoint]
        right = data[midpoint:]

        node.children.append(build(left))
        node.children.append(build(right))
        return node

    return build(values)


def print_tree(root: TreeNode, prefix: str = "", is_last: bool = True) -> None:
    """Render a recursion tree using Unicode branch characters."""
    connector = "└── " if is_last else "├── "
    print(prefix + connector + root.label)

    child_prefix = prefix + ("    " if is_last else "│   ")

    for index, child in enumerate(root.children):
        print_tree(
            child,
            child_prefix,
            index == len(root.children) - 1,
        )


def count_nodes(root: TreeNode) -> int:
    """Count every recursive call represented by a tree node."""
    return 1 + sum(count_nodes(child) for child in root.children)


def tree_height(root: TreeNode) -> int:
    """Return the number of levels represented by the tree."""
    if not root.children:
        return 1
    return 1 + max(tree_height(child) for child in root.children)


def fibonacci_value(n: int) -> int:
    """Compute Fibonacci iteratively to avoid exponential recursion."""
    if n < 0:
        raise ValueError("n must be non-negative")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def subsets(items: Iterable[str]) -> list[tuple[str, ...]]:
    """Generate subsets while avoiding recursion-tree rendering overhead."""
    values = list(items)

    result: list[tuple[str, ...]] = []

    def generate(index: int, selected: tuple[str, ...]) -> None:
        if index == len(values):
            result.append(selected)
            return

        generate(index + 1, selected)
        generate(index + 1, selected + (values[index],))

    generate(0, ())
    return result


def main() -> None:
    print("FIBONACCI RECURSION TREE")
    fib_root = fibonacci_tree(5)
    print_tree(fib_root)
    print(f"Recursive calls: {count_nodes(fib_root)}")
    print(f"Tree height: {tree_height(fib_root)}")
    print(f"Fibonacci(5): {fibonacci_value(5)}")

    print("\nSUBSET RECURSION TREE")
    subset_root = subset_tree(["A", "B", "C"])
    print_tree(subset_root)

    generated = subsets(["A", "B", "C"])
    print(f"Generated subsets: {len(generated)}")
    print(f"Subsets: {generated}")

    print("\nBINARY CHOICE RECURSION TREE")
    binary_root = binary_choice_tree(3)
    print_tree(binary_root)
    print(f"Leaf choices: {2 ** 3}")

    print("\nDIVIDE-AND-CONQUER RECURSION TREE")
    merge_root = merge_sort_tree([8, 3, 7, 4, 2, 6])
    print_tree(merge_root)
    print(f"Recursive calls: {count_nodes(merge_root)}")
    print(f"Tree height: {tree_height(merge_root)}")


if __name__ == "__main__":
    main()
