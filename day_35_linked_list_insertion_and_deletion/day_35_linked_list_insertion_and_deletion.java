import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * Enterprise-oriented linked-list workflow.
 *
 * The domain models an ordered approval queue.  Each node contains a
 * workflow item, while the LinkedApprovalQueue controls legal insertion
 * and deletion operations.
 *
 * Positions are zero-based.
 */
public class LinkedListInsertionDeletion {

    enum Priority {
        LOW,
        NORMAL,
        HIGH,
        CRITICAL
    }

    record ApprovalRequest(
            String requestId,
            String repository,
            Priority priority
    ) {
        ApprovalRequest {
            if (requestId == null || requestId.isBlank()) {
                throw new IllegalArgumentException("requestId is required");
            }
            if (repository == null || repository.isBlank()) {
                throw new IllegalArgumentException("repository is required");
            }
            Objects.requireNonNull(priority, "priority is required");
        }

        @Override
        public String toString() {
            return requestId + "@" + repository + "[" + priority + "]";
        }
    }

    static final class LinkedApprovalQueue {

        private static final class Node {
            private final ApprovalRequest request;
            private Node next;

            private Node(ApprovalRequest request) {
                this.request = request;
            }
        }

        private Node head;
        private int size;

        private void validateInsertPosition(int position) {
            if (position < 0 || position > size) {
                throw new IndexOutOfBoundsException(
                        "Insertion position must be between 0 and " + size
                );
            }
        }

        private void validateDeletePosition(int position) {
            if (position < 0 || position >= size) {
                throw new IndexOutOfBoundsException(
                        "Deletion position must be between 0 and " + (size - 1)
                );
            }
        }

        int size() {
            return size;
        }

        boolean isEmpty() {
            return head == null;
        }

        /*
         * The new node becomes the head and keeps the previous head as
         * its successor.  No traversal is necessary.
         */
        void insertAtBeginning(ApprovalRequest request) {
            Node node = new Node(Objects.requireNonNull(request));
            node.next = head;
            head = node;
            size++;
        }

        /*
         * This implementation intentionally has no tail field so the
         * mechanics of reaching the final node remain visible.
         */
        void insertAtEnd(ApprovalRequest request) {
            Node node = new Node(Objects.requireNonNull(request));

            if (head == null) {
                head = node;
                size++;
                return;
            }

            Node current = head;
            while (current.next != null) {
                current = current.next;
            }

            current.next = node;
            size++;
        }

        void insertAtPosition(int position, ApprovalRequest request) {
            validateInsertPosition(position);

            if (position == 0) {
                insertAtBeginning(request);
                return;
            }

            if (position == size) {
                insertAtEnd(request);
                return;
            }

            Node previous = head;

            for (int i = 1; i < position; i++) {
                previous = previous.next;
            }

            Node node = new Node(Objects.requireNonNull(request));
            node.next = previous.next;
            previous.next = node;
            size++;
        }

        ApprovalRequest deleteFirst() {
            if (head == null) {
                throw new IllegalStateException(
                        "Cannot delete the first item from an empty queue"
                );
            }

            ApprovalRequest removed = head.request;
            head = head.next;
            size--;

            return removed;
        }

        ApprovalRequest deleteLast() {
            if (head == null) {
                throw new IllegalStateException(
                        "Cannot delete the last item from an empty queue"
                );
            }

            if (head.next == null) {
                return deleteFirst();
            }

            Node previous = head;

            while (previous.next != null && previous.next.next != null) {
                previous = previous.next;
            }

            ApprovalRequest removed = previous.next.request;
            previous.next = null;
            size--;

            return removed;
        }

        /*
         * Equality is based on the immutable requestId.  This avoids
         * accidentally deleting a different request that happens to
         * contain similar descriptive data.
         */
        Optional<ApprovalRequest> deleteByRequestId(String requestId) {
            if (requestId == null || requestId.isBlank() || head == null) {
                return Optional.empty();
            }

            if (head.request.requestId().equals(requestId)) {
                return Optional.of(deleteFirst());
            }

            Node previous = head;

            while (previous.next != null) {
                if (previous.next.request.requestId().equals(requestId)) {
                    ApprovalRequest removed = previous.next.request;
                    previous.next = previous.next.next;
                    size--;

                    return Optional.of(removed);
                }

                previous = previous.next;
            }

            return Optional.empty();
        }

        ApprovalRequest deleteAtPosition(int position) {
            validateDeletePosition(position);

            if (position == 0) {
                return deleteFirst();
            }

            Node previous = head;

            for (int i = 1; i < position; i++) {
                previous = previous.next;
            }

            ApprovalRequest removed = previous.next.request;
            previous.next = previous.next.next;
            size--;

            return removed;
        }

        Optional<Integer> findPosition(String requestId) {
            if (requestId == null) {
                return Optional.empty();
            }

            Node current = head;
            int position = 0;

            while (current != null) {
                if (current.request.requestId().equals(requestId)) {
                    return Optional.of(position);
                }

                current = current.next;
                position++;
            }

            return Optional.empty();
        }

        List<ApprovalRequest> snapshot() {
            List<ApprovalRequest> requests = new ArrayList<>();
            Node current = head;

            while (current != null) {
                requests.add(current.request);
                current = current.next;
            }

            return List.copyOf(requests);
        }

        /*
         * The invariant is that size equals the number of reachable nodes
         * and the list must not contain a cycle.
         */
        void validateInvariant() {
            Node slow = head;
            Node fast = head;

            while (fast != null && fast.next != null) {
                slow = slow.next;
                fast = fast.next.next;

                if (slow == fast) {
                    throw new IllegalStateException("Linked-list cycle detected");
                }
            }

            int counted = 0;
            Node current = head;

            while (current != null) {
                counted++;
                current = current.next;
            }

            if (counted != size) {
                throw new IllegalStateException(
                        "List size invariant violated: expected "
                                + size + ", counted " + counted
                );
            }
        }
    }

    private static ApprovalRequest request(
            String id,
            String repository,
            Priority priority
    ) {
        return new ApprovalRequest(id, repository, priority);
    }

    private static void show(
            String operation,
            LinkedApprovalQueue queue
    ) {
        queue.validateInvariant();
        System.out.printf(
                "%-35s %s%n",
                operation,
                queue.snapshot()
        );
    }

    private static void demonstrateWorkflow() {
        System.out.println("=== Approval queue insertion/deletion ===");

        LinkedApprovalQueue queue = new LinkedApprovalQueue();
        show("initial", queue);

        queue.insertAtBeginning(
                request("REQ-100", "payments-api", Priority.CRITICAL)
        );
        show("insertAtBeginning REQ-100", queue);

        queue.insertAtEnd(
                request("REQ-103", "analytics-api", Priority.NORMAL)
        );
        show("insertAtEnd REQ-103", queue);

        queue.insertAtPosition(
                1,
                request("REQ-101", "identity-api", Priority.HIGH)
        );
        show("insertAtPosition 1 REQ-101", queue);

        queue.insertAtPosition(
                2,
                request("REQ-102", "billing-api", Priority.HIGH)
        );
        show("insertAtPosition 2 REQ-102", queue);

        ApprovalRequest first = queue.deleteFirst();
        System.out.println("deleteFirst -> " + first);

        ApprovalRequest last = queue.deleteLast();
        System.out.println("deleteLast -> " + last);

        queue.insertAtEnd(
                request("REQ-104", "search-api", Priority.LOW)
        );

        Optional<ApprovalRequest> byId = queue.deleteByRequestId("REQ-102");
        System.out.println("deleteByRequestId REQ-102 -> " + byId);

        ApprovalRequest byPosition = queue.deleteAtPosition(0);
        System.out.println("deleteAtPosition 0 -> " + byPosition);

        show("final queue", queue);
    }

    private static void demonstrateBoundaries() {
        System.out.println("\n=== Boundary and failure behavior ===");

        LinkedApprovalQueue queue = new LinkedApprovalQueue();

        try {
            queue.deleteFirst();
        } catch (IllegalStateException error) {
            System.out.println("Expected empty-list error: " + error.getMessage());
        }

        try {
            queue.insertAtPosition(1, request(
                    "REQ-X",
                    "test-api",
                    Priority.NORMAL
            ));
        } catch (IndexOutOfBoundsException error) {
            System.out.println("Expected invalid insertion: " + error.getMessage());
        }

        queue.insertAtBeginning(
                request("REQ-200", "orders-api", Priority.NORMAL)
        );

        try {
            queue.deleteAtPosition(1);
        } catch (IndexOutOfBoundsException error) {
            System.out.println("Expected invalid deletion: " + error.getMessage());
        }

        Optional<ApprovalRequest> missing =
                queue.deleteByRequestId("REQ-NOT-FOUND");

        System.out.println("Missing-value deletion -> " + missing);
        queue.validateInvariant();
    }

    private static void demonstrateComplexity() {
        System.out.println("\n=== Complexity characteristics ===");
        System.out.println("Beginning insertion: O(1)");
        System.out.println("End insertion:       O(n) without a tail reference");
        System.out.println("Position insertion:  O(n) worst case");
        System.out.println("First deletion:      O(1)");
        System.out.println("Last deletion:       O(n)");
        System.out.println("Delete by ID:        O(n)");
        System.out.println("Position deletion:   O(n) worst case");
        System.out.println(
                "The list uses O(n) node memory; each node stores one payload "
                        + "and one successor reference."
        );
    }

    public static void main(String[] args) {
        demonstrateWorkflow();
        demonstrateBoundaries();
        demonstrateComplexity();
    }
}
