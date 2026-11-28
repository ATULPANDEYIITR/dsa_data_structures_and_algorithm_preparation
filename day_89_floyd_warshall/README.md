# Floyd-Warshall Algorithm

## 1. Problem Definition

The Floyd-Warshall algorithm calculates the shortest paths between every pair of vertices in a weighted graph.

It belongs to the dynamic programming family of algorithms and is particularly useful when an application needs repeated shortest-distance queries across a relatively dense graph.

Unlike Dijkstra's algorithm, Floyd-Warshall supports negative edge weights. It does not produce valid finite shortest paths when a reachable negative-weight cycle exists.

### Problem characteristics

| Characteristic | Description |
|---|---|
| Input | Weighted directed or undirected graph |
| Output | Shortest distance between every vertex pair |
| Algorithm category | Dynamic programming |
| Negative edges | Supported |
| Negative cycles | Detected |
| Unreachable vertices | Represented by infinity |
| Time complexity | O(V³) |
| Space complexity | O(V²) |

Here, V represents the number of vertices.

## 2. Graph Representation

A weighted graph consists of vertices and edges.

Consider a directed graph:

    A --3--> B
    A --8--> C
    A --(-4)--> E
    B --1--> D
    C --4--> B
    D --(-5)--> C
    E --6--> D
    D --2--> A

An edge contains three elements:

- Source vertex
- Destination vertex
- Weight

The weight represents the cost of travelling between two vertices.

Possible applications include:

- Transportation networks
- Computer network routing
- Logistics optimization
- Dependency analysis
- Financial transaction networks
- Communication infrastructure

The implementations use integer vertex identifiers internally to simplify matrix indexing.

## 3. All-Pairs Shortest Paths

A single-source shortest-path algorithm calculates the minimum distance from one source vertex to other vertices.

An all-pairs shortest-path algorithm calculates the minimum distance for every possible source-destination combination.

For V vertices, the result contains V × V distance values.

For example:

| Source | Destination | Shortest distance |
|---|---|---:|
| A | B | 1 |
| A | C | -3 |
| A | D | 2 |
| A | E | -4 |

The complete result is stored in a distance matrix.

    D =
    [ d(0,0)  d(0,1)  d(0,2)  ... ]
    [ d(1,0)  d(1,1)  d(1,2)  ... ]
    [ d(2,0)  d(2,1)  d(2,2)  ... ]
    [   ...     ...     ...    ... ]

Each element D[i][j] represents the shortest known distance from vertex i to vertex j.

The diagonal initially contains zero because travelling from a vertex to itself requires no movement.

Unreachable pairs initially contain infinity.

## 4. Dynamic Programming Relationship

Floyd-Warshall uses a sequence of increasingly permissive shortest-path calculations.

Define:

D(k)[i][j]

as the shortest distance from vertex i to vertex j when only vertices 0 through k are permitted as intermediate vertices.

An intermediate vertex is a vertex used between the source and destination. It is not necessarily the source or destination itself.

The initial state permits no intermediate vertices.

Therefore:

D(-1)[i][j] = weight(i,j)

If no direct edge exists:

D(-1)[i][j] = infinity

For each intermediate vertex k, two alternatives are evaluated.

**Alternative 1: Do not use k**

The previously calculated shortest distance remains unchanged.

D(k-1)[i][j]

**Alternative 2: Use k**

The path travels from i to k and then from k to j.

D(k-1)[i][k] + D(k-1)[k][j]

The recurrence is:

D(k)[i][j] = min(
    D(k-1)[i][j],
    D(k-1)[i][k] + D(k-1)[k][j]
)

The implementation uses an in-place matrix because the recurrence permits the previous and current states to share the same storage.

The update becomes:

    distance[i][j] = min(
        distance[i][j],
        distance[i][k] + distance[k][j]
    )

This reduces the storage requirement from a three-dimensional dynamic programming table to a two-dimensional matrix.

## 5. Intermediate Vertices

The intermediate vertex is the central concept in Floyd-Warshall.

The outer loop selects which vertex may be introduced into existing shortest paths.

The algorithm processes vertices in sequence.

    for k = 0 to V - 1:
        for i = 0 to V - 1:
            for j = 0 to V - 1:

                if distance[i][k] + distance[k][j]
                   < distance[i][j]:

                    distance[i][j] =
                        distance[i][k] + distance[k][j]

The loop order is important.

The intermediate vertex loop must remain outside the source and destination loops to preserve the intended dynamic programming recurrence.

### Intermediate vertex example

Suppose the graph contains:

    A --4--> B
    B --3--> C
    A --10--> C

Initially:

    Distance(A,C) = 10

When B becomes an allowed intermediate vertex:

    Distance(A,B) + Distance(B,C)
    = 4 + 3
    = 7

The algorithm compares:

    min(10, 7) = 7

The shortest distance changes from 10 to 7.

## 6. Floyd-Warshall Execution Workflow

    Graph Input
        |
        v
    Initialize Distance Matrix
        |
        v
    Initialize Diagonal to Zero
        |
        v
    Insert Direct Edge Weights
        |
        v
    Select Intermediate Vertex k
        |
        v
    Evaluate Every Source-Destination Pair
        |
        v
    Compare Direct and Intermediate Routes
        |
        v
    Update Distance Matrix
        |
        v
    Process Remaining Intermediate Vertices
        |
        v
    Check Negative Cycles
        |
        v
    Store All-Pairs Shortest Distances
        |
        v
    Reconstruct Requested Paths

Each iteration considers whether introducing another intermediate vertex improves existing shortest paths.

## 7. Negative Edge Weights

A negative edge represents a transition that decreases the accumulated path cost.

For example:

    A --4--> B
    B --(-6)--> C
    A --3--> C

The direct path from A to C costs 3.

The indirect path costs:

    4 + (-6) = -2

Therefore:

    Shortest distance(A,C) = -2

Floyd-Warshall supports this situation without requiring special changes to its recurrence.

Dijkstra's algorithm, by contrast, does not generally support negative edge weights.

Negative edges are not equivalent to negative cycles.

A negative edge can exist without making the shortest-path problem undefined.

## 8. Negative Cycle Detection

A negative-weight cycle is a cycle whose total edge weight is negative.

Example:

    A --1--> B
    B --(-3)--> C
    C --1--> A

Total cycle weight:

    1 - 3 + 1 = -1

Repeatedly travelling through this cycle decreases the total path cost without a finite lower bound.

Consequently, a finite shortest path does not exist for vertex pairs that can enter and leave the cycle.

Floyd-Warshall detects negative cycles through diagonal values.

    distance[i][i] < 0

A negative diagonal indicates a negative-weight cycle reachable from that vertex.

The implementations reject the computed result when such a cycle exists.

A production implementation that needs partial results for graphs containing negative cycles must classify affected source-destination pairs separately rather than treating every pair as having a valid finite shortest distance.

## 9. Path Reconstruction

A distance matrix answers the question:

What is the minimum cost of travelling between two vertices?

It does not independently identify the actual sequence of vertices.

The implementations therefore maintain a next-vertex matrix.

Initially:

- A direct edge from i to j stores j as the next vertex.
- A vertex's diagonal stores itself.
- An unreachable pair stores no next vertex.

When an intermediate route improves the distance:

    next[i][j] = next[i][k]

This records the first vertex on the improved path.

Path reconstruction repeatedly follows the stored next vertex until the destination is reached.

Example:

    A -> B -> D -> C

The reconstructed path is accompanied by its calculated total distance.

An unreachable destination returns no path.

## 10. Python Implementation

The Python implementation uses a `Graph` dataclass to manage graph state.

### Main components

| Component | Responsibility |
|---|---|
| `Graph` | Stores graph and computation state |
| `add_edge()` | Validates and registers weighted edges |
| `floyd_warshall()` | Calculates all-pairs shortest paths |
| `detect_negative_cycles()` | Validates the distance matrix |
| `shortest_distance()` | Retrieves a calculated distance |
| `shortest_path()` | Reconstructs a route |
| `print_matrix()` | Displays the computed matrix |

The implementation uses nested lists because they provide straightforward two-dimensional indexing.

The `next_vertex` matrix provides route reconstruction.

Assertions validate single-vertex graphs, disconnected vertices, parallel edges, negative edges, and negative cycles.

The implementation uses Python's standard library without external dependencies.

## 11. JavaScript Implementation

The JavaScript implementation provides an event-driven route computation engine.

It uses:

- `Map` for adjacency representation.
- `Float64Array` for distance storage.
- `Int32Array` for next-vertex storage.
- `EventEmitter` for computation notifications.
- Promises for asynchronous execution.
- Custom error classes for graph and negative-cycle failures.

### Event lifecycle

    computationStarted
          |
          v
    intermediateVertexProcessed
          |
          v
    intermediateVertexProcessed
          |
          v
    computationCompleted

A failed computation emits `computationFailed`.

The computation yields to the Node.js event loop between intermediate-vertex iterations using `setImmediate`.

This improves event-loop responsiveness but does not reduce the algorithm's computational complexity or make its matrix updates parallel.

The graph maintains a version number.

If the graph changes while computation is running, the result is rejected.

Previously computed results are also rejected when the graph version no longer matches.

## 12. C++17 Implementation

The C++ implementation focuses on efficient matrix processing and explicit resource management.

### Main components

| Component | Responsibility |
|---|---|
| `WeightedGraph` | Graph state and matrix storage |
| `addEdge()` | Validates and registers edges |
| `floydWarshall()` | Performs dynamic programming |
| `detectNegativeCycle()` | Checks diagonal values |
| `getDistance()` | Retrieves shortest distance |
| `getPath()` | Reconstructs the shortest route |
| `printMatrix()` | Displays shortest distances |

The implementation uses:

- `vector<vector<double>>` for distance storage.
- `vector<vector<int>>` for next-vertex storage.
- `optional<vector<int>>` for reachable-path results.
- STL algorithms and numeric limits.
- Custom exception handling.

The `optional` return type distinguishes an unreachable destination from a valid path.

The program compiles using the C++17 standard without third-party libraries.

## 13. Java 17 Implementation

The Java implementation models route optimization as an enterprise-oriented service.

### Domain types

| Type | Responsibility |
|---|---|
| `Edge` | Immutable weighted edge |
| `RouteResult` | Immutable shortest-path result |
| `WeightedGraph` | Graph and matrix state |
| `FloydWarshallService` | Shortest-path computation |
| `RoutePlanningApplication` | Application-level workflow |
| `ComputationStatus` | Computation lifecycle |

Java records represent immutable domain data.

The service separates graph management from shortest-path computation.

It maintains a graph version to identify stale results after modifications.

The application supports route registration, optimization, matrix reporting, and individual route queries.

The custom exceptions distinguish negative cycles from general graph validation errors.

## 14. PostgreSQL Implementation

The SQL implementation represents graph information relationally.

### Database entities

| Table | Purpose |
|---|---|
| `graphs` | Stores graph definitions |
| `vertices` | Stores graph vertices |
| `edges` | Stores weighted directed edges |
| `all_pairs_shortest_paths` | Stores computed results |

The composite primary key on the vertices table prevents duplicate vertex identifiers within a graph.

Foreign keys ensure that every registered edge connects existing vertices.

The shortest-path table uses a composite primary key consisting of graph, source, and destination identifiers.

### Computation procedure

The `compute_all_pairs()` procedure:

1. Validates the graph.
2. Verifies contiguous vertex identifiers.
3. Initializes a session-local distance matrix.
4. Sets diagonal distances to zero.
5. Inserts minimum direct edge weights.
6. Processes intermediate vertices.
7. Detects negative cycles.
8. Publishes validated results.

The implementation uses a temporary relational table rather than a three-dimensional array.

Each intermediate vertex iteration performs a set-based update.

The procedure does not publish results when a negative cycle is detected.

### Path reconstruction

The `get_shortest_path()` function follows the stored next-vertex information to reconstruct a route.

It validates the graph and route endpoints.

It also prevents reconstruction from continuing indefinitely.

### Reporting

The SQL implementation provides:

- Edge-weight classification.
- Named shortest-distance reports.
- Reachability reporting.
- Minimum and maximum distance aggregation.
- Route reconstruction.
- Negative-cycle validation.

The indexes support graph-specific edge retrieval and shortest-path queries.

## 15. Time and Space Complexity

Let V represent the number of vertices and E represent the number of edges.

| Operation | Time complexity |
|---|---|
| Distance matrix initialization | O(V²) |
| Direct edge initialization | O(E) |
| Floyd-Warshall computation | O(V³) |
| Negative cycle detection | O(V) |
| Distance query | O(1) |
| Path reconstruction | O(V) |
| Distance matrix storage | O(V²) |
| Next-vertex matrix storage | O(V²) |

The dominant computational cost is O(V³).

The two matrices require O(V²) memory.

For dense graphs, this matrix representation is practical because the number of possible edges is already proportional to V².

For very large sparse graphs, repeated single-source shortest-path algorithms may offer better performance.

## 16. Important Edge Cases

| Case | Expected behavior |
|---|---|
| Single vertex | Distance to itself is zero |
| No direct edge | Distance is infinity |
| Disconnected vertices | No path is returned |
| Negative edge | Included in distance calculations |
| Negative cycle | Computation is rejected |
| Parallel edges | Minimum direct edge weight is retained |
| Zero-weight edge | Valid edge |
| Self-loop with positive weight | Zero-length diagonal remains preferable |
| Self-loop with negative weight | Negative cycle detected |
| Invalid vertex | Validation error |
| Non-finite edge weight | Rejected |
| Modified graph | Previous results become stale |

## 17. Floyd-Warshall Compared with Other Algorithms

| Property | Floyd-Warshall | Dijkstra | Bellman-Ford |
|---|---|---|---|
| Problem | All pairs | Single source | Single source |
| Negative edges | Yes | No, in general | Yes |
| Negative cycle detection | Yes | No general support | Yes |
| Dynamic programming | Yes | No | Repeated relaxation |
| Matrix-based implementation | Natural | Optional | Optional |
| Dense graph suitability | Good | Depends on implementation | Usually less attractive |
| Time complexity | O(V³) | O((V+E) log V) with a binary heap | O(VE) |

The algorithms solve related but different shortest-path problems.

Floyd-Warshall is appropriate when the application requires shortest distances between many pairs of vertices.

## 18. Implementation Constraints and Production Considerations

### Numerical precision

The Python, JavaScript, C++, and Java implementations use floating-point representations.

Floating-point arithmetic can introduce rounding errors.

Applications involving monetary values, precise scientific calculations, or exact integer weights should select an appropriate numeric representation.

For bounded integer weights, sufficiently wide integer types can avoid floating-point precision issues.

### Overflow and infinity

Distance calculations must be protected against arithmetic overflow.

The implementations use finite input validation and infinity checks before adding path distances.

A production implementation using fixed-width integer arithmetic should explicitly check addition boundaries.

### Memory usage

Two V × V matrices are required for distances and next-vertex information.

Large graphs may exceed available memory before computation begins.

### Graph modifications

A shortest-path matrix describes a particular graph state.

Changing an edge or vertex invalidates previous calculations.

The Python, JavaScript, and Java implementations explicitly manage computation validity.

The PostgreSQL implementation requires recomputation after graph modifications.

### Database concurrency

Database applications should calculate shortest paths against a consistent graph snapshot.

Concurrent modifications must not cause partially calculated or outdated results to be published.

A production deployment should coordinate graph updates and computation using suitable transaction isolation, locking, or graph-version validation.

### Negative cycles

A negative cycle invalidates finite shortest-path results for affected vertex pairs.

Applications must not interpret an arbitrary matrix value as a valid shortest distance when such a cycle exists.

### Performance

The algorithm requires O(V³) operations regardless of graph density.

For repeated queries against an unchanged graph, calculating the matrix once and reusing it avoids repeated shortest-path computations.

## 19. Learning Outcomes

The implementations demonstrate the relationship between:

- Weighted graph representation.
- All-pairs shortest paths.
- Dynamic programming state transitions.
- Intermediate vertex selection.
- Distance matrix updates.
- Negative edge handling.
- Negative cycle detection.
- Next-vertex matrix maintenance.
- Shortest-path reconstruction.
- Complexity analysis.
- Database-based graph processing.
- State validation and failure handling.

The central algorithmic principle is that the shortest path between two vertices either avoids the newly permitted intermediate vertex or uses that vertex to connect two previously calculated shortest paths.
