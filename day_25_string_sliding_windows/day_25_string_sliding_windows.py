String Sliding Window
==============================

A comprehensive, executable study file covering string sliding-window
techniques from beginner to advanced level.

Topics:
- Sliding-window fundamentals
- Longest substring without repetition
- Character-frequency windows
- Minimum-window concepts
- Window expansion and contraction
- At-most-K-distinct-character problems
- Exactly-K-distinct-character problems
- Frequency constraints
- Fixed-size and variable-size windows
- Unicode considerations
- Edge cases
- Complexity analysis
- Testing and debugging
- Practical string-processing patterns
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


# ============================================================================
# 1. FOUNDATIONS
# ============================================================================

def print_section(title: str) -> None:
    """Print a consistent heading for the interactive study output."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def window_text(text: str, left: int, right: int) -> str:
    """Return the inclusive window [left, right], or an empty string."""
    if left > right:
        return ""
    return text[left:right + 1]


# A sliding window maintains a contiguous range:
#
#     left ---------------- right
#          current window
#
# The right boundary normally expands the window.
# The left boundary contracts it when a constraint is violated.
#
# The central idea is not simply "use two pointers". The important property
# is that the window represents a state that can be updated incrementally.


def demonstrate_basic_window() -> None:
    print_section("1. Basic Sliding-Window Mechanics")

    text = "abcdef"
    left = 0

    print(f"Input: {text!r}")

    for right, character in enumerate(text):
        current = text[left:right + 1]
        print(
            f"right={right}, character={character!r}, "
            f"window={current!r}, left={left}, right={right}"
        )

    print(
        "\nThe right pointer visits each character once. "
        "A real variable-size algorithm usually moves the left pointer "
        "only when the current window violates its rule."
    )


# ============================================================================
# 2. FIXED-SIZE WINDOWS
# ============================================================================

def fixed_size_window_sums(values: List[int], k: int) -> List[int]:
    """
    Calculate every contiguous window sum of exactly k elements.

    Time: O(n)
    Space: O(n) for the output.
    """
    if k <= 0:
        raise ValueError("Window size k must be positive.")

    if k > len(values):
        return []

    results: List[int] = []
    current_sum = sum(values[:k])
    results.append(current_sum)

    for right in range(k, len(values)):
        # Remove the element leaving from the left.
        current_sum -= values[right - k]

        # Add the new element entering from the right.
        current_sum += values[right]

        results.append(current_sum)

    return results


# ============================================================================
# 3. LONGEST SUBSTRING WITHOUT REPETITION
# ============================================================================

def longest_substring_without_repetition_set(text: str) -> Tuple[int, str]:
    """
    Find the longest substring containing no repeated characters.

    A set stores the characters currently inside the window.

    When a duplicate appears, repeatedly remove characters from the left
    until the duplicate is no longer present.

    Time: O(n) because every character enters and leaves the set at most once.
    Space: O(min(n, alphabet_size)).
    """
    characters: set[str] = set()
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        while character in characters:
            characters.remove(text[left])
            left += 1

        characters.add(character)

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


def longest_substring_without_repetition_last_seen(
    text: str,
) -> Tuple[int, str]:
    """
    Optimized version using the last index of each character.

    Instead of moving left one position at a time, jump directly.

    Important detail:
        left = max(left, last_seen[character] + 1)

    The max() prevents left from moving backward.
    """
    last_seen: Dict[str, int] = {}
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        if character in last_seen:
            left = max(left, last_seen[character] + 1)

        last_seen[character] = right

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


def demonstrate_longest_unique() -> None:
    print_section("2. Longest Substring Without Repetition")

    examples = [
        "",
        "a",
        "abcabcbb",
        "bbbbb",
        "pwwkew",
        "dvdf",
        "abba",
        "abcdef",
        "a b c a",
        "😀ab😀cd",
    ]

    for text in examples:
        length_a, substring_a = longest_substring_without_repetition_set(text)
        length_b, substring_b = longest_substring_without_repetition_last_seen(text)

        print(
            f"{text!r:16} -> "
            f"set={substring_a!r} ({length_a}), "
            f"last_seen={substring_b!r} ({length_b})"
        )


# ============================================================================
# 4. CHARACTER-FREQUENCY WINDOWS
# ============================================================================

def frequency_window_demo(text: str, left: int, right: int) -> Counter:
    """
    Return frequencies for a specified inclusive substring.
    """
    return Counter(text[left:right + 1])


def longest_substring_with_at_most_k_distinct(
    text: str,
    k: int,
) -> Tuple[int, str]:
    """
    Longest substring containing at most k distinct characters.

    Frequency counts let us know when a character disappears completely
    from the window during contraction.
    """
    if k < 0:
        raise ValueError("k cannot be negative.")

    if k == 0 or not text:
        return 0, ""

    frequencies: Dict[str, int] = defaultdict(int)
    distinct = 0
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        if frequencies[character] == 0:
            distinct += 1

        frequencies[character] += 1

        while distinct > k:
            left_character = text[left]
            frequencies[left_character] -= 1

            if frequencies[left_character] == 0:
                distinct -= 1

            left += 1

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


def demonstrate_frequency_windows() -> None:
    print_section("3. Character-Frequency Windows")

    text = "aabccbb"
    print(f"Text: {text!r}")

    for left, right in [(0, 0), (0, 2), (1, 4), (2, 6)]:
        print(
            f"window={window_text(text, left, right)!r}, "
            f"frequency={dict(frequency_window_demo(text, left, right))}"
        )

    examples = [
        ("eceba", 2),
        ("aa", 1),
        ("aabbcc", 2),
        ("aabbcc", 3),
        ("abcadcacacaca", 2),
    ]

    for text, k in examples:
        length, substring = longest_substring_with_at_most_k_distinct(text, k)
        print(
            f"at_most_{k}_distinct: {text!r} -> "
            f"{substring!r}, length={length}"
        )


# ============================================================================
# 5. MINIMUM WINDOW SUBSTRING
# ============================================================================

def minimum_window_substring(text: str, target: str) -> str:
    """
    Find the shortest substring of text containing every character in target
    with at least the required frequency.

    Example:
        text   = "ADOBECODEBANC"
        target = "ABC"
        result = "BANC"

    The target may contain duplicate characters:
        target = "AABC"
    requires two As, one B, and one C.

    Complexity:
        Time: O(len(text) + len(target))
        Space: O(number of distinct target characters)
    """
    if not text or not target:
        return ""

    required = Counter(target)
    window: Dict[str, int] = defaultdict(int)

    required_distinct = len(required)
    satisfied_distinct = 0

    left = 0
    best_start = 0
    best_length = float("inf")

    for right, character in enumerate(text):
        window[character] += 1

        if character in required and window[character] == required[character]:
            satisfied_distinct += 1

        # Contract while all required character counts are satisfied.
        while satisfied_distinct == required_distinct:
            current_length = right - left + 1

            if current_length < best_length:
                best_length = current_length
                best_start = left

            left_character = text[left]
            window[left_character] -= 1

            if (
                left_character in required
                and window[left_character] < required[left_character]
            ):
                satisfied_distinct -= 1

            left += 1

    if best_length == float("inf"):
        return ""

    return text[best_start:best_start + int(best_length)]


def demonstrate_minimum_window() -> None:
    print_section("4. Minimum-Window Concepts")

    examples = [
        ("ADOBECODEBANC", "ABC"),
        ("a", "a"),
        ("a", "aa"),
        ("aa", "aa"),
        ("aaflslflsldkalskaaa", "aaa"),
        ("abc", "cba"),
        ("abc", "xyz"),
        ("", "A"),
        ("ABC", ""),
    ]

    for text, target in examples:
        result = minimum_window_substring(text, target)
        print(f"text={text!r}, target={target!r} -> {result!r}")


# ============================================================================
# 6. EXACTLY K DISTINCT
# ============================================================================

def count_substrings_with_at_most_k_distinct(text: str, k: int) -> int:
    """
    Count all substrings containing at most k distinct characters.

    For every right endpoint, after contraction, every starting position
    from left through right creates a valid substring.

    Therefore the number of valid substrings ending at right is:
        right - left + 1
    """
    if k < 0:
        return 0

    if k == 0:
        return 0

    frequencies: Dict[str, int] = defaultdict(int)
    distinct = 0
    left = 0
    count = 0

    for right, character in enumerate(text):
        if frequencies[character] == 0:
            distinct += 1

        frequencies[character] += 1

        while distinct > k:
            left_character = text[left]
            frequencies[left_character] -= 1

            if frequencies[left_character] == 0:
                distinct -= 1

            left += 1

        count += right - left + 1

    return count


def count_substrings_with_exactly_k_distinct(text: str, k: int) -> int:
    """
    Exactly K distinct can be transformed into:

        atMost(K) - atMost(K - 1)

    This is a powerful reusable sliding-window identity.
    """
    if k <= 0:
        return 0

    return (
        count_substrings_with_at_most_k_distinct(text, k)
        - count_substrings_with_at_most_k_distinct(text, k - 1)
    )


def demonstrate_exactly_k_distinct() -> None:
    print_section("5. At-Most-K and Exactly-K Distinct Characters")

    examples = [
        ("pqpqs", 2),
        ("a", 1),
        ("abc", 2),
        ("aaaa", 1),
        ("aabbcc", 2),
    ]

    for text, k in examples:
        at_most = count_substrings_with_at_most_k_distinct(text, k)
        exactly = count_substrings_with_exactly_k_distinct(text, k)

        print(
            f"{text!r}, k={k}: "
            f"at_most={at_most}, exactly={exactly}"
        )


# ============================================================================
# 7. LONGEST SUBSTRING WITH EXACTLY K DISTINCT
# ============================================================================

def longest_substring_with_exactly_k_distinct(
    text: str,
    k: int,
) -> Tuple[int, str]:
    """
    Find the longest substring containing exactly k distinct characters.

    Unlike the at-most-K problem, a valid answer is recorded only when
    distinct == k.
    """
    if k <= 0:
        return 0, ""

    frequencies: Dict[str, int] = defaultdict(int)
    distinct = 0
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        if frequencies[character] == 0:
            distinct += 1

        frequencies[character] += 1

        while distinct > k:
            left_character = text[left]
            frequencies[left_character] -= 1

            if frequencies[left_character] == 0:
                distinct -= 1

            left += 1

        if distinct == k:
            current_length = right - left + 1

            if current_length > best_length:
                best_length = current_length
                best_start = left

    return best_length, text[best_start:best_start + best_length]


# ============================================================================
# 8. FREQUENCY-CONSTRAINED WINDOWS
# ============================================================================

def longest_repeating_character_replacement(
    text: str,
    k: int,
) -> Tuple[int, str]:
    """
    Find the longest substring that can be converted into one repeated
    character using at most k replacements.

    Window condition:
        window_length - highest_frequency <= k

    Why?
        The most frequent character can remain unchanged.
        Every other character must be replaced.

    Example:
        "AABABBA", k=1 -> "AABA" or "ABBA", length 4.
    """
    if k < 0:
        raise ValueError("k cannot be negative.")

    frequencies: Dict[str, int] = defaultdict(int)
    left = 0
    highest_frequency = 0

    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        frequencies[character] += 1
        highest_frequency = max(highest_frequency, frequencies[character])

        while (right - left + 1) - highest_frequency > k:
            frequencies[text[left]] -= 1
            left += 1

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


def demonstrate_frequency_constraints() -> None:
    print_section("6. Frequency-Constrained Windows")

    examples = [
        ("AABABBA", 1),
        ("ABAB", 2),
        ("AAAA", 0),
        ("ABCDE", 1),
        ("", 3),
    ]

    for text, k in examples:
        length, substring = longest_repeating_character_replacement(text, k)
        print(f"{text!r}, k={k} -> {substring!r}, length={length}")


# ============================================================================
# 9. ANAGRAM WINDOWS
# ============================================================================

def find_anagram_start_indices(text: str, pattern: str) -> List[int]:
    """
    Find every starting index where an anagram of pattern occurs.

    This is a fixed-size sliding window.

    Every valid window has exactly len(pattern) characters, and its frequency
    table must equal the pattern frequency table.
    """
    if not pattern or len(pattern) > len(text):
        return []

    pattern_frequency = Counter(pattern)
    window_frequency: Dict[str, int] = defaultdict(int)

    result: List[int] = []
    k = len(pattern)

    for right, character in enumerate(text):
        window_frequency[character] += 1

        if right >= k:
            outgoing = text[right - k]
            window_frequency[outgoing] -= 1

            if window_frequency[outgoing] == 0:
                del window_frequency[outgoing]

        if window_frequency == pattern_frequency:
            result.append(right - k + 1)

    return result


# ============================================================================
# 10. PERMUTATION EXISTENCE
# ============================================================================

def contains_permutation(text: str, pattern: str) -> bool:
    """Return True when text contains any permutation of pattern."""
    return bool(find_anagram_start_indices(text, pattern))


# ============================================================================
# 11. LONGEST SUBARRAY ANALOGUE
# ============================================================================

def longest_binary_subarray_with_at_most_k_zeros(
    values: List[int],
    k: int,
) -> Tuple[int, List[int]]:
    """
    A direct numeric analogue of a string sliding window.

    Find the longest contiguous binary subarray containing at most k zeros.
    """
    if k < 0:
        raise ValueError("k cannot be negative.")

    left = 0
    zero_count = 0
    best_start = 0
    best_length = 0

    for right, value in enumerate(values):
        if value == 0:
            zero_count += 1
        elif value != 1:
            raise ValueError("Input must contain only 0 and 1.")

        while zero_count > k:
            if values[left] == 0:
                zero_count -= 1
            left += 1

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, values[best_start:best_start + best_length]


# ============================================================================
# 12. GENERIC VARIABLE-WINDOW PATTERN
# ============================================================================

def generic_at_most_distinct(
    text: str,
    maximum_distinct: int,
) -> Tuple[int, str]:
    """
    A reusable template for longest substring under a distinct-count limit.

    The invariant is:

        distinct <= maximum_distinct

    after every contraction phase.
    """
    return longest_substring_with_at_most_k_distinct(text, maximum_distinct)


# ============================================================================
# 13. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print_section("7. Important Edge Cases")

    cases = [
        ("empty string", ""),
        ("single character", "x"),
        ("all characters equal", "aaaaaa"),
        ("all characters different", "abcdef"),
        ("Unicode characters", "😀😃😀😄"),
        ("spaces", "a b c a"),
        ("punctuation", "a!b!c"),
    ]

    for name, text in cases:
        length, substring = longest_substring_without_repetition_last_seen(text)

        print(
            f"{name:24} input={text!r}, "
            f"longest_unique={substring!r}, length={length}"
        )

    print(
        "\nImportant boundary cases include k=0, k<0, target longer than the "
        "source, empty input, duplicate target characters, and characters "
        "that appear many times."
    )


# ============================================================================
# 14. WINDOW TRACE FOR DEBUGGING
# ============================================================================

def trace_longest_unique(text: str) -> None:
    """
    Print every important state transition.

    Tracing window boundaries is one of the most effective ways to debug
    sliding-window algorithms.
    """
    print_section("8. Sliding-Window Debug Trace")

    characters: set[str] = set()
    left = 0

    print(f"Input: {text!r}\n")

    for right, character in enumerate(text):
        print(f"RIGHT -> {right}: {character!r}")

        while character in characters:
            removed = text[left]
            characters.remove(removed)
            print(f"  CONTRACT: remove {removed!r} at index {left}")
            left += 1

        characters.add(character)

        print(
            f"  WINDOW: [{left}, {right}] = {text[left:right + 1]!r}"
        )
        print(f"  ACTIVE CHARACTERS: {sorted(characters)}")


# ============================================================================
# 15. NAIVE VS SLIDING WINDOW
# ============================================================================

def naive_longest_unique(text: str) -> Tuple[int, str]:
    """
    A deliberately straightforward implementation.

    It examines every starting position and extends until a duplicate occurs.
    This is useful for comparison and testing, although the optimized
    sliding-window algorithm is preferred for large input.
    """
    best = ""

    for start in range(len(text)):
        seen: set[str] = set()

        for end in range(start, len(text)):
            if text[end] in seen:
                break

            seen.add(text[end])

            if end - start + 1 > len(best):
                best = text[start:end + 1]

    return len(best), best


# ============================================================================
# 16. VALIDATION HELPERS
# ============================================================================

def assert_longest_unique_correct(text: str) -> None:
    optimized = longest_substring_without_repetition_last_seen(text)
    reference = naive_longest_unique(text)

    assert optimized[0] == reference[0], (
        f"Length mismatch for {text!r}: "
        f"{optimized[0]} != {reference[0]}"
    )


def run_tests() -> None:
    print_section("9. Built-In Tests")

    known_cases = {
        "": 0,
        "a": 1,
        "abcabcbb": 3,
        "bbbbb": 1,
        "pwwkew": 3,
        "dvdf": 3,
        "abba": 2,
    }

    for text, expected_length in known_cases.items():
        actual_length, _ = longest_substring_without_repetition_last_seen(text)
        assert actual_length == expected_length

    assert minimum_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert minimum_window_substring("a", "aa") == ""
    assert minimum_window_substring("aa", "aa") == "aa"

    assert longest_substring_with_at_most_k_distinct("eceba", 2)[0] == 3
    assert longest_substring_with_at_most_k_distinct("aa", 1)[0] == 2

    assert count_substrings_with_exactly_k_distinct("pqpqs", 2) == 7

    assert find_anagram_start_indices("cbaebabacd", "abc") == [0, 6]
    assert contains_permutation("eidbaooo", "ab") is True
    assert contains_permutation("eidboaoo", "ab") is False

    for text in [
        "",
        "a",
        "aa",
        "abc",
        "abca",
        "abba",
        "abcabc",
        "aabbcc",
        "😀ab😀cd",
    ]:
        assert_longest_unique_correct(text)

    print("All tests passed.")


# ============================================================================
# 17. COMPLEXITY TABLE
# ============================================================================

def print_complexity_reference() -> None:
    print_section("10. Complexity Reference")

    rows = [
        (
            "Longest unique substring",
            "O(n)",
            "O(min(n, alphabet))",
        ),
        (
            "Longest at most K distinct",
            "O(n)",
            "O(min(n, alphabet))",
        ),
        (
            "Minimum window substring",
            "O(n + m)",
            "O(distinct target)",
        ),
        (
            "Count at most K distinct",
            "O(n)",
            "O(min(n, alphabet))",
        ),
        (
            "Exactly K distinct",
            "O(n)",
            "O(min(n, alphabet))",
        ),
        (
            "Find anagram windows",
            "O(n)",
            "O(distinct pattern)",
        ),
    ]

    print(f"{'Problem':34} {'Time':12} {'Extra Space'}")
    print("-" * 62)

    for problem, time, space in rows:
        print(f"{problem:34} {time:12} {space}")


# ============================================================================
# 18. ADVANCED CONCEPTS
# ============================================================================

def demonstrate_advanced_concepts() -> None:
    print_section("11. Advanced Sliding-Window Concepts")

    print_subsection("Invariant")

    print(
        "A sliding-window algorithm is easiest to reason about when the "
        "current window has a clearly stated invariant."
    )
    print(
        "Example invariant: after contraction, the current window contains "
        "at most K distinct characters."
    )

    print_subsection("Monotonicity")

    print(
        "Many variable-window problems work because adding characters can "
        "only move a window from valid to invalid, while removing characters "
        "can restore validity."
    )

    print_subsection("Two different optimization directions")

    print(
        "Longest-window problems generally expand the window and contract "
        "only when invalid."
    )
    print(
        "Minimum-window problems generally expand until valid and then "
        "contract aggressively to minimize the valid window."
    )

    print_subsection("At-most transformation")

    print(
        "Exactly-K counting is often transformed into "
        "atMost(K) - atMost(K - 1)."
    )

    print_subsection("Stale maximum frequencies")

    print(
        "In the character-replacement problem, highest_frequency may remain "
        "larger than the actual maximum frequency after contraction. This is "
        "intentional: the resulting condition still permits a correct maximum "
        "length, and recomputing the maximum at every step is unnecessary."
    )


# ============================================================================
# 19. PRACTICAL MINI CASE STUDY
# ============================================================================

@dataclass
class LogRecord:
    user_id: str
    action: str
    timestamp: int


def longest_unique_action_sequence(records: Iterable[LogRecord]) -> List[LogRecord]:
    """
    Find the longest contiguous sequence of log records in which no action
    repeats.

    This shows that sliding windows apply to structured records, not only
    raw strings.
    """
    records = list(records)

    seen: set[str] = set()
    left = 0
    best_start = 0
    best_length = 0

    for right, record in enumerate(records):
        while record.action in seen:
            seen.remove(records[left].action)
            left += 1

        seen.add(record.action)

        length = right - left + 1

        if length > best_length:
            best_length = length
            best_start = left

    return records[best_start:best_start + best_length]


def demonstrate_real_world_case() -> None:
    print_section("12. Practical Structured-Data Case Study")

    records = [
        LogRecord("U1", "LOGIN", 1),
        LogRecord("U1", "SEARCH", 2),
        LogRecord("U1", "VIEW", 3),
        LogRecord("U1", "SEARCH", 4),
        LogRecord("U1", "CHECKOUT", 5),
        LogRecord("U1", "PAYMENT", 6),
    ]

    result = longest_unique_action_sequence(records)

    print("Longest sequence with no repeated action:")
    for record in result:
        print(record)


# ============================================================================
# 20. MAIN DEMONSTRATION
# ============================================================================

def main() -> None:
    demonstrate_basic_window()

    print_section("Day 25 — String Sliding Window")

    demonstrate_longest_unique()
    demonstrate_frequency_windows()
    demonstrate_minimum_window()
    demonstrate_exactly_k_distinct()
    demonstrate_frequency_constraints()

    print_subsection("Exactly-K Distinct Longest Substring")

    examples = [
        ("aabacbebebe", 3),
        ("aa", 1),
        ("abc", 2),
        ("aabbcc", 2),
    ]

    for text, k in examples:
        length, substring = longest_substring_with_exactly_k_distinct(text, k)
        print(
            f"{text!r}, k={k} -> {substring!r}, length={length}"
        )

    print_subsection("Anagram Windows")

    for text, pattern in [
        ("cbaebabacd", "abc"),
        ("abab", "ab"),
        ("aaaa", "aa"),
        ("abcdef", "gh"),
    ]:
        print(
            f"text={text!r}, pattern={pattern!r} -> "
            f"indices={find_anagram_start_indices(text, pattern)}"
        )

    print_subsection("Binary At-Most-K-Zero Window")

    values = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0]
    length, result = longest_binary_subarray_with_at_most_k_zeros(values, 2)
    print(f"values={values}")
    print(f"longest window={result}, length={length}")

    demonstrate_edge_cases()
    trace_longest_unique("abcad")
    demonstrate_advanced_concepts()
    demonstrate_real_world_case()
    print_complexity_reference()

    run_tests()

    print_section("Study Checklist")
    checklist = [
        "Understand what the left and right boundaries represent.",
        "Know when a window is valid and when it becomes invalid.",
        "Use a set for simple uniqueness constraints.",
        "Use a frequency map when counts matter.",
        "Recognize longest-window versus minimum-window patterns.",
        "Recognize fixed-size versus variable-size windows.",
        "Use atMost(K) - atMost(K-1) for exactly-K counting.",
        "State the invariant before implementing the algorithm.",
        "Trace left/right movements when debugging.",
        "Check empty input, zero K, duplicate requirements, and Unicode input.",
    ]

    for item in checklist:
        print(f"[ ] {item}")


if __name__ == "__main__":
    main()
