"""
Day 28 — Binary Search
=======================

A comprehensive, executable study file covering binary search from beginner
to advanced level.

Topics:
- Sorted-array requirement
- Left and right boundaries
- Midpoint calculation
- Search-space reduction
- Exact search
- First occurrence
- Last occurrence
- Lower bound
- Upper bound
- Search in variations of sorted arrays
- Rotated sorted arrays
- Descending arrays
- Nearly sorted arrays
- Binary search on the answer
- Invariant-based reasoning
- Complexity, edge cases, testing, and production considerations

The script uses only the Python standard library.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence
import random
import time


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL IDEA
# ---------------------------------------------------------------------------

def explain_binary_search() -> None:
    """
    Binary search repeatedly cuts a sorted search space approximately in half.

    For an ascending array:
        left  = first possible index
        right = last possible index
        mid   = middle candidate

    If array[mid] is smaller than the target, everything at or before mid
    can be discarded.

    If array[mid] is larger than the target, everything at or after mid
    can be discarded.

    If array[mid] equals the target, an exact match has been found.

    Time complexity:
        Best case:    O(1)
        Average case: O(log n)
        Worst case:   O(log n)

    Space complexity for an iterative implementation:
        O(1)
    """
    print("\n=== Binary Search Fundamentals ===")
    print("Binary search requires an ordered search space.")
    print("Each comparison discards roughly half of the remaining candidates.")
    print("Iterative binary search uses O(1) auxiliary space.")


# ---------------------------------------------------------------------------
# 2. MIDPOINT CALCULATION
# ---------------------------------------------------------------------------

def safe_midpoint(left: int, right: int) -> int:
    """
    Return the midpoint without directly computing left + right.

    In languages with fixed-width integer arithmetic, the expression
    (left + right) // 2 can overflow when left and right are very large.

    Python integers do not have the same fixed-width overflow problem, but
    this form teaches the portable pattern used in many languages.
    """
    return left + (right - left) // 2


# ---------------------------------------------------------------------------
# 3. EXACT SEARCH
# ---------------------------------------------------------------------------

def binary_search_exact(values: Sequence[int], target: int) -> int:
    """
    Find target in an ascending sorted sequence.

    Returns:
        The index of target if present.
        -1 otherwise.

    Preconditions:
        values must be sorted in ascending order.

    Important:
        With duplicate values, this function may return any matching index.
        It does not promise the first or last occurrence.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        mid = safe_midpoint(left, right)
        current = values[mid]

        if current == target:
            return mid

        if current < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def demonstrate_exact_search() -> None:
    print("\n=== Exact Search ===")

    values = [2, 5, 8, 12, 16, 21, 27, 35]
    for target in [2, 16, 35, 10]:
        index = binary_search_exact(values, target)
        print(f"values={values}, target={target}, index={index}")


# ---------------------------------------------------------------------------
# 4. BINARY SEARCH WITH A HALF-OPEN INTERVAL
# ---------------------------------------------------------------------------

def binary_search_half_open(values: Sequence[int], target: int) -> int:
    """
    Exact search using the interval [left, right).

    This representation uses:
        left = 0
        right = len(values)

    The right endpoint is excluded.

    The invariant is:
        If target exists, it must be within [left, right).

    This style is particularly useful when implementing lower_bound and
    upper_bound because the empty interval [x, x) is naturally represented.
    """
    left = 0
    right = len(values)

    while left < right:
        mid = left + (right - left) // 2

        if values[mid] == target:
            return mid

        if values[mid] < target:
            left = mid + 1
        else:
            right = mid

    return -1


# ---------------------------------------------------------------------------
# 5. FIRST OCCURRENCE
# ---------------------------------------------------------------------------

def first_occurrence(values: Sequence[int], target: int) -> int:
    """
    Return the index of the first occurrence of target.

    When a match is found, do not stop immediately.
    Save the candidate and continue searching to the left.

    Complexity:
        O(log n) time
        O(1) space
    """
    left = 0
    right = len(values) - 1
    answer = -1

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            answer = mid
            right = mid - 1
        elif values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return answer


# ---------------------------------------------------------------------------
# 6. LAST OCCURRENCE
# ---------------------------------------------------------------------------

def last_occurrence(values: Sequence[int], target: int) -> int:
    """
    Return the index of the last occurrence of target.

    When a match is found, save the candidate and continue searching to the
    right.
    """
    left = 0
    right = len(values) - 1
    answer = -1

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            answer = mid
            left = mid + 1
        elif values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return answer


# ---------------------------------------------------------------------------
# 7. LOWER BOUND
# ---------------------------------------------------------------------------

def lower_bound(values: Sequence[int], target: int) -> int:
    """
    Return the first index i such that values[i] >= target.

    If every value is smaller than target, return len(values).

    Examples:
        [1, 2, 2, 4], target=2 -> 1
        [1, 2, 2, 4], target=3 -> 3
        [1, 2, 2, 4], target=9 -> 4
        [], target=3        -> 0

    This is the same conceptual operation as bisect_left.
    """
    left = 0
    right = len(values)

    while left < right:
        mid = left + (right - left) // 2

        if values[mid] < target:
            left = mid + 1
        else:
            right = mid

    return left


# ---------------------------------------------------------------------------
# 8. UPPER BOUND
# ---------------------------------------------------------------------------

def upper_bound(values: Sequence[int], target: int) -> int:
    """
    Return the first index i such that values[i] > target.

    If no value is greater than target, return len(values).

    This is the same conceptual operation as bisect_right.
    """
    left = 0
    right = len(values)

    while left < right:
        mid = left + (right - left) // 2

        if values[mid] <= target:
            left = mid + 1
        else:
            right = mid

    return left


def occurrence_count(values: Sequence[int], target: int) -> int:
    """
    Count target occurrences using lower_bound and upper_bound.

    The target occupies:
        [lower_bound(target), upper_bound(target))

    Therefore:
        count = upper_bound - lower_bound
    """
    return upper_bound(values, target) - lower_bound(values, target)


# ---------------------------------------------------------------------------
# 9. RANGE OF OCCURRENCES
# ---------------------------------------------------------------------------

def occurrence_range(values: Sequence[int], target: int) -> tuple[int, int]:
    """
    Return the inclusive range of target occurrences.

    Returns (-1, -1) when target is absent.
    """
    first = lower_bound(values, target)

    if first == len(values) or values[first] != target:
        return -1, -1

    last = upper_bound(values, target) - 1
    return first, last


# ---------------------------------------------------------------------------
# 10. DESCENDING-ORDER BINARY SEARCH
# ---------------------------------------------------------------------------

def binary_search_descending(values: Sequence[int], target: int) -> int:
    """
    Exact binary search for a sequence sorted in descending order.

    The direction of the comparison changes because larger values appear
    toward the left and smaller values toward the right.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            return mid

        if values[mid] > target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ---------------------------------------------------------------------------
# 11. ROTATED SORTED ARRAY
# ---------------------------------------------------------------------------

def search_rotated_sorted(values: Sequence[int], target: int) -> int:
    """
    Search an ascending sorted array rotated at an unknown pivot.

    Example:
        Original: [1, 2, 3, 4, 5, 6, 7]
        Rotated:  [4, 5, 6, 7, 1, 2, 3]

    At least one half of the current search range is normally sorted when
    all values are distinct.

    We identify the sorted half and determine whether the target lies inside
    it. If it does, search that half. Otherwise search the other half.

    Complexity with distinct values:
        O(log n) time
        O(1) space

    With duplicates, the clean logarithmic guarantee can degrade to O(n).
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            return mid

        # Left half is sorted.
        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1

        # Right half is sorted.
        else:
            if values[mid] < target <= values[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


def search_rotated_with_duplicates(
    values: Sequence[int], target: int
) -> bool:
    """
    Search a rotated sorted array that may contain duplicates.

    When values[left] == values[mid] == values[right], we cannot determine
    which half is sorted. Removing one boundary from each side resolves the
    ambiguity.

    Worst case can become O(n), for example:
        [1, 1, 1, 1, 1, 1, 1]
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            return True

        if values[left] == values[mid] == values[right]:
            left += 1
            right -= 1
            continue

        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if values[mid] < target <= values[right]:
                left = mid + 1
            else:
                right = mid - 1

    return False


# ---------------------------------------------------------------------------
# 12. NEARLY SORTED ARRAY
# ---------------------------------------------------------------------------

def search_nearly_sorted(values: Sequence[int], target: int) -> int:
    """
    Search an array where each element may have moved by at most one position.

    Example:
        Sorted: [10, 20, 30, 40, 50]
        Nearly: [10, 30, 20, 50, 40]

    At each midpoint, inspect:
        mid
        mid - 1
        mid + 1

    Then eliminate the region that cannot contain the target.

    This assumes a specific "distance at most one" disorder model.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            return mid

        if mid - 1 >= left and values[mid - 1] == target:
            return mid - 1

        if mid + 1 <= right and values[mid + 1] == target:
            return mid + 1

        if target < values[mid]:
            right = mid - 2
        else:
            left = mid + 2

    return -1


# ---------------------------------------------------------------------------
# 13. FINDING A PEAK
# ---------------------------------------------------------------------------

def find_peak(values: Sequence[int]) -> int:
    """
    Find an index of a peak.

    A peak is an element that is not smaller than its relevant neighbors.

    This demonstrates an important generalization:
    binary search is not limited to finding a specific value. It can search
    for a boundary satisfying a monotonic property.

    For this implementation, the array is treated as having conceptual
    negative-infinity values outside its boundaries.

    Returns:
        A valid peak index, or -1 for an empty sequence.
    """
    if not values:
        return -1

    left = 0
    right = len(values) - 1

    while left < right:
        mid = safe_midpoint(left, right)

        if values[mid] < values[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return left


# ---------------------------------------------------------------------------
# 14. BINARY SEARCH ON THE ANSWER
# ---------------------------------------------------------------------------

def minimum_capacity_for_shipping(
    weights: Sequence[int],
    days: int,
) -> int:
    """
    Find the minimum ship capacity needed to transport all packages in order
    within the specified number of days.

    The search space is not an array of answers. Instead, it is a numerical
    range of possible capacities.

    Feasibility is monotonic:
        If capacity C works, every capacity > C also works.

    That monotonic property permits binary search.

    Complexity:
        O(n log S)
    where S is approximately max_possible_capacity - min_possible_capacity.
    """
    if days <= 0:
        raise ValueError("days must be positive")

    if not weights:
        return 0

    if any(weight < 0 for weight in weights):
        raise ValueError("weights cannot be negative")

    if days >= len(weights):
        return max(weights)

    left = max(weights)
    right = sum(weights)

    def can_ship(capacity: int) -> bool:
        used_days = 1
        current_load = 0

        for weight in weights:
            if current_load + weight <= capacity:
                current_load += weight
            else:
                used_days += 1
                current_load = weight

                if used_days > days:
                    return False

        return True

    while left < right:
        mid = left + (right - left) // 2

        if can_ship(mid):
            right = mid
        else:
            left = mid + 1

    return left


# ---------------------------------------------------------------------------
# 15. INTEGER SQUARE ROOT
# ---------------------------------------------------------------------------

def integer_square_root(number: int) -> int:
    """
    Return floor(sqrt(number)) without using math.sqrt.

    The answer is searched in the integer interval [0, number].

    Predicate:
        mid * mid <= number

    is monotonic:
        Once mid * mid becomes greater than number, every larger candidate
        also fails.
    """
    if number < 0:
        raise ValueError("square root is undefined for negative integers")

    if number < 2:
        return number

    left = 1
    right = number // 2
    answer = 1

    while left <= right:
        mid = safe_midpoint(left, right)
        square = mid * mid

        if square == number:
            return mid

        if square < number:
            answer = mid
            left = mid + 1
        else:
            right = mid - 1

    return answer


# ---------------------------------------------------------------------------
# 16. FIRST TRUE PREDICATE
# ---------------------------------------------------------------------------

def first_true(low: int, high: int, predicate: Callable[[int], bool]) -> int:
    """
    Find the first integer in [low, high] for which predicate(x) is True.

    Required property:
        predicate is monotonic:
            False False False True True True

    Returns -1 when no value satisfies the predicate.

    This abstraction captures a large family of "binary search on the answer"
    problems.
    """
    if low > high:
        return -1

    left = low
    right = high
    answer = -1

    while left <= right:
        mid = safe_midpoint(left, right)

        if predicate(mid):
            answer = mid
            right = mid - 1
        else:
            left = mid + 1

    return answer


# ---------------------------------------------------------------------------
# 17. FLOATING-POINT BINARY SEARCH
# ---------------------------------------------------------------------------

def approximate_square_root(number: float, iterations: int = 100) -> float:
    """
    Approximate sqrt(number) using binary search.

    Floating-point binary search should generally use either:
    - a fixed iteration count, or
    - a tolerance condition.

    Fixed iterations provide predictable execution.
    """
    if number < 0:
        raise ValueError("number must be non-negative")

    if number == 0:
        return 0.0

    low = 0.0
    high = max(1.0, number)

    for _ in range(iterations):
        mid = (low + high) / 2.0

        if mid * mid < number:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


# ---------------------------------------------------------------------------
# 18. SEARCH IN AN INFINITE-LIKE ORDERED STREAM
# ---------------------------------------------------------------------------

def exponential_search(values: Sequence[int], target: int) -> int:
    """
    Exponential search first expands the range exponentially, then performs
    binary search.

    Useful when:
    - the upper bound is unknown,
    - or the target is expected near the beginning.

    This implementation works with a finite Python sequence, but models the
    range-expansion technique used with larger or conceptually unbounded
    ordered data.
    """
    if not values:
        return -1

    if values[0] == target:
        return 0

    bound = 1

    while bound < len(values) and values[bound] < target:
        bound *= 2

    left = bound // 2
    right = min(bound, len(values) - 1)

    while left <= right:
        mid = safe_midpoint(left, right)

        if values[mid] == target:
            return mid

        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ---------------------------------------------------------------------------
# 19. SEARCH A 2D MATRIX
# ---------------------------------------------------------------------------

def search_sorted_matrix(
    matrix: Sequence[Sequence[int]],
    target: int,
) -> tuple[int, int]:
    """
    Search a matrix where:
    - each row is sorted,
    - each row's first value is greater than the previous row's last value.

    The matrix can therefore be conceptually flattened into one sorted array.

    Returns:
        (row, column), or (-1, -1).
    """
    if not matrix or not matrix[0]:
        return -1, -1

    rows = len(matrix)
    columns = len(matrix[0])

    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix must be rectangular")

    left = 0
    right = rows * columns - 1

    while left <= right:
        mid = safe_midpoint(left, right)
        row = mid // columns
        column = mid % columns
        current = matrix[row][column]

        if current == target:
            return row, column

        if current < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1, -1


# ---------------------------------------------------------------------------
# 20. CUSTOM OBJECT SEARCH
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Product:
    product_id: int
    name: str
    price: float


def binary_search_product(
    products: Sequence[Product],
    product_id: int,
) -> int:
    """
    Search objects ordered by product_id.

    Binary search works with objects as long as the comparison key has a
    meaningful sorted order.
    """
    left = 0
    right = len(products) - 1

    while left <= right:
        mid = safe_midpoint(left, right)
        current_id = products[mid].product_id

        if current_id == product_id:
            return mid

        if current_id < product_id:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ---------------------------------------------------------------------------
# 21. ITERATIVE VS RECURSIVE SEARCH
# ---------------------------------------------------------------------------

def binary_search_recursive(
    values: Sequence[int],
    target: int,
    left: int = 0,
    right: int | None = None,
) -> int:
    """
    Recursive exact binary search.

    Recursive form is conceptually elegant but consumes call-stack space.

    Iterative binary search is usually preferable for production code when
    there is no need for recursion.
    """
    if right is None:
        right = len(values) - 1

    if left > right:
        return -1

    mid = safe_midpoint(left, right)

    if values[mid] == target:
        return mid

    if values[mid] < target:
        return binary_search_recursive(values, target, mid + 1, right)

    return binary_search_recursive(values, target, left, mid - 1)


# ---------------------------------------------------------------------------
# 22. VALIDATION
# ---------------------------------------------------------------------------

def is_sorted_ascending(values: Sequence[int]) -> bool:
    """Return True if values are non-decreasing."""
    return all(values[index] <= values[index + 1] for index in range(len(values) - 1))


def require_sorted_ascending(values: Sequence[int]) -> None:
    """
    Validate the most important precondition of standard binary search.

    Checking sortedness costs O(n), so production code should normally avoid
    repeating this check when the data structure already guarantees ordering.
    """
    if not is_sorted_ascending(values):
        raise ValueError("binary search requires ascending sorted data")


def validated_binary_search(values: Sequence[int], target: int) -> int:
    """Educational wrapper that explicitly validates the sorted-array rule."""
    require_sorted_ascending(values)
    return binary_search_exact(values, target)


# ---------------------------------------------------------------------------
# 23. COMMON MISTAKES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    print("\n=== Common Binary Search Mistakes ===")

    print("1. Searching an unsorted array:")
    unsorted_values = [8, 2, 10, 4, 6]
    print(
        "   Input:",
        unsorted_values,
        "target=6",
        "result:",
        binary_search_exact(unsorted_values, 6),
        "(result is not meaningful because the precondition is violated)",
    )

    print("2. Forgetting duplicate behavior:")
    duplicate_values = [1, 2, 2, 2, 3]
    arbitrary = binary_search_exact(duplicate_values, 2)
    first = first_occurrence(duplicate_values, 2)
    last = last_occurrence(duplicate_values, 2)
    print(f"   Any match={arbitrary}, first={first}, last={last}")

    print("3. Off-by-one errors:")
    print("   Empty array:", binary_search_exact([], 10))
    print("   One element present:", binary_search_exact([10], 10))
    print("   One element absent:", binary_search_exact([10], 20))

    print("4. Confusing lower_bound with exact search:")
    values = [10, 20, 20, 30]
    print("   lower_bound(25):", lower_bound(values, 25))
    print("   exact search(25):", binary_search_exact(values, 25))


# ---------------------------------------------------------------------------
# 24. PERFORMANCE COMPARISON
# ---------------------------------------------------------------------------

def linear_search(values: Sequence[int], target: int) -> int:
    """Reference O(n) search used for comparison."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def benchmark_searches() -> None:
    """
    Small educational benchmark.

    Exact timings depend on hardware, Python version, system load, and data.
    The purpose is to illustrate scaling rather than produce a formal
    benchmark.
    """
    print("\n=== Performance Comparison ===")

    values = list(range(2_000_000))
    target = 1_999_999

    start = time.perf_counter()
    linear_result = linear_search(values, target)
    linear_time = time.perf_counter() - start

    start = time.perf_counter()
    binary_result = binary_search_exact(values, target)
    binary_time = time.perf_counter() - start

    print(f"Linear result: {linear_result}, time: {linear_time:.6f}s")
    print(f"Binary result: {binary_result}, time: {binary_time:.6f}s")
    print("Linear search performs O(n) comparisons in the worst case.")
    print("Binary search performs O(log n) comparisons when ordering is available.")


# ---------------------------------------------------------------------------
# 25. TESTING
# ---------------------------------------------------------------------------

def run_deterministic_tests() -> None:
    """Test important correctness cases."""
    print("\n=== Deterministic Tests ===")

    assert binary_search_exact([], 5) == -1
    assert binary_search_exact([5], 5) == 0
    assert binary_search_exact([5], 4) == -1

    values = [1, 2, 2, 2, 3, 4, 4, 9]

    assert first_occurrence(values, 2) == 1
    assert last_occurrence(values, 2) == 3
    assert first_occurrence(values, 4) == 5
    assert last_occurrence(values, 4) == 6
    assert first_occurrence(values, 8) == -1
    assert last_occurrence(values, 8) == -1

    assert lower_bound(values, 0) == 0
    assert lower_bound(values, 1) == 0
    assert lower_bound(values, 2) == 1
    assert lower_bound(values, 3) == 4
    assert lower_bound(values, 8) == 7
    assert lower_bound(values, 10) == len(values)

    assert upper_bound(values, 2) == 4
    assert upper_bound(values, 4) == 7
    assert upper_bound(values, 10) == len(values)

    assert occurrence_count(values, 2) == 3
    assert occurrence_range(values, 2) == (1, 3)
    assert occurrence_range(values, 8) == (-1, -1)

    descending = [10, 8, 6, 4, 2, 0]
    assert binary_search_descending(descending, 6) == 2
    assert binary_search_descending(descending, 7) == -1

    rotated = [4, 5, 6, 7, 0, 1, 2]
    assert search_rotated_sorted(rotated, 0) == 4
    assert search_rotated_sorted(rotated, 3) == -1

    rotated_duplicates = [2, 5, 6, 0, 0, 1, 2]
    assert search_rotated_with_duplicates(rotated_duplicates, 0)
    assert not search_rotated_with_duplicates(rotated_duplicates, 3)

    nearly_sorted = [10, 30, 20, 50, 40, 60]
    assert search_nearly_sorted(nearly_sorted, 20) == 2
    assert search_nearly_sorted(nearly_sorted, 40) == 4
    assert search_nearly_sorted(nearly_sorted, 99) == -1

    assert integer_square_root(0) == 0
    assert integer_square_root(1) == 1
    assert integer_square_root(15) == 3
    assert integer_square_root(16) == 4
    assert integer_square_root(17) == 4

    assert minimum_capacity_for_shipping([1, 2, 3, 1, 1], 4) == 3

    matrix = [
        [1, 3, 5, 7],
        [10, 11, 16, 20],
        [23, 30, 34, 60],
    ]
    assert search_sorted_matrix(matrix, 3) == (0, 1)
    assert search_sorted_matrix(matrix, 13) == (-1, -1)

    products = [
        Product(100, "Keyboard", 50.0),
        Product(200, "Monitor", 250.0),
        Product(300, "Mouse", 30.0),
    ]
    assert binary_search_product(products, 200) == 1
    assert binary_search_product(products, 999) == -1

    print("All deterministic tests passed.")


# ---------------------------------------------------------------------------
# 26. PROPERTY-STYLE RANDOMIZED TESTING
# ---------------------------------------------------------------------------

def run_randomized_tests(iterations: int = 500) -> None:
    """
    Compare binary-search results with Python's straightforward behavior.

    Randomized testing is valuable for catching boundary and duplicate bugs.
    """
    print(f"\n=== Randomized Tests ({iterations} cases) ===")

    random_generator = random.Random(28)

    for _ in range(iterations):
        values = sorted(
            random_generator.randint(-20, 20)
            for _ in range(random_generator.randint(0, 100))
        )
        target = random_generator.randint(-25, 25)

        expected_index = (
            values.index(target)
            if target in values
            else -1
        )

        actual_index = binary_search_exact(values, target)

        if expected_index == -1:
            assert actual_index == -1
        else:
            assert actual_index != -1
            assert values[actual_index] == target

        expected_first = bisect_left(values, target)
        expected_first = (
            expected_first
            if expected_first < len(values) and values[expected_first] == target
            else -1
        )

        expected_last = bisect_right(values, target) - 1
        expected_last = (
            expected_last
            if expected_last >= 0 and values[expected_last] == target
            else -1
        )

        assert first_occurrence(values, target) == expected_first
        assert last_occurrence(values, target) == expected_last
        assert lower_bound(values, target) == bisect_left(values, target)
        assert upper_bound(values, target) == bisect_right(values, target)

    print("All randomized tests passed.")


# ---------------------------------------------------------------------------
# 27. PRACTICAL EXAMPLES
# ---------------------------------------------------------------------------

def demonstrate_practical_examples() -> None:
    print("\n=== Practical Examples ===")

    exam_scores = [35, 42, 42, 48, 55, 55, 55, 61, 73, 88]

    print("Scores:", exam_scores)
    print("First score >= 55:", lower_bound(exam_scores, 55))
    print("First score > 55:", upper_bound(exam_scores, 55))
    print("Number of students scoring exactly 55:",
          occurrence_count(exam_scores, 55))

    timestamps = [100, 125, 150, 175, 200, 225]
    target_timestamp = 160
    insertion_point = lower_bound(timestamps, target_timestamp)
    print(
        "Insertion point for timestamp",
        target_timestamp,
        "is",
        insertion_point,
    )

    file_sizes = [100, 250, 500, 750, 1000]
    size_limit = 600
    allowed_index = upper_bound(file_sizes, size_limit)
    print(
        "First file size greater than limit:",
        allowed_index,
        "value:",
        file_sizes[allowed_index] if allowed_index < len(file_sizes) else None,
    )


# ---------------------------------------------------------------------------
# 28. ERROR AND EDGE CASE DEMONSTRATIONS
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n=== Edge Cases ===")

    cases = [
        ([], 10),
        ([10], 10),
        ([10], 5),
        ([1, 2, 3], 1),
        ([1, 2, 3], 3),
        ([1, 2, 3], 4),
        ([5, 5, 5, 5], 5),
        ([-10, -5, -2, 0, 4], -10),
        ([-10, -5, -2, 0, 4], 4),
    ]

    for values, target in cases:
        print(
            f"values={values!r}, target={target}: "
            f"exact={binary_search_exact(values, target)}, "
            f"first={first_occurrence(values, target)}, "
            f"last={last_occurrence(values, target)}, "
            f"lower={lower_bound(values, target)}, "
            f"upper={upper_bound(values, target)}"
        )

    try:
        validated_binary_search([3, 1, 2], 1)
    except ValueError as error:
        print("Validation error:", error)

    try:
        integer_square_root(-1)
    except ValueError as error:
        print("Square-root error:", error)

    try:
        minimum_capacity_for_shipping([1, 2, 3], 0)
    except ValueError as error:
        print("Shipping error:", error)


# ---------------------------------------------------------------------------
# 29. COMPLEXITY REFERENCE
# ---------------------------------------------------------------------------

def print_complexity_reference() -> None:
    print("\n=== Complexity Reference ===")
    rows = [
        ("Exact binary search", "O(log n)", "O(1)"),
        ("First occurrence", "O(log n)", "O(1)"),
        ("Last occurrence", "O(log n)", "O(1)"),
        ("Lower bound", "O(log n)", "O(1)"),
        ("Upper bound", "O(log n)", "O(1)"),
        ("Rotated search, distinct", "O(log n)", "O(1)"),
        ("Rotated search, duplicates", "O(n) worst case", "O(1)"),
        ("Exponential search", "O(log n)", "O(1)"),
        ("Recursive binary search", "O(log n)", "O(log n) stack"),
        ("Binary search on answer", "O(log S × predicate)", "O(1)"),
    ]

    for name, time_complexity, space_complexity in rows:
        print(f"{name:35} time={time_complexity:22} space={space_complexity}")


# ---------------------------------------------------------------------------
# 30. MAIN STUDY PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    explain_binary_search()
    demonstrate_exact_search()

    print("\n=== Half-Open Interval ===")
    values = [1, 4, 7, 10, 15]
    print("Search result:", binary_search_half_open(values, 10))

    duplicate_values = [1, 2, 2, 2, 3, 4]
    print("\n=== Duplicate Handling ===")
    print("Values:", duplicate_values)
    print("First occurrence of 2:", first_occurrence(duplicate_values, 2))
    print("Last occurrence of 2:", last_occurrence(duplicate_values, 2))
    print("Lower bound of 2:", lower_bound(duplicate_values, 2))
    print("Upper bound of 2:", upper_bound(duplicate_values, 2))
    print("Count of 2:", occurrence_count(duplicate_values, 2))
    print("Range of 2:", occurrence_range(duplicate_values, 2))

    print("\n=== Descending Search ===")
    descending = [100, 90, 80, 70, 60, 50]
    print("Search for 70:", binary_search_descending(descending, 70))

    print("\n=== Rotated Search ===")
    rotated = [40, 50, 60, 70, 10, 20, 30]
    for target in [10, 70, 30, 99]:
        print(target, "->", search_rotated_sorted(rotated, target))

    print("\n=== Nearly Sorted Search ===")
    nearly_sorted = [10, 30, 20, 50, 40, 60]
    for target in [10, 20, 40, 60, 100]:
        print(target, "->", search_nearly_sorted(nearly_sorted, target))

    print("\n=== Peak Search ===")
    peak_values = [1, 3, 8, 12, 9, 4, 2]
    peak_index = find_peak(peak_values)
    print("Values:", peak_values)
    print("Peak index:", peak_index)
    print("Peak value:", peak_values[peak_index])

    print("\n=== Binary Search on the Answer ===")
    weights = [1, 2, 3, 1, 1]
    for days in [3, 4, 5]:
        capacity = minimum_capacity_for_shipping(weights, days)
        print(f"weights={weights}, days={days}, minimum capacity={capacity}")

    print("\n=== Integer Square Root ===")
    for number in [0, 1, 2, 15, 16, 17, 100]:
        print(f"floor(sqrt({number})) = {integer_square_root(number)}")

    print("\n=== First True Predicate ===")
    threshold = 73
    answer = first_true(0, 100, lambda value: value >= threshold)
    print("First value >= 73:", answer)

    print("\n=== Floating-Point Search ===")
    for number in [2.0, 10.0, 100.0]:
        estimate = approximate_square_root(number)
        print(f"sqrt({number}) ≈ {estimate:.12f}")

    print("\n=== Exponential Search ===")
    values = list(range(0, 1000, 3))
    print("Search 600:", exponential_search(values, 600))
    print("Search 601:", exponential_search(values, 601))

    print("\n=== Matrix Search ===")
    matrix = [
        [1, 3, 5, 7],
        [10, 11, 16, 20],
        [23, 30, 34, 60],
    ]
    print("Search 16:", search_sorted_matrix(matrix, 16))
    print("Search 17:", search_sorted_matrix(matrix, 17))

    print("\n=== Product Search ===")
    products = [
        Product(101, "Keyboard", 49.99),
        Product(205, "Monitor", 249.99),
        Product(310, "Mouse", 29.99),
        Product(415, "Webcam", 89.99),
    ]
    product_index = binary_search_product(products, 310)
    print("Product index:", product_index)
    if product_index != -1:
        print("Product:", products[product_index])

    print("\n=== Recursive Search ===")
    recursive_values = [2, 4, 6, 8, 10, 12]
    print("Search 8:", binary_search_recursive(recursive_values, 8))

    demonstrate_practical_examples()
    demonstrate_common_mistakes()
    demonstrate_edge_cases()
    run_deterministic_tests()
    run_randomized_tests()
    print_complexity_reference()

    print("\n=== Study Notes ===")
    print("1. Standard binary search needs a sorted search space.")
    print("2. Choose and maintain one interval convention consistently.")
    print("3. A match does not necessarily mean the search is finished.")
    print("4. Lower bound finds the first value >= target.")
    print("5. Upper bound finds the first value > target.")
    print("6. Many advanced problems search a monotonic predicate instead of a value.")
    print("7. Correct boundary updates prevent infinite loops and missed answers.")


if __name__ == "__main__":
    main()
