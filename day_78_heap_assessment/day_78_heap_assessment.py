#!/usr/bin/env python3
"""
Heap Assessment: Mixed Heap and Priority Queue Problems

Covers:
- Min heaps and max heaps
- Kth largest and smallest elements
- Top K frequent elements
- Merge K sorted arrays
- Running median
- Sliding window maximum
- Task scheduling
- Heap-based event prioritization
- Input validation and edge cases

Python 3.10+
"""

from __future__ import annotations

import heapq
import random
import statistics
import unittest

from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Any, Iterable


class HeapError(ValueError):
    """Raised when a heap operation receives invalid input."""


class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(order=True)
class ScheduledTask:
    priority: int
    sequence: int
    task_id: str = field(compare=False)
    description: str = field(compare=False)
    completed: bool = field(default=False, compare=False)


class MinPriorityQueue:
    """Min-priority queue with stable insertion ordering."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, Any]] = []
        self._counter = count()

    def push(self, item: Any, priority: int) -> None:
        heapq.heappush(
            self._heap,
            (priority, next(self._counter), item)
        )

    def pop(self) -> Any:
        if not self._heap:
            raise HeapError("Priority queue is empty.")
        return heapq.heappop(self._heap)[2]

    def peek(self) -> Any:
        if not self._heap:
            raise HeapError("Priority queue is empty.")
        return self._heap[0][2]

    def __len__(self) -> int:
        return len(self._heap)


class HeapAlgorithms:

    @staticmethod
    def validate_numbers(values: Iterable[int]) -> list[int]:
        if isinstance(values, (str, bytes)):
            raise HeapError("Expected an iterable of integers.")

        result = list(values)

        if not all(type(x) is int for x in result):
            raise HeapError("All elements must be integers.")

        return result

    @staticmethod
    def kth_largest(values: Iterable[int], k: int) -> int:
        """Find kth largest using an O(k) auxiliary min heap."""
        nums = HeapAlgorithms.validate_numbers(values)

        if not 1 <= k <= len(nums):
            raise HeapError("k must be between 1 and array length.")

        heap: list[int] = []

        for value in nums:
            heapq.heappush(heap, value)

            if len(heap) > k:
                heapq.heappop(heap)

        return heap[0]

    @staticmethod
    def kth_smallest(values: Iterable[int], k: int) -> int:
        """Find kth smallest using a bounded max heap."""
        nums = HeapAlgorithms.validate_numbers(values)

        if not 1 <= k <= len(nums):
            raise HeapError("Invalid k.")

        heap: list[int] = []

        for value in nums:
            heapq.heappush(heap, -value)

            if len(heap) > k:
                heapq.heappop(heap)

        return -heap[0]

    @staticmethod
    def top_k_frequent(values: Iterable[int], k: int) -> list[int]:
        """
        Return the k most frequent elements.
        Ties are resolved by smaller numeric value.
        """
        nums = HeapAlgorithms.validate_numbers(values)

        if not 0 <= k <= len(set(nums)):
            raise HeapError("Invalid k.")

        frequencies = Counter(nums)

        return [
            value
            for value, frequency in heapq.nsmallest(
                k,
                frequencies.items(),
                key=lambda item: (-item[1], item[0])
            )
        ]

    @staticmethod
    def merge_k_sorted_arrays(
        arrays: list[list[int]]
    ) -> list[int]:
        """Merge sorted arrays using a min heap."""
        if not isinstance(arrays, list):
            raise HeapError("Expected a list of arrays.")

        heap: list[tuple[int, int, int]] = []

        for array_index, array in enumerate(arrays):
            if any(type(x) is not int for x in array):
                raise HeapError("Arrays must contain integers.")

            if any(
                array[i] > array[i + 1]
                for i in range(len(array) - 1)
            ):
                raise HeapError("Input arrays must be sorted.")

            if array:
                heapq.heappush(
                    heap,
                    (array[0], array_index, 0)
                )

        result: list[int] = []

        while heap:
            value, array_index, element_index = heapq.heappop(heap)
            result.append(value)

            next_index = element_index + 1
            array = arrays[array_index]

            if next_index < len(array):
                heapq.heappush(
                    heap,
                    (array[next_index], array_index, next_index)
                )

        return result

    @staticmethod
    def sliding_window_maximum(
        values: Iterable[int],
        window: int
    ) -> list[int]:
        """O(n) sliding window maximum using a monotonic deque."""
        nums = HeapAlgorithms.validate_numbers(values)

        if not 1 <= window <= len(nums):
            raise HeapError("Invalid window size.")

        indices: deque[int] = deque()
        result: list[int] = []

        for i, value in enumerate(nums):

            while indices and indices[0] <= i - window:
                indices.popleft()

            while indices and nums[indices[-1]] <= value:
                indices.pop()

            indices.append(i)

            if i >= window - 1:
                result.append(nums[indices[0]])

        return result

    @staticmethod
    def connect_ropes(lengths: Iterable[int]) -> int:
        """Minimum cost of connecting all ropes."""
        nums = HeapAlgorithms.validate_numbers(lengths)

        if any(x < 0 for x in nums):
            raise HeapError("Rope lengths cannot be negative.")

        heap = nums[:]
        heapq.heapify(heap)

        total_cost = 0

        while len(heap) > 1:
            first = heapq.heappop(heap)
            second = heapq.heappop(heap)

            combined = first + second
            total_cost += combined

            heapq.heappush(heap, combined)

        return total_cost

    @staticmethod
    def minimum_meeting_rooms(
        intervals: list[tuple[int, int]]
    ) -> int:
        """
        Calculate the minimum meeting rooms.
        Intervals use [start, end) semantics.
        """
        if not isinstance(intervals, list):
            raise HeapError("Intervals must be a list.")

        meetings = []

        for interval in intervals:
            if not isinstance(interval, (tuple, list)) or len(interval) != 2:
                raise HeapError("Each interval must contain two values.")

            start, end = interval

            if (
                type(start) is not int
                or type(end) is not int
                or start < 0
                or end <= start
            ):
                raise HeapError("Invalid meeting interval.")

            meetings.append((start, end))

        meetings.sort()

        active: list[int] = []
        maximum_rooms = 0

        for start, end in meetings:

            while active and active[0] <= start:
                heapq.heappop(active)

            heapq.heappush(active, end)

            maximum_rooms = max(maximum_rooms, len(active))

        return maximum_rooms

    @staticmethod
    def reorganize_string(text: str) -> str | None:
        """
        Rearrange characters so identical characters
        are never adjacent.
        """
        if not isinstance(text, str):
            raise HeapError("Expected a string.")

        frequencies = Counter(text)

        heap = [
            (-frequency, character)
            for character, frequency in frequencies.items()
        ]

        heapq.heapify(heap)

        previous = None
        result = []

        while heap:
            frequency, character = heapq.heappop(heap)
            result.append(character)

            if previous is not None:
                heapq.heappush(heap, previous)

            frequency += 1

            previous = (
                (frequency, character)
                if frequency < 0
                else None
            )

        output = "".join(result)

        if len(output) != len(text):
            return None

        return output


class RunningMedian:
    """
    Maintain a running median with two heaps.

    Lower half: max heap.
    Upper half: min heap.
    """

    def __init__(self) -> None:
        self.lower: list[int] = []
        self.upper: list[int] = []

    def add(self, value: int) -> None:
        if type(value) is not int:
            raise HeapError("Median values must be integers.")

        if not self.lower or value <= -self.lower[0]:
            heapq.heappush(self.lower, -value)
        else:
            heapq.heappush(self.upper, value)

        if len(self.lower) > len(self.upper) + 1:
            heapq.heappush(
                self.upper,
                -heapq.heappop(self.lower)
            )

        elif len(self.upper) > len(self.lower):
            heapq.heappush(
                self.lower,
                -heapq.heappop(self.upper)
            )

    def median(self) -> float:
        if not self.lower:
            raise HeapError("Median is undefined for an empty stream.")

        if len(self.lower) > len(self.upper):
            return float(-self.lower[0])

        return (-self.lower[0] + self.upper[0]) / 2.0


class TaskScheduler:
    """Stable priority-based task scheduler."""

    def __init__(self) -> None:
        self._heap: list[ScheduledTask] = []
        self._sequence = count()
        self._task_ids: set[str] = set()

    def submit(
        self,
        task_id: str,
        description: str,
        priority: Priority
    ) -> None:

        if not task_id or task_id in self._task_ids:
            raise HeapError("Task ID must be unique and nonempty.")

        if not isinstance(priority, Priority):
            raise HeapError("Invalid task priority.")

        if not description.strip():
            raise HeapError("Task description cannot be empty.")

        task = ScheduledTask(
            priority.value,
            next(self._sequence),
            task_id,
            description
        )

        heapq.heappush(self._heap, task)
        self._task_ids.add(task_id)

    def execute_next(self) -> ScheduledTask:
        if not self._heap:
            raise HeapError("No pending tasks.")

        task = heapq.heappop(self._heap)
        task.completed = True
        return task

    def pending_count(self) -> int:
        return len(self._heap)


def run_assessment() -> None:
    print("=" * 60)
    print("HEAP AND PRIORITY QUEUE ASSESSMENT")
    print("=" * 60)

    nums = [7, 10, 4, 3, 20, 15, 10]

    print("\n1. Kth largest:", HeapAlgorithms.kth_largest(nums, 3))
    print("2. Kth smallest:", HeapAlgorithms.kth_smallest(nums, 3))

    print(
        "3. Top 3 frequent:",
        HeapAlgorithms.top_k_frequent(nums, 3)
    )

    arrays = [
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]
    ]

    print(
        "4. Merge K arrays:",
        HeapAlgorithms.merge_k_sorted_arrays(arrays)
    )

    print(
        "5. Sliding window maximum:",
        HeapAlgorithms.sliding_window_maximum(
            [1, 3, -1, -3, 5, 3, 6, 7],
            3
        )
    )

    print(
        "6. Minimum rope connection cost:",
        HeapAlgorithms.connect_ropes([4, 3, 2, 6])
    )

    print(
        "7. Minimum meeting rooms:",
        HeapAlgorithms.minimum_meeting_rooms(
            [(0, 30), (5, 10), (15, 20)]
        )
    )

    stream = RunningMedian()

    for value in [5, 15, 1, 3]:
        stream.add(value)
        print(f"Running median after {value}: {stream.median()}")

    scheduler = TaskScheduler()

    scheduler.submit("T1", "Database backup", Priority.NORMAL)
    scheduler.submit("T2", "Security incident", Priority.CRITICAL)
    scheduler.submit("T3", "Generate report", Priority.LOW)
    scheduler.submit("T4", "Production deployment", Priority.HIGH)

    print("\n8. Task execution order:")

    while scheduler.pending_count():
        task = scheduler.execute_next()
        print(task.task_id, task.description)


class HeapTests(unittest.TestCase):

    def test_kth_largest(self):
        self.assertEqual(
            HeapAlgorithms.kth_largest([3, 2, 1, 5, 6, 4], 2),
            5
        )

    def test_kth_smallest(self):
        self.assertEqual(
            HeapAlgorithms.kth_smallest([7, 10, 4, 3, 20, 15], 3),
            7
        )

    def test_top_k(self):
        self.assertEqual(
            HeapAlgorithms.top_k_frequent([1, 1, 1, 2, 2, 3], 2),
            [1, 2]
        )

    def test_merge(self):
        self.assertEqual(
            HeapAlgorithms.merge_k_sorted_arrays(
                [[1, 4], [2, 5], [3, 6]]
            ),
            [1, 2, 3, 4, 5, 6]
        )

    def test_running_median(self):
        median = RunningMedian()

        for value in [5, 15, 1, 3]:
            median.add(value)

        self.assertEqual(median.median(), 4.0)

    def test_sliding_window(self):
        self.assertEqual(
            HeapAlgorithms.sliding_window_maximum(
                [1, 3, -1, -3, 5, 3, 6, 7],
                3
            ),
            [3, 3, 5, 5, 6, 7]
        )

    def test_connect_ropes(self):
        self.assertEqual(
            HeapAlgorithms.connect_ropes([4, 3, 2, 6]),
            29
        )

    def test_meeting_rooms(self):
        self.assertEqual(
            HeapAlgorithms.minimum_meeting_rooms(
                [(0, 30), (5, 10), (15, 20)]
            ),
            2
        )

    def test_invalid_k(self):
        with self.assertRaises(HeapError):
            HeapAlgorithms.kth_largest([1, 2], 3)

    def test_empty_median(self):
        with self.assertRaises(HeapError):
            RunningMedian().median()

    def test_reorganize(self):
        result = HeapAlgorithms.reorganize_string("aab")
        self.assertEqual(len(result), 3)
        self.assertNotEqual(result[0], result[1])
        self.assertNotEqual(result[1], result[2])

    def test_empty_reorganization(self):
        self.assertEqual(
            HeapAlgorithms.reorganize_string(""),
            ""
        )


if __name__ == "__main__":
    run_assessment()
    print("\nRunning unit tests...")
    unittest.main(argv=["heap_assessment.py"], exit=False)
