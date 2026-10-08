# Advanced Linked-List Problems

## Scope

This learning artifact focuses on six advanced linked-list problems:

- merging two sorted lists
- removing duplicates
- removing the nth node from the end
- detecting intersection
- working with circular lists
- detecting a palindrome linked list

The implementations deliberately use different perspectives in each language. Python emphasizes reusable algorithms and edge-case validation. JavaScript emphasizes object identity, iterators, `Set`, and event-driven processing. C++ combines pointer algorithms with explicit memory ownership and a repository-governance case study. Java models the domain with interfaces, records, enums, collections, and explicit merge rules. PostgreSQL represents linked-list-related structures and repository governance as relational data with integrity constraints and merge-eligibility queries.

The six linked-list problems share a central property: the important state is represented by links between nodes rather than by contiguous storage. That changes how traversal, insertion, deletion, cycle detection, and identity comparisons must be reasoned about.

## Core Linked-List Model

A singly linked list consists of nodes where each node stores a value and a reference or pointer to another node.

The Python, JavaScript, C++, and Java implementations use a structure equivalent to:

`value -> next`

The final node in a normal acyclic list has `next = null` or its language-specific equivalent. A circular list instead contains a link that eventually points back to an existing node.

The distinction between a node's value and its identity is essential. Two nodes may both contain `50` while still being completely different objects. Conversely, two separate lists may physically share the same node. Intersection detection therefore compares node identity rather than only node values.

## Merge Two Sorted Lists

Merging sorted lists is a pointer-relinking problem. Given two lists whose values are already ordered, the algorithm compares the current nodes and attaches the smaller node to the result.

The implementations use a dummy node to simplify the first insertion. Once either input reaches its end, the remaining suffix of the other list can be attached without further comparisons.

The iterative algorithm requires `O(n + m)` time and `O(1)` auxiliary space when existing nodes are reused.

The Python implementation exposes both iterative and recursive versions. The iterative version is preferable for large lists because the recursive implementation consumes call-stack space.

The JavaScript implementation uses the same linked-node concept but wraps list construction in a class and provides a generator for safe traversal.

The C++ implementation highlights ownership concerns. Relinking nodes is efficient, but the program must ensure that two owners do not later attempt to delete the same node.

The Java implementation benefits from garbage collection, so the algorithm can focus on references and does not require explicit node deletion.

## Remove Duplicates

Duplicate removal depends on whether the list is sorted.

For a sorted list, equal values are adjacent. A single traversal can compare `current.value` with `current.next.value`. When they match, the current node skips the duplicate node.

This produces `O(n)` time and `O(1)` auxiliary space.

An unsorted list requires a different strategy. The Python implementation includes a separate unsorted-list method using a `set` of previously observed values. That approach has expected `O(n)` time and `O(n)` additional memory.

The distinction matters because applying the sorted-list algorithm to an unsorted list is incorrect. For example, `4 -> 2 -> 4` contains a duplicate even though the two `4` nodes are not adjacent.

## Remove the Nth Node from the End

Finding the nth node from the end can be performed in one traversal with two pointers separated by `n` nodes.

A dummy node before the real head removes a special case when the node being removed is the first node. The fast pointer advances `n` positions first. The slow pointer then follows until fast reaches the final node. At that point, `slow.next` is the node that must be removed.

The method runs in `O(n)` time and uses `O(1)` auxiliary space.

Validation is important. A non-positive `n` is invalid, and an `n` larger than the list length must not silently modify the list.

## Detect Intersection

Linked-list intersection means that two lists eventually reference the same physical node.

Consider:

`A1 -> A2 -> C1 -> C2`

and

`B1 -> B2 -> B3 -> C1 -> C2`

The intersection is `C1`, not merely a value equal to `C1`.

The pointer-switching algorithm starts one pointer on each head. When a pointer reaches the end of its list, it continues from the other list's head. Each pointer therefore traverses the combined lengths of both lists. Their unequal prefixes cancel out, allowing the pointers to meet at the shared node or both reach `null`.

The algorithm runs in `O(n + m)` time and `O(1)` auxiliary space.

The examples intentionally compare object identity. This is especially visible in JavaScript, C++, and Java because values can be equal while references point to different node objects.

## Circular Lists

A circular linked list has no terminating `null` link along its cycle.

Naive traversal is dangerous because code that assumes `current != null` as its stopping condition will never terminate.

Floyd's tortoise-and-hare algorithm solves cycle detection using two pointers. The slow pointer advances one node while the fast pointer advances two. If a cycle exists, the fast pointer eventually catches the slow pointer.

After a meeting occurs, resetting one pointer to the head and moving both pointers one step at a time identifies the cycle entry.

This requires `O(n)` time and `O(1)` auxiliary space.

The Python, JavaScript, C++, and Java implementations expose both cycle detection and cycle-entry detection. The examples also construct an actual cycle so that the behavior is demonstrated rather than represented only through theoretical discussion.

The C++ implementation is particularly careful because cyclic structures interact with memory ownership. A destructor that blindly follows `next` cannot assume that the structure is acyclic.

## Circular Elimination

Circular structures also appear in elimination problems. The Python and JavaScript implementations include the Josephus recurrence as a compact example of reasoning over circular positions.

For a circle of size `n` and step `k`, the survivor can be computed iteratively without physically creating a circular linked list. The recurrence transforms the survivor's position from a smaller circle into the coordinate system of the larger circle.

This illustrates an important algorithm-design principle: a linked-list representation may model a problem naturally, but it is not always the most efficient implementation.

## Palindrome Linked List

A palindrome reads identically in both directions.

For a linked list, random access is unavailable, so an efficient algorithm finds the midpoint with slow and fast pointers, reverses the second half, compares both halves, and restores the reversed half.

The restoration step is important when the function is expected to be non-destructive from the caller's perspective.

The Python, JavaScript, C++, and Java implementations therefore demonstrate:

`find midpoint -> reverse second half -> compare -> restore`

The algorithm runs in `O(n)` time and `O(1)` auxiliary space.

A recursive alternative is also shown in Python. Recursion makes the comparison conceptually simple but consumes `O(n)` stack space.

## Python Implementation

The Python program provides a broad algorithmic treatment of the topic.

`Node` represents the linked-list node. `build_list` constructs ordinary lists while `to_list` provides bounded traversal so that accidental cycles do not cause an infinite display operation.

`merge_two_sorted_lists` demonstrates in-place pointer reuse. `remove_duplicates_sorted` exploits adjacency created by sorting, while `remove_duplicates_unsorted` uses a set when adjacency cannot be assumed.

`remove_nth_from_end` demonstrates the two-pointer gap technique. `intersection_node` compares node identity and uses pointer switching.

`has_cycle`, `cycle_entry`, and `cycle_length` demonstrate Floyd's algorithm. `josephus_circular` shows that some circular problems can be solved mathematically without constructing nodes.

`is_palindrome` demonstrates constant-space palindrome checking while restoring the list. The script also includes validation failures and edge cases such as empty lists, single-node lists, invalid nth-node requests, and cycles.

## JavaScript Implementation

The JavaScript implementation uses a `ListNode` class and a `LinkedList` class to separate node representation from list construction and traversal.

The `values()` generator provides lazy traversal. A `Set` of visited node objects protects diagnostic traversal from infinite loops in cyclic structures.

The intersection implementation relies on JavaScript object identity. Two separate objects with the same numeric value are not considered the same node.

The event-driven section introduces a small `WorkflowEmitter`. Linked-list operations emit domain events such as `merged` and `palindromeChecked`. This provides a JavaScript-specific example of how algorithmic processing can be integrated into event-oriented application code.

JavaScript's `Set` is also useful for duplicate tracking and cycle-safe diagnostic traversal. The implementation avoids unnecessary external packages.

## C++ Case Study

The C++ program combines linked-list algorithms with explicit memory-management concerns and a repository-governance case study.

The `LinkedList` class owns dynamically allocated nodes for ordinary lists. Copying is disabled to prevent accidental double ownership, while move operations transfer ownership explicitly.

The destructor uses a visited-node set so that an accidentally cyclic structure does not cause an endless deletion traversal.

The repository case study represents a pull request with a source branch, target branch, reviews, status checks, unresolved discussions, conflicts, and a merge policy.

This separation is deliberate. Linked-list algorithms determine structural properties such as node order, shared identity, and cycles. The governance model determines whether a change is allowed to merge.

`countEligibleApprovals` distinguishes eligible reviewers from reviewers who are not permitted to satisfy an approval requirement. `checksPass` evaluates required status checks. `mergeBlockers` collects independent reasons that prevent merging.

The resulting evaluator demonstrates that merge eligibility is a conjunction of several independent conditions rather than a synonym for having a valid commit chain.

## Java Enterprise-Oriented Model

The Java program uses explicit domain types to separate algorithmic behavior from repository governance.

`PullRequestState`, `ReviewDecision`, and `CheckState` are enums because their values represent controlled state machines rather than arbitrary strings.

`Reviewer`, `Review`, and `StatusCheck` are records because they represent compact immutable data.

The `MergeRule` interface models a policy rule. `RequiredApprovalsRule`, `PassingChecksRule`, and `DiscussionRule` implement different merge requirements without collapsing them into one large conditional statement.

`MergeEligibilityService` evaluates the rules and returns specific blockers. This makes policy failures observable and testable.

The example also distinguishes reviewer eligibility from approval state. An approved review from an ineligible reviewer does not automatically satisfy a required-approval rule.

The `PullRequest.merge()` method protects its own state transition by allowing merging only from the open state. This prevents invalid transitions such as merging an already closed pull request.

## SQL Data Model

The PostgreSQL implementation represents the surrounding repository workflow relationally.

`repositories` and `branches` establish repository and branch identity. `pull_requests` connects authors, source branches, and target branches.

`commits` represents commit objects, while `pull_request_commits` preserves the ordered changeset associated with a pull request. The parent-commit relationship models commit ancestry without treating the commit chain as an ordinary array.

`reviewers`, `reviews`, and `review_comments` separate reviewer eligibility, review decisions, and discussion-level information.

`status_checks` records individual automated checks and whether each is required.

`branch_protection_policies` contains repository-governance requirements associated with protected target branches. Requirements include minimum approvals, passing checks, resolved conversations, direct-push restrictions, force-push restrictions, deletion restrictions, linear-history requirements, and stale-approval policy.

The `merge_eligibility` view combines these independent facts into a database-level evaluation.

## Approval Semantics

An approval is a review decision, not simply evidence that somebody inspected a change.

The data model records the reviewer, review state, eligibility, and timestamps separately. This allows policies to distinguish an approval from a comment or a changes-requested review.

The examples count distinct eligible approvers. An ineligible reviewer may submit an approval, but that approval does not satisfy a policy requiring eligible reviewers.

Approval requirements can also become stale when the underlying changeset changes. The SQL schema includes `dismiss_stale_approvals` as an explicit policy property so that the repository governance layer can represent that behavior rather than assuming every historical approval remains valid indefinitely.

## Code Review Mechanics

Code review operates at the level of proposed changes and their discussion.

The relational model separates reviews from review comments. A review represents the reviewer's decision state, while a comment can be attached to a particular commit and source location.

Unresolved comments are therefore different from a review state. A pull request can have approvals and still contain unresolved conversations if the branch protection policy requires those conversations to be resolved before merging.

The Java and C++ implementations model this distinction through separate approval and discussion conditions.

Review quality also depends on reviewer eligibility and scope. A policy should not infer authorization merely from the existence of a review record.

## Pull Request Lifecycle

A pull request provides the workflow container for a proposed change.

The modeled lifecycle distinguishes draft, open, closed, and merged states. A draft can exist while work is still being prepared. An open pull request is eligible for review and status evaluation. A closed pull request is no longer an active merge candidate. A merged pull request represents a completed integration.

The source branch identifies where the proposed changes originate. The target branch identifies the branch whose governance rules control the merge.

Synchronizing a source branch with its target can change the effective changeset. This is relevant to conflicts and stale review decisions because approval is attached to a particular review context rather than being an unconditional authorization for every future version of the branch.

## Branch Protection

Branch protection is repository governance applied to a branch.

The SQL policy explicitly represents:

- required approvals
- required passing checks
- required resolution of review conversations
- restrictions on direct pushes
- restrictions on force pushes
- branch-deletion restrictions
- linear-history requirements
- stale-approval dismissal behavior

These are not properties of a pull request alone. They are constraints imposed by the protected target branch.

A pull request can therefore be technically valid while still being blocked by branch policy. Conversely, an approval does not override a failing required status check.

The C++ and Java governance models demonstrate this separation by evaluating multiple independent merge conditions.

## Relationship Between the Categories

A pull request provides the workflow through which a proposed changeset is evaluated.

Code review evaluates the changeset and records reviewer decisions and discussions.

Approvals represent specific review decisions that may satisfy part of a repository policy.

Branch protection defines the repository-level conditions under which a proposed change may be integrated into the protected target branch.

These mechanisms overlap operationally but are not interchangeable. Treating them as separate domain concepts produces clearer implementations and prevents incorrect assumptions such as equating an approval with merge permission.

## Edge Cases

Empty lists must be handled without dereferencing a missing head node.

A single-node list is both trivially a palindrome and a boundary case for deletion.

Removing the nth node requires validation when `n` is zero, negative, or larger than the list length.

Two lists with equal values do not necessarily intersect. Intersection requires shared node identity.

A circular list cannot be traversed safely using only a `null` termination condition.

A cycle can begin at the head or at an interior node, and the cycle length may be one.

A palindrome algorithm that reverses the second half without restoring it changes the caller's data structure. The implementations restore the structure after comparison.

Duplicate removal must respect whether ordering is guaranteed. An adjacent-comparison algorithm is correct for sorted input but incomplete for arbitrary input.

## Performance Considerations

The principal algorithms are linear because each relevant node is visited a bounded number of times.

Merging two sorted lists is `O(n + m)` and can use constant auxiliary space when nodes are reused.

Removing duplicates from a sorted list is `O(n)` with constant auxiliary space.

Removing duplicates from an unsorted list is expected `O(n)` with `O(n)` additional memory when a hash set is used.

Nth-node removal is `O(n)` with constant auxiliary space.

Intersection detection is `O(n + m)` with constant auxiliary space.

Floyd cycle detection and cycle-entry discovery are `O(n)` with constant auxiliary space.

Palindrome detection using midpoint discovery and in-place reversal is `O(n)` with constant auxiliary space.

Recursive algorithms trade auxiliary memory for implementation simplicity because each recursive call occupies stack space.

## Common Failure Modes

Comparing node values instead of node identity produces incorrect intersection results.

Using a `null`-based traversal loop on a circular list can produce an infinite loop.

Forgetting the dummy node in nth-node removal often creates unnecessary special-case logic when the head itself must be removed.

Failing to restore a reversed palindrome half mutates the input unexpectedly.

Using the sorted duplicate-removal algorithm on unsorted data leaves non-adjacent duplicates intact.

Treating every approval as eligible can violate repository review policy.

Treating review approval as sufficient for merging ignores status checks, unresolved discussions, conflicts, and protected-branch requirements.

## Practical Design Principles

Pointer algorithms should state clearly whether they mutate existing nodes or allocate new nodes.

Identity-sensitive operations should compare references or pointers rather than values.

Algorithms that temporarily mutate a data structure should restore it when callers expect non-destructive behavior.

Validation should happen before pointer movement that assumes a valid input range.

Repository governance should be modeled as independent policy rules rather than as one opaque merge condition.

Database constraints should enforce structural invariants that belong at the persistence layer, while application services should evaluate workflow policies that depend on multiple domain facts.

The implementations demonstrate these principles through actual pointer manipulation, state transitions, policy evaluation, relational constraints, and executable edge-case handling.
