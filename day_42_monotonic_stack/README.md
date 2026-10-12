# Monotonic Stack: Increasing Stacks, Decreasing Stacks, and Next-Element Queries

## Technical scope

A monotonic stack is a stack whose retained elements follow a consistent ordering. It is useful when a problem asks for the nearest element to the left or right that satisfies an ordering condition.

The central operations are insertion and removal from the top. When a new value arrives, it invalidates some unresolved candidates. Those candidates are removed until the remaining stack satisfies the required invariant. Each element is pushed once and popped at most once, which gives many monotonic-stack algorithms linear time complexity.

This project examines four closely related mechanisms:

- Increasing and decreasing stacks, including the distinction between strict and non-strict ordering.
- Next greater element queries, which identify the nearest later element with a greater value.
- Next smaller element queries, which identify the nearest later element with a smaller value.
- Applications that derive waiting times, circular-array answers, and histogram rectangle boundaries from these mechanisms.

The implementations use Python, JavaScript, C++17, Java 17, and PostgreSQL. They present different perspectives on the same family of algorithms rather than using identical program structures in every language.

## The stack invariant

A stack is monotonic when the values it retains are ordered from bottom to top.

An **increasing stack** retains values in non-decreasing order:

`bottom <= ... <= top`

A **decreasing stack** retains values in non-increasing order:

`bottom >= ... >= top`

The terms sometimes refer to strictly increasing or strictly decreasing stacks. The implementation must therefore state whether equal values are allowed. This distinction affects both correctness and the handling of duplicates.

Consider the sequence `[3, 5, 5, 2, 4]`.

For a non-decreasing stack, each incoming value removes larger values from the top. The final stack is `[2, 4]`. For a non-increasing stack, each incoming value removes smaller values from the top. The final stack is `[5, 5, 4]`.

The stack is not simply a copy of the input. It retains candidates that remain relevant to future comparisons. In next-element algorithms, storing indices instead of values allows the program to recover the original position and calculate distances.

## Increasing and decreasing stacks

### Choosing the removal condition

The comparison in the removal loop determines the invariant.

| Intended stack | Removal condition for incoming value `x` | Retained order |
|---|---|---|
| Non-decreasing | Pop while `top > x` | Bottom to top never decreases |
| Strictly increasing | Pop while `top >= x` | Bottom to top strictly increases |
| Non-increasing | Pop while `top < x` | Bottom to top never increases |
| Strictly decreasing | Pop while `top <= x` | Bottom to top strictly decreases |

A stack's ordering and the query's comparison rule are related but distinct. For example, a strictly greater query must ignore an equal value. A non-strict query may accept equality, depending on the problem specification.

The Python and Java examples expose both non-strict stack orderings. Their next-greater and next-smaller queries use strict comparisons by default.

### Why indices matter

A value-only stack is sufficient when the answer is another value. An index stack is more useful when the result must include the nearest position, the number of steps until a qualifying event, or the width of a range.

Suppose the readings are `[2, 1, 3]`.

- The next greater value for the first reading is `3`.
- The next greater value for the second reading is also `3`.
- The final reading has no greater value to its right.

The corresponding target indices are `[2, 2, null]` when positions are zero-based. The index representation preserves the identity of each source observation, even when several observations contain the same value.

## Next greater element

The next greater element to the right of position `i` is the first position `j` such that `j > i` and `values[j] > values[i]`.

If no such position exists, the answer is absent. The Python and JavaScript programs represent this with `None` and `null`; C++ uses `std::optional`; Java uses a nullable target index and target metric.

### Left-to-right resolution

The algorithm maintains a stack of indices whose next-greater answers are not yet known.

When the next value is greater than the value at the stack top, the current position resolves that earlier position. The algorithm records the answer and removes the resolved index. It repeats until the stack is empty or the top value is greater than or equal to the incoming value. The current index is then pushed.

For `[4, 2, 7]`, the value `7` resolves both `4` and `2`. Neither requires another search after that event.

The stack contains unresolved candidates rather than all historical values. Each candidate enters the stack once and leaves it at most once.

### Correctness argument

When an index is removed by an incoming value, the incoming value is strictly greater than the removed value. Any earlier position that could have resolved the removed index would already have done so when that earlier position was processed. Therefore, the incoming position is the first qualifying position encountered, and it is the correct next-greater answer.

An index remaining in the stack at the end has no qualifying value to its right.

## Next smaller element

The next smaller element to the right is the first later position whose value is strictly smaller than the current value.

The algorithm uses the same resolution structure as next-greater processing, but reverses the comparison. An incoming value resolves every outstanding index whose value is strictly greater than the incoming value.

For `[2, 3, 1]`, the value `1` resolves both `2` and `3`. Neither earlier element has a closer smaller value.

The same invariant supports nearest-smaller queries on the left by processing the input from left to right while removing candidates that are greater than or equal to the current value. After those removals, the stack top, if present, is the nearest strictly smaller value.

## Comparison direction and duplicates

Duplicate handling is a common source of incorrect answers.

For a strict next-greater query, the resolution condition is `previous < current`. Replacing it with `previous <= current` changes the question: an equal value now qualifies.

Likewise, strict next-smaller processing uses `previous > current`. A non-strict variant would use `previous >= current`.

For `[5, 5, 5]`, the strict next-greater and next-smaller answers are absent at every position. An implementation that pops on equality will produce different results and must be documented as non-strict.

Boundary queries have a related concern. Histogram algorithms often require the nearest **strictly** smaller bar. Removing equal heights while computing boundaries allows a bar to extend across equal-height neighbors. The precise comparison must match the boundary definition and area calculation.

## Circular next-greater queries

A circular array allows an element near the end to search through the beginning. The search must not return the source element itself merely because the algorithm revisits its index.

The Python, JavaScript, and C++ implementations process at most two passes. The first pass inserts each source index once. The second pass allows early values to resolve unresolved positions near the end without adding duplicate indices.

For `[1, 2, 1]`, the circular next-greater result is `[2, null, 2]`. The last value finds `2` after wrapping around, while the middle value has no strictly greater value anywhere in the circular sequence.

The algorithm uses `O(n)` time and `O(n)` auxiliary space. Care is required for empty arrays because modulo by the array length is invalid when the length is zero. The implementations explicitly return an empty result before performing circular indexing.

## Application: waiting for a warmer temperature

The Python and JavaScript implementations calculate how many days each daily temperature must wait for a strictly warmer reading.

The stack stores unresolved day indices. When a warmer temperature arrives, each cooler unresolved day is assigned the difference between the current day and its original index. A day that never receives a warmer reading retains a result of zero.

This is a distance query, not merely a next-value query. Storing indices makes the distance calculation direct.

For the sequence `[73, 74, 75, 71, 69, 72, 76, 73]`, the result is `[1, 1, 4, 2, 1, 1, 0, 0]`. The `75` reading waits four days for `76`; the final reading has no future warmer day.

## Application: stock span

Stock span counts the consecutive observations ending at the current day whose prices are less than or equal to the current price.

The stack stores indices of previous prices that are strictly greater than the current price after smaller or equal prices have been removed. The remaining top, when present, is the nearest previous day that blocks the span.

If no blocking day exists, the span includes every observation since the beginning of the input. Otherwise, the span is the distance from the previous greater price.

This is a previous-greater boundary problem. It differs from next-greater processing because the answer is based on the left side of the current observation rather than on a future observation.

## Application: largest rectangle in a histogram

The largest-rectangle problem asks for the maximum area of a rectangle whose width covers contiguous histogram bars and whose height does not exceed any bar in that interval.

For a bar of height `h`, the maximum interval in which that bar can determine the limiting height extends between the nearest strictly smaller bars on its left and right.

If those boundary indices are `left` and `right`, the width is:

`width = right - left - 1`

The area candidate is:

`area = h * width`

The Python program provides both a boundary calculation and a largest-area implementation. The JavaScript implementation independently uses a stack of indices and a virtual zero-height bar to flush outstanding positive heights.

For `[2, 1, 5, 6, 2, 3]`, the largest area is `10`, formed by the adjacent bars of heights `5` and `6`.

The virtual bar is not appended to the original input. It is an algorithmic sentinel that ensures all outstanding bars are evaluated. Non-negative heights are required because negative bar heights do not describe ordinary histogram rectangles.

The two-pass boundary algorithm and the single-pass area algorithm use related invariants, but their intermediate data structures serve different purposes. The boundary algorithm stores explicit left and right limits. The area algorithm calculates each rectangle when a bar is removed from the stack.

## Python implementation

The Python script, `monotonic_stack.py`, provides reusable functions for next-greater and next-smaller values, target indices, circular next-greater queries, daily temperatures, stock span, histogram boundaries, and maximal rectangles in binary matrices.

It uses `Sequence` type annotations to accept lists and other sequence inputs without modifying them. Result arrays are initialized with `None`, making unresolved answers explicit.

The `BoundaryResult` frozen dataclass returns immutable tuples for histogram boundaries. This separates computed boundary data from the mutable stack used during calculation.

The binary-matrix implementation converts each row into a histogram of consecutive ones. For each column, the height increases when the current cell is `"1"` and resets to zero when the cell is `"0"`. The largest histogram rectangle for each row contributes to the global maximum.

Input validation rejects negative histogram heights and ragged matrices. The test suite compares linear next-element algorithms against a quadratic reference implementation on deterministic randomized inputs. This reference check is useful because an algorithm can pass simple examples while failing on duplicate values or monotonic sequences.

## JavaScript implementation

The JavaScript file, `monotonic-stack.js`, uses arrays as explicit stacks and validates that query inputs contain finite numbers. It includes the same strict next-element semantics but emphasizes event-driven processing.

The `streamNextGreater` generator produces an event when an earlier reading's next-greater value becomes known. The result includes the original index, source value, and resolving value. Readings that remain unresolved when the iterable ends receive `null`.

The generator illustrates an important streaming distinction: results can be emitted as soon as they are resolved, but unresolved results cannot be finalized until the input ends. The generator also retains pending source values because the unresolved indices alone would not be sufficient to return their values after the input is consumed.

`TemperatureMonitor` encapsulates the pending measurements in a private class field. Each call to `record` processes the new reading and returns events for earlier measurements that have just been resolved. Returned events are frozen to prevent accidental mutation of the notification records.

The streaming implementation does not promise bounded memory for arbitrary input. A monotonically decreasing sequence can leave every index unresolved, requiring linear pending storage. The algorithm still performs linear total stack operations.

## C++ case study

The C++ program models industrial sensor readings. Each reading has a sensor identifier, timestamp, and numeric value. The query engine finds future readings that are strictly greater or strictly smaller than the source reading.

The `MonotonicQueryEngine` separates value queries, index queries, circular queries, and event-oriented reading analysis. `std::optional` represents a missing answer without relying on a special numeric sentinel, which would be unsafe if every numeric value were a valid measurement.

The event-oriented method emits a `Resolution` record when an incoming reading resolves an earlier one. It then emits unresolved records for readings that never find a qualifying future value. Sorting the records by source index restores source order because resolutions naturally occur in the order that later values arrive, not necessarily in the order of the source positions they resolve.

The implementation reserves vector capacity where the expected size is known and uses const references for read-only input. The test cases check strict comparisons, duplicates, circular processing, and empty input. Exceptions are caught at the program boundary, and test failures produce a non-zero exit status.

The case study is an in-memory batch model. A production monitoring service would also need to define event-time ordering, duplicate timestamps, late-arriving readings, sensor isolation, persistence, and notification delivery guarantees. Those concerns affect the interpretation of the stream but do not change the core stack invariant.

## Java implementation

The Java program models a metric-analysis service with explicit domain types. `Metric` validates its identity and timestamp, `QueryPolicy` records the comparison direction and strictness, and `Match` represents the source reading and its optional target.

`MonotonicAnalyzer` accepts an immutable copy of the input list and returns an unmodifiable list of results. The policy object distinguishes greater-than from smaller-than queries and supports circular processing without exposing a mutable internal stack.

The `MetricAlertService` applies a threshold filter before invoking next-greater analysis. This separation is deliberate: filtering readings according to a service rule is different from deciding whether a reading resolves an outstanding stack entry.

The implementation uses `ArrayDeque` for stack operations, records for compact immutable domain data, and explicit exceptions for invalid input. Circular analysis uses a second pass but inserts source indices only on the first pass.

The threshold example demonstrates an important semantic decision. Filtering out readings changes the sequence in which adjacency and next-element queries are evaluated. If the requirement is to find the next greater reading in the original timeline, non-qualifying readings must remain in the sequence. If the requirement is to analyze only a filtered population, filtering first may be appropriate. The application must define which meaning it needs.

## PostgreSQL data model

The SQL script models sensors and their ordered readings.

| Table or view | Responsibility |
|---|---|
| `sensor` | Identifies each sensor and its measurement unit. |
| `sensor_reading` | Stores timestamped numeric observations with a stable sequence number per sensor. |
| `monotonic_query_result` | Stores a computed answer for each source reading and query type. |
| `next_greater_reading` | Finds the nearest later observation with a strictly greater value. |
| `next_smaller_reading` | Finds the nearest later observation with a strictly smaller value. |

The primary keys establish record identity. Foreign keys prevent readings from referring to nonexistent sensors and stored answers from referring to nonexistent source readings. Unique constraints prevent duplicate sequence numbers and duplicate timestamps for one sensor. The non-negative sequence constraint rejects invalid positions at the database layer.

The lateral queries use `ORDER BY sequence_no` and `LIMIT 1` to select the nearest qualifying future observation. A simple maximum or minimum of future values would not solve the next-element problem because it would ignore which qualifying value occurs first.

The stored-result table uses a unique constraint on `(source_reading_id, query_kind)`. The `INSERT ... ON CONFLICT` statements make result refreshes repeatable: recomputing an answer updates the existing row instead of creating a duplicate.

The SQL views are reference implementations rather than linear-time monotonic-stack implementations. Each source reading can trigger a search through future readings. Depending on the data distribution and execution plan, the total work may approach quadratic complexity. The supporting index assists ordered searches, but it does not guarantee the same linear bound as a single-pass stack algorithm.

The script also demonstrates a constraint failure in an exception block. The invalid negative sequence number is rejected without leaving the surrounding workflow unusable. PostgreSQL-specific features include identity columns, `TIMESTAMPTZ`, lateral joins, filtered aggregates, `ON CONFLICT`, and a PL/pgSQL exception block.

## Complexity and performance

For a sequence of `n` elements, the standard next-greater and next-smaller stack algorithms run in `O(n)` time and require `O(n)` auxiliary space.

The linear bound follows from amortized analysis. Every index is pushed once and popped at most once. Although a single incoming value can trigger many pops, those removals cannot be charged repeatedly to the same index.

The brute-force reference algorithm can take `O(n²)` time because it scans the remaining suffix for each source position. It is valuable for testing small random inputs but is unsuitable for very large sequences.

Circular next-greater processing performs at most `2n` iterations and keeps at most `n` unresolved source indices. Histogram analysis is also linear because every bar is pushed and removed at most once.

For large data sets, constant factors and allocation patterns still matter. Reserving stack capacity, storing indices instead of duplicated records, and avoiding repeated copying of input sequences can reduce overhead. For streaming systems, memory is proportional to the maximum number of unresolved candidates rather than necessarily being constant.

## Common failure modes

- **Using the wrong comparison operator:** A strict next-greater query must not accept equal values. Non-strict variants require a deliberate change to the rule.
- **Confusing stack order with the answer direction:** An increasing stack is not automatically a next-greater stack. The traversal direction, removal condition, and stored candidate invariant must work together.
- **Returning the farthest qualifying value:** A next-element query requires the nearest qualifying position, not the maximum or minimum value anywhere in the suffix.
- **Losing source positions:** Value-only stacks cannot calculate waiting distances or histogram widths without additional positional information.
- **Mismanaging circular traversal:** Pushing an index during both passes can create duplicate pending entries and invalid state.
- **Forgetting unresolved elements:** An absent answer is a valid result, not an error. Result arrays should be initialized to an explicit absent state.
- **Using an incorrect histogram width:** The interval excludes both smaller boundary bars, so its width is `right - left - 1`.
- **Ignoring stream semantics:** A next-greater result becomes final only when a greater reading arrives or the input is known to have ended.

## Testing and operational considerations

Correctness tests should cover empty sequences, single-element inputs, increasing sequences, decreasing sequences, equal values, negative numeric readings where allowed, and values that resolve several pending elements at once. Circular queries need cases where a solution exists only after wrapping and cases where no greater value exists anywhere.

Randomized testing against a brute-force reference is especially useful for checking strict comparisons and nearest-position semantics. The reference implementation should remain simple enough to inspect independently of the optimized algorithm.

In production, sequence ordering must be defined before running the algorithm. If timestamps can arrive out of order, processing arrival order may not represent chronological next-element relationships. The system must either reorder events, delay finalization, or explicitly define its query over arrival order.

Threshold filtering must also be defined as part of the domain contract. Removing observations before stack processing can change which reading counts as the next greater or smaller event. Keeping the complete ordered stream and applying a condition only to emitted results produces different behavior.

Finally, a monotonic stack is a specialized data structure, not a general replacement for sorted collections or priority queues. It is appropriate when the required result depends on unresolved candidates and their order of arrival. Its efficiency comes from permanently discarding candidates that can no longer contribute to a future answer.
