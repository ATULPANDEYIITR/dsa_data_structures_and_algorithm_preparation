# Fast and Slow Pointers

Fast and slow pointers are a constant-space technique for traversing linked structures at different rates. The central pattern maintains two references to nodes: a slow pointer advances one node at a time, while a fast pointer advances two nodes at a time.

This difference in movement speed creates two useful behaviors.

For a finite linked list, the fast pointer reaches the end while the slow pointer has covered approximately half the distance. This makes the technique useful for finding a middle node without first calculating the list length.

For a cyclic linked list, the fast pointer eventually catches the slow pointer. This is the basis of Floyd's cycle detection algorithm.

The important distinction is that the pointers are not searching for values. They are following links between nodes. Cycle detection therefore compares node identity, not merely payload equality.

## Core pointer model

Consider a list shaped like:

`A -> B -> C -> D -> E -> null`

At the beginning, both pointers reference `A`.

After one iteration:

`slow = B`

`fast = C`

After another iteration:

`slow = C`

`fast = E`

The fast pointer has moved approximately twice as far as the slow pointer. When `fast` can no longer make another two-node movement, `slow` identifies the middle according to the chosen even-length convention.

The implementations deliberately expose both middle conventions.

The second-middle convention returns `C` for `A -> B -> C -> D`.

The first-middle convention returns `B` for the same four-node list.

Neither convention is universally correct. The appropriate choice depends on the operation that follows. Splitting a list, for example, may require one convention so that the two resulting portions have the desired sizes.

## Floyd's cycle detection

Floyd's algorithm uses two phases.

During the detection phase, `slow` moves one node and `fast` moves two nodes per iteration. If the structure is acyclic, `fast` eventually becomes `null`. If a cycle exists, both pointers eventually occupy the same node.

The important implementation condition is effectively:

`fast != null && fast.next != null`

Without both checks, a two-step movement can attempt to follow a missing link.

The meeting point does not necessarily represent the beginning of the cycle. It is simply a node somewhere inside the cycle.

The second phase finds the entry. One pointer is reset to the head while the other remains at the meeting point. Both then advance one node at a time. Their next meeting point is the first node of the cycle.

This property follows from the distances traveled before and within the cycle. If the non-cyclic prefix has length `mu` and the cycle has length `lambda`, the first meeting occurs at a position whose modular relationship to the cycle entry allows equal-speed traversal from the head and meeting point to converge at that entry.

## Why node identity matters

Suppose two different nodes both contain the value `42`.

`nodeA.value == nodeB.value`

does not imply:

`nodeA == nodeB`

The Python implementation uses `is`, JavaScript uses `===`, C++ compares pointers, and Java uses `==` for object identity.

This distinction is essential for cycle detection. A list containing repeated values is not necessarily cyclic.

For example:

`42 -> 17 -> 42 -> null`

contains two different nodes with the value `42`, but it is acyclic.

A cycle exists only when a link eventually returns to an already existing node object.

## Python implementation

The Python program uses a `ListNode` class to represent a singly linked node. Its `find_middle_node` function implements the one-step/two-step traversal pattern and returns the second middle for even-sized lists.

The `has_cycle` function contains the basic Floyd algorithm. It does not allocate a set of visited nodes, which keeps its auxiliary space at O(1).

`find_cycle_entry` implements the second phase of Floyd's algorithm. `cycle_length` traverses the cycle once after its entry has been identified, while `distance_to_cycle_entry` measures the non-cyclic prefix.

The program also demonstrates practical use of fast and slow pointers for palindrome detection. It finds the midpoint, reverses the second half, compares both portions, and restores the original list. Restoring the list matters when the function operates on a structure owned by another part of an application.

The self-checks cover empty lists, single-node lists, even and odd lengths, self-cycles, multi-node cycles, and repeated payload values.

## JavaScript implementation

The JavaScript program models nodes as objects and therefore provides a clear demonstration of JavaScript object identity.

Its `traceFloyd` function exposes each movement through a callback. This gives the algorithm an event-driven representation: every iteration reports the current slow node, fast node, and whether a meeting has occurred.

That design is useful for debugging because the algorithm's state can be observed without changing its core detection logic.

The JavaScript implementation also validates cycle creation. An invalid entry index is rejected instead of silently constructing a malformed demonstration structure.

The palindrome implementation uses JavaScript-specific object references while preserving the same linked-list invariant as the other implementations.

## C++ case study

The C++ program models an event-processing chain.

`EventNode` contains a sequence number, an event name, and a pointer to the next event. `EventChain` owns the allocated nodes through `std::unique_ptr`, while the links between nodes are raw non-owning pointers.

This separation is deliberate. Ownership determines which object is responsible for lifetime management, while the `next` pointer represents the logical graph relationship. A cycle in the logical links therefore does not cause ownership recursion.

The case study creates a corrupted processing chain where the final event points back to the third event. The resulting structure has a finite prefix followed by a cycle.

`floydMeetingPoint` detects the cycle, `findCycleEntry` locates its beginning, and `cycleLength` measures the repeating portion.

The program also implements a hash-set detector using `std::unordered_set<EventNode*>`. That alternative is useful for comparison because it is conceptually straightforward, but it requires O(n) additional memory. Floyd's method achieves the same asymptotic time bound with O(1) auxiliary pointer storage.

## Java enterprise model

The Java program represents a processing pipeline through `Stage` and `Pipeline` domain types.

`PipelineIntegrityService` isolates the algorithms from the data model. This is useful in larger systems because the linked structure can be owned by one component while integrity analysis is performed by another service.

`CycleReport` represents the result as a domain object rather than requiring callers to interpret a collection of unrelated return values. It distinguishes an empty chain, an acyclic chain, and a cyclic chain and records the meeting stage, entry stage, cycle length, and distance to the entry.

The `isMergeSafe` method demonstrates a domain-level consequence of the algorithm. A cyclic processing pipeline cannot be treated as a finite sequence because normal traversal never reaches a terminal node.

The implementation also validates stage names, sequence numbers, null targets, empty pipelines, invalid indexes, and self-cycles.

## SQL data model

The PostgreSQL script represents a linked structure relationally.

`pointer_chain` identifies independent chains.

`chain_node` stores the node payload, its sequence position, and the `next_node_id` representing the pointer.

The composite foreign key `(chain_id, next_node_id)` ensures that a node cannot point to a node belonging to a different chain. This is a database-level integrity rule rather than an assumption made by application code.

The `sequence_no` uniqueness constraint prevents duplicate positions inside one chain. The index on `(chain_id, sequence_no)` supports ordered chain inspection, while the index on `next_node_id` supports reverse-link investigations.

The examples include three different structures:

- `healthy_pipeline` terminates normally.
- `cyclic_pipeline` contains a prefix followed by a cycle beginning at `transform`.
- `self_cycle` points its only node back to itself.

The recursive SQL queries use path arrays to detect repeated node identifiers. This is deliberately different from Floyd's algorithm. A recursive SQL traversal can retain the visited path explicitly, whereas Floyd's algorithm detects repetition through two moving references and constant auxiliary memory.

The PostgreSQL function `floyd_has_cycle` models the fast/slow algorithm directly at the database layer. Its `slow_id` advances one link and its `fast_id` advances two links until either pointer reaches the end or the identifiers become equal.

## Middle-node behavior

The midpoint technique does not require a separate pass to count nodes.

For a list with an odd number of nodes, there is one unambiguous middle.

For a list with an even number of nodes, there are two mathematically central nodes. An implementation must therefore define which one it returns.

The second-middle implementation advances while `fast` and `fast.next` exist. The first-middle implementation stops earlier by requiring `fast.next.next` to exist before advancing.

This small change is important when midpoint detection is used as part of a larger linked-list algorithm.

## Cycle structure

A cyclic list can be viewed as two regions:

`head -> non-cyclic prefix -> cycle entry -> cycle -> back to cycle entry`

The prefix may have length zero. A self-cycle is the special case where the head itself is the cycle entry and the cycle length is one.

The examples therefore include:

`A -> A`

as well as structures such as:

`A -> B -> C -> D -> E -> C`

In the second structure, `C` is the cycle entry and the cycle contains `C`, `D`, and `E`.

The distinction between cycle entry and meeting point is important. Floyd's first phase only guarantees that the pointers meet somewhere inside the cycle. The second phase is required when the application needs the entry node.

## Complexity

Middle-node detection requires O(n) time and O(1) auxiliary space.

Floyd cycle detection requires O(n) time and O(1) auxiliary space.

Finding the cycle entry remains O(n) time and O(1) auxiliary space.

Computing the cycle length after locating the entry requires another traversal of the cycle and therefore remains O(n) in the worst case.

A visited-node set also provides O(n) time cycle detection, but its auxiliary memory grows with the number of distinct nodes traversed.

The main advantage of Floyd's technique is therefore not asymptotic time improvement. Its key advantage is constant auxiliary space.

## Edge cases

An empty list has no middle node and cannot contain a reachable cycle.

A single-node acyclic list has that node as its middle.

A single-node self-cycle is cyclic, with the same node serving as both the head and cycle entry and with cycle length one.

Even-sized lists require an explicit middle-node convention.

Repeated values must not be confused with repeated nodes.

A corrupted pointer may create a cycle far from the head, so testing only whether the final node points backward is insufficient.

For a cyclic structure, ordinary traversal code that stops only at `null` is unsafe because `null` may never be reached.

## Common implementation mistakes

A common error is advancing `fast` by two nodes without checking that both `fast` and `fast.next` exist. This can produce null-reference errors in languages with direct pointer or object traversal.

Another error is comparing node payloads instead of node identities. Equal values are allowed in different nodes.

Another error is assuming that Floyd's meeting point is the cycle entry. It is not necessarily the entry.

A further mistake is modifying the linked structure while searching for a middle or cycle without restoring it. Algorithms such as palindrome detection may temporarily reverse part of a list, so ownership and mutation expectations should be explicit.

For recursive or SQL implementations, an independent termination limit can be useful as a defensive measure when malformed data could otherwise produce an unbounded traversal.

## Practical interpretation

Fast and slow pointers are most valuable when the underlying structure supports sequential pointer traversal and the algorithm needs relative position rather than random access.

Middle detection exploits a speed ratio.

Cycle detection exploits the fact that two different speeds cannot remain separated forever once both pointers are constrained to a finite circular region.

Cycle-entry detection extends the same meeting information into a second constant-space traversal.

The Python, JavaScript, C++, Java, and PostgreSQL implementations intentionally present these mechanisms from different technical perspectives while preserving the same core invariants.
