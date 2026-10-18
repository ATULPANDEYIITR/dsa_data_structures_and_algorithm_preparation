"""
Two-sum pattern: complement lookup, pair counting, and difference-based lookup.

Run with:
    python two_sum_patterns.py

The implementations use only the Python standard library.
"""

from collections import Counter, defaultdict
from itertools import combinations
from typing import Iterable, Optional, Sequence


def two_sum(nums: Sequence[int], target: int) -> Optional[tuple[int, int]]:
    """
    Return indices of two distinct elements whose sum equals target.

    Each value is stored only after its complement has been checked.
    This guarantees that an element cannot be paired with itself.
    Expected time: O(n). Auxiliary space: O(n).
    """
    seen: dict[int, int] = {}

    for index, value in enumerate(nums):
        complement = target - value

        if complement in seen:
            return seen[complement], index

        # Preserve the earliest index for each value.
        if value not in seen:
            seen[value] = index

    return None


def two_sum_all_index_pairs(
    nums: Sequence[int], target: int
) -> list[tuple[int, int]]:
    """
    Return every index pair i < j satisfying nums[i] + nums[j] == target.

    The value-to-indices map handles duplicates without reusing an index.
    Output-sensitive complexity: O(n + k), where k is the pair count.
    """
    previous_indices: dict[int, list[int]] = defaultdict(list)
    pairs: list[tuple[int, int]] = []

    for right, value in enumerate(nums):
        complement = target - value

        for left in previous_indices.get(complement, []):
            pairs.append((left, right))

        previous_indices[value].append(right)

    return pairs


def count_pairs(nums: Sequence[int], target: int) -> int:
    """
    Count index pairs i < j whose values sum to target.

    Duplicate values at different indices count as separate pairs.
    Expected time: O(n). Auxiliary space: O(u), where u is the
    number of distinct values.
    """
    frequencies: Counter[int] = Counter()
    total = 0

    for value in nums:
        total += frequencies[target - value]
        frequencies[value] += 1

    return total


def count_pairs_by_frequency(nums: Sequence[int], target: int) -> int:
    """
    Count pairs using a frequency formula.

    For distinct values a and b, count is freq[a] * freq[b].
    For a == b, count is freq[a] * (freq[a] - 1) // 2.
    """
    frequencies = Counter(nums)
    total = 0

    for value, frequency in frequencies.items():
        complement = target - value

        if complement not in frequencies:
            continue

        if value < complement:
            total += frequency * frequencies[complement]
        elif value == complement:
            total += frequency * (frequency - 1) // 2

    return total


def find_pair_with_difference(
    nums: Sequence[int], difference: int
) -> Optional[tuple[int, int]]:
    """
    Return indices (i, j) such that nums[j] - nums[i] == difference.

    The difference is signed. For difference == 0, two distinct
    indices containing the same value are required.
    Expected time: O(n). Auxiliary space: O(n).
    """
    if not isinstance(difference, int) or isinstance(difference, bool):
        raise TypeError("difference must be an integer")

    seen: dict[int, int] = {}

    for right, value in enumerate(nums):
        required_left = value - difference

        if required_left in seen:
            return seen[required_left], right

        if value not in seen:
            seen[value] = right

    return None


def find_pair_with_absolute_difference(
    nums: Sequence[int], difference: int
) -> Optional[tuple[int, int]]:
    """
    Find a pair with abs(nums[j] - nums[i]) == difference.

    For nonzero differences, check both directional complements.
    For zero, require two occurrences at different indices.
    """
    if not isinstance(difference, int) or isinstance(difference, bool):
        raise TypeError("difference must be an integer")

    if difference < 0:
        raise ValueError("absolute difference cannot be negative")

    seen: dict[int, int] = {}

    for right, value in enumerate(nums):
        candidates = (
            (value,)
            if difference == 0
            else (value - difference, value + difference)
        )

        for candidate in candidates:
            if candidate in seen:
                return seen[candidate], right

        if value not in seen:
            seen[value] = right

    return None


def two_sum_sorted(nums: Sequence[int], target: int) -> Optional[tuple[int, int]]:
    """
    Two-pointer solution for an already sorted sequence.

    Returns original indices in the sorted sequence, not in an
    unsorted source array. Expected time O(n), auxiliary space O(1).
    """
    left, right = 0, len(nums) - 1

    while left < right:
        current = nums[left] + nums[right]

        if current == target:
            return left, right
        if current < target:
            left += 1
        else:
            right -= 1

    return None


def two_sum_unique_value_pairs(
    nums: Sequence[int], target: int
) -> list[tuple[int, int]]:
    """
    Return distinct value pairs, not index pairs.

    A pair (a, b) is represented in ascending order, and repeated
    occurrences do not produce duplicate value pairs.
    """
    frequencies = Counter(nums)
    result: list[tuple[int, int]] = []

    for value in sorted(frequencies):
        complement = target - value

        if complement < value or complement not in frequencies:
            continue

        if complement == value and frequencies[value] < 2:
            continue

        result.append((value, complement))

    return result


def brute_force_two_sum(
    nums: Sequence[int], target: int
) -> Optional[tuple[int, int]]:
    """Reference implementation used to verify optimized behavior."""
    for left, right in combinations(range(len(nums)), 2):
        if nums[left] + nums[right] == target:
            return left, right

    return None


def validate_two_sum(
    nums: Sequence[int], target: int, result: Optional[tuple[int, int]]
) -> bool:
    """Check index validity, distinctness, and the requested sum."""
    if result is None:
        return True

    left, right = result

    return (
        0 <= left < len(nums)
        and 0 <= right < len(nums)
        and left != right
        and nums[left] + nums[right] == target
    )


def run_tests() -> None:
    """Exercise duplicates, negative numbers, boundaries, and failures."""
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([3], 6) is None
    assert two_sum([], 0) is None
    assert two_sum([-4, 9, 1, 3], 5) == (0, 3)
    assert two_sum([1, 2, 3], 20) is None

    nums = [1, 5, 1, 5]
    assert two_sum_all_index_pairs(nums, 6) == [
        (0, 1), (0, 3), (1, 2), (2, 3)
    ]
    assert count_pairs(nums, 6) == 4
    assert count_pairs_by_frequency(nums, 6) == 4

    assert count_pairs([2, 2, 2, 2], 4) == 6
    assert count_pairs_by_frequency([2, 2, 2, 2], 4) == 6
    assert count_pairs([-2, -1, 0, 1, 2], 0) == 2

    assert find_pair_with_difference([4, 1, 8, 3], 2) == (3, 2)
    assert find_pair_with_difference([7, 7], 0) == (0, 1)
    assert find_pair_with_difference([2, 4], -2) == (1, 0)
    assert find_pair_with_difference([1, 4], 8) is None

    assert find_pair_with_absolute_difference([1, 8, 3, 10], 2) == (0, 2)
    assert find_pair_with_absolute_difference([5, 5], 0) == (0, 1)
    assert find_pair_with_absolute_difference([5], 0) is None

    assert two_sum_sorted([-5, -1, 2, 7], 1) == (0, 3)
    assert two_sum_sorted([1, 2, 3], 20) is None
    assert two_sum_unique_value_pairs([1, 1, 2, 2, 3], 4) == [
        (1, 3), (2, 2)
    ]

    try:
        find_pair_with_absolute_difference([1, 2], -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative absolute difference must be rejected")

    # Differential testing compares optimized results with a brute-force
    # reference across many small arrays, including duplicate values.
    test_arrays: Iterable[list[int]] = (
        [],
        [0],
        [1, 1],
        [-2, 0, 2],
        [3, -1, 3, 0, -1],
    )

    for values in test_arrays:
        for target in range(-5, 6):
            optimized = two_sum(values, target)
            reference = brute_force_two_sum(values, target)

            assert validate_two_sum(values, target, optimized)
            assert (optimized is None) == (reference is None)

    print("All Two-sum pattern tests passed.")


def main() -> None:
    """Run focused examples and the test suite."""
    print("Two Sum")
    values = [12, 7, 19, 4, 7]
    target = 11
    pair = two_sum(values, target)
    print(f"Values: {values}, target: {target}, indices: {pair}")

    if pair is not None:
        left, right = pair
        print(f"Matched values: {values[left]} + {values[right]}")

    print("\nPair counting")
    transactions = [100, 50, 100, 150, 50]
    print("Pairs totaling 200:", count_pairs(transactions, 200))
    print("Unique value pairs:", two_sum_unique_value_pairs(transactions, 200))

    print("\nDifference-based lookup")
    measurements = [18, 23, 15, 30, 23]
    print("Signed difference of 7:", find_pair_with_difference(measurements, 7))
    print(
        "Absolute difference of 8:",
        find_pair_with_absolute_difference(measurements, 8),
    )

    print("\nSorted-array lookup")
    ordered = [-10, -3, 2, 6, 14]
    print("Indices for target 11:", two_sum_sorted(ordered, 11))

    run_tests()


if __name__ == "__main__":
    main()
