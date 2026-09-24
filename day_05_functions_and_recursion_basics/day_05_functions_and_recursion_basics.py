"""
Day 5 — Functions and Recursion Basics
A comprehensive standalone study and practice program.

Topics covered:
- Function declaration and definition
- Parameters and arguments
- Return values
- Local variables and scope
- Function composition
- Iteration versus recursion
- Recursive functions
- Base cases
- Recursive calls
- Call stack
- Factorial
- Fibonacci
- Power calculation
- Greatest common divisor
- Sum of digits
- Recursive countdown
- Recursive array traversal
- Input validation
- Error handling
- Testing
- Memoization
- Tail-recursive style
- Recursive divide-and-conquer
- Performance and recursion limits
- Practical design considerations
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Iterable, Sequence
import sys
import time


# ============================================================================
# 1. FUNCTION FUNDAMENTALS
# ============================================================================

def greet(name: str) -> str:
    """Return a greeting.

    A function packages a reusable operation under a meaningful name.
    """
    return f"Hello, {name}!"


def add(first_number: int, second_number: int) -> int:
    """Return the sum of two integers."""
    return first_number + second_number


def multiply(first_number: int, second_number: int) -> int:
    """Return the product of two integers."""
    return first_number * second_number


def demonstrate_basic_functions() -> None:
    print("\n=== 1. FUNCTION FUNDAMENTALS ===")

    message = greet("Atul")
    print(message)

    result = add(10, 20)
    print("10 + 20 =", result)

    product = multiply(6, 7)
    print("6 × 7 =", product)


# ============================================================================
# 2. PARAMETERS, ARGUMENTS, DEFAULTS, AND KEYWORD ARGUMENTS
# ============================================================================

def describe_person(
    name: str,
    age: int,
    country: str = "India",
) -> str:
    """Demonstrate required and default parameters."""
    return f"{name} is {age} years old and lives in {country}."


def calculate_rectangle_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    if length < 0 or width < 0:
        raise ValueError("Length and width cannot be negative.")
    return length * width


def demonstrate_parameters() -> None:
    print("\n=== 2. PARAMETERS AND ARGUMENTS ===")

    print(describe_person("Atul", 25))
    print(describe_person(name="Atul", age=25, country="India"))

    print("Rectangle area:", calculate_rectangle_area(10, 5))


# ============================================================================
# 3. RETURN VALUES
# ============================================================================

def divide(dividend: float, divisor: float) -> float:
    """Return a quotient while explicitly handling division by zero."""
    if divisor == 0:
        raise ZeroDivisionError("A number cannot be divided by zero.")
    return dividend / divisor


def square(number: float) -> float:
    return number * number


def demonstrate_return_values() -> None:
    print("\n=== 3. RETURN VALUES ===")

    quotient = divide(20, 4)
    print("20 / 4 =", quotient)

    value = square(8)
    print("8² =", value)

    try:
        divide(10, 0)
    except ZeroDivisionError as error:
        print("Handled error:", error)


# ============================================================================
# 4. LOCAL VARIABLES AND SCOPE
# ============================================================================

global_demo_value = "global value"


def scope_example() -> str:
    # This variable exists only while this function is executing.
    local_demo_value = "local value"
    return local_demo_value


def demonstrate_scope() -> None:
    print("\n=== 4. LOCAL VARIABLES AND SCOPE ===")

    print("Global variable:", global_demo_value)
    print("Local variable returned by function:", scope_example())

    # local_demo_value cannot be accessed here because it belongs to
    # scope_example(). Uncommenting the following line would cause NameError:
    # print(local_demo_value)


# ============================================================================
# 5. FUNCTION COMPOSITION
# ============================================================================

def double(number: int) -> int:
    return number * 2


def increment(number: int) -> int:
    return number + 1


def double_then_increment(number: int) -> int:
    """Compose two smaller functions into one operation."""
    doubled = double(number)
    return increment(doubled)


def normalize_score(score: float) -> float:
    """Clamp a score to the valid range [0, 100]."""
    return max(0.0, min(100.0, score))


def calculate_percentage(obtained: float, maximum: float) -> float:
    if maximum <= 0:
        raise ValueError("Maximum marks must be positive.")
    return normalize_score((obtained / maximum) * 100)


def demonstrate_function_composition() -> None:
    print("\n=== 5. FUNCTION COMPOSITION ===")

    print("double_then_increment(5):", double_then_increment(5))
    print("Percentage:", calculate_percentage(72, 100))


# ============================================================================
# 6. ITERATION VERSUS RECURSION
# ============================================================================

def factorial_iterative(number: int) -> int:
    """Calculate factorial using iteration.

    Iteration repeats work with an explicit loop.
    """
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    result = 1
    for current in range(2, number + 1):
        result *= current

    return result


def factorial_recursive(number: int) -> int:
    """Calculate factorial using recursion.

    Mathematical definition:
        0! = 1
        n! = n × (n - 1)! for n > 0

    The condition number == 0 is the base case.
    Without it, recursive calls would never terminate.
    """
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    # Base case: stop recursion.
    if number == 0:
        return 1

    # Recursive case: reduce the problem toward the base case.
    return number * factorial_recursive(number - 1)


def demonstrate_iteration_vs_recursion() -> None:
    print("\n=== 6. ITERATION VERSUS RECURSION ===")

    for value in range(6):
        iterative_result = factorial_iterative(value)
        recursive_result = factorial_recursive(value)

        print(
            f"{value}! -> iterative={iterative_result}, "
            f"recursive={recursive_result}"
        )


# ============================================================================
# 7. CALL STACK VISUALIZATION
# ============================================================================

def countdown(number: int) -> None:
    """Print a recursive countdown and demonstrate call-stack behavior."""
    if number < 0:
        raise ValueError("Countdown cannot start below zero.")

    # Base case.
    if number == 0:
        print("0 -> base case reached")
        return

    print(f"{number} -> recursive call to countdown({number - 1})")

    # Each call remains on the call stack while the next call executes.
    countdown(number - 1)


def demonstrate_call_stack() -> None:
    print("\n=== 7. CALL STACK AND RECURSIVE COUNTDOWN ===")
    countdown(5)


# ============================================================================
# 8. FACTORIAL
# ============================================================================

def demonstrate_factorial() -> None:
    print("\n=== 8. FACTORIAL ===")

    for value in [0, 1, 3, 5, 10]:
        print(f"{value}! =", factorial_recursive(value))

    print("Important: 0! =", factorial_recursive(0))


# ============================================================================
# 9. POWER CALCULATION
# ============================================================================

def power_recursive(base: float, exponent: int) -> float:
    """Calculate base^exponent recursively.

    This implementation supports negative exponents and uses exponentiation
    by squaring, reducing the number of recursive calls.

    For even n:
        x^n = (x^(n/2))²

    For odd n:
        x^n = x × x^(n-1)

    The zero exponent is the base case.
    """
    if base == 0 and exponent < 0:
        raise ValueError("Zero cannot be raised to a negative exponent.")

    if exponent == 0:
        return 1.0

    if exponent < 0:
        return 1.0 / power_recursive(base, -exponent)

    half_power = power_recursive(base, exponent // 2)

    if exponent % 2 == 0:
        return half_power * half_power

    return base * half_power * half_power


def demonstrate_power() -> None:
    print("\n=== 9. RECURSIVE POWER CALCULATION ===")

    examples = [
        (2, 0),
        (2, 5),
        (3, 4),
        (10, 3),
        (2, -3),
    ]

    for base, exponent in examples:
        print(f"{base}^{exponent} =", power_recursive(base, exponent))


# ============================================================================
# 10. GREATEST COMMON DIVISOR
# ============================================================================

def gcd_recursive(first: int, second: int) -> int:
    """Calculate GCD using Euclid's recursive algorithm.

    gcd(a, b) = gcd(b, a mod b)
    Base case:
        gcd(a, 0) = |a|
    """
    first = abs(first)
    second = abs(second)

    if second == 0:
        return first

    return gcd_recursive(second, first % second)


def gcd_iterative(first: int, second: int) -> int:
    """Iterative equivalent of Euclid's algorithm."""
    first = abs(first)
    second = abs(second)

    while second != 0:
        first, second = second, first % second

    return first


def demonstrate_gcd() -> None:
    print("\n=== 10. GREATEST COMMON DIVISOR ===")

    pairs = [(48, 18), (100, 35), (17, 13), (0, 15), (-48, 18)]

    for first, second in pairs:
        print(
            f"gcd({first}, {second}) = "
            f"{gcd_recursive(first, second)}"
        )


# ============================================================================
# 11. SUM OF DIGITS
# ============================================================================

def sum_of_digits(number: int) -> int:
    """Return the sum of decimal digits recursively."""
    number = abs(number)

    # Base case: a single digit needs no further decomposition.
    if number < 10:
        return number

    return (number % 10) + sum_of_digits(number // 10)


def demonstrate_sum_of_digits() -> None:
    print("\n=== 11. SUM OF DIGITS ===")

    for number in [0, 5, 123, 9876, -54321]:
        print(f"sum_of_digits({number}) =", sum_of_digits(number))


# ============================================================================
# 12. FIBONACCI
# ============================================================================

def fibonacci_recursive(number: int) -> int:
    """Naive recursive Fibonacci implementation.

    Definition:
        F(0) = 0
        F(1) = 1
        F(n) = F(n-1) + F(n-2)

    This implementation is intentionally simple so that the recursive
    structure is visible. It has exponential time complexity.
    """
    if number < 0:
        raise ValueError("Fibonacci requires a non-negative integer.")

    if number <= 1:
        return number

    return (
        fibonacci_recursive(number - 1)
        + fibonacci_recursive(number - 2)
    )


@lru_cache(maxsize=None)
def fibonacci_memoized(number: int) -> int:
    """Memoized Fibonacci.

    Previously calculated values are cached, eliminating repeated work.
    """
    if number < 0:
        raise ValueError("Fibonacci requires a non-negative integer.")

    if number <= 1:
        return number

    return (
        fibonacci_memoized(number - 1)
        + fibonacci_memoized(number - 2)
    )


def fibonacci_iterative(number: int) -> int:
    """Efficient iterative Fibonacci implementation."""
    if number < 0:
        raise ValueError("Fibonacci requires a non-negative integer.")

    first, second = 0, 1

    for _ in range(number):
        first, second = second, first + second

    return first


def demonstrate_fibonacci() -> None:
    print("\n=== 12. FIBONACCI ===")

    print("First 12 Fibonacci values:")
    print([fibonacci_recursive(index) for index in range(12)])

    print("Memoized Fibonacci F(40):", fibonacci_memoized(40))
    print("Iterative Fibonacci F(40):", fibonacci_iterative(40))


# ============================================================================
# 13. RECURSIVE ARRAY TRAVERSAL
# ============================================================================

def recursive_array_traversal(
    values: Sequence[int],
    index: int = 0,
) -> None:
    """Visit each array/list element recursively."""
    if index >= len(values):
        return

    print(f"index={index}, value={values[index]}")
    recursive_array_traversal(values, index + 1)


def recursive_array_sum(
    values: Sequence[int],
    index: int = 0,
) -> int:
    """Calculate the sum of a sequence recursively."""
    if index >= len(values):
        return 0

    return values[index] + recursive_array_sum(values, index + 1)


def recursive_array_maximum(
    values: Sequence[int],
    index: int = 0,
) -> int:
    """Find the maximum element recursively."""
    if not values:
        raise ValueError("Cannot find a maximum in an empty sequence.")

    if index == len(values) - 1:
        return values[index]

    remaining_maximum = recursive_array_maximum(values, index + 1)
    return max(values[index], remaining_maximum)


def demonstrate_recursive_array_operations() -> None:
    print("\n=== 13. RECURSIVE ARRAY TRAVERSAL ===")

    values = [4, 8, 15, 16, 23, 42]

    print("Traversal:")
    recursive_array_traversal(values)

    print("Recursive sum:", recursive_array_sum(values))
    print("Recursive maximum:", recursive_array_maximum(values))


# ============================================================================
# 14. RECURSIVE STRING PROCESSING
# ============================================================================

def reverse_string_recursive(text: str) -> str:
    """Reverse a string recursively."""
    if len(text) <= 1:
        return text

    return text[-1] + reverse_string_recursive(text[:-1])


def is_palindrome_recursive(text: str) -> bool:
    """Determine whether a string is a palindrome recursively."""
    normalized = "".join(character.lower() for character in text if character.isalnum())

    if len(normalized) <= 1:
        return True

    if normalized[0] != normalized[-1]:
        return False

    return is_palindrome_recursive(normalized[1:-1])


def demonstrate_recursive_strings() -> None:
    print("\n=== 14. RECURSIVE STRING PROCESSING ===")

    for text in ["recursion", "level", "radar", "Python"]:
        print(f"reverse({text!r}) =", reverse_string_recursive(text))
        print(f"palindrome({text!r}) =", is_palindrome_recursive(text))


# ============================================================================
# 15. RECURSIVE BINARY SEARCH
# ============================================================================

def binary_search_recursive(
    sorted_values: Sequence[int],
    target: int,
    left: int = 0,
    right: int | None = None,
) -> int:
    """Return target index using recursive binary search.

    The input must already be sorted.
    Each recursive call discards approximately half of the search space.
    """
    if right is None:
        right = len(sorted_values) - 1

    if left > right:
        return -1

    middle = left + (right - left) // 2

    if sorted_values[middle] == target:
        return middle

    if target < sorted_values[middle]:
        return binary_search_recursive(
            sorted_values,
            target,
            left,
            middle - 1,
        )

    return binary_search_recursive(
        sorted_values,
        target,
        middle + 1,
        right,
    )


def demonstrate_binary_search() -> None:
    print("\n=== 15. RECURSIVE BINARY SEARCH ===")

    values = [3, 7, 11, 18, 21, 27, 35, 42]

    for target in [3, 21, 42, 100]:
        print(
            f"Search for {target}:",
            binary_search_recursive(values, target),
        )


# ============================================================================
# 16. RECURSIVE MERGE SORT
# ============================================================================

def merge(left: Sequence[int], right: Sequence[int]) -> list[int]:
    """Merge two sorted sequences."""
    result: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result


def merge_sort_recursive(values: Sequence[int]) -> list[int]:
    """Sort values using recursive divide-and-conquer."""
    if len(values) <= 1:
        return list(values)

    middle = len(values) // 2

    left_half = merge_sort_recursive(values[:middle])
    right_half = merge_sort_recursive(values[middle:])

    return merge(left_half, right_half)


def demonstrate_merge_sort() -> None:
    print("\n=== 16. RECURSIVE MERGE SORT ===")

    values = [38, 27, 43, 3, 9, 82, 10]
    print("Original:", values)
    print("Sorted:", merge_sort_recursive(values))


# ============================================================================
# 17. TREE-LIKE RECURSION
# ============================================================================

@dataclass
class TreeNode:
    """A minimal binary-tree node used to demonstrate recursion."""

    value: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def inorder_traversal(node: TreeNode | None) -> list[int]:
    """Visit left subtree, root, then right subtree."""
    if node is None:
        return []

    return (
        inorder_traversal(node.left)
        + [node.value]
        + inorder_traversal(node.right)
    )


def demonstrate_tree_recursion() -> None:
    print("\n=== 17. TREE RECURSION ===")

    tree = TreeNode(
        10,
        left=TreeNode(
            5,
            left=TreeNode(2),
            right=TreeNode(7),
        ),
        right=TreeNode(
            15,
            left=TreeNode(12),
            right=TreeNode(20),
        ),
    )

    print("In-order traversal:", inorder_traversal(tree))


# ============================================================================
# 18. MULTIPLE RECURSIVE CALLS
# ============================================================================

def count_paths(rows: int, columns: int) -> int:
    """Count paths through a grid moving only right or down.

    This intentionally demonstrates branching recursion.
    """
    if rows <= 0 or columns <= 0:
        return 0

    if rows == 1 or columns == 1:
        return 1

    return (
        count_paths(rows - 1, columns)
        + count_paths(rows, columns - 1)
    )


@lru_cache(maxsize=None)
def count_paths_memoized(rows: int, columns: int) -> int:
    """Memoized version of the grid-path recurrence."""
    if rows <= 0 or columns <= 0:
        return 0

    if rows == 1 or columns == 1:
        return 1

    return (
        count_paths_memoized(rows - 1, columns)
        + count_paths_memoized(rows, columns - 1)
    )


def demonstrate_branching_recursion() -> None:
    print("\n=== 18. BRANCHING RECURSION ===")

    print("3×3 grid paths:", count_paths(3, 3))
    print("10×10 grid paths with memoization:",
          count_paths_memoized(10, 10))


# ============================================================================
# 19. INPUT VALIDATION AND SAFE FUNCTION DESIGN
# ============================================================================

def read_non_negative_integer(
    prompt: str,
    input_function: Callable[[str], str] = input,
) -> int:
    """Read and validate a non-negative integer."""
    while True:
        raw_value = input_function(prompt).strip()

        try:
            value = int(raw_value)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if value < 0:
            print("Please enter a non-negative number.")
            continue

        return value


def demonstrate_validation_without_interactive_input() -> None:
    print("\n=== 19. VALIDATION AND SAFE FUNCTION DESIGN ===")

    test_values = ["10", "-4", "abc", "0"]

    for raw_value in test_values:
        try:
            value = int(raw_value)

            if value < 0:
                raise ValueError("Value must be non-negative.")

            print(f"{raw_value!r} accepted as {value}")
        except ValueError as error:
            print(f"{raw_value!r} rejected: {error}")


# ============================================================================
# 20. RECURSION LIMIT AND STACK CONSIDERATIONS
# ============================================================================

def recursion_limit_information() -> None:
    print("\n=== 20. RECURSION LIMIT ===")
    print("Python recursion limit:", sys.getrecursionlimit())
    print(
        "Deep recursion can raise RecursionError. "
        "Iteration is often safer for very deep linear work."
    )


# ============================================================================
# 21. PERFORMANCE COMPARISON
# ============================================================================

def measure_function(
    function: Callable[[int], int],
    argument: int,
) -> tuple[int, float]:
    """Measure result and elapsed execution time."""
    start = time.perf_counter()
    result = function(argument)
    elapsed = time.perf_counter() - start
    return result, elapsed


def demonstrate_performance() -> None:
    print("\n=== 21. PERFORMANCE COMPARISON ===")

    number = 30

    _, recursive_time = measure_function(
        fibonacci_recursive,
        number,
    )

    _, memoized_time = measure_function(
        fibonacci_memoized,
        number,
    )

    _, iterative_time = measure_function(
        fibonacci_iterative,
        number,
    )

    print(f"Naive recursive Fibonacci({number}): {recursive_time:.6f}s")
    print(f"Memoized Fibonacci({number}): {memoized_time:.6f}s")
    print(f"Iterative Fibonacci({number}): {iterative_time:.6f}s")


# ============================================================================
# 22. UNIT-STYLE TESTS
# ============================================================================

def run_assertion_tests() -> None:
    print("\n=== 22. FUNCTION TESTS ===")

    assert add(2, 3) == 5
    assert multiply(4, 5) == 20

    assert factorial_recursive(0) == 1
    assert factorial_recursive(5) == 120

    assert power_recursive(2, 10) == 1024
    assert power_recursive(2, -2) == 0.25

    assert gcd_recursive(48, 18) == 6
    assert gcd_recursive(0, 15) == 15

    assert sum_of_digits(12345) == 15

    assert fibonacci_iterative(0) == 0
    assert fibonacci_iterative(10) == 55
    assert fibonacci_memoized(10) == 55

    assert recursive_array_sum([1, 2, 3, 4]) == 10
    assert recursive_array_maximum([8, 2, 10, 4]) == 10

    assert reverse_string_recursive("abc") == "cba"
    assert is_palindrome_recursive("Level") is True
    assert is_palindrome_recursive("Python") is False

    assert binary_search_recursive([1, 3, 5, 7], 5) == 2
    assert binary_search_recursive([1, 3, 5, 7], 6) == -1

    assert merge_sort_recursive([5, 1, 4, 2, 3]) == [1, 2, 3, 4, 5]

    assert count_paths_memoized(3, 3) == 6

    print("All assertion tests passed.")


# ============================================================================
# 23. COMMON RECURSION FAILURES
# ============================================================================

def safe_factorial(number: int) -> int | None:
    """Demonstrate converting an expected validation error into None."""
    try:
        return factorial_recursive(number)
    except ValueError:
        return None


def demonstrate_edge_cases() -> None:
    print("\n=== 23. EDGE CASES AND FAILURE CONDITIONS ===")

    print("Factorial(-1):", safe_factorial(-1))

    try:
        power_recursive(0, -1)
    except ValueError as error:
        print("Power error:", error)

    try:
        recursive_array_maximum([])
    except ValueError as error:
        print("Maximum error:", error)

    print("Empty recursive traversal:")
    recursive_array_traversal([])


# ============================================================================
# 24. PRACTICAL FUNCTION PIPELINE
# ============================================================================

def clean_number(value: str) -> int:
    """Convert a string into a validated integer."""
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("The input is empty.")

    return int(cleaned)


def compute_digit_sum(value: str) -> int:
    """Compose parsing and recursive calculation."""
    number = clean_number(value)
    return sum_of_digits(number)


def classify_digit_sum(value: str) -> str:
    """Compose multiple functions into a small processing pipeline."""
    digit_sum = compute_digit_sum(value)

    if digit_sum == 0:
        return "zero"

    if digit_sum % 2 == 0:
        return "even digit sum"

    return "odd digit sum"


def demonstrate_function_pipeline() -> None:
    print("\n=== 24. FUNCTION COMPOSITION PIPELINE ===")

    for value in ["12345", "2468", "0"]:
        print(
            f"{value}: digit sum={compute_digit_sum(value)}, "
            f"classification={classify_digit_sum(value)}"
        )


# ============================================================================
# 25. MAIN STUDY PROGRAM
# ============================================================================

def main() -> None:
    """Run the complete Day 5 study demonstrations."""
    print("=" * 78)
    print("DAY 5 — FUNCTIONS AND RECURSION BASICS")
    print("=" * 78)

    demonstrate_basic_functions()
    demonstrate_parameters()
    demonstrate_return_values()
    demonstrate_scope()
    demonstrate_function_composition()
    demonstrate_iteration_vs_recursion()
    demonstrate_call_stack()
    demonstrate_factorial()
    demonstrate_power()
    demonstrate_gcd()
    demonstrate_sum_of_digits()
    demonstrate_fibonacci()
    demonstrate_recursive_array_operations()
    demonstrate_recursive_strings()
    demonstrate_binary_search()
    demonstrate_merge_sort()
    demonstrate_tree_recursion()
    demonstrate_branching_recursion()
    demonstrate_validation_without_interactive_input()
    recursion_limit_information()
    demonstrate_performance()
    run_assertion_tests()
    demonstrate_edge_cases()
    demonstrate_function_pipeline()

    print("\n" + "=" * 78)
    print("DAY 5 STUDY PROGRAM COMPLETED")
    print("=" * 78)


if __name__ == "__main__":
    main()
