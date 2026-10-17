# Maps and Sets: Frequency Analysis, Membership, and Set Algebra

## Technical scope

Maps and sets provide complementary representations for problems involving collections of values.

A **map** associates a key with a value. It is appropriate for counting occurrences, indexing records, maintaining per-entity statistics, and associating identifiers with their latest states.

A **set** represents distinct elements. It is appropriate for duplicate detection, membership checks, removing repeated values, and determining the overlap or difference between groups.

The implementations use repository engineering as a practical context. Changed-file frequencies, reviewer participation, review decisions, status-check results, and branch governance illustrate how these data structures support different operations without conflating their purposes.

## Map operations and frequency counting

Given a sequence of changed file paths, a frequency map associates each path with its occurrence count.

For a sequence such as:

`["src/auth.js", "src/router.js", "src/auth.js"]`

the resulting map contains the entries `src/auth.js → 2` and `src/router.js → 1`.

Frequency counting is useful when a collection contains repeated observations. It distinguishes a value's presence from the number of times it appears.

- Python's `Counter` provides a specialized frequency-counting structure, while an ordinary dictionary demonstrates explicit initialization and increment operations.
- JavaScript's `Map` associates arbitrary keys with values and exposes explicit `get` and `set` operations. The implementation uses a default count of zero before incrementing.
- Java's `HashMap.merge` combines lookup and update into one operation. The generic `FrequencyIndex` also derives the set of duplicated values from the resulting counts.
- PostgreSQL uses `GROUP BY` and `COUNT(*)` to aggregate stored rows without requiring application code to maintain an in-memory counter.

For \(n\) observations and \(k\) distinct keys, hash-based frequency counting typically takes expected \(O(n)\) time and \(O(k)\) additional space. Hash collisions and implementation details can affect individual operations.

A frequency map is not equivalent to a set. A set can answer whether a value is present, but it does not retain the number of occurrences.

## Duplicate detection and unique elements

Duplicate detection identifies values occurring more than once. A standard single-pass algorithm maintains two sets:

- `seen` contains values encountered previously.
- `duplicates` contains values encountered at least twice.

For each incoming value, membership in `seen` determines whether it has appeared before. The algorithm adds a value to `duplicates` when a repeat is found.

The algorithm requires expected \(O(n)\) time and \(O(k)\) space, where \(k\) is the number of distinct values.

Three related results must be distinguished:

| Operation | Meaning |
|---|---|
| Duplicate values | Each repeated value appears once in the result. |
| Repeated occurrences | Every occurrence after the first is retained. |
| Unique sequence | Each value appears once, in first-occurrence order. |
| Values appearing once | Only values whose total frequency equals one are returned. |

These results answer different questions. For example, an audit system may need the identities of repeated failed requests, while a data-cleaning pipeline may need the original records that occurred exactly once.

Python's dictionary preserves insertion order, allowing `dict.fromkeys` to remove repeated values while retaining first-occurrence order. JavaScript's `Set` also preserves insertion order. Java can use `LinkedHashSet` when deterministic encounter order matters.

PostgreSQL can identify duplicated values with `GROUP BY ... HAVING COUNT(*) > 1`. A unique database constraint serves a different purpose: it prevents duplicate values in a specified column or column combination rather than merely reporting them.

## Membership testing

Membership testing asks whether a candidate belongs to a collection.

Suppose a deployment request requires the `security-scan` check. A membership test determines whether that check is present in the required-check set.

A list scan takes \(O(n)\) time in the worst case for a collection of \(n\) elements. A hash set generally provides expected \(O(1)\) membership testing after construction, at the cost of additional memory.

When the same collection is queried repeatedly, building a set once can reduce total work substantially. For a single lookup against a small collection, converting the collection to a set may cost more than a direct scan.

Membership alone does not prove authorization. A repository system must also establish that the reviewer is active, eligible under the applicable policy, and permitted to perform the requested operation.

The Python access audit uses maps to count outcomes per employee and sets to maintain distinct users of each resource. The JavaScript event processor uses a set to maintain the current collection of pull requests with failing checks.

## Set algebra

Set operations compare distinct memberships rather than occurrence counts.

Let \(A\) represent the reviewers eligible for a security review and \(B\) represent reviewers assigned to a platform review.

| Operation | Mathematical meaning | Repository application |
|---|---|---|
| Union | \(A \cup B\) | All reviewers belonging to either team. |
| Intersection | \(A \cap B\) | Reviewers shared by both teams. |
| Difference | \(A - B\) | Security reviewers not in the platform group. |
| Symmetric difference | \((A-B) \cup (B-A)\) | Reviewers belonging to exactly one group. |

Hash-based implementations typically process these operations in expected linear time in the sizes of the input sets. The exact cost depends on which set is traversed, how membership is implemented, and whether the output must be ordered.

Intersection across multiple groups requires careful empty-input semantics. The Python implementation returns an empty set when no groups are supplied. For a nonempty sequence of groups, it begins with the first group and intersects subsequent groups. If any group is empty, the final intersection is empty.

Set algebra is useful for comparing reviewer pools, finding shared resource users, checking required permissions, and identifying differences between repository configurations. It should not be used where repeated occurrences or sequence order are meaningful.

## Hashability, equality, and identity

Hash-based maps and sets depend on stable hashing and equality behavior.

### Python

Dictionary keys and set elements must be hashable. Strings, integers, and tuples containing hashable values are suitable examples. Mutable lists cannot be stored directly as set elements.

The Python implementation converts structured list records into tuples before inserting them into a set. Such normalization is appropriate only when the chosen representation preserves the intended equality semantics.

Python also treats `True`, `1`, and `1.0` as equal dictionary keys and set elements because they compare equal and have compatible hashes. Applications must account for such equivalence when mixing numeric and Boolean values.

### JavaScript

JavaScript `Map` and `Set` distinguish object references by identity. Two separate objects containing the same properties are different keys unless they are the same object reference.

This differs from the usual expectation that two records with matching fields should represent the same logical entity. When logical equality is required, applications can normalize records to stable identifiers such as pull request IDs or reviewer usernames.

### Java and C++

Java collections depend on appropriate `equals` and `hashCode` implementations for logical key equality. Keys should not change in ways that invalidate their hash-based lookup behavior.

C++ unordered containers use hash and equality functions. Ordered containers such as `std::set` instead use ordering to determine uniqueness. A custom type must define consistent comparison or hashing semantics for the selected container.

### SQL

Relational uniqueness is defined by database constraints and the equality behavior of the relevant column types and collations. It is not identical to object identity in JavaScript or arbitrary object equality in Python.

## Pull Requests and repository governance

The C++ and Java programs apply maps and sets to a repository-governance problem. Their data structures help evaluate merge eligibility, but each repository rule retains a distinct meaning.

### Pull Requests

A Pull Request proposes changes from a source branch into a target branch. Its lifecycle includes opening, updating the proposed commits, review, status-check execution, conflict resolution, closing, reopening where supported, and merging.

The target branch determines which protection policy is relevant. A draft Pull Request is not ready to merge. A change to the proposed commit may invalidate earlier review decisions or status-check results, depending on repository policy.

Merge strategies such as merge commits, squash merges, and rebasing produce different history structures. A linear-history requirement can restrict which strategies are permitted.

### Code Review

Code Review evaluates the technical quality and correctness of a proposed changeset. Reviewers may inspect implementation logic, security boundaries, tests, compatibility, maintainability, and unintended behavior.

Inline comments identify specific locations in changed files. Review discussions provide context for requested modifications. Resolving a discussion records that the conversation has been addressed; it does not necessarily prove that the implementation is correct.

The programs represent review states explicitly. A comment-only review is not an approval, and a dismissed approval is not an effective approval.

### Approvals

An approval is a recorded review decision that may satisfy a repository policy. Its effect depends on reviewer eligibility, the current review state, the commit that was reviewed, and the policy's requirements.

The C++ engine considers the latest decision for each reviewer and counts only eligible reviewers whose latest state is approved. The Java implementation also requires an approval to reference the current Pull Request head commit.

An approval on an older commit may be stale after new changes are pushed. Review dismissal, changes-requested decisions, and policy changes can also change merge eligibility.

Approval counts alone do not establish that a Pull Request can be merged.

### Branch Protection

Branch Protection defines repository-level restrictions on changes to a target branch. Policies can require approvals and successful checks, prohibit direct pushes, disallow force pushes, prevent branch deletion, require resolved discussions, or enforce linear history.

The C++ and Java models separate branch policy from individual Pull Request state. The SQL schema stores policy requirements and eligible reviewers separately from reviews and check runs.

Administrator bypass is a separate governance capability. Recording a bypass setting does not itself implement secure bypass authorization or audit logging. A production system must identify authorized bypass actors, record each bypass, and define the rules governing its use.

## Python implementation

The Python script contains reusable functions for counting, duplicate detection, ordered deduplication, membership reporting, set operations, intersection across groups, and frequency distribution.

Its `AccessAudit` class models repository-resource access events. A dictionary of counters aggregates outcomes by employee, a set tracks resources associated with denied requests, and a map of resource names to employee sets supports distinct-user analysis.

Input validation rejects empty identities, empty resource names, and unknown outcomes. The benchmark compares list membership with set membership and verifies that both produce identical results before reporting elapsed times.

The benchmark is illustrative rather than a universal performance measurement. Runtime conditions, input size, and data distribution affect the results.

## JavaScript implementation

The JavaScript implementation emphasizes event-driven processing. `RepositoryEventProcessor` stores validated events and maintains projections using maps and sets.

A map counts events by Pull Request and event type. Another map associates each Pull Request ID with a set of distinct reviewers. A set tracks Pull Requests whose latest processed check event indicates failure.

The event processor exposes copies of reviewer and failure sets so callers cannot directly mutate those internal collections. Events are frozen after validation to prevent accidental mutation of stored event objects.

The asynchronous stream consumer accepts an iterable through `for await...of`. This provides a compatible processing pattern for asynchronous iterables, but the demonstration uses in-memory data rather than a durable event broker.

The failure projection also illustrates an important limitation: a simple event-driven set is reliable only when event ordering and event meaning are well defined. A passing check should clear a failure only when it refers to the appropriate check and commit. Production processing requires event identity, persistence, idempotency, and out-of-order event handling.

## C++ governance engine

The C++ case study evaluates three Pull Requests against a protection policy for `main`.

`BranchProtection` stores required checks and eligible reviewers in sets. `PullRequest` holds review and check records in vectors. The evaluation engine uses unordered maps to determine the latest review state for each reviewer and the latest result for each named check.

The effective approval count includes only reviewers who are eligible under the policy and whose latest decision is approved. The engine separately evaluates Pull Request state, branch targeting, merge conflicts, discussion resolution, linear history, and check outcomes.

The example demonstrates both an eligible change and blocked changes. It also rejects an impossible policy configuration in which the required number of approvals exceeds the number of eligible reviewers.

The use of `std::set` makes diagnostic output deterministic. `std::unordered_map` provides expected constant-time lookup for aggregation. These structures have different trade-offs: ordered containers maintain ordering, while unordered containers generally prioritize lookup efficiency.

The engine is a local policy model, not an implementation of a hosting provider's complete merge API. It does not execute merges, synchronize branches, perform authorization against a live identity provider, or guarantee that policy state remains unchanged between evaluation and merge.

## Java enterprise model

The Java implementation uses records for immutable domain data, enums for finite states, and explicit service classes for aggregation and merge eligibility.

`PullRequest` validates branch identities and stores immutable copies of its review and check lists. `BranchPolicy` represents governance requirements and prevents configurations that require more approvals than the eligible reviewer pool can supply.

`FrequencyIndex` uses `HashMap.merge` for aggregation and exposes duplicated keys separately from occurrence counts.

`MergeEligibilityService` evaluates the target branch, Pull Request state, conflict status, discussion resolution, merge strategy, effective approvals, and current-commit check results. `LinkedHashMap` ensures that a reviewer's latest decision replaces earlier decisions for that reviewer.

The implementation distinguishes three cases that are often incorrectly combined: an approval from an ineligible reviewer, an approval on a stale commit, and an approval superseded by a later review decision.

The model reports direct-push restrictions, force-push restrictions, branch-deletion restrictions, and administrator bypass settings independently of the merge decision. This reflects the distinction between evaluating a proposed merge and governing all operations that can alter a protected branch.

## PostgreSQL relational model

The SQL script defines a schema containing repositories, branches, Pull Requests, commits, reviewers, protection policies, eligible reviewers, required status checks, reviews, inline comments, status-check runs, and Pull Request events.

Primary keys identify individual records. Foreign keys preserve relationships between repositories, branches, reviews, comments, and check runs. Unique constraints prevent duplicate repository names within an owner and duplicate branch names within a repository.

Check constraints enforce valid state values, nonnegative approval requirements, valid discussion line numbers, and consistent merged-state timestamps. Partial and composite indexes support queries involving unresolved discussions, review history, check runs, Pull Request states, and event chronology.

The script uses several SQL mechanisms to express collection operations:

- `GROUP BY` and `COUNT(*)` calculate frequencies from persisted rows.
- `SELECT DISTINCT` returns unique reviewer identities.
- `UNION` combines distinct reviewer populations.
- `HAVING COUNT(DISTINCT ...)` identifies reviewers who participated in multiple Pull Requests.
- `DISTINCT ON`, a PostgreSQL-specific feature, selects the latest review decision and latest status-check result for each relevant key.
- Common table expressions organize the intermediate results used to evaluate merge eligibility.

The `pull_request_merge_eligibility` view combines effective approvals with required check results and branch policy. A required check is considered unsuccessful for eligibility purposes if its latest result is missing, failed, pending, cancelled, or associated with a stale commit.

The view evaluates whether the modeled Pull Request satisfies the stored conditions. It does not lock the repository, reserve a merge, or prevent concurrent changes between evaluation and execution.

The schema records direct-push, force-push, deletion, and administrator-bypass settings, but these flags alone cannot enforce every operation against an external hosting service. Such enforcement belongs to the repository platform or to a service that authoritatively mediates those operations.

## Correctness and operational limitations

Map and set algorithms are concise because they rely on efficient lookup. Their correctness still depends on well-defined equality, stable keys, and accurate input state.

- Repeated review events should not automatically count as multiple independent approvals. Effective approvals must be counted by reviewer identity after determining each reviewer's current decision.
- A successful check on an older commit must not be accepted when policy requires a successful result for the current commit.
- A reviewer who appears in a team set is not necessarily authorized to approve a particular repository. Eligibility and current authorization must be checked separately.
- Removing duplicates can discard meaningful sequence information. Use frequency maps or retain the original event sequence when multiplicity matters.
- Empty input collections require deliberate handling. The intersection of no supplied groups and the intersection of one or more groups containing an empty set are different programming cases.
- In-memory maps and sets do not provide durable storage, transaction isolation, or protection against concurrent updates.
- Hash-based operations have expected rather than unconditional constant-time performance. Hash collisions, resizing, memory pressure, and adversarial input can affect behavior.

For production governance, merge eligibility should be evaluated against authoritative repository state and revalidated at the point of merge. Review decisions, policy versions, status-check results, and bypass actions should be auditable. Database constraints can protect relational consistency, but they do not replace authorization checks or repository-platform enforcement.
