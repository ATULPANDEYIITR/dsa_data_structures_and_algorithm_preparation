# Topological Sorting and Dependency Scheduling

## Project Description

This project implements directed acyclic graphs (DAGs), dependency relationships, DFS-based topological sorting, Kahn's algorithm, parallel execution scheduling, cycle detection, and critical path analysis.

The implementations use a realistic software development workflow in which architecture, database design, backend development, frontend development, integration, testing, security assessment, and deployment have explicit execution dependencies.

The five source files provide independent implementations:

| File | Engineering perspective |
|---|---|
| Python | Graph modeling, algorithm comparison, scheduling, validation |
| JavaScript | Event-driven asynchronous workflow execution |
| C++17 | Efficient graph representation and scheduling engine |
| Java 17 | Enterprise domain modeling and controlled state transitions |
| PostgreSQL | Relational dependency management and transactional scheduling |

## 1. Directed Acyclic Graph

A directed graph consists of vertices and directed edges.

A dependency graph represents tasks as vertices and execution constraints as directed edges.

For example:

`A -> B`

means that task B depends on task A. Task A must complete before B can execute.

A directed acyclic graph contains no directed path that returns to its starting vertex.

### DAG characteristics

- Vertices represent tasks, activities, or operations.
- Directed edges represent precedence constraints.
- A vertex can have multiple prerequisites.
- A vertex can have multiple dependent tasks.
- Independent vertices can execute concurrently.
- A valid DAG has at least one topological ordering.
- A directed cycle makes the dependency requirements impossible to satisfy.

A DAG does not require every vertex to be connected. Independent tasks and multiple disconnected components are valid.

### Example dependency graph

The project uses the following relationships:

| Task | Activity | Prerequisites |
|---|---|---|
| T1 | Gather requirements | None |
| T2 | Design architecture | T1 |
| T3 | Design database | T1 |
| T4 | Implement backend | T2, T3 |
| T5 | Implement frontend | T2 |
| T6 | Integrate application | T4, T5 |
| T7 | Execute testing | T6 |
| T8 | Security assessment | T6 |
| T9 | Production deployment | T7, T8 |

The dependency structure is:

    T1
    |
    +---- T2 -------- T5
    |      |
    |      +---- T4
    |             |
    +---- T3       |
           |       |
           +-------+
                   |
                   T6
                   |
              +----+----+
              |         |
              T7        T8
              |         |
              +----+----+
                   |
                   T9

The diagram represents precedence constraints rather than an exact timeline.

## 2. Dependency Relationships

A dependency establishes an ordering requirement between two tasks.

The graph uses the convention:

`prerequisite -> dependent`

This direction is important because some graph representations use edges in the opposite direction.

### Adjacency list

An adjacency list stores the outgoing neighbors of each vertex.

For the project:

| Vertex | Outgoing neighbors |
|---|---|
| T1 | T2, T3 |
| T2 | T4, T5 |
| T3 | T4 |
| T4 | T6 |
| T5 | T6 |
| T6 | T7, T8 |
| T7 | T9 |
| T8 | T9 |
| T9 | None |

The outgoing adjacency list supports traversal from prerequisites to dependent tasks.

A reverse adjacency list stores incoming dependencies. It makes prerequisite lookup and indegree calculation straightforward.

### Indegree

Indegree is the number of incoming edges for a vertex.

For example:

- T1 has indegree 0.
- T2 has indegree 1.
- T4 has indegree 2.
- T6 has indegree 2.
- T9 has indegree 2.

A vertex with indegree zero has no remaining prerequisites and can be selected for execution.

### Outdegree

Outdegree is the number of outgoing edges.

A task with high outdegree has many dependent tasks.

This is useful when analyzing the consequences of a failed prerequisite or a delayed activity.

## 3. Topological Sorting

Topological sorting produces a linear ordering of vertices in which every directed edge points from an earlier vertex to a later vertex.

For every edge:

`u -> v`

the resulting order must satisfy:

`position(u) < position(v)`

Topological sorting is defined for DAGs.

A graph may have multiple valid topological orderings because independent vertices can appear in different positions.

For example, after T1 completes, T2 and T3 can both become available. Either can appear first in a valid ordering.

Topological sorting does not itself execute tasks. It determines a valid sequence that respects dependency constraints.

## 4. DFS-Based Topological Sorting

Depth-First Search explores a vertex's outgoing edges before completing that vertex.

The algorithm maintains three traversal states:

| State | Meaning |
|---|---|
| White | Not visited |
| Gray | Currently being explored |
| Black | Fully explored |

### Algorithm

1. Initialize all vertices as white.
2. Select an unvisited vertex.
3. Mark it gray.
4. Explore its outgoing neighbors.
5. Recursively process unvisited neighbors.
6. Detect a cycle if an edge reaches a gray vertex.
7. Mark the vertex black after exploring all neighbors.
8. Append the completed vertex to the result.
9. Reverse the resulting postorder.

Appending a vertex after exploring its descendants is essential.

Reversing this completion order produces a valid topological ordering.

### Cycle detection

An edge from the current traversal path to a gray vertex indicates a back edge.

A back edge establishes a directed cycle.

For example:

`A -> B -> C -> A`

The traversal encounters A while A is still gray.

The algorithm can reconstruct the cycle from the active recursion path.

### Complexity

| Operation | Complexity |
|---|---|
| Vertex initialization | O(V) |
| Edge traversal | O(E) |
| DFS traversal | O(V + E) |
| Postorder reversal | O(V) |
| Auxiliary storage | O(V) |

V represents the number of vertices and E represents the number of edges.

DFS is useful when traversal information, cycle reconstruction, and recursive graph exploration are required.

### Implementation details

- Python maintains color states and an active traversal path.
- JavaScript uses Maps and Sets for graph state.
- C++17 uses ordered containers for deterministic traversal.
- Java 17 separates traversal policy from repository storage.

Recursive DFS can encounter call-stack limitations on very deep graphs. An iterative DFS implementation is preferable when graph depth is potentially very large.

## 5. Kahn's Algorithm

Kahn's algorithm performs topological sorting through indegree management.

Instead of exploring descendants recursively, it repeatedly removes vertices that have no remaining incoming dependencies.

### Algorithm

1. Calculate the indegree of every vertex.
2. Insert all zero-indegree vertices into a ready collection.
3. Remove one available vertex.
4. Append it to the topological result.
5. Visit its outgoing neighbors.
6. Decrease each neighbor's indegree.
7. Insert a neighbor when its indegree becomes zero.
8. Continue until no available vertices remain.
9. Compare the number of processed vertices with the total number of vertices.

If all vertices have been processed, the graph is acyclic.

If some vertices remain unprocessed, the graph contains a directed cycle.

### Example

Initial indegrees:

| Task | Indegree |
|---|---:|
| T1 | 0 |
| T2 | 1 |
| T3 | 1 |
| T4 | 2 |
| T5 | 1 |
| T6 | 2 |
| T7 | 1 |
| T8 | 1 |
| T9 | 2 |

T1 is initially available.

After T1 is processed, T2 and T3 become available.

After both are processed, T4 and T5 become available.

The process continues until every task has been selected.

### Complexity

With an ordinary FIFO queue:

- Time complexity: O(V + E).
- Auxiliary space: O(V).

The Python, C++17, and Java implementations use a priority-based ready collection to produce deterministic ordering.

A binary heap introduces logarithmic insertion and removal costs:

`O((V + E) log V)`

The JavaScript implementation uses a sorted array for its ready collection, which is simpler for the small demonstration graph but can be less efficient for large graphs.

### DFS and Kahn comparison

| Characteristic | DFS | Kahn |
|---|---|---|
| Main mechanism | Depth-first traversal | Indegree reduction |
| Data structure | Stack or recursion | Queue or priority queue |
| Cycle detection | Back edge to gray vertex | Unprocessed vertices remain |
| Ordering | Reverse postorder | Zero-indegree selection |
| Parallel scheduling | Requires additional analysis | Naturally exposes available tasks |
| Common application | Dependency analysis | Build and task scheduling |

Both algorithms produce valid topological orderings when the graph is acyclic.

Neither guarantees a unique ordering.

## 6. Parallel Execution Scheduling

A topological ordering is a sequential representation of dependency constraints.

A parallel schedule identifies tasks that can be executed at the same stage.

The implementations calculate an execution level for each task.

The level of a task is:

`level(v) = 0` when v has no prerequisites.

Otherwise:

`level(v) = 1 + max(level(p))`

where p represents each direct prerequisite.

### Project execution levels

| Stage | Available tasks |
|---|---|
| 0 | T1 |
| 1 | T2, T3 |
| 2 | T4, T5 |
| 3 | T6 |
| 4 | T7, T8 |
| 5 | T9 |

Tasks in the same level have no dependency path between them.

They can be considered for concurrent execution, subject to available resources and other operational constraints.

A task becomes eligible only when all its prerequisites have completed successfully.

Being present in the same execution level does not mean that tasks must start simultaneously.

### Important distinction

Topological sorting determines a valid ordering.

Level calculation identifies dependency-based parallelism.

Actual scheduling also requires resource availability, worker limits, execution durations, failure handling, and operational policies.

The JavaScript implementation demonstrates bounded asynchronous execution with a configurable concurrency limit.

## 7. Critical Path Analysis

The critical path is the longest-duration path through a directed acyclic project network.

It determines the minimum theoretical project completion time when:

- Task durations are known.
- Tasks execute as soon as dependencies permit.
- Resources are sufficient.
- No unexpected delays occur.
- The dependency constraints remain unchanged.

### Earliest finish calculation

For a task v:

`EF(v) = duration(v) + max(EF(p))`

where p represents its prerequisites.

For a task without prerequisites:

`EF(v) = duration(v)`

The final project duration is the maximum earliest finish among all tasks.

### Example

The project has the following durations:

| Task | Duration |
|---|---:|
| T1 | 2 |
| T2 | 3 |
| T3 | 2 |
| T4 | 5 |
| T5 | 4 |
| T6 | 2 |
| T7 | 3 |
| T8 | 2 |
| T9 | 1 |

One critical path is:

`T1 -> T2 -> T4 -> T6 -> T7 -> T9`

Its duration is:

`2 + 3 + 5 + 2 + 3 + 1 = 16`

The alternative path through T8 is shorter.

The Python, JavaScript, C++17, and Java implementations calculate the longest dependency path using dynamic programming over a topological ordering.

The critical path is not necessarily the same as the topological ordering. It is a specific longest-duration path within the graph.

## 8. Python Implementation

The Python script uses an object-oriented graph model.

### Main components

| Component | Responsibility |
|---|---|
| `Task` | Stores task information and duration |
| `TaskStatus` | Defines execution states |
| `DependencyGraph` | Maintains vertices and dependency edges |
| `CycleError` | Reports invalid cyclic relationships |
| `topological_sort_dfs()` | Performs DFS-based sorting |
| `topological_sort_kahn()` | Performs indegree-based sorting |
| `calculate_levels()` | Determines parallel execution stages |
| `calculate_critical_path()` | Calculates the longest weighted path |
| `validate_order()` | Checks ordering correctness |

The adjacency and reverse-adjacency structures use dictionaries and sets.

This supports efficient neighbor lookup and prevents duplicate edges.

The dependency insertion operation rolls back an edge when it introduces a cycle.

The implementation also verifies that both algorithms produce valid orderings.

The critical path calculation uses task durations rather than treating all vertices as equal.

## 9. JavaScript Implementation

The JavaScript implementation emphasizes event-driven execution and asynchronous operations.

### Event-driven architecture

`WorkflowEngine` extends Node.js `EventEmitter`.

It publishes events for:

- Workflow initiation.
- Task initiation.
- Task completion.
- Task failure.
- Task blocking.
- Workflow completion.

Event listeners can observe execution without being tightly coupled to the internal scheduling implementation.

### Asynchronous scheduling

The scheduler divides tasks into dependency levels.

Each level is processed using a bounded worker pool.

Tasks in the same level can execute concurrently, subject to the configured concurrency limit.

The implementation uses:

- `Map` for task storage.
- `Set` for dependency relationships.
- `Promise` for asynchronous operations.
- `async` and `await` for execution control.
- `EventEmitter` for event notification.

### Failure handling

A failed task is marked `FAILED`.

Its dependent tasks cannot execute because their prerequisite conditions are not satisfied.

They are marked `BLOCKED`.

The `failFast` option controls whether execution stops scheduling additional work after a failure.

The demonstration also calculates the critical path independently of actual execution time.

The sample actions use short asynchronous delays to demonstrate scheduling behavior. They are not measurements of real project task durations.

## 10. C++17 Implementation

The C++ program emphasizes explicit graph structures, deterministic traversal, and efficient STL operations.

### Data structures

| Structure | Purpose |
|---|---|
| `map` | Ordered task and adjacency storage |
| `set` | Unique and ordered dependency relationships |
| `unordered_map` | DFS traversal state |
| `priority_queue` | Efficient selection of available tasks |
| `vector` | Topological ordering and critical paths |

The graph uses ordered containers to produce reproducible output.

Kahn's algorithm uses a min-priority queue.

This ensures that the lexicographically smallest currently available task is selected first.

### Error handling

Custom exceptions distinguish dependency errors from cycle errors.

Invalid tasks, duplicate identifiers, unknown dependencies, and cycles are rejected.

A rejected dependency insertion restores the original graph state.

The program validates both topological ordering methods before reporting successful execution.

The C++ implementation uses standard-library facilities only.

## 11. Java 17 Implementation

The Java implementation separates domain modeling, graph storage, scheduling policies, and execution-state management.

### Domain model

The `Task` and `Dependency` records represent immutable domain values.

The `TaskStatus` enum defines the permitted task lifecycle states.

### Repository

The `Repository` class stores tasks and dependency relationships.

It provides:

- Task registration.
- Dependency validation.
- Incoming dependency lookup.
- Outgoing dependency lookup.
- Cycle detection.
- Controlled dependency insertion.

### Scheduling policies

The `SchedulingPolicy` interface defines the topological-ordering contract.

Two implementations provide alternative strategies:

- `DfsPolicy`
- `KahnPolicy`

This allows the scheduling service to use either algorithm without changing repository storage.

### State transitions

The scheduling service maintains execution state separately from immutable task definitions.

The permitted transitions are:

`PENDING -> READY`

`PENDING -> BLOCKED`

`READY -> RUNNING`

`READY -> BLOCKED`

`RUNNING -> COMPLETED`

`RUNNING -> FAILED`

A task cannot become ready until all its prerequisites have completed.

Terminal states cannot transition back to active states through the provided service.

This prevents invalid execution sequences.

## 12. PostgreSQL Implementation

The SQL implementation stores the dependency graph relationally.

### Relational model

| Table | Purpose |
|---|---|
| `tasks` | Task definitions and execution states |
| `task_dependencies` | Directed dependency relationships |

The `task_dependencies` table uses a composite primary key:

`(prerequisite_id, dependent_id)`

This prevents duplicate dependency relationships.

Foreign keys maintain referential integrity.

The self-dependency constraint rejects an edge from a task to itself.

### Cycle prevention

The `prevent_dependency_cycle()` trigger uses a recursive CTE.

When a new edge is inserted, it checks whether the dependent task can already reach the proposed prerequisite.

If that path exists, the new edge would introduce a cycle.

The trigger rejects the modification.

The trigger also excludes the existing edge when evaluating an update.

### Transactional state validation

The task status trigger validates state transitions.

It also prevents a task from becoming ready while any direct prerequisite remains incomplete.

The transaction example demonstrates a valid transition of T1:

`pending -> ready -> running -> completed`

After T1 completes, T2 becomes eligible for the ready state.

### Kahn's algorithm in PostgreSQL

The `topological_order()` function implements Kahn's algorithm using temporary tables.

The temporary working table stores:

- Task identifier.
- Current indegree.
- Execution level.
- Processing status.

The temporary result table stores:

- Task identifier.
- Execution position.
- Execution level.

The function repeatedly selects a zero-indegree task and decreases the indegree of its dependents.

If unprocessed tasks remain but no zero-indegree task is available, it raises an exception.

This provides database-side cycle detection during ordering.

### Reporting

The implementation provides:

- Dependency retrieval.
- Prerequisite and dependent task reports.
- Topological ordering.
- Parallel execution levels.
- Critical path reporting.
- Dependency eligibility.
- Transitive dependency analysis.
- Project status aggregation.

The indexes support task-status filtering and dependency lookups.

## 13. Cycle Detection and Failure Conditions

A directed cycle makes topological sorting impossible.

Consider:

`A -> B -> C -> A`

Every vertex has at least one incoming dependency.

Kahn's algorithm cannot find an initial zero-indegree vertex in this isolated cycle.

DFS detects the cycle when it encounters an edge to a gray vertex.

### Important failure cases

| Failure | Expected behavior |
|---|---|
| Duplicate task identifier | Reject insertion |
| Unknown prerequisite | Reject dependency |
| Unknown dependent | Reject dependency |
| Self-dependency | Reject immediately |
| Duplicate edge | Ignore without modifying the graph |
| Directed cycle | Reject dependency or sorting |
| Missing prerequisite completion | Prevent task readiness |
| Failed prerequisite | Block dependent execution |
| Empty graph | Return an empty ordering |
| Disconnected graph | Process every component |
| Multiple valid orderings | Return one deterministic or valid ordering |

Cycle prevention during edge insertion is useful for maintaining graph integrity.

A complete validation pass is still necessary when importing existing graph data or processing modifications from an external system.

## 14. Performance Analysis

Let V denote the number of tasks and E denote the number of dependency relationships.

| Operation | DFS | Kahn |
|---|---|---|
| Graph traversal | O(V + E) | O(V + E) |
| Cycle detection | O(V + E) | O(V + E) |
| Ordering with ordinary stack or queue | O(V + E) | O(V + E) |
| Ordering with binary heap | Not required | O((V + E) log V) |
| Graph storage | O(V + E) | O(V + E) |
| Auxiliary traversal memory | O(V) | O(V) |

The priority-based versions add deterministic tie-breaking.

The JavaScript sorted-array implementation can require additional sorting and shifting work. A binary heap would be preferable for large graphs.

The SQL implementation uses indexed relational operations and temporary working tables. Its actual performance depends on the database execution plan, graph size, transaction isolation, and indexing strategy.

For large dependency networks, additional considerations include:

- Avoiding repeated complete cycle checks after every edge insertion.
- Processing dependency changes in batches.
- Using iterative DFS to avoid recursion limits.
- Maintaining a cached topological order when graph updates are infrequent.
- Invalidating cached schedules after dependency changes.
- Limiting concurrent execution according to resource availability.
- Measuring database query plans on representative workloads.

## 15. Practical Applications

Topological sorting is applicable whenever activities have precedence constraints.

| Domain | Example |
|---|---|
| Software engineering | Build-system dependency resolution |
| Project management | Task and milestone scheduling |
| Data engineering | ETL pipeline execution |
| Cloud computing | Infrastructure deployment dependencies |
| Databases | Schema migration ordering |
| Operating systems | Process dependency management |
| Education | Course prerequisite planning |
| Machine learning | Computation graph execution |
| Cybersecurity | Security remediation sequencing |
| Business operations | Approval and fulfillment workflows |

In build systems, a source module must be compiled before dependent modules can be linked.

In ETL systems, extraction and validation must finish before dependent transformation and loading tasks execute.

In deployment systems, infrastructure and database migrations must complete before application services that rely on them are released.

These are different operational applications of the same underlying graph principle.

## 16. Limitations and Engineering Considerations

Topological sorting validates precedence constraints. It does not independently solve every scheduling problem.

A production scheduler may also need:

- Resource capacity constraints.
- Worker allocation.
- Task priorities.
- Deadlines.
- Time windows.
- Retry policies.
- Cancellation handling.
- Timeout management.
- Persistent execution history.
- Distributed locking.
- Idempotent task execution.
- Dependency version management.

The parallel execution levels in these implementations assume that dependency constraints are the primary scheduling restriction.

Real systems may have resource conflicts even when tasks are graph-theoretically independent.

The critical path calculation assumes fixed task durations and sufficient execution resources. It does not automatically account for resource contention, uncertainty, or task failures.

The JavaScript demonstration processes dependency levels sequentially. Tasks within a level execute concurrently, while subsequent levels wait for the current level to finish.

The Java and Python examples model execution state and validation rather than providing distributed execution infrastructure.

The PostgreSQL implementation provides transactional integrity for individual operations, but a production multi-user scheduler would also require concurrency controls around graph modifications and scheduling decisions.

## 17. Execution and Validation

### Python

Run the script using Python 3.10 or later:

`python topological_sorting.py`

### JavaScript

Run using Node.js:

`node topological_sorting.js`

### C++17

Compile and execute:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic topological_sorting.cpp -o topological_sorting`

`./topological_sorting`

### Java 17

Compile and execute:

`javac TopologicalSortingEnterprise.java`

`java TopologicalSortingEnterprise`

### PostgreSQL

Execute the SQL file in a PostgreSQL 15+ database with permission to create schemas, functions, triggers, and tables.

The script creates the `dependency_lab` schema and its objects.

It deliberately drops an existing schema with that name before recreating it. Do not run it against a schema containing data that must be preserved.

The cycle-prevention and invalid-transition examples are included as separate test statements in SQL comments so that the main script can complete successfully.

### Validation criteria

A correct implementation must satisfy the following properties:

1. Every task appears exactly once in the topological ordering.
2. Every prerequisite appears before its dependent.
3. Independent tasks may appear in different valid orders.
4. Both DFS and Kahn produce valid orderings for an acyclic graph.
5. A directed cycle is detected.
6. A rejected dependency insertion does not corrupt the original graph.
7. Execution levels respect all dependency relationships.
8. A task cannot become ready while its prerequisites are incomplete.
9. The critical path calculation respects task durations.
10. An empty graph produces an empty topological ordering.

These properties establish the correctness of the dependency model and its scheduling operations.
