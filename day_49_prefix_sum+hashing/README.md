# Prefix Sum + Hashing

## Topic Scope

Prefix sums and hashing provide a general method for recognizing subarray properties without examining every possible pair of endpoints.

The central idea is to represent the portion of a sequence before the current position as a **prefix state**. When the current state and an earlier state have a required relationship, the interval between those two positions satisfies the desired condition.

This repository treats four closely related problems as distinct applications:

| Area | Prefix state | Matching rule |
|---|---|---|
| Subarray sum | Numeric cumulative sum | `current - previous = target` |
| Zero-sum subarray | Numeric cumulative sum | `current = previous` |
| Equal-frequency conditions | Relative frequency vector | `current state = previous state` |
| Prefix-state tracking | General accumulated state | Equal or transformed states identify valid intervals |

Hashing supplies the fast lookup mechanism. The prefix representation supplies the mathematical meaning of the lookup key.

## Core Prefix-Sum Mechanism

For a sequence

`a[0], a[1], ..., a[n-1]`

define

`P[j] = a[0] + a[1] + ... + a[j]`.

Using a conceptual prefix before the first element with value zero, the sum of the interval from `i` through `j` is:

`P[j] - P[i-1]`.

Therefore, when the required subarray sum is `K`, the current prefix `P[j]` needs an earlier prefix equal to:

`P[j] - K`.

A hash table can store the frequency of previously observed prefix sums. Each lookup therefore replaces a potentially linear search through earlier positions.

The implementations use this relationship directly rather than enumerating all subarrays.

## Subarray Sum

The Python implementation stores a frequency table of prefix sums. If the current prefix is `P`, every occurrence of `P - K` represents one subarray ending at the current position whose sum is `K`.

This is important when prefix sums repeat. A frequency table counts every valid starting position instead of retaining only one occurrence.

For example, repeated prefix states can represent several different valid intervals ending at the same element. The Python `subarray_sum_equals_k` function preserves the positions as well when the actual ranges are required.

The JavaScript implementation separates counting from interval discovery. `countSubarraysWithSum` uses a `Map` containing frequencies, while `findSubarraysWithSum` stores the positions associated with each prefix value.

The C++ implementation uses `std::unordered_map<long long, long long>` so that the prefix sum and the number of matching prefixes can exceed the range of a small integer counter independently.

The SQL implementation approaches the problem differently. It models the repository-governance domain rather than trying to reproduce the array algorithm relationally. This keeps the database artifact focused on integrity and state enforcement instead of turning SQL into a translation of an array algorithm.

## Zero-Sum Subarrays

Zero-sum detection is the special case where the target is zero.

The condition becomes:

`P[j] - P[i-1] = 0`

which is equivalent to:

`P[j] = P[i-1]`.

Thus, every repeated prefix sum identifies a zero-sum interval.

There are two useful implementations in the Python file.

`has_zero_sum_subarray` stores only whether a prefix state has appeared. It is sufficient when the question is existence.

`count_zero_sum_subarrays` stores frequencies. If a prefix state has already occurred `f` times, the new occurrence creates `f` additional zero-sum intervals.

This distinction matters because existence, counting, and interval reconstruction require different amounts of state.

The JavaScript and C++ versions apply the same mathematical relationship through `Map` and `unordered_map`, respectively, while their surrounding implementations use language-specific structures rather than mechanically translating the Python source.

## Equal-Frequency Conditions

Equal-frequency problems can often be converted into zero-sum prefix-state problems.

For binary data containing zeros and ones, map:

`0 -> -1`

and

`1 -> +1`.

An interval containing the same number of zeros and ones then has transformed sum zero.

The binary problem therefore becomes a repeated-prefix-state problem.

For multiple symbols, a single numeric balance is insufficient. Suppose the symbols are `A`, `B`, and `C`. Select `C` as the reference symbol and track:

`count(A) - count(C)`

and

`count(B) - count(C)`.

The prefix state is therefore a vector:

`(A-C, B-C)`.

If two prefix positions have the same vector, the interval between them has equal numbers of `A`, `B`, and `C`.

The Python implementation represents this state as a tuple. The JavaScript implementation serializes the relative counts into a `Map` key. The C++ implementation introduces `FrequencyState` and a custom hash function for vector states. The Java implementation uses a record containing immutable frequency differences.

The dimensionality increases with the number of tracked symbols, so the state is no longer a single integer. The same equality principle remains valid.

## Prefix-State Tracking

Prefix-state tracking is broader than numeric prefix sums.

A state can represent:

- a cumulative numeric value;
- a zero/one balance;
- several relative character frequencies;
- another finite-dimensional accumulated property whose equality has a useful interval interpretation.

The critical design question is not merely "what should be accumulated?" It is:

> What state equality or state difference proves that an interval satisfies the desired property?

Once that state has been defined, hashing can index previously observed states.

For longest-interval problems, the earliest occurrence of each state is usually retained. If the same state occurs later, the earliest occurrence creates the longest possible interval ending at the current position.

For counting problems, all previous occurrences contribute, so frequencies are retained.

This gives two important storage patterns:

| Requirement | Stored information |
|---|---|
| Existence | Set of states |
| Count | Frequency of each state |
| Longest interval | Earliest position of each state |
| All intervals | Every position associated with each state |

## Python Implementation

The Python script progresses from direct subarray-sum queries to more general state representations.

`subarray_sum_equals_k` demonstrates frequency-based prefix lookup and can return actual matching ranges.

`longest_subarray_sum_equals_k` changes the stored information from frequency to earliest position because the optimization objective is interval length rather than the number of matches.

`zero_sum_subarrays` stores every position associated with a repeated prefix so that all valid ranges can be reconstructed.

`count_equal_zero_one_subarrays` demonstrates the `-1/+1` transformation for equal binary frequencies.

`longest_equal_frequency_subarray` generalizes the technique to multiple symbols by storing relative frequency differences.

`count_subarrays_with_all_symbols_equal_frequency` shows that the same vector-state concept can count intervals rather than merely find the longest one.

The script also validates binary input and rejects symbols that do not belong to the declared frequency domain.

## JavaScript Implementation

The JavaScript implementation uses `Map` as the primary prefix-state index.

`countSubarraysWithSum` demonstrates the frequency form of prefix tracking.

`findSubarraysWithSum` keeps arrays of positions for each prefix value because returning all intervals requires more information than counting them.

`longestZeroSumSubarray` uses the earliest-position strategy.

The equal-frequency functions use JavaScript `Map` state keys and explicitly validate their symbol domain.

The file also contains an event-driven Pull Request model. Its purpose is to connect state tracking to a realistic state-machine problem without pretending that repository governance is the same algorithm as array processing.

The `PullRequestWorkflow` object tracks draft status, review requests, review decisions, status checks, source updates, base synchronization, conflicts, closure, reopening, and merge strategy. Merge eligibility is evaluated from the current Pull Request state and an explicit policy.

## C++ Repository Governance Case Study

The C++ program combines prefix-state algorithms with a repository governance case study.

The algorithmic portion uses `unordered_map` for prefix frequencies and introduces a custom `FrequencyStateHash` for multidimensional equal-frequency states.

The governance model is deliberately separate from the array algorithms. A `PullRequest` contains its source branch, target branch, revisions, review states, status checks, draft state, and conflict state.

`BranchProtection` defines repository-level constraints such as required approvals, required status checks, direct-push restrictions, and force-push restrictions.

`RepositoryGovernance::mergeEligible` evaluates those conditions together.

This distinction is important:

- The Pull Request represents the proposed change.
- Reviews represent evaluation of that change.
- Approvals represent particular review decisions.
- Branch protection represents repository policy that can make conditions mandatory.

A conflict therefore makes the Pull Request ineligible even when the required number of approvals and status checks are present.

The program is designed for C++17 and uses standard-library containers only.

## Java Enterprise Domain Model

The Java implementation uses explicit domain types instead of representing repository governance as loosely structured strings.

`ReviewState` distinguishes comments, approvals, and requested changes.

`PullRequestState` represents lifecycle states such as draft, open, closed, and merged.

`Review` is a record containing the reviewer, decision, and commit against which the review was made.

`BranchProtectionPolicy` captures required approvals, required status checks, conversation requirements, direct-push restrictions, and force-push restrictions.

`PullRequest` owns its reviews and status checks and validates state transitions.

A particularly important rule is approval freshness. An approval applies to a particular commit. When the Pull Request head changes, the implementation replaces the review commit references so that the subsequent merge decision evaluates whether approvals correspond to the current revision.

The `RepositoryGovernanceService` keeps repository-level policy separate from the Pull Request's domain state.

This structure models the relationship between change lifecycle and repository governance without treating them as a single concept.

## SQL Data Model

The PostgreSQL implementation represents the governance domain relationally.

`repositories` stores repository identity and its default branch.

`branches` associates branches with repositories and records whether a branch is protected.

`pull_requests` records source and target branches, author, lifecycle state, draft status, current head commit, base commit, and merge conflicts.

`pull_request_commits` records the commits associated with a Pull Request.

`reviews` records the reviewer, review state, and exact commit reviewed.

`review_comments` stores file-level discussion and whether each discussion has been resolved.

`status_checks` records check results against a specific commit.

`branch_protection_policies` stores repository governance rules, while `required_status_checks` expresses the required checks relationally.

Foreign keys prevent references to nonexistent repositories, branches, users, commits, reviews, and policies.

Check constraints restrict lifecycle and review values to known states.

Indexes target common governance queries such as Pull Requests by target branch and state, reviews by Pull Request and state, current-commit review lookups, status-check lookups, and unresolved review discussions.

## Approval Freshness

An approval is not necessarily a permanent property of a Pull Request.

A reviewer approves a particular version of the proposed change. If new commits modify the Pull Request, the repository may require a new review.

The SQL view `pull_request_merge_eligibility` therefore compares:

`reviews.reviewed_commit_id`

with:

`pull_requests.head_commit_id`.

A mismatch is reported as `STALE_REVIEW`.

The Java model applies the same domain rule through the `Review` record and the Pull Request's current head commit.

This separates the concept of "a reviewer approved something" from the more precise question "has an eligible reviewer approved the current proposed revision?"

## Pull Request Lifecycle

A Pull Request is the change-proposal workflow.

The relevant lifecycle in these implementations includes draft creation, readiness for review, review requests, review activity, source updates, base synchronization, conflict handling, closure, reopening, and merge.

A draft Pull Request is intentionally not treated as merge-ready.

When the source branch changes, the proposed changeset changes. Review and status-check information may therefore need to be evaluated against the new head revision.

When the base branch changes, synchronization can reveal conflicts. A conflict blocks merge eligibility until it is resolved.

Merge strategy is a property of the final integration operation. The JavaScript model explicitly accepts `merge`, `squash`, or `rebase` only after eligibility has been established.

## Code Review

Code review is the evaluation mechanism applied to the proposed change.

The implementations distinguish review states:

`COMMENTED` represents feedback without approval.

`CHANGES_REQUESTED` indicates that the reviewer requires modification before the change should be accepted.

`APPROVED` represents a positive review decision.

Review comments are separate records from the overall review state in the SQL model. This allows several inline discussions to exist under a review and allows each discussion to be resolved independently.

Review quality depends on the reviewer evaluating the relevant changeset rather than merely providing a nominal approval. The commit association in the Java and SQL implementations makes the evaluated revision explicit.

A review system should also avoid treating comments as equivalent to approvals. A comment can identify a defect, ask a question, or explain an architectural concern without granting merge permission.

## Approvals

Approval is a decision with governance significance.

The approval requirement belongs to repository policy rather than merely to the Pull Request's local data.

The sample policy requires two distinct approved reviewers. The implementations use reviewer identity rather than counting review rows blindly, preventing duplicate approval records from artificially satisfying the threshold.

Approval freshness is also evaluated against the current head commit.

This produces a clear relationship:

`review decision -> approval state -> policy threshold -> merge eligibility`.

Approval alone does not guarantee merge eligibility because required status checks, conflict state, draft state, unresolved conversations, and other branch-policy requirements can independently block the merge.

## Branch Protection

Branch protection is the repository-level enforcement layer.

The PostgreSQL policy records whether direct pushes and force pushes are allowed, whether conversations must be resolved, whether linear history is required, and how many approvals are required.

A protected branch can therefore impose conditions that individual contributors cannot bypass through an ordinary Pull Request workflow.

The SQL data model deliberately keeps branch protection separate from Pull Request records. This allows the same policy to govern multiple Pull Requests targeting the protected branch.

The C++ and Java governance models follow the same separation by placing merge rules inside a policy object rather than hard-coding every requirement into Pull Request state.

Branch protection is not itself a review. It is not itself an approval. It is the repository policy that determines which conditions must be satisfied before integration is permitted.

## Relationship Between the Four Areas

The four areas form a dependency chain without becoming interchangeable:

`Pull Request -> Code Review -> Approval Decisions -> Branch Protection Enforcement`

A Pull Request defines the proposed change and its lifecycle.

Code review evaluates the changeset and records reviewer interaction.

An approval is one particular review outcome that may satisfy an approval requirement.

Branch protection determines which approvals and other repository conditions are mandatory before the Pull Request can merge.

A Pull Request can therefore contain approved reviews and still be blocked by a failed security check or merge conflict.

## Edge Cases and Failure Conditions

An empty sequence has no non-empty subarrays, so its prefix state contains only the initial zero state.

Negative values are valid for prefix-sum algorithms. The technique does not require non-negative input.

A target sum can also be negative or zero.

Repeated prefix sums can generate many zero-sum intervals. Replacing a frequency table with a set is therefore correct only when existence is the sole requirement.

For longest-subarray problems, storing the earliest prefix position is essential. Replacing it with the most recent position can silently produce shorter answers.

Equal-frequency tracking requires a consistent reference symbol. Every other symbol's count is compared against that reference.

Unexpected symbols must be rejected rather than silently inserted into a frequency vector with an incompatible interpretation.

For repository governance, a Pull Request with enough approvals can still be blocked by a conflict, a failed required check, unresolved conversations, draft state, or stale approvals.

## Performance Considerations

For scalar prefix states, hash-based counting requires expected `O(n)` time and `O(n)` additional state.

A naive enumeration of all subarrays requires `O(n²)` interval examination before optimization.

For a frequency vector with `d - 1` independent dimensions, each state update can require `O(d)` work. The total expected complexity becomes approximately `O(n d)` with `O(n d)` state storage when each vector is materialized.

Returning every matching subarray can itself require `O(n²)` output because the number of valid intervals can be quadratic.

Hash-table operations are expected constant time, not a mathematical worst-case guarantee. Hash quality, memory pressure, collision behavior, and state representation therefore matter in production systems.

## Security and Reliability Considerations

Hash-based state structures should not be treated as a substitute for input validation.

The implementations reject invalid binary symbols and unknown equal-frequency categories.

The repository-governance models keep authorization and policy concepts explicit. In a production repository service, the ability to approve, dismiss an approval, bypass protection, or merge would require authenticated identity and authorization checks in addition to the state rules demonstrated here.

A database constraint is valuable for invariants that must survive application failures. Foreign keys, unique constraints, and check constraints prevent classes of invalid states independently of application logic.

Approval freshness is particularly important because accepting an old approval after a material source update can undermine the purpose of review.

## Common Implementation Mistakes

Using a plain set when the task requires counting loses information about repeated prefix states.

Keeping only the latest prefix position when finding a longest interval can destroy the optimal earlier endpoint.

Forgetting the initial prefix state `0` causes subarrays beginning at index zero to be missed.

Mapping binary values inconsistently, such as treating zero as `0` instead of `-1`, prevents equal-frequency detection from becoming a zero-sum condition.

For multidimensional frequency states, comparing absolute counts at the current prefix is insufficient. The useful state is the vector of differences from a reference category.

In governance systems, counting all approval rows rather than distinct eligible reviewers can incorrectly satisfy an approval threshold.

Treating an approval as permanently valid after the Pull Request head changes can allow an outdated review decision to authorize a newer changeset.

Treating branch protection as synonymous with code review also obscures the difference between reviewer evaluation and repository-level enforcement.

## Production Design Implications

Prefix-state algorithms are strongest when the required interval property can be expressed as equality or a simple difference between two accumulated states.

The state definition should be established before choosing the hash-table representation.

For scalar states, an integer key is usually sufficient.

For multidimensional conditions, an immutable tuple, record, vector, or canonical serialized representation provides a composite key.

For counting, preserve frequencies.

For longest intervals, preserve earliest positions.

For reconstruction, preserve all relevant positions.

For governance systems, preserve the revision associated with each review and status check. Merge eligibility should be calculated from the current Pull Request head, current policy, current review decisions, current check results, and current conflict state rather than from an irreversible historical boolean.

The same design principle appears in both domains: **the stored state must preserve exactly the information required to prove the condition being evaluated.**
