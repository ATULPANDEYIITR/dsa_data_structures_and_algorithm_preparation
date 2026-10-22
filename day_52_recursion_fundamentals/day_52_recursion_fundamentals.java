import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Supplier;

public class RecursionFundamentals {

    public record CallFrame(String function, String state, int depth) {
        public CallFrame {
            Objects.requireNonNull(function, "function");
            Objects.requireNonNull(state, "state");
            if (depth < 0) {
                throw new IllegalArgumentException("depth must be non-negative");
            }
        }
    }

    public record CalculationResult(String operation, BigInteger value) {
        public CalculationResult {
            Objects.requireNonNull(operation, "operation");
            Objects.requireNonNull(value, "value");
        }
    }

    public interface RecursiveOperation<T> {
        T execute();
    }

    public enum CalculationStatus {
        SUCCESS,
        REJECTED
    }

    public record CalculationOutcome(
            CalculationStatus status, String message, BigInteger value) {
        public CalculationOutcome {
            Objects.requireNonNull(status, "status");
            Objects.requireNonNull(message, "message");
            if (status == CalculationStatus.SUCCESS && value == null) {
                throw new IllegalArgumentException("Successful result needs a value");
            }
        }
    }

    private static final int MAX_DEPTH = 900;

    public static BigInteger factorial(int n) {
        validateNonNegative(n, "n");
        if (n > MAX_DEPTH) {
            throw new IllegalArgumentException("n exceeds the recursion limit");
        }
        if (n <= 1) return BigInteger.ONE;
        return BigInteger.valueOf(n).multiply(factorial(n - 1));
    }

    public static BigInteger fibonacci(int n) {
        validateNonNegative(n, "n");
        if (n > MAX_DEPTH) {
            throw new IllegalArgumentException("n exceeds the recursion limit");
        }
        return fibonacciMemo(n, new HashMap<>());
    }

    private static BigInteger fibonacciMemo(
            int n, Map<Integer, BigInteger> memo) {
        if (n <= 1) return BigInteger.valueOf(n);
        BigInteger cached = memo.get(n);
        if (cached != null) return cached;

        BigInteger result = fibonacciMemo(n - 1, memo)
                .add(fibonacciMemo(n - 2, memo));
        memo.put(n, result);
        return result;
    }

    public static BigInteger power(BigInteger base, int exponent) {
        Objects.requireNonNull(base, "base");
        validateNonNegative(exponent, "exponent");
        if (exponent == 0) return BigInteger.ONE;

        BigInteger half = power(base, exponent / 2);
        BigInteger squared = half.multiply(half);
        return exponent % 2 == 0 ? squared : base.multiply(squared);
    }

    public static BigInteger sumTo(int n) {
        validateNonNegative(n, "n");
        if (n > MAX_DEPTH) {
            throw new IllegalArgumentException("n exceeds the recursion limit");
        }
        if (n == 0) return BigInteger.ZERO;
        return BigInteger.valueOf(n).add(sumTo(n - 1));
    }

    public static String reverseString(String value) {
        Objects.requireNonNull(value, "value");
        int[] codePoints = value.codePoints().toArray();
        StringBuilder result = new StringBuilder();
        reverseCodePoints(codePoints, 0, result);
        return result.toString();
    }

    private static void reverseCodePoints(
            int[] codePoints, int index, StringBuilder result) {
        if (index == codePoints.length) return;
        reverseCodePoints(codePoints, index + 1, result);
        result.appendCodePoint(codePoints[index]);
    }

    public static List<Integer> reverseList(List<Integer> values) {
        Objects.requireNonNull(values, "values");
        List<Integer> copy = new ArrayList<>(values);
        reverseRange(copy, 0, copy.size() - 1);
        return Collections.unmodifiableList(copy);
    }

    private static void reverseRange(
            List<Integer> values, int left, int right) {
        if (left >= right) return;
        Collections.swap(values, left, right);
        reverseRange(values, left + 1, right - 1);
    }

    public static BigInteger sumArray(List<Integer> values, int index) {
        Objects.requireNonNull(values, "values");
        if (index < 0 || index > values.size()) {
            throw new IndexOutOfBoundsException("index is outside the list");
        }
        if (index == values.size()) return BigInteger.ZERO;
        Integer element = Objects.requireNonNull(values.get(index), "array element");
        return BigInteger.valueOf(element).add(sumArray(values, index + 1));
    }

    public static int binarySearch(List<Integer> values, int target) {
        Objects.requireNonNull(values, "values");
        for (int i = 1; i < values.size(); i++) {
            if (values.get(i - 1) > values.get(i)) {
                throw new IllegalArgumentException("Input must be sorted");
            }
        }
        return binarySearchRange(values, target, 0, values.size() - 1);
    }

    private static int binarySearchRange(
            List<Integer> values, int target, int left, int right) {
        if (left > right) return -1;
        int middle = left + (right - left) / 2;
        int value = Objects.requireNonNull(values.get(middle), "array element");
        if (value == target) return middle;
        if (target < value) {
            return binarySearchRange(values, target, left, middle - 1);
        }
        return binarySearchRange(values, target, middle + 1, right);
    }

    public static List<CallFrame> factorialTrace(int n) {
        validateNonNegative(n, "n");
        List<CallFrame> frames = new ArrayList<>();
        traceFactorial(n, 0, frames);
        return Collections.unmodifiableList(frames);
    }

    private static void traceFactorial(
            int n, int depth, List<CallFrame> frames) {
        frames.add(new CallFrame("factorial", "n=" + n, depth));
        if (n > 1) traceFactorial(n - 1, depth + 1, frames);
    }

    public static CalculationOutcome evaluate(
            String operation, Supplier<BigInteger> calculation) {
        Objects.requireNonNull(operation, "operation");
        Objects.requireNonNull(calculation, "calculation");
        try {
            return new CalculationOutcome(
                    CalculationStatus.SUCCESS,
                    operation + " completed",
                    Objects.requireNonNull(calculation.get(), "calculation result"));
        } catch (IllegalArgumentException | IndexOutOfBoundsException error) {
            return new CalculationOutcome(
                    CalculationStatus.REJECTED, error.getMessage(), null);
        }
    }

    private static void validateNonNegative(int n, String name) {
        if (n < 0) throw new IllegalArgumentException(name + " must be non-negative");
    }

    private static void runTests() {
        if (!factorial(0).equals(BigInteger.ONE)
                || !factorial(5).equals(BigInteger.valueOf(120))) {
            throw new AssertionError("Factorial test failed");
        }
        if (!fibonacci(10).equals(BigInteger.valueOf(55))) {
            throw new AssertionError("Fibonacci test failed");
        }
        if (!power(BigInteger.TWO, 10).equals(BigInteger.valueOf(1024))) {
            throw new AssertionError("Power test failed");
        }
        if (!sumTo(10).equals(BigInteger.valueOf(55))) {
            throw new AssertionError("Sum test failed");
        }
        if (!reverseString("recursion").equals("noisrucer")) {
            throw new AssertionError("String reversal test failed");
        }
        if (!reverseList(List.of(1, 2, 3)).equals(List.of(3, 2, 1))) {
            throw new AssertionError("List reversal test failed");
        }
        if (!sumArray(List.of(2, 4, 6), 0).equals(BigInteger.valueOf(12))) {
            throw new AssertionError("Array sum test failed");
        }
        if (binarySearch(List.of(1, 3, 5, 7), 5) != 2
                || binarySearch(List.of(), 5) != -1) {
            throw new AssertionError("Binary search test failed");
        }
        if (factorialTrace(4).size() != 3) {
            throw new AssertionError("Trace test failed");
        }

        CalculationOutcome rejected = evaluate(
                "factorial", () -> factorial(-1));
        if (rejected.status() != CalculationStatus.REJECTED) {
            throw new AssertionError("Invalid input was accepted");
        }
        System.out.println("All Java recursion tests passed.");
    }

    public static void main(String[] args) {
        runTests();

        List<CalculationResult> results = List.of(
                new CalculationResult("factorial(5)", factorial(5)),
                new CalculationResult("fibonacci(10)", fibonacci(10)),
                new CalculationResult("power(2, 10)", power(BigInteger.TWO, 10)),
                new CalculationResult("sumTo(10)", sumTo(10))
        );

        results.stream()
                .map(result -> result.operation() + " = " + result.value())
                .forEach(System.out::println);

        System.out.println("Reversed text: " + reverseString("recursion"));
        System.out.println("Reversed list: " + reverseList(List.of(7, 2, 9, 4, 1)));
        System.out.println("Array sum: " + sumArray(List.of(7, 2, 9, 4, 1), 0));

        System.out.println("Factorial call stack:");
        factorialTrace(4).forEach(frame ->
                System.out.println("  ".repeat(frame.depth())
                        + frame.function() + "(" + frame.state() + ")"));

        CalculationOutcome invalid = evaluate("factorial", () -> factorial(-3));
        System.out.println("Invalid calculation: " + invalid.status()
                + " - " + invalid.message());
    }
}
