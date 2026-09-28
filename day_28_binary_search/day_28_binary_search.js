/**
 * Day 28 — Binary Search
 * =======================
 *
 * A comprehensive executable study file covering binary search from
 * beginner to advanced level.
 *
 * Topics:
 * - Sorted-array requirement
 * - Left and right boundaries
 * - Midpoint
 * - Search-space reduction
 * - Exact search
 * - First occurrence
 * - Last occurrence
 * - Lower bound
 * - Upper bound
 * - Descending arrays
 * - Rotated arrays
 * - Nearly sorted arrays
 * - Binary search on the answer
 * - Predicate-based search
 * - Asynchronous JavaScript integration
 * - Testing, validation, edge cases, and performance
 *
 * Runtime:
 * - Node.js 18+ recommended
 *
 * No external packages are required.
 */

"use strict";

// ---------------------------------------------------------------------------
// 1. FUNDAMENTALS
// ---------------------------------------------------------------------------

function explainBinarySearch() {
    console.log("\n=== Binary Search Fundamentals ===");
    console.log("Binary search operates on an ordered search space.");
    console.log("Each comparison removes approximately half of the candidates.");
    console.log("Typical iterative complexity: O(log n) time and O(1) space.");
}

// ---------------------------------------------------------------------------
// 2. EXACT SEARCH
// ---------------------------------------------------------------------------

function binarySearchExact(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        // Math.floor avoids a fractional array index.
        const middle = left + Math.floor((right - left) / 2);
        const current = values[middle];

        if (current === target) {
            return middle;
        }

        if (current < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function demonstrateExactSearch() {
    console.log("\n=== Exact Search ===");

    const values = [2, 5, 8, 12, 16, 21, 27, 35];

    for (const target of [2, 16, 35, 10]) {
        console.log(
            `target=${target}, index=${binarySearchExact(values, target)}`
        );
    }
}

// ---------------------------------------------------------------------------
// 3. HALF-OPEN INTERVAL
// ---------------------------------------------------------------------------

function binarySearchHalfOpen(values, target) {
    // Search interval is [left, right).
    let left = 0;
    let right = values.length;

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 4. FIRST OCCURRENCE
// ---------------------------------------------------------------------------

function firstOccurrence(values, target) {
    let left = 0;
    let right = values.length - 1;
    let answer = -1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            answer = middle;
            right = middle - 1;
        } else if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return answer;
}

// ---------------------------------------------------------------------------
// 5. LAST OCCURRENCE
// ---------------------------------------------------------------------------

function lastOccurrence(values, target) {
    let left = 0;
    let right = values.length - 1;
    let answer = -1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            answer = middle;
            left = middle + 1;
        } else if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return answer;
}

// ---------------------------------------------------------------------------
// 6. LOWER BOUND
// ---------------------------------------------------------------------------

function lowerBound(values, target) {
    // Find the first index where values[index] >= target.
    let left = 0;
    let right = values.length;

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

// ---------------------------------------------------------------------------
// 7. UPPER BOUND
// ---------------------------------------------------------------------------

function upperBound(values, target) {
    // Find the first index where values[index] > target.
    let left = 0;
    let right = values.length;

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] <= target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

function occurrenceCount(values, target) {
    return upperBound(values, target) - lowerBound(values, target);
}

function occurrenceRange(values, target) {
    const first = lowerBound(values, target);

    if (first === values.length || values[first] !== target) {
        return [-1, -1];
    }

    return [first, upperBound(values, target) - 1];
}

// ---------------------------------------------------------------------------
// 8. DESCENDING SEARCH
// ---------------------------------------------------------------------------

function binarySearchDescending(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (values[middle] > target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 9. ROTATED SORTED ARRAY
// ---------------------------------------------------------------------------

function searchRotatedSorted(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        // The left half is sorted.
        if (values[left] <= values[middle]) {
            if (values[left] <= target && target < values[middle]) {
                right = middle - 1;
            } else {
                left = middle + 1;
            }
        } else {
            // The right half is sorted.
            if (values[middle] < target && target <= values[right]) {
                left = middle + 1;
            } else {
                right = middle - 1;
            }
        }
    }

    return -1;
}

function searchRotatedWithDuplicates(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return true;
        }

        // Equal boundaries remove information about which half is sorted.
        if (
            values[left] === values[middle] &&
            values[middle] === values[right]
        ) {
            left++;
            right--;
            continue;
        }

        if (values[left] <= values[middle]) {
            if (values[left] <= target && target < values[middle]) {
                right = middle - 1;
            } else {
                left = middle + 1;
            }
        } else {
            if (values[middle] < target && target <= values[right]) {
                left = middle + 1;
            } else {
                right = middle - 1;
            }
        }
    }

    return false;
}

// ---------------------------------------------------------------------------
// 10. NEARLY SORTED ARRAY
// ---------------------------------------------------------------------------

function searchNearlySorted(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (
            middle - 1 >= left &&
            values[middle - 1] === target
        ) {
            return middle - 1;
        }

        if (
            middle + 1 <= right &&
            values[middle + 1] === target
        ) {
            return middle + 1;
        }

        if (target < values[middle]) {
            right = middle - 2;
        } else {
            left = middle + 2;
        }
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 11. PEAK SEARCH
// ---------------------------------------------------------------------------

function findPeak(values) {
    if (values.length === 0) {
        return -1;
    }

    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] < values[middle + 1]) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

// ---------------------------------------------------------------------------
// 12. BINARY SEARCH ON THE ANSWER
// ---------------------------------------------------------------------------

function minimumCapacityForShipping(weights, days) {
    if (!Number.isInteger(days) || days <= 0) {
        throw new RangeError("days must be a positive integer");
    }

    if (weights.some(
        weight => !Number.isFinite(weight) || weight < 0
    )) {
        throw new RangeError("weights must be finite and non-negative");
    }

    if (weights.length === 0) {
        return 0;
    }

    let left = Math.max(...weights);
    let right = weights.reduce((sum, weight) => sum + weight, 0);

    function canShip(capacity) {
        let usedDays = 1;
        let currentLoad = 0;

        for (const weight of weights) {
            if (currentLoad + weight <= capacity) {
                currentLoad += weight;
            } else {
                usedDays++;
                currentLoad = weight;

                if (usedDays > days) {
                    return false;
                }
            }
        }

        return true;
    }

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (canShip(middle)) {
            right = middle;
        } else {
            left = middle + 1;
        }
    }

    return left;
}

// ---------------------------------------------------------------------------
// 13. INTEGER SQUARE ROOT
// ---------------------------------------------------------------------------

function integerSquareRoot(number) {
    if (!Number.isSafeInteger(number) || number < 0) {
        throw new RangeError(
            "number must be a non-negative JavaScript safe integer"
        );
    }

    if (number < 2) {
        return number;
    }

    let left = 1;
    let right = Math.floor(number / 2);
    let answer = 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);
        const square = middle * middle;

        if (square === number) {
            return middle;
        }

        if (square < number) {
            answer = middle;
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return answer;
}

// ---------------------------------------------------------------------------
// 14. FIRST TRUE PREDICATE
// ---------------------------------------------------------------------------

function firstTrue(low, high, predicate) {
    if (!Number.isInteger(low) || !Number.isInteger(high)) {
        throw new TypeError("bounds must be integers");
    }

    let left = low;
    let right = high;
    let answer = -1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (predicate(middle)) {
            answer = middle;
            right = middle - 1;
        } else {
            left = middle + 1;
        }
    }

    return answer;
}

// ---------------------------------------------------------------------------
// 15. FLOATING-POINT BINARY SEARCH
// ---------------------------------------------------------------------------

function approximateSquareRoot(number, iterations = 100) {
    if (!Number.isFinite(number) || number < 0) {
        throw new RangeError("number must be a non-negative finite number");
    }

    if (!Number.isInteger(iterations) || iterations <= 0) {
        throw new RangeError("iterations must be a positive integer");
    }

    if (number === 0) {
        return 0;
    }

    let low = 0;
    let high = Math.max(1, number);

    for (let iteration = 0; iteration < iterations; iteration++) {
        const middle = (low + high) / 2;

        if (middle * middle < number) {
            low = middle;
        } else {
            high = middle;
        }
    }

    return (low + high) / 2;
}

// ---------------------------------------------------------------------------
// 16. EXPONENTIAL SEARCH
// ---------------------------------------------------------------------------

function exponentialSearch(values, target) {
    if (values.length === 0) {
        return -1;
    }

    if (values[0] === target) {
        return 0;
    }

    let bound = 1;

    while (
        bound < values.length &&
        values[bound] < target
    ) {
        bound *= 2;
    }

    let left = Math.floor(bound / 2);
    let right = Math.min(bound, values.length - 1);

    while (left <= right) {
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

// ---------------------------------------------------------------------------
// 17. MATRIX SEARCH
// ---------------------------------------------------------------------------

function searchSortedMatrix(matrix, target) {
    if (matrix.length === 0 || matrix[0].length === 0) {
        return [-1, -1];
    }

    const columns = matrix[0].length;

    if (matrix.some(row => row.length !== columns)) {
        throw new Error("matrix must be rectangular");
    }

    let left = 0;
    let right = matrix.length * columns - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);
        const row = Math.floor(middle / columns);
        const column = middle % columns;
        const current = matrix[row][column];

        if (current === target) {
            return [row, column];
        }

        if (current < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return [-1, -1];
}

// ---------------------------------------------------------------------------
// 18. OBJECT SEARCH
// ---------------------------------------------------------------------------

class Product {
    constructor(productId, name, price) {
        if (!Number.isInteger(productId)) {
            throw new TypeError("productId must be an integer");
        }

        if (typeof name !== "string" || name.trim() === "") {
            throw new TypeError("name must be a non-empty string");
        }

        if (!Number.isFinite(price) || price < 0) {
            throw new RangeError("price must be non-negative and finite");
        }

        this.productId = productId;
        this.name = name;
        this.price = price;
    }
}

function binarySearchProduct(products, productId) {
    let left = 0;
    let right = products.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);
        const currentId = products[middle].productId;

        if (currentId === productId) {
            return middle;
        }

        if (currentId < productId) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

// ---------------------------------------------------------------------------
// 19. SORTEDNESS VALIDATION
// ---------------------------------------------------------------------------

function isSortedAscending(values) {
    for (let index = 1; index < values.length; index++) {
        if (values[index - 1] > values[index]) {
            return false;
        }
    }

    return true;
}

function validatedBinarySearch(values, target) {
    if (!isSortedAscending(values)) {
        throw new Error(
            "binary search requires ascending sorted data"
        );
    }

    return binarySearchExact(values, target);
}

// ---------------------------------------------------------------------------
// 20. ASYNCHRONOUS APPLICATION EXAMPLE
// ---------------------------------------------------------------------------

function fetchSortedRecords() {
    /*
     * A real application might obtain records from a database or HTTP API.
     * This local Promise keeps the example completely self-contained.
     */
    return new Promise(resolve => {
        setTimeout(() => {
            resolve([
                { id: 101, name: "Alpha" },
                { id: 205, name: "Beta" },
                { id: 310, name: "Gamma" },
                { id: 415, name: "Delta" }
            ]);
        }, 10);
    });
}

async function findRecordAfterFetch(recordId) {
    const records = await fetchSortedRecords();

    // Convert the object key into a numeric array for a focused binary search.
    const identifiers = records.map(record => record.id);
    const index = binarySearchExact(identifiers, recordId);

    return index === -1 ? null : records[index];
}

// ---------------------------------------------------------------------------
// 21. TESTING
// ---------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runDeterministicTests() {
    console.log("\n=== Deterministic Tests ===");

    assert(binarySearchExact([], 1) === -1, "empty exact search");
    assert(binarySearchExact([7], 7) === 0, "single exact match");
    assert(binarySearchExact([7], 8) === -1, "single missing value");

    const values = [1, 2, 2, 2, 3, 4, 4, 9];

    assert(firstOccurrence(values, 2) === 1, "first occurrence");
    assert(lastOccurrence(values, 2) === 3, "last occurrence");
    assert(lowerBound(values, 2) === 1, "lower bound");
    assert(upperBound(values, 2) === 4, "upper bound");
    assert(occurrenceCount(values, 2) === 3, "count");
    assert(
        JSON.stringify(occurrenceRange(values, 2)) === "[1,3]",
        "range"
    );

    assert(lowerBound(values, 0) === 0, "lower below range");
    assert(lowerBound(values, 10) === values.length, "lower above range");

    const descending = [100, 90, 80, 70, 60, 50];
    assert(
        binarySearchDescending(descending, 70) === 3,
        "descending search"
    );

    const rotated = [40, 50, 60, 70, 10, 20, 30];
    assert(searchRotatedSorted(rotated, 10) === 4, "rotated search");
    assert(searchRotatedSorted(rotated, 99) === -1, "rotated missing");

    const rotatedDuplicates = [2, 5, 6, 0, 0, 1, 2];
    assert(
        searchRotatedWithDuplicates(rotatedDuplicates, 0),
        "rotated duplicate search"
    );
    assert(
        !searchRotatedWithDuplicates(rotatedDuplicates, 3),
        "rotated duplicate missing"
    );

    const nearlySorted = [10, 30, 20, 50, 40, 60];
    assert(
        searchNearlySorted(nearlySorted, 20) === 2,
        "nearly sorted search"
    );

    assert(integerSquareRoot(0) === 0, "sqrt zero");
    assert(integerSquareRoot(16) === 4, "sqrt perfect square");
    assert(integerSquareRoot(17) === 4, "sqrt floor");

    assert(
        minimumCapacityForShipping([1, 2, 3, 1, 1], 4) === 3,
        "shipping capacity"
    );

    const matrix = [
        [1, 3, 5, 7],
        [10, 11, 16, 20],
        [23, 30, 34, 60]
    ];

    assert(
        JSON.stringify(searchSortedMatrix(matrix, 16)) === "[1,2]",
        "matrix search"
    );

    const products = [
        new Product(100, "Keyboard", 50),
        new Product(200, "Monitor", 250),
        new Product(300, "Mouse", 30)
    ];

    assert(
        binarySearchProduct(products, 200) === 1,
        "object search"
    );

    console.log("All deterministic tests passed.");
}

// ---------------------------------------------------------------------------
// 22. RANDOMIZED TESTING
// ---------------------------------------------------------------------------

function randomInteger(minimum, maximum) {
    return Math.floor(
        Math.random() * (maximum - minimum + 1)
    ) + minimum;
}

function runRandomizedTests(iterations = 500) {
    console.log(`\n=== Randomized Tests (${iterations} cases) ===`);

    for (let iteration = 0; iteration < iterations; iteration++) {
        const values = [];

        const length = randomInteger(0, 100);

        for (let index = 0; index < length; index++) {
            values.push(randomInteger(-20, 20));
        }

        values.sort((a, b) => a - b);

        const target = randomInteger(-25, 25);

        const exactIndex = binarySearchExact(values, target);

        if (values.includes(target)) {
            assert(
                exactIndex !== -1 &&
                values[exactIndex] === target,
                "exact randomized search"
            );
        } else {
            assert(
                exactIndex === -1,
                "missing randomized search"
            );
        }

        const first = lowerBound(values, target);
        const expectedFirst =
            values.findIndex(value => value >= target);

        const normalizedExpectedFirst =
            expectedFirst === -1
                ? values.length
                : expectedFirst;

        assert(
            first === normalizedExpectedFirst,
            "randomized lower bound"
        );

        const upper = upperBound(values, target);
        const expectedUpper =
            values.findIndex(value => value > target);

        const normalizedExpectedUpper =
            expectedUpper === -1
                ? values.length
                : expectedUpper;

        assert(
            upper === normalizedExpectedUpper,
            "randomized upper bound"
        );
    }

    console.log("All randomized tests passed.");
}

// ---------------------------------------------------------------------------
// 23. PERFORMANCE COMPARISON
// ---------------------------------------------------------------------------

function linearSearch(values, target) {
    for (let index = 0; index < values.length; index++) {
        if (values[index] === target) {
            return index;
        }
    }

    return -1;
}

function benchmarkSearches() {
    console.log("\n=== Performance Comparison ===");

    const values = Array.from(
        { length: 2_000_000 },
        (_, index) => index
    );

    const target = values[values.length - 1];

    let start = performance.now();
    const linearResult = linearSearch(values, target);
    const linearTime = performance.now() - start;

    start = performance.now();
    const binaryResult = binarySearchExact(values, target);
    const binaryTime = performance.now() - start;

    console.log(
        `Linear result=${linearResult}, time=${linearTime.toFixed(4)} ms`
    );

    console.log(
        `Binary result=${binaryResult}, time=${binaryTime.toFixed(4)} ms`
    );
}

// ---------------------------------------------------------------------------
// 24. COMMON MISTAKES
// ---------------------------------------------------------------------------

function demonstrateCommonMistakes() {
    console.log("\n=== Common Mistakes ===");

    const unsorted = [8, 2, 10, 4, 6];

    console.log(
        "Unsorted input is invalid for standard binary search:",
        unsorted
    );

    const duplicates = [1, 2, 2, 2, 3];

    console.log(
        "Exact search may return any matching duplicate:",
        binarySearchExact(duplicates, 2)
    );

    console.log(
        "First occurrence:",
        firstOccurrence(duplicates, 2)
    );

    console.log(
        "Last occurrence:",
        lastOccurrence(duplicates, 2)
    );

    console.log(
        "Empty input:",
        binarySearchExact([], 100)
    );

    console.log(
        "One-element input:",
        binarySearchExact([100], 100)
    );
}

// ---------------------------------------------------------------------------
// 25. PRACTICAL EXAMPLES
// ---------------------------------------------------------------------------

function demonstratePracticalExamples() {
    console.log("\n=== Practical Examples ===");

    const scores = [35, 42, 42, 48, 55, 55, 55, 61, 73, 88];

    console.log("Scores:", scores);
    console.log("First score >= 55:", lowerBound(scores, 55));
    console.log("First score > 55:", upperBound(scores, 55));
    console.log("Number of 55 scores:", occurrenceCount(scores, 55));

    const timestamps = [100, 125, 150, 175, 200, 225];
    const requestedTimestamp = 160;

    console.log(
        `Insertion point for ${requestedTimestamp}:`,
        lowerBound(timestamps, requestedTimestamp)
    );

    const fileSizes = [100, 250, 500, 750, 1000];
    const sizeLimit = 600;
    const firstTooLarge = upperBound(fileSizes, sizeLimit);

    console.log(
        "First file larger than 600:",
        firstTooLarge < fileSizes.length
            ? fileSizes[firstTooLarge]
            : "none"
    );
}

// ---------------------------------------------------------------------------
// 26. MAIN ASYNCHRONOUS PROGRAM
// ---------------------------------------------------------------------------

async function main() {
    explainBinarySearch();
    demonstrateExactSearch();

    console.log("\n=== Half-Open Interval ===");
    console.log(
        binarySearchHalfOpen([1, 4, 7, 10, 15], 10)
    );

    console.log("\n=== Duplicate Handling ===");

    const duplicates = [1, 2, 2, 2, 3, 4];

    console.log("First:", firstOccurrence(duplicates, 2));
    console.log("Last:", lastOccurrence(duplicates, 2));
    console.log("Lower bound:", lowerBound(duplicates, 2));
    console.log("Upper bound:", upperBound(duplicates, 2));
    console.log("Count:", occurrenceCount(duplicates, 2));
    console.log("Range:", occurrenceRange(duplicates, 2));

    console.log("\n=== Descending Search ===");

    const descending = [100, 90, 80, 70, 60, 50];

    console.log(
        "Index of 70:",
        binarySearchDescending(descending, 70)
    );

    console.log("\n=== Rotated Search ===");

    const rotated = [40, 50, 60, 70, 10, 20, 30];

    for (const target of [10, 70, 30, 99]) {
        console.log(
            `target=${target}, index=${searchRotatedSorted(rotated, target)}`
        );
    }

    console.log("\n=== Nearly Sorted Search ===");

    const nearlySorted = [10, 30, 20, 50, 40, 60];

    for (const target of [10, 20, 40, 60, 99]) {
        console.log(
            `target=${target}, index=${searchNearlySorted(
                nearlySorted,
                target
            )}`
        );
    }

    console.log("\n=== Peak Search ===");

    const peakValues = [1, 3, 8, 12, 9, 4, 2];
    const peakIndex = findPeak(peakValues);

    console.log("Peak index:", peakIndex);
    console.log("Peak value:", peakValues[peakIndex]);

    console.log("\n=== Binary Search on the Answer ===");

    const weights = [1, 2, 3, 1, 1];

    for (const days of [3, 4, 5]) {
        console.log(
            `days=${days}, capacity=${minimumCapacityForShipping(
                weights,
                days
            )}`
        );
    }

    console.log("\n=== Integer Square Root ===");

    for (const number of [0, 1, 2, 15, 16, 17, 100]) {
        console.log(
            `floor(sqrt(${number}))=${integerSquareRoot(number)}`
        );
    }

    console.log("\n=== First True Predicate ===");

    const threshold = 73;

    console.log(
        firstTrue(0, 100, value => value >= threshold)
    );

    console.log("\n=== Floating-Point Search ===");

    for (const number of [2, 10, 100]) {
        console.log(
            `sqrt(${number})≈${approximateSquareRoot(number).toFixed(12)}`
        );
    }

    console.log("\n=== Exponential Search ===");

    const exponentialValues = Array.from(
        { length: 334 },
        (_, index) => index * 3
    );

    console.log(
        "600:",
        exponentialSearch(exponentialValues, 600)
    );

    console.log(
        "601:",
        exponentialSearch(exponentialValues, 601)
    );

    console.log("\n=== Matrix Search ===");

    const matrix = [
        [1, 3, 5, 7],
        [10, 11, 16, 20],
        [23, 30, 34, 60]
    ];

    console.log("16:", searchSortedMatrix(matrix, 16));
    console.log("17:", searchSortedMatrix(matrix, 17));

    console.log("\n=== Object Search ===");

    const products = [
        new Product(100, "Keyboard", 50),
        new Product(200, "Monitor", 250),
        new Product(300, "Mouse", 30)
    ];

    const productIndex = binarySearchProduct(products, 200);

    console.log(
        "Found product:",
        productIndex === -1 ? null : products[productIndex]
    );

    console.log("\n=== Validation ===");

    console.log(
        "Sorted input:",
        validatedBinarySearch([1, 2, 3, 4], 3)
    );

    try {
        validatedBinarySearch([3, 1, 2], 1);
    } catch (error) {
        console.log("Validation error:", error.message);
    }

    console.log("\n=== Asynchronous Application ===");

    const record = await findRecordAfterFetch(310);
    console.log("Fetched record:", record);

    demonstratePracticalExamples();
    demonstrateCommonMistakes();
    runDeterministicTests();
    runRandomizedTests();
    benchmarkSearches();

    console.log("\n=== Complexity Reference ===");
    console.log("Exact search: O(log n) time, O(1) space");
    console.log("First/last occurrence: O(log n) time, O(1) space");
    console.log("Lower/upper bound: O(log n) time, O(1) space");
    console.log("Rotated distinct array: O(log n) time, O(1) space");
    console.log("Rotated array with duplicates: O(n) worst case");
    console.log("Binary search on answer: O(log S × predicate cost)");
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
