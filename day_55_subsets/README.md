# Subset Algorithms and Constraint-Based Search

## Scope

This project implements subset generation and search in Python, JavaScript, C++17, Java 17, and PostgreSQL. The implementations cover four related operations:

- **Subset generation:** enumerate every selection of input positions.
- **Duplicate handling:** avoid repeated value combinations when input elements have equal values.
- **Subset sum:** find selections whose elements total a specified target.
- **Constrained subsets:** retain selections satisfying size, sum, and custom conditions.

A subset contains zero or more selected elements. The empty subset is valid, and every set of \(n\) distinct input positions has \(2^n\) possible selections.

For example, the input `[1, 2, 2]` has eight index-distinct subsets but only six unique value-based subsets. The distinction matters whenever repeated input values represent interchangeable choices rather than separately identifiable items.

## Core Algorithms

### Generate subsets

The iterative generation algorithm starts with the empty subset. For each input element, it copies every existing subset and appends the element to each copy.

For an input containing three elements, the process grows as follows:

    Start:       []
    Add 1:       [], [1]
    Add 2:       [], [1], [2], [1, 2]
    Add 3:       [], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]

The iterative implementation is useful when the result collection must be available as a complete list. It preserves input order and treats equal values at different positions as separate choices.

There are \(2^n\) subsets. Materializing all subsets requires exponential time and memory. Because the output itself contains up to \(n2^{n-1}\) element occurrences, no algorithm that explicitly returns every subset can avoid the cost of producing that output.

### Duplicate handling

The unique-subset algorithm sorts the input and uses depth-first search. At each recursion level, it skips an element when that element equals the previous element at the same level.

This rule prevents equivalent selections from being generated more than once without incorrectly eliminating combinations containing multiple copies of a value.

For `[1, 1, 2]`, the unique subsets are:

- `[]`
- `[1]`
- `[1, 1]`
- `[1, 2]`
- `[1, 1, 2]`
- `[2]`

The order depends on the implementation. Python, JavaScript, and Java sort the values before unique-subset search, while the C++ implementation follows the same ordering rule.

Value-based deduplication is not appropriate when equal values represent distinct identities. If two separate inventory units must remain distinguishable, each element should carry an identifier and duplicate handling should use that identifier instead.

### Subset sum

Subset-sum enumeration searches for combinations whose total equals a target. The recursive search makes two decisions for each input position: exclude the element or include it.

When the remaining target reaches zero, the current selection is a valid answer. Search continues because adding zero-valued elements can produce other valid subsets.

For `[1, 2, 2, 3]` and target `4`, the unique value-based answers are `[1, 3]` and `[2, 2]`.

Negative numbers are supported. Sorting alone does not justify pruning a branch because negative values can reduce a sum that has already exceeded the target.

Two different operations are provided:

- **Enumeration** returns all matching subsets and can require exponential time and space.
- **Existence checking** determines whether a target is reachable without constructing the complete answer list.

The existence-checking implementations maintain a collection of reachable sums. This approach is useful for decision queries, although the number of reachable sums can itself grow exponentially. The algorithms use integer arithmetic and explicitly validate input types where appropriate.

### Constrained subsets

Constrained enumeration adds rules to the include-or-exclude search. A candidate can be accepted only when it satisfies the configured limits.

The supplied implementations support:

- Minimum and maximum subset size.
- Minimum and maximum sum.
- A custom predicate for domain-specific requirements.

Examples include selecting between two and three components whose combined cost lies within a budget, or identifying groups that meet a capacity requirement.

Constraints must be validated before searching. Invalid size intervals and contradictory sum limits are rejected rather than silently producing misleading results.

The implementation uses pruning when the current selection already exceeds the permitted maximum size. More aggressive sum pruning requires care: with negative numbers, partial sums cannot safely be used to infer that a branch will remain outside a target interval.

## Python Implementation

The Python script defines `generate_subsets`, `unique_subsets`, `subset_sum`, `constrained_subsets`, and `subset_sum_exists`.

- Lists represent selections and result collections.
- Recursive functions maintain a mutable path and copy it when recording a result.
- `SubsetResult` is a frozen dataclass containing a selected tuple and its sum.
- `validate_integers` rejects non-integer values, including booleans, which Python otherwise treats as integers.
- Assertions verify empty inputs, duplicate values, zero-sum combinations, and reachability.

The script uses only the Python standard library. The recursive implementation is easy to extend with new conditions, but very large inputs can exceed the recursion limit or consume excessive memory. Input size should therefore be bounded in production services.

## JavaScript Implementation

The JavaScript file implements the same algorithmic operations using arrays, `Set`, and explicit validation. Its `SubsetSearch` class extends Node.js `EventEmitter` to expose search progress.

The search emits:

- `match` when a target-matching subset is discovered.
- `progress` periodically during traversal.
- `complete` when enumeration finishes.

The asynchronous traversal yields through `setImmediate` periodically, allowing other event-loop work to proceed. This does not reduce the exponential search complexity, and it does not make an unrestricted search inexpensive.

JavaScript validation uses `Number.isSafeInteger` to prevent silent loss of integer precision. Applications handling larger numeric ranges should use `BigInt` consistently, including in sum calculations and comparisons.

## C++17 Implementation

The C++ program uses a `SubsetEngine` class to separate algorithm behavior from console output.

- `vector<int>` represents input values and subsets.
- Recursive lambdas implement depth-first enumeration.
- Sorting and sibling skipping provide duplicate suppression.
- `set<long long>` tracks reachable sums for existence queries.
- `SubsetRecord` associates a selected subset with its calculated total.
- Checked addition detects overflow in sum calculations.

The constrained-search method accepts a predicate, allowing callers to enforce domain-specific rules without changing the search engine.

The design offers direct control over containers and value movement. Its main trade-off is that materialized results still require exponential memory. Large workloads should use bounded inputs, result limits, or a streaming interface rather than storing every candidate.

## Java 17 Implementation

The Java program models search parameters and results with records:

- `SubsetResult` contains an immutable copy of the selected values and their sum.
- `SizeConstraint` validates the permitted subset-size interval.
- `SumConstraint` supports optional lower and upper sum bounds.
- `SubsetService` owns generation, search, and validation operations.

The constrained search accepts a `Predicate<List<Integer>>` for additional policy evaluation. Immutable copies protect returned results from changes to the internal recursion path.

`Math.addExact` and `Math.subtractExact` detect arithmetic overflow. The service rejects null input and null elements. The program requires Java 17 or later and uses no third-party dependencies.

The immutable result model is appropriate for service boundaries where callers should not be able to alter previously calculated results. It does not remove the cost of retaining exponentially many selections.

## PostgreSQL Data Model

The SQL script uses the `subset_lab` schema to represent jobs, ordered input values, and generated results.

    subset_jobs
        |
        +---- subset_items
        |
        +---- subset_results

### Tables and constraints

**`subset_jobs`** stores the target sum, size bounds, sum bounds, duplicate policy, and processing status. Check constraints reject invalid ranges and unsupported status values.

**`subset_items`** stores each input value with its position. The unique constraint on `(job_id, position)` preserves a stable position for each input occurrence.

**`subset_results`** stores each accepted selection as an integer array, with its size and sum. A unique constraint on `(job_id, ordinal)` gives each stored result a job-specific position.

Indexes support retrieval of input items in position order and filtering results by sum or size. These indexes are useful for the queries included in the script, though they add storage and write overhead.

### Recursive enumeration

The `enumerate_subsets` procedure builds a recursive sequence of include-or-exclude decisions using a recursive CTE. Each completed candidate contains an array of selected values and its calculated sum.

The procedure:

1. Locks the requested job row.
2. Validates its state and size limits.
3. Transitions the job to `running`.
4. Clears prior results.
5. Enumerates candidate selections.
6. Applies size, sum, and target conditions.
7. Deduplicates arrays when requested.
8. Stores the accepted results and marks the job `completed`.

If processing fails, the exception handler marks the running job as `failed` and rethrows the error. Transaction boundaries determine whether the caller commits or rolls back the changes.

The result-validation trigger independently checks the stored size, sum, permitted bounds, and job state. This prevents ordinary insert or update operations from bypassing the central result rules.

### Queries and operational behavior

The final SQL statements retrieve individual subsets, aggregate result counts and sum ranges, and report the number of empty, zero-sum, and target-matching subsets.

A deliberately invalid result insert demonstrates database-level rejection. The exception is handled inside a nested PL/pgSQL block so the demonstration can continue.

The recursive CTE materializes candidates and is suitable only for small input sets. Its number of states grows exponentially. Production use requires limits on input cardinality, execution time, and result volume. Database constraints validate persisted results but do not make exhaustive enumeration scalable.

The `unique_values` setting deduplicates identical value arrays. When repeated input values are intended to represent distinct choices, set this option to false. Because the stored result contains values rather than source positions, distinct positional selections that produce the same array cannot be distinguished in the result table.

## Correctness and Edge Cases

| Case | Required behavior |
|---|---|
| Empty input | Return the empty subset |
| Repeated values | Preserve duplicates in ordinary generation; suppress equivalent combinations in unique mode |
| Target zero | Include the empty subset and every other valid zero-sum selection |
| Negative values | Allow positive and negative elements to combine to the target |
| Invalid bounds | Reject inconsistent size or sum constraints |
| Invalid numeric input | Reject values outside the supported integer model |
| Large input | Recognize that enumeration grows exponentially |
| Arithmetic overflow | Detect overflow in implementations that provide checked arithmetic |
| Failed database job | Record failure and propagate the database error |

## Complexity

Let \(n\) be the number of input elements.

| Operation | Time complexity | Additional or output space |
|---|---|---|
| Generate all subsets | \(O(n2^n)\) | \(O(n2^n)\) for materialized output |
| Generate unique subsets | \(O(n2^n)\) worst case, excluding sorting details | Proportional to the number and total size of returned subsets |
| Enumerate target matches | \(O(n2^n)\) worst case | Proportional to returned matches and recursion depth |
| Reachable-sum existence | Depends on the number of distinct reachable sums; worst case exponential | Proportional to the number of reachable sums |
| Constrained enumeration | \(O(n2^n)\) worst case | Proportional to accepted output and recursion depth |

Sorting-based algorithms add \(O(n\log n)\) preprocessing time. These bounds describe general worst-case behavior. Duplicate-heavy inputs can reduce the number of unique subsets, but they do not eliminate the exponential worst case.

## Security and Operational Boundaries

Subset algorithms can be abused through excessively large input collections, especially when every possible result is materialized. Applications should enforce input-size limits, result-count limits, execution deadlines, and memory budgets.

The PostgreSQL procedure runs with the caller's database privileges and does not use dynamic SQL. Access controls should restrict who can create jobs, modify their inputs, execute enumeration, or delete results. The trigger validates individual results, while application-level permissions must control which jobs a caller may access.

All implementations are educational reference programs rather than unbounded production search services. Their central algorithms are executable, but workload limits and domain-specific constraints must be chosen for the actual application.
