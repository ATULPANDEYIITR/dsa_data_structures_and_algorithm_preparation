"""
Day 4 — Loops
A comprehensive study and practice program covering:

- for loops
- while loops
- do-while behavior in Python
- nested loops
- loop counters
- loop termination
- break
- continue
- sequences
- sums
- factorial
- multiplication tables
- digit counting
- number reversal
- palindrome numbers
- prime numbers
- Fibonacci numbers
- pattern generation
- validation
- edge cases
- performance and complexity
- practical algorithmic applications

The file is intentionally self-contained and executable with standard Python.
"""

from __future__ import annotations

import math
import time
from typing import Callable, Iterable, Iterator, List, Tuple


# ============================================================================
# 1. FUNDAMENTAL LOOP CONCEPTS
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def demonstrate_for_loop() -> None:
    """
    A for loop repeats once for every item produced by an iterable.

    range(start, stop, step) is commonly used for numeric repetition.
    The stop value is exclusive.
    """
    section("1. FOR LOOPS")

    print("Numbers from 0 through 4:")
    for number in range(5):
        print(number, end=" ")
    print()

    print("Numbers from 1 through 5:")
    for number in range(1, 6):
        print(number, end=" ")
    print()

    print("Even numbers from 2 through 10:")
    for number in range(2, 11, 2):
        print(number, end=" ")
    print()

    print("Counting backwards:")
    for number in range(10, 0, -1):
        print(number, end=" ")
    print()

    print("Iterating over a collection:")
    names = ["Ada", "Grace", "Alan", "Dennis"]
    for name in names:
        print(name)


def demonstrate_loop_counter() -> None:
    """
    A counter records how many iterations have occurred.

    enumerate() is generally safer than manually maintaining an index.
    """
    section("2. LOOP COUNTERS")

    languages = ["Python", "JavaScript", "C++", "Java"]

    print("Manual counter:")
    counter = 0
    for language in languages:
        print(counter, language)
        counter += 1

    print("\nenumerate() counter:")
    for index, language in enumerate(languages):
        print(index, language)

    print("\nCounter beginning at 1:")
    for position, language in enumerate(languages, start=1):
        print(position, language)


def demonstrate_while_loop() -> None:
    """
    A while loop repeats while its condition remains True.

    A crucial rule:
    the state used by the condition must eventually change when
    termination is expected.
    """
    section("3. WHILE LOOPS")

    counter = 1

    while counter <= 5:
        print(counter, end=" ")
        counter += 1

    print()

    print("Countdown:")
    countdown = 5

    while countdown > 0:
        print(countdown, end=" ")
        countdown -= 1

    print("Done")


def demonstrate_do_while_behavior() -> None:
    """
    Python has no native do-while syntax.

    A do-while loop executes its body at least once and checks the
    condition afterward. The equivalent Python structure is commonly:

        while True:
            ...
            if condition:
                break

    This demonstration shows that behavior.
    """
    section("4. DO-WHILE BEHAVIOR IN PYTHON")

    attempts = 0

    while True:
        attempts += 1
        print(f"Body executed for attempt {attempts}")

        if attempts >= 3:
            break

    print("The loop body executed before the termination condition was checked.")


def demonstrate_break_and_continue() -> None:
    """Demonstrate the two major loop-control statements."""
    section("5. BREAK AND CONTINUE")

    print("break stops the entire loop:")
    for number in range(1, 11):
        if number == 6:
            break
        print(number, end=" ")
    print()

    print("continue skips the current iteration:")
    for number in range(1, 11):
        if number % 2 == 0:
            continue
        print(number, end=" ")
    print()

    print("break inside nested loops only exits the nearest loop:")
    for row in range(3):
        for column in range(5):
            if column == 2:
                break
            print(f"({row},{column})", end=" ")
        print()


# ============================================================================
# 2. NUMBER SEQUENCES
# ============================================================================

def print_number_sequence(start: int, end: int, step: int = 1) -> None:
    """Print a configurable arithmetic sequence."""
    if step == 0:
        raise ValueError("step cannot be zero")

    for number in range(start, end + (1 if step > 0 else -1), step):
        print(number, end=" ")
    print()


def generate_number_sequence(start: int, end: int, step: int = 1) -> List[int]:
    """Return a number sequence as a list."""
    if step == 0:
        raise ValueError("step cannot be zero")

    return list(range(start, end + (1 if step > 0 else -1), step))


# ============================================================================
# 3. SUMS
# ============================================================================

def sum_with_loop(numbers: Iterable[int]) -> int:
    """
    Calculate a sum manually.

    This illustrates the accumulator pattern:
    accumulator = accumulator + current_value
    """
    total = 0

    for number in numbers:
        total += number

    return total


def sum_with_while(numbers: List[int]) -> int:
    """Calculate a list sum using a while loop."""
    total = 0
    index = 0

    while index < len(numbers):
        total += numbers[index]
        index += 1

    return total


def sum_even_numbers(limit: int) -> int:
    """Sum all even numbers from 1 through limit."""
    total = 0

    for number in range(1, limit + 1):
        if number % 2 != 0:
            continue
        total += number

    return total


# ============================================================================
# 4. FACTORIAL
# ============================================================================

def factorial_iterative(number: int) -> int:
    """
    Calculate n!.

    Mathematical definition:
        0! = 1
        n! = n × (n - 1) × ... × 1

    Time complexity: O(n)
    Space complexity: O(1), excluding the size of the resulting integer.
    """
    if number < 0:
        raise ValueError("factorial is undefined for negative integers")

    result = 1

    for value in range(2, number + 1):
        result *= value

    return result


def factorial_while(number: int) -> int:
    """Factorial using while instead of for."""
    if number < 0:
        raise ValueError("factorial is undefined for negative integers")

    result = 1
    current = 2

    while current <= number:
        result *= current
        current += 1

    return result


# ============================================================================
# 5. MULTIPLICATION TABLES
# ============================================================================

def multiplication_table(number: int, limit: int = 10) -> List[str]:
    """Generate a multiplication table as formatted strings."""
    if limit < 0:
        raise ValueError("limit cannot be negative")

    table = []

    for multiplier in range(1, limit + 1):
        product = number * multiplier
        table.append(f"{number} × {multiplier} = {product}")

    return table


def print_multiplication_table(number: int, limit: int = 10) -> None:
    for line in multiplication_table(number, limit):
        print(line)


def print_all_tables(max_number: int = 10, max_multiplier: int = 10) -> None:
    """Use nested loops to print multiple multiplication tables."""
    for number in range(1, max_number + 1):
        print(f"\nTable of {number}")
        for multiplier in range(1, max_multiplier + 1):
            print(f"{number} × {multiplier} = {number * multiplier}")


# ============================================================================
# 6. DIGIT OPERATIONS
# ============================================================================

def count_digits(number: int) -> int:
    """
    Count decimal digits without converting the number to a string.

    Zero has one digit.
    Negative signs are not digits, so abs() is used.
    """
    number = abs(number)

    if number == 0:
        return 1

    count = 0

    while number > 0:
        number //= 10
        count += 1

    return count


def reverse_number(number: int) -> int:
    """
    Reverse the decimal digits using repeated division.

    Example:
        12340 -> 4321

    Leading zeroes in the reversed representation disappear because
    the result is an integer.
    """
    sign = -1 if number < 0 else 1
    number = abs(number)

    reversed_number = 0

    while number > 0:
        digit = number % 10
        reversed_number = reversed_number * 10 + digit
        number //= 10

    return sign * reversed_number


def sum_of_digits(number: int) -> int:
    """Calculate the sum of decimal digits."""
    number = abs(number)

    total = 0

    if number == 0:
        return 0

    while number > 0:
        total += number % 10
        number //= 10

    return total


# ============================================================================
# 7. PALINDROME NUMBERS
# ============================================================================

def is_palindrome_number(number: int) -> bool:
    """
    A non-negative integer is a palindrome if it reads identically
    from left to right and right to left.

    Negative numbers are treated as non-palindromes here because the
    negative sign does not mirror a decimal digit.
    """
    if number < 0:
        return False

    return number == reverse_number(number)


def is_palindrome_without_full_reversal(number: int) -> bool:
    """
    Check a palindrome by comparing corresponding outer digits.

    This demonstrates an alternative approach that only processes
    approximately half of the digits.
    """
    if number < 0:
        return False

    if number < 10:
        return True

    divisor = 1

    while number // divisor >= 10:
        divisor *= 10

    while number != 0:
        leading_digit = number // divisor
        trailing_digit = number % 10

        if leading_digit != trailing_digit:
            return False

        number = (number % divisor) // 10
        divisor //= 100

    return True


# ============================================================================
# 8. PRIME NUMBERS
# ============================================================================

def is_prime_basic(number: int) -> bool:
    """
    Basic primality test.

    Every divisor from 2 through n-1 is tested.

    Time complexity: O(n).
    """
    if number < 2:
        return False

    for divisor in range(2, number):
        if number % divisor == 0:
            return False

    return True


def is_prime_optimized(number: int) -> bool:
    """
    Optimized primality test.

    If n has a divisor greater than sqrt(n), its paired divisor must
    be smaller than sqrt(n). Therefore testing through sqrt(n) is enough.

    Time complexity: O(sqrt(n)).
    """
    if number < 2:
        return False

    if number == 2:
        return True

    if number % 2 == 0:
        return False

    divisor = 3

    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2

    return True


def generate_primes(limit: int) -> List[int]:
    """Generate all prime numbers from 2 through limit."""
    primes = []

    for number in range(2, limit + 1):
        if is_prime_optimized(number):
            primes.append(number)

    return primes


# ============================================================================
# 9. FIBONACCI
# ============================================================================

def fibonacci_sequence(count: int) -> List[int]:
    """
    Generate the first count Fibonacci numbers.

    Sequence:
        0, 1, 1, 2, 3, 5, 8, ...

    Iterative generation is O(n) and uses O(1) working memory apart
    from the returned list.
    """
    if count < 0:
        raise ValueError("count cannot be negative")

    sequence = []
    first, second = 0, 1

    for _ in range(count):
        sequence.append(first)
        first, second = second, first + second

    return sequence


def fibonacci_until_limit(limit: int) -> List[int]:
    """Generate Fibonacci values not exceeding limit."""
    if limit < 0:
        return []

    sequence = []
    first, second = 0, 1

    while first <= limit:
        sequence.append(first)
        first, second = second, first + second

    return sequence


# ============================================================================
# 10. NESTED LOOPS AND PATTERNS
# ============================================================================

def square_pattern(size: int) -> List[str]:
    """Create a solid square of stars."""
    if size < 0:
        raise ValueError("size cannot be negative")

    lines = []

    for _ in range(size):
        row = ""
        for _ in range(size):
            row += "* "
        lines.append(row.rstrip())

    return lines


def right_triangle_pattern(height: int) -> List[str]:
    """Create a right-aligned-by-growth triangle."""
    if height < 0:
        raise ValueError("height cannot be negative")

    lines = []

    for row in range(1, height + 1):
        line = ""
        for _ in range(row):
            line += "* "
        lines.append(line.rstrip())

    return lines


def number_triangle(height: int) -> List[str]:
    """Generate a triangle containing repeated row numbers."""
    lines = []

    for row in range(1, height + 1):
        values = []

        for _ in range(row):
            values.append(str(row))

        lines.append(" ".join(values))

    return lines


def multiplication_grid(size: int) -> List[List[int]]:
    """Create a two-dimensional multiplication grid."""
    grid = []

    for row in range(1, size + 1):
        current_row = []

        for column in range(1, size + 1):
            current_row.append(row * column)

        grid.append(current_row)

    return grid


def print_multiplication_grid(size: int) -> None:
    for row in multiplication_grid(size):
        print(" ".join(f"{value:3}" for value in row))


# ============================================================================
# 11. LOOP CONTROL AND SEARCH
# ============================================================================

def first_multiple(numbers: Iterable[int], divisor: int) -> int | None:
    """
    Search for the first value divisible by divisor.

    break is represented naturally by returning when the value is found.
    """
    if divisor == 0:
        raise ValueError("divisor cannot be zero")

    for number in numbers:
        if number % divisor == 0:
            return number

    return None


def find_first_prime(start: int, end: int) -> int | None:
    """Find the first prime in an inclusive range."""
    for number in range(start, end + 1):
        if is_prime_optimized(number):
            return number

    return None


def classify_numbers(limit: int) -> Tuple[List[int], List[int], List[int]]:
    """
    Classify numbers into negative, zero, and positive values.

    continue makes the zero case explicit.
    """
    negatives = []
    zeroes = []
    positives = []

    for number in range(-limit, limit + 1):
        if number < 0:
            negatives.append(number)
            continue

        if number == 0:
            zeroes.append(number)
            continue

        positives.append(number)

    return negatives, zeroes, positives


# ============================================================================
# 12. LOOP INVARIANTS AND ACCUMULATORS
# ============================================================================

def maximum_with_loop(numbers: Iterable[int]) -> int:
    """
    Find the maximum without using max().

    Loop invariant:
    after processing each item, current_max is the maximum among all
    values processed so far.
    """
    iterator = iter(numbers)

    try:
        current_max = next(iterator)
    except StopIteration:
        raise ValueError("cannot find maximum of an empty sequence")

    for number in iterator:
        if number > current_max:
            current_max = number

    return current_max


def count_occurrences(numbers: Iterable[int], target: int) -> int:
    """Count target values using an accumulator."""
    count = 0

    for number in numbers:
        if number == target:
            count += 1

    return count


# ============================================================================
# 13. INPUT VALIDATION WITH A CONTROLLED LOOP
# ============================================================================

def parse_positive_integer(text: str) -> int:
    """Convert text to a positive integer or raise ValueError."""
    value = int(text)

    if value <= 0:
        raise ValueError("value must be positive")

    return value


def demonstrate_validation_without_interactive_input() -> None:
    """
    Demonstrate the same logic used by an interactive input loop
    without making the study file wait for user input.
    """
    section("13. VALIDATION LOOP")

    simulated_inputs = ["hello", "-5", "0", "12"]

    for user_input in simulated_inputs:
        try:
            value = parse_positive_integer(user_input)
        except ValueError as error:
            print(f"Input {user_input!r}: invalid ({error})")
            continue

        print(f"Input {user_input!r}: accepted as {value}")
        break


# ============================================================================
# 14. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    section("14. EDGE CASES")

    print("count_digits(0):", count_digits(0))
    print("count_digits(-12345):", count_digits(-12345))
    print("reverse_number(1200):", reverse_number(1200))
    print("reverse_number(-123):", reverse_number(-123))

    for value in [0, 1, 2, 9, 10, 11, 121, 122, -121]:
        print(
            f"is_palindrome_number({value}) = "
            f"{is_palindrome_number(value)}"
        )

    for value in [-10, -1, 0, 1, 2, 3, 4, 17, 25]:
        print(f"is_prime_optimized({value}) = {is_prime_optimized(value)}")

    print("fibonacci_sequence(0):", fibonacci_sequence(0))
    print("fibonacci_sequence(1):", fibonacci_sequence(1))
    print("fibonacci_sequence(8):", fibonacci_sequence(8))


# ============================================================================
# 15. COMPARING LOOP STYLES
# ============================================================================

def sum_with_for_loop(limit: int) -> int:
    total = 0

    for number in range(1, limit + 1):
        total += number

    return total


def sum_with_while_loop(limit: int) -> int:
    total = 0
    number = 1

    while number <= limit:
        total += number
        number += 1

    return total


def sum_with_formula(limit: int) -> int:
    """
    Mathematical alternative:
        1 + 2 + ... + n = n(n + 1) / 2

    This is O(1), unlike the explicit loop approaches.
    """
    return limit * (limit + 1) // 2


def compare_sum_methods(limit: int) -> None:
    section("15. LOOP VERSUS MATHEMATICAL FORMULA")

    start = time.perf_counter()
    loop_result = sum_with_for_loop(limit)
    loop_time = time.perf_counter() - start

    start = time.perf_counter()
    formula_result = sum_with_formula(limit)
    formula_time = time.perf_counter() - start

    print("Loop result:", loop_result)
    print("Formula result:", formula_result)
    print(f"Loop time: {loop_time:.8f} seconds")
    print(f"Formula time: {formula_time:.8f} seconds")

    if loop_result != formula_result:
        raise AssertionError("methods produced different results")


# ============================================================================
# 16. A SMALL ALGORITHM CASE STUDY
# ============================================================================

class NumberAnalyzer:
    """
    A reusable class that combines several loop-based algorithms.

    This illustrates how simple loop operations can become components
    of a larger application.
    """

    def __init__(self, numbers: Iterable[int]) -> None:
        self.numbers = list(numbers)

    def total(self) -> int:
        total = 0

        for number in self.numbers:
            total += number

        return total

    def positive_numbers(self) -> List[int]:
        result = []

        for number in self.numbers:
            if number > 0:
                result.append(number)

        return result

    def even_numbers(self) -> List[int]:
        result = []

        for number in self.numbers:
            if number % 2 == 0:
                result.append(number)

        return result

    def prime_numbers(self) -> List[int]:
        result = []

        for number in self.numbers:
            if is_prime_optimized(number):
                result.append(number)

        return result

    def frequency_table(self) -> dict[int, int]:
        frequencies: dict[int, int] = {}

        for number in self.numbers:
            frequencies[number] = frequencies.get(number, 0) + 1

        return frequencies


# ============================================================================
# 17. TWO-DIMENSIONAL DATA PROCESSING
# ============================================================================

def calculate_matrix_row_sums(matrix: List[List[int]]) -> List[int]:
    """Calculate one sum for every matrix row."""
    row_sums = []

    for row in matrix:
        total = 0

        for value in row:
            total += value

        row_sums.append(total)

    return row_sums


def calculate_matrix_column_sums(matrix: List[List[int]]) -> List[int]:
    """
    Calculate column sums for a rectangular matrix.

    Validation is important because nested loops rely on consistent
    dimensions.
    """
    if not matrix:
        return []

    column_count = len(matrix[0])

    for row in matrix:
        if len(row) != column_count:
            raise ValueError("matrix must be rectangular")

    column_sums = [0] * column_count

    for row in matrix:
        for column_index in range(column_count):
            column_sums[column_index] += row[column_index]

    return column_sums


# ============================================================================
# 18. ITERATORS AND LOOP PROTOCOL
# ============================================================================

class Countdown:
    """
    A custom iterable that can be consumed by a for loop.

    Python's for loop repeatedly calls __next__() until StopIteration.
    """

    def __init__(self, start: int) -> None:
        self.start = start

    def __iter__(self) -> Iterator[int]:
        current = self.start

        while current >= 0:
            yield current
            current -= 1


def demonstrate_custom_iterable() -> None:
    section("18. CUSTOM ITERABLE")

    for value in Countdown(5):
        print(value, end=" ")
    print()


# ============================================================================
# 19. COMMON LOOP MISTAKES
# ============================================================================

def demonstrate_common_mistakes_correctly() -> None:
    section("19. COMMON LOOP MISTAKES")

    print("Mistake prevention: update the while-loop state.")
    counter = 0

    while counter < 3:
        print(counter, end=" ")
        counter += 1
    print()

    print("Avoid modifying a collection while iterating over it.")
    original = [1, 2, 3, 4, 5]

    filtered = []

    for value in original:
        if value % 2 == 0:
            filtered.append(value)

    print("Original:", original)
    print("Filtered:", filtered)

    print("Use range correctly: stop is exclusive.")
    for value in range(1, 5):
        print(value, end=" ")
    print()


# ============================================================================
# 20. COMPLEXITY EXAMPLES
# ============================================================================

def linear_work(limit: int) -> int:
    """One loop: O(n)."""
    operations = 0

    for _ in range(limit):
        operations += 1

    return operations


def quadratic_work(limit: int) -> int:
    """Two independent nested loops: O(n²)."""
    operations = 0

    for _ in range(limit):
        for _ in range(limit):
            operations += 1

    return operations


def triangular_nested_work(limit: int) -> int:
    """
    Inner loop gets progressively longer.

    Number of iterations is:
        1 + 2 + ... + n = n(n+1)/2
    which is still O(n²).
    """
    operations = 0

    for outer in range(1, limit + 1):
        for _ in range(outer):
            operations += 1

    return operations


# ============================================================================
# 21. PRACTICE EXAMPLES
# ============================================================================

def practice_examples() -> None:
    section("21. PRACTICE PROBLEMS")

    print("Number sequence:")
    print_number_sequence(1, 10)

    print("Sum from 1 to 100:", sum_with_loop(range(1, 101)))

    print("Factorial of 5:", factorial_iterative(5))

    print("\nMultiplication table of 7:")
    print_multiplication_table(7)

    print("\nDigits in 987654:", count_digits(987654))

    print("Reverse of 123456:", reverse_number(123456))

    print("Is 1221 a palindrome?", is_palindrome_number(1221))

    print("Primes through 50:", generate_primes(50))

    print("First 12 Fibonacci numbers:", fibonacci_sequence(12))

    print("\nRight triangle:")
    for line in right_triangle_pattern(5):
        print(line)


# ============================================================================
# 22. AUTOMATED TESTS
# ============================================================================

def run_tests() -> None:
    """Run assertions covering the main algorithms."""
    section("22. AUTOMATED TESTS")

    assert generate_number_sequence(1, 5) == [1, 2, 3, 4, 5]
    assert generate_number_sequence(5, 1, -1) == [5, 4, 3, 2, 1]

    assert sum_with_loop([1, 2, 3, 4]) == 10
    assert sum_with_while([1, 2, 3, 4]) == 10
    assert sum_even_numbers(10) == 30

    assert factorial_iterative(0) == 1
    assert factorial_iterative(5) == 120
    assert factorial_while(6) == 720

    assert count_digits(0) == 1
    assert count_digits(12345) == 5
    assert count_digits(-12345) == 5

    assert reverse_number(12345) == 54321
    assert reverse_number(1200) == 21

    assert is_palindrome_number(0)
    assert is_palindrome_number(1221)
    assert not is_palindrome_number(1234)
    assert not is_palindrome_number(-121)

    assert is_prime_optimized(2)
    assert is_prime_optimized(97)
    assert not is_prime_optimized(1)
    assert not is_prime_optimized(100)

    assert fibonacci_sequence(8) == [0, 1, 1, 2, 3, 5, 8, 13]

    analyzer = NumberAnalyzer([1, 2, 2, 3, 5, 6])
    assert analyzer.total() == 19
    assert analyzer.even_numbers() == [2, 2, 6]
    assert analyzer.prime_numbers() == [2, 2, 3, 5]
    assert analyzer.frequency_table() == {1: 1, 2: 2, 3: 1, 5: 1, 6: 1}

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    assert calculate_matrix_row_sums(matrix) == [6, 15]
    assert calculate_matrix_column_sums(matrix) == [5, 7, 9]

    assert linear_work(10) == 10
    assert quadratic_work(4) == 16
    assert triangular_nested_work(4) == 10

    print("All tests passed.")


# ============================================================================
# 23. MAIN PROGRAM
# ============================================================================

def main() -> None:
    section("DAY 4 — LOOPS")

    demonstrate_for_loop()
    demonstrate_loop_counter()
    demonstrate_while_loop()
    demonstrate_do_while_behavior()
    demonstrate_break_and_continue()

    section("NUMBER SEQUENCE EXAMPLES")
    print_number_sequence(1, 10)
    print_number_sequence(10, 1, -1)

    section("SUM EXAMPLES")
    values = [1, 2, 3, 4, 5]
    print("for-loop sum:", sum_with_loop(values))
    print("while-loop sum:", sum_with_while(values))
    print("even-number sum through 20:", sum_even_numbers(20))

    section("FACTORIAL")
    for value in range(0, 8):
        print(f"{value}! = {factorial_iterative(value)}")

    section("MULTIPLICATION TABLE")
    print_multiplication_table(8)

    section("DIGIT OPERATIONS")
    print("Count:", count_digits(123456789))
    print("Reverse:", reverse_number(123456789))
    print("Digit sum:", sum_of_digits(123456789))

    section("PALINDROMES")
    for value in [121, 123, 1331, 12321]:
        print(value, is_palindrome_number(value))

    section("PRIMES")
    print("Primes through 30:", generate_primes(30))

    section("FIBONACCI")
    print(fibonacci_sequence(15))

    section("PATTERNS")
    for line in square_pattern(4):
        print(line)

    print()

    for line in right_triangle_pattern(5):
        print(line)

    print()

    for line in number_triangle(5):
        print(line)

    section("MULTIPLICATION GRID")
    print_multiplication_grid(5)

    section("SEARCH")
    print("First multiple of 7:", first_multiple(range(1, 100), 7))
    print("First prime from 50 through 100:", find_first_prime(50, 100))

    negatives, zeroes, positives = classify_numbers(3)
    print("Negatives:", negatives)
    print("Zeroes:", zeroes)
    print("Positives:", positives)

    section("ACCUMULATORS")
    sample_numbers = [8, 3, 9, 3, 1, 9, 9]
    print("Maximum:", maximum_with_loop(sample_numbers))
    print("Occurrences of 9:", count_occurrences(sample_numbers, 9))

    demonstrate_validation_without_interactive_input()
    demonstrate_edge_cases()
    compare_sum_methods(100_000)

    section("NUMBER ANALYZER CASE STUDY")
    analyzer = NumberAnalyzer([12, 7, 7, 13, 20, 29, 30, 30])
    print("Numbers:", analyzer.numbers)
    print("Total:", analyzer.total())
    print("Positive:", analyzer.positive_numbers())
    print("Even:", analyzer.even_numbers())
    print("Prime:", analyzer.prime_numbers())
    print("Frequency:", analyzer.frequency_table())

    section("MATRIX PROCESSING")
    matrix = [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90],
    ]

    print("Row sums:", calculate_matrix_row_sums(matrix))
    print("Column sums:", calculate_matrix_column_sums(matrix))

    demonstrate_custom_iterable()
    demonstrate_common_mistakes_correctly()

    section("COMPLEXITY")
    for size in [5, 10, 100]:
        print(
            f"n={size}: "
            f"linear={linear_work(size)}, "
            f"quadratic={quadratic_work(size)}, "
            f"triangular={triangular_nested_work(size)}"
        )

    practice_examples()
    run_tests()

    section("DAY 4 COMPLETE")
    print("The core loop patterns have been demonstrated and tested.")


if __name__ == "__main__":
    main()
