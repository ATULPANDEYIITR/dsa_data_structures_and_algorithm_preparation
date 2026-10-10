import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Objects;

/**
 * Stack fundamentals in an enterprise document-approval workflow.
 *
 * Compile: javac StackFundamentals.java
 * Run:     java StackFundamentals
 */
public class StackFundamentals {

    public static final class StackUnderflowException
            extends NoSuchElementException {
        public StackUnderflowException(String message) {
            super(message);
        }
    }

    public static final class StackOverflowException
            extends IllegalStateException {
        public StackOverflowException(String message) {
            super(message);
        }
    }

    public interface Stack<T> extends Iterable<T> {
        void push(T value);
        T pop();
        T peek();
        boolean isEmpty();
        int size();
    }

    /**
     * The final ArrayList element is the stack top.
     * ArrayList resizing can occasionally cost O(n), making push amortized O(1).
     */
    public static final class ArrayStack<T> implements Stack<T> {
        private final List<T> elements;
        private final int capacity;

        public ArrayStack() {
            this(Integer.MAX_VALUE);
        }

        public ArrayStack(int capacity) {
            if (capacity < 0) {
                throw new IllegalArgumentException(
                        "Capacity must not be negative.");
            }
            this.capacity = capacity;
            this.elements = new ArrayList<>();
        }

        @Override
        public void push(T value) {
            if (elements.size() >= capacity) {
                throw new StackOverflowException(
                        "The configured stack capacity has been reached.");
            }
            elements.add(value);
        }

        @Override
        public T pop() {
            if (isEmpty()) {
                throw new StackUnderflowException(
                        "Cannot pop from an empty stack.");
            }
            return elements.remove(elements.size() - 1);
        }

        @Override
        public T peek() {
            if (isEmpty()) {
                throw new StackUnderflowException(
                        "Cannot peek at an empty stack.");
            }
            return elements.get(elements.size() - 1);
        }

        @Override
        public boolean isEmpty() {
            return elements.isEmpty();
        }

        @Override
        public int size() {
            return elements.size();
        }

        public List<T> snapshotBottomToTop() {
            return Collections.unmodifiableList(new ArrayList<>(elements));
        }

        @Override
        public Iterator<T> iterator() {
            List<T> snapshot = new ArrayList<>(elements);
            Collections.reverse(snapshot);
            return Collections.unmodifiableList(snapshot).iterator();
        }
    }

    private static final class Node<T> {
        private final T value;
        private Node<T> next;

        private Node(T value, Node<T> next) {
            this.value = value;
            this.next = next;
        }
    }

    /**
     * A singly linked list with its head as the stack top.
     * The size field prevents repeated list traversal for size queries.
     */
    public static final class LinkedStack<T> implements Stack<T> {
        private Node<T> top;
        private int size;

        @Override
        public void push(T value) {
            top = new Node<>(value, top);
            size++;
        }

        @Override
        public T pop() {
            if (isEmpty()) {
                throw new StackUnderflowException(
                        "Cannot pop from an empty stack.");
            }

            Node<T> removed = top;
            top = removed.next;
            removed.next = null;
            size--;
            return removed.value;
        }

        @Override
        public T peek() {
            if (isEmpty()) {
                throw new StackUnderflowException(
                        "Cannot peek at an empty stack.");
            }
            return top.value;
        }

        @Override
        public boolean isEmpty() {
            return size == 0;
        }

        @Override
        public int size() {
            return size;
        }

        @Override
        public Iterator<T> iterator() {
            // Capture the node chain at iterator creation for a stable
            // traversal. This is a shallow snapshot of element references.
            List<T> snapshot = new ArrayList<>(size);
            for (Node<T> node = top; node != null; node = node.next) {
                snapshot.add(node.value);
            }
            return Collections.unmodifiableList(snapshot).iterator();
        }
    }

    enum DocumentStatus {
        DRAFT,
        SUBMITTED,
        APPROVED,
        REJECTED
    }

    static final class DocumentVersion {
        private final int version;
        private final String content;
        private final String author;

        DocumentVersion(int version, String content, String author) {
            if (version < 1) {
                throw new IllegalArgumentException(
                        "Version number must be positive.");
            }
            this.content = Objects.requireNonNull(content, "content");
            this.author = Objects.requireNonNull(author, "author");
            if (author.isBlank()) {
                throw new IllegalArgumentException(
                        "Author must not be blank.");
            }
            this.version = version;
        }

        @Override
        public String toString() {
            return "v" + version + " by " + author + ": " + content;
        }
    }

    /**
     * Each edit is an immutable version. Reverting pops the latest version
     * and exposes the previous saved version.
     */
    static final class DocumentHistory {
        private final LinkedStack<DocumentVersion> versions =
                new LinkedStack<>();
        private int nextVersion = 1;

        DocumentHistory(String author, String initialContent) {
            save(author, initialContent);
        }

        void save(String author, String content) {
            versions.push(new DocumentVersion(
                    nextVersion++, content, author));
        }

        DocumentVersion current() {
            return versions.peek();
        }

        DocumentVersion revert() {
            if (versions.size() <= 1) {
                throw new StackUnderflowException(
                        "The original document version cannot be removed.");
            }
            versions.pop();
            return versions.peek();
        }

        int versionCount() {
            return versions.size();
        }
    }

    static final class ApprovalWorkflow {
        private final DocumentHistory history;
        private final ArrayStack<String> pendingActions =
                new ArrayStack<>(5);
        private DocumentStatus status = DocumentStatus.DRAFT;

        ApprovalWorkflow(DocumentHistory history) {
            this.history = Objects.requireNonNull(history, "history");
        }

        void submit(String reviewer) {
            if (status != DocumentStatus.DRAFT
                    && status != DocumentStatus.REJECTED) {
                throw new IllegalStateException(
                        "Only a draft or rejected document can be submitted.");
            }
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException(
                        "A reviewer must be specified.");
            }
            pendingActions.push("Review requested from " + reviewer);
            status = DocumentStatus.SUBMITTED;
        }

        String processLatestAction() {
            if (status != DocumentStatus.SUBMITTED) {
                throw new IllegalStateException(
                        "There is no submitted review workflow.");
            }
            return pendingActions.pop();
        }

        void approve() {
            if (status != DocumentStatus.SUBMITTED) {
                throw new IllegalStateException(
                        "Only a submitted document can be approved.");
            }
            status = DocumentStatus.APPROVED;
        }

        void reject() {
            if (status != DocumentStatus.SUBMITTED) {
                throw new IllegalStateException(
                        "Only a submitted document can be rejected.");
            }
            status = DocumentStatus.REJECTED;
        }

        DocumentStatus status() {
            return status;
        }

        int pendingActionCount() {
            return pendingActions.size();
        }

        DocumentHistory history() {
            return history;
        }
    }

    private static void verifyCoreOperations() {
        Stack<Integer> array = new ArrayStack<>();
        Stack<Integer> linked = new LinkedStack<>();

        for (Stack<Integer> stack : List.of(array, linked)) {
            stack.push(11);
            stack.push(22);
            stack.push(33);

            if (stack.peek() != 33 || stack.size() != 3) {
                throw new AssertionError("Push or peek failed.");
            }
            if (stack.pop() != 33 || stack.pop() != 22
                    || stack.pop() != 11 || !stack.isEmpty()) {
                throw new AssertionError("LIFO order failed.");
            }

            try {
                stack.pop();
                throw new AssertionError("Empty pop should fail.");
            } catch (StackUnderflowException expected) {
                // The expected failure confirms underflow is explicit.
            }
        }
    }

    public static void main(String[] args) {
        verifyCoreOperations();

        DocumentHistory history =
                new DocumentHistory("Analyst", "Initial procurement policy");
        history.save("Reviewer", "Clarified approval thresholds");
        history.save("Analyst", "Corrected supplier evaluation rules");

        System.out.println("Current version: " + history.current());
        System.out.println("Reverted to: " + history.revert());

        ApprovalWorkflow workflow = new ApprovalWorkflow(history);
        workflow.submit("Compliance Team");
        System.out.println(workflow.processLatestAction());
        workflow.approve();

        System.out.println("Document status: " + workflow.status());
        System.out.println("Remaining versions: " + history.versionCount());
        System.out.println("All stack checks passed.");
    }
}
