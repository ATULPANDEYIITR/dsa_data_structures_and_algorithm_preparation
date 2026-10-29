# Sudoku and Backtracking Assessment

## Scope

This assessment uses Sudoku as the primary constraint-satisfaction problem and then applies the same recursive search pattern to mixed backtracking problems.

The central pattern is:

Choice → Constraint → Recursive Call → Undo Choice

A backtracking algorithm makes a candidate decision, checks whether that decision remains legal, explores the resulting state recursively, and restores the previous state when the branch cannot produce a solution.

The four concepts have distinct roles:

| Concept | Meaning |
|---|---|
| Choice | A candidate value or action selected for the current state |
| Constraint | A rule that determines whether the choice is legal |
| Recursive call | Exploration of the state produced by the choice |
| Undo choice | Restoration of the previous state after a failed branch |

Sudoku provides a useful assessment problem because every empty cell has a finite candidate set and every candidate affects three constraint groups: its row, column, and 3×3 box.

## Sudoku Constraint Model

A Sudoku board contains 81 cells arranged as nine rows, nine columns, and nine 3×3 boxes.

A valid placement must satisfy three simultaneous constraints:

1. The value must not already occur in the cell's row.
2. The value must not already occur in the cell's column.
3. The value must not already occur in the cell's 3×3 box.

The implementations use `0` as the representation of an empty cell.

The search state can be viewed as:

`Board + Row Constraints + Column Constraints + Box Constraints`

For an empty cell `(r, c)`, its candidate set is:

`{1,2,3,4,5,6,7,8,9} - rowValues - columnValues - boxValues`

The solver then selects a candidate and recursively continues.

## Search Strategy

The implementations use a most-constrained-cell strategy. Instead of selecting the first empty cell, the solver examines candidate counts and selects the empty cell with the smallest legal candidate set.

This is a practical search heuristic because a cell with fewer choices produces a smaller branching factor and exposes contradictions earlier.

The recursive sequence is:

1. Find an unresolved cell.
2. Calculate its legal candidates.
3. Select one candidate.
4. Add the candidate to the board and constraint structures.
5. Recursively search the resulting state.
6. If the branch fails, remove the candidate.
7. Continue with the next candidate.
8. Report success when no unresolved cells remain.

An empty candidate set is a contradiction. It means the current partial board cannot be completed.

## Python Implementation

The Python implementation uses `dataclass` objects for solver results and an `Enum` for the final solving state.

`SudokuSolver` maintains independent sets for rows, columns, and boxes. This avoids repeatedly scanning all nine cells in each constraint group during candidate evaluation.

The `_place` and `_undo` operations keep the board and constraint sets synchronized. This is important because backtracking modifies shared mutable state.

The solver also records:

- Number of candidate decisions
- Number of failed branches requiring undo
- Elapsed solving time

Input validation rejects malformed dimensions, invalid cell values, and contradictory fixed values before recursive search begins.

The same file contains two smaller backtracking assessments:

- Subset construction with a target sum
- Balanced-parentheses generation

These examples demonstrate that Sudoku is one instance of a broader recursive search pattern.

## JavaScript Implementation

The JavaScript implementation uses classes, `Set`, asynchronous policy evaluation, and Node.js standard-library functionality.

`SudokuBoard` owns the mutable Sudoku state. `SudokuSolver` owns the search process and metrics. This separates state management from recursive decision-making.

JavaScript `Set` objects provide efficient membership checks for row, column, and box constraints.

The file also includes subset-sum search and an asynchronous policy evaluator. The policy evaluator models a separate event-driven workflow in which multiple conditions determine eligibility.

The asynchronous function deliberately uses a Promise boundary so that policy evaluation remains compatible with larger event-driven Node.js workflows.

Validation rejects malformed boards and duplicate fixed values before search begins.

## C++17 Implementation

The C++ implementation treats Sudoku as a stateful search engine with explicit ownership of its grid and constraint sets.

The board uses fixed-size `std::array` structures because Sudoku always contains exactly nine rows and nine columns. This gives predictable storage characteristics and avoids unnecessary dynamic allocation for the core board.

`std::set<int>` is used for candidate and constraint membership. The recursive search returns a Boolean result, while `Statistics` records the search cost.

The C++ program also contains a separate combination-search case. The combination problem demonstrates the same state mutation pattern without Sudoku-specific constraints.

The important C++ engineering distinction is explicit resource and state management. Every recursive placement has a corresponding undo operation on every affected data structure.

## Java 17 Implementation

The Java implementation uses records for immutable domain values such as `Position`, `SearchChoice`, `SolveMetrics`, and `SolveResult`.

The `Sudoku` class owns mutable search state, while `CombinationSearch` implements a separate search problem through the generic `SearchProblem<S, R>` interface.

The explicit domain types make the search state easier to reason about:

`Position → SearchChoice → SolveResult`

Java collections provide the constraint sets, while streams are used to produce deterministic sorted candidate traversal.

The enterprise-oriented design separates:

- Input validation
- Constraint initialization
- Candidate calculation
- State mutation
- Recursive search
- Result reporting

The same recursive invariant is preserved across the different domain implementations.

## PostgreSQL Model

The PostgreSQL implementation represents the assessment as relational state rather than as an in-memory recursive algorithm.

The principal entities are:

`puzzles → puzzle_cells`

`puzzles → solving_runs → backtracking_steps`

`puzzles` stores assessment-level state.

`puzzle_cells` stores individual Sudoku coordinates, given values, and solved values.

`solving_runs` records the outcome and performance characteristics of a solver execution.

`backtracking_steps` records individual search decisions, rejections, and undo operations.

The relational design separates the puzzle definition from the execution history. This allows multiple solving runs for the same puzzle without overwriting the original puzzle state.

## Database Integrity

Primary keys uniquely identify puzzles, cells, solving runs, and search steps.

Foreign keys enforce relationships between the entities.

Check constraints restrict:

- Sudoku coordinates to 1 through 9
- Cell values to 1 through 9 when present
- Search depth and counters to non-negative values
- Run results to known states
- Backtracking actions to `choice`, `reject`, or `undo`

A deferred constraint trigger checks Sudoku given-value conflicts after a statement transaction has enough information to evaluate the puzzle state.

Indexes support common access paths for puzzle cells, solving results, and chronological search-depth analysis.

## Transactional Workflow

The SQL script demonstrates a transaction in which:

1. A solving run is created.
2. Solved values are recorded.
3. Puzzle status is changed.
4. The transaction is committed.

This ensures that related state changes are committed together.

A solver workflow should not expose a puzzle as successfully solved while its associated state remains incomplete.

## Mixed Backtracking Problems

Sudoku is a constraint-satisfaction problem, but the same structure appears in many search problems.

### Subset Sum

The subset-sum implementations maintain a path and a remaining target.

A value is selected when it can contribute to the target. The recursive call explores the remaining values. The value is removed from the path after returning.

The sorted input enables an early stop when the current value exceeds the remaining target.

The four-step structure remains explicit:

`Choose value → validate remaining target → recurse → remove value`

### Parentheses Generation

The Python implementation also generates balanced parentheses.

Its constraints are different from Sudoku:

- The number of opening parentheses cannot exceed the requested total.
- The number of closing parentheses cannot exceed the number of opening parentheses.
- A result is complete only after both counts reach the requested total.

The choice is either an opening or closing parenthesis. The constraint determines whether that choice is legal.

This distinction demonstrates why backtracking is a technique rather than a single algorithm. The recursive structure stays stable while the state and constraints change.

## Complexity

Sudoku has a finite but potentially large search space. A naive upper bound can be expressed in terms of up to nine choices for each of 81 cells, although Sudoku constraints reduce the practical search space substantially.

The most-constrained-cell heuristic reduces branching by selecting cells with fewer candidates.

For each candidate, constraint membership is checked against row, column, and box structures.

The dominant cost is recursive search rather than board storage.

Subset generation is exponential in the number of input elements because the algorithm may need to examine many subsets. Sorting and pruning reduce the practical number of explored branches for positive target values.

Parentheses generation is proportional to the number of valid sequences produced, with the Catalan-number growth characteristic of balanced-parentheses generation.

## Failure Conditions

The implementations explicitly handle:

- Invalid board dimensions
- Values outside the Sudoku domain
- Duplicate fixed values
- Empty candidate sets
- Unsolvable puzzles
- Negative subset targets
- Invalid asynchronous policy input
- Inconsistent database states
- Invalid solving results
- Negative search counters

A failed recursive branch is not treated as an exceptional program failure. It is a normal search outcome and causes the algorithm to execute the undo operation.

Input corruption and invalid domain state are handled separately through validation and exceptions.

## State Invariants

A correct backtracking implementation must preserve several invariants.

For Sudoku:

- Every non-empty row contains unique values.
- Every non-empty column contains unique values.
- Every non-empty box contains unique values.
- Constraint sets correspond exactly to the current board.
- Every recursive return restores the state of failed branches.

The most important invariant is state restoration.

If a candidate is placed but not removed after a failed recursive branch, later branches operate on corrupted state and can produce incorrect results.

## Security and Reliability Considerations

The implementations do not execute external commands, load arbitrary code, or require third-party runtime dependencies.

Input validation limits Sudoku values to the expected domain and prevents malformed dimensions from entering recursive search.

For production services, recursive depth and execution time should be bounded when inputs are user-controlled. A deliberately difficult search problem can consume substantial CPU time.

Database writes should use transactions, foreign keys, constraints, and controlled privileges. Search-history tables should not grant arbitrary users permission to alter solver results.

Operational systems can also record solver duration, decision count, backtrack count, and failure state for diagnosing pathological inputs.

## Relationship Between the Concepts

The four assessment concepts should not be treated as interchangeable:

| Concept | Role in the solver |
|---|---|
| Choice | Select a candidate for the current state |
| Constraint | Reject candidates that violate the problem rules |
| Recursive call | Explore the consequences of an accepted candidate |
| Undo choice | Restore the state when exploration fails |

For Sudoku:

`Empty cell → candidate digit → row/column/box validation → recursive search → remove digit`

For subset sum:

`Unused value → remaining-target validation → recursive search → remove value`

For balanced parentheses:

`Opening/closing parenthesis → count constraint → recursive search → remove character`

The domain-specific constraints change, but the search architecture remains recognizable.

## Practical Assessment Criteria

A correct backtracking implementation should be evaluated for more than whether it produces one correct answer.

| Criterion | Required behavior |
|---|---|
| Choice | Selects a valid candidate |
| Constraint | Rejects illegal states before deeper search |
| Recursion | Explores the new state |
| Undo | Restores state after failure |
| Termination | Detects both success and contradiction |
| Validation | Rejects malformed initial input |
| State consistency | Keeps auxiliary structures synchronized |
| Edge cases | Handles unsolvable and already-solved inputs |
| Performance | Reduces branching where practical |
| Observability | Reports meaningful search metrics |

The resulting architecture makes the central backtracking assessment explicit: every recursive search step is a controlled state transition whose failed branches can be safely reversed.
