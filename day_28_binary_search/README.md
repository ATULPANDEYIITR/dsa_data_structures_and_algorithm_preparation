# Day 28 — Binary Search

## Topic

Binary search is an algorithm for locating values or boundaries inside an ordered search space. Instead of examining every candidate from left to right, it compares the target with a middle element and eliminates approximately half of the remaining search space.

The central idea is simple:

1. Define the current search boundaries.
2. Calculate a midpoint.
3. Compare the midpoint with the target or evaluate a search condition.
4. Eliminate the part of the search space that cannot contain the answer.
5. Repeat until the search space is empty or the required boundary is identified.

For a correctly ordered search space, binary search reduces the problem from linear growth to logarithmic growth.

For `n` elements:

- Linear search: `O(n)`
- Binary search: `O(log n)`
- Iterative binary search auxiliary space: `O(1)`
- Recursive binary search stack space: `O(log n)`

---

## Learning Objectives

This implementation set develops binary search from the basic exact-match problem to more advanced forms:

- Sorted-array requirements
- Ascending and descending ordering
- Left and right boundaries
- Inclusive and half-open intervals
- Midpoint calculation
- Search-space reduction
- Exact search
- Duplicate handling
- First occurrence
- Last occurrence
- Lower bound
- Upper bound
- Counting duplicates
- Finding occurrence ranges
- Rotated sorted arrays
- Rotated arrays containing duplicates
- Nearly sorted arrays
- Peak finding
- Search in a sorted matrix
- Exponential search
- Binary search on the answer
- Monotonic predicates
- Integer square root
- Floating-point approximation
- Object-based searching
- Input validation
- Testing
- Randomized testing
- Performance measurement
- Production considerations

---

# 1. Fundamental Concept

Binary search works because ordering provides information.

Consider:

`[10, 20, 30, 40, 50, 60, 70]`

Suppose the target is `60`.

The middle element is `40`.

Because the array is sorted in ascending order:

- Everything before `40` is less than or equal to `40`.
- Therefore, `60` cannot be in that portion.
- The search can continue only in the right portion.

The search space changes from approximately:

`[10, 20, 30, 40, 50, 60, 70]`

to:

`[50, 60, 70]`

The process continues until the target is found or no candidates remain.

The important feature is not simply that the array is indexed. The important feature is that the ordering lets the algorithm safely eliminate candidates.

---

# 2. The Sorted-Array Requirement

Ordinary binary search assumes that the search space is ordered according to the comparison being used.

For ascending data:

`1, 4, 7, 10, 15, 20`

For descending data:

`20, 15, 10, 7, 4, 1`

An unsorted sequence such as:

`10, 3, 20, 5, 8`

does not satisfy the ordinary binary-search precondition.

Running binary search against unsorted data does not merely make the algorithm less efficient. Its result is not reliable because the algorithm's decisions about which half can be discarded are no longer justified.

The Python implementation contains `is_sorted_ascending()` and `validated_binary_search()` to demonstrate explicit precondition validation.

In production systems, repeatedly checking sortedness can be undesirable because checking the entire array costs `O(n)`. If a data structure already guarantees sorted ordering, the validation normally belongs at the point where the data structure is created or modified rather than before every search.

---

# 3. Search Boundaries

Two common representations are used.

## Inclusive interval

The search interval is:

`[left, right]`

Both endpoints are possible candidates.

A typical initialization is:

`left = 0`

`right = len(values) - 1`

The loop usually continues while:

`left <= right`

When the midpoint is too small:

`left = middle + 1`

When the midpoint is too large:

`right = middle - 1`

This representation is used by the exact-search implementations.

## Half-open interval

The search interval is:

`[left, right)`

The left endpoint is included and the right endpoint is excluded.

A typical initialization is:

`left = 0`

`right = len(values)`

The loop continues while:

`left < right`

This representation is particularly useful for lower and upper bounds because an empty range naturally becomes:

`[x, x)`

The most important rule is consistency. Many binary-search bugs are caused by mixing inclusive and exclusive boundary conventions.

---

# 4. Midpoint Calculation

The midpoint can be calculated conceptually as:

`(left + right) / 2`

For integer array indexes, integer division is required.

A safer general expression in fixed-width integer languages is:

`left + (right - left) / 2`

This avoids directly adding two potentially large values.

Python integers do not have the same fixed-width overflow behavior as C++ integer types, but the Python implementation uses the safer pattern because it teaches a portable technique.

C++ uses:

`left + (right - left) / 2`

JavaScript uses:

`left + Math.floor((right - left) / 2)`

---

# 5. Exact Search

Exact binary search answers:

> Does this exact value exist, and if so, at which index?

The Python implementation is `binary_search_exact()`.

The JavaScript implementation is `binarySearchExact()`.

The C++ implementation is `binarySearchExact()`.

The basic decision structure is:

- If `values[middle] == target`, return the index.
- If `values[middle] < target`, discard the left side including the midpoint.
- If `values[middle] > target`, discard the right side including the midpoint.

The algorithm terminates when:

`left > right`

At that point the search interval is empty.

---

# 6. Search-Space Reduction

The defining operation is elimination.

Suppose there are 64 candidates.

After one effective comparison:

`64 -> 32`

Then:

`32 -> 16`

Then:

`16 -> 8`

Then:

`8 -> 4`

Then:

`4 -> 2`

Then:

`2 -> 1`

Then:

`1 -> 0`

This logarithmic reduction explains the `O(log n)` complexity.

The logarithm is base 2 because the search space is approximately divided into two portions at every step.

---

# 7. Duplicates

Exact binary search does not necessarily return the first occurrence when duplicates exist.

Consider:

`[1, 2, 2, 2, 3]`

There are three copies of `2`.

An ordinary exact search may return any one of them.

Applications frequently need more specific information:

- First occurrence
- Last occurrence
- Number of occurrences
- Insertion position
- Range occupied by a value

These problems require slightly different stopping conditions.

---

# 8. First Occurrence

The first occurrence is the smallest index containing the target.

For:

`[1, 2, 2, 2, 3]`

the first occurrence of `2` is index `1`.

When binary search finds `2`, it does not stop.

Instead:

1. Save the current index as a valid answer.
2. Continue searching to the left.
3. Keep the best answer found.

The Python function is `first_occurrence()`.

The JavaScript function is `firstOccurrence()`.

The C++ implementation derives the answer from `lowerBound()`.

The complexity remains:

- Time: `O(log n)`
- Space: `O(1)`

---

# 9. Last Occurrence

The last occurrence is the greatest index containing the target.

For:

`[1, 2, 2, 2, 3]`

the last occurrence of `2` is index `3`.

When a match is found:

1. Save the index.
2. Continue searching to the right.
3. Keep the greatest valid index.

This remains `O(log n)`.

---

# 10. Lower Bound

Lower bound is one of the most important generalized forms of binary search.

It finds:

> The first index `i` such that `values[i] >= target`.

Example:

`values = [10, 20, 20, 30, 40]`

For target `20`:

`lower_bound(20) = 1`

For target `25`:

`lower_bound(25) = 3`

For target `50`:

`lower_bound(50) = 5`

Index `5` is valid even though it is outside the array because it represents the insertion position at the end.

Python provides the standard-library equivalent through `bisect_left`.

The educational implementation is named `lower_bound()`.

---

# 11. Upper Bound

Upper bound finds:

> The first index `i` such that `values[i] > target`.

For:

`[10, 20, 20, 30, 40]`

the upper bound of `20` is index `3`.

The distinction is:

- Lower bound: first value `>= target`
- Upper bound: first value `> target`

This difference is extremely useful when processing duplicate values.

---

# 12. Counting Occurrences

For sorted data:

`count(target) = upper_bound(target) - lower_bound(target)`

Suppose:

`values = [1, 2, 2, 2, 2, 3]`

Then:

`lower_bound(2) = 1`

`upper_bound(2) = 5`

Therefore:

`5 - 1 = 4`

The Python implementation exposes this as `occurrence_count()`.

This is more efficient than scanning the entire array when the data is already sorted.

---

# 13. Finding the Complete Range

The target range can be represented as:

`[first_occurrence, last_occurrence]`

For a sorted array:

`first = lower_bound(target)`

If `values[first]` is not the target, the target is absent.

Otherwise:

`last = upper_bound(target) - 1`

The Python function `occurrence_range()` demonstrates this directly.

---

# 14. Descending Arrays

Binary search is not restricted to ascending arrays.

For:

`[100, 90, 80, 70, 60, 50]`

the comparisons must be interpreted in the opposite direction.

When the midpoint value is greater than the target, the algorithm must move right because smaller values occur toward the right.

The Python function is `binary_search_descending()`.

The JavaScript function is `binarySearchDescending()`.

The C++ program also demonstrates the same mechanism.

The key principle is:

> Binary search needs an ordered search space, not necessarily ascending order.

---

# 15. Rotated Sorted Arrays

A rotated sorted array begins as sorted data and is then shifted around a pivot.

Original:

`[1, 2, 3, 4, 5, 6, 7]`

Rotated:

`[4, 5, 6, 7, 1, 2, 3]`

The complete array is no longer globally sorted, so ordinary binary search cannot be applied directly.

With distinct values, at least one half of the current search interval is sorted.

For every iteration:

1. Inspect the midpoint.
2. Determine which half is sorted.
3. Check whether the target belongs to that sorted half.
4. Search the appropriate half.

The Python implementation is `search_rotated_sorted()`.

The JavaScript implementation is `searchRotatedSorted()`.

The C++ implementation is `searchRotatedSorted()`.

With distinct values, the complexity remains:

`O(log n)`

---

# 16. Rotated Arrays With Duplicates

Duplicates create an important complication.

Consider:

`[2, 2, 2, 3, 2, 2]`

When:

`values[left] == values[middle] == values[right]`

the algorithm cannot always determine which side contains the useful ordering information.

The specialized implementation handles this by shrinking the boundaries:

`left++`

`right--`

This resolves the ambiguity but can reduce the worst-case complexity to:

`O(n)`

For example, an array consisting almost entirely of identical values can force many boundary reductions.

This is an important example of how additional data characteristics can weaken a theoretical logarithmic guarantee.

---

# 17. Nearly Sorted Arrays

A nearly sorted array can have a constrained amount of disorder.

In the provided example:

`[10, 30, 20, 50, 40, 60]`

some elements have moved by one position.

For this particular model, the target can be checked at:

- `middle`
- `middle - 1`
- `middle + 1`

If the target is not found, the algorithm can discard a larger region based on the midpoint comparison.

This technique is not a universal replacement for binary search. It depends on the stated structural guarantee about how far elements can move.

Algorithm correctness depends on matching the algorithm to the actual data invariant.

---

# 18. Peak Search

Binary search can find a property instead of an exact value.

Consider:

`[1, 3, 8, 12, 9, 4, 2]`

The value `12` is a peak.

At a midpoint, compare:

`values[middle]`

with:

`values[middle + 1]`

If the sequence is increasing at that location, a peak must exist to the right.

If it is decreasing or equal, a peak can exist at or to the left.

The implementation demonstrates a broader principle:

> Binary search is useful whenever a decision produces a monotonic elimination rule.

---

# 19. Binary Search on the Answer

One of the most important advanced applications does not search an existing array.

Instead, it searches a numerical answer space.

The C++ and Python programs solve a shipping-capacity problem.

Given package weights and a maximum number of shipping days, determine the minimum daily capacity that can transport all packages while preserving their order.

Suppose the weights are:

`[1, 2, 3, 1, 1]`

and there are `4` days.

The smallest possible capacity must be at least the largest individual package.

The largest possible capacity is the sum of all packages.

Therefore the capacity search range is:

`[max(weights), sum(weights)]`

The important property is feasibility.

For a candidate capacity:

- If it is too small, the shipment cannot finish within the required days.
- Once a capacity becomes sufficient, every larger capacity is also sufficient.

That produces a monotonic predicate:

`False False False False True True True`

Binary search can therefore find the first feasible capacity.

---

# 20. Generic First-True Search

The Python function `first_true()` and C++ template `firstTrue()` demonstrate a general pattern.

The problem is:

> Find the smallest value in a range for which a predicate becomes true.

Suppose:

`predicate(x) = x >= 73`

The result is:

`73`

The essential requirement is monotonicity.

Valid:

`False False False True True True`

Invalid:

`False True False True False`

If the predicate can switch back and forth, eliminating half of the search space is not logically safe.

---

# 21. Integer Square Root

The Python, JavaScript, and C++ implementations demonstrate integer square root through binary search.

For a number such as:

`17`

the mathematical square root is approximately:

`4.123...`

The integer square root is:

`4`

because:

`4² <= 17`

and:

`5² > 17`

The search therefore looks for the greatest integer satisfying:

`x² <= n`

C++ uses division in its comparison:

`middle <= number / middle`

instead of directly calculating:

`middle * middle`

This avoids multiplication overflow for sufficiently large integer values.

---

# 22. Floating-Point Binary Search

Binary search can also approximate real-valued answers.

The Python and JavaScript implementations approximate square roots using repeated interval reduction.

Floating-point searches generally need one of two termination strategies:

1. Fixed number of iterations.
2. Stop when the interval width becomes smaller than a selected tolerance.

A fixed iteration count provides predictable runtime.

A tolerance provides a direct relationship to the desired numerical precision.

Floating-point arithmetic introduces rounding behavior, so exact equality checks should generally be avoided when testing approximate real-number results.

---

# 23. Exponential Search

Exponential search is useful when the upper boundary is initially unknown or when the target is expected relatively close to the beginning.

The algorithm expands the search boundary approximately as:

`1, 2, 4, 8, 16, 32, ...`

Once the target must lie within a known interval, ordinary binary search is applied.

The Python and JavaScript implementations demonstrate this technique using finite arrays to model the general strategy.

Its typical complexity is:

`O(log n)`

for a target within a bounded ordered range.

---

# 24. Sorted Matrix Search

The Python, JavaScript, and C++ implementations demonstrate searching a matrix when the matrix has the following property:

- Every row is sorted.
- Each row starts after the previous row ends.

Example:

`1  3  5  7`

`10 11 16 20`

`23 30 34 60`

The matrix can be treated conceptually as one flattened sorted sequence.

For an index:

`middle`

the row and column are recovered with:

`row = middle // columns`

and:

`column = middle % columns`

This produces:

`O(log(rows × columns))`

search time.

---

# 25. Searching Objects

Binary search does not require primitive integers.

A collection can be ordered by a key such as:

- Product ID
- Employee ID
- Timestamp
- Account number
- Version number
- Database record ID

The Python implementation uses the `Product` data class.

The JavaScript implementation uses the `Product` class.

The C++ case study uses `Shipment`.

The essential requirement is that the objects have a consistent ordering key.

For example, if shipment records are sorted by `shipmentId`, binary search can locate a shipment by that identifier without scanning every record.

---

# 26. C++ Industry Case Study

The C++ program models a logistics shipment registry.

Each shipment contains:

- Shipment ID
- Weight
- Destination

The `ShipmentRegistry` class enforces important data invariants.

Shipment IDs must be strictly increasing.

Shipment weights must be positive.

Destinations must not be empty.

These constraints matter because binary search is only valid when its ordering assumptions remain true.

The registry provides:

`findShipmentIndex()`

for exact identifier lookup.

It also provides:

`findShipment()`

which returns an optional result rather than requiring callers to interpret a raw index.

The range-counting operation uses lower and upper bounds to determine how many shipment IDs fall within an inclusive identifier range.

---

# 27. Why the Shipment Registry Uses Binary Search

Suppose a registry contains millions of records sorted by shipment ID.

A linear scan can require examining a large portion of the collection.

Binary search reduces the number of comparisons from approximately proportional to the number of records to approximately proportional to the logarithm of the number of records.

For example, the comparison growth is conceptually:

`1, 2, 4, 8, 16, 32, ...`

rather than:

`1, 2, 3, 4, 5, 6, ...`

The advantage depends on the data already being ordered and efficiently indexable.

If inserting new records frequently requires maintaining a contiguous sorted vector, insertion itself may be expensive even though searching is fast.

This illustrates an important engineering trade-off:

> Fast lookup does not imply that the entire data structure is cheap to maintain.

---

# 28. Shipping Capacity Case Study

The same C++ program demonstrates a second form of binary search.

The input is a sequence of package weights and a maximum number of days.

The algorithm asks whether a proposed capacity is feasible.

For example:

`[1, 2, 3, 1, 1, 4, 2, 3]`

The feasibility test greedily packs consecutive packages until adding another package would exceed the candidate capacity.

At that point a new shipping day begins.

The candidate capacity is:

- feasible, or
- infeasible.

Because increasing capacity cannot make a feasible shipment infeasible, the predicate is monotonic.

Binary search finds the minimum feasible capacity.

If `S` represents the size of the numeric capacity range, the complexity is approximately:

`O(n log S)`

where the feasibility check costs `O(n)` and binary search performs logarithmically many checks.

---

# 29. C++ Data Structures

The C++ case study uses:

- `std::vector` for ordered records and package weights
- `std::optional` for potentially missing shipments
- `std::pair` for matrix coordinates
- `std::function`-compatible predicates through templates and lambdas
- Classes for domain modeling
- Exceptions for invalid input
- Standard algorithms for test validation

The implementation deliberately avoids external libraries.

---

# 30. Python Implementation

The Python script is designed as a broad study file.

Important functions include:

- `binary_search_exact()`
- `binary_search_half_open()`
- `first_occurrence()`
- `last_occurrence()`
- `lower_bound()`
- `upper_bound()`
- `occurrence_count()`
- `occurrence_range()`
- `binary_search_descending()`
- `search_rotated_sorted()`
- `search_rotated_with_duplicates()`
- `search_nearly_sorted()`
- `find_peak()`
- `minimum_capacity_for_shipping()`
- `integer_square_root()`
- `first_true()`
- `approximate_square_root()`
- `exponential_search()`
- `search_sorted_matrix()`

The Python standard library's `bisect_left()` and `bisect_right()` are also used in randomized testing to compare the educational implementations against established library behavior.

---

# 31. JavaScript Implementation

The JavaScript file demonstrates binary search in a Node.js environment.

It contains equivalent algorithmic forms while also demonstrating JavaScript-specific concerns.

The file includes:

- `Math.floor()` for integer midpoint handling
- Classes for domain objects
- Promises
- `async` and `await`
- Runtime validation
- Error handling
- Performance measurement through `performance.now()`

The asynchronous example simulates retrieving sorted records before performing a binary search.

This illustrates that binary search can be one component inside a larger asynchronous application rather than an isolated algorithm.

The asynchronous operation itself is not made faster by binary search. Instead, once the sorted records are available, binary search reduces the local lookup cost.

---

# 32. Python, JavaScript, and C++ Differences

## Python

Python emphasizes:

- Readability
- Rapid experimentation
- High-level data structures
- Compact algorithm implementation
- Built-in testing and library support

Its `bisect` module already implements boundary-search functionality.

Python is useful for studying the algorithm because the implementation can remain close to the mathematical idea.

## JavaScript

JavaScript is particularly useful when binary search becomes part of application-level logic.

The implementation demonstrates:

- Arrays
- Classes
- Promises
- `async` and `await`
- Runtime validation
- Node.js execution
- Performance measurement

JavaScript's `Number` type also creates numerical considerations that differ from C++ integer arithmetic.

## C++

C++ provides explicit control over:

- Integer types
- Memory representation
- Data structures
- Templates
- Exception handling
- Performance characteristics

The C++ case study demonstrates how binary search can be embedded in a domain model with validation and business constraints.

---

# 33. Recursive Versus Iterative Binary Search

Recursive binary search directly mirrors the mathematical definition:

1. Check the midpoint.
2. Recursively search one half.

Its disadvantage is additional call-stack usage.

For a search depth of `O(log n)`, recursive binary search requires:

`O(log n)`

stack space.

Iterative binary search requires:

`O(1)`

auxiliary space.

For production systems, iterative binary search is frequently attractive because it avoids unnecessary recursion and makes boundary state explicit.

The Python implementation includes `binary_search_recursive()` for comparison.

---

# 34. Common Off-by-One Errors

Binary search is particularly sensitive to boundary mistakes.

Typical errors include:

- Using `left < right` with an inclusive interval.
- Using `left <= right` with a half-open interval without adjusting updates.
- Forgetting `+1` after discarding the midpoint.
- Forgetting `-1` after discarding the midpoint.
- Returning `right` when the desired result is `left`.
- Returning an insertion index as though it were an exact match.
- Accessing `values[middle - 1]` when `middle` is zero.
- Accessing `values[middle + 1]` when `middle` is the final index.

Testing empty and one-element arrays is especially useful for exposing these errors.

---

# 35. Common Logical Mistakes

## Mistake 1: Using binary search on unsorted data

The algorithm's elimination decisions become invalid.

## Mistake 2: Stopping at the first duplicate

An exact match does not imply the first occurrence.

## Mistake 3: Confusing lower bound and upper bound

Lower bound uses:

`>= target`

Upper bound uses:

`> target`

## Mistake 4: Forgetting the target may be absent

A lower-bound index is not automatically proof that the target exists.

The implementation must check:

`index < length`

and:

`values[index] == target`

## Mistake 5: Breaking the invariant

Every iteration should preserve the statement describing where the answer can still exist.

If an update removes a valid candidate, the algorithm becomes incorrect.

---

# 36. Loop Invariants

A loop invariant is a condition that remains true throughout the algorithm.

For inclusive exact search, an important invariant is:

> If the target exists, it must be somewhere inside `[left, right]`.

For lower bound using `[left, right)`:

> The first valid position has not been eliminated and remains within the current search interval.

Writing the invariant explicitly before implementing the algorithm is a powerful way to prevent boundary errors.

A binary search implementation should not be designed only from remembered syntax. It should be derived from:

1. The meaning of the boundaries.
2. The condition being searched.
3. The candidates that can safely be eliminated.
4. The termination condition.

---

# 37. Complexity

| Algorithm | Time | Auxiliary Space |
|---|---:|---:|
| Exact binary search | `O(log n)` | `O(1)` |
| First occurrence | `O(log n)` | `O(1)` |
| Last occurrence | `O(log n)` | `O(1)` |
| Lower bound | `O(log n)` | `O(1)` |
| Upper bound | `O(log n)` | `O(1)` |
| Descending search | `O(log n)` | `O(1)` |
| Rotated search, distinct values | `O(log n)` | `O(1)` |
| Rotated search with duplicates | `O(n)` worst case | `O(1)` |
| Exponential search | `O(log n)` | `O(1)` |
| Recursive binary search | `O(log n)` | `O(log n)` stack |
| Search on answer | `O(log S × predicate cost)` | Usually `O(1)` |

`S` represents the size of the numeric answer range in a binary-search-on-the-answer problem.

---

# 38. Performance Considerations

Binary search has excellent asymptotic search complexity, but real-world performance depends on the surrounding data structure.

A binary search on a contiguous array can have good cache behavior.

A theoretically logarithmic search over a data structure with expensive random access may have different practical characteristics.

The cost of maintaining sorted data also matters.

For a dynamic collection:

- Searching a sorted vector is efficient.
- Inserting into the middle of a vector can require shifting many elements.
- A balanced tree supports ordered insertion and lookup but has different memory and cache behavior.
- A hash table provides expected constant-time lookup for exact keys but does not naturally provide sorted-order queries such as lower bound and range traversal.

Algorithm selection therefore depends on the required operations, not just the complexity of one search operation.

---

# 39. Binary Search Versus Linear Search

| Property | Linear Search | Binary Search |
|---|---|---|
| Requires sorted data | No | Yes, for standard form |
| Worst-case search | `O(n)` | `O(log n)` |
| Simple implementation | Very simple | Boundary-sensitive |
| Works with arbitrary order | Yes | No |
| Supports ordered boundaries | Not efficiently | Yes |
| Good for very small arrays | Often sufficient | Also possible |
| Requires random-access-friendly structure | No | Usually useful |
| Handles dynamic unsorted data directly | Yes | No |

Binary search should not be used automatically merely because it is asymptotically faster.

For tiny collections, a simple linear scan can be perfectly appropriate.

The important question is whether the data and access pattern provide the ordering needed by binary search.

---

# 40. Standard Library Equivalents

Python:

- `bisect_left()` corresponds conceptually to lower bound.
- `bisect_right()` corresponds conceptually to upper bound.

C++:

- `std::lower_bound()`
- `std::upper_bound()`
- `std::binary_search()`

The educational implementations are valuable because they expose the underlying mechanism.

Production software should consider standard-library implementations where they provide the required semantics and have been appropriately tested.

---

# 41. Security Considerations

Binary search itself is not normally a security boundary.

Security concerns arise from the data and system surrounding the algorithm.

Relevant considerations include:

- Validate input before relying on ordering assumptions.
- Avoid integer overflow in midpoint or arithmetic calculations.
- Be careful with maliciously constructed data that triggers worst-case behavior in specialized algorithms.
- Do not assume that a search result is authorization.
- Separate lookup from access-control decisions.
- Validate object identifiers and numeric ranges.
- Do not expose sensitive records merely because their identifiers are searchable.

For security-sensitive systems, finding a record and determining whether the caller is permitted to access it should remain separate operations.

---

# 42. JavaScript Numeric Considerations

JavaScript's ordinary `Number` type uses IEEE 754 double-precision floating-point representation.

Safe integer values are limited to:

`Number.MAX_SAFE_INTEGER`

For values beyond that range, exact integer behavior cannot be assumed when using ordinary `Number` arithmetic.

The JavaScript integer square-root implementation therefore validates safe integers.

For very large exact integers, JavaScript's `BigInt` type can be considered, although mixing `BigInt` and `Number` without explicit conversion is not allowed.

This is a language-specific issue that does not appear in exactly the same form in Python.

---

# 43. C++ Numeric Considerations

C++ integer arithmetic uses fixed-width integer types on typical implementations.

Expressions such as:

`left + right`

can overflow when the values are sufficiently large.

The midpoint pattern:

`left + (right - left) / 2`

reduces that risk when the bounds themselves are valid.

The C++ square-root implementation avoids calculating `middle * middle` directly by comparing:

`middle <= number / middle`

This is a useful general technique when multiplication might overflow.

For production systems, explicit integer types such as `std::int64_t` may be appropriate when numeric ranges are known.

---

# 44. Testing Strategy

The implementations include deterministic and randomized tests.

Deterministic tests cover:

- Empty arrays
- One-element arrays
- First element
- Last element
- Missing values
- Duplicate values
- Negative values
- Rotated arrays
- Rotated arrays with duplicates
- Matrix search
- Shipping capacity
- Integer square root
- Object search

Randomized tests generate sorted arrays and compare the custom boundary functions against standard-library behavior.

Randomized testing is particularly useful for binary search because many bugs occur only at unusual boundary positions.

---

# 45. Important Edge Cases

A robust implementation should consider:

- Empty collection
- Single-element collection
- Target below the minimum
- Target above the maximum
- Target exactly at the minimum
- Target exactly at the maximum
- All elements identical
- Multiple duplicates
- Negative values
- Very large numeric values
- Invalid ordering
- Rotated arrays
- Rotation at index zero
- Rotation at the final possible pivot
- Duplicate values around a rotation boundary
- Invalid shipping days
- Invalid weights
- Empty matrices
- Non-rectangular matrices

The provided programs explicitly exercise many of these cases.

---

# 46. Production Design Considerations

Before introducing binary search into a production component, establish the data invariant.

Important questions include:

1. Is the data guaranteed to be sorted?
2. What key defines the ordering?
3. Can duplicate keys exist?
4. Is the required operation exact lookup or boundary lookup?
5. Does the collection change frequently?
6. Does insertion preserve ordering?
7. Is random access efficient?
8. What happens when the target is absent?
9. What numerical range is possible?
10. Are concurrency controls required?
11. Is stale data possible?
12. Does finding a record imply permission to use it?

Binary search is an algorithmic component, not a complete data-management strategy.

---

# 47. Design Trade-Offs

## Sorted array

Advantages:

- Very fast binary search
- Compact storage
- Good locality for contiguous memory
- Simple implementation

Trade-off:

- Maintaining order can make insertion expensive.

## Hash table

Advantages:

- Excellent expected exact-key lookup

Trade-offs:

- Does not naturally provide ordered traversal.
- Lower-bound and range operations are not its primary strength.

## Balanced search tree

Advantages:

- Maintains ordering
- Supports logarithmic search and insertion in standard balanced structures

Trade-offs:

- More pointer and allocation overhead than a contiguous array
- Different cache behavior

The correct data structure depends on the dominant workload.

---

# 48. When Binary Search Does Not Apply

Ordinary binary search is inappropriate when:

- Data is not ordered.
- The ordering changes during the search.
- Random access is prohibitively expensive.
- The comparison relation does not provide a reliable elimination rule.
- The predicate is not monotonic.
- The data structure does not support the required indexing behavior efficiently.

A sorted array is one common environment, but the deeper requirement is a safely reducible ordered search space.

---

# 49. Deeper Principle: Monotonicity

The most important advanced idea in this lesson is monotonicity.

Traditional binary search often appears to search an ordered list:

`small small small target target large`

But the more general pattern is a monotonic decision function.

For example:

`capacity 1 -> false`

`capacity 2 -> false`

`capacity 3 -> true`

`capacity 4 -> true`

`capacity 5 -> true`

The binary search does not care that these values represent shipping capacity.

It cares that the truth value changes in one direction.

This abstraction explains why binary search appears in:

- Scheduling
- Capacity planning
- Resource allocation
- Optimization
- Numerical computation
- Threshold detection
- Performance limits
- Feasibility problems
- Partition problems

---

# 50. Practical Applications

Binary search and its boundary variants are useful for:

- Searching sorted database exports
- Finding insertion positions
- Locating timestamps
- Version lookup
- Product identifiers
- Employee identifiers
- Score thresholds
- Price thresholds
- Capacity planning
- Scheduling limits
- Numerical approximation
- Finding transition points
- Range queries
- Search indexes
- Sorted logs
- Ranked datasets
- Algorithmic optimization

The actual implementation should depend on the data structure and the exact semantics required by the application.

---

# 51. Implementation Checklist

Before implementing binary search:

- Confirm the search space is ordered.
- Define what `left` means.
- Define what `right` means.
- Choose inclusive or half-open intervals.
- Define the midpoint.
- Define the loop condition.
- Define what happens when the midpoint matches.
- Define the exact update for a midpoint that is too small.
- Define the exact update for a midpoint that is too large.
- Confirm that every iteration shrinks the search space.
- Test empty input.
- Test one element.
- Test both boundaries.
- Test an absent target.
- Test duplicates when relevant.
- Check numeric overflow risks.
- Check the complexity of the underlying data structure.

---

# 52. Files and Execution

The Python implementation can be executed directly with a modern Python installation.

The JavaScript implementation is designed for Node.js.

The C++ implementation targets C++17 or later.

The C++ program can be compiled with a command equivalent to:

`g++ -std=c++17 -O2 binary_search.cpp -o binary_search`

The resulting executable runs the demonstrations, case study, validation checks, deterministic tests, randomized tests, and performance measurement.

---

# 53. Key Distinctions

The most important distinctions from this implementation are:

- Exact search asks whether a specific value exists.
- First occurrence asks for the smallest matching index.
- Last occurrence asks for the largest matching index.
- Lower bound finds the first value greater than or equal to a target.
- Upper bound finds the first value strictly greater than a target.
- Rotated-array search exploits the fact that one side remains sorted.
- Duplicate-aware rotated search may degrade to linear time.
- Nearly sorted search relies on a specific bounded-disorder assumption.
- Peak search searches for a structural property.
- Binary search on the answer searches a numerical range using a monotonic feasibility predicate.
- Exponential search first discovers a useful interval and then applies binary search.
- Floating-point binary search approximates a numerical boundary rather than finding an exact array index.

These are variations of one fundamental idea:

> Safely eliminate a portion of an ordered or monotonic search space.
