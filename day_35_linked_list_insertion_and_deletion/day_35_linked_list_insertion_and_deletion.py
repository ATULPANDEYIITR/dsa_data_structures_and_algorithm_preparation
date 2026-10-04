"""Linked-list insertion and deletion: executable learning and practice suite.

The implementation uses a singly linked list and demonstrates:
- insertion at beginning
- insertion at end
- insertion at a position
- deletion of first node
- deletion of last node
- deletion by value
- deletion by position

Positions are zero-based: position 0 is the first node.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional


@dataclass
class Node:
    """A single singly-linked-list node.

    `next` stores the reference to the following node.  The final node
    stores None because it has no successor.
    """

    value: int
    next: Optional["Node"] = None


class LinkedList:
    """Singly linked list with insertion and deletion operations."""

    def __init__(self, values: Optional[Iterable[int]] = None) -> None:
        self.head: Optional[Node] = None
        self._size = 0

        if values is not None:
            for value in values:
                self.insert_end(value)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[int]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __str__(self) -> str:
        return " -> ".join(map(str, self)) if self.head else "EMPTY"

    def to_list(self) -> list[int]:
        return list(self)

    def _validate_position_for_insert(self, position: int) -> None:
        """Allow positions from 0 through size for insertion."""
        if not isinstance(position, int):
            raise TypeError("position must be an integer")
        if position < 0 or position > self._size:
            raise IndexError(
                f"insertion position {position} is outside 0..{self._size}"
            )

    def _validate_position_for_delete(self, position: int) -> None:
        """Allow only positions occupied by existing nodes."""
        if not isinstance(position, int):
            raise TypeError("position must be an integer")
        if position < 0 or position >= self._size:
            raise IndexError(
                f"deletion position {position} is outside 0..{self._size - 1}"
            )

    def insert_beginning(self, value: int) -> None:
        """Insert a node before the current head.

        The new node points to the old head, then head is redirected to
        the new node.  This does not require traversal.
        """
        new_node = Node(value=value, next=self.head)
        self.head = new_node
        self._size += 1

    def insert_end(self, value: int) -> None:
        """Insert a node after the current last node."""
        new_node = Node(value)

        if self.head is None:
            self.head = new_node
            self._size += 1
            return

        current = self.head
        while current.next is not None:
            current = current.next

        current.next = new_node
        self._size += 1

    def insert_position(self, position: int, value: int) -> None:
        """Insert value at a zero-based position.

        Position size is valid because it means inserting immediately
        after the current last node.
        """
        self._validate_position_for_insert(position)

        if position == 0:
            self.insert_beginning(value)
            return

        if position == self._size:
            self.insert_end(value)
            return

        previous = self.head
        for _ in range(position - 1):
            assert previous is not None
            previous = previous.next

        assert previous is not None
        new_node = Node(value, previous.next)
        previous.next = new_node
        self._size += 1

    def delete_first(self) -> int:
        """Remove and return the first value."""
        if self.head is None:
            raise IndexError("cannot delete from an empty linked list")

        removed = self.head
        self.head = removed.next
        removed.next = None
        self._size -= 1
        return removed.value

    def delete_last(self) -> int:
        """Remove and return the final value.

        A singly linked list must locate the node immediately before the
        tail because nodes do not contain backward references.
        """
        if self.head is None:
            raise IndexError("cannot delete from an empty linked list")

        if self.head.next is None:
            return self.delete_first()

        previous = self.head
        while previous.next is not None and previous.next.next is not None:
            previous = previous.next

        assert previous.next is not None
        removed = previous.next
        previous.next = None
        self._size -= 1
        return removed.value

    def delete_by_value(self, value: int) -> bool:
        """Delete the first node whose value equals value.

        Returns True when a node was removed and False when the value
        does not occur.  Duplicate values are allowed, so only the first
        matching node is removed.
        """
        if self.head is None:
            return False

        if self.head.value == value:
            self.delete_first()
            return True

        previous = self.head
        while previous.next is not None:
            if previous.next.value == value:
                removed = previous.next
                previous.next = removed.next
                removed.next = None
                self._size -= 1
                return True
            previous = previous.next

        return False

    def delete_by_position(self, position: int) -> int:
        """Delete and return the value at a zero-based position."""
        self._validate_position_for_delete(position)

        if position == 0:
            return self.delete_first()

        previous = self.head
        for _ in range(position - 1):
            assert previous is not None
            previous = previous.next

        assert previous is not None
        assert previous.next is not None

        removed = previous.next
        previous.next = removed.next
        removed.next = None
        self._size -= 1
        return removed.value

    def find(self, value: int) -> Optional[int]:
        """Return the first zero-based position containing value."""
        current = self.head
        position = 0

        while current is not None:
            if current.value == value:
                return position
            current = current.next
            position += 1

        return None

    def reverse(self) -> None:
        """Reverse links in place.

        This is included because understanding pointer direction makes
        insertion and deletion link changes easier to reason about.
        """
        previous = None
        current = self.head

        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following

        self.head = previous

    def check_integrity(self) -> None:
        """Detect size mismatches and accidental cycles.

        Floyd's slow/fast pointer algorithm detects a cycle without
        allocating a second collection.
        """
        slow = self.head
        fast = self.head

        while fast is not None and fast.next is not None:
            slow = slow.next if slow is not None else None
            fast = fast.next.next

            if slow is fast:
                raise RuntimeError("linked-list integrity failure: cycle detected")

        counted = 0
        current = self.head
        while current is not None:
            counted += 1
            current = current.next

        if counted != self._size:
            raise RuntimeError(
                f"linked-list integrity failure: expected {self._size}, "
                f"counted {counted}"
            )


def show(operation: str, linked_list: LinkedList) -> None:
    linked_list.check_integrity()
    print(f"{operation:<32} {linked_list}   size={len(linked_list)}")


def basic_operations_demo() -> None:
    print("\n=== Basic insertion and deletion ===")

    linked_list = LinkedList()
    show("empty list", linked_list)

    linked_list.insert_beginning(20)
    show("insert_beginning(20)", linked_list)

    linked_list.insert_beginning(10)
    show("insert_beginning(10)", linked_list)

    linked_list.insert_end(40)
    show("insert_end(40)", linked_list)

    linked_list.insert_position(2, 30)
    show("insert_position(2, 30)", linked_list)

    linked_list.delete_first()
    show("delete_first()", linked_list)

    linked_list.delete_last()
    show("delete_last()", linked_list)

    linked_list.delete_by_value(30)
    show("delete_by_value(30)", linked_list)

    linked_list.insert_end(50)
    linked_list.insert_end(60)
    linked_list.delete_by_position(1)
    show("delete_by_position(1)", linked_list)


def position_demo() -> None:
    print("\n=== Position semantics ===")

    linked_list = LinkedList([10, 20, 30])

    print("Initial:", linked_list)
    linked_list.insert_position(0, 5)
    print("Insert at position 0:", linked_list)

    linked_list.insert_position(len(linked_list), 40)
    print("Insert at position size:", linked_list)

    removed = linked_list.delete_by_position(2)
    print(f"Delete position 2 -> {removed}:", linked_list)

    print("Positions are zero-based:", linked_list.to_list())


def duplicate_value_demo() -> None:
    print("\n=== Delete by value with duplicates ===")

    linked_list = LinkedList([7, 4, 7, 9, 7])
    print("Before:", linked_list)

    removed = linked_list.delete_by_value(7)
    print("Removed first matching 7:", removed)
    print("After:", linked_list)

    while linked_list.delete_by_value(7):
        print("Removed another 7:", linked_list)

    print("No 7 remains:", linked_list)


def error_handling_demo() -> None:
    print("\n=== Edge cases and validation ===")

    empty = LinkedList()

    for operation in (
        lambda: empty.delete_first(),
        lambda: empty.delete_last(),
        lambda: empty.delete_by_position(0),
    ):
        try:
            operation()
        except (IndexError, TypeError) as exc:
            print("Expected error:", exc)

    for invalid_position in (-1, 2):
        try:
            LinkedList([10]).insert_position(invalid_position, 99)
        except (IndexError, TypeError) as exc:
            print("Invalid insertion:", exc)

    try:
        LinkedList([10]).delete_by_position(1)
    except (IndexError, TypeError) as exc:
        print("Invalid deletion:", exc)

    result = LinkedList([1, 2, 3]).delete_by_value(99)
    print("Deleting missing value returns:", result)


def reverse_and_integrity_demo() -> None:
    print("\n=== Link reversal and integrity checking ===")

    linked_list = LinkedList([1, 2, 3, 4])
    print("Before reverse:", linked_list)

    linked_list.reverse()
    linked_list.check_integrity()

    print("After reverse:", linked_list)
    print("Find value 2 at position:", linked_list.find(2))


def complexity_reference() -> None:
    print("\n=== Operation complexity ===")
    print("Insert at beginning : O(1) time, O(1) extra space")
    print("Insert at end       : O(n) time for this head-only design")
    print("Insert at position  : O(n) time in the worst case")
    print("Delete first        : O(1) time")
    print("Delete last         : O(n) time for a singly linked list")
    print("Delete by value     : O(n) time")
    print("Delete by position  : O(n) time")
    print("Finding a value     : O(n) time")
    print("Reversing links     : O(n) time, O(1) extra space")


def practice_scenario() -> None:
    print("\n=== Repository-style queue scenario ===")
    print("A linked list can represent an ordered stream of pending change IDs.")

    pending = LinkedList(["PR-101", "PR-102", "PR-103"])  # type: ignore[arg-type]
    print("Pending:", pending)

    pending.insert_beginning("PR-100")
    print("Urgent item inserted at beginning:", pending)

    pending.insert_end("PR-104")
    print("Normal item appended:", pending)

    pending.insert_position(2, "PR-101A")
    print("Item inserted at position 2:", pending)

    pending.delete_first()
    print("First item processed:", pending)

    pending.delete_by_value("PR-101A")
    print("Specific item removed:", pending)

    pending.delete_by_position(len(pending) - 1)
    print("Last item cancelled:", pending)


def main() -> None:
    basic_operations_demo()
    position_demo()
    duplicate_value_demo()
    error_handling_demo()
    reverse_and_integrity_demo()
    complexity_reference()

    # The Node type is generic at the structural level, so the final
    # demonstration uses strings even though the earlier type annotation
    # examples use integers.
    practice_scenario()


if __name__ == "__main__":
    main()
