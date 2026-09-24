"""
Day 9 — Logarithmic and Linearithmic Complexity

Topics covered:
- Binary search
- Divide-and-conquer
- Logarithmic growth
- Merge sort
- Heap operations
- O(log n) versus O(n)
- Recurrence relations
- Iterative and recursive algorithms
- Correctness conditions
- Edge cases
- Stability and in-place considerations
- Heap construction and heap sort
- Complexity analysis
- Practical performance measurements
- Testing and validation

This file is designed to be executable as a standalone study program.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log2
from random import Random
from time import perf_counter
from typing import Iterable, Optional


# ============================================================================
# 1. COMPLEXITY FUNDAMENTALS
# ============================================================================

def explain_growth():
    """
    Demonstrate why logarithmic growth is much slower than linear growth.

    A logarithm answers:
        "How many times can I divide n by a fixed base before reaching 1?"

    For binary algorithms, the base is usually 2.

    Examples:
        log2(8) = 3
        log2(16) = 4
        log2(1024) = 10
        log2(1_048_576) = 20
    """
    print("\n" + "=" * 78)
    print("1. LOGARITHMIC GROWTH")
    print("=" * 78)

    values = [1, 2, 4, 8, 16, 32, 64, 1_024, 1_000_000, 1_000_000_000]

    print(f"{'n':>15} {'log2(n)':>15} {'n':>15}")
    print("-" * 48)

    for n in values:
        logarithm = 0 if n == 1 else log2(n)
        print(f"{n:>15,} {logarithm:>15.2f} {n:>15,}")

    print(
        """
A logarithmic algorithm does not need to inspect every element.

If each operation cuts the remaining search space approximately in half:

    n -> n/2 -> n/4 -> n/8 -> ...

After k divisions:

    n / 2^k = 1

Therefore:

    2^k = n
    k = log2(n)

This is the mathematical reason binary search is O(log n).
"""
    )


def compare_logarithmic_and_linear(n: int):
    """Compare the number of conceptual operations for O(log n) and O(n)."""
    if n < 1:
        raise ValueError("n must be at least 1.")

    logarithmic_steps = 0 if n == 1 else int(log2(n)) + 1
    linear_steps = n

    print(f"\nFor n = {n:,}:")
    print(f"Approximate logarithmic steps: {logarithmic_steps:,}")
    print(f"Linear steps:                  {linear_steps:,}")
    print(f"Linear/logarithmic ratio:      {linear_steps / logarithmic_steps:,.2f}x")


# ============================================================================
# 2. LINEAR SEARCH
# ============================================================================

def linear_search(values: list[int], target: int) -> int:
    """
    Search every element from left to right.

    Best case:
        O(1), if target is the first element.

    Worst case:
        O(n), if target is absent or is the last element.

    Space:
        O(1).
    """
    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


# ============================================================================
# 3. BINARY SEARCH
# ============================================================================

def binary_search_iterative(values: list[int], target: int) -> int:
    """
    Iterative binary search.

    Important precondition:
        values must already be sorted in ascending order.

    At every iteration, approximately half of the remaining elements
    are eliminated.

    Time:
        Best case:  O(1)
        Average:    O(log n)
        Worst case: O(log n)

    Space:
        O(1)
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        # This calculation avoids integer overflow in languages where
        # integers have fixed ranges.
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            # Target must be to the right.
            left = middle + 1
        else:
            # Target must be to the left.
            right = middle - 1

    return -1


def binary_search_recursive(
    values: list[int],
    target: int,
    left: int = 0,
    right: Optional[int] = None,
) -> int:
    """
    Recursive binary search.

    Each recursive call works on roughly half the previous range.

    Time:
        O(log n)

    Auxiliary call-stack space:
        O(log n)

    The iterative version uses O(1) auxiliary space, so it is generally
    preferable when recursion provides no additional benefit.
    """
    if right is None:
        right = len(values) - 1

    if left > right:
        return -1

    middle = left + (right - left) // 2

    if values[middle] == target:
        return middle

    if values[middle] < target:
        return binary_search_recursive(values, target, middle + 1, right)

    return binary_search_recursive(values, target, left, middle - 1)


def first_occurrence_binary_search(values: list[int], target: int) -> int:
    """
    Find the first occurrence of target in a sorted list containing duplicates.

    Ordinary binary search can return any matching occurrence.
    This variation continues searching left after finding a match.

    Time: O(log n)
    Space: O(1)
    """
    left = 0
    right = len(values) - 1
    answer = -1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            answer = middle
            right = middle - 1
        elif values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return answer


def last_occurrence_binary_search(values: list[int], target: int) -> int:
    """Find the last occurrence of target in a sorted list in O(log n)."""
    left = 0
    right = len(values) - 1
    answer = -1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            answer = middle
            left = middle + 1
        elif values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return answer


def lower_bound(values: list[int], target: int) -> int:
    """
    Return the first index i for which values[i] >= target.

    If no such index exists, return len(values).

    This is a binary-search boundary problem.
    """
    left = 0
    right = len(values)

    while left < right:
        middle = left + (right - left) // 2

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle

    return left


def upper_bound(values: list[int], target: int) -> int:
    """
    Return the first index i for which values[i] > target.

    If no such index exists, return len(values).
    """
    left = 0
    right = len(values)

    while left < right:
        middle = left + (right - left) // 2

        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle

    return left


# ============================================================================
# 4. BINARY SEARCH ON A MONOTONIC CONDITION
# ============================================================================

def integer_square_root(number: int) -> int:
    """
    Find floor(sqrt(number)) using binary search.

    Example:
        sqrt(10) is approximately 3.162...
        floor(sqrt(10)) = 3

    We do not calculate the square root directly.

    Search space:
        [0, number]

    At each step, half the candidates are eliminated.

    Time: O(log n)
    Space: O(1)
    """
    if number < 0:
        raise ValueError("Square root is undefined for negative integers.")

    if number < 2:
        return number

    left = 1
    right = number
    answer = 1

    while left <= right:
        middle = left + (right - left) // 2

        if middle <= number // middle:
            answer = middle
            left = middle + 1
        else:
            right = middle - 1

    return answer


def minimum_capacity_for_shipping(weights: list[int], days: int) -> int:
    """
    Binary search the answer to a capacity problem.

    Given package weights in fixed order, find the minimum ship capacity
    that allows all packages to be shipped within a specified number of days.

    This is not searching for an element in an array.

    Instead, we search a numeric answer space.

    A capacity is feasible if it can ship everything within `days`.

    Complexity:
        O(n log S)

    where S is the range between the maximum package weight and
    the sum of all weights.
    """
    if not weights:
        raise ValueError("weights cannot be empty.")

    if days < 1:
        raise ValueError("days must be positive.")

    if any(weight <= 0 for weight in weights):
        raise ValueError("All weights must be positive.")

    if days > len(weights):
        # This is still possible because each package can be shipped
        # separately and unused days are harmless.
        days = len(weights)

    def feasible(capacity: int) -> bool:
        required_days = 1
        current_load = 0

        for weight in weights:
            if current_load + weight <= capacity:
                current_load += weight
            else:
                required_days += 1
                current_load = weight

        return required_days <= days

    left = max(weights)
    right = sum(weights)

    while left < right:
        middle = left + (right - left) // 2

        if feasible(middle):
            right = middle
        else:
            left = middle + 1

    return left


# ============================================================================
# 5. DIVIDE-AND-CONQUER
# ============================================================================

def divide_and_conquer_explanation():
    print("\n" + "=" * 78)
    print("5. DIVIDE-AND-CONQUER")
    print("=" * 78)

    print(
        """
Divide-and-conquer algorithms generally have three conceptual stages:

1. Divide
   Split a problem into smaller subproblems.

2. Conquer
   Solve the smaller problems, often recursively.

3. Combine
   Combine the smaller solutions into the solution to the original problem.

Binary search:
    Divide -> keep one half -> solve one half

Merge sort:
    Divide -> solve BOTH halves -> merge them

This difference is important.

Binary search:
    T(n) = T(n/2) + O(1)
    T(n) = O(log n)

Merge sort:
    T(n) = 2T(n/2) + O(n)
    T(n) = O(n log n)
"""
    )


def binary_search_recursion_trace(
    values: list[int],
    target: int,
    left: int,
    right: int,
    depth: int = 0,
) -> int:
    """Print recursive binary-search decisions for educational purposes."""
    if left > right:
        print("  " * depth + "empty range -> not found")
        return -1

    middle = left + (right - left) // 2

    print(
        "  " * depth
        + f"range=[{left}, {right}], middle={middle}, value={values[middle]}"
    )

    if values[middle] == target:
        print("  " * depth + "target found")
        return middle

    if values[middle] < target:
        return binary_search_recursion_trace(
            values, target, middle + 1, right, depth + 1
        )

    return binary_search_recursion_trace(
        values, target, left, middle - 1, depth + 1
    )


# ============================================================================
# 6. MERGE SORT
# ============================================================================

def merge(left: list[int], right: list[int]) -> list[int]:
    """
    Merge two sorted lists.

    Every element from both lists is processed once.

    Therefore:
        O(len(left) + len(right))
    """
    result: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            # <= preserves stability when equal values occur.
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result


def merge_sort(values: list[int]) -> list[int]:
    """
    Recursive merge sort.

    Base case:
        A list containing zero or one element is already sorted.

    Divide:
        Split the list into two halves.

    Conquer:
        Recursively sort both halves.

    Combine:
        Merge the two sorted halves.

    Recurrence:
        T(n) = 2T(n/2) + O(n)

    Therefore:
        Time = O(n log n)
        Auxiliary space = O(n)

    Merge sort is stable when the merge operation takes the left element
    first when values are equal.
    """
    if len(values) <= 1:
        return values.copy()

    middle = len(values) // 2

    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    return merge(left, right)


@dataclass(frozen=True)
class Student:
    """Small record used to demonstrate stable sorting."""

    name: str
    score: int


def merge_students(left: list[Student], right: list[Student]) -> list[Student]:
    """Stable merge based on score."""
    result: list[Student] = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i].score <= right[j].score:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def stable_student_merge_sort(students: list[Student]) -> list[Student]:
    """Stable merge sort for Student records."""
    if len(students) <= 1:
        return students.copy()

    middle = len(students) // 2
    left = stable_student_merge_sort(students[:middle])
    right = stable_student_merge_sort(students[middle:])

    return merge_students(left, right)


# ============================================================================
# 7. BOTTOM-UP MERGE SORT
# ============================================================================

def bottom_up_merge_sort(values: list[int]) -> list[int]:
    """
    Iterative merge sort.

    Instead of recursively dividing the list, start with sorted runs of
    size 1, then merge runs of size 2, then 4, then 8, and so on.

    Time: O(n log n)
    Auxiliary space: O(n)

    This removes recursive function calls while preserving merge sort's
    asymptotic complexity.
    """
    result = values.copy()
    n = len(result)
    width = 1

    while width < n:
        for start in range(0, n, 2 * width):
            middle = min(start + width, n)
            end = min(start + 2 * width, n)

            left = result[start:middle]
            right = result[middle:end]

            result[start:end] = merge(left, right)

        width *= 2

    return result


# ============================================================================
# 8. HEAPS
# ============================================================================

class MaxHeap:
    """
    Array-based max heap.

    Heap property:
        Every parent is greater than or equal to its children.

    For zero-based indexing:

        parent(i) = (i - 1) // 2
        left(i)   = 2*i + 1
        right(i)  = 2*i + 2

    Important operations:

        peek_max:       O(1)
        insert:         O(log n)
        extract_max:    O(log n)
        heapify_down:   O(log n)
        build heap:     O(n)

    The O(n) build-heap result is subtle and important:
    not every node requires O(log n) work.
    Most nodes are near the bottom and move only a small distance.
    """

    def __init__(self, values: Optional[Iterable[int]] = None):
        self.data: list[int] = []

        if values is not None:
            self.data = list(values)
            self._build_heap()

    @staticmethod
    def parent(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def left_child(index: int) -> int:
        return 2 * index + 1

    @staticmethod
    def right_child(index: int) -> int:
        return 2 * index + 2

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_index = self.parent(index)

            if self.data[parent_index] >= self.data[index]:
                break

            self.data[parent_index], self.data[index] = (
                self.data[index],
                self.data[parent_index],
            )

            index = parent_index

    def _sift_down(self, index: int) -> None:
        size = len(self.data)

        while True:
            largest = index
            left = self.left_child(index)
            right = self.right_child(index)

            if left < size and self.data[left] > self.data[largest]:
                largest = left

            if right < size and self.data[right] > self.data[largest]:
                largest = right

            if largest == index:
                break

            self.data[index], self.data[largest] = (
                self.data[largest],
                self.data[index],
            )

            index = largest

    def _build_heap(self) -> None:
        # Every leaf is already a valid heap.
        # Only internal nodes need heapify-down.
        first_parent = (len(self.data) // 2) - 1

        for index in range(first_parent, -1, -1):
            self._sift_down(index)

    def insert(self, value: int) -> None:
        self.data.append(value)
        self._sift_up(len(self.data) - 1)

    def peek_max(self) -> int:
        if not self.data:
            raise IndexError("Cannot peek an empty heap.")

        return self.data[0]

    def extract_max(self) -> int:
        if not self.data:
            raise IndexError("Cannot extract from an empty heap.")

        maximum = self.data[0]
        last = self.data.pop()

        if self.data:
            self.data[0] = last
            self._sift_down(0)

        return maximum

    def is_valid(self) -> bool:
        """Verify the heap property in O(n)."""
        for child in range(1, len(self.data)):
            parent = self.parent(child)

            if self.data[parent] < self.data[child]:
                return False

        return True

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"MaxHeap({self.data})"


def heap_sort(values: list[int]) -> list[int]:
    """
    Sort values using a max heap.

    Build heap:
        O(n)

    n extractions:
        O(n log n)

    Total:
        O(n log n)

    This implementation returns a new sorted list.
    """
    heap = MaxHeap(values)
    result = []

    while heap:
        result.append(heap.extract_max())

    result.reverse()
    return result


# ============================================================================
# 9. HEAPIFY AND BUILD-HEAP COMPLEXITY
# ============================================================================

def demonstrate_heap_structure(values: list[int]) -> None:
    """Display parent-child relationships of a heap."""
    heap = MaxHeap(values)

    print("\nHeap input:", values)
    print("Max heap:  ", heap.data)
    print("Valid heap:", heap.is_valid())

    for index, value in enumerate(heap.data):
        left = 2 * index + 1
        right = 2 * index + 2

        children = []

        if left < len(heap.data):
            children.append(heap.data[left])

        if right < len(heap.data):
            children.append(heap.data[right])

        print(f"node={value:>3} children={children}")


# ============================================================================
# 10. COMPLEXITY TABLE
# ============================================================================

def print_complexity_table():
    print("\n" + "=" * 78)
    print("10. COMPLEXITY COMPARISON")
    print("=" * 78)

    rows = [
        ("Array indexing", "O(1)", "O(1)", "Direct address calculation"),
        ("Linear search", "O(1)", "O(n)", "May inspect every element"),
        ("Binary search", "O(1)", "O(log n)", "Halves sorted search space"),
        ("Merge sort", "O(n log n)", "O(n log n)", "Two recursive halves + merge"),
        ("Heap peek", "O(1)", "O(1)", "Maximum/minimum is at root"),
        ("Heap insert", "O(1)", "O(log n)", "Element may rise to root"),
        ("Heap extraction", "O(log n)", "O(log n)", "Root replaced and sifted down"),
        ("Build heap", "O(n)", "O(n)", "Bottom-up heap construction"),
        ("Heap sort", "O(n log n)", "O(n log n)", "Repeated extraction"),
    ]

    print(
        f"{'Operation':<22} {'Best':<15} {'Worst':<15} {'Reason'}"
    )
    print("-" * 78)

    for operation, best, worst, reason in rows:
        print(f"{operation:<22} {best:<15} {worst:<15} {reason}")


# ============================================================================
# 11. EDGE CASES
# ============================================================================

def test_edge_cases():
    print("\n" + "=" * 78)
    print("11. EDGE CASES")
    print("=" * 78)

    cases = [
        [],
        [1],
        [1, 2],
        [2, 1],
        [5, 5, 5, 5],
        [-10, -5, 0, 5, 10],
    ]

    for values in cases:
        sorted_values = sorted(values)

        print(f"\nInput: {values}")
        print(f"Sorted: {merge_sort(values)}")

        if sorted_values:
            target = sorted_values[0]
            print(
                f"Binary search for {target}: "
                f"{binary_search_iterative(sorted_values, target)}"
            )
        else:
            print("Binary search skipped because the list is empty.")

        heap = MaxHeap(values)
        print(f"Heap: {heap.data}")
        print(f"Heap valid: {heap.is_valid()}")


# ============================================================================
# 12. TESTING
# ============================================================================

def run_correctness_tests():
    print("\n" + "=" * 78)
    print("12. CORRECTNESS TESTS")
    print("=" * 78)

    random_generator = Random(42)

    for size in range(0, 101):
        values = [
            random_generator.randint(-1_000, 1_000)
            for _ in range(size)
        ]

        expected = sorted(values)

        assert merge_sort(values) == expected
        assert bottom_up_merge_sort(values) == expected
        assert heap_sort(values) == expected

        heap = MaxHeap(values)
        assert heap.is_valid()

        extracted = []
        while heap:
            extracted.append(heap.extract_max())

        assert extracted == sorted(values, reverse=True)

    for values in [
        [],
        [1],
        [1, 2, 3],
        [3, 2, 1],
        [1, 1, 1],
        [-5, 0, 5],
    ]:
        sorted_values = sorted(values)

        for target in range(-6, 7):
            expected_index = (
                sorted_values.index(target)
                if target in sorted_values
                else -1
            )

            actual_index = binary_search_iterative(sorted_values, target)

            if expected_index == -1:
                assert actual_index == -1
            else:
                assert sorted_values[actual_index] == target

    print("All algorithmic correctness tests passed.")


# ============================================================================
# 13. STABILITY DEMONSTRATION
# ============================================================================

def demonstrate_stability():
    print("\n" + "=" * 78)
    print("13. MERGE SORT STABILITY")
    print("=" * 78)

    students = [
        Student("Asha", 80),
        Student("Ravi", 70),
        Student("Neha", 80),
        Student("Vikram", 70),
        Student("Sara", 90),
    ]

    sorted_students = stable_student_merge_sort(students)

    print("Original:")
    for student in students:
        print(f"  {student.name}: {student.score}")

    print("\nSorted by score:")
    for student in sorted_students:
        print(f"  {student.name}: {student.score}")

    print(
        "\nFor equal scores, the original relative order is preserved:"
        " Ravi remains before Vikram and Asha remains before Neha."
    )


# ============================================================================
# 14. PERFORMANCE MEASUREMENT
# ============================================================================

def measure_performance():
    print("\n" + "=" * 78)
    print("14. PRACTICAL PERFORMANCE MEASUREMENT")
    print("=" * 78)

    random_generator = Random(7)

    sizes = [1_000, 10_000, 100_000]

    for size in sizes:
        values = [
            random_generator.randint(0, size * 10)
            for _ in range(size)
        ]

        target = values[-1]

        sorted_values = sorted(values)

        start = perf_counter()
        linear_search(values, target)
        linear_time = perf_counter() - start

        start = perf_counter()
        binary_search_iterative(sorted_values, target)
        binary_time = perf_counter() - start

        start = perf_counter()
        merge_sort(values)
        merge_time = perf_counter() - start

        print(f"\nn = {size:,}")
        print(f"Linear search: {linear_time:.8f} seconds")
        print(f"Binary search: {binary_time:.8f} seconds")
        print(f"Merge sort:    {merge_time:.8f} seconds")

    print(
        """
Benchmark results vary by hardware, interpreter, cache behavior,
implementation details, and input distribution.

Big-O notation describes asymptotic growth. It does not guarantee that
one implementation is faster for every small input.

For example, a theoretically O(log n) operation may have larger constant
overhead than a simple O(n) operation for a tiny data set.
"""
    )


# ============================================================================
# 15. RECURSION DEPTH AND PRACTICAL DESIGN
# ============================================================================

def recursion_depth_demo():
    print("\n" + "=" * 78)
    print("15. RECURSION DEPTH")
    print("=" * 78)

    values = list(range(1, 33))

    print("Tracing recursive binary search for target 29:")
    binary_search_recursion_trace(
        values,
        29,
        0,
        len(values) - 1,
    )

    print(
        """
Binary search recursion depth is O(log n), which is small for practical
input sizes. Nevertheless, the iterative version avoids recursion-stack
usage entirely.

Merge sort has O(log n) recursive depth but performs O(n) auxiliary work
for merging.
"""
    )


# ============================================================================
# 16. COMMON MISTAKES
# ============================================================================

def common_mistakes():
    print("\n" + "=" * 78)
    print("16. COMMON MISTAKES")
    print("=" * 78)

    mistakes = [
        (
            "Using binary search on unsorted data",
            "Binary search relies on ordering. Sort first or use another method.",
        ),
        (
            "Using middle = (left + right) // 2 in fixed-width languages",
            "For very large indices this can overflow. Use left + (right-left)//2.",
        ),
        (
            "Forgetting to shrink the interval",
            "Use middle + 1 or middle - 1 after checking middle.",
        ),
        (
            "Assuming binary search always returns the first duplicate",
            "Ordinary binary search may return any matching position.",
        ),
        (
            "Calling merge sort O(log n)",
            "The recursive depth is logarithmic, but every level processes O(n).",
        ),
        (
            "Assuming build-heap is O(n log n)",
            "Bottom-up construction is O(n), even though individual sift-downs can be O(log n).",
        ),
        (
            "Ignoring the sorted-data requirement",
            "The correctness of binary search depends on a monotonic ordering.",
        ),
    ]

    for mistake, correction in mistakes:
        print(f"\nMistake:    {mistake}")
        print(f"Correction: {correction}")


# ============================================================================
# 17. ADVANCED RELATIONSHIPS
# ============================================================================

def advanced_complexity_relationships():
    print("\n" + "=" * 78)
    print("17. ADVANCED COMPLEXITY RELATIONSHIPS")
    print("=" * 78)

    print(
        """
Common recurrence patterns:

1. T(n) = T(n/2) + O(1)
   Result: O(log n)

   Example:
       Binary search

2. T(n) = 2T(n/2) + O(n)
   Result: O(n log n)

   Example:
       Merge sort

3. T(n) = 2T(n/2) + O(1)
   Result: O(n)

   The number of subproblems doubles while their depth decreases.

4. T(n) = T(n-1) + O(1)
   Result: O(n)

   Example:
       A simple recursive traversal that reduces input by one.

The key question is not simply:
    "Does this algorithm use recursion?"

Instead ask:
    - How many subproblems are created?
    - How large is each subproblem?
    - How much work occurs outside recursion?
    - How many levels are there?
"""
    )


# ============================================================================
# 18. APPLICATIONS
# ============================================================================

def real_world_applications():
    print("\n" + "=" * 78)
    print("18. REAL-WORLD APPLICATIONS")
    print("=" * 78)

    applications = {
        "Binary search": [
            "Searching sorted records",
            "Finding insertion boundaries",
            "Database/index-style lookup concepts",
            "Searching monotonic answer spaces",
            "Configuration and threshold problems",
        ],
        "Merge sort": [
            "External sorting",
            "Large data processing",
            "Stable sorting requirements",
            "Linked-list sorting",
            "Divide-and-conquer data processing",
        ],
        "Heaps": [
            "Priority queues",
            "Task scheduling",
            "Top-k problems",
            "Event simulation",
            "Graph algorithms such as Dijkstra's algorithm",
        ],
    }

    for algorithm, uses in applications.items():
        print(f"\n{algorithm}:")
        for use in uses:
            print(f"  - {use}")


# ============================================================================
# 19. MAIN STUDY PROGRAM
# ============================================================================

def main():
    print("=" * 78)
    print("DAY 9 — LOGARITHMIC AND LINEARITHMIC COMPLEXITY")
    print("=" * 78)

    explain_growth()

    compare_logarithmic_and_linear(1_000)
    compare_logarithmic_and_linear(1_000_000)
    compare_logarithmic_and_linear(1_000_000_000)

    print("\n" + "=" * 78)
    print("2. LINEAR SEARCH VS BINARY SEARCH")
    print("=" * 78)

    data = list(range(0, 100, 2))
    target = 74

    print("Data:", data)
    print("Target:", target)
    print("Linear search index:", linear_search(data, target))
    print("Binary search index:", binary_search_iterative(data, target))
    print("Recursive binary search index:",
          binary_search_recursive(data, target))

    duplicates = [1, 2, 2, 2, 3, 4, 4, 5]

    print("\nDuplicate data:", duplicates)
    print("First 2:", first_occurrence_binary_search(duplicates, 2))
    print("Last 2:", last_occurrence_binary_search(duplicates, 2))
    print("Lower bound of 3:", lower_bound(duplicates, 3))
    print("Upper bound of 3:", upper_bound(duplicates, 3))

    divide_and_conquer_explanation()

    print("\nInteger square root:")
    for number in [0, 1, 2, 8, 9, 10, 100, 999]:
        print(f"floor(sqrt({number})) = {integer_square_root(number)}")

    weights = [1, 2, 3, 4, 5, 6, 7]
    days = 3

    print(
        "\nMinimum shipping capacity:",
        minimum_capacity_for_shipping(weights, days),
    )

    print("\nMerge sort:")
    unsorted_values = [38, 27, 43, 3, 9, 82, 10]
    print("Input:", unsorted_values)
    print("Output:", merge_sort(unsorted_values))

    print("\nBottom-up merge sort:")
    print("Output:", bottom_up_merge_sort(unsorted_values))

    demonstrate_heap_structure([3, 1, 6, 5, 2, 4])

    print("\nHeap operations:")
    heap = MaxHeap()

    for value in [10, 4, 15, 7, 20, 3]:
        heap.insert(value)
        print(f"Inserted {value:>2}: {heap.data}")

    print("Maximum:", heap.peek_max())

    while heap:
        print("Extracted:", heap.extract_max())

    print("\nHeap sort:")
    print(heap_sort([9, 4, 7, 1, 3, 6, 2, 8, 5]))

    print_complexity_table()
    test_edge_cases()
    run_correctness_tests()
    demonstrate_stability()
    recursion_depth_demo()
    common_mistakes()
    advanced_complexity_relationships()
    real_world_applications()

    print("\n" + "=" * 78)
    print("DAY 9 PROGRAM COMPLETED")
    print("=" * 78)


if __name__ == "__main__":
    main()
