# Day 10 — Best, average and worst case

[View Day 10 on GitHub](https://github.com/ATULPANDEYIITR/dsa_data_structures_and_algorithm_preparation#day-10--best-average-and-worst-case)

## Topic scope

This chapter focuses on analyzing the efficiency of algorithms and data-structure operations using time and space complexity.

The main concepts covered are:

- Algorithmic complexity
- Best-case complexity
- Average-case complexity
- Worst-case complexity
- Asymptotic notation
- Big O notation
- Growth rates
- Searching algorithms
- Sorting algorithms
- Hash tables
- Arrays and dynamic arrays
- Linked lists
- Amortized analysis
- Practical complexity analysis
- Security and performance considerations
- Implementation considerations in Python, JavaScript, and C++

## What algorithmic complexity means

Algorithmic complexity describes how the resource requirements of an algorithm change as the size of the input increases.

The two primary resources are:

- **Time complexity** — how the number of operations grows with input size.
- **Space complexity** — how the amount of additional memory grows with input size.

If an algorithm processes `n` elements and performs approximately `n` operations, its time complexity is linear.

If it performs approximately `n²` operations, its time complexity is quadratic.

The objective of complexity analysis is not normally to determine the exact number of processor instructions. Instead, it identifies how the algorithm scales as the input becomes larger.

## Best-case, average-case and worst-case complexity

An algorithm can behave differently depending on the arrangement of the input.

### Best case

The best case represents the most favorable input.

For example, when searching for an element using linear search, the element may be the first element in the collection.

Only one comparison is required.

The best-case time complexity is therefore:

`O(1)`

### Average case

The average case describes expected behavior across typical inputs.

For linear search, if the requested element is equally likely to appear at any position, approximately half of the elements are examined on average.

The average-case complexity is:

`O(n)`

### Worst case

The worst case represents the maximum amount of work required for an input of size `n`.

For linear search, the requested element may be the final element or may not exist at all.

The algorithm may therefore inspect every element.

The worst-case complexity is:

`O(n)`

## Asymptotic notation

Asymptotic notation describes how an algorithm grows as the input size becomes large.

The most common notation is Big O.

### Big O notation

Big O provides an upper-bound style description of growth and is commonly used to describe worst-case scalability.

Common examples include:

- `O(1)` — constant
- `O(log n)` — logarithmic
- `O(n)` — linear
- `O(n log n)` — linearithmic
- `O(n²)` — quadratic
- `O(n³)` — cubic
- `O(2ⁿ)` — exponential
- `O(n!)` — factorial

The difference between these growth rates becomes increasingly important as `n` increases.

## Why constants are ignored

Consider two algorithms:

`5n`

and:

`100n`

Both are linear.

Their exact runtimes can differ significantly for a particular machine or implementation, but their growth pattern is the same.

Big O therefore focuses on the dominant growth term.

For example:

`3n² + 5n + 10`

is simplified to:

`O(n²)`

The lower-order terms and constant factors are ignored when describing asymptotic growth.

This does not mean constants are irrelevant in real software. Constants can have a major effect on actual runtime. They are simply omitted when classifying asymptotic growth.

## Growth-rate hierarchy

A simplified growth-rate hierarchy from generally slower growth to faster growth is:

`O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!)`

The difference becomes substantial for large inputs.

For example:

- An `O(1)` operation remains approximately constant.
- An `O(log n)` algorithm grows very slowly.
- An `O(n)` algorithm grows proportionally with input size.
- An `O(n log n)` algorithm is common for efficient comparison sorting.
- An `O(n²)` algorithm can become expensive for large collections.
- Exponential and factorial algorithms become impractical very quickly.

## Linear search

Linear search examines elements sequentially until the target is found or the collection is exhausted.

For an array:

`[10, 20, 30, 40, 50]`

Searching for `40` checks:

`10 → 20 → 30 → 40`

Searching for `100` checks every element.

### Linear search complexity

| Case | Complexity |
|---|---|
| Best case | `O(1)` |
| Average case | `O(n)` |
| Worst case | `O(n)` |
| Space | `O(1)` |

Linear search requires no special ordering of the data.

### Linear search edge cases

Important cases include:

- Empty collection
- Single-element collection
- Target at the first position
- Target at the last position
- Target absent
- Duplicate values
- Very large collection

For an empty collection, the search completes immediately.

For a single-element collection, the search requires at most one comparison.

If duplicates exist, the implementation must define whether it returns the first occurrence, last occurrence, all occurrences, or simply any occurrence.

## Binary search

Binary search repeatedly divides a sorted search space into two parts.

Suppose the sorted array is:

`[10, 20, 30, 40, 50, 60, 70]`

To search for `60`, the algorithm examines the middle element and determines whether the target lies to the left or right.

The search space is repeatedly reduced by approximately half.

### Binary search requirements

Binary search normally requires:

- Random access to elements
- Sorted data
- A comparison operation that establishes ordering

If the data is not sorted, ordinary binary search cannot be applied correctly.

### Binary search complexity

| Case | Complexity |
|---|---|
| Best case | `O(1)` |
| Average case | `O(log n)` |
| Worst case | `O(log n)` |
| Space | `O(1)` for an iterative implementation |

The logarithmic behavior comes from repeatedly halving the search space.

For example:

`1,000,000`

elements can be reduced to approximately:

`500,000 → 250,000 → 125,000 → ...`

Only a small number of divisions are required compared with scanning every element.

### Linear search versus binary search

| Feature | Linear Search | Binary Search |
|---|---|---|
| Data must be sorted | No | Yes |
| Best case | `O(1)` | `O(1)` |
| Average case | `O(n)` | `O(log n)` |
| Worst case | `O(n)` | `O(log n)` |
| Random access required | No | Usually yes |
| Simple implementation | Yes | Moderate |
| Good for unsorted data | Yes | No |
| Good for repeated searches | Sometimes | Yes |

If the collection is small or unsorted, linear search may be perfectly adequate.

If the collection is sorted and many searches are performed, binary search can substantially reduce search work.

## Sorting algorithms

Sorting rearranges data according to an ordering rule.

Examples include:

- Ascending numeric order
- Descending numeric order
- Alphabetical order
- Sorting records by age
- Sorting records by score
- Sorting objects by multiple fields

Different sorting algorithms have different complexity characteristics.

## Bubble sort

Bubble sort repeatedly compares neighboring elements and swaps them when they are in the wrong order.

For:

`[5, 2, 4, 1]`

the algorithm compares adjacent values and gradually moves larger values toward the end.

### Bubble sort complexity

| Case | Complexity |
|---|---|
| Best case | `O(n)` with an early-exit optimization |
| Average case | `O(n²)` |
| Worst case | `O(n²)` |
| Space | `O(1)` |

Bubble sort is easy to understand but is generally inefficient for large datasets.

## Selection sort

Selection sort repeatedly identifies the smallest remaining element and places it into its final position.

For example:

`[5, 2, 4, 1]`

The smallest element, `1`, is selected and placed at the beginning.

The process continues with the remaining elements.

### Selection sort complexity

| Case | Complexity |
|---|---|
| Best case | `O(n²)` |
| Average case | `O(n²)` |
| Worst case | `O(n²)` |
| Space | `O(1)` |

Selection sort performs roughly the same number of comparisons regardless of whether the input is already sorted.

## Insertion sort

Insertion sort builds a sorted section of the collection one element at a time.

For example:

`[5, 2, 4, 1]`

The algorithm treats the first element as sorted and inserts subsequent elements into the appropriate position.

### Insertion sort complexity

| Case | Complexity |
|---|---|
| Best case | `O(n)` |
| Average case | `O(n²)` |
| Worst case | `O(n²)` |
| Space | `O(1)` |

Insertion sort performs well on:

- Small collections
- Nearly sorted data
- Data arriving incrementally

## Merge sort

Merge sort uses divide and conquer.

The collection is divided into smaller parts until individual elements remain.

The smaller sorted collections are then merged together.

For example:

`[8, 3, 5, 1]`

can be divided into:

`[8, 3]` and `[5, 1]`

which are further divided and then merged in sorted order.

### Merge sort complexity

| Case | Complexity |
|---|---|
| Best case | `O(n log n)` |
| Average case | `O(n log n)` |
| Worst case | `O(n log n)` |
| Space | `O(n)` for a typical implementation |

Merge sort provides predictable performance but normally requires additional memory for merging.

## Quicksort

Quicksort also uses divide and conquer.

A pivot is selected and the collection is partitioned around the pivot.

Values smaller than the pivot are placed on one side and larger values on the other side.

The partitions are recursively sorted.

### Quicksort complexity

| Case | Complexity |
|---|---|
| Best case | `O(n log n)` |
| Average case | `O(n log n)` |
| Worst case | `O(n²)` |
| Space | Typically `O(log n)` average recursion stack, depending on implementation |

The worst case can occur when pivot selection produces highly unbalanced partitions.

Good pivot-selection strategies reduce the likelihood of poor partitioning.

## Sorting comparison

| Algorithm | Best | Average | Worst | Typical extra space |
|---|---:|---:|---:|---:|
| Bubble sort | `O(n)`* | `O(n²)` | `O(n²)` | `O(1)` |
| Selection sort | `O(n²)` | `O(n²)` | `O(n²)` | `O(1)` |
| Insertion sort | `O(n)` | `O(n²)` | `O(n²)` | `O(1)` |
| Merge sort | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(n)` |
| Quicksort | `O(n log n)` | `O(n log n)` | `O(n²)` | Depends on recursion and implementation |

`*` Bubble sort achieves `O(n)` best-case behavior when implemented with an early-exit check for an already sorted collection.

## Hash tables

A hash table stores data using a hash function that maps keys to positions in an underlying table.

For example:

`"alice" → hash("alice") → index`

This allows direct access to a location based on the key.

### Hash-table complexity

| Operation | Average | Worst |
|---|---:|---:|
| Search | `O(1)` | `O(n)` |
| Insert | `O(1)` | `O(n)` |
| Delete | `O(1)` | `O(n)` |

The average `O(1)` behavior depends on a good hash function, appropriate table sizing, and effective collision handling.

### Hash collisions

A collision occurs when two different keys map to the same table location.

For example:

`hash("Alice") = 10`

and:

`hash("Bob") = 10`

Possible collision-handling approaches include:

- Separate chaining
- Open addressing
- Linear probing
- Quadratic probing
- Double hashing

Poor collision behavior can degrade performance toward `O(n)`.

## Arrays

Arrays provide contiguous or logically indexed storage depending on the underlying language and implementation.

Typical operations include:

- Access by index
- Update by index
- Search
- Insert
- Delete
- Append

### Array operation complexity

| Operation | Typical complexity |
|---|---:|
| Access by index | `O(1)` |
| Update by index | `O(1)` |
| Search unsorted array | `O(n)` |
| Search sorted array using binary search | `O(log n)` |
| Insert at beginning | `O(n)` |
| Insert in middle | `O(n)` |
| Delete from beginning | `O(n)` |
| Delete from middle | `O(n)` |
| Append to fixed-capacity array | `O(1)` if space exists |

Insertion or deletion in the middle can require shifting many elements.

## Dynamic arrays

Dynamic arrays automatically resize when their current capacity becomes insufficient.

Examples include:

- Python lists
- JavaScript arrays
- C++ `std::vector`

Appending to a dynamic array is usually:

`O(1)` amortized

A resize operation itself may require:

`O(n)`

elements to be copied.

### Amortized analysis

Amortized analysis studies the average cost of a sequence of operations rather than treating every operation independently.

Suppose a dynamic array doubles its capacity when full.

Most append operations require constant work.

Occasionally, a resize copies many elements.

Over a long sequence of append operations, the total work is still proportional to the number of inserted elements.

Therefore:

`append = O(1) amortized`

This does not mean every append is literally `O(1)`.

A particular append that triggers resizing may take `O(n)`.

## Linked lists

A singly linked list consists of nodes where each node stores data and a reference to the next node.

Conceptually:

`Node → Node → Node → None`

Each node can be located separately in memory.

### Linked-list operation complexity

| Operation | Complexity |
|---|---:|
| Access by index | `O(n)` |
| Search | `O(n)` |
| Insert at head | `O(1)` |
| Delete at head | `O(1)` |
| Insert after known node | `O(1)` |
| Delete after known node | `O(1)` |
| Append without tail pointer | `O(n)` |
| Append with tail pointer | `O(1)` |

The major difference between arrays and linked lists is how elements are accessed.

Arrays provide direct indexed access.

Linked lists require traversal from a known starting point.

## Array versus linked list

| Feature | Array | Linked List |
|---|---|---|
| Random access | `O(1)` | `O(n)` |
| Search | `O(n)` | `O(n)` |
| Insert at beginning | `O(n)` | `O(1)` |
| Delete at beginning | `O(n)` | `O(1)` |
| Memory layout | Typically contiguous | Nodes can be distributed |
| Extra pointer/reference memory | No per-element link required | Required |
| Cache locality | Usually strong | Usually weaker |
| Resizing | May require reallocation | Usually not required |

The correct data structure depends on the operation pattern.

## C++ student record case study

Consider a collection of student records:

`Student`

with fields such as:

- Student ID
- Name
- Age
- Course
- Score

Suppose the program stores:

`n`

student records.

### Record validation

A validation operation might check:

- ID format
- Name validity
- Age range
- Course validity
- Score range

If each record is validated independently and each validation takes constant work, validating all records requires:

`O(n)`

time.

If validation includes operations whose complexity depends on the number of fields or related records, that additional cost must also be considered.

### Linear search in the case study

Suppose the program searches for a student by ID using a vector.

A sequential search may inspect:

`1, 2, 3, ..., n`

records.

The complexity is:

- Best case: `O(1)`
- Average case: `O(n)`
- Worst case: `O(n)`

### Sorting before repeated searches

Suppose the application repeatedly searches a large collection by student ID.

One strategy is:

- Sort the records by ID.
- Use binary search for each query.

Sorting may cost:

`O(n log n)`

For example, using merge sort.

Each binary search then costs:

`O(log n)`

For `q` searches, the total approximate complexity becomes:

`O(n log n + q log n)`

This can be preferable to performing `q` linear searches:

`O(qn)`

when the same dataset is searched many times.

### Hash-table index

Another approach is to create a hash table:

`student_id → student record`

Building the index generally requires:

`O(n)` average time.

A lookup is:

`O(1)` average

and:

`O(n)` worst case

under poor collision conditions.

For repeated lookups, a hash-based index can provide very fast average access.

### Linked-list representation

If student records are stored in a singly linked list, searching by student ID requires traversal.

Therefore:

- Best case: `O(1)`
- Average case: `O(n)`
- Worst case: `O(n)`

If a record is already known through a node reference, inserting or deleting adjacent nodes can be `O(1)`.

The structure is therefore useful for certain insertion and deletion patterns but does not provide efficient random access.

## Complexity reference sheet

### Searching

| Algorithm | Best | Average | Worst |
|---|---:|---:|---:|
| Linear search | `O(1)` | `O(n)` | `O(n)` |
| Binary search | `O(1)` | `O(log n)` | `O(log n)` |
| Hash-table lookup | `O(1)` | `O(1)` | `O(n)` |

### Sorting

| Algorithm | Best | Average | Worst |
|---|---:|---:|---:|
| Bubble sort | `O(n)`* | `O(n²)` | `O(n²)` |
| Selection sort | `O(n²)` | `O(n²)` | `O(n²)` |
| Insertion sort | `O(n)` | `O(n²)` | `O(n²)` |
| Merge sort | `O(n log n)` | `O(n log n)` | `O(n log n)` |
| Quicksort | `O(n log n)` | `O(n log n)` | `O(n²)` |

### Hash tables

| Operation | Average | Worst |
|---|---:|---:|
| Search | `O(1)` | `O(n)` |
| Insert | `O(1)` | `O(n)` |
| Delete | `O(1)` | `O(n)` |

### Dynamic arrays

| Operation | Complexity |
|---|---:|
| Index access | `O(1)` |
| Update | `O(1)` |
| Search | `O(n)` |
| Append | `O(1)` amortized |
| Resize | `O(n)` |
| Insert in middle | `O(n)` |
| Delete in middle | `O(n)` |

### Singly linked lists

| Operation | Complexity |
|---|---:|
| Access by index | `O(n)` |
| Search | `O(n)` |
| Insert at head | `O(1)` |
| Delete at head | `O(1)` |
| Insert after known node | `O(1)` |
| Delete after known node | `O(1)` |
| Append with tail pointer | `O(1)` |

## Important distinctions

### Worst-case complexity is not actual runtime

If an algorithm has worst-case complexity `O(n²)`, it does not mean every execution performs `n²` operations.

Worst-case complexity describes how bad the algorithm can become for an input of size `n`.

Real runtime also depends on:

- Input distribution
- Hardware
- Programming language
- Compiler or interpreter
- Memory hierarchy
- Implementation details
- Constant factors
- Operating-system behavior
- Other running processes

### Average complexity is not the same as amortized complexity

Average-case analysis considers expected behavior over a distribution of inputs.

Amortized analysis considers the total cost of a sequence of operations.

For example:

- Hash-table lookup may have expected `O(1)` average complexity under appropriate assumptions.
- Dynamic-array append is `O(1)` amortized even though individual resizing operations can cost `O(n)`.

These are different concepts.

## Edge cases

Complexity analysis should account for important input conditions.

### Empty input

For:

`n = 0`

many algorithms return immediately.

For example, searching an empty collection may take constant work:

`O(1)`

### Single element

For:

`n = 1`

many algorithms complete almost immediately.

The asymptotic classification still matters because complexity describes how behavior changes as `n` grows.

### Duplicate values

Duplicates can affect:

- Search results
- Sorting behavior
- Stability
- Hash-table representation
- Record indexing

The implementation must define the expected behavior.

### Already sorted input

Already sorted data can significantly improve some algorithms.

Insertion sort can operate in:

`O(n)`

when the input is already sorted.

An optimized bubble sort can also achieve:

`O(n)`

when no swaps are required.

### Reverse-sorted input

Reverse-sorted data can produce poor behavior for some algorithms.

For example, insertion sort may require approximately quadratic work:

`O(n²)`

and a poorly implemented quicksort can also reach:

`O(n²)`.

## Common mistakes

### Confusing Big O with exact runtime

`O(n)` does not mean exactly `n` seconds or exactly `n` operations.

It describes asymptotic growth.

### Ignoring input requirements

Binary search requires sorted data.

A binary search implementation cannot simply be applied to arbitrary unsorted data.

### Assuming hash tables are always O(1)

Hash-table operations are commonly `O(1)` on average, not guaranteed `O(1)` in every possible situation.

Collisions and implementation details matter.

### Forgetting the cost of sorting

If data must first be sorted before binary search can be used, the sorting cost must be included when analyzing the entire workflow.

For example:

`O(n log n) + O(log n)`

for one search after sorting is effectively:

`O(n log n)`

for the complete process.

### Ignoring repeated operations

A single linear search may be acceptable.

Thousands or millions of linear searches over the same dataset may become expensive.

The total workload must be considered.

### Confusing space complexity with total memory usage

Space complexity commonly focuses on additional or auxiliary memory required by the algorithm.

The memory required to store the original input may be discussed separately depending on the analysis.

## Performance considerations

Complexity is important, but it is not the only factor affecting performance.

Other considerations include:

- Cache locality
- Memory allocation
- Branch prediction
- Data representation
- CPU architecture
- Input/output operations
- Network latency
- Database latency
- Concurrency
- Garbage collection
- Interpreter or runtime overhead

An algorithm with theoretically better asymptotic complexity may not always be faster for small inputs.

For example, a simple `O(n²)` algorithm can sometimes outperform a more complicated `O(n log n)` algorithm on very small datasets because of lower constant overhead.

## Security considerations

Complexity analysis also matters for security.

Algorithms with poor worst-case behavior can be exploited through specially constructed inputs.

Examples include:

- Hash-table collision attacks
- Algorithmic complexity attacks
- Denial-of-service through expensive parsing
- Worst-case sorting behavior
- Excessive recursion
- Memory exhaustion
- Repeated expensive searches

When processing untrusted input, developers should consider both normal-case performance and adversarial inputs.

Good engineering practices include:

- Validating input
- Limiting input sizes
- Avoiding predictable worst-case behavior where possible
- Choosing robust algorithms
- Monitoring resource usage
- Applying appropriate timeouts
- Avoiding uncontrolled recursion

## Implementation considerations in Python

Python provides built-in data structures that hide many implementation details.

Common examples include:

- `list`
- `dict`
- `set`
- `tuple`

Typical operations include:

`list[index]`

for constant-time indexed access.

Dictionary lookup is generally expected to be:

`O(1)`

on average.

Appending to a Python list is:

`O(1)` amortized.

Searching a list is:

`O(n)`

unless another structure or algorithm is used.

## Implementation considerations in JavaScript

JavaScript arrays are dynamic structures and can support indexed access and append operations efficiently in typical implementations.

Objects and `Map` can be used for key-based lookup.

For example:

`map.get(key)`

typically provides expected constant-time lookup.

When analyzing JavaScript applications, consider:

- Dynamic typing
- JavaScript engine optimizations
- Garbage collection
- Array representation
- Object property behavior
- Browser or Node.js runtime characteristics

Asymptotic complexity remains useful even though runtime implementations can be highly optimized.

## Implementation considerations in C++

C++ provides direct control over many data structures and memory-related decisions.

Common structures include:

- `std::vector`
- `std::list`
- `std::unordered_map`
- `std::map`
- `std::array`

Typical complexity examples include:

`std::vector` indexed access: `O(1)`

`std::vector` amortized append: `O(1)`

`std::unordered_map` average lookup: `O(1)`

`std::map` lookup: `O(log n)`

`std::list` insertion or deletion at a known iterator position: `O(1)`

The actual performance depends on the workload, memory behavior, and implementation.

## Practical application patterns

### Small data

For small datasets, simplicity may be more important than asymptotic optimization.

A straightforward linear search or insertion sort may be entirely appropriate.

### Large data

As the dataset grows, growth rate becomes increasingly important.

An `O(n²)` algorithm can become significantly slower than an `O(n log n)` algorithm.

### Repeated searches

When the same dataset is queried repeatedly, preprocessing may be worthwhile.

Possible strategies include:

- Sorting followed by binary search
- Building a hash-table index
- Creating database indexes
- Caching frequently accessed values

### Dynamic workloads

When data changes frequently, maintaining a sorted structure may have a different cost from using a hash-based structure.

The correct choice depends on:

- Number of reads
- Number of writes
- Ordering requirements
- Memory constraints
- Lookup requirements

## Complexity analysis process

A practical process for analyzing an algorithm is:

### Identify the input size

Determine what `n` represents.

For example:

- Number of array elements
- Number of records
- Number of graph vertices
- Number of characters
- Number of queries

### Identify the dominant operations

Look for:

- Loops
- Nested loops
- Recursion
- Sorting
- Searching
- Hash-table operations
- Data copying
- Memory allocation

### Count repeated work

A single loop over `n` elements usually gives:

`O(n)`

Two independent loops give:

`O(n + n) = O(n)`

Nested loops often give:

`O(n²)`

### Check whether operations are sequential

If an algorithm performs:

`O(n)`

followed by:

`O(n)`

the total is:

`O(n + n) = O(n)`

The dominant growth rate remains linear.

### Check nested operations

If one `O(n)` operation occurs inside another `O(n)` operation:

`O(n × n) = O(n²)`

### Check divide and conquer

If an algorithm repeatedly divides the input and processes each level efficiently, the complexity may be:

`O(log n)`

or:

`O(n log n)`

depending on the amount of work performed at each level.

## Sequential algorithms

Suppose an algorithm contains:

`for each element in n:`

followed by:

`for each element in n:`

The total is:

`O(n + n)`

which simplifies to:

`O(n)`

Constants are ignored in asymptotic notation.

## Nested algorithms

Suppose:

`for each element in n:`
`    for each element in n:`

The inner loop executes approximately `n` times for each of the `n` outer iterations.

Therefore:

`O(n × n) = O(n²)`

Nested loops do not always automatically mean `O(n²)`. The exact relationship between loop bounds must be analyzed.

For example, if the inner loop executes a constant number of times, the total may still be:

`O(n)`.

## Divide-and-conquer algorithms

Merge sort demonstrates divide and conquer.

The input is divided into approximately equal halves.

There are approximately:

`log n`

levels.

At each level, approximately:

`O(n)`

work is performed to merge the elements.

Therefore:

`O(n log n)`

overall.

## Final reference sheet

| Concept | Typical complexity |
|---|---:|
| Constant operation | `O(1)` |
| Binary search | `O(log n)` |
| Linear search | `O(n)` |
| Efficient comparison sorting | `O(n log n)` |
| Quadratic sorting | `O(n²)` |
| Exponential algorithm | `O(2ⁿ)` |
| Factorial algorithm | `O(n!)` |
| Hash-table lookup average | `O(1)` |
| Hash-table lookup worst case | `O(n)` |
| Dynamic-array append amortized | `O(1)` |
| Array indexed access | `O(1)` |
| Linked-list indexed access | `O(n)` |

## Core lessons

- Complexity describes how resource usage scales with input size.
- Time complexity measures computational work.
- Space complexity measures additional memory requirements.
- Best case describes the most favorable input.
- Average case describes expected behavior under an input distribution.
- Worst case describes the maximum work for inputs of a given size.
- Big O is used to describe asymptotic growth.
- Constant factors and lower-order terms are normally ignored in asymptotic classification.
- Linear search has `O(n)` average and worst-case complexity.
- Binary search has `O(log n)` average and worst-case complexity when its requirements are satisfied.
- Binary search requires sorted data and suitable access to the search space.
- Bubble sort, selection sort, and insertion sort can have `O(n²)` average or worst-case behavior.
- Merge sort provides `O(n log n)` worst-case performance.
- Quicksort has `O(n log n)` average complexity but can reach `O(n²)` in the worst case.
- Hash tables provide expected `O(1)` lookup under suitable assumptions.
- Hash-table operations can degrade to `O(n)` in the worst case.
- Array indexing is typically `O(1)`.
- Linked-list indexed access is `O(n)`.
- Dynamic-array append is `O(1)` amortized.
- Amortized analysis is different from average-case analysis.
- Repeated searches can justify preprocessing through sorting or indexing.
- Edge cases and input characteristics can affect actual behavior.
- Worst-case complexity should be considered when handling untrusted input.
- Asymptotic complexity is an important tool, but real performance also depends on implementation, hardware, memory behavior, and workload.
