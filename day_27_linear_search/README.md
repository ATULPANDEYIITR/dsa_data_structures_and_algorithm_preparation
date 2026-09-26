# Day 27 — Linear Search

## Topic

Linear search, also called **sequential search**, is a fundamental searching technique in which elements are examined one after another until the required condition is satisfied or the entire collection has been examined.

This implementation set studies linear search from its basic equality comparison through predicate-based searching, duplicate handling, first and last occurrence detection, record searching, streaming-style traversal, complexity analysis, performance, and production considerations.

The three implementations deliberately emphasize different aspects:

- **Python** focuses on algorithmic fundamentals, reusable search abstractions, iterable processing, testing, and progressively advanced examples.
- **JavaScript** demonstrates linear search in a dynamic language, including arrays, objects, generators, strict equality, predicates, and runtime performance.
- **C++** develops an industry-style incident-management case study using classes, enumerations, structured records, templates, predicates, validation, testing, and performance measurement.

---

## 1. Introduction to Searching

A search operation attempts to determine whether a particular value, record, or condition exists within a collection.

For example, given:

`[17, 4, 9, 23, 11, 8]`

and target `23`, a sequential search examines:

1. `17`
2. `4`
3. `9`
4. `23`

The fourth element satisfies the search condition, so the algorithm stops and returns its position.

The fundamental pattern is:

1. Start at the beginning.
2. Inspect the current element.
3. Evaluate the search condition.
4. Stop if the condition succeeds.
5. Otherwise move to the next element.
6. Report failure if the collection ends.

Linear search does not require the collection to be sorted.

---

## 2. Sequential Search

**Sequential search** means that elements are considered in sequence.

For an array containing `n` elements, the algorithm can potentially inspect every element.

A basic implementation can be described as:

`for each element: compare element with target; if equal, return its position`

If the target is the first element, only one comparison is required.

If the target is the last element, all `n` elements may be inspected.

If the target is absent, all `n` elements must be inspected.

This behavior is the foundation of the complexity analysis for linear search.

---

## 3. Search Conditions

The condition being tested does not have to be simple equality.

A search can ask:

- Is this value equal to the target?
- Is this number greater than a threshold?
- Is this value even?
- Does this string match after normalization?
- Does this object have a particular identifier?
- Is this record open and high priority?
- Is this event critical?
- Does a property satisfy a specified business rule?

For example, for:

`[4, 7, 12, 15, 22, 31]`

a search condition could be:

`value % 2 == 0`

The first matching value is `4`.

Another condition could be:

`value > 20`

The first matching value is `22`.

This distinction is important because linear search is fundamentally a **sequential condition-evaluation technique**, not merely an equality-checking technique.

---

## 4. First Occurrence

The **first occurrence** is the lowest index at which the target appears.

Consider:

`[5, 8, 5, 2, 5, 9, 5]`

The value `5` occurs at indices:

`0, 2, 4, 6`

Therefore:

- first occurrence = `0`
- last occurrence = `6`

The most direct first-occurrence algorithm returns immediately when the first match is found.

This early return is important.

If the target is at index `0`, the algorithm performs only one comparison.

If the target is at index `k`, it performs `k + 1` comparisons.

---

## 5. Last Occurrence

The **last occurrence** is the highest index containing the target.

There are two common approaches.

### Forward scan

Maintain a variable containing the most recent matching index.

For every matching element:

`lastIndex = currentIndex`

The entire collection must generally be examined because a later match may exist.

### Reverse scan

Start from the last element and move toward the first.

The first match encountered from the right is automatically the last occurrence.

For an indexable collection, reverse scanning can stop early.

Both approaches have worst-case `O(n)` time.

The reverse version can be practically useful when the desired match is near the end.

---

## 6. All Occurrences

Sometimes a program needs every matching position rather than only the first or last one.

For:

`[2, 7, 2, 9, 2, 4, 2]`

the positions of `2` are:

`[0, 2, 4, 6]`

Finding all occurrences requires continuing through the entire collection.

If there are `k` matches, the output itself requires `O(k)` storage.

The traversal requires `O(n)` time.

---

## 7. Existence Search

If the only question is:

"Does the target exist?"

there is no need to store an index.

The algorithm can return `true` immediately after the first match.

This creates the following behavior:

| Situation | Work |
|---|---:|
| First element matches | `O(1)` |
| Early element matches | Small number of comparisons |
| Last element matches | `O(n)` |
| Target absent | `O(n)` |

The Python, JavaScript, and C++ implementations all demonstrate this early-exit principle in different forms.

---

## 8. Generic Predicate Search

A reusable search function can accept a condition rather than a fixed target.

Conceptually:

`find first element where condition(element) is true`

This supports searches such as:

- first even number
- first negative number
- first score above 90
- first available product
- first critical event
- first open high-priority incident

This is more general than equality-based search.

Python uses callable predicates.

JavaScript uses functions.

C++ uses generic predicates and lambda expressions.

---

## 9. Searching Objects and Records

Real applications usually search structured records rather than isolated integers.

A student record might contain:

- student ID
- name
- score

A product record might contain:

- product code
- name
- price
- stock

An incident record might contain:

- incident ID
- title
- owner
- severity
- status
- priority

A linear search can inspect one selected field while leaving the rest of the record unchanged.

For example:

`incident.incidentId == requestedId`

This is a normal and important application of linear search.

---

# Python Implementation

## 10. Python Fundamentals

The Python implementation begins with a straightforward `linear_search()` function.

Its contract is:

- return the first matching index
- return `-1` when no match exists

Python's `enumerate()` makes index-and-value traversal clear:

`for index, item in enumerate(items):`

The function returns immediately after finding the target.

This implementation uses no external packages.

---

## 11. Python Search Variants

The Python file contains separate implementations for:

- basic linear search
- traced sequential search
- first occurrence
- last occurrence
- reverse last-occurrence search
- all occurrences
- predicate-based search
- key-based search
- object search
- existence checking
- occurrence counting
- sorted-data early exit
- generator-based searching

The functions deliberately have different contracts so the distinction between search operations remains explicit.

---

## 12. Python Search Statistics

The `SearchResult` class stores:

- whether a match was found
- the resulting index
- number of comparisons

For:

`[11, 22, 33, 44, 55]`

searching for `11` requires one comparison.

Searching for `33` requires three.

Searching for `55` requires five.

Searching for an absent value such as `99` requires five.

This makes the relationship between position and work directly observable.

---

## 13. Python Iterable Search

A useful property of sequential search is that it does not inherently require random access.

The Python implementation includes a generator:

`generate_numbers()`

and a function that searches an `Iterable`.

This is important because some data sources are naturally consumed sequentially.

Examples include:

- event streams
- generated values
- file-like processing
- incoming records
- other lazy iterables

A sequential algorithm can stop as soon as a matching item appears.

---

## 14. Python Object Search

The Python implementation defines:

`Student`

and:

`Product`

data classes.

Searching a list of students by `student_id` demonstrates searching by a record field.

Searching products by product code demonstrates the same concept in a commerce-oriented example.

Searching for the first product with positive stock demonstrates predicate-based search.

---

## 15. Python Testing

The Python script includes a built-in `run_tests()` function.

It tests:

- empty collections
- singleton collections
- successful search
- unsuccessful search
- first occurrence
- last occurrence
- all occurrences
- predicate searches
- occurrence counting
- existence checking
- sorted search
- reverse search
- binary search comparison
- search statistics
- normalized string search

The use of assertions provides executable verification without requiring a third-party testing package.

---

# JavaScript Implementation

## 16. JavaScript Linear Search

The JavaScript implementation starts with:

`linearSearch(items, target)`

The algorithm uses a conventional indexed `for` loop.

JavaScript arrays provide efficient index-based access, so the implementation can directly examine:

`items[index]`

The first equality match returns immediately.

---

## 17. Strict Equality

JavaScript has multiple equality operators.

The implementation deliberately demonstrates:

`===`

and:

`==`

Strict equality is generally preferable when the search contract requires values to match without implicit type coercion.

For example:

`5 === "5"`

is false.

By contrast:

`5 == "5"`

is true because the loose equality operator permits coercion.

Search behavior should be based on an explicitly chosen equality contract.

---

## 18. JavaScript `NaN` and Object Identity

JavaScript has special equality behavior for `NaN`.

For example:

`NaN === NaN`

is false.

Objects also use identity-based equality.

Two separately created objects containing the same properties are not strictly equal:

`{ value: 1 } === { value: 1 }`

is false.

Therefore, object searching normally compares a meaningful property such as an ID rather than comparing independently created objects by identity.

---

## 19. JavaScript Predicate Search

The JavaScript implementation provides:

`firstIndexWhere(items, condition)`

The condition is supplied as a function.

For example:

`value => value % 2 === 0`

can locate the first even value.

This demonstrates how higher-order functions can make a search implementation reusable without changing its traversal logic.

---

## 20. JavaScript Objects

The implementation defines `Student` and `Product` classes.

Examples include:

- finding a student by ID
- finding the first student above a score threshold
- finding a product by code
- finding the first product in stock

These examples show that linear search is independent of the primitive type of the collection.

The search logic depends on the condition being evaluated.

---

## 21. JavaScript Generators

The implementation includes:

`generateNumbers()`

which produces values lazily.

`findFirstInIterable()` consumes an iterable until the condition succeeds.

This demonstrates a key relationship between sequential algorithms and lazy data processing.

A generator does not need to construct every possible result in memory before the search begins.

If the required value appears early, the search can terminate early.

---

## 22. JavaScript Performance

The JavaScript implementation measures elapsed time with:

`process.hrtime.bigint()`

The benchmark places the target at the end of arrays of increasing size.

The purpose is to expose the growth in comparison count.

Timing itself is machine-dependent.

Differences can arise from:

- processor speed
- JavaScript runtime
- memory behavior
- optimization
- operating-system activity
- garbage collection
- system load

Algorithmic complexity should therefore not be inferred from a single timing result.

---

# C++ Case Study

## 23. Incident Management Scenario

The C++ implementation models an in-memory **incident registry**.

Each incident contains:

- incident ID
- title
- owner
- severity
- status
- priority

The system supports several types of searches.

This makes linear search a component of a realistic record-processing system rather than an isolated numeric example.

---

## 24. C++ Domain Types

The case study uses enumerations for:

`Severity`

and:

`Status`

Severity values include:

- Low
- Medium
- High
- Critical

Status values include:

- Open
- Investigating
- Resolved

This is preferable to relying on arbitrary strings throughout the program because the allowed domain values are explicit.

---

## 25. `IncidentRegistry`

The `IncidentRegistry` class owns a collection of incidents and provides search operations.

Its methods include:

- `findById()`
- `findFirstCritical()`
- `findFirstOpenHighPriority()`
- `findAllByOwner()`
- `findAllBySeverity()`
- `findLastResolved()`

Each method uses a sequential traversal appropriate to its search contract.

---

## 26. Finding an Incident by ID

`findById()` performs a linear search through the incident vector.

The function returns an `optional<Incident>`.

This is useful because an incident may not exist.

The result therefore represents two states:

- an incident exists
- no incident exists

This avoids forcing a fake record or special object to represent failure.

---

## 27. Finding the First Critical Incident

`findFirstCritical()` scans from the beginning and immediately returns when it encounters:

`Severity::Critical`

This is a direct example of a search condition.

The algorithm does not need to examine later records after the first critical incident is found.

---

## 28. Compound Search Conditions

`findFirstOpenHighPriority()` demonstrates a compound condition.

A record must satisfy both:

`status == Open`

and:

`priority >= minimumPriority`

This shows that linear search can implement application-level business rules without requiring the data to be sorted or indexed.

---

## 29. Finding All Records

`findAllByOwner()` and `findAllBySeverity()` return every matching record.

Unlike first-match search, these functions must inspect the entire collection.

This distinction is important:

**First match**

Can stop early.

**All matches**

Must continue through the complete input.

Both are linear traversals, but their result contracts differ.

---

## 30. Last Match in the C++ Case Study

`findLastResolved()` scans from the end of the vector.

The first resolved incident found during reverse traversal is the last resolved incident in the original ordering.

This demonstrates why traversal direction can be chosen based on the required result.

---

## 31. Templates and Generic Search

The C++ implementation includes a templated:

`linearSearch()`

This allows the same search logic to operate on different types that support the required equality operation.

It also includes generic predicate-based functions using templates.

This separates:

- traversal mechanism
- search condition

The resulting design is reusable without copying the algorithm for every record type.

---

## 32. C++ Error Handling

The program uses:

`try`

and:

`catch`

around the main application.

Validation helpers can throw exceptions for invalid conditions.

The testing function uses a `require()` helper that throws `runtime_error` when an assertion fails.

This provides an explicit failure path instead of silently continuing after a broken invariant.

---

## 33. Complexity Analysis

Let `n` represent the number of elements.

### First occurrence

Best case:

`O(1)`

The first element matches.

Worst case:

`O(n)`

The target is at the last position or is absent.

Auxiliary space:

`O(1)`

for the basic iterative algorithm.

### Last occurrence

Forward scan:

`O(n)` worst case.

Reverse scan:

`O(n)` worst case.

Both use constant auxiliary space when the result itself is not counted as additional collection storage.

### All occurrences

Traversal:

`O(n)`

If `k` matches are stored, output storage is:

`O(k)`

### Existence search

Best case:

`O(1)`

Worst case:

`O(n)`

### Sorted-data early-exit linear search

Best case:

`O(1)`

Worst case:

`O(n)`

Sorting does not automatically turn linear search into binary search.

---

## 34. Average Successful Search

Assume:

- there are `n` elements
- exactly one target exists
- every position is equally likely

The target could require:

`1, 2, 3, ..., n`

comparisons.

The average is:

`(1 + 2 + ... + n) / n`

which simplifies to:

`(n + 1) / 2`

Therefore, the average successful linear search requires approximately half the collection to be examined under that assumption.

This is still `O(n)` because constant factors are ignored in asymptotic complexity.

---

## 35. Space Complexity

The basic iterative linear search uses a fixed number of variables.

Therefore its auxiliary space complexity is:

`O(1)`

This does not mean that the input collection occupies constant memory.

The collection itself requires whatever storage its representation requires.

For an all-occurrences operation, the result collection adds `O(k)` storage where `k` is the number of matches.

---

## 36. Linear Search Versus Binary Search

| Property | Linear Search | Binary Search |
|---|---|---|
| Basic strategy | Sequential inspection | Repeatedly halve search interval |
| Requires sorted data | No | Yes |
| Worst-case search time | `O(n)` | `O(log n)` |
| Basic iterative auxiliary space | `O(1)` | `O(1)` |
| Works naturally on streams | Yes | Generally no |
| Simple to implement | Yes | More conditions required |
| Supports arbitrary predicate scans | Yes | Only under suitable ordering |
| Useful for unsorted data | Yes | No |

Binary search is faster asymptotically for suitable sorted random-access data.

Linear search remains useful when:

- the collection is small
- data is unsorted
- only one or a few searches are needed
- records arrive sequentially
- the search condition is naturally expressed as a predicate
- maintaining a separate index is unnecessary

---

## 37. Sorted Data and Early Termination

Suppose:

`[4, 8, 13, 21, 29, 35]`

is sorted.

When searching for `20`, once the algorithm reaches `21`, it knows that `20` cannot occur later.

Therefore it can stop.

This is an optimization based on ordering.

It does not change the worst-case complexity to `O(log n)`.

Binary search achieves logarithmic behavior because it deliberately reduces the remaining search interval by approximately half after each comparison.

A sorted linear search does not make that reduction.

---

## 38. Edge Cases

Important cases include:

### Empty collection

There is nothing to inspect.

The search should immediately report absence.

### One-element collection

There are only two possible outcomes:

- the element matches
- the element does not match

### Target at first position

This is the best case for ordinary first-match linear search.

### Target at last position

This is the worst successful case.

### Target absent

The entire collection must normally be examined.

### Duplicate values

The search contract must define whether the result is:

- first occurrence
- last occurrence
- all occurrences
- any occurrence
- existence only

### Negative values

There is no special difficulty because linear search does not depend on values being positive.

### Strings

The comparison condition may be exact, case-insensitive, trimmed, normalized, or otherwise domain-specific.

---

## 39. Search Semantics Matter

A technically correct traversal can still produce the wrong application behavior if its result contract is ambiguous.

For example, given:

`[20, 30, 20, 40, 20]`

returning `20` is insufficient if the caller needs an index.

Returning index `0` is correct for first occurrence.

Returning index `4` is correct for last occurrence.

Returning `[0, 2, 4]` is correct for all occurrences.

The search function should therefore define its output precisely.

---

## 40. Common Mistakes

### Mistake 1: Forgetting early return

A first-occurrence function that continues scanning unnecessarily is correct in result but inefficient in behavior.

### Mistake 2: Returning the first match when the caller needs the last

Duplicate handling must match the specified contract.

### Mistake 3: Forgetting the absent case

A search function needs an explicit failure representation.

Examples include:

- `-1`
- `None`
- `undefined`
- `optional`

depending on language and API design.

### Mistake 4: Assuming sorted input

Basic linear search does not need sorting.

### Mistake 5: Using binary search on unsorted data

Binary search depends on ordering.

### Mistake 6: Off-by-one errors

Index traversal must correctly handle:

- index `0`
- index `n - 1`
- empty input

### Mistake 7: Confusing equality with identity

This is particularly important for JavaScript objects.

### Mistake 8: Ignoring input size

A linear scan that is harmless for 20 records may be expensive when repeated across millions of records.

### Mistake 9: Using the wrong data structure

If an application performs millions of exact-key lookups, repeatedly scanning a vector may be inappropriate when an index can be maintained.

### Mistake 10: Treating benchmark timing as universal

Hardware and runtime conditions affect measurements.

---

## 41. Performance Considerations

Linear search has low algorithmic complexity in terms of implementation and memory, but its runtime can become significant as `n` grows.

Important factors include:

- collection size
- target position
- number of repeated searches
- comparison cost
- memory locality
- data representation
- runtime or compiler
- frequency of updates
- whether the collection is already sorted
- whether an index is available

The comparison itself can also be expensive.

For example, comparing simple integers is generally cheaper than comparing complex objects with several normalization operations.

---

## 42. Repeated Searches and Indexing

Suppose a collection contains `n` records and the program performs `q` exact-key searches.

A straightforward linear approach can require approximately:

`O(nq)`

work in the worst case.

An alternative is to build an index such as a hash table.

Building the index requires additional work and memory, but subsequent exact-key lookups can often be much faster on average.

The trade-off becomes:

**Linear search**

- minimal additional structure
- simple
- good for small or infrequently searched collections
- `O(n)` worst-case lookup

**Indexed structure**

- additional memory
- index construction and maintenance
- faster repeated exact-key lookup
- more architectural complexity

The appropriate choice depends on workload characteristics.

---

## 43. Streaming and Sequential Data

Linear search is particularly natural when data arrives sequentially.

Examples include:

- processing events
- reading records from a stream
- examining log entries
- scanning generated values
- looking for the first matching message
- stopping when a critical event appears

A binary-search-style random-access strategy is generally unsuitable for an unbounded or naturally sequential stream.

This is one reason why linear traversal remains fundamental despite the existence of faster search algorithms for particular data structures.

---

## 44. Security Considerations

Linear search is not a security mechanism.

It does not provide:

- authentication
- authorization
- confidentiality
- encryption
- access control

When searching sensitive application data:

- validate external input
- normalize values consistently where appropriate
- enforce authorization before returning records
- avoid unnecessary logging of confidential search terms
- consider worst-case processing time
- avoid exposing sensitive information merely because a record exists
- use appropriate database indexes for persistent data
- avoid treating an in-memory scan as an access-control boundary

For authentication systems, password handling must use appropriate password-hashing and verification mechanisms rather than a simple linear lookup through plaintext passwords.

---

## 45. Python, JavaScript, and C++ Comparison

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Primary emphasis | Algorithmic study | Dynamic application behavior | Structured technical case study |
| Generic search | Callables and iterables | Functions and iterables | Templates and predicates |
| Record model | `dataclass` | Classes/objects | Structs, enums, class |
| Optional result | `None` | `undefined` | `std::optional` |
| Basic indexing | Direct sequence indexing | Array indexing | Vector indexing |
| Lazy processing | Generators | Generators | Not the primary focus |
| Equality example | Python object equality | Strict equality and identity behavior | Typed equality |
| Error handling | Exceptions and assertions | Exceptions and assertions | Exceptions and validation |
| Performance timing | `perf_counter()` | `process.hrtime.bigint()` | `std::chrono` |
| Case study | Students/products/events | Students/products/events | Incident registry |

---

## 46. Implementation Design Principles

The three implementations demonstrate several general design principles.

### Separate traversal from condition

A reusable search algorithm should not need to be rewritten every time the condition changes.

### Define result semantics

The caller should know whether the function returns:

- index
- object
- boolean
- all matches
- optional result
- structured statistics

### Stop as soon as the contract allows

For first-match and existence searches, unnecessary traversal should be avoided.

### Choose traversal direction deliberately

If the required result is the last occurrence, reverse traversal can be natural.

### Keep validation separate from core algorithm logic

This improves testability and keeps the search mechanism simple.

### Test edge cases

Empty, singleton, duplicate, missing, first-position, and last-position cases are especially important.

---

## 47. Practical Applications

Linear search can appear in many systems, including:

- small in-memory collections
- configuration processing
- event processing
- log scanning
- record validation
- resource availability checks
- application-level filtering
- stream processing
- simple lookup tables
- first-match business rules
- prototype systems
- educational implementations
- low-volume administrative tools

The key question is not simply whether a faster asymptotic algorithm exists.

The important question is whether the data structure, workload, ordering, update frequency, and required search semantics justify another approach.

---

## 48. Important Distinction: Algorithm Versus Data Structure

Linear search describes the **search procedure**.

The underlying collection determines important implementation characteristics.

Examples include:

- array
- vector
- linked list
- generator
- stream
- object collection

Linear search is particularly natural for sequential structures.

For an array or vector, direct indexing makes forward and reverse traversal straightforward.

For a linked structure, moving sequentially is natural, while random access may be expensive.

For a generator or stream, only sequential consumption may be available.

---

## 49. Important Distinction: Search Versus Filter

A first-match search asks:

"Where is the first element satisfying this condition?"

A filter asks:

"Which elements satisfy this condition?"

The first-match operation can stop early.

The filter normally requires a complete traversal.

Both may have `O(n)` worst-case traversal, but they have different result contracts and different practical behavior.

---

## 50. Advanced Linear-Scan Patterns

Linear traversal can implement more than direct searching.

Examples include:

- finding minimum
- finding maximum
- counting values
- checking whether all values satisfy a condition
- checking whether any value satisfies a condition
- finding the first valid record
- finding the last matching record
- collecting all matches
- calculating aggregates
- detecting the first anomaly
- locating the first threshold crossing

These operations demonstrate that linear scanning is a broader algorithmic pattern.

---

## 51. Industry Case Study Architecture

The C++ incident registry follows a simple architecture:

`Incident data -> IncidentRegistry -> Search operation -> Search result`

The registry owns the data.

Search methods encapsulate the traversal logic.

The caller does not need to know how the records are stored internally.

For example:

`findById(1004)`

expresses the required operation without exposing the loop to the caller.

This separation improves maintainability.

---

## 52. Why the C++ Case Study Uses a Vector

The incident registry uses:

`std::vector<Incident>`

because the case study is specifically demonstrating sequential access.

A vector provides:

- contiguous storage
- efficient indexed access
- predictable iteration
- simple ownership
- standard-library integration

For a large production system with frequent ID lookups, another data structure might be more appropriate.

The choice here is intentional because the educational goal is to expose linear traversal clearly.

---

## 53. Testing Strategy

The implementations test several dimensions of correctness.

### Functional correctness

Does the correct index or record return?

### Absence handling

Does the search correctly report a missing target?

### Duplicate semantics

Does first occurrence differ correctly from last occurrence?

### Predicate correctness

Does the search stop at the first record satisfying the condition?

### Boundary correctness

Does the implementation handle empty and singleton collections?

### Performance behavior

Does a worst-case search inspect approximately all `n` elements?

The comparison-count functions make this last property directly measurable.

---

## 54. Complexity Reference

| Operation | Best Case | Worst Case | Auxiliary Space |
|---|---:|---:|---:|
| First occurrence | `O(1)` | `O(n)` | `O(1)` |
| Existence check | `O(1)` | `O(n)` | `O(1)` |
| Last occurrence, forward | `O(n)` | `O(n)` | `O(1)` |
| Last occurrence, reverse | `O(1)` | `O(n)` | `O(1)` |
| All occurrences | `O(n)` | `O(n)` | `O(k)` output |
| Predicate first match | `O(1)` | `O(n)` | `O(1)` |
| Sorted early-exit linear search | `O(1)` | `O(n)` | `O(1)` |
| Binary search | `O(1)` | `O(log n)` | `O(1)` iterative |

Here `n` is the input size and `k` is the number of matching results stored.

---

## 55. Core Principles to Retain

The essential ideas demonstrated by the implementations are:

1. Linear search examines elements sequentially.
2. It does not require sorted data.
3. The search condition determines what counts as a match.
4. First-occurrence search can terminate immediately after the first match.
5. Last-occurrence search must identify the final matching position.
6. Reverse traversal can efficiently locate the last match in an indexable collection.
7. Finding all matches requires a complete scan.
8. Best-case linear search is `O(1)`.
9. Worst-case linear search is `O(n)`.
10. Basic iterative linear search uses `O(1)` auxiliary space.
11. Sorted data can enable early termination but does not make linear search logarithmic.
12. Binary search requires appropriate ordering.
13. Repeated large-scale exact-key searches may justify an index or different data structure.
14. Search functions should have explicit result contracts.
15. Edge cases are part of algorithm correctness, not optional additions.
16. Linear traversal is useful for sequential and streaming data where random access is unavailable or inappropriate.
17. Algorithm selection should consider both asymptotic complexity and the actual data/workload characteristics.
