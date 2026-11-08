# Binary Search Tree: Search and Insertion

## 1. Project Overview

This project implements a Binary Search Tree (BST) across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementation focuses on four fundamental operations:

- Search
- Insert
- Minimum
- Maximum

An unbalanced BST stores unique keys while maintaining an ordering relationship between parent and child nodes.

For a node containing key `k`:

- Every key in its left subtree is smaller than `k`.
- Every key in its right subtree is greater than `k`.
- Duplicate keys are rejected.

The implementations use an enterprise asset registry as their practical domain. Asset identifiers are stored in a searchable tree to demonstrate ordered retrieval and efficient lookup.

## 2. Binary Search Tree Structure

A BST consists of nodes containing:

| Field | Purpose |
|---|---|
| Key | Identifies the stored value |
| Left | References the left child |
| Right | References the right child |

Consider the following insertion sequence:

`50, 30, 70, 20, 40, 60, 80, 35, 45`

The resulting tree is:

             50
           /    \
         30      70
        /  \    /  \
       20  40  60  80

The structure is determined by insertion order. A different insertion sequence can produce a different tree even when the stored keys are identical.

## 3. Search Operation

Search determines whether a specified key exists.

The algorithm begins at the root and compares the target with the current node.

| Condition                 | Action         |
| ------------------------- | -------------- |
| Target equals current key | Return success |
| Target is smaller         | Move left      |
| Target is greater         | Move right     |
| Current node is null      | Return failure |

For example, searching for `45` follows this path:

`50 → 30 → 40 → 45`

Searching for `100` eventually reaches a null child and returns false.

The search algorithm does not need to inspect every node when the tree is reasonably balanced.

## 4. Insert Operation

Insertion places a new key in its correct position while preserving the BST ordering property.

The process is:

1. Validate the incoming key.
2. Create a candidate node.
3. Compare the key with the root.
4. Follow the appropriate child.
5. Continue until an empty child position is found.
6. Attach the new node.
7. Update the node count.

Duplicate keys are rejected rather than creating multiple nodes with identical values.

For example, inserting `35` into the sample tree follows:

`50 → 30 → 40 → 35`

The new node becomes the left child of `40`.

Insertion does not automatically rebalance an ordinary BST. This distinction is important when evaluating its performance.

## 5. Minimum Operation

The minimum operation returns the smallest key.

The smallest key must be located along the leftmost path.

Algorithm:

1. Start at the root.
2. Follow left-child references.
3. Stop when the current node has no left child.
4. Return its key.

For the example tree, the minimum is `20`.

For an empty tree, the operation returns `None`, `null`, `std::nullopt`, or an empty optional value, depending on the implementation.

## 6. Maximum Operation

The maximum operation follows the opposite path.

Algorithm:

1. Start at the root.
2. Follow right-child references.
3. Stop when the current node has no right child.
4. Return its key.

For the example tree, the maximum is `80`.

An empty tree has no maximum value.

## 7. Complexity Analysis

Let:

- `n` represent the number of nodes.
- `h` represent the height of the tree.

The height determines how many nodes an operation may need to inspect.

| Operation             | Average case | Worst case |
| --------------------- | ------------ | ---------- |
| Search                | O(log n)     | O(n)       |
| Insert                | O(log n)     | O(n)       |
| Minimum               | O(log n)     | O(n)       |
| Maximum               | O(log n)     | O(n)       |
| Inorder traversal     | O(n)         | O(n)       |
| Structural validation | O(n)         | O(n)       |

### Average-case behavior

With reasonably distributed insertion orders, the tree tends to have a height proportional to `log n`.

Search, insertion, minimum, and maximum therefore require approximately logarithmic work.

### Worst-case behavior

Consider sorted insertion:

`10, 20, 30, 40, 50`

The resulting structure is:

```
10
  \
   20
     \
      30
        \
         40
           \
            50
```

This structure behaves like a linked list.

Its height is `n - 1`, so searching for the final key requires `n` comparisons.

The same degradation affects insertion, minimum, and maximum depending on the direction of the chain.

### Space complexity

| Operation or structure           | Space          |
| -------------------------------- | -------------- |
| BST storage                      | O(n)           |
| Search                           | O(1) auxiliary |
| Insert                           | O(1) auxiliary |
| Minimum                          | O(1) auxiliary |
| Maximum                          | O(1) auxiliary |
| Inorder traversal                | O(h) auxiliary |
| Breadth-first height calculation | O(n) auxiliary |
| Validation                       | O(h) auxiliary |

The iterative implementations avoid recursive call-stack growth when a tree becomes highly skewed.

## 8. Balancing and Performance

A normal BST does not enforce a maximum height.

A balanced construction can improve lookup behavior by choosing middle values before recursively processing smaller and larger ranges.

For sorted values, median-first insertion produces a relatively balanced structure.

The Python, JavaScript, C++17, and Java 17 implementations compare:

- Median-first insertion
- Sorted insertion
- Tree height
- Search comparisons
- Measured execution time

Comparison counts provide a direct measurement of algorithmic work. Execution time is affected by hardware, runtime optimization, memory allocation, and system load.

The median-first construction is useful for demonstrating balanced insertion order. It does not make the underlying BST self-balancing.

AVL trees and Red-Black trees provide additional structural rules to maintain logarithmic height after arbitrary insertions.

## 9. Python Implementation

The Python implementation uses:

- `Node` dataclass for node representation.
- `BinarySearchTree` class for state management.
- Iterative search and insertion.
- Optional node references.
- Lists as traversal stacks and queues.
- Assertions for correctness checks.
- JSON export for reporting.
- `time.perf_counter()` for performance measurement.

The implementation rejects Boolean values as keys because Python treats Boolean values as a subclass of integers.

The `validate()` method checks lower and upper key boundaries throughout the tree and verifies that the number of visited nodes matches the recorded size.

The report contains the sorted keys, node count, height, minimum, and maximum.

## 10. JavaScript Implementation

The JavaScript implementation uses Node.js capabilities.

Important design elements include:

- `BSTNode` class for node representation.
- `BinarySearchTree` extending `EventEmitter`.
- Safe-integer validation.
- Event-based operation notifications.
- Iterative traversal.
- Promise-based JSON file export.
- `performance.now()` for timing.

Events distinguish successful insertion, duplicate insertion, and search outcomes.

The implementation uses `Number.isSafeInteger()` because JavaScript numbers cannot exactly represent every integer beyond the safe-integer range.

Asynchronous report export prevents file operations from being treated as synchronous application logic.

## 11. C++17 Implementation

The C++ implementation uses:

- `unique_ptr` for node ownership.
- `optional` for empty-tree results.
- STL vectors for traversal and benchmarking.
- Exception handling for file and application failures.
- `chrono` for performance measurement.
- Explicit deletion of copy operations.

`unique_ptr` ensures that each node has a single owning parent reference.

When the tree is destroyed, its owned nodes are released automatically.

The implementation uses iterative algorithms to avoid recursive traversal depth problems.

The report writer validates the output extension and checks file-writing errors.

## 12. Java 17 Implementation

The Java implementation models an enterprise asset registry.

Its principal components are:

| Component              | Responsibility                |
| ---------------------- | ----------------------------- |
| `Asset`                | Immutable asset record        |
| `Node`                 | BST node representation       |
| `SearchableTree`       | Tree operation contract       |
| `BinarySearchTree`     | Tree implementation           |
| `AssetRegistryService` | Asset registration and lookup |
| `OperationResult`      | Immutable operation result    |
| `OperationType`        | Operation classification      |

Java records provide concise immutable domain objects.

The registry service separates asset registration from tree indexing.

Duplicate asset identifiers are rejected before an asset is added to the registry.

The implementation returns `OptionalInt` for minimum and maximum operations and uses immutable list results for ordered traversal.

The tree is not thread-safe. A production application requiring concurrent modifications would need synchronization or a different indexing strategy.

## 13. PostgreSQL Implementation

The SQL implementation represents a BST using relational tables.

### Data model

| Table               | Purpose                                 |
| ------------------- | --------------------------------------- |
| `asset`             | Stores enterprise asset information     |
| `bst_tree`          | Stores tree metadata and root reference |
| `bst_node`          | Stores node relationships               |
| `bst_operation_log` | Records operation outcomes              |

### Node relationships

Each node stores:

- Its asset identifier.
- Its parent node identifier.
- Its left child identifier.
- Its right child identifier.
- Its associated tree identifier.

Composite foreign keys restrict parent and child references to the same tree.

Unique constraints prevent duplicate asset keys within one tree.

Check constraints reject self-referencing relationships and identical left and right children.

### Insertion function

`bst_insert()` implements iterative BST insertion using PL/pgSQL.

The tree row is locked using `FOR UPDATE` before insertion.

This serializes concurrent insertions into the same tree and prevents competing transactions from attaching nodes to stale parent positions.

A duplicate key returns false without creating another node.

### Search function

`bst_search()` begins at the root and follows left or right references according to key comparisons.

The function records the comparison count and operation outcome.

### Minimum and maximum functions

`bst_minimum()` follows left-child references.

`bst_maximum()` follows right-child references.

Both functions return `NULL` when the tree is empty.

### Inorder traversal

`bst_inorder()` uses a recursive CTE to traverse the stored node relationships and return the asset identifiers in ascending order.

### Integrity validation

`bst_validate()` checks:

- Recorded node count.
- Actual node count.
- Root existence.
- Root parent relationship.
- Reachability of nodes from the root.

Foreign keys and uniqueness constraints enforce important relational integrity conditions.

The validation function does not independently prove every BST ordering boundary. A complete production integrity audit should also verify each node against all of its ancestor boundaries and detect cycles explicitly.

### Operation reporting

The `bst_operation_log` table records:

- Operation type.
- Requested key.
- Success or failure.
- Comparison count.
- Execution timestamp.

Aggregation queries calculate average comparisons, maximum comparisons, and success counts by operation type.

The reporting view provides tree metadata, minimum, maximum, and structural validation status.

## 14. Important Edge Cases

| Case                      | Expected behavior                 |
| ------------------------- | --------------------------------- |
| Empty tree                | Search returns false              |
| Empty tree minimum        | No value                          |
| Empty tree maximum        | No value                          |
| Single-node tree          | Minimum and maximum are identical |
| Duplicate insertion       | Rejected                          |
| Missing key               | Search returns false              |
| Sorted insertion          | May produce a skewed tree         |
| Invalid key type          | Rejected                          |
| Invalid report filename   | Export rejected                   |
| File-writing failure      | Error reported                    |
| Invalid node relationship | Integrity validation fails        |

The implementations use unique keys to keep the ordering rules unambiguous.

A production system must also consider memory limits, concurrent writes, persistent storage, and recovery after process failure.

## 15. Security and Production Considerations

A BST is a data structure, not a complete security mechanism.

For production use:

- Validate external keys before insertion.
- Apply database permissions to tree-management functions.
- Use parameterized SQL instead of dynamically constructed SQL statements.
- Restrict direct modifications to node relationships.
- Preserve transaction boundaries during insertion.
- Audit important changes.
- Protect exported reports with appropriate filesystem permissions.
- Consider resource limits when accepting large or adversarial insertion sequences.

An attacker who controls insertion order can deliberately create a highly skewed tree, increasing operation costs from logarithmic to linear.

A self-balancing tree or database-native indexed structure may be more appropriate for unpredictable production workloads.

## 16. Execution

| File       | Execution                                                                       |
| ---------- | ------------------------------------------------------------------------------- |
| Python     | `python bst.py`                                                                 |
| JavaScript | `node bst.js`                                                                   |
| C++17      | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic bst.cpp -o bst` followed by `./bst` |
| Java 17    | `javac Main.java` followed by `java Main`                                       |
| PostgreSQL | Execute `bst.sql` using `psql`                                                  |

The Python, JavaScript, C++17, and Java 17 programs create a JSON report named `bst_report.json`.

The PostgreSQL implementation creates its schema, tables, indexes, functions, views, sample records, and operation history within a transaction.

## 17. Implementation Comparison

| Feature             | Python            | JavaScript         | C++17            | Java 17            | PostgreSQL                         |
| ------------------- | ----------------- | ------------------ | ---------------- | ------------------ | ---------------------------------- |
| Node representation | Dataclass         | Class              | Struct           | Generic class      | Relational row                     |
| Ownership           | Python references | Garbage collection | `unique_ptr`     | Garbage collection | Database-managed                   |
| Search              | Iterative         | Iterative          | Iterative        | Iterative          | PL/pgSQL                           |
| Insert              | Iterative         | Iterative          | Iterative        | Iterative          | PL/pgSQL                           |
| Minimum             | Iterative         | Iterative          | Iterative        | Iterative          | SQL function                       |
| Maximum             | Iterative         | Iterative          | Iterative        | Iterative          | SQL function                       |
| Validation          | Bounds and count  | Bounds and count   | Bounds and count | Bounds and count   | Relational checks and reachability |
| Reporting           | JSON              | JSON               | JSON             | JSON               | SQL view and logs                  |

## 18. Key Terminology

| Term              | Meaning                                             |
| ----------------- | --------------------------------------------------- |
| Root              | First node of the tree                              |
| Parent            | Node directly above another node                    |
| Child             | Node directly below another node                    |
| Leaf              | Node without children                               |
| Subtree           | A node and all its descendants                      |
| Height            | Maximum number of edges from root to a leaf         |
| Depth             | Number of edges from root to a node                 |
| Search path       | Sequence of nodes inspected during lookup           |
| Skewed tree       | Tree with nodes concentrated on one side            |
| Balanced tree     | Tree with controlled differences in subtree heights |
| Inorder traversal | Left subtree, root, right subtree                   |
| Duplicate key     | A key already present in the tree                   |

## 19. Practical Applications

BSTs demonstrate ordered indexing in applications such as:

- Asset identifier lookup.
- In-memory inventory indexes.
- Ordered record management.
- Educational database indexing models.
- Range-oriented data structures.
- Search and retrieval systems.

The central engineering consideration is the relationship between insertion order, tree height, and operation cost.

A basic BST provides efficient average-case operations when its structure remains reasonably balanced. It provides no worst-case logarithmic guarantee without an additional balancing mechanism.
           / \
          35 45
