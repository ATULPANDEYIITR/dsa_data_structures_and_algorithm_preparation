# Recursion Fundamentals

## Overview

Recursion solves a problem by having a function call itself on a smaller instance of the same problem. A correct recursive algorithm must make progress toward a terminating condition and combine the results of smaller computations into the final answer.

This project implements recursion in Python, JavaScript, C++17, Java 17, and PostgreSQL. Each implementation covers recursive arithmetic, sequence processing, string reversal, array operations, search, validation, and the relationship between recursive calls and the call stack.

## Core Concepts

### Base Case

A base case defines the smallest input that can be answered without another recursive call. It prevents the computation from continuing indefinitely.

Examples include:

- `factorial(0) = 1`
- `fibonacci(0) = 0`
- `power(base, 0) = 1`
- The sum of an empty array is zero.
- Reversing an empty or single-character string requires no further processing.

The base case must match the mathematical definition of the problem. Returning zero for factorial at zero, for example, would make every positive factorial incorrect.

### Recursive Case

The recursive case reduces the original problem to smaller instances.

For factorial:

\[
n! = n \times (n-1)!
\]

The implementation computes the factorial of a smaller integer, then multiplies the returned result by the current integer.

For a sum:

\[
S(n) = n + S(n-1)
\]

For exponentiation by squaring:

\[
b^n =
\begin{cases}
1 & n = 0 \\
(b^{n/2})^2 & n \text{ is even} \\
b(b^{\lfloor n/2 \rfloor})^2 & n \text{ is odd}
\end{cases}
\]

The exponentiation algorithm reduces the exponent approximately by half per call, improving its time complexity from \(O(n)\) to \(O(\log n)\).

### Call Stack

Each active recursive call maintains its own execution state. This state includes arguments, local variables, the return location, and intermediate results that must be combined after the child call finishes.

For `factorial(4)`, the calls expand as follows:

    factorial(4)
      factorial(3)
        factorial(2)
          factorial(1)
          return 1
        return 2
      return 6
    return 24

Calls descend until a base case is reached. Results then propagate upward as calls return.

Deep recursion can exhaust the available call stack. Python and JavaScript have runtime-specific recursion limits, and C++ and Java can terminate through stack exhaustion. A recursion limit is therefore a practical safeguard, not a mathematical requirement.

### Recursive State

Recursive state is the information needed to describe a particular subproblem.

| Algorithm | Recursive state | Progress |
|---|---|---|
| Factorial | Current integer `n` | Decrement `n` |
| Fibonacci | Position `n` | Reduce positions by one and two |
| Power | Base and exponent | Halve the exponent |
| Sum | Remaining integer or array index | Decrease the integer or advance the index |
| String reversal | Current position or remaining suffix | Move toward the string boundary |
| Binary search | Left and right boundaries | Discard half the search interval |

A well-designed recursive function makes its state explicit. Incorrect state updates can cause repeated work, incorrect results, invalid indexing, or infinite recursion.

## Implemented Algorithms

### Factorial

Factorial multiplies all positive integers up to the supplied integer.

\[
n! =
\begin{cases}
1 & n \leq 1 \\
n(n-1)! & n > 1
\end{cases}
\]

The implementation rejects negative inputs. Python and Java use arbitrary-precision integer arithmetic through native integers and `BigInteger`, respectively. The C++ version uses `uint64_t` and rejects inputs beyond its supported factorial range. The JavaScript implementation uses safe integer validation and a practical upper bound.

Time complexity is \(O(n)\), and recursive stack usage is \(O(n)\).

### Fibonacci

The Fibonacci sequence follows:

\[
F(n) =
\begin{cases}
0 & n = 0 \\
1 & n = 1 \\
F(n-1) + F(n-2) & n > 1
\end{cases}
\]

A direct recursive implementation repeats many calculations. The Python, JavaScript, C++, and Java implementations use memoization or cached results to avoid recomputing completed subproblems.

Memoized Fibonacci takes \(O(n)\) time and \(O(n)\) additional space for the cache, with recursion depth proportional to \(n\). PostgreSQL uses a direct recursive definition with a restrictive input limit because it does not implement memoization in the supplied function.

### Power

Power computes a non-negative integer exponent using exponentiation by squaring. It returns one when the exponent is zero, including when the base is zero under the conventional integer-power definition.

The exponent is halved at each recursive level. The number of recursive levels is \(O(\log n)\), excluding the cost of arithmetic on very large numbers.

Negative exponents are rejected because the implementations focus on integer results. Fixed-width implementations must also guard against overflow.

### Sum

The sum algorithm computes the sum of integers from zero through a supplied non-negative integer.

\[
S(n) =
\begin{cases}
0 & n = 0 \\
n + S(n-1) & n > 0
\end{cases}
\]

Its time complexity and stack usage are both \(O(n)\).

The SQL implementation uses `BIGINT` for the sum, while Python and Java use integer types suitable for their respective arithmetic models. The C++ implementation applies a demonstration input limit to avoid unreasonable recursion depth.

### Reverse Operations

String reversal illustrates how a result can be constructed while recursive calls return. Each call processes a smaller string or advances to the next character, then places the character in the appropriate output position.

The implementations use different techniques:

- Python combines the reversal of the suffix with the first character.
- JavaScript converts strings into Unicode code points before reversing, avoiding reversal of individual UTF-16 surrogate halves.
- C++ processes the input string by position. Its demonstration uses byte-oriented `std::string`, so it is suitable for ASCII but does not fully reverse Unicode grapheme clusters.
- Java processes Unicode code points and appends them to a `StringBuilder`.
- PostgreSQL removes the first character and recursively reverses the remaining text.

Reversal by repeatedly copying substrings or concatenating immutable strings can take \(O(n^2)\) time. In-place array reversal uses two boundaries and performs \(O(n)\) swaps.

### Recursive Array Processing

Array sum uses an index as the recursive state. Each call adds the current element to the sum of the remaining elements. The base case occurs when the index reaches the array length.

For an array of length \(n\), the algorithm takes \(O(n)\) time and \(O(n)\) stack space.

The examples also include maximum-value calculation and binary search. Binary search requires sorted input, compares the target with the middle element, and recursively processes only the half that could contain the target.

Binary search takes \(O(\log n)\) time and stack space. An absent target returns `-1`. Empty arrays are valid search inputs, while maximum-value calculation rejects empty arrays because no maximum exists.

## Python Implementation

The Python script provides:

- Explicit input validation through `require_integer`.
- Factorial, memoized Fibonacci, exponentiation by squaring, and recursive summation.
- String and list reversal.
- Indexed array summation and maximum-value calculation.
- Recursive binary search.
- Immutable `CallFrame` records for visualizing recursive depth.
- Assertion-based tests covering ordinary inputs and invalid conditions.

Python's `functools.lru_cache` supplies memoization for Fibonacci. The `dataclass` declaration makes recorded stack-frame information structured and easy to inspect.

The script uses only the standard library and runs its tests before printing example results. Recursion limits remain relevant even when Python integers can represent arbitrarily large results.

## JavaScript Implementation

The JavaScript file uses a closure to maintain a Fibonacci cache. This keeps memoization state private to the returned calculation function.

The recursive array reversal works on copies, preserving the caller's original array. The string reversal uses `Array.from` to operate on Unicode code points rather than individual UTF-16 code units.

`RecursionEventProcessor` demonstrates event-driven observation of recursive execution. Event handlers are registered by name and awaited in sequence. Sequential awaiting preserves the registered handler order and propagates handler failures to the caller.

The program checks calculated values against expected results and uses explicit process failure reporting. Its safe-integer validation prevents unsupported integer inputs, although arithmetic results should still be checked when precision-sensitive values exceed JavaScript's safe integer range.

## C++17 Implementation

The C++ program organizes algorithms inside a `RecursionLab` class. Public static methods expose the supported operations, while private helpers implement memoization, recursive string processing, array reversal, and binary search.

The Fibonacci cache uses `std::unordered_map`. Array reversal uses `std::swap` to modify a local copy, and binary search validates that the input is sorted.

`std::uint64_t` provides a fixed-width unsigned result type for factorial and power. The implementation checks multiplication bounds before performing operations that could overflow. `std::numeric_limits` supplies the maximum representable value.

Exceptions communicate invalid input and arithmetic overflow. A top-level exception handler prints failures and returns a non-zero exit status. The call-stack trace prints recursive descent and return events to show that calls unwind in the opposite order from their invocation.

The demonstration is intended for ordinary teaching inputs. Recursive stack depth and fixed-width arithmetic remain limitations even when individual algorithms are mathematically correct.

## Java 17 Implementation

The Java implementation uses domain-oriented types to represent calculation results, call frames, and evaluation outcomes.

Java records provide immutable data carriers for `CallFrame`, `CalculationResult`, and `CalculationOutcome`. The `CalculationStatus` enum distinguishes successful calculations from rejected inputs. The `RecursiveOperation` interface represents a calculation contract, while `Supplier<BigInteger>` allows the evaluation service to execute a calculation and capture supported validation failures.

`BigInteger` prevents arithmetic overflow in factorial, Fibonacci, power, and summation. The recursive algorithms still have stack-depth limits, and large arbitrary-precision operations consume additional time and memory.

The `reverseString` method converts text into Unicode code points. The list-reversal method creates a copy before swapping elements, then returns an unmodifiable view. Binary search checks ordering before descending into a smaller interval.

The evaluation service returns a structured failure outcome for supported invalid calculations rather than silently accepting bad input. Unexpected programming errors are not disguised as ordinary validation failures.

## PostgreSQL Implementation

The SQL script implements recursive calculations as PL/pgSQL functions and records their execution in a relational table.

### Calculation Functions

The database functions cover factorial, Fibonacci, power, integer summation, string reversal, and array summation. Each recursive function defines a base case and checks its input domain before making further calls.

`NUMERIC` is used for calculations that need more range than ordinary fixed-width integer arithmetic. Array summation returns `BIGINT` and rejects null arrays, invalid indices, and null elements.

PostgreSQL functions can be called directly from SQL queries, so recursive results can participate in inserts, reports, and larger query expressions.

### Run Tracking

The `recursion_run` table stores the operation name, input, result, status, error message, and timestamps. Its check constraints ensure that successful, rejected, and pending records have consistent combinations of values.

The index on operation and creation time supports operation-specific reporting over recent runs. It is useful when the table grows beyond the small demonstration dataset.

The `recursion_calculation_report` view groups runs by operation and status. It provides a compact view of execution history without duplicating the aggregation logic in every reporting query.

### Recursive CTEs

A recursive common table expression generates factorial call-frame states:

    WITH RECURSIVE factorial_frames(n, depth) AS (
        SELECT 4, 0
        UNION ALL
        SELECT n - 1, depth + 1
        FROM factorial_frames
        WHERE n > 1
    )
    SELECT n, depth
    FROM factorial_frames;

The anchor query defines the initial state. The recursive query generates smaller states until its termination condition is false. This is distinct from calling a recursive PL/pgSQL function: a recursive CTE describes a query result as an iterative sequence of relational states.

### Transactions and Failure Handling

The script runs within a transaction and records a rejected factorial input using a nested exception block. The block catches the error locally, preserving the outer transaction so the rejection can be stored as data.

A savepoint demonstrates how an optional calculation insert can be rolled back without rolling back earlier successful records.

The transaction ensures that the schema, sample data, and reporting objects are committed together. The initial drop statements make the script repeatable in a dedicated learning database, but they should not be used unmodified against a database containing valuable existing data.

## Cross-Language Comparison

| Concern | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Memoized Fibonacci | `lru_cache` | Closure and `Map` | `unordered_map` | `HashMap` | Direct recursive function |
| Large integer support | Arbitrary precision | Safe integer checks | Fixed-width integer | `BigInteger` | `NUMERIC` |
| Recursive state tracing | Dataclass records | Event processor | Printed call frames | Immutable records | Recursive CTE |
| Array reversal | New list | Copied array | Local vector copy | Copied list | Not included |
| Input validation | Explicit helper | Safe-integer checks | Exceptions and range checks | Domain validation | PL/pgSQL exceptions |
| Persistent run tracking | Not required | Not required | Not required | Not required | Relational table and view |

## Complexity and Practical Constraints

Let \(n\) denote the numeric input or the number of elements, depending on the operation.

| Algorithm | Time complexity | Recursive stack space |
|---|---:|---:|
| Factorial | \(O(n)\) | \(O(n)\) |
| Naive Fibonacci | \(O(2^n)\) | \(O(n)\) |
| Memoized Fibonacci | \(O(n)\) | \(O(n)\) |
| Power by squaring | \(O(\log n)\) multiplications | \(O(\log n)\) |
| Sum from zero through \(n\) | \(O(n)\) | \(O(n)\) |
| String reversal | Depends on copying strategy; up to \(O(n^2)\) | \(O(n)\) |
| Array summation | \(O(n)\) | \(O(n)\) |
| In-place array reversal | \(O(n)\) | \(O(n)\) |
| Binary search | \(O(\log n)\) | \(O(\log n)\) |

The costs above describe ordinary arithmetic operations. Arbitrary-precision arithmetic has a cost that grows with the number of digits, and immutable string concatenation may copy increasingly large intermediate strings.

Recursion is most appropriate when a problem naturally decomposes into smaller instances and the depth remains manageable. Iteration or an explicit stack is often preferable for very deep inputs. Memoization is valuable when recursive subproblems overlap, but it consumes additional memory and does not remove the call-stack limit.
