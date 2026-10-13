# Queue Data Structure: FIFO Operations and Practical Implementations

## Technical overview

A queue is a linear data structure that processes elements in **First-In, First-Out (FIFO)** order. An element inserted earlier is removed before an element inserted later, provided the queue follows ordinary FIFO semantics.

Queues are used in build pipelines, support-ticket systems, network request handling, background processing, print services, event delivery, and task scheduling. Their value comes from separating the submission of work from its processing.

The core interface consists of five related concepts:

- **Queue:** The collection and its rules for maintaining FIFO order.
- **Enqueue:** Adds a new element at the rear.
- **Dequeue:** Removes and returns the element at the front.
- **Front:** Reads the oldest element without removing it.
- **Rear:** Reads the newest element without removing it.

Front and Rear are inspection operations. They must not change queue order or size. Dequeue changes the queue by removing exactly one element. Enqueue changes it by adding exactly one element.

## FIFO behavior

Consider a repository validation pipeline that must run compilation, unit tests, and a security scan in submission order.

| Operation | Queue contents, front to rear |
|---|---|
| Start | Empty |
| Enqueue `compile` | `compile` |
| Enqueue `unit-tests` | `compile`, `unit-tests` |
| Enqueue `security-scan` | `compile`, `unit-tests`, `security-scan` |
| Front | Returns `compile`; queue unchanged |
| Rear | Returns `security-scan`; queue unchanged |
| Dequeue | Returns `compile` |
| Remaining elements | `unit-tests`, `security-scan` |

A queue is not a stack. A stack removes the most recently inserted element first, while a FIFO queue removes the oldest pending element first.

## Queue invariants

A correct implementation maintains these properties:

- The front refers to the oldest element still present.
- The rear refers to the newest element still present.
- Enqueue preserves the order of existing elements and places the new element last.
- Dequeue returns the front element and preserves the relative order of all remaining elements.
- Front and Rear leave the queue unchanged.
- The size equals the number of elements available for removal.
- Empty-queue operations have defined behavior rather than accessing invalid storage.
- A bounded queue never exceeds its configured capacity.

These invariants are more important than the specific programming language or internal representation.

## Python implementation

The Python program begins with a generic `Queue` class backed by `collections.deque`. The `append` operation adds at the right-hand end, while `popleft` removes from the left-hand end. This avoids the repeated shifting of elements that occurs when removing index zero from an ordinary list.

The class exposes `enqueue`, `dequeue`, `front`, `rear`, `is_empty`, `size`, and `to_list`. Its snapshot method returns a new list so that callers cannot directly alter the internal collection.

Empty operations raise `QueueEmptyError`. This makes failure explicit and distinguishes an invalid operation from a valid result that happens to be `None`.

### Bounded queues

`BoundedQueue` introduces a maximum capacity. Enqueue raises `QueueFullError` if the queue has no remaining space. A removed element releases capacity for a subsequent insertion.

A bounded queue is useful when accepting unlimited pending work could exhaust memory or overload downstream services. Capacity rejection requires an application-level response, such as retrying later, reporting backpressure, or rejecting the request.

### Circular queues

`CircularQueue` uses a fixed-size array and three pieces of state:

- `head` identifies the next element to remove.
- `tail` identifies the next insertion position.
- `size` distinguishes empty and full states.

After an insertion or removal, an index advances using modulo arithmetic. When the index reaches the end of the array, it wraps to the beginning. Released positions are reused without shifting elements.

This representation provides constant-time enqueue and dequeue operations. It is particularly useful in fixed-memory systems, streaming buffers, and embedded applications.

### Linked queues

`LinkedQueue` uses nodes connected by references. The head points to the front node, while the tail points to the rear node. Enqueue attaches a node after the current tail, and dequeue advances the head.

Both operations take constant time. When the final node is removed, both head and tail must become empty. Failing to reset the tail leaves a stale reference and can corrupt later insertions.

The linked representation grows dynamically but allocates a separate node for each element. Its memory overhead is usually higher than that of an array-backed queue.

### Thread safety

`ThreadSafeQueue` protects each individual operation with a lock. This prevents two threads from concurrently modifying the underlying collection in an unsafe sequence.

The guarantee applies to individual methods. A sequence such as checking the size and then removing an element is not automatically atomic as a whole. Applications that require multi-operation guarantees need a larger synchronized operation or a purpose-built concurrent queue.

### Executable checks

The Python file uses `unittest` to verify FIFO ordering, non-destructive Front and Rear operations, empty-queue failures, capacity enforcement, circular wraparound, linked-queue reuse, and snapshot isolation.

The tests target observable behavior rather than internal implementation details. That makes it possible to replace the underlying representation without changing the public queue contract.

## JavaScript implementation

The JavaScript implementation uses an array plus a head index. A naive implementation using `Array.shift()` on every dequeue may require moving many remaining elements. The head-index approach advances a position instead.

When enough elements have been removed, the implementation compacts the remaining array. This avoids retaining a large number of obsolete entries indefinitely while preserving amortized constant-time removal.

The class also provides an iterator over a snapshot, making it possible to inspect queue contents without exposing the live internal array.

### Event-driven queue

`EventQueue` extends the basic queue and emits notifications after successful enqueue and dequeue operations. Consumers can subscribe to events and receive the affected element and the resulting queue size.

The unsubscribe function removes a listener. This matters in long-running applications where retaining obsolete listeners can cause memory leaks or duplicate event handling.

### Asynchronous work processing

`AsyncWorkQueue` separates queued tasks from currently executing tasks. It accepts a concurrency limit and starts new work while capacity remains available.

Each submitted task receives its own promise. Successful work resolves that promise, while failed work rejects it. A failure does not prevent the queue from starting later tasks.

The `onIdle` method resolves when no tasks are pending or active. The `close` method rejects future submissions and waits for accepted work to finish. The implementation demonstrates bounded concurrency, but it does not impose a maximum pending-queue size, cancellation, retry policy, or persistent recovery. Production workers may require all of these features.

## C++ case study: repository build coordination

The C++ program uses `std::queue` to model the FIFO portion of a repository build pipeline. It then adds a `BuildCoordinator` that submits and processes compilation, unit-test, and security-scan jobs.

Each `BuildJob` contains a job identifier, repository, source branch, commit identifier, and check name. This makes each queued item a meaningful unit of work rather than an arbitrary integer.

The coordinator tracks job states separately from queue order:

- `Queued` means the job awaits a worker.
- `Running` means a worker has removed it from the pending queue.
- `Passed` means processing completed successfully.
- `Failed` means processing finished with a failure.

Dequeue transitions a job from Queued to Running. Completion is valid only for a Running job. The coordinator rejects unknown identifiers, duplicate job identifiers, invalid fields, and submissions that exceed capacity.

The queue itself contains pending jobs only. Completed and failed jobs remain represented in the state map, so removing a job from the queue does not erase its processing outcome.

This distinction is useful in real build infrastructure. A FIFO queue determines which pending job is selected next, while a separate state model records what happened after selection. A failed security scan must not silently become a successful result merely because the queue continued processing later jobs.

The implementation uses `std::queue` for its restricted FIFO interface and `std::unordered_map` for job-state lookup. Queue insertion and removal are constant-time operations under the standard container's usual complexity guarantees. State lookup is average constant time.

The program is a single-threaded case study. A production coordinator shared by multiple worker threads would require synchronization around the queue, identifier registry, and state transitions. A distributed coordinator would also need durable job storage, ownership or lease handling, retry rules, and recovery from worker failure.

## Java implementation: enterprise validation service

The Java program models the same family of queue operations using `ArrayDeque`. The generic `Queue<T>` class rejects null elements, returns the oldest element from `dequeue`, and inspects the ends without changing the queue.

The bounded implementation composes the queue with a capacity rule. It checks capacity before accepting a new item, making the rejection behavior explicit.

The enterprise service uses a `ValidationJob` record to hold immutable job data. Its compact constructor validates the identifier and required text fields. Invalid jobs therefore cannot be created successfully through the normal record constructor.

`CheckState` represents the permitted lifecycle states. `ValidationService` tracks each known job in a map and uses a set to detect duplicate identifiers. Submission, start, and completion are distinct operations with distinct validation rules.

The state map and pending queue serve different purposes. The queue answers which job should run next. The state map answers what happened to a particular job. Conflating these concerns would make it difficult to retain results after dequeue.

The Java example uses standard-library data structures and requires no third-party dependencies. It is not a persistent or concurrent queue service. Production deployment would require transactional persistence or synchronized state management, depending on whether the service is local or distributed.

## SQL implementation: relational queue processing

The PostgreSQL script represents queued work as rows in `queue_job`. Each row has a unique job identifier, a queue sequence, repository metadata, a status, and timestamps.

The `queue_sequence` column provides deterministic FIFO ordering. The queue's front is the queued row with the smallest sequence, and its rear is the queued row with the largest sequence. Completed rows are excluded from these inspections.

### Relational integrity

The schema uses primary keys, a unique sequence constraint, nonempty-field checks, and status validation. Additional checks ensure that completed jobs have completion timestamps, running jobs have start timestamps, and failed jobs include a failure reason.

These constraints protect the data even if a caller bypasses the intended application workflow. They do not, by themselves, enforce every possible transition rule. The supplied functions restrict normal processing to the expected transitions.

### Enqueue and dequeue

`enqueue_job` creates a new queued row and returns its generated identifier.

`dequeue_job` uses a common table expression to locate the oldest queued row, locks it, and updates its state to Running. The `FOR UPDATE SKIP LOCKED` clause allows concurrent workers to claim different rows instead of waiting for the same pending row.

This approach is useful for concurrent database-backed workers, but a claim is not equivalent to guaranteed completion. If a worker fails after claiming a row, the job may remain Running until a recovery policy detects and handles the abandoned work.

### Completion and audit history

`complete_job` permits completion only when a row is currently Running. Failed jobs must include a meaningful failure reason. Repeated completion attempts are rejected.

A trigger writes enqueue and state-transition events to `queue_event`. The event table supports investigation of when jobs entered the system and how their statuses changed.

The partial index on `queue_sequence` for queued rows supports FIFO selection without indexing completed jobs for that query. The event index supports retrieving a job's recent history.

PostgreSQL sequence values are not transactional counters. Gaps can occur after rollbacks, and sequence order should not be interpreted as a count of successful transactions. The example guarantees FIFO according to its assigned sequence, not according to a universal definition of wall-clock arrival across concurrent transactions.

## Complexity and implementation trade-offs

| Operation | Deque-backed queue | Circular array queue | Linked queue |
|---|---:|---:|---:|
| Enqueue | O(1) amortized | O(1) | O(1) |
| Dequeue | O(1) | O(1) | O(1) |
| Front | O(1) | O(1) | O(1) |
| Rear | O(1) | O(1) | O(1) |
| Size | O(1) | O(1) | O(1) |
| Capacity | Dynamic | Fixed | Dynamic |

The circular queue uses a fixed allocation and avoids per-element node allocation. The linked queue grows dynamically but pays for node allocation and references. A deque provides a practical general-purpose implementation. A database-backed queue adds persistence and concurrent claiming at the cost of database operations, locking, and recovery requirements.

These complexity values describe the data-structure operations. They do not include the time needed to execute the work represented by a queued item.

## Edge cases and operational considerations

**Empty queue:** Dequeue, Front, and Rear require an explicit empty-state policy. The implementations raise exceptions rather than accessing nonexistent elements.

**Single element:** Front and Rear must refer to the same element. After removing it, the queue must become empty.

**Capacity reached:** A bounded queue must reject an insertion or apply an explicitly defined alternative. Silent overwriting changes ordinary FIFO behavior and should not happen accidentally.

**Repeated enqueue and dequeue:** Circular-buffer indices must wrap correctly. Linked queues must clear both endpoint references after the final removal.

**Mutable elements:** Queue ordering does not make the contents of an object immutable. A caller can still modify a mutable object stored in the queue unless the application applies its own ownership rules.

**Concurrent consumers:** Two consumers must not claim the same item. A local lock can protect an in-process queue, while a database worker can use row-level locking. Neither approach alone guarantees successful processing after a crash.

**Retries and duplicate delivery:** Real systems may process a task more than once after timeouts or recovery. Operations that cause external side effects should use idempotency keys or another explicit duplicate-handling strategy.

**Backpressure:** Unbounded queues can accumulate work faster than consumers can process it. Capacity limits, producer throttling, admission control, and monitoring help prevent uncontrolled growth.

**Ordering guarantees:** FIFO governs selection from the pending queue. With multiple concurrent workers, job completion order can differ from dequeue order because jobs may require different amounts of time.

## Practical applications

Repository pipelines use queues to schedule compilation, testing, security checks, packaging, and deployment validation. Support systems use them to process requests in arrival order. Network services use them to buffer messages between producers and consumers. Data-processing systems use queues to decouple ingestion from downstream processing.

Across these settings, the central design decision is to define precisely what FIFO ordering applies to, how empty and full conditions behave, and how an item moves from pending work into a recorded outcome. The queue provides the ordering mechanism; capacity management, error handling, persistence, and concurrency control make that mechanism reliable within a larger system.
