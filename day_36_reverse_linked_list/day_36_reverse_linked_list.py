from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class Node:
    """A single node in a singly linked list."""
    value: int
    next: Optional["Node"] = None


class LinkedList:
    """Singly linked list supporting iterative and recursive reversal."""

    def __init__(self, values: Iterable[int] = ()) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.size = 0

        for value in values:
            self.append(value)

    def append(self, value: int) -> None:
        """Append a node while maintaining head, tail, and size invariants."""
        new_node = Node(value)

        if self.head is None:
            self.head = self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node

        self.size += 1

    def to_list(self) -> list[int]:
        """Materialize the linked list while detecting accidental cycles."""
        values: list[int] = []
        current = self.head
        visited: set[int] = set()

        while current is not None:
            identity = id(current)
            if identity in visited:
                raise RuntimeError("Cycle detected while traversing linked list.")

            visited.add(identity)
            values.append(current.value)
            current = current.next

        return values

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return " -> ".join(map(str, self.to_list())) if self.head else "EMPTY"

    def _recalculate_tail(self) -> None:
        """Restore the tail reference after operations that change node links."""
        current = self.head

        if current is None:
            self.tail = None
            return

        while current.next is not None:
            current = current.next

        self.tail = current

    def reverse_iterative(self) -> None:
        """
        Reverse the list by changing one next pointer at a time.

        At each iteration:
            previous -> already reversed prefix
            current  -> first node not yet reversed
            following -> remaining unreversed suffix

        Time: O(n)
        Extra space: O(1)
        """
        previous: Optional[Node] = None
        current = self.head
        old_head = self.head

        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following

        self.head = previous
        self.tail = old_head

    def reverse_recursive(self) -> None:
        """
        Reverse the list recursively.

        The recursive helper reaches the original tail first. During
        unwinding, each predecessor is attached after its successor.

        Time: O(n)
        Extra space: O(n) because of the call stack.
        """
        def reverse(node: Optional[Node]) -> Optional[Node]:
            if node is None or node.next is None:
                return node

            new_head = reverse(node.next)

            # node.next is the successor after the suffix has been reversed.
            assert node.next is not None
            node.next.next = node
            node.next = None

            return new_head

        old_head = self.head
        self.head = reverse(self.head)
        self.tail = old_head

    def reverse_recursive_safe(self) -> None:
        """
        Recursive reversal with an explicit size guard.

        Python's recursion limit makes recursion unsuitable for very long
        linked lists. This method raises a clear exception before recursion
        becomes unsafe rather than relying on RecursionError.
        """
        import sys

        if self.size > sys.getrecursionlimit() - 50:
            raise RecursionError(
                f"Recursive reversal is unsafe for a list of size {self.size}; "
                f"Python recursion limit is {sys.getrecursionlimit()}."
            )

        self.reverse_recursive()


def build_and_show(values: Iterable[int]) -> None:
    """Demonstrate both reversal strategies on the same logical input."""
    original = list(values)

    iterative = LinkedList(original)
    print(f"Original:           {iterative}")
    iterative.reverse_iterative()
    print(f"Iterative reversal: {iterative}")

    recursive = LinkedList(original)
    recursive.reverse_recursive_safe()
    print(f"Recursive reversal: {recursive}")
    print()


def demonstrate_core_mechanism() -> None:
    print("SINGLY LINKED LIST REVERSAL")
    print("============================")

    build_and_show([10, 20, 30, 40, 50])

    print("Single-node edge case")
    build_and_show([42])

    print("Empty-list edge case")
    build_and_show([])

    print("Two-node edge case")
    build_and_show([1, 2])


def demonstrate_pointer_state() -> None:
    """
    Show the state changes of the iterative algorithm.

    This makes the pointer manipulation explicit without using an
    auxiliary collection to perform the reversal.
    """
    values = [1, 2, 3, 4]
    linked_list = LinkedList(values)

    print("ITERATIVE POINTER TRACE")
    print("=======================")

    previous: Optional[Node] = None
    current = linked_list.head

    while current is not None:
        following = current.next

        print(
            f"current={current.value}, "
            f"previous={previous.value if previous else None}, "
            f"following={following.value if following else None}"
        )

        current.next = previous
        previous = current
        current = following

    linked_list.head = previous
    linked_list.tail = Node(0) if False else linked_list.head

    if linked_list.head is not None:
        tail = linked_list.head
        while tail.next is not None:
            tail = tail.next
        linked_list.tail = tail

    print(f"Reversed result: {linked_list}")
    print()


def demonstrate_recursive_structure() -> None:
    """
    Illustrate why recursive reversal needs node.next.next = node.

    For 10 -> 20 -> 30, the recursive call first reaches 30.
    While returning:
        20.next.next = 20
        20.next = None
    Then:
        10.next.next = 10
        10.next = None
    """
    print("RECURSIVE REVERSAL MECHANISM")
    print("============================")

    linked_list = LinkedList([10, 20, 30])
    print(f"Before recursion: {linked_list}")
    linked_list.reverse_recursive()
    print(f"After recursion:  {linked_list}")
    print()


def demonstrate_invariants() -> None:
    """Verify that reversal preserves node count and values."""
    original = [5, 10, 15, 20, 25]

    linked_list = LinkedList(original)
    original_nodes = linked_list.size
    linked_list.reverse_iterative()

    assert linked_list.size == original_nodes
    assert linked_list.to_list() == list(reversed(original))
    assert linked_list.tail is not None
    assert linked_list.tail.next is None

    linked_list.reverse_recursive()

    assert linked_list.size == original_nodes
    assert linked_list.to_list() == original
    assert linked_list.tail is not None
    assert linked_list.tail.next is None

    print("Invariant checks passed:")
    print("- Node count remains unchanged.")
    print("- Iterative reversal produces the exact reverse.")
    print("- Recursive reversal restores the original ordering.")
    print("- Tail always points to the final node.")
    print("- Final tail.next is always None.")
    print()


def demonstrate_large_list() -> None:
    """Compare practical behavior without converting the list to recursion."""
    values = list(range(1, 10_001))
    linked_list = LinkedList(values)

    linked_list.reverse_iterative()

    assert linked_list.head is not None
    assert linked_list.head.value == 10_000
    assert linked_list.tail is not None
    assert linked_list.tail.value == 1

    print("Large-list test")
    print("---------------")
    print(f"Nodes reversed iteratively: {len(linked_list)}")
    print(f"New head: {linked_list.head.value}")
    print(f"New tail: {linked_list.tail.value}")
    print("Iterative reversal remains O(1) auxiliary-space.")
    print()


def demonstrate_failure_conditions() -> None:
    """
    Demonstrate why recursion has a practical limit in Python.

    The iterative algorithm does not consume one Python stack frame per node,
    so it is the preferred implementation for arbitrarily long lists.
    """
    values = list(range(1, 20_001))
    linked_list = LinkedList(values)

    try:
        linked_list.reverse_recursive_safe()
    except RecursionError as exc:
        print("Recursive safety guard:")
        print(exc)
        print("Use iterative reversal for very large linked lists.")
        print()


def explain_complexity() -> None:
    print("COMPLEXITY")
    print("----------")
    print("Iterative reversal: O(n) time, O(1) auxiliary space.")
    print("Recursive reversal:  O(n) time, O(n) call-stack space.")
    print(
        "Both methods reverse the links in place; neither requires a second "
        "linked list."
    )
    print()


def main() -> None:
    demonstrate_core_mechanism()
    demonstrate_pointer_state()
    demonstrate_recursive_structure()
    demonstrate_invariants()
    demonstrate_large_list()
    demonstrate_failure_conditions()
    explain_complexity()


if __name__ == "__main__":
    main()
