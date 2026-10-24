# Subsequences: Generation, Sum Analysis, and Counting

## Purpose

A subsequence is obtained by selecting zero or more elements from a sequence without changing their original relative order. Selected elements do not need to be adjacent.

For the sequence `[1, 2, 3]`, examples include `[]`, `[1]`, `[2, 3]`, and `[1, 2, 3]`. The sequence `[3, 1]` is not a subsequence because it reverses the original order.

The implementations cover four related operations:

- Generate every subsequence using include/exclude decisions.
- Determine whether a subsequence has a specified sum.
- Count subsequences with a specified sum.
- Count subsequences that satisfy a condition on their elements.

The examples also connect sequence analysis to a repository-change scenario, where a proposed change set is evaluated alongside separate review and automated-check conditions.

## Core Concepts

### Subsequences and index-based identity

A sequence of length \(n\) has exactly \(2^n\) index-based subsequences because each position has two choices: include the element or exclude it.

Repeated values remain distinct choices when they originate at different positions. For example, `[0, 0]` has four subsequences:

| Selected positions | Subsequence | Sum |
|---|---|---:|
| None | `[]` | 0 |
| First position | `[0]` | 0 |
| Second position | `[0]` | 0 |
| Both positions | `[0, 0]` | 0 |

Consequently, there are four subsequences with sum zero, not three. Counting distinct value lists and counting index-based subsequences are different problems.

The empty subsequence is valid under the standard definition. Its sum is zero, so an empty input has one subsequence with sum zero and no subsequences with any other sum.

### Include/exclude recursion

At position \(i\), the algorithm makes two decisions:

1. Exclude the current element and continue.
2. Include the current element and continue.

After processing every position, the current selection is a complete subsequence.

The recursion explores a binary decision tree. Every root-to-leaf path represents one selection of input positions.

For `[1, 2]`, the leaves correspond to `[]`, `[2]`, `[1]`, and `[1, 2]`, depending on the order in which branches are visited.

The implementation must restore the working selection after exploring an inclusion branch. Failing to remove the last selected element causes values to leak into sibling branches and produces incorrect results.

## Subsequence Sum

Given an input sequence \(A\) and target \(T\), the existence problem asks whether at least one subsequence satisfies

\[
\sum_{x \in S} x = T
\]

A separate counting problem asks how many index-based subsequences satisfy that equality.

For `[1, 2, 3]` and target `3`, the matching subsequences are `[3]` and `[1, 2]`. Existence is therefore true and the count is two.

### Dynamic programming over reachable sums

The Python, JavaScript, and Java implementations maintain a mapping or set of reachable sums.

Initially, only sum zero is reachable, representing the empty subsequence. For each input value \(x\), every previously reachable sum \(s\) produces a new candidate sum \(s+x\).

For counting, each sum stores the number of ways to reach it. The initial state is:

| Sum | Count |
|---:|---:|
| 0 | 1 |

Each input element contributes both exclusion choices, which preserve the existing counts, and inclusion choices, which add counts to the corresponding new sums.

The implementation copies the previous state before applying inclusion transitions. This prevents a value from being selected multiple times during one iteration.

### Negative values and zero values

The reachable-sum method supports negative, positive, and zero integers. It does not assume that partial sums increase monotonically.

A zero-valued element doubles the number of ways to obtain every existing sum because each previous subsequence has two distinct choices: exclude that zero or include it.

The number of reachable sums can grow substantially with the input values. Dynamic programming is effective when many subsequences share the same sum, but it is not guaranteed to use polynomial time for every integer input.

## Counting Subsequences by an Element Condition

A different problem counts subsequences according to their minimum and maximum values.

For a nonempty subsequence, consider the condition:

`minimum element + maximum element <= limit`

After sorting the input, use two pointers, `left` and `right`.

- If the smallest remaining value plus the largest remaining value is within the limit, every subset of the elements between those positions can be combined with the leftmost value.
- There are \(2^{right-left}\) such choices for the intervening elements.
- Otherwise, the largest remaining value cannot be paired with the current minimum, so move the right pointer left.

This technique counts nonempty subsequences by index without constructing every subsequence. Sorting costs \(O(n\log n)\), and the pointer scan costs \(O(n)\). The powers-of-two table uses \(O(n)\) space.

This optimization applies to the minimum-plus-maximum condition. It is not a general replacement for subsequence generation or arbitrary predicate evaluation.

## Implementation Design

### Python

The Python script uses separate functions for validation, generation, existence testing, counting, and conditional analysis.

- `generate_subsequences` returns a materialized list of lists.
- `iter_subsequences` yields immutable tuples lazily.
- `subsequence_sum` tracks reachable sums.
- `count_subsequences_with_sum` tracks the number of ways to obtain each sum.
- `count_subsequences_matching` evaluates an arbitrary predicate.
- `count_nonempty_subsequences_at_most` applies the sorting and two-pointer optimization.
- `SubsequenceReport` provides an immutable result structure.

`SubsequenceError` distinguishes invalid input from valid calculations. The assertions test empty input, duplicate zero values, negative values, and known target counts.

Materializing all subsequences requires exponential memory. The iterator avoids storing the entire result set, but generating all results still requires exponential time.

### JavaScript

The JavaScript implementation uses a generator to produce subsequences on demand. The generator avoids allocating an array containing every result at once.

`Map` stores the number of ways to obtain each sum, and `Set` stores reachable sums for existence checks. The counting implementation uses `BigInt` so subsequence counts are not restricted to JavaScript's ordinary safe-integer range.

Input values and targets are checked using `Number.isSafeInteger`. The implementation rejects sums outside the safe integer range instead of silently accepting inaccurate numeric results.

`PracticeSession` encapsulates the input and emits an `analysis` event after each calculation. The session exposes a copy of its values and prevents analysis after closure. This separates the calculation from the event consumer, allowing a caller to respond to results without changing the subsequence algorithm.

The program uses Node.js built-in modules only.

### C++17

The C++ implementation generates subsequences using bit masks rather than recursive traversal.

For an input of length \(n\), each mask from zero through \(2^n-1\) specifies which positions are selected. Testing the corresponding bit determines whether an element is included.

The `sumCounts` function uses an ordered map from sums to counts. It checks integer addition and count overflow before storing updated results.

`SubsequenceChangeAnalyzer` provides a small domain-specific service. It evaluates a proposed repository change set against a target-sum condition and separate automated-check and approval flags.

The example deliberately keeps these conditions distinct. A matching subsequence does not itself establish that a pull request has received a valid review or passed its checks.

Bit-mask generation is compact and predictable, but it is suitable only for inputs small enough to enumerate all \(2^n\) possibilities. The implementation rejects lengths that cannot safely be represented by its mask type.

### Java 17

The Java implementation uses recursive generation, immutable records, explicit domain types, and service classes.

`Analysis` holds the target, existence result, count, and total number of subsequences. `SubsequenceService` owns the generation and counting algorithms.

`RepositoryPolicy` represents governance requirements as validated immutable configuration. `PullRequest` captures a change set, target sum, check result, and review state.

`MergeEligibilityService` combines these domain objects. A pull request is rejected when a required check has failed, when a required approval is missing, or when its configured sum condition is not satisfied.

The review-state enumeration distinguishes pending review, approval, requested changes, and dismissal. A real repository system would also track reviewer identity, eligibility, review timestamps, commit versions, discussion resolution, and branch-protection rules.

The Java implementation uses checked arithmetic operations for sum and count updates. Its explicit materialization limit prevents an unexpectedly large recursive output from exhausting available memory.

### PostgreSQL

The SQL script creates the `subsequence_lab` schema and relational tables for exercises, input values, targets, and repository changes.

The `exercise_values` table uses `(exercise_id, position)` as its primary key. This preserves index identity, including repeated values, while enforcing one value per position in each exercise.

The `targets` table stores requested sums separately from input sequences. This allows one exercise to be evaluated against several targets without duplicating its input values.

`generate_subsequences` uses a recursive common table expression to explore include and exclude decisions. The result includes the selected values and their sums.

`count_subsequences_with_sum` uses a JSONB object to maintain counts for reachable sums. Its state begins with one empty subsequence at sum zero. For each input value, the function preserves existing counts and adds inclusion counts to their destination sums.

`target_sum_report` combines exercises and targets into a reporting view. `pull_request_sum_report` aggregates change values and reports whether all associated checks passed, approvals are present, and the pull request remains open.

The repository evaluator combines these workflow indicators with a subsequence-sum condition. It is an educational policy example, not a substitute for the enforcement mechanisms of a real Git hosting platform.

The SQL enumeration functions produce \(2^n\) rows and should be used only for small inputs. Dynamic programming avoids enumerating every selection, but its state can still grow with the number of distinct reachable sums.

## Repository-Change Scenario

The repository examples use change values as a simplified dataset. Each pull request has an ordered list of values, an automated-check state, an approval state, and an open or closed state.

The evaluation separates four questions:

| Concern | Meaning |
|---|---|
| Proposed changes | Which values belong to the change set? |
| Subsequence analysis | Does a selection of those values satisfy the target condition? |
| Review and checks | Have the configured approval and automated-check conditions passed? |
| Merge eligibility | Do all modeled conditions permit the change to proceed? |

A valid subsequence is a mathematical result, not a repository authorization. A real branch-protection policy may require independent reviewers, successful status checks, resolved conversations, restrictions on direct pushes, and other repository-level conditions.

The examples keep the mathematical condition explicit so that it can be replaced with a domain-specific rule without confusing algorithmic correctness with governance enforcement.

## Complexity and Practical Limits

Let \(n\) denote the input length and \(k\) the number of distinct reachable sums.

| Operation | Time complexity | Additional space |
|---|---|---|
| Generate all subsequences | \(O(n2^n)\) | \(O(n2^n)\) when materialized |
| Generate subsequences lazily | \(O(n)\) per output on average, excluding consumer work | \(O(n)\) recursion and selection state |
| Reachable-sum existence | \(O(nk)\) expected with hash-based state | \(O(k)\) |
| Count subsequences by sum | \(O(nk)\) expected with hash-based state | \(O(k)\) |
| Minimum-plus-maximum condition | \(O(n\log n)\) | \(O(n)\) for sorting and powers |

The \(O(nk)\) bounds depend on the number of distinct reachable sums and do not imply polynomial complexity in the bit length of arbitrary integer inputs.

Counting all subsequences also creates a numeric-capacity concern. Counts grow exponentially, so fixed-width integer types can overflow. Python integers and JavaScript `BigInt` support arbitrary-precision counts. The C++ and Java examples use fixed-width counters and report overflow instead of treating wrapped results as valid.

## Validation and Failure Handling

The implementations validate the input before running the algorithms.

- Inputs must contain integers of the supported numeric type.
- Empty sequences retain their mathematically valid empty subsequence.
- Duplicate values preserve distinct index selections.
- Negative values are allowed in sum-based operations.
- Invalid target types are rejected where applicable.
- Fixed-width arithmetic checks prevent silent overflow in implementations that use bounded integers.
- Exponential generation is restricted where materialization would exceed practical limits.

The PostgreSQL schema uses primary keys, foreign keys, uniqueness constraints, and checks to preserve relational integrity. The demonstration data uses conflict-safe inserts so the setup can be rerun without duplicating the same sample rows.

## Running the Implementations

- Python: save the first source file as `subsequences.py` and run it with Python 3.10 or later.
- JavaScript: save the second source file as `subsequences.js` and run it with Node.js 18 or later.
- C++17: save the third source file as `main.cpp`, compile with a C++17-compatible compiler, and run the resulting executable.
- Java 17: save the fourth source file as `Main.java`, compile with Java 17 or later, and run `Main`.
- PostgreSQL: execute the fifth source file in a PostgreSQL 14 or later session with permission to create schemas, tables, views, and functions.

The examples include assertions or runtime checks for empty input, repeated zeros, negative values, and known counts. These tests provide small, deterministic checks of the core subsequence behavior.
