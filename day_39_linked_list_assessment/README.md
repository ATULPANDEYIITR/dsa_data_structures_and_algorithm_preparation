# Linked-List Assessment: Eight Problems

## Assessment scope

This assessment contains eight linked-list problems organized by algorithmic difficulty. It covers pointer manipulation, cycle detection, sorted merging, two-pointer techniques, node identity, in-place rearrangement, and heap-based multiway merging.

The problems are designed for singly linked lists, where each node stores a value and a reference to the next node. Unlike an array, a linked list does not provide constant-time indexed access. Operations often require traversal, but inserting, removing, or repositioning a node can be inexpensive when the relevant references are available.

| Difficulty | Problem | Main technique |
|---|---|---|
| Easy | Reverse a Linked List | Iterative pointer reversal |
| Easy | Detect a Cycle | Floyd's tortoise-and-hare algorithm |
| Easy | Merge Two Sorted Lists | Two-pointer merge |
| Medium | Remove Nth Node From End | Fixed-gap pointers |
| Medium | Intersection of Two Linked Lists | Pointer switching and identity comparison |
| Medium | Palindrome Linked List | Reverse and compare halves |
| Medium | Reorder List | Split, reverse, and interleave |
| Difficult | Merge K Sorted Lists | Min-heap |

The Python, JavaScript, C++, Java, and PostgreSQL implementations provide complementary treatments of these problems. The implementations focus on executable algorithms, validation, edge cases, and the practical consequences of modifying linked structures.

## Node representation and pointer invariants

A singly linked node has a value and a reference to its successor. A null successor marks the end of an ordinary list.

The fundamental structural invariant is that following `next` references from the head must eventually reach null. A cyclic list violates this condition because traversal eventually revisits a node.

Several algorithms modify existing links instead of allocating replacement nodes. This reduces auxiliary memory usage but requires careful handling of references. Before overwriting a link, the implementation must preserve any successor that would otherwise become unreachable.

Node identity and node value are distinct concepts. Two nodes can both store `8` without being the same node. This distinction is essential for intersection detection and for preventing ambiguous merges of lists that share a tail.

## Easy problems

### Reverse a Linked List

The objective is to reverse the direction of every link while preserving all node values.

The iterative algorithm maintains three references:

- `previous` identifies the already reversed prefix.
- `current` identifies the node being processed.
- `following` saves the successor before the current link is overwritten.

At each iteration, `current.next` is redirected to `previous`. The references then advance until the original list has been reversed. The final value of `previous` becomes the new head.

The operation takes O(n) time and O(1) auxiliary space. An empty list remains empty, and a single-node list is unchanged.

A common implementation error is overwriting `current.next` before saving the original successor. Doing so disconnects the unprocessed remainder of the list.

### Detect a Cycle

Floyd's algorithm uses a slow pointer that advances one node per iteration and a fast pointer that advances two nodes.

If the list is acyclic, the fast pointer eventually reaches null. If a cycle exists, the pointers eventually meet inside the cycle.

The algorithm takes O(n) time and O(1) auxiliary space. It does not require a set of previously visited nodes.

Cycle detection is also an important defensive check for other algorithms. A reversal or traversal routine that assumes an acyclic list can otherwise run indefinitely or corrupt the structure.

### Merge Two Sorted Lists

The two-pointer merge combines two sorted, disjoint lists into one sorted list.

A dummy node simplifies initialization because the first selected node can be attached using the same logic as every subsequent node. The algorithm compares the current values of both inputs, attaches the smaller node, and advances the corresponding pointer.

When one input is exhausted, the remaining suffix of the other input is attached directly.

For input lengths n and m, the algorithm takes O(n + m) time and O(1) auxiliary space, excluding the returned structure.

The implementation reuses nodes rather than copying their values into new nodes. It therefore requires disjoint inputs. Shared nodes can cause duplicated references or cycles if both input chains are independently consumed.

## Medium problems

### Remove Nth Node From End

The objective is to remove the Nth node counted backward from the tail.

A dummy node is placed before the head so that removing the first real node uses the same pointer-update logic as removing an interior node.

The fast pointer advances n positions ahead of the slow pointer. Both then move together until the fast pointer reaches the last node. At that point, the slow pointer identifies the predecessor of the node to remove.

The algorithm takes O(n) time and O(1) auxiliary space.

The value of n must be positive and must not exceed the list length. Implementations explicitly reject invalid requests rather than silently returning an incorrect result.

The removed node is detached by setting its `next` reference to null. In languages with manual memory management, such as C++, the caller or algorithm must also establish clear ownership and release the removed node when appropriate.

### Intersection of Two Linked Lists

Two lists intersect when their chains converge on the same physical node. Matching values alone do not establish an intersection.

The pointer-switching algorithm starts one pointer at each head. When a pointer reaches null, it restarts at the other list's head. Each pointer therefore traverses the combined lengths in opposite orders.

If the lists intersect, the pointers meet at the first shared node. If they do not intersect, both eventually reach null together.

The time complexity is O(n + m), with O(1) auxiliary space.

This technique avoids computing list lengths explicitly. It relies on both lists being acyclic and on comparing node references rather than stored values.

### Palindrome Linked List

A linked list is a palindrome when its sequence of values reads identically from either direction.

The algorithm finds the midpoint using slow and fast pointers. It reverses the second half and compares corresponding values from the head and the reversed half.

For odd-length lists, the middle node does not need to be compared against itself. The comparison therefore proceeds only while the second-half pointer remains non-null.

The algorithm takes O(n) time and O(1) auxiliary space. Reversing the second half changes the input structure temporarily, so the implementation restores the links before returning. Failing to restore them can surprise callers that retain the original head.

An alternative is to copy values into an array and compare symmetric positions. That approach is simpler but uses O(n) additional space.

### Reorder List

The objective is to transform a list ordered as `L0 → L1 → ... → Ln` into `L0 → Ln → L1 → Ln-1 → ...`.

The algorithm first locates the midpoint. It then disconnects the second half, reverses it, and alternately attaches nodes from the two halves.

No replacement nodes are needed, so the operation takes O(n) time and O(1) auxiliary space.

The critical implementation detail is preserving the next reference from each half before changing its links. Without this precaution, nodes can become unreachable or the resulting list can contain an unintended cycle.

## Difficult problem

### Merge K Sorted Lists

The multiway merge combines K individually sorted lists into one sorted output.

Repeatedly scanning every list for the smallest head can take O(NK) time, where N is the total number of nodes. A min-heap avoids that repeated full scan.

The heap stores at most one candidate node from each non-empty input list. Each iteration removes the smallest candidate, appends that node to the result, and inserts its successor when one exists.

The resulting complexity is O(N log K) time and O(K) auxiliary heap space, excluding validation structures and the reused nodes.

The Python implementation uses `heapq` and a sequence number to avoid comparing node objects when values tie. The JavaScript implementation supplies a binary min-heap. The C++ implementation uses `std::priority_queue` with a comparator, while the Java implementation uses `PriorityQueue` with a comparator that breaks ties deterministically.

The implementations validate that input lists are acyclic and disjoint. These checks cost O(N) time and can use O(N) auxiliary memory. In production systems with trusted, validated inputs, the validation strategy may be adjusted to avoid that extra cost, provided the preconditions remain enforced elsewhere.

## Python implementation

The Python file defines a `ListNode` data class and helper functions for constructing and inspecting lists. Its assessment methods implement all eight problems.

The `unittest` suite checks ordinary results, empty inputs, invalid removal positions, cycles, shared-tail intersection, and restoration of the original palindrome list. Tests compare node identity where structural identity matters and compare values where sequence equality is the intended behavior.

The merge-K implementation uses a monotonically increasing sequence number as the second heap key. This prevents Python from attempting to order `ListNode` instances when values are equal.

Run the file with Python 3.10 or later. The demonstration prints representative results before executing the test suite.

## JavaScript implementation

The JavaScript file uses ordinary objects to represent nodes and `Set` collections to track node identity. Its functions are usable in a Node.js environment and export the algorithm implementations for reuse.

The custom `MinHeap` demonstrates the mechanics of binary-heap insertion and removal. Insertion moves an item upward while its parent has a larger value. Removal replaces the root with the last element and restores the heap by moving the replacement downward.

The test harness uses Node.js's built-in `node:assert/strict` module. No third-party package is required.

JavaScript references behave differently from manually managed C++ pointers: the runtime manages memory, but incorrect reference updates can still lose nodes, create cycles, or change a structure unexpectedly.

## C++ case study

The C++ program models ordered telemetry records flowing through linked queues. Each node stores a timestamp, an event label, and a raw pointer to the next node.

The case study demonstrates reversal, two-list merging, removal, palindrome checking, reordering, and multiway merging in a coherent event-processing context. Floyd's algorithm detects cycles, and an identity-based set rejects overlapping input chains before destructive merging.

The K-way merge uses `std::priority_queue` with a comparator that makes the earliest timestamp the highest-priority entry. A sequence field provides deterministic ordering for equal timestamps.

Manual memory management is a key distinction. Nodes created by `buildList` must eventually be released by `destroyList`. The deliberately cyclic example is disconnected before destruction because a conventional linear deletion loop cannot safely traverse a cycle. The removed node is explicitly deleted by the removal operation.

In larger systems, ownership could be represented through smart pointers or an owning container. The raw-pointer implementation keeps the link-manipulation mechanics visible, but it requires careful rules about who owns nodes and when they may be released.

Compile with a C++17-compatible compiler. The program reports processing failures through exceptions and returns a nonzero status if an exception escapes the main workflow.

## Java implementation

The Java implementation models nodes as objects with immutable integer values and mutable successor references. Helper methods separate structural validation from the individual algorithms.

`PriorityQueue` implements the multiway merge frontier. A local `Entry` class pairs a candidate node with a sequence number, and a comparator orders entries by value and then by sequence. Identity-based sets prevent shared nodes from being accepted as independent merge inputs.

Java's garbage collector removes the need for explicit deallocation, but it does not guarantee structural correctness. A cycle can still cause infinite traversal, and overwriting a successor can make part of a list unreachable.

The `finally` block in the palindrome algorithm restores the reversed half even if the comparison logic changes to throw an exception. This is an example of preserving a data-structure invariant across a temporary mutation.

The program uses standard Java 17 APIs and includes executable assertions implemented through explicit checks.

## PostgreSQL assessment model

The SQL script stores assessment definitions, sample node layouts, and recorded execution outcomes. It does not attempt to implement mutable pointer algorithms as ordinary relational operations. Instead, it records the problem metadata and supports assessment reporting and structural inspection.

The `assessment_case` table stores each problem's difficulty, technique, expected complexity, and description. The `list_node` table represents node positions and their next positions within a named list. Its unique constraint prevents duplicate positions within the same list, while check constraints reject negative positions and direct self-links.

The `assessment_result` table records successful and failed runs, elapsed time, JSONB observations, and failure explanations. A consistency constraint requires successful runs to have no failure reason and failed runs to provide one.

Indexes support list traversal and recent-result queries. The summary view aggregates run counts and pass percentages by assessment case. A recursive common table expression follows recorded links while tracking visited positions, exposing cycles without continuing indefinitely.

Relational constraints cannot guarantee every property of a linked structure. In particular, the schema does not prevent every possible multi-node cycle. The integrity query identifies links that point to missing positions, while recursive traversal helps detect cycles. An application or database trigger could enforce additional invariants if linked-list structures were persisted as operational data rather than as assessment records.

Execute the SQL script in PostgreSQL. It creates its own tables, inserts sample data, queries the assessment results, and commits the transaction.

## Complexity comparison

| Problem | Time complexity | Auxiliary space |
|---|---|---|
| Reverse a list | O(n) | O(1) |
| Detect a cycle | O(n) | O(1) |
| Merge two sorted lists | O(n + m) | O(1) |
| Remove Nth from end | O(n) | O(1) |
| Find intersection | O(n + m) | O(1) |
| Check palindrome | O(n) | O(1) |
| Reorder a list | O(n) | O(1) |
| Merge K sorted lists | O(N log K) | O(K) heap space |

These complexities describe the core algorithms. Additional cycle and shared-node validation may require extra traversal time and memory. For example, a defensive merge-K implementation can use O(N) space to validate that all input nodes are distinct before modifying their links.

## Edge cases and implementation correctness

Empty lists and single-node lists should be tested explicitly because they frequently expose incorrect assumptions about `head`, `next`, and midpoint calculations.

Invalid removal positions must be rejected before attempting to unlink a node. Cycle detection must precede algorithms whose termination depends on reaching null. Intersections must be determined by reference identity rather than by value equality.

For destructive merge operations, the input lists should be sorted, acyclic, and disjoint. If these preconditions are not guaranteed, the implementation should validate them or clearly define the consequences of violating them.

Palindrome checking and reordering illustrate another important concern: a correct output sequence is not always sufficient evidence of a correct implementation. Tests should also verify that nodes remain reachable exactly as intended and that temporary changes are restored whenever the operation promises not to mutate its input.

For assessment environments, each problem should be evaluated against ordinary inputs, boundary cases, invalid requests, and structural invariants. This distinguishes algorithms that produce expected output on simple examples from implementations that behave reliably across the full range of supported inputs.
