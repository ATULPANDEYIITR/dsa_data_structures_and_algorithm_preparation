"""
Day 24 — Substrings
A comprehensive study of substring generation, contiguous and non-contiguous
sequences, substring counting, and string searching.

The file progresses from beginner concepts to advanced algorithms and includes
validation, edge cases, complexity analysis, practical demonstrations, and
a small collection of substring problem solutions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Tuple


# ============================================================================
# 1. FUNDAMENTAL DEFINITIONS
# ============================================================================

def is_valid_substring(text: str, candidate: str) -> bool:
    """Return True when candidate occurs contiguously inside text."""
    return candidate in text


def all_substrings(text: str, unique: bool = False) -> List[str]:
    """
    Generate all contiguous substrings.

    For a string of length n, there are n(n + 1) / 2 substring occurrences.
    Repeated substring values are retained unless unique=True.
    """
    substrings: List[str] = []

    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            substrings.append(text[start:end])

    if unique:
        return list(dict.fromkeys(substrings))

    return substrings


def all_substrings_with_positions(
    text: str,
) -> List[Tuple[int, int, str]]:
    """
    Return (start, end, substring), where end is exclusive.

    Example:
        "abc" -> (0, 1, "a"), (0, 2, "ab"), ...
    """
    result = []

    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            result.append((start, end, text[start:end]))

    return result


def print_substring_table(text: str) -> None:
    """Display every substring occurrence with its interval."""
    print(f"\nSubstring table for {text!r}")

    for start, end, substring in all_substrings_with_positions(text):
        print(f"[{start}:{end}] -> {substring!r}")


# ============================================================================
# 2. CONTIGUOUS VERSUS NON-CONTIGUOUS SEQUENCES
# ============================================================================

def is_subsequence(text: str, candidate: str) -> bool:
    """
    Check whether candidate is a subsequence of text.

    Characters must occur in the same order, but they do not have to be
    adjacent.

    Example:
        "abcde" -> "ace" is a subsequence.
        "abcde" -> "ad" is a subsequence.
        "abcde" -> "aec" is not a subsequence.
    """
    candidate_index = 0

    for character in text:
        if candidate_index < len(candidate) and character == candidate[candidate_index]:
            candidate_index += 1

    return candidate_index == len(candidate)


def is_contiguous_match(text: str, candidate: str) -> bool:
    """Explicitly demonstrate the stricter substring relationship."""
    return candidate in text


def demonstrate_contiguous_vs_non_contiguous() -> None:
    text = "ABCDE"
    examples = ["ABC", "ACE", "ADE", "AEC", "BCD"]

    print("\nContiguous versus non-contiguous:")
    for candidate in examples:
        print(
            f"{candidate!r}: "
            f"substring={is_contiguous_match(text, candidate)}, "
            f"subsequence={is_subsequence(text, candidate)}"
        )


# ============================================================================
# 3. COUNTING SUBSTRINGS
# ============================================================================

def count_all_substrings(text: str) -> int:
    """
    Count substring occurrences mathematically.

    Every substring is identified by choosing a start position and an end
    position after it.

    Number of non-empty substring occurrences:
        n * (n + 1) // 2
    """
    n = len(text)
    return n * (n + 1) // 2


def count_substrings_of_length(text: str, length: int) -> int:
    """
    Count substring occurrences having exactly the requested length.

    There are n - length + 1 such substrings when 1 <= length <= n.
    """
    if length < 1 or length > len(text):
        return 0

    return len(text) - length + 1


def count_distinct_substrings_bruteforce(text: str) -> int:
    """Count distinct non-empty substrings using a set."""
    return len(set(all_substrings(text, unique=False)))


def distinct_substring_frequency(text: str) -> Dict[str, int]:
    """Count how often every substring occurrence appears."""
    return dict(Counter(all_substrings(text)))


def count_occurrences_overlapping(text: str, pattern: str) -> int:
    """
    Count overlapping occurrences.

    Example:
        text="aaaa", pattern="aa" -> 3

    Python's str.count() is not appropriate here because it counts
    non-overlapping occurrences.
    """
    if pattern == "":
        raise ValueError("An empty pattern is not accepted for this function.")

    count = 0

    for start in range(len(text) - len(pattern) + 1):
        if text.startswith(pattern, start):
            count += 1

    return count


def count_occurrences_non_overlapping(text: str, pattern: str) -> int:
    """Count non-overlapping occurrences using Python's built-in search."""
    if pattern == "":
        raise ValueError("An empty pattern is not accepted.")

    return text.count(pattern)


# ============================================================================
# 4. BRUTE-FORCE STRING SEARCH
# ============================================================================

def brute_force_search(text: str, pattern: str) -> int:
    """
    Return the first index where pattern occurs in text.

    Worst-case time:
        O(nm)

    where n is the text length and m is the pattern length.
    """
    if pattern == "":
        return 0

    if len(pattern) > len(text):
        return -1

    for start in range(len(text) - len(pattern) + 1):
        matched = True

        for offset in range(len(pattern)):
            if text[start + offset] != pattern[offset]:
                matched = False
                break

        if matched:
            return start

    return -1


def brute_force_search_all(text: str, pattern: str) -> List[int]:
    """Return all occurrence positions, including overlapping occurrences."""
    if pattern == "":
        return list(range(len(text) + 1))

    positions = []

    for start in range(len(text) - len(pattern) + 1):
        if text[start:start + len(pattern)] == pattern:
            positions.append(start)

    return positions


# ============================================================================
# 5. PREFIX FUNCTION AND KMP
# ============================================================================

def prefix_function(pattern: str) -> List[int]:
    """
    Build the KMP prefix-function/LPS array.

    lps[i] stores the length of the longest proper prefix of pattern[:i+1]
    that is also a suffix of pattern[:i+1].

    Complexity: O(m)
    """
    lps = [0] * len(pattern)
    length = 0
    index = 1

    while index < len(pattern):
        if pattern[index] == pattern[length]:
            length += 1
            lps[index] = length
            index += 1
        elif length > 0:
            length = lps[length - 1]
        else:
            lps[index] = 0
            index += 1

    return lps


def kmp_search(text: str, pattern: str) -> int:
    """
    Knuth-Morris-Pratt string search.

    Complexity:
        preprocessing: O(m)
        search:        O(n)
        total:         O(n + m)
    """
    if pattern == "":
        return 0

    if len(pattern) > len(text):
        return -1

    lps = prefix_function(pattern)
    text_index = 0
    pattern_index = 0

    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1

            if pattern_index == len(pattern):
                return text_index - pattern_index
        elif pattern_index > 0:
            pattern_index = lps[pattern_index - 1]
        else:
            text_index += 1

    return -1


def kmp_search_all(text: str, pattern: str) -> List[int]:
    """Find every pattern occurrence, including overlapping matches."""
    if pattern == "":
        return list(range(len(text) + 1))

    lps = prefix_function(pattern)
    positions = []
    text_index = 0
    pattern_index = 0

    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1

            if pattern_index == len(pattern):
                positions.append(text_index - pattern_index)
                pattern_index = lps[pattern_index - 1]
        elif pattern_index > 0:
            pattern_index = lps[pattern_index - 1]
        else:
            text_index += 1

    return positions


# ============================================================================
# 6. RABIN-KARP ROLLING HASH SEARCH
# ============================================================================

def rabin_karp_search(
    text: str,
    pattern: str,
    base: int = 256,
    modulus: int = 1_000_000_007,
) -> int:
    """
    Search using a rolling polynomial hash.

    Hash matches are verified character-by-character, preventing a hash
    collision from becoming a false positive.

    Average behavior is close to O(n + m) with a suitable hash.
    Worst-case behavior can reach O(nm) because of collisions.
    """
    if pattern == "":
        return 0

    n = len(text)
    m = len(pattern)

    if m > n:
        return -1

    pattern_hash = 0
    window_hash = 0
    highest_power = pow(base, m - 1, modulus)

    for index in range(m):
        pattern_hash = (
            pattern_hash * base + ord(pattern[index])
        ) % modulus
        window_hash = (
            window_hash * base + ord(text[index])
        ) % modulus

    for start in range(n - m + 1):
        if pattern_hash == window_hash:
            if text[start:start + m] == pattern:
                return start

        if start < n - m:
            leading = ord(text[start]) * highest_power
            window_hash = (
                (window_hash - leading) * base
                + ord(text[start + m])
            ) % modulus

    return -1


# ============================================================================
# 7. Z ALGORITHM
# ============================================================================

def z_function(text: str) -> List[int]:
    """
    Compute the Z-array.

    z[i] is the length of the longest substring beginning at i that matches
    the prefix of text.

    Complexity: O(n).
    """
    n = len(text)

    if n == 0:
        return []

    z = [0] * n
    left = right = 0

    for index in range(1, n):
        if index <= right:
            z[index] = min(right - index + 1, z[index - left])

        while (
            index + z[index] < n
            and text[z[index]] == text[index + z[index]]
        ):
            z[index] += 1

        if index + z[index] - 1 > right:
            left = index
            right = index + z[index] - 1

    z[0] = n
    return z


def z_search(text: str, pattern: str) -> int:
    """
    Search using the Z algorithm.

    A separator not present in either string is used to prevent a pattern
    match from crossing the pattern/text boundary.
    """
    if pattern == "":
        return 0

    separator = "\0"

    # If NUL occurs in either input, use a private Unicode character instead.
    if separator in text or separator in pattern:
        separator = "\U0010ffff"

    combined = pattern + separator + text
    z = z_function(combined)

    target_length = len(pattern)

    for index in range(target_length + 1, len(combined)):
        if z[index] >= target_length:
            return index - target_length - 1

    return -1


# ============================================================================
# 8. LONGEST COMMON PREFIX
# ============================================================================

def longest_common_prefix(strings: Iterable[str]) -> str:
    """
    Find the longest prefix shared by all strings.

    This is not a substring search problem by itself, but it demonstrates the
    distinction between a prefix and an arbitrary substring.
    """
    values = list(strings)

    if not values:
        return ""

    shortest = min(values, key=len)

    for index, character in enumerate(shortest):
        if any(value[index] != character for value in values):
            return shortest[:index]

    return shortest


# ============================================================================
# 9. LONGEST PALINDROMIC SUBSTRING
# ============================================================================

def longest_palindromic_substring(text: str) -> str:
    """
    Expand around every possible center.

    Complexity:
        Time:  O(n^2)
        Space: O(1), excluding returned substring.
    """
    if not text:
        return ""

    best_start = 0
    best_length = 1

    def expand(left: int, right: int) -> Tuple[int, int]:
        while left >= 0 and right < len(text) and text[left] == text[right]:
            left -= 1
            right += 1

        return left + 1, right - left - 1

    for center in range(len(text)):
        start, length = expand(center, center)
        if length > best_length:
            best_start = start
            best_length = length

        start, length = expand(center, center + 1)
        if length > best_length:
            best_start = start
            best_length = length

    return text[best_start:best_start + best_length]


# ============================================================================
# 10. LONGEST SUBSTRING WITHOUT REPEATING CHARACTERS
# ============================================================================

def longest_unique_substring(text: str) -> str:
    """
    Sliding-window solution.

    Each character's most recent position allows the left boundary to jump
    forward instead of repeatedly shrinking one character at a time.

    Complexity:
        Time: O(n)
        Space: O(min(n, alphabet size)).
    """
    last_seen: Dict[str, int] = {}
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1

        last_seen[character] = right

        current_length = right - left + 1

        if current_length > best_length:
            best_start = left
            best_length = current_length

    return text[best_start:best_start + best_length]


def longest_unique_substring_bruteforce(text: str) -> str:
    """Quadratic-style educational solution for comparison."""
    best = ""

    for start in range(len(text)):
        seen = set()

        for end in range(start, len(text)):
            if text[end] in seen:
                break

            seen.add(text[end])

            if end - start + 1 > len(best):
                best = text[start:end + 1]

    return best


# ============================================================================
# 11. COUNT SUBSTRINGS WITH EXACTLY K DISTINCT CHARACTERS
# ============================================================================

def count_at_most_k_distinct(text: str, k: int) -> int:
    """
    Count substrings containing at most k distinct characters.

    Sliding-window invariant:
        every substring ending at right and beginning at any index >= left
        has at most k distinct characters.
    """
    if k < 0:
        return 0

    frequency: Dict[str, int] = defaultdict(int)
    left = 0
    total = 0

    for right, character in enumerate(text):
        frequency[character] += 1

        while len(frequency) > k:
            outgoing = text[left]
            frequency[outgoing] -= 1

            if frequency[outgoing] == 0:
                del frequency[outgoing]

            left += 1

        total += right - left + 1

    return total


def count_exactly_k_distinct(text: str, k: int) -> int:
    """
    Exactly k distinct characters can be calculated as:

        at_most(k) - at_most(k - 1)
    """
    if k <= 0:
        return 0

    return count_at_most_k_distinct(text, k) - count_at_most_k_distinct(
        text, k - 1
    )


# ============================================================================
# 12. MINIMUM WINDOW SUBSTRING
# ============================================================================

def minimum_window_substring(text: str, target: str) -> str:
    """
    Find the shortest substring of text containing all characters of target,
    including multiplicities.

    Example:
        text="ADOBECODEBANC", target="ABC" -> "BANC"

    Complexity: O(n + m) time.
    """
    if not text or not target:
        return ""

    required = Counter(target)
    remaining = len(target)
    left = 0
    best_start = 0
    best_length = float("inf")

    for right, character in enumerate(text):
        if character in required:
            if required[character] > 0:
                remaining -= 1

            required[character] -= 1

        while remaining == 0:
            current_length = right - left + 1

            if current_length < best_length:
                best_length = current_length
                best_start = left

            outgoing = text[left]

            if outgoing in required:
                required[outgoing] += 1

                if required[outgoing] > 0:
                    remaining += 1

            left += 1

    if best_length == float("inf"):
        return ""

    return text[best_start:best_start + int(best_length)]


# ============================================================================
# 13. LONGEST REPEATED SUBSTRING USING A SUFFIX ARRAY IDEA
# ============================================================================

def suffix_array(text: str) -> List[int]:
    """
    Build a suffix array using Python sorting.

    This educational implementation is intentionally simple.

    A production suffix-array construction can use more sophisticated
    O(n log n) or O(n) algorithms. Python's sorting makes the conceptual
    relationship easy to inspect.
    """
    return sorted(range(len(text)), key=lambda index: text[index:])


def longest_common_prefix_length(
    text: str,
    first_suffix: int,
    second_suffix: int,
) -> int:
    """Compute LCP length between two suffixes."""
    length = 0

    while (
        first_suffix + length < len(text)
        and second_suffix + length < len(text)
        and text[first_suffix + length] == text[second_suffix + length]
    ):
        length += 1

    return length


def longest_repeated_substring(text: str) -> str:
    """
    Find a longest repeated substring using the suffix-array/LCP idea.

    Repeated substrings occur as common prefixes of adjacent suffixes in
    lexicographic order.
    """
    if not text:
        return ""

    suffixes = suffix_array(text)

    best_start = 0
    best_length = 0

    for index in range(len(suffixes) - 1):
        common_length = longest_common_prefix_length(
            text,
            suffixes[index],
            suffixes[index + 1],
        )

        if common_length > best_length:
            best_length = common_length
            best_start = suffixes[index]

    return text[best_start:best_start + best_length]


# ============================================================================
# 14. DISTINCT SUBSTRING COUNT USING A SUFFIX ARRAY
# ============================================================================

def count_distinct_substrings_suffix_array(text: str) -> int:
    """
    Count distinct non-empty substrings using suffixes and LCP values.

    For suffix i, the number of new distinct substrings contributed is:

        suffix_length - LCP(previous_suffix, suffix)

    Therefore:

        total = n(n + 1)/2 - sum(LCP values)
    """
    n = len(text)

    if n == 0:
        return 0

    suffixes = suffix_array(text)
    total = n * (n + 1) // 2

    for index in range(1, n):
        total -= longest_common_prefix_length(
            text,
            suffixes[index - 1],
            suffixes[index],
        )

    return total


# ============================================================================
# 15. SUBSTRING HASHING
# ============================================================================

class PolynomialRollingHash:
    """
    Prefix-hash structure for fast substring hash queries.

    With prefix hashes and powers, a substring hash can be obtained in O(1).

    Hash equality is not a mathematical proof of string equality because
    collisions are possible. Applications requiring deterministic equality
    should verify the actual substring or use multiple independent hashes.
    """

    def __init__(
        self,
        text: str,
        base: int = 911382323,
        modulus: int = 972663749,
    ) -> None:
        if modulus <= base:
            raise ValueError("Choose a modulus larger than the base.")

        self.text = text
        self.base = base
        self.modulus = modulus
        self.prefix = [0] * (len(text) + 1)
        self.power = [1] * (len(text) + 1)

        for index, character in enumerate(text):
            self.prefix[index + 1] = (
                self.prefix[index] * base + ord(character)
            ) % modulus
            self.power[index + 1] = (
                self.power[index] * base
            ) % modulus

    def substring_hash(self, start: int, end: int) -> int:
        """Return a normalized hash for text[start:end]."""
        if not (0 <= start <= end <= len(self.text)):
            raise IndexError("Substring bounds are invalid.")

        return (
            self.prefix[end]
            - self.prefix[start] * self.power[end - start]
        ) % self.modulus

    def equal_substrings(
        self,
        first_start: int,
        first_end: int,
        second_start: int,
        second_end: int,
    ) -> bool:
        """Hash comparison followed by exact comparison for correctness."""
        first = self.substring_hash(first_start, first_end)
        second = self.substring_hash(second_start, second_end)

        if first != second:
            return False

        return self.text[first_start:first_end] == self.text[second_start:second_end]


# ============================================================================
# 16. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print("\nEdge cases:")

    cases = [
        "",
        "a",
        "aa",
        "aaaa",
        "abc",
        "😀ab😀",
    ]

    for text in cases:
        print(
            f"{text!r}: "
            f"occurrences={count_all_substrings(text)}, "
            f"distinct={count_distinct_substrings_bruteforce(text)}, "
            f"longest_unique={longest_unique_substring(text)!r}, "
            f"longest_palindrome={longest_palindromic_substring(text)!r}"
        )

    print(
        "Empty pattern search:",
        brute_force_search("abc", ""),
        kmp_search("abc", ""),
        rabin_karp_search("abc", ""),
        z_search("abc", ""),
    )


# ============================================================================
# 17. COMPARISON TABLE
# ============================================================================

def compare_search_algorithms() -> None:
    text = "ABABDABACDABABCABAB"
    pattern = "ABABCABAB"

    algorithms = [
        ("Python in operator", lambda: text.find(pattern)),
        ("Brute force", lambda: brute_force_search(text, pattern)),
        ("KMP", lambda: kmp_search(text, pattern)),
        ("Rabin-Karp", lambda: rabin_karp_search(text, pattern)),
        ("Z algorithm", lambda: z_search(text, pattern)),
    ]

    print("\nString-search comparison:")
    for name, algorithm in algorithms:
        print(f"{name:22} -> index {algorithm()}")


# ============================================================================
# 18. PRACTICE PROBLEMS
# ============================================================================

def problem_count_a_substrings(text: str) -> int:
    """
    Count substrings made entirely from character 'a'.

    A run of length L contributes:
        L(L + 1) / 2
    """
    total = 0
    run_length = 0

    for character in text:
        if character == "a":
            run_length += 1
            total += run_length
        else:
            run_length = 0

    return total


def problem_longest_substring_with_k_distinct(
    text: str,
    k: int,
) -> str:
    """Return the longest substring containing at most k distinct characters."""
    if k <= 0:
        return ""

    frequency: Dict[str, int] = defaultdict(int)
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        frequency[character] += 1

        while len(frequency) > k:
            outgoing = text[left]
            frequency[outgoing] -= 1

            if frequency[outgoing] == 0:
                del frequency[outgoing]

            left += 1

        current_length = right - left + 1

        if current_length > best_length:
            best_start = left
            best_length = current_length

    return text[best_start:best_start + best_length]


def problem_contains_permutation(text: str, pattern: str) -> bool:
    """
    Determine whether text contains any permutation of pattern.

    A fixed-size sliding window maintains character frequencies.
    """
    if len(pattern) > len(text):
        return False

    if not pattern:
        return True

    target = Counter(pattern)
    window = Counter(text[:len(pattern)])

    if window == target:
        return True

    window_size = len(pattern)

    for right in range(window_size, len(text)):
        incoming = text[right]
        outgoing = text[right - window_size]

        window[incoming] += 1
        window[outgoing] -= 1

        if window[outgoing] == 0:
            del window[outgoing]

        if window == target:
            return True

    return False


def problem_longest_common_substring(
    first: str,
    second: str,
) -> str:
    """
    Dynamic-programming solution for the longest common substring.

    Important distinction:
        Longest common substring requires contiguous characters.
        Longest common subsequence does not.

    Time:  O(nm)
    Space: O(nm)
    """
    if not first or not second:
        return ""

    rows = len(first) + 1
    columns = len(second) + 1
    dp = [[0] * columns for _ in range(rows)]

    best_length = 0
    best_end = 0

    for i in range(1, rows):
        for j in range(1, columns):
            if first[i - 1] == second[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1

                if dp[i][j] > best_length:
                    best_length = dp[i][j]
                    best_end = i

    return first[best_end - best_length:best_end]


# ============================================================================
# 19. TESTING
# ============================================================================

def run_assertions() -> None:
    """Basic correctness checks for the educational implementations."""
    assert all_substrings("abc") == [
        "a", "ab", "abc", "b", "bc", "c"
    ]

    assert count_all_substrings("abcde") == 15
    assert count_substrings_of_length("abcde", 3) == 3
    assert count_distinct_substrings_bruteforce("aaa") == 3

    assert is_subsequence("abcde", "ace")
    assert not is_subsequence("abcde", "aec")

    assert brute_force_search("hello", "ll") == 2
    assert brute_force_search("hello", "xyz") == -1

    assert kmp_search("ABABDABACDABABCABAB", "ABABCABAB") == 10
    assert kmp_search_all("aaaa", "aa") == [0, 1, 2]

    assert rabin_karp_search("hello world", "world") == 6
    assert z_search("hello world", "world") == 6

    assert count_occurrences_overlapping("aaaa", "aa") == 3
    assert count_occurrences_non_overlapping("aaaa", "aa") == 2

    assert longest_palindromic_substring("babad") in {"bab", "aba"}
    assert longest_unique_substring("abcabcbb") == "abc"

    assert count_exactly_k_distinct("pqpqs", 2) == 7
    assert minimum_window_substring("ADOBECODEBANC", "ABC") == "BANC"

    assert longest_repeated_substring("banana") == "ana"
    assert count_distinct_substrings_suffix_array("aaa") == 3

    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"

    assert problem_count_a_substrings("aaabb") == 6
    assert problem_longest_substring_with_k_distinct("eceba", 2) == "ece"
    assert problem_contains_permutation("eidbaooo", "ab")
    assert not problem_contains_permutation("eidboaoo", "ab")
    assert problem_longest_common_substring("ABABC", "BABCA") == "BABC"

    rolling_hash = PolynomialRollingHash("abracadabra")
    assert rolling_hash.equal_substrings(0, 3, 7, 10)


# ============================================================================
# 20. INTERACTIVE STUDY DEMONSTRATION
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("DAY 24 — SUBSTRINGS")
    print("=" * 78)

    text = "banana"

    print("\n1. Basic substring generation")
    print("Text:", text)
    print("All occurrences:", all_substrings(text))
    print("Distinct substrings:", all_substrings(text, unique=True))
    print_substring_table("abc")

    print("\n2. Contiguous versus non-contiguous")
    demonstrate_contiguous_vs_non_contiguous()

    print("\n3. Counting")
    print("banana occurrence count:", count_all_substrings(text))
    print("banana distinct count:", count_distinct_substrings_bruteforce(text))
    print("Length-3 substrings:", count_substrings_of_length(text, 3))

    print("\n4. Pattern occurrences")
    print("banana / ana overlapping:", count_occurrences_overlapping("banana", "ana"))
    print("aaaa / aa overlapping:", count_occurrences_overlapping("aaaa", "aa"))
    print("aaaa / aa non-overlapping:", count_occurrences_non_overlapping("aaaa", "aa"))

    print("\n5. Search algorithms")
    compare_search_algorithms()

    print("\n6. Prefix function")
    pattern = "ABABCABAB"
    print(pattern)
    print(prefix_function(pattern))

    print("\n7. Sliding-window examples")
    print(
        "Longest unique substring:",
        longest_unique_substring("abcabcbb"),
    )
    print(
        "Longest substring with at most 2 distinct:",
        problem_longest_substring_with_k_distinct("eceba", 2),
    )
    print(
        "Exactly 2 distinct count:",
        count_exactly_k_distinct("pqpqs", 2),
    )

    print("\n8. Window and palindrome problems")
    print(
        "Minimum window:",
        minimum_window_substring("ADOBECODEBANC", "ABC"),
    )
    print(
        "Longest palindrome:",
        longest_palindromic_substring("forgeeksskeegfor"),
    )

    print("\n9. Suffix-array examples")
    print("Suffix array of banana:", suffix_array("banana"))
    print("Longest repeated substring:", longest_repeated_substring("banana"))
    print(
        "Distinct substring count:",
        count_distinct_substrings_suffix_array("banana"),
    )

    print("\n10. Practice problems")
    print("Substrings containing only a:", problem_count_a_substrings("aaabb"))
    print(
        "Permutation exists:",
        problem_contains_permutation("eidbaooo", "ab"),
    )
    print(
        "Longest common substring:",
        problem_longest_common_substring("ABABC", "BABCA"),
    )

    print("\n11. Edge cases")
    demonstrate_edge_cases()

    print("\n12. Correctness tests")
    run_assertions()
    print("All assertions passed.")

    print("\nStudy notes:")
    print("- A substring is contiguous.")
    print("- A subsequence preserves order but does not require contiguity.")
    print("- A length-n string has n(n+1)/2 non-empty substring occurrences.")
    print("- Distinct substring counting is harder because duplicate values merge.")
    print("- Brute-force search is simple but can take O(nm).")
    print("- KMP guarantees O(n+m) pattern searching.")
    print("- Rabin-Karp uses hashing and requires collision awareness.")
    print("- Sliding windows are powerful for constrained substring problems.")
    print("- Suffix structures support advanced substring analysis.")


if __name__ == "__main__":
    main()
