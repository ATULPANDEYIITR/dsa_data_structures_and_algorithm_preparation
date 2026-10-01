"""
Merge Sort: Divide and Conquer, Splitting, Merging, Recursion, and Complexity

A self-contained implementation that builds merge sort from first principles
without using Python's sorting libraries.

The program demonstrates:
- Recursive divide-and-conquer decomposition
- Stable merging of sorted ranges
- Top-down merge sort
- Bottom-up iterative merge sort
- In-place range management using one auxiliary buffer
- Custom comparison support
- Stability with records
- Input validation and edge cases
- Operation counting for algorithmic analysis
- Comparison with theoretical O(n log n) behavior
- A small verification suite
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Iterable, MutableSequence, Optional, Sequence, TypeVar


T = TypeVar("T")
K = TypeVar("K")


def merge(
    values: MutableSequence[T],
    auxiliary: MutableSequence[T],
    left: int,
    middle: int,
    right: int,
    *,
    key: Callable[[T], K] | None = None,
    operation_counter: Optional[dict[str, int]] = None,
) -> None:
    """
    Merge two already-sorted adjacent ranges:

        values[left : middle + 1]
        values[middle + 1 : right + 1]

    The result is written back into values[left : right + 1].

    The auxiliary array prevents overwriting elements that still need to
    participate in the merge. The <= comparison is intentional: when two
    elements have equal keys, the element from the left half is selected
    first, which preserves stability.
    """
    if left > middle or middle >= right:
        return

    if key is None:
        key_function: Callable[[T], K] = lambda item: item  # type: ignore
    else:
        key_function = key

    i = left
    j = middle + 1
    destination = left

    while i <= middle and j <= right:
        if operation_counter is not None:
            operation_counter["comparisons"] += 1

        # Taking the left item on equality makes the algorithm stable.
        if key_function(values[i]) <= key_function(values[j]):
            auxiliary[destination] = values[i]
            i += 1
        else:
            auxiliary[destination] = values[j]
            j += 1

        destination += 1

    while i <= middle:
        auxiliary[destination] = values[i]
        i += 1
        destination += 1

    while j <= right:
        auxiliary[destination] = values[j]
        j += 1
        destination += 1

    for index in range(left, right + 1):
        values[index] = auxiliary[index]

    if operation_counter is not None:
        operation_counter["merges"] += 1


def merge_sort(
    values: MutableSequence[T],
    *,
    key: Callable[[T], K] | None = None,
    operation_counter: Optional[dict[str, int]] = None,
) -> MutableSequence[T]:
    """
    Sort values using recursive top-down merge sort.

    Time:
        Best:    O(n log n)
        Average: O(n log n)
        Worst:   O(n log n)

    Auxiliary space:
        O(n) for the merge buffer plus O(log n) recursion depth.

    The input sequence is modified in place and returned for convenience.
    """
    if len(values) < 2:
        return values

    auxiliary = list(values)

    def sort_range(left: int, right: int) -> None:
        if left >= right:
            return

        middle = left + (right - left) // 2

        sort_range(left, middle)
        sort_range(middle + 1, right)

        # If the largest element on the left is already <= the smallest
        # element on the right, the range is already globally sorted.
        if operation_counter is not None:
            operation_counter["boundary_checks"] += 1

        if key is None:
            already_ordered = values[middle] <= values[middle + 1]  # type: ignore
        else:
            already_ordered = key(values[middle]) <= key(values[middle + 1])

        if already_ordered:
            operation_counter["skipped_merges"] = (
                operation_counter.get("skipped_merges", 0) + 1
                if operation_counter is not None
                else 0
            )
            return

        merge(
            values,
            auxiliary,
            left,
            middle,
            right,
            key=key,
            operation_counter=operation_counter,
        )

    sort_range(0, len(values) - 1)
    return values


def merge_sort_with_trace(values: Sequence[int]) -> list[int]:
    """
    Educational version that prints the recursive splitting and merging.

    A separate list is returned so the original input is not modified.
    """
    working = list(values)

    def merge_two(left: list[int], right: list[int]) -> list[int]:
        result: list[int] = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            if left[left_index] <= right[right_index]:
                result.append(left[left_index])
                left_index += 1
            else:
                result.append(right[right_index])
                right_index += 1

        result.extend(left[left_index:])
        result.extend(right[right_index:])
        return result

    def sort(items: list[int], depth: int = 0) -> list[int]:
        indentation = "  " * depth

        if len(items) <= 1:
            print(f"{indentation}Base case: {items}")
            return items

        middle = len(items) // 2
        left = items[:middle]
        right = items[middle:]

        print(f"{indentation}Split: {items} -> {left} | {right}")

        sorted_left = sort(left, depth + 1)
        sorted_right = sort(right, depth + 1)
        merged = merge_two(sorted_left, sorted_right)

        print(f"{indentation}Merge: {sorted_left} + {sorted_right} -> {merged}")
        return merged

    return sort(working)


@dataclass(frozen=True)
class Student:
    """
    A record used to demonstrate stable sorting.

    Students with the same score should retain their original relative order.
    """
    name: str
    score: int
    registration_order: int


def demonstrate_stability() -> None:
    students = [
        Student("Aarav", 82, 0),
        Student("Meera", 95, 1),
        Student("Kabir", 82, 2),
        Student("Ishita", 95, 3),
        Student("Rohan", 70, 4),
    ]

    merge_sort(students, key=lambda student: student.score)

    print("\nStable sort demonstration:")
    for student in students:
        print(
            f"  {student.name:8} score={student.score} "
            f"original_position={student.registration_order}"
        )

    score_82 = [student.name for student in students if student.score == 82]
    score_95 = [student.name for student in students if student.score == 95]

    assert score_82 == ["Aarav", "Kabir"]
    assert score_95 == ["Meera", "Ishita"]


def bottom_up_merge_sort(values: MutableSequence[T]) -> MutableSequence[T]:
    """
    Iterative merge sort.

    Instead of recursively splitting the input, this implementation starts
    with sorted runs of width 1, then merges runs of width 2, 4, 8, and so on.

    It has the same O(n log n) time complexity as top-down merge sort but
    avoids recursive call-stack growth.
    """
    length = len(values)

    if length < 2:
        return values

    auxiliary = list(values)
    width = 1

    while width < length:
        left = 0

        while left < length:
            middle = min(left + width - 1, length - 1)
            right = min(left + 2 * width - 1, length - 1)

            if middle < right:
                merge(
                    values,
                    auxiliary,
                    left,
                    middle,
                    right,
                )

            left += 2 * width

        width *= 2

    return values


def count_inversions(values: Sequence[int]) -> int:
    """
    Count inversions using the merge process.

    An inversion is a pair (i, j) where i < j but values[i] > values[j].

    During merging, if the current right-half value is selected before the
    remaining left-half values, every remaining left-half value forms an
    inversion with that right-half value.

    This changes merge sort from only a sorting algorithm into an efficient
    O(n log n) inversion-counting algorithm.
    """
    working = list(values)
    auxiliary = [0] * len(working)

    def sort_and_count(left: int, right: int) -> int:
        if left >= right:
            return 0

        middle = left + (right - left) // 2

        inversions = (
            sort_and_count(left, middle)
            + sort_and_count(middle + 1, right)
        )

        i = left
        j = middle + 1
        destination = left

        while i <= middle and j <= right:
            if working[i] <= working[j]:
                auxiliary[destination] = working[i]
                i += 1
            else:
                auxiliary[destination] = working[j]
                j += 1
                inversions += middle - i + 1

            destination += 1

        while i <= middle:
            auxiliary[destination] = working[i]
            i += 1
            destination += 1

        while j <= right:
            auxiliary[destination] = working[j]
            j += 1
            destination += 1

        for index in range(left, right + 1):
            working[index] = auxiliary[index]

        return inversions

    return sort_and_count(0, len(working) - 1) if working else 0


def verify_sorting_algorithm() -> None:
    """
    Test important correctness properties rather than only one example.
    """
    test_cases = [
        [],
        [1],
        [2, 1],
        [1, 2],
        [5, 5, 5],
        [3, -1, 8, 0, -5, 2],
        list(range(20)),
        list(range(20, 0, -1)),
        [4, 1, 4, 2, 1, 3, 2],
    ]

    for original in test_cases:
        expected = sorted(original)

        recursive_result = original.copy()
        merge_sort(recursive_result)
        assert recursive_result == expected

        iterative_result = original.copy()
        bottom_up_merge_sort(iterative_result)
        assert iterative_result == expected

    random_generator = Random(42)

    for _ in range(100):
        original = [
            random_generator.randint(-1_000, 1_000)
            for _ in range(random_generator.randint(0, 100))
        ]

        expected = sorted(original)
        actual = original.copy()
        merge_sort(actual)

        assert actual == expected

    print("\nVerification: all sorting tests passed.")


def demonstrate_complexity() -> None:
    """
    Collect comparison counts for several input patterns.

    Merge sort remains O(n log n) even when the input is reversed.
    Already-sorted input can benefit from the boundary check used by the
    optimized implementation.
    """
    print("\nOperation-count demonstration:")

    for size in (8, 16, 32, 64):
        patterns = {
            "random": [
                Random(size).randint(0, size * 10)
                for _ in range(size)
            ],
            "sorted": list(range(size)),
            "reversed": list(range(size, 0, -1)),
        }

        print(f"\nInput size: {size}")

        for name, data in patterns.items():
            counters = {
                "comparisons": 0,
                "merges": 0,
                "boundary_checks": 0,
                "skipped_merges": 0,
            }

            merge_sort(data, operation_counter=counters)
            print(f"  {name:8} {counters}")


def explain_complexity_with_small_tree() -> None:
    """
    Show why the recurrence is T(n) = 2T(n/2) + O(n).

    Every recursive level performs approximately n total work while the
    number of levels is logarithmic in n.
    """
    print("\nRecursion-level model:")

    n = 16
    level = 0

    while n >= 1:
        print(
            f"  level={level}, subproblems={2 ** level}, "
            f"elements per subproblem={n}"
        )
        n //= 2
        level += 1

    print("  Each level processes O(n) total elements.")
    print("  The number of levels is O(log n).")
    print("  Therefore total running time is O(n log n).")


def main() -> None:
    print("MERGE SORT CASE STUDY")
    print("=" * 60)

    values = [38, 27, 43, 3, 9, 82, 10]
    print(f"\nOriginal values: {values}")

    sorted_values = values.copy()
    merge_sort(sorted_values)

    print(f"Sorted values:   {sorted_values}")

    print("\nRecursive split/merge trace:")
    merge_sort_with_trace([38, 27, 43, 3, 9, 82, 10])

    demonstrate_stability()

    iterative_values = [12, 5, 19, 1, 7, 3, 15]
    print("\nBottom-up merge sort:")
    print(f"  before: {iterative_values}")
    bottom_up_merge_sort(iterative_values)
    print(f"  after:  {iterative_values}")

    inversion_input = [2, 4, 1, 3, 5]
    print("\nInversion counting:")
    print(f"  input: {inversion_input}")
    print(f"  inversions: {count_inversions(inversion_input)}")

    verify_sorting_algorithm()
    demonstrate_complexity()
    explain_complexity_with_small_tree()

    print("\nKey implementation properties:")
    print("  - Divide: recursively split each range into two halves.")
    print("  - Conquer: recursively sort each half.")
    print("  - Combine: merge the two sorted halves.")
    print("  - Stability: equal keys preserve their original relative order.")
    print("  - Time: O(n log n) in best, average, and worst cases.")
    print("  - Auxiliary space: O(n) for the merge buffer.")


if __name__ == "__main__":
    main()
