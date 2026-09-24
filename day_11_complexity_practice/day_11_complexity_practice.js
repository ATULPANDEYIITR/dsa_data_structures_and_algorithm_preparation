/*
 * Day 11 — Complexity Practice
 *
 * This file complements the Python study script by using JavaScript to
 * demonstrate complexity analysis through arrays, objects, Map/Set,
 * recursion, sorting, iteration, and practical application patterns.
 *
 * Run with:
 *     node day11_complexity_practice.js
 *
 * No external packages are required.
 */

// ============================================================================
// 1. CONSTANT-TIME ACCESS
// ============================================================================

function getFirstElement(values) {
    /*
     * Array indexing directly accesses a position.
     * Time: O(1)
     * Auxiliary space: O(1)
     */
    return values.length === 0 ? undefined : values[0];
}

// ============================================================================
// 2. LINEAR SEARCH
// ============================================================================

function linearSearch(values, target) {
    /*
     * At most n elements are inspected.
     *
     * Best case: O(1)
     * Worst case: O(n)
     * Auxiliary space: O(1)
     */
    for (let index = 0; index < values.length; index += 1) {
        if (values[index] === target) {
            return index;
        }
    }

    return -1;
}

// ============================================================================
// 3. BINARY SEARCH
// ============================================================================

function binarySearch(sortedValues, target) {
    /*
     * The search interval is cut approximately in half after every iteration.
     *
     * Time: O(log n)
     * Auxiliary space: O(1)
     *
     * The input must already be sorted.
     */
    let left = 0;
    let right = sortedValues.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);
        const value = sortedValues[middle];

        if (value === target) {
            return middle;
        }

        if (value < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

// ============================================================================
// 4. SINGLE LINEAR PASS
// ============================================================================

function sumValues(values) {
    /*
     * Every element must be examined.
     *
     * Time: O(n)
     * Space: O(1)
     */
    let total = 0;

    for (const value of values) {
        total += value;
    }

    return total;
}

// ============================================================================
// 5. SEQUENTIAL LOOPS
// ============================================================================

function sequentialProcessing(values) {
    /*
     * First loop: O(n)
     * Second loop: O(n)
     *
     * Total:
     *     O(n) + O(n) = O(2n) = O(n)
     */
    let total = 0;
    let maximum = undefined;

    for (const value of values) {
        total += value;
    }

    for (const value of values) {
        if (maximum === undefined || value > maximum) {
            maximum = value;
        }
    }

    return { total, maximum };
}

// ============================================================================
// 6. NESTED LOOPS
// ============================================================================

function generateAllPairs(values) {
    /*
     * n iterations of the outer loop multiplied by n iterations of the
     * inner loop produces O(n^2) work.
     *
     * Because this function stores all pairs, output space is also O(n^2).
     */
    const pairs = [];

    for (const first of values) {
        for (const second of values) {
            pairs.push([first, second]);
        }
    }

    return pairs;
}

// ============================================================================
// 7. TRIANGULAR LOOP
// ============================================================================

function generateUniquePairs(values) {
    /*
     * The inner loop gets shorter as i increases:
     *
     *     (n - 1) + (n - 2) + ... + 1
     *
     * This is n(n - 1) / 2, which is still O(n^2).
     */
    const pairs = [];

    for (let i = 0; i < values.length; i += 1) {
        for (let j = i + 1; j < values.length; j += 1) {
            pairs.push([values[i], values[j]]);
        }
    }

    return pairs;
}

// ============================================================================
// 8. LOGARITHMIC PROCESS
// ============================================================================

function countHalvings(value) {
    if (!Number.isInteger(value) || value < 1) {
        throw new RangeError("value must be a positive integer");
    }

    let steps = 0;

    while (value > 1) {
        value = Math.floor(value / 2);
        steps += 1;
    }

    /*
     * The value is reduced by a constant factor each iteration.
     * Time: O(log n)
     * Space: O(1)
     */
    return steps;
}

// ============================================================================
// 9. MERGE SORT
// ============================================================================

function merge(left, right) {
    /*
     * Each element from both sorted arrays is considered once.
     * Time: O(n) relative to the combined input size.
     */
    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    while (leftIndex < left.length && rightIndex < right.length) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push(left[leftIndex]);
            leftIndex += 1;
        } else {
            result.push(right[rightIndex]);
            rightIndex += 1;
        }
    }

    while (leftIndex < left.length) {
        result.push(left[leftIndex]);
        leftIndex += 1;
    }

    while (rightIndex < right.length) {
        result.push(right[rightIndex]);
        rightIndex += 1;
    }

    return result;
}

function mergeSort(values) {
    /*
     * Recurrence:
     *
     *     T(n) = 2T(n/2) + O(n)
     *
     * Therefore:
     *
     *     Time = O(n log n)
     *
     * This implementation creates arrays during splitting and merging, so
     * auxiliary memory is O(n), apart from recursion overhead.
     */
    if (values.length <= 1) {
        return [...values];
    }

    const middle = Math.floor(values.length / 2);
    const left = mergeSort(values.slice(0, middle));
    const right = mergeSort(values.slice(middle));

    return merge(left, right);
}

// ============================================================================
// 10. TWO-SUM USING MAP
// ============================================================================

function twoSumWithMap(values, target) {
    /*
     * Map lookup is average O(1).
     *
     * The loop runs n times.
     *
     * Average time: O(n)
     * Auxiliary space: O(n)
     */
    const seen = new Map();

    for (let index = 0; index < values.length; index += 1) {
        const value = values[index];
        const complement = target - value;

        if (seen.has(complement)) {
            return [seen.get(complement), index];
        }

        seen.set(value, index);
    }

    return null;
}

// ============================================================================
// 11. TWO-POINTER TWO-SUM
// ============================================================================

function twoSumSorted(values, target) {
    /*
     * Requires sorted input.
     *
     * Each pointer moves only toward the center.
     * Total pointer movement is O(n).
     *
     * Time: O(n)
     * Auxiliary space: O(1)
     */
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        const sum = values[left] + values[right];

        if (sum === target) {
            return [left, right];
        }

        if (sum < target) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    return null;
}

// ============================================================================
// 12. DUPLICATE DETECTION
// ============================================================================

function containsDuplicateWithSet(values) {
    /*
     * Set membership is average O(1).
     *
     * Time: O(n) average
     * Space: O(n)
     */
    const seen = new Set();

    for (const value of values) {
        if (seen.has(value)) {
            return true;
        }

        seen.add(value);
    }

    return false;
}

function containsDuplicateBySorting(values) {
    /*
     * Sorting costs approximately O(n log n).
     * Scanning adjacent elements costs O(n).
     *
     * Total remains O(n log n).
     */
    const sortedValues = [...values].sort((a, b) => a - b);

    for (let index = 1; index < sortedValues.length; index += 1) {
        if (sortedValues[index] === sortedValues[index - 1]) {
            return true;
        }
    }

    return false;
}

// ============================================================================
// 13. RECURSIVE FACTORIAL
// ============================================================================

function factorialRecursive(n) {
    /*
     * One recursive call is made for every decrement.
     *
     * Time: O(n)
     * Recursion-stack space: O(n)
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n <= 1) {
        return 1;
    }

    return n * factorialRecursive(n - 1);
}

function factorialIterative(n) {
    /*
     * Time: O(n)
     * Auxiliary space: O(1)
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    let result = 1;

    for (let value = 2; value <= n; value += 1) {
        result *= value;
    }

    return result;
}

// ============================================================================
// 14. FIBONACCI AND REPEATED SUBPROBLEMS
// ============================================================================

function fibonacciNaive(n) {
    /*
     * This function repeatedly recalculates the same values.
     *
     * Its growth is exponential and is commonly described with an O(2^n)
     * upper-bound classification for introductory analysis.
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n <= 1) {
        return n;
    }

    return fibonacciNaive(n - 1) + fibonacciNaive(n - 2);
}

function fibonacciMemoized(n, memo = new Map()) {
    /*
     * Memoization stores each result.
     *
     * Time: O(n)
     * Space: O(n)
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (memo.has(n)) {
        return memo.get(n);
    }

    if (n <= 1) {
        return n;
    }

    const result =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    memo.set(n, result);
    return result;
}

function fibonacciIterative(n) {
    /*
     * Dynamic programming without a table.
     *
     * Time: O(n)
     * Auxiliary space: O(1)
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    let previous = 0;
    let current = 1;

    for (let index = 0; index < n; index += 1) {
        [previous, current] = [current, previous + current];
    }

    return previous;
}

// ============================================================================
// 15. OBJECT / MAP LOOKUP TRADE-OFF
// ============================================================================

function countFrequencies(values) {
    /*
     * A Map allows average constant-time updates.
     *
     * Time: O(n)
     * Space: O(k), where k is the number of distinct values.
     *
     * Since k <= n, worst-case space is O(n).
     */
    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
    }

    return frequencies;
}

// ============================================================================
// 16. INDEPENDENT INPUT SIZES
// ============================================================================

function compareEveryPair(first, second) {
    /*
     * If the first input has n elements and the second has m elements:
     *
     * Time = O(nm)
     *
     * It is incorrect to automatically call this O(n^2) unless n and m are
     * explicitly assumed to have the same growth rate.
     */
    let comparisons = 0;

    for (const firstValue of first) {
        for (const secondValue of second) {
            comparisons += firstValue === secondValue ? 1 : 0;
        }
    }

    return comparisons;
}

// ============================================================================
// 17. AMORTIZED ARRAY OPERATIONS
// ============================================================================

function demonstrateDynamicArray() {
    /*
     * JavaScript arrays can grow dynamically.
     *
     * push() is generally treated as amortized O(1), although an individual
     * resize can require more work.
     */
    const values = [];

    for (let number = 0; number < 10; number += 1) {
        values.push(number);
    }

    return values;
}

// ============================================================================
// 18. OUTPUT SIZE MATTERS
// ============================================================================

function generateAllTriples(values) {
    /*
     * Generating all combinations of three values produces Θ(n^3) output.
     *
     * Even a theoretically faster computation cannot produce n^3 distinct
     * output items in o(n^3) time because the output itself has that size.
     */
    const triples = [];

    for (let i = 0; i < values.length; i += 1) {
        for (let j = i + 1; j < values.length; j += 1) {
            for (let k = j + 1; k < values.length; k += 1) {
                triples.push([values[i], values[j], values[k]]);
            }
        }
    }

    return triples;
}

// ============================================================================
// 19. COMPLEXITY OF A FUNCTION CALL INSIDE A LOOP
// ============================================================================

function expensivePattern(values) {
    /*
     * Calling linearSearch inside a loop over n values gives:
     *
     * Outer loop: O(n)
     * linearSearch: O(n)
     *
     * Combined: O(n^2)
     */
    let foundCount = 0;

    for (const value of values) {
        if (linearSearch(values, value) !== -1) {
            foundCount += 1;
        }
    }

    return foundCount;
}

function optimizedPattern(values) {
    /*
     * Build a Set once:
     *
     * Construction: O(n) average
     * Membership checks: O(1) average each
     * n checks: O(n)
     *
     * Total: O(n) average.
     */
    const valueSet = new Set(values);
    let foundCount = 0;

    for (const value of values) {
        if (valueSet.has(value)) {
            foundCount += 1;
        }
    }

    return foundCount;
}

// ============================================================================
// 20. BEST / AVERAGE / WORST CASE
// ============================================================================

function demonstrateSearchCases() {
    const values = [10, 20, 30, 40, 50];

    return {
        bestCase: linearSearch(values, 10),
        worstCase: linearSearch(values, 50),
        missingCase: linearSearch(values, 999)
    };
}

// ============================================================================
// 21. BENCHMARKING
// ============================================================================

function benchmark(functionToMeasure, argument, repetitions = 5) {
    /*
     * Benchmarking measures one implementation on one machine and workload.
     * It is useful evidence, but it does not establish Big-O by itself.
     */
    let bestMilliseconds = Number.POSITIVE_INFINITY;

    for (let attempt = 0; attempt < repetitions; attempt += 1) {
        const start = performance.now();

        functionToMeasure(argument);

        const elapsed = performance.now() - start;
        bestMilliseconds = Math.min(bestMilliseconds, elapsed);
    }

    return bestMilliseconds;
}

// ============================================================================
// 22. CODE-READING PRACTICE
// ============================================================================

function explainCodeReadingPatterns() {
    console.log(`
CODE READING PRACTICE

Pattern A:
    for (let i = 0; i < n; i++) {
        work();
    }

Time: O(n)
Space: O(1), assuming work() does not allocate growing memory.

Pattern B:
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            work();
        }
    }

Time: O(n^2)

Pattern C:
    let value = 1;
    while (value < n) {
        value *= 2;
    }

Time: O(log n)

Pattern D:
    for (const value of values) {
        linearSearch(values, value);
    }

Time: O(n^2), because O(n) search occurs n times.

Pattern E:
    const seen = new Set(values);
    for (const value of values) {
        seen.has(value);
    }

Average time: O(n)
Extra space: O(n)
`);
}

// ============================================================================
// 23. COMPLEXITY ANALYSIS RECORDS
// ============================================================================

function printAnalysis(title, approach, time, space, optimization) {
    console.log(`\n=== ${title} ===`);
    console.log(`Approach: ${approach}`);
    console.log(`Time Complexity: ${time}`);
    console.log(`Space Complexity: ${space}`);
    console.log(`Possible Optimization: ${optimization}`);
}

function printProblemAnalyses() {
    printAnalysis(
        "Find Maximum",
        "Scan once while maintaining the largest value.",
        "O(n)",
        "O(1) auxiliary space",
        "No asymptotic improvement is possible when every value may need inspection."
    );

    printAnalysis(
        "Reverse Array",
        "Use two pointers and swap values from both ends.",
        "O(n)",
        "O(1) auxiliary space",
        "The in-place two-pointer method is already asymptotically optimal."
    );

    printAnalysis(
        "Binary Search",
        "Repeatedly halve the search interval in sorted data.",
        "O(log n)",
        "O(1) auxiliary space",
        "Maintain sorted data so repeated searches can remain logarithmic."
    );

    printAnalysis(
        "Two Sum With Map",
        "Store previously seen values and check complements.",
        "O(n) average",
        "O(n)",
        "Use a two-pointer solution when sorted input and constant auxiliary space are preferable."
    );

    printAnalysis(
        "Merge Sort",
        "Divide the input into halves and merge sorted results.",
        "O(n log n)",
        "O(n) auxiliary space in this implementation",
        "Alternative sorting strategies may reduce memory or improve practical constants."
    );
}

// ============================================================================
// 24. EDGE CASES
// ============================================================================

function demonstrateEdgeCases() {
    const cases = {
        empty: [],
        single: [42],
        duplicates: [5, 5, 5],
        sorted: [1, 2, 3, 4, 5],
        reverseSorted: [5, 4, 3, 2, 1]
    };

    console.log("\n=== Edge Cases ===");
    console.log("Empty search:", linearSearch(cases.empty, 1));
    console.log("Single search:", linearSearch(cases.single, 42));
    console.log("Duplicates:", containsDuplicateWithSet(cases.duplicates));
    console.log("Sorted merge sort:", mergeSort(cases.sorted));
    console.log("Reverse merge sort:", mergeSort(cases.reverseSorted));

    try {
        countHalvings(0);
    } catch (error) {
        console.log("Invalid input:", error.message);
    }
}

// ============================================================================
// 25. PERFORMANCE AND SPACE DEMONSTRATION
// ============================================================================

function runBenchmark() {
    /*
     * Keep the quadratic workload modest so the demonstration remains practical.
     */
    const values = Array.from(
        { length: 700 },
        (_, index) => (index * 37) % 10000
    );

    const linearMilliseconds = benchmark(sumValues, values, 3);
    const quadraticMilliseconds = benchmark(generateUniquePairs, values, 3);

    console.log("\n=== Small Benchmark ===");
    console.log(`Linear operation: ${linearMilliseconds.toFixed(4)} ms`);
    console.log(`Quadratic operation: ${quadraticMilliseconds.toFixed(4)} ms`);
    console.log(
        "Measured performance depends on hardware, runtime, input, allocation, and implementation."
    );
}

// ============================================================================
// 26. MAIN
// ============================================================================

function main() {
    console.log("=".repeat(78));
    console.log("DAY 11 — COMPLEXITY PRACTICE");
    console.log("=".repeat(78));

    const sample = [7, 2, 9, 4, 1, 8];

    console.log("\n=== Basic Examples ===");
    console.log("First:", getFirstElement(sample));
    console.log("Linear search:", linearSearch(sample, 4));
    console.log("Sum:", sumValues(sample));
    console.log("Sequential processing:", sequentialProcessing(sample));
    console.log("Sorted:", mergeSort(sample));
    console.log("Binary search:", binarySearch([1, 2, 4, 7, 8, 9], 7));

    console.log("\n=== Pair and Search Examples ===");
    console.log("All pairs:", generateAllPairs([1, 2, 3]));
    console.log("Unique pairs:", generateUniquePairs([1, 2, 3]));
    console.log("Two sum Map:", twoSumWithMap(sample, 10));
    console.log("Two sum sorted:", twoSumSorted([1, 2, 4, 7, 8, 9], 10));

    console.log("\n=== Duplicate Detection ===");
    console.log("Set:", containsDuplicateWithSet([1, 2, 3, 2]));
    console.log("Sorting:", containsDuplicateBySorting([1, 2, 3, 2]));

    console.log("\n=== Recursion ===");
    console.log("Recursive factorial:", factorialRecursive(6));
    console.log("Iterative factorial:", factorialIterative(6));
    console.log("Naive Fibonacci:", fibonacciNaive(20));
    console.log("Memoized Fibonacci:", fibonacciMemoized(20));
    console.log("Iterative Fibonacci:", fibonacciIterative(20));

    console.log("\n=== Frequency Counting ===");
    console.log(
        "Frequencies:",
        Object.fromEntries(countFrequencies([2, 2, 4, 4, 4, 7]))
    );

    console.log("\n=== Independent Inputs ===");
    console.log(
        "Comparisons:",
        compareEveryPair([1, 2, 3], ["a", "b", "c", "d"])
    );

    console.log("\n=== Dynamic Array ===");
    console.log(demonstrateDynamicArray());

    console.log("\n=== Function-Call Complexity ===");
    console.log("Unoptimized:", expensivePattern(sample));
    console.log("Optimized:", optimizedPattern(sample));

    console.log("\n=== Search Cases ===");
    console.log(demonstrateSearchCases());

    explainCodeReadingPatterns();
    printProblemAnalyses();
    demonstrateEdgeCases();

    console.log("\n=== Output-Sensitive Example ===");
    console.log(
        "Number of triples:",
        generateAllTriples([1, 2, 3, 4]).length
    );

    runBenchmark();

    console.log("\n=== Day 11 Checkpoint ===");
    console.log("Identify loops, nesting, recursion, function-call costs, and extra memory.");
    console.log("Reduce the result to its dominant asymptotic growth.");
    console.log("State assumptions when using average-case complexity.");
    console.log("Separate time complexity from auxiliary space complexity.");
    console.log("Day 11 practice completed.");
}

main();
