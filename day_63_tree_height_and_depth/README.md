# Tree Height and Depth

## Scope

This project implements four core binary-tree operations:

- Maximum depth
- Minimum depth
- Leaf counting
- Balanced-tree checking

The five source implementations use the same conceptual tree model while applying different engineering approaches. A tree is represented as nodes with at most one left child and one right child.

The central distinction is:

| Operation | Meaning | Empty tree |
|---|---|---:|
| Maximum depth | Number of nodes on the longest root-to-leaf path | `0` |
| Minimum depth | Number of nodes on the shortest root-to-leaf path | `0` |
| Leaf count | Number of nodes with no children | `0` |
| Balanced check | Every node has subtree heights differing by at most one | `true` |

Depth is measured in nodes rather than edges. Therefore, a single-node tree has maximum depth `1` and minimum depth `1`.

## Domain Model

The implementations use this structure:

Repository-style tree representation is not required here. The computational domain is a binary tree:

`Root → Left/Right Children → Descendant Nodes → Leaves`

A node is a leaf when both child references are absent.

The four operations are deliberately separate:

- Maximum depth evaluates the longest path.
- Minimum depth finds the first reachable leaf from the root.
- Leaf counting identifies terminal nodes.
- Balance checking evaluates the height difference at every node.

These operations answer different questions even though they traverse the same structure.

## Maximum Depth

Maximum depth is computed recursively in all implementations because the tree itself is recursive.

For a node `N`:

`depth(N) = 1 + max(depth(N.left), depth(N.right))`

The empty subtree contributes depth `0`.

For example:

`        10`
`       /  \`
`      5    15`
`     / \     \`
`    3   7     20`

The longest root-to-leaf path contains four nodes when an additional descendant exists at the fourth level.

The recursive formulation directly mirrors the tree definition. Its time complexity is `O(n)` because every reachable node is visited. Its auxiliary space is `O(h)` for the recursion stack, where `h` is tree height.

For a highly skewed tree, recursive depth can become large. The Python implementation uses recursion for maximum depth because the method is compact and clear, while leaf counting and minimum-depth search demonstrate iterative alternatives.

## Minimum Depth

Minimum depth is the shortest root-to-leaf path, not the shortest path to any missing child.

This distinction matters for trees such as:

`    1`
`   /`
`  2`
` /`
`3`

The minimum depth is `3`. Treating the absent right child of node `1` as a zero-length path would incorrectly produce `1`.

The implementations use breadth-first search for minimum depth. BFS visits nodes by increasing depth, so the first encountered leaf is guaranteed to be at minimum depth.

The process is:

`Root`
`  ↓`
`Depth 1`
`  ↓`
`Depth 2`
`  ↓`
`First leaf encountered`

Time complexity is `O(n)` in the worst case. Auxiliary queue space is `O(w)`, where `w` is the maximum width of the tree.

The implementations also preserve one shortest path in their reporting layer. This makes the result auditable rather than returning only a numeric value.

## Leaf Counting

A leaf has:

`left = null`
`right = null`

Leaf counting is independent of depth. A tree can have a large height while containing only one leaf, as in a completely skewed tree.

The Python, JavaScript, and Java implementations use iterative traversal for this operation. The C++ implementation uses recursive traversal to emphasize ownership-safe tree navigation with `std::unique_ptr`.

For every visited node:

1. Check whether both children are absent.
2. Count the node if it is a leaf.
3. Otherwise continue to its existing children.

The traversal is `O(n)` time.

The iterative versions use `O(h)` stack space in a skewed tree and up to `O(w)` pending nodes depending on traversal order.

## Balanced-Tree Checking

A binary tree is height-balanced when, for every node:

`abs(height(left) - height(right)) <= 1`

Checking only the root is insufficient. A tree can have balanced root subtrees while containing an unbalanced subtree deeper in the structure.

The implementations use a bottom-up height calculation with an early-failure marker.

For each node:

1. Calculate the left subtree height.
2. Stop immediately if the left subtree is unbalanced.
3. Calculate the right subtree height.
4. Stop immediately if the right subtree is unbalanced.
5. Compare the two heights.
6. Return the current height when the node is balanced.

A height of `-1` represents an already detected imbalance.

This avoids recalculating subtree heights. A naive implementation that repeatedly computes heights from every node can degrade toward `O(n²)` on skewed trees. The bottom-up method is `O(n)`.

The balance rule is therefore both a correctness rule and a performance decision.

## Edge Cases

The implementations explicitly cover:

| Case | Maximum depth | Minimum depth | Leaves | Balanced |
|---|---:|---:|---:|---|
| Empty tree | `0` | `0` | `0` | `true` |
| Single node | `1` | `1` | `1` | `true` |
| Completely skewed tree | `h` | `h` | `1` | Depends on `h` |
| Perfect binary tree | `h` | `h` | `2^(h-1)` | `true` |
| Deep unbalanced subtree | Depends on structure | Depends on structure | Depends on structure | `false` |

The input builders also reject malformed level-order representations where non-null nodes would become unreachable.

## Python Implementation

The Python file uses:

- `dataclass` for the node representation.
- `Enum` for explicit balance states.
- `deque` for breadth-first minimum-depth traversal.
- Lists for depth-first stack traversal.
- Type annotations for tree references.
- Explicit validation and custom exceptions.
- JSON serialization for a generated analysis report.
- Assertions for production-example verification.

`BinaryTreeAnalyzer.from_level_order()` converts a level-order sequence into linked node objects. `None` represents a missing child.

The balance operation returns a `BalanceState` rather than exposing the internal `-1` failure marker. The marker remains an implementation detail.

The script also accepts JSON input through standard input when invoked with `--stdin`, allowing the same analyzer to process an externally supplied level-order tree without adding third-party dependencies.

## JavaScript Implementation

The JavaScript file models the tree with classes and uses Node.js standard-library modules for report output.

The implementation differs from Python by introducing an event-driven service:

`TreeAnalysisService`
`    ↓`
`analysis.started`
`    ↓`
`Tree validation and construction`
`    ↓`
`Tree analysis`
`    ↓`
`analysis.completed`

Failures emit `analysis.failed`.

`Map` stores event names and `Set` stores listeners. This avoids duplicate listeners and demonstrates a reusable event mechanism without an external event library.

The analysis service is asynchronous because report persistence uses Node.js promise-based filesystem APIs. The tree algorithms themselves remain synchronous because their in-memory computation does not require asynchronous operations.

## C++17 Implementation

The C++ implementation treats tree ownership explicitly.

Each child is stored as `std::unique_ptr<TreeNode>`. This gives the tree a clear ownership model:

`TreeBuilder`
`    ↓`
`unique_ptr<TreeNode>`
`    ↓`
`Owned child nodes`

No manual `delete` operations are required.

The analyzer receives a non-owning `const TreeNode*` because analysis does not modify or own the tree.

The C++ implementation uses:

- `std::optional<int>` for level-order missing children.
- `std::queue` for breadth-first minimum-depth processing.
- `std::vector` for paths.
- `std::unordered_map` for named examples.
- `std::unique_ptr` for ownership.
- Exceptions for invalid input and report failures.
- `std::ofstream` for report persistence.

The separation between construction, analysis, and reporting provides a stronger ownership boundary than a single procedural function.

## Java 17 Implementation

The Java implementation uses explicit domain types and immutable result structures.

`TreeMetrics` is a Java record containing:

- maximum depth
- minimum depth
- leaf count
- balance state
- shortest path

The record copies the shortest-path list with `List.copyOf`, preventing callers from modifying the stored result.

`TreeAnalyzer` is an interface, allowing the analysis service to depend on behavior rather than a concrete implementation.

`GovernanceService` performs validation before delegating to the analyzer. This separates input policy from tree algorithms.

The Java implementation also uses a local record for breadth-first queue entries. This keeps the path and node together without introducing a mutable transport class.

## PostgreSQL Implementation

The PostgreSQL implementation represents trees relationally.

The main entities are:

| Table | Purpose |
|---|---|
| `binary_trees` | Tree-level metadata |
| `tree_nodes` | Node values and parent relationships |
| `tree_metrics` | Persisted analysis results |

The `tree_nodes` table stores a parent reference and a `child_position` of `L` or `R`.

Partial unique indexes enforce the binary-child constraint:

- At most one left child per parent.
- At most one right child per parent.
- At most one root per tree.

The trigger verifies that a referenced parent belongs to the same tree and prevents a node from becoming its own parent.

This places structural integrity at the database layer rather than relying only on application code.

## Recursive SQL Analysis

`calculate_tree_metrics()` uses a recursive CTE to walk from the root through descendants.

The recursive relation records:

- node identity
- parent identity
- node value
- depth

The query then derives leaf nodes by identifying nodes without children.

The database representation makes depth an explicit derived property of traversal rather than a stored attribute on every node. This prevents stale depth values when parent relationships change.

`refresh_tree_metrics()` stores the current calculated metrics in `tree_metrics`.

The refresh operation uses `INSERT ... ON CONFLICT` so recalculation updates the existing metric record for the tree.

## Validation and Failure Handling

Validation is present at multiple levels.

Application implementations reject:

- non-list or non-array input where applicable
- invalid node values
- oversized inputs
- unreachable level-order nodes
- malformed roots

The SQL implementation rejects:

- invalid child positions
- duplicate left children
- duplicate right children
- duplicate roots
- cross-tree parent references
- self-parenting nodes

These checks address different failure boundaries. Application validation protects the computation interface, while database constraints protect persisted structural integrity.

## Complexity

Let `n` be the number of nodes and `h` the tree height.

| Operation | Time | Typical auxiliary space |
|---|---:|---:|
| Maximum depth | `O(n)` | `O(h)` |
| Minimum depth | `O(n)` worst case | `O(w)` |
| Leaf counting | `O(n)` | `O(h)` or `O(w)` |
| Balanced checking | `O(n)` | `O(h)` |
| Tree construction | `O(n)` | `O(w)` |

`w` denotes maximum tree width.

The balanced-tree implementation is deliberately bottom-up so that subtree heights are calculated once.

## Security and Reliability Considerations

The code does not execute tree values as code or construct SQL using interpolated user values.

The application implementations place an upper bound on accepted input size. This reduces exposure to accidental memory exhaustion and excessively deep computational input.

The SQL model uses parameter-oriented structural relationships through keys and constraints. Tree identifiers are relational values rather than dynamically constructed SQL fragments.

Report files are written as generated data. No generated value is interpreted as executable content.

For production systems, externally supplied trees should also have authorization and resource controls appropriate to the application boundary. These examples focus on algorithmic and structural correctness rather than authentication.

## Practical Distinctions

Maximum and minimum depth should not be confused with tree height conventions based on edges.

If height is defined as edges rather than nodes, a single-node tree has height `0`. These implementations use node count for both depth measurements, so a single-node tree has depth `1`.

Leaf count is not a depth metric. It measures terminal structure.

Balance is not equivalent to equal depths. A balanced tree may have leaves at different depths, provided every node satisfies the subtree-height difference rule.

A tree can therefore be:

- balanced with multiple leaf depths,
- unbalanced with many leaves,
- deep with a single leaf,
- shallow with several leaves.

These distinctions are preserved across all five implementations.

## Example Result

For the production tree:

`          10`
`        /    \`
`       5      15`
`      / \    /  \`
`     3   7  12  18`
`    / \ / \   \ / \`
`   1  4 6 8   13 17 20`

the analysis produces:

| Metric | Result |
|---|---:|
| Maximum depth | `4` |
| Minimum depth | `3` |
| Leaf count | `7` |
| Balanced | `true` |

The shortest root-to-leaf paths contain three nodes, while the longest paths contain four nodes.

## File Responsibilities

| File | Primary engineering perspective |
|---|---|
| Python | Recursive and iterative tree analysis with validation, assertions, and JSON reporting |
| JavaScript | Event-driven analysis service with asynchronous report persistence |
| C++17 | Ownership-safe tree model using `unique_ptr` and STL traversal structures |
| Java 17 | Explicit domain model, interfaces, records, immutable results, and service boundaries |
| PostgreSQL | Relational tree representation, recursive CTE analysis, constraints, indexes, triggers, and transactional metric refresh |

The implementations intentionally solve the same four analytical problems through different architectural mechanisms rather than serving as line-by-line translations of one another.
