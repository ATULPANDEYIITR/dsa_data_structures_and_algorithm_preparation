import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;

/*
 * Enterprise-oriented linked-list assessment.
 *
 * The domain models ordered processing records and exposes algorithms used
 * by an in-memory ingestion pipeline. Node identity is significant for
 * intersection detection, while values determine sorting and palindrome
 * comparisons.
 */
public class LinkedListAssessment {

    static final class Node {
        final int value;
        Node next;

        Node(int value) {
            this.value = value;
        }
    }

    static Node fromList(List<Integer> values) {
        Node dummy = new Node(0);
        Node tail = dummy;

        for (int value : values) {
            tail.next = new Node(value);
            tail = tail.next;
        }
        return dummy.next;
    }

    static List<Integer> toList(Node head) {
        requireAcyclic(head);
        List<Integer> result = new ArrayList<>();

        for (Node current = head; current != null; current = current.next) {
            result.add(current.value);
        }
        return result;
    }

    static boolean hasCycle(Node head) {
        Node slow = head;
        Node fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow == fast) return true;
        }
        return false;
    }

    static void requireAcyclic(Node head) {
        if (hasCycle(head)) {
            throw new IllegalArgumentException(
                "Operation requires an acyclic linked list."
            );
        }
    }

    static void requireDisjoint(Node first, Node second) {
        Set<Node> nodes = Collections.newSetFromMap(
            new java.util.IdentityHashMap<>()
        );

        for (Node current = first; current != null; current = current.next) {
            nodes.add(current);
        }

        for (Node current = second; current != null; current = current.next) {
            if (nodes.contains(current)) {
                throw new IllegalArgumentException(
                    "Input lists must not share nodes."
                );
            }
        }
    }

    static Node reverse(Node head) {
        requireAcyclic(head);
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

    static Node mergeTwoSorted(Node first, Node second) {
        requireAcyclic(first);
        requireAcyclic(second);
        requireDisjoint(first, second);

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

    static Node removeNthFromEnd(Node head, int n) {
        if (n <= 0) {
            throw new IllegalArgumentException("n must be positive.");
        }
        requireAcyclic(head);

        Node dummy = new Node(0);
        dummy.next = head;
        Node fast = dummy;
        Node slow = dummy;

        for (int i = 0; i < n; i++) {
            fast = fast.next;
            if (fast == null) {
                throw new IllegalArgumentException(
                    "n exceeds the list length."
                );
            }
        }

        while (fast.next != null) {
            fast = fast.next;
            slow = slow.next;
        }

        Node removed = slow.next;
        slow.next = removed.next;
        removed.next = null;
        return dummy.next;
    }

    static Node intersectionNode(Node first, Node second) {
        requireAcyclic(first);
        requireAcyclic(second);

        Node left = first;
        Node right = second;

        while (left != right) {
            left = left == null ? second : left.next;
            right = right == null ? first : right.next;
        }
        return left;
    }

    static boolean isPalindrome(Node head) {
        requireAcyclic(head);
        if (head == null || head.next == null) return true;

        Node slow = head;
        Node fast = head;

        while (fast.next != null && fast.next.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }

        Node reversed = reverse(slow.next);
        slow.next = reversed;

        boolean matches = true;
        Node left = head;
        Node right = reversed;

        try {
            while (right != null) {
                if (left.value != right.value) {
                    matches = false;
                    break;
                }
                left = left.next;
                right = right.next;
            }
        } finally {
            // Restoring links matters when callers retain the original list.
            slow.next = reverse(reversed);
        }

        return matches;
    }

    static Node reorder(Node head) {
        requireAcyclic(head);
        if (head == null || head.next == null) return head;

        Node slow = head;
        Node fast = head;

        while (fast.next != null && fast.next.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }

        Node second = slow.next;
        slow.next = null;
        second = reverse(second);

        Node first = head;
        while (second != null) {
            Node firstNext = first.next;
            Node secondNext = second.next;
            first.next = second;
            second.next = firstNext;
            first = firstNext;
            second = secondNext;
        }
        return head;
    }

    static Node mergeKSorted(List<Node> lists) {
        Objects.requireNonNull(lists, "lists cannot be null");

        Set<Node> seen = Collections.newSetFromMap(
            new java.util.IdentityHashMap<>()
        );

        for (Node head : lists) {
            requireAcyclic(head);
            for (Node current = head; current != null; current = current.next) {
                if (!seen.add(current)) {
                    throw new IllegalArgumentException(
                        "Input lists must not share nodes."
                    );
                }
            }
        }

        // The sequence field makes equal-valued entries deterministic.
        final class Entry {
            final Node node;
            final long sequence;

            Entry(Node node, long sequence) {
                this.node = node;
                this.sequence = sequence;
            }
        }

        PriorityQueue<Entry> heap = new PriorityQueue<>(
            Comparator.comparingInt((Entry entry) -> entry.node.value)
                .thenComparingLong(entry -> entry.sequence)
        );

        long sequence = 0;
        for (Node head : lists) {
            if (head != null) heap.add(new Entry(head, sequence++));
        }

        Node dummy = new Node(0);
        Node tail = dummy;

        while (!heap.isEmpty()) {
            Node current = heap.remove().node;
            Node following = current.next;

            tail.next = current;
            tail = current;

            if (following != null) {
                heap.add(new Entry(following, sequence++));
            }
        }

        tail.next = null;
        return dummy.next;
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void expectIllegalArgument(Runnable action) {
        try {
            action.run();
            throw new AssertionError("Expected IllegalArgumentException.");
        } catch (IllegalArgumentException expected) {
            // The tested invalid input was rejected.
        }
    }

    public static void main(String[] args) {
        check(
            toList(reverse(fromList(List.of(1, 2, 3))))
                .equals(List.of(3, 2, 1)),
            "Reverse failed"
        );

        Node cyclic = fromList(List.of(1, 2, 3));
        cyclic.next.next.next = cyclic.next;
        check(hasCycle(cyclic), "Cycle detection failed");
        expectIllegalArgument(() -> reverse(cyclic));

        check(
            toList(mergeTwoSorted(
                fromList(List.of(1, 3, 5)),
                fromList(List.of(2, 4, 6))
            )).equals(List.of(1, 2, 3, 4, 5, 6)),
            "Two-list merge failed"
        );

        check(
            toList(removeNthFromEnd(fromList(List.of(1, 2, 3, 4, 5)), 2))
                .equals(List.of(1, 2, 3, 5)),
            "Removal failed"
        );
        expectIllegalArgument(
            () -> removeNthFromEnd(fromList(List.of(1)), 2)
        );

        Node shared = fromList(List.of(8, 9));
        Node first = new Node(1);
        first.next = shared;
        Node second = new Node(2);
        second.next = shared;
        check(intersectionNode(first, second) == shared,
            "Intersection must use identity");
        check(intersectionNode(fromList(List.of(1)),
            fromList(List.of(1))) == null, "Equal values are not intersection");

        Node palindrome = fromList(List.of(1, 2, 3, 2, 1));
        check(isPalindrome(palindrome), "Palindrome check failed");
        check(toList(palindrome).equals(List.of(1, 2, 3, 2, 1)),
            "Palindrome check failed to restore links");
        check(!isPalindrome(fromList(List.of(1, 2, 3))),
            "Non-palindrome incorrectly accepted");

        check(
            toList(reorder(fromList(List.of(1, 2, 3, 4, 5))))
                .equals(List.of(1, 5, 2, 4, 3)),
            "Reorder failed"
        );

        check(
            toList(mergeKSorted(List.of(
                fromList(List.of(1, 4, 7)),
                fromList(List.of(2, 5, 8)),
                fromList(List.of(3, 6, 9)),
                null
            ))).equals(List.of(1, 2, 3, 4, 5, 6, 7, 8, 9)),
            "K-list merge failed"
        );

        expectIllegalArgument(() -> mergeKSorted(List.of(shared, shared)));

        System.out.println("Reverse: " + toList(reverse(fromList(
            List.of(10, 20, 30, 40)
        ))));
        System.out.println("Reordered: " + toList(reorder(fromList(
            List.of(1, 2, 3, 4, 5)
        ))));
        System.out.println("All linked-list assessment checks passed.");
    }
}
