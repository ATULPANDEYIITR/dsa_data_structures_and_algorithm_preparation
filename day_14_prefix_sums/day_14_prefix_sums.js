"use strict";

/*
 * Day 14 — Prefix Sums
 *
 * Topics:
 * - Prefix-sum construction
 * - Range-sum queries
 * - Multiple range queries
 * - Subarray sums
 * - Prefix-frequency maps
 * - Equilibrium indices
 * - Subarray sum equals K
 * - Longest subarray with sum K
 * - Zero-sum subarrays
 * - Divisibility by K
 * - Prefix XOR
 * - Two-dimensional prefix sums
 * - Difference arrays
 * - Sliding-window comparison
 * - Validation and edge cases
 *
 * This file is executable with Node.js and uses no external packages.
 */


// -----------------------------------------------------------------------------
// 1. PREFIX-SUM CONSTRUCTION
// -----------------------------------------------------------------------------

function buildPrefixSum(numbers) {
    /*
     * The leading zero gives every range the same formula:
     *
     * sum(left..right) = prefix[right + 1] - prefix[left]
     */
    const prefix = [0];

    for (const value of numbers) {
        prefix.push(prefix[prefix.length - 1] + value);
    }

    return prefix;
}

function demonstratePrefixConstruction() {
    const numbers = [3, 1, 4, 2, 5];
    const prefix = buildPrefixSum(numbers);

    console.log("\n=== Prefix-sum construction ===");
    console.log("Array :", numbers);
    console.log("Prefix:", prefix);
}


// -----------------------------------------------------------------------------
// 2. RANGE-SUM QUERIES
// -----------------------------------------------------------------------------

function rangeSum(prefix, left, right) {
    if (left < 0 || right < 0) {
        throw new RangeError("Range indices cannot be negative.");
    }

    if (left > right) {
        throw new RangeError("left cannot be greater than right.");
    }

    if (right + 1 >= prefix.length) {
        throw new RangeError("Range endpoint is outside the prefix array.");
    }

    return prefix[right + 1] - prefix[left];
}

function naiveRangeSum(numbers, left, right) {
    if (left < 0 || right >= numbers.length || left > right) {
        throw new RangeError("Invalid range.");
    }

    let total = 0;

    for (let index = left; index <= right; index += 1) {
        total += numbers[index];
    }

    return total;
}

function demonstrateRangeQueries() {
    const numbers = [2, 5, 1, 7, 3, 4];
    const prefix = buildPrefixSum(numbers);

    console.log("\n=== Range-sum queries ===");

    for (const [left, right] of [
        [0, 2],
        [1, 4],
        [3, 5],
        [0, 5],
    ]) {
        const optimized = rangeSum(prefix, left, right);
        const reference = naiveRangeSum(numbers, left, right);

        console.log(
            `[${left}, ${right}] -> optimized=${optimized}, reference=${reference}`
        );
    }
}


// -----------------------------------------------------------------------------
// 3. MULTIPLE RANGE QUERIES
// -----------------------------------------------------------------------------

function answerRangeQueries(numbers, queries) {
    const prefix = buildPrefixSum(numbers);

    return queries.map(([left, right]) =>
        rangeSum(prefix, left, right)
    );
}

function demonstrateMultipleQueries() {
    const numbers = [10, 20, 30, 40, 50];

    const queries = [
        [0, 1],
        [1, 3],
        [2, 4],
        [0, 4],
    ];

    console.log("\n=== Multiple range queries ===");
    console.log(answerRangeQueries(numbers, queries));
}


// -----------------------------------------------------------------------------
// 4. SUBARRAY SUM ENUMERATION
// -----------------------------------------------------------------------------

function enumerateSubarraySums(numbers) {
    const prefix = buildPrefixSum(numbers);
    const result = [];

    for (let left = 0; left < numbers.length; left += 1) {
        for (let right = left; right < numbers.length; right += 1) {
            const total = prefix[right + 1] - prefix[left];

            result.push({
                left,
                right,
                sum: total,
            });
        }
    }

    return result;
}

function demonstrateSubarraySums() {
    const numbers = [2, -1, 3];

    console.log("\n=== Subarray sums ===");

    for (const item of enumerateSubarraySums(numbers)) {
        console.log(item);
    }
}


// -----------------------------------------------------------------------------
// 5. EQUILIBRIUM INDEX
// -----------------------------------------------------------------------------

function equilibriumIndices(numbers) {
    const total = numbers.reduce((sum, value) => sum + value, 0);

    let leftSum = 0;
    const result = [];

    for (let index = 0; index < numbers.length; index += 1) {
        const value = numbers[index];
        const rightSum = total - leftSum - value;

        if (leftSum === rightSum) {
            result.push(index);
        }

        leftSum += value;
    }

    return result;
}

function demonstrateEquilibriumIndex() {
    console.log("\n=== Equilibrium indices ===");

    const examples = [
        [-7, 1, 5, 2, -4, 3, 0],
        [1, 2, 3],
        [2, -2, 2, -2],
        [5],
    ];

    for (const numbers of examples) {
        console.log(numbers, "->", equilibriumIndices(numbers));
    }
}


// -----------------------------------------------------------------------------
// 6. PREFIX-FREQUENCY MAP
// -----------------------------------------------------------------------------

function countSubarraysWithSumK(numbers, target) {
    /*
     * Map:
     *     prefix sum -> number of occurrences
     *
     * If currentPrefix - oldPrefix = target,
     * then oldPrefix = currentPrefix - target.
     *
     * Map.get() returns undefined for a missing key, so default to zero.
     */
    const frequency = new Map();
    frequency.set(0, 1);

    let runningSum = 0;
    let count = 0;

    for (const value of numbers) {
        runningSum += value;

        const requiredPrefix = runningSum - target;
        count += frequency.get(requiredPrefix) ?? 0;

        frequency.set(
            runningSum,
            (frequency.get(runningSum) ?? 0) + 1
        );
    }

    return count;
}

function demonstrateSubarraySumK() {
    console.log("\n=== Count subarrays with sum K ===");

    const examples = [
        { numbers: [1, 1, 1], target: 2 },
        { numbers: [1, 2, 3], target: 3 },
        { numbers: [1, -1, 0], target: 0 },
        { numbers: [0, 0, 0], target: 0 },
    ];

    for (const { numbers, target } of examples) {
        console.log(
            numbers,
            "K=",
            target,
            "->",
            countSubarraysWithSumK(numbers, target)
        );
    }
}


// -----------------------------------------------------------------------------
// 7. LIST SUBARRAYS WITH SUM K
// -----------------------------------------------------------------------------

function subarraysWithSumK(numbers, target) {
    /*
     * Map each prefix sum to every index where it appeared.
     *
     * The conceptual index -1 represents the empty prefix before
     * the first element.
     */
    const positions = new Map();
    positions.set(0, [-1]);

    const result = [];
    let runningSum = 0;

    for (let right = 0; right < numbers.length; right += 1) {
        runningSum += numbers[right];

        const requiredPrefix = runningSum - target;
        const matchingPositions = positions.get(requiredPrefix) ?? [];

        for (const previousIndex of matchingPositions) {
            result.push([previousIndex + 1, right]);
        }

        if (!positions.has(runningSum)) {
            positions.set(runningSum, []);
        }

        positions.get(runningSum).push(right);
    }

    return result;
}

function demonstrateListingSubarrays() {
    const numbers = [1, 2, 1, 2, 1];
    const target = 3;

    console.log("\n=== Subarrays with target sum ===");

    for (const [left, right] of subarraysWithSumK(numbers, target)) {
        console.log(
            `[${left}, ${right}] ->`,
            numbers.slice(left, right + 1)
        );
    }
}


// -----------------------------------------------------------------------------
// 8. LONGEST SUBARRAY WITH SUM K
// -----------------------------------------------------------------------------

function longestSubarrayWithSumK(numbers, target) {
    /*
     * Keep the FIRST occurrence of every prefix sum.
     *
     * Earlier index = longer possible subarray.
     */
    const firstOccurrence = new Map([[0, -1]]);

    let runningSum = 0;
    let bestLength = 0;
    let bestRange = null;

    for (let index = 0; index < numbers.length; index += 1) {
        runningSum += numbers[index];

        const requiredPrefix = runningSum - target;

        if (firstOccurrence.has(requiredPrefix)) {
            const previousIndex = firstOccurrence.get(requiredPrefix);
            const length = index - previousIndex;

            if (length > bestLength) {
                bestLength = length;
                bestRange = [previousIndex + 1, index];
            }
        }

        if (!firstOccurrence.has(runningSum)) {
            firstOccurrence.set(runningSum, index);
        }
    }

    return {
        length: bestLength,
        range: bestRange,
    };
}

function demonstrateLongestSubarray() {
    const numbers = [1, -1, 5, -2, 3];

    console.log("\n=== Longest subarray with sum K ===");
    console.log(
        longestSubarrayWithSumK(numbers, 3)
    );
}


// -----------------------------------------------------------------------------
// 9. ZERO-SUM SUBARRAYS
// -----------------------------------------------------------------------------

function countZeroSumSubarrays(numbers) {
    const frequency = new Map([[0, 1]]);

    let runningSum = 0;
    let count = 0;

    for (const value of numbers) {
        runningSum += value;

        count += frequency.get(runningSum) ?? 0;

        frequency.set(
            runningSum,
            (frequency.get(runningSum) ?? 0) + 1
        );
    }

    return count;
}

function demonstrateZeroSum() {
    console.log("\n=== Zero-sum subarrays ===");

    for (const numbers of [
        [1, -1],
        [1, -1, 1, -1],
        [0, 0],
        [3, -1, -2, 4],
    ]) {
        console.log(numbers, "->", countZeroSumSubarrays(numbers));
    }
}


// -----------------------------------------------------------------------------
// 10. SUBARRAYS DIVISIBLE BY K
// -----------------------------------------------------------------------------

function countSubarraysDivisibleByK(numbers, k) {
    if (k === 0) {
        throw new RangeError("k cannot be zero.");
    }

    /*
     * JavaScript's remainder operator can be negative.
     * Normalize it into [0, |k| - 1].
     */
    const divisor = Math.abs(k);

    function normalizedRemainder(value) {
        return ((value % divisor) + divisor) % divisor;
    }

    const frequency = new Map([[0, 1]]);

    let runningSum = 0;
    let count = 0;

    for (const value of numbers) {
        runningSum += value;

        const remainder = normalizedRemainder(runningSum);

        count += frequency.get(remainder) ?? 0;

        frequency.set(
            remainder,
            (frequency.get(remainder) ?? 0) + 1
        );
    }

    return count;
}

function demonstrateDivisibility() {
    console.log("\n=== Subarrays divisible by K ===");

    const numbers = [4, 5, 0, -2, -3, 1];

    console.log(
        numbers,
        "k=5 ->",
        countSubarraysDivisibleByK(numbers, 5)
    );
}


// -----------------------------------------------------------------------------
// 11. PREFIX XOR
// -----------------------------------------------------------------------------

function countSubarraysWithXorK(numbers, target) {
    /*
     * XOR follows:
     *
     * A ^ B = K
     * B = A ^ K
     *
     * This makes prefix XOR suitable for the same frequency-map pattern.
     */
    const frequency = new Map([[0, 1]]);

    let runningXor = 0;
    let count = 0;

    for (const value of numbers) {
        runningXor ^= value;

        const requiredPrefix = runningXor ^ target;

        count += frequency.get(requiredPrefix) ?? 0;

        frequency.set(
            runningXor,
            (frequency.get(runningXor) ?? 0) + 1
        );
    }

    return count;
}

function demonstratePrefixXor() {
    const numbers = [4, 2, 2, 6, 4];

    console.log("\n=== Prefix XOR ===");
    console.log(
        numbers,
        "target=6 ->",
        countSubarraysWithXorK(numbers, 6)
    );
}


// -----------------------------------------------------------------------------
// 12. TWO-DIMENSIONAL PREFIX SUM
// -----------------------------------------------------------------------------

function build2DPrefixSum(matrix) {
    if (matrix.length === 0) {
        return [[0]];
    }

    const columns = matrix[0].length;

    if (matrix.some(row => row.length !== columns)) {
        throw new Error("Matrix rows must have equal lengths.");
    }

    const prefix = Array.from(
        { length: matrix.length + 1 },
        () => Array(columns + 1).fill(0)
    );

    for (let row = 1; row <= matrix.length; row += 1) {
        for (let column = 1; column <= columns; column += 1) {
            prefix[row][column] =
                matrix[row - 1][column - 1]
                + prefix[row - 1][column]
                + prefix[row][column - 1]
                - prefix[row - 1][column - 1];
        }
    }

    return prefix;
}

function rectangleSum(prefix, top, left, bottom, right) {
    if (
        top < 0 ||
        left < 0 ||
        top > bottom ||
        left > right
    ) {
        throw new RangeError("Invalid rectangle.");
    }

    return (
        prefix[bottom + 1][right + 1]
        - prefix[top][right + 1]
        - prefix[bottom + 1][left]
        + prefix[top][left]
    );
}

function demonstrate2DPrefixSum() {
    const matrix = [
        [3, 1, 2, 5],
        [4, 2, 0, 1],
        [7, 3, 6, 2],
    ];

    const prefix = build2DPrefixSum(matrix);

    console.log("\n=== Two-dimensional prefix sums ===");
    console.table(prefix);

    console.log(
        "Rectangle [0,1] to [2,3] ->",
        rectangleSum(prefix, 0, 1, 2, 3)
    );
}


// -----------------------------------------------------------------------------
// 13. DIFFERENCE ARRAY
// -----------------------------------------------------------------------------

function applyRangeUpdates(size, updates) {
    if (size < 0) {
        throw new RangeError("size cannot be negative.");
    }

    const difference = Array(size + 1).fill(0);

    for (const [left, right, delta] of updates) {
        if (
            left < 0 ||
            right >= size ||
            left > right
        ) {
            throw new RangeError(
                `Invalid update: [${left}, ${right}, ${delta}]`
            );
        }

        difference[left] += delta;
        difference[right + 1] -= delta;
    }

    const result = Array(size).fill(0);
    let runningValue = 0;

    for (let index = 0; index < size; index += 1) {
        runningValue += difference[index];
        result[index] = runningValue;
    }

    return result;
}

function demonstrateDifferenceArray() {
    const updates = [
        [1, 3, 5],
        [2, 5, 2],
        [0, 2, -1],
    ];

    console.log("\n=== Difference array ===");
    console.log(applyRangeUpdates(6, updates));
}


// -----------------------------------------------------------------------------
// 14. PREFIX MINIMUM
// -----------------------------------------------------------------------------

function buildPrefixMinimum(numbers) {
    if (numbers.length === 0) {
        return [];
    }

    const result = [];
    let currentMinimum = numbers[0];

    for (const value of numbers) {
        currentMinimum = Math.min(currentMinimum, value);
        result.push(currentMinimum);
    }

    return result;
}

function demonstratePrefixMinimum() {
    const numbers = [7, 4, 9, 2, 5, 1];

    console.log("\n=== Prefix minimum ===");
    console.log(buildPrefixMinimum(numbers));
}


// -----------------------------------------------------------------------------
// 15. SLIDING WINDOW COMPARISON
// -----------------------------------------------------------------------------

function countPositiveSubarraysWithSumAtMostK(numbers, k) {
    /*
     * This method requires strictly positive values.
     *
     * Positivity gives the window its monotonic behavior:
     * expanding increases the sum and shrinking decreases it.
     */
    if (numbers.some(value => value <= 0)) {
        throw new Error(
            "Sliding-window implementation requires positive values."
        );
    }

    let left = 0;
    let runningSum = 0;
    let count = 0;

    for (let right = 0; right < numbers.length; right += 1) {
        runningSum += numbers[right];

        while (runningSum > k && left <= right) {
            runningSum -= numbers[left];
            left += 1;
        }

        count += right - left + 1;
    }

    return count;
}

function demonstrateSlidingWindow() {
    console.log("\n=== Sliding window comparison ===");

    const numbers = [1, 2, 1, 1];

    console.log(
        numbers,
        "sum <= 3 ->",
        countPositiveSubarraysWithSumAtMostK(numbers, 3)
    );
}


// -----------------------------------------------------------------------------
// 16. VALIDATION
// -----------------------------------------------------------------------------

function randomInteger(random, minimum, maximum) {
    return Math.floor(
        random() * (maximum - minimum + 1)
    ) + minimum;
}

function validateRangeSum() {
    let seed = 42;

    function random() {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 0x100000000;
    }

    for (let trial = 0; trial < 100; trial += 1) {
        const length = randomInteger(random, 1, 30);
        const numbers = Array.from(
            { length },
            () => randomInteger(random, -20, 20)
        );

        const prefix = buildPrefixSum(numbers);

        for (let query = 0; query < 30; query += 1) {
            const left = randomInteger(random, 0, length - 1);
            const right = randomInteger(random, left, length - 1);

            const optimized = rangeSum(prefix, left, right);
            const reference = naiveRangeSum(numbers, left, right);

            if (optimized !== reference) {
                throw new Error("Range-sum validation failed.");
            }
        }
    }

    console.log("\nRange-sum randomized validation: PASSED");
}

function validateSubarraySumK() {
    let seed = 7;

    function random() {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 0x100000000;
    }

    for (let trial = 0; trial < 100; trial += 1) {
        const length = randomInteger(random, 0, 15);

        const numbers = Array.from(
            { length },
            () => randomInteger(random, -5, 5)
        );

        const target = randomInteger(random, -5, 5);

        const optimized = countSubarraysWithSumK(numbers, target);

        let bruteForce = 0;

        for (let left = 0; left < length; left += 1) {
            let sum = 0;

            for (let right = left; right < length; right += 1) {
                sum += numbers[right];

                if (sum === target) {
                    bruteForce += 1;
                }
            }
        }

        if (optimized !== bruteForce) {
            throw new Error("Subarray-sum validation failed.");
        }
    }

    console.log("Subarray-sum randomized validation: PASSED");
}


// -----------------------------------------------------------------------------
// 17. EDGE CASES
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    console.log("\n=== Edge cases ===");

    const cases = [
        [],
        [0],
        [5],
        [-5],
        [0, 0, 0],
        [-1, -2, -3],
        [1_000_000_000_000, -1_000_000_000_000],
    ];

    for (const numbers of cases) {
        console.log(
            JSON.stringify(numbers),
            "prefix=",
            buildPrefixSum(numbers),
            "zeroSumCount=",
            countZeroSumSubarrays(numbers)
        );
    }
}


// -----------------------------------------------------------------------------
// 18. MAIN
// -----------------------------------------------------------------------------

function main() {
    demonstratePrefixConstruction();
    demonstrateRangeQueries();
    demonstrateMultipleQueries();
    demonstrateSubarraySums();
    demonstrateEquilibriumIndex();
    demonstrateSubarraySumK();
    demonstrateListingSubarrays();
    demonstrateLongestSubarray();
    demonstrateZeroSum();
    demonstrateDivisibility();
    demonstratePrefixXor();
    demonstrate2DPrefixSum();
    demonstrateDifferenceArray();
    demonstratePrefixMinimum();
    demonstrateSlidingWindow();
    validateRangeSum();
    validateSubarraySumK();
    demonstrateEdgeCases();

    console.log("\n=== Study file completed successfully ===");
}

main();
