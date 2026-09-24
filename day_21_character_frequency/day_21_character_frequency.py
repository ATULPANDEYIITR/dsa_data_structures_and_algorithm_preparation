"""
Day 21 — Character Frequency
============================

A comprehensive study of character-frequency techniques:

1. Character counting
2. Frequency arrays
3. Dictionaries / maps
4. Most frequent character
5. Duplicate characters
6. Unique characters
7. Frequency comparison
8. Character grouping
9. Case sensitivity
10. Whitespace and punctuation
11. Unicode considerations
12. Algorithmic complexity
13. Validation and edge cases
14. Testing
15. Advanced frequency-based algorithms

The examples use only Python's standard library.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from string import ascii_lowercase
from typing import Dict, Iterable, List, Optional, Tuple


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def count_characters_basic(text: str) -> Dict[str, int]:
    """
    Count every character using a dictionary.

    Example:
        "banana" -> {'b': 1, 'a': 3, 'n': 2}

    Time: O(n)
    Space: O(k), where k is the number of distinct characters.
    """
    frequency: Dict[str, int] = {}

    for character in text:
        # get(character, 0) gives zero when the character has not appeared.
        frequency[character] = frequency.get(character, 0) + 1

    return frequency


def count_characters_defaultdict(text: str) -> Dict[str, int]:
    """Same idea using defaultdict."""
    frequency = defaultdict(int)

    for character in text:
        frequency[character] += 1

    return dict(frequency)


def count_characters_counter(text: str) -> Counter:
    """
    Python's Counter is specialized for frequency counting.
    """
    return Counter(text)


# ============================================================================
# 2. FREQUENCY ARRAY
# ============================================================================

def lowercase_frequency_array(text: str) -> List[int]:
    """
    Count lowercase English letters using a fixed-size frequency array.

    'a' maps to index 0.
    'b' maps to index 1.
    ...
    'z' maps to index 25.

    This is faster and more memory-predictable than a dictionary when the
    alphabet is known and small.

    Characters outside a-z are ignored.
    """
    frequency = [0] * 26

    for character in text:
        if "a" <= character <= "z":
            index = ord(character) - ord("a")
            frequency[index] += 1

    return frequency


def frequency_array_to_dict(frequency: List[int]) -> Dict[str, int]:
    """Convert a 26-element lowercase frequency array into a dictionary."""
    return {
        ascii_lowercase[index]: count
        for index, count in enumerate(frequency)
        if count > 0
    }


def lowercase_frequency_array_case_insensitive(text: str) -> List[int]:
    """Case-insensitive frequency array for English letters."""
    frequency = [0] * 26

    for character in text.lower():
        if "a" <= character <= "z":
            frequency[ord(character) - ord("a")] += 1

    return frequency


# ============================================================================
# 3. NORMALIZATION
# ============================================================================

def normalize_letters_only(text: str) -> str:
    """
    Keep only English alphabetic characters and convert them to lowercase.

    This creates a normalized representation useful for many frequency
    problems where spaces and punctuation should not matter.
    """
    return "".join(
        character.lower()
        for character in text
        if "a" <= character.lower() <= "z"
    )


def normalize_alphanumeric(text: str) -> str:
    """Keep ASCII letters and digits, converting letters to lowercase."""
    return "".join(
        character.lower()
        for character in text
        if ("a" <= character.lower() <= "z") or ("0" <= character <= "9")
    )


# ============================================================================
# 4. MOST FREQUENT CHARACTER
# ============================================================================

def most_frequent_character(text: str) -> Optional[Tuple[str, int]]:
    """
    Return the first character with the highest frequency.

    If there are ties, the character appearing earliest in the input wins.

    Example:
        "swiss" -> ('s', 3)

    Time: O(n)
    Space: O(k)
    """
    if not text:
        return None

    frequency = count_characters_basic(text)
    best_character = text[0]
    best_count = frequency[best_character]

    for character in text:
        if frequency[character] > best_count:
            best_character = character
            best_count = frequency[character]

    return best_character, best_count


def most_frequent_character_alphabetical_tie_break(
    text: str,
) -> Optional[Tuple[str, int]]:
    """
    Return the most frequent character.

    When several characters have the same frequency, the smallest character
    according to Python's normal string ordering is selected.
    """
    if not text:
        return None

    frequency = count_characters_basic(text)

    best_character = min(
        frequency,
        key=lambda character: (-frequency[character], character),
    )

    return best_character, frequency[best_character]


# ============================================================================
# 5. DUPLICATE AND UNIQUE CHARACTERS
# ============================================================================

def duplicate_characters(text: str) -> Dict[str, int]:
    """Return only characters appearing at least twice."""
    frequency = count_characters_basic(text)
    return {
        character: count
        for character, count in frequency.items()
        if count > 1
    }


def unique_characters(text: str) -> Dict[str, int]:
    """Return only characters appearing exactly once."""
    frequency = count_characters_basic(text)
    return {
        character: count
        for character, count in frequency.items()
        if count == 1
    }


def first_non_repeating_character(text: str) -> Optional[str]:
    """
    Return the first character whose frequency is exactly one.

    Two passes are used:
    1. Count all characters.
    2. Scan the original string to preserve positional order.
    """
    frequency = count_characters_basic(text)

    for character in text:
        if frequency[character] == 1:
            return character

    return None


def first_repeating_character(text: str) -> Optional[str]:
    """
    Return the first character encountered for which a previous occurrence
    exists.
    """
    seen = set()

    for character in text:
        if character in seen:
            return character
        seen.add(character)

    return None


# ============================================================================
# 6. FREQUENCY COMPARISON
# ============================================================================

def same_character_frequencies(text_a: str, text_b: str) -> bool:
    """
    Determine whether two strings have exactly the same character-frequency
    distribution.

    Order does not matter.

    "aabbc" and "bcaba" return True.
    """
    return Counter(text_a) == Counter(text_b)


def same_letter_frequencies(text_a: str, text_b: str) -> bool:
    """
    Case-insensitive comparison that ignores non-English letters.
    """
    normalized_a = normalize_letters_only(text_a)
    normalized_b = normalize_letters_only(text_b)

    return Counter(normalized_a) == Counter(normalized_b)


def can_form_anagram(text_a: str, text_b: str) -> bool:
    """
    An anagram requires equal character counts.

    Spaces and punctuation are ignored for this educational version.
    """
    return same_letter_frequencies(text_a, text_b)


def frequency_difference(
    text_a: str,
    text_b: str,
) -> Dict[str, int]:
    """
    Calculate count(text_a) - count(text_b).

    Positive values mean text_a contains more occurrences.
    Negative values mean text_b contains more occurrences.
    """
    difference = Counter(text_a)
    difference.subtract(Counter(text_b))

    return {
        character: count
        for character, count in difference.items()
        if count != 0
    }


# ============================================================================
# 7. CHARACTER GROUPING
# ============================================================================

def group_characters_by_frequency(
    text: str,
) -> Dict[int, List[str]]:
    """
    Group distinct characters according to their frequency.

    Example:
        "banana"
        {
            1: ['b'],
            2: ['n'],
            3: ['a']
        }
    """
    frequency = count_characters_basic(text)
    groups: Dict[int, List[str]] = defaultdict(list)

    for character, count in frequency.items():
        groups[count].append(character)

    for characters in groups.values():
        characters.sort()

    return dict(sorted(groups.items()))


def characters_sorted_by_frequency(text: str) -> List[Tuple[str, int]]:
    """
    Sort characters by decreasing frequency and then by character.

    Sorting makes this O(n + k log k), where k is the number of distinct
    characters.
    """
    frequency = count_characters_basic(text)

    return sorted(
        frequency.items(),
        key=lambda item: (-item[1], item[0]),
    )


# ============================================================================
# 8. ASCII FREQUENCY TABLE
# ============================================================================

def printable_ascii_frequency(text: str) -> Dict[str, int]:
    """
    Count printable ASCII characters.

    This demonstrates a larger fixed domain than the 26-letter alphabet.
    """
    frequency = [0] * 128

    for character in text:
        code = ord(character)

        if 0 <= code < 128 and character.isprintable():
            frequency[code] += 1

    return {
        chr(code): count
        for code, count in enumerate(frequency)
        if count > 0
    }


# ============================================================================
# 9. UNICODE
# ============================================================================

def unicode_character_frequency(text: str) -> Dict[str, int]:
    """
    Count Unicode code points using a dictionary.

    Unlike a 26-element English-letter array, Unicode has a much larger
    character space, so a dictionary is generally more practical.

    Note:
        A visible human-perceived character can consist of multiple Unicode
        code points. This function counts Python string characters/code points,
        not necessarily grapheme clusters.
    """
    return count_characters_basic(text)


# ============================================================================
# 10. WORD-FREQUENCY RELATIONSHIP
# ============================================================================

def character_frequency_without_whitespace(text: str) -> Dict[str, int]:
    """Count characters while excluding whitespace."""
    return Counter(
        character
        for character in text
        if not character.isspace()
    )


def letter_frequency(text: str) -> Dict[str, int]:
    """
    Count alphabetic Unicode characters case-insensitively.

    Unlike the ASCII-only normalization functions, str.isalpha() supports
    alphabetic Unicode characters.
    """
    frequency = Counter()

    for character in text:
        if character.isalpha():
            frequency[character.casefold()] += 1

    return dict(frequency)


# ============================================================================
# 11. DATA-STRUCTURE COMPARISON
# ============================================================================

def compare_counting_methods(text: str) -> Dict[str, Dict[str, int]]:
    """
    Demonstrate that different data structures can represent the same
    frequency information.
    """
    dictionary_result = count_characters_basic(text)
    counter_result = dict(count_characters_counter(text))

    array_result = frequency_array_to_dict(
        lowercase_frequency_array(text.lower())
    )

    return {
        "dictionary": dictionary_result,
        "counter": counter_result,
        "lowercase_array": array_result,
    }


# ============================================================================
# 12. ADVANCED: SLIDING WINDOW CHARACTER FREQUENCY
# ============================================================================

def longest_substring_without_repeating_characters(text: str) -> str:
    """
    Find the longest substring containing no repeated character.

    Sliding-window approach:
        - left marks the beginning of the current window.
        - last_seen records the most recent position.
        - when a duplicate occurs inside the current window, move left.

    Time: O(n)
    Space: O(k)
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
            best_length = current_length
            best_start = left

    return text[best_start:best_start + best_length]


# ============================================================================
# 13. ADVANCED: MINIMUM WINDOW CONTAINING REQUIRED FREQUENCIES
# ============================================================================

def minimum_window_with_required_characters(
    text: str,
    required: str,
) -> Optional[str]:
    """
    Find the smallest substring of text containing every character in
    required with at least the required frequency.

    Example:
        text = "ADOBECODEBANC"
        required = "ABC"
        result = "BANC"

    Time: O(n)
    Space: O(k)
    """
    if not required:
        return ""

    required_counts = Counter(required)
    window_counts = Counter()

    need = len(required_counts)
    formed = 0

    left = 0
    best_start = 0
    best_length = float("inf")

    for right, character in enumerate(text):
        window_counts[character] += 1

        if (
            character in required_counts
            and window_counts[character] == required_counts[character]
        ):
            formed += 1

        while formed == need:
            current_length = right - left + 1

            if current_length < best_length:
                best_length = current_length
                best_start = left

            left_character = text[left]
            window_counts[left_character] -= 1

            if (
                left_character in required_counts
                and window_counts[left_character]
                < required_counts[left_character]
            ):
                formed -= 1

            left += 1

    if best_length == float("inf"):
        return None

    return text[best_start:best_start + best_length]


# ============================================================================
# 14. FREQUENCY SIGNATURES
# ============================================================================

def frequency_signature(text: str) -> Tuple[Tuple[str, int], ...]:
    """
    Produce a hashable canonical representation of character frequencies.

    This can be used as a dictionary key when grouping anagrams.
    """
    return tuple(sorted(Counter(text).items()))


def group_anagrams(words: Iterable[str]) -> Dict[Tuple[Tuple[str, int], ...], List[str]]:
    """
    Group words having identical character-frequency signatures.
    """
    groups: Dict[Tuple[Tuple[str, int], ...], List[str]] = defaultdict(list)

    for word in words:
        groups[frequency_signature(word)].append(word)

    return dict(groups)


# ============================================================================
# 15. VALIDATION
# ============================================================================

def validate_text_input(text: object) -> None:
    """
    Validate input before frequency analysis.

    bool is rejected even though bool is technically a subclass of int;
    this function specifically expects textual data.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")


def safe_character_frequency(text: object) -> Dict[str, int]:
    """Validated public-facing frequency function."""
    validate_text_input(text)
    return count_characters_basic(text)


# ============================================================================
# 16. EDUCATIONAL DISPLAY HELPERS
# ============================================================================

def print_frequency_table(frequency: Dict[str, int]) -> None:
    """Display a deterministic frequency table."""
    if not frequency:
        print("(empty)")

    for character, count in sorted(frequency.items(), key=lambda item: item[0]):
        display_character = {
            " ": "<space>",
            "\t": "<tab>",
            "\n": "<newline>",
        }.get(character, character)

        print(f"{display_character!r:12} -> {count}")


def print_section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ============================================================================
# 17. TESTS
# ============================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""


def run_tests() -> List[TestResult]:
    """Run focused tests covering normal cases and edge cases."""
    tests: List[TestResult] = []

    def check(name: str, actual, expected) -> None:
        tests.append(
            TestResult(
                name=name,
                passed=actual == expected,
                detail=f"expected={expected!r}, actual={actual!r}",
            )
        )

    check(
        "Basic frequency",
        count_characters_basic("banana"),
        {"b": 1, "a": 3, "n": 2},
    )

    check(
        "Empty input",
        count_characters_basic(""),
        {},
    )

    check(
        "Most frequent",
        most_frequent_character("swiss"),
        ("s", 3),
    )

    check(
        "Unique characters",
        unique_characters("banana"),
        {"b": 1},
    )

    check(
        "Duplicate characters",
        duplicate_characters("banana"),
        {"a": 3, "n": 2},
    )

    check(
        "First non-repeating",
        first_non_repeating_character("swiss"),
        "w",
    )

    check(
        "First repeating",
        first_repeating_character("swiss"),
        "s",
    )

    check(
        "Frequency comparison",
        same_character_frequencies("aabbcc", "ccbbaa"),
        True,
    )

    check(
        "Anagram",
        can_form_anagram("Dormitory", "Dirty room"),
        True,
    )

    check(
        "Frequency difference",
        frequency_difference("aab", "ab"),
        {"a": 1},
    )

    check(
        "Grouping",
        group_characters_by_frequency("banana"),
        {1: ["b"], 2: ["n"], 3: ["a"]},
    )

    check(
        "Sliding window",
        longest_substring_without_repeating_characters("abcabcbb"),
        "abc",
    )

    check(
        "Minimum window",
        minimum_window_with_required_characters("ADOBECODEBANC", "ABC"),
        "BANC",
    )

    check(
        "Anagram grouping",
        group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]),
        {
            (("a", 1), ("e", 1), ("t", 1)): ["eat", "tea", "ate"],
            (("a", 1), ("n", 1), ("t", 1)): ["tan", "nat"],
            (("a", 1), ("b", 1), ("t", 1)): ["bat"],
        },
    )

    check(
        "Case-insensitive letters",
        letter_frequency("AaBbA!"),
        {"a": 3, "b": 2},
    )

    try:
        safe_character_frequency(123)
        tests.append(TestResult("Type validation", False, "Expected TypeError"))
    except TypeError:
        tests.append(TestResult("Type validation", True))

    return tests


# ============================================================================
# 18. MAIN EDUCATIONAL DEMONSTRATION
# ============================================================================

def main() -> None:
    print_section("DAY 21 — CHARACTER FREQUENCY")

    text = "banana"

    print("\nInput:", repr(text))

    print("\n1. Dictionary counting")
    print(count_characters_basic(text))

    print("\n2. defaultdict counting")
    print(count_characters_defaultdict(text))

    print("\n3. Counter counting")
    print(count_characters_counter(text))

    print("\n4. Lowercase frequency array")
    array = lowercase_frequency_array(text)
    print(array)
    print(frequency_array_to_dict(array))

    print("\n5. Frequency table")
    print_frequency_table(count_characters_basic(text))

    print("\n6. Most frequent character")
    print(most_frequent_character(text))

    print("\n7. Duplicate characters")
    print(duplicate_characters(text))

    print("\n8. Unique characters")
    print(unique_characters(text))

    print("\n9. First non-repeating character")
    print(first_non_repeating_character("swiss"))

    print("\n10. First repeating character")
    print(first_repeating_character("swiss"))

    print("\n11. Frequency comparison")
    print(same_character_frequencies("listen", "silent"))

    print("\n12. Letter-frequency comparison")
    print(can_form_anagram("The eyes", "They see"))

    print("\n13. Frequency difference")
    print(frequency_difference("aabbc", "abcc"))

    print("\n14. Character grouping")
    print(group_characters_by_frequency(text))

    print("\n15. Characters sorted by frequency")
    print(characters_sorted_by_frequency(text))

    print("\n16. Printable ASCII frequencies")
    print(printable_ascii_frequency("Hello!"))

    print("\n17. Unicode frequency")
    print(unicode_character_frequency("café café"))

    print("\n18. Character frequency without whitespace")
    print(character_frequency_without_whitespace("a b\tc a"))

    print("\n19. Normalized letters")
    print(normalize_letters_only("Hello, World! 123"))

    print("\n20. Longest substring without repetition")
    print(longest_substring_without_repeating_characters("abcabcbb"))

    print("\n21. Minimum required-character window")
    print(minimum_window_with_required_characters("ADOBECODEBANC", "ABC"))

    print("\n22. Anagram grouping")
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    grouped = group_anagrams(words)
    for signature, members in grouped.items():
        print(signature, "->", members)

    print("\n23. Data-structure comparison")
    comparison = compare_counting_methods("banana")
    for method, result in comparison.items():
        print(method, "->", result)

    print_section("EDGE CASES")

    edge_cases = [
        "",
        "a",
        "aaaaaa",
        "AaAa",
        "a a a",
        "123123",
        "!@!!",
        "ééa",
        "😀😀a",
    ]

    for case in edge_cases:
        print(
            f"{case!r:15} -> "
            f"{count_characters_basic(case)}"
        )

    print_section("COMPLEXITY REFERENCE")

    print("Dictionary counting:              O(n) time, O(k) space")
    print("Frequency array, fixed alphabet:  O(n) time, O(A) space")
    print("Most frequent character:          O(n) time, O(k) space")
    print("Duplicate detection:              O(n) time, O(k) space")
    print("Frequency comparison:              O(n + m) expected time")
    print("Frequency sorting:                 O(n + k log k) time")
    print("Sliding-window unique substring:  O(n) time, O(k) space")
    print("Minimum-character window:          O(n) time, O(k) space")

    print_section("RUNNING TESTS")

    results = run_tests()
    passed = sum(result.passed for result in results)

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        if result.detail and not result.passed:
            print(f"       {result.detail}")

    print(f"\n{passed}/{len(results)} tests passed.")

    if passed != len(results):
        raise AssertionError("One or more educational tests failed.")


if __name__ == "__main__":
    main()
