# Lowest Common Ancestor

## 1. Topic Overview

The Lowest Common Ancestor (LCA) is a fundamental tree algorithm used to identify the deepest node that is an ancestor of two or more specified nodes.

An ancestor of a node is any node encountered while moving from that node toward the root. A node is considered its own ancestor for LCA calculations.

For two nodes `u` and `v`, their lowest common ancestor is the deepest node that belongs to both ancestor paths.

For example:

                    1
               /       \
              2         3
             / \       / \
            4   5     6   7
               / \         \
              8   9         10

Examples:

| Query | Lowest Common Ancestor | Reason |
|---|---:|---|
| LCA(4, 5) | 2 | Both nodes are children of 2. |
| LCA(4, 6) | 1 | Their paths first meet at the root. |
| LCA(8, 9) | 5 | Both nodes belong to the subtree rooted at 5. |
| LCA(8, 10) | 1 | Their paths meet at the root. |
| LCA(2, 8) | 2 | One target is an ancestor of the other. |
| LCA(8, 8) | 8 | Both targets represent the same node. |

The implementations use a binary tree, where each node has at most two children.

## 2. Core Terminology

| Term | Meaning |
|---|---|
| Node | An individual element in a tree. |
| Root | The node without a parent. |
| Parent | The immediate predecessor of a node. |
| Child | A node directly connected below another node. |
| Leaf | A node without children. |
| Ancestor | A node on the path from a target node toward the root. |
| Descendant | A node belonging to another node's subtree. |
| Subtree | A node and all its descendants. |
| Depth | Number of edges between a node and the root. |
| Height | Maximum number of edges from a node to a leaf. |
| LCA | The deepest common ancestor of the target nodes. |

The root has depth zero. A direct child of the root has depth one.

A binary tree is not necessarily a binary search tree. LCA does not require sorted node values.

## 3. LCA Concept

Consider two nodes with root-to-node paths:

- Node 8: `1 → 2 → 5 → 8`
- Node 9: `1 → 2 → 5 → 9`

The common prefix is:

`1 → 2 → 5`

The last node in this common prefix is 5. Therefore, `LCA(8, 9) = 5`.

The LCA has three important properties:

1. It must be an ancestor of the first target.
2. It must be an ancestor of the second target.
3. No deeper node can satisfy both conditions.

The LCA is unique when both targets belong to the same rooted tree.

### Important edge cases

- Both targets are the same node.
- One target is an ancestor of the other.
- Both targets belong to separate root subtrees.
- One or both targets are absent.
- The tree contains only one node.
- The tree is empty.
- The structure contains a cycle or shared child.
- Duplicate values make value-based lookup ambiguous.

Node identity and node value must be distinguished. Two different objects can contain the same value, but they are not necessarily the same tree node.

## 4. Recursive LCA

Recursive LCA uses depth-first traversal.

At each node:

1. Return `None` if the current node is empty.
2. Return the current node if it matches either target.
3. Search the left subtree.
4. Search the right subtree.
5. If both searches return a node, the current node is the LCA.
6. Otherwise, propagate the nonempty result upward.

The algorithm works because a common ancestor must have one target in each of its subtrees, unless one target is itself the ancestor.

### Complexity

Let `n` represent the number of nodes and `h` represent tree height.

| Metric | Complexity |
|---|---|
| Time | O(n) |
| Auxiliary recursion space | O(h) |
| Balanced tree height | O(log n) |
| Skewed tree height | O(n) |

The recursive method is easy to implement, but a highly skewed tree can exceed the language's recursion limit or stack capacity.

The Python, JavaScript, C++17 and Java 17 implementations validate that both targets belong to the tree before returning a result.

## 5. Parent-Based LCA

Parent-based LCA requires every node to maintain a reference to its parent.

The algorithm works as follows:

1. Start from the first target.
2. Traverse upward and store all its ancestors.
3. Start from the second target.
4. Traverse upward.
5. Return the first node found in the stored ancestor set.

For example:

- First target 8 has ancestors `{8, 5, 2, 1}`.
- Second target 9 has ancestors `{9, 5, 2, 1}`.
- The first common node encountered from 9 is 5.

Therefore, the LCA is 5.

### Complexity

| Metric | Complexity |
|---|---|
| Time | O(h) |
| Auxiliary space | O(h) |

This approach is particularly useful when parent pointers already exist in the application's data model.

Its primary trade-off is storage and maintenance of parent references. Every structural modification must keep parent and child relationships consistent.

A parent-based implementation must also detect malformed parent chains rather than entering an infinite loop.

## 6. Binary-Tree LCA

Binary-tree LCA refers to finding the common ancestor in a general binary tree.

It does not depend on the binary search tree ordering property.

For example, a binary search tree can eliminate one subtree based on value comparisons. A general binary tree cannot make that assumption.

The implementations use three general binary-tree strategies:

| Strategy | Mechanism | Time | Auxiliary Space |
|---|---|---:|---:|
| Recursive | Left and right DFS | O(n) | O(h) |
| Parent-based | Parent references | O(h) | O(h) |
| Iterative | Parent map built using traversal | O(n) | O(n) |

### Iterative approach

The iterative implementation traverses the tree and constructs a map containing each node's parent.

It then follows the same ancestor-intersection principle as the parent-based method.

This avoids recursive traversal and is useful for trees that may be deeply skewed.

### Node lookup

The Python implementation includes value-based lookup with duplicate-value rejection.

The JavaScript and Java implementations maintain maps from employee IDs to node objects.

The C++ implementation uses an `unordered_map` for employee identification.

The PostgreSQL implementation uses employee IDs as primary keys.

## 7. Binary Lifting

Binary lifting is an advanced LCA optimization for repeated queries on a static tree.

Instead of traversing the tree for every query, it preprocesses ancestors at powers of two.

For each node `v`:

- `up[v][0]` stores its immediate parent.
- `up[v][1]` stores its 2nd ancestor.
- `up[v][2]` stores its 4th ancestor.
- `up[v][k]` stores its 2^k-th ancestor.

The recurrence is:

`up[v][k] = up[up[v][k-1]][k-1]`

The query algorithm:

1. Compare the depths of the two targets.
2. Lift the deeper node until both nodes have equal depth.
3. If the nodes are equal, return that node.
4. Lift both nodes together, starting from the largest power of two.
5. Stop when their next ancestors would be equal.
6. Return their immediate common parent.

### Complexity

| Operation | Complexity |
|---|---|
| Preprocessing | O(n log n) |
| Storage | O(n log n) |
| Individual query | O(log n) |

Binary lifting is appropriate when a hierarchy receives many LCA queries without structural changes.

If the tree changes, the index must be rebuilt or maintained using a more advanced dynamic-tree technique.

The JavaScript, C++17 and Java 17 programs implement binary lifting.

## 8. Multiple-Target LCA

The LCA concept can be extended to more than two targets.

The lowest common ancestor of a set of targets is the deepest node that is an ancestor of every target.

For example:

- LCA(8, 9, 10) = 1.
- LCA(8, 9, 5) = 5.

The Python implementation performs a postorder traversal and counts how many targets occur in each subtree.

A node becomes a valid candidate when its subtree contains every requested target.

This extension is useful for determining the common organizational supervisor of multiple employees.

## 9. Python Implementation

The Python script provides a reusable object-oriented tree model.

### Main components

| Component | Responsibility |
|---|---|
| `TreeNode` | Stores a node value, child references and parent reference. |
| `attach_left()` | Attaches a left child with relationship validation. |
| `attach_right()` | Attaches a right child with relationship validation. |
| `validate_tree()` | Checks structural integrity. |
| `recursive_lca()` | Calculates the LCA using recursive DFS. |
| `parent_based_lca()` | Finds the LCA using parent references. |
| `binary_tree_lca_by_value()` | Resolves unique values before performing LCA. |
| `distance_between()` | Calculates ancestor-to-descendant edge distance. |
| `lowest_common_ancestor_many()` | Calculates the LCA of multiple targets. |

### Validation and reliability

The script uses object identity rather than values for structural comparisons.

Its validation checks:

- Repeated node references.
- Inconsistent parent pointers.
- Cycles.
- Invalid attachment.
- Missing targets.
- Duplicate values during value-based lookup.

The test suite uses assertions to verify expected results and failure conditions.

Run the file with Python 3.10 or later.

## 10. JavaScript Implementation

The JavaScript implementation focuses on event-driven queries and repeated-query optimization.

### Main components

| Component | Responsibility |
|---|---|
| `TreeNode` | Represents a hierarchy node. |
| `BinaryTree` | Maintains node registration and relationships. |
| `LCAService` | Provides recursive, parent-based and iterative LCA. |
| `BinaryLiftingIndex` | Precomputes ancestors for fast queries. |
| `LCAQueryProcessor` | Processes requests and emits query events. |

### Event-driven workflow

The query processor extends Node.js `EventEmitter`.

It emits:

- `queryCompleted` when a valid query completes.
- `queryError` when a requested employee is missing.

The event response includes the requested targets, resulting ancestor, selected strategy and query sequence number.

This design separates hierarchy computation from query reporting and application-level event handling.

### Binary lifting

The implementation uses JavaScript `Map` objects to associate nodes with depth and ancestor information.

`Set` objects provide efficient ancestor membership checks.

The index should be reconstructed after changes to the tree.

Run the file with Node.js.

## 11. C++17 Implementation

The C++17 implementation models an enterprise organizational hierarchy.

Each node represents an employee and stores:

- Employee ID.
- Department name.
- Left child.
- Right child.
- Parent.

### Main components

| Component | Responsibility |
|---|---|
| `TreeNode` | Represents an employee node. |
| `BinaryTree` | Owns nodes and validates relationships. |
| `LCAEngine` | Implements three LCA strategies. |
| `BinaryLiftingIndex` | Provides optimized repeated queries. |
| `runTests()` | Verifies correctness across multiple cases. |

### Memory management

The tree owns nodes through `unique_ptr`.

Parent and child references are non-owning raw pointers. This avoids shared ownership cycles while keeping node addresses stable when the storage vector grows.

The tree must outlive the LCA engine and binary lifting index that reference it.

### Error handling

The program rejects:

- Duplicate employee IDs.
- Unknown employees.
- Invalid parent-child relationships.
- Occupied child positions.
- Cycles.
- Inconsistent parent pointers.
- Unreachable nodes.

It uses exceptions to report invalid structural operations.

Compile using a C++17-compatible compiler.

## 12. Java 17 Implementation

The Java implementation models an enterprise employee hierarchy using explicit domain types and service boundaries.

### Domain model

`EmployeeRecord` is an immutable Java record containing the employee identifier, department and employment status.

`TreeNode` stores the employee record and structural references.

`BinaryTree` owns the employee-to-node mapping and validates the hierarchy.

`LCAService` provides recursive, parent-based and iterative operations.

`BinaryLiftingIndex` provides optimized queries.

`HierarchyQueryService` acts as the application service and selects the required query strategy.

### Query strategies

The `QueryStrategy` enum defines four supported strategies:

- `RECURSIVE`
- `PARENT_BASED`
- `ITERATIVE`
- `BINARY_LIFTING`

The service returns an immutable `QueryResult` record.

### Enterprise validation

The application distinguishes between:

- An employee ID that does not exist.
- An employee node that does not belong to the hierarchy.
- An invalid hierarchy structure.
- A valid query with a common ancestor.

The employee status is modeled independently of structural membership. An inactive employee can remain part of an organizational hierarchy and participate in historical hierarchy queries.

The binary lifting index is constructed from the hierarchy and remains valid only while the hierarchy is unchanged.

Run using Java 17.

## 13. PostgreSQL Implementation

The PostgreSQL script models an organizational hierarchy using relational tables and recursive queries.

### Relational schema

| Table | Purpose |
|---|---|
| `department` | Stores organizational departments. |
| `employee` | Stores employee records. |
| `employee_relationship` | Stores parent-child relationships. |
| `hierarchy_audit` | Records relationship changes. |

### Relationship model

`employee_relationship` stores:

- `employee_id`: The employee whose reporting relationship is represented.
- `manager_id`: The immediate manager.
- `child_position`: The employee's left or right position in the manager's binary tree.

The employee ID is the primary key of the relationship table. This ensures that an employee has at most one direct manager.

A unique constraint on `(manager_id, child_position)` ensures that a manager cannot have two left children or two right children.

### Recursive CTE

PostgreSQL recursive CTEs provide a natural way to traverse hierarchical data.

The `find_lca()` function constructs root-to-node paths.

It compares the paths and identifies their deepest common prefix.

The `find_lca_parent_based()` function follows a different approach. It independently constructs the ancestor chains of both targets and finds their first common node.

The distinction is important:

- Recursive path comparison evaluates common root-to-node paths.
- Parent-based lookup intersects upward ancestor chains.

### Multiple-target queries

`find_lca_many()` extends the query to multiple employee identifiers.

It identifies the deepest node common to all target paths.

### Distance calculation

`get_ancestor_distance()` returns the number of edges between an ancestor and a descendant.

It returns `NULL` if the specified ancestor is not on the descendant's upward path.

### Integrity controls

The schema includes:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Relationship indexes.
- Cycle-prevention triggers.
- Relationship audit triggers.
- Recursive integrity reporting.

The cycle-prevention trigger checks the proposed manager's ancestors before allowing a relationship change.

The audit trigger records previous and new manager relationships.

The sample update demonstrates transactional handling with a savepoint and rollback.

### Performance considerations

Indexes on `manager_id` support recursive downward traversal.

The primary key on `employee_id` supports upward ancestor lookup.

For frequently executed queries on a large, mostly static hierarchy, a materialized path, closure table or precomputed ancestor table may be preferable to repeatedly executing recursive CTEs.

The SQL implementation uses recursive CTEs for clarity and does not maintain a persistent binary-lifting index.

## 14. Implementation Comparison

| Technique | Preprocessing | Query Time | Query Space | Suitable Scenario |
|---|---:|---:|---:|---|
| Recursive DFS | None | O(n) | O(h) | Occasional queries |
| Parent-based | None | O(h) | O(h) | Existing parent references |
| Iterative traversal | None | O(n) | O(n) | Deep trees and nonrecursive traversal |
| Binary lifting | O(n log n) | O(log n) | O(n log n) | Repeated queries on static trees |
| PostgreSQL recursive CTE | None | Depends on hierarchy size | Depends on recursive result | Relational organizational data |

The best method depends on tree structure, query frequency, memory availability and whether the hierarchy changes frequently.

## 15. Practical Applications

### Organizational management

An organization can use LCA to identify the lowest shared manager of two employees.

This helps determine:

- Common reporting authority.
- Shared departmental leadership.
- Escalation responsibility.
- Organizational distance.

### File systems

A directory tree can use LCA to find the deepest common parent directory of two files.

For example, the LCA of `/projects/security/api` and `/projects/security/cloud` is `/projects/security`.

### Network routing

Hierarchical network structures can use common ancestors to identify shared routing domains or administrative boundaries.

### Access control

LCA can help identify the nearest shared administrative scope between two organizational resources.

It does not independently establish authorization. Permission decisions must still evaluate access policies, user roles and resource restrictions.

### Knowledge hierarchies

Taxonomies and classification trees can use LCA to identify the closest shared category of two concepts.

## 16. Limitations and Engineering Considerations

**Binary-tree restriction:** The implementations model at most two children per node. General rooted trees can use the same LCA principles with arbitrary child collections.

**Recursive depth:** Recursive algorithms may fail on extremely deep trees. Iterative traversal avoids recursion-stack limitations.

**Missing targets:** A valid LCA requires both targets to belong to the same rooted tree. Implementations must not return a partial match when the other target is absent.

**Duplicate values:** Value-based queries require unique identifiers. Object identity or database primary keys provide unambiguous node identification.

**Mutable hierarchies:** Parent pointers and precomputed indexes must be updated or rebuilt when relationships change.

**Concurrency:** Applications modifying organizational relationships should coordinate concurrent updates. Database transactions, appropriate isolation levels and structural integrity constraints help prevent inconsistent hierarchy states.

**Authorization:** Knowing the LCA of two nodes does not grant permission to access either node or its associated resources.

**Binary lifting:** Its query efficiency comes at the cost of additional memory and preprocessing. It is most useful for large numbers of queries against a stable tree.

## 17. Learning Outcomes

The implementations establish the following distinctions:

- LCA identifies the deepest shared ancestor, not merely the first shared parent.
- Recursive LCA uses subtree traversal and result propagation.
- Parent-based LCA uses upward traversal and ancestor membership.
- General binary-tree LCA does not depend on sorted node values.
- Binary lifting improves repeated-query performance through preprocessing.
- PostgreSQL recursive CTEs express hierarchy traversal directly in relational workflows.
- Structural validation is essential for reliable ancestor calculations.
- Hierarchy membership, node identity and authorization are separate concerns.
