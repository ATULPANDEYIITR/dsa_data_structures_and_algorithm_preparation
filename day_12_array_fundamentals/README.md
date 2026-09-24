# Day 12 — Array Fundamentals

## Topic overview

Arrays are one of the fundamental data structures used in programming and algorithm design. An array stores multiple values under one logical structure and provides access to individual elements through indexes.

Day 12 focuses on the operations that form the foundation of many later data-structure and algorithm problems:

- Indexing
- Traversal
- Updating
- Searching
- Minimum and maximum
- Frequency counting
- Finding the maximum element
- Finding the minimum element
- Finding the second-largest distinct element
- Reversing an array
- Rotating an array
- Removing duplicates
- Counting positive and negative values
- Finding missing values

The implementations deliberately move from direct array operations to techniques such as two pointers, prefix sums, XOR-based missing-value detection, binary search, frequency tables, and in-place transformations.

---

## 1. What is an array?

An array is a collection of elements organized under one data structure. Each element occupies a logical position identified by an index.

For example:

`[10, 20, 30, 40, 50]`

The positions are:

| Index | Value |
|---:|---:|
| 0 | 10 |
| 1 | 20 |
| 2 | 30 |
| 3 | 40 |
| 4 | 50 |

The first element has index `0`, not `1`.

This is called **zero-based indexing**.

If an array contains `n` elements, its valid indexes are:

`0` through `n - 1`

An attempt to access index `n` is outside the valid range.

---

## 2. Array fundamentals

### Indexing

Indexing means accessing one element using its position.

For an array `A`:

`A[0]` refers to the first element.

`A[1]` refers to the second element.

`A[n - 1]` refers to the last element.

Index access is normally an O(1) operation because the address of an element can be calculated directly from the array's starting location and the element position.

This is one of the major advantages of arrays.

### Traversal

Traversal means visiting array elements one by one.

A basic traversal looks conceptually like:

`for each element in the array`

A traversal of `n` elements takes O(n) time.

Traversal is the foundation for many array algorithms, including:

- Finding minimum
- Finding maximum
- Searching
- Counting values
- Calculating sums
- Building frequency tables
- Applying transformations

### Updating

An element can be changed by accessing its index.

For example:

`A[3] = 100`

changes the value at index `3`.

Updating one known index is O(1).

Updating every element requires traversal and therefore takes O(n).

### Searching

Searching determines whether a target value exists and, depending on the algorithm, can return its location.

The simplest approach is **linear search**.

Linear search checks elements sequentially until:

1. the target is found, or
2. the array ends.

Worst-case time complexity is O(n).

If the target is the first element, the best case is O(1).

---

## 3. Python implementation

The Python implementation uses the built-in `list` type as the primary array-like structure.

Python lists are dynamic arrays. They support indexed access, iteration, insertion, deletion, slicing, and many built-in operations.

The Python file demonstrates:

- Creating arrays with lists
- Positive indexing
- Negative indexing
- Slicing
- Forward traversal
- Reverse traversal
- `enumerate`
- Updating values
- Linear search
- Minimum and maximum
- Frequency counting
- Second-largest distinct value
- In-place reversal
- Array rotation
- Duplicate removal
- Sign counting
- Missing-value detection
- Binary search
- Prefix sums
- Two-pointer processing
- Validation
- Edge cases
- Automated tests
- Complexity analysis

### Python indexing

For:

`values = [15, 25, 35, 45, 55]`

the expression `values[0]` returns `15`.

Python also supports negative indexes:

- `values[-1]` is the last element.
- `values[-2]` is the second-last element.

This differs from languages such as C++ and JavaScript, where negative values supplied to the conventional bracket operator do not mean "count from the end."

### Python traversal

The implementation demonstrates three useful forms.

A direct value traversal:

`for value in values`

An index-based traversal:

`for index in range(len(values))`

An indexed traversal using `enumerate`:

`for index, value in enumerate(values)`

`enumerate` is often preferable when both the index and value are required.

### Updating

The Python implementation first changes one element directly and then demonstrates traversal-based modification.

A single assignment such as:

`values[2] = 999`

is O(1).

Changing every element requires O(n) work.

### Linear search

The `linear_search` function returns the first matching index and returns `-1` when the target is absent.

Its complexity is:

- Best case: O(1)
- Worst case: O(n)
- Extra space: O(1)

The implementation is useful because it exposes the actual mechanism instead of hiding the operation behind a built-in method.

---

## 4. Minimum and maximum

Finding the minimum or maximum element is a classic array traversal problem.

A robust algorithm initializes the candidate using the first element rather than assuming a particular value such as zero.

For example, an array containing only negative numbers must still work correctly:

`[-10, -3, -25, -7]`

The minimum is `-25`.

Initializing the minimum to `0` would be incorrect for this input because zero is not part of the array.

The Python implementation therefore uses the first element as the initial candidate.

Both minimum and maximum can be found in:

- Time: O(n)
- Extra space: O(1)

Python also provides `min()` and `max()`, but the manual implementations demonstrate the underlying algorithm.

---

## 5. Frequency counting

Frequency counting determines how many times each value occurs.

For:

`[2, 5, 2, 8, 5, 2, 9, 8, 8]`

the frequency table is conceptually:

| Value | Frequency |
|---:|---:|
| 2 | 3 |
| 5 | 2 |
| 8 | 3 |
| 9 | 1 |

A frequency table is usually implemented with a hash-based structure.

In Python, the implementation demonstrates both:

- A normal dictionary
- `collections.Counter`

The manual implementation uses:

`frequencies[value] = frequencies.get(value, 0) + 1`

This illustrates an important pattern:

1. Check the current count.
2. Use zero if the value has not appeared.
3. Increment the count.

Average time complexity is O(n).

If there are `k` distinct values, the frequency structure requires approximately O(k) additional space.

---

## 6. Second-largest distinct element

Finding the second-largest value contains an important distinction.

Consider:

`[30, 30, 20, 10]`

The second-largest **distinct** value is `20`.

It is not `30`, because the two occurrences of `30` represent the same value.

The implementation maintains two candidates:

- Largest
- Second-largest distinct

The algorithm processes the array once.

This gives:

- Time: O(n)
- Extra space: O(1)

A sorting-based solution could also find the answer, but sorting would generally cost O(n log n), making the one-pass approach preferable when only the second-largest value is required.

Important edge cases include:

- Empty array
- One-element array
- All values equal
- Negative values
- Repeated maximum values

---

## 7. Reversing an array

Reversal changes:

`[1, 2, 3, 4, 5]`

into:

`[5, 4, 3, 2, 1]`

The Python and JavaScript implementations demonstrate a **two-pointer** solution.

Two indexes are maintained:

- `left` starts at the first element.
- `right` starts at the last element.

The elements are swapped and the pointers move toward the center.

The process stops when the pointers meet or cross.

Complexity:

- Time: O(n)
- Extra space: O(1)

This is an in-place algorithm because it does not require another array proportional to the input size.

---

## 8. Array rotation

Rotation shifts elements around the array boundary.

A right rotation of:

`[1, 2, 3, 4, 5]`

by two positions produces:

`[4, 5, 1, 2, 3]`

A common edge case is a rotation amount larger than the array length.

For an array of length `5`, rotating by `7` is equivalent to rotating by:

`7 mod 5 = 2`

Therefore the rotation count is normalized using modulo arithmetic.

The implementations demonstrate two approaches.

### Copy-based rotation

The Python and JavaScript versions can construct a new array using slices.

This is simple but requires O(n) extra space.

### Reversal-based rotation

The in-place implementation uses three reversals:

1. Reverse the entire array.
2. Reverse the first `k` elements.
3. Reverse the remaining elements.

For:

`[1, 2, 3, 4, 5]`

with `k = 2`:

After reversing everything:

`[5, 4, 3, 2, 1]`

After reversing the first two:

`[4, 5, 3, 2, 1]`

After reversing the remaining portion:

`[4, 5, 1, 2, 3]`

Complexity:

- Time: O(n)
- Extra space: O(1)

This demonstrates the difference between a convenient implementation and a memory-efficient implementation.

---

## 9. Removing duplicates

Duplicate removal has multiple possible interpretations.

One common requirement is:

> Remove repeated values while preserving the order of their first occurrence.

For:

`[4, 2, 4, 7, 2, 9, 7, 1]`

the result is:

`[4, 2, 7, 9, 1]`

A hash-based set is useful because membership checking is O(1) on average.

The algorithm maintains:

- A set of values already seen.
- A result array containing the first occurrence of each value.

Average complexity:

- Time: O(n)
- Extra space: O(k)

where `k` is the number of distinct values.

The C++ case study uses `unordered_set`, while the JavaScript implementation uses `Set`.

---

## 10. Removing duplicates from a sorted array

A different problem occurs when the array is already sorted.

For example:

`[1, 1, 2, 2, 2, 3, 4, 4]`

Because equal values are adjacent, a two-pointer or read/write-index technique can compact the array.

The general idea is:

- One position reads elements.
- Another position writes the next distinct value.
- The write position advances only when a new value is found.

This can be performed in O(n) time and O(1) extra space when the array itself may be modified.

This is different from the hash-set approach because the sorted order provides useful information that eliminates the need for a separate set.

---

## 11. Counting positive, negative, and zero values

A single traversal can classify every value.

For each element:

- If `value > 0`, increment the positive count.
- If `value < 0`, increment the negative count.
- Otherwise, increment the zero count.

The three counts together equal the array length.

For:

`[-5, 0, 8, -2, 7, 0, -10, 4]`

the result is:

- Positive: 3
- Negative: 3
- Zero: 2

Complexity:

- Time: O(n)
- Extra space: O(1)

The same pattern can be adapted to many classifications, such as:

- Even and odd
- Above and below a threshold
- Valid and invalid
- Pass and fail
- In-range and out-of-range

---

## 12. Finding missing values

"Find missing values" can describe several different problems.

### Finding all missing values in a known range

Suppose the expected range is:

`1..9`

and the input is:

`[1, 2, 4, 6, 7, 9]`

The missing values are:

`[3, 5, 8]`

A set-based solution stores all present values and then checks every expected number.

If the input contains `n` values and the expected range contains `r` values, the process takes approximately:

O(n + r)

space depends on the number of stored values.

### Finding one missing value from 0 through n

A more specialized problem provides `n` values selected from:

`0, 1, 2, ..., n`

with exactly one missing.

For example:

`[3, 0, 1]`

is missing `2`.

The implementation uses XOR.

Important XOR properties are:

`x ^ x = 0`

and:

`x ^ 0 = x`

When all expected values are XORed with all observed values, matching values cancel and only the missing value remains.

Complexity:

- Time: O(n)
- Extra space: O(1)

This method is appropriate only when the stated assumptions hold.

It should not be used for an arbitrary missing-values problem containing multiple missing values, duplicates, or values outside the expected domain.

---

## 13. Binary search

Linear search does not require sorted data.

Binary search does.

For a sorted array:

`[3, 8, 12, 19, 24, 31, 45, 50]`

binary search repeatedly examines the middle element and eliminates approximately half of the remaining search space.

Its complexity is:

- Time: O(log n)
- Extra space: O(1) for an iterative implementation

The key trade-off is that binary search requires sorted input.

Using binary search on an unsorted array without first establishing the ordering condition can produce an incorrect result.

If the data changes frequently and remains unsorted, repeatedly sorting it merely to perform occasional searches may eliminate the practical benefit of binary search.

---

## 14. Prefix sums

A prefix sum array stores cumulative totals.

For:

`[5, 2, 7, 3, 10]`

the prefix sums are:

`[5, 7, 14, 17, 27]`

The value at index `i` represents the sum from index `0` through `i`.

Once prefix sums have been constructed, a range sum can be calculated quickly.

For indexes `left` through `right`:

`prefix[right] - prefix[left - 1]`

when `left` is not zero.

If `left` is zero, the answer is simply `prefix[right]`.

This changes repeated range-sum queries from O(n) each to O(1) after O(n) preprocessing.

The trade-off is O(n) additional memory.

Prefix sums are important because they introduce a broader algorithmic idea:

> Precompute information once when many later queries can benefit from it.

---

## 15. Two-pointer technique

Two pointers use two positions to process an array without repeatedly scanning the same elements.

The C++ and Python implementations demonstrate two-pointer searching on a sorted array.

For:

`[1, 3, 4, 6, 8, 10, 13]`

and target `14`:

- Start at the smallest value.
- Start another pointer at the largest value.
- Calculate their sum.
- Move the left pointer when the sum is too small.
- Move the right pointer when the sum is too large.

This works because the array is sorted.

Complexity:

- Time: O(n)
- Extra space: O(1)

Without sorted data, this exact two-pointer strategy is not generally valid.

---

## 16. Combined array analysis

Several independent statistics can sometimes be calculated in one traversal.

The Python and JavaScript implementations include a combined analysis that calculates:

- Length
- Minimum
- Maximum
- Positive count
- Negative count
- Zero count
- Frequency table

Instead of making a separate O(n) traversal for every statistic, related calculations can be performed during one pass.

This does not change the asymptotic complexity when the number of statistics is constant, but it can reduce traversal overhead and improve implementation efficiency.

The frequency table still requires additional memory proportional to the number of distinct values.

---

## 17. JavaScript implementation

The JavaScript implementation focuses on practical array behavior in modern JavaScript.

It demonstrates:

- Array creation
- Zero-based indexing
- `length`
- `at()`
- `slice()`
- `for`
- `for...of`
- `forEach`
- Direct updates
- `map`
- Linear search
- `includes`
- `indexOf`
- `Map`
- `Set`
- In-place operations
- Validation
- Binary search
- Prefix sums
- Two pointers

### JavaScript arrays

JavaScript arrays are dynamic objects optimized by JavaScript engines for common array-like operations.

They are flexible and can contain different types, although using a consistent element type is generally preferable for algorithmic and performance-sensitive code.

The implementation uses numeric arrays consistently because the subject is numerical array processing.

### `at()`

Modern JavaScript supports:

`array.at(-1)`

for retrieving the final element.

This provides negative-position access without changing the meaning of the normal bracket operator.

### `Map` for frequency counting

The JavaScript implementation uses `Map` rather than relying exclusively on ordinary objects.

A `Map` explicitly represents key-value associations and supports arbitrary key types.

The frequency pattern is:

`frequencies.set(value, (frequencies.get(value) ?? 0) + 1)`

This is closely related to the dictionary approach used in Python.

### `Set` for uniqueness

JavaScript's `Set` stores unique values.

It is therefore suitable for:

- Duplicate detection
- Duplicate removal
- Membership tests
- Finding missing values within a known range

The expression:

`[...new Set(values)]`

creates an array containing unique values while preserving insertion order.

---

## 18. C++ case study: Inventory Analytics Engine

The C++ implementation models a simplified inventory analytics system.

Each integer represents the quantity associated with a product slot.

For example:

`[42, 18, 75, 30, 18, 55, 90, 12, 75, 30]`

could represent quantities recorded for ten inventory entries.

The system is implemented through the `InventoryAnalytics` class.

The class demonstrates how basic array algorithms can become components of a larger software system.

### System responsibilities

The class provides:

- Safe indexed access
- Validated updates
- Traversal
- Linear search
- Minimum quantity
- Maximum quantity
- Second-largest distinct quantity
- Frequency counting
- Reversal
- Rotation
- Duplicate removal
- Sign analysis
- Binary search
- Prefix sums

A separate function handles the specialized single-missing-value XOR algorithm.

---

## 19. C++ data structure choice

The core storage structure is:

`std::vector<int>`

A vector is the standard C++ dynamic-array container.

It provides:

- Contiguous storage
- O(1) random access
- Dynamic size
- Iteration support
- Compatibility with standard algorithms

The vector is appropriate for this case because inventory quantities are naturally represented as a sequence of numeric values.

The program deliberately uses standard-library structures rather than external dependencies.

---

## 20. C++ validation

The constructor validates inventory quantities and rejects negative values.

This represents an important production principle:

> Validate data at system boundaries.

If invalid data is allowed to enter the internal representation, every later method must account for that invalid state.

Centralizing validation simplifies the rest of the class.

The implementation also validates indexes before accessing the vector.

An invalid index produces an `std::out_of_range` exception.

---

## 21. C++ `optional`

Operations such as minimum, maximum, second-largest value, and search can fail to produce a meaningful result.

An empty array has no minimum.

An array containing only one distinct value has no second-largest distinct value.

A search may not find its target.

The C++ implementation uses `std::optional` to represent this possibility explicitly.

For example, a search returns either:

- an index, or
- `std::nullopt`

This is safer than returning a special numeric value that could accidentally be confused with a legitimate index.

---

## 22. C++ exception handling

The case study demonstrates different failure categories.

### `std::out_of_range`

Used when an index or range is outside valid bounds.

### `std::invalid_argument`

Used when input violates a method's value requirements, such as negative inventory quantities.

### `std::logic_error`

Used when an operation's precondition has not been satisfied.

The binary-search method checks whether the data is sorted before executing binary search.

If the data is unsorted, it raises a logic error instead of silently returning an unreliable result.

---

## 23. C++ frequency counting

The case study uses:

`std::unordered_map<int, size_t>`

for frequency counting.

Average lookup and insertion are O(1).

If there are `k` distinct quantities, the frequency table requires approximately O(k) additional space.

The program does not rely on the order of an `unordered_map` during output because an unordered map does not guarantee sorted iteration order.

If deterministic sorted output were required, `std::map` could be used instead, with O(log k) lookup and insertion.

---

## 24. C++ duplicate removal

The C++ case study uses:

`std::unordered_set<int>`

to track previously observed values.

The algorithm preserves the first occurrence.

For:

`[1, 2, 1, 3, 2]`

the resulting sequence is:

`[1, 2, 3]`

The average complexity is O(n).

This technique trades additional memory for faster membership checking.

---

## 25. C++ binary search

The C++ binary-search implementation first verifies that the vector is sorted.

The search interval uses a half-open representation:

`[left, right)`

This convention can simplify boundary management.

The midpoint is calculated as:

`left + (right - left) / 2`

rather than:

`(left + right) / 2`

The first form avoids unnecessary integer overflow risks in fixed-width integer environments when index values are very large.

Binary search runs in O(log n) time.

---

## 26. C++ rotation

The C++ case study performs right rotation using the reversal technique.

This is useful because the operation can be completed:

- In O(n) time
- With O(1) additional space

The implementation also normalizes large and negative rotation counts.

For an array of length `n`, the effective rotation is based on:

`k mod n`

A negative result from C++'s remainder operation is normalized into the valid range.

---

## 27. Important edge cases

Array algorithms often fail not because the main algorithm is incorrect, but because boundary conditions were not considered.

Important cases include:

### Empty array

`[]`

There is no first element, minimum, maximum, or second-largest value.

### Single-element array

`[42]`

The maximum and minimum are `42`, but a second-largest distinct value does not exist.

### All elements equal

`[7, 7, 7]`

There is no second-largest distinct value.

### Negative values

`[-10, -3, -20]`

Minimum and maximum logic must not assume values are positive.

### Zero values

`[0, 0, 5, -3]`

Zero should be classified separately when counting positive and negative values.

### Rotation larger than array length

For an array of length five, rotation by twelve is equivalent to rotation by two.

### Negative rotation

A robust implementation should explicitly define how negative rotation values are interpreted.

The implementations normalize them as equivalent left rotations.

### Target absent

Search algorithms should clearly represent failure rather than accessing an invalid result.

### Unsorted input for binary search

Binary search should not be applied unless the sorted-input requirement is satisfied.

---

## 28. Common mistakes

### Using the wrong last index

For an array of length `n`, the last valid index is:

`n - 1`

not `n`.

### Initializing minimum or maximum incorrectly

Using `0` as the initial maximum fails when all values are negative.

Using an arbitrary large constant for minimum can also introduce unnecessary assumptions.

Initializing from the first element is safer when the array is known to be non-empty.

### Ignoring the empty-array case

Operations requiring an element should define what happens when there are no elements.

### Confusing second-largest with second element after sorting

The second-largest distinct value is different from simply selecting an arbitrary second position.

Duplicates must be considered.

### Forgetting rotation normalization

A rotation by a value much larger than the array length should not cause unnecessary work.

### Using binary search on unsorted data

Binary search depends on ordering.

Without sorted input, the elimination logic is invalid.

### Accidentally modifying the input

Some operations create a new array while others modify the original array.

This distinction matters when the same data is needed elsewhere.

### Treating missing-value detection as one universal problem

Finding all missing values in a range is different from finding one missing value under strict `0..n` assumptions.

The algorithm must match the problem definition.

---

## 29. Performance considerations

The most important array performance characteristic is the cost of accessing elements.

Random access by index is generally O(1).

A complete scan is O(n).

Sorting normally requires O(n log n) time with comparison-based algorithms.

Hash-based frequency counting is typically O(n) average time.

Binary search is O(log n), but it requires sorted data.

In-place algorithms can reduce memory consumption.

For example:

| Operation | Typical time | Extra space |
|---|---:|---:|
| Index access | O(1) | O(1) |
| Update | O(1) | O(1) |
| Traversal | O(n) | O(1) |
| Linear search | O(n) | O(1) |
| Minimum | O(n) | O(1) |
| Maximum | O(n) | O(1) |
| Second-largest | O(n) | O(1) |
| Frequency counting | O(n) average | O(k) |
| Reverse in place | O(n) | O(1) |
| Rotate by reversal | O(n) | O(1) |
| Duplicate removal with hashing | O(n) average | O(k) |
| Binary search | O(log n) | O(1) |
| Prefix-sum construction | O(n) | O(n) |

Here, `k` represents the number of distinct values.

---

## 30. Time complexity versus number of passes

Two algorithms can both be O(n) while having different practical costs.

For example, these two designs both have asymptotic complexity O(n):

1. Calculate minimum in one pass, maximum in another, and sign counts in a third.
2. Calculate all three during one traversal.

The second approach may reduce traversal overhead.

This does not mean that every calculation should be forced into one giant loop. Code clarity, maintainability, and correctness remain important.

The appropriate design depends on the application.

---

## 31. Space complexity

Space complexity describes additional memory used by an algorithm.

An in-place reversal uses O(1) extra space because it only maintains a small number of variables.

Frequency counting requires additional storage because every distinct value must be represented in the frequency table.

Duplicate removal using a set also requires memory proportional to the number of distinct values.

Prefix sums require a separate array containing one cumulative value per input element.

Therefore, choosing an algorithm is often a trade-off between:

- Execution time
- Memory consumption
- Code complexity
- Input characteristics
- Frequency of repeated operations

---

## 32. Python, JavaScript, and C++ comparison

### Python

Python is useful for expressing array algorithms concisely.

Strengths demonstrated in this lesson include:

- Readable syntax
- Built-in lists
- Dictionaries
- Sets
- `Counter`
- Simple iteration
- Rapid algorithm experimentation

The Python implementation is especially suitable for studying algorithmic logic without much language overhead.

### JavaScript

JavaScript is useful when array algorithms are part of browser or application logic.

The implementation demonstrates:

- Arrays
- `Map`
- `Set`
- `at`
- `slice`
- `map`
- `forEach`
- Runtime validation
- Modern JavaScript syntax

The same fundamental algorithmic ideas transfer directly to web applications.

### C++

C++ exposes more implementation details and provides explicit control over data structures and memory-related behavior.

The case study demonstrates:

- `std::vector`
- `std::unordered_map`
- `std::unordered_set`
- `std::optional`
- Exceptions
- Classes
- Standard algorithms
- Explicit validation
- In-place processing

C++ is particularly useful for understanding how array algorithms fit into larger performance-sensitive systems.

---

## 33. Security and reliability considerations

Array algorithms are usually not security-sensitive by themselves, but incorrect boundary handling can create serious software defects.

Important practices include:

- Validate indexes.
- Validate input values.
- Avoid reading outside valid memory boundaries in languages where this is possible.
- Define behavior for empty arrays.
- Define behavior for invalid rotation counts.
- Do not use binary search without its sorted-input precondition.
- Avoid integer overflow when calculating indexes or cumulative sums.
- Use sufficiently wide integer types when aggregate values can exceed the range of individual elements.
- Treat external input as untrusted until validated.

The C++ implementation uses `long long` for prefix sums because a cumulative total may be larger than an individual `int`.

In production systems, numeric limits should be selected according to the actual domain rather than assumed from a small teaching example.

---

## 34. Implementation design principles

The three implementations demonstrate several reusable design principles.

### Separate algorithms from demonstrations

Core functions implement specific operations while demonstration functions show how those operations behave.

### Validate assumptions

An algorithm should make important preconditions explicit.

Binary search is a good example: sorted input is a requirement, not an optional detail.

### Handle boundaries deliberately

Empty arrays, single elements, duplicates, negative values, and large rotation counts should be considered during design rather than discovered accidentally through failures.

### Prefer the simplest correct algorithm

A one-pass O(n) solution is preferable to sorting when sorting is not required.

### Use specialized data structures when appropriate

Frequency counting benefits from dictionaries, maps, or hash tables.

Duplicate removal benefits from sets.

### Consider mutation

An in-place operation can save memory but changes the original data.

A copy-based operation preserves the original but consumes additional memory.

---

## 35. Real-world applications

Array fundamentals appear throughout software engineering.

Examples include:

- Inventory quantities
- Financial time series
- Sensor readings
- Exam scores
- Temperature measurements
- Image pixels
- Network packets
- Transaction amounts
- User activity metrics
- Machine-learning feature vectors
- Database query results
- Game state
- Audio samples
- Scientific measurements

More advanced data structures and algorithms frequently build on these same operations.

For example:

- Sorting builds on traversal and comparison.
- Searching builds on indexing and ordering.
- Hash tables support frequency counting.
- Sliding-window algorithms repeatedly process array ranges.
- Prefix sums support fast range queries.
- Two-pointer algorithms solve structured sequence problems.
- Dynamic programming frequently uses arrays for stored subproblem results.

---

## 36. Practice problems implemented

The three deliverables directly implement the requested Day 12 exercises.

### Maximum element

Find the largest value using a single traversal.

### Minimum element

Find the smallest value using a single traversal.

### Second-largest element

Find the second-largest distinct value in one pass.

### Reverse array

Reverse the array using two pointers and in-place swapping.

### Rotate array

Rotate the array using both copy-based and in-place reversal techniques.

### Remove duplicates

Remove repeated values while preserving the first occurrence.

### Count positive/negative values

Classify values into positive, negative, and zero categories.

### Find missing values

Demonstrate both:

- Multiple missing values in a known range.
- One missing value from a complete `0..n` sequence using XOR.

---

## 37. Verification and testing

The Python, JavaScript, and C++ implementations contain test cases for important operations.

The tests verify:

- Maximum
- Minimum
- Second-largest distinct value
- Reversal
- Rotation
- Duplicate removal
- Sign counting
- Missing-value detection
- Linear search
- Binary search
- Prefix sums
- Two-pointer search

Testing edge cases is particularly important for array algorithms because boundary errors often occur at:

- Index `0`
- Last index
- Empty arrays
- One-element arrays
- Duplicate values
- Missing targets
- Rotation boundaries

---

## 38. Core principles to retain

The most important ideas from this topic are algorithmic rather than language-specific.

1. Array indexes normally begin at zero.
2. Direct indexed access is O(1).
3. Traversing all elements is O(n).
4. Linear search does not require sorted data.
5. Binary search requires sorted data.
6. Minimum and maximum can be found in one pass.
7. The second-largest distinct value can also be found in one pass.
8. Two pointers can perform efficient in-place transformations.
9. Rotation counts should be normalized using the array length.
10. Sets and maps are useful for duplicate removal and frequency counting.
11. Prefix sums trade memory for faster repeated range queries.
12. XOR can solve the single-missing-value problem under strict assumptions.
13. Empty arrays and boundary conditions must be handled explicitly.
14. An algorithm's assumptions are part of its correctness.
15. Time complexity and space complexity should both be considered when choosing an implementation.
