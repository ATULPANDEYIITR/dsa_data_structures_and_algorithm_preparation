from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class ListNode:
    value: int
    next: Optional["ListNode"] = None


def build_linked_list(values: Iterable[int]) -> Optional[ListNode]:
    """Create a singly linked list from an iterable of values."""
    iterator = iter(values)

    try:
        first_value = next(iterator)
    except StopIteration:
        return None

    head = ListNode(first_value)
    tail = head

    for value in iterator:
        tail.next = ListNode(value)
        tail = tail.next

    return head


def linked_list_to_string(head: Optional[ListNode], limit: int = 20) -> str:
    """
    Convert a list to readable text.

    A limit prevents accidental infinite traversal when the list contains
    a cycle, which is important when demonstrating cycle detection.
    """
    values = []
    current = head

    for _ in range(limit):
        if current is None:
            return " -> ".join(map(str, values)) if values else "empty"

        values.append(str(current.value))
        current = current.next

    values.append("...")
    return " -> ".join(values)


def find_middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Return the middle node using the slow/fast pointer technique.

    slow moves one node per iteration.
    fast moves two nodes per iteration.

    For an even-sized list this implementation returns the second middle
    node. For example, [10, 20, 30, 40] returns 30.
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    return slow


def find_first_middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Return the first of the two middle nodes for an even-sized list.

    The loop intentionally stops one step earlier than the usual
    second-middle implementation.
    """
    if head is None:
        return None

    slow = head
    fast = head

    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next

    return slow


def has_cycle(head: Optional[ListNode]) -> bool:
    """
    Floyd's cycle detection algorithm.

    If a cycle exists, the fast pointer eventually catches the slow pointer.
    If no cycle exists, fast reaches None.
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            return True

    return False


def find_cycle_entry(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Find the first node belonging to the cycle.

    Phase one detects whether slow and fast meet.
    Phase two resets one pointer to the head and moves both one step at a
    time. Their next meeting point is the cycle entry.

    This is the second phase of Floyd's algorithm and uses O(1) extra space.
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            break
    else:
        return None

    slow = head

    while slow is not fast:
        slow = slow.next
        fast = fast.next

    return slow


def cycle_length(head: Optional[ListNode]) -> int:
    """Return the number of nodes in the cycle, or zero if no cycle exists."""
    meeting = find_cycle_entry(head)

    if meeting is None:
        return 0

    length = 1
    current = meeting.next

    while current is not meeting:
        current = current.next
        length += 1

    return length


def distance_to_cycle_entry(head: Optional[ListNode]) -> Optional[int]:
    """
    Return the number of edges from head to the cycle entry.

    A list without a cycle returns None.
    """
    entry = find_cycle_entry(head)

    if entry is None:
        return None

    distance = 0
    current = head

    while current is not entry:
        current = current.next
        distance += 1

    return distance


def demonstrate_basic_pointer_movement() -> None:
    print("\n=== Basic Two-Pointer Movement ===")

    head = build_linked_list([10, 20, 30, 40, 50, 60, 70])
    slow = head
    fast = head

    step = 0

    while fast is not None and fast.next is not None:
        step += 1
        slow = slow.next
        fast = fast.next.next

        print(
            f"step={step}: "
            f"slow={slow.value}, "
            f"fast={fast.value if fast else None}"
        )

    print(f"Final slow pointer: {slow.value}")
    print("The slow pointer has reached the middle while fast has reached the end.")


def demonstrate_middle_detection() -> None:
    print("\n=== Middle-Node Detection ===")

    examples = [
        [],
        [10],
        [10, 20],
        [10, 20, 30],
        [10, 20, 30, 40],
        [10, 20, 30, 40, 50],
        [10, 20, 30, 40, 50, 60],
    ]

    for values in examples:
        head = build_linked_list(values)
        second_middle = find_middle_node(head)
        first_middle = find_first_middle_node(head)

        print(
            f"{values!r:35} "
            f"first-middle={first_middle.value if first_middle else None!s:>5} "
            f"second-middle={second_middle.value if second_middle else None!s:>5}"
        )


def demonstrate_cycle_detection() -> None:
    print("\n=== Floyd Cycle Detection ===")

    acyclic = build_linked_list([1, 2, 3, 4, 5])
    print(f"Acyclic list has cycle: {has_cycle(acyclic)}")

    cyclic = build_linked_list([10, 20, 30, 40, 50])

    # Save references so the cycle can be created without searching by value.
    assert cyclic is not None
    second = cyclic.next
    third = second.next
    fourth = third.next
    fifth = fourth.next

    # 50 -> 30 creates a cycle containing 30, 40 and 50.
    fifth.next = third

    print("Cyclic structure preview:", linked_list_to_string(cyclic, limit=10))
    print(f"Cyclic list has cycle: {has_cycle(cyclic)}")

    entry = find_cycle_entry(cyclic)

    print(f"Cycle entry value: {entry.value if entry else None}")
    print(f"Cycle length: {cycle_length(cyclic)}")
    print(f"Distance from head to cycle entry: {distance_to_cycle_entry(cyclic)}")


def demonstrate_floyd_phases() -> None:
    print("\n=== Floyd Algorithm: Detection and Entry Location ===")

    head = build_linked_list([7, 11, 13, 17, 19, 23, 29])

    assert head is not None
    entry = head.next.next
    tail = head

    while tail.next is not None:
        tail = tail.next

    tail.next = entry

    slow = head
    fast = head
    iteration = 0
    meeting = None

    while fast is not None and fast.next is not None:
        iteration += 1
        slow = slow.next
        fast = fast.next.next

        print(
            f"iteration {iteration}: "
            f"slow={slow.value}, fast={fast.value}"
        )

        if slow is fast:
            meeting = slow
            break

    if meeting is None:
        print("No cycle was detected.")
        return

    print(f"Pointers met at node value {meeting.value}.")

    slow = head
    phase_two = 0

    while slow is not fast:
        phase_two += 1
        slow = slow.next
        fast = fast.next

        print(
            f"entry-search {phase_two}: "
            f"left={slow.value}, right={fast.value}"
        )

    print(f"Cycle entry found at value {slow.value}.")


def demonstrate_value_duplicates() -> None:
    print("\n=== Identity Versus Value ===")

    first = ListNode(42)
    second = ListNode(42)
    first.next = second

    # Equal values do not mean the nodes are the same object.
    print(f"first.value == second.value: {first.value == second.value}")
    print(f"first is second: {first is second}")

    # Floyd's algorithm must compare node identity, not only values.
    print(
        "Cycle detection result:",
        has_cycle(first),
    )

    second.next = first

    print(
        "Cycle detection after linking second back to first:",
        has_cycle(first),
    )


def demonstrate_cycle_without_extra_memory() -> None:
    print("\n=== Constant-Space Cycle Detection ===")

    head = build_linked_list(range(1, 11))
    assert head is not None

    cycle_entry = head
    for _ in range(4):
        cycle_entry = cycle_entry.next

    tail = head
    while tail.next is not None:
        tail = tail.next

    tail.next = cycle_entry

    print(f"Cycle entry: {find_cycle_entry(head).value}")
    print(f"Cycle length: {cycle_length(head)}")
    print(
        "Extra pointer storage remains constant regardless of list size: "
        "O(1)"
    )


def demonstrate_common_failure_conditions() -> None:
    print("\n=== Edge Cases and Failure Conditions ===")

    cases = {
        "empty": None,
        "single node": build_linked_list([99]),
        "two nodes": build_linked_list([1, 2]),
    }

    for name, head in cases.items():
        middle = find_middle_node(head)
        print(
            f"{name}: "
            f"middle={middle.value if middle else None}, "
            f"cycle={has_cycle(head)}"
        )

    self_cycle = ListNode(123)
    self_cycle.next = self_cycle

    print(
        f"self-cycle: has_cycle={has_cycle(self_cycle)}, "
        f"entry={find_cycle_entry(self_cycle).value}, "
        f"length={cycle_length(self_cycle)}"
    )


def demonstrate_application_split_list() -> None:
    print("\n=== Application: Splitting a Linked List at Its Middle ===")

    values = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    head = build_linked_list(values)

    if head is None:
        return

    slow = head
    fast = head

    # prev tracks the node before slow so the original list can be split.
    prev = None

    while fast is not None and fast.next is not None:
        prev = slow
        slow = slow.next
        fast = fast.next.next

    if prev is not None:
        prev.next = None

    print("Original values:", values)
    print("First half:", linked_list_to_string(head))
    print("Second half:", linked_list_to_string(slow))


def demonstrate_palindrome_check() -> None:
    print("\n=== Application: Palindrome Detection ===")

    def reverse_list(node: Optional[ListNode]) -> Optional[ListNode]:
        previous = None
        current = node

        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following

        return previous

    def is_palindrome(head: Optional[ListNode]) -> bool:
        if head is None or head.next is None:
            return True

        slow = head
        fast = head

        while fast.next is not None and fast.next.next is not None:
            slow = slow.next
            fast = fast.next.next

        second_half = reverse_list(slow.next)
        slow.next = second_half

        left = head
        right = second_half
        result = True

        while right is not None:
            if left.value != right.value:
                result = False
                break

            left = left.next
            right = right.next

        # Restore the list so this utility does not unexpectedly mutate
        # caller-owned data.
        slow.next = reverse_list(second_half)

        return result

    for values in ([1, 2, 3, 2, 1], [1, 2, 2, 1], [1, 2, 3], [1], []):
        head = build_linked_list(values)
        print(f"{values!r:25} palindrome={is_palindrome(head)}")


def demonstrate_algorithmic_properties() -> None:
    print("\n=== Algorithmic Properties ===")

    print(
        "Middle detection: O(n) time, O(1) auxiliary space."
    )
    print(
        "Cycle detection: O(n) time, O(1) auxiliary space."
    )
    print(
        "Cycle entry detection: O(n) time, O(1) auxiliary space."
    )
    print(
        "The fast pointer does not make the algorithm O(n/2); "
        "asymptotically, the running time remains O(n)."
    )
    print(
        "A hash-set cycle detector also takes O(n) time, but needs O(n) "
        "additional memory. Floyd trades extra memory for pointer movement."
    )


def run_self_checks() -> None:
    print("\n=== Self Checks ===")

    assert find_middle_node(build_linked_list([])) is None
    assert find_middle_node(build_linked_list([1])).value == 1
    assert find_middle_node(build_linked_list([1, 2])).value == 2
    assert find_middle_node(build_linked_list([1, 2, 3])).value == 2
    assert find_middle_node(build_linked_list([1, 2, 3, 4])).value == 3

    assert not has_cycle(build_linked_list([1, 2, 3]))

    self_cycle = ListNode(5)
    self_cycle.next = self_cycle

    assert has_cycle(self_cycle)
    assert find_cycle_entry(self_cycle) is self_cycle
    assert cycle_length(self_cycle) == 1

    cyclic = build_linked_list([1, 2, 3, 4, 5])
    assert cyclic is not None

    node3 = cyclic.next.next
    tail = node3

    while tail.next is not None:
        tail = tail.next

    tail.next = node3

    assert has_cycle(cyclic)
    assert find_cycle_entry(cyclic) is node3
    assert cycle_length(cyclic) == 3
    assert distance_to_cycle_entry(cyclic) == 2

    print("All assertions passed.")


def main() -> None:
    print("FAST AND SLOW POINTERS")
    print("======================")
    print("The demonstrations use singly linked lists and Floyd's algorithm.")

    demonstrate_basic_pointer_movement()
    demonstrate_middle_detection()
    demonstrate_cycle_detection()
    demonstrate_floyd_phases()
    demonstrate_value_duplicates()
    demonstrate_cycle_without_extra_memory()
    demonstrate_common_failure_conditions()
    demonstrate_application_split_list()
    demonstrate_palindrome_check()
    demonstrate_algorithmic_properties()
    run_self_checks()


if __name__ == "__main__":
    main()
