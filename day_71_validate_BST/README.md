# Validate Binary Search Tree

## 1. Technical Scope

A Binary Search Tree (BST) is a binary tree that maintains an ordering relationship between the keys stored in its nodes.

For a BST with unique keys:

- Every key in the left subtree is smaller than the current node.
- Every key in the right subtree is greater than the current node.
- Both subtrees must independently satisfy the same ordering rules.

The defining property applies to entire subtrees, not just immediate children.

Consider the following tree:

             50
           /    \
         30      70
        /  \    /  \
       20  40  60  80

Its inorder traversal is:

`20, 30, 40, 50, 60, 70, 80`

The sequence is strictly increasing, so the tree satisfies the BST property.

An important counterexample is:

             10
            /  \
           5    15
            \
             12

The node `12` is greater than its immediate parent `5`, but it is located in the left subtree of `10`. Therefore, the tree is invalid.

This distinction motivates two important validation algorithms.

## 2. Range-Based Validation

Range-based validation assigns an allowable interval to every node.

Initially, the root has no lower or upper restriction.

For each node:

- Its left child inherits the current lower bound and receives the current node's key as its upper bound.
- Its right child receives the current node's key as its lower bound and inherits the current upper bound.

For a tree containing unique keys, the interval is:

\[
low < key < high
\]

The algorithm rejects a node whenever its value falls outside its permitted interval.

### Example

Consider:

             50
           /    \
         30      70
        /  \    /  \
       20  40  60  80

The root has an unrestricted range.

| Node | Permitted range |
|---|---|
| 50 | Unrestricted |
| 30 | Less than 50 |
| 70 | Greater than 50 |
| 20 | Less than 30 |
| 40 | Between 30 and 50 |
| 60 | Between 50 and 70 |
| 80 | Greater than 70 |

A node must satisfy every inherited ancestor constraint.

### Complexity

| Metric | Complexity |
|---|---|
| Time | O(n) |
| Recursive auxiliary space | O(h) |
| Iterative auxiliary space | O(h) |
| Worst-case height | O(n) |
| Balanced-tree height | O(log n) |

Here, `n` represents the number of nodes and `h` represents tree height.

The Python implementation provides recursive range validation. The JavaScript, C++17 and Java implementations use explicit stacks for range propagation.

The PostgreSQL implementation uses recursive CTEs to propagate bounds through relational node references.

## 3. Inorder-Based Validation

Inorder traversal visits nodes in this order:

1. Left subtree.
2. Current node.
3. Right subtree.

A valid BST with unique keys must produce a strictly increasing sequence.

For example:

`20, 30, 40, 50, 60, 70, 80`

The validation condition is:

\[
current > previous
\]

If a current value is less than or equal to the previous value, the tree is invalid under the unique-key policy.

### Iterative Algorithm

An explicit stack eliminates the need for recursive calls.

The algorithm:

- Starts at the root.
- Pushes nodes while moving left.
- Processes the top stack element.
- Compares its key against the previously processed key.
- Moves to its right subtree.
- Continues until both the current pointer and stack are empty.

### Complexity

| Metric | Complexity |
|---|---|
| Time | O(n) |
| Auxiliary space | O(h) |
| Output storage | O(n) if traversal results are retained |

The implementations perform validation directly without requiring a complete inorder array.

This reduces unnecessary memory allocation.

## 4. Range Validation vs Inorder Validation

Both approaches establish the same global ordering property for a BST with unique keys, but they use different mechanisms.

| Characteristic | Range-based | Inorder-based |
|---|---|---|
| Main mechanism | Ancestor-derived bounds | Sorted traversal |
| Data structure | Stack or recursion | Traversal stack |
| Time complexity | O(n) | O(n) |
| Auxiliary space | O(h) | O(h) |
| Detects global ordering violations | Yes | Yes |
| Explicit permitted intervals | Yes | No |
| Produces sorted traversal | No | Yes |
| Useful for | Structural validation | Ordering verification |

Range-based validation is particularly useful when explaining why a node violates an ancestor constraint.

Inorder validation is useful when sorted traversal is already required for another operation.

Neither method automatically verifies that a relational representation contains no disconnected nodes, duplicate references, or cycles. Those structural conditions must also be checked when the tree is stored outside a conventional pointer-based representation.

## 5. Duplicate-Key Policies

Duplicate handling must be explicitly defined.

Three policies are implemented.

| Policy | Left subtree | Right subtree |
|---|---|---|
| FORBID | Strictly smaller | Strictly greater |
| LEFT | Smaller or equal | Strictly greater |
| RIGHT | Strictly smaller | Greater or equal |

Under the `FORBID` policy, inorder traversal must be strictly increasing.

Under the other policies, inorder traversal must be nondecreasing.

An important distinction exists between sorted traversal and duplicate placement.

For example, an inorder sequence can be nondecreasing even when a duplicate appears in a subtree that violates the configured placement rule.

Therefore, the implementations also examine duplicate placement relative to equal ancestors.

For large datasets, duplicate values are often better represented through a frequency field or a collection of records associated with a unique tree key. This avoids ambiguity in structural successor and predecessor operations.

## 6. Successor and Predecessor

The inorder successor of a node is the next node encountered during inorder traversal.

The inorder predecessor is the previous node.

These operations are closely related to ordered searching.

### Successor

For an existing node:

**Case 1: The node has a right subtree.**

The successor is the minimum-valued node in its right subtree.

Example:

             50
           /    \
         30      70
                   \
                    80

The successor of `70` is `80` when a right subtree contains that minimum.

**Case 2: The node has no right subtree.**

Move upward through the search path.

The successor is the lowest ancestor for which the original node belongs to its left subtree.

Example:

             50
           /    \
         30      70
        /  \
       20  40

The successor of `40` is `50`.

The node has no right subtree, so the search moves upward until it reaches an ancestor greater than `40`.

### Predecessor

The logic is symmetric.

**Case 1: The node has a left subtree.**

The predecessor is the maximum-valued node in its left subtree.

**Case 2: The node has no left subtree.**

Move upward until reaching the lowest ancestor for which the original node belongs to its right subtree.

### Successor of an Existing Node vs Next Greater Key

The implementations expose two related operations:

| Operation | Meaning |
|---|---|
| `successorOfNode(key)` | Inorder successor of an existing node |
| `successor(key)` | Smallest stored key strictly greater than the supplied key |
| `predecessorOfNode(key)` | Inorder predecessor of an existing node |
| `predecessor(key)` | Largest stored key strictly smaller than the supplied key |

The distinction matters when the supplied key is absent from the tree.

For example, given:

`20, 30, 40, 50, 60, 70, 80`

The successor of `55` is `60`, even though `55` is not a stored node.

### Complexity

| Operation | Complexity |
|---|---|
| Successor | O(h) |
| Predecessor | O(h) |
| Minimum | O(h) |
| Maximum | O(h) |
| Search | O(h) |

## 7. Supporting BST Operations

The implementations include additional operations that establish the complete lifecycle of a search tree.

### Search

Compare the requested key with the current node.

- Equal: return the node.
- Smaller: move left.
- Greater: move right.

The search terminates when the key is found or a null child is reached.

### Insertion

Insertion follows the same comparison process as searching.

The new node is attached at the first permitted empty child position.

The configured duplicate policy determines whether equal keys are rejected or directed to a specific subtree.

### Deletion

Deletion has three structural cases.

| Case | Operation |
|---|---|
| Leaf node | Remove the node |
| One child | Replace the node with its child |
| Two children | Replace its key with its inorder successor and remove that successor node |

The successor is selected from the right subtree.

It has no left child, so its removal requires at most one child-link replacement.

### Lowest Common Ancestor

The lowest common ancestor (LCA) is the deepest node that is an ancestor of both requested nodes.

BST ordering provides an efficient search strategy.

- If both keys are smaller than the current key, move left.
- If both keys are greater, move right.
- Otherwise, the current node is their lowest common ancestor.

The implementations verify that both requested keys exist before returning an LCA.

## 8. Python Implementation

**File:** `validate_bst.py`

The Python implementation uses object-oriented domain modeling and standard-library features.

| Component | Purpose |
|---|---|
| `Node` | Represents a tree node |
| `DuplicatePolicy` | Defines duplicate placement |
| `BinarySearchTree` | Owns BST operations |
| `BSTError` | Base exception |
| `DuplicateKeyError` | Handles duplicate insertion |
| `validate_range()` | Performs range validation |
| `validate_inorder()` | Checks sorted traversal |
| `successor()` | Finds the next greater key |
| `predecessor()` | Finds the previous smaller key |
| `delete()` | Removes a node |
| `to_dict()` | Exports a nested tree representation |

The implementation uses `dataclasses`, `Enum`, type annotations, optional node references, and explicit exception handling.

The demonstration includes malformed trees, duplicate-key behavior, extreme integer values, and automated assertions.

Python integers have arbitrary precision, so the range-validation implementation does not depend on fixed-width integer boundaries.

## 9. JavaScript Implementation

**File:** `validate_bst.js`

The JavaScript implementation introduces an event-driven validation service.

Its main components are:

| Component | Purpose |
|---|---|
| `TreeNode` | Represents nodes |
| `BinarySearchTree` | Implements tree operations |
| `BSTValidationService` | Coordinates validation |
| `EventEmitter` | Publishes validation events |
| `Map` | Stores validation records |
| `Promise.all()` | Coordinates batch validation |
| `assert` | Checks expected behavior |

JavaScript uses `Number.isSafeInteger()` to prevent precision-related ordering errors.

The validation service emits:

- `validation:passed`
- `validation:failed`

Each event contains a tree identifier, validation result, node count, and timestamp.

The asynchronous batch operation demonstrates how several independently maintained trees can be validated through one service interface.

The batch implementation does not make CPU-intensive validation parallel. Its asynchronous interface supports coordination, but actual CPU parallelism would require worker threads or another execution strategy.

## 10. C++17 Implementation

**File:** `validate_bst.cpp`

The C++ implementation emphasizes explicit ownership and memory management.

| Component | Purpose |
|---|---|
| `Node` | Tree-node structure |
| `unique_ptr` | Exclusive ownership of child nodes |
| `optional` | Represents absent keys and bounds |
| `stack` | Supports iterative traversal |
| `vector` | Stores traversal results |
| `enum class` | Defines duplicate policies |
| `BinarySearchTree` | Encapsulates tree behavior |

`unique_ptr` ensures that each node has a single owner.

Deleting a node transfers ownership of its surviving child into the appropriate parent link.

The implementation uses `optional<long long>` for range boundaries. This avoids reserving an ordinary integer value as a special representation of an unbounded range.

The `erase()` method handles root replacement, one-child deletion, and two-child deletion.

Assertions cover successor and predecessor boundaries, deletion, invalid global ordering, duplicate insertion, and extreme integer values.

## 11. Java 17 Implementation

**File:** `ValidateBST.java`

The Java implementation presents BST operations through an enterprise-oriented service structure.

| Component | Purpose |
|---|---|
| `Node` | Encapsulates node state |
| `BinarySearchTree` | Maintains tree invariants |
| `DuplicatePolicy` | Defines duplicate rules |
| `ValidationResult` | Immutable validation record |
| `BSTValidationService` | Provides validation operations |
| `BSTException` | Base domain exception |
| `DuplicateKeyException` | Handles invalid duplicate insertion |
| `MissingNodeException` | Represents missing-node failures |

Java 17 records provide immutable validation results.

`Optional` represents missing successors, predecessors, search results, and LCA results without using arbitrary sentinel values.

The validation service supports batch processing through collections and streams.

The implementation also demonstrates how custom domain exceptions distinguish expected business-rule failures from successful operations.

Run with Java assertions enabled when executing the test cases.

## 12. PostgreSQL Implementation

**File:** `validate_bst.sql`

The PostgreSQL implementation represents a BST as relational data rather than in-memory pointers.

The principal relationship is:

`bst_trees → bst_nodes → bst_nodes`

The `bst_nodes` table stores:

- Node identifier.
- Tree identifier.
- Key.
- Parent identifier.
- Left-child identifier.
- Right-child identifier.

### Database Components

| Database object | Responsibility |
|---|---|
| `bst_trees` | Tree metadata and root references |
| `bst_nodes` | Node and relationship storage |
| `validation_audit` | Validation history |
| `bst_tree_report` | Tree-level reporting |
| `validate_bst_range()` | Range-based validation |
| `validate_bst_inorder()` | Inorder validation |
| `bst_insert()` | Transactional node insertion |
| `bst_delete()` | Node deletion |
| `bst_search()` | Key lookup |
| `bst_successor()` | Next greater key |
| `bst_predecessor()` | Previous smaller key |
| `bst_lca()` | Lowest common ancestor |
| `record_bst_validation()` | Validation audit procedure |

### Relational Integrity

Primary keys identify individual records.

Foreign keys connect nodes with their trees and parent-child relationships.

Unique indexes prevent a node from being assigned to multiple parent or child positions within the corresponding relationship.

The tree root uses a composite foreign key so that its referenced node must belong to the same tree.

These constraints establish important structural conditions, but they do not independently guarantee global BST ordering.

The validation routines must still examine the complete tree.

### Recursive CTEs

Recursive common table expressions traverse hierarchical relationships.

Range validation propagates lower and upper boundaries through child relationships.

Inorder validation derives a traversal sequence and compares adjacent keys.

The recursive queries also account for reachability and malformed structural references.

### Transactions

Insertion and deletion use transactions and row-level locking.

A tree-level lock serializes competing modifications to the same tree.

Validation can be performed before committing a structural change.

If validation raises an exception, PostgreSQL rolls back the affected transaction.

### Database Limitations

The SQL implementation is an educational relational representation.

For a production implementation, additional protections are necessary:

- Restrict direct modification of structural columns.
- Enforce same-tree relationships on all node references.
- Enforce acyclic parent-child relationships.
- Ensure every non-root node has exactly one valid parent.
- Prevent inconsistent parent and child references.
- Use a consistent duplicate policy during every operation.
- Review transaction isolation and concurrent modification behavior.

Recursive traversal also has a practical depth limitation in the demonstration's positional encoding. Large production trees require a traversal representation designed for their expected maximum depth.

For ordinary database indexing, PostgreSQL's native B-tree indexes are generally preferable to maintaining a manually implemented unbalanced BST.

## 13. Complexity Analysis

Let:

- `n` = number of nodes.
- `h` = height of the tree.

| Operation | Average balanced BST | Worst-case BST |
|---|---:|---:|
| Search | O(log n) | O(n) |
| Insertion | O(log n) | O(n) |
| Deletion | O(log n) | O(n) |
| Range validation | O(n) | O(n) |
| Inorder validation | O(n) | O(n) |
| Successor | O(log n) | O(n) |
| Predecessor | O(log n) | O(n) |
| Minimum | O(log n) | O(n) |
| Maximum | O(log n) | O(n) |
| Lowest common ancestor | O(log n) | O(n) |
| Inorder traversal | O(n) | O(n) |

A conventional BST does not automatically remain balanced.

Inserting sorted values such as:

`10, 20, 30, 40, 50, 60`

can create a tree resembling a linked list.

This increases search, insertion, deletion, successor, and predecessor costs to O(n).

Self-balancing trees such as AVL trees and Red-Black trees address this issue by maintaining additional structural invariants.

## 14. Edge Cases and Failure Handling

The source implementations cover the following cases:

| Scenario | Expected behavior |
|---|---|
| Empty tree | Valid BST |
| Single-node tree | Valid BST |
| Negative keys | Supported |
| Minimum integer | Supported |
| Maximum integer | Supported |
| Duplicate key under FORBID | Rejected |
| Duplicate key under LEFT | Allowed on left |
| Duplicate key under RIGHT | Allowed on right |
| Invalid ancestor relationship | Rejected |
| Missing search key | Empty result |
| Successor of maximum | No successor |
| Predecessor of minimum | No predecessor |
| Missing deletion key | No structural modification |
| Delete leaf | Remove node |
| Delete one-child node | Promote child |
| Delete two-child node | Replace with successor |
| Missing LCA input | No LCA returned |

A malformed tree should not be treated as valid merely because its immediate parent-child comparisons appear correct.

## 15. Security and Performance Considerations

### Memory Safety

The C++ implementation uses exclusive ownership through `unique_ptr`.

The Python and JavaScript implementations explicitly represent missing child references using `None` and `null`.

The Java implementation uses encapsulated node state.

### Numeric Safety

JavaScript's safe-integer limitation is checked before insertion and searching.

C++ uses optional numeric bounds.

Python supports arbitrary-precision integers.

Java uses fixed-width integer values with wider numeric bounds for validation.

### Input Validation

All implementations reject or control invalid duplicate insertion according to the configured policy.

Production interfaces should also impose limits on tree size, input volume, and execution time.

### Unbalanced Trees

An unbalanced BST can produce unexpectedly high processing costs.

Applications handling large or adversarial input should consider self-balancing trees.

### Database Concurrency

Database operations that modify parent-child relationships must be transactional.

Concurrent writers require consistent locking and integrity enforcement to prevent structural corruption.

### Auditability

The PostgreSQL implementation records validation outcomes, including the validation method, node count, status, and timestamp.

This provides a basis for monitoring structural changes and investigating invalid trees.

## 16. Execution

### Python

File: `validate_bst.py`

Python 3.10 or later.

### JavaScript

File: `validate_bst.js`

Node.js 18 or later.

### C++17

File: `validate_bst.cpp`

Compile using a C++17-compatible compiler.

### Java 17

File: `ValidateBST.java`

Compile and execute with Java 17. Enable assertions for the included tests.

### PostgreSQL

File: `validate_bst.sql`

Execute using PostgreSQL 15 or later.

The SQL script creates its own `bst_lab` schema and sample datasets.

## 17. Learning Outcomes

The five implementations establish the following relationships:

| Concept | Technical understanding |
|---|---|
| BST invariant | Global ordering across complete subtrees |
| Range validation | Ancestor-derived constraints |
| Inorder validation | Sorted traversal property |
| Duplicate policies | Explicit equality placement |
| Search | Ordered navigation |
| Successor | Next greater element |
| Predecessor | Previous smaller element |
| Deletion | Structural replacement |
| LCA | Shared ancestor using BST ordering |
| Relational representation | Hierarchical data stored through foreign keys |
| Validation auditing | Recorded integrity results |

The central distinction is that a BST is defined by its complete ordering invariant. Correct parent-child comparisons alone are insufficient. Both range-based and inorder-based validation provide ways to verify that invariant, while successor and predecessor operations use the same ordering structure to navigate between adjacent keys.
