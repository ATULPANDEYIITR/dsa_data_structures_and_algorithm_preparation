# Tree Diameter Practice Project

## Project scope

This project studies the diameter of an unweighted tree through executable implementations in Python, JavaScript, C++17, Java 17, and PostgreSQL.

A tree is a connected, undirected graph without cycles. Its edges represent relationships between nodes. A tree containing \(n\) nodes has exactly \(n-1\) edges.

The implementations use an organizational or infrastructure hierarchy as a practical model. Nodes represent offices, service locations, or organizational units. Edges represent direct relationships.

The main objectives are to calculate:

- The longest simple path between any two nodes.
- The height of a tree relative to a selected root.
- The longest path that contains a selected node.
- The diameter using independent algorithmic formulations.

All algorithms use **edge count** as their primary distance measurement. The number of nodes on a path is its edge count plus one.

## Core terminology

### Height

Height is defined relative to a selected root.

It is the maximum distance from that root to any node in the tree.

For a root \(r\):

\[
H(r)=\max_{v\in V} d(r,v)
\]

where \(d(r,v)\) is the number of edges on the unique path between \(r\) and \(v\).

A tree's height can change when the selected root changes. Its diameter does not.

A single-node tree has height zero because no edges are required to reach another node.

### Longest path

A path is a sequence of nodes connected by edges. A simple path cannot visit the same node more than once.

A tree has exactly one simple path between any two distinct nodes. This property makes tree diameter calculations simpler than longest-path calculations in general graphs.

### Diameter

The diameter is the maximum distance between any two nodes:

\[
D=\max_{u,v\in V}d(u,v)
\]

The two nodes achieving this maximum are diameter endpoints.

The diameter is independent of the selected root.

Two common measurement conventions are:

| Measurement | Definition |
|---|---|
| Diameter in edges | Number of edges on the longest path |
| Diameter in nodes | Number of nodes on the longest path |

For every non-empty tree:

\[
D_{\text{nodes}}=D_{\text{edges}}+1
\]

For a single-node tree, the diameter is zero edges and one node.

### Diameter through a node

The longest path through a node \(u\) is the maximum-length simple path that contains \(u\).

Remove \(u\) conceptually. Its neighboring components represent distinct directions in which a path can leave the node.

For each direction, calculate the maximum distance from \(u\) into that component.

Let the two largest branch distances be \(a\) and \(b\). Then:

\[
D(u)=a+b
\]

When only one branch exists, the second branch has value zero. The path can therefore start or end at \(u\).

When the node is isolated, its value is zero.

The tree diameter can also be expressed as:

\[
D=\max_{u\in V}D(u)
\]

This relationship is the basis of the bottom-up and rerooting implementations.

## Algorithmic formulations

### 1. Bottom-up dynamic programming

Root the tree at an arbitrary node.

For each node \(u\), define:

\[
down[u]=\max_{v\text{ in the subtree of }u}d(u,v)
\]

For a leaf:

\[
down[u]=0
\]

For an internal node:

\[
down[u]=\max_{c\in children(u)}(1+down[c])
\]

The two longest child branches can form a path through \(u\).

If their lengths are \(a\) and \(b\):

\[
through[u]=a+b
\]

The diameter is the maximum value among all nodes.

This formulation calculates the diameter in \(O(n)\) time because each node and edge is processed a constant number of times.

### 2. Rerooting dynamic programming

The bottom-up calculation only considers descendants. To calculate the longest path through every node, the implementation must also consider the direction toward the parent.

Define:

\[
up[u]
\]

as the greatest distance from \(u\) to a node outside its rooted subtree.

For a child \(v\) of \(u\):

\[
up[v]=1+\max(0,up[u],siblingBest)
\]

Here, `siblingBest` is the greatest downward branch from \(u\) that does not use \(v\).

For every node, combine:

- Its parent-side branch, if one exists.
- Its longest child branch.
- Its second-longest child branch.

The sum of the two greatest distinct branch distances is the longest path through that node.

Maintaining the two best child branches allows all parent-side values to be calculated in linear time.

### 3. Two-traversal diameter algorithm

The two-sweep algorithm uses breadth-first search.

1. Start from any node.
2. Find a node farthest from the starting node.
3. Start a second BFS from that farthest node.
4. The farthest node in the second traversal is the opposite diameter endpoint.
5. The second traversal's maximum distance is the diameter.

In an unweighted tree, BFS calculates shortest-path distances. Since a tree has a unique path between every pair of nodes, the second traversal finds a longest path.

The algorithm takes:

\[
O(n)
\]

time and \(O(n)\) auxiliary space.

It also provides the diameter endpoints and the actual path when parent information is retained during BFS.

### 4. Brute-force verification

For small trees, run BFS from every node and retain the greatest distance.

The running time is:

\[
O(n(n+m))
\]

For a tree, \(m=n-1\), giving:

\[
O(n^2)
\]

This is less efficient than the linear-time formulations. Its value is independent verification of optimized implementations during testing.

## Why the root and diameter are different

The height measures the greatest root-to-node distance. The diameter measures the greatest distance between any two nodes.

Consider:

    A
    |
    B
   / \
  C   D
       |
       E
       |
       F

When rooted at `A`, the height is three edges.

The diameter is four edges, from `C` to `F`.

Changing the root to `C` changes the height but does not change the diameter.

This distinction is important in rooted-tree problems, where the root is an algorithmic reference point rather than an inherent property of the undirected tree.

## Implementation details

### Python

The Python implementation uses a generic `Tree` class with hashable node identifiers.

Its main mechanisms are:

| Method | Responsibility |
|---|---|
| `_validate_connectivity_and_acyclicity()` | Reject cycles and disconnected structures |
| `_rooted_order()` | Create parent, depth, and traversal-order mappings |
| `_dynamic_programming_metrics()` | Calculate height, rerooted branches, and paths through nodes |
| `_bfs()` | Calculate distances and predecessor mappings |
| `diameter_two_sweep()` | Calculate diameter endpoints and reconstruct the longest path |
| `diameter_bruteforce()` | Check every possible BFS starting point |
| `analyze()` | Compare independent diameter results |

The implementation uses iterative traversals rather than recursive DFS. This avoids Python recursion-depth failures on long chain-shaped trees.

The `DiameterResult` data class stores the selected root, height, diameter, endpoints, path, and per-node longest-path values.

The tests cover:

- A chain.
- A star.
- A balanced tree.
- A single-node tree.
- Invalid edge counts.
- Cycles and duplicate edges.
- An unknown root.

### JavaScript

The JavaScript implementation uses Node.js standard-library capabilities.

`TreeIndex` extends `EventEmitter` and publishes events for validation and analysis completion.

Its engineering characteristics include:

- `Map` for node-to-neighbor relationships.
- `Set` for adjacency and duplicate detection.
- Iterative stack-based rooted traversal.
- BFS queue processing with a moving array index.
- Bottom-up and top-down dynamic programming passes.
- Independent two-sweep diameter verification.
- `Object.freeze()` for returned result objects and arrays.
- `analyzeAsync()` for Promise-based analysis.
- `AbortSignal` support for cancellation before analysis execution.

The asynchronous interface is useful when analysis is part of an event-driven Node.js service. The underlying tree calculations are synchronous and linear in the number of nodes.

### C++17

The C++ implementation models a campus network using `Site` and `Link` structures.

`CampusNetworkTree` stores sites in a vector and maintains an ID-to-index lookup using `unordered_map`.

Its construction validation uses a disjoint-set data structure.

The disjoint-set implementation uses:

- Path compression.
- Union by rank.

These mechanisms detect cycles and redundant connections during tree construction.

The analysis service uses vectors for parent, depth, downward height, upward height, and per-node path values. This avoids repeated dynamic allocation and provides efficient indexed access.

The implementation calculates the diameter with both dynamic programming and two BFS traversals. A mismatch produces an explicit error.

The example also verifies that invalid cyclic input is rejected.

### Java 17

The Java implementation models an enterprise hierarchy.

Its domain objects use Java records:

- `Site`
- `Link`
- `DiameterPolicy`
- `AnalysisResult`

The `TreeGraph` class owns the validated graph representation.

`DynamicProgrammingStrategy` calculates height and the longest path through every site. `TwoSweepStrategy` independently calculates the diameter and reconstructs the path.

`TreeAnalysisService` combines these calculations and verifies their agreement before returning a result.

The policy object supports two reporting conventions:

| Policy unit | Reported value |
|---|---|
| `EDGES` | Number of edges on the diameter |
| `NODES` | Number of nodes on the diameter |

A maximum-site policy limits the size of the hierarchy accepted by the service.

The implementation uses immutable collection copies for graph data and result objects. A custom exception identifies invalid tree structures and policy violations.

### PostgreSQL

The SQL implementation uses an adjacency-list relational model.

The main tables are:

| Table | Purpose |
|---|---|
| `tree_registry` | Stores tree metadata and validation state |
| `tree_node` | Stores nodes and their parent relationships |

Each node has one optional parent. A null parent identifies a root candidate.

The composite foreign key `(tree_id, parent_node_id)` ensures that a parent belongs to the same tree as its child.

Database mechanisms include:

- Primary and foreign keys.
- Unique constraints.
- Non-null and check constraints.
- Parent lookup indexes.
- A trigger to reject cycle-producing parent assignments.
- A trigger to prevent modification of validated trees.
- A recursive validation function.
- A procedure to validate and mark a tree.
- Recursive traversal functions.
- Reporting views.

`validate_tree()` checks for an existing tree, non-empty node data, exactly one root, and reachability from that root.

`compute_tree_diameter()` performs two farthest-node traversals. Each traversal builds an undirected adjacency relation from the stored parent relationships.

`longest_path_through_node()` starts a separate traversal for each neighbor of a selected node. It calculates the maximum distance in every direction and combines the two largest branch heights.

`tree_node_structure` reports child counts and leaf status. `tree_node_depth` reports root-relative depths. `tree_diameter_report` provides calculated results for validated trees.

The sample data contains two valid hierarchies and one deliberately invalid disconnected fixture. The invalid fixture demonstrates that individually valid node records do not necessarily form a valid tree.

## Worked example

The primary example is:

    Headquarters
    ├── North
    │   ├── North-East
    │   └── North-West
    └── South
        └── South-Central
            ├── South-East
            └── South-West

Rooting this hierarchy at `Headquarters` gives:

| Metric | Value |
|---|---:|
| Number of nodes | 8 |
| Number of edges | 7 |
| Height | 3 edges |
| Diameter | 5 edges |
| Nodes on a diameter path | 6 |
| Maximum path through `Headquarters` | 5 edges |

One valid diameter path is:

`North-East -> North -> Headquarters -> South -> South-Central -> South-East`

The path has six nodes and five edges.

The maximum path through `South` also has five edges. The maximum path through `North` has four edges.

The diameter is therefore five edges, regardless of whether the tree is rooted at `Headquarters`, `North-East`, or another node.

## Edge cases and validation rules

| Case | Expected behavior |
|---|---|
| Single node | Height 0, diameter 0 edges |
| Two connected nodes | Diameter 1 edge |
| Chain | Diameter equals the number of edges in the chain |
| Star with at least two leaves | Diameter 2 edges |
| Balanced tree | Diameter may pass through an internal node |
| Unknown root | Reject the analysis request |
| Unknown link endpoint | Reject the tree |
| Self-loop | Reject the tree |
| Duplicate edge | Reject the tree |
| Cycle | Reject the tree |
| Disconnected graph | Reject the tree |
| Empty input | Reject the tree |

A graph with \(n-1\) edges is not automatically a tree. It must also be connected and acyclic.

The implementations enforce these properties before performing diameter calculations.

## Complexity analysis

Let \(n\) be the number of nodes and \(m\) be the number of edges.

For a valid tree:

\[
m=n-1
\]

| Operation | Time complexity | Auxiliary space |
|---|---:|---:|
| Tree validation | \(O(n)\) | \(O(n)\) |
| Rooted traversal | \(O(n)\) | \(O(n)\) |
| Bottom-up dynamic programming | \(O(n)\) | \(O(n)\) |
| Rerooting calculation | \(O(n)\) | \(O(n)\) |
| One BFS traversal | \(O(n)\) | \(O(n)\) |
| Two-sweep diameter | \(O(n)\) | \(O(n)\) |
| Brute-force diameter | \(O(n^2)\) | \(O(n)\) per traversal |

The SQL implementation uses recursive CTEs and visited-path arrays. The number of database operations depends on the execution plan and the size of the tree. The indexes on `(tree_id, parent_node_id)` and `(tree_id)` support parent-child lookups and tree-scoped access.

## Practical considerations

### Choosing an algorithm

Use two BFS traversals when the primary requirement is the diameter and its endpoints.

Use bottom-up dynamic programming when the requirement includes subtree heights or the diameter value.

Use rerooting dynamic programming when the longest path through every node is required. Repeating a separate traversal for each node would be unnecessarily expensive.

Use brute-force BFS as a test oracle for small cases rather than as a production calculation.

### Tree validation

Tree-specific algorithms rely on the connected, acyclic structure.

Applying two-sweep BFS to an arbitrary graph does not generally guarantee its longest simple path. General graphs can contain cycles, multiple routes between nodes, and substantially harder longest-path problems.

Input validation is therefore part of the algorithm's correctness, not just data hygiene.

### Edge count versus node count

A frequent implementation error is mixing distance conventions.

The diameter of a single-node tree is zero edges, not one edge. Its diameter in nodes is one.

The height of a rooted tree also uses edge count in these implementations.

The reporting convention should be explicit wherever diameter values are stored, exported, or compared.

### Iterative traversal and deep trees

Recursive DFS can fail on very deep trees because of language or runtime call-stack limits.

The Python, C++, and Java implementations use iterative traversal structures for the main calculations. The JavaScript implementation uses iterative traversal as well.

PostgreSQL uses recursive CTEs. Very large trees require attention to database execution cost, memory consumption, and statement time limits.

### Data integrity and security

Node identifiers must be unique within a tree. Every edge must reference valid nodes in the same tree.

The PostgreSQL implementation enforces these conditions through relational constraints and triggers. It also prevents normal node modifications after a tree reaches the validated state.

Applications that accept externally supplied trees should validate input sizes and enforce request limits. Large inputs can consume significant memory even when the algorithm itself is linear.

### Correctness checks

The project compares two independent linear-time formulations:

\[
D_{\text{DP}}=D_{\text{two-sweep}}
\]

The brute-force implementation provides a third check on small trees.

This comparison helps detect errors in branch calculations, parent-side rerooting, path reconstruction, and distance conventions.
