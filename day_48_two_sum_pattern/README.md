# Two-Sum Pattern: Complement Lookup, Pair Counting, and Difference Search

## Problem definition

The two-sum pattern identifies two distinct elements in a collection whose values satisfy a numeric relationship. Given an array \(A\) and a target \(T\), the classic problem asks for indices \(i\) and \(j\) such that

\[
i \ne j,\qquad A[i]+A[j]=T
\]

The same underlying pattern supports transaction reconciliation, matching records, identifying combinations of measurements, and detecting pairs separated by a specified difference.

The implementation must distinguish three different results:

- **Index pair:** Two positions in the original collection. Equal values at different positions can form a valid pair.
- **Value pair:** A distinct combination of numeric values, independent of how many records contain those values.
- **Pair count:** The number of valid combinations of distinct positions. Duplicate records can increase this count.

These results are related, but they are not interchangeable.

## Complement lookup

For a current value \(x\), rearranging the target equation gives

\[
y=T-x
\]

The required value \(y\) is the complement of \(x\).

A hash map stores previously encountered values and their positions. When the next value arrives, the algorithm checks whether its complement is already present. If it is, the algorithm has found a valid pair.

The order of operations is important. The complement must be checked before the current value is inserted. Otherwise, when \(T=2x\), a single element could incorrectly match itself.

For a collection of \(n\) elements, the hash-map algorithm takes expected \(O(n)\) time and \(O(n)\) auxiliary space. Hash-table operations are expected constant time, although adversarial collisions and implementation-specific behavior can affect practical performance.

### Duplicate handling

Consider the collection `[3, 3]` with target `6`.

The first occurrence is stored at index `0`. When the second occurrence is processed, its complement is already present, so the returned pair is `(0, 1)`.

By contrast, `[3]` cannot satisfy the target. A value is not a separate record merely because the algorithm needs two operands.

The Python and JavaScript implementations preserve the earliest position for each value in the single-result search. This produces a predictable result without changing the expected linear-time complexity.

## Pair counting

Finding one pair is different from counting all pairs.

For each new value \(x\), the number of new pairs is equal to the number of previously encountered occurrences of \(T-x\). A frequency map records how many such occurrences exist.

The running total is updated before the current value's frequency is increased. This ensures that every counted pair uses two distinct positions and that each unordered pair is counted exactly once.

For example, `[2, 2, 2, 2]` with target `4` has

\[
\binom{4}{2}=\frac{4(4-1)}{2}=6
\]

valid index pairs. There is only one distinct value pair, `(2, 2)`, but six combinations of records.

For two distinct values \(a\) and \(b\), their contribution to the pair count is

\[
f(a)f(b)
\]

where \(f(x)\) denotes the frequency of value \(x\).

When both values are equal, the contribution is

\[
\frac{f(a)(f(a)-1)}{2}
\]

The frequency-based Python and SQL implementations use these relationships directly. This is useful when the desired output is an aggregate rather than a list of individual matching records.

## Difference-based lookup

Two-sum reasoning also applies when the relationship is a difference rather than a sum.

### Signed difference

For an ordered pair of positions, a signed difference \(D\) satisfies

\[
A[j]-A[i]=D
\]

Rearranging gives

\[
A[i]=A[j]-D
\]

The algorithm searches for the required earlier value using the same complement-lookup mechanism as two-sum.

A negative difference is valid. For example, a difference of `-2` means the value at the right position must be two less than the value at the left position.

### Absolute difference

An absolute difference \(D\) satisfies

\[
|A[j]-A[i]|=D
\]

For a positive \(D\), the current value \(x\) may match either \(x-D\) or \(x+D\). Both candidates must be checked.

When \(D=0\), a match requires equal values at distinct positions. A single occurrence cannot form a pair.

The Python, JavaScript, C++, and Java implementations explicitly reject negative absolute-difference thresholds. Silently accepting a negative threshold would make the API ambiguous.

## Implementation details

### Python

The Python script uses dictionaries and `Counter` to implement the core algorithms.

- `two_sum` returns the first matching pair of indices, or `None` when no pair exists.
- `two_sum_all_index_pairs` preserves every matching combination of positions. It stores a list of previous indices for each value.
- `count_pairs` counts combinations incrementally without materializing the pair list.
- `count_pairs_by_frequency` computes the result from value frequencies.
- `find_pair_with_difference` handles signed differences.
- `find_pair_with_absolute_difference` checks both directional candidates.
- `two_sum_sorted` demonstrates the two-pointer alternative for sorted input.
- `two_sum_unique_value_pairs` returns distinct numeric combinations rather than individual record pairs.

The test suite includes duplicates, negative values, empty input, missing matches, invalid difference thresholds, and comparisons against a brute-force reference implementation.

The brute-force algorithm has \(O(n^2)\) worst-case time complexity. Its main purpose here is correctness verification on small inputs, where its simplicity makes it a useful reference.

### JavaScript

The JavaScript file uses `Map` rather than ordinary objects for numeric-keyed lookup. A `Map` avoids object-property coercion concerns and provides explicit membership checks.

The `allTwoSumPairs` function is a generator. It yields matches as they are discovered, allowing a consumer to process results incrementally instead of requiring a complete result array. The number of yielded results can still be quadratic.

The input-validation functions require safe integers. JavaScript's ordinary `Number` type cannot represent every integer exactly, so arithmetic outside the safe-integer range can produce incorrect complement calculations.

The sorted-array function validates its ascending-order precondition. The two-pointer algorithm relies on sorted values: if the current sum is too small, moving the left pointer right increases the sum; if it is too large, moving the right pointer left decreases it.

The tests compare optimized results with a brute-force implementation and check invalid inputs and duplicate behavior.

### C++ case study

The C++ program models a warehouse or financial reconciliation system in which transaction amounts are stored as integer cents.

The `PairAnalytics` class separates several responsibilities:

- `findTwoSum` returns one matching pair of transaction positions.
- `findAllPairs` enumerates every valid pair.
- `countPairs` calculates the number of matches without building the full result.
- `uniqueValuePairs` aggregates repeated amounts into distinct numeric combinations.
- The difference-search methods find ordered or absolute-difference matches.
- `findSortedTwoSum` validates sorted input before using the two-pointer algorithm.

The implementation uses `unordered_map` for expected constant-time lookup and vectors to retain transaction positions. The all-pairs operation stores multiple positions for each amount, ensuring that repeated transaction values are not lost.

Widened intermediate arithmetic using `__int128` protects subtraction and addition operations against signed 64-bit overflow on compilers that support this type, including common GCC and Clang environments. It is a compiler extension rather than a standard C++17 integer type, so a strictly portable implementation would need checked arithmetic helpers instead.

The case study uses assertions to verify duplicate counting, single-record rejection, invalid difference thresholds, and sorted-input validation. In production systems, error reporting and overflow handling should remain explicit rather than depending solely on assertions.

### Java implementation

The Java program represents each record using an immutable `Transaction` record containing a reference and an amount in cents.

`TransactionMatcher` provides methods for finding a single pair, enumerating every pair, counting pairs, returning unique amount combinations, and searching for signed or absolute differences.

`Optional<IndexPair>` distinguishes a successful match from the absence of a match without requiring sentinel indices. Immutable lists prevent callers from accidentally modifying returned pair collections.

The implementation uses `Math.subtractExact` and `Math.addExact` where arithmetic overflow must be detected. This is particularly important when working with 64-bit monetary values near their numeric limits.

`HashMap` supports complement lookup, while `TreeMap` provides ordered frequency processing for unique amount pairs. `Math.addExact` also detects overflow in accumulated pair counts.

The Java example keeps transaction identity separate from transaction amount. This allows two transactions with equal amounts to be treated as separate records and makes the distinction between matching records and matching values explicit.

### PostgreSQL data model

The SQL script models transaction reconciliation using two tables.

**`transactions`** stores transaction references, integer-cent amounts, timestamps, and processing status. A primary key identifies each record, while a unique constraint prevents duplicate transaction reference codes.

**`reconciliation_targets`** stores the target amount, a description, and the transaction status required for matching.

Check constraints restrict allowed status values and reject blank identifiers. The amount index supports searches by complementary amount while excluding records with status `excluded`. A timestamp index supports recent-record queries.

The complement join uses the equation

`b.amount_cents = target_cents - a.amount_cents`

and the condition `b.transaction_id > a.transaction_id` to avoid counting an unordered pair twice or pairing a row with itself.

The script also demonstrates:

- Counting matching record pairs through a join.
- Reusing a view to retrieve pairs for a fixed target.
- Evaluating several targets through a lateral join.
- Counting pairs from grouped frequencies.
- Finding signed and absolute-difference matches.
- Updating matched records within a transaction boundary.
- Returning zero for targets with no matches through a left join.

The absolute-difference query converts amounts to `NUMERIC` before subtraction so the absolute-value calculation does not overflow a signed 64-bit integer during subtraction.

The transaction example uses a savepoint and rolls back the demonstration update, preserving the original sample state. This illustrates transactional control without leaving the sample data in a changed state.

The database constraints validate record structure and allowed statuses. They do not, by themselves, guarantee that a reconciliation pair remains unique under concurrent updates. A production reconciliation service may require explicit locking, a reconciliation-group table, uniqueness constraints on assigned transaction records, or serializable transaction handling, depending on the business rules.

## Complexity and design trade-offs

| Method | Expected time | Auxiliary space | Best use |
|---|---:|---:|---|
| Hash-map two-sum | \(O(n)\) | \(O(n)\) | Find one matching pair |
| All-pairs lookup | \(O(n+k)\) | \(O(n+k)\) | Enumerate \(k\) matches |
| Incremental pair counting | \(O(n)\) | \(O(u)\) | Count matches without storing them |
| Frequency-based counting | \(O(n+u\log u)\) in the sorted Python implementation | \(O(u)\) | Aggregate duplicate values |
| Sorted two-pointer lookup | \(O(n)\) | \(O(1)\) | Search an already sorted sequence |
| Brute-force search | \(O(n^2)\) | \(O(1)\) | Reference implementation and small test cases |

Here, \(n\) is the number of records, \(u\) is the number of distinct values, and \(k\) is the number of matching index pairs.

The sorted two-pointer method uses constant auxiliary space when the input is already sorted. Sorting an unsorted collection first generally costs \(O(n\log n)\) time and may require additional space. Sorting also changes the relationship between positions in the sorted array and positions in the original collection unless the original indices are retained.

## Common correctness failures

- **Checking the current element too early:** Inserting an element before checking its complement can allow a record to match itself.
- **Ignoring duplicates:** A dictionary containing only one count or position may be insufficient when all pairs or pair counts are required.
- **Counting the same pair twice:** Enumerating both `(i, j)` and `(j, i)` incorrectly doubles an unordered pair count.
- **Checking only one absolute-difference direction:** Searching only `x - D` misses valid pairs whose earlier value is `x + D`.
- **Using two pointers on unsorted data:** Pointer movement is justified only by sorted order.
- **Using floating-point currency amounts:** Binary floating-point representations can introduce rounding errors. Integer cents or a suitable exact decimal type is safer for monetary data.
- **Ignoring integer overflow:** Complement calculations, sums, and aggregate pair counts may exceed the chosen numeric type.
- **Confusing unique values with unique records:** Distinct transaction references can have the same amount and must remain separate when record-level matching is required.

## Practical applications

The complement pattern is useful when two independently recorded amounts must explain a target total. The difference pattern is useful when measurements, prices, or timestamps represented as integers must be separated by a fixed threshold.

The choice of result representation depends on the operational requirement. A search interface may need only one pair, an audit report may need every matching record, and an analytics query may need only a count. Choosing the appropriate representation avoids unnecessary memory use and makes duplicate handling explicit.
