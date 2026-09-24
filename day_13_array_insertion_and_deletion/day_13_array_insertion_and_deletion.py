"""
Day 13 — Array Insertion and Deletion

A comprehensive standalone study script covering:
- Insert at beginning
- Insert at end
- Insert at a position
- Delete from beginning
- Delete from end
- Delete by index
- Delete by value
- Element shifting
- Cost of shifting
- Dynamic arrays
- Bounds validation
- Duplicates
- Empty arrays
- Complexity analysis
- In-place mutation
- Stable deletion
- Unordered deletion
- Practical array-backed data structures
- Testing and performance measurement

The examples use Python lists because Python's list is a dynamic array:
contiguous storage is managed internally and the list automatically grows
when additional capacity is required.

For educational clarity, several operations are implemented manually rather
than relying entirely on list.insert() and list.pop().
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable, Optional


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL ARRAY OPERATIONS
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def display_array(values: list[int], label: str = "Array") -> None:
    """Display an array with indices."""
    print(f"{label}: {values}")
    if values:
        print("Index :", " ".join(f"{i:>4}" for i in range(len(values))))
        print("Value :", " ".join(f"{value:>4}" for value in values))
    else:
        print("The array is empty.")


# ---------------------------------------------------------------------------
# 2. INSERTION AT THE BEGINNING
# ---------------------------------------------------------------------------

def insert_at_beginning(values: list[int], value: int) -> None:
    """
    Insert a value at index 0.

    Every existing element must move one position to the right.

    Example:
        [10, 20, 30]
        insert 5
        [5, 10, 20, 30]

    Time complexity: O(n)
    Space complexity: O(1) auxiliary space for the conceptual operation.
    """
    values.append(0)

    # Shift from right to left so that no original value is overwritten.
    for index in range(len(values) - 1, 0, -1):
        values[index] = values[index - 1]

    values[0] = value


# ---------------------------------------------------------------------------
# 3. INSERTION AT THE END
# ---------------------------------------------------------------------------

def insert_at_end(values: list[int], value: int) -> None:
    """
    Insert a value at the end.

    Python's append() normally has amortized O(1) complexity because the
    dynamic array reserves extra capacity when necessary.
    """
    values.append(value)


# ---------------------------------------------------------------------------
# 4. INSERTION AT AN ARBITRARY POSITION
# ---------------------------------------------------------------------------

def insert_at_position(values: list[int], index: int, value: int) -> None:
    """
    Insert value before the current element at index.

    Valid insertion indices are 0 through len(values), inclusive.

    index == len(values) means insertion at the end.

    Time complexity:
        O(n) in the worst case because elements may need to shift.
    """
    if index < 0 or index > len(values):
        raise IndexError(
            f"Insertion index {index} is outside the valid range "
            f"0..{len(values)}."
        )

    values.append(0)

    # Move elements rightward, starting from the end.
    for current in range(len(values) - 1, index, -1):
        values[current] = values[current - 1]

    values[index] = value


# ---------------------------------------------------------------------------
# 5. DELETION FROM THE BEGINNING
# ---------------------------------------------------------------------------

def delete_from_beginning(values: list[int]) -> int:
    """
    Remove and return the first element.

    Every remaining element shifts one position to the left.

    Time complexity: O(n)
    """
    if not values:
        raise IndexError("Cannot delete from an empty array.")

    removed = values[0]

    for index in range(1, len(values)):
        values[index - 1] = values[index]

    values.pop()
    return removed


# ---------------------------------------------------------------------------
# 6. DELETION FROM THE END
# ---------------------------------------------------------------------------

def delete_from_end(values: list[int]) -> int:
    """
    Remove and return the final element.

    No remaining elements need to shift.

    Time complexity: O(1) amortized.
    """
    if not values:
        raise IndexError("Cannot delete from an empty array.")

    return values.pop()


# ---------------------------------------------------------------------------
# 7. DELETION BY INDEX
# ---------------------------------------------------------------------------

def delete_by_index(values: list[int], index: int) -> int:
    """
    Delete the element at a specific index.

    Elements after the deleted position shift left.

    Time complexity:
        O(n - index)
        O(n) worst case
        O(1) when deleting the final element
    """
    if index < 0 or index >= len(values):
        raise IndexError(
            f"Deletion index {index} is outside the valid range "
            f"0..{len(values) - 1}."
        )

    removed = values[index]

    for current in range(index + 1, len(values)):
        values[current - 1] = values[current]

    values.pop()
    return removed


# ---------------------------------------------------------------------------
# 8. DELETION BY VALUE
# ---------------------------------------------------------------------------

def delete_by_value(values: list[int], value: int) -> int:
    """
    Delete the first occurrence of value.

    Two operations are conceptually involved:
    1. Search for the value: O(n)
    2. Shift elements after it: O(n)

    Overall worst-case complexity: O(n).
    """
    for index, current_value in enumerate(values):
        if current_value == value:
            return delete_by_index(values, index)

    raise ValueError(f"Value {value} was not found.")


def delete_all_by_value(values: list[int], value: int) -> int:
    """
    Delete every occurrence of value while preserving the order of the
    remaining elements.

    This uses a write-pointer technique.

    Time complexity: O(n)
    Auxiliary space: O(1)
    """
    write_index = 0
    removed_count = 0

    for read_index in range(len(values)):
        if values[read_index] == value:
            removed_count += 1
        else:
            values[write_index] = values[read_index]
            write_index += 1

    del values[write_index:]
    return removed_count


# ---------------------------------------------------------------------------
# 9. SHIFTING ELEMENTS
# ---------------------------------------------------------------------------

def shift_right(values: list[int], positions: int = 1) -> None:
    """
    Shift array elements to the right by the requested number of positions.

    This implementation performs a circular shift so every original element
    remains represented.

    Example:
        [1, 2, 3, 4], shift right by 1
        [4, 1, 2, 3]

    Time complexity: O(n)
    """
    if not values:
        return

    positions %= len(values)

    if positions == 0:
        return

    values[:] = values[-positions:] + values[:-positions]


def shift_left(values: list[int], positions: int = 1) -> None:
    """
    Circularly shift elements to the left.

    Example:
        [1, 2, 3, 4], shift left by 1
        [2, 3, 4, 1]
    """
    if not values:
        return

    positions %= len(values)

    if positions == 0:
        return

    values[:] = values[positions:] + values[:positions]


def demonstrate_manual_shift() -> None:
    """
    Show why shifting direction matters during insertion.

    During right-shifting, the last element must be moved first.
    If we copied left-to-right, values would overwrite data that had not
    yet been moved.
    """
    values = [10, 20, 30, 40]
    print("Before insertion:", values)

    values.append(0)

    for index in range(len(values) - 1, 1, -1):
        values[index] = values[index - 1]

    values[1] = 15
    print("After inserting 15 at index 1:", values)


# ---------------------------------------------------------------------------
# 10. STABLE VERSUS UNORDERED DELETION
# ---------------------------------------------------------------------------

def delete_unordered(values: list[int], index: int) -> int:
    """
    Delete an element without preserving order.

    The final element replaces the deleted element.

    Example:
        [10, 20, 30, 40], delete index 1
        [10, 40, 30]

    This can be O(1), making it useful when element order is irrelevant.
    """
    if index < 0 or index >= len(values):
        raise IndexError("Index out of range.")

    removed = values[index]
    last_index = len(values) - 1

    if index != last_index:
        values[index] = values[last_index]

    values.pop()
    return removed


# ---------------------------------------------------------------------------
# 11. DYNAMIC ARRAY IMPLEMENTATION
# ---------------------------------------------------------------------------

class DynamicArray:
    """
    Educational dynamic-array implementation.

    It models the central behavior of an array that has:
    - logical size: number of elements currently stored
    - capacity: number of storage positions currently available

    When size reaches capacity, the implementation allocates a larger
    storage area and copies the existing elements.

    A geometric growth factor gives append() amortized O(1) complexity.
    """

    def __init__(self, initial_capacity: int = 4) -> None:
        if initial_capacity < 1:
            raise ValueError("Initial capacity must be at least 1.")

        self._data: list[Optional[int]] = [None] * initial_capacity
        self._size = 0

    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._data)

    def _resize(self, new_capacity: int) -> None:
        if new_capacity < self._size:
            raise ValueError("New capacity cannot be smaller than size.")

        new_data: list[Optional[int]] = [None] * new_capacity

        for index in range(self._size):
            new_data[index] = self._data[index]

        self._data = new_data

    def _ensure_capacity(self) -> None:
        if self._size == self.capacity:
            self._resize(max(1, self.capacity * 2))

    def append(self, value: int) -> None:
        self._ensure_capacity()
        self._data[self._size] = value
        self._size += 1

    def insert(self, index: int, value: int) -> None:
        if index < 0 or index > self._size:
            raise IndexError("Insertion index out of range.")

        self._ensure_capacity()

        for current in range(self._size, index, -1):
            self._data[current] = self._data[current - 1]

        self._data[index] = value
        self._size += 1

    def pop(self, index: Optional[int] = None) -> int:
        if self._size == 0:
            raise IndexError("Cannot pop from an empty dynamic array.")

        if index is None:
            index = self._size - 1

        if index < 0:
            index += self._size

        if index < 0 or index >= self._size:
            raise IndexError("Index out of range.")

        removed = self._data[index]

        for current in range(index + 1, self._size):
            self._data[current - 1] = self._data[current]

        self._size -= 1
        self._data[self._size] = None

        # Shrink only when the array is substantially under-utilized.
        # Shrinking after every deletion can cause repeated reallocations.
        if self._size > 0 and self._size <= self.capacity // 4:
            new_capacity = max(1, self.capacity // 2)
            if new_capacity >= self._size:
                self._resize(new_capacity)

        if removed is None:
            raise RuntimeError("Internal storage invariant was violated.")

        return removed

    def get(self, index: int) -> int:
        if index < 0:
            index += self._size

        if index < 0 or index >= self._size:
            raise IndexError("Index out of range.")

        value = self._data[index]

        if value is None:
            raise RuntimeError("Internal storage invariant was violated.")

        return value

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> int:
        return self.get(index)

    def __repr__(self) -> str:
        values = [self.get(index) for index in range(self._size)]
        return f"DynamicArray(size={self._size}, capacity={self.capacity}, data={values})"


# ---------------------------------------------------------------------------
# 12. SHIFT COUNT ANALYSIS
# ---------------------------------------------------------------------------

def insertion_shift_count(size: int, index: int) -> int:
    """Return the number of elements shifted during insertion."""
    if index < 0 or index > size:
        raise ValueError("Invalid insertion index.")
    return size - index


def deletion_shift_count(size: int, index: int) -> int:
    """Return the number of elements shifted during deletion."""
    if index < 0 or index >= size:
        raise ValueError("Invalid deletion index.")
    return size - index - 1


def show_shift_costs(size: int) -> None:
    print(f"\nArray size = {size}")
    print("Index | Insertion shifts | Deletion shifts")
    print("-" * 48)

    for index in range(size):
        insertion = insertion_shift_count(size, index)
        deletion = deletion_shift_count(size, index)
        print(f"{index:5d} | {insertion:16d} | {deletion:15d}")

    print(
        f"{size:5d} | {0:16d} | {'N/A':>15}  <- insertion at end"
    )


# ---------------------------------------------------------------------------
# 13. ERROR HANDLING AND EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    cases = [
        ("delete from empty", lambda: delete_from_end([])),
        ("delete invalid index", lambda: delete_by_index([1, 2], 5)),
        ("insert invalid index", lambda: insert_at_position([1, 2], 4, 9)),
        ("delete missing value", lambda: delete_by_value([1, 2], 99)),
    ]

    for description, operation in cases:
        try:
            operation()
        except (IndexError, ValueError) as error:
            print(f"{description}: handled safely -> {error}")


# ---------------------------------------------------------------------------
# 14. DUPLICATES
# ---------------------------------------------------------------------------

def demonstrate_duplicates() -> None:
    values = [5, 2, 5, 3, 5, 4]

    print("Original:", values)

    delete_by_value(values, 5)
    print("After deleting first 5:", values)

    count = delete_all_by_value(values, 5)
    print(f"After deleting remaining 5 values ({count} removed):", values)


# ---------------------------------------------------------------------------
# 15. COMPARING DELETION STRATEGIES
# ---------------------------------------------------------------------------

def demonstrate_deletion_strategies() -> None:
    ordered = [10, 20, 30, 40, 50]
    unordered = ordered.copy()

    delete_by_index(ordered, 1)
    delete_unordered(unordered, 1)

    print("Stable deletion:", ordered)
    print("Unordered deletion:", unordered)
    print(
        "Stable deletion preserves order; unordered deletion may be O(1) "
        "when removing by known index."
    )


# ---------------------------------------------------------------------------
# 16. SIMPLE ARRAY-BACKED QUEUE
# ---------------------------------------------------------------------------

class ArrayQueue:
    """
    A queue implemented using a dynamic array.

    The naive dequeue operation removes index 0 and therefore shifts all
    remaining elements. A production queue can avoid this cost using a
    circular buffer.
    """

    def __init__(self) -> None:
        self._items: list[int] = []

    def enqueue(self, value: int) -> None:
        self._items.append(value)

    def dequeue(self) -> int:
        if not self._items:
            raise IndexError("Queue is empty.")

        return delete_from_beginning(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"ArrayQueue({self._items})"


class CircularQueue:
    """
    Fixed-capacity circular queue.

    This demonstrates a design that avoids shifting elements during dequeue.
    """

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be positive.")

        self._data: list[Optional[int]] = [None] * capacity
        self._capacity = capacity
        self._front = 0
        self._size = 0

    def enqueue(self, value: int) -> None:
        if self._size == self._capacity:
            raise OverflowError("Circular queue is full.")

        position = (self._front + self._size) % self._capacity
        self._data[position] = value
        self._size += 1

    def dequeue(self) -> int:
        if self._size == 0:
            raise IndexError("Circular queue is empty.")

        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1

        if value is None:
            raise RuntimeError("Internal queue invariant was violated.")

        return value

    def __repr__(self) -> str:
        values = [
            self._data[(self._front + offset) % self._capacity]
            for offset in range(self._size)
        ]
        return f"CircularQueue({values})"


# ---------------------------------------------------------------------------
# 17. PERFORMANCE MEASUREMENT
# ---------------------------------------------------------------------------

def measure_operation(operation, repeat: int = 1_000) -> float:
    """
    Measure approximate execution time.

    This is educational rather than a rigorous benchmark. Operating-system
    scheduling, CPU frequency, Python implementation, and background work
    influence timing.
    """
    start = perf_counter()

    for _ in range(repeat):
        operation()

    return perf_counter() - start


def benchmark_insertions() -> None:
    """
    Compare insertion at the beginning and at the end.

    The exact numbers are machine-dependent. The important observation is
    the growth trend: beginning insertion requires shifting many elements,
    while append normally has amortized O(1) behavior.
    """
    size = 10_000

    beginning_time = measure_operation(
        lambda: insert_at_beginning(list(range(size)), -1),
        repeat=20,
    )

    ending_time = measure_operation(
        lambda: insert_at_end(list(range(size)), -1),
        repeat=20,
    )

    print(f"Beginning insertion benchmark: {beginning_time:.6f} seconds")
    print(f"End insertion benchmark:       {ending_time:.6f} seconds")
    print("Benchmark values vary between machines and Python implementations.")


# ---------------------------------------------------------------------------
# 18. TESTS
# ---------------------------------------------------------------------------

def run_tests() -> None:
    values = [10, 20, 30]

    insert_at_beginning(values, 5)
    assert values == [5, 10, 20, 30]

    insert_at_end(values, 40)
    assert values == [5, 10, 20, 30, 40]

    insert_at_position(values, 2, 15)
    assert values == [5, 10, 15, 20, 30, 40]

    assert delete_from_beginning(values) == 5
    assert values == [10, 15, 20, 30, 40]

    assert delete_from_end(values) == 40
    assert values == [10, 15, 20, 30]

    assert delete_by_index(values, 1) == 15
    assert values == [10, 20, 30]

    assert delete_by_value(values, 20) == 20
    assert values == [10, 30]

    values = [1, 2, 1, 3, 1]
    assert delete_all_by_value(values, 1) == 3
    assert values == [2, 3]

    values = [1, 2, 3, 4]
    shift_right(values)
    assert values == [4, 1, 2, 3]

    shift_left(values)
    assert values == [1, 2, 3, 4]

    values = [10, 20, 30]
    delete_unordered(values, 0)
    assert values == [30, 20]

    dynamic = DynamicArray()
    for value in range(10):
        dynamic.append(value)

    assert len(dynamic) == 10
    assert dynamic[0] == 0
    assert dynamic[-1] == 9

    dynamic.insert(5, 100)
    assert dynamic[5] == 100

    assert dynamic.pop(5) == 100
    assert len(dynamic) == 10

    queue = CircularQueue(3)
    queue.enqueue(10)
    queue.enqueue(20)
    assert queue.dequeue() == 10
    queue.enqueue(30)
    assert queue.dequeue() == 20
    assert queue.dequeue() == 30

    print("All tests passed.")


# ---------------------------------------------------------------------------
# 19. EDUCATIONAL DEMONSTRATION
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("DAY 13 — ARRAY INSERTION AND DELETION")

    print_section("Basic insertion operations")
    values = [10, 20, 30]
    display_array(values)

    insert_at_beginning(values, 5)
    display_array(values, "After inserting 5 at beginning")

    insert_at_end(values, 40)
    display_array(values, "After inserting 40 at end")

    insert_at_position(values, 2, 15)
    display_array(values, "After inserting 15 at index 2")

    print_section("Basic deletion operations")
    removed = delete_from_beginning(values)
    print("Removed from beginning:", removed)
    display_array(values)

    removed = delete_from_end(values)
    print("Removed from end:", removed)
    display_array(values)

    removed = delete_by_index(values, 1)
    print("Removed by index:", removed)
    display_array(values)

    values = [10, 20, 30, 20, 40]
    removed = delete_by_value(values, 20)
    print("Removed first value 20:", removed)
    display_array(values)

    print_section("Element shifting")
    demonstrate_manual_shift()

    values = [1, 2, 3, 4, 5]
    shift_right(values, 2)
    print("Circular right shift by 2:", values)

    shift_left(values, 3)
    print("Circular left shift by 3:", values)

    print_section("Shift cost")
    show_shift_costs(8)

    print_section("Duplicate values")
    demonstrate_duplicates()

    print_section("Stable versus unordered deletion")
    demonstrate_deletion_strategies()

    print_section("Edge cases and exceptions")
    demonstrate_edge_cases()

    print_section("Dynamic array")
    dynamic = DynamicArray(initial_capacity=2)

    for value in [10, 20, 30, 40]:
        dynamic.append(value)
        print(dynamic)

    dynamic.insert(2, 25)
    print("After insertion:", dynamic)

    removed = dynamic.pop(1)
    print("Removed:", removed)
    print(dynamic)

    print_section("Array-backed queue")
    queue = ArrayQueue()
    for value in [100, 200, 300]:
        queue.enqueue(value)

    print("Queue:", queue)
    print("Dequeued:", queue.dequeue())
    print("Queue after dequeue:", queue)

    print_section("Circular queue")
    circular = CircularQueue(4)

    for value in [1, 2, 3]:
        circular.enqueue(value)

    print(circular)
    print("Dequeued:", circular.dequeue())
    circular.enqueue(4)
    circular.enqueue(5)
    print("After wrap-around:", circular)

    print_section("Testing")
    run_tests()

    print_section("Performance experiment")
    benchmark_insertions()

    print_section("Complexity reference")
    print(
        """
Operation                         Typical complexity
----------------------------------------------------
Access by index                   O(1)
Insert at beginning              O(n)
Insert at middle                 O(n)
Insert at end                    O(1) amortized
Delete from beginning            O(n)
Delete from middle               O(n)
Delete from end                  O(1)
Delete by index                  O(n) worst case
Delete by value                  O(n)
Stable deletion                  O(n)
Unordered deletion by index      O(1)
Search in unsorted array         O(n)
"""
    )

    print(
        "Key principle: insertion or deletion near the beginning of an "
        "array is expensive because many elements must move."
    )


if __name__ == "__main__":
    main()
