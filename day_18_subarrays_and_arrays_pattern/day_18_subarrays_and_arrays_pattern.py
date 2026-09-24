"""
Day 18 — Subarrays and Array Patterns

A standalone study and practice program covering:
- Subarray enumeration
- Prefix sums
- Hashing with arrays
- Two pointers
- Sliding windows
- Sorting-based solutions
- Maximum/minimum subarray problems
- Complexity analysis
- Edge cases and validation
- Progressive problem solving

All examples use only the Python standard library.
"""

from __future__ import annotations

from collections import defaultdict
from bisect import bisect_left
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


# ============================================================
# 1. FUNDAMENTALS
# ============================================================

def explain_subarray() -> None:
    """Print the essential definition of a subarray."""
    print("\n=== SUBARRAY FUNDAMENTALS ===")
    print("A subarray is a contiguous sequence of elements from an array.")
    print("For [1, 2, 3, 4], examples include [1], [2, 3], [1, 2, 3, 4].")
    print("Non-examples include [1, 3], because the elements are not contiguous.")

    values = [1, 2, 3, 4]
    print("\nArray:", values)
    print("Subarray values[1:3]:", values[1:3])
    print("The slice contains indices 1 and 2.")


def count_subarrays(n: int) -> int:
    """
    Number of non-empty contiguous subarrays of an array of length n.

    Every subarray is identified by a start and end index.
    There are n choices for a length-1 starting position,
    n-1 for length 2, and so on:

        n + (n-1) + ... + 1 = n(n+1)/2
    """
    if n < 0:
        raise ValueError("Array length cannot be negative.")
    return n * (n + 1) // 2


def enumerate_subarrays(values: list[int]) -> list[tuple[int, int, list[int]]]:
    """
    Enumerate every non-empty subarray.

    Returns:
        (start_index, end_index, subarray)

    Time: O(n^3) if copying each subarray is counted.
    The nested index enumeration itself is O(n^2).
    """
    result = []

    for start in range(len(values)):
        for end in range(start, len(values)):
            result.append((start, end, values[start:end + 1]))

    return result


def enumerate_subarray_ranges(values: list[int]) -> list[tuple[int, int]]:
    """
    Enumerate only start/end boundaries.

    This avoids copying elements and therefore demonstrates
    the distinction between enumerating ranges and materializing
    every subarray.
    """
    ranges = []

    for start in range(len(values)):
        for end in range(start, len(values)):
            ranges.append((start, end))

    return ranges


# ============================================================
# 2. BASIC SUBARRAY AGGREGATION
# ============================================================

def all_subarray_sums_bruteforce(values: list[int]) -> list[tuple[int, int, int]]:
    """
    Calculate every subarray sum directly.

    Time: O(n^3) in the worst case because sum(values[start:end+1])
    takes O(n) for each of O(n^2) subarrays.

    This is useful for teaching and verification, not large inputs.
    """
    result = []

    for start in range(len(values)):
        for end in range(start, len(values)):
            total = sum(values[start:end + 1])
            result.append((start, end, total))

    return result


def all_subarray_sums_incremental(values: list[int]) -> list[tuple[int, int, int]]:
    """
    Improve brute-force summation to O(n^2).

    For a fixed start index, extend the end index one element at a time
    and update the current sum instead of recalculating it.
    """
    result = []

    for start in range(len(values)):
        current_sum = 0

        for end in range(start, len(values)):
            current_sum += values[end]
            result.append((start, end, current_sum))

    return result


# ============================================================
# 3. PREFIX SUMS
# ============================================================

def build_prefix_sum(values: list[int]) -> list[int]:
    """
    Build a prefix sum array.

    prefix[i] stores the sum of the first i elements.

    Example:
        values = [2, 4, 1]
        prefix = [0, 2, 6, 7]

    Then:
        sum(values[left:right + 1]) = prefix[right + 1] - prefix[left]

    Time: O(n)
    Space: O(n)
    """
    prefix = [0]

    for value in values:
        prefix.append(prefix[-1] + value)

    return prefix


def range_sum(prefix: list[int], left: int, right: int) -> int:
    """Return the inclusive range sum using prefix sums."""
    if not prefix:
        raise ValueError("Prefix array cannot be empty.")

    if left < 0 or right < left or right + 1 >= len(prefix):
        raise IndexError("Invalid range.")

    return prefix[right + 1] - prefix[left]


def prefix_sum_demo() -> None:
    print("\n=== PREFIX SUMS ===")

    values = [3, -2, 5, 7, -4, 6]
    prefix = build_prefix_sum(values)

    print("Values:", values)
    print("Prefix:", prefix)

    left, right = 1, 4
    print(
        f"Sum of values[{left}:{right + 1}] =",
        range_sum(prefix, left, right),
    )

    # A prefix sum does not make building the prefix itself free.
    # Its advantage appears when many range queries must be answered.
    queries = [(0, 2), (1, 4), (2, 5)]

    print("Multiple O(1) range queries:")
    for query_left, query_right in queries:
        print(
            f"  [{query_left}, {query_right}] -> "
            f"{range_sum(prefix, query_left, query_right)}"
        )


def subarray_sum_equals_k_bruteforce(values: list[int], target: int) -> int:
    """Count subarrays with sum == target using O(n^2) enumeration."""
    count = 0

    for start in range(len(values)):
        current_sum = 0
        for end in range(start, len(values)):
            current_sum += values[end]
            if current_sum == target:
                count += 1

    return count


def subarray_sum_equals_k_hashing(values: list[int], target: int) -> int:
    """
    Count subarrays whose sum equals target in O(n) average time.

    If:
        prefix[j] - prefix[i] = target

    then:
        prefix[i] = prefix[j] - target

    A frequency map stores how often previous prefix sums occurred.
    """
    prefix_frequency = defaultdict(int)
    prefix_frequency[0] = 1

    prefix = 0
    count = 0

    for value in values:
        prefix += value

        # Previous prefix sums equal to prefix - target
        # produce subarrays ending at the current position.
        count += prefix_frequency[prefix - target]

        prefix_frequency[prefix] += 1

    return count


# ============================================================
# 4. HASHING WITH ARRAYS
# ============================================================

def two_sum_hashing(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Find two indices whose values sum to target.

    Average:
        Time O(n)
        Space O(n)

    Unlike sorting, this preserves the original indices.
    """
    seen: dict[int, int] = {}

    for index, value in enumerate(values):
        needed = target - value

        if needed in seen:
            return seen[needed], index

        seen[value] = index

    return None


def frequency_table(values: Iterable[int]) -> dict[int, int]:
    """Build a frequency table using hashing."""
    frequencies: dict[int, int] = defaultdict(int)

    for value in values:
        frequencies[value] += 1

    return dict(frequencies)


def longest_zero_sum_subarray(values: list[int]) -> tuple[int, int, int] | None:
    """
    Find the longest subarray whose sum is zero.

    Prefix sums are used as follows:
    If the same prefix sum occurs at i and j,
    then values[i+1:j+1] sums to zero.

    Time: O(n) average
    Space: O(n)
    """
    first_position: dict[int, int] = {0: -1}

    prefix = 0
    best_length = 0
    best_range: tuple[int, int, int] | None = None

    for index, value in enumerate(values):
        prefix += value

        if prefix in first_position:
            start = first_position[prefix] + 1
            length = index - first_position[prefix]

            if length > best_length:
                best_length = length
                best_range = (start, index, length)
        else:
            # Store only the earliest occurrence because it maximizes
            # the length of a future subarray.
            first_position[prefix] = index

    return best_range


# ============================================================
# 5. TWO POINTERS
# ============================================================

def two_pointer_pair_sum_sorted(values: list[int], target: int) -> tuple[int, int] | None:
    """
    Find a pair summing to target in an already sorted array.

    left starts at the smallest value.
    right starts at the largest value.

    If the sum is too small, move left forward.
    If the sum is too large, move right backward.

    Time: O(n)
    Space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        current_sum = values[left] + values[right]

        if current_sum == target:
            return values[left], values[right]

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


def two_pointer_pair_sum_unsorted(values: list[int], target: int) -> tuple[int, int] | None:
    """
    Sort a copy, then use two pointers.

    Time: O(n log n)
    Space: O(n) for the copied array.

    This is useful when the original indices are not important.
    """
    sorted_values = sorted(values)
    return two_pointer_pair_sum_sorted(sorted_values, target)


def remove_duplicates_sorted(values: list[int]) -> list[int]:
    """
    Remove duplicates from a sorted array using two-pointer logic.

    This version returns a new list and does not mutate the input.
    """
    if not values:
        return []

    result = [values[0]]
    write = 1

    for read in range(1, len(values)):
        if values[read] != values[write - 1]:
            result.append(values[read])
            write += 1

    return result


def container_with_most_water(heights: list[int]) -> int:
    """
    Classic two-pointer optimization.

    Area = width * min(left_height, right_height).

    Moving the shorter boundary is the only move that can potentially
    improve the limiting height.

    Time: O(n)
    Space: O(1)
    """
    if any(height < 0 for height in heights):
        raise ValueError("Heights cannot be negative.")

    left = 0
    right = len(heights) - 1
    best_area = 0

    while left < right:
        width = right - left
        area = width * min(heights[left], heights[right])
        best_area = max(best_area, area)

        if heights[left] <= heights[right]:
            left += 1
        else:
            right -= 1

    return best_area


# ============================================================
# 6. SLIDING WINDOWS
# ============================================================

def maximum_sum_fixed_window(values: list[int], window_size: int) -> int:
    """
    Maximum sum of any subarray of exactly window_size elements.

    Sliding the window avoids recomputing the entire sum.

    Time: O(n)
    Space: O(1)
    """
    if window_size <= 0:
        raise ValueError("Window size must be positive.")

    if window_size > len(values):
        raise ValueError("Window size cannot exceed array length.")

    current_sum = sum(values[:window_size])
    best_sum = current_sum

    for right in range(window_size, len(values)):
        current_sum += values[right]
        current_sum -= values[right - window_size]
        best_sum = max(best_sum, current_sum)

    return best_sum


def minimum_size_subarray_sum_positive(values: list[int], target: int) -> int:
    """
    Find the minimum length subarray with sum >= target.

    This sliding-window method requires all array values to be positive.

    Time: O(n)
    Space: O(1)

    The positivity condition matters because adding an element always
    increases the sum and removing the leftmost element always decreases it.
    """
    if target <= 0:
        raise ValueError("Target must be positive.")

    if any(value <= 0 for value in values):
        raise ValueError(
            "This sliding-window implementation requires strictly positive values."
        )

    left = 0
    current_sum = 0
    best_length = len(values) + 1

    for right, value in enumerate(values):
        current_sum += value

        while current_sum >= target:
            best_length = min(best_length, right - left + 1)
            current_sum -= values[left]
            left += 1

    return 0 if best_length == len(values) + 1 else best_length


def longest_subarray_at_most_k_distinct(values: list[int], k: int) -> int:
    """
    Longest subarray containing at most k distinct values.

    Unlike the previous positive-sum example, this pattern works with
    arbitrary values because the window condition is based on frequency.

    Time: O(n) average
    Space: O(k) approximately for the active window.
    """
    if k < 0:
        raise ValueError("k cannot be negative.")

    if k == 0:
        return 0

    counts: dict[int, int] = defaultdict(int)
    left = 0
    best = 0

    for right, value in enumerate(values):
        counts[value] += 1

        while len(counts) > k:
            outgoing = values[left]
            counts[outgoing] -= 1

            if counts[outgoing] == 0:
                del counts[outgoing]

            left += 1

        best = max(best, right - left + 1)

    return best


def longest_subarray_sum_at_most_k_nonnegative(
    values: list[int], target: int
) -> int:
    """
    Longest subarray with sum <= target for non-negative values.

    The non-negative constraint is essential to the simple sliding-window
    reasoning: extending right never decreases the sum.
    """
    if target < 0:
        return 0

    if any(value < 0 for value in values):
        raise ValueError("Values must be non-negative.")

    left = 0
    current_sum = 0
    best = 0

    for right, value in enumerate(values):
        current_sum += value

        while current_sum > target and left <= right:
            current_sum -= values[left]
            left += 1

        best = max(best, right - left + 1)

    return best


# ============================================================
# 7. KADANE'S ALGORITHM
# ============================================================

@dataclass
class SubarrayResult:
    start: int
    end: int
    value: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def maximum_subarray_bruteforce(values: list[int]) -> SubarrayResult | None:
    """
    O(n^2) maximum-subarray solution using incremental sums.

    Useful as a reference implementation for testing Kadane's algorithm.
    """
    if not values:
        return None

    best = SubarrayResult(0, 0, values[0])

    for start in range(len(values)):
        current_sum = 0

        for end in range(start, len(values)):
            current_sum += values[end]

            if current_sum > best.value:
                best = SubarrayResult(start, end, current_sum)

    return best


def maximum_subarray_kadane(values: list[int]) -> SubarrayResult | None:
    """
    Kadane's algorithm.

    At each position:
        current = best sum of a subarray ending here.

    Either:
        1. Extend the previous subarray.
        2. Start a new subarray at the current element.

    Time: O(n)
    Space: O(1)

    This implementation also tracks the actual range.
    """
    if not values:
        return None

    current_sum = values[0]
    best_sum = values[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(values)):
        value = values[index]

        if current_sum + value < value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return SubarrayResult(best_start, best_end, best_sum)


def minimum_subarray_kadane(values: list[int]) -> SubarrayResult | None:
    """Find the minimum-sum contiguous subarray in O(n)."""
    if not values:
        return None

    current_sum = values[0]
    best_sum = values[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(values)):
        value = values[index]

        if current_sum + value > value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        if current_sum < best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return SubarrayResult(best_start, best_end, best_sum)


def maximum_circular_subarray(values: list[int]) -> int | None:
    """
    Maximum subarray sum in a circular array.

    Two cases:
    1. The best subarray does not wrap: ordinary Kadane.
    2. The best subarray wraps: total_sum - minimum_subarray_sum.

    Special case:
    If all values are negative, total_sum - minimum_sum becomes zero,
    which would represent an empty subarray. The correct answer is the
    largest single element instead.
    """
    if not values:
        return None

    normal = maximum_subarray_kadane(values)
    minimum = minimum_subarray_kadane(values)

    assert normal is not None
    assert minimum is not None

    if normal.value < 0:
        return normal.value

    total = sum(values)
    wrapped = total - minimum.value

    return max(normal.value, wrapped)


# ============================================================
# 8. PREFIX SUM + HASHING ADVANCED PATTERNS
# ============================================================

def longest_subarray_sum_k(values: list[int], target: int) -> int:
    """
    Longest subarray with sum exactly target.

    Prefix sums + earliest occurrence.

    If prefix[j] - prefix[i] = target,
    then prefix[i] = prefix[j] - target.

    We retain the earliest index for every prefix sum because
    an earlier occurrence gives the longest possible range.

    Time: O(n) average.
    """
    earliest: dict[int, int] = {0: -1}
    prefix = 0
    best = 0

    for index, value in enumerate(values):
        prefix += value

        if prefix - target in earliest:
            best = max(best, index - earliest[prefix - target])

        if prefix not in earliest:
            earliest[prefix] = index

    return best


def subarray_divisible_by_k_count(values: list[int], k: int) -> int:
    """
    Count subarrays whose sum is divisible by k.

    Two prefix sums have the same remainder modulo k exactly when
    their difference is divisible by k.

    Python's modulo operator produces a non-negative remainder for
    positive k, which makes the frequency map straightforward.
    """
    if k <= 0:
        raise ValueError("k must be positive.")

    remainder_frequency = defaultdict(int)
    remainder_frequency[0] = 1

    prefix = 0
    count = 0

    for value in values:
        prefix += value
        remainder = prefix % k

        count += remainder_frequency[remainder]
        remainder_frequency[remainder] += 1

    return count


def count_subarrays_with_equal_zero_one(binary_values: list[int]) -> int:
    """
    Count binary subarrays containing an equal number of zeros and ones.

    Transform:
        0 -> -1
        1 -> +1

    Then the problem becomes counting equal prefix sums.
    """
    if any(value not in (0, 1) for value in binary_values):
        raise ValueError("Input must contain only 0 and 1.")

    frequency = defaultdict(int)
    frequency[0] = 1

    balance = 0
    count = 0

    for value in binary_values:
        balance += 1 if value == 1 else -1

        count += frequency[balance]
        frequency[balance] += 1

    return count


# ============================================================
# 9. SORTING-BASED SUBARRAY PATTERNS
# ============================================================

def pair_sum_sorting(values: list[int], target: int) -> bool:
    """
    Determine whether a pair sums to target using sorting.

    Time: O(n log n)
    Extra space: O(n) because sorted() creates a new list.
    """
    ordered = sorted(values)

    left = 0
    right = len(ordered) - 1

    while left < right:
        total = ordered[left] + ordered[right]

        if total == target:
            return True
        if total < target:
            left += 1
        else:
            right -= 1

    return False


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Sorting-based interval merging.

    Intervals are not subarrays, but the same ordering principle is
    important in array problem solving: sort first to establish structure.
    """
    if not intervals:
        return []

    normalized = []

    for start, end in intervals:
        if start > end:
            raise ValueError("Interval start cannot exceed end.")
        normalized.append((start, end))

    normalized.sort()

    merged = [normalized[0]]

    for start, end in normalized[1:]:
        previous_start, previous_end = merged[-1]

        if start <= previous_end:
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))

    return merged


# ============================================================
# 10. BINARY SEARCH ON PREFIX SUMS FOR NON-NEGATIVE ARRAYS
# ============================================================

def shortest_subarray_sum_at_least_k_nonnegative_binary_search(
    values: list[int], target: int
) -> int:
    """
    Find shortest subarray with sum >= target using prefix sums + binary search.

    Requires non-negative values because prefix sums must be non-decreasing.

    Time: O(n log n)
    Space: O(n)

    This is educationally useful because it contrasts with the O(n)
    sliding-window solution for the same restricted problem.
    """
    if target <= 0:
        raise ValueError("Target must be positive.")

    if any(value < 0 for value in values):
        raise ValueError("Values must be non-negative.")

    prefix = build_prefix_sum(values)
    best = len(values) + 1

    for right in range(1, len(prefix)):
        required = prefix[right] - target

        # Find the first prefix position whose value is greater than
        # or equal to required. Because prefix is sorted, binary search
        # can identify the earliest valid left boundary.
        left = bisect_left(prefix, required + 1, 0, right)

        # The previous position may be the exact target boundary.
        exact = bisect_left(prefix, required, 0, right)

        candidates = [left, exact]

        for candidate in candidates:
            if candidate < right and prefix[right] - prefix[candidate] >= target:
                best = min(best, right - candidate)

    return 0 if best == len(values) + 1 else best


# ============================================================
# 11. DIFFERENCE BETWEEN SUBARRAY, SUBSEQUENCE AND SUBSET
# ============================================================

def demonstrate_relationships() -> None:
    print("\n=== SUBARRAY VS SUBSEQUENCE VS SUBSET ===")

    values = [1, 2, 3]

    print("Original:", values)
    print("Subarray example:", [2, 3])
    print("Subsequence example:", [1, 3])
    print("Subset example:", [1, 3])

    print(
        "The same values [1, 3] can be a subsequence or subset, "
        "but it is not a subarray."
    )

    print("Number of non-empty subarrays:", count_subarrays(len(values)))
    print("Number of non-empty subsets:", 2 ** len(values) - 1)


# ============================================================
# 12. EDGE CASES
# ============================================================

def edge_case_tests() -> None:
    print("\n=== EDGE CASES ===")

    cases = {
        "empty": [],
        "single": [7],
        "all_positive": [1, 2, 3],
        "all_negative": [-5, -2, -9],
        "mixed": [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        "zeros": [0, 0, 0],
        "duplicates": [2, 2, 2, 2],
    }

    for name, values in cases.items():
        result = maximum_subarray_kadane(values)
        print(f"{name:14}: {values} -> {result}")

    print("\nZero-target count:", subarray_sum_equals_k_hashing([0, 0, 0], 0))
    print("Single element:", maximum_subarray_kadane([42]))
    print("All negative:", maximum_subarray_kadane([-8, -3, -5]))

    try:
        maximum_sum_fixed_window([1, 2], 3)
    except ValueError as error:
        print("Invalid window correctly rejected:", error)

    try:
        minimum_size_subarray_sum_positive([2, -1, 3], 3)
    except ValueError as error:
        print("Invalid sliding-window assumption correctly rejected:", error)


# ============================================================
# 13. VERIFICATION USING DIFFERENT ALGORITHMS
# ============================================================

def verify_maximum_subarray_implementations() -> None:
    """
    Compare an O(n^2) reference implementation against Kadane's O(n)
    implementation on many deterministic test cases.

    Using a slower but simple implementation as an oracle is a valuable
    debugging and testing technique.
    """
    test_cases = [
        [],
        [1],
        [-1],
        [1, 2, 3],
        [-1, -2, -3],
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        [0, 0, 0],
        [5, -10, 5],
        [-5, 10, -2, 3, -20, 8],
    ]

    for values in test_cases:
        brute = maximum_subarray_bruteforce(values)
        fast = maximum_subarray_kadane(values)

        if brute is None or fast is None:
            assert brute is None and fast is None
        else:
            assert brute.value == fast.value, (
                f"Mismatch for {values}: {brute} != {fast}"
            )

    print("\nAll maximum-subarray verification tests passed.")


# ============================================================
# 14. PERFORMANCE COMPARISON
# ============================================================

def benchmark_algorithm(
    name: str,
    function: Callable[..., object],
    *args: object,
) -> None:
    """Measure a function without requiring third-party libraries."""
    import time

    start = time.perf_counter()
    result = function(*args)
    elapsed = time.perf_counter() - start

    print(f"{name:35} {elapsed:.6f}s | result={result}")


def performance_demo() -> None:
    print("\n=== PERFORMANCE COMPARISON ===")

    values = [((index * 17) % 101) - 50 for index in range(800)]

    # The quadratic method is intentionally kept at a manageable input size.
    benchmark_algorithm(
        "Maximum subarray O(n^2)",
        maximum_subarray_bruteforce,
        values,
    )

    benchmark_algorithm(
        "Maximum subarray O(n) Kadane",
        maximum_subarray_kadane,
        values,
    )

    larger_values = [((index * 13) % 31) - 15 for index in range(50_000)]

    benchmark_algorithm(
        "Maximum subarray O(n) on 50,000",
        maximum_subarray_kadane,
        larger_values,
    )


# ============================================================
# 15. PRACTICAL CASE STUDY: DAILY CASH FLOW
# ============================================================

def best_profit_period(daily_changes: list[int]) -> SubarrayResult | None:
    """
    Model daily changes in profit/loss.

    A positive number means improvement.
    A negative number means deterioration.

    The maximum-sum subarray identifies the contiguous period with
    the greatest accumulated improvement.
    """
    return maximum_subarray_kadane(daily_changes)


def cash_flow_case_study() -> None:
    print("\n=== PRACTICAL CASE STUDY: CASH FLOW ===")

    daily_changes = [12, -5, 18, -20, 25, 14, -3, 7, -30, 15]

    result = best_profit_period(daily_changes)

    print("Daily changes:", daily_changes)

    if result:
        print("Best period:", daily_changes[result.start:result.end + 1])
        print("Period indices:", result.start, "to", result.end)
        print("Accumulated change:", result.value)


# ============================================================
# 16. ADVANCED PATTERN SELECTION
# ============================================================

def choose_array_pattern(
    *,
    needs_contiguous_range: bool,
    array_is_sorted: bool,
    fixed_window_size: bool,
    values_nonnegative: bool,
    exact_sum_with_negatives: bool,
) -> str:
    """
    A small rule-based decision helper.

    This is not a universal decision engine. It demonstrates how problem
    constraints determine algorithm choice.
    """
    if exact_sum_with_negatives:
        return "Prefix sum + hashing"

    if fixed_window_size:
        return "Fixed-size sliding window"

    if needs_contiguous_range and values_nonnegative:
        return "Variable-size sliding window"

    if array_is_sorted:
        return "Two pointers"

    if needs_contiguous_range:
        return "Prefix sums or Kadane, depending on objective"

    return "Clarify whether sorting, hashing, or another structure is appropriate"


# ============================================================
# 17. MAIN DEMONSTRATION
# ============================================================

def main() -> None:
    print("=" * 72)
    print("DAY 18 — SUBARRAYS AND ARRAY PATTERNS")
    print("=" * 72)

    explain_subarray()

    print("\n=== SUBARRAY ENUMERATION ===")
    values = [2, -1, 3]

    print("Array:", values)
    print("Number of non-empty subarrays:", count_subarrays(len(values)))

    for start, end, subarray in enumerate_subarrays(values):
        print(f"[{start}, {end}] -> {subarray}")

    print("\nOnly ranges:")
    print(enumerate_subarray_ranges(values))

    print("\n=== SUBARRAY SUMS ===")
    print("Brute-force sums:")
    print(all_subarray_sums_bruteforce(values))

    print("\nIncremental O(n^2) sums:")
    print(all_subarray_sums_incremental(values))

    prefix_sum_demo()

    print("\n=== PREFIX SUM + HASHING ===")
    sample = [1, 2, 3, -2, 2, 1]
    target = 3

    print("Array:", sample)
    print("Target:", target)
    print(
        "Brute-force count:",
        subarray_sum_equals_k_bruteforce(sample, target),
    )
    print(
        "Hashing count:",
        subarray_sum_equals_k_hashing(sample, target),
    )

    print(
        "Longest subarray with target sum:",
        longest_subarray_sum_k([10, 5, 2, 7, 1, 9], 15),
    )

    print(
        "Longest zero-sum subarray:",
        longest_zero_sum_subarray([15, -2, 2, -8, 1, 7, 10, 23]),
    )

    print("\n=== HASHING ===")
    numbers = [2, 7, 11, 15]
    print("Two-sum:", two_sum_hashing(numbers, 9))
    print("Frequencies:", frequency_table([1, 2, 2, 3, 3, 3]))

    print("\n=== TWO POINTERS ===")
    sorted_values = [1, 2, 3, 4, 6, 8, 10]
    print(
        "Pair in sorted array:",
        two_pointer_pair_sum_sorted(sorted_values, 14),
    )
    print(
        "Pair after sorting:",
        two_pointer_pair_sum_unsorted([8, 1, 6, 10, 4], 14),
    )
    print(
        "Unique values:",
        remove_duplicates_sorted([1, 1, 2, 2, 3, 3, 3, 4]),
    )
    print(
        "Maximum container area:",
        container_with_most_water([1, 8, 6, 2, 5, 4, 8, 3, 7]),
    )

    print("\n=== SLIDING WINDOWS ===")
    window_values = [2, 1, 5, 1, 3, 2]
    print(
        "Maximum fixed-window sum:",
        maximum_sum_fixed_window(window_values, 3),
    )
    print(
        "Minimum positive-sum window:",
        minimum_size_subarray_sum_positive([2, 3, 1, 2, 4, 3], 7),
    )
    print(
        "Longest at most 2 distinct:",
        longest_subarray_at_most_k_distinct(
            [1, 2, 1, 2, 3],
            2,
        ),
    )
    print(
        "Longest non-negative sum <= 5:",
        longest_subarray_sum_at_most_k_nonnegative(
            [1, 2, 1, 1, 3],
            5,
        ),
    )

    print("\n=== MAXIMUM AND MINIMUM SUBARRAY ===")
    mixed = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    print("Array:", mixed)
    print("Maximum:", maximum_subarray_kadane(mixed))
    print("Minimum:", minimum_subarray_kadane(mixed))
    print("Circular maximum:", maximum_circular_subarray(mixed))

    print("\n=== ADVANCED PREFIX PATTERNS ===")
    print(
        "Subarrays divisible by 5:",
        subarray_divisible_by_k_count([4, 5, 0, -2, -3, 1], 5),
    )
    print(
        "Equal zeros and ones:",
        count_subarrays_with_equal_zero_one([0, 1, 0, 1, 1, 0]),
    )

    print("\n=== SORTING-BASED PATTERNS ===")
    print("Pair exists:", pair_sum_sorting([7, 1, 5, 3, 6, 4], 10))
    print(
        "Merged intervals:",
        merge_intervals([(1, 3), (2, 6), (8, 10), (9, 12)]),
    )

    print("\n=== NON-NEGATIVE PREFIX SUM + BINARY SEARCH ===")
    print(
        "Shortest sum >= 7:",
        shortest_subarray_sum_at_least_k_nonnegative_binary_search(
            [2, 3, 1, 2, 4, 3],
            7,
        ),
    )

    demonstrate_relationships()
    edge_case_tests()
    verify_maximum_subarray_implementations()

    print("\n=== PATTERN SELECTION ===")
    print(
        choose_array_pattern(
            needs_contiguous_range=True,
            array_is_sorted=False,
            fixed_window_size=False,
            values_nonnegative=False,
            exact_sum_with_negatives=True,
        )
    )

    cash_flow_case_study()
    performance_demo()

    print("\n" + "=" * 72)
    print("END OF DAY 18 PRACTICE")
    print("=" * 72)


if __name__ == "__main__":
    main()
