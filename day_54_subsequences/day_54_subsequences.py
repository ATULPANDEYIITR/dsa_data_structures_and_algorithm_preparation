#!/usr/bin/env python3
"""Generate, analyze, and count subsequences using executable examples."""

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Iterator, Sequence


class SubsequenceError(ValueError):
    """Raised when a subsequence operation receives invalid input."""


def validate_sequence(values: Sequence[int]) -> None:
    if isinstance(values, (str, bytes)):
        raise SubsequenceError("Expected a sequence of integers, not text.")
    if not all(isinstance(value, int) and not isinstance(value, bool)
               for value in values):
        raise SubsequenceError("Every element must be an integer.")


def generate_subsequences(values: Sequence[int]) -> list[list[int]]:
    """Generate every subsequence, preserving original element order."""
    validate_sequence(values)
    result: list[list[int]] = []

    def backtrack(index: int, current: list[int]) -> None:
        if index == len(values):
            result.append(current.copy())
            return

        # Exclude the current element.
        backtrack(index + 1, current)

        # Include the current element.
        current.append(values[index])
        backtrack(index + 1, current)
        current.pop()

    backtrack(0, [])
    return result


def iter_subsequences(values: Sequence[int]) -> Iterator[tuple[int, ...]]:
    """Yield subsequences lazily to avoid storing all results."""
    validate_sequence(values)
    current: list[int] = []

    def visit(index: int) -> Iterator[tuple[int, ...]]:
        if index == len(values):
            yield tuple(current)
            return

        yield from visit(index + 1)

        current.append(values[index])
        yield from visit(index + 1)
        current.pop()

    yield from visit(0)


def subsequence_sum(values: Sequence[int], target: int) -> bool:
    """Return whether any subsequence has the requested sum."""
    validate_sequence(values)

    # Reachable sums support negative and positive integers.
    reachable = {0}
    for value in values:
        reachable |= {total + value for total in reachable}
        if target in reachable:
            return True
    return target == 0


def count_subsequences_with_sum(
    values: Sequence[int], target: int
) -> int:
    """Count index-distinct subsequences whose sum equals target."""
    validate_sequence(values)
    counts = {0: 1}

    for value in values:
        updated = counts.copy()
        for total, count in counts.items():
            new_total = total + value
            updated[new_total] = updated.get(new_total, 0) + count
        counts = updated

    return counts.get(target, 0)


def count_subsequences_matching(
    values: Sequence[int], predicate: Callable[[tuple[int, ...]], bool]
) -> int:
    """Count subsequences satisfying an arbitrary predicate."""
    return sum(1 for item in iter_subsequences(values) if predicate(item))


def count_nonempty_subsequences_at_most(
    values: Sequence[int], limit: int
) -> int:
    """
    Count nonempty subsequences whose minimum + maximum <= limit.

    This optimized method requires nonnegative or negative integers alike;
    sorting works for any integers. Equal values at different indices remain
    distinct choices, as in index-based subsequence counting.
    """
    validate_sequence(values)
    ordered = sorted(values)
    left, right = 0, len(ordered) - 1
    answer = 0
    powers = [1] * (len(ordered) + 1)

    for index in range(1, len(powers)):
        powers[index] = powers[index - 1] * 2

    while left <= right:
        if ordered[left] + ordered[right] <= limit:
            answer += powers[right - left]
            left += 1
        else:
            right -= 1

    return answer


@dataclass(frozen=True)
class SubsequenceReport:
    input_values: tuple[int, ...]
    target: int
    exists: bool
    count: int
    total_subsequences: int


def analyze(values: Sequence[int], target: int) -> SubsequenceReport:
    validate_sequence(values)
    return SubsequenceReport(
        input_values=tuple(values),
        target=target,
        exists=subsequence_sum(values, target),
        count=count_subsequences_with_sum(values, target),
        total_subsequences=1 << len(values),
    )


def main() -> None:
    values = [1, 2, 3]
    target = 3

    print("Input:", values)
    print("Subsequences:")
    for sequence in iter_subsequences(values):
        print(list(sequence))

    report = analyze(values, target)
    print("\nTarget sum:", report.target)
    print("Exists:", report.exists)
    print("Count:", report.count)
    print("Total subsequences:", report.total_subsequences)
    print("Nonempty subsequences with sum 3:",
          count_subsequences_matching(
              values, lambda item: bool(item) and sum(item) == 3
          ))
    print("Minimum + maximum <= 4:",
          count_nonempty_subsequences_at_most(values, 4))

    # Empty input has exactly one subsequence: the empty subsequence.
    assert generate_subsequences([]) == [[]]
    assert count_subsequences_with_sum([], 0) == 1
    assert count_subsequences_with_sum([], 1) == 0
    assert count_subsequences_with_sum([1, 2, 3], 3) == 2
    assert count_subsequences_with_sum([0, 0], 0) == 4
    assert subsequence_sum([-2, 5], 3)
    assert count_nonempty_subsequences_at_most([3, 5, 6, 7], 9) == 4

    try:
        generate_subsequences([1, "2"])  # type: ignore[list-item]
    except SubsequenceError as error:
        print("Validation caught:", error)


if __name__ == "__main__":
    main()
