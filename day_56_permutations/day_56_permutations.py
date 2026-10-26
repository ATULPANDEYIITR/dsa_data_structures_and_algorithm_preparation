from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence
from collections import Counter
import math


class PermutationError(ValueError):
    """Raised when permutation input violates the supported constraints."""


@dataclass(frozen=True)
class PermutationStats:
    input_size: int
    unique_permutations: int
    generated_permutations: int
    method: str


def validate_sequence(items: Sequence[object]) -> None:
    if items is None:
        raise PermutationError("Input sequence must not be None.")
    if len(items) > 9:
        raise PermutationError(
            "Input is too large for exhaustive permutation generation; "
            "maximum supported size is 9."
        )


def permutation_count(items: Sequence[object]) -> int:
    """Return n! / product(count(x)!) for inputs containing duplicates."""
    validate_sequence(items)
    counts = Counter(items)
    result = math.factorial(len(items))
    for count in counts.values():
        result //= math.factorial(count)
    return result


def permutations_used_array(items: Sequence[object]) -> Iterator[tuple[object, ...]]:
    """
    Generate permutations using a used-array.

    Duplicate values are handled at each recursion depth by skipping a value
    that has already been selected at that depth.
    """
    validate_sequence(items)

    values = sorted(items, key=lambda value: (type(value).__name__, repr(value)))
    used = [False] * len(values)
    current: list[object] = []

    def backtrack() -> Iterator[tuple[object, ...]]:
        if len(current) == len(values):
            yield tuple(current)
            return

        previous = object()
        has_previous = False

        for index, value in enumerate(values):
            if used[index]:
                continue

            if has_previous and value == previous:
                continue

            previous = value
            has_previous = True
            used[index] = True
            current.append(value)

            yield from backtrack()

            current.pop()
            used[index] = False

    yield from backtrack()


def permutations_swap(items: Sequence[object]) -> Iterator[tuple[object, ...]]:
    """
    Generate permutations using in-place swapping.

    Sorting first makes duplicate handling deterministic. At each recursion
    depth, only the first occurrence of a value is placed in that position.
    """
    validate_sequence(items)

    values = sorted(items, key=lambda value: (type(value).__name__, repr(value)))

    def backtrack(start: int) -> Iterator[tuple[object, ...]]:
        if start == len(values):
            yield tuple(values)
            return

        used_at_level: set[object] = set()

        for index in range(start, len(values)):
            value = values[index]

            try:
                already_seen = value in used_at_level
            except TypeError as exc:
                raise PermutationError(
                    "Swap-based duplicate handling requires hashable values."
                ) from exc

            if already_seen:
                continue

            used_at_level.add(value)
            values[start], values[index] = values[index], values[start]

            yield from backtrack(start + 1)

            values[start], values[index] = values[index], values[start]

    yield from backtrack(0)


def permutations_distinct(items: Sequence[object]) -> Iterator[tuple[object, ...]]:
    """Generate permutations only when all input values are distinct."""
    validate_sequence(items)

    if len(set(items)) != len(items):
        raise PermutationError(
            "permutations_distinct requires all input values to be distinct."
        )

    values = list(items)
    yield from _swap_distinct(values, 0)


def _swap_distinct(values: list[object], start: int) -> Iterator[tuple[object, ...]]:
    if start == len(values):
        yield tuple(values)
        return

    for index in range(start, len(values)):
        values[start], values[index] = values[index], values[start]
        yield from _swap_distinct(values, start + 1)
        values[start], values[index] = values[index], values[start]


def generate_stats(
    items: Sequence[object],
    method: str,
    generator: Iterable[tuple[object, ...]],
) -> PermutationStats:
    generated = sum(1 for _ in generator)
    return PermutationStats(
        input_size=len(items),
        unique_permutations=permutation_count(items),
        generated_permutations=generated,
        method=method,
    )


def main() -> None:
    examples = [
        ("ABC", list("ABC")),
        ("AAB", list("AAB")),
        ("ABCD", list("ABCD")),
    ]

    for name, values in examples:
        print(f"\n{name}")
        print(f"Unique permutation count: {permutation_count(values)}")

        swap_result = list(permutations_swap(values))
        used_result = list(permutations_used_array(values))

        print("Swap-based:")
        print(swap_result)

        print("Used-array:")
        print(used_result)

        assert len(swap_result) == permutation_count(values)
        assert len(used_result) == permutation_count(values)
        assert set(swap_result) == set(used_result)

    print("\nDistinct-only example:")
    print(list(permutations_distinct(["A", "B", "C"])))

    print("\nEdge case: empty sequence")
    print(list(permutations_used_array([])))
    assert permutation_count([]) == 1

    print("\nValidation example:")
    try:
        list(permutations_distinct(["A", "A"]))
    except PermutationError as exc:
        print(f"Rejected correctly: {exc}")

    print("\nComplexity:")
    print("For n distinct values, n! permutations are produced.")
    print("Generating every permutation requires O(n × n!) output work.")
    print("Recursive auxiliary state is O(n).")


if __name__ == "__main__":
    main()
