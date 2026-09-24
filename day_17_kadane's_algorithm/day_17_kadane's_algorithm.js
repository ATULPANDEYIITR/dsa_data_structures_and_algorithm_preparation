/**
 * Day 17 — Kadane's Algorithm
 * ============================
 *
 * A self-contained JavaScript study file for maximum-subarray problems.
 *
 * The implementation progresses from:
 *   - basic subarray enumeration
 *   - brute force
 *   - running sums
 *   - Kadane's algorithm
 *   - index reconstruction
 *   - negative values
 *   - tie-breaking
 *   - minimum subarray
 *   - circular subarrays
 *   - deletion variants
 *   - fixed-length windows
 *   - prefix sums
 *   - streaming computation
 *   - testing
 *   - performance considerations
 *
 * Run with:
 *   node day17-kadanes-algorithm.js
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. Output helpers
// -----------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function result(label, value) {
    console.log(`${label.padEnd(36)}:`, value);
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

// -----------------------------------------------------------------------------
// 2. Validation
// -----------------------------------------------------------------------------

function validateNonEmptyNumberArray(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Input must be an array.");
    }

    if (values.length === 0) {
        throw new RangeError("Input array must not be empty.");
    }

    for (const value of values) {
        if (typeof value !== "number" || Number.isNaN(value)) {
            throw new TypeError("Every element must be a valid number.");
        }
    }
}

// -----------------------------------------------------------------------------
// 3. Enumerating subarrays
// -----------------------------------------------------------------------------

function allSubarrays(values) {
    validateNonEmptyNumberArray(values);

    const subarrays = [];

    for (let start = 0; start < values.length; start += 1) {
        for (let end = start; end < values.length; end += 1) {
            subarrays.push({
                start,
                end,
                values: values.slice(start, end + 1),
            });
        }
    }

    return subarrays;
}

// -----------------------------------------------------------------------------
// 4. O(n^3) brute force
// -----------------------------------------------------------------------------

function maximumSubarrayCubic(values) {
    validateNonEmptyNumberArray(values);

    let bestSum = values[0];
    let bestStart = 0;
    let bestEnd = 0;

    for (let start = 0; start < values.length; start += 1) {
        for (let end = start; end < values.length; end += 1) {
            let currentSum = 0;

            for (let index = start; index <= end; index += 1) {
                currentSum += values[index];
            }

            if (currentSum > bestSum) {
                bestSum = currentSum;
                bestStart = start;
                bestEnd = end;
            }
        }
    }

    return {
        sum: bestSum,
        start: bestStart,
        end: bestEnd,
        values: values.slice(bestStart, bestEnd + 1),
    };
}

// -----------------------------------------------------------------------------
// 5. O(n^2) running-sum solution
// -----------------------------------------------------------------------------

function maximumSubarrayQuadratic(values) {
    validateNonEmptyNumberArray(values);

    let bestSum = values[0];
    let bestStart = 0;
    let bestEnd = 0;

    for (let start = 0; start < values.length; start += 1) {
        let currentSum = 0;

        for (let end = start; end < values.length; end += 1) {
            currentSum += values[end];

            if (currentSum > bestSum) {
                bestSum = currentSum;
                bestStart = start;
                bestEnd = end;
            }
        }
    }

    return {
        sum: bestSum,
        start: bestStart,
        end: bestEnd,
        values: values.slice(bestStart, bestEnd + 1),
    };
}

// -----------------------------------------------------------------------------
// 6. Standard Kadane's algorithm
// -----------------------------------------------------------------------------

function kadane(values) {
    validateNonEmptyNumberArray(values);

    let currentSum = values[0];
    let bestSum = values[0];

    for (let index = 1; index < values.length; index += 1) {
        const value = values[index];

        // Either:
        //   1. start a new subarray with value, or
        //   2. extend the previous subarray.
        currentSum = Math.max(value, currentSum + value);

        // bestSum stores the best subarray found anywhere so far.
        bestSum = Math.max(bestSum, currentSum);
    }

    return bestSum;
}

// -----------------------------------------------------------------------------
// 7. Kadane with indices
// -----------------------------------------------------------------------------

function kadaneWithIndices(values) {
    validateNonEmptyNumberArray(values);

    let currentSum = values[0];
    let bestSum = values[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let index = 1; index < values.length; index += 1) {
        const value = values[index];

        if (value > currentSum + value) {
            currentSum = value;
            currentStart = index;
        } else {
            currentSum += value;
        }

        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = index;
        }
    }

    return {
        sum: bestSum,
        start: bestStart,
        end: bestEnd,
        values: values.slice(bestStart, bestEnd + 1),
    };
}

// -----------------------------------------------------------------------------
// 8. Step-by-step Kadane trace
// -----------------------------------------------------------------------------

function traceKadane(values) {
    validateNonEmptyNumberArray(values);

    let currentSum = values[0];
    let bestSum = values[0];

    console.log(
        "Index".padStart(5),
        "Value".padStart(8),
        "Current".padStart(12),
        "Best".padStart(12),
        "Decision"
    );

    console.log("-".repeat(62));

    console.log(
        String(0).padStart(5),
        String(values[0]).padStart(8),
        String(currentSum).padStart(12),
        String(bestSum).padStart(12),
        "start"
    );

    for (let index = 1; index < values.length; index += 1) {
        const value = values[index];
        const extended = currentSum + value;

        let decision;

        if (value > extended) {
            currentSum = value;
            decision = "reset";
        } else {
            currentSum = extended;
            decision = "extend";
        }

        bestSum = Math.max(bestSum, currentSum);

        console.log(
            String(index).padStart(5),
            String(value).padStart(8),
            String(currentSum).padStart(12),
            String(bestSum).padStart(12),
            decision
        );
    }
}

// -----------------------------------------------------------------------------
// 9. Minimum subarray
// -----------------------------------------------------------------------------

function minimumSubarray(values) {
    validateNonEmptyNumberArray(values);

    let currentSum = values[0];
    let bestSum = values[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let index = 1; index < values.length; index += 1) {
        const value = values[index];

        if (value < currentSum + value) {
            currentSum = value;
            currentStart = index;
        } else {
            currentSum += value;
        }

        if (currentSum < bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = index;
        }
    }

    return {
        sum: bestSum,
        start: bestStart,
        end: bestEnd,
        values: values.slice(bestStart, bestEnd + 1),
    };
}

// -----------------------------------------------------------------------------
// 10. Maximum circular subarray
// -----------------------------------------------------------------------------

function maximumCircularSubarray(values) {
    validateNonEmptyNumberArray(values);

    const normal = kadaneWithIndices(values);

    if (normal.sum < 0) {
        return normal;
    }

    const minimum = minimumSubarray(values);
    const total = values.reduce((sum, value) => sum + value, 0);
    const wrappedSum = total - minimum.sum;

    if (wrappedSum <= normal.sum) {
        return normal;
    }

    const wrappedValues = [
        ...values.slice(minimum.end + 1),
        ...values.slice(0, minimum.start),
    ];

    return {
        sum: wrappedSum,
        start: minimum.end + 1,
        end: minimum.start - 1,
        values: wrappedValues,
        wraps: true,
    };
}

// -----------------------------------------------------------------------------
// 11. Maximum subarray with one deletion
// -----------------------------------------------------------------------------

function maximumSubarrayOneDeletion(values) {
    validateNonEmptyNumberArray(values);

    let keep = values[0];
    let deleted = -Infinity;
    let best = values[0];

    for (let index = 1; index < values.length; index += 1) {
        const value = values[index];

        // Deleting the current value means the previous keep state is used.
        // Otherwise an earlier deletion has already occurred.
        const newDeleted = Math.max(
            deleted + value,
            keep
        );

        const newKeep = Math.max(
            value,
            keep + value
        );

        keep = newKeep;
        deleted = newDeleted;

        best = Math.max(best, keep, deleted);
    }

    return best;
}

// -----------------------------------------------------------------------------
// 12. Maximum subarray with at most k deletions
// -----------------------------------------------------------------------------

function maximumSubarrayKDeletions(values, k) {
    validateNonEmptyNumberArray(values);

    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer.");
    }

    k = Math.min(k, values.length - 1);

    const negativeInfinity = Number.NEGATIVE_INFINITY;
    const dp = Array(k + 1).fill(negativeInfinity);

    dp[0] = values[0];

    let best = values[0];

    for (let index = 1; index < values.length; index += 1) {
        const value = values[index];
        const previous = [...dp];

        dp[0] = Math.max(
            value,
            previous[0] + value
        );

        for (let deletions = 1; deletions <= k; deletions += 1) {
            dp[deletions] = Math.max(
                previous[deletions] + value,
                previous[deletions - 1]
            );
        }

        best = Math.max(best, ...dp);
    }

    return best;
}

// -----------------------------------------------------------------------------
// 13. Maximum fixed-length subarray
// -----------------------------------------------------------------------------

function maximumFixedLengthSubarray(values, length) {
    validateNonEmptyNumberArray(values);

    if (!Number.isInteger(length) || length <= 0) {
        throw new RangeError("Window length must be a positive integer.");
    }

    if (length > values.length) {
        throw new RangeError("Window length exceeds array length.");
    }

    let currentSum = 0;

    for (let index = 0; index < length; index += 1) {
        currentSum += values[index];
    }

    let bestSum = currentSum;
    let bestStart = 0;

    for (
        let start = 1;
        start <= values.length - length;
        start += 1
    ) {
        currentSum += values[start + length - 1];
        currentSum -= values[start - 1];

        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = start;
        }
    }

    return {
        sum: bestSum,
        start: bestStart,
        end: bestStart + length - 1,
        values: values.slice(
            bestStart,
            bestStart + length
        ),
    };
}

// -----------------------------------------------------------------------------
// 14. Prefix-sum formulation
// -----------------------------------------------------------------------------

function maximumSubarrayPrefixSum(values) {
    validateNonEmptyNumberArray(values);

    let prefixSum = 0;
    let minimumPrefix = 0;
    let bestSum = values[0];

    for (const value of values) {
        prefixSum += value;

        bestSum = Math.max(
            bestSum,
            prefixSum - minimumPrefix
        );

        minimumPrefix = Math.min(
            minimumPrefix,
            prefixSum
        );
    }

    return bestSum;
}

// -----------------------------------------------------------------------------
// 15. Streaming Kadane
// -----------------------------------------------------------------------------

class StreamingKadane {
    constructor() {
        this.currentSum = null;
        this.bestSum = null;
        this.currentStart = 0;
        this.bestStart = 0;
        this.bestEnd = 0;
        this.position = -1;
    }

    add(value) {
        if (typeof value !== "number" || Number.isNaN(value)) {
            throw new TypeError("Streaming value must be a valid number.");
        }

        this.position += 1;

        if (this.currentSum === null) {
            this.currentSum = value;
            this.bestSum = value;
            this.currentStart = this.position;
            this.bestStart = this.position;
            this.bestEnd = this.position;
            return;
        }

        if (value > this.currentSum + value) {
            this.currentSum = value;
            this.currentStart = this.position;
        } else {
            this.currentSum += value;
        }

        if (this.currentSum > this.bestSum) {
            this.bestSum = this.currentSum;
            this.bestStart = this.currentStart;
            this.bestEnd = this.position;
        }
    }

    getResult() {
        if (this.bestSum === null) {
            throw new Error("No values have been added.");
        }

        return {
            sum: this.bestSum,
            start: this.bestStart,
            end: this.bestEnd,
        };
    }
}

// -----------------------------------------------------------------------------
// 16. Generator-based streaming input
// -----------------------------------------------------------------------------

function* numberGenerator(values) {
    for (const value of values) {
        yield value;
    }
}

function kadaneFromIterable(iterable) {
    let initialized = false;
    let currentSum = 0;
    let bestSum = 0;

    for (const value of iterable) {
        if (typeof value !== "number" || Number.isNaN(value)) {
            throw new TypeError("Iterable contains an invalid number.");
        }

        if (!initialized) {
            currentSum = value;
            bestSum = value;
            initialized = true;
            continue;
        }

        currentSum = Math.max(
            value,
            currentSum + value
        );

        bestSum = Math.max(
            bestSum,
            currentSum
        );
    }

    if (!initialized) {
        throw new Error("Iterable contains no values.");
    }

    return bestSum;
}

// -----------------------------------------------------------------------------
// 17. Intentionally flawed empty-allowed implementation
// -----------------------------------------------------------------------------

function incorrectEmptyAllowedKadane(values) {
    let currentSum = 0;
    let bestSum = 0;

    for (const value of values) {
        currentSum = Math.max(
            0,
            currentSum + value
        );

        bestSum = Math.max(
            bestSum,
            currentSum
        );
    }

    return bestSum;
}

// -----------------------------------------------------------------------------
// 18. Deterministic tests
// -----------------------------------------------------------------------------

function runTests() {
    assert(
        kadane([1, 2, 3]) === 6,
        "positive values"
    );

    assert(
        kadane([-5, -2, -9]) === -2,
        "all negative values"
    );

    assert(
        kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]) === 6,
        "classic example"
    );

    const indexed = kadaneWithIndices(
        [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    );

    assert(indexed.sum === 6, "index reconstruction sum");
    assert(
        JSON.stringify(indexed.values) ===
        JSON.stringify([4, -1, 2, 1]),
        "index reconstruction values"
    );

    assert(
        minimumSubarray([3, -4, 2, -3, -1, 7]).sum === -6,
        "minimum subarray"
    );

    assert(
        maximumSubarrayOneDeletion([1, -2, 0, 3]) === 4,
        "one deletion"
    );

    assert(
        maximumSubarrayOneDeletion([-1, -1, -1]) === -1,
        "one deletion with negative values"
    );

    assert(
        maximumSubarrayKDeletions(
            [1, -2, 0, 3],
            1
        ) === 4,
        "k deletions"
    );

    assert(
        maximumFixedLengthSubarray(
            [2, -1, 5, -3, 4],
            3
        ).sum === 6,
        "fixed window"
    );

    assert(
        maximumSubarrayPrefixSum(
            [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        ) === 6,
        "prefix formulation"
    );

    assert(
        incorrectEmptyAllowedKadane([-8, -3, -10]) === 0,
        "empty-allowed variant"
    );

    console.log("All deterministic tests passed.");
}

// -----------------------------------------------------------------------------
// 19. Randomized verification
// -----------------------------------------------------------------------------

function randomInteger(random, minimum, maximum) {
    return Math.floor(
        random() * (maximum - minimum + 1)
    ) + minimum;
}

function runRandomizedVerification() {
    // A deterministic pseudo-random generator makes test results reproducible.
    let state = 17;

    function random() {
        state = (
            state * 1664525 +
            1013904223
        ) >>> 0;

        return state / 4294967296;
    }

    for (let trial = 0; trial < 500; trial += 1) {
        const length = randomInteger(random, 1, 20);
        const values = [];

        for (let index = 0; index < length; index += 1) {
            values.push(
                randomInteger(random, -20, 20)
            );
        }

        const cubic = maximumSubarrayCubic(values).sum;
        const quadratic = maximumSubarrayQuadratic(values).sum;
        const linear = kadane(values);
        const prefix = maximumSubarrayPrefixSum(values);

        assert(
            cubic === quadratic &&
            quadratic === linear &&
            linear === prefix,
            `Randomized mismatch: ${JSON.stringify(values)}`
        );
    }

    console.log("500 randomized verification trials passed.");
}

// -----------------------------------------------------------------------------
// 20. Performance demonstration
// -----------------------------------------------------------------------------

function performanceDemo() {
    const size = 100_000;
    const values = new Array(size);

    for (let index = 0; index < size; index += 1) {
        values[index] = (
            Math.floor(
                Math.sin(index * 0.017) * 50
            ) - 10
        );
    }

    console.time("Kadane on 100,000 values");
    const answer = kadane(values);
    console.timeEnd("Kadane on 100,000 values");

    result("Large-input answer", answer);
}

// -----------------------------------------------------------------------------
// 21. Main educational demonstration
// -----------------------------------------------------------------------------

function main() {
    section("Day 17 — Kadane's Algorithm");

    const values = [
        -2, 1, -3, 4,
        -1, 2, 1, -5, 4
    ];

    section("1. Maximum-subarray definition");

    result("Input", values);
    result(
        "Cubic brute force",
        maximumSubarrayCubic(values)
    );
    result(
        "Quadratic running sum",
        maximumSubarrayQuadratic(values)
    );
    result(
        "Kadane",
        kadane(values)
    );
    result(
        "Kadane with indices",
        kadaneWithIndices(values)
    );

    section("2. Kadane state transitions");

    traceKadane(values);

    section("3. Negative values");

    const negativeValues = [
        -8, -3, -10, -4
    ];

    result(
        "Input",
        negativeValues
    );

    result(
        "Correct non-empty answer",
        kadane(negativeValues)
    );

    result(
        "Incorrect empty-allowed answer",
        incorrectEmptyAllowedKadane(negativeValues)
    );

    section("4. Edge cases");

    const edgeCases = [
        [7],
        [-7],
        [2, 4, 1, 8],
        [-8, -3, -10],
        [0, 0, 0],
        [5, -100, 6, 7],
        [10, -10, 10, -10, 10],
    ];

    for (const testCase of edgeCases) {
        result(
            JSON.stringify(testCase),
            kadaneWithIndices(testCase)
        );
    }

    section("5. Minimum subarray");

    result(
        "Input",
        [3, -4, 2, -3, -1, 7]
    );

    result(
        "Minimum",
        minimumSubarray([3, -4, 2, -3, -1, 7])
    );

    section("6. Circular maximum subarray");

    const circularCases = [
        [5, -3, 5],
        [3, -2, 2, -3],
        [-3, -2, -1],
        [1, 2, 3, 4],
    ];

    for (const testCase of circularCases) {
        result(
            JSON.stringify(testCase),
            maximumCircularSubarray(testCase)
        );
    }

    section("7. Maximum subarray with one deletion");

    const deletionCases = [
        [1, -2, 0, 3],
        [1, -2, -2, 3],
        [-1, -1, -1],
        [8, -1, 6, -10, 5],
    ];

    for (const testCase of deletionCases) {
        result(
            JSON.stringify(testCase),
            maximumSubarrayOneDeletion(testCase)
        );
    }

    section("8. Maximum subarray with k deletions");

    const deletionInput = [
        5, -100, 6, 7, -2, 4
    ];

    for (let k = 0; k <= 3; k += 1) {
        result(
            `k = ${k}`,
            maximumSubarrayKDeletions(
                deletionInput,
                k
            )
        );
    }

    section("9. Fixed-length windows");

    const fixedWindowInput = [
        2, -1, 5, -3, 4, 6, -2
    ];

    for (const length of [1, 2, 3, 4]) {
        result(
            `Length = ${length}`,
            maximumFixedLengthSubarray(
                fixedWindowInput,
                length
            )
        );
    }

    section("10. Streaming Kadane");

    const stream = new StreamingKadane();

    for (const value of values) {
        stream.add(value);

        result(
            `After adding ${value}`,
            stream.getResult()
        );
    }

    section("11. Generator-based processing");

    result(
        "Generator result",
        kadaneFromIterable(
            numberGenerator(values)
        )
    );

    section("12. Prefix-sum interpretation");

    result(
        "Kadane",
        kadane(values)
    );

    result(
        "Prefix-sum method",
        maximumSubarrayPrefixSum(values)
    );

    section("13. Testing");

    runTests();
    runRandomizedVerification();

    section("14. Performance");

    performanceDemo();

    section("15. Algorithmic invariants");

    console.log(
        "currentSum = maximum sum of a non-empty subarray ending at the current index."
    );

    console.log(
        "bestSum = maximum sum observed among all prefixes processed so far."
    );

    console.log(
        "At each value, the only decision is whether to extend the current"
        + " candidate or start a new candidate."
    );

    section("16. Complexity");

    console.table([
        {
            algorithm: "Cubic brute force",
            time: "O(n^3)",
            space: "O(1)",
        },
        {
            algorithm: "Quadratic running sum",
            time: "O(n^2)",
            space: "O(1)",
        },
        {
            algorithm: "Kadane",
            time: "O(n)",
            space: "O(1)",
        },
        {
            algorithm: "Prefix-sum scan",
            time: "O(n)",
            space: "O(1)",
        },
        {
            algorithm: "Circular Kadane",
            time: "O(n)",
            space: "O(1)",
        },
        {
            algorithm: "One-deletion DP",
            time: "O(n)",
            space: "O(1)",
        },
        {
            algorithm: "k-deletion DP",
            time: "O(nk)",
            space: "O(k)",
        },
    ]);
}

main();
