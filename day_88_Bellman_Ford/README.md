# Bellman-Ford: Shortest Paths, Negative Edges and Negative Cycles

## 1. Problem Definition

The shortest-path problem determines the minimum total edge weight required to travel from a source vertex to another vertex in a weighted graph.

A weighted directed graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) represents the set of vertices.
- \(E\) represents the set of directed edges.
- Each edge has a weight \(w(u,v)\).
- A source vertex \(s\) specifies the starting point.

For a path containing edges \(e_1,e_2,\ldots,e_k\), its total weight is:

\[
W(P)=\sum_{i=1}^{k}w(e_i)
\]

The objective is to determine:

\[
d(s,v)=\min_{P:s\rightarrow v}W(P)
\]

A shortest path may not exist as a finite value when a reachable negative-weight cycle can be traversed repeatedly.

The Bellman-Ford algorithm addresses this problem by repeatedly relaxing edges and subsequently checking for negative cycles.

## 2. Fundamental Graph Concepts

### Directed graph

An edge from vertex A to vertex B does not automatically create an edge from B to A.

For example:

| Source | Destination | Weight |
|---|---|---:|
| A | B | 4 |
| A | C | 5 |
| B | C | -2 |
| C | D | 3 |

The edge B → C does not imply C → B.

### Weighted edge

An edge weight represents the cost of moving between two vertices.

Weights can represent:

- Travel costs.
- Financial transaction costs.
- Network routing metrics.
- Resource consumption.
- Distances.
- Time differences.
- Credits or gains.

A negative edge indicates that traversing an edge reduces the accumulated path cost. It does not automatically indicate a negative cycle.

### Path

A path is a sequence of connected vertices.

For example:

A → B → C → D

Its total weight is:

\[
4+(-2)+3=5
\]

### Reachability

A vertex is reachable from source \(s\) if at least one directed path connects them.

An unreachable vertex has no valid source-to-destination path. Its distance is represented as infinity mathematically and as `None`, `Infinity`, or `NULL` in the implementations.

## 3. Edge Relaxation

Relaxation is the central operation of Bellman-Ford.

Suppose an edge connects vertex \(u\) to vertex \(v\), with weight \(w(u,v)\).

The current distance estimates are:

\[
d[u],d[v]
\]

The algorithm evaluates:

\[
d[u]+w(u,v)<d[v]
\]

If the condition is true, the destination distance is improved:

\[
d[v]=d[u]+w(u,v)
\]

The predecessor is updated:

\[
pred[v]=u
\]

If the condition is false, the existing distance remains unchanged.

### Example

Consider the following edges:

| Edge | Weight |
|---|---:|
| A → B | 4 |
| A → C | 5 |
| B → C | -2 |
| C → D | 3 |

Starting from A:

| Vertex | Initial distance |
|---|---:|
| A | 0 |
| B | ∞ |
| C | ∞ |
| D | ∞ |

After processing A → B:

\[
d[B]=0+4=4
\]

After processing A → C:

\[
d[C]=0+5=5
\]

After processing B → C:

\[
d[C]=4-2=2
\]

After processing C → D:

\[
d[D]=2+3=5
\]

The resulting shortest distances are:

| Vertex | Distance | Path |
|---|---:|---|
| A | 0 | A |
| B | 4 | A → B |
| C | 2 | A → B → C |
| D | 5 | A → B → C → D |

The important observation is that the direct path to C has cost 5, while the alternative path through B has cost 2.

Relaxation discovers the better route.

## 4. Bellman-Ford Algorithm

For a graph containing \(V\) vertices, a shortest simple path contains at most \(V-1\) edges.

A simple path does not repeat vertices.

Consequently, Bellman-Ford performs at most:

\[
V-1
\]

complete edge-relaxation passes.

### Algorithm workflow

1. Initialize every vertex distance to infinity.
2. Set the source distance to zero.
3. Iterate through all edges.
4. Relax each edge when its source is reachable.
5. Repeat for at most \(V-1\) passes.
6. Stop early if an entire pass produces no changes.
7. Perform an additional edge-relaxation check.
8. Identify vertices affected by reachable negative cycles.
9. Propagate the effect to their downstream vertices.
10. Reconstruct valid shortest paths using predecessor information.

### Why V-1 passes?

A shortest simple path cannot contain more than \(V-1\) edges.

Each complete relaxation pass can extend the known shortest-path information by at least one additional edge.

After \(V-1\) passes, every finite shortest path must have been discovered if no reachable negative cycle exists.

The implementation processes edges in a fixed order and can propagate information across multiple edges in one pass. This can make convergence faster, but does not change the correctness of the \(V-1\) bound.

### Early termination

If an entire pass does not change any distance, further passes cannot improve the current shortest distances.

The algorithm can terminate immediately.

This optimization improves practical performance on graphs that converge quickly.

## 5. Negative Edge Weights

A negative edge has a weight below zero.

For example:

\[
w(B,C)=-2
\]

Negative edges are valid in Bellman-Ford.

They can represent:

- Discounts in transportation networks.
- Financial credits.
- Negative exchange-cost adjustments.
- Recovery of previously accumulated costs.
- Reward-based routing models.

A negative edge does not necessarily create a negative cycle.

Consider:

A → B with weight 4.

B → C with weight -2.

C → D with weight 3.

The path total is:

\[
4-2+3=5
\]

The path has a valid finite shortest distance.

Bellman-Ford handles this situation without requiring nonnegative weights.

## 6. Negative Cycles

A cycle is a path that begins and ends at the same vertex.

A negative cycle has a negative total edge weight.

For example:

| Edge | Weight |
|---|---:|
| B → C | 2 |
| C → D | -5 |
| D → B | 1 |

Its total weight is:

\[
2-5+1=-2
\]

Traversing this cycle repeatedly decreases the accumulated path weight.

After one traversal:

\[
-2
\]

After two traversals:

\[
-4
\]

After three traversals:

\[
-6
\]

Therefore, no finite minimum path cost exists for vertices reachable from this cycle.

### Detection mechanism

After the standard \(V-1\) relaxation passes, Bellman-Ford performs another check.

For every edge:

\[
d[u]+w(u,v)<d[v]
\]

If an edge can still improve a reachable destination, a reachable negative cycle exists.

The distinction between reachable and unreachable cycles is essential.

An isolated negative cycle cannot affect shortest paths originating from a source that cannot reach it.

### Propagation

Detecting one relaxable edge identifies a vertex influenced by a negative cycle.

Every vertex reachable from an affected vertex is also affected.

A breadth-first search over the adjacency list identifies all such downstream vertices.

The resulting classifications are:

| Classification | Meaning |
|---|---|
| Finite distance | A valid finite shortest distance exists |
| Unreachable | No path exists from the source |
| Negative-cycle affected | No finite shortest distance exists |

The implementations preserve this distinction instead of treating every vertex as affected by any negative cycle in the graph.

## 7. Shortest-Path Reconstruction

Distances alone do not identify the actual route.

Bellman-Ford therefore maintains a predecessor for each vertex.

Whenever relaxation improves a destination:

\[
pred[v]=u
\]

The final route is reconstructed by following predecessors backward.

For example:

\[
pred[D]=C
\]

\[
pred[C]=B
\]

\[
pred[B]=A
\]

Starting from D and following predecessors produces:

D → C → B → A

Reversing this sequence produces:

A → B → C → D

Path reconstruction must reject:

- Unknown destinations.
- Unreachable destinations.
- Negative-cycle-affected destinations.
- Invalid predecessor chains.
- Cyclic predecessor relationships.

## 8. Bellman-Ford Versus Dijkstra

Both algorithms solve the single-source shortest-path problem, but their operating assumptions differ.

### Dijkstra

Dijkstra uses a greedy strategy.

At each step, it selects the unsettled vertex with the smallest known distance.

It finalizes that vertex under the assumption that no subsequently discovered route can reduce its distance.

This assumption requires nonnegative edge weights.

A negative edge can invalidate an earlier finalization decision.

### Bellman-Ford

Bellman-Ford does not finalize vertices using Dijkstra's greedy rule.

It repeatedly examines all edges and improves distance estimates through relaxation.

It supports negative edge weights and detects reachable negative cycles.

### Technical comparison

| Criterion | Bellman-Ford | Dijkstra |
|---|---|---|
| Negative edges | Supported | Not supported |
| Negative-cycle detection | Yes | No |
| Greedy finalization | No | Yes |
| Main mechanism | Repeated relaxation | Priority queue |
| Typical implementation | Edge list | Adjacency list |
| Time complexity | O(VE) | O((V+E) log V) with a binary heap |
| Space complexity | O(V+E) | O(V+E) |
| Sparse nonnegative graphs | Usually slower | Usually faster |
| Negative-weight graphs | Suitable | Invalid |
| Unreachable vertices | Supported | Supported |

For a dense graph, Dijkstra with a simple array-based implementation can also run in \(O(V^2)\).

The precise complexity depends on the priority-queue and graph representation.

### When to choose each algorithm

Choose Bellman-Ford when:

- Negative edge weights are possible.
- Negative-cycle detection is required.
- Financial or cost-adjustment models contain negative values.
- The graph's weight assumptions are not guaranteed to be nonnegative.

Choose Dijkstra when:

- All edge weights are nonnegative.
- Efficient shortest-path computation is important.
- Negative-cycle detection is not required.
- A priority-queue-based implementation is appropriate.

Dijkstra should not be selected merely because it produces faster results on a graph whose weights violate its assumptions.

## 9. Python Implementation

The Python implementation models a graph using:

- A vertex collection.
- An edge list.
- An adjacency dictionary.
- A dataclass representing each edge.
- An enum identifying the selected algorithm.
- A result object containing distances and predecessors.

### Important mechanisms

`WeightedGraph` manages graph construction and validates vertex references.

`bellman_ford()` implements repeated relaxation, early termination, negative-cycle detection, and downstream propagation.

`dijkstra()` uses Python's `heapq` priority queue and explicitly rejects negative edge weights.

`ShortestPathResult.path_to()` reconstructs routes while protecting against invalid predecessor chains.

The implementation uses Python integers, which support arbitrary-precision arithmetic.

This avoids fixed-width integer overflow for ordinary graph calculations.

The demonstration cases cover negative edges, negative cycles, unreachable vertices, algorithm comparison, and invalid inputs.

## 10. JavaScript Implementation

The JavaScript implementation uses an event-driven design.

`WeightedGraph` extends Node.js `EventEmitter`.

It exposes events for:

- `edgeAdded`
- `relaxation`
- `passCompleted`
- `analysisCompleted`

This allows monitoring applications to observe algorithm progress without coupling event consumers to the internal relaxation loop.

Bellman-Ford is asynchronous and yields between passes using `setImmediate()`.

This makes it possible for an application to process progress events between computational passes.

Dijkstra uses a sorted-array priority queue for a compact implementation. Sorting the queue repeatedly is less efficient than using a binary heap, so this implementation is primarily suitable for demonstration and smaller graphs.

JavaScript's ordinary `Number` type cannot represent every integer exactly.

Consequently, the implementation checks `Number.isSafeInteger()` and raises an error when distance arithmetic exceeds safe integer precision.

For larger numerical ranges, `BigInt` is a suitable alternative, provided all arithmetic and comparisons use compatible types.

## 11. C++17 Implementation

The C++ implementation emphasizes explicit graph modeling and computational control.

Its primary structures are:

- `Edge`: represents a weighted directed edge.
- `ShortestPathResult`: stores distances, predecessors, and affected vertices.
- `WeightedGraph`: manages graph construction and algorithms.

The adjacency list supports efficient traversal of outgoing edges.

The edge list provides direct access to all edges during Bellman-Ford relaxation.

Dijkstra uses `std::priority_queue` with a minimum-priority comparator.

The implementation uses `__int128` for intermediate addition to detect values outside the supported `long long` distance range.

This is supported by common GCC and Clang environments, although it is a compiler extension rather than a standard C++17 integer type.

The implementation uses an explicit infinity sentinel and validates graph membership before processing.

The negative-cycle propagation stage uses breadth-first search.

## 12. Java 17 Implementation

The Java implementation adopts an enterprise-oriented service design.

Its domain components include:

| Component | Responsibility |
|---|---|
| `Edge` | Immutable weighted edge |
| `DirectedGraph` | Graph state and validation |
| `AnalysisPolicy` | Algorithm execution policy |
| `BellmanFordService` | Relaxation and cycle detection |
| `DijkstraService` | Priority-queue shortest paths |
| `ShortestPathResult` | Immutable analysis output |
| `AlgorithmPolicyException` | Invalid algorithm or policy execution |

Java records provide concise immutable edge and queue-entry models.

`BigInteger` supports arbitrary-precision distance arithmetic, avoiding the overflow limitations associated with primitive integer types.

The services separate graph validation from algorithm execution.

The analysis policy can prohibit negative weights even when the underlying algorithm supports them. This distinction is useful in applications where organizational rules impose stricter requirements than mathematical correctness alone.

The result object protects its collections through immutable copies.

It also prevents the application from treating negative-cycle-affected distances as valid shortest paths.

## 13. PostgreSQL Implementation

The SQL implementation stores graphs and their analysis results relationally.

### Relational model

The principal relationships are:

    repositories
        |
        +---- vertices
        |       |
        |       +---- edges (source)
        |       |
        |       +---- edges (destination)
        |
        +---- analysis_runs
                    |
                    +---- shortest_path_results

### Database tables

| Table | Purpose |
|---|---|
| `repositories` | Stores independent graph definitions |
| `vertices` | Stores graph vertices |
| `edges` | Stores directed weighted edges |
| `analysis_runs` | Records algorithm execution |
| `shortest_path_results` | Persists distances and predecessor information |

Composite foreign keys ensure that an edge's source and destination belong to the same graph.

The schema permits parallel edges because two vertices may have multiple connections with different weights.

### Bellman-Ford database function

`bellman_ford()` implements the algorithm using temporary working tables.

The `bf_distance` table maintains current distance estimates and predecessor identifiers.

The `bf_affected` table tracks vertices influenced by reachable negative cycles.

The function:

1. Validates the graph and source.
2. Initializes distance estimates.
3. Executes relaxation passes.
4. Stops when no changes occur.
5. Checks for additional improvements.
6. Propagates negative-cycle influence.
7. Returns the final vertex classifications.

`execute_bellman_ford()` stores the results in permanent analysis tables.

The execution is transactional. If the calling transaction fails, its changes can be rolled back.

### Database integrity

The schema uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Partial indexes.
- Composite indexes.
- Reporting views.
- PL/pgSQL functions.
- Temporary tables.
- Transaction boundaries.

The `validate_dijkstra_eligibility()` function prevents Dijkstra execution on a graph containing negative-weight edges.

This is an eligibility check, not an implementation of Dijkstra in SQL.

The analysis history records the selected algorithm, execution time, number of result vertices, and negative-cycle status.

### SQL numeric representation

PostgreSQL `NUMERIC` is used for edge weights and distance calculations.

This avoids the overflow behavior associated with fixed-width integer arithmetic for the selected numeric precision.

The implementation assumes edge weights fall within the declared range.

Temporary working tables are session-local. Concurrent executions in different database sessions therefore do not share intermediate distance state.

Repeated calls in one session truncate and reuse the working tables.

## 14. Complexity Analysis

Let:

- \(V\) = number of vertices.
- \(E\) = number of directed edges.

### Bellman-Ford

Each pass examines all edges.

There are at most \(V-1\) relaxation passes.

The additional negative-cycle check examines the edge list once.

Therefore:

\[
T(V,E)=O(VE)
\]

The distance and predecessor structures require:

\[
O(V)
\]

The graph representation requires:

\[
O(V+E)
\]

Negative-cycle propagation uses an additional breadth-first traversal:

\[
O(V+E)
\]

The total space complexity, including graph storage, is:

\[
O(V+E)
\]

### Dijkstra

Using an adjacency list and binary heap:

\[
T(V,E)=O((V+E)\log V)
\]

The graph, distances, predecessors, and priority queue require:

\[
O(V+E)
\]

For sparse nonnegative graphs, Dijkstra is generally preferable when negative-edge support is unnecessary.

## 15. Edge Cases and Failure Conditions

| Scenario | Expected behavior |
|---|---|
| Empty graph | Reject graph creation |
| Duplicate vertices | Reject invalid input |
| Unknown source | Reject analysis |
| Unknown destination | Reject path reconstruction |
| Negative edge | Accept in Bellman-Ford |
| Negative edge with Dijkstra | Reject execution |
| Unreachable vertex | Return no finite distance |
| Reachable negative cycle | Report affected vertices |
| Unreachable negative cycle | Do not affect source analysis |
| Negative self-loop | Detect when reachable |
| Parallel edges | Evaluate every edge |
| Zero-weight edge | Process normally |
| No relaxation in a pass | Terminate early |
| Invalid predecessor chain | Reject reconstruction |
| Numeric overflow | Reject unsupported arithmetic where applicable |

A particularly important distinction is that a negative cycle does not invalidate every shortest path in the graph.

Only vertices reachable from a reachable negative cycle have undefined shortest distances.

Vertices outside that affected region may still have valid shortest paths.

## 16. Practical Applications

### Network routing

Bellman-Ford provides the conceptual foundation for distance-vector routing.

Routers exchange distance information and update route estimates based on neighboring routing information.

The distributed setting introduces additional concerns such as convergence, routing loops, and count-to-infinity behavior.

### Financial cost models

Negative edge weights can represent credits, discounts, or adjustments.

Negative-cycle detection can identify repeated sequences of transitions that continually reduce modeled cost.

The mathematical result must be interpreted carefully: a negative cycle in a cost graph may indicate an inconsistent model, an exploitable opportunity, or a missing business constraint.

### Transportation systems

Transportation graphs can include positive travel costs and negative adjustments.

Bellman-Ford can analyze shortest paths when the graph contains valid negative edges, provided reachable negative cycles are absent.

### Dependency and optimization models

Weighted directed graphs can represent transitions between states.

Negative edges can represent improvements or benefits.

Negative cycles can reveal an optimization model in which the objective is unbounded below.

## 17. Implementation Limitations

The implementations are educational graph-analysis systems rather than distributed routing platforms.

Important limitations include:

- The graph is directed.
- Edge weights are integers.
- The implementations operate on a complete in-memory graph, except for the PostgreSQL implementation.
- No incremental shortest-path maintenance is implemented.
- No distributed execution or graph partitioning is implemented.
- Dijkstra is intentionally restricted to nonnegative weights.
- Bellman-Ford does not return a finite shortest path for vertices affected by reachable negative cycles.
- The JavaScript priority queue uses a sorted array instead of a binary heap.
- The C++ implementation uses the commonly available `__int128` extension.
- The PostgreSQL implementation uses ordered in-place relaxation and session-local temporary working tables.

For large dense graphs, Bellman-Ford can become computationally expensive.

Algorithm selection should therefore consider graph size, edge-weight constraints, required guarantees, and execution environment.

## 18. Verification Scenarios

The five implementations use consistent representative graph scenarios.

### Scenario A: Negative edges without negative cycles

Expected shortest distances from vertex 0:

| Vertex | Distance |
|---|---:|
| 0 | 0 |
| 1 | 4 |
| 2 | 2 |
| 3 | 5 |
| 4 | 7 |
| 5 | Unreachable |

Bellman-Ford must produce finite distances for vertices 0 through 4 and leave vertex 5 unreachable.

Dijkstra must reject this graph because it contains negative edges.

### Scenario B: Reachable and unreachable negative cycles

Edges:

- 0 → 1, weight 2
- 1 → 2, weight 2
- 2 → 3, weight -5
- 3 → 1, weight 1
- 3 → 4, weight 3
- 5 → 5, weight -1

The cycle:

\[
1\rightarrow2\rightarrow3\rightarrow1
\]

has total weight:

\[
2-5+1=-2
\]

Vertices 1, 2, 3, and 4 are affected.

Vertex 5 contains a negative self-loop, but it is unreachable from vertex 0. It must remain classified as unreachable rather than negative-cycle-affected.

### Scenario C: Nonnegative graph comparison

The implementations run Bellman-Ford and Dijkstra on the same nonnegative graph.

Both algorithms must produce identical shortest distances.

This verifies their agreement when Dijkstra's weight assumptions are satisfied.

## 19. Core Conceptual Distinctions

The central ideas can be separated into four mechanisms:

| Mechanism | Purpose |
|---|---|
| Relaxation | Improves distance estimates |
| Negative edges | Allow transitions that reduce accumulated cost |
| Negative-cycle detection | Identifies the absence of a finite shortest distance |
| Algorithm selection | Determines whether Bellman-Ford or Dijkstra is valid |

The relationship between these mechanisms is fundamental.

Bellman-Ford supports negative edges because it repeatedly relaxes edges instead of permanently finalizing vertices using a greedy assumption.

Its additional relaxation check detects reachable negative cycles.

Dijkstra is faster for many nonnegative graphs, but its correctness depends on that nonnegative-weight condition.

The correct algorithm is determined by the mathematical properties of the graph, not merely by execution speed.
