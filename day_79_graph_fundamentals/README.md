**# Graph Fundamentals

## 1. Introduction

A graph is a non-linear data structure used to represent relationships between objects.

A graph consists of two fundamental components:

- **Vertex:** An individual object or entity in a graph.
- **Edge:** A connection between two vertices.

The mathematical representation is:

\[
G = (V,E)
\]

Where:

- \(G\) represents the graph.
- \(V\) represents the set of vertices.
- \(E\) represents the set of edges.

Consider a transportation network containing five cities connected by roads.

The cities are vertices, while the roads are edges.

A graph can represent social networks, computer networks, transportation systems, application dependencies, communication systems, and many other real-world relationships.

## 2. Vertex

A vertex, also called a node, represents an individual entity.

For example:

\[
V = \{A,B,C,D,E\}
\]

This graph contains five vertices.

Each vertex has an identity and can participate in one or more relationships.

A vertex does not necessarily need to be connected to another vertex.

An isolated vertex is a vertex that has no incident edges.

For example:

\[
V = \{A,B,C,D\}
\]

\[
E = \{(A,B),(B,C)\}
\]

Vertex D is isolated.

### Implementation

| Language | Representation |
|---|---|
| Python | Dictionary keys |
| JavaScript | Map keys |
| C++17 | Map keys |
| Java 17 | Map keys |
| PostgreSQL | Records in the vertices table |

The implementations maintain vertices independently of edges. This distinction allows isolated vertices to exist.

## 3. Edge

An edge represents a relationship between two vertices.

An edge connecting A and B can be represented as:

\[
e = (A,B)
\]

A graph containing three vertices and two edges is:

\[
V = \{A,B,C\}
\]

\[
E = \{(A,B),(B,C)\}
\]

Edges can be represented using ordered or unordered pairs, depending on the graph type.

An edge may also have an associated weight.

### Edge properties

- Source vertex
- Target vertex
- Weight, when applicable
- Direction, determined by the graph type

The source and target have distinct meanings in directed graphs.

In an undirected graph, the relationship is symmetric.

### Duplicate edges

The implementations use a simple graph model.

A pair of vertices cannot have multiple independently stored edges between them.

Adding an existing edge updates its weight in weighted implementations rather than increasing the edge count.

Self-loops are structurally possible, although their treatment depends on the application.

## 4. Directed Graph

A directed graph, also called a digraph, contains edges with a specified direction.

An edge from A to B is written as:

\[
A \rightarrow B
\]

It does not automatically imply:

\[
B \rightarrow A
\]

Example:

\[
V = \{A,B,C\}
\]

\[
E = \{(A,B),(A,C),(C,B)\}
\]

The relationships are:

- A points to B.
- A points to C.
- C points to B.

This structure is useful when relationships have a direction.

Practical examples include:

- Website hyperlinks
- Application dependencies
- One-way roads
- Task dependencies
- Data-flow relationships
- Communication between services

### Directed graph degree

Directed graphs have two separate degree measurements.

**In-degree**

The in-degree of a vertex is the number of incoming edges.

\[
d^{-}(v) =
\text{Number of incoming edges}
\]

**Out-degree**

The out-degree of a vertex is the number of outgoing edges.

\[
d^{+}(v) =
\text{Number of outgoing edges}
\]

For the example:

\[
A \rightarrow B,\quad
A \rightarrow C,\quad
C \rightarrow B
\]

| Vertex | In-degree | Out-degree |
|---|---:|---:|
| A | 0 | 2 |
| B | 2 | 0 |
| C | 1 | 1 |

An important property is:

\[
\sum_{v \in V} d^{-}(v)
=
\sum_{v \in V} d^{+}(v)
=
|E|
\]

The total in-degree and total out-degree both equal the number of directed edges.

## 5. Undirected Graph

An undirected graph contains edges without direction.

An edge between A and B is represented as:

\[
A-B
\]

The relationship works in both directions.

Therefore:

\[
(A,B) = (B,A)
\]

Example:

\[
V = \{A,B,C,D\}
\]

\[
E = \{\{A,B\},\{A,C\},\{B,D\}\}
\]

Practical examples include:

- Mutual social relationships
- Two-way roads
- Physical network connections
- Collaboration relationships
- Undirected communication links

### Undirected graph properties

Each edge connects two vertices.

An edge contributes one degree to each endpoint.

Therefore:

\[
\sum_{v \in V} d(v) = 2|E|
\]

This is known as the handshaking lemma.

For a simple undirected graph, a vertex with no incident edges has degree zero.

## 6. Weighted Graph

A weighted graph associates a numerical value with an edge.

The weight represents a measurable property of a relationship.

Examples include:

- Distance
- Travel time
- Transportation cost
- Network latency
- Communication cost
- Financial transaction cost

Example:

\[
A \xrightarrow{4} B
\]

\[
A \xrightarrow{2} C
\]

\[
C \xrightarrow{1} B
\]

The edge between A and B has weight 4.

The edge between A and C has weight 2.

The edge between C and B has weight 1.

A weighted graph can be directed or undirected.

### Weighted versus unweighted graphs

| Property | Weighted | Unweighted |
|---|---|---|
| Edge value | Numerical weight | Connection only |
| Edge representation | Source, target, weight | Source and target |
| Typical application | Transportation | Basic relationships |
| Shortest path | Minimum total weight | Minimum number of edges |
| Adjacency matrix | Stores weights | Stores connection indicators |

A weighted graph may contain negative weights, depending on the application.

The Dijkstra implementations in the source files explicitly reject negative edge weights.

This restriction is necessary because Dijkstra's algorithm assumes non-negative weights.

## 7. Degree

Degree describes the number of edges associated with a vertex.

For an undirected graph:

\[
d(v) = \text{Number of incident edges}
\]

Consider:

\[
A-B
\]

\[
A-C
\]

\[
B-D
\]

\[
C-D
\]

\[
D-E
\]

The degree values are:

| Vertex | Degree |
|---|---:|
| A | 2 |
| B | 2 |
| C | 2 |
| D | 3 |
| E | 1 |

Vertex D has the highest degree.

Vertex E has degree one.

A vertex with degree zero is isolated.

### Degree distribution

Degree distribution describes how vertex degrees are distributed across a graph.

It can help identify:

- Highly connected vertices
- Isolated vertices
- Network hubs
- Uneven connectivity
- Potentially important infrastructure nodes

The average degree of an undirected graph is:

\[
\bar{d} = \frac{2|E|}{|V|}
\]

For directed graphs:

\[
\bar{d}_{in} = \frac{|E|}{|V|}
\]

\[
\bar{d}_{out} = \frac{|E|}{|V|}
\]

## 8. Graph Representation

Graphs can be represented using different data structures.

The five implementations use adjacency lists as their primary representation.

### Adjacency List

An adjacency list stores the neighboring vertices of each vertex.

Example:

- A: B, C
- B: A, D
- C: A, D
- D: B, C, E
- E: D

For weighted graphs, each neighbor also stores the corresponding edge weight.

**Advantages**

- Efficient representation of sparse graphs.
- Efficient neighbor retrieval.
- Memory proportional to vertices and edges.
- Suitable for BFS and DFS.

**Limitations**

- Checking whether two arbitrary vertices are connected may require searching the adjacency list.
- Less suitable for dense graphs requiring frequent arbitrary edge lookups.

### Adjacency Matrix

An adjacency matrix represents graph connections using a two-dimensional matrix.

For an unweighted undirected graph:

| | A | B | C |
|---|---:|---:|---:|
| A | 0 | 1 | 1 |
| B | 1 | 0 | 1 |
| C | 1 | 1 | 0 |

A value of 1 indicates an edge.

A value of 0 indicates no edge.

For weighted graphs, matrix cells contain the edge weight. A separate absence marker is needed to distinguish a missing edge from a zero-weight edge.

**Advantages**

- Constant-time edge lookup.
- Simple mathematical representation.
- Suitable for dense graphs.

**Limitations**

- Requires quadratic memory.
- Expensive to expand when vertices are frequently added.

### Representation comparison

| Property | Adjacency List | Adjacency Matrix |
|---|---|---|
| Storage | \(O(V+E)\) | \(O(V^2)\) |
| Neighbor retrieval | \(O(degree(v))\) | \(O(V)\) |
| Edge lookup | Usually \(O(degree(v))\) | \(O(1)\) |
| Best suited for | Sparse graphs | Dense graphs |

## 9. Graph Traversal

Graph traversal is the process of visiting vertices according to a defined search strategy.

The two fundamental traversal algorithms are Breadth-First Search and Depth-First Search.

### Breadth-First Search

Breadth-First Search, or BFS, explores vertices level by level.

It uses a queue.

Example:

\[
A-B,\quad A-C,\quad B-D,\quad C-E
\]

Starting from A, a possible BFS order is:

\[
A,B,C,D,E
\]

The traversal follows these operations:

1. Insert the starting vertex into a queue.
2. Mark it as visited.
3. Remove the next vertex from the queue.
4. Visit its unvisited neighbors.
5. Insert those neighbors into the queue.
6. Continue until the queue becomes empty.

**Applications**

- Shortest paths in unweighted graphs
- Network reachability
- Social network exploration
- Level-order exploration
- Minimum-hop routing

Complexity using adjacency lists:

\[
O(V+E)
\]

### Depth-First Search

Depth-First Search, or DFS, explores one path as deeply as possible before backtracking.

It uses a stack or recursion.

Example:

\[
A-B,\quad A-C,\quad B-D,\quad C-E
\]

A possible DFS order is:

\[
A,B,D,C,E
\]

The exact order depends on neighbor ordering.

DFS is useful for:

- Cycle detection
- Connected components
- Dependency analysis
- Reachability
- Structural graph analysis

Complexity:

\[
O(V+E)
\]

Both algorithms maintain a visited collection to avoid repeatedly processing vertices.

## 10. Connected Components

A connected component is a maximal set of vertices in an undirected graph where every vertex is reachable from every other vertex in that set.

Consider:

\[
V = \{A,B,C,D,E,F\}
\]

\[
E = \{\{A,B\},\{B,C\},\{D,E\}\}
\]

The graph has three connected components:

\[
C_1 = \{A,B,C\}
\]

\[
C_2 = \{D,E\}
\]

\[
C_3 = \{F\}
\]

An isolated vertex is itself a connected component.

The Python, JavaScript, C++17, Java 17, and PostgreSQL implementations demonstrate component analysis.

For directed graphs, ordinary connected components are not sufficient to describe all reachability relationships. Strongly connected components and weakly connected components are separate concepts.

## 11. Cycle Detection

A cycle is a path that returns to its starting vertex without repeating intermediate vertices.

An undirected example is:

\[
A-B-C-A
\]

A directed example is:

\[
A \rightarrow B \rightarrow C \rightarrow A
\]

Cycle detection differs between directed and undirected graphs.

### Undirected graph

DFS tracks the parent vertex.

An already visited neighbor other than the parent indicates a cycle.

Self-loops also form cycles.

### Directed graph

DFS uses three states:

| State | Meaning |
|---|---|
| 0 | Unvisited |
| 1 | Currently being explored |
| 2 | Completely explored |

An edge to a vertex currently being explored indicates a directed cycle.

This is called back-edge detection.

Both approaches have:

\[
O(V+E)
\]

time complexity.

## 12. Weighted Shortest Paths

A shortest-path algorithm determines the minimum-cost path between vertices.

For weighted graphs, the path cost is the sum of its edge weights.

Consider:

\[
A \xrightarrow{4} B
\]

\[
A \xrightarrow{2} C
\]

\[
C \xrightarrow{1} B
\]

There are two routes from A to B:

Direct route:

\[
4
\]

Indirect route:

\[
2+1=3
\]

Therefore, the shortest distance is:

\[
d(A,B)=3
\]

### Dijkstra's Algorithm

Dijkstra's algorithm calculates shortest distances from one starting vertex to all reachable vertices.

It uses:

- A distance map
- A priority queue
- Edge relaxation
- A visited or stale-entry check

An edge relaxation updates a distance when a cheaper route is found.

\[
d(v) = \min(d(v),d(u)+w(u,v))
\]

The implementation rejects negative weights.

With adjacency lists and a binary heap:

\[
O((V+E)\log V)
\]

The algorithm is appropriate for non-negative edge weights.

Unreachable vertices retain infinite distance.

## 13. Technical Implementation Across Languages

### Python

The Python implementation uses:

- Dictionaries for adjacency lists.
- Sets for visited vertices.
- `deque` for BFS.
- Lists for DFS.
- `heapq` for shortest paths.
- Dataclasses for edge definitions.
- Enums for graph types.
- Exceptions for invalid operations.

It also includes graph serialization and executable assertions.

### JavaScript

The JavaScript implementation uses:

- `Map` for adjacency lists.
- `Set` for visited vertices.
- `EventEmitter` for graph change notifications.
- A custom binary min-heap.
- Private class fields for internal state.
- Promises and asynchronous file operations.
- JSON snapshots for persistence.

The graph emits events when vertices or edges change.

This event-driven approach is useful when graph modifications must trigger monitoring, logging, or downstream processing.

### C++17

The C++ implementation uses:

- STL maps for ordered adjacency storage.
- STL sets for visited vertices.
- Queues for BFS.
- Stacks implemented through vectors for DFS.
- Priority queues for shortest paths.
- Lambda functions for recursive traversal.
- Exceptions for invalid graph operations.

The implementation includes integrity validation to check edge symmetry and stored edge counts.

### Java 17

The Java implementation uses:

- Collections and generics.
- Records for immutable domain objects.
- Enums for graph classification.
- Interfaces for reporting.
- Priority queues.
- Streams for reporting operations.
- Custom exceptions.
- Immutable traversal and shortest-path results.

The enterprise-oriented design separates graph operations from report generation.

### PostgreSQL

The relational implementation models graphs through three main tables.

| Table | Purpose |
|---|---|
| `graphs` | Graph configuration |
| `vertices` | Individual graph vertices |
| `edges` | Relationships between vertices |

Additional database objects provide:

- Referential integrity.
- Unique vertex identifiers within each graph.
- Edge validation triggers.
- Adjacency views.
- Degree calculations.
- Graph statistics.
- Recursive BFS.
- Connected component identification.
- Validation reports.
- Transactional edge insertion.

The database stores each undirected edge once using canonical vertex ordering. Queries interpret that stored relationship in both directions.

Directed edges retain their source and target ordering.

## 14. Complexity Analysis

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.
- \(d(v)\) = degree of vertex \(v\).

| Operation | Adjacency List |
|---|---:|
| Add vertex | \(O(1)\) average |
| Add edge | \(O(1)\) average |
| Find neighbors | \(O(d(v))\) |
| Remove edge | \(O(d(v))\) in the Python representation |
| BFS | \(O(V+E)\) |
| DFS | \(O(V+E)\) |
| Connected components | \(O(V+E)\) |
| Cycle detection | \(O(V+E)\) |
| Degree | \(O(1)\) average for undirected adjacency maps |
| Dijkstra | \(O((V+E)\log V)\) |

The exact operation costs depend on the underlying collection.

For example, ordered maps in C++ and Java have different lookup costs from hash-based collections.

## 15. Practical Applications

| Application | Graph Model | Example |
|---|---|---|
| Social networks | Undirected | Mutual relationships |
| Website navigation | Directed | Hyperlinks |
| Transportation | Weighted | Road distances |
| Cloud infrastructure | Directed | Service dependencies |
| Computer networks | Weighted or unweighted | Network connections |
| Supply chains | Directed | Supplier dependencies |
| Project planning | Directed | Task dependencies |
| Communication systems | Directed or undirected | Message connections |

Graph fundamentals provide the structural foundation for advanced graph algorithms and network analysis.

## 16. Important Distinctions

| Concept | Meaning |
|---|---|
| Vertex | An entity in the graph |
| Edge | A relationship between vertices |
| Directed graph | Edges have direction |
| Undirected graph | Edges have no direction |
| Weighted graph | Edges contain numerical weights |
| Unweighted graph | Edges represent connections without meaningful weights |
| Degree | Number of incident edges in an undirected graph |
| In-degree | Number of incoming directed edges |
| Out-degree | Number of outgoing directed edges |
| BFS | Level-by-level traversal |
| DFS | Depth-oriented traversal |
| Connected component | Maximal connected vertex set |
| Cycle | A closed path |
| Shortest path | A path with minimum cost |

These concepts are related but are not interchangeable.

In particular, edge direction, edge weight, and vertex degree describe different properties of graph structure.

## 17. Limitations and Engineering Considerations

The implementations use simple graphs rather than multigraphs.

Consequently:

- Parallel edges are not independently represented.
- Vertex identifiers must be unique within a graph.
- The Dijkstra implementations do not support negative edge weights.
- Recursive cycle detection can encounter recursion-depth or stack limits on very deep graphs.
- Adjacency matrices require quadratic memory.
- PostgreSQL recursive traversal can become expensive on large or highly connected networks.
- Graph modifications and concurrent operations require appropriate synchronization in multi-user systems.

For production environments, additional considerations include:

- Transactional graph updates.
- Consistent vertex and edge identifiers.
- Input validation.
- Access control.
- Resource limits.
- Query optimization.
- Concurrency management.
- Monitoring and audit logging.

The choice of graph representation and algorithms should depend on graph density, expected query patterns, graph size, and application requirements.**
