from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable, Iterator


@dataclass
class Node:
    value: int
    next: Optional["Node"] = None


def build_list(values: Iterable[int]) -> Optional[Node]:
    head = tail = None
    for value in values:
        node = Node(value)
        if head is None:
            head = node
        else:
            tail.next = node
        tail = node
    return head


def to_list(head: Optional[Node], limit: int = 100) -> list[int]:
    result = []
    current = head
    seen = set()

    while current is not None and len(result) < limit:
        identity = id(current)
        if identity in seen:
            result.append(current.value)
            break
        seen.add(identity)
        result.append(current.value)
        current = current.next

    return result


def print_list(title: str, head: Optional[Node], limit: int = 100) -> None:
    values = to_list(head, limit)
    suffix = " -> ..." if len(values) == limit else ""
    print(f"{title}: " + " -> ".join(map(str, values)) + suffix)


def merge_two_sorted_lists(
    first: Optional[Node], second: Optional[Node]
) -> Optional[Node]:
    """Merge two ascending lists by reusing their existing nodes."""
    dummy = Node(0)
    tail = dummy

    while first is not None and second is not None:
        if first.value <= second.value:
            tail.next = first
            first = first.next
        else:
            tail.next = second
            second = second.next
        tail = tail.next

    tail.next = first if first is not None else second
    return dummy.next


def merge_two_sorted_lists_recursive(
    first: Optional[Node], second: Optional[Node]
) -> Optional[Node]:
    """Recursive version; useful for understanding pointer decisions."""
    if first is None:
        return second
    if second is None:
        return first

    if first.value <= second.value:
        first.next = merge_two_sorted_lists_recursive(first.next, second)
        return first

    second.next = merge_two_sorted_lists_recursive(first, second.next)
    return second


def remove_duplicates_sorted(head: Optional[Node]) -> Optional[Node]:
    """Remove duplicate values from an already sorted linked list."""
    current = head

    while current is not None and current.next is not None:
        if current.value == current.next.value:
            current.next = current.next.next
        else:
            current = current.next

    return head


def remove_duplicates_unsorted(head: Optional[Node]) -> Optional[Node]:
    """Remove repeated values from an arbitrary-order list in O(n) time."""
    if head is None:
        return None

    seen = {head.value}
    current = head

    while current.next is not None:
        if current.next.value in seen:
            current.next = current.next.next
        else:
            seen.add(current.next.value)
            current = current.next

    return head


def remove_nth_from_end(head: Optional[Node], n: int) -> Optional[Node]:
    """Remove the nth node from the end using two pointers."""
    if n <= 0:
        raise ValueError("n must be positive")

    dummy = Node(0, head)
    fast = dummy

    for _ in range(n):
        fast = fast.next
        if fast is None:
            raise ValueError("n is larger than the list length")

    slow = dummy

    while fast.next is not None:
        fast = fast.next
        slow = slow.next

    slow.next = slow.next.next
    return dummy.next


def intersection_node(
    first: Optional[Node], second: Optional[Node]
) -> Optional[Node]:
    """
    Find the first shared node by identity, not by equal value.

    Switching heads after reaching the end compensates for different
    prefix lengths, giving both pointers the same total traversal length.
    """
    a, b = first, second

    while a is not b:
        a = a.next if a is not None else second
        b = b.next if b is not None else first

    return a


def has_cycle(head: Optional[Node]) -> bool:
    slow = fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True

    return False


def cycle_entry(head: Optional[Node]) -> Optional[Node]:
    """Return the node where Floyd's algorithm finds the cycle entry."""
    slow = fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow

    return None


def cycle_length(head: Optional[Node]) -> int:
    entry = cycle_entry(head)
    if entry is None:
        return 0

    length = 1
    current = entry.next
    while current is not entry:
        length += 1
        current = current.next
    return length


def josephus_circular(n: int, step: int) -> int:
    """
    Solve a circular elimination problem without constructing a linked list.

    The recurrence moves the survivor from a smaller circle into the
    coordinate system of the original circle.
    """
    if n <= 0 or step <= 0:
        raise ValueError("n and step must be positive")

    survivor = 0
    for size in range(2, n + 1):
        survivor = (survivor + step) % size
    return survivor


def circular_move(head: Optional[Node], steps: int) -> Optional[Node]:
    """Move around a circular list, validating that it is actually circular."""
    if head is None:
        return None

    entry = cycle_entry(head)
    if entry is None:
        raise ValueError("circular_move requires a circular linked list")

    length = cycle_length(head)
    steps %= length
    current = head

    for _ in range(steps):
        current = current.next

    return current


def reverse_list(head: Optional[Node]) -> Optional[Node]:
    previous = None
    current = head

    while current is not None:
        following = current.next
        current.next = previous
        previous = current
        current = following

    return previous


def is_palindrome(head: Optional[Node]) -> bool:
    """
    O(n) time and O(1) auxiliary space palindrome detection.

    The second half is reversed temporarily and restored before returning,
    which preserves the caller's linked-list structure.
    """
    if head is None or head.next is None:
        return True

    slow = fast = head
    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next

    second_half = reverse_list(slow.next)
    slow.next = second_half

    left = head
    right = second_half
    palindrome = True

    while right is not None:
        if left.value != right.value:
            palindrome = False
            break
        left = left.next
        right = right.next

    slow.next = reverse_list(second_half)
    return palindrome


def recursive_palindrome(head: Optional[Node]) -> bool:
    """A compact recursive approach; uses O(n) call-stack space."""
    left = head

    def compare(right: Optional[Node]) -> bool:
        nonlocal left
        if right is None:
            return True

        if not compare(right.next):
            return False

        if left.value != right.value:
            return False

        left = left.next
        return True

    return compare(head)


def demonstrate_intersection() -> None:
    shared = build_list([30, 40, 50])

    first = build_list([10, 20])
    first_tail = first
    while first_tail.next:
        first_tail = first_tail.next
    first_tail.next = shared

    second = build_list([5, 15, 25])
    second_tail = second
    while second_tail.next:
        second_tail = second_tail.next
    second_tail.next = shared

    result = intersection_node(first, second)
    print(f"Intersection node: {result.value if result else None}")
    print("Intersection uses node identity: the shared node is physically the same object.")


def demonstrate_cycle() -> None:
    head = build_list([1, 2, 3, 4, 5])
    tail = head
    while tail.next:
        tail = tail.next

    entry = head.next.next
    tail.next = entry

    detected = has_cycle(head)
    cycle_start = cycle_entry(head)

    print(f"Cycle detected: {detected}")
    print(f"Cycle entry: {cycle_start.value if cycle_start else None}")
    print(f"Cycle length: {cycle_length(head)}")


def run_edge_cases() -> None:
    print("\nEdge cases")

    print_list("Merge empty + values", merge_two_sorted_lists(None, build_list([1, 4])))
    print_list(
        "Remove duplicates",
        remove_duplicates_sorted(build_list([1, 1, 2, 2, 2, 3])),
    )

    single = build_list([99])
    print_list("Remove only node", remove_nth_from_end(single, 1))

    print(f"Empty palindrome: {is_palindrome(None)}")
    print(f"Single-node palindrome: {is_palindrome(build_list([7]))}")

    try:
        remove_nth_from_end(build_list([1, 2]), 3)
    except ValueError as exc:
        print(f"Invalid nth-node request rejected: {exc}")


def main() -> None:
    print("ADVANCED LINKED-LIST PROBLEMS")

    first = build_list([1, 3, 5, 7])
    second = build_list([2, 3, 6, 8])
    merged = merge_two_sorted_lists(first, second)
    print_list("Merged sorted lists", merged)

    duplicate_values = build_list([1, 1, 2, 3, 3, 3, 4])
    remove_duplicates_sorted(duplicate_values)
    print_list("Sorted-list duplicates removed", duplicate_values)

    arbitrary = build_list([4, 2, 4, 1, 2, 4, 3])
    remove_duplicates_unsorted(arbitrary)
    print_list("Unsorted-list duplicates removed", arbitrary)

    nth_example = build_list([10, 20, 30, 40, 50])
    nth_example = remove_nth_from_end(nth_example, 2)
    print_list("After removing second node from end", nth_example)

    demonstrate_intersection()
    demonstrate_cycle()

    print(f"Josephus survivor for n=7, step=3: {josephus_circular(7, 3)}")

    palindrome = build_list([1, 2, 3, 2, 1])
    print(f"Palindrome [1,2,3,2,1]: {is_palindrome(palindrome)}")
    print_list("Palindrome after restoration", palindrome)

    non_palindrome = build_list([1, 2, 3, 4])
    print(f"Palindrome [1,2,3,4]: {is_palindrome(non_palindrome)}")

    print(
        "Recursive palindrome [4,5,5,4]:",
        recursive_palindrome(build_list([4, 5, 5, 4])),
    )

    run_edge_cases()

    print("\nComplexity")
    print("Merge sorted lists: O(n + m) time, O(1) auxiliary space.")
    print("Sorted duplicate removal: O(n) time, O(1) auxiliary space.")
    print("Unsorted duplicate removal: O(n) expected time, O(n) space.")
    print("Nth from end: O(n) time, O(1) auxiliary space.")
    print("Intersection detection: O(n + m) time, O(1) auxiliary space.")
    print("Cycle detection and entry: O(n) time, O(1) auxiliary space.")
    print("Palindrome with restoration: O(n) time, O(1) auxiliary space.")


if __name__ == "__main__":
    main()
