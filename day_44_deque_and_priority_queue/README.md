# Deque and Priority Queue

## Technical scope

A deque and a priority queue solve different ordering problems. A deque supports insertion and removal at both ends. A priority queue selects an element according to a priority ordering rather than simply selecting the oldest or newest element.

This repository models engineering work such as production incidents, security patches, maintenance tasks, and repository operations. It demonstrates how these structures influence intake order, dispatch decisions, fairness, cancellation, and concurrent processing.

The implementations are deliberately different across languages. Python emphasizes reusable data structures and executable tests. JavaScript implements a binary heap and asynchronous event intake. C++ presents an incident-dispatch case study. Java models enterprise work states and policy-driven scheduling. PostgreSQL provides a relational representation with integrity constraints, queue ordering, transactional dispatch, and event history.

## Deque mechanics

A double-ended queue, commonly called a deque, permits insertion and removal at both the front and the back.

| Operation | Meaning | Typical time complexity |
|---|---|---|
| Append at the back | Add the newest item | O(1) amortized |
| Append at the front | Add an item before existing items | O(1) amortized |
| Remove from the front | Consume the oldest or front-prioritized item | O(1) |
| Remove from the back | Consume the newest or back-prioritized item | O(1) |
| Inspect an end | Read the first or last item without removing it | O(1) |
| Search for an arbitrary item | Locate an item by value | O(n) |

These complexities describe the usual implementations rather than every possible implementation of a deque.

A deque is useful when the consumer must choose an end dynamically. A worklist can accept normal work at the back and urgent work at the front. A task can also be removed from the back when a workflow explicitly follows newest-first processing.

A deque does not automatically understand urgency. Its ordering comes from the operations used to insert and remove items.

### Capacity and empty-state behavior

An unbounded deque can continue growing until available memory becomes a constraint. A bounded deque makes the capacity rule explicit. The Python implementation rejects insertions when its configured capacity is reached rather than silently discarding an existing item.

Removal from an empty deque is an invalid operation. The Python and JavaScript implementations raise an exception instead of returning a fabricated work item. Explicit empty-state behavior helps distinguish an empty worklist from a valid work item whose fields happen to contain empty-looking values.

The JavaScript implementation uses a head index and a tail index rather than shifting every remaining element after front removal. Periodic compaction reclaims unused array space. This avoids repeatedly moving the entire queue during sustained front-removal workloads.

## Priority-based processing

A priority queue selects the item that ranks first under its comparator. A binary heap is a common implementation because it supports efficient insertion and removal of the highest-ranked element.

For a binary heap, every parent satisfies the heap-order property relative to its children. In a min-heap, the parent is no greater than either child. In a max-heap, the parent is no less than either child.

The heap is not a fully sorted array. Only the root is guaranteed to be the next element under the configured ordering. Traversing the underlying heap does not necessarily produce sorted output.

| Operation | Binary heap complexity |
|---|---|
| Insert an item | O(log n) |
| Inspect the root | O(1) |
| Remove the root | O(log n) |
| Build a heap from a collection | O(n) with bottom-up heap construction |
| Find an arbitrary item | O(n) without an auxiliary index |

A priority queue is appropriate for incident response, job scheduling, event simulation, shortest-path algorithms, and any system where the next item must be chosen by a ranking rule.

## Min-priority and max-priority queues

A min-priority queue returns the item with the smallest key. A max-priority queue returns the item with the largest key.

The interpretation of the key belongs to the application. If numeric priority 100 means critical, a max-priority queue dispatches critical work first. If numeric priority 0 means critical, the same policy should use a min-priority queue.

The direction of the ordering and the meaning of the value must be specified separately. An incorrectly chosen comparator can produce technically valid queue behavior that is operationally wrong.

The examples use integer priorities and stable tie-breaking. Items with equal priorities are processed in submission order where the implementation defines that policy. This prevents equal-priority work from being reordered arbitrarily by a heap.

Stable ordering does not provide fairness across different priority levels. Under continuous arrivals of high-priority work, lower-priority items may wait indefinitely. Systems that require bounded waiting times may need aging, reserved capacity, weighted scheduling, or explicit deadlines.

## Python implementation

The Python file provides a bounded deque, a reusable priority queue, a work scheduler, cancellation, and executable tests.

### Bounded deque

`BoundedDeque` wraps `collections.deque` and adds an explicit capacity rule. Its `append`, `appendleft`, `pop`, and `popleft` methods expose the core end operations. Inspection methods return the current front and back values without changing the structure.

The wrapper makes overflow and empty-state behavior part of the interface. This is useful when queue capacity is an application policy rather than an implementation detail.

### Heap-backed priority queue

Python's `heapq` implements a min-heap. The `PriorityQueue` class stores tuples containing a ranking key, a sequence number, and the associated value.

The sequence number preserves insertion order when priorities tie. It also avoids requiring arbitrary work-item objects to be directly comparable.

The `highest_first` option reverses the numeric ranking while retaining stable tie-breaking. The priority itself remains unchanged in the stored domain object.

### Lazy cancellation

The queue supports cancellation by marking an entry inactive in a dictionary. The physical heap entry remains until it reaches the root, where `_discard_cancelled` removes it.

This approach avoids searching the heap to remove an arbitrary entry. It also introduces a trade-off: cancelled entries may continue occupying memory until they reach the root. Systems with heavy cancellation rates may need heap compaction or an indexed heap.

The queue protects its operations with a reentrant lock. That lock makes individual operations on this object mutually exclusive within a process. It does not coordinate separate processes or machines.

### Validation and tests

`WorkItem` rejects blank identifiers, blank titles, negative priorities, and non-positive estimated durations. `WorkScheduler` rejects duplicate active ticket identifiers.

The `--test` command runs unit tests for deque operations, capacity, empty-state behavior, min-heap ordering, max-heap ordering, stable ties, cancellation, invalid input, duplicate identifiers, and randomized ordering.

Run the demonstrations with `python deque_priority_queue.py`. Run the tests with `python deque_priority_queue.py --test`.

## JavaScript implementation

The JavaScript file focuses on event-driven processing and an explicit binary heap rather than delegating all queue behavior to a library.

### Indexed deque

`Deque` uses a head index and a tail index to track the active region of its array. Front removal advances the head instead of shifting all remaining values. The implementation compacts its storage when the unused prefix becomes sufficiently large.

This design is useful for long-running event consumers because repeatedly calling `Array.prototype.shift()` can require linear movement of remaining elements.

### Binary heap and comparator

`BinaryHeap` accepts a comparison function. Insertion moves an item upward until the heap property holds. Removal replaces the root with the final element and moves it downward until the property is restored.

`StablePriorityQueue` supplies the ordering rule. The comparison first evaluates priority and then the sequence number. The same heap implementation can therefore serve both min-priority and max-priority use cases.

The comparison uses integer priorities validated with `Number.isSafeInteger`. This prevents unsafe numeric priorities from entering the ordering logic.

### Asynchronous intake

`eventStream` is an asynchronous generator. `processEvents` consumes it with `for await...of`, making the processing function compatible with asynchronous event sources.

The example separates urgent deque intake from scheduled priority dispatch. It also uses immutable event snapshots to prevent callers from changing an event's fields after submission.

This is a local processing model, not a durable distributed queue. It does not provide crash recovery, cross-process coordination, persistence, or exactly-once execution.

## C++ incident-dispatch case study

The C++ program models an incident desk receiving operational failures from payments, identity, databases, and network services.

### Domain representation

`Incident` carries an identifier, affected service, description, severity, and arrival sequence. Its constructor validates the data before an incident can enter a queue.

`IncidentDesk` maintains separate structures for immediate intake, critical dispatch, and lowest-severity triage:

- A `std::deque` handles immediate intake from the front.
- A `std::priority_queue` with `HighestSeverityFirst` dispatches the highest-severity incident.
- A second `std::priority_queue` with `LowestSeverityFirst` exposes the opposite ranking policy.

The structures use the same incident representation but make different selection decisions.

### Comparator semantics

C++ `std::priority_queue` places the element that ranks highest according to its ordering rules at the top. Its comparator therefore requires careful interpretation.

`HighestSeverityFirst` returns `true` when the left incident should rank below the right incident. Greater severity consequently reaches the root. Equal severities are resolved using the earlier arrival sequence.

`LowestSeverityFirst` reverses the severity comparison while retaining the same tie-breaking rule.

### Validation and consistency

The incident desk validates an incident before changing queue state. It rejects duplicate identifiers and severities outside the supported range. Exceptions communicate invalid input and attempts to consume an empty queue.

The example maintains more than one queue representation of an incident. This demonstrates an important design limitation: removing an incident from one structure does not automatically remove it from every other structure. A production implementation would normally maintain explicit lifecycle state and coordinate updates across all representations, or use a single authoritative scheduler with derived indexes.

The example is a sequential case study. Its containers are not thread-safe, and its multiple queues are not a durable job-processing service.

Compile and run with a C++17-compatible compiler, for example `g++ -std=c++17 incident_dispatch.cpp -o incident_dispatch`.

## Java enterprise scheduler

The Java program models repository engineering work as typed domain objects with explicit lifecycle rules.

### Immutable work records

`WorkItem` is a record that holds the ticket identifier, repository, description, numeric priority, and submission time. Its compact constructor rejects missing fields and priorities outside the supported range.

Using an immutable record prevents a queued item's priority from changing after insertion. Mutating a priority without repairing the heap could otherwise violate the ordering property.

### Explicit lifecycle states

`ScheduledWork` represents a work item's current state. The allowed transitions are:

- `QUEUED` to `IN_PROGRESS` or `CANCELLED`.
- `IN_PROGRESS` to `COMPLETED` or `CANCELLED`.

Completed and cancelled work are terminal states in this model. An invalid transition raises `IllegalStateException`.

The lifecycle state is separate from queue membership. Removing an item from a queue does not itself imply that the work has completed.

### Policy-driven scheduling

`QueuePolicy` distinguishes minimum-numeric-priority scheduling from maximum-numeric-priority scheduling. The comparator orders by priority, submission time, and identifier, providing deterministic tie-breaking.

`WorkScheduler` uses `ArrayDeque` for urgent intake and `PriorityQueue` for scheduled dispatch. This demonstrates how different structures can serve separate responsibilities within an enterprise service.

The implementation is intentionally single-threaded. A concurrent service would need synchronization or a dedicated coordination mechanism around state transitions, active identifiers, and queue updates. If persistence is required, lifecycle transitions and dispatch claims should be coordinated transactionally with the durable work record.

Compile and run with Java 17 or later using `javac RepositoryWorkScheduler.java` followed by `java RepositoryWorkScheduler`.

## PostgreSQL relational model

The SQL script models queue membership and work lifecycle in separate tables. It uses PostgreSQL enums, identity columns, partial indexes, triggers, JSONB event details, a dispatch function, and a reporting view.

### Work records

`work_item` stores the authoritative ticket information and lifecycle status. Its constraints enforce unique ticket identifiers, non-empty descriptive fields, and a priority range of 0 through 100.

The `work_status` enum restricts lifecycle values to the states supported by the database model. A trigger validates transitions so that completed work cannot silently return to the queued state.

### Queue membership

`queue_entry` represents membership in a selected queue policy. A work item may have entries in multiple queue representations because each policy is evaluated independently.

The partial unique index `uq_active_work_queue` prevents the same work item from having duplicate active entries for the same queue direction. The sequence index supports scans of active queue membership.

The queue's selection rule is applied when dispatching rather than by assuming that insertion order alone represents priority. The min-priority policy sorts numeric priority in ascending order. The max-priority policy sorts it in descending order. Deque policies use sequence order from the selected end.

### Transactional dispatch

`dispatch_next` selects a matching active entry, marks it inactive, changes the work status to `in_progress`, and writes an event record. The operations execute within the caller's transaction.

The query uses `FOR UPDATE ... SKIP LOCKED`, allowing concurrent workers to skip entries locked by other transactions. This can support competing database workers without requiring them to wait on the same selected row.

The function raises an exception if no eligible entry is available. Because the exception aborts the current transaction unless handled, the caller should treat an unsuccessful dispatch as a failed operation rather than as a successful empty result.

### Integrity and performance

The unique partial index enforces active membership at the database layer. The priority check prevents unsupported priority values. The lifecycle trigger enforces valid transitions even when updates do not originate from the intended application.

The queued-priority index supports queries filtering queued work and sorting by priority, submission time, and identifier. The active queue index supports queue membership scans.

These indexes improve particular access paths but add storage and write overhead. Their actual value depends on data volume, query plans, the number of active queue entries, and the frequency of queue changes.

### Event history and reporting

`queue_event` records submissions, enqueue operations, dispatches, and cancellations. Its JSONB details preserve contextual values such as queue direction and priority without adding a separate column for every event-specific attribute.

`active_queue_summary` aggregates active entries by queue direction and reports the minimum, maximum, and average priorities. This provides a useful operational view without consuming queue entries.

The script resets the `queue_lab` schema before creating its objects, so it is intended for an isolated demonstration database rather than an existing production schema. The sample dispatch is wrapped in a transaction to make the state change explicit.

## Choosing the appropriate structure

| Requirement | Appropriate structure | Reason |
|---|---|---|
| Insert and remove at either end | Deque | Both ends are directly accessible |
| Process the smallest ranking key first | Min-priority queue | The smallest key remains at the root |
| Process the largest ranking key first | Max-priority queue | The largest key remains at the root |
| Process ordinary work in arrival order | FIFO queue or deque | Insertion order determines removal order |
| Process newest work first | Deque with back removal | The newest item can be consumed from the back |
| Support both immediate intake and ranked dispatch | Separate deque and priority queue | Intake order and dispatch ranking are distinct policies |

The structures are not interchangeable. A deque does not sort items by priority, and a heap does not provide efficient arbitrary access to both ends. Combining them is useful when a system has distinct intake and scheduling requirements, but the application must define which structure owns each item and how lifecycle changes are coordinated.

## Edge cases and production constraints

**Equal priorities:** Define a tie-breaking policy explicitly. Stable ordering avoids unpredictable behavior among equally ranked items, but stable ordering alone does not prevent starvation.

**Priority changes:** A heap assumes that an entry's ordering key remains stable while it is stored. If priority changes, remove and reinsert the entry or use a data structure designed for indexed priority updates.

**Cancellation:** Lazy cancellation avoids searching the heap, but inactive entries consume memory until discarded. Monitor cancellation rates and compact the heap when necessary.

**Duplicate work:** An identifier should have a clear uniqueness scope. It may be globally unique, unique among active tasks, or unique only within a repository. The Python and Java examples use active-work semantics for their schedulers, while the PostgreSQL sample keeps ticket identifiers unique in the work table.

**Concurrent consumers:** A thread-safe in-memory structure does not automatically provide durable processing. Multiple workers need an atomic claim operation, and distributed systems need a defined recovery policy for worker failures.

**Fairness:** Strict priority can indefinitely postpone low-priority work. Priority aging or weighted scheduling can reduce starvation when the business requires bounded waiting times.

**Capacity and backpressure:** An unbounded queue can consume excessive memory during sustained overload. Bounded capacity, rejection policies, batching, and producer backpressure should reflect the system's service rate and operational limits.

**Observability:** Queue depth, waiting time, processing duration, cancellation rate, failed dispatches, and priority distribution are more informative than queue size alone. A growing queue can indicate that incoming work exceeds processing capacity.

**Failure recovery:** In-memory queues lose state when the process terminates. Persistent work records, transactional dispatch, event history, and idempotent handlers are needed when work must survive restarts or be safely retried.

## Performance and implementation trade-offs

Deque operations at either end are generally constant time. Heap insertion and root removal take logarithmic time because they restore the heap-order property along a tree path. Root inspection is constant time.

The Python implementation uses `heapq`, minimizing custom heap logic. The JavaScript implementation exposes the heap algorithm directly, making comparison and repair behavior explicit. C++ uses the standard library's `std::priority_queue` with custom comparators. Java uses `PriorityQueue` with a domain-specific comparator. PostgreSQL evaluates ordering through indexed relational queries and transactional row locking.

These approaches optimize different concerns. Standard-library heaps reduce implementation complexity. A custom heap provides direct control over internal behavior. Database-backed scheduling provides persistence and transactional coordination at the cost of database work, index maintenance, locking, and transaction management.

A correct scheduling design starts by specifying the selection policy, priority direction, tie-breaking rule, empty-state behavior, cancellation semantics, capacity constraints, and concurrency requirements. The data structure should implement that policy without silently changing its meaning.
