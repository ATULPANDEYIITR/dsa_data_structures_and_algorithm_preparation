"""
Day 11 — Complexity Practice

This study script teaches algorithmic complexity by taking familiar algorithmic
problems and analyzing their approach, time complexity, space complexity, and
possible optimizations.

The central skill is not memorizing Big-O expressions. It is learning to look
at unfamiliar code, identify the operations that grow with the input, count
repetitions, identify additional memory, and estimate the dominant growth rate.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional
import random
import time


# ============================================================================
# 1. FOUNDATIONS
# ============================================================================

def explain_complexity_basics() -> None:
    """
    Introduce the main complexity concepts.

    Time complexity describes how the amount of computation grows as input size
    grows.

    Space complexity describes how much additional memory an algorithm needs
    as input size grows.

    Big-O describes an asymptotic upper-growth classification. In practice,
    we usually focus on the dominant term and ignore constants.

    Examples:
        5n + 20      -> O(n)
        3n^2 + 2n + 1 -> O(n^2)
        n + log(n)   -> O(n)
        7            -> O(1)
    """

    examples = {
        "constant": "O(1)",
        "logarithmic": "O(log n)",
        "linear": "O(n)",
        "linearithmic": "O(n log n)",
        "quadratic": "O(n^2)",
        "cubic": "O(n^3)",
        "exponential": "O(2^n)",
        "factorial": "O(n!)",
    }

    print("\n=== Common Complexity Classes ===")
    for name, notation in examples.items():
        print(f"{name:15} {notation}")

    print("\nImportant rules:")
    print("1. Ignore constants: O(5n) becomes O(n).")
    print("2. Keep the dominant term: O(n^2 + n) becomes O(n^2).")
    print("3. Sequential loops usually add their costs.")
    print("4. Nested loops usually multiply their costs.")
    print("5. Independent inputs should not automatically be treated as one n.")
    print("6. Recursion requires analysis of both branching and depth.")
    print("7. Auxiliary data structures contribute to extra space.")
    print("8. Input storage itself is normally distinguished from auxiliary space.")


# ============================================================================
# 2. A STRUCTURED WAY TO RECORD ANALYSIS
# ============================================================================

@dataclass
class ComplexityAnalysis:
    approach: str
    time_complexity: str
    space_complexity: str
    possible_optimization: str

    def display(self, title: str) -> None:
        print(f"\n=== {title} ===")
        print(f"Approach:             {self.approach}")
        print(f"Time Complexity:      {self.time_complexity}")
        print(f"Space Complexity:     {self.space_complexity}")
        print(f"Possible Optimization:{self.possible_optimization}")


# ============================================================================
# 3. CONSTANT-TIME EXAMPLE
# ============================================================================

def get_first_element(values: list[int]) -> Optional[int]:
    """Array indexing does not depend on list length."""
    if not values:
        return None
    return values[0]


CONSTANT_TIME_ANALYSIS = ComplexityAnalysis(
    approach="Directly access the first element using an index.",
    time_complexity="O(1)",
    space_complexity="O(1) auxiliary space.",
    possible_optimization="No meaningful asymptotic optimization is required.",
)


# ============================================================================
# 4. LINEAR SEARCH
# ============================================================================

def linear_search(values: list[int], target: int) -> int:
    """
    Search from left to right.

    Best case:
        target is the first element -> O(1)

    Average/worst case:
        many or all elements may be inspected -> O(n)

    Auxiliary space:
        only a few variables are used -> O(1)
    """
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


LINEAR_SEARCH_ANALYSIS = ComplexityAnalysis(
    approach="Inspect each element from left to right until the target is found.",
    time_complexity="O(n) worst case; O(1) best case.",
    space_complexity="O(1) auxiliary space.",
    possible_optimization=(
        "If the data is sorted and random access is available, binary search "
        "can reduce search time to O(log n)."
    ),
)


# ============================================================================
# 5. BINARY SEARCH
# ============================================================================

def binary_search(sorted_values: list[int], target: int) -> int:
    """
    Binary search repeatedly discards half of the remaining search space.

    The input must be sorted.

    Number of remaining candidates approximately follows:
        n, n/2, n/4, n/8, ...

    After k divisions:
        n / 2^k

    The search ends when:
        n / 2^k <= 1

    Therefore:
        k >= log2(n)

    Time: O(log n)
    Auxiliary space: O(1)
    """
    left = 0
    right = len(sorted_values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if sorted_values[middle] == target:
            return middle

        if sorted_values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


BINARY_SEARCH_ANALYSIS = ComplexityAnalysis(
    approach="Repeatedly discard half of a sorted search interval.",
    time_complexity="O(log n)",
    space_complexity="O(1) auxiliary space for the iterative version.",
    possible_optimization=(
        "The asymptotic search complexity is already logarithmic. "
        "The main practical optimization is maintaining sorted data efficiently."
    ),
)


# ============================================================================
# 6. ONE LOOP: O(n)
# ============================================================================

def sum_values(values: list[int]) -> int:
    """One pass over n elements performs n iterations."""
    total = 0

    for value in values:
        total += value

    return total


ONE_LOOP_ANALYSIS = ComplexityAnalysis(
    approach="Visit every element exactly once and accumulate its value.",
    time_complexity="O(n)",
    space_complexity="O(1) auxiliary space.",
    possible_optimization="A complete sum requires examining all elements, so O(n) is asymptotically optimal.",
)


# ============================================================================
# 7. TWO SEQUENTIAL LOOPS: STILL O(n)
# ============================================================================

def sequential_processing(values: list[int]) -> tuple[int, int]:
    """
    Two loops execute one after another.

    First loop: n operations.
    Second loop: n operations.

    Total:
        n + n = 2n

    Drop the constant:
        O(n)
    """
    total = 0
    maximum = None

    for value in values:
        total += value

    for value in values:
        if maximum is None or value > maximum:
            maximum = value

    return total, 0 if maximum is None else maximum


SEQUENTIAL_LOOPS_ANALYSIS = ComplexityAnalysis(
    approach="Perform two independent linear scans sequentially.",
    time_complexity="O(n + n) = O(n)",
    space_complexity="O(1) auxiliary space.",
    possible_optimization=(
        "The two scans can be combined into one pass when their operations are "
        "compatible, reducing constants while remaining O(n)."
    ),
)


# ============================================================================
# 8. NESTED LOOPS: O(n^2)
# ============================================================================

def all_pairs(values: list[int]) -> list[tuple[int, int]]:
    """
    Generate every ordered pair.

    For n elements:
        outer loop -> n iterations
        inner loop -> n iterations

    Total:
        n * n = n^2

    Therefore:
        O(n^2)
    """
    pairs = []

    for first in values:
        for second in values:
            pairs.append((first, second))

    return pairs


ALL_PAIRS_ANALYSIS = ComplexityAnalysis(
    approach="Compare every element with every element.",
    time_complexity="O(n^2)",
    space_complexity="O(n^2) if all pairs are stored; O(1) extra if processed one at a time.",
    possible_optimization=(
        "Do not store every pair unless required. For a specific search problem, "
        "hashing or sorting may reduce the computational complexity."
    ),
)


# ============================================================================
# 9. TRIANGULAR NESTED LOOP
# ============================================================================

def unique_pairs(values: list[int]) -> list[tuple[int, int]]:
    """
    Generate each unordered pair exactly once.

    Number of generated pairs:
        n(n - 1) / 2

    This is still:
        O(n^2)
    """
    pairs = []

    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            pairs.append((values[i], values[j]))

    return pairs


UNIQUE_PAIRS_ANALYSIS = ComplexityAnalysis(
    approach="Use the second loop's starting position to avoid duplicate pairs.",
    time_complexity="O(n^2)",
    space_complexity="O(n^2) when storing all generated pairs.",
    possible_optimization=(
        "The loop avoids unnecessary duplicate work, improving the constant "
        "factor, but the asymptotic bound remains quadratic."
    ),
)


# ============================================================================
# 10. LOGARITHMIC LOOP
# ============================================================================

def count_halvings(value: int) -> int:
    """
    Divide by two repeatedly.

    Example:
        64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1

    The number of iterations is proportional to log2(value).
    """
    if value < 1:
        raise ValueError("value must be at least 1")

    steps = 0

    while value > 1:
        value //= 2
        steps += 1

    return steps


LOGARITHMIC_ANALYSIS = ComplexityAnalysis(
    approach="Repeatedly reduce the problem size by a constant factor.",
    time_complexity="O(log n)",
    space_complexity="O(1)",
    possible_optimization="No asymptotically smaller general bound is obtained by simply changing the loop syntax.",
)


# ============================================================================
# 11. O(n log n): MERGE SORT
# ============================================================================

def merge(left: list[int], right: list[int]) -> list[int]:
    """Merge two already sorted lists in linear time."""
    result = []
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


def merge_sort(values: list[int]) -> list[int]:
    """
    Divide-and-conquer sorting.

    Recurrence:
        T(n) = 2T(n/2) + O(n)

    Therefore:
        T(n) = O(n log n)

    The merge step requires additional storage proportional to n.
    """
    if len(values) <= 1:
        return values.copy()

    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    return merge(left, right)


MERGE_SORT_ANALYSIS = ComplexityAnalysis(
    approach="Recursively divide the list into halves and linearly merge sorted halves.",
    time_complexity="O(n log n)",
    space_complexity="O(n) auxiliary data for merging, plus recursion overhead.",
    possible_optimization=(
        "In-place algorithms can reduce auxiliary memory, while optimized "
        "library sorting implementations may improve practical performance."
    ),
)


# ============================================================================
# 12. HASH-BASED TWO-SUM
# ============================================================================

def two_sum_hash(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Find two indices whose values add to target.

    For each value x, look for:
        target - x

    A hash table provides average O(1) membership lookup.

    Time:
        O(n) average

    Extra space:
        O(n)
    """
    seen: dict[int, int] = {}

    for index, value in enumerate(values):
        complement = target - value

        if complement in seen:
            return seen[complement], index

        seen[value] = index

    return None


TWO_SUM_ANALYSIS = ComplexityAnalysis(
    approach="Store previously seen values in a hash table and check complements.",
    time_complexity="O(n) average-case.",
    space_complexity="O(n) auxiliary space.",
    possible_optimization=(
        "If the input is sorted, a two-pointer solution can use O(1) auxiliary "
        "space, although sorting first costs O(n log n) unless the data is already sorted."
    ),
)


# ============================================================================
# 13. TWO-POINTER TWO-SUM FOR SORTED DATA
# ============================================================================

def two_sum_sorted(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Two-pointer solution for sorted data.

    left moves right when the sum is too small.
    right moves left when the sum is too large.

    Each pointer moves at most n times.
    Therefore the scan is O(n).
    """
    left = 0
    right = len(values) - 1

    while left < right:
        current_sum = values[left] + values[right]

        if current_sum == target:
            return left, right

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


TWO_POINTER_ANALYSIS = ComplexityAnalysis(
    approach="Move two pointers inward through a sorted array.",
    time_complexity="O(n)",
    space_complexity="O(1) auxiliary space.",
    possible_optimization=(
        "The asymptotic scan is already linear. The major requirement is sorted input."
    ),
)


# ============================================================================
# 14. DUPLICATE DETECTION: TRADE-OFF
# ============================================================================

def contains_duplicate_set(values: list[int]) -> bool:
    """Use a set for average O(1) membership checks."""
    seen = set()

    for value in values:
        if value in seen:
            return True
        seen.add(value)

    return False


def contains_duplicate_sort(values: list[int]) -> bool:
    """
    Sort a copy and compare adjacent values.

    Time: O(n log n)
    Auxiliary memory depends on sorting strategy and implementation.
    """
    sorted_values = sorted(values)

    for first, second in zip(sorted_values, sorted_values[1:]):
        if first == second:
            return True

    return False


# ============================================================================
# 15. RECURSION: FACTORIAL
# ============================================================================

def factorial_recursive(n: int) -> int:
    """
    Recursive factorial.

    Recurrence:
        T(n) = T(n - 1) + O(1)

    Therefore:
        O(n) time

    Recursion depth:
        O(n)

    The iterative version can compute the same result in O(1) auxiliary space.
    """
    if n < 0:
        raise ValueError("factorial is undefined for negative integers")

    if n <= 1:
        return 1

    return n * factorial_recursive(n - 1)


def factorial_iterative(n: int) -> int:
    """Iterative factorial using constant auxiliary space."""
    if n < 0:
        raise ValueError("factorial is undefined for negative integers")

    result = 1

    for value in range(2, n + 1):
        result *= value

    return result


# ============================================================================
# 16. FIBONACCI: A CLASSIC COMPLEXITY TRAP
# ============================================================================

def fibonacci_naive(n: int) -> int:
    """
    Naive recursive Fibonacci.

    The same subproblems are repeatedly calculated.

    Its running time grows exponentially. A simple upper description is
    O(2^n), while tighter bounds can be expressed using the golden ratio.

    This implementation is educational and should not be used for large n.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n <= 1:
        return n

    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def fibonacci_memoized(n: int, memo: Optional[dict[int, int]] = None) -> int:
    """
    Memoization stores previously calculated Fibonacci values.

    Each Fibonacci value is computed once.

    Time: O(n)
    Space: O(n)
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]


def fibonacci_iterative(n: int) -> int:
    """
    Bottom-up Fibonacci.

    Time: O(n)
    Auxiliary space: O(1)
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    previous = 0
    current = 1

    for _ in range(n):
        previous, current = current, previous + current

    return previous


# ============================================================================
# 17. O(n^3) EXAMPLE
# ============================================================================

def count_equal_triples(values: list[int], target: int) -> int:
    """
    Brute-force three-sum count.

    Every combination of three indices is examined.

    The number of combinations is proportional to n^3.

    Time: O(n^3)
    Auxiliary space: O(1)
    """
    count = 0
    n = len(values)

    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if values[i] + values[j] + values[k] == target:
                    count += 1

    return count


# ============================================================================
# 18. AMORTIZED COMPLEXITY: DYNAMIC ARRAY
# ============================================================================

def demonstrate_list_growth() -> None:
    """
    Python lists behave like dynamically growing arrays.

    Appending is amortized O(1), even though an occasional resize can require
    O(n) work to move elements.

    This distinction matters:
        individual worst-case append -> O(n) during resize
        amortized append             -> O(1)
        n appends overall            -> O(n)
    """
    values: list[int] = []

    for number in range(10):
        values.append(number)

    print("\nDynamic array example:", values)
    print("append(): amortized O(1)")


# ============================================================================
# 19. SPACE COMPLEXITY: INPUT VS AUXILIARY SPACE
# ============================================================================

def copy_values(values: list[int]) -> list[int]:
    """
    This creates a second collection containing n elements.

    Auxiliary space: O(n).
    """
    return list(values)


def reverse_in_place(values: list[int]) -> None:
    """
    Reverses the existing list without creating another n-sized collection.

    Auxiliary space: O(1).
    """
    left = 0
    right = len(values) - 1

    while left < right:
        values[left], values[right] = values[right], values[left]
        left += 1
        right -= 1


# ============================================================================
# 20. CODE READING PRACTICE
# ============================================================================

def analyze_unfamiliar_code_examples() -> None:
    """
    These examples train the exact skill expected from a complexity checkpoint.
    """

    print("\n=== Unfamiliar Code Practice ===")

    print(
        """
Example A:

    for i in range(n):
        print(i)

Analysis:
    The body runs n times.
    Time = O(n)
    Extra space = O(1)
"""
    )

    print(
        """
Example B:

    for i in range(n):
        for j in range(n):
            process(i, j)

Analysis:
    The inner loop runs n times for every outer iteration.
    Time = O(n * n) = O(n^2)
"""
    )

    print(
        """
Example C:

    i = 1
    while i < n:
        i *= 2

Analysis:
    i doubles each iteration.
    Time = O(log n)
    Extra space = O(1)
"""
    )

    print(
        """
Example D:

    for i in range(n):
        for j in range(i):
            process(i, j)

Analysis:
    Total iterations are:

        0 + 1 + 2 + ... + (n - 1)
        = n(n - 1) / 2
        = O(n^2)

This is quadratic even though the inner loop does not always run n times.
"""
    )

    print(
        """
Example E:

    for value in values:
        if value not in seen:
            seen.add(value)

Analysis:
    A hash set normally provides average O(1) membership.
    The loop runs n times.
    Time = O(n) average.
    Extra space = O(n).
"""
    )

    print(
        """
Example F:

    for i in range(n):
        do_linear_work(values)

Analysis:
    If do_linear_work itself takes O(n), the total becomes:

        n * O(n) = O(n^2)
"""
    )


# ============================================================================
# 21. BEST, AVERAGE, AND WORST CASE
# ============================================================================

def linear_search_case_demo() -> None:
    """Show why an algorithm may have different cases."""
    values = [10, 20, 30, 40, 50]

    best = linear_search(values, 10)
    worst = linear_search(values, 50)
    missing = linear_search(values, 999)

    print("\nLinear search:")
    print("Best-case target index:", best)
    print("Worst-case target index:", worst)
    print("Missing target result:", missing)
    print("Best case: O(1)")
    print("Worst case: O(n)")


# ============================================================================
# 22. SORTING TRADE-OFF
# ============================================================================

def sorting_tradeoff(values: list[int]) -> None:
    """
    Sorting can be used as a preprocessing step.

    Example:
        repeated linear searches -> O(qn)
        sort once                -> O(n log n)
        repeated binary searches -> O(q log n)

    This can be valuable when q, the number of searches, is large.
    """
    sorted_values = sorted(values)

    targets = [values[0]] if values else []

    print("\nSorting trade-off demonstration:")
    print("Original:", values)
    print("Sorted:", sorted_values)

    for target in targets:
        print("Binary-search result:", binary_search(sorted_values, target))


# ============================================================================
# 23. PERFORMANCE BENCHMARKING
# ============================================================================

def benchmark(function: Callable, argument, repetitions: int = 3) -> float:
    """
    Measure elapsed wall-clock time.

    Benchmarking does NOT prove Big-O complexity. It measures one environment,
    one implementation, and one range of input sizes.

    Complexity analysis explains how growth behaves as input becomes large.
    """
    best_time = float("inf")

    for _ in range(repetitions):
        start = time.perf_counter()
        function(argument)
        elapsed = time.perf_counter() - start
        best_time = min(best_time, elapsed)

    return best_time


def run_small_benchmark() -> None:
    """Compare linear and quadratic work on modest inputs."""
    random_values = [random.randint(0, 100_000) for _ in range(800)]

    linear_time = benchmark(sum_values, random_values)
    quadratic_time = benchmark(unique_pairs, random_values)

    print("\n=== Small Benchmark ===")
    print(f"Linear operation time:   {linear_time:.6f} seconds")
    print(f"Quadratic operation time: {quadratic_time:.6f} seconds")
    print("Measured timings depend on hardware, interpreter, input, and workload.")


# ============================================================================
# 24. COMPLEXITY OF COMMON OPERATIONS
# ============================================================================

def print_common_operation_table() -> None:
    """Provide a compact reference for common Python data structures."""
    print(
        """
=== Common Operation Complexity Reference ===

Python list:
    Index access                 O(1)
    Append (amortized)           O(1)
    Insert/remove at front       O(n)
    Search                       O(n)
    Membership                   O(n)

Python set:
    Membership average           O(1)
    Insert average               O(1)
    Delete average               O(1)

Python dict:
    Lookup average               O(1)
    Insert average               O(1)
    Delete average               O(1)

Sorting:
    Python sorted()/list.sort()  O(n log n) typical comparison-based behavior

Important:
    These are asymptotic descriptions. Actual performance also depends on
    implementation details, memory locality, hashing behavior, input shape,
    allocation, interpreter overhead, and hardware.
"""
    )


# ============================================================================
# 25. COMMON COMPLEXITY MISTAKES
# ============================================================================

def print_common_mistakes() -> None:
    print(
        """
=== Common Mistakes ===

1. Calling two sequential O(n) loops O(n^2).
   Correct: O(n + n) = O(n).

2. Assuming every nested loop is O(n^2).
   Check how the bounds change.

3. Ignoring data-structure operations.
   A loop containing an O(n) operation may become O(n^2).

4. Calling recursion O(1) space without checking call depth.

5. Forgetting memory used by sets, dictionaries, lists, queues, and maps.

6. Assuming a hash table is mathematically guaranteed O(1) in every situation.
   Average-case behavior is the usual practical classification.

7. Confusing input size with the numeric value of the input.
   An integer n and a list containing n items are different contexts.

8. Treating benchmarking as a substitute for complexity analysis.

9. Ignoring preprocessing.
   Sorting O(n) data before searching is part of the total algorithm cost.

10. Optimizing constants before addressing a poor asymptotic algorithm.
"""
    )


# ============================================================================
# 26. PRACTICE PROBLEMS
# ============================================================================

def complexity_quiz() -> None:
    """
    Answers are deliberately calculated in the code rather than hidden behind
    a static worksheet.
    """
    questions = [
        (
            "One loop from 0 to n",
            "O(n)",
        ),
        (
            "Two nested loops each running n times",
            "O(n^2)",
        ),
        (
            "Repeatedly divide n by 2",
            "O(log n)",
        ),
        (
            "Merge sort",
            "O(n log n)",
        ),
        (
            "Three independent nested loops over n",
            "O(n^3)",
        ),
        (
            "Hash-table two-sum average case",
            "O(n)",
        ),
    ]

    print("\n=== Complexity Quiz ===")
    for question, answer in questions:
        print(f"{question:55} -> {answer}")


# ============================================================================
# 27. FULL ANALYSIS OF PREVIOUSLY SOLVED-STYLE PROBLEMS
# ============================================================================

def previous_problem_analysis() -> None:
    """
    The requested Day 11 format:

        Approach
        Time Complexity
        Space Complexity
        Possible Optimization

    The important habit is to write this analysis after solving a problem,
    rather than treating complexity as an unrelated theory topic.
    """

    analyses = [
        ("Find maximum", ComplexityAnalysis(
            "Scan the array and maintain the largest value seen.",
            "O(n)",
            "O(1) auxiliary space.",
            "No asymptotic improvement is possible when every value may need inspection."
        )),
        ("Reverse array", ComplexityAnalysis(
            "Use two pointers and swap elements from both ends.",
            "O(n)",
            "O(1) auxiliary space.",
            "Two-pointer in-place reversal already provides linear time and constant extra space."
        )),
        ("Binary search", BINARY_SEARCH_ANALYSIS),
        ("Merge sort", MERGE_SORT_ANALYSIS),
        ("Two-sum with hash table", TWO_SUM_ANALYSIS),
        ("Two-sum with sorted data", TWO_POINTER_ANALYSIS),
        ("Recursive factorial", ComplexityAnalysis(
            "Reduce n by one until the base case.",
            "O(n)",
            "O(n) recursion stack.",
            "Use the iterative version for O(1) auxiliary space."
        )),
        ("Fibonacci naive recursion", ComplexityAnalysis(
            "Recursively calculate both previous Fibonacci values.",
            "Exponential, commonly bounded as O(2^n).",
            "O(n) recursion depth.",
            "Use memoization for O(n) time or iterative dynamic programming for O(n) time and O(1) auxiliary space."
        )),
    ]

    for title, analysis in analyses:
        analysis.display(title)


# ============================================================================
# 28. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print("\n=== Edge Cases ===")

    empty: list[int] = []
    single = [42]
    duplicates = [5, 5, 5]
    already_sorted = [1, 2, 3, 4, 5]
    reverse_sorted = [5, 4, 3, 2, 1]

    print("Empty linear search:", linear_search(empty, 1))
    print("Single-element search:", linear_search(single, 42))
    print("Duplicate detection:", contains_duplicate_set(duplicates))
    print("Already sorted merge sort:", merge_sort(already_sorted))
    print("Reverse sorted merge sort:", merge_sort(reverse_sorted))

    for invalid in [-1, 0]:
        try:
            count_halvings(invalid)
        except ValueError as error:
            print(f"Invalid logarithmic input {invalid}: {error}")


# ============================================================================
# 29. INDEPENDENT INPUT SIZES
# ============================================================================

def independent_input_example(first: list[int], second: list[int]) -> int:
    """
    Important complexity lesson:

    If the algorithm has two independent inputs with sizes n and m:

        for x in first:
            for y in second:
                ...

    the complexity is O(nm), not automatically O(n^2).
    """
    count = 0

    for _ in first:
        for _ in second:
            count += 1

    return count


# ============================================================================
# 30. COMPLEXITY CHECKLIST
# ============================================================================

def complexity_checklist() -> None:
    print(
        """
=== Complexity Analysis Checklist ===

When seeing unfamiliar code:

1. Identify the input size variables.
2. Find loops.
3. Determine how many times each loop executes.
4. Check whether loops are sequential or nested.
5. Check whether a loop variable doubles, halves, or changes another way.
6. Inspect function calls inside loops.
7. Analyze the cost of those called functions.
8. Inspect sorting and searching operations.
9. Inspect data-structure operations.
10. Check recursion:
       - number of recursive calls
       - work per call
       - recursion depth
11. Identify newly allocated collections.
12. Separate input storage from auxiliary memory.
13. Determine best, average, and worst cases when relevant.
14. Keep the dominant term.
15. Remove constant factors.
16. State assumptions when using average-case complexity.
17. Consider preprocessing cost.
18. Consider output size.
19. Consider practical trade-offs.
20. Verify the reasoning with small tests or benchmarks when useful.
"""
    )


# ============================================================================
# 31. MAIN STUDY RUN
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("DAY 11 — COMPLEXITY PRACTICE")
    print("=" * 78)

    explain_complexity_basics()

    CONSTANT_TIME_ANALYSIS.display("Constant-Time Access")
    LINEAR_SEARCH_ANALYSIS.display("Linear Search")
    BINARY_SEARCH_ANALYSIS.display("Binary Search")
    ONE_LOOP_ANALYSIS.display("Single Linear Loop")
    SEQUENTIAL_LOOPS_ANALYSIS.display("Sequential Linear Loops")
    ALL_PAIRS_ANALYSIS.display("Nested Loops")
    UNIQUE_PAIRS_ANALYSIS.display("Triangular Nested Loops")
    LOGARITHMIC_ANALYSIS.display("Repeated Halving")
    MERGE_SORT_ANALYSIS.display("Merge Sort")
    TWO_SUM_ANALYSIS.display("Hash-Based Two Sum")
    TWO_POINTER_ANALYSIS.display("Two-Pointer Two Sum")

    sample = [7, 2, 9, 4, 1, 8]

    print("\n=== Executable Examples ===")
    print("Sample:", sample)
    print("Maximum:", max(sample))
    print("Sum:", sum_values(sample))
    print("Search 4:", linear_search(sample, 4))
    print("Sorted:", merge_sort(sample))
    print("Two sum target 10:", two_sum_hash(sample, 10))
    print("Unique pairs:", unique_pairs([1, 2, 3]))

    print("\n=== Fibonacci Comparison ===")
    n = 20
    print("Naive recursive:", fibonacci_naive(n))
    print("Memoized:", fibonacci_memoized(n))
    print("Iterative:", fibonacci_iterative(n))

    print("\n=== Factorial Comparison ===")
    print("Recursive 6!:", factorial_recursive(6))
    print("Iterative 6!:", factorial_iterative(6))

    demonstrate_list_growth()

    values = [5, 1, 4, 2, 8]
    copied = copy_values(values)
    reverse_in_place(copied)
    print("\nOriginal:", values)
    print("Reversed copy:", copied)

    analyze_unfamiliar_code_examples()
    linear_search_case_demo()
    sorting_tradeoff(values)
    print_common_operation_table()
    print_common_mistakes()
    complexity_quiz()
    previous_problem_analysis()
    demonstrate_edge_cases()
    complexity_checklist()

    print("\n=== Final Checkpoint ===")
    print("Can you identify the dominant operation in unfamiliar code?")
    print("Can you distinguish O(n), O(n log n), O(n^2), and O(log n)?")
    print("Can you identify extra memory and recursion depth?")
    print("Can you explain a possible optimization without changing correctness?")
    print("\nDay 11 practice completed.")


if __name__ == "__main__":
    main()
