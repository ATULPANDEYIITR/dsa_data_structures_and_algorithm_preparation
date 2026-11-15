# Top-K Problems: Selection, Frequency Ranking and Proximity Search

## Technical Scope

Top-K problems select a limited number of elements from a collection according to a ranking rule.

They are common in:

- Ranking search results.
- Identifying the highest-performing records.
- Selecting the most frequent events.
- Finding nearest geographical or numerical observations.
- Processing streaming measurements.
- Building recommendation and analytics systems.

This project implements four distinct problems:

| Problem | Objective | Primary technique |
|---|---|---|
| Kth largest | Find the element at descending rank K | Min-heap or Quickselect |
| Kth smallest | Find the element at ascending rank K | Max-heap |
| Top K frequent | Find the K most frequently occurring distinct values | Hash map and heap |
| K closest elements | Find K values closest to a target | Binary search |

All implementations use integer inputs and explicitly validate selection boundaries.

## 1. Kth Largest Element

Given an unsorted array, find the element occupying position K when values are ordered from largest to smallest.

Example:

Input: `[3, 2, 1, 5, 6, 4]`

K: `2`

Output: `5`

### Min-Heap Approach

Maintain a min-heap containing at most K elements.

For each input value:

1. Insert the value.
2. If the heap contains more than K elements, remove its smallest element.
3. Continue until all values have been processed.

The heap contains the K largest elements encountered so far. Its root is the smallest among those K elements.

Therefore, the root is the Kth largest element after processing the entire input.

**Complexity**

- Time: `O(n log k)`
- Auxiliary space: `O(k)`

This approach is useful when K is substantially smaller than the input size.

### Quickselect Approach

Quickselect uses partitioning to locate the required position without completely sorting the array.

The implementation uses three-way partitioning:

- Values greater than the pivot.
- Values equal to the pivot.
- Values smaller than the pivot.

The algorithm continues searching only the partition containing the requested rank.

Random pivot selection reduces the likelihood of consistently poor partitions.

| Property | Complexity |
|---|---|
| Average time | `O(n)` |
| Worst-case time | `O(n²)` |
| Auxiliary partition space | `O(1)` |
| Additional copied input | `O(n)` |

Three-way partitioning is especially useful when the input contains many duplicate values.

### Kth Largest Versus K Distinct Largest

The implementations treat repeated occurrences as separate positions.

For `[8, 8, 5]`:

- First largest: `8`
- Second largest: `8`
- Third largest: `5`

Finding the second distinct largest value is a different problem and requires deduplication before selection.

## 2. Kth Smallest Element

Kth smallest selects an element according to ascending order.

Example:

Input: `[7, 10, 4, 3, 20, 15]`

K: `3`

Output: `7`

### Max-Heap Approach

Maintain a max-heap containing at most K elements.

When a new value is inserted and the heap exceeds K elements, remove its largest element.

After processing the complete input, the root is the Kth smallest element.

**Complexity**

- Time: `O(n log k)`
- Auxiliary space: `O(k)`

The choice of heap direction is important:

| Problem | Heap retained | Root |
|---|---|---|
| Kth largest | K largest elements | Smallest retained |
| Kth smallest | K smallest elements | Largest retained |

The root identifies the required boundary of the retained selection.

## 3. Top K Frequent Elements

Top K frequent selects distinct values according to their occurrence counts.

Example:

Input: `[1, 1, 1, 2, 2, 3]`

K: `2`

Output: `[1, 2]`

The frequency distribution is:

| Value | Frequency |
|---|---:|
| 1 | 3 |
| 2 | 2 |
| 3 | 1 |

### Frequency Aggregation

A hash map stores the number of occurrences of each value.

For every input element:

- Retrieve its existing count.
- Increment the count.
- Insert a new entry when the value has not previously appeared.

If the input contains N elements and U unique values, frequency aggregation requires expected `O(n)` time and `O(u)` space.

### Heap-Based Ranking

The implementations use a bounded heap containing at most K frequency records.

Each record contains:

- Value.
- Frequency.

The ranking policy is:

1. Higher frequency ranks first.
2. Smaller numerical value wins a frequency tie.

This produces deterministic results.

For example:

Input: `[4, 3, 2, 1]`

K: `2`

Output: `[1, 2]`

All four values have equal frequencies, so the smaller values are selected.

**Complexity**

- Frequency aggregation: `O(n)` expected time.
- Heap selection: `O(u log k)`.
- Final ordering: `O(k log k)`.
- Auxiliary space: `O(u + k)`.

### Bucket-Based Ranking

The Python implementation also demonstrates frequency buckets.

An array of buckets groups values by occurrence count.

A value appearing four times belongs to bucket four.

The algorithm examines buckets from highest frequency to lowest frequency.

Sorting values within each bucket provides deterministic tie-breaking.

This approach is useful when the maximum possible frequency is bounded by the input size.

## 4. K Closest Elements

This problem selects K values closest to a specified target from an already sorted array.

Example:

Input: `[1, 2, 3, 4, 5]`

K: `4`

Target: `3`

Output: `[1, 2, 3, 4]`

### Ranking Rule

The distance of an element X from target T is:

`abs(X - T)`

When two elements have equal distances, the smaller value wins.

For target `3`:

| Value | Distance |
|---|---:|
| 1 | 2 |
| 2 | 1 |
| 3 | 0 |
| 4 | 1 |
| 5 | 2 |

Both `1` and `5` are equally distant, so the smaller value is preferred.

### Binary Search on Window Boundaries

The important property is that the input is sorted.

The selected K closest values form a contiguous window.

For an array of length N, the possible window starting positions range from:

`0` to `N - K`

Binary search determines the optimal starting position.

At each iteration, compare:

- Distance from the target to the left boundary.
- Distance from the target to the first element immediately outside the candidate window.

If the left boundary is farther away, shift the window right.

Otherwise, retain the left half of the search range.

**Complexity**

- Binary search: `O(log(n-k))`
- Returning the selected elements: `O(k)`
- Total: `O(log(n-k) + k)`

The algorithm avoids sorting all elements by distance.

### Why This Is Different from General Top-K

General nearest-element selection does not always have a sorted input.

A heap can solve the general case in `O(n log k)` time.

The binary-search window algorithm is more efficient when the input is sorted and the selected values must be contiguous.

## 5. Algorithm Comparison

| Technique | Main use | Time complexity | Space complexity |
|---|---|---|---|
| Full sorting | General ranking | `O(n log n)` | `O(n)` |
| Bounded min-heap | Kth largest | `O(n log k)` | `O(k)` |
| Bounded max-heap | Kth smallest | `O(n log k)` | `O(k)` |
| Quickselect | Kth element | Average `O(n)` | `O(1)` auxiliary |
| Hash map + heap | Top K frequent | `O(n + u log k)` expected | `O(u + k)` |
| Frequency buckets | Top K frequent | `O(n + u log u)` with tie sorting | `O(n + u)` |
| Binary-search window | K closest sorted elements | `O(log(n-k) + k)` | `O(k)` |

Here:

- N represents the number of input elements.
- K represents the requested selection size.
- U represents the number of distinct values.

The best technique depends on input ordering, K relative to N, duplicate frequency, and memory constraints.

## 6. Implementation Architecture

### Python

The Python implementation uses:

- `heapq` for bounded selection.
- `Counter` for frequency aggregation.
- Lists and dictionaries for intermediate data.
- Three-way Quickselect for average-linear selection.
- Dataclasses for immutable result records.
- Custom exceptions for invalid requests.
- `unittest` for automated validation.

The `TopKService` provides a consistent interface for the four operations.

The script includes sorting, heap, Quickselect, and bucket-based alternatives so that different algorithmic tradeoffs can be compared.

### JavaScript

The JavaScript implementation uses a custom comparator-driven binary heap.

The heap supports:

- Insertion.
- Root inspection.
- Root removal.
- Heap restructuring.

`Map` stores frequencies, while `EventEmitter` reports completed and failed operations.

The `TopKEngine` provides asynchronous execution and bounded batch concurrency.

Batch processing preserves the original request order and isolates individual request failures.

This design is useful for service-oriented processing where multiple selection requests must be evaluated independently.

### C++17

The C++ implementation uses:

- `priority_queue` for heap selection.
- `unordered_map` for frequency counting.
- STL sorting for deterministic ranking.
- Three-way randomized Quickselect.
- Exception-based input validation.
- Assertions for test verification.

The implementation uses `long long` when calculating target distances to avoid integer subtraction overflow.

The heap-based design limits retained state to K elements for the two order-statistic operations.

### Java 17

The Java implementation models requests and responses using records.

Its architecture separates:

- Operation types.
- Immutable request data.
- Immutable response data.
- Selection service.
- Validation exceptions.

The service uses `PriorityQueue`, collections, streams, and immutable result lists.

The batch interface executes multiple requests through the same service while retaining a consistent response structure.

The Java implementation represents a service-oriented design rather than a direct translation of the other languages.

## 7. PostgreSQL Data Model

The SQL implementation uses a dedicated `topk` schema.

### Relational Structure

The principal relationships are:

`datasets`

- Stores dataset metadata.
- Assigns a unique identifier to each dataset.

`dataset_values`

- Stores individual integer observations.
- Associates each observation with its dataset.
- Preserves original position.
- Enforces unique positions within a dataset.

`selection_requests`

- Records requested operations.
- Stores K and optional target values.
- Tracks execution status.
- Stores results and failure information.

`selection_audit`

- Records execution events.
- Stores structured JSONB event details.
- Supports request-level audit retrieval.

### Database Integrity

The schema uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Referential deletion rules.
- Performance-oriented indexes.

The request table restricts operation names to supported values.

It also enforces the requirement that K closest requests must include a target.

The validation function checks dataset availability, operation validity, K boundaries, and sorted-input requirements.

### SQL Ranking

The frequency-ranking query uses:

- `GROUP BY` to calculate frequencies.
- `COUNT(*)` to aggregate occurrences.
- `DENSE_RANK()` to rank frequency groups.
- Value-based ordering for deterministic ties.

The Kth element queries use ordered selection with `OFFSET` and `LIMIT`.

The closest-element query ranks values using absolute distance and numerical tie-breaking.

Casting subtraction to `BIGINT` prevents overflow for the supported integer input type.

### Transaction and Audit Behavior

The stored procedure:

1. Validates the request.
2. Creates a request record.
3. Changes its state to running.
4. Records an audit event.
5. Executes the selection function.
6. Stores the result.
7. Marks the request completed.
8. Records completion.

An exception handler attempts to record failure information before re-raising the exception.

PostgreSQL transaction semantics are important here: re-raising an exception can roll back the procedure's statement-level effects. Durable failure auditing therefore requires a separate transaction or an external audit mechanism.

## 8. Validation and Edge Cases

The five implementations account for the following conditions:

| Condition | Expected behavior |
|---|---|
| K is zero for Kth selection | Reject |
| K exceeds input length | Reject |
| K is zero for Top K | Return empty result |
| K exceeds distinct count for Top K | Reject |
| Empty input with Kth selection | Reject |
| Empty input with Top K = 0 | Return empty result |
| Duplicate integer values | Preserve occurrence-based ranking |
| Equal frequencies | Smaller integer wins |
| Unsorted closest-element input | Reject |
| Closest selection with K = 0 | Return empty result |
| Missing closest target | Reject |
| Invalid operation | Reject |
| Invalid batch request | Isolate failure in JavaScript batch execution |

The distinction between input occurrences and distinct values is important.

Kth largest and Kth smallest rank individual occurrences. Top K frequent ranks distinct values.

## 9. Testing

The Python script runs its `unittest` suite automatically.

The JavaScript program uses Node.js assertions.

The C++17 and Java 17 programs include executable assertions.

The tests cover:

- Standard selection examples.
- Duplicate-heavy inputs.
- Frequency ties.
- Closest-element tie-breaking.
- Empty selections.
- Invalid K values.
- Sorted-input requirements.
- Service execution.

Java assertions should be enabled when executing the program with `-ea`.

## 10. Execution

### Python

Save the first implementation as `top_k.py`.

Run:

`python top_k.py`

### JavaScript

Save the second implementation as `top_k.js`.

Run:

`node top_k.js`

Requires Node.js 18 or later.

### C++17

Save the third implementation as `top_k.cpp`.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic top_k.cpp -o top_k`

Run:

`./top_k`

On Windows, run:

`.\top_k.exe`

### Java 17

Save the fourth implementation as `TopKEnterprise.java`.

Compile:

`javac TopKEnterprise.java`

Run:

`java -ea TopKEnterprise`

### PostgreSQL

Save the SQL implementation as `top_k.sql`.

Execute:

`psql -U postgres -d your_database -f top_k.sql`

The script creates its own `topk` schema and sample datasets.

The database role must have permission to create schemas, tables, functions, procedures, and indexes.

## 11. Security and Production Considerations

- Validate K before executing expensive operations.
- Apply input-size limits when accepting externally supplied arrays.
- Avoid accepting arbitrary SQL fragments as ranking parameters.
- Use parameterized SQL statements in application integrations.
- Restrict database write permissions according to operational roles.
- Avoid exposing internal exception messages to untrusted clients.
- Monitor heap memory usage for large datasets.
- Use bounded concurrency for batch processing.
- Account for integer overflow when computing distances.
- Use deterministic tie-breaking to support reproducible results.
- Consider data freshness when ranking frequently updated datasets.
- Use database query plans and representative datasets to evaluate index effectiveness.

A database `ORDER BY` operation and an application-level bounded heap are different execution strategies. PostgreSQL provides relational ranking and aggregation, while application implementations provide direct control over selection data structures.

## 12. Practical Algorithm Selection

| Requirement | Preferred approach |
|---|---|
| One Kth largest query, small K | Min-heap |
| One Kth smallest query, small K | Max-heap |
| Average-linear Kth selection | Quickselect |
| Most frequent distinct values | Hash map and bounded heap |
| Frequency ranking with bounded counts | Bucket-based selection |
| Closest values in sorted input | Binary search |
| Closest values in unsorted input | Bounded heap |
| Repeated relational analytics | SQL aggregation and window functions |

The central design decision is to select an algorithm according to the structure of the input and the required output rather than applying full sorting to every ranking problem.
