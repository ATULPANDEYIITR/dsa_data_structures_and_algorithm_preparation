/*
 * Day 16 — Sliding Window
 *
 * Comprehensive JavaScript implementation of the sliding-window technique.
 *
 * Topics:
 *   - Fixed-size windows
 *   - Variable-size windows
 *   - Window expansion and contraction
 *   - Frequency maps
 *   - Distinct-element windows
 *   - Anagram windows
 *   - Monotonic deques
 *   - Edge cases
 *   - Validation
 *   - Complexity
 *   - Practical case study
 *
 * Runtime:
 *   Node.js 18+ recommended.
 *
 * No external packages are required.
 */

"use strict";

// -----------------------------------------------------------------------------
// Utility functions
// -----------------------------------------------------------------------------

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function validateArray(values, name = "values") {
    if (!Array.isArray(values)) {
        throw new TypeError(`${name} must be an array.`);
    }

    if (values.length === 0) {
        throw new RangeError(`${name} must not be empty.`);
    }
}

function validatePositiveK(k) {
    if (!Number.isInteger(k)) {
        throw new TypeError("k must be an integer.");
    }

    if (k <= 0) {
        throw new RangeError("k must be greater than zero.");
    }
}

function validateWindowSize(values, k) {
    validateArray(values);
    validatePositiveK(k);

    if (k > values.length) {
        throw new RangeError("k cannot exceed the array length.");
    }
}


// -----------------------------------------------------------------------------
// Frequency-map helpers
// -----------------------------------------------------------------------------

function incrementFrequency(map, key) {
    map.set(key, (map.get(key) ?? 0) + 1);
}

function decrementFrequency(map, key) {
    const nextCount = (map.get(key) ?? 0) - 1;

    if (nextCount <= 0) {
        map.delete(key);
    } else {
        map.set(key, nextCount);
    }
}


// -----------------------------------------------------------------------------
// Fixed-size sliding windows
// -----------------------------------------------------------------------------

function maxSumSubarrayBruteForce(values, k) {
    validateWindowSize(values, k);

    let best = -Infinity;

    for (let left = 0; left <= values.length - k; left++) {
        let currentSum = 0;

        for (let index = left; index < left + k; index++) {
            currentSum += values[index];
        }

        best = Math.max(best, currentSum);
    }

    return best;
}

function maxSumSubarray(values, k) {
    validateWindowSize(values, k);

    // The first window is computed once.
    let windowSum = 0;

    for (let index = 0; index < k; index++) {
        windowSum += values[index];
    }

    let best = windowSum;

    // Every move removes one old element and adds one new element.
    for (let right = k; right < values.length; right++) {
        windowSum += values[right];
        windowSum -= values[right - k];

        best = Math.max(best, windowSum);
    }

    return best;
}

function allWindowSums(values, k) {
    validateWindowSize(values, k);

    const result = [];
    let windowSum = 0;

    for (let index = 0; index < k; index++) {
        windowSum += values[index];
    }

    result.push(windowSum);

    for (let right = k; right < values.length; right++) {
        windowSum += values[right];
        windowSum -= values[right - k];
        result.push(windowSum);
    }

    return result;
}

function minSumSubarray(values, k) {
    validateWindowSize(values, k);

    let windowSum = 0;

    for (let index = 0; index < k; index++) {
        windowSum += values[index];
    }

    let best = windowSum;

    for (let right = k; right < values.length; right++) {
        windowSum += values[right] - values[right - k];
        best = Math.min(best, windowSum);
    }

    return best;
}

function maxAverageSubarray(values, k) {
    return maxSumSubarray(values, k) / k;
}


// -----------------------------------------------------------------------------
// Variable-size windows
// -----------------------------------------------------------------------------

function minimumSizeSubarraySum(values, target) {
    validateArray(values);

    if (target <= 0) {
        throw new RangeError("target must be positive.");
    }

    if (values.some(value => value < 0)) {
        throw new RangeError(
            "This implementation requires non-negative values."
        );
    }

    let left = 0;
    let windowSum = 0;
    let best = Infinity;

    for (let right = 0; right < values.length; right++) {
        windowSum += values[right];

        // Contract as long as the window remains valid.
        while (windowSum >= target) {
            best = Math.min(best, right - left + 1);
            windowSum -= values[left];
            left++;
        }
    }

    return best === Infinity ? 0 : best;
}

function longestSubarraySumAtMost(values, limit) {
    validateArray(values);

    if (values.some(value => value < 0)) {
        throw new RangeError(
            "This implementation requires non-negative values."
        );
    }

    if (limit < 0) {
        return 0;
    }

    let left = 0;
    let windowSum = 0;
    let best = 0;

    for (let right = 0; right < values.length; right++) {
        windowSum += values[right];

        while (windowSum > limit) {
            windowSum -= values[left];
            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}


// -----------------------------------------------------------------------------
// Longest window with at most/exactly k distinct values
// -----------------------------------------------------------------------------

function longestAtMostKDistinct(values, k) {
    validateArray(values);

    if (!Number.isInteger(k) || k <= 0) {
        throw new RangeError("k must be a positive integer.");
    }

    const frequencies = new Map();
    let left = 0;
    let best = 0;

    for (let right = 0; right < values.length; right++) {
        incrementFrequency(frequencies, values[right]);

        while (frequencies.size > k) {
            decrementFrequency(frequencies, values[left]);
            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}

function longestExactlyKDistinct(values, k) {
    validateArray(values);

    if (!Number.isInteger(k) || k <= 0) {
        return 0;
    }

    const frequencies = new Map();
    let left = 0;
    let best = 0;

    for (let right = 0; right < values.length; right++) {
        incrementFrequency(frequencies, values[right]);

        while (frequencies.size > k) {
            decrementFrequency(frequencies, values[left]);
            left++;
        }

        if (frequencies.size === k) {
            best = Math.max(best, right - left + 1);
        }
    }

    return best;
}


// -----------------------------------------------------------------------------
// String windows
// -----------------------------------------------------------------------------

function longestSubstringWithoutRepeating(text) {
    const lastSeen = new Map();

    let left = 0;
    let best = 0;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        if (
            lastSeen.has(character) &&
            lastSeen.get(character) >= left
        ) {
            // Jump directly beyond the previous occurrence.
            left = lastSeen.get(character) + 1;
        }

        lastSeen.set(character, right);
        best = Math.max(best, right - left + 1);
    }

    return best;
}

function longestSubstringAtMostKDistinct(text, k) {
    if (k <= 0) {
        return 0;
    }

    const frequencies = new Map();
    let left = 0;
    let best = 0;

    for (let right = 0; right < text.length; right++) {
        incrementFrequency(frequencies, text[right]);

        while (frequencies.size > k) {
            decrementFrequency(frequencies, text[left]);
            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}


// -----------------------------------------------------------------------------
// Fixed-size frequency window: anagrams
// -----------------------------------------------------------------------------

function sameFrequencyMap(first, second) {
    if (first.size !== second.size) {
        return false;
    }

    for (const [key, count] of first) {
        if (second.get(key) !== count) {
            return false;
        }
    }

    return true;
}

function containsPermutation(pattern, text) {
    if (pattern.length === 0) {
        return true;
    }

    if (pattern.length > text.length) {
        return false;
    }

    const required = new Map();
    const window = new Map();

    for (const character of pattern) {
        incrementFrequency(required, character);
    }

    for (let index = 0; index < pattern.length; index++) {
        incrementFrequency(window, text[index]);
    }

    if (sameFrequencyMap(required, window)) {
        return true;
    }

    const k = pattern.length;

    for (let right = k; right < text.length; right++) {
        incrementFrequency(window, text[right]);
        decrementFrequency(window, text[right - k]);

        if (sameFrequencyMap(required, window)) {
            return true;
        }
    }

    return false;
}

function findAnagramStarts(pattern, text) {
    const result = [];

    if (
        pattern.length === 0 ||
        pattern.length > text.length
    ) {
        return result;
    }

    const required = new Map();
    const window = new Map();

    for (const character of pattern) {
        incrementFrequency(required, character);
    }

    for (let index = 0; index < pattern.length; index++) {
        incrementFrequency(window, text[index]);
    }

    if (sameFrequencyMap(required, window)) {
        result.push(0);
    }

    const k = pattern.length;

    for (let right = k; right < text.length; right++) {
        incrementFrequency(window, text[right]);
        decrementFrequency(window, text[right - k]);

        if (sameFrequencyMap(required, window)) {
            result.push(right - k + 1);
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Distinct elements in every fixed window
// -----------------------------------------------------------------------------

function distinctCountInEveryWindow(values, k) {
    validateWindowSize(values, k);

    const frequencies = new Map();
    const result = [];

    for (let index = 0; index < k; index++) {
        incrementFrequency(frequencies, values[index]);
    }

    result.push(frequencies.size);

    for (let right = k; right < values.length; right++) {
        decrementFrequency(frequencies, values[right - k]);
        incrementFrequency(frequencies, values[right]);

        result.push(frequencies.size);
    }

    return result;
}


// -----------------------------------------------------------------------------
// Binary-array sliding window
// -----------------------------------------------------------------------------

function longestOnesAfterFlippingKZeros(values, k) {
    validateArray(values);

    if (k < 0) {
        throw new RangeError("k cannot be negative.");
    }

    let left = 0;
    let zeroCount = 0;
    let best = 0;

    for (let right = 0; right < values.length; right++) {
        if (values[right] !== 0 && values[right] !== 1) {
            throw new RangeError("The array must contain only 0 and 1.");
        }

        if (values[right] === 0) {
            zeroCount++;
        }

        while (zeroCount > k) {
            if (values[left] === 0) {
                zeroCount--;
            }

            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}


// -----------------------------------------------------------------------------
// Character replacement
// -----------------------------------------------------------------------------

function longestRepeatingCharacterReplacement(text, k) {
    if (k < 0) {
        throw new RangeError("k cannot be negative.");
    }

    const frequencies = new Map();

    let left = 0;
    let highestFrequency = 0;
    let best = 0;

    for (let right = 0; right < text.length; right++) {
        incrementFrequency(frequencies, text[right]);

        highestFrequency = Math.max(
            highestFrequency,
            frequencies.get(text[right])
        );

        // Window length minus the most frequent character count equals the
        // number of replacements needed.
        while (
            right - left + 1 - highestFrequency > k
        ) {
            decrementFrequency(frequencies, text[left]);
            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}


// -----------------------------------------------------------------------------
// Positive-product window
// -----------------------------------------------------------------------------

function minimumSizeSubarrayProduct(values, target) {
    validateArray(values);

    if (target <= 0) {
        throw new RangeError("target must be positive.");
    }

    if (values.some(value => value <= 0)) {
        throw new RangeError(
            "All values must be strictly positive."
        );
    }

    let left = 0;
    let product = 1;
    let best = Infinity;

    for (let right = 0; right < values.length; right++) {
        product *= values[right];

        while (product >= target) {
            best = Math.min(best, right - left + 1);
            product /= values[left];
            left++;
        }
    }

    return best === Infinity ? 0 : best;
}


// -----------------------------------------------------------------------------
// Monotonic deque implementation
// -----------------------------------------------------------------------------

class IndexDeque {
    constructor() {
        this.data = [];
        this.head = 0;
    }

    pushBack(value) {
        this.data.push(value);
    }

    popBack() {
        return this.data.pop();
    }

    popFront() {
        if (!this.isEmpty()) {
            const value = this.data[this.head];
            this.head++;

            // Periodically compact the array so that removed elements do not
            // remain indefinitely in memory.
            if (this.head > 64 && this.head * 2 > this.data.length) {
                this.data = this.data.slice(this.head);
                this.head = 0;
            }

            return value;
        }

        return undefined;
    }

    front() {
        return this.data[this.head];
    }

    back() {
        return this.data[this.data.length - 1];
    }

    isEmpty() {
        return this.head >= this.data.length;
    }

    length() {
        return this.data.length - this.head;
    }
}

function slidingWindowMaximum(values, k) {
    validateWindowSize(values, k);

    const deque = new IndexDeque();
    const result = [];

    for (let right = 0; right < values.length; right++) {
        // Remove expired indices.
        while (
            !deque.isEmpty() &&
            deque.front() <= right - k
        ) {
            deque.popFront();
        }

        // Maintain decreasing values in the deque.
        while (
            !deque.isEmpty() &&
            values[deque.back()] <= values[right]
        ) {
            deque.popBack();
        }

        deque.pushBack(right);

        if (right >= k - 1) {
            result.push(values[deque.front()]);
        }
    }

    return result;
}

function slidingWindowMinimum(values, k) {
    validateWindowSize(values, k);

    const deque = new IndexDeque();
    const result = [];

    for (let right = 0; right < values.length; right++) {
        while (
            !deque.isEmpty() &&
            deque.front() <= right - k
        ) {
            deque.popFront();
        }

        // Maintain increasing values in the deque.
        while (
            !deque.isEmpty() &&
            values[deque.back()] >= values[right]
        ) {
            deque.popBack();
        }

        deque.pushBack(right);

        if (right >= k - 1) {
            result.push(values[deque.front()]);
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Maximum-minimum constrained window
// -----------------------------------------------------------------------------

function longestSubarrayAbsoluteDifference(values, limit) {
    validateArray(values);

    if (limit < 0) {
        return 0;
    }

    const maximums = new IndexDeque();
    const minimums = new IndexDeque();

    let left = 0;
    let best = 0;

    for (let right = 0; right < values.length; right++) {
        while (
            !maximums.isEmpty() &&
            values[maximums.back()] <= values[right]
        ) {
            maximums.popBack();
        }

        maximums.pushBack(right);

        while (
            !minimums.isEmpty() &&
            values[minimums.back()] >= values[right]
        ) {
            minimums.popBack();
        }

        minimums.pushBack(right);

        while (
            values[maximums.front()] -
            values[minimums.front()] >
            limit
        ) {
            if (maximums.front() === left) {
                maximums.popFront();
            }

            if (minimums.front() === left) {
                minimums.popFront();
            }

            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}


// -----------------------------------------------------------------------------
// Generic variable-window framework
// -----------------------------------------------------------------------------

function longestValidWindow(values, state) {
    let left = 0;
    let bestLength = 0;
    let bestLeft = 0;
    let bestRight = -1;

    for (let right = 0; right < values.length; right++) {
        state.add(values[right]);

        while (!state.isValid()) {
            state.remove(values[left]);
            left++;
        }

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestLeft = left;
            bestRight = right;
        }
    }

    return {
        length: bestLength,
        left: bestLeft,
        right: bestRight,
        values: values.slice(bestLeft, bestRight + 1)
    };
}


// -----------------------------------------------------------------------------
// Practical case study: network traffic monitoring
// -----------------------------------------------------------------------------

class TrafficMonitor {
    constructor(windowSize, alertThreshold) {
        if (!Number.isInteger(windowSize) || windowSize <= 0) {
            throw new RangeError(
                "windowSize must be a positive integer."
            );
        }

        if (alertThreshold < 0) {
            throw new RangeError(
                "alertThreshold cannot be negative."
            );
        }

        this.windowSize = windowSize;
        this.alertThreshold = alertThreshold;
    }

    analyze(packetCounts) {
        validateArray(packetCounts);

        if (this.windowSize > packetCounts.length) {
            throw new RangeError(
                "Window size exceeds packet stream length."
            );
        }

        const alerts = [];
        let windowSum = 0;

        for (let index = 0; index < this.windowSize; index++) {
            windowSum += packetCounts[index];
        }

        for (
            let right = this.windowSize - 1;
            right < packetCounts.length;
            right++
        ) {
            if (right >= this.windowSize) {
                windowSum += packetCounts[right];
                windowSum -= packetCounts[right - this.windowSize];
            }

            const left = right - this.windowSize + 1;

            if (windowSum >= this.alertThreshold) {
                alerts.push({
                    start: left,
                    end: right,
                    totalPackets: windowSum,
                    averagePackets: windowSum / this.windowSize
                });
            }
        }

        return alerts;
    }
}


// -----------------------------------------------------------------------------
// Prefix-sum comparison
// -----------------------------------------------------------------------------

function rangeSumWithPrefix(values, left, right) {
    validateArray(values);

    if (
        left < 0 ||
        right >= values.length ||
        left > right
    ) {
        throw new RangeError("Invalid inclusive range.");
    }

    const prefix = new Array(values.length + 1).fill(0);

    for (let index = 0; index < values.length; index++) {
        prefix[index + 1] =
            prefix[index] + values[index];
    }

    return prefix[right + 1] - prefix[left];
}


// -----------------------------------------------------------------------------
// Testing
// -----------------------------------------------------------------------------

function runAssertions() {
    printSection("Correctness assertions");

    console.assert(
        maxSumSubarray([2, 1, 5, 1, 3, 2], 3) === 9
    );

    console.assert(
        maxSumSubarray([-5, -2, -8], 2) === -7
    );

    console.assert(
        minSumSubarray([2, 1, 5, 1, 3, 2], 3) === 6
    );

    console.assert(
        minimumSizeSubarraySum(
            [2, 3, 1, 2, 4, 3],
            7
        ) === 2
    );

    console.assert(
        longestAtMostKDistinct(
            [1, 2, 1, 2, 3],
            2
        ) === 4
    );

    console.assert(
        longestExactlyKDistinct(
            [1, 2, 1, 2, 3],
            2
        ) === 4
    );

    console.assert(
        longestSubstringWithoutRepeating(
            "abcabcbb"
        ) === 3
    );

    console.assert(
        containsPermutation(
            "ab",
            "eidbaooo"
        )
    );

    console.assert(
        !containsPermutation(
            "ab",
            "eidboaoo"
        )
    );

    console.assert(
        JSON.stringify(
            findAnagramStarts(
                "abc",
                "cbaebabacd"
            )
        ) === JSON.stringify([0, 6])
    );

    console.assert(
        JSON.stringify(
            distinctCountInEveryWindow(
                [1, 2, 1, 3, 4, 2, 3],
                4
            )
        ) === JSON.stringify([3, 4, 4, 4])
    );

    console.assert(
        longestOnesAfterFlippingKZeros(
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
            2
        ) === 6
    );

    console.assert(
        longestRepeatingCharacterReplacement(
            "AABABBA",
            1
        ) === 4
    );

    console.assert(
        minimumSizeSubarrayProduct(
            [10, 5, 2, 6],
            100
        ) === 3
    );

    console.assert(
        JSON.stringify(
            slidingWindowMaximum(
                [1, 3, -1, -3, 5, 3, 6, 7],
                3
            )
        ) === JSON.stringify([3, 3, 5, 5, 6, 7])
    );

    console.assert(
        JSON.stringify(
            slidingWindowMinimum(
                [1, 3, -1, -3, 5, 3, 6, 7],
                3
            )
        ) === JSON.stringify([-1, -3, -3, -3, 3, 3])
    );

    console.assert(
        longestSubarrayAbsoluteDifference(
            [8, 2, 4, 7],
            4
        ) === 2
    );

    console.log("All assertions passed.");
}


// -----------------------------------------------------------------------------
// Demonstrations
// -----------------------------------------------------------------------------

function runExamples() {
    printSection("1. Fixed-size windows");

    const values = [2, 1, 5, 1, 3, 2];

    console.log("Array:", values);
    console.log(
        "Brute-force maximum sum:",
        maxSumSubarrayBruteForce(values, 3)
    );
    console.log(
        "Sliding-window maximum sum:",
        maxSumSubarray(values, 3)
    );
    console.log(
        "All window sums:",
        allWindowSums(values, 3)
    );
    console.log(
        "Minimum window sum:",
        minSumSubarray(values, 3)
    );
    console.log(
        "Maximum average:",
        maxAverageSubarray(values, 3)
    );

    printSection("2. Variable-size windows");

    const positiveValues = [2, 3, 1, 2, 4, 3];

    console.log(
        "Minimum size with sum >= 7:",
        minimumSizeSubarraySum(
            positiveValues,
            7
        )
    );

    console.log(
        "Longest sum <= 8:",
        longestSubarraySumAtMost(
            positiveValues,
            8
        )
    );

    printSection("3. Distinct-element windows");

    const distinctValues = [
        1, 2, 1, 2, 3, 2, 2
    ];

    console.log(
        "At most 2 distinct:",
        longestAtMostKDistinct(
            distinctValues,
            2
        )
    );

    console.log(
        "Exactly 2 distinct:",
        longestExactlyKDistinct(
            distinctValues,
            2
        )
    );

    console.log(
        "Distinct count in windows:",
        distinctCountInEveryWindow(
            distinctValues,
            3
        )
    );

    printSection("4. Frequency-based string windows");

    console.log(
        "Longest substring without repetition:",
        longestSubstringWithoutRepeating(
            "abcabcbb"
        )
    );

    console.log(
        "Longest substring with at most 2 distinct:",
        longestSubstringAtMostKDistinct(
            "eceba",
            2
        )
    );

    printSection("5. Anagram windows");

    console.log(
        "Contains permutation:",
        containsPermutation(
            "ab",
            "eidbaooo"
        )
    );

    console.log(
        "Anagram positions:",
        findAnagramStarts(
            "abc",
            "cbaebabacd"
        )
    );

    printSection("6. Binary window");

    console.log(
        "Longest ones after two zero flips:",
        longestOnesAfterFlippingKZeros(
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
            2
        )
    );

    printSection("7. Character replacement");

    console.log(
        "Longest repeated-character result:",
        longestRepeatingCharacterReplacement(
            "AABABBA",
            1
        )
    );

    printSection("8. Monotonic deque");

    const dequeValues = [
        1, 3, -1, -3, 5, 3, 6, 7
    ];

    console.log(
        "Window maximum:",
        slidingWindowMaximum(
            dequeValues,
            3
        )
    );

    console.log(
        "Window minimum:",
        slidingWindowMinimum(
            dequeValues,
            3
        )
    );

    printSection("9. Maximum-minimum constrained window");

    console.log(
        "Longest valid window:",
        longestSubarrayAbsoluteDifference(
            [8, 2, 4, 7],
            4
        )
    );

    printSection("10. Generic window framework");

    const state = {
        frequencies: new Map(),

        add(value) {
            incrementFrequency(this.frequencies, value);
        },

        remove(value) {
            decrementFrequency(this.frequencies, value);
        },

        isValid() {
            return this.frequencies.size <= 2;
        }
    };

    console.log(
        longestValidWindow(
            [1, 2, 1, 3, 4, 2, 3],
            state
        )
    );

    printSection("11. Prefix-sum comparison");

    console.log(
        "Range sum:",
        rangeSumWithPrefix(
            [3, 1, 4, 1, 5, 9],
            1,
            4
        )
    );

    printSection("12. Network traffic case study");

    const monitor = new TrafficMonitor(
        3,
        750
    );

    const alerts = monitor.analyze([
        120,
        130,
        145,
        300,
        280,
        290,
        150,
        140,
        135
    ]);

    console.table(alerts);

    printSection("13. Complexity reference");

    console.table([
        {
            problem: "Fixed-size sum",
            time: "O(n)",
            space: "O(1)"
        },
        {
            problem: "Minimum-size sum",
            time: "O(n)",
            space: "O(1)"
        },
        {
            problem: "At-most-k distinct",
            time: "O(n) average",
            space: "O(k)"
        },
        {
            problem: "No repeated characters",
            time: "O(n) average",
            space: "O(alphabet)"
        },
        {
            problem: "Monotonic deque",
            time: "O(n)",
            space: "O(k)"
        }
    ]);
}


// -----------------------------------------------------------------------------
// Edge-case demonstration
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    printSection("14. Edge cases");

    const cases = [
        {
            name: "Single element",
            values: [7],
            k: 1
        },
        {
            name: "All negative",
            values: [-8, -3, -5, -2],
            k: 2
        },
        {
            name: "Window equals array",
            values: [1, 2, 3],
            k: 3
        },
        {
            name: "Repeated values",
            values: [5, 5, 5, 5],
            k: 2
        },
        {
            name: "Zeros",
            values: [0, 0, 0, 0],
            k: 3
        }
    ];

    for (const testCase of cases) {
        console.log(
            testCase.name,
            "=>",
            maxSumSubarray(
                testCase.values,
                testCase.k
            )
        );
    }

    try {
        maxSumSubarray([], 2);
    } catch (error) {
        console.log(
            "Handled empty input:",
            error.message
        );
    }

    try {
        maxSumSubarray([1, 2, 3], 4);
    } catch (error) {
        console.log(
            "Handled oversized window:",
            error.message
        );
    }
}


// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

function main() {
    runExamples();
    demonstrateEdgeCases();
    runAssertions();

    printSection("Study checkpoints");

    const checkpoints = [
        "A fixed window keeps its length constant.",
        "A variable window expands with the right pointer.",
        "Contraction moves the left pointer when validity is violated.",
        "Frequency maps maintain counts incrementally.",
        "A key should be deleted when its frequency reaches zero.",
        "Each pointer normally moves only forward.",
        "Monotonic deques maintain candidates for window extrema.",
        "Many sum-based variable windows require non-negative values.",
        "Window validity should be expressed as an invariant.",
        "Sliding windows are about incremental state maintenance."
    ];

    checkpoints.forEach(
        (checkpoint, index) => {
            console.log(
                `${String(index + 1).padStart(2, "0")}. ${checkpoint}`
            );
        }
    );

    console.log(
        "\nSliding-window study program completed successfully."
    );
}

main();
