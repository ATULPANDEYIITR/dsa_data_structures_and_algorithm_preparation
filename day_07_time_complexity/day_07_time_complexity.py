"""
Day 7 — Time Complexity
A self-contained study and practice program covering running time,
constant operations, loops, nested loops, sequential operations,
halving/doubling loops, Big O notation, and simple recursion.

The program is intentionally written as an executable teaching file.
Run it with Python 3. The demonstrations use only the Python standard
library.
"""

from __future__ import annotations

import math
import random
import sys
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple


# ============================================================================
# 1. FUNDAMENTAL IDEAS
# ============================================================================

def print_section(title: str) -> None:
    """Print a clearly separated study section."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def constant_operation(value: int) -> int:
    """
    O(1): the amount of work does not depend on the size of the input.

    Accessing one list element is treated as constant-time in the usual
    array/list complexity model.
    """
    if not value:
        return 0
    return value * 2


def linear_sum(numbers: Sequence[int]) -> int:
    """
    O(n): every element is visited once.

    n = len(numbers)
    The loop body executes n times.
    """
    total = 0
    for number in numbers:
        total += number
    return total


def nested_pair_count(numbers: Sequence[int]) -> int:
    """
    O(n^2): for every element, the program examines every element again.

    The exact number of inner-loop executions is n * n.
    """
    count = 0
    for _ in numbers:
        for _ in numbers:
            count += 1
    return count


def triangular_pair_count(numbers: Sequence[int]) -> int:
    """
    O(n^2), even though the inner loop becomes shorter.

    The number of iterations is approximately:
        n + (n-1) + ... + 1
        = n(n+1)/2
        = O(n^2)
    """
    count = 0
    for i in range(len(numbers)):
        for j in range(i, len(numbers)):
            count += 1
    return count


def cubic_operation(n: int) -> int:
    """
    O(n^3): three independently growing loops.

    This function does not store the generated triples. It simply counts
    them so that the algorithm remains memory efficient.
    """
    count = 0
    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                count += 1
    return count


# ============================================================================
# 2. LOGARITHMIC ALGORITHMS
# ============================================================================

def halving_steps(n: int) -> int:
    """
    O(log n): repeatedly divide the problem size by two.

    Example:
        64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1

    The number of iterations is approximately log2(n).
    """
    if n <= 1:
        return 0

    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps


def doubling_steps(n: int) -> int:
    """
    O(log n): repeatedly double a value until it reaches n.

    Example:
        1 -> 2 -> 4 -> 8 -> 16 -> ...

    The number of iterations is approximately log2(n).
    """
    if n <= 1:
        return 0

    value = 1
    steps = 0

    while value < n:
        value *= 2
        steps += 1

    return steps


def binary_search(sorted_numbers: Sequence[int], target: int) -> int:
    """
    O(log n) time, O(1) auxiliary space.

    Binary search repeatedly eliminates approximately half of the remaining
    search space.

    Returns the index of target, or -1 when target is absent.
    """
    left = 0
    right = len(sorted_numbers) - 1

    while left <= right:
        middle = (left + right) // 2

        if sorted_numbers[middle] == target:
            return middle

        if sorted_numbers[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


# ============================================================================
# 3. N LOG N EXAMPLE
# ============================================================================

def merge(left: List[int], right: List[int]) -> List[int]:
    """Merge two already sorted lists in O(len(left) + len(right))."""
    result: List[int] = []
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


def merge_sort(numbers: Sequence[int]) -> List[int]:
    """
    O(n log n) time and O(n) auxiliary space.

    The array is divided recursively until individual elements remain.
    The sorted pieces are then merged.

    Recursion depth is O(log n).
    """
    if len(numbers) <= 1:
        return list(numbers)

    middle = len(numbers) // 2
    left = merge_sort(numbers[:middle])
    right = merge_sort(numbers[middle:])

    return merge(left, right)


# ============================================================================
# 4. SEQUENTIAL OPERATIONS
# ============================================================================

def sequential_linear_work(numbers: Sequence[int]) -> int:
    """
    Two sequential O(n) loops remain O(n), not O(n^2).

    O(n) + O(n) = O(2n) = O(n)
    """
    total = 0

    for number in numbers:
        total += number

    for number in numbers:
        total += number * 2

    return total


def linear_then_quadratic(numbers: Sequence[int]) -> int:
    """
    O(n) followed by O(n^2):

        O(n) + O(n^2) = O(n^2)

    The dominant growth term determines the final Big O classification.
    """
    total = 0

    for number in numbers:
        total += number

    for first in numbers:
        for second in numbers:
            total += first * second

    return total


# ============================================================================
# 5. COMMON LOOP PATTERNS
# ============================================================================

def count_single_loop(n: int) -> int:
    """A single loop: O(n)."""
    count = 0
    for _ in range(max(0, n)):
        count += 1
    return count


def count_nested_loops(n: int) -> int:
    """Two independent loops nested inside one another: O(n^2)."""
    count = 0
    for _ in range(max(0, n)):
        for _ in range(max(0, n)):
            count += 1
    return count


def count_three_nested_loops(n: int) -> int:
    """Three independent loops: O(n^3)."""
    count = 0
    for _ in range(max(0, n)):
        for _ in range(max(0, n)):
            for _ in range(max(0, n)):
                count += 1
    return count


def loop_with_halving(n: int) -> int:
    """A loop that halves n each time: O(log n)."""
    if n <= 0:
        return 0

    count = 0
    while n > 1:
        n //= 2
        count += 1

    return count


def loop_with_doubling(n: int) -> int:
    """A loop whose control value doubles: O(log n)."""
    if n <= 1:
        return 0

    value = 1
    count = 0

    while value < n:
        value *= 2
        count += 1

    return count


def dependent_nested_loop(n: int) -> int:
    """
    Another important O(n^2) pattern.

    The inner loop depends on the outer loop, but the total is still
    proportional to n^2:
        1 + 2 + ... + n = n(n+1)/2
    """
    count = 0

    for i in range(1, max(0, n) + 1):
        for _ in range(i):
            count += 1

    return count


def logarithmic_inner_loop(n: int) -> int:
    """
    O(n log n).

    The outer loop executes n times, and for each outer iteration the
    inner loop performs logarithmic work.
    """
    if n <= 0:
        return 0

    total = 0

    for _ in range(n):
        value = n
        while value > 1:
            value //= 2
            total += 1

    return total


# ============================================================================
# 6. SIMPLE RECURSION
# ============================================================================

def recursive_countdown(n: int) -> int:
    """
    O(n) time and O(n) call-stack space.

    Each recursive call decreases n by one.
    """
    if n <= 0:
        return 0
    return 1 + recursive_countdown(n - 1)


def recursive_binary_search(
    sorted_numbers: Sequence[int],
    target: int,
    left: int = 0,
    right: int | None = None,
) -> int:
    """
    O(log n) time.

    The search interval is halved at each recursive call.
    Auxiliary space is O(log n) because of recursion depth.
    """
    if right is None:
        right = len(sorted_numbers) - 1

    if left > right:
        return -1

    middle = (left + right) // 2

    if sorted_numbers[middle] == target:
        return middle

    if sorted_numbers[middle] < target:
        return recursive_binary_search(
            sorted_numbers, target, middle + 1, right
        )

    return recursive_binary_search(
        sorted_numbers, target, left, middle - 1
    )


def naive_fibonacci(n: int) -> int:
    """
    Exponential-time example.

    The recurrence is approximately:
        T(n) = T(n-1) + T(n-2) + O(1)

    Therefore the running time grows exponentially.

    This implementation is intentionally inefficient because it demonstrates
    why recursive structure matters when analyzing time complexity.
    """
    if n <= 1:
        return n

    return naive_fibonacci(n - 1) + naive_fibonacci(n - 2)


def fibonacci_dynamic(n: int) -> int:
    """
    O(n) time and O(1) extra space.

    Previously calculated values are retained instead of recomputed.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n <= 1:
        return n

    previous = 0
    current = 1

    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current


# ============================================================================
# 7. BEST, AVERAGE, AND WORST CASES
# ============================================================================

def linear_search(numbers: Sequence[int], target: int) -> int:
    """
    Linear search:
        Best case: O(1)
        Average case: O(n)
        Worst case: O(n)

    The overall algorithm is normally described as O(n) because the worst
    case grows linearly.
    """
    for index, number in enumerate(numbers):
        if number == target:
            return index

    return -1


# ============================================================================
# 8. BIG O IS ABOUT GROWTH, NOT EXACT RUNTIME
# ============================================================================

def operation_count_example(n: int) -> int:
    """
    An artificial algorithm with:

        3n^2 + 7n + 10

    primitive-style operations.

    Big O ignores constants and lower-order terms:

        O(3n^2 + 7n + 10)
        = O(n^2)
    """
    return 3 * n * n + 7 * n + 10


def demonstrate_dominant_terms() -> None:
    print("Expression: 3n^2 + 7n + 10")
    print("n = 1   ->", operation_count_example(1))
    print("n = 10  ->", operation_count_example(10))
    print("n = 100 ->", operation_count_example(100))
    print("Classification: O(n^2)")


# ============================================================================
# 9. COMPLEXITY CLASSIFICATION HELPER
# ============================================================================

@dataclass(frozen=True)
class ComplexityExample:
    name: str
    complexity: str
    explanation: str


COMPLEXITY_TABLE = [
    ComplexityExample(
        "Constant operation",
        "O(1)",
        "The amount of work does not grow with n.",
    ),
    ComplexityExample(
        "Binary search",
        "O(log n)",
        "The search space is approximately halved each iteration.",
    ),
    ComplexityExample(
        "Single loop",
        "O(n)",
        "One operation is performed for each input element.",
    ),
    ComplexityExample(
        "Merge sort",
        "O(n log n)",
        "There are logarithmic levels and linear work per level.",
    ),
    ComplexityExample(
        "Two independent nested loops",
        "O(n^2)",
        "Each of n outer iterations performs n inner iterations.",
    ),
    ComplexityExample(
        "Three independent nested loops",
        "O(n^3)",
        "Each of n^2 combinations performs another n operations.",
    ),
]


def print_complexity_table() -> None:
    for example in COMPLEXITY_TABLE:
        print(f"{example.name:30} {example.complexity:10} {example.explanation}")


# ============================================================================
# 10. EDGE CASES
# ============================================================================

def safe_log2(n: int) -> float:
    """
    Return log2(n) for positive n.

    log(0) and log(negative numbers) are undefined in the real-number
    setting, so those inputs are rejected explicitly.
    """
    if n <= 0:
        raise ValueError("log2 is defined here only for positive integers")
    return math.log2(n)


def demonstrate_edge_cases() -> None:
    print("Empty linear search:", linear_search([], 10))
    print("Empty merge sort:", merge_sort([]))
    print("Single-item merge sort:", merge_sort([7]))
    print("Halving 1:", halving_steps(1))
    print("Doubling to 1:", doubling_steps(1))

    for invalid_value in [0, -1]:
        try:
            safe_log2(invalid_value)
        except ValueError as error:
            print(f"safe_log2({invalid_value}) -> {error}")


# ============================================================================
# 11. TIMING EXPERIMENT
# ============================================================================

def measure_runtime(
    function: Callable[..., object],
    *arguments: object,
    repetitions: int = 1,
) -> float:
    """
    Measure elapsed wall-clock time.

    This is useful for experiments, but measured time is not the same thing
    as asymptotic complexity. Hardware, interpreter overhead, caches, input
    values, operating-system scheduling, and many other factors influence it.
    """
    start = time.perf_counter()

    for _ in range(repetitions):
        function(*arguments)

    elapsed = time.perf_counter() - start
    return elapsed / repetitions


def runtime_experiment() -> None:
    print_section("RUNTIME EXPERIMENT")

    sizes = [100, 500, 1_000, 2_000]

    print(f"{'n':>8} {'O(n)':>14} {'O(n²)':>14}")
    print("-" * 42)

    for n in sizes:
        data = list(range(n))

        linear_time = measure_runtime(linear_sum, data)

        # Keep the quadratic experiment bounded so the study script remains
        # practical on ordinary computers.
        quadratic_n = min(n, 2_000)
        quadratic_data = list(range(quadratic_n))
        quadratic_time = measure_runtime(
            nested_pair_count,
            quadratic_data,
        )

        print(
            f"{n:>8} "
            f"{linear_time:>14.8f} "
            f"{quadratic_time:>14.8f}"
        )


# ============================================================================
# 12. PRACTICAL ALGORITHM COMPARISON
# ============================================================================

def compare_search_algorithms() -> None:
    print_section("LINEAR SEARCH VS BINARY SEARCH")

    data = list(range(0, 100_000, 2))
    target = 98_765

    linear_start = time.perf_counter()
    linear_result = linear_search(data, target)
    linear_elapsed = time.perf_counter() - linear_start

    binary_start = time.perf_counter()
    binary_result = binary_search(data, target)
    binary_elapsed = time.perf_counter() - binary_start

    print("Target:", target)
    print("Linear result:", linear_result)
    print("Binary result:", binary_result)
    print(f"Linear elapsed time: {linear_elapsed:.8f} seconds")
    print(f"Binary elapsed time: {binary_elapsed:.8f} seconds")
    print()
    print("Linear search: O(n)")
    print("Binary search: O(log n)")
    print("Binary search requires sorted data.")


# ============================================================================
# 13. RANDOMIZED PRACTICE DATA
# ============================================================================

def generate_practice_data(size: int, seed: int = 7) -> List[int]:
    """Create reproducible random data for algorithm demonstrations."""
    if size < 0:
        raise ValueError("size cannot be negative")

    generator = random.Random(seed)
    return [generator.randint(-1000, 1000) for _ in range(size)]


def practice_merge_sort() -> None:
    data = generate_practice_data(20)
    sorted_data = merge_sort(data)

    print("Original:", data)
    print("Sorted:  ", sorted_data)
    print("Correct:", sorted_data == sorted(data))


# ============================================================================
# 14. AUTOMATED CORRECTNESS TESTS
# ============================================================================

def run_tests() -> None:
    print_section("CORRECTNESS TESTS")

    assert constant_operation(5) == 10
    assert linear_sum([]) == 0
    assert linear_sum([1, 2, 3, 4]) == 10

    assert nested_pair_count([]) == 0
    assert nested_pair_count([1, 2, 3]) == 9

    assert triangular_pair_count([1, 2, 3, 4]) == 10
    assert cubic_operation(3) == 27

    assert halving_steps(1) == 0
    assert halving_steps(2) == 1
    assert halving_steps(8) == 3
    assert doubling_steps(1) == 0
    assert doubling_steps(8) == 3

    sorted_data = [2, 4, 6, 8, 10, 12, 14]
    assert binary_search(sorted_data, 2) == 0
    assert binary_search(sorted_data, 14) == 6
    assert binary_search(sorted_data, 9) == -1

    assert recursive_binary_search(sorted_data, 8) == 3
    assert recursive_binary_search(sorted_data, 9) == -1

    assert merge_sort([]) == []
    assert merge_sort([3, 1, 2]) == [1, 2, 3]
    assert merge_sort([5, 5, 1, -2]) == [-2, 1, 5, 5]

    assert recursive_countdown(5) == 5
    assert naive_fibonacci(10) == 55

    for n in range(20):
        assert fibonacci_dynamic(n) == naive_fibonacci(n)

    assert linear_search([10, 20, 30], 10) == 0
    assert linear_search([10, 20, 30], 30) == 2
    assert linear_search([10, 20, 30], 99) == -1

    print("All correctness tests passed.")


# ============================================================================
# 15. PRACTICE QUESTIONS
# ============================================================================

def practice_analysis_questions() -> None:
    print_section("PRACTICE ANALYSIS")

    questions = [
        (
            "1. One loop from 0 to n-1",
            "O(n)",
        ),
        (
            "2. Two nested loops, each running n times",
            "O(n^2)",
        ),
        (
            "3. Three nested loops, each running n times",
            "O(n^3)",
        ),
        (
            "4. A value is repeatedly divided by 2",
            "O(log n)",
        ),
        (
            "5. n iterations, each containing a halving loop",
            "O(n log n)",
        ),
        (
            "6. O(n) loop followed by another O(n) loop",
            "O(n)",
        ),
        (
            "7. O(n) loop followed by O(n^2) nested loops",
            "O(n^2)",
        ),
        (
            "8. Recursive function calling itself once with n-1",
            "O(n)",
        ),
        (
            "9. Recursive binary search",
            "O(log n)",
        ),
        (
            "10. Naive recursive Fibonacci",
            "Exponential time",
        ),
    ]

    for question, answer in questions:
        print(f"{question:65} -> {answer}")


# ============================================================================
# 16. SPACE COMPLEXITY
# ============================================================================

def iterative_sum(numbers: Sequence[int]) -> int:
    """
    O(n) time and O(1) auxiliary space.

    The input itself occupies memory, but the algorithm creates only a fixed
    number of additional variables.
    """
    total = 0
    for number in numbers:
        total += number
    return total


def copied_sum(numbers: Sequence[int]) -> int:
    """
    O(n) time and O(n) auxiliary space because a new list is created.

    The distinction between input space and auxiliary space matters when
    discussing algorithm memory usage.
    """
    copied_numbers = list(numbers)
    return sum(copied_numbers)


# ============================================================================
# 17. INPUT SIZE AND PRACTICAL SCALING
# ============================================================================

def approximate_operation_counts(n: int) -> dict[str, float]:
    """
    Give rough operation counts for common growth classes.

    These are mathematical growth estimates, not predictions of actual
    processor instructions or seconds.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    return {
        "O(1)": 1,
        "O(log2 n)": math.log2(n),
        "O(n)": n,
        "O(n log2 n)": n * math.log2(n),
        "O(n^2)": n * n,
        "O(n^3)": n * n * n,
    }


def print_scaling_table() -> None:
    print_section("SCALING WITH INPUT SIZE")

    sizes = [10, 100, 1_000, 10_000]

    header = (
        f"{'n':>8}"
        f"{'log n':>14}"
        f"{'n':>14}"
        f"{'n log n':>18}"
        f"{'n²':>18}"
        f"{'n³':>22}"
    )
    print(header)
    print("-" * len(header))

    for n in sizes:
        values = approximate_operation_counts(n)
        print(
            f"{n:>8}"
            f"{values['O(log2 n)']:>14.2f}"
            f"{values['O(n)']:>14.0f}"
            f"{values['O(n log2 n)']:>18.2f}"
            f"{values['O(n^2)']:>18.0f}"
            f"{values['O(n^3)']:>22.0f}"
        )


# ============================================================================
# 18. IMPORTANT DISTINCTIONS
# ============================================================================

def explain_key_distinctions() -> None:
    print_section("KEY DISTINCTIONS")

    distinctions = [
        (
            "Big O vs exact runtime",
            "Big O describes asymptotic growth; it does not give seconds.",
        ),
        (
            "O(2n) vs O(n)",
            "Constants are ignored for asymptotic classification.",
        ),
        (
            "O(n + n²)",
            "The highest-growth term dominates, so the result is O(n²).",
        ),
        (
            "Nested vs sequential loops",
            "Nesting often multiplies work; sequential work is added.",
        ),
        (
            "Time vs space",
            "An algorithm can be fast but use more memory, or save memory at a time cost.",
        ),
        (
            "Best vs worst case",
            "Different input arrangements can produce different actual work.",
        ),
        (
            "Logarithm base",
            "For Big O, constant logarithm bases are equivalent: O(log2 n) = O(log10 n).",
        ),
    ]

    for topic, explanation in distinctions:
        print(f"{topic}: {explanation}")


# ============================================================================
# 19. MAIN STUDY SESSION
# ============================================================================

def main() -> None:
    print_section("DAY 7 — TIME COMPLEXITY")

    print(
        """
Time complexity describes how the amount of computational work grows as
the input size n grows.

The most important beginner-level growth classes in this study are:

    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) linearithmic
    O(n²)      quadratic
    O(n³)      cubic

Big O normally focuses on asymptotic growth rather than exact machine time.
That means constants and lower-order terms are removed when classifying
an algorithm.

Examples:
    5n + 20       -> O(n)
    3n² + 7n + 10 -> O(n²)
    8log(n) + 4   -> O(log n)
"""
    )

    print_section("CONSTANT, LINEAR, QUADRATIC, AND CUBIC")
    data = [1, 2, 3, 4]
    print("O(1) result:", constant_operation(10))
    print("O(n) result:", linear_sum(data))
    print("O(n²) operation count:", nested_pair_count(data))
    print("O(n³) operation count for n=4:", cubic_operation(4))

    print_section("LOGARITHMIC LOOPS")
    for n in [1, 2, 4, 8, 16, 32, 64]:
        print(
            f"n={n:>2} | "
            f"halving steps={halving_steps(n):>2} | "
            f"doubling steps={doubling_steps(n):>2}"
        )

    print_section("N LOG N")
    data = [9, 1, 8, 2, 7, 3, 6, 4, 5]
    print("Before:", data)
    print("After: ", merge_sort(data))

    print_section("SEQUENTIAL OPERATIONS")
    print("Two O(n) loops:", sequential_linear_work(list(range(5))))
    print("O(n) + O(n²):", linear_then_quadratic(list(range(5))))

    print_section("RECURSION")
    print("recursive_countdown(5):", recursive_countdown(5))
    print("naive_fibonacci(10):", naive_fibonacci(10))
    print("dynamic_fibonacci(10):", fibonacci_dynamic(10))

    print_section("BINARY SEARCH")
    sorted_numbers = list(range(0, 100, 5))
    print("Data:", sorted_numbers)
    print("Search 50:", binary_search(sorted_numbers, 50))
    print("Search 51:", binary_search(sorted_numbers, 51))

    print_section("COMPLEXITY CLASSIFICATION TABLE")
    print_complexity_table()

    demonstrate_dominant_terms()
    explain_key_distinctions()
    demonstrate_edge_cases()
    practice_merge_sort()
    run_tests()
    practice_analysis_questions()
    print_scaling_table()

    # The timing section is deliberately run near the end because measured
    # performance varies by machine and is not a substitute for analysis.
    runtime_experiment()
    compare_search_algorithms()

    print_section("STUDY FILE COMPLETED")
    print(
        "The examples above demonstrate how to identify common growth "
        "patterns from loops, sequential operations, halving/doubling, "
        "sorting, searching, and recursion."
    )


if __name__ == "__main__":
    # Increase the recursion limit modestly for educational demonstrations,
    # while avoiding an unnecessarily large limit that could make accidental
    # runaway recursion dangerous.
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 2000))
    main()
