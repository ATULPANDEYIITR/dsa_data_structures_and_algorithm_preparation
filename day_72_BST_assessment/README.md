# Binary Search Tree Assessment and Practice

## 1. Domain and Assessment Objectives

A Binary Search Tree (BST) is a binary tree that maintains an ordering relationship between the keys stored in its nodes.

For every node:

- All keys in its left subtree are smaller than its key.
- All keys in its right subtree are greater than its key.
- Both subtrees independently satisfy the BST property.

The implementations use a strict ordering policy. Duplicate keys are rejected.

The assessment covers seven principal operations:

1. Search
2. Insert
3. Delete
4. Validation
5. Lowest Common Ancestor (LCA)
6. Minimum and maximum
7. Inorder successor and predecessor

Traversal, range queries, height calculation, balance assessment, structural integrity, and automated testing extend the core assessment.

## 2. BST Structure and Ordering

A node contains:

| Field | Purpose |
|---|---|
| Key | Stores the integer value |
| Left | References the left child |
| Right | References the right child |

Consider the following tree:

            50
           /  \
          30   70
         / \   / \
        20 40 60 80

The root is `50`.

The left subtree contains `30`, `20`, and `40`.

The right subtree contains `70`, `60`, and `80`.

Each subtree independently satisfies the ordering property.

### Important terminology

| Term | Meaning |
|---|---|
| Root | Topmost node |
| Parent | Node directly above another node |
| Child | Node directly below another node |
| Leaf | Node without children |
| Subtree | A node and its descendants |
| Depth | Number of edges from the root |
| Height | Maximum number of edges from a node to a leaf |
| Ancestor | A node appearing above another node |
| Descendant | A node appearing below another node |
| Inorder | Left, root, right |
| Preorder | Root, left, right |
| Postorder | Left, right, root |
| Level order | Breadth-first traversal |

The height of an empty tree is defined as `-1`. A single-node tree has height `0`.

## 3. Search

Search determines whether a particular key exists.

Starting from the root:

1. Compare the requested key with the current node.
2. If equal, return the matching node.
3. If smaller, continue into the left subtree.
4. If greater, continue into the right subtree.
5. If the traversal reaches an empty reference, the key does not exist.

For a search of `60`:

- Compare `60` with `50`.
- Move right to `70`.
- Compare `60` with `70`.
- Move left to `60`.
- Return the matching node.

Search uses the ordering property to avoid examining unrelated subtrees.

**Complexity:** O(h), where h is the tree height.

## 4. Insert

Insertion adds a new key while preserving BST ordering.

The insertion algorithm follows the same comparisons as search.

When an empty child reference is reached, a new node is attached there.

Example:

Initial tree:

        50
       /  \
      30   70

Insert `40`:

        50
       /  \
      30   70
        \
         40

The new node becomes the right child of `30`.

### Duplicate-key policy

All five implementations reject duplicates.

An insertion of `30` into a tree that already contains `30` does not change the structure or node count.

This policy simplifies ordering validation and makes successor and predecessor behavior unambiguous.

## 5. Delete

Deletion is the most structurally demanding core BST operation.

It has three distinct cases.

### Case 1: Leaf node

A leaf has no children.

Example:

        50
       /
      30
     /
    20

Delete `20`.

The parent's left reference becomes empty.

### Case 2: Node with one child

A node with one child is replaced by its existing child.

Example:

        50
       /
      30
        \
         40

Delete `30`.

Result:

        50
       /
      40

The child takes the deleted node's position.

### Case 3: Node with two children

A node with two children cannot simply be removed without reorganizing the tree.

The implementations use its inorder successor.

The inorder successor is the smallest key in the right subtree.

Example:

             50
            /  \
           30   70
               /
              60
             /
            55

Delete `50`.

The successor is `55`.

Replace the key `50` with `55`, then remove the original successor node.

The resulting tree is:

             55
            /  \
           30   70
               /
              60

The ordering property remains valid.

An inorder predecessor could also be used. It is the largest key in the left subtree.

The implementations consistently use the successor strategy.

## 6. Validation

Validation determines whether an existing tree satisfies the complete BST ordering invariant.

Checking only immediate parent-child relationships is insufficient.

Consider:

          50
         /
        30
       /  \
      20   60

The node `60` is greater than its immediate parent `30`, but it violates the upper boundary established by the root `50`.

Therefore, validation must maintain lower and upper bounds.

For a node with key `k`:

- Its lower boundary must be strictly smaller than `k`.
- Its upper boundary must be strictly greater than `k`.
- Its left subtree inherits the current upper boundary.
- Its right subtree inherits the current lower boundary.

The Python implementation uses recursive bounds.

The JavaScript, C++, and Java implementations also detect repeated node references during structural validation.

The PostgreSQL implementation checks parent-child consistency, ordering, root ownership, reachability, and stored node counts.

Validation is distinct from balance assessment. A highly unbalanced tree can still be a valid BST.

## 7. Lowest Common Ancestor

The Lowest Common Ancestor (LCA) of two nodes is their lowest shared ancestor.

Consider:

             50
            /  \
           30   70
          / \   / \
         20 40 60 80

Examples:

| Nodes | LCA |
|---|---:|
| 20 and 40 | 30 |
| 60 and 80 | 70 |
| 20 and 80 | 50 |
| 30 and 40 | 30 |

BST ordering allows LCA to be calculated without traversing the complete tree.

Starting from the root:

- If both requested keys are smaller, move left.
- If both are greater, move right.
- Otherwise, the current node is the split point and therefore the LCA.

The implementations first verify that both requested keys exist.

A missing key results in no LCA rather than an incorrect ancestor result.

**Complexity:** O(h).

## 8. Minimum and Maximum

The minimum key is the leftmost node.

The maximum key is the rightmost node.

For the example tree:

- Minimum = `20`
- Maximum = `80`

An empty tree has neither a minimum nor a maximum.

The implementations represent missing results using appropriate optional values or SQL `NULL`.

**Complexity:** O(h).

## 9. Inorder Successor and Predecessor

These operations find the next and previous keys in sorted order.

### Successor

The inorder successor of a key is the smallest existing key strictly greater than it.

For:

`20, 30, 40, 50, 60, 70, 80`

| Requested key | Successor |
|---|---:|
| 20 | 30 |
| 30 | 40 |
| 40 | 50 |
| 50 | 60 |
| 60 | 70 |
| 70 | 80 |
| 80 | NULL |

If the requested key has a right subtree, its successor is the minimum of that subtree.

Otherwise, the successor is the nearest qualifying ancestor.

The implementations use a candidate-based search, which also supports keys that are not present in the tree.

### Predecessor

The predecessor is the largest existing key strictly smaller than the requested key.

If the requested key has a left subtree, its predecessor is the maximum of that subtree.

Otherwise, it is the nearest qualifying ancestor.

A key smaller than or equal to the minimum has no predecessor.

A key greater than or equal to the maximum has no successor.

**Complexity:** O(h) for both operations.

## 10. Traversal and Range Queries

### Traversal comparison

| Traversal | Order | Main application |
|---|---|---|
| Inorder | Left, root, right | Sorted key retrieval |
| Preorder | Root, left, right | Structural serialization |
| Postorder | Left, right, root | Bottom-up processing |
| Level order | Breadth-first | Level-based inspection |

For a valid BST, inorder traversal produces strictly increasing values.

This provides an additional practical assessment check.

### Range queries

A range query retrieves all keys between two inclusive boundaries.

For example:

`rangeQuery(30, 70)`

Returns:

`30, 40, 50, 60, 70`

The Python and C++ implementations use BST-aware traversal and prune unnecessary subtrees.

The JavaScript implementation uses iterative traversal.

The Java implementation filters the sorted inorder result.

The PostgreSQL implementation uses the indexed `session_id` and `node_key` columns for range retrieval.

## 11. Height and Balance

A BST does not automatically maintain a balanced structure.

Consider inserting:

`10, 20, 30, 40, 50`

The resulting tree is right-skewed:

    10
      \
       20
         \
          30
            \
             40
               \
                50

Its height is `4`.

Its shape resembles a linked list.

### Balance assessment

The implementations use the AVL-style height-balance condition:

\[
|h_{\text{left}}-h_{\text{right}}|\leq 1
\]

This is an assessment of structural balance, not an implementation of AVL rotations.

A valid BST may fail this balance condition.

The standard BST implementations do not automatically rebalance after insertion or deletion.

## 12. Python Implementation

The Python script uses:

- `Node` dataclass for node representation.
- `BinarySearchTree` for tree operations.
- Lists for traversal and queue processing.
- Recursive lower-bound and upper-bound validation.
- Custom exceptions for invalid tree representations.
- JSON serialization and restoration.
- `unittest` for automated testing.
- Randomized operations for consistency checking.

### Serialization

The tree is represented as a nested structure containing:

- Key
- Left subtree
- Right subtree

The serialized document also contains a format version and node count.

Restoration checks ordering boundaries and verifies the stored node count.

This prevents an invalid serialized structure from being silently accepted.

### File handling

The implementation saves and restores JSON documents using UTF-8.

The restoration process validates the tree instead of trusting the input file.

The filename extension is restricted to `.json`.

## 13. JavaScript Implementation

The JavaScript implementation provides an event-driven assessment model.

### Event handling

`BinarySearchTree` extends Node.js `EventEmitter`.

Operations emit structured events containing:

- Operation name
- Requested key
- Success state
- Current node count
- Timestamp

This provides a simple foundation for monitoring tree operations.

### Asynchronous assessment

`BSTAssessmentService` uses `Promise.all()` to evaluate multiple requests.

Each request is isolated so that one invalid operation does not prevent other requests from producing results.

The service supports:

- Search
- Insert
- Delete
- Successor
- Predecessor

### Data persistence

The implementation supports JSON serialization and restoration.

It uses Node.js standard-library filesystem operations for temporary file-based testing.

The assessment uses safe integers to avoid silently accepting values outside JavaScript's exact integer range.

## 14. C++17 Implementation

The C++ program emphasizes memory ownership and explicit state management.

### Memory management

Each node uses `std::unique_ptr`.

This provides:

- Automatic ownership management.
- Automatic recursive cleanup.
- Explicit parent-child ownership.
- Reduced risk of memory leaks.

The BST disables copy operations to avoid accidental ownership duplication.

### Deletion

The deletion algorithm operates on pointers to owning `unique_ptr` references.

This allows root replacement and child replacement without manually managing raw memory ownership.

### Optional results

`std::optional<int>` represents operations that may have no result.

Examples include:

- Minimum of an empty tree.
- Maximum of an empty tree.
- Missing successor.
- Missing predecessor.
- LCA when one key does not exist.

### Assessment engine

`BSTAssessmentEngine` separates assessment-facing operations from the underlying data structure.

The program includes randomized testing against a reference `unordered_set`.

## 15. Java 17 Implementation

The Java program uses an enterprise-oriented assessment structure.

### Domain types

| Type | Responsibility |
|---|---|
| `Node` | Represents a tree node |
| `BinarySearchTree` | Maintains BST structure |
| `AssessmentPolicy` | Defines assessment conditions |
| `AssessmentService` | Evaluates the tree |
| `AssessmentReport` | Provides an immutable result |
| `OperationEvent` | Records operation information |
| `AssessmentListener` | Receives operation events |
| `ReviewStatus` | Represents assessment status |

Java records provide immutable assessment results.

The `AssessmentService` separates evaluation rules from tree operations.

### Policy evaluation

An assessment policy can require:

- Valid BST structure.
- Strictly increasing inorder traversal.
- Correct node count.

The assessment report includes:

- Number of nodes.
- Height.
- Balance status.
- Structural validity.
- Inorder traversal.
- Assessment status.
- Findings.

A tree may be structurally valid but unbalanced. The report records these properties independently.

## 16. PostgreSQL Implementation

The PostgreSQL script models a BST as a relational structure.

### Relational model

The principal entities are:

**bst_sessions**

Represents an independent assessment tree.

Important fields:

- `session_id`
- `session_name`
- `root_node_id`
- `expected_node_count`

**bst_nodes**

Represents individual tree nodes.

Important fields:

- `node_id`
- `session_id`
- `node_key`
- `parent_node_id`
- `left_child_id`
- `right_child_id`

**bst_operations**

Stores operation history.

Important fields:

- `operation_id`
- `session_id`
- `operation_type`
- `requested_key`
- `successful`
- `details`
- `executed_at`

### Integrity constraints

The database uses:

- Primary keys.
- Foreign keys.
- Composite foreign keys for same-session references.
- Unique constraints for keys within a tree.
- Self-reference restrictions.
- Check constraints.
- Indexes on session and key combinations.

The relational constraints prevent several classes of invalid references.

Full BST ordering and reachability require additional validation because ordinary foreign keys cannot enforce recursive tree invariants.

### Database functions

| Function | Responsibility |
|---|---|
| `bst_insert` | Inserts a new key |
| `bst_search` | Finds a key |
| `bst_delete` | Deletes a node |
| `bst_minimum` | Finds the minimum |
| `bst_maximum` | Finds the maximum |
| `bst_successor` | Finds the successor |
| `bst_predecessor` | Finds the predecessor |
| `bst_lca` | Calculates the LCA |
| `bst_inorder` | Retrieves inorder traversal |
| `bst_range` | Retrieves keys in a range |
| `bst_validate` | Checks structural integrity |
| `bst_height` | Calculates tree height |
| `bst_is_balanced` | Checks height balance |

### Transactions and concurrency

The insertion and deletion functions lock the corresponding session row using `FOR UPDATE`.

This serializes competing modifications to the same assessment tree when operations execute within normal PostgreSQL transactions.

The database functions do not automatically provide a complete concurrency protocol for arbitrary direct modifications to `bst_nodes`.

Production deployments should restrict direct table writes and expose controlled database functions or procedures.

### Reporting

`bst_assessment_report` combines:

- Expected node count.
- Actual node count.
- Minimum and maximum.
- Height.
- Balance.
- Structural validity.
- Inorder traversal.
- Assessment status.

The operation history provides an auditable record of successful and unsuccessful operations.

## 17. Complexity Analysis

Let:

- `n` = number of nodes.
- `h` = tree height.

| Operation | Average time | Worst-case time |
|---|---:|---:|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Validation | O(n) | O(n) |
| LCA | O(log n) | O(n) |
| Minimum | O(log n) | O(n) |
| Maximum | O(log n) | O(n) |
| Successor | O(log n) | O(n) |
| Predecessor | O(log n) | O(n) |
| Inorder traversal | O(n) | O(n) |
| Preorder traversal | O(n) | O(n) |
| Postorder traversal | O(n) | O(n) |
| Level-order traversal | O(n) | O(n) |
| Height | O(n) | O(n) |
| Balance assessment | O(n) | O(n) |

A balanced BST has height O(log n).

A skewed BST can have height O(n).

The average-case estimates assume reasonably distributed insertion orders. They are not guaranteed by an ordinary BST.

### Space complexity

| Operation | Additional space |
|---|---|
| Iterative search | O(1) |
| Iterative insertion | O(1) |
| Deletion | O(1) |
| Recursive validation | O(h) |
| Inorder traversal | O(h + n) including output |
| Level order | O(n) |
| Balance assessment | O(h) with recursive evaluation |

The PostgreSQL implementation also incurs relational storage, index maintenance, and recursive query processing costs.

## 18. Edge Cases and Failure Handling

The implementations explicitly consider:

| Condition | Expected behavior |
|---|---|
| Empty tree | Valid tree with height -1 |
| Single-node tree | Height 0 |
| Duplicate insertion | Rejected |
| Missing search key | No match |
| Missing deletion key | No modification |
| Delete root | Root is replaced appropriately |
| Delete leaf | Parent reference is cleared |
| Delete one-child node | Child takes its position |
| Delete two-child node | Successor replacement |
| Missing LCA key | No result |
| Minimum successor | Next larger key |
| Maximum successor | No result |
| Minimum predecessor | No result |
| Maximum predecessor | Previous smaller key |
| Invalid range | Error |
| Invalid serialized tree | Restoration rejected |
| Inconsistent node count | Validation failure |
| Skewed tree | Correct operations, potentially O(n) |

## 19. Testing Strategy

The implementations include deterministic and randomized tests.

### Deterministic tests

The primary example uses:

`50, 30, 70, 20, 40, 60, 80`

Tests verify:

- Successful search.
- Unsuccessful search.
- Duplicate insertion rejection.
- Minimum and maximum.
- All deletion cases.
- LCA.
- Successor and predecessor.
- Sorted inorder traversal.
- Range queries.
- Structural validation.
- Empty-tree behavior.

### Randomized testing

Randomized tests compare BST behavior against an independent reference collection.

The reference collection provides expected membership and sorted values.

After every operation, the tests compare:

- Inorder traversal.
- Node count.
- Structural validity.
- Insertion results.
- Deletion results.

This approach detects errors that may not appear in a small fixed example.

## 20. Practical Limitations and Engineering Decisions

### Ordinary BST versus balanced BST

An ordinary BST does not guarantee logarithmic height.

AVL trees and Red-Black trees introduce rotation-based balancing mechanisms.

Those mechanisms are intentionally outside this implementation's scope.

### Recursive versus iterative algorithms

Recursive algorithms are concise and naturally express subtree relationships.

Iterative algorithms reduce dependence on the programming language call stack.

The implementations use both approaches according to the operation and language.

Very deep trees can cause recursion-depth or stack-exhaustion problems. Iterative traversal and explicit resource limits are preferable for untrusted or unusually large structures.

### Integer-key restriction

The implementations use integer keys to keep ordering semantics consistent across languages.

Supporting strings or composite keys requires an explicitly defined comparison rule.

### Database representation

A relational representation requires identifiers and references between rows.

It is useful for persistent assessment records and reporting, but a relational database is not necessarily the most efficient representation for every in-memory tree workload.

The PostgreSQL implementation favors integrity, auditability, and transactional modification.

### Security and operational considerations

- Validate external keys before modifying a tree.
- Avoid trusting serialized tree structures.
- Restrict database modification privileges.
- Use transactions for multi-row structural changes.
- Serialize concurrent modifications to the same tree.
- Monitor tree height for pathological insertion sequences.
- Avoid exposing unrestricted recursive queries to untrusted workloads.
- Apply input-size and execution-time limits in production assessment services.

## 21. Execution and Assessment Workflow

| Deliverable | Runtime | Execution |
|---|---|---|
| Python | Python 3.10+ | `python bst.py` |
| JavaScript | Node.js 18+ | `node bst.js` |
| C++17 | C++17 compiler | `g++ -std=c++17 -O2 bst.cpp -o bst` |
| Java | Java 17 | `javac BSTAssessment.java` followed by `java BSTAssessment` |
| PostgreSQL | PostgreSQL 15+ | Execute the SQL script using `psql` |

The database script creates the `bst_lab` schema and its sample assessment sessions.

The Python, JavaScript, C++, and Java programs execute their built-in tests and print assessment results.

## 22. Core Assessment Checklist

- [ ] Search for existing keys.
- [ ] Search for missing keys.
- [ ] Insert into an empty tree.
- [ ] Insert into left and right subtrees.
- [ ] Reject duplicate keys.
- [ ] Delete a leaf.
- [ ] Delete a node with one child.
- [ ] Delete a node with two children.
- [ ] Delete the root.
- [ ] Validate lower and upper ordering boundaries.
- [ ] Calculate LCA for two existing keys.
- [ ] Handle missing LCA keys.
- [ ] Find minimum and maximum.
- [ ] Find successor and predecessor.
- [ ] Verify inorder traversal.
- [ ] Verify preorder and postorder traversal.
- [ ] Verify level-order traversal.
- [ ] Execute inclusive range queries.
- [ ] Calculate tree height.
- [ ] Evaluate height balance.
- [ ] Test an empty tree.
- [ ] Test a skewed tree.
- [ ] Verify node counts after modifications.
- [ ] Test randomized insertion and deletion.
- [ ] Validate serialized tree data.
- [ ] Verify transactional database modifications.
