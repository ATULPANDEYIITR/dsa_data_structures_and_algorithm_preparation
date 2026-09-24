/*
 * Day 18 — Subarrays and Array Patterns
 *
 * Topics:
 * - Subarray enumeration
 * - Prefix sums
 * - Hashing with arrays
 * - Two pointers
 * - Sliding windows
 * - Sorting-based solutions
 * - Maximum/minimum subarray problems
 * - Edge cases
 * - Complexity and algorithm selection
 *
 * Self-contained Node.js program.
 */

"use strict";

// ============================================================
// 1. SUBARRAY FUNDAMENTALS
// ============================================================

function countSubarrays(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("Array length must be a non-negative integer.");
    }

    return (n * (n + 1)) / 2;
}

function enumerateSubarrays(values) {
    const result = [];

    for (let start = 0; start < values.length; start++) {
        for (let end = start; end < values.length; end++) {
            result.push({
                start,
                end,
                values: values.slice(start, end + 1),
            });
        }
    }

    return result;
}

function enumerateSubarrayRanges(values) {
    const ranges = [];

    for (let start = 0; start < values.length; start++) {
        for (let end = start; end < values.length; end++) {
            ranges.push([start, end]);
        }
    }

    return ranges;
}

// ============================================================
// 2. SUBARRAY SUM ENUMERATION
// ============================================================

function allSubarraySumsIncremental(values) {
    const result = [];

    // Incremental accumulation turns repeated O(n) summation
    // into O(n^2) total work.
    for (let start = 0; start < values.length; start++) {
        let currentSum = 0;

        for (let end = start; end < values.length; end++) {
            currentSum += values[end];
            result.push({
                start,
                end,
                sum: currentSum,
            });
        }
    }

    return result;
}

// ============================================================
// 3. PREFIX SUMS
// ============================================================

function buildPrefixSum(values) {
    const prefix = new Array(values.length + 1).fill(0);

    for (let i = 0; i < values.length; i++) {
        prefix[i + 1] = prefix[i] + values[i];
    }

    return prefix;
}

function rangeSum(prefix, left, right) {
    if (
        left < 0 ||
        right < left ||
        right + 1 >= prefix.length
    ) {
        throw new RangeError("Invalid inclusive range.");
    }

    return prefix[right + 1] - prefix[left];
}

function prefixSumDemo() {
    const values = [3, -2, 5, 7, -4, 6];
    const prefix = buildPrefixSum(values);

    console.log("\n=== PREFIX SUMS ===");
    console.log("Values:", values);
    console.log("Prefix:", prefix);
    console.log("Range [1, 4]:", rangeSum(prefix, 1, 4));
}

// ============================================================
// 4. HASHING WITH PREFIX SUMS
// ============================================================

function subarraySumEqualsK(values, target) {
    /*
     * Map prefix sum -> number of occurrences.
     *
     * If currentPrefix - oldPrefix === target,
     * then the elements between those two prefix positions
     * form a subarray whose sum equals target.
     *
     * Average time: O(n)
     * Space: O(n)
     */
    const frequency = new Map([[0, 1]]);

    let prefix = 0;
    let count = 0;

    for (const value of values) {
        prefix += value;

        count += frequency.get(prefix - target) ?? 0;
        frequency.set(prefix, (frequency.get(prefix) ?? 0) + 1);
    }

    return count;
}

function longestSubarraySumK(values, target) {
    /*
     * Store the earliest index of each prefix sum.
     * Earliest occurrence produces the longest range.
     */
    const earliest = new Map([[0, -1]]);

    let prefix = 0;
    let bestLength = 0;

    for (let i = 0; i < values.length; i++) {
        prefix += values[i];

        const required = prefix - target;

        if (earliest.has(required)) {
            bestLength = Math.max(
                bestLength,
                i - earliest.get(required)
            );
        }

        if (!earliest.has(prefix)) {
            earliest.set(prefix, i);
        }
    }

    return bestLength;
}

function countDivisibleSubarrays(values, k) {
    if (!Number.isInteger(k) || k <= 0) {
        throw new RangeError("k must be a positive integer.");
    }

    const frequency = new Map([[0, 1]]);

    let prefix = 0;
    let count = 0;

    for (const value of values) {
        prefix += value;

        // JavaScript's % can be negative, so normalize the remainder.
        const remainder = ((prefix % k) + k) % k;

        count += frequency.get(remainder) ?? 0;
        frequency.set(remainder, (frequency.get(remainder) ?? 0) + 1);
    }

    return count;
}

function longestZeroSumSubarray(values) {
    const earliest = new Map([[0, -1]]);

    let prefix = 0;
    let best = {
        start: -1,
        end: -1,
        length: 0,
    };

    for (let i = 0; i < values.length; i++) {
        prefix += values[i];

        if (earliest.has(prefix)) {
            const start = earliest.get(prefix) + 1;
            const length = i - earliest.get(prefix);

            if (length > best.length) {
                best = {
                    start,
                    end: i,
                    length,
                };
            }
        } else {
            earliest.set(prefix, i);
        }
    }

    return best.length === 0 ? null : best;
}

// ============================================================
// 5. TWO SUM USING HASHING
// ============================================================

function twoSumHashing(values, target) {
    const seen = new Map();

    for (let i = 0; i < values.length; i++) {
        const needed = target - values[i];

        if (seen.has(needed)) {
            return [seen.get(needed), i];
        }

        seen.set(values[i], i);
    }

    return null;
}

// ============================================================
// 6. TWO POINTERS
// ============================================================

function twoPointerPairSumSorted(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        const sum = values[left] + values[right];

        if (sum === target) {
            return [values[left], values[right]];
        }

        if (sum < target) {
            left++;
        } else {
            right--;
        }
    }

    return null;
}

function twoPointerPairSumUnsorted(values, target) {
    // Sorting makes the two-pointer invariant possible.
    const ordered = [...values].sort((a, b) => a - b);

    return twoPointerPairSumSorted(ordered, target);
}

function removeDuplicatesSorted(values) {
    if (values.length === 0) {
        return [];
    }

    const result = [values[0]];

    for (let read = 1; read < values.length; read++) {
        if (values[read] !== result[result.length - 1]) {
            result.push(values[read]);
        }
    }

    return result;
}

function containerWithMostWater(heights) {
    if (heights.some((height) => height < 0)) {
        throw new RangeError("Heights cannot be negative.");
    }

    let left = 0;
    let right = heights.length - 1;
    let best = 0;

    while (left < right) {
        const width = right - left;
        const height = Math.min(heights[left], heights[right]);
        best = Math.max(best, width * height);

        if (heights[left] <= heights[right]) {
            left++;
        } else {
            right--;
        }
    }

    return best;
}

// ============================================================
// 7. SLIDING WINDOWS
// ============================================================

function maximumSumFixedWindow(values, windowSize) {
    if (!Number.isInteger(windowSize) || windowSize <= 0) {
        throw new RangeError("Window size must be positive.");
    }

    if (windowSize > values.length) {
        throw new RangeError("Window size exceeds array length.");
    }

    let currentSum = 0;

    for (let i = 0; i < windowSize; i++) {
        currentSum += values[i];
    }

    let best = currentSum;

    for (let right = windowSize; right < values.length; right++) {
        currentSum += values[right];
        currentSum -= values[right - windowSize];

        best = Math.max(best, currentSum);
    }

    return best;
}

function minimumSizeSubarraySumPositive(values, target) {
    if (target <= 0) {
        throw new RangeError("Target must be positive.");
    }

    if (values.some((value) => value <= 0)) {
        throw new RangeError(
            "This sliding-window algorithm requires positive values."
        );
    }

    let left = 0;
    let currentSum = 0;
    let best = Infinity;

    for (let right = 0; right < values.length; right++) {
        currentSum += values[right];

        while (currentSum >= target) {
            best = Math.min(best, right - left + 1);
            currentSum -= values[left];
            left++;
        }
    }

    return best === Infinity ? 0 : best;
}

function longestAtMostKDistinct(values, k) {
    if (k < 0) {
        throw new RangeError("k cannot be negative.");
    }

    if (k === 0) {
        return 0;
    }

    const counts = new Map();

    let left = 0;
    let best = 0;

    for (let right = 0; right < values.length; right++) {
        const value = values[right];
        counts.set(value, (counts.get(value) ?? 0) + 1);

        while (counts.size > k) {
            const outgoing = values[left];
            const newCount = counts.get(outgoing) - 1;

            if (newCount === 0) {
                counts.delete(outgoing);
            } else {
                counts.set(outgoing, newCount);
            }

            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}

// ============================================================
// 8. KADANE'S ALGORITHM
// ============================================================

function maximumSubarrayKadane(values) {
    if (values.length === 0) {
        return null;
    }

    let currentSum = values[0];
    let bestSum = values[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let i = 1; i < values.length; i++) {
        const value = values[i];

        if (currentSum + value < value) {
            currentSum = value;
            currentStart = i;
        } else {
            currentSum += value;
        }

        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = i;
        }
    }

    return {
        start: bestStart,
        end: bestEnd,
        sum: bestSum,
        values: values.slice(bestStart, bestEnd + 1),
    };
}

function minimumSubarrayKadane(values) {
    if (values.length === 0) {
        return null;
    }

    let currentSum = values[0];
    let bestSum = values[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let i = 1; i < values.length; i++) {
        const value = values[i];

        if (currentSum + value > value) {
            currentSum = value;
            currentStart = i;
        } else {
            currentSum += value;
        }

        if (currentSum < bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = i;
        }
    }

    return {
        start: bestStart,
        end: bestEnd,
        sum: bestSum,
        values: values.slice(bestStart, bestEnd + 1),
    };
}

function maximumCircularSubarray(values) {
    if (values.length === 0) {
        return null;
    }

    const normal = maximumSubarrayKadane(values);
    const minimum = minimumSubarrayKadane(values);

    if (normal.sum < 0) {
        return normal.sum;
    }

    const total = values.reduce((sum, value) => sum + value, 0);
    const wrapped = total - minimum.sum;

    return Math.max(normal.sum, wrapped);
}

// ============================================================
// 9. SORTING-BASED PATTERNS
// ============================================================

function pairExistsBySorting(values, target) {
    const ordered = [...values].sort((a, b) => a - b);

    let left = 0;
    let right = ordered.length - 1;

    while (left < right) {
        const sum = ordered[left] + ordered[right];

        if (sum === target) {
            return true;
        }

        if (sum < target) {
            left++;
        } else {
            right--;
        }
    }

    return false;
}

function mergeIntervals(intervals) {
    if (intervals.length === 0) {
        return [];
    }

    const ordered = intervals
        .map(([start, end]) => {
            if (start > end) {
                throw new RangeError("Interval start exceeds end.");
            }

            return [start, end];
        })
        .sort((a, b) => a[0] - b[0]);

    const merged = [ordered[0]];

    for (let i = 1; i < ordered.length; i++) {
        const [start, end] = ordered[i];
        const previous = merged[merged.length - 1];

        if (start <= previous[1]) {
            previous[1] = Math.max(previous[1], end);
        } else {
            merged.push([start, end]);
        }
    }

    return merged;
}

// ============================================================
// 10. EDGE CASES AND VALIDATION
// ============================================================

function runEdgeCases() {
    console.log("\n=== EDGE CASES ===");

    const cases = [
        [],
        [7],
        [-5, -2, -9],
        [0, 0, 0],
        [1, 2, 3],
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],
    ];

    for (const values of cases) {
        console.log(
            JSON.stringify(values),
            "=>",
            maximumSubarrayKadane(values)
        );
    }

    try {
        minimumSizeSubarraySumPositive([2, -1, 3], 3);
    } catch (error) {
        console.log("Rejected invalid sliding-window input:", error.message);
    }
}

// ============================================================
// 11. SIMPLE TESTING
// ============================================================

function assertEqual(actual, expected, description) {
    const actualText = JSON.stringify(actual);
    const expectedText = JSON.stringify(expected);

    if (actualText !== expectedText) {
        throw new Error(
            `${description}\nExpected: ${expectedText}\nActual: ${actualText}`
        );
    }
}

function runTests() {
    assertEqual(
        countSubarrays(4),
        10,
        "Subarray count"
    );

    assertEqual(
        subarraySumEqualsK([1, 2, 3, -2, 2, 1], 3),
        4,
        "Subarray sum equals k"
    );

    assertEqual(
        twoSumHashing([2, 7, 11, 15], 9),
        [0, 1],
        "Two-sum hashing"
    );

    assertEqual(
        twoPointerPairSumSorted([1, 2, 3, 4, 6, 8], 10),
        [2, 8],
        "Two-pointer pair sum"
    );

    assertEqual(
        maximumSumFixedWindow([2, 1, 5, 1, 3, 2], 3),
        9,
        "Fixed sliding window"
    );

    assertEqual(
        minimumSizeSubarraySumPositive([2, 3, 1, 2, 4, 3], 7),
        2,
        "Minimum positive window"
    );

    assertEqual(
        maximumSubarrayKadane(
            [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        ).sum,
        6,
        "Kadane maximum"
    );

    assertEqual(
        minimumSubarrayKadane(
            [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        ).sum,
        -5,
        "Kadane minimum"
    );

    assertEqual(
        countDivisibleSubarrays([4, 5, 0, -2, -3, 1], 5),
        7,
        "Divisible subarray count"
    );

    console.log("\nAll JavaScript tests passed.");
}

// ============================================================
// 12. MAIN PROGRAM
// ============================================================

function main() {
    console.log("=".repeat(72));
    console.log("DAY 18 — SUBARRAYS AND ARRAY PATTERNS");
    console.log("=".repeat(72));

    const values = [2, -1, 3];

    console.log("\n=== SUBARRAY ENUMERATION ===");
    console.log("Array:", values);
    console.log("Number of subarrays:", countSubarrays(values.length));
    console.log("Subarrays:", enumerateSubarrays(values));
    console.log("Ranges:", enumerateSubarrayRanges(values));

    console.log("\n=== INCREMENTAL SUBARRAY SUMS ===");
    console.log(allSubarraySumsIncremental(values));

    prefixSumDemo();

    console.log("\n=== PREFIX SUM + HASHING ===");
    console.log(
        "Count sum=3:",
        subarraySumEqualsK([1, 2, 3, -2, 2, 1], 3)
    );
    console.log(
        "Longest sum=15:",
        longestSubarraySumK([10, 5, 2, 7, 1, 9], 15)
    );
    console.log(
        "Longest zero-sum:",
        longestZeroSumSubarray([15, -2, 2, -8, 1, 7, 10, 23])
    );

    console.log("\n=== HASHING ===");
    console.log("Two-sum indices:", twoSumHashing([2, 7, 11, 15], 9));

    console.log("\n=== TWO POINTERS ===");
    console.log(
        "Sorted pair:",
        twoPointerPairSumSorted([1, 2, 3, 4, 6, 8], 10)
    );
    console.log(
        "Unsorted pair:",
        twoPointerPairSumUnsorted([8, 1, 6, 10, 4], 14)
    );
    console.log(
        "Unique sorted values:",
        removeDuplicatesSorted([1, 1, 2, 2, 3, 3, 4])
    );
    console.log(
        "Maximum container area:",
        containerWithMostWater([1, 8, 6, 2, 5, 4, 8, 3, 7])
    );

    console.log("\n=== SLIDING WINDOWS ===");
    console.log(
        "Fixed-window maximum:",
        maximumSumFixedWindow([2, 1, 5, 1, 3, 2], 3)
    );
    console.log(
        "Minimum positive window:",
        minimumSizeSubarraySumPositive([2, 3, 1, 2, 4, 3], 7)
    );
    console.log(
        "Longest at most 2 distinct:",
        longestAtMostKDistinct([1, 2, 1, 2, 3], 2)
    );

    console.log("\n=== MAXIMUM / MINIMUM SUBARRAY ===");

    const sample = [-2, 1, -3, 4, -1, 2, 1, -5, 4];

    console.log(
        "Maximum:",
        maximumSubarrayKadane(sample)
    );

    console.log(
        "Minimum:",
        minimumSubarrayKadane(sample)
    );

    console.log(
        "Circular maximum:",
        maximumCircularSubarray(sample)
    );

    console.log("\n=== SORTING ===");
    console.log(
        "Pair exists:",
        pairExistsBySorting([7, 1, 5, 3, 6, 4], 10)
    );

    console.log(
        "Merged intervals:",
        mergeIntervals([[1, 3], [2, 6], [8, 10], [9, 12]])
    );

    console.log("\n=== ADVANCED PREFIX PATTERN ===");
    console.log(
        "Subarrays divisible by 5:",
        countDivisibleSubarrays([4, 5, 0, -2, -3, 1], 5)
    );

    runEdgeCases();
    runTests();

    console.log("\n" + "=".repeat(72));
    console.log("END OF DAY 18 PRACTICE");
    console.log("=".repeat(72));
}

main();
