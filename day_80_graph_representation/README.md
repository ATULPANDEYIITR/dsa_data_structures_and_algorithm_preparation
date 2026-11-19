# Graph Representation: Adjacency Matrix and Adjacency List

## 1. Graph Fundamentals

A graph is a non-linear data structure consisting of vertices and edges.

A graph is mathematically represented as:

\[
G = (V,E)
\]

Where:

- \(V\) is the set of vertices.
- \(E\) is the set of edges connecting vertices.

A vertex represents an entity. An edge represents a relationship between two entities.

For example, a transportation network can represent cities as vertices and roads as edges. An enterprise dependency network can represent software services as vertices and their dependencies as directed edges.

Graphs support relationships that cannot be represented naturally by simple linear structures such as arrays or linked lists.

### 1.1 Graph terminology

| Term | Meaning |
|---|---|
| Vertex | Individual graph element |
| Edge | Connection between two vertices |
| Adjacent vertices | Vertices connected by an edge |
| Degree | Number of incident edges |
| In-degree | Number of incoming directed edges |
| Out-degree | Number of outgoing directed edges |
| Path | Sequence of connected vertices |
| Cycle | Path that returns to its starting vertex |
| Connected graph | Every vertex is reachable from every other vertex in an undirected graph |
| Weighted graph | Graph whose edges contain numerical weights |
| Directed graph | Graph whose edges have a direction |
| Undirected graph | Graph whose edges have no direction |
| Density | Proportion of possible edges that exist |

For an undirected graph without self-loops, the maximum number of edges is:

\[
E_{\max} = \frac{V(V-1)}{2}
\]

For a directed graph without self-loops:

\[
E_{\max} = V(V-1)
\]

Graph density is:

\[
D = \frac{E}{E_{\max}}
\]

A density close to zero indicates a sparse graph. A density close to one indicates a dense graph.

## 2. Adjacency Matrix

An adjacency matrix represents a graph using a two-dimensional array.

For a graph containing \(V\) vertices, the matrix contains \(V\) rows and \(V\) columns.

The matrix entry \(A[i][j]\) represents the relationship between vertex \(i\) and vertex \(j\).

For an unweighted graph:

\[
A[i][j] =
\begin{cases}
1 & \text{if an edge exists}\\
0 & \text{otherwise}
\end{cases}
\]

For a weighted graph:

\[
A[i][j] =
\begin{cases}
w(i,j) & \text{if an edge exists}\\
\text{NULL} & \text{otherwise}
\end{cases}
\]

The implementations use `None`, `null`, `std::nullopt`, and SQL `NULL` to represent an absent edge.

This distinction is important because a weight of zero can represent a valid edge. Using zero as the absence marker would make zero-weight edges ambiguous.

### 2.1 Example

Consider the undirected weighted graph:

- A connects to B with weight 4.
- A connects to C with weight 2.
- B connects to C with weight 1.
- B connects to D with weight 5.

Its adjacency matrix is:

| Vertex | A | B | C | D |
|---|---:|---:|---:|---:|
| A | NULL | 4 | 2 | NULL |
| B | 4 | NULL | 1 | 5 |
| C | 2 | 1 | NULL | NULL |
| D | NULL | 5 | NULL | NULL |

For an undirected graph:

\[
A[i][j] = A[j][i]
\]

The matrix is symmetric.

For a directed graph, symmetry is not required. An edge from A to B does not automatically imply an edge from B to A.

### 2.2 Matrix characteristics

- Requires \(O(V^2)\) storage.
- Edge existence can be checked in \(O(1)\).
- Edge insertion takes \(O(1)\) after vertex indexing.
- Edge removal takes \(O(1)\) after vertex indexing.
- Finding all neighbors requires \(O(V)\).
- Iterating through all possible vertex pairs takes \(O(V^2)\).

An adjacency matrix is suitable when the graph is relatively dense or when frequent edge-existence queries are important.

Its main disadvantage is that it allocates storage for relationships that may not exist.

## 3. Adjacency List

An adjacency list represents a graph using a collection of vertices and their corresponding neighbors.

Each vertex stores its outgoing connections.

For a weighted graph, each connection also stores its weight.

### 3.1 Example

For the same undirected weighted graph:

| Vertex | Neighbors |
|---|---|
| A | B(4), C(2) |
| B | A(4), C(1), D(5) |
| C | A(2), B(1) |
| D | B(5) |

For an undirected graph, every ordinary edge is represented twice:

- Once in the source vertex's neighbor collection.
- Once in the target vertex's neighbor collection.

For a directed graph, only the outgoing connection is stored.

### 3.2 List characteristics

- Requires \(O(V+E)\) storage.
- Neighbor iteration takes \(O(degree(v))\).
- Edge insertion takes \(O(1)\) average time with a hash-based neighbor collection.
- Edge lookup takes \(O(degree(v))\) with a hash-based representation.
- Edge removal takes \(O(1)\) average time with a hash-based neighbor collection.
- BFS and DFS take \(O(V+E)\).

An adjacency list is generally more efficient for sparse graphs.

It stores existing relationships instead of allocating space for every possible relationship.

## 4. Memory Usage and Access Patterns

The two representations make different trade-offs.

### 4.1 Memory comparison

| Characteristic | Adjacency Matrix | Adjacency List |
|---|---|---|
| Storage complexity | \(O(V^2)\) | \(O(V+E)\) |
| Sparse graph | Inefficient | Efficient |
| Dense graph | Often competitive | Stores more relationship references |
| Vertex indexing | Array indices | Keys or vertex objects |
| Missing edges | Explicit empty cells | Absent entries |
| Weighted edges | Matrix values | Neighbor-weight pairs |
| Undirected edges | Two symmetric cells | Two neighbor entries |
| Dynamic vertex addition | Requires resizing | Usually straightforward |

For an undirected graph without self-loops, the number of stored adjacency entries is:

\[
2E
\]

For a directed graph, the number of stored adjacency entries is:

\[
E
\]

The matrix always contains:

\[
V^2
\]

cells.

### 4.2 Numerical example

Consider a graph with:

- 1,000 vertices.
- 2,000 undirected edges.

Adjacency matrix:

\[
1000^2 = 1,000,000
\]

The matrix requires one million cells.

Adjacency list:

\[
V+2E = 1000+4000=5000
\]

The adjacency list contains approximately five thousand structural entries, excluding object, key, and container overhead.

This example illustrates why adjacency lists are generally preferred for sparse networks.

The exact physical memory consumption depends on the programming language, data types, object layout, allocator, and container implementation.

### 4.3 Complexity comparison

| Operation | Adjacency Matrix | Adjacency List |
|---|---:|---:|
| Space | \(O(V^2)\) | \(O(V+E)\) |
| Check edge | \(O(1)\) | \(O(degree(v))\) |
| Add edge | \(O(1)\) | \(O(1)\) average |
| Remove edge | \(O(1)\) | \(O(1)\) average |
| Find neighbors | \(O(V)\) | \(O(degree(v))\) |
| Calculate out-degree | \(O(V)\) | \(O(1)\) with stored collections |
| BFS | \(O(V^2)\) | \(O(V+E)\) |
| DFS | \(O(V^2)\) | \(O(V+E)\) |

These complexities assume direct vertex indexing for the matrix and suitable hash-based neighbor collections for the list.

A sorted list, tree-based collection, or array-based neighbor collection can have different insertion and lookup costs.

### 4.4 Practical selection

Choose an adjacency matrix when:

- The graph is dense.
- Edge-existence checks are frequent.
- The vertex count is relatively stable.
- Predictable indexed access is important.
- Matrix-based graph algorithms are required.

Choose an adjacency list when:

- The graph is sparse.
- The vertex count can change.
- Traversal is frequent.
- Only existing neighbors need to be examined.
- Memory efficiency is important.

## 5. Directed and Undirected Graphs

The distinction between directed and undirected relationships changes the interpretation of the representation.

### Directed graph

An edge has a source and a destination.

\[
A \rightarrow B
\]

The reverse relationship does not automatically exist.

Examples include:

- Website navigation links.
- Software service dependencies.
- One-way transportation routes.
- Task dependency networks.

Directed graphs distinguish:

\[
InDegree(v)
\]

and:

\[
OutDegree(v)
\]

The total directed degree is:

\[
Degree(v)=InDegree(v)+OutDegree(v)
\]

### Undirected graph

An edge connects two vertices without a direction.

\[
A-B
\]

Both endpoints represent the same relationship.

Examples include:

- Mutual friendships.
- Two-way road connections.
- Undirected network connectivity.

An undirected adjacency matrix is symmetric.

An undirected adjacency list stores each non-self-loop relationship in both endpoint collections.

## 6. Weighted and Unweighted Graphs

An unweighted graph represents whether a relationship exists.

An edge normally has an implicit weight of one for counting purposes.

A weighted graph assigns a numerical value to each edge.

Weights can represent:

- Distance.
- Travel time.
- Cost.
- Network latency.
- Communication capacity.
- Relationship strength.

The implementations validate weights and distinguish an absent edge from an edge whose weight is zero.

Negative weights are allowed by the in-memory implementations because graph representation itself does not prohibit them. Specific algorithms may impose additional restrictions.

For example, Dijkstra's shortest-path algorithm requires non-negative edge weights.

## 7. Breadth-First Search

Breadth-First Search (BFS) explores a graph level by level.

It uses a queue.

The process is:

1. Select a starting vertex.
2. Mark it as visited.
3. Add it to the queue.
4. Remove the next vertex from the queue.
5. Examine its unvisited neighbors.
6. Mark those neighbors as visited and enqueue them.
7. Continue until the queue is empty.

A visited set prevents repeated processing and infinite traversal through cycles.

For an adjacency list:

\[
T(V,E)=O(V+E)
\]

BFS is useful for:

- Finding reachable vertices.
- Determining minimum edge-count distances in unweighted graphs.
- Exploring network connectivity.
- Identifying connected components.

The supplied implementations return traversal order rather than shortest weighted paths.

## 8. Depth-First Search

Depth-First Search (DFS) explores one branch before returning to another.

It can use recursion or an explicit stack.

The implementations use an explicit stack to avoid depending on the programming language's call-stack depth.

The process is:

1. Select a starting vertex.
2. Push it onto the stack.
3. Pop a vertex.
4. Skip it if already visited.
5. Mark it as visited.
6. Push its unvisited neighbors.
7. Continue until the stack is empty.

For an adjacency list:

\[
T(V,E)=O(V+E)
\]

DFS is useful for:

- Cycle detection.
- Connected-component exploration.
- Dependency analysis.
- Path exploration.
- Topological ordering when combined with suitable directed-graph logic.

Traversal order depends on neighbor iteration order. The implementations preserve or explicitly sort neighbor order where appropriate to make results reproducible.

## 9. Python Implementation

The Python implementation provides a reusable graph class with both representations maintained simultaneously.

### Main components

| Component | Responsibility |
|---|---|
| `Graph` | Graph state and operations |
| `Edge` | Immutable edge description |
| `Representation` | Representation identifiers |
| `VertexNotFoundError` | Invalid vertex handling |
| `add_vertex()` | Vertex insertion |
| `add_edge()` | Relationship insertion |
| `remove_edge()` | Relationship deletion |
| `remove_vertex()` | Vertex deletion |
| `bfs()` | Breadth-first traversal |
| `dfs()` | Depth-first traversal |
| `statistics()` | Structural graph statistics |
| `compare_representations()` | Complexity and memory comparison |

The implementation uses:

- Lists for matrix storage.
- Dictionaries for adjacency collections.
- Sets for traversal state.
- A deque for BFS.
- Dataclasses for edge modeling.
- Enumerations for representation types.

Both representations are maintained during mutation, making comparison straightforward.

The memory measurements use Python's `sys.getsizeof()` and are shallow container estimates rather than exact process memory measurements.

The demonstration also includes directed graph validation, edge deletion, vertex deletion, and assertions.

## 10. JavaScript Implementation

The JavaScript implementation emphasizes event-driven graph management.

### Main components

| Component | Responsibility |
|---|---|
| `Graph` | Graph operations and state |
| `Map` | Vertex indices and adjacency collections |
| `Set` | Visited vertex tracking |
| `EventEmitter` | Graph mutation events |
| `snapshot()` | Immutable structural snapshot |
| `bfsAsync()` | Batched asynchronous traversal |
| `statistics()` | Graph measurements |

The event-driven design publishes changes when vertices or edges are added or removed.

The asynchronous traversal processes vertices in batches and yields to the Node.js event loop.

It also records the graph version before traversal. If the graph changes during execution, the result reports that the traversal did not observe a consistent graph version.

This is an important distinction: yielding to the event loop does not provide transaction isolation or an immutable graph snapshot.

Applications requiring consistent concurrent reads should traverse an immutable snapshot or use explicit synchronization.

## 11. C++17 Implementation

The C++ implementation uses standard library containers and explicit domain validation.

### Main components

| Component | Responsibility |
|---|---|
| `Graph` | Graph representation and operations |
| `Edge` | Relationship data structure |
| `optional<double>` | Edge-presence representation |
| `unordered_map` | Vertex indexing |
| `unordered_set` | Visited-state tracking |
| `queue` | BFS |
| `vector` | Matrix and traversal storage |
| `GraphException` | Domain-specific errors |

`std::optional<double>` is particularly important because it distinguishes a missing edge from a valid edge with a zero weight.

The implementation rebuilds vertex indices after deleting a vertex because matrix positions must remain consistent with vertex identifiers.

The graph also provides a representation comparison using vertex count, edge count, adjacency entries, and density.

The use of hash-based collections provides average constant-time lookup, subject to hashing costs and collision behavior.

## 12. Java 17 Implementation

The Java implementation introduces an enterprise-oriented graph model.

Its domain types include:

- `GraphType`.
- `Edge`.
- `GraphSnapshot`.
- `GraphStatistics`.
- `GraphException`.

Java records provide immutable value-oriented representations for edges, snapshots, and statistics.

The graph uses:

- `ArrayList` for matrix rows.
- `LinkedHashMap` for deterministic vertex and neighbor iteration.
- `HashSet` for traversal tracking.
- `ArrayDeque` for queue and stack operations.
- `Consumer` for event listeners.
- `OptionalDouble` for optional edge weights.

### Enterprise dependency scenario

The implementation includes a directed service dependency network:

API → AUTH → DATABASE

API → CACHE → DATABASE

API → MESSAGE_QUEUE

This represents a simplified enterprise application in which services depend on other services.

BFS determines whether a dependency is reachable from a given service.

Reachability is not equivalent to dependency ordering or failure propagation analysis. Those tasks require additional graph algorithms and domain rules.

The immutable snapshot prevents consumers from directly modifying the returned vertex and edge collections.

## 13. PostgreSQL Implementation

The PostgreSQL implementation models graphs as relational entities.

### Relational structure

| Table | Purpose |
|---|---|
| `graphs` | Graph configuration |
| `vertices` | Graph vertices |
| `edges` | Graph relationships |

The relationship is:

\[
Graphs \rightarrow Vertices \rightarrow Edges
\]

Each vertex belongs to exactly one graph.

Each edge identifies:

- Its graph.
- Its source vertex.
- Its target vertex.
- Its numerical weight.

Foreign keys enforce endpoint existence.

Unique constraints prevent duplicate directed endpoint pairs.

A trigger validates that both endpoints belong to the same graph and enforces the weight-mode and undirected-edge conventions.

### 13.1 Adjacency list query

The `adjacency_list` view aggregates outgoing relationships into JSONB arrays.

This is useful when an application needs each vertex and its immediate neighbors.

The view avoids storing a separate adjacency-list copy that could become inconsistent with the underlying edge table.

### 13.2 Adjacency matrix query

The `get_adjacency_matrix()` function uses a cross join between the graph's source and target vertices.

A left join identifies whether an edge exists.

This returns every possible vertex pair, including pairs without edges.

Consequently, the result contains:

\[
V^2
\]

rows for a graph with \(V\) vertices.

This operation is appropriate for small or moderate graphs but can become expensive for large vertex counts.

### 13.3 Breadth-first search

The `bfs()` function uses a recursive CTE.

It tracks:

- Current vertex.
- Traversal depth.
- Previously visited vertex identifiers.

The visited array prevents cycles from causing unbounded recursion.

For undirected graphs, the function considers relationships in both directions. For directed graphs, it follows outgoing edges only.

The returned depth represents the minimum number of edges from the starting vertex.

This implementation favors clarity and database-side traversal over a specialized high-performance graph execution engine.

### 13.4 Integrity and transactions

The SQL script demonstrates:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Indexes.
- Views.
- Functions.
- Triggers.
- Recursive CTEs.
- Transactional mutations.
- Exception handling.

The sample transaction inserts an edge and verifies its presence before committing.

The schema is designed to prevent cross-graph relationships and inconsistent undirected edge ordering.

The schema does not implement every possible graph constraint, such as automatic cascading updates to the graph's direction or weight mode. Changes to those configuration fields should be controlled through an application-level migration or administrative workflow.

## 14. Important Implementation Distinctions

The five implementations share the same underlying graph concepts but make different engineering decisions.

| Language | Main design emphasis |
|---|---|
| Python | Readable graph operations and memory estimation |
| JavaScript | Event-driven mutation and asynchronous traversal |
| C++17 | Explicit storage control and STL-based graph operations |
| Java 17 | Enterprise domain modeling and immutable snapshots |
| PostgreSQL | Relational integrity and database-side graph queries |

The adjacency matrix and adjacency list are two representations of the same logical graph.

They should not be treated as two independent graph definitions.

When both are maintained simultaneously, every mutation must update both structures correctly.

For large production graphs, maintaining one authoritative representation and deriving other representations when needed may be more appropriate.

## 15. Edge Cases and Failure Conditions

The implementations address several important cases.

| Case | Expected behavior |
|---|---|
| Empty vertex name | Reject insertion |
| Duplicate vertex | Do not create another vertex |
| Unknown source | Reject edge insertion |
| Unknown target | Reject edge insertion |
| Duplicate edge | Replace existing weight in in-memory implementations |
| Self-loop | Support as an edge |
| Zero-weight edge | Distinguish from missing edge |
| Negative weight | Allow in the representation |
| Non-finite weight | Reject |
| Missing edge removal | Return false or equivalent |
| Vertex removal | Remove associated relationships |
| Directed reverse edge | Treat as a separate relationship |
| Undirected reverse edge | Represent the same relationship |
| Cyclic graph | Prevent repeated traversal |
| Disconnected graph | Traverse only the reachable component |
| Empty graph | Return zero structural statistics |

The SQL implementation uses a canonical endpoint order for undirected edges and represents each undirected relationship once in the `edges` table.

The in-memory implementations instead store both directions in their adjacency structures.

This is a deliberate storage distinction rather than a difference in graph meaning.

## 16. Performance and Production Considerations

### 16.1 Matrix resizing

Adding a vertex to a conventional adjacency matrix requires expanding every existing row and adding a new row.

This involves \(O(V)\) work for each vertex insertion.

Removing a vertex also requires deleting its corresponding row and column.

Frequent vertex changes can therefore make matrix-based graph storage expensive.

### 16.2 Adjacency-list mutation

Adjacency lists are more flexible for changing graph structures.

However, performance depends on the underlying collection.

Hash-based collections provide average constant-time insertion and lookup. Tree-based collections provide ordered iteration but generally require logarithmic-time operations.

### 16.3 Cache behavior

An adjacency matrix uses contiguous row storage in typical array implementations.

This can improve locality when scanning matrix rows.

Adjacency lists may require following references between separate objects or containers. This can increase memory overhead and reduce locality.

The actual performance depends on the language runtime and memory layout.

### 16.4 Large graphs

For very large graphs:

- Avoid materializing a full adjacency matrix unless necessary.
- Use compact integer vertex identifiers.
- Consider compressed sparse row storage for static sparse graphs.
- Use streaming or batched traversal when appropriate.
- Avoid unnecessary copying of complete graph structures.
- Maintain indexes for frequently queried relationships.
- Monitor memory consumption and traversal latency.

### 16.5 Security

Graph systems can process untrusted vertex identifiers and relationship data.

Production systems should:

- Validate vertex identifiers.
- Restrict graph modification permissions.
- Apply input-size limits.
- Validate numeric weights.
- Use parameterized database queries.
- Prevent unauthorized cross-graph relationships.
- Apply transaction boundaries to multi-step mutations.
- Control resource-intensive traversal requests.
- Avoid exposing internal database identifiers unnecessarily.

## 17. Execution

| File | Runtime |
|---|---|
| Python | Python 3.10 or newer |
| JavaScript | Node.js 18 or newer |
| C++17 | C++ compiler supporting C++17 |
| Java | Java 17 |
| PostgreSQL | PostgreSQL 15 or newer |

The Python, JavaScript, C++17, and Java 17 implementations include executable demonstrations and validation tests.

The PostgreSQL script creates the `graph_lab` schema and its database objects, inserts sample graph data, executes retrieval and analysis queries, demonstrates BFS, and performs transactional graph mutation.

The central engineering decision is the relationship between graph density, storage cost, and access frequency. Adjacency matrices favor direct edge access, while adjacency lists favor efficient storage and traversal of sparse networks.
