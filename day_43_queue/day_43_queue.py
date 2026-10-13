"""
Queue: FIFO Data Structure
==========================

A queue follows First-In, First-Out (FIFO) ordering. The first element
inserted is the first element removed.

Core operations:
- Queue: Create and manage the collection.
- Enqueue: Add an element at the rear.
- Dequeue: Remove and return the front element.
- Front: Inspect the first element without removing it.
- Rear: Inspect the last element without removing it.

The implementation progresses from a simple queue to a circular buffer,
a linked queue, workload processing, and automated tests.

Run:
    python queue_implementation.py
"""

from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Deque, Generic, Iterable, Iterator, Optional, TypeVar
import unittest

T = TypeVar("T")


class QueueEmptyError(IndexError):
    """Raised when an operation requires an element from an empty queue."""


class QueueFullError(OverflowError):
    """Raised when a bounded queue has no remaining capacity."""


class Queue(Generic[T]):
    """A FIFO queue implemented with collections.deque."""

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._items: Deque[T] = deque(items or [])

    def enqueue(self, item: T) -> None:
        """Insert an item at the rear in O(1) amortized time."""
        self._items.append(item)

    def dequeue(self) -> T:
        """Remove and return the front item in O(1) time."""
        if not self._items:
            raise QueueEmptyError("Cannot dequeue from an empty queue.")
        return self._items.popleft()

    def front(self) -> T:
        """Return the front item without changing the queue."""
        if not self._items:
            raise QueueEmptyError("Cannot inspect the front of an empty queue.")
        return self._items[0]

    def rear(self) -> T:
        """Return the rear item without changing the queue."""
        if not self._items:
            raise QueueEmptyError("Cannot inspect the rear of an empty queue.")
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()

    def to_list(self) -> list[T]:
        """Return a snapshot, preventing callers from modifying internal state."""
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.to_list())

    def __repr__(self) -> str:
        return f"Queue({self.to_list()!r})"


class BoundedQueue(Generic[T]):
    """A FIFO queue that rejects insertions when its capacity is reached."""

    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("Capacity must be an integer.")
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        self._capacity = capacity
        self._items: Deque[T] = deque()

    @property
    def capacity(self) -> int:
        return self._capacity

    def enqueue(self, item: T) -> None:
        if len(self._items) >= self._capacity:
            raise QueueFullError("Queue capacity reached.")
        self._items.append(item)

    def dequeue(self) -> T:
        if not self._items:
            raise QueueEmptyError("Cannot dequeue from an empty queue.")
        return self._items.popleft()

    def front(self) -> T:
        if not self._items:
            raise QueueEmptyError("Queue is empty.")
        return self._items[0]

    def rear(self) -> T:
        if not self._items:
            raise QueueEmptyError("Queue is empty.")
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items

    def is_full(self) -> bool:
        return len(self._items) == self._capacity

    def size(self) -> int:
        return len(self._items)

    def to_list(self) -> list[T]:
        return list(self._items)


class CircularQueue(Generic[T]):
    """
    Fixed-capacity circular buffer.

    Head identifies the next item to remove. Tail identifies the next
    insertion position. Modular arithmetic reuses released array positions.
    An explicit size distinguishes empty and full states.
    """

    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("Capacity must be an integer.")
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")

        self._buffer: list[Optional[T]] = [None] * capacity
        self._capacity = capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def enqueue(self, item: T) -> None:
        if self._size == self._capacity:
            raise QueueFullError("Circular queue is full.")

        self._buffer[self._tail] = item
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1

    def dequeue(self) -> T:
        if self._size == 0:
            raise QueueEmptyError("Circular queue is empty.")

        item = self._buffer[self._head]
        self._buffer[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        return item  # type: ignore[return-value]

    def front(self) -> T:
        if self._size == 0:
            raise QueueEmptyError("Circular queue is empty.")
        return self._buffer[self._head]  # type: ignore[return-value]

    def rear(self) -> T:
        if self._size == 0:
            raise QueueEmptyError("Circular queue is empty.")
        index = (self._tail - 1) % self._capacity
        return self._buffer[index]  # type: ignore[return-value]

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == self._capacity

    def size(self) -> int:
        return self._size

    def to_list(self) -> list[T]:
        return [
            self._buffer[(self._head + offset) % self._capacity]
            for offset in range(self._size)
        ]  # type: ignore[list-item]


@dataclass
class Node(Generic[T]):
    value: T
    next: Optional["Node[T]"] = None


class LinkedQueue(Generic[T]):
    """
    Queue using singly linked nodes.

    Head points to the front; tail points to the rear. Both insertion
    and removal take O(1) time without shifting existing elements.
    """

    def __init__(self) -> None:
        self._head: Optional[Node[T]] = None
        self._tail: Optional[Node[T]] = None
        self._size = 0

    def enqueue(self, item: T) -> None:
        node = Node(item)

        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node

        self._size += 1

    def dequeue(self) -> T:
        if self._head is None:
            raise QueueEmptyError("Linked queue is empty.")

        item = self._head.value
        self._head = self._head.next
        self._size -= 1

        # Avoid retaining a stale tail after removing the final element.
        if self._head is None:
            self._tail = None

        return item

    def front(self) -> T:
        if self._head is None:
            raise QueueEmptyError("Linked queue is empty.")
        return self._head.value

    def rear(self) -> T:
        if self._tail is None:
            raise QueueEmptyError("Linked queue is empty.")
        return self._tail.value

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def to_list(self) -> list[T]:
        result: list[T] = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result


class ThreadSafeQueue(Generic[T]):
    """
    A queue whose individual operations are protected by a lock.

    The lock makes each public operation atomic relative to other calls
    using this instance. It does not make compound sequences of calls
    atomic as a group.
    """

    def __init__(self) -> None:
        self._items: Deque[T] = deque()
        self._lock = Lock()

    def enqueue(self, item: T) -> None:
        with self._lock:
            self._items.append(item)

    def dequeue(self) -> T:
        with self._lock:
            if not self._items:
                raise QueueEmptyError("Thread-safe queue is empty.")
            return self._items.popleft()

    def front(self) -> T:
        with self._lock:
            if not self._items:
                raise QueueEmptyError("Thread-safe queue is empty.")
            return self._items[0]

    def rear(self) -> T:
        with self._lock:
            if not self._items:
                raise QueueEmptyError("Thread-safe queue is empty.")
            return self._items[-1]

    def size(self) -> int:
        with self._lock:
            return len(self._items)


def process_support_tickets() -> None:
    """Model FIFO ticket processing for a technical support team."""
    tickets = Queue[dict[str, str]]()

    tickets.enqueue({
        "id": "INC-1042",
        "team": "Network Operations",
        "priority": "normal",
    })
    tickets.enqueue({
        "id": "INC-1043",
        "team": "Database Operations",
        "priority": "normal",
    })
    tickets.enqueue({
        "id": "INC-1044",
        "team": "Security Operations",
        "priority": "normal",
    })

    print("\nSupport ticket queue")
    print("Waiting:", [ticket["id"] for ticket in tickets])
    print("Next ticket:", tickets.front()["id"])
    print("Newest ticket:", tickets.rear()["id"])

    while tickets:
        ticket = tickets.dequeue()
        print(f"Processing {ticket['id']} for {ticket['team']}")

    print("All tickets processed:", tickets.is_empty())


def demonstrate_queue() -> None:
    print("Basic FIFO queue")
    queue = Queue[int]()

    for value in (10, 20, 30):
        queue.enqueue(value)

    print("Queue:", queue)
    print("Front:", queue.front())
    print("Rear:", queue.rear())
    print("Dequeued:", queue.dequeue())
    print("After dequeue:", queue.to_list())
    print("Size:", queue.size())

    print("\nBounded queue")
    bounded = BoundedQueue[str](2)
    bounded.enqueue("request-A")
    bounded.enqueue("request-B")
    print("Full:", bounded.is_full())
    try:
        bounded.enqueue("request-C")
    except QueueFullError as error:
        print("Rejected:", error)
    print("Removed:", bounded.dequeue())
    bounded.enqueue("request-C")
    print("Queue after reuse:", bounded.to_list())

    print("\nCircular queue")
    circular = CircularQueue[str](3)
    for item in ("job-A", "job-B", "job-C"):
        circular.enqueue(item)
    print("Initial order:", circular.to_list())
    print("Removed:", circular.dequeue())
    circular.enqueue("job-D")
    print("Order after wraparound:", circular.to_list())
    print("Front:", circular.front())
    print("Rear:", circular.rear())

    print("\nLinked queue")
    linked = LinkedQueue[str]()
    linked.enqueue("compile")
    linked.enqueue("test")
    linked.enqueue("deploy")
    print("Queue:", linked.to_list())
    print("Removed:", linked.dequeue())
    print("Front:", linked.front())
    print("Rear:", linked.rear())

    process_support_tickets()


class QueueTests(unittest.TestCase):
    def test_fifo_order(self) -> None:
        queue = Queue[int]()
        for item in (1, 2, 3):
            queue.enqueue(item)
        self.assertEqual([queue.dequeue(), queue.dequeue(), queue.dequeue()],
                         [1, 2, 3])

    def test_front_and_rear_do_not_remove_items(self) -> None:
        queue = Queue[str](["alpha", "beta", "gamma"])
        self.assertEqual(queue.front(), "alpha")
        self.assertEqual(queue.rear(), "gamma")
        self.assertEqual(queue.size(), 3)

    def test_empty_operations(self) -> None:
        queue = Queue[int]()
        for operation in (queue.dequeue, queue.front, queue.rear):
            with self.assertRaises(QueueEmptyError):
                operation()

    def test_bounded_capacity(self) -> None:
        queue = BoundedQueue[int](1)
        queue.enqueue(7)
        with self.assertRaises(QueueFullError):
            queue.enqueue(8)
        self.assertEqual(queue.dequeue(), 7)

    def test_circular_wraparound(self) -> None:
        queue = CircularQueue[int](3)
        queue.enqueue(1)
        queue.enqueue(2)
        queue.enqueue(3)
        self.assertEqual(queue.dequeue(), 1)
        queue.enqueue(4)
        self.assertEqual(queue.to_list(), [2, 3, 4])
        self.assertEqual(queue.rear(), 4)

    def test_linked_queue_resets_tail(self) -> None:
        queue = LinkedQueue[int]()
        queue.enqueue(1)
        self.assertEqual(queue.dequeue(), 1)
        self.assertTrue(queue.is_empty())
        queue.enqueue(2)
        self.assertEqual(queue.front(), 2)
        self.assertEqual(queue.rear(), 2)

    def test_snapshot_does_not_change_queue(self) -> None:
        queue = Queue[int]([1, 2])
        snapshot = queue.to_list()
        snapshot.append(3)
        self.assertEqual(queue.to_list(), [1, 2])


if __name__ == "__main__":
    demonstrate_queue()
    print("\nAutomated tests")
    unittest.main(argv=["queue_implementation.py"], exit=False, verbosity=2)
