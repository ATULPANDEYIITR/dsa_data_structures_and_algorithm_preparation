# Stack Fundamentals: Array and Linked-List Implementations

## Overview

A stack is a linear data structure that follows **Last In, First Out (LIFO)**. The last element inserted is the first element removed. A stack exposes one principal access point, called the **top**.

Stacks are used in expression evaluation, function-call management, undo operations, browser navigation, depth-first search, and task processing that requires the most recently added item to be handled first.

This project implements stacks using arrays and linked lists in Python, JavaScript, C++, and Java. The PostgreSQL script models stack contents and operations as persistent relational records.

## Core Operations

| Operation | Behavior | Expected time |
|---|---|---|
| `push(value)` | Add an element to the top | O(1) amortized for a dynamic array; O(1) for a linked list |
| `pop()` | Remove and return the top element | O(1) |
| `peek()` | Return the top element without removing it | O(1) |
| `is_empty()` / `isEmpty()` | Check whether the stack contains elements | O(1) |

The size of a stack is zero immediately after construction. A push increases the size by one, and a successful pop decreases it by one. Peek and is-empty do not modify the stack.

A pop or peek on an empty stack is an **underflow condition**. The implementations report this condition explicitly instead of returning an arbitrary value that could be confused with valid data. A bounded array stack can also reject a push when its configured capacity has been reached.

## Array-Based Stack

An array-based stack stores elements in a contiguous sequence or a dynamic array abstraction. In Python, the implementation uses a list. JavaScript uses a private array, Java uses an `ArrayList`, and C++ uses a `std::vector`.

The top is represented by the last element. Pushing appends to the end, popping removes the final element, and peeking reads the last element without changing the collection.

Dynamic arrays provide amortized O(1) push operations. Most appends are constant time, but an append that triggers allocation and copying can take O(n). Pop and peek at the end remain O(1).

The Python, JavaScript, and Java implementations support an optional capacity. This introduces a clear distinction between an empty stack and a full stack. The C++ incident console uses a linked stack for incident records and a bounded array stack for short-lived alert labels.

## Linked-List Stack

A linked-list stack represents each element as a node containing a value and a reference to the next node. The top pointer references the head of the list.

During push, a new node is created and its next reference points to the previous top. The new node then becomes the top. During pop, the top node is removed from the chain and the top pointer advances to the next node.

Both operations take O(1) time. The structure does not need to shift existing elements or resize a contiguous array. Each node requires additional memory for its reference, and node allocation can have more overhead than appending to a dynamic array.

The Python implementation maintains an explicit size and detaches removed nodes. The JavaScript implementation uses private fields to prevent callers from modifying the top pointer. The C++ implementation uses `std::unique_ptr` to express node ownership and prevent accidental copying of the linked stack. Java maintains the head pointer and size as internal state.

## Choosing an Implementation

| Property | Array-backed stack | Linked-list stack |
|---|---|---|
| Push | O(1) amortized | O(1) |
| Pop | O(1) at the end | O(1) at the head |
| Peek | O(1) | O(1) |
| Storage | Dynamic contiguous storage | Individually allocated nodes |
| Capacity | Can be bounded explicitly | Usually limited by available memory |
| Memory overhead | Lower per element in typical implementations | Extra reference and node-allocation overhead |
| Cache locality | Usually better | Usually weaker |
| Resizing | May occasionally reallocate | No whole-stack resize |
| Implementation complexity | Relatively simple | Requires correct node-link management |

Both representations implement the same abstract behavior. The choice depends on capacity requirements, memory layout, allocation overhead, and the expected workload. Neither representation is universally faster in every environment.

## Python Implementation

The Python program defines a common `Stack` interface, `ArrayStack`, and `LinkedListStack`. Dedicated exceptions distinguish underflow, overflow, and invalid capacity.

The array stack exposes a bottom-to-top snapshot for inspection while iteration yields values from top to bottom. Its snapshot iterator also demonstrates how traversal can remain stable when the underlying stack changes after the iterator is created.

The linked-list stack uses a `Node` dataclass with a value and a reference to the next node. It maintains a separate size counter, avoiding an O(n) traversal when the caller requests the number of elements.

The executable examples demonstrate text reversal, delimiter validation, postfix expression evaluation, and undo history. In postfix evaluation, operands are popped in reverse order: the first pop is the right operand, and the second is the left operand. This distinction is essential for subtraction and division.

The test suite verifies LIFO ordering, underflow, bounded capacity, zero capacity, `None` as a legitimate element, malformed expressions, undo behavior, and snapshot iteration. A seeded randomized test compares both stack implementations against a Python list reference model.

## JavaScript Implementation

The JavaScript file uses private class fields to protect the internal array, capacity, linked-list head, and element count. The public API exposes only the operations needed to manipulate a stack.

The `NavigationHistory` example models browser navigation. Visiting a page pushes the current URL onto the back stack. Going backward pushes the current page onto the forward stack. Visiting a different page after going backward clears the forward stack because the previous forward path is no longer valid.

The `AsyncLifoWorker` example processes asynchronous jobs in LIFO order. It awaits each job before starting the next one, so the execution order is deterministic. The example also rejects concurrent drain attempts. A LIFO worker is appropriate only when recent work should take priority; it is not a substitute for a FIFO queue when fairness or arrival order is required.

The JavaScript checks verify that falsy values such as `0`, `false`, and `null` remain valid stack elements. Empty-state checks must use stack size or explicit emptiness, not the truthiness of the top value.

## C++ Case Study: Incident Response

The C++ program models an incident console in which the newest unresolved incident is retrieved first.

`ArrayStack<T>` uses `std::vector<T>` for alert labels and supports a configured capacity. `LinkedStack<T>` stores incident records in singly linked nodes managed by `std::unique_ptr`. Automatic ownership ensures that nodes are released when their owning pointers are replaced or destroyed.

The `Incident` type validates identifiers, service names, and severity values. `IncidentConsole` provides a domain-specific interface for reporting incidents, inspecting the latest incident, resolving the newest incident, and checking unresolved count.

The console returns `std::optional<Incident>` when resolving an incident. This lets the caller distinguish the absence of a record from a valid incident without fabricating a placeholder. Underflow and overflow use dedicated exception types, while invalid incident data is rejected before it enters the stack.

The scenario illustrates both the value and limitation of LIFO. It works when the latest incident should be examined next, but a real incident-response service should not rely on LIFO alone to prioritize severity. High-severity incidents may require a priority queue or another explicit scheduling policy.

## Java Implementation: Document Approval History

The Java program uses a generic `Stack<T>` interface so that array and linked-list implementations expose the same operations while retaining separate storage mechanisms.

`ArrayStack<T>` uses an `ArrayList` and can enforce a configured capacity. Its iterator traverses a snapshot from top to bottom, and its snapshot method returns an unmodifiable copy of the underlying sequence.

`LinkedStack<T>` maintains a node reference and a size counter. Its iterator captures the current chain into a list before traversal. These snapshots are shallow: the sequence of element references is fixed, but mutable objects stored as elements are not automatically copied.

The enterprise example stores immutable `DocumentVersion` records in a linked stack. Saving a revision pushes a new version. Reverting removes the current revision and reveals the preceding version. The original version cannot be removed, which is enforced by the history service.

`ApprovalWorkflow` models a limited document-submission lifecycle. It validates which statuses may transition into submitted, approved, or rejected states. Its pending action stack demonstrates LIFO processing independently of the document-version history.

The workflow is illustrative rather than a complete approval platform. A production service would also need identity verification, authorization, persistent history, concurrent-update protection, and a clearly defined policy for preserving rejected revisions.

## PostgreSQL Data Model

The SQL script uses three tables to represent stack state and its operation history.

- `stack_registry` identifies each stack, its implementation label, and its optional capacity. The unique stack name prevents duplicate identifiers at the business level.
- `stack_items` stores the current elements. The composite primary key `(stack_id, position)` prevents duplicate positions within one stack. The highest position represents the top.
- `stack_operations` records push, pop, peek, and is-empty operations, including whether the operation succeeded and why it failed.

The `stack_top` view uses a lateral query to retrieve the highest-position item for every registered stack. The descending index on `(stack_id, position)` supports top-element lookups.

The `stack_push`, `stack_pop`, `stack_peek`, and `stack_is_empty` functions provide the principal operations. Push locks the registry row before determining the next position and checking capacity. Pop removes the item with the highest position. Peek records an inspection without deleting the item, and is-empty checks whether any item remains.

The sample data exercises both array-style and linked-list-style models. It demonstrates a successful pop, a capacity failure, an empty-stack pop, and the audit trail of successful and unsuccessful operations.

The SQL representation is a persistent model of stack behavior, not an in-memory array or linked list. Database indexes, row locks, transaction isolation, and record persistence have different costs from pointer updates in application memory. The registry-row lock serializes push and pop operations that use these functions for a particular stack, but applications must still handle transaction failures and concurrent access correctly.

## Edge Cases and Correctness

An empty stack must remain empty after a failed pop or peek. The implementations preserve this invariant by checking emptiness before changing the top element.

For every successful push, the size increases by one. For every successful pop, the size decreases by one. A peek leaves both size and element order unchanged.

A bounded stack must reject a push before adding an element when the capacity has been reached. A capacity of zero means that no element can be inserted.

Valid elements should not be confused with the absence of an element. For example, Python permits `None`, JavaScript permits `null`, and C++ can store an object whose value is zero. Emptiness should therefore be determined through explicit state, not by interpreting the top value as a Boolean.

In a linked-list implementation, pointer updates must preserve the remaining chain. Removing the top requires advancing the head to the removed node's successor. Incorrect pointer ordering can lose access to every remaining element.

## Performance and Production Considerations

Push and pop at the top are the defining efficient operations of a stack. Removing elements from the beginning of an ordinary array-backed list is generally less efficient because the remaining elements may need to shift.

Array stacks usually have favorable memory locality and lower per-element overhead. Linked stacks avoid whole-array resizing but allocate individual nodes and store additional references. Both require O(n) storage for n elements.

These implementations are not inherently thread-safe. Concurrent pushes and pops can corrupt the expected logical order unless access is synchronized or serialized. The SQL version addresses database-level coordination by locking each stack's registry row during mutations.

In production systems, stack behavior should be chosen to match the actual workflow. Undo histories and nested evaluation naturally fit LIFO semantics. Work that must be handled in arrival order belongs in a queue, while work prioritized by urgency may require a priority queue.
