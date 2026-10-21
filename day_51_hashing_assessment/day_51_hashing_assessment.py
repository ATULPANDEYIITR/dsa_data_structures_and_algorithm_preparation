#!/usr/bin/env python3
"""Hashing assessment: frequency, duplicates, pairs, prefix sums, sets/maps, strings."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


def frequency_counts(values: Iterable[int]) -> dict[int, int]:
    """Count occurrences in expected O(n) time."""
    return dict(Counter(values))


def find_duplicates(values: Iterable[int]) -> list[int]:
    """Return each duplicated value once, in order of its second occurrence."""
    seen: set[int] = set()
    reported: set[int] = set()
    duplicates: list[int] = []

    for value in values:
        if value in seen and value not in reported:
            duplicates.append(value)
            reported.add(value)
        seen.add(value)

    return duplicates


def two_sum(values: list[int], target: int) -> tuple[int, int] | None:
    """Return indices of two distinct elements whose sum equals target."""
    earliest_index: dict[int, int] = {}

    for index, value in enumerate(values):
        complement = target - value
        if complement in earliest_index:
            return earliest_index[complement], index
        earliest_index.setdefault(value, index)

    return None


def count_subarrays_with_sum(values: list[int], target: int) -> int:
    """Count target-sum subarrays, including those containing negative values."""
    prefix_frequency: dict[int, int] = defaultdict(int)
    prefix_frequency[0] = 1
    prefix_sum = 0
    total = 0

    for value in values:
        prefix_sum += value
        total += prefix_frequency[prefix_sum - target]
        prefix_frequency[prefix_sum] += 1

    return total


def longest_consecutive_sequence(values: Iterable[int]) -> int:
    """Find the longest consecutive integer run in expected O(n) time."""
    unique_values = set(values)
    longest = 0

    for value in unique_values:
        if value - 1 not in unique_values:
            length = 1
            while value + length in unique_values:
                length += 1
            longest = max(longest, length)

    return longest


def group_anagrams(words: Iterable[str]) -> list[list[str]]:
    """Group lowercase ASCII words by character-frequency signature."""
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in words:
        if not isinstance(word, str) or not word.isascii() or not word.isalpha():
            raise ValueError(f"Expected nonempty ASCII alphabetic word: {word!r}")
        signature = [0] * 26
        for character in word.lower():
            signature[ord(character) - ord("a")] += 1
        groups[tuple(signature)].append(word)

    return list(groups.values())


def longest_unique_substring(text: str) -> int:
    """Sliding window using the last-seen position of each character."""
    last_seen: dict[str, int] = {}
    left = 0
    longest = 0

    for right, character in enumerate(text):
        if character in last_seen:
            left = max(left, last_seen[character] + 1)
        last_seen[character] = right
        longest = max(longest, right - left + 1)

    return longest


def polynomial_string_hash(text: str, base: int = 257,
                           modulus: int = 1_000_000_007) -> int:
    """Compute a polynomial rolling hash; collisions remain possible."""
    if base < 1 or modulus < 2:
        raise ValueError("base must be positive and modulus must be at least 2")

    result = 0
    for character in text:
        result = (result * base + ord(character)) % modulus
    return result


def group_by_hash_with_verification(strings: Iterable[str]) -> list[list[str]]:
    """Use hashes as buckets, verifying actual strings to handle collisions."""
    buckets: dict[int, list[list[str]]] = defaultdict(list)

    for text in strings:
        hashed = polynomial_string_hash(text)
        matching_group = next(
            (group for group in buckets[hashed] if group[0] == text), None
        )
        if matching_group is None:
            buckets[hashed].append([text])
        else:
            matching_group.append(text)

    return [group for bucket in buckets.values() for group in bucket]


@dataclass(frozen=True)
class AssessmentResult:
    name: str
    passed: bool
    details: str


def run_assessment() -> list[AssessmentResult]:
    """Execute deterministic test cases and report failures clearly."""
    tests = [
        ("frequency", lambda: frequency_counts([1, 2, 2, 3, 1, 2])
         == {1: 2, 2: 3, 3: 1}),
        ("duplicates", lambda: find_duplicates([4, 2, 4, 2, 4, 3])
         == [4, 2]),
        ("two sum with negative values",
         lambda: two_sum([3, -2, 7, 5], 3) == (1, 2)),
        ("two sum with repeated values",
         lambda: two_sum([3, 3], 6) == (0, 1)),
        ("two sum impossible",
         lambda: two_sum([1, 2], 9) is None),
        ("prefix sum with negative values",
         lambda: count_subarrays_with_sum([1, -1, 0], 0) == 3),
        ("prefix sum empty input",
         lambda: count_subarrays_with_sum([], 0) == 0),
        ("consecutive sequence",
         lambda: longest_consecutive_sequence([100, 4, 200, 1, 3, 2]) == 4),
        ("anagrams",
         lambda: sorted(sorted(group) for group in group_anagrams(
             ["eat", "tea", "tan", "ate", "nat", "bat"]
         )) == sorted([["eat", "tea", "ate"], ["tan", "nat"], ["bat"]])),
        ("unique substring",
         lambda: longest_unique_substring("abcabcbb") == 3),
        ("empty string",
         lambda: longest_unique_substring("") == 0),
        ("string hash determinism",
         lambda: polynomial_string_hash("repository")
         == polynomial_string_hash("repository")),
        ("hash buckets verify equality",
         lambda: group_by_hash_with_verification(["cat", "dog", "cat"])
         == [["cat", "cat"], ["dog"]]),
    ]

    results = []
    for name, test in tests:
        try:
            passed = bool(test())
            details = "passed" if passed else "assertion failed"
        except Exception as error:
            passed = False
            details = f"{type(error).__name__}: {error}"
        results.append(AssessmentResult(name, passed, details))

    return results


def main() -> None:
    results = run_assessment()
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} | {result.name}: {result.details}")

    passed_count = sum(result.passed for result in results)
    print(f"\nScore: {passed_count}/{len(results)}")
    if passed_count != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
