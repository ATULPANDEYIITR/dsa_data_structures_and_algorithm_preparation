import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * Enterprise assessment engine for bounded work queues, expression
 * validation, and monotonic-stack diagnostics.
 *
 * Compile: javac StackQueueAssessment.java
 * Run:     java StackQueueAssessment
 */
public class StackQueueAssessment {

    enum WorkState {
        SUBMITTED, QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED
    }

    enum Priority {
        NORMAL, HIGH, CRITICAL
    }

    record WorkItem(String id, String description, Priority priority) {
        WorkItem {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Work ID is required");
            }
            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException("Description is required");
            }
            Objects.requireNonNull(priority, "Priority is required");
        }
    }

    static final class WorkRecord {
        private final WorkItem item;
        private WorkState state = WorkState.SUBMITTED;
        private int attempts;

        WorkRecord(WorkItem item) {
            this.item = item;
        }

        WorkItem item() {
            return item;
        }

        WorkState state() {
            return state;
        }

        int attempts() {
            return attempts;
        }

        void transition(WorkState next) {
            Set<WorkState> allowed = switch (state) {
                case SUBMITTED -> EnumSet.of(WorkState.QUEUED, WorkState.CANCELLED);
                case QUEUED -> EnumSet.of(WorkState.RUNNING, WorkState.CANCELLED);
                case RUNNING -> EnumSet.of(WorkState.SUCCEEDED, WorkState.FAILED);
                case FAILED -> EnumSet.of(WorkState.QUEUED, WorkState.CANCELLED);
                case SUCCEEDED, CANCELLED -> EnumSet.noneOf(WorkState.class);
            };

            if (!allowed.contains(next)) {
                throw new IllegalStateException(
                    "Illegal work transition: " + state + " -> " + next
                );
            }

            if (next == WorkState.RUNNING) {
                attempts++;
            }
            state = next;
        }
    }

    static final class WorkQueue {
        private final int capacity;
        private final Deque<String> pending = new ArrayDeque<>();
        private final Map<String, WorkRecord> records = new HashMap<>();

        WorkQueue(int capacity) {
            if (capacity <= 0) {
                throw new IllegalArgumentException("Capacity must be positive");
            }
            this.capacity = capacity;
        }

        void submit(WorkItem item) {
            Objects.requireNonNull(item);
            if (records.containsKey(item.id())) {
                throw new IllegalArgumentException("Duplicate work ID");
            }
            if (pending.size() >= capacity) {
                throw new IllegalStateException("Queue capacity reached");
            }

            WorkRecord record = new WorkRecord(item);
            record.transition(WorkState.QUEUED);
            records.put(item.id(), record);
            pending.addLast(item.id());
        }

        WorkRecord dispatch() {
            String id = pending.pollFirst();
            if (id == null) {
                throw new IllegalStateException("No queued work is available");
            }

            WorkRecord record = records.get(id);
            record.transition(WorkState.RUNNING);
            return record;
        }

        void finish(String id, boolean succeeded) {
            WorkRecord record = records.get(id);
            if (record == null) {
                throw new IllegalArgumentException("Unknown work ID: " + id);
            }

            record.transition(succeeded ? WorkState.SUCCEEDED : WorkState.FAILED);
        }

        void retry(String id) {
            WorkRecord record = records.get(id);
            if (record == null) {
                throw new IllegalArgumentException("Unknown work ID: " + id);
            }
            if (pending.size() >= capacity) {
                throw new IllegalStateException("Queue capacity reached");
            }

            record.transition(WorkState.QUEUED);
            pending.addLast(id);
        }

        List<WorkRecord> records() {
            return List.copyOf(records.values());
        }
    }

    static boolean hasBalancedDelimiters(String input) {
        Objects.requireNonNull(input, "Input is required");

        Deque<Character> opening = new ArrayDeque<>();
        Map<Character, Character> pairs = Map.of(
            ')', '(', ']', '[', '}', '{'
        );

        for (char character : input.toCharArray()) {
            if (character == '(' || character == '[' || character == '{') {
                opening.push(character);
            } else if (pairs.containsKey(character)) {
                if (opening.isEmpty() || opening.pop() != pairs.get(character)) {
                    return false;
                }
            }
        }

        return opening.isEmpty();
    }

    static int[] nextGreaterValues(int[] values) {
        int[] result = new int[values.length];
        java.util.Arrays.fill(result, -1);
        Deque<Integer> unresolved = new ArrayDeque<>();

        for (int index = 0; index < values.length; index++) {
            while (!unresolved.isEmpty()
                    && values[unresolved.peek()] < values[index]) {
                result[unresolved.pop()] = values[index];
            }
            unresolved.push(index);
        }

        return result;
    }

    static int[] slidingWindowMaximum(int[] values, int width) {
        if (width < 1 || width > values.length) {
            throw new IllegalArgumentException("Invalid window width");
        }

        int[] result = new int[values.length - width + 1];
        Deque<Integer> candidates = new ArrayDeque<>();

        for (int index = 0; index < values.length; index++) {
            while (!candidates.isEmpty()
                    && candidates.peekFirst() <= index - width) {
                candidates.removeFirst();
            }

            while (!candidates.isEmpty()
                    && values[candidates.peekLast()] <= values[index]) {
                candidates.removeLast();
            }

            candidates.addLast(index);

            if (index >= width - 1) {
                result[index - width + 1] = values[candidates.peekFirst()];
            }
        }

        return result;
    }

    static int evaluatePostfix(List<String> tokens) {
        Deque<Integer> operands = new ArrayDeque<>();

        for (String token : tokens) {
            if (!Set.of("+", "-", "*", "/").contains(token)) {
                try {
                    operands.push(Integer.parseInt(token));
                } catch (NumberFormatException exception) {
                    throw new IllegalArgumentException(
                        "Invalid integer operand: " + token, exception
                    );
                }
                continue;
            }

            if (operands.size() < 2) {
                throw new IllegalArgumentException("Insufficient operands");
            }

            int right = operands.pop();
            int left = operands.pop();

            int result = switch (token) {
                case "+" -> Math.addExact(left, right);
                case "-" -> Math.subtractExact(left, right);
                case "*" -> Math.multiplyExact(left, right);
                case "/" -> {
                    if (right == 0) {
                        throw new ArithmeticException("Division by zero");
                    }
                    if (left == Integer.MIN_VALUE && right == -1) {
                        throw new ArithmeticException("Integer overflow");
                    }
                    yield left / right;
                }
                default -> throw new IllegalArgumentException("Unknown operator");
            };

            operands.push(result);
        }

        if (operands.size() != 1) {
            throw new IllegalArgumentException(
                "Expression must leave exactly one result"
            );
        }

        return operands.pop();
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) {
        WorkQueue queue = new WorkQueue(3);
        queue.submit(new WorkItem("BUILD-41", "Compile release candidate", Priority.HIGH));
        queue.submit(new WorkItem("TEST-41", "Execute regression suite", Priority.CRITICAL));

        WorkRecord build = queue.dispatch();
        queue.finish(build.item().id(), true);

        WorkRecord tests = queue.dispatch();
        queue.finish(tests.item().id(), false);
        queue.retry(tests.item().id());

        WorkRecord retried = queue.dispatch();
        queue.finish(retried.item().id(), true);

        for (WorkRecord record : queue.records()) {
            System.out.printf(
                "%s | %s | attempts=%d%n",
                record.item().id(),
                record.state(),
                record.attempts()
            );
        }

        require(hasBalancedDelimiters("{[()]}"), "Valid delimiters rejected");
        require(!hasBalancedDelimiters("([)]"), "Invalid delimiters accepted");
        require(
            java.util.Arrays.equals(
                nextGreaterValues(new int[]{2, 1, 2, 4, 3}),
                new int[]{4, 2, 4, -1, -1}
            ),
            "Next-greater evaluation failed"
        );
        require(
            java.util.Arrays.equals(
                slidingWindowMaximum(new int[]{1, 3, -1, -3, 5, 3, 6, 7}, 3),
                new int[]{3, 3, 5, 5, 6, 7}
            ),
            "Window maximum evaluation failed"
        );
        require(
            evaluatePostfix(List.of("12", "3", "/", "4", "+")) == 8,
            "Postfix evaluation failed"
        );

        try {
            queue.finish("BUILD-41", true);
            throw new AssertionError("Illegal terminal transition was accepted");
        } catch (IllegalStateException expected) {
            System.out.println("Illegal transition rejected correctly");
        }

        try {
            evaluatePostfix(List.of("9", "0", "/"));
            throw new AssertionError("Division by zero was accepted");
        } catch (ArithmeticException expected) {
            System.out.println("Division by zero rejected correctly");
        }

        System.out.println("All Java assessment cases passed.");
    }
}
