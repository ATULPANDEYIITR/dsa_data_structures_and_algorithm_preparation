"""
Advanced Sorting Review
=======================

A self-contained study and implementation of:

- Counting sort
- Heap sort
- Sorting-based problem solving
- Comparative analysis of classical sorting algorithms

The program is executable with Python 3.9+ and uses only the standard library.

The implementation deliberately emphasizes:
- Correctness
- Stability
- Input validation
- Edge cases
- Complexity
- Practical algorithm selection
- Sorting as a tool for solving larger problems
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from time import perf_counter
from typing import Callable, Iterable, Sequence, TypeVar
import heapq


T = TypeVar("T")
SortFunction = Callable[[list[int]], list[int]]


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def validate_integer_list(values: Iterable[int]) -> list[int]:
    """
    Materialize an iterable and verify that it contains only integers.

    bool is rejected explicitly because bool is a subclass of int in Python,
    but treating True as the number 1 is normally surprising in a sorting API.
    """
    result = list(values)

    for value in result:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"sorting algorithms in this study require integers; "
                f"received {value!r}"
            )

    return result


def is_sorted(values: Sequence[int]) -> bool:
    """Return True when values are in nondecreasing order."""
    return all(values[index] <= values[index + 1]
               for index in range(len(values) - 1))


def same_multiset(left: Sequence[int], right: Sequence[int]) -> bool:
    """
    Check that two integer sequences contain exactly the same values.

    Sorting correctness requires both ordering and preservation of elements.
    """
    return sorted(left) == sorted(right)


def verify_sort(
    sorter: SortFunction,
    values: Sequence[int],
) -> list[int]:
    """Run a sorter and verify ordering plus element preservation."""
    original = list(values)
    result = sorter(original)

    if not is_sorted(result):
        raise AssertionError(f"{sorter.__name__} produced unsorted output")

    if not same_multiset(original, result):
        raise AssertionError(
            f"{sorter.__name__} changed the input elements"
        )

    return result


# ---------------------------------------------------------------------------
# Elementary algorithms used for comparison
# ---------------------------------------------------------------------------

def bubble_sort(values: list[int]) -> list[int]:
    """
    Bubble sort with an early-exit optimization.

    The optimization changes the best case to O(n) for already sorted input,
    while the worst and average cases remain O(n^2).
    """
    data = validate_integer_list(values)

    for end in range(len(data) - 1, 0, -1):
        swapped = False

        for index in range(end):
            if data[index] > data[index + 1]:
                data[index], data[index + 1] = data[index + 1], data[index]
                swapped = True

        if not swapped:
            break

    return data


def selection_sort(values: list[int]) -> list[int]:
    """
    Selection sort.

    Selecting the minimum for each position gives O(n^2) comparisons.
    Swapping can reorder equal values, so the normal implementation is not
    stable.
    """
    data = validate_integer_list(values)

    for start in range(len(data) - 1):
        minimum_index = start

        for index in range(start + 1, len(data)):
            if data[index] < data[minimum_index]:
                minimum_index = index

        if minimum_index != start:
            data[start], data[minimum_index] = (
                data[minimum_index],
                data[start],
            )

    return data


def insertion_sort(values: list[int]) -> list[int]:
    """
    Insertion sort.

    Elements are shifted rather than arbitrarily swapped, preserving the
    relative order of equal values and therefore providing stability.
    """
    data = validate_integer_list(values)

    for index in range(1, len(data)):
        current = data[index]
        position = index - 1

        while position >= 0 and data[position] > current:
            data[position + 1] = data[position]
            position -= 1

        data[position + 1] = current

    return data


# ---------------------------------------------------------------------------
# Merge sort
# ---------------------------------------------------------------------------

def merge_sort(values: list[int]) -> list[int]:
    """
    Stable merge sort.

    The merge operation chooses the left item when values compare equal.
    That <= decision is what preserves the relative order of equal keys.
    """
    data = validate_integer_list(values)

    if len(data) <= 1:
        return data

    middle = len(data) // 2
    left = merge_sort(data[:middle])
    right = merge_sort(data[middle:])

    merged: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])

    return merged


# ---------------------------------------------------------------------------
# Quick sort
# ---------------------------------------------------------------------------

def quick_sort(values: list[int]) -> list[int]:
    """
    Three-way quicksort using a median-of-three pivot.

    Three-way partitioning is useful when many values are equal because it
    separates values into less-than, equal-to, and greater-than partitions.

    This implementation is not stable. Its worst case remains O(n^2), even
    though median-of-three selection reduces some poor pivot choices.
    """
    data = validate_integer_list(values)

    def sort_range(left: int, right: int) -> None:
        while left < right:
            middle = (left + right) // 2
            candidates = [
                (data[left], left),
                (data[middle], middle),
                (data[right], right),
            ]
            candidates.sort(key=lambda item: item[0])
            pivot = candidates[1][0]

            less = left
            current = left
            greater = right

            while current <= greater:
                if data[current] < pivot:
                    data[less], data[current] = data[current], data[less]
                    less += 1
                    current += 1
                elif data[current] > pivot:
                    data[current], data[greater] = (
                        data[greater],
                        data[current],
                    )
                    greater -= 1
                else:
                    current += 1

            # Recurse into the smaller side first and process the other side
            # iteratively to reduce recursion depth.
            if less - left < right - greater:
                sort_range(left, less - 1)
                left = greater + 1
            else:
                sort_range(greater + 1, right)
                right = less - 1

    sort_range(0, len(data) - 1)
    return data


# ---------------------------------------------------------------------------
# Counting sort
# ---------------------------------------------------------------------------

def counting_sort(
    values: list[int],
    *,
    stable: bool = True,
    allow_negative: bool = True,
    max_range_ratio: int = 50,
) -> list[int]:
    """
    Counting sort for integer keys.

    Core idea:
        count[value] records how many times each key occurs.

    When stable=True, cumulative counts identify the final position of every
    occurrence. Processing the input from right to left preserves the
    relative order of equal keys.

    Negative integers are supported by translating the minimum value to
    index zero.

    A range guard prevents accidental allocation of an enormous counting
    array for sparse values such as [1, 10**12].

    Time:  O(n + k)
    Space: O(n + k)

    where k is the numeric range max_value - min_value + 1.
    """
    data = validate_integer_list(values)

    if not data:
        return []

    minimum = min(data)
    maximum = max(data)
    numeric_range = maximum - minimum + 1

    if numeric_range <= 0:
        raise ValueError("invalid integer range")

    if numeric_range > max(1, len(data) * max_range_ratio):
        raise ValueError(
            "counting sort is unsuitable for this sparse numeric range; "
            f"range={numeric_range}, n={len(data)}"
        )

    counts = [0] * numeric_range

    for value in data:
        counts[value - minimum] += 1

    if not stable:
        result: list[int] = []

        for offset, count in enumerate(counts):
            if count:
                result.extend([offset + minimum] * count)

        return result

    # Convert frequencies to cumulative end positions.
    for index in range(1, len(counts)):
        counts[index] += counts[index - 1]

    result = [0] * len(data)

    # Reverse traversal is essential for stable counting sort. If equal keys
    # were processed from left to right, their relative order would reverse.
    for value in reversed(data):
        offset = value - minimum
        counts[offset] -= 1
        result[counts[offset]] = value

    return result


# ---------------------------------------------------------------------------
# Heap sort
# ---------------------------------------------------------------------------

def heap_sort(values: list[int]) -> list[int]:
    """
    In-place heap sort.

    A max heap is constructed in the input array. The largest item is then
    repeatedly moved to the end of the active region.

    Unlike heapq-based sorting, this implementation explicitly builds the
    heap so the O(1) auxiliary-space property of heap sort is visible.

    Time:  O(n log n)
    Extra space: O(1), excluding the copied input required by this function's
    non-mutating API.
    """
    data = validate_integer_list(values)
    size = len(data)

    def sift_down(root: int, heap_size: int) -> None:
        while True:
            left = 2 * root + 1
            right = left + 1
            largest = root

            if left < heap_size and data[left] > data[largest]:
                largest = left

            if right < heap_size and data[right] > data[largest]:
                largest = right

            if largest == root:
                return

            data[root], data[largest] = data[largest], data[root]
            root = largest

    # Every internal node is sifted down. Starting at the last internal node
    # guarantees that children are already valid heaps when their parent is
    # processed.
    for root in range(size // 2 - 1, -1, -1):
        sift_down(root, size)

    for end in range(size - 1, 0, -1):
        data[0], data[end] = data[end], data[0]
        sift_down(0, end)

    return data


# ---------------------------------------------------------------------------
# Sorting-based problem solving
# ---------------------------------------------------------------------------

def contains_duplicate_by_sorting(values: Sequence[int]) -> bool:
    """
    Detect duplicates by sorting.

    This is useful when the sorted representation is also needed for another
    part of the problem. Complexity is O(n log n) due to sorting.
    """
    data = sorted(validate_integer_list(values))

    return any(
        data[index] == data[index - 1]
        for index in range(1, len(data))
    )


def merge_intervals(
    intervals: Iterable[tuple[int, int]],
) -> list[tuple[int, int]]:
    """
    Merge overlapping closed intervals.

    Sorting by start time transforms an arbitrary interval collection into a
    sequence where only the current merged interval needs to be tracked.
    """
    normalized: list[tuple[int, int]] = []

    for start, end in intervals:
        if not isinstance(start, int) or not isinstance(end, int):
            raise TypeError("interval endpoints must be integers")

        if start > end:
            raise ValueError(
                f"invalid interval ({start}, {end}): start exceeds end"
            )

        normalized.append((start, end))

    normalized.sort(key=lambda interval: interval[0])

    if not normalized:
        return []

    merged = [normalized[0]]

    for start, end in normalized[1:]:
        previous_start, previous_end = merged[-1]

        if start <= previous_end:
            merged[-1] = (
                previous_start,
                max(previous_end, end),
            )
        else:
            merged.append((start, end))

    return merged


def two_sum_sorted(
    values: Sequence[int],
    target: int,
) -> tuple[int, int] | None:
    """
    Find two values whose sum equals target after sorting.

    The function returns values rather than original indices because sorting
    changes positional information. The two-pointer scan is O(n) after the
    O(n log n) sort.
    """
    data = validate_integer_list(values)
    data.sort()

    left = 0
    right = len(data) - 1

    while left < right:
        total = data[left] + data[right]

        if total == target:
            return data[left], data[right]

        if total < target:
            left += 1
        else:
            right -= 1

    return None


@dataclass(frozen=True)
class Job:
    """A job with a start and finish time."""

    name: str
    start: int
    finish: int

    def __post_init__(self) -> None:
        if self.start > self.finish:
            raise ValueError("job start cannot exceed finish")


def maximum_non_overlapping_jobs(
    jobs: Iterable[Job],
) -> list[Job]:
    """
    Select a maximum-size set of non-overlapping jobs.

    Sorting by finish time enables the classic greedy interval scheduling
    strategy. The choice with the earliest finishing time leaves the largest
    remaining time window for future jobs.
    """
    ordered = sorted(jobs, key=lambda job: job.finish)

    selected: list[Job] = []
    current_finish: int | None = None

    for job in ordered:
        if current_finish is None or job.start >= current_finish:
            selected.append(job)
            current_finish = job.finish

    return selected


@dataclass(frozen=True)
class Transaction:
    """A transaction used to demonstrate stable sorting by a secondary key."""

    transaction_id: str
    customer: str
    amount: int


def stable_group_transactions(
    transactions: Sequence[Transaction],
) -> list[Transaction]:
    """
    Group transactions by customer while preserving original order.

    Python's sorted() is stable, so transactions belonging to the same
    customer retain their input order. This is a practical reason stability
    matters when records contain more information than their sorting key.
    """
    return sorted(transactions, key=lambda transaction: transaction.customer)


def kth_largest_by_heap(values: Sequence[int], k: int) -> int:
    """
    Find the kth largest value without fully sorting the input.

    A min heap of size k stores only the candidates that can still become the
    kth largest value. Complexity is O(n log k), useful when k is much smaller
    than n.
    """
    data = validate_integer_list(values)

    if not 1 <= k <= len(data):
        raise ValueError("k must be between 1 and the number of values")

    heap: list[int] = []

    for value in data:
        if len(heap) < k:
            heapq.heappush(heap, value)
        elif value > heap[0]:
            heapq.heapreplace(heap, value)

    return heap[0]


# ---------------------------------------------------------------------------
# Stability demonstration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Record:
    key: int
    original_position: int
    payload: str


def stable_counting_sort_records(
    records: Sequence[Record],
) -> list[Record]:
    """
    Stable counting sort for records keyed by a small integer.

    This makes stability observable: records with equal keys must emerge in
    the same order in which they entered the algorithm.
    """
    if not records:
        return []

    keys = [record.key for record in records]

    for key in keys:
        if not isinstance(key, int):
            raise TypeError("record keys must be integers")

    minimum = min(keys)
    maximum = max(keys)
    numeric_range = maximum - minimum + 1

    if numeric_range > len(records) * 20:
        raise ValueError("key range is too sparse for this demonstration")

    counts = [0] * numeric_range

    for record in records:
        counts[record.key - minimum] += 1

    for index in range(1, len(counts)):
        counts[index] += counts[index - 1]

    result: list[Record | None] = [None] * len(records)

    for record in reversed(records):
        offset = record.key - minimum
        counts[offset] -= 1
        result[counts[offset]] = record

    return [record for record in result if record is not None]


def demonstrate_stability() -> None:
    """Show why stable sorting matters for records with duplicate keys."""
    records = [
        Record(2, 0, "first priority-2 record"),
        Record(1, 1, "first priority-1 record"),
        Record(2, 2, "second priority-2 record"),
        Record(1, 3, "second priority-1 record"),
        Record(2, 4, "third priority-2 record"),
    ]

    sorted_records = stable_counting_sort_records(records)

    print("\nStable counting sort of records:")
    for record in sorted_records:
        print(
            f"  key={record.key}, "
            f"original_position={record.original_position}, "
            f"payload={record.payload}"
        )

    key_two_positions = [
        record.original_position
        for record in sorted_records
        if record.key == 2
    ]

    if key_two_positions != [0, 2, 4]:
        raise AssertionError("stable ordering was not preserved")


# ---------------------------------------------------------------------------
# Counting-sort decision logic
# ---------------------------------------------------------------------------

def choose_integer_sort(values: Sequence[int]) -> str:
    """
    Explain whether counting sort is a reasonable choice for the data.

    The decision is based on the relationship between n and k rather than
    simply checking whether values are integers.
    """
    data = validate_integer_list(values)

    if not data:
        return "counting sort is applicable to the empty input"

    minimum = min(data)
    maximum = max(data)
    numeric_range = maximum - minimum + 1

    if numeric_range <= len(data) * 10:
        return (
            f"counting sort is attractive: n={len(data)}, "
            f"k={numeric_range}"
        )

    return (
        f"comparison-based sorting is likely more memory-efficient: "
        f"n={len(data)}, k={numeric_range}"
    )


# ---------------------------------------------------------------------------
# Performance experiment
# ---------------------------------------------------------------------------

def benchmark_sorters(
    dataset: Sequence[int],
    sorters: dict[str, SortFunction],
) -> dict[str, float]:
    """
    Measure elapsed time for each sorter.

    Each sorter receives an independent copy so no algorithm benefits from
    another algorithm having already sorted the same list.
    """
    timings: dict[str, float] = {}

    for name, sorter in sorters.items():
        start = perf_counter()
        result = sorter(list(dataset))
        elapsed = perf_counter() - start

        if not is_sorted(result):
            raise AssertionError(f"{name} failed benchmark validation")

        timings[name] = elapsed

    return timings


def run_benchmark() -> None:
    """
    Run a moderate benchmark.

    Bubble, selection, and insertion sort are intentionally benchmarked on a
    smaller dataset because quadratic algorithms become impractical quickly.
    """
    random = Random(42)

    small_dataset = [
        random.randint(-500, 500)
        for _ in range(700)
    ]

    larger_dataset = [
        random.randint(0, 10_000)
        for _ in range(8_000)
    ]

    small_sorters: dict[str, SortFunction] = {
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "Heap Sort": heap_sort,
    }

    large_sorters: dict[str, SortFunction] = {
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "Heap Sort": heap_sort,
        "Counting Sort": counting_sort,
    }

    print("\nBenchmark: moderate quadratic/comparison workload")
    for name, elapsed in benchmark_sorters(
        small_dataset,
        small_sorters,
    ).items():
        print(f"  {name:<18} {elapsed:.6f} seconds")

    print("\nBenchmark: larger integer workload")
    for name, elapsed in benchmark_sorters(
        larger_dataset,
        large_sorters,
    ).items():
        print(f"  {name:<18} {elapsed:.6f} seconds")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def run_edge_cases() -> None:
    """Exercise inputs that frequently reveal implementation errors."""
    cases = [
        [],
        [7],
        [5, 5, 5, 5],
        [-3, -1, -2, 0, 2],
        [9, 1, 9, 3, 1, 9],
        [0, -1, 0, -1, 2, -2],
    ]

    sorters = [
        counting_sort,
        heap_sort,
        merge_sort,
        quick_sort,
        insertion_sort,
        selection_sort,
        bubble_sort,
    ]

    print("\nEdge-case verification:")

    for case in cases:
        print(f"  input={case}")

        for sorter in sorters:
            result = verify_sort(sorter, case)
            print(f"    {sorter.__name__:<16} -> {result}")

    print("\nCounting-sort sparse-range guard:")
    try:
        counting_sort([1, 1_000_000_000])
    except ValueError as error:
        print(f"  rejected safely: {error}")


# ---------------------------------------------------------------------------
# Heap internals demonstration
# ---------------------------------------------------------------------------

def show_heap_structure(values: Sequence[int]) -> None:
    """
    Display the array representation of a max heap.

    For a zero-based array:
        left child  = 2*i + 1
        right child = 2*i + 2
    """
    data = validate_integer_list(values)

    def sift_down(root: int, heap_size: int) -> None:
        while True:
            left = root * 2 + 1
            right = left * 2 + 2
            largest = root

            if left < heap_size and data[left] > data[largest]:
                largest = left

            if right < heap_size and data[right] > data[largest]:
                largest = right

            if largest == root:
                return

            data[root], data[largest] = data[largest], data[root]
            root = largest

    for root in range(len(data) // 2 - 1, -1, -1):
        sift_down(root, len(data))

    print("\nMax-heap array representation:")
    print(f"  {data}")


# ---------------------------------------------------------------------------
# Sorting-based analytical workflow
# ---------------------------------------------------------------------------

def analyze_sales_data() -> None:
    """
    Demonstrate sorting as a problem-solving primitive.

    The task is not merely "sort the data". Sorting creates useful structure:
    the ordered amounts reveal the largest transaction, the median, adjacent
    differences, and duplicate amounts.
    """
    sales = [1250, 900, 1250, 430, 2100, 900, 1800, 760, 2100]

    ordered = sorted(sales)

    median = (
        ordered[len(ordered) // 2]
        if len(ordered) % 2
        else (
            ordered[len(ordered) // 2 - 1]
            + ordered[len(ordered) // 2]
        ) / 2
    )

    adjacent_gaps = [
        ordered[index + 1] - ordered[index]
        for index in range(len(ordered) - 1)
    ]

    duplicate_amounts = [
        value
        for value in set(ordered)
        if ordered.count(value) > 1
    ]

    print("\nSorting-based sales analysis:")
    print(f"  ordered amounts: {ordered}")
    print(f"  median: {median}")
    print(f"  largest transaction: {ordered[-1]}")
    print(f"  adjacent gaps: {adjacent_gaps}")
    print(f"  repeated amounts: {sorted(duplicate_amounts)}")


# ---------------------------------------------------------------------------
# Complete study
# ---------------------------------------------------------------------------

def run_sorting_case_study() -> None:
    """Run the practical examples for sorting-based problem solving."""
    intervals = [
        (1, 4),
        (2, 6),
        (8, 10),
        (9, 12),
        (15, 18),
    ]

    jobs = [
        Job("API maintenance", 1, 3),
        Job("database migration", 3, 5),
        Job("security review", 0, 2),
        Job("release validation", 5, 7),
        Job("performance test", 4, 6),
    ]

    transactions = [
        Transaction("T001", "C002", 500),
        Transaction("T002", "C001", 700),
        Transaction("T003", "C002", 300),
        Transaction("T004", "C001", 200),
        Transaction("T005", "C003", 900),
    ]

    print("\nSorting-based problem solving:")

    print(
        "  duplicate detection:",
        contains_duplicate_by_sorting([4, 8, 2, 8, 7]),
    )

    print(
        "  two-sum after sorting:",
        two_sum_sorted([11, 2, 7, 15, 4], 9),
    )

    print("  merged intervals:", merge_intervals(intervals))

    selected_jobs = maximum_non_overlapping_jobs(jobs)
    print(
        "  non-overlapping schedule:",
        [(job.name, job.start, job.finish) for job in selected_jobs],
    )

    grouped = stable_group_transactions(transactions)
    print(
        "  customer-grouped transactions:",
        [(item.customer, item.transaction_id) for item in grouped],
    )

    print(
        "  2nd largest using heap:",
        kth_largest_by_heap([91, 13, 55, 72, 40, 99], 2),
    )


def print_complexity_reference() -> None:
    """Print the requested final algorithm comparison."""
    rows = [
        (
            "Bubble Sort",
            "O(n²)",
            "O(n²)",
            "O(1)",
            "Yes",
        ),
        (
            "Selection Sort",
            "O(n²)",
            "O(n²)",
            "O(1)",
            "Usually No",
        ),
        (
            "Insertion Sort",
            "O(n²)",
            "O(n²)",
            "O(1)",
            "Yes",
        ),
        (
            "Merge Sort",
            "O(n log n)",
            "O(n log n)",
            "O(n)",
            "Yes",
        ),
        (
            "Quick Sort",
            "O(n log n)",
            "O(n²)",
            "Depends",
            "Usually No",
        ),
        (
            "Counting Sort",
            "O(n + k)",
            "O(n + k)",
            "O(n + k)",
            "Can be",
        ),
        (
            "Heap Sort",
            "O(n log n)",
            "O(n log n)",
            "O(1)",
            "No",
        ),
    ]

    print("\nFinal algorithm comparison:")
    print(
        f"{'Algorithm':<18}"
        f"{'Average Time':<16}"
        f"{'Worst Time':<16}"
        f"{'Extra Space':<16}"
        f"{'Stable':<12}"
    )
    print("-" * 78)

    for row in rows:
        print(
            f"{row[0]:<18}"
            f"{row[1]:<16}"
            f"{row[2]:<16}"
            f"{row[3]:<16}"
            f"{row[4]:<12}"
        )


def run_internal_assertions() -> None:
    """Perform deterministic correctness checks before demonstrations."""
    test_inputs = [
        [],
        [1],
        [4, 1, 3, 2],
        [5, 5, 5],
        [-10, 0, 7, -3, 2, -3],
        [100, 1, 50, 1, 100],
    ]

    sorters = [
        bubble_sort,
        selection_sort,
        insertion_sort,
        merge_sort,
        quick_sort,
        counting_sort,
        heap_sort,
    ]

    for sorter in sorters:
        for values in test_inputs:
            if sorter is counting_sort:
                result = sorter(values)
            else:
                result = sorter(values)

            expected = sorted(values)

            if result != expected:
                raise AssertionError(
                    f"{sorter.__name__}: expected {expected}, got {result}"
                )

    assert merge_intervals([]) == []
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]
    assert two_sum_sorted([3, 1, 4, 8], 7) == (3, 4)
    assert two_sum_sorted([1, 2, 8], 20) is None
    assert kth_largest_by_heap([9, 2, 7, 5], 1) == 9
    assert kth_largest_by_heap([9, 2, 7, 5], 4) == 2


def main() -> None:
    """Execute the complete advanced sorting review."""
    print("=" * 78)
    print("ADVANCED SORTING REVIEW")
    print("=" * 78)

    run_internal_assertions()

    sample = [12, -3, 7, 7, 0, -8, 4, 2, 12]

    print("\nSample input:")
    print(f"  {sample}")

    print("\nCounting sort:")
    print(f"  {counting_sort(sample)}")

    print("\nHeap sort:")
    print(f"  {heap_sort(sample)}")

    print("\nCounting-sort decision:")
    print(f"  {choose_integer_sort(sample)}")

    show_heap_structure(sample)
    demonstrate_stability()
    run_sorting_case_study()
    analyze_sales_data()
    run_edge_cases()
    run_benchmark()
    print_complexity_reference()

    print("\nAll correctness assertions passed.")


if __name__ == "__main__":
    main()
