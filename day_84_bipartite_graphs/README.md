# Bipartite Graphs: Two-Coloring, BFS, DFS, and Bipartite Condition

## 1. Problem Definition

A bipartite graph is an undirected graph whose vertex set can be divided into two disjoint groups such that every edge connects vertices belonging to different groups.

Let a graph be represented by:

\[
G=(V,E)
\]

where:

- \(V\) is the set of vertices.
- \(E\) is the set of undirected edges.

A graph is bipartite if there exists a partition:

\[
V=V_1\cup V_2
\]

such that:

\[
V_1\cap V_2=\varnothing
\]

and:

\[
\forall (u,v)\in E,\quad
(u\in V_1\land v\in V_2)
\lor
(u\in V_2\land v\in V_1)
\]

No edge may connect two vertices belonging to the same group.

The problem is also known as two-coloring because each vertex must receive one of two colors.

## 2. Two-Coloring

Two-coloring assigns one of two distinct colors to every vertex.

The colors are represented as:

| Color | Numeric representation |
|---|---:|
| Red | 0 |
| Blue | 1 |
| Uncolored | -1 |

For every edge connecting vertices \(u\) and \(v\), the following condition must hold:

\[
color(u)\neq color(v)
\]

The coloring process follows three rules:

1. Assign an initial color to an uncolored vertex.
2. Assign the opposite color to every uncolored neighbor.
3. Reject the graph if an edge connects vertices having the same color.

The opposite-color operation is:

\[
color(v)=1-color(u)
\]

For example, consider:

- Vertices: 0, 1, 2, 3
- Edges: (0,1), (1,2), (2,3), (3,0)

One valid partition is:

| Red | Blue |
|---|---|
| 0 | 1 |
| 2 | 3 |

Every edge crosses the two groups.

A valid coloring does not need to be unique. The colors of an entire connected component can be exchanged without affecting validity.

## 3. Bipartite Condition and Odd Cycles

A fundamental graph-theory result is:

**An undirected graph is bipartite if and only if it contains no odd-length cycle.**

A cycle is a closed path that begins and ends at the same vertex.

Its length is the number of edges in the cycle.

### Even cycle

Consider:

\[
0\rightarrow1\rightarrow2\rightarrow3\rightarrow0
\]

The cycle contains four edges.

Alternating colors produces:

\[
RED\rightarrow BLUE\rightarrow RED
\rightarrow BLUE\rightarrow RED
\]

The starting vertex and ending vertex have the same color, so the coloring is consistent.

### Odd cycle

Consider a triangle:

\[
0\rightarrow1\rightarrow2\rightarrow0
\]

The first two edges require:

- Vertex 0: Red
- Vertex 1: Blue
- Vertex 2: Red

The final edge connects two red vertices.

This violates the bipartite condition.

Therefore, a triangle is not bipartite.

### Important special cases

| Graph structure | Bipartite? | Reason |
|---|---|---|
| Empty graph | Yes | No conflicting edges |
| Isolated vertex | Yes | No neighbors |
| Tree | Yes | Contains no cycles |
| Even cycle | Yes | Alternating coloring is consistent |
| Odd cycle | No | Alternating coloring creates a conflict |
| Self-loop | No | Connects a vertex to itself |
| Parallel edges | Yes, if the underlying graph is bipartite | Repeated edges do not change coloring constraints |
| Disconnected graph | Depends on its components | Every component must be bipartite |

## 4. Breadth-First Search Coloring

Breadth-First Search explores vertices in increasing order of their distance from a starting vertex.

It uses a queue.

The algorithm processes every connected component independently.

### Algorithm

1. Initialize every vertex as uncolored.
2. Select an uncolored vertex.
3. Assign it red.
4. Insert it into a queue.
5. Remove a vertex from the queue.
6. Inspect every adjacent vertex.
7. Assign the opposite color to uncolored neighbors.
8. If an adjacent vertex already has the same color, report that the graph is not bipartite.
9. Continue until the queue is empty.
10. Repeat for any remaining uncolored vertices.

### BFS pseudocode

The essential operation is:

\[
color[v]=1-color[u]
\]

for an uncolored neighbor \(v\) of \(u\).

If:

\[
color[u]=color[v]
\]

the graph is not bipartite.

### Why BFS works

BFS explores a connected component in layers.

Every newly discovered vertex is reached through a parent vertex in the preceding layer. Assigning alternating colors ensures that parent-child edges connect opposite colors.

If a same-color edge is discovered, the two BFS paths from the component root, together with that edge, establish an odd cycle.

### Complexity

Using an adjacency-list representation:

- Time: \(O(V+E)\)
- Space: \(O(V+E)\), including graph storage.
- Auxiliary traversal space: \(O(V)\).

The implementation uses an array-based queue with a moving head index in JavaScript to avoid repeated array-element shifting.

## 5. Depth-First Search Coloring

Depth-First Search explores one path as deeply as possible before returning to another branch.

It can use recursion or an explicit stack.

The coloring rule is identical to BFS:

\[
color[v]=1-color[u]
\]

### Algorithm

1. Initialize all vertices as uncolored.
2. Select an uncolored vertex.
3. Assign red.
4. Push it onto a stack.
5. Pop a vertex.
6. Inspect its neighbors.
7. Assign opposite colors to uncolored neighbors.
8. Reject the graph if an adjacent vertex has the same color.
9. Continue until the stack becomes empty.
10. Process any remaining disconnected components.

### BFS versus DFS

| Property | BFS | DFS |
|---|---|---|
| Primary structure | Queue | Stack |
| Traversal pattern | Layer by layer | Deep exploration |
| Coloring rule | Alternate colors | Alternate colors |
| Detects odd cycles | Yes | Yes |
| Handles disconnected graphs | Yes | Yes |
| Time complexity | \(O(V+E)\) | \(O(V+E)\) |
| Auxiliary space | \(O(V)\) | \(O(V)\) |

Both algorithms correctly determine whether an undirected graph is bipartite.

The choice generally depends on the surrounding application rather than asymptotic performance.

The Python, C++, and Java implementations use iterative DFS to avoid recursion-depth or call-stack problems on large graphs.

## 6. Odd-Cycle Reconstruction

Detecting a coloring conflict establishes that the graph is not bipartite.

A useful extension is identifying an actual odd cycle.

During BFS or DFS, maintain:

- `parent[v]`: the vertex through which \(v\) was discovered.
- `depth[v]`: its depth in the traversal tree.

When an edge connects equally colored vertices \(u\) and \(v\):

1. Move the deeper vertex toward its parent.
2. Continue until both vertices reach the same depth.
3. Move both vertices upward until their lowest common ancestor is found.
4. Combine the two parent paths.
5. Include the conflicting edge to close the cycle.

The resulting sequence starts and ends at the same vertex.

For a self-loop, the detected cycle has length one.

The cycle reconstruction takes time proportional to the lengths of the two parent paths.

## 7. Disconnected Graphs

A graph is disconnected when at least one vertex cannot be reached from another vertex through existing edges.

A single BFS or DFS starting from vertex zero is insufficient for validating every component.

The correct implementation iterates through every vertex:

- If the vertex is already colored, skip it.
- Otherwise, begin a new traversal.
- Assign an initial color.
- Continue until that component has been fully processed.

The number of traversal roots equals the number of connected components.

For example:

\[
G_1=\{0,1,2\}
\]

\[
G_2=\{3,4\}
\]

\[
G_3=\{5\}
\]

These components must each be checked independently.

A graph is bipartite only when all its connected components are bipartite.

## 8. Python Implementation

The Python implementation uses an object-oriented adjacency-list model.

### Main components

| Component | Responsibility |
|---|---|
| `Color` | Represents red, blue, and uncolored states |
| `BipartiteResult` | Stores the analysis result |
| `Graph` | Manages vertices and undirected edges |
| `bfs_coloring()` | Performs BFS two-coloring |
| `dfs_coloring()` | Performs iterative DFS two-coloring |
| `_reconstruct_odd_cycle()` | Reconstructs a conflicting cycle |
| `run_tests()` | Validates important graph structures |

The `deque` collection provides efficient queue operations.

The result object separates graph analysis from output formatting.

The implementation validates vertex types and boundaries before inserting edges.

Parallel edges are accepted because they do not change the mathematical bipartite condition.

A self-loop is stored once and immediately creates a coloring conflict.

The implementation also checks that BFS and DFS agree on whether the graph is bipartite.

### Execution

Run the file using:

`python bipartite_graphs.py`

The demonstration evaluates an even cycle, an odd cycle, and a disconnected graph.

It also tests:

- Empty graphs.
- Isolated vertices.
- Trees.
- Self-loops.
- Parallel edges.
- Disconnected components.

## 9. JavaScript Implementation

The JavaScript implementation emphasizes event-driven graph management and state changes.

### Main components

| Component | Responsibility |
|---|---|
| `BipartiteGraph` | Encapsulates graph state |
| `Set` adjacency lists | Prevent duplicate edges |
| `on()` | Registers graph event listeners |
| `addEdge()` | Inserts an edge and updates the graph version |
| `removeEdge()` | Removes an existing edge |
| `analyzeBFS()` | Performs BFS validation |
| `analyzeDFS()` | Performs iterative DFS validation |
| `analyzeAsync()` | Provides Promise-based analysis |
| `snapshot()` | Provides an independent adjacency snapshot |

The graph uses private fields for adjacency data, event listeners, and version tracking.

A graph version increases whenever an edge is successfully added or removed.

This allows applications to distinguish results associated with different graph states.

Event listeners receive notifications when graph modifications occur.

Observer errors are isolated so that an exception in a listener does not invalidate an already completed graph update.

The analysis methods operate on adjacency snapshots, preventing a traversal from depending on later mutations to the original adjacency structure.

The implementation uses a moving queue-head index for BFS.

The `Set` structure also makes duplicate-edge insertion idempotent.

### Execution

Run:

`node bipartite_graphs.js`

The program creates an even cycle, adds an edge that introduces a triangle, detects the violation, and removes that edge to restore bipartiteness.

## 10. C++17 Implementation

The C++ implementation models a conflict-assignment system.

Vertices represent departments.

Edges represent pairs of departments that cannot share the same scheduling group.

The two colors represent two available assignment categories.

### Main components

| Component | Responsibility |
|---|---|
| `Color` | Represents the coloring state |
| `Algorithm` | Identifies BFS or DFS analysis |
| `AnalysisResult` | Stores coloring and conflict information |
| `BipartiteGraph` | Manages graph operations |
| `AssignmentGovernance` | Evaluates two-group scheduling eligibility |

The implementation uses:

- `vector<vector<int>>` for adjacency lists.
- `queue<int>` for BFS.
- `vector<int>` as an iterative DFS stack.
- STL algorithms for edge removal.
- Exceptions for invalid input and execution failures.

The assignment service separates graph representation from the decision to approve a two-group schedule.

A graph update can invalidate an earlier assignment.

For example, an even cycle can be assigned two colors. Introducing a diagonal edge may create a triangle, making the assignment impossible.

Removing the conflicting edge restores the original valid structure.

This demonstrates why eligibility must be evaluated against the current graph state.

### Execution

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic bipartite_graphs.cpp -o bipartite_graphs`

Run:

`./bipartite_graphs`

## 11. Java 17 Enterprise Implementation

The Java implementation uses explicit domain types and a policy-based assignment service.

### Main components

| Component | Responsibility |
|---|---|
| `Color` | Represents the two groups |
| `Algorithm` | Identifies the traversal method |
| `AssignmentStatus` | Represents approval or rejection |
| `Edge` | Models an undirected edge |
| `AnalysisResult` | Immutable graph-analysis result |
| `AssignmentDecision` | Immutable eligibility decision |
| `BipartiteGraph` | Graph operations and traversal |
| `AssignmentPolicy` | Defines the eligibility contract |
| `TwoSlotAssignmentPolicy` | Enforces two-group eligibility |
| `AssignmentService` | Coordinates policy evaluation |

Java records are used for immutable result and decision structures.

The policy interface separates the mathematical graph condition from the enterprise decision.

The service does not directly implement BFS. It delegates the decision to the configured policy.

This design allows different assignment policies to be introduced without changing graph traversal.

The implementation distinguishes:

- Graph validity.
- Coloring results.
- Assignment approval.
- Assignment rejection.
- The reason associated with a decision.

A rejected graph is not modified by the analysis operation.

The assignment service evaluates the current graph state whenever validation is requested.

### Execution

Compile:

`javac BipartiteGraphEnterprise.java`

Run:

`java BipartiteGraphEnterprise`

## 12. PostgreSQL Implementation

The PostgreSQL implementation stores graph structures and analysis results in relational tables.

### Relational model

| Table | Purpose |
|---|---|
| `graph` | Stores graph definitions |
| `graph_vertex` | Stores vertices belonging to graphs |
| `graph_edge` | Stores undirected edges |
| `graph_analysis` | Stores BFS analysis outcomes |
| `vertex_coloring` | Stores individual vertex colors |
| `assignment_policy` | Defines assignment requirements |
| `assignment_decision` | Stores eligibility decisions |

### Entity relationships

Graph

→ Graph vertices

→ Graph edges

→ Graph analysis

→ Vertex coloring

→ Assignment policy

→ Assignment decision

Composite foreign keys ensure that edges connect vertices belonging to the same graph.

The edge normalization trigger ensures that an undirected edge is stored in canonical order.

For example:

- Edge (1, 3)
- Edge (3, 1)

Both represent the same relationship.

The unique constraint prevents duplicate representations.

A self-loop such as (2, 2) remains valid as stored graph data but causes bipartite analysis to fail.

### BFS processing in PostgreSQL

The `analyze_bipartite_bfs()` function uses temporary tables to maintain traversal state.

| Temporary table | Purpose |
|---|---|
| `work_colors` | Stores colors, component identifiers, and parent relationships |
| `work_frontier` | Stores the current BFS layer |
| `work_next` | Stores newly discovered vertices |

The function processes all connected components.

When it discovers an uncolored neighbor, it assigns the opposite color and records the parent.

When an edge connects equally colored vertices, the graph is marked as non-bipartite.

The resulting analysis is stored in `graph_analysis`, while successful or partially completed coloring information is stored in `vertex_coloring`.

### Assignment eligibility

The `evaluate_assignment()` function evaluates a graph against a policy.

The two-group policy requires:

1. An enabled policy.
2. Exactly two required groups.
3. A successful bipartite analysis.

The decision is stored in `assignment_decision`.

An unsupported three-group policy is rejected by this particular two-coloring evaluation workflow.

A disabled policy is also rejected.

### Database integrity and performance

The implementation uses:

- Primary keys for entity identity.
- Foreign keys for graph membership.
- Unique constraints for undirected edges.
- Check constraints for valid vertex identifiers and colors.
- Triggers for edge normalization.
- Indexes for graph traversal and reporting.
- Views for analysis and assignment reporting.
- CTEs for selecting recent decisions.
- Transactions and savepoints for graph modifications.

The adjacency queries use indexes on both edge endpoints.

This is important because an undirected graph must retrieve neighbors through either endpoint.

### Execution

Run the SQL script in PostgreSQL using a client that supports standard PostgreSQL transactions and PL/pgSQL.

The script creates the schema, tables, functions, views, sample graphs, and analysis records.

The sample data includes:

- An even cycle.
- An odd cycle.
- A disconnected graph.
- A self-loop.
- A tree.

The transactional example temporarily adds a conflicting edge and rolls back the modification.

## 13. Correctness and Edge Cases

The algorithms rely on the invariant that every edge must connect opposite colors.

If a connected component can be consistently colored using two colors, that component is bipartite.

If any edge connects equal-colored vertices, the component is not bipartite.

The following cases require explicit attention:

| Case | Required behavior |
|---|---|
| Zero vertices | Return bipartite |
| One isolated vertex | Assign either color |
| Multiple components | Start a traversal for each uncolored component |
| Self-loop | Reject |
| Parallel edges | Accept if coloring constraints are satisfied |
| Even cycle | Accept |
| Odd cycle | Reject |
| Tree | Accept |
| Invalid vertex identifier | Reject graph modification |
| Empty adjacency list | Process without error |

A graph containing no edges is always bipartite because every vertex can independently belong to either group.

A tree is always bipartite because it contains no cycles.

The graph does not need to be connected to satisfy the bipartite condition.

## 14. Complexity Analysis

Let:

- \(V\) represent the number of vertices.
- \(E\) represent the number of undirected edges.

With adjacency lists, each vertex is processed at most once and each undirected edge is inspected at most twice.

| Operation | Time complexity |
|---|---|
| Graph initialization | \(O(V)\) |
| Edge insertion | \(O(1)\) amortized |
| BFS coloring | \(O(V+E)\) |
| DFS coloring | \(O(V+E)\) |
| Bipartite condition check | \(O(V+E)\) |
| Color-group extraction | \(O(V)\) |
| Odd-cycle reconstruction | \(O(V)\) worst case |
| Edge removal | Representation-dependent |

The graph representation requires:

\[
O(V+E)
\]

space.

The traversal requires:

\[
O(V)
\]

additional space for colors, parents, depths, and the queue or stack.

The PostgreSQL implementation uses relational lookups and temporary tables rather than a specialized in-memory graph engine. Its actual execution cost depends on indexes, table size, query planning, and procedural-loop overhead.

## 15. Practical Applications

Bipartite graphs are useful whenever relationships must connect two different categories.

### Scheduling and conflict assignment

Departments that cannot share a time slot are connected by edges.

A valid two-coloring determines whether two scheduling groups are sufficient.

### Examination timetabling

Examinations with common students can be represented as conflicting vertices.

An edge connects examinations that cannot occur simultaneously.

A bipartite graph can be scheduled using two time groups when every conflict is represented accurately.

### Network allocation

Two groups of network resources can be modeled as separate partitions.

Edges represent permitted relationships between the groups.

### Matching problems

A bipartite graph provides the mathematical foundation for matching algorithms such as maximum bipartite matching.

The two-coloring test determines whether a graph has the required two-part structure before applying matching algorithms.

### Task assignment

Tasks and workers can form separate vertex groups.

Edges can represent which worker is eligible to perform which task.

This is naturally modeled as a bipartite graph.

## 16. Limitations and Design Considerations

Two-coloring only determines whether two groups can satisfy all represented edge constraints.

It does not optimize group sizes.

It does not calculate a minimum number of colors for a general graph.

It does not determine a maximum matching.

It does not solve arbitrary scheduling optimization problems.

A graph that is not bipartite may still be colorable using three or more colors.

For example, a triangle requires three colors, even though it cannot be colored using only two.

The implementations assume undirected graphs. Directed graphs require an explicitly defined interpretation of their edges before applying the bipartite condition.

The C++, Java, Python, and JavaScript implementations use in-memory graph representations. The PostgreSQL implementation provides persistent relational storage and transactional analysis.

The PostgreSQL workflow uses procedural BFS and is intended for demonstrating relational graph processing rather than replacing a specialized graph-processing engine for very large networks.
