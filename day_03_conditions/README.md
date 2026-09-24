# Day 3 — Conditions

## Introduction

Conditions allow a program to make decisions.

A program normally receives data, evaluates one or more expressions, and then chooses what should happen next. This is the foundation of validation, classification, authentication, pricing, billing, access control, business rules, error handling, algorithms, and many other forms of software logic.

The central skill for this topic is:

> Convert a written decision process into precise program conditions.

For example, a written rule might say:

- If a student's score is 90 or above, assign grade A.
- Otherwise, if the score is 80 or above, assign grade B.
- Otherwise, if the score is 70 or above, assign grade C.
- Otherwise, assign a lower grade.

That decision process becomes an ordered set of conditional branches.

The implementations in this topic demonstrate the same fundamental reasoning using Python, JavaScript, and C++. Python provides concise examples and reusable functions, JavaScript demonstrates conditional logic in application-oriented code, and C++ develops the topic into a structured rule-based electricity billing case study.

---

## Fundamental concept: a Boolean decision

A condition ultimately evaluates to a Boolean result.

A Boolean has two possible values:

- `True` or `False` in Python
- `true` or `false` in JavaScript and C++

For example, the expression `age >= 18` asks whether the value of `age` is at least 18.

If `age` is 25, the expression is true.

If `age` is 15, the expression is false.

A conditional statement uses that result to decide whether a block of code should execute.

---

## `if`

The `if` statement executes its block only when its condition is true.

Python uses indentation to define the block.

JavaScript and C++ normally use braces to define the block.

The basic conceptual structure is:

`if condition -> execute block`

The Python implementation demonstrates this through temperature, age, balance, and other simple examples.

The JavaScript implementation demonstrates the same idea using functions.

The C++ implementation begins with simple age and score decisions before developing the larger case study.

---

## `else`

`else` provides the alternative path.

The structure is conceptually:

`if condition -> first path`

`else -> alternative path`

A typical example is classifying a number as even or odd.

If the number is divisible by two, the first branch executes. Otherwise, the second branch executes.

`else` does not have a condition of its own. It represents everything not handled by the preceding `if` condition.

---

## `elif` and `else if`

Python uses `elif`.

JavaScript and C++ use `else if`.

These structures are useful when there are several mutually exclusive ranges or categories.

The grade calculator demonstrates this pattern:

- 90–100 -> A
- 80–89.99 -> B
- 70–79.99 -> C
- 60–69.99 -> D
- below 60 -> F

The order is important.

A score of 95 satisfies both `score >= 90` and `score >= 80`, but the first matching branch must receive the decision.

Therefore, the highest threshold is checked first.

If the 80-point condition were placed before the 90-point condition, a score of 95 would incorrectly be classified as B.

This is one of the most common errors in conditional programming.

---

## Comparison operators

Conditions commonly use comparison operators.

| Meaning | Python | JavaScript | C++ |
|---|---|---|---|
| Equal | `==` | `===` | `==` |
| Not equal | `!=` | `!==` | `!=` |
| Less than | `<` | `<` | `<` |
| Less than or equal | `<=` | `<=` | `<=` |
| Greater than | `>` | `>` | `>` |
| Greater than or equal | `>=` | `>=` | `>=` |

JavaScript deserves special attention because it provides both loose equality and strict equality.

`10 == "10"` performs type conversion and evaluates as true.

`10 === "10"` evaluates as false because the values have different types.

For predictable application logic, strict equality is generally preferable when equality is intended.

Python and C++ do not have JavaScript's `===` operator.

---

## Boolean operators

Conditions frequently need to combine multiple rules.

### AND

The logical AND operator requires every required condition to be true.

Python:

`condition_a and condition_b`

JavaScript:

`condition_a && condition_b`

C++:

`condition_a && condition_b`

Example:

A customer may qualify only when:

- age is at least 21
- income is at least 30,000
- credit score is at least 700

All three requirements must be satisfied.

---

## OR

OR requires at least one condition to be true.

Python:

`condition_a or condition_b`

JavaScript and C++:

`condition_a || condition_b`

For example, a discount might apply when the customer is a student or a senior citizen.

---

## NOT

NOT reverses a Boolean value.

Python:

`not account_locked`

JavaScript and C++:

`!accountLocked`

If `account_locked` is false, `not account_locked` becomes true.

This is particularly useful when a rule is naturally expressed as an exception:

- if the account is not locked
- if the user is not authenticated
- if the input is not valid

---

## Compound conditions

A compound condition contains multiple Boolean expressions.

For example:

`age >= 21 and income >= 30000 and credit_score >= 700`

contains three comparisons connected by AND.

Compound conditions are important because real business rules rarely depend on only one variable.

Examples include:

- eligibility decisions
- access control
- discounts
- loan screening
- shipping prices
- billing
- validation
- permissions
- classification

When a condition becomes difficult to read, parentheses should be used to make the intended grouping explicit.

---

## Operator precedence

Logical operators have an evaluation order.

In Python, the common order relevant to these examples is:

1. comparisons
2. `not`
3. `and`
4. `or`

JavaScript and C++ have corresponding operator-precedence rules.

Even when the language has a well-defined precedence rule, complicated conditions should use parentheses.

For example:

`income >= 100000 and (credit_score >= 750 or verified)`

is easier to understand than a long ungrouped expression.

Parentheses communicate the business rule directly to another programmer.

---

## Nested conditions

A nested condition places one decision inside another.

For example:

- Is the person an adult?
  - If yes, does the person have a ticket?
    - If yes, allow entry.
    - Otherwise, reject entry.
- If no, reject entry.

Nested conditions can represent hierarchical decision processes.

They can also become difficult to maintain when there are too many levels.

The implementations therefore demonstrate both nested conditions and flatter compound conditions.

If several nested checks simply need to be true together, a compound condition may be clearer.

---

## Guard clauses

A guard clause handles an invalid or exceptional situation early.

For example:

1. Reject a negative payment amount.
2. Reject an inactive account.
3. Reject insufficient balance.
4. Process the payment.

This structure avoids deeply nested code.

The Python, JavaScript, and C++ implementations use guard-style validation in several functions.

Guard clauses are particularly useful for:

- input validation
- authentication
- authorization
- financial calculations
- API request processing
- data validation
- error handling

---

## Truthiness and falsiness

A Boolean condition does not always have to be explicitly written as a comparison.

Python has a concept of truthy and falsy values.

Common falsy Python values include:

- `False`
- `0`
- `0.0`
- `""`
- empty collections
- `None`

JavaScript has its own truthy/falsy rules.

Common falsy JavaScript values include:

- `false`
- `0`
- `""`
- `null`
- `undefined`
- `NaN`

An important JavaScript distinction is that empty arrays and empty objects are truthy.

Therefore, an empty array does not behave like a false Boolean value in a JavaScript condition.

Understanding truthiness is important because implicit Boolean conversion can otherwise create unexpected decisions.

---

## Equality and identity

Equality asks whether two values are equivalent.

Identity asks whether two references represent the same object.

Python uses `==` for equality and `is` for identity.

A common Python pattern is:

`value is None`

because `None` represents the absence of a value and identity is the appropriate test.

JavaScript uses strict equality such as `===`.

The distinction is important when working with objects, references, special values, and application state.

---

## Conditional expressions

Sometimes a decision is simple enough to be represented directly inside an expression.

Python provides a conditional expression such as:

`result = "even" if number % 2 == 0 else "odd"`

JavaScript provides the ternary operator:

`result = condition ? valueIfTrue : valueIfFalse`

C++ also supports the ternary conditional operator.

These forms are useful for short decisions.

They should not be used to compress complicated business rules into unreadable expressions.

---

## Validation

A condition is often used to validate data before the rest of the program uses it.

Examples include:

- age cannot be negative
- score must be between 0 and 100
- quantity must be positive
- price cannot be negative
- electricity consumption cannot be negative
- a triangle side must be positive

Validation is important because incorrect input can cause incorrect decisions.

A strong conditional implementation therefore considers both normal values and invalid values.

---

## Boundary values

Conditional problems frequently contain boundaries.

For a grade system, these values are especially important:

- 59.99
- 60
- 69.99
- 70
- 79.99
- 80
- 89.99
- 90
- 100

The implementations explicitly test boundary values.

Boundary testing is important because an expression such as `score > 90` is different from `score >= 90`.

A one-character difference can change the classification of an entire range of inputs.

---

## Grade calculator

The grade calculator validates the score and then evaluates ordered thresholds.

The Python implementation exposes `calculate_grade()`.

The JavaScript implementation exposes `calculateGrade()`.

The C++ implementation provides `calculateGrade()`.

All three implementations demonstrate:

- validation
- ordered branches
- boundary conditions
- explicit categories
- error handling

This makes the example useful for understanding how the same decision model maps to different programming languages.

---

## Leap-year calculation

A leap year is not simply every fourth year.

The Gregorian rule used in the implementations is:

1. If divisible by 400, it is a leap year.
2. Otherwise, if divisible by 100, it is not a leap year.
3. Otherwise, if divisible by 4, it is a leap year.
4. Otherwise, it is not a leap year.

The compact Boolean rule is:

`year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)`

Important boundary examples include:

- 1600 -> leap year
- 1700 -> not a leap year
- 1900 -> not a leap year
- 2000 -> leap year
- 2024 -> leap year
- 2025 -> not a leap year
- 2100 -> not a leap year

This demonstrates why nested or compound conditions sometimes need careful reasoning rather than a single simple comparison.

---

## Number classification

Number classification demonstrates several mutually exclusive decisions:

- zero
- positive integer
- positive non-integer
- negative integer
- negative non-integer

The implementations first distinguish zero from non-zero values and then distinguish positive from negative values.

This is an example of hierarchical decision-making.

---

## Triangle validity

Three positive numbers form a valid triangle only when:

- `a + b > c`
- `a + c > b`
- `b + c > a`

All three conditions must be true.

This is an example of a compound condition.

After validity has been established, the triangle can be classified as:

- equilateral
- isosceles
- scalene

The order is important.

The equality test for all three sides must be performed before checking whether any two sides are equal.

Otherwise, an equilateral triangle could incorrectly be classified as isosceles.

This is a useful example of how classification order affects correctness.

---

## Largest of multiple values

Finding the largest value demonstrates repeated conditional comparison.

The algorithm starts with the first value as the current largest.

Each later value is compared against the current largest.

If it is larger, the current largest is replaced.

For `n` values, this requires one pass through the input:

- time complexity: `O(n)`
- auxiliary space: `O(1)`

The algorithm also demonstrates why an empty input requires explicit handling.

There is no first element from which a current maximum can be initialized when the collection is empty.

---

## Simple billing system

The billing examples combine multiple conditions into a realistic calculation.

The basic model is:

1. Calculate subtotal.
2. Determine whether the subtotal qualifies for a discount.
3. Subtract the discount.
4. Calculate tax.
5. Calculate the final amount.

The condition is not simply a classification. It affects a numerical result.

This illustrates an important characteristic of real-world conditional logic: decisions often change downstream calculations.

---

## Age classification

The age classifier divides values into categories:

- child
- teenager
- adult
- senior

Boundary values such as 12, 13, 17, 18, 59, and 60 are tested.

The example illustrates the importance of specifying exact category boundaries before writing code.

A written rule such as "teenagers are 13 through 17" translates directly into:

`age >= 13 and age <= 17`

or, when earlier conditions already exclude lower ages, an ordered `elif` or `else if` chain.

---

## Electricity billing

The electricity-bill example is a slab-based decision system.

The example uses these rates:

| Consumption range | Rate |
|---|---:|
| First 100 units | ₹1.50/unit |
| Next 200 units | ₹2.50/unit |
| Next 200 units | ₹4.00/unit |
| Above 500 units | ₹6.00/unit |

A fixed charge of ₹50 is applied.

The implementation handles each range with conditions.

For example, consumption of 50 units uses only the first slab.

Consumption of 250 units uses:

- 100 units at ₹1.50
- 150 units at ₹2.50

Consumption above 500 units uses all preceding slabs plus the highest rate for the remaining units.

This is a practical example of piecewise business logic.

---

## C++ case study

The C++ implementation develops the electricity-billing problem into a small rule-based system.

The major components are:

- `Customer`
- `CustomerType`
- `ElectricityBill`
- `ElectricityBillingEngine`
- `CustomerEligibilityEngine`
- validation functions
- reporting functions
- test functions

The architecture separates the data being processed from the logic that makes decisions.

### Customer model

The `Customer` structure contains:

- customer ID
- name
- age
- customer type
- senior-citizen status

The model allows multiple conditions to use the same customer information.

### Customer type

The `CustomerType` enum contains:

- Regular
- Member
- Premium

Using an enum restricts the customer category to defined alternatives instead of relying on arbitrary strings.

### Billing engine

The billing engine contains separate functions for:

- energy charge
- surcharge
- discount
- complete bill calculation

This separation makes each rule easier to understand and test.

### Surcharge rule

The example applies a surcharge when:

- consumption is above 500 units
- the customer is not a senior citizen

This is a compound Boolean condition.

### Discount rule

The example applies a discount when:

- the customer is a senior citizen
- consumption does not exceed 300 units

The resulting discount is then subtracted before the final amount is calculated.

The rules are educational examples rather than a representation of an actual utility provider's tariff.

---

## Decision ordering

The order of conditions is a core part of conditional programming.

Consider these rules:

- premium customer -> 15% discount
- regular member above threshold -> 10% discount
- senior customer -> additional 5%

The implementation first determines the primary customer discount and then applies the age-based rule.

It then caps the total discount at 20%.

This demonstrates how a series of conditions can form a controlled decision pipeline rather than one isolated `if`.

---

## Nested conditions versus compound conditions

Nested conditions:

`if A:`

`    if B:`

are useful when the second decision only makes sense after the first decision has succeeded.

Compound conditions:

`if A and B:`

are often clearer when both requirements must simply be satisfied.

Neither approach is universally superior.

The appropriate structure depends on the relationship between the decisions.

A good implementation should make the underlying business rule obvious to the reader.

---

## Short-circuit evaluation

Logical operators can avoid evaluating unnecessary expressions.

For example:

`values and values[0] > 10`

in Python safely avoids accessing the first element when the collection is empty.

JavaScript and C++ provide similar short-circuit behavior with `&&` and `||`.

Short-circuiting is useful for:

- avoiding invalid operations
- reducing unnecessary work
- checking prerequisites
- handling optional values
- implementing safe compound conditions

It should not be confused with ordinary condition ordering. The order of expressions can affect both correctness and whether later expressions execute.

---

## Guard clauses versus nesting

Consider a payment function.

A deeply nested design might look conceptually like:

- if amount is valid
  - if account is active
    - if balance is sufficient
      - approve payment

A guard-clause design checks invalid cases first:

- invalid amount -> return
- inactive account -> return
- insufficient balance -> return
- otherwise approve

Guard clauses can make the successful path easier to read.

They are particularly useful when invalid conditions are independent and can immediately terminate the operation.

---

## Error handling

Conditional validation and error handling work together.

The implementations demonstrate errors such as:

- negative age
- invalid score
- invalid quantity
- negative price
- invalid electricity consumption
- empty input
- invalid triangle dimensions

Python uses exceptions such as `ValueError` and `TypeError`.

JavaScript uses `RangeError`, `TypeError`, and `Error`.

C++ uses standard exceptions such as `invalid_argument` and `logic_error`.

The important principle is that invalid data should be rejected explicitly rather than silently producing an incorrect result.

---

## Common mistakes

### Checking equality instead of a range

A condition such as:

`age == 18`

means exactly 18.

It does not mean 18 or older.

The appropriate expression for adulthood is usually:

`age >= 18`

when that is the actual business rule.

### Incorrect branch order

If a higher threshold is placed after a lower threshold, the higher category may never be reached.

For example:

`if score >= 80`

before:

`if score >= 90`

causes 90 and above to match the first condition.

### Incorrect use of OR

A requirement such as:

"age must be at least 18 and the user must have an ID"

requires AND.

Using OR would allow someone who satisfies only one requirement.

### Forgetting boundary values

A condition using `>` excludes the boundary.

A condition using `>=` includes it.

The difference must match the written rule.

### Excessive nesting

Many nested levels make decision logic difficult to read and test.

Compound conditions, guard clauses, helper functions, and structured rules can reduce unnecessary nesting.

### Mixing validation with calculation

If invalid input is allowed to enter the calculation stage, later logic may become difficult to reason about.

Validation should happen before calculations whenever practical.

---

## Edge cases

Important conditional programs explicitly consider unusual values.

Examples include:

- zero
- negative values
- empty collections
- maximum values
- minimum values
- exact thresholds
- just below a threshold
- just above a threshold
- invalid types
- missing values
- contradictory input
- extremely large values

The implementations test several of these cases.

For a threshold of 100, testing only 50 and 200 is not enough.

Values such as 99, 100, and 101 are much more useful for verifying the boundary logic.

---

## Testing conditional logic

Conditional code benefits strongly from systematic testing.

For each branch, identify at least one input that should reach it.

For a grade calculator, the meaningful categories are:

- A
- B
- C
- D
- F

Then test the boundaries.

The implementations include assertions and explicit test cases.

The goal is not merely to test normal values. It is to verify that each logical branch behaves correctly.

---

## Performance considerations

Most simple condition chains operate in constant time, `O(1)`, because they perform a fixed number of comparisons.

Examples include:

- leap-year calculation
- grade classification
- triangle classification
- age classification
- electricity slab calculation

Finding the largest value in a collection is different.

For `n` values, it requires one comparison pass and therefore has:

- time complexity: `O(n)`
- auxiliary space: `O(1)`

Conditional logic itself is usually inexpensive.

In large applications, the main performance concern is often what happens inside the condition rather than the `if` statement itself.

For example, a condition that performs a database query, network request, or expensive computation can be much more significant than a simple comparison.

---

## Security considerations

Conditions frequently control access to protected operations.

Examples include:

- authentication
- authorization
- account state
- transaction approval
- input validation
- role-based access
- feature availability

Security-sensitive conditions should not rely only on client-side validation.

For example, a web application's JavaScript may check whether a user appears authorized, but the server must independently enforce authorization.

Similarly, financial or access-control decisions should not assume that user-supplied Boolean values are trustworthy.

Conditions are part of a security boundary when they determine whether a protected operation is permitted.

---

## Floating-point considerations

The examples use simple monetary calculations for educational purposes.

Real financial systems require careful treatment of currency.

Binary floating-point numbers can represent some decimal values only approximately.

For production financial software, the representation strategy should be chosen deliberately, such as:

- integer minor units
- decimal arithmetic
- a validated monetary library
- database decimal types

Conditional logic does not remove numerical precision issues.

For example, comparing calculated floating-point values directly can sometimes produce surprising results.

---

## Production design considerations

Conditional logic becomes easier to maintain when:

- business rules are clearly defined
- boundaries are explicit
- validation happens early
- conditions have meaningful names
- complex rules are divided into functions
- repeated rules are centralized
- error cases are handled explicitly
- tests cover every branch
- threshold values are documented
- calculations are separated from presentation

A function such as `is_valid_triangle()` communicates more clearly than repeating the same three comparisons throughout an application.

A function such as `calculate_bill()` gives the decision process a defined interface.

---

## Python implementation

The Python implementation progresses from simple conditions to structured systems.

It demonstrates:

- basic `if`
- `if` and `else`
- `elif`
- comparison operators
- Boolean operators
- compound conditions
- nested conditions
- truthiness
- equality and identity
- conditional expressions
- validation
- reusable functions
- dataclasses
- enums
- guard clauses
- structured decision models
- assertions
- billing rules
- performance reasoning

Python's indentation makes block structure visually explicit.

The implementation also demonstrates how decision rules can be represented as reusable functions rather than being placed directly inside one large program.

---

## JavaScript implementation

The JavaScript implementation complements the Python version by emphasizing application-oriented syntax.

It demonstrates:

- `if`
- `else`
- `else if`
- strict equality
- logical operators
- truthy/falsy behavior
- ternary expressions
- `Number.isFinite`
- `Number.isInteger`
- exceptions
- classes
- object data
- short-circuit operators
- nullish coalescing
- structured billing
- testing

JavaScript's truthiness rules are particularly important because JavaScript frequently processes data from web forms, APIs, browser state, and JSON objects.

The use of strict equality is also deliberately demonstrated because JavaScript's coercive equality behavior can create unexpected decisions when used without care.

---

## C++ implementation

The C++ implementation presents a more structured technical case study.

The scenario is a rule-based electricity billing system.

The program models:

- customers
- customer categories
- electricity consumption
- billing slabs
- fixed charges
- surcharges
- discounts
- eligibility decisions
- input validation
- error handling
- reporting

The program uses:

- `struct`
- `enum class`
- classes
- private helper functions
- public calculation interfaces
- vectors
- exceptions
- formatted output
- assertions through explicit test checks

The architecture separates individual rules so that the main billing operation does not become one large conditional block.

---

## Python, JavaScript, and C++ comparison

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Basic condition | `if` | `if` | `if` |
| Alternative | `else` | `else` | `else` |
| Multiple branch | `elif` | `else if` | `else if` |
| AND | `and` | `&&` | `&&` |
| OR | `or` | `||` | `||` |
| NOT | `not` | `!` | `!` |
| Conditional expression | `x if c else y` | `c ? x : y` | `c ? x : y` |
| Equality | `==` | `===` recommended for strict equality | `==` |
| Main block syntax | indentation | braces | braces |
| Truthiness | built into Boolean contexts | extensive truthy/falsy rules | expressions convert to Boolean context |
| Typical strength in this topic | concise decision logic | application and web logic | structured systems and explicit types |

The underlying decision-making principle is the same across all three languages.

The syntax changes, but the reasoning remains:

1. Identify the input.
2. Define the rule.
3. Identify possible outcomes.
4. Establish boundaries.
5. Order overlapping conditions correctly.
6. Handle invalid input.
7. Test each branch.

---

## Converting written rules into code

A reliable process for converting a decision process into code is:

### Identify the inputs

Determine what information the decision needs.

Example:

- age
- income
- score
- quantity
- units consumed

### Identify the outputs

Determine what the program must decide.

Example:

- eligible
- not eligible
- grade
- discount
- billing amount

### Write the rules in plain language

For example:

- If units are at most 100, use the first rate.
- Otherwise, if units are at most 300, use the second rate.
- Otherwise, if units are at most 500, use the third rate.
- Otherwise, use the fourth rate.

### Identify boundaries

Ask:

- What happens at exactly 100?
- What happens at 101?
- What happens at exactly 300?
- What happens at 301?

### Identify invalid input

Ask:

- Can the value be negative?
- Can it be empty?
- Can it be outside a valid range?
- Can it have an invalid type?

### Translate the rules

Only after the decision process is clear should it be converted into code.

### Test every branch

Normal examples and boundary examples should both be tested.

---

## Decision tables

A decision table can help before writing a complicated conditional structure.

For example, a simplified billing decision might use:

| Condition | Result |
|---|---|
| Units <= 100 | First slab |
| Units > 100 and <= 300 | Second slab |
| Units > 300 and <= 500 | Third slab |
| Units > 500 | Fourth slab |

A more complex system might include customer status:

| Premium | Senior | High usage | Result |
|---|---|---|---|
| Yes | No | No | Premium discount |
| Yes | Yes | No | Premium plus senior rule |
| No | Yes | No | Senior rule |
| No | No | Yes | High-usage rule |
| No | No | No | Standard rule |

Writing such a table can reveal missing combinations before implementation.

---

## Practical applications

Conditional logic appears throughout software systems.

### Authentication

- Is the username valid?
- Is the password correct?
- Is the account active?
- Is multi-factor authentication required?

### Authorization

- Does the user have the required role?
- Is the requested resource accessible?
- Is the account permitted to perform the operation?

### E-commerce

- Does the order exceed the discount threshold?
- Is the customer a member?
- Is the product eligible?
- Does free shipping apply?

### Finance

- Is the transaction amount valid?
- Is the balance sufficient?
- Does the account satisfy the required conditions?

### Healthcare software

- Does an input fall inside an allowed range?
- Is a required field present?
- Does a rule require additional review?

### Networking

- Is a connection established?
- Is the packet valid?
- Is the destination reachable?
- Should a request be accepted or rejected?

### Algorithms

Conditional statements are fundamental to:

- searching
- sorting
- classification
- graph algorithms
- dynamic programming
- simulation
- validation
- optimization

---

## Important distinctions

### `if` versus `elif` / `else if`

`if` begins a decision.

`elif` or `else if` adds another mutually exclusive branch.

### `else` versus another condition

`else` catches the remaining cases.

It does not test a new expression.

### Nested condition versus compound condition

Nested conditions represent decisions inside other decisions.

Compound conditions combine multiple requirements into one Boolean expression.

### Validation versus classification

Validation asks whether input is acceptable.

Classification assigns an accepted value to a category.

A robust program often performs validation before classification.

### Condition versus calculation

A condition decides which path should execute.

A calculation produces a numerical or other computed result.

Real applications commonly combine both.

---

## Testing checklist

For a new conditional problem, test:

- normal valid input
- minimum valid input
- maximum valid input
- exactly-on-threshold input
- just below threshold
- just above threshold
- zero
- negative values where relevant
- empty input where relevant
- invalid type where relevant
- every branch
- conflicting conditions
- overlapping ranges

A condition that has not been tested at its boundaries has not been thoroughly validated.

---

## Code quality principles

Good conditional code should be:

- explicit
- readable
- deterministic
- testable
- easy to modify
- based on clearly defined rules
- resistant to invalid input
- structured around meaningful decisions

The goal is not to minimize the number of lines.

The goal is to make the decision process correctly represent the requirements.

A short but ambiguous condition can be worse than several clearly separated conditions.

---

## Core practice problems implemented

The implementations cover the requested practice areas:

- Grade calculator
- Leap-year check
- Number classification
- Triangle validity
- Triangle classification
- Simple billing system
- Age/category classification
- Largest of multiple values
- Electricity-bill style slab calculation
- Shipping-cost decision system
- Multi-criteria eligibility
- Structured customer billing

These examples increase in complexity because the underlying skill is not memorizing `if` syntax. The objective is learning how to translate rules into reliable decision structures.

---

## Central programming skill

The essential pattern for this topic is:

`Input -> Boolean expression -> Decision -> Action or result`

A more complete production-oriented pattern is:

`Input -> Validation -> Condition evaluation -> Branch selection -> Calculation/action -> Result -> Test`

Conditions form the bridge between raw data and program behavior.

A programmer who can accurately translate written rules into Boolean expressions and correctly order the resulting branches can implement a large class of practical software decisions.
