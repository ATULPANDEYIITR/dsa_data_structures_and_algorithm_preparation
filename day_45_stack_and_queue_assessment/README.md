# Stack and Queue Assessment

## Scope

This assessment examines stacks, queues, deques, parenthesis validation, monotonic stacks, and next-greater-element problems through executable implementations in Python, JavaScript, C++17, Java 17, and PostgreSQL.

The central objective is to select the correct data structure for a problem's access pattern. A stack exposes the most recently inserted item, a queue processes the earliest pending item, and a deque supports efficient operations at both ends. Monotonic stacks and deques use these access rules to solve certain array problems in linear time.

The implementations cover both isolated algorithmic questions and operational scenarios involving task dispatch, undo history, event processing, and assessment records.

## Stack, queue, and deque semantics

| Structure | Access rule | Typical operations | Common application |
|---|---|---|---|
| Stack | Last in, first out (LIFO) | Push, pop, peek | Undo history, delimiter matching, postfix evaluation |
| Queue | First in, first out (FIFO) | Enqueue, dequeue, front | Task scheduling, event processing |
| Deque | Both ends | Add or remove at either end | Sliding-window maximum, candidate maintenance |
| Monotonic stack | Ordered unresolved candidates | Push, pop while a condition holds | Next greater element, histogram area |
| Monotonic deque | Ordered candidates with expiration | Remove obsolete indices and dominated values | Sliding-window maximum |

A conventional stack and queue represent different processing contracts. Replacing a queue with a stack changes the order in which tasks execute. A deque is useful when candidates must be discarded from either end, rather than only from the top of a stack.

The implementations use collections with efficient end operations instead of repeatedly removing the first element of a dynamic array. Removing an array's first element may require shifting all remaining elements.

## Python implementation

The Python script uses small classes to make the access rules explicit. `Stack` exposes `push`, `pop`, and `peek`; `Queue` uses `collections.deque`; and `TwoStackQueue` demonstrates how two LIFO collections can implement FIFO behavior.

The two-stack queue transfers incoming elements to its outgoing stack only when the outgoing stack is empty. Reversing the incoming stack establishes the required removal order. Each element is transferred at most once in each direction, giving amortized O(1) enqueue and dequeue operations.

The algorithm functions cover several distinct assessment patterns:

- `is_valid_parentheses` matches each closing delimiter against the most recent unmatched opening delimiter. A mismatched pair or an unexpected closing delimiter immediately makes the expression invalid.
- `minimum_parentheses_insertions` counts unmatched opening and closing parentheses without storing every character. It applies only to strings containing parentheses.
- `evaluate_postfix` uses an operand stack. Binary operators remove the right operand before the left operand, which matters for subtraction and division.
- `next_greater_elements` stores indices of unresolved values. A new value resolves all smaller values at the top of the stack.
- `daily_temperatures` uses the same unresolved-index pattern, but returns distances between days rather than temperature values.
- `sliding_window_maximum` keeps candidate indices in a decreasing-value deque and removes indices that fall outside the active window.
- `largest_histogram_rectangle` uses an increasing-height stack. When a lower bar appears, it establishes a right boundary for taller bars and permits their rectangle areas to be calculated.
- `circular_next_greater` scans the array twice while pushing each original index only once, allowing elements near the end to find greater values near the beginning.

The executable assessment uses assertions to compare actual outputs against expected results. It also exercises empty-stack errors, invalid window widths, and division by zero.

## JavaScript implementation

The JavaScript file emphasizes event-driven processing and stateful operations.

`EventQueue` uses a private array and a head index. Advancing the head avoids the repeated shifting associated with removing index zero. Periodic compaction releases consumed prefixes when they occupy a substantial portion of the array. Events are shallow-copied and frozen when enqueued; nested objects would still require their own immutability policy.

`processEvents` separates queue mechanics from event interpretation. The handler defines what each event means and explicitly rejects unsupported operations. If a handler throws, the event is not silently recorded as successfully processed.

`UndoHistory` maintains separate undo and redo stacks. A new edit clears redo history because the previous future state no longer follows the newly applied change.

The algorithm implementations use index-based candidate collections. `nextGreaterIndices` returns the index of the next strictly greater value, which is useful when the caller needs the location of an element rather than its value. `maximumInWindows` removes expired candidates and discards values that cannot become a future maximum while a newer, larger value remains in the window.

The file uses Node.js's built-in assertion library and requires no third-party packages.

## C++ case study: task scheduling and diagnostics

The C++ program models a small task-processing service. Tasks move through explicit states, and the scheduler uses `std::deque` for FIFO dispatch and `std::unordered_map` for ID-based lookup.

`TaskScheduler::submit` rejects non-positive identifiers, empty names, and duplicate identifiers. `dispatch` removes the oldest pending task and changes its state to `Running`. `finish` accepts only running tasks, preventing a completed task from being completed a second time.

The state model distinguishes queued, running, completed, and failed work. A failed task remains failed because the case study deliberately avoids introducing an unimplemented retry policy. Production retry behavior would need an explicit transition, retry limit, backoff policy, and duplicate-execution safeguards.

`UndoableConfiguration` illustrates a different use of a stack: each update saves the previous configuration, and undo restores the most recent saved value.

The diagnostic algorithms demonstrate monotonic candidate maintenance:

- `nextGreaterValues` stores indices in a vector and resolves smaller values when a greater measurement arrives.
- `slidingMaximum` stores candidate indices in a deque, removes expired indices from the front, and removes dominated values from the back.
- `balancedDelimiters` uses a stack to validate nested delimiter types.

The implementation uses `std::optional` to represent an empty dispatch result, exceptions to report invalid operations, and standard containers to avoid manual memory management. The monotonic algorithms take O(n) time because each input index enters and leaves its candidate structure at most once.

## Java implementation: enterprise work-state management

The Java program separates work data, state transitions, scheduling, and algorithm evaluation.

`WorkItem` is an immutable record that validates its identifier, description, and priority. `WorkRecord` owns mutable execution state and restricts transitions according to an explicit state machine. A successful or cancelled task cannot be restarted, while a failed task may be requeued.

`WorkQueue` maintains a FIFO deque of pending identifiers and a map of work records. This separation allows the scheduler to remove an identifier efficiently while preserving a durable-in-memory record of the task's current state and attempt count.

The queue has a configured capacity. Submission and retry reject operations that exceed it. The implementation does not silently drop old tasks to make room for new ones, since doing so would violate the scheduling contract.

The algorithm utilities demonstrate delimiter matching, next-greater values, sliding-window maxima, and postfix expression evaluation. `evaluatePostfix` uses exact arithmetic checks for addition, subtraction, and multiplication. Division rejects zero divisors and the integer overflow case involving the minimum integer divided by negative one.

The program uses Java 17 language features, including records, switch expressions, immutable collection factories, and `ArrayDeque`. The state transition rules make invalid operations visible as exceptions rather than relying on convention.

## PostgreSQL relational assessment model

The SQL script stores algorithm cases, their inputs, execution results, scheduled work, and work-event history.

### Data relationships

`assessment_cases` defines each problem's category, difficulty, complexity expectation, and description. `algorithm_inputs` associates inputs and expected results with a case. `algorithm_runs` stores observed outputs, pass/fail status, elapsed time, and diagnostics.

`work_items` represents scheduled work, while `work_events` records events associated with each task. Foreign keys preserve the relationship between event history and the corresponding work record.

### Database integrity

The schema uses primary keys, unique identifiers, foreign keys, and check constraints to reject invalid categories, states, priorities, negative durations, and invalid window sizes. The work-item state constraint also enforces basic timestamp consistency, such as requiring a start timestamp for running tasks.

These checks enforce row-level invariants. They do not independently guarantee that every state transition is legal, that an event was emitted for every update, or that two concurrent workers cannot claim the same queued task. A production scheduler would need controlled transactions, appropriate locking, and restricted update permissions to enforce those stronger rules.

### Queries and indexing

`assessment_results` joins case definitions, inputs, and observed executions. Aggregate queries compare run counts, passing counts, and average recorded execution times by category.

The partial index `idx_work_queue_fifo` supports retrieval of queued work in creation order. The query includes `work_id` as a stable tie-breaker when timestamps are equal. The event-history index supports retrieval of a task's latest diagnostic events.

The script uses PostgreSQL arrays for integer sequences, `JSONB` for structured event details, filtered aggregates for pass counts, and transaction boundaries to load the fixture consistently.

The inserted execution times are illustrative fixture values, not measured benchmark results. The SQL stores and analyzes recorded results; it does not execute the stack algorithms itself.

## Monotonic stacks and deques

A monotonic structure maintains an ordering invariant among its unresolved candidates. This invariant eliminates elements that can no longer influence the answer.

### Next greater element

For each index, the objective is to locate the first strictly greater value to its right. Indices are pushed while their values remain unresolved. When a larger value arrives, it resolves every smaller candidate at the top of the stack.

For an array of length n, the worst-case running time is O(n), and the auxiliary space is O(n). Equal values do not resolve one another when the comparison is strictly less than. Changing `<` to `<=` changes the problem from strictly greater to greater than or equal.

### Sliding-window maximum

A window of width k moves across the input. The deque contains indices of values that are still eligible to become a maximum, ordered by decreasing value.

An index is removed from the front after it expires. Indices whose values are no greater than the incoming value can be removed from the back because the incoming value is newer and at least as large. Such older values cannot become a future maximum while the newer value remains in the window.

The algorithm takes O(n) time and O(k) auxiliary space for a window of width k. It is more efficient than independently scanning every window, which takes O(nk) time in the straightforward implementation.

### Largest histogram rectangle

A histogram rectangle has a limiting bar height and a contiguous width. An increasing stack tracks bars whose maximum possible right boundary has not yet been established.

When a shorter bar arrives, each taller bar is removed and its area is calculated using the current position as the right boundary and the new stack top as the preceding smaller boundary. A sentinel height of zero closes the remaining positive bars.

The algorithm runs in O(n) time and uses O(n) auxiliary space. Non-negative heights are required because negative histogram heights do not represent valid rectangle dimensions.

## Parentheses and expression evaluation

Delimiter validation and postfix evaluation use stacks for different reasons.

Delimiter validation records unmatched opening symbols. Every closing symbol must match the latest unmatched opening symbol, so a queue would be inappropriate: FIFO removal would pair symbols in the wrong nesting order.

Postfix evaluation stores numeric operands. When an operator appears, its operands are removed in reverse stack order, the operation is applied, and the result is pushed back. A valid binary postfix expression must finish with exactly one value.

The provided evaluators use integer arithmetic. They do not implement floating-point arithmetic, unary operators, or a complete infix-expression parser. Those are separate language and parsing requirements rather than necessary properties of a basic postfix stack.

## Complexity reference

| Problem | Time | Auxiliary space |
|---|---:|---:|
| Stack push/pop | O(1) | O(n) stored elements |
| Queue enqueue/dequeue | O(1) amortized | O(n) stored elements |
| Parenthesis validation | O(n) | O(n) |
| Postfix evaluation | O(n) | O(n) |
| Next greater element | O(n) | O(n) |
| Daily temperatures | O(n) | O(n) |
| Sliding-window maximum | O(n) | O(k) |
| Largest histogram rectangle | O(n) | O(n) |
| Circular next greater element | O(n) | O(n) |

The linear bounds for monotonic algorithms depend on each element being inserted a bounded number of times and removed at most once. Nested loops do not necessarily imply quadratic time when each iteration permanently removes an element from the candidate structure.

## Assessment edge cases

- Empty inputs should return empty algorithm results when the operation permits them. A sliding window over an empty array is invalid when its width must be positive.
- Repeated values require deliberate comparison operators. Strictly greater element problems must not treat equality as a match.
- A delimiter sequence can have the correct number of opening and closing symbols while still being incorrectly nested.
- Postfix expressions can fail because of insufficient operands, extra operands, invalid tokens, division by zero, or arithmetic overflow.
- Queue capacity is a policy decision. Rejecting excess work preserves existing pending tasks, while silently evicting tasks changes the system's delivery guarantees.
- A task's state and its event history can diverge if updates are performed outside a controlled transaction. Persisted events and state transitions should be designed together when auditability matters.

## Operational and performance considerations

Stacks are well suited to recent-history operations, but a stack alone does not provide durable undo history. Persistence, snapshot versioning, and concurrency controls are separate concerns.

Queues preserve order, but concurrent workers require atomic task claiming and clear failure recovery. In PostgreSQL, a production worker can claim tasks in a transaction using row locking and `FOR UPDATE SKIP LOCKED`, then update the task state before committing. Worker leases or recovery rules are needed for processes that terminate after claiming work.

Monotonic algorithms are efficient because they discard dominated candidates. They are not universally interchangeable: a next-greater stack tracks unresolved elements, while a sliding-window deque must also expire elements by index. Choosing the correct invariant is more important than choosing a container with a particular name.

Benchmark results should be measured with repeatable input distributions, including increasing, decreasing, repeated, and random values. Recorded execution times should identify their environment and measurement method before they are used to compare implementations.
