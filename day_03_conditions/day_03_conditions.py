"""
Day 3 — Conditions
===================

A comprehensive beginner-to-advanced study file for decision-making in Python.

Topics covered:
- if
- else
- elif
- nested conditions
- multiple conditions
- Boolean expressions
- compound conditions
- comparison and logical operators
- truthiness and falsiness
- conditional expressions
- validation
- decision tables
- progressively complex practical problems
- grade calculation
- leap-year checking
- number classification
- triangle validity and classification
- billing
- age/category classification
- largest of multiple values
- electricity billing
- edge cases
- common mistakes
- testing
- debugging
- performance
- production-oriented decision design

The central objective is to convert a written decision process into
correct, readable, testable code.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


# ============================================================================
# 1. FUNDAMENTALS: WHAT IS A CONDITION?
# ============================================================================

def basic_if_examples() -> None:
    print("\n=== 1. Basic if Statements ===")

    temperature = 32

    # The expression "temperature > 30" is evaluated as True or False.
    if temperature > 30:
        print("It is a hot day.")

    age = 20

    if age >= 18:
        print("The person is an adult.")

    # If the condition is False, the body is skipped.
    balance = 100

    if balance >= 500:
        print("Premium threshold reached.")

    print("Program continues regardless of the previous condition.")


# ============================================================================
# 2. if / else
# ============================================================================

def if_else_examples() -> None:
    print("\n=== 2. if / else ===")

    number = 17

    if number % 2 == 0:
        print("The number is even.")
    else:
        print("The number is odd.")

    age = 16

    if age >= 18:
        print("Eligible for the adult category.")
    else:
        print("Not eligible for the adult category.")


# ============================================================================
# 3. if / elif / else
# ============================================================================

def elif_examples() -> None:
    print("\n=== 3. if / elif / else ===")

    score = 87

    # Conditions are evaluated from top to bottom.
    # Once one condition is True, the remaining branches are skipped.
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    print(f"Score: {score}, Grade: {grade}")


# ============================================================================
# 4. COMPARISON OPERATORS
# ============================================================================

def comparison_operator_examples() -> None:
    print("\n=== 4. Comparison Operators ===")

    a = 10
    b = 20

    print("a == b:", a == b)
    print("a != b:", a != b)
    print("a < b:", a < b)
    print("a <= b:", a <= b)
    print("a > b:", a > b)
    print("a >= b:", a >= b)

    # Comparisons produce Boolean values.
    result = a < b
    print("The type of a comparison result:", type(result).__name__)


# ============================================================================
# 5. BOOLEAN OPERATORS
# ============================================================================

def boolean_operator_examples() -> None:
    print("\n=== 5. Boolean Operators ===")

    age = 25
    has_id = True
    is_student = False

    # and: every condition must be True.
    can_enter = age >= 18 and has_id
    print("Can enter:", can_enter)

    # or: at least one condition must be True.
    receives_discount = is_student or age >= 60
    print("Receives age/student discount:", receives_discount)

    # not reverses a Boolean value.
    account_locked = False
    print("Account available:", not account_locked)


# ============================================================================
# 6. COMPOUND CONDITIONS
# ============================================================================

def compound_condition_examples() -> None:
    print("\n=== 6. Compound Conditions ===")

    age = 25
    income = 80000
    credit_score = 760

    # A loan applicant must satisfy all three requirements.
    eligible = (
        age >= 21
        and income >= 30000
        and credit_score >= 700
    )

    print("Loan eligibility:", eligible)

    # Parentheses make complex expressions easier to understand.
    priority_customer = (
        (income >= 100000 and credit_score >= 750)
        or credit_score >= 800
    )

    print("Priority customer:", priority_customer)


# ============================================================================
# 7. OPERATOR PRECEDENCE
# ============================================================================

def precedence_examples() -> None:
    print("\n=== 7. Boolean Precedence ===")

    # Python evaluates comparisons before logical operators.
    # "not" has higher logical precedence than "and".
    # "and" has higher precedence than "or".
    result_without_parentheses = True or False and False

    # This is equivalent to:
    result_with_parentheses = True or (False and False)

    print(result_without_parentheses)
    print(result_with_parentheses)

    # Parentheses are recommended when a condition is complicated.
    age = 19
    citizen = True
    has_permission = False

    allowed = age >= 18 and (citizen or has_permission)
    print("Allowed:", allowed)


# ============================================================================
# 8. NESTED CONDITIONS
# ============================================================================

def nested_condition_examples() -> None:
    print("\n=== 8. Nested Conditions ===")

    age = 24
    has_ticket = True

    if age >= 18:
        if has_ticket:
            print("Entry approved.")
        else:
            print("Entry denied: ticket required.")
    else:
        print("Entry denied: minimum age requirement not met.")

    # A nested structure represents a decision inside another decision.
    username = "admin"
    password_correct = True
    account_active = True

    if username == "admin":
        if password_correct:
            if account_active:
                print("Login successful.")
            else:
                print("Account is inactive.")
        else:
            print("Incorrect password.")
    else:
        print("Unknown user.")


# ============================================================================
# 9. REWRITING NESTED CONDITIONS
# ============================================================================

def flatten_nested_conditions() -> None:
    print("\n=== 9. Flattening Nested Conditions ===")

    age = 25
    has_ticket = True

    # When the business rule is simply "both must be true",
    # one compound condition is clearer.
    if age >= 18 and has_ticket:
        print("Entry approved.")

    # This is logically equivalent to the nested version above,
    # but the compound form can be easier to maintain.


# ============================================================================
# 10. TRUTHINESS AND FALSINESS
# ============================================================================

def truthiness_examples() -> None:
    print("\n=== 10. Truthiness and Falsiness ===")

    values = [
        True,
        False,
        0,
        1,
        "",
        "Python",
        [],
        [1, 2],
        {},
        {"name": "Atul"},
        None,
    ]

    for value in values:
        if value:
            print(repr(value), "is truthy")
        else:
            print(repr(value), "is falsy")

    # This is useful for validating optional input.
    username = "atul"
    if username:
        print("Username supplied.")
    else:
        print("Username missing.")


# ============================================================================
# 11. IDENTITY VS EQUALITY
# ============================================================================

def equality_and_identity() -> None:
    print("\n=== 11. Equality vs Identity ===")

    first_name = "Atul"
    second_name = "Atul"

    # == asks whether two values are equal.
    print("Values equal:", first_name == second_name)

    # "is" asks whether two references point to the same object.
    # It should not normally be used to compare ordinary values.
    missing_value = None

    if missing_value is None:
        print("The value is None.")


# ============================================================================
# 12. CONDITIONAL EXPRESSIONS
# ============================================================================

def conditional_expression_examples() -> None:
    print("\n=== 12. Conditional Expressions ===")

    number = 42

    # Compact form:
    classification = "even" if number % 2 == 0 else "odd"
    print(classification)

    age = 20
    category = "adult" if age >= 18 else "minor"
    print(category)


# ============================================================================
# 13. INPUT VALIDATION
# ============================================================================

def validate_age(age: int) -> str:
    """
    Validate an age before using it in a decision process.
    """

    if age < 0:
        raise ValueError("Age cannot be negative.")

    if age > 150:
        raise ValueError("Age is outside the supported range.")

    if age < 13:
        return "child"
    elif age < 18:
        return "teenager"
    elif age < 60:
        return "adult"
    else:
        return "senior"


def validation_examples() -> None:
    print("\n=== 13. Validation ===")

    test_ages = [5, 16, 30, 70, -1, 200]

    for age in test_ages:
        try:
            print(age, "->", validate_age(age))
        except ValueError as error:
            print(age, "-> validation error:", error)


# ============================================================================
# 14. GRADE CALCULATOR
# ============================================================================

def calculate_grade(score: float) -> str:
    """
    Convert a score into a grade.

    Valid range: 0 through 100.
    """

    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def grade_calculator_demo() -> None:
    print("\n=== 14. Grade Calculator ===")

    scores = [100, 91, 90, 89.9, 80, 70, 60, 59.99, 0]

    for score in scores:
        print(f"{score:6.2f} -> {calculate_grade(score)}")


# ============================================================================
# 15. LEAP YEAR
# ============================================================================

def is_leap_year(year: int) -> bool:
    """
    Gregorian leap-year rule:

    1. Divisible by 400 -> leap year.
    2. Divisible by 100 -> not a leap year.
    3. Divisible by 4 -> leap year.
    4. Otherwise -> not a leap year.
    """

    if year <= 0:
        raise ValueError("Year must be positive.")

    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def leap_year_demo() -> None:
    print("\n=== 15. Leap-Year Check ===")

    for year in [1600, 1700, 1900, 2000, 2024, 2025, 2100]:
        print(year, "->", is_leap_year(year))


# ============================================================================
# 16. NUMBER CLASSIFICATION
# ============================================================================

def classify_number(number: float) -> str:
    if number == 0:
        return "zero"
    elif number > 0:
        if number.is_integer():
            return "positive integer"
        return "positive number"
    else:
        if number.is_integer():
            return "negative integer"
        return "negative number"


def number_classification_demo() -> None:
    print("\n=== 16. Number Classification ===")

    for number in [-10.0, -2.5, 0.0, 3.0, 4.75]:
        print(number, "->", classify_number(number))


# ============================================================================
# 17. TRIANGLE VALIDITY
# ============================================================================

def is_valid_triangle(a: float, b: float, c: float) -> bool:
    """
    A triangle requires:
    - all sides > 0
    - a + b > c
    - a + c > b
    - b + c > a
    """

    if a <= 0 or b <= 0 or c <= 0:
        return False

    return a + b > c and a + c > b and b + c > a


def classify_triangle(a: float, b: float, c: float) -> str:
    if not is_valid_triangle(a, b, c):
        return "invalid"

    if a == b == c:
        return "equilateral"

    if a == b or b == c or a == c:
        return "isosceles"

    return "scalene"


def triangle_demo() -> None:
    print("\n=== 17. Triangle Classification ===")

    triangles = [
        (3, 3, 3),
        (3, 3, 4),
        (3, 4, 5),
        (1, 2, 3),
        (-1, 2, 2),
    ]

    for sides in triangles:
        print(sides, "->", classify_triangle(*sides))


# ============================================================================
# 18. LARGEST OF MULTIPLE VALUES
# ============================================================================

def largest_of_three(a: float, b: float, c: float) -> float:
    """
    Manual conditional implementation.

    This demonstrates decision-making without using max().
    """

    largest = a

    if b > largest:
        largest = b

    if c > largest:
        largest = c

    return largest


def largest_of_values(values: Iterable[float]) -> float:
    values = list(values)

    if not values:
        raise ValueError("At least one value is required.")

    largest = values[0]

    for value in values[1:]:
        if value > largest:
            largest = value

    return largest


def largest_demo() -> None:
    print("\n=== 18. Largest Value ===")

    print(largest_of_three(10, 25, 7))
    print(largest_of_values([-100, -5, -20, -1]))
    print(largest_of_values([4, 4, 4]))


# ============================================================================
# 19. SIMPLE BILLING SYSTEM
# ============================================================================

@dataclass
class Bill:
    subtotal: float
    discount: float
    tax: float
    total: float


def calculate_bill(
    unit_price: float,
    quantity: int,
    discount_threshold: float = 5000.0,
    discount_rate: float = 0.10,
    tax_rate: float = 0.18,
) -> Bill:
    if unit_price < 0:
        raise ValueError("Unit price cannot be negative.")

    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    subtotal = unit_price * quantity

    if subtotal >= discount_threshold:
        discount = subtotal * discount_rate
    else:
        discount = 0.0

    taxable_amount = subtotal - discount
    tax = taxable_amount * tax_rate
    total = taxable_amount + tax

    return Bill(
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
    )


def billing_demo() -> None:
    print("\n=== 19. Simple Billing System ===")

    for price, quantity in [(100, 3), (1000, 6), (5000, 1)]:
        bill = calculate_bill(price, quantity)
        print(
            f"Subtotal={bill.subtotal:.2f}, "
            f"Discount={bill.discount:.2f}, "
            f"Tax={bill.tax:.2f}, "
            f"Total={bill.total:.2f}"
        )


# ============================================================================
# 20. AGE AND CATEGORY CLASSIFICATION
# ============================================================================

def classify_age(age: int) -> str:
    if not isinstance(age, int):
        raise TypeError("Age must be an integer.")

    if age < 0:
        raise ValueError("Age cannot be negative.")

    if age <= 12:
        return "child"
    elif age <= 17:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"


def age_category_demo() -> None:
    print("\n=== 20. Age Category Classification ===")

    for age in [0, 12, 13, 17, 18, 59, 60, 100]:
        print(age, "->", classify_age(age))


# ============================================================================
# 21. ELECTRICITY BILL
# ============================================================================

def electricity_bill(units: float) -> float:
    """
    Example slab-based electricity calculation.

    Slabs:
    - first 100 units: 1.50/unit
    - next 200 units: 2.50/unit
    - next 200 units: 4.00/unit
    - remaining units: 6.00/unit

    A fixed charge of 50 is applied.
    """

    if units < 0:
        raise ValueError("Units cannot be negative.")

    fixed_charge = 50.0

    if units <= 100:
        energy_charge = units * 1.50
    elif units <= 300:
        energy_charge = 100 * 1.50 + (units - 100) * 2.50
    elif units <= 500:
        energy_charge = (
            100 * 1.50
            + 200 * 2.50
            + (units - 300) * 4.00
        )
    else:
        energy_charge = (
            100 * 1.50
            + 200 * 2.50
            + 200 * 4.00
            + (units - 500) * 6.00
        )

    return fixed_charge + energy_charge


def electricity_demo() -> None:
    print("\n=== 21. Electricity Bill ===")

    for units in [0, 50, 100, 101, 300, 301, 500, 501, 1000]:
        print(f"{units:4.0f} units -> ₹{electricity_bill(units):.2f}")


# ============================================================================
# 22. MULTI-CRITERIA LOAN DECISION
# ============================================================================

def loan_decision(
    age: int,
    monthly_income: float,
    credit_score: int,
    existing_debt: float,
) -> str:
    """
    A simplified educational loan decision.

    This is a programming example, not a real lending model.
    """

    if age < 18:
        return "rejected: applicant must be an adult"

    if monthly_income <= 0:
        return "rejected: income must be positive"

    if credit_score < 300 or credit_score > 900:
        return "rejected: invalid credit score"

    if existing_debt < 0:
        return "rejected: debt cannot be negative"

    debt_to_income = existing_debt / (monthly_income * 12)

    if credit_score >= 750 and monthly_income >= 50000 and debt_to_income < 0.40:
        return "standard approval"

    if credit_score >= 650 and monthly_income >= 30000 and debt_to_income < 0.50:
        return "manual review"

    return "rejected"


def loan_demo() -> None:
    print("\n=== 22. Multi-Criteria Decision ===")

    applicants = [
        (30, 80000, 780, 100000),
        (25, 40000, 680, 150000),
        (17, 50000, 800, 10000),
        (40, 20000, 600, 50000),
    ]

    for applicant in applicants:
        print(applicant, "->", loan_decision(*applicant))


# ============================================================================
# 23. DECISION TABLE: SHIPPING
# ============================================================================

def shipping_cost(weight_kg: float, express: bool, international: bool) -> float:
    if weight_kg <= 0:
        raise ValueError("Weight must be positive.")

    if international:
        base = 1500.0
    else:
        base = 100.0

    if weight_kg <= 1:
        weight_charge = 0
    elif weight_kg <= 5:
        weight_charge = (weight_kg - 1) * 50
    else:
        weight_charge = 4 * 50 + (weight_kg - 5) * 75

    express_charge = 500 if express else 0

    return base + weight_charge + express_charge


def shipping_demo() -> None:
    print("\n=== 23. Shipping Decision ===")

    scenarios = [
        (0.5, False, False),
        (3, False, False),
        (8, True, False),
        (2, True, True),
    ]

    for scenario in scenarios:
        print(scenario, "-> ₹", shipping_cost(*scenario))


# ============================================================================
# 24. EDGE CASES
# ============================================================================

def edge_case_examples() -> None:
    print("\n=== 24. Edge Cases ===")

    # Boundary values often reveal incorrect conditions.
    boundaries = [59, 60, 89, 90, 99, 100]

    for score in boundaries:
        print(score, "->", calculate_grade(score))

    # Empty collections require explicit handling.
    try:
        largest_of_values([])
    except ValueError as error:
        print("Empty input:", error)

    # Invalid triangle:
    print("Triangle (1, 2, 3):", is_valid_triangle(1, 2, 3))

    # Zero electricity usage still has the fixed charge.
    print("Zero units bill:", electricity_bill(0))


# ============================================================================
# 25. COMMON LOGICAL ERRORS
# ============================================================================

def common_mistake_examples() -> None:
    print("\n=== 25. Common Logical Mistakes ===")

    age = 20

    # Correct:
    if age >= 18:
        print("Correct adult check.")

    # A common mistake is using:
    # if age == 18:
    # This means "exactly 18", not "18 or older".

    score = 85

    # Correct ordering:
    if score >= 90:
        print("A")
    elif score >= 80:
        print("B")

    # If the 80 check appeared first, a score of 95 would
    # incorrectly receive B.


# ============================================================================
# 26. TESTING CONDITIONAL LOGIC
# ============================================================================

def run_condition_tests() -> None:
    print("\n=== 26. Tests ===")

    assert calculate_grade(100) == "A"
    assert calculate_grade(90) == "A"
    assert calculate_grade(89.99) == "B"
    assert calculate_grade(80) == "B"
    assert calculate_grade(79.99) == "C"
    assert calculate_grade(0) == "F"

    assert is_leap_year(2000) is True
    assert is_leap_year(1900) is False
    assert is_leap_year(2024) is True
    assert is_leap_year(2025) is False

    assert is_valid_triangle(3, 4, 5) is True
    assert is_valid_triangle(1, 2, 3) is False
    assert classify_triangle(3, 3, 3) == "equilateral"
    assert classify_triangle(3, 3, 4) == "isosceles"
    assert classify_triangle(3, 4, 5) == "scalene"

    assert classify_age(12) == "child"
    assert classify_age(13) == "teenager"
    assert classify_age(18) == "adult"
    assert classify_age(60) == "senior"

    print("All assertions passed.")


# ============================================================================
# 27. DECISION PROCESS AS A REUSABLE FUNCTION
# ============================================================================

class TrafficLight(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


def driving_instruction(light: TrafficLight) -> str:
    """
    Demonstrates enum-based branching.

    Enumerations reduce accidental use of unrelated strings.
    """

    if light is TrafficLight.RED:
        return "Stop"
    elif light is TrafficLight.YELLOW:
        return "Prepare to stop"
    elif light is TrafficLight.GREEN:
        return "Proceed"
    else:
        raise ValueError("Unknown traffic light")


def enum_demo() -> None:
    print("\n=== 27. Enum-Based Conditions ===")

    for light in TrafficLight:
        print(light.value, "->", driving_instruction(light))


# ============================================================================
# 28. ADVANCED: GUARD CLAUSES
# ============================================================================

def process_payment(amount: float, account_active: bool, balance: float) -> str:
    """
    Guard clauses handle invalid cases early.

    This avoids excessive nesting and makes the main path clearer.
    """

    if amount <= 0:
        return "invalid amount"

    if not account_active:
        return "account inactive"

    if balance < amount:
        return "insufficient funds"

    return "payment approved"


def guard_clause_demo() -> None:
    print("\n=== 28. Guard Clauses ===")

    cases = [
        (-10, True, 100),
        (50, False, 100),
        (150, True, 100),
        (50, True, 100),
    ]

    for case in cases:
        print(case, "->", process_payment(*case))


# ============================================================================
# 29. ADVANCED: BOOLEAN PREDICATE FUNCTIONS
# ============================================================================

def is_adult(age: int) -> bool:
    return age >= 18


def is_valid_score(score: float) -> bool:
    return 0 <= score <= 100


def is_eligible_for_discount(age: int, member: bool) -> bool:
    return member or age >= 60


def predicate_demo() -> None:
    print("\n=== 29. Boolean Predicate Functions ===")

    print("Adult:", is_adult(21))
    print("Valid score:", is_valid_score(85))
    print("Discount:", is_eligible_for_discount(25, True))


# ============================================================================
# 30. ADVANCED: SHORT-CIRCUIT EVALUATION
# ============================================================================

def short_circuit_demo() -> None:
    print("\n=== 30. Short-Circuit Evaluation ===")

    values = []

    # The second condition is never evaluated because the first is False.
    if values and values[0] > 10:
        print("First value is greater than 10.")
    else:
        print("Safe evaluation of an empty list.")

    username = ""
    display_name = username or "Guest"
    print("Display name:", display_name)


# ============================================================================
# 31. ADVANCED: STRUCTURED DECISION MODEL
# ============================================================================

@dataclass(frozen=True)
class Applicant:
    age: int
    income: float
    credit_score: int
    verified_identity: bool


def assess_applicant(applicant: Applicant) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if applicant.age < 18:
        reasons.append("underage")

    if applicant.income < 30000:
        reasons.append("income below threshold")

    if applicant.credit_score < 650:
        reasons.append("credit score below threshold")

    if not applicant.verified_identity:
        reasons.append("identity not verified")

    if reasons:
        return "not eligible", reasons

    if applicant.credit_score >= 750 and applicant.income >= 60000:
        return "priority review", ["meets enhanced criteria"]

    return "eligible", ["meets baseline criteria"]


def structured_decision_demo() -> None:
    print("\n=== 31. Structured Decision Model ===")

    applicants = [
        Applicant(30, 80000, 780, True),
        Applicant(25, 25000, 700, True),
        Applicant(17, 90000, 800, True),
        Applicant(40, 70000, 680, False),
    ]

    for applicant in applicants:
        print(applicant, "->", assess_applicant(applicant))


# ============================================================================
# 32. PERFORMANCE CONSIDERATIONS
# ============================================================================

def linear_largest(values: list[int]) -> int:
    if not values:
        raise ValueError("values cannot be empty")

    largest = values[0]

    for value in values[1:]:
        if value > largest:
            largest = value

    return largest


def performance_demo() -> None:
    print("\n=== 32. Performance Considerations ===")

    values = list(range(1, 10001))
    result = linear_largest(values)

    # Finding the largest value requires one pass: O(n) time and O(1)
    # additional space when the input list already exists.
    print("Largest:", result)
    print("Algorithmic complexity: O(n) time, O(1) auxiliary space.")


# ============================================================================
# 33. CAPSTONE: COMPLETE CUSTOMER BILLING DECISION
# ============================================================================

@dataclass
class Customer:
    age: int
    member: bool
    premium_member: bool


@dataclass
class Product:
    name: str
    price: float
    quantity: int


@dataclass
class Invoice:
    subtotal: float
    discount: float
    tax: float
    total: float
    message: str


def create_invoice(
    customer: Customer,
    products: list[Product],
    tax_rate: float = 0.18,
) -> Invoice:
    """
    A complete decision-heavy billing example.

    Rules:
    - Product prices must be non-negative.
    - Quantities must be positive.
    - Premium members receive 15% discount.
    - Regular members receive 10% discount when subtotal >= 5000.
    - Customers aged 60+ receive 5% additional discount.
    - Discounts are capped at 20%.
    - Tax is calculated after discount.
    """

    if not products:
        raise ValueError("At least one product is required.")

    subtotal = 0.0

    for product in products:
        if product.price < 0:
            raise ValueError(f"Negative price for {product.name}.")
        if product.quantity <= 0:
            raise ValueError(f"Invalid quantity for {product.name}.")

        subtotal += product.price * product.quantity

    discount_rate = 0.0

    if customer.premium_member:
        discount_rate = 0.15
    elif customer.member and subtotal >= 5000:
        discount_rate = 0.10

    if customer.age >= 60:
        discount_rate += 0.05

    discount_rate = min(discount_rate, 0.20)

    discount = subtotal * discount_rate
    taxable_amount = subtotal - discount
    tax = taxable_amount * tax_rate
    total = taxable_amount + tax

    if discount_rate >= 0.20:
        message = "Maximum discount applied."
    elif discount_rate > 0:
        message = "Member or age-based discount applied."
    else:
        message = "No discount applied."

    return Invoice(
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
        message=message,
    )


def capstone_demo() -> None:
    print("\n=== 33. Capstone Billing System ===")

    customer = Customer(
        age=62,
        member=True,
        premium_member=True,
    )

    products = [
        Product("Laptop", 60000, 1),
        Product("Keyboard", 2500, 1),
        Product("Mouse", 1500, 2),
    ]

    invoice = create_invoice(customer, products)

    print(f"Subtotal: ₹{invoice.subtotal:,.2f}")
    print(f"Discount: ₹{invoice.discount:,.2f}")
    print(f"Tax:      ₹{invoice.tax:,.2f}")
    print(f"Total:    ₹{invoice.total:,.2f}")
    print("Decision:", invoice.message)


# ============================================================================
# 34. MAIN STUDY RUNNER
# ============================================================================

def main() -> None:
    print("=" * 72)
    print("DAY 3 — CONDITIONS")
    print("From beginner decision-making to structured conditional systems")
    print("=" * 72)

    basic_if_examples()
    if_else_examples()
    elif_examples()
    comparison_operator_examples()
    boolean_operator_examples()
    compound_condition_examples()
    precedence_examples()
    nested_condition_examples()
    flatten_nested_conditions()
    truthiness_examples()
    equality_and_identity()
    conditional_expression_examples()
    validation_examples()
    grade_calculator_demo()
    leap_year_demo()
    number_classification_demo()
    triangle_demo()
    largest_demo()
    billing_demo()
    age_category_demo()
    electricity_demo()
    loan_demo()
    shipping_demo()
    edge_case_examples()
    common_mistake_examples()
    run_condition_tests()
    enum_demo()
    guard_clause_demo()
    predicate_demo()
    short_circuit_demo()
    structured_decision_demo()
    performance_demo()
    capstone_demo()

    print("\n" + "=" * 72)
    print("CONDITION STUDY COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
