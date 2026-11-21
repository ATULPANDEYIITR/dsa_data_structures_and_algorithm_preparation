# Depth-First Search (DFS)

## 1. Introduction

Depth-First Search (DFS) is a graph traversal algorithm that explores a graph by following one available path as deeply as possible before returning to an earlier vertex and exploring another path.

DFS is used to examine graph connectivity, identify connected components, detect cycles, reconstruct traversal paths, and analyze relationships between vertices.

A graph consists of:

- **Vertices:** Individual entities represented by nodes.
- **Edges:** Connections between pairs of vertices.
- **Adjacency list:** A representation that stores the neighbors of each vertex.
- **Visited set:** A collection of vertices already discovered.
- **Stack:** A Last-In, First-Out (LIFO) structure used to control traversal.
- **Parent:** The vertex from which another vertex was first discovered.
- **Depth:** The number of DFS tree edges between the starting vertex and a discovered vertex.

DFS can operate on directed and undirected graphs. The implementations in this project primarily use undirected graphs to demonstrate connected components.

## 2. Graph Representation

The adjacency-list representation stores the neighbors of each vertex.

Consider the following graph:

    1 ----- 2 ----- 4
    |       |
    |       5 ----- 8
    |              /
    3 ----- 6 -----
    |
    7

    9 ----- 10

    11

Its adjacency list is:

| Vertex | Neighbors |
|---|---|
| 1 | 2, 3 |
| 2 | 1, 4, 5 |
| 3 | 1, 6, 7 |
| 4 | 2 |
| 5 | 2, 8 |
| 6 | 3, 8 |
| 7 | 3 |
| 8 | 5, 6 |
| 9 | 10 |
| 10 | 9 |
| 11 | None |

The graph contains three connected components:

- Component 1: `{1, 2, 3, 4, 5, 6, 7, 8}`
- Component 2: `{9, 10}`
- Component 3: `{11}`

Vertex 11 is an isolated vertex because it has no connecting edges.

For an undirected graph, each edge connects two vertices symmetrically. The adjacency list therefore records each connection in both directions.

### Adjacency-list complexity

For a graph with V vertices and E edges:

| Operation | Typical complexity |
|---|---:|
| Store vertices | O(V) |
| Store undirected edges | O(V + E) |
| Retrieve neighbors | O(1) to access the collection |
| Iterate over neighbors | O(degree of vertex) |
| Check membership | O(1) average with hash sets |
| Check membership | O(log degree) with ordered sets |

An adjacency list is generally more space-efficient than an adjacency matrix for sparse graphs.

## 3. Recursive Depth-First Search

Recursive DFS uses function calls to represent the traversal path.

Each recursive call processes one vertex and explores its undiscovered neighbors.

### Mechanism

1. Select a starting vertex.
2. Mark it as visited.
3. Record the vertex in the traversal order.
4. Examine its adjacent vertices.
5. Recursively visit each undiscovered neighbor.
6. Return to the previous function call when no undiscovered neighbors remain.

The function call stack automatically maintains the traversal state.

### Example

Starting from vertex 1, with neighbors examined in ascending order:

    DFS(1)
      |
      +-- DFS(2)
      |     |
      |     +-- DFS(4)
      |     |
      |     +-- DFS(5)
      |           |
      |           +-- DFS(8)
      |                 |
      |                 +-- DFS(6)
      |                       |
      |                       +-- DFS(3)
      |                             |
      |                             +-- DFS(7)

The resulting traversal order is:

`1, 2, 4, 5, 8, 6, 3, 7`

The exact order depends on the order in which neighbors are examined.

### Python implementation

The Python implementation defines `recursive_dfs()` inside the `Graph` class.

It maintains:

- A `visited` set.
- An `order` list.
- A `parents` dictionary.
- A `depth` dictionary.

The nested `visit()` function handles recursive exploration.

### JavaScript implementation

The JavaScript implementation uses a recursive closure inside `recursiveDFS()`.

A `Map` stores parent and depth information, while a `Set` tracks visited vertices.

Traversal events are emitted through Node.js `EventEmitter`, separating traversal execution from event observation.

### C++17 implementation

The C++ implementation uses a recursive lambda with `std::function`.

This allows the function to call itself while maintaining access to traversal state.

### Java 17 implementation

The Java implementation separates recursive traversal into `recursiveDFS()` and `recursiveVisit()`.

The traversal service returns an immutable `TraversalResult` containing the resulting order and metadata.

### Advantages

- Natural correspondence with the mathematical definition of DFS.
- Concise implementation.
- Automatic backtracking through function returns.
- Convenient for recursive graph problems.

### Limitations

Recursive DFS consumes call-stack space.

In Python and JavaScript, sufficiently deep graphs can exceed the runtime's recursion or call-stack limits. C++ and Java can also encounter stack exhaustion.

Recursive DFS is therefore less suitable for extremely deep graphs when the available stack size is uncertain.

## 4. Iterative Depth-First Search

Iterative DFS replaces recursive function calls with an explicit stack.

The programmer controls when vertices are inserted and removed from the stack.

### Mechanism

1. Create an empty stack.
2. Insert the starting vertex.
3. Mark it as visited.
4. Remove the top vertex.
5. Process the removed vertex.
6. Insert its undiscovered neighbors.
7. Continue until the stack becomes empty.

### Stack behavior

Consider a vertex with neighbors 2 and 3.

To visit vertex 2 first:

    Push 3
    Push 2

The stack becomes:

    TOP -> 2
           3

The next removal returns vertex 2 because a stack follows LIFO ordering.

### Discovery and processing

A critical implementation decision is when a vertex becomes visited.

The implementations mark a vertex as visited when it is pushed onto the stack.

This prevents multiple adjacent vertices from inserting the same undiscovered vertex repeatedly.

It also ensures that the first discovered parent remains associated with that vertex.

### Python implementation

`iterative_dfs()` uses a Python list as a stack.

The `append()` method inserts a vertex, while `pop()` removes the most recently inserted vertex.

### JavaScript implementation

`iterativeDFS()` uses a JavaScript array as the stack.

`push()` and `pop()` implement the LIFO behavior.

### C++17 implementation

The C++ program uses `std::stack<int>`.

The `push()`, `top()`, and `pop()` operations provide explicit stack management.

### Java 17 implementation

The Java program uses `ArrayDeque<Integer>`.

Its `push()` and `pop()` operations provide stack behavior without requiring the older `Stack` class.

### Advantages

- Avoids dependence on recursive call-stack depth.
- Explicit control over traversal state.
- Suitable for large and deep graphs.
- Easier to integrate with iterative processing pipelines.

### Recursive versus iterative DFS

| Characteristic | Recursive DFS | Iterative DFS |
|---|---|---|
| Control mechanism | Function calls | Explicit stack |
| Backtracking | Automatic | Explicit |
| Visited tracking | Required | Required |
| Auxiliary stack | Runtime call stack | Application-managed stack |
| Deep graph handling | Stack exhaustion risk | Avoids recursive stack exhaustion |
| Implementation | Compact | More explicit |
| Traversal complexity | O(V + E) | O(V + E) |

Both approaches implement the same fundamental graph exploration strategy.

With the same neighbor ordering and discovery policy, their traversal orders can be identical.

The implementations in this project deliberately reverse neighbor insertion in iterative DFS to reproduce recursive traversal order.

## 5. Connected Components

A connected component is a maximal set of vertices in an undirected graph where every pair of vertices is connected through some path.

A connected component cannot be extended by including another vertex without losing the connectivity property.

### Example

Consider:

    1 ----- 2 ----- 3
    |
    4

    5 ----- 6

    7

There are three components:

- `{1, 2, 3, 4}`
- `{5, 6}`
- `{7}`

An isolated vertex forms its own component.

### Component detection algorithm

1. Initialize an empty global visited set.
2. Examine every vertex.
3. If a vertex is already visited, skip it.
4. Otherwise, start a new DFS traversal.
5. Add every discovered vertex to the current component.
6. Mark every discovered vertex globally as visited.
7. Continue until every vertex has been examined.

Each new traversal identifies one complete connected component.

### Why global visited state matters

The visited set must persist between component searches.

If it is recreated for every starting vertex, previously discovered vertices may be processed repeatedly.

A persistent visited set guarantees that each vertex belongs to exactly one discovered component.

### Complexity

For an adjacency-list graph:

- Every vertex is visited once.
- Every undirected edge is examined from both endpoints.
- Each component search uses DFS.

Total time complexity:

`O(V + E)`

Auxiliary space complexity:

`O(V)`

### Python implementation

`connected_components()` uses an explicit stack and a shared visited set.

Each component is returned as a sorted list of vertices.

### JavaScript implementation

`connectedComponents()` uses `Map`, `Set`, and an array-backed stack.

The resulting components are returned as arrays.

### C++17 implementation

`connectedComponents()` uses `std::unordered_set`, `std::stack`, and `std::vector`.

Each discovered component is sorted before being added to the result.

### Java 17 implementation

`analyzeComponents()` produces `ComponentReport` records.

Each report includes:

- Component identifier.
- Vertices.
- Number of vertices.
- Number of internal edges.

The edge count is calculated using the undirected graph degree-sum relationship.

For a component:

`Number of edges = Sum of vertex degrees / 2`

Every undirected edge contributes two to the sum of vertex degrees.

### PostgreSQL implementation

The SQL procedure `calculate_components()` uses iterative label propagation.

Each vertex initially receives its own component identifier.

The procedure repeatedly propagates the smallest neighboring component identifier until no labels change.

This provides a relational alternative to application-level DFS.

The algorithm terminates because component labels can only decrease and the graph contains a finite number of vertices.

Its purpose is connected-component identification, not reproduction of DFS visitation order.

## 6. Parent Relationships and Path Reconstruction

During DFS, a parent records the vertex that first discovered another vertex.

For example:

    1
    |
    2
    |
    5
    |
    8

The parent relationships are:

| Vertex | Parent |
|---|---|
| 1 | None |
| 2 | 1 |
| 5 | 2 |
| 8 | 5 |

The DFS tree provides a route from the starting vertex to each reachable vertex.

### Path reconstruction

To reconstruct a path:

1. Start from the destination.
2. Retrieve its parent.
3. Continue following parents.
4. Stop when the starting vertex has no parent.
5. Reverse the collected sequence.

For example, reconstructing the path from vertex 1 to vertex 8 produces:

`1 → 2 → 5 → 8`

This is a DFS-tree path.

It is not necessarily the shortest path.

DFS explores depth before breadth, so a different path may contain fewer edges.

For shortest paths in an unweighted graph, Breadth-First Search (BFS) is the appropriate algorithm.

### Unreachable vertices

If a destination is not included in the DFS traversal result, no path from the selected starting vertex was discovered.

The Python, JavaScript, and Java implementations return `None`, `null`, or an empty list respectively.

The C++ implementation returns an empty vector.

## 7. Cycle Detection

A cycle is a path that begins and ends at the same vertex without repeating other vertices.

For an undirected graph, DFS can detect a cycle using parent tracking.

### Detection rule

When exploring a vertex:

- An unvisited neighbor is explored recursively.
- A visited neighbor equal to the current vertex's parent represents the reverse direction of the same undirected edge.
- A visited neighbor different from the parent indicates a cycle.

The parent comparison is essential.

Without it, every ordinary undirected edge would incorrectly appear to form a cycle.

### Example

    1 ----- 2
     \     /
       3

The graph contains the cycle:

`1 → 2 → 3 → 1`

The C++ and Java implementations use recursive parent tracking.

The Python and JavaScript implementations apply the same rule.

The PostgreSQL script provides a separate recursive CTE-based cycle evaluation.

For directed graphs, cycle detection requires a different rule. A directed DFS generally uses three states:

- White: Not discovered.
- Gray: Currently being explored.
- Black: Completely explored.

A directed edge to a gray vertex identifies a back edge and therefore a directed cycle.

## 8. Implementation Architecture

The five source files provide different engineering perspectives.

| File | Main implementation | Distinct characteristics |
|---|---|---|
| Python | `Graph` and `TraversalResult` | Dataclasses, validation, assertions, path reconstruction |
| JavaScript | Event-driven `Graph` | EventEmitter, asynchronous generator, graph-version checks |
| C++17 | STL-based `Graph` | Ordered adjacency containers, explicit stack, recursive lambda |
| Java 17 | Graph and analysis services | Records, immutable results, enums, domain-oriented reports |
| PostgreSQL | Relational graph model | Recursive CTEs, temporary tables, stored functions, label propagation |

### Python design

The Python implementation uses a `Graph` class with an adjacency dictionary containing sets.

A frozen `TraversalResult` dataclass separates traversal output from graph state.

This makes traversal results easy to inspect and use for subsequent path reconstruction.

### JavaScript design

The JavaScript implementation introduces event-driven behavior.

Graph changes emit events that can be observed independently of the graph's traversal methods.

Its asynchronous generator allows traversal results to be consumed incrementally.

The graph version is checked between asynchronous batches to detect modifications during traversal.

### C++17 design

The C++ implementation uses ordered maps and sets to provide deterministic neighbor ordering.

An explicit stack handles iterative DFS, while a recursive lambda demonstrates recursive traversal.

The implementation uses standard-library containers without external dependencies.

### Java 17 design

The Java implementation separates domain data from graph operations and reporting.

`TraversalResult` and `ComponentReport` are records.

`TraversalStrategy` is an enum that selects the traversal algorithm.

`GraphAnalysisService` validates results and produces component reports.

A graph version prevents previously calculated traversal results from being treated as current after graph modification.

### PostgreSQL design

The SQL implementation models a graph using relational tables.

Its principal relationships are:

    Graph
      |
      +-- Vertices
      |
      +-- Edges
      |
      +-- Traversal Runs
      |      |
      |      +-- Traversal Results
      |
      +-- Component Results

The database uses composite foreign keys to ensure that edge endpoints belong to the correct graph.

The edge constraint stores an undirected edge in canonical order.

For example, an edge between 2 and 5 is stored as `(2, 5)` rather than storing both `(2, 5)` and `(5, 2)`.

## 9. PostgreSQL DFS Mechanisms

### Recursive CTE

A recursive Common Table Expression (CTE) repeatedly expands the current traversal state.

The `recursive_dfs()` function maintains:

- Current vertex.
- Parent vertex.
- Current depth.
- Traversal path.

The path array prevents a vertex already present in the current path from being visited again.

The generated paths are sorted to present the recursive traversal in depth-first order.

A recursive CTE does not itself guarantee DFS evaluation order. The explicit final ordering is important.

### Temporary stack

The `iterative_dfs()` function creates temporary tables:

- `dfs_stack`
- `dfs_visited`

The stack table stores pending vertices, parent identifiers, and depths.

A generated identity column establishes stack insertion order.

The function repeatedly removes the newest pending entry and processes it.

The visited table prevents duplicate processing.

### Label propagation

The `calculate_components()` procedure uses a different connected-component technique.

Every vertex starts with its own label.

For each edge, neighboring labels are compared and the smaller identifier propagates across the graph.

Iterations continue until no labels change.

This algorithm identifies connected components without storing DFS parent relationships.

### Indexing and integrity

The database includes:

- Composite primary keys for graph vertices.
- Composite foreign keys for edge endpoints.
- A canonical edge constraint.
- An index on destination vertices.
- Unique traversal positions within each run.
- Cascading deletion of graph-dependent records.

These constraints prevent inconsistent graph relationships and support efficient traversal queries.

The traversal functions still require repeated neighbor lookups, so edge indexes are important as graph size increases.

## 10. Complexity Analysis

Let:

- V = Number of vertices.
- E = Number of edges.
- D = Maximum degree of a vertex.

| Operation | Time complexity | Auxiliary space |
|---|---:|---:|
| Recursive DFS | O(V + E) | O(V) |
| Iterative DFS | O(V + E) | O(V) |
| Connected components | O(V + E) | O(V) |
| Path reconstruction | O(L) | O(L) |
| Undirected cycle detection | O(V + E) | O(V) |

L represents the number of vertices in the reconstructed path.

The complexity assumes adjacency-list traversal without sorting.

The implementations sort neighbors to produce deterministic traversal results. Sorting adds overhead.

For an adjacency-list implementation that sorts every adjacency collection during traversal, the additional cost is bounded by:

`O(Σ d(v) log d(v))`

where d(v) is the degree of vertex v.

An adjacency matrix changes traversal complexity because examining all possible neighbors requires scanning an entire row.

Its DFS complexity is generally:

`O(V²)`

The adjacency matrix requires:

`O(V²)` storage.

## 11. Edge Cases and Failure Handling

The implementations address several graph conditions.

| Condition | Expected behavior |
|---|---|
| Empty graph | No components |
| Isolated vertex | One component containing that vertex |
| Disconnected graph | Separate traversal components |
| Unknown starting vertex | Validation error |
| Repeated edge insertion | Existing connection remains unchanged |
| Self-loop | Rejected |
| Unreachable destination | No reconstructed path |
| Cycle | Detected using parent tracking |
| Deep graph | Iterative DFS avoids recursive call-stack exhaustion |
| Graph modification | Previously generated results may become stale |

### Duplicate edges

An undirected graph should not create duplicate neighbor relationships.

The Python and JavaScript implementations use sets.

C++ uses `std::set`.

Java uses `TreeSet`.

PostgreSQL uses a composite primary key.

### Deep graphs

Recursive DFS can fail when graph depth exceeds the available call-stack capacity.

Iterative DFS avoids this particular limitation by storing traversal state in an explicit stack.

The explicit stack still requires memory proportional to the number of pending vertices.

### Disconnected graphs

A single DFS starting from one vertex does not necessarily visit the entire graph.

Connected-component detection solves this by initiating additional DFS traversals for undiscovered vertices.

### Mutation during traversal

Graph modifications can invalidate previously calculated traversal metadata.

The Java implementation records a graph version in each result and rejects stale results during verification.

The JavaScript asynchronous traversal checks the graph version between processing batches.

The Python and C++ demonstrations use traversal results against an unchanged graph during normal execution.

## 12. Security and Reliability Considerations

Graph traversal is often used in dependency analysis, access-control relationship analysis, network topology exploration, and infrastructure discovery.

Production implementations should consider:

- Validate vertex identifiers before inserting them.
- Restrict graph size and edge count where inputs are untrusted.
- Prevent malformed graph relationships.
- Avoid unbounded recursive execution on externally supplied graphs.
- Use iterative traversal for potentially deep graphs.
- Apply authorization before exposing graph data.
- Protect database graph records through appropriate access controls.
- Use transactions when graph changes and traversal records must remain consistent.
- Detect stale traversal results after graph modification.
- Avoid exposing sensitive vertex labels or relationships in diagnostic output.
- Validate database inputs through constraints and parameterized queries.

The graph-version mechanism demonstrates one form of stale-result detection. It does not provide full concurrent transaction isolation or automatically prevent simultaneous modifications.

For concurrent graph processing, snapshot consistency and synchronization must be considered separately.

## 13. Practical Applications

DFS and connected-component detection have several practical applications.

| Application | DFS contribution |
|---|---|
| Network analysis | Discover reachable network devices |
| Dependency analysis | Explore dependency relationships |
| Cybersecurity | Analyze connected infrastructure relationships |
| Social networks | Identify connected user groups |
| File systems | Traverse directory structures |
| Knowledge graphs | Explore entity relationships |
| Compiler design | Analyze graph-based program structures |
| Infrastructure management | Identify isolated infrastructure groups |
| Workflow analysis | Explore reachable workflow states |
| Data integration | Identify disconnected data groups |

DFS establishes reachability from a selected starting vertex.

Connected-component detection extends this operation to the entire undirected graph.

These concepts are useful when understanding how entities are connected, identifying isolated groups, and examining graph structure.

## 14. Execution and Validation

### Python

Run the script using Python 3:

`python dfs.py`

The script uses standard-library modules and includes assertions comparing recursive and iterative traversal orders.

### JavaScript

Run using Node.js:

`node dfs.js`

The program demonstrates synchronous traversal, event emission, asynchronous iteration, and graph validation.

### C++17

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic dfs.cpp -o dfs`

Execute:

`./dfs`

On Windows:

`dfs.exe`

### Java 17

Compile:

`javac Main.java`

Execute:

`java Main`

### PostgreSQL

Execute the SQL script using a PostgreSQL 15 or newer database.

The script creates the `dfs_lab` schema and its associated objects, inserts demonstration records, executes both traversal approaches, calculates connected components, evaluates cycles, and runs reporting and validation queries.

The transaction commits the completed database setup and demonstration results.

### Expected demonstration results

For the supplied graph:

| Measurement | Expected result |
|---|---:|
| Total vertices | 11 |
| Total undirected edges | 9 |
| Connected components | 3 |
| Largest component | 8 vertices |
| Smallest component | 1 vertex |
| Isolated vertices | 1 |
| Contains cycle | True |
| Vertex 10 reachable from vertex 1 | False |
| Vertex 8 reachable from vertex 1 | True |

The recursive and iterative implementations use the same ascending neighbor-processing policy and should produce:

`1, 2, 4, 5, 8, 6, 3, 7`

The SQL recursive function produces the same DFS tree ordering through path-based ordering. The iterative SQL function uses an explicit temporary stack.

The SQL connected-component procedure independently identifies the three components through label propagation.
