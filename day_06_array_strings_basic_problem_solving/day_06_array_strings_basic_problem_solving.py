"""
Day 6 — Arrays, Strings and Basic Problem Solving

A self-contained study and practice program covering:
- Array/list creation, indexing, traversal, mutation, and slicing
- String creation, indexing, traversal, and manipulation
- Linear searching and counting
- Maximum, minimum, sum, average, reversal, palindrome checking
- Duplicate detection
- Character frequency
- Second-largest value
- Even/odd counting
- Edge cases and validation
- Time and space complexity
- Progressive problem-solving techniques
- 15 mixed beginner problems
- A small test suite

The examples use only Python's standard library.
"""

from collections import Counter
from typing import Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS: ARRAYS IN PYTHON
# ---------------------------------------------------------------------------

def demonstrate_array_creation() -> None:
    """Show common ways to create Python lists."""
    empty_array = []
    numbers = [10, 20, 30, 40, 50]
    repeated_values = [0] * 5
    mixed_values = [10, "Python", 3.14, True]

    print("\n=== ARRAY CREATION ===")
    print("Empty array:", empty_array)
    print("Numbers:", numbers)
    print("Repeated values:", repeated_values)
    print("Mixed values:", mixed_values)


def demonstrate_array_indexing() -> None:
    """Demonstrate zero-based indexing and negative indexing."""
    numbers = [10, 20, 30, 40, 50]

    print("\n=== ARRAY INDEXING ===")
    print("Array:", numbers)
    print("Index 0:", numbers[0])
    print("Index 2:", numbers[2])
    print("Last element:", numbers[-1])
    print("Second-last element:", numbers[-2])

    try:
        print(numbers[10])
    except IndexError as error:
        print("Invalid index handled:", error)


def demonstrate_array_traversal() -> None:
    """Show value-based and index-based traversal."""
    numbers = [12, 7, 25, 9, 18]

    print("\n=== ARRAY TRAVERSAL ===")

    print("Value-based traversal:")
    for number in numbers:
        print(number, end=" ")
    print()

    print("Index-based traversal:")
    for index in range(len(numbers)):
        print(f"index={index}, value={numbers[index]}")

    print("Traversal with enumerate:")
    for index, number in enumerate(numbers):
        print(f"index={index}, value={number}")


def demonstrate_array_mutation_and_slicing() -> None:
    """Demonstrate updating elements and extracting portions of a list."""
    numbers = [10, 20, 30, 40, 50]

    print("\n=== ARRAY MUTATION AND SLICING ===")
    numbers[2] = 35
    print("After replacing index 2:", numbers)

    print("First three:", numbers[:3])
    print("Middle section:", numbers[1:4])
    print("Last two:", numbers[-2:])
    print("Every second element:", numbers[::2])
    print("Reversed using slicing:", numbers[::-1])


# ---------------------------------------------------------------------------
# 2. FUNDAMENTALS: STRINGS
# ---------------------------------------------------------------------------

def demonstrate_string_basics() -> None:
    """Show indexing, traversal, slicing, and basic string operations."""
    text = "Algorithm"

    print("\n=== STRING BASICS ===")
    print("String:", text)
    print("First character:", text[0])
    print("Last character:", text[-1])

    print("Characters:")
    for character in text:
        print(character, end=" ")
    print()

    print("First four characters:", text[:4])
    print("Reversed string:", text[::-1])
    print("Length:", len(text))
    print("Lowercase:", text.lower())
    print("Uppercase:", text.upper())
    print("Starts with 'Algo':", text.startswith("Algo"))
    print("Contains 'g':", "g" in text)


def demonstrate_string_manipulation() -> None:
    """Demonstrate common string transformations."""
    raw_text = "  Data Structures and Algorithms  "

    print("\n=== STRING MANIPULATION ===")
    cleaned = raw_text.strip()
    print("Original:", repr(raw_text))
    print("Stripped:", repr(cleaned))
    print("Replaced:", cleaned.replace("Algorithms", "Problem Solving"))
    print("Split into words:", cleaned.split())
    print("Joined:", "-".join(cleaned.split()))

    sentence = "python is useful"
    capitalized_words = sentence.title()
    print("Title case:", capitalized_words)


# ---------------------------------------------------------------------------
# 3. BASIC SEARCHING
# ---------------------------------------------------------------------------

def linear_search(numbers: Sequence[int], target: int) -> int:
    """
    Return the first index containing target.

    Linear search checks elements from left to right.
    Time complexity: O(n)
    Extra space: O(1)
    """
    for index, number in enumerate(numbers):
        if number == target:
            return index
    return -1


def contains_value(numbers: Sequence[int], target: int) -> bool:
    """Return True if target exists in the sequence."""
    return linear_search(numbers, target) != -1


def find_all_positions(numbers: Sequence[int], target: int) -> List[int]:
    """Return every index where target occurs."""
    positions = []

    for index, number in enumerate(numbers):
        if number == target:
            positions.append(index)

    return positions


# ---------------------------------------------------------------------------
# 4. BASIC COUNTING
# ---------------------------------------------------------------------------

def count_occurrences(numbers: Sequence[int], target: int) -> int:
    """Count how many times target occurs."""
    count = 0

    for number in numbers:
        if number == target:
            count += 1

    return count


def count_characters(text: str) -> dict:
    """
    Count every character manually.

    A dictionary stores:
        character -> number of occurrences

    Time complexity: O(n)
    Space complexity: O(k), where k is the number of distinct characters.
    """
    frequency = {}

    for character in text:
        frequency[character] = frequency.get(character, 0) + 1

    return frequency


def count_characters_case_insensitive(text: str) -> dict:
    """Count alphabetic characters without treating uppercase/lowercase differently."""
    frequency = {}

    for character in text.lower():
        if character.isalpha():
            frequency[character] = frequency.get(character, 0) + 1

    return frequency


# ---------------------------------------------------------------------------
# 5. MAXIMUM, MINIMUM, SUM AND AVERAGE
# ---------------------------------------------------------------------------

def find_maximum(numbers: Sequence[int]) -> int:
    """
    Find maximum without using max().

    Raises ValueError for an empty sequence because there is no maximum.
    """
    if not numbers:
        raise ValueError("Cannot find maximum of an empty sequence.")

    maximum = numbers[0]

    for number in numbers[1:]:
        if number > maximum:
            maximum = number

    return maximum


def find_minimum(numbers: Sequence[int]) -> int:
    """Find minimum without using min()."""
    if not numbers:
        raise ValueError("Cannot find minimum of an empty sequence.")

    minimum = numbers[0]

    for number in numbers[1:]:
        if number < minimum:
            minimum = number

    return minimum


def calculate_sum(numbers: Sequence[int]) -> int:
    """Calculate sum manually."""
    total = 0

    for number in numbers:
        total += number

    return total


def calculate_average(numbers: Sequence[int]) -> float:
    """Calculate arithmetic mean."""
    if not numbers:
        raise ValueError("Cannot calculate average of an empty sequence.")

    return calculate_sum(numbers) / len(numbers)


# ---------------------------------------------------------------------------
# 6. REVERSING ARRAYS AND STRINGS
# ---------------------------------------------------------------------------

def reverse_array_in_place(numbers: List[int]) -> None:
    """
    Reverse a list in place using two pointers.

    The left pointer starts at the beginning.
    The right pointer starts at the end.
    They move toward each other after every swap.

    Time complexity: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(numbers) - 1

    while left < right:
        numbers[left], numbers[right] = numbers[right], numbers[left]
        left += 1
        right -= 1


def reverse_string_manually(text: str) -> str:
    """
    Reverse a string using a loop.

    Python strings are immutable, so a new string is produced.
    """
    reversed_characters = []

    for index in range(len(text) - 1, -1, -1):
        reversed_characters.append(text[index])

    return "".join(reversed_characters)


# ---------------------------------------------------------------------------
# 7. PALINDROME CHECKING
# ---------------------------------------------------------------------------

def is_palindrome(text: str) -> bool:
    """
    Check whether a string reads the same forward and backward.

    This version ignores spaces, punctuation, and letter case.
    """
    normalized = []

    for character in text.lower():
        if character.isalnum():
            normalized.append(character)

    left = 0
    right = len(normalized) - 1

    while left < right:
        if normalized[left] != normalized[right]:
            return False

        left += 1
        right -= 1

    return True


def is_numeric_palindrome(numbers: Sequence[int]) -> bool:
    """Check whether an array of values forms a palindrome."""
    left = 0
    right = len(numbers) - 1

    while left < right:
        if numbers[left] != numbers[right]:
            return False

        left += 1
        right -= 1

    return True


# ---------------------------------------------------------------------------
# 8. DUPLICATE VALUES
# ---------------------------------------------------------------------------

def find_duplicate_values(numbers: Sequence[int]) -> List[int]:
    """
    Return distinct values that occur more than once.

    A set provides average O(1) membership checks.
    """
    seen = set()
    duplicates = set()

    for number in numbers:
        if number in seen:
            duplicates.add(number)
        else:
            seen.add(number)

    return sorted(duplicates)


def find_first_duplicate(numbers: Sequence[int]) -> Optional[int]:
    """Return the first value encountered for the second time."""
    seen = set()

    for number in numbers:
        if number in seen:
            return number
        seen.add(number)

    return None


# ---------------------------------------------------------------------------
# 9. SECOND-LARGEST VALUE
# ---------------------------------------------------------------------------

def find_second_largest(numbers: Sequence[int]) -> int:
    """
    Find the second distinct-largest value in one pass.

    Example:
        [10, 20, 20, 5] -> 10

    Raises ValueError when fewer than two distinct values exist.
    """
    if len(numbers) < 2:
        raise ValueError("At least two values are required.")

    largest = None
    second_largest = None

    for number in numbers:
        if largest is None or number > largest:
            second_largest = largest
            largest = number
        elif number != largest and (
            second_largest is None or number > second_largest
        ):
            second_largest = number

    if second_largest is None:
        raise ValueError("At least two distinct values are required.")

    return second_largest


# ---------------------------------------------------------------------------
# 10. EVEN AND ODD COUNTING
# ---------------------------------------------------------------------------

def count_even_and_odd(numbers: Sequence[int]) -> Tuple[int, int]:
    """Return (even_count, odd_count)."""
    even_count = 0
    odd_count = 0

    for number in numbers:
        if number % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    return even_count, odd_count


# ---------------------------------------------------------------------------
# 11. ADDITIONAL BEGINNER PROBLEM-SOLVING FUNCTIONS
# ---------------------------------------------------------------------------

def find_first_maximum_index(numbers: Sequence[int]) -> int:
    """Return the index of the first maximum value."""
    if not numbers:
        raise ValueError("Array cannot be empty.")

    maximum_index = 0

    for index in range(1, len(numbers)):
        if numbers[index] > numbers[maximum_index]:
            maximum_index = index

    return maximum_index


def count_positive_negative_zero(numbers: Sequence[int]) -> Tuple[int, int, int]:
    """Count positive values, negative values, and zeros."""
    positive = 0
    negative = 0
    zero = 0

    for number in numbers:
        if number > 0:
            positive += 1
        elif number < 0:
            negative += 1
        else:
            zero += 1

    return positive, negative, zero


def remove_duplicates_preserving_order(numbers: Sequence[int]) -> List[int]:
    """Remove duplicate values while keeping first-occurrence order."""
    seen = set()
    result = []

    for number in numbers:
        if number not in seen:
            seen.add(number)
            result.append(number)

    return result


def merge_two_arrays(first: Sequence[int], second: Sequence[int]) -> List[int]:
    """Concatenate two arrays into a new list."""
    result = []

    for value in first:
        result.append(value)

    for value in second:
        result.append(value)

    return result


def find_common_values(first: Sequence[int], second: Sequence[int]) -> List[int]:
    """Return distinct values occurring in both sequences."""
    second_values = set(second)
    common = set()

    for value in first:
        if value in second_values:
            common.add(value)

    return sorted(common)


def move_zeros_to_end(numbers: List[int]) -> None:
    """
    Move all zero values to the end while preserving non-zero order.

    This uses a write position rather than repeatedly removing elements.
    """
    write_position = 0

    for value in numbers:
        if value != 0:
            numbers[write_position] = value
            write_position += 1

    while write_position < len(numbers):
        numbers[write_position] = 0
        write_position += 1


def is_sorted_ascending(numbers: Sequence[int]) -> bool:
    """Check whether values are in non-decreasing order."""
    for index in range(1, len(numbers)):
        if numbers[index] < numbers[index - 1]:
            return False

    return True


def find_missing_value(numbers: Sequence[int], maximum_value: int) -> int:
    """
    Find the missing value from 0..maximum_value.

    The input must contain every value in that range except one.
    Uses the arithmetic-sum identity.
    """
    expected = maximum_value * (maximum_value + 1) // 2
    actual = calculate_sum(numbers)
    return expected - actual


# ---------------------------------------------------------------------------
# 12. STRING PROBLEM SOLVING
# ---------------------------------------------------------------------------

def count_vowels_and_consonants(text: str) -> Tuple[int, int]:
    """Count alphabetic vowels and consonants."""
    vowels = set("aeiou")
    vowel_count = 0
    consonant_count = 0

    for character in text.lower():
        if character.isalpha():
            if character in vowels:
                vowel_count += 1
            else:
                consonant_count += 1

    return vowel_count, consonant_count


def first_non_repeating_character(text: str) -> Optional[str]:
    """
    Return the first character appearing exactly once.

    The first pass counts.
    The second pass preserves original order.
    """
    frequencies = count_characters(text)

    for character in text:
        if frequencies[character] == 1:
            return character

    return None


def remove_spaces(text: str) -> str:
    """Remove every whitespace character."""
    return "".join(character for character in text if not character.isspace())


def are_anagrams(first: str, second: str) -> bool:
    """
    Determine whether two strings contain the same characters with
    the same frequencies, ignoring spaces and letter case.
    """
    first_clean = remove_spaces(first).lower()
    second_clean = remove_spaces(second).lower()

    return Counter(first_clean) == Counter(second_clean)


def reverse_words(sentence: str) -> str:
    """Reverse word order while preserving individual word spelling."""
    words = sentence.split()
    return " ".join(reversed(words))


def find_longest_word(sentence: str) -> str:
    """Return the first longest word in a sentence."""
    words = sentence.split()

    if not words:
        return ""

    longest = words[0]

    for word in words[1:]:
        if len(word) > len(longest):
            longest = word

    return longest


# ---------------------------------------------------------------------------
# 13. EDGE CASES AND BEHAVIOR
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n=== EDGE CASES ===")

    examples = {
        "empty array": [],
        "one element": [42],
        "negative values": [-10, -5, -20],
        "all equal": [7, 7, 7, 7],
        "mixed duplicates": [4, 2, 4, 3, 2, 4],
        "zeros": [0, 0, 0],
        "empty string": "",
        "one-character string": "a",
        "spaces": "   ",
    }

    for description, value in examples.items():
        print(f"{description}: {value!r}")

    try:
        find_maximum([])
    except ValueError as error:
        print("Empty maximum handled:", error)

    try:
        find_second_largest([5, 5, 5])
    except ValueError as error:
        print("No second distinct-largest value handled:", error)

    print("Empty string palindrome:", is_palindrome(""))
    print("One-character palindrome:", is_palindrome("x"))


# ---------------------------------------------------------------------------
# 14. COMPLEXITY DEMONSTRATIONS
# ---------------------------------------------------------------------------

def complexity_notes() -> None:
    """
    Print a compact complexity reference.

    Most basic scans in this lesson are O(n).
    Nested scans can become O(n^2).
    Sets and dictionaries usually provide average O(1) lookup.
    """
    print("\n=== COMPLEXITY REFERENCE ===")
    notes = [
        ("Array traversal", "O(n)", "O(1) extra space"),
        ("Linear search", "O(n)", "O(1)"),
        ("Count occurrences", "O(n)", "O(1)"),
        ("Maximum/minimum", "O(n)", "O(1)"),
        ("Reverse with two pointers", "O(n)", "O(1)"),
        ("Character frequency", "O(n)", "O(k)"),
        ("Duplicate detection with set", "O(n) average", "O(n)"),
        ("Naive duplicate detection", "O(n^2)", "O(1)"),
        ("Palindrome two pointers", "O(n)", "O(n) for normalized text"),
    ]

    for operation, time, space in notes:
        print(f"{operation:<35} Time: {time:<12} Space: {space}")


# ---------------------------------------------------------------------------
# 15. 15 MIXED BEGINNER PROBLEMS
# ---------------------------------------------------------------------------

def problem_01_sum(numbers: Sequence[int]) -> int:
    """Problem 1: Calculate array sum."""
    return calculate_sum(numbers)


def problem_02_maximum(numbers: Sequence[int]) -> int:
    """Problem 2: Find maximum."""
    return find_maximum(numbers)


def problem_03_minimum(numbers: Sequence[int]) -> int:
    """Problem 3: Find minimum."""
    return find_minimum(numbers)


def problem_04_count_target(numbers: Sequence[int], target: int) -> int:
    """Problem 4: Count target occurrences."""
    return count_occurrences(numbers, target)


def problem_05_reverse_array(numbers: Sequence[int]) -> List[int]:
    """Problem 5: Return a reversed copy."""
    result = list(numbers)
    reverse_array_in_place(result)
    return result


def problem_06_reverse_string(text: str) -> str:
    """Problem 6: Reverse a string."""
    return reverse_string_manually(text)


def problem_07_palindrome(text: str) -> bool:
    """Problem 7: Check palindrome."""
    return is_palindrome(text)


def problem_08_duplicates(numbers: Sequence[int]) -> List[int]:
    """Problem 8: Find duplicate values."""
    return find_duplicate_values(numbers)


def problem_09_character_count(text: str) -> dict:
    """Problem 9: Count characters."""
    return count_characters(text)


def problem_10_second_largest(numbers: Sequence[int]) -> int:
    """Problem 10: Find second distinct-largest value."""
    return find_second_largest(numbers)


def problem_11_even_odd(numbers: Sequence[int]) -> Tuple[int, int]:
    """Problem 11: Count even and odd values."""
    return count_even_and_odd(numbers)


def problem_12_first_non_repeating(text: str) -> Optional[str]:
    """Problem 12: Find first non-repeating character."""
    return first_non_repeating_character(text)


def problem_13_anagram(first: str, second: str) -> bool:
    """Problem 13: Check whether two strings are anagrams."""
    return are_anagrams(first, second)


def problem_14_move_zeros(numbers: Sequence[int]) -> List[int]:
    """Problem 14: Move zeros to the end."""
    result = list(numbers)
    move_zeros_to_end(result)
    return result


def problem_15_missing_value(numbers: Sequence[int], maximum_value: int) -> int:
    """Problem 15: Find one missing value from a complete 0..n range."""
    return find_missing_value(numbers, maximum_value)


def run_mixed_practice() -> None:
    print("\n=== 15 MIXED BEGINNER PROBLEMS ===")

    sample_numbers = [8, 3, 5, 3, 10, 2, 8, 6]
    sample_text = "programming"

    results = [
        ("1. Array sum", problem_01_sum(sample_numbers)),
        ("2. Maximum", problem_02_maximum(sample_numbers)),
        ("3. Minimum", problem_03_minimum(sample_numbers)),
        ("4. Count 3", problem_04_count_target(sample_numbers, 3)),
        ("5. Reverse array", problem_05_reverse_array(sample_numbers)),
        ("6. Reverse string", problem_06_reverse_string(sample_text)),
        ("7. Palindrome", problem_07_palindrome("Never odd or even")),
        ("8. Duplicates", problem_08_duplicates(sample_numbers)),
        ("9. Character count", problem_09_character_count("banana")),
        ("10. Second largest", problem_10_second_largest(sample_numbers)),
        ("11. Even and odd", problem_11_even_odd(sample_numbers)),
        ("12. First non-repeating", problem_12_first_non_repeating("swiss")),
        ("13. Anagram", problem_13_anagram("listen", "silent")),
        ("14. Move zeros", problem_14_move_zeros([0, 1, 0, 3, 12])),
        ("15. Missing value", problem_15_missing_value([0, 1, 2, 4, 5], 5)),
    ]

    for name, result in results:
        print(f"{name}: {result}")


# ---------------------------------------------------------------------------
# 16. TESTS
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Run assertions covering normal cases and edge cases."""
    print("\n=== TEST SUITE ===")

    numbers = [4, 2, 9, 2, 7]

    assert find_maximum(numbers) == 9
    assert find_minimum(numbers) == 2
    assert calculate_sum(numbers) == 24
    assert calculate_average(numbers) == 4.8
    assert linear_search(numbers, 9) == 2
    assert linear_search(numbers, 100) == -1
    assert count_occurrences(numbers, 2) == 2
    assert find_all_positions(numbers, 2) == [1, 3]

    reversed_numbers = numbers.copy()
    reverse_array_in_place(reversed_numbers)
    assert reversed_numbers == [7, 2, 9, 2, 4]

    assert reverse_string_manually("hello") == "olleh"
    assert is_palindrome("racecar")
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert not is_palindrome("python")

    assert find_duplicate_values(numbers) == [2]
    assert find_first_duplicate(numbers) == 2
    assert find_second_largest(numbers) == 7

    assert count_even_and_odd([1, 2, 3, 4, 6]) == (3, 2)
    assert count_characters("aabbc") == {"a": 2, "b": 2, "c": 1}
    assert first_non_repeating_character("swiss") == "w"

    assert are_anagrams("listen", "silent")
    assert not are_anagrams("hello", "world")
    assert reverse_words("one two three") == "three two one"
    assert find_longest_word("small medium longest") == "longest"

    assert remove_duplicates_preserving_order([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert find_common_values([1, 2, 3, 4], [3, 4, 5]) == [3, 4]
    assert is_sorted_ascending([1, 2, 2, 5])
    assert not is_sorted_ascending([1, 3, 2])

    zero_test = [0, 1, 0, 3, 12]
    move_zeros_to_end(zero_test)
    assert zero_test == [1, 3, 12, 0, 0]

    assert find_missing_value([0, 1, 2, 4], 4) == 3

    print("All tests passed.")


# ---------------------------------------------------------------------------
# 17. INTERACTIVE INPUT UTILITIES
# ---------------------------------------------------------------------------

def parse_integer_array(raw_input: str) -> List[int]:
    """
    Convert a space-separated string such as '10 20 30' into integers.

    Invalid tokens are rejected rather than silently ignored.
    """
    tokens = raw_input.split()

    if not tokens:
        raise ValueError("At least one integer is required.")

    numbers = []

    for token in tokens:
        try:
            numbers.append(int(token))
        except ValueError as error:
            raise ValueError(f"Invalid integer: {token!r}") from error

    return numbers


def interactive_demo() -> None:
    """
    Optional interactive section.

    It is disabled by default so the study file runs immediately.
    """
    print("\n=== OPTIONAL INTERACTIVE DEMO ===")
    print("This function can be called manually from main().")
    print("Example input: 10 4 7 4 2 9")

    raw_numbers = input("Enter space-separated integers: ")
    numbers = parse_integer_array(raw_numbers)

    print("Array:", numbers)
    print("Maximum:", find_maximum(numbers))
    print("Minimum:", find_minimum(numbers))
    print("Sum:", calculate_sum(numbers))
    print("Even/odd:", count_even_and_odd(numbers))
    print("Duplicates:", find_duplicate_values(numbers))


# ---------------------------------------------------------------------------
# 18. MAIN STUDY PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete Day 6 study demonstration."""
    print("=" * 72)
    print("DAY 6 — ARRAYS, STRINGS AND BASIC PROBLEM SOLVING")
    print("=" * 72)

    demonstrate_array_creation()
    demonstrate_array_indexing()
    demonstrate_array_traversal()
    demonstrate_array_mutation_and_slicing()

    demonstrate_string_basics()
    demonstrate_string_manipulation()

    print("\n=== BASIC SEARCHING ===")
    search_numbers = [5, 9, 2, 9, 7, 9]
    print("Array:", search_numbers)
    print("Search for 7:", linear_search(search_numbers, 7))
    print("Search for 100:", linear_search(search_numbers, 100))
    print("All positions of 9:", find_all_positions(search_numbers, 9))

    print("\n=== BASIC COUNTING ===")
    print("Occurrences of 9:", count_occurrences(search_numbers, 9))
    print("Character frequencies:", count_characters("data structures"))

    print("\n=== MAXIMUM, MINIMUM, SUM AND AVERAGE ===")
    statistics_numbers = [12, 4, 18, 7, 25, 3]
    print("Array:", statistics_numbers)
    print("Maximum:", find_maximum(statistics_numbers))
    print("Minimum:", find_minimum(statistics_numbers))
    print("Sum:", calculate_sum(statistics_numbers))
    print("Average:", calculate_average(statistics_numbers))

    print("\n=== REVERSAL ===")
    reverse_numbers = [1, 2, 3, 4, 5]
    print("Original:", reverse_numbers)
    reverse_array_in_place(reverse_numbers)
    print("Reversed in place:", reverse_numbers)
    print("Reversed string:", reverse_string_manually("algorithm"))

    print("\n=== PALINDROMES ===")
    print("'racecar':", is_palindrome("racecar"))
    print("'hello':", is_palindrome("hello"))
    print("'A man, a plan, a canal: Panama':",
          is_palindrome("A man, a plan, a canal: Panama"))

    print("\n=== DUPLICATES ===")
    duplicate_numbers = [4, 7, 4, 2, 7, 7, 9]
    print("Array:", duplicate_numbers)
    print("Duplicate values:", find_duplicate_values(duplicate_numbers))
    print("First duplicate:", find_first_duplicate(duplicate_numbers))

    print("\n=== SECOND LARGEST ===")
    print("Array:", [10, 20, 20, 5, 15])
    print("Second distinct-largest:", find_second_largest([10, 20, 20, 5, 15]))

    print("\n=== EVEN AND ODD ===")
    print("Array:", [1, 2, 3, 4, 5, 6])
    print("Counts:", count_even_and_odd([1, 2, 3, 4, 5, 6]))

    print("\n=== ADDITIONAL PROBLEM-SOLVING PATTERNS ===")
    print(
        "Positive, negative, zero:",
        count_positive_negative_zero([-2, 0, 5, -1, 0, 8])
    )
    print(
        "Remove duplicates:",
        remove_duplicates_preserving_order([4, 2, 4, 1, 2, 3])
    )
    print(
        "Common values:",
        find_common_values([1, 2, 3, 4], [3, 4, 5, 6])
    )

    zero_array = [0, 4, 0, 5, 2, 0, 8]
    move_zeros_to_end(zero_array)
    print("Zeros moved to end:", zero_array)

    print("Sorted check [1,2,2,4]:", is_sorted_ascending([1, 2, 2, 4]))
    print("Missing value from [0,1,2,4]:", find_missing_value([0, 1, 2, 4], 4))

    print("\n=== STRING PROBLEM SOLVING ===")
    print(
        "Vowels/consonants:",
        count_vowels_and_consonants("Data Structures")
    )
    print(
        "First non-repeating:",
        first_non_repeating_character("swiss")
    )
    print(
        "Anagram:",
        are_anagrams("Dormitory", "Dirty room")
    )
    print(
        "Reverse words:",
        reverse_words("arrays strings problem solving")
    )
    print(
        "Longest word:",
        find_longest_word("arrays make data processing practical")
    )

    demonstrate_edge_cases()
    complexity_notes()
    run_mixed_practice()
    run_tests()

    print("\nStudy program completed.")


if __name__ == "__main__":
    main()
