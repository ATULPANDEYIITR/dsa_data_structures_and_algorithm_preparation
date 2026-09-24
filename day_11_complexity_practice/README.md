# Day 11 — Complexity Practice

## Topic introduction

Algorithmic complexity is the practice of estimating how an algorithm's resource requirements grow as its input becomes larger.

The two main resources considered in this study are:

- **Time complexity**: how the amount of computation grows with input size.
- **Space complexity**: how much additional memory an algorithm requires as input size grows.

The objective of Day 11 is not simply to memorize `O(n)`, `O(n log n)`, or `O(n²)`. The practical objective is to look at an unfamiliar piece of code and estimate its approximate time and space complexity by examining loops, function calls, recursion, data structures, input reduction, and memory allocation.

The three implementations approach this subject from different perspectives:

- The **Python implementation** is a broad study file containing progressively difficult examples and explicit complexity analyses.
- The **JavaScript implementation** emphasizes executable algorithm patterns using arrays, `Map`, `Set`, recursion, dynamic structures, and runtime behavior.
- The **C++ implementation** presents an industry-style inventory analysis system in which different algorithms solve related requirements with different performance and memory trade-offs.

---

## Core terminology

### Input size

Complexity analysis needs a variable representing the size of the input.

For an array containing `n` elements, `n` is normally the input size.

For two independent collections, their sizes may need separate variables:

- first collection: `n`
- second collection: `m`

An algorithm that compares every element of the first collection with every element of the second has complexity `O(nm)`, not automatically `O(n²)`.

### Operation

An operation is a unit of work used to reason about an algorithm.

Examples include:

- comparing two values
- assigning a variable
- accessing an array element
- inserting into a data structure
- searching a collection
- performing arithmetic
- calling another function

The analysis usually focuses on the operation whose number of executions grows most significantly with the input.

### Asymptotic analysis

Asymptotic analysis describes growth as the input becomes large.

For example:

`5n + 20`

is classified as:

`O(n)`

The constant `5` and the constant `20` do not change the overall growth class.

Similarly:

`3n² + 10n + 50`

is classified as:

`O(n²)`

because the quadratic term eventually dominates the linear and constant terms.

---

## Big-O notation

Big-O notation is commonly used to express an upper asymptotic growth classification.

Common complexity classes include:

| Complexity | Common name | Typical example |
|---|---|---|
| `O(1)` | Constant | Array indexing |
| `O(log n)` | Logarithmic | Binary search |
| `O(n)` | Linear | Linear search |
| `O(n log n)` | Linearithmic | Merge sort |
| `O(n²)` | Quadratic | Pairwise comparison |
| `O(n³)` | Cubic | Triple nested loop |
| `O(2^n)` | Exponential | Naive recursive Fibonacci |
| `O(n!)` | Factorial | Exhaustive permutation generation |

The practical importance of these classes becomes clear as `n` increases.

An algorithm that performs approximately `n` operations and an algorithm that performs approximately `n²` operations may behave similarly for a very small input. Their behavior becomes substantially different as the input grows.

---

## Rules for simplifying complexity

### Ignore constant factors

If an algorithm performs `4n` operations, its asymptotic classification is:

`O(n)`

not `O(4n)`.

### Keep the dominant term

For:

`n² + n + 100`

the dominant term is `n²`.

Therefore:

`O(n²)`

### Sequential work is usually added

Suppose one loop requires `O(n)` and another independent loop also requires `O(n)`.

The total is:

`O(n) + O(n)`

which becomes:

`O(2n)`

and then:

`O(n)`

Two sequential linear loops therefore remain linear.

### Nested work is usually multiplied

If an outer loop runs `n` times and an inner loop runs `n` times for each outer iteration:

`n × n = n²`

Therefore:

`O(n²)`

The exact loop bounds must still be examined. Not every nested loop is automatically quadratic.

### Repeated division produces logarithmic complexity

Consider a value that repeatedly becomes half its previous value:

`n → n/2 → n/4 → n/8 → ...`

The number of reductions required to reach a constant is proportional to `log n`.

Therefore:

`O(log n)`

---

## Time complexity

Time complexity does not necessarily mean literal clock time.

It describes how the amount of algorithmic work grows.

For example, linear search may inspect:

- one element in its best case
- many elements in its average case
- all elements in its worst case

Therefore its worst-case complexity is `O(n)`.

The actual number of seconds depends on the programming language, hardware, compiler or interpreter, memory system, implementation details, and workload.

---

## Best-case, average-case, and worst-case complexity

Different inputs can cause the same algorithm to perform different amounts of work.

### Linear search

For:

`[10, 20, 30, 40, 50]`

searching for `10` succeeds immediately.

Best case:

`O(1)`

Searching for `50` requires inspecting every element.

Worst case:

`O(n)`

A missing value also requires inspecting every element.

Worst case:

`O(n)`

When a complexity statement is written without qualification, it is important to understand which case is being described.

---

## Space complexity

Space complexity measures memory requirements.

A useful distinction is between:

- input space
- output space
- auxiliary space

### Constant auxiliary space

An algorithm that uses only a fixed number of variables has:

`O(1)`

auxiliary space.

For example, an in-place reversal can use two indices and temporary storage for a swap.

### Linear auxiliary space

If an algorithm creates another collection containing up to `n` elements, its additional memory can be:

`O(n)`

A hash table used to store previously seen values is a common example.

### Output space

An algorithm that deliberately produces `n²` pairs may require `O(n²)` output storage if all pairs are retained.

The complexity of the output should not be confused with temporary memory used only to calculate the result.

---

## Python implementation

The Python script is structured as a standalone complexity study.

It begins with the basic complexity classes and then demonstrates concrete algorithms.

### Constant-time access

The function `get_first_element()` accesses the first list element directly.

The list can contain:

- 1 element
- 100 elements
- 1,000,000 elements

The operation still performs one direct access.

Therefore:

- Time: `O(1)`
- Auxiliary space: `O(1)`

---

## Linear search

The Python function `linear_search()` scans the collection from left to right.

For `n` elements, it may inspect all `n` elements.

Therefore:

- Best case: `O(1)`
- Worst case: `O(n)`
- Auxiliary space: `O(1)`

This demonstrates why the input arrangement can influence actual work even though the worst-case complexity remains linear.

---

## Binary search

Binary search is based on repeatedly reducing the search interval.

For a sorted collection:

`n`

becomes approximately:

`n/2`

then:

`n/4`

then:

`n/8`

and so on.

After approximately `log₂(n)` reductions, the remaining search space becomes constant-sized.

Therefore:

- Time: `O(log n)`
- Auxiliary space for the iterative implementation: `O(1)`

The sorting requirement is important. Binary search does not make an unsorted collection searchable in logarithmic time without first establishing the required ordering.

---

## One linear loop

The `sum_values()` function visits each element exactly once.

For `n` elements:

`n` iterations are performed.

Therefore:

- Time: `O(n)`
- Auxiliary space: `O(1)`

If every input value may affect the final sum, inspecting all values is necessary. There is no general asymptotic improvement to sublinear time for the basic problem when the complete unsummarized input is provided only at query time.

---

## Two sequential loops

The Python implementation includes a function that calculates both a sum and a maximum using two separate loops.

The work is approximately:

`n + n`

which is:

`2n`

and therefore:

`O(n)`

The two loops can sometimes be combined into one pass:

`n`

instead of:

`2n`

This can improve the constant factor while leaving the asymptotic classification unchanged.

This distinction is important:

- optimization of constants can improve practical speed
- optimization of asymptotic growth changes scalability

---

## Nested loops

The `all_pairs()` function contains two loops.

For `n` values:

- outer loop: `n`
- inner loop: `n`

Total:

`n × n = n²`

Therefore:

`O(n²)`

If every generated pair is stored, the result itself also requires quadratic output space.

---

## Triangular nested loops

The `unique_pairs()` implementation avoids generating both `(a, b)` and `(b, a)`.

Its number of operations is approximately:

`1 + 2 + 3 + ... + (n - 1)`

which is:

`n(n - 1) / 2`

The constant factor and lower-order term are removed during asymptotic simplification.

The result remains:

`O(n²)`

This illustrates why reducing duplicate work does not necessarily change the complexity class.

---

## Logarithmic loops

The `count_halvings()` function repeatedly divides a value by two.

For example:

`64 → 32 → 16 → 8 → 4 → 2 → 1`

There are six reductions.

The number of reductions grows logarithmically.

Therefore:

- Time: `O(log n)`
- Auxiliary space: `O(1)`

A similar pattern occurs when a binary search repeatedly eliminates half of the remaining possibilities.

---

## Merge sort

The Python implementation provides a complete merge sort.

Its basic process is:

1. Split the input into two halves.
2. Recursively sort each half.
3. Merge the two sorted halves.

The recurrence is:

`T(n) = 2T(n/2) + O(n)`

The two recursive calls account for the two halves.

The merge step examines the elements of the two halves.

The resulting complexity is:

`O(n log n)`

The implementation creates additional lists during merging, so its auxiliary memory is proportional to the input size.

---

## Hash-based two-sum

The hash-based `two_sum_hash()` function stores previously seen values.

For each value `x`, it searches for:

`target - x`

A hash table normally provides average constant-time membership lookup.

The algorithm therefore performs one main pass:

- Time: `O(n)` average
- Space: `O(n)`

This is a classic example of exchanging memory for computation.

The algorithm uses more memory than a constant-space brute-force solution, but it can reduce time from quadratic to linear average-case behavior.

---

## Two-pointer two-sum

The two-pointer version assumes sorted input.

One pointer starts at the beginning and another at the end.

If the sum is too small, the left pointer moves right.

If the sum is too large, the right pointer moves left.

Each pointer moves only toward the other pointer.

Therefore:

- Time: `O(n)`
- Auxiliary space: `O(1)`

The important trade-off is that sorting may itself cost `O(n log n)` if the input is not already sorted.

For repeated searches, maintaining sorted data can make the approach attractive.

---

## Duplicate detection

Two approaches are demonstrated.

### Hash-set approach

A set stores values already encountered.

Average complexity:

- Time: `O(n)`
- Space: `O(n)`

### Sorting approach

The values are sorted and adjacent values are compared.

Typical sorting complexity:

`O(n log n)`

The subsequent scan is:

`O(n)`

The total remains:

`O(n log n)`

The two approaches demonstrate a common algorithmic trade-off:

- hashing uses additional memory and usually provides faster lookup
- sorting uses ordering and may provide useful structure for additional operations

---

## Recursive factorial

The recursive factorial implementation performs one recursive call for each decrement.

For:

`n! = n × (n - 1)!`

the recursion depth is `n`.

Therefore:

- Time: `O(n)`
- Recursion-stack space: `O(n)`

The iterative implementation performs the same amount of asymptotic work but does not require a growing recursion stack.

Therefore:

- Time: `O(n)`
- Auxiliary space: `O(1)`

This demonstrates that two algorithms can have identical time complexity while having different space complexity.

---

## Fibonacci and repeated subproblems

Naive recursive Fibonacci is a classic complexity problem.

The recurrence is approximately:

`T(n) = T(n - 1) + T(n - 2) + O(1)`

The recursion repeatedly calculates the same values.

For example, computing `F(5)` requires several independent calculations of smaller Fibonacci numbers that overlap heavily.

The simple implementation has exponential growth and is commonly described in introductory analysis as:

`O(2^n)`

The recursion stack itself grows to:

`O(n)`

### Memoization

Memoization stores previously calculated results.

Each Fibonacci value can then be calculated once.

The resulting complexity becomes:

- Time: `O(n)`
- Space: `O(n)`

### Iterative dynamic programming

The Python implementation also contains an iterative version that keeps only the two most recent values.

Therefore:

- Time: `O(n)`
- Auxiliary space: `O(1)`

This is a major example of algorithmic optimization through removal of repeated work.

---

## Cubic complexity

The `count_equal_triples()` function examines every combination of three positions.

The structure contains three nested loops.

The work grows approximately with:

`n³`

Therefore:

`O(n³)`

Cubic algorithms become impractical much faster than linear or quadratic algorithms as input size increases.

---

## Amortized complexity

Some operations occasionally perform significantly more work but are still efficient when averaged across a long sequence of operations.

Dynamic arrays are a standard example.

An append operation is commonly classified as amortized:

`O(1)`

An individual resize can require:

`O(n)`

work because elements may need to be moved.

The important distinction is:

- individual worst-case append: can be `O(n)`
- amortized append: `O(1)`
- `n` appends overall: `O(n)`

Amortized analysis is therefore different from simply examining the most expensive individual operation.

---

# JavaScript implementation

The JavaScript implementation provides the same complexity reasoning in a runtime where arrays, `Map`, `Set`, recursion, dynamic allocation, and object-oriented patterns are common.

## Arrays

Direct array indexing is normally treated as:

`O(1)`

A linear search is:

`O(n)`

because the desired element may occur at the end or may not exist.

JavaScript arrays are dynamically sized. Operations such as `push()` are generally treated as amortized `O(1)`, although an individual resize can require more work.

---

## Map and Set

JavaScript `Map` and `Set` provide useful average-case lookup behavior.

Typical practical classifications are:

- `Map` lookup: average `O(1)`
- `Map` insertion: average `O(1)`
- `Set` membership: average `O(1)`
- `Set` insertion: average `O(1)`

These are average-case classifications rather than a claim that every possible operation is mathematically guaranteed to take constant time under every implementation condition.

The JavaScript implementation uses these structures for:

- two-sum
- duplicate detection
- frequency counting
- optimization of repeated searches

---

## Function-call complexity

One of the most important Day 11 skills is analyzing functions called inside loops.

Consider:

`n` iterations of a loop

where each iteration performs:

`O(n)`

work.

The combined complexity becomes:

`O(n²)`

The JavaScript function `expensivePattern()` demonstrates this pattern by repeatedly calling a linear search.

The optimized version builds a `Set` once.

Construction takes average:

`O(n)`

and subsequent membership checks take average:

`O(1)`

per element.

The resulting overall average complexity becomes:

`O(n)`

This demonstrates why the implementation details of a function call cannot be ignored during complexity analysis.

---

## Output-sensitive complexity

The JavaScript implementation includes a function that generates every triple.

The number of generated triples grows approximately as:

`n³`

If all triples are stored, the output itself has cubic size.

This leads to an important principle:

An algorithm cannot produce `n³` distinct output items in less than `Ω(n³)` time simply because writing those outputs already requires that much work.

This is one reason output complexity should be considered separately from auxiliary memory.

---

# C++ industry-style case study

## Problem being modeled

The C++ program models a small product inventory system.

Each product contains:

- product ID
- product name
- price
- stock quantity

The system supports operations such as:

- calculating inventory value
- finding low-stock products
- finding products by ID
- sorting products
- performing binary search
- building a hash-based product index
- finding product pairs
- handling invalid input
- benchmarking different algorithmic approaches

This is intentionally more realistic than isolated syntax demonstrations because the same business requirement can often be implemented using several algorithms with different performance characteristics.

---

## Product lookup with linear search

The first lookup method scans the product vector.

For `n` products:

- best case: `O(1)`
- worst case: `O(n)`
- auxiliary space: `O(1)`

This approach is simple and does not require additional indexing structures.

It can be reasonable when:

- the collection is small
- searches are infrequent
- preserving simple implementation is important
- additional memory is undesirable

Its main limitation is repeated search over large collections.

---

## Sorting plus binary search

The program creates a copy of the product list and sorts it by ID.

Sorting costs approximately:

`O(n log n)`

After sorting, each binary search costs:

`O(log n)`

This creates a preprocessing trade-off.

For one lookup, sorting may not be justified.

For many repeated lookups, preprocessing can become useful because the sorted structure can be reused.

The analysis must therefore include both:

- preprocessing cost
- query cost

It is incorrect to state only `O(log n)` without acknowledging that sorting an initially unsorted collection was necessary.

---

## Hash-based product index

The `ProductIndex` class builds:

`product ID → vector position`

using an `unordered_map`.

Construction is approximately:

`O(n)` average

Each lookup is:

`O(1)` average

The trade-off is memory.

The index requires:

`O(n)`

additional space.

This is an example of a common production design decision:

> Spend memory and preprocessing time to reduce repeated query time.

The correct choice depends on workload characteristics.

---

## Inventory value calculation

The total inventory value is calculated as:

`sum(price × stock)`

Every product contributes to the result.

Therefore:

- Time: `O(n)`
- Auxiliary space: `O(1)`

No asymptotically faster algorithm can generally determine the exact sum without examining all relevant values.

---

## Low-stock search

The low-stock query scans every product and returns the records whose stock is at or below a threshold.

Its computational cost is:

`O(n)`

The result may contain `k` products.

Therefore its output space is:

`O(k)`

and in the worst case:

`O(n)`

This illustrates why space analysis should distinguish between the amount of temporary working memory and the size of the required result.

---

## Brute-force pair matching

The C++ case study includes a pair-search operation that checks every unique pair.

The number of pairs is:

`n(n - 1) / 2`

This simplifies to:

`O(n²)`

The implementation stores only a counter, so its auxiliary space is:

`O(1)`

The algorithm is simple but does not scale well when the collection becomes large.

---

## Hash-based pair matching

The optimized pair-search implementation converts prices to integer cents and stores previously seen values in a hash map.

The integer conversion is important because exact equality comparisons of floating-point monetary values can be problematic.

For each price, the algorithm calculates the required complement:

`target - current`

Average complexity:

- Time: `O(n)`
- Space: `O(n)`

This changes the computational growth from quadratic to linear average-case behavior at the cost of additional memory.

---

# Complexity comparisons

| Problem | Approach | Time | Auxiliary Space |
|---|---|---:|---:|
| First element | Direct indexing | `O(1)` | `O(1)` |
| Linear search | Sequential scan | `O(n)` | `O(1)` |
| Binary search | Halving sorted range | `O(log n)` | `O(1)` |
| Sum | Single pass | `O(n)` | `O(1)` |
| All pairs | Nested loops | `O(n²)` | `O(1)` if not stored |
| Merge sort | Divide and merge | `O(n log n)` | `O(n)` in these implementations |
| Hash two-sum | Hash lookup | `O(n)` average | `O(n)` |
| Two-pointer two-sum | Sorted scan | `O(n)` after sorting | `O(1)` |
| Naive Fibonacci | Repeated recursion | Exponential | `O(n)` stack |
| Memoized Fibonacci | Stored subproblems | `O(n)` | `O(n)` |
| Iterative Fibonacci | Rolling state | `O(n)` | `O(1)` |
| Triple enumeration | Three nested loops | `O(n³)` | Output-dependent |

---

# Sequential versus nested loops

Consider two loops:

`for each element: process it`

followed by another:

`for each element: process it`

The total is:

`O(n) + O(n) = O(n)`

Now consider:

`for each element`
`    for each element`

The inner work occurs for every outer iteration:

`O(n × n) = O(n²)`

This distinction is fundamental when reading unfamiliar code.

---

# Triangular loops

A loop whose inner boundary depends on the outer index often produces a triangular number of operations.

For example:

`for i = 0 to n`
`    for j = i + 1 to n`

The total work is approximately:

`n(n - 1) / 2`

Although this is approximately half of a full `n²` grid, its asymptotic classification remains:

`O(n²)`

Reducing a constant factor does not change the Big-O class.

---

# Logarithmic behavior

A loop that repeatedly multiplies or divides by a constant often has logarithmic complexity.

Examples include:

`value *= 2`

and:

`value /= 2`

The exact base of the logarithm generally does not matter for Big-O classification because logarithms with different constant bases differ only by a constant factor.

Therefore:

`O(log₂ n)`

and:

`O(log₁₀ n)`

are both written as:

`O(log n)`

---

# Recursive complexity

Recursive algorithms require more careful analysis than simple loops.

Three questions are particularly useful:

1. How many recursive calls are made?
2. How much work occurs during each call?
3. How deep can the recursion become?

For recursive factorial:

`T(n) = T(n - 1) + O(1)`

which gives:

`O(n)`

For naive Fibonacci, two recursive calls are made repeatedly, producing exponential growth.

For divide-and-conquer algorithms such as merge sort:

`T(n) = 2T(n/2) + O(n)`

which results in:

`O(n log n)`

---

# Recursion stack space

A recursive algorithm can consume memory even if it does not explicitly allocate a collection.

For factorial:

`factorial(n)`
→ `factorial(n - 1)`
→ `factorial(n - 2)`
→ ...

There can be `n` active stack frames.

Therefore the auxiliary space is:

`O(n)`

An iterative implementation can often eliminate that recursion-stack growth.

This does not mean iteration is always superior. Recursion can provide clearer representations for tree algorithms, divide-and-conquer algorithms, graph traversal, and other naturally recursive structures.

The important point is to account for the stack when analyzing space.

---

# Average-case hashing

Hash tables are frequently described as providing average `O(1)` lookup.

This is useful for practical analysis, but the statement must be interpreted correctly.

Hash-table performance can depend on:

- hash function quality
- key distribution
- collision behavior
- table resizing
- implementation details
- workload characteristics

Therefore a precise analysis should state:

`O(1) average`

rather than treating the behavior as universally guaranteed under every circumstance.

---

# Amortized analysis

Amortized complexity examines the average cost across a sequence of operations.

Dynamic arrays illustrate the concept.

Most append operations may require constant work.

Occasionally the underlying storage must be expanded and elements moved.

That individual operation can be expensive, but the expensive resizing events are sufficiently infrequent that the average cost per append over a long sequence is commonly classified as:

`O(1)` amortized

This is different from saying that every individual append is always `O(1)` in the strict worst-case sense.

---

# Preprocessing trade-offs

Suppose an unsorted collection must answer many searches.

A direct linear search has approximately:

`O(n)`

per search.

If the collection is sorted first:

`O(n log n)`

preprocessing is required.

Each later binary search is:

`O(log n)`

If there are `q` searches, the approximate total becomes:

`O(n log n + q log n)`

The best design depends on:

- number of queries
- frequency of updates
- memory constraints
- whether the collection remains stable
- whether ordering is useful for other operations

Complexity analysis therefore supports design decisions rather than merely assigning labels to algorithms.

---

# Space-time trade-offs

An important recurring pattern is:

> More memory can sometimes reduce computation.

Examples include:

- hash tables
- memoization
- lookup indexes
- caching
- frequency tables
- precomputed values

The reverse can also occur:

> Less memory can sometimes require more computation.

Examples include:

- repeatedly scanning an array instead of building an index
- recomputing recursive subproblems instead of memoizing them
- processing data in multiple passes instead of storing intermediate results

Neither direction is universally correct. The appropriate choice depends on the constraints of the system.

---

# Common mistakes

## Mistake 1: Calling two sequential loops quadratic

This:

`O(n) + O(n)`

is:

`O(n)`

not:

`O(n²)`.

## Mistake 2: Calling every nested loop quadratic

A nested loop may have a logarithmic inner loop, a shrinking range, or independent bounds.

The exact iteration behavior must be examined.

## Mistake 3: Ignoring function calls

If a loop runs `n` times and calls an `O(n)` function every time, the total may be:

`O(n²)`

## Mistake 4: Ignoring data-structure operations

A line such as membership testing may not be `O(1)` for every data structure.

For example:

- array membership: typically `O(n)`
- hash-set membership: average `O(1)`
- binary search on sorted data: `O(log n)`

## Mistake 5: Ignoring recursion depth

A recursive function may use significant stack memory even when no explicit collection is allocated.

## Mistake 6: Forgetting preprocessing

If sorting is required before binary search, the sorting cost belongs in the complete algorithm analysis.

## Mistake 7: Treating benchmarking as complexity analysis

A benchmark tells you how one implementation performed on one machine for one input.

It does not by itself establish asymptotic growth.

## Mistake 8: Ignoring output size

If an algorithm must produce `n²` separate results, the output itself requires quadratic work and potentially quadratic storage.

## Mistake 9: Treating average-case hashing as an unconditional guarantee

Hash-table complexity depends on implementation and assumptions.

## Mistake 10: Optimizing constants before growth rate

Changing:

`5n`

to:

`2n`

may improve performance.

Changing:

`n²`

to:

`n`

can have a much larger effect as the input grows.

---

# Edge cases

Complexity analysis should be accompanied by correctness analysis.

The implementations explicitly consider cases such as:

- empty collections
- one-element collections
- missing search values
- duplicate values
- already sorted input
- reverse-sorted input
- invalid negative values
- invalid thresholds
- empty search results
- repeated values
- small recursion inputs

An algorithm should remain correct when the input is small, empty, duplicated, ordered differently, or invalid according to the defined input contract.

---

# Performance considerations

Asymptotic complexity is essential but does not explain every performance difference.

Actual performance can depend on:

- CPU speed
- cache locality
- memory bandwidth
- allocation behavior
- compiler optimizations
- interpreter overhead
- runtime implementation
- hash-table behavior
- branch prediction
- object representation
- input distribution
- garbage collection in managed runtimes

This is why the three implementations also include small benchmarking examples.

The benchmarks are demonstrations rather than proofs.

A measured result such as:

`2 ms`

does not mean an algorithm is inherently `O(2)`.

Complexity is about growth behavior.

---

# C++ performance considerations

C++ allows detailed control over data representation and memory.

The case study uses:

- `vector` for contiguous collections
- `unordered_map` for average constant-time lookup
- `unordered_set` for duplicate detection
- sorting algorithms from the standard library
- references to avoid unnecessary copying where appropriate
- a deliberate copy when demonstrating preprocessing

The difference between passing:

`vector<Product>`

and:

`const vector<Product>&`

is also relevant.

Passing a vector by value can create a copy proportional to the number of elements.

Passing by constant reference avoids that copy when mutation is not required.

The C++ case study uses these distinctions intentionally.

---

# JavaScript runtime considerations

JavaScript arrays and collections are managed by the runtime.

The language provides:

- `Array`
- `Map`
- `Set`

which make many common algorithmic patterns convenient.

The same asymptotic principles still apply.

For example:

A linear search through an array remains `O(n)`.

A `Set` membership operation is normally analyzed as average `O(1)`.

Creating a new array of `n` values still requires `O(n)` memory.

The fact that the runtime manages memory automatically does not remove space complexity.

---

# Python implementation considerations

Python provides high-level data structures such as:

- lists
- sets
- dictionaries

These make algorithm development concise.

The underlying complexity still matters.

For example:

- list indexing is typically `O(1)`
- list search is `O(n)`
- set membership is average `O(1)`
- dictionary lookup is average `O(1)`
- sorting is typically `O(n log n)`

The Python implementation uses these operations explicitly so that their algorithmic consequences can be observed.

---

# Security considerations

Complexity can become a security concern when an attacker controls input size or structure.

Potential problems include:

- algorithms with quadratic or worse growth receiving very large input
- excessive recursion depth
- memory exhaustion
- inefficient repeated searches
- uncontrolled output generation
- pathological data structures
- resource-exhaustion attacks

A production system should consider limits on:

- input size
- recursion depth
- number of requested operations
- output size
- memory consumption
- execution time

Complexity analysis therefore has relevance beyond academic exercises.

---

# Production considerations

Before choosing an algorithm for a production system, consider:

### Input scale

An `O(n²)` algorithm may be perfectly acceptable for `n = 20` and unacceptable for `n = 1,000,000`.

### Query frequency

An index may not be worth building for a single query but may be valuable for millions of repeated queries.

### Update frequency

Maintaining a sorted or indexed structure introduces update costs.

### Memory limits

A linear-memory optimization may not be appropriate when memory is constrained.

### Output requirements

If the output itself is large, the algorithm cannot eliminate the cost of producing it.

### Correctness requirements

An optimization is useful only if it preserves the required behavior.

### Implementation complexity

A theoretically faster algorithm can introduce maintenance and correctness risks.

### Measurement

After complexity analysis identifies an appropriate algorithmic approach, benchmarking can help identify implementation-level bottlenecks.

---

# A practical method for unfamiliar code

When presented with code you have never seen before, use the following sequence.

## Identify the input

Ask:

`What grows?`

It may be:

- number of array elements
- number of nodes
- number of records
- number of characters
- number of queries
- number of graph edges

Give that quantity a symbol such as `n`.

## Find loops

For each loop, determine:

- starting point
- ending point
- increment
- whether the bound depends on another loop
- whether the variable doubles or halves

## Inspect nesting

Sequential loops generally add.

Nested loops generally multiply.

Do not stop at counting the visible loops. Determine how many total iterations actually occur.

## Inspect called functions

If a loop calls another function, analyze that function.

For example:

`n × O(n) = O(n²)`

## Inspect recursion

Determine:

- number of recursive calls
- problem-size reduction
- work per call
- recursion depth
- repeated subproblems

## Inspect data structures

Ask what each operation costs.

For example:

- array search
- hash lookup
- tree search
- sorting
- insertion
- deletion

## Inspect memory

Look for:

- copied arrays
- sets
- maps
- matrices
- queues
- stacks
- recursion frames
- generated output

## Simplify

Remove constants and lower-order terms.

For example:

`4n² + 8n + 20`

becomes:

`O(n²)`

---

# Day 11 analysis format

For every previously solved problem, use the following four-part structure.

## Approach

Describe the algorithm in plain technical language.

Example:

`Scan the array once while maintaining the largest value encountered so far.`

## Time Complexity

State the asymptotic running time and the relevant case.

Example:

`O(n)`

or:

`O(n) average, O(n²) worst case`

when the distinction is necessary.

## Space Complexity

State auxiliary memory separately when appropriate.

Example:

`O(1) auxiliary space`

or:

`O(n) auxiliary space for the hash table`

## Possible Optimization

State whether a meaningful optimization exists.

An optimization can involve:

- changing the algorithm
- choosing a different data structure
- avoiding repeated work
- using preprocessing
- reducing memory
- reducing constant factors
- changing recursion to iteration
- using sorted data
- using memoization

The optimization should not be described merely as "make it faster." It should identify the specific mechanism that changes the resource usage.

---

# Worked Day 11 examples

## Find maximum

**Approach:** Scan every element and maintain the largest value encountered.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)` auxiliary space.

**Possible Optimization:** No general asymptotic improvement is possible because any element could contain the maximum.

---

## Reverse an array

**Approach:** Use two pointers, one at each end, and swap values while moving inward.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)` auxiliary space.

**Possible Optimization:** The two-pointer in-place approach already provides linear time and constant auxiliary space.

---

## Binary search

**Approach:** Repeatedly compare the target with the middle element and discard half of the remaining search interval.

**Time Complexity:** `O(log n)`

**Space Complexity:** `O(1)` for the iterative implementation.

**Possible Optimization:** The asymptotic search complexity is already logarithmic. Maintaining sorted data efficiently is the primary structural consideration.

---

## Two-sum with a hash table

**Approach:** Store values already seen and search for the complement required to reach the target.

**Time Complexity:** `O(n)` average.

**Space Complexity:** `O(n)`.

**Possible Optimization:** Use a two-pointer method when sorted input is available and constant auxiliary space is preferred.

---

## Merge sort

**Approach:** Divide the collection into halves, recursively sort each half, and merge the sorted halves.

**Time Complexity:** `O(n log n)`.

**Space Complexity:** `O(n)` auxiliary space for the implementations used here.

**Possible Optimization:** Alternative sorting strategies can change memory requirements and practical performance while retaining the same or similar asymptotic time.

---

# Phase checkpoint

The required Day 11 checkpoint is:

> You should be able to look at an unfamiliar piece of code and estimate its approximate time and space complexity.

A practical checkpoint is to inspect code and answer these questions without executing it:

1. What is the input size?
2. Which operation dominates the work?
3. How many times does the operation execute?
4. Are loops sequential or nested?
5. Does the loop variable grow or shrink exponentially?
6. Is an `O(n)` function being called inside another `O(n)` loop?
7. Is sorting performed before another operation?
8. Is a hash table or set changing the lookup complexity?
9. Does recursion create repeated subproblems?
10. How deep can the recursion become?
11. How much additional memory is allocated?
12. Is the complexity worst-case, best-case, average-case, or amortized?
13. Is the result itself large?
14. Can preprocessing reduce repeated query cost?
15. Is the proposed optimization changing asymptotic growth or only reducing constants?

A useful progression is to recognize these patterns quickly:

`O(1)` → direct fixed work

`O(log n)` → repeatedly reduce the problem by a constant factor

`O(n)` → one complete pass

`O(n log n)` → divide-and-conquer with linear work per level

`O(n²)` → pairwise or two-dimensional work

`O(n³)` → triple combinations or three nested dimensions

`O(2^n)` → repeated branching over subproblems

`O(n!)` → exhaustive permutation-style growth

The essential Day 11 skill is the ability to derive these classifications from the structure of unfamiliar code rather than relying only on memorized examples.
