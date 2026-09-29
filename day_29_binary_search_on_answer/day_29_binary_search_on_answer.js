/*
 * Binary Search on Answer
 * ========================
 *
 * This file demonstrates binary search over a numeric answer space rather
 * than over a sorted input array.
 *
 * Main idea:
 *
 *   Find the smallest x for which feasible(x) is true
 *   OR
 *   Find the largest x for which feasible(x) is true
 *
 * The important property is monotonic feasibility:
 *
 *   false false false true true true
 *   true true true false false false
 *
 * JavaScript-specific considerations demonstrated here include:
 * - functions as first-class values
 * - closures for feasibility predicates
 * - Number-safe integer arithmetic
 * - classes and static methods
 * - array processing
 * - validation and exceptions
 * - BigInt for values beyond Number's exact integer range
 * - performance-oriented early exits
 * - reusable binary-search abstractions
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. BASIC SEARCH PRIMITIVES
// -----------------------------------------------------------------------------

function firstTrue(low, high, feasible) {
    if (!Number.isInteger(low) || !Number.isInteger(high)) {
        throw new TypeError("Bounds must be integers.");
    }

    if (low > high) {
        throw new RangeError("low must not exceed high.");
    }

    while (low < high) {
        const mid = low + Math.floor((high - low) / 2);

        if (feasible(mid)) {
            high = mid;
        } else {
            low = mid + 1;
        }
    }

    return low;
}

function lastTrue(low, high, feasible) {
    if (!Number.isInteger(low) || !Number.isInteger(high)) {
        throw new TypeError("Bounds must be integers.");
    }

    if (low > high) {
        throw new RangeError("low must not exceed high.");
    }

    while (low < high) {
        // Upper midpoint is essential for progress in last-true searches.
        const mid = low + Math.floor((high - low + 1) / 2);

        if (feasible(mid)) {
            low = mid;
        } else {
            high = mid - 1;
        }
    }

    return low;
}

// -----------------------------------------------------------------------------
// 2. SIMPLE MINIMUM FEASIBLE ANSWER
// -----------------------------------------------------------------------------

function minimumIntegerWithSquareAtLeast(target) {
    if (!Number.isSafeInteger(target) || target < 0) {
        throw new RangeError("target must be a non-negative safe integer.");
    }

    if (target <= 1) {
        return target;
    }

    return firstTrue(0, target, (x) => x * x >= target);
}

console.log("Minimum square-root-style answers:");

for (const target of [0, 1, 2, 9, 10, 24, 100]) {
    const answer = minimumIntegerWithSquareAtLeast(target);
    console.log(
        `target=${target}, answer=${answer}, square=${answer * answer}`
    );
}

// -----------------------------------------------------------------------------
// 3. MINIMUM SHIPPING CAPACITY
// -----------------------------------------------------------------------------

function validatePositiveIntegerArray(values, name) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new TypeError(`${name} must be a non-empty array.`);
    }

    for (const value of values) {
        if (!Number.isSafeInteger(value) || value <= 0) {
            throw new RangeError(
                `${name} must contain positive safe integers.`
            );
        }
    }
}

function minimumShippingCapacity(weights, days) {
    validatePositiveIntegerArray(weights, "weights");

    if (!Number.isSafeInteger(days) || days <= 0) {
        throw new RangeError("days must be a positive integer.");
    }

    let low = Math.max(...weights);
    let high = weights.reduce((sum, weight) => sum + weight, 0);

    function feasible(capacity) {
        let requiredDays = 1;
        let currentLoad = 0;

        for (const weight of weights) {
            if (currentLoad + weight <= capacity) {
                currentLoad += weight;
            } else {
                requiredDays += 1;
                currentLoad = weight;

                // Early termination avoids unnecessary work.
                if (requiredDays > days) {
                    return false;
                }
            }
        }

        return true;
    }

    return firstTrue(low, high, feasible);
}

console.log("\nShipping capacity:");

const shippingCases = [
    { weights: [1, 2, 3, 1, 1], days: 4 },
    { weights: [3, 2, 2, 4, 1, 4], days: 3 },
    { weights: [5, 5, 5, 5], days: 2 }
];

for (const testCase of shippingCases) {
    console.log(
        testCase,
        "->",
        minimumShippingCapacity(testCase.weights, testCase.days)
    );
}

// -----------------------------------------------------------------------------
// 4. MINIMUM PROCESSING SPEED
// -----------------------------------------------------------------------------

function minimumProcessingSpeed(workloads, hours) {
    validatePositiveIntegerArray(workloads, "workloads");

    if (!Number.isSafeInteger(hours) || hours <= 0) {
        throw new RangeError("hours must be positive.");
    }

    const low = 1;
    const high = Math.max(...workloads);

    function feasible(speed) {
        let requiredHours = 0;

        for (const workload of workloads) {
            // Ceiling(workload / speed) without floating-point precision
            // problems for ordinary safe integers.
            requiredHours += Math.ceil(workload / speed);

            if (requiredHours > hours) {
                return false;
            }
        }

        return true;
    }

    return firstTrue(low, high, feasible);
}

console.log("\nMinimum processing speed:");

console.log(
    minimumProcessingSpeed([3, 6, 7, 11], 8)
);

console.log(
    minimumProcessingSpeed([30, 11, 23, 4, 20], 5)
);

// -----------------------------------------------------------------------------
// 5. CONTIGUOUS ALLOCATION
// -----------------------------------------------------------------------------

function minimumLargestPartitionSum(values, groups) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new TypeError("values must be a non-empty array.");
    }

    if (!values.every(Number.isSafeInteger) || values.some((v) => v < 0)) {
        throw new RangeError("values must contain non-negative integers.");
    }

    if (!Number.isSafeInteger(groups) || groups <= 0) {
        throw new RangeError("groups must be positive.");
    }

    groups = Math.min(groups, values.length);

    const low = Math.max(...values);
    const high = values.reduce((sum, value) => sum + value, 0);

    function feasible(limit) {
        let partitionCount = 1;
        let currentSum = 0;

        for (const value of values) {
            if (currentSum + value <= limit) {
                currentSum += value;
            } else {
                partitionCount += 1;
                currentSum = value;

                if (partitionCount > groups) {
                    return false;
                }
            }
        }

        return true;
    }

    return firstTrue(low, high, feasible);
}

console.log("\nContiguous allocation:");

console.log(
    minimumLargestPartitionSum([7, 2, 5, 10, 8], 2)
);

console.log(
    minimumLargestPartitionSum([1, 2, 3, 4, 5], 2)
);

// -----------------------------------------------------------------------------
// 6. MAXIMUM MINIMUM DISTANCE
// -----------------------------------------------------------------------------

function maximumMinimumDistance(positions, objects) {
    if (!Array.isArray(positions) || positions.length === 0) {
        throw new TypeError("positions must be non-empty.");
    }

    if (!positions.every(Number.isSafeInteger)) {
        throw new RangeError("positions must contain safe integers.");
    }

    if (!Number.isSafeInteger(objects) || objects <= 0) {
        throw new RangeError("objects must be positive.");
    }

    const sorted = [...new Set(positions)].sort((a, b) => a - b);

    if (objects > sorted.length) {
        throw new RangeError(
            "Cannot place more objects than distinct positions."
        );
    }

    const low = 0;
    const high = sorted[sorted.length - 1] - sorted[0];

    function feasible(distance) {
        let selected = 1;
        let lastPosition = sorted[0];

        for (let i = 1; i < sorted.length; i += 1) {
            if (sorted[i] - lastPosition >= distance) {
                selected += 1;
                lastPosition = sorted[i];

                if (selected >= objects) {
                    return true;
                }
            }
        }

        return selected >= objects;
    }

    return lastTrue(low, high, feasible);
}

console.log("\nMaximum minimum distance:");

console.log(
    maximumMinimumDistance([1, 2, 4, 8, 9], 3)
);

// -----------------------------------------------------------------------------
// 7. CLASS-BASED ANSWER SEARCH
// -----------------------------------------------------------------------------

class AnswerSpaceSearch {
    static firstFeasible(low, high, feasible) {
        return firstTrue(low, high, feasible);
    }

    static lastFeasible(low, high, feasible) {
        return lastTrue(low, high, feasible);
    }

    static traceFirstFeasible(low, high, feasible) {
        const trace = [];

        while (low < high) {
            const previousLow = low;
            const previousHigh = high;
            const mid = low + Math.floor((high - low) / 2);
            const result = feasible(mid);

            trace.push({
                low: previousLow,
                mid,
                high: previousHigh,
                feasible: result
            });

            if (result) {
                high = mid;
            } else {
                low = mid + 1;
            }
        }

        return {
            answer: low,
            trace
        };
    }
}

console.log("\nSearch trace:");

const tracedSearch = AnswerSpaceSearch.traceFirstFeasible(
    1,
    100,
    (value) => value >= 73
);

console.table(tracedSearch.trace);
console.log("Answer:", tracedSearch.answer);

// -----------------------------------------------------------------------------
// 8. ADVANCED: BIGINT ANSWER SPACE
// -----------------------------------------------------------------------------

/*
 * JavaScript Number represents integers exactly only through
 * Number.MAX_SAFE_INTEGER. For larger integer answer spaces, BigInt is the
 * appropriate standard-library primitive.
 *
 * BigInt values cannot be mixed directly with Number values in arithmetic.
 */

function firstTrueBigInt(low, high, feasible) {
    if (typeof low !== "bigint" || typeof high !== "bigint") {
        throw new TypeError("BigInt bounds are required.");
    }

    if (low > high) {
        throw new RangeError("low must not exceed high.");
    }

    while (low < high) {
        const mid = low + (high - low) / 2n;

        if (feasible(mid)) {
            high = mid;
        } else {
            low = mid + 1n;
        }
    }

    return low;
}

function minimumBigIntSquareRootStyle(target) {
    if (typeof target !== "bigint" || target < 0n) {
        throw new RangeError("target must be a non-negative BigInt.");
    }

    if (target <= 1n) {
        return target;
    }

    return firstTrueBigInt(
        0n,
        target,
        (x) => x * x >= target
    );
}

const hugeTarget = 10_000_000_000_000_000_000n;
const hugeAnswer = minimumBigIntSquareRootStyle(hugeTarget);

console.log("\nBigInt answer-space search:");
console.log("target:", hugeTarget.toString());
console.log("answer:", hugeAnswer.toString());

// -----------------------------------------------------------------------------
// 9. FEASIBILITY AS A CLOSURE
// -----------------------------------------------------------------------------

function createShippingFeasibilityChecker(weights, days) {
    validatePositiveIntegerArray(weights, "weights");

    return function feasible(capacity) {
        let usedDays = 1;
        let currentLoad = 0;

        for (const weight of weights) {
            if (currentLoad + weight <= capacity) {
                currentLoad += weight;
            } else {
                usedDays += 1;
                currentLoad = weight;
            }
        }

        return usedDays <= days;
    };
}

const shippingFeasible = createShippingFeasibilityChecker(
    [4, 7, 2, 9, 5],
    3
);

console.log("\nClosure-based feasibility:");

for (const capacity of [9, 10, 11, 12, 13, 14, 20]) {
    console.log(
        `capacity=${capacity}: feasible=${shippingFeasible(capacity)}`
    );
}

// -----------------------------------------------------------------------------
// 10. BRUTE FORCE REFERENCE IMPLEMENTATION
// -----------------------------------------------------------------------------

function bruteForceShippingCapacity(weights, days) {
    const low = Math.max(...weights);
    const high = weights.reduce((sum, value) => sum + value, 0);

    for (let capacity = low; capacity <= high; capacity += 1) {
        let usedDays = 1;
        let currentLoad = 0;

        for (const weight of weights) {
            if (currentLoad + weight <= capacity) {
                currentLoad += weight;
            } else {
                usedDays += 1;
                currentLoad = weight;
            }
        }

        if (usedDays <= days) {
            return capacity;
        }
    }

    throw new Error("No feasible answer.");
}

function validateShippingAlgorithm() {
    const cases = [
        { weights: [1, 2, 3], days: 2 },
        { weights: [2, 2, 2, 2], days: 2 },
        { weights: [5, 1, 1, 1], days: 3 },
        { weights: [7, 3, 4, 2], days: 2 }
    ];

    for (const { weights, days } of cases) {
        const optimized = minimumShippingCapacity(weights, days);
        const reference = bruteForceShippingCapacity(weights, days);

        if (optimized !== reference) {
            throw new Error(
                `Validation failure: optimized=${optimized}, ` +
                `reference=${reference}`
            );
        }

        console.log(
            `Validated ${JSON.stringify(weights)} / days=${days}: ${optimized}`
        );
    }
}

// -----------------------------------------------------------------------------
// 11. EDGE CASES
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    console.log("\nEdge cases:");

    console.log(
        "Single package:",
        minimumShippingCapacity([42], 1)
    );

    console.log(
        "Many available days:",
        minimumShippingCapacity([4, 5, 6], 10)
    );

    console.log(
        "One delivery day:",
        minimumShippingCapacity([4, 5, 6], 1)
    );

    console.log(
        "One workload:",
        minimumProcessingSpeed([100], 100)
    );

    console.log(
        "One allocation group:",
        minimumLargestPartitionSum([3, 1, 8, 2], 1)
    );

    const invalidOperations = [
        () => minimumShippingCapacity([], 3),
        () => minimumShippingCapacity([1, 2], 0),
        () => minimumProcessingSpeed([], 3),
        () => maximumMinimumDistance([1, 2], 3)
    ];

    for (const operation of invalidOperations) {
        try {
            operation();
        } catch (error) {
            console.log(
                `Expected ${error.name}: ${error.message}`
            );
        }
    }
}

// -----------------------------------------------------------------------------
// 12. PERFORMANCE DISCUSSION
// -----------------------------------------------------------------------------

function explainComplexity() {
    console.log("\nComplexity:");

    console.log(
        "Shipping: O(n log R), where R is the numeric capacity range."
    );

    console.log(
        "Speed: O(n log R), where R is the speed range."
    );

    console.log(
        "Allocation: O(n log R), where R is the maximum possible answer range."
    );

    console.log(
        "Distance: O(n log R), where R is the coordinate-distance range."
    );

    console.log(
        "Binary search itself performs O(log R) feasibility evaluations."
    );

    console.log(
        "If feasibility is O(n), the complete algorithm is O(n log R)."
    );
}

// -----------------------------------------------------------------------------
// 13. MAIN CASE STUDY
// -----------------------------------------------------------------------------

function runCaseStudy() {
    console.log("\nIntegrated case study:");

    const projectEffort = [120, 80, 200, 150, 90, 60];
    const engineers = 3;

    const maximumEngineerLoad = minimumLargestPartitionSum(
        projectEffort,
        engineers
    );

    console.log(
        "Minimum possible maximum engineer workload:",
        maximumEngineerLoad
    );

    const packages = [10, 20, 30, 40, 50];

    const capacity = minimumShippingCapacity(
        packages,
        3
    );

    console.log(
        "Minimum shipping capacity:",
        capacity
    );

    const workloads = [50, 120, 80, 30];

    const speed = minimumProcessingSpeed(
        workloads,
        7
    );

    console.log(
        "Minimum processing speed:",
        speed
    );

    const locations = [0, 4, 9, 15, 21, 30];

    const spacing = maximumMinimumDistance(
        locations,
        4
    );

    console.log(
        "Maximum minimum spacing:",
        spacing
    );
}

// -----------------------------------------------------------------------------
// 14. ASSERTION-STYLE TESTS
// -----------------------------------------------------------------------------

function assertEqual(actual, expected, description) {
    if (actual !== expected) {
        throw new Error(
            `${description}: expected ${expected}, received ${actual}`
        );
    }
}

function runTests() {
    assertEqual(
        minimumIntegerWithSquareAtLeast(0),
        0,
        "sqrt target 0"
    );

    assertEqual(
        minimumIntegerWithSquareAtLeast(10),
        4,
        "sqrt target 10"
    );

    assertEqual(
        minimumShippingCapacity([1, 2, 3, 1, 1], 4),
        3,
        "shipping case 1"
    );

    assertEqual(
        minimumShippingCapacity([3, 2, 2, 4, 1, 4], 3),
        6,
        "shipping case 2"
    );

    assertEqual(
        minimumProcessingSpeed([3, 6, 7, 11], 8),
        4,
        "speed case 1"
    );

    assertEqual(
        minimumLargestPartitionSum([7, 2, 5, 10, 8], 2),
        18,
        "allocation case"
    );

    assertEqual(
        maximumMinimumDistance([1, 2, 4, 8, 9], 3),
        3,
        "distance case"
    );

    assertEqual(
        Number(minimumBigIntSquareRootStyle(10_000_000_000_000_000_000n)),
        100_000_000,
        "BigInt square-root case"
    );

    console.log("\nAll JavaScript tests passed.");
}

// -----------------------------------------------------------------------------
// 15. PROGRAM ENTRY
// -----------------------------------------------------------------------------

function main() {
    console.log("BINARY SEARCH ON ANSWER");
    console.log("=======================");

    validateShippingAlgorithm();
    demonstrateEdgeCases();
    explainComplexity();
    runCaseStudy();
    runTests();
}

main();
