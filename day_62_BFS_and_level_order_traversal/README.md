# BFS and Level-Order Traversal

## 1. Domain Overview

Breadth-First Search (BFS) is a traversal algorithm that explores nodes in increasing order of their distance from a starting node.

For a tree, BFS processes the root first, followed by its children, then their children. A FIFO (First In, First Out) queue maintains this processing order.

The implementations in this repository use binary trees and organizational hierarchies to demonstrate queue-based traversal, level separation, and hierarchical analytics.

### Core relationship

- **BFS:** The underlying traversal strategy that visits nodes in breadth-first order.
- **Level-order traversal:** A BFS operation that groups visited nodes according to their depth.
- **Level averages:** An aggregation over the values belonging to each depth.
- **Zigzag traversal:** A level-order presentation that alternates direction between consecutive levels.

These operations share the same traversal foundation but produce different outputs.

## 2. Learning Objectives

The implementations address the following concepts:

| Concept | Technical objective |
|---|---|
| FIFO queue | Maintain breadth-first processing order |
| Queue processing | Visit previously discovered nodes before their descendants |
| Level separation | Capture the queue size before processing each level |
| Tree construction | Build hierarchical structures from level-order input |
| Level-order traversal | Group nodes by depth |
| Level averages | Calculate numerical aggregates for each level |
| Zigzag traversal | Reverse presentation direction on alternating levels |
| Hierarchical analytics | Generate depth-based statistics |
| Validation | Reject invalid tree structures and inconsistent data |
| Testing | Verify traversal order and boundary conditions |

## 3. BFS Fundamentals

### 3.1 Queue-Based Traversal

BFS uses a FIFO queue.

The algorithm begins by inserting the root node into the queue.

For every iteration:

1. Remove the node at the front.
2. Process its value.
3. Insert its existing children at the back.
4. Continue until the queue becomes empty.

The queue ensures that nodes discovered earlier are processed earlier.

For a tree with the following structure:

        10
       /  \
      20   30
     / \   / \
    40 50 60 70

The queue evolves as follows:

| Operation | Queue |
|---|---|
| Initialize | 10 |
| Process 10 | 20, 30 |
| Process 20 | 30, 40, 50 |
| Process 30 | 40, 50, 60, 70 |
| Process remaining nodes | Empty |

The resulting traversal is:

`10, 20, 30, 40, 50, 60, 70`

### 3.2 Level Separation

Ordinary BFS produces a sequence of nodes. Level-order traversal introduces an additional requirement: identify which nodes belong to the same depth.

The important implementation decision is to capture the queue size before processing a level.

If the queue contains three nodes at the beginning of a level, exactly three nodes must be processed before moving to the next level.

Children inserted during these operations belong to the next level.

This avoids mixing parent and child nodes in the same result group.

For the example tree:

| Depth | Nodes |
|---|---|
| 0 | 10 |
| 1 | 20, 30 |
| 2 | 40, 50, 60, 70 |

### 3.3 Level-Order Processing

Once nodes are separated by depth, additional operations become straightforward.

Each level can be processed independently for:

- Aggregation
- Filtering
- Statistical analysis
- Reporting
- Reordering
- Hierarchical visualization

The traversal order remains unchanged unless a presentation-specific operation modifies the resulting levels.

## 4. Level Averages

Level averages calculate the arithmetic mean of all node values at a particular depth.

For a level containing values \(x_1, x_2, \ldots, x_n\):

\[
Average = \frac{\sum_{i=1}^{n}x_i}{n}
\]

Consider:

| Depth | Values | Average |
|---|---|---:|
| 0 | 10 | 10 |
| 1 | 20, 30 | 25 |
| 2 | 40, 50, 60, 70 | 55 |

The average calculation is performed independently for each level.

The implementations also calculate:

- Node count
- Minimum value
- Maximum value
- Total value

Using a sufficiently wide accumulator prevents avoidable integer overflow during aggregation. Floating-point averages are used where appropriate.

An empty tree produces an empty result rather than attempting to calculate an average over zero elements.

## 5. Zigzag Traversal

Zigzag traversal preserves BFS level discovery while alternating the order in which values are presented.

The traversal follows two directions:

- Even-numbered levels: left to right.
- Odd-numbered levels: right to left.

For the sample tree:

| Depth | Standard order | Zigzag order |
|---|---|---|
| 0 | 10 | 10 |
| 1 | 20, 30 | 30, 20 |
| 2 | 40, 50, 60, 70 | 40, 50, 60, 70 |

The resulting traversal is:

`[[10], [30, 20], [40, 50, 60, 70]]`

The distinction between traversal and presentation is important. Zigzag traversal does not change the underlying tree or the BFS discovery order.

The Python implementation uses a deque for directional insertion. C++ uses indexed placement in a preallocated level vector. JavaScript and Java reverse alternating completed levels.

## 6. Implementation Architecture

### 6.1 Python

The Python implementation provides a reusable `BinaryTree` class.

| Component | Responsibility |
|---|---|
| `TreeNode` | Represents an individual binary tree node |
| `BinaryTree` | Owns the tree and traversal operations |
| `from_level_order()` | Constructs a tree from an input sequence |
| `level_order()` | Returns depth-separated values |
| `flat_level_order()` | Returns the ordinary BFS sequence |
| `level_averages()` | Calculates per-level means |
| `zigzag_traversal()` | Alternates level presentation |
| `level_statistics()` | Calculates depth-based metrics |
| `find()` | Searches for a value using BFS |
| `serialize()` | Converts the tree into JSON |
| `deserialize()` | Reconstructs the tree from JSON |

**Important implementation mechanisms**

- `collections.deque` provides efficient queue operations.
- Dataclasses represent tree nodes.
- Lists store level results.
- JSON supports tree serialization.
- Exceptions reject invalid representations.
- `unittest` verifies expected traversal behavior.

The tree uses `None` to represent absent children.

The serialization mechanism removes unnecessary trailing null values while retaining internal gaps.

### 6.2 JavaScript

The JavaScript implementation focuses on asynchronous and event-driven traversal.

| Component | Responsibility |
|---|---|
| `TreeNode` | Stores node values and child references |
| `BFSProcessor` | Executes queue-based traversal |
| `TreeAnalytics` | Calculates level-based results |
| `RepositoryTreeMonitor` | Collects traversal events and audit records |

The `BFSProcessor` extends Node.js `EventEmitter`.

It emits:

| Event | Meaning |
|---|---|
| `levelStart` | A new depth is beginning |
| `visit` | A node is being processed |
| `levelEnd` | Processing of the current level is complete |
| `complete` | Traversal has finished |
| `errorOccurred` | Traversal has encountered a failure |

The asynchronous traversal method supports:

- Execution delays between levels
- Cancellation through `AbortSignal`
- Early termination using a predicate
- Event-based monitoring
- Error propagation

The implementation uses an array with a moving head index instead of repeatedly calling `Array.shift()`. This avoids repeatedly moving remaining queue elements.

Audit records can be written to a local JSON file with restrictive file permissions.

### 6.3 C++17

The C++ implementation uses an ownership-oriented design.

| Component | Responsibility |
|---|---|
| `TreeNode` | Stores a node and its children |
| `BinaryTree` | Encapsulates the hierarchy |
| `LevelReport` | Stores depth-specific statistics |
| `fromLevelOrder()` | Constructs a tree |
| `levelOrder()` | Performs standard BFS |
| `zigzagTraversal()` | Performs alternating presentation |
| `statistics()` | Calculates level metrics |
| `rightSideView()` | Finds the last node at each depth |

**Engineering decisions**

- `std::unique_ptr` manages child ownership.
- `std::queue` provides FIFO processing.
- `std::optional` represents missing nodes.
- `std::vector` stores traversal results.
- `std::numeric_limits` initializes statistical boundaries.
- Exceptions report invalid tree input and execution failures.

The zigzag implementation preallocates each level's output vector and places values at calculated indices. This avoids reversing the completed level.

The implementation also separates node ownership from traversal references. Queue entries use non-owning pointers because the tree owns the actual nodes.

### 6.4 Java 17

The Java implementation models BFS as an enterprise hierarchy analytics service.

The example organization contains:

- Executive Office
- Technology
- Operations
- Security
- Engineering
- Analytics
- Infrastructure
- Support

The hierarchy demonstrates how BFS can support organizational reporting.

**Domain components**

| Component | Responsibility |
|---|---|
| `Department` | Immutable department information |
| `HierarchyNode` | Represents parent-child relationships |
| `HierarchyRepository` | Validates and stores the hierarchy root |
| `HierarchyAnalyticsService` | Performs traversal and analysis |
| `HierarchyWorkflow` | Controls processing state |
| `LevelMetrics` | Stores level-based statistics |
| `ProcessingResult` | Returns an immutable processing result |

Java records provide immutable data structures for department information and analytical results.

The repository checks for duplicate department identifiers and repeated node references. This prevents shared-node structures and cycles from being accepted as valid trees.

The analytics service supports:

- Standard BFS
- Level averages
- Zigzag traversal
- Bottom-up traversal
- Workload filtering
- Level-based reporting

The workflow uses explicit processing states:

`PENDING → PROCESSING → COMPLETED`

A failed execution enters `FAILED`.

Repeated execution of a completed workflow is rejected.

### 6.5 PostgreSQL

The SQL implementation models organizational hierarchies using relational tables.

The database represents a tree through an adjacency-list structure.

Each department stores its parent identifier in `parent_department_id`.

A root department has a null parent identifier.

**Relational structure**

| Table | Purpose |
|---|---|
| `organizations` | Stores organization records |
| `departments` | Stores department hierarchy and workload |
| `traversal_results` | Records traversal execution |
| `traversal_audit` | Records individual node processing positions |

The `departments` table uses a self-referencing foreign key.

Constraints enforce:

- Valid organization references
- Valid parent references
- Non-negative workload
- Unique department codes within an organization
- Prevention of direct self-parent relationships

A trigger checks organization consistency and rejects indirect hierarchy cycles.

The timestamp trigger automatically updates `updated_at` whenever a department record changes.

**Recursive CTEs**

PostgreSQL recursive common table expressions calculate hierarchy depth.

The anchor query identifies root departments.

The recursive query joins each parent to its children and increases the depth by one.

A path array tracks previously visited identifiers and provides an additional cycle safeguard during traversal.

The `get_hierarchy_levels()` function exposes the calculated hierarchy.

The `calculate_level_metrics()` function calculates workload statistics grouped by depth.

The `execute_bfs_traversal()` procedure records traversal execution and node positions transactionally.

## 7. Complexity Analysis

Let:

- \(N\) represent the number of nodes.
- \(H\) represent the height of the tree.
- \(W\) represent the maximum number of nodes at any level.

| Operation | Time complexity | Auxiliary space |
|---|---|---|
| Tree construction | \(O(N)\) | \(O(W)\) |
| BFS traversal | \(O(N)\) | \(O(W)\) |
| Level-order traversal | \(O(N)\) | \(O(N)\) including output |
| Level averages | \(O(N)\) | \(O(H)\) for results |
| Zigzag traversal | \(O(N)\) | \(O(W)\) auxiliary, excluding output |
| BFS search | \(O(N)\) | \(O(W)\) |
| Right-side view | \(O(N)\) | \(O(H)\) for results |

A complete binary tree can have a large final level, making queue memory proportional to its width.

A highly unbalanced tree can have a queue containing very few nodes at a time.

The traversal itself remains linear because every node is inserted and removed from the queue once.

## 8. Edge Cases and Validation

The implementations address the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty input | Return an empty tree |
| Single-node tree | Return one level |
| Missing children | Skip absent nodes |
| Sparse hierarchy | Preserve valid parent-child relationships |
| Negative node values | Accept valid integer values |
| Invalid node types | Reject invalid values |
| Missing search target | Return no result |
| Invalid root representation | Reject descendants without a root |
| Duplicate department identifiers | Reject invalid enterprise hierarchy |
| Cyclic hierarchy | Reject invalid parent relationships |
| Empty analytical result | Avoid division by zero |
| Repeated workflow execution | Reject duplicate execution |
| Interrupted asynchronous traversal | Propagate cancellation |

The implementations assume a proper tree rather than a general graph. A graph may contain cycles and multiple paths to the same node, requiring a visited set to avoid repeated processing.

## 9. Testing Strategy

The source files contain executable checks.

| Test | Expected result |
|---|---|
| Standard BFS | Correct left-to-right traversal |
| Level separation | Correct grouping by depth |
| Level averages | Correct arithmetic means |
| Zigzag traversal | Alternating direction |
| Empty tree | Empty output |
| Single-node tree | One-element result |
| Sparse tree | Correct handling of missing children |
| Search | Correct matching and missing-value behavior |
| Serialization | Equivalent restored tree |
| Invalid hierarchy | Rejected input |
| Enterprise workflow | Valid state transitions |

The tests verify actual outputs rather than relying on visual inspection.

## 10. Execution

### Python

Run the Python source file using Python 3:

`python bfs.py`

The program displays traversal results and executes its `unittest` test cases.

### JavaScript

Run the JavaScript source file using Node.js:

`node bfs.js`

The implementation uses Node.js standard-library modules and requires no external npm packages.

### C++17

Compile using:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic bfs.cpp -o bfs`

Execute using:

`./bfs`

On Windows:

`bfs.exe`

### Java 17

Compile:

`javac BFSLevelOrderEnterprise.java`

Execute:

`java BFSLevelOrderEnterprise`

### PostgreSQL

Execute the SQL file using:

`psql -U postgres -d postgres -f bfs.sql`

The script creates a dedicated `bfs_learning` schema and performs its database operations inside a transaction.

The executing database role must have permission to create schemas, tables, functions, procedures, triggers, and views.

## 11. Practical Applications

BFS and level-order processing are useful when information must be processed according to hierarchical distance.

Examples include:

- Organizational department hierarchies
- File-system directory structures
- Category and product trees
- Multi-level reporting systems
- Dependency hierarchies
- Decision trees
- Network exploration
- Hierarchical workload aggregation

For large-scale systems, traversal should consider memory consumption, maximum hierarchy depth, concurrent modifications, and input validation.

In database-backed applications, recursive CTEs provide a convenient way to query hierarchy depth without loading the entire structure into application memory.

For asynchronous applications, cancellation and event monitoring allow traversal to be integrated into larger processing workflows.

## 12. Important Technical Distinctions

| Mechanism | Primary responsibility |
|---|---|
| Queue | Controls node processing order |
| BFS | Determines breadth-first discovery |
| Level separation | Identifies depth boundaries |
| Level-order traversal | Groups nodes by depth |
| Level averages | Aggregates values within each depth |
| Zigzag traversal | Changes the presentation direction of alternating levels |
| Recursive CTE | Computes hierarchy relationships inside PostgreSQL |
| Audit records | Preserve information about traversal execution |

The queue is the central data structure. Level separation is the mechanism that converts ordinary BFS into level-order processing. Averages and zigzag traversal are separate operations performed on the resulting levels.
