"""
Day 17 — Kadane's Algorithm
============================

A comprehensive, executable study of maximum-subarray problems.

The central problem is:

    Given an array of integers, find a contiguous subarray whose sum is
    as large as possible.

Kadane's algorithm solves the basic problem in O(n) time and O(1) auxiliary
space.

This file progresses from:
    1. Definitions and terminology
    2. Brute-force solutions
    3. Running sums
    4. Kadane's algorithm
    5. Negative-only arrays
    6. Index reconstruction
    7. Tie-breaking
    8. Minimum subarray
    9. Maximum circular subarray
    10. Maximum subarray with one deletion
    11. Fixed-length windows
    12. Variable-length constrained variants
    13. Prefix-sum interpretation
    14. Divide-and-conquer comparison
    15. Streaming computation
    16. Testing and verification
    17. Performance considerations
    18. Practical applications

The program uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from random import Random
from typing import Iterable, Optional, Sequence


# ---------------------------------------------------------------------------
# 1. Fundamental terminology
# ---------------------------------------------------------------------------

"""
Array:
    A sequence of values accessed by index.

Subarray:
    A contiguous portion of an array.

Subsequence:
    A sequence obtained by deleting zero or more elements without changing
    the relative order. A subsequence does not have to be contiguous.

For example:
    data = [4, -2, 7, 1]

    [4, -2, 7] is a subarray.
    [4, 7] is a subsequence, but not a subarray.

Kadane's algorithm specifically solves a contiguous-subarray problem.
"""


def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_result(label: str, value: object) -> None:
    """Print a labeled result."""
    print(f"{label:<36}: {value}")


# ---------------------------------------------------------------------------
# 2. Basic subarray enumeration
# ---------------------------------------------------------------------------

def all_subarrays(values: Sequence[int]) -> list[tuple[int, int, list[int]]]:
    """
    Return every non-empty contiguous subarray.

    Each result contains:
        (start_index, end_index, subarray_values)

    This is intentionally simple and educational rather than optimal.
    """
    result: list[tuple[int, int, list[int]]] = []

    for start in range(len(values)):
        for end in range(start, len(values)):
            result.append((start, end, list(values[start:end + 1])))

    return result


# ---------------------------------------------------------------------------
# 3. Brute-force maximum subarray: O(n^3)
# ---------------------------------------------------------------------------

def maximum_subarray_cubic(values: Sequence[int]) -> tuple[int, int, int]:
    """
    Find the maximum-sum non-empty subarray in O(n^3).

    Complexity:
        Number of subarrays = O(n^2)
        Computing each sum from scratch = O(n)
        Total = O(n^3)

    This implementation is useful because it makes the definition explicit.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    best_sum = values[0]
    best_start = 0
    best_end = 0

    for start in range(len(values)):
        for end in range(start, len(values)):
            current_sum = 0

            for index in range(start, end + 1):
                current_sum += values[index]

            if current_sum > best_sum:
                best_sum = current_sum
                best_start = start
                best_end = end

    return best_sum, best_start, best_end


# ---------------------------------------------------------------------------
# 4. Brute-force maximum subarray using a running sum: O(n^2)
# ---------------------------------------------------------------------------

def maximum_subarray_quadratic(values: Sequence[int]) -> tuple[int, int, int]:
    """
    Find the maximum-sum non-empty subarray in O(n^2).

    The sum for a fixed start index is extended incrementally.

    Instead of repeatedly calculating:
        values[start] + ... + values[end]

    we maintain:
        current_sum += values[end]

    This is the first important running-sum optimization.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    best_sum = values[0]
    best_start = 0
    best_end = 0

    for start in range(len(values)):
        current_sum = 0

        for end in range(start, len(values)):
            current_sum += values[end]

            if current_sum > best_sum:
                best_sum = current_sum
                best_start = start
                best_end = end

    return best_sum, best_start, best_end


# ---------------------------------------------------------------------------
# 5. Kadane's algorithm
# ---------------------------------------------------------------------------

def kadane(values: Sequence[int]) -> int:
    """
    Return the maximum sum of a non-empty contiguous subarray.

    Core recurrence:

        current = max(value, current + value)
        best = max(best, current)

    Interpretation:
        At every position, decide whether the best subarray ending here is:

            1. the current element alone, or
            2. the previous best subarray ending at the previous position
               extended by the current element.

    Complexity:
        Time:  O(n)
        Space: O(1)

    Important:
        The initialization uses values[0], not zero. This ensures that
        all-negative arrays are handled correctly.

        Example:
            [-8, -3, -10]

        Correct answer = -3

        A careless implementation initialized with zero would incorrectly
        return 0, which represents an empty subarray.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    current_sum = values[0]
    best_sum = values[0]

    for value in values[1:]:
        current_sum = max(value, current_sum + value)
        best_sum = max(best_sum, current_sum)

    return best_sum


# ---------------------------------------------------------------------------
# 6. Kadane's algorithm with index reconstruction
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SubarrayResult:
    """Represent a maximum-subarray result."""

    total: int
    start: int
    end: int
    values: tuple[int, ...]

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def kadane_with_indices(values: Sequence[int]) -> SubarrayResult:
    """
    Return the maximum subarray, including its indices and values.

    The reset decision is:

        if current_sum + value < value:
            start a new subarray at this value

    Otherwise extend the current candidate.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    current_sum = values[0]
    best_sum = values[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(values)):
        value = values[index]

        if value > current_sum + value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return SubarrayResult(
        total=best_sum,
        start=best_start,
        end=best_end,
        values=tuple(values[best_start:best_end + 1]),
    )


# ---------------------------------------------------------------------------
# 7. Why the reset decision works
# ---------------------------------------------------------------------------

def explain_reset_decision(values: Sequence[int]) -> None:
    """
    Print Kadane's state after every element.

    This makes the algorithm's local decision visible.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    current_sum = values[0]
    best_sum = values[0]

    print(f"{'Index':>5} {'Value':>8} {'Current':>12} {'Best':>12} {'Decision'}")
    print("-" * 62)
    print(f"{0:>5} {values[0]:>8} {current_sum:>12} {best_sum:>12} {'start'}")

    for index in range(1, len(values)):
        value = values[index]
        extended = current_sum + value

        if value > extended:
            current_sum = value
            decision = "reset"
        else:
            current_sum = extended
            decision = "extend"

        best_sum = max(best_sum, current_sum)

        print(
            f"{index:>5} {value:>8} {current_sum:>12} "
            f"{best_sum:>12} {decision}"
        )


# ---------------------------------------------------------------------------
# 8. Tie-breaking policies
# ---------------------------------------------------------------------------

def kadane_prefer_earlier(
    values: Sequence[int],
) -> SubarrayResult:
    """
    Prefer the earliest start index when multiple subarrays have the same sum.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    current_sum = values[0]
    best_sum = values[0]
    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(values)):
        value = values[index]

        if value > current_sum + value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return SubarrayResult(
        best_sum,
        best_start,
        best_end,
        tuple(values[best_start:best_end + 1]),
    )


def kadane_prefer_shorter_on_tie(
    values: Sequence[int],
) -> SubarrayResult:
    """
    Maximize sum first; among equal sums, prefer the shorter subarray.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    current_sum = values[0]
    current_start = 0

    best_sum = values[0]
    best_start = 0
    best_end = 0

    for index in range(1, len(values)):
        value = values[index]

        if value > current_sum + value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        current_length = index - current_start + 1
        best_length = best_end - best_start + 1

        if (
            current_sum > best_sum
            or (
                current_sum == best_sum
                and current_length < best_length
            )
        ):
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return SubarrayResult(
        best_sum,
        best_start,
        best_end,
        tuple(values[best_start:best_end + 1]),
    )


# ---------------------------------------------------------------------------
# 9. Minimum subarray
# ---------------------------------------------------------------------------

def minimum_subarray(values: Sequence[int]) -> SubarrayResult:
    """
    Find the minimum-sum non-empty contiguous subarray.

    This is Kadane's algorithm with max replaced by min.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    current_sum = values[0]
    best_sum = values[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(values)):
        value = values[index]

        if value < current_sum + value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        if current_sum < best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return SubarrayResult(
        best_sum,
        best_start,
        best_end,
        tuple(values[best_start:best_end + 1]),
    )


# ---------------------------------------------------------------------------
# 10. Maximum circular subarray
# ---------------------------------------------------------------------------

def maximum_circular_subarray(values: Sequence[int]) -> SubarrayResult:
    """
    Find the maximum-sum subarray when the array is circular.

    There are two possibilities:

        Case A:
            The best subarray does not wrap.
            Use ordinary Kadane.

        Case B:
            The best subarray wraps around the end.
            Its sum is:

                total_sum - minimum_subarray_sum

    Special case:
        If every element is negative, the minimum-subarray calculation would
        effectively remove the entire array. A non-empty result is required,
        so the ordinary Kadane result must be returned.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    normal = kadane_with_indices(values)

    if normal.total < 0:
        return normal

    minimum = minimum_subarray(values)
    wrapped_sum = sum(values) - minimum.total

    if wrapped_sum <= normal.total:
        return normal

    # The wrapped subarray consists of:
    #   values[minimum.end + 1:] + values[:minimum.start]
    wrapped_values = tuple(
        values[minimum.end + 1:] + values[:minimum.start]
    )

    return SubarrayResult(
        wrapped_sum,
        minimum.end + 1,
        minimum.start - 1,
        wrapped_values,
    )


# ---------------------------------------------------------------------------
# 11. Maximum subarray with one deletion
# ---------------------------------------------------------------------------

def maximum_subarray_one_deletion(values: Sequence[int]) -> int:
    """
    Maximum subarray sum when at most one element may be deleted.

    Dynamic-programming states:

        keep:
            best sum ending here without deleting an element.

        delete:
            best sum ending here after deleting exactly one element.

    Transitions:

        new_keep = max(value, keep + value)

        new_delete = max(
            delete + value,  # deletion happened earlier
            keep             # delete current value
        )
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    keep = values[0]
    delete = float("-inf")
    best = values[0]

    for value in values[1:]:
        new_delete = max(delete + value, keep)
        new_keep = max(value, keep + value)

        keep = new_keep
        delete = new_delete

        best = max(best, keep, delete)

    return int(best)


# ---------------------------------------------------------------------------
# 12. Maximum subarray with at most k deletions
# ---------------------------------------------------------------------------

def maximum_subarray_k_deletions(
    values: Sequence[int],
    k: int,
) -> int:
    """
    Generalize the deletion problem to at most k deletions.

    State:
        dp[d] = best sum of a subarray ending at the current position after
                exactly d deletions.

    For every value:
        - keep it: dp[d] + value
        - delete it: previous dp[d - 1]

    Complexity:
        Time: O(nk)
        Space: O(k)

    This is a useful example of how the two-state one-deletion solution
    generalizes into a small dynamic-programming state vector.
    """
    if not values:
        raise ValueError("The input array must not be empty.")
    if k < 0:
        raise ValueError("k must be non-negative.")

    k = min(k, len(values) - 1)

    negative_infinity = float("-inf")
    dp = [negative_infinity] * (k + 1)
    dp[0] = values[0]

    best = values[0]

    for value in values[1:]:
        previous = dp[:]

        dp[0] = max(value, previous[0] + value)

        for deletions in range(1, k + 1):
            dp[deletions] = max(
                previous[deletions] + value,
                previous[deletions - 1],
            )

        best = max(best, *dp)

    return int(best)


# ---------------------------------------------------------------------------
# 13. Maximum subarray of exactly k elements
# ---------------------------------------------------------------------------

def maximum_fixed_length_subarray(
    values: Sequence[int],
    length: int,
) -> tuple[int, int, int]:
    """
    Find the maximum sum of a subarray having exactly `length` elements.

    This is a fixed-size sliding-window problem, not ordinary Kadane.

    Complexity:
        Time: O(n)
        Space: O(1)
    """
    if length <= 0:
        raise ValueError("The window length must be positive.")
    if length > len(values):
        raise ValueError("The window length cannot exceed the array length.")

    current_sum = sum(values[:length])
    best_sum = current_sum
    best_start = 0

    for start in range(1, len(values) - length + 1):
        current_sum += values[start + length - 1]
        current_sum -= values[start - 1]

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = start

    return best_sum, best_start, best_start + length - 1


# ---------------------------------------------------------------------------
# 14. Maximum subarray with sum at least a threshold
# ---------------------------------------------------------------------------

def maximum_length_subarray_at_most_sum(
    values: Sequence[int],
    limit: int,
) -> Optional[tuple[int, int, int]]:
    """
    For non-negative values only, find the longest contiguous subarray
    whose sum is <= limit.

    This is not a Kadane problem. It demonstrates an important distinction:
    algorithm choice depends on constraints and objective.

    A sliding window works because all values are non-negative.
    Negative values would invalidate the monotonicity assumption.
    """
    if any(value < 0 for value in values):
        raise ValueError(
            "This sliding-window implementation requires non-negative values."
        )

    left = 0
    current_sum = 0
    best: Optional[tuple[int, int, int]] = None

    for right, value in enumerate(values):
        current_sum += value

        while left <= right and current_sum > limit:
            current_sum -= values[left]
            left += 1

        if left <= right:
            length = right - left + 1

            if best is None or length > best[0]:
                best = (length, left, right)

    return best


# ---------------------------------------------------------------------------
# 15. Prefix-sum interpretation of maximum subarray
# ---------------------------------------------------------------------------

def maximum_subarray_prefix_sum(values: Sequence[int]) -> int:
    """
    Solve maximum subarray using prefix sums.

    Let:

        P[i] = sum(values[:i])

    Then the sum from j through i - 1 is:

        P[i] - P[j]

    To maximize this value while scanning i, maintain the smallest prefix
    sum seen before i.

    Complexity:
        Time: O(n)
        Space: O(1) beyond the input.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    prefix_sum = 0
    minimum_prefix = 0
    best_sum = values[0]

    for value in values:
        prefix_sum += value
        best_sum = max(best_sum, prefix_sum - minimum_prefix)
        minimum_prefix = min(minimum_prefix, prefix_sum)

    return best_sum


# ---------------------------------------------------------------------------
# 16. Divide-and-conquer maximum subarray
# ---------------------------------------------------------------------------

def maximum_subarray_divide_and_conquer(
    values: Sequence[int],
) -> tuple[int, int, int]:
    """
    Solve maximum subarray using divide and conquer.

    A maximum subarray in a range is one of:

        1. Entirely in the left half.
        2. Entirely in the right half.
        3. Crossing the midpoint.

    Complexity:
        Time: O(n log n)
        Space: O(log n) recursion stack.

    Kadane is asymptotically faster, but divide-and-conquer is important
    because it exposes the structural reasoning behind the problem.
    """
    if not values:
        raise ValueError("The input array must not be empty.")

    def solve(left: int, right: int) -> tuple[int, int, int]:
        if left == right:
            return values[left], left, right

        middle = (left + right) // 2

        left_result = solve(left, middle)
        right_result = solve(middle + 1, right)
        crossing_result = crossing_sum(left, middle, right)

        return max(
            left_result,
            right_result,
            crossing_result,
            key=lambda result: result[0],
        )

    def crossing_sum(
        left: int,
        middle: int,
        right: int,
    ) -> tuple[int, int, int]:
        left_sum = float("-inf")
        running = 0
        best_left = middle

        for index in range(middle, left - 1, -1):
            running += values[index]

            if running > left_sum:
                left_sum = running
                best_left = index

        right_sum = float("-inf")
        running = 0
        best_right = middle + 1

        for index in range(middle + 1, right + 1):
            running += values[index]

            if running > right_sum:
                right_sum = running
                best_right = index

        return int(left_sum + right_sum), best_left, best_right

    return solve(0, len(values) - 1)


# ---------------------------------------------------------------------------
# 17. Streaming Kadane
# ---------------------------------------------------------------------------

class StreamingKadane:
    """
    Maintain a maximum-subarray result while values arrive one at a time.

    This demonstrates that the basic Kadane state can be maintained without
    storing the complete array.

    State:
        current_sum
        best_sum
        current_start
        best_start
        best_end
        position

    The first value establishes the non-empty-subarray state.
    """

    def __init__(self) -> None:
        self.current_sum: Optional[int] = None
        self.best_sum: Optional[int] = None
        self.current_start = 0
        self.best_start = 0
        self.best_end = 0
        self.position = -1

    def add(self, value: int) -> None:
        self.position += 1

        if self.current_sum is None:
            self.current_sum = value
            self.best_sum = value
            self.current_start = self.position
            self.best_start = self.position
            self.best_end = self.position
            return

        assert self.best_sum is not None

        if value > self.current_sum + value:
            self.current_sum = value
            self.current_start = self.position
        else:
            self.current_sum += value

        if self.current_sum > self.best_sum:
            self.best_sum = self.current_sum
            self.best_start = self.current_start
            self.best_end = self.position

    def result(self) -> SubarrayResult:
        """Return the best result observed so far."""
        if self.best_sum is None:
            raise ValueError("No values have been added.")

        return SubarrayResult(
            total=self.best_sum,
            start=self.best_start,
            end=self.best_end,
            values=(),
        )


# ---------------------------------------------------------------------------
# 18. Profit interpretation
# ---------------------------------------------------------------------------

def maximum_profit_from_daily_changes(changes: Sequence[int]) -> int:
    """
    Interpret daily price changes as gains/losses.

    A positive-sum contiguous interval represents a period with net positive
    movement. Kadane can identify the strongest such interval.

    This is an educational mathematical analogy, not a complete trading
    strategy.
    """
    return kadane(changes)


# ---------------------------------------------------------------------------
# 19. Generic Kadane over arbitrary numeric values
# ---------------------------------------------------------------------------

def generic_kadane(
    values: Iterable[float],
) -> float:
    """
    Kadane for real-valued numeric data.

    The iterable is materialized because the algorithm needs the first value
    for correct non-empty initialization.

    For huge streaming sources, StreamingKadane avoids materializing input.
    """
    data = list(values)

    if not data:
        raise ValueError("The input iterable must contain at least one value.")

    current = data[0]
    best = data[0]

    for value in data[1:]:
        current = max(value, current + value)
        best = max(best, current)

    return best


# ---------------------------------------------------------------------------
# 20. Input validation
# ---------------------------------------------------------------------------

def validate_integer_sequence(values: Sequence[int]) -> None:
    """Validate assumptions used by integer-array demonstrations."""
    if not values:
        raise ValueError("Array must not be empty.")

    if any(not isinstance(value, int) or isinstance(value, bool)
           for value in values):
        raise TypeError("Every array element must be an integer.")


# ---------------------------------------------------------------------------
# 21. Property-style verification against brute force
# ---------------------------------------------------------------------------

def verify_against_brute_force(
    values: Sequence[int],
) -> bool:
    """
    Verify Kadane's answer against the cubic reference implementation.
    """
    brute_force = maximum_subarray_cubic(values)[0]
    linear = kadane(values)
    return brute_force == linear


def run_randomized_verification(
    seed: int = 17,
    trials: int = 500,
) -> None:
    """
    Compare multiple implementations on randomly generated small arrays.

    Randomized verification is valuable because it tests many combinations
    of positive, negative, and zero values.
    """
    rng = Random(seed)

    for _ in range(trials):
        length = rng.randint(1, 20)
        values = [rng.randint(-20, 20) for _ in range(length)]

        brute = maximum_subarray_cubic(values)[0]
        quadratic = maximum_subarray_quadratic(values)[0]
        linear = kadane(values)
        prefix = maximum_subarray_prefix_sum(values)
        divide_and_conquer = maximum_subarray_divide_and_conquer(values)[0]

        if not (
            brute
            == quadratic
            == linear
            == prefix
            == divide_and_conquer
        ):
            raise AssertionError(
                "Implementation mismatch for "
                f"{values}: {brute}, {quadratic}, {linear}, "
                f"{prefix}, {divide_and_conquer}"
            )

    print_result("Randomized verification", f"{trials} trials passed")


# ---------------------------------------------------------------------------
# 22. Complexity comparison
# ---------------------------------------------------------------------------

def complexity_table() -> None:
    """Print a conceptual complexity comparison."""
    rows = [
        ("Cubic brute force", "O(n^3)", "O(1)", "Definition-level reference"),
        ("Quadratic running sum", "O(n^2)", "O(1)", "Simple optimization"),
        ("Kadane", "O(n)", "O(1)", "Standard maximum-subarray solution"),
        ("Prefix-sum scan", "O(n)", "O(1)", "Alternative derivation"),
        ("Divide and conquer", "O(n log n)", "O(log n)", "Structural approach"),
        ("Circular Kadane", "O(n)", "O(1)", "Circular array variant"),
        ("One deletion DP", "O(n)", "O(1)", "One optional deletion"),
        ("k-deletion DP", "O(nk)", "O(k)", "Generalized deletion state"),
    ]

    print(f"{'Method':<28} {'Time':<10} {'Space':<10} {'Purpose'}")
    print("-" * 86)

    for method, time, space, purpose in rows:
        print(f"{method:<28} {time:<10} {space:<10} {purpose}")


# ---------------------------------------------------------------------------
# 23. Practical example: sensor health score
# ---------------------------------------------------------------------------

def sensor_health_interval(
    hourly_changes: Sequence[int],
) -> SubarrayResult:
    """
    Identify the strongest contiguous positive interval in a sequence of
    sensor-derived score changes.

    In a real system, the values could represent normalized changes in a
    service health metric. The mathematical operation remains the same.
    """
    return kadane_with_indices(hourly_changes)


# ---------------------------------------------------------------------------
# 24. Demonstrate edge cases
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Exercise important edge conditions."""
    cases = {
        "single positive": [7],
        "single negative": [-7],
        "all positive": [2, 4, 1, 8],
        "all negative": [-8, -3, -10, -4],
        "mixed": [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        "zeros": [0, 0, 0],
        "positive and zeros": [0, 5, 0, -1, 0],
        "alternating": [10, -10, 10, -10, 10],
        "large negative separator": [5, -100, 6, 7],
    }

    for name, values in cases.items():
        result = kadane_with_indices(values)
        print_result(
            name,
            f"sum={result.total}, indices={result.start}..{result.end}, "
            f"subarray={list(result.values)}",
        )


# ---------------------------------------------------------------------------
# 25. Demonstrate common mistakes
# ---------------------------------------------------------------------------

def incorrect_empty_allowed_kadane(values: Sequence[int]) -> int:
    """
    A deliberately flawed implementation.

    Starting at zero solves a different problem: maximum sum where selecting
    nothing is allowed. For the standard non-empty problem this is incorrect
    for all-negative arrays.
    """
    current = 0
    best = 0

    for value in values:
        current = max(0, current + value)
        best = max(best, current)

    return best


def demonstrate_common_mistake() -> None:
    """Show why zero initialization can be wrong."""
    values = [-9, -4, -12]

    print_result(
        "Correct non-empty result",
        kadane(values),
    )

    print_result(
        "Incorrect empty-allowed result",
        incorrect_empty_allowed_kadane(values),
    )

    print(
        "\nThe second result is not the standard Kadane answer because "
        "the standard problem requires a non-empty subarray."
    )


# ---------------------------------------------------------------------------
# 26. Unit-style tests
# ---------------------------------------------------------------------------

def run_unit_tests() -> None:
    """Run deterministic tests covering core variants."""
    assert kadane([1, 2, 3]) == 6
    assert kadane([-5, -2, -9]) == -2
    assert kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6

    result = kadane_with_indices(
        [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    )
    assert result.total == 6
    assert result.values == (4, -1, 2, 1)

    assert minimum_subarray([3, -4, 2, -3, -1, 7]) .total == -6
    assert maximum_subarray_one_deletion([1, -2, 0, 3]) == 4
    assert maximum_subarray_one_deletion([-1, -1, -1]) == -1

    assert maximum_subarray_k_deletions(
        [1, -2, 0, 3],
        1,
    ) == 4

    assert maximum_fixed_length_subarray(
        [2, -1, 5, -3, 4],
        3,
    ) == (6, 0, 2)

    assert maximum_subarray_prefix_sum(
        [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    ) == 6

    assert maximum_subarray_divide_and_conquer(
        [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    )[0] == 6

    assert incorrect_empty_allowed_kadane([-4, -2]) == 0

    try:
        kadane([])
    except ValueError:
        pass
    else:
        raise AssertionError("Empty input should raise ValueError.")

    try:
        maximum_fixed_length_subarray([1, 2], 3)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid window length should raise ValueError.")

    print_result("Deterministic unit tests", "all passed")


# ---------------------------------------------------------------------------
# 27. Main educational demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("Day 17 — Kadane's Algorithm")

    print(
        "Goal: find the maximum sum of a non-empty contiguous subarray "
        "in linear time."
    )

    print_section("1. Basic example")

    values = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    print_result("Input", values)
    print_result(
        "Cubic brute force",
        maximum_subarray_cubic(values),
    )
    print_result(
        "Quadratic running sum",
        maximum_subarray_quadratic(values),
    )
    print_result(
        "Kadane",
        kadane(values),
    )
    print_result(
        "Kadane with indices",
        kadane_with_indices(values),
    )

    print_section("2. Running state")

    explain_reset_decision(values)

    print_section("3. Edge cases")

    demonstrate_edge_cases()

    print_section("4. Common initialization mistake")

    demonstrate_common_mistake()

    print_section("5. Minimum subarray")

    values = [3, -4, 2, -3, -1, 7]
    print_result("Input", values)
    print_result("Minimum subarray", minimum_subarray(values))

    print_section("6. Circular maximum subarray")

    circular_cases = [
        [5, -3, 5],
        [3, -2, 2, -3],
        [-3, -2, -1],
        [1, 2, 3, 4],
    ]

    for case in circular_cases:
        print_result(
            f"Input {case}",
            maximum_circular_subarray(case),
        )

    print_section("7. One deletion")

    deletion_cases = [
        [1, -2, 0, 3],
        [1, -2, -2, 3],
        [-1, -1, -1],
        [8, -1, 6, -10, 5],
    ]

    for case in deletion_cases:
        print_result(
            f"Input {case}",
            maximum_subarray_one_deletion(case),
        )

    print_section("8. k deletions")

    values = [5, -100, 6, 7, -2, 4]

    for k in range(4):
        print_result(
            f"k={k}",
            maximum_subarray_k_deletions(values, k),
        )

    print_section("9. Fixed-length window")

    values = [2, -1, 5, -3, 4, 6, -2]
    print_result("Input", values)

    for length in (1, 2, 3, 4):
        print_result(
            f"Length={length}",
            maximum_fixed_length_subarray(values, length),
        )

    print_section("10. Non-negative sliding-window contrast")

    values = [2, 1, 3, 1, 1, 2]
    print_result("Input", values)
    print_result(
        "Longest sum <= 6",
        maximum_length_subarray_at_most_sum(values, 6),
    )

    print_section("11. Prefix-sum formulation")

    values = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    print_result(
        "Kadane",
        kadane(values),
    )
    print_result(
        "Prefix-sum formulation",
        maximum_subarray_prefix_sum(values),
    )

    print_section("12. Divide-and-conquer formulation")

    print_result(
        "Divide and conquer",
        maximum_subarray_divide_and_conquer(values),
    )

    print_section("13. Streaming computation")

    stream = StreamingKadane()

    for value in values:
        stream.add(value)
        print_result(
            f"After adding {value}",
            stream.result(),
        )

    print_section("14. Tie-breaking")

    tie_values = [4, -2, 2, 4, -4, 6, -6]

    print_result(
        "Default",
        kadane_prefer_earlier(tie_values),
    )
    print_result(
        "Prefer shorter on tie",
        kadane_prefer_shorter_on_tie(tie_values),
    )

    print_section("15. Practical score-change interpretation")

    changes = [-3, 4, -1, 2, 1, -8, 5, 2]
    print_result("Changes", changes)
    print_result(
        "Best interval",
        sensor_health_interval(changes),
    )

    print_section("16. Complexity comparison")

    complexity_table()

    print_section("17. Unit tests")

    run_unit_tests()

    print_section("18. Randomized verification")

    run_randomized_verification()

    print_section("19. Key algorithmic invariant")

    print(
        "At index i, current_sum represents the largest possible sum of a "
        "non-empty subarray that ends exactly at i. best_sum represents the "
        "largest sum found anywhere from index 0 through i."
    )

    print_section("20. Practical rules")

    rules = [
        "A subarray must be contiguous.",
        "For the standard problem, the subarray is non-empty.",
        "Initialize from the first value when empty selection is not allowed.",
        "At each element, choose between starting fresh and extending.",
        "Use indices when the actual subarray is required, not just its sum.",
        "For circular arrays, combine ordinary Kadane with minimum-subarray logic.",
        "For deletion variants, expand the state rather than forcing ordinary Kadane.",
        "Do not confuse fixed-window problems with unconstrained maximum subarray.",
        "Use sliding windows only when their monotonicity assumptions hold.",
        "Validate empty input and constraints explicitly.",
        "For very large streams, maintain only the necessary Kadane state.",
    ]

    for number, rule in enumerate(rules, start=1):
        print(f"{number:>2}. {rule}")


if __name__ == "__main__":
    main()
