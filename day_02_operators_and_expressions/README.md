# Operators and expressions

## Topic scope

Operators and expressions are fundamental to programming because they allow programs to calculate values, compare data, make decisions, modify state, validate conditions, and express algorithms.

This project studies the following concepts:

- Arithmetic operators
- Comparison operators
- Logical operators
- Assignment operators
- Increment and decrement
- Modulo and remainder calculations
- Operator precedence
- Expressions
- Conditional expressions
- Boolean expressions
- Short-circuit evaluation
- Type conversion and coercion
- Bitwise operators
- Membership and identity concepts
- Floating-point arithmetic
- Integer division
- Validation and error handling
- Operator overloading
- Practical numerical problems
- Calculator implementation
- Digit calculations
- Real-world billing calculations
- Performance and complexity considerations

The three implementations deliberately use the strengths and rules of Python, JavaScript, and C++ rather than forcing identical syntax across the languages.

---

## Fundamental concept: expression

An expression is a piece of code that is evaluated to produce a value.

Examples include:

- `10 + 5`
- `price * quantity`
- `age >= 18`
- `is_verified and has_permission`
- `number % 2`
- `2 ** 5`
- `Math.max(a, b)`
- `a + b` in a C++ class that overloads `operator+`

Expressions can be very small or can contain several operations.

For example:

`quantity * price`

is an arithmetic expression.

A more complicated calculation can be:

`quantity * price - quantity * price * discount_rate`

The result is still a value produced by evaluating the expression.

Complex expressions should normally be divided into meaningful intermediate values when that improves readability, validation, testing, or debugging.

---

## Values and operands

An operator acts on one or more operands.

For example:

`10 + 5`

contains:

- `10`: left operand
- `+`: operator
- `5`: right operand

The result is `15`.

Operators can be classified by the number of operands they require.

### Unary operators

A unary operator works with one operand.

Examples include:

- Python: `-number`
- JavaScript: `!value`
- C++: `++counter`

For example:

`-10`

changes the sign of the value.

### Binary operators

A binary operator uses two operands.

Examples include:

- `a + b`
- `a - b`
- `a * b`
- `a > b`
- `a && b`

### Conditional operators

Some languages provide an operator that selects between two expressions based on a condition.

Python uses a conditional expression such as:

`"even" if number % 2 == 0 else "odd"`

JavaScript and C++ use the conditional operator:

`condition ? value_if_true : value_if_false`

---

## Arithmetic operators

Arithmetic operators perform numerical calculations.

| Operation | Python | JavaScript | C++ |
|---|---|---|---|
| Addition | `+` | `+` | `+` |
| Subtraction | `-` | `-` | `-` |
| Multiplication | `*` | `*` | `*` |
| Division | `/` | `/` | `/` |
| Remainder | `%` | `%` | `%` |
| Exponentiation | `**` | `**` | usually `std::pow` or multiplication |
| Floor division | `//` | no dedicated operator | no dedicated operator |

### Addition

`a + b`

adds two values.

### Subtraction

`a - b`

subtracts the right operand from the left operand.

### Multiplication

`a * b`

multiplies two values.

### Division

`a / b`

divides the left operand by the right operand.

The behavior of division differs between languages.

Python's `/` produces a floating-point result.

JavaScript's `/` normally produces a JavaScript `Number`.

C++ division depends on operand types. If both operands are integers, the result is integer division.

For example, in C++:

`17 / 5`

produces `3`.

If floating-point division is intended, at least one operand must be floating point:

`static_cast<double>(17) / 5`

produces `3.4`.

---

## Modulo

The modulo operator is `%`.

It returns the remainder after division.

For example:

`17 % 5`

produces `2`.

Modulo is particularly important in algorithmic programming.

### Even and odd numbers

An integer is even when its remainder after division by two is zero.

The condition is:

`number % 2 == 0`

An integer is odd when:

`number % 2 != 0`

The three implementations use this rule directly.

### Divisibility

A number `a` is divisible by `b` when:

`a % b == 0`

For example:

`100 % 5 == 0`

is true.

Modulo therefore provides a direct implementation of many divisibility problems.

### Digit extraction

For a positive decimal integer, the last digit can be obtained with:

`number % 10`

For example:

`58327 % 10`

produces `7`.

The remaining digits can be obtained with integer division:

`58327 // 10`

in Python, or an appropriate integer division operation in C++ and JavaScript.

Repeating these two operations allows a program to:

- extract digits
- calculate digit sums
- count digits
- reverse numbers
- test digit properties
- construct new numbers

The Python, JavaScript, and C++ implementations all demonstrate this technique.

---

## Comparison operators

Comparison operators produce Boolean results.

Common comparison operators are:

| Meaning | Python | JavaScript | C++ |
|---|---|---|---|
| Equal | `==` | `===` normally | `==` |
| Not equal | `!=` | `!==` normally | `!=` |
| Less than | `<` | `<` | `<` |
| Less than or equal | `<=` | `<=` | `<=` |
| Greater than | `>` | `>` | `>` |
| Greater than or equal | `>=` | `>=` | `>=` |

The result is normally a Boolean value.

For example:

`age >= 18`

asks whether `age` is at least 18.

### Equality differences

Python's `==` compares values.

C++'s `==` normally compares values according to the types involved.

JavaScript has two equality systems:

- `==`, which permits type coercion
- `===`, which performs strict equality

For example:

`5 == "5"`

is true in JavaScript because the string can be converted for the comparison.

But:

`5 === "5"`

is false because the operands have different types.

The JavaScript implementation demonstrates this distinction and uses strict equality for normal comparisons.

---

## Chained comparisons

Python allows expressions such as:

`0 <= age <= 100`

This is a language feature.

It is not valid C++ or JavaScript syntax with the same mathematical meaning.

In C++ and JavaScript, the condition should normally be written explicitly:

`age >= 0 && age <= 100`

This is an important example of why programming syntax must be understood within the rules of the language being used.

---

## Logical operators

Logical operators combine conditions.

The core operations are:

- AND
- OR
- NOT

### AND

Python:

`condition_a and condition_b`

JavaScript:

`conditionA && conditionB`

C++:

`conditionA && conditionB`

AND requires both conditions to be true for the combined Boolean condition to be true.

For example:

`age >= 18 and has_id`

requires both conditions to be satisfied in Python.

### OR

Python:

`condition_a or condition_b`

JavaScript and C++:

`conditionA || conditionB`

OR requires at least one condition to be true.

### NOT

Python:

`not condition`

JavaScript and C++:

`!condition`

NOT reverses a Boolean value.

---

## Short-circuit evaluation

Short-circuit evaluation means that a logical expression may stop being evaluated before every operand is processed.

For AND, if the left side is already false, the right side does not need to be evaluated.

For OR, if the left side is already true, the right side does not need to be evaluated.

This has practical consequences.

A condition such as:

`denominator != 0 && 100 / denominator > 2`

can protect the division because the second expression is evaluated only when the denominator is non-zero.

Short-circuit evaluation can also improve performance by avoiding unnecessary calculations.

It should not be confused with ordinary Boolean simplification. In languages such as JavaScript and Python, logical operators can also return operands rather than strictly returning Boolean values.

---

## Logical operators as value-producing operators in JavaScript

JavaScript has an important behavior:

`a && b`

and

`a || b`

can return one of their operands.

For example:

`"hello" && 42`

produces `42`.

Similarly:

`"" && 42`

produces the empty string.

A common pattern is:

`username || "Guest"`

This uses the fallback when `username` is falsy.

This behavior is different from pure Boolean algebra and should be understood before using these expressions in application code.

---

## Nullish coalescing

Modern JavaScript provides:

`??`

Nullish coalescing uses a fallback only when the left operand is `null` or `undefined`.

This differs from `||`.

For example:

`0 || 100`

produces `100`.

But:

`0 ?? 100`

produces `0`.

This distinction matters when zero, an empty string, or another falsy value is a legitimate input.

---

## Optional chaining

JavaScript also provides:

`?.`

Optional chaining allows property or method access without immediately throwing an error when an intermediate value is `null` or `undefined`.

For example:

`user?.profile?.name`

can safely attempt to reach `name`.

The JavaScript implementation demonstrates optional chaining together with nullish coalescing.

---

## Assignment operators

The basic assignment operator is:

`=`

For example:

`value = 10`

stores `10` in `value`.

Compound assignment operators combine an operation with assignment.

Common examples are:

- `+=`
- `-=`
- `*=`
- `/=`
- `%=`
- `**=`

For example:

`value += 5`

is conceptually equivalent to increasing the existing value by five and assigning the result back.

These operators are useful for counters, accumulators, totals, balances, quantities, and other changing state.

---

## Increment and decrement

C++, JavaScript, and several other languages provide:

- `++`
- `--`

Python does not provide these operators.

In Python, incrementing is normally written as:

`counter += 1`

and decrementing as:

`counter -= 1`.

### Prefix and postfix forms

C++ and JavaScript distinguish:

`++counter`

from:

`counter++`

Prefix increment changes the value first and then produces the new value.

Postfix increment produces the old value and then changes the variable.

For example:

`int counter = 5;`

`counter++`

produces `5` as the expression value while changing `counter` to `6`.

By contrast:

`++counter`

changes the value to `7` before producing the expression value when the starting value was `6`.

This distinction becomes important when increment and decrement operations appear inside larger expressions.

In general, using increment or decrement as a separate statement is easier to read than embedding multiple state changes in one complex expression.

---

## Operator precedence

Operator precedence determines which operators are evaluated first when parentheses do not explicitly specify the order.

For example:

`2 + 3 * 4`

is evaluated as:

`2 + (3 * 4)`

and produces `14`.

The multiplication occurs before the addition.

Parentheses change the order:

`(2 + 3) * 4`

produces `20`.

### Practical rule

When an expression is difficult to understand, use parentheses even when the language's precedence rules already produce the intended result.

The goal is not only machine correctness. It is also human readability and maintainability.

---

## Expressions and readability

A technically valid expression is not necessarily a well-designed expression.

Consider a calculation involving:

- quantity
- unit price
- discount
- discounted price
- tax
- final amount

A single expression can calculate the final value, but separate intermediate variables often make the calculation easier to inspect:

`subtotal`

`discount`

`discounted_price`

`tax`

`final_price`

This approach makes it easier to:

- debug calculations
- test intermediate values
- validate inputs
- identify incorrect formulas
- explain the algorithm
- modify business rules

The Python implementation explicitly demonstrates both a staged calculation and an equivalent larger expression.

---

## Conditional expressions

Conditional expressions select one value according to a condition.

Python uses:

`value_if_true if condition else value_if_false`

For example:

`"even" if number % 2 == 0 else "odd"`

JavaScript and C++ use:

`condition ? value_if_true : value_if_false`

These are useful for short, straightforward decisions.

Nested conditional expressions can become difficult to read. When several conditions are involved, ordinary `if`, `else if`, and `else` statements are often clearer.

---

## Bitwise operators

Bitwise operators work at the level of individual bits in integer representations.

Common bitwise operations include:

- AND
- OR
- XOR
- NOT
- left shift
- right shift

Python, JavaScript, and C++ all provide bitwise operators, although their integer models differ.

Typical operators include:

`&`

`|`

`^`

`~`

`<<`

`>>`

### Bitmasks

Bitwise operators are useful for representing multiple independent Boolean flags in a single integer-like value.

For example, permissions can be represented as:

- View = `001`
- Purchase = `010`
- Refund = `100`

Combining View and Purchase produces:

`011`

Testing a particular permission can be performed with bitwise AND.

The C++ case study uses an enum-based permission system to demonstrate this concept in a type-oriented manner.

---

## Membership and identity in Python

Python provides operators that are not ordinary arithmetic or comparison operators.

### Membership

`in`

`not in`

can test whether a value belongs to a collection.

For example:

`"Python" in languages`

checks membership in a list.

### Identity

`is`

`is not`

test whether two references refer to the same object.

This differs from `==`, which tests value equality.

For example, two separate lists can contain the same values:

`[1, 2, 3] == [1, 2, 3]`

is true.

But they may be different objects:

`first is second`

is false when the lists were separately created.

Identity checks are commonly associated with checks such as:

`value is None`

rather than value comparisons.

---

## Python operator overloading

Python allows classes to define special methods that control how certain operators behave.

The Python implementation defines a `Vector2D` class with:

- `__add__`
- `__sub__`
- `__mul__`

This permits expressions such as:

`first + second`

where `first` and `second` are vectors.

The operator is not performing ordinary scalar addition. The class defines what addition means for that domain.

Operator overloading should represent a natural and understandable operation. It should not be used merely to make unrelated operations look like arithmetic.

---

## C++ operator overloading

C++ provides extensive operator overloading capabilities.

The case study defines a `Money` class with operators such as:

- `+`
- `-`
- `+=`
- `-=`
- `<`
- `>`
- `==`

This allows monetary values to participate in expressions such as:

`subtotal - discount`

and:

`total += order.total`

The class stores currency internally as integer cents rather than a binary floating-point value.

For many financial-style calculations, representing monetary amounts using an integer smallest-unit representation avoids common binary floating-point representation issues.

The exact representation required by a real financial system depends on its currency rules, rounding requirements, accounting standards, and regulatory environment.

---

## JavaScript and operator overloading

JavaScript does not provide Python- or C++-style user-defined operator overloading for ordinary classes.

A JavaScript domain object therefore commonly exposes explicit methods.

The JavaScript implementation uses:

`distance.scale(2)`

rather than defining a custom multiplication operator for the `Measurement` class.

This is an important language-level distinction.

---

## Type conversion and coercion

Different languages handle type conversion differently.

Python generally uses explicit conversion functions such as:

`int()`

`float()`

`str()`

JavaScript performs both explicit and implicit type conversion.

For example:

`Number("5")`

explicitly converts a string to a number.

JavaScript's `+` operator can also concatenate strings.

Therefore:

`"5" + 3`

produces a string result.

Other arithmetic operators can trigger numeric conversion.

For example:

`"5" - 3`

performs numeric conversion.

Understanding these rules is important because apparently similar expressions can have different results depending on operand types.

---

## Boolean values and truthiness

Boolean expressions are central to decision-making.

Python and JavaScript both have concepts of truthy and falsy values, although the exact rules differ.

Examples of values commonly treated as false-like include:

- `False` or `false`
- zero
- empty strings
- null-like values

JavaScript has an important distinction:

`[]`

and:

`{}`

are truthy even though they are empty.

The JavaScript implementation demonstrates these values explicitly.

---

## Floating-point arithmetic

Binary floating-point numbers cannot represent every decimal fraction exactly.

This means an expression such as:

`0.1 + 0.2`

may not produce an exact binary representation of decimal `0.3`.

Python demonstrates the use of:

`math.isclose()`

for approximate comparisons.

Python's `Decimal` type is also demonstrated for decimal-oriented arithmetic.

JavaScript uses the IEEE 754 double-precision floating-point representation for its ordinary `Number` type.

For JavaScript applications requiring exact decimal monetary behavior, the representation and arithmetic strategy must be designed deliberately.

---

## Division by zero

Division by zero is an important edge case.

Python normally raises `ZeroDivisionError`.

C++ integer division by zero has undefined behavior and therefore must be prevented.

JavaScript numeric division by zero generally produces:

- `Infinity`
- `-Infinity`
- `NaN`

depending on the operands.

This is an important cross-language difference.

The three implementations demonstrate different handling strategies.

---

## Integer division

Python provides:

`//`

for floor division.

For positive values:

`17 // 5`

produces `3`.

For negative values, Python's floor division is mathematically different from simply truncating toward zero.

JavaScript does not have a dedicated `//` operator. `Math.floor()` can be used when floor behavior is intended.

C++ integer division truncates toward zero.

These differences matter when algorithms use negative numbers.

---

## JavaScript Number and BigInt

JavaScript's ordinary `Number` type is a floating-point numeric type.

It can exactly represent integers only within a specific safe integer range.

The implementation demonstrates:

`Number.MAX_SAFE_INTEGER`

and JavaScript's `BigInt`.

BigInt literals use the `n` suffix, for example:

`9007199254740991n`

BigInt is useful when exact integer arithmetic is required beyond the safe integer range.

Ordinary `Number` and `BigInt` cannot be freely mixed in arithmetic expressions.

---

## Practical problem: even or odd

The standard expression is:

`number % 2 == 0`

in Python or C++, and:

`number % 2 === 0`

in JavaScript.

This is an example of a small expression becoming a reusable algorithmic rule.

The implementations apply the rule to positive, negative, and zero values.

---

## Practical problem: positive, negative, or zero

The basic classification uses comparisons:

- `number > 0`
- `number < 0`
- otherwise zero

This demonstrates how comparison operators combine with conditional logic.

It also illustrates why boundary cases matter. Zero is neither positive nor negative in ordinary mathematical classification.

---

## Practical problem: largest of two numbers

The largest of two values can be found with a comparison:

`a if a >= b else b`

or with a language's built-in maximum function.

The important expression is the comparison itself.

The C++ case study also demonstrates standard-library facilities such as `std::max`.

---

## Practical problem: largest of three numbers

The largest of three values can be calculated through nested comparisons or a standard library function.

The C++ implementation uses `std::max`.

The Python implementation uses `max`.

The JavaScript implementation uses `Math.max`.

The same mathematical requirement therefore maps naturally to each language's standard facilities.

---

## Practical problem: divisibility

A number is divisible by another number when the remainder is zero.

The expression is:

`number % divisor == 0`

The divisor must be validated because modulo by zero is invalid.

The implementations explicitly demonstrate this failure condition.

---

## Practical problem: digit calculations

Modulo and integer division provide a general digit-processing technique.

For a positive decimal integer:

1. `number % 10` obtains the final digit.
2. Integer division by 10 removes the final digit.
3. Repeat until no digits remain.

This supports:

- digit sum
- digit counting
- number reversal
- digit classification
- palindrome-related algorithms

For example, the number `58327` can be processed as:

`7`

then:

`2`

then:

`3`

then:

`8`

then:

`5`

The Python, JavaScript, and C++ programs implement digit processing directly rather than relying entirely on string conversion.

---

## Simple calculator

The three implementations include calculator functionality.

### Python

Python maps operator symbols to functions using the `operator` module.

This creates a compact relationship between:

- `+`
- `-`
- `*`
- `/`
- `//`
- `%`
- `**`

and their corresponding operations.

The calculator validates unsupported operators and division by zero.

### JavaScript

JavaScript uses an object whose properties contain functions.

For example, an operator symbol maps to a function that performs the operation.

This demonstrates that functions can be stored as values and selected dynamically.

### C++

The C++ case study does not rely on a simple text calculator as its main application. Instead, it uses operators inside a larger marketplace billing system.

This demonstrates how arithmetic expressions become components of a realistic application.

---

## C++ case study: marketplace billing engine

The C++ program models a small digital marketplace.

The system contains:

- products
- prices
- stock quantities
- orders
- discounts
- taxes
- revenue
- permissions
- validation
- low-stock reporting

This creates a realistic environment in which operators and expressions are used repeatedly.

---

## Product representation

Each product contains:

- product ID
- product name
- price
- stock
- category code

A product is validated before it is added.

The validation prevents:

- non-positive product IDs
- empty names
- negative prices
- negative stock
- duplicate product IDs

These checks use comparison and logical expressions.

---

## Money representation

The `Money` class stores amounts in cents.

For example:

`1200`

represents:

`12.00`

This approach allows arithmetic such as:

`subtotal + tax`

without storing the amount itself as a binary floating-point number.

The class provides operator overloads for common operations.

This makes the billing expressions readable while keeping the underlying representation explicit.

---

## Order calculation

The marketplace calculates:

`subtotal = price × quantity`

Then:

`discount = subtotal × discount percentage`

Then:

`discounted subtotal = subtotal - discount`

Then:

`tax = discounted subtotal × tax percentage`

Finally:

`total = discounted subtotal + tax`

The calculations are built from arithmetic expressions and compound assignments.

The program also validates:

- quantity
- discount percentage
- tax percentage
- available stock

---

## Stock management

Stock is reduced using compound assignment:

`product.stock -= quantity`

The operation occurs only after the requested quantity has passed validation.

The system refuses an order when the requested quantity is larger than available stock.

The failure is represented using `std::optional<Order>`.

This is preferable to silently creating an invalid order.

---

## Permission flags

The C++ program defines permissions using bit flags.

The permissions include:

- View
- Purchase
- Refund
- Admin

Bitwise OR combines permissions.

Bitwise AND checks whether a particular permission exists.

This is a common pattern in systems programming and configuration management.

---

## Order identifiers and increment

The marketplace generates order IDs using a counter:

`nextOrderId_++`

This demonstrates postfix increment in a real application context.

The old counter value is used as the ID, after which the counter is increased for the next order.

---

## Conditional expressions in the case study

The C++ program uses the conditional operator for concise classifications such as even or odd.

For larger business decisions, ordinary conditional statements would generally be more readable.

The choice between a conditional expression and a multi-line conditional structure should be based on clarity rather than merely reducing line count.

---

## Validation and error handling

The implementations use different mechanisms.

### Python

Python uses exceptions such as:

`ValueError`

and:

`ZeroDivisionError`

### JavaScript

JavaScript uses:

`throw new Error(...)`

and:

`try...catch`

### C++

C++ uses standard exceptions such as:

`std::invalid_argument`

`std::out_of_range`

`std::overflow_error`

and:

`std::runtime_error`

These mechanisms allow invalid conditions to be detected instead of silently producing incorrect results.

---

## Edge cases

Important edge cases include:

- zero
- negative values
- zero divisors
- very large integers
- floating-point values
- empty strings
- missing values
- invalid operators
- insufficient stock
- invalid percentages
- integer overflow
- minimum and maximum numeric values

A robust implementation considers these cases before they become production failures.

---

## Operator precedence and correctness

Precedence errors can produce mathematically valid but logically incorrect programs.

For example:

`a + b * c`

means:

`a + (b * c)`

not:

`(a + b) * c`

Parentheses are therefore important when the intended mathematical grouping is different.

The same principle applies to logical expressions.

For example:

`a || b && c`

is governed by operator precedence, but explicitly writing the intended grouping can make the code easier to review.

---

## Common mistakes

### Confusing assignment with comparison

Assignment:

`value = 10`

Comparison:

`value == 10`

JavaScript commonly uses:

`value === 10`

for strict equality.

### Dividing by zero

Always validate a divisor when it can originate from user input or external data.

### Ignoring integer division

In C++, integer division discards the fractional component.

In Python, `/` and `//` have different purposes.

### Misusing modulo with floating-point values

Modulo is primarily useful for integer divisibility and remainder problems. Floating-point remainder behavior should be used deliberately.

### Assuming all languages have the same precedence

Languages share many conventional precedence rules, but their complete operator systems differ.

### Using `is` instead of `==` in Python

`is` tests identity rather than ordinary value equality.

### Using JavaScript `==` without understanding coercion

Implicit conversion can produce surprising comparisons.

### Confusing `||` and `??`

`||` treats many falsy values as absent.

`??` specifically targets `null` and `undefined`.

### Overusing complex expressions

A shorter expression is not automatically better.

Named intermediate variables can make important calculations easier to verify.

### Ignoring overflow

C++ integer types have fixed ranges.

Python integers grow dynamically, while JavaScript `Number` has precision limits and JavaScript `BigInt` has different arithmetic rules.

---

## Important distinctions between the languages

| Concept | Python | JavaScript | C++ |
|---|---|---|---|
| Main ordinary integer model | Arbitrary-precision integers | `Number` plus `BigInt` | Fixed-width integer types |
| Integer division | `//` | No dedicated operator | `/` with integer operands |
| Increment operator | Not available | `++` | `++` |
| Decrement operator | Not available | `--` | `--` |
| Strict equality | `==` compares values | `===` | `==` |
| Logical AND | `and` | `&&` | `&&` |
| Logical OR | `or` | `||` | `||` |
| Logical NOT | `not` | `!` | `!` |
| Exponentiation | `**` | `**` | Usually `std::pow` |
| Conditional expression | `x if condition else y` | `condition ? x : y` | `condition ? x : y` |
| Modulo | `%` | `%` | `%` |
| Bitwise AND | `&` | `&` | `&` |
| User-defined operator overloading | Supported | Not ordinary class operator overloading | Supported |
| Chained comparison | Supported | Not equivalent to mathematical chaining | Not equivalent to mathematical chaining |
| Membership operator | `in` | No equivalent `in` operator for general arrays | No general `in` operator |
| Identity operator | `is` | Reference identity is represented through strict equality for objects | Object identity depends on the type and expression |

---

## Performance considerations

Most basic arithmetic operations are constant-time for ordinary machine-sized values.

The performance of an entire algorithm usually depends more heavily on:

- number of operations
- input size
- data structures
- memory access
- algorithmic complexity
- repeated computation
- I/O
- allocation behavior

For example, checking whether every number from `1` through `n` is even requires O(n) iterations.

Each modulo operation is generally treated as an O(1) primitive operation for ordinary machine-sized integers.

Therefore, the complete loop is O(n).

Replacing `% 2` with a cleverer-looking expression does not normally change the fundamental complexity.

Algorithm design should be considered before micro-optimizing basic operators.

---

## Security considerations

Operators themselves are normally low-level language mechanisms, but expressions can become security-sensitive when their operands originate from external input.

Important considerations include:

- validate numeric input
- reject invalid divisors
- constrain quantities and percentages
- check integer overflow in fixed-width languages
- avoid unsafe assumptions about numeric ranges
- validate financial calculations
- distinguish missing values from legitimate zero values
- avoid executing untrusted expressions dynamically
- avoid constructing executable code from user-provided strings

A calculator should parse permitted operations explicitly rather than evaluating arbitrary source code supplied by a user.

The Python calculator demonstrates an operator lookup table rather than executing an arbitrary expression string.

---

## Financial calculation considerations

The marketplace case study intentionally stores money as integer cents.

For example:

`₹12.00`

can be represented as:

`1200`

The exact implementation required for production financial systems depends on:

- currency
- decimal precision
- rounding rules
- taxation
- accounting requirements
- localization
- exchange rates
- regulatory requirements

Floating-point arithmetic should not automatically be assumed to be appropriate for exact monetary calculations.

---

## Debugging expressions

When an expression produces an unexpected result, break it into meaningful pieces.

For example, instead of immediately inspecting:

`quantity * price - quantity * price * discount + ...`

calculate:

`subtotal`

then:

`discount`

then:

`discounted_subtotal`

then:

`tax`

then:

`total`

This allows each intermediate value to be tested independently.

Useful debugging questions include:

- What are the operand types?
- What are the operand values?
- What precedence rules apply?
- Is integer division occurring?
- Is a conversion occurring?
- Could the divisor be zero?
- Could the value overflow?
- Is floating-point precision relevant?
- Is a logical expression short-circuiting?
- Is a variable being changed by an increment or compound assignment?

---

## Implementation mapping

### Python implementation

The Python program emphasizes:

- readable arithmetic expressions
- modulo-based algorithms
- comparison operators
- logical operators
- augmented assignment
- Python's absence of `++` and `--`
- floor division
- chained comparisons
- conditional expressions
- membership
- identity
- assignment expressions
- floating-point comparison with `math.isclose`
- decimal arithmetic
- operator overloading
- validation
- assertions

The `Vector2D` class demonstrates how Python can give mathematical meaning to operators through special methods.

### JavaScript implementation

The JavaScript program emphasizes:

- arithmetic operators
- strict and loose equality
- logical operators
- short-circuit evaluation
- prefix and postfix increment/decrement
- assignment operators
- conditional expressions
- type coercion
- truthy and falsy values
- logical operators returning operands
- nullish coalescing
- optional chaining
- bitwise operations
- `Number`
- `BigInt`
- validation
- JavaScript classes and methods

The `Measurement` class demonstrates an explicit method-based approach where Python or C++ might use operator overloading.

### C++ implementation

The C++ program provides the most substantial system-style case study.

It demonstrates:

- arithmetic expressions
- integer division
- comparison operators
- logical operators
- short-circuit evaluation
- compound assignment
- prefix and postfix increment/decrement
- modulo
- conditional expressions
- bitwise permissions
- operator overloading
- integer-based money representation
- validation
- exceptions
- `std::optional`
- `std::unordered_map`
- `std::vector`
- stock management
- billing calculations
- order generation
- revenue calculation
- low-stock reporting
- complexity analysis

---

## Complexity of the major algorithms

### Even or odd

Checking:

`number % 2 == 0`

takes O(1) time for ordinary machine-sized integer values.

### Divisibility

Checking:

`number % divisor == 0`

is treated as O(1) for ordinary fixed-width integers.

### Digit sum

For a number containing `d` decimal digits, the digit-processing loop runs approximately `d` times.

Time complexity:

O(d)

For ordinary fixed-width integers, the number of digits is bounded. For arbitrarily large integers, the digit count matters explicitly.

### Reverse integer

The reverse operation processes each decimal digit once.

Time complexity:

O(d)

### Largest of three values

Only a fixed number of comparisons are required.

Time complexity:

O(1)

### Marketplace product lookup

The C++ case study uses `unordered_map` for product storage.

Average-case lookup is approximately O(1), although worst-case behavior can differ because hash-table performance depends on the distribution of keys and implementation details.

### Low-stock report

Every stored product is inspected.

For `n` products:

Time complexity:

O(n)

### Revenue calculation

Every completed order is visited.

For `m` orders:

Time complexity:

O(m)

---

## Practical applications

Operators and expressions appear throughout software systems.

Examples include:

- financial calculations
- billing systems
- taxation
- shopping carts
- inventory management
- access control
- authentication conditions
- data validation
- scientific calculations
- engineering formulas
- game mechanics
- search algorithms
- sorting conditions
- database filtering
- networking logic
- resource management
- operating systems
- embedded systems
- cryptographic implementations
- machine-learning calculations
- scheduling
- simulation
- statistics
- web applications

Operators are therefore not an isolated beginner topic. They form part of nearly every executable algorithm.

---

## Production considerations

Production code should treat expressions as part of a larger correctness system.

Important practices include:

- validate external input
- use explicit types when appropriate
- use parentheses where they improve clarity
- avoid unnecessarily complicated expressions
- test boundary values
- test zero and negative values
- test invalid divisors
- test numeric limits
- use appropriate numeric representations
- avoid unintended type coercion
- use strict equality in JavaScript when appropriate
- use explicit conversions when numeric semantics matter
- use domain-specific classes when they improve correctness
- document non-obvious formulas
- test intermediate calculations
- avoid silent failure
- consider overflow in fixed-width integer languages
- consider floating-point precision
- use appropriate error handling

---

## Files in this project

The four deliverables are:

- `operators_and_expressions.py`: comprehensive Python study and practice program
- `operators_and_expressions.js`: JavaScript implementation with language-specific operator behavior
- `operators_and_expressions.cpp`: C++17 marketplace billing case study
- `README.md`: conceptual and implementation documentation

---

## Running the Python implementation

Use Python 3.10 or later.

Run:

`python operators_and_expressions.py`

The program prints demonstrations, practical examples, edge cases, and verification results.

---

## Running the JavaScript implementation

Use a modern Node.js runtime.

Run:

`node operators_and_expressions.js`

The program prints JavaScript-specific operator behavior, numerical examples, validation cases, and verification results.

---

## Running the C++ implementation

Use a compiler supporting C++17 or later.

Compile with:

`g++ -std=c++17 -O2 operators_and_expressions.cpp -o operators`

Then run:

`./operators`

On Windows with a suitable C++ compiler, the generated executable can be run as:

`operators.exe`

The C++ program executes the operator demonstrations, marketplace case study, validation examples, complexity demonstration, and verification tests.
