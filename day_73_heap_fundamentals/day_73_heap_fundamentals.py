#!/usr/bin/env python3
"""
Heap Fundamentals
Complete binary trees, min heaps, max heaps, parent-child relationships,
array representation, heap construction, insertion, deletion, and heap sort.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Iterable, Optional, TypeVar
import heapq
import random

T = TypeVar("T")


class HeapType(Enum):
    MIN = "min"
    MAX = "max"


@dataclass
class BinaryHeap(Generic[T]):
    """Array-backed binary heap supporting min and max ordering."""

    heap_type: HeapType = HeapType.MIN
    data: list[T] = field(default_factory=list)

    def __post_init__(self):
        self.heapify(self.data)

    def _higher_priority(self, a: T, b: T) -> bool:
        return a < b if self.heap_type == HeapType.MIN else a > b

    @staticmethod
    def parent(index: int) -> Optional[int]:
        if index <= 0:
            return None
        return (index - 1) // 2

    @staticmethod
    def left_child(index: int) -> int:
        return 2 * index + 1

    @staticmethod
    def right_child(index: int) -> int:
        return 2 * index + 2

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def peek(self) -> T:
        if not self.data:
            raise IndexError("Cannot inspect an empty heap.")
        return self.data[0]

    def push(self, value: T) -> None:
        """Insert an element and restore heap order."""
        self.data.append(value)
        self._sift_up(len(self.data) - 1)
        assert self.validate()

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = self.parent(index)
            if parent is None:
                break

            if not self._higher_priority(
                self.data[index], self.data[parent]
            ):
                break

            self.data[index], self.data[parent] = (
                self.data[parent],
                self.data[index],
            )
            index = parent

    def pop(self) -> T:
        """Remove and return the root element."""
        if not self.data:
            raise IndexError("Cannot remove from an empty heap.")

        result = self.data[0]
        last = self.data.pop()

        if self.data:
            self.data[0] = last
            self._sift_down(0)

        assert self.validate()
        return result

    def _sift_down(self, index: int) -> None:
        size = len(self.data)

        while True:
            best = index
            left = self.left_child(index)
            right = self.right_child(index)

            if (
                left < size
                and self._higher_priority(
                    self.data[left], self.data[best]
                )
            ):
                best = left

            if (
                right < size
                and self._higher_priority(
                    self.data[right], self.data[best]
                )
            ):
                best = right

            if best == index:
                break

            self.data[index], self.data[best] = (
                self.data[best],
                self.data[index],
            )
            index = best

    def heapify(self, values: Iterable[T]) -> None:
        """Build a heap using bottom-up construction in O(n)."""
        self.data = list(values)

        for index in range(len(self.data) // 2 - 1, -1, -1):
            self._sift_down(index)

        assert self.validate()

    def validate(self) -> bool:
        """Verify the heap-order property."""
        for index in range(len(self.data)):
            for child in (
                self.left_child(index),
                self.right_child(index),
            ):
                if child < len(self.data):
                    if self._higher_priority(
                        self.data[child], self.data[index]
                    ):
                        return False
        return True

    def levels(self) -> list[list[T]]:
        """Return elements grouped by complete-tree level."""
        result = []
        start = 0
        level_size = 1

        while start < len(self.data):
            result.append(self.data[start:start + level_size])
            start += level_size
            level_size *= 2

        return result

    def tree_relationships(self) -> list[dict]:
        """Display array indexes and parent-child relationships."""
        relationships = []

        for index, value in enumerate(self.data):
            parent = self.parent(index)
            left = self.left_child(index)
            right = self.right_child(index)

            relationships.append({
                "index": index,
                "value": value,
                "parent": (
                    self.data[parent] if parent is not None else None
                ),
                "left": (
                    self.data[left] if left < len(self.data) else None
                ),
                "right": (
                    self.data[right] if right < len(self.data) else None
                ),
            })

        return relationships

    def sorted_values(self) -> list[T]:
        """Return ordered values without modifying the original heap."""
        copy = BinaryHeap(self.heap_type, self.data.copy())
        return [copy.pop() for _ in range(len(copy))]


def heap_sort(values: Iterable[T], reverse: bool = False) -> list[T]:
    """Heap sort using the standard library."""
    result = list(values)
    heapq.heapify(result)

    ordered = [heapq.heappop(result) for _ in range(len(result))]
    return ordered[::-1] if reverse else ordered


def demonstrate():
    values = [40, 10, 30, 50, 20, 60, 15]

    print("INPUT:", values)

    min_heap = BinaryHeap[int](HeapType.MIN, values)
    print("\nMIN HEAP:", min_heap.data)
    print("MINIMUM:", min_heap.peek())
    print("LEVELS:", min_heap.levels())
    print("RELATIONSHIPS:")

    for relationship in min_heap.tree_relationships():
        print(relationship)

    min_heap.push(5)
    print("\nAFTER INSERTION:", min_heap.data)
    print("REMOVED MINIMUM:", min_heap.pop())
    print("AFTER DELETION:", min_heap.data)

    max_heap = BinaryHeap[int](HeapType.MAX, values)
    print("\nMAX HEAP:", max_heap.data)
    print("MAXIMUM:", max_heap.peek())
    print("REMOVED MAXIMUM:", max_heap.pop())

    print("\nMIN HEAP SORT:", min_heap.sorted_values())
    print("ASCENDING HEAP SORT:", heap_sort(values))
    print("DESCENDING HEAP SORT:", heap_sort(values, reverse=True))

    # Empty heap and single-element edge cases.
    empty = BinaryHeap[int]()
    try:
        empty.pop()
    except IndexError as error:
        print("\nEXPECTED EMPTY-HEAP ERROR:", error)

    single = BinaryHeap[int](HeapType.MIN, [42])
    assert single.pop() == 42
    assert len(single) == 0

    # Duplicate and negative values.
    duplicates = BinaryHeap[int](HeapType.MIN, [4, 4, -2, 8, 1, -2])
    assert duplicates.sorted_values() == [-2, -2, 1, 4, 4, 8]

    # Randomized validation.
    random.seed(42)
    random_values = [random.randint(-1000, 1000) for _ in range(1000)]

    random_heap = BinaryHeap[int](HeapType.MIN, random_values)
    extracted = [random_heap.pop() for _ in range(len(random_heap))]
    assert extracted == sorted(random_values)

    print("\nALL ASSERTIONS PASSED.")


if __name__ == "__main__":
    demonstrate()
