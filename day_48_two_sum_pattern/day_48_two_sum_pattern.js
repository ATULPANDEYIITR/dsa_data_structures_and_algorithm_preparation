"use strict";

/*
 * Two-sum patterns using JavaScript Maps, event-style input processing,
 * pair counting, and differential checks.
 *
 * Run with: node two_sum_patterns.js
 */

function requireIntegerArray(values, name = "values") {
    if (!Array.isArray(values)) {
        throw new TypeError(`${name} must be an array`);
    }

    // Number.isSafeInteger avoids silent precision errors in complement
    // arithmetic for integers beyond JavaScript's exact integer range.
    for (const value of values) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError(`${name} must contain safe integers`);
        }
    }
}

function requireSafeInteger(value, name) {
    if (!Number.isSafeInteger(value)) {
        throw new TypeError(`${name} must be a safe integer`);
    }
}

function twoSum(values, target) {
    requireIntegerArray(values);
    requireSafeInteger(target, "target");

    const earliestIndex = new Map();

    for (let index = 0; index < values.length; index += 1) {
        const value = values[index];
        const complement = target - value;
        requireSafeInteger(complement, "computed complement");

        if (earliestIndex.has(complement)) {
            return [earliestIndex.get(complement), index];
        }

        if (!earliestIndex.has(value)) {
            earliestIndex.set(value, index);
        }
    }

    return null;
}

function* allTwoSumPairs(values, target) {
    requireIntegerArray(values);
    requireSafeInteger(target, "target");

    const indicesByValue = new Map();

    for (let right = 0; right < values.length; right += 1) {
        const value = values[right];
        const complement = target - value;
        const matchingIndices = indicesByValue.get(complement) ?? [];

        // A generator yields results lazily, so callers can consume pairs
        // without requiring an additional result array.
        for (const left of matchingIndices) {
            yield [left, right];
        }

        if (!indicesByValue.has(value)) {
            indicesByValue.set(value, []);
        }
        indicesByValue.get(value).push(right);
    }
}

function countPairs(values, target) {
    requireIntegerArray(values);
    requireSafeInteger(target, "target");

    const frequencies = new Map();
    let count = 0;

    for (const value of values) {
        const complement = target - value;
        requireSafeInteger(complement, "computed complement");

        count += frequencies.get(complement) ?? 0;
        frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
    }

    return count;
}

function uniqueValuePairs(values, target) {
    requireIntegerArray(values);
    requireSafeInteger(target, "target");

    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
    }

    const pairs = [];

    for (const value of [...frequencies.keys()].sort((a, b) => a - b)) {
        const complement = target - value;

        if (
            complement < value ||
            !frequencies.has(complement) ||
            (complement === value && frequencies.get(value) < 2)
        ) {
            continue;
        }

        pairs.push([value, complement]);
    }

    return pairs;
}

function findSignedDifference(values, difference) {
    requireIntegerArray(values);
    requireSafeInteger(difference, "difference");

    const earliestIndex = new Map();

    for (let right = 0; right < values.length; right += 1) {
        const value = values[right];
        const required = value - difference;
        requireSafeInteger(required, "computed difference complement");

        if (earliestIndex.has(required)) {
            return [earliestIndex.get(required), right];
        }

        if (!earliestIndex.has(value)) {
            earliestIndex.set(value, right);
        }
    }

    return null;
}

function findAbsoluteDifference(values, difference) {
    requireIntegerArray(values);
    requireSafeInteger(difference, "difference");

    if (difference < 0) {
        throw new RangeError("Absolute difference cannot be negative");
    }

    const earliestIndex = new Map();

    for (let right = 0; right < values.length; right += 1) {
        const value = values[right];
        const candidates = difference === 0
            ? [value]
            : [value - difference, value + difference];

        for (const candidate of candidates) {
            requireSafeInteger(candidate, "computed difference complement");

            if (earliestIndex.has(candidate)) {
                return [earliestIndex.get(candidate), right];
            }
        }

        if (!earliestIndex.has(value)) {
            earliestIndex.set(value, right);
        }
    }

    return null;
}

function twoSumSorted(values, target) {
    requireIntegerArray(values);
    requireSafeInteger(target, "target");

    // Validate the precondition rather than silently returning a wrong result.
    for (let index = 1; index < values.length; index += 1) {
        if (values[index - 1] > values[index]) {
            throw new RangeError("twoSumSorted requires ascending input");
        }
    }

    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        const sum = values[left] + values[right];
        requireSafeInteger(sum, "computed sum");

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

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function samePairResult(actual, expected) {
    return JSON.stringify(actual) === JSON.stringify(expected);
}

function bruteForceTwoSum(values, target) {
    for (let left = 0; left < values.length; left += 1) {
        for (let right = left + 1; right < values.length; right += 1) {
            if (values[left] + values[right] === target) {
                return [left, right];
            }
        }
    }

    return null;
}

function runTests() {
    assert(samePairResult(twoSum([2, 7, 11, 15], 9), [0, 1]), "basic sum");
    assert(samePairResult(twoSum([3, 3], 6), [0, 1]), "duplicate values");
    assert(twoSum([1], 2) === null, "no self-pair");
    assert(countPairs([2, 2, 2, 2], 4) === 6, "duplicate pair count");
    assert(countPairs([1, 5, 1, 5], 6) === 4, "cross-value pair count");
    assert(
        [...allTwoSumPairs([1, 5, 1, 5], 6)].length === 4,
        "generator returns all index pairs"
    );
    assert(
        samePairResult(uniqueValuePairs([1, 1, 2, 2, 3], 4), [[1, 3], [2, 2]]),
        "unique value pairs"
    );
    assert(
        samePairResult(findSignedDifference([4, 1, 8, 3], 2), [3, 2]),
        "signed difference"
    );
    assert(
        samePairResult(findAbsoluteDifference([1, 8, 3, 10], 2), [0, 2]),
        "absolute difference"
    );
    assert(
        samePairResult(findAbsoluteDifference([5, 5], 0), [0, 1]),
        "zero difference requires duplicates"
    );
    assert(
        samePairResult(twoSumSorted([-5, -1, 2, 7], 1), [0, 3]),
        "two-pointer search"
    );

    let rejectedUnsorted = false;
    try {
        twoSumSorted([2, 1], 3);
    } catch (error) {
        rejectedUnsorted = error instanceof RangeError;
    }
    assert(rejectedUnsorted, "sorted-input precondition");

    let rejectedNegativeDifference = false;
    try {
        findAbsoluteDifference([1, 2], -1);
    } catch (error) {
        rejectedNegativeDifference = error instanceof RangeError;
    }
    assert(rejectedNegativeDifference, "negative absolute difference");

    const testCases = [
        [],
        [0],
        [1, 1],
        [-2, 0, 2],
        [3, -1, 3, 0, -1]
    ];

    for (const values of testCases) {
        for (let target = -5; target <= 5; target += 1) {
            const optimized = twoSum(values, target);
            const reference = bruteForceTwoSum(values, target);

            assert(
                (optimized === null) === (reference === null),
                `differential test: ${JSON.stringify(values)}, target ${target}`
            );

            if (optimized !== null) {
                const [left, right] = optimized;
                assert(left !== right, "indices must differ");
                assert(values[left] + values[right] === target, "sum must match");
            }
        }
    }

    console.log("All JavaScript Two-sum pattern tests passed.");
}

function main() {
    const purchasePrices = [125, 275, 80, 200, 125];
    console.log("Purchase pair for budget 400:", twoSum(purchasePrices, 400));
    console.log("All pairs for budget 400:", [...allTwoSumPairs(purchasePrices, 400)]);
    console.log("Number of pairs for budget 400:", countPairs(purchasePrices, 400));
    console.log("Unique price pairs:", uniqueValuePairs(purchasePrices, 400));
    console.log("Signed difference of 75:", findSignedDifference(purchasePrices, 75));
    console.log(
        "Absolute difference of 75:",
        findAbsoluteDifference(purchasePrices, 75)
    );

    runTests();
}

if (require.main === module) {
    main();
}

module.exports = {
    twoSum,
    allTwoSumPairs,
    countPairs,
    uniqueValuePairs,
    findSignedDifference,
    findAbsoluteDifference,
    twoSumSorted
};
