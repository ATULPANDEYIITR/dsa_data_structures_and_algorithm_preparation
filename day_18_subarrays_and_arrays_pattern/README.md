# Day 18 — Subarrays and Array Patterns

## Topic scope

This study module focuses on contiguous ranges inside arrays and the algorithmic patterns commonly used to process them efficiently.

The implementations cover:

- Subarray enumeration
- Subarray counting
- Incremental subarray sums
- Prefix sums
- Prefix sums combined with hashing
- Two-sum and two-pointer techniques
- Sliding windows
- Fixed-size and variable-size windows
- Sorting-based solutions
- Maximum subarray problems
- Minimum subarray problems
- Circular maximum subarray
- Zero-sum and exact-sum problems
- Divisibility patterns
- Binary-array transformations
- Edge cases and validation
- Complexity analysis
- Testing and algorithm verification
- Practical transaction-analysis modeling

The Python implementation provides a broad algorithm laboratory. The JavaScript implementation demonstrates the same problem-solving patterns in an executable application-oriented language. The C++ implementation turns the concepts into a structured transaction analytics case study.

## Fundamental concept: what is a subarray?

A subarray is a contiguous sequence of elements from an array.

For the array `[1, 2, 3, 4]`, valid subarrays include:

- `[1]`
- `[2]`
- `[3, 4]`
- `[1, 2, 3]`
- `[1, 2, 3, 4]`

The sequence `[1, 3]` is not a subarray because the elements are not adjacent in the original array.

The requirement of contiguity is the central distinction between a subarray and many other array structures.

## Subarray, subsequence, and subset

These terms should not be treated as interchangeable.

### Subarray

Elements must remain contiguous and in their original order.

For `[1, 2, 3]`, `[2, 3]` is a subarray.

### Subsequence

Elements must preserve relative order, but they do not need to be contiguous.

For `[1, 2, 3]`, `[1, 3]` is a subsequence.

### Subset

The concept focuses on membership rather than contiguity or necessarily preserving order.

For `[1, 2, 3]`, `{1, 3}` is a subset.

Many array problems become substantially easier once the exact requirement is identified.

## Number of non-empty subarrays

For an array of length `n`, the number of non-empty subarrays is:

`n(n + 1) / 2`

The reasoning is based on selecting the start and end positions.

For an array of length 4:

- Length 1: 4 subarrays
- Length 2: 3 subarrays
- Length 3: 2 subarrays
- Length 4: 1 subarray

Therefore:

`4 + 3 + 2 + 1 = 10`

The number grows quadratically. This is important when deciding whether explicit enumeration is practical.

## Subarray enumeration

The simplest implementation uses two boundaries:

- `start`
- `end`

For each start position, the end position moves from the start through the end of the array.

This creates `O(n^2)` ranges.

The Python implementation contains `enumerate_subarrays()` and `enumerate_subarray_ranges()`. The first materializes every subarray. The second stores only the boundaries.

That distinction matters because materializing every element of every subarray can require `O(n^3)` total element copying in the worst case.

## Incremental subarray sums

A naive approach may repeatedly calculate:

`sum(values[start:end + 1])`

That introduces an additional linear operation for every subarray.

A better educational baseline fixes the start position and maintains a running sum:

`current_sum += values[end]`

For each start position, the sum can therefore be updated in constant time as the end boundary moves.

The resulting complexity is:

- Time: `O(n^2)`
- Additional space for the output: dependent on the number of results
- Auxiliary working space: `O(1)`

This pattern is useful even when a more advanced algorithm exists because it provides a straightforward reference implementation.

## Prefix sums

A prefix sum array stores cumulative totals.

For:

`[3, -2, 5, 7]`

a prefix representation can be:

`[0, 3, 1, 6, 13]`

The zero at the beginning represents the sum of zero elements.

For an inclusive range `[left, right]`:

`range_sum = prefix[right + 1] - prefix[left]`

For example, the sum of indices 1 through 3 is:

`prefix[4] - prefix[1]`

which gives:

`13 - 3 = 10`

### Prefix-sum complexity

Building the prefix array:

- Time: `O(n)`
- Space: `O(n)`

Answering an individual range query:

- Time: `O(1)`

Therefore prefix sums are particularly useful when many range-sum queries are performed against an array that does not change frequently.

## Prefix sums with negative values

Prefix sums work with negative values without modification.

For:

`[5, -3, 7, -2]`

the cumulative values can increase and decrease.

This makes prefix sums more general than some sliding-window techniques.

A major distinction is that a standard variable-size sum window often requires non-negative or positive values, while prefix-sum identities do not have that restriction.

## Hashing with prefix sums

A powerful transformation occurs when the task asks for subarrays having an exact target sum.

Suppose:

`prefix[j] - prefix[i] = target`

Then:

`prefix[i] = prefix[j] - target`

At each position, the algorithm can ask whether the required earlier prefix sum has already appeared.

A hash table stores the frequency of previous prefix sums.

The Python function `subarray_sum_equals_k_hashing()` and the JavaScript function `subarraySumEqualsK()` demonstrate this technique.

The average complexity is:

- Time: `O(n)`
- Space: `O(n)`

This is a major improvement over `O(n^2)` enumeration for large arrays.

## Counting versus finding

There is an important distinction between several similar-looking tasks.

A problem may ask for:

- Whether at least one valid subarray exists
- The number of valid subarrays
- The longest valid subarray
- The shortest valid subarray
- The actual valid subarray
- The maximum sum among all subarrays
- The minimum sum among all subarrays

The same basic array can require very different algorithms depending on the requested result.

For example, exact-sum counting naturally uses prefix-sum frequencies, while longest exact-sum problems generally store the earliest occurrence of each prefix sum.

## Why earliest prefix positions matter

For the longest subarray with a particular sum, the earliest occurrence of a required prefix sum should be retained.

Suppose the current index is `j` and a suitable prefix sum appeared at several earlier positions.

The earliest position creates the largest possible distance:

`j - earliest_position`

Therefore replacing an earlier position with a later one would lose potentially valid longer answers.

This is why the Python function `longest_subarray_sum_k()` and the C++ method `longestSubarrayWithSum()` preserve the earliest occurrence.

## Hashing for two-sum

The two-sum problem asks whether two values add to a target.

For each value `x`, calculate:

`needed = target - x`

A hash table stores values already encountered.

If `needed` exists in the table, a solution has been found.

Average complexity:

- Time: `O(n)`
- Space: `O(n)`

This is useful when the original indices matter and the array does not have an ordering that can support two pointers.

## Two pointers

Two pointers use two indices that move according to a known invariant.

For a sorted array, a pair-sum problem can use:

- `left` at the smallest value
- `right` at the largest value

If:

`values[left] + values[right] < target`

the left pointer moves right because a larger value is required.

If:

`values[left] + values[right] > target`

the right pointer moves left because a smaller value is required.

If the sum equals the target, the pair has been found.

The complexity is:

- Time: `O(n)`
- Space: `O(1)`

This assumes the input is already sorted.

## Sorting before two pointers

If the input is unsorted, sorting can establish the required ordering.

The total complexity then becomes:

- Sorting: `O(n log n)`
- Two-pointer scan: `O(n)`
- Total: `O(n log n)`

The JavaScript and C++ implementations demonstrate sorting a copy or value collection before applying the two-pointer method.

Sorting can change the relationship between values and original indices. Therefore it is not automatically interchangeable with a hash-table solution.

## Two pointers versus hashing

The main distinction is the information being preserved.

Hashing generally provides:

- Average `O(n)` lookup-based processing
- Additional `O(n)` memory
- Direct preservation of original indices

Sorting plus two pointers generally provides:

- `O(n log n)` total time when sorting is necessary
- Potentially lower auxiliary memory depending on implementation
- Ordered data that can support other operations

The appropriate technique depends on the input constraints and required output.

## Sliding windows

A sliding window maintains a contiguous region using two boundaries.

The window is typically represented by:

- `left`
- `right`

The right boundary expands the window.

The left boundary contracts it when a constraint is violated.

The major advantage is that elements entering and leaving the window are processed incrementally rather than repeatedly recomputing the complete range.

## Fixed-size sliding window

Suppose the task asks for the maximum sum of exactly `k` consecutive elements.

The first window is calculated directly.

After that:

- Add the new rightmost value.
- Remove the value leaving the left side.

For a window of size 3:

`[2, 1, 5]`

becomes:

`[1, 5, 1]`

The transition is:

`new_sum = old_sum + incoming - outgoing`

Complexity:

- Time: `O(n)`
- Auxiliary space: `O(1)`

The Python function is `maximum_sum_fixed_window()`, the JavaScript function is `maximumSumFixedWindow()`, and the C++ implementation is `maximumFixedWindowSum()`.

## Variable-size sliding window

Variable-size windows are useful when the problem has a condition that can be restored by moving the left boundary.

For positive values, consider the requirement:

`sum >= target`

As the right boundary expands, the sum increases.

When the sum becomes large enough, the left boundary can move forward to make the window shorter.

This produces an `O(n)` solution because each element enters and leaves the active window at most once.

## Why positivity matters

The positive-value assumption is not a cosmetic restriction.

For a positive-value array:

- Adding a value cannot decrease the sum.
- Removing a value cannot increase the sum.

This monotonic behavior supports the sliding-window invariant.

With negative values, expanding the window can decrease the sum and removing an element can increase it. The simple sliding-window logic may then fail.

For exact target-sum problems containing arbitrary positive and negative values, prefix sums combined with hashing are generally more appropriate.

## Sliding window with frequency maps

Not every sliding window is based on sums.

A window can instead track:

- Distinct values
- Character frequencies
- Counts of categories
- Number of violations
- Other constraints

The JavaScript function `longestAtMostKDistinct()` demonstrates a frequency-map window.

The algorithm expands the right side and contracts the left side whenever the number of distinct values exceeds `k`.

Each element is added and removed at most once, producing average `O(n)` time.

## Maximum subarray problem

The maximum subarray problem asks for the contiguous subarray with the greatest sum.

A brute-force method can enumerate all ranges.

An improved `O(n^2)` method keeps an incremental sum for each starting position.

Kadane's algorithm reduces this to `O(n)`.

## Kadane's algorithm

For each position, define the best sum of a subarray ending at that position.

There are two possibilities:

1. Extend the previous subarray.
2. Start a new subarray at the current element.

The recurrence is:

`current = max(value, current + value)`

The global best is then updated from `current`.

The implementations also preserve:

- Start index
- End index
- Maximum sum

Therefore the algorithm returns the actual range instead of only the sum.

## Important all-negative edge case

Consider:

`[-8, -3, -5]`

The maximum non-empty subarray is:

`[-3]`

with sum:

`-3`

An implementation that initializes the answer to zero would incorrectly report zero, which represents an empty selection rather than a valid non-empty subarray.

The Python, JavaScript, and C++ Kadane implementations initialize their state from the first element so that all-negative arrays are handled correctly.

## Minimum subarray

The minimum subarray problem is the analogous problem for the smallest sum.

The recurrence reverses the comparison:

`current = min(value, current + value)`

The Python function `minimum_subarray_kadane()`, JavaScript function `minimumSubarrayKadane()`, and C++ function `minimumSubarray()` demonstrate this pattern.

The same linear-time structure can therefore solve both maximum and minimum contiguous-sum problems.

## Circular maximum subarray

A circular array allows the end of the array to connect to the beginning.

The maximum circular result has two possibilities:

1. The optimal range does not wrap around.
2. The optimal range wraps around.

The non-wrapping result is the ordinary maximum-subarray answer.

For a wrapping solution:

`wrapped = total_sum - minimum_subarray_sum`

The reason is that removing the minimum contiguous middle section leaves the maximum possible circular remainder.

### All-negative special case

If every value is negative, the formula can produce zero by removing the entire array.

That would represent an empty subarray.

The implementation therefore checks whether the ordinary maximum subarray is negative and returns that value directly.

## Divisibility with prefix sums

A useful mathematical extension is counting subarrays whose sum is divisible by `k`.

If two prefix sums have the same remainder modulo `k`, their difference is divisible by `k`.

Therefore the algorithm stores frequencies of prefix-sum remainders.

For prefix sums `P1` and `P2`:

`P1 mod k = P2 mod k`

implies:

`(P2 - P1) mod k = 0`

The Python and JavaScript implementations demonstrate this pattern.

In JavaScript, negative remainders require normalization because `%` can return a negative value. The expression `((remainder % k) + k) % k` produces a normalized non-negative remainder for positive `k`.

## Equal zeros and ones

A binary-array problem can often be transformed into a sum problem.

Replace:

`0 -> -1`

and:

`1 -> +1`

Then a subarray containing equal numbers of zeros and ones has transformed sum zero.

This converts a specialized counting problem into a prefix-sum frequency problem.

The Python function `count_subarrays_with_equal_zero_one()` demonstrates the transformation.

## Sorting-based solutions

Sorting is often used to impose structure on an otherwise unordered array.

A common pattern is:

1. Copy or transform the input.
2. Sort it.
3. Apply a linear scan or two-pointer technique.

The pair-sum example demonstrates this.

The C++ implementation also contains interval merging as a sorting-based case study.

For intervals:

`[1, 3]`, `[2, 6]`, `[8, 10]`, `[9, 12]`

sorting by starting position allows overlapping intervals to be processed in order.

The result is:

`[1, 6]`, `[8, 12]`

The interval problem is not itself a subarray problem, but it demonstrates the broader array-pattern principle that sorting can create an invariant that makes a later linear scan possible.

## Prefix sums versus sliding windows

These techniques solve overlapping but distinct classes of problems.

| Technique | Typical requirement | Time | Extra space |
|---|---|---:|---:|
| Brute-force enumeration | Small inputs or reference solution | `O(n^2)` to `O(n^3)` | Depends on output |
| Prefix sums | Range sums or prefix-based identities | Build `O(n)`, query `O(1)` | `O(n)` |
| Prefix sum + hashing | Exact sums with arbitrary integers | Average `O(n)` | `O(n)` |
| Fixed sliding window | Exactly `k` contiguous elements | `O(n)` | `O(1)` |
| Variable sliding window | Monotonic window constraint | Usually `O(n)` | Usually `O(1)` or `O(k)` |
| Two pointers | Ordered structure or special invariant | `O(n)` after ordering | Usually `O(1)` |
| Sorting + two pointers | Unordered input | `O(n log n)` | Depends on sort |
| Kadane | Maximum/minimum contiguous sum | `O(n)` | `O(1)` |

The key is not memorizing names in isolation. The input constraints determine which invariant is valid.

## Edge cases

Important cases include:

### Empty array

There is no non-empty subarray.

Functions that return a subarray result use an optional or null-style result for this case.

### Single-element array

For `[42]`, the only non-empty subarray is `[42]`.

Maximum and minimum subarray values are both 42.

### All-negative array

The maximum non-empty subarray is the least negative element.

### All-positive array

For maximum-sum problems, the complete array is generally optimal.

For minimum-sum problems, the smallest individual value may be optimal.

### Zeros

Zeros can create many different subarrays with the same sum.

For example, `[0, 0, 0]` contains six non-empty subarrays and all have sum zero.

Hash-based frequency counting must therefore store counts rather than merely whether a prefix sum has occurred.

### Duplicate values

Duplicates can affect frequency-map logic and pair problems.

A two-sum hash map must be able to distinguish different positions when the same value appears multiple times.

### Window larger than the array

A fixed-size sliding-window implementation should reject an invalid window size rather than silently return an incorrect value.

### Negative values in sliding windows

A sliding-window algorithm designed for positive values should not be applied to arbitrary integers.

The implementations explicitly validate the assumptions for such functions.

## Common mistakes

### Treating a subsequence as a subarray

A subarray must be contiguous.

### Recomputing sums unnecessarily

Calling `sum()` for every possible range produces unnecessary repeated work.

An incremental sum or prefix sum is usually more appropriate.

### Using a sliding window with arbitrary negative values

The standard monotonic-sum reasoning may no longer hold.

### Forgetting the empty-prefix entry

For prefix-sum hashing, initializing the frequency of prefix sum zero to one is essential.

It represents a subarray beginning at index zero.

### Storing the latest prefix position for a longest-range problem

For longest exact-sum problems, the earliest occurrence is normally required.

### Initializing Kadane's answer to zero

This incorrectly handles all-negative arrays when the problem requires a non-empty subarray.

### Sorting when original indices matter

Sorting changes positions.

If the answer requires original indices, a hash-based method or indexed records may be more appropriate.

### Ignoring integer overflow

The C++ implementation uses `long long` for accumulated sums because the sum of many integer values can exceed the range of a typical 32-bit integer.

### Ignoring JavaScript numeric limits

JavaScript's ordinary `Number` uses IEEE-754 double precision. Very large integer calculations can lose exact integer precision beyond the safe integer range. The examples use ordinary practical integer sizes, but applications involving very large financial or scientific integer values may require `BigInt` or another numeric representation.

## Testing strategy

The implementations use several levels of verification.

The Python implementation compares the `O(n^2)` maximum-subarray reference implementation with Kadane's `O(n)` algorithm.

This is a useful engineering technique:

- Write a simple trusted reference implementation.
- Write the optimized implementation.
- Compare their outputs across representative cases.

The JavaScript and C++ versions include assertion-based tests for important algorithms.

Test categories include:

- Empty arrays
- Single elements
- All-negative arrays
- Zero-heavy arrays
- Mixed positive and negative values
- Invalid windows
- Exact target sums
- Pair-sum cases
- Circular arrays
- Interval merging

## Python implementation

The Python script is structured as a progressive algorithm laboratory.

Important components include:

- `enumerate_subarrays()`
- `build_prefix_sum()`
- `range_sum()`
- `subarray_sum_equals_k_hashing()`
- `two_sum_hashing()`
- `two_pointer_pair_sum_sorted()`
- `maximum_sum_fixed_window()`
- `minimum_size_subarray_sum_positive()`
- `longest_subarray_at_most_k_distinct()`
- `maximum_subarray_kadane()`
- `minimum_subarray_kadane()`
- `maximum_circular_subarray()`
- `longest_subarray_sum_k()`
- `subarray_divisible_by_k_count()`
- `merge_intervals()`

Python is particularly suitable for demonstrating these algorithms because list operations, dictionaries, type annotations, data classes, and exception handling make the algorithmic structure compact and readable.

The Python implementation also includes a practical cash-flow example in which daily changes are treated as array values and Kadane's algorithm identifies the strongest contiguous period.

## JavaScript implementation

The JavaScript file uses standard language facilities without external packages.

The primary data structures include:

- Arrays
- `Map`
- Objects
- Numeric values

JavaScript's `Map` is especially useful for prefix-sum frequencies because it provides explicit key-value semantics and avoids relying on object-property coercion.

The JavaScript implementation includes:

- Prefix-sum range queries
- Hash-based exact-sum counting
- Longest exact-sum subarrays
- Divisibility using normalized remainders
- Hash-based two-sum
- Two pointers
- Fixed and variable sliding windows
- Frequency-map windows
- Kadane's maximum and minimum subarray algorithms
- Circular maximum subarray
- Sorting-based interval merging
- Assertions and validation

JavaScript is also useful for array-pattern learning because these techniques map directly to application-level data processing and browser or server-side JavaScript workloads.

## C++ case study

The C++ implementation models a transaction analytics system.

Each transaction contains:

- A transaction identifier
- A signed amount

The system treats the sequence of transaction changes as an array.

The case study asks questions such as:

- What contiguous period produced the greatest net growth?
- What contiguous period produced the largest decline?
- How many contiguous periods have a specified net change?
- What is the best fixed-length period?
- What happens when values wrap around circularly?

### C++ architecture

The system is divided into several components.

`Transaction` represents an individual transaction.

`SubarrayResult` represents an identified range and its aggregate value.

`PrefixSumIndex` encapsulates prefix-sum construction and range queries.

`TransactionAnalytics` provides domain-level operations over transaction data.

Algorithmic functions remain independent from the business object so that they can be tested separately.

This separation makes the implementation easier to reason about and supports reuse.

## C++ prefix-sum design

`PrefixSumIndex` stores an array of cumulative values.

The constructor builds the prefix representation in `O(n)`.

The `rangeSum()` method then answers an inclusive range query in `O(1)`.

The class demonstrates a useful production design principle: preprocessing can be encapsulated behind a dedicated abstraction rather than exposing implementation details throughout the application.

## C++ hashing design

The C++ implementation uses `std::unordered_map` for prefix-sum frequency tables.

The expected average lookup complexity is `O(1)`.

The implementation reserves capacity based on the input size to reduce the likelihood of repeated hash-table reallocation.

Hash-table performance can still depend on implementation details and collision behavior, so average complexity should not be interpreted as an absolute worst-case guarantee.

## C++ two-pointer design

The two-pointer implementation explicitly verifies that the input is sorted.

This is an important defensive programming practice.

The algorithm's correctness depends on the ordering invariant:

- Moving the left pointer increases the candidate sum.
- Moving the right pointer decreases the candidate sum.

If the input is unsorted, these statements are no longer guaranteed.

The higher-level `sortedPairSum()` function therefore sorts the data first when necessary.

## C++ sliding-window design

The fixed-window algorithm maintains one aggregate value.

When the window moves:

`new_sum = old_sum + incoming_value - outgoing_value`

This prevents repeated summation.

The variable-size positive-window algorithm relies on the fact that all values are strictly positive.

Input validation makes that assumption explicit instead of leaving correctness dependent on undocumented caller behavior.

## C++ transaction analytics

The `TransactionAnalytics` class converts transaction objects into their numeric amount sequence.

It then delegates array analysis to reusable algorithms.

This produces a useful distinction between:

- Domain modeling
- Algorithm implementation
- Validation
- Presentation

A production system could replace console output with database persistence, an API, a message-processing layer, or another interface without fundamentally changing the array algorithms.

## Complexity considerations

The major algorithms have different scalability characteristics.

### Explicit enumeration

There are `O(n^2)` possible subarray ranges.

If every range is materialized, the total copied data can become cubic in the worst case.

### Prefix sums

Building:

`O(n)`

Range query:

`O(1)`

Memory:

`O(n)`

### Prefix sum plus hashing

Average:

`O(n)`

Memory:

`O(n)`

This is often the preferred approach for exact-sum counting when negative values are allowed.

### Two pointers on sorted input

Scanning:

`O(n)`

Additional working memory:

`O(1)`

If sorting is necessary:

`O(n log n)` total time.

### Fixed sliding window

Time:

`O(n)`

Extra working memory:

`O(1)`

### Variable sliding window

When the window invariant is valid, each element enters and leaves the window at most once.

Time:

`O(n)`

### Kadane's algorithm

Time:

`O(n)`

Extra working memory:

`O(1)`

The range boundaries require only a few integer variables.

## Performance considerations

Algorithm selection matters more than micro-optimizing individual statements.

An `O(n^2)` algorithm may be perfectly suitable for a small educational input and completely inappropriate for millions of elements.

For example, an array of length 10,000 contains approximately:

`50,005,000`

non-empty subarrays.

Explicit enumeration is therefore expensive even before the contents of those ranges are copied.

Kadane's algorithm, by contrast, performs one primary pass over the same data.

Prefix sums and hashing also replace repeated range scanning with constant-time or average constant-time operations after preprocessing.

## Memory considerations

Different techniques trade memory for speed.

A brute-force algorithm can use little auxiliary memory if it processes one range at a time, but its running time can be large.

Prefix sums use `O(n)` memory to make range queries constant time.

Hashing uses `O(n)` memory to store prefix frequencies.

Two pointers and Kadane's algorithm can use `O(1)` auxiliary memory.

There is no universally optimal memory strategy. The required output and workload determine the appropriate trade-off.

## Security and robustness considerations

Array algorithms are generally not security-sensitive by themselves, but production implementations should still validate input.

Relevant considerations include:

- Reject invalid window sizes.
- Reject malformed ranges.
- Validate assumptions such as positivity or non-negativity.
- Guard against integer overflow in fixed-width languages.
- Avoid uncontrolled memory allocation for extremely large enumerations.
- Avoid trusting input ordering when an algorithm requires sorted data.
- Consider hash-table behavior for adversarial inputs in security-sensitive systems.
- Use appropriate numeric representations for large financial values.

The C++ implementation uses `long long` rather than ordinary 32-bit integers for aggregate sums.

The JavaScript implementation explicitly normalizes negative modulo results for divisibility calculations.

## Important algorithm-selection rules

When a problem asks for all contiguous ranges, first determine whether the input is small enough for enumeration.

When many static range-sum queries exist, consider prefix sums.

When the problem asks for an exact target sum and negative values are allowed, prefix sums with hashing are a strong pattern.

When the array is sorted and the problem compares values from opposite ends, consider two pointers.

When the window has a fixed number of elements, consider a fixed sliding window.

When values are positive or non-negative and the condition changes monotonically as the window expands, consider a variable sliding window.

When the task is maximum or minimum contiguous sum, Kadane's algorithm is usually the fundamental linear-time pattern.

When ordering can simplify the problem and original positions do not need to be preserved, sorting may enable a simpler two-pointer solution.

## Practical applications

These patterns appear in many technical systems.

### Financial analytics

Daily profit or loss changes can be represented as an array.

Maximum subarray analysis can identify the strongest contiguous period.

Minimum subarray analysis can identify the largest contiguous decline.

### Monitoring systems

A sequence of measurements can be analyzed using fixed windows to detect periods of unusually high or low activity.

### Log analysis

Contiguous events can be grouped and searched for periods satisfying cumulative constraints.

### Network telemetry

Sliding windows can track packet counts, throughput, latency events, or threshold violations.

### Time-series analysis

Prefix sums can accelerate repeated range calculations.

### Resource utilization

Fixed and variable windows can detect sustained load periods.

### Transaction systems

The C++ case study demonstrates how transaction changes can be treated as an array while keeping domain objects separate from algorithm implementations.

## Implementation distinctions across the three languages

### Python

Python emphasizes algorithm readability.

Dictionaries naturally implement frequency tables and prefix-sum maps.

Lists make array transformations concise.

Type annotations and data classes provide structure while retaining relatively compact code.

### JavaScript

JavaScript uses arrays and `Map` for the core data structures.

The language is especially suitable for application-facing array processing.

The implementation also demonstrates a JavaScript-specific issue with the remainder operator for negative numbers.

### C++

C++ provides explicit control over data structures and memory.

The case study uses:

- `vector`
- `unordered_map`
- `optional`
- Classes
- Exceptions
- Assertions
- `long long`

The C++ implementation makes algorithmic assumptions explicit through validation and separates the domain model from algorithmic services.

## Numerical considerations

Subarray algorithms often accumulate many values.

If an array contains large numbers, the aggregate may exceed the range of the element type.

Python integers automatically support arbitrary-precision integer arithmetic.

JavaScript `Number` provides exact integer representation only within its safe integer range.

C++ uses `long long` in the examples, but even `long long` has a finite range.

For production systems, numeric requirements should therefore be part of the design rather than an afterthought.

## Design principles demonstrated

The implementations illustrate several general algorithm-engineering principles:

1. Identify the mathematical structure of the problem.
2. State the assumptions required by an algorithm.
3. Choose an invariant that can be maintained efficiently.
4. Avoid repeated computation.
5. Separate preprocessing from repeated queries when appropriate.
6. Preserve the information needed by the requested output.
7. Validate assumptions at system boundaries.
8. Compare optimized implementations with simpler reference implementations.
9. Test edge cases explicitly.
10. Consider both time and space complexity.

These principles are more general than any single subarray algorithm.

## Final algorithm reference

| Problem | Typical technique | Complexity |
|---|---|---:|
| Enumerate all subarrays | Nested boundaries | `O(n²)` ranges |
| Calculate all sums incrementally | Nested boundaries + running sum | `O(n²)` |
| Static range-sum queries | Prefix sums | Build `O(n)`, query `O(1)` |
| Count exact-sum subarrays | Prefix sum + hash map | Average `O(n)` |
| Longest exact-sum subarray | Prefix sum + earliest index | Average `O(n)` |
| Two-sum on arbitrary input | Hash map | Average `O(n)` |
| Pair sum on sorted input | Two pointers | `O(n)` |
| Pair sum after sorting | Sort + two pointers | `O(n log n)` |
| Maximum fixed-length sum | Sliding window | `O(n)` |
| Minimum positive-sum window | Variable sliding window | `O(n)` |
| At-most-k distinct values | Frequency-map window | Average `O(n)` |
| Maximum subarray | Kadane | `O(n)` |
| Minimum subarray | Inverted Kadane | `O(n)` |
| Circular maximum subarray | Kadane + minimum subarray | `O(n)` |
| Divisible subarray counting | Prefix remainder frequencies | Average `O(n)` |
| Interval merging | Sorting + linear scan | `O(n log n)` |

The central lesson of Day 18 is that a subarray problem is rarely solved efficiently by examining every range independently. The strongest solutions exploit structure: cumulative sums, frequency information, ordering, boundary movement, or a recurrence that summarizes the best state ending at the current position.
