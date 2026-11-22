# Connected Components and Cycles in Graphs

## 1. Graph Representation

A graph is a mathematical structure consisting of vertices and edges.

- A vertex represents an entity or state.
- An edge represents a relationship or connection between two vertices.
- An adjacency list stores the neighboring vertices of each vertex.
- A path is a sequence of vertices connected by edges.
- A cycle is a path that returns to a previously visited vertex while following valid edges.

A graph can be directed or undirected.

| Property | Undirected graph | Directed graph |
|---|---|---|
| Edge representation | Two-way relationship | One-way relationship |
| Edge notation | `(u, v)` | `u → v` |
| Adjacency | Usually stored in both directions | Stored in the specified direction |
| Cycle detection | Parent tracking or DSU | DFS coloring or topological elimination |
| Common application | Networks and connectivity | Dependencies and workflows |

The implementations use adjacency lists because they provide efficient neighbor traversal and avoid allocating space for nonexistent edges.

For a graph with `V` vertices and `E` edges, adjacency-list storage requires `O(V + E)` space.

## 2. Connected Components

A connected component is a maximal set of vertices in an undirected graph where every pair of vertices is connected by a path.

A graph may contain several disconnected components.

Consider this graph:

- Component 1: `1 — 2 — 3`, with an additional edge between `3` and `1`.
- Component 2: `4 — 5`.
- Component 3: `6 — 7`.
- Component 4: isolated vertex `8`.

The component count is four.

An isolated vertex forms its own connected component because it is reachable from itself.

### 2.1 Component discovery using DFS

Depth-First Search explores a vertex and continues through its unvisited neighbors.

The component-discovery procedure is:

1. Initialize an empty visited set.
2. Iterate through every vertex.
3. If the vertex is unvisited, start a DFS traversal.
4. Mark each discovered vertex as visited.
5. Collect all vertices reached during that traversal.
6. Store the collected vertices as one component.
7. Continue until every vertex has been examined.

Each DFS traversal identifies exactly one connected component.

The implementations use iterative DFS rather than recursive DFS. This avoids recursion-depth failures on large graphs.

**Complexity**

- Time: `O(V + E)`.
- Auxiliary space: `O(V)` for visited vertices and traversal storage.
- Component storage: `O(V)`.

### 2.2 Why isolated vertices matter

Consider a graph with vertices `{1, 2, 3, 4}` and one edge `(1, 2)`.

The components are:

| Component | Vertices |
|---|---|
| 1 | `{1, 2}` |
| 2 | `{3}` |
| 3 | `{4}` |

The correct component count is three.

An implementation that discovers vertices only by traversing edges will miss isolated vertices. Every vertex must therefore be registered independently of edge insertion.

## 3. Cycle Detection in Undirected Graphs

An undirected cycle exists when a traversal can reach an already visited vertex through an edge other than the edge connecting the current vertex to its parent.

Consider:

`1 — 2 — 3 — 1`

The traversal can return to an already visited vertex without simply reversing its immediately preceding edge.

### 3.1 DFS with parent tracking

During DFS, each newly discovered vertex records its parent.

For a current vertex `u` and neighbor `v`:

- If `v` is unvisited, mark it visited and continue DFS.
- If `v` is already visited and `v` is not the parent of `u`, a cycle exists.
- If `v` is the parent of `u`, the edge is the reverse representation of the edge used to reach `u`.

The parent condition is essential.

In an undirected adjacency list, an edge between vertices `1` and `2` appears as:

- `1 → 2`
- `2 → 1`

Without parent tracking, the reverse representation would be incorrectly classified as a cycle.

The Python, C++, and Java implementations use iterative DFS with explicit traversal frames. This preserves the recursive DFS behavior without depending on the language's call-stack limit.

**Complexity**

- Time: `O(V + E)`.
- Auxiliary space: `O(V)`.

### 3.2 Disjoint Set Union

Disjoint Set Union, also called Union-Find, maintains a collection of disjoint sets.

It supports two fundamental operations:

- `find(x)`: identifies the representative of the set containing `x`.
- `union(x, y)`: combines the sets containing `x` and `y`.

Initially, every vertex belongs to its own set.

For every undirected edge `(u, v)`:

1. Find the representative of `u`.
2. Find the representative of `v`.
3. If both representatives are equal, the edge connects vertices already in the same component.
4. This additional connection creates a cycle.
5. Otherwise, combine their sets.

Two optimizations improve performance:

**Path compression**

During `find`, visited parent links are updated to point closer to the representative.

**Union by rank**

The smaller-rank tree is attached below the larger-rank tree.

The resulting amortized complexity is approximately `O(α(V))` per operation, where `α` is the inverse Ackermann function.

For an entire graph, the complexity is:

`O(V + E α(V))`

This is particularly useful when processing large edge collections or maintaining connectivity as edges arrive.

### 3.3 Self-loops and parallel edges

A self-loop is an edge from a vertex to itself.

`1 — 1`

A self-loop is a cycle because the traversal returns immediately to its starting vertex.

Parallel edges are multiple distinct edges connecting the same pair of vertices.

In a multigraph, two parallel edges form a cycle of length two.

The Union-Find implementations detect both cases.

The adjacency-list implementations preserve repeated edges, so the distinction is not lost.

A simple graph convention prohibits self-loops and parallel edges. A multigraph permits them. The examples intentionally support multigraph behavior.

## 4. Cycle Detection in Directed Graphs

Directed edges have an orientation.

An edge `u → v` permits movement from `u` to `v`, but does not imply an edge from `v` to `u`.

A directed cycle exists when a sequence of directed edges returns to an earlier vertex.

Example:

`1 → 2 → 3 → 4 → 2`

The cycle is:

`2 → 3 → 4 → 2`

Directed cycle detection requires different logic from undirected cycle detection.

An edge to a previously visited vertex does not necessarily indicate a cycle. That vertex might belong to a completed DFS branch.

Two complementary algorithms are implemented.

### 4.1 DFS with three-color marking

Three states describe the traversal status of each vertex.

| Color | Meaning |
|---|---|
| WHITE | Not visited |
| GRAY | Currently being explored |
| BLACK | Completely processed |

The algorithm works as follows:

1. Initialize every vertex as WHITE.
2. Select an unvisited vertex.
3. Mark it GRAY.
4. Explore its outgoing edges.
5. Mark a vertex GRAY when entering it.
6. Mark it BLACK when all its outgoing edges have been examined.
7. If an edge points to a GRAY vertex, a directed cycle exists.

An edge to a GRAY vertex is called a back edge.

It connects the current traversal path to a vertex already on that same path.

An edge to a BLACK vertex does not establish a cycle by itself.

The Python, JavaScript, C++, and Java implementations reconstruct a cycle using parent relationships when DFS finds a back edge.

For example:

`2 → 3 → 4 → 2`

The returned sequence includes the repeated starting vertex to make the cycle explicit.

**Complexity**

- Time: `O(V + E)`.
- Auxiliary space: `O(V)`.

### 4.2 Kahn's algorithm

Kahn's algorithm uses vertex indegrees to determine whether a directed graph can be completely processed in topological order.

The indegree of a vertex is the number of incoming edges.

A directed acyclic graph always has at least one vertex with indegree zero, unless the graph is empty.

The procedure is:

1. Calculate the indegree of every vertex.
2. Add all zero-indegree vertices to a queue.
3. Remove one vertex from the queue.
4. Count it as processed.
5. Decrease the indegree of each outgoing neighbor.
6. Add a neighbor to the queue when its indegree becomes zero.
7. Continue until the queue becomes empty.

After processing:

- If every vertex has been removed, the graph is acyclic.
- If some vertices remain, the graph contains a directed cycle.

Vertices downstream from a cycle may also remain unprocessed. Therefore, the remaining vertices are not necessarily all members of a cycle.

Kahn's algorithm is particularly useful for dependency validation, scheduling, and topological sorting.

**Complexity**

- Time: `O(V + E)`.
- Auxiliary space: `O(V)`.

### 4.3 DFS versus Kahn's algorithm

| Criterion | DFS coloring | Kahn's algorithm |
|---|---|---|
| Main mechanism | Traversal state | Indegree reduction |
| Cycle identification | Back edge | Unprocessed vertices |
| Explicit cycle path | Supported | Not directly produced |
| Topological ordering | Not produced by this implementation | Naturally supported |
| Time complexity | `O(V + E)` | `O(V + E)` |
| Common application | Structural cycle diagnosis | Dependency processing |

Both algorithms must agree on whether a directed graph contains a cycle.

The JavaScript and Java reporting services compare their results to detect inconsistencies.

## 5. Graph Modeling and Implementation Architecture

The five implementations use different engineering approaches while maintaining consistent graph semantics.

### 5.1 Python implementation

The Python script separates graph representation, data structures, and algorithms.

| Component | Responsibility |
|---|---|
| `Graph` | Maintains vertices and adjacency lists |
| `DisjointSetUnion` | Maintains connectivity representatives |
| `CycleResult` | Stores cycle detection results |
| `GraphAlgorithms` | Implements graph traversal and detection |
| `run_tests()` | Verifies expected behavior |
| `main()` | Executes demonstrations |

Python dictionaries provide adjacency storage. Sets provide constant-average-time membership checks. Deques support efficient queue operations.

The implementation provides three undirected cycle-detection methods and two directed methods.

It also distinguishes between cycle existence and cycle reconstruction.

### 5.2 JavaScript implementation

The JavaScript implementation uses `Map` and `Set` for graph state and traversal management.

Private class fields prevent callers from modifying adjacency storage directly.

The `GraphAnalysisPipeline` introduces event-driven reporting.

Its events include:

- `components`
- `cycle`
- `directedAnalysis`
- `error`

The analysis methods return Promises, making the reporting pipeline compatible with asynchronous application workflows.

Kahn's algorithm uses an array-backed queue and a moving head index rather than repeatedly calling `Array.shift()`. This avoids the repeated element-reindexing cost associated with removing the first array element.

The pipeline also compares DFS and Kahn results before publishing directed graph analysis.

### 5.3 C++17 implementation

The C++ program uses STL containers and explicit domain modeling.

| Structure | Purpose |
|---|---|
| `map` | Deterministic vertex iteration |
| `vector` | Adjacency storage |
| `unordered_set` | Visited tracking |
| `unordered_map` | Parent and color tracking |
| `queue` | BFS and Kahn processing |
| `DisjointSet` | Union-Find operations |
| `CycleResult` | Cycle analysis output |

The governance engine validates graph type before running algorithms.

Exceptions represent invalid operations, such as running directed cycle detection on an undirected graph.

The iterative traversal frames use a vertex and an adjacency index to preserve DFS processing order without recursive calls.

### 5.4 Java 17 implementation

The Java implementation uses an enterprise-oriented service structure.

- `Graph`: graph state and adjacency management.
- `GraphValidationService`: graph type and structural validation.
- `GraphAnalysisService`: graph algorithms.
- `GraphReportService`: presentation of analysis results.
- `DisjointSet`: connectivity management.

Records represent immutable analysis results.

The `ComponentReport` record validates its component count and copies component collections to prevent external mutation.

The use of separate validation, analysis, and reporting services keeps domain operations independent from output formatting.

## 6. PostgreSQL Graph Data Model

The SQL implementation represents graph structures through relational tables.

### 6.1 Tables

| Table | Purpose |
|---|---|
| `graphs` | Stores graph identity and graph type |
| `graph_vertices` | Stores registered vertices |
| `graph_edges` | Stores directed or canonical undirected edges |

The graph identifier is used throughout the relational model so multiple independent graphs can coexist in the same database.

The composite primary key on `graph_vertices` ensures that a vertex identifier is unique within its graph.

The edge table uses composite foreign keys to ensure that both endpoints belong to the same graph.

### 6.2 Undirected edge normalization

An undirected edge has no orientation.

Therefore, `(1, 2)` and `(2, 1)` represent the same edge.

The `add_graph_edge()` function normalizes undirected endpoints using `LEAST` and `GREATEST`.

Both representations become:

`(1, 2)`

A unique index prevents duplicate edge records.

The adjacency view expands each undirected edge into both traversal directions.

Self-loops are not duplicated.

Directed edges retain their original orientation.

### 6.3 Recursive CTEs

A recursive Common Table Expression allows PostgreSQL to perform graph traversal using SQL.

The `WITH RECURSIVE` mechanism contains:

- An initial query that establishes traversal starting points.
- A recursive query that discovers neighboring vertices.
- A termination condition that prevents revisiting vertices in the same traversal path.

The component-reporting view calculates reachable vertices from every starting vertex.

For undirected graphs, two vertices belong to the same component when each is reachable from the other.

The minimum reachable root identifier provides a deterministic component representative.

Isolated vertices are included because the initial query starts from every registered vertex.

### 6.4 SQL cycle detection

The database implements cycle checks using recursive traversal paths.

For undirected graphs, the algorithm excludes the immediately preceding parent vertex when checking revisits.

For directed graphs, a repeated vertex within the current traversal path identifies a directed cycle.

The SQL implementation is intended for educational and moderate-sized graph datasets.

It uses repeated recursive reachability operations rather than a specialized linear-time traversal engine. Consequently, its worst-case performance can be substantially higher than the in-memory DFS and Union-Find implementations.

For large production graphs, an application-side traversal engine or a dedicated graph-processing system may be more appropriate.

### 6.5 Integrity enforcement

The database enforces:

- Valid graph types.
- Nonempty graph names.
- Existing source vertices.
- Existing destination vertices.
- Nonnegative edge weights.
- Canonical ordering of undirected edges.
- Unique edge representations.

The edge-validation trigger also locks the corresponding graph row during edge insertion or modification.

The graph functions use exceptions to reject invalid graph types and missing graph identifiers.

The transaction groups schema creation, functions, triggers, views, and sample data into one atomic operation.

## 7. Realistic Graph Scenarios

### 7.1 Network connectivity

A communication network contains devices as vertices and communication links as undirected edges.

Connected components identify independent network groups.

An isolated device is a component containing one vertex.

Undirected cycle detection identifies redundant paths in the network.

Redundant paths may improve fault tolerance, although cycle existence alone does not establish that the network is resilient to every failure.

### 7.2 Dependency management

A software build system represents tasks as vertices and dependency relationships as directed edges.

For example:

`Compile → Test → Package → Deploy`

This is a directed acyclic graph.

If deployment indirectly becomes a prerequisite for compilation, a cycle appears:

`Compile → Test → Package → Deploy → Compile`

Such a dependency structure cannot be resolved through ordinary topological scheduling.

DFS can identify an explicit cycle path, while Kahn's algorithm determines whether all tasks can be topologically processed.

### 7.3 Organizational relationships

A directed graph can represent approval or reporting dependencies.

A cycle such as:

`Department A → Department B → Department C → Department A`

may indicate an invalid circular dependency.

Connected-component analysis is not interchangeable with directed reachability analysis. The component-count implementation deliberately accepts only undirected graphs.

## 8. Edge Cases and Correctness

The implementations test the following conditions.

| Scenario | Expected behavior |
|---|---|
| Empty graph | Zero connected components |
| One isolated vertex | One connected component |
| Multiple disconnected groups | One component per group |
| Undirected tree | No cycle |
| Undirected triangle | Cycle detected |
| Undirected self-loop | Cycle detected |
| Parallel undirected edges | Cycle detected in a multigraph |
| Directed chain | No cycle |
| Directed self-loop | Cycle detected |
| Directed back edge | Cycle detected |
| Directed acyclic dependencies | No cycle |
| Incorrect graph type | Validation error |
| Unknown vertex | Validation error |

A particularly important distinction concerns visited vertices.

For undirected graphs, an already visited neighbor other than the parent indicates a cycle.

For directed graphs, an edge to a currently active DFS vertex indicates a cycle. An edge to a completed vertex does not necessarily indicate one.

Using the wrong condition produces incorrect results.

## 9. Complexity Analysis

Let:

- `V` = number of vertices.
- `E` = number of edges.
- `α(V)` = inverse Ackermann function.

| Operation | Algorithm | Time complexity | Auxiliary space |
|---|---|---|---|
| Connected components | DFS | `O(V + E)` | `O(V)` |
| Undirected cycle | DFS | `O(V + E)` | `O(V)` |
| Undirected cycle | DSU | `O(V + E α(V))` | `O(V)` |
| Directed cycle | DFS coloring | `O(V + E)` | `O(V)` |
| Directed cycle | Kahn | `O(V + E)` | `O(V)` |

Adjacency-list storage requires `O(V + E)` memory.

For an undirected graph, every non-self-loop edge appears twice in adjacency storage. The DSU implementation processes only one representation of each edge.

For a directed graph, each edge is stored once.

The PostgreSQL recursive CTE approach maintains visited paths and performs repeated reachability traversals. Its resource requirements can be considerably greater than the linear-time in-memory algorithms.

## 10. Testing and Verification

Each source implementation contains executable checks.

The tests validate:

- Connected-component counts.
- Undirected cycle detection.
- Directed cycle detection.
- Acyclic graph behavior.
- Self-loop handling.
- Parallel-edge handling.
- Empty graph behavior.
- Agreement between alternative directed cycle algorithms.

Expected component count for the principal undirected example:

`4`

Expected result for the directed dependency example:

`Cycle detected`

Expected result for the directed acyclic example:

`No cycle`

The SQL script creates independent sample graphs and produces component, aggregation, and cycle reports.

## 11. Security and Production Considerations

Graph processing can involve untrusted input and large datasets.

Important safeguards include:

- Validate vertex identifiers before insertion.
- Enforce graph ownership and access permissions at the application or database layer.
- Use parameterized SQL statements rather than constructing SQL from user input.
- Apply graph-size and edge-count limits to prevent resource exhaustion.
- Avoid unrestricted recursive processing of attacker-controlled graphs.
- Use transaction boundaries for graph modifications.
- Preserve graph-type consistency.
- Avoid exposing internal graph data to unauthorized users.
- Monitor traversal duration and memory consumption.
- Use iterative traversal where recursion depth may become excessive.

The examples use integer vertex identifiers and in-memory adjacency lists. They do not implement authentication, multi-tenant authorization, distributed graph storage, or concurrent graph mutation protocols.

The SQL schema provides relational integrity, but application-level authorization must still control which users can create, inspect, or modify individual graphs.

For dynamic graph systems, component and cycle reports should be recalculated or incrementally maintained after relevant edge changes. A previously valid acyclic dependency graph may become cyclic after a single additional edge.
