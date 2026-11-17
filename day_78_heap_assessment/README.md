# Heap Assessment: Mixed Heap and Priority Queue Problems

## 1. Technical Scope

This project implements a collection of heap and priority queue problems across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover two related but distinct areas:

- **Heap algorithms:** Efficient selection, ordering, aggregation, and streaming calculations.
- **Priority queue applications:** Processing tasks according to priority, maintaining execution order, and managing queued operations.

A binary heap is a complete binary tree that satisfies a heap-order property.

In a min heap, every parent is less than or equal to its children. In a max heap, every parent is greater than or equal to its children.

The root provides immediate access to the minimum or maximum element, depending on the heap type.

## 2. Heap Fundamentals

### Binary heap structure

A binary heap is commonly represented using an array rather than explicit tree nodes.

For an element at index `i`, using zero-based indexing:

| Relationship | Array index |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

The array representation avoids the memory overhead of separately allocated tree nodes.

### Core operations

| Operation | Time complexity |
|---|---:|
| Access minimum or maximum | O(1) |
| Insert | O(log n) |
| Extract root | O(log n) |
| Build heap using heapify | O(n) |
| Search arbitrary element | O(n) |
| Remove arbitrary element | O(n) without an index structure |
| Heap sort | O(n log n) |

Insertion and extraction restore the heap property using sift-up and sift-down operations.

Heap construction is O(n), rather than O(n log n), when implemented through bottom-up heapification.

### Min heap and max heap

A min heap prioritizes smaller values.

A max heap prioritizes larger values.

Python's `heapq` implements a min heap. A max heap can be represented using negated numeric values.

JavaScript and Java implementations use explicit comparators to establish the required ordering.

C++17 uses `std::priority_queue`, whose default configuration is a max-priority queue.

## 3. Kth Largest and Kth Smallest Elements

The kth largest problem asks for the element occupying position `k` when values are ordered from largest to smallest.

A full sorting solution requires O(n log n) time.

A bounded min heap provides a more efficient approach when `k` is substantially smaller than the input size.

### Algorithm

1. Create an initially empty min heap.
2. Insert each input value.
3. If the heap contains more than `k` elements, remove its smallest element.
4. After processing all values, the root represents the kth largest element.

Complexity:

- Time: O(n log k)
- Auxiliary space: O(k)

The kth smallest problem uses the corresponding bounded max-heap strategy.

The implementations validate the value of `k`, reject invalid inputs, and handle duplicate values correctly.

## 4. Top K Frequent Elements

This problem combines frequency counting with heap-based selection.

A frequency map records how often each distinct value occurs.

The heap then selects the most frequent values without sorting the entire frequency collection.

The implementations use a deterministic tie-breaking rule: smaller numeric values are preferred when frequencies are equal.

Let:

- `n` represent the number of input elements.
- `u` represent the number of distinct elements.
- `k` represent the requested number of results.

Complexity:

| Operation | Complexity |
|---|---:|
| Frequency calculation | O(n) |
| Bounded heap processing | O(u log k) |
| Auxiliary storage | O(u + k) |

The result contains distinct values, not repeated copies corresponding to their frequencies.

## 5. Merging K Sorted Arrays

Merging multiple sorted sequences is a natural priority queue application.

Each heap entry contains:

- Current value.
- Source array index.
- Element index within that array.

The heap maintains the smallest currently available value across all input arrays.

### Processing sequence

The algorithm initially inserts the first element of each nonempty array.

It repeatedly extracts the smallest value, adds it to the output, and inserts the next element from the same source array.

This avoids repeatedly scanning every input array.

For `N` total elements and `K` input arrays:

- Time: O(N log K)
- Auxiliary space: O(K), excluding the output.

The source arrays must already be sorted. Empty arrays are supported.

## 6. Running Median

A running median maintains the median as new values arrive.

Sorting the complete input after every insertion is inefficient.

The two-heap technique maintains two partitions.

| Heap | Stored values | Purpose |
|---|---|---|
| Lower heap | Smaller half | Max heap |
| Upper heap | Larger half | Min heap |

The following invariants must always hold:

1. Every value in the lower partition is less than or equal to every value in the upper partition.
2. The lower partition contains either the same number of elements as the upper partition or exactly one additional element.

When the total number of elements is odd, the median is the root of the lower heap.

When the total number is even, the median is the average of both roots.

Complexity:

- Insertion: O(log n)
- Median retrieval: O(1)
- Storage: O(n)

The implementations also account for empty streams and even-sized collections.

## 7. Sliding Window Maximum

The sliding window maximum finds the largest value in every consecutive window of a specified size.

The Python and JavaScript implementations use a monotonic decreasing deque.

A deque stores indices rather than values so that expired elements can be removed accurately.

When a new value arrives:

1. Remove indices outside the current window.
2. Remove indices whose values are smaller than or equal to the incoming value.
3. Insert the new index.
4. Read the maximum from the front of the deque.

Every index enters and leaves the deque at most once.

Therefore:

- Time: O(n)
- Auxiliary space: O(k)

Although this problem is included in a heap assessment, the deque is generally more efficient than a conventional heap for fixed-size sliding windows.

This distinction is important when selecting the appropriate data structure.

## 8. Minimum Cost of Connecting Ropes

Given several rope lengths, the objective is to connect all ropes while minimizing the total connection cost.

Connecting two ropes costs the sum of their lengths.

The optimal greedy strategy repeatedly combines the two shortest available ropes.

A min heap efficiently identifies these two values.

### Algorithm

1. Insert every rope length into a min heap.
2. Extract the two smallest values.
3. Calculate their combined length.
4. Add that value to the accumulated cost.
5. Insert the combined length back into the heap.
6. Continue until one rope remains.

For `n` ropes:

- Time: O(n log n)
- Auxiliary space: O(n)

The implementation rejects negative lengths and uses wider integer types where appropriate to reduce overflow risks.

## 9. Meeting Room Allocation

The meeting room problem determines the minimum number of rooms required to accommodate overlapping meetings.

Meetings are represented using start and end times.

The intervals use half-open semantics: `[start, end)`.

Consequently, a meeting ending at time `10` does not overlap with another meeting beginning at time `10`.

The algorithm sorts meetings by starting time and maintains a min heap containing the ending times of active meetings.

Before assigning a new meeting, expired meetings are removed.

The heap size represents the number of currently occupied rooms.

Complexity:

- Sorting: O(n log n)
- Heap processing: O(n log n)
- Auxiliary space: O(n)

This is an example of using a heap to manage changing resource availability.

## 10. Character Reorganization

The character reorganization problem requires rearranging characters so that identical adjacent characters do not appear.

A frequency map records character counts.

A max-priority queue selects the character with the highest remaining frequency.

The previously selected character is temporarily withheld from the next selection. This prevents immediate repetition.

A valid arrangement exists only when the maximum character frequency does not exceed the ceiling of half the input length.

The Python implementation returns `None` when no valid arrangement exists.

## 11. Priority Queue Scheduling

A priority queue is useful when processing order depends on business importance rather than insertion order alone.

The project defines four priority levels:

| Priority | Rank | Processing preference |
|---|---:|---|
| Critical | 0 | Highest |
| High | 1 | Second |
| Normal | 2 | Third |
| Low | 3 | Lowest |

A sequence number provides FIFO ordering among tasks with identical priorities.

This prevents arbitrary reordering when multiple tasks share the same priority.

The Python, JavaScript, C++17, and Java implementations demonstrate different approaches to scheduling.

### Event-driven processing

The JavaScript implementation extends `EventEmitter`.

It publishes events for:

- Task submission.
- Task cancellation.
- Task execution.
- Successful completion.
- Execution failure.

Asynchronous handlers allow processing to integrate with operations that return Promises.

### Enterprise job management

The Java implementation introduces explicit job states:

- `QUEUED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

It also demonstrates queue capacity validation, synchronized operations, and job-state validation.

A priority queue alone does not provide complete job management. Applications must also maintain task identity, lifecycle state, cancellation behavior, retry policies, and execution results.

## 12. PostgreSQL Relational Workflow

PostgreSQL does not expose an application-level binary heap through ordinary relational tables.

The SQL implementation therefore models priority queue behavior using relational records, indexed ordering, and transactional row locking.

This is distinct from implementing sift-up and sift-down in application memory.

### Relational model

The principal relationships are:

- A learner participates in an assessment.
- An assessment contains multiple problems.
- An attempt belongs to a learner and assessment.
- A submission belongs to an attempt and problem.
- A submission has multiple test results.
- A submission can generate a priority job.
- A priority job moves through defined processing states.
- Heap operation metrics record algorithm performance.

### Queue ordering

Jobs are ordered using:

1. Priority class.
2. Availability time.
3. Sequence number.

The sequence number preserves insertion order within a priority class.

A partial index focuses on jobs in the `QUEUED` state, reducing the indexed population for the principal worker retrieval operation.

### Concurrent processing

The `claim_next_job()` function uses:

- A common table expression.
- `FOR UPDATE SKIP LOCKED`.
- An atomic update.
- A returned job identifier.

`SKIP LOCKED` allows multiple database workers to claim different available jobs without waiting for rows already locked by other workers.

A production worker should execute job claiming and its associated state transition within an explicit transaction.

### Integrity controls

The database uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Enumerated workflow states.
- Submission validation triggers.
- Score validation triggers.
- Performance-oriented indexes.

The eligibility function evaluates whether a submission satisfies its acceptance, execution-time, memory, and test-case conditions.

The reporting views calculate learner performance and acceptance rates across problem categories.

## 13. Distinctions Between Implementations

| Implementation | Primary engineering perspective |
|---|---|
| Python | Algorithm experimentation, validation, reusable functions, and unit testing |
| JavaScript | Generic heap implementation, asynchronous processing, events, and cancellation |
| C++17 | STL priority queues, explicit domain structures, and governance evaluation |
| Java 17 | Enterprise-oriented types, bounded job scheduling, state management, and policy objects |
| PostgreSQL | Relational integrity, transactional queue processing, reporting, and operational metrics |

The implementations share algorithmic concepts but do not mechanically reproduce one another.

Python emphasizes algorithm clarity and testing.

JavaScript demonstrates how priority queues interact with asynchronous application workflows.

C++17 uses STL containers and explicit comparator definitions to model scheduling and evaluation.

Java 17 emphasizes typed domain models and controlled state transitions.

PostgreSQL provides persistent workflow state and concurrency-safe job claiming.

## 14. Complexity Comparison

| Problem | Primary data structure | Time complexity |
|---|---|---:|
| Kth largest | Bounded min heap | O(n log k) |
| Kth smallest | Bounded max heap | O(n log k) |
| Top K frequent | Frequency map and heap | O(n + u log k) |
| Merge K sorted arrays | Min heap | O(N log K) |
| Running median | Two heaps | O(log n) insertion |
| Sliding window maximum | Monotonic deque | O(n) |
| Connect ropes | Min heap | O(n log n) |
| Meeting rooms | Min heap | O(n log n) |
| Character reorganization | Max heap | O(n log u) |
| Priority scheduling | Priority queue | O(log n) insertion and extraction |

Here, `n` represents input size, `u` represents distinct values, `k` represents the selected number of elements, and `N` represents the total number of elements across merged arrays.

The complexity of a heap-based solution depends on the number of elements retained in the heap, not necessarily the entire input size.

## 15. Validation and Failure Conditions

The implementations explicitly handle common failure conditions.

| Condition | Expected handling |
|---|---|
| Empty heap extraction | Raise an error |
| Invalid `k` | Reject the request |
| Unsorted merge input | Reject the input |
| Invalid window size | Reject the request |
| Negative rope length | Reject the input |
| Empty running median | Reject median retrieval |
| Duplicate task identifier | Reject task submission |
| Invalid task priority | Reject submission |
| Queue capacity exceeded | Reject new enterprise job |
| Failed asynchronous handler | Record failure and propagate the error |
| Invalid job state transition | Reject the transition |
| Invalid SQL foreign key | Reject the database operation |
| Score exceeding maximum | Reject the database update |

Validation is important because heap algorithms frequently assume that their input satisfies specific ordering, range, and uniqueness conditions.

## 16. Security and Production Considerations

Heap algorithms do not independently provide application security.

A production implementation must consider the surrounding system.

### Input validation

- Validate numeric ranges before inserting values.
- Restrict input collection sizes.
- Reject malformed scheduling requests.
- Prevent unbounded memory allocation.
- Validate identifiers and task metadata.

### Resource management

- Set queue capacity limits.
- Establish execution deadlines.
- Monitor heap size.
- Control retry counts.
- Record failed and cancelled tasks.
- Prevent repeatedly failing tasks from consuming unlimited resources.

### Concurrency

A shared priority queue requires synchronization when multiple workers modify it.

The Java scheduler uses synchronized methods.

The PostgreSQL implementation uses transactional locking.

The JavaScript scheduler assumes its queue is accessed through a single Node.js event loop. Asynchronous execution does not automatically provide distributed concurrency control.

### Fairness and starvation

Strict priority ordering can starve lower-priority tasks when high-priority tasks continuously arrive.

Production schedulers may introduce:

- Priority aging.
- Execution quotas.
- Separate priority queues.
- Maximum waiting-time policies.
- Weighted scheduling.

These policies change the ordering behavior and should be selected according to operational requirements.

### Database security

The SQL workflow should be deployed with:

- Restricted database roles.
- Least-privilege access.
- Parameterized application queries.
- Controlled source-code retention.
- Audit logging.
- Transaction boundaries.
- Appropriate backup and recovery procedures.

## 17. Assessment and Testing Scenarios

The implementations include executable examples and correctness checks.

Important test scenarios include:

| Scenario | Expected behavior |
|---|---|
| Duplicate numbers | Correct kth-element selection |
| Negative numbers | Correct heap ordering |
| Single-element collection | Valid kth-element result |
| Empty input | Appropriate validation failure |
| Multiple empty arrays | Empty merged output |
| Unequal array lengths | Correct merged sequence |
| Equal frequencies | Deterministic tie-breaking |
| Even-sized median stream | Average of two middle values |
| Odd-sized median stream | Middle value |
| Expired meeting intervals | Reuse existing room |
| Equal task priorities | Preserve FIFO order |
| Cancelled queued task | Do not execute cancelled task |
| Failed execution | Record failure state |
| Concurrent database workers | Avoid duplicate job claiming |

The Python implementation includes a `unittest` suite.

The JavaScript implementation uses Node.js assertions.

The C++17 implementation uses runtime assertions.

The Java implementation performs executable correctness checks in its main method.

The PostgreSQL implementation includes sample records, constraints, triggers, workflow functions, and reporting queries.

## 18. Execution Requirements

| Deliverable | Runtime or platform |
|---|---|
| Python | Python 3.10+ |
| JavaScript | Node.js 18+ |
| C++17 | C++17-compatible compiler |
| Java | Java 17 |
| PostgreSQL | PostgreSQL 14+ |

### Python

The Python file uses standard-library modules and runs directly.

### JavaScript

The JavaScript file uses Node.js built-in modules and does not require npm packages.

### C++17

Compile using a C++17-compatible compiler with standard library support.

### Java 17

Compile the source using Java 17 and run the `HeapAssessment` class.

### PostgreSQL

Execute the SQL script using a PostgreSQL client connected to a database where the executing role has permission to create schemas, types, tables, functions, procedures, and triggers.

## 19. Technical Limitations

The implementations are designed as educational and executable assessment artifacts.

Some operational limitations are intentional:

- The Python and C++ scheduling examples demonstrate in-memory processing rather than distributed job execution.
- The JavaScript scheduler uses lazy cancellation and does not provide durable task persistence.
- The Java scheduler demonstrates job lifecycle management but does not implement a complete distributed retry service.
- The C++ governance example is separate from the heap algorithms and demonstrates another application of priority-based evaluation.
- The SQL queue models persistent priority ordering rather than a physical binary heap.
- The SQL sample workflow does not provide a sandbox for executing untrusted submitted source code.
- Heap-based selection does not guarantee stable ordering unless an explicit tie-breaking mechanism is included.

The central engineering decision is to select the data structure according to the operation being optimized. A heap is effective for repeated minimum or maximum extraction, while a deque, hash map, sorting algorithm, or database index may be more appropriate for other operations.
