# Day 17 — Kadane's Algorithm

## Topic overview

Kadane's algorithm is a linear-time dynamic programming technique for solving the maximum-subarray problem.

Given an array of integers, the standard problem asks for the maximum possible sum of a **non-empty contiguous subarray**.

For example, in:

`[-2, 1, -3, 4, -1, 2, 1, -5, 4]`

the maximum-sum subarray is:

`[4, -1, 2, 1]`

and its sum is `6`.

The important property is contiguity. A subarray must occupy consecutive positions. This distinguishes the problem from a subsequence problem, where elements can be skipped.

This topic develops several closely related techniques:

- maximum subarray
- running sums
- reset decisions
- negative values
- index reconstruction
- minimum subarray
- circular maximum subarray
- maximum subarray with deletion
- fixed-length maximum windows
- prefix-sum interpretation
- streaming computation
- algorithmic invariants
- testing and verification
- complexity analysis
- practical system applications

The three implementations approach the topic differently:

- Python provides a broad algorithmic study with multiple variants and verification techniques.
- JavaScript demonstrates the algorithms in a practical executable environment, including iterable and streaming patterns.
- C++ develops an industry-style service-health analysis system using explicit data structures, validation, testing, and modular design.

---

## Fundamental terminology

### Array

An array is an ordered collection of values accessed by index.

For example:

`[4, -2, 7, 3]`

has four elements with indices `0` through `3`.

### Subarray

A subarray is a contiguous part of an array.

For:

`[4, -2, 7, 3]`

valid subarrays include:

- `[4]`
- `[-2]`
- `[7, 3]`
- `[4, -2, 7]`
- `[4, -2, 7, 3]`

`[4, 7]` is not a subarray because `-2` lies between them.

### Subsequence

A subsequence preserves relative order but does not require contiguity.

For:

`[4, -2, 7, 3]`

`[4, 7]` is a subsequence but not a subarray.

Kadane's algorithm solves a contiguous-subarray problem.

### Prefix

A prefix is a segment beginning at the first element.

For:

`[4, -2, 7, 3]`

possible prefixes are:

- `[4]`
- `[4, -2]`
- `[4, -2, 7]`
- `[4, -2, 7, 3]`

### Suffix

A suffix is a segment ending at the final element.

For the same array:

- `[3]`
- `[7, 3]`
- `[-2, 7, 3]`
- `[4, -2, 7, 3]`

### Running sum

A running sum is an accumulated value updated as elements are processed.

For:

`[3, -2, 5]`

the running sums are:

- `3`
- `1`
- `6`

Running sums are important because repeatedly calculating every subarray sum from scratch creates unnecessary work.

---

## The maximum-subarray problem

The standard problem can be written mathematically as:

Given an array `A` of length `n`, find indices `i` and `j` such that:

`0 <= i <= j < n`

and:

`A[i] + A[i+1] + ... + A[j]`

is as large as possible.

The subarray is normally required to be non-empty.

That last condition matters.

For:

`[-8, -3, -10]`

the correct answer is `-3`.

Returning `0` would mean selecting no elements. That solves a different problem.

---

## Brute-force approach

The most direct method examines every possible subarray.

There are:

`n(n + 1) / 2`

non-empty contiguous subarrays.

This is `O(n^2)` possible subarrays.

If every subarray is summed by scanning all of its elements, the total complexity becomes `O(n^3)`.

The Python implementation contains `maximum_subarray_cubic()`.

The C++ implementation contains `maximumSubarrayCubic()`.

The JavaScript implementation contains `maximumSubarrayCubic()`.

These functions are intentionally inefficient compared with Kadane's algorithm. Their primary purpose is to provide a simple reference implementation against which optimized algorithms can be tested.

---

## Running-sum optimization

The cubic method repeatedly recalculates sums.

For a fixed start index, the sum can instead be extended incrementally.

Suppose the current subarray is:

`[4, -1, 2]`

with sum `5`.

Adding the next value `3` produces:

`5 + 3 = 8`

There is no need to scan the entire subarray again.

This reduces the complexity from `O(n^3)` to `O(n^2)`.

The Python function is `maximum_subarray_quadratic()`.

The JavaScript function is `maximumSubarrayQuadratic()`.

The C++ function is `maximumSubarrayQuadratic()`.

The improvement demonstrates a general algorithmic principle:

> Reuse previously computed information instead of recomputing it.

---

## Kadane's algorithm

Kadane's algorithm observes that a maximum subarray ending at the current position has only two meaningful possibilities.

For the current value `x`:

1. Start a new subarray containing only `x`.
2. Extend the best subarray that ended at the previous position.

Therefore:

`current = max(x, current + x)`

The global answer is then updated with:

`best = max(best, current)`

This produces an `O(n)` algorithm.

The Python implementation is `kadane()`.

The JavaScript implementation is `kadane()`.

The C++ implementation is `kadane()`.

---

## The central invariant

The most important concept is the meaning of `current`.

At array position `i`:

`current`

represents the maximum possible sum of a **non-empty subarray that ends exactly at position `i`**.

`best` represents the maximum sum found anywhere from the beginning of the array through position `i`.

This distinction is critical.

`current` is constrained to end at the current position.

`best` is not.

For example, when processing:

`[-2, 1, -3, 4, -1, 2, 1]`

the current candidate changes at every position, while the global best remains the best value found so far.

---

## Reset decisions

The reset decision is the core operation.

Suppose the previous best subarray ending at the previous position has sum `current`.

The next value is `x`.

Two candidates exist:

`x`

and:

`current + x`

If:

`x > current + x`

then the previous subarray is harmful to the new candidate, so the algorithm starts again at `x`.

Otherwise, the current candidate is extended.

This can also be expressed as:

`current = max(x, current + x)`

The phrase "reset" does not mean the algorithm forgets the global answer. It only means that the best subarray ending at the current position begins again.

---

## Why negative values matter

Negative values are the main source of mistakes in beginner implementations.

Consider:

`[-8, -3, -10, -4]`

There is no positive-sum subarray.

The best non-empty choice is:

`[-3]`

with sum:

`-3`

An incorrect implementation often starts:

`current = 0`

and:

`best = 0`

Then it repeatedly applies:

`current = max(0, current + value)`

That implementation returns `0`.

It is correct only when an empty selection is explicitly allowed.

For the standard non-empty maximum-subarray problem, initialization should use the first element:

`current = values[0]`

and:

`best = values[0]`

This is one of the most important implementation details in Kadane's algorithm.

---

## Example trace

For:

`[-2, 1, -3, 4, -1, 2, 1, -5, 4]`

the algorithm maintains two conceptual states.

| Index | Value | Best ending here | Global best |
|---:|---:|---:|---:|
| 0 | -2 | -2 | -2 |
| 1 | 1 | 1 | 1 |
| 2 | -3 | -2 | 1 |
| 3 | 4 | 4 | 4 |
| 4 | -1 | 3 | 4 |
| 5 | 2 | 5 | 5 |
| 6 | 1 | 6 | 6 |
| 7 | -5 | 1 | 6 |
| 8 | 4 | 5 | 6 |

The final answer is `6`.

The corresponding subarray is:

`[4, -1, 2, 1]`

---

## Index reconstruction

Sometimes the required result is not just the maximum sum.

A real application may need:

- the start index
- the end index
- the selected values
- the duration represented by the interval
- the associated records
- timestamps
- identifiers

The reset position therefore needs to be tracked.

The algorithm maintains:

- `current_start`
- `best_start`
- `best_end`

When a new subarray starts, `current_start` is updated.

When a new global best is discovered, the current range becomes the best range.

The Python result is represented by the `SubarrayResult` data class.

The JavaScript implementation returns an object.

The C++ implementation uses the `SubarrayResult` structure.

---

## Tie-breaking

Multiple subarrays can have the same maximum sum.

For example, an array can contain multiple single-element values with the same maximum.

The mathematical maximum is unchanged, but an application may need a deterministic rule.

Possible rules include:

- prefer the earliest occurrence
- prefer the latest occurrence
- prefer the shortest interval
- prefer the longest interval

The Python implementation demonstrates an explicit shorter-on-tie variant.

Tie-breaking should be treated as a separate requirement from maximizing the sum.

The primary optimization objective is the sum.

A tie-breaking policy determines which equally optimal range is selected.

---

## Minimum subarray

Kadane's reasoning can be inverted to find the minimum-sum subarray.

Instead of:

`max(value, current + value)`

use:

`min(value, current + value)`

The same invariant applies:

`current_min`

is the smallest sum of a non-empty subarray ending at the current position.

The Python function is `minimum_subarray()`.

The JavaScript function is `minimumSubarray()`.

The C++ function is `minimumSubarray()`.

This variant is particularly useful when solving circular-array problems.

---

## Maximum circular subarray

In a circular array, the end and beginning are connected.

For example:

`[5, -3, 5]`

A circular subarray can take:

`[5, 5]`

by wrapping around the boundary.

There are two possibilities:

1. The optimal subarray does not wrap.
2. The optimal subarray wraps.

The first case is ordinary Kadane.

For the wrapping case:

`wrapped_sum = total_sum - minimum_subarray_sum`

Why?

If the minimum-sum contiguous portion is removed from the middle, the remaining elements form the maximum wrapping interval.

For:

`[5, -3, 5]`

the total is:

`7`

The minimum subarray is:

`[-3]`

with sum:

`-3`

Therefore:

`7 - (-3) = 10`

which corresponds to the circular selection:

`[5, 5]`

A special case must be handled when all values are negative. Otherwise, removing the minimum subarray could remove the entire array and produce an empty result.

---

## Maximum subarray with one deletion

A more advanced variation permits one element to be removed.

The state can be expanded into two states:

### Keep state

The best sum ending at the current position without deleting an element.

### Deleted state

The best sum ending at the current position after deleting exactly one element.

The transitions are:

`new_keep = max(value, keep + value)`

and:

`new_deleted = max(deleted + value, keep)`

The second expression has two meanings:

- the deletion occurred earlier and the current value is kept
- the current value itself is deleted

This is a useful example of how Kadane's algorithm can evolve into a more general dynamic-programming state machine.

---

## At most k deletions

The one-deletion algorithm can be generalized.

Instead of maintaining two states:

- zero deletions
- one deletion

maintain:

- zero deletions
- one deletion
- two deletions
- ...
- `k` deletions

Let:

`dp[d]`

represent the best sum of a valid subarray ending at the current position after exactly `d` deletions.

For each value:

`dp[d] = max(previous_dp[d] + value, previous_dp[d - 1])`

The first choice keeps the value.

The second choice deletes the current value.

This produces:

- time: `O(nk)`
- auxiliary space: `O(k)`

The Python implementation is `maximum_subarray_k_deletions()`.

The JavaScript implementation is `maximumSubarrayKDeletions()`.

The C++ case study focuses on the simpler one-deletion form because it is sufficient to demonstrate state expansion without turning the main domain model into a generalized multidimensional problem.

---

## Fixed-length maximum subarray

A different problem asks:

> What is the maximum sum among all subarrays having exactly `k` elements?

This is not ordinary Kadane.

Every candidate has the same length.

A sliding window is appropriate.

For an initial window:

`[a, b, c]`

the sum is:

`a + b + c`

When the window moves one position:

- subtract the outgoing value
- add the incoming value

This provides:

- time: `O(n)`
- auxiliary space: `O(1)`

The implementations include this distinction because algorithm selection depends on the exact constraints of the problem.

---

## Prefix-sum interpretation

Kadane's algorithm can also be derived from prefix sums.

Define:

`P[i] = sum of the first i elements`

The sum of the subarray from `j` through `i - 1` is:

`P[i] - P[j]`

For a fixed ending position `i`, maximizing the subarray sum means minimizing the prefix sum `P[j]` that occurred earlier.

Therefore, while scanning:

1. maintain the current prefix sum
2. maintain the smallest prefix sum seen so far
3. calculate the difference
4. update the maximum

This produces an `O(n)` solution.

The Python function is `maximum_subarray_prefix_sum()`.

The JavaScript function is `maximumSubarrayPrefixSum()`.

The C++ function is `maximumSubarrayPrefixSum()`.

This derivation shows that Kadane's algorithm is closely related to prefix-sum optimization.

---

## Divide-and-conquer formulation

The maximum subarray can also be solved by divide and conquer.

For a range divided around a midpoint, the optimal subarray must be one of:

1. entirely in the left half
2. entirely in the right half
3. crossing the midpoint

The crossing case is found by:

- scanning left from the midpoint
- finding the best suffix of the left half
- scanning right from the midpoint
- finding the best prefix of the right half
- combining the two

The resulting complexity is:

- time: `O(n log n)`
- recursion stack: `O(log n)`

This is asymptotically slower than Kadane's `O(n)` solution, but it is valuable because it demonstrates a different problem-solving strategy.

The Python implementation is `maximum_subarray_divide_and_conquer()`.

---

## Streaming Kadane

Kadane's algorithm does not need to retain the complete array when only the maximum sum is required.

The necessary state is small:

- current sum
- best sum
- current start index
- best start index
- best end index
- current position

The Python `StreamingKadane` class and JavaScript `StreamingKadane` class demonstrate this pattern.

The C++ implementation also contains a `StreamingKadane` class.

This is useful for data sources such as:

- telemetry
- logs
- event streams
- sensor measurements
- time-series processing
- large files
- message streams

The key limitation is that if the actual values or records belonging to the final subarray must be recovered later, the system needs an appropriate retention strategy.

---

## Python implementation

The Python implementation is designed as a comprehensive algorithm laboratory.

### Core implementation

The function `kadane()` demonstrates the fundamental two-state logic:

`current_sum = max(value, current_sum + value)`

followed by:

`best_sum = max(best_sum, current_sum)`

### Data modeling

The `SubarrayResult` data class stores:

- total
- start
- end
- values

It also exposes a `length` property.

This makes algorithm results explicit rather than returning an unstructured collection of unrelated values.

### Variants

The Python file implements:

- cubic brute force
- quadratic running sum
- standard Kadane
- index reconstruction
- reset tracing
- tie-breaking
- minimum subarray
- circular maximum subarray
- one deletion
- k deletions
- fixed-length windows
- constrained sliding-window processing
- prefix-sum formulation
- divide and conquer
- streaming computation

### Verification

The Python file compares several independent implementations.

The randomized verification generates many small arrays and checks that:

- cubic brute force
- quadratic running sum
- Kadane
- prefix-sum processing
- divide and conquer

produce the same maximum sum.

This is a form of differential testing.

It is especially useful for algorithms where multiple implementations can be independently derived.

---

## JavaScript implementation

The JavaScript implementation emphasizes executable application-level patterns.

### Arrays and objects

JavaScript arrays provide the basic sequence structure.

Results are represented using objects such as:

`{ sum, start, end, values }`

This is convenient for applications that consume algorithmic results as structured data.

### Validation

The implementation validates:

- array type
- non-empty input
- numeric values
- integer constraints where required
- window length constraints
- deletion count constraints

Validation prevents silent failures and makes incorrect assumptions explicit.

### Iterable processing

The JavaScript implementation includes `numberGenerator()` and `kadaneFromIterable()`.

This demonstrates that the algorithm can process an iterable rather than requiring a conventional array.

This is particularly relevant to JavaScript because the language provides a broad iterable protocol used by arrays, generators, maps, sets, and custom iterable objects.

### Streaming state

`StreamingKadane` maintains the minimum state necessary for incremental processing.

This provides a bridge between a textbook algorithm and event-driven application processing.

### Runtime performance

The JavaScript implementation also processes a large generated array to demonstrate that an `O(n)` scan is suitable for substantially larger inputs than a cubic reference algorithm.

---

## C++ case study

The C++ implementation models an infrastructure monitoring scenario.

### Problem being solved

A service produces a sequence of normalized changes in a health or performance score.

Positive values represent improvements.

Negative values represent deterioration.

The system needs to identify:

- the strongest contiguous improvement interval
- the strongest contiguous deterioration interval
- circular improvement periods
- the effect of one anomalous observation
- fixed-size monitoring windows
- results while data arrives incrementally

The values are abstract so that the algorithm is separated from a particular monitoring vendor or telemetry system.

### `SubarrayResult`

The `SubarrayResult` structure stores:

- `sum`
- `start`
- `end`

The `length()` method derives the interval size.

This separates algorithmic output from the surrounding service-analysis logic.

### `ServiceHealthAnalyzer`

The `ServiceHealthAnalyzer` class provides domain-level operations:

- `strongestImprovement()`
- `strongestDeterioration()`
- `improvementScore()`

These functions delegate to reusable algorithmic implementations.

This separation is important in larger systems because business or domain logic should not be tightly coupled to low-level array processing.

---

## C++ architecture

The C++ program is divided into several layers.

### Validation layer

`validateNonEmpty()` enforces the fundamental non-empty-input assumption.

### Reference algorithms

The cubic and quadratic implementations provide independently structured baselines.

### Optimized algorithm

`kadane()` provides the production-oriented linear-time solution.

### Specialized algorithms

The program contains:

- minimum subarray
- circular maximum subarray
- one-deletion maximum subarray
- fixed-length maximum subarray
- prefix-sum maximum subarray

### Streaming component

`StreamingKadane` provides incremental processing.

### Domain component

`ServiceHealthAnalyzer` gives the algorithms a realistic operational context.

### Testing component

Deterministic tests and randomized differential verification check correctness.

This modular organization makes the algorithm reusable without mixing every concern into a single function.

---

## Algorithmic complexity

| Algorithm | Time | Auxiliary space |
|---|---:|---:|
| Cubic brute force | `O(n^3)` | `O(1)` |
| Quadratic running sum | `O(n^2)` | `O(1)` |
| Kadane | `O(n)` | `O(1)` |
| Prefix-sum scan | `O(n)` | `O(1)` |
| Divide and conquer | `O(n log n)` | `O(log n)` recursion |
| Circular Kadane | `O(n)` | `O(1)` apart from returned values |
| One-deletion DP | `O(n)` | `O(1)` |
| k-deletion DP | `O(nk)` | `O(k)` |
| Fixed-length sliding window | `O(n)` | `O(1)` |

Kadane's linear complexity is the main reason it is preferred for the standard maximum-subarray problem.

The algorithm examines every element once.

---

## Space considerations

The basic Kadane algorithm requires only a constant number of scalar variables.

It does not require:

- a prefix-sum array
- a table of all subarrays
- a dynamic-programming matrix
- recursion
- copying every candidate subarray

Therefore:

`O(1)`

auxiliary space is possible.

The situation changes when the application needs to return the actual subarray values.

The result itself can require `O(n)` storage in the worst case.

This distinction is important:

- algorithmic working memory can be `O(1)`
- output storage can still be `O(n)`

---

## Integer overflow

The theoretical recurrence is simple, but real implementations must consider numeric limits.

For example, adding two very large signed integers can overflow a fixed-width integer type.

The C++ implementation uses `long long`, which provides a wider range than a typical 32-bit integer.

A production system should still validate that the expected input range fits within the selected type.

If values may exceed the range, alternatives include:

- a wider integer representation
- checked arithmetic
- arbitrary-precision arithmetic
- domain-specific scaling

Python integers automatically expand to arbitrary precision, subject to available memory.

JavaScript's ordinary `Number` type is floating-point and represents integers exactly only within its safe integer range. For extremely large integer values, JavaScript's `BigInt` may be more appropriate, although mixing `Number` and `BigInt` requires explicit handling.

---

## Negative values and empty arrays

These two conditions should not be confused.

An empty array means there is no valid non-empty subarray.

An all-negative array contains valid candidates, but every candidate has a negative sum.

Therefore:

- empty input should generally raise an error or be handled according to an explicit API contract
- all-negative input should return the largest individual negative value for the standard problem

For example:

`[-9, -4, -12]`

returns:

`-4`

because `[-4]` is the highest-sum non-empty contiguous subarray.

---

## Common mistakes

### Initializing the answer to zero

This incorrectly permits an empty subarray.

Use the first element when the specification requires a non-empty result.

### Confusing subarray and subsequence

A subarray must be contiguous.

### Returning only the sum when indices are required

Track the current start and best range if the actual interval matters.

### Resetting whenever the current sum becomes negative

This is a useful intuition, but the exact recurrence is safer:

`max(value, current + value)`

A negative current sum may still interact with later values in ways that make explicit state reasoning preferable.

### Mishandling all-negative arrays in circular Kadane

The circular formula must not be allowed to select an empty result.

### Applying sliding windows to arbitrary negative data

Many sliding-window techniques depend on non-negative values or another monotonicity property.

Negative numbers can invalidate those assumptions.

### Using `O(n^2)` logic when `O(n)` is required

A correct answer is not sufficient when the input constraints make the slower algorithm impractical.

---

## Edge cases

Important test cases include:

### One element

`[7]`

Answer:

`7`

### One negative element

`[-7]`

Answer:

`-7`

### All positive

`[2, 4, 1, 8]`

The complete array is optimal.

### All negative

`[-8, -3, -10, -4]`

Answer:

`-3`

### All zeros

`[0, 0, 0]`

The maximum sum is `0`.

Tie-breaking determines which zero interval is returned when indices are required.

### Large negative separator

`[5, -100, 6, 7]`

The algorithm should not allow the large negative value to remain inside the best candidate.

### Alternating values

`[10, -10, 10, -10, 10]`

This tests tie handling and extension behavior.

### Empty input

The implementation treats this as invalid for the standard non-empty maximum-subarray problem.

---

## Maximum subarray versus related problems

| Problem | Typical technique |
|---|---|
| Maximum arbitrary subarray sum | Kadane |
| Minimum arbitrary subarray sum | Inverted Kadane |
| Maximum circular subarray | Kadane + minimum subarray |
| Maximum subarray with one deletion | Two-state DP |
| Maximum subarray with k deletions | `O(nk)` DP |
| Maximum fixed-length sum | Sliding window |
| Longest non-negative subarray under sum limit | Sliding window |
| Maximum subarray from prefix representation | Prefix-sum minimum tracking |
| Maximum subarray using structural recursion | Divide and conquer |

The important lesson is that similar-looking array problems can require different algorithms.

The exact constraints determine the state and recurrence.

---

## Dynamic programming interpretation

Kadane's algorithm is often described as dynamic programming because it stores the best result for a smaller subproblem and uses it to construct the next result.

The state can be written as:

`dp[i] = maximum sum of a non-empty subarray ending at i`

The recurrence is:

`dp[i] = max(A[i], dp[i-1] + A[i])`

The global answer is:

`max(dp[i])`

A complete DP table is unnecessary because `dp[i]` only depends on `dp[i-1]`.

Therefore the state can be compressed to one variable.

This is a standard example of **space optimization in dynamic programming**.

---

## Why state compression works

A conventional dynamic-programming solution might conceptually store:

`dp[0], dp[1], dp[2], ..., dp[n-1]`

But the recurrence only needs the previous state.

Therefore:

`previous_dp`

can be replaced by:

`current_sum`

This reduces auxiliary memory from `O(n)` to `O(1)`.

The same principle appears throughout algorithm design:

> If a state depends only on a small fixed number of previous states, the complete table may not be necessary.

---

## Streaming and online processing

Kadane is naturally suited to online processing.

Each incoming value can update:

- the best subarray ending at the current position
- the best global result

without rescanning previous values.

This makes the technique relevant to:

- telemetry pipelines
- streaming analytics
- real-time monitoring
- financial time-series analysis
- sensor systems
- event processing
- operational dashboards

The mathematical algorithm does not depend on the source of the data.

The source could be:

- a vector
- a file
- a generator
- a network stream
- a database cursor
- a message queue

The surrounding system determines how values are produced and retained.

---

## Security considerations

Kadane's algorithm itself is not a security mechanism.

Security considerations arise from the data and system surrounding it.

### Input validation

Applications should validate:

- input type
- empty input
- numeric ranges
- unexpected values
- malformed records

### Resource limits

Although Kadane uses constant working memory, other parts of an application may materialize a complete input array.

For untrusted or very large data, streaming processing can reduce memory pressure.

### Numeric safety

Extreme numeric values should be handled according to the numeric type's limits.

### Denial-of-service considerations

An algorithm with `O(n)` processing is substantially more resistant to computational abuse than an `O(n^3)` implementation when large input is accepted.

Input size limits may still be appropriate in systems exposed to untrusted clients.

### Data provenance

If the array represents operational, financial, user, or sensor data, the algorithm should not be treated as a substitute for validation, anomaly detection, or source verification.

---

## Debugging considerations

A useful debugging strategy is to expose the algorithm's state.

For each element, inspect:

- current value
- current candidate sum
- global best sum
- current candidate start
- best start
- best end
- reset or extension decision

The Python and C++ implementations provide trace-oriented demonstrations.

For a failing example, manually verify:

1. the current value
2. the previous current sum
3. the two competing candidates
4. the reset decision
5. the global best update

This often reveals initialization or indexing errors quickly.

---

## Testing strategy

A robust implementation should test more than the classic example.

### Deterministic tests

Useful deterministic categories include:

- one positive
- one negative
- all positive
- all negative
- zeros
- alternating signs
- large negative separators
- duplicate maxima
- empty input
- invalid window sizes

### Differential testing

The implementations compare Kadane against slower but simpler reference algorithms.

For small arrays, a brute-force implementation is practical.

If:

`brute_force(values) != kadane(values)`

then at least one implementation contains an error.

### Randomized testing

Randomized arrays containing positive, negative, and zero values expose combinations that are easy to overlook in hand-written examples.

The Python, JavaScript, and C++ implementations include randomized verification or deterministic equivalents.

---

## Practical applications

Kadane's algorithm is a general optimization pattern rather than a domain-specific trading or monitoring technique.

Potential applications include:

### Time-series analysis

Find the strongest contiguous improvement or deterioration interval.

### Monitoring

Identify a continuous period during which a metric accumulated the largest net improvement.

### Finance

Analyze contiguous periods of gains or losses in transformed price-change data.

A maximum-subarray calculation alone is not a complete trading strategy.

### Sensor analytics

Identify the strongest sustained cumulative movement in a sequence of sensor changes.

### Performance analysis

Find the contiguous interval with the largest accumulated change in a normalized performance metric.

### Operations

Detect the strongest continuous period of improvement or deterioration in a derived score.

### Resource utilization

Analyze changes in capacity, utilization, or demand over contiguous periods.

The meaning of the values must be defined by the application. Kadane supplies the optimization mechanism.

---

## Python, JavaScript, and C++ distinctions

### Python

Python is particularly effective for algorithm study because the syntax is concise and the standard library provides useful testing and data-modeling facilities.

The Python implementation emphasizes:

- educational clarity
- multiple algorithmic variants
- data classes
- randomized verification
- readable reference implementations
- streaming state

### JavaScript

JavaScript adds useful perspectives around:

- arrays and objects
- iterable protocols
- generators
- application-oriented validation
- runtime execution
- streaming-style processing

The JavaScript implementation demonstrates how the same algorithm can operate over arrays and custom iterable sources.

### C++

C++ is useful for demonstrating:

- explicit data structures
- value semantics
- standard-library containers
- strong control over numeric types
- exception-based validation
- modular system design
- performance-conscious implementation

The C++ case study places the algorithm inside a domain-oriented service-health analyzer.

---

## Implementation design principles

Several general software-engineering principles appear throughout the implementations.

### Separate algorithm from domain logic

The core maximum-subarray function does not need to know whether values represent:

- sensor readings
- financial changes
- service metrics
- scores
- physical measurements

The domain layer interprets the result.

### Keep invariants explicit

A function should have a clear statement of what each state variable means.

### Validate assumptions

If an algorithm requires:

- non-empty input
- positive window size
- non-negative values

those requirements should be explicit.

### Use reference implementations

A slower implementation can serve as an executable specification for testing a faster implementation.

### Return structured results when appropriate

When callers need indices and values, returning only a number is insufficient.

### Keep variants separate

Circular arrays, deletion variants, and fixed-size windows have different state requirements. Treating them as separate algorithms avoids hidden assumptions.

---

## Performance considerations

Kadane's algorithm requires one pass through the data.

For an input of size `n`:

`T(n) = O(n)`

The auxiliary state is constant:

`S(n) = O(1)`

This is optimal in the standard comparison model because every element may affect the answer, so the input generally has to be examined.

The cubic implementation becomes impractical quickly.

For example, increasing input size by a factor of ten can increase the approximate number of cubic operations by a factor of one thousand.

The linear algorithm grows proportionally with input size.

---

## Numerical precision

For integer data, exact arithmetic is usually preferred.

Python provides arbitrary-precision integers.

C++ requires selecting an appropriate integer type.

JavaScript's `Number` type uses IEEE 754 floating-point representation.

For ordinary values, `Number` is convenient and efficient.

For integer values outside the safe exact-integer range, JavaScript applications may need `BigInt`.

If floating-point measurements are used, comparison behavior can be affected by rounding.

For example, values that are mathematically equal may not be represented by exactly equal floating-point values.

Production systems should define acceptable numerical error according to the domain.

---

## Constraints and limitations

Kadane solves a specific class of optimization problem.

It does not automatically solve:

- maximum product subarray
- longest subarray under arbitrary constraints
- maximum subarray with arbitrary penalties
- multidimensional maximum subarray
- arbitrary subsequence optimization
- fixed-size problems more efficiently than a suitable sliding window
- problems requiring complex external constraints

The recurrence must match the problem definition.

Changing the objective or constraints can require a different state representation.

---

## Important distinction: sum versus actual interval

Two different outputs may be required.

### Maximum sum only

Only `best_sum` is needed.

This can be maintained with constant auxiliary state.

### Maximum sum plus interval

The implementation must track:

- current start
- best start
- best end

### Maximum sum plus original records

If the original records are large objects, retaining the entire selected interval can consume substantial memory.

A production system may instead retain:

- identifiers
- offsets
- timestamps
- indices

and retrieve detailed records only when required.

---

## Algorithmic reasoning pattern

Kadane's algorithm illustrates a reusable reasoning process.

### Identify the local state

Ask:

> What is the best solution that must end at the current position?

### Identify the choices

For each value:

- start here
- extend the previous candidate

### Write the recurrence

`current = max(value, current + value)`

### Track the global result

`best = max(best, current)`

### Check boundary conditions

Ask:

- Is the input empty?
- Is an empty solution allowed?
- Can all values be negative?
- Are indices required?
- Are values within numeric limits?

### Optimize memory

If the recurrence uses only the previous state, retain only that state.

This reasoning style applies to many dynamic-programming problems beyond maximum subarray.

---

## Reference implementations in the repository

The three implementations are intentionally related but not identical.

### Python

The Python file functions as a broad study implementation and contains the largest collection of algorithmic variants.

### JavaScript

The JavaScript file emphasizes executable application behavior, iterables, generators, streaming state, and runtime-oriented validation.

### C++

The C++ file develops a service-health monitoring case study and demonstrates how the algorithm can be integrated into a modular system.

All three implementations contain complete executable logic rather than pseudocode.

---

## Core formulas

### Standard Kadane

`current = max(value, current + value)`

`best = max(best, current)`

### Minimum subarray

`current = min(value, current + value)`

`best = min(best, current)`

### Circular maximum

`max(normal_max, total_sum - minimum_subarray_sum)`

with an all-negative special case.

### One deletion

`keep = max(value, previous_keep + value)`

`deleted = max(previous_deleted + value, previous_keep)`

### Prefix-sum formulation

For prefix sums `P`:

`subarray_sum = P[right] - P[left]`

To maximize the difference, maintain the smallest prefix sum encountered before the current position.

---

## Practical checklist

When implementing a maximum-subarray solution:

- Confirm that the problem requires contiguity.
- Confirm whether the subarray must be non-empty.
- Decide whether only the sum or also the indices are required.
- Initialize correctly for all-negative arrays.
- Maintain the current best ending at the current position.
- Maintain the global best.
- Test single-element input.
- Test all-positive input.
- Test all-negative input.
- Test zero values.
- Test alternating positive and negative values.
- Test empty input behavior.
- Test large values for numeric safety.
- Compare against a brute-force reference on small random inputs.
- Use a variant-specific algorithm when the constraints change.
- Avoid unnecessary storage when processing large streams.

---

## Relationship to dynamic programming

Kadane's algorithm is a compact example of dynamic programming because it converts a global optimization problem into a sequence of local optimal states.

The full conceptual DP state is:

`dp[i] = best sum of a non-empty subarray ending at i`

The recurrence is:

`dp[i] = max(A[i], dp[i - 1] + A[i])`

The final answer is:

`max(dp[0], dp[1], ..., dp[n - 1])`

Because each state depends only on the previous state, the entire DP array can be compressed into one variable.

This demonstrates the relationship between:

- recurrence design
- state definition
- state transition
- global optimization
- space optimization

---

## Production considerations

A production implementation should separate algorithmic correctness from operational requirements.

Relevant considerations include:

- input validation
- numeric range validation
- handling empty streams
- logging
- deterministic tie-breaking
- monitoring processing latency
- memory management
- error handling
- testing
- concurrency strategy
- data retention
- input provenance
- overflow behavior
- API contracts

The algorithm itself is small, but the surrounding production system can be significantly more complex.

The C++ service-health case study demonstrates this separation by keeping the core algorithms independent from the domain-level analyzer.

---

## Final technical perspective

Kadane's algorithm is fundamentally about maintaining the best contiguous solution that ends at the current position while preserving the best solution found globally.

Its key ideas are compact:

- extend a useful candidate
- discard a harmful accumulated prefix
- preserve the global optimum
- initialize correctly for negative values
- compress the dynamic-programming state

The most important implementation detail is not the syntax. It is the state invariant:

`current` must represent the best non-empty subarray ending at the current position.

Once that invariant is correct, the recurrence naturally produces an `O(n)` solution with `O(1)` auxiliary state for the standard problem.
