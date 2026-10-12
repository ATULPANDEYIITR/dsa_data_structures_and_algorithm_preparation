#!/usr/bin/env python3
"""Monotonic stacks: increasing/decreasing stacks and next-element queries.

Run with:
    python monotonic_stack.py

The examples use only the Python standard library and include reference
implementations, index-based algorithms, circular arrays, range boundaries,
histogram analysis, and automated correctness checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence
import random


def next_greater_right(values: Sequence[int]) -> list[int | None]:
    """Return the first strictly greater value to the right of each element.

    The stack stores indices whose unresolved values decrease from bottom
    to top. Each new value resolves every smaller value at the stack top.
    Time: O(n); auxiliary space: O(n).
    """
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            result[stack.pop()] = value
        stack.append(i)

    return result


def next_greater_indices(values: Sequence[int]) -> list[int | None]:
    """Return indices of the next strictly greater elements."""
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            result[stack.pop()] = i
        stack.append(i)

    return result


def next_greater_left(values: Sequence[int]) -> list[int | None]:
    """Return the nearest strictly greater value on the left."""
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] <= value:
            stack.pop()
        if stack:
            result[i] = values[stack[-1]]
        stack.append(i)

    return result


def next_smaller_right(values: Sequence[int]) -> list[int | None]:
    """Return the first strictly smaller value to the right."""
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] > value:
            result[stack.pop()] = value
        stack.append(i)

    return result


def next_smaller_indices(values: Sequence[int]) -> list[int | None]:
    """Return indices of the next strictly smaller elements."""
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] > value:
            result[stack.pop()] = i
        stack.append(i)

    return result


def next_smaller_left(values: Sequence[int]) -> list[int | None]:
    """Return the nearest strictly smaller value on the left."""
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] >= value:
            stack.pop()
        if stack:
            result[i] = values[stack[-1]]
        stack.append(i)

    return result


def next_greater_circular(values: Sequence[int]) -> list[int | None]:
    """Find next greater values while treating the array as circular.

    Each original index is pushed only during the first pass. The second
    pass can resolve outstanding elements but does not duplicate indices.
    """
    n = len(values)
    result: list[int | None] = [None] * n
    stack: list[int] = []

    for i in range(2 * n):
        index = i % n
        while stack and values[stack[-1]] < values[index]:
            result[stack.pop()] = values[index]
        if i < n:
            stack.append(index)

    return result


def daily_temperatures(temperatures: Sequence[int]) -> list[int]:
    """Days until a strictly warmer temperature; zero if none exists."""
    answer = [0] * len(temperatures)
    stack: list[int] = []

    for day, temperature in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temperature:
            previous_day = stack.pop()
            answer[previous_day] = day - previous_day
        stack.append(day)

    return answer


def stock_span(prices: Sequence[int]) -> list[int]:
    """For each day, count consecutive previous days with price <= today's."""
    spans: list[int] = [0] * len(prices)
    stack: list[int] = []

    for day, price in enumerate(prices):
        while stack and prices[stack[-1]] <= price:
            stack.pop()
        spans[day] = day - stack[-1] if stack else day + 1
        stack.append(day)

    return spans


def largest_histogram_rectangle(heights: Sequence[int]) -> int:
    """Find the largest rectangle in a histogram in O(n) time.

    A non-negative height is required. A virtual zero-height bar flushes
    the remaining stack without modifying the original input.
    """
    if any(height < 0 for height in heights):
        raise ValueError("Histogram heights must be non-negative")

    best = 0
    stack: list[int] = []
    n = len(heights)

    for i in range(n + 1):
        current_height = heights[i] if i < n else 0

        while stack and heights[stack[-1]] > current_height:
            height = heights[stack.pop()]
            left_boundary = stack[-1] if stack else -1
            width = i - left_boundary - 1
            best = max(best, height * width)

        stack.append(i)

    return best


def maximal_rectangle(matrix: Sequence[Sequence[str]]) -> int:
    """Largest all-'1' rectangle in a rectangular binary matrix."""
    if not matrix:
        return 0

    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("Matrix must be rectangular")

    heights = [0] * columns
    best = 0

    for row in matrix:
        for column, cell in enumerate(row):
            if cell not in ("0", "1"):
                raise ValueError("Matrix cells must be '0' or '1'")
            heights[column] = heights[column] + 1 if cell == "1" else 0
        best = max(best, largest_histogram_rectangle(heights))

    return best


@dataclass(frozen=True)
class BoundaryResult:
    """Nearest strictly smaller boundaries around each histogram bar."""

    left: tuple[int, ...]
    right: tuple[int, ...]


def histogram_boundaries(heights: Sequence[int]) -> BoundaryResult:
    """Return exclusive smaller-bar boundaries as index sentinels.

    left[i] is the nearest smaller index or -1.
    right[i] is the nearest smaller index or len(heights).
    Equal heights are retained as valid candidates because the boundary
    is strictly smaller.
    """
    if any(height < 0 for height in heights):
        raise ValueError("Histogram heights must be non-negative")

    n = len(heights)
    left = [-1] * n
    right = [n] * n
    stack: list[int] = []

    for i, height in enumerate(heights):
        while stack and heights[stack[-1]] >= height:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)

    stack.clear()

    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)

    return BoundaryResult(tuple(left), tuple(right))


def next_element_brute_force(
    values: Sequence[int],
    *,
    greater: bool,
    direction: str = "right",
) -> list[int | None]:
    """Quadratic reference algorithm for testing monotonic-stack results."""
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")

    answer: list[int | None] = [None] * len(values)

    for i, value in enumerate(values):
        candidates = (
            range(i + 1, len(values))
            if direction == "right"
            else range(i - 1, -1, -1)
        )

        for j in candidates:
            condition = values[j] > value if greater else values[j] < value
            if condition:
                answer[i] = values[j]
                break

    return answer


def print_table(
    values: Sequence[int],
    results: dict[str, Sequence[int | None]],
) -> None:
    """Print aligned data without requiring a tabulation dependency."""
    print("Index:", list(range(len(values))))
    print("Value:", list(values))
    for label, result in results.items():
        print(f"{label}: {list(result)}")


def demonstrate_core_patterns() -> None:
    print("\n=== Increasing and decreasing stack patterns ===")

    values = [4, 2, 2, 7, 3, 6, 1, 8]
    print_table(
        values,
        {
            "Next greater right": next_greater_right(values),
            "Next smaller right": next_smaller_right(values),
            "Next greater left": next_greater_left(values),
            "Next smaller left": next_smaller_left(values),
        },
    )

    print("\n=== Index-based results ===")
    print("Next greater indices:", next_greater_indices(values))
    print("Next smaller indices:", next_smaller_indices(values))

    # An increasing stack pops larger elements when a smaller value arrives.
    increasing_stack: list[int] = []
    for value in [3, 5, 5, 2, 4]:
        while increasing_stack and increasing_stack[-1] > value:
            increasing_stack.pop()
        increasing_stack.append(value)
    print("Non-decreasing stack after processing [3, 5, 5, 2, 4]:",
          increasing_stack)

    # A decreasing stack pops smaller elements when a larger value arrives.
    decreasing_stack: list[int] = []
    for value in [3, 5, 5, 2, 4]:
        while decreasing_stack and decreasing_stack[-1] < value:
            decreasing_stack.pop()
        decreasing_stack.append(value)
    print("Non-increasing stack after processing [3, 5, 5, 2, 4]:",
          decreasing_stack)


def demonstrate_applications() -> None:
    print("\n=== Real-world monotonic-stack applications ===")

    temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
    print("Temperatures:", temperatures)
    print("Days until warmer:", daily_temperatures(temperatures))

    prices = [100, 80, 60, 70, 60, 75, 85]
    print("Stock prices:", prices)
    print("Stock span:", stock_span(prices))

    circular = [1, 2, 1]
    print("Circular array:", circular)
    print("Circular next greater:", next_greater_circular(circular))

    histogram = [2, 1, 5, 6, 2, 3]
    boundaries = histogram_boundaries(histogram)
    print("Histogram heights:", histogram)
    print("Nearest smaller left:", list(boundaries.left))
    print("Nearest smaller right:", list(boundaries.right))
    print("Largest rectangle:", largest_histogram_rectangle(histogram))

    matrix = [
        ["1", "0", "1", "0", "0"],
        ["1", "0", "1", "1", "1"],
        ["1", "1", "1", "1", "1"],
        ["1", "0", "0", "1", "0"],
    ]
    print("Largest all-ones matrix rectangle:", maximal_rectangle(matrix))


def run_tests() -> None:
    """Check edge cases and compare linear algorithms against brute force."""
    assert next_greater_right([]) == []
    assert next_smaller_right([]) == []
    assert next_greater_circular([]) == []
    assert next_greater_right([5, 5, 5]) == [None, None, None]
    assert next_smaller_right([5, 5, 5]) == [None, None, None]
    assert next_greater_right([2, 1, 3]) == [3, 3, None]
    assert next_smaller_right([2, 3, 1]) == [1, 1, None]
    assert next_greater_left([2, 1, 3]) == [None, 2, None]
    assert next_smaller_left([2, 3, 1]) == [None, 2, None]
    assert next_greater_indices([2, 1, 3]) == [2, 2, None]
    assert next_smaller_indices([2, 3, 1]) == [2, 2, None]
    assert next_greater_circular([1, 2, 1]) == [2, None, 2]
    assert daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
    assert stock_span([100, 80, 60, 70, 60, 75, 85]) == [
        1, 1, 1, 2, 1, 4, 6
    ]
    assert largest_histogram_rectangle([]) == 0
    assert largest_histogram_rectangle([2, 2, 2]) == 6
    assert largest_histogram_rectangle([2, 1, 5, 6, 2, 3]) == 10
    assert maximal_rectangle([]) == 0
    assert maximal_rectangle([["1", "1"], ["1", "1"]]) == 4
    assert maximal_rectangle([["0", "0"]]) == 0

    try:
        largest_histogram_rectangle([2, -1])
    except ValueError:
        pass
    else:
        raise AssertionError("Negative histogram heights must be rejected")

    try:
        maximal_rectangle([["1"], ["1", "0"]])
    except ValueError:
        pass
    else:
        raise AssertionError("Ragged matrices must be rejected")

    rng = random.Random(20261012)
    for _ in range(500):
        values = [rng.randint(-10, 10) for _ in range(rng.randint(0, 25))]
        assert next_greater_right(values) == next_element_brute_force(
            values, greater=True
        )
        assert next_smaller_right(values) == next_element_brute_force(
            values, greater=False
        )
        assert next_greater_left(values) == next_element_brute_force(
            values, greater=True, direction="left"
        )
        assert next_smaller_left(values) == next_element_brute_force(
            values, greater=False, direction="left"
        )

    print("\nAll deterministic and randomized tests passed.")


def main() -> None:
    demonstrate_core_patterns()
    demonstrate_applications()
    run_tests()


if __name__ == "__main__":
    main()
