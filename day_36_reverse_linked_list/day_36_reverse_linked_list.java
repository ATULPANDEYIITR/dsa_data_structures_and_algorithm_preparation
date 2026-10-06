import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class LinkedListReversal {

    private static final class Node {
        private final int value;
        private Node next;

        private Node(int value) {
            this.value = value;
        }
    }

    private static final class SinglyLinkedList {
        private Node head;
        private Node tail;
        private int size;

        void add(int value) {
            Node node = new Node(value);

            if (head == null) {
                head = node;
                tail = node;
            } else {
                tail.next = node;
                tail = node;
            }

            size++;
        }

        int size() {
            return size;
        }

        List<Integer> values() {
            List<Integer> result = new ArrayList<>(size);
            Node current = head;

            while (current != null) {
                result.add(current.value);
                current = current.next;
            }

            return result;
        }

        String display() {
            if (head == null) {
                return "EMPTY";
            }

            StringBuilder result = new StringBuilder();
            Node current = head;

            while (current != null) {
                if (result.length() > 0) {
                    result.append(" -> ");
                }

                result.append(current.value);
                current = current.next;
            }

            return result.toString();
        }

        /*
         * Three references are sufficient:
         * previous is the reversed prefix, current is the active node, and
         * following preserves the unreversed suffix before current.next is
         * redirected.
         */
        void reverseIterative() {
            Node previous = null;
            Node current = head;
            Node oldHead = head;

            while (current != null) {
                Node following = current.next;
                current.next = previous;
                previous = current;
                current = following;
            }

            head = previous;
            tail = oldHead;
        }

        void reverseRecursive() {
            Node oldHead = head;
            head = reverse(head);
            tail = oldHead;
        }

        /*
         * The base case identifies the new head. During stack unwinding,
         * successor.next is redirected to the current node and current.next
         * is cleared so the old forward edge cannot form a cycle.
         */
        private Node reverse(Node current) {
            if (current == null || current.next == null) {
                return current;
            }

            Node newHead = reverse(current.next);

            current.next.next = current;
            current.next = null;

            return newHead;
        }

        boolean isValid() {
            if (size == 0) {
                return head == null && tail == null;
            }

            if (head == null || tail == null || tail.next != null) {
                return false;
            }

            int count = 0;
            Node current = head;

            while (current != null) {
                count++;
                current = current.next;

                if (count > size) {
                    return false;
                }
            }

            return count == size;
        }
    }

    /*
     * A domain-level service makes the reversal policy explicit. The
     * production choice here favors iteration when input can be large because
     * recursion consumes stack frames proportional to list length.
     */
    private static final class ReversalService {
        static void reverse(SinglyLinkedList list, boolean recursive) {
            Objects.requireNonNull(list, "list must not be null");

            if (recursive) {
                list.reverseRecursive();
            } else {
                list.reverseIterative();
            }

            if (!list.isValid()) {
                throw new IllegalStateException(
                    "Linked-list invariant violated after reversal."
                );
            }
        }
    }

    private static void demonstrateWorkflow() {
        System.out.println("LINKED-LIST REVERSAL");
        System.out.println("====================");

        SinglyLinkedList list = new SinglyLinkedList();

        for (int value : List.of(100, 200, 300, 400, 500)) {
            list.add(value);
        }

        System.out.println("Original: " + list.display());

        ReversalService.reverse(list, false);
        System.out.println("Iterative: " + list.display());

        ReversalService.reverse(list, true);
        System.out.println("Recursive: " + list.display());

        System.out.println("Size: " + list.size());
        System.out.println("Valid: " + list.isValid());
        System.out.println();
    }

    private static void demonstrateEdgeCases() {
        System.out.println("EDGE CASES");
        System.out.println("----------");

        SinglyLinkedList empty = new SinglyLinkedList();
        empty.reverseIterative();
        System.out.println("Empty list: " + empty.display());

        SinglyLinkedList single = new SinglyLinkedList();
        single.add(42);
        single.reverseRecursive();
        System.out.println("Single node: " + single.display());

        SinglyLinkedList pair = new SinglyLinkedList();
        pair.add(1);
        pair.add(2);
        pair.reverseIterative();
        System.out.println("Two nodes: " + pair.display());

        System.out.println();
    }

    private static void demonstrateRecursiveState() {
        System.out.println("RECURSIVE STATE TRANSITION");
        System.out.println("==========================");

        SinglyLinkedList list = new SinglyLinkedList();

        for (int value : List.of(10, 20, 30)) {
            list.add(value);
        }

        System.out.println("Before: " + list.display());

        list.reverseRecursive();

        System.out.println("After:  " + list.display());
        System.out.println(
            "The original tail becomes the new head, and links are redirected "
                + "during recursive stack unwinding."
        );
        System.out.println();
    }

    private static void verifyRoundTrip() {
        SinglyLinkedList list = new SinglyLinkedList();

        for (int value : List.of(5, 10, 15, 20, 25)) {
            list.add(value);
        }

        List<Integer> original = list.values();

        list.reverseIterative();

        List<Integer> reversed = list.values();
        List<Integer> expectedReversed = new ArrayList<>(original);
        java.util.Collections.reverse(expectedReversed);

        if (!reversed.equals(expectedReversed)) {
            throw new AssertionError("Iterative reversal invariant failed.");
        }

        list.reverseRecursive();

        if (!list.values().equals(original)) {
            throw new AssertionError(
                "Recursive reversal did not restore original ordering."
            );
        }

        if (!list.isValid()) {
            throw new AssertionError("List metadata invariant failed.");
        }

        System.out.println("Round-trip verification passed.");
        System.out.println();
    }

    private static void explainComplexity() {
        System.out.println("COMPLEXITY");
        System.out.println("----------");
        System.out.println("Iterative reversal: O(n) time, O(1) auxiliary space.");
        System.out.println("Recursive reversal:  O(n) time, O(n) call-stack space.");
        System.out.println(
            "For production workloads with potentially large lists, the "
                + "iterative method avoids recursion-depth failures."
        );
    }

    public static void main(String[] args) {
        demonstrateWorkflow();
        demonstrateEdgeCases();
        demonstrateRecursiveState();
        verifyRoundTrip();
        explainComplexity();
    }
}
