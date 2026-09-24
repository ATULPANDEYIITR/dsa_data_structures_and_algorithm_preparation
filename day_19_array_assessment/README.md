# Day 19 — Array assessment

## Topic

Day 19 is an assessment of array problem-solving ability using eight problems:

- 3 easy problems
- 4 medium problems
- 1 difficult problem

The assessment concentrates on recognizing reusable array patterns rather than solving every problem through brute force.

The selected patterns are:

- Prefix sums
- Two pointers
- Stable in-place compaction
- Kadane's algorithm
- Fixed-size sliding window
- Hashing with prefix sums
- Prefix and suffix products
- Two pointers with running boundary maxima

Each problem is documented through:

- Pattern
- Approach
- Time Complexity
- Space Complexity
- Mistake
- Improvement

---

## Assessment structure

| Level | Problem | Main pattern |
|---|---|---|
| Easy | Find Pivot Index | Prefix sum |
| Easy | Move Zeroes | Two pointers |
| Easy | Maximum Subarray | Kadane's algorithm |
| Medium | Maximum Sum Subarray of Size K | Sliding window |
| Medium | Two Sum II | Two pointers |
| Medium | Subarray Sum Equals K | Prefix sum + hashing |
| Medium | Product of Array Except Self | Prefix/suffix products |
| Difficult | Trapping Rain Water | Two pointers + boundary maxima |

The three implementations are intentionally different:

- Python emphasizes readable algorithmic demonstrations, reference implementations, testing, and study-oriented explanations.
- JavaScript demonstrates the same array patterns using JavaScript arrays, `Map`, destructuring, runtime validation, and executable Node.js examples.
- C++ develops the problems into an industry-style assessment engine with classes, metadata, validation, deterministic testing, benchmarking, and structured reporting.

---

## Fundamental array concepts

An array stores a sequence of elements that can be accessed by index.

For an array such as:

`[10, 20, 30, 40]`

the valid zero-based indices are:

`0, 1, 2, 3`

The value at index `2` is `30`.

Array problems often become difficult not because accessing an element is complicated, but because the algorithm must efficiently maintain information while moving through the array.

Important questions to ask before coding include:

1. Is the array sorted?
2. Can values be negative?
3. Can values be duplicated?
4. Is the array allowed to be modified?
5. Is the result required to be contiguous?
6. Is a fixed window size given?
7. Is extra memory allowed?
8. Does the problem ask for a value, an index, a count, or an actual subarray?
9. Does the ordering of the input provide useful information?
10. Can previous calculations be reused?

These questions often reveal the appropriate pattern.

---

# Easy problems

## 1. Find Pivot Index

### Problem

Given an integer array, find the first index where the sum of all elements to the left equals the sum of all elements to the right.

For:

`[1, 7, 3, 6, 5, 6]`

the answer is index `3`.

The left side is:

`1 + 7 + 3 = 11`

The right side is:

`5 + 6 = 11`

### Pattern

Prefix-sum reasoning.

### Approach

First calculate the total array sum.

Maintain a running `left_sum`.

At index `i`:

`right_sum = total_sum - left_sum - nums[i]`

If:

`left_sum == right_sum`

then the current index is the pivot.

This avoids independently summing the two sides at every position.

### Time Complexity

`O(n)`

Every element is processed a constant number of times.

### Space Complexity

`O(1)` auxiliary space.

Only a few running variables are required.

### Mistake

A common inefficient solution calculates:

`sum(nums[:i])`

and:

`sum(nums[i+1:])`

for every index.

That can result in `O(n²)` work.

### Improvement

Calculate the total once and maintain the left sum incrementally.

### Edge cases

Important cases include:

- Empty array
- No pivot
- Pivot at index `0`
- Pivot at the last index
- Negative numbers
- Multiple possible pivot positions

The implementation returns the first valid index.

---

## 2. Move Zeroes

### Problem

Move all zeroes to the end of an array while preserving the relative ordering of non-zero elements.

Example:

`[0, 1, 0, 3, 12]`

becomes:

`[1, 3, 12, 0, 0]`

### Pattern

Two pointers and stable compaction.

### Approach

Use two indices:

- `read_index` scans the array.
- `write_index` identifies where the next non-zero value should be placed.

Whenever a non-zero value is found, exchange it with the value at the write position and advance the write position.

The array is modified in place.

### Time Complexity

`O(n)`

### Space Complexity

`O(1)` auxiliary space.

### Mistake

Removing zeroes from the array while iterating can shift elements and cause skipped values.

Creating another array is easier to write but does not satisfy an in-place requirement when one exists.

### Improvement

Use a write pointer and perform stable in-place compaction.

### Important property

The relative ordering of non-zero values is preserved.

For:

`[4, 0, 2, 0, 7]`

the non-zero values remain:

`4, 2, 7`

---

## 3. Maximum Subarray

### Problem

Find the contiguous subarray with the largest possible sum.

For:

`[-2, 1, -3, 4, -1, 2, 1, -5, 4]`

the maximum-sum subarray is:

`[4, -1, 2, 1]`

with sum:

`6`

### Pattern

Kadane's algorithm.

### Approach

At every position, determine whether it is better to:

- extend the previous subarray, or
- start a new subarray at the current element.

The recurrence is:

`current_sum = max(value, current_sum + value)`

The best answer is the maximum value of `current_sum` encountered during the scan.

The implementation also tracks the starting and ending indices.

### Time Complexity

`O(n)`

### Space Complexity

`O(1)`

### Mistake

Initializing the answer to zero.

For:

`[-8, -3, -6, -2]`

the correct answer is `-2`, not `0`.

### Improvement

Initialize the running and best sums using the first array element.

This preserves correctness for arrays containing only negative values.

---

# Medium problems

## 4. Maximum Sum Subarray of Size K

### Problem

Find the largest sum among all contiguous subarrays containing exactly `k` elements.

Example:

`[2, 1, 5, 1, 3, 2]`

with:

`k = 3`

The windows are:

`[2, 1, 5]`

`[1, 5, 1]`

`[5, 1, 3]`

`[1, 3, 2]`

The maximum sum is:

`9`

### Pattern

Fixed-size sliding window.

### Brute-force approach

For every possible starting position, calculate the complete sum of the next `k` elements.

If there are approximately `n` windows and each contains `k` elements, the complexity is:

`O(n*k)`

### Optimized approach

Calculate the first window once.

When the window moves one position:

- subtract the element leaving the window
- add the element entering the window

Therefore each element is handled a constant number of times.

### Time Complexity

`O(n)`

### Space Complexity

`O(1)`

### Mistake

Recalculating every window from scratch.

### Improvement

Reuse the previous window sum.

The key idea is:

`new_window_sum = old_window_sum - outgoing + incoming`

This is one of the most important fixed-window transformations.

---

## 5. Two Sum II — Input Array Is Sorted

### Problem

Given a sorted array, find two numbers whose sum equals a target.

Example:

`[2, 7, 11, 15]`

with target:

`9`

The answer is positions:

`[1, 2]`

when using one-based indexing.

### Pattern

Opposite-direction two pointers.

### Approach

Place:

- `left` at the beginning
- `right` at the end

Calculate:

`numbers[left] + numbers[right]`

If the sum is too small:

`left += 1`

If the sum is too large:

`right -= 1`

If it equals the target, the answer has been found.

### Why sorting matters

The sorted order provides information about how pointer movement changes the sum.

If the current sum is too small, moving the right pointer left would make the sum even smaller. Therefore the left pointer must move right.

If the current sum is too large, the right pointer must move left.

### Time Complexity

`O(n)`

### Space Complexity

`O(1)`

### Mistake

Ignoring the sorted property and using nested loops or a hash table automatically.

### Improvement

Exploit the ordering constraint before reaching for extra memory.

---

## 6. Subarray Sum Equals K

### Problem

Count the number of contiguous subarrays whose sum equals `k`.

Example:

`[1, 1, 1]`

with:

`k = 2`

contains two valid subarrays:

`[1, 1]`

and:

`[1, 1]`

Therefore the answer is:

`2`

### Pattern

Prefix sum plus frequency hashing.

### Prefix-sum relationship

Suppose the current prefix sum is:

`P`

A previous prefix sum:

`Q`

forms a subarray with sum `k` when:

`P - Q = k`

Therefore:

`Q = P - k`

At every position, the algorithm checks how many times `P - k` has appeared.

### Why frequencies are required

A prefix sum can appear multiple times.

If a required prefix sum has appeared three times, there are three different starting positions that produce a valid subarray ending at the current position.

### Time Complexity

`O(n)` expected with a hash map.

### Space Complexity

`O(n)`

The prefix-frequency map may contain many distinct sums.

### Mistake

Using a normal variable-size sliding window when negative numbers are permitted.

Sliding windows generally depend on a useful monotonic relationship between expanding or shrinking the window and its sum.

Negative values can destroy that property.

For example:

`[1, -1, 0]`

contains several zero-sum subarrays.

### Improvement

Use prefix sums and a frequency map when arbitrary negative, zero, and positive values are possible.

---

## 7. Product of Array Except Self

### Problem

For every position, calculate the product of all array elements except the value at that position.

Example:

`[1, 2, 3, 4]`

produces:

`[24, 12, 8, 6]`

### Pattern

Prefix products and suffix products.

### Prefix concept

For every index, first calculate the product of all elements before that index.

For:

`[1, 2, 3, 4]`

the prefix contribution is:

`[1, 1, 2, 6]`

Then perform a reverse pass and multiply each position by the product of all elements after it.

The suffix contribution is maintained using one variable.

### Why division is avoided

A division-based approach becomes complicated when zeroes are present.

For example:

`[-1, 1, 0, -3, 3]`

has exactly one zero.

The expected output is:

`[0, 0, 9, 0, 0]`

The prefix/suffix approach handles zeroes naturally.

### Time Complexity

`O(n)`

### Space Complexity

`O(1)` auxiliary space, excluding the required output array.

The output array itself is reused to store prefix information.

### Mistake

Using division without correctly handling:

- one zero
- multiple zeroes
- integer overflow
- division by zero

### Improvement

Use two linear passes without division.

---

# Difficult problem

## 8. Trapping Rain Water

### Problem

Given an array representing vertical bars, calculate how much water can be trapped after rainfall.

Example:

`[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]`

produces:

`6`

units of trapped water.

### Pattern

Two pointers with running boundary maxima.

### Core formula

At a position:

`water = min(max_left, max_right) - height`

when the result is positive.

The challenge is obtaining `max_left` and `max_right` efficiently.

### Prefix-array approach

One straightforward approach creates:

- `left_max`
- `right_max`

arrays.

This takes:

`O(n)` time

and:

`O(n)` auxiliary space.

It is easy to understand and is useful as a reference implementation.

### Optimized two-pointer approach

Maintain:

- `left`
- `right`
- `left_max`
- `right_max`

If the left boundary is lower than or equal to the right boundary, the left side can be processed safely.

Otherwise the right side is processed.

The lower boundary is the limiting side.

This permits the algorithm to calculate the trapped water without storing complete prefix and suffix arrays.

### Time Complexity

`O(n)`

### Space Complexity

`O(1)`

### Mistake

For every position, independently search for the highest bar to the left and right.

That produces:

`O(n²)`

behavior.

Another mistake is moving pointers without preserving the lower-boundary invariant.

### Improvement

Maintain running maximum boundaries and process each position once.

---

# Pattern recognition

## Prefix sums

Use prefix sums when a problem repeatedly asks about sums over contiguous ranges or relationships between previous cumulative sums.

Typical clues include:

- range sum
- equilibrium or pivot position
- subarray sum
- count of subarrays with a target sum

The important transformation is:

`range_sum(i, j) = prefix[j] - prefix[i - 1]`

For subarray counting, the relationship becomes:

`current_prefix - previous_prefix = target`

---

## Two pointers

Two pointers are useful when the structure of the array allows one pointer movement to eliminate a group of possibilities.

Common forms include:

### Opposite-direction pointers

One pointer begins at the left and one at the right.

Useful for:

- sorted two-sum problems
- partitioning
- container-style problems
- trapping rain water

### Same-direction pointers

Both pointers move forward.

Useful for:

- stable compaction
- removing elements
- maintaining a valid range
- some sliding-window implementations

---

## Sliding window

A sliding window represents a contiguous region.

For a fixed-size window:

`[left ... right]`

has a fixed number of elements.

When it moves:

- remove the outgoing element
- add the incoming element

This avoids recalculating the entire window.

Variable-size sliding windows require an additional condition that tells the algorithm when the window should expand or contract.

---

## Kadane's algorithm

Kadane's algorithm solves the maximum-subarray-sum problem in linear time.

The central decision is:

`start new`

versus:

`extend previous`

The algorithm does not enumerate every possible subarray.

It keeps only the information needed to determine the best subarray ending at the current position.

---

## Prefix sum plus hashing

This combination is particularly useful for counting subarrays.

The prefix sum converts a range-sum condition into a difference between two cumulative values.

Hashing makes the search for the required previous value approximately constant time on average.

This is different from a sliding window because it does not require the values to be positive.

---

## Prefix and suffix products

Many array problems can be decomposed into:

- information before the current index
- information after the current index

A forward pass can calculate the first component.

A backward pass can calculate the second component.

The output array can sometimes be reused as storage, reducing auxiliary memory.

---

# Complexity comparison

| Problem | Optimized time | Auxiliary space | Main reason |
|---|---:|---:|---|
| Find Pivot Index | O(n) | O(1) | Running sums |
| Move Zeroes | O(n) | O(1) | Two pointers |
| Maximum Subarray | O(n) | O(1) | Kadane state |
| Maximum Sum Subarray of Size K | O(n) | O(1) | Reused window |
| Two Sum II | O(n) | O(1) | Sorted two pointers |
| Subarray Sum Equals K | O(n) expected | O(n) | Prefix-frequency map |
| Product Except Self | O(n) | O(1) auxiliary | Two passes |
| Trapping Rain Water | O(n) | O(1) | Running boundary maxima |

The comparison demonstrates an important principle: a lower time complexity sometimes requires additional memory, while other optimizations exploit the input structure to improve both time and space.

---

# Python implementation

The Python implementation is structured as a study-oriented reference file.

It contains:

- input validation
- reusable functions
- brute-force reference solutions
- optimized solutions
- edge-case demonstrations
- deterministic unit tests
- complexity documentation
- common mistake explanations
- performance comparison
- maximum-subarray index tracking
- a structured `ProblemRecord` data class

### Python-specific observations

Python lists provide convenient dynamic-array behavior, but operations such as inserting or deleting from the middle can require shifting elements.

The assessment therefore focuses on algorithms that scan or manipulate arrays efficiently rather than relying on expensive repeated structural changes.

Python dictionaries are used for prefix-sum frequencies because they provide expected constant-time lookup and insertion.

The Python implementation also uses type annotations to make function inputs and outputs easier to understand.

---

# JavaScript implementation

The JavaScript implementation is designed to run as a standalone Node.js file.

It demonstrates:

- JavaScript arrays
- `Map`
- destructuring assignment
- runtime validation
- object-based result structures
- performance measurement with `performance.now()`
- in-place array mutation
- deterministic assertions

### JavaScript-specific observations

JavaScript arrays are flexible and can contain values of different types, so explicit validation is useful in an algorithm-study environment.

The implementation uses `Map` for prefix-sum frequencies rather than relying on object keys.

The expression:

`map.get(key) ?? 0`

provides a convenient default when a key has not yet been stored.

Destructuring is used for in-place swapping:

`[a, b] = [b, a]`

This makes the two-pointer and compaction implementations concise while retaining their algorithmic structure.

---

# C++ case study

## Problem being modeled

The C++ implementation treats the eight array problems as a small assessment system rather than merely a collection of independent functions.

The system:

1. Defines reusable algorithms.
2. Stores metadata about every problem.
3. Executes deterministic tests.
4. Records pass/fail results.
5. Reports assessment documentation.
6. Demonstrates edge cases.
7. Benchmarks an inefficient and optimized implementation.

This models a simplified technical assessment environment in which algorithms are not only implemented but also tested and documented.

---

## C++ design

The central class is `ArrayAssessmentEngine`.

It contains metadata for all eight problems.

Each metadata record stores:

- problem name
- difficulty
- pattern
- approach
- time complexity
- space complexity
- common mistake
- improvement

The engine also stores individual assessment results.

This separates problem knowledge from algorithm execution.

---

## Major C++ components

### `ProblemMetadata`

Represents the documentation associated with one problem.

It prevents algorithmic information from being scattered throughout the reporting logic.

### `AssessmentResult`

Represents whether a deterministic test passed.

It also stores a human-readable explanation.

### `SubarrayResult`

Represents the maximum-subarray result:

- sum
- start index
- end index

This is preferable to returning unrelated values through separate global variables.

### `ArrayAssessmentEngine`

Coordinates:

- assessment execution
- metadata reporting
- result reporting

The algorithms themselves remain independent functions.

This separation makes testing and replacement easier.

---

# Algorithmic details in the C++ implementation

## Integer width

Several calculations use `long long` instead of `int`.

This is relevant for:

- cumulative sums
- products
- trapped-water totals

The type choice reduces the risk of overflow compared with using `int` for larger intermediate values.

It does not eliminate overflow for arbitrarily large input. Production systems should choose numeric types based on explicit input constraints.

---

## Hashing

`unordered_map` stores prefix-sum frequencies for the subarray-sum problem.

Its expected lookup and insertion complexity is approximately:

`O(1)`

per operation.

Worst-case hash-table behavior can degrade, so the complexity is conventionally described as expected `O(n)` for the complete algorithm.

---

## Vectors

C++ `vector` is used for array-like storage.

It provides:

- contiguous storage
- constant-time indexed access
- automatic memory management
- dynamic size

The contiguous representation is useful for array algorithms because sequential traversal has good cache behavior.

---

## In-place modification

The Move Zeroes implementation accepts the vector by reference:

`vector<int>&`

This allows the original vector to be modified directly.

The function does not create another array.

---

# Correctness considerations

## Pivot index

The invariant is:

`left_sum + current_value + right_sum = total_sum`

At every index, the right sum is derived from the invariant.

The algorithm therefore does not need to traverse either side repeatedly.

---

## Move Zeroes

The write pointer always identifies the next location for a non-zero element.

After processing the first `i` elements, all non-zero elements encountered so far have been compacted into the prefix beginning at index zero.

---

## Maximum Subarray

The state `current_sum` represents the maximum sum of a subarray that must end at the current position.

The global best value is therefore the maximum of all such ending-at-current-position states.

---

## Fixed sliding window

The window always contains exactly `k` elements.

When the right boundary moves one position, exactly one element leaves and exactly one element enters.

Therefore the running sum remains the sum of exactly the current window.

---

## Two Sum II

Because the array is sorted:

- increasing the left pointer cannot decrease the value at the left side
- decreasing the right pointer cannot increase the value at the right side

This gives a deterministic way to eliminate impossible pairs.

---

## Subarray Sum Equals K

For current prefix sum `P`, every previous occurrence of:

`P - K`

corresponds to a subarray ending at the current position whose sum is `K`.

The frequency map counts all such starting positions.

---

## Product Except Self

At each index:

`result[i] = product_before_i × product_after_i`

The forward pass stores the first factor.

The reverse pass supplies the second factor.

No division is required.

---

## Trapping Rain Water

For each processed position, the amount of water depends on the smaller of the two boundary maxima.

The two-pointer algorithm processes the side whose current boundary is lower.

The running maximum for that side is therefore sufficient to determine the contribution.

---

# Edge cases

Array algorithms frequently fail at boundaries rather than normal examples.

The implementations test or demonstrate:

### Empty arrays

Some operations, such as maximum subarray, require at least one element and therefore raise an error.

Other operations naturally return an empty result or zero.

### Single-element arrays

There is not enough structure for many pair or water-trapping problems.

The algorithm should not access invalid neighboring positions.

### All-zero arrays

Useful for testing Move Zeroes, Product Except Self, and water calculations.

### All-negative arrays

Critical for maximum-subarray problems.

The answer must remain negative if every value is negative.

### Negative and positive mixtures

Important for prefix-sum problems because negative values can invalidate assumptions used by some sliding-window algorithms.

### Duplicate values

Useful for testing pointer movement and prefix-frequency counting.

### Monotonic arrays

Increasing and decreasing arrays expose incorrect assumptions about local maxima and minima.

### No solution

Two Sum II returns `(-1, -1)` when no pair exists.

Pivot Index returns `-1` when no pivot exists.

---

# Exceptions and validation

The Python implementation validates integer arrays and raises appropriate exceptions for invalid input.

Examples include:

- `None`
- non-integer values
- invalid window size
- empty input for maximum-subarray operations

The JavaScript implementation performs equivalent runtime checks because JavaScript does not enforce array element types at compile time.

The C++ implementation uses exceptions for invalid `k` values and invalid states such as requesting a maximum subarray from an empty vector.

Validation prevents algorithmic failures from being confused with invalid input.

---

# Common mistakes

## Mistake 1: Brute force before identifying reusable state

Many array problems become unnecessarily expensive when previous work is discarded.

The fixed sliding-window problem is the clearest example.

Recomputing every window is wasteful because adjacent windows overlap heavily.

---

## Mistake 2: Using a sliding window for every subarray-sum problem

Sliding windows require appropriate monotonic behavior.

When negative numbers are allowed, expanding a window can decrease its sum and shrinking it can increase its sum.

Prefix sums do not have this limitation.

---

## Mistake 3: Ignoring sorted input

A sorted array provides information.

Two Sum II demonstrates that a hash table is not automatically the best representation when ordering allows a constant-space two-pointer solution.

---

## Mistake 4: Mishandling all-negative arrays

Maximum subarray problems are frequently implemented incorrectly by initializing the best sum to zero.

That implicitly assumes that an empty subarray is allowed.

The implementation here requires a non-empty subarray.

---

## Mistake 5: Using division for Product Except Self

Division introduces special cases involving zero.

Prefix and suffix products are more robust for the intended constraints.

---

## Mistake 6: Incorrect pointer movement in Trapping Rain Water

The two-pointer method depends on processing the side with the lower boundary.

Moving an arbitrary pointer breaks the reasoning behind the algorithm.

---

## Mistake 7: Confusing input space with auxiliary space

If a problem requires returning an output array, that output consumes memory.

Complexity discussions often report auxiliary space separately so that required output storage is not incorrectly counted as working memory.

---

# Performance considerations

Algorithmic performance should be evaluated using asymptotic complexity before relying on benchmark timings.

For example:

`O(n*k)`

and:

`O(n)`

may perform similarly on a small input.

As `n` grows, the difference becomes increasingly significant.

The Python, JavaScript, and C++ implementations include performance demonstrations for the fixed-window problem.

These benchmarks are illustrative rather than scientific measurements.

Actual runtime depends on:

- processor
- operating system
- interpreter or compiler
- runtime version
- memory hierarchy
- input size
- system load
- compiler optimization settings

For algorithm assessment, complexity analysis remains the primary comparison.

---

# Security considerations

These algorithms are not network protocols or authentication systems, but defensive implementation still matters.

## Input validation

Untrusted input should not be assumed to contain valid integers or valid window sizes.

Validation prevents unexpected runtime behavior.

## Numeric overflow

C++ calculations involving large sums or products can overflow fixed-width integer types.

The C++ implementation uses `long long` for important intermediate calculations, but production constraints should determine whether wider integer types or arbitrary-precision arithmetic are necessary.

## Memory limits

The prefix-frequency solution uses `O(n)` additional memory.

For extremely large input, memory consumption should be considered before choosing that approach.

## Denial-of-service considerations

When arrays originate from external requests, input-size limits should be enforced.

An algorithm with acceptable complexity can still consume excessive resources if an attacker is allowed to submit unbounded input.

---

# Implementation trade-offs

| Technique | Main advantage | Main trade-off |
|---|---|---|
| Prefix sum | Fast cumulative/range reasoning | May require stored prefix information |
| Two pointers | Often O(1) extra space | Usually requires structural properties |
| Sliding window | Avoids repeated range calculation | Requires a valid window invariant |
| Kadane | O(n) maximum subarray | Specialized to additive subarray optimization |
| Hash map | Fast expected lookup | Additional memory |
| Prefix/suffix passes | Avoids division and handles zeroes | Requires multiple passes |
| Two-pointer rain water | O(1) auxiliary space | More subtle correctness reasoning |
| Prefix-array rain water | Easy to reason about | O(n) extra memory |

The correct pattern depends on the problem constraints.

No single array technique should be applied mechanically.

---

# Python, JavaScript, and C++ comparison

## Python

Python is effective for algorithm study because the syntax is concise.

The implementation can focus directly on:

- algorithmic state
- invariants
- complexity
- testing

Dictionaries provide a convenient implementation of frequency maps.

The main limitation for performance-intensive workloads is that Python generally has higher per-operation runtime overhead than optimized native C++.

---

## JavaScript

JavaScript is useful when array algorithms need to be integrated into web applications or Node.js services.

The implementation demonstrates:

- arrays
- `Map`
- destructuring
- runtime validation
- JavaScript-specific timing APIs

The same algorithmic patterns remain applicable in browser-based applications.

---

## C++

C++ provides explicit control over:

- data types
- references
- memory behavior
- object structure
- numeric representation

The C++ case study therefore focuses on turning the individual algorithms into a small assessment framework.

This is useful for understanding how algorithmic functions can become components of a larger software system.

---

# Testing strategy

The implementations use deterministic examples rather than relying only on visual inspection.

Testing covers:

- normal inputs
- missing answers
- negative values
- zeroes
- duplicate values
- all-negative arrays
- monotonic arrays
- comparison with brute-force reference implementations

For an algorithmic solution, a useful testing process is:

1. Test the smallest valid input.
2. Test a normal example.
3. Test an input with duplicates.
4. Test zero values.
5. Test negative values where permitted.
6. Test an input with no answer.
7. Test a large enough input to expose poor complexity.
8. Compare the optimized implementation with a trusted brute-force implementation on small random inputs.

The Python and JavaScript files include deterministic assertions, while the C++ case study includes an assessment engine that records pass/fail results.

---

# Complexity reasoning

The most important skill in this assessment is not memorizing eight solutions.

It is learning to recognize why the solutions have their complexity.

Consider the progression:

### Repeated range calculation

`O(n²)`

### Reusing a fixed window

`O(n)`

### Reusing cumulative information

`O(n)`

### Using hashing to remember previous states

`O(n)` expected

### Exploiting sorted order

`O(n)` with constant extra space

### Maintaining boundary information

`O(n)` with constant extra space

The recurring theme is removal of repeated work.

---

# Problem-by-problem documentation

## Find Pivot Index

**Pattern:** Prefix-sum reasoning

**Approach:** Calculate the total sum once and maintain the left sum.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Mistake:** Recalculating both sides at each index.

**Improvement:** Derive the right sum from the total.

---

## Move Zeroes

**Pattern:** Two pointers

**Approach:** Use a read pointer and write pointer to compact non-zero elements.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Mistake:** Removing elements while traversing.

**Improvement:** Modify the array in place.

---

## Maximum Subarray

**Pattern:** Kadane's algorithm

**Approach:** Choose between extending the current subarray and starting a new one.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Mistake:** Initializing the answer to zero.

**Improvement:** Initialize state from the first element.

---

## Maximum Sum Subarray of Size K

**Pattern:** Fixed-size sliding window

**Approach:** Subtract the outgoing value and add the incoming value.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Mistake:** Recomputing every window.

**Improvement:** Maintain one rolling sum.

---

## Two Sum II

**Pattern:** Opposite-direction two pointers

**Approach:** Use sorted order to decide which pointer can move.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Mistake:** Ignoring sorted input.

**Improvement:** Use the sorted-array invariant.

---

## Subarray Sum Equals K

**Pattern:** Prefix sum plus hashing

**Approach:** Count previous prefix sums equal to `current_prefix - k`.

**Time Complexity:** `O(n)` expected

**Space Complexity:** `O(n)`

**Mistake:** Applying a sliding window to arbitrary signed values.

**Improvement:** Use a prefix-frequency map.

---

## Product of Array Except Self

**Pattern:** Prefix and suffix products

**Approach:** Store prefix products in the result and multiply suffix products in reverse.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)` auxiliary, excluding output.

**Mistake:** Using division without handling zeroes.

**Improvement:** Avoid division completely.

---

## Trapping Rain Water

**Pattern:** Two pointers and running boundary maxima

**Approach:** Process the side with the lower boundary while maintaining its maximum.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Mistake:** Repeatedly scanning for left and right maxima.

**Improvement:** Maintain both maxima incrementally.

---

# Assessment-level decision process

When encountering a new array problem, first classify the structure.

If the problem involves a balance between the left and right portions of the array, consider prefix sums.

If the array is sorted and the problem asks for a pair or boundary relationship, consider two pointers.

If the problem asks about a contiguous region of fixed length, consider a fixed sliding window.

If the problem asks for the best contiguous sum, consider Kadane's algorithm.

If the problem asks for the number of subarrays matching a sum and negative values are allowed, consider prefix sums plus hashing.

If every output position depends on elements before and after it, consider prefix/suffix decomposition.

If each position depends on left and right boundaries, consider whether two pointers can maintain the required boundary invariant.

This classification process is more transferable than memorizing individual code templates.

---

# Practical relevance

Array techniques appear in many real systems.

Examples include:

- time-series processing
- financial price analysis
- telemetry processing
- sensor streams
- memory buffers
- image rows and pixel data
- analytics pipelines
- inventory calculations
- scheduling data
- ranking systems
- resource measurements
- log processing
- numerical computation

For large datasets, avoiding repeated work can substantially reduce CPU usage and latency.

The same reasoning used in an interview-style array problem can therefore contribute to production algorithm design.

---

# Production implementation considerations

A production implementation should go beyond a correct algorithm.

Important considerations include:

- Validate external input.
- Define maximum input sizes.
- Select numeric types based on possible value ranges.
- Decide whether input may be mutated.
- Document whether indexing is zero-based or one-based.
- Define behavior for empty input.
- Define behavior when no answer exists.
- Test boundary conditions.
- Measure realistic workloads.
- Monitor memory usage for hash-based approaches.
- Avoid relying on benchmark timings from tiny datasets.
- Preserve algorithmic invariants when refactoring.
- Separate algorithm logic from input/output code.

The C++ assessment engine demonstrates this separation by keeping algorithm functions independent from assessment reporting.

---

# Key distinctions

## Subarray versus subsequence

A subarray must be contiguous.

For:

`[1, 2, 3, 4]`

`[2, 3]` is a subarray.

`[1, 3]` is not a contiguous subarray.

It may be considered a subsequence because the relative order is preserved while elements can be skipped.

Several problems in this assessment specifically depend on contiguity.

---

## Auxiliary space versus output space

If an algorithm must return an array of size `n`, that output itself requires `O(n)` memory.

When reporting auxiliary space, the required output storage is commonly excluded.

This distinction explains why Product of Array Except Self can be described as using `O(1)` auxiliary space even though it returns an `O(n)` result.

---

## Expected versus worst-case hash complexity

Hash tables generally provide expected `O(1)` lookup and insertion.

This produces expected `O(n)` complexity for Subarray Sum Equals K.

The exact worst-case behavior of a hash table depends on implementation and collision behavior.

---

# Final assessment record

| # | Difficulty | Problem | Pattern | Time | Space |
|---:|---|---|---|---:|---:|
| 1 | Easy | Find Pivot Index | Prefix sum | O(n) | O(1) |
| 2 | Easy | Move Zeroes | Two pointers | O(n) | O(1) |
| 3 | Easy | Maximum Subarray | Kadane | O(n) | O(1) |
| 4 | Medium | Maximum Sum Subarray of Size K | Sliding window | O(n) | O(1) |
| 5 | Medium | Two Sum II | Two pointers | O(n) | O(1) |
| 6 | Medium | Subarray Sum Equals K | Prefix sum + hashing | O(n) expected | O(n) |
| 7 | Medium | Product Except Self | Prefix/suffix | O(n) | O(1) auxiliary |
| 8 | Difficult | Trapping Rain Water | Two pointers | O(n) | O(1) |

The assessment covers the principal array patterns required to move from direct traversal toward optimized linear-time solutions while emphasizing invariants, constraints, edge cases, and complexity analysis.
