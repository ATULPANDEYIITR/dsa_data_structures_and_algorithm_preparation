"""
Day 10 — Best, Average and Worst Case
Data Structures and Algorithms Preparation

This standalone script studies time complexity through:
    1. Linear search
    2. Binary search
    3. Sorting algorithms
    4. Hash-table operations
    5. Array operations
    6. Linked-list operations

The script combines:
    - mathematical complexity analysis
    - executable algorithms
    - best/average/worst-case demonstrations
    - operation-cost comparisons
    - edge cases
    - empirical timing
    - a practical complexity reference sheet

No external packages are required.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


# ============================================================
# 1. COMPLEXITY FUNDAMENTALS
# ============================================================

def explain_complexity_basics() -> None:
    print("\n" + "=" * 80)
    print("1. COMPLEXITY FUNDAMENTALS")
    print("=" * 80)

    concepts = {
        "Input size n":
            "The amount of data an algorithm processes.",
        "Best case":
            "The most favorable valid input arrangement for the algorithm.",
        "Average case":
            "The expected cost over a defined distribution of inputs.",
        "Worst case":
            "The maximum cost among valid inputs of size n.",
        "Time complexity":
            "How the number of elementary operations grows as n grows.",
        "Space complexity":
            "How additional memory usage grows as n grows.",
        "Big O":
            "An asymptotic upper-bound notation commonly used for growth rate.",
        "Big Omega":
            "An asymptotic lower-bound notation.",
        "Big Theta":
            "A tight asymptotic bound when upper and lower growth match.",
    }

    for term, definition in concepts.items():
        print(f"{term:20} : {definition}")

    print("\nCommon growth rates:")
    growth_rates = [
        ("O(1)", "constant", "Does not grow with n"),
        ("O(log n)", "logarithmic", "Grows very slowly"),
        ("O(n)", "linear", "Roughly proportional to n"),
        ("O(n log n)", "linearithmic", "Typical of efficient comparison sorting"),
        ("O(n²)", "quadratic", "Often produced by nested loops"),
        ("O(n³)", "cubic", "Often produced by three nested loops"),
        ("O(2ⁿ)", "exponential", "Doubles approximately with each extra input"),
        ("O(n!)", "factorial", "Grows extremely rapidly"),
    ]

    for notation, name, description in growth_rates:
        print(f"{notation:8} | {name:15} | {description}")


def operation_count_examples() -> None:
    print("\n" + "=" * 80)
    print("2. OPERATION-COUNT EXAMPLES")
    print("=" * 80)

    n = 10

    constant_operations = 1
    linear_operations = n
    quadratic_operations = n * n
    cubic_operations = n * n * n

    print(f"For n = {n}:")
    print(f"O(1)       ≈ {constant_operations:,} unit")
    print(f"O(n)       ≈ {linear_operations:,} units")
    print(f"O(n²)      ≈ {quadratic_operations:,} units")
    print(f"O(n³)      ≈ {cubic_operations:,} units")

    print("\nImportant principle:")
    print("Asymptotic analysis focuses on growth rather than exact machine-level timing.")
    print("Constants and lower-order terms are usually ignored for large n.")


# ============================================================
# 3. LINEAR SEARCH
# ============================================================

def linear_search(data: list[Any], target: Any) -> int:
    """
    Search sequentially from the first element.

    Best case:
        O(1), when target is the first element.

    Average case:
        O(n), assuming the target is equally likely to occur
        at any position.

    Worst case:
        O(n), when target is last or absent.

    Space:
        O(1) auxiliary space.
    """
    for index, value in enumerate(data):
        if value == target:
            return index
    return -1


def demonstrate_linear_search() -> None:
    print("\n" + "=" * 80)
    print("3. LINEAR SEARCH")
    print("=" * 80)

    data = [10, 20, 30, 40, 50]

    print("Data:", data)

    best_target = 10
    average_target = 30
    worst_target = 50
    absent_target = 99

    for target in [best_target, average_target, worst_target, absent_target]:
        index = linear_search(data, target)
        print(f"Search {target:>2}: index = {index}")

    print("\nComplexity:")
    print("Best case   : O(1)")
    print("Average case: O(n)")
    print("Worst case  : O(n)")
    print("Space       : O(1)")

    print("\nImportant observation:")
    print("Linear search does not require sorted data.")

    print("\nEdge cases:")
    edge_cases = [
        [],
        [5],
        [5, 5, 5],
        [1, 2, 3],
    ]

    for case in edge_cases:
        target = case[0] if case else 5
        print(f"Data={case}, target={target}, result={linear_search(case, target)}")


# ============================================================
# 4. BINARY SEARCH
# ============================================================

def binary_search(data: list[Any], target: Any) -> int:
    """
    Iterative binary search.

    Requirement:
        data must be sorted in ascending order.

    Best case:
        O(1), when the middle element is the target.

    Average case:
        O(log n).

    Worst case:
        O(log n).

    Space:
        O(1) auxiliary space.
    """
    left = 0
    right = len(data) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if data[middle] == target:
            return middle

        if data[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    print("\n" + "=" * 80)
    print("4. BINARY SEARCH")
    print("=" * 80)

    data = [10, 20, 30, 40, 50, 60, 70]

    print("Sorted data:", data)

    for target in [40, 10, 70, 99]:
        print(
            f"Search {target:>2}: "
            f"index = {binary_search(data, target)}"
        )

    print("\nComplexity:")
    print("Best case   : O(1)")
    print("Average case: O(log n)")
    print("Worst case  : O(log n)")
    print("Space       : O(1) iterative")

    print("\nWhy O(log n)?")
    print("Each comparison eliminates approximately half of the remaining search space.")

    print("\nCritical requirement:")
    print("Binary search is valid only when the search range is ordered according to")
    print("the comparison rule being used.")

    unsorted_data = [40, 10, 70, 20, 60]
    print("\nUnsorted data:", unsorted_data)
    print(
        "Applying binary search directly to unsorted data is not valid:",
        binary_search(unsorted_data, 20),
    )


# ============================================================
# 5. BINARY SEARCH COMPARISON COUNT
# ============================================================

def binary_search_with_count(
    data: list[Any], target: Any
) -> tuple[int, int]:
    """Return (index, number_of_comparisons)."""
    left = 0
    right = len(data) - 1
    comparisons = 0

    while left <= right:
        middle = left + (right - left) // 2
        comparisons += 1

        if data[middle] == target:
            return middle, comparisons

        if data[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1, comparisons


def demonstrate_search_scaling() -> None:
    print("\n" + "=" * 80)
    print("5. LINEAR SEARCH VS BINARY SEARCH SCALING")
    print("=" * 80)

    print(f"{'n':>10} {'Linear worst comparisons':>28} {'Binary worst comparisons':>28}")

    for n in [10, 100, 1_000, 10_000, 100_000]:
        data = list(range(n))
        _, binary_comparisons = binary_search_with_count(data, -1)

        print(
            f"{n:>10,} "
            f"{n:>28,} "
            f"{binary_comparisons:>28,}"
        )

    print("\nBinary search saves comparisons by repeatedly halving the problem.")


# ============================================================
# 6. SORTING ALGORITHMS
# ============================================================

def bubble_sort(data: list[int]) -> list[int]:
    """
    Bubble sort with an early-exit optimization.

    Best:
        O(n) when already sorted.

    Average:
        O(n²).

    Worst:
        O(n²).

    Auxiliary space:
        O(1).

    Stable:
        Yes, when equal values are not swapped unnecessarily.
    """
    values = data.copy()

    for end in range(len(values) - 1, 0, -1):
        swapped = False

        for index in range(end):
            if values[index] > values[index + 1]:
                values[index], values[index + 1] = (
                    values[index + 1],
                    values[index],
                )
                swapped = True

        if not swapped:
            break

    return values


def selection_sort(data: list[int]) -> list[int]:
    """
    Selection sort.

    Best:
        O(n²)

    Average:
        O(n²)

    Worst:
        O(n²)

    Auxiliary space:
        O(1).

    Selection sort performs approximately the same number of comparisons
    regardless of input ordering.
    """
    values = data.copy()

    for position in range(len(values)):
        minimum_index = position

        for index in range(position + 1, len(values)):
            if values[index] < values[minimum_index]:
                minimum_index = index

        values[position], values[minimum_index] = (
            values[minimum_index],
            values[position],
        )

    return values


def insertion_sort(data: list[int]) -> list[int]:
    """
    Insertion sort.

    Best:
        O(n), especially when already sorted.

    Average:
        O(n²).

    Worst:
        O(n²), typically reverse-sorted input.

    Auxiliary space:
        O(1).

    Stable:
        Yes.
    """
    values = data.copy()

    for position in range(1, len(values)):
        current_value = values[position]
        previous = position - 1

        while previous >= 0 and values[previous] > current_value:
            values[previous + 1] = values[previous]
            previous -= 1

        values[previous + 1] = current_value

    return values


def merge_sort(data: list[int]) -> list[int]:
    """
    Merge sort.

    Best:
        O(n log n)

    Average:
        O(n log n)

    Worst:
        O(n log n)

    Auxiliary space:
        O(n) for this implementation.

    The input is recursively divided and then merged.
    """
    if len(data) <= 1:
        return data.copy()

    middle = len(data) // 2
    left = merge_sort(data[:middle])
    right = merge_sort(data[middle:])

    merged: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])

    return merged


def quick_sort(data: list[int]) -> list[int]:
    """
    Quicksort using a middle-value pivot.

    Average:
        O(n log n).

    Worst:
        O(n²) for unfavorable partition behavior.

    Auxiliary recursion:
        Depends on partition balance.

    This implementation is intentionally educational rather than
    optimized for production workloads.
    """
    if len(data) <= 1:
        return data.copy()

    pivot = data[len(data) // 2]

    smaller = [value for value in data if value < pivot]
    equal = [value for value in data if value == pivot]
    greater = [value for value in data if value > pivot]

    return quick_sort(smaller) + equal + quick_sort(greater)


def demonstrate_sorting() -> None:
    print("\n" + "=" * 80)
    print("6. SORTING ALGORITHMS")
    print("=" * 80)

    sample = [7, 2, 9, 1, 5, 2, 8]

    algorithms: list[tuple[str, Callable[[list[int]], list[int]]]] = [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
        ("Merge sort", merge_sort),
        ("Quicksort", quick_sort),
    ]

    print("Original:", sample)

    for name, algorithm in algorithms:
        print(f"{name:18}: {algorithm(sample)}")

    print("\nComplexity reference:")
    print(
        f"{'Algorithm':<18}"
        f"{'Best':<12}"
        f"{'Average':<12}"
        f"{'Worst':<12}"
        f"{'Extra space'}"
    )

    rows = [
        ("Bubble sort", "O(n)", "O(n²)", "O(n²)", "O(1)"),
        ("Selection sort", "O(n²)", "O(n²)", "O(n²)", "O(1)"),
        ("Insertion sort", "O(n)", "O(n²)", "O(n²)", "O(1)"),
        ("Merge sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)"),
        ("Quicksort", "O(n log n)", "O(n log n)", "O(n²)", "O(log n)*"),
    ]

    for row in rows:
        print(
            f"{row[0]:<18}"
            f"{row[1]:<12}"
            f"{row[2]:<12}"
            f"{row[3]:<12}"
            f"{row[4]}"
        )

    print("* Typical recursive auxiliary space for balanced partitions.")


# ============================================================
# 7. SORTING EDGE CASES
# ============================================================

def demonstrate_sorting_edge_cases() -> None:
    print("\n" + "=" * 80)
    print("7. SORTING EDGE CASES")
    print("=" * 80)

    cases = {
        "Empty": [],
        "One element": [42],
        "Already sorted": [1, 2, 3, 4, 5],
        "Reverse sorted": [5, 4, 3, 2, 1],
        "Duplicates": [3, 1, 3, 2, 1, 3],
        "Negative values": [-4, 2, -1, 7, 0],
    }

    for name, values in cases.items():
        print(f"\n{name}: {values}")
        print("Bubble   :", bubble_sort(values))
        print("Selection:", selection_sort(values))
        print("Insertion:", insertion_sort(values))
        print("Merge    :", merge_sort(values))
        print("Quick    :", quick_sort(values))


# ============================================================
# 8. HASH TABLE
# ============================================================

class SimpleHashTable:
    """
    Educational hash table using separate chaining.

    Average-case assumptions:
        O(1) insertion
        O(1) lookup
        O(1) deletion

    Worst case:
        O(n) when many keys collide into the same bucket.

    The quality of a hash table depends on:
        - hash function
        - bucket count
        - collision strategy
        - load factor
        - resizing policy
    """

    def __init__(self, bucket_count: int = 8) -> None:
        if bucket_count <= 0:
            raise ValueError("bucket_count must be positive")

        self._buckets: list[list[tuple[Any, Any]]] = [
            [] for _ in range(bucket_count)
        ]
        self._size = 0

    def _bucket_index(self, key: Any) -> int:
        return hash(key) % len(self._buckets)

    def put(self, key: Any, value: Any) -> None:
        bucket = self._buckets[self._bucket_index(key)]

        for index, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[index] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

    def get(self, key: Any) -> Any:
        bucket = self._buckets[self._bucket_index(key)]

        for existing_key, value in bucket:
            if existing_key == key:
                return value

        raise KeyError(key)

    def delete(self, key: Any) -> None:
        bucket = self._buckets[self._bucket_index(key)]

        for index, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                del bucket[index]
                self._size -= 1
                return

        raise KeyError(key)

    def contains(self, key: Any) -> bool:
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def __len__(self) -> int:
        return self._size

    def load_factor(self) -> float:
        return self._size / len(self._buckets)


def demonstrate_hash_tables() -> None:
    print("\n" + "=" * 80)
    print("8. HASH-TABLE OPERATIONS")
    print("=" * 80)

    table = SimpleHashTable()

    table.put("name", "Atul")
    table.put("language", "Python")
    table.put("topic", "Complexity")

    print("name:", table.get("name"))
    print("language:", table.get("language"))
    print("Contains topic:", table.contains("topic"))

    table.put("language", "C++")
    print("Updated language:", table.get("language"))

    table.delete("topic")
    print("Contains topic after deletion:", table.contains("topic"))

    print("\nHash-table complexity:")
    print("Insert average: O(1)")
    print("Lookup average: O(1)")
    print("Delete average: O(1)")
    print("Insert worst  : O(n)")
    print("Lookup worst  : O(n)")
    print("Delete worst  : O(n)")
    print("Space         : O(n)")

    print("\nLoad factor:", table.load_factor())

    print("\nImportant distinction:")
    print("O(1) hash-table operations are expected/average-case claims,")
    print("not guarantees that every individual operation always takes constant time.")


# ============================================================
# 9. ARRAY OPERATIONS
# ============================================================

def demonstrate_array_operations() -> None:
    print("\n" + "=" * 80)
    print("9. ARRAY OPERATIONS")
    print("=" * 80)

    values = [10, 20, 30, 40, 50]

    print("Original:", values)

    print("\nAccess by index:")
    print("values[2] =", values[2])
    print("Complexity: O(1)")

    print("\nUpdate by index:")
    values[2] = 35
    print(values)
    print("Complexity: O(1)")

    print("\nAppend:")
    values.append(60)
    print(values)
    print("Typical amortized complexity: O(1)")

    print("\nInsert at beginning:")
    values.insert(0, 5)
    print(values)
    print("Complexity: O(n), because existing elements shift.")

    print("\nDelete from beginning:")
    values.pop(0)
    print(values)
    print("Complexity: O(n), because existing elements shift.")

    print("\nDelete from end:")
    values.pop()
    print(values)
    print("Complexity: O(1) amortized in Python lists.")

    print("\nSearch:")
    print("30 in values:", 30 in values)
    print("Complexity: O(n)")

    print("\nArray/list reference table:")
    print("Index access       : O(1)")
    print("Index update       : O(1)")
    print("Append             : O(1) amortized")
    print("Pop from end       : O(1)")
    print("Insert at front    : O(n)")
    print("Delete from front  : O(n)")
    print("Unordered search   : O(n)")
    print("Sorting             : O(n log n) for efficient comparison sorts")


# ============================================================
# 10. AMORTIZED ARRAY BEHAVIOR
# ============================================================

def demonstrate_amortized_analysis() -> None:
    print("\n" + "=" * 80)
    print("10. AMORTIZED ANALYSIS")
    print("=" * 80)

    print(
        "Dynamic arrays occasionally resize. A single resize can cost O(n), "
        "but resizing is infrequent."
    )
    print(
        "Across a long sequence of append operations, the average cost per "
        "append is typically O(1) amortized."
    )

    values: list[int] = []
    previous_capacity = values.__sizeof__()

    print("\nPython list storage changes during growth:")
    print(f"{'Length':>10} {'Approx. storage':>18}")

    for value in range(50):
        values.append(value)
        current_capacity = values.__sizeof__()

        if current_capacity != previous_capacity:
            print(f"{len(values):>10} {current_capacity:>18}")
            previous_capacity = current_capacity


# ============================================================
# 11. LINKED LIST
# ============================================================

@dataclass
class LinkedNode:
    value: Any
    next: Optional["LinkedNode"] = None


class SinglyLinkedList:
    """
    Singly linked list.

    Head insertion:
        O(1)

    Tail insertion with a maintained tail pointer:
        O(1)

    Search:
        O(n)

    Access by position:
        O(n)

    Deletion after a known node:
        O(1)

    Deletion by value:
        O(n), because the predecessor must be found.

    Space:
        O(n).
    """

    def __init__(self) -> None:
        self.head: Optional[LinkedNode] = None
        self.tail: Optional[LinkedNode] = None
        self.size = 0

    def append(self, value: Any) -> None:
        node = LinkedNode(value)

        if self.head is None:
            self.head = self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            self.tail = node

        self.size += 1

    def prepend(self, value: Any) -> None:
        node = LinkedNode(value, self.head)
        self.head = node

        if self.tail is None:
            self.tail = node

        self.size += 1

    def find(self, value: Any) -> Optional[LinkedNode]:
        current = self.head

        while current is not None:
            if current.value == value:
                return current
            current = current.next

        return None

    def get_at(self, index: int) -> Any:
        if index < 0 or index >= self.size:
            raise IndexError("linked-list index out of range")

        current = self.head

        for _ in range(index):
            assert current is not None
            current = current.next

        assert current is not None
        return current.value

    def delete_value(self, value: Any) -> bool:
        previous: Optional[LinkedNode] = None
        current = self.head

        while current is not None:
            if current.value == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

                if current is self.tail:
                    self.tail = previous

                self.size -= 1

                if self.size == 0:
                    self.head = self.tail = None

                return True

            previous = current
            current = current.next

        return False

    def to_list(self) -> list[Any]:
        result: list[Any] = []
        current = self.head

        while current is not None:
            result.append(current.value)
            current = current.next

        return result


def demonstrate_linked_lists() -> None:
    print("\n" + "=" * 80)
    print("11. LINKED-LIST OPERATIONS")
    print("=" * 80)

    linked_list = SinglyLinkedList()

    linked_list.append(20)
    linked_list.append(30)
    linked_list.prepend(10)
    linked_list.append(40)

    print("List:", linked_list.to_list())
    print("Size:", linked_list.size)

    print("\nAccess index 2:", linked_list.get_at(2))
    print("Access complexity: O(n)")

    node = linked_list.find(30)
    print("Find 30:", node.value if node else None)
    print("Search complexity: O(n)")

    print("\nDelete 30:", linked_list.delete_value(30))
    print("List:", linked_list.to_list())

    print("\nLinked-list complexity:")
    print("Access by index       : O(n)")
    print("Search by value       : O(n)")
    print("Prepend               : O(1)")
    print("Append with tail      : O(1)")
    print("Delete by value       : O(n)")
    print("Delete after node     : O(1)")
    print("Space                 : O(n)")


# ============================================================
# 12. ARRAY VS LINKED LIST
# ============================================================

def compare_array_and_linked_list() -> None:
    print("\n" + "=" * 80)
    print("12. ARRAY VS LINKED LIST")
    print("=" * 80)

    rows = [
        ("Access by index", "O(1)", "O(n)"),
        ("Search", "O(n)", "O(n)"),
        ("Insert at beginning", "O(n)", "O(1)"),
        ("Delete at beginning", "O(n)", "O(1)"),
        ("Append", "O(1) amortized", "O(1) with tail"),
        ("Memory locality", "Usually strong", "Usually weaker"),
        ("Per-element overhead", "Low", "Higher"),
        ("Random access", "Excellent", "Poor"),
    ]

    print(f"{'Operation':<24}{'Dynamic array':<22}{'Linked list'}")
    for operation, array_cost, linked_cost in rows:
        print(f"{operation:<24}{array_cost:<22}{linked_cost}")


# ============================================================
# 13. BEST, AVERAGE, WORST INPUTS
# ============================================================

def classify_search_inputs() -> None:
    print("\n" + "=" * 80)
    print("13. BEST, AVERAGE AND WORST SEARCH INPUTS")
    print("=" * 80)

    data = list(range(1, 11))

    examples = [
        ("Linear best", linear_search, 1),
        ("Linear middle", linear_search, 5),
        ("Linear worst", linear_search, 10),
        ("Linear absent", linear_search, 999),
    ]

    for name, function, target in examples:
        print(f"{name:<20} -> index {function(data, target)}")

    print("\nFor binary search, the exact best-case position depends on the midpoint.")
    print("For this data set, 5 or 6 can be found immediately depending on midpoint convention.")
    print("Other values require additional halving steps.")


# ============================================================
# 14. HASH COLLISION DEMONSTRATION
# ============================================================

class DeliberatelyCollidingKey:
    """A key class used only to demonstrate hash collisions."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return 1

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DeliberatelyCollidingKey)
            and self.name == other.name
        )

    def __repr__(self) -> str:
        return f"Key({self.name!r})"


def demonstrate_hash_collisions() -> None:
    print("\n" + "=" * 80)
    print("14. HASH COLLISIONS")
    print("=" * 80)

    table = SimpleHashTable(bucket_count=4)

    keys = [DeliberatelyCollidingKey(str(i)) for i in range(5)]

    for index, key in enumerate(keys):
        table.put(key, index)

    print("Inserted keys:", keys)
    print("All keys deliberately map to the same hash value.")
    print("Separate chaining keeps them in the same bucket.")
    print("Lookup can therefore degrade toward O(n) in the bucket.")


# ============================================================
# 15. EMPIRICAL TIMING
# ============================================================

def benchmark(
    function: Callable[[list[int]], Any],
    data: list[int],
    repetitions: int = 3,
) -> float:
    """
    Return average execution time in seconds.

    Timing is affected by:
        - operating system scheduling
        - CPU state
        - interpreter/runtime overhead
        - memory behavior
        - background processes

    Therefore timing is useful evidence, but it is not a replacement
    for asymptotic analysis.
    """
    start = time.perf_counter()

    for _ in range(repetitions):
        function(data)

    elapsed = time.perf_counter() - start
    return elapsed / repetitions


def demonstrate_empirical_sorting() -> None:
    print("\n" + "=" * 80)
    print("15. EMPIRICAL SORTING TIMING")
    print("=" * 80)

    random.seed(42)

    sizes = [100, 500, 1_000]

    algorithms: list[
        tuple[str, Callable[[list[int]], list[int]]]
    ] = [
        ("Insertion sort", insertion_sort),
        ("Merge sort", merge_sort),
        ("Quicksort", quick_sort),
        ("Built-in sorted", sorted),
    ]

    for size in sizes:
        data = [random.randint(-10_000, 10_000) for _ in range(size)]

        print(f"\nInput size: {size}")

        for name, function in algorithms:
            repetitions = 1 if size >= 1_000 else 3
            elapsed = benchmark(function, data, repetitions)
            print(f"{name:<20}: {elapsed:.6f} seconds")

    print(
        "\nThe exact measurements vary by machine. "
        "The purpose is to observe growth patterns rather than establish "
        "universal benchmark numbers."
    )


# ============================================================
# 16. COMPLEXITY REFERENCE SHEET
# ============================================================

def complexity_reference_sheet() -> None:
    print("\n" + "=" * 80)
    print("16. PERSONAL COMPLEXITY REFERENCE SHEET")
    print("=" * 80)

    print(
        """
SEARCH
----------------------------------------------------------------------
Linear search
    Best       O(1)
    Average    O(n)
    Worst      O(n)
    Space      O(1)

Binary search
    Best       O(1)
    Average    O(log n)
    Worst      O(log n)
    Space      O(1) iterative
    Requirement: sorted/search-ordered data


SORTING
----------------------------------------------------------------------
Bubble sort
    Best       O(n) with early-exit optimization
    Average    O(n²)
    Worst      O(n²)
    Space      O(1)

Selection sort
    Best       O(n²)
    Average    O(n²)
    Worst      O(n²)
    Space      O(1)

Insertion sort
    Best       O(n)
    Average    O(n²)
    Worst      O(n²)
    Space      O(1)

Merge sort
    Best       O(n log n)
    Average    O(n log n)
    Worst      O(n log n)
    Space      O(n) for common array implementation

Quicksort
    Best       O(n log n)
    Average    O(n log n)
    Worst      O(n²)
    Extra space depends on recursion/partition strategy


HASH TABLE
----------------------------------------------------------------------
Insert       Average O(1), Worst O(n)
Lookup       Average O(1), Worst O(n)
Delete       Average O(1), Worst O(n)
Space        O(n)


DYNAMIC ARRAY
----------------------------------------------------------------------
Index access     O(1)
Index update     O(1)
Append           O(1) amortized
Delete at end    O(1)
Insert at front  O(n)
Delete at front  O(n)
Search           O(n)
Sorting          commonly O(n log n)


SINGLY LINKED LIST
----------------------------------------------------------------------
Access by index       O(n)
Search by value       O(n)
Prepend               O(1)
Append with tail      O(1)
Delete by value       O(n)
Delete after node     O(1)
Space                 O(n)


COMMON GROWTH ORDER
----------------------------------------------------------------------
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
O(n³)
O(2ⁿ)
O(n!)


KEY RULE
----------------------------------------------------------------------
Best case, average case and worst case describe different input
conditions. They are not three different algorithms.

An O(1) average operation may still have an O(n) worst case.
An O(n log n) worst-case algorithm may be preferable to an algorithm
with an unpredictable O(n²) worst case when predictable performance
matters.
"""
    )


# ============================================================
# 17. COMMON MISTAKES
# ============================================================

def common_mistakes() -> None:
    print("\n" + "=" * 80)
    print("17. COMMON COMPLEXITY-ANALYSIS MISTAKES")
    print("=" * 80)

    mistakes = [
        (
            "Calling every fast operation O(1)",
            "A fast operation may still grow with n."
        ),
        (
            "Assuming average case means the middle input",
            "Average case requires an input distribution or probability model."
        ),
        (
            "Using binary search on unsorted data",
            "Binary search depends on ordering."
        ),
        (
            "Calling hash-table lookup guaranteed O(1)",
            "Expected lookup is O(1), while pathological collisions can cause O(n)."
        ),
        (
            "Ignoring shifting in arrays",
            "Insertion or deletion away from the end can move many elements."
        ),
        (
            "Assuming linked lists are always faster",
            "They have poor random access and can have worse cache locality."
        ),
        (
            "Using benchmarks as the complexity proof",
            "Measurements are machine-dependent; asymptotic analysis describes growth."
        ),
        (
            "Ignoring auxiliary space",
            "An algorithm can have efficient time complexity but substantial memory usage."
        ),
    ]

    for mistake, correction in mistakes:
        print(f"\nMistake   : {mistake}")
        print(f"Correction: {correction}")


# ============================================================
# 18. PRACTICAL DECISION FRAMEWORK
# ============================================================

def decision_framework() -> None:
    print("\n" + "=" * 80)
    print("18. PRACTICAL DECISION FRAMEWORK")
    print("=" * 80)

    decisions = [
        (
            "Need to search an unsorted collection once?",
            "Linear search may be appropriate."
        ),
        (
            "Need repeated searches over ordered data?",
            "Binary search can reduce each search to O(log n)."
        ),
        (
            "Need fast key-based lookup?",
            "A hash table usually provides expected O(1) lookup."
        ),
        (
            "Need frequent random access?",
            "An array/dynamic array is usually appropriate."
        ),
        (
            "Need frequent insertion at the front?",
            "A linked structure can provide O(1) insertion."
        ),
        (
            "Need predictable O(n log n) comparison sorting?",
            "Merge sort provides that worst-case bound."
        ),
        (
            "Data is nearly sorted and small?",
            "Insertion sort can perform well because its best case is O(n)."
        ),
    ]

    for question, answer in decisions:
        print(f"\nQuestion: {question}")
        print(f"Analysis: {answer}")


# ============================================================
# 19. ASSERTION-BASED VERIFICATION
# ============================================================

def run_correctness_tests() -> None:
    print("\n" + "=" * 80)
    print("19. CORRECTNESS TESTS")
    print("=" * 80)

    test_data = [7, 2, 9, 1, 5, 2, 8, -1]

    expected_sorted = sorted(test_data)

    assert bubble_sort(test_data) == expected_sorted
    assert selection_sort(test_data) == expected_sorted
    assert insertion_sort(test_data) == expected_sorted
    assert merge_sort(test_data) == expected_sorted
    assert quick_sort(test_data) == expected_sorted

    assert linear_search([1, 2, 3], 1) == 0
    assert linear_search([1, 2, 3], 3) == 2
    assert linear_search([1, 2, 3], 99) == -1

    sorted_data = [1, 2, 3, 4, 5]
    assert binary_search(sorted_data, 1) == 0
    assert binary_search(sorted_data, 3) == 2
    assert binary_search(sorted_data, 5) == 4
    assert binary_search(sorted_data, 99) == -1

    linked_list = SinglyLinkedList()
    linked_list.append(10)
    linked_list.append(20)
    linked_list.prepend(5)

    assert linked_list.to_list() == [5, 10, 20]
    assert linked_list.get_at(1) == 10
    assert linked_list.delete_value(10)
    assert linked_list.to_list() == [5, 20]

    table = SimpleHashTable()
    table.put("a", 1)
    table.put("b", 2)
    assert table.get("a") == 1
    assert table.contains("b")
    table.delete("a")
    assert not table.contains("a")

    print("All correctness tests passed.")


# ============================================================
# 20. MAIN PROGRAM
# ============================================================

def main() -> None:
    print("=" * 80)
    print("DAY 10 — BEST, AVERAGE AND WORST CASE")
    print("=" * 80)

    explain_complexity_basics()
    operation_count_examples()
    demonstrate_linear_search()
    demonstrate_binary_search()
    demonstrate_search_scaling()
    demonstrate_sorting()
    demonstrate_sorting_edge_cases()
    demonstrate_hash_tables()
    demonstrate_array_operations()
    demonstrate_amortized_analysis()
    demonstrate_linked_lists()
    compare_array_and_linked_list()
    classify_search_inputs()
    demonstrate_hash_collisions()
    demonstrate_empirical_sorting()
    complexity_reference_sheet()
    common_mistakes()
    decision_framework()
    run_correctness_tests()

    print("\n" + "=" * 80)
    print("END OF DAY 10 STUDY SCRIPT")
    print("=" * 80)


if __name__ == "__main__":
    main()
