/*
 * Day 7 — Time Complexity
 *
 * A self-contained JavaScript study file covering:
 *   - Running time
 *   - Constant operations
 *   - Linear operations
 *   - Nested loops
 *   - Sequential operations
 *   - O(1), O(log n), O(n), O(n log n), O(n²), O(n³)
 *   - Halving and doubling loops
 *   - Searching
 *   - Sorting
 *   - Recursion
 *   - Best/worst cases
 *   - Space complexity
 *   - Timing experiments
 *   - Edge cases
 *
 * Run with:
 *   node day7_time_complexity.js
 */

"use strict";

// ============================================================================
// 1. DISPLAY HELPERS
// ============================================================================

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function formatNumber(value) {
    return new Intl.NumberFormat("en-US").format(value);
}

// ============================================================================
// 2. CONSTANT TIME
// ============================================================================

function constantOperation(value) {
    /*
     * O(1): only a fixed number of operations are performed regardless of n.
     *
     * Accessing an array element by index is treated as constant-time in
     * the normal random-access array model.
     */
    if (value.length === 0) {
        return undefined;
    }

    return value[0];
}

// ============================================================================
// 3. LINEAR TIME
// ============================================================================

function linearSum(numbers) {
    /*
     * O(n): every element is visited once.
     *
     * If n doubles, the number of loop iterations approximately doubles.
     */
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    return total;
}

// ============================================================================
// 4. QUADRATIC AND CUBIC TIME
// ============================================================================

function quadraticPairCount(numbers) {
    /*
     * O(n²): n outer iterations multiplied by n inner iterations.
     */
    let count = 0;

    for (let i = 0; i < numbers.length; i++) {
        for (let j = 0; j < numbers.length; j++) {
            count++;
        }
    }

    return count;
}

function triangularPairCount(numbers) {
    /*
     * O(n²), despite the decreasing inner-loop length.
     *
     * The work is:
     *   n + (n - 1) + ... + 1
     *   = n(n + 1) / 2
     *   = O(n²)
     */
    let count = 0;

    for (let i = 0; i < numbers.length; i++) {
        for (let j = i; j < numbers.length; j++) {
            count++;
        }
    }

    return count;
}

function cubicOperation(n) {
    /*
     * O(n³): three independently growing loops.
     */
    let count = 0;

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            for (let k = 0; k < n; k++) {
                count++;
            }
        }
    }

    return count;
}

// ============================================================================
// 5. LOGARITHMIC TIME
// ============================================================================

function halvingSteps(n) {
    /*
     * O(log n): the problem size is divided by two after every iteration.
     */
    if (n <= 1) {
        return 0;
    }

    let steps = 0;

    while (n > 1) {
        n = Math.floor(n / 2);
        steps++;
    }

    return steps;
}

function doublingSteps(n) {
    /*
     * O(log n): a control value doubles until it reaches n.
     */
    if (n <= 1) {
        return 0;
    }

    let value = 1;
    let steps = 0;

    while (value < n) {
        value *= 2;
        steps++;
    }

    return steps;
}

function binarySearch(sortedNumbers, target) {
    /*
     * Iterative binary search:
     *
     * Time:  O(log n)
     * Space: O(1)
     *
     * Requirement: the input must already be sorted.
     */
    let left = 0;
    let right = sortedNumbers.length - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);
        const middleValue = sortedNumbers[middle];

        if (middleValue === target) {
            return middle;
        }

        if (middleValue < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

// ============================================================================
// 6. N LOG N
// ============================================================================

function merge(left, right) {
    /*
     * Merging two sorted arrays takes O(n) relative to the combined
     * number of elements.
     */
    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    while (leftIndex < left.length && rightIndex < right.length) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push(left[leftIndex]);
            leftIndex++;
        } else {
            result.push(right[rightIndex]);
            rightIndex++;
        }
    }

    while (leftIndex < left.length) {
        result.push(left[leftIndex]);
        leftIndex++;
    }

    while (rightIndex < right.length) {
        result.push(right[rightIndex]);
        rightIndex++;
    }

    return result;
}

function mergeSort(numbers) {
    /*
     * Merge sort:
     *
     * Number of levels: O(log n)
     * Work per level:  O(n)
     * Total time:      O(n log n)
     *
     * This implementation creates arrays while dividing and merging, so its
     * auxiliary space is O(n).
     */
    if (numbers.length <= 1) {
        return [...numbers];
    }

    const middle = Math.floor(numbers.length / 2);
    const left = mergeSort(numbers.slice(0, middle));
    const right = mergeSort(numbers.slice(middle));

    return merge(left, right);
}

// ============================================================================
// 7. SEQUENTIAL WORK
// ============================================================================

function sequentialLinearWork(numbers) {
    /*
     * O(n) + O(n) = O(2n) = O(n).
     *
     * Sequential loops add their costs instead of multiplying them.
     */
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    for (const number of numbers) {
        total += number * 2;
    }

    return total;
}

function linearThenQuadratic(numbers) {
    /*
     * O(n) + O(n²) = O(n²).
     *
     * The quadratic term grows faster and dominates as n becomes large.
     */
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    for (const first of numbers) {
        for (const second of numbers) {
            total += first * second;
        }
    }

    return total;
}

// ============================================================================
// 8. N LOG N LOOP PATTERN
// ============================================================================

function nLogNWork(n) {
    /*
     * Outer loop: n times
     * Inner loop: approximately log2(n) times
     *
     * Total: O(n log n)
     */
    if (n <= 0) {
        return 0;
    }

    let count = 0;

    for (let i = 0; i < n; i++) {
        let value = n;

        while (value > 1) {
            value = Math.floor(value / 2);
            count++;
        }
    }

    return count;
}

// ============================================================================
// 9. RECURSION
// ============================================================================

function recursiveCountdown(n) {
    /*
     * One recursive call with n - 1:
     *
     * T(n) = T(n - 1) + O(1)
     * Therefore T(n) = O(n).
     *
     * JavaScript recursion also consumes call-stack space.
     */
    if (n <= 0) {
        return 0;
    }

    return 1 + recursiveCountdown(n - 1);
}

function recursiveBinarySearch(sortedNumbers, target, left = 0, right = null) {
    /*
     * O(log n) time.
     *
     * The recursive implementation has O(log n) call-stack space.
     */
    if (right === null) {
        right = sortedNumbers.length - 1;
    }

    if (left > right) {
        return -1;
    }

    const middle = Math.floor((left + right) / 2);

    if (sortedNumbers[middle] === target) {
        return middle;
    }

    if (sortedNumbers[middle] < target) {
        return recursiveBinarySearch(
            sortedNumbers,
            target,
            middle + 1,
            right
        );
    }

    return recursiveBinarySearch(
        sortedNumbers,
        target,
        left,
        middle - 1
    );
}

function naiveFibonacci(n) {
    /*
     * Exponential-time example.
     *
     * The same smaller Fibonacci values are calculated repeatedly.
     * This creates a rapidly growing recursion tree.
     */
    if (n <= 1) {
        return n;
    }

    return naiveFibonacci(n - 1) + naiveFibonacci(n - 2);
}

function dynamicFibonacci(n) {
    /*
     * O(n) time and O(1) additional space.
     *
     * Each Fibonacci value is calculated once.
     */
    if (n < 0) {
        throw new RangeError("n must be non-negative");
    }

    if (n <= 1) {
        return n;
    }

    let previous = 0;
    let current = 1;

    for (let i = 2; i <= n; i++) {
        const next = previous + current;
        previous = current;
        current = next;
    }

    return current;
}

// ============================================================================
// 10. LINEAR SEARCH
// ============================================================================

function linearSearch(numbers, target) {
    /*
     * Best case:  O(1)
     * Average:    O(n)
     * Worst case: O(n)
     *
     * If the target is the first element, only one comparison is needed.
     */
    for (let index = 0; index < numbers.length; index++) {
        if (numbers[index] === target) {
            return index;
        }
    }

    return -1;
}

// ============================================================================
// 11. OPERATION COUNT AND DOMINANT TERMS
// ============================================================================

function operationCountExample(n) {
    /*
     * The expression is:
     *
     *   3n² + 7n + 10
     *
     * Asymptotically:
     *   O(3n² + 7n + 10)
     *   = O(n²)
     */
    return 3 * n * n + 7 * n + 10;
}

function demonstrateDominantTerms() {
    console.log("Expression: 3n² + 7n + 10");

    for (const n of [1, 10, 100]) {
        console.log(`n=${n}: ${formatNumber(operationCountExample(n))}`);
    }

    console.log("Classification: O(n²)");
}

// ============================================================================
// 12. ARRAY ACCESS AND JAVASCRIPT-SPECIFIC CONSIDERATIONS
// ============================================================================

function arrayAccessExample(numbers) {
    /*
     * Index access is normally treated as O(1).
     *
     * This is different from scanning the entire array, which is O(n).
     */
    if (numbers.length === 0) {
        return undefined;
    }

    return numbers[Math.floor(numbers.length / 2)];
}

function arrayScanExample(numbers, target) {
    /*
     * Array scanning is O(n).
     */
    return linearSearch(numbers, target);
}

// ============================================================================
// 13. SPACE COMPLEXITY
// ============================================================================

function iterativeSum(numbers) {
    /*
     * Time: O(n)
     * Auxiliary space: O(1)
     */
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    return total;
}

function copiedSum(numbers) {
    /*
     * Time: O(n)
     * Auxiliary space: O(n)
     *
     * The spread operation creates another array.
     */
    const copy = [...numbers];
    return copy.reduce((sum, number) => sum + number, 0);
}

// ============================================================================
// 14. TIMING
// ============================================================================

function measureMilliseconds(functionToMeasure) {
    /*
     * performance.now() gives a high-resolution elapsed-time measurement
     * where supported by the current Node.js runtime.
     *
     * Timing is affected by the machine and runtime environment, so it is
     * evidence about one execution, not a mathematical complexity proof.
     */
    const start = performance.now();
    functionToMeasure();
    const end = performance.now();

    return end - start;
}

function runtimeExperiment() {
    printSection("RUNTIME EXPERIMENT");

    const sizes = [100, 500, 1000, 2000];

    console.log(
        "n".padStart(8),
        "O(n) ms".padStart(16),
        "O(n²) ms".padStart(16)
    );

    for (const n of sizes) {
        const data = Array.from({ length: n }, (_, index) => index);

        const linearMilliseconds = measureMilliseconds(() => {
            linearSum(data);
        });

        const quadraticSize = Math.min(n, 2000);
        const quadraticData = Array.from(
            { length: quadraticSize },
            (_, index) => index
        );

        const quadraticMilliseconds = measureMilliseconds(() => {
            quadraticPairCount(quadraticData);
        });

        console.log(
            String(n).padStart(8),
            linearMilliseconds.toFixed(5).padStart(16),
            quadraticMilliseconds.toFixed(5).padStart(16)
        );
    }
}

// ============================================================================
// 15. COMPLEXITY REFERENCE
// ============================================================================

const complexityExamples = [
    {
        name: "Array index access",
        complexity: "O(1)",
        reason: "One direct access is performed."
    },
    {
        name: "Binary search",
        complexity: "O(log n)",
        reason: "Approximately half of the remaining elements are eliminated."
    },
    {
        name: "Single loop",
        complexity: "O(n)",
        reason: "One pass visits the input."
    },
    {
        name: "Merge sort",
        complexity: "O(n log n)",
        reason: "Logarithmic levels each process linear total work."
    },
    {
        name: "Two independent nested loops",
        complexity: "O(n²)",
        reason: "n iterations are performed for each of n iterations."
    },
    {
        name: "Three nested loops",
        complexity: "O(n³)",
        reason: "Three independent dimensions each grow with n."
    }
];

function printComplexityTable() {
    for (const example of complexityExamples) {
        console.log(
            `${example.name.padEnd(34)} ` +
            `${example.complexity.padEnd(10)} ` +
            `${example.reason}`
        );
    }
}

// ============================================================================
// 16. EDGE CASES
// ============================================================================

function safeLog2(n) {
    /*
     * log2(0) and log2(negative numbers) are not valid real-number inputs.
     */
    if (n <= 0) {
        throw new RangeError("log2 requires a positive number");
    }

    return Math.log2(n);
}

function demonstrateEdgeCases() {
    console.log("Empty search:", linearSearch([], 10));
    console.log("Empty sort:", mergeSort([]));
    console.log("Single-item sort:", mergeSort([7]));
    console.log("Halving n=1:", halvingSteps(1));
    console.log("Doubling n=1:", doublingSteps(1));

    for (const invalidValue of [0, -1]) {
        try {
            safeLog2(invalidValue);
        } catch (error) {
            console.log(
                `safeLog2(${invalidValue}) -> ${error.message}`
            );
        }
    }
}

// ============================================================================
// 17. CORRECTNESS TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function arraysEqual(first, second) {
    if (first.length !== second.length) {
        return false;
    }

    for (let i = 0; i < first.length; i++) {
        if (first[i] !== second[i]) {
            return false;
        }
    }

    return true;
}

function runTests() {
    printSection("CORRECTNESS TESTS");

    assert(constantOperation([10, 20]) === 10, "constant operation");
    assert(linearSum([1, 2, 3]) === 6, "linear sum");
    assert(quadraticPairCount([1, 2, 3]) === 9, "quadratic count");
    assert(triangularPairCount([1, 2, 3, 4]) === 10, "triangular count");
    assert(cubicOperation(3) === 27, "cubic count");

    assert(halvingSteps(1) === 0, "halving 1");
    assert(halvingSteps(8) === 3, "halving 8");
    assert(doublingSteps(1) === 0, "doubling 1");
    assert(doublingSteps(8) === 3, "doubling 8");

    const sorted = [2, 4, 6, 8, 10, 12];

    assert(binarySearch(sorted, 2) === 0, "binary first");
    assert(binarySearch(sorted, 12) === 5, "binary last");
    assert(binarySearch(sorted, 9) === -1, "binary missing");

    assert(
        recursiveBinarySearch(sorted, 8) === 3,
        "recursive binary search"
    );

    assert(
        arraysEqual(mergeSort([3, 1, 2]), [1, 2, 3]),
        "merge sort"
    );

    assert(recursiveCountdown(5) === 5, "recursive countdown");
    assert(naiveFibonacci(10) === 55, "naive Fibonacci");

    for (let n = 0; n <= 20; n++) {
        assert(
            dynamicFibonacci(n) === naiveFibonacci(n),
            `Fibonacci ${n}`
        );
    }

    assert(linearSearch([10, 20, 30], 10) === 0, "linear first");
    assert(linearSearch([10, 20, 30], 30) === 2, "linear last");
    assert(linearSearch([10, 20, 30], 99) === -1, "linear missing");

    console.log("All correctness tests passed.");
}

// ============================================================================
// 18. SCALING TABLE
// ============================================================================

function printScalingTable() {
    printSection("MATHEMATICAL GROWTH");

    const sizes = [10, 100, 1000, 10000];

    console.log(
        "n".padStart(8),
        "log₂n".padStart(14),
        "n".padStart(14),
        "n log₂n".padStart(18),
        "n²".padStart(18),
        "n³".padStart(22)
    );

    for (const n of sizes) {
        const logN = Math.log2(n);
        const nLogN = n * logN;
        const nSquared = n * n;
        const nCubed = n * n * n;

        console.log(
            String(n).padStart(8),
            logN.toFixed(2).padStart(14),
            formatNumber(n).padStart(14),
            nLogN.toFixed(2).padStart(18),
            formatNumber(nSquared).padStart(18),
            formatNumber(nCubed).padStart(22)
        );
    }
}

// ============================================================================
// 19. STUDY SESSION
// ============================================================================

function main() {
    printSection("DAY 7 — TIME COMPLEXITY");

    console.log(`
Time complexity describes how algorithmic work grows as input size n grows.

Common classes:

    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) linearithmic
    O(n²)      quadratic
    O(n³)      cubic

Examples:
    5n + 20       -> O(n)
    3n² + 7n + 10 -> O(n²)
    8log(n) + 4   -> O(log n)

Big O focuses on asymptotic growth. It does not directly state how many
milliseconds a program will take on a particular computer.
`);

    printSection("BASIC EXAMPLES");

    const data = [1, 2, 3, 4];

    console.log("O(1):", constantOperation(data));
    console.log("O(n):", linearSum(data));
    console.log("O(n²) operation count:", quadraticPairCount(data));
    console.log("O(n³) operation count:", cubicOperation(4));

    printSection("HALVING AND DOUBLING");

    for (const n of [1, 2, 4, 8, 16, 32, 64]) {
        console.log(
            `n=${n.toString().padStart(2)} | ` +
            `halving=${halvingSteps(n).toString().padStart(2)} | ` +
            `doubling=${doublingSteps(n).toString().padStart(2)}`
        );
    }

    printSection("MERGE SORT");

    const unsorted = [9, 1, 8, 2, 7, 3, 6, 4, 5];
    console.log("Before:", unsorted);
    console.log("After: ", mergeSort(unsorted));

    printSection("SEQUENTIAL OPERATIONS");

    console.log(
        "O(n) + O(n):",
        sequentialLinearWork([1, 2, 3, 4])
    );

    console.log(
        "O(n) + O(n²):",
        linearThenQuadratic([1, 2, 3, 4])
    );

    printSection("RECURSION");

    console.log("recursiveCountdown(5):", recursiveCountdown(5));
    console.log("naiveFibonacci(10):", naiveFibonacci(10));
    console.log("dynamicFibonacci(10):", dynamicFibonacci(10));

    printSection("BINARY SEARCH");

    const sortedNumbers = Array.from(
        { length: 20 },
        (_, index) => index * 5
    );

    console.log("Data:", sortedNumbers);
    console.log("Search 50:", binarySearch(sortedNumbers, 50));
    console.log("Search 51:", binarySearch(sortedNumbers, 51));

    printSection("DOMINANT TERMS");
    demonstrateDominantTerms();

    printSection("COMPLEXITY REFERENCE");
    printComplexityTable();

    printSection("EDGE CASES");
    demonstrateEdgeCases();

    printSection("SPACE COMPLEXITY");
    console.log("Iterative sum:", iterativeSum([1, 2, 3, 4]));
    console.log("Copied sum:", copiedSum([1, 2, 3, 4]));
    console.log("Iterative sum uses O(1) auxiliary space.");
    console.log("Copied sum uses O(n) auxiliary space.");

    printScalingTable();
    runTests();

    /*
     * The timing experiment is intentionally near the end. Mathematical
     * analysis should come first; measurements only show observed behavior
     * under one runtime environment.
     */
    runtimeExperiment();

    printSection("STUDY FILE COMPLETED");
    console.log(
        "The demonstrations cover the major Day 7 time-complexity patterns."
    );
}

main();
