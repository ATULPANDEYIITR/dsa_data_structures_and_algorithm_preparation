#!/usr/bin/env python3
"""Generate subsets, handle duplicates, solve subset-sum, and apply constraints."""

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Iterator


@dataclass(frozen=True)
class SubsetResult:
    values: tuple[int, ...]
    total: int


def validate_integers(values: Iterable[int]) -> list[int]:
    """Reject booleans and non-integer values."""
    result = list(values)
    if any(type(value) is not int for value in result):
        raise TypeError("Every element must be an integer.")
    return result


def generate_subsets(values: Iterable[int]) -> list[list[int]]:
    """Generate all index-distinct subsets in O(n * 2^n) output work."""
    items = validate_integers(values)
    result: list[list[int]] = [[]]

    for value in items:
        result += [subset + [value] for subset in result]

    return result


def unique_subsets(values: Iterable[int]) -> list[list[int]]:
    """Generate unique value-based subsets in lexicographic DFS order."""
    items = sorted(validate_integers(values))
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int) -> None:
        result.append(path.copy())

        for index in range(start, len(items)):
            if index > start and items[index] == items[index - 1]:
                continue

            path.append(items[index])
            backtrack(index + 1)
            path.pop()

    backtrack(0)
    return result


def subset_sum(
    values: Iterable[int],
    target: int,
) -> list[list[int]]:
    """Find unique value-based subsets summing to target."""
    if type(target) is not int:
        raise TypeError("Target must be an integer.")

    items = sorted(validate_integers(values))
    result: list[list[int]] = []
    path: list[int] = []

    def search(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path.copy())
            # Continue searching: zeros can extend a valid subset.
            # Duplicate skipping ensures each value combination is unique.

        for index in range(start, len(items)):
            if index > start and items[index] == items[index - 1]:
                continue

            path.append(items[index])
            search(index + 1, remaining - items[index])
            path.pop()

    search(0, target)
    return result


def constrained_subsets(
    values: Iterable[int],
    min_size: int = 0,
    max_size: int | None = None,
    min_sum: int | None = None,
    max_sum: int | None = None,
    predicate: Callable[[tuple[int, ...]], bool] | None = None,
) -> list[SubsetResult]:
    """Filter subsets using size, sum, and an optional custom predicate."""
    items = validate_integers(values)
    n = len(items)

    if max_size is None:
        max_size = n

    if not 0 <= min_size <= max_size <= n:
        raise ValueError("Require 0 <= min_size <= max_size <= input size.")

    if min_sum is not None and type(min_sum) is not int:
        raise TypeError("min_sum must be an integer or None.")

    if max_sum is not None and type(max_sum) is not int:
        raise TypeError("max_sum must be an integer or None.")

    if min_sum is not None and max_sum is not None and min_sum > max_sum:
        raise ValueError("min_sum cannot exceed max_sum.")

    result: list[SubsetResult] = []
    path: list[int] = []

    def search(index: int, total: int) -> None:
        if len(path) > max_size:
            return

        if index == n:
            if len(path) < min_size:
                return
            if min_sum is not None and total < min_sum:
                return
            if max_sum is not None and total > max_sum:
                return

            candidate = tuple(path)
            if predicate is None or predicate(candidate):
                result.append(SubsetResult(candidate, total))
            return

        search(index + 1, total)

        path.append(items[index])
        search(index + 1, total + items[index])
        path.pop()

    search(0, 0)
    return result


def subset_sum_exists(values: Iterable[int], target: int) -> bool:
    """Use a set of reachable sums for a decision-only query."""
    if type(target) is not int:
        raise TypeError("Target must be an integer.")

    items = validate_integers(values)
    reachable = {0}

    for value in items:
        reachable |= {subtotal + value for subtotal in reachable}
        if target in reachable:
            return True

    return target == 0


def main() -> None:
    values = [1, 2, 2, 3]

    print("All index-distinct subsets:")
    print(generate_subsets(values))

    print("\nUnique value-based subsets:")
    print(unique_subsets(values))

    print("\nSubsets summing to 4:")
    print(subset_sum(values, 4))

    print("\nSubsets with size 2-3 and sum 4-6:")
    for item in constrained_subsets(
        values, min_size=2, max_size=3, min_sum=4, max_sum=6
    ):
        print(item)

    print("\nSubset sum 7 exists:", subset_sum_exists(values, 7))

    assert len(generate_subsets([])) == 1
    assert generate_subsets([]) == [[]]
    assert unique_subsets([1, 1]) == [[], [1], [1, 1]]
    assert subset_sum([1, 2, 2, 3], 4) == [[1, 3], [2, 2]]
    assert subset_sum([0, 0], 0) == [[], [0], [0, 0]]
    assert subset_sum_exists([-3, 1, 2], 0)
    assert not subset_sum_exists([2, 4], 3)

    try:
        generate_subsets([1, True])
    except TypeError as error:
        print("\nValidation caught:", error)

    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
