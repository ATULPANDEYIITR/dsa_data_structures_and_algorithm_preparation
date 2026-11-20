# Breadth-First Search (BFS)

## 1. Introduction

Breadth-First Search is a graph traversal algorithm that explores vertices in increasing order of their distance from one or more starting vertices.

BFS uses a First-In, First-Out (FIFO) queue. It visits all immediately reachable neighbors before exploring vertices farther away.

For an unweighted graph, BFS finds the shortest path measured by the number of edges.

Its principal applications include:

- Graph traversal and reachability.
- Shortest paths in unweighted graphs.
- Level-order processing.
- Multi-source distance calculations.
- Connected-component discovery.
- Grid navigation.
- Dependency and network exploration.

## 2. Graph Representation

A graph consists of vertices and edges.

Formally:

G = (V, E)

Where:

- V represents the set of vertices.
- E represents the set of edges.

An adjacency list stores the neighbors of each vertex.

Example:

A -- B -- D
|    |
C    E -- H
|        /
F -- G

A corresponding adjacency-list representation stores each vertex and its neighboring vertices.

### Directed and undirected graphs

| Property | Directed graph | Undirected graph |
|---|---|---|
| Edge direction | One direction | Both directions |
| Representation | Source to destination | Both adjacency entries |
| Reverse traversal | Not automatic | Automatic |
| Typical application | Dependencies | Road networks |

The implementations support both graph types.

An edge from A to B in a directed graph does not imply an edge from B to A.

## 3. BFS Algorithm

The fundamental BFS workflow is:

1. Select a starting vertex.
2. Mark it as visited.
3. Insert it into a queue.
4. Remove the front vertex.
5. Examine its unvisited neighbors.
6. Mark each discovered neighbor as visited.
7. Record its parent and distance.
8. Insert it into the queue.
9. Continue until the queue is empty.

### Queue processing

Example graph:

A connects to B and C.

B connects to D and E.

C connects to F and G.

Expected traversal:

A → B → C → D → E → F → G

The queue evolves as follows:

| Operation | Queue |
|---|---|
| Initialize | A |
| Remove A | B, C |
| Remove B | C, D, E |
| Remove C | D, E, F, G |
| Remove D | E, F, G |
| Remove E | F, G |
| Remove F | G |
| Remove G | Empty |

The queue ensures that vertices discovered earlier are processed earlier.

## 4. Visited-Node Tracking

A visited collection prevents repeated exploration.

This is essential because graphs can contain:

- Cycles.
- Multiple paths to the same vertex.
- Self-reachable structures through different edges.
- Dense connections.

For example:

A → B → C → A

Without visited tracking, traversal could continue indefinitely.

The implementations mark vertices when they are inserted into the queue, not when they are removed.

This guarantees that each vertex is enqueued at most once.

### Data structures

| Implementation | Adjacency representation | Visited tracking | Queue |
|---|---|---|---|
| Python | Dictionary of lists | Distance dictionary | deque |
| JavaScript | Map of arrays | Map | Array with head index |
| C++17 | unordered_map | Distance map | std::queue |
| Java 17 | LinkedHashMap | Distance map | ArrayDeque |
| PostgreSQL | Relational edge table | Temporary work table | Indexed array |

The JavaScript implementation uses a queue head index instead of repeatedly removing the first array element. This avoids the cost of shifting remaining array elements.

## 5. Shortest Path in an Unweighted Graph

BFS discovers vertices in nondecreasing order of distance.

If a vertex is first discovered from a vertex at distance d, its shortest distance is:

d(v) = d(u) + 1

Where u is the vertex from which v was discovered.

For an unweighted graph, this first discovery establishes a shortest path.

### Parent tracking

The algorithm maintains:

- `distance`: minimum number of edges from the source.
- `parent`: previous vertex on the discovered shortest path.

Example:

A → B → E → H

The distances are:

| Vertex | Distance | Parent |
|---|---:|---|
| A | 0 | None |
| B | 1 | A |
| C | 1 | A |
| D | 2 | B |
| E | 2 | B |
| F | 2 | C |
| G | 2 | C |
| H | 3 | E |

To reconstruct the path to H, follow parent references backward:

H → E → B → A

Reverse the sequence:

A → B → E → H

### Important distinction

BFS guarantees shortest paths by edge count only when every edge has equal cost.

For weighted graphs with different nonnegative edge weights, Dijkstra's algorithm is generally appropriate.

## 6. Level Processing

BFS naturally organizes vertices into levels.

The level of a vertex is its shortest distance from the starting vertex.

For the example graph:

| Level | Vertices |
|---|---|
| 0 | A |
| 1 | B, C |
| 2 | D, E, F, G |
| 3 | H |

Level processing is useful for:

- Social-network degree analysis.
- Minimum-step problems.
- Network hop calculations.
- Tree-level traversal.
- Dependency exploration.
- Distance-based classification.

The Python and Java implementations explicitly store vertices by level.

The JavaScript implementation also provides asynchronous level iteration and emits a `level` event after processing each level.

## 7. Multi-Source BFS

Multi-source BFS extends ordinary BFS by initializing several starting vertices simultaneously.

Every source receives distance zero.

The algorithm then processes all sources through the same queue.

Example:

Graph:

A -- B -- C -- D -- E

Suppose A and E are starting vertices.

Initial state:

| Vertex | Distance |
|---|---:|
| A | 0 |
| E | 0 |

After traversal:

| Vertex | Minimum distance |
|---|---:|
| A | 0 |
| B | 1 |
| C | 2 |
| D | 1 |
| E | 0 |

The algorithm calculates the distance to the nearest source.

### Applications

- Nearest hospital or service-center discovery.
- Multiple-source network propagation.
- Nearest-exit calculations.
- Fire-spread simulations.
- Distributed network exploration.
- Minimum distance to a set of target nodes.

All sources must belong to the same graph.

Duplicate sources are removed before traversal.

A source cannot receive a positive distance because it is initialized at zero.

## 8. Grid-Based BFS

A grid can be represented as an implicit graph.

Each traversable cell represents a vertex.

Adjacent cells represent edges.

The implementations use four-directional movement:

- Up.
- Down.
- Left.
- Right.

Grid representation:

| Value | Meaning |
|---|---|
| 0 | Traversable |
| 1 | Blocked |

Example:

| 0 | 0 | 0 | 1 |
|---|---|---|---|
| 1 | 0 | 0 | 0 |
| 0 | 0 | 1 | 0 |
| 0 | 0 | 0 | 0 |

The algorithm explores valid neighboring cells and stores parent coordinates.

A shortest route is reconstructed by following those coordinates backward.

### Grid edge cases

The implementations account for:

- Empty grids.
- Rectangular-grid validation.
- Blocked starting cells.
- Blocked destination cells.
- Unreachable destinations.
- Boundary restrictions.
- Repeated cell discovery.

For a grid containing R rows and C columns, the time complexity is O(R × C), and auxiliary space is O(R × C).

## 9. Connected Components

A connected component is a maximal group of vertices in which every vertex is reachable from every other vertex.

For undirected graphs, BFS can discover connected components.

The procedure is:

1. Maintain a global visited collection.
2. Select an unvisited vertex.
3. Run BFS from that vertex.
4. Record all reached vertices as one component.
5. Continue until every vertex is visited.

Example:

Component 1: A, B, C, D

Component 2: X, Y, Z

An isolated vertex forms a component containing only itself.

The implementations reject connected-component processing on directed graphs because directed connectivity requires a different definition and algorithm.

Strongly connected components can be calculated using algorithms such as Kosaraju's or Tarjan's algorithm.

## 10. Complexity Analysis

Let:

- V = number of vertices.
- E = number of edges.
- R = number of grid rows.
- C = number of grid columns.

| Operation | Time complexity |
|---|---|
| Graph construction | O(V + E) |
| BFS traversal | O(V + E) |
| Shortest-distance calculation | O(V + E) |
| Parent-based path reconstruction | O(V) worst case |
| Level processing | O(V + E) |
| Multi-source BFS | O(V + E) |
| Connected components | O(V + E) |
| Grid BFS | O(R × C) |

For adjacency-list representations, BFS requires O(V + E) total space, including the graph and traversal structures.

The traversal-specific auxiliary space is O(V).

For an adjacency-matrix representation, neighbor discovery requires scanning a complete row, potentially increasing traversal time to O(V²).

Adjacency lists are preferable for sparse graphs.

## 11. Python Implementation

The Python implementation uses the standard library.

### Main structures

- `Graph`: graph management.
- `BFSResult`: traversal output.
- `deque`: efficient FIFO processing.
- Dictionaries: distances, parents and levels.
- Sets: visited-state tracking for component discovery.

### Main methods

| Method | Responsibility |
|---|---|
| `add_vertex()` | Create a vertex |
| `add_edge()` | Add a graph edge |
| `bfs()` | Single-source traversal |
| `multi_source_bfs()` | Multiple-source traversal |
| `connected_components()` | Discover undirected components |
| `shortest_path()` | Reconstruct a shortest path |
| `shortest_path_grid()` | Find a grid route |

The implementation uses a distance dictionary as its visited structure. A vertex is considered visited as soon as its distance is assigned.

This avoids maintaining a separate visited set for ordinary BFS.

## 12. JavaScript Implementation

The JavaScript implementation emphasizes event-driven and asynchronous processing.

### Main structures

- `Map`: graph and traversal state.
- `Set`: duplicate-source elimination.
- `EventEmitter`: level notifications.
- Async generators: incremental level processing.
- Array queue with a head pointer: efficient FIFO traversal.

### Event-driven traversal

The `traverseByLevel()` asynchronous generator yields one completed level at a time.

The `level` event provides a notification to independent consumers.

This design can support:

- Graph visualization.
- Progress monitoring.
- Incremental reporting.
- Asynchronous processing pipelines.

The implementation does not require third-party npm packages.

## 13. C++17 Implementation

The C++ implementation emphasizes efficient data structures and explicit domain modeling.

### Main structures

- `Graph`: graph representation and operations.
- `BFSResult`: distances, parents and levels.
- `GridPoint`: coordinate representation.
- `unordered_map`: adjacency and traversal state.
- `unordered_set`: visited tracking.
- `queue`: FIFO processing.
- `map`: ordered level reporting.

The implementation uses STL algorithms for path reversal and standard exceptions for invalid operations.

The grid implementation uses fixed-size direction arrays and a two-dimensional visited structure.

This avoids constructing a separate graph object for every grid cell.

## 14. Java 17 Implementation

The Java implementation follows an enterprise-oriented domain design.

### Domain types

| Type | Purpose |
|---|---|
| `GraphType` | Directed or undirected graph |
| `GraphException` | Domain validation errors |
| `GridPoint` | Immutable grid coordinates |
| `Level` | Immutable level representation |
| `BFSResult` | Immutable traversal output |
| `Graph` | Graph operations |

The `BFSResult` class protects its collections from modification by returning unmodifiable maps and immutable lists.

The implementation uses `ArrayDeque` for queue operations.

`Optional` represents the possible absence of a shortest path.

This distinguishes an unreachable destination from a valid empty or partially constructed path.

## 15. PostgreSQL Implementation

The SQL implementation models graph traversal using relational tables.

### Relational structure

| Table | Purpose |
|---|---|
| `graphs` | Graph metadata |
| `vertices` | Graph vertices |
| `edges` | Directed edge records |
| `bfs_runs` | Traversal execution history |
| `bfs_sources` | Initial traversal vertices |
| `bfs_results` | Distance and parent records |

### Relationship diagram

Graphs

→ Vertices

→ Edges

→ BFS Runs

→ BFS Sources

→ BFS Results

### Integrity enforcement

Primary keys uniquely identify records.

Foreign keys ensure that edge endpoints belong to valid vertices.

Unique constraints prevent duplicate directed edges.

Check constraints enforce valid graph types and nonnegative distances.

Indexes support graph-specific edge lookup and traversal-result retrieval.

### BFS execution function

`run_bfs()` implements queue-based traversal in PL/pgSQL.

Its principal operations are:

1. Validate the graph and source vertices.
2. Create a traversal record.
3. Initialize unique sources.
4. Insert sources into the queue.
5. Retrieve the next vertex.
6. Expand its neighboring vertices.
7. Record newly discovered vertices.
8. Save distances and parent references.
9. Mark the run completed.

The function supports both directed and undirected graphs.

For undirected graphs, it considers incoming and outgoing edge records.

The temporary work table maintains discovered vertices and prevents repeated insertion.

The execution history stores results independently for different BFS runs.

### Path reconstruction

`reconstruct_path()` follows parent references backward from the destination.

It returns vertices in source-to-destination order.

A destination absent from the traversal result produces an exception rather than an incorrect path.

### Level reporting

`bfs_level_report` aggregates traversal results by distance.

It reports:

- Run identifier.
- BFS level.
- Number of vertices.
- Vertices belonging to that level.

### Connected components

`connected_component_report()` uses BFS-style exploration to assign component identifiers.

It is restricted to undirected graphs.

## 16. BFS Correctness

BFS correctness relies on three important properties.

### Property 1: FIFO ordering

Vertices discovered at smaller distances are processed before vertices at larger distances.

### Property 2: First discovery

A vertex is marked visited when it enters the queue.

This ensures that its first discovered distance is the shortest distance from the source.

### Property 3: Complete exploration

Every reachable vertex is eventually removed from the queue and processed.

Therefore, when the queue becomes empty, all reachable vertices have been discovered.

Together, these properties establish that BFS computes shortest paths by edge count in an unweighted graph.

## 17. Edge Cases and Failure Handling

| Scenario | Expected behavior |
|---|---|
| Empty graph | No traversal results |
| Unknown starting vertex | Validation error |
| Empty multi-source input | Validation error |
| Duplicate sources | Deduplicate sources |
| Isolated vertex | Distance zero from itself |
| Cyclic graph | Terminate through visited tracking |
| Unreachable vertex | No distance or path result |
| Multiple shortest paths | Return one valid shortest path |
| Directed graph | Respect edge direction |
| Blocked grid destination | No path |
| Invalid grid dimensions | Validation error |
| Disconnected graph | Process reachable component only |

When several shortest paths have equal length, the particular path depends on adjacency-list insertion order.

The algorithm does not guarantee a lexicographically smallest shortest path.

## 18. Security and Performance Considerations

For production graph-processing systems:

- Validate external vertex identifiers.
- Enforce graph ownership for edge endpoints.
- Restrict graph size and traversal workload.
- Prevent unauthorized graph modifications.
- Use parameterized SQL statements.
- Apply transaction boundaries to graph updates.
- Avoid exposing internal database errors to untrusted clients.
- Monitor queue size and memory consumption.
- Use adjacency indexes for relational traversal.
- Consider partitioning for very large graph datasets.
- Apply execution timeouts to untrusted traversal requests.

The PostgreSQL example stores execution history and uses temporary traversal state. Its temporary tables are session-local, so concurrent sessions do not share the same traversal workspace.

A production deployment should also consider concurrent graph modifications. For a consistent traversal snapshot, execute the traversal using an appropriate transaction isolation strategy or immutable graph version.

## 19. Practical Applications

| Application | BFS role |
|---|---|
| Social networks | Find connections within a given number of hops |
| Computer networks | Calculate minimum-hop routes |
| Maps | Find shortest paths on unweighted road networks |
| Web crawling | Explore pages by link distance |
| Games | Find shortest movement sequences |
| Operating systems | Explore state-transition graphs |
| Distributed systems | Propagate information from multiple sources |
| Emergency services | Find nearest reachable service locations |
| Dependency analysis | Discover reachable dependent services |
| Grid navigation | Calculate minimum movement steps |

## 20. Practice Exercises

| Level | Problem | Main concept |
|---|---|---|
| Beginner | Implement BFS traversal | Queue and visited set |
| Beginner | Print vertices level by level | Level processing |
| Beginner | Count reachable vertices | Reachability |
| Intermediate | Find shortest path | Parent tracking |
| Intermediate | Find connected components | Repeated BFS |
| Intermediate | Detect shortest distance in a grid | Grid traversal |
| Intermediate | Find minimum depth of a binary tree | Level-order BFS |
| Advanced | Nearest exit in a maze | Grid BFS |
| Advanced | Rotting oranges | Multi-source BFS |
| Advanced | Shortest path in a binary matrix | Grid BFS |
| Advanced | Word ladder | State-space BFS |
| Advanced | 01 matrix | Multi-source BFS |
| Advanced | Shortest path in an undirected graph | Distance and parent tracking |

## 21. Key Distinctions

| Concept | Meaning |
|---|---|
| Graph traversal | Visiting reachable vertices |
| BFS | Systematic traversal using a FIFO queue |
| Visited tracking | Preventing repeated exploration |
| Shortest path | Minimum number of edges in an unweighted graph |
| Level processing | Grouping vertices by distance |
| Multi-source BFS | Calculating distance from the nearest initial source |
| Connected components | Partitioning an undirected graph into reachable groups |
| Parent tracking | Recording the predecessor used to discover a vertex |

BFS is particularly effective when a problem involves minimum steps, equal-cost transitions, graph reachability, or exploration in increasing distance order.
