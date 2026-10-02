#!/usr/bin/env python3
"""
Quick Sort: pivot selection, partitioning, recursive partitioning,
worst-case behavior, and comparison with merge sort.

The program is self-contained and executable with Python's standard library.
It demonstrates:
- Lomuto and Hoare partitioning
- Several pivot strategies
- Recursive quick sort
- Worst-case behavior on already ordered data
- Recursion-depth considerations
- Three-way partitioning for duplicate-heavy data
- Merge sort for comparison
- Correctness validation
- Instrumentation for comparisons, swaps, and recursion depth
- Practical performance measurements
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import sys
import time
from typing import Callable, List, Sequence, Tuple


@dataclass
class SortStats:
    """Collect operational information while a sorting algorithm runs."""

    comparisons: int = 0
    swaps: int = 0
    recursive_calls: int = 0
    max_recursion_depth: int = 0

    def reset(self) -> None:
        self.comparisons = 0
        self.swaps = 0
        self.recursive_calls = 0
        self.max_recursion_depth = 0


def validate_numeric_sequence(values: Sequence[int]) -> None:
    """
    Validate that the input contains comparable integers.

    Quick sort itself only requires an ordering relation, but this teaching
    implementation deliberately restricts the examples to integers so that
    the algorithms can focus on partitioning behavior.
    """
    if not isinstance(values, Sequence):
        raise TypeError("values must be a sequence")

    for value in values:
        if not isinstance(value, int):
            raise TypeError(f"quick sort example expects integers, got {type(value).__name__}")


def is_sorted(values: Sequence[int]) -> bool:
    """Return True when values are in non-decreasing order."""
    return all(values[index] <= values[index + 1] for index in range(len(values) - 1))


def swap(values: List[int], left: int, right: int, stats: SortStats | None = None) -> None:
    """Swap two elements and optionally count the operation."""
    if left == right:
        return

    values[left], values[right] = values[right], values[left]

    if stats is not None:
        stats.swaps += 1


def lomuto_partition(
    values: List[int],
    low: int,
    high: int,
    stats: SortStats | None = None,
) -> int:
    """
    Partition values[low:high + 1] using the Lomuto scheme.

    The final element is used as the pivot. After partitioning:
      values[low:pivot_index] <= pivot
      values[pivot_index] == pivot
      values[pivot_index + 1:high + 1] > pivot

    Lomuto is easy to understand but can perform poorly when its fixed pivot
    choice repeatedly creates highly unbalanced partitions.
    """
    pivot = values[high]
    smaller_boundary = low

    for current in range(low, high):
        if stats is not None:
            stats.comparisons += 1

        if values[current] <= pivot:
            swap(values, smaller_boundary, current, stats)
            smaller_boundary += 1

    swap(values, smaller_boundary, high, stats)
    return smaller_boundary


def quick_sort_lomuto(
    values: List[int],
    stats: SortStats | None = None,
    low: int = 0,
    high: int | None = None,
    depth: int = 1,
) -> None:
    """Recursive quick sort using Lomuto partitioning."""
    if high is None:
        high = len(values) - 1

    if stats is not None:
        stats.recursive_calls += 1
        stats.max_recursion_depth = max(stats.max_recursion_depth, depth)

    if low >= high:
        return

    pivot_index = lomuto_partition(values, low, high, stats)

    quick_sort_lomuto(values, stats, low, pivot_index - 1, depth + 1)
    quick_sort_lomuto(values, stats, pivot_index + 1, high, depth + 1)


def hoare_partition(
    values: List[int],
    low: int,
    high: int,
    stats: SortStats | None = None,
) -> int:
    """
    Partition using Hoare's partition scheme.

    Hoare partitioning does not necessarily place the pivot at its final
    sorted index. Instead, it returns a boundary that separates values into
    two regions suitable for recursive sorting.
    """
    pivot = values[(low + high) // 2]
    left = low - 1
    right = high + 1

    while True:
        while True:
            left += 1
            if stats is not None:
                stats.comparisons += 1
            if values[left] >= pivot:
                break

        while True:
            right -= 1
            if stats is not None:
                stats.comparisons += 1
            if values[right] <= pivot:
                break

        if left >= right:
            return right

        swap(values, left, right, stats)


def quick_sort_hoare(
    values: List[int],
    stats: SortStats | None = None,
    low: int = 0,
    high: int | None = None,
    depth: int = 1,
) -> None:
    """Recursive quick sort using Hoare partitioning."""
    if high is None:
        high = len(values) - 1

    if stats is not None:
        stats.recursive_calls += 1
        stats.max_recursion_depth = max(stats.max_recursion_depth, depth)

    if low >= high:
        return

    boundary = hoare_partition(values, low, high, stats)

    quick_sort_hoare(values, stats, low, boundary, depth + 1)
    quick_sort_hoare(values, stats, boundary + 1, high, depth + 1)


def choose_pivot_index(
    values: Sequence[int],
    low: int,
    high: int,
    strategy: str,
    rng: random.Random | None = None,
) -> int:
    """Select a pivot according to a named strategy."""
    if strategy == "first":
        return low

    if strategy == "last":
        return high

    if strategy == "middle":
        return (low + high) // 2

    if strategy == "random":
        if rng is None:
            rng = random.Random()
        return rng.randint(low, high)

    if strategy == "median_of_three":
        middle = (low + high) // 2
        candidates = [
            (values[low], low),
            (values[middle], middle),
            (values[high], high),
        ]
        candidates.sort(key=lambda item: item[0])
        return candidates[1][1]

    raise ValueError(f"unknown pivot strategy: {strategy}")


def quick_sort_with_pivot_strategy(
    values: List[int],
    strategy: str = "median_of_three",
    stats: SortStats | None = None,
    rng: random.Random | None = None,
) -> None:
    """
    Quick sort using Lomuto partitioning with configurable pivot selection.

    The selected pivot is moved to the end so that the same partition routine
    can be reused. This isolates pivot selection from partition mechanics.
    """
    if not values:
        return

    validate_numeric_sequence(values)

    if stats is None:
        stats = SortStats()

    if rng is None:
        rng = random.Random(42)

    def recursive_sort(low: int, high: int, depth: int) -> None:
        stats.recursive_calls += 1
        stats.max_recursion_depth = max(stats.max_recursion_depth, depth)

        if low >= high:
            return

        pivot_index = choose_pivot_index(values, low, high, strategy, rng)
        swap(values, pivot_index, high, stats)

        final_pivot_index = lomuto_partition(values, low, high, stats)

        recursive_sort(low, final_pivot_index - 1, depth + 1)
        recursive_sort(final_pivot_index + 1, high, depth + 1)

    recursive_sort(0, len(values) - 1, 1)


def three_way_partition(
    values: List[int],
    low: int,
    high: int,
    stats: SortStats | None = None,
) -> Tuple[int, int]:
    """
    Partition into three regions around a pivot value.

    The resulting regions are:
        values[low:less]       < pivot
        values[less:greater+1] == pivot
        values[greater+1:high+1] > pivot

    This is especially useful when many elements have the same value because
    equal elements are removed from further recursive partitioning.
    """
    pivot = values[(low + high) // 2]
    less = low
    current = low
    greater = high

    while current <= greater:
        if stats is not None:
            stats.comparisons += 1

        if values[current] < pivot:
            swap(values, less, current, stats)
            less += 1
            current += 1
        elif values[current] > pivot:
            swap(values, current, greater, stats)
            greater -= 1
        else:
            current += 1

    return less, greater


def quick_sort_three_way(
    values: List[int],
    stats: SortStats | None = None,
) -> None:
    """Quick sort optimized for inputs containing many duplicate values."""
    if not values:
        return

    validate_numeric_sequence(values)

    if stats is None:
        stats = SortStats()

    def recursive_sort(low: int, high: int, depth: int) -> None:
        stats.recursive_calls += 1
        stats.max_recursion_depth = max(stats.max_recursion_depth, depth)

        if low >= high:
            return

        equal_start, equal_end = three_way_partition(values, low, high, stats)

        recursive_sort(low, equal_start - 1, depth + 1)
        recursive_sort(equal_end + 1, high, depth + 1)

    recursive_sort(0, len(values) - 1, 1)


def merge(
    values: List[int],
    temporary: List[int],
    left: int,
    middle: int,
    right: int,
    stats: SortStats | None = None,
) -> None:
    """
    Merge two sorted ranges.

    Unlike quick sort, merge sort does not rearrange elements around a pivot.
    It builds a sorted result by repeatedly choosing the smaller front item
    from two already-sorted ranges.
    """
    left_index = left
    right_index = middle + 1
    output_index = left

    while left_index <= middle and right_index <= right:
        if stats is not None:
            stats.comparisons += 1

        if values[left_index] <= values[right_index]:
            temporary[output_index] = values[left_index]
            left_index += 1
        else:
            temporary[output_index] = values[right_index]
            right_index += 1

        output_index += 1

    while left_index <= middle:
        temporary[output_index] = values[left_index]
        left_index += 1
        output_index += 1

    while right_index <= right:
        temporary[output_index] = values[right_index]
        right_index += 1
        output_index += 1

    for index in range(left, right + 1):
        values[index] = temporary[index]


def merge_sort(
    values: List[int],
    stats: SortStats | None = None,
) -> None:
    """In-place interface around a merge-sort implementation using one buffer."""
    if len(values) < 2:
        return

    validate_numeric_sequence(values)

    if stats is None:
        stats = SortStats()

    temporary = [0] * len(values)

    def recursive_sort(left: int, right: int, depth: int) -> None:
        stats.recursive_calls += 1
        stats.max_recursion_depth = max(stats.max_recursion_depth, depth)

        if left >= right:
            return

        middle = left + (right - left) // 2

        recursive_sort(left, middle, depth + 1)
        recursive_sort(middle + 1, right, depth + 1)
        merge(values, temporary, left, middle, right, stats)

    recursive_sort(0, len(values) - 1, 1)


def demonstrate_basic_partition() -> None:
    """Show exactly what a partition operation does to one array."""
    print("\n=== Pivot and Partition ===")

    values = [29, 10, 14, 37, 13, 8, 42, 18]
    original = values.copy()
    pivot_value = values[-1]

    stats = SortStats()
    pivot_index = lomuto_partition(values, 0, len(values) - 1, stats)

    print(f"Original array: {original}")
    print(f"Pivot value:    {pivot_value}")
    print(f"After partition:{values}")
    print(f"Pivot position: {pivot_index}")
    print(f"Elements left of pivot are <= {pivot_value}")
    print(f"Elements right of pivot are > {pivot_value}")
    print(f"Comparisons:    {stats.comparisons}")
    print(f"Swaps:          {stats.swaps}")


def demonstrate_recursive_quick_sort() -> None:
    """Show recursive partitioning on a small realistic dataset."""
    print("\n=== Recursive Quick Sort ===")

    values = [34, 7, 23, 32, 5, 62, 19, 44, 12]
    print(f"Before: {values}")

    stats = SortStats()
    quick_sort_with_pivot_strategy(
        values,
        strategy="median_of_three",
        stats=stats,
        rng=random.Random(7),
    )

    print(f"After:  {values}")
    print(f"Sorted: {is_sorted(values)}")
    print(f"Recursive calls: {stats.recursive_calls}")
    print(f"Maximum recursion depth: {stats.max_recursion_depth}")


def demonstrate_pivot_strategies() -> None:
    """
    Compare pivot choices on the same data.

    A pivot does not have to be the median. The practical goal is to avoid
    repeatedly creating extremely unbalanced partitions.
    """
    print("\n=== Pivot Strategies ===")

    data = [41, 8, 29, 17, 63, 4, 52, 31, 22, 70, 11]

    for strategy in ("first", "last", "middle", "random", "median_of_three"):
        values = data.copy()
        stats = SortStats()

        quick_sort_with_pivot_strategy(
            values,
            strategy=strategy,
            stats=stats,
            rng=random.Random(123),
        )

        print(
            f"{strategy:>16}: "
            f"comparisons={stats.comparisons:4d}, "
            f"swaps={stats.swaps:3d}, "
            f"depth={stats.max_recursion_depth:2d}, "
            f"sorted={is_sorted(values)}"
        )


def demonstrate_duplicate_handling() -> None:
    """
    Show why three-way partitioning can be preferable for duplicate-heavy data.
    """
    print("\n=== Duplicate-Heavy Input ===")

    data = [
        5, 3, 5, 2, 5, 8, 5, 1, 3, 5,
        4, 5, 2, 5, 7, 5, 3, 5, 6, 5,
    ]

    standard_values = data.copy()
    three_way_values = data.copy()

    standard_stats = SortStats()
    three_way_stats = SortStats()

    quick_sort_with_pivot_strategy(
        standard_values,
        strategy="median_of_three",
        stats=standard_stats,
    )
    quick_sort_three_way(three_way_values, three_way_stats)

    print(f"Input:       {data}")
    print(f"Two-way:     {standard_values}")
    print(f"Three-way:   {three_way_values}")
    print(
        f"Two-way comparisons={standard_stats.comparisons}, "
        f"depth={standard_stats.max_recursion_depth}"
    )
    print(
        f"Three-way comparisons={three_way_stats.comparisons}, "
        f"depth={three_way_stats.max_recursion_depth}"
    )


def demonstrate_worst_case_behavior() -> None:
    """
    Expose the O(n^2) behavior of a poor pivot strategy.

    For an already sorted array, always choosing the last element makes the
    partition produce one large side and one empty side at every step.
    """
    print("\n=== Worst-Case Behavior ===")

    sample_size = 200
    sorted_data = list(range(sample_size))

    values = sorted_data.copy()
    stats = SortStats()

    quick_sort_with_pivot_strategy(
        values,
        strategy="last",
        stats=stats,
    )

    expected_comparisons = sample_size * (sample_size - 1) // 2

    print(f"Input size: {sample_size}")
    print(f"Sorted correctly: {is_sorted(values)}")
    print(f"Observed comparisons: {stats.comparisons}")
    print(f"Quadratic comparison pattern: approximately {expected_comparisons}")
    print(f"Maximum recursion depth: {stats.max_recursion_depth}")

    print(
        "\nA balanced quick sort has approximately logarithmic recursion depth, "
        "while repeatedly selecting an extreme pivot can make the depth linear."
    )


def demonstrate_best_and_average_behavior() -> None:
    """
    Contrast balanced, random, and adversarial input patterns.

    The expected running time of quick sort is O(n log n), but its worst case
    remains O(n^2) when partitions repeatedly become highly unbalanced.
    """
    print("\n=== Input Distribution and Practical Behavior ===")

    size = 300
    datasets = {
        "random": random.Random(99).sample(range(size * 5), size),
        "already sorted": list(range(size)),
        "reverse sorted": list(range(size, 0, -1)),
        "duplicates": [random.Random(101).choice([10, 20, 30, 40, 50]) for _ in range(size)],
    }

    for name, data in datasets.items():
        values = data.copy()
        stats = SortStats()

        quick_sort_with_pivot_strategy(
            values,
            strategy="median_of_three",
            stats=stats,
            rng=random.Random(2026),
        )

        print(
            f"{name:>16}: "
            f"comparisons={stats.comparisons:6d}, "
            f"swaps={stats.swaps:5d}, "
            f"depth={stats.max_recursion_depth:3d}, "
            f"sorted={is_sorted(values)}"
        )


def benchmark_quick_sort_and_merge_sort() -> None:
    """
    Compare quick sort and merge sort using identical data.

    Timings are environment-dependent. Operation counts and asymptotic
    properties are more meaningful than a single wall-clock measurement.
    """
    print("\n=== Quick Sort vs Merge Sort ===")

    rng = random.Random(2026)
    original = [rng.randrange(-100_000, 100_001) for _ in range(4_000)]

    quick_values = original.copy()
    merge_values = original.copy()

    quick_stats = SortStats()
    merge_stats = SortStats()

    start = time.perf_counter()
    quick_sort_three_way(quick_values, quick_stats)
    quick_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    merge_sort(merge_values, merge_stats)
    merge_elapsed = time.perf_counter() - start

    print(f"Quick sort sorted correctly: {is_sorted(quick_values)}")
    print(f"Merge sort sorted correctly: {is_sorted(merge_values)}")
    print(f"Quick sort time: {quick_elapsed:.6f} seconds")
    print(f"Merge sort time: {merge_elapsed:.6f} seconds")
    print(f"Quick sort comparisons: {quick_stats.comparisons}")
    print(f"Merge sort comparisons: {merge_stats.comparisons}")
    print(f"Quick sort swaps: {quick_stats.swaps}")
    print(f"Merge sort swaps: {merge_stats.swaps}")

    print("\nComplexity comparison:")
    print("Quick sort average expected time: O(n log n)")
    print("Quick sort worst-case time:       O(n^2)")
    print("Merge sort best/average/worst:    O(n log n)")
    print("Quick sort auxiliary space:       O(log n) expected for recursion")
    print("Merge sort auxiliary space:       O(n) for the merge buffer")


def demonstrate_edge_cases() -> None:
    """Exercise inputs that commonly reveal sorting implementation bugs."""
    print("\n=== Edge Cases and Validation ===")

    cases = {
        "empty": [],
        "one element": [42],
        "already sorted": [1, 2, 3, 4, 5],
        "reverse sorted": [5, 4, 3, 2, 1],
        "all equal": [7, 7, 7, 7, 7],
        "negative values": [-4, 9, -1, 0, -12, 6],
        "mixed duplicates": [3, 1, 3, 2, 1, 3, 2],
    }

    for name, data in cases.items():
        values = data.copy()
        quick_sort_three_way(values)
        print(f"{name:>18}: {values} | sorted={is_sorted(values)}")

    print("\nValidation example:")

    try:
        quick_sort_three_way([3, "2", 1])  # type: ignore[list-item]
    except TypeError as error:
        print(f"Caught invalid input: {error}")


def verify_against_python_reference() -> None:
    """
    Run randomized correctness checks against Python's built-in sorted().

    This is useful when developing sorting algorithms because a visually
    plausible result does not prove that every partition edge case is correct.
    """
    print("\n=== Randomized Correctness Verification ===")

    rng = random.Random(555)

    for case_number in range(250):
        length = rng.randrange(0, 80)
        data = [rng.randrange(-20, 21) for _ in range(length)]
        expected = sorted(data)

        algorithms: list[Callable[[List[int]], None]] = [
            lambda values: quick_sort_lomuto(values),
            lambda values: quick_sort_hoare(values),
            lambda values: quick_sort_with_pivot_strategy(
                values,
                strategy="median_of_three",
                rng=random.Random(case_number),
            ),
            quick_sort_three_way,
            merge_sort,
        ]

        for algorithm in algorithms:
            actual = data.copy()
            algorithm(actual)

            if actual != expected:
                raise AssertionError(
                    f"Sorting failure in case {case_number}: "
                    f"input={data}, expected={expected}, actual={actual}"
                )

    print("250 randomized cases passed for all implemented algorithms.")


def explain_algorithmic_reasoning() -> None:
    """Print concise technical reminders tied directly to the implementation."""
    print("\n=== Algorithmic Reasoning ===")

    print(
        "Pivot: an element or value used to divide the current range into "
        "subproblems."
    )
    print(
        "Partition: rearranges a range so that elements fall on the proper "
        "side of the pivot according to the chosen partition scheme."
    )
    print(
        "Recursive partitioning: after partitioning, quick sort recursively "
        "sorts the resulting subranges."
    )
    print(
        "Balanced partitions produce a recursion tree close to logarithmic "
        "height, giving expected O(n log n) behavior."
    )
    print(
        "Repeatedly unbalanced partitions produce a recursion tree close to "
        "linear height and can require O(n^2) comparisons."
    )
    print(
        "Merge sort avoids quick sort's quadratic worst case by recursively "
        "splitting the input and deterministically merging sorted halves."
    )


def demonstrate_recursion_limit_risk() -> None:
    """
    Show the relationship between recursion depth and Python's recursion limit.

    The function does not intentionally trigger RecursionError. It explains
    the risk because a naive recursive quick sort can create one call per
    element on adversarial input.
    """
    print("\n=== Recursion Safety ===")

    print(f"Current Python recursion limit: {sys.getrecursionlimit()}")
    print(
        "A naive quick sort with a linear recursion chain can approach this "
        "limit on sufficiently large adversarial inputs."
    )
    print(
        "Production implementations can reduce this risk by recursing first "
        "into the smaller partition and processing the larger partition "
        "iteratively, or by using an introspective sorting strategy."
    )


def main() -> None:
    """Run the complete quick-sort learning demonstration."""
    print("QUICK SORT TECHNICAL DEMONSTRATION")
    print("=" * 60)

    demonstrate_basic_partition()
    demonstrate_recursive_quick_sort()
    demonstrate_pivot_strategies()
    demonstrate_duplicate_handling()
    demonstrate_worst_case_behavior()
    demonstrate_best_and_average_behavior()
    benchmark_quick_sort_and_merge_sort()
    demonstrate_edge_cases()
    verify_against_python_reference()
    explain_algorithmic_reasoning()
    demonstrate_recursion_limit_risk()

    print("\nAll demonstrations completed successfully.")


if __name__ == "__main__":
    main()
