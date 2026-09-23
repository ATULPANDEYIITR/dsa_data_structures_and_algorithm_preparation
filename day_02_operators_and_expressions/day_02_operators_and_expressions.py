"""
Operators and Expressions
=========================

A comprehensive standalone study program covering:
- Arithmetic operators
- Comparison operators
- Logical operators
- Assignment operators
- Increment and decrement concepts
- Modulo
- Operator precedence
- Expressions
- Practical numerical problems
- Validation and error handling
- Boolean logic
- Bitwise operators
- Membership and identity operators
- Chained comparisons
- Short-circuit evaluation
- Floating-point considerations
- Integer division
- Augmented assignment
- Conditional expressions
- Expression design and debugging
- Performance and implementation considerations

Python does not provide ++ or -- operators. Their conceptual role is
demonstrated using += 1 and -= 1.

The program is intentionally executable and educational. Run it directly
with Python 3.10+.
"""

from __future__ import annotations

import math
import operator
from dataclasses import dataclass
from typing import Callable


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a clear section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller section heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def show(label: str, value) -> None:
    """Print a labeled demonstration result."""
    print(f"{label:<42} -> {value!r}")


# ---------------------------------------------------------------------------
# 1. Expressions and values
# ---------------------------------------------------------------------------

def demonstrate_expressions() -> None:
    section("1. Expressions and values")

    # An expression is a combination of values, variables, operators,
    # function calls, and other constructs that Python evaluates to a value.
    age = 25
    years_to_retirement = 60 - age
    expression_result = (10 + 5) * 2

    show("age", age)
    show("60 - age", years_to_retirement)
    show("(10 + 5) * 2", expression_result)

    # Expressions can be nested.
    nested = ((8 + 4) * 3) - (20 // 5)
    show("Nested expression", nested)

    # Function calls are expressions too.
    show("abs(-42)", abs(-42))
    show("round(3.14159, 2)", round(3.14159, 2))

    # A Boolean expression produces True or False.
    temperature = 28
    is_hot = temperature > 25
    show("temperature > 25", is_hot)


# ---------------------------------------------------------------------------
# 2. Arithmetic operators
# ---------------------------------------------------------------------------

def demonstrate_arithmetic() -> None:
    section("2. Arithmetic operators")

    a = 17
    b = 5

    show("a + b", a + b)
    show("a - b", a - b)
    show("a * b", a * b)
    show("a / b", a / b)
    show("a // b", a // b)
    show("a % b", a % b)
    show("a ** b", a ** b)

    subsection("Arithmetic with negative values")

    values = [-17, -5, 5, 17]
    for left in values:
        for right in [3, -3]:
            if right != 0:
                print(
                    f"{left:>4} // {right:>3} = {left // right:>4}, "
                    f"{left:>4} % {right:>3} = {left % right:>4}"
                )

    # Python's // operator performs floor division, not truncation toward zero.
    show("7 // 2", 7 // 2)
    show("-7 // 2", -7 // 2)

    # Floating-point arithmetic may contain representation effects.
    floating_result = 0.1 + 0.2
    show("0.1 + 0.2", floating_result)
    show("isclose(0.1 + 0.2, 0.3)", math.isclose(floating_result, 0.3))


# ---------------------------------------------------------------------------
# 3. Modulo
# ---------------------------------------------------------------------------

def demonstrate_modulo() -> None:
    section("3. Modulo and remainder")

    number = 29

    show("29 % 2", number % 2)
    show("29 % 3", number % 3)
    show("29 % 5", number % 5)

    print("\nEven/odd rule:")
    for value in range(0, 11):
        classification = "even" if value % 2 == 0 else "odd"
        print(f"{value:2} -> {classification}")

    print("\nDivisibility rule:")
    divisors = [2, 3, 5, 7]
    for divisor in divisors:
        print(
            f"{number} is "
            f"{'divisible' if number % divisor == 0 else 'not divisible'} "
            f"by {divisor}"
        )

    subsection("Digit extraction with modulo and floor division")

    value = 58327
    original = value
    digits = []

    while value > 0:
        digit = value % 10
        digits.append(digit)
        value //= 10

    show("Original number", original)
    show("Digits from right to left", digits)
    show("Digit sum", sum(digits))

    # The same idea can be used to reverse an integer.
    reverse = 0
    value = original
    while value > 0:
        reverse = reverse * 10 + value % 10
        value //= 10

    show("Reversed number", reverse)


# ---------------------------------------------------------------------------
# 4. Comparison operators
# ---------------------------------------------------------------------------

def demonstrate_comparisons() -> None:
    section("4. Comparison operators")

    a = 10
    b = 20

    show("a == b", a == b)
    show("a != b", a != b)
    show("a < b", a < b)
    show("a <= b", a <= b)
    show("a > b", a > b)
    show("a >= b", a >= b)

    subsection("Chained comparisons")

    x = 15

    # Python permits mathematical-style chained comparisons.
    show("10 < x < 20", 10 < x < 20)
    show("0 <= x <= 100", 0 <= x <= 100)

    # This is equivalent in logical meaning to:
    show("(10 < x) and (x < 20)", (10 < x) and (x < 20))


# ---------------------------------------------------------------------------
# 5. Logical operators
# ---------------------------------------------------------------------------

def demonstrate_logical_operators() -> None:
    section("5. Logical operators")

    truth_values = [True, False]

    print("\nAND truth table")
    for left in truth_values:
        for right in truth_values:
            print(f"{left!s:<5} and {right!s:<5} = {left and right}")

    print("\nOR truth table")
    for left in truth_values:
        for right in truth_values:
            print(f"{left!s:<5} or  {right!s:<5} = {left or right}")

    print("\nNOT")
    for value in truth_values:
        print(f"not {value!s:<5} = {not value}")

    age = 25
    has_id = True
    is_allowed = age >= 18 and has_id
    show("Adult with valid ID", is_allowed)

    is_weekend = False
    is_holiday = True
    can_rest = is_weekend or is_holiday
    show("Weekend OR holiday", can_rest)

    subsection("Short-circuit evaluation")

    def expensive_check() -> bool:
        print("expensive_check() was evaluated")
        return True

    # Because the first operand of and is False, Python does not need to
    # evaluate the second operand.
    result = False and expensive_check()
    show("False and expensive_check()", result)

    # Because the first operand of or is True, the second operand is skipped.
    result = True or expensive_check()
    show("True or expensive_check()", result)


# ---------------------------------------------------------------------------
# 6. Assignment and augmented assignment
# ---------------------------------------------------------------------------

def demonstrate_assignment() -> None:
    section("6. Assignment operators")

    value = 10
    show("Initial value", value)

    value += 5
    show("value += 5", value)

    value -= 3
    show("value -= 3", value)

    value *= 2
    show("value *= 2", value)

    value /= 4
    show("value /= 4", value)

    value //= 2
    show("value //= 2", value)

    value **= 3
    show("value **= 3", value)

    value %= 5
    show("value %= 5", value)

    subsection("Multiple assignment")

    first, second = 10, 20
    show("first", first)
    show("second", second)

    # Python allows swapping without a temporary variable.
    first, second = second, first
    show("first after swap", first)
    show("second after swap", second)

    # Augmented assignment on mutable objects has important semantics.
    numbers = [1, 2, 3]
    numbers += [4, 5]
    show("List after += operation", numbers)


# ---------------------------------------------------------------------------
# 7. Increment and decrement concepts
# ---------------------------------------------------------------------------

def demonstrate_increment_decrement() -> None:
    section("7. Increment and decrement concepts")

    print(
        "Python intentionally does not have the C/C++/Java-style "
        "++ and -- operators."
    )

    counter = 0

    # The normal Python equivalent of incrementing is += 1.
    for _ in range(5):
        counter += 1
        print(f"Incremented counter: {counter}")

    for _ in range(3):
        counter -= 1
        print(f"Decremented counter: {counter}")

    # Prefix/postfix distinctions found in languages such as C++ do not
    # exist as operators in Python.
    print(
        "Python uses explicit assignment such as counter += 1 and "
        "counter -= 1 instead of ++ and --."
    )


# ---------------------------------------------------------------------------
# 8. Operator precedence
# ---------------------------------------------------------------------------

def demonstrate_precedence() -> None:
    section("8. Operator precedence")

    # Multiplication happens before addition.
    show("2 + 3 * 4", 2 + 3 * 4)

    # Parentheses explicitly control evaluation order.
    show("(2 + 3) * 4", (2 + 3) * 4)

    show("20 - 4 * 3", 20 - 4 * 3)
    show("(20 - 4) * 3", (20 - 4) * 3)

    show("2 ** 3 * 2", 2 ** 3 * 2)

    subsection("A practical precedence example")

    principal = 1000
    annual_rate = 0.08
    years = 2

    wrong_without_parentheses = principal * 1 + annual_rate ** years
    correct = principal * (1 + annual_rate) ** years

    show("Incorrectly structured expression", wrong_without_parentheses)
    show("Correct compound-growth expression", correct)

    print(
        "\nImportant rule: use parentheses when the intended evaluation "
        "order is important to readability or correctness."
    )


# ---------------------------------------------------------------------------
# 9. Conditional expressions
# ---------------------------------------------------------------------------

def demonstrate_conditional_expressions() -> None:
    section("9. Conditional expressions")

    number = 17
    classification = "even" if number % 2 == 0 else "odd"
    show("Classification", classification)

    score = 82
    grade = (
        "A" if score >= 90
        else "B" if score >= 80
        else "C" if score >= 70
        else "D" if score >= 60
        else "F"
    )
    show("Grade", grade)

    print(
        "\nConditional expressions are useful for short decisions. "
        "For complex decisions, normal if/elif/else statements are usually clearer."
    )


# ---------------------------------------------------------------------------
# 10. Practical beginner problems
# ---------------------------------------------------------------------------

def is_even(number: int) -> bool:
    return number % 2 == 0


def is_positive(number: float) -> bool:
    return number > 0


def largest_of_two(a: float, b: float) -> float:
    return a if a >= b else b


def largest_of_three(a: float, b: float, c: float) -> float:
    return max(a, b, c)


def is_divisible(number: int, divisor: int) -> bool:
    if divisor == 0:
        raise ValueError("A divisor cannot be zero.")
    return number % divisor == 0


def digit_sum(number: int) -> int:
    value = abs(number)
    total = 0

    if value == 0:
        return 0

    while value > 0:
        total += value % 10
        value //= 10

    return total


def count_digits(number: int) -> int:
    value = abs(number)

    if value == 0:
        return 1

    count = 0
    while value > 0:
        value //= 10
        count += 1

    return count


def reverse_integer(number: int) -> int:
    sign = -1 if number < 0 else 1
    value = abs(number)
    result = 0

    while value > 0:
        result = result * 10 + value % 10
        value //= 10

    return sign * result


def demonstrate_beginner_problems() -> None:
    section("10. Beginner practice problems")

    numbers = [0, 1, 2, 17, -8, 101]

    for number in numbers:
        print(
            f"{number:>4}: "
            f"even={is_even(number)}, "
            f"positive={is_positive(number)}, "
            f"digits={count_digits(number)}, "
            f"digit_sum={digit_sum(number)}, "
            f"reverse={reverse_integer(number)}"
        )

    show("Largest of 10 and 25", largest_of_two(10, 25))
    show("Largest of 10, 25 and 17", largest_of_three(10, 25, 17))

    for divisor in [2, 3, 5, 7]:
        show(
            f"100 divisible by {divisor}",
            is_divisible(100, divisor),
        )


# ---------------------------------------------------------------------------
# 11. Calculator
# ---------------------------------------------------------------------------

OPERATIONS: dict[str, Callable[[float, float], float]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
}


def calculate(left: float, operation: str, right: float) -> float:
    if operation not in OPERATIONS:
        raise ValueError(f"Unsupported operator: {operation}")

    if operation in {"/", "//", "%"} and right == 0:
        raise ZeroDivisionError("Division or remainder by zero is undefined.")

    return OPERATIONS[operation](left, right)


def demonstrate_calculator() -> None:
    section("11. Simple calculator")

    examples = [
        (10, "+", 5),
        (10, "-", 5),
        (10, "*", 5),
        (10, "/", 5),
        (10, "//", 3),
        (10, "%", 3),
        (2, "**", 5),
    ]

    for left, operation, right in examples:
        result = calculate(left, operation, right)
        print(f"{left} {operation} {right} = {result}")

    subsection("Calculator error handling")

    invalid_operations = [
        (10, "/", 0),
        (10, "%", 0),
        (10, "$", 2),
    ]

    for left, operation, right in invalid_operations:
        try:
            result = calculate(left, operation, right)
            print(f"{left} {operation} {right} = {result}")
        except (ValueError, ZeroDivisionError) as error:
            print(f"{left} {operation} {right} -> ERROR: {error}")


# ---------------------------------------------------------------------------
# 12. Floating-point comparisons
# ---------------------------------------------------------------------------

def demonstrate_floating_point() -> None:
    section("12. Floating-point expressions")

    a = 0.1
    b = 0.2
    c = 0.3

    show("a + b", a + b)
    show("(a + b) == c", (a + b) == c)
    show("math.isclose(a + b, c)", math.isclose(a + b, c))

    # Decimal can be appropriate when decimal-exact arithmetic is required,
    # such as some financial calculations.
    from decimal import Decimal

    decimal_result = Decimal("0.1") + Decimal("0.2")
    show("Decimal('0.1') + Decimal('0.2')", decimal_result)
    show(
        "Decimal result equals Decimal('0.3')",
        decimal_result == Decimal("0.3"),
    )


# ---------------------------------------------------------------------------
# 13. Boolean values as part of expressions
# ---------------------------------------------------------------------------

def demonstrate_boolean_numerical_relationship() -> None:
    section("13. Boolean values and expressions")

    show("True == 1", True == 1)
    show("False == 0", False == 0)

    # bool is a subclass of int in Python. This is a language-specific
    # behavior that should be understood when writing generic numerical code.
    show("isinstance(True, int)", isinstance(True, int))

    values = [0, 1, 2, -1, "", "text", [], [1]]

    for value in values:
        print(f"{value!r:<10} -> bool(value) = {bool(value)}")


# ---------------------------------------------------------------------------
# 14. Bitwise operators
# ---------------------------------------------------------------------------

def demonstrate_bitwise_operators() -> None:
    section("14. Bitwise operators")

    a = 0b1100
    b = 0b1010

    show("a in binary", bin(a))
    show("b in binary", bin(b))
    show("a & b", bin(a & b))
    show("a | b", bin(a | b))
    show("a ^ b", bin(a ^ b))
    show("~a", bin(~a))
    show("a << 1", bin(a << 1))
    show("a >> 1", bin(a >> 1))

    print(
        "\nBitwise operations work on integer bit patterns and are "
        "different from logical operations such as and/or."
    )

    # A common bitmask example.
    READ = 0b001
    WRITE = 0b010
    EXECUTE = 0b100

    permissions = READ | WRITE

    show("Permissions", bin(permissions))
    show("Has READ", bool(permissions & READ))
    show("Has EXECUTE", bool(permissions & EXECUTE))

    permissions |= EXECUTE
    show("After adding EXECUTE", bin(permissions))

    permissions &= ~WRITE
    show("After removing WRITE", bin(permissions))


# ---------------------------------------------------------------------------
# 15. Membership and identity
# ---------------------------------------------------------------------------

def demonstrate_membership_and_identity() -> None:
    section("15. Membership and identity operators")

    languages = ["Python", "JavaScript", "C++"]

    show("'Python' in languages", "Python" in languages)
    show("'Java' not in languages", "Java" not in languages)

    first = [1, 2, 3]
    second = [1, 2, 3]
    third = first

    show("first == second", first == second)
    show("first is second", first is second)
    show("first is third", first is third)

    # == compares values. is compares object identity.
    print(
        "\nUse == when you want to compare values. "
        "Use is primarily for identity checks such as value is None."
    )


# ---------------------------------------------------------------------------
# 16. Assignment expressions
# ---------------------------------------------------------------------------

def demonstrate_assignment_expression() -> None:
    section("16. Assignment expressions")

    # The := operator assigns a value inside an expression.
    if (length := len("operators")) > 5:
        print(f"The word contains {length} characters.")

    print(
        "Assignment expressions can reduce repeated computation, "
        "but they should be used only when they improve clarity."
    )


# ---------------------------------------------------------------------------
# 17. Operator overloading
# ---------------------------------------------------------------------------

@dataclass
class Vector2D:
    x: float
    y: float

    def __add__(self, other: "Vector2D") -> "Vector2D":
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)


def demonstrate_operator_overloading() -> None:
    section("17. Operator overloading")

    first = Vector2D(2, 3)
    second = Vector2D(5, 7)

    show("first + second", first + second)
    show("second - first", second - first)
    show("first * 3", first * 3)
    show("Magnitude of first", first.magnitude())

    print(
        "\nPython operators can invoke special methods such as __add__, "
        "__sub__, and __mul__. This allows domain-specific types to behave "
        "naturally while retaining explicit semantics."
    )


# ---------------------------------------------------------------------------
# 18. Validation and robust expressions
# ---------------------------------------------------------------------------

def safe_percentage(part: float, whole: float) -> float:
    if not math.isfinite(part) or not math.isfinite(whole):
        raise ValueError("Inputs must be finite numbers.")

    if whole == 0:
        raise ValueError("The whole value cannot be zero.")

    return part / whole * 100


def demonstrate_validation() -> None:
    section("18. Validation and robust expressions")

    examples = [
        (25, 100),
        (3, 12),
        (0, 100),
    ]

    for part, whole in examples:
        print(f"{part}/{whole} -> {safe_percentage(part, whole):.2f}%")

    invalid = [(10, 0), (math.inf, 100)]

    for part, whole in invalid:
        try:
            print(safe_percentage(part, whole))
        except ValueError as error:
            print(f"Invalid input {part}, {whole}: {error}")


# ---------------------------------------------------------------------------
# 19. Practical mathematical expressions
# ---------------------------------------------------------------------------

def demonstrate_mathematical_expressions() -> None:
    section("19. Practical mathematical expressions")

    # Rectangle
    length = 12
    width = 7
    rectangle_area = length * width
    rectangle_perimeter = 2 * (length + width)

    show("Rectangle area", rectangle_area)
    show("Rectangle perimeter", rectangle_perimeter)

    # Circle
    radius = 5
    circle_area = math.pi * radius ** 2
    circle_circumference = 2 * math.pi * radius

    show("Circle area", circle_area)
    show("Circle circumference", circle_circumference)

    # Simple interest
    principal = 10000
    rate = 7.5
    years = 3
    simple_interest = principal * rate * years / 100
    total_amount = principal + simple_interest

    show("Simple interest", simple_interest)
    show("Total amount", total_amount)

    # Celsius to Fahrenheit
    celsius = 25
    fahrenheit = celsius * 9 / 5 + 32
    show("25 Celsius in Fahrenheit", fahrenheit)


# ---------------------------------------------------------------------------
# 20. Compound expressions and debugging
# ---------------------------------------------------------------------------

def demonstrate_debugging_expressions() -> None:
    section("20. Debugging complex expressions")

    quantity = 8
    price = 125
    discount_rate = 0.10
    tax_rate = 0.18

    subtotal = quantity * price
    discount = subtotal * discount_rate
    discounted_price = subtotal - discount
    tax = discounted_price * tax_rate
    final_price = discounted_price + tax

    print("Breaking a complex expression into named steps:")
    show("subtotal", subtotal)
    show("discount", discount)
    show("discounted_price", discounted_price)
    show("tax", tax)
    show("final_price", final_price)

    # The named-step approach makes debugging and validation easier than
    # placing the entire calculation in one long expression.
    one_expression = (
        quantity * price
        - quantity * price * discount_rate
        + (quantity * price - quantity * price * discount_rate) * tax_rate
    )

    show("Equivalent single expression", one_expression)
    show("Values agree", math.isclose(final_price, one_expression))


# ---------------------------------------------------------------------------
# 21. Edge cases
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    section("21. Important edge cases")

    cases = [
        ("zero", 0),
        ("negative", -10),
        ("one", 1),
        ("large", 10**50),
    ]

    for name, value in cases:
        print(
            f"{name:<10} value={value}, "
            f"value % 2={value % 2}, "
            f"abs(value)={abs(value)}"
        )

    subsection("Division by zero")

    try:
        print(10 / 0)
    except ZeroDivisionError as error:
        print(f"Caught expected exception: {error}")

    subsection("Modulo by zero")

    try:
        print(10 % 0)
    except ZeroDivisionError as error:
        print(f"Caught expected exception: {error}")

    subsection("Very large integers")

    huge = 10**100
    show("Number of digits in 10**100", len(str(huge)))


# ---------------------------------------------------------------------------
# 22. Performance considerations
# ---------------------------------------------------------------------------

def demonstrate_performance_considerations() -> None:
    section("22. Performance considerations")

    # Basic arithmetic on primitive numeric values is normally inexpensive.
    # Algorithmic structure often matters more than tiny operator-level
    # optimizations.

    number = 10**6

    # Repeated modulo is O(1) per operation, so processing n numbers this way
    # is O(n).
    count_even = sum(1 for value in range(number) if value % 2 == 0)

    show("Even numbers below one million", count_even)

    print(
        "\nFor large programs, optimize the algorithm and data movement before "
        "attempting micro-optimizations of individual operators."
    )


# ---------------------------------------------------------------------------
# 23. Practice suite
# ---------------------------------------------------------------------------

def run_practice_suite() -> None:
    section("23. Practice suite")

    test_numbers = [2, 3, 10, 17, 100, 101, -4, 0]

    print("Even/odd:")
    for number in test_numbers:
        print(f"{number:>4}: {'even' if is_even(number) else 'odd'}")

    print("\nPositive/negative/zero:")
    for number in test_numbers:
        if number > 0:
            label = "positive"
        elif number < 0:
            label = "negative"
        else:
            label = "zero"
        print(f"{number:>4}: {label}")

    print("\nLargest values:")
    triples = [
        (1, 2, 3),
        (100, 20, 50),
        (-10, -3, -7),
        (5, 5, 5),
    ]

    for triple in triples:
        print(f"{triple} -> {largest_of_three(*triple)}")

    print("\nDivisibility:")
    for number in [12, 25, 36, 49, 100]:
        divisible_by_3 = number % 3 == 0
        divisible_by_5 = number % 5 == 0
        print(
            f"{number}: by 3={divisible_by_3}, "
            f"by 5={divisible_by_5}"
        )

    print("\nDigit calculations:")
    for number in [0, 7, 1234, 90807, -54321]:
        print(
            f"{number}: digits={count_digits(number)}, "
            f"sum={digit_sum(number)}, "
            f"reverse={reverse_integer(number)}"
        )


# ---------------------------------------------------------------------------
# 24. Assertions as lightweight tests
# ---------------------------------------------------------------------------

def run_assertions() -> None:
    section("24. Built-in verification")

    assert 2 + 3 == 5
    assert 10 - 4 == 6
    assert 6 * 7 == 42
    assert 20 / 4 == 5
    assert 20 // 6 == 3
    assert 20 % 6 == 2
    assert 2 ** 5 == 32

    assert is_even(10)
    assert not is_even(11)

    assert largest_of_two(5, 10) == 10
    assert largest_of_three(1, 9, 3) == 9

    assert digit_sum(12345) == 15
    assert reverse_integer(12345) == 54321
    assert reverse_integer(-123) == -321

    assert calculate(10, "+", 5) == 15
    assert calculate(10, "%", 3) == 1

    try:
        calculate(10, "/", 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("Division by zero should fail.")

    print("All demonstration assertions passed.")


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    print("OPERATORS AND EXPRESSIONS")
    print("A structured Python study and practice program")

    demonstrate_expressions()
    demonstrate_arithmetic()
    demonstrate_modulo()
    demonstrate_comparisons()
    demonstrate_logical_operators()
    demonstrate_assignment()
    demonstrate_increment_decrement()
    demonstrate_precedence()
    demonstrate_conditional_expressions()
    demonstrate_beginner_problems()
    demonstrate_calculator()
    demonstrate_floating_point()
    demonstrate_boolean_numerical_relationship()
    demonstrate_bitwise_operators()
    demonstrate_membership_and_identity()
    demonstrate_assignment_expression()
    demonstrate_operator_overloading()
    demonstrate_validation()
    demonstrate_mathematical_expressions()
    demonstrate_debugging_expressions()
    demonstrate_edge_cases()
    demonstrate_performance_considerations()
    run_practice_suite()
    run_assertions()

    section("End of operators and expressions study program")
    print(
        "The program demonstrated arithmetic, comparison, logical, "
        "assignment, modulo, precedence, expressions, practical problems, "
        "edge cases, and advanced operator behavior."
    )


if __name__ == "__main__":
    main()
