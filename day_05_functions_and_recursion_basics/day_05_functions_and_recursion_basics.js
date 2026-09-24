/*
 * Day 5 — Functions and Recursion Basics
 *
 * Topics:
 * - Function declarations
 * - Parameters and arguments
 * - Return values
 * - Local scope
 * - Function composition
 * - Iteration versus recursion
 * - Base cases
 * - Recursive calls
 * - Call stack
 * - Factorial
 * - Fibonacci
 * - Power
 * - Greatest common divisor
 * - Sum of digits
 * - Recursive countdown
 * - Recursive array traversal
 * - Memoization
 * - Recursive search and sorting
 * - Tree traversal
 * - Error handling
 * - Performance considerations
 *
 * This file runs in modern Node.js without external packages.
 */


// ============================================================================
// 1. FUNCTION DECLARATIONS
// ============================================================================

function greet(name) {
    return `Hello, ${name}!`;
}

function add(firstNumber, secondNumber) {
    return firstNumber + secondNumber;
}

function multiply(firstNumber, secondNumber) {
    return firstNumber * secondNumber;
}

function demonstrateBasicFunctions() {
    console.log("\n=== 1. FUNCTION DECLARATIONS ===");

    console.log(greet("Atul"));
    console.log("10 + 20 =", add(10, 20));
    console.log("6 × 7 =", multiply(6, 7));
}


// ============================================================================
// 2. PARAMETERS, ARGUMENTS, AND DEFAULT PARAMETERS
// ============================================================================

function describePerson(name, age, country = "India") {
    return `${name} is ${age} years old and lives in ${country}.`;
}

function calculateRectangleArea(length, width) {
    if (!Number.isFinite(length) || !Number.isFinite(width)) {
        throw new TypeError("Length and width must be finite numbers.");
    }

    if (length < 0 || width < 0) {
        throw new RangeError("Length and width cannot be negative.");
    }

    return length * width;
}

function demonstrateParameters() {
    console.log("\n=== 2. PARAMETERS AND ARGUMENTS ===");

    console.log(describePerson("Atul", 25));
    console.log(describePerson("Atul", 25, "India"));
    console.log("Rectangle area:", calculateRectangleArea(10, 5));
}


// ============================================================================
// 3. RETURN VALUES
// ============================================================================

function divide(dividend, divisor) {
    if (divisor === 0) {
        throw new RangeError("Division by zero is not allowed.");
    }

    return dividend / divisor;
}

function square(number) {
    return number * number;
}

function demonstrateReturnValues() {
    console.log("\n=== 3. RETURN VALUES ===");

    console.log("20 / 4 =", divide(20, 4));
    console.log("8² =", square(8));

    try {
        divide(10, 0);
    } catch (error) {
        console.log("Handled error:", error.message);
    }
}


// ============================================================================
// 4. LOCAL SCOPE
// ============================================================================

const globalDemoValue = "global value";

function scopeExample() {
    const localDemoValue = "local value";
    return localDemoValue;
}

function demonstrateScope() {
    console.log("\n=== 4. LOCAL SCOPE ===");

    console.log("Global value:", globalDemoValue);
    console.log("Local value returned from function:", scopeExample());

    // localDemoValue does not exist here because const creates block scope.
}


// ============================================================================
// 5. FUNCTION COMPOSITION
// ============================================================================

function double(number) {
    return number * 2;
}

function increment(number) {
    return number + 1;
}

function doubleThenIncrement(number) {
    const doubled = double(number);
    return increment(doubled);
}

function normalizeScore(score) {
    return Math.max(0, Math.min(100, score));
}

function calculatePercentage(obtained, maximum) {
    if (maximum <= 0) {
        throw new RangeError("Maximum must be greater than zero.");
    }

    return normalizeScore((obtained / maximum) * 100);
}

function demonstrateFunctionComposition() {
    console.log("\n=== 5. FUNCTION COMPOSITION ===");

    console.log("doubleThenIncrement(5):", doubleThenIncrement(5));
    console.log("Percentage:", calculatePercentage(72, 100));
}


// ============================================================================
// 6. ITERATION VERSUS RECURSION
// ============================================================================

function factorialIterative(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError("Factorial requires a non-negative integer.");
    }

    let result = 1;

    for (let current = 2; current <= number; current += 1) {
        result *= current;
    }

    return result;
}

function factorialRecursive(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError("Factorial requires a non-negative integer.");
    }

    // Base case: recursion stops at zero.
    if (number === 0) {
        return 1;
    }

    // Recursive case: the problem becomes smaller.
    return number * factorialRecursive(number - 1);
}

function demonstrateIterationVsRecursion() {
    console.log("\n=== 6. ITERATION VERSUS RECURSION ===");

    for (let value = 0; value <= 5; value += 1) {
        console.log(
            `${value}! -> iterative=${factorialIterative(value)}, ` +
            `recursive=${factorialRecursive(value)}`
        );
    }
}


// ============================================================================
// 7. RECURSIVE COUNTDOWN AND CALL STACK
// ============================================================================

function countdown(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError("Countdown requires a non-negative integer.");
    }

    // Base case.
    if (number === 0) {
        console.log("0 -> base case reached");
        return;
    }

    console.log(
        `${number} -> recursive call to countdown(${number - 1})`
    );

    // The current function call remains active while this call executes.
    countdown(number - 1);
}

function demonstrateCallStack() {
    console.log("\n=== 7. CALL STACK ===");
    countdown(5);
}


// ============================================================================
// 8. POWER CALCULATION
// ============================================================================

function powerRecursive(base, exponent) {
    if (!Number.isInteger(exponent)) {
        throw new TypeError("Exponent must be an integer.");
    }

    if (base === 0 && exponent < 0) {
        throw new RangeError("Zero cannot have a negative exponent.");
    }

    // Base case.
    if (exponent === 0) {
        return 1;
    }

    if (exponent < 0) {
        return 1 / powerRecursive(base, -exponent);
    }

    // Exponentiation by squaring reduces the recursion depth.
    const halfPower = powerRecursive(base, Math.floor(exponent / 2));

    if (exponent % 2 === 0) {
        return halfPower * halfPower;
    }

    return base * halfPower * halfPower;
}

function demonstratePower() {
    console.log("\n=== 8. RECURSIVE POWER ===");

    for (const [base, exponent] of [
        [2, 0],
        [2, 5],
        [3, 4],
        [10, 3],
        [2, -3]
    ]) {
        console.log(
            `${base}^${exponent} =`,
            powerRecursive(base, exponent)
        );
    }
}


// ============================================================================
// 9. GREATEST COMMON DIVISOR
// ============================================================================

function gcdRecursive(first, second) {
    first = Math.abs(first);
    second = Math.abs(second);

    // Base case for Euclid's algorithm.
    if (second === 0) {
        return first;
    }

    return gcdRecursive(second, first % second);
}

function gcdIterative(first, second) {
    first = Math.abs(first);
    second = Math.abs(second);

    while (second !== 0) {
        [first, second] = [second, first % second];
    }

    return first;
}

function demonstrateGcd() {
    console.log("\n=== 9. GREATEST COMMON DIVISOR ===");

    for (const [first, second] of [
        [48, 18],
        [100, 35],
        [17, 13],
        [0, 15],
        [-48, 18]
    ]) {
        console.log(
            `gcd(${first}, ${second}) =`,
            gcdRecursive(first, second)
        );
    }
}


// ============================================================================
// 10. SUM OF DIGITS
// ============================================================================

function sumOfDigits(number) {
    number = Math.abs(Math.trunc(number));

    // Base case: a single digit needs no further decomposition.
    if (number < 10) {
        return number;
    }

    return (number % 10) + sumOfDigits(Math.floor(number / 10));
}

function demonstrateSumOfDigits() {
    console.log("\n=== 10. SUM OF DIGITS ===");

    for (const number of [0, 5, 123, 9876, -54321]) {
        console.log(
            `sumOfDigits(${number}) =`,
            sumOfDigits(number)
        );
    }
}


// ============================================================================
// 11. FIBONACCI
// ============================================================================

function fibonacciRecursive(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError(
            "Fibonacci requires a non-negative integer."
        );
    }

    if (number <= 1) {
        return number;
    }

    return (
        fibonacciRecursive(number - 1) +
        fibonacciRecursive(number - 2)
    );
}

const fibonacciMemoized = (() => {
    const cache = new Map([
        [0, 0],
        [1, 1]
    ]);

    function fibonacci(number) {
        if (!Number.isInteger(number) || number < 0) {
            throw new RangeError(
                "Fibonacci requires a non-negative integer."
            );
        }

        if (cache.has(number)) {
            return cache.get(number);
        }

        const result =
            fibonacci(number - 1) +
            fibonacci(number - 2);

        cache.set(number, result);
        return result;
    }

    return fibonacci;
})();

function fibonacciIterative(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError(
            "Fibonacci requires a non-negative integer."
        );
    }

    let first = 0;
    let second = 1;

    for (let index = 0; index < number; index += 1) {
        [first, second] = [second, first + second];
    }

    return first;
}

function demonstrateFibonacci() {
    console.log("\n=== 11. FIBONACCI ===");

    const firstValues = [];

    for (let index = 0; index < 12; index += 1) {
        firstValues.push(fibonacciRecursive(index));
    }

    console.log("First 12 values:", firstValues);
    console.log("Memoized F(40):", fibonacciMemoized(40));
    console.log("Iterative F(40):", fibonacciIterative(40));
}


// ============================================================================
// 12. RECURSIVE ARRAY TRAVERSAL
// ============================================================================

function recursiveArrayTraversal(values, index = 0) {
    // Base case: all elements have been visited.
    if (index >= values.length) {
        return;
    }

    console.log(`index=${index}, value=${values[index]}`);

    recursiveArrayTraversal(values, index + 1);
}

function recursiveArraySum(values, index = 0) {
    if (index >= values.length) {
        return 0;
    }

    return values[index] + recursiveArraySum(values, index + 1);
}

function recursiveArrayMaximum(values, index = 0) {
    if (values.length === 0) {
        throw new RangeError("Cannot find maximum of an empty array.");
    }

    if (index === values.length - 1) {
        return values[index];
    }

    return Math.max(
        values[index],
        recursiveArrayMaximum(values, index + 1)
    );
}

function demonstrateRecursiveArrays() {
    console.log("\n=== 12. RECURSIVE ARRAY TRAVERSAL ===");

    const values = [4, 8, 15, 16, 23, 42];

    recursiveArrayTraversal(values);
    console.log("Recursive sum:", recursiveArraySum(values));
    console.log("Recursive maximum:", recursiveArrayMaximum(values));
}


// ============================================================================
// 13. RECURSIVE STRING PROCESSING
// ============================================================================

function reverseStringRecursive(text) {
    if (text.length <= 1) {
        return text;
    }

    return (
        text[text.length - 1] +
        reverseStringRecursive(text.slice(0, -1))
    );
}

function isPalindromeRecursive(text) {
    const normalized = text
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "");

    if (normalized.length <= 1) {
        return true;
    }

    if (normalized[0] !== normalized[normalized.length - 1]) {
        return false;
    }

    return isPalindromeRecursive(
        normalized.slice(1, -1)
    );
}

function demonstrateRecursiveStrings() {
    console.log("\n=== 13. RECURSIVE STRINGS ===");

    for (const text of ["recursion", "level", "radar", "JavaScript"]) {
        console.log(
            `reverse(${JSON.stringify(text)}) =`,
            reverseStringRecursive(text)
        );

        console.log(
            `palindrome(${JSON.stringify(text)}) =`,
            isPalindromeRecursive(text)
        );
    }
}


// ============================================================================
// 14. RECURSIVE BINARY SEARCH
// ============================================================================

function binarySearchRecursive(
    sortedValues,
    target,
    left = 0,
    right = sortedValues.length - 1
) {
    if (left > right) {
        return -1;
    }

    const middle = left + Math.floor((right - left) / 2);

    if (sortedValues[middle] === target) {
        return middle;
    }

    if (target < sortedValues[middle]) {
        return binarySearchRecursive(
            sortedValues,
            target,
            left,
            middle - 1
        );
    }

    return binarySearchRecursive(
        sortedValues,
        target,
        middle + 1,
        right
    );
}

function demonstrateBinarySearch() {
    console.log("\n=== 14. RECURSIVE BINARY SEARCH ===");

    const values = [3, 7, 11, 18, 21, 27, 35, 42];

    for (const target of [3, 21, 42, 100]) {
        console.log(
            `Search ${target}:`,
            binarySearchRecursive(values, target)
        );
    }
}


// ============================================================================
// 15. RECURSIVE MERGE SORT
// ============================================================================

function merge(left, right) {
    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    while (
        leftIndex < left.length &&
        rightIndex < right.length
    ) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push(left[leftIndex]);
            leftIndex += 1;
        } else {
            result.push(right[rightIndex]);
            rightIndex += 1;
        }
    }

    result.push(...left.slice(leftIndex));
    result.push(...right.slice(rightIndex));

    return result;
}

function mergeSortRecursive(values) {
    if (values.length <= 1) {
        return [...values];
    }

    const middle = Math.floor(values.length / 2);

    const left = mergeSortRecursive(
        values.slice(0, middle)
    );

    const right = mergeSortRecursive(
        values.slice(middle)
    );

    return merge(left, right);
}

function demonstrateMergeSort() {
    console.log("\n=== 15. RECURSIVE MERGE SORT ===");

    const values = [38, 27, 43, 3, 9, 82, 10];

    console.log("Original:", values);
    console.log("Sorted:", mergeSortRecursive(values));
}


// ============================================================================
// 16. TREE RECURSION
// ============================================================================

class TreeNode {
    constructor(value, left = null, right = null) {
        this.value = value;
        this.left = left;
        this.right = right;
    }
}

function inorderTraversal(node, result = []) {
    if (node === null) {
        return result;
    }

    inorderTraversal(node.left, result);
    result.push(node.value);
    inorderTraversal(node.right, result);

    return result;
}

function demonstrateTreeRecursion() {
    console.log("\n=== 16. TREE RECURSION ===");

    const tree = new TreeNode(
        10,
        new TreeNode(
            5,
            new TreeNode(2),
            new TreeNode(7)
        ),
        new TreeNode(
            15,
            new TreeNode(12),
            new TreeNode(20)
        )
    );

    console.log("In-order traversal:", inorderTraversal(tree));
}


// ============================================================================
// 17. BRANCHING RECURSION
// ============================================================================

function countPaths(rows, columns) {
    if (rows <= 0 || columns <= 0) {
        return 0;
    }

    if (rows === 1 || columns === 1) {
        return 1;
    }

    return (
        countPaths(rows - 1, columns) +
        countPaths(rows, columns - 1)
    );
}

const countPathsMemoized = (() => {
    const cache = new Map();

    function calculate(rows, columns) {
        const key = `${rows},${columns}`;

        if (cache.has(key)) {
            return cache.get(key);
        }

        if (rows <= 0 || columns <= 0) {
            return 0;
        }

        if (rows === 1 || columns === 1) {
            return 1;
        }

        const result =
            calculate(rows - 1, columns) +
            calculate(rows, columns - 1);

        cache.set(key, result);
        return result;
    }

    return calculate;
})();

function demonstrateBranchingRecursion() {
    console.log("\n=== 17. BRANCHING RECURSION ===");

    console.log("3×3 grid paths:", countPaths(3, 3));
    console.log(
        "10×10 grid paths with memoization:",
        countPathsMemoized(10, 10)
    );
}


// ============================================================================
// 18. PRACTICAL FUNCTION PIPELINE
// ============================================================================

function cleanNumber(value) {
    const cleaned = String(value).trim();

    if (cleaned.length === 0) {
        throw new Error("Input cannot be empty.");
    }

    const number = Number(cleaned);

    if (!Number.isInteger(number)) {
        throw new TypeError("Input must be an integer.");
    }

    return number;
}

function computeDigitSum(value) {
    const number = cleanNumber(value);
    return sumOfDigits(number);
}

function classifyDigitSum(value) {
    const digitSum = computeDigitSum(value);

    if (digitSum === 0) {
        return "zero";
    }

    return digitSum % 2 === 0
        ? "even digit sum"
        : "odd digit sum";
}

function demonstrateFunctionPipeline() {
    console.log("\n=== 18. FUNCTION PIPELINE ===");

    for (const value of ["12345", "2468", "0"]) {
        console.log(
            `${value}: digit sum=${computeDigitSum(value)}, ` +
            `classification=${classifyDigitSum(value)}`
        );
    }
}


// ============================================================================
// 19. PERFORMANCE MEASUREMENT
// ============================================================================

function measureFunction(functionToMeasure, argument) {
    const start = performance.now();
    const result = functionToMeasure(argument);
    const elapsedMilliseconds = performance.now() - start;

    return {
        result,
        elapsedMilliseconds
    };
}

function demonstratePerformance() {
    console.log("\n=== 19. PERFORMANCE ===");

    const number = 30;

    const recursive = measureFunction(
        fibonacciRecursive,
        number
    );

    const memoized = measureFunction(
        fibonacciMemoized,
        number
    );

    const iterative = measureFunction(
        fibonacciIterative,
        number
    );

    console.log(
        `Naive recursion: ${recursive.elapsedMilliseconds.toFixed(4)} ms`
    );

    console.log(
        `Memoization: ${memoized.elapsedMilliseconds.toFixed(4)} ms`
    );

    console.log(
        `Iteration: ${iterative.elapsedMilliseconds.toFixed(4)} ms`
    );
}


// ============================================================================
// 20. TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    console.log("\n=== 20. TESTS ===");

    assert(add(2, 3) === 5, "addition");
    assert(multiply(4, 5) === 20, "multiplication");

    assert(factorialRecursive(0) === 1, "factorial zero");
    assert(factorialRecursive(5) === 120, "factorial five");

    assert(powerRecursive(2, 10) === 1024, "power");
    assert(powerRecursive(2, -2) === 0.25, "negative exponent");

    assert(gcdRecursive(48, 18) === 6, "GCD");

    assert(sumOfDigits(12345) === 15, "digit sum");

    assert(fibonacciIterative(10) === 55, "iterative Fibonacci");
    assert(fibonacciMemoized(10) === 55, "memoized Fibonacci");

    assert(
        recursiveArraySum([1, 2, 3, 4]) === 10,
        "recursive array sum"
    );

    assert(
        recursiveArrayMaximum([8, 2, 10, 4]) === 10,
        "recursive maximum"
    );

    assert(
        reverseStringRecursive("abc") === "cba",
        "reverse string"
    );

    assert(
        isPalindromeRecursive("Level") === true,
        "palindrome"
    );

    assert(
        binarySearchRecursive([1, 3, 5, 7], 5) === 2,
        "binary search"
    );

    assert(
        binarySearchRecursive([1, 3, 5, 7], 6) === -1,
        "missing binary-search value"
    );

    assert(
        JSON.stringify(mergeSortRecursive([5, 1, 4, 2, 3])) ===
        JSON.stringify([1, 2, 3, 4, 5]),
        "merge sort"
    );

    assert(
        countPathsMemoized(3, 3) === 6,
        "grid paths"
    );

    console.log("All tests passed.");
}


// ============================================================================
// 21. MAIN
// ============================================================================

function main() {
    console.log("=".repeat(78));
    console.log("DAY 5 — FUNCTIONS AND RECURSION BASICS");
    console.log("=".repeat(78));

    demonstrateBasicFunctions();
    demonstrateParameters();
    demonstrateReturnValues();
    demonstrateScope();
    demonstrateFunctionComposition();
    demonstrateIterationVsRecursion();
    demonstrateCallStack();
    demonstratePower();
    demonstrateGcd();
    demonstrateSumOfDigits();
    demonstrateFibonacci();
    demonstrateRecursiveArrays();
    demonstrateRecursiveStrings();
    demonstrateBinarySearch();
    demonstrateMergeSort();
    demonstrateTreeRecursion();
    demonstrateBranchingRecursion();
    demonstrateFunctionPipeline();
    demonstratePerformance();
    runTests();

    console.log("\n" + "=".repeat(78));
    console.log("DAY 5 STUDY PROGRAM COMPLETED");
    console.log("=".repeat(78));
}

main();
