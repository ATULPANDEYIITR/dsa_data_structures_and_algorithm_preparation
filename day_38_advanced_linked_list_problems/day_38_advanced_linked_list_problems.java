import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class AdvancedLinkedListProblems {

    static final class Node {
        final int value;
        Node next;

        Node(int value) {
            this.value = value;
        }
    }

    static final class SinglyLinkedList {
        Node head;
        Node tail;

        SinglyLinkedList(int... values) {
            for (int value : values) {
                append(value);
            }
        }

        Node append(int value) {
            Node node = new Node(value);

            if (head == null) {
                head = tail = node;
            } else {
                tail.next = node;
                tail = node;
            }

            return node;
        }

        String display() {
            StringBuilder result = new StringBuilder();
            Node current = head;
            Set<Node> seen = new HashSet<>();

            while (current != null) {
                if (!seen.add(current)) {
                    result.append(" -> ").append(current.value).append(" (cycle)");
                    break;
                }

                if (!result.isEmpty()) {
                    result.append(" -> ");
                }

                result.append(current.value);
                current = current.next;
            }

            return result.toString();
        }
    }

    static Node mergeSorted(Node first, Node second) {
        Node dummy = new Node(0);
        Node tail = dummy;

        while (first != null && second != null) {
            if (first.value <= second.value) {
                tail.next = first;
                first = first.next;
            } else {
                tail.next = second;
                second = second.next;
            }

            tail = tail.next;
        }

        tail.next = first != null ? first : second;
        return dummy.next;
    }

    static Node removeSortedDuplicates(Node head) {
        Node current = head;

        while (current != null && current.next != null) {
            if (current.value == current.next.value) {
                current.next = current.next.next;
            } else {
                current = current.next;
            }
        }

        return head;
    }

    static Node removeNthFromEnd(Node head, int n) {
        if (n <= 0) {
            throw new IllegalArgumentException("n must be positive");
        }

        Node dummy = new Node(0);
        dummy.next = head;

        Node fast = dummy;

        for (int i = 0; i < n; i++) {
            fast = fast.next;

            if (fast == null) {
                throw new IllegalArgumentException(
                    "n exceeds the list length"
                );
            }
        }

        Node slow = dummy;

        while (fast.next != null) {
            fast = fast.next;
            slow = slow.next;
        }

        slow.next = slow.next.next;
        return dummy.next;
    }

    static Node findIntersection(Node first, Node second) {
        Node a = first;
        Node b = second;

        while (a != b) {
            a = a != null ? a.next : second;
            b = b != null ? b.next : first;
        }

        return a;
    }

    static boolean hasCycle(Node head) {
        Node slow = head;
        Node fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow == fast) {
                return true;
            }
        }

        return false;
    }

    static Node cycleEntry(Node head) {
        Node slow = head;
        Node fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow == fast) {
                slow = head;

                while (slow != fast) {
                    slow = slow.next;
                    fast = fast.next;
                }

                return slow;
            }
        }

        return null;
    }

    static Node reverse(Node head) {
        Node previous = null;
        Node current = head;

        while (current != null) {
            Node following = current.next;
            current.next = previous;
            previous = current;
            current = following;
        }

        return previous;
    }

    static boolean isPalindrome(Node head) {
        if (head == null || head.next == null) {
            return true;
        }

        Node slow = head;
        Node fast = head;

        while (fast.next != null && fast.next.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }

        Node secondHalf = reverse(slow.next);
        slow.next = secondHalf;

        Node left = head;
        Node right = secondHalf;
        boolean result = true;

        while (right != null) {
            if (left.value != right.value) {
                result = false;
                break;
            }

            left = left.next;
            right = right.next;
        }

        slow.next = reverse(secondHalf);
        return result;
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        CLOSED,
        MERGED
    }

    enum ReviewDecision {
        APPROVED,
        CHANGES_REQUESTED,
        COMMENTED,
        DISMISSED
    }

    enum CheckState {
        PASSING,
        FAILING,
        PENDING
    }

    record Reviewer(String username, boolean eligible) {}

    record Review(
        Reviewer reviewer,
        ReviewDecision decision
    ) {}

    record StatusCheck(
        String name,
        CheckState state,
        boolean required
    ) {}

    interface MergeRule {
        String description();
        boolean satisfied(PullRequest pullRequest);
    }

    static final class RequiredApprovalsRule implements MergeRule {
        private final int required;

        RequiredApprovalsRule(int required) {
            if (required < 0) {
                throw new IllegalArgumentException(
                    "required approvals cannot be negative"
                );
            }
            this.required = required;
        }

        @Override
        public String description() {
            return "At least " + required + " eligible approvals";
        }

        @Override
        public boolean satisfied(PullRequest pullRequest) {
            Set<String> approvers = new HashSet<>();

            for (Review review : pullRequest.reviews) {
                if (review.reviewer.eligible()
                    && review.decision == ReviewDecision.APPROVED) {
                    approvers.add(review.reviewer.username());
                }
            }

            return approvers.size() >= required;
        }
    }

    static final class PassingChecksRule implements MergeRule {
        @Override
        public String description() {
            return "All required status checks are passing";
        }

        @Override
        public boolean satisfied(PullRequest pullRequest) {
            return pullRequest.checks.stream()
                .filter(StatusCheck::required)
                .allMatch(check -> check.state() == CheckState.PASSING);
        }
    }

    static final class DiscussionRule implements MergeRule {
        @Override
        public String description() {
            return "All required review discussions are resolved";
        }

        @Override
        public boolean satisfied(PullRequest pullRequest) {
            return pullRequest.unresolvedDiscussions == 0;
        }
    }

    static final class PullRequest {
        private final String id;
        private final String sourceBranch;
        private final String targetBranch;
        private PullRequestState state;
        private final boolean mergeConflicts;
        private final List<Review> reviews;
        private final List<StatusCheck> checks;
        private int unresolvedDiscussions;

        PullRequest(
            String id,
            String sourceBranch,
            String targetBranch,
            PullRequestState state,
            boolean mergeConflicts,
            List<Review> reviews,
            List<StatusCheck> checks,
            int unresolvedDiscussions
        ) {
            this.id = Objects.requireNonNull(id);
            this.sourceBranch = Objects.requireNonNull(sourceBranch);
            this.targetBranch = Objects.requireNonNull(targetBranch);
            this.state = Objects.requireNonNull(state);
            this.mergeConflicts = mergeConflicts;
            this.reviews = new ArrayList<>(reviews);
            this.checks = new ArrayList<>(checks);
            this.unresolvedDiscussions = unresolvedDiscussions;
        }

        boolean isOpen() {
            return state == PullRequestState.OPEN;
        }

        boolean hasMergeConflicts() {
            return mergeConflicts;
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        List<StatusCheck> checks() {
            return List.copyOf(checks);
        }

        int unresolvedDiscussions() {
            return unresolvedDiscussions;
        }

        void resolveDiscussion() {
            if (unresolvedDiscussions == 0) {
                throw new IllegalStateException(
                    "No unresolved discussion exists"
                );
            }

            unresolvedDiscussions--;
        }

        void merge() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                    "Only an open pull request can be merged"
                );
            }

            state = PullRequestState.MERGED;
        }

        String id() {
            return id;
        }

        String sourceBranch() {
            return sourceBranch;
        }

        String targetBranch() {
            return targetBranch;
        }
    }

    static final class MergeEligibilityService {
        private final List<MergeRule> rules;

        MergeEligibilityService(List<MergeRule> rules) {
            this.rules = List.copyOf(rules);
        }

        List<String> blockers(PullRequest pullRequest) {
            List<String> blockers = new ArrayList<>();

            if (!pullRequest.isOpen()) {
                blockers.add("pull request is not open");
            }

            if (pullRequest.hasMergeConflicts()) {
                blockers.add(
                    "source branch conflicts with the target branch"
                );
            }

            for (MergeRule rule : rules) {
                if (!rule.satisfied(pullRequest)) {
                    blockers.add(rule.description());
                }
            }

            return blockers;
        }

        boolean eligible(PullRequest pullRequest) {
            return blockers(pullRequest).isEmpty();
        }
    }

    static void demonstrateRepositoryGovernance() {
        Reviewer alice = new Reviewer("alice", true);
        Reviewer bob = new Reviewer("bob", true);
        Reviewer contractor = new Reviewer("contractor", false);

        PullRequest pullRequest = new PullRequest(
            "PR-482",
            "feature/payment-reconciliation",
            "main",
            PullRequestState.OPEN,
            false,
            List.of(
                new Review(alice, ReviewDecision.APPROVED),
                new Review(bob, ReviewDecision.APPROVED),
                new Review(contractor, ReviewDecision.APPROVED)
            ),
            List.of(
                new StatusCheck(
                    "unit-tests",
                    CheckState.PASSING,
                    true
                ),
                new StatusCheck(
                    "security-scan",
                    CheckState.PASSING,
                    true
                ),
                new StatusCheck(
                    "integration-tests",
                    CheckState.PENDING,
                    true
                )
            ),
            1
        );

        MergeEligibilityService service = new MergeEligibilityService(
            List.of(
                new RequiredApprovalsRule(2),
                new PassingChecksRule(),
                new DiscussionRule()
            )
        );

        printEligibility(service, pullRequest);

        pullRequest.checks().get(2);
        pullRequest.resolveDiscussion();

        /*
         * The example intentionally keeps the status-check object immutable.
         * In a real service, a check update would replace the stored state
         * rather than mutating a record. This makes state transitions explicit.
         */
        PullRequest readyPullRequest = new PullRequest(
            "PR-482",
            "feature/payment-reconciliation",
            "main",
            PullRequestState.OPEN,
            false,
            pullRequest.reviews(),
            List.of(
                new StatusCheck("unit-tests", CheckState.PASSING, true),
                new StatusCheck("security-scan", CheckState.PASSING, true),
                new StatusCheck(
                    "integration-tests",
                    CheckState.PASSING,
                    true
                )
            ),
            0
        );

        printEligibility(service, readyPullRequest);

        if (service.eligible(readyPullRequest)) {
            readyPullRequest.merge();
            System.out.println(
                "State transition: OPEN -> MERGED"
            );
        }
    }

    static void printEligibility(
        MergeEligibilityService service,
        PullRequest pullRequest
    ) {
        List<String> blockers = service.blockers(pullRequest);

        System.out.println(
            pullRequest.id() + " merge eligibility: "
            + (blockers.isEmpty() ? "ELIGIBLE" : "BLOCKED")
        );

        blockers.forEach(blocker ->
            System.out.println("  - " + blocker)
        );
    }

    public static void main(String[] args) {
        System.out.println("ADVANCED LINKED-LIST PROBLEMS");

        SinglyLinkedList first = new SinglyLinkedList(1, 3, 5, 7);
        SinglyLinkedList second = new SinglyLinkedList(2, 3, 6, 8);
        Node merged = mergeSorted(first.head, second.head);

        SinglyLinkedList mergedView = new SinglyLinkedList();
        mergedView.head = merged;
        System.out.println("Merged: " + mergedView.display());

        SinglyLinkedList duplicates =
            new SinglyLinkedList(1, 1, 2, 2, 3, 3, 4);
        duplicates.head = removeSortedDuplicates(duplicates.head);
        System.out.println(
            "Duplicates removed: " + duplicates.display()
        );

        SinglyLinkedList nth =
            new SinglyLinkedList(10, 20, 30, 40, 50);
        nth.head = removeNthFromEnd(nth.head, 2);
        System.out.println(
            "Nth from end removed: " + nth.display()
        );

        Node shared = new Node(90);
        shared.next = new Node(100);

        SinglyLinkedList firstPrefix =
            new SinglyLinkedList(10, 20);
        firstPrefix.tail.next = shared;
        firstPrefix.tail = shared.next;

        SinglyLinkedList secondPrefix =
            new SinglyLinkedList(30, 40, 50);
        secondPrefix.tail.next = shared;
        secondPrefix.tail = shared.next;

        Node intersection = findIntersection(
            firstPrefix.head,
            secondPrefix.head
        );

        System.out.println(
            "Intersection: "
            + (intersection == null ? "none" : intersection.value)
        );

        SinglyLinkedList circular =
            new SinglyLinkedList(1, 2, 3, 4, 5);
        circular.tail.next = circular.head.next.next;

        Node entry = cycleEntry(circular.head);
        System.out.println(
            "Cycle detected: " + hasCycle(circular.head)
        );
        System.out.println(
            "Cycle entry: "
            + (entry == null ? "none" : entry.value)
        );

        SinglyLinkedList palindrome =
            new SinglyLinkedList(1, 2, 3, 2, 1);

        System.out.println(
            "Palindrome: " + isPalindrome(palindrome.head)
        );
        System.out.println(
            "Restored palindrome: " + palindrome.display()
        );

        demonstrateRepositoryGovernance();
    }
}
