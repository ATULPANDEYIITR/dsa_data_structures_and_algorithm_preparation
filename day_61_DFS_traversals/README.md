# DFS Tree Traversals

## Scope

This project implements depth-first traversal of a binary tree through three distinct visitation orders:

| Traversal | Visit order | Typical interpretation |
|---|---|---|
| Preorder | Root → Left → Right | Process a node before either subtree |
| Inorder | Left → Root → Right | Process a node between its two subtrees |
| Postorder | Left → Right → Root | Process a node after both subtrees |

Each traversal is implemented recursively and iteratively where practical. The implementations use the same underlying binary-tree model but deliberately use language-specific data structures and design techniques.

The central distinction is traversal order, not merely the mechanism used to traverse the tree.

## Binary-Tree Model

The core structure is a node containing a value and up to two child references.

Plain-text representation:

    1
   / \
  2   3
 / \ / \
4  5 6  7

For this tree:

- Preorder produces `1, 2, 4, 5, 3, 6, 7`.
- Inorder produces `4, 2, 5, 1, 6, 3, 7`.
- Postorder produces `4, 5, 2, 6, 7, 3, 1`.

The same node set can therefore produce different sequences without changing the tree itself.

## Traversal Mechanics

### Preorder

Preorder visits the current node before its children.

    visit(root)
    traverse(left)
    traverse(right)

The recursive implementation directly expresses this definition. The iterative implementation uses a LIFO stack. The right child is pushed before the left child because the left child must be removed from the stack first.

Preorder is useful when parent information must appear before descendant information. It can also represent a tree structure when combined with suitable null-child information.

### Inorder

Inorder processes the left subtree, then the current node, then the right subtree.

    traverse(left)
    visit(root)
    traverse(right)

The iterative version maintains a stack of ancestors while repeatedly descending through left children. When no left child remains, the most recently stored ancestor is processed and traversal continues through its right child.

For a binary search tree, inorder traversal produces values in sorted order when the tree satisfies the binary-search-tree ordering invariant.

### Postorder

Postorder delays processing of a node until both subtrees have been processed.

    traverse(left)
    traverse(right)
    visit(root)

This order is useful when a parent operation depends on completed child operations. Examples include expression-tree evaluation, recursive deletion strategies, and computing aggregate properties from children.

The implementations include both a two-stack iterative technique and a one-stack technique. The one-stack implementation tracks the previously processed node so that a parent is emitted only after its right subtree has been handled.

## Recursive Versus Iterative Traversal

| Property | Recursive | Iterative |
|---|---|---|
| State representation | Call stack | Explicit stack |
| Code structure | Close to mathematical definition | Explicit control flow |
| Auxiliary space | `O(h)` call stack | `O(h)` explicit stack |
| Very deep tree | Can exceed runtime stack capacity | Usually safer |
| Debugging | Natural call hierarchy | Explicit traversal state |
| Memory control | Runtime-managed stack | Application-managed stack |

Here `h` is the tree height.

For a balanced tree, `h` is approximately `log2(n)`. For a completely skewed tree, `h` can be `n`.

The iterative implementations are therefore important for production workloads where input depth cannot be trusted.

## Python Implementation

The Python program defines a `TreeNode` dataclass and separate functions for each traversal.

The recursive functions express the traversal rules directly. The iterative functions use Python lists as stacks because `append` and `pop` from the end provide efficient LIFO operations.

The implementation also includes:

- Empty-tree handling.
- Single-node handling.
- A 5,000-node skewed tree.
- Recursive and iterative result comparisons.
- A two-stack postorder implementation.
- A one-stack postorder implementation.
- Structural validation.
- Cycle detection.
- Detection of a node appearing under multiple parents.
- Assertions that verify expected traversal sequences.

The validator is intentionally separate from traversal logic. A malformed graph should not silently be treated as a valid tree.

## JavaScript Implementation

The JavaScript program uses a `TreeNode` class and `Set` objects for structural validation.

The iterative traversals use arrays as explicit stacks. The program also demonstrates asynchronous event-style processing with `setImmediate`, showing that traversal results can be consumed by an event-driven application without changing the traversal algorithm itself.

The implementation validates:

- Cycles.
- Multiple-parent structures.
- Empty trees.
- Single-node trees.
- Deep right-skewed trees.
- Expected traversal sequences.

The deep-tree test is especially relevant to JavaScript because recursive functions ultimately depend on the runtime call stack, while explicit arrays provide application-managed traversal state.

## C++17 Implementation

The C++ program models child ownership using `std::unique_ptr`.

This gives the binary-tree model explicit ownership semantics:

    Tree
      |
      +-- unique_ptr left
      |
      +-- unique_ptr right

The traversal functions expose `const TreeNode*` because traversal does not need to mutate the tree.

The implementation uses:

- `std::vector` for traversal results.
- `std::vector<const TreeNode*>` as explicit stacks.
- `std::unordered_set` for structural validation.
- `std::unique_ptr` for ownership.
- Exceptions for invalid structures.
- Assertions for executable verification.

The two-stack postorder implementation separates discovery order from output order. The one-stack implementation reduces auxiliary traversal storage but requires more explicit state management.

C++ ownership makes accidental sharing harder in the primary tree representation, while the validation logic still demonstrates how malformed graph structures can be detected.

## Java 17 Implementation

The Java program uses a domain-oriented `TreeNode` class and Java collections for traversal state.

`ArrayDeque` is used as the stack because it provides efficient stack operations without the synchronization overhead of legacy `Stack`.

The program includes:

- Recursive traversal methods.
- Iterative traversal methods.
- A two-stack postorder algorithm.
- A one-stack postorder algorithm.
- Structural validation.
- A custom `TraversalException`.
- Deep-tree validation.
- Empty and single-node cases.
- Assertion-style runtime checks.

The Java implementation keeps traversal operations separate from validation. This makes the traversal service easier to reason about and allows malformed input to fail explicitly rather than producing an incomplete result.

## PostgreSQL Model

The SQL implementation treats a binary tree as relational data.

The main entities are:

| Table | Purpose |
|---|---|
| `tree` | Stores logical tree definitions |
| `tree_node` | Stores nodes and child relationships |
| `traversal_run` | Records traversal execution state |
| `traversal_result` | Stores ordered traversal output |

The relationship is:

    tree
      |
      +-- tree_node
      |     |
      |     +-- left_node_id
      |     +-- right_node_id
      |
      +-- traversal_run
              |
              +-- traversal_result

Foreign keys enforce references between records. The node trigger checks that child nodes belong to the same tree and prevents direct self-reference and identical left/right children.

`validate_tree_structure` checks whether a populated tree has exactly one root and whether its nodes are reachable from that root.

The traversal execution function records a traversal run and materializes the resulting ordered nodes into `traversal_result`. The reporting view combines execution metadata with result counts.

## Validation and Failure Conditions

A valid binary tree should have:

- Zero or one root for an empty or non-empty tree.
- Exactly one parent for every non-root node.
- No node pointing to itself.
- No cycles.
- No disconnected node component.
- At most one left child and one right child per parent.
- Child nodes belonging to the same logical tree.

The in-memory implementations explicitly detect cycles and multiple-parent structures.

The PostgreSQL model enforces local relationship rules with constraints and triggers and performs broader structural validation through a recursive query.

Database validation is deliberately different from application validation. Constraints handle invariants that can be enforced locally, while recursive validation is required for graph-wide properties such as reachability.

## Complexity

For `n` nodes:

| Algorithm | Time | Auxiliary traversal space |
|---|---:|---:|
| Preorder recursive | `O(n)` | `O(h)` |
| Preorder iterative | `O(n)` | `O(h)` |
| Inorder recursive | `O(n)` | `O(h)` |
| Inorder iterative | `O(n)` | `O(h)` |
| Postorder recursive | `O(n)` | `O(h)` |
| Postorder two-stack | `O(n)` | `O(n)` |
| Postorder one-stack | `O(n)` | `O(h)` |

The output list itself requires `O(n)` storage when all node values are materialized.

A balanced tree generally has `h = O(log n)`, while a skewed tree can have `h = O(n)`.

## Edge Cases

### Empty tree

A null root produces an empty traversal.

This is the natural identity case and should not be treated as an error.

### Single-node tree

All three traversal orders produce exactly the same one-element sequence because there are no children whose relative positions can differ.

### Left-skewed tree

For a tree containing only left children:

- Preorder follows root-to-leaf order.
- Inorder follows leaf-to-root order.
- Postorder also follows leaf-to-root order.

### Right-skewed tree

For a tree containing only right children:

- Preorder follows root-to-leaf order.
- Inorder follows root-to-leaf order.
- Postorder follows leaf-to-root order.

### Duplicate values

Traversal operates on nodes, not unique values. Duplicate values therefore do not invalidate a binary tree.

This is why the implementations validate node identity rather than using node values as structural identifiers.

## Security and Robustness

Tree traversal is often exposed to input-derived structures in parsers, expression evaluators, configuration systems, compilers, and data-processing applications.

Important controls include:

- Reject cyclic structures when a tree is required.
- Avoid trusting claimed tree depth.
- Prefer iterative traversal when depth can be attacker-controlled.
- Bound input size before allocating large structures.
- Avoid using node values as structural identities.
- Validate parent-child relationships before processing.
- Fail explicitly on malformed structures.
- Preserve database referential integrity.
- Use transactions when traversal execution and result recording must remain consistent.

The primary denial-of-service risk in recursive implementations is excessive depth. An adversarially skewed tree can make recursion consume the runtime call stack even though the algorithmic complexity remains `O(n)`.

## Traversal Order and Application Semantics

The traversal order determines when a node becomes available to downstream logic.

    Preorder:
        Parent
          ↓
        Children

    Inorder:
        Left child
          ↓
        Parent
          ↓
        Right child

    Postorder:
        Children
          ↓
        Parent

This distinction matters when traversal is used for more than printing values.

Preorder is suitable when parent records must be emitted before descendants.

Inorder is especially significant for ordered binary-search-tree data.

Postorder is appropriate when parent processing depends on completed child processing.

## Verification Strategy

The five implementations use the same canonical seven-node tree so that their outputs can be compared directly.

Expected values:

| Traversal | Result |
|---|---|
| Preorder | `1, 2, 4, 5, 3, 6, 7` |
| Inorder | `4, 2, 5, 1, 6, 3, 7` |
| Postorder | `4, 5, 2, 6, 7, 3, 1` |

The source files also test empty trees, single-node trees, deep skewed trees, and malformed cyclic structures.

The validation strategy therefore checks both normal traversal semantics and failure behavior.

## Practical Distinctions

A traversal algorithm answers the question:

> In what order should nodes be visited?

A recursive implementation answers it through function-call state.

An iterative implementation answers it through explicit data structures.

A relational implementation answers it through stored relationships, recursive queries, ordered paths, and persisted traversal results.

These are different engineering representations of the same DFS concepts. The traversal order remains the invariant across implementations, while memory management, state representation, validation, and failure handling differ by runtime and execution environment.
