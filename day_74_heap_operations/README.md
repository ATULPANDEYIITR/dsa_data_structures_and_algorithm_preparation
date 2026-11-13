# Heap Operations: Insert, Extract Minimum, Extract Maximum and Heapify

## Project Description

This project implements binary heap operations through five different programming and database perspectives.

It covers the construction, maintenance, validation, and application of binary heaps, with particular attention to minimum heaps, maximum heaps, priority scheduling, and complexity analysis.

The central operations are:

- Insert: Add an element while maintaining the heap property.
- Extract Minimum: Remove and return the smallest element.
- Extract Maximum: Remove and return the largest element.
- Heapify: Convert an unordered collection into a valid heap.

The implementations use executable examples, input validation, exception handling, state management, and practical scheduling scenarios.

## 1. Binary Heap Fundamentals

A binary heap is a complete binary tree that satisfies a specific ordering condition.

A complete binary tree has the following properties:

- Every level is completely filled except possibly the last.
- The last level is filled from left to right.
- Each node has at most two children.

A binary heap is generally stored in an array rather than through explicit tree nodes.

### Array Representation

For an array using zero-based indexing, the relationships are:

| Relationship | Formula |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

Example input:

`[45, 12, 30, 8, 25, 60, 18]`

A valid minimum heap can be represented as:

        8
       / \
      12  18
     / \  / \
    45 25 60 30

Array representation:

`[8, 12, 18, 45, 25, 60, 30]`

The array representation avoids the memory overhead of separate tree-node objects and provides efficient parent and child access.

## 2. Minimum Heap and Maximum Heap

### Minimum Heap

In a minimum heap, every parent must be smaller than or equal to its children.

The root always contains the smallest element.

For every parent-child relationship:

`parent <= child`

Applications include:

- Task scheduling.
- Shortest-path algorithms.
- Event simulation.
- Priority-based processing.
- Finding the smallest available element.

### Maximum Heap

In a maximum heap, every parent must be greater than or equal to its children.

The root always contains the largest element.

For every parent-child relationship:

`parent >= child`

Applications include:

- Highest-priority task selection.
- Top-K problems.
- Maximum-value extraction.
- Resource allocation.
- Ranking systems.

### Important Distinction

A heap is not a fully sorted array.

Only the parent-child ordering is guaranteed. Elements in different subtrees do not necessarily have a globally sorted relationship.

This property is what makes heap insertion and extraction efficient.

## 3. Insert Operation

Insertion adds a new element at the next available position in the complete binary tree.

The heap property is restored through an operation called sift-up.

### Workflow

1. Insert the new element at the end of the array.
2. Calculate its parent index.
3. Compare the element with its parent.
4. Swap if the heap property is violated.
5. Continue until the root is reached or the property is restored.

Example:

Initial minimum heap:

`[8, 12, 18, 45, 25, 60, 30]`

Insert:

`5`

The new element is initially appended:

`[8, 12, 18, 45, 25, 60, 30, 5]`

It moves upward through its parent relationships.

Final heap:

`[5, 8, 18, 12, 25, 60, 30, 45]`

### Complexity

| Measurement | Complexity |
|---|---|
| Best case | O(1) |
| Average case | O(log n) |
| Worst case | O(log n) |
| Additional space | O(1) |

The worst-case height of a complete binary tree is logarithmic.

## 4. Extract Minimum

Extract Minimum removes the root of a minimum heap.

Because the root contains the smallest element, it can be returned immediately after restoring the remaining structure.

### Workflow

1. Store the root value.
2. Replace the root with the last element.
3. Remove the last array position.
4. Compare the new root with its children.
5. Swap it with the smaller child when necessary.
6. Continue until the heap property is restored.

This downward movement is called sift-down or heapify-down.

Example:

Initial heap:

`[5, 8, 18, 12, 25, 60, 30]`

Extracted element:

`5`

Remaining heap:

`[8, 12, 18, 30, 25, 60]`

### Complexity

| Measurement | Complexity |
|---|---|
| Best case | O(1) |
| Average case | O(log n) |
| Worst case | O(log n) |
| Additional space | O(1) |

The returned root is the minimum element, not necessarily the element at the first position of an originally sorted input.

## 5. Extract Maximum

Extract Maximum is the corresponding operation for a maximum heap.

The root contains the largest element.

### Workflow

1. Store the root.
2. Move the last element to the root.
3. Remove the last position.
4. Compare the root with its children.
5. Swap with the larger child if necessary.
6. Continue until the maximum-heap property is restored.

Example:

Initial maximum heap:

`[90, 70, 85, 20, 10, 45]`

Extracted element:

`90`

The remaining structure is:

`[85, 70, 45, 20, 10]`

### Complexity

| Measurement | Complexity |
|---|---|
| Best case | O(1) |
| Average case | O(log n) |
| Worst case | O(log n) |
| Additional space | O(1) |

Extract Minimum and Extract Maximum normally operate on different heap orderings.

A single ordinary minimum heap does not provide constant-time maximum extraction.

## 6. Heapify

Heapify converts an unordered collection into a valid binary heap.

Two different techniques are important.

### Repeated Insertion

Each element is inserted separately.

For n elements:

`O(n log n)`

This approach is useful when elements arrive incrementally.

### Bottom-Up Heap Construction

Bottom-up heapification starts from the last non-leaf node and processes nodes towards the root.

The last non-leaf node is located at:

`floor(n / 2) - 1`

Leaf nodes already satisfy the heap property because they have no children.

Example:

Unordered collection:

`[45, 12, 30, 8, 25, 60, 18]`

Minimum heap after heapification:

`[8, 12, 18, 45, 25, 60, 30]`

### Why Heapify Is O(n)

A common misconception is that heapify takes O(n log n).

Although an individual sift-down operation can take O(log n), most nodes are close to the leaves and require very little movement.

The total work is proportional to:

`Σ (number of nodes at height h × h)`

This produces a linear bound:

`O(n)`

| Construction method | Complexity |
|---|---|
| Repeated insertion | O(n log n) |
| Bottom-up heapify | O(n) |

Bottom-up heapification is preferable when an entire collection is available before construction.

## 7. Core Algorithm Comparison

| Operation | Minimum heap | Maximum heap |
|---|---|---|
| Insert | O(log n) | O(log n) |
| Peek root | O(1) | O(1) |
| Extract root | O(log n) | O(log n) |
| Heapify | O(n) | O(n) |
| Search arbitrary value | O(n) | O(n) |
| Build sorted output | O(n log n) | O(n log n) |

A heap is designed for efficient priority access, not arbitrary searching.

## 8. Python Implementation

File: `heap_operations.py`

The Python implementation provides a double-ended priority queue.

### Design

It maintains:

- A minimum binary heap.
- A maximum binary heap.
- A frequency counter for logically active values.
- Operation statistics.
- Automatic compaction of stale entries.

The frequency counter allows the implementation to support both minimum and maximum extraction while handling duplicate values.

### Lazy Deletion

Maintaining two independent heaps creates a synchronization problem.

When an element is extracted from one heap, its corresponding entry remains in the other heap.

The implementation solves this through lazy deletion.

Each value has a frequency in a shared counter.

When a value is removed:

1. Its frequency is decreased.
2. The corresponding stale entry remains in the other heap.
3. When that entry reaches the root, it is discarded.
4. Periodic rebuilding controls stale-entry growth.

### Important Characteristics

- Duplicate values are supported.
- Empty extraction raises a custom exception.
- Invalid values are rejected.
- Both heap structures can be validated.
- Randomized tests verify minimum and maximum behavior.

The two-heap design provides amortized logarithmic extraction, excluding occasional rebuilding costs.

A production implementation should also consider synchronization if operations are accessed concurrently.

## 9. JavaScript Implementation

File: `heap_operations.js`

The JavaScript implementation uses Node.js event-driven programming.

### Design

It includes:

- A reusable `BinaryHeap` class.
- A double-ended priority queue.
- JavaScript `Map` for frequency management.
- `EventEmitter` for operation notifications.
- Promise-based batch processing.
- Explicit safe-integer validation.

### Event-Driven Operations

The queue emits events for:

- Insertion.
- Minimum extraction.
- Maximum extraction.
- Heapification.

This separates the data structure from monitoring and reporting logic.

For example, an application can listen for an extraction event and update its task-processing dashboard.

### Asynchronous Batch Processing

The `processBatch()` method executes a sequence of operations in order.

Sequential execution is important because heap operations modify shared state.

Running multiple state-changing operations concurrently without synchronization could produce incorrect results.

The asynchronous interface does not make the underlying heap operations parallel.

## 10. C++17 Implementation

File: `heap_operations.cpp`

The C++ implementation uses explicit binary heap management.

### Design

The `BinaryHeap` class uses:

- `vector<int>` for contiguous storage.
- An enum to distinguish minimum and maximum heaps.
- Sift-up for insertion.
- Sift-down for extraction.
- Bottom-up heapification.
- Exceptions for invalid operations.

### Repository Task Scheduler

A repository task scheduler provides a practical application.

Each task receives a numerical priority.

Two heaps maintain different ordering requirements:

- Maximum heap: retrieves the most urgent task.
- Minimum heap: retrieves the least urgent task.

This implementation uses independent heaps for the two retrieval perspectives. Each heap represents its own task collection and is not automatically synchronized after extraction from the other.

### Memory and Performance

The vector-backed design offers:

- Contiguous memory.
- Low per-element overhead.
- Efficient index calculations.
- Good cache locality.

The implementation uses no third-party dependencies.

## 11. Java 17 Implementation

File: `HeapOperations.java`

The Java implementation models enterprise task scheduling through explicit domain types.

### Domain Model

| Type | Responsibility |
|---|---|
| `Task` | Immutable task representation |
| `TaskState` | Task processing state |
| `HeapType` | Minimum or maximum ordering |
| `BinaryHeap` | Generic heap implementation |
| `TaskScheduler` | Task submission and retrieval |
| `ProcessingResult` | Immutable processing record |

### Generic Heap

The `BinaryHeap<T>` class accepts a comparator.

This allows the same heap implementation to process different object types rather than being limited to integers.

For example, task ordering is determined through:

- Priority.
- Task identifier as a deterministic tie-breaker.

### Enterprise Considerations

The implementation includes:

- Immutable task records.
- Input validation.
- Explicit task states.
- Processing history.
- Heap rebuilding.
- Custom exception handling.
- Heap invariant verification.

The two scheduling heaps are independent collections. A task extracted from one remains present in the other unless the application coordinates their removal.

A production task scheduler should use a shared task registry and atomic state transitions to prevent duplicate processing.

## 12. PostgreSQL Implementation

File: `heap_operations.sql`

The PostgreSQL implementation represents heap nodes relationally.

### Database Architecture

The schema is:

`heap_lab`

Its main tables are:

| Table | Purpose |
|---|---|
| `heap_instances` | Stores heap identity and ordering type |
| `heap_nodes` | Stores values and array positions |
| `heap_operations` | Maintains operation history |

### Relational Representation

Every heap node has:

- Heap identifier.
- Array position.
- Integer value.

The primary key combines heap identifier and position.

This prevents duplicate positions inside the same heap while allowing identical values at different positions.

### Database Operations

The SQL script implements:

- `create_heap()` for heap creation.
- `swap_heap_nodes()` for node exchange.
- `heap_insert()` for insertion.
- `heap_extract()` for root extraction.
- `heapify_values()` for bottom-up construction.
- `heap_integrity_report` for structural validation.
- `heap_roots` for root retrieval.

### Transactional Integrity

The insertion, extraction, and heapification procedures lock the relevant heap record using `FOR UPDATE`.

This serializes modifications to the same heap and prevents concurrent operations from independently modifying its structure.

PostgreSQL transactions ensure that a failed operation can be rolled back without leaving a partially modified heap.

### Database Performance Limitation

The relational implementation prioritizes persistence, integrity, and transaction management.

It is not intended to outperform an in-memory heap.

Its operations involve SQL statements, row locking, index maintenance, and database execution overhead.

The array-backed in-memory implementation generally offers better performance for high-frequency priority operations.

## 13. Complexity Analysis

Let n represent the number of elements in a binary heap.

The height of a complete binary tree is:

`floor(log2(n))`

### Operation Complexity

| Operation | Time complexity | Explanation |
|---|---|---|
| Insert | O(log n) | Element moves towards root |
| Extract Minimum | O(log n) | Root replacement and sift-down |
| Extract Maximum | O(log n) | Root replacement and sift-down |
| Peek Minimum | O(1) | Root access |
| Peek Maximum | O(1) | Root access in max heap |
| Heapify | O(n) | Bottom-up construction |
| Search | O(n) | No global sorting guarantee |
| Heap Sort | O(n log n) | Repeated extraction |

### Space Complexity

| Structure | Space |
|---|---|
| Single binary heap | O(n) |
| Two independent heaps | O(2n), equivalent to O(n) |
| Frequency counter | O(k), where k is distinct values |
| Operation history | O(m), where m is recorded operations |

### Best, Average and Worst Cases

Insertion can finish immediately if the new element already satisfies the parent ordering condition.

Its best-case time is O(1).

In the worst case, the element moves from a leaf to the root, requiring O(log n) comparisons and swaps.

Extraction performs downward adjustment.

Its worst-case complexity is O(log n).

Bottom-up heapification takes O(n), including when the input is initially in reverse order.

## 14. Heap Sort

Heap sort uses a heap to arrange elements in sorted order.

The standard algorithm:

1. Build a heap.
2. Extract the root.
3. Restore heap order.
4. Repeat until the heap becomes empty.

With a minimum heap, repeated extraction produces ascending order.

With a maximum heap, repeated extraction produces descending order.

| Property | Heap Sort |
|---|---|
| Best-case time | O(n log n) |
| Average-case time | O(n log n) |
| Worst-case time | O(n log n) |
| Auxiliary space | O(n) for a separate heap |
| Stability | Not stable |

An in-place heap sort can achieve O(1) auxiliary space, excluding the input array.

## 15. Edge Cases and Failure Handling

The implementations consider several operational conditions.

| Edge case | Expected behavior |
|---|---|
| Empty heap extraction | Raise an error |
| Single-element extraction | Return element and empty heap |
| Duplicate elements | Preserve multiplicity |
| Negative values | Support valid integer values |
| Already ordered input | Heapify successfully |
| Reverse-ordered input | Heapify successfully |
| Invalid priority | Reject input |
| Invalid heap type | Reject configuration |
| Large input | Preserve logarithmic update operations |
| Invalid internal ordering | Detect through validation |

Duplicate values require particular attention.

A frequency counter or stable element identifier may be necessary when multiple heaps represent the same logical collection.

## 16. Security and Production Considerations

Although heaps are primarily algorithmic data structures, production use requires additional controls.

### Input Validation

- Reject invalid numeric values.
- Restrict priority ranges where required.
- Avoid accepting arbitrary objects as comparable values.
- Validate input sizes before allocating large structures.

### Concurrency

A heap is mutable state.

Concurrent insertion and extraction require synchronization.

For persistent database heaps, row locking and transactions provide an integrity mechanism.

For in-memory implementations, appropriate locks or serialized operation queues may be necessary.

### Memory Management

Lazy deletion can retain stale entries.

Periodic rebuilding limits this growth.

A production implementation should monitor:

- Logical element count.
- Physical heap size.
- Rebuild frequency.
- Extraction latency.
- Memory consumption.

### Deterministic Ordering

When multiple tasks have identical priorities, a secondary key such as task identifier or insertion sequence can provide deterministic ordering.

This is particularly important in enterprise scheduling systems.

### Failure Recovery

Database-backed implementations should use transactions and rollback.

In-memory implementations should validate inputs before changing their structures and avoid exposing internal mutable arrays.

## 17. Practical Applications

| Application | Heap type | Purpose |
|---|---|---|
| Operating system scheduling | Min/max | Priority-based task selection |
| Dijkstra's algorithm | Min | Select smallest tentative distance |
| Event simulation | Min | Process earliest event |
| Top-K analysis | Min/max | Maintain selected values |
| Emergency task processing | Max | Retrieve highest priority |
| Streaming statistics | Two heaps | Maintain lower and upper partitions |
| Job scheduling | Min/max | Manage execution priorities |
| Heap Sort | Min/max | Produce ordered output |

A double-ended priority queue is particularly useful when an application needs access to both the smallest and largest active elements.

## 18. Complexity Comparison Across Implementations

| Implementation | Heap representation | Special capability |
|---|---|---|
| Python | Two binary heaps and frequency counter | Lazy deletion and compaction |
| JavaScript | Two binary heaps and Map | Event-driven operations |
| C++17 | Vector-backed binary heaps | Explicit low-overhead implementation |
| Java 17 | Generic comparator-based heaps | Enterprise task domain model |
| PostgreSQL | Relational nodes and positions | Transactional persistence |

The implementations intentionally use different engineering approaches while preserving the fundamental binary heap properties.

## 19. Verification Checklist

The following conditions define a valid implementation:

- Every parent satisfies the selected heap ordering rule.
- Every insertion preserves completeness.
- Every extraction removes the root.
- Every extraction restores heap ordering.
- Heapify processes all internal nodes.
- Duplicate values remain correctly represented.
- Empty extraction is handled explicitly.
- Minimum and maximum ordering are not confused.
- Database modifications preserve valid node positions.
- Complexity claims match the implemented algorithms.

The essential distinction is that a binary heap maintains partial ordering, allowing efficient priority access without maintaining a completely sorted collection.
