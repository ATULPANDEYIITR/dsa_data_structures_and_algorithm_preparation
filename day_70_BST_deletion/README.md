# Binary Search Tree Deletion

## 1. Technical Overview

A Binary Search Tree (BST) is a hierarchical data structure in which every node follows an ordering rule:

- Keys in the left subtree are smaller than the node's key.
- Keys in the right subtree are greater than the node's key.
- Both subtrees independently satisfy the BST property.

This implementation uses unique integer keys. Duplicate insertions are rejected to maintain strict ordering.

The principal operation studied is deletion. Unlike insertion, deletion must preserve the ordering relationship while removing a node and potentially reconnecting its descendants.

## 2. BST Structure

A node contains three logical components:

| Component | Purpose |
|---|---|
| Key | Stores the value used for ordering |
| Left | References the left subtree |
| Right | References the right subtree |

The implementations use different memory-management approaches:

| Language | Implementation decision |
|---|---|
| Python | Node dataclass with optional child references |
| JavaScript | Node objects, parent references and Map registry |
| C++17 | Struct-based nodes with unique_ptr ownership |
| Java 17 | Explicit node classes and replacement policy objects |
| PostgreSQL | Relational nodes with parent references |

The following tree is used for the principal deletion examples:

                 50
              /      \
            30        70
           /  \      /  \
         20   40    60   80
             /  \     \
            35  45    65

Its inorder traversal is:

`20, 30, 35, 40, 45, 50, 60, 65, 70, 80`

An inorder traversal of a valid BST produces keys in ascending order.

## 3. BST Deletion Cases

Deletion requires identifying the structural position of the requested node.

### 3.1 Leaf Node Deletion

A leaf is a node without children.

Example: deleting `20`.

Before:

                 30
                /
               20

After:

                 30

The parent no longer references the deleted node.

If the deleted node is the root and has no children, the tree becomes empty.

**Implementation rule:** Replace the reference to the leaf with `null` or an empty ownership pointer.

Time complexity: O(h).

Space complexity: O(h) for recursive implementations, excluding the existing tree.

### 3.2 Node with One Child

A node with one child must be removed without losing its descendant subtree.

Example: deleting `60`.

Before:

                 70
                /
               60
                 \
                  65

After:

                 70
                /
               65

The child replaces the deleted node directly.

There are two possibilities:

- Only a left child exists.
- Only a right child exists.

The same principle applies when the node being deleted is the root.

**Implementation rule:** Transfer the existing child reference to the deleted node's parent.

Time complexity: O(h).

### 3.3 Node with Two Children

This is the most important deletion case.

A node with two children cannot simply be removed and replaced by either child. Doing so may violate the ordering relationship.

Two valid replacement strategies exist:

1. Inorder successor.
2. Inorder predecessor.

The implementations support both strategies.

#### Inorder Successor

The inorder successor is the smallest key greater than the requested key.

It is identified by:

1. Moving to the right subtree.
2. Repeatedly following left-child references.
3. Selecting the leftmost node.

For the example tree, the successor of `50` is `60`.

The replacement maintains:

- All keys in the left subtree smaller than `60`.
- All keys in the right subtree greater than `60`.

#### Inorder Predecessor

The inorder predecessor is the largest key smaller than the requested key.

It is identified by:

1. Moving to the left subtree.
2. Repeatedly following right-child references.
3. Selecting the rightmost node.

For the example tree, the predecessor of `50` is `45`.

Both strategies preserve BST ordering when implemented correctly.

### 3.4 Successor and Predecessor Comparison

| Property | Successor | Predecessor |
|---|---|---|
| Definition | Next larger key | Next smaller key |
| Initial subtree | Right | Left |
| Navigation | Repeatedly left | Repeatedly right |
| Selected node | Minimum of right subtree | Maximum of left subtree |
| Replacement position | Deleted node's position | Deleted node's position |

Neither strategy is universally better. Both have O(h) search complexity.

## 4. Important Deletion Mechanisms

### 4.1 Recursive Deletion

Recursive deletion follows the BST ordering rule.

At each node:

- Search left when the requested key is smaller.
- Search right when the requested key is greater.
- Apply the appropriate deletion case when the key matches.

The recursive function returns the updated subtree root.

This return value is essential because deletion can change the root of a subtree.

### 4.2 Subtree Transplantation

The JavaScript implementation uses parent references and a transplant operation.

A transplant replaces one node with another while updating the parent relationship.

This is particularly useful for two-child deletion because the successor can be physically moved into the deleted node's position.

The C++ implementation uses `std::unique_ptr` instead. Moving ownership of child subtrees avoids manual memory allocation and deallocation.

### 4.3 Extracting the Minimum

The C++ implementation uses an `extractMinimum` operation.

A minimum node cannot have a left child.

It may have a right child, which must replace it at its original location.

This operation isolates the successor while preserving the remaining subtree.

### 4.4 Parent References

Parent pointers provide upward navigation.

They make successor and predecessor operations convenient because an ancestor can be examined without restarting from the root.

They also introduce an additional integrity requirement: every child reference must have the correct corresponding parent reference.

The JavaScript implementation explicitly validates these relationships.

## 5. Implementation Details

### 5.1 Python

The Python implementation emphasizes algorithmic clarity.

Important components:

| Component | Responsibility |
|---|---|
| `Node` | Stores a key and child references |
| `BinarySearchTree` | Maintains the root and node count |
| `insert()` | Inserts unique keys |
| `delete()` | Handles all three deletion cases |
| `delete_using_predecessor()` | Implements alternative replacement |
| `successor()` | Finds the next larger key |
| `predecessor()` | Finds the next smaller key |
| `validate()` | Checks ordering and node count |

Iterative traversal methods avoid unnecessary recursion for reading tree contents.

The deletion operation is recursive, which provides a direct representation of subtree replacement.

### 5.2 JavaScript

The JavaScript implementation emphasizes event-driven state management.

The `EventEmitter` publishes events for:

- Successful insertion.
- Successful deletion.
- Missing keys.
- Tree clearing.

A `Map` maintains a key-to-node registry, making exact-key lookup O(1) on average.

This registry is an auxiliary index. It does not replace the BST structure or change the ordering requirements.

Parent pointers are used for upward navigation and structural transplantation.

The mutation operations remain synchronous. The asynchronous workflow demonstrates how the tree can participate in a larger Node.js process.

### 5.3 C++17

The C++ implementation emphasizes ownership and resource safety.

`std::unique_ptr` establishes exclusive ownership of each child subtree.

When a node is deleted:

- A leaf releases its ownership.
- A one-child node transfers ownership to its replacement.
- A two-child node receives ownership from the extracted successor.

Copy operations are disabled because duplicating a tree requires explicit deep-copy semantics.

Move operations are enabled.

This design avoids raw owning pointers and reduces the possibility of memory leaks or double deletion.

### 5.4 Java 17

The Java implementation emphasizes explicit domain modeling.

Important domain types include:

| Type | Purpose |
|---|---|
| `DeletionCase` | Identifies the structural deletion case |
| `ReplacementStrategy` | Selects successor or predecessor |
| `DeletionResult` | Captures the operation outcome |
| `AuditEvent` | Records the operation |
| `ReplacementPolicy` | Defines replacement selection |
| `SuccessorPolicy` | Finds the successor |
| `PredecessorPolicy` | Finds the predecessor |

The deletion service separates replacement selection from structural modification.

The returned deletion record identifies:

- Requested key.
- Whether deletion succeeded.
- Deletion category.
- Replacement key, when applicable.
- Remaining node count.

This makes operation results suitable for application-level auditing.

### 5.5 PostgreSQL

The PostgreSQL implementation represents the BST through relational records.

The principal tables are:

| Table | Responsibility |
|---|---|
| `trees` | Stores independent tree instances |
| `nodes` | Stores keys and parent relationships |
| `tree_roots` | Identifies each tree's root |
| `deletion_audit` | Records deletion outcomes |

Composite foreign keys restrict parent references to the same tree.

A unique constraint prevents duplicate keys within an individual tree.

The insertion and deletion procedures serialize mutations by locking the corresponding tree record.

Recursive CTEs support structural validation.

The audit table distinguishes successful deletion cases from unsuccessful requests.

The relational representation is intentionally different from an in-memory binary node structure. Child relationships are determined through the parent reference and key ordering.

## 6. Deletion Workflow

The complete deletion workflow follows this sequence:

                 Receive requested key
                          |
                          v
                   Search the BST
                          |
                 +--------+--------+
                 |                 |
              Not found           Found
                 |                 |
              Return         Examine children
                                   |
                     +-------------+-------------+
                     |             |             |
                    Zero          One           Two
                   children     child       children
                     |             |             |
                  Remove        Promote       Select
                   node          child       replacement
                                                 |
                                      +----------+----------+
                                      |                     |
                                  Successor             Predecessor
                                      |                     |
                                      +----------+----------+
                                                 |
                                        Reconnect subtrees
                                                 |
                                                 v
                                          Validate BST
                                                 |
                                                 v
                                          Record result

The process must maintain the ordering invariant after every successful operation.

## 7. Complexity Analysis

Let:

- `n` represent the number of nodes.
- `h` represent the tree height.

| Operation | Average balanced BST | Worst-case BST |
|---|---:|---:|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Successor | O(log n) | O(n) |
| Predecessor | O(log n) | O(n) |
| Minimum | O(log n) | O(n) |
| Maximum | O(log n) | O(n) |
| Inorder traversal | O(n) | O(n) |
| Structural validation | O(n) | O(n) |

Deletion requires at most one search path and one replacement search path. Both are bounded by the tree height.

Recursive deletion requires O(h) auxiliary stack space.

Iterative search and traversal methods use O(h) auxiliary storage in the worst case.

A plain BST does not guarantee logarithmic height.

## 8. Edge Cases and Validation

The implementations account for the following situations:

| Scenario | Expected behavior |
|---|---|
| Empty tree deletion | Return unsuccessful |
| Single-node deletion | Root becomes empty |
| Leaf deletion | Parent loses the child |
| One-child deletion | Child replaces deleted node |
| Two-child deletion | Successor or predecessor replaces node |
| Root deletion | Root reference changes |
| Missing key | No structural modification |
| Duplicate insertion | Reject duplicate |
| Minimum-key deletion | Preserve remaining ordering |
| Maximum-key deletion | Preserve remaining ordering |
| Repeated deletion | Handle missing keys safely |
| Invalid key type | Reject invalid input |
| Invalid replacement policy | Reject the operation |

Structural validation checks the strict ordering condition:

`lower_bound < node.key < upper_bound`

This is stronger than checking only whether each node is greater than its left child and smaller than its right child.

It verifies the complete ancestor-imposed ordering constraints.

## 9. Testing Strategy

The Python, JavaScript, C++ and Java programs exercise:

- Leaf deletion.
- One-child deletion.
- Two-child deletion.
- Root deletion.
- Successor calculation.
- Predecessor calculation.
- Missing-key deletion.
- Duplicate insertion.
- Empty-tree deletion.
- Single-node deletion.
- Structural validation.

The PostgreSQL script exercises independent trees, relational constraints, deletion procedures, transaction handling and audit reporting.

A particularly important test is deleting a node whose successor has a right child.

That successor must be detached from its original location, and its right child must be reconnected before the successor replaces the deleted node.

Failing to perform this reconnection causes data loss.

## 10. Practical Limitations

A standard BST can become highly unbalanced when keys are inserted in sorted order.

For example:

    10
      \
       20
         \
          30
            \
             40

Its height is O(n), so search and deletion can degrade to linear time.

The implementations do not automatically rebalance the tree.

AVL trees and Red-Black trees address this limitation through rotations and balancing invariants.

The Python, C++ and Java implementations use recursive deletion, so extremely unbalanced trees can encounter call-stack limitations.

The JavaScript and C++ implementations also illustrate different ownership and navigation choices, rather than claiming that one representation is universally preferable.

The PostgreSQL representation uses relational parent references and is intended for educational workflow modeling. Production systems requiring frequent structural changes would need additional concurrency, integrity and indexing controls, including careful validation of parent-child ordering and cycle prevention.

## 11. Important Distinctions

| Concept | Meaning |
|---|---|
| BST deletion | Removes a key while preserving ordering |
| Successor | Smallest key greater than a given key |
| Predecessor | Largest key smaller than a given key |
| Transplantation | Replaces a subtree reference |
| Subtree | A node and all its descendants |
| Root | Topmost node of the tree |
| Leaf | Node without children |
| Height | Maximum number of nodes along a root-to-leaf path |
| Inorder traversal | Left, root, right |
| Structural invariant | Ordering condition that every node must satisfy |

The central requirement of BST deletion is not merely removing a node. It is preserving every remaining key and every ordering relationship while correctly reconnecting the affected subtrees.
