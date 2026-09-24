"""
Day 8 — Space Complexity
DSA Preparation: Input Space, Auxiliary Space, Variables, Arrays,
Recursion Stack, In-Place Algorithms, and Practical Space Analysis.

This file is a standalone study program. It progresses from the basic
meaning of space complexity to iterative, recursive, array-based,
string-based, and map/set-based solutions.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import sys


# ============================================================================
# 1. FUNDAMENTAL IDEA: WHAT IS SPACE COMPLEXITY?
# ============================================================================

def explain_space_complexity() -> None:
    print("\n" + "=" * 78)
    print("1. FUNDAMENTAL IDEA: SPACE COMPLEXITY")
    print("=" * 78)

    print(
        """
Space complexity describes how much memory an algorithm needs as the input
size grows.

A useful decomposition is:

    Total space = input space + auxiliary space

Input space is the memory occupied by the input itself.

Auxiliary space is the additional memory required by the algorithm while
processing that input.

Example:

    def total(numbers):
        return sum(numbers)

The list 'numbers' already exists before the function starts. The algorithm
does not create another list proportional to n. Apart from a few scalar
variables and implementation details, its additional working memory is O(1).

By contrast:

    def doubled(numbers):
        result = [2 * value for value in numbers]
        return result

The returned result contains n elements, so the newly created data structure
requires O(n) additional memory.

Space complexity is about growth, not the exact number of bytes used by one
machine at one moment.

Common growth classes are:

    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) near-linear
    O(n^2)     quadratic
    O(2^n)     exponential

The same input can be processed by two algorithms with the same time
complexity but different space requirements.
"""
    )


# ============================================================================
# 2. INPUT SPACE VS AUXILIARY SPACE
# ============================================================================

def input_space_and_auxiliary_space(numbers: List[int]) -> None:
    print("\n" + "=" * 78)
    print("2. INPUT SPACE VS AUXILIARY SPACE")
    print("=" * 78)

    print(f"Input contains {len(numbers)} integers.")
    print("The input list itself occupies space proportional to n.")
    print("That input storage is normally classified as input space.")

    total = sum(numbers)
    print(f"Sum using constant auxiliary space: {total}")

    copied = list(numbers)
    print(f"Created a second list containing {len(copied)} integers.")
    print("The copied list is auxiliary space of O(n).")

    print(
        """
Important distinction:

    Input space:
        Space required to represent the supplied input.

    Auxiliary space:
        Extra working memory created by the algorithm.

    Total space:
        Input storage + auxiliary storage + relevant execution overhead.

For algorithm comparisons, auxiliary space is often emphasized because the
input exists regardless of which algorithm processes it.
"""
    )


# ============================================================================
# 3. VARIABLES AND CONSTANT SPACE
# ============================================================================

def constant_space_example(numbers: List[int]) -> int:
    """
    Uses a fixed number of scalar variables.

    The number of variables does not increase when n increases.
    Therefore auxiliary space is O(1).
    """
    total = 0
    maximum = None

    for value in numbers:
        total += value

        if maximum is None or value > maximum:
            maximum = value

    if maximum is None:
        return 0

    return total + maximum


def many_values_are_still_constant_if_count_is_fixed() -> Tuple[int, int, int]:
    """
    A fixed number of variables is O(1), regardless of their names or values.
    """
    first = 10
    second = 20
    third = 30
    return first, second, third


def demonstrate_constant_space() -> None:
    print("\n" + "=" * 78)
    print("3. VARIABLES AND CONSTANT SPACE")
    print("=" * 78)

    numbers = [4, 8, 1, 9, 3]
    result = constant_space_example(numbers)
    print(f"Result: {result}")

    fixed_values = many_values_are_still_constant_if_count_is_fixed()
    print(f"Fixed variables: {fixed_values}")

    print(
        """
The number of scalar variables is constant:

    total
    maximum
    value

The loop processes n elements, but it does not create n persistent variables.

Therefore:

    Auxiliary space = O(1)

A common mistake is to see a loop and conclude O(n) space. A loop by itself
does not determine space complexity. The important question is whether the
algorithm creates or retains an amount of memory that grows with n.
"""
    )


# ============================================================================
# 4. ARRAY SPACE
# ============================================================================

def create_array_of_same_size(numbers: List[int]) -> List[int]:
    """
    Creates a new list with one output element per input element.

    Auxiliary space: O(n).
    """
    result = [0] * len(numbers)

    for index, value in enumerate(numbers):
        result[index] = value * value

    return result


def create_constant_size_array(numbers: List[int]) -> int:
    """
    Uses a fixed-size accumulator instead of an n-sized array.

    Auxiliary space: O(1).
    """
    even_count = 0
    odd_count = 0

    for value in numbers:
        if value % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    return even_count + odd_count


def demonstrate_array_space() -> None:
    print("\n" + "=" * 78)
    print("4. ARRAYS AND LISTS")
    print("=" * 78)

    numbers = [1, 2, 3, 4, 5]

    transformed = create_array_of_same_size(numbers)
    print(f"Original:    {numbers}")
    print(f"New array:   {transformed}")
    print("New array size grows with n -> O(n) auxiliary space.")

    count = create_constant_size_array(numbers)
    print(f"Elements processed: {count}")
    print("Only two counters are retained -> O(1) auxiliary space.")

    print(
        """
Examples:

    result = [0] * n
        O(n) extra space

    result = []
    for value in numbers:
        result.append(value)
        O(n) extra space

    left = 0
    right = n - 1
        O(1) extra space

An array is not automatically O(n) auxiliary space. It depends on whether
the array is input storage, output storage, or newly allocated working
storage.
"""
    )


# ============================================================================
# 5. IN-PLACE ALGORITHMS
# ============================================================================

def reverse_in_place(numbers: List[int]) -> None:
    """
    Reverses the list without allocating another list of size n.

    Auxiliary space: O(1).
    """
    left = 0
    right = len(numbers) - 1

    while left < right:
        numbers[left], numbers[right] = numbers[right], numbers[left]
        left += 1
        right -= 1


def reverse_using_extra_array(numbers: List[int]) -> List[int]:
    """
    Creates a second array.

    Auxiliary space: O(n).
    """
    return numbers[::-1]


def demonstrate_in_place_algorithms() -> None:
    print("\n" + "=" * 78)
    print("5. IN-PLACE ALGORITHMS")
    print("=" * 78)

    values = [10, 20, 30, 40, 50]
    reverse_in_place(values)

    print(f"In-place result: {values}")
    print("The original list was modified and no n-sized working list was made.")

    original = [10, 20, 30, 40, 50]
    copied_result = reverse_using_extra_array(original)

    print(f"Original remains: {original}")
    print(f"New reversed list: {copied_result}")

    print(
        """
An in-place algorithm generally uses O(1) or otherwise very small auxiliary
memory while modifying the existing data structure.

Important nuance:

    In-place does not always mean exactly O(1) space.

Some definitions allow a small amount of additional memory, while strict
definitions require constant auxiliary storage.

Python's slicing operation:

    numbers[::-1]

creates a new list, so it is not an O(1)-auxiliary-space reversal.
"""
    )


# ============================================================================
# 6. ITERATIVE VS RECURSIVE SPACE
# ============================================================================

def factorial_iterative(n: int) -> int:
    """Iterative factorial: O(1) auxiliary space."""
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    result = 1

    for value in range(2, n + 1):
        result *= value

    return result


def factorial_recursive(n: int) -> int:
    """
    Recursive factorial.

    Each active recursive call remains on the call stack.
    Auxiliary space: O(n).
    """
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    if n <= 1:
        return 1

    return n * factorial_recursive(n - 1)


def demonstrate_iterative_vs_recursive() -> None:
    print("\n" + "=" * 78)
    print("6. ITERATIVE VS RECURSIVE SOLUTIONS")
    print("=" * 78)

    n = 6

    iterative_result = factorial_iterative(n)
    recursive_result = factorial_recursive(n)

    print(f"Iterative factorial({n}): {iterative_result}")
    print(f"Recursive factorial({n}): {recursive_result}")

    print(
        """
Time:

    Both factorial implementations perform O(n) arithmetic operations.

Auxiliary space:

    Iterative factorial:
        O(1)

    Recursive factorial:
        O(n)

Why?

The recursive version creates a chain:

    factorial(6)
        factorial(5)
            factorial(4)
                factorial(3)
                    factorial(2)
                        factorial(1)

At the deepest point, approximately n stack frames are active.

The recursion stack is real memory. It must be included when analyzing
space complexity.
"""
    )


# ============================================================================
# 7. RECURSION STACK VISUALIZATION
# ============================================================================

def recursive_sum(numbers: List[int], index: int = 0) -> int:
    """
    Recursively sums an array.

    Auxiliary space:
        O(n) because at most n recursive calls can be active.
    """
    if index == len(numbers):
        return 0

    return numbers[index] + recursive_sum(numbers, index + 1)


def iterative_sum(numbers: List[int]) -> int:
    """
    Iterative equivalent.

    Auxiliary space: O(1).
    """
    total = 0

    for value in numbers:
        total += value

    return total


def demonstrate_recursion_stack() -> None:
    print("\n" + "=" * 78)
    print("7. RECURSION STACK")
    print("=" * 78)

    numbers = [5, 10, 15, 20]

    recursive_result = recursive_sum(numbers)
    iterative_result = iterative_sum(numbers)

    print(f"Recursive sum: {recursive_result}")
    print(f"Iterative sum: {iterative_result}")

    print(
        """
For:

    recursive_sum([5, 10, 15, 20])

The active calls conceptually grow as:

    recursive_sum(index=0)
    recursive_sum(index=1)
    recursive_sum(index=2)
    recursive_sum(index=3)
    recursive_sum(index=4)

After the base case returns, frames are removed.

The maximum number of simultaneously active frames determines stack-space
growth.

A recursive algorithm can therefore use substantial memory even when it does
not explicitly create an array, map, or set.
"""
    )


# ============================================================================
# 8. STRING-BASED SPACE
# ============================================================================

def reverse_string_with_extra_space(text: str) -> str:
    """
    Creates a new string.

    Auxiliary space: O(n) under the usual algorithmic model.
    """
    return text[::-1]


def reverse_string_using_characters(text: str) -> str:
    """
    Builds a new list of characters and joins it.

    Auxiliary space: O(n).
    """
    characters = []

    for character in text:
        characters.append(character)

    characters.reverse()
    return "".join(characters)


def remove_spaces(text: str) -> str:
    """
    Creates a new output string.

    Auxiliary space: O(n).
    """
    return "".join(character for character in text if not character.isspace())


def demonstrate_string_space() -> None:
    print("\n" + "=" * 78)
    print("8. STRING-BASED SOLUTIONS")
    print("=" * 78)

    text = "space complexity"

    print(f"Original: {text}")
    print(f"Reversed: {reverse_string_with_extra_space(text)}")
    print(f"No spaces: {remove_spaces(text)}")

    print(
        """
Strings require special attention because many languages treat strings as
immutable values.

In Python, an operation that appears simple can allocate another string.

For example:

    reversed_text = text[::-1]

The resulting string has O(n) size.

This is different from an in-place reversal of a mutable array.

When analyzing strings, ask:

    1. Is the string immutable?
    2. Does the operation create a new string?
    3. Are temporary strings created repeatedly?
    4. Are characters copied?
    5. Is a list of characters created?
"""
    )


# ============================================================================
# 9. EXTRA MAP / SET SPACE
# ============================================================================

def contains_duplicate_using_set(numbers: List[int]) -> bool:
    """
    Stores previously observed values.

    Auxiliary space: O(n) in the worst case.
    """
    seen: Set[int] = set()

    for value in numbers:
        if value in seen:
            return True

        seen.add(value)

    return False


def contains_duplicate_bruteforce(numbers: List[int]) -> bool:
    """
    No additional set or map.

    Auxiliary space: O(1).
    Time: O(n^2) in the worst case.
    """
    for first_index in range(len(numbers)):
        for second_index in range(first_index + 1, len(numbers)):
            if numbers[first_index] == numbers[second_index]:
                return True

    return False


def demonstrate_set_tradeoff() -> None:
    print("\n" + "=" * 78)
    print("9. EXTRA SET SPACE AND TIME/SPACE TRADE-OFFS")
    print("=" * 78)

    numbers = [3, 8, 1, 7, 3]

    print(f"Using set:        {contains_duplicate_using_set(numbers)}")
    print(f"Without extra set:{contains_duplicate_bruteforce(numbers)}")

    print(
        """
The set-based solution usually gives:

    Time:  O(n) average-case
    Space: O(n)

The brute-force solution gives:

    Time:  O(n^2)
    Space: O(1)

This is an important algorithm-design trade-off:

    More memory can sometimes reduce running time.

The correct choice depends on constraints. If memory is severely limited,
the O(1)-space solution may be appropriate. If speed matters and memory is
available, the set-based solution may be preferable.
"""
    )


# ============================================================================
# 10. MAP-BASED FREQUENCY COUNT
# ============================================================================

def frequency_count(numbers: List[int]) -> Dict[int, int]:
    """
    Stores one frequency entry per distinct value.

    Auxiliary space: O(k), where k is the number of distinct values.

    Since k <= n, the worst case is O(n).
    """
    frequencies: Dict[int, int] = {}

    for value in numbers:
        frequencies[value] = frequencies.get(value, 0) + 1

    return frequencies


def demonstrate_map_space() -> None:
    print("\n" + "=" * 78)
    print("10. MAP SPACE: O(k) VERSUS O(n)")
    print("=" * 78)

    numbers = [4, 4, 4, 2, 2, 9]

    frequencies = frequency_count(numbers)

    print(f"Input: {numbers}")
    print(f"Frequencies: {frequencies}")

    print(
        """
A useful refinement is to describe space as O(k), where k is the number of
distinct values.

For:

    [5, 5, 5, 5, 5]

k = 1, even though n = 5.

For:

    [1, 2, 3, 4, 5]

k = 5 = n.

Therefore:

    Space = O(k)
    and because k <= n:
    Worst case = O(n)

Parameterized complexity often gives a more informative analysis than simply
writing O(n).
"""
    )


# ============================================================================
# 11. SORTING AND SPACE
# ============================================================================

def selection_sort_in_place(numbers: List[int]) -> None:
    """
    Selection sort performed directly on the input list.

    Auxiliary space: O(1).
    Time: O(n^2).
    """
    n = len(numbers)

    for current in range(n):
        minimum_index = current

        for candidate in range(current + 1, n):
            if numbers[candidate] < numbers[minimum_index]:
                minimum_index = candidate

        numbers[current], numbers[minimum_index] = (
            numbers[minimum_index],
            numbers[current],
        )


def demonstrate_in_place_sorting() -> None:
    print("\n" + "=" * 78)
    print("11. IN-PLACE SORTING")
    print("=" * 78)

    numbers = [7, 3, 9, 1, 5]
    selection_sort_in_place(numbers)

    print(f"Sorted in place: {numbers}")

    print(
        """
Selection sort is a useful educational example because its auxiliary space
is O(1), even though its time complexity is O(n^2).

This illustrates that:

    Time complexity and space complexity measure different resources.

An algorithm can be:

    fast but memory-heavy,
    slow but memory-efficient,
    fast and memory-efficient,
    or slow and memory-heavy.

The classification must be determined independently.
"""
    )


# ============================================================================
# 12. MATRIX SPACE
# ============================================================================

def create_matrix(rows: int, columns: int) -> List[List[int]]:
    """
    Creates a rows x columns matrix.

    Space: O(rows * columns).
    """
    return [[0 for _ in range(columns)] for _ in range(rows)]


def demonstrate_matrix_space() -> None:
    print("\n" + "=" * 78)
    print("12. MULTIDIMENSIONAL SPACE")
    print("=" * 78)

    rows = 3
    columns = 4
    matrix = create_matrix(rows, columns)

    print(f"Created a {rows} x {columns} matrix:")
    for row in matrix:
        print(row)

    print(
        """
If a matrix contains r rows and c columns:

    Space = O(r * c)

If r = c = n:

    Space = O(n^2)

Nested loops do not automatically imply O(n^2) space. They imply O(n^2)
space only if the algorithm stores O(n^2) data.

A nested loop that only uses two counters may still use O(1) auxiliary space.
"""
    )


# ============================================================================
# 13. EDGE CASES
# ============================================================================

def safe_maximum(numbers: List[int]) -> Optional[int]:
    """Returns None for an empty list instead of accessing an invalid index."""
    if not numbers:
        return None

    maximum = numbers[0]

    for value in numbers[1:]:
        if value > maximum:
            maximum = value

    return maximum


def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("13. EDGE CASES")
    print("=" * 78)

    cases = [
        [],
        [1],
        [5, 5, 5],
        [-10, -3, -20],
    ]

    for case in cases:
        print(f"{case!r} -> maximum = {safe_maximum(case)}")

    print(
        """
Space analysis should also consider unusual inputs:

    n = 0
    n = 1
    repeated values
    all unique values
    negative values
    very large n
    unusually long strings
    deeply recursive inputs

A set-based algorithm may use little memory for highly repetitive input but
can reach O(n) memory when every value is unique.

A recursive algorithm may work for small inputs but fail for sufficiently
large inputs because of the language's recursion-depth or stack limitations.
"""
    )


# ============================================================================
# 14. RECURSION DEPTH AND PYTHON LIMITS
# ============================================================================

def recursion_depth_demo(depth: int) -> int:
    """
    Educational recursion-depth example.

    The function itself is intentionally simple. Each active invocation
    consumes stack space, so auxiliary space is O(depth).
    """
    if depth <= 0:
        return 0

    return 1 + recursion_depth_demo(depth - 1)


def demonstrate_recursion_limit() -> None:
    print("\n" + "=" * 78)
    print("14. RECURSION LIMITS")
    print("=" * 78)

    print(f"Python recursion limit reported by sys: {sys.getrecursionlimit()}")

    depth = 10
    print(f"Safe demonstration depth: {depth}")
    print(f"Result: {recursion_depth_demo(depth)}")

    print(
        """
A theoretical O(n)-space recursive algorithm can encounter a practical
failure before n becomes extremely large.

Python deliberately limits recursion depth to reduce the risk of uncontrolled
stack growth.

Changing the recursion limit is not automatically a solution. The underlying
algorithm still consumes stack memory.

For algorithms that require deep recursion, an iterative approach or an
explicit stack data structure may be more appropriate.
"""
    )


# ============================================================================
# 15. EXPLICIT STACK VS RECURSION
# ============================================================================

def iterative_depth_processing(values: List[int]) -> int:
    """
    Uses an explicit stack.

    Worst-case auxiliary space: O(n).
    """
    stack = list(values)
    count = 0

    while stack:
        stack.pop()
        count += 1

    return count


def demonstrate_explicit_stack() -> None:
    print("\n" + "=" * 78)
    print("15. EXPLICIT STACK")
    print("=" * 78)

    values = [10, 20, 30, 40]
    print(f"Processed: {iterative_depth_processing(values)} elements")

    print(
        """
Replacing recursion with an explicit stack does not necessarily reduce
asymptotic space.

Recursive:

    call stack -> O(n)

Explicit:

    stack data structure -> O(n)

The advantage is control. An explicit stack can avoid language recursion
limits and can make memory management more visible.
"""
    )


# ============================================================================
# 16. TWO-POINTER TECHNIQUE
# ============================================================================

def is_palindrome_in_place_style(text: str) -> bool:
    """
    Uses two indexes and does not create a reversed copy.

    Auxiliary space: O(1) under a character-indexing model.

    Python strings are immutable, but reading characters by index does not
    require constructing another string.
    """
    left = 0
    right = len(text) - 1

    while left < right:
        if text[left] != text[right]:
            return False

        left += 1
        right -= 1

    return True


def demonstrate_two_pointers() -> None:
    print("\n" + "=" * 78)
    print("16. TWO-POINTER SPACE OPTIMIZATION")
    print("=" * 78)

    samples = ["level", "algorithm", "racecar", ""]

    for sample in samples:
        print(f"{sample!r} -> {is_palindrome_in_place_style(sample)}")

    print(
        """
Two pointers are a common way to avoid additional arrays.

Instead of:

    create reversed copy
    compare original and reversed

we use:

    left = 0
    right = n - 1

and compare pairs directly.

The auxiliary variables remain constant in number, so auxiliary space is O(1).
"""
    )


# ============================================================================
# 17. SLIDING WINDOW SPACE
# ============================================================================

def maximum_sum_fixed_window(numbers: List[int], window_size: int) -> Optional[int]:
    """
    Sliding-window calculation.

    Auxiliary space: O(1), excluding the input list.
    """
    if window_size <= 0 or window_size > len(numbers):
        return None

    current_sum = sum(numbers[:window_size])
    maximum_sum = current_sum

    for index in range(window_size, len(numbers)):
        current_sum += numbers[index]
        current_sum -= numbers[index - window_size]
        maximum_sum = max(maximum_sum, current_sum)

    return maximum_sum


def demonstrate_sliding_window() -> None:
    print("\n" + "=" * 78)
    print("17. SLIDING WINDOW")
    print("=" * 78)

    numbers = [2, 1, 5, 1, 3, 2]
    window_size = 3

    result = maximum_sum_fixed_window(numbers, window_size)

    print(f"Input: {numbers}")
    print(f"Window size: {window_size}")
    print(f"Maximum window sum: {result}")

    print(
        """
A naive implementation could create every window separately.

A sliding-window implementation reuses information from the previous window.

The algorithm retains:

    current_sum
    maximum_sum
    indexes

A fixed number of variables means O(1) auxiliary space.
"""
    )


# ============================================================================
# 18. SPACE COMPLEXITY OF COMMON PATTERNS
# ============================================================================

@dataclass
class SpacePattern:
    name: str
    auxiliary_space: str
    reason: str


def common_space_patterns() -> List[SpacePattern]:
    return [
        SpacePattern(
            "Single accumulator",
            "O(1)",
            "Only a fixed number of scalar variables are retained.",
        ),
        SpacePattern(
            "Copy of input array",
            "O(n)",
            "A second structure stores n elements.",
        ),
        SpacePattern(
            "Frequency map",
            "O(k), worst O(n)",
            "One entry is retained per distinct value.",
        ),
        SpacePattern(
            "Recursive linear call chain",
            "O(n)",
            "n stack frames can be active.",
        ),
        SpacePattern(
            "Two pointers",
            "O(1)",
            "Only a fixed number of indexes and temporary values are used.",
        ),
        SpacePattern(
            "r x c matrix",
            "O(r*c)",
            "The matrix stores one value per cell.",
        ),
    ]


def demonstrate_common_patterns() -> None:
    print("\n" + "=" * 78)
    print("18. COMMON SPACE PATTERNS")
    print("=" * 78)

    for pattern in common_space_patterns():
        print(f"{pattern.name:28} {pattern.auxiliary_space:18} {pattern.reason}")


# ============================================================================
# 19. AMORTIZED / TEMPORARY MEMORY CONSIDERATIONS
# ============================================================================

def build_output_incrementally(numbers: List[int]) -> List[int]:
    """
    Output-building example.

    The returned list itself requires O(n) memory.

    Whether that memory is classified as auxiliary depends on the problem's
    definition of output space. It is important to distinguish output space
    from temporary working memory.
    """
    output = []

    for value in numbers:
        output.append(value * 2)

    return output


def demonstrate_output_space() -> None:
    print("\n" + "=" * 78)
    print("19. OUTPUT SPACE VS AUXILIARY SPACE")
    print("=" * 78)

    numbers = [1, 2, 3]
    output = build_output_incrementally(numbers)

    print(f"Input:  {numbers}")
    print(f"Output: {output}")

    print(
        """
Suppose a problem explicitly asks an algorithm to return n transformed
elements.

The output itself necessarily occupies O(n) space.

Many algorithm analyses report:

    auxiliary space = extra working memory excluding required output

This distinction matters.

An algorithm returning an n-element array may have:

    Output space: O(n)
    Auxiliary space: O(1)

That can be very different from:

    Output space: O(n)
    Auxiliary space: O(n)

where a second n-sized working structure is also created.
"""
    )


# ============================================================================
# 20. SPACE COMPARISON TABLE
# ============================================================================

def print_space_comparison() -> None:
    print("\n" + "=" * 78)
    print("20. SPACE COMPARISON")
    print("=" * 78)

    rows = [
        ("Sum with loop", "O(1)", "Scalars only"),
        ("Copy an array", "O(n)", "New array"),
        ("Reverse in place", "O(1)", "Two indexes + swap"),
        ("Recursive sum", "O(n)", "Call stack"),
        ("Duplicate detection with set", "O(n)", "Set of values"),
        ("Duplicate detection by nested loops", "O(1)", "No extra structure"),
        ("Frequency map", "O(k)", "Distinct values"),
        ("Matrix r x c", "O(r*c)", "Stored cells"),
    ]

    print(f"{'Algorithm':40} {'Auxiliary space':18} Reason")
    print("-" * 78)

    for name, complexity, reason in rows:
        print(f"{name:40} {complexity:18} {reason}")


# ============================================================================
# 21. PRACTICAL SPACE ANALYSIS PROCEDURE
# ============================================================================

def analyze_space_step_by_step() -> None:
    print("\n" + "=" * 78)
    print("21. A PRACTICAL SPACE-ANALYSIS PROCEDURE")
    print("=" * 78)

    print(
        """
For a new algorithm, use this sequence:

1. Identify the input.
   Ask what data already exists before the algorithm starts.

2. Count additional variables.
   A fixed number of scalar variables usually contributes O(1).

3. Look for growing collections.
   Arrays, lists, maps, sets, queues, stacks, and matrices may grow with n.

4. Inspect recursion.
   Count the maximum number of simultaneously active calls.

5. Inspect temporary objects.
   Slices, copies, strings, comprehensions, and helper structures can allocate
   memory even when they look syntactically small.

6. Determine whether the output is counted separately.
   Some problems exclude required output memory from auxiliary space.

7. Express the dominant growth rate.
   Ignore constant factors and lower-order terms.

8. Check the worst case.
   A set may contain k values, where k can become n.

9. Consider implementation behavior.
   Language runtimes may have object overhead, allocation strategies, and
   garbage collection that affect actual memory consumption.

10. Compare alternatives.
    A faster algorithm may use more memory, while a memory-efficient algorithm
    may require more time.
"""
    )


# ============================================================================
# 22. ADVANCED EXAMPLE: TWO DUPLICATE-DETECTION STRATEGIES
# ============================================================================

def duplicate_strategy_report(numbers: List[int]) -> Dict[str, object]:
    """
    Compares two algorithms.

    This function itself uses a fixed-size dictionary containing results, not
    data proportional to the input, so its own auxiliary contribution is O(1)
    relative to n. The called set-based algorithm uses O(n).
    """
    return {
        "set_based": contains_duplicate_using_set(numbers),
        "brute_force": contains_duplicate_bruteforce(numbers),
    }


def demonstrate_tradeoff_case() -> None:
    print("\n" + "=" * 78)
    print("22. ADVANCED TIME/SPACE TRADE-OFF")
    print("=" * 78)

    numbers = list(range(1000))
    numbers.append(500)

    report = duplicate_strategy_report(numbers)

    print(f"Set-based duplicate result: {report['set_based']}")
    print(f"Brute-force duplicate result: {report['brute_force']}")

    print(
        """
For a large input, the difference in time can become substantial.

The set-based approach spends memory to avoid repeatedly comparing elements.

This is one of the most important practical patterns in algorithm design:

    Time-space trade-off

Common examples include:

    Hash maps for faster lookup
    Memoization for faster repeated computation
    Caches for reducing recomputation
    Prefix arrays for faster range queries
    Precomputed tables for repeated calculations

Each technique exchanges additional memory for another benefit.
"""
    )


# ============================================================================
# 23. ADVANCED EXAMPLE: MEMOIZATION
# ============================================================================

def fibonacci_without_memoization(n: int) -> int:
    """
    Exponential-time recursive Fibonacci.

    Auxiliary space from recursion depth: O(n).
    """
    if n <= 1:
        return n

    return (
        fibonacci_without_memoization(n - 1)
        + fibonacci_without_memoization(n - 2)
    )


def fibonacci_with_memoization(
    n: int,
    memo: Optional[Dict[int, int]] = None,
) -> int:
    """
    Memoized Fibonacci.

    Time: O(n)
    Auxiliary space: O(n)

    The dictionary stores computed results.
    """
    if n <= 1:
        return n

    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]

    memo[n] = (
        fibonacci_with_memoization(n - 1, memo)
        + fibonacci_with_memoization(n - 2, memo)
    )

    return memo[n]


def demonstrate_memoization() -> None:
    print("\n" + "=" * 78)
    print("23. MEMOIZATION AS A SPACE-TIME TRADE-OFF")
    print("=" * 78)

    n = 20

    plain = fibonacci_without_memoization(n)
    memoized = fibonacci_with_memoization(n)

    print(f"Plain recursive Fibonacci({n}): {plain}")
    print(f"Memoized Fibonacci({n}):        {memoized}")

    print(
        """
Memoization stores previously computed results.

Without memoization:

    Time: approximately exponential
    Extra stored results: none
    Recursion stack: O(n)

With memoization:

    Time: O(n)
    Memo dictionary: O(n)
    Recursion stack: O(n)

Memory is deliberately used to reduce repeated computation.

This pattern is fundamental to dynamic programming.
"""
    )


# ============================================================================
# 24. ADVANCED EXAMPLE: ITERATIVE DYNAMIC PROGRAMMING
# ============================================================================

def fibonacci_dp_array(n: int) -> int:
    """
    Dynamic programming with an array.

    Time: O(n)
    Auxiliary space: O(n).
    """
    if n <= 1:
        return n

    values = [0] * (n + 1)
    values[1] = 1

    for index in range(2, n + 1):
        values[index] = values[index - 1] + values[index - 2]

    return values[n]


def fibonacci_dp_optimized(n: int) -> int:
    """
    Space-optimized dynamic programming.

    Only the previous two values are needed.

    Time: O(n)
    Auxiliary space: O(1).
    """
    if n <= 1:
        return n

    previous_two = 0
    previous_one = 1

    for _ in range(2, n + 1):
        current = previous_two + previous_one
        previous_two = previous_one
        previous_one = current

    return previous_one


def demonstrate_space_optimized_dp() -> None:
    print("\n" + "=" * 78)
    print("24. SPACE-OPTIMIZED DYNAMIC PROGRAMMING")
    print("=" * 78)

    n = 30

    array_result = fibonacci_dp_array(n)
    optimized_result = fibonacci_dp_optimized(n)

    print(f"Array DP result:     {array_result}")
    print(f"Optimized DP result: {optimized_result}")

    print(
        """
The array version stores every previous result:

    dp[0], dp[1], ..., dp[n]

Space = O(n)

But Fibonacci only needs:

    previous_two
    previous_one

Therefore the optimized version uses:

    Space = O(1)

This illustrates an important optimization technique:

    Identify which previous states are actually required.

Do not store information that the future computation never uses.
"""
    )


# ============================================================================
# 25. SECURITY AND RELIABILITY CONSIDERATIONS
# ============================================================================

def security_and_reliability_notes() -> None:
    print("\n" + "=" * 78)
    print("25. SECURITY AND RELIABILITY CONSIDERATIONS")
    print("=" * 78)

    print(
        """
Space usage can become a security and reliability concern when input size is
controlled by an external user.

Examples:

    - An attacker supplies an extremely large input.
    - A program creates a map entry for every input element.
    - Deep recursion causes stack exhaustion.
    - Repeated string concatenation creates many temporary objects.
    - A cache grows without a defined limit.
    - A queue accumulates unprocessed work faster than it can be consumed.

Important defensive techniques include:

    - Validate input sizes.
    - Set reasonable collection limits.
    - Avoid unbounded caches.
    - Prefer iterative processing when recursion depth can be attacker-
      controlled.
    - Stream large data instead of loading everything into memory.
    - Release references to objects that are no longer needed.
    - Monitor memory consumption in production systems.
    - Define explicit failure behavior for oversized inputs.

Space complexity is therefore not merely an academic property. It can affect
availability, reliability, and resistance to resource-exhaustion failures.
"""
    )


# ============================================================================
# 26. DEBUGGING SPACE USAGE
# ============================================================================

def demonstrate_debugging_questions() -> None:
    print("\n" + "=" * 78)
    print("26. DEBUGGING SPACE USAGE")
    print("=" * 78)

    print(
        """
When memory usage is unexpectedly high, ask:

    1. Did I accidentally copy the input?
    2. Am I creating a slice repeatedly?
    3. Is a map or set growing for every element?
    4. Is recursion deeper than expected?
    5. Am I storing results that are never reused?
    6. Are temporary strings being created in a loop?
    7. Is a cache unbounded?
    8. Does a queue retain processed data?
    9. Am I keeping references to objects unnecessarily?
    10. Is the output itself being mistaken for auxiliary memory?

For serious applications, theoretical analysis should be combined with
runtime measurement and profiling.

Theoretical complexity predicts growth behavior.

Profiling reveals actual implementation behavior.

Both are useful.
"""
    )


# ============================================================================
# 27. FINAL SELF-TEST
# ============================================================================

def run_self_test() -> None:
    print("\n" + "=" * 78)
    print("27. SELF-TEST")
    print("=" * 78)

    assert factorial_iterative(0) == 1
    assert factorial_recursive(0) == 1
    assert factorial_iterative(6) == factorial_recursive(6)

    values = [1, 2, 3, 4]
    assert iterative_sum(values) == 10
    assert recursive_sum(values) == 10

    reversed_values = [1, 2, 3, 4]
    reverse_in_place(reversed_values)
    assert reversed_values == [4, 3, 2, 1]

    assert contains_duplicate_using_set([1, 2, 3, 2])
    assert not contains_duplicate_using_set([1, 2, 3])

    assert contains_duplicate_bruteforce([1, 2, 3, 2])
    assert not contains_duplicate_bruteforce([1, 2, 3])

    assert frequency_count([1, 1, 2]) == {1: 2, 2: 1}

    assert is_palindrome_in_place_style("racecar")
    assert not is_palindrome_in_place_style("python")

    assert maximum_sum_fixed_window([2, 1, 5, 1, 3, 2], 3) == 9

    assert fibonacci_dp_array(10) == 55
    assert fibonacci_dp_optimized(10) == 55

    print("All self-tests passed.")


# ============================================================================
# 28. QUICK REFERENCE
# ============================================================================

def quick_reference() -> None:
    print("\n" + "=" * 78)
    print("28. QUICK REFERENCE")
    print("=" * 78)

    print(
        """
Input space:
    Memory required to represent the input.

Auxiliary space:
    Additional working memory used by the algorithm.

O(1):
    Fixed amount of auxiliary memory.

O(n):
    Auxiliary memory grows linearly with input size.

O(k):
    Memory grows with a secondary parameter such as the number of distinct
    values.

Recursion:
    Include the maximum number of simultaneously active stack frames.

Array copy:
    Usually O(n) additional memory.

Map/set:
    Usually O(n) in the worst case, or O(k) when k distinct entries are stored.

In-place:
    Modifies existing storage while using little additional working memory.

Time and space:
    Analyze independently. A faster algorithm may require more memory.

Output:
    Required output memory may be reported separately from auxiliary space.

Practical rule:
    Count every data structure, temporary object, and active recursive frame
    whose size can grow with the input.
"""
    )


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("DAY 8 — SPACE COMPLEXITY")
    print("From absolute beginner concepts to advanced analysis")
    print("=" * 78)

    explain_space_complexity()
    input_space_and_auxiliary_space([2, 4, 6, 8])
    demonstrate_constant_space()
    demonstrate_array_space()
    demonstrate_in_place_algorithms()
    demonstrate_iterative_vs_recursive()
    demonstrate_recursion_stack()
    demonstrate_string_space()
    demonstrate_set_tradeoff()
    demonstrate_map_space()
    demonstrate_in_place_sorting()
    demonstrate_matrix_space()
    demonstrate_edge_cases()
    demonstrate_recursion_limit()
    demonstrate_explicit_stack()
    demonstrate_two_pointers()
    demonstrate_sliding_window()
    demonstrate_common_patterns()
    demonstrate_output_space()
    print_space_comparison()
    analyze_space_step_by_step()
    demonstrate_tradeoff_case()
    demonstrate_memoization()
    demonstrate_space_optimized_dp()
    security_and_reliability_notes()
    demonstrate_debugging_questions()
    run_self_test()
    quick_reference()

    print("\n" + "=" * 78)
    print("END OF DAY 8 — SPACE COMPLEXITY")
    print("=" * 78)


if __name__ == "__main__":
    main()
