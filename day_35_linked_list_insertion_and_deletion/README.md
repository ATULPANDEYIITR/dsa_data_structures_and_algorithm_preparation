# Linked-List Insertion and Deletion

## Scope

This learning artifact focuses on a **singly linked list** and the structural operations used to insert and delete nodes:

- Insert at the beginning
- Insert at the end
- Insert at a position
- Delete the first node
- Delete the last node
- Delete by value
- Delete by position

The implementations deliberately treat insertion and deletion as **link-management operations** rather than as array operations. A linked list does not move a block of elements when a node is inserted. Instead, it changes references between nodes.

Positions in the Python, JavaScript, C++, and Java implementations are **zero-based**. Position `0` identifies the first node. For insertion, the position equal to the current size is also valid because it represents insertion immediately after the existing final node.

The SQL implementation uses an explicit `position_no` because a relational table does not expose memory pointers. It demonstrates how the same logical operations can be represented with ordered rows and transactional updates.

---

## Core Structure

A singly linked list consists of nodes. Each node contains:

- a value or domain object
- a reference to the next node

The final node has a next reference of `null`, `None`, or an equivalent null pointer.

The conceptual structure is:

`HEAD -> Node A -> Node B -> Node C -> NULL`

The head reference is especially important. If it is lost without another reference to the first node, the rest of the list becomes unreachable.

A node does not normally know which node precedes it. This distinction explains why some operations are constant time while others require traversal.

### Insertion at the beginning

Suppose the list is:

`A -> B -> C`

To insert `X` at the beginning:

`X -> A -> B -> C`

Only two relationships are required:

- make `X.next` point to the old head
- make `head` point to `X`

The operation is **O(1)** because it does not depend on the number of nodes.

### Insertion at the end

For a singly linked list containing only a head reference, the implementation must traverse:

`A -> B -> C -> NULL`

until it reaches `C`. It then changes `C.next` from `NULL` to the new node.

This is **O(n)** with the head-only representation.

A list could maintain a separate tail reference and make ordinary end insertion **O(1)**. That design introduces an additional invariant: every operation that can remove or replace the final node must keep the tail reference correct.

### Insertion at a position

For:

`A -> B -> C`

inserting `X` at position `1` produces:

`A -> X -> B -> C`

The implementation first reaches the node before the target position, `A`. It then performs the equivalent of:

`X.next = A.next`

followed by:

`A.next = X`

The order matters. If the original successor is not saved before redirecting the predecessor, the remainder of the list can become unreachable.

Position insertion is **O(n)** in the worst case because locating the predecessor may require traversal.

---

## Deletion Mechanics

Deletion does not physically shift every later node. It removes a node from the reachable chain by redirecting a link.

### Delete the first node

Given:

`A -> B -> C`

deleting the first node changes the head from `A` to `B`:

`B -> C`

This is **O(1)**.

The old first node no longer belongs to the list. Languages with automatic memory management can eventually reclaim it when no references remain. In C++, the implementation uses `std::unique_ptr`, so ownership is released through RAII.

### Delete the last node

Given:

`A -> B -> C`

the final node is `C`, but a singly linked node does not know that `B` is its predecessor.

The algorithm therefore finds `B` and changes:

`B.next = C`

to:

`B.next = NULL`

This is **O(n)**.

The one-node boundary requires special treatment. When the list is:

`A -> NULL`

deleting the last node is equivalent to deleting the first node.

### Delete by value

Deletion by value requires searching for a matching node.

For:

`A -> B -> C -> D`

if `C` matches, the predecessor `B` is found and its successor is changed from `C` to `D`.

The resulting list is:

`A -> B -> D`

The search is **O(n)** in the worst case.

The implementations deliberately specify the duplicate-value behavior. If several nodes contain the same value, the first matching node is removed. A production API could instead provide operations such as delete-all-matches, delete-by-unique-ID, or return the number of removed nodes.

### Delete by position

Deleting a node at position `p` requires reaching the node immediately before `p`.

For:

`A -> B -> C -> D`

deleting position `2` means locating `B`, then changing its successor from `C` to `D`.

The operation is **O(n)** in the worst case.

Deleting position `0` is delegated to the constant-time first-node operation.

---

## Invariants

Correct linked-list implementations maintain structural invariants.

The Python implementation uses `check_integrity()`. The JavaScript implementation uses `verifyIntegrity()`. The C++ and Java programs expose equivalent invariant checks.

The important invariants include:

- An empty list has a null head.
- A non-empty list has a reachable first node.
- The final reachable node has no successor.
- The recorded size equals the number of reachable nodes.
- A normal singly linked list does not contain a cycle.
- An insertion changes the size by exactly one.
- A successful deletion changes the size by exactly one.
- An unsuccessful delete-by-value operation does not change the list.
- A failed positional operation does not modify the list.

The cycle checks use **Floyd's tortoise-and-hare technique**. One traversal pointer moves one node at a time while another moves two. If they meet, a cycle exists.

Cycle detection is not required for every linked-list operation, but it is valuable when debugging pointer manipulation because a single incorrect assignment can cause traversal to continue indefinitely.

---

## Python Implementation

The Python program in the first deliverable uses a `Node` dataclass and a `LinkedList` class.

The class maintains both `head` and `_size`. `_size` avoids repeatedly traversing the entire list merely to determine its current length.

`insert_beginning()` demonstrates the simplest pointer change. `insert_end()` deliberately traverses from the head so the cost of a head-only singly linked representation remains visible.

`insert_position()` handles three distinct boundary cases:

- position `0`
- an interior position
- position equal to the current size

`delete_first()` changes the head directly. `delete_last()` searches for the predecessor of the tail. `delete_by_value()` searches for the first matching node and bypasses it. `delete_by_position()` reaches the predecessor associated with the requested position.

The Python implementation also demonstrates:

- empty-list exceptions
- invalid positions
- duplicate values
- unsuccessful value deletion
- list reversal as an example of systematic link reassignment
- cycle and size-integrity validation
- search by value
- operation-complexity reporting

The `practice_scenario()` uses change identifiers as values to show that the same data structure can hold domain objects rather than only simple integers.

---

## JavaScript Implementation

The JavaScript program uses explicit `Node` and `SinglyLinkedList` classes.

It complements the Python implementation by emphasizing JavaScript's object-reference model and an event-driven operation layer.

The event-driven demonstration receives operation objects such as an append, prepend, positional insertion, value deletion, or positional deletion. A dispatcher maps each event type to the appropriate linked-list method.

This separates **what operation was requested** from **how node links are changed**.

The JavaScript implementation also uses `Object.is()` for value comparison. This gives the value-deletion operation explicit JavaScript comparison semantics rather than relying on implicit coercion.

Validation is performed before positional operations. A negative position and a position greater than the list size are rejected for insertion. For deletion, a position must refer to an existing node.

The `verifyIntegrity()` method checks both cycles and the stored size. This is particularly useful in JavaScript because objects are references, so an incorrect `next` assignment can make multiple nodes reachable through an unintended structure.

---

## C++ Case Study

The C++ implementation models a **deployment pipeline job list**.

Each node contains a `Job` with:

- a positive job ID
- a job name
- a priority from 1 through 5

The linked-list class uses `std::unique_ptr<Node>` for ownership.

This is an important implementation choice. Each node owns its successor. When a link is removed, ownership is transferred or released through `std::unique_ptr`, reducing the risk of manual memory leaks.

The implementation does not use an external library.

### Ownership during insertion

For insertion into an interior position, the new node first receives ownership of the existing successor. The predecessor then receives ownership of the new node.

Conceptually:

`previous -> old_successor`

becomes:

`previous -> new_node -> old_successor`

The ownership transfers preserve the entire remaining chain.

### Ownership during deletion

For deletion by ID or position, the predecessor owns the node being removed. The implementation moves that node into a temporary smart pointer, reconnects the predecessor to the removed node's successor, and returns the removed domain object.

This makes the deletion operation explicit without requiring calls to `delete`.

### Validation

`makeJob()` enforces domain constraints before a `Job` enters the list. The linked list separately validates positional constraints and structural integrity.

The case study therefore separates:

- **domain validation**, such as legal priority
- **list validation**, such as legal position
- **structural validation**, such as no cycle and correct size

This separation is useful in larger systems because invalid business data and corrupted data structures are different failure classes.

---

## Java Enterprise-Oriented Model

The Java implementation models an **approval request queue**.

An `ApprovalRequest` is an immutable Java record containing:

- `requestId`
- repository name
- priority

The record constructor validates required values, while the `Priority` enum restricts priority to a controlled domain.

The linked-list implementation remains mutable because insertion and deletion are inherently state-changing operations, but the individual approval request objects are immutable.

This separation is useful in enterprise systems: the collection changes over time, while a request's identity and descriptive attributes should not unexpectedly change after it has entered a workflow.

### Domain-specific deletion

The Java implementation uses `requestId` for value-based deletion rather than deleting based on the entire record object.

This represents a common application design decision. A stable identifier is usually a safer deletion key than a mutable or composite description.

`deleteByRequestId()` returns `Optional<ApprovalRequest>`. This distinguishes successful deletion from a missing request without returning `null`.

### Boundary behavior

The program explicitly exercises:

- deletion from an empty queue
- insertion beyond the legal position range
- deletion at the position equal to the current size
- deletion of a missing request ID
- normal one-node behavior

These cases are important because linked-list algorithms often fail at boundaries rather than in the middle of a long list.

---

## SQL Representation

A relational database does not expose linked-list pointers in the same way an in-memory node structure does.

The SQL implementation therefore represents order using `position_no`.

A simplified relational state is:

| position_no | item_code | meaning |
|---:|---|---|
| 0 | JOB-099 | first item |
| 1 | JOB-101 | second item |
| 2 | JOB-102 | third item |
| 3 | JOB-103 | later item |

The database uses a unique constraint on `position_no`, so two rows cannot occupy the same logical position.

`item_code` is also unique, making it suitable for value-based deletion.

### Insert at beginning

The database shifts every existing position upward before inserting a row at position zero.

This is not pointer manipulation. It is an ordered-set transformation performed transactionally.

The transaction matters because the intermediate state can temporarily contain conflicting positions. The final operation should be visible as one logical change to other transactions according to the database's transaction semantics.

### Insert at end

The SQL implementation obtains the current maximum position and inserts at the next position.

An empty table is handled with `COALESCE`, causing the first row to receive position zero.

### Insert at position

Rows at or after the requested position are shifted by one before the new row is inserted.

For large queues, this can be expensive because many rows may need updates. This illustrates an important distinction between linked lists and relational storage: an in-memory linked list changes a small number of pointers, while a position-based SQL representation may modify many rows.

### Delete first and delete last

Deleting the first row removes position zero and shifts the remaining positions downward.

Deleting the last row does not require a shift because no later position exists.

### Delete by value

The SQL script uses `item_code` as the stable value/key and removes the matching row. The position gap is subsequently closed with a window-function-based update.

### Delete by position

The row at the specified position is deleted and later positions are decremented.

The script includes a validation query that checks whether positions are contiguous and whether duplicate positions exist.

---

## Complexity

For the head-only singly linked lists used by the main implementations:

| Operation | Worst-case time | Reason |
|---|---:|---|
| Insert at beginning | O(1) | Head is changed directly |
| Insert at end | O(n) | The tail must be located |
| Insert at position | O(n) | The predecessor may require traversal |
| Delete first | O(1) | Head moves to its successor |
| Delete last | O(n) | The predecessor of the tail must be found |
| Delete by value | O(n) | The list may require a full search |
| Delete by position | O(n) | The predecessor may require traversal |
| Find by value | O(n) | Nodes are examined sequentially |

The linked list stores **O(n)** nodes.

An additional tail reference can reduce end insertion to O(1), but it does not automatically make end deletion O(1) for a singly linked list. The predecessor of the tail is still required.

A doubly linked list changes this trade-off because each node can reference both its successor and predecessor.

---

## Edge Cases

### Empty list

Insertion at the beginning or end must create the first node and update the head.

Deletion from an empty list must fail in a controlled way rather than dereferencing a null reference.

### One-node list

For:

`A -> NULL`

both deleting the first and deleting the last remove the same node and leave an empty list.

This is a distinct boundary case because the general multi-node algorithm expects a predecessor that does not exist.

### Insertion at position zero

This is equivalent to insertion at the beginning and should reuse the same logic rather than duplicate pointer manipulation.

### Insertion at position equal to size

If the list contains four nodes, positions `0` through `4` are legal for insertion. Position `4` means append after the existing final node.

### Deletion at position equal to size

This is invalid. If the list has four nodes, valid deletion positions are `0` through `3`.

### Missing value

Delete-by-value should have a defined behavior when no match exists. The implementations return a failure indication rather than modifying an unrelated node.

### Duplicate values

A value may occur more than once. The implementations delete the first match. This rule prevents ambiguity while keeping the operation deterministic.

---

## Common Implementation Errors

### Losing the successor during insertion

For an interior insertion, changing the predecessor's `next` pointer before preserving the old successor can disconnect the remainder of the list.

The safe conceptual sequence is:

`new.next = previous.next`

then:

`previous.next = new`

### Forgetting the head boundary

Generic predecessor-based deletion does not work for position zero because the first node has no predecessor inside the list.

The first-node case should be handled separately.

### Incorrect size tracking

Every successful insertion must increment the size exactly once. Every successful deletion must decrement it exactly once.

Delegating position zero to `deleteFirst()` while also changing the size in the caller is a common source of double updates.

### Returning the wrong duplicate

A delete-by-value implementation should explicitly define whether it removes the first, last, or all matching values. The implementations here remove the first matching value.

### Mishandling the tail

Deleting the last node from a singly linked list requires changing the predecessor's successor to null.

If a design also maintains a tail pointer, deleting the last node must update both the predecessor link and the tail reference.

### Confusing position with value

A position is an index in the current ordering. A value identifies data stored in a node.

Deleting by position and deleting by value are therefore different operations even if both ultimately remove one node.

---

## Debugging Strategy

When an insertion or deletion behaves incorrectly, inspect the structure rather than only the printed values.

For each affected operation, verify:

`previous -> target -> successor`

before the operation and:

`previous -> successor`

after a deletion.

For insertion, verify:

`previous -> new_node -> successor`

The integrity checks included in the implementations detect two high-value failure classes:

- cycles
- disagreement between the recorded size and the number of reachable nodes

A debugger can also be used to inspect the head and each `next` reference immediately before and after the mutation.

---

## Design Trade-offs

A singly linked list is useful when operations frequently occur near the head or when stable node linkage is more important than random access.

It is a poor substitute for an array when the primary requirement is fast indexed lookup. Accessing position `p` requires traversal from the head and is O(n).

The absence of backward links saves memory per node but makes operations involving predecessors more expensive.

A tail pointer improves append performance but adds state that must remain synchronized.

A doubly linked list increases per-node storage but can simplify deletion when the node itself is already known.

A relational position model, as shown in the SQL script, has a different performance profile. Reordering rows can require updates to many records, while database constraints provide strong persistence and integrity guarantees.

---

## Practical Relationship Between the Operations

The seven practice operations are not independent algorithms. They are combinations of a small set of structural ideas.

Insertion changes the successor relationship so that a new node becomes reachable.

Deletion changes the successor relationship so that a node becomes unreachable.

Insertion at the beginning is special because the head itself changes.

Deletion of the first node is special for the same reason.

Insertion at an interior position requires the predecessor and its current successor.

Deletion at an interior position also requires the predecessor because a singly linked node does not have a backward reference.

Deletion by value adds a search phase before the structural deletion.

Deletion by position adds a traversal phase based on the requested index.

Understanding these relationships makes the implementation easier to reason about than memorizing seven unrelated procedures.
