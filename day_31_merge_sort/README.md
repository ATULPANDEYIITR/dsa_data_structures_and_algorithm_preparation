# Merge Sort: Divide and Conquer, Splitting, Merging, Recursion, and Complexity

## Scope

This repository studies **merge sort** as a divide-and-conquer sorting algorithm and implements it without relying on a library sorting routine.

The three implementations use different perspectives:

- The Python program develops merge sort from a recursive algorithm into an instrumented implementation, a stable record sorter, an iterative bottom-up variant, and an inversion-counting algorithm.
- The JavaScript program models sorting as an executable processing workflow and adds event callbacks, asynchronous job handling, stable object sorting, and a bottom-up implementation.
- The C++ program treats merge sort as the core of a transaction reconciliation engine. It uses generic comparators, stable record ordering, explicit metrics, validation, and an additional inversion-counting algorithm.

The central relationship is:

`divide -> recursively sort -> merge`

The important property is that the merge operation receives two already-sorted ranges and combines them into one sorted range in linear time.

---

## Core Idea

Merge sort does not attempt to find the final position of every element immediately.

Instead, it repeatedly reduces the problem:

`[38, 27, 43, 3, 9, 82, 10]`

becomes two smaller problems:

`[38, 27, 43]` and `[3, 9, 82, 10]`

Those are divided again until every subproblem contains zero or one element.

A sequence containing one element is already sorted. This is the **base case** of the recursion.

The algorithm then works in the opposite direction. Small sorted sequences are merged into larger sorted sequences until the complete input has been reconstructed in sorted order.

The key insight is that merging two sorted sequences is much easier than sorting an arbitrary sequence.

For example:

`[3, 27, 38]`

and

`[9, 10, 82]`

can be merged by repeatedly comparing the first unconsumed element from each half.

The smallest available value is selected, and that side advances.

The result is:

`[3, 9, 10, 27, 38, 82]`

---

## Divide and Conquer

Merge sort follows the three stages of divide and conquer closely.

### Divide

The input range is divided around a midpoint.

For a range from `left` to `right`, the implementations calculate the midpoint as:

`left + (right - left) // 2`

rather than directly adding both endpoints.

This formulation is useful in general indexed algorithms because it avoids an integer overflow that can occur with `left + right` when indexes become very large.

### Conquer

Each half is sorted recursively.

The recursive calls operate on progressively smaller ranges:

`sort(left, middle)`

and

`sort(middle + 1, right)`

Eventually the range contains one element, where recursion stops.

### Combine

The sorted halves are passed to the merge operation.

The merge operation has a simple invariant:

> At every iteration, the output prefix contains the smallest elements that can safely be selected from the two remaining sorted ranges.

Because each half is already sorted, only its current front element needs to be considered.

---

## Splitting and the Recursion Tree

For eight elements, the recursive structure is approximately:

`8`
`├── 4`
`│   ├── 2`
`│   │   ├── 1`
`│   │   └── 1`
`│   └── 2`
`│       ├── 1`
`│       └── 1`
`└── 4`
`    ├── 2`
`    │   ├── 1`
`    │   └── 1`
`    └── 2`
`        ├── 1`
`        └── 1`

The exact tree becomes slightly irregular when the input length is not a power of two, but the depth remains logarithmic because each split approximately halves the problem.

The Python trace prints this decomposition for a concrete input. The JavaScript implementation exposes the same process through `onSplit` events.

---

## Merging

The merge operation is the central mechanism of merge sort.

Suppose the current halves are:

`left = [3, 27, 38]`

`right = [9, 10, 82]`

The algorithm compares:

`3` versus `9`

It selects `3`.

It then compares:

`27` versus `9`

It selects `9`.

Next:

`27` versus `10`

It selects `10`.

The remaining values are already ordered relative to one another, so the remaining elements can be copied directly.

The merge therefore processes each element at most a constant number of times.

For a combined range containing `n` elements, merging requires `O(n)` time.

---

## Why an Auxiliary Buffer Is Used

A merge implementation needs to avoid destroying values that have not yet been compared.

The Python, JavaScript, and C++ implementations therefore allocate an auxiliary buffer.

Conceptually:

`values:    [left sorted half | right sorted half]`

`buffer:    [temporary merged representation          ]`

After the merge has selected the correct elements, the merged range is copied back into the original storage.

This means the implementations are not constant-space sorting algorithms.

The additional merge storage is `O(n)`.

The recursive implementation also consumes `O(log n)` call-stack space because the splitting is balanced.

The auxiliary array dominates the asymptotic additional space requirement, giving `O(n)` auxiliary space.

---

## Stability

Merge sort can be stable.

A stable sorting algorithm preserves the original relative ordering of records whose sort keys are equivalent.

Consider:

`Aarav: 82`

`Kabir: 82`

If the records are sorted by score, a stable result keeps Aarav before Kabir because that was their original order.

The merge implementation deliberately chooses the left-half element when the two keys are equivalent.

In Python, this behavior appears in the comparison:

`key(values[i]) <= key(values[j])`

The JavaScript implementation applies the same rule to object records.

The C++ implementation expresses the rule using its comparator. If neither object should precede the other, the element from the left range is selected first.

Stability is important when sorting records through multiple ordering stages. An earlier ordering can remain meaningful when a later stable sort is applied using another key.

---

## Complexity

Merge sort has the recurrence:

`T(n) = 2T(n/2) + O(n)`

The two recursive calls represent sorting the two halves.

The `O(n)` term represents the merge operation.

At each recursion level, the combined size of all subproblems is approximately `n`, so each level performs linear total work.

The number of levels is logarithmic:

`log₂(n)`

Therefore:

`T(n) = O(n log n)`

This applies to the normal top-down implementation in the best, average, and worst cases.

The important distinction is that the amount of work is not reduced to `O(n)` merely because an input happens to be sorted. The Python and JavaScript implementations include an optimization that detects already-ordered adjacent halves and can skip a merge, but the recursive decomposition itself still exists.

The standard asymptotic characterization remains `O(n log n)`.

---

## Best, Average, and Worst Cases

| Case | Merge sort behavior |
|---|---|
| Best case | `O(n log n)` in the standard implementation |
| Average case | `O(n log n)` |
| Worst case | `O(n log n)` |
| Auxiliary storage | `O(n)` |
| Recursive depth | `O(log n)` for balanced splitting |
| Stable | Yes, when the merge chooses the left equivalent element first |

The predictable worst-case complexity is one of merge sort's major algorithmic characteristics.

By comparison, algorithms whose behavior depends heavily on pivot selection or input arrangement can have substantially different worst-case behavior.

---

## Top-Down and Bottom-Up Merge Sort

The Python and JavaScript deliverables contain both recursive top-down and iterative bottom-up approaches.

### Top-Down

Top-down merge sort starts with the entire input and recursively divides it.

The conceptual flow is:

`whole range`

`-> left half + right half`

`-> smaller halves`

`-> single-element ranges`

`-> merge upward`

This version is particularly useful for understanding divide and conquer because the recursive structure directly reflects the mathematical decomposition.

### Bottom-Up

Bottom-up merge sort avoids recursive splitting.

It begins with runs of width `1`.

For example:

`[8] [3] [7] [4] [2] [9] [1] [6]`

The width-1 runs are merged:

`[3, 8] [4, 7] [2, 9] [1, 6]`

Then width-2 runs are merged:

`[3, 4, 7, 8] [1, 2, 6, 9]`

Finally the width-4 runs are merged into the complete sorted sequence.

The width grows approximately as:

`1 -> 2 -> 4 -> 8 -> ...`

This remains `O(n log n)` but does not require recursive function calls.

---

## Python Implementation

The Python program uses a reusable `merge` function and a recursive `merge_sort` implementation.

A single auxiliary list is allocated for the complete sort rather than allocating a new merge buffer for every recursive call. This makes the memory behavior more controlled.

The implementation also accepts an optional `key` function. That permits records such as `Student` objects to be ordered by `score` without changing the merge algorithm itself.

The `operation_counter` records comparisons, merges, boundary checks, and skipped merges. These values make the algorithm's behavior observable without changing its fundamental logic.

The Python program also contains `merge_sort_with_trace`, which prints the actual recursive decomposition and the resulting merges. This is useful for connecting the abstract recursion tree to concrete data.

The `count_inversions` function demonstrates an important extension of merge sort. When a right-half element is selected before the remaining left-half elements, all those remaining left elements form inversions with it. Instead of examining every pair individually, the merge step counts the entire group at once.

That produces an `O(n log n)` inversion-counting algorithm.

---

## JavaScript Implementation

The JavaScript implementation uses a different presentation from the Python program.

Its `mergeSort` function accepts lifecycle callbacks:

`onSplit`

and

`onMerge`

These callbacks expose the recursive workflow without coupling the sorting algorithm to a specific user interface.

The implementation returns both the sorted result and metrics such as comparison count, merge count, split events, and skipped merges.

This makes the algorithm suitable for an event-driven application model where another component could observe sorting progress.

The JavaScript implementation also demonstrates asynchronous job processing through `processSortJob`.

The important distinction is that wrapping a CPU-bound sort in a Promise does not automatically make the algorithm parallel. JavaScript's event loop still executes the sorting computation synchronously unless the work is explicitly moved to mechanisms such as worker threads.

The program also sorts objects by a selected property and verifies stability using student records.

---

## C++ Transaction Reconciliation Case Study

The C++ program models a transaction reconciliation pipeline.

Each `Transaction` contains:

- A transaction identifier
- An account identifier
- An amount stored as integer cents
- Its original position in the incoming stream

The merge sort engine is implemented generically so that it can operate on different element types through a comparator.

The transaction-specific comparator orders records by `amount_cents`.

This produces a useful stability requirement.

If two transactions have the same amount, their original order should remain unchanged unless another explicit business rule says otherwise.

For example:

`TX-1001: 12500 cents`

`TX-1003: 12500 cents`

must retain their relative order after sorting by amount.

The C++ implementation verifies this property explicitly.

The case study also instruments the recursive algorithm with `SortMetrics`. This exposes the number of comparisons, merge operations, and split operations performed during execution.

This is useful when studying the relationship between implementation behavior and asymptotic complexity.

---

## Generic Comparison in C++

The C++ implementation does not hard-code numeric ordering into its core merge operation.

Instead, `merge_ranges` accepts a comparator.

The comparator answers whether one value should precede another.

This makes the same merge engine applicable to numeric values, transactions, or other records.

The merge operation uses the comparator in a way that preserves equivalent elements from the left range before equivalent elements from the right range.

This separates algorithmic behavior from application-specific ordering rules.

The algorithm therefore handles the general pattern:

`data + ordering policy -> stable merge sort`

rather than only:

`integer array -> ascending integer sort`

---

## Inversion Counting

An inversion is a pair of positions `(i, j)` satisfying:

`i < j`

and

`values[i] > values[j]`

For:

`[2, 4, 1, 3, 5]`

the inversions are:

`(2, 1)`

`(4, 1)`

`(4, 3)`

so the total is `3`.

A direct pair-by-pair implementation takes `O(n²)` time.

Merge sort provides a more efficient approach.

During the merge step, suppose the smallest remaining right-half value is selected because it is smaller than the current left-half value.

Because the left half is already sorted, every unconsumed value in the left half is also greater than that right-half value.

Therefore the number of new inversions can be calculated as:

`middle - left_index + 1`

The Python, JavaScript, and C++ programs use this principle.

The resulting inversion-counting algorithm runs in `O(n log n)` time.

---

## Optimization for Already Ordered Halves

The Python and JavaScript recursive implementations check whether:

`last(left_half) <= first(right_half)`

If this is true, the two sorted halves can already be treated as one sorted range.

No element-level merge is necessary.

This is a practical optimization because it avoids copying elements when the two halves are already correctly ordered.

It does not change the standard worst-case complexity.

It also illustrates an important implementation principle: asymptotic complexity describes the growth bound, while concrete optimizations can still reduce actual work for particular input distributions.

---

## Edge Cases

The implementations explicitly handle:

- Empty arrays
- Single-element arrays
- Already-sorted input
- Reverse-sorted input
- Duplicate values
- Negative numeric values
- Repeated equal keys in records
- Odd-length arrays
- Non-power-of-two input sizes

An empty or single-element sequence is already sorted, so the recursive implementation terminates immediately.

Odd-sized ranges are split as evenly as integer division permits. The two halves need not have exactly equal sizes. They only need to be small enough that recursion eventually reaches the base case.

---

## Common Implementation Errors

### Forgetting the Base Case

Without a condition such as `left >= right`, recursion would continue indefinitely.

The base case represents a range that requires no sorting.

### Incorrect Midpoint Calculation

Using an unsafe midpoint expression can cause integer overflow in languages with fixed-width integer types.

The implementations use the safer difference-based calculation.

### Losing Stability

Changing the merge condition so that the right element wins when keys are equal can reverse the relative ordering of equivalent records.

Stable merging deliberately gives the left equivalent element priority.

### Copying the Wrong Range

The merge must copy the complete merged range back into the original storage.

Copying only one half or using incorrect boundaries can leave stale values in the output.

### Off-by-One Errors

The implementations use inclusive range endpoints in the recursive C++ and Python core algorithms.

That means a range from `left` through `right` contains:

`right - left + 1`

elements.

The midpoint and merge boundaries must consistently follow this convention.

### Recreating Buffers Unnecessarily

Allocating a new auxiliary array during every merge can create unnecessary allocation overhead.

The Python and C++ recursive implementations allocate one reusable buffer for the complete sort.

---

## Recursive Depth and Practical Constraints

Balanced merge sort has logarithmic recursion depth.

For `n` elements, the depth is approximately:

`O(log n)`

This is much smaller than the input size itself, but recursive implementations still depend on the runtime's call-stack capacity.

The bottom-up versions avoid this recursive call stack.

The iterative approach can therefore be useful when an environment has strict stack constraints or when avoiding recursion simplifies operational behavior.

The auxiliary data buffer remains necessary for the standard stable merge implementation used here.

---

## Memory Behavior

Merge sort's major memory cost is the temporary storage required during merging.

For an input of `n` elements, the auxiliary buffer requires `O(n)` storage.

The buffer is reused across merge operations.

This is preferable to allocating separate temporary containers for every recursive merge because it keeps the peak auxiliary allocation bounded by the input size.

For large production datasets, the memory requirement should be considered alongside the algorithm's excellent time complexity.

If data cannot fit into memory, an external merge sort architecture can divide the data into manageable sorted runs and merge those runs from external storage. That is a separate systems-level design because the merge operation must then account for I/O rather than only in-memory array access.

---

## Practical Applications

Merge sort is particularly useful when predictable `O(n log n)` sorting behavior and stability are valuable.

Examples include:

- Sorting transaction records by amount while preserving the arrival order of equal amounts.
- Ordering event records by timestamp while retaining source order for identical timestamps.
- Sorting database-export records by a secondary key after an earlier stable ordering.
- Counting inversions or measuring how far a sequence differs from sorted order.
- Merging independently sorted data streams.
- Building external sorting pipelines where large datasets are processed in sorted runs.

The C++ transaction example demonstrates the first case directly, while the inversion-counting implementations demonstrate how the merge mechanism can support a related analytical computation.

---

## Merge Sort Compared With Insertion Sort

Insertion sort is simple and can perform well for very small or nearly sorted inputs.

Its worst-case time complexity is `O(n²)`.

Merge sort provides predictable `O(n log n)` behavior for large inputs but uses additional storage in the implementation presented here.

The algorithms therefore have different operational trade-offs.

Merge sort gains efficiency from dividing the input and exploiting the fact that merging two sorted ranges is linear.

---

## Merge Sort Compared With Unstable In-Place Sorting

An in-place sorting algorithm can reduce auxiliary memory requirements, but it may not preserve the relative order of equal records.

The implementations here intentionally prioritize stable behavior and predictable `O(n log n)` running time over constant auxiliary storage.

That trade-off is particularly relevant when sorting structured records rather than anonymous numeric values.

---

## Production Considerations

A production merge-sort implementation should define the ordering contract precisely.

For structured records, the comparator should establish a consistent ordering. If the ordering policy is inconsistent, the merge algorithm cannot reliably produce the intended result.

Large inputs should also be evaluated for:

- Memory capacity for the auxiliary buffer
- Integer overflow in index arithmetic
- Recursive stack limits
- Cost of expensive comparison functions
- Cost of copying large records
- Stability requirements
- Whether an iterative implementation is operationally preferable
- Whether the dataset must be processed externally rather than entirely in memory

The C++ implementation moves records into the auxiliary buffer during the final copy, which can reduce unnecessary copying for movable types.

For expensive record objects, the representation and movement cost can become significant even when the algorithmic comparison count remains `O(n log n)`.

---

## Security and Reliability Considerations

Merge sort itself is not a security boundary, but its surrounding application can have reliability and security requirements.

Input validation prevents malformed data from violating application assumptions.

The C++ transaction model stores monetary values as integer cents rather than floating-point values. This avoids binary floating-point representation issues for exact currency amounts.

Sorting should not be treated as validation. A correctly sorted dataset can still contain invalid records, duplicate transaction identifiers, unauthorized data, or corrupted business fields.

When sort keys originate from untrusted input, the surrounding system should validate their type, range, encoding, and business meaning before they enter downstream processing.

---

## Verification Strategy

The three implementations test more than one convenient input.

The test cases cover empty inputs, single elements, duplicates, sorted sequences, reverse-sorted sequences, negative values, and randomly generated values.

The programs compare their merge-sort output against an independent expected ordering during verification.

This is important because an algorithm can appear correct on a small example while still containing boundary errors.

The stable-record tests verify a property that ordinary numeric equality tests cannot detect: equal keys must retain their relative order.

The inversion-counting examples separately verify the analytical extension of the merge operation.

---

## Relationship Between the Main Concepts

The concepts in this topic are distinct parts of one algorithmic mechanism.

**Divide and conquer** is the overall strategy.

**Splitting** is the divide phase that reduces one large sorting problem into smaller ranges.

**Recursion** provides the natural control structure for repeatedly applying that reduction until the base case is reached.

**Merging** is the combine phase. It exploits the fact that the recursively sorted halves are already ordered.

**Complexity** describes the resulting cost. There are logarithmically many levels of balanced division, and each level performs linear total merging work, giving `O(n log n)` time.

Removing any one of these ideas changes the structure of the algorithm. The recursive splitting alone does not sort the data, and merging arbitrary unsorted ranges would not provide the linear-time combine step that gives merge sort its efficiency.

---

## Implementation Summary

| Implementation | Primary perspective | Important mechanisms |
|---|---|---|
| Python | Algorithmic learning and instrumentation | Recursive merge sort, stable records, bottom-up sorting, inversion counting, metrics |
| JavaScript | Event-driven processing model | Split/merge callbacks, object sorting, async job processing, bottom-up sorting, inversion counting |
| C++ | Transaction reconciliation system | Generic comparator, stable records, reusable buffer, validation, metrics, inversion counting |

All three implementations use the same fundamental mathematical idea while expressing it through different language capabilities and application structures.

The common invariant is that each merge receives two sorted ranges and produces one sorted range without losing elements or changing the relative order of equivalent keys.
