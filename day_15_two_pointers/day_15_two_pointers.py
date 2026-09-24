"""
Day 15 — Two Pointers
=====================

A comprehensive standalone study script covering:

- Opposite-direction pointers
- Same-direction pointers
- Sorted-array techniques
- Pair sum
- Remove duplicates
- Reverse array
- Container-style problems
- Three-sum foundations
- Partition-style problems
- Edge cases
- Correctness reasoning
- Complexity analysis
- Common mistakes
- Advanced variations
- Testing and validation

The script uses only the Python standard library.
"""


from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple
import random
import unittest


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain_pointer_models() -> None:
    print_section("1. TWO-POINTER FUNDAMENTALS")

    print(
        """
A two-pointer algorithm maintains two indices, references, or iterators
while processing a sequence.

The main models demonstrated in this script are:

1. Opposite-direction pointers:
       left starts near the beginning.
       right starts near the end.
       The pointers move toward each other.

2. Same-direction pointers:
       both pointers move from left to right.
       One pointer often reads while another writes.

3. Sorted-array techniques:
       sorting creates an ordering property that allows one pointer to
       move safely without examining every possible pair.

The main benefit is often a reduction from O(n^2) brute force to O(n),
or from O(n^3) to O(n^2) for problems such as three-sum.
"""
    )


# ---------------------------------------------------------------------------
# 2. OPPOSITE-DIRECTION POINTERS
# ---------------------------------------------------------------------------

def pair_sum_sorted(numbers: Sequence[int], target: int) -> Optional[Tuple[int, int]]:
    """
    Return the indices of two values whose sum equals target.

    Requirement:
        numbers must already be sorted in nondecreasing order.

    Two-pointer invariant:
        - If numbers[left] + numbers[right] is too small, increasing left
          is the only direction that can increase the sum.
        - If the sum is too large, decreasing right is the only direction
          that can decrease the sum.

    Time: O(n)
    Space: O(1)
    """
    left = 0
    right = len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]

        if current_sum == target:
            return left, right

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


def pair_sum_sorted_values(
    numbers: Sequence[int], target: int
) -> Optional[Tuple[int, int]]:
    """Return the values rather than their indices."""
    result = pair_sum_sorted(numbers, target)

    if result is None:
        return None

    left, right = result
    return numbers[left], numbers[right]


def pair_sum_brute_force(
    numbers: Sequence[int], target: int
) -> Optional[Tuple[int, int]]:
    """
    Reference implementation.

    Time: O(n^2)
    Space: O(1)
    """
    for left in range(len(numbers)):
        for right in range(left + 1, len(numbers)):
            if numbers[left] + numbers[right] == target:
                return left, right

    return None


def demonstrate_pair_sum() -> None:
    print_section("2. PAIR SUM")

    numbers = [1, 2, 4, 6, 8, 9, 11]
    target = 15

    print("Sorted numbers:", numbers)
    print("Target:", target)
    print("Two-pointer indices:", pair_sum_sorted(numbers, target))
    print("Two-pointer values:", pair_sum_sorted_values(numbers, target))

    examples = [
        ([1, 2, 3, 4, 5], 7),
        ([1, 2, 3, 4, 5], 100),
        ([], 10),
        ([5], 10),
        ([1, 1, 1, 2], 2),
    ]

    for values, target_value in examples:
        print(
            f"values={values}, target={target_value}, "
            f"result={pair_sum_sorted(values, target_value)}"
        )

    print(
        """
Important:
The two-pointer version depends on sorted order. If an arbitrary
unsorted array is supplied, moving a pointer based on the current sum
is not generally valid.

For an unsorted array, a hash-map approach can solve pair sum in
expected O(n) time, while sorting first costs O(n log n).
"""
    )


# ---------------------------------------------------------------------------
# 3. REVERSE ARRAY
# ---------------------------------------------------------------------------

def reverse_in_place(values: List[int]) -> None:
    """
    Reverse a list in place using opposite-direction pointers.

    Time: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        values[left], values[right] = values[right], values[left]
        left += 1
        right -= 1


def is_palindrome(values: Sequence[int]) -> bool:
    """
    Check whether a sequence reads identically in both directions.

    Time: O(n)
    Space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        if values[left] != values[right]:
            return False

        left += 1
        right -= 1

    return True


def demonstrate_reverse_and_palindrome() -> None:
    print_section("3. REVERSE ARRAY AND PALINDROME")

    values = [10, 20, 30, 40, 50]
    print("Before:", values)
    reverse_in_place(values)
    print("After:", values)

    for example in [
        [1, 2, 3, 2, 1],
        [1, 2, 3],
        [],
        [7],
        [4, 4],
    ]:
        print(f"{example} -> palindrome={is_palindrome(example)}")


# ---------------------------------------------------------------------------
# 4. SAME-DIRECTION POINTERS
# ---------------------------------------------------------------------------

def remove_duplicates_sorted(values: List[int]) -> int:
    """
    Remove duplicates from a sorted list in place.

    The returned integer is the logical length of the unique prefix.

    Example:
        [1, 1, 2, 2, 3]
        becomes [1, 2, 3, 2, 3]
        and returns 3.

    Only values[:returned_length] are logically part of the result.

    Read pointer:
        scans every element.

    Write pointer:
        records the next location where a new unique value belongs.

    Time: O(n)
    Extra space: O(1)
    """
    if not values:
        return 0

    write = 1

    for read in range(1, len(values)):
        if values[read] != values[write - 1]:
            values[write] = values[read]
            write += 1

    return write


def demonstrate_remove_duplicates() -> None:
    print_section("4. SAME-DIRECTION POINTERS: REMOVE DUPLICATES")

    examples = [
        [1, 1, 2, 2, 3, 3, 3, 4],
        [],
        [5],
        [2, 2, 2, 2],
        [1, 2, 3, 4],
    ]

    for values in examples:
        original = values.copy()
        length = remove_duplicates_sorted(values)

        print(
            f"original={original}, "
            f"unique_prefix={values[:length]}, "
            f"logical_length={length}"
        )

    print(
        """
This technique is a classic read/write-pointer pattern.

It does not require a second array because the portion before the write
pointer contains the already-processed result.
"""
    )


def move_zeroes(values: List[int]) -> None:
    """
    Move all zeroes to the end while preserving the relative order
    of nonzero values.

    This is another read/write-pointer technique.

    Time: O(n)
    Extra space: O(1)
    """
    write = 0

    for read in range(len(values)):
        if values[read] != 0:
            values[write], values[read] = values[read], values[write]
            write += 1


def demonstrate_move_zeroes() -> None:
    print_section("5. SAME-DIRECTION POINTERS: MOVE ZEROES")

    examples = [
        [0, 1, 0, 3, 12],
        [0, 0, 0],
        [1, 2, 3],
        [],
        [4, 0, 5, 0, 6],
    ]

    for values in examples:
        move_zeroes(values)
        print(values)


# ---------------------------------------------------------------------------
# 5. CONTAINER-STYLE PROBLEMS
# ---------------------------------------------------------------------------

def max_container_area(heights: Sequence[int]) -> int:
    """
    Solve the classic maximum-container problem.

    For boundaries left and right:

        width = right - left
        height = min(height[left], height[right])

        area = width * height

    Why move the shorter boundary?

    The current width decreases after every move. If the shorter boundary
    stays in place, the limiting height cannot increase. Moving the taller
    boundary cannot produce a better area with the current shorter boundary.

    Therefore the shorter boundary is the only useful candidate to move.

    Time: O(n)
    Space: O(1)
    """
    left = 0
    right = len(heights) - 1
    best_area = 0

    while left < right:
        width = right - left
        limiting_height = min(heights[left], heights[right])
        best_area = max(best_area, width * limiting_height)

        if heights[left] <= heights[right]:
            left += 1
        else:
            right -= 1

    return best_area


def max_container_area_brute_force(heights: Sequence[int]) -> int:
    """Reference O(n^2) implementation."""
    best_area = 0

    for left in range(len(heights)):
        for right in range(left + 1, len(heights)):
            area = min(heights[left], heights[right]) * (right - left)
            best_area = max(best_area, area)

    return best_area


def demonstrate_container() -> None:
    print_section("6. CONTAINER-STYLE PROBLEM")

    examples = [
        [1, 8, 6, 2, 5, 4, 8, 3, 7],
        [1, 1],
        [5, 4, 3, 2, 1],
        [1, 2, 1],
        [],
    ]

    for heights in examples:
        print(
            f"heights={heights}, "
            f"max_area={max_container_area(heights)}"
        )


# ---------------------------------------------------------------------------
# 6. THREE-SUM FOUNDATIONS
# ---------------------------------------------------------------------------

def three_sum(values: Sequence[int], target: int = 0) -> List[Tuple[int, int, int]]:
    """
    Find all unique value triples whose sum equals target.

    Strategy:
        1. Sort the values.
        2. Fix one value with index i.
        3. Use two pointers for the remaining suffix.
        4. Skip duplicates.

    Time: O(n^2) after sorting.
    Sorting: O(n log n).
    Overall: O(n^2).
    Space: O(n) for the sorted copy.

    The output contains value triples, not original indices.
    """
    numbers = sorted(values)
    result: List[Tuple[int, int, int]] = []

    for i in range(len(numbers) - 2):
        if i > 0 and numbers[i] == numbers[i - 1]:
            continue

        left = i + 1
        right = len(numbers) - 1

        while left < right:
            current_sum = numbers[i] + numbers[left] + numbers[right]

            if current_sum == target:
                result.append((numbers[i], numbers[left], numbers[right]))

                left_value = numbers[left]
                right_value = numbers[right]

                while left < right and numbers[left] == left_value:
                    left += 1

                while left < right and numbers[right] == right_value:
                    right -= 1

            elif current_sum < target:
                left += 1
            else:
                right -= 1

    return result


def demonstrate_three_sum() -> None:
    print_section("7. THREE-SUM FOUNDATIONS")

    examples = [
        ([-1, 0, 1, 2, -1, -4], 0),
        ([0, 0, 0, 0], 0),
        ([1, 2, 3, 4], 100),
        ([-2, 0, 1, 1, 2], 0),
    ]

    for values, target in examples:
        print(
            f"values={values}, target={target}, "
            f"triples={three_sum(values, target)}"
        )

    print(
        """
Three-sum illustrates an important general pattern:

    nested outer loop + two-pointer inner search

A brute-force three-value search is O(n^3). Sorting plus two pointers
reduces this to O(n^2).
"""
    )


# ---------------------------------------------------------------------------
# 7. PARTITION-STYLE PROBLEMS
# ---------------------------------------------------------------------------

def partition_around_value(values: List[int], pivot: int) -> int:
    """
    Partition values so elements less than pivot occur before elements
    greater than or equal to pivot.

    The returned index is the boundary of the first region.

    This is intentionally an unstable partition: relative order is not
    guaranteed.

    Time: O(n)
    Extra space: O(1)
    """
    boundary = 0

    for current in range(len(values)):
        if values[current] < pivot:
            values[boundary], values[current] = (
                values[current],
                values[boundary],
            )
            boundary += 1

    return boundary


def dutch_national_flag(values: List[int]) -> None:
    """
    Sort an array containing only 0, 1, and 2 in O(n) time and O(1) space.

    Three regions are maintained:

        [0, low)       -> zeros
        [low, mid)     -> ones
        [mid, high]    -> unknown
        (high, end)    -> twos

    This is a three-pointer partitioning technique.
    """
    low = 0
    mid = 0
    high = len(values) - 1

    while mid <= high:
        if values[mid] == 0:
            values[low], values[mid] = values[mid], values[low]
            low += 1
            mid += 1

        elif values[mid] == 1:
            mid += 1

        elif values[mid] == 2:
            values[mid], values[high] = values[high], values[mid]
            high -= 1

        else:
            raise ValueError(
                "Dutch National Flag input must contain only 0, 1, and 2."
            )


def demonstrate_partitioning() -> None:
    print_section("8. PARTITION-STYLE PROBLEMS")

    values = [9, 4, 7, 3, 10, 2, 8, 1]
    boundary = partition_around_value(values, 6)

    print("Partitioned:", values)
    print("Boundary:", boundary)
    print("Left region:", values[:boundary])
    print("Right region:", values[boundary:])

    colors = [2, 0, 2, 1, 1, 0, 2, 0]
    dutch_national_flag(colors)
    print("Dutch National Flag:", colors)


# ---------------------------------------------------------------------------
# 8. VARIATIONS AND RELATED TECHNIQUES
# ---------------------------------------------------------------------------

def squares_of_sorted_array(values: Sequence[int]) -> List[int]:
    """
    Given a nondecreasing array, return its squares in nondecreasing order.

    Negative values have large absolute values, so the largest square can
    originate from either end of the input.

    We fill the output from right to left.

    Time: O(n)
    Space: O(n) for the result.
    """
    result = [0] * len(values)
    left = 0
    right = len(values) - 1
    write = len(values) - 1

    while left <= right:
        left_square = values[left] ** 2
        right_square = values[right] ** 2

        if left_square > right_square:
            result[write] = left_square
            left += 1
        else:
            result[write] = right_square
            right -= 1

        write -= 1

    return result


def valid_palindrome_after_one_deletion(text: str) -> bool:
    """
    Return True if text is already a palindrome or can become one after
    deleting at most one character.

    This demonstrates a two-pointer algorithm with a controlled branch.
    """
    def is_range_palindrome(left: int, right: int) -> bool:
        while left < right:
            if text[left] != text[right]:
                return False

            left += 1
            right -= 1

        return True

    left = 0
    right = len(text) - 1

    while left < right:
        if text[left] != text[right]:
            return (
                is_range_palindrome(left + 1, right)
                or is_range_palindrome(left, right - 1)
            )

        left += 1
        right -= 1

    return True


def merge_two_sorted_arrays(
    first: Sequence[int],
    second: Sequence[int],
) -> List[int]:
    """
    Merge two sorted arrays using two read pointers.

    Time: O(n + m)
    Space: O(n + m) for the result.
    """
    i = 0
    j = 0
    merged: List[int] = []

    while i < len(first) and j < len(second):
        if first[i] <= second[j]:
            merged.append(first[i])
            i += 1
        else:
            merged.append(second[j])
            j += 1

    merged.extend(first[i:])
    merged.extend(second[j:])

    return merged


def demonstrate_variations() -> None:
    print_section("9. TWO-POINTER VARIATIONS")

    print(
        "Sorted squares:",
        squares_of_sorted_array([-7, -3, -1, 2, 4, 8]),
    )

    for text in ["aba", "abca", "abc", "", "deeee"]:
        print(
            f"'{text}' -> valid after <= 1 deletion: "
            f"{valid_palindrome_after_one_deletion(text)}"
        )

    print(
        "Merged:",
        merge_two_sorted_arrays([1, 4, 7], [2, 3, 8, 9]),
    )


# ---------------------------------------------------------------------------
# 9. EDGE CASES AND POINTER INVARIANTS
# ---------------------------------------------------------------------------

@dataclass
class PointerState:
    left: int
    right: int
    current_sum: Optional[int] = None


def trace_pair_sum(numbers: Sequence[int], target: int) -> None:
    """
    Print every state of the pair-sum algorithm.

    This is useful for debugging and for understanding pointer movement.
    """
    left = 0
    right = len(numbers) - 1

    print("Pointer trace:")

    while left < right:
        current_sum = numbers[left] + numbers[right]

        state = PointerState(left, right, current_sum)

        print(
            f"left={state.left}, right={state.right}, "
            f"values=({numbers[left]}, {numbers[right]}), "
            f"sum={state.current_sum}"
        )

        if current_sum == target:
            print("Target found.")
            return

        if current_sum < target:
            left += 1
        else:
            right -= 1

    print("No pair found.")


# ---------------------------------------------------------------------------
# 10. INPUT VALIDATION
# ---------------------------------------------------------------------------

def require_sorted(values: Sequence[int]) -> None:
    """Raise ValueError when the input is not nondecreasing."""
    for index in range(1, len(values)):
        if values[index] < values[index - 1]:
            raise ValueError("The sequence must be sorted.")


def safe_pair_sum_sorted(
    values: Sequence[int],
    target: int,
) -> Optional[Tuple[int, int]]:
    """
    Validated version of pair_sum_sorted.

    Validation is useful in production-facing code, although it adds O(n)
    work before the actual O(n) two-pointer scan.
    """
    require_sorted(values)
    return pair_sum_sorted(values, target)


def demonstrate_validation() -> None:
    print_section("10. VALIDATION AND FAILURE CONDITIONS")

    valid = [1, 3, 5, 7, 9]
    invalid = [1, 5, 3, 7]

    print("Valid input:", safe_pair_sum_sorted(valid, 10))

    try:
        safe_pair_sum_sorted(invalid, 8)
    except ValueError as error:
        print("Expected validation error:", error)


# ---------------------------------------------------------------------------
# 11. COMMON MISTAKES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    print_section("11. COMMON TWO-POINTER MISTAKES")

    print(
        """
Mistake 1: Applying sorted-array logic to an unsorted array.
Fix: Sort first or use a method appropriate for unsorted input.

Mistake 2: Using <= incorrectly and allowing left == right when a problem
requires two distinct elements.
Fix: Carefully define the loop condition.

Mistake 3: Forgetting duplicate handling in three-sum.
Fix: Skip duplicate fixed values and duplicate pointer values.

Mistake 4: Moving the wrong pointer in a monotonic problem.
Fix: State the invariant before writing the loop.

Mistake 5: Returning physical array length after in-place compaction.
Fix: Return the logical write-pointer length.

Mistake 6: Reading a value after moving a pointer beyond the valid range.
Fix: Update the loop condition and access order carefully.

Mistake 7: Assuming every two-pointer problem has O(1) total space.
Fix: Sorting may require extra memory depending on the language and
implementation.

Mistake 8: Ignoring integer overflow in fixed-width languages.
Fix: Use a sufficiently wide integer type when sums can exceed int range.
"""
    )


# ---------------------------------------------------------------------------
# 12. COMPLEXITY COMPARISON
# ---------------------------------------------------------------------------

def complexity_comparison() -> None:
    print_section("12. COMPLEXITY COMPARISON")

    comparison = [
        ("Pair sum brute force", "O(n^2)", "O(1)"),
        ("Pair sum sorted pointers", "O(n)", "O(1)"),
        ("Three sum brute force", "O(n^3)", "O(1)"),
        ("Three sum sorted + pointers", "O(n^2)", "O(n)"),
        ("Reverse in place", "O(n)", "O(1)"),
        ("Remove duplicates", "O(n)", "O(1)"),
        ("Container brute force", "O(n^2)", "O(1)"),
        ("Container two pointers", "O(n)", "O(1)"),
        ("Sorted squares", "O(n)", "O(n)"),
    ]

    print(f"{'Technique':35} {'Time':12} {'Extra Space':12}")
    print("-" * 62)

    for name, time_complexity, space_complexity in comparison:
        print(
            f"{name:35} {time_complexity:12} {space_complexity:12}"
        )


# ---------------------------------------------------------------------------
# 13. PROPERTY-STYLE RANDOM TESTING
# ---------------------------------------------------------------------------

def verify_pair_sum_against_brute_force() -> None:
    """
    Generate random sorted arrays and compare the two-pointer algorithm
    with a trusted brute-force reference.

    The exact pair may differ when multiple answers exist, so validation
    checks whether both algorithms agree on the existence of a solution.
    """
    random_generator = random.Random(42)

    for _ in range(500):
        values = sorted(
            random_generator.randint(-20, 20)
            for _ in range(random_generator.randint(0, 15))
        )
        target = random_generator.randint(-30, 30)

        pointer_result = pair_sum_sorted(values, target)
        brute_result = pair_sum_brute_force(values, target)

        assert (pointer_result is not None) == (brute_result is not None)

        if pointer_result is not None:
            left, right = pointer_result
            assert left != right
            assert values[left] + values[right] == target

    print("Random pair-sum verification: passed 500 cases.")


# ---------------------------------------------------------------------------
# 14. UNIT TESTS
# ---------------------------------------------------------------------------

class TestTwoPointerAlgorithms(unittest.TestCase):
    def test_pair_sum(self) -> None:
        self.assertEqual(pair_sum_sorted([1, 2, 4, 7, 11], 9), (1, 3))
        self.assertIsNone(pair_sum_sorted([1, 2, 3], 100))

    def test_reverse(self) -> None:
        values = [1, 2, 3, 4]
        reverse_in_place(values)
        self.assertEqual(values, [4, 3, 2, 1])

    def test_empty_reverse(self) -> None:
        values: List[int] = []
        reverse_in_place(values)
        self.assertEqual(values, [])

    def test_remove_duplicates(self) -> None:
        values = [1, 1, 2, 2, 3]
        length = remove_duplicates_sorted(values)
        self.assertEqual(length, 3)
        self.assertEqual(values[:length], [1, 2, 3])

    def test_container(self) -> None:
        heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]
        self.assertEqual(max_container_area(heights), 49)

    def test_container_matches_brute_force(self) -> None:
        examples = [
            [1, 2, 3],
            [5, 1, 5],
            [1, 8, 6, 2, 5, 4, 8, 3, 7],
        ]

        for values in examples:
            self.assertEqual(
                max_container_area(values),
                max_container_area_brute_force(values),
            )

    def test_three_sum(self) -> None:
        result = three_sum([-1, 0, 1, 2, -1, -4])
        self.assertEqual(
            result,
            [(-1, -1, 2), (-1, 0, 1)],
        )

    def test_three_sum_duplicates(self) -> None:
        self.assertEqual(three_sum([0, 0, 0, 0]), [(0, 0, 0)])

    def test_partition(self) -> None:
        values = [3, 5, 2, 8, 1, 7]
        boundary = partition_around_value(values, 5)

        self.assertTrue(all(value < 5 for value in values[:boundary]))
        self.assertTrue(all(value >= 5 for value in values[boundary:]))

    def test_dutch_national_flag(self) -> None:
        values = [2, 0, 2, 1, 1, 0]
        dutch_national_flag(values)
        self.assertEqual(values, [0, 0, 1, 1, 2, 2])

    def test_sorted_squares(self) -> None:
        self.assertEqual(
            squares_of_sorted_array([-7, -3, -1, 2, 4, 8]),
            [1, 4, 9, 16, 49, 64],
        )

    def test_valid_palindrome_after_one_deletion(self) -> None:
        self.assertTrue(valid_palindrome_after_one_deletion("abca"))
        self.assertTrue(valid_palindrome_after_one_deletion("racecar"))
        self.assertFalse(valid_palindrome_after_one_deletion("abc"))


def run_tests() -> None:
    print_section("13. UNIT TESTS")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTwoPointerAlgorithms)
    runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)


# ---------------------------------------------------------------------------
# 15. PRACTICAL DECISION GUIDE
# ---------------------------------------------------------------------------

def decision_guide() -> None:
    print_section("14. WHEN TO USE TWO POINTERS")

    print(
        """
Consider two pointers when:

- The input is sorted or can be sorted.
- A pair or range is being examined.
- One pointer can be moved safely based on an invariant.
- You need to compare both ends of a sequence.
- You need in-place compaction.
- One pointer reads while another writes.
- A nested search can be reduced by monotonic movement.
- A problem naturally creates a left region and right region.

Typical clues include:

- "sorted array"
- "find two values"
- "closest pair"
- "reverse"
- "palindrome"
- "remove duplicates in place"
- "move elements"
- "partition"
- "maximum area"
- "three sum"

Two pointers are not automatically better.

Sorting may change the required ordering, may cost O(n log n), and may
require extra memory. If the original indices must be preserved, a hash map
or another technique may be more appropriate.

The central question is:

    Can pointer movement permanently eliminate candidates?

If yes, a two-pointer solution may be possible.
"""
    )


# ---------------------------------------------------------------------------
# 16. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    explain_pointer_models()
    demonstrate_pair_sum()
    demonstrate_reverse_and_palindrome()
    demonstrate_remove_duplicates()
    demonstrate_move_zeroes()
    demonstrate_container()
    demonstrate_three_sum()
    demonstrate_partitioning()
    demonstrate_variations()

    print_section("POINTER TRACE")
    trace_pair_sum([1, 3, 4, 6, 8, 10], 14)

    demonstrate_validation()
    demonstrate_common_mistakes()
    complexity_comparison()
    verify_pair_sum_against_brute_force()
    run_tests()
    decision_guide()


if __name__ == "__main__":
    main()
