"""
Day 20 — String Fundamentals
=============================

A comprehensive standalone study program covering:

Fundamentals
- Characters
- String indexing
- Traversal
- Concatenation
- Comparison
- Conversion
- Case conversion

Practice
- Reverse a string
- Count characters
- Remove spaces
- Change case
- Count vowels
- Find the first unique character
- Count words

The examples progress from basic operations to validation, Unicode considerations,
frequency analysis, normalization, and a small text-analysis case study.

Python strings are immutable Unicode sequences. Indexing returns a one-character
string, and slicing creates another string.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Basic string concepts
# ---------------------------------------------------------------------------

def demonstrate_characters() -> None:
    """Demonstrate characters and strings."""
    print("\n=== 1. Characters and strings ===")

    character = "A"
    word = "Python"
    sentence = "String fundamentals are important."

    print("Character:", character)
    print("Word:", word)
    print("Sentence:", sentence)
    print("Character type:", type(character).__name__)
    print("String type:", type(word).__name__)

    # Python does not have a separate built-in char type.
    # A single character is simply a string whose length is one.
    print("Length of character:", len(character))
    print("Length of word:", len(word))

    # Unicode characters are also strings.
    unicode_text = "café भारत 日本"
    print("Unicode text:", unicode_text)
    print("Unicode character count:", len(unicode_text))


def demonstrate_indexing_and_slicing() -> None:
    """Demonstrate positive and negative indexing and slicing."""
    print("\n=== 2. Indexing and slicing ===")

    text = "PYTHON"

    print("Text:", text)
    print("Index 0:", text[0])
    print("Index 1:", text[1])
    print("Index 5:", text[5])

    # Negative indexes count from the end.
    print("Index -1:", text[-1])
    print("Index -2:", text[-2])

    # Slicing uses start:stop and excludes stop.
    print("First three:", text[:3])
    print("From index 2:", text[2:])
    print("Indexes 1 through 4:", text[1:5])
    print("Every second character:", text[::2])
    print("Reversed:", text[::-1])

    # Invalid indexes raise IndexError.
    try:
        print(text[100])
    except IndexError as error:
        print("Invalid index handled:", error)


# ---------------------------------------------------------------------------
# 2. Traversal
# ---------------------------------------------------------------------------

def demonstrate_traversal() -> None:
    """Demonstrate several ways to traverse a string."""
    print("\n=== 3. String traversal ===")

    text = "Code"

    print("Direct traversal:")
    for character in text:
        print(character)

    print("Traversal with indexes:")
    for index, character in enumerate(text):
        print(index, character)

    print("Reverse traversal:")
    for character in reversed(text):
        print(character)


# ---------------------------------------------------------------------------
# 3. Concatenation and construction
# ---------------------------------------------------------------------------

def demonstrate_concatenation() -> None:
    """Demonstrate string concatenation and efficient construction."""
    print("\n=== 4. Concatenation ===")

    first_name = "Atul"
    last_name = "Pandey"

    full_name = first_name + " " + last_name
    print("Using +:", full_name)

    # f-strings are usually clearer when values are embedded in text.
    age = 25
    message = f"{full_name} is {age} years old."
    print("Using f-string:", message)

    # join() is useful when combining many strings.
    words = ["Python", "strings", "are", "immutable"]
    sentence = " ".join(words)
    print("Using join():", sentence)

    # Repetition is another string operation.
    print("Repeated:", "ha" * 3)


# ---------------------------------------------------------------------------
# 4. Comparison
# ---------------------------------------------------------------------------

def demonstrate_comparison() -> None:
    """Demonstrate equality, ordering, and case-insensitive comparison."""
    print("\n=== 5. String comparison ===")

    print('"apple" == "apple":', "apple" == "apple")
    print('"apple" == "Apple":', "apple" == "Apple")
    print('"apple" != "orange":', "apple" != "orange")

    # Lexicographic comparison compares Unicode code points.
    print('"apple" < "banana":', "apple" < "banana")
    print('"cat" > "car":', "cat" > "car")

    first = "Python"
    second = "python"

    print("Case-sensitive equality:", first == second)
    print("Case-insensitive equality:", first.casefold() == second.casefold())


# ---------------------------------------------------------------------------
# 5. Conversion and case conversion
# ---------------------------------------------------------------------------

def demonstrate_conversion_and_case() -> None:
    """Demonstrate conversions and common case transformations."""
    print("\n=== 6. Conversion and case conversion ===")

    number = 12345
    number_as_string = str(number)
    print("Integer:", number)
    print("Converted to string:", number_as_string)

    numeric_text = "987"
    converted_number = int(numeric_text)
    print("String:", numeric_text)
    print("Converted to integer:", converted_number)

    text = "pYtHoN programming"

    print("Original:", text)
    print("upper():", text.upper())
    print("lower():", text.lower())
    print("capitalize():", text.capitalize())
    print("title():", text.title())
    print("swapcase():", text.swapcase())

    # casefold() is intended for robust caseless comparisons.
    print("casefold():", text.casefold())


# ---------------------------------------------------------------------------
# 6. Core practice problems
# ---------------------------------------------------------------------------

def reverse_string(text: str) -> str:
    """Return the string in reverse order."""
    return text[::-1]


def reverse_string_manually(text: str) -> str:
    """
    Reverse a string without using slicing.

    Building a list and joining once avoids repeatedly creating intermediate
    strings in a loop.
    """
    characters = []

    for index in range(len(text) - 1, -1, -1):
        characters.append(text[index])

    return "".join(characters)


def count_characters(text: str) -> int:
    """Return the number of Unicode code points in the string."""
    return len(text)


def character_frequency(text: str, ignore_case: bool = False) -> Dict[str, int]:
    """Return a frequency dictionary for characters."""
    if ignore_case:
        text = text.casefold()

    return dict(Counter(text))


def remove_spaces(text: str) -> str:
    """Remove all whitespace characters."""
    return "".join(character for character in text if not character.isspace())


def remove_literal_spaces(text: str) -> str:
    """Remove only ordinary ASCII space characters."""
    return text.replace(" ", "")


def change_case(text: str, mode: str) -> str:
    """
    Change string case according to the requested mode.

    Supported modes:
    upper, lower, title, capitalize, swapcase, casefold
    """
    operations = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
        "capitalize": str.capitalize,
        "swapcase": str.swapcase,
        "casefold": str.casefold,
    }

    if mode not in operations:
        valid_modes = ", ".join(operations)
        raise ValueError(f"Unsupported case mode. Use: {valid_modes}")

    return operations[mode](text)


def count_vowels(text: str) -> int:
    """Count English vowels, ignoring case."""
    vowels = set("aeiou")
    return sum(1 for character in text.casefold() if character in vowels)


def count_vowels_and_consonants(text: str) -> Tuple[int, int]:
    """
    Count English alphabetic vowels and consonants.

    Digits, spaces, punctuation, and non-Latin alphabetic characters are
    excluded from both counts.
    """
    vowels = set("aeiou")
    vowel_count = 0
    consonant_count = 0

    for character in text.casefold():
        if "a" <= character <= "z":
            if character in vowels:
                vowel_count += 1
            else:
                consonant_count += 1

    return vowel_count, consonant_count


def first_unique_character(text: str) -> Optional[str]:
    """
    Return the first character that occurs exactly once.

    Counter creates O(n) frequency information, followed by one O(n) scan.
    """
    frequencies = Counter(text)

    for character in text:
        if frequencies[character] == 1:
            return character

    return None


def first_unique_character_ignore_case(text: str) -> Optional[str]:
    """
    Find the first character unique under case-insensitive comparison.

    The returned character retains its original spelling.
    """
    normalized = text.casefold()
    frequencies = Counter(normalized)

    for original, normalized_character in zip(text, normalized):
        if frequencies[normalized_character] == 1:
            return original

    return None


def count_words(text: str) -> int:
    """
    Count whitespace-separated words.

    split() without an argument handles multiple spaces, tabs, and newlines.
    """
    return len(text.split())


def count_words_simple(text: str) -> int:
    """Count words using an explicit traversal."""
    word_count = 0
    inside_word = False

    for character in text:
        if character.isspace():
            inside_word = False
        elif not inside_word:
            word_count += 1
            inside_word = True

    return word_count


# ---------------------------------------------------------------------------
# 7. Validation and cleaning
# ---------------------------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces and trim the result."""
    return " ".join(text.split())


def is_palindrome(text: str, ignore_case: bool = True) -> bool:
    """
    Determine whether text reads identically in both directions.

    Spaces and punctuation are removed so phrases can be tested as well.
    """
    cleaned = "".join(
        character
        for character in text.casefold()
        if character.isalnum()
    )

    return cleaned == cleaned[::-1]


def validate_non_empty(text: str) -> str:
    """Validate that a string contains meaningful non-whitespace content."""
    if not isinstance(text, str):
        raise TypeError("Expected a string.")

    if not text.strip():
        raise ValueError("String must not be empty or whitespace-only.")

    return text


def safe_integer_from_string(text: str) -> Optional[int]:
    """Safely convert integer text while returning None for invalid input."""
    try:
        return int(text.strip())
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# 8. More advanced string processing
# ---------------------------------------------------------------------------

def longest_word(text: str) -> str:
    """Return the longest whitespace-separated word."""
    words = text.split()

    if not words:
        return ""

    return max(words, key=len)


def most_common_character(
    text: str,
    ignore_whitespace: bool = True,
) -> Optional[Tuple[str, int]]:
    """Return the most frequent character and its frequency."""
    characters = (
        character
        for character in text
        if not (ignore_whitespace and character.isspace())
    )

    frequencies = Counter(characters)

    if not frequencies:
        return None

    return frequencies.most_common(1)[0]


def character_classes(text: str) -> Dict[str, int]:
    """Classify characters into common categories."""
    result = {
        "letters": 0,
        "digits": 0,
        "whitespace": 0,
        "punctuation_or_symbols": 0,
    }

    for character in text:
        if character.isalpha():
            result["letters"] += 1
        elif character.isdigit():
            result["digits"] += 1
        elif character.isspace():
            result["whitespace"] += 1
        else:
            result["punctuation_or_symbols"] += 1

    return result


def contains_only_ascii(text: str) -> bool:
    """Check whether every character belongs to the ASCII range."""
    return all(ord(character) < 128 for character in text)


def unicode_code_points(text: str) -> List[int]:
    """Return Unicode code points for every character."""
    return [ord(character) for character in text]


def find_all_occurrences(text: str, target: str) -> List[int]:
    """Return every starting index at which target occurs."""
    if target == "":
        raise ValueError("Target must not be empty.")

    positions = []
    start = 0

    while True:
        position = text.find(target, start)

        if position == -1:
            break

        positions.append(position)
        start = position + 1

    return positions


# ---------------------------------------------------------------------------
# 9. Immutability demonstration
# ---------------------------------------------------------------------------

def demonstrate_immutability() -> None:
    """Show that string operations create new strings."""
    print("\n=== 7. String immutability ===")

    text = "hello"

    try:
        text[0] = "H"
    except TypeError as error:
        print("Direct character assignment is invalid:", error)

    changed = "H" + text[1:]

    print("Original:", text)
    print("New string:", changed)

    # Methods such as upper() do not modify the original object.
    uppercase = text.upper()
    print("After upper():", uppercase)
    print("Original remains:", text)


# ---------------------------------------------------------------------------
# 10. Performance comparison
# ---------------------------------------------------------------------------

def demonstrate_performance_principles() -> None:
    """
    Explain practical performance considerations through executable examples.

    Repeated += can create many intermediate strings. Building a list and
    joining once is usually preferable when constructing large text.
    """
    print("\n=== 8. Performance considerations ===")

    parts = [f"item-{index}" for index in range(10)]

    joined = "".join(parts)
    repeated_concatenation = ""

    for part in parts:
        repeated_concatenation += part

    print("join() result:", joined)
    print("Repeated + result:", repeated_concatenation)
    print("Results equal:", joined == repeated_concatenation)

    print("Frequency counting:", character_frequency("banana"))
    print("Frequency counting uses a hash-based Counter.")


# ---------------------------------------------------------------------------
# 11. Small text analyzer
# ---------------------------------------------------------------------------

@dataclass
class TextAnalysis:
    """Structured results produced by the text-analysis case study."""

    original: str
    character_count: int
    character_count_without_spaces: int
    word_count: int
    vowel_count: int
    consonant_count: int
    unique_character: Optional[str]
    longest_word: str
    most_common_character: Optional[Tuple[str, int]]
    is_palindrome: bool
    normalized: str
    character_classes: Dict[str, int]


def analyze_text(text: str) -> TextAnalysis:
    """Perform several independent string-analysis operations."""
    validate_non_empty(text)

    vowels, consonants = count_vowels_and_consonants(text)

    return TextAnalysis(
        original=text,
        character_count=len(text),
        character_count_without_spaces=len(remove_spaces(text)),
        word_count=count_words(text),
        vowel_count=vowels,
        consonant_count=consonants,
        unique_character=first_unique_character(text),
        longest_word=longest_word(text),
        most_common_character=most_common_character(text),
        is_palindrome=is_palindrome(text),
        normalized=normalize_whitespace(text),
        character_classes=character_classes(text),
    )


def print_analysis(analysis: TextAnalysis) -> None:
    """Display a TextAnalysis result in a readable form."""
    print("\n=== Text analysis case study ===")
    print("Original:", analysis.original)
    print("Character count:", analysis.character_count)
    print(
        "Characters without spaces:",
        analysis.character_count_without_spaces,
    )
    print("Word count:", analysis.word_count)
    print("Vowel count:", analysis.vowel_count)
    print("Consonant count:", analysis.consonant_count)
    print("First unique character:", analysis.unique_character)
    print("Longest word:", analysis.longest_word)
    print("Most common character:", analysis.most_common_character)
    print("Palindrome:", analysis.is_palindrome)
    print("Normalized:", analysis.normalized)
    print("Character classes:", analysis.character_classes)


# ---------------------------------------------------------------------------
# 12. Practice test suite
# ---------------------------------------------------------------------------

def run_practice_tests() -> None:
    """Run assertions covering normal cases and edge cases."""
    print("\n=== 9. Practice tests ===")

    assert reverse_string("Python") == "nohtyP"
    assert reverse_string("") == ""
    assert reverse_string_manually("abc") == "cba"

    assert count_characters("hello") == 5
    assert count_characters("") == 0

    assert remove_spaces("a b c") == "abc"
    assert remove_spaces("a\tb\nc") == "abc"

    assert change_case("python", "upper") == "PYTHON"
    assert change_case("PYTHON", "lower") == "python"

    assert count_vowels("education") == 5
    assert count_vowels("") == 0

    assert first_unique_character("swiss") == "w"
    assert first_unique_character("aabb") is None

    assert count_words("one two three") == 3
    assert count_words("  one   two\tthree\n") == 3
    assert count_words("") == 0

    assert normalize_whitespace("  Python   is\tgreat ") == "Python is great"

    assert is_palindrome("level")
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert not is_palindrome("Python")

    assert find_all_occurrences("banana", "ana") == [1, 3]

    assert safe_integer_from_string("42") == 42
    assert safe_integer_from_string("not-a-number") is None

    print("All tests passed.")


# ---------------------------------------------------------------------------
# 13. Edge cases
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Demonstrate unusual and boundary inputs."""
    print("\n=== 10. Edge cases ===")

    examples = [
        "",
        " ",
        "   ",
        "12345",
        "!@#$%",
        "A1 B2 C3",
        "café",
        "भारत",
        "hello\nworld",
        "hello\tworld",
    ]

    for text in examples:
        print(
            repr(text),
            "=>",
            {
                "length": len(text),
                "words": count_words(text),
                "vowels": count_vowels(text),
                "classes": character_classes(text),
            },
        )

    try:
        change_case("hello", "unsupported")
    except ValueError as error:
        print("Invalid case mode handled:", error)

    try:
        validate_non_empty("   ")
    except ValueError as error:
        print("Empty-content validation handled:", error)

    try:
        find_all_occurrences("abc", "")
    except ValueError as error:
        print("Empty search target handled:", error)


# ---------------------------------------------------------------------------
# 14. Practical demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete Day 20 string fundamentals lesson."""
    print("=" * 72)
    print("DAY 20 — STRING FUNDAMENTALS")
    print("=" * 72)

    demonstrate_characters()
    demonstrate_indexing_and_slicing()
    demonstrate_traversal()
    demonstrate_concatenation()
    demonstrate_comparison()
    demonstrate_conversion_and_case()

    print("\n=== Practice problem demonstrations ===")

    sample = "Python String Fundamentals"

    print("Original:", sample)
    print("Reverse:", reverse_string(sample))
    print("Manual reverse:", reverse_string_manually(sample))
    print("Character count:", count_characters(sample))
    print("Without spaces:", remove_spaces(sample))
    print("Uppercase:", change_case(sample, "upper"))
    print("Lowercase:", change_case(sample, "lower"))
    print("Vowels:", count_vowels(sample))
    print("First unique character:", first_unique_character(sample))
    print("Word count:", count_words(sample))
    print("Frequency:", character_frequency(sample, ignore_case=True))

    demonstrate_immutability()
    demonstrate_performance_principles()

    analysis = analyze_text(
        "Python makes text processing readable, expressive, and practical."
    )
    print_analysis(analysis)

    demonstrate_edge_cases()
    run_practice_tests()

    print("\n=== Study checklist ===")
    checklist = [
        "Characters",
        "Indexing",
        "Traversal",
        "Concatenation",
        "Comparison",
        "Conversion",
        "Case conversion",
        "Reverse string",
        "Count characters",
        "Remove spaces",
        "Change case",
        "Count vowels",
        "First unique character",
        "Count words",
    ]

    for item in checklist:
        print("[x]", item)

    print("\nDay 20 string fundamentals completed.")


if __name__ == "__main__":
    main()
