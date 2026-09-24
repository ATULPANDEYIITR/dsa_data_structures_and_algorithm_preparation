# Day 7 — Time complexity

## Topic overview

Time complexity is a method for describing how the amount of computational work performed by an algorithm grows as the size of its input grows.

The input size is commonly represented by `n`.

For example, an algorithm that examines every item in a list once performs work that grows approximately in proportion to `n`. Its time complexity is `O(n)`.

An algorithm that compares every item with every other item can perform approximately `n × n` operations. Its time complexity is `O(n²)`.

Time complexity is primarily concerned with growth rather than the exact number of seconds required by one execution on one computer.

The main complexity classes studied in this implementation are:

| Complexity | Common name | Typical growth pattern |
|---|---|---|
| `O(1)` | Constant | Work remains approximately fixed |
| `O(log n)` | Logarithmic | Work grows very slowly |
| `O(n)` | Linear | Work grows proportionally with input size |
| `O(n log n)` | Linearithmic | Linear work across logarithmic levels |
| `O(n²)` | Quadratic | Work grows approximately with the square of input size |
| `O(n³)` | Cubic | Work grows approximately with the cube of input size |

The three implementations approach the subject from different perspectives. Python emphasizes direct algorithmic experimentation, JavaScript demonstrates the same principles in an application-oriented language, and C++ develops a more substantial transaction-processing case study.

---

## Running time

Running time means the amount of computational work required by an algorithm for a particular input.

In actual execution, runtime can be measured in seconds or milliseconds. It is affected by many factors:

- processor speed
- memory hierarchy
- cache behavior
- compiler optimization
- interpreter overhead
- operating-system scheduling
- programming-language implementation
- input values
- memory allocation
- hardware architecture

For algorithm analysis, exact elapsed time is usually less useful than understanding how work grows as the input becomes larger.

Suppose an algorithm performs:

`5n + 20`

operations.

When `n` is small, both terms may matter. As `n` becomes large, the `5n` term dominates the fixed `20`.

For asymptotic analysis:

`5n + 20 = O(n)`

The constant `5` and the lower-order constant `20` do not change the growth class.

Similarly:

`3n² + 7n + 10 = O(n²)`

The quadratic term eventually dominates the linear and constant terms.

---

## What does `n` mean?

`n` represents the size of the relevant input.

The meaning of `n` depends on the problem.

For an array, `n` can mean the number of elements.

For a string, `n` can mean the number of characters.

For a graph, several size measures may matter, such as:

- `V` = number of vertices
- `E` = number of edges

For a matrix, complexity may depend on both the number of rows and columns.

For a database operation, the relevant size might be:

- number of records
- number of indexed records
- number of records returned
- number of distinct keys

It is therefore important to define what is growing before analyzing an algorithm.

---

## Constant operations: `O(1)`

An operation is considered constant time when the amount of work does not grow with the input size.

A typical example is direct indexing into a random-access array.

The Python implementation demonstrates this with `constant_operation()`.

The JavaScript implementation demonstrates direct array access through `constantOperation()`.

The C++ implementation uses `vector` indexing in `getTransactionAt()`.

Conceptually:

`array[index]`

does not require scanning all previous elements.

If an array contains 10 elements or 10 million elements, retrieving an element at a known index is normally treated as `O(1)`.

Constant time does not necessarily mean one processor instruction.

`O(1)` means the amount of work is bounded by a constant independent of `n`.

An operation could internally require several machine instructions and still be `O(1)` if that number does not grow with the input size.

---

## Linear operations: `O(n)`

An algorithm is linear when its work grows proportionally with the number of input elements.

A typical pattern is:

`for each element in the input: perform constant work`

If there are:

- 10 elements, approximately 10 iterations occur
- 1,000 elements, approximately 1,000 iterations occur
- 1,000,000 elements, approximately 1,000,000 iterations occur

The complexity is:

`O(n)`

The Python function `linear_sum()` visits every element exactly once.

The JavaScript function `linearSum()` does the same.

The C++ transaction case study uses linear processing for operations such as:

- calculating the total value of completed transactions
- counting completed transactions
- scanning transactions by ID

A linear algorithm can still be expensive for very large inputs, but its growth is much slower than quadratic or cubic growth.

---

## Nested loops

Nested loops require careful analysis.

Consider two loops where both depend on `n`.

The outer loop runs `n` times.

For each outer iteration, the inner loop runs `n` times.

The total work is:

`n × n = n²`

Therefore:

`O(n²)`

The Python function `nested_pair_count()` demonstrates this directly.

The JavaScript function `quadraticPairCount()` uses the same pattern.

The C++ case study uses a quadratic pairwise transaction comparison in `findAccountPairsQuadratic()`.

Quadratic algorithms are often practical for small datasets but can become expensive as the dataset grows.

For example:

| `n` | `n` | `n²` |
|---:|---:|---:|
| 10 | 10 | 100 |
| 100 | 100 | 10,000 |
| 1,000 | 1,000 | 1,000,000 |
| 10,000 | 10,000 | 100,000,000 |
| 100,000 | 100,000 | 10,000,000,000 |

This is why nested loops should not automatically be treated as harmless merely because each individual operation is simple.

---

## Dependent nested loops

Not every nested loop has exactly `n²` iterations, but many still belong to the `O(n²)` class.

Consider a pattern where the inner loop runs:

`n + (n - 1) + (n - 2) + ... + 1`

The total is:

`n(n + 1) / 2`

Expanding:

`(n² + n) / 2`

The constant factor and lower-order term are ignored for asymptotic classification:

`O(n²)`

The Python and JavaScript implementations include triangular pair-count examples to demonstrate this distinction.

The fact that the inner loop gets shorter does not automatically make the algorithm linear.

---

## Three nested loops: `O(n³)`

Three independent loops that each execute approximately `n` times produce:

`n × n × n = n³`

Therefore:

`O(n³)`

The Python function `cubic_operation()` demonstrates this.

The JavaScript function `cubicOperation()` demonstrates the same growth.

The C++ function `cubicRiskScan()` models a three-dimensional analytical scan.

Cubic growth becomes impractical much faster than linear or quadratic growth.

For example:

| `n` | `n²` | `n³` |
|---:|---:|---:|
| 10 | 100 | 1,000 |
| 100 | 10,000 | 1,000,000 |
| 1,000 | 1,000,000 | 1,000,000,000 |
| 10,000 | 100,000,000 | 1,000,000,000,000 |

This is why algorithms with three independently growing dimensions require careful input-size constraints.

---

## Sequential operations

A common beginner mistake is to multiply the complexities of all loops simply because they appear in the same function.

Consider two sequential loops:

- first loop: `O(n)`
- second loop: `O(n)`

The total is:

`O(n) + O(n)`

which becomes:

`O(2n)`

and therefore:

`O(n)`

Sequential operations are added, not multiplied.

The Python function `sequential_linear_work()`, JavaScript function `sequentialLinearWork()`, and C++ function `sequentialLinearWork()` demonstrate this principle.

Now consider:

- first operation: `O(n)`
- second operation: `O(n²)`

The total is:

`O(n) + O(n²)`

The quadratic term dominates for large `n`.

Therefore:

`O(n²)`

The implementations demonstrate this with `linearThenQuadratic()`.

---

## Dominant terms

When combining complexity terms, the fastest-growing term normally determines the asymptotic classification.

Examples:

`O(n + 10) = O(n)`

`O(3n + 100) = O(n)`

`O(n² + n) = O(n²)`

`O(n³ + n² + n) = O(n³)`

`O(n log n + n) = O(n log n)`

The Python and JavaScript operation-count examples use:

`3n² + 7n + 10`

The final classification is:

`O(n²)`

This does not mean that the `3`, `7`, and `10` are meaningless during actual execution. They can matter significantly for real performance. They are ignored only when identifying the asymptotic growth class.

---

## Logarithmic complexity: `O(log n)`

Logarithmic algorithms repeatedly reduce the remaining problem by a constant factor.

The most common beginner example is halving.

Suppose:

`n = 64`

Repeated halving produces:

`64 → 32 → 16 → 8 → 4 → 2 → 1`

Only six divisions are required.

For a much larger input, the number of divisions increases slowly.

This gives:

`O(log n)`

The base of the logarithm does not affect Big O classification when the base is a fixed constant.

Therefore:

`O(log₂ n)`

and

`O(log₁₀ n)`

belong to the same asymptotic class.

The actual numerical values differ, but the difference between logarithm bases is a constant factor.

---

## Halving loops

A typical logarithmic loop is:

`while n > 1: n = n / 2`

The Python function `halving_steps()` implements this behavior.

The JavaScript function `halvingSteps()` demonstrates it.

The C++ function `halvingSteps()` demonstrates the same principle.

If `n` doubles, the number of iterations increases by approximately one.

That is the defining scaling behavior of logarithmic growth.

---

## Doubling loops

A loop can also be logarithmic when a control value repeatedly doubles.

The pattern is:

`1 → 2 → 4 → 8 → 16 → ...`

If the target is `n`, the number of doublings required is approximately:

`log₂ n`

The implementations include:

- Python `doubling_steps()`
- JavaScript `doublingSteps()`
- C++ `doublingSteps()`

A common mistake is to see multiplication inside a loop and classify it as `O(n)`. The correct analysis depends on how many times the multiplication occurs.

A loop that changes:

`value = value + 1`

until `value` reaches `n` is generally `O(n)`.

A loop that changes:

`value = value * 2`

until `value` reaches `n` is generally `O(log n)`.

---

## Binary search: `O(log n)`

Binary search works on sorted data.

Suppose a sorted collection contains:

`[10, 20, 30, 40, 50, 60, 70]`

Instead of checking every value from the beginning, binary search examines the middle.

If the target is larger than the middle value, the entire lower half can be discarded.

If the target is smaller, the upper half can be discarded.

The search space therefore shrinks approximately by half after each comparison.

The complexity is:

`O(log n)`

The iterative implementations use:

- Python `binary_search()`
- JavaScript `binarySearch()`
- C++ `binarySearchById()`

The recursive versions are:

- Python `recursive_binary_search()`
- JavaScript `recursiveBinarySearch()`

The C++ case study uses the iterative version because it avoids recursive call-stack growth.

### Binary search requirements

Binary search is not a replacement for linear search in every situation.

The data must be ordered according to the search key.

If the data is unsorted, binary search cannot safely eliminate half of the remaining elements.

This creates an important engineering trade-off:

- sorting may cost `O(n log n)`
- repeated searches can then benefit from `O(log n)` search
- a one-time search on unsorted data may be simpler with `O(n)` linear search

The correct choice depends on the workload.

---

## Linear search: `O(n)`

Linear search examines elements sequentially until the target is found or the collection ends.

The implementations use:

- Python `linear_search()`
- JavaScript `linearSearch()`
- C++ `linearSearchById()`

Its cases can differ:

### Best case

The target is the first element.

Complexity:

`O(1)`

### Worst case

The target is the final element or is absent.

Complexity:

`O(n)`

### Average case

For a typical uniformly distributed successful search, a substantial fraction of the collection may be inspected.

The asymptotic classification is:

`O(n)`

When discussing the complexity of an algorithm generally, worst-case complexity is often reported because it provides a useful upper bound on growth.

---

## `O(n log n)`

`O(n log n)` commonly appears in efficient comparison-based sorting algorithms.

Merge sort is the principal example used in all three implementations.

The basic process is:

1. Divide the input into smaller pieces.
2. Recursively sort the pieces.
3. Merge the sorted pieces.

The input is repeatedly divided in half.

The number of division levels is approximately:

`log₂ n`

At each level, the total amount of merging work is approximately:

`n`

Therefore:

`n × log n`

which gives:

`O(n log n)`

---

## Merge sort

The Python implementation provides `merge()` and `merge_sort()`.

The JavaScript implementation provides `merge()` and `mergeSort()`.

The C++ implementation provides:

- `mergeRanges()`
- `mergeSortRecursive()`
- `mergeSortById()`

The C++ version sorts transactions according to transaction ID.

This creates a realistic reason for sorting: once transactions are ordered by ID, binary search can be used.

### Merge sort time complexity

Best case:

`O(n log n)`

Average case:

`O(n log n)`

Worst case:

`O(n log n)`

### Merge sort auxiliary space

The implementations use additional storage for merging.

The auxiliary space is approximately:

`O(n)`

This illustrates an important point:

An algorithm can have good time complexity while consuming additional memory.

---

## Recursion and time complexity

Recursion occurs when a function calls itself.

Recursion does not automatically mean an algorithm is slow.

The complexity depends on:

- how many recursive calls are created
- how much work occurs per call
- how quickly the input becomes smaller
- the number of recursive levels
- whether subproblems overlap

A simple countdown:

`T(n) = T(n - 1) + O(1)`

has:

`O(n)`

time complexity.

The Python function `recursive_countdown()`, JavaScript function `recursiveCountdown()`, and C++ function `recursiveCountdown()` demonstrate this pattern.

The recursive call stack also requires memory.

Therefore, although the time complexity is `O(n)`, auxiliary space is also `O(n)` for the recursion stack.

---

## Recursive binary search

Recursive binary search reduces the input range by half after every call.

The recurrence is approximately:

`T(n) = T(n / 2) + O(1)`

Therefore:

`T(n) = O(log n)`

The recursive implementation also uses call-stack space.

Its auxiliary space is:

`O(log n)`

An iterative binary search can achieve:

`O(log n)` time

with:

`O(1)` auxiliary space.

This is an example of how two implementations of the same algorithm can have identical time complexity but different space complexity.

---

## Naive recursive Fibonacci

Naive recursive Fibonacci is a useful complexity example because it demonstrates how quickly recursive branching can grow.

The implementation follows:

`F(n) = F(n - 1) + F(n - 2)`

A simplified recurrence for its running time is:

`T(n) = T(n - 1) + T(n - 2) + O(1)`

This grows exponentially.

The exact bound can be expressed using the Fibonacci sequence and is commonly described as exponential time, often written as approximately:

`O(2^n)`

as a simple upper-bound classification.

The important issue is repeated work.

For example, calculating `F(5)` causes the program to calculate some smaller Fibonacci values multiple times.

The dynamic version avoids this repeated work.

---

## Dynamic Fibonacci

The iterative Fibonacci implementation stores only the two values needed to calculate the next value.

It performs approximately `n` iterations.

Therefore:

`O(n)` time

and:

`O(1)` auxiliary space.

The three implementations compare naive recursive Fibonacci against an efficient iterative version.

This demonstrates a general algorithmic principle:

Avoid recomputing information when previously calculated results can be reused.

The broader family of techniques used to eliminate repeated subproblem work includes dynamic programming, although the Day 7 focus remains time-complexity analysis.

---

## Big O notation

Big O describes an asymptotic upper-growth classification.

For introductory algorithm analysis, common examples are:

`O(1)`

`O(log n)`

`O(n)`

`O(n log n)`

`O(n²)`

`O(n³)`

The notation is not a measurement of seconds.

An `O(n)` implementation can be slower than an `O(n²)` implementation for very small inputs because the two implementations may have very different constants and fixed overhead.

For sufficiently large inputs, asymptotic growth becomes increasingly important.

---

## Big O versus exact runtime

Suppose Algorithm A takes:

`1000n`

basic operations.

Algorithm B takes:

`n²`

basic operations.

For `n = 10`:

Algorithm A:

`1000 × 10 = 10,000`

Algorithm B:

`10² = 100`

Algorithm B may perform less work.

For `n = 1,000,000`:

Algorithm A:

`1,000,000,000`

Algorithm B:

`1,000,000,000,000`

The asymptotic behavior eventually becomes dominant.

This illustrates why Big O is useful while also showing why Big O alone does not describe every practical performance characteristic.

---

## Best case, average case, and worst case

An algorithm can perform different amounts of work depending on the input.

Linear search provides a simple example.

Suppose the target is at the first position.

Best case:

`O(1)`

Suppose the target is at the final position.

Worst case:

`O(n)`

Suppose the target is somewhere in the middle.

Typical successful searches may inspect a substantial fraction of the input.

Average case:

`O(n)`

The case being analyzed must therefore be stated explicitly when precision matters.

---

## Space complexity

Time complexity describes computational work.

Space complexity describes memory requirements.

These are separate dimensions.

An algorithm can be:

- fast but memory-intensive
- memory-efficient but computationally expensive
- efficient in both dimensions
- constrained by either CPU or memory depending on workload

The Python implementation compares:

`iterative_sum()`

with:

`copied_sum()`

The first uses:

`O(n)` time and `O(1)` auxiliary space.

The second creates a copy:

`O(n)` time and `O(n)` auxiliary space.

The JavaScript implementation provides the same conceptual comparison.

The C++ merge sort implementation uses additional storage for merging.

---

## Input space versus auxiliary space

When discussing space complexity, it is useful to distinguish between memory already occupied by the input and additional memory created by the algorithm.

For example, if a function receives an array containing `n` elements, that array already requires memory.

If the function creates another array of `n` elements, the algorithm has introduced `O(n)` additional storage.

This is why algorithm analyses often refer specifically to auxiliary space.

---

## Complexity of common patterns

| Code pattern | Typical complexity |
|---|---|
| Direct indexed access | `O(1)` |
| One fixed number of operations | `O(1)` |
| One loop over `n` elements | `O(n)` |
| Two sequential loops over `n` elements | `O(n)` |
| Loop that repeatedly halves input | `O(log n)` |
| Loop that repeatedly doubles a value | `O(log n)` |
| Loop of `n` iterations containing a logarithmic loop | `O(n log n)` |
| Two independent nested loops | `O(n²)` |
| Three independent nested loops | `O(n³)` |
| Binary search | `O(log n)` |
| Linear search | `O(n)` |
| Merge sort | `O(n log n)` |
| Simple recursive countdown | `O(n)` |
| Recursive binary search | `O(log n)` |
| Naive recursive Fibonacci | Exponential |

These classifications assume that the stated input-size relationship actually applies to the code.

---

## Important distinction: nested loops do not always mean `O(n²)`

A nested loop must be analyzed according to how many times the inner loop actually executes.

For example, if the outer loop runs `n` times and the inner loop halves a value:

`n × log n`

the result can be:

`O(n log n)`

Similarly, if the inner loop executes a fixed number of times independent of `n`, the nested structure may still be:

`O(n)`

The visual appearance of the source code is not enough. The number of executions must be analyzed.

---

## Important distinction: sequential loops do not multiply

Consider:

`O(n) + O(n)`

This is:

`O(n)`

not:

`O(n²)`.

Multiplication generally appears when one amount of work occurs inside another amount of work.

For example:

`n` outer iterations × `n` inner iterations

gives:

`n²`

This distinction is one of the most important beginner-level rules in time-complexity analysis.

---

## Logarithm bases

For asymptotic classification:

`O(log₂ n)`

and:

`O(log₁₀ n)`

are equivalent.

The mathematical identity is:

`log_a(n) = log_b(n) / log_b(a)`

The denominator is a constant when the bases are fixed.

Therefore changing the base only changes the constant factor.

In actual numerical calculations, the values are different.

For Big O classification, the growth class remains logarithmic.

---

## Common mistakes

### Mistake: treating every loop as `O(n)`

A loop that increments by one may be `O(n)`.

A loop that doubles its value may be `O(log n)`.

A loop whose work depends on another loop may be `O(n²)` or another complexity.

The update rule matters.

### Mistake: multiplying sequential loops

Two consecutive `O(n)` loops are:

`O(n) + O(n) = O(n)`

not `O(n²)`.

### Mistake: ignoring recursion structure

A recursive function with one recursive call can be linear.

A recursive function with two branching calls can be exponential.

The number of recursive calls matters.

### Mistake: assuming nested loops always produce `O(n²)`

The bounds of the loops must be examined.

### Mistake: confusing runtime with Big O

Big O does not say:

"This program takes 0.2 seconds."

It says how computational work grows as the input size grows.

### Mistake: ignoring input requirements

Binary search is `O(log n)`, but it requires sorted data.

If sorting is required first, the total process may include:

`O(n log n) + O(log n)`

which is:

`O(n log n)`

for a one-time sort followed by one search.

### Mistake: ignoring memory

An algorithm may have excellent time complexity but consume large amounts of memory.

---

## Edge cases

Correct complexity analysis also requires correct handling of boundary conditions.

The implementations demonstrate:

- empty arrays
- one-element arrays
- missing search targets
- smallest valid input values
- invalid logarithm inputs
- invalid transaction IDs
- invalid transaction amounts
- negative Fibonacci inputs
- out-of-range vector access

For example, logarithmic analysis assumes a meaningful positive input for logarithms.

`log₂(0)` is not defined in the ordinary real-number setting.

Likewise, binary search over an empty collection must terminate safely.

Edge cases are not separate from algorithm design. They are part of the correctness requirements.

---

## Performance measurements

All three implementations include timing demonstrations.

Python uses `time.perf_counter()`.

JavaScript uses `performance.now()`.

C++ uses `std::chrono::steady_clock`.

These measurements are useful for experimentation, but they do not replace complexity analysis.

Measured execution time depends on:

- hardware
- operating system
- background processes
- compiler optimization
- interpreter overhead
- memory allocation
- CPU cache
- runtime implementation
- dataset contents

Two implementations with the same Big O complexity can have very different measured performance.

For example, both of these may be `O(n)`:

- a simple integer scan
- a scan performing expensive cryptographic or numerical work per element

Their actual runtime can be very different.

---

## Complexity and production engineering

Time complexity becomes particularly important when input size grows.

An algorithm that works well for:

`n = 100`

may not work well for:

`n = 1,000,000`

The growth class determines how rapidly the computational burden increases.

This matters in:

- databases
- search systems
- financial analytics
- recommendation systems
- network processing
- scientific computing
- machine learning pipelines
- web applications
- cybersecurity
- distributed systems
- data processing
- simulation systems

The C++ case study models a transaction-processing environment because such systems frequently perform searches, aggregation, sorting, pairwise analysis, and reporting.

---

## C++ case study

The C++ program models a fictional financial transaction analytics system.

Each transaction contains:

- transaction ID
- account ID
- transaction amount
- completion status

The central data structure is:

`std::vector<Transaction>`

This provides random access and supports sorting and sequential processing.

### Constant-time transaction access

`getTransactionAt()` accesses a vector element using an index.

The operation is modeled as:

`O(1)`

provided the index is already known.

The function validates the index and throws an exception when it is invalid.

### Linear transaction search

`linearSearchById()` scans transactions from beginning to end.

Worst case:

`O(n)`

Best case:

`O(1)`

This is appropriate when the collection is unsorted and the number of searches is limited.

### Binary transaction search

`binarySearchById()` assumes transactions are sorted by transaction ID.

The search range is repeatedly divided.

Complexity:

`O(log n)`

The implementation uses an iterative approach, so its auxiliary space is:

`O(1)`

### Merge sorting

`mergeSortById()` orders transactions by ID.

Its complexity is:

`O(n log n)`

The implementation uses temporary storage for merging, giving approximately:

`O(n)`

auxiliary space.

Once the data is sorted, binary search becomes available.

This demonstrates an important systems-level trade-off:

A preprocessing cost can be worthwhile when it enables many faster operations later.

---

## Quadratic pairwise analysis

`findAccountPairsQuadratic()` compares transaction pairs.

The number of pair comparisons is approximately:

`n(n - 1) / 2`

Therefore the complexity is:

`O(n²)`

This is a realistic pattern because pairwise comparison appears in many domains.

Examples include:

- duplicate detection
- similarity comparison
- conflict detection
- correlation analysis
- relationship discovery
- pairwise risk analysis

The approach is simple and sometimes appropriate for small datasets.

Its weakness is scalability.

---

## Improving the quadratic problem

The C++ case study also provides:

`countTransactionsByAccount()`

This uses:

`std::unordered_map`

to aggregate transactions by account.

Average-case hash-table insertion and lookup are approximately:

`O(1)`

Therefore processing `n` transactions is approximately:

`O(n)`

average time.

The trade-off is additional memory.

This is an important algorithm-design pattern:

A slower algorithm can sometimes be replaced with a faster algorithm by storing additional information.

In this example:

Quadratic pairwise comparison:

`O(n²)`

Hash-based aggregation:

approximately `O(n)`

average time

with additional storage.

---

## Hash-table complexity caveat

Hash tables are often described as having average-case constant-time lookup.

That does not mean every hash-table operation is guaranteed to be exactly `O(1)` under every possible condition.

Factors include:

- hash-function quality
- collisions
- resizing
- implementation details
- adversarial inputs

The `unordered_map` implementation is therefore described as approximately constant-time on average rather than universally constant-time.

---

## Three-dimensional analysis

The C++ function `cubicRiskScan()` uses three independent dimensions.

Its work grows approximately as:

`n × n × n`

Therefore:

`O(n³)`

This is included to make the difference between quadratic and cubic growth concrete.

Cubic algorithms can be useful when the problem genuinely requires three-dimensional combinations, but they require careful constraints when `n` becomes large.

---

## Error handling

The C++ case study uses exceptions for invalid conditions such as:

- invalid transaction IDs
- empty account IDs
- invalid transaction amounts
- out-of-range vector access
- invalid Fibonacci input
- numeric overflow in Fibonacci calculations

Error handling does not automatically change the main asymptotic complexity of the successful algorithm.

It is still essential for production-quality software because correctness includes predictable behavior for invalid input.

---

## Security considerations

Time complexity also has security implications.

An algorithm that performs excessive work on attacker-controlled input can create a denial-of-service risk.

Examples include:

- extremely large inputs
- deliberately expensive nested comparisons
- pathological recursive input
- inefficient parsing
- expensive repeated computations
- hash-table collision attacks
- unbounded data processing

The complexity of an algorithm should therefore be considered when accepting external input.

A theoretically correct algorithm can still be unsuitable if an attacker can force it to process an unexpectedly large amount of data.

---

## Recursion limits and stack usage

Recursive algorithms use call-stack memory.

For a recursion depth of `n`, auxiliary stack usage may be:

`O(n)`

This can eventually exceed the runtime's supported stack depth.

Python and JavaScript environments impose practical recursion limits or stack constraints.

C++ also has finite stack capacity.

Iterative implementations can avoid recursion-related stack growth.

For example:

- iterative binary search: `O(log n)` time and `O(1)` auxiliary space
- recursive binary search: `O(log n)` time and `O(log n)` stack space

The time complexity is the same, but the memory behavior differs.

---

## Trade-offs

Algorithm selection is rarely based on time complexity alone.

Relevant factors include:

- time complexity
- space complexity
- implementation complexity
- correctness requirements
- data ordering
- input size
- frequency of operations
- memory availability
- latency requirements
- maintainability
- worst-case behavior
- average-case behavior
- security requirements

For example, binary search is faster asymptotically than linear search, but it requires sorted data.

Merge sort has strong time complexity but uses additional memory.

Hash-based aggregation can improve average runtime while increasing memory usage.

A simple quadratic algorithm can be completely reasonable when `n` is small and the implementation simplicity has value.

---

## Python implementation

The Python file is organized as a standalone study program.

It demonstrates:

- constant operations
- linear operations
- nested loops
- triangular loops
- cubic loops
- halving
- doubling
- binary search
- merge sort
- sequential complexity
- `O(n log n)` loop structures
- recursion
- naive Fibonacci
- dynamic Fibonacci
- best and worst cases
- operation counting
- space complexity
- timing
- edge cases
- automated correctness tests
- scaling tables

The functions are intentionally separated so that each complexity pattern can be studied independently.

Python is particularly useful for learning because the syntax allows the algorithmic structure to remain visually clear.

---

## JavaScript implementation

The JavaScript file provides equivalent algorithmic concepts while demonstrating JavaScript-specific syntax and runtime behavior.

It includes:

- arrays
- functions
- loops
- recursion
- array copying
- timing through `performance.now()`
- error handling with `RangeError`
- object-based complexity descriptions
- assertions
- sorting implementation
- iterative and recursive searching

The JavaScript implementation is designed to run in a Node.js environment without external packages.

JavaScript is useful for demonstrating how the same complexity principles apply in application and web-oriented programming.

The complexity comes from the algorithmic structure, not from the programming language itself.

For example, a linear loop remains conceptually `O(n)` whether implemented in Python, JavaScript, or C++.

The constants and actual runtime can differ.

---

## C++ implementation

The C++ program develops the topic through a more substantial transaction-processing scenario.

Major components include:

- `Transaction` data model
- transaction validation
- vector-based storage
- constant-time indexed access
- linear search
- binary search
- linear transaction aggregation
- quadratic pairwise analysis
- hash-based account aggregation
- cubic risk scanning
- halving and doubling demonstrations
- merge sort
- recursive algorithms
- iterative Fibonacci
- timing measurements
- correctness tests
- edge-case tests

The program is compatible with C++17 and uses the standard library.

C++ is particularly useful for demonstrating how algorithmic complexity interacts with explicit data structures, memory allocation, standard-library containers, recursion, and low-level performance considerations.

---

## Comparison of the three implementations

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Beginner algorithm demonstration | Strong | Strong | Strong |
| Direct executable examples | Yes | Yes | Yes |
| Loop analysis | Yes | Yes | Yes |
| Recursion | Yes | Yes | Yes |
| Binary search | Yes | Yes | Yes |
| Merge sort | Yes | Yes | Yes |
| Timing | `perf_counter()` | `performance.now()` | `steady_clock` |
| Error handling | Exceptions | Exceptions | Exceptions |
| Case study | General algorithm demonstrations | Application-oriented demonstrations | Transaction analytics system |
| Memory control | Higher-level | Higher-level | More explicit |
| Standard-library data structures | Python collections | JavaScript arrays/objects | `vector`, `unordered_map` |
| Production-style system modeling | Moderate | Moderate | Detailed |

The mathematical complexity classifications do not change simply because the language changes.

The actual runtime characteristics can change substantially because language runtimes, compilers, memory models, and standard libraries differ.

---

## Practical complexity analysis procedure

A systematic approach can be used when analyzing a new function.

### Identify the input size

Determine what `n` represents.

### Identify the dominant work

Look for loops, recursive calls, sorting, searching, or repeated operations.

### Count loop iterations

Ask how many times each loop executes.

### Examine nesting

Nested independent loops often multiply their iteration counts.

### Examine sequential operations

Sequential blocks normally add their costs.

### Examine changing variables

Check whether a variable:

- increments
- decrements
- doubles
- halves
- changes according to another input

### Analyze recursion

Identify:

- number of recursive calls
- input reduction
- work performed per call
- overlapping subproblems
- recursion depth

### Combine terms

For example:

`O(n) + O(n²)`

becomes:

`O(n²)`

### Consider space

Identify:

- new arrays
- maps
- temporary buffers
- recursive call stack
- copied data

### Check assumptions

Ask whether the algorithm requires:

- sorted data
- unique values
- bounded input
- random access
- hashing
- extra memory

---

## Complexity of the Day 7 practice patterns

### Single loop

A loop that executes once per input element:

`O(n)`

### Nested loops

Two loops each running approximately `n` times:

`O(n²)`

### Sequential loops

Two loops each running approximately `n` times but executed one after another:

`O(n)`

### Loop with halving

A loop repeatedly dividing a value by two:

`O(log n)`

### Loop with doubling

A loop repeatedly multiplying a value by two:

`O(log n)`

### `n` iterations containing a halving loop

Outer work:

`O(n)`

Inner work:

`O(log n)`

Combined:

`O(n log n)`

### Simple recursion with `n - 1`

One recursive call per level:

`O(n)`

### Recursive binary search

Input approximately halves:

`O(log n)`

### Naive recursive Fibonacci

Two overlapping recursive branches:

Exponential time

---

## Complexity hierarchy

For sufficiently large `n`, the common growth rates can be ordered approximately as:

`O(1)`

then

`O(log n)`

then

`O(n)`

then

`O(n log n)`

then

`O(n²)`

then

`O(n³)`

The exact practical performance can still depend on constants and implementation details.

The hierarchy is most useful for understanding how quickly computational requirements grow as input size increases.

---

## Why input constraints matter

Suppose a problem allows only:

`n ≤ 100`

An `O(n²)` solution performs at most roughly:

`10,000`

pairwise-scale operations.

That may be entirely practical.

If the constraint becomes:

`n ≤ 1,000,000`

then an `O(n²)` approach implies a scale around:

`10¹²`

operations.

The same algorithm can therefore be reasonable under one input constraint and unusable under another.

Complexity analysis must always be connected to expected input sizes.

---

## Real-world relevance

Time complexity affects many real systems.

### Search systems

Large collections benefit from indexing and efficient search algorithms.

### Databases

Indexes can transform repeated scans into substantially faster lookup operations.

### Financial systems

Transaction analytics can involve millions of records, making unnecessary quadratic operations expensive.

### Cybersecurity

Security systems often process large volumes of logs, events, network packets, and authentication records.

### Data processing

Sorting and aggregation are common operations where complexity directly affects processing time.

### Web applications

Poor algorithms can create latency when request size or database result size grows.

### Scientific computing

Simulation algorithms may operate over multiple dimensions, making quadratic or cubic growth particularly important.

### Distributed systems

Complexity affects the amount of computation that must be distributed across machines.

---

## Limitations of Big O

Big O is powerful but incomplete.

It does not directly tell us:

- exact execution time
- memory latency
- cache behavior
- constant factors
- compiler optimizations
- processor-specific instructions
- network latency
- disk latency
- database implementation details
- concurrency effects

Two algorithms with the same complexity can have substantially different practical performance.

For example:

`O(n)`

does not identify the cost of the operation performed during each iteration.

An algorithm that performs a simple integer addition in each iteration can behave very differently from an algorithm that performs a large cryptographic calculation in each iteration.

Big O is therefore one part of performance engineering rather than a complete performance model.

---

## Best practices

When analyzing and implementing algorithms:

- Define the input size clearly.
- Identify the dominant operation.
- Count loop iterations rather than judging code by appearance.
- Distinguish sequential loops from nested loops.
- Analyze recursive call structure.
- Remove constant factors for asymptotic classification.
- Remove lower-order terms when identifying the dominant growth class.
- Consider both time and auxiliary space.
- State important input assumptions.
- Consider best, average, and worst cases when relevant.
- Test boundary conditions.
- Use measured timing only as experimental evidence.
- Consider realistic input sizes.
- Avoid unnecessarily expensive algorithms for large inputs.
- Consider memory and time together.
- Consider security implications of attacker-controlled input.
- Document assumptions that affect complexity.

---

## Key formulas

### Constant

`O(1)`

### Linear

`O(n)`

### Logarithmic

`O(log n)`

### Linearithmic

`O(n log n)`

### Quadratic

`O(n²)`

### Cubic

`O(n³)`

### Triangular sum

`1 + 2 + ... + n = n(n + 1) / 2`

Therefore:

`O(n²)`

### Sequential operations

`O(n) + O(n) = O(n)`

### Dominant term

`O(n²) + O(n) = O(n²)`

### Nested independent loops

`n × n = n²`

### Three nested independent loops

`n × n × n = n³`

### Halving

Repeated division by a constant factor:

`O(log n)`

### Doubling

Repeated multiplication by a constant factor:

`O(log n)`

---

## Important conceptual distinction

The most important idea in Day 7 is not memorizing a table of complexity classes.

The essential skill is learning to derive the growth from the structure of the algorithm.

For example:

A loop that increments from `1` to `n` suggests linear growth.

A loop that repeatedly divides by two suggests logarithmic growth.

Two independent `n`-sized loops nested together suggest quadratic growth.

Three independent `n`-sized loops suggest cubic growth.

A divide-and-conquer algorithm that performs linear work across logarithmic levels suggests `O(n log n)`.

A recursive function must be analyzed according to the number and size of its recursive subproblems.

This reasoning can then be applied to algorithms that are not explicitly listed in a complexity table.

---

## Implementation files

The complete study material consists of three executable implementations:

- Python: a comprehensive algorithm-analysis study program with demonstrations, experiments, tests, and complexity comparisons.
- JavaScript: an executable implementation emphasizing language-level algorithm demonstrations, recursion, arrays, timing, and application-oriented behavior.
- C++: an industry-style transaction analytics case study showing how algorithm choice affects search, sorting, aggregation, pairwise analysis, memory usage, and scalability.

Each implementation is self-contained and uses standard language facilities without requiring third-party packages.
