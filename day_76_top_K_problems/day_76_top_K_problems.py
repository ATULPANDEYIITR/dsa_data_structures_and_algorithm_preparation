#!/usr/bin/env python3
"""
Top-K Problems: Kth Largest, Kth Smallest, Top-K Frequent, K Closest Elements.

Demonstrates:
- Sorting and heap-based selection
- Min-heaps and max-heaps
- Frequency dictionaries and bucket sorting
- Quickselect with three-way partitioning
- Binary search for closest elements
- Input validation, edge cases, and automated assertions

Python standard library only.
"""

from __future__ import annotations

import heapq
import random
import unittest
from collections import Counter
from dataclasses import dataclass
from typing import Sequence


class SelectionError(ValueError):
    """Raised when a selection request is invalid."""


def validate_k(k: int, n: int, allow_zero: bool = False) -> None:
    if isinstance(k, bool) or not isinstance(k, int):
        raise SelectionError("k must be an integer")

    minimum = 0 if allow_zero else 1

    if not minimum <= k <= n:
        raise SelectionError(f"k must be between {minimum} and {n}")


def kth_largest_sort(nums: Sequence[int], k: int) -> int:
    """Sorting solution: O(n log n) time and O(n) space."""
    validate_k(k, len(nums))
    return sorted(nums, reverse=True)[k - 1]


def kth_smallest_sort(nums: Sequence[int], k: int) -> int:
    """Sorting solution: O(n log n) time and O(n) space."""
    validate_k(k, len(nums))
    return sorted(nums)[k - 1]


def kth_largest_heap(nums: Sequence[int], k: int) -> int:
    """Maintain a min-heap containing the k largest values."""
    validate_k(k, len(nums))
    return heapq.nlargest(k, nums)[-1]


def kth_smallest_heap(nums: Sequence[int], k: int) -> int:
    """Maintain a max-selection result using a bounded min-heap."""
    validate_k(k, len(nums))
    return -heapq.nlargest(k, (-value for value in nums))[-1]


def kth_largest_quickselect(nums: Sequence[int], k: int) -> int:
    """
    Average O(n) time, O(1) auxiliary partition space.

    Three-way partitioning handles duplicate-heavy input efficiently.
    Randomization reduces the likelihood of consistently poor pivots.
    """
    validate_k(k, len(nums))

    values = list(nums)
    target = k - 1
    left, right = 0, len(values) - 1

    while left <= right:
        pivot = values[random.randrange(left, right + 1)]

        low = left
        current = left
        high = right

        while current <= high:
            if values[current] > pivot:
                values[low], values[current] = values[current], values[low]
                low += 1
                current += 1
            elif values[current] < pivot:
                values[current], values[high] = values[high], values[current]
                high -= 1
            else:
                current += 1

        if target < low:
            right = low - 1
        elif target > high:
            left = high + 1
        else:
            return values[target]

    raise RuntimeError("Quickselect failed unexpectedly")


def top_k_frequent(nums: Sequence[int], k: int) -> list[int]:
    """
    Return k most frequent distinct values.

    Frequency descending, value ascending for deterministic ties.
    O(n + u log u) time, where u is the number of unique values.
    """
    frequencies = Counter(nums)
    validate_k(k, len(frequencies), allow_zero=True)

    ordered = sorted(
        frequencies,
        key=lambda value: (-frequencies[value], value)
    )
    return ordered[:k]


def top_k_frequent_heap(nums: Sequence[int], k: int) -> list[int]:
    """Heap-based implementation with deterministic tie-breaking."""
    frequencies = Counter(nums)
    validate_k(k, len(frequencies), allow_zero=True)

    return [
        value
        for value, frequency in heapq.nsmallest(
            k,
            frequencies.items(),
            key=lambda item: (-item[1], item[0])
        )
    ]


def top_k_frequent_bucket(nums: Sequence[int], k: int) -> list[int]:
    """
    Bucket sort by frequency.

    O(n + u log u) in this deterministic implementation because
    values within each frequency bucket are sorted.
    """
    frequencies = Counter(nums)
    validate_k(k, len(frequencies), allow_zero=True)

    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]

    for value, frequency in frequencies.items():
        buckets[frequency].append(value)

    result = []

    for frequency in range(len(nums), 0, -1):
        result.extend(sorted(buckets[frequency]))

        if len(result) >= k:
            return result[:k]

    return result


def k_closest_elements(
    nums: Sequence[int],
    k: int,
    target: int
) -> list[int]:
    """
    Return k closest elements from a sorted array.

    Binary-search the left boundary of a contiguous window.
    O(log(n-k) + k) time and O(k) output space.

    Equal distances favor the smaller value.
    """
    if any(nums[i] > nums[i + 1] for i in range(len(nums) - 1)):
        raise SelectionError("Input must be sorted in ascending order")

    validate_k(k, len(nums), allow_zero=True)

    if k == 0:
        return []

    left, right = 0, len(nums) - k

    while left < right:
        middle = (left + right) // 2

        if target - nums[middle] > nums[middle + k] - target:
            left = middle + 1
        else:
            right = middle

    return list(nums[left:left + k])


def k_closest_elements_heap(
    nums: Sequence[int],
    k: int,
    target: int
) -> list[int]:
    """Alternative: O(n log k + k log k) time."""
    validate_k(k, len(nums), allow_zero=True)

    if k == 0:
        return []

    selected = heapq.nsmallest(
        k,
        nums,
        key=lambda value: (abs(value - target), value)
    )

    return sorted(selected)


@dataclass(frozen=True)
class TopKResult:
    operation: str
    values: tuple[int, ...]


class TopKService:
    """Small service layer for consistent operation and result handling."""

    @staticmethod
    def execute(
        operation: str,
        nums: Sequence[int],
        k: int,
        target: int | None = None
    ) -> TopKResult:

        operations = {
            "kth_largest": lambda: [kth_largest_heap(nums, k)],
            "kth_smallest": lambda: [kth_smallest_heap(nums, k)],
            "top_frequent": lambda: top_k_frequent(nums, k),
        }

        if operation == "closest":
            if target is None:
                raise SelectionError("Target is required for closest")
            result = k_closest_elements(nums, k, target)
        elif operation in operations:
            result = operations[operation]()
        else:
            raise SelectionError(f"Unsupported operation: {operation}")

        return TopKResult(operation, tuple(result))


class TopKTests(unittest.TestCase):

    def test_kth_largest(self):
        nums = [3, 2, 1, 5, 6, 4]
        self.assertEqual(kth_largest_sort(nums, 2), 5)
        self.assertEqual(kth_largest_heap(nums, 2), 5)
        self.assertEqual(kth_largest_quickselect(nums, 2), 5)

    def test_kth_smallest(self):
        self.assertEqual(kth_smallest_sort([7, 10, 4, 3, 20, 15], 3), 7)
        self.assertEqual(kth_smallest_heap([7, 10, 4, 3, 20, 15], 3), 7)

    def test_duplicates(self):
        nums = [5, 5, 5, 2, 2, 8]
        self.assertEqual(kth_largest_quickselect(nums, 3), 5)

    def test_top_frequent(self):
        nums = [1, 1, 1, 2, 2, 3]
        self.assertEqual(top_k_frequent(nums, 2), [1, 2])
        self.assertEqual(top_k_frequent_heap(nums, 2), [1, 2])

    def test_top_frequent_ties(self):
        self.assertEqual(top_k_frequent([4, 3, 2, 1], 2), [1, 2])

    def test_closest(self):
        nums = [1, 2, 3, 4, 5]
        self.assertEqual(k_closest_elements(nums, 4, 3), [1, 2, 3, 4])
        self.assertEqual(k_closest_elements_heap(nums, 4, 3), [2, 3, 4, 5])

    def test_empty_selection(self):
        self.assertEqual(top_k_frequent([], 0), [])
        self.assertEqual(k_closest_elements([], 0, 5), [])

    def test_invalid_k(self):
        with self.assertRaises(SelectionError):
            kth_largest_heap([1, 2], 3)

    def test_unsorted_closest(self):
        with self.assertRaises(SelectionError):
            k_closest_elements([3, 1, 2], 2, 2)

    def test_service(self):
        result = TopKService.execute("kth_largest", [1, 8, 3, 6], 2)
        self.assertEqual(result.values, (6,))


def demonstrate() -> None:
    nums = [3, 2, 1, 5, 6, 4]

    print("TOP-K PROBLEM DEMONSTRATION")
    print("-" * 40)

    print("Input:", nums)
    print("Second largest:", kth_largest_heap(nums, 2))
    print("Third smallest:", kth_smallest_heap(nums, 3))
    print("Second largest using quickselect:",
          kth_largest_quickselect(nums, 2))

    frequencies = [1, 1, 1, 2, 2, 3, 4, 4, 4, 4]
    print("\nFrequency input:", frequencies)
    print("Top two frequent:", top_k_frequent(frequencies, 2))
    print("Top two using buckets:", top_k_frequent_bucket(frequencies, 2))

    sorted_values = [1, 2, 3, 4, 5]
    print("\nSorted input:", sorted_values)
    print("Four closest to 3:",
          k_closest_elements(sorted_values, 4, 3))

    print("\nRunning automated tests...")


if __name__ == "__main__":
    demonstrate()
    unittest.main(argv=["top_k"], exit=False, verbosity=2)
