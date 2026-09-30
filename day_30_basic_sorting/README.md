# Basic Sorting: Bubble Sort, Selection Sort, and Insertion Sort

This project implements three fundamental comparison-based sorting algorithms from scratch:

- Bubble sort
- Selection sort
- Insertion sort

The implementations focus on the mechanics that distinguish these algorithms rather than relying on a language-provided sorting function. The Python program provides an instrumented algorithm laboratory, the JavaScript program models sorting as reusable jobs in an event-driven runtime, and the C++ program applies the algorithms to a realistic inventory-record ordering problem.

The central comparison is not simply which algorithm produces a sorted sequence. All three can correctly sort the same data. The important differences are how they perform comparisons, how they move elements, how they behave on different input arrangements, whether equal elements retain their relative order, and how much additional memory they require.

## Sorting Model

A comparison-based sorting algorithm determines the order of elements by repeatedly asking whether one element belongs before another.

For ascending numeric sorting, the fundamental relation is:

`a < b`

When the relation is true, `a` should appear before `b`. An implementation can use this relation in different ways.

Bubble sort compares neighboring elements and exchanges them when they are reversed.

Selection sort searches an unsorted region for the element that should occupy its next position.

Insertion sort assumes that a prefix is already ordered and inserts the next element into that prefix.

The three algorithms therefore solve the same ordering problem using different movement strategies.

## Comparisons

A comparison is an ordering decision between two elements.

For example, when sorting `[7, 3, 5]` in ascending order, comparing `7` and `3` determines that `3` belongs before `7`.

Comparisons are central to the running time of all three algorithms because the algorithms do not know an element's final position without examining relationships between elements.

### Bubble sort comparisons

Bubble sort compares adjacent positions:

`values[index]` with `values[index + 1]`

A successful comparison that discovers an inversion immediately leads to a swap.

For example:

`[7, 3, 5]`

The first comparison sees `7` and `3`. Since `3 < 7`, they are exchanged:

`[3, 7, 5]`

The next comparison sees `7` and `5`, producing:

`[3, 5, 7]`

After a complete pass, a large element that was too far to the left has moved toward the right side.

The Python, JavaScript, and C++ implementations all use an early-exit condition. If a complete pass performs no swaps, the sequence contains no adjacent inversion and is already sorted.

### Selection sort comparisons

Selection sort uses comparisons to locate the best candidate in the remaining unsorted region.

For:

`[4, 2, 5, 1, 3]`

the first position requires a scan of all remaining elements to determine that `1` is the minimum. The algorithm then moves `1` to the first position.

The important property is that the scan occurs even if the input is already sorted. Selection sort does not obtain a linear best case merely because the input contains no inversions.

### Insertion sort comparisons

Insertion sort compares the current element with elements in the already-sorted prefix.

For:

`[2, 4, 7, 3]`

the prefix `[2, 4, 7]` is sorted when `3` is selected. The algorithm compares `3` with `7`, shifts `7`, compares `3` with `4`, shifts `4`, and then inserts `3` after `2`.

This makes insertion sort sensitive to how close the input is to its final ordering.

## Swaps and Element Movement

A swap exchanges two positions.

Bubble sort uses adjacent swaps as its fundamental movement operation. An element can therefore travel many positions through a sequence of individual exchanges.

Selection sort generally performs far fewer swaps. It first finds the selected element and then exchanges it with the element occupying the target position.

Insertion sort is different from both. The implementations primarily shift elements to create a gap and then write the current element into that gap. Treating every shift as a swap would obscure the actual mechanism of insertion sort.

This distinction matters when evaluating operation counts. Two algorithms can perform similar numbers of comparisons while producing very different numbers of writes or swaps.

Selection sort is often useful when minimizing the number of exchanges is important, while insertion sort can efficiently exploit existing order through local shifts.

## Stability

A sorting algorithm is **stable** when equal-key records retain their original relative order.

Consider records sorted by `score`:

| Original position | Record | Score |
|---:|---|---:|
| 0 | Asha | 80 |
| 1 | Bharat | 70 |
| 2 | Chen | 80 |
| 3 | Divya | 60 |
| 4 | Esha | 80 |

The three records with score `80` originally appear as:

`Asha, Chen, Esha`

A stable sort by score keeps them in that order even though their score values are equal.

Stability matters when records have multiple attributes. A system might first sort employees by department and later perform a stable sort by salary. The second sort can preserve the earlier department ordering among employees with equal salaries.

### Bubble sort stability

The implementation uses a strict inversion test:

`before(values[index + 1], values[index])`

Equal elements do not trigger a swap. Because only inverted adjacent pairs are exchanged, equal records do not cross each other.

The implementation is therefore stable.

### Selection sort stability

Selection sort is not stable in its normal in-place form.

A selected minimum can be exchanged across records with an equal key. The exchange can change the relative order of records whose primary keys are equal.

The C++ inventory example makes this behavior visible using SKUs with equal stock quantities.

### Insertion sort stability

Insertion sort uses a strict comparison when deciding whether the current item belongs before an item in the sorted prefix.

An equal-key element therefore stops the shifting process rather than moving beyond an earlier equal-key element.

The implementation is stable.

## In-Place Behavior

An in-place sorting algorithm modifies the existing collection rather than constructing another full collection to hold the result.

All three implementations modify their input sequence directly.

Their auxiliary sorting space is therefore `O(1)` apart from temporary storage required for individual values and the input storage supplied by the caller.

This does not mean that every language operation uses literally zero temporary memory. For example, the Python and C++ implementations hold a temporary value during insertion, and the JavaScript implementation uses a temporary value during swaps. The relevant algorithmic distinction is that they do not allocate a second array proportional to the input size for sorting.

The JavaScript job layer intentionally creates separate arrays before running concurrent demonstrations. That copying belongs to the demonstration infrastructure, not to the sorting algorithms themselves.

## Time Complexity

| Algorithm | Best case | Average case | Worst case | Stable | In-place |
|---|---:|---:|---:|---|---|
| Bubble sort with early exit | `O(n)` | `O(n²)` | `O(n²)` | Yes | Yes |
| Selection sort | `O(n²)` | `O(n²)` | `O(n²)` | No | Yes |
| Insertion sort | `O(n)` | `O(n²)` | `O(n²)` | Yes | Yes |

The best-case behavior deserves special attention.

Bubble sort reaches `O(n)` when its early-exit check detects that an entire pass made no swaps.

Insertion sort reaches `O(n)` when the input is already ordered because each new element needs only a small number of comparisons and no shifts.

Selection sort remains `O(n²)` because it continues scanning the remaining region to locate the next selected element.

For large arbitrary datasets, these quadratic algorithms become expensive. Their primary educational value is that their mechanics make comparison-based ordering, stability, in-place mutation, and input sensitivity easy to observe.

## Best Cases and Worst Cases

### Bubble sort

For an already sorted sequence:

`[1, 2, 3, 4, 5]`

the first pass performs comparisons but no swaps. The algorithm terminates immediately.

For reverse-sorted data:

`[5, 4, 3, 2, 1]`

many adjacent inversions must be removed. Elements repeatedly move through the sequence, producing quadratic behavior.

### Selection sort

An already sorted sequence still requires the algorithm to inspect each remaining region.

For `n` elements, the number of comparisons is:

`(n - 1) + (n - 2) + ... + 1`

which is:

`n(n - 1) / 2`

This is `O(n²)`.

Selection sort can still use relatively few swaps because a swap is performed only after the correct element for a position has been identified.

### Insertion sort

An already sorted sequence is favorable because each new element is already in the correct position relative to the sorted prefix.

Reverse-sorted input is unfavorable because every new element may need to move across the entire existing prefix.

The number of shifts can therefore grow quadratically.

## Python Implementation

The Python program is an executable algorithm laboratory rather than a collection of isolated functions.

Each sorting function accepts a mutable list and a comparison function. This separates the ordering rule from the mechanics of the algorithm.

`SortStats` records comparisons, swaps, and writes. This makes it possible to observe differences that a final sorted array cannot reveal.

The program tests:

- empty collections
- single-element collections
- duplicate values
- already sorted input
- reverse-sorted input
- mixed input
- ascending and descending ordering
- record stability
- randomized correctness
- operation counts
- small-input timing

The randomized tests use Python's `sorted()` only as an independent correctness oracle. None of the three educational implementations calls the library sorting operation.

The record example uses a `Student` data class with a `score` key and original position. Because the comparison considers only the score, the relative order of equal scores can be inspected directly.

The timing section intentionally uses modest input sizes. These measurements are useful for observing behavior but should not be treated as rigorous benchmarks because interpreter overhead, operating-system scheduling, processor state, and other environmental factors affect elapsed time.

## JavaScript Implementation

The JavaScript implementation uses the same three sorting mechanisms but adds a runtime-specific perspective.

The `SortJob` class treats a sorting operation as an executable job with explicit states:

`created → running → completed`

A failed operation moves into the `failed` state.

The job uses `Promise.resolve()` to demonstrate an event-loop boundary. The sorting algorithms themselves remain synchronous CPU-bound operations. Wrapping them in a Promise does not make the computation parallel or remove its CPU cost.

`Promise.all()` is used to execute independent demonstrations together. Each job receives a copy of the input array because the algorithms are in-place. Sharing the same mutable array between jobs would make the results dependent on execution order and would introduce avoidable state interference.

The JavaScript program also uses a separate numeric reference sort for randomized testing. The reference uses the built-in array sorting facility only for verification; the three implementations under study never invoke it.

## C++ Case Study

The C++ program models a warehouse inventory-ordering scenario.

Each `InventoryItem` contains:

- an SKU
- a stock quantity
- an arrival order

The sorting key is stock quantity. Arrival order is intentionally not part of the comparison.

This creates a realistic reason to care about stability. If several products have the same stock quantity, a stable algorithm preserves their original arrival order. An unstable algorithm can change that order while still producing a numerically correct stock ordering.

The case study therefore demonstrates a distinction that cannot be observed reliably with unique integers alone.

The C++ implementation uses templates so the sorting algorithms are independent of the specific record type. A comparison function determines the desired ordering.

`SortStats` records comparisons, swaps, and writes.

The `swapTracked()` helper centralizes exchange accounting, while insertion sort records shifts separately because shifting is its fundamental movement mechanism.

The program validates the resulting order, tests ascending and descending comparisons, examines sorted and reverse-sorted inputs, demonstrates stability with inventory records, and performs randomized correctness testing.

`std::sort` appears only in the randomized testing routine as an independent reference implementation. It is not part of any of the three sorting algorithms.

## Algorithmic Distinctions

| Property | Bubble sort | Selection sort | Insertion sort |
|---|---|---|---|
| Fundamental movement | Adjacent swaps | Final-position swaps | Shifts and insertion |
| Maintains a useful invariant | Sorted suffix | Correct prefix | Sorted prefix |
| Early exit on sorted input | Yes | No | Naturally |
| Stable in this implementation | Yes | No | Yes |
| Worst-case comparisons | Quadratic | Quadratic | Quadratic |
| Worst-case movement | Many swaps | Relatively few swaps | Many shifts |
| Useful input characteristic | Detectable existing order | Few exchanges desired | Nearly sorted data |

The algorithms are therefore not interchangeable despite having the same asymptotic worst-case time complexity.

## Invariants

An invariant is a property that remains true at a particular point in the algorithm.

Bubble sort maintains a sorted suffix after each completed pass. The rightmost part of the array contains elements that no longer need consideration.

Selection sort maintains a prefix containing elements that have already been selected for their final positions.

Insertion sort maintains a sorted prefix before processing each new element.

These invariants explain the algorithms more precisely than describing them merely as repeated comparisons.

## Common Implementation Errors

### Incorrect bubble-sort boundary

The inner loop should avoid comparing against elements that have already reached the sorted suffix. Extending every pass unnecessarily does not change correctness, but it performs avoidable comparisons.

### Missing bubble-sort early exit

Without the no-swap check, bubble sort loses its `O(n)` best case. It would continue performing quadratic numbers of comparisons even when the input is already sorted.

### Swapping equal values unnecessarily

Using a non-strict comparison for an exchange can cause equal records to cross each other. This can destroy stability.

For stable ascending ordering, an inversion should be recognized when the right element is strictly less than the left element.

### Assuming selection sort is stable

Selection sort's low swap count does not imply stability. A single long-distance exchange can move one record past another record with an equal key.

### Implementing insertion sort as repeated swaps

Insertion sort can be implemented using swaps, but its characteristic operation is shifting larger elements and inserting the current value into the resulting gap. Counting and analyzing it as a sequence of swaps hides the algorithm's actual structure.

### Forgetting the empty and single-element cases

The algorithms should safely handle zero or one element. Such inputs are already sorted and should not cause invalid index calculations.

## Validation Strategy

Correctness should not be inferred from a few visible examples.

The implementations use several layers of validation:

- known edge cases test empty, singleton, duplicate, ordered, reverse-ordered, and negative values
- sortedness checks verify the ordering invariant after execution
- randomized tests compare results against an independently implemented reference sort
- record-based tests expose stability behavior
- operation counters reveal how input arrangement changes algorithmic work

Randomized testing is particularly useful because a hand-selected example can accidentally miss a boundary condition.

## Performance Considerations

The three algorithms have quadratic average and worst-case behavior, so their execution cost grows rapidly as input size increases.

For an input of size `n`, quadratic growth means that doubling `n` can lead to roughly four times as much dominant work in cases governed by `n²`.

The exact cost is not identical among the algorithms because comparisons, swaps, shifts, and writes have different behavior.

Bubble sort may perform many exchanges.

Selection sort performs fewer exchanges but still performs a full sequence of searches.

Insertion sort can perform very little movement when the input is already nearly sorted, but can perform many shifts on reverse-sorted data.

The operation counters in the implementations are therefore more informative than treating all primitive operations as identical.

## Practical Interpretation

Bubble sort is particularly useful for understanding adjacent exchanges and the idea of an adaptive early-exit optimization.

Selection sort makes the relationship between searching for a minimum and minimizing exchanges especially clear.

Insertion sort demonstrates why an algorithm can be simple, in-place, and stable while still having a useful best case for partially ordered data.

All three algorithms are important as foundational models because their internal mechanics expose concepts that become harder to see in highly optimized library sorting implementations.

The central lesson is that sorting algorithms with identical `O(n²)` worst-case complexity can still have materially different behavior because their comparison patterns, movement operations, stability properties, and response to input order are different.
