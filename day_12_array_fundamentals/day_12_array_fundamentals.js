/*
 * Day 12 — Array Fundamentals
 * ============================
 *
 * Topics:
 *   - Indexing
 *   - Traversal
 *   - Updating
 *   - Searching
 *   - Minimum / maximum
 *   - Frequency counting
 *   - Maximum element
 *   - Minimum element
 *   - Second-largest element
 *   - Reverse array
 *   - Rotate array
 *   - Remove duplicates
 *   - Count positive / negative values
 *   - Find missing values
 *
 * This file uses JavaScript arrays to demonstrate fundamental and advanced
 * array-processing techniques in a standalone executable program.
 *
 * It can run with:
 *   node day12_array_fundamentals.js
 */

"use strict";

// ============================================================================
// 1. UTILITY FUNCTIONS
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

// ============================================================================
// 2. ARRAY CREATION AND INDEXING
// ============================================================================

function demonstrateCreationAndIndexing() {
    section("1. Array creation and indexing");

    const numbers = [10, 20, 30, 40, 50];

    console.log("Array:", numbers);
    console.log("Length:", numbers.length);

    // JavaScript arrays use zero-based indexing.
    console.log("First element:", numbers[0]);
    console.log("Third element:", numbers[2]);
    console.log("Last element:", numbers[numbers.length - 1]);

    // Unlike Python, JavaScript does not use negative indexes with [].
    // Modern JavaScript provides at() for negative indexing.
    console.log("Last element using at(-1):", numbers.at(-1));
    console.log("Second-last using at(-2):", numbers.at(-2));

    console.log("Slice:", numbers.slice(1, 4));
}

// ============================================================================
// 3. TRAVERSAL
// ============================================================================

function demonstrateTraversal() {
    section("2. Traversal");

    const values = [4, 8, 15, 16, 23, 42];

    subsection("Traditional index traversal");

    for (let index = 0; index < values.length; index++) {
        console.log(`index=${index}, value=${values[index]}`);
    }

    subsection("for...of traversal");

    for (const value of values) {
        console.log(value);
    }

    subsection("forEach traversal");

    values.forEach((value, index) => {
        console.log(`index=${index}, value=${value}`);
    });

    // Traversing n elements takes O(n) time.
}

// ============================================================================
// 4. UPDATING
// ============================================================================

function demonstrateUpdating() {
    section("3. Updating elements");

    const values = [10, 20, 30, 40, 50];

    console.log("Before:", values);

    // Direct access by index is O(1).
    values[2] = 999;

    console.log("After values[2] = 999:", values);

    // Updating every element requires O(n) traversal.
    for (let index = 0; index < values.length; index++) {
        values[index] *= 2;
    }

    console.log("After doubling:", values);

    // map() returns a new array.
    const incremented = values.map(value => value + 1);
    console.log("New array after adding 1:", incremented);
}

// ============================================================================
// 5. LINEAR SEARCH
// ============================================================================

function linearSearch(values, target) {
    for (let index = 0; index < values.length; index++) {
        if (values[index] === target) {
            return index;
        }
    }

    return -1;
}

function demonstrateSearching() {
    section("4. Searching");

    const values = [17, 4, 29, 8, 31, 12];

    for (const target of [29, 100, 17]) {
        const index = linearSearch(values, target);

        if (index === -1) {
            console.log(`${target} was not found`);
        } else {
            console.log(`${target} found at index ${index}`);
        }
    }

    // includes() answers a membership question directly.
    console.log("31 exists:", values.includes(31));
    console.log("100 exists:", values.includes(100));

    // indexOf() returns the first matching index or -1.
    console.log("Index of 8:", values.indexOf(8));
}

// ============================================================================
// 6. MINIMUM AND MAXIMUM
// ============================================================================

function manualMinimum(values) {
    if (values.length === 0) {
        throw new Error("Cannot find minimum of an empty array");
    }

    let smallest = values[0];

    for (let index = 1; index < values.length; index++) {
        if (values[index] < smallest) {
            smallest = values[index];
        }
    }

    return smallest;
}

function manualMaximum(values) {
    if (values.length === 0) {
        throw new Error("Cannot find maximum of an empty array");
    }

    let largest = values[0];

    for (let index = 1; index < values.length; index++) {
        if (values[index] > largest) {
            largest = values[index];
        }
    }

    return largest;
}

function demonstrateMinimumMaximum() {
    section("5. Minimum and maximum");

    const values = [34, 7, 91, 23, 56, 12];

    console.log("Array:", values);
    console.log("Manual minimum:", manualMinimum(values));
    console.log("Manual maximum:", manualMaximum(values));

    // Math.min and Math.max can be convenient for small arrays.
    console.log("Built-in minimum:", Math.min(...values));
    console.log("Built-in maximum:", Math.max(...values));

    try {
        manualMinimum([]);
    } catch (error) {
        console.log("Empty-array error handled:", error.message);
    }
}

// ============================================================================
// 7. FREQUENCY COUNTING
// ============================================================================

function frequencyCount(values) {
    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
    }

    return frequencies;
}

function mapToObject(map) {
    return Object.fromEntries(map.entries());
}

function demonstrateFrequencyCounting() {
    section("6. Frequency counting");

    const values = [2, 5, 2, 8, 5, 2, 9, 8, 8];

    const frequencies = frequencyCount(values);

    console.log("Array:", values);
    console.log("Frequency table:", mapToObject(frequencies));
    console.log("Frequency of 2:", frequencies.get(2) ?? 0);
    console.log("Frequency of 100:", frequencies.get(100) ?? 0);
}

// ============================================================================
// 8. SECOND-LARGEST DISTINCT VALUE
// ============================================================================

function secondLargestDistinct(values) {
    let largest = null;
    let secondLargest = null;

    for (const value of values) {
        if (largest === null || value > largest) {
            secondLargest = largest;
            largest = value;
        } else if (
            value !== largest &&
            (secondLargest === null || value > secondLargest)
        ) {
            secondLargest = value;
        }
    }

    return secondLargest;
}

function demonstrateSecondLargest() {
    section("7. Second-largest distinct element");

    const testCases = [
        [10, 20, 5, 8, 30],
        [30, 30, 20, 10],
        [5, 5, 5],
        [-10, -20, -3, -7],
        [1],
        []
    ];

    for (const values of testCases) {
        console.log(
            values,
            "=>",
            secondLargestDistinct(values)
        );
    }
}

// ============================================================================
// 9. REVERSE ARRAY
// ============================================================================

function reverseInPlace(values) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        [values[left], values[right]] = [values[right], values[left]];
        left++;
        right--;
    }

    return values;
}

function demonstrateReverse() {
    section("8. Reverse array");

    const values = [1, 2, 3, 4, 5, 6];

    console.log("Before:", values);
    reverseInPlace(values);
    console.log("After:", values);

    const original = [1, 2, 3, 4];
    const reversedCopy = [...original].reverse();

    console.log("Original:", original);
    console.log("Reversed copy:", reversedCopy);
}

// ============================================================================
// 10. ROTATION
// ============================================================================

function rotateRight(values, k) {
    if (values.length === 0) {
        return [];
    }

    // JavaScript's remainder operator can produce negative values.
    k = ((k % values.length) + values.length) % values.length;

    if (k === 0) {
        return [...values];
    }

    return [
        ...values.slice(-k),
        ...values.slice(0, -k)
    ];
}

function rotateRightInPlace(values, k) {
    if (values.length === 0) {
        return values;
    }

    k = ((k % values.length) + values.length) % values.length;

    if (k === 0) {
        return values;
    }

    function reverseRange(start, end) {
        while (start < end) {
            [values[start], values[end]] = [values[end], values[start]];
            start++;
            end--;
        }
    }

    reverseRange(0, values.length - 1);
    reverseRange(0, k - 1);
    reverseRange(k, values.length - 1);

    return values;
}

function demonstrateRotation() {
    section("9. Rotate array");

    const values = [1, 2, 3, 4, 5];

    for (const k of [0, 1, 2, 5, 7, -1]) {
        console.log(`Rotate right by ${k}:`, rotateRight(values, k));
    }

    const inPlace = [1, 2, 3, 4, 5];
    rotateRightInPlace(inPlace, 2);
    console.log("In-place rotation by 2:", inPlace);
}

// ============================================================================
// 11. REMOVE DUPLICATES
// ============================================================================

function removeDuplicatesPreserveOrder(values) {
    const seen = new Set();
    const result = [];

    for (const value of values) {
        if (!seen.has(value)) {
            seen.add(value);
            result.push(value);
        }
    }

    return result;
}

function demonstrateRemoveDuplicates() {
    section("10. Remove duplicates");

    const values = [4, 2, 4, 7, 2, 9, 7, 1];

    console.log("Original:", values);
    console.log(
        "Unique preserving order:",
        removeDuplicatesPreserveOrder(values)
    );

    // Set is a natural JavaScript data structure for unique values.
    console.log("Using Set:", [...new Set(values)]);
}

// ============================================================================
// 12. COUNT POSITIVE, NEGATIVE, ZERO
// ============================================================================

function countSigns(values) {
    let positive = 0;
    let negative = 0;
    let zero = 0;

    for (const value of values) {
        if (value > 0) {
            positive++;
        } else if (value < 0) {
            negative++;
        } else {
            zero++;
        }
    }

    return { positive, negative, zero };
}

function demonstrateSignCounting() {
    section("11. Count positive, negative, and zero values");

    const values = [-5, 0, 8, -2, 7, 0, -10, 4];

    console.log("Array:", values);
    console.log("Counts:", countSigns(values));
}

// ============================================================================
// 13. FIND MISSING VALUES
// ============================================================================

function findMissingValues(values, start, end) {
    const present = new Set(values);
    const missing = [];

    for (let number = start; number <= end; number++) {
        if (!present.has(number)) {
            missing.push(number);
        }
    }

    return missing;
}

function missingSingleValueXor(values, n) {
    if (values.length !== n) {
        return null;
    }

    let missing = n;

    for (let index = 0; index < values.length; index++) {
        missing ^= index;
        missing ^= values[index];
    }

    return missing;
}

function demonstrateMissingValues() {
    section("12. Find missing values");

    const values = [1, 2, 4, 6, 7, 9];

    console.log(
        "Missing from 1..9:",
        findMissingValues(values, 1, 9)
    );

    const singleMissing = [3, 0, 1];

    console.log(
        "Missing from 0..3:",
        missingSingleValueXor(singleMissing, 3)
    );
}

// ============================================================================
// 14. SORTED ARRAY AND BINARY SEARCH
// ============================================================================

function binarySearch(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        // This form avoids unnecessary overflow in fixed-width integer
        // languages such as C++.
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function demonstrateBinarySearch() {
    section("13. Binary search");

    const values = [3, 8, 12, 19, 24, 31, 45, 50];

    for (const target of [3, 24, 50, 100]) {
        console.log(
            `target=${target}, index=${binarySearch(values, target)}`
        );
    }

    // Binary search requires sorted input.
}

// ============================================================================
// 15. PREFIX SUMS
// ============================================================================

function buildPrefixSums(values) {
    const prefix = [];
    let runningTotal = 0;

    for (const value of values) {
        runningTotal += value;
        prefix.push(runningTotal);
    }

    return prefix;
}

function rangeSum(prefix, left, right) {
    if (
        left < 0 ||
        right >= prefix.length ||
        left > right
    ) {
        throw new RangeError("Invalid range");
    }

    if (left === 0) {
        return prefix[right];
    }

    return prefix[right] - prefix[left - 1];
}

function demonstratePrefixSums() {
    section("14. Prefix sums");

    const values = [5, 2, 7, 3, 10];
    const prefix = buildPrefixSums(values);

    console.log("Values:", values);
    console.log("Prefix sums:", prefix);
    console.log("Sum indexes 1..3:", rangeSum(prefix, 1, 3));
    console.log("Sum indexes 0..4:", rangeSum(prefix, 0, 4));
}

// ============================================================================
// 16. TWO-POINTER TECHNIQUE
// ============================================================================

function twoSumSorted(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        const currentSum = values[left] + values[right];

        if (currentSum === target) {
            return [left, right];
        }

        if (currentSum < target) {
            left++;
        } else {
            right--;
        }
    }

    return null;
}

function demonstrateTwoPointers() {
    section("15. Two-pointer technique");

    const values = [1, 3, 4, 6, 8, 10, 13];
    const target = 14;
    const result = twoSumSorted(values, target);

    console.log("Array:", values);
    console.log("Target:", target);

    if (result === null) {
        console.log("No pair found");
    } else {
        const [left, right] = result;

        console.log(
            `Found ${values[left]} + ${values[right]} = ${target}`
        );
    }
}

// ============================================================================
// 17. COMBINED ARRAY ANALYSIS
// ============================================================================

function analyzeArray(values) {
    if (values.length === 0) {
        return {
            length: 0,
            minimum: null,
            maximum: null,
            positive: 0,
            negative: 0,
            zero: 0,
            frequencies: {}
        };
    }

    let minimum = values[0];
    let maximum = values[0];
    let positive = 0;
    let negative = 0;
    let zero = 0;

    const frequencies = new Map();

    for (const value of values) {
        if (value < minimum) {
            minimum = value;
        }

        if (value > maximum) {
            maximum = value;
        }

        if (value > 0) {
            positive++;
        } else if (value < 0) {
            negative++;
        } else {
            zero++;
        }

        frequencies.set(
            value,
            (frequencies.get(value) ?? 0) + 1
        );
    }

    return {
        length: values.length,
        minimum,
        maximum,
        positive,
        negative,
        zero,
        frequencies: mapToObject(frequencies)
    };
}

function demonstrateCombinedAnalysis() {
    section("16. Combined array analysis");

    const values = [8, -2, 5, 8, 0, -2, 11, 5, 5];

    console.log(analyzeArray(values));
}

// ============================================================================
// 18. VALIDATION AND EDGE CASES
// ============================================================================

function requireNumericArray(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Expected an array");
    }

    for (const value of values) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new TypeError(
                "Every element must be a finite number"
            );
        }
    }
}

function demonstrateValidation() {
    section("17. Validation and edge cases");

    const examples = [
        [],
        [42],
        [7, 7, 7],
        [-5, -2, -10],
        [0, 0, 0],
        [-2, 0, 5, -7, 8]
    ];

    for (const values of examples) {
        console.log("\nArray:", values);
        console.log("Minimum:", values.length ? manualMinimum(values) : null);
        console.log("Maximum:", values.length ? manualMaximum(values) : null);
        console.log(
            "Second-largest:",
            secondLargestDistinct(values)
        );
        console.log(
            "Unique:",
            removeDuplicatesPreserveOrder(values)
        );
    }

    try {
        requireNumericArray([1, 2, "three"]);
    } catch (error) {
        console.log("Validation error:", error.message);
    }
}

// ============================================================================
// 19. COMPLEXITY REFERENCE
// ============================================================================

function printComplexityReference() {
    section("18. Complexity reference");

    const rows = [
        ["Index access", "O(1)", "O(1)"],
        ["Update by index", "O(1)", "O(1)"],
        ["Traversal", "O(n)", "O(1)"],
        ["Linear search", "O(n)", "O(1)"],
        ["Minimum / maximum", "O(n)", "O(1)"],
        ["Frequency counting", "O(n)", "O(k)"],
        ["Reverse in place", "O(n)", "O(1)"],
        ["Rotation using copy", "O(n)", "O(n)"],
        ["Rotation by reversal", "O(n)", "O(1)"],
        ["Duplicate removal", "O(n) average", "O(k)"],
        ["Binary search", "O(log n)", "O(1)"],
        ["Prefix sums", "O(n)", "O(n)"]
    ];

    console.log(
        "Operation".padEnd(32),
        "Time".padEnd(18),
        "Extra space"
    );

    console.log("-".repeat(65));

    for (const [operation, time, space] of rows) {
        console.log(
            operation.padEnd(32),
            time.padEnd(18),
            space
        );
    }
}

// ============================================================================
// 20. TESTS
// ============================================================================

function assertEqual(actual, expected, description) {
    const actualText = JSON.stringify(actual);
    const expectedText = JSON.stringify(expected);

    if (actualText !== expectedText) {
        throw new Error(
            `${description}: expected ${expectedText}, got ${actualText}`
        );
    }
}

function runTests() {
    section("19. Verification tests");

    assertEqual(
        manualMaximum([3, 1, 9, 2]),
        9,
        "maximum"
    );

    assertEqual(
        manualMinimum([3, 1, 9, 2]),
        1,
        "minimum"
    );

    assertEqual(
        secondLargestDistinct([10, 30, 20, 30]),
        20,
        "second-largest"
    );

    const reversed = [1, 2, 3, 4];
    reverseInPlace(reversed);

    assertEqual(
        reversed,
        [4, 3, 2, 1],
        "reverse"
    );

    assertEqual(
        rotateRight([1, 2, 3, 4, 5], 2),
        [4, 5, 1, 2, 3],
        "rotation"
    );

    assertEqual(
        removeDuplicatesPreserveOrder([1, 2, 1, 3, 2]),
        [1, 2, 3],
        "duplicate removal"
    );

    assertEqual(
        countSigns([-2, 0, 3, 5, -1]),
        { positive: 2, negative: 2, zero: 1 },
        "sign counting"
    );

    assertEqual(
        findMissingValues([1, 2, 4, 6], 1, 6),
        [3, 5],
        "missing values"
    );

    assertEqual(
        missingSingleValueXor([3, 0, 1], 3),
        2,
        "single missing value"
    );

    assertEqual(
        linearSearch([5, 8, 2], 8),
        1,
        "linear search"
    );

    assertEqual(
        binarySearch([2, 4, 6, 8, 10], 8),
        3,
        "binary search"
    );

    assertEqual(
        buildPrefixSums([2, 4, 6]),
        [2, 6, 12],
        "prefix sums"
    );

    assertEqual(
        twoSumSorted([1, 3, 4, 6, 8], 10),
        [1, 4],
        "two pointers"
    );

    console.log("All tests passed.");
}

// ============================================================================
// 21. MAIN
// ============================================================================

function main() {
    section("DAY 12 — ARRAY FUNDAMENTALS");

    demonstrateCreationAndIndexing();
    demonstrateTraversal();
    demonstrateUpdating();
    demonstrateSearching();
    demonstrateMinimumMaximum();
    demonstrateFrequencyCounting();
    demonstrateSecondLargest();
    demonstrateReverse();
    demonstrateRotation();
    demonstrateRemoveDuplicates();
    demonstrateSignCounting();
    demonstrateMissingValues();
    demonstrateBinarySearch();
    demonstratePrefixSums();
    demonstrateTwoPointers();
    demonstrateCombinedAnalysis();
    demonstrateValidation();
    printComplexityReference();
    runTests();

    section("Day 12 practice checklist");

    const practiceTasks = [
        "Maximum element",
        "Minimum element",
        "Second-largest element",
        "Reverse array",
        "Rotate array",
        "Remove duplicates",
        "Count positive/negative values",
        "Find missing values"
    ];

    practiceTasks.forEach((task, index) => {
        console.log(`${index + 1}. ${task}`);
    });

    console.log("\nDay 12 study program completed.");
}

main();
