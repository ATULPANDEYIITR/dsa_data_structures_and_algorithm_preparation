# Stack Applications: Parsing, Evaluation, Reversal, and Undo

## Scope

A stack is a last-in, first-out (LIFO) data structure. The most recently pushed element is the first element removed. This ordering is useful when a system must remember nested contexts, defer operations until their operands are available, reverse a sequence, or restore an earlier state.

The implementations examine several distinct applications:

- **Bracket matching** uses nested opening delimiters to validate structural order.
- **Expression conversion and evaluation** use operator stacks, operand stacks, and expression trees to preserve arithmetic precedence and associativity.
- **Undo and redo** retain historical states so users can reverse edits and reapply them.
- **Reversal** uses the LIFO ordering directly to reverse characters or collections.
- **Minimum tracking** augments a normal stack with a second stack to retrieve the current minimum efficiently.

The C++ and Java programs also connect stack-based expression processing and history management to repository governance scenarios. Their merge-policy models illustrate how an expression can be parsed or how a previous document state can be restored without confusing those mechanisms with actual Git hosting behavior.

## Stack mechanics and complexity

A stack normally exposes `push`, `pop`, `peek`, and `isEmpty`. A list-backed implementation provides amortized \(O(1)\) insertion and removal at the end. A linked-list implementation can provide \(O(1)\) insertion and removal at the head, although each node requires additional memory.

| Operation | Typical time | Purpose |
|---|---:|---|
| Push | \(O(1)\) amortized | Save a value or state |
| Pop | \(O(1)\) | Retrieve the newest saved value |
| Peek | \(O(1)\) | Inspect the top without removing it |
| Bracket validation | \(O(n)\) | Validate a sequence of length \(n\) |
| Infix-to-postfix conversion | \(O(n)\) | Convert an expression with \(n\) tokens |
| Postfix evaluation | \(O(n)\) | Evaluate an expression with \(n\) tokens |
| Reversal | \(O(n)\) time and space | Reverse a sequence of \(n\) elements |

Empty-stack behavior must be explicit. Returning an arbitrary value from `pop` can conceal a logic error. The implementations therefore use exceptions or checked conditions when an operation requires a missing element.

## Bracket matching and balanced parentheses

### Why a counter is sometimes insufficient

For parentheses alone, a depth counter is enough. Increment it for each opening parenthesis and decrement it for each closing parenthesis. A negative depth identifies a closing parenthesis that has no corresponding opening parenthesis. A final nonzero depth identifies an unclosed parenthesis.

Matching multiple delimiter types requires a stack. Consider `([)]`. The input contains two opening delimiters and two closing delimiters, but the nesting is invalid. When `)` appears, the most recent unmatched opening delimiter is `[`, not `(`. A counter cannot preserve that information.

The general algorithm pushes each opening delimiter and, for each closing delimiter, compares it with the top opening delimiter. It rejects an unexpected closing delimiter, a mismatched pair, or any opening delimiter left at the end.

### Python implementation

The Python program provides both `balanced_parentheses` and `check_brackets`. The former demonstrates the simpler depth-counter algorithm. The latter retains each opening delimiter and its position, making it possible to report where a mismatch occurred.

A stack entry is a pair containing the opening character and its position. This additional information improves diagnostics without changing the algorithm's \(O(n)\) time complexity.

### JavaScript implementation

The JavaScript implementation uses a `Map` for opening-to-closing relationships and another map for reverse lookup. It returns a structured result with a Boolean status, an error position, and a reason. This format is convenient when bracket validation is part of a configuration editor or an interactive form.

JavaScript strings use UTF-16 internally. `reverseStringByCodePoint` converts the string with `Array.from` before reversing it, avoiding the common mistake of splitting many non-BMP characters into separate surrogate code units. This does not preserve every user-perceived grapheme cluster, such as a character assembled from multiple combining code points.

## Infix, postfix, and prefix expressions

Arithmetic expressions have more structure than a left-to-right sequence of operators. In `2 + 3 * 4`, multiplication must happen before addition. Parentheses can override normal precedence, and exponentiation is commonly right-associative.

The three representations differ in operator placement:

| Representation | Example | Main characteristic |
|---|---|---|
| Infix | `2 + 3 * 4` | Operators appear between operands |
| Postfix | `2 3 4 * +` | Operators follow their operands |
| Prefix | `+ 2 * 3 4` | Operators precede their operands |

Postfix evaluation does not need precedence rules during evaluation because the expression order already encodes them.

### Shunting-yard conversion

The Python and JavaScript implementations use the shunting-yard method to convert infix input to postfix output. Operands go directly to the output. Operators are held on a stack until the precedence and associativity rules determine when they should be emitted. Parentheses temporarily limit operator removal.

For a left-associative operator, an operator of equal precedence is emitted before the new operator. For a right-associative operator such as exponentiation, an operator of equal precedence stays on the stack. This distinction ensures that `2^3^2` is interpreted as `2^(3^2)` rather than `(2^3)^2`.

Unary signs require special handling. A minus sign in `-2` is not a binary subtraction operator. The implementations represent unary operators as `u-` and `u+`. With the precedence policy used here, `-2^2` becomes `2 2 ^ u-`, corresponding to `-(2^2)`. The chosen convention should be documented because arithmetic parsers do not all assign unary operators identical precedence.

### Postfix evaluation

Evaluation uses a separate stack of numeric operands. A number is pushed when encountered. A unary operator consumes one operand. A binary operator consumes two operands, with the right operand popped first and the left operand popped second. The computed result is pushed back.

For `8 2 /`, the stack supplies `2` as the right operand and `8` as the left operand, producing `4`. Reversing these operands would produce an incorrect result for subtraction and division.

The Python evaluator supports named variables, allowing expressions such as `2*x + 1` to be evaluated with an explicit variable mapping. The JavaScript evaluator uses own-property checks to prevent inherited object properties from being treated as supplied variables.

Neither evaluator executes arbitrary source code. A tokenizer, an operator allowlist, and explicit evaluation functions define the supported expression language. This is safer and easier to audit than evaluating an expression using a general-purpose execution mechanism.

### Validation and numerical limitations

A valid expression must not leave extra operands on the evaluation stack. Binary operators require two operands, and unary operators require one. The parsers reject adjacent operands, unmatched parentheses, misplaced operators, unknown characters, and incomplete expressions.

Division by zero is rejected explicitly. The implementations also limit expression length and exponent size to reduce resource-exhaustion risks. Floating-point arithmetic remains subject to rounding, and very large intermediate values may exceed the numeric representation. Production systems may need bounded integer arithmetic, decimal arithmetic, stricter exponent limits, or explicit policies for overflow and non-finite results.

### Prefix conversion

The Python implementation converts postfix tokens into an expression tree, then traverses the tree in preorder to produce prefix notation. Each operator becomes an internal node and each operand becomes a leaf.

An expression tree makes operator relationships explicit. It is useful when a system needs to inspect or transform an expression rather than merely evaluate it. The tree-based approach also avoids relying on simple token reversal, which can mishandle unary operators and associativity if applied without a complete grammar.

## Undo and redo as state history

Undo and redo are not expression-evaluation operations. They use the same LIFO structure to preserve a sequence of document states.

A simple editor saves its current state before a mutation. Undo moves the current state to the redo stack and restores the most recent saved state. Redo performs the reverse transfer.

When a new edit occurs after an undo, the redo stack must be cleared. Otherwise, the editor could reapply an action that belongs to a history branch that the user has abandoned.

### Python snapshot editor

The Python `TextEditor` keeps complete string snapshots in `_undo_stack` and `_redo_stack`. It supports insertion, deletion, replacement, undo, and redo. Its implementation emphasizes correctness and clear state transitions.

Snapshot history is simple to reason about, but copying a large document for every edit can require substantial time and memory. A deletion of an empty range is treated as a no-op so that an operation with no effect does not create an unnecessary history entry.

### JavaScript editor and calculation history

The JavaScript `TransactionalEditor` demonstrates bounded snapshot history. Its history limit prevents unbounded retention of document copies. When the limit is reached, the oldest snapshots are discarded.

The separate `ExpressionHistory` class records immutable calculation entries containing the expression, result, and timestamp. Its cursor allows users to navigate backward and forward through prior calculations. Recording a new calculation after moving backward discards the obsolete forward history.

These classes illustrate two distinct requirements: restoring editable document state and navigating immutable calculation records. They share stack-like behavior but need different stored data and public operations.

### Memory and correctness trade-offs

Full snapshots simplify undo because each entry contains a complete prior state. They can be inefficient for large documents. Alternative approaches include inverse operations, command objects, edit deltas, and persistent data structures.

An inverse-operation history records what must be done to reverse a mutation. For example, deleting a range can store the deleted text and its original position. This can save memory for small changes, but inverse operations require careful handling of offsets and dependencies between edits.

A production editor should also define whether cursor position, selection, formatting, and other metadata belong to the undoable state. If an operation affects several related structures, restoring only the text may produce an inconsistent result.

## Reversal and minimum tracking

### Reversal

Reversal is a direct consequence of LIFO ordering. Push every element from the input sequence, then repeatedly pop elements into the output. The newest input element becomes the first output element.

The Python implementation supports arbitrary iterables by first materializing their elements into a stack. The JavaScript implementation demonstrates both collection reversal and string reversal.

Reversal through a stack uses \(O(n)\) additional memory. An in-place array reversal can use \(O(1)\) auxiliary memory, so the stack version is most valuable when learning LIFO behavior or when elements must be temporarily stored for another stack-based operation.

### Minimum stack

The Python `MinStack` keeps the values in one stack and the historical minima in another. A value is pushed onto the minimum stack whenever it is less than or equal to the current minimum.

The equality condition matters. If two identical minimum values are pushed, removing one must not remove the minimum while the other remains in the main stack. When a popped value equals the minimum at the top of the auxiliary stack, the corresponding minimum entry is removed.

This design supports minimum lookup in \(O(1)\) time, with \(O(n)\) worst-case auxiliary space. It is useful when a system repeatedly needs the current minimum but should not scan the entire collection after each mutation.

## C++ case study: repository policy expression evaluation

The C++ program uses a repository-governance scenario to show how delimiter validation and stack-driven expression parsing can support a policy evaluator.

The lexer converts the input into typed tokens. A recursive-descent parser then uses the grammar's call stack to construct a syntax tree for logical operators, comparisons, variables, and numeric values. Although this parser does not use an explicit operator stack for expression conversion, it remains a stack-based parsing implementation and demonstrates a different expression-processing strategy.

The evaluator looks up policy variables in a context object and computes logical results. Boolean operators short-circuit: a false left operand makes the right operand of `&&` unnecessary, and a true left operand makes the right operand of `||` unnecessary.

The policy context models approval count, successful checks, and conflicts. A separate merge-eligibility engine checks request state, source and target branches, synchronization, conflicts, approvals, status checks, discussion resolution, linear-history requirements, and target protection.

These are separate responsibilities. The expression parser evaluates a supplied policy expression; the eligibility engine evaluates explicit merge conditions. Neither is an implementation of a hosting provider's actual branch-protection API.

The case study also illustrates safe handling of user-supplied policy expressions. The lexer accepts a restricted character set, the parser recognizes an explicit grammar, and evaluation supports only declared operators and variables. Unsupported input raises an exception rather than being executed as a general-purpose program.

## Java case study: enterprise governance and editing

The Java program uses records for immutable values such as `Reviewer`, `Review`, `StatusCheck`, and `BranchProtection`. Enums constrain review states, Pull Request states, check outcomes, and merge strategies to defined alternatives.

The `PullRequest` class owns mutable workflow state. It validates branch names, records commits, accepts reviews, stores checks, and controls state transitions. A new commit invalidates stored status checks because those checks may describe a previous head revision.

The `GovernanceService` evaluates merge eligibility using a separate branch-protection policy. It counts distinct eligible reviewers, excludes inactive or unauthorized reviewers, considers stale approvals, checks the current head associated with status results, and enforces discussion and history policies.

An approval is not equivalent to merge eligibility. Approval is one input into the policy decision. The request may still be blocked by a failed check, a conflict, an unresolved discussion, a draft state, or an incompatible merge strategy.

The `SnapshotEditor` provides a separate example of stack-based state restoration. Its bounded `ArrayDeque` history illustrates the trade-off between simple snapshot semantics and memory use. The example deliberately keeps document editing independent from repository governance.

## SQL model: relational state and derived eligibility

The PostgreSQL script models repository governance as related entities rather than as one large record.

- `repositories`, `users`, and `repository_members` define repository ownership and review permissions.
- `branches` records the current head commit and deletion state for each branch.
- `branch_protection` stores the rules applied to a protected target branch.
- `pull_requests` records source and target branches, request state, the observed source and base revisions, conflict status, discussion resolution, and proposed history behavior.
- `pull_request_commits` preserves commit membership and basic commit metadata.
- `reviews` stores review decisions and the revision associated with each decision.
- `review_comments` stores inline comments, optional replies, and resolution state.
- `status_checks` records check outcomes for particular commits.
- `merge_events` records merge actors, strategies, resulting commits, and timestamps.

Primary keys identify records. Foreign keys enforce relationships, while check constraints restrict states, require nonnegative approval counts, and validate merge-state combinations. Indexes support target-branch workflow queries, latest-review retrieval, status-check lookup, and unresolved-comment inspection.

### Review authorization

The `validate_review_submission` trigger rejects reviews from Pull Request authors and prevents inactive or unauthorized users from submitting reviews. This is database-level enforcement rather than a convention left entirely to application code.

The trigger does not make every policy decision. Eligibility still depends on the branch protection rules, review history, and current commit state.

### Merge-eligibility view

The `merge_eligibility` view derives the latest review state per reviewer, counts eligible approvals, checks required status results, and combines the results with request and branch state.

Stale approvals are excluded when the protection policy requires dismissal after the source revision changes. A check must belong to the current source head and have a successful result. The view also compares the Pull Request's observed source and base revisions with the current branch heads.

This design avoids maintaining a separate mergeable Boolean that can become outdated after a commit, review, or check changes. The view calculates eligibility from the current relational state each time it is queried.

The demonstration transaction advances the feature branch to a new commit and updates the Pull Request's observed source revision. Existing checks and approvals remain attached to the previous commit, so the policy can identify the request as ineligible. A rollback restores the original demonstration state.

### Database limitations

The schema is an educational governance model rather than a complete hosting platform. It does not implement distributed merge conflict detection, cryptographic commit verification, webhook delivery, or all provider-specific permission rules.

Some invariants span multiple tables and concurrent transactions. A production implementation should use appropriate transaction isolation, locking, or serialized merge operations to prevent concurrent state changes from invalidating an eligibility decision between evaluation and merge. The final merge operation must revalidate the conditions it relies on.

## Common implementation failures

- **Popping operands in the wrong order:** postfix subtraction and division require the second popped operand to be the left operand.
- **Ignoring associativity:** treating every operator as left-associative changes the meaning of exponentiation chains.
- **Confusing unary and binary signs:** `-x` consumes one operand, while `x-y` consumes two.
- **Checking only delimiter counts:** matching counts do not guarantee correct nesting.
- **Retaining obsolete redo history:** a new edit after undo creates a different history path.
- **Using stale approvals or checks:** review decisions and check results are tied to particular source revisions.
- **Treating approval as permission to merge:** merge eligibility depends on the complete applicable policy.
- **Trusting a previously computed eligibility flag:** repository state may change before the merge is performed.

## Production considerations

Stack-based algorithms are predictable, but the data placed on a stack determines the system's operational behavior. A stack of characters is small and straightforward. A stack of full document snapshots can consume significant memory. A parser's stack or recursion depth can be exhausted by adversarially nested input.

Input length, nesting depth, numeric ranges, history retention, and exception handling should be explicit policy decisions. Diagnostics should identify invalid input without exposing sensitive configuration values.

For collaborative editors, a single-user snapshot stack is insufficient to model concurrent edits. Collaborative editing requires a defined conflict-resolution strategy and a representation of changes that can be reconciled across users.

For repository governance, merge eligibility is time-sensitive. The target branch, source head, approvals, checks, and discussion state must be revalidated at the point where the merge is committed. The database and service examples illustrate why historical review decisions, current revision identity, and protected-branch rules must remain distinct parts of the workflow.
