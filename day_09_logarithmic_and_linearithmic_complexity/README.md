# Day 9 — Logarithmic and linearithmic complexity

## Topic

This study focuses on four closely related ideas:

- Binary search
- Divide-and-conquer
- Logarithmic growth
- Merge sort
- Heap operations

The central comparison is between `O(log n)`, `O(n)`, and `O(n log n)`.

The important question is not simply whether an algorithm is fast for a small input. The more useful question is how the amount of work changes when the input becomes very large.

---

## 1. Complexity and growth

Algorithmic complexity describes how an algorithm's resource requirements grow as the input size increases.

For this topic, the most important growth patterns are:

| Complexity | Common name | General behavior | Example |
|---|---|---|---|
| `O(1)` | Constant | Work stays approximately fixed | Heap maximum lookup |
| `O(log n)` | Logarithmic | Work grows very slowly | Binary search |
| `O(n)` | Linear | Work grows proportionally with input | Linear search |
| `O(n log n)` | Linearithmic | Linear work combined with logarithmic levels | Merge sort, heap sort |

Big-O notation focuses on asymptotic growth. It intentionally ignores constant factors and lower-order terms when describing the dominant behavior for large inputs.

For example:

`3n + 20`

and

`100n + 5000`

are both `O(n)`.

They can have very different actual execution times for a particular input, but they have the same asymptotic growth category.

---

## 2. Why logarithmic growth is so important

A logarithm answers a question such as:

> How many times can I divide a number by a fixed base before reaching approximately 1?

For binary algorithms, the base is usually 2.

Examples:

- `log2(2) = 1`
- `log2(4) = 2`
- `log2(8) = 3`
- `log2(16) = 4`
- `log2(1024) = 10`
- `log2(1,048,576) = 20`

This growth is extremely slow compared with linear growth.

Consider an input containing 1,000,000 elements.

A linear algorithm can require work proportional to 1,000,000.

A binary-search-style algorithm needs only about 20 halvings because:

`2^20 = 1,048,576`

This is the central advantage of `O(log n)`.

The improvement comes from eliminating a large portion of the remaining search space at every step.

---

## 3. Linear growth

An `O(n)` algorithm performs work proportional to the number of input elements.

Linear search is the basic example.

Given:

`[10, 20, 30, 40, 50]`

and target `50`, a linear search checks:

1. `10`
2. `20`
3. `30`
4. `40`
5. `50`

If the target is absent, every element must be examined.

### Complexity

Best case:

`O(1)`

The first element is the target.

Worst case:

`O(n)`

The target is the final element or does not exist.

Average behavior is also linear in the general case.

Space complexity is:

`O(1)`

because the algorithm needs only a small fixed amount of additional state.

The Python implementation uses `linear_search`, the JavaScript implementation uses `linearSearch`, and the C++ implementation uses `linearSearch`.

---

## 4. Binary search

Binary search works on an ordered search space.

For a sorted ascending array:

`[10, 20, 30, 40, 50, 60, 70, 80]`

suppose the target is `70`.

Instead of starting from the first element, binary search examines the middle.

The middle value is approximately `40`.

Because `70 > 40`, every element at or below `40` can be discarded.

The remaining search space is:

`[50, 60, 70, 80]`

The next middle value is examined.

Again, approximately half the remaining possibilities are eliminated.

The process continues until the target is found or the search interval becomes empty.

---

## 5. Mathematical derivation of binary search complexity

Suppose the original input contains `n` elements.

After one division:

`n / 2`

After two divisions:

`n / 4`

After three divisions:

`n / 8`

After `k` divisions:

`n / 2^k`

The process ends when approximately one candidate remains:

`n / 2^k = 1`

Multiplying both sides by `2^k`:

`n = 2^k`

Taking logarithm base 2:

`k = log2(n)`

Therefore binary search requires:

`O(log n)`

comparisons in the worst case.

---

## 6. Binary search precondition

Binary search is not a general replacement for linear search.

The search space must have an appropriate ordering.

For ordinary binary search over an array, the array must be sorted.

For example:

`[2, 5, 8, 11, 17, 20]`

is sorted.

Binary search can determine whether `17` exists.

An unsorted array such as:

`[11, 2, 20, 5, 17, 8]`

does not satisfy the ordinary binary-search requirement.

Applying ordinary binary search to such data can produce an incorrect result.

This is one of the most common binary-search mistakes.

---

## 7. Iterative binary search

The Python implementation uses `binary_search_iterative`.

The JavaScript implementation uses `binarySearch`.

The C++ implementation uses `binarySearch`.

The essential state consists of:

- `left`
- `right`
- `middle`

A typical calculation is:

`middle = left + (right - left) // 2`

The equivalent JavaScript and C++ calculations use integer division appropriate to those languages.

The form `left + (right - left) / 2` is useful in fixed-width integer languages because directly calculating `(left + right) / 2` can overflow if both indices are extremely large.

Python integers do not have the same fixed-width overflow behavior, but using the safer form is still a good cross-language habit.

---

## 8. Recursive binary search

Binary search can also be implemented recursively.

The recursive algorithm has a smaller problem after every call:

`n -> n/2 -> n/4 -> n/8 -> ...`

Its time complexity remains:

`O(log n)`

The difference is auxiliary space.

An iterative version uses:

`O(1)`

auxiliary space.

A recursive version uses:

`O(log n)`

call-stack space because the number of active calls is proportional to the logarithm of the input size.

For binary search, recursion is mainly useful for demonstrating the divide-and-conquer structure. An iterative implementation is often preferable when recursion does not provide a meaningful design benefit.

---

## 9. Binary search with duplicate values

Ordinary binary search answers a question such as:

> Does the target occur?

It does not necessarily answer:

> What is the first occurrence?

For:

`[1, 2, 2, 2, 3, 4]`

an ordinary binary search for `2` can return any valid position containing `2`.

The Python implementation includes:

- `first_occurrence_binary_search`
- `last_occurrence_binary_search`
- `lower_bound`
- `upper_bound`

The JavaScript implementation provides corresponding functions.

The C++ case study includes `firstOccurrence` and `lowerBoundIndex`.

These variations are important because many practical search problems are boundary problems rather than simple equality searches.

---

## 10. Lower bound

A lower bound searches for the first position satisfying:

`values[index] >= target`

For:

`[1, 2, 2, 2, 3, 4]`

the lower bound of `2` is index `1`.

The lower bound of `3` is index `4`.

If the target is larger than every element, the result can be the array length.

The lower-bound pattern is especially useful for insertion positions and range-processing algorithms.

Its complexity is:

`O(log n)`

---

## 11. Upper bound

An upper bound searches for the first position satisfying:

`values[index] > target`

For:

`[1, 2, 2, 2, 3, 4]`

the upper bound of `2` is index `4`.

The range from lower bound to upper bound can therefore describe all occurrences of a value.

For target `2`:

`[lower_bound(2), upper_bound(2))`

becomes:

`[1, 4)`

which covers indices `1`, `2`, and `3`.

This technique is useful when processing duplicates efficiently.

---

## 12. Binary search does not always search an array

A more advanced idea is binary search over an answer space.

The Python, JavaScript, and C++ implementations demonstrate this with a shipping-capacity problem.

Suppose packages have weights:

`[1, 2, 3, 4, 5, 6, 7]`

and all packages must be shipped in their original order within three days.

The question is:

> What is the smallest truck capacity that makes the schedule possible?

The algorithm does not search for a particular package.

Instead, it searches possible capacity values.

The smallest possible capacity is the largest individual package weight.

The largest possible capacity is the sum of all package weights.

A capacity is either:

- feasible, or
- infeasible.

Most importantly, feasibility is monotonic.

If a capacity of `15` works, a capacity of `16` also works.

If a capacity of `10` does not work, a smaller capacity cannot suddenly work.

This monotonic property allows binary search.

The complexity is:

`O(n log S)`

where `n` is the number of packages and `S` represents the capacity search range.

This pattern is sometimes described as binary search on the answer.

---

## 13. Integer square root

The implementations also calculate the floor of a square root using binary search.

For example:

`sqrt(10) ≈ 3.162`

Therefore:

`floor(sqrt(10)) = 3`

The algorithm searches the integer range from `1` to `n`.

For a candidate `m`, it asks whether:

`m² <= n`

If the candidate is valid, larger candidates are considered.

If the candidate is too large, smaller candidates are considered.

This demonstrates that binary search can be applied to any ordered search space with a suitable monotonic condition.

---

## 14. Divide-and-conquer

Divide-and-conquer is an algorithm design strategy built around three stages.

### Divide

Break a large problem into smaller problems.

### Conquer

Solve the smaller problems.

### Combine

Combine the smaller solutions into the final solution.

Binary search and merge sort are both divide-and-conquer algorithms, but they use the strategy differently.

Binary search keeps only one half of the problem.

Merge sort recursively processes both halves.

This distinction explains their different recurrences.

---

## 15. Binary search recurrence

Binary search can be modeled as:

`T(n) = T(n/2) + O(1)`

There is:

- one recursive subproblem
- half the original size
- constant additional work

Therefore:

`T(n) = O(log n)`

The recursion tree is essentially a single path.

---

## 16. Merge sort

Merge sort is a classic linearithmic algorithm.

Suppose the input is:

`[38, 27, 43, 3, 9, 82, 10]`

Merge sort repeatedly divides the input.

The conceptual structure is:

`[38, 27, 43, 3, 9, 82, 10]`

then smaller halves, eventually reaching individual elements.

An array containing one element is already sorted.

The sorted pieces are then merged.

The important operation is the merge.

Two sorted arrays can be merged in linear time relative to their combined size.

For example:

`[3, 10, 27]`

and:

`[9, 38, 43]`

can be merged by repeatedly taking the smaller front element.

---

## 17. Merge sort recurrence

Merge sort performs:

- two recursive calls on approximately `n/2` elements each
- `O(n)` work to merge the results

Therefore:

`T(n) = 2T(n/2) + O(n)`

The result is:

`O(n log n)`

There are approximately:

`log2(n)`

levels.

At each level, the total amount of merging work is approximately:

`O(n)`

Therefore:

`O(n) × O(log n) = O(n log n)`

This is the fundamental reason merge sort is linearithmic.

---

## 18. Why merge sort is not O(log n)

A common mistake is to see that merge sort repeatedly divides its input and conclude that it must be `O(log n)`.

The division depth is logarithmic, but merge sort does not perform constant work at each level.

At every level, it processes the elements during merging.

For `n` elements, that merging work is approximately `O(n)` per level.

There are approximately `O(log n)` levels.

Therefore the total is:

`O(n log n)`

---

## 19. Stability of merge sort

A sorting algorithm is stable if equal-key elements retain their original relative order.

Consider:

- Asha: score 80
- Ravi: score 70
- Neha: score 80
- Vikram: score 70

A stable sort by score keeps:

- Ravi before Vikram
- Asha before Neha

The implementations deliberately select the left element when comparison keys are equal.

In the Python implementation this appears in `merge` and `merge_students`.

The C++ merge operation similarly prefers the left item when priorities are equal.

Stability is important when records have multiple meaningful fields and sorting occurs in stages.

---

## 20. Recursive merge sort

The Python implementation provides `merge_sort`.

The JavaScript implementation provides `mergeSort`.

The C++ implementation uses `mergeSortRecursive` and `mergeSort`.

All three implementations follow the same conceptual architecture:

1. Stop for zero or one element.
2. Find the middle.
3. Sort the left half.
4. Sort the right half.
5. Merge the two sorted halves.

The implementations are complete rather than pseudocode.

---

## 21. Bottom-up merge sort

The Python implementation includes `bottom_up_merge_sort`.

The JavaScript implementation includes `bottomUpMergeSort`.

Instead of recursion, the algorithm starts with runs of size one.

It then merges:

- size 1 runs into size 2 runs
- size 2 runs into size 4 runs
- size 4 runs into size 8 runs
- and so on

The asymptotic complexity remains:

`O(n log n)`

The main difference is implementation structure.

Recursive merge sort naturally expresses divide-and-conquer.

Bottom-up merge sort expresses the same sorting process iteratively.

---

## 22. Heap data structure

A heap is a complete binary tree commonly represented by an array.

A max heap satisfies:

`parent >= children`

For zero-based indexing:

`parent(i) = floor((i - 1) / 2)`

`left(i) = 2i + 1`

`right(i) = 2i + 2`

No explicit tree-node objects are required.

The array representation is compact and cache-friendly.

---

## 23. Max heap example

Consider a max heap containing:

`[20, 10, 15, 4, 7, 3]`

The root contains the largest element:

`20`

The children of the root are:

`10` and `15`

The heap does not require the entire array to be sorted.

It only requires the parent-child ordering constraint.

This distinction is important.

A heap is not a sorted array.

---

## 24. Heap insertion

To insert an element:

1. Put it at the end of the array.
2. Compare it with its parent.
3. If it violates the heap property, swap it upward.
4. Continue until the property is restored.

This is called sift-up or bubble-up.

The height of a complete binary tree is:

`O(log n)`

Therefore insertion is:

`O(log n)`

The best case can be `O(1)` when the new element already satisfies the heap property at its initial location.

---

## 25. Heap extraction

For a max heap, the largest element is at the root.

To remove it:

1. Save the root.
2. Move the final element to the root.
3. Remove the final array position.
4. Sift the replacement downward.
5. Restore the heap property.

This operation is:

`O(log n)`

because the replacement element can move down at most the height of the heap.

The Python class calls this `extract_max`.

The JavaScript class calls it `extractMax`.

The C++ `MaxHeap` class exposes `pop`.

---

## 26. Heap peek

Looking at the maximum value requires no restructuring.

The maximum is stored at the root.

Therefore:

`peek = O(1)`

This is one of the main reasons heaps are useful for priority queues.

A priority queue repeatedly needs access to the highest-priority item without fully sorting all remaining items.

---

## 27. Build heap

A particularly important complexity result is:

`Build heap = O(n)`

At first this may appear surprising.

If one inserts `n` elements individually and each insertion costs `O(log n)`, the total can be:

`O(n log n)`

But bottom-up heap construction is different.

It starts from the final internal node and performs sift-down operations toward the root.

Most nodes are near the bottom and can move only a small distance.

Only a small number of nodes are capable of moving a large distance.

The total work therefore sums to:

`O(n)`

This is why the C++, Python, and JavaScript heap implementations construct a heap bottom-up.

---

## 28. Heap sort

Heap sort can be built from the heap operations.

The basic process is:

1. Build a heap.
2. Extract the maximum.
3. Repeat until the heap is empty.
4. Reverse the extraction sequence if ascending order is required.

Build heap:

`O(n)`

Repeated extraction:

`O(n log n)`

Total:

`O(n log n)`

The Python implementation provides `heap_sort`.

The JavaScript implementation provides `heapSort`.

The C++ case study demonstrates the underlying heap mechanism directly.

---

## 29. Comparison of binary search, merge sort, and heaps

| Technique | Primary purpose | Typical complexity |
|---|---|---|
| Linear search | Find an item without ordering assumptions | `O(n)` |
| Binary search | Search an ordered space | `O(log n)` |
| Merge sort | Produce a sorted sequence | `O(n log n)` |
| Heap | Maintain repeated priority access | `O(log n)` insertion/extraction |
| Heap peek | Read highest priority | `O(1)` |
| Build heap | Construct heap from existing data | `O(n)` |

Each technique solves a different problem.

It is incorrect to treat `O(log n)` as universally better than `O(n log n)` without considering the operation being performed.

Sorting an unsorted array cannot generally be replaced by one binary search.

---

## 30. Python implementation

The Python script is organized from simple concepts toward advanced implementations.

It demonstrates:

- Logarithmic growth
- Linear search
- Iterative binary search
- Recursive binary search
- First occurrence search
- Last occurrence search
- Lower bound
- Upper bound
- Integer square root using binary search
- Binary search on a shipping-capacity answer space
- Divide-and-conquer recursion
- Recursive merge sort
- Stable merge sort for records
- Bottom-up merge sort
- Max heap
- Heap insertion
- Heap extraction
- Heap validation
- Heap sort
- Edge cases
- Correctness testing
- Performance measurement
- Complexity tables
- Common mistakes
- Real-world applications

The implementation uses Python's type annotations and `dataclass` for the student-record stability example.

No third-party packages are required.

---

## 31. JavaScript implementation

The JavaScript implementation provides the same algorithmic concepts in a form appropriate for a JavaScript runtime.

It demonstrates:

- Arrays
- Functions
- Recursion
- Array copying
- Classes
- Error handling
- Binary search
- Boundary search
- Merge sort
- Bottom-up merge sort
- A custom max heap
- Heap sort
- Answer-space binary search
- Correctness assertions
- Runtime measurement

The implementation uses `process.hrtime.bigint()` for high-resolution Node.js timing.

JavaScript arrays are dynamic objects, so implementation-level performance characteristics can differ from C++ arrays or Python lists. The algorithmic complexity remains the same for the operations implemented here.

---

## 32. C++ case study

The C++ program models a package distribution center.

Each package contains:

- Package ID
- Priority
- Weight
- Destination

The system needs several different operations.

### Package lookup

Package identifiers are sorted and searched with binary search.

After sorting, a lookup takes:

`O(log n)`

for the search itself.

The sorting cost must also be considered if the data was not already sorted.

### Priority scheduling

Packages are inserted into a max heap.

Higher-priority packages are processed first.

Insertion:

`O(log n)`

Extraction:

`O(log n)`

Top-priority inspection:

`O(1)`

### Batch priority sorting

The system can sort packages by priority using merge sort.

The complexity is:

`O(n log n)`

### Capacity planning

The program searches for the minimum truck capacity required to process all package weights within a fixed number of days.

This is binary search over an answer space.

The complexity is:

`O(n log S)`

where `S` is the numeric capacity search range.

---

## 33. C++ data structures and design

The case study uses:

- `vector`
- `struct`
- `class`
- custom max heap
- recursive merge sort
- binary search
- validation functions
- exception handling
- high-resolution timing

The `Package` structure stores the domain data.

The `MaxHeap` class encapsulates heap operations.

The `DistributionCenter` class combines package storage and priority scheduling.

This separation makes the algorithmic components reusable while keeping the case study close to a realistic system design.

---

## 34. Complexity of the distribution-center operations

| Operation | Complexity |
|---|---:|
| Add package to vector | Amortized `O(1)` |
| Add package to priority heap | `O(log n)` |
| View highest priority | `O(1)` |
| Process highest priority | `O(log n)` |
| Sort package records with merge sort | `O(n log n)` |
| Binary-search sorted package IDs | `O(log n)` |
| Find minimum shipping capacity | `O(n log S)` |

These complexities describe the individual operations.

The complexity of a complete application depends on how many times each operation is performed.

---

## 35. Edge cases

The implementations explicitly address important edge cases.

### Empty collection

Searching an empty collection should return not-found rather than attempting to access an invalid position.

Sorting an empty collection should return an empty collection.

Extracting from an empty heap should produce an error.

### One-element collection

A single element is already sorted.

Binary search should correctly handle it.

A heap containing one item should allow both peek and extraction.

### Duplicate values

Ordinary binary search may return any occurrence.

First-occurrence and last-occurrence searches are therefore separate algorithms.

### Missing target

Binary search returns a not-found indicator when the target does not exist.

### Negative values

The sorting and searching algorithms can process negative integers.

### Invalid shipping data

The shipping-capacity functions reject empty weight lists and invalid day counts.

The C++ distribution center validates package IDs, priorities, weights, and destinations.

---

## 36. Common binary-search mistakes

### Mistake: forgetting the sorted requirement

Binary search depends on ordering.

Without ordering, discarding half of the search space is not logically justified.

### Mistake: failing to shrink the search interval

After examining the middle element, the algorithm must exclude the already examined position.

Typical updates are:

`left = middle + 1`

or:

`right = middle - 1`

### Mistake: incorrect midpoint calculation

For fixed-width integer languages, directly calculating:

`(left + right) / 2`

can overflow.

The safer form is:

`left + (right - left) / 2`

### Mistake: confusing search and sorting

Binary search searches an ordered collection.

It does not sort the collection.

If an array is unsorted, sorting it first introduces a separate cost.

---

## 37. Common merge-sort mistakes

### Mistake: forgetting the base case

A recursive sort needs to stop when the range contains zero or one elements.

### Mistake: incorrect merge boundaries

The merge operation must process every element exactly once.

### Mistake: accidentally losing stability

When keys are equal, selecting the left element first preserves the original relative order.

### Mistake: claiming O(log n)

The recursion depth is logarithmic, but the algorithm performs linear work at every level.

The correct time complexity is:

`O(n log n)`

---

## 38. Common heap mistakes

### Mistake: confusing a heap with a sorted array

A heap guarantees parent-child ordering, not complete global ordering.

### Mistake: using incorrect child formulas

For zero-based arrays:

`left = 2i + 1`

`right = 2i + 2`

### Mistake: forgetting to restore the heap property

Insertion requires upward adjustment.

Root removal requires downward adjustment.

### Mistake: assuming build heap is O(n log n)

Bottom-up build heap is:

`O(n)`

This is an important distinction between repeated insertion and bottom-up construction.

---

## 39. Complexity of the main algorithms

### Linear search

Best case:

`O(1)`

Worst case:

`O(n)`

Space:

`O(1)`

### Binary search

Best case:

`O(1)`

Worst case:

`O(log n)`

Iterative auxiliary space:

`O(1)`

Recursive auxiliary space:

`O(log n)`

### Merge sort

Best, average, and worst-case time:

`O(n log n)`

Typical auxiliary space:

`O(n)`

Recursive depth:

`O(log n)`

### Heap insertion

Worst case:

`O(log n)`

### Heap extraction

Worst case:

`O(log n)`

### Heap peek

`O(1)`

### Bottom-up build heap

`O(n)`

### Heap sort

`O(n log n)`

---

## 40. O(log n) versus O(n)

The key difference can be illustrated using powers of two.

| `n` | Approximate `log2(n)` | Linear work `n` |
|---:|---:|---:|
| 8 | 3 | 8 |
| 16 | 4 | 16 |
| 32 | 5 | 32 |
| 1,024 | 10 | 1,024 |
| 1,048,576 | 20 | 1,048,576 |
| 1,073,741,824 | 30 | 1,073,741,824 |

For roughly one billion elements:

`log2(n) ≈ 30`

while:

`n ≈ 1,000,000,000`

That difference explains why algorithms capable of repeatedly eliminating half the search space can be extremely powerful.

The caveat is that the logarithmic algorithm requires the necessary structural property, such as sorted data or a monotonic decision condition.

---

## 41. O(n log n)

`O(n log n)` lies between linear and quadratic growth in the usual hierarchy.

A common source is:

- `O(log n)` levels
- `O(n)` work per level

This gives:

`O(n log n)`

Merge sort is the canonical example.

Heap sort is another important example.

For large inputs, `O(n log n)` is generally much more scalable than `O(n²)` sorting algorithms such as simple quadratic comparison sorts.

---

## 42. Recurrence relationships

The main recurrence patterns in this study are:

### Binary search

`T(n) = T(n/2) + O(1)`

Result:

`O(log n)`

### Merge sort

`T(n) = 2T(n/2) + O(n)`

Result:

`O(n log n)`

The difference is the number of recursive subproblems.

Binary search creates one smaller subproblem.

Merge sort creates two smaller subproblems and then performs linear combination work.

This is a fundamental divide-and-conquer distinction.

---

## 43. Performance considerations

Big-O complexity is not the same as wall-clock execution time.

Actual performance can depend on:

- CPU architecture
- memory hierarchy
- cache locality
- branch prediction
- allocation overhead
- interpreter or compiler behavior
- runtime optimization
- input distribution
- constant factors
- object representation

For example, a simple linear scan over a tiny contiguous array can be faster than a more complicated logarithmic operation because the linear scan has very low overhead and excellent memory locality.

As input sizes become sufficiently large, asymptotic behavior becomes increasingly important.

The Python, JavaScript, and C++ files include practical timing demonstrations.

These measurements should be treated as demonstrations rather than universal benchmarks.

---

## 44. Python versus JavaScript versus C++

The three implementations emphasize different aspects of the same algorithmic ideas.

### Python

Python provides concise implementations that make algorithmic structure easy to inspect.

The Python version emphasizes:

- readable algorithms
- type annotations
- recursive structure
- data classes
- testing
- educational demonstrations

### JavaScript

JavaScript demonstrates the same ideas in a language commonly used for applications and web development.

It emphasizes:

- dynamic arrays
- classes
- functions
- runtime behavior
- Node.js timing
- error handling
- executable algorithm implementations

### C++

C++ emphasizes lower-level control and an industry-style system model.

The case study demonstrates:

- explicit data structures
- vectors
- classes
- custom heap implementation
- object ownership through standard containers
- exceptions
- high-resolution timing
- system-oriented design

The algorithmic principles remain language-independent even though implementation details differ.

---

## 45. Security and reliability considerations

These algorithms are not security mechanisms by themselves, but implementation choices can affect system reliability.

For binary search, incorrect boundary handling can cause incorrect results or, in poorly designed implementations, non-terminating loops.

For C++, integer overflow is a practical correctness concern because fixed-width integer types have finite ranges.

For shipping-capacity calculations, totals may exceed the range of a small integer type when very large datasets are processed. The C++ implementation therefore uses `long long` for cumulative capacity.

For heap-based systems, invalid input should be rejected before it enters the data structure.

The C++ case study validates:

- package IDs
- priorities
- weights
- destinations
- shipping days

Correct algorithm selection does not remove the need for input validation and defensive programming.

---

## 46. Design considerations

Algorithm selection should be based on the operation the system needs to perform.

If the requirement is:

> Find one value in an already sorted array.

Binary search is appropriate.

If the requirement is:

> Sort a collection of records.

Merge sort is one possible approach.

If the requirement is:

> Repeatedly retrieve the highest-priority item.

A heap is a natural data structure.

If the requirement is:

> Determine the smallest capacity that satisfies a monotonic feasibility condition.

Binary search over the answer space can be appropriate.

The important design principle is to match the data structure and algorithm to the required operation.

---

## 47. Practical applications

### Binary search

Applications include:

- searching sorted records
- finding insertion boundaries
- lookup in ordered datasets
- threshold discovery
- capacity planning
- numerical search
- monotonic decision problems

### Merge sort

Applications include:

- stable record sorting
- external sorting
- large-scale data processing
- linked-list sorting
- deterministic `O(n log n)` sorting

### Heaps

Applications include:

- priority queues
- task scheduling
- event simulation
- top-k problems
- shortest-path algorithms
- resource management
- job scheduling

---

## 48. Important distinction: sorting before searching

Suppose a collection contains `n` unsorted elements.

A binary search cannot immediately be applied.

If the collection must first be sorted using merge sort, the preprocessing cost is:

`O(n log n)`

After sorting, each binary search costs:

`O(log n)`

If many searches are performed against the same static dataset, paying the sorting cost once can be worthwhile.

For example, with `q` searches:

`O(n log n + q log n)`

This can be substantially better than performing `q` linear searches:

`O(qn)`

when `q` is large.

This is an important practical reason to consider preprocessing.

---

## 49. Important distinction: heap versus sorted data

A heap provides efficient access to the highest or lowest priority element.

It does not provide arbitrary sorted-order lookup.

If the requirement is repeated extraction of the maximum, a heap can be highly appropriate.

If the requirement is arbitrary search by key, a heap is not a replacement for a search-oriented structure.

Data structures optimize different operations.

---

## 50. Testing strategy

The implementations include correctness tests covering:

- empty collections
- single-element collections
- duplicate values
- positive values
- negative values
- sorted values
- reverse-order values
- missing search targets
- heap construction
- heap extraction
- merge sorting
- binary-search boundaries
- shipping-capacity search

Randomized tests are also used.

Testing multiple input sizes helps detect errors that may not appear in a single example.

---

## 51. Core concepts demonstrated by the code

The Python implementation demonstrates the algorithms in a study-oriented form.

The JavaScript implementation demonstrates their executable application in a dynamic-language environment.

The C++ implementation integrates the concepts into a distribution-center case study.

The three implementations collectively demonstrate that complexity analysis is not tied to one programming language.

The same mathematical structure appears across all three languages:

Binary search:

`O(log n)`

Merge sort:

`O(n log n)`

Heap insertion:

`O(log n)`

Heap extraction:

`O(log n)`

Heap peek:

`O(1)`

Build heap:

`O(n)`

---

## 52. Essential conceptual distinction

The most important distinction in this study is:

`O(log n)` does not mean that an algorithm is merely "fast."

It means the amount of work grows logarithmically with the input size.

For binary search, the reason is structural:

**each step eliminates approximately half of the remaining search space.**

By contrast:

`O(n)`

means the algorithm may need to process every input element.

And:

`O(n log n)`

often means the algorithm performs linear work across a logarithmic number of levels.

Understanding why the complexity arises is more important than memorizing the notation.
