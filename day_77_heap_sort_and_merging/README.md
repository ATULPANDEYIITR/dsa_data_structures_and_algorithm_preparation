# Heap Sort and Merging

## 1. Problem Domain

Heap sort and merging are fundamental algorithms for ordering data and consolidating multiple ordered datasets.

This implementation covers three related but distinct operations:

- Heap sort: sorts an unsorted collection using a binary heap.
- Merge K sorted lists: combines multiple independently sorted sequences into one sorted sequence.
- Multiway merging: generalizes merging to multiple input streams, including balanced pairwise merging and external-style sorting.

The implementations use Python, JavaScript, C++17, Java 17, and PostgreSQL. Each language provides a different perspective on algorithm execution, memory management, coordination, validation, and persistence.

## 2. Heap Data Structure

A binary heap is a complete binary tree satisfying a heap-order property.

A complete binary tree fills every level except possibly the last, which is filled from left to right.

Two principal heap types are:

| Heap | Property | Typical use |
|---|---|---|
| Max heap | Parent is greater than or equal to its children | Heap sort |
| Min heap | Parent is less than or equal to its children | K-way merging |

A heap is commonly represented by an array rather than explicit tree nodes.

For a zero-based array:

| Node | Index |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

The array representation provides compact storage and constant-time access to the root.

### Heap operations

**Insertion**

An element is appended to the end of the heap. It is repeatedly exchanged with its parent until the heap property is restored.

**Extraction**

The root is removed, the final element is moved to the root position, and the heap is restored through downward adjustment.

**Sift-down**

Sift-down compares a parent with its children and exchanges it with the appropriate child until the heap property is satisfied.

**Sift-up**

Sift-up moves a newly inserted element towards the root while it violates the heap property.

## 3. Heap Sort

Heap sort uses a max heap to produce ascending order.

### Execution workflow

1. Receive an unsorted array.
2. Construct a max heap.
3. Exchange the root with the final element.
4. Reduce the active heap size.
5. Restore the max-heap property.
6. Repeat until the remaining heap contains one element.

The maximum element is placed into its final position during each extraction.

The algorithm sorts the input copy in the Python, JavaScript, and Java implementations. The C++ implementation also accepts its input by value, preserving the caller's original vector.

### Heap construction

Bottom-up heap construction begins with the last internal node and processes nodes in reverse order.

Leaves already satisfy the heap property because they have no children.

Bottom-up construction requires O(n) time. This is more efficient than inserting all elements individually, which requires O(n log n) time in the worst case.

### Complexity

| Operation | Time complexity |
|---|---:|
| Build max heap | O(n) |
| Extract maximum | O(log n) |
| Complete heap sort | O(n log n) |
| Additional algorithmic space | O(1) for in-place array sorting |

The implementations use iterative sift-down operations to avoid recursive call overhead.

Heap sort provides predictable O(n log n) worst-case running time.

It is not a stable sorting algorithm. Equal elements are not guaranteed to retain their original relative order.

## 4. Merge Two Sorted Lists

Merging two sorted lists is the basic operation used by several merging algorithms.

Consider:

- Left: `[1, 4, 7, 10]`
- Right: `[2, 5, 8, 11]`

The algorithm maintains two positions:

- `i` identifies the current element in the left list.
- `j` identifies the current element in the right list.

At each iteration, the smaller current element is appended to the result.

When one list is exhausted, the remaining elements of the other list are appended.

The process never needs to compare elements that have already been processed.

**Complexity**

For input lengths n and m:

- Time: O(n + m)
- Output space: O(n + m)

The comparison uses `<=` to select the left element when values are equal. This preserves stability between the two input sequences.

## 5. Merge K Sorted Lists

K-way merging combines K sorted sequences into one sorted result.

Each sequence is independently ordered before merging begins.

For example:

| Source | Sorted elements |
|---|---|
| A | 1, 4, 7, 10 |
| B | 2, 5, 8, 11 |
| C | 3, 6, 9, 12 |
| D | 0, 13, 15 |

The expected result is:

`[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]`

### Min-heap approach

A min heap contains the smallest unprocessed element from each nonempty source.

Each heap entry contains:

| Field | Purpose |
|---|---|
| Value | Current candidate value |
| Source index | Identifies the originating sequence |
| Element index | Identifies the element's position |

The algorithm follows this sequence:

1. Insert the first element of every nonempty list.
2. Extract the smallest element.
3. Append it to the output.
4. Identify the source from which it originated.
5. Insert the next element from that source, if available.
6. Repeat until the heap is empty.

Only one element from each active source needs to be stored in the heap.

This reduces auxiliary heap storage compared with inserting every input element.

### Complexity

Let:

- K represent the number of input lists.
- N represent the total number of elements.

| Operation | Complexity |
|---|---|
| Initial heap construction by insertion | O(K log K) |
| Each extraction | O(log K) |
| Each subsequent insertion | O(log K) |
| Complete merge | O(N log K) |
| Heap storage | O(K) |
| Output storage | O(N) |

For K = 1, the operation simply returns the original sorted sequence as the merged result.

Empty lists do not require heap entries.

Duplicate and negative values are supported.

### Deterministic tie-breaking

The implementations use source and element positions to break ties between equal values.

This makes output ordering deterministic for a fixed source order.

The numeric result remains correct regardless of the ordering of equal values.

## 6. Multiway Merging

Multiway merging is a broader approach to combining several ordered runs.

Two strategies are implemented.

### 6.1 Heap-based multiway merging

Heap-based merging maintains one active candidate from each source.

It is particularly useful when:

- Many sorted sources must be consolidated.
- Source lengths are different.
- Data arrives from independent producers.
- Only a small portion of each source needs to remain active in memory.

Its principal advantage is that it does not repeatedly merge large intermediate arrays.

For N total elements and K sources, the time complexity is O(N log K).

### 6.2 Balanced pairwise merging

Pairwise merging repeatedly combines two sorted sequences.

For K input lists, the process creates successive rounds.

Example:

| Round | Active sequences |
|---|---|
| Initial | A, B, C, D |
| First | AB, CD |
| Second | ABCD |

If the number of lists is odd, the unpaired list proceeds to the next round.

A balanced merge tree avoids the excessive repeated work associated with merging one large sequence with one small sequence in a sequential chain.

For approximately balanced input sequences, its total work is O(N log K).

The JavaScript, Python, C++, and Java implementations use this approach as an alternative to heap-based merging.

### Strategy comparison

| Criterion | Heap merging | Pairwise merging |
|---|---|---|
| Main structure | Min heap | Balanced merge rounds |
| Active candidates | One per source | Intermediate merged sequences |
| Output construction | Incremental | Round-based |
| Time | O(N log K) | O(N log K) for balanced rounds |
| Auxiliary memory | O(K), excluding output | Depends on intermediate arrays |
| Typical application | Multiple independent streams | Batch consolidation |

Heap merging is generally suitable when memory efficiency and incremental source consumption are important.

Pairwise merging is useful when intermediate runs are already available and merging can be organized into balanced stages.

## 7. External-Style Sorting

External sorting addresses situations where the complete dataset cannot conveniently be sorted in memory at once.

The Python, JavaScript, and C++ implementations demonstrate a chunk-based workflow.

The procedure is:

1. Divide the input into bounded chunks.
2. Sort each chunk independently.
3. Treat each sorted chunk as an independent source.
4. Merge the sorted chunks using a min heap.
5. Produce the final ordered sequence.

For a chunk size of 1,000 elements, each individual sorting operation processes at most 1,000 elements.

The final merge maintains one active element per chunk.

### Practical distinction

The supplied external-style implementations retain sorted chunks in application memory. They demonstrate the external sorting algorithm's run-generation and merge stages, but they are not complete disk-streaming implementations.

A production external sorter would write sorted runs to separate files and use buffered file readers to merge them without loading every run into memory.

Its storage requirements, file descriptors, buffering, I/O scheduling, and failure recovery would need separate management.

## 8. Python Implementation

The Python script provides a self-contained algorithm and benchmarking environment.

### Main components

| Component | Responsibility |
|---|---|
| `MergeStrategy` | Selects the merging algorithm |
| `MergeStatistics` | Stores execution measurements |
| `MergeResult` | Combines output and statistics |
| `HeapAlgorithms` | Implements sorting and merging |

The implementation uses:

- Lists for arrays and sorted sources.
- Tuples for heap entries.
- `heapq` for priority queue operations.
- Dataclasses for structured results.
- Enums for strategy selection.
- Type hints for interface clarity.
- Exceptions for invalid input handling.
- JSON serialization for result persistence.
- `time.perf_counter()` for performance measurements.

The custom heap sort uses iterative sift-down.

The multiway merge uses Python's standard-library min heap.

The pairwise implementation creates balanced merge rounds.

The benchmark compares the custom heap sort with Python's built-in sorting implementation. This provides a practical performance reference rather than assuming that a hand-written algorithm is faster than an optimized library implementation.

The script also checks correctness using assertions.

## 9. JavaScript Implementation

The JavaScript implementation uses Node.js standard-library features and an explicit min-heap class.

### Main components

| Component | Responsibility |
|---|---|
| `MinHeap` | Generic priority queue |
| `HeapAlgorithms` | Sorting and merging algorithms |
| `MergeCoordinator` | Coordinates independent data sources |
| `externalStyleMerge` | Performs asynchronous chunk processing |
| `saveJSON` | Persists the final result |

The heap comparator supports deterministic ordering through value, source index, and element index.

`Map` is used to associate source identifiers with sorted arrays.

`EventEmitter` exposes source registration and merge-completion events.

The coordinator rejects duplicate source identifiers, unexpected additional sources, and registrations after completion.

The asynchronous chunk workflow periodically yields to the Node.js event loop using `setImmediate`.

This prevents long synchronous chunk-processing sequences from monopolizing the event loop.

It does not make CPU-intensive heap operations parallel. Parallel computation would require worker threads or separate processes.

The result exporter writes to a temporary file before renaming it to the destination.

## 10. C++17 Implementation

The C++ program emphasizes explicit data ownership, standard-library containers, and predictable algorithm behavior.

### Main components

| Component | Responsibility |
|---|---|
| `MergeStatistics` | Execution measurements |
| `MergeResult` | Output and metrics |
| `HeapAlgorithms` | Heap sort and merging |
| `RepositoryMergeEngine` | Multi-source registration and finalization |

The min heap uses `std::priority_queue` with `std::greater`.

A tuple stores the value, source index, and element position.

The pairwise implementation transfers intermediate vectors using move semantics where appropriate.

This avoids unnecessary copying of large intermediate collections.

`std::is_sorted` validates source ordering before merging.

The coordination engine maintains a registration flag for each source.

Finalization is permitted only after all expected sources have registered successfully.

The implementation rejects:

- Invalid source identifiers.
- Duplicate registrations.
- Unsorted input.
- Incomplete source registration.
- Repeated finalization.

The standard library provides dynamic arrays, sorting utilities, priority queues, random-number generation, timing, and input/output functionality without third-party dependencies.

## 11. Java 17 Implementation

The Java implementation models merging as an enterprise-oriented service operation.

It separates algorithm execution from source registration, policy enforcement, event reporting, and result export.

### Domain types

| Type | Responsibility |
|---|---|
| `Source` | Immutable source information |
| `MergePolicy` | Operational limits and validation rules |
| `MergeStatistics` | Execution measurements |
| `MergeResult` | Immutable result |
| `MergeEvent` | Operation-state notification |
| `OperationStatus` | Lifecycle state |
| `MergeStrategy` | Algorithm selection |

Java records provide immutable domain representations.

The `MergeService` manages the operation lifecycle.

Its policy checks include:

- Maximum number of sources.
- Maximum number of elements.
- Source identifier uniqueness.
- Sorted input requirements.
- Terminal operation states.

The service uses observers to publish operational events.

Observer failures are isolated so that a reporting failure does not invalidate a successful merge.

The heap algorithm uses `PriorityQueue` with a comparator based on the value and source position.

The pairwise algorithm uses successive merge rounds.

`ResultExporter` writes results to a temporary file and attempts atomic replacement.

This supports safer result publication when an existing output file is being replaced.

## 12. PostgreSQL Implementation

The SQL implementation provides a relational representation of sorting and merging operations.

It includes persistent source data, execution history, working structures, database-side validation, and reporting.

### Relational model

The principal relationships are:

- One merge job can contain multiple sources.
- One source can contain multiple elements.
- One job can have multiple executions.
- One execution can contain multiple result elements.

The relational structure is:

`merge_jobs → merge_sources → source_elements`

`merge_jobs → merge_executions → merge_results`

### Tables

| Table | Purpose |
|---|---|
| `merge_jobs` | Stores merge operations and lifecycle states |
| `merge_sources` | Registers individual sorted sequences |
| `source_elements` | Stores ordered source values |
| `merge_executions` | Records algorithm execution |
| `merge_results` | Stores final merged values |

### Integrity controls

Primary keys identify persistent records.

Foreign keys enforce relationships between jobs, sources, executions, and results.

Unique constraints prevent duplicate source positions and duplicate element positions within a source.

Check constraints enforce positive limits and nonnegative positions.

Indexes support retrieval by job, source, element position, execution, and result value.

### Source ordering

The `validate_source_element` trigger checks neighboring positions before accepting an insertion or update.

An element cannot violate ascending order relative to its immediate predecessor or successor.

The source counter trigger maintains the number of stored elements.

The validation function also compares maintained counts with actual element counts before execution.

These checks protect the integrity of the input sequences.

### Database-side heap operations

The temporary `merge_heap_work` table represents an indexed min heap.

Each entry contains:

- Heap position.
- Element value.
- Source identifier.
- Source element position.

`heap_push` performs upward adjustment.

`heap_pop` extracts the root and restores the min-heap property through downward adjustment.

The `execute_heap_merge` function initializes the heap with the first element of every source and repeatedly extracts the minimum.

The next element from the extracted element's source is inserted when available.

This implements K-way merging within PostgreSQL.

### Pairwise execution

`execute_pairwise_merge` stores sorted runs as arrays.

Each round combines adjacent runs and carries forward an unpaired run.

The procedure records the final output in `merge_results`.

The SQL pairwise implementation uses array concatenation and sorting during intermediate rounds. It demonstrates the strategy but is not equivalent to an optimized linear two-pointer merge for every intermediate pair.

### Transactions and failure handling

The example includes transactional execution and deliberate invalid input.

The invalid insertion violates source ordering and is rolled back inside an exception-handling block.

Job state transitions are enforced through a trigger.

Completed and failed jobs are treated as terminal states.

Execution errors are recorded in `error_message` before being propagated.

A production deployment should use an appropriate transaction boundary and consider concurrency control for simultaneous executions against the same job.

### Reporting

The reporting views expose:

- Job-level source counts.
- Total input elements.
- Validated source counts.
- Execution durations.
- Algorithm selection.
- Result ordering validation.

The aggregation queries compare recorded performance by merge strategy.

## 13. Distinctions Between the Five Implementations

| Dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Heap sort | Custom | Custom | Custom | Custom | Not required for merge execution |
| K-way merge | `heapq` | Custom min heap | `priority_queue` | `PriorityQueue` | PL/pgSQL heap |
| Pairwise merge | Yes | Yes | Yes | Yes | Yes |
| Source coordination | Function-based | Event-driven | Registration engine | Service and observers | Relational records |
| Validation | Exceptions | Type and range checks | STL checks | Policy and domain validation | Constraints and triggers |
| Persistence | JSON | JSON | Standard output | Text export | Relational tables |

The implementations share algorithmic principles but differ in operational design.

Python emphasizes algorithm experimentation.

JavaScript emphasizes asynchronous coordination and events.

C++ emphasizes efficient container operations and explicit state management.

Java emphasizes domain modeling and service-level policy enforcement.

PostgreSQL emphasizes persistent integrity, execution history, and database-side processing.

## 14. Validation and Edge Cases

The implementations include the following test conditions:

| Case | Expected behavior |
|---|---|
| Empty input | Return an empty sequence |
| One element | Return the element unchanged |
| One sorted source | Preserve its values |
| Empty source | Ignore it during heap initialization |
| Multiple empty sources | Return an empty result |
| Duplicate values | Preserve every occurrence |
| Negative values | Sort in ascending numeric order |
| Unequal source lengths | Continue until all sources are exhausted |
| Unsorted source | Reject the operation |
| Duplicate source identifier | Reject registration |
| Incomplete source registration | Prevent finalization |
| Repeated finalization | Reject the operation |
| Invalid chunk size | Reject the operation |
| Excessive input size | Enforce configured limits |

A central correctness condition is element conservation.

For an input containing N elements, the merged output must contain exactly N elements.

Another condition is monotonic ordering:

`output[i] <= output[i + 1]`

for every valid adjacent pair.

These invariants are checked directly or through assertions and database reporting.

## 15. Performance and Memory Considerations

Heap-based merging requires only one active candidate per nonempty source.

For K sources and N elements, the principal computational cost is O(N log K).

The heap size remains bounded by K.

The output itself requires O(N) memory when the complete result is materialized.

For extremely large datasets, output streaming is preferable to storing the entire result.

Heap sort has predictable O(n log n) time and O(1) auxiliary algorithmic space when operating on a mutable array.

Pairwise merging requires intermediate storage. Its actual memory consumption depends on the number and size of active runs and how intermediate results are represented.

Performance comparisons must consider more than asymptotic complexity.

Relevant factors include:

- Cache locality.
- Memory allocation.
- Heap implementation.
- Input distribution.
- Number of source lists.
- Source length imbalance.
- Database indexing.
- Disk I/O.
- Serialization overhead.
- Thread scheduling.

The Python and JavaScript implementations prioritize clarity and correctness.

The C++ implementation benefits from STL container and move-operation support.

The Java implementation emphasizes immutable interfaces and explicit service boundaries.

The PostgreSQL implementation demonstrates database-side execution, although its row-level working-table heap operations introduce database overhead that would not occur in an optimized in-memory heap.

## 16. Security and Operational Considerations

Heap algorithms are not inherently security controls. Their surrounding data-processing workflows require appropriate safeguards.

Important considerations include:

- Validate source identifiers before registration.
- Enforce input-size limits.
- Reject malformed or unsorted sources.
- Avoid accepting untrusted filesystem destinations.
- Restrict database permissions for execution functions.
- Protect persistent source and result records.
- Avoid exposing sensitive input values through logs.
- Use controlled transaction boundaries.
- Monitor failed and long-running jobs.
- Prevent unauthorized concurrent modification of active source data.

The supplied examples use local output files and synthetic records.

A production service would also require authentication, authorization, resource quotas, observability, durable job recovery, and controlled retention policies.

## 17. Limitations

The implementations are educational, executable algorithmic models rather than complete distributed data-processing platforms.

Specific limitations include:

- The Python, JavaScript, C++, and Java external-style examples retain sorted runs in memory.
- The JavaScript asynchronous implementation yields to the event loop but does not provide parallel CPU execution.
- The C++ coordination model is synchronous.
- The Java service uses in-process state rather than distributed coordination.
- The PostgreSQL heap implementation uses temporary relational structures and incurs database execution overhead.
- The PostgreSQL pairwise implementation sorts concatenated arrays rather than implementing a specialized linear-time merge for each pair.
- Performance measurements depend on hardware, runtime, data size, and system load.

These limitations distinguish algorithmic demonstrations from production-grade streaming, distributed, or persistent processing systems.
