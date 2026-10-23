# Recursive Trees

This project studies recursion by representing recursive calls as trees. Each node corresponds to one invocation or one recursive state, while each outgoing edge represents a recursive decision made by that invocation.

The four models are deliberately distinct:

| Model | Recursive decision | Typical tree behavior | Main complexity insight |
|---|---|---|---|
| Fibonacci | `fib(n-1)` and `fib(n-2)` | Uneven binary tree with repeated subproblems | Exponential naive recursion |
| Subsets | Exclude or include each item | Complete binary decision tree | `2^n` subsets |
| Binary choices | Choose `0` or `1` | Complete binary tree | `2^d` leaves |
| Divide-and-conquer | Split the input into smaller independent parts | Balanced decomposition tree | Often logarithmic depth with linear or near-linear work per level |

A recursion tree makes the call structure visible. It is different from a mathematical expression tree because the important information here is the sequence of recursive calls and the branching caused by each recursive rule.

## Recursion-tree representation

The implementations use a common conceptual structure:

```text
                  recursive state
                  /              \
             decision A       decision B
                /                 \
           smaller state       smaller state
```

A node stores a description of the current state. Its children store the states produced by recursive calls.

The tree can be analyzed through:

- node count, representing recursive calls;
- depth, representing recursion depth;
- leaf count, representing base cases or completed decisions;
- branching factor, representing the number of recursive alternatives;
- repeated states, revealing overlapping subproblems;
- work performed at each level.

A recursion tree is therefore useful both for understanding execution and for estimating asymptotic cost.

## Fibonacci

The Python, JavaScript, C++, and Java implementations construct the tree for the naive recursive definition:

`fib(n) = fib(n-1) + fib(n-2)`

with `fib(0)` and `fib(1)` as base cases.

For `fib(5)`, the upper portion has the form:

```text
fib(5)
├── fib(4)
│   ├── fib(3)
│   │   ├── fib(2)
│   │   └── fib(1)
│   └── fib(2)
│       ├── fib(1)
│       └── fib(0)
└── fib(3)
    ├── fib(2)
    └── fib(1)
```

The important feature is repeated work. States such as `fib(3)` and `fib(2)` appear multiple times. The tree exposes why directly implementing the mathematical recurrence produces exponential growth.

The source files therefore separate tree construction from value computation. The tree uses the intentionally naive recurrence so that recursive structure can be observed, while the value calculation uses an iterative algorithm. This avoids unnecessarily executing the exponentially large call tree when only the Fibonacci value is required.

The recursive tree has depth proportional to `n`, but the number of calls grows exponentially. The exact growth is related to the Fibonacci sequence.

For production software, memoization or dynamic programming eliminates repeated subproblems. The recursion tree remains valuable because it shows exactly what memoization is preventing.

## Subsets

Subset generation has a different structure. For every item, there are exactly two independent choices:

```text
                 item A
                /      \
           exclude A   include A
             /            \
          item B          item B
          /   \            /   \
        ...   ...        ...   ...
```

For `n` items, every item contributes one binary decision. The tree therefore contains `2^n` leaves.

The Python and JavaScript implementations also provide actual subset generation. The tree representation describes the decision process, while the generated collection contains the completed subsets.

The important distinction from Fibonacci is that repeated states are not the central issue. The exponential result is inherent when every subset must actually be produced. Memoization cannot reduce the output requirement from `2^n` subsets to a polynomial amount of work.

An empty input has one subset: the empty set. This is consistent with `2^0 = 1`.

## Binary choices

The generic binary-choice model isolates the branching pattern without attaching it to a particular domain.

At each recursion level, the algorithm chooses either `0` or `1`:

```text
                 ""
               /    \
              0      1
             / \    / \
            00 01  10 11
           /...           ...
```

For depth `d`, the number of leaves is `2^d`.

This model is useful for recognizing exponential search spaces in problems involving independent yes/no decisions, configuration generation, Boolean assignments, and many backtracking algorithms.

The number of nodes in a complete binary tree of depth `d`, when the root is depth zero, is:

`1 + 2 + 4 + ... + 2^d = 2^(d+1) - 1`

The Java and C++ implementations use explicit tree objects and immutable-style access to child collections where appropriate. The Python implementation uses a lightweight recursive node model, while JavaScript uses a mutable event-friendly object model.

## Divide-and-conquer

Divide-and-conquer recursion has a different purpose from binary enumeration.

The recursive operation first divides the problem and then independently processes the resulting subproblems:

```text
                 sort([8,3,7,4,2,6])
                       /        \
              sort([8,3,7])   sort([4,2,6])
                 /    \          /      \
             ...      ...      ...      ...
```

The merge-sort example reaches singleton arrays as base cases. The recursive tree records decomposition, not every comparison performed during the eventual merge phase.

For an input of size `n`, balanced splitting gives a recursion depth of `O(log n)`. Merge sort performs `O(n)` combination work at each level, producing `O(n log n)` total time.

This is fundamentally different from subset generation. The two children represent smaller pieces of one original problem rather than mutually exclusive output choices.

The C++ implementation emphasizes ownership of recursive nodes through `std::unique_ptr`. This makes tree ownership explicit and prevents manual memory-management errors.

The Java implementation models nodes as domain objects and exposes children through immutable list views. This prevents callers from modifying the internal child collection accidentally.

## Python implementation

The Python file provides one coherent recursion-tree model through `TreeNode`.

`fibonacci_tree()` constructs a tree that mirrors overlapping Fibonacci calls. `subset_tree()` models include/exclude decisions. `binary_choice_tree()` generates a complete binary decision tree. `merge_sort_tree()` represents divide-and-conquer decomposition.

`print_tree()` renders the structure with Unicode tree connectors. `count_nodes()` measures the number of recursive calls represented by the structure, while `tree_height()` measures recursion depth.

The Python implementation also separates expensive recursive visualization from practical computation. `fibonacci_value()` uses an iterative recurrence, and `subsets()` performs actual subset generation without storing an unnecessary visualization tree.

Input validation rejects negative Fibonacci indices and invalid tree depths. Type checks prevent malformed input from silently producing misleading trees.

## JavaScript implementation

The JavaScript implementation uses a `TreeNode` class with mutable child registration. This fits JavaScript's object-oriented and event-driven programming model while keeping the recursion structure explicit.

The implementation is executable under Node.js without third-party dependencies.

The subset generator uses controlled mutation with `push()` and `pop()`. This avoids allocating a new array for every intermediate branch while preserving the selected-item state during depth-first traversal.

`mergeSortTree()` uses `slice()` to create independent left and right partitions. This makes the decomposition visible and avoids modifying the original input.

The iterative Fibonacci function uses destructuring assignment to update consecutive values without constructing the exponential call tree.

JavaScript's numeric type is sufficient for the small demonstration values, but large Fibonacci values eventually exceed the exact integer range of `Number`. Production implementations requiring exact large integer results should use `BigInt` and adjust validation and formatting accordingly.

## C++ implementation

The C++17 program treats the recursion tree as an owned object graph.

Each `TreeNode` owns its children through `std::unique_ptr`. This is appropriate because every child has exactly one parent in the represented recursion tree. Ownership is automatically released when the root is destroyed.

The implementation constructs four different trees:

- Fibonacci recursion with two different recursive indices;
- subset decisions through include and exclude branches;
- binary choices through zero and one branches;
- merge-sort decomposition through contiguous vector partitions.

The C++ implementation explicitly catches exceptions at the program boundary. Invalid negative recursion parameters are rejected before tree construction begins.

The divide-and-conquer example uses vectors for subproblem representation. This is easy to understand but creates copied sub-vectors. A high-performance merge-sort implementation would normally use iterator ranges or index boundaries to avoid repeated copying.

That distinction illustrates an important point about recursion trees: the tree describes algorithmic structure, but actual runtime cost also depends on what each node does.

## Java implementation

The Java program uses a domain-oriented `TreeNode` class and validates constructor inputs.

The `children()` method returns an immutable copy using `List.copyOf()`. The internal collection can therefore be controlled by the tree object rather than exposed directly to callers.

The subset model uses explicit include and exclude states. The binary-choice model stores the accumulated binary path, making every leaf directly interpretable as a complete sequence of choices.

The merge-sort model represents each subproblem with a list. Java's collection abstractions make the recursive decomposition easy to express, while `List.copyOf()` prevents accidental mutation of stored subproblem descriptions.

The program uses checked assumptions through runtime validation rather than accepting invalid negative depths or null domain values.

The Java version is particularly suited to an enterprise setting where recursion-tree structures may be part of a diagnostic or analysis service. For very deep recursion, iterative traversal or an explicit stack would be safer because JVM stack depth is finite.

## PostgreSQL implementation

The SQL file represents recursion trees relationally.

`recursion_trees` stores the high-level tree definition. `recursion_nodes` stores individual recursive states. The `parent_id` foreign key forms an adjacency-list representation:

`parent node -> child node`

This model is flexible because different recursion patterns can have different numbers of children.

The schema uses:

- primary keys for node and tree identity;
- foreign keys for parent and tree integrity;
- check constraints for valid depths and child positions;
- indexes on tree/depth and parent relationships;
- a PostgreSQL function for controlled node insertion;
- a recursive CTE for tree traversal;
- views for reusable structural reporting;
- transactional validation for an intentionally invalid depth.

The recursive CTE walks from root nodes toward descendants:

`root -> child -> grandchild -> ...`

This mirrors procedural recursive traversal while operating on relational rows.

The SQL implementation does not attempt to replace algorithm execution with database recursion. Its purpose is to persist, inspect, aggregate, and validate recursion-tree structures.

## Relationship between the four recursion patterns

The four patterns can be distinguished by what the branches mean.

| Property | Fibonacci | Subsets | Binary choices | Divide-and-conquer |
|---|---|---|---|---|
| Branch meaning | Alternative recursive subproblems | Include/exclude decision | Binary decision | Partition of one problem |
| Overlapping states | Yes | Usually no | Usually no | Usually no |
| Leaves | Base cases | Completed subsets | Completed assignments | Smallest subproblems |
| Typical depth | `O(n)` | `O(n)` | `O(d)` | `O(log n)` when balanced |
| Typical tree size | Exponential | `2^n` leaves | `2^d` leaves | Often `O(n)` nodes for binary splitting |
| Main concern | Repeated computation | Output-space explosion | Search-space explosion | Work per level |

The same visual shape does not imply the same algorithmic behavior. A binary-looking tree may represent duplicated work, exhaustive enumeration, or independent decomposition depending on what its edges mean.

## Complexity interpretation

A recursion tree is most useful when each node's work is combined with the tree structure.

For Fibonacci:

`T(n) = T(n-1) + T(n-2) + O(1)`

The repeated states create exponential growth.

For subset generation:

`T(n) = 2T(n-1) + O(1)`

There are `2^n` completed subsets, so exponential output is unavoidable when every subset must be materialized.

For binary choices:

`T(d) = 2T(d-1) + O(1)`

The number of complete assignments is `2^d`.

For balanced divide-and-conquer:

`T(n) = 2T(n/2) + combine(n)`

When `combine(n)` is `O(n)`, as in merge sort, the resulting complexity is `O(n log n)`.

The tree therefore provides a visual route from a recurrence relation to an asymptotic complexity estimate.

## Edge cases and practical limits

A recursion tree for an empty subset input has one leaf representing the empty subset.

A binary-choice tree with depth zero contains only its root and therefore has one complete choice.

Fibonacci inputs below zero are invalid under the mathematical definition used here.

A divide-and-conquer tree for an empty or singleton input terminates immediately because no further partition is required.

The principal scalability limitation is exponential tree growth. Visualization should therefore use small inputs for Fibonacci, subset enumeration, and binary choices. Increasing a depth from 20 to 30 does not merely make the output somewhat larger; it multiplies the number of leaves by 1,024.

Deep linear recursion can also exhaust the runtime call stack. Balanced divide-and-conquer trees generally have much smaller depth than linear recursive algorithms, but the actual implementation still needs to account for runtime stack limits.

## Debugging recursion with trees

When debugging a recursive algorithm, each node can be treated as a snapshot of the recursive state.

Useful information includes:

- current input size;
- current index;
- selected decisions;
- parent-child branch meaning;
- base-case condition;
- recursion depth;
- repeated states.

For Fibonacci, repeated labels immediately expose redundant work.

For subsets and binary choices, missing or duplicated branches indicate an incorrect decision path.

For divide-and-conquer, an incorrect split becomes visible when the child states do not cover the intended parent state or when a child fails to become smaller.

The tree is therefore a debugging model as well as a complexity-analysis model.

## Security and production considerations

Recursive-tree visualization should validate input sizes before constructing large structures. An externally supplied recursion depth can otherwise cause excessive CPU, memory consumption, or stack exhaustion.

Exponential algorithms should not accept unbounded user-controlled input merely because the individual recursive operation is inexpensive.

For persisted trees, the PostgreSQL adjacency-list model should be protected by transaction boundaries and constraints. Parent references should never be accepted without validating that the parent belongs to the same logical tree.

For production recursive algorithms, it is often better to calculate the result without materializing the complete recursion tree. The tree is primarily an analysis and diagnostic representation.

The key distinction is between the **recursive structure** and the **execution strategy**. A recursion tree explains how a recursive definition expands. Optimization techniques such as memoization, dynamic programming, iterative execution, pruning, and balanced partitioning determine how much of that theoretical expansion actually has to be performed.
