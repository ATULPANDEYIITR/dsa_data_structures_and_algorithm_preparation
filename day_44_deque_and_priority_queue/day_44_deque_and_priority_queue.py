#!/usr/bin/env python3
"""Deque and priority queue implementations using only the Python standard library.

Run with: python deque_priority_queue.py

The examples model a repository engineering team processing urgent incidents,
ordinary maintenance tasks, and scheduled work while retaining deque-based
operations at both ends of a worklist.
"""

from __future__ import annotations

import heapq
import itertools
import random
import threading
import unittest
from collections import deque
from dataclasses import dataclass, field
from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


class EmptyStructureError(IndexError):
    """Raised when an operation requires an element but none exists."""


class BoundedDeque(Generic[T]):
    """A deque with explicit capacity and nonblocking insertion semantics."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        self._items: deque[T] = deque()
        self.capacity = capacity

    def append(self, item: T) -> None:
        if len(self._items) >= self.capacity:
            raise OverflowError("Deque is full.")
        self._items.append(item)

    def appendleft(self, item: T) -> None:
        if len(self._items) >= self.capacity:
            raise OverflowError("Deque is full.")
        self._items.appendleft(item)

    def pop(self) -> T:
        if not self._items:
            raise EmptyStructureError("Cannot pop from an empty deque.")
        return self._items.pop()

    def popleft(self) -> T:
        if not self._items:
            raise EmptyStructureError("Cannot remove from an empty deque.")
        return self._items.popleft()

    def peek_front(self) -> T:
        if not self._items:
            raise EmptyStructureError("Deque is empty.")
        return self._items[0]

    def peek_back(self) -> T:
        if not self._items:
            raise EmptyStructureError("Deque is empty.")
        return self._items[-1]

    def snapshot(self) -> tuple[T, ...]:
        return tuple(self._items)

    def __len__(self) -> int:
        return len(self._items)


@dataclass(frozen=True)
class WorkItem:
    ticket: str
    title: str
    priority: int
    estimated_minutes: int

    def __post_init__(self) -> None:
        if not self.ticket.strip():
            raise ValueError("Ticket identifier cannot be empty.")
        if not self.title.strip():
            raise ValueError("Work title cannot be empty.")
        if self.priority < 0:
            raise ValueError("Priority must be non-negative.")
        if self.estimated_minutes <= 0:
            raise ValueError("Estimated duration must be positive.")


@dataclass(order=True)
class _HeapEntry:
    rank: int
    sequence: int
    item: WorkItem = field(compare=False)


class PriorityQueue(Generic[T]):
    """Stable min- or max-priority queue with lazy cancellation."""

    def __init__(self, *, highest_first: bool = False):
        self._heap: list[tuple[int, int, T]] = []
        self._sequence = itertools.count()
        self._active: dict[int, T] = {}
        self._highest_first = highest_first
        self._lock = threading.RLock()

    def put(self, item: T, priority: int) -> int:
        if not isinstance(priority, int):
            raise TypeError("Priority must be an integer.")
        with self._lock:
            sequence = next(self._sequence)
            rank = -priority if self._highest_first else priority
            self._active[sequence] = item
            heapq.heappush(self._heap, (rank, sequence, item))
            return sequence

    def cancel(self, sequence: int) -> bool:
        """Mark an item inactive; heap removal is deferred until it reaches the top."""
        with self._lock:
            if sequence not in self._active:
                return False
            del self._active[sequence]
            return True

    def _discard_cancelled(self) -> None:
        while self._heap and self._heap[0][1] not in self._active:
            heapq.heappop(self._heap)

    def get(self) -> T:
        with self._lock:
            self._discard_cancelled()
            if not self._heap:
                raise EmptyStructureError("Priority queue is empty.")
            _, sequence, item = heapq.heappop(self._heap)
            del self._active[sequence]
            return item

    def peek(self) -> T:
        with self._lock:
            self._discard_cancelled()
            if not self._heap:
                raise EmptyStructureError("Priority queue is empty.")
            return self._heap[0][2]

    def __len__(self) -> int:
        with self._lock:
            return len(self._active)

    def is_empty(self) -> bool:
        return len(self) == 0


class WorkScheduler:
    """Combines FIFO urgent intake, a min-heap, and a max-heap."""

    def __init__(self) -> None:
        self.urgent_intake: deque[WorkItem] = deque()
        self.min_queue: PriorityQueue[WorkItem] = PriorityQueue()
        self.max_queue: PriorityQueue[WorkItem] = PriorityQueue(
            highest_first=True
        )
        self._tickets: set[str] = set()

    def submit(self, item: WorkItem, *, urgent: bool = False) -> None:
        if item.ticket in self._tickets:
            raise ValueError(f"Duplicate ticket: {item.ticket}")
        self._tickets.add(item.ticket)
        if urgent:
            self.urgent_intake.appendleft(item)
        self.min_queue.put(item, item.priority)
        self.max_queue.put(item, item.priority)

    def take_urgent(self) -> WorkItem:
        if not self.urgent_intake:
            raise EmptyStructureError("No urgent intake items.")
        item = self.urgent_intake.popleft()
        self._tickets.remove(item.ticket)
        return item

    def next_lowest_priority_number(self) -> WorkItem:
        """Return the smallest numeric priority, such as the least urgent work."""
        item = self.min_queue.get()
        self._tickets.discard(item.ticket)
        return item

    def next_highest_priority_number(self) -> WorkItem:
        """Return the largest numeric priority, such as the most urgent work."""
        item = self.max_queue.get()
        self._tickets.discard(item.ticket)
        return item


def demonstrate_deque() -> None:
    print("\nDeque: operations at both ends")
    tasks = BoundedDeque[str](capacity=5)
    tasks.append("review documentation")
    tasks.append("run integration tests")
    tasks.appendleft("restore failed deployment")
    print("Front:", tasks.peek_front())
    print("Back:", tasks.peek_back())
    print("Current order:", tasks.snapshot())
    print("Removed from front:", tasks.popleft())
    print("Removed from back:", tasks.pop())
    print("Remaining:", tasks.snapshot())


def demonstrate_priority_queues() -> None:
    jobs = [
        WorkItem("OPS-101", "Investigate production outage", 9, 60),
        WorkItem("DEV-204", "Fix authentication defect", 7, 45),
        WorkItem("DOC-302", "Update deployment guide", 2, 20),
        WorkItem("SEC-110", "Patch vulnerable dependency", 10, 35),
        WorkItem("DEV-205", "Improve query performance", 5, 50),
    ]

    print("\nMin-priority queue: lowest numeric priority first")
    min_queue: PriorityQueue[WorkItem] = PriorityQueue()
    for job in jobs:
        min_queue.put(job, job.priority)
    while not min_queue.is_empty():
        job = min_queue.get()
        print(f"{job.priority:2} {job.ticket}: {job.title}")

    print("\nMax-priority queue: highest numeric priority first")
    max_queue: PriorityQueue[WorkItem] = PriorityQueue(highest_first=True)
    for job in jobs:
        max_queue.put(job, job.priority)
    while not max_queue.is_empty():
        job = max_queue.get()
        print(f"{job.priority:2} {job.ticket}: {job.title}")


def demonstrate_cancellation() -> None:
    print("\nLazy cancellation")
    queue: PriorityQueue[str] = PriorityQueue(highest_first=True)
    cancelled_id = queue.put("obsolete deployment", 8)
    queue.put("security patch", 10)
    queue.put("documentation update", 2)
    print("Cancelled:", queue.cancel(cancelled_id))
    while not queue.is_empty():
        print(queue.get())


def demonstrate_scheduler() -> None:
    print("\nWork intake")
    scheduler = WorkScheduler()
    scheduler.submit(
        WorkItem("INC-900", "Production outage", 10, 60), urgent=True
    )
    scheduler.submit(
        WorkItem("SEC-901", "Security patch", 9, 30), urgent=True
    )
    scheduler.submit(
        WorkItem("DOC-902", "Documentation", 1, 20)
    )
    print("Urgent intake:", scheduler.take_urgent().ticket)
    print("Next urgent intake:", scheduler.take_urgent().ticket)
    print(
        "Lowest numeric priority:",
        scheduler.next_lowest_priority_number().ticket,
    )
    print(
        "Highest numeric priority:",
        scheduler.next_highest_priority_number().ticket,
    )


class StructureTests(unittest.TestCase):
    def test_deque_end_operations(self) -> None:
        items = BoundedDeque[int](3)
        items.append(2)
        items.appendleft(1)
        items.append(3)
        self.assertEqual(items.snapshot(), (1, 2, 3))
        self.assertEqual(items.popleft(), 1)
        self.assertEqual(items.pop(), 3)

    def test_deque_capacity(self) -> None:
        items = BoundedDeque[int](1)
        items.append(1)
        with self.assertRaises(OverflowError):
            items.append(2)

    def test_empty_deque(self) -> None:
        with self.assertRaises(EmptyStructureError):
            BoundedDeque[int](2).popleft()

    def test_min_queue(self) -> None:
        queue: PriorityQueue[str] = PriorityQueue()
        queue.put("later", 5)
        queue.put("earlier", 1)
        self.assertEqual(queue.get(), "earlier")

    def test_max_queue(self) -> None:
        queue: PriorityQueue[str] = PriorityQueue(highest_first=True)
        queue.put("normal", 3)
        queue.put("critical", 10)
        self.assertEqual(queue.get(), "critical")

    def test_stable_ties(self) -> None:
        queue: PriorityQueue[str] = PriorityQueue()
        queue.put("first", 4)
        queue.put("second", 4)
        self.assertEqual(queue.get(), "first")
        self.assertEqual(queue.get(), "second")

    def test_cancellation(self) -> None:
        queue: PriorityQueue[str] = PriorityQueue()
        identifier = queue.put("cancelled", 1)
        queue.put("active", 2)
        self.assertTrue(queue.cancel(identifier))
        self.assertFalse(queue.cancel(identifier))
        self.assertEqual(queue.get(), "active")

    def test_work_validation(self) -> None:
        with self.assertRaises(ValueError):
            WorkItem("X", "Invalid priority", -1, 5)

    def test_duplicate_ticket(self) -> None:
        scheduler = WorkScheduler()
        item = WorkItem("X-1", "Task", 1, 5)
        scheduler.submit(item)
        with self.assertRaises(ValueError):
            scheduler.submit(item)

    def test_randomized_min_heap_order(self) -> None:
        generator = random.Random(42)
        values = [generator.randrange(0, 1000) for _ in range(250)]
        queue: PriorityQueue[int] = PriorityQueue()
        for value in values:
            queue.put(value, value)
        self.assertEqual(
            [queue.get() for _ in values],
            sorted(values),
        )


def main() -> None:
    demonstrate_deque()
    demonstrate_priority_queues()
    demonstrate_cancellation()
    demonstrate_scheduler()
    print("\nRun automated checks with: python deque_priority_queue.py --test")


if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        main()
