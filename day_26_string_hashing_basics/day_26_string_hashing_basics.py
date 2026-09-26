"""
Day 26 — String Hashing Basics
================================

A standalone study program covering string hashing from beginner to advanced
foundations.

Topics demonstrated:
- Hashing concept
- Hash representation
- Deterministic hashing
- Polynomial rolling hash
- Prefix hashes
- O(1) substring-hash queries
- Collision detection and collision handling
- Double hashing
- Hash normalization
- String equality verification
- Rabin-Karp pattern matching
- Duplicate substring detection
- Longest repeated substring using hashing + binary search
- Practical applications
- Edge cases
- Complexity and performance considerations
- Security distinction between ordinary algorithmic hashing and cryptographic hashing
- Mixed assessment problems

No third-party packages are required.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


# ---------------------------------------------------------------------------
# 1. BASIC HASHING CONCEPT
# ---------------------------------------------------------------------------

def simple_character_sum_hash(text: str) -> int:
    """
    A deliberately simple hash.

    Each character contributes its Unicode code point.

    This demonstrates the idea of mapping a string to a numeric
    representation, but it is NOT a good general-purpose string hash because
    many different strings produce the same result.

    Example:
        "abc" -> ord('a') + ord('b') + ord('c') = 294
        "acb" -> the same value = 294

    Therefore, this function illustrates collisions very clearly.
    """
    return sum(ord(character) for character in text)


def demonstrate_basic_hashing() -> None:
    print("\n" + "=" * 78)
    print("1. BASIC HASHING")
    print("=" * 78)

    examples = ["abc", "acb", "hello", "world", ""]
    for text in examples:
        print(f"{text!r:10} -> {simple_character_sum_hash(text)}")

    print("\nCollision example:")
    first = "abc"
    second = "acb"
    print(
        f"{first!r} and {second!r} have the same character-sum hash: "
        f"{simple_character_sum_hash(first) == simple_character_sum_hash(second)}"
    )


# ---------------------------------------------------------------------------
# 2. HASH REPRESENTATION
# ---------------------------------------------------------------------------

def polynomial_hash(
    text: str,
    base: int = 257,
    modulus: int = 1_000_000_007,
) -> int:
    """
    Compute a polynomial rolling hash.

    For characters c0, c1, ..., cn-1:

        H = (((c0 * base + c1) * base + c2) ... ) mod modulus

    Equivalently:

        H = c0 * base^(n-1) + c1 * base^(n-2) + ... + cn-1

    The modulus keeps the number bounded.

    Important:
    - The result is deterministic for fixed parameters.
    - A collision is possible because infinitely many strings map into a
      finite set of hash values.
    - This is suitable for algorithmic techniques, not password storage.
    """
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if base <= 0:
        raise ValueError("base must be positive")

    hash_value = 0
    for character in text:
        hash_value = (hash_value * base + ord(character)) % modulus

    return hash_value


def demonstrate_polynomial_hash() -> None:
    print("\n" + "=" * 78)
    print("2. POLYNOMIAL STRING HASH")
    print("=" * 78)

    for text in ["", "a", "abc", "hello", "Hello", "hello!"]:
        value = polynomial_hash(text)
        print(f"{text!r:10} -> {value}")


# ---------------------------------------------------------------------------
# 3. A REUSABLE ROLLING-HASH CLASS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HashParameters:
    base: int
    modulus: int


class RollingHash:
    """
    Prefix-hash data structure.

    For a string s of length n, store:

        prefix[i] = hash(s[0:i])

    and:

        power[i] = base^i mod modulus

    A substring hash can then be calculated in O(1).

    This is one of the most important practical uses of string hashing.
    """

    def __init__(
        self,
        text: str,
        base: int = 911382323,
        modulus: int = 972663749,
    ) -> None:
        if modulus <= 1:
            raise ValueError("modulus must be greater than 1")
        if base <= 0 or base >= modulus:
            raise ValueError("base must be positive and smaller than modulus")

        self.text = text
        self.parameters = HashParameters(base, modulus)

        self.prefix = [0] * (len(text) + 1)
        self.power = [1] * (len(text) + 1)

        for index, character in enumerate(text):
            code = ord(character)
            self.prefix[index + 1] = (
                self.prefix[index] * base + code
            ) % modulus
            self.power[index + 1] = (
                self.power[index] * base
            ) % modulus

    def substring_hash(self, left: int, right: int) -> int:
        """
        Return the hash of text[left:right].

        The interval is half-open:
            left is included
            right is excluded

        Complexity: O(1)
        """
        if not (0 <= left <= right <= len(self.text)):
            raise IndexError("substring bounds are invalid")

        result = (
            self.prefix[right]
            - self.prefix[left] * self.power[right - left]
        ) % self.parameters.modulus

        return result

    def equal_substrings(
        self,
        first_left: int,
        first_right: int,
        second_left: int,
        second_right: int,
        verify: bool = True,
    ) -> bool:
        """
        Compare two substrings.

        Hash equality is extremely useful as a fast filter.

        If verify=True, actual substring equality is checked after the hashes
        match. This makes the method logically exact even if a collision
        occurs.
        """
        first_length = first_right - first_left
        second_length = second_right - second_left

        if first_length != second_length:
            return False

        first_hash = self.substring_hash(first_left, first_right)
        second_hash = self.substring_hash(second_left, second_right)

        if first_hash != second_hash:
            return False

        if verify:
            return (
                self.text[first_left:first_right]
                == self.text[second_left:second_right]
            )

        return True


def demonstrate_prefix_hashes() -> None:
    print("\n" + "=" * 78)
    print("3. PREFIX HASHES AND O(1) SUBSTRING HASHING")
    print("=" * 78)

    text = "abracadabra"
    rolling = RollingHash(text)

    print(f"Text: {text!r}")
    print("Prefix hashes:")
    for index, value in enumerate(rolling.prefix):
        print(f"prefix[{index:2}] = {value}")

    first = "abra"
    second = "abra"

    first_position = text.find(first)
    second_position = text.rfind(second)

    print(
        f"\nComparing {first!r} at positions "
        f"{first_position}:{first_position + len(first)} and "
        f"{second!r} at positions "
        f"{second_position}:{second_position + len(second)}"
    )

    print(
        "Equal:",
        rolling.equal_substrings(
            first_position,
            first_position + len(first),
            second_position,
            second_position + len(second),
        ),
    )


# ---------------------------------------------------------------------------
# 4. COLLISIONS
# ---------------------------------------------------------------------------

def find_character_sum_collisions(
    alphabet: str = "abcd",
    maximum_length: int = 4,
) -> list[tuple[str, str, int]]:
    """
    Find distinct strings that collide under the intentionally weak
    character-sum hash.
    """
    by_hash: dict[int, list[str]] = defaultdict(list)

    def generate(current: str, remaining: int) -> None:
        if current:
            by_hash[simple_character_sum_hash(current)].append(current)

        if remaining == 0:
            return

        for character in alphabet:
            generate(current + character, remaining - 1)

    generate("", maximum_length)

    collisions: list[tuple[str, str, int]] = []

    for hash_value, strings in by_hash.items():
        unique_strings = list(dict.fromkeys(strings))
        if len(unique_strings) >= 2:
            collisions.append(
                (unique_strings[0], unique_strings[1], hash_value)
            )

    return collisions


def demonstrate_collisions() -> None:
    print("\n" + "=" * 78)
    print("4. COLLISIONS")
    print("=" * 78)

    collisions = find_character_sum_collisions()

    for first, second, hash_value in collisions[:8]:
        print(
            f"{first!r} and {second!r} -> collision at hash {hash_value}"
        )

    print(
        "\nA collision does not mean hashing is broken. "
        "It means multiple inputs can map to one finite hash space."
    )


# ---------------------------------------------------------------------------
# 5. DOUBLE HASHING
# ---------------------------------------------------------------------------

class DoubleRollingHash:
    """
    Two independent polynomial hashes.

    A pair:

        (hash_1, hash_2)

    creates a much larger effective hash space than either hash alone.

    This greatly reduces accidental collision probability in algorithmic
    applications, but it is still not a mathematical proof of equality.
    """

    def __init__(
        self,
        text: str,
        first: HashParameters = HashParameters(911382323, 972663749),
        second: HashParameters = HashParameters(97266353, 1_000_000_007),
    ) -> None:
        self.text = text
        self.first = RollingHash(text, first.base, first.modulus)
        self.second = RollingHash(text, second.base, second.modulus)

    def substring_hash(
        self,
        left: int,
        right: int,
    ) -> tuple[int, int]:
        return (
            self.first.substring_hash(left, right),
            self.second.substring_hash(left, right),
        )

    def equal_substrings(
        self,
        first_left: int,
        first_right: int,
        second_left: int,
        second_right: int,
        verify: bool = True,
    ) -> bool:
        if first_right - first_left != second_right - second_left:
            return False

        if self.substring_hash(first_left, first_right) != (
            self.substring_hash(second_left, second_right)
        ):
            return False

        if verify:
            return (
                self.text[first_left:first_right]
                == self.text[second_left:second_right]
            )

        return True


def demonstrate_double_hashing() -> None:
    print("\n" + "=" * 78)
    print("5. DOUBLE HASHING")
    print("=" * 78)

    text = "the quick brown fox jumps over the lazy dog"
    hasher = DoubleRollingHash(text)

    left = 4
    right = 9

    print(f"Substring: {text[left:right]!r}")
    print(f"Hash pair: {hasher.substring_hash(left, right)}")

    print(
        "Same substring comparison:",
        hasher.equal_substrings(left, right, left, right),
    )


# ---------------------------------------------------------------------------
# 6. HASH-BASED STRING EQUALITY
# ---------------------------------------------------------------------------

def hash_based_equality(
    first: str,
    second: str,
    verify: bool = True,
) -> bool:
    """
    Compare two strings using hashing.

    This is useful when strings are long and hashes have already been
    computed or when many comparisons are required.

    For a one-off comparison of Python strings, direct equality is usually
    preferable because Python's native string comparison is already highly
    optimized.
    """
    if len(first) != len(second):
        return False

    first_hash = DoubleRollingHash(first).substring_hash(0, len(first))
    second_hash = DoubleRollingHash(second).substring_hash(0, len(second))

    if first_hash != second_hash:
        return False

    if verify:
        return first == second

    return True


def demonstrate_string_equality() -> None:
    print("\n" + "=" * 78)
    print("6. HASH-BASED STRING EQUALITY")
    print("=" * 78)

    pairs = [
        ("algorithm", "algorithm"),
        ("algorithm", "algorithms"),
        ("abc", "acb"),
        ("", ""),
        ("", "a"),
    ]

    for first, second in pairs:
        print(
            f"{first!r:15} == {second!r:15} -> "
            f"{hash_based_equality(first, second)}"
        )


# ---------------------------------------------------------------------------
# 7. RABIN-KARP PATTERN MATCHING
# ---------------------------------------------------------------------------

def rabin_karp_search(
    text: str,
    pattern: str,
    base: int = 911382323,
    modulus: int = 972663749,
) -> list[int]:
    """
    Find every occurrence of pattern in text.

    The algorithm:
    1. Hash the pattern.
    2. Hash each text window of the same length.
    3. Compare hashes.
    4. Verify actual characters when hashes match.

    Expected time is close to O(n + m), where:
        n = len(text)
        m = len(pattern)

    Worst-case behavior can degrade if many collisions occur.
    """
    if pattern == "":
        return list(range(len(text) + 1))

    if len(pattern) > len(text):
        return []

    pattern_hash = polynomial_hash(pattern, base, modulus)
    rolling = RollingHash(text, base, modulus)

    pattern_length = len(pattern)
    matches: list[int] = []

    for start in range(len(text) - pattern_length + 1):
        end = start + pattern_length

        if rolling.substring_hash(start, end) == pattern_hash:
            if text[start:end] == pattern:
                matches.append(start)

    return matches


def demonstrate_rabin_karp() -> None:
    print("\n" + "=" * 78)
    print("7. RABIN-KARP PATTERN MATCHING")
    print("=" * 78)

    text = "abracadabra"
    patterns = ["abra", "cad", "xyz", "", "a"]

    for pattern in patterns:
        print(
            f"Pattern {pattern!r:6} -> positions "
            f"{rabin_karp_search(text, pattern)}"
        )


# ---------------------------------------------------------------------------
# 8. DUPLICATE SUBSTRING DETECTION
# ---------------------------------------------------------------------------

def has_duplicate_substring(
    text: str,
    length: int,
) -> bool:
    """
    Determine whether two equal substrings of a fixed length exist.

    Hashes are used as candidate identifiers, followed by direct verification
    to make the result exact.

    Complexity:
        O(n) hash queries for a fixed length.
    """
    if length < 0:
        raise ValueError("length cannot be negative")

    if length == 0:
        return True

    if length > len(text):
        return False

    hasher = DoubleRollingHash(text)
    seen: dict[tuple[int, int], list[int]] = defaultdict(list)

    for start in range(len(text) - length + 1):
        end = start + length
        key = hasher.substring_hash(start, end)

        for previous_start in seen[key]:
            if text[previous_start:end - (start - previous_start)] == text[start:end]:
                return True

        seen[key].append(start)

    return False


def duplicate_substring_positions(
    text: str,
    length: int,
) -> tuple[int, int] | None:
    """
    Return two positions containing the same substring, or None.
    """
    if length < 0:
        raise ValueError("length cannot be negative")
    if length == 0:
        return (0, 0)
    if length > len(text):
        return None

    hasher = DoubleRollingHash(text)
    seen: dict[tuple[int, int], list[int]] = defaultdict(list)

    for start in range(len(text) - length + 1):
        end = start + length
        key = hasher.substring_hash(start, end)

        for previous_start in seen[key]:
            if text[previous_start:previous_start + length] == text[start:end]:
                return previous_start, start

        seen[key].append(start)

    return None


def demonstrate_duplicate_detection() -> None:
    print("\n" + "=" * 78)
    print("8. DUPLICATE SUBSTRING DETECTION")
    print("=" * 78)

    text = "banana"

    for length in range(1, len(text) + 1):
        positions = duplicate_substring_positions(text, length)
        if positions:
            first, second = positions
            print(
                f"Length {length}: {text[first:first + length]!r} "
                f"appears at {first} and {second}"
            )
        else:
            print(f"Length {length}: no duplicate")


# ---------------------------------------------------------------------------
# 9. LONGEST REPEATED SUBSTRING
# ---------------------------------------------------------------------------

def longest_repeated_substring(text: str) -> str:
    """
    Find one longest repeated substring.

    Technique:
        binary search over substring length
        +
        hash-based duplicate detection

    A subtle point:
    The predicate "there exists a repeated substring of length L" is
    monotonic. If a repeated substring of length L exists, then a repeated
    substring of every smaller length exists.

    Complexity:
        O(n log n) expected with hashing.
    """
    if not text:
        return ""

    hasher = DoubleRollingHash(text)

    def find_duplicate(length: int) -> tuple[int, int] | None:
        if length == 0:
            return (0, 0)

        seen: dict[tuple[int, int], list[int]] = defaultdict(list)

        for start in range(len(text) - length + 1):
            key = hasher.substring_hash(start, start + length)

            for previous_start in seen[key]:
                if (
                    text[previous_start:previous_start + length]
                    == text[start:start + length]
                ):
                    return previous_start, start

            seen[key].append(start)

        return None

    low = 1
    high = len(text)
    best = ""

    while low <= high:
        middle = (low + high) // 2
        positions = find_duplicate(middle)

        if positions is not None:
            first, _ = positions
            best = text[first:first + middle]
            low = middle + 1
        else:
            high = middle - 1

    return best


def demonstrate_longest_repeated_substring() -> None:
    print("\n" + "=" * 78)
    print("9. LONGEST REPEATED SUBSTRING")
    print("=" * 78)

    for text in ["banana", "abracadabra", "aaaaa", "abcdef", "mississippi"]:
        result = longest_repeated_substring(text)
        print(f"{text!r:15} -> {result!r}")


# ---------------------------------------------------------------------------
# 10. NORMALIZED HASHING
# ---------------------------------------------------------------------------

def normalized_case_insensitive_hash(text: str) -> int:
    """
    Hash normalized text.

    Normalization is a policy decision:
    "Apple" and "apple" are distinct strings normally, but an application
    might intentionally treat them as equivalent.
    """
    normalized = text.casefold()
    return polynomial_hash(normalized)


def demonstrate_normalization() -> None:
    print("\n" + "=" * 78)
    print("10. NORMALIZATION")
    print("=" * 78)

    values = ["Apple", "apple", "APPLE", "ApPlE"]

    for value in values:
        print(
            f"{value!r:10} -> normalized hash "
            f"{normalized_case_insensitive_hash(value)}"
        )


# ---------------------------------------------------------------------------
# 11. PALINDROME CHECKING WITH HASHING
# ---------------------------------------------------------------------------

class BidirectionalStringHash:
    """
    Store forward and reversed hashes.

    This allows a substring to be compared with the corresponding substring
    in the reversed string.

    Direct character comparison is still needed if absolute correctness is
    required without accepting collision probability.
    """

    def __init__(self, text: str) -> None:
        self.text = text
        self.reversed_text = text[::-1]
        self.forward = DoubleRollingHash(text)
        self.backward = DoubleRollingHash(self.reversed_text)

    def is_palindrome(self, left: int, right: int) -> bool:
        if not (0 <= left <= right <= len(self.text)):
            raise IndexError("invalid substring bounds")

        length = right - left

        if length <= 1:
            return True

        forward_hash = self.forward.substring_hash(left, right)

        reverse_left = len(self.text) - right
        reverse_right = reverse_left + length

        backward_hash = self.backward.substring_hash(
            reverse_left,
            reverse_right,
        )

        if forward_hash != backward_hash:
            return False

        # Verification makes the final answer exact.
        return self.text[left:right] == self.text[left:right][::-1]


def demonstrate_palindrome_hashing() -> None:
    print("\n" + "=" * 78)
    print("11. PALINDROME CHECKING")
    print("=" * 78)

    text = "racecarannakayak"
    hasher = BidirectionalStringHash(text)

    examples = [
        (0, 7),
        (7, 10),
        (10, 16),
        (0, 5),
    ]

    for left, right in examples:
        print(
            f"{text[left:right]!r:12} -> "
            f"palindrome = {hasher.is_palindrome(left, right)}"
        )


# ---------------------------------------------------------------------------
# 12. HASH TABLE FOR STRING FREQUENCIES
# ---------------------------------------------------------------------------

def frequency_by_hash(
    words: Iterable[str],
) -> dict[tuple[int, int], list[str]]:
    """
    Group strings by double hash.

    This is useful for demonstrating a common hash-table pattern.

    The actual strings are retained in each bucket so collisions can be
    distinguished rather than silently treated as equal.
    """
    buckets: dict[tuple[int, int], list[str]] = defaultdict(list)

    for word in words:
        key = DoubleRollingHash(word).substring_hash(0, len(word))
        buckets[key].append(word)

    return dict(buckets)


def exact_frequency(words: Iterable[str]) -> dict[str, int]:
    """
    Python's built-in dictionary is the practical choice for exact string
    frequency counting.
    """
    frequencies: dict[str, int] = defaultdict(int)

    for word in words:
        frequencies[word] += 1

    return dict(frequencies)


def demonstrate_hash_table_usage() -> None:
    print("\n" + "=" * 78)
    print("12. PRACTICAL HASH-TABLE USAGE")
    print("=" * 78)

    words = [
        "apple",
        "banana",
        "apple",
        "orange",
        "banana",
        "apple",
    ]

    print("Exact frequencies:")
    for word, count in exact_frequency(words).items():
        print(f"{word:10} -> {count}")

    print("\nHash buckets:")
    buckets = frequency_by_hash(words)
    for hash_pair, bucket in buckets.items():
        print(f"{hash_pair} -> {bucket}")


# ---------------------------------------------------------------------------
# 13. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("13. EDGE CASES")
    print("=" * 78)

    cases = [
        "",
        "a",
        "aaaaaa",
        "123456789",
        "hello world",
        "A",
        "a",
        "é",
        "你好",
    ]

    for text in cases:
        print(
            f"{text!r:16} length={len(text):2} "
            f"hash={polynomial_hash(text)}"
        )

    print("\nPattern longer than text:")
    print(rabin_karp_search("abc", "abcdef"))

    print("\nEmpty pattern:")
    print(rabin_karp_search("abc", ""))

    print("\nSubstring boundaries:")
    rolling = RollingHash("abcdef")
    for left, right in [(0, 0), (0, 6), (2, 4), (6, 6)]:
        print(
            f"[{left}:{right}] -> "
            f"{rolling.substring_hash(left, right)}"
        )

    print("\nInvalid bounds:")
    try:
        rolling.substring_hash(-1, 2)
    except IndexError as error:
        print(f"Handled: {error}")


# ---------------------------------------------------------------------------
# 14. PERFORMANCE COMPARISON
# ---------------------------------------------------------------------------

def naive_substring_search(text: str, pattern: str) -> list[int]:
    """
    Straightforward pattern search.

    Complexity:
        O(n * m) in the worst case.
    """
    if pattern == "":
        return list(range(len(text) + 1))

    matches = []

    for start in range(len(text) - len(pattern) + 1):
        if text[start:start + len(pattern)] == pattern:
            matches.append(start)

    return matches


def compare_search_methods() -> None:
    print("\n" + "=" * 78)
    print("14. SEARCH METHOD COMPARISON")
    print("=" * 78)

    text = "ab" * 1000 + "needle" + "cd" * 1000
    pattern = "needle"

    naive_result = naive_substring_search(text, pattern)
    hashed_result = rabin_karp_search(text, pattern)

    print(f"Naive result:  {naive_result}")
    print(f"Hash result:   {hashed_result}")
    print(f"Results equal: {naive_result == hashed_result}")

    print(
        "\nFor production Python code, built-in string operations are often "
        "preferable to hand-written Rabin-Karp because the built-in "
        "implementation is heavily optimized."
    )


# ---------------------------------------------------------------------------
# 15. SECURITY DISTINCTION
# ---------------------------------------------------------------------------

def demonstrate_security_distinction() -> None:
    print("\n" + "=" * 78)
    print("15. ALGORITHMIC HASHING VS CRYPTOGRAPHIC HASHING")
    print("=" * 78)

    print(
        """
Algorithmic string hashing:
  - Optimized for fast comparisons.
  - Useful for substring algorithms.
  - Collisions are acceptable when handled correctly.
  - Polynomial rolling hashes are common.

Cryptographic hashing:
  - Designed for security properties such as preimage resistance.
  - Examples include SHA-256 and SHA-3.
  - Used for integrity verification and many security protocols.
  - Password storage requires a password-hashing/KDF scheme such as Argon2,
    scrypt, or bcrypt rather than a fast general-purpose hash.

Never treat a polynomial rolling hash as a password hash.
"""
    )


# ---------------------------------------------------------------------------
# 16. MIXED ASSESSMENT
# ---------------------------------------------------------------------------

def assessment_count_distinct_substrings(text: str) -> int:
    """
    Count distinct substrings.

    This educational implementation uses sets of actual strings for clarity.

    Complexity is O(n^3) in the worst case because creating slices and hashing
    them both have costs. More advanced solutions use suffix arrays,
    suffix automata, suffix trees, or carefully engineered rolling hashes.

    It is included as an assessment implementation rather than a claim that
    this is the optimal general algorithm.
    """
    distinct: set[str] = set()

    for left in range(len(text)):
        for right in range(left + 1, len(text) + 1):
            distinct.add(text[left:right])

    return len(distinct)


def assessment_longest_common_substring(
    first: str,
    second: str,
) -> str:
    """
    Find one longest common substring using dynamic programming.

    This assessment intentionally uses a different technique so that string
    hashing is not treated as the solution to every string problem.

    Complexity:
        Time:  O(n * m)
        Space: O(m)
    """
    if not first or not second:
        return ""

    previous = [0] * (len(second) + 1)
    best_length = 0
    best_end = 0

    for i, first_character in enumerate(first, start=1):
        current = [0] * (len(second) + 1)

        for j, second_character in enumerate(second, start=1):
            if first_character == second_character:
                current[j] = previous[j - 1] + 1

                if current[j] > best_length:
                    best_length = current[j]
                    best_end = i

        previous = current

    return first[best_end - best_length:best_end]


def assessment_find_repeated_words(sentence: str) -> dict[str, int]:
    """
    A practical hash-table assessment.

    This uses Python's built-in dictionary rather than manually implementing
    a hash table.
    """
    normalized_words = [
        word.strip(".,!?;:").casefold()
        for word in sentence.split()
    ]

    counts: dict[str, int] = defaultdict(int)

    for word in normalized_words:
        if word:
            counts[word] += 1

    return {
        word: count
        for word, count in counts.items()
        if count > 1
    }


def run_assessment() -> None:
    print("\n" + "=" * 78)
    print("16. MIXED ASSESSMENT")
    print("=" * 78)

    test_strings = ["ababa", "aaa", "abc", ""]
    for text in test_strings:
        print(
            f"Distinct substrings in {text!r}: "
            f"{assessment_count_distinct_substrings(text)}"
        )

    pairs = [
        ("abcdef", "zcdemf"),
        ("abc", "xyz"),
        ("banana", "ananas"),
    ]

    for first, second in pairs:
        print(
            f"Longest common substring of {first!r} and {second!r}: "
            f"{assessment_longest_common_substring(first, second)!r}"
        )

    sentence = "Hashing makes lookup fast, and hashing makes comparison useful."
    print(
        "Repeated words:",
        assessment_find_repeated_words(sentence),
    )


# ---------------------------------------------------------------------------
# 17. TESTS
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """
    Small self-contained assertions.

    These verify the central implementations and also demonstrate that
    algorithmic examples should be tested against edge cases.
    """
    assert polynomial_hash("") == 0
    assert simple_character_sum_hash("abc") == simple_character_sum_hash("acb")

    rolling = RollingHash("abcdef")
    assert rolling.substring_hash(0, 3) == polynomial_hash(
        "abc",
        rolling.parameters.base,
        rolling.parameters.modulus,
    )

    assert rolling.substring_hash(2, 5) == polynomial_hash(
        "cde",
        rolling.parameters.base,
        rolling.parameters.modulus,
    )

    assert rabin_karp_search("aaaaa", "aaa") == [0, 1, 2]
    assert rabin_karp_search("abcdef", "xyz") == []
    assert rabin_karp_search("", "") == [0]

    assert hash_based_equality("same", "same")
    assert not hash_based_equality("same", "different")

    assert longest_repeated_substring("aaaa") == "aaa"
    assert longest_repeated_substring("abcdef") == ""

    assert assessment_longest_common_substring("abcdef", "zcdemf") == "cde"

    print("\nAll self-tests passed.")


# ---------------------------------------------------------------------------
# 18. STUDY NOTES
# ---------------------------------------------------------------------------

def print_study_notes() -> None:
    print("\n" + "=" * 78)
    print("17. CORE STUDY NOTES")
    print("=" * 78)

    notes = [
        (
            "Hash function",
            "Maps an input into a bounded representation, normally a fixed-size "
            "integer or tuple of integers."
        ),
        (
            "Collision",
            "Two different inputs produce the same hash representation."
        ),
        (
            "Polynomial rolling hash",
            "Represents characters as coefficients in a polynomial and evaluates "
            "the polynomial modulo a chosen integer."
        ),
        (
            "Prefix hash",
            "Stores hashes of all prefixes so substring hashes can be derived "
            "without scanning every character."
        ),
        (
            "Double hashing",
            "Uses two independently parameterized hashes to reduce accidental "
            "collision probability."
        ),
        (
            "Verification",
            "Checks actual characters after a hash match when exact equality is "
            "required."
        ),
        (
            "Rabin-Karp",
            "Uses rolling hashes to search for pattern occurrences efficiently."
        ),
        (
            "Hash table",
            "Uses hashing to provide expected constant-time insertion and lookup "
            "under normal assumptions."
        ),
    ]

    for name, description in notes:
        print(f"{name}: {description}")


# ---------------------------------------------------------------------------
# 19. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    demonstrate_basic_hashing()
    demonstrate_polynomial_hash()
    demonstrate_prefix_hashes()
    demonstrate_collisions()
    demonstrate_double_hashing()
    demonstrate_string_equality()
    demonstrate_rabin_karp()
    demonstrate_duplicate_detection()
    demonstrate_longest_repeated_substring()
    demonstrate_normalization()
    demonstrate_palindrome_hashing()
    demonstrate_hash_table_usage()
    demonstrate_edge_cases()
    compare_search_methods()
    demonstrate_security_distinction()
    run_assessment()
    print_study_notes()
    run_tests()


if __name__ == "__main__":
    main()
