# Tree Assessment

## 1. Technical Scope

Tree assessment evaluates the structure, relationships, paths, and traversal behavior of binary trees.

The implementations provide six principal assessment areas:

| Area | Operations |
|---|---|
| Traversal | Preorder, inorder, postorder |
| Tree dimensions | Height, diameter, minimum depth |
| Path analysis | Root-to-leaf sums, all matching paths, maximum path sum |
| Ancestor analysis | Lowest common ancestor |
| Structural validation | Balanced-tree assessment, cycle and shared-child detection |
| Level-order analysis | BFS, zigzag traversal, right-side view |

The Python, JavaScript, C++17, Java 17, and PostgreSQL implementations use the same sample tree and consistent definitions for height and diameter.

## 2. Binary Tree Structure

A binary tree is a hierarchical data structure in which each node has at most two children.

Each node contains:

- A value.
- A reference to its left child.
- A reference to its right child.

A node without children is called a leaf.

A root is the first node in the hierarchy. Every other node has one parent in a valid tree.

### Sample structure

                            10
                       /        \
                      5          15
                    /   \          \
                   3     7          20
                  / \     \
                 1   4     8

The tree contains nine nodes.

| Property | Value |
|---|---:|
| Root | 10 |
| Total nodes | 9 |
| Leaf nodes | 1, 4, 8, 20 |
| Height | 3 |
| Diameter | 6 |
| Balanced | Yes |

A binary tree does not necessarily satisfy the ordering rules of a binary search tree. The implementations therefore operate on general binary trees.

## 3. Tree Traversal

Traversal determines the order in which nodes are visited.

### 3.1 Preorder

Order:

1. Visit root.
2. Visit left subtree.
3. Visit right subtree.

For the sample tree:

`[10, 5, 3, 1, 4, 7, 8, 15, 20]`

Applications include:

- Serializing hierarchical structures.
- Generating directory representations.
- Processing expressions in prefix notation.
- Copying tree structures.

### 3.2 Inorder

Order:

1. Visit left subtree.
2. Visit root.
3. Visit right subtree.

For the sample tree:

`[1, 3, 4, 5, 7, 8, 10, 15, 20]`

Inorder traversal produces sorted output only when the input satisfies binary search tree ordering rules.

Applications include:

- Inspecting binary search trees.
- Evaluating expression structures.
- Producing ordered node sequences.

### 3.3 Postorder

Order:

1. Visit left subtree.
2. Visit right subtree.
3. Visit root.

For the sample tree:

`[1, 4, 3, 8, 7, 5, 20, 15, 10]`

Applications include:

- Deleting hierarchical structures.
- Evaluating expression trees.
- Calculating subtree properties.
- Bottom-up structural analysis.

### Traversal comparison

| Traversal | Visiting order | Typical application |
|---|---|---|
| Preorder | Root, left, right | Serialization |
| Inorder | Left, root, right | BST inspection |
| Postorder | Left, right, root | Subtree calculations |
| Level-order | Level by level | Hierarchical reporting |

Depth-first traversals use stacks or recursion. Level-order traversal uses a queue.

All three depth-first traversals and level-order traversal require O(n) time.

## 4. Height

Height measures the longest downward path from a node to a leaf.

This implementation measures height in edges.

For a node:

\[
H(node)=1+\max(H(left),H(right))
\]

The base case is:

\[
H(null)=-1
\]

Consequently:

- An empty tree has height -1.
- A single-node tree has height 0.
- A root with two leaf children has height 1.

The sample tree has height 3.

The implementations use breadth-first traversal for height in Python, JavaScript, C++, and Java.

The SQL implementation uses a recursive CTE to determine the maximum depth.

Complexity:

- Time: O(n).
- Auxiliary space: O(n) in the worst case.

Height is useful for evaluating tree shape, traversal depth, and balancing requirements.

## 5. Diameter

Diameter is the maximum number of edges on a path between any two nodes.

The path does not necessarily pass through the root.

For every node, calculate the heights of its left and right subtrees.

\[
D(node)=H(left)+H(right)+2
\]

The final diameter is:

\[
D=\max_{node \in T}D(node)
\]

For the sample tree, the longest path is:

`1 → 3 → 5 → 10 → 15 → 20`

Its diameter is six edges.

The Python implementation uses a postorder recursive calculation.

JavaScript, C++17, and Java 17 use iterative postorder calculations and store previously calculated subtree heights.

The SQL implementation calculates subtree heights from leaves towards their ancestors.

Complexity:

- Time: O(n).
- Auxiliary space: O(n).

A naive implementation that recalculates subtree heights independently at every node can require O(n²) time in a skewed tree.

## 6. Path Sum

Path-sum assessment evaluates the sum of node values along a path.

### 6.1 Root-to-leaf path sum

A root-to-leaf path starts at the root and ends at a leaf.

For each visited node:

\[
S_{new}=S_{previous}+value(node)
\]

The sample tree contains this matching path:

`10 → 5 → 3 → 1`

Its sum is:

\[
10+5+3+1=19
\]

The implementations provide:

- Boolean target-sum verification.
- Retrieval of every matching root-to-leaf path.
- Support for negative values.

A common error is accepting a partial path that reaches the target before reaching a leaf. The implementations require the complete root-to-leaf path.

### 6.2 Maximum path sum

Maximum path sum considers a path between any two nodes, not only root-to-leaf paths.

For each node, calculate the maximum downward contribution:

\[
G(node)=value(node)+
\max(0,G(left),G(right))
\]

The best path passing through that node is:

\[
P(node)=value(node)+
\max(0,G(left))+
\max(0,G(right))
\]

The maximum result is the greatest value of P across all nodes.

Negative subtree contributions are excluded when they reduce the path sum.

A non-empty path must still be selected. For a tree containing only -5, the answer is -5 rather than zero.

Complexity:

- Time: O(n).
- Auxiliary space: O(n) for the iterative implementations.

## 7. Lowest Common Ancestor

The Lowest Common Ancestor (LCA) of two nodes is their deepest shared ancestor.

For example:

- LCA of nodes 1 and 8 is 5.
- LCA of nodes 1 and 20 is 10.

The implementations treat the structure as a general binary tree.

They do not assume that smaller values belong on the left or larger values belong on the right.

### LCA processing

1. Identify the two requested nodes.
2. Record their ancestors.
3. Compare their ancestor relationships.
4. Return the deepest shared ancestor.
5. Return no result when either requested node is missing.

Python uses recursive decomposition.

JavaScript and Java use parent mappings.

C++17 uses recursive subtree searches.

PostgreSQL uses recursive ancestor CTEs and selects the shared ancestor with the minimum combined depth.

Complexity:

- Time: O(n).
- Auxiliary space: O(n).

The sample implementations use unique node values for value-based LCA requests. A production system should prefer stable node identifiers when duplicate values are permitted.

## 8. Balanced-Tree Assessment

A binary tree is height-balanced when the height difference between the left and right subtrees of every node is at most one.

The condition is:

\[
|H(left)-H(right)|\leq1
\]

The condition must hold at every node, not just at the root.

For example:

    1
     \
      2
       \
        3
         \
          4

This structure is unbalanced.

A common inefficient approach calculates subtree heights repeatedly.

The implementations instead use bottom-up height calculations. If an unbalanced subtree is identified, the balance assessment can stop immediately.

Complexity:

- Time: O(n).
- Auxiliary space: O(n) in the iterative implementations.

Balanced-tree assessment is particularly important in search trees and other structures where excessive height can degrade operation performance.

The assessment does not rebalance the tree. It only evaluates its current structure.

## 9. Level-Order Problems

Level-order traversal uses breadth-first search.

A queue stores nodes waiting to be processed.

The algorithm:

1. Insert the root.
2. Determine the current queue size.
3. Process exactly that many nodes.
4. Insert their children.
5. Repeat until the queue is empty.

For the sample tree:

`[[10], [5, 15], [3, 7, 20], [1, 4, 8]]`

### 9.1 Zigzag traversal

Zigzag traversal reverses the visiting direction at alternate levels.

Expected output:

`[[10], [15, 5], [3, 7, 20], [8, 4, 1]]`

### 9.2 Right-side view

The right-side view selects the final node from every level.

Expected output:

`[10, 15, 20, 8]`

### 9.3 Minimum depth

Minimum depth is the shortest number of nodes from the root to a leaf.

Unlike height, this implementation measures minimum depth in nodes.

The sample tree has minimum depth three.

Breadth-first search can return as soon as it encounters the first leaf.

### Complexity

| Operation | Time | Auxiliary space |
|---|---:|---:|
| Level-order | O(n) | O(n) |
| Zigzag | O(n) | O(n) |
| Right-side view | O(n) | O(n) |
| Minimum depth | O(n) worst case | O(n) |

## 10. Python Implementation

The Python implementation provides a reusable `BinaryTree` class and a `TreeNode` dataclass.

Its main design decisions include:

- Lists for traversal results.
- `deque` for efficient queue operations.
- Explicit stacks for iterative traversals.
- Recursive postorder calculations for diameter and balance.
- Path copying when storing matching paths.
- Exceptions for invalid tree structures.
- Assertions for functional verification.

The `validate()` method detects cycles and shared children using object identities.

The implementation distinguishes between an empty tree, a single-node tree, and a structurally unbalanced tree.

The test suite verifies normal cases, negative values, missing LCA nodes, shared children, and cycles.

Run the script using Python 3.

## 11. JavaScript Implementation

The JavaScript implementation uses classes, generators, Maps, Sets, and asynchronous iteration.

Its distinct features include:

- Generator-based depth-first traversal.
- Iterative postorder algorithms.
- `Map` for storing subtree heights and parent relationships.
- `WeakSet` for structural validation.
- Asynchronous level-order event production.
- Explicit validation of safe integer values.

The `levelOrderEvents()` method exposes each level as an asynchronous event.

This approach is useful when a consumer needs to process a large hierarchy level by level instead of receiving the entire traversal result immediately.

The event contains:

- The current level number.
- The values found at that level.

The implementation uses no third-party npm dependencies.

Run it using Node.js.

## 12. C++17 Implementation

The C++17 implementation uses explicit ownership through `std::unique_ptr`.

This provides automatic memory management and prevents accidental ownership duplication through ordinary pointer copying.

Important design decisions:

- `TreeNode` models individual nodes.
- `TreeAssessment` provides the assessment interface.
- `std::queue` implements breadth-first traversal.
- `std::vector` stores traversal results.
- `std::unordered_set` detects shared nodes and cycles.
- `std::unique_ptr` manages child ownership.
- Exceptions report invalid structures and unsupported operations.

The diameter and balance operations use bottom-up calculations.

The maximum path-sum implementation uses `long long` for accumulated values to reduce the risk of integer overflow.

The program includes assertions for the sample tree, an empty tree, a negative-value tree, and an unbalanced tree.

Compile using a C++17-compatible compiler.

## 13. Java 17 Implementation

The Java implementation uses an enterprise-oriented service structure.

### Domain components

| Component | Responsibility |
|---|---|
| `TreeNode` | Represents a tree node |
| `TraversalOrder` | Defines traversal policies |
| `TreeValidationException` | Reports structural violations |
| `TreeAssessmentService` | Executes assessment operations |
| `AssessmentReport` | Stores an immutable assessment result |

Java records are used for traversal frames and assessment reports.

Collections such as `ArrayDeque`, `HashMap`, `HashSet`, and `ArrayList` provide the necessary data structures.

The service keeps its root reference private and exposes assessment methods rather than exposing the internal collection of nodes.

The report uses immutable list snapshots to prevent callers from modifying the results after assessment.

The implementation validates the tree before performing operations.

It also distinguishes between a missing LCA result and a valid ancestor.

Compile and execute using Java 17.

## 14. PostgreSQL Implementation

The PostgreSQL implementation represents a tree through relational tables.

### 14.1 Relational structure

The primary tables are:

**binary_tree**

Stores individual tree definitions.

**tree_node**

Stores nodes and their parent relationships.

The main relationship is:

    binary_tree
        |
        | 1:N
        |
    tree_node
        |
        | parent_id
        |
        +---- tree_node

The composite primary key `(tree_id, node_id)` ensures that node identifiers are unique within each tree.

The composite self-referencing foreign key ensures that a parent belongs to the same tree.

A partial unique index prevents multiple root nodes within one tree.

### 14.2 Recursive CTEs

A recursive Common Table Expression contains an initial query and a recursive query.

The initial query selects the root.

The recursive query finds children of previously discovered nodes.

The recursion continues until no additional children are found.

This mechanism supports:

- Hierarchical retrieval.
- Depth calculation.
- Level-order reporting.
- Root-to-leaf path construction.
- Ancestor identification.
- Subtree analysis.

### 14.3 Functions and triggers

`validate_tree()` checks root count and reachability.

`tree_height()` calculates maximum depth.

`tree_lca()` finds the lowest common ancestor.

The `validate_tree_node()` trigger function prevents invalid self-parenting and cyclic parent assignments.

The database also enforces referential integrity through foreign keys.

### 14.4 Indexing

The parent index:

`idx_tree_parent`

Supports retrieval of children belonging to a particular parent.

The node-value index:

`idx_tree_node_value`

Supports value-based searches.

The indexes are useful for repeated hierarchical queries, although they introduce additional storage and write-maintenance costs.

### 14.5 Transaction handling

The SQL script uses a transaction to group schema changes and sample-data operations.

A failure during execution prevents a partially committed setup.

The demonstration also isolates intentionally invalid operations inside exception-handling blocks.

The SQL implementation assumes valid binary-tree relationships. The relational schema enforces parent existence and one root, while the validation function checks reachability.

A production system requiring strict binary-tree enforcement should also add a maximum-two-children constraint through a concurrency-safe database operation. A simple row-level trigger counting children is insufficient under concurrent transactions.

## 15. Edge Cases and Validation

The implementations explicitly address the following situations.

| Case | Expected behavior |
|---|---|
| Empty tree | Height -1, diameter 0 |
| Single-node tree | Height 0, diameter 0 |
| Missing LCA node | No ancestor result |
| Negative node values | Valid path calculations |
| All-negative tree | Maximum non-empty path selected |
| Unbalanced tree | Balance assessment returns false |
| Shared child | Invalid tree structure |
| Cyclic relationship | Invalid tree structure |
| Missing target path | Path-sum assessment returns false |
| Multiple matching paths | Every matching path is returned |

A tree's structural validity and its balance are separate properties.

A valid tree can be unbalanced.

An empty tree is considered balanced by convention.

## 16. Complexity Analysis

Let:

- n represent the number of nodes.
- h represent the height of the tree.

| Operation | Time complexity | Space complexity |
|---|---|---|
| Preorder | O(n) | O(n) |
| Inorder | O(n) | O(n) |
| Postorder | O(n) | O(n) |
| Level-order | O(n) | O(n) |
| Height | O(n) | O(n) |
| Diameter | O(n) | O(n) |
| Balanced-tree check | O(n) | O(n) |
| Path-sum existence | O(n) | O(h) |
| All matching paths | O(n + output size) | O(h + output size) |
| LCA | O(n) | O(n) |
| Right-side view | O(n) | O(n) |
| Minimum depth | O(n) worst case | O(n) |
| Maximum path sum | O(n) | O(n) |

The recursive implementations use O(h) call-stack space for recursive calculations.

For a skewed tree, h can approach n. This can cause stack-depth problems in languages with limited recursion depth.

The iterative JavaScript, C++17, and Java implementations avoid recursive postorder processing for the major height-based calculations.

The SQL implementation uses recursive CTEs, whose execution and memory costs depend on the number of nodes, tree depth, indexes, and database execution plans.

## 17. Practical Assessment Workflow

A consistent tree-assessment process is:

    Input tree
        |
        v
    Validate node relationships
        |
        v
    Calculate traversal sequences
        |
        v
    Calculate height and diameter
        |
        v
    Check structural balance
        |
        v
    Evaluate root-to-leaf paths
        |
        v
    Calculate lowest common ancestor
        |
        v
    Generate level-order results
        |
        v
    Produce assessment report

Traversal establishes the visiting order.

Height and diameter measure tree dimensions.

Path analysis evaluates node-value relationships.

LCA evaluates shared ancestry.

Balance assessment evaluates structural efficiency.

Level-order operations provide a breadth-first view of the hierarchy.

These operations together provide a practical foundation for evaluating binary-tree correctness, structure, and behavior.
