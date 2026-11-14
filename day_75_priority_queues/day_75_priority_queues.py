#!/usr/bin/env python3
"""
Priority Queues: Min-Heaps, Max-Heaps, Scheduling and Selection.

Features:
- Min-priority and max-priority queues.
- Stable ordering for equal priorities.
- Task scheduling and execution.
- Task cancellation and priority updates.
- Top-K selection.
- K-th largest and smallest elements.
- Running median using two heaps.
- Validation, exception handling and unit-style assertions.

Python 3.10+
"""

from __future__ import annotations

import heapq
import itertools
import random
import unittest
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Iterable, Optional, TypeVar


T = TypeVar("T")


class PriorityType(Enum):
    MIN = "min"
    MAX = "max"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    description: str
    priority: int
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0

    def __post_init__(self):
        if not self.task_id.strip():
            raise ValueError("Task ID cannot be empty")
        if not isinstance(self.priority, int):
            raise TypeError("Priority must be an integer")
        if not self.description.strip():
            raise ValueError("Description cannot be empty")


class PriorityQueue(Generic[T]):
    """Stable heap supporting both minimum and maximum priority."""

    def __init__(self, priority_type: PriorityType = PriorityType.MIN):
        self.priority_type = priority_type
        self._heap: list[tuple[int, int, T]] = []
        self._counter = itertools.count()

    def push(self, priority: int, item: T) -> None:
        if not isinstance(priority, int):
            raise TypeError("Priority must be an integer")

        effective_priority = (
            priority if self.priority_type == PriorityType.MIN
            else -priority
        )

        heapq.heappush(
            self._heap,
            (effective_priority, next(self._counter), item)
        )

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("Cannot remove from an empty priority queue")
        return heapq.heappop(self._heap)[2]

    def peek(self) -> T:
        if not self._heap:
            raise IndexError("Priority queue is empty")
        return self._heap[0][2]

    def is_empty(self) -> bool:
        return not self._heap

    def __len__(self) -> int:
        return len(self._heap)

    def clear(self) -> None:
        self._heap.clear()


class TaskScheduler:
    """
    Scheduler with lazy invalidation.

    A newer heap entry supersedes an older entry when a task's
    priority changes. Cancelled and superseded entries are skipped.
    """

    def __init__(self):
        self._heap: list[tuple[int, int, str, int]] = []
        self._tasks: dict[str, Task] = {}
        self._versions: dict[str, int] = {}
        self._sequence = itertools.count()

    def submit(self, task: Task) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"Duplicate task: {task.task_id}")

        self._tasks[task.task_id] = task
        self._versions[task.task_id] = 0
        self._enqueue(task)

    def _enqueue(self, task: Task) -> None:
        sequence = next(self._sequence)
        version = self._versions[task.task_id]

        # Higher priority values are processed first.
        heapq.heappush(
            self._heap,
            (-task.priority, sequence, task.task_id, version)
        )

    def update_priority(self, task_id: str, priority: int) -> None:
        task = self._tasks.get(task_id)

        if task is None:
            raise KeyError(f"Unknown task: {task_id}")

        if task.status != TaskStatus.PENDING:
            raise ValueError("Only pending tasks can be reprioritized")

        if not isinstance(priority, int):
            raise TypeError("Priority must be an integer")

        task.priority = priority
        self._versions[task_id] += 1
        self._enqueue(task)

    def cancel(self, task_id: str) -> None:
        task = self._tasks.get(task_id)

        if task is None:
            raise KeyError(f"Unknown task: {task_id}")

        if task.status != TaskStatus.PENDING:
            raise ValueError("Only pending tasks can be cancelled")

        task.status = TaskStatus.CANCELLED
        self._versions[task_id] += 1

    def next_task(self) -> Optional[Task]:
        while self._heap:
            _, _, task_id, version = heapq.heappop(self._heap)

            task = self._tasks[task_id]

            if version != self._versions[task_id]:
                continue

            if task.status != TaskStatus.PENDING:
                continue

            task.status = TaskStatus.RUNNING
            task.attempts += 1
            return task

        return None

    def complete(self, task_id: str, success: bool = True) -> None:
        task = self._tasks.get(task_id)

        if task is None:
            raise KeyError(task_id)

        if task.status != TaskStatus.RUNNING:
            raise ValueError("Task is not running")

        task.status = (
            TaskStatus.COMPLETED if success else TaskStatus.FAILED
        )

    def process_all(self) -> list[str]:
        execution_order = []

        while True:
            task = self.next_task()

            if task is None:
                break

            execution_order.append(task.task_id)
            self.complete(task.task_id)

        return execution_order

    def get_task(self, task_id: str) -> Task:
        return self._tasks[task_id]

    def report(self) -> dict[str, int]:
        result = {status.value: 0 for status in TaskStatus}

        for task in self._tasks.values():
            result[task.status.value] += 1

        return result


def top_k_largest(numbers: Iterable[int], k: int) -> list[int]:
    """Return the k largest values using an O(n log k) approach."""

    if k < 0:
        raise ValueError("k cannot be negative")

    if k == 0:
        return []

    heap = []

    for number in numbers:
        if len(heap) < k:
            heapq.heappush(heap, number)
        elif number > heap[0]:
            heapq.heapreplace(heap, number)

    return sorted(heap, reverse=True)


def kth_smallest(numbers: Iterable[int], k: int) -> int:
    """Find the k-th smallest element using a bounded max-heap."""

    if k <= 0:
        raise ValueError("k must be positive")

    heap = []

    for number in numbers:
        heapq.heappush(heap, -number)

        if len(heap) > k:
            heapq.heappop(heap)

    if len(heap) < k:
        raise ValueError("k exceeds the number of elements")

    return -heap[0]


class RunningMedian:
    """
    Maintain a running median with two heaps.

    lower: max-heap containing the smaller half.
    upper: min-heap containing the larger half.
    """

    def __init__(self):
        self.lower: list[int] = []
        self.upper: list[int] = []

    def add(self, number: int) -> None:
        if not isinstance(number, int):
            raise TypeError("Only integers are supported")

        if not self.lower or number <= -self.lower[0]:
            heapq.heappush(self.lower, -number)
        else:
            heapq.heappush(self.upper, number)

        if len(self.lower) > len(self.upper) + 1:
            heapq.heappush(
                self.upper, -heapq.heappop(self.lower)
            )
        elif len(self.upper) > len(self.lower):
            heapq.heappush(
                self.lower, -heapq.heappop(self.upper)
            )

    def median(self) -> float:
        if not self.lower:
            raise ValueError("Median is undefined for an empty collection")

        if len(self.lower) == len(self.upper):
            return (-self.lower[0] + self.upper[0]) / 2

        return float(-self.lower[0])


def demonstrate_basic_queues() -> None:
    print("\nMIN-PRIORITY QUEUE")

    minimum = PriorityQueue[int](PriorityType.MIN)

    for value in [40, 10, 30, 5, 20]:
        minimum.push(value, value)

    while not minimum.is_empty():
        print(minimum.pop(), end=" ")

    print("\n\nMAX-PRIORITY QUEUE")

    maximum = PriorityQueue[int](PriorityType.MAX)

    for value in [40, 10, 30, 5, 20]:
        maximum.push(value, value)

    while not maximum.is_empty():
        print(maximum.pop(), end=" ")

    print()


def demonstrate_scheduler() -> None:
    print("\nTASK SCHEDULER")

    scheduler = TaskScheduler()

    scheduler.submit(Task("T101", "Database backup", 3))
    scheduler.submit(Task("T102", "Security incident", 10))
    scheduler.submit(Task("T103", "Generate report", 2))
    scheduler.submit(Task("T104", "Deploy application", 7))

    scheduler.update_priority("T103", 8)
    scheduler.cancel("T101")

    print("Execution order:", scheduler.process_all())
    print("Task report:", scheduler.report())


def demonstrate_selection() -> None:
    numbers = [17, 4, 29, 11, 8, 35, 21, 3, 29]

    print("\nSELECTION OPERATIONS")
    print("Input:", numbers)
    print("Top 3:", top_k_largest(numbers, 3))
    print("Third smallest:", kth_smallest(numbers, 3))


def demonstrate_median() -> None:
    print("\nRUNNING MEDIAN")

    stream = [12, 4, 5, 3, 8, 7, 15, 20]
    tracker = RunningMedian()

    for number in stream:
        tracker.add(number)
        print(f"Inserted {number:2d}, median = {tracker.median()}")


class PriorityQueueTests(unittest.TestCase):

    def test_min_heap(self):
        queue = PriorityQueue[int]()
        for value in [8, 2, 5]:
            queue.push(value, value)
        self.assertEqual(
            [queue.pop(), queue.pop(), queue.pop()],
            [2, 5, 8]
        )

    def test_max_heap(self):
        queue = PriorityQueue[int](PriorityType.MAX)
        for value in [8, 2, 5]:
            queue.push(value, value)
        self.assertEqual(
            [queue.pop(), queue.pop(), queue.pop()],
            [8, 5, 2]
        )

    def test_top_k(self):
        self.assertEqual(
            top_k_largest([4, 9, 1, 7, 3], 2),
            [9, 7]
        )

    def test_kth_smallest(self):
        self.assertEqual(kth_smallest([5, 1, 3, 2], 2), 2)

    def test_running_median(self):
        tracker = RunningMedian()
        for value in [1, 3, 2, 4]:
            tracker.add(value)
        self.assertEqual(tracker.median(), 2.5)

    def test_priority_update(self):
        scheduler = TaskScheduler()
        scheduler.submit(Task("A", "Normal", 1))
        scheduler.submit(Task("B", "Urgent", 2))
        scheduler.update_priority("A", 5)

        self.assertEqual(scheduler.process_all(), ["A", "B"])

    def test_stable_order(self):
        scheduler = TaskScheduler()
        scheduler.submit(Task("A", "First", 5))
        scheduler.submit(Task("B", "Second", 5))
        self.assertEqual(scheduler.process_all(), ["A", "B"])

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            kth_smallest([1, 2], 3)

    def test_empty_queue(self):
        queue = PriorityQueue[int]()
        with self.assertRaises(IndexError):
            queue.pop()


def run_tests() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PriorityQueueTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        raise SystemExit(1)


def main() -> None:
    random.seed(42)

    demonstrate_basic_queues()
    demonstrate_scheduler()
    demonstrate_selection()
    demonstrate_median()

    print("\nUNIT TESTS")
    run_tests()


if __name__ == "__main__":
    main()
