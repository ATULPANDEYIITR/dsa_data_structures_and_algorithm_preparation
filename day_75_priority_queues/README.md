# Priority Queues: Scheduling, Selection and Heap Algorithms

## Technical Scope

This project implements priority queues and their practical applications through five independent programming and database implementations.

The central problem is selecting the next element from a collection according to a priority rule rather than its insertion position.

The implementations cover:

- Minimum-priority queues.
- Maximum-priority queues.
- Binary heap operations.
- Stable priority scheduling.
- Task processing and cancellation.
- Dynamic priority updates.
- Top-K selection.
- K-th smallest and largest elements.
- Running median calculation.
- Concurrent task claiming and failure recovery.
- Enterprise scheduling policies.

## 1. Priority Queue Fundamentals

A priority queue is an abstract data type in which removal depends on an element's priority.

Unlike a conventional FIFO queue, the earliest inserted element is not necessarily the next element removed.

Each entry contains:

- An element or task.
- A priority value.
- An ordering rule.
- Optionally, a sequence number for stable ordering.

### Minimum-priority queue

A minimum-priority queue removes the element with the smallest priority value first.

Example:

| Element | Priority |
|---|---:|
| A | 40 |
| B | 10 |
| C | 30 |
| D | 5 |
| E | 20 |

Extraction order:

`D → B → E → C → A`

This behavior is appropriate for shortest-distance algorithms, earliest-deadline scheduling, and selecting the smallest available value.

### Maximum-priority queue

A maximum-priority queue removes the element with the largest priority value first.

Using the same entries:

`A → C → E → B → D`

This behavior is useful for urgent incident processing, emergency task scheduling, and selecting the largest elements from a dataset.

The numeric interpretation of priority is a design decision. A system must document whether larger or smaller values indicate greater urgency.

## 2. Binary Heap Data Structure

A binary heap is a complete binary tree satisfying a heap-order property.

A complete binary tree fills each level from left to right, except possibly the last level.

### Min-heap property

Every parent has a value less than or equal to its children.

### Max-heap property

Every parent has a value greater than or equal to its children.

For an array-based heap, the relationship between a node and its children is calculated using indices.

For a zero-based array:

| Relationship | Formula |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

A heap does not maintain complete sorted order. It guarantees that the root contains the next highest-priority element according to its ordering rule.

### Heap representation

Example min-heap:

       5
      / \
     10  8
    / \
   40  20

Array representation:

`[5, 10, 8, 40, 20]`

The root is the minimum element. Other elements are only partially ordered.

## 3. Core Heap Operations

| Operation | Time complexity |
|---|---:|
| Insert | O(log n) |
| Peek | O(1) |
| Extract minimum | O(log n) |
| Extract maximum | O(log n) |
| Search arbitrary element | O(n) |
| Build heap | O(n) |
| Heapify one node | O(log n) |
| Remove arbitrary element | O(n) without an index map |
| Sort using heap | O(n log n) |

Insertion places an element at the end of the heap and moves it upward until the heap property is restored.

Extraction removes the root, moves the final element to the root position, and moves it downward until the heap property is restored.

The Python and JavaScript implementations provide explicit heap behavior. C++ and Java also demonstrate their standard-library priority queue facilities.

## 4. Stable Priority Queues

Two entries can have identical priorities.

A basic heap does not necessarily preserve their insertion order.

For scheduling systems, this can cause unpredictable behavior when tasks have equal urgency.

A stable priority queue adds a monotonically increasing sequence number.

Each entry is conceptually represented as:

`(priority, sequence, task)`

For a maximum-priority queue:

1. Compare priority in descending order.
2. When priorities match, compare sequence in ascending order.
3. Process the earliest submitted task first.

The Python, JavaScript, C++, and Java implementations demonstrate stable scheduling.

Stable ordering is particularly important when processing customer requests, background jobs, and operational workloads.

## 5. Priority-Based Task Scheduling

A scheduling system maintains pending tasks and repeatedly selects the highest-priority eligible task.

The scheduling lifecycle is:

`Submission → Pending → Running → Completed`

Alternative transitions include:

- Pending → Cancelled
- Running → Failed
- Running → Pending after a retry

Each task contains an identifier, description, category, priority, and execution state.

### Priority updates

A pending task may become more or less urgent.

For example:

| Task | Initial priority | Updated priority |
|---|---:|---:|
| Database backup | 3 | 3 |
| Security incident | 10 | 10 |
| Generate report | 2 | 8 |
| Deployment | 7 | 7 |

The report moves ahead of lower-priority tasks.

### Lazy invalidation

Updating an element already stored in a heap can be difficult because a heap does not provide efficient arbitrary-element lookup by default.

The Python, JavaScript, and C++ scheduling models use versioned entries.

When a priority changes:

1. Update the authoritative task record.
2. Increase its version number.
3. Insert a new heap entry.
4. Ignore older entries when they are extracted.

This avoids searching and modifying an arbitrary heap position.

The tradeoff is that stale entries consume memory until removed.

A production implementation should periodically rebuild the heap when stale entries become excessive.

### Cancellation

Cancellation changes the authoritative task state.

The old heap entry remains physically present but is ignored when encountered.

Only pending tasks may be cancelled or reprioritized in these examples.

Running tasks require a separate interruption or cooperative cancellation mechanism.

## 6. Top-K Selection

Top-K selection identifies the K largest elements without completely sorting the input.

For an input collection of size `n`, maintain a min-heap containing at most `k` elements.

For every incoming element:

1. Insert it if the heap contains fewer than K elements.
2. Otherwise compare it with the heap root.
3. Replace the root when the incoming element is larger.
4. Ignore smaller elements.

The root always represents the smallest member of the current top-K collection.

The final K elements are the largest values.

### Complexity

- Time: O(n log k)
- Auxiliary space: O(k)

This is useful when the complete dataset is large but only a small number of leading results are required.

The Python, JavaScript, C++, and Java implementations provide top-K selection.

The PostgreSQL implementation uses ordered retrieval and ranking.

## 7. K-th Smallest and K-th Largest Elements

The K-th smallest element can be identified by maintaining a max-heap containing at most K values.

The K-th largest element can be identified by maintaining a min-heap containing at most K values.

For example:

Input:

`[17, 4, 29, 11, 8, 35, 21, 3, 29]`

Sorted order:

`[3, 4, 8, 11, 17, 21, 29, 29, 35]`

Results:

| Operation | Result |
|---|---:|
| Third smallest | 8 |
| Third largest | 21 |
| Largest | 35 |
| Smallest | 3 |

The implementations validate K to prevent invalid indexing and empty-result errors.

Duplicate values are treated as separate observations.

For distinct-element selection, duplicate elimination must be applied explicitly.

## 8. Running Median with Two Heaps

A running median calculates the median as new values arrive without sorting the entire collection after every insertion.

Two heaps divide the observations into two groups.

**Lower half**

A max-heap containing the smaller values.

**Upper half**

A min-heap containing the larger values.

The invariants are:

- Every lower-half value is less than or equal to every upper-half value.
- The size difference between the heaps is at most one.

If both heaps contain the same number of elements, the median is the average of their roots.

If the lower heap contains one extra element, its root is the median.

Example:

| Inserted value | Running median |
|---:|---:|
| 12 | 12 |
| 4 | 8 |
| 5 | 5 |
| 3 | 4.5 |
| 8 | 5 |
| 7 | 6 |
| 15 | 7 |
| 20 | 7.5 |

### Complexity

| Operation | Complexity |
|---|---:|
| Insert | O(log n) |
| Median retrieval | O(1) |
| Total storage | O(n) |

This structure is useful for streaming latency measurements, financial observations, system monitoring, and real-time statistics.

## 9. Python Implementation

The Python implementation emphasizes reusable data structures and simulation of a task-processing system.

| Component | Responsibility |
|---|---|
| `PriorityQueue` | Stable min-priority and max-priority behavior |
| `Task` | Task data validation |
| `TaskScheduler` | Task lifecycle and scheduling |
| `top_k_largest` | Bounded heap selection |
| `kth_smallest` | K-th smallest selection |
| `RunningMedian` | Streaming median |
| `PriorityQueueTests` | Automated correctness checks |

Python's `heapq` module implements a min-heap.

A maximum-priority queue is implemented by negating integer priorities.

The scheduler uses a dictionary for authoritative task records and a heap for scheduling decisions.

This separation allows efficient task-state lookup without relying on heap contents as the source of truth.

Run the implementation with:

`python priority_queue.py`

The program executes demonstrations and unit tests.

## 10. JavaScript Implementation

The JavaScript implementation focuses on event-driven and asynchronous processing.

### Engineering mechanisms

- Custom binary heap.
- `Map` for authoritative task storage.
- `EventEmitter` for task lifecycle events.
- Promises for asynchronous execution.
- Versioned entries for priority updates.
- Explicit processing-state protection.
- Error isolation between individual tasks.

The scheduler emits events for:

- Submission.
- Start.
- Completion.
- Failure.
- Cancellation.
- Priority changes.

An asynchronous handler executes each selected task.

If one task fails, the failure is recorded and processing continues with the remaining tasks.

The queue does not claim that a completed event means a real external deployment succeeded. The example uses a simulated handler.

Run with:

`node priority_queue.js`

## 11. C++17 Implementation

The C++ implementation emphasizes efficient container operations and explicit scheduling state.

The standard `priority_queue` container adaptor provides heap-based insertion and extraction.

Its comparator determines which element appears at the top.

The scheduling engine uses:

- `unordered_map` for task lookup.
- `priority_queue` for scheduling.
- Enumerations for task states and categories.
- Versioned entries for priority changes.
- Exceptions for invalid state transitions.

The selection implementation uses `greater<int>` to construct a min-heap.

A separate max-heap supports K-th smallest selection.

The implementation demonstrates why the comparator must be selected carefully when using the C++ standard library.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra main.cpp -o priority`

Execute:

`./priority`

On Windows:

`priority.exe`

## 12. Java 17 Enterprise Implementation

The Java implementation emphasizes domain modeling, policy evaluation, and controlled state transitions.

### Domain types

| Type | Purpose |
|---|---|
| `Job` | Immutable task representation |
| `JobCategory` | Task classification |
| `JobStatus` | Execution state |
| `QueueEntry` | Heap scheduling metadata |
| `SchedulingPolicy` | Eligibility rules |
| `Scheduler` | Task-processing service |
| `RunningMedian` | Streaming statistics |

Java records provide immutable task snapshots.

The scheduler replaces an existing record when its priority or state changes.

This avoids exposing mutable task objects to external callers.

### Enterprise deployment policy

A deployment job must satisfy:

- Minimum priority requirements.
- Security-scan requirements.
- Deployment approval requirements.

A job that fails these checks is not executed.

The example keeps policy evaluation separate from heap ordering.

This distinction is important because the highest-priority task is not necessarily an eligible task.

A production system would normally maintain a separate blocked-task collection to prevent ineligible jobs from repeatedly entering scheduling evaluation.

Compile and execute:

`javac Main.java`

`java Main`

## 13. PostgreSQL Implementation

The PostgreSQL implementation models a persistent scheduling system.

### Relational model

`Repositories`
→ `Scheduling Policies`
→ `Tasks`
→ `Workers`
→ `Task Events`

Numeric observations are stored separately for selection and statistical calculations.

### Main tables

| Table | Responsibility |
|---|---|
| `repositories` | Repository identity and activity |
| `workers` | Available execution workers |
| `scheduling_policies` | Priority and retry rules |
| `tasks` | Authoritative task records |
| `task_events` | Execution audit history |
| `numeric_samples` | Values used for selection problems |

### Database integrity

Primary keys identify records.

Foreign keys maintain relationships between tasks, repositories, workers, and policies.

Check constraints prevent invalid priority ranges, retry counts, and task states.

Partial indexes improve retrieval of pending tasks.

The event trigger records task submission, state transitions, and priority changes.

### Min-priority and max-priority retrieval

The `get_priority_queue` function reads the selected scheduling policy and chooses the appropriate ordering.

Min-priority policy:

`ORDER BY priority ASC`

Max-priority policy:

`ORDER BY priority DESC`

Both use submission time and task ID to establish deterministic ordering for equal priorities.

### Concurrent task claiming

The `claim_next_task` function uses:

`FOR UPDATE SKIP LOCKED`

This is important for multi-worker systems.

When one worker locks a pending task, another worker skips that record instead of waiting for the same task.

The selected task is changed to the running state within the transaction.

This provides a transactional task-claiming mechanism.

The worker and policy records are also checked before claiming.

### Failure handling

The `finish_task` procedure distinguishes successful execution from failure.

Successful execution changes the state to completed.

Failed execution either:

- Returns the task to pending with a future availability time.
- Changes the task to failed when the retry limit is reached.

Retry delays are controlled by scheduling policy.

### Reporting and analytics

The database includes:

- Queue summary view.
- Worker activity view.
- Task-state aggregation.
- Execution history.
- Delayed-task retrieval.
- Failed-task reporting.
- Top-K selection.
- K-th smallest selection.
- Median and average calculations.

PostgreSQL's `percentile_cont(0.5)` computes the median using ordered observations.

This is a statistical query, not a persistent two-heap streaming implementation.

## 14. Practical Applications

| Application | Priority queue usage |
|---|---|
| Operating systems | Process scheduling |
| Cloud platforms | Background job processing |
| Cybersecurity | Security incident prioritization |
| Repository automation | Build and deployment scheduling |
| Network systems | Packet prioritization |
| Artificial intelligence | Best-first search |
| Graph algorithms | Dijkstra's shortest path |
| Data analytics | Top-K selection |
| Monitoring | Running median |
| Financial systems | Event and order processing |

### Dijkstra's shortest-path connection

Dijkstra's algorithm repeatedly selects the unsettled vertex with the smallest tentative distance.

A min-priority queue makes this selection efficient.

The queue stores vertex-distance pairs.

When a shorter distance is discovered, a new entry can be inserted. Outdated entries are discarded when extracted.

This is conceptually similar to the versioned-entry approach used in the task scheduler.

### Best-first search

Best-first search selects the next candidate according to an evaluation function.

The priority queue organizes candidates according to their estimated relevance or cost.

The queue's ordering rule determines which candidate is explored next.

## 15. Edge Cases and Failure Conditions

The implementations account for several important conditions.

| Condition | Expected handling |
|---|---|
| Empty heap extraction | Raise an exception |
| Empty median collection | Reject median calculation |
| Negative K | Reject invalid input |
| K greater than collection size | Reject selection |
| Duplicate task ID | Reject submission |
| Unknown task ID | Reject modification |
| Priority update after execution | Reject modification |
| Cancellation after execution | Reject cancellation |
| Equal priorities | Preserve insertion order |
| Repeated priority updates | Ignore stale heap entries |
| Asynchronous handler failure | Mark task failed |
| Invalid deployment policy | Reject execution |
| Concurrent task claim | Lock and skip already claimed records |

## 16. Performance and Engineering Tradeoffs

### Heap versus sorted array

A sorted array provides efficient access to the next element but requires O(n) insertion in the general case.

A binary heap provides O(log n) insertion and extraction.

For continuously changing scheduling workloads, heaps are generally more suitable.

### Heap versus balanced search tree

A balanced search tree maintains sorted ordering and supports efficient search and deletion.

A heap is simpler and usually offers better constant-factor performance when only the highest- or lowest-priority element is required.

### Lazy invalidation versus indexed heap

Lazy invalidation simplifies priority updates but increases the number of heap entries.

An indexed heap maintains a mapping from task identifiers to heap positions.

It supports direct priority updates in O(log n), but requires more complicated index maintenance.

### Concurrency

An in-memory priority queue is not automatically thread-safe.

Production systems need synchronization, worker coordination, failure recovery, and durable task state.

The PostgreSQL implementation demonstrates transactional claiming, while the JavaScript example protects against duplicate processing within a single scheduler instance.

## 17. Security and Reliability Considerations

Priority values must be validated before entering the scheduling system.

Unrestricted priority values can allow low-trust users to monopolize execution capacity.

Production systems should enforce:

- Role-based task submission permissions.
- Authorized priority modifications.
- Bounded priority ranges.
- Maximum retry counts.
- Worker identity validation.
- Audit logging.
- Task execution time limits.
- Resource quotas.
- Duplicate-submission protection.
- Secure handling of task payloads.
- Explicit failure and recovery policies.

Priority queues alone do not provide fairness.

A continuously arriving stream of high-priority jobs can starve lower-priority tasks.

Possible mitigations include aging, quotas, weighted scheduling, and separate queues for different workload classes.

## 18. Complexity Comparison

| Problem | Algorithm | Time complexity | Auxiliary space |
|---|---|---:|---:|
| Insert into heap | Binary heap | O(log n) | O(n) total |
| Extract root | Binary heap | O(log n) | O(n) total |
| Read root | Binary heap | O(1) | O(1) |
| Build heap | Heapify | O(n) | O(n) |
| Top-K largest | Bounded min-heap | O(n log k) | O(k) |
| K-th smallest | Bounded max-heap | O(n log k) | O(k) |
| Running median insertion | Two heaps | O(log n) | O(n) |
| Running median retrieval | Two heaps | O(1) | O(1) |
| Task lookup | Hash map | O(1) average | O(n) |
| Task priority update | Lazy invalidation | O(log n) | O(n) additional entries |

## 19. Key Conceptual Distinctions

- A priority queue is an abstract data type.
- A binary heap is one implementation of that data type.
- A min-heap exposes the smallest element first.
- A max-heap exposes the largest element first.
- Heap order does not mean that the complete array is sorted.
- Stable ordering requires an additional tie-breaking mechanism.
- Scheduling requires task lifecycle management beyond heap operations.
- Priority updates require either indexed updates or stale-entry handling.
- Top-K selection uses a bounded heap rather than a complete sort.
- Running median requires two complementary heaps rather than one.
- Priority and eligibility are separate concepts: the most urgent task may still be ineligible for execution.
- Concurrent processing requires coordination beyond an ordinary in-memory heap.

These implementations provide a practical foundation for heap-based selection, scheduling systems, streaming statistics, and priority-driven processing.
