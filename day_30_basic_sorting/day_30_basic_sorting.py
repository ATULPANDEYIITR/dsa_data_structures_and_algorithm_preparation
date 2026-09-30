"""
Basic Sorting: Bubble Sort, Selection Sort, and Insertion Sort

A self-contained executable study of three elementary comparison-based
sorting algorithms implemented from scratch.

The program demonstrates:
- comparisons and swaps
- stable versus unstable behavior
- in-place sorting
- best-case and worst-case behavior
- operation counting
- duplicate values
- already sorted and reverse-sorted input
- records with equal keys to make stability observable
- validation of algorithm results
"""

from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple
import random
import time


# ---------------------------------------------------------------------------
# Instrumentation
# ---------------------------------------------------------------------------

@dataclass
class SortStats:
    """Counts observable operations performed by a sorting algorithm."""
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0

    @property
    def operations(self) -> int:
        return self.comparisons + self.swaps + self.writes


Comparator = Callable[[object, object], bool]


def less_than(a: object, b: object) -> bool:
    """Default ascending-order comparison."""
    return a < b


def is_sorted(values: Sequence[object], before: Comparator = less_than) -> bool:
    """Return True when every adjacent pair is in the requested order."""
    return all(not before(values[index + 1], values[index])
               for index in range(len(values) - 1))


def swap_in_place(values: List[object], left: int, right: int, stats: SortStats) -> None:
    """Swap two elements and record the operation."""
    if left != right:
        values[left], values[right] = values[right], values[left]
        stats.swaps += 1
        stats.writes += 2


# ---------------------------------------------------------------------------
# Bubble sort
# ---------------------------------------------------------------------------

def bubble_sort(
    values: List[object],
    before: Comparator = less_than,
) -> SortStats:
    """
    Sort values in place using bubble sort.

    Adjacent elements are compared. When the right element belongs before
    the left element, the two are swapped. After each pass, the largest
    remaining element has moved to the end of the unsorted region.

    The early-exit check gives bubble sort a linear best case when the input
    is already sorted.
    """
    stats = SortStats()
    end = len(values) - 1

    while end > 0:
        swapped = False

        for index in range(end):
            stats.comparisons += 1

            if before(values[index + 1], values[index]):
                swap_in_place(values, index, index + 1, stats)
                swapped = True

        if not swapped:
            break

        end -= 1

    return stats


# ---------------------------------------------------------------------------
# Selection sort
# ---------------------------------------------------------------------------

def selection_sort(
    values: List[object],
    before: Comparator = less_than,
) -> SortStats:
    """
    Sort values in place using selection sort.

    For each position, scan the remaining unsorted region to locate the
    element that belongs at that position. Only after the scan completes is
    one swap performed.

    The algorithm deliberately uses a strict comparison when updating the
    selected index. Equal keys therefore retain their relative positions
    only when the surrounding movement happens not to disturb them; the
    algorithm itself is not stable in general.
    """
    stats = SortStats()
    size = len(values)

    for position in range(size - 1):
        selected = position

        for index in range(position + 1, size):
            stats.comparisons += 1

            if before(values[index], values[selected]):
                selected = index

        if selected != position:
            swap_in_place(values, position, selected, stats)

    return stats


# ---------------------------------------------------------------------------
# Insertion sort
# ---------------------------------------------------------------------------

def insertion_sort(
    values: List[object],
    before: Comparator = less_than,
) -> SortStats:
    """
    Sort values in place using insertion sort.

    The prefix before the current element is treated as sorted. Larger
    elements are shifted one position to the right until the current value
    can be inserted.

    The implementation uses a strict comparison. Equal elements are not
    shifted past one another, which preserves their relative order and makes
    insertion sort stable.
    """
    stats = SortStats()

    for position in range(1, len(values)):
        current = values[position]
        stats.writes += 1
        index = position - 1

        while index >= 0:
            stats.comparisons += 1

            if not before(current, values[index]):
                break

            values[index + 1] = values[index]
            stats.writes += 1
            index -= 1

        values[index + 1] = current
        stats.writes += 1

    return stats


# ---------------------------------------------------------------------------
# Demonstrating stability
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Student:
    """
    A record with a sorting key and original position.

    Sorting by score lets us inspect whether equal-score records remain in
    their original relative order.
    """
    name: str
    score: int
    original_position: int


def student_before(left: Student, right: Student) -> bool:
    """Sort students by score without comparing their names."""
    return left.score < right.score


def relative_order_by_score(
    students: Iterable[Student],
) -> dict[int, List[str]]:
    """Group names by score in the order in which they currently appear."""
    groups: dict[int, List[str]] = {}

    for student in students:
        groups.setdefault(student.score, []).append(student.name)

    return groups


def demonstrate_stability() -> None:
    """
    Show that insertion sort preserves equal-key order while selection sort
    can change it.

    The chosen data places equal scores around elements that selection sort
    moves, exposing the distinction between stable and unstable algorithms.
    """
    original = [
        Student("Asha", 80, 0),
        Student("Bharat", 70, 1),
        Student("Chen", 80, 2),
        Student("Divya", 60, 3),
        Student("Esha", 80, 4),
    ]

    algorithms = [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
    ]

    print("\nSTABILITY WITH RECORDS")
    print("-" * 72)
    print("Original equal-score order:", relative_order_by_score(original))

    for name, algorithm in algorithms:
        data = list(original)
        stats = algorithm(data, student_before)
        grouped = relative_order_by_score(data)

        print(f"\n{name}")
        print("Sorted:", [(student.name, student.score) for student in data])
        print("Equal-score order:", grouped)
        print("Stable for this input:", grouped == relative_order_by_score(original))
        print("Comparisons:", stats.comparisons)
        print("Swaps:", stats.swaps)
        print("Writes:", stats.writes)


# ---------------------------------------------------------------------------
# General demonstrations
# ---------------------------------------------------------------------------

def demonstrate_basic_sorting() -> None:
    """Run every algorithm against several meaningful integer inputs."""
    test_cases = {
        "empty": [],
        "single element": [42],
        "duplicates": [5, 2, 5, 1, 2, 5, 3],
        "already sorted": [1, 2, 3, 4, 5, 6],
        "reverse sorted": [6, 5, 4, 3, 2, 1],
        "mixed": [9, 1, 7, 3, 2, 8, 4, 6, 5],
    }

    algorithms = [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
    ]

    print("BASIC SORTING IMPLEMENTATIONS")
    print("=" * 72)

    for case_name, original in test_cases.items():
        print(f"\nInput: {case_name}")
        print("Original:", original)

        for algorithm_name, algorithm in algorithms:
            data = list(original)
            stats = algorithm(data)

            assert is_sorted(data), f"{algorithm_name} failed on {case_name}"

            print(
                f"{algorithm_name:16} -> {data!s:35} "
                f"comparisons={stats.comparisons:3} "
                f"swaps={stats.swaps:2} "
                f"writes={stats.writes:3}"
            )


# ---------------------------------------------------------------------------
# Ascending and descending ordering
# ---------------------------------------------------------------------------

def greater_than(a: object, b: object) -> bool:
    """Comparison used to produce descending order."""
    return a > b


def demonstrate_custom_order() -> None:
    """Show that the algorithms can use a different comparison rule."""
    original = [8, 3, 7, 4, 9, 2, 6, 1, 5]

    print("\nCUSTOM ORDER")
    print("-" * 72)
    print("Original:", original)

    for name, algorithm in [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
    ]:
        data = list(original)
        algorithm(data, greater_than)
        assert is_sorted(data, greater_than)
        print(f"{name:16} descending -> {data}")


# ---------------------------------------------------------------------------
# Best-case and worst-case operation behavior
# ---------------------------------------------------------------------------

def measure_operation_patterns() -> None:
    """
    Compare operation counts for favorable and unfavorable input order.

    For insertion and bubble sort, sorted data exposes their adaptive
    behavior. Selection sort still scans the entire remaining region because
    it must identify the minimum even when the input is already ordered.
    """
    algorithms = [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
    ]

    sizes = [5, 10, 20, 40]

    print("\nBEST-CASE AND WORST-CASE OPERATION PATTERNS")
    print("-" * 96)
    print(
        f"{'Algorithm':16} {'N':>4} "
        f"{'Sorted comparisons':>20} {'Sorted swaps':>15} "
        f"{'Reverse comparisons':>21} {'Reverse swaps':>16}"
    )

    for size in sizes:
        sorted_values = list(range(size))
        reverse_values = list(reversed(sorted_values))

        for name, algorithm in algorithms:
            best_data = list(sorted_values)
            best_stats = algorithm(best_data)

            worst_data = list(reverse_values)
            worst_stats = algorithm(worst_data)

            print(
                f"{name:16} {size:4} "
                f"{best_stats.comparisons:20} {best_stats.swaps:15} "
                f"{worst_stats.comparisons:21} {worst_stats.swaps:16}"
            )


# ---------------------------------------------------------------------------
# Correctness checking against Python's reference sort
# ---------------------------------------------------------------------------

def randomized_correctness_test() -> None:
    """
    Run deterministic randomized tests.

    Python's sorted() is used only as a correctness oracle. The three
    algorithms themselves perform all sorting work without relying on a
    library sorting routine.
    """
    random_generator = random.Random(20260930)

    algorithms = [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
    ]

    total_tests = 0

    for _ in range(100):
        size = random_generator.randint(0, 30)
        original = [
            random_generator.randint(-20, 20)
            for _ in range(size)
        ]
        expected = sorted(original)

        for name, algorithm in algorithms:
            candidate = list(original)
            algorithm(candidate)

            if candidate != expected:
                raise AssertionError(
                    f"{name} failed.\n"
                    f"Input: {original}\n"
                    f"Expected: {expected}\n"
                    f"Actual: {candidate}"
                )

            total_tests += 1

    print("\nRANDOMIZED CORRECTNESS")
    print("-" * 72)
    print(f"Passed {total_tests} algorithm/input combinations.")


# ---------------------------------------------------------------------------
# Timing experiment
# ---------------------------------------------------------------------------

def benchmark_small_inputs() -> None:
    """
    Measure elapsed time on modest inputs.

    These are educational measurements rather than rigorous benchmarks.
    Timing is affected by the Python interpreter, operating system,
    background processes, and hardware.
    """
    random_generator = random.Random(7)
    size = 800

    original = [
        random_generator.randint(0, 100_000)
        for _ in range(size)
    ]

    print("\nSMALL PERFORMANCE EXPERIMENT")
    print("-" * 72)
    print(f"Input size: {size}")

    for name, algorithm in [
        ("Bubble sort", bubble_sort),
        ("Selection sort", selection_sort),
        ("Insertion sort", insertion_sort),
    ]:
        data = list(original)

        start = time.perf_counter()
        stats = algorithm(data)
        elapsed = time.perf_counter() - start

        assert is_sorted(data)

        print(
            f"{name:16} "
            f"time={elapsed:.6f}s "
            f"comparisons={stats.comparisons} "
            f"swaps={stats.swaps}"
        )


# ---------------------------------------------------------------------------
# Complexity reference implemented as data
# ---------------------------------------------------------------------------

def display_complexity() -> None:
    """
    Display the theoretical properties demonstrated by the implementations.

    Bubble sort here includes an early-exit optimization, so its best case
    is O(n). Selection sort remains O(n^2) even for sorted input. Insertion
    sort reaches O(n) when the input is already sorted.
    """
    rows = [
        (
            "Bubble sort",
            "O(n)",
            "O(n^2)",
            "O(n^2)",
            "Yes",
            "Yes",
        ),
        (
            "Selection sort",
            "O(n^2)",
            "O(n^2)",
            "O(n^2)",
            "No",
            "Yes",
        ),
        (
            "Insertion sort",
            "O(n)",
            "O(n^2)",
            "O(n^2)",
            "Yes",
            "Yes",
        ),
    ]

    print("\nCOMPLEXITY AND PROPERTIES")
    print("-" * 88)
    print(
        f"{'Algorithm':16} {'Best':>10} {'Average':>12} "
        f"{'Worst':>10} {'Stable':>10} {'In-place':>12}"
    )

    for row in rows:
        print(
            f"{row[0]:16} {row[1]:>10} {row[2]:>12} "
            f"{row[3]:>10} {row[4]:>10} {row[5]:>12}"
        )


# ---------------------------------------------------------------------------
# Educational edge cases
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Exercise conditions that frequently reveal implementation errors."""
    edge_cases = [
        [],
        [1],
        [2, 1],
        [1, 2],
        [3, 3, 3],
        [-3, -1, -2, 0],
        [10, -10, 10, -10, 0],
    ]

    print("\nEDGE CASE VALIDATION")
    print("-" * 72)

    for original in edge_cases:
        for name, algorithm in [
            ("Bubble", bubble_sort),
            ("Selection", selection_sort),
            ("Insertion", insertion_sort),
        ]:
            data = list(original)
            algorithm(data)
            expected = sorted(original)

            assert data == expected, (
                f"{name} failed for {original}: got {data}"
            )

        print(f"{original!s:35} -> {sorted(original)}")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main() -> None:
    demonstrate_basic_sorting()
    demonstrate_custom_order()
    demonstrate_stability()
    demonstrate_edge_cases()
    measure_operation_patterns()
    randomized_correctness_test()
    display_complexity()
    benchmark_small_inputs()

    print("\nKEY IMPLEMENTATION OBSERVATIONS")
    print("-" * 72)
    print(
        "Bubble sort repeatedly compares neighboring elements and swaps "
        "them when they are out of order. Its early-exit condition makes "
        "already sorted input especially efficient."
    )
    print(
        "Selection sort searches the remaining unsorted region before "
        "performing a swap. It therefore performs few swaps but remains "
        "quadratic in comparisons."
    )
    print(
        "Insertion sort grows a sorted prefix and shifts larger elements "
        "rather than repeatedly swapping adjacent elements. It is stable "
        "and performs particularly well on nearly sorted data."
    )
    print(
        "All three implementations modify the supplied list directly, so "
        "their auxiliary sorting space is O(1), excluding the storage used "
        "by the caller for the input itself."
    )


if __name__ == "__main__":
    main()
