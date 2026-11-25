# Graph Assessment: BFS, DFS, Components, Cycles, Bipartite Graphs and Topological Sorting

## 1. Graph Representation and Assessment

A graph is a mathematical structure consisting of vertices and edges. It represents relationships, connections, dependencies, and movement between entities.

A graph is commonly represented as:

\[
G=(V,E)
\]

Where:

- \(V\) represents the set of vertices.
- \(E\) represents the set of edges.
- An edge establishes a relationship between two vertices.

The implementations use adjacency lists as their primary graph representation.

An adjacency list stores the neighbors of each vertex. For a sparse graph, this representation requires approximately \(O(V+E)\) space and supports efficient neighbor traversal.

### Directed and undirected graphs

| Property | Undirected graph | Directed graph |
|---|---|---|
| Edge representation | \(u-v\) | \(u\rightarrow v\) |
| Relationship | Bidirectional | Directional |
| Adjacency | Both vertices reference each other | Source references target |
| Common application | Social networks | Dependency systems |
| Cycle detection | Parent tracking | DFS recursion states |
| Components | Connected components | Strongly connected components |
| Bipartite checking | Standard two-coloring | Requires a defined underlying undirected graph |
| Topological sorting | Not applicable | Applicable to DAGs |

A directed graph can contain an edge from vertex A to vertex B without containing an edge from B to A.

An undirected edge represents a bidirectional relationship. The implementations prevent duplicate undirected edges by using canonical edge representations.

Self-loops are permitted. A self-loop immediately establishes a cycle and makes an undirected graph non-bipartite.

---

## 2. Breadth-First Search (BFS)

Breadth-First Search explores a graph level by level, beginning with a selected starting vertex.

It uses a FIFO queue.

### Mechanism

1. Mark the starting vertex as visited.
2. Insert it into the queue.
3. Remove the first vertex from the queue.
4. Examine its adjacent vertices.
5. Mark previously unvisited neighbors as visited.
6. Insert those neighbors into the queue.
7. Continue until the queue becomes empty.

The visited set prevents repeated processing and infinite traversal through cycles.

### Example

Consider the following undirected graph:

- 1 connects to 2 and 3.
- 2 connects to 4.
- 3 connects to 4.
- 5 connects to 6.

Starting BFS from vertex 1 produces:

`1 → 2 → 3 → 4`

Vertices 5 and 6 remain unreachable from vertex 1.

### Shortest-path property

For an unweighted graph, BFS calculates the minimum number of edges between the starting vertex and every reachable vertex.

For example:

`1 → 2 → 4`

has a distance of two edges.

The distance is calculated as:

\[
d(v)=d(parent(v))+1
\]

The parent map stores the predecessor of each discovered vertex. Following parent references backwards reconstructs a shortest path.

BFS does not guarantee minimum total weight in a weighted graph. Dijkstra's algorithm or another appropriate shortest-path algorithm is required for weighted graphs with non-negative weights.

### Applications

- Shortest paths in unweighted networks.
- Social network connection analysis.
- Web crawling.
- Network broadcasting.
- Level-order exploration.
- Minimum-hop communication routing.

---

## 3. Depth-First Search (DFS)

Depth-First Search explores one path as deeply as possible before returning to another available path.

It can use recursion or an explicit stack.

### Mechanism

1. Select a starting vertex.
2. Mark it as visited.
3. Examine an unvisited neighbor.
4. Continue exploring that neighbor.
5. Return when no unvisited neighbor remains.
6. Explore another available branch.

The Python, C++, and Java implementations use iterative DFS to avoid recursion-depth limitations. JavaScript uses an explicit stack as well.

### Example

For the graph:

`1 → {2, 3}`

`2 → {4}`

`3 → {4}`

A DFS beginning at vertex 1 may produce:

`1 → 2 → 4 → 3`

The exact ordering depends on neighbor insertion order.

### DFS applications

- Cycle detection.
- Graph connectivity analysis.
- Topological sorting.
- Dependency analysis.
- Maze exploration.
- Path existence.
- Strongly connected component algorithms.

DFS and BFS both visit reachable vertices, but their traversal orders and properties differ.

| Feature | BFS | DFS |
|---|---|---|
| Main data structure | Queue | Stack |
| Exploration | Level by level | Depth first |
| Unweighted shortest path | Yes | No |
| Cycle detection | Possible | Common approach |
| Connected components | Yes | Yes |
| Topological sorting | Kahn's algorithm uses BFS-like processing | DFS-based method also possible |

---

## 4. Connected Components

A connected component is a maximal group of vertices in which every vertex can reach every other vertex through undirected edges.

A disconnected graph contains multiple components.

### Example

Consider:

- Component 1: `1 - 2 - 3`
- Component 2: `4 - 5`
- Component 3: `6`

The graph has three connected components.

An isolated vertex is itself a connected component.

### Algorithm

The implementation repeatedly starts BFS from an unvisited vertex.

Every vertex reached during that traversal belongs to the same component.

After completing one traversal, the algorithm selects another unvisited vertex.

The process continues until every vertex has been visited.

### Complexity

\[
O(V+E)
\]

Each vertex is visited once, and each undirected edge is examined a constant number of times.

### Directed graph distinction

Ordinary connected components are defined for undirected graphs.

For directed graphs, two important concepts are:

- Weakly connected components: connectivity after ignoring edge directions.
- Strongly connected components: every vertex in a component is reachable from every other vertex following directed edges.

Kosaraju's and Tarjan's algorithms are commonly used for strongly connected component analysis.

The supplied implementations explicitly reject ordinary connected-component analysis on directed graphs rather than silently treating directed relationships as undirected.

---

## 5. Cycle Detection

A cycle is a path that starts and finishes at the same vertex without repeating intermediate vertices.

Cycle detection depends on whether the graph is directed or undirected.

### 5.1 Undirected cycle detection

The implementation uses DFS-style exploration with parent tracking.

During traversal:

- An unvisited neighbor becomes part of the DFS tree.
- The current vertex becomes the neighbor's parent.
- A previously visited neighbor that is not the parent indicates a cycle.

The parent condition is essential.

In an undirected graph, every ordinary edge appears in both adjacency lists. Without parent tracking, the traversal could incorrectly identify the reverse representation of the same edge as a cycle.

A self-loop is immediately detected because its neighbor is the current vertex rather than an unvisited vertex.

### 5.2 Directed cycle detection

The directed implementation uses three traversal states:

| State | Meaning |
|---|---|
| WHITE | Unvisited |
| GRAY | Currently being explored |
| BLACK | Completely processed |

A directed edge to a GRAY vertex identifies a back edge.

A back edge establishes a directed cycle.

An edge to a BLACK vertex does not independently establish a cycle.

This distinction is important in directed acyclic graphs containing cross edges or edges to previously completed subgraphs.

### Example

A directed cycle:

`1 → 2 → 3 → 1`

The edge `3 → 1` returns to a vertex that is still active in the DFS traversal.

Therefore, a cycle exists.

### Applications

- Circular dependencies.
- Deadlock analysis.
- Dependency validation.
- Build-system verification.
- Scheduling feasibility.
- Workflow validation.

---

## 6. Bipartite Graphs

A graph is bipartite if its vertices can be divided into two disjoint sets such that every edge connects vertices belonging to different sets.

The sets are often represented as:

\[
V=U\cup W
\]

With:

\[
U\cap W=\varnothing
\]

No edge may connect two vertices within the same set.

### Two-coloring algorithm

The implementation uses BFS.

Each starting vertex receives color 0.

Every adjacent uncolored vertex receives the opposite color.

If an adjacent vertex already has the same color as the current vertex, the graph is not bipartite.

The algorithm repeats for disconnected components.

### Example

Consider:

- Employees: A and B.
- Projects: X, Y and Z.
- A connects to X and Y.
- B connects to Y and Z.

The graph can be divided into:

`Set U = {A, B}`

`Set W = {X, Y, Z}`

The graph is bipartite.

### Odd-cycle property

An undirected graph is bipartite if and only if it contains no odd-length cycle.

Examples:

| Graph structure | Bipartite |
|---|---|
| A tree | Yes |
| A path | Yes |
| An even-length cycle | Yes |
| A triangle | No |
| A five-vertex cycle | No |
| A self-loop | No |

### Applications

- Employee-project allocation.
- Student-course assignment.
- Matching problems.
- Job allocation.
- Recommendation systems.
- Resource assignment.

The supplied algorithms check bipartiteness but do not implement maximum bipartite matching. Maximum matching requires an additional algorithm, such as Hopcroft-Karp.

---

## 7. Topological Sorting

Topological sorting produces a linear ordering of vertices in a directed acyclic graph (DAG).

For every directed edge:

\[
u\rightarrow v
\]

Vertex \(u\) must appear before vertex \(v\).

A topological ordering is possible only when the directed graph has no cycle.

### Applications

- Course prerequisite scheduling.
- Software build systems.
- Package installation.
- Task scheduling.
- Data pipeline execution.
- Project dependency management.

### 7.1 Kahn's algorithm

The Python, JavaScript, C++, and Java implementations use Kahn's algorithm.

The algorithm maintains the indegree of every vertex.

Indegree is the number of incoming edges.

Processing steps:

1. Calculate every vertex's indegree.
2. Insert all zero-indegree vertices into a queue.
3. Remove a vertex from the queue.
4. Add it to the ordering.
5. Decrease the indegree of its outgoing neighbors.
6. Insert any neighbor whose indegree becomes zero.
7. Continue until the queue is empty.

### Cycle detection through topological sorting

After processing, compare the number of processed vertices with the total number of vertices.

If:

\[
|Order|=|V|
\]

A complete topological ordering exists.

If:

\[
|Order|<|V|
\]

The graph contains a directed cycle.

### Example

Consider these dependencies:

- Programming before Data Structures.
- Data Structures before Algorithms.
- Algorithms before Graph Theory.
- Graph Theory before Advanced Algorithms.

A valid ordering is:

`Programming → Data Structures → Algorithms → Graph Theory → Advanced Algorithms`

Multiple valid topological orderings may exist when independent vertices are available simultaneously.

Topological sorting is not necessarily unique.

---

## 8. Algorithm Complexity

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.

| Algorithm | Time complexity | Auxiliary space |
|---|---:|---:|
| BFS | \(O(V+E)\) | \(O(V)\) |
| DFS | \(O(V+E)\) | \(O(V)\) |
| Connected components | \(O(V+E)\) | \(O(V)\) |
| Undirected cycle detection | \(O(V+E)\) | \(O(V)\) |
| Directed cycle detection | \(O(V+E)\) | \(O(V)\) |
| Bipartite checking | \(O(V+E)\) | \(O(V)\) |
| Topological sorting | \(O(V+E)\) | \(O(V)\) |
| BFS shortest path | \(O(V+E)\) | \(O(V)\) |

The adjacency-list representation requires:

\[
O(V+E)
\]

space.

For an undirected graph, every non-self-loop edge appears in two adjacency lists.

For a directed graph, each edge appears in the adjacency list of its source.

An adjacency matrix requires:

\[
O(V^2)
\]

space.

Adjacency matrices can be useful for dense graphs and constant-time edge existence checks, but they are less memory-efficient for sparse graphs.

---

## 9. Python Implementation

The Python file implements a reusable `Graph` class.

### Main mechanisms

- `GraphType` distinguishes directed and undirected graphs.
- `TraversalResult` stores traversal order, parents and distances.
- `TopologicalResult` reports ordering validity.
- `deque` provides efficient BFS queue operations.
- Sets prevent duplicate edges and repeated vertex processing.
- Iterative DFS avoids Python recursion-depth limitations.
- Exceptions reject unsupported graph operations.
- Assertions verify algorithm behavior.

### Implemented operations

| Method | Purpose |
|---|---|
| `add_edge()` | Add an edge |
| `remove_edge()` | Remove an edge |
| `bfs()` | Breadth-first traversal |
| `bfs_all()` | Traverse every reachable region |
| `dfs()` | Depth-first traversal |
| `connected_components()` | Identify undirected components |
| `has_undirected_cycle()` | Detect undirected cycles |
| `has_directed_cycle()` | Detect directed cycles |
| `is_bipartite()` | Perform two-coloring |
| `topological_sort()` | Produce a DAG ordering |
| `shortest_path()` | Recover a shortest unweighted path |

### Execution

Run the file using Python 3:

`python graph_assessment.py`

The script demonstrates both graph types and executes automated assertions.

---

## 10. JavaScript Implementation

The JavaScript file provides an event-driven graph assessment model.

It uses:

- `Map` for adjacency and traversal state.
- `Set` for vertex and edge tracking.
- Iterators for iterative directed DFS.
- Asynchronous generators for traversal events.
- Promises for asynchronous execution.
- `EventEmitter` for assessment notifications.

### Event-driven assessment

The `GraphAssessmentService` separates algorithm execution from application-level assessment history.

It supports events such as:

- `assessment-completed`
- `traversal-event`

An application can subscribe to these events to update a monitoring interface or record algorithm execution.

The asynchronous BFS generator emits individual vertex-visited events while yielding control to the Node.js event loop.

This is useful for applications that need observable traversal progress.

### Execution

`node graph_assessment.js`

No external npm packages are required.

---

## 11. C++17 Implementation

The C++ implementation uses a class-oriented graph engine.

### Engineering decisions

- `unordered_map` provides adjacency lookup.
- `unordered_set` tracks visited vertices.
- `queue` implements BFS.
- `vector` implements iterative DFS.
- `pair` stores parent relationships during undirected cycle detection.
- `string` canonicalizes edge identity.
- Structured bindings simplify result processing.
- Exceptions handle invalid graph operations.

The `GraphAssessment` class separates graph representation from algorithm execution.

The implementation supports edge insertion, removal, traversal, connectivity analysis, cycle detection, bipartite checking and topological sorting.

### Execution

Compile with:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic graph_assessment.cpp -o graph_assessment`

Run:

`./graph_assessment`

On Windows:

`graph_assessment.exe`

---

## 12. Java 17 Implementation

The Java implementation models graph assessment as an enterprise-oriented service.

### Domain types

| Type | Responsibility |
|---|---|
| `GraphType` | Graph direction |
| `Algorithm` | Assessment operation |
| `TraversalResult` | Traversal output |
| `TopologicalResult` | DAG ordering and cycle status |
| `BipartiteResult` | Two-coloring result |
| `AssessmentRecord` | Execution history |
| `GraphException` | Domain-specific failures |

Java records provide immutable result objects.

The `Graph` class maintains graph structure and validates operations.

The `AssessmentService` handles algorithm execution, assessment history and listener notification.

Listener exceptions are isolated so that an observer failure does not invalidate a completed algorithm.

### Execution

Compile:

`javac GraphAssessment.java`

Run:

`java GraphAssessment`

Java 17 is required.

---

## 13. PostgreSQL Implementation

The PostgreSQL script provides a relational graph-assessment model.

### Relational structure

The main relationship is:

`Graphs → Vertices → Edges → Assessment Runs → Traversal Results`

Additional tables record connected-component membership.

### Database objects

| Object | Purpose |
|---|---|
| `graphs` | Graph metadata and direction |
| `vertices` | Graph vertices |
| `edges` | Directed or undirected relationships |
| `assessment_runs` | Algorithm execution records |
| `traversal_results` | Vertex order, parent and distance |
| `component_results` | Component membership |
| `graph_statistics` | Graph-level aggregation |
| `graph_adjacency` | Normalized adjacency representation |
| `add_graph_edge()` | Validated edge insertion |
| `reachable_vertices()` | Recursive reachability |
| `execute_bfs()` | BFS distance assessment |
| `execute_topological_sort()` | Kahn-style dependency processing |

### Referential integrity

Composite foreign keys ensure that an edge's source and destination belong to the same graph.

Unique constraints prevent duplicate directed edges.

For undirected graphs, `add_graph_edge()` canonicalizes vertex identifiers so that the same relationship cannot be stored in both orientations.

The schema also validates:

- Graph names.
- Vertex labels.
- Edge weights.
- Assessment status.
- Execution timestamps.
- Traversal positions.
- Component identifiers.

### Recursive CTEs

Recursive Common Table Expressions support graph reachability.

The `reachable_vertices()` function begins from a specified vertex and repeatedly expands neighboring vertices.

A path array prevents a single recursive path from revisiting a vertex.

The minimum distance is obtained by grouping reachable vertices and selecting their minimum depth.

### Topological sorting

The `execute_topological_sort()` procedure implements Kahn's algorithm using a temporary working table.

It repeatedly selects an unprocessed zero-indegree vertex and reduces the indegrees of its outgoing neighbors.

Vertices that remain unprocessed indicate a directed cycle.

### Database execution

Run the complete script in a PostgreSQL database using:

`psql -U postgres -d graph_database -f graph_assessment.sql`

The script recreates the `graph_lab` schema and its demonstration data.

The recursive SQL queries intentionally target small assessment graphs. Enumerating simple paths can grow exponentially in dense graphs, so production-scale traversal should generally use an optimized graph-processing engine or an iterative application-level algorithm.

---

## 14. Important Algorithmic Distinctions

Several graph problems appear similar but require different definitions and validation rules.

| Problem | Required graph | Main technique | Important condition |
|---|---|---|---|
| BFS | Directed or undirected | Queue | Visits reachable vertices |
| DFS | Directed or undirected | Stack | Explores depth first |
| Connected components | Undirected | BFS or DFS | Covers disconnected regions |
| Strongly connected components | Directed | Tarjan or Kosaraju | Mutual directed reachability |
| Undirected cycle | Undirected | DFS and parent | Visited non-parent neighbor |
| Directed cycle | Directed | DFS states | Edge to active vertex |
| Bipartite checking | Undirected | BFS coloring | No odd-length cycle |
| Topological sorting | Directed | Indegree queue or DFS | Graph must be acyclic |

These distinctions matter when designing algorithm assessments. Applying an algorithm outside its mathematical assumptions can produce misleading results.

---

## 15. Edge Cases and Failure Conditions

The implementations include several important cases.

| Case | Expected behavior |
|---|---|
| Empty graph | Zero components |
| Single vertex | One component in an undirected graph |
| Isolated vertices | Each forms a separate component |
| Duplicate edge | Ignored |
| Unknown vertex | Validation error |
| Self-loop | Cycle detected |
| Triangle | Not bipartite |
| Even-length cycle | Bipartite |
| Disconnected graph | Every component is assessed |
| Directed back edge | Directed cycle detected |
| DAG | Valid topological ordering |
| Directed cyclic graph | Topological ordering rejected |
| Unreachable destination | No shortest path |
| Duplicate vertex | Construction rejected |

### Additional production considerations

- Traversal should operate on a consistent graph snapshot if concurrent modifications are possible.
- Large graphs may require memory-efficient adjacency structures.
- Recursive DFS can overflow the call stack.
- Traversal output can be nondeterministic when unordered containers determine neighbor order.
- Directed and undirected edge semantics must remain consistent across storage and algorithms.
- Weighted shortest paths require algorithms different from ordinary BFS.
- Graph databases and recursive SQL queries require workload-specific indexing and execution planning.

---

## 16. Practical Assessment Workflow

A mixed graph assessment can follow this sequence:

`Input Graph`

↓

`Validate Vertices and Edges`

↓

`Determine Directed or Undirected Structure`

↓

`Build Adjacency Representation`

↓

`Run BFS and DFS`

↓

`Assess Reachability and Components`

↓

`Detect Cycles`

↓

`Check Bipartiteness Where Applicable`

↓

`Perform Topological Sorting for Directed Graphs`

↓

`Validate Results and Report Complexity`

This sequence separates graph construction, traversal, structural analysis and dependency validation.

The five implementations demonstrate the same underlying graph concepts through different engineering approaches: Python provides a compact simulation engine, JavaScript provides event-driven assessment, C++17 provides an STL-based algorithm engine, Java 17 provides service-oriented domain modeling, and PostgreSQL provides relational graph storage and recursive query processing.
