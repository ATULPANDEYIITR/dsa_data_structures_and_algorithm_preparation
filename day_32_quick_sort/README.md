# Quick Sort

Quick sort is a comparison-based sorting algorithm built around a central operation called **partitioning**. A chosen element or pivot is used to divide a range into smaller regions. The algorithm then recursively sorts those regions.

The implementation set in this repository approaches quick sort from three complementary perspectives:

- The Python program develops the algorithm from basic partitioning through pivot strategies, duplicate handling, worst-case behavior, randomized correctness testing, and comparison with merge sort.
- The JavaScript program emphasizes executable algorithm design, explicit-stack recursion control, deterministic randomness, event-loop considerations, and metrics.
- The C++ program models a transaction-processing system in which sorted transaction amounts become input to ordered-statistics calculations. It also compares recursive, three-way, iterative quick sort, and merge sort implementations.

The central relationship is:

`pivot selection → partition → smaller subproblems → recursive or iterative processing → sorted array`

## Core Mechanism

Suppose the input is:

`[34, 7, 23, 32, 5, 62, 19]`

A quick-sort implementation selects a pivot. If `19` is selected, partitioning rearranges the current range so that values smaller than the pivot occupy one region and values greater than the pivot occupy another.

The important point is that partitioning does **not** need to completely sort either region. It only establishes enough ordering that the pivot separates the two subproblems.

After partitioning, the algorithm conceptually becomes:

`sort(left region) + pivot region + sort(right region)`

For a two-way partition, the regions normally represent values less than or equal to the pivot and values greater than the pivot. A three-way partition adds an explicit region for values equal to the pivot.

## Pivot Selection

The pivot strongly influences the shape of quick sort's recursion tree.

A pivot can be selected from several locations:

| Strategy | Mechanism | Important behavior |
|---|---|---|
| First element | Uses the left boundary | Vulnerable when input is already ordered and the first value is extreme |
| Last element | Uses the right boundary | Produces a quadratic pattern on common sorted inputs |
| Middle element | Uses the middle position | Often avoids obvious sorted-input extremes, but position does not guarantee median value |
| Random element | Chooses a position probabilistically | Makes predictable adversarial patterns harder to construct |
| Median-of-three | Compares first, middle, and last values | Uses a small amount of local information to seek a better pivot |

The pivot does not have to be the mathematical median. What matters operationally is how balanced the resulting partitions are.

A partition of approximately:

`n / 2 + n / 2`

creates a recursion tree with height close to `log₂(n)`.

A partition of:

`n - 1 + 0`

creates a long chain of recursive calls.

The Python and C++ implementations expose pivot strategies explicitly so that this difference can be observed through comparison counts and recursion depth.

## Partitioning

Partitioning is the operation that rearranges a subarray around the selected pivot.

### Lomuto partitioning

The Lomuto implementation used in the examples keeps a boundary marking the end of the region containing values that satisfy the pivot condition.

For a pivot at the end of the range, the scan proceeds from left to right:

`[unknown values] | [values <= pivot] | pivot`

When a value belongs on the left side, it is swapped toward the boundary and the boundary advances.

At the end, the pivot is exchanged into its final partition position.

This scheme is straightforward to reason about and is useful for teaching the relationship between pivot selection and partitioning. Its simplicity comes with trade-offs. It can perform many swaps and can expose poor pivot choices very clearly.

### Hoare partitioning

The Python implementation also contains Hoare partitioning.

Instead of moving a pivot to a guaranteed final index, two scanning positions move toward each other. One searches from the left for a value that belongs on the right, while the other searches from the right for a value that belongs on the left.

When both are found, they are exchanged.

Hoare partitioning returns a boundary rather than necessarily returning the final sorted position of the pivot. Consequently, recursive calls must be formed around the returned boundary rather than treating it as a pivot-finalization index.

This distinction is an important implementation detail. Mixing the recursion rules of Lomuto and Hoare partitioning can produce incorrect algorithms or infinite recursion.

## Recursive Partitioning

Quick sort terminates naturally when a subarray contains zero or one element.

For a range `[low, high]`, the recursive process is conceptually:

`if low >= high: stop`

Otherwise:

- choose a pivot
- partition the range
- recursively process the left region
- recursively process the right region

The Python, JavaScript, and C++ implementations track recursion depth so that the shape of the recursion tree becomes observable.

A balanced recursion tree has approximately logarithmic depth. A repeatedly unbalanced tree can have depth proportional to the number of elements.

This difference matters because recursion consumes stack space. The asymptotic auxiliary space commonly associated with quick sort is `O(log n)` when partitioning remains reasonably balanced, but a naive recursive implementation can require `O(n)` stack space in the worst case.

## Three-Way Partitioning

Duplicate-heavy data creates a special opportunity for optimization.

Consider:

`[5, 3, 5, 2, 5, 8, 5, 1, 5, 7, 5]`

A conventional two-way partition can repeatedly process values equal to the pivot.

Three-way partitioning creates three regions:

`values < pivot | values == pivot | values > pivot`

The middle region is already complete and does not need recursive sorting.

The Python, JavaScript, and C++ implementations contain three-way quick sort specifically to demonstrate this behavior.

This technique is particularly useful when an application frequently sorts data with low cardinality, such as categorical values or datasets containing many repeated measurements.

## Worst-Case Behavior

Quick sort has:

- best-case time: `O(n log n)`
- expected or average time: `O(n log n)`
- worst-case time: `O(n²)`

The quadratic case occurs when partitioning repeatedly produces extremely unbalanced subproblems.

For example, suppose the array is already sorted:

`[1, 2, 3, 4, 5, 6, 7]`

If the implementation always selects the last element as pivot, the pivot is already the largest value. Partitioning therefore creates:

`[1, 2, 3, 4, 5, 6] | 7`

The next recursive call repeats the pattern:

`[1, 2, 3, 4, 5] | 6`

The resulting comparison count follows the pattern:

`(n - 1) + (n - 2) + ... + 1`

which is:

`n(n - 1) / 2`

and therefore `O(n²)`.

The demonstration programs deliberately construct this case so that the relationship between pivot choice and worst-case complexity can be measured rather than merely described.

## Why Pivot Choice Matters

The pivot affects the amount of work performed at every recursive level.

A balanced partition approximately halves the problem:

`T(n) = 2T(n/2) + O(n)`

which gives:

`T(n) = O(n log n)`

A maximally unbalanced partition produces:

`T(n) = T(n - 1) + O(n)`

which gives:

`T(n) = O(n²)`

The partition operation itself generally examines the current range in linear time. The difference in total performance therefore comes largely from how many levels of partitioning are required.

Pivot selection is consequently a mechanism for influencing the shape of the recursion tree rather than a separate sorting operation.

## Python Implementation

The Python program is organized around executable algorithm components rather than a collection of isolated syntax examples.

`lomuto_partition()` demonstrates the basic partition mechanism. It records comparisons and swaps through `SortStats`, making the internal work observable.

`quick_sort_lomuto()` uses the classic recursive structure directly.

`hoare_partition()` demonstrates that a different partition contract requires different recursive boundaries. This provides a concrete distinction between two major partition schemes.

`choose_pivot_index()` isolates pivot selection from partitioning. The same Lomuto partition implementation can therefore be evaluated with first-element, last-element, middle-element, random, and median-of-three strategies.

`quick_sort_three_way()` demonstrates how duplicate values can be grouped into an already-complete equality region.

`merge_sort()` provides a comparison algorithm using an auxiliary merge buffer. The implementation makes the different strategy visible: merge sort divides by position first and combines already sorted ranges, while quick sort rearranges elements around pivots.

`verify_against_python_reference()` runs randomized tests against Python's built-in `sorted()` result. This catches partition-boundary errors that may not appear in a small hand-written example.

The program also checks:

- empty arrays
- single-element arrays
- sorted arrays
- reverse-sorted arrays
- arrays containing only duplicates
- negative values
- mixed duplicate values
- invalid non-integer input
- recursion depth
- comparison counts
- swap counts

## JavaScript Implementation

The JavaScript implementation uses the same algorithmic principles but introduces concerns that are specific to JavaScript execution.

`SortMetrics` records algorithm behavior without relying on external packages.

`createDeterministicRandom()` provides repeatable pseudo-random pivot experiments. It is explicitly not a cryptographic random-number generator. Its purpose is reproducible algorithm testing.

`quickSortRecursive()` demonstrates recursive partitioning while allowing the pivot strategy to be changed independently.

`quickSortThreeWay()` uses the Dutch-national-flag-style three-region partition:

`less | equal | greater`

`quickSortIterative()` replaces JavaScript call-stack recursion with an explicit array of ranges. This is relevant when the input can cause a recursive implementation to become excessively deep.

The JavaScript file also performs a large synchronous sorting operation after yielding through `setImmediate()`. The yield does not make the sort itself non-blocking. It demonstrates an important event-loop distinction: scheduling a synchronous computation after an event-loop turn is different from moving the computation into a worker or otherwise preventing event-loop blocking.

For a production browser or Node.js application, a very large synchronous sort can delay timers, requests, rendering, or other event-loop work. Algorithmic efficiency and execution-model behavior therefore both matter.

## C++ Transaction Batch Case Study

The C++ program models a batch-processing service in which transaction amounts are represented as integer cents.

For example:

`1499` represents a transaction of 14.99 currency units.

The workflow is:

`incoming transaction batch → quick sort → ordered transaction amounts → minimum/maximum/median`

The sorting algorithm is therefore an intermediate processing stage rather than the final business operation.

`analyze_sorted_transactions()` assumes the input has already been sorted and calculates the minimum, maximum, and median. This makes the practical reason for sorting explicit: ordered statistics become straightforward after the ordering operation.

The program implements three-way quick sort for the main transaction workflow because duplicate transaction amounts are realistic. Repeated amounts do not require independent recursive processing when they are already known to equal the pivot.

The program also contains an iterative quick sort. It stores pending ranges in a `std::vector` instead of relying entirely on the C++ call stack. This provides an explicit mechanism for controlling auxiliary stack usage.

Merge sort is implemented separately using a reusable temporary buffer. The buffer demonstrates the primary space trade-off between the two algorithms.

## Quick Sort and Merge Sort

| Property | Quick Sort | Merge Sort |
|---|---|---|
| Basic strategy | Partition around a pivot | Split ranges and merge sorted halves |
| Best-case time | `O(n log n)` | `O(n log n)` |
| Expected/average time | `O(n log n)` | `O(n log n)` |
| Worst-case time | `O(n²)` for naive implementations | `O(n log n)` |
| Typical auxiliary space | `O(log n)` expected recursion stack | `O(n)` auxiliary merge storage |
| Main sensitivity | Pivot quality and partition balance | Merge-buffer memory and data movement |
| Duplicate-heavy optimization | Three-way partitioning | Merge process naturally handles duplicates |
| Worst-case predictability | Requires attention to pivot strategy | Worst-case bound remains `O(n log n)` |
| In-place behavior | Common quick-sort implementations rearrange the original array | Typical merge sort requires auxiliary storage for arrays |
| Stability | Standard in-place quick sort is not stable | Merge sort can be implemented as stable |

The algorithms solve the same high-level problem through different mechanisms.

Quick sort performs local rearrangement during partitioning. Merge sort performs deterministic division followed by combination.

Neither algorithm is universally superior. The appropriate choice depends on constraints such as memory, stability requirements, input distribution, worst-case guarantees, cache behavior, implementation complexity, and expected workload.

## Recursion Depth and Stack Safety

Recursive quick sort is elegant because the algorithm naturally describes itself in terms of smaller ranges.

The same property can create a problem.

If every partition removes only one element from further consideration, the recursion depth becomes approximately `n`. For sufficiently large inputs, this can exhaust the language runtime's call stack.

The iterative implementations in the JavaScript and C++ programs replace recursive calls with explicit range stacks.

Another production strategy is **smaller-partition-first recursion**. After partitioning, the implementation recursively processes the smaller side and handles the larger side iteratively. This limits the amount of stack space required by the recursion strategy even when partitions are uneven.

Industrial sorting implementations may go further and use introspective techniques that switch algorithms when recursion depth indicates pathological quick-sort behavior.

## Correctness Conditions

A correct partition implementation must preserve the elements of the input while establishing the required relationship to the pivot.

For a two-way Lomuto partition:

`left region <= pivot`

`pivot position`

`right region > pivot`

The exact inequalities depend on the partition contract. An implementation must consistently use the same rules during partitioning and recursion.

For three-way partitioning:

`less region < pivot`

`equal region == pivot`

`greater region > pivot`

The equality region is important because those elements no longer need recursive processing.

The test programs compare their results with independently produced sorted arrays. Randomized tests are particularly useful because partition bugs often occur at boundaries involving:

- empty subranges
- single-element ranges
- all-equal input
- repeated values
- pivot values at the minimum or maximum
- pivot values occurring many times
- already sorted input
- reverse-sorted input

## Performance Considerations

The dominant quick-sort cost is the amount of partition work accumulated across the recursion tree.

With balanced partitions, each level processes approximately `n` elements, and there are approximately `log n` levels:

`O(n) × O(log n) = O(n log n)`

With repeatedly unbalanced partitions, the amount of work becomes:

`n + (n - 1) + (n - 2) + ... + 1`

which is `O(n²)`.

Operation counters in all three programs are more useful for algorithm analysis than treating one wall-clock benchmark as a universal result. Runtime depends on processor architecture, compiler optimization, interpreter implementation, memory hierarchy, data distribution, and surrounding workload.

The C++ benchmark is compiled-code oriented, while the Python and JavaScript measurements occur inside managed runtime environments. Their raw timings should therefore not be interpreted as direct language-performance rankings.

## Common Implementation Errors

### Treating a partition index as universally equivalent

Lomuto partitioning returns a pivot's final position. Hoare partitioning returns a separation boundary. The recursive ranges must follow the specific partition contract.

### Choosing a bad pivot without considering input structure

Always selecting an endpoint is particularly problematic when input is already sorted or reverse sorted. The resulting recursion can become linear in depth and quadratic in total work.

### Forgetting the base case

A recursive call must eventually stop when its range has fewer than two elements. Incorrect boundaries can also cause the same range to be processed repeatedly.

### Mishandling equal values

Two-way partitioning remains correct with duplicates, but repeated equal values can create poor partition behavior. Three-way partitioning can reduce unnecessary recursion by grouping equal values.

### Assuming recursion is free

Recursive quick sort uses stack space. The expected stack requirement is much smaller than the worst case, but a production system should consider adversarial or unusually ordered inputs.

### Measuring only execution time

A single benchmark does not reveal why an algorithm behaved as it did. Comparisons, swaps, recursion depth, partition count, input distribution, and memory requirements provide more useful diagnostic information.

## Practical Design Choices

The examples use median-of-three and randomized pivot strategies to demonstrate how pivot selection can reduce exposure to simple ordered-input patterns.

The three-way implementation is appropriate when duplicates are common because values equal to the pivot can be removed from further recursive work.

The iterative implementation is appropriate when controlling call-stack growth is important.

Merge sort is a useful alternative when a predictable `O(n log n)` worst-case bound or stable ordering is more important than minimizing auxiliary storage.

For a production system, the choice should be based on measurable workload characteristics and explicit requirements rather than the algorithm name alone.

## Security and Robustness

Sorting is normally not considered a security boundary, but algorithmic worst cases can become a resource-exhaustion concern when an application sorts attacker-controlled or externally supplied data.

A service that blindly uses a naive endpoint-pivot quick sort can be exposed to deliberately structured input that causes excessive comparisons and deep recursion.

Relevant defensive techniques include:

- randomized or carefully selected pivots
- three-way partitioning for duplicate-heavy workloads
- explicit stack management
- recursion-depth monitoring
- introspective fallback strategies
- input-size limits where appropriate
- using a mature standard-library sorting implementation when custom behavior is unnecessary

The C++ case study validates the batch size before processing it. The Python and JavaScript implementations validate the expected data type for their demonstrations.

## Debugging Strategy

When a quick-sort implementation produces incorrect output, inspecting the entire algorithm at once can obscure the actual defect.

The most useful unit to inspect first is the partition function.

For a selected pivot, verify that:

- every element remains present after partitioning
- the partition boundary is within the expected range
- elements on each side satisfy the partition invariant
- recursive ranges are strictly smaller than the previous range
- equal values do not cause an endless loop
- empty and single-element ranges terminate immediately

The executable metrics in these implementations make unusually deep recursion or unexpectedly high comparison counts visible. Those measurements can reveal a poor pivot distribution even when the final sorted result is correct.

## Relationship Between the Implementations

The three implementations intentionally provide different perspectives.

The **Python implementation** emphasizes learning and algorithm instrumentation. It exposes several partition schemes and pivot strategies and uses randomized correctness checks.

The **JavaScript implementation** emphasizes runtime behavior. It demonstrates deterministic pseudo-random pivot selection, explicit-stack processing, and the relationship between synchronous computation and the event loop.

The **C++ implementation** treats quick sort as part of a typed data-processing system. The transaction case study connects sorting to ordered statistics and contrasts recursive and iterative implementations with merge sort.

The underlying algorithm remains the same: choose a pivot, partition the current range, and process the resulting subranges. The engineering concerns around that mechanism change with the implementation environment and workload.
