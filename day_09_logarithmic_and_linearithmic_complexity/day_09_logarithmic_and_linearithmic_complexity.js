/*
 * Day 9 — Logarithmic and Linearithmic Complexity
 *
 * Topics:
 * - Binary search
 * - Divide-and-conquer
 * - Logarithmic growth
 * - Merge sort
 * - Heap operations
 * - O(log n) versus O(n)
 * - Boundary searching
 * - Binary search on answer spaces
 * - JavaScript-specific implementation details
 * - Error handling
 * - Testing
 * - Performance measurement
 *
 * This file is executable with a modern JavaScript runtime such as Node.js.
 */

"use strict";

// ============================================================================
// 1. LOGARITHMIC GROWTH
// ============================================================================

function log2(value) {
    if (value <= 0) {
        throw new RangeError("log2 requires a positive number.");
    }

    return Math.log2(value);
}

function demonstrateGrowth() {
    console.log("\n" + "=".repeat(78));
    console.log("1. LOGARITHMIC GROWTH");
    console.log("=".repeat(78));

    const values = [
        1,
        2,
        4,
        8,
        16,
        32,
        64,
        1024,
        1_000_000,
        1_000_000_000
    ];

    console.log("n".padStart(15), "log2(n)".padStart(15), "n".padStart(15));
    console.log("-".repeat(48));

    for (const value of values) {
        console.log(
            value.toLocaleString().padStart(15),
            log2(value).toFixed(2).padStart(15),
            value.toLocaleString().padStart(15)
        );
    }

    console.log(`
If an algorithm repeatedly cuts its search space in half:

    n -> n/2 -> n/4 -> n/8 -> ...

then after k divisions:

    n / 2^k = 1

so:

    k = log2(n)

This is why binary search is O(log n).
`);
}

function compareGrowth(n) {
    if (!Number.isSafeInteger(n) || n < 1) {
        throw new RangeError("n must be a positive safe integer.");
    }

    const logarithmicSteps = n === 1 ? 0 : Math.ceil(log2(n));
    const linearSteps = n;

    console.log(`\nn = ${n.toLocaleString()}`);
    console.log(`Approximate logarithmic steps: ${logarithmicSteps.toLocaleString()}`);
    console.log(`Linear steps:                  ${linearSteps.toLocaleString()}`);
    console.log(
        `Linear/logarithmic ratio:      ${(linearSteps / Math.max(logarithmicSteps, 1)).toFixed(2)}x`
    );
}


// ============================================================================
// 2. LINEAR SEARCH
// ============================================================================

function linearSearch(values, target) {
    /*
     * Linear search checks elements one by one.
     *
     * Best case:  O(1)
     * Worst case: O(n)
     * Space:      O(1)
     */
    for (let index = 0; index < values.length; index++) {
        if (values[index] === target) {
            return index;
        }
    }

    return -1;
}


// ============================================================================
// 3. ITERATIVE BINARY SEARCH
// ============================================================================

function binarySearch(values, target) {
    /*
     * The input must be sorted in ascending order.
     *
     * Each comparison eliminates approximately half the remaining
     * candidates.
     *
     * Time:  O(log n)
     * Space: O(1)
     */
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        // Math.floor prevents a fractional array index.
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


// ============================================================================
// 4. RECURSIVE BINARY SEARCH
// ============================================================================

function binarySearchRecursive(values, target, left = 0, right = values.length - 1) {
    /*
     * The recursive version has O(log n) call-stack depth.
     *
     * Unlike an iterative implementation, recursion consumes stack space.
     */
    if (left > right) {
        return -1;
    }

    const middle = left + Math.floor((right - left) / 2);

    if (values[middle] === target) {
        return middle;
    }

    if (values[middle] < target) {
        return binarySearchRecursive(values, target, middle + 1, right);
    }

    return binarySearchRecursive(values, target, left, middle - 1);
}


// ============================================================================
// 5. BOUNDARY SEARCH
// ============================================================================

function firstOccurrence(values, target) {
    /*
     * Find the first matching position.
     *
     * When a match is found, continue searching left.
     *
     * Time: O(log n)
     * Space: O(1)
     */
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

function lowerBound(values, target) {
    /*
     * Return the first index where values[index] >= target.
     *
     * The search interval uses [left, right), where right is exclusive.
     */
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

function upperBound(values, target) {
    /*
     * Return the first index where values[index] > target.
     */
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


// ============================================================================
// 6. BINARY SEARCH ON AN ANSWER SPACE
// ============================================================================

function integerSquareRoot(number) {
    /*
     * Find floor(sqrt(number)) without calling Math.sqrt.
     *
     * This demonstrates that binary search can operate on a range of
     * possible answers rather than on an array.
     *
     * Time: O(log n)
     * Space: O(1)
     */
    if (!Number.isSafeInteger(number) || number < 0) {
        throw new RangeError("number must be a non-negative safe integer.");
    }

    if (number < 2) {
        return number;
    }

    let left = 1;
    let right = number;
    let answer = 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        // Avoid multiplication overflow beyond JavaScript's safe integer
        // range by comparing using division.
        if (middle <= Math.floor(number / middle)) {
            answer = middle;
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return answer;
}

function minimumShippingCapacity(weights, days) {
    /*
     * Find the minimum capacity that can ship all weights in order
     * within the given number of days.
     *
     * Binary search is applied to possible capacities.
     *
     * Complexity:
     *     O(n log S)
     *
     * where S is the numeric capacity range.
     */
    if (!Array.isArray(weights) || weights.length === 0) {
        throw new TypeError("weights must be a non-empty array.");
    }

    if (!Number.isInteger(days) || days < 1) {
        throw new RangeError("days must be a positive integer.");
    }

    if (weights.some(weight => !Number.isSafeInteger(weight) || weight <= 0)) {
        throw new RangeError("Every weight must be a positive safe integer.");
    }

    function feasible(capacity) {
        let requiredDays = 1;
        let currentLoad = 0;

        for (const weight of weights) {
            if (currentLoad + weight <= capacity) {
                currentLoad += weight;
            } else {
                requiredDays++;
                currentLoad = weight;
            }
        }

        return requiredDays <= days;
    }

    let left = Math.max(...weights);
    let right = weights.reduce((sum, weight) => sum + weight, 0);

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (feasible(middle)) {
            right = middle;
        } else {
            left = middle + 1;
        }
    }

    return left;
}


// ============================================================================
// 7. MERGE SORT
// ============================================================================

function merge(left, right) {
    /*
     * Merge two sorted arrays.
     *
     * Every item is examined at most once during the merge.
     *
     * Time: O(left.length + right.length)
     */
    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    while (leftIndex < left.length && rightIndex < right.length) {
        if (left[leftIndex] <= right[rightIndex]) {
            // Taking the left item first for equality preserves stability.
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

function mergeSort(values) {
    /*
     * Divide:
     *     Split the input into two halves.
     *
     * Conquer:
     *     Recursively sort both halves.
     *
     * Combine:
     *     Merge the sorted halves.
     *
     * Recurrence:
     *     T(n) = 2T(n/2) + O(n)
     *
     * Therefore:
     *     Time: O(n log n)
     *     Space: O(n)
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
// 8. BOTTOM-UP MERGE SORT
// ============================================================================

function bottomUpMergeSort(values) {
    /*
     * Iterative merge sort.
     *
     * Start with runs of size 1.
     * Merge runs of size 1 -> 2.
     * Merge runs of size 2 -> 4.
     * Continue until the whole array is covered.
     *
     * Time: O(n log n)
     * Space: O(n)
     */
    const result = [...values];

    for (let width = 1; width < result.length; width *= 2) {
        for (let start = 0; start < result.length; start += 2 * width) {
            const middle = Math.min(start + width, result.length);
            const end = Math.min(start + 2 * width, result.length);

            const left = result.slice(start, middle);
            const right = result.slice(middle, end);

            const merged = merge(left, right);

            for (let i = 0; i < merged.length; i++) {
                result[start + i] = merged[i];
            }
        }
    }

    return result;
}


// ============================================================================
// 9. MAX HEAP
// ============================================================================

class MaxHeap {
    /*
     * A binary heap is a complete binary tree commonly represented by
     * an array.
     *
     * For zero-based indexing:
     *
     * parent(i) = floor((i - 1) / 2)
     * left(i)   = 2i + 1
     * right(i)  = 2i + 2
     *
     * Operations:
     *
     * peek:       O(1)
     * insert:     O(log n)
     * extractMax: O(log n)
     * buildHeap:  O(n)
     */

    constructor(values = []) {
        this.data = [...values];
        this.buildHeap();
    }

    parent(index) {
        return Math.floor((index - 1) / 2);
    }

    leftChild(index) {
        return 2 * index + 1;
    }

    rightChild(index) {
        return 2 * index + 2;
    }

    swap(first, second) {
        [this.data[first], this.data[second]] =
            [this.data[second], this.data[first]];
    }

    siftUp(index) {
        while (index > 0) {
            const parentIndex = this.parent(index);

            if (this.data[parentIndex] >= this.data[index]) {
                break;
            }

            this.swap(parentIndex, index);
            index = parentIndex;
        }
    }

    siftDown(index) {
        while (true) {
            let largest = index;

            const left = this.leftChild(index);
            const right = this.rightChild(index);

            if (
                left < this.data.length &&
                this.data[left] > this.data[largest]
            ) {
                largest = left;
            }

            if (
                right < this.data.length &&
                this.data[right] > this.data[largest]
            ) {
                largest = right;
            }

            if (largest === index) {
                break;
            }

            this.swap(index, largest);
            index = largest;
        }
    }

    buildHeap() {
        /*
         * Leaves already satisfy the heap property.
         * Start at the last internal node and move toward the root.
         *
         * The complete bottom-up construction is O(n).
         */
        const firstParent = Math.floor(this.data.length / 2) - 1;

        for (let index = firstParent; index >= 0; index--) {
            this.siftDown(index);
        }
    }

    insert(value) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new TypeError("Heap values must be finite numbers.");
        }

        this.data.push(value);
        this.siftUp(this.data.length - 1);
    }

    peekMax() {
        if (this.data.length === 0) {
            throw new Error("Cannot peek an empty heap.");
        }

        return this.data[0];
    }

    extractMax() {
        if (this.data.length === 0) {
            throw new Error("Cannot extract from an empty heap.");
        }

        const maximum = this.data[0];
        const last = this.data.pop();

        if (this.data.length > 0) {
            this.data[0] = last;
            this.siftDown(0);
        }

        return maximum;
    }

    isValid() {
        for (let child = 1; child < this.data.length; child++) {
            const parent = this.parent(child);

            if (this.data[parent] < this.data[child]) {
                return false;
            }
        }

        return true;
    }

    get size() {
        return this.data.length;
    }
}


// ============================================================================
// 10. HEAP SORT
// ============================================================================

function heapSort(values) {
    /*
     * Build heap: O(n)
     * Extract n elements: O(n log n)
     *
     * Total: O(n log n)
     */
    const heap = new MaxHeap(values);
    const result = [];

    while (heap.size > 0) {
        result.push(heap.extractMax());
    }

    result.reverse();
    return result;
}


// ============================================================================
// 11. RECURSIVE TRACE
// ============================================================================

function binarySearchTrace(values, target, left = 0, right = values.length - 1, depth = 0) {
    const indentation = "  ".repeat(depth);

    if (left > right) {
        console.log(indentation + "empty range -> not found");
        return -1;
    }

    const middle = left + Math.floor((right - left) / 2);

    console.log(
        `${indentation}range=[${left}, ${right}], ` +
        `middle=${middle}, value=${values[middle]}`
    );

    if (values[middle] === target) {
        console.log(indentation + "target found");
        return middle;
    }

    if (values[middle] < target) {
        return binarySearchTrace(
            values,
            target,
            middle + 1,
            right,
            depth + 1
        );
    }

    return binarySearchTrace(
        values,
        target,
        left,
        middle - 1,
        depth + 1
    );
}


// ============================================================================
// 12. TESTING HELPERS
// ============================================================================

function arraysEqual(first, second) {
    if (first.length !== second.length) {
        return false;
    }

    return first.every((value, index) => value === second[index]);
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runCorrectnessTests() {
    console.log("\n" + "=".repeat(78));
    console.log("12. CORRECTNESS TESTS");
    console.log("=".repeat(78));

    let seed = 123456789;

    function randomInteger(min, max) {
        // Simple deterministic pseudo-random generator for reproducible tests.
        seed = (1664525 * seed + 1013904223) >>> 0;
        return min + (seed % (max - min + 1));
    }

    for (let size = 0; size <= 100; size++) {
        const values = [];

        for (let i = 0; i < size; i++) {
            values.push(randomInteger(-1000, 1000));
        }

        const expected = [...values].sort((a, b) => a - b);

        assert(
            arraysEqual(mergeSort(values), expected),
            `mergeSort failed for size ${size}`
        );

        assert(
            arraysEqual(bottomUpMergeSort(values), expected),
            `bottomUpMergeSort failed for size ${size}`
        );

        assert(
            arraysEqual(heapSort(values), expected),
            `heapSort failed for size ${size}`
        );

        const heap = new MaxHeap(values);

        assert(heap.isValid(), `heap invalid for size ${size}`);

        const extracted = [];

        while (heap.size > 0) {
            extracted.push(heap.extractMax());
        }

        assert(
            arraysEqual(extracted, [...values].sort((a, b) => b - a)),
            `heap extraction failed for size ${size}`
        );
    }

    const testValues = [-10, -1, 0, 1, 2, 3, 10];

    for (const values of [
        [],
        [1],
        [1, 2],
        [2, 1],
        [1, 1, 1],
        testValues
    ]) {
        const sorted = [...values].sort((a, b) => a - b);

        for (let target = -12; target <= 12; target++) {
            const index = binarySearch(sorted, target);

            if (sorted.includes(target)) {
                assert(
                    sorted[index] === target,
                    `binary search returned wrong index for ${target}`
                );
            } else {
                assert(
                    index === -1,
                    `binary search should not find ${target}`
                );
            }
        }
    }

    console.log("All correctness tests passed.");
}


// ============================================================================
// 13. PERFORMANCE MEASUREMENT
// ============================================================================

function measurePerformance() {
    console.log("\n" + "=".repeat(78));
    console.log("13. PRACTICAL PERFORMANCE MEASUREMENT");
    console.log("=".repeat(78));

    function createData(size) {
        const values = new Array(size);

        for (let index = 0; index < size; index++) {
            values[index] = (index * 7919) % (size * 10);
        }

        return values;
    }

    for (const size of [1_000, 10_000, 100_000]) {
        const values = createData(size);
        const sorted = [...values].sort((a, b) => a - b);
        const target = sorted[sorted.length - 1];

        const linearStart = process.hrtime.bigint();
        linearSearch(values, target);
        const linearEnd = process.hrtime.bigint();

        const binaryStart = process.hrtime.bigint();
        binarySearch(sorted, target);
        const binaryEnd = process.hrtime.bigint();

        const mergeStart = process.hrtime.bigint();
        mergeSort(values);
        const mergeEnd = process.hrtime.bigint();

        const linearMilliseconds =
            Number(linearEnd - linearStart) / 1_000_000;

        const binaryMilliseconds =
            Number(binaryEnd - binaryStart) / 1_000_000;

        const mergeMilliseconds =
            Number(mergeEnd - mergeStart) / 1_000_000;

        console.log(`\nn = ${size.toLocaleString()}`);
        console.log(`Linear search: ${linearMilliseconds.toFixed(4)} ms`);
        console.log(`Binary search: ${binaryMilliseconds.toFixed(4)} ms`);
        console.log(`Merge sort:    ${mergeMilliseconds.toFixed(4)} ms`);
    }

    console.log(`
Measured time depends on hardware, runtime optimization, memory behavior,
input distribution, and implementation constants.

Big-O notation describes how work grows as input size becomes large.
It does not state the exact runtime in milliseconds.
`);
}


// ============================================================================
// 14. DEMONSTRATIONS
// ============================================================================

function demonstrateHeap() {
    console.log("\n" + "=".repeat(78));
    console.log("14. HEAP OPERATIONS");
    console.log("=".repeat(78));

    const heap = new MaxHeap();

    for (const value of [10, 4, 15, 7, 20, 3]) {
        heap.insert(value);
        console.log(`Inserted ${value}:`, heap.data);
    }

    console.log("Valid heap:", heap.isValid());
    console.log("Maximum:", heap.peekMax());

    while (heap.size > 0) {
        console.log("Extracted:", heap.extractMax());
    }
}

function demonstrateBoundarySearch() {
    console.log("\n" + "=".repeat(78));
    console.log("15. BOUNDARY SEARCH");
    console.log("=".repeat(78));

    const values = [1, 2, 2, 2, 3, 4, 4, 5];

    console.log("Values:", values);
    console.log("First 2:", firstOccurrence(values, 2));
    console.log("Last 2:", lastOccurrence(values, 2));
    console.log("Lower bound of 3:", lowerBound(values, 3));
    console.log("Upper bound of 3:", upperBound(values, 3));
}

function demonstrateDivideAndConquer() {
    console.log("\n" + "=".repeat(78));
    console.log("16. DIVIDE-AND-CONQUER");
    console.log("=".repeat(78));

    console.log(`
Binary search:
    T(n) = T(n/2) + O(1)
    Result = O(log n)

Merge sort:
    T(n) = 2T(n/2) + O(n)
    Result = O(n log n)

Binary search discards one half.
Merge sort processes both halves and then performs a linear merge.
`);

    const values = Array.from({ length: 32 }, (_, index) => index + 1);

    console.log("Recursive trace:");
    binarySearchTrace(values, 29);
}


// ============================================================================
// 15. MAIN
// ============================================================================

function main() {
    console.log("=".repeat(78));
    console.log("DAY 9 — LOGARITHMIC AND LINEARITHMIC COMPLEXITY");
    console.log("=".repeat(78));

    demonstrateGrowth();

    compareGrowth(1_000);
    compareGrowth(1_000_000);
    compareGrowth(1_000_000_000);

    console.log("\n" + "=".repeat(78));
    console.log("2. LINEAR SEARCH VS BINARY SEARCH");
    console.log("=".repeat(78));

    const values = Array.from({ length: 50 }, (_, index) => index * 2);
    const target = 74;

    console.log("Target:", target);
    console.log("Linear search:", linearSearch(values, target));
    console.log("Binary search:", binarySearch(values, target));
    console.log(
        "Recursive binary search:",
        binarySearchRecursive(values, target)
    );

    demonstrateBoundarySearch();

    console.log("\nInteger square roots:");

    for (const number of [0, 1, 2, 8, 9, 10, 100, 999]) {
        console.log(
            `floor(sqrt(${number})) = ${integerSquareRoot(number)}`
        );
    }

    const weights = [1, 2, 3, 4, 5, 6, 7];

    console.log(
        "\nMinimum shipping capacity:",
        minimumShippingCapacity(weights, 3)
    );

    console.log("\n" + "=".repeat(78));
    console.log("MERGE SORT");
    console.log("=".repeat(78));

    const unsorted = [38, 27, 43, 3, 9, 82, 10];

    console.log("Input:", unsorted);
    console.log("Merge sort:", mergeSort(unsorted));
    console.log("Bottom-up merge sort:", bottomUpMergeSort(unsorted));

    demonstrateHeap();
    demonstrateDivideAndConquer();
    runCorrectnessTests();
    measurePerformance();

    console.log("\n" + "=".repeat(78));
    console.log("DAY 9 PROGRAM COMPLETED");
    console.log("=".repeat(78));
}

main();
