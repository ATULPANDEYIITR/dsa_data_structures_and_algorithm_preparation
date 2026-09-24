"""
Day 19 — Array Assessment
==========================

Assessment structure:
    3 Easy
    4 Medium
    1 Difficult

Every problem records:
    Pattern
    Approach
    Time Complexity
    Space Complexity
    Mistake
    Improvement

Problems:
    Easy 1    Find Pivot Index
    Easy 2    Move Zeroes
    Easy 3    Maximum Subarray
    Medium 1  Maximum Sum Subarray of Size K
    Medium 2  Two Sum II — Input Array Is Sorted
    Medium 3  Subarray Sum Equals K
    Medium 4  Product of Array Except Self
    Hard      Trapping Rain Water

The file is deliberately self-contained and uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple
import time


# ============================================================================
# Utility functions
# ============================================================================

def print_section(title: str) -> None:
    """Print a readable section separator."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_subsection(title: str) -> None:
    """Print a smaller heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def validate_integer_array(values: Sequence[int], name: str = "array") -> None:
    """Validate that a sequence contains only integer values."""
    if values is None:
        raise ValueError(f"{name} cannot be None.")

    for value in values:
        if not isinstance(value, int):
            raise TypeError(
                f"{name} must contain integers; received {type(value).__name__}."
            )


def format_array(values: Sequence[int]) -> str:
    """Create a compact representation for console output."""
    return "[" + ", ".join(map(str, values)) + "]"


@dataclass
class ProblemRecord:
    """Stores the required assessment documentation for one problem."""

    name: str
    difficulty: str
    pattern: str
    approach: str
    time_complexity: str
    space_complexity: str
    mistake: str
    improvement: str


# ============================================================================
# EASY 1 — Find Pivot Index
# ============================================================================

def find_pivot_index(nums: Sequence[int]) -> int:
    """
    Return the first index where the sum of elements to the left equals
    the sum of elements to the right.

    Example:
        [1, 7, 3, 6, 5, 6] -> 3

    Pattern:
        Prefix-sum reasoning / running totals.

    Key observation:
        total = left_sum + current + right_sum

        Therefore:
        left_sum == total - left_sum - current

    This avoids calculating a separate sum for every index.
    """
    validate_integer_array(nums)

    total_sum = sum(nums)
    left_sum = 0

    for index, value in enumerate(nums):
        right_sum = total_sum - left_sum - value

        if left_sum == right_sum:
            return index

        left_sum += value

    return -1


def find_pivot_index_bruteforce(nums: Sequence[int]) -> int:
    """
    Educational brute-force implementation.

    At every index, sum both sides independently.
    This is intentionally less efficient so that the optimization is visible.
    """
    validate_integer_array(nums)

    for index in range(len(nums)):
        left_sum = sum(nums[:index])
        right_sum = sum(nums[index + 1:])

        if left_sum == right_sum:
            return index

    return -1


# ============================================================================
# EASY 2 — Move Zeroes
# ============================================================================

def move_zeroes(nums: List[int]) -> List[int]:
    """
    Move all zeroes to the end while preserving the relative order of
    non-zero elements.

    The operation is performed in-place.

    Pattern:
        Two pointers / stable compaction.

    The write pointer represents the next location where a non-zero value
    should be placed.
    """
    validate_integer_array(nums)

    write_index = 0

    for read_index in range(len(nums)):
        if nums[read_index] != 0:
            nums[write_index], nums[read_index] = (
                nums[read_index],
                nums[write_index],
            )
            write_index += 1

    return nums


# ============================================================================
# EASY 3 — Maximum Subarray
# ============================================================================

def maximum_subarray(nums: Sequence[int]) -> Tuple[int, int, int]:
    """
    Return:
        (maximum_sum, start_index, end_index)

    Uses Kadane's algorithm.

    Example:
        [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        -> (6, 3, 6)
        because [4, -1, 2, 1] has sum 6.

    Important edge case:
        An array containing only negative values must return the largest
        negative value rather than zero.
    """
    validate_integer_array(nums)

    if not nums:
        raise ValueError("maximum_subarray requires at least one element.")

    current_sum = nums[0]
    best_sum = nums[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(nums)):
        value = nums[index]

        # Starting a new subarray is better when the previous running
        # contribution would reduce the current value.
        if value > current_sum + value:
            current_sum = value
            current_start = index
        else:
            current_sum += value

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index

    return best_sum, best_start, best_end


# ============================================================================
# MEDIUM 1 — Maximum Sum Subarray of Size K
# ============================================================================

def maximum_sum_subarray_of_size_k(nums: Sequence[int], k: int) -> int:
    """
    Find the maximum sum among all contiguous subarrays of exactly size k.

    Pattern:
        Fixed-size sliding window.

    Example:
        [2, 1, 5, 1, 3, 2], k=3 -> 9
        because [5, 1, 3] has the largest sum.
    """
    validate_integer_array(nums)

    if k <= 0:
        raise ValueError("k must be positive.")

    if k > len(nums):
        raise ValueError("k cannot be larger than the array length.")

    window_sum = sum(nums[:k])
    maximum_sum = window_sum

    for right in range(k, len(nums)):
        left = right - k

        window_sum += nums[right]
        window_sum -= nums[left]

        maximum_sum = max(maximum_sum, window_sum)

    return maximum_sum


def maximum_sum_subarray_of_size_k_bruteforce(
    nums: Sequence[int],
    k: int,
) -> int:
    """O(n*k) comparison implementation for learning purposes."""
    validate_integer_array(nums)

    if k <= 0 or k > len(nums):
        raise ValueError("k must satisfy 1 <= k <= len(nums).")

    maximum_sum = float("-inf")

    for start in range(len(nums) - k + 1):
        current_sum = 0

        for index in range(start, start + k):
            current_sum += nums[index]

        maximum_sum = max(maximum_sum, current_sum)

    return int(maximum_sum)


# ============================================================================
# MEDIUM 2 — Two Sum II
# ============================================================================

def two_sum_sorted(nums: Sequence[int], target: int) -> Tuple[int, int]:
    """
    Return 1-based indices of two values whose sum equals target.

    The input must be sorted in non-decreasing order.

    Pattern:
        Opposite-direction two pointers.

    Why it works:
        If nums[left] + nums[right] is too small, increasing left is the
        only direction that can increase the sum.

        If it is too large, decreasing right is the only direction that
        can decrease the sum.
    """
    validate_integer_array(nums)

    left = 0
    right = len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]

        if current_sum == target:
            return left + 1, right + 1

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return (-1, -1)


def two_sum_sorted_hashing(nums: Sequence[int], target: int) -> Tuple[int, int]:
    """
    Alternative solution using a hash map.

    This works without relying on sorted order but requires extra memory.
    It is included to show a real trade-off between exploiting a constraint
    and using additional storage.
    """
    validate_integer_array(nums)

    seen: Dict[int, int] = {}

    for index, value in enumerate(nums):
        complement = target - value

        if complement in seen:
            return seen[complement] + 1, index + 1

        seen[value] = index

    return (-1, -1)


# ============================================================================
# MEDIUM 3 — Subarray Sum Equals K
# ============================================================================

def subarray_sum_equals_k(nums: Sequence[int], k: int) -> int:
    """
    Count contiguous subarrays whose sum equals k.

    Pattern:
        Prefix sum + frequency hash map.

    If:
        prefix[j] - prefix[i] = k

    then:
        prefix[i] = prefix[j] - k

    Instead of searching for every earlier prefix sum, store how many times
    each prefix sum has occurred.

    This also works when negative numbers are present.
    """
    validate_integer_array(nums)

    prefix_frequency: Dict[int, int] = {0: 1}
    prefix_sum = 0
    count = 0

    for value in nums:
        prefix_sum += value

        required_prefix = prefix_sum - k
        count += prefix_frequency.get(required_prefix, 0)

        prefix_frequency[prefix_sum] = (
            prefix_frequency.get(prefix_sum, 0) + 1
        )

    return count


def subarray_sum_equals_k_bruteforce(nums: Sequence[int], k: int) -> int:
    """O(n^2) educational implementation."""
    validate_integer_array(nums)

    count = 0

    for start in range(len(nums)):
        current_sum = 0

        for end in range(start, len(nums)):
            current_sum += nums[end]

            if current_sum == k:
                count += 1

    return count


# ============================================================================
# MEDIUM 4 — Product of Array Except Self
# ============================================================================

def product_except_self(nums: Sequence[int]) -> List[int]:
    """
    Return an output array where output[i] equals the product of every
    element except nums[i].

    Pattern:
        Prefix products + suffix products.

    The implementation uses the output array itself to avoid a second
    prefix/suffix array.

    Division is deliberately not used because:
        1. Zero values create special cases.
        2. The standard problem expects O(n) time and O(1) auxiliary space.
    """
    validate_integer_array(nums)

    n = len(nums)

    if n == 0:
        return []

    result = [1] * n

    prefix_product = 1

    for index in range(n):
        result[index] = prefix_product
        prefix_product *= nums[index]

    suffix_product = 1

    for index in range(n - 1, -1, -1):
        result[index] *= suffix_product
        suffix_product *= nums[index]

    return result


# ============================================================================
# HARD — Trapping Rain Water
# ============================================================================

def trap_rain_water(height: Sequence[int]) -> int:
    """
    Calculate how much water can be trapped between vertical bars.

    Pattern:
        Two pointers with running left/right maximums.

    For a position:
        trapped water = min(max_left, max_right) - height[position]

    Instead of constructing left_max and right_max arrays, the algorithm
    keeps both boundaries in constant auxiliary space.
    """
    validate_integer_array(height)

    if len(height) < 3:
        return 0

    left = 0
    right = len(height) - 1

    left_max = 0
    right_max = 0

    trapped_water = 0

    while left < right:
        if height[left] <= height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                trapped_water += left_max - height[left]

            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                trapped_water += right_max - height[right]

            right -= 1

    return trapped_water


def trap_rain_water_prefix_arrays(height: Sequence[int]) -> int:
    """
    Reference implementation using prefix maximum arrays.

    This version is easier to reason about but uses O(n) auxiliary space.
    """
    validate_integer_array(height)

    n = len(height)

    if n < 3:
        return 0

    left_max = [0] * n
    right_max = [0] * n

    left_max[0] = height[0]

    for index in range(1, n):
        left_max[index] = max(left_max[index - 1], height[index])

    right_max[n - 1] = height[n - 1]

    for index in range(n - 2, -1, -1):
        right_max[index] = max(right_max[index + 1], height[index])

    water = 0

    for index in range(n):
        water += min(left_max[index], right_max[index]) - height[index]

    return water


# ============================================================================
# Assessment documentation
# ============================================================================

ASSESSMENT: List[ProblemRecord] = [
    ProblemRecord(
        name="Find Pivot Index",
        difficulty="Easy",
        pattern="Prefix-sum reasoning",
        approach=(
            "Calculate the total sum once. Scan from left to right while "
            "maintaining the left sum. At each position, derive the right "
            "sum as total - left - current."
        ),
        time_complexity="O(n)",
        space_complexity="O(1) auxiliary space",
        mistake=(
            "Repeatedly calculating left and right sums for every index, "
            "which creates O(n²) behavior."
        ),
        improvement=(
            "Maintain one running left sum and derive the right sum from "
            "the total."
        ),
    ),
    ProblemRecord(
        name="Move Zeroes",
        difficulty="Easy",
        pattern="Two pointers / stable compaction",
        approach=(
            "Use a read pointer to inspect every element and a write pointer "
            "to place each non-zero value at the next valid position."
        ),
        time_complexity="O(n)",
        space_complexity="O(1) auxiliary space",
        mistake=(
            "Removing zeroes while iterating can change list indices and may "
            "skip elements. Creating a second array also uses unnecessary "
            "memory."
        ),
        improvement=(
            "Compact non-zero values in place and preserve their original "
            "relative order."
        ),
    ),
    ProblemRecord(
        name="Maximum Subarray",
        difficulty="Easy",
        pattern="Kadane's algorithm",
        approach=(
            "Track the best sum ending at the current position. Start a new "
            "subarray when the current value is better than extending the "
            "existing subarray."
        ),
        time_complexity="O(n)",
        space_complexity="O(1)",
        mistake=(
            "Initializing the answer to zero, which incorrectly returns "
            "zero for arrays containing only negative values."
        ),
        improvement=(
            "Initialize current and best sums from the first element and "
            "track indices when the actual subarray is required."
        ),
    ),
    ProblemRecord(
        name="Maximum Sum Subarray of Size K",
        difficulty="Medium",
        pattern="Fixed-size sliding window",
        approach=(
            "Build the first window, then remove the element leaving the "
            "window and add the element entering it."
        ),
        time_complexity="O(n)",
        space_complexity="O(1)",
        mistake=(
            "Recomputing every window sum independently, producing O(n*k) "
            "time."
        ),
        improvement=(
            "Reuse the previous window sum so every element enters and "
            "leaves the running window once."
        ),
    ),
    ProblemRecord(
        name="Two Sum II — Input Array Is Sorted",
        difficulty="Medium",
        pattern="Opposite-direction two pointers",
        approach=(
            "Place one pointer at each end. Move the left pointer when the "
            "sum is too small and the right pointer when the sum is too large."
        ),
        time_complexity="O(n)",
        space_complexity="O(1)",
        mistake=(
            "Ignoring the sorted constraint and using nested loops or a hash "
            "map without recognizing that two pointers are sufficient."
        ),
        improvement=(
            "Exploit the monotonic effect of pointer movement in a sorted "
            "array."
        ),
    ),
    ProblemRecord(
        name="Subarray Sum Equals K",
        difficulty="Medium",
        pattern="Prefix sum + frequency hash map",
        approach=(
            "Store how frequently each prefix sum has appeared. A current "
            "prefix sum p forms a valid subarray whenever p-k was seen before."
        ),
        time_complexity="O(n) expected",
        space_complexity="O(n)",
        mistake=(
            "Using a sliding window even though negative values may exist. "
            "Negative values destroy the monotonic behavior needed by a "
            "standard variable-size sliding window."
        ),
        improvement=(
            "Use prefix sums and frequencies so negative, zero, and positive "
            "values are all handled correctly."
        ),
    ),
    ProblemRecord(
        name="Product of Array Except Self",
        difficulty="Medium",
        pattern="Prefix and suffix products",
        approach=(
            "Store the product of all values before each position in the "
            "result array, then multiply by the product of all values after "
            "each position during a reverse scan."
        ),
        time_complexity="O(n)",
        space_complexity="O(1) auxiliary space, excluding the required output",
        mistake=(
            "Using division without considering zero values, or allocating "
            "separate prefix and suffix arrays unnecessarily."
        ),
        improvement=(
            "Reuse the output array and perform a second reverse pass for "
            "suffix products."
        ),
    ),
    ProblemRecord(
        name="Trapping Rain Water",
        difficulty="Hard",
        pattern="Two pointers + boundary maxima",
        approach=(
            "Maintain left and right boundaries and their maximum heights. "
            "Process the side whose boundary is lower because that side's "
            "maximum determines the amount that can safely be accumulated."
        ),
        time_complexity="O(n)",
        space_complexity="O(1)",
        mistake=(
            "Trying to compute each position independently with a full scan, "
            "leading to O(n²), or moving the wrong pointer without respecting "
            "the lower-boundary invariant."
        ),
        improvement=(
            "Maintain running maxima and process each bar once using the "
            "lower-boundary invariant."
        ),
    ),
]


# ============================================================================
# Testing helpers
# ============================================================================

def assert_equal(actual, expected, description: str) -> None:
    """Raise a useful error when an assessment test fails."""
    if actual != expected:
        raise AssertionError(
            f"FAILED: {description}\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )


def run_unit_tests() -> None:
    """Run deterministic tests covering normal cases and edge cases."""
    print_section("UNIT TESTS")

    # Easy 1
    assert_equal(
        find_pivot_index([1, 7, 3, 6, 5, 6]),
        3,
        "pivot index example",
    )
    assert_equal(
        find_pivot_index([1, 2, 3]),
        -1,
        "pivot index absent",
    )
    assert_equal(
        find_pivot_index([2, 1, -1]),
        0,
        "pivot index with negative values",
    )
    assert_equal(
        find_pivot_index([]),
        -1,
        "empty pivot array",
    )

    # Easy 2
    values = [0, 1, 0, 3, 12]
    assert_equal(
        move_zeroes(values),
        [1, 3, 12, 0, 0],
        "move zeroes",
    )

    values = [0, 0, 0]
    assert_equal(
        move_zeroes(values),
        [0, 0, 0],
        "all zeroes",
    )

    values = [1, 2, 3]
    assert_equal(
        move_zeroes(values),
        [1, 2, 3],
        "no zeroes",
    )

    # Easy 3
    assert_equal(
        maximum_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]),
        (6, 3, 6),
        "maximum subarray",
    )
    assert_equal(
        maximum_subarray([-8, -3, -6, -2, -5, -4]),
        (-2, 3, 3),
        "all-negative maximum subarray",
    )

    # Medium 1
    assert_equal(
        maximum_sum_subarray_of_size_k([2, 1, 5, 1, 3, 2], 3),
        9,
        "fixed-size sliding window",
    )
    assert_equal(
        maximum_sum_subarray_of_size_k([-5, -2, -3], 2),
        -5,
        "negative fixed-size window",
    )

    # Medium 2
    assert_equal(
        two_sum_sorted([2, 7, 11, 15], 9),
        (1, 2),
        "two sum sorted",
    )
    assert_equal(
        two_sum_sorted([1, 2, 3, 4, 4, 9, 56, 90], 8),
        (4, 5),
        "duplicate values in sorted two sum",
    )
    assert_equal(
        two_sum_sorted([1, 2, 3], 100),
        (-1, -1),
        "two sum not found",
    )

    # Medium 3
    assert_equal(
        subarray_sum_equals_k([1, 1, 1], 2),
        2,
        "subarray sum equals k",
    )
    assert_equal(
        subarray_sum_equals_k([1, 2, 3], 3),
        2,
        "subarray sum with overlapping candidates",
    )
    assert_equal(
        subarray_sum_equals_k([1, -1, 0], 0),
        3,
        "subarray sum with negative values",
    )

    # Medium 4
    assert_equal(
        product_except_self([1, 2, 3, 4]),
        [24, 12, 8, 6],
        "product except self",
    )
    assert_equal(
        product_except_self([-1, 1, 0, -3, 3]),
        [0, 0, 9, 0, 0],
        "product except self with zero",
    )

    # Hard
    assert_equal(
        trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]),
        6,
        "trapping rain water",
    )
    assert_equal(
        trap_rain_water([4, 2, 0, 3, 2, 5]),
        9,
        "trapping rain water second example",
    )
    assert_equal(
        trap_rain_water([1, 2, 3, 4]),
        0,
        "monotonically increasing heights",
    )

    print("All unit tests passed.")


# ============================================================================
# Demonstrations
# ============================================================================

def demonstrate_easy_problems() -> None:
    """Demonstrate the three easy assessment problems."""
    print_section("EASY PROBLEMS")

    print_subsection("Easy 1 — Find Pivot Index")
    array = [1, 7, 3, 6, 5, 6]
    print(f"Input:  {format_array(array)}")
    print(f"Output: {find_pivot_index(array)}")

    print("\nBrute-force comparison:")
    print(f"Output: {find_pivot_index_bruteforce(array)}")

    print_subsection("Easy 2 — Move Zeroes")
    array = [0, 1, 0, 3, 12]
    print(f"Input:  {format_array(array)}")
    print(f"Output: {format_array(move_zeroes(array))}")
    print("The same list object is modified in place.")

    print_subsection("Easy 3 — Maximum Subarray")
    array = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    result = maximum_subarray(array)
    start = result[1]
    end = result[2]
    print(f"Input:  {format_array(array)}")
    print(f"Maximum sum: {result[0]}")
    print(f"Subarray indices: {start} through {end}")
    print(f"Subarray: {format_array(array[start:end + 1])}")

    negative_array = [-8, -3, -6, -2, -5]
    negative_result = maximum_subarray(negative_array)
    print("\nAll-negative edge case:")
    print(f"Input:  {format_array(negative_array)}")
    print(f"Output: {negative_result}")


def demonstrate_medium_problems() -> None:
    """Demonstrate the four medium assessment problems."""
    print_section("MEDIUM PROBLEMS")

    print_subsection("Medium 1 — Maximum Sum Subarray of Size K")
    array = [2, 1, 5, 1, 3, 2]
    k = 3
    print(f"Input: {format_array(array)}, k={k}")
    print(f"Output: {maximum_sum_subarray_of_size_k(array, k)}")
    print(
        "Brute-force result:",
        maximum_sum_subarray_of_size_k_bruteforce(array, k),
    )

    print_subsection("Medium 2 — Two Sum II")
    array = [2, 7, 11, 15]
    target = 9
    print(f"Input: {format_array(array)}, target={target}")
    print(f"Two-pointer output: {two_sum_sorted(array, target)}")
    print(f"Hash-map output:     {two_sum_sorted_hashing(array, target)}")

    print_subsection("Medium 3 — Subarray Sum Equals K")
    array = [1, 2, 1, 2, 1]
    target = 3
    print(f"Input: {format_array(array)}, k={target}")
    print(f"Optimized output:  {subarray_sum_equals_k(array, target)}")
    print(
        "Brute-force output:",
        subarray_sum_equals_k_bruteforce(array, target),
    )

    print_subsection("Medium 4 — Product of Array Except Self")
    array = [1, 2, 3, 4]
    print(f"Input:  {format_array(array)}")
    print(f"Output: {format_array(product_except_self(array))}")


def demonstrate_hard_problem() -> None:
    """Demonstrate the difficult assessment problem."""
    print_section("DIFFICULT PROBLEM")

    print_subsection("Hard — Trapping Rain Water")

    heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

    print(f"Input:  {format_array(heights)}")
    print(f"Water:  {trap_rain_water(heights)}")

    print("\nReference implementation using prefix arrays:")
    print(f"Water:  {trap_rain_water_prefix_arrays(heights)}")

    print(
        "\nThe prefix-array implementation uses O(n) extra space, "
        "while the two-pointer implementation uses O(1) auxiliary space."
    )


# ============================================================================
# Complexity demonstrations
# ============================================================================

def benchmark_function(
    function: Callable,
    *args,
    repetitions: int = 5,
) -> float:
    """
    Measure average execution time.

    Benchmarking is approximate and affected by hardware, interpreter state,
    operating-system scheduling, and input characteristics.
    """
    durations = []

    for _ in range(repetitions):
        start = time.perf_counter()
        function(*args)
        durations.append(time.perf_counter() - start)

    return sum(durations) / len(durations)


def demonstrate_performance() -> None:
    """Compare selected brute-force and optimized approaches."""
    print_section("PERFORMANCE COMPARISON")

    data = list(range(1, 2001))
    k = 100

    brute_time = benchmark_function(
        maximum_sum_subarray_of_size_k_bruteforce,
        data,
        k,
        repetitions=3,
    )

    optimized_time = benchmark_function(
        maximum_sum_subarray_of_size_k,
        data,
        k,
        repetitions=3,
    )

    print("Maximum Sum Subarray of Size K")
    print(f"Input size: {len(data)}")
    print(f"k: {k}")
    print(f"Brute-force average: {brute_time:.6f} seconds")
    print(f"Sliding-window average: {optimized_time:.6f} seconds")

    print(
        "\nThe important algorithmic distinction is O(n*k) versus O(n), "
        "not the exact timing on one computer."
    )


# ============================================================================
# Mistake demonstrations
# ============================================================================

def demonstrate_common_mistakes() -> None:
    """Show typical incorrect reasoning and the corresponding correction."""
    print_section("COMMON MISTAKES")

    print(
        "1. Pivot Index:\n"
        "   Mistake: calculate two sums from scratch at every index.\n"
        "   Improvement: total sum + running left sum."
    )

    print(
        "\n2. Move Zeroes:\n"
        "   Mistake: remove elements while traversing the same list.\n"
        "   Improvement: use a write pointer for stable in-place compaction."
    )

    print(
        "\n3. Maximum Subarray:\n"
        "   Mistake: initialize best sum to 0.\n"
        "   Improvement: initialize from nums[0] so all-negative arrays work."
    )

    print(
        "\n4. Fixed Sliding Window:\n"
        "   Mistake: recalculate each window from scratch.\n"
        "   Improvement: subtract the outgoing value and add the incoming value."
    )

    print(
        "\n5. Two Sum on Sorted Array:\n"
        "   Mistake: ignore the sorted property.\n"
        "   Improvement: use the ordering to eliminate impossible pairs."
    )

    print(
        "\n6. Subarray Sum Equals K:\n"
        "   Mistake: use a sliding window with arbitrary negative numbers.\n"
        "   Improvement: prefix sums + frequency map."
    )

    print(
        "\n7. Product Except Self:\n"
        "   Mistake: use division and forget the zero case.\n"
        "   Improvement: prefix and suffix products."
    )

    print(
        "\n8. Trapping Rain Water:\n"
        "   Mistake: independently scan left and right for every position.\n"
        "   Improvement: two pointers with running boundary maxima."
    )


# ============================================================================
# Assessment report
# ============================================================================

def print_assessment_report() -> None:
    """Print the requested documentation for all eight problems."""
    print_section("ASSESSMENT DOCUMENTATION")

    for number, problem in enumerate(ASSESSMENT, start=1):
        print(f"\n{number}. {problem.name} [{problem.difficulty}]")
        print(f"Pattern: {problem.pattern}")
        print(f"Approach: {problem.approach}")
        print(f"Time Complexity: {problem.time_complexity}")
        print(f"Space Complexity: {problem.space_complexity}")
        print(f"Mistake: {problem.mistake}")
        print(f"Improvement: {problem.improvement}")


# ============================================================================
# Additional array reasoning examples
# ============================================================================

def demonstrate_edge_cases() -> None:
    """Demonstrate boundaries that frequently cause assessment failures."""
    print_section("EDGE CASES")

    edge_cases = [
        ("Empty array", []),
        ("Single element", [7]),
        ("All zeroes", [0, 0, 0]),
        ("All negative", [-5, -2, -9]),
        ("Mixed signs", [-3, 4, -1, 2, -6, 5]),
        ("Already sorted", [1, 2, 3, 4, 5]),
        ("Reverse sorted", [5, 4, 3, 2, 1]),
        ("Duplicate values", [2, 2, 2, 2]),
    ]

    for description, values in edge_cases:
        print(f"{description:20} {format_array(values)}")

    print(
        "\nAssessment habit: always test empty input where permitted, "
        "single-element input, duplicate values, zero values, negative "
        "values, monotonic input, and cases where no answer exists."
    )


# ============================================================================
# Main program
# ============================================================================

def main() -> None:
    """Run the complete Day 19 array assessment lesson."""
    print_section("DAY 19 — ARRAY ASSESSMENT")
    print("3 Easy + 4 Medium + 1 Difficult")
    print("Focus: prefix sums, two pointers, sliding windows, Kadane, hashing")

    demonstrate_easy_problems()
    demonstrate_medium_problems()
    demonstrate_hard_problem()
    demonstrate_edge_cases()
    demonstrate_common_mistakes()
    print_assessment_report()
    run_unit_tests()
    demonstrate_performance()

    print_section("ASSESSMENT COMPLETE")
    print("Eight array problems were implemented, tested, compared, and documented.")


if __name__ == "__main__":
    main()
