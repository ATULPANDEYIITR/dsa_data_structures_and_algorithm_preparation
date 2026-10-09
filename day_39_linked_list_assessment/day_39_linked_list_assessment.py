"""
Linked-List Assessment
======================

Eight executable linked-list assessment problems:
Easy:
    Reverse a linked list
    Detect a cycle
    Merge two sorted linked lists

Medium:
    Remove the Nth node from the end
    Find the intersection of two linked lists
    Check whether a linked list is a palindrome
    Reorder a linked list

Difficult:
    Merge K sorted linked lists

The implementations use singly linked lists and standard-library Python.
Run this file directly to execute all assessment tests.
"""

from __future__ import annotations

import heapq
import itertools
import unittest
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(eq=False)
class ListNode:
    """A node uses identity equality so shared tails can be detected correctly."""

    value: int
    next: Optional["ListNode"] = None


def build_list(values: Iterable[int]) -> Optional[ListNode]:
    """Construct a linked list while preserving the input order."""
    dummy = ListNode(0)
    tail = dummy

    for value in values:
        tail.next = ListNode(value)
        tail = tail.next

    return dummy.next


def to_list(head: Optional[ListNode], limit: int = 100_000) -> list[int]:
    """Convert an acyclic list to an array and reject accidental cycles."""
    result = []
    seen = set()
    current = head

    while current is not None:
        if id(current) in seen:
            raise ValueError("Cannot convert a cyclic linked list.")
        if len(result) >= limit:
            raise ValueError("Linked-list traversal exceeded the safety limit.")

        seen.add(id(current))
        result.append(current.value)
        current = current.next

    return result


def has_cycle(head: Optional[ListNode]) -> bool:
    """Easy: Floyd's tortoise-and-hare cycle detection."""
    slow = fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            return True

    return False


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """Easy: reverse links in place using constant auxiliary space."""
    if has_cycle(head):
        raise ValueError("Cannot reverse a cyclic linked list.")

    previous = None
    current = head

    while current is not None:
        following = current.next
        current.next = previous
        previous = current
        current = following

    return previous


def merge_two_sorted(
    first: Optional[ListNode],
    second: Optional[ListNode],
) -> Optional[ListNode]:
    """Easy: merge sorted lists by relinking existing nodes."""
    if has_cycle(first) or has_cycle(second):
        raise ValueError("Input lists must be acyclic.")

    # A shared tail would otherwise cause repeated nodes or a cycle.
    first_nodes = set()
    current = first
    while current is not None:
        first_nodes.add(id(current))
        current = current.next

    current = second
    while current is not None:
        if id(current) in first_nodes:
            raise ValueError("Input lists must not share nodes.")
        current = current.next

    dummy = ListNode(0)
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


def remove_nth_from_end(
    head: Optional[ListNode], n: int
) -> Optional[ListNode]:
    """Medium: remove the Nth node from the end in one traversal."""
    if n <= 0:
        raise ValueError("n must be positive.")
    if has_cycle(head):
        raise ValueError("Input list must be acyclic.")

    dummy = ListNode(0, head)
    fast = slow = dummy

    for _ in range(n):
        fast = fast.next
        if fast is None:
            raise ValueError("n exceeds the linked-list length.")

    while fast.next is not None:
        fast = fast.next
        slow = slow.next

    removed = slow.next
    slow.next = removed.next
    removed.next = None
    return dummy.next


def get_intersection_node(
    first: Optional[ListNode], second: Optional[ListNode]
) -> Optional[ListNode]:
    """Medium: find the first shared node by identity, not by value."""
    if has_cycle(first) or has_cycle(second):
        raise ValueError("Input lists must be acyclic.")

    left, right = first, second

    while left is not right:
        left = second if left is None else left.next
        right = first if right is None else right.next

    return left


def is_palindrome(head: Optional[ListNode]) -> bool:
    """Medium: compare halves using O(1) auxiliary space.

    The original links are restored before returning, including on mismatch.
    """
    if has_cycle(head):
        raise ValueError("Input list must be acyclic.")

    if head is None or head.next is None:
        return True

    slow = fast = head
    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next

    reversed_second = reverse_list(slow.next)
    slow.next = reversed_second

    left = head
    right = reversed_second
    matches = True

    try:
        while right is not None:
            if left.value != right.value:
                matches = False
                break
            left = left.next
            right = right.next
    finally:
        slow.next = reverse_list(reversed_second)

    return matches


def reorder_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """Medium: transform L0,L1,...,Ln into L0,Ln,L1,Ln-1,... in place."""
    if has_cycle(head):
        raise ValueError("Input list must be acyclic.")

    if head is None or head.next is None:
        return head

    slow = fast = head
    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next

    second = slow.next
    slow.next = None
    second = reverse_list(second)

    first = head
    while second is not None:
        first_next = first.next
        second_next = second.next

        first.next = second
        second.next = first_next

        first = first_next
        second = second_next

    return head


def merge_k_sorted(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """Difficult: merge K sorted lists using a min-heap.

    Complexity: O(N log K) time and O(K) heap space for N total nodes.
    The sequence number provides stable tie-breaking without comparing nodes.
    """
    if any(has_cycle(head) for head in lists):
        raise ValueError("All input lists must be acyclic.")

    # Validate that inputs are disjoint. Merging shared nodes is ambiguous.
    seen = set()
    for head in lists:
        current = head
        while current is not None:
            if id(current) in seen:
                raise ValueError("Input lists must not share nodes.")
            seen.add(id(current))
            current = current.next

    heap = []
    sequence = itertools.count()

    for head in lists:
        if head is not None:
            heapq.heappush(heap, (head.value, next(sequence), head))

    dummy = ListNode(0)
    tail = dummy

    while heap:
        _, _, node = heapq.heappop(heap)
        following = node.next

        tail.next = node
        tail = node

        if following is not None:
            heapq.heappush(
                heap, (following.value, next(sequence), following)
            )

    tail.next = None
    return dummy.next


class LinkedListAssessmentTests(unittest.TestCase):
    def test_easy_reverse(self):
        self.assertEqual(to_list(reverse_list(build_list([1, 2, 3]))),
                         [3, 2, 1])
        self.assertIsNone(reverse_list(None))
        self.assertEqual(to_list(reverse_list(build_list([7]))), [7])

    def test_easy_cycle(self):
        head = build_list([1, 2, 3])
        head.next.next.next = head.next
        self.assertTrue(has_cycle(head))
        self.assertFalse(has_cycle(build_list([1, 2, 3])))
        self.assertFalse(has_cycle(None))

    def test_easy_merge_two(self):
        result = merge_two_sorted(
            build_list([1, 3, 5]), build_list([1, 2, 6])
        )
        self.assertEqual(to_list(result), [1, 1, 2, 3, 5, 6])
        self.assertEqual(to_list(merge_two_sorted(None, build_list([4]))),
                         [4])

    def test_medium_remove_nth(self):
        self.assertEqual(
            to_list(remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 2)),
            [1, 2, 3, 5],
        )
        self.assertEqual(to_list(remove_nth_from_end(build_list([1]), 1)), [])
        with self.assertRaises(ValueError):
            remove_nth_from_end(build_list([1, 2]), 3)

    def test_medium_intersection(self):
        shared = build_list([8, 9])
        first = ListNode(1, ListNode(2, shared))
        second = ListNode(3, shared)
        self.assertIs(get_intersection_node(first, second), shared)
        self.assertIsNone(
            get_intersection_node(build_list([1]), build_list([1]))
        )

    def test_medium_palindrome_restores_links(self):
        head = build_list([1, 2, 3, 2, 1])
        original_nodes = []
        current = head
        while current:
            original_nodes.append(current)
            current = current.next

        self.assertTrue(is_palindrome(head))
        self.assertEqual(to_list(head), [1, 2, 3, 2, 1])

        current = head
        for node in original_nodes:
            self.assertIs(current, node)
            current = current.next

        self.assertFalse(is_palindrome(build_list([1, 2, 3])))

    def test_medium_reorder(self):
        self.assertEqual(to_list(reorder_list(build_list([1, 2, 3, 4]))),
                         [1, 4, 2, 3])
        self.assertEqual(to_list(reorder_list(build_list([1, 2, 3, 4, 5]))),
                         [1, 5, 2, 4, 3])
        self.assertIsNone(reorder_list(None))

    def test_difficult_merge_k(self):
        heads = [
            build_list([1, 4, 7]),
            build_list([2, 5, 8]),
            build_list([3, 6, 9]),
            None,
        ]
        self.assertEqual(to_list(merge_k_sorted(heads)),
                         list(range(1, 10)))
        self.assertIsNone(merge_k_sorted([]))

    def test_invalid_cycle_conversion(self):
        head = build_list([1, 2])
        head.next.next = head
        with self.assertRaises(ValueError):
            to_list(head)


def run_demonstration() -> None:
    examples = [
        ("Reverse", lambda: reverse_list(build_list([1, 2, 3, 4]))),
        ("Remove second from end",
         lambda: remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 2)),
        ("Reorder", lambda: reorder_list(build_list([1, 2, 3, 4, 5]))),
        ("Merge K", lambda: merge_k_sorted([
            build_list([1, 4, 7]), build_list([2, 5]), build_list([3, 6])
        ])),
    ]

    for title, operation in examples:
        print(f"{title}: {to_list(operation())}")

    print(f"Cycle detected: ", end="")
    cyclic = build_list([10, 20, 30])
    cyclic.next.next.next = cyclic.next
    print(has_cycle(cyclic))


if __name__ == "__main__":
    run_demonstration()
    unittest.main(argv=["linked_list_assessment.py"], exit=False)
