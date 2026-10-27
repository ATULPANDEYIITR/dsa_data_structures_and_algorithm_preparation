from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Decision(Enum):
    CHOOSE = "choose"
    SKIP = "skip"


@dataclass
class CombinationResult:
    values: list[int]
    total: int


@dataclass
class CombinationEngine:
    numbers: list[int]
    target: int
    allow_reuse: bool = False
    results: list[CombinationResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.target, int):
            raise TypeError("target must be an integer")
        if not all(isinstance(value, int) for value in self.numbers):
            raise TypeError("numbers must contain integers")

        self.numbers = sorted(set(self.numbers))

        if any(value <= 0 for value in self.numbers):
            raise ValueError("numbers must contain only positive integers")

    def generate_fixed_size(self, size: int) -> list[list[int]]:
        """Generate every size-element combination without repetition."""
        if size < 0:
            raise ValueError("size cannot be negative")

        output: list[list[int]] = []
        path: list[int] = []

        def backtrack(start: int) -> None:
            if len(path) == size:
                output.append(path.copy())
                return

            remaining = size - len(path)
            if len(self.numbers) - start < remaining:
                return

            for index in range(start, len(self.numbers)):
                path.append(self.numbers[index])
                backtrack(index + 1)
                path.pop()

        if size == 0:
            return [[]]

        backtrack(0)
        return output

    def combination_sum(self) -> list[CombinationResult]:
        """
        Find combinations whose values add to target.

        With allow_reuse=False, each value can be used once.
        With allow_reuse=True, a value may be selected repeatedly.
        """
        if self.target < 0:
            return []

        output: list[CombinationResult] = []
        path: list[int] = []

        def search(start: int, remaining: int) -> None:
            if remaining == 0:
                output.append(
                    CombinationResult(path.copy(), self.target)
                )
                return

            for index in range(start, len(self.numbers)):
                value = self.numbers[index]

                if value > remaining:
                    break

                path.append(value)

                next_index = index if self.allow_reuse else index + 1
                search(next_index, remaining - value)

                path.pop()

        search(0, self.target)
        self.results = output
        return output

    def constrained_combinations(
        self,
        size: int,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> list[list[int]]:
        """
        Generate fixed-size combinations subject to sum constraints.

        The search prunes branches whose partial sum already exceeds
        maximum and branches that cannot possibly reach the minimum.
        """
        if size < 0:
            raise ValueError("size cannot be negative")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("minimum cannot exceed maximum")

        output: list[list[int]] = []
        path: list[int] = []

        def smallest_possible_sum(start: int, count: int) -> int | None:
            if len(self.numbers) - start < count:
                return None
            return sum(self.numbers[start:start + count])

        def search(start: int, current_sum: int) -> None:
            remaining_slots = size - len(path)

            if remaining_slots == 0:
                if (
                    (minimum is None or current_sum >= minimum)
                    and (maximum is None or current_sum <= maximum)
                ):
                    output.append(path.copy())
                return

            if len(self.numbers) - start < remaining_slots:
                return

            lower_bound = smallest_possible_sum(start, remaining_slots)
            if lower_bound is None:
                return

            if minimum is not None and current_sum + lower_bound > maximum if maximum is not None else False:
                pass

            if maximum is not None and current_sum + lower_bound > maximum:
                return

            for index in range(start, len(self.numbers)):
                value = self.numbers[index]
                next_sum = current_sum + value

                if maximum is not None and next_sum > maximum:
                    break

                path.append(value)
                search(index + 1, next_sum)
                path.pop()

        if size == 0:
            if (
                (minimum is None or 0 >= minimum)
                and (maximum is None or 0 <= maximum)
            ):
                return [[]]
            return []

        search(0, 0)
        return output


def choose_or_skip(items: list[str]) -> list[list[str]]:
    """Classic binary recursion: every item is either chosen or skipped."""
    output: list[list[str]] = []
    path: list[str] = []

    def search(index: int) -> None:
        if index == len(items):
            output.append(path.copy())
            return

        # Choose.
        path.append(items[index])
        search(index + 1)
        path.pop()

        # Skip.
        search(index + 1)

    search(0)
    return output


def unique_combinations_with_duplicates(
    values: Iterable[int],
    size: int,
) -> list[list[int]]:
    """
    Generate unique combinations from input that may contain duplicates.

    Sorting allows duplicate values to be skipped at the same recursion
    depth while still allowing the same value at different depths.
    """
    values = sorted(values)

    if size < 0:
        raise ValueError("size cannot be negative")

    output: list[list[int]] = []
    path: list[int] = []

    def search(start: int) -> None:
        if len(path) == size:
            output.append(path.copy())
            return

        for index in range(start, len(values)):
            if index > start and values[index] == values[index - 1]:
                continue

            path.append(values[index])
            search(index + 1)
            path.pop()

    if size == 0:
        return [[]]

    search(0)
    return output


def validate_results(results: list[list[int]], target: int) -> None:
    """Executable assertions useful for debugging recursive algorithms."""
    for combination in results:
        assert sum(combination) == target
        assert combination == sorted(combination)


def main() -> None:
    items = ["A", "B", "C"]
    subsets = choose_or_skip(items)

    print("Choose/not choose:")
    for subset in subsets:
        print(subset)

    engine = CombinationEngine([2, 3, 5, 7], target=10)

    print("\nFixed-size combinations of size 2:")
    print(engine.generate_fixed_size(2))

    print("\nCombination sum without reuse:")
    no_reuse = engine.combination_sum()
    for result in no_reuse:
        print(result.values)

    reusable = CombinationEngine(
        [2, 3, 5],
        target=8,
        allow_reuse=True,
    )

    print("\nCombination sum with reuse:")
    reusable_results = reusable.combination_sum()
    for result in reusable_results:
        print(result.values)

    validate_results(
        [result.values for result in reusable_results],
        8,
    )

    print("\nConstraint-based recursion:")
    constrained = engine.constrained_combinations(
        size=3,
        minimum=12,
        maximum=15,
    )
    print(constrained)

    print("\nDuplicate-safe combinations:")
    print(unique_combinations_with_duplicates([1, 1, 2, 2, 3], 2))

    # Important edge cases.
    assert choose_or_skip([]) == [[]]
    assert engine.generate_fixed_size(0) == [[]]
    assert engine.generate_fixed_size(10) == []
    assert unique_combinations_with_duplicates([], 0) == [[]]

    try:
        CombinationEngine([1, 0, 2], 3)
    except ValueError as exc:
        print(f"\nValidation correctly rejected input: {exc}")

    # Complexity:
    # choose_or_skip creates O(2^n) subsets.
    # Fixed-size combinations create O(C(n, k)) results.
    # Combination-sum search is exponential in the worst case, but
    # sorting and positive values enable early pruning.
    print("\nCompleted combination-problem demonstrations.")


if __name__ == "__main__":
    main()
