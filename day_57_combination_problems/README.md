# Combination Problems

## Scope

This project implements combination problems as constraint-based search problems rather than treating recursion as a single generic technique.

The central model is:

`candidate values → decision at each level → partial combination → constraint check → pruning or continuation → valid result`

Four related but distinct patterns are implemented:

| Pattern | Core decision | Repetition | Main constraint |
|---|---|---:|---|
| Choose/not choose | Include or skip each item | No | Item position |
| Combination generation | Select positions in increasing order | No | Combination size |
| Combination sum | Select values until a target is reached | Optional | Remaining sum |
| Constraint-based recursion | Select while maintaining bounds | Usually no | Size and aggregate bounds |

The implementations use the same mathematical foundation while giving each language a different engineering perspective.

## Domain Model

A combination search maintains a partial solution called the `path`.

At each recursion level, the algorithm chooses whether to extend that path. A completed path becomes a result only when the required constraints are satisfied.

For a fixed-size combination:

`start index → candidate → recursive selection → next start index`

For a choose/not-choose search:

`candidate → CHOOSE`
`       └──→ SKIP`

For target-based search:

`remaining target → candidate → smaller remaining target`

Positive candidate values are especially useful because a value larger than the remaining target can terminate the current branch after the candidates have been sorted.

## Choose/Not Choose

The choose/not-choose pattern creates the power set of the input.

For each candidate there are exactly two decisions:

- `CHOOSE`: add the candidate to the current path.
- `SKIP`: leave the candidate out.

With `n` candidates, the search has `2^n` possible subsets.

The Python implementation exposes this as `choose_or_skip`. The JavaScript implementation uses a generator so results can be consumed lazily. The C++ implementation places the same binary decision inside a governance-oriented engine. Java uses an explicit recursive service.

The empty input has one mathematically valid result: the empty combination.

## Combination Generation

Fixed-size combination generation differs from choose/not-choose recursion because the search tracks a starting position.

After selecting position `i`, later recursion begins at `i + 1`. This prevents permutations of the same combination from being produced.

For candidates `[1, 2, 3, 4]` and size `2`, the results include:

`[1, 2]`
`[1, 3]`
`[1, 4]`
`[2, 3]`
`[2, 4]`
`[3, 4]`

The number of generated results is `C(n, k)`. An implementation cannot asymptotically avoid outputting those results when the caller requires every combination.

## Combination Sum

Combination sum changes the termination condition.

Instead of asking whether a particular number of elements has been selected, the algorithm asks whether the remaining target has reached zero.

Two policies are represented:

| Mode | Recursive next position |
|---|---|
| No reuse | `index + 1` |
| Reuse allowed | `index` |

This distinction is fundamental. Keeping the same index allows another copy of the selected value. Advancing the index means that value cannot be selected again.

Candidates are sorted and deduplicated. Since all values are positive, encountering a value greater than the remaining target allows the current loop to stop.

## Constraint-Based Recursion

Constraint-based recursion evaluates partial solutions before exploring every possible continuation.

The implementations use constraints such as:

- required combination size
- minimum aggregate sum
- maximum aggregate sum
- target sum
- value reuse policy

A branch can be rejected when its partial state proves that no valid completion is possible.

For example, if three positions remain and the smallest three available values already make the maximum permitted sum impossible, there is no reason to explore that branch.

This is stronger than checking only at leaf nodes because invalid regions of the search tree are eliminated early.

## Python Implementation

The Python file models the search space with `CombinationEngine`, `CombinationResult`, and explicit validation.

Important mechanisms include:

- `dataclass` domain objects
- `Enum` for decision semantics
- sorted and deduplicated candidate values
- recursive backtracking
- path mutation followed by restoration
- fixed-size generation
- reusable and non-reusable combination sums
- minimum and maximum constraints
- assertions for executable validation
- explicit handling of invalid and empty input

`choose_or_skip` is kept separate from `CombinationEngine` because its binary decision structure is different from target-based combination search.

The constrained search uses positive integer values to establish useful lower-bound pruning.

The script also exercises invalid input, impossible combination sizes, empty inputs, duplicate candidates, and reusable target sums.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library functionality and focuses on incremental and event-driven processing.

The `chooseOrSkip` and `combinations` functions are generators. This means a caller can consume results without requiring every result to be stored immediately.

`SearchSession` adds an application-level workflow around combination search:

`request → cache lookup → asynchronous scheduling → search → cache → event`

The session uses `Map` for memoization and `EventEmitter` for lifecycle events.

Events include:

- `started`
- `completed`
- `cacheHit`

The asynchronous boundary uses `setImmediate` so the search request participates in the Node.js event loop rather than executing as an entirely synchronous service operation.

Input validation rejects negative targets, invalid sizes, non-integer values, and non-positive candidates.

The implementation also uses a UUID for each search session, giving a practical correlation identifier for logs and operational tracing.

## C++17 Implementation

The C++ program treats combination search as a repository-governance-style decision engine.

`GovernanceCombinationEngine` owns sorted candidate values and provides:

- binary choose/not-choose search
- fixed-size combination generation
- reusable and non-reusable target sums
- bounded combination search
- node-count instrumentation

The program also introduces `PullRequestCandidate` and `GovernancePolicy` to demonstrate how a combinatorial search can become part of a concrete policy decision.

The governance evaluator checks:

- required approval count
- test status
- maximum risk
- uniqueness of changed components

This is deliberately separate from the mathematical combination generator. The search engine produces candidate sets; the governance policy evaluates whether a candidate state is acceptable.

C++17 STL containers provide deterministic storage and set-based validation. Exceptions reject invalid values and integer-overflow conditions.

## Java 17 Implementation

The Java implementation models combinations as an enterprise service.

Records represent immutable domain values:

- `PullRequest`
- `Review`
- `ApprovalPolicy`
- `StatusCheck`

Enums represent explicit state and decision semantics.

`CombinationService` owns candidate validation, fixed-size generation, target search, constraint search, and a cache keyed by target and reuse policy.

`MergeEligibilityService` demonstrates a separate policy layer. Combination search is not itself a merge decision. The policy service evaluates a pull request using its state, reviews, checks, risk, and approval requirements.

This separation creates a clear architecture:

`CombinationService → candidate solutions`

`MergeEligibilityService → policy decision`

The Java implementation uses immutable lists at domain boundaries, a `HashMap` cache for repeated searches, and a `HashSet` to count distinct eligible reviewers.

## PostgreSQL Implementation

The PostgreSQL script represents combination problems relationally.

The principal relationships are:

`combination_problems`
→ `problem_candidates`
→ `candidate_values`

and:

`combination_problems`
→ `generated_combinations`
→ `combination_members`

`evaluation_runs` provides explicit workflow state for evaluation operations.

Database constraints enforce:

- positive candidate values
- non-negative targets
- valid combination sizes
- valid evaluation states
- valid minimum and maximum relationships
- referential integrity
- uniqueness of candidate labels
- uniqueness of stored combination keys within a problem

A trigger prevents a generated combination from exceeding a configured fixed size.

The script also uses a recursive PostgreSQL CTE to generate fixed-size combinations directly inside the database.

Reporting queries demonstrate:

- retrieval
- aggregation
- target validation
- minimum and maximum validation
- member reconstruction
- workflow status reporting
- failed evaluation reporting

The transactional example inserts a generated combination and its members as one unit.

## State and Constraint Distinctions

A combination algorithm has several states that should not be confused.

| State | Meaning |
|---|---|
| Candidate | Available value that may be selected |
| Partial path | Current recursive selection |
| Remaining target | Amount still required |
| Constraint violation | Current branch cannot produce a valid result |
| Complete path | Required number or target has been reached |
| Valid result | Complete path satisfying all constraints |
| Failed evaluation | Processing could not be completed or a workflow rule failed |

An empty result is not necessarily an error. A valid problem may simply have no combination satisfying its constraints.

The PostgreSQL model explicitly distinguishes a completed evaluation with zero suitable results from a failed evaluation.

## Pruning Rules

Pruning is the main performance improvement beyond basic recursive enumeration.

The implementations use several forms.

### Target Upper Bound

With positive sorted values:

`candidate > remaining target`

means all later candidates are also too large, so the loop can stop.

### Combination Size

If the number of available candidates is smaller than the number of positions still required, the branch cannot complete.

### Minimum Completion Bound

When several positions remain, the smallest possible continuation can be calculated.

If:

`current sum + smallest possible completion > maximum sum`

the branch can be rejected immediately.

These rules reduce unnecessary recursion without changing the result set.

## Duplicate Handling

Duplicate values require careful treatment.

The Python and JavaScript fixed-size examples use distinct candidate values for deterministic combination generation.

The general rule for duplicate-containing input is:

`sort → skip equal values at the same recursion depth`

Skipping duplicates only at the same depth preserves valid repeated values across different depths while preventing equivalent combinations from being emitted multiple times.

Combination sum implementations also deduplicate their candidate sets before searching.

## Complexity

| Operation | Worst-case behavior |
|---|---|
| Choose/not choose | `O(2^n)` generated subsets |
| Fixed-size combinations | `O(C(n,k))` result generation |
| Combination sum | Exponential in the worst case |
| Constraint search | Exponential worst case, reduced by pruning |
| Sorting candidates | `O(n log n)` |
| Hash-based search cache | Average `O(1)` lookup |

Space consumption includes the recursion stack and current path. Storing all generated combinations adds output-dependent memory.

For large search spaces, lazy generation or streaming is preferable when callers do not require all results simultaneously.

## Edge Cases

The implementations explicitly address:

- empty input
- zero-size combinations
- target zero
- negative target
- negative combination size
- target smaller than every candidate
- combination size larger than the candidate set
- duplicate candidates
- invalid zero or negative candidate values
- minimum greater than maximum
- impossible constraints
- repeated target searches
- failed evaluation states
- integer overflow checks in the C++ implementation

A target of zero has a valid empty combination when the search semantics permit it.

## Security and Reliability

Combination search can create exponential workloads. Unrestricted input sizes can therefore become a resource-exhaustion risk.

Production systems should enforce:

- maximum candidate count
- maximum target value
- maximum recursion depth where applicable
- maximum number of returned combinations
- request timeouts
- cancellation support for long-running searches
- bounded caches
- structured logging
- validation before search execution

The JavaScript event-driven implementation provides a foundation for asynchronous service integration, but asynchronous scheduling alone does not make exponential computation inexpensive.

Database constraints are used for rules that should remain true even when data is inserted outside application code.

## Relationship Between the Five Implementations

The implementations share the same mathematical concepts but are intentionally not mechanical translations.

| Language | Primary engineering perspective |
|---|---|
| Python | Algorithmic exploration and executable validation |
| JavaScript | Generator-based and event-driven processing |
| C++17 | High-control search and governance engine |
| Java 17 | Enterprise domain model and policy services |
| PostgreSQL | Relational constraints, recursive SQL, and workflow reporting |

The same concepts therefore appear at different system boundaries:

`Python`
`  ↓`
`algorithm and validation`

`JavaScript`
`  ↓`
`incremental/event-driven processing`

`C++17`
`  ↓`
`search and policy evaluation`

`Java 17`
`  ↓`
`domain services and explicit state`

`PostgreSQL`
`  ↓`
`persistent constraints and relational evaluation`

## Practical Design Decisions

The source files deliberately favor positive integer candidates because they make target pruning mathematically sound and easy to reason about.

Sorting is performed before target-oriented search so that exceeding a remaining target or maximum bound can terminate the current loop.

Path mutation is followed immediately by restoration. This avoids allocating a new list at every recursion level while preserving the correctness of sibling branches.

Validation occurs before recursive processing. Invalid input should fail at the boundary rather than produce misleading partial results.

Policy evaluation is separated from combination generation in the C++ and Java implementations. A generated candidate solution is data; whether it is acceptable is a separate business rule.

The PostgreSQL schema follows the same separation by storing problems, candidates, generated results, members, and evaluation runs as distinct relational concepts.
