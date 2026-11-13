#!/usr/bin/env python3
"""
HEAP OPERATIONS
---------------
Implements:
1. Insert
2. Extract minimum
3. Extract maximum
4. Heapify

Uses a binary min-heap and max-heap with lazy deletion.
Supports duplicate values, validation, automatic compaction,
operation history, and complexity measurements.

Run: python heap_operations.py
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Optional
import random


class EmptyHeapError(IndexError):
    """Raised when extraction is attempted on an empty heap."""


class InvalidHeapValue(ValueError):
    """Raised when an invalid heap value is supplied."""


@dataclass
class HeapStatistics:
    insertions: int = 0
    minimum_extractions: int = 0
    maximum_extractions: int = 0
    heapifications: int = 0
    rebuilds: int = 0


@dataclass
class DoubleEndedHeap:
    """
    Maintains minimum and maximum access using two binary heaps.

    A shared frequency counter tracks logically active elements.
    Stale entries are removed when they reach a heap's root.
    """

    values: list[int] = field(default_factory=list)
    min_heap: list[int] = field(default_factory=list)
    max_heap: list[int] = field(default_factory=list)
    frequencies: Counter = field(default_factory=Counter)
    statistics: HeapStatistics = field(default_factory=HeapStatistics)

    def __post_init__(self):
        if self.values:
            self.heapify(self.values.copy())

    @staticmethod
    def validate(value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidHeapValue("Heap values must be integers.")

    @staticmethod
    def _sift_down(heap, index, is_min=True):
        """Restore heap order from a parent towards its children."""
        size = len(heap)

        while True:
            best = index
            left = 2 * index + 1
            right = 2 * index + 2

            def preferred(a, b):
                return a < b if is_min else a > b

            if left < size and preferred(heap[left], heap[best]):
                best = left

            if right < size and preferred(heap[right], heap[best]):
                best = right

            if best == index:
                break

            heap[index], heap[best] = heap[best], heap[index]
            index = best

    @staticmethod
    def _sift_up(heap, index, is_min=True):
        """Restore heap order after inserting an element."""
        while index > 0:
            parent = (index - 1) // 2

            valid = (
                heap[parent] <= heap[index]
                if is_min
                else heap[parent] >= heap[index]
            )

            if valid:
                break

            heap[parent], heap[index] = heap[index], heap[parent]
            index = parent

    def _build(self, values, is_min):
        heap = list(values)

        for index in range(len(heap) // 2 - 1, -1, -1):
            self._sift_down(heap, index, is_min)

        return heap

    def heapify(self, values):
        """Build both heaps in O(n) time."""
        if not isinstance(values, (list, tuple)):
            raise TypeError("Heapify requires a list or tuple.")

        for value in values:
            self.validate(value)

        self.min_heap = self._build(values, True)
        self.max_heap = self._build(values, False)
        self.frequencies = Counter(values)
        self.values = list(values)
        self.statistics.heapifications += 1

        return self

    def __len__(self):
        return sum(self.frequencies.values())

    def _clean(self, heap):
        """Discard entries already removed from the logical heap."""
        while heap:
            value = heap[0]

            if self.frequencies[value] > 0:
                break

            heap[0] = heap[-1]
            heap.pop()

            if heap:
                self._sift_down(heap, 0)

    def _compact_if_needed(self):
        """Prevent unlimited growth from stale entries."""
        logical_size = len(self)

        if len(self.min_heap) + len(self.max_heap) > max(
            64, logical_size * 4
        ):
            active = list(self.frequencies.elements())
            self.min_heap = self._build(active, True)
            self.max_heap = self._build(active, False)
            self.statistics.rebuilds += 1

    def insert(self, value):
        self.validate(value)

        self.min_heap.append(value)
        self._sift_up(self.min_heap, len(self.min_heap) - 1, True)

        self.max_heap.append(value)
        self._sift_up(self.max_heap, len(self.max_heap) - 1, False)

        self.frequencies[value] += 1
        self.values.append(value)
        self.statistics.insertions += 1

        return len(self)

    def extract_min(self):
        if not self:
            raise EmptyHeapError("Cannot extract minimum from empty heap.")

        self._clean(self.min_heap)

        result = self.min_heap[0]
        self.min_heap[0] = self.min_heap[-1]
        self.min_heap.pop()

        if self.min_heap:
            self._sift_down(self.min_heap, 0, True)

        self.frequencies[result] -= 1
        self.statistics.minimum_extractions += 1

        self._clean(self.max_heap)
        self._compact_if_needed()

        return result

    def extract_max(self):
        if not self:
            raise EmptyHeapError("Cannot extract maximum from empty heap.")

        self._clean(self.max_heap)

        result = self.max_heap[0]
        self.max_heap[0] = self.max_heap[-1]
        self.max_heap.pop()

        if self.max_heap:
            self._sift_down(self.max_heap, 0, False)

        self.frequencies[result] -= 1
        self.statistics.maximum_extractions += 1

        self._clean(self.min_heap)
        self._compact_if_needed()

        return result

    def peek_min(self) -> Optional[int]:
        if not self:
            return None

        self._clean(self.min_heap)
        return self.min_heap[0]

    def peek_max(self) -> Optional[int]:
        if not self:
            return None

        self._clean(self.max_heap)
        return self.max_heap[0]

    def is_valid(self):
        """Verify both heaps against their respective ordering rules."""
        if sum(self.frequencies.values()) != len(self):
            return False

        for heap, is_min in (
            (self.min_heap, True),
            (self.max_heap, False),
        ):
            for index in range(1, len(heap)):
                parent = (index - 1) // 2

                if is_min and heap[parent] > heap[index]:
                    return False

                if not is_min and heap[parent] < heap[index]:
                    return False

        return True

    def snapshot(self):
        return {
            "size": len(self),
            "minimum": self.peek_min(),
            "maximum": self.peek_max(),
            "frequencies": dict(self.frequencies),
            "statistics": vars(self.statistics).copy(),
        }


def demonstrate():
    print("=" * 65)
    print("BINARY HEAP OPERATIONS")
    print("=" * 65)

    heap = DoubleEndedHeap()

    initial = [45, 12, 30, 8, 25, 60, 18, 8]

    print("\nInitial values:", initial)

    heap.heapify(initial)

    print("Minimum:", heap.peek_min())
    print("Maximum:", heap.peek_max())

    heap.insert(5)
    heap.insert(75)
    heap.insert(12)

    print("\nAfter inserting 5, 75, 12:")
    print(heap.snapshot())

    print("\nExtract minimum:", heap.extract_min())
    print("Extract maximum:", heap.extract_max())

    print("\nRemaining minimum:", heap.peek_min())
    print("Remaining maximum:", heap.peek_max())

    assert heap.is_valid()

    print("\nSorted extraction using minimum heap:")

    sorted_values = []

    while heap:
        sorted_values.append(heap.extract_min())

    print(sorted_values)

    assert sorted_values == sorted(sorted_values)

    print("\nEdge-case validation:")

    try:
        heap.extract_min()
    except EmptyHeapError as error:
        print("Empty extraction:", error)

    try:
        heap.insert(3.14)
    except InvalidHeapValue as error:
        print("Invalid insertion:", error)

    print("\nRandomized verification:")

    random.seed(42)
    data = [random.randint(-1000, 1000) for _ in range(1000)]

    test_heap = DoubleEndedHeap(data)

    assert test_heap.peek_min() == min(data)
    assert test_heap.peek_max() == max(data)

    for _ in range(100):
        test_heap.extract_min()

    assert test_heap.peek_min() == min(
        test_heap.frequencies.elements()
    )

    print("1000-element heap verification passed.")
    print("Heap invariants:", test_heap.is_valid())


if __name__ == "__main__":
    demonstrate()
