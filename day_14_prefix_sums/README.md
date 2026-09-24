# Day 14 — Prefix sums

## Introduction

A prefix sum is a cumulative representation of an array. Instead of repeatedly adding the elements of a range, a prefix-sum array stores cumulative totals so that many range-sum queries can be answered in constant time after linear preprocessing.

For an array

`A = [a0, a1, a2, ..., an-1]`

a prefix-sum array with a leading zero is defined as

`P[0] = 0`

and

`P[i + 1] = P[i] + A[i]`.

Therefore, the sum of the inclusive range from `left` through `right` is

`P[right + 1] - P[left]`.

Prefix sums are more than a range-sum optimization. The same prefix-state idea can be combined with hash maps to solve subarray-counting problems, equilibrium-index problems, divisibility problems, longest-subarray problems, and several related algorithmic patterns.

This implementation set develops the subject through Python, JavaScript, and a C++ transaction-analytics case study.

---

## Fundamental concepts

### Prefix

A prefix is an initial portion of a sequence.

For:

`[4, 2, 7, 1]`

the prefixes are:

- `[4]`
- `[4, 2]`
- `[4, 2, 7]`
- `[4, 2, 7, 1]`

A prefix sum stores the sum associated with each prefix.

For the same array:

`[0, 4, 6, 13, 14]`

The leading zero represents the empty prefix.

### Prefix-sum array

For an input array `A`, the prefix array `P` satisfies:

`P[i] = A[0] + A[1] + ... + A[i - 1]`.

The index is deliberately shifted by one position. This representation removes special cases for ranges beginning at index zero.

For:

`A = [3, 1, 4, 2]`

the prefix array is:

`P = [0, 3, 4, 8, 10]`.

Thus:

`sum(1..3) = P[4] - P[1] = 10 - 3 = 7`.

---

## Why prefix sums are useful

Suppose an array contains `n` values and there are `q` range queries.

Without preprocessing, calculating every range sum directly may require scanning many elements. In the worst case, this produces approximately `O(nq)` work.

With prefix sums:

- preprocessing takes `O(n)`
- each range query takes `O(1)`
- `q` queries take `O(q)`
- total time becomes `O(n + q)`

The trade-off is additional memory of `O(n)` for the prefix array.

This is especially valuable when the underlying array is static or changes rarely while many queries are performed.

---

## Prefix-sum construction

The Python implementation uses `build_prefix_sum`.

For every input value, the running total is appended to the prefix array.

For example:

`[3, 1, 4, 2, 5]`

becomes:

`[0, 3, 4, 8, 10, 15]`.

The JavaScript implementation uses the same mathematical representation while demonstrating JavaScript arrays and iteration.

The C++ implementation encapsulates the prefix array inside `PrefixSumArray`. The class exposes operations such as `rangeSum`, `totalSum`, and `size`, separating construction from the code that consumes the data.

---

## Range-sum queries

The central formula is:

`rangeSum(left, right) = prefix[right + 1] - prefix[left]`

For:

`A = [2, 5, 1, 7, 3, 4]`

the prefix array is:

`[0, 2, 7, 8, 15, 18, 22]`.

The range `[1, 4]` contains:

`[5, 1, 7, 3]`

and its sum is:

`prefix[5] - prefix[1]`

which is:

`18 - 2 = 16`.

The implementation also includes a naive range-sum function. This is useful for testing because an optimized algorithm should be compared against a straightforward reference implementation.

---

## Multiple range queries

A common use case is a static array followed by many queries.

For example, given:

`[10, 20, 30, 40, 50]`

queries may ask for:

- indices `0..1`
- indices `1..3`
- indices `2..4`
- indices `0..4`

The prefix array is built once and reused.

This changes the computational model from repeatedly scanning ranges to:

`O(n + q)`.

The Python and JavaScript implementations explicitly demonstrate this pattern.

---

## Subarray versus subsequence

A subarray is contiguous.

For:

`[1, 2, 3, 4]`

`[2, 3]` is a subarray.

`[1, 3]` is not a contiguous subarray because element `2` has been skipped.

A subsequence does not require contiguity.

This distinction is essential because prefix-sum techniques discussed here are primarily designed for contiguous ranges.

---

## Number of subarrays

An array of length `n` has:

`n(n + 1) / 2`

non-empty contiguous subarrays.

For `n = 4`, there are:

`4 × 5 / 2 = 10`.

Although a prefix sum lets an individual subarray sum be calculated in `O(1)`, there are still `O(n²)` subarrays. Therefore, explicitly enumerating every subarray cannot become linear merely because prefix sums are available.

The Python implementation demonstrates this distinction.

---

## Prefix sums and negative numbers

Prefix sums do not require non-negative values.

For:

`[5, -2, 7, -4]`

the prefix representation is:

`[0, 5, 3, 10, 6]`.

Negative values simply decrease the running total.

This is an important distinction from some sliding-window techniques. A sliding window often depends on values being positive or non-negative so that the sum changes monotonically when the window expands or contracts.

Prefix sums do not require this monotonicity.

---

## Equilibrium index

An equilibrium index is an index where the sum of the elements before it equals the sum of the elements after it.

For:

`[-7, 1, 5, 2, -4, 3, 0]`

index `3` is an equilibrium index because:

left side:

`-7 + 1 + 5 = -1`

right side:

`-4 + 3 + 0 = -1`.

The implementation does not need to build an explicit prefix array. It can maintain:

- total array sum
- current left-side sum

At index `i`:

`rightSum = total - leftSum - A[i]`.

Then the condition is:

`leftSum == rightSum`.

This uses `O(n)` time and `O(1)` auxiliary space apart from the result.

---

## Prefix-frequency concepts

The most important advanced prefix-sum pattern is not simply storing prefix sums. It is storing how frequently particular prefix states have occurred.

Suppose two prefix sums are:

`P[i]` and `P[j]`.

The sum between them is:

`P[j] - P[i]`.

If that difference must equal `K`, then:

`P[i] = P[j] - K`.

While scanning the array, the current prefix sum is known. Therefore, the algorithm only needs to know how many times the required previous prefix sum has appeared.

This transforms many quadratic subarray-counting problems into linear expected-time algorithms.

---

## Counting subarrays with sum K

The algorithm maintains:

`frequency[prefixSum] = number of times this prefix sum has appeared`.

It starts with:

`frequency[0] = 1`.

For each element:

1. Update the running prefix sum.
2. Compute `requiredPrefix = runningSum - target`.
3. Add the frequency of `requiredPrefix` to the answer.
4. Record the current prefix sum.

The initial frequency of zero is critical.

Without it, a subarray beginning at index zero would not be counted.

For:

`[1, 1, 1]`

and target `2`, the valid subarrays are:

- indices `0..1`
- indices `1..2`

so the answer is `2`.

---

## Why duplicate prefix sums matter

Consider:

`[1, -1, 1, -1]`.

Its prefix sums are:

`0, 1, 0, 1, 0`.

The repeated value `0` means there are multiple pairs of positions whose difference is zero.

Every pair of equal prefix sums defines a zero-sum subarray.

This observation is the basis of zero-sum counting and many related prefix-frequency algorithms.

---

## Listing subarrays with sum K

Counting only requires the frequency of each prefix sum.

Listing the actual subarrays requires more information.

The implementation maps:

`prefixSum -> list of previous indices`.

If the current prefix is `P` and the target is `K`, every earlier occurrence of:

`P - K`

defines a valid subarray ending at the current index.

The output size can itself be quadratic. Therefore, even an `O(n)` scanning component may require `O(n²)` total time when the number of matching subarrays is `O(n²)`.

---

## Longest subarray with sum K

The longest-subarray problem uses a related but different rule.

For each prefix sum, retain only its earliest index.

If:

`currentPrefix - previousPrefix = K`

then an earlier occurrence of `previousPrefix` produces a longer subarray than a later occurrence.

Therefore, storing the first occurrence is essential.

The implementation returns both:

- maximum length
- corresponding `(left, right)` range when one exists

If no matching subarray exists, the range is represented as `null` in JavaScript and `std::optional` in C++.

---

## Zero-sum subarrays

For a zero-sum target:

`P[j] - P[i] = 0`

which means:

`P[j] = P[i]`.

Therefore, every pair of equal prefix sums defines a zero-sum subarray.

The frequency-map algorithm counts such pairs while scanning.

For a prefix value that has already appeared `f` times, the new occurrence creates `f` additional zero-sum subarrays ending at the current position.

---

## Prefix-frequency counting by parity

Prefix sums can also be classified by properties rather than exact values.

A subarray has an even sum if its two boundary prefix sums have the same parity.

Therefore:

- even prefix + even prefix → even difference
- odd prefix + odd prefix → even difference
- even prefix + odd prefix → odd difference

The Python implementation demonstrates this concept by counting even and odd prefix states.

This is an example of a broader principle:

> A prefix-state transformation can sometimes reduce a numerical condition to an equivalence-class condition.

---

## Subarrays divisible by K

A subarray sum is divisible by `K` when:

`P[j] - P[i] ≡ 0 (mod K)`.

Therefore:

`P[j] ≡ P[i] (mod K)`.

Instead of storing the exact prefix sum, the implementation stores its remainder modulo `K`.

Repeated remainders define subarrays whose sums are divisible by `K`.

Negative numbers require careful remainder normalization.

The Python implementation relies on Python's modulo behavior for a positive divisor.

The JavaScript and C++ implementations explicitly normalize the remainder so that it lies in:

`0..K-1`.

This illustrates an important language-level difference that can affect algorithm implementation.

---

## Prefix XOR

Prefix techniques are not restricted to addition.

XOR has the identity:

`A XOR B = K`

which can be rearranged as:

`B = A XOR K`.

Therefore, if `runningXor` is the current prefix XOR, the required earlier prefix is:

`runningXor XOR K`.

A frequency map can count the required prefix XOR states.

The JavaScript and C++ implementations demonstrate this related technique.

---

## Two-dimensional prefix sums

Prefix sums generalize to matrices.

For a matrix, define:

`P[r][c]`

as the sum of the rectangle from the origin through the cell immediately above and left of the current boundary.

The construction uses inclusion-exclusion:

`P[r][c] = A[r-1][c-1] + P[r-1][c] + P[r][c-1] - P[r-1][c-1]`.

A rectangle query can then be answered in constant time:

`P[bottom+1][right+1]`
`- P[top][right+1]`
`- P[bottom+1][left]`
`+ P[top][left]`.

The subtraction of the upper and left rectangles removes unwanted areas, while the top-left overlap is added back once.

The Python, JavaScript, and C++ implementations demonstrate this construction.

---

## Difference arrays

A difference array reverses the perspective.

Prefix sums efficiently answer range queries.

Difference arrays efficiently represent range updates.

For an update:

`add delta to [left, right]`

record:

`difference[left] += delta`

and:

`difference[right + 1] -= delta`.

After all updates, take a prefix sum of the difference array to reconstruct the final values.

For `q` range updates over an array of size `n`, the resulting procedure is:

`O(n + q)`.

This is particularly useful when many updates are known before the final values are required.

---

## Prefix aggregation beyond sums

The prefix concept can be generalized.

Examples include:

- prefix minimum
- prefix maximum
- prefix XOR
- prefix frequency
- prefix parity
- prefix modulo class
- prefix counts
- two-dimensional prefix aggregates

The exact operation must have properties that make the desired query or transformation valid.

A prefix minimum, for example, can answer:

"What is the minimum value from index zero through index i?"

but it cannot generally answer an arbitrary interior range minimum using simple subtraction because minimum does not have an inverse analogous to addition.

This distinction is important: not every aggregate supports the same range-query formula.

---

## Difference between prefix sums and sliding windows

Prefix sums and sliding windows can solve overlapping categories of problems, but their assumptions differ.

### Prefix sums

Useful when:

- negative numbers are allowed
- arbitrary range queries are needed
- many static range queries exist
- exact prefix relationships are important
- frequency maps can exploit repeated prefix states

Typical complexity:

`O(n)` preprocessing and `O(1)` range queries.

### Sliding windows

Useful when:

- the input has appropriate monotonicity
- values are often positive or non-negative
- the window condition can be maintained incrementally

Typical complexity:

`O(n)` with `O(1)` auxiliary state.

A sliding window should not be substituted for prefix-frequency methods merely because both involve contiguous ranges.

---

## Python implementation

The Python script is organized from basic prefix construction to more advanced frequency-based techniques.

Important functions include:

- `build_prefix_sum`
- `range_sum`
- `answer_range_queries`
- `enumerate_subarray_sums`
- `equilibrium_indices`
- `count_subarrays_with_sum_k`
- `subarrays_with_sum_k`
- `longest_subarray_with_sum_k`
- `count_zero_sum_subarrays`
- `count_subarrays_divisible_by_k`
- `count_subarrays_with_xor_k`
- `build_2d_prefix_sum`
- `rectangle_sum`
- `apply_range_updates`

Python dictionaries and `Counter` provide convenient hash-based frequency maps.

The script also contains randomized validation. Optimized algorithms are checked against brute-force reference implementations, which is a useful technique for detecting subtle indexing errors.

---

## JavaScript implementation

The JavaScript implementation emphasizes practical use of the language's `Map`, arrays, exception handling, and executable Node.js code.

The prefix-frequency algorithms use `Map` because prefix sums are dynamic keys and may include negative values.

The expression `map.get(key) ?? 0` provides a clear default for a missing frequency.

The JavaScript implementation also demonstrates an important language-specific issue with modulo arithmetic. JavaScript's `%` operator is a remainder operator and may return a negative value. Normalization is therefore required when a non-negative remainder class is needed.

The file also includes randomized validation and edge-case demonstrations.

---

## C++ case study

The C++ program models a retail transaction analytics system.

Each daily value represents a net change:

- positive values represent net inflow
- negative values represent net outflow

The system must support repeated historical analysis over a relatively static sequence.

### Problem being solved

Analysts need to determine:

- the total change over a period
- the change between arbitrary days
- equilibrium indices
- the number of contiguous periods totaling a target value
- the longest period totaling a target
- zero-sum periods
- divisibility-based periods
- related two-dimensional and range-update operations

A naive implementation could repeatedly scan the original data.

The case study instead preprocesses prefix information and uses hash maps where necessary.

---

## C++ architecture

### `PrefixSumArray`

`PrefixSumArray` owns the cumulative representation and exposes:

- `size`
- `rangeSum`
- `totalSum`
- `data`

The leading zero makes range calculations uniform.

### `TransactionAnalytics`

`TransactionAnalytics` represents the application-level analytics service.

It owns:

- original daily changes
- a `PrefixSumArray`

This separates domain data from the preprocessing mechanism.

### Prefix-frequency functions

The program contains dedicated functions for:

- `countSubarraysWithSumK`
- `longestSubarrayWithSumK`
- `countZeroSumSubarrays`
- `countSubarraysDivisibleByK`
- `countSubarraysWithXorK`

This separation makes each algorithm independently testable.

### `MatrixPrefixSum`

This class demonstrates that the same concept can be extended to two dimensions.

### Difference-array updates

`applyRangeUpdates` demonstrates the complementary range-update technique.

---

## Algorithmic complexity

| Operation | Time | Extra space |
|---|---:|---:|
| Build one-dimensional prefix sum | O(n) | O(n) |
| One range-sum query | O(1) | O(1) |
| q static range queries | O(n + q) | O(n) |
| Enumerate all subarray sums | O(n²) | O(n²) if stored |
| Count subarrays with sum K | O(n) expected | O(n) |
| Longest subarray with sum K | O(n) expected | O(n) |
| Count zero-sum subarrays | O(n) expected | O(n) |
| Count subarrays divisible by K | O(n) expected | O(min(n, K)) in typical remainder-map usage |
| Build 2D prefix sums | O(rows × columns) | O(rows × columns) |
| One 2D rectangle query | O(1) | O(1) |
| q range updates with difference array | O(n + q) | O(n) |

Hash-table-based methods are described as expected `O(n)` because hash-table operations are expected constant time, not guaranteed constant time under every theoretical collision scenario.

---

## Edge cases

The implementations explicitly consider:

- empty arrays
- single-element arrays
- all-zero arrays
- negative-only arrays
- mixed positive and negative values
- ranges beginning at index zero
- ranges ending at the final index
- target zero
- repeated prefix sums
- duplicate matching prefix states
- invalid range boundaries
- invalid zero divisors
- matrices with inconsistent row lengths
- invalid range updates

The leading-zero representation is particularly useful because it removes a common boundary special case.

---

## Integer considerations

Python integers grow automatically beyond normal machine integer limits, subject to available memory.

JavaScript's ordinary `Number` type is a double-precision floating-point value. Exact integer arithmetic is guaranteed only within the safe integer range. For very large financial or algorithmic values, JavaScript `BigInt` may be appropriate, with the trade-off that it cannot be mixed directly with ordinary `Number` arithmetic.

The C++ implementation uses `long long`, which provides a substantially larger signed integer range than a typical 32-bit integer. Production systems must still verify that expected cumulative totals cannot overflow the selected type.

For extremely large values, C++ applications may require wider integer types or checked arithmetic.

---

## Common mistakes

### Off-by-one errors

With a leading-zero prefix array, use:

`prefix[right + 1] - prefix[left]`.

Using `prefix[right] - prefix[left]` shifts the range incorrectly.

### Forgetting `frequency[0] = 1`

This prevents subarrays beginning at index zero from being counted.

### Replacing earliest occurrences

For longest-subarray problems, replacing the earliest prefix occurrence with a later one can reduce the maximum length.

### Confusing subarrays and subsequences

Prefix-sum range techniques operate on contiguous intervals.

### Assuming negative values invalidate prefix sums

They do not. Negative values are completely valid for ordinary prefix-sum construction.

### Assuming sliding windows always work

Sliding windows depend on structural properties such as monotonicity. Arbitrary negative values can invalidate those assumptions.

### Mishandling negative modulo values

Different programming languages represent remainder operations differently. Algorithms based on remainder classes should normalize negative results when necessary.

---

## Validation strategy

The Python, JavaScript, and C++ implementations include comparisons between optimized algorithms and brute-force reference logic.

This is particularly valuable for:

- range-query formulas
- subarray counting
- boundary conditions
- negative values
- zero targets
- repeated prefix sums

Randomized testing is effective because prefix algorithms often fail through small indexing or initialization mistakes that are not obvious from a few hand-written examples.

---

## Performance considerations

Prefix sums are most valuable when the data is read frequently relative to how often it changes.

If an array is static:

- preprocessing is performed once
- range queries become constant time

If the underlying values change frequently, a simple prefix array may become expensive to maintain because a change can affect every later prefix value.

For dynamic data, other structures may be more suitable, such as:

- Fenwick trees
- segment trees
- other specialized range-query structures

Those structures address a different problem model and should not be introduced merely because prefix sums exist.

---

## Security and reliability considerations

Prefix sums are not inherently a security mechanism, but production implementations should still consider input validation and arithmetic correctness.

Relevant concerns include:

- integer overflow
- malformed ranges
- invalid divisors
- inconsistent matrix dimensions
- excessive input sizes
- memory consumption from storing prefix states
- adversarial hash-map workloads in systems where hash behavior matters

The C++ program validates range boundaries and catches exceptions at the application boundary.

A production financial system would also require explicit monetary representation rules rather than assuming floating-point arithmetic is suitable for currency.

---

## Important distinctions

### Prefix sum versus cumulative total

A cumulative total is the running accumulation itself.

A prefix-sum array stores those cumulative states in an indexed structure so they can be reused.

### Prefix sum versus subarray sum

A prefix sum describes a range beginning at the first element.

A subarray sum can describe any contiguous interval.

The difference between two prefix sums produces a subarray sum.

### Prefix frequency versus prefix value

The prefix value is the cumulative state.

Prefix frequency records how many times that state has appeared.

Many `O(n)` subarray-counting algorithms depend on the second concept.

### Prefix sum versus difference array

Prefix sums convert stored cumulative information into fast range queries.

Difference arrays represent range changes compactly and use a final prefix operation to reconstruct values.

---

## Practical applications

Prefix techniques are used in many data-processing situations, including:

- financial time-series analysis
- transaction aggregation
- sales reporting
- telemetry processing
- cumulative counters
- log analytics
- resource-consumption analysis
- image and matrix processing
- competitive programming
- database-style analytical workloads
- interval update processing
- signal and event analysis

The key engineering question is not simply whether a prefix sum can be constructed. It is whether preprocessing the data produces a useful computational advantage for the workload being performed.

---

## Implementation considerations

A prefix-sum solution should normally begin by identifying the query model:

1. Is the data static?
2. Are there many range queries?
3. Are values allowed to be negative?
4. Is the problem asking for sums, counts, lengths, or actual intervals?
5. Can repeated prefix states be exploited?
6. Is the output itself potentially quadratic?
7. Does the operation have an inverse or equivalence relation suitable for prefix reasoning?
8. Can integer overflow occur?
9. Does the language's numeric model affect correctness?

These questions determine whether ordinary prefix sums, prefix-frequency maps, difference arrays, two-dimensional prefixes, sliding windows, or a dynamic data structure is appropriate.

---

## Real-world relevance of the three implementations

Python makes prefix algorithms concise and exposes the mathematical structure clearly through lists, dictionaries, and `Counter`.

JavaScript demonstrates the same ideas in an application-oriented language where `Map`, arrays, numeric semantics, and runtime validation are important implementation details.

C++ demonstrates how prefix techniques can be incorporated into a typed, modular analytics system with classes, exception handling, explicit integer types, standard containers, and deterministic testing.

The underlying algorithm is the same mathematical idea, but each implementation highlights different engineering concerns.

---

## Key formulas

### One-dimensional prefix

`P[i + 1] = P[i] + A[i]`

### Range sum

`sum(left..right) = P[right + 1] - P[left]`

### Subarray sum target

`P[j] - P[i] = K`

therefore:

`P[i] = P[j] - K`

### Zero-sum subarray

`P[j] = P[i]`

### Divisible-by-K subarray

`P[j] mod K = P[i] mod K`

### Number of non-empty subarrays

`n(n + 1) / 2`

### Two-dimensional prefix

`P[r][c] = A[r-1][c-1] + P[r-1][c] + P[r][c-1] - P[r-1][c-1]`

### Difference-array update

`D[left] += delta`

`D[right + 1] -= delta`

---

## Files and execution

The Python implementation can be executed with a standard Python 3 interpreter.

The JavaScript implementation is designed for Node.js.

The C++ implementation uses C++17 or a later standard.

The implementations are self-contained and use no external dependencies.

The Python and JavaScript files execute demonstrations and validation automatically. The C++ program runs the transaction-analytics case study, related prefix algorithms, validation routines, edge cases, two-dimensional prefix queries, and difference-array updates.
