/*
 * Day 8 — Space Complexity
 *
 * This standalone JavaScript file studies:
 *   - Input space
 *   - Auxiliary space
 *   - Variables
 *   - Arrays
 *   - Recursion stack
 *   - In-place algorithms
 *   - Iterative and recursive solutions
 *   - Array-based and string-based solutions
 *   - Extra Maps and Sets
 *   - Time-space trade-offs
 *   - Space-optimized dynamic programming
 *
 * The examples can be executed with a modern JavaScript runtime such as Node.js.
 */

"use strict";

// ============================================================================
// 1. BASIC SPACE COMPLEXITY
// ============================================================================

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function explainSpaceComplexity() {
    printSection("1. BASIC SPACE COMPLEXITY");

    console.log(`
Space complexity describes how memory requirements grow as input size grows.

A useful conceptual model is:

    Total space = input space + auxiliary space

Input space is memory occupied by the input.

Auxiliary space is additional working memory created by the algorithm.

Examples:

    A few numbers:
        O(1) auxiliary space

    A copied array of n elements:
        O(n) auxiliary space

    A recursive call chain of n levels:
        O(n) stack space

    An r by c matrix:
        O(r * c) space

Important:
A loop does not automatically mean O(n) space.
A nested loop does not automatically mean O(n^2) space.

Space depends on how much data the algorithm stores simultaneously.
`);

    const input = [10, 20, 30, 40];
    console.log("Input:", input);
}


// ============================================================================
// 2. CONSTANT SPACE
// ============================================================================

function sumWithConstantSpace(numbers) {
    // Only one accumulator is retained regardless of input length.
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    return total;
}

function findMaximumWithConstantSpace(numbers) {
    if (numbers.length === 0) {
        return undefined;
    }

    let maximum = numbers[0];

    for (let index = 1; index < numbers.length; index++) {
        if (numbers[index] > maximum) {
            maximum = numbers[index];
        }
    }

    return maximum;
}

function demonstrateConstantSpace() {
    printSection("2. VARIABLES AND O(1) AUXILIARY SPACE");

    const numbers = [8, 3, 15, 2, 9];

    console.log("Sum:", sumWithConstantSpace(numbers));
    console.log("Maximum:", findMaximumWithConstantSpace(numbers));

    console.log(`
The algorithms use a fixed number of variables:

    total
    maximum
    index

The number of variables does not grow with n.

Auxiliary space = O(1).
`);
}


// ============================================================================
// 3. ARRAY COPY VS IN-PLACE MODIFICATION
// ============================================================================

function squareUsingNewArray(numbers) {
    // map creates a new array containing n results.
    return numbers.map(number => number * number);
}

function squareInPlace(numbers) {
    // The existing array is modified.
    // No second n-sized result array is intentionally created.
    for (let index = 0; index < numbers.length; index++) {
        numbers[index] *= numbers[index];
    }

    return numbers;
}

function demonstrateArrays() {
    printSection("3. ARRAYS: O(n) SPACE VS O(1) AUXILIARY SPACE");

    const original = [1, 2, 3, 4, 5];
    const copiedResult = squareUsingNewArray(original);

    console.log("Original:", original);
    console.log("New squared array:", copiedResult);
    console.log("New result requires O(n) storage.");

    const inPlaceInput = [1, 2, 3, 4, 5];
    squareInPlace(inPlaceInput);

    console.log("In-place squared array:", inPlaceInput);
    console.log("In-place processing uses O(1) auxiliary variables.");

    console.log(`
The returned output itself may occupy O(n) memory.

When analyzing auxiliary space, many algorithm problems distinguish:

    required output space
from
    additional working space

This distinction must be stated when it affects the analysis.
`);
}


// ============================================================================
// 4. IN-PLACE REVERSAL
// ============================================================================

function reverseInPlace(numbers) {
    let left = 0;
    let right = numbers.length - 1;

    while (left < right) {
        [numbers[left], numbers[right]] =
            [numbers[right], numbers[left]];

        left++;
        right--;
    }

    return numbers;
}

function reverseWithCopy(numbers) {
    // slice creates a copy and reverse modifies that copy.
    return [...numbers].reverse();
}

function demonstrateInPlaceAlgorithm() {
    printSection("4. IN-PLACE ALGORITHMS");

    const first = [10, 20, 30, 40, 50];
    const second = [10, 20, 30, 40, 50];

    console.log("In-place:", reverseInPlace(first));
    console.log("Copy-based:", reverseWithCopy(second));

    console.log(`
The in-place implementation maintains only:

    left
    right
    temporary swap storage

Therefore auxiliary space is O(1).

The copy-based implementation creates another array of n elements,
so auxiliary space is O(n).
`);
}


// ============================================================================
// 5. RECURSION STACK
// ============================================================================

function factorialRecursive(n) {
    if (n < 0) {
        throw new RangeError("Factorial requires n >= 0.");
    }

    if (n <= 1) {
        return 1;
    }

    return n * factorialRecursive(n - 1);
}

function factorialIterative(n) {
    if (n < 0) {
        throw new RangeError("Factorial requires n >= 0.");
    }

    let result = 1;

    for (let value = 2; value <= n; value++) {
        result *= value;
    }

    return result;
}

function recursiveSum(numbers, index = 0) {
    if (index === numbers.length) {
        return 0;
    }

    return numbers[index] + recursiveSum(numbers, index + 1);
}

function iterativeSum(numbers) {
    let total = 0;

    for (const number of numbers) {
        total += number;
    }

    return total;
}

function demonstrateRecursion() {
    printSection("5. ITERATIVE VS RECURSIVE SPACE");

    const n = 6;

    console.log("Iterative factorial:", factorialIterative(n));
    console.log("Recursive factorial:", factorialRecursive(n));

    const numbers = [5, 10, 15, 20];

    console.log("Iterative sum:", iterativeSum(numbers));
    console.log("Recursive sum:", recursiveSum(numbers));

    console.log(`
The iterative versions use O(1) auxiliary space.

The recursive versions can have O(n) stack usage because multiple calls
remain active simultaneously.

Conceptually:

    function(n)
        function(n - 1)
            function(n - 2)
                ...

The call stack is memory and must be included in space analysis.
`);
}


// ============================================================================
// 6. STRING SPACE
// ============================================================================

function reverseString(text) {
    // Array.from creates an array of characters/code points and reverse()
    // modifies that temporary array. The result is another string.
    return Array.from(text).reverse().join("");
}

function isPalindromeConstantAuxiliary(text) {
    let left = 0;
    let right = text.length - 1;

    while (left < right) {
        if (text[left] !== text[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}

function removeWhitespace(text) {
    // replace creates a new string.
    return text.replace(/\s/g, "");
}

function demonstrateStrings() {
    printSection("6. STRING-BASED SPACE");

    const text = "space complexity";

    console.log("Original:", text);
    console.log("Reversed:", reverseString(text));
    console.log("Without whitespace:", removeWhitespace(text));

    console.log("Palindrome 'level':",
        isPalindromeConstantAuxiliary("level"));

    console.log(`
String operations need careful analysis.

Depending on the language and operation:

    - A new string may be allocated.
    - A temporary character array may be allocated.
    - Concatenation may create temporary strings.
    - Immutable strings cannot normally be modified in place.

A two-pointer palindrome check can use O(1) additional algorithmic variables,
while constructing a reversed copy generally requires O(n) additional storage.
`);
}


// ============================================================================
// 7. SET SPACE
// ============================================================================

function containsDuplicateUsingSet(numbers) {
    const seen = new Set();

    for (const number of numbers) {
        if (seen.has(number)) {
            return true;
        }

        seen.add(number);
    }

    return false;
}

function containsDuplicateBruteForce(numbers) {
    for (let first = 0; first < numbers.length; first++) {
        for (let second = first + 1; second < numbers.length; second++) {
            if (numbers[first] === numbers[second]) {
                return true;
            }
        }
    }

    return false;
}

function demonstrateSetTradeoff() {
    printSection("7. EXTRA SET SPACE AND TIME-SPACE TRADE-OFF");

    const numbers = [4, 8, 2, 9, 4];

    console.log(
        "Set solution:",
        containsDuplicateUsingSet(numbers)
    );

    console.log(
        "Brute-force solution:",
        containsDuplicateBruteForce(numbers)
    );

    console.log(`
Set-based approach:

    Average time: O(n)
    Worst-case stored entries: O(n)

Brute-force approach:

    Time: O(n^2)
    Auxiliary space: O(1)

The set consumes additional memory to avoid repeated comparisons.

This is a classic time-space trade-off.
`);
}


// ============================================================================
// 8. MAP / FREQUENCY COUNT
// ============================================================================

function frequencyCount(numbers) {
    const frequencies = new Map();

    for (const number of numbers) {
        frequencies.set(
            number,
            (frequencies.get(number) ?? 0) + 1
        );
    }

    return frequencies;
}

function demonstrateMapSpace() {
    printSection("8. MAP SPACE: O(k)");

    const numbers = [5, 5, 5, 2, 2, 9];
    const frequencies = frequencyCount(numbers);

    console.log("Input:", numbers);
    console.log("Frequency map:", frequencies);

    console.log(`
If k is the number of distinct values:

    Space = O(k)

Since k <= n:

    Worst case = O(n)

For highly repetitive data, k may be much smaller than n.

Parameterized analysis is often more informative than simply writing O(n).
`);
}


// ============================================================================
// 9. MATRIX SPACE
// ============================================================================

function createMatrix(rows, columns) {
    const matrix = [];

    for (let row = 0; row < rows; row++) {
        const currentRow = [];

        for (let column = 0; column < columns; column++) {
            currentRow.push(0);
        }

        matrix.push(currentRow);
    }

    return matrix;
}

function demonstrateMatrixSpace() {
    printSection("9. MULTIDIMENSIONAL SPACE");

    const rows = 3;
    const columns = 4;

    const matrix = createMatrix(rows, columns);

    console.log("Matrix:", matrix);
    console.log(`Space = O(rows * columns) = O(${rows} * ${columns})`);

    console.log(`
For an n by n matrix:

    Space = O(n^2)

A nested loop alone does not establish O(n^2) space.
It becomes O(n^2) space when the algorithm stores n^2 values.
`);
}


// ============================================================================
// 10. SLIDING WINDOW WITH CONSTANT SPACE
// ============================================================================

function maximumFixedWindowSum(numbers, windowSize) {
    if (!Number.isInteger(windowSize) ||
        windowSize <= 0 ||
        windowSize > numbers.length) {
        return undefined;
    }

    let currentSum = 0;

    for (let index = 0; index < windowSize; index++) {
        currentSum += numbers[index];
    }

    let maximumSum = currentSum;

    for (let index = windowSize; index < numbers.length; index++) {
        currentSum += numbers[index];
        currentSum -= numbers[index - windowSize];

        maximumSum = Math.max(maximumSum, currentSum);
    }

    return maximumSum;
}

function demonstrateSlidingWindow() {
    printSection("10. SLIDING WINDOW");

    const numbers = [2, 1, 5, 1, 3, 2];

    console.log(
        "Maximum sum of a window of size 3:",
        maximumFixedWindowSum(numbers, 3)
    );

    console.log(`
The sliding-window algorithm stores only a fixed number of variables:

    currentSum
    maximumSum
    index

Therefore:

    Auxiliary space = O(1)

It avoids creating a separate array for every possible window.
`);
}


// ============================================================================
// 11. MEMOIZATION
// ============================================================================

function fibonacciPlainRecursive(n) {
    if (n <= 1) {
        return n;
    }

    return (
        fibonacciPlainRecursive(n - 1) +
        fibonacciPlainRecursive(n - 2)
    );
}

function fibonacciMemoized(n, memo = new Map()) {
    if (n <= 1) {
        return n;
    }

    if (memo.has(n)) {
        return memo.get(n);
    }

    const result =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    memo.set(n, result);

    return result;
}

function demonstrateMemoization() {
    printSection("11. MEMOIZATION");

    const n = 20;

    console.log(
        "Plain recursive Fibonacci:",
        fibonacciPlainRecursive(n)
    );

    console.log(
        "Memoized Fibonacci:",
        fibonacciMemoized(n)
    );

    console.log(`
Memoization stores already computed results.

Typical analysis:

    Plain recursive Fibonacci:
        Time: exponential
        Stack: O(n)

    Memoized Fibonacci:
        Time: O(n)
        Map: O(n)
        Stack: O(n)

Memory is intentionally used to reduce repeated work.
`);
}


// ============================================================================
// 12. SPACE-OPTIMIZED DYNAMIC PROGRAMMING
// ============================================================================

function fibonacciWithArray(n) {
    if (n <= 1) {
        return n;
    }

    const dp = new Array(n + 1);
    dp[0] = 0;
    dp[1] = 1;

    for (let index = 2; index <= n; index++) {
        dp[index] = dp[index - 1] + dp[index - 2];
    }

    return dp[n];
}

function fibonacciSpaceOptimized(n) {
    if (n <= 1) {
        return n;
    }

    let previousTwo = 0;
    let previousOne = 1;

    for (let index = 2; index <= n; index++) {
        const current = previousTwo + previousOne;
        previousTwo = previousOne;
        previousOne = current;
    }

    return previousOne;
}

function demonstrateSpaceOptimizedDP() {
    printSection("12. SPACE-OPTIMIZED DYNAMIC PROGRAMMING");

    const n = 30;

    console.log(
        "Array DP:",
        fibonacciWithArray(n)
    );

    console.log(
        "Space-optimized DP:",
        fibonacciSpaceOptimized(n)
    );

    console.log(`
Array DP:

    Time: O(n)
    Space: O(n)

Optimized DP:

    Time: O(n)
    Space: O(1)

The optimization is possible because each Fibonacci state only needs the
previous two states.
`);
}


// ============================================================================
// 13. STREAMING AND BOUNDED MEMORY
// ============================================================================

function runningMaximum(numbers) {
    let maximum = undefined;

    for (const number of numbers) {
        if (maximum === undefined || number > maximum) {
            maximum = number;
        }
    }

    return maximum;
}

function demonstrateStreamingIdea() {
    printSection("13. STREAMING AND BOUNDED MEMORY");

    const numbers = [7, 2, 15, 4, 11];

    console.log("Running maximum:", runningMaximum(numbers));

    console.log(`
A streaming algorithm processes input one item at a time and retains only
the state required to continue the computation.

For a maximum operation:

    State = current maximum

Therefore the working memory can remain O(1), even when the conceptual input
contains millions of values.

Real applications can extend this idea to files, network streams, logs,
events, and database result streams.
`);
}


// ============================================================================
// 14. EDGE CASES AND VALIDATION
// ============================================================================

function demonstrateEdgeCases() {
    printSection("14. EDGE CASES");

    const cases = [
        [],
        [1],
        [5, 5, 5],
        [-10, -3, -20],
    ];

    for (const numbers of cases) {
        console.log(
            "Input:",
            numbers,
            "Maximum:",
            findMaximumWithConstantSpace(numbers)
        );
    }

    console.log(`
Important edge cases include:

    n = 0
    n = 1
    duplicate values
    all unique values
    negative values
    very long strings
    extremely large collections
    deep recursion

For a Set or Map, the worst case can occur when all values are distinct.

For recursion, sufficiently large depth can cause a runtime stack failure.
`);
}


// ============================================================================
// 15. GARBAGE COLLECTION AND MEMORY RETENTION
// ============================================================================

function demonstrateObjectLifetime() {
    printSection("15. OBJECT LIFETIME AND MEMORY RETENTION");

    let largeTemporaryStructure = new Array(100000).fill(42);

    console.log(
        "Created structure with length:",
        largeTemporaryStructure.length
    );

    // Removing the reference makes the object eligible for garbage collection
    // when no other references exist.
    largeTemporaryStructure = null;

    console.log(
        "Reference removed. The runtime may reclaim the memory later."
    );

    console.log(`
JavaScript uses automatic memory management.

Setting a variable to null does not force immediate garbage collection.

It can, though, remove one reference to an object.

Practical memory problems can occur when a program unintentionally keeps
references to objects through:

    - global variables
    - long-lived arrays
    - caches
    - event listeners
    - closures
    - queues
    - maps

Space analysis should consider how long objects remain reachable.
`);
}


// ============================================================================
// 16. CACHES AND UNBOUNDED SPACE
// ============================================================================

class SimpleCache {
    constructor() {
        this.values = new Map();
    }

    set(key, value) {
        this.values.set(key, value);
    }

    get(key) {
        return this.values.get(key);
    }

    size() {
        return this.values.size;
    }
}

function demonstrateCacheSpace() {
    printSection("16. CACHES AND UNBOUNDED SPACE");

    const cache = new SimpleCache();

    for (let index = 0; index < 5; index++) {
        cache.set(`key-${index}`, index * index);
    }

    console.log("Cache entries:", cache.size());

    console.log(`
A cache improves performance by retaining previous results.

Its space usage may be:

    O(k)

where k is the number of retained entries.

An unbounded cache can become a production memory problem.

Real systems often use:

    - maximum entry counts
    - expiration
    - least-recently-used policies
    - size limits
    - eviction strategies
`);
}


// ============================================================================
// 17. PERFORMANCE MEASUREMENT
// ============================================================================

function measureMemorySnapshot(label) {
    if (typeof process === "undefined" || !process.memoryUsage) {
        console.log(`${label}: runtime memory API unavailable.`);
        return;
    }

    const memory = process.memoryUsage();

    console.log(label, {
        heapUsedBytes: memory.heapUsed,
        heapTotalBytes: memory.heapTotal,
        externalBytes: memory.external,
        arrayBuffersBytes: memory.arrayBuffers
    });
}

function demonstrateRuntimeMeasurement() {
    printSection("17. RUNTIME MEMORY MEASUREMENT");

    measureMemorySnapshot("Before allocation:");

    const temporary = new Array(50000).fill("data");

    measureMemorySnapshot("After allocation:");

    // Keep the example deterministic while making the lifetime explicit.
    console.log("Temporary structure length:", temporary.length);

    console.log(`
Theoretical analysis tells us that an array with n stored elements is O(n).

Runtime memory measurement tells us the actual memory behavior of a particular
JavaScript runtime and implementation.

Both perspectives are useful:

    Big-O -> growth behavior
    Measurement -> concrete runtime behavior
`);
}


// ============================================================================
// 18. PRACTICAL SPACE-ANALYSIS CHECKLIST
// ============================================================================

function printAnalysisChecklist() {
    printSection("18. PRACTICAL SPACE-ANALYSIS CHECKLIST");

    console.log(`
1. Identify the input.
2. Separate input storage from newly allocated storage.
3. Count scalar variables.
4. Find arrays, objects, Maps, Sets, queues, and stacks.
5. Check whether those structures grow with n.
6. Check whether temporary copies are created.
7. Check string operations.
8. Count recursive call depth.
9. Determine whether output space is counted separately.
10. Identify the largest simultaneously live structure.
11. Express the growth using Big-O.
12. Look for a possible time-space trade-off.
13. Consider worst-case input.
14. Consider practical memory limits.
15. For production systems, consider object lifetime and unbounded retention.
`);
}


// ============================================================================
// 19. SELF-TEST
// ============================================================================

function runSelfTest() {
    printSection("19. SELF-TEST");

    console.assert(factorialIterative(6) === 720);
    console.assert(factorialRecursive(6) === 720);

    console.assert(iterativeSum([1, 2, 3, 4]) === 10);
    console.assert(recursiveSum([1, 2, 3, 4]) === 10);

    console.assert(
        JSON.stringify(reverseInPlace([1, 2, 3])) ===
        JSON.stringify([3, 2, 1])
    );

    console.assert(containsDuplicateUsingSet([1, 2, 1]) === true);
    console.assert(containsDuplicateUsingSet([1, 2, 3]) === false);

    console.assert(containsDuplicateBruteForce([1, 2, 1]) === true);
    console.assert(containsDuplicateBruteForce([1, 2, 3]) === false);

    const frequency = frequencyCount([1, 1, 2]);
    console.assert(frequency.get(1) === 2);
    console.assert(frequency.get(2) === 1);

    console.assert(isPalindromeConstantAuxiliary("racecar") === true);
    console.assert(isPalindromeConstantAuxiliary("javascript") === false);

    console.assert(
        maximumFixedWindowSum([2, 1, 5, 1, 3, 2], 3) === 9
    );

    console.assert(fibonacciWithArray(10) === 55);
    console.assert(fibonacciSpaceOptimized(10) === 55);

    console.log("All self-tests passed.");
}


// ============================================================================
// 20. MAIN
// ============================================================================

function main() {
    console.log("=".repeat(78));
    console.log("DAY 8 — SPACE COMPLEXITY");
    console.log("=".repeat(78));

    explainSpaceComplexity();
    demonstrateConstantSpace();
    demonstrateArrays();
    demonstrateInPlaceAlgorithm();
    demonstrateRecursion();
    demonstrateStrings();
    demonstrateSetTradeoff();
    demonstrateMapSpace();
    demonstrateMatrixSpace();
    demonstrateSlidingWindow();
    demonstrateMemoization();
    demonstrateSpaceOptimizedDP();
    demonstrateStreamingIdea();
    demonstrateEdgeCases();
    demonstrateObjectLifetime();
    demonstrateCacheSpace();
    demonstrateRuntimeMeasurement();
    printAnalysisChecklist();
    runSelfTest();

    console.log("\n" + "=".repeat(78));
    console.log("END OF DAY 8 — SPACE COMPLEXITY");
    console.log("=".repeat(78));
}

main();
