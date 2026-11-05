# Balanced Trees

## 1. Introduction

A balanced tree is a tree data structure designed to control its height so that operations such as searching, insertion, and deletion remain efficient.

A binary search tree (BST) maintains the ordering property:

- Values smaller than a node belong in its left subtree.
- Values greater than a node belong in its right subtree.
- Duplicate keys are rejected in the implementations in this project.

A balanced binary search tree additionally maintains a height constraint that prevents one subtree from becoming substantially deeper than the other.

The main implementation is an AVL tree, which automatically restores height balance following insertion and deletion.

## 2. Fundamental Terminology

| Term | Meaning |
|---|---|
| Node | An individual element in the tree |
| Root | The topmost node |
| Parent | A node directly above another node |
| Child | A node directly below another node |
| Leaf | A node without children |
| Subtree | A node and all its descendants |
| Height | Number of edges on the longest downward path, or number of nodes on that path, depending on convention |
| Balance factor | Difference between the left and right subtree heights |
| Rotation | A restructuring operation that restores balance |
| Depth | Distance from the root to a node |
| Skewed tree | A tree that behaves like a linked list |

### Height convention

The implementations use the following convention:

- Empty tree: height 0.
- Leaf node: height 1.
- Other nodes: one plus the maximum height of their children.

Mathematically:

\[
H(T)=1+\max(H(T_L),H(T_R))
\]

For an empty tree:

\[
H(\varnothing)=0
\]

This convention makes height calculations consistent across all implementations.

## 3. Height Balance

Height balance describes the relationship between the heights of a node's left and right subtrees.

For an AVL tree, the balance factor is:

\[
BF(v)=H(v_L)-H(v_R)
\]

The AVL balance condition is:

\[
|BF(v)|\leq 1
\]

The condition must hold at every node, not merely at the root.

### Balance factor interpretation

| Balance factor | Interpretation |
|---:|---|
| -2 or smaller | Right-heavy violation |
| -1 | Slightly right-heavy |
| 0 | Equal subtree heights |
| +1 | Slightly left-heavy |
| +2 or greater | Left-heavy violation |

A tree is AVL-balanced only when every node satisfies the permitted balance-factor range.

A root with equally sized subtrees does not guarantee that every descendant is balanced.

## 4. Balanced and Unbalanced Trees

<text> </text>

### Balanced tree

A balanced tree distributes nodes across its subtrees to avoid excessive depth.

Example:

                40
           /        \
         20          60
        /  \        /  \
      10   30     50    70

The height is 3 under the node-count convention.

Searching can eliminate approximately half of the remaining search space at each level.

### Unbalanced tree

An ordinary BST can become skewed when keys arrive in sorted order.

Example:

    10
      \
       20
         \
          30
            \
             40
               \
                50

This structure behaves like a linked list.

Searching for the final element requires examining every preceding node.

The tree has height \(n\), where \(n\) is the number of nodes.

## 5. Why Unbalanced Trees Degrade Performance

The efficiency of a BST depends on its height.

A balanced tree generally has logarithmic height, whereas an ordinary BST can have linear height.

| Operation | Balanced AVL tree | Ordinary BST |
|---|---:|---:|
| Search | O(log n) | Average O(log n), worst O(n) |
| Insertion | O(log n) | Average O(log n), worst O(n) |
| Deletion | O(log n) | Average O(log n), worst O(n) |
| Minimum | O(log n) | O(h) |
| Maximum | O(log n) | O(h) |
| Traversal | O(n) | O(n) |
| Storage | O(n) | O(n) |

Here, \(h\) represents the actual tree height.

### Example

Consider 1,000 nodes.

A reasonably balanced tree requires approximately 10 levels.

A completely skewed tree can require 1,000 levels.

The difference affects:

- Number of comparisons.
- Search latency.
- Insertion and deletion costs.
- Recursive call-stack depth.
- Application throughput.
- Predictability of execution time.

An ordinary BST does not automatically reorganize itself after insertion.

AVL trees actively maintain their height constraints.

## 6. AVL Tree Rotations

AVL trees restore balance through four rotation cases.

### 6.1 Left-Left case

Occurs when a node becomes unbalanced because of insertion into the left subtree of its left child.

Correction: Right rotation.

    Before:             After:

          30               20
         /                /  \
        20               10   30
       /
      10

### 6.2 Right-Right case

Occurs when insertion takes place in the right subtree of the right child.

Correction: Left rotation.

    Before:             After:

      10                  20
        \                /  \
         20             10   30
           \
            30

### 6.3 Left-Right case

Occurs when insertion takes place in the right subtree of the left child.

Correction:

1. Left rotation on the left child.
2. Right rotation on the unbalanced node.

    Before:             After:

          30               20
         /                /  \
        10               10   30
          \
           20

### 6.4 Right-Left case

Occurs when insertion takes place in the left subtree of the right child.

Correction:

1. Right rotation on the right child.
2. Left rotation on the unbalanced node.

    Before:             After:

       10                  20
         \                /  \
          30             10   30
         /
        20

Rotations preserve BST ordering while changing the shape of the tree.

## 7. Balance Checking

A balance checker determines whether the height constraint holds throughout the tree.

A correct checker must:

1. Examine the left subtree.
2. Examine the right subtree.
3. Calculate their actual heights.
4. Compare the height difference.
5. Verify the balance condition.
6. Validate the BST ordering property when required.

The recursive height calculation is:

\[
H(v)=1+\max(H(v_L),H(v_R))
\]

The balance condition is:

\[
|H(v_L)-H(v_R)|\leq 1
\]

The Python and Java implementations validate both stored heights and structural ordering.

The C++ implementation uses recursive inspection to calculate height, node count, and balance status.

The JavaScript implementation exposes an inspection method that checks stored heights and BST ordering.

The PostgreSQL implementation uses recursive CTEs to calculate subtree heights and report node-level balance factors.

### Complexity of balance checking

A straightforward recursive checker visits every node once.

- Time complexity: O(n).
- Auxiliary space: O(h).

For a balanced tree, the recursive stack is O(log n).

For a highly skewed tree, it can reach O(n).

The checker is useful for testing and auditing, but it should not be confused with the balancing mechanism itself.

## 8. AVL Insertion Workflow

The insertion process follows these stages:

    Validate key
         |
         v
    Locate insertion position
         |
         v
    Insert new leaf
         |
         v
    Update ancestor heights
         |
         v
    Calculate balance factors
         |
         v
    Detect imbalance
         |
         v
    Apply appropriate rotation
         |
         v
    Verify tree invariants

Insertion maintains two separate properties:

- BST ordering.
- AVL height balance.

A rotation is required only when an ancestor becomes unbalanced.

Duplicate keys are ignored in the Python, JavaScript, C++, and Java implementations.

## 9. AVL Deletion Workflow

Deletion is more involved because removing a node can reduce the height of a subtree.

The deletion process handles three cases:

| Case | Action |
|---|---|
| Leaf node | Remove the node |
| One child | Replace the node with its child |
| Two children | Replace its key with its inorder successor and remove the successor |

After deletion, the algorithm updates ancestor heights and checks balance factors.

Unlike insertion, deletion may require rebalancing at multiple ancestors.

The implementation handles the LL, LR, RR, and RL rotation cases through the common rebalancing procedure.

## 10. Python Implementation

**File:** `balanced_trees.py`

The Python implementation provides two tree structures.

### AVLTree

Responsibilities:

- Insertion.
- Search.
- Deletion.
- Inorder traversal.
- Height calculation.
- Balance-factor calculation.
- Four rotation cases.
- Structural validation.

The `Node` dataclass stores the key, child references, and cached height.

The `validate()` method checks:

- BST ordering.
- Correct stored heights.
- AVL balance at every node.
- Consistency between node count and tree size.

### BinarySearchTree

This implementation deliberately does not perform rotations.

It demonstrates how sorted input creates a skewed tree.

The `search_with_comparisons()` method measures the number of comparisons required for a lookup.

### Testing

The script tests:

- Empty trees.
- Single-node trees.
- Duplicate insertion.
- Successful deletion.
- Sorted insertion.
- Search operations.
- Invalid key types.
- Height and balance invariants.

The implementation uses only the Python standard library.

## 11. JavaScript Implementation

**File:** `balanced-trees.js`

The JavaScript implementation uses an event-driven design.

### AVLTree

The class extends Node.js `EventEmitter`.

It emits:

| Event | Trigger |
|---|---|
| `insert` | A new key is successfully inserted |
| `delete` | An existing key is deleted |

Each successful modification increments the tree version.

This allows an application to observe changes without coupling event consumers to the internal rotation logic.

The implementation also provides:

- Safe integer validation.
- Search comparison counts.
- Iterative inorder traversal.
- Recursive structural inspection.
- Insertion and deletion.
- Asynchronous insertion processing through Promises.

### UnbalancedBST

The second implementation provides an ordinary BST without automatic balancing.

Its height calculation uses an explicit stack, avoiding recursive traversal for the demonstration.

The comparison highlights how identical insertion-order problems affect an unbalanced tree.

### Engineering considerations

JavaScript numbers cannot represent every possible integer exactly.

The implementation therefore uses `Number.isSafeInteger()` to reject unsafe numeric keys.

The tree is designed for single-threaded execution. Event emission does not provide thread synchronization or transactional isolation.

## 12. C++17 Implementation

**File:** `balanced_trees.cpp`

The C++ implementation emphasizes explicit memory ownership and modular tree operations.

### Memory management

Each node uses:

- `unique_ptr<Node>` for the left child.
- `unique_ptr<Node>` for the right child.

This ensures that child ownership is managed automatically.

Rotations transfer ownership using move semantics.

The implementation avoids raw owning pointers and manual memory deallocation.

### Main components

| Component | Responsibility |
|---|---|
| `Node` | Stores the key, height, and children |
| `TreeMetrics` | Represents validation results |
| `AVLTree` | Implements automatic balancing |
| `UnbalancedBST` | Demonstrates performance degradation |
| `rotateLeft()` | Corrects right-heavy imbalance |
| `rotateRight()` | Corrects left-heavy imbalance |
| `rebalance()` | Handles all four rotation cases |
| `validate()` | Checks structural and height invariants |

### Design decisions

The implementation uses recursive insertion and deletion because AVL height remains logarithmic.

The validation procedure independently recalculates heights rather than trusting cached values.

This detects incorrect height updates and structural corruption.

Compilation requires a C++17-compatible compiler.

## 13. Java 17 Implementation

**File:** `Main.java`

The Java implementation models a repository indexing service.

Repository identifiers are stored in an AVL tree to provide predictable lookup performance.

### Enterprise domain components

| Component | Responsibility |
|---|---|
| `RepositoryIndexService` | Provides repository registration and lookup |
| `AVLTree` | Maintains the balanced index |
| `RepositoryIndex` | Demonstrates an ordinary unbalanced index |
| `TreeAudit` | Associates a tree version with its metrics |
| `TreeMetrics` | Stores height, node count, and validation status |
| `SearchResult` | Stores lookup outcome and comparison count |
| `OperationStatus` | Represents operation outcomes |
| `TreeValidationException` | Represents validation failures |

### Repository indexing workflow

    Repository registration
             |
             v
    Validate repository ID
             |
             v
    Check duplicate identifier
             |
             v
    Insert into AVL index
             |
             v
    Rebalance affected ancestors
             |
             v
    Update version
             |
             v
    Audit tree invariants

The service rejects non-positive repository identifiers and duplicate registrations.

Java records provide immutable metric and result objects.

The implementation uses standard Java collections and no third-party libraries.

The service is a demonstration of domain separation. It is not a concurrent repository database or a persistent storage implementation.

## 14. PostgreSQL Implementation

**File:** `balanced_trees.sql`

The PostgreSQL implementation represents trees through relational tables.

### Relational model

#### tree_registry

Stores metadata about individual trees.

Important fields:

- `tree_id`: Primary key.
- `tree_name`: Unique tree name.
- `tree_type`: Balanced or unbalanced classification.
- `description`: Tree description.
- `created_at`: Creation timestamp.

#### tree_nodes

Stores individual nodes.

Important fields:

- `node_id`: Primary key.
- `tree_id`: Foreign key to the tree registry.
- `node_key`: Integer key.
- `parent_node_id`: Self-referencing parent relationship.

The unique constraint on `(tree_id, node_key)` prevents duplicate keys within a tree.

The parent reference allows the table to represent a hierarchical structure.

### Database integrity controls

The implementation includes:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Performance-oriented indexes.
- Triggers for parent-child validation.
- Cycle prevention.
- Recursive CTEs.
- SQL functions.
- A reporting view.
- Transaction handling.

The child-limit trigger prevents a parent from having more than two direct children.

The cycle-prevention trigger rejects parent assignments that would introduce an ancestor cycle.

### Recursive height calculation

The `calculate_tree_height()` function uses a recursive CTE.

It starts with root nodes at depth one and recursively visits their descendants.

The maximum depth becomes the tree height.

The empty tree returns zero.

### Node-level balance inspection

The `inspect_tree()` function calculates:

- Subtree height.
- Left subtree height.
- Right subtree height.
- Balance factor.
- Local balance status.

This separates individual node measurements from the overall tree report.

### Reporting

The `tree_health_report` view combines tree metadata, node counts, height, and balance status.

The script also demonstrates:

- Tree retrieval.
- Node-level validation.
- Aggregation by tree type.
- BST insertion.
- Duplicate-key failure handling.
- Invalid-parent handling.
- Performance comparison.

### Database limitation

The SQL model represents binary tree relationships and checks structural integrity, but it does not automatically rebalance the tree after insertion or deletion.

The `insert_node()` function performs ordinary BST insertion.

The balanced sample is constructed with a suitable insertion arrangement.

A production database requiring guaranteed AVL or other self-balancing behavior would need additional rotation and transactional maintenance logic.

The balance report evaluates current structure rather than enforcing AVL balance during every modification.

## 15. Important Distinctions

| Concept | Meaning |
|---|---|
| BST | Maintains key ordering |
| Balanced BST | Maintains a height constraint |
| AVL tree | Maintains a strict height difference of at most one |
| Height-balanced tree | A tree satisfying a specified subtree-height condition |
| Complete binary tree | All levels are filled except possibly the last, which is filled from left to right |
| Full binary tree | Every node has either zero or two children |
| Perfect binary tree | Every internal node has two children and all leaves have equal depth |

These properties are not interchangeable.

A complete tree is not necessarily an AVL tree under every possible structure, and a height-balanced tree is not necessarily complete.

## 16. Performance and Engineering Trade-offs

Balancing improves the worst-case performance of dynamic search operations, but it introduces maintenance overhead.

### AVL tree advantages

- Guaranteed logarithmic search.
- Guaranteed logarithmic insertion.
- Guaranteed logarithmic deletion.
- Predictable tree height.
- Effective for lookup-intensive workloads.

### AVL tree trade-offs

- Additional height metadata.
- Rotation operations.
- More complicated deletion.
- Extra maintenance during modifications.
- More implementation complexity than an ordinary BST.

### Ordinary BST advantages

- Simple implementation.
- No balancing rotations.
- Lower maintenance overhead.
- Suitable for small or controlled datasets.

### Ordinary BST limitations

- Input order affects its structure.
- Sorted insertion can produce linear height.
- Search performance can degrade to O(n).
- Recursive operations can encounter stack-depth problems.

## 17. Security and Reliability Considerations

Tree implementations used in production systems should consider:

- Validate incoming keys before modifying the tree.
- Reject duplicate identifiers when uniqueness is required.
- Protect structural invariants during updates.
- Avoid trusting externally supplied height metadata.
- Detect cycles and invalid parent references.
- Use transactions for multi-step database changes.
- Apply appropriate access controls to database modification functions.
- Avoid unbounded recursive processing on untrusted tree structures.
- Consider concurrency control when multiple processes modify the same tree.
- Monitor tree height and operation latency.

A balanced tree reduces pathological depth, but it does not eliminate every resource-exhaustion or concurrency risk.

## 18. Practical Applications

Balanced search trees are useful in systems that need predictable ordered access.

Examples include:

- In-memory indexes.
- Ordered key-value collections.
- Repository metadata indexing.
- Scheduling systems.
- Dynamic lookup structures.
- Range-query implementations.
- Database index structures.
- Memory-resident configuration registries.

Different balanced tree families have different operational characteristics.

AVL trees maintain strict height balance.

Red-black trees use color-based invariants to provide logarithmic height with different rotation and recoloring trade-offs.

B-trees and B+ trees are designed for storage systems that operate on blocks or pages and reduce disk or page-access operations.

The appropriate structure depends on the workload, storage model, update frequency, and lookup requirements.

## 19. Final Technical Reference

| Implementation | Main emphasis | Balance checking | Automatic balancing |
|---|---|---|---|
| Python | AVL operations and performance comparison | Yes | Yes |
| JavaScript | Event-driven tree updates | Yes | Yes |
| C++17 | Ownership and rotation mechanics | Yes | Yes |
| Java 17 | Enterprise repository indexing | Yes | Yes |
| PostgreSQL | Relational tree storage and reporting | Yes | No |

The central invariant studied throughout these implementations is:

\[
\boxed{|H(v_L)-H(v_R)|\leq 1}
\]

For AVL trees, maintaining this invariant at every node ensures that the tree height remains logarithmic in the number of stored nodes.
