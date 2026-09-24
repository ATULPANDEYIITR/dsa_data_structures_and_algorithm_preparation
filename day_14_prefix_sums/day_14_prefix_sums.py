"""
Day 14 — Prefix Sums
====================

A comprehensive study script covering:

- Prefix-sum construction
- Range-sum queries
- Subarray sums
- Prefix-frequency concepts
- Equilibrium index
- Multiple range queries
- Prefix-based counting
- Prefix sums with negative values
- Prefix-frequency maps
- 2D prefix sums
- Difference arrays
- Coordinate/complement reasoning
- Complexity analysis
- Validation and edge cases

The script uses only Python's standard library.
"""

from collections import Counter, defaultdict
from random import Random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL IDEA
# ---------------------------------------------------------------------------

def build_prefix_sum(numbers: Sequence[int]) -> List[int]:
    """
    Build a prefix-sum array with a leading zero.

    For:
        numbers = [3, 1, 4, 2]

    prefix becomes:
        [0, 3, 4, 8, 10]

    Meaning:
        prefix[i] = sum(numbers[0:i])

    Therefore:
        sum(numbers[left:right + 1]) = prefix[right + 1] - prefix[left]

    Time:  O(n)
    Space: O(n)
    """
    prefix = [0]

    for value in numbers:
        prefix.append(prefix[-1] + value)

    return prefix


def build_prefix_sum_without_leading_zero(numbers: Sequence[int]) -> List[int]:
    """
    Alternative representation:

        numbers = [3, 1, 4, 2]
        prefix  = [3, 4, 8, 10]

    This representation is valid but requires special handling when
    left == 0 during a range query.
    """
    prefix = []
    running_sum = 0

    for value in numbers:
        running_sum += value
        prefix.append(running_sum)

    return prefix


def demonstrate_prefix_construction() -> None:
    numbers = [3, 1, 4, 2, 5]

    prefix = build_prefix_sum(numbers)

    print("\n=== Prefix-sum construction ===")
    print("Array :", numbers)
    print("Prefix:", prefix)

    for index in range(1, len(prefix)):
        print(
            f"prefix[{index}] = {prefix[index]} "
            f"= sum(numbers[0:{index}])"
        )


# ---------------------------------------------------------------------------
# 2. RANGE-SUM QUERIES
# ---------------------------------------------------------------------------

def range_sum(
    prefix: Sequence[int],
    left: int,
    right: int,
) -> int:
    """
    Return the inclusive range sum numbers[left:right + 1].

    Formula:
        prefix[right + 1] - prefix[left]

    Example:
        numbers = [2, 5, 1, 7, 3]
        prefix  = [0, 2, 7, 8, 15, 18]

        sum(1..3) = prefix[4] - prefix[1]
                  = 15 - 2
                  = 13

    Time: O(1)
    """
    if left < 0 or right < 0:
        raise IndexError("Range indices cannot be negative.")

    if left > right:
        raise ValueError("left must not be greater than right.")

    if right + 1 >= len(prefix):
        raise IndexError("Range endpoint is outside the array.")

    return prefix[right + 1] - prefix[left]


def naive_range_sum(
    numbers: Sequence[int],
    left: int,
    right: int,
) -> int:
    """Reference implementation that takes O(length of queried range)."""
    if left < 0 or right >= len(numbers) or left > right:
        raise IndexError("Invalid range.")

    return sum(numbers[left:right + 1])


def demonstrate_range_queries() -> None:
    numbers = [2, 5, 1, 7, 3, 4]
    prefix = build_prefix_sum(numbers)

    queries = [
        (0, 2),
        (1, 4),
        (3, 5),
        (0, 5),
    ]

    print("\n=== Range-sum queries ===")
    print("Array :", numbers)
    print("Prefix:", prefix)

    for left, right in queries:
        result = range_sum(prefix, left, right)
        reference = naive_range_sum(numbers, left, right)

        print(
            f"sum[{left}:{right}] = {result}; "
            f"naive verification = {reference}"
        )


# ---------------------------------------------------------------------------
# 3. MULTIPLE RANGE QUERIES
# ---------------------------------------------------------------------------

def answer_range_queries(
    numbers: Sequence[int],
    queries: Iterable[Tuple[int, int]],
) -> List[int]:
    """
    Answer many static range-sum queries efficiently.

    Preprocessing:
        O(n)

    Each query:
        O(1)

    Total:
        O(n + q)
    """
    prefix = build_prefix_sum(numbers)
    answers = []

    for left, right in queries:
        answers.append(range_sum(prefix, left, right))

    return answers


def demonstrate_multiple_queries() -> None:
    numbers = [10, 20, 30, 40, 50]

    queries = [
        (0, 1),
        (1, 3),
        (2, 4),
        (0, 4),
    ]

    answers = answer_range_queries(numbers, queries)

    print("\n=== Multiple range queries ===")

    for query, answer in zip(queries, answers):
        print(f"{query} -> {answer}")


# ---------------------------------------------------------------------------
# 4. SUBARRAY SUMS
# ---------------------------------------------------------------------------

def enumerate_subarray_sums(numbers: Sequence[int]) -> List[Tuple[int, int, int]]:
    """
    Enumerate every contiguous subarray and its sum.

    Prefix sums allow each individual subarray sum to be obtained in O(1),
    but there are O(n^2) subarrays, so enumeration remains O(n^2).
    """
    prefix = build_prefix_sum(numbers)
    result = []

    for left in range(len(numbers)):
        for right in range(left, len(numbers)):
            total = prefix[right + 1] - prefix[left]
            result.append((left, right, total))

    return result


def demonstrate_subarray_sums() -> None:
    numbers = [2, -1, 3]

    print("\n=== Subarray sums ===")
    print("Array:", numbers)

    for left, right, total in enumerate_subarray_sums(numbers):
        print(
            f"subarray [{left}, {right}] "
            f"{numbers[left:right + 1]} -> {total}"
        )


# ---------------------------------------------------------------------------
# 5. TOTAL NUMBER OF SUBARRAYS
# ---------------------------------------------------------------------------

def number_of_subarrays(n: int) -> int:
    """
    Number of non-empty contiguous subarrays:

        n * (n + 1) / 2
    """
    return n * (n + 1) // 2


def demonstrate_subarray_count() -> None:
    print("\n=== Number of subarrays ===")

    for n in range(1, 7):
        print(f"n={n}: {number_of_subarrays(n)} subarrays")


# ---------------------------------------------------------------------------
# 6. EQUILIBRIUM INDEX
# ---------------------------------------------------------------------------

def equilibrium_indices(numbers: Sequence[int]) -> List[int]:
    """
    Find every index where:

        sum(elements before index)
        ==
        sum(elements after index)

    Let total be the entire array sum.

    At index i:
        left_sum = running sum
        right_sum = total - left_sum - numbers[i]

    Time: O(n)
    Space: O(1) apart from the result list.
    """
    total = sum(numbers)
    left_sum = 0
    result = []

    for index, value in enumerate(numbers):
        right_sum = total - left_sum - value

        if left_sum == right_sum:
            result.append(index)

        left_sum += value

    return result


def demonstrate_equilibrium_index() -> None:
    examples = [
        [-7, 1, 5, 2, -4, 3, 0],
        [1, 2, 3],
        [2, -2, 2, -2],
        [5],
    ]

    print("\n=== Equilibrium indices ===")

    for numbers in examples:
        print(numbers, "->", equilibrium_indices(numbers))


# ---------------------------------------------------------------------------
# 7. SUBARRAY SUM EQUAL TO K
# ---------------------------------------------------------------------------

def count_subarrays_with_sum_k(
    numbers: Sequence[int],
    target: int,
) -> int:
    """
    Count contiguous subarrays whose sum equals target.

    Core prefix-frequency identity:

        prefix[j] - prefix[i] = target

    Therefore:

        prefix[i] = prefix[j] - target

    While scanning the array, maintain the number of previous occurrences
    of each prefix sum.

    The initial prefix sum 0 occurs once. This handles subarrays beginning
    at index 0.

    Time: O(n) average-case with a hash map.
    Space: O(n).
    """
    frequency = defaultdict(int)
    frequency[0] = 1

    running_sum = 0
    count = 0

    for value in numbers:
        running_sum += value

        required_prefix = running_sum - target
        count += frequency[required_prefix]

        frequency[running_sum] += 1

    return count


def demonstrate_subarray_sum_k() -> None:
    examples = [
        ([1, 1, 1], 2),
        ([1, 2, 3], 3),
        ([1, -1, 0], 0),
        ([3, 4, 7, 2, -3, 1, 4, 2], 7),
        ([0, 0, 0], 0),
    ]

    print("\n=== Count subarrays with sum K ===")

    for numbers, target in examples:
        count = count_subarrays_with_sum_k(numbers, target)
        print(f"{numbers}, K={target} -> {count}")


# ---------------------------------------------------------------------------
# 8. LISTING SUBARRAYS WITH SUM K
# ---------------------------------------------------------------------------

def subarrays_with_sum_k(
    numbers: Sequence[int],
    target: int,
) -> List[Tuple[int, int]]:
    """
    Return (left, right) pairs for every subarray whose sum is target.

    A dictionary maps each prefix sum to all indices where that prefix
    occurred.

    If current prefix is P and P - target occurred at index i, then
    the subarray from i + 1 through the current index has sum target.

    Time: O(n + output size)
    Space: O(n + output size)
    """
    positions: Dict[int, List[int]] = defaultdict(list)
    positions[0].append(-1)

    running_sum = 0
    result = []

    for right, value in enumerate(numbers):
        running_sum += value
        required_prefix = running_sum - target

        for previous_index in positions.get(required_prefix, []):
            result.append((previous_index + 1, right))

        positions[running_sum].append(right)

    return result


def demonstrate_listing_subarrays() -> None:
    numbers = [1, 2, 1, 2, 1]
    target = 3

    print("\n=== List subarrays with target sum ===")

    for left, right in subarrays_with_sum_k(numbers, target):
        print(
            f"[{left}, {right}] -> "
            f"{numbers[left:right + 1]}"
        )


# ---------------------------------------------------------------------------
# 9. LONGEST SUBARRAY WITH SUM K
# ---------------------------------------------------------------------------

def longest_subarray_with_sum_k(
    numbers: Sequence[int],
    target: int,
) -> Tuple[int, Optional[Tuple[int, int]]]:
    """
    Find the maximum length subarray with sum target.

    Store only the first occurrence of each prefix sum.

    If:
        current_prefix - target = old_prefix

    then the earliest occurrence of old_prefix produces the longest
    possible subarray ending at the current position.

    Time: O(n) average.
    Space: O(n).
    """
    first_occurrence: Dict[int, int] = {0: -1}

    running_sum = 0
    best_length = 0
    best_range = None

    for index, value in enumerate(numbers):
        running_sum += value

        required_prefix = running_sum - target

        if required_prefix in first_occurrence:
            left_boundary = first_occurrence[required_prefix]
            length = index - left_boundary

            if length > best_length:
                best_length = length
                best_range = (left_boundary + 1, index)

        if running_sum not in first_occurrence:
            first_occurrence[running_sum] = index

    return best_length, best_range


def demonstrate_longest_subarray() -> None:
    numbers = [1, -1, 5, -2, 3]
    target = 3

    length, result = longest_subarray_with_sum_k(numbers, target)

    print("\n=== Longest subarray with sum K ===")
    print("Array:", numbers)
    print("Target:", target)
    print("Length:", length)
    print("Range:", result)


# ---------------------------------------------------------------------------
# 10. PREFIX-FREQUENCY CONCEPT
# ---------------------------------------------------------------------------

def prefix_frequency_table(numbers: Sequence[int]) -> Counter:
    """
    Count how often each prefix sum occurs.

    Repeated prefix sums imply a zero-sum subarray between their positions.
    """
    frequency = Counter()
    running_sum = 0

    frequency[0] += 1

    for value in numbers:
        running_sum += value
        frequency[running_sum] += 1

    return frequency


def demonstrate_prefix_frequency() -> None:
    numbers = [2, -2, 3, -3, 3]

    print("\n=== Prefix-frequency table ===")
    print("Array:", numbers)

    frequency = prefix_frequency_table(numbers)

    for prefix_value in sorted(frequency):
        print(f"Prefix sum {prefix_value}: {frequency[prefix_value]} occurrence(s)")


# ---------------------------------------------------------------------------
# 11. COUNT ZERO-SUM SUBARRAYS
# ---------------------------------------------------------------------------

def count_zero_sum_subarrays(numbers: Sequence[int]) -> int:
    """
    Count subarrays whose sum is zero.

    A zero-sum subarray exists whenever two prefix sums are equal.

    If a prefix value has frequency f, it contributes:

        f * (f - 1) / 2

    pairs of equal prefix positions.
    """
    frequency = Counter()
    frequency[0] = 1

    running_sum = 0
    count = 0

    for value in numbers:
        running_sum += value
        count += frequency[running_sum]
        frequency[running_sum] += 1

    return count


def demonstrate_zero_sum() -> None:
    examples = [
        [1, -1],
        [1, -1, 1, -1],
        [0, 0],
        [3, -1, -2, 4],
    ]

    print("\n=== Zero-sum subarrays ===")

    for numbers in examples:
        print(numbers, "->", count_zero_sum_subarrays(numbers))


# ---------------------------------------------------------------------------
# 12. COUNT SUBARRAYS WITH EVEN SUM
# ---------------------------------------------------------------------------

def count_subarrays_with_even_sum(numbers: Sequence[int]) -> int:
    """
    A subarray has even sum when the two prefix sums have the same parity.

    Maintain counts of:
        even prefix sums
        odd prefix sums

    If there are E even prefixes and O odd prefixes, the number of
    even-sum subarrays is:

        C(E, 2) + C(O, 2)
    """
    even_count = 1
    odd_count = 0
    running_sum = 0
    result = 0

    for value in numbers:
        running_sum += value

        if running_sum % 2 == 0:
            result += even_count
            even_count += 1
        else:
            result += odd_count
            odd_count += 1

    return result


def demonstrate_even_sum() -> None:
    numbers = [1, 2, 3, 4]

    print("\n=== Count subarrays with even sum ===")
    print(numbers, "->", count_subarrays_with_even_sum(numbers))


# ---------------------------------------------------------------------------
# 13. COUNT SUBARRAYS DIVISIBLE BY K
# ---------------------------------------------------------------------------

def count_subarrays_divisible_by_k(
    numbers: Sequence[int],
    k: int,
) -> int:
    """
    Count subarrays whose sum is divisible by k.

    If:
        prefix[j] % k == prefix[i] % k

    then:
        prefix[j] - prefix[i]

    is divisible by k.

    Python's modulo operation handles negative values consistently for
    a positive divisor, which makes the normalization below reliable.
    """
    if k == 0:
        raise ValueError("k cannot be zero.")

    frequency = Counter()
    frequency[0] = 1

    running_sum = 0
    result = 0

    for value in numbers:
        running_sum += value
        remainder = running_sum % k

        result += frequency[remainder]
        frequency[remainder] += 1

    return result


def demonstrate_divisible_by_k() -> None:
    numbers = [4, 5, 0, -2, -3, 1]

    print("\n=== Subarrays divisible by K ===")
    print(numbers, "k=5 ->", count_subarrays_divisible_by_k(numbers, 5))


# ---------------------------------------------------------------------------
# 14. PREFIX XOR: RELATED PREFIX TECHNIQUE
# ---------------------------------------------------------------------------

def count_subarrays_with_xor_k(
    numbers: Sequence[int],
    target: int,
) -> int:
    """
    XOR has a prefix technique analogous to arithmetic prefix sums.

    If:
        prefix_xor[j] XOR prefix_xor[i] = target

    then:
        prefix_xor[i] = prefix_xor[j] XOR target

    Time: O(n) average.
    """
    frequency = Counter()
    frequency[0] = 1

    running_xor = 0
    result = 0

    for value in numbers:
        running_xor ^= value

        required_prefix = running_xor ^ target
        result += frequency[required_prefix]
        frequency[running_xor] += 1

    return result


def demonstrate_prefix_xor() -> None:
    numbers = [4, 2, 2, 6, 4]

    print("\n=== Prefix XOR ===")
    print(
        f"{numbers}, target XOR=6 -> "
        f"{count_subarrays_with_xor_k(numbers, 6)}"
    )


# ---------------------------------------------------------------------------
# 15. 2D PREFIX SUM
# ---------------------------------------------------------------------------

def build_2d_prefix_sum(matrix: Sequence[Sequence[int]]) -> List[List[int]]:
    """
    Construct a two-dimensional prefix-sum matrix.

    prefix[r][c] stores the sum of the rectangle:

        rows 0 .. r-1
        columns 0 .. c-1

    Inclusion-exclusion formula:

        prefix[r][c]
        = matrix[r-1][c-1]
        + prefix[r-1][c]
        + prefix[r][c-1]
        - prefix[r-1][c-1]

    The leading row and column of zeros simplify boundary cases.
    """
    if not matrix:
        return [[0]]

    column_count = len(matrix[0])

    if any(len(row) != column_count for row in matrix):
        raise ValueError("All matrix rows must have equal length.")

    prefix = [
        [0] * (column_count + 1)
        for _ in range(len(matrix) + 1)
    ]

    for row in range(1, len(matrix) + 1):
        for column in range(1, column_count + 1):
            prefix[row][column] = (
                matrix[row - 1][column - 1]
                + prefix[row - 1][column]
                + prefix[row][column - 1]
                - prefix[row - 1][column - 1]
            )

    return prefix


def rectangle_sum(
    prefix: Sequence[Sequence[int]],
    top: int,
    left: int,
    bottom: int,
    right: int,
) -> int:
    """Return the inclusive rectangle sum in O(1)."""
    if top < 0 or left < 0 or top > bottom or left > right:
        raise ValueError("Invalid rectangle.")

    return (
        prefix[bottom + 1][right + 1]
        - prefix[top][right + 1]
        - prefix[bottom + 1][left]
        + prefix[top][left]
    )


def demonstrate_2d_prefix_sum() -> None:
    matrix = [
        [3, 1, 2, 5],
        [4, 2, 0, 1],
        [7, 3, 6, 2],
    ]

    prefix = build_2d_prefix_sum(matrix)

    print("\n=== Two-dimensional prefix sums ===")

    for row in prefix:
        print(row)

    query = (0, 1, 2, 3)

    print(
        f"Rectangle {query} -> "
        f"{rectangle_sum(prefix, *query)}"
    )


# ---------------------------------------------------------------------------
# 16. DIFFERENCE ARRAYS
# ---------------------------------------------------------------------------

def apply_range_updates(
    size: int,
    updates: Iterable[Tuple[int, int, int]],
) -> List[int]:
    """
    Apply many inclusive range additions using a difference array.

    Each update:
        (left, right, delta)

    is represented by:
        difference[left] += delta
        difference[right + 1] -= delta

    A final prefix sum reconstructs the actual values.

    Time:
        O(n + q)

    This is closely related to prefix sums but solves the inverse-style
    problem of efficiently applying range modifications.
    """
    if size < 0:
        raise ValueError("size cannot be negative.")

    difference = [0] * (size + 1)

    for left, right, delta in updates:
        if not (0 <= left <= right < size):
            raise ValueError(f"Invalid update: {(left, right, delta)}")

        difference[left] += delta
        difference[right + 1] -= delta

    result = [0] * size
    running_value = 0

    for index in range(size):
        running_value += difference[index]
        result[index] = running_value

    return result


def demonstrate_difference_array() -> None:
    updates = [
        (1, 3, 5),
        (2, 5, 2),
        (0, 2, -1),
    ]

    print("\n=== Difference array ===")
    print("Updates:", updates)
    print("Result :", apply_range_updates(6, updates))


# ---------------------------------------------------------------------------
# 17. PREFIX MINIMUM AND RELATED PREFIX AGGREGATES
# ---------------------------------------------------------------------------

def build_prefix_minimum(numbers: Sequence[int]) -> List[int]:
    """Build prefix minimum values as an example of prefix aggregation."""
    if not numbers:
        return []

    result = []
    current_min = numbers[0]

    for value in numbers:
        current_min = min(current_min, value)
        result.append(current_min)

    return result


def demonstrate_prefix_minimum() -> None:
    numbers = [7, 4, 9, 2, 5, 1]

    print("\n=== Prefix minimum ===")
    print(numbers)
    print(build_prefix_minimum(numbers))


# ---------------------------------------------------------------------------
# 18. WHEN TWO-POINTERS CAN REPLACE PREFIX HASHING
# ---------------------------------------------------------------------------

def count_positive_subarrays_with_sum_at_most_k(
    numbers: Sequence[int],
    k: int,
) -> int:
    """
    Count subarrays with sum <= k when all numbers are strictly positive.

    A sliding window works because adding a positive number can only
    increase the sum, creating the monotonic property required by the
    technique.

    This demonstrates an important distinction:

    - Prefix sums are broadly applicable.
    - Sliding windows can be faster in some specialized problems.
    - Sliding windows generally fail for arbitrary negative values.
    """
    if any(value <= 0 for value in numbers):
        raise ValueError(
            "This sliding-window implementation requires strictly positive values."
        )

    left = 0
    running_sum = 0
    result = 0

    for right, value in enumerate(numbers):
        running_sum += value

        while running_sum > k and left <= right:
            running_sum -= numbers[left]
            left += 1

        result += right - left + 1

    return result


def demonstrate_sliding_window_comparison() -> None:
    numbers = [1, 2, 1, 1]
    k = 3

    print("\n=== Prefix techniques versus sliding window ===")
    print(
        "Positive array:",
        numbers,
        "sum <= 3 ->",
        count_positive_subarrays_with_sum_at_most_k(numbers, k),
    )


# ---------------------------------------------------------------------------
# 19. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases ===")

    cases = [
        [],
        [0],
        [5],
        [-5],
        [0, 0, 0],
        [-1, -2, -3],
        [10**12, -10**12],
    ]

    for numbers in cases:
        prefix = build_prefix_sum(numbers)
        print(
            f"array={numbers!r}, "
            f"prefix={prefix}, "
            f"zero_sum_count={count_zero_sum_subarrays(numbers)}"
        )


# ---------------------------------------------------------------------------
# 20. VALIDATION
# ---------------------------------------------------------------------------

def validate_range_sum_implementation() -> None:
    """
    Compare optimized range sums against a naive implementation on
    deterministic pseudo-random data.
    """
    random = Random(42)

    for _ in range(100):
        length = random.randint(1, 30)
        numbers = [random.randint(-20, 20) for _ in range(length)]
        prefix = build_prefix_sum(numbers)

        for _ in range(30):
            left = random.randint(0, length - 1)
            right = random.randint(left, length - 1)

            optimized = range_sum(prefix, left, right)
            reference = naive_range_sum(numbers, left, right)

            assert optimized == reference

    print("\nRange-sum randomized validation: PASSED")


def validate_subarray_sum_k() -> None:
    """
    Verify the O(n) frequency-map algorithm against brute force.
    """
    random = Random(7)

    for _ in range(100):
        length = random.randint(0, 15)
        numbers = [random.randint(-5, 5) for _ in range(length)]
        target = random.randint(-5, 5)

        optimized = count_subarrays_with_sum_k(numbers, target)

        brute_force = 0

        for left in range(length):
            running_sum = 0

            for right in range(left, length):
                running_sum += numbers[right]

                if running_sum == target:
                    brute_force += 1

        assert optimized == brute_force

    print("Subarray-sum randomized validation: PASSED")


# ---------------------------------------------------------------------------
# 21. COMPLEXITY TABLE
# ---------------------------------------------------------------------------

def print_complexity_reference() -> None:
    print("\n=== Complexity reference ===")

    rows = [
        ("Build 1D prefix sum", "O(n)", "O(n)"),
        ("One range-sum query", "O(1)", "O(1)"),
        ("q range queries", "O(n + q)", "O(n)"),
        ("Enumerate all subarray sums", "O(n^2)", "O(n^2) output"),
        ("Count subarrays with sum K", "O(n) average", "O(n)"),
        ("Longest subarray with sum K", "O(n) average", "O(n)"),
        ("2D prefix construction", "O(rows * cols)", "O(rows * cols)"),
        ("2D rectangle query", "O(1)", "O(1)"),
        ("Difference-array updates", "O(n + q)", "O(n)"),
    ]

    for operation, time, space in rows:
        print(f"{operation:40} Time: {time:18} Space: {space}")


# ---------------------------------------------------------------------------
# 22. COMMON MISTAKES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    print("\n=== Common mistakes ===")

    mistakes = [
        (
            "Forgetting the leading zero",
            "A prefix array with prefix[0] = 0 makes left-boundary queries uniform."
        ),
        (
            "Using prefix[right] - prefix[left]",
            "With a leading-zero prefix array, the correct formula is prefix[right + 1] - prefix[left]."
        ),
        (
            "Initializing prefix frequency incorrectly",
            "frequency[0] = 1 is required so subarrays beginning at index 0 can be counted."
        ),
        (
            "Keeping the latest index for a longest-subarray problem",
            "The earliest prefix occurrence gives the longest candidate."
        ),
        (
            "Assuming prefix sums require non-negative values",
            "Prefix sums work with negative values; sliding-window assumptions are different."
        ),
        (
            "Confusing a subarray with a subsequence",
            "A subarray must be contiguous. A subsequence does not have to be."
        ),
    ]

    for mistake, correction in mistakes:
        print(f"- {mistake}: {correction}")


# ---------------------------------------------------------------------------
# 23. INTEGRATED STUDY EXAMPLE
# ---------------------------------------------------------------------------

def integrated_example() -> None:
    """
    A small analytical workload showing how multiple prefix techniques
    can coexist in one program.
    """
    sales = [120, -20, 50, 80, -10, 60, 30]
    prefix = build_prefix_sum(sales)

    print("\n=== Integrated example ===")
    print("Daily changes:", sales)
    print("Cumulative values:", prefix)

    print(
        "Days 2 through 5 total:",
        range_sum(prefix, 2, 5),
    )

    target = 100
    print(
        f"Number of contiguous periods totaling {target}:",
        count_subarrays_with_sum_k(sales, target),
    )

    print(
        "Equilibrium indices:",
        equilibrium_indices(sales),
    )


# ---------------------------------------------------------------------------
# 24. MAIN DRIVER
# ---------------------------------------------------------------------------

def main() -> None:
    demonstrate_prefix_construction()
    demonstrate_range_queries()
    demonstrate_multiple_queries()
    demonstrate_subarray_sums()
    demonstrate_subarray_count()
    demonstrate_equilibrium_index()
    demonstrate_subarray_sum_k()
    demonstrate_listing_subarrays()
    demonstrate_longest_subarray()
    demonstrate_prefix_frequency()
    demonstrate_zero_sum()
    demonstrate_even_sum()
    demonstrate_divisible_by_k()
    demonstrate_prefix_xor()
    demonstrate_2d_prefix_sum()
    demonstrate_difference_array()
    demonstrate_prefix_minimum()
    demonstrate_sliding_window_comparison()
    demonstrate_edge_cases()
    validate_range_sum_implementation()
    validate_subarray_sum_k()
    print_complexity_reference()
    demonstrate_common_mistakes()
    integrated_example()

    print("\n=== Study script completed successfully ===")


if __name__ == "__main__":
    main()
