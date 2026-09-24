# Day 6 — Arrays, strings and basic problem solving

## Topic scope

Day 6 introduces two of the most frequently used data representations in beginner programming: arrays and strings. The day also develops basic problem-solving patterns that form the foundation for later data structures and algorithms.

The implementations cover:

- Array creation
- Array traversal
- Array indexing
- Array modification
- String traversal
- Basic string manipulation
- Linear searching
- Counting
- Maximum and minimum
- Array sum and average
- Array reversal
- String reversal
- Palindrome detection
- Duplicate detection
- Character frequency
- Second-largest value
- Even and odd counting
- Additional beginner problem-solving patterns
- Edge cases
- Validation
- Error handling
- Testing
- Time and space complexity
- A realistic C++ inventory-analysis case study

The three implementations use the same conceptual foundation while demonstrating language-specific techniques.

---

## Fundamental concept: arrays

An array stores multiple values under one variable name and provides access to individual elements through positions called indexes.

In Python, the most common array-like structure for this level is a `list`.

In JavaScript, the standard array is represented by `Array`.

In C++, the case study uses `std::vector`, which provides a dynamically sized contiguous sequence and is generally more convenient than a raw built-in array for this type of application.

Consider the logical sequence:

`10, 20, 30, 40, 50`

Its indexes are:

| Index | Value |
|---:|---:|
| 0 | 10 |
| 1 | 20 |
| 2 | 30 |
| 3 | 40 |
| 4 | 50 |

The important rule is that most programming languages use zero-based indexing. The first element is therefore at index `0`, not index `1`.

---

## Array creation

### Python

Python lists are created with square brackets.

Examples used in the Python implementation include:

`[]`

`[10, 20, 30, 40, 50]`

`[0] * 5`

A Python list can contain values of different types, although homogeneous collections are usually easier to reason about for algorithmic work.

### JavaScript

JavaScript arrays use square brackets.

Examples include:

`[]`

`[10, 20, 30, 40, 50]`

`new Array(5).fill(0)`

JavaScript arrays can also contain values of different types. For algorithmic problems, consistent element types generally make the logic clearer.

### C++

The C++ case study uses `std::vector<int>` for sequences of integers.

For example:

`vector<int> values = {10, 20, 30, 40, 50};`

A vector manages its own storage and can grow dynamically.

---

## Array indexing

Indexing retrieves one element from a known position.

For an array containing five values:

`values[0]`

returns the first element.

`values[4]`

returns the fifth element.

The final valid index is always:

`length - 1`

This relationship is fundamental because an array of length `n` has indexes from `0` through `n - 1`.

### Language differences

Python raises an `IndexError` when a list is accessed outside its valid range.

JavaScript returns `undefined` for an ordinary out-of-range array access.

C++ `vector::at()` performs bounds checking and can throw an exception, while the `[]` operator does not perform the same runtime bounds check. The C++ case study primarily uses known-valid indexes and explicit size checks.

These differences matter when writing defensive programs.

---

## Array traversal

Traversal means visiting the elements of an array one by one.

A basic traversal usually has the following structure:

1. Start at the first element.
2. Process the current element.
3. Move to the next element.
4. Stop after the final element.

The most direct form is an index-based loop.

If there are `n` elements and each element is processed once, the running time is generally `O(n)`.

The Python implementation demonstrates:

- direct value traversal
- `range(len(...))`
- `enumerate`

The JavaScript implementation demonstrates:

- traditional `for`
- `for...of`
- `forEach`

The C++ implementation demonstrates index-based traversal and range-based `for` loops.

---

## Array mutation

Mutation means changing an existing array.

For example, changing the value at index `2` transforms:

`[10, 20, 30, 40, 50]`

into:

`[10, 20, 35, 40, 50]`

Python lists, JavaScript arrays, and C++ vectors can all be modified.

A key distinction is that some operations create a new collection while others modify the existing collection.

This distinction becomes important when an algorithm must preserve the original input.

---

## Array slicing

Slicing extracts part of an array.

Python provides a dedicated slicing syntax such as:

`numbers[1:4]`

which selects indexes `1`, `2`, and `3`.

JavaScript commonly uses:

`numbers.slice(1, 4)`

which has similar end-exclusive behavior.

The C++ standard library does not provide Python-style slicing syntax for `vector`, so a programmer normally constructs another vector or uses iterator ranges.

Slicing is useful for creating smaller views or copies, but repeated slicing can allocate additional memory. For performance-sensitive algorithms, processing the original sequence with indexes or iterators can avoid unnecessary copies.

---

# Strings

A string is a sequence of characters.

Examples include:

`"Algorithm"`

`"Data Structures"`

`"problem solving"`

Strings support many of the same fundamental operations as arrays:

- indexing
- traversal
- searching
- counting
- comparison
- reversal
- extraction
- transformation

Strings are especially important because many programming problems are fundamentally sequence-processing problems.

---

## String indexing

For the string:

`Algorithm`

the first character is at index `0`.

The final character is at index `length - 1`.

Python also supports negative indexes, so `text[-1]` retrieves the final character.

JavaScript and C++ normally use the explicit final position, such as `text[text.length - 1]` or `text[text.size() - 1]`.

---

## String traversal

A string can be processed one character at a time.

For example, a character-counting algorithm visits every character and updates a frequency structure.

For a string such as:

`banana`

the frequency result is:

- `b` → 1
- `a` → 3
- `n` → 2

The Python implementation uses a dictionary.

The JavaScript implementation uses `Map`.

The C++ implementation uses `std::map`.

The underlying algorithmic idea is the same even though the data structures differ by language.

---

## String immutability

Python strings are immutable. JavaScript primitive strings are also immutable. C++ `std::string` is mutable.

This affects implementation details.

For Python and JavaScript, directly replacing an individual character inside a string is not performed in the same way as changing an array element. A new string normally has to be constructed.

For C++, characters in a `std::string` can be modified through valid indexes.

This distinction is important when considering memory allocation and algorithm design.

---

# Basic searching

The first search algorithm introduced in Day 6 is linear search.

Linear search examines elements sequentially until:

- the target is found, or
- all elements have been examined.

For:

`[5, 9, 2, 9, 7, 9]`

searching for `7` examines values from left to right until index `4`.

The implementations return `-1` when the target does not exist.

### Complexity

Worst-case time:

`O(n)`

Best-case time:

`O(1)`

Extra space:

`O(1)`

The best case occurs when the target is the first element.

The worst case occurs when the target is the final element or does not exist.

---

## Finding every occurrence

A single linear search stops at the first match.

Finding all positions requires the traversal to continue after a match.

For:

`[5, 9, 2, 9, 7, 9]`

the positions of `9` are:

`[1, 3, 5]`

This is still `O(n)` because the entire sequence is examined once.

---

# Basic counting

Counting is one of the most common beginner problem-solving patterns.

The general structure is:

1. Create a counter.
2. Traverse the input.
3. Test each element.
4. Increase the counter when the condition is true.
5. Return the counter.

For example, counting even numbers requires only one integer counter.

Counting occurrences of a particular value also requires only one counter.

Counting multiple distinct values requires a frequency structure such as a dictionary, map, or hash map.

---

# Maximum and minimum

Finding a maximum does not require sorting.

A one-pass algorithm is sufficient.

The basic approach is:

1. Assume the first element is the maximum.
2. Compare every remaining element against it.
3. Replace the maximum when a larger value is encountered.
4. Return the final value.

The minimum algorithm follows the same structure with the comparison reversed.

### Complexity

Time:

`O(n)`

Extra space:

`O(1)`

Sorting first would usually require more work and is unnecessary if the only requirement is the maximum or minimum.

This is an important problem-solving lesson:

> Do not perform a more expensive operation when the required answer can be obtained directly.

---

# Sum and average

The sum of an array is calculated by accumulating values.

For:

`[10, 20, 30]`

the sum is:

`60`

The average is:

`60 / 3 = 20`

The average therefore requires both:

- the total sum
- the number of elements

An empty array requires special handling because division by zero is not a valid average calculation.

The Python and JavaScript implementations explicitly reject empty inputs.

The C++ implementation throws an exception for the same condition.

---

# Reversing an array

There are several ways to reverse an array.

A simple method is to create a new reversed array.

A more memory-efficient method uses two pointers.

Suppose the array is:

`[1, 2, 3, 4, 5]`

The left pointer starts at `1`.

The right pointer starts at `5`.

Swap them:

`[5, 2, 3, 4, 1]`

Move both pointers inward:

`[5, 4, 3, 2, 1]`

The process stops when the pointers meet or cross.

### Complexity

Time:

`O(n)`

Extra space:

`O(1)`

The Python, JavaScript, and C++ implementations demonstrate this in-place technique.

---

# Reversing a string

A string can be reversed by traversing from the final character to the first.

For:

`hello`

the result is:

`olleh`

Because Python and JavaScript strings are immutable, their implementations construct a new string.

The C++ implementation also constructs a new string, which keeps the function simple and avoids modifying the caller's original value.

---

# Palindromes

A palindrome reads the same in both directions.

Examples:

- `racecar`
- `level`
- `madam`

The implementations also demonstrate normalized palindrome checking.

For example:

`A man, a plan, a canal: Panama`

is treated as:

`amanaplanacanalpanama`

after ignoring case and non-alphanumeric characters.

The two-pointer approach compares symmetrical characters.

For a normalized sequence:

`a b c b a`

the comparisons are:

- first vs last
- second vs second-last

If any pair differs, the string is not a palindrome.

### Complexity

Time:

`O(n)`

Space:

`O(n)` when a normalized copy is constructed.

A more advanced implementation can reduce auxiliary storage by scanning while skipping irrelevant characters, although the details become more complicated for Unicode text.

---

# Duplicate detection

Duplicate detection asks whether a value occurs more than once.

A naive solution compares every pair of values.

That approach can require:

`O(n²)`

time.

A set-based approach is more efficient for general unsorted input.

The algorithm is:

1. Create an empty set called `seen`.
2. Visit each value.
3. If the value is already in `seen`, it is a duplicate.
4. Otherwise insert it into `seen`.

Average set membership is approximately `O(1)` in hash-based implementations.

Therefore, duplicate detection is typically:

Time: `O(n)` average

Space: `O(n)`

The trade-off is additional memory in exchange for faster membership testing.

---

# Character frequency

Character frequency is a fundamental pattern that appears in many string problems.

The general structure is:

`character -> count`

For:

`banana`

the frequency mapping is:

- `b` → 1
- `a` → 3
- `n` → 2

This pattern is used by:

- duplicate-character detection
- anagram checking
- first non-repeating character problems
- text analysis
- simple parsing tasks

The exact data structure varies:

| Language | Structure used |
|---|---|
| Python | `dict` |
| JavaScript | `Map` |
| C++ | `std::map` |

---

# Second-largest value

The second-largest problem has an important ambiguity.

Consider:

`[10, 20, 20, 5]`

There are two possible interpretations:

1. The second element after sorting is `20`.
2. The second distinct-largest value is `10`.

The implementations use the second interpretation.

The algorithm maintains:

- `largest`
- `secondLargest`

When a new largest value is found, the old largest becomes the second-largest candidate.

Equal values do not replace the second-largest value.

For:

`[10, 20, 20, 5, 15]`

the result is:

`15`

For:

`[7, 7, 7]`

there is no second distinct-largest value, so the implementations report an error.

This is an example of why input assumptions must be made explicit.

---

# Even and odd elements

An integer is even when:

`number % 2 == 0`

Otherwise it is odd.

The remainder operator provides a direct test.

For:

`[1, 2, 3, 4, 5, 6]`

the result is:

- even = 3
- odd = 3

Negative integers also work correctly with this test.

---

# Additional problem-solving patterns

The implementations include several related problems because they reinforce the same fundamental techniques.

## Positive, negative and zero counting

Each value is classified into exactly one category:

- positive
- negative
- zero

This demonstrates mutually exclusive conditional branches.

---

## Removing duplicates while preserving order

For:

`[3, 1, 3, 2, 1]`

the result is:

`[3, 1, 2]`

The first occurrence is preserved.

A set tracks which values have already appeared while a result array stores the original order.

---

## Finding common values

Given two arrays, the goal is to identify values appearing in both.

A set representing one array makes membership testing efficient.

The C++ implementation uses a set for deterministic sorted output.

---

## Moving zeros to the end

Given:

`[0, 1, 0, 3, 12]`

the target is:

`[1, 3, 12, 0, 0]`

The non-zero values remain in their original relative order.

The implementation uses a write position.

This avoids repeatedly deleting and inserting elements, which could cause unnecessary shifting.

---

## Checking whether an array is sorted

An array is non-decreasing when:

`values[i] >= values[i - 1]`

for every valid `i`.

Only neighboring elements need to be compared.

Therefore the problem can be solved in one traversal.

---

# Missing value problem

The implementations include a simple missing-value problem.

If the complete range is:

`0, 1, 2, 3, 4`

and the input is:

`0, 1, 2, 4`

the missing value is `3`.

The sum of integers from `0` to `n` is:

`n(n + 1) / 2`

The expected sum minus the actual sum produces the missing value.

### Complexity

Time:

`O(n)`

Extra space:

`O(1)`

This technique depends on the problem guarantee that exactly one value is missing from the expected range.

---

# String problem-solving patterns

## Vowel and consonant counting

The implementation checks alphabetic characters and classifies them as vowels or consonants.

Non-alphabetic characters are ignored.

The classification is intentionally basic and English-oriented. Natural-language text processing becomes more complicated when Unicode alphabets and language-specific rules are introduced.

---

## First non-repeating character

The problem has two logical phases:

1. Count every character.
2. Traverse the original string again and return the first character whose count is one.

For:

`swiss`

the frequency counts identify:

- `s` → 3
- `w` → 1
- `i` → 1

The first character with frequency one is:

`w`

The second traversal is necessary to preserve the original order.

---

## Anagrams

Two strings are anagrams when they contain the same characters with the same frequencies, ignoring the specific ordering.

For example:

`listen`

and:

`silent`

have the same character counts.

The Python implementation uses `Counter`.

The JavaScript implementation builds frequency objects.

The C++ implementation provides character-frequency functionality that can support the same reasoning.

The concept is more important than the particular implementation:

`frequency(first) == frequency(second)`

---

## Reversing word order

Given:

`one two three`

the word-reversed result is:

`three two one`

This is different from reversing every character.

Character reversal:

`eerht owt eno`

Word reversal:

`three two one`

Understanding exactly what a problem asks is a major part of problem solving.

---

# C++ case study: inventory analysis system

The C++ implementation develops the Day 6 concepts into a small industry-style scenario.

The modeled system represents a business inventory containing products such as:

- keyboards
- mice
- monitors
- USB cables
- laptop stands

Each product has:

- product ID
- product name
- quantity
- unit price

The system can calculate:

- total inventory value
- maximum quantity
- minimum quantity
- average quantity
- low-stock products
- product lookup by ID
- duplicate product names

This makes the basic array and string techniques part of a larger program instead of isolated exercises.

---

# C++ architecture

The implementation has two major levels.

## `InventoryItem`

`InventoryItem` represents one product.

It validates:

- positive product ID
- non-empty product name
- non-negative quantity
- non-negative price

It provides methods for:

- retrieving the ID
- retrieving the product name
- retrieving quantity
- retrieving price
- calculating inventory value
- checking low-stock status

The inventory value is:

`quantity × unit price`

---

## `InventoryAnalyzer`

`InventoryAnalyzer` owns a collection of inventory items.

Its responsibilities include:

- adding items
- rejecting duplicate IDs
- searching by ID
- extracting quantities
- calculating aggregate values
- finding maximum quantity
- finding minimum quantity
- calculating average quantity
- identifying low-stock products
- identifying duplicate product names
- generating a report

This separates product-level behavior from collection-level analysis.

---

# Why `vector` is used

`std::vector` is appropriate for this educational case study because:

- the number of items can grow
- elements are stored contiguously
- indexed access is efficient
- range-based traversal is convenient
- it integrates well with the standard library

For a very large production inventory system, a database or indexed in-memory structure would normally be more appropriate.

The example intentionally stays within the standard library so the algorithmic ideas remain visible.

---

# Searching the inventory

The product lookup method uses a linear search over inventory items.

The algorithm checks:

`item.getId() == productId`

for every product until a match is found.

### Complexity

If there are `n` products:

Worst-case lookup:

`O(n)`

This is acceptable for a small educational collection.

For a much larger in-memory system, an indexed structure such as:

`unordered_map<int, InventoryItem>`

could provide average constant-time lookup by product ID.

The trade-off is that a hash-based index uses additional memory and introduces a different data-management design.

---

# Validation and failure conditions

Input validation is important even for simple programs.

The C++ case study rejects:

- product IDs less than or equal to zero
- empty product names
- negative quantities
- negative prices
- duplicate product IDs
- negative low-stock thresholds
- empty arrays when maximum/minimum/average calculations require data
- insufficient distinct values for second-largest calculation

These checks prevent invalid state from silently entering the system.

---

# Exception handling

The C++ program uses exceptions for invalid operations.

For example:

`throw invalid_argument(...)`

signals that the supplied input violates a function's requirements.

The main function catches `std::exception` so that an unexpected failure produces an understandable error message rather than terminating without context.

Python uses `ValueError` for similar validation failures.

JavaScript uses `Error`.

The mechanism differs, but the design principle is the same:

> Detect invalid input close to the operation that cannot correctly process it.

---

# Edge cases

Beginner algorithms often fail not on ordinary input but on boundary conditions.

Important Day 6 edge cases include:

### Empty array

Examples:

`[]`

Problems affected:

- maximum
- minimum
- average
- second-largest

These operations require at least some data.

### One element

`[42]`

The maximum and minimum are well-defined, but a second-largest distinct value does not exist.

### All equal

`[7, 7, 7, 7]`

There is only one distinct value.

A second distinct-largest value therefore does not exist.

### Negative values

`[-10, -5, -20]`

The maximum is `-5`, not `0`.

This is why initializing a maximum to zero is a common mistake.

The correct approach is to initialize from the first actual element or use an appropriate optional state.

### Zeros

`[0, 0, 0]`

Zeros must not accidentally be treated as missing or false values.

### Empty string

`""`

An empty string is commonly considered a palindrome because there are no conflicting character pairs.

The exact definition can depend on the problem statement.

---

# Common mistakes

## Starting maximum at zero

Incorrect logic:

`maximum = 0`

This fails for arrays containing only negative values.

Better:

`maximum = first element`

---

## Starting minimum at zero

The same problem occurs for minimum calculations.

For:

`[-10, -5, -20]`

zero is not an element and therefore cannot be assumed to be the minimum.

---

## Confusing index with value

Given:

`[10, 20, 30]`

index `1` is not the same thing as value `1`.

Index `1` refers to value `20`.

---

## Using the wrong stopping condition

Loops must stop at the correct boundary.

For an array of length `n`, valid indexes are:

`0` through `n - 1`

Accessing `n` is outside the valid range.

---

## Forgetting empty input

Functions that require at least one value should define what happens when the input is empty.

Silently producing an incorrect result is worse than explicitly rejecting invalid input.

---

## Treating duplicates incorrectly

The phrase "second largest" can be ambiguous.

For:

`[10, 20, 20, 5]`

the second largest distinct value is `10`.

A problem statement should clarify whether duplicate values count separately.

---

## Reversing the wrong thing

Reversing characters and reversing words are different operations.

`one two three`

character reversal:

`eerht owt eno`

word reversal:

`three two one`

---

## Removing elements repeatedly

Repeated deletion from the middle of an array can cause many elements to shift.

The zero-moving algorithm demonstrates a more efficient write-position technique.

---

## Sorting when sorting is unnecessary

If the task is simply to find a maximum, scanning once is enough.

Sorting introduces additional work.

This is an early example of selecting an algorithm based on the actual requirement rather than automatically using a familiar operation.

---

# Complexity analysis

Complexity describes how an algorithm's resource requirements grow as input size increases.

## Common Day 6 operations

| Operation | Typical time | Extra space |
|---|---:|---:|
| Traverse array | `O(n)` | `O(1)` |
| Linear search | `O(n)` | `O(1)` |
| Find maximum | `O(n)` | `O(1)` |
| Find minimum | `O(n)` | `O(1)` |
| Calculate sum | `O(n)` | `O(1)` |
| Count target | `O(n)` | `O(1)` |
| Reverse with two pointers | `O(n)` | `O(1)` |
| Character frequency | `O(n)` | `O(k)` |
| Duplicate detection with set | `O(n)` average | `O(n)` |
| Naive duplicate comparison | `O(n²)` | `O(1)` |
| Palindrome checking after normalization | `O(n)` | `O(n)` |

Here `n` represents input size.

For character-frequency problems, `k` represents the number of distinct characters.

---

# Why `O(n)` is important

A linear algorithm processes each input element a bounded number of times.

If the input grows from:

`100` elements to `1,000` elements,

the amount of work generally grows by roughly a factor of ten.

This is usually preferable to an `O(n²)` approach, where the work can grow by approximately a factor of one hundred for the same tenfold increase.

The difference becomes increasingly important as datasets grow.

---

# Why `O(n²)` appears in beginner problems

A common pattern is nested traversal.

For example, comparing every pair of elements can produce:

`n × n`

comparisons.

This results in:

`O(n²)`

time.

Such an approach can still be completely acceptable for very small inputs.

The important skill is recognizing its cost and understanding when a different data structure can reduce the work.

---

# Sets and hash-based lookup

Duplicate detection is a useful example.

Without an auxiliary structure, checking whether each element has appeared before may require scanning previously processed elements.

A set provides membership testing.

The general pattern is:

`if value already exists: duplicate`

otherwise:

`record value`

This transforms many repeated-search problems into a single traversal with additional memory.

The trade-off is:

- faster average lookup
- additional memory
- dependence on hash-table behavior

---

# Python implementation

The Python implementation is designed as a complete study program rather than a collection of isolated snippets.

It demonstrates:

- Python lists
- list indexing
- slicing
- `enumerate`
- dictionary-based frequency counting
- sets for duplicate detection
- functions
- type annotations
- tuples
- optional return values
- exceptions
- assertions
- manual algorithms
- standard-library `Counter`

The implementation deliberately avoids replacing the learning objective with one-line built-in solutions everywhere.

For example, maximum and minimum are implemented manually so the underlying traversal and comparison logic is visible.

The program also contains a test suite so the learner can see how algorithmic functions can be validated.

---

# JavaScript implementation

The JavaScript implementation complements the Python version by demonstrating how the same algorithmic ideas appear in JavaScript.

Important JavaScript-specific features include:

- `Array`
- `Map`
- `Set`
- `for`
- `for...of`
- `forEach`
- destructuring assignment
- `slice`
- string methods
- `const` and `let`
- exceptions
- Node.js console output

The JavaScript implementation also demonstrates an important language distinction: an out-of-range ordinary array access produces `undefined`, unlike Python's `IndexError`.

The examples are executable in a modern Node.js environment.

---

# C++ implementation

The C++ program turns the Day 6 concepts into an inventory-analysis case study.

It demonstrates:

- `std::vector`
- `std::string`
- `std::map`
- `std::set`
- `std::unordered_set`
- `std::optional`
- classes
- constructors
- encapsulation
- validation
- exceptions
- references
- range-based loops
- formatted output
- input parsing
- modular functions
- assertions through explicit test conditions

The program is intended for C++17 or later.

The inventory model makes the basic algorithms more concrete.

Instead of merely finding the maximum in an arbitrary array, the system finds the maximum product quantity.

Instead of merely searching a number, it searches an inventory product ID.

Instead of merely calculating a sum, it calculates the total inventory value.

This illustrates how fundamental algorithms become components of larger software systems.

---

# Python, JavaScript and C++ comparison

| Concept | Python | JavaScript | C++ |
|---|---|---|---|
| Dynamic sequence | `list` | `Array` | `vector` |
| Frequency structure | `dict` | `Map` | `map` |
| Unique-value structure | `set` | `Set` | `set` / `unordered_set` |
| String | `str` | primitive string | `std::string` |
| Length | `len(values)` | `values.length` | `values.size()` |
| Exception type | `ValueError` | `Error` | `std::invalid_argument` |
| Optional result | `Optional` | `null` | `std::optional` |
| Common loop | `for` | `for` | `for` |
| Direct sequence loop | `for value in values` | `for...of` | range-based `for` |

The algorithmic ideas are transferable even when the syntax changes.

Learning the concept separately from the syntax is an important part of developing problem-solving ability.

---

# Practical applications

The Day 6 techniques occur throughout software development.

## Arrays and vectors

Common applications include:

- product lists
- transaction records
- sensor readings
- student marks
- financial time series
- search results
- inventory records
- configuration values

## Strings

Common applications include:

- names
- addresses
- usernames
- search queries
- log messages
- file paths
- identifiers
- natural-language text

## Searching

Search algorithms appear in:

- product lookup
- user lookup
- validation
- configuration lookup
- record retrieval
- filtering

## Counting

Counting appears in:

- frequency analysis
- statistics
- voting or survey aggregation
- text processing
- event monitoring
- inventory quantities
- log analysis

## Duplicate detection

Duplicate detection appears in:

- data cleaning
- validation
- transaction processing
- record deduplication
- identifier checking

---

# Security considerations

The algorithms in this lesson are simple, but input handling still matters.

## Validate external input

Never assume that user-provided data is valid.

Check:

- type
- range
- required fields
- empty values
- duplicate identifiers
- invalid numeric values

## Avoid accidental resource consumption

Very large inputs can expose inefficient algorithms.

An `O(n²)` algorithm that is harmless for 100 elements can become expensive for millions of elements.

## Be careful with text normalization

Simple ASCII-oriented character checks do not fully represent international text.

Production applications may need Unicode-aware handling for:

- accented characters
- non-Latin scripts
- case conversion
- grapheme clusters
- locale-specific rules

## Do not confuse validation with security

Checking whether a string contains a particular character is not sufficient to make that string safe for use in another system.

Production software must also consider the context in which data is used, such as:

- SQL queries
- HTML
- shell commands
- file paths
- network protocols

Those concerns are outside the basic scope of Day 6 but become important when these simple algorithms are integrated into larger applications.

---

# Performance considerations

The most important performance lesson in Day 6 is to understand the difference between:

`O(n)`

and:

`O(n²)`

A second important lesson is the trade-off between time and memory.

For example, duplicate detection can be implemented without extra storage, but repeated comparisons may produce `O(n²)` time.

Using a set can reduce expected running time to approximately `O(n)` while requiring `O(n)` additional memory.

The correct choice depends on:

- input size
- memory limits
- required ordering
- expected number of queries
- frequency of updates
- performance requirements

---

# Testing

The three implementations include tests or validation checks.

Testing is important because simple algorithms still contain boundary conditions.

Representative test categories include:

- normal input
- empty input
- one-element input
- all-equal values
- negative values
- zeros
- missing search targets
- duplicate values
- no duplicate values
- palindrome strings
- non-palindrome strings
- insufficient values for second-largest calculations

A good beginner habit is to test both the expected successful path and the cases where the input violates the function's assumptions.

---

# Phase review: 15 mixed beginner problems

The implementations contain 15 mixed problems corresponding to the Day 6 practice requirements.

1. Calculate array sum.
2. Find maximum.
3. Find minimum.
4. Count occurrences of a target.
5. Reverse an array.
6. Reverse a string.
7. Check whether a string is a palindrome.
8. Find duplicate values.
9. Count characters.
10. Find the second distinct-largest value.
11. Count even and odd elements.
12. Find the first non-repeating character.
13. Check whether two strings are anagrams.
14. Move zeros to the end.
15. Find a missing value from a complete integer range.

The purpose of the mixed set is to require switching between different patterns instead of repeatedly applying the same algorithm.

---

# Problem-solving method used throughout Day 6

A reliable approach to these beginner problems is:

## Understand the input

Determine:

- What data is provided?
- Is it an array, string, or both?
- Can it be empty?
- Can values repeat?
- Can values be negative?
- Are there guaranteed constraints?

## Define the output

Determine exactly what must be returned.

Examples:

- a value
- an index
- a count
- a Boolean
- a new array
- a string
- an exception for invalid input

## Work through a small example

For example:

`[4, 2, 7, 2]`

For counting `2`:

- inspect `4` → no
- inspect `2` → count becomes 1
- inspect `7` → no
- inspect `2` → count becomes 2

Result:

`2`

## Identify the simplest correct pattern

Typical Day 6 patterns include:

- single traversal
- accumulator
- counter
- two pointers
- set for membership
- map/dictionary for frequency
- conditional classification

## Consider edge cases

Ask:

- What if the array is empty?
- What if there is one element?
- What if every value is equal?
- What if there are negative numbers?
- What if the target does not exist?
- What if there is no valid second-largest value?

## Estimate complexity

Before optimizing, determine whether the solution is:

- `O(1)`
- `O(n)`
- `O(n log n)`
- `O(n²)`

Also consider extra memory.

---

# Important distinctions

## Array traversal vs searching

Traversal visits every element when required.

Searching may stop early after finding a target.

A linear search can therefore be faster than a full traversal on some inputs, even though its worst-case complexity remains `O(n)`.

## Counting vs frequency mapping

Counting one specific value needs one counter.

Counting every distinct value requires a frequency structure.

## Reversal vs sorting

Reversal changes order deterministically:

`[1, 2, 3]` → `[3, 2, 1]`

Sorting orders values according to a comparison rule:

`[3, 1, 2]` → `[1, 2, 3]`

They solve different problems.

## Maximum vs second-largest

Maximum requires one best value.

Second-largest distinct requires maintaining two distinct candidates.

## Duplicate detection vs frequency counting

Duplicate detection only needs to know whether a value has appeared.

Frequency counting also needs to know how many times it appeared.

---

# Limitations of the implementations

These programs intentionally focus on foundational algorithms rather than production-scale data systems.

The examples do not implement:

- database persistence
- distributed processing
- concurrent data access
- Unicode grapheme segmentation
- external APIs
- large-scale indexing
- database-backed search
- authentication
- authorization
- persistent inventory storage

The C++ inventory system is an educational model. A real inventory platform would normally include persistent storage, transaction management, concurrency control, auditing, authorization, validation at multiple boundaries, and database indexes.

The purpose of the case study is to demonstrate how basic array, string, search, and counting algorithms fit into a larger program.

---

# Best practices established by Day 6

- Initialize maximum and minimum from actual input values.
- Validate assumptions before performing calculations.
- Use a single traversal when a single traversal is sufficient.
- Use sets for efficient membership checks when extra memory is acceptable.
- Use frequency maps when counts for many distinct values are required.
- Use two pointers for many symmetric sequence problems.
- Preserve input when the problem requires a non-destructive solution.
- Avoid unnecessary sorting.
- Test empty and boundary inputs.
- Distinguish values from indexes.
- Make ambiguous requirements explicit.
- Analyze both time and extra-space complexity.
- Use meaningful names.
- Keep functions focused on one logical task.
- Reject invalid states rather than silently producing misleading results.
- Choose data structures based on the operations the program performs most frequently.

---

# File relationship

The three source files approach the same Day 6 subject from different perspectives.

The Python implementation emphasizes algorithmic clarity, compact experimentation, type annotations, dictionaries, sets, exceptions, and assertions.

The JavaScript implementation demonstrates the same problem-solving foundations using JavaScript arrays, strings, `Map`, `Set`, loops, destructuring, and Node.js execution.

The C++ implementation places the concepts inside an inventory-analysis system. It demonstrates how arrays, strings, searching, counting, validation, and aggregation become components of a larger object-oriented program.

Together, the implementations show that arrays, strings, traversal, searching, and counting are not isolated beginner topics. They are recurring building blocks for more advanced algorithms and software systems.
