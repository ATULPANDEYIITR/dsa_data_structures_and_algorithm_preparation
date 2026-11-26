# Dijkstra's Algorithm: Single-Source Shortest Paths

## 1. Problem Definition

Dijkstra's algorithm computes the shortest distances from one starting vertex to every reachable vertex in a weighted graph.

It is a greedy shortest-path algorithm. At each iteration, it selects the unsettled vertex with the smallest known tentative distance and uses that vertex to improve the distances of its adjacent vertices.

The algorithm is applicable to directed and undirected graphs containing non-negative edge weights.

### Learning objectives

- Understand single-source shortest paths.
- Represent weighted directed and undirected graphs.
- Implement Dijkstra's algorithm from scratch.
- Understand non-negative edge-weight restrictions.
- Implement priority queue optimization.
- Perform distance relaxation.
- Reconstruct shortest paths using predecessor information.
- Handle unreachable vertices and zero-weight edges.
- Compare heap-based implementations with relational database execution.

## 2. Graph Terminology

A weighted graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) is the set of vertices.
- \(E\) is the set of edges.
- \(w(u,v)\) represents the weight of an edge connecting vertices \(u\) and \(v\).

A vertex represents an entity or location. An edge represents a connection between two vertices. Its weight represents a measurable cost, such as distance, time, or monetary expense.

### Directed and undirected graphs

| Property | Directed graph | Undirected graph |
|---|---|---|
| Edge direction | One direction | Both directions |
| Representation | \(u \rightarrow v\) | \(u \leftrightarrow v\) |
| Reverse edge | Not automatic | Automatically represented |
| Example | One-way road | Two-way road |

The implementations support both graph types.

### Weighted edges

Consider an edge:

\[
A \rightarrow B,\quad w(A,B)=4
\]

The cost of travelling from A to B is 4.

Dijkstra's algorithm minimizes the sum of edge weights along a complete path.

For a path containing vertices \(v_0,v_1,\ldots,v_k\):

\[
D(P)=\sum_{i=0}^{k-1}w(v_i,v_{i+1})
\]

The shortest path minimizes this total cost.

## 3. Single-Source Shortest Path

Single-source shortest path means calculating the minimum distance from one specified source vertex to every other vertex in the graph.

For a source vertex \(s\):

\[
dist(s)=0
\]

For every other vertex:

\[
dist(v)=\infty
\]

Initially, no route to another vertex is known.

As the algorithm discovers connections, it replaces tentative distances with shorter values.

The output contains:

1. The source vertex.
2. The shortest known distance to each vertex.
3. The predecessor of each vertex.
4. The reconstructed shortest path.

### Example

Consider this directed graph:

| Edge | Weight |
|---|---:|
| S → A | 10 |
| S → B | 3 |
| B → A | 2 |
| A → T | 4 |
| B → T | 8 |

The shortest distances from S are:

| Vertex | Shortest distance | Shortest path |
|---|---:|---|
| S | 0 | S |
| A | 5 | S → B → A |
| B | 3 | S → B |
| T | 9 | S → B → A → T |

The direct edge from S to A has weight 10. The alternative route through B has total weight 5 and is therefore preferable.

This illustrates why the algorithm must evaluate alternative routes rather than simply selecting direct connections.

## 4. Non-Negative Edge Weights

Dijkstra's algorithm requires:

\[
w(u,v)\geq 0
\]

Every edge must have a non-negative weight.

Zero-weight edges are valid.

Negative-weight edges are not supported because they invalidate the greedy finalization property on which Dijkstra's algorithm depends.

### Why negative weights cause problems

Dijkstra's algorithm assumes that once a vertex has been selected as the minimum-distance unsettled vertex, its shortest distance cannot subsequently improve.

With negative weights, a later route could reduce an already finalized distance.

Therefore, accepting negative weights can produce incorrect shortest-path results.

The implementations reject:

- Negative weights.
- Non-numeric weights where applicable.
- Non-finite weights.
- Invalid source vertices.
- Invalid destination vertices.

For applications involving negative edge weights, a different shortest-path algorithm is required.

## 5. Core Algorithm

Dijkstra's algorithm maintains three important structures.

| Structure | Purpose |
|---|---|
| Distance map | Stores the current best distance to each vertex |
| Predecessor map | Stores the previous vertex in the best-known path |
| Priority queue | Selects the unsettled vertex with minimum tentative distance |

### Distance initialization

Set the source distance to zero and all other distances to infinity.

\[
dist(s)=0
\]

\[
dist(v)=\infty,\quad v\neq s
\]

### Extract minimum

Select the unsettled vertex with the smallest tentative distance.

The priority queue makes this operation efficient.

### Relaxation

For an edge from \(u\) to \(v\):

\[
candidate=dist(u)+w(u,v)
\]

If:

\[
candidate<dist(v)
\]

update:

\[
dist(v)=candidate
\]

and:

\[
pred(v)=u
\]

The predecessor records which vertex produced the improved route.

### Repeat

Continue until no reachable unsettled vertex remains.

Unreachable vertices retain their infinite distance.

### Algorithm workflow

    Initialize all distances to infinity
                |
                v
       Set source distance to zero
                |
                v
       Insert source into priority queue
                |
                v
       Extract minimum-distance vertex
                |
                v
          Check adjacent edges
                |
                v
       Calculate alternative distance
                |
                v
         Is the new distance shorter?
                |
          +-----+-----+
          |           |
         Yes          No
          |           |
          v           |
      Update distance |
      and predecessor|
          |           |
          +-----+-----+
                |
                v
       Continue processing queue
                |
                v
       No reachable vertex remains
                |
                v
       Return shortest distances

## 6. Priority Queue Optimization

A priority queue is a data structure that efficiently retrieves the element with the highest priority.

For Dijkstra's algorithm, priority is determined by the smallest tentative distance.

A min-priority queue is used.

### Why a priority queue is necessary

A basic implementation could scan all unsettled vertices to identify the smallest distance.

This requires repeated linear searches.

A binary min-heap provides efficient minimum extraction and insertion.

| Operation | Binary heap complexity |
|---|---:|
| Insert | \(O(\log V)\) |
| Extract minimum | \(O(\log V)\) |
| Access minimum | \(O(1)\) |

### Lazy deletion

The Python, JavaScript, C++, and Java implementations use a practical optimization called lazy deletion.

When a shorter route is discovered, a new entry is inserted into the priority queue.

The earlier entry is not explicitly removed.

When an outdated entry is extracted, the algorithm checks whether its distance is greater than the current recorded distance.

If it is outdated, it is skipped.

This avoids requiring a specialized decrease-key operation.

### Binary heap implementation

| Language | Priority queue mechanism |
|---|---|
| Python | `heapq` |
| JavaScript | Custom binary min-heap |
| C++17 | `std::priority_queue` with a custom comparator |
| Java 17 | `PriorityQueue` with a distance comparator |
| PostgreSQL | Indexed minimum-distance selection |

The JavaScript implementation includes its own binary heap to demonstrate the underlying data structure instead of depending on an external package.

## 7. Mathematical Correctness

Dijkstra's algorithm relies on the non-negativity of edge weights.

When the algorithm extracts the unsettled vertex \(u\) with the smallest tentative distance, that distance is optimal.

The reason is that any alternative path to \(u\) through another unsettled vertex would have to include an additional non-negative edge weight. It therefore cannot produce a smaller distance than the currently selected minimum.

By repeatedly applying this property, the algorithm finalizes shortest distances for all reachable vertices.

The algorithm maintains the following invariant:

**Every settled vertex has its final shortest distance from the source.**

This invariant is not guaranteed when negative-weight edges are present.

## 8. Complexity Analysis

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.

### Binary heap implementation

The algorithm processes vertices through priority queue operations and examines their outgoing edges.

The standard complexity is:

\[
O((V+E)\log V)
\]

For connected graphs, this is commonly expressed as:

\[
O(E\log V)
\]

The space complexity is:

\[
O(V+E)
\]

This includes graph adjacency storage, distances, predecessors, and priority queue entries.

### Comparison of implementations

| Implementation | Minimum selection | Expected complexity |
|---|---|---|
| Python | Binary heap | \(O((V+E)\log V)\) |
| JavaScript | Custom binary heap | \(O((V+E)\log V)\) |
| C++17 | Standard priority queue | \(O((V+E)\log V)\) |
| Java 17 | PriorityQueue | \(O((V+E)\log V)\) |
| PostgreSQL | Indexed relational selection | Higher than binary-heap implementation |

The PostgreSQL implementation performs minimum-distance selection using SQL ordering and an index. Its procedural approach is intentionally different from the heap-based implementations.

In the worst case, repeated relational minimum selection can approach quadratic vertex-selection work, with additional edge-processing and database-operation costs.

For large sparse graphs, a binary heap is generally more appropriate.

## 9. Python Implementation

The Python implementation uses `heapq` for efficient priority queue operations.

### Main components

| Component | Responsibility |
|---|---|
| `WeightedGraph` | Stores vertices and weighted adjacency lists |
| `ShortestPathResult` | Stores distances and predecessors |
| `dijkstra()` | Executes shortest-path computation |
| `path_to()` | Reconstructs a route |
| `distance_to()` | Retrieves a shortest distance |
| `run_tests()` | Validates algorithm behavior |

### Important implementation decisions

**Adjacency list**

The graph uses a dictionary whose values are lists of destination-weight pairs.

This representation is efficient for sparse graphs because only existing edges are stored.

**Priority queue**

`heapq` provides minimum-distance extraction.

An insertion counter is included to avoid comparing arbitrary vertex objects when two queue distances are equal.

**Predecessor reconstruction**

The predecessor map stores the previous vertex in the best-known route.

Route reconstruction starts at the destination and follows predecessor links until the source is reached.

**Unreachable vertices**

Unreachable vertices have infinite distances and return `None` when a route is requested.

### Validation

The tests cover:

- Shortest-distance calculation.
- Alternative route discovery.
- Predecessor reconstruction.
- Unreachable vertices.
- Zero-weight edges.
- Negative-weight rejection.
- Unknown source rejection.

### Execution

Run the file with Python 3:

    python dijkstra.py

The implementation uses only Python's standard library.

## 10. JavaScript Implementation

The JavaScript implementation emphasizes event-driven execution and explicit priority queue engineering.

### Main components

| Component | Responsibility |
|---|---|
| `MinPriorityQueue` | Implements binary min-heap operations |
| `WeightedGraph` | Manages graph state |
| `dijkstra()` | Calculates shortest distances |
| `findRoute()` | Exposes an asynchronous route-query interface |
| `EventEmitter` | Publishes graph and distance-update events |

### Event-driven behavior

The graph extends Node.js `EventEmitter`.

It publishes events when:

- A vertex is created.
- An edge is inserted.
- A shortest distance is improved.

This makes it possible for monitoring services and application components to respond to graph changes without being embedded in the shortest-path algorithm.

### Graph versioning

Each structural graph modification increments a version counter.

A shortest-path result includes the graph version used during its calculation.

This is useful for identifying results computed from older graph states.

A graph snapshot or immutable graph version is required when an application needs strict consistency during concurrent graph modifications.

### Asynchronous route queries

`findRoute()` provides a Promise-based interface suitable for integration with asynchronous application workflows.

The underlying Dijkstra calculation remains synchronous.

### Execution

Run with Node.js:

    node dijkstra.js

No external npm packages are required.

## 11. C++17 Implementation

The C++ implementation emphasizes efficient STL-based graph processing.

### Main components

| Component | Responsibility |
|---|---|
| `Edge` | Represents a weighted connection |
| `QueueEntry` | Stores a vertex and tentative distance |
| `CompareDistance` | Defines min-priority ordering |
| `WeightedGraph` | Maintains graph adjacency |
| `ShortestPathResult` | Stores distances and predecessors |
| `dijkstra()` | Executes the shortest-path algorithm |

### STL mechanisms

`unordered_map` stores adjacency lists and distance information.

`vector` stores edges and reconstructed paths.

`priority_queue` manages the frontier.

A custom comparator reverses the default priority queue ordering so that the smallest distance is extracted first.

### Engineering decisions

- Graph adjacency uses hash-based lookup.
- The priority queue uses lazy deletion.
- Distances use `double`.
- Non-finite weights are rejected.
- Distance overflow is checked.
- Unknown vertices produce exceptions.
- Unreachable vertices are represented by infinity.

The implementation does not require third-party libraries.

### Execution

Compile:

    g++ -std=c++17 -O2 -Wall -Wextra -pedantic dijkstra.cpp -o dijkstra

Run:

    ./dijkstra

The program prints shortest distances and reconstructed paths, followed by validation tests.

## 12. Java 17 Implementation

The Java implementation models shortest-path computation as an enterprise-oriented service.

### Domain model

| Type | Purpose |
|---|---|
| `GraphType` | Distinguishes directed and undirected graphs |
| `Edge` | Immutable weighted connection |
| `QueueEntry` | Priority queue entry |
| `Route` | Immutable route result |
| `ShortestPathResult` | Immutable shortest-path result |
| `WeightedGraph` | Graph representation |
| `ShortestPathService` | Shortest-path calculation |
| `RouteGovernanceService` | Applies route-distance policies |

### Records and immutable results

Java 17 records represent simple domain values.

The route result stores:

- Source.
- Destination.
- Distance.
- Ordered path.

The path is copied into an immutable list.

The shortest-path result similarly protects its returned maps from external modification.

The graph provides a snapshot of its adjacency structure to the computation service.

### Service separation

The `ShortestPathService` performs the mathematical shortest-path calculation.

The `RouteGovernanceService` applies an independent business rule by checking whether a route exceeds a permitted maximum distance.

This separates algorithmic correctness from application-specific policy.

### Failure handling

The implementation includes:

- `UnknownVertexException`.
- `NegativeWeightException`.
- `GraphException`.
- Invalid distance-policy rejection.
- Distance overflow detection.
- Unreachable route handling.

### Execution

Compile:

    javac DijkstraAlgorithm.java

Run:

    java -ea DijkstraAlgorithm

The `-ea` option enables Java assertions used by the test suite.

## 13. PostgreSQL Implementation

The SQL implementation represents a graph as relational data.

### Relational model

| Table | Purpose |
|---|---|
| `graph` | Stores graph metadata |
| `vertex` | Stores graph vertices |
| `edge` | Stores weighted connections |

The primary and foreign keys enforce graph ownership and referential integrity.

A vertex belongs to one graph. An edge references two vertices belonging to the same graph.

The composite foreign keys prevent an edge from connecting vertices belonging to different graphs.

### Constraints

The database enforces:

- Unique graph names.
- Unique vertex names within a graph.
- Non-negative edge weights.
- Finite numeric weights.
- Valid source and destination references.
- No self-loops.
- No duplicate directed edges.

The graph type determines whether an edge represents a directed or undirected connection.

The `add_graph_edge` procedure inserts the reverse edge automatically for undirected graphs.

Direct insertion into the edge table is available for the sample data and is not automatically expanded into a reverse edge. Production callers should use the procedure for undirected graph modifications.

### Dijkstra function

`calculate_shortest_paths()` implements the main algorithm using PL/pgSQL.

It creates two temporary tables:

- `dijkstra_distance`
- `dijkstra_settled`

The distance table stores:

- Vertex identifier.
- Current shortest tentative distance.
- Predecessor identifier.

The settled table records vertices whose shortest distances have been finalized.

The function repeatedly selects the minimum-distance unsettled vertex and relaxes its outgoing edges.

### Why SQL uses a different priority mechanism

The relational implementation uses:

- `ORDER BY distance`
- `LIMIT 1`
- Indexed distance selection
- Temporary tables
- SQL updates

It does not implement a binary heap.

This approach demonstrates how a graph algorithm can be represented using relational operations and procedural database logic.

### Path reconstruction

`get_shortest_path()` executes the shortest-path calculation and follows predecessor identifiers from the destination to the source.

It then returns the path in source-to-destination order.

An unreachable destination returns no route rows.

### Database reporting

The SQL script includes:

- Graph statistics.
- Edge retrieval.
- Graph validation.
- Shortest-distance reports.
- Route reconstruction.
- Reachability evaluation.
- Aggregate distance statistics.
- Maximum-distance eligibility evaluation.
- Edge-weight classification.

### Transaction handling

The script creates the schema and sample data inside a transaction.

It also demonstrates savepoint-based transaction handling for an edge insertion test.

### Execution

Execute the complete script in PostgreSQL using:

    psql -U postgres -d postgres -f dijkstra.sql

The script recreates the `dijkstra_lab` schema, so existing objects in that schema are removed.

## 14. Practical Applications

Dijkstra's algorithm is useful wherever the objective is to minimize the cumulative cost of travelling through a network.

| Application | Vertices | Edges | Weight |
|---|---|---|---|
| Road navigation | Locations | Roads | Distance or travel time |
| Computer networks | Routers | Network links | Latency or cost |
| Logistics | Warehouses | Transport connections | Transport expense |
| Telecommunications | Network nodes | Communication links | Transmission cost |
| Robotics | Positions | Movement options | Movement cost |
| Utility networks | Distribution points | Connections | Operational cost |
| Cloud infrastructure | Services | Communication links | Network latency |

The meaning of an edge weight must be consistent with the optimization objective.

For example, minimizing geographical distance is not necessarily equivalent to minimizing travel time.

## 15. Edge Cases and Engineering Considerations

### Disconnected graphs

A graph may contain multiple disconnected components.

Dijkstra's algorithm processes only vertices reachable from the selected source.

Other vertices retain infinite distances.

### Zero-weight edges

An edge can have zero cost.

Such edges do not violate the non-negative-weight requirement.

### Multiple shortest paths

Two or more routes may have identical minimum distances.

The implementations update predecessors only when a strictly shorter distance is found.

Consequently, they return one valid shortest path rather than enumerating every shortest path.

The selected path can depend on adjacency insertion order or priority-queue tie ordering.

### Floating-point precision

The Python, JavaScript, C++, and Java implementations use floating-point distances.

Decimal arithmetic can introduce small representation differences.

Applications requiring exact financial or decimal measurements should consider fixed-point or decimal arithmetic.

The PostgreSQL implementation uses `NUMERIC` for distance calculations.

### Graph modifications

Shortest-path results depend on the graph state at calculation time.

Adding or modifying edges can invalidate previously calculated results.

Applications maintaining dynamic networks should associate results with graph versions or use explicit immutable snapshots.

### Input validation

A production graph service should validate all external graph input before computation.

Important controls include:

- Vertex identifier validation.
- Edge-weight validation.
- Graph-size limits.
- Duplicate-edge policies.
- Numeric overflow checks.
- Authorization for graph modifications.
- Resource limits for large graph requests.

## 16. Limitations

Dijkstra's algorithm has specific operational boundaries.

| Limitation | Implication |
|---|---|
| Negative edge weights | Unsupported |
| Dynamic graph modifications | Existing results may become stale |
| All-shortest-path enumeration | Not provided by the implementations |
| Large dense graphs | Heap operations may not be the best choice |
| Floating-point arithmetic | Small numerical differences are possible |
| PostgreSQL procedural execution | Less efficient than specialized heap implementations for large sparse graphs |

The algorithm calculates shortest paths from one source per execution. Calculating shortest paths from every vertex requires repeated single-source executions or a different all-pairs shortest-path approach.

## 17. Implementation Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Graph representation | Dictionary | Map | Unordered map | HashMap | Relational tables |
| Priority structure | `heapq` | Custom heap | `priority_queue` | `PriorityQueue` | Indexed SQL selection |
| Directed graphs | Yes | Yes | Yes | Yes | Yes |
| Undirected graphs | Yes | Yes | Yes | Yes | Yes |
| Path reconstruction | Yes | Yes | Yes | Yes | Yes |
| Unreachable handling | Infinity | Infinity | Infinity | Infinity | NULL |
| Input validation | Yes | Yes | Yes | Yes | Constraints and procedures |
| External dependencies | None | None | None | None | None |

## 18. Key Distinctions

Three concepts must remain separate:

**Tentative distance**

The best distance discovered so far. It may improve when another route is found.

**Finalized distance**

The shortest distance established when the vertex is extracted as the minimum-distance unsettled vertex.

**Predecessor**

The previous vertex on the currently selected shortest route. It is used to reconstruct the actual path.

The distance table answers how expensive the route is. The predecessor structure explains which route produces that distance.

These structures work together but represent different information.

## 19. Technical Reference

| Concept | Mathematical or technical representation |
|---|---|
| Graph | \(G=(V,E)\) |
| Source | \(s\) |
| Edge weight | \(w(u,v)\) |
| Initial source distance | \(dist(s)=0\) |
| Initial other distances | \(dist(v)=\infty\) |
| Relaxation | \(dist(u)+w(u,v)<dist(v)\) |
| Priority queue | Min-heap |
| Shortest-path complexity | \(O((V+E)\log V)\) |
| Auxiliary graph storage | \(O(V+E)\) |
| Weight restriction | \(w(u,v)\geq 0\) |

The five implementations demonstrate the same shortest-path problem through different engineering approaches: Python's standard-library heap, JavaScript's custom event-driven heap, C++ STL priority queues, Java's enterprise-oriented service model, and PostgreSQL's relational and procedural execution model.
