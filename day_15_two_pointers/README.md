# Day 15 — Two Pointers

## Topic

Two pointers is a family of array and sequence techniques in which two indices, iterators, or references are moved according to a problem-specific invariant.

The technique is especially useful when:

- the input is sorted,
- two ends of a sequence must be compared,
- one pointer reads while another writes,
- a search space can be eliminated monotonically,
- elements must be partitioned in place,
- a pair or range must be evaluated efficiently,
- an outer loop can be combined with an inner two-pointer search.

The central idea is not simply to use two variables called `left` and `right`. A correct two-pointer algorithm requires a reason that each pointer movement permanently eliminates candidates from consideration.

This implementation set develops the technique from basic pointer movement to pair search, in-place modification, container-style optimization, three-sum, partitioning, validation, testing, and an industry-style C++ case study.

## Learning objectives

The implementations cover:

- opposite-direction pointers,
- same-direction pointers,
- sorted-array pair search,
- pair sum,
- in-place array reversal,
- palindrome detection,
- duplicate removal,
- read/write pointer patterns,
- moving zeroes,
- container-style problems,
- three-sum,
- partition-style algorithms,
- three-way partitioning,
- closest-pair search,
- input validation,
- invariants,
- edge cases,
- randomized testing,
- unit testing,
- complexity analysis,
- implementation trade-offs.

## Fundamental concept

A pointer is an index or reference representing a current position in a data structure.

For an array, two pointers may be represented as:

- `left`
- `right`

For a read/write algorithm, they may instead be:

- `read`
- `write`

The names are not important. Their responsibilities and movement rules are important.

A typical opposite-direction structure is conceptually:

`left -> ... <- right`

The pointers begin at different ends and move toward each other.

A typical same-direction structure is conceptually:

`read ->`
`write ->`

The read pointer scans incoming elements while the write pointer maintains a processed region.

## Opposite-direction pointers

Opposite-direction pointers are particularly useful when information at both ends of a sequence matters.

A common structure is:

1. Set `left` to the first index.
2. Set `right` to the last index.
3. Inspect both values.
4. Decide which pointer can safely move.
5. Repeat until the pointers meet.

The termination condition is commonly `left < right` when two distinct elements are required.

### Why sorted arrays matter

Suppose a sorted array is:

`[1, 2, 4, 6, 8, 10]`

and the target sum is `14`.

Start with:

- left = `1`
- right = `10`
- sum = `11`

The sum is too small. Because the array is sorted, moving `right` leftward would make the sum even smaller. The only useful direction is to move `left` rightward.

Now:

- left = `2`
- right = `10`
- sum = `12`

Again, the sum is too small, so `left` moves.

Eventually:

- left = `4`
- right = `10`
- sum = `14`

The target is found.

The sorted property is what makes this pointer movement logically valid.

## Pair sum

The Python implementation provides `pair_sum_sorted`.

The JavaScript implementation provides `pairSumSorted`.

The C++ implementation provides `pairSumSorted`.

Each implementation uses the same fundamental invariant:

- if the sum is too small, increase the smaller-side pointer;
- if the sum is too large, decrease the larger-side pointer;
- if the sum matches the target, return the pair.

For a sorted array, this changes a brute-force `O(n^2)` search into an `O(n)` scan.

### Brute-force comparison

A brute-force algorithm checks every pair.

For `n` elements, the number of possible pairs grows approximately as:

`n(n - 1) / 2`

This gives `O(n^2)` time.

The two-pointer method makes only a linear number of pointer movements, giving `O(n)` time after the data is already sorted.

If sorting is necessary first, the complete cost becomes:

`O(n log n) + O(n) = O(n log n)`

This distinction is important when comparing a two-pointer solution with a hash-table solution for unsorted data.

## Why the pair-sum algorithm works

Assume the array is sorted and the current values are `A[left]` and `A[right]`.

If:

`A[left] + A[right] < target`

then every element at an index smaller than or equal to `left` is no larger than `A[left]`.

Keeping `left` fixed and decreasing `right` cannot increase the sum. Therefore the current `left` can be discarded for the current `right`, and moving `left` forward is justified.

Similarly, if:

`A[left] + A[right] > target`

moving `left` forward cannot reduce the sum. Therefore `right` can safely move backward.

This is the elimination property that makes the algorithm efficient.

## Reverse array

Array reversal is a direct opposite-direction application.

For:

`[10, 20, 30, 40, 50]`

the first and last values are swapped.

Then:

- `left` moves right,
- `right` moves left.

The process stops when the pointers meet.

The Python function is `reverse_in_place`.

The JavaScript function is `reverseInPlace`.

The C++ case study uses `reverseTransactions` for transaction records rather than simple integers.

### Complexity

Time: `O(n)`

Extra space: `O(1)`

The algorithm modifies the array in place.

## Palindrome detection

A palindrome reads the same from both directions.

Examples include:

- `[1, 2, 3, 2, 1]`
- `[4, 4]`
- `[7]`
- an empty sequence

The algorithm compares:

`values[left]` with `values[right]`

If they differ, the sequence is not a palindrome.

If they match, both pointers move inward.

The comparison stops as soon as a mismatch is found or the pointers meet.

## Same-direction pointers

Not every two-pointer algorithm moves inward from opposite ends.

A second major pattern uses two pointers moving in the same direction.

The most important form is the read/write pattern.

The read pointer examines every input element.

The write pointer identifies where the next accepted element belongs.

The already-processed prefix is maintained as an invariant.

## Remove duplicates from a sorted array

Consider:

`[1, 1, 2, 2, 3, 3]`

The objective is to retain one copy of each value.

The read pointer examines the input.

The write pointer identifies the next output position.

When a new value is found, it is written at the write position.

The Python function is `remove_duplicates_sorted`.

The JavaScript function is `removeDuplicatesSorted`.

The C++ implementation applies the same technique to transaction records using transaction IDs.

The logical output is represented by the prefix before the write pointer.

For example, the physical array may contain:

`[1, 2, 3, 2, 3, 3]`

after compaction.

If the returned logical length is `3`, only:

`[1, 2, 3]`

belongs to the result.

This distinction between physical storage and logical length is important in in-place algorithms.

### Complexity

Time: `O(n)`

Extra space: `O(1)`

The technique works because the input is sorted. In an unsorted array, equal values may be separated by unrelated values.

## Moving zeroes

The read/write pattern can also rearrange elements.

The JavaScript function `moveZeroes` maintains:

- a read pointer scanning all elements,
- a write pointer identifying the next nonzero position.

Nonzero elements are moved toward the front while their relative order is preserved.

The remaining positions contain zeroes.

This demonstrates that same-direction pointers are useful beyond duplicate removal.

## Container-style problems

The container problem asks for two boundaries that maximize an area-like quantity.

For two heights:

`height[left]`

and:

`height[right]`

the area is:

`min(height[left], height[right]) * (right - left)`

The limiting height is the shorter boundary.

### Pointer movement

Suppose:

`height[left] <= height[right]`

Moving `right` inward decreases the width while leaving the limiting height no greater than the current left boundary.

Therefore moving the taller side cannot improve the current limiting configuration.

The shorter side must move.

This produces an `O(n)` solution.

The Python implementation is `max_container_area`.

The JavaScript implementation is `maxContainerArea`.

The C++ implementation is `maximumContainerCapacity`.

### Brute force versus two pointers

Brute force evaluates every pair of boundaries:

Time: `O(n^2)`

The two-pointer algorithm evaluates a linear number of states:

Time: `O(n)`

Both approaches use constant extra space when the input is already available.

The important difference is the proof that allows candidate pairs to be eliminated.

## Three-sum foundations

Three-sum extends the pair-sum idea.

The objective is to find triples whose sum equals a target.

A brute-force solution checks three indices:

`i`, `j`, and `k`

and has `O(n^3)` time complexity.

A more efficient strategy is:

1. Sort the array.
2. Fix one value with index `i`.
3. Search the remaining suffix with two pointers.
4. Move the pointers according to the current sum.
5. Skip duplicate values.

The resulting complexity is:

Sorting:

`O(n log n)`

Outer loop plus two-pointer search:

`O(n^2)`

Overall:

`O(n^2)`

The Python function is `three_sum`.

The JavaScript function is `threeSum`.

The C++ implementation is `threeSum`.

## Duplicate handling in three-sum

Duplicate handling is an important part of three-sum.

Suppose the input is:

`[0, 0, 0, 0]`

There is only one unique value triple:

`[0, 0, 0]`

The implementation avoids duplicate triples by:

1. skipping duplicate fixed values,
2. skipping repeated left values after a match,
3. skipping repeated right values after a match.

Without these checks, the same logical triple could appear multiple times.

## Partition-style algorithms

Partitioning divides an array into regions according to a condition.

A basic partition condition might be:

`value < pivot`

The partition algorithm maintains a boundary.

Values before the boundary satisfy the condition.

Values after the boundary have not necessarily been ordered internally, but they satisfy the complementary condition.

The Python function is `partition_around_value`.

The JavaScript function is `partitionAroundValue`.

The C++ implementation is `partitionRiskLevels`.

### Stability

The partition implementations are unstable.

This means the relative ordering of elements within the resulting regions is not guaranteed.

This is a deliberate trade-off.

An unstable partition can often be implemented in:

Time: `O(n)`

Extra space: `O(1)`

A stable partition generally requires more work or additional storage, depending on the exact implementation.

## Dutch National Flag pattern

The C++ and JavaScript implementations include a three-way partitioning technique for values `0`, `1`, and `2`.

The maintained regions are:

- `[0, low)` contains zeroes,
- `[low, mid)` contains ones,
- `[mid, high]` contains unknown values,
- `(high, end)` contains twos.

The algorithm processes the unknown region until it becomes empty.

This is a three-pointer technique rather than a simple two-pointer technique, but it belongs to the same broader family of pointer-driven partition algorithms.

Time complexity is:

`O(n)`

Extra space is:

`O(1)`

## Sorted squares

A sorted array can contain negative values whose squares become large.

For example:

`[-7, -3, -1, 2, 4, 8]`

The largest square must come from one of the two ends because the input is sorted.

The algorithm compares the square of the left value with the square of the right value.

The larger square is written into the result from right to left.

This produces:

`[1, 4, 9, 16, 49, 64]`

in `O(n)` time.

The Python function is `squares_of_sorted_array`.

The JavaScript function is `sortedSquares`.

The result requires `O(n)` storage because a separate sorted output array is produced.

## Valid palindrome after one deletion

A variation of palindrome detection allows one character to be removed.

When a mismatch occurs, there are only two immediate candidates:

- remove the left character,
- remove the right character.

The implementation checks both remaining ranges.

The important point is that the branching is tightly bounded.

The algorithm does not recursively explore arbitrary deletion combinations.

The Python function is `valid_palindrome_after_one_deletion`.

The JavaScript function is `validPalindromeAfterOneDeletion`.

## Merging sorted arrays

Two sorted arrays can be merged using one read pointer for each array.

At each step, the smaller current value is appended to the output.

When one input is exhausted, the remaining suffix of the other input can be appended directly.

For arrays of lengths `n` and `m`:

Time: `O(n + m)`

Output space: `O(n + m)`

This is a core pointer technique behind merge-based algorithms.

## Closest pair

The C++ case study includes `closestPairToTarget`.

The values are sorted and then processed with two pointers.

Instead of stopping only when the exact target is found, the algorithm records the smallest absolute difference seen.

If the current sum is smaller than the target, the left pointer moves forward.

If it is larger, the right pointer moves backward.

If an exact match occurs, the search can stop because the absolute difference is already zero.

Because sorting is required, the overall complexity is:

`O(n log n)`

for sorting plus:

`O(n)`

for the two-pointer scan.

The sorting step therefore dominates.

## Input validation

Two-pointer algorithms often rely on preconditions.

For sorted-array algorithms, sorted order is not merely an optimization. It can be part of the correctness argument.

The Python implementation contains `require_sorted`.

The JavaScript implementation contains `requireSorted`.

The C++ implementation validates sorted data using `validateSortedNonDecreasing`.

Production systems should make important preconditions explicit when invalid input is possible.

There is a trade-off: validation itself can cost `O(n)`.

If a system already guarantees sorted input through its data contract, repeating the check may be unnecessary.

## Edge cases

Important edge cases include:

- empty arrays,
- one-element arrays,
- two-element arrays,
- duplicate values,
- all values equal,
- no valid pair,
- multiple valid pairs,
- negative values,
- zero values,
- target values outside the possible range,
- already sorted data,
- reverse-sorted data,
- invalid input,
- invalid classification values,
- duplicate triples.

For example, a pair-sum loop normally uses:

`left < right`

rather than:

`left <= right`

when the problem requires two distinct elements.

Allowing `left == right` could accidentally use the same element twice.

## Pointer invariants

An invariant is a condition that remains true throughout the algorithm.

For pair sum, a useful invariant is:

All candidate pairs that have not been eliminated remain within the current pointer range.

For duplicate removal:

The prefix before the write pointer contains the correct unique result discovered so far.

For partitioning:

Elements before the boundary satisfy the partition condition.

For three-way classification:

Each completed region satisfies its assigned classification.

Writing down the invariant before implementing the loop is a useful correctness technique.

## Common mistakes

### Applying sorted logic to unsorted data

This is one of the most serious mistakes.

If an array is not sorted, a decision such as "the sum is too small, so move left" is not necessarily valid.

The solution must either:

- sort the input,
- use a suitable data structure,
- or use another algorithm.

### Forgetting duplicate handling

Three-sum can easily return duplicate triples if equal values are not skipped.

### Moving the wrong pointer

A pointer should move only when the problem's invariant proves that doing so cannot discard a valid better answer.

### Confusing physical length and logical length

In in-place compaction, the underlying container may retain stale values after the valid prefix.

The returned length identifies the logical result.

### Accidentally using the same element twice

For pair problems requiring two distinct elements, `left < right` is usually the correct condition.

### Ignoring integer overflow

Python integers grow automatically, but C++ integer arithmetic can overflow fixed-width types.

The C++ case study therefore converts pair and triple sums to `long long`.

This is especially important when input values can approach the limits of `int`.

### Assuming sorting is free

Sorting changes the complexity and can change the original order.

A two-pointer solution based on sorting should account for:

- sorting cost,
- additional memory,
- whether original indices matter,
- whether original ordering must be preserved.

## Python implementation

The Python script is designed as a standalone study and execution file.

It includes:

- `pair_sum_sorted`,
- `pair_sum_brute_force`,
- `reverse_in_place`,
- `is_palindrome`,
- `remove_duplicates_sorted`,
- `move_zeroes`,
- `max_container_area`,
- `max_container_area_brute_force`,
- `three_sum`,
- `partition_around_value`,
- `dutch_national_flag`,
- `squares_of_sorted_array`,
- `valid_palindrome_after_one_deletion`,
- `merge_two_sorted_arrays`,
- input validation,
- pointer tracing,
- randomized verification,
- unit tests.

The Python implementation is particularly useful for expressing the algorithms directly and comparing reference implementations with optimized implementations.

Python's arbitrary-precision integers also make it convenient for demonstrating arithmetic without fixed-width integer overflow.

## JavaScript implementation

The JavaScript file provides the same conceptual family through JavaScript-specific executable code.

It demonstrates:

- arrays,
- functions,
- mutation,
- destructuring swaps,
- sorting with a numeric comparator,
- exceptions,
- object-based debugging output,
- randomized verification,
- assertions.

A particularly important JavaScript detail is numeric sorting.

The expression:

`array.sort()`

does not perform general numeric ascending sorting as expected by many beginners.

For numbers, the implementation uses:

`array.sort((a, b) => a - b)`

This is essential for the sorted-array two-pointer algorithms.

The JavaScript implementation also uses array copying with the spread syntax where the algorithm should preserve the caller's original array.

## C++ case study

The C++ program models an industry-style transaction analytics component.

The scenario combines multiple two-pointer patterns rather than treating each technique as an isolated exercise.

### Domain model

The `Transaction` structure contains:

- transaction ID,
- amount,
- risk level.

This allows pointer techniques to operate on meaningful domain records.

### Pair settlement detection

`pairSumSorted` searches sorted transaction amounts for two values matching a target.

The implementation validates the sorted precondition and uses `long long` for the sum.

### Duplicate transaction normalization

`removeDuplicateTransactionIds` demonstrates same-direction read/write pointers.

Transactions are assumed to be sorted by ID.

The returned logical length identifies the duplicate-free prefix.

### Reverse audit processing

`reverseTransactions` demonstrates opposite-direction pointers on objects rather than primitive values.

This shows that the technique is independent of the element type.

### Capacity analysis

`maximumContainerCapacity` adapts the container problem to a capacity-style analytics model.

The algorithm tracks:

- left boundary,
- right boundary,
- current capacity,
- best capacity,
- best boundary indices.

### Three-sum risk combinations

`threeSum` demonstrates the standard sorted three-sum pattern.

The outer index fixes one value, while the two-pointer scan handles the remaining two values.

Duplicate combinations are removed.

### Risk threshold partition

`partitionRiskLevels` places transactions with risk below a threshold before records meeting or exceeding the threshold.

This is an unstable partition.

### Three-way classification

`classifyRiskLevels` separates low, medium, and high risk values using three regions.

The implementation validates that every classification is one of `0`, `1`, or `2`.

### Closest settlement pair

`closestPairToTarget` demonstrates a variation of pair sum where an exact match is not required.

The algorithm tracks the pair with the smallest absolute difference from the target.

## Testing strategy

The Python implementation uses `unittest`.

The JavaScript implementation provides an assertion-based test suite.

The C++ implementation uses `assert`.

The tests cover:

- successful pair searches,
- unsuccessful searches,
- reversal,
- duplicate removal,
- container calculations,
- three-sum,
- partitioning,
- three-way classification,
- sorted squares,
- palindrome validation,
- sorted-array merging,
- input validation.

The programs also compare optimized algorithms against simpler reference implementations where practical.

## Randomized testing

Randomized testing is useful for algorithms whose outputs can be compared against a simpler trusted implementation.

The Python and JavaScript implementations generate deterministic test sequences.

The C++ implementation uses a fixed random seed.

For pair sum, the test compares:

- brute-force existence,
- two-pointer existence.

The exact returned pair does not need to be identical when multiple valid pairs exist. The important property is that both algorithms agree on whether a solution exists and that any returned pair satisfies the target.

This is a useful testing principle for nondeterministic or multi-answer algorithms.

## Complexity reference

| Algorithm | Time | Extra space |
|---|---:|---:|
| Pair sum on sorted input | `O(n)` | `O(1)` |
| Pair sum after sorting | `O(n log n)` | depends on sorting |
| Pair sum brute force | `O(n^2)` | `O(1)` |
| Reverse in place | `O(n)` | `O(1)` |
| Palindrome check | `O(n)` | `O(1)` |
| Remove duplicates | `O(n)` | `O(1)` |
| Move zeroes | `O(n)` | `O(1)` |
| Container problem | `O(n)` | `O(1)` |
| Three-sum after sorting | `O(n^2)` | `O(n)` for copied input |
| Partition | `O(n)` | `O(1)` |
| Dutch National Flag | `O(n)` | `O(1)` |
| Sorted squares | `O(n)` | `O(n)` result |
| Merge two sorted arrays | `O(n + m)` | `O(n + m)` result |
| Closest pair after sorting | `O(n log n)` | sorting-dependent |

The exact space complexity of sorting can depend on the programming language, standard library, and implementation.

## Python, JavaScript, and C++ comparison

### Python

Python emphasizes concise expression of the algorithm.

It is particularly convenient for:

- experimentation,
- algorithm prototyping,
- readable educational implementations,
- automated tests,
- rapid comparison between brute-force and optimized solutions.

Python's integers avoid the fixed-width overflow concerns common in C++.

### JavaScript

JavaScript demonstrates how two-pointer algorithms behave in an application-oriented language.

Relevant considerations include:

- numeric sorting,
- mutable arrays,
- exceptions,
- object inspection,
- array copying,
- runtime assertions.

JavaScript is especially relevant when the same algorithm will later be used in browser or Node.js data-processing code.

### C++

C++ exposes lower-level implementation decisions more directly.

The case study demonstrates:

- explicit data structures,
- references,
- standard library algorithms,
- exception handling,
- fixed-width integer considerations,
- object-oriented domain modeling,
- memory-aware in-place operations,
- deterministic randomized testing.

C++ is useful for examining performance-sensitive implementations where memory layout, object movement, and numeric representation matter.

## When two pointers is appropriate

Two pointers are strong candidates when:

- the input is sorted,
- the problem involves a pair,
- both ends of a sequence matter,
- a range can be reduced monotonically,
- an array needs in-place compaction,
- elements need to be partitioned,
- a problem contains a pair-search subproblem,
- the solution can eliminate candidates permanently.

Typical problem clues include:

- sorted array,
- pair sum,
- closest pair,
- palindrome,
- reverse,
- remove duplicates,
- move elements,
- maximum area,
- three sum,
- partition.

## When two pointers is not appropriate

Two pointers should not be selected merely because an array is present.

It may be unsuitable when:

- the input has no useful ordering,
- pointer movement cannot be justified,
- arbitrary lookups dominate the problem,
- the original ordering must be preserved and sorting would violate requirements,
- a hash-based method provides a better direct solution,
- the problem requires a different data structure,
- candidate elimination is not monotonic.

The correct algorithm depends on the constraints and required output.

## Sorting trade-offs

Sorting can enable an efficient two-pointer algorithm, but sorting changes the input arrangement.

For example, an unsorted pair-sum problem may be solved using:

- a hash table in expected `O(n)` time,
- sorting plus two pointers in `O(n log n)` time.

A hash-based method can preserve original indices more naturally.

Sorting can be preferable when:

- ordering is already useful,
- multiple subsequent queries benefit from sorted data,
- the problem naturally depends on order,
- memory or implementation constraints favor the sorted approach.

The correct choice depends on the complete problem specification.

## Stability and in-place operations

Several two-pointer algorithms work in place.

Advantages include:

- low extra memory,
- fewer allocations,
- potentially better cache behavior,
- suitability for constrained environments.

Trade-offs include:

- mutation of the input,
- possible loss of original ordering,
- more complicated invariants,
- unstable rearrangement.

A production implementation should document whether input mutation is allowed.

## Security considerations

Two-pointer algorithms are normally algorithmic rather than security-specific, but production implementations still need input validation.

Relevant concerns include:

- malformed input,
- unexpected negative values,
- non-finite floating-point values,
- integer overflow,
- extremely large input sizes,
- invalid classification values,
- assumptions about sorted data.

The C++ implementation explicitly uses `long long` for arithmetic involving multiple `int` values.

The validation functions also reject invalid data where the case study requires stricter domain rules.

## Performance considerations

Two-pointer algorithms can improve performance substantially by replacing repeated candidate searches with monotonic pointer movement.

For example:

Pair sum:

`O(n^2)` → `O(n)`

Three-sum:

`O(n^3)` → `O(n^2)`

Container:

`O(n^2)` → `O(n)`

These improvements become increasingly important as input sizes grow.

The main performance principle is that each pointer should generally move in one direction and should not repeatedly revisit the same positions.

## Debugging strategy

A useful debugging technique is to print pointer state.

The Python function `trace_pair_sum` and the JavaScript function `tracePairSum` display:

- left index,
- right index,
- left value,
- right value,
- current sum.

This makes incorrect pointer movement visible.

For more complicated algorithms, the same technique can be extended to display:

- current invariant,
- partition boundaries,
- candidate ranges,
- number of processed elements,
- best answer found so far.

When debugging, check the invariant rather than only checking the final output.

## Design principles

A robust two-pointer implementation should make the following decisions explicit:

1. What does each pointer represent?
2. Where does each pointer start?
3. What condition ends the loop?
4. What invariant is maintained?
5. Under which condition does each pointer move?
6. Can a pointer ever move backward?
7. Can both pointers move in one iteration?
8. What happens with duplicate values?
9. What happens with an empty input?
10. What are the exact time and space requirements?
11. Is input mutation allowed?
12. Does sorting change required information?
13. Can arithmetic overflow?
14. What validation is necessary?

Answering these questions before implementation reduces many common pointer errors.

## Practical applications

Two-pointer techniques appear in:

- array and sequence processing,
- financial transaction analysis,
- data cleaning,
- deduplication,
- interval-like processing,
- resource allocation,
- capacity analysis,
- risk classification,
- search optimization,
- streaming-style scans,
- parsing,
- partitioning,
- geometric computations,
- competitive programming,
- technical interview problems.

The underlying principle is broadly useful whenever ordered or bounded data allows impossible candidates to be discarded without explicitly testing every possibility.
