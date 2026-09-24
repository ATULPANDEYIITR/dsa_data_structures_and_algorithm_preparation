# Day 13 — Array insertion and deletion

## Topic

Array insertion and deletion are fundamental operations in data structures. An array provides fast indexed access because elements are stored in an ordered sequence of positions. The same layout creates an important cost: when an element is inserted or deleted while preserving order, other elements may have to move.

This implementation set studies the relationship between array position, element shifting, logical size, physical capacity, and algorithmic complexity.

The three implementations approach the topic from different perspectives:

- Python demonstrates the operations directly with lists and a manually implemented dynamic array.
- JavaScript demonstrates array manipulation, validation, dynamic-array behavior, and an application-oriented task list.
- C++ develops an industry-style inventory reservation system using a custom generic dynamic array, explicit memory management, stable and unordered deletion, and queue designs.

## Fundamental array model

An array can be viewed as a sequence of indexed storage positions:

`A[0], A[1], A[2], ..., A[n - 1]`

For an array containing `n` elements:

- The first element is at index `0`.
- The final element is at index `n - 1`.
- The number of elements is `n`.
- Accessing an element by a valid index is normally `O(1)`.
- Inserting or deleting near the beginning can require many elements to move.
- Inserting at the end can be efficient when the array has unused capacity.
- Deleting the final element does not require shifting other elements.

The central question for this topic is not simply whether an operation is insertion or deletion. The important question is:

> How many existing elements must move to preserve the required order?

## Terminology

### Array

An array is an indexed collection of elements arranged in a defined order.

### Index

An index identifies the position of an element. In zero-based arrays, the first element has index `0`.

### Element

An element is one stored value or object in the array.

### Logical size

Logical size is the number of elements currently stored.

For `[10, 20, 30]`, the logical size is `3`.

### Capacity

Capacity is the amount of storage currently available before the underlying storage must be expanded.

A dynamic array can have a size of `3` and a capacity of `8`.

### Shifting

Shifting means moving elements to different indices to create or fill a position.

For insertion, elements usually shift right.

For deletion, elements usually shift left.

### Stable deletion

Stable deletion preserves the relative order of the remaining elements.

For example:

`[10, 20, 30, 40]`

Deleting `20` stably produces:

`[10, 30, 40]`

### Unordered deletion

Unordered deletion does not preserve the order of remaining elements.

For example:

`[10, 20, 30, 40]`

Deleting index `1` can replace `20` with `40`:

`[10, 40, 30]`

This can reduce deletion from `O(n)` to `O(1)` when the index is already known and ordering is irrelevant.

## Insertion at the beginning

Consider:

`[20, 30, 40]`

To insert `10` at index `0`, the existing values must move:

`[20, 30, 40]`

becomes conceptually:

`[20, 20, 30, 40]`

and then:

`[10, 20, 30, 40]`

Three existing elements were shifted.

For an array of size `n`, insertion at index `0` requires `n` element movements.

Therefore:

`Time = O(n)`

The Python implementation uses a loop that starts at the final position and moves toward the insertion position. The reverse direction is essential because moving from left to right would overwrite values that have not yet been copied.

The JavaScript implementation uses the same conceptual mechanism.

The C++ dynamic array implements the same operation with explicit storage and element movement.

## Insertion at the end

For:

`[10, 20, 30]`

inserting `40` at the end produces:

`[10, 20, 30, 40]`

No existing element has to move.

A dynamic array may therefore provide amortized `O(1)` insertion at the end.

The word "amortized" matters because a dynamic array occasionally has to allocate a larger storage region and copy its elements.

Most appends are inexpensive, but an occasional resize can cost `O(n)`.

Across a long sequence of append operations, geometric capacity growth makes the average cost per append approximately constant.

## Insertion at a position

Suppose the array is:

`[10, 20, 30, 40, 50]`

and `99` must be inserted at index `2`.

The result must be:

`[10, 20, 99, 30, 40, 50]`

The values `30`, `40`, and `50` must move one position right.

For an array of size `n` and insertion index `i`:

`shift count = n - i`

Examples:

| Array size | Insertion index | Elements shifted |
|---:|---:|---:|
| 5 | 0 | 5 |
| 5 | 1 | 4 |
| 5 | 2 | 3 |
| 5 | 3 | 2 |
| 5 | 4 | 1 |
| 5 | 5 | 0 |

Insertion at index `n` is insertion at the end and requires no shifting.

## Why insertion shifts from right to left

Suppose:

`[10, 20, 30, 40]`

must receive `99` at index `1`.

The correct sequence is:

1. Move `40` to the new final position.
2. Move `30` one position right.
3. Move `20` one position right.
4. Place `99` at index `1`.

If the operation moved left to right, `20` could overwrite data before that data had been moved.

This principle is important in low-level array manipulation.

## Deletion from the beginning

Consider:

`[10, 20, 30, 40]`

Deleting the first element produces:

`[20, 30, 40]`

To preserve order:

- `20` moves to index `0`.
- `30` moves to index `1`.
- `40` moves to index `2`.

Three elements move.

Therefore deletion from the beginning is `O(n)` for a normal order-preserving array.

This explains why an array is not automatically the best implementation for a queue that repeatedly removes the first element.

## Deletion from the end

For:

`[10, 20, 30, 40]`

deleting the final element produces:

`[10, 20, 30]`

No remaining element moves.

The operation is normally `O(1)`.

Python uses `list.pop()` for this case, JavaScript uses `Array.pop()`, and the C++ dynamic array implements `popBack()`.

## Deletion by index

For:

`[10, 20, 30, 40, 50]`

deleting index `2` removes `30`.

The remaining values after the deleted position must shift left:

`40` moves to index `2`.

`50` moves to index `3`.

The resulting array is:

`[10, 20, 40, 50]`

For an array of size `n` and deletion index `i`:

`shift count = n - i - 1`

The worst case occurs at the beginning:

`n - 1`

The best case occurs at the end:

`0`

## Deletion by value

Deletion by value usually consists of two conceptual operations:

1. Find the value.
2. Remove it from the discovered position.

Finding an arbitrary value in an unsorted array requires linear search:

`O(n)`

If the value is found near the beginning, deletion can then require additional shifting.

The complete worst-case operation remains:

`O(n)`

The Python implementation uses a loop to locate the first matching value.

The JavaScript implementation uses `indexOf()` before performing the deletion.

The C++ implementation searches through the custom array by product ID.

## Deleting duplicates

Consider:

`[5, 2, 5, 3, 5]`

Deleting only the first `5` produces:

`[2, 5, 3, 5]`

Deleting every `5` produces:

`[2, 3]`

The implementations include a write-pointer technique for deleting all matching values.

The read pointer scans the original sequence.

The write pointer records where the next retained value should be placed.

This allows all matching elements to be removed in `O(n)` time without creating a second array.

## The write-pointer technique

For:

`[1, 2, 1, 3, 1]`

with `1` selected for deletion:

- Read `1`: discard it.
- Read `2`: write it to the next retained position.
- Read `1`: discard it.
- Read `3`: write it after `2`.
- Read `1`: discard it.

The resulting sequence is:

`[2, 3]`

The technique is useful beyond deletion. It is a general pattern for filtering an array in place.

## Shift cost

For insertion at index `i`:

`shifted = n - i`

For deletion at index `i`:

`shifted = n - i - 1`

The number of shifted elements directly explains the performance.

For example, with `n = 1,000,000`:

- Inserting at index `0` can move `1,000,000` elements.
- Inserting near the middle can move roughly `500,000` elements.
- Inserting at index `1,000,000` moves zero existing elements.
- Deleting index `0` can move `999,999` elements.
- Deleting the last element moves zero elements.

This is why the physical position of an operation matters.

## Complexity table

| Operation | Typical complexity |
|---|---:|
| Access by index | `O(1)` |
| Search by value | `O(n)` |
| Insert at beginning | `O(n)` |
| Insert in middle | `O(n)` |
| Insert at end | `O(1)` amortized |
| Delete from beginning | `O(n)` |
| Delete from middle | `O(n)` |
| Delete from end | `O(1)` |
| Delete by index | `O(n)` worst case |
| Delete by value | `O(n)` |
| Delete all matching values | `O(n)` |
| Unordered deletion by known index | `O(1)` |
| Dynamic-array resize | `O(n)` |

The complexity describes growth as the number of elements increases. Actual execution time also depends on hardware, implementation, compiler, runtime, memory allocation, and object size.

## Python implementation

The Python script begins with direct list operations and then implements the underlying shifting behavior manually.

### Beginning insertion

`insert_at_beginning()` expands the list and shifts values from right to left.

This demonstrates why the operation is `O(n)`.

### End insertion

`insert_at_end()` calls `append()`.

Python lists are dynamic arrays, so appending is normally amortized `O(1)`.

### Position insertion

`insert_at_position()` validates that the index lies between `0` and the current size.

The index equal to the current size represents insertion at the end.

### Deletion

The Python implementation contains separate functions for:

- `delete_from_beginning()`
- `delete_from_end()`
- `delete_by_index()`
- `delete_by_value()`
- `delete_all_by_value()`

This separation makes the different costs explicit.

### Dynamic array

The `DynamicArray` class models logical size and physical capacity separately.

It expands its storage when the logical size reaches capacity.

The implementation doubles capacity during expansion.

This means a sequence of append operations has amortized `O(1)` insertion cost.

It also demonstrates controlled shrinking when the array becomes substantially under-utilized.

### Queue comparison

The Python implementation contains both `ArrayQueue` and `CircularQueue`.

The naive queue deletes index `0`, causing shifting.

The circular queue uses modular indexing so that the logical front can move without shifting every element.

This illustrates an important design principle:

A slow operation can sometimes be avoided by changing the representation rather than optimizing the same operation.

## JavaScript implementation

JavaScript's built-in `Array` is dynamic and supports convenient methods such as:

- `push()`
- `pop()`
- `shift()`
- `unshift()`
- `splice()`

The educational implementation does not rely exclusively on these methods. Manual versions demonstrate the movement of elements.

### `push()`

`push()` adds to the end.

It is generally amortized `O(1)`.

### `pop()`

`pop()` removes the final element.

It is generally `O(1)`.

### `shift()`

Removing the first element from a conventional JavaScript array can require rearranging later elements.

Therefore it should not be treated as equivalent to `pop()` in terms of cost.

### `splice()`

`splice()` can insert or remove elements at arbitrary positions.

The cost depends on how many elements need to move and how many elements are inserted or removed.

### Task list application

The `TaskList` class demonstrates a practical use of array insertion and deletion.

A priority task can be inserted near the beginning, which means existing tasks must move.

Removing a task by name requires searching before deletion.

The example demonstrates why an application developer must understand the underlying cost of convenient array methods.

## C++ case study

The C++ implementation models an inventory reservation system.

Products contain:

- product ID
- name
- quantity
- price

The system supports adding products, inserting priority products, deleting by index, deleting by ID, deleting all matching IDs, and removing products without preserving order.

### Custom dynamic array

The `DynamicArray<T>` template explicitly manages:

- pointer-based storage
- logical size
- capacity
- resizing
- copying
- moving
- insertion
- stable deletion
- unordered deletion

The template allows the same data structure to store integers, products, or other assignable types.

### Memory management

The custom implementation uses dynamically allocated storage.

The destructor releases memory with `delete[]`.

Copy construction creates independent storage.

Copy assignment uses a temporary object and `swap()` to provide a clear ownership model.

Move construction and move assignment transfer ownership rather than copying every element.

These concerns are particularly important in C++ because memory ownership is explicit.

### Capacity growth

The array doubles its capacity when it becomes full.

For example, capacities can progress approximately as:

`2 → 4 → 8 → 16 → 32`

A resize requires copying or moving the existing elements.

A single resize is `O(n)`, but geometric growth provides amortized `O(1)` append performance.

## Stable deletion in the C++ case study

The `erase()` method preserves ordering.

For example:

`Keyboard, Mouse, Monitor`

deleting `Mouse` produces:

`Keyboard, Monitor`

The relative order of the remaining products does not change.

This is useful when array position has meaning.

Examples include:

- ranked records
- display ordering
- chronological records
- priority queues implemented as arrays
- ordered user interfaces

## Unordered deletion in the C++ case study

The `eraseUnordered()` method replaces the deleted element with the final element.

For:

`10, 20, 30, 40`

deleting index `1` can produce:

`10, 40, 30`

Only one assignment is needed.

This is `O(1)` when the index is already known.

The trade-off is that the original order is lost.

This technique is appropriate when:

- ordering has no semantic meaning
- the array represents a set-like collection
- fast deletion matters more than stable ordering

It is inappropriate when users expect a particular order.

## Queue design implications

A queue follows first-in, first-out behavior.

The naive array-backed implementation performs deletion at index `0`.

If the queue contains:

`A, B, C, D`

dequeueing `A` requires:

`B → index 0`

`C → index 1`

`D → index 2`

Repeated dequeues can therefore result in many element movements.

A circular queue changes the representation.

Instead of physically moving elements after every dequeue, it records the logical front and calculates positions using modular arithmetic.

The circular queue therefore demonstrates how a suitable data structure can change the cost profile of repeated operations.

## Edge cases

Insertion and deletion implementations must handle boundary conditions explicitly.

### Empty array

Deleting from an empty array is invalid.

The implementations raise or throw an exception.

### Index equal to size during insertion

An insertion index equal to the current size is valid.

For example:

`[10, 20, 30]`

inserting at index `3` produces:

`[10, 20, 30, new_value]`

### Index equal to size during deletion

An index equal to the current size is invalid because valid element indices end at `size - 1`.

### Negative indexes

Python naturally supports negative indexing in lists, but the educational insertion functions deliberately use explicit validation.

The JavaScript and C++ examples use explicit non-negative index validation except where the dynamic-array demonstrations intentionally support a negative index as a convenience.

### Missing value

Deleting a value that does not exist should not silently corrupt the data structure.

The Python and JavaScript examples raise errors.

The C++ inventory operation returns `false` when a product ID is not found.

The appropriate behavior depends on the application's API design.

### Duplicate values

Deleting by value requires defining whether the operation removes:

- the first occurrence
- all occurrences
- a particular occurrence

The implementations demonstrate both first-match and all-match behavior.

## Exceptions and validation

Validation prevents invalid operations from producing incorrect state.

Important checks include:

- array is not empty before deletion
- index is within bounds
- insertion index is between `0` and `size`
- values satisfy domain constraints
- dynamic-array capacity is sufficient before writing
- queue is not empty before dequeue
- queue is not full before enqueue

The C++ case study also validates product quantity, price, and ID.

## Common mistakes

### Shifting in the wrong direction

During right-shifting for insertion, start from the end.

Moving from left to right can overwrite values.

### Forgetting to increase logical size

An insertion requires the logical size to increase.

### Forgetting to decrease logical size

A deletion must reduce logical size after the remaining elements have been moved.

### Accessing an invalid index

An index outside the valid range can cause exceptions or undefined behavior depending on the language and operation.

### Assuming every array operation is `O(1)`

Indexed access is typically `O(1)`, but arbitrary insertion and deletion are often `O(n)`.

### Ignoring order requirements

Unordered deletion is faster, but it changes the sequence.

It should only be used when the application does not depend on order.

### Repeatedly deleting index zero

Repeated front deletion from an array can result in repeated shifting and poor performance.

A queue, deque, circular buffer, linked structure, or another representation may be more appropriate depending on requirements.

### Excessive resizing

Growing the backing storage by only one position at a time can cause repeated reallocations.

Geometric growth reduces the number of resizes.

### Shrinking too aggressively

Shrinking after every deletion can cause alternating growth and shrink operations.

A threshold-based strategy avoids unnecessary reallocations.

## Important distinctions

### Size versus capacity

Size answers:

"How many elements are stored?"

Capacity answers:

"How many elements can be stored before the backing storage must grow?"

These are different concepts.

### Array versus dynamic array

A fixed-size array has a predetermined storage capacity.

A dynamic array can allocate a larger storage area when necessary.

Python lists and JavaScript arrays provide dynamic-array-like behavior to programmers.

The C++ case study explicitly models the underlying mechanism.

### Stable versus unordered deletion

Stable deletion:

- preserves order
- can require many movements
- generally costs `O(n)`

Unordered deletion:

- does not preserve order
- can be `O(1)` for a known index
- is useful when order is irrelevant

### Search versus deletion

Deleting by value is not equivalent to deleting by index.

Deleting by index assumes the location is known.

Deleting by value normally requires a search first.

This distinction is important in complexity analysis.

## Performance considerations

The most important performance factor in array insertion and deletion is the number of elements that must move.

For a large array, inserting at the beginning can be substantially more expensive than appending.

For example, if an array contains one million elements:

- append may require no existing-element movement
- beginning insertion can require one million movements
- middle insertion can require approximately half a million movements

The actual cost also depends on the size of each element.

Moving a small integer is generally cheaper than moving a large object or performing expensive copy operations.

In C++, move semantics can reduce the cost of transferring objects when the type supports efficient moves.

## Memory considerations

Dynamic arrays usually reserve unused capacity.

This consumes more memory than the exact logical size, but the extra capacity enables efficient growth.

There is therefore a space-time trade-off:

- more spare capacity can reduce the frequency of reallocations
- less spare capacity can reduce unused memory
- aggressive shrinking can increase allocation overhead
- geometric growth provides a useful balance for general-purpose dynamic arrays

## Security and reliability considerations

Array manipulation is also relevant to software reliability and security.

Important considerations include:

- validate external indexes before accessing storage
- reject negative or excessively large positions where they are not supported
- prevent writes beyond allocated capacity
- maintain size and capacity invariants
- validate domain data before inserting it
- avoid integer overflow when calculating new capacities
- handle allocation failures appropriately in production C++
- avoid using uninitialized storage as though it contained valid elements
- test empty-array and single-element cases
- test very large inputs where performance changes become significant

The C++ implementation uses bounds validation and exceptions to make invalid states explicit.

## Production design considerations

A production system should not automatically choose an array simply because indexed access is fast.

The correct structure depends on workload.

An array or dynamic array is appropriate when:

- indexed access is frequent
- data is naturally sequential
- memory locality matters
- insertion and deletion are relatively infrequent
- appending is common

Other structures may be more appropriate when:

- frequent front insertion or deletion is required
- frequent arbitrary insertion is required
- order is not important
- fast key-based lookup is required
- concurrent access has specific synchronization requirements

The correct choice should be driven by the actual access and mutation pattern.

## Practical applications

Array insertion and deletion appear in many systems.

Examples include:

- task lists
- inventory systems
- user interface lists
- search results
- playlists
- rankings
- buffers
- event queues
- order management
- memory tables
- scheduling systems
- simulation state
- game entity collections
- numerical computing
- data-processing pipelines

The underlying operation is the same even when the application domain changes: an ordered contiguous sequence must accommodate or remove an element.

## Implementation comparison

| Concern | Python | JavaScript | C++ |
|---|---|---|---|
| Main structure | `list` | `Array` | Custom `DynamicArray<T>` |
| Dynamic growth | Runtime-managed | Runtime-managed | Explicitly implemented |
| Manual shifting | Demonstrated | Demonstrated | Explicitly implemented |
| Index validation | Explicit | Explicit | Explicit |
| Stable deletion | Yes | Yes | Yes |
| Unordered deletion | Yes | Yes | Yes |
| Duplicate deletion | Demonstrated | Demonstrated | Demonstrated |
| Queue example | Yes | Conceptual application | Yes |
| Memory management | Runtime-managed | Runtime-managed | Explicit |
| Generic structure | Python class | JavaScript class | C++ template |
| Testing | Assertions | Custom assertions | Exception-based tests |

## Testing strategy

The implementations include tests for:

- insertion at the beginning
- insertion at the end
- insertion at an arbitrary position
- deletion at the beginning
- deletion at the end
- deletion by index
- deletion by value
- deletion of duplicates
- shifting
- unordered deletion
- dynamic-array growth
- dynamic-array deletion
- queue behavior
- invalid indexes
- empty-array operations

Boundary testing is especially important for array operations because off-by-one errors commonly occur at:

- index `0`
- index `size - 1`
- insertion index `size`
- empty arrays
- one-element arrays

## Algorithmic reasoning

The core reasoning can be expressed directly through the number of elements moved.

For insertion:

`elements moved = n - i`

For deletion:

`elements moved = n - i - 1`

This gives a direct bridge between the physical operation and its Big-O complexity.

The maximum number of shifts occurs near the beginning.

The minimum number occurs at the end.

This is the fundamental performance principle demonstrated throughout the three implementations.
