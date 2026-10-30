# Binary Tree Fundamentals and Manual Construction

## Domain and Learning Objectives

A binary tree is a hierarchical data structure in which each node has at most two children. The child positions are distinct: a left child and a right child. A node can have no children, only a left child, only a right child, or both children.

This implementation studies the structure of a binary tree through explicit node creation and manual attachment. It does not use an insertion algorithm, automatic balancing, or a search-tree ordering rule. The purpose is to understand the relationships between nodes before studying more specialized tree structures.

The implementations cover:

- Root, parent, left child, right child, and leaf.
- Height, depth, level, and subtree.
- Manual construction of a binary tree.
- Structural validation and invalid attachment detection.
- Preorder, inorder, postorder, and level-order traversal.
- Subtree size and node-level metrics.
- Ownership and relational integrity.

## Binary Tree Structure

The example tree contains seven nodes:

                         A
                        / \
                       B   C
                      / \   \
                     D   E   F
                        /
                       G

Each node has an identifier and a value. The identifiers make relationships easy to inspect; they do not determine the tree's shape.

| Node | Parent | Left child | Right child |
|---|---|---|---|
| A | None | B | C |
| B | A | D | E |
| C | A | None | F |
| D | B | None | None |
| E | B | G | None |
| F | C | None | None |
| G | E | None | None |

A missing child is represented by `None`, `null`, or an empty child pointer depending on the language. A missing child is not a separate node.

## Core Terminology

### Root

The root is the topmost node of a tree. It has no parent. In the example, A is the root.

A non-empty binary tree has exactly one root. A tree can also be empty, in which case it has no root.

### Parent

A parent is the node directly above another node. B is the parent of D and E. A is not the parent of D because A is an ancestor of D, not its direct parent.

Each non-root node has exactly one parent in a valid tree.

### Child

A child is a node directly connected below a parent. A parent can have up to two children, identified by their positions.

The left and right positions are meaningful. A node with only a right child is different in structure from a node with only a left child.

### Leaf

A leaf is a node with no children. D, F, and G are leaves.

A leaf can still have a parent. Being a leaf describes the node's downward relationships, not its position in the tree.

### Depth

Depth is the number of edges from the root to a node.

| Node | Depth |
|---|---:|
| A | 0 |
| B, C | 1 |
| D, E, F | 2 |
| G | 3 |

The root has depth zero. Moving from a parent to one of its children increases depth by one.

### Level

Level is depth plus one. This convention numbers the root as level 1.

| Node | Level |
|---|---:|
| A | 1 |
| B, C | 2 |
| D, E, F | 3 |
| G | 4 |

Some references use different level-numbering conventions. These implementations consistently use a root level of 1.

### Height

Height is the number of edges on the longest downward path from a node to a leaf.

- A leaf has height 0.
- D, F, and G each have height 0.
- E has height 1 because its longest downward path is E to G.
- B has height 2 because its longest downward path is B to E to G.
- A has height 3 because its longest downward path is A to B to E to G.

Height belongs to a node or subtree. The height of the whole non-empty tree is the height of its root.

For an empty tree, the implementations and database reporting convention use height -1. This makes the height rule consistent with a leaf having height 0.

### Subtree

A subtree is a node together with all its descendants. The subtree rooted at B contains B, D, E, and G.

The subtree rooted at B has:

| Property | Value |
|---|---:|
| Root | B |
| Node count | 4 |
| Height | 2 |
| Leaves | D, G |

A subtree retains the original parent-child relationships among its included nodes. Its root is treated as the starting point for subtree height calculations.

## Relationship Between the Concepts

The terms describe different properties:

| Concept | What it describes | Example |
|---|---|---|
| Root | Topmost node | A |
| Parent | Direct node above another node | B is parent of D |
| Child | Direct node below another node | E is child of B |
| Leaf | Node with no children | G |
| Depth | Distance from root | G has depth 3 |
| Level | Depth plus one | G is on level 4 |
| Height | Longest downward path | B has height 2 |
| Subtree | Node and all descendants | B, D, E, G |

Depth measures upward distance from the root. Height measures downward distance to the deepest leaf. They are not interchangeable. A node's level is a numbering convention derived from its depth.

## Manual Construction Workflow

The sample tree is built by creating nodes and explicitly assigning each child to a parent.

The sequence is:

1. Create A and designate it as the root.
2. Create B and C.
3. Attach B as A's left child and C as A's right child.
4. Create D, E, and F.
5. Attach D and E to B, and F to C.
6. Create G and attach it as E's left child.

The resulting relationships are:

- A: left B, right C.
- B: left D, right E.
- C: right F.
- E: left G.

No sorting or balancing takes place. This is a direct representation of the specified structure.

### Structural Rules

A valid binary tree must satisfy these conditions:

- It has one root if it is non-empty.
- The root has no parent.
- Every non-root node has exactly one parent.
- A node has at most one left child and one right child.
- A node cannot be its own child.
- A node cannot be reachable through multiple parent-child paths.
- A node cannot be attached in a way that creates a cycle.
- Every node in the tree must be reachable from the root.

The source implementations validate these conditions during construction and inspection.

## Traversal Methods

Traversal is the process of visiting nodes in a defined order.

### Preorder

Visit the current node, then the left subtree, then the right subtree.

For the sample tree:

`A, B, D, E, G, C, F`

Preorder is useful when a parent must be processed before its descendants.

### Inorder

Visit the left subtree, then the current node, then the right subtree.

For the sample tree:

`D, B, G, E, A, C, F`

Inorder is particularly useful when studying binary search trees. In this general binary tree, it does not necessarily produce sorted values.

### Postorder

Visit the left subtree, then the right subtree, then the current node.

For the sample tree:

`D, G, E, B, F, C, A`

Postorder is useful when child nodes must be processed before their parent.

### Level-Order

Visit nodes level by level, from left to right.

For the sample tree:

`A, B, C, D, E, F, G`

Level-order traversal uses a queue. It is also called breadth-first traversal.

## Python Implementation

The Python implementation uses a `Node` dataclass with identity-based equality. This is important because two different nodes may contain the same value while remaining different objects.

`BinaryTree` manages the root and the set of nodes connected to it. The `attach` method accepts a detached subtree and validates it before changing the parent-child links. It rejects occupied child positions, nodes already in the tree, inconsistent parent references, cycles, and overlapping subtrees.

The implementation uses:

- Dataclasses for node representation.
- Sets for identity-based membership and structural validation.
- A deque for level-order traversal.
- Explicit stacks for preorder, inorder, and postorder traversal.
- Iterative postorder evaluation for height.
- A report containing parent, child, depth, level, height, leaf status, and subtree size.
- Assertions to verify the sample tree's expected metrics.

The implementation deliberately uses iterative height calculation. Recursive algorithms are concise, but a highly unbalanced tree can exceed Python's recursion limit.

## JavaScript Implementation

The JavaScript implementation uses `TreeNode` and `BinaryTree` classes. A `Map` tracks node identifiers, while `Set` objects track known nodes and reachable nodes.

The tree extends Node.js's `EventEmitter`. Each successful attachment emits a `nodeAttached` event containing the parent identifier, child identifier, and child position. This separates structural changes from observers that may need to log or react to them.

Traversal methods use generators so callers can consume node identifiers without first constructing an entire traversal array. The reporting method computes depth and height maps and returns structured node metrics.

The implementation also distinguishes between nodes registered with the tree and nodes already reachable from its root. This permits detached nodes to be prepared before attachment while preventing the same node from being incorporated twice.

## C++17 Implementation

The C++ implementation focuses on explicit memory ownership.

Each parent owns its left and right children through `std::unique_ptr`. A child's parent pointer is non-owning. This design establishes a clear ownership direction:

- Parent to child: ownership.
- Child to parent: observation.

Moving a detached subtree into a parent transfers ownership. The attachment operation validates the existing tree and incoming subtree before performing that transfer.

The program uses:

- `std::unique_ptr` for exclusive child ownership.
- Raw parent pointers for upward navigation.
- `std::vector` and `std::queue` for traversal.
- `std::unordered_set` for cycle and membership checks.
- `std::unordered_map` for postorder height calculations.
- Exceptions for invalid construction and attachment operations.

The use of iterative traversal avoids unnecessary dependence on call-stack depth. Exclusive ownership also prevents ordinary shared ownership of the same child node.

## Java 17 Implementation

The Java implementation separates structural management from metric reporting.

`Node` is a domain type with immutable identifiers and values. Its parent and child links are mutable only through the tree's attachment operations.

`BinaryTree` maintains:

- A map of registered nodes by identifier.
- An identity-based set of nodes connected to the root.
- Explicit left and right attachment operations.
- Structural validation.
- Traversal methods and metric calculations.

The identity-based set prevents object equality from being confused with node identity. Two nodes with equal data must not be treated as the same node.

`TreeMetricsService` produces immutable `NodeMetrics` records. This keeps reporting separate from structural mutation and provides a stable representation for downstream processing.

## PostgreSQL Implementation

### Relational Representation

The PostgreSQL implementation uses an adjacency-list model. Each row in `tree_nodes` represents one node.

| Column | Purpose |
|---|---|
| `node_id` | Unique database identity |
| `tree_id` | Owning tree |
| `node_key` | Human-readable node identifier |
| `node_value` | Node content |
| `parent_node_id` | Direct parent reference |
| `child_side` | `left`, `right`, or `NULL` for the root |

The parent relationship is stored directly. A root has a null parent and a null child position.

### Database Integrity

The relational model enforces structural rules through multiple mechanisms:

- Primary keys uniquely identify trees and nodes.
- A composite foreign key requires the parent to belong to the same tree.
- A partial unique index allows at most one root per tree.
- A partial unique index prevents two left children or two right children under the same parent.
- Check constraints restrict valid child positions and reject direct self-parenting.
- A trigger detects cycle-producing reparenting.
- Node identity and tree ownership cannot be changed through an update.

The insertion function validates root and child-position arguments before inserting a node. The database constraints remain authoritative if another operation bypasses that function.

### Recursive Metrics

`v_tree_node_metrics` uses a recursive common table expression to walk from each root to its descendants.

It calculates:

- Depth from the root.
- Level as depth plus one.
- Whether a node is a leaf.
- Height from the deepest descendant.
- Subtree size, including the node itself.

`v_tree_summary` aggregates tree-level metrics. The `tree_height` function provides a direct height lookup and returns -1 for an empty tree.

The example also includes a duplicate-child-position test and a cycle-producing update test. Both operations are expected to fail without leaving invalid data behind.

### Query and Performance Considerations

Adjacency lists provide straightforward parent and child lookups. The unique indexes also support the common operation of retrieving children for a particular parent.

Recursive metrics are more expensive than direct relationship lookups. The metrics view calculates descendant information for each node, which can become costly for large trees. A high-volume system may store derived metrics, maintain them transactionally, or calculate them on demand for selected subtrees.

The SQL script uses a recursive path array as an additional safeguard while traversing. The trigger and relational constraints are the primary structural controls.

## Complexity

Let `n` be the number of nodes and `h` the height of the tree.

| Operation | Time complexity | Explanation |
|---|---:|---|
| Attach a subtree | O(n + s) | Validates the existing tree and incoming subtree of size `s` |
| Find depth | O(h) | Follows parent links |
| Find height | O(n) | Visits the selected subtree |
| Count subtree nodes | O(s) | Traverses the selected subtree |
| Preorder traversal | O(n) | Visits every node once |
| Inorder traversal | O(n) | Visits every node once |
| Postorder traversal | O(n) | Visits every node once |
| Level-order traversal | O(n) | Visits every node once using a queue |

For an unbalanced tree, height can approach `n - 1`. A balanced tree with a similar number of nodes usually has a much smaller height. The implementations do not assume that the tree is balanced.

The Python and JavaScript reporting methods calculate subtree size separately for each node, so a complete report can take O(n²) time in the worst case. This is acceptable for the small educational example. A production reporting service should calculate subtree sizes using one postorder pass.

## Running the Implementations

| Implementation | Command |
|---|---|
| Python | `python tree_fundamentals.py` |
| JavaScript | `node tree_fundamentals.js` |
| C++17 | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic tree_fundamentals.cpp -o tree_fundamentals` |
| C++ execution | `./tree_fundamentals` |
| Java 17 compilation | `javac TreeFundamentals.java` |
| Java execution | `java TreeFundamentals` |
| PostgreSQL | `psql -v ON_ERROR_STOP=1 -f tree_fundamentals.sql` |

The PostgreSQL script drops and recreates the `tree_lab` schema. Run it only in a database where replacing that schema is acceptable.

## Expected Structural Results

For the seven-node example:

| Metric | Expected result |
|---|---:|
| Total nodes | 7 |
| Root | A |
| Tree height | 3 |
| Number of levels | 4 |
| Leaf count | 3 |
| Depth of G | 3 |
| Level of G | 4 |
| Height of B | 2 |
| Size of subtree rooted at B | 4 |

The leaves are D, F, and G.

The implementation conventions are consistent across the four programming languages and the database: height and depth are edge counts, and level starts at 1.

## Practical Limitations

This is a general binary tree, not a binary search tree. There is no rule that places smaller values on the left or larger values on the right. Searching for a value therefore requires traversal in the general case.

The examples also do not implement AVL rotations, red-black balancing, heap ordering, threaded-tree links, or automatic insertion. Those mechanisms introduce additional invariants beyond the basic parent-child structure.

The database stores nodes as relational rows, so deleting a parent cascades to its descendants. The C++ implementation uses exclusive child ownership, while Python and JavaScript rely on managed object references and explicit structural checks. Java uses identity-based membership to preserve the distinction between node objects and their values.

These differences demonstrate that the same logical tree can be represented through different ownership, validation, and persistence models without changing the underlying definitions of root, parent, child, leaf, height, depth, subtree, and level.
