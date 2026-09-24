"""
Day 22 — Palindromes
Comprehensive study script covering character, two-pointer, number, substring,
valid-palindrome, remove-one-character, and longest-palindrome concepts.

The script is intentionally self-contained and uses only the Python standard library.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import random
import string
import time
from typing import Callable, Iterable, Optional


# ============================================================
# 1. FUNDAMENTALS
# ============================================================

def is_character_palindrome(text: str) -> bool:
    """Return True when text reads identically from both directions."""
    return text == text[::-1]


def is_character_palindrome_loop(text: str) -> bool:
    """Beginner implementation using explicit character comparisons."""
    left = 0
    right = len(text) - 1

    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1

    return True


def is_two_pointer_palindrome(text: str) -> bool:
    """
    Check a string with two pointers.

    The pointers begin at opposite ends and move toward the center.
    This avoids constructing a reversed copy.
    """
    left = 0
    right = len(text) - 1

    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1

    return True


def is_valid_palindrome(text: str) -> bool:
    """
    Ignore non-alphanumeric characters and compare case-insensitively.

    Examples:
        "A man, a plan, a canal: Panama" -> True
        "race a car" -> False
    """
    left = 0
    right = len(text) - 1

    while left < right:
        while left < right and not text[left].isalnum():
            left += 1

        while left < right and not text[right].isalnum():
            right -= 1

        if text[left].casefold() != text[right].casefold():
            return False

        left += 1
        right -= 1

    return True


def normalize_for_palindrome(text: str) -> str:
    """Create the canonical representation used by valid-palindrome checks."""
    return "".join(character.casefold() for character in text if character.isalnum())


def is_valid_palindrome_by_normalization(text: str) -> bool:
    """Alternative implementation that explicitly creates normalized text."""
    normalized = normalize_for_palindrome(text)
    return normalized == normalized[::-1]


# ============================================================
# 2. NUMBER PALINDROMES
# ============================================================

def is_number_palindrome_string(number: int) -> bool:
    """
    Beginner-friendly integer palindrome test.

    Negative numbers are considered non-palindromic because '-' appears
    only on the left side.
    """
    value = str(number)
    return value == value[::-1]


def is_number_palindrome_math(number: int) -> bool:
    """
    Integer palindrome test without converting the number to a string.

    Only the latter half of the digits is reversed, preventing unnecessary
    work and avoiding overflow in fixed-width implementations.
    """
    if number < 0:
        return False

    if number != 0 and number % 10 == 0:
        return False

    reversed_half = 0

    while number > reversed_half:
        reversed_half = reversed_half * 10 + number % 10
        number //= 10

    return number == reversed_half or number == reversed_half // 10


def digit_count(number: int) -> int:
    """Return the number of decimal digits in a non-negative integer."""
    if number == 0:
        return 1

    return len(str(abs(number)))


# ============================================================
# 3. BASIC PRACTICE: REMOVE ONE CHARACTER
# ============================================================

def can_be_palindrome_after_removing_one(text: str) -> bool:
    """
    Return True if the string is already a palindrome or can become one
    after removing at most one character.

    Once a mismatch is found, only two possibilities need checking:
        1. remove the left mismatching character
        2. remove the right mismatching character

    Time: O(n)
    Extra space: O(1)
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


# ============================================================
# 4. SUBSTRING PALINDROMES
# ============================================================

def is_substring_palindrome(text: str, start: int, end: int) -> bool:
    """
    Check whether text[start:end] is a palindrome.

    The end index is exclusive, matching Python slicing conventions.
    """
    if start < 0 or end > len(text) or start > end:
        raise ValueError("Invalid substring boundaries")

    left = start
    right = end - 1

    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1

    return True


def brute_force_palindromic_substrings(text: str) -> list[str]:
    """
    Return all palindromic substrings using enumeration.

    Complexity:
        O(n^3) in the worst case when substring creation and palindrome
        checking are both counted.
    """
    result: list[str] = []

    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            candidate = text[start:end]
            if is_character_palindrome(candidate):
                result.append(candidate)

    return result


def brute_force_palindromic_substring_positions(
    text: str,
) -> list[tuple[int, int, str]]:
    """Return start, end-exclusive, and value for every palindromic substring."""
    result = []

    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            if is_substring_palindrome(text, start, end):
                result.append((start, end, text[start:end]))

    return result


def expand_around_center(
    text: str,
    left: int,
    right: int,
) -> tuple[int, int]:
    """
    Expand while characters match.

    Returns a half-open interval [start, end) for the palindrome.
    """
    while left >= 0 and right < len(text) and text[left] == text[right]:
        left -= 1
        right += 1

    return left + 1, right


def longest_palindromic_substring_center(text: str) -> str:
    """
    Find the longest palindromic substring by expanding around every center.

    There are two center types:
        - one character for odd-length palindromes
        - the gap between two characters for even-length palindromes

    Time: O(n^2)
    Extra space: O(1), excluding the returned substring.
    """
    if not text:
        return ""

    best_start = 0
    best_end = 1

    for center in range(len(text)):
        start, end = expand_around_center(text, center, center)
        if end - start > best_end - best_start:
            best_start, best_end = start, end

        start, end = expand_around_center(text, center, center + 1)
        if end - start > best_end - best_start:
            best_start, best_end = start, end

    return text[best_start:best_end]


def longest_palindromic_substring_dp(text: str) -> str:
    """
    Dynamic-programming solution.

    dp[left][right] is True when text[left:right+1] is a palindrome.

    Recurrence:
        text[left] == text[right] and
        (length <= 2 or dp[left+1][right-1])

    Time: O(n^2)
    Space: O(n^2)
    """
    n = len(text)

    if n == 0:
        return ""

    dp = [[False] * n for _ in range(n)]
    best_start = 0
    best_length = 1

    for index in range(n):
        dp[index][index] = True

    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1

            if text[left] == text[right] and (
                length == 2 or dp[left + 1][right - 1]
            ):
                dp[left][right] = True

                if length > best_length:
                    best_start = left
                    best_length = length

    return text[best_start:best_start + best_length]


def all_palindromic_substrings_center(text: str) -> list[str]:
    """Return every palindromic substring, including duplicates by position."""
    result: list[str] = []

    for center in range(len(text)):
        left = center
        right = center

        while left >= 0 and right < len(text) and text[left] == text[right]:
            result.append(text[left:right + 1])
            left -= 1
            right += 1

        left = center
        right = center + 1

        while left >= 0 and right < len(text) and text[left] == text[right]:
            result.append(text[left:right + 1])
            left -= 1
            right += 1

    return result


# ============================================================
# 5. DISTINCT PALINDROMIC SUBSTRINGS
# ============================================================

def distinct_palindromic_substrings(text: str) -> set[str]:
    """
    Return distinct palindromic substring values.

    A set removes duplicates caused by repeated occurrences.
    """
    return set(all_palindromic_substrings_center(text))


# ============================================================
# 6. PALINDROME PERMUTATION CONCEPT
# ============================================================

def can_rearrange_into_palindrome(text: str) -> bool:
    """
    A string can be rearranged into a palindrome when at most one character
    has an odd frequency.

    This is a frequency property, not a test of the current character order.
    """
    odd_frequency_count = sum(
        count % 2 for count in Counter(text).values()
    )
    return odd_frequency_count <= 1


# ============================================================
# 7. LONGEST PALINDROMIC SUBSEQUENCE
# ============================================================

def longest_palindromic_subsequence_length(text: str) -> int:
    """
    Compute the length of the longest palindromic subsequence.

    A subsequence may skip characters. This differs fundamentally from a
    substring, which must occupy one contiguous interval.

    Recurrence:
        if text[i] == text[j]:
            dp[i][j] = dp[i+1][j-1] + 2
        else:
            dp[i][j] = max(dp[i+1][j], dp[i][j-1])

    Time: O(n^2)
    Space: O(n^2)
    """
    n = len(text)

    if n == 0:
        return 0

    dp = [[0] * n for _ in range(n)]

    for index in range(n):
        dp[index][index] = 1

    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1

            if text[left] == text[right]:
                if length == 2:
                    dp[left][right] = 2
                else:
                    dp[left][right] = dp[left + 1][right - 1] + 2
            else:
                dp[left][right] = max(
                    dp[left + 1][right],
                    dp[left][right - 1],
                )

    return dp[0][n - 1]


# ============================================================
# 8. MANACHER'S ALGORITHM
# ============================================================

def longest_palindromic_substring_manacher(text: str) -> str:
    """
    Find the longest palindromic substring in O(n) time using Manacher's
    algorithm.

    The transformed string places separators between characters so that
    odd- and even-length palindromes can be treated uniformly.

    Example:
        "abba" -> "^#a#b#b#a#$"

    p[i] stores the palindrome radius around transformed position i.
    """
    if not text:
        return ""

    transformed = "^#" + "#".join(text) + "#$"
    radius = [0] * len(transformed)

    center = 0
    right_boundary = 0

    for index in range(1, len(transformed) - 1):
        mirror = 2 * center - index

        if index < right_boundary:
            radius[index] = min(
                right_boundary - index,
                radius[mirror],
            )

        while (
            transformed[index + 1 + radius[index]]
            == transformed[index - 1 - radius[index]]
        ):
            radius[index] += 1

        if index + radius[index] > right_boundary:
            center = index
            right_boundary = index + radius[index]

    best_center = max(range(len(radius)), key=radius.__getitem__)
    best_radius = radius[best_center]

    start = (best_center - best_radius) // 2
    return text[start:start + best_radius]


# ============================================================
# 9. PALINDROME PARTITIONING
# ============================================================

def palindrome_partitioning(text: str) -> list[list[str]]:
    """
    Generate every partition in which every component is a palindrome.

    This is a backtracking problem. The number of valid partitions can be
    exponential, so exponential output is unavoidable for some inputs.
    """
    result: list[list[str]] = []
    current: list[str] = []

    def backtrack(start: int) -> None:
        if start == len(text):
            result.append(current.copy())
            return

        for end in range(start + 1, len(text) + 1):
            candidate = text[start:end]

            if is_character_palindrome(candidate):
                current.append(candidate)
                backtrack(end)
                current.pop()

    backtrack(0)
    return result


# ============================================================
# 10. VALIDATION AND TESTING
# ============================================================

@dataclass
class TestCase:
    name: str
    actual: object
    expected: object


def run_tests() -> None:
    """Run deterministic correctness tests for the major algorithms."""
    tests = [
        TestCase("empty character palindrome", is_character_palindrome(""), True),
        TestCase("single character", is_character_palindrome("a"), True),
        TestCase("racecar", is_character_palindrome("racecar"), True),
        TestCase("python", is_character_palindrome("python"), False),
        TestCase(
            "valid punctuation",
            is_valid_palindrome("A man, a plan, a canal: Panama"),
            True,
        ),
        TestCase(
            "invalid normalized text",
            is_valid_palindrome("race a car"),
            False,
        ),
        TestCase(
            "number 121",
            is_number_palindrome_math(121),
            True,
        ),
        TestCase(
            "number 123",
            is_number_palindrome_math(123),
            False,
        ),
        TestCase(
            "negative number",
            is_number_palindrome_math(-121),
            False,
        ),
        TestCase(
            "trailing zero",
            is_number_palindrome_math(10),
            False,
        ),
        TestCase(
            "remove one character",
            can_be_palindrome_after_removing_one("abca"),
            True,
        ),
        TestCase(
            "cannot remove one",
            can_be_palindrome_after_removing_one("abc"),
            False,
        ),
        TestCase(
            "already palindrome with removal allowed",
            can_be_palindrome_after_removing_one("racecar"),
            True,
        ),
        TestCase(
            "longest center",
            longest_palindromic_substring_center("babad") in {"bab", "aba"},
            True,
        ),
        TestCase(
            "longest DP",
            longest_palindromic_substring_dp("cbbd"),
            "bb",
        ),
        TestCase(
            "Manacher",
            longest_palindromic_substring_manacher("cbbd"),
            "bb",
        ),
        TestCase(
            "permutation palindrome",
            can_rearrange_into_palindrome("carrace"),
            True,
        ),
        TestCase(
            "permutation impossible",
            can_rearrange_into_palindrome("daily"),
            False,
        ),
        TestCase(
            "subsequence length",
            longest_palindromic_subsequence_length("bbbab"),
            4,
        ),
    ]

    failures = []

    for test in tests:
        if test.actual != test.expected:
            failures.append(test)

    if failures:
        for failure in failures:
            print(
                f"FAILED: {failure.name}: "
                f"expected {failure.expected!r}, got {failure.actual!r}"
            )
        raise AssertionError(f"{len(failures)} test(s) failed")

    print(f"All {len(tests)} tests passed.")


# ============================================================
# 11. COMPLEXITY COMPARISON
# ============================================================

def benchmark_longest_palindrome() -> None:
    """Compare practical runtimes of several longest-palindrome algorithms."""
    sample = ("abacabadabacaba" * 8)

    algorithms: list[tuple[str, Callable[[str], str]]] = [
        ("center expansion", longest_palindromic_substring_center),
        ("dynamic programming", longest_palindromic_substring_dp),
        ("Manacher", longest_palindromic_substring_manacher),
    ]

    print("\nLongest-palindrome benchmark:")
    print(f"Input length: {len(sample)}")

    for name, algorithm in algorithms:
        start_time = time.perf_counter()
        result = algorithm(sample)
        elapsed = time.perf_counter() - start_time

        print(
            f"{name:22s} "
            f"{elapsed * 1000:10.4f} ms "
            f"length={len(result)}"
        )


# ============================================================
# 12. EDGE CASE EXAMPLES
# ============================================================

def demonstrate_edge_cases() -> None:
    """Display important boundary cases and unusual inputs."""
    examples = [
        "",
        "a",
        "aa",
        "ab",
        "abba",
        "abcba",
        "abcd",
        "A",
        "Aa",
        "12321",
        "10",
        "😊",
        "😊a😊",
    ]

    print("\nCharacter palindrome edge cases:")

    for value in examples:
        print(
            f"{value!r:12} "
            f"exact={is_character_palindrome(value)!s:5} "
            f"valid={is_valid_palindrome(value)!s:5}"
        )

    print("\nNumber palindrome edge cases:")

    numbers = [
        0,
        1,
        9,
        10,
        11,
        100,
        101,
        121,
        1221,
        -121,
        12321,
        123456,
    ]

    for number in numbers:
        print(
            f"{number:8d} -> "
            f"string={is_number_palindrome_string(number)}, "
            f"math={is_number_palindrome_math(number)}"
        )


# ============================================================
# 13. SUBSTRING VS SUBSEQUENCE
# ============================================================

def demonstrate_substring_vs_subsequence() -> None:
    """Show the difference between contiguous substrings and subsequences."""
    text = "bbbab"

    substrings = distinct_palindromic_substrings(text)
    subsequence_length = longest_palindromic_subsequence_length(text)

    print("\nSubstring versus subsequence:")
    print(f"Text: {text}")
    print(f"Distinct palindromic substrings: {sorted(substrings)}")
    print(f"Longest palindromic subsequence length: {subsequence_length}")

    print(
        "\nA substring occupies a contiguous interval; "
        "a subsequence may skip characters."
    )


# ============================================================
# 14. PALINDROME PARTITIONING EXAMPLE
# ============================================================

def demonstrate_partitioning() -> None:
    """Display all palindrome-only partitions for a small input."""
    text = "aab"
    partitions = palindrome_partitioning(text)

    print(f"\nPalindrome partitions of {text!r}:")

    for partition in partitions:
        print(" | ".join(partition))


# ============================================================
# 15. RANDOMIZED CROSS-CHECKING
# ============================================================

def randomized_cross_check(iterations: int = 250) -> None:
    """
    Compare independent implementations on random strings.

    Multiple implementations are useful because a second algorithm can
    expose subtle bugs in the first implementation.
    """
    alphabet = "abc"

    for _ in range(iterations):
        length = random.randint(0, 12)
        text = "".join(random.choice(alphabet) for _ in range(length))

        center = longest_palindromic_substring_center(text)
        dynamic = longest_palindromic_substring_dp(text)
        manacher = longest_palindromic_substring_manacher(text)

        if len(center) != len(dynamic) or len(center) != len(manacher):
            raise AssertionError(
                f"Longest-palindrome disagreement for {text!r}: "
                f"{center!r}, {dynamic!r}, {manacher!r}"
            )

    print(f"\nRandomized cross-check passed for {iterations} inputs.")


# ============================================================
# 16. SECURITY AND INPUT-SAFETY CONSIDERATIONS
# ============================================================

def safe_palindrome_analysis(text: str, max_length: int = 1_000_000) -> dict[str, object]:
    """
    Example of defensive input handling.

    Production systems should establish reasonable input limits before
    performing memory-intensive operations such as O(n^2) dynamic programming
    or collecting every palindromic substring.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if len(text) > max_length:
        raise ValueError(
            f"text exceeds the configured limit of {max_length} characters"
        )

    return {
        "length": len(text),
        "is_palindrome": is_two_pointer_palindrome(text),
        "valid_palindrome": is_valid_palindrome(text),
        "can_remove_one": can_be_palindrome_after_removing_one(text),
    }


# ============================================================
# 17. EDUCATIONAL DRIVER
# ============================================================

def main() -> None:
    print("=" * 72)
    print("DAY 22 — PALINDROMES")
    print("=" * 72)

    print("\nBasic character palindrome:")
    for value in ["racecar", "hello", "level", "a", ""]:
        print(f"{value!r}: {is_character_palindrome(value)}")

    print("\nTwo-pointer palindrome:")
    for value in ["racecar", "python", "abba", "abcba"]:
        print(f"{value!r}: {is_two_pointer_palindrome(value)}")

    print("\nValid palindrome:")
    valid_examples = [
        "A man, a plan, a canal: Panama",
        "race a car",
        " ",
        "No 'x' in Nixon",
    ]

    for value in valid_examples:
        print(f"{value!r}: {is_valid_palindrome(value)}")

    print("\nNumber palindrome:")
    for number in [121, 123, 1221, -121, 10, 0]:
        print(f"{number}: {is_number_palindrome_math(number)}")

    print("\nRemove-one-character palindrome:")
    for value in ["abca", "abc", "deeee", "racecar"]:
        print(f"{value!r}: {can_be_palindrome_after_removing_one(value)}")

    print("\nLongest palindromic substring:")
    for value in ["babad", "cbbd", "racecar", "forgeeksskeegfor"]:
        print(
            f"{value!r}: "
            f"center={longest_palindromic_substring_center(value)!r}, "
            f"DP={longest_palindromic_substring_dp(value)!r}, "
            f"Manacher={longest_palindromic_substring_manacher(value)!r}"
        )

    print("\nAll palindromic substrings:")
    for value in ["aba", "aaa", "abba"]:
        print(f"{value!r}: {all_palindromic_substrings_center(value)}")

    demonstrate_substring_vs_subsequence()
    demonstrate_partitioning()
    demonstrate_edge_cases()

    print("\nDefensive input analysis:")
    print(safe_palindrome_analysis("A man, a plan, a canal: Panama"))

    run_tests()
    randomized_cross_check()
    benchmark_longest_palindrome()

    print("\nKey complexity facts:")
    print("Single palindrome two-pointer check: O(n) time, O(1) extra space.")
    print("Remove-one-character palindrome: O(n) time, O(1) extra space.")
    print("Center expansion for longest substring: O(n^2) time, O(1) extra space.")
    print("DP for longest substring: O(n^2) time, O(n^2) space.")
    print("Manacher's algorithm: O(n) time, O(n) space.")
    print("Palindrome partitioning: potentially exponential output size.")


if __name__ == "__main__":
    main()
