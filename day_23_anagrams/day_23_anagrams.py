"""
Day 23 — Anagrams
==================

A comprehensive, self-contained study program covering:

1. What anagrams are
2. Sorting-based anagram checking
3. Frequency-based anagram checking
4. Character maps / dictionaries
5. Unicode-aware frequency counting
6. Normalization and preprocessing
7. Case sensitivity and punctuation
8. Anagram detection in collections
9. Grouping anagrams
10. Anagram windows
11. Frequency matching
12. Sliding-window techniques
13. Exact and normalized anagrams
14. Edge cases and failure conditions
15. Complexity analysis
16. Testing and validation
17. Practical applications
18. Advanced implementations
19. Streaming-oriented frequency comparison
20. Performance comparisons

The program intentionally uses only the Python standard library.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable, Iterator, Sequence


# ============================================================================
# 1. FUNDAMENTAL CONCEPTS
# ============================================================================

def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_result(label: str, result: object) -> None:
    """Print a labeled result."""
    print(f"{label:<42}: {result}")


def explain_anagram() -> None:
    """
    Demonstrate the fundamental definition.

    Two strings are anagrams when they contain exactly the same characters
    with exactly the same multiplicities, after applying whatever
    normalization rule the problem specifies.
    """
    print_section("1. What Is an Anagram?")

    examples = [
        ("listen", "silent"),
        ("evil", "vile"),
        ("rail safety", "fairy tales"),
        ("python", "typhon"),
        ("hello", "world"),
    ]

    for first, second in examples:
        print(f"{first!r:15} <-> {second!r:15}")


# ============================================================================
# 2. NORMALIZATION
# ============================================================================

def normalize_letters_only(text: str) -> str:
    """
    Keep only Unicode alphanumeric characters and normalize case.

    This is useful when a problem defines anagrams independently of spaces,
    punctuation, and letter case.
    """
    return "".join(character.casefold() for character in text if character.isalnum())


def normalize_ascii_letters(text: str) -> str:
    """
    Keep ASCII letters only and normalize them to lowercase.

    This is appropriate when a problem explicitly defines the alphabet
    as English A-Z/a-z.
    """
    return "".join(
        character.lower()
        for character in text
        if ("a" <= character.lower() <= "z")
    )


def demonstrate_normalization() -> None:
    print_section("2. Normalization and Problem Definitions")

    samples = [
        "Listen",
        "Rail Safety!",
        "Dormitory",
        "The Eyes",
        "A gentleman",
        "你好",
        "São Paulo",
    ]

    for sample in samples:
        print(
            f"{sample!r:20} -> "
            f"Unicode alphanumeric: {normalize_letters_only(sample)!r:20} | "
            f"ASCII letters: {normalize_ascii_letters(sample)!r}"
        )


# ============================================================================
# 3. SORTING-BASED ANAGRAM CHECKING
# ============================================================================

def are_anagrams_sorting(
    first: str,
    second: str,
    *,
    normalize: bool = False,
) -> bool:
    """
    Determine whether two strings are anagrams using sorting.

    Complexity:
        Time:  O(n log n)
        Space: O(n)

    Sorting makes the character order canonical. If the sorted sequences
    are identical, the original strings contain the same characters with
    the same multiplicities.
    """
    if normalize:
        first = normalize_letters_only(first)
        second = normalize_letters_only(second)

    if len(first) != len(second):
        return False

    return sorted(first) == sorted(second)


def demonstrate_sorting_method() -> None:
    print_section("3. Sorting-Based Anagram Checking")

    test_cases = [
        ("listen", "silent"),
        ("triangle", "integral"),
        ("apple", "papel"),
        ("rat", "car"),
        ("", ""),
        ("a", "A"),
    ]

    for first, second in test_cases:
        print_result(
            f"{first!r} vs {second!r}",
            are_anagrams_sorting(first, second),
        )

    print("\nCase-insensitive and punctuation-independent:")
    print_result(
        "Dormitory vs Dirty room",
        are_anagrams_sorting("Dormitory", "Dirty room", normalize=True),
    )
    print_result(
        "The eyes vs They see",
        are_anagrams_sorting("The eyes", "They see", normalize=True),
    )


# ============================================================================
# 4. FREQUENCY-BASED ANAGRAM CHECKING
# ============================================================================

def character_frequency(text: str) -> dict[str, int]:
    """
    Build a character-frequency map.

    A frequency map records:
        character -> number of occurrences
    """
    frequencies: dict[str, int] = {}

    for character in text:
        frequencies[character] = frequencies.get(character, 0) + 1

    return frequencies


def are_anagrams_frequency_map(
    first: str,
    second: str,
    *,
    normalize: bool = False,
) -> bool:
    """
    Determine whether two strings are anagrams using a dictionary.

    Complexity:
        Average time: O(n)
        Space: O(k)

    k is the number of distinct characters.
    """
    if normalize:
        first = normalize_letters_only(first)
        second = normalize_letters_only(second)

    if len(first) != len(second):
        return False

    return character_frequency(first) == character_frequency(second)


def are_anagrams_counter(
    first: str,
    second: str,
    *,
    normalize: bool = False,
) -> bool:
    """
    Determine whether two strings are anagrams using collections.Counter.

    Counter is a specialized frequency-map implementation from the
    Python standard library.
    """
    if normalize:
        first = normalize_letters_only(first)
        second = normalize_letters_only(second)

    if len(first) != len(second):
        return False

    return Counter(first) == Counter(second)


def demonstrate_frequency_method() -> None:
    print_section("4. Frequency-Based Checking")

    test_cases = [
        ("listen", "silent"),
        ("anagram", "nagaram"),
        ("hello", "world"),
        ("aabbcc", "abcabc"),
        ("aabb", "abab"),
        ("aab", "abb"),
    ]

    for first, second in test_cases:
        print(
            f"{first!r:12} vs {second!r:12} -> "
            f"map={are_anagrams_frequency_map(first, second)}, "
            f"Counter={are_anagrams_counter(first, second)}"
        )

    print("\nFrequency map for 'mississippi':")
    print(character_frequency("mississippi"))


# ============================================================================
# 5. FIXED-SIZE ALPHABET FREQUENCY ARRAY
# ============================================================================

def are_anagrams_ascii_array(first: str, second: str) -> bool:
    """
    Compare two strings using a fixed 26-element array.

    Assumption:
        Only ASCII English letters are valid.

    Complexity:
        Time: O(n)
        Space: O(1), because the array always contains 26 counters.

    This technique can be faster than a dictionary when the alphabet is
    small and fixed.
    """
    first = first.lower()
    second = second.lower()

    if len(first) != len(second):
        return False

    frequencies = [0] * 26

    for character in first:
        if not ("a" <= character <= "z"):
            raise ValueError(
                f"Unsupported character {character!r}; expected a-z."
            )
        frequencies[ord(character) - ord("a")] += 1

    for character in second:
        if not ("a" <= character <= "z"):
            raise ValueError(
                f"Unsupported character {character!r}; expected a-z."
            )
        frequencies[ord(character) - ord("a")] -= 1

    return all(value == 0 for value in frequencies)


# ============================================================================
# 6. SORTING VS FREQUENCY COMPARISON
# ============================================================================

def compare_methods() -> None:
    print_section("5. Sorting vs Frequency Methods")

    comparisons = [
        ("Sorting", "O(n log n)", "O(n)", "Simple; requires sorting"),
        (
            "Dictionary",
            "O(n) average",
            "O(k)",
            "Works with arbitrary characters",
        ),
        (
            "Counter",
            "O(n) average",
            "O(k)",
            "Concise standard-library implementation",
        ),
        (
            "26-element array",
            "O(n)",
            "O(1)",
            "Fast but only for a fixed alphabet",
        ),
    ]

    print(f"{'Method':<22}{'Time':<18}{'Space':<12}Notes")
    print("-" * 78)

    for method, time_complexity, space_complexity, notes in comparisons:
        print(
            f"{method:<22}{time_complexity:<18}"
            f"{space_complexity:<12}{notes}"
        )


# ============================================================================
# 7. GROUP ANAGRAMS
# ============================================================================

def group_anagrams_sorting(words: Sequence[str]) -> list[list[str]]:
    """
    Group words whose sorted characters are identical.

    Example:
        ["eat", "tea", "tan", "ate", "nat", "bat"]

    becomes groups equivalent to:
        [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]

    Complexity:
        O(n * m log m)
        where n is the number of words and m is the typical word length.
    """
    groups: dict[str, list[str]] = defaultdict(list)

    for word in words:
        key = "".join(sorted(word))
        groups[key].append(word)

    return list(groups.values())


def group_anagrams_frequency(words: Sequence[str]) -> list[list[str]]:
    """
    Group anagrams using a frequency tuple as the dictionary key.

    For lowercase ASCII words, the tuple contains 26 integer counts.
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in words:
        frequencies = [0] * 26

        for character in word.lower():
            if not ("a" <= character <= "z"):
                raise ValueError(
                    "group_anagrams_frequency expects lowercase ASCII letters."
                )
            frequencies[ord(character) - ord("a")] += 1

        groups[tuple(frequencies)].append(word)

    return list(groups.values())


def demonstrate_grouping() -> None:
    print_section("6. Group Anagrams")

    words = [
        "eat",
        "tea",
        "tan",
        "ate",
        "nat",
        "bat",
        "listen",
        "silent",
        "enlist",
    ]

    print("Input:")
    print(words)

    print("\nSorting-key groups:")
    print(group_anagrams_sorting(words))

    print("\nFrequency-key groups:")
    print(group_anagrams_frequency(words))


# ============================================================================
# 8. ANAGRAM DETECTION
# ============================================================================

def find_anagram_pairs(words: Sequence[str]) -> list[tuple[str, str]]:
    """
    Find every pair of words that are anagrams.

    This implementation groups first, then generates pairs inside each group.

    If a group has r members, it contributes r * (r - 1) / 2 pairs.
    """
    groups = group_anagrams_sorting(words)
    pairs: list[tuple[str, str]] = []

    for group in groups:
        for index in range(len(group)):
            for other_index in range(index + 1, len(group)):
                pairs.append((group[index], group[other_index]))

    return pairs


def find_anagram_pairs_naive(words: Sequence[str]) -> list[tuple[str, str]]:
    """
    Baseline O(n^2) pairwise comparison.

    Useful for understanding why grouping is preferable for large collections.
    """
    pairs: list[tuple[str, str]] = []

    for index in range(len(words)):
        for other_index in range(index + 1, len(words)):
            if are_anagrams_counter(words[index], words[other_index]):
                pairs.append((words[index], words[other_index]))

    return pairs


# ============================================================================
# 9. ANAGRAM WINDOWS
# ============================================================================

def find_anagram_windows(
    text: str,
    pattern: str,
) -> list[int]:
    """
    Find all starting indices where a substring of text is an anagram
    of pattern.

    Example:
        text    = "cbaebabacd"
        pattern = "abc"

    result:
        [0, 6]

    This uses a fixed-size sliding window.

    Complexity:
        Time: O(n)
        Space: O(k)

    The window has exactly len(pattern) characters.
    """
    if not pattern:
        return []

    if len(pattern) > len(text):
        return []

    pattern_counts = Counter(pattern)
    window_counts = Counter(text[: len(pattern)])
    result: list[int] = []

    if window_counts == pattern_counts:
        result.append(0)

    window_size = len(pattern)

    for right in range(window_size, len(text)):
        entering_character = text[right]
        leaving_character = text[right - window_size]

        window_counts[entering_character] += 1
        window_counts[leaving_character] -= 1

        if window_counts[leaving_character] == 0:
            del window_counts[leaving_character]

        if window_counts == pattern_counts:
            result.append(right - window_size + 1)

    return result


def find_anagram_windows_optimized(
    text: str,
    pattern: str,
) -> list[int]:
    """
    Optimized ASCII sliding-window solution.

    Instead of comparing two dictionaries for every window, maintain a
    'difference count' describing how far the current window is from the
    pattern.

    The variable `matches` records how many of the 26 character counts
    currently match exactly.
    """
    if not pattern or len(pattern) > len(text):
        return []

    text = text.lower()
    pattern = pattern.lower()

    if not (
        all("a" <= character <= "z" for character in text)
        and all("a" <= character <= "z" for character in pattern)
    ):
        raise ValueError("This optimized implementation accepts ASCII letters.")

    pattern_counts = [0] * 26
    window_counts = [0] * 26

    for character in pattern:
        pattern_counts[ord(character) - ord("a")] += 1

    for character in text[: len(pattern)]:
        window_counts[ord(character) - ord("a")] += 1

    matches = sum(
        pattern_counts[index] == window_counts[index]
        for index in range(26)
    )

    result: list[int] = []
    window_size = len(pattern)

    if matches == 26:
        result.append(0)

    def update(index: int, delta: int) -> None:
        nonlocal matches

        before_equal = pattern_counts[index] == window_counts[index]

        window_counts[index] += delta

        after_equal = pattern_counts[index] == window_counts[index]

        if before_equal and not after_equal:
            matches -= 1
        elif not before_equal and after_equal:
            matches += 1

    for right in range(window_size, len(text)):
        entering_index = ord(text[right]) - ord("a")
        leaving_index = ord(text[right - window_size]) - ord("a")

        update(entering_index, 1)
        update(leaving_index, -1)

        if matches == 26:
            result.append(right - window_size + 1)

    return result


def demonstrate_anagram_windows() -> None:
    print_section("7. Anagram Windows")

    cases = [
        ("cbaebabacd", "abc"),
        ("abab", "ab"),
        ("baa", "aa"),
        ("abcdef", "xyz"),
        ("aaaaa", "aa"),
    ]

    for text, pattern in cases:
        print(
            f"text={text!r:15} pattern={pattern!r:8} "
            f"-> {find_anagram_windows(text, pattern)}"
        )

    print("\nOptimized fixed-alphabet implementation:")
    print(find_anagram_windows_optimized("cbaebabacd", "abc"))


# ============================================================================
# 10. FREQUENCY MATCHING
# ============================================================================

def contains_permutation(text: str, pattern: str) -> bool:
    """
    Return True when text contains a substring that is an anagram
    of pattern.

    This is equivalent to asking whether a permutation of pattern occurs
    inside text.
    """
    return bool(find_anagram_windows(text, pattern))


def frequency_difference(
    first: str,
    second: str,
) -> dict[str, int]:
    """
    Return first - second character frequencies.

    A zero value means the character occurs equally often in both strings.
    """
    result = Counter(first)
    result.subtract(Counter(second))
    return {character: count for character, count in result.items() if count}


def demonstrate_frequency_matching() -> None:
    print_section("8. Frequency Matching")

    first = "abbccc"
    second = "abcc"

    print_result("First string", first)
    print_result("Second string", second)
    print_result("Frequency difference", frequency_difference(first, second))
    print_result(
        "Contains permutation",
        contains_permutation("oidbcaf", "abc"),
    )


# ============================================================================
# 11. ANAGRAM WINDOWS WITH NORMALIZATION
# ============================================================================

def find_normalized_anagram_windows(
    text: str,
    pattern: str,
) -> list[int]:
    """
    Find anagram windows after normalization.

    Because normalization can change the number of characters and their
    relationship with original indices, this function returns positions
    in the normalized text, not positions in the original raw string.
    """
    normalized_text = normalize_letters_only(text)
    normalized_pattern = normalize_letters_only(pattern)

    return find_anagram_windows(normalized_text, normalized_pattern)


# ============================================================================
# 12. STREAMING FREQUENCY COMPARISON
# ============================================================================

class FrequencyMap:
    """
    Mutable frequency map with increment/decrement operations.

    This abstraction is useful when a problem repeatedly modifies a
    character window rather than rebuilding a Counter from scratch.
    """

    def __init__(self, values: Iterable[str] = ()) -> None:
        self._counts: dict[str, int] = {}
        for value in values:
            self.add(value)

    def add(self, value: str) -> None:
        self._counts[value] = self._counts.get(value, 0) + 1

    def remove(self, value: str) -> None:
        if value not in self._counts:
            raise KeyError(f"Cannot remove absent character {value!r}.")

        self._counts[value] -= 1

        if self._counts[value] == 0:
            del self._counts[value]

    def get(self, value: str) -> int:
        return self._counts.get(value, 0)

    def as_dict(self) -> dict[str, int]:
        return dict(self._counts)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrequencyMap):
            return NotImplemented
        return self._counts == other._counts

    def __repr__(self) -> str:
        return f"FrequencyMap({self._counts!r})"


def demonstrate_frequency_map_class() -> None:
    print_section("9. Reusable FrequencyMap Abstraction")

    frequencies = FrequencyMap("banana")
    print_result("Initial frequencies", frequencies.as_dict())

    frequencies.remove("a")
    frequencies.add("x")

    print_result("After remove('a')", frequencies.as_dict())
    print_result("After add('x')", frequencies.as_dict())

    first = FrequencyMap("listen")
    second = FrequencyMap("silent")

    print_result("listen == silent frequency maps", first == second)


# ============================================================================
# 13. ANAGRAM INDEX
# ============================================================================

@dataclass(frozen=True)
class AnagramIndex:
    """
    Immutable-style index of normalized anagram groups.

    The index allows repeated group lookup without recomputing every
    relationship from scratch.
    """

    groups: dict[str, tuple[str, ...]]

    @classmethod
    def build(cls, words: Iterable[str]) -> "AnagramIndex":
        grouped: dict[str, list[str]] = defaultdict(list)

        for word in words:
            normalized = normalize_letters_only(word)
            grouped["".join(sorted(normalized))].append(word)

        immutable_groups = {
            key: tuple(values)
            for key, values in grouped.items()
        }

        return cls(immutable_groups)

    def find(self, word: str) -> tuple[str, ...]:
        normalized = normalize_letters_only(word)
        key = "".join(sorted(normalized))
        return self.groups.get(key, ())


def demonstrate_anagram_index() -> None:
    print_section("10. Reusable Anagram Index")

    dictionary = [
        "listen",
        "silent",
        "enlist",
        "stone",
        "tones",
        "notes",
        "python",
        "typhon",
    ]

    index = AnagramIndex.build(dictionary)

    for query in ["listen", "tones", "python", "unknown"]:
        print_result(query, index.find(query))


# ============================================================================
# 14. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print_section("11. Edge Cases")

    cases = [
        ("", ""),
        ("", "a"),
        ("a", ""),
        ("a", "a"),
        ("a", "A"),
        ("aa", "a"),
        ("abc", "abcd"),
        ("a b", "ab"),
        ("😊", "😊"),
        ("é", "e"),
        ("ß", "ss"),
    ]

    for first, second in cases:
        result = are_anagrams_counter(first, second)
        normalized_result = are_anagrams_counter(
            first,
            second,
            normalize=True,
        )

        print(
            f"{first!r:10} vs {second!r:10} "
            f"exact={result!s:<5} normalized={normalized_result}"
        )


# ============================================================================
# 15. ERROR HANDLING
# ============================================================================

def demonstrate_error_handling() -> None:
    print_section("12. Error Handling")

    try:
        are_anagrams_ascii_array("hello!", "olleh!")
    except ValueError as error:
        print_result("Expected validation error", error)

    try:
        group_anagrams_frequency(["eat", "tea", "é"])
    except ValueError as error:
        print_result("Expected grouping error", error)

    frequency_map = FrequencyMap("abc")

    try:
        frequency_map.remove("z")
    except KeyError as error:
        print_result("Expected frequency-map error", error)


# ============================================================================
# 16. TESTING
# ============================================================================

def run_assertion_tests() -> None:
    print_section("13. Automated Assertions")

    positive_cases = [
        ("listen", "silent"),
        ("triangle", "integral"),
        ("evil", "vile"),
        ("anagram", "nagaram"),
        ("aabbcc", "abcabc"),
        ("", ""),
    ]

    negative_cases = [
        ("hello", "world"),
        ("abc", "abd"),
        ("a", "aa"),
        ("abc", "abcd"),
    ]

    for first, second in positive_cases:
        assert are_anagrams_sorting(first, second)
        assert are_anagrams_frequency_map(first, second)
        assert are_anagrams_counter(first, second)

    for first, second in negative_cases:
        assert not are_anagrams_sorting(first, second)
        assert not are_anagrams_frequency_map(first, second)
        assert not are_anagrams_counter(first, second)

    assert are_anagrams_ascii_array("listen", "silent")
    assert not are_anagrams_ascii_array("listen", "silentx")

    assert find_anagram_windows("cbaebabacd", "abc") == [0, 6]
    assert find_anagram_windows("abab", "ab") == [0, 1, 2]
    assert find_anagram_windows("", "a") == []
    assert find_anagram_windows("abc", "") == []

    assert find_anagram_windows_optimized("cbaebabacd", "abc") == [0, 6]

    grouped = group_anagrams_sorting(
        ["eat", "tea", "tan", "ate", "nat", "bat"]
    )
    normalized_groups = {frozenset(group) for group in grouped}

    expected_groups = {
        frozenset({"eat", "tea", "ate"}),
        frozenset({"tan", "nat"}),
        frozenset({"bat"}),
    }

    assert normalized_groups == expected_groups

    print("All assertions passed.")


# ============================================================================
# 17. PERFORMANCE BENCHMARK
# ============================================================================

def benchmark_methods() -> None:
    print_section("14. Small Performance Benchmark")

    first = ("abcdefghijklmnopqrstuvwxyz" * 2_000)
    second = "".join(reversed(first))

    methods = [
        ("Sorting", lambda: are_anagrams_sorting(first, second)),
        ("Dictionary", lambda: are_anagrams_frequency_map(first, second)),
        ("Counter", lambda: are_anagrams_counter(first, second)),
    ]

    for name, function in methods:
        start = perf_counter()
        result = function()
        elapsed = perf_counter() - start

        print(
            f"{name:<15} result={result!s:<5} "
            f"time={elapsed:.6f} seconds"
        )


# ============================================================================
# 18. PRACTICAL CASE STUDY
# ============================================================================

def detect_duplicate_signatures(
    values: Sequence[str],
) -> dict[str, list[str]]:
    """
    Build signatures for normalized strings.

    Such signatures can be used for duplicate/anagram detection in
    text-processing systems.
    """
    result: dict[str, list[str]] = defaultdict(list)

    for value in values:
        normalized = normalize_letters_only(value)
        signature = "".join(sorted(normalized))
        result[signature].append(value)

    return dict(result)


def demonstrate_case_study() -> None:
    print_section("15. Practical Case Study: Text Record Matching")

    records = [
        "Debit Card",
        "Credit Card",
        "Bad Credit",
        "Debitcard",
        "card debit",
        "Secure Login",
        "Login Secure",
    ]

    signatures = detect_duplicate_signatures(records)

    for signature, values in signatures.items():
        if len(values) > 1:
            print(f"Signature {signature!r}:")
            for value in values:
                print(f"  - {value}")


# ============================================================================
# 19. ADVANCED DISCUSSION THROUGH EXECUTABLE DATA
# ============================================================================

def demonstrate_complexity_examples() -> None:
    print_section("16. Complexity Examples")

    examples = {
        "Single pair, sorting": "O(n log n)",
        "Single pair, frequency map": "O(n) average",
        "Fixed alphabet frequency array": "O(n)",
        "Grouping n words by sorting": "O(n * m log m)",
        "Grouping n words by fixed frequency": "O(n * m)",
        "Naive pairwise comparison": "O(n² * m)",
        "Sliding-window anagram search": "O(n)",
    }

    for technique, complexity in examples.items():
        print(f"{technique:<45}: {complexity}")


# ============================================================================
# 20. STUDY CHECKLIST
# ============================================================================

def print_study_checklist() -> None:
    print_section("17. Study Checklist")

    checklist = [
        "Understand the definition of an anagram.",
        "Know when normalization changes the problem definition.",
        "Implement sorting-based checking.",
        "Implement dictionary frequency checking.",
        "Use Counter for concise frequency counting.",
        "Understand fixed-size frequency arrays.",
        "Group strings using canonical signatures.",
        "Detect anagrams inside a larger text.",
        "Understand fixed-size sliding windows.",
        "Understand entering and leaving characters.",
        "Use frequency matching instead of repeatedly sorting windows.",
        "Distinguish ASCII constraints from Unicode requirements.",
        "Analyze time and space complexity.",
        "Handle empty strings and mismatched lengths.",
        "Validate unsupported characters when necessary.",
        "Use assertions to test implementations.",
    ]

    for index, item in enumerate(checklist, start=1):
        print(f"{index:02d}. {item}")


# ============================================================================
# 21. MAIN PROGRAM
# ============================================================================

def main() -> None:
    print_section("Day 23 — Anagrams")
    print("A complete study and executable demonstration of anagram algorithms.")

    explain_anagram()
    demonstrate_normalization()
    demonstrate_sorting_method()
    demonstrate_frequency_method()
    compare_methods()

    print_section("ASCII Array Demonstration")
    print_result(
        "'listen' and 'silent'",
        are_anagrams_ascii_array("listen", "silent"),
    )
    print_result(
        "'rat' and 'car'",
        are_anagrams_ascii_array("rat", "car"),
    )

    demonstrate_grouping()

    print_section("Anagram Pair Detection")
    words = ["listen", "silent", "enlist", "stone", "tones", "apple"]
    print_result("Grouped pairs", find_anagram_pairs(words))
    print_result("Naive pair detection", find_anagram_pairs_naive(words))

    demonstrate_anagram_windows()
    demonstrate_frequency_matching()
    demonstrate_frequency_map_class()
    demonstrate_anagram_index()
    demonstrate_edge_cases()
    demonstrate_error_handling()
    run_assertion_tests()
    benchmark_methods()
    demonstrate_case_study()
    demonstrate_complexity_examples()
    print_study_checklist()

    print_section("Program Completed")
    print("All demonstrations and validation tests completed successfully.")


if __name__ == "__main__":
    main()
