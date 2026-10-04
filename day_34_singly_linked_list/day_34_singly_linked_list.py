"""
Singly Linked Lists
====================

A self-contained implementation and teaching example covering:

- Node representation
- Head management
- Traversal
- Insertion
- Deletion
- Searching and length calculation
- Edge cases and validation
- Reverse traversal through pointer reversal
- Cycle detection
- Safe mutation patterns
- Complexity analysis through executable operations

The implementation deliberately avoids Python's built-in linked-list abstractions.
Each node stores a value and a reference to the next node.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Iterator, Optional


@dataclass
class Node:
    """One element of a singly linked list.

    `next` points only toward the following node. The final node points
    to None, which represents the end of the list.
    """

    data: Any
    next: Optional["Node"] = None


class SinglyLinkedList:
    """A singly linked list implemented entirely with explicit Node objects."""

    def __init__(self, values: Optional[Iterable[Any]] = None) -> None:
        self.head: Optional[Node] = None
        self._size = 0

        if values is not None:
            for value in values:
                self.insert_at_end(value)

    # ------------------------------------------------------------------
    # Basic observation
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return True when the head does not reference a node."""
        return self.head is None

    def __len__(self) -> int:
        """Return the maintained number of nodes."""
        return self._size

    def traverse(self) -> list[Any]:
        """Visit nodes from head to tail and return their stored values."""
        values: list[Any] = []
        current = self.head

        while current is not None:
            values.append(current.data)
            current = current.next

        return values

    def iter_nodes(self) -> Iterator[Node]:
        """Yield actual nodes instead of only their values.

        A cycle would make this iterator non-terminating, so normal list
        operations maintain an acyclic structure.
        """
        current = self.head

        while current is not None:
            yield current
            current = current.next

    def display(self) -> str:
        """Return a human-readable representation of the chain."""
        if self.head is None:
            return "HEAD -> None"

        parts: list[str] = ["HEAD"]
        current = self.head

        while current is not None:
            parts.append(str(current.data))
            current = current.next

        parts.append("None")
        return " -> ".join(parts)

    # ------------------------------------------------------------------
    # Searching and position handling
    # ------------------------------------------------------------------

    def search(self, value: Any) -> Optional[Node]:
        """Return the first node containing value, or None if absent."""
        current = self.head

        while current is not None:
            if current.data == value:
                return current
            current = current.next

        return None

    def contains(self, value: Any) -> bool:
        """Return whether at least one node stores value."""
        return self.search(value) is not None

    def get(self, index: int) -> Any:
        """Return the value at a zero-based index."""
        node = self._node_at(index)
        return node.data

    def _validate_index(self, index: int, allow_end: bool = False) -> None:
        """Validate an index before traversing the list."""
        upper_bound = self._size if allow_end else self._size - 1

        if index < 0 or index > upper_bound:
            raise IndexError(
                f"index {index} is outside the valid range "
                f"0..{upper_bound}"
            )

    def _node_at(self, index: int) -> Node:
        """Return the node at a valid zero-based index."""
        self._validate_index(index)

        current = self.head
        for _ in range(index):
            assert current is not None
            current = current.next

        assert current is not None
        return current

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------

    def insert_at_head(self, value: Any) -> Node:
        """Insert a new node before the current head.

        This is O(1) because no traversal is required.
        """
        new_node = Node(value, self.head)
        self.head = new_node
        self._size += 1
        return new_node

    def insert_at_end(self, value: Any) -> Node:
        """Insert a node after the current tail.

        Because this implementation deliberately stores only `head`,
        reaching the tail requires O(n) traversal.
        """
        new_node = Node(value)

        if self.head is None:
            self.head = new_node
            self._size += 1
            return new_node

        current = self.head

        while current.next is not None:
            current = current.next

        current.next = new_node
        self._size += 1
        return new_node

    def insert_at(self, index: int, value: Any) -> Node:
        """Insert value before the node currently at index.

        index == 0 inserts at the head.
        index == len(list) inserts after the current tail.
        """
        self._validate_index(index, allow_end=True)

        if index == 0:
            return self.insert_at_head(value)

        previous = self._node_at(index - 1)
        new_node = Node(value, previous.next)
        previous.next = new_node
        self._size += 1
        return new_node

    def insert_after_value(self, target: Any, value: Any) -> Node:
        """Insert value after the first node containing target."""
        target_node = self.search(target)

        if target_node is None:
            raise ValueError(f"target value {target!r} was not found")

        new_node = Node(value, target_node.next)
        target_node.next = new_node
        self._size += 1
        return new_node

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete_head(self) -> Any:
        """Remove and return the head value.

        The next node becomes the new head. This operation is O(1).
        """
        if self.head is None:
            raise IndexError("cannot delete the head of an empty list")

        removed = self.head
        self.head = removed.next

        # Disconnect the removed node so accidental references cannot
        # continue to expose the remainder of the list through it.
        removed.next = None

        self._size -= 1
        return removed.data

    def delete_at(self, index: int) -> Any:
        """Delete and return the node at a zero-based index."""
        self._validate_index(index)

        if index == 0:
            return self.delete_head()

        previous = self._node_at(index - 1)
        removed = previous.next

        assert removed is not None
        previous.next = removed.next
        removed.next = None

        self._size -= 1
        return removed.data

    def delete_first(self, value: Any) -> Any:
        """Delete the first occurrence of value and return it."""
        if self.head is None:
            raise ValueError("cannot delete from an empty list")

        if self.head.data == value:
            return self.delete_head()

        previous = self.head
        current = self.head.next

        while current is not None:
            if current.data == value:
                previous.next = current.next
                current.next = None
                self._size -= 1
                return current.data

            previous = current
            current = current.next

        raise ValueError(f"value {value!r} was not found")

    def delete_all(self, value: Any) -> int:
        """Delete every occurrence of value and return the number removed."""
        removed_count = 0

        while self.head is not None and self.head.data == value:
            self.delete_head()
            removed_count += 1

        if self.head is None:
            return removed_count

        previous = self.head
        current = self.head.next

        while current is not None:
            if current.data == value:
                previous.next = current.next
                current.next = None
                self._size -= 1
                removed_count += 1
                current = previous.next
            else:
                previous = current
                current = current.next

        return removed_count

    # ------------------------------------------------------------------
    # Structural operations
    # ------------------------------------------------------------------

    def reverse(self) -> None:
        """Reverse links in-place using three pointers.

        previous represents the already-reversed prefix.
        current represents the node being processed.
        next_node preserves the remaining suffix before the link changes.

        Time: O(n)
        Extra space: O(1)
        """
        previous: Optional[Node] = None
        current = self.head

        while current is not None:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node

        self.head = previous

    def detect_cycle(self) -> bool:
        """Detect a cycle with Floyd's tortoise-and-hare algorithm.

        A valid ordinary singly linked list terminates at None. If two
        pointers moving at different speeds eventually meet, a cycle exists.
        """
        slow = self.head
        fast = self.head

        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next

            if slow is fast:
                return True

        return False

    def clear(self) -> None:
        """Remove all nodes and reset the list."""
        current = self.head

        while current is not None:
            next_node = current.next
            current.next = None
            current = next_node

        self.head = None
        self._size = 0

    def map(self, transform: Callable[[Any], Any]) -> None:
        """Apply a transformation to each stored value in place."""
        if not callable(transform):
            raise TypeError("transform must be callable")

        current = self.head

        while current is not None:
            current.data = transform(current.data)
            current = current.next

    def validate_integrity(self) -> None:
        """Verify size consistency and reject cycles.

        This is useful during development because pointer mistakes can
        silently corrupt a linked structure.
        """
        if self.detect_cycle():
            raise RuntimeError("linked list integrity failure: cycle detected")

        counted = 0
        current = self.head

        while current is not None:
            counted += 1
            current = current.next

        if counted != self._size:
            raise RuntimeError(
                f"linked list integrity failure: stored size={self._size}, "
                f"counted nodes={counted}"
            )


def print_operation(title: str, linked_list: SinglyLinkedList) -> None:
    print(f"\n{title}")
    print(linked_list.display())
    print(f"size = {len(linked_list)}")


def demonstrate_node_and_head() -> None:
    print("=== Node and Head ===")

    first = Node("repository")
    second = Node("branch")
    third = Node("commit")

    first.next = second
    second.next = third

    head = first

    print("The head points to:", head.data)
    print("Following next pointers:")

    current = head
    while current is not None:
        print(f"  node={current.data!r}, next={current.next.data if current.next else None!r}")
        current = current.next


def demonstrate_traversal() -> None:
    print("\n=== Traversal ===")

    linked_list = SinglyLinkedList(["main", "feature/auth", "feature/search"])

    print("Traversal result:", linked_list.traverse())
    print("Display:", linked_list.display())

    print("Searching for feature/search:", linked_list.contains("feature/search"))
    print("Searching for release:", linked_list.contains("release"))


def demonstrate_insertions() -> None:
    print("\n=== Insertion ===")

    linked_list = SinglyLinkedList()

    linked_list.insert_at_head("review")
    linked_list.insert_at_head("changes")
    linked_list.insert_at_end("merge")
    print_operation("After head and tail insertion", linked_list)

    linked_list.insert_at(1, "approval")
    print_operation("After insertion at index 1", linked_list)

    linked_list.insert_after_value("approval", "status-check")
    print_operation("After insertion after approval", linked_list)

    linked_list.validate_integrity()


def demonstrate_deletions() -> None:
    print("\n=== Deletion ===")

    linked_list = SinglyLinkedList(
        ["pull-request", "code-review", "approval", "status-check", "merge"]
    )

    print_operation("Initial structure", linked_list)

    removed = linked_list.delete_head()
    print(f"Deleted head: {removed!r}")
    print_operation("After deleting head", linked_list)

    removed = linked_list.delete_at(1)
    print(f"Deleted index 1: {removed!r}")
    print_operation("After deleting index 1", linked_list)

    removed = linked_list.delete_first("merge")
    print(f"Deleted first matching value: {removed!r}")
    print_operation("After deleting first occurrence", linked_list)

    linked_list.insert_at_end("approval")
    linked_list.insert_at_end("approval")
    print_operation("Before deleting duplicate approvals", linked_list)

    count = linked_list.delete_all("approval")
    print(f"Deleted {count} occurrence(s) of approval")
    print_operation("After deleting all approvals", linked_list)

    linked_list.validate_integrity()


def demonstrate_reverse_and_cycle_detection() -> None:
    print("\n=== Reverse and Cycle Detection ===")

    linked_list = SinglyLinkedList(["A", "B", "C", "D"])

    print("Before reverse:", linked_list.display())
    linked_list.reverse()
    print("After reverse:", linked_list.display())

    print("Cycle present:", linked_list.detect_cycle())

    # Deliberately create a cycle to demonstrate detection.
    tail = linked_list._node_at(len(linked_list) - 1)
    tail.next = linked_list.head

    print("Cycle present after deliberate corruption:", linked_list.detect_cycle())

    # Restore the structure before any normal traversal.
    tail.next = None
    linked_list.validate_integrity()


def demonstrate_validation_and_failures() -> None:
    print("\n=== Validation and Failure Conditions ===")

    linked_list = SinglyLinkedList(["alpha", "beta", "gamma"])

    failure_cases = [
        ("invalid get", lambda: linked_list.get(10)),
        ("invalid insertion index", lambda: linked_list.insert_at(10, "delta")),
        ("invalid deletion index", lambda: linked_list.delete_at(-1)),
        ("missing deletion value", lambda: linked_list.delete_first("missing")),
        ("missing insertion target", lambda: linked_list.insert_after_value("missing", "x")),
    ]

    for name, operation in failure_cases:
        try:
            operation()
        except (IndexError, ValueError) as exc:
            print(f"{name}: correctly rejected -> {exc}")

    empty = SinglyLinkedList()

    try:
        empty.delete_head()
    except IndexError as exc:
        print(f"empty-list deletion: correctly rejected -> {exc}")


def demonstrate_processing() -> None:
    print("\n=== In-place Value Processing ===")

    commits = SinglyLinkedList(
        ["fix login", "Add Search", "update documentation"]
    )

    print("Original:", commits.display())

    commits.map(lambda message: message.lower())

    print("Normalized:", commits.display())


def demonstrate_realistic_workflow() -> None:
    print("\n=== Realistic Queue-like Workflow ===")

    pending_changes = SinglyLinkedList()

    # A singly linked list can model a lightweight ordered chain when
    # explicit node ownership and pointer behavior are more important
    # than random access.
    for change in [
        "validate pull request",
        "run tests",
        "request review",
        "check approval",
    ]:
        pending_changes.insert_at_end(change)

    print("Pending workflow:", pending_changes.display())

    while not pending_changes.is_empty():
        completed = pending_changes.delete_head()
        print("Completed:", completed)

    print("Remaining:", pending_changes.display())


def demonstrate_complexity() -> None:
    print("\n=== Operation Characteristics ===")

    complexity = {
        "insert_at_head": "O(1)",
        "delete_head": "O(1)",
        "traverse": "O(n)",
        "search": "O(n)",
        "get_by_index": "O(n)",
        "insert_at_arbitrary_index": "O(n)",
        "delete_at_arbitrary_index": "O(n)",
        "insert_at_end_without_tail": "O(n)",
        "reverse": "O(n)",
        "cycle_detection": "O(n) time, O(1) extra space",
    }

    for operation, cost in complexity.items():
        print(f"{operation:<32} {cost}")


def run_edge_case_suite() -> None:
    print("\n=== Edge Case Verification ===")

    cases = [
        [],
        [42],
        [42, 42, 42],
        ["x", None, False, 0],
    ]

    for values in cases:
        linked_list = SinglyLinkedList(values)
        linked_list.validate_integrity()

        if values:
            assert linked_list.traverse() == values
            assert linked_list.get(0) == values[0]
            assert linked_list.delete_at(0) == values[0]
            linked_list.validate_integrity()
        else:
            assert linked_list.is_empty()
            assert len(linked_list) == 0

        print(f"validated: {values!r}")


def main() -> None:
    demonstrate_node_and_head()
    demonstrate_traversal()
    demonstrate_insertions()
    demonstrate_deletions()
    demonstrate_reverse_and_cycle_detection()
    demonstrate_validation_and_failures()
    demonstrate_processing()
    demonstrate_realistic_workflow()
    demonstrate_complexity()
    run_edge_case_suite()

    print("\n=== Final Integrity Check ===")

    final_list = SinglyLinkedList(["node-a", "node-b", "node-c"])
    final_list.delete_at(1)
    final_list.insert_at_head("node-head")
    final_list.insert_at_end("node-tail")
    final_list.reverse()
    final_list.validate_integrity()

    print(final_list.display())
    print("All demonstrations completed successfully.")


if __name__ == "__main__":
    main()
