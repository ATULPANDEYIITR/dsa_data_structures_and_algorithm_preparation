# Heap Fundamentals

## 1. Heap Data Structure

A heap is a specialized tree-based data structure that maintains a priority relationship between parent nodes and their children.

A binary heap is a complete binary tree. It is commonly implemented using an array rather than individually allocated tree nodes.

The two fundamental binary heap variants are:

- **Min heap:** Every parent is less than or equal to its children. The minimum element occupies the root.
- **Max heap:** Every parent is greater than or equal to its children. The maximum element occupies the root.

A heap does not maintain complete sorted order. Its guarantee concerns the relationship between each parent and its immediate children.

## 2. Complete Binary Tree

A complete binary tree satisfies two structural conditions:

1. Every level except possibly the last is completely filled.
2. Nodes at the last level occupy positions from left to right without gaps.

Example:

    Complete binary tree:

                 10
               /    \
             20      30
            /  \    /  \
           40  50  60   70

An incomplete structure:

                 10
               /    \
             20      30
               \
                50

The second structure is not complete because a position is missing before another node.

Completeness is important because it allows a binary heap to use contiguous array positions without storing explicit pointers.

## 3. Min Heap

A min heap maintains the following invariant:

    Parent <= Left Child
    Parent <= Right Child

Example:

                 10
               /    \
             20      15
            /  \    /
           50  30  40

Array representation:

    [10, 20, 15, 50, 30, 40]

The root contains the minimum value.

The entire array is not necessarily sorted. For example, the relationship between the value at index 1 and the value at index 2 is not constrained beyond their relationship with the root.

### Min heap applications

- Task scheduling by smallest priority value.
- Finding the smallest element repeatedly.
- Dijkstra's shortest-path algorithm.
- Event simulation.
- Finding the k smallest elements.
- Priority-based resource allocation.

## 4. Max Heap

A max heap maintains the opposite invariant:

    Parent >= Left Child
    Parent >= Right Child

Example:

                 90
               /    \
             70      80
            /  \    /
           40  50  60

Array representation:

    [90, 70, 80, 40, 50, 60]

The root contains the maximum value.

### Max heap applications

- Finding the largest elements.
- Highest-priority job scheduling.
- Finding the k largest elements.
- Heap sort in ascending order.
- Resource allocation based on maximum priority.

## 5. Parent-Child Relationships

For an array-backed binary heap, the position of every node determines its parent and children.

The Python, JavaScript, C++, and Java implementations use zero-based indexing.

| Relationship | Formula |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

For a node at index `3`:

- Parent index = `(3 - 1) // 2 = 1`
- Left child index = `2 * 3 + 1 = 7`
- Right child index = `2 * 3 + 2 = 8`

Example:

    Array: [10, 20, 15, 50, 30, 40]

    Index:   0   1   2   3   4   5
    Value:  10  20  15  50  30  40

                 10 (0)
                /      \
           20 (1)      15 (2)
           /   \       /
        50(3) 30(4) 40(5)

For PostgreSQL, the implementation uses one-based positions.

| Relationship | Formula |
|---|---|
| Parent | `i / 2` |
| Left child | `2 * i` |
| Right child | `2 * i + 1` |

Index calculations must always account for the indexing convention of the implementation.

## 6. Array Representation

A binary heap can be represented by a contiguous array.

The array stores nodes in level-order traversal:

1. Root.
2. Left and right children of the root.
3. Nodes on the next level, from left to right.
4. Remaining levels in the same order.

Example:

    Tree:

                 10
               /    \
             20      15
            /  \    /  \
           50  30  40  60

    Array:

    [10, 20, 15, 50, 30, 40, 60]

This representation has several advantages:

- No explicit node pointers.
- No separate parent references.
- Efficient index calculations.
- Good memory locality.
- No memory allocation for individual tree nodes.

The complete-tree property guarantees that the array has no gaps between occupied positions.

## 7. Heap Operations

### 7.1 Insertion

Insertion adds a new element at the end of the array.

The heap then restores its ordering property using sift-up, also called bubble-up or percolate-up.

Example:

    Initial min heap:

                 10
               /    \
             20      15

    Insert 5:

                 10
               /    \
             20      15
            /
           5

    Compare 5 with 20 and swap:

                 10
               /    \
              5      15
             /
            20

    Compare 5 with 10 and swap:

                  5
                /   \
              10     15
             /
            20

The resulting heap satisfies the min-heap property.

### 7.2 Peek

Peek returns the root without modifying the heap.

- Min heap: returns the minimum.
- Max heap: returns the maximum.

Its time complexity is `O(1)`.

### 7.3 Extraction

Extraction removes the root.

The process is:

1. Store the root value.
2. Move the last array element to the root.
3. Remove the last array position.
4. Restore heap ordering using sift-down.

Example:

    Initial min heap:

                 5
               /   \
             10     15
            /  \
           20  30

    Remove 5.

    Move 30 to the root:

                 30
               /    \
             10      15
            /
           20

    Restore heap order:

                 10
               /    \
             20      15
            /
           30

The resulting root is the new minimum.

### 7.4 Heapify

Heapify converts an unordered array into a valid heap.

The implementations use bottom-up construction:

- Start at the last internal node.
- Apply sift-down.
- Move toward the root.
- Finish after processing the root.

The last internal node in a zero-based array of length `n` is:

`n // 2 - 1`

Bottom-up heap construction takes `O(n)` time.

This is more efficient than repeatedly inserting all elements, which can require `O(n log n)` time.

## 8. Sift-Up and Sift-Down

| Mechanism | Purpose | Direction |
|---|---|---|
| Sift-up | Restore order after insertion | Child to parent |
| Sift-down | Restore order after root replacement | Parent to child |
| Heapify | Construct a heap from an unordered array | Bottom-up |

Both sift operations require at most the height of the tree.

A complete binary tree containing `n` nodes has height `O(log n)`.

## 9. Complexity Analysis

| Operation | Time Complexity |
|---|---:|
| Access root | O(1) |
| Insert | O(log n) |
| Extract root | O(log n) |
| Sift-up | O(log n) |
| Sift-down | O(log n) |
| Build heap | O(n) |
| Validate heap | O(n) |
| Heap sort | O(n log n) |
| Search arbitrary value | O(n) |

Space complexity:

- Array-backed heap storage: `O(n)`.
- Insertion: `O(1)` auxiliary space.
- Extraction: `O(1)` auxiliary space for iterative implementations.
- Heap construction: `O(1)` auxiliary space beyond the stored array, excluding input copying.

A heap is not a binary search tree. Searching for an arbitrary value does not generally achieve logarithmic time.

## 10. Python Implementation

The Python implementation provides a generic `BinaryHeap` class.

### Implemented mechanisms

- `HeapType` enum distinguishes min and max ordering.
- `BinaryHeap` stores values in a Python list.
- `parent`, `left_child`, and `right_child` calculate array relationships.
- `push` inserts values.
- `pop` extracts the root.
- `heapify` performs bottom-up construction.
- `validate` verifies heap ordering.
- `levels` groups elements by tree level.
- `tree_relationships` displays parent-child relationships.
- `sorted_values` extracts from a copied heap.

The implementation also demonstrates Python's standard-library `heapq` module and heap-based sorting.

The custom implementation is useful for understanding internal operations. The standard library is preferable for ordinary application priority queues.

Assertions verify structural correctness, including randomized extraction tests.

## 11. JavaScript Implementation

The JavaScript implementation uses an event-driven job scheduler.

It demonstrates how heaps support asynchronous workload management.

### Implemented mechanisms

- `PriorityHeap` implements min and max heap behavior.
- `Map`-like object records represent structured jobs.
- A `Set` tracks completed job identifiers.
- `EventEmitter` publishes scheduling events.
- Promises and `async/await` support asynchronous job execution.
- Stable sequence numbers resolve equal-priority ordering.
- Failed jobs are recorded without terminating the entire processing cycle.

The scheduler uses a max heap so higher numerical priorities execute first.

The heap itself remains responsible for priority ordering. Event handling and job execution are separate responsibilities.

This separation is important in event-driven systems because scheduling and execution are different operations.

## 12. C++17 Implementation

The C++ implementation models an operations workload using an array-backed priority queue.

### Implemented mechanisms

- `Job` struct represents individual workloads.
- `HeapMode` distinguishes min and max ordering.
- `BinaryHeap` encapsulates the internal array.
- STL `vector` stores elements.
- STL algorithms support swapping and sorting-related operations.
- Exceptions represent invalid operations and empty-heap access.
- `validate` checks the heap invariant.

The heap supports construction from an existing collection, insertion, extraction, root inspection, and sorted extraction.

The comparator uses job identifiers to provide deterministic ordering when priorities are equal.

The implementation uses a copied heap for sorted extraction so the original data structure remains unchanged.

## 13. Java 17 Implementation

The Java implementation models enterprise job processing.

### Implemented mechanisms

- Records represent immutable jobs and processing results.
- Enums represent heap modes and job states.
- Generic `BinaryHeap` supports reusable heap operations.
- Comparator objects define priority ordering.
- `JobService` separates business operations from heap mechanics.
- Collections maintain job history and identifier uniqueness.
- Streams aggregate processing outcomes.

The enterprise workflow uses the following state transitions:

    QUEUED
       |
       v
    RUNNING
       |
       +----------> COMPLETED
       |
       +----------> FAILED

A failed job is recorded as failed rather than being silently treated as completed.

The implementation distinguishes the data structure from the service responsible for workload execution.

Java's standard `PriorityQueue` is also available for production use when custom internal heap behavior is unnecessary.

## 14. PostgreSQL Implementation

The PostgreSQL implementation models binary heaps using relational tables.

### Database entities

| Entity | Responsibility |
|---|---|
| `heaps` | Stores heap identity and ordering mode |
| `heap_nodes` | Stores array positions and node values |
| `heap_operations` | Records build, insertion, and extraction events |
| `heap_relationships` | Exposes parent-child relationships |
| `heap_summary` | Provides heap-level statistics |

### Relational representation

Each heap node has:

- A heap identifier.
- A one-based array position.
- An integer value.

The primary key `(heap_id, position)` prevents duplicate positions within a heap.

The relationship view uses self-joins to retrieve parents and children.

### Database functions and procedures

| Routine | Purpose |
|---|---|
| `create_heap` | Creates a min or max heap |
| `higher_priority` | Evaluates ordering |
| `swap_nodes` | Exchanges node values |
| `sift_up` | Restores ordering after insertion |
| `sift_down` | Restores ordering after extraction |
| `validate_heap` | Checks structural and ordering invariants |
| `heap_insert` | Inserts a value |
| `heap_extract` | Removes and returns the root |
| `heap_build` | Constructs a heap from an integer array |

Advisory transaction locks serialize modifications to individual heaps. Row locks protect heap metadata, while transactions protect intermediate changes.

The SQL implementation is intended as a learning model. A relational database is not generally the most efficient storage mechanism for a high-frequency in-memory priority queue.

## 15. Min Heap and Max Heap Distinctions

| Characteristic | Min Heap | Max Heap |
|---|---|---|
| Root | Minimum | Maximum |
| Parent-child rule | Parent <= Children | Parent >= Children |
| Sift-up condition | Child is smaller | Child is larger |
| Sift-down selection | Smallest child | Largest child |
| Typical use | Minimum-priority scheduling | Maximum-priority scheduling |

The structural properties of both heaps are identical.

Only the comparison rule changes.

## 16. Heap Sort

Heap sort uses a heap to arrange elements in sorted order.

The process involves:

1. Constructing a heap.
2. Extracting the root repeatedly.
3. Collecting the extracted values.

For ascending output, a min heap can produce elements in increasing order through repeated extraction.

The Python implementation also demonstrates standard-library heap-based extraction.

Heap sort has `O(n log n)` time complexity and does not require the recursive partitioning used by quicksort.

## 17. Edge Cases and Validation

The implementations account for several important conditions:

| Edge case | Expected behavior |
|---|---|
| Empty heap | Extraction raises an error |
| Empty heap peek | Raises an error |
| Single element | Extraction leaves an empty heap |
| Duplicate values | Multiple equal elements remain valid |
| Negative values | Supported |
| Invalid heap mode | Rejected |
| Invalid job identifier | Rejected |
| Negative execution duration | Rejected |
| Failed job execution | Recorded as failed |
| Equal priorities | Deterministic tie-breaking where implemented |

Heap validation checks every node against its existing children.

A heap can be structurally complete while violating its ordering invariant. Both properties must be considered.

## 18. Security and Production Considerations

A heap is a data structure rather than a complete scheduling or authorization system.

Production implementations should consider:

- Validate input values before inserting them.
- Apply queue capacity limits where workload volume is uncontrolled.
- Avoid trusting externally supplied priority values.
- Prevent duplicate job submissions using unique identifiers.
- Record failed and completed operations.
- Protect shared queue modifications through synchronization.
- Use transaction boundaries for persistent heap updates.
- Avoid exposing internal queue structures to untrusted callers.
- Monitor queue size and processing latency.
- Consider starvation when continuously inserting higher-priority jobs.

A basic binary heap does not automatically provide thread safety, persistence, fairness, or distributed coordination.

Those requirements must be handled by the surrounding application architecture.

## 19. Practical Engineering Distinctions

The five implementations demonstrate different uses of the same underlying structure.

| Implementation | Main engineering perspective |
|---|---|
| Python | Algorithm construction and verification |
| JavaScript | Event-driven asynchronous scheduling |
| C++17 | Efficient domain-specific priority queue |
| Java 17 | Enterprise service and state management |
| PostgreSQL | Persistent relational representation and transactional operations |

The central invariant remains consistent:

    For every existing child:
        The parent has at least as much heap priority.

A complete binary tree provides the structural guarantee, while the heap-order property provides the priority guarantee.

Both properties together define a valid binary heap.
