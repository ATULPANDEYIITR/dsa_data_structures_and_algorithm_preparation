# BST Fundamentals

## Project Overview

This project implements Binary Search Tree (BST) fundamentals through five independent implementations:

| File | Implementation | Primary engineering focus |
|---|---|---|
| `bst_fundamentals.py` | Python | BST operations, validation and balancing |
| `bst_fundamentals.js` | JavaScript | Event-driven product catalog |
| `bst_fundamentals.cpp` | C++17 | Inventory indexing and memory ownership |
| `Main.java` | Java 17 | Enterprise product catalog and service layer |
| `bst_fundamentals.sql` | PostgreSQL | Relational representation and recursive queries |

The implementations cover insertion, searching, deletion, tree traversal, minimum and maximum values, height calculation, validation, and balanced-tree construction.

## 1. Binary Search Tree Structure

A Binary Search Tree is a hierarchical data structure in which each node contains a key and references to its left and right children.

For a node with key `K`:

- Every key in its left subtree is smaller than `K`.
- Every key in its right subtree is greater than `K`.
- Both subtrees must independently satisfy the BST property.

The implementations use unique integer keys. Duplicate keys are rejected rather than inserted as separate nodes.

### Example structure

The sample tree is constructed using the insertion sequence:

`50, 30, 70, 20, 40, 60, 80`

Its structure is:

                    50
                   /  \
                 30    70
                / \    / \
               20 40  60 80

The root is `50`. Its left subtree contains smaller keys, and its right subtree contains larger keys.

### Important terminology

| Term | Meaning |
|---|---|
| Node | An individual element containing a key and child references |
| Root | The first node of the tree |
| Parent | A node directly above another node |
| Child | A node directly connected below another node |
| Leaf | A node without children |
| Subtree | A node and all its descendants |
| Depth | Number of edges from the root to a node |
| Height | Number of edges on the longest downward path |
| Successor | The next larger key in inorder ordering |
| Predecessor | The next smaller key in inorder ordering |

The implementations define the height of an empty tree as `-1` and the height of a single-node tree as `0`.

## 2. Core BST Operations

### Insertion

Insertion adds a new node while preserving the ordering invariant.

The algorithm begins at the root:

1. Compare the new key with the current node.
2. Move left when the new key is smaller.
3. Move right when the new key is larger.
4. Insert at the first available child position.
5. Reject the operation when an equal key already exists.

For example, inserting `35` into the sample tree follows:

`50 → 30 → 40 → 35`

The new node becomes the left child of `40`.

Insertion takes `O(h)` time, where `h` is the current tree height.

### Searching

Searching uses the same ordering property.

A search for `60` follows:

`50 → 70 → 60`

There is no need to examine unrelated subtrees.

The search returns whether the key exists in Python, a product record or `null` in JavaScript, a node pointer in C++, and an `Optional<Product>` in Java.

### Deletion

Deletion has three distinct cases.

| Case | Structure | Operation |
|---|---|---|
| Leaf | No children | Remove the node |
| One child | One existing child | Replace the node with its child |
| Two children | Both children exist | Replace the node with its inorder successor and remove the successor |

The inorder successor is the smallest key in the right subtree.

For example, deleting `50` from the sample tree uses `60` as its successor.

The successor replacement maintains the BST ordering property.

Deletion takes `O(h)` time, excluding any additional traversal required by a particular implementation.

### Minimum and maximum

The minimum is found by repeatedly following left-child references.

The maximum is found by repeatedly following right-child references.

For the sample tree:

- Minimum: `20`
- Maximum: `80`

Both operations take `O(h)` time.

## 3. Tree Traversals

Traversal determines the order in which nodes are visited.

### Inorder traversal

Order:

`Left → Root → Right`

For a valid BST, inorder traversal produces ascending key order.

Sample result:

`20, 30, 40, 50, 60, 70, 80`

This property makes inorder traversal useful for sorted retrieval, validation, and conversion into a balanced BST.

### Preorder traversal

Order:

`Root → Left → Right`

Sample result:

`50, 30, 20, 40, 70, 60, 80`

Preorder traversal is useful when recording or reconstructing tree structure.

### Postorder traversal

Order:

`Left → Right → Root`

Sample result:

`20, 40, 30, 60, 80, 70, 50`

Postorder traversal processes children before their parent. It is useful when releasing tree resources or processing hierarchical dependencies.

### Level-order traversal

Level-order traversal visits nodes breadth-first.

Sample result:

`50`

`30, 70`

`20, 40, 60, 80`

It uses a queue and requires `O(n)` time and `O(w)` auxiliary space, where `w` is the maximum tree width.

## 4. Height, Depth and Order Statistics

### Height

Height measures the longest path from a node to a leaf.

For the sample tree, the height is `2`.

A tree with a long one-sided chain has a much greater height than a balanced tree containing the same number of nodes.

### Depth

Depth measures the distance from the root.

The root has depth `0`.

For the sample tree:

| Node | Depth |
|---|---:|
| 50 | 0 |
| 30 | 1 |
| 70 | 1 |
| 20 | 2 |
| 40 | 2 |

### Kth-smallest element

The kth-smallest operation uses inorder traversal.

Because inorder traversal returns sorted keys, the kth visited node is the kth-smallest element.

For the sample tree:

| Position | Value |
|---|---:|
| 1st | 20 |
| 2nd | 30 |
| 3rd | 40 |
| 4th | 50 |
| 5th | 60 |

The implementations reject invalid positions rather than returning an arbitrary value.

The iterative implementation requires `O(h + k)` time and `O(h)` auxiliary space.

## 5. Balanced Binary Search Trees

A BST can become inefficient when inserted keys arrive in sorted order.

Consider:

`10, 20, 30, 40, 50`

The resulting structure is:

    10
      \
       20
         \
          30
            \
             40
               \
                50

This tree behaves like a linked list.

Searching for a key near the bottom can require examining almost every node.

A balanced BST distributes nodes more evenly between the left and right subtrees.

### Balancing procedure

The implementations construct a balanced copy using these steps:

1. Obtain sorted values using inorder traversal.
2. Select the middle value as the root.
3. Recursively construct the left subtree from the lower half.
4. Recursively construct the right subtree from the upper half.

For five sorted keys, the resulting structure is:

             30
            /  \
          20    50
         /      /
        10     40

The resulting height is approximately `O(log n)`.

This is a rebuilding operation, not an automatic balancing algorithm. Unlike AVL and Red-Black trees, an ordinary BST does not automatically rebalance itself after insertion or deletion.

## 6. Implementation Design

### Python

The Python implementation uses a `Node` dataclass and a `BinarySearchTree` class.

Its main characteristics are:

- Type validation for integer keys.
- Iterative insertion and searching.
- Recursive deletion and traversal.
- Iterative level-order traversal.
- Inorder-based kth-smallest retrieval.
- Recursive ordering validation using lower and upper bounds.
- Balanced-tree construction.
- Assertions covering insertion, searching, deletion and tree integrity.

The lower and upper bounds are important because checking only direct parent-child relationships is insufficient to establish global BST validity.

### JavaScript

The JavaScript implementation uses private class fields to protect the internal root and size.

Its engineering characteristics include:

- `EventEmitter` notifications for insertion and deletion.
- `Map`-independent tree nodes with explicit references.
- Iterative traversals to reduce recursive call-stack usage.
- Safe integer validation through `Number.isSafeInteger`.
- An asynchronous product lookup using a Promise.
- A balanced-copy operation.
- Automated assertions using Node.js `assert`.

The event system separates catalog operations from notifications about catalog changes.

The asynchronous lookup demonstrates an API-style access pattern without introducing external dependencies.

### C++17

The C++ implementation models an inventory index.

It uses:

- `struct` for individual inventory nodes.
- `unique_ptr` for automatic memory ownership.
- STL `vector` for traversal results.
- STL `queue` for breadth-first traversal.
- `optional` for operations that may not return a value.
- `function` for recursive deletion logic.
- Exceptions for invalid inventory records.

Using `unique_ptr` ensures that child nodes are automatically released when their owning tree nodes are destroyed.

The tree is not internally synchronized. Concurrent access requires external synchronization.

### Java 17

The Java implementation separates the catalog data model from its indexing and service responsibilities.

Its components include:

- `Product` record for immutable product data.
- `Node` class for tree structure.
- `CatalogIndex` interface for the core indexing contract.
- `BinarySearchTree` for data structure operations.
- `CatalogService` for application-level operations.
- `OperationStatus` for explicit operation outcomes.
- `Optional` and `OptionalInt` for missing results.

The service layer supports stock-based filtering without exposing the internal tree structure.

The immutable product records also prevent changes to product identifiers from silently invalidating tree ordering.

## 7. PostgreSQL Relational Model

The SQL implementation represents a BST using an adjacency-list structure.

Rather than storing pointers, each node stores a reference to its parent.

### Database relationships

    bst_tree
       |
       | 1:N
       |
    bst_node
       |
       | parent_id
       |
       +---- Parent node
       |
       +---- Left child
       |
       +---- Right child

### Main tables

| Table | Responsibility |
|---|---|
| `bst_tree` | Stores tree metadata |
| `bst_node` | Stores keys and parent-child relationships |

The `bst_node` table contains:

- `node_id`: Unique node identifier.
- `tree_id`: Parent tree identifier.
- `node_key`: BST ordering value.
- `parent_id`: Parent node reference.
- `position`: Left or right child designation.

A root node has a null `parent_id` and null `position`.

### Integrity constraints

The SQL implementation uses:

- Primary keys to identify nodes and trees.
- Foreign keys to enforce parent references.
- Unique constraints to prevent duplicate keys within a tree.
- Partial unique indexes to permit only one root per tree.
- Partial unique indexes to permit one left and one right child per parent.
- Check constraints to validate root and child positions.

The composite parent foreign key prevents a node from referencing a parent in another tree.

These constraints enforce important structural rules, while the insertion function enforces BST ordering during normal operations.

### Database functions

| Function | Purpose |
|---|---|
| `create_tree()` | Creates a new BST |
| `insert_node()` | Inserts a key while maintaining ordering |
| `search_node()` | Searches for a key |
| `inorder_keys()` | Returns sorted keys using a recursive CTE |
| `minimum_key()` | Returns the minimum key |
| `maximum_key()` | Returns the maximum key |
| `validate_bst()` | Checks ordering and reachability |

The insertion function uses transaction-level advisory locking to serialize mutations to the same tree when all writers follow the function.

Direct table modifications should be restricted in production because foreign keys and unique indexes alone cannot enforce the complete BST ordering invariant.

### Recursive CTEs

A recursive common table expression allows PostgreSQL to traverse parent-child relationships.

The recursive traversal begins with the root and repeatedly joins each node to its children.

The `SEARCH` and `CYCLE` clauses provide traversal ordering and cycle detection.

The SQL validation function also calculates lower and upper bounds for descendants. This is necessary because a node can violate an ancestor's ordering rule even when its immediate parent-child relationship appears valid.

## 8. Complexity Analysis

Let:

- `n` represent the total number of nodes.
- `h` represent tree height.
- `w` represent maximum tree width.

| Operation | Average balanced BST | Worst-case BST |
|---|---:|---:|
| Insertion | O(log n) | O(n) |
| Search | O(log n) | O(n) |
| Deletion | O(log n) | O(n) |
| Minimum | O(log n) | O(n) |
| Maximum | O(log n) | O(n) |
| Inorder traversal | O(n) | O(n) |
| Preorder traversal | O(n) | O(n) |
| Postorder traversal | O(n) | O(n) |
| Level-order traversal | O(n) | O(n) |
| Height calculation | O(n) | O(n) |
| BST validation | O(n) | O(n) |
| Balanced-copy construction | O(n) | O(n) |

Additional space requirements:

| Operation | Auxiliary space |
|---|---|
| Iterative search | O(1) |
| Iterative insertion | O(1) |
| Iterative traversal | O(h) |
| Recursive traversal | O(h) |
| Level-order traversal | O(w) |
| Balanced-copy construction | O(n) |

These complexities assume ordinary BST operations without an automatic balancing mechanism.

## 9. Validation and Failure Handling

The implementations include checks for common operational errors.

| Condition | Expected behavior |
|---|---|
| Duplicate key | Reject insertion |
| Missing search key | Return a missing result |
| Missing deletion key | Return false or NOT_FOUND |
| Empty tree | Return an empty result |
| Invalid kth position | Reject or return an absent result |
| Invalid product ID | Reject the record |
| Negative stock | Reject the record |
| Invalid key type | Raise an appropriate exception |
| Incorrect tree ordering | Fail BST validation |

The SQL implementation additionally checks duplicate keys, parent relationships, tree membership, and descendant ordering.

## 10. Security and Production Considerations

A BST is a data structure, not an access-control mechanism.

When incorporated into an application:

- Validate all externally supplied keys.
- Restrict direct modification of internal tree structures.
- Use parameterized SQL queries.
- Separate database read and write privileges.
- Perform related database mutations within transactions.
- Restrict recursive query resource consumption.
- Monitor tree height as insertion patterns change.
- Avoid untrusted input that can deliberately create highly unbalanced trees.
- Apply synchronization when multiple threads or transactions modify the same tree.

The average-case performance of an ordinary BST depends on insertion order. For workloads requiring predictable logarithmic operations, a self-balancing structure such as an AVL tree or Red-Black tree is more appropriate.

## 11. Execution

| File | Execution |
|---|---|
| Python | `python bst_fundamentals.py` |
| JavaScript | `node bst_fundamentals.js` |
| C++17 | `g++ -std=c++17 -O2 bst_fundamentals.cpp -o bst_fundamentals` |
| C++17 | `./bst_fundamentals` |
| Java 17 | `javac Main.java` |
| Java 17 | `java Main` |
| PostgreSQL | Execute `bst_fundamentals.sql` using `psql` |

Python, JavaScript, C++17 and Java 17 require no third-party packages.

The PostgreSQL script creates its own schema, tables, indexes, functions, sample records, validation queries and transaction examples.
