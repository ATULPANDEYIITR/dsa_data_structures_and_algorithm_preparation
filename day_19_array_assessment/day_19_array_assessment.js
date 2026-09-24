/*
 * Day 19 — Array Assessment
 * ==========================
 *
 * 3 Easy:
 *   1. Find Pivot Index
 *   2. Move Zeroes
 *   3. Maximum Subarray
 *
 * 4 Medium:
 *   4. Maximum Sum Subarray of Size K
 *   5. Two Sum II — Input Array Is Sorted
 *   6. Subarray Sum Equals K
 *   7. Product of Array Except Self
 *
 * 1 Difficult:
 *   8. Trapping Rain Water
 *
 * Every problem is documented with:
 *   Pattern
 *   Approach
 *   Time Complexity
 *   Space Complexity
 *   Mistake
 *   Improvement
 *
 * Runtime:
 *   Node.js 18+ or another modern JavaScript runtime.
 *
 * No external packages are required.
 */

"use strict";

// ============================================================================
// Utility functions
// ============================================================================

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function printSubsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

function validateIntegerArray(values, name = "array") {
    if (!Array.isArray(values)) {
        throw new TypeError(`${name} must be an array.`);
    }

    for (const value of values) {
        if (!Number.isInteger(value)) {
            throw new TypeError(`${name} must contain only integers.`);
        }
    }
}

function formatArray(values) {
    return `[${values.join(", ")}]`;
}

function assertEqual(actual, expected, description) {
    const actualText = JSON.stringify(actual);
    const expectedText = JSON.stringify(expected);

    if (actualText !== expectedText) {
        throw new Error(
            `FAILED: ${description}\nExpected: ${expectedText}\nActual:   ${actualText}`
        );
    }
}


// ============================================================================
// EASY 1 — Find Pivot Index
// ============================================================================

function findPivotIndex(numbers) {
    validateIntegerArray(numbers);

    const totalSum = numbers.reduce((sum, value) => sum + value, 0);
    let leftSum = 0;

    for (let index = 0; index < numbers.length; index += 1) {
        const rightSum = totalSum - leftSum - numbers[index];

        if (leftSum === rightSum) {
            return index;
        }

        leftSum += numbers[index];
    }

    return -1;
}


// ============================================================================
// EASY 2 — Move Zeroes
// ============================================================================

function moveZeroes(numbers) {
    validateIntegerArray(numbers);

    let writeIndex = 0;

    for (let readIndex = 0; readIndex < numbers.length; readIndex += 1) {
        if (numbers[readIndex] !== 0) {
            [numbers[writeIndex], numbers[readIndex]] = [
                numbers[readIndex],
                numbers[writeIndex],
            ];

            writeIndex += 1;
        }
    }

    return numbers;
}


// ============================================================================
// EASY 3 — Maximum Subarray
// ============================================================================

function maximumSubarray(numbers) {
    validateIntegerArray(numbers);

    if (numbers.length === 0) {
        throw new RangeError("maximumSubarray requires a non-empty array.");
    }

    let currentSum = numbers[0];
    let bestSum = numbers[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let index = 1; index < numbers.length; index += 1) {
        const value = numbers[index];

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
        subarray: numbers.slice(bestStart, bestEnd + 1),
    };
}


// ============================================================================
// MEDIUM 1 — Maximum Sum Subarray of Size K
// ============================================================================

function maximumSumSubarrayOfSizeK(numbers, k) {
    validateIntegerArray(numbers);

    if (!Number.isInteger(k) || k <= 0 || k > numbers.length) {
        throw new RangeError("k must satisfy 1 <= k <= array length.");
    }

    let windowSum = 0;

    for (let index = 0; index < k; index += 1) {
        windowSum += numbers[index];
    }

    let maximumSum = windowSum;

    for (let right = k; right < numbers.length; right += 1) {
        const left = right - k;

        windowSum += numbers[right];
        windowSum -= numbers[left];

        maximumSum = Math.max(maximumSum, windowSum);
    }

    return maximumSum;
}


// ============================================================================
// MEDIUM 2 — Two Sum II
// ============================================================================

function twoSumSorted(numbers, target) {
    validateIntegerArray(numbers);

    let left = 0;
    let right = numbers.length - 1;

    while (left < right) {
        const currentSum = numbers[left] + numbers[right];

        if (currentSum === target) {
            return [left + 1, right + 1];
        }

        if (currentSum < target) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    return [-1, -1];
}


// ============================================================================
// MEDIUM 3 — Subarray Sum Equals K
// ============================================================================

function subarraySumEqualsK(numbers, target) {
    validateIntegerArray(numbers);

    /*
     * Map stores how many times each prefix sum has appeared.
     *
     * If:
     *   currentPrefix - previousPrefix = target
     *
     * then:
     *   previousPrefix = currentPrefix - target
     *
     * The frequency matters because the same prefix sum may occur multiple
     * times, producing multiple valid subarrays.
     */
    const prefixFrequency = new Map([[0, 1]]);

    let prefixSum = 0;
    let count = 0;

    for (const value of numbers) {
        prefixSum += value;

        const requiredPrefix = prefixSum - target;
        count += prefixFrequency.get(requiredPrefix) ?? 0;

        prefixFrequency.set(
            prefixSum,
            (prefixFrequency.get(prefixSum) ?? 0) + 1
        );
    }

    return count;
}


// ============================================================================
// MEDIUM 4 — Product of Array Except Self
// ============================================================================

function productExceptSelf(numbers) {
    validateIntegerArray(numbers);

    const result = new Array(numbers.length).fill(1);

    let prefixProduct = 1;

    for (let index = 0; index < numbers.length; index += 1) {
        result[index] = prefixProduct;
        prefixProduct *= numbers[index];
    }

    let suffixProduct = 1;

    for (let index = numbers.length - 1; index >= 0; index -= 1) {
        result[index] *= suffixProduct;
        suffixProduct *= numbers[index];
    }

    return result;
}


// ============================================================================
// HARD — Trapping Rain Water
// ============================================================================

function trapRainWater(heights) {
    validateIntegerArray(heights);

    if (heights.length < 3) {
        return 0;
    }

    let left = 0;
    let right = heights.length - 1;

    let leftMax = 0;
    let rightMax = 0;

    let trappedWater = 0;

    while (left < right) {
        /*
         * The lower boundary determines how much water is guaranteed on
         * that side. Processing the lower side preserves the correctness
         * invariant.
         */
        if (heights[left] <= heights[right]) {
            if (heights[left] >= leftMax) {
                leftMax = heights[left];
            } else {
                trappedWater += leftMax - heights[left];
            }

            left += 1;
        } else {
            if (heights[right] >= rightMax) {
                rightMax = heights[right];
            } else {
                trappedWater += rightMax - heights[right];
            }

            right -= 1;
        }
    }

    return trappedWater;
}


// ============================================================================
// Brute-force/reference implementations
// ============================================================================

function maximumSumSubarrayOfSizeKBruteForce(numbers, k) {
    validateIntegerArray(numbers);

    if (!Number.isInteger(k) || k <= 0 || k > numbers.length) {
        throw new RangeError("k must satisfy 1 <= k <= array length.");
    }

    let maximumSum = -Infinity;

    for (let start = 0; start <= numbers.length - k; start += 1) {
        let currentSum = 0;

        for (let index = start; index < start + k; index += 1) {
            currentSum += numbers[index];
        }

        maximumSum = Math.max(maximumSum, currentSum);
    }

    return maximumSum;
}

function subarraySumEqualsKBruteForce(numbers, target) {
    validateIntegerArray(numbers);

    let count = 0;

    for (let start = 0; start < numbers.length; start += 1) {
        let currentSum = 0;

        for (let end = start; end < numbers.length; end += 1) {
            currentSum += numbers[end];

            if (currentSum === target) {
                count += 1;
            }
        }
    }

    return count;
}

function trapRainWaterWithArrays(heights) {
    validateIntegerArray(heights);

    const n = heights.length;

    if (n < 3) {
        return 0;
    }

    const leftMax = new Array(n).fill(0);
    const rightMax = new Array(n).fill(0);

    leftMax[0] = heights[0];

    for (let index = 1; index < n; index += 1) {
        leftMax[index] = Math.max(
            leftMax[index - 1],
            heights[index]
        );
    }

    rightMax[n - 1] = heights[n - 1];

    for (let index = n - 2; index >= 0; index -= 1) {
        rightMax[index] = Math.max(
            rightMax[index + 1],
            heights[index]
        );
    }

    let water = 0;

    for (let index = 0; index < n; index += 1) {
        water += Math.min(leftMax[index], rightMax[index]) - heights[index];
    }

    return water;
}


// ============================================================================
// Assessment records
// ============================================================================

const assessment = [
    {
        name: "Find Pivot Index",
        difficulty: "Easy",
        pattern: "Prefix-sum reasoning",
        approach:
            "Compute the total sum once and maintain the left sum while deriving the right sum.",
        time: "O(n)",
        space: "O(1) auxiliary",
        mistake:
            "Recalculating both sides at every index creates O(n²) work.",
        improvement:
            "Use one total sum and one running left sum.",
    },
    {
        name: "Move Zeroes",
        difficulty: "Easy",
        pattern: "Two pointers / stable compaction",
        approach:
            "Read every element and use a write pointer to place non-zero values in order.",
        time: "O(n)",
        space: "O(1) auxiliary",
        mistake:
            "Removing elements during traversal can skip values and shift indices.",
        improvement:
            "Modify the array in place with a write pointer.",
    },
    {
        name: "Maximum Subarray",
        difficulty: "Easy",
        pattern: "Kadane's algorithm",
        approach:
            "Track the best subarray sum ending at the current position.",
        time: "O(n)",
        space: "O(1)",
        mistake:
            "Starting the answer at zero fails when every element is negative.",
        improvement:
            "Initialize the state from the first element.",
    },
    {
        name: "Maximum Sum Subarray of Size K",
        difficulty: "Medium",
        pattern: "Fixed-size sliding window",
        approach:
            "Reuse the previous window sum by removing the outgoing value and adding the incoming value.",
        time: "O(n)",
        space: "O(1)",
        mistake:
            "Recomputing every window produces O(n*k) complexity.",
        improvement:
            "Maintain one rolling window sum.",
    },
    {
        name: "Two Sum II",
        difficulty: "Medium",
        pattern: "Opposite-direction two pointers",
        approach:
            "Use sorted order to move the left pointer upward or the right pointer downward.",
        time: "O(n)",
        space: "O(1)",
        mistake:
            "Ignoring the sorted constraint and using unnecessary extra memory.",
        improvement:
            "Exploit the monotonic effect of pointer movement.",
    },
    {
        name: "Subarray Sum Equals K",
        difficulty: "Medium",
        pattern: "Prefix sum + frequency map",
        approach:
            "Count previous prefix sums equal to currentPrefix - target.",
        time: "O(n) expected",
        space: "O(n)",
        mistake:
            "Using a normal sliding window when negative numbers are allowed.",
        improvement:
            "Use prefix sums because they do not require monotonic values.",
    },
    {
        name: "Product of Array Except Self",
        difficulty: "Medium",
        pattern: "Prefix and suffix products",
        approach:
            "Build prefix products in the result and multiply suffix products during a reverse scan.",
        time: "O(n)",
        space: "O(1) auxiliary, excluding output",
        mistake:
            "Using division without correctly handling zero values.",
        improvement:
            "Avoid division and reuse the output array.",
    },
    {
        name: "Trapping Rain Water",
        difficulty: "Hard",
        pattern: "Two pointers + running boundary maxima",
        approach:
            "Process the side with the lower boundary while maintaining left and right maximum heights.",
        time: "O(n)",
        space: "O(1)",
        mistake:
            "Scanning both directions independently for every position creates O(n²) work.",
        improvement:
            "Maintain boundary maxima and process each position once.",
    },
];


// ============================================================================
// Demonstrations
// ============================================================================

function demonstrateEasyProblems() {
    printSection("EASY PROBLEMS");

    printSubsection("Easy 1 — Find Pivot Index");

    const pivotInput = [1, 7, 3, 6, 5, 6];

    console.log("Input:", formatArray(pivotInput));
    console.log("Output:", findPivotIndex(pivotInput));

    printSubsection("Easy 2 — Move Zeroes");

    const zeroInput = [0, 1, 0, 3, 12];

    console.log("Before:", formatArray(zeroInput));
    moveZeroes(zeroInput);
    console.log("After: ", formatArray(zeroInput));

    printSubsection("Easy 3 — Maximum Subarray");

    const maximumInput = [-2, 1, -3, 4, -1, 2, 1, -5, 4];
    const maximumResult = maximumSubarray(maximumInput);

    console.log("Input:", formatArray(maximumInput));
    console.log("Result:", maximumResult);
}

function demonstrateMediumProblems() {
    printSection("MEDIUM PROBLEMS");

    printSubsection("Medium 1 — Maximum Sum Subarray of Size K");

    const windowInput = [2, 1, 5, 1, 3, 2];
    const k = 3;

    console.log("Input:", formatArray(windowInput));
    console.log("k:", k);
    console.log(
        "Optimized:",
        maximumSumSubarrayOfSizeK(windowInput, k)
    );
    console.log(
        "Brute force:",
        maximumSumSubarrayOfSizeKBruteForce(windowInput, k)
    );

    printSubsection("Medium 2 — Two Sum II");

    const twoSumInput = [2, 7, 11, 15];

    console.log("Input:", formatArray(twoSumInput));
    console.log("Target:", 9);
    console.log("Output:", twoSumSorted(twoSumInput, 9));

    printSubsection("Medium 3 — Subarray Sum Equals K");

    const subarrayInput = [1, 2, 1, 2, 1];

    console.log("Input:", formatArray(subarrayInput));
    console.log("Target:", 3);
    console.log(
        "Optimized:",
        subarraySumEqualsK(subarrayInput, 3)
    );
    console.log(
        "Brute force:",
        subarraySumEqualsKBruteForce(subarrayInput, 3)
    );

    printSubsection("Medium 4 — Product of Array Except Self");

    const productInput = [1, 2, 3, 4];

    console.log("Input:", formatArray(productInput));
    console.log("Output:", formatArray(productExceptSelf(productInput)));
}

function demonstrateHardProblem() {
    printSection("DIFFICULT PROBLEM");

    printSubsection("Hard — Trapping Rain Water");

    const heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1];

    console.log("Input:", formatArray(heights));
    console.log("Two-pointer result:", trapRainWater(heights));
    console.log(
        "Prefix-array result:",
        trapRainWaterWithArrays(heights)
    );
}


// ============================================================================
// Edge cases
// ============================================================================

function demonstrateEdgeCases() {
    printSection("EDGE CASES");

    const cases = [
        ["Empty array", []],
        ["Single element", [7]],
        ["All zeroes", [0, 0, 0]],
        ["All negative", [-5, -2, -9]],
        ["Mixed signs", [-3, 4, -1, 2, -6, 5]],
        ["Sorted", [1, 2, 3, 4, 5]],
        ["Reverse sorted", [5, 4, 3, 2, 1]],
        ["Duplicates", [2, 2, 2, 2]],
    ];

    for (const [name, values] of cases) {
        console.log(`${name.padEnd(20)} ${formatArray(values)}`);
    }

    console.log(
        "\nImportant assessment edge cases include empty input where permitted, " +
        "single-element arrays, duplicates, zeroes, negative values, monotonic " +
        "arrays, and inputs with no valid answer."
    );
}


// ============================================================================
// Documentation output
// ============================================================================

function printAssessmentDocumentation() {
    printSection("ASSESSMENT DOCUMENTATION");

    assessment.forEach((problem, index) => {
        console.log(
            `\n${index + 1}. ${problem.name} [${problem.difficulty}]`
        );
        console.log(`Pattern: ${problem.pattern}`);
        console.log(`Approach: ${problem.approach}`);
        console.log(`Time Complexity: ${problem.time}`);
        console.log(`Space Complexity: ${problem.space}`);
        console.log(`Mistake: ${problem.mistake}`);
        console.log(`Improvement: ${problem.improvement}`);
    });
}


// ============================================================================
// Tests
// ============================================================================

function runTests() {
    printSection("UNIT TESTS");

    assertEqual(
        findPivotIndex([1, 7, 3, 6, 5, 6]),
        3,
        "pivot index"
    );

    assertEqual(
        findPivotIndex([1, 2, 3]),
        -1,
        "missing pivot"
    );

    assertEqual(
        moveZeroes([0, 1, 0, 3, 12]),
        [1, 3, 12, 0, 0],
        "move zeroes"
    );

    assertEqual(
        maximumSubarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]),
        {
            sum: 6,
            start: 3,
            end: 6,
            subarray: [4, -1, 2, 1],
        },
        "maximum subarray"
    );

    assertEqual(
        maximumSubarray([-8, -3, -6, -2]),
        {
            sum: -2,
            start: 3,
            end: 3,
            subarray: [-2],
        },
        "all-negative maximum subarray"
    );

    assertEqual(
        maximumSumSubarrayOfSizeK([2, 1, 5, 1, 3, 2], 3),
        9,
        "fixed-size sliding window"
    );

    assertEqual(
        twoSumSorted([2, 7, 11, 15], 9),
        [1, 2],
        "two sum sorted"
    );

    assertEqual(
        subarraySumEqualsK([1, 1, 1], 2),
        2,
        "subarray sum equals k"
    );

    assertEqual(
        subarraySumEqualsK([1, -1, 0], 0),
        3,
        "negative values in prefix-sum problem"
    );

    assertEqual(
        productExceptSelf([1, 2, 3, 4]),
        [24, 12, 8, 6],
        "product except self"
    );

    assertEqual(
        productExceptSelf([-1, 1, 0, -3, 3]),
        [0, 0, 9, 0, 0],
        "product except self with zero"
    );

    assertEqual(
        trapRainWater([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]),
        6,
        "trapping rain water"
    );

    assertEqual(
        trapRainWater([4, 2, 0, 3, 2, 5]),
        9,
        "second trapping example"
    );

    console.log("All JavaScript unit tests passed.");
}


// ============================================================================
// Performance measurement
// ============================================================================

function benchmark(functionToMeasure, ...argumentsList) {
    const start = performance.now();
    functionToMeasure(...argumentsList);
    return performance.now() - start;
}

function demonstratePerformance() {
    printSection("PERFORMANCE COMPARISON");

    const data = Array.from({ length: 2000 }, (_, index) => index + 1);
    const k = 100;

    const bruteTime = benchmark(
        maximumSumSubarrayOfSizeKBruteForce,
        data,
        k
    );

    const optimizedTime = benchmark(
        maximumSumSubarrayOfSizeK,
        data,
        k
    );

    console.log(`Input size: ${data.length}`);
    console.log(`Window size: ${k}`);
    console.log(`Brute-force: ${bruteTime.toFixed(4)} ms`);
    console.log(`Sliding window: ${optimizedTime.toFixed(4)} ms`);

    console.log(
        "\nBenchmark timings vary by machine and runtime. " +
        "The important distinction is O(n*k) versus O(n)."
    );
}


// ============================================================================
// Main
// ============================================================================

function main() {
    printSection("DAY 19 — ARRAY ASSESSMENT");

    console.log(
        "Assessment: 3 Easy + 4 Medium + 1 Difficult"
    );

    console.log(
        "Patterns: prefix sums, two pointers, sliding window, " +
        "Kadane's algorithm, hashing, prefix/suffix products"
    );

    demonstrateEasyProblems();
    demonstrateMediumProblems();
    demonstrateHardProblem();
    demonstrateEdgeCases();
    printAssessmentDocumentation();
    runTests();
    demonstratePerformance();

    printSection("ASSESSMENT COMPLETE");
    console.log(
        "All eight array problems were implemented, tested, and documented."
    );
}

main();
