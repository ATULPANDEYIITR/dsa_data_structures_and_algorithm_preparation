# Singly Linked Lists

## Scope

This project provides three independent implementations of a singly linked list in Python, JavaScript, and C++.

The implementations focus on the fundamental linked-list mechanisms rather than relying on a library linked-list type:

- `Node`
- `head`
- traversal
- insertion
- deletion
- searching
- reversal
- structural validation
- cycle detection
- edge-case handling
- complexity and implementation trade-offs

The three programs use the same underlying data-structure model but deliberately approach it from different language-specific perspectives.

## Core Data Structure

A singly linked list is a sequence of nodes in which each node contains two pieces of information:

- a data value
- a reference or pointer to the next node

The first node is referenced by `head`.

The final node has no successor, represented by `None` in Python, `null` in JavaScript, and `nullptr` in C++.

A typical structure therefore has the form:

`HEAD -> Node A -> Node B -> Node C -> NULL`

Unlike an array, the nodes do not have to occupy adjacent memory locations. The relationship between nodes is established through the `next` reference.

The singly linked design permits movement in only one direction. To reach a later node, traversal starts at `head` and repeatedly follows `next`.

## Node

The `Node` is the fundamental building block.

The Python implementation uses a `dataclass` with `data` and `next`. The `next` attribute contains either another `Node` or `None`.

The JavaScript implementation uses a `Node` class. JavaScript object references allow one node object to hold a reference to another node object.

The C++ implementation defines `Node` internally within `SinglyLinkedList`. Each node stores its value and a raw pointer to the next node. The list owns those dynamically allocated nodes and releases them in `clear()` and the destructor.

The important structural invariant is that changing a link changes the topology of the list. Insertion and deletion are therefore pointer-manipulation operations, not merely changes to a sequence of values.

## Head Management

`head` identifies the first node.

An empty list has a null head:

`HEAD -> NULL`

When the first node is inserted, `head` points to that node.

Head insertion is particularly efficient because no traversal is required. The new node first points to the current head, and then the head is replaced by the new node:

`new_node.next = head`

`head = new_node`

This takes constant time, O(1).

Head deletion is similarly efficient. The current head is saved, `head` is moved to the successor, and the removed node is disconnected.

The implementations explicitly handle the empty-list condition because attempting to remove a nonexistent head is an invalid operation.

## Traversal

Traversal begins at `head`.

The general mechanism is:

`current = head`

followed by repeated evaluation of:

`current = current.next`

until the current node becomes null.

Traversal is O(n), where n is the number of nodes.

The singly linked structure does not provide constant-time random access. Finding the node at index 50 requires following up to 50 links from the head.

This distinction is fundamental when choosing between a linked structure and an indexed sequence.

## Insertion

### Insertion at the head

Head insertion is O(1).

The new node is placed before the existing head, so only two references need to be updated.

This is demonstrated directly in all three implementations.

### Insertion at the end

The Python and JavaScript lists intentionally do not maintain a tail pointer. Consequently, finding the final node requires traversal from the head.

Tail insertion therefore takes O(n).

The C++ implementation makes the same design choice so that the pointer mechanics remain explicit and consistent.

A production implementation that performs frequent tail insertion can maintain both `head` and `tail`. That changes tail insertion to O(1), but it introduces another structural invariant: whenever the list is non-empty, `tail` must refer to the final node.

### Insertion at an index

Indexed insertion requires reaching the node immediately before the insertion position.

For example:

`A -> B -> C`

Inserting `X` between `B` and `C` changes the links to:

`A -> B -> X -> C`

The implementation must preserve the original successor before overwriting the predecessor's `next` reference.

The operation is O(n) because reaching the insertion position may require traversal.

### Insertion after a value

The examples also support insertion after the first matching value.

The implementation traverses until it finds the target node, then performs the same local link transformation used for indexed insertion.

This demonstrates an important linked-list property: once the correct predecessor or target node is already known, changing the chain around that location requires only constant-time pointer updates.

## Deletion

### Deleting the head

Head deletion is O(1).

The current head becomes detached and the next node becomes the new head.

This operation is especially suitable for queue-like processing where elements are consumed from the front.

### Deleting at an index

For an internal node, deletion requires the predecessor.

For:

`A -> B -> C -> D`

deleting `C` changes the predecessor's link from:

`B -> C`

to:

`B -> D`

The removed node is then disconnected or released, depending on the language.

The traversal needed to find the predecessor makes arbitrary indexed deletion O(n).

### Deleting the first matching value

The implementation maintains both `previous` and `current` references.

`current` identifies the candidate node, while `previous` identifies the node whose `next` pointer must be changed if deletion occurs.

This distinction is central to singly linked-list deletion because a node does not contain a reference to its predecessor.

### Deleting all matching values

The Python and JavaScript implementations also handle repeated values.

The head is processed separately because removing the head changes the starting point. Internal matches can then be removed while maintaining a valid predecessor reference.

This avoids the common bug where consecutive matching nodes cause one occurrence to be skipped.

## Reversal

The implementations reverse the list in place rather than creating another list.

The algorithm maintains three references:

- `previous`
- `current`
- `next`

For each node, the original successor is saved before the current node's `next` link is reversed.

The transformation changes:

`A -> B -> C -> NULL`

into:

`A <- B <- C`

and finally makes `C` the new head:

`C -> B -> A -> NULL`

The operation takes O(n) time and O(1) auxiliary space.

The temporary `next` reference is essential. If the original successor is not saved before changing `current.next`, the remainder of the chain can become unreachable.

## Searching

Searching is sequential because a singly linked list does not provide direct addressing by index.

The implementations begin at `head` and compare each node's stored value with the requested value.

Worst-case search complexity is O(n).

The Python version returns the matching `Node` object, while the JavaScript and C++ implementations expose value-oriented search operations suitable for their respective examples.

## Cycle Detection

A valid ordinary singly linked list eventually reaches a null successor.

A corrupted structure can instead contain a cycle:

`A -> B -> C -> B`

Traversal without cycle protection would never terminate.

All three implementations demonstrate Floyd's tortoise-and-hare algorithm.

The algorithm uses:

- a slow reference moving one node at a time
- a fast reference moving two nodes at a time

If a cycle exists, the two references eventually meet.

Cycle detection requires O(n) time and O(1) additional space.

The demonstrations deliberately create a cycle and then repair it so that the detection mechanism can be observed without leaving the final data structure corrupted.

## Structural Integrity

The implementations maintain a node count in addition to the head pointer.

An integrity check independently traverses the structure and verifies that:

- no cycle exists
- the number of reachable nodes matches the maintained size

This is useful during development because pointer errors can produce structures that appear partially correct while internally losing nodes or creating loops.

The C++ implementation performs explicit ownership cleanup. The destructor calls `clear()`, ensuring dynamically allocated nodes are released when the list object is destroyed.

Copy construction and copy assignment are disabled in the C++ implementation because a shallow copy of raw node pointers would cause multiple list objects to believe they own the same nodes. Move construction and move assignment transfer ownership instead.

## Python Implementation

The Python program uses a `Node` dataclass and a `SinglyLinkedList` class.

Its implementation covers:

- explicit node creation
- head manipulation
- traversal through `next`
- searching
- indexed access
- insertion at the head
- insertion at the end
- indexed insertion
- insertion after a matching value
- head deletion
- indexed deletion
- first-match deletion
- deletion of all matching values
- in-place reversal
- Floyd cycle detection
- integrity validation
- in-place value transformation
- realistic ordered processing
- failure handling
- edge-case verification

The Python program deliberately does not replace the structure with a built-in collection. Lists are used only for convenient output and test data; the linked structure itself is represented by explicit `Node` objects.

The `validate_integrity()` method is especially useful for educational debugging because it checks the relationship between the maintained size and the actual reachable nodes.

## JavaScript Implementation

The JavaScript implementation uses a `Node` class and a `SinglyLinkedList` class.

It emphasizes JavaScript object references and adds an event-driven extension through `ObservableLinkedList`.

The event-driven class demonstrates a useful JavaScript-specific design: mutation operations can emit structured events to registered callbacks.

For example, after insertion, a listener can receive:

`operation`

`details`

`size`

`snapshot`

This does not change the underlying linked-list algorithm. It demonstrates how a manually implemented data structure can participate in event-driven application code without mixing event behavior into the basic node representation.

The JavaScript implementation also uses `Set` for listener registration and unsubscribe functions for managing event subscriptions.

## C++ Case Study

The C++ program models an ordered repository validation pipeline.

The stages are represented as a singly linked chain:

`validate-change -> run-status-checks -> collect-review -> verify-merge-policy -> merge-change`

The pipeline is intentionally modeled as a singly linked list because each stage has a natural successor and processing proceeds from the front toward the end.

When a stage is completed, `deleteHead()` removes it and the next stage becomes the head.

This provides a concrete example of why O(1) head deletion can be useful.

The C++ implementation uses manual dynamic allocation to expose ownership and pointer behavior directly. The destructor invokes `clear()`, which deletes every node.

The class also demonstrates move semantics. Copy operations are disabled to avoid accidental shallow ownership of the node chain, while move operations transfer the head pointer and size to the destination and reset the source.

The case study includes explicit exception handling for invalid indexes, missing values, and operations on empty lists.

## Complexity

| Operation | Time | Additional Space |
|---|---:|---:|
| Access head | O(1) | O(1) |
| Insert at head | O(1) | O(1) |
| Delete head | O(1) | O(1) |
| Traverse | O(n) | O(1) excluding output |
| Search | O(n) | O(1) |
| Access by index | O(n) | O(1) |
| Insert at index | O(n) | O(1) |
| Delete at index | O(n) | O(1) |
| Insert at end without tail | O(n) | O(1) |
| Delete first matching value | O(n) | O(1) |
| Reverse | O(n) | O(1) |
| Floyd cycle detection | O(n) | O(1) |

The O(n) bounds arise primarily from the need to traverse from the head.

A singly linked list becomes more attractive when sequential traversal and local link modification matter more than random indexed access.

## Edge Cases

The implementations explicitly exercise:

- an empty list
- a single-node list
- repeated values
- deletion of the first node
- deletion of the last node
- insertion into an empty list
- insertion at the beginning
- insertion at the end
- invalid indexes
- missing search targets
- deletion of all repeated occurrences
- reversal of a list
- deliberate cycle creation
- cycle detection and repair

Empty-list operations require special handling because there is no node from which a link can be read.

Single-node operations are also important because deleting that node must restore the empty state by setting `head` to null.

Repeated values expose a common deletion bug: advancing both predecessor and current after a deletion can skip adjacent matches. The implementations update the current reference carefully after removing a node.

## Common Pointer Errors

A linked-list implementation can fail even when the values printed during simple tests appear correct.

One common insertion error is overwriting the predecessor's `next` pointer before saving the original successor. The remainder of the chain can then become inaccessible.

One common deletion error is failing to update `head` when the first node is removed.

Another error is advancing the traversal pointer after deleting a node and thereby skipping the node that moved into the deleted position.

A reversal implementation can lose the remaining suffix if it changes `current.next` before preserving the original successor.

A cycle can be accidentally introduced when a link is assigned to an earlier node rather than to the intended successor.

The integrity checks and cycle detection code are designed to expose these structural failures.

## Memory and Ownership

Python and JavaScript use managed memory. Once removed nodes are no longer reachable, their storage can eventually be reclaimed by the runtime.

The C++ implementation requires explicit ownership management because nodes are created with `new`.

Each removed C++ node is released with `delete`, and `clear()` releases the entire chain.

The C++ class disables copying because copying only the `head_` pointer would create two objects referring to the same ownership graph. The destructor of both objects could then attempt to delete the same nodes.

Move semantics provide a safe alternative when ownership needs to be transferred.

## When a Singly Linked List Is Appropriate

A singly linked list is useful when operations naturally proceed from one element to its successor and frequent head insertion or deletion is important.

It is less suitable when applications require frequent indexed access because reaching an arbitrary position requires sequential traversal.

A maintained tail pointer can improve append performance, but it increases the number of structural invariants that must remain correct.

The data structure is also less cache-friendly than a contiguous array in many practical workloads because nodes may be distributed across memory rather than stored consecutively.

## Practical Design Decisions

The implementations intentionally expose the node links instead of hiding the structure behind a library collection.

This makes the cost of traversal and the mechanics of insertion and deletion visible.

The examples also separate observation from mutation. Traversal and searching inspect the chain, while insertion, deletion, reversal, and clearing change its structure.

Integrity validation is treated as a development and debugging mechanism rather than as a requirement for every production operation. Running a full validation after every mutation would introduce unnecessary traversal overhead.

The C++ case study adds explicit ownership rules because manual memory management makes those concerns materially different from Python and JavaScript.

## Running the Implementations

The Python implementation requires Python 3 and uses only the standard library.

Run it with:

`python singly_linked_list.py`

The JavaScript implementation is designed for Node.js and has no npm dependencies.

Run it with:

`node singly_linked_list.js`

The C++ implementation requires a compiler supporting C++17 or later.

Compile it with:

`g++ -std=c++17 -Wall -Wextra -pedantic singly_linked_list.cpp -o linked_list`

Then run the executable with:

`./linked_list`

On Windows with a MinGW-based compiler, the executable can be started as:

`linked_list.exe`

The programs print their traversal, mutation, validation, failure-handling, cycle-detection, and complexity demonstrations directly to standard output.
