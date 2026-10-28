# N-Queens and Maze Problems

## Scope

This project studies two closely related constraint-search problems:

- **N-Queens:** place `N` queens on an `N × N` chessboard so that no two queens share a row, column, or diagonal.
- **Maze path generation:** enumerate valid paths through an open grid while preventing cycles and respecting blocked cells.

The implementations treat these as search problems rather than as isolated puzzles. Board representation, constraint checking, recursive backtracking, pruning, path state, validation, and shortest-path search are represented explicitly across five technical perspectives.

The four central concepts are deliberately separated:

| Concept | N-Queens | Maze |
|---|---|---|
| State representation | One queen column per row | Current grid position plus visited cells |
| Constraint | Column and diagonal conflicts | Bounds, blocked cells, and repeated cells |
| Search | Backtracking | Backtracking for all paths |
| Pruning | Reject threatened columns and diagonals | Reject invalid or already visited cells |
| Shortest solution | Not the primary objective | Breadth-first search provides shortest path |

## Domain Model

The common search relationship is:

`Problem → State → Candidate Move → Constraint Check → Pruning → Recursive Search → Solution`

For N-Queens:

`Board → Row → Candidate Column → Column/Diagonal Check → Place Queen → Recurse → Undo`

For maze generation:

`Grid → Current Position → Neighbor → Open/Unvisited Check → Move → Recurse → Undo`

The two problems share the backtracking pattern but have different state semantics.

A queen placement permanently represents one decision for a board row during the current branch. A maze path represents a sequence of movements, and the visited set must be restored when recursion returns so that another independent path can reuse the cell.

## Board Representation

### N-Queens

The implementations represent a solution as a one-dimensional sequence:

`placement[row] = column`

For example, `[1, 3, 0, 2]` represents:

- row 0 → column 1
- row 1 → column 3
- row 2 → column 0
- row 3 → column 2

This avoids storing an entire two-dimensional board during search.

Three constraint collections are maintained:

| Collection | Meaning |
|---|---|
| `columns` | Columns already occupied |
| `row - column` | One diagonal direction |
| `row + column` | The other diagonal direction |

A candidate is valid only when all three corresponding constraints are unused.

This changes conflict detection from scanning all previously placed queens to constant-time average membership checks in the Python and JavaScript implementations.

### Maze

The maze is represented as a rectangular collection of cells.

` . ` represents an open cell.

` # ` represents a blocked cell.

A position is represented by a row and column pair.

The search state consists of:

- current position
- current path
- visited positions
- target position

Four movement directions are supported:

`up → down → left → right`

The visited set is local to the current recursive branch. This is essential because permanently marking a cell after one path has explored it would incorrectly remove that cell from other possible paths.

## Constraint Checking

N-Queens checks three independent constraints before placing a queen:

1. The column must be unused.
2. `row - column` must be unused.
3. `row + column` must be unused.

The row itself does not require a separate set because the recursive algorithm places exactly one queen in each row.

Maze search checks:

1. The position must be inside the board.
2. The cell must be open.
3. The cell must not already occur in the current path.

These checks are applied before recursion. Invalid states therefore never become deeper search states.

## Backtracking

Backtracking follows a state-transition pattern:

`choose → validate → apply → recurse → undo`

For N-Queens, placing a queen updates the column and diagonal sets. After the recursive call returns, those entries are removed.

For maze generation, moving to a neighbor adds the position to the path and visited set. Returning from recursion removes it from both.

The undo step is what allows one search tree to represent many candidate solutions without copying the complete state at every recursive call.

## Pruning

Pruning is the primary reason constraint-aware backtracking is useful.

A naive N-Queens implementation could place queens without checking conflicts and validate the complete board later. That explores many states that can already be proven impossible.

The implemented approach rejects a candidate immediately when its column or either diagonal is occupied.

For maze generation, blocked cells and repeated cells are rejected before recursion. The visited set also prevents cycles such as:

`A → B → C → B`

without requiring a separate global path-history structure.

The maze implementation places a configurable `max_paths` limit around complete path generation. This is an important operational control because the number of simple paths can grow rapidly.

## Python Implementation

The Python file provides two principal classes:

- `NQueensSolver`
- `Maze`

`NQueensSolver` uses sets for constant-time average conflict membership. It supports both complete solution generation and solution counting.

`Maze` provides:

- complete path generation with a path limit
- shortest-path discovery
- path rendering
- rectangular-grid validation

Python `dataclass` structures provide immutable `Position` values and explicit solver state. Exceptions are used for invalid board sizes, malformed mazes, and invalid path-generation limits.

The script also contains assertions covering:

- 1-Queens
- 2-Queens
- 3-Queens
- 4-Queens
- reachable maze paths
- blocked maze behavior
- shortest-path existence

## JavaScript Implementation

The JavaScript file models positions with a `Position` class and uses `Set` and `Map` collections for state management.

The N-Queens implementation keeps three sets:

- occupied columns
- descending diagonals
- ascending diagonals

The maze implementation uses a `Set` containing serialized position keys such as `2,3`.

The shortest-path implementation uses an array as a queue with a moving head index. This avoids repeated removal from the beginning of an array and keeps queue processing efficient.

The entry point is asynchronous and terminates with a nonzero process status when validation fails. No external npm package is required.

## C++17 Implementation

The C++ implementation presents the problem as a reusable technical case study.

`NQueensSolver` uses:

- `std::vector`
- `std::set`
- boolean constraint arrays
- recursive search
- explicit validation

The maze implementation uses `Position`, `std::set`, vectors, and `std::optional`.

The C++ version uses fixed-size direction definitions and separates recursive path generation from public maze operations.

The shortest-path implementation uses breadth-first search. Since every movement has equal cost, the first time the target is reached produces a shortest path.

The program handles invalid board dimensions, malformed maze rows, unreachable targets, and invalid generated solutions through exceptions.

## Java 17 Implementation

The Java implementation models the domain with explicit types:

| Type | Responsibility |
|---|---|
| `Position` | Immutable row and column |
| `Cell` | Open and blocked cell semantics |
| `SearchPolicy` | Search-policy abstraction |
| `NQueensSolver` | Constraint-based queen search |
| `Maze` | Maze validation and path operations |
| `BreadthFirstPolicy` | Shortest-path policy |

Java records provide immutable position values. Collections such as `Set`, `Map`, `List`, and `ArrayDeque` represent search state and traversal structures.

The `SearchPolicy` interface separates the search strategy from the maze model. The supplied breadth-first policy delegates to the maze's shortest-path operation, keeping path-generation and shortest-path concerns distinct.

## PostgreSQL Model

The PostgreSQL implementation models the puzzle domain relationally.

The main relationships are:

`Puzzles → N-Queens Boards → N-Queens Solutions`

and

`Puzzles → Mazes → Maze Cells → Positions`

Search execution is represented separately:

`Puzzles → Search Runs → Maze Paths`

### Important Tables

| Table | Purpose |
|---|---|
| `puzzles` | Identifies puzzle instances |
| `n_queens_boards` | Stores board dimensions |
| `n_queens_solutions` | Stores queen placements |
| `mazes` | Stores maze dimensions |
| `maze_cells` | Stores individual grid cells |
| `positions` | Defines maze start and target |
| `search_runs` | Tracks search execution state |
| `maze_paths` | Stores generated paths |

The database uses primary keys, foreign keys, unique constraints, check constraints, partial indexes, views, functions, and triggers.

## Database-Level Validation

N-Queens placement validation is implemented through `validate_n_queens_placement`.

The function checks:

- correct number of positions
- column bounds
- duplicate columns
- diagonal conflicts

A trigger invokes this function before inserting or updating an N-Queens solution.

Maze start and target positions are also protected by a trigger. The trigger verifies that:

- the maze exists
- coordinates are inside the declared dimensions
- the referenced cell is open

This moves important integrity rules into the database rather than depending entirely on application code.

## Search Runs and Workflow State

Maze search executions use the `search_status` enumeration:

`PENDING → RUNNING → COMPLETED`

A failed execution may use:

`FAILED`

The schema prevents a pending run from having a start timestamp and requires a timestamp for non-pending states.

This provides a persistent representation of search execution state instead of treating a search as an untracked function call.

## Queries and Reporting

The PostgreSQL script includes queries for:

- retrieving open maze cells
- validating stored N-Queens solutions
- aggregating generated paths
- identifying shortest paths
- evaluating JSON path structures
- reporting search status
- reconstructing maze rows
- identifying blocked cells

The `v_maze_open_cells` view provides a reusable representation of accessible cells.

The `v_merge_style_search_report` view presents execution status and derives a high-level outcome such as `REACHABLE`, `NO_PATH`, or `FAILED`.

## Shortest Path Versus All Paths

These are different computational problems.

All-path generation uses depth-first backtracking and attempts to enumerate simple paths. Its output can become very large even for moderately sized grids.

Shortest-path search uses breadth-first search. With uniform movement cost, BFS finds a minimum-length path without enumerating every possible path.

Therefore:

| Requirement | Appropriate algorithm |
|---|---|
| Find every simple path | Backtracking |
| Find one feasible path | Backtracking or DFS |
| Find shortest unweighted path | BFS |
| Enumerate only a bounded number of paths | Backtracking with a path limit |

The project intentionally implements both backtracking and BFS because they solve different maze requirements.

## Complexity

### N-Queens

The search has exponential or factorial-style growth depending on how the search space is expressed. The important practical improvement is pruning.

With `N` rows, each recursive level considers candidate columns, but conflicts are rejected before deeper recursion.

The memory required for the active search state is approximately `O(N)` excluding stored solutions. Storing all solutions adds the size of the solution collection.

### Maze Path Generation

For a grid containing `R × C` cells, a simple-path enumeration problem can have a very large number of possible paths. Backtracking therefore has exponential worst-case behavior relative to the grid size.

The active recursive state requires approximately `O(R × C)` space for the path and visited set.

The `max_paths` limit controls output growth but does not change the worst-case search complexity of paths encountered before the limit is reached.

### Maze Shortest Path

BFS visits each reachable cell at most once.

For a grid with `R × C` cells:

- time: `O(R × C)`
- auxiliary space: `O(R × C)`

This makes BFS substantially more predictable than complete path enumeration.

## Edge Cases

The implementations explicitly handle:

- `N = 1`
- `N = 2`
- `N = 3`
- invalid N-Queens sizes
- empty mazes
- non-rectangular mazes
- invalid maze characters
- blocked start cells
- blocked target cells
- unreachable targets
- repeated maze positions
- excessive path enumeration
- invalid stored queen placements
- invalid database maze positions

The 2-Queens and 3-Queens cases correctly produce no solutions.

## Security and Reliability Considerations

The source implementations do not execute external commands or load untrusted code.

For database usage, integrity is enforced with constraints and triggers so that malformed solutions cannot be inserted through ordinary SQL writes.

Path enumeration is potentially expensive. Production applications should treat path limits as an operational control rather than accepting unlimited enumeration.

N-Queens input size is also bounded in the examples because unrestricted exhaustive search can become computationally expensive.

Database JSON paths are structurally validated as arrays, while relational maze coordinates remain normalized in `maze_cells` and `positions`.

## Practical Workflow

A typical execution flow is:

`Define Board/Grid`
       |
       v
`Validate Input`
       |
       v
`Initialize Search State`
       |
       v
`Choose Candidate`
       |
       v
`Check Constraints`
       |
   +---+---+
   |       |
 Invalid  Valid
   |       |
   |       v
   |    `Apply State`
   |       |
   |       v
   |    `Recurse`
   |       |
   |       v
   |    `Undo State`
   |       |
   +-------+
       |
       v
`Record Solution`

For shortest maze paths, the workflow changes to:

`Grid`
  |
  v
`Start Queue`
  |
  v
`Visit Cell`
  |
  v
`Enqueue Valid Neighbors`
  |
  v
`Record Parent`
  |
  v
`Reach Target`
  |
  v
`Reconstruct Path`

## Running the Source Files

The Python program requires Python 3 and uses only the standard library.

The JavaScript program requires a Node.js runtime and uses no external packages.

The C++ source requires a C++17-compatible compiler.

The Java source requires Java 17 or later.

The PostgreSQL script requires a PostgreSQL server supporting the used enum, JSONB, trigger, function, and generated-series features.

The programs are self-contained demonstrations and print their validation results and representative solutions directly to standard output.

## Technical Distinctions

N-Queens and maze problems are both search problems, but their state spaces differ substantially.

N-Queens is primarily a constraint-satisfaction problem. The central operation is determining whether a new queen is compatible with decisions already made.

Maze path generation is a graph traversal problem constrained by grid geometry. The central operation is determining which neighboring states can be entered without violating the current path.

Backtracking provides a common mechanism for both, while BFS supplies a separate solution for shortest-path requirements. This distinction prevents the implementations from treating every search problem as the same algorithmic task.
