"""
Day 12 — Array Fundamentals
============================

A comprehensive standalone study script covering:

Core concepts
-------------
- Indexing
- Traversal
- Updating
- Searching
- Minimum and maximum
- Frequency counting

Practice problems
-----------------
- Maximum element
- Minimum element
- Second-largest element
- Reverse array
- Rotate array
- Remove duplicates
- Count positive and negative values
- Find missing values

The examples progress from basic array/list operations to more advanced
linear-time techniques, edge cases, validation, and complexity analysis.

Python uses the built-in list as its general-purpose dynamic array.
"""

from collections import Counter
from typing import Iterable, Optional


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def demonstrate_array_creation() -> None:
    section("1. Array creation and basic properties")

    numbers = [10, 20, 30, 40, 50]

    print("Array:", numbers)
    print("Number of elements:", len(numbers))
    print("First element:", numbers[0])
    print("Last element:", numbers[-1])

    # Python lists are zero-indexed:
    # index 0 -> first element
    # index 1 -> second element
    # index n-1 -> last element
    for index in range(len(numbers)):
        print(f"index={index}, value={numbers[index]}")

    # Slicing creates a new list containing a selected range.
    print("First three:", numbers[:3])
    print("Elements from index 2:", numbers[2:])
    print("Every second element:", numbers[::2])
    print("Reversed using slicing:", numbers[::-1])


# ============================================================================
# 2. INDEXING
# ============================================================================

def demonstrate_indexing() -> None:
    section("2. Indexing")

    values = [15, 25, 35, 45, 55]

    print("Array:", values)

    # Positive indexes count from the beginning.
    print("values[0] =", values[0])
    print("values[2] =", values[2])
    print("values[4] =", values[4])

    # Negative indexes count backward from the end.
    print("values[-1] =", values[-1])
    print("values[-2] =", values[-2])

    # An invalid index raises IndexError.
    try:
        print(values[100])
    except IndexError as error:
        print("Invalid index handled:", error)


# ============================================================================
# 3. TRAVERSAL
# ============================================================================

def demonstrate_traversal() -> None:
    section("3. Traversal")

    values = [4, 8, 15, 16, 23, 42]

    subsection("Value-based traversal")
    for value in values:
        print(value)

    subsection("Index-based traversal")
    for index in range(len(values)):
        print(f"index={index}, value={values[index]}")

    subsection("Traversal with enumerate")
    for index, value in enumerate(values):
        print(f"index={index}, value={value}")

    subsection("Reverse traversal")
    for value in reversed(values):
        print(value)

    # Traversal is normally O(n) because each element is visited once.


# ============================================================================
# 4. UPDATING ELEMENTS
# ============================================================================

def demonstrate_updating() -> None:
    section("4. Updating array elements")

    values = [10, 20, 30, 40, 50]
    print("Before:", values)

    # Updating a known position is O(1).
    values[2] = 999
    print("After values[2] = 999:", values)

    # Updating every element requires traversal and is O(n).
    for index in range(len(values)):
        values[index] *= 2

    print("After doubling every element:", values)

    # A list comprehension is a concise transformation.
    values = [value + 1 for value in values]
    print("After adding 1 to every element:", values)


# ============================================================================
# 5. SEARCHING
# ============================================================================

def linear_search(values: list[int], target: int) -> int:
    """
    Return the first index containing target.

    Returns -1 when target is absent.

    Complexity:
        Best case: O(1)
        Worst case: O(n)
        Extra space: O(1)
    """
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def demonstrate_searching() -> None:
    section("5. Searching")

    values = [17, 4, 29, 8, 31, 12]

    for target in [29, 100, 17]:
        index = linear_search(values, target)
        if index == -1:
            print(f"{target} was not found")
        else:
            print(f"{target} found at index {index}")

    # Python's `in` operator is convenient for membership testing.
    print("31 in values:", 31 in values)
    print("100 in values:", 100 in values)


# ============================================================================
# 6. MINIMUM AND MAXIMUM
# ============================================================================

def manual_minimum(values: list[int]) -> int:
    """Find minimum without using min()."""
    if not values:
        raise ValueError("Cannot find minimum of an empty array")

    smallest = values[0]

    for value in values[1:]:
        if value < smallest:
            smallest = value

    return smallest


def manual_maximum(values: list[int]) -> int:
    """Find maximum without using max()."""
    if not values:
        raise ValueError("Cannot find maximum of an empty array")

    largest = values[0]

    for value in values[1:]:
        if value > largest:
            largest = value

    return largest


def demonstrate_minimum_maximum() -> None:
    section("6. Minimum and maximum")

    values = [34, 7, 91, 23, 56, 12]

    print("Array:", values)
    print("Manual minimum:", manual_minimum(values))
    print("Manual maximum:", manual_maximum(values))
    print("Built-in minimum:", min(values))
    print("Built-in maximum:", max(values))

    try:
        manual_minimum([])
    except ValueError as error:
        print("Empty-array case:", error)


# ============================================================================
# 7. FREQUENCY COUNTING
# ============================================================================

def frequency_count_manual(values: Iterable[int]) -> dict[int, int]:
    """
    Count how many times every value occurs.

    Average complexity: O(n)
    Extra space: O(k), where k is the number of distinct values.
    """
    frequencies: dict[int, int] = {}

    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    return frequencies


def demonstrate_frequency_counting() -> None:
    section("7. Frequency counting")

    values = [2, 5, 2, 8, 5, 2, 9, 8, 8]

    print("Array:", values)
    print("Manual frequency table:", frequency_count_manual(values))

    # Counter is optimized and purpose-built for frequency counting.
    print("Counter:", dict(Counter(values)))

    # Frequency can answer questions such as:
    frequencies = frequency_count_manual(values)

    for number in [2, 5, 100]:
        print(f"Frequency of {number}:", frequencies.get(number, 0))


# ============================================================================
# 8. MAXIMUM ELEMENT
# ============================================================================

def maximum_element(values: list[int]) -> Optional[int]:
    """Return maximum value or None for an empty array."""
    if not values:
        return None

    largest = values[0]
    for value in values[1:]:
        if value > largest:
            largest = value

    return largest


# ============================================================================
# 9. MINIMUM ELEMENT
# ============================================================================

def minimum_element(values: list[int]) -> Optional[int]:
    """Return minimum value or None for an empty array."""
    if not values:
        return None

    smallest = values[0]
    for value in values[1:]:
        if value < smallest:
            smallest = value

    return smallest


# ============================================================================
# 10. SECOND-LARGEST ELEMENT
# ============================================================================

def second_largest_distinct(values: list[int]) -> Optional[int]:
    """
    Find the second-largest DISTINCT value.

    Example:
        [10, 20, 20, 5] -> 10

    This uses one pass and O(1) additional space.

    Time: O(n)
    Space: O(1)
    """
    if len(values) < 2:
        return None

    largest: Optional[int] = None
    second_largest: Optional[int] = None

    for value in values:
        if largest is None or value > largest:
            second_largest = largest
            largest = value
        elif value != largest and (
            second_largest is None or value > second_largest
        ):
            second_largest = value

    return second_largest


def demonstrate_second_largest() -> None:
    section("8. Second-largest distinct element")

    test_cases = [
        [10, 20, 5, 8, 30],
        [30, 30, 20, 10],
        [5, 5, 5],
        [-10, -20, -3, -7],
        [1],
        [],
    ]

    for values in test_cases:
        print(
            f"{values} -> "
            f"second-largest distinct = {second_largest_distinct(values)}"
        )


# ============================================================================
# 11. REVERSE ARRAY
# ============================================================================

def reverse_in_place(values: list[int]) -> None:
    """
    Reverse the array in-place using two pointers.

    Time: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        values[left], values[right] = values[right], values[left]
        left += 1
        right -= 1


def demonstrate_reverse() -> None:
    section("9. Reverse array")

    values = [1, 2, 3, 4, 5, 6]
    print("Before:", values)

    reverse_in_place(values)

    print("After:", values)

    # Python slicing creates a new list rather than modifying the original.
    original = [1, 2, 3, 4]
    reversed_copy = original[::-1]

    print("Original:", original)
    print("Reversed copy:", reversed_copy)


# ============================================================================
# 12. ROTATE ARRAY
# ============================================================================

def rotate_right(values: list[int], k: int) -> list[int]:
    """
    Return a new array rotated right by k positions.

    Example:
        [1,2,3,4,5], k=2 -> [4,5,1,2,3]

    k is normalized so values greater than n are handled correctly.
    """
    if not values:
        return []

    k %= len(values)

    if k == 0:
        return values.copy()

    return values[-k:] + values[:-k]


def rotate_right_in_place(values: list[int], k: int) -> None:
    """
    In-place right rotation using the reversal algorithm.

    Example:
        [1,2,3,4,5], k=2
        reverse all -> [5,4,3,2,1]
        reverse first 2 -> [4,5,3,2,1]
        reverse rest -> [4,5,1,2,3]

    Time: O(n)
    Extra space: O(1)
    """
    if not values:
        return

    k %= len(values)

    if k == 0:
        return

    def reverse_range(start: int, end: int) -> None:
        while start < end:
            values[start], values[end] = values[end], values[start]
            start += 1
            end -= 1

    reverse_range(0, len(values) - 1)
    reverse_range(0, k - 1)
    reverse_range(k, len(values) - 1)


def demonstrate_rotation() -> None:
    section("10. Rotate array")

    values = [1, 2, 3, 4, 5]

    for k in [0, 1, 2, 5, 7, -1]:
        print(f"Right rotation by {k}: {rotate_right(values, k)}")

    in_place_values = [1, 2, 3, 4, 5]
    rotate_right_in_place(in_place_values, 2)
    print("In-place rotation by 2:", in_place_values)


# ============================================================================
# 13. REMOVE DUPLICATES
# ============================================================================

def remove_duplicates_preserve_order(values: list[int]) -> list[int]:
    """
    Remove duplicates while preserving first-occurrence order.

    Average time: O(n)
    Extra space: O(k)
    """
    seen: set[int] = set()
    result: list[int] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def demonstrate_remove_duplicates() -> None:
    section("11. Remove duplicates")

    values = [4, 2, 4, 7, 2, 9, 7, 1]
    print("Original:", values)
    print(
        "Unique, preserving order:",
        remove_duplicates_preserve_order(values),
    )

    # For sorted arrays, duplicate removal can be performed in-place with
    # two pointers. This is a different problem because sorted order helps.
    sorted_values = [1, 1, 2, 2, 2, 3, 4, 4]

    write_index = 1

    for read_index in range(1, len(sorted_values)):
        if sorted_values[read_index] != sorted_values[read_index - 1]:
            sorted_values[write_index] = sorted_values[read_index]
            write_index += 1

    compacted = sorted_values[:write_index]

    print("Sorted input:", sorted_values)
    print("Unique sorted result:", compacted)


# ============================================================================
# 14. COUNT POSITIVE AND NEGATIVE VALUES
# ============================================================================

def count_positive_negative(values: list[int]) -> tuple[int, int, int]:
    """
    Return positive count, negative count, and zero count.
    """
    positive = 0
    negative = 0
    zero = 0

    for value in values:
        if value > 0:
            positive += 1
        elif value < 0:
            negative += 1
        else:
            zero += 1

    return positive, negative, zero


def demonstrate_sign_counts() -> None:
    section("12. Count positive, negative, and zero values")

    values = [-5, 0, 8, -2, 7, 0, -10, 4]
    positive, negative, zero = count_positive_negative(values)

    print("Array:", values)
    print("Positive:", positive)
    print("Negative:", negative)
    print("Zero:", zero)


# ============================================================================
# 15. FIND MISSING VALUES
# ============================================================================

def missing_values_using_set(
    values: list[int],
    start: int,
    end: int,
) -> list[int]:
    """
    Find all missing integers in an inclusive range.

    Example:
        values = [1, 2, 4, 6]
        range = 1..6
        result = [3, 5]

    Time: O(n + r)
    Extra space: O(n + m)
    """
    present = set(values)
    return [number for number in range(start, end + 1) if number not in present]


def missing_single_value_xor(values: list[int], n: int) -> Optional[int]:
    """
    Find the single missing value from [0, n].

    Example:
        [3, 0, 1] -> 2

    XOR has the useful properties:
        x ^ x = 0
        x ^ 0 = x

    Time: O(n)
    Extra space: O(1)

    Assumption:
        Every number from 0 through n occurs at most once and exactly
        one number is missing.
    """
    if len(values) != n:
        return None

    missing = n

    for index, value in enumerate(values):
        missing ^= index
        missing ^= value

    return missing


def demonstrate_missing_values() -> None:
    section("13. Find missing values")

    values = [1, 2, 4, 6, 7, 9]
    print("Array:", values)
    print("Missing values from 1..9:", missing_values_using_set(values, 1, 9))

    single_missing = [3, 0, 1]
    print(
        "Single missing value from 0..3:",
        missing_single_value_xor(single_missing, 3),
    )


# ============================================================================
# 16. ARRAY INPUT VALIDATION
# ============================================================================

def parse_integer_array(text: str) -> list[int]:
    """
    Convert whitespace-separated text into integers.

    Empty input produces an empty list.
    Invalid input raises ValueError with a useful message.
    """
    if not text.strip():
        return []

    tokens = text.split()
    result: list[int] = []

    for token in tokens:
        try:
            result.append(int(token))
        except ValueError as error:
            raise ValueError(
                f"Invalid integer: {token!r}"
            ) from error

    return result


def demonstrate_validation() -> None:
    section("14. Input validation")

    examples = [
        "10 20 -5 7",
        "",
        "5 8 abc 12",
    ]

    for text in examples:
        try:
            print(f"Input: {text!r} -> {parse_integer_array(text)}")
        except ValueError as error:
            print(f"Input: {text!r} -> error: {error}")


# ============================================================================
# 17. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    section("15. Edge cases")

    test_arrays = [
        [],
        [42],
        [7, 7, 7],
        [-5, -2, -10],
        [0, 0, 0],
        [-2, 0, 5, -7, 8],
    ]

    for values in test_arrays:
        print("\nArray:", values)
        print("Minimum:", minimum_element(values))
        print("Maximum:", maximum_element(values))
        print("Second-largest distinct:", second_largest_distinct(values))
        print("Reversed:", values[::-1])
        print("Unique:", remove_duplicates_preserve_order(values))

    # Rotation of an empty array is safe.
    print("\nRotate empty array:", rotate_right([], 4))

    # Rotation by a multiple of the length changes nothing.
    print("Rotate [1,2,3] by 6:", rotate_right([1, 2, 3], 6))


# ============================================================================
# 18. COMBINED ARRAY ANALYSIS
# ============================================================================

def analyze_array(values: list[int]) -> dict:
    """
    Perform several common array analyses in one traversal where possible.

    This demonstrates an important optimization principle:
    related O(n) calculations can sometimes be combined into one pass.
    """
    if not values:
        return {
            "length": 0,
            "minimum": None,
            "maximum": None,
            "positive": 0,
            "negative": 0,
            "zero": 0,
            "frequencies": {},
        }

    minimum = values[0]
    maximum = values[0]
    positive = 0
    negative = 0
    zero = 0
    frequencies: dict[int, int] = {}

    for value in values:
        if value < minimum:
            minimum = value

        if value > maximum:
            maximum = value

        if value > 0:
            positive += 1
        elif value < 0:
            negative += 1
        else:
            zero += 1

        frequencies[value] = frequencies.get(value, 0) + 1

    return {
        "length": len(values),
        "minimum": minimum,
        "maximum": maximum,
        "positive": positive,
        "negative": negative,
        "zero": zero,
        "frequencies": frequencies,
    }


def demonstrate_combined_analysis() -> None:
    section("16. Combined array analysis")

    values = [8, -2, 5, 8, 0, -2, 11, 5, 5]
    analysis = analyze_array(values)

    for key, value in analysis.items():
        print(f"{key}: {value}")


# ============================================================================
# 19. SORTED-ARRAY SEARCHING
# ============================================================================

def binary_search(values: list[int], target: int) -> int:
    """
    Binary search for a target in a sorted array.

    Time:
        O(log n)

    Space:
        O(1)

    Requirement:
        The input must already be sorted in ascending order.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    section("17. Linear search versus binary search")

    sorted_values = [3, 8, 12, 19, 24, 31, 45, 50]

    print("Sorted array:", sorted_values)

    for target in [3, 24, 50, 100]:
        print(
            f"Target {target}: "
            f"linear={linear_search(sorted_values, target)}, "
            f"binary={binary_search(sorted_values, target)}"
        )


# ============================================================================
# 20. PREFIX SUM
# ============================================================================

def prefix_sums(values: list[int]) -> list[int]:
    """
    Construct prefix sums.

    Example:
        [2, 4, 6] -> [2, 6, 12]

    A prefix-sum array allows many contiguous range sums to be answered
    in O(1) after O(n) preprocessing.
    """
    result: list[int] = []
    running_total = 0

    for value in values:
        running_total += value
        result.append(running_total)

    return result


def range_sum(prefix: list[int], left: int, right: int) -> int:
    """Return sum of values from left through right, inclusive."""
    if left < 0 or right >= len(prefix) or left > right:
        raise IndexError("Invalid range")

    if left == 0:
        return prefix[right]

    return prefix[right] - prefix[left - 1]


def demonstrate_prefix_sum() -> None:
    section("18. Prefix sums")

    values = [5, 2, 7, 3, 10]
    prefix = prefix_sums(values)

    print("Values:", values)
    print("Prefix sums:", prefix)

    print("Sum indices 1..3:", range_sum(prefix, 1, 3))
    print("Sum indices 0..4:", range_sum(prefix, 0, 4))


# ============================================================================
# 21. TWO-POINTER TECHNIQUE
# ============================================================================

def two_sum_sorted(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Find two values in a sorted array whose sum equals target.

    Returns the pair of indexes when found.

    Time: O(n)
    Space: O(1)
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


def demonstrate_two_pointers() -> None:
    section("19. Two-pointer technique")

    values = [1, 3, 4, 6, 8, 10, 13]
    target = 14

    result = two_sum_sorted(values, target)

    print("Sorted array:", values)
    print("Target:", target)

    if result is None:
        print("No pair found")
    else:
        left, right = result
        print(
            f"Pair found at indexes {left} and {right}: "
            f"{values[left]} + {values[right]} = {target}"
        )


# ============================================================================
# 22. FREQUENCY-BASED DUPLICATE DETECTION
# ============================================================================

def find_duplicates(values: list[int]) -> list[int]:
    """Return values occurring at least twice, preserving first duplicate order."""
    frequencies = frequency_count_manual(values)
    duplicates: list[int] = []
    already_added: set[int] = set()

    for value in values:
        if frequencies[value] > 1 and value not in already_added:
            duplicates.append(value)
            already_added.add(value)

    return duplicates


def demonstrate_duplicates() -> None:
    section("20. Duplicate detection using frequency counting")

    values = [4, 7, 4, 9, 7, 7, 2, 1, 9]
    print("Array:", values)
    print("Duplicates:", find_duplicates(values))


# ============================================================================
# 23. COMPLEXITY REFERENCE
# ============================================================================

def print_complexity_reference() -> None:
    section("21. Complexity reference")

    rows = [
        ("Index access", "O(1)", "O(1)"),
        ("Update by index", "O(1)", "O(1)"),
        ("Traversal", "O(n)", "O(1)"),
        ("Linear search", "O(n)", "O(1)"),
        ("Minimum/maximum", "O(n)", "O(1)"),
        ("Frequency counting", "O(n)", "O(k)"),
        ("Reverse in place", "O(n)", "O(1)"),
        ("Rotate using slicing", "O(n)", "O(n)"),
        ("Rotate using reversal", "O(n)", "O(1)"),
        ("Remove duplicates with set", "O(n) average", "O(k)"),
        ("Binary search", "O(log n)", "O(1)"),
        ("Prefix-sum construction", "O(n)", "O(n)"),
    ]

    print(f"{'Operation':35} {'Time':18} {'Extra space'}")
    print("-" * 78)

    for operation, time, space in rows:
        print(f"{operation:35} {time:18} {space}")


# ============================================================================
# 24. PRACTICE TEST SUITE
# ============================================================================

def assert_equal(actual, expected, description: str) -> None:
    """Small local testing helper."""
    if actual != expected:
        raise AssertionError(
            f"{description}: expected {expected!r}, got {actual!r}"
        )


def run_tests() -> None:
    section("22. Verification tests")

    assert_equal(maximum_element([3, 1, 9, 2]), 9, "maximum")
    assert_equal(minimum_element([3, 1, 9, 2]), 1, "minimum")
    assert_equal(
        second_largest_distinct([10, 30, 20, 30]),
        20,
        "second-largest distinct",
    )

    values = [1, 2, 3, 4]
    reverse_in_place(values)
    assert_equal(values, [4, 3, 2, 1], "reverse")

    assert_equal(
        rotate_right([1, 2, 3, 4, 5], 2),
        [4, 5, 1, 2, 3],
        "rotation",
    )

    assert_equal(
        remove_duplicates_preserve_order([1, 2, 1, 3, 2]),
        [1, 2, 3],
        "duplicate removal",
    )

    assert_equal(
        count_positive_negative([-2, 0, 3, 5, -1]),
        (2, 2, 1),
        "sign counting",
    )

    assert_equal(
        missing_values_using_set([1, 2, 4, 6], 1, 6),
        [3, 5],
        "missing values",
    )

    assert_equal(
        missing_single_value_xor([3, 0, 1], 3),
        2,
        "single missing value",
    )

    assert_equal(linear_search([5, 8, 2], 8), 1, "linear search")
    assert_equal(binary_search([2, 4, 6, 8, 10], 8), 3, "binary search")

    assert_equal(
        prefix_sums([2, 4, 6]),
        [2, 6, 12],
        "prefix sums",
    )

    assert_equal(
        two_sum_sorted([1, 3, 4, 6, 8], 10),
        (1, 4),
        "two pointers",
    )

    print("All tests passed.")


# ============================================================================
# 25. MAIN PROGRAM
# ============================================================================

def main() -> None:
    """
    Run the complete Day 12 study session.

    The program is intentionally executable from start to finish.
    """
    section("DAY 12 — ARRAY FUNDAMENTALS")

    demonstrate_array_creation()
    demonstrate_indexing()
    demonstrate_traversal()
    demonstrate_updating()
    demonstrate_searching()
    demonstrate_minimum_maximum()
    demonstrate_frequency_counting()
    demonstrate_second_largest()
    demonstrate_reverse()
    demonstrate_rotation()
    demonstrate_remove_duplicates()
    demonstrate_sign_counts()
    demonstrate_missing_values()
    demonstrate_validation()
    demonstrate_edge_cases()
    demonstrate_combined_analysis()
    demonstrate_binary_search()
    demonstrate_prefix_sum()
    demonstrate_two_pointers()
    demonstrate_duplicates()
    print_complexity_reference()
    run_tests()

    section("Day 12 practice checklist")

    practice_tasks = [
        "Find the maximum element",
        "Find the minimum element",
        "Find the second-largest distinct element",
        "Reverse an array",
        "Rotate an array",
        "Remove duplicates",
        "Count positive and negative values",
        "Find missing values",
    ]

    for number, task in enumerate(practice_tasks, start=1):
        print(f"{number}. {task}")

    print("\nDay 12 study program completed.")


if __name__ == "__main__":
    main()
