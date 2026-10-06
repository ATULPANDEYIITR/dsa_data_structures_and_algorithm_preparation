# Reverse Linked List: Iterative and Recursive Reversal

## Scope

This implementation studies reversal of a singly linked list through two distinct algorithms:

- **Iterative reversal**, which redirects node links using a small fixed set of references.
- **Recursive reversal**, which reaches the original tail through recursion and redirects links while the call stack unwinds.

The central operation is the same in both cases: the existing `next` relationships are reversed in place. The important difference is how the algorithm manages traversal state and auxiliary memory.

The six deliverables use different representations of the same problem. Python emphasizes executable algorithmic behavior and validation. JavaScript emphasizes object references and runtime behavior. C++ examines ownership and pointer-management concerns. Java models the operation through domain-oriented classes and invariant checks. PostgreSQL represents list order relationally rather than through memory pointers. This distinction is important because a relational table does not contain a direct equivalent of an in-memory `next` pointer.

## Singly Linked List Model

A singly linked list consists of nodes where each node contains a value and a reference to the next node.

For a list containing `10 -> 20 -> 30 -> 40`, the logical relationships are:

`10.next = 20`

`20.next = 30`

`30.next = 40`

`40.next = null`

Reversal must transform those relationships into:

`40.next = 30`

`30.next = 20`

`20.next = 10`

`10.next = null`

The original head becomes the new tail, while the original tail becomes the new head.

The operation does not require allocating another linked list. The nodes themselves are reused and their links are redirected.

## Iterative Reversal

The iterative algorithm maintains three references:

`previous` represents the already reversed portion.

`current` represents the node whose link is currently being changed.

`following` preserves the unreversed remainder before `current.next` is modified.

The essential transition is:

`following = current.next`

`current.next = previous`

`previous = current`

`current = following`

The order of these operations matters. If `current.next` is changed before the old successor is saved, the algorithm can lose access to the remaining nodes.

For a list `10 -> 20 -> 30`, the first iteration changes:

`10 -> 20`

into:

`10 -> null`

while `20 -> 30` remains accessible through `following`.

The next iteration changes `20 -> 30` into:

`20 -> 10`

and the process continues until `current` becomes `null`.

### Iterative complexity

The algorithm visits every node exactly once.

- Time: `O(n)`
- Auxiliary space: `O(1)`
- Node allocation: none
- Recursion depth: none

The iterative implementation is generally the safest choice when the list may contain a very large number of nodes.

## Recursive Reversal

Recursive reversal uses a different control-flow model.

For:

`10 -> 20 -> 30 -> 40`

the recursive calls continue until the final node, `40`, is reached.

At that point, `40` becomes the new head. During stack unwinding, the predecessor is attached after its successor.

For the pair `30 -> 40`, the critical transformation is:

`40.next = 30`

followed by:

`30.next = null`

The operation is represented in the implementations by:

`current.next.next = current`

and:

`current.next = null`

The second assignment is essential. Without clearing the old forward link, the reversal would create a cycle.

### Recursive complexity

Every node is processed once, but every recursive call consumes stack space.

- Time: `O(n)`
- Auxiliary space: `O(n)` for the call stack
- Node allocation: none
- Recursion depth: proportional to list length

The algorithm is conceptually elegant, but recursion depth is a practical constraint in Python, JavaScript, Java, and C++. Stack capacity is finite, so recursive reversal should not automatically be considered equivalent to iterative reversal for production workloads.

## Head and Tail Invariants

A correct linked-list implementation must maintain structural invariants.

For an empty list:

`head == null`

`tail == null`

For a non-empty list:

`head != null`

`tail != null`

`tail.next == null`

The node count must remain unchanged after reversal.

If the original list contains `n` nodes, reversal must still contain exactly `n` nodes.

A second reversal should restore the original ordering:

`reverse(reverse(list)) == list`

This property is used by the implementations as a practical correctness check.

## Python Implementation

The Python implementation defines `Node` and `LinkedList` classes.

`reverse_iterative()` implements the constant-space pointer algorithm. It explicitly preserves the old successor before redirecting `current.next`.

`reverse_recursive()` uses a nested recursive helper. The base case handles both an empty list and a single-node suffix. The recursive case returns the new head obtained from the suffix and then redirects the current node behind its successor.

The class also maintains `head`, `tail`, and `size`. The `to_list()` method detects accidental cycles by tracking node identities. This is useful when debugging reversal code because an incorrectly cleared link can otherwise make traversal continue indefinitely.

The Python program also demonstrates a practical recursion safety policy. Python has a recursion limit, so recursive reversal of a sufficiently large list can fail even though the algorithm is mathematically correct. The implementation therefore provides `reverse_recursive_safe()` and demonstrates why iterative reversal is preferable for large inputs.

## JavaScript Implementation

The JavaScript implementation uses object references through `ListNode`.

The iterative method uses `previous`, `current`, and `nextNode`. JavaScript's reference semantics mean that changing `current.next` changes the actual linked structure rather than copying the node.

The recursive implementation uses a nested `reverse()` function. The returned node is the new head of the reversed suffix.

The JavaScript file also includes a recursion safety guard. JavaScript does not provide a portable standard mechanism for determining the available call-stack depth, so the example uses a configurable node-count policy rather than pretending that recursion can safely handle arbitrarily large lists.

This implementation also demonstrates JavaScript-specific runtime concerns through `Set`-based cycle detection and `RangeError` for an intentionally rejected recursive workload.

## C++ Case Study

The C++ program treats linked-list reversal as a pointer-ownership problem.

The list uses `std::unique_ptr<Node>` for ownership. This makes node lifetime explicit and prevents accidental memory leaks from normal list destruction.

The iterative implementation moves ownership through the list:

- `current` owns the remaining unreversed suffix.
- `previous` owns the reversed prefix.
- `following` temporarily owns the next part of the unreversed suffix.

The use of `std::move` is important because `unique_ptr` is non-copyable. Ownership must be transferred rather than duplicated.

The C++ case study also demonstrates a recursive educational implementation. It intentionally exposes an important design trade-off: a recursive algorithm can be logically correct while a particular ownership representation introduces additional traversal work. The implementation therefore distinguishes the conceptual recursive reversal from the performance characteristics of a specific ownership strategy.

This is a useful systems-level distinction. Algorithmic complexity is determined not only by the abstract recurrence but also by the data structure operations used to implement each recursive step.

The program validates node counts, empty lists, single-node lists, two-node lists, and round-trip reversal.

## Java Implementation

The Java program models the list with a private `Node` class and a `SinglyLinkedList` domain class.

The list explicitly maintains:

- `head`
- `tail`
- `size`

The reversal methods update these fields so the list remains structurally valid after the operation.

The recursive implementation uses a private `reverse()` method. Its base case returns the current node when no successor exists. The recursive result becomes the new head, while stack unwinding performs the link reversal.

`isValid()` checks the structural invariants, including the relationship between the recorded size and the number of reachable nodes. It also ensures that the tail has no successor.

`ReversalService` separates the choice of reversal strategy from the list's data representation. This gives the example an enterprise-oriented structure without adding unnecessary framework dependencies.

## PostgreSQL Representation

An in-memory linked list uses direct references between nodes. A relational database uses rows, keys, and relationships instead.

The SQL implementation therefore represents logical linked-list order through:

- `linked_lists` for list identity.
- `list_nodes` for node values and positions.
- `reversal_runs` for recording reversal operations.
- `reversal_snapshots` for associating captured reversal state with an operation.

The `(list_id, position)` unique constraint ensures that two nodes cannot occupy the same logical position in one list.

The `position` field provides the database equivalent of sequence order. Reversal can therefore be expressed by changing each position according to:

`new_position = max_position - old_position + 1`

For positions `1, 2, 3, 4`, this produces `4, 3, 2, 1`.

The SQL script uses PostgreSQL-compatible syntax and demonstrates transactional updating. The reversal is performed inside a transaction so that the position changes form one atomic database operation.

A recursive common table expression is also used to traverse positions in reverse order. This demonstrates an important distinction: SQL recursion is not the same mechanism as recursive pointer manipulation in an in-memory data structure. PostgreSQL recursively evaluates rows and relationships; it does not recursively dereference C++-style memory pointers.

## Database Integrity

The relational model enforces structural rules with database constraints rather than depending exclusively on application code.

`PRIMARY KEY` constraints identify lists, nodes, and reversal runs.

`FOREIGN KEY` constraints ensure that nodes belong to existing lists and that reversal records refer to existing lists.

`UNIQUE (list_id, position)` prevents duplicate positions within a list.

`CHECK` constraints prevent invalid positions and unsupported reversal-run states.

The index on `(list_id, position)` supports queries that retrieve a list in logical order.

The SQL demonstration intentionally attempts a duplicate position and catches PostgreSQL's `unique_violation`, showing that an invalid state can be rejected by the database itself.

## Iterative Versus Recursive

| Property | Iterative reversal | Recursive reversal |
|---|---|---|
| Time | `O(n)` | `O(n)` |
| Auxiliary space | `O(1)` | `O(n)` call stack |
| Uses recursion | No | Yes |
| Stack-depth risk | No | Yes |
| Pointer/link mutation | Direct | During stack unwinding |
| Large-list suitability | Strong | Limited by runtime stack |
| Conceptual structure | State maintained explicitly | State maintained by call stack |

Both algorithms perform the same logical transformation, but their resource behavior is different.

The iterative algorithm stores traversal state in local variables. The recursive algorithm stores part of that state in activation records on the call stack.

## Edge Cases

An empty list has no node to reverse. Both algorithms should leave it unchanged.

A single-node list already satisfies the reversed ordering because there is no successor to redirect.

A two-node list exposes the essential reversal operation clearly. For `1 -> 2`, the result must be `2 -> 1`, with `1.next == null`.

Repeated reversal is another useful correctness test. Reversing twice should return the list to its original sequence.

The tail pointer is an important edge case. A reversal that correctly changes `head` but leaves `tail` pointing to the old head incorrectly represents the list to callers that depend on constant-time tail access.

## Common Implementation Errors

A frequent iterative error is failing to save the old successor before changing `current.next`. This disconnects the remainder of the list.

A frequent recursive error is performing `current.next.next = current` but forgetting `current.next = null`. That leaves the old forward edge in place and can create a cycle.

Another error is changing the head but not the tail. The node sequence may look correct during forward traversal while the list metadata is inconsistent.

Another problem is assuming recursive reversal has the same memory behavior as iterative reversal. Both use `O(n)` time, but recursive reversal consumes `O(n)` stack space.

A production implementation should also consider whether the runtime can support the maximum expected list length before selecting recursion.

## Practical Interpretation

The reversal operation is a compact example of state transformation.

The iterative algorithm makes that state explicit through local references. At any point, the list is divided conceptually into a reversed prefix and an unreversed suffix.

The recursive algorithm divides the problem differently. It delegates the suffix to a recursive call and performs the local link transformation after the suffix has been reversed.

Both approaches are in-place with respect to node allocation. The difference is not whether nodes are copied, but where the algorithm stores the information needed to continue processing.

The Python, JavaScript, Java, and C++ programs therefore demonstrate the same linked-list transformation through different runtime and memory models, while the SQL script demonstrates how ordering and reversal are represented when the underlying storage model consists of relational rows rather than memory references.

## Production Considerations

For an application that may process very long linked lists, iterative reversal is normally the safer implementation because its auxiliary memory usage remains constant and it does not consume one call-stack frame per node.

For recursive implementations, maximum input depth should be treated as a runtime constraint rather than an abstract theoretical detail.

When a linked list is shared between multiple components, reversal is a mutation of shared state. Callers holding references to individual nodes can observe the changed links immediately. An API should therefore make mutation semantics clear.

Cycle detection can be valuable during development and debugging because a single incorrect link can turn an ordinary traversal into an infinite loop.

The central correctness conditions remain simple: every original node must remain reachable exactly once, the ordering must be reversed, the new tail must have no successor, and the node count must remain unchanged.
