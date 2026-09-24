"use strict";

/*
 * Day 15 — Two Pointers
 *
 * JavaScript study implementation covering:
 * - Opposite-direction pointers
 * - Same-direction pointers
 * - Sorted-array techniques
 * - Pair sum
 * - Reverse array
 * - Remove duplicates
 * - Container-style problems
 * - Three-sum foundations
 * - Partitioning
 * - Edge cases
 * - Validation
 * - Complexity
 * - Testing
 *
 * The file runs with modern Node.js and requires no external packages.
 */

// -----------------------------------------------------------------------------
// 1. BASIC UTILITIES
// -----------------------------------------------------------------------------

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function arraysEqual(first, second) {
    return (
        first.length === second.length &&
        first.every((value, index) => value === second[index])
    );
}

// -----------------------------------------------------------------------------
// 2. PAIR SUM
// -----------------------------------------------------------------------------

function pairSumSorted(numbers, target) {
    /*
     * numbers must be sorted.
     *
     * If the current sum is too small, moving left rightward is the only
     * pointer movement that can increase the sum.
     *
     * If the sum is too large, moving right leftward can decrease it.
     *
     * Time: O(n)
     * Extra space: O(1)
     */
    let left = 0;
    let right = numbers.length - 1;

    while (left < right) {
        const currentSum = numbers[left] + numbers[right];

        if (currentSum === target) {
            return [left, right];
        }

        if (currentSum < target) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    return null;
}

function pairSumBruteForce(numbers, target) {
    for (let left = 0; left < numbers.length; left += 1) {
        for (let right = left + 1; right < numbers.length; right += 1) {
            if (numbers[left] + numbers[right] === target) {
                return [left, right];
            }
        }
    }

    return null;
}

function demonstratePairSum() {
    printSection("PAIR SUM");

    const numbers = [1, 2, 4, 6, 8, 9, 11];
    const target = 15;

    const result = pairSumSorted(numbers, target);

    console.log("Numbers:", numbers);
    console.log("Target:", target);
    console.log("Indices:", result);

    if (result) {
        console.log(
            "Values:",
            numbers[result[0]],
            numbers[result[1]]
        );
    }

    for (const [values, desired] of [
        [[1, 2, 3, 4, 5], 7],
        [[1, 2, 3], 100],
        [[], 10],
        [[5], 10],
    ]) {
        console.log(
            `values=${JSON.stringify(values)}, target=${desired}, result=`,
            pairSumSorted(values, desired)
        );
    }
}

// -----------------------------------------------------------------------------
// 3. OPPOSITE-DIRECTION POINTERS
// -----------------------------------------------------------------------------

function reverseInPlace(values) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        [values[left], values[right]] = [values[right], values[left]];
        left += 1;
        right -= 1;
    }

    return values;
}

function isPalindrome(values) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        if (values[left] !== values[right]) {
            return false;
        }

        left += 1;
        right -= 1;
    }

    return true;
}

function demonstrateOppositePointers() {
    printSection("REVERSE AND PALINDROME");

    const values = [10, 20, 30, 40, 50];

    console.log("Before:", values);
    reverseInPlace(values);
    console.log("After:", values);

    for (const example of [
        [1, 2, 3, 2, 1],
        [1, 2, 3],
        [],
        [7],
    ]) {
        console.log(
            `${JSON.stringify(example)} -> palindrome=${isPalindrome(example)}`
        );
    }
}

// -----------------------------------------------------------------------------
// 4. SAME-DIRECTION READ/WRITE POINTERS
// -----------------------------------------------------------------------------

function removeDuplicatesSorted(values) {
    /*
     * Read pointer scans the array.
     * Write pointer marks the next location for a unique value.
     *
     * The array prefix values[0..write-1] is always the valid result.
     *
     * Time: O(n)
     * Extra space: O(1)
     */
    if (values.length === 0) {
        return 0;
    }

    let write = 1;

    for (let read = 1; read < values.length; read += 1) {
        if (values[read] !== values[write - 1]) {
            values[write] = values[read];
            write += 1;
        }
    }

    return write;
}

function moveZeroes(values) {
    let write = 0;

    for (let read = 0; read < values.length; read += 1) {
        if (values[read] !== 0) {
            [values[write], values[read]] = [values[read], values[write]];
            write += 1;
        }
    }

    return values;
}

function demonstrateSameDirectionPointers() {
    printSection("SAME-DIRECTION POINTERS");

    for (const example of [
        [1, 1, 2, 2, 3, 3],
        [],
        [5],
        [2, 2, 2, 2],
    ]) {
        const values = [...example];
        const length = removeDuplicatesSorted(values);

        console.log({
            original: example,
            uniquePrefix: values.slice(0, length),
            logicalLength: length,
        });
    }

    for (const example of [
        [0, 1, 0, 3, 12],
        [0, 0, 0],
        [1, 2, 3],
        [],
    ]) {
        console.log(
            "Move zeroes:",
            moveZeroes([...example])
        );
    }
}

// -----------------------------------------------------------------------------
// 5. CONTAINER PROBLEM
// -----------------------------------------------------------------------------

function maxContainerArea(heights) {
    /*
     * The area is:
     *
     *     min(leftHeight, rightHeight) * width
     *
     * Moving the taller wall cannot improve the limiting height while
     * the shorter wall remains fixed. Therefore the shorter wall moves.
     *
     * Time: O(n)
     * Extra space: O(1)
     */
    let left = 0;
    let right = heights.length - 1;
    let bestArea = 0;

    while (left < right) {
        const width = right - left;
        const height = Math.min(heights[left], heights[right]);

        bestArea = Math.max(bestArea, width * height);

        if (heights[left] <= heights[right]) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    return bestArea;
}

function maxContainerAreaBruteForce(heights) {
    let bestArea = 0;

    for (let left = 0; left < heights.length; left += 1) {
        for (let right = left + 1; right < heights.length; right += 1) {
            const area =
                Math.min(heights[left], heights[right]) *
                (right - left);

            bestArea = Math.max(bestArea, area);
        }
    }

    return bestArea;
}

function demonstrateContainer() {
    printSection("CONTAINER-STYLE PROBLEM");

    const examples = [
        [1, 8, 6, 2, 5, 4, 8, 3, 7],
        [1, 1],
        [5, 4, 3, 2, 1],
        [],
    ];

    for (const heights of examples) {
        console.log(
            heights,
            "->",
            maxContainerArea(heights)
        );
    }
}

// -----------------------------------------------------------------------------
// 6. THREE-SUM
// -----------------------------------------------------------------------------

function threeSum(values, target = 0) {
    /*
     * Sort first, then fix one value and solve the remaining pair problem
     * with two pointers.
     *
     * Time: O(n^2)
     * Space: O(n) for the sorted copy.
     */
    const numbers = [...values].sort((a, b) => a - b);
    const result = [];

    for (let i = 0; i < numbers.length - 2; i += 1) {
        if (i > 0 && numbers[i] === numbers[i - 1]) {
            continue;
        }

        let left = i + 1;
        let right = numbers.length - 1;

        while (left < right) {
            const currentSum =
                numbers[i] + numbers[left] + numbers[right];

            if (currentSum === target) {
                result.push([
                    numbers[i],
                    numbers[left],
                    numbers[right],
                ]);

                const leftValue = numbers[left];
                const rightValue = numbers[right];

                while (
                    left < right &&
                    numbers[left] === leftValue
                ) {
                    left += 1;
                }

                while (
                    left < right &&
                    numbers[right] === rightValue
                ) {
                    right -= 1;
                }
            } else if (currentSum < target) {
                left += 1;
            } else {
                right -= 1;
            }
        }
    }

    return result;
}

function demonstrateThreeSum() {
    printSection("THREE-SUM FOUNDATIONS");

    for (const [values, target] of [
        [[-1, 0, 1, 2, -1, -4], 0],
        [[0, 0, 0, 0], 0],
        [[1, 2, 3, 4], 100],
        [[-2, 0, 1, 1, 2], 0],
    ]) {
        console.log(
            `values=${JSON.stringify(values)}, target=${target}`,
            "triples=",
            threeSum(values, target)
        );
    }
}

// -----------------------------------------------------------------------------
// 7. PARTITIONING
// -----------------------------------------------------------------------------

function partitionAroundValue(values, pivot) {
    let boundary = 0;

    for (let current = 0; current < values.length; current += 1) {
        if (values[current] < pivot) {
            [values[boundary], values[current]] = [
                values[current],
                values[boundary],
            ];

            boundary += 1;
        }
    }

    return boundary;
}

function dutchNationalFlag(values) {
    /*
     * Three regions:
     * [0, low)       => 0
     * [low, mid)     => 1
     * [mid, high]    => unknown
     * (high, end)    => 2
     */
    let low = 0;
    let mid = 0;
    let high = values.length - 1;

    while (mid <= high) {
        if (values[mid] === 0) {
            [values[low], values[mid]] = [
                values[mid],
                values[low],
            ];
            low += 1;
            mid += 1;
        } else if (values[mid] === 1) {
            mid += 1;
        } else if (values[mid] === 2) {
            [values[mid], values[high]] = [
                values[high],
                values[mid],
            ];
            high -= 1;
        } else {
            throw new Error(
                "Dutch National Flag input must contain only 0, 1, and 2."
            );
        }
    }

    return values;
}

function demonstratePartitioning() {
    printSection("PARTITION-STYLE PROBLEMS");

    const values = [9, 4, 7, 3, 10, 2, 8, 1];
    const boundary = partitionAroundValue(values, 6);

    console.log("Partitioned:", values);
    console.log("Boundary:", boundary);

    const colors = [2, 0, 2, 1, 1, 0, 2, 0];
    console.log(
        "Dutch National Flag:",
        dutchNationalFlag(colors)
    );
}

// -----------------------------------------------------------------------------
// 8. OTHER TWO-POINTER PATTERNS
// -----------------------------------------------------------------------------

function sortedSquares(values) {
    const result = new Array(values.length);
    let left = 0;
    let right = values.length - 1;
    let write = values.length - 1;

    while (left <= right) {
        const leftSquare = values[left] ** 2;
        const rightSquare = values[right] ** 2;

        if (leftSquare > rightSquare) {
            result[write] = leftSquare;
            left += 1;
        } else {
            result[write] = rightSquare;
            right -= 1;
        }

        write -= 1;
    }

    return result;
}

function validPalindromeAfterOneDeletion(text) {
    function isRangePalindrome(left, right) {
        while (left < right) {
            if (text[left] !== text[right]) {
                return false;
            }

            left += 1;
            right -= 1;
        }

        return true;
    }

    let left = 0;
    let right = text.length - 1;

    while (left < right) {
        if (text[left] !== text[right]) {
            return (
                isRangePalindrome(left + 1, right) ||
                isRangePalindrome(left, right - 1)
            );
        }

        left += 1;
        right -= 1;
    }

    return true;
}

function mergeSortedArrays(first, second) {
    const result = [];
    let firstIndex = 0;
    let secondIndex = 0;

    while (
        firstIndex < first.length &&
        secondIndex < second.length
    ) {
        if (first[firstIndex] <= second[secondIndex]) {
            result.push(first[firstIndex]);
            firstIndex += 1;
        } else {
            result.push(second[secondIndex]);
            secondIndex += 1;
        }
    }

    while (firstIndex < first.length) {
        result.push(first[firstIndex]);
        firstIndex += 1;
    }

    while (secondIndex < second.length) {
        result.push(second[secondIndex]);
        secondIndex += 1;
    }

    return result;
}

function demonstrateAdvancedVariations() {
    printSection("ADVANCED VARIATIONS");

    console.log(
        "Sorted squares:",
        sortedSquares([-7, -3, -1, 2, 4, 8])
    );

    for (const text of ["aba", "abca", "abc", "", "deeee"]) {
        console.log(
            text,
            "=>",
            validPalindromeAfterOneDeletion(text)
        );
    }

    console.log(
        "Merged:",
        mergeSortedArrays([1, 4, 7], [2, 3, 8, 9])
    );
}

// -----------------------------------------------------------------------------
// 9. VALIDATION AND DEBUGGING
// -----------------------------------------------------------------------------

function requireSorted(values) {
    for (let index = 1; index < values.length; index += 1) {
        if (values[index] < values[index - 1]) {
            throw new Error("The sequence must be sorted.");
        }
    }
}

function safePairSumSorted(numbers, target) {
    requireSorted(numbers);
    return pairSumSorted(numbers, target);
}

function tracePairSum(numbers, target) {
    let left = 0;
    let right = numbers.length - 1;

    console.log("Pair-sum pointer trace:");

    while (left < right) {
        const currentSum = numbers[left] + numbers[right];

        console.log({
            left,
            right,
            leftValue: numbers[left],
            rightValue: numbers[right],
            currentSum,
        });

        if (currentSum === target) {
            console.log("Target found.");
            return;
        }

        if (currentSum < target) {
            left += 1;
        } else {
            right -= 1;
        }
    }

    console.log("No pair found.");
}

// -----------------------------------------------------------------------------
// 10. RANDOMIZED VERIFICATION
// -----------------------------------------------------------------------------

function randomInteger(random, minimum, maximum) {
    return Math.floor(
        random() * (maximum - minimum + 1)
    ) + minimum;
}

function verifyPairSum() {
    /*
     * A deterministic pseudo-random generator is used so that the test
     * is reproducible without external libraries.
     */
    let seed = 123456789;

    function random() {
        seed = (1664525 * seed + 1013904223) >>> 0;
        return seed / 0x100000000;
    }

    for (let test = 0; test < 500; test += 1) {
        const length = randomInteger(random, 0, 15);
        const values = [];

        for (let index = 0; index < length; index += 1) {
            values.push(randomInteger(random, -20, 20));
        }

        values.sort((a, b) => a - b);

        const target = randomInteger(random, -30, 30);

        const pointerResult = pairSumSorted(values, target);
        const bruteResult = pairSumBruteForce(values, target);

        assert(
            (pointerResult !== null) === (bruteResult !== null),
            "Pair-sum existence mismatch."
        );

        if (pointerResult !== null) {
            const [left, right] = pointerResult;

            assert(
                left < right,
                "Pair-sum pointers must refer to distinct elements."
            );

            assert(
                values[left] + values[right] === target,
                "Pair-sum result is incorrect."
            );
        }
    }

    console.log("Random pair-sum verification: passed 500 cases.");
}

// -----------------------------------------------------------------------------
// 11. TESTS
// -----------------------------------------------------------------------------

function runTests() {
    printSection("UNIT TESTS");

    assert(
        arraysEqual(pairSumSorted([1, 2, 4, 7, 11], 9), [1, 3]),
        "pairSumSorted failed."
    );

    assert(
        pairSumSorted([1, 2, 3], 100) === null,
        "pairSumSorted no-result case failed."
    );

    assert(
        arraysEqual(
            reverseInPlace([1, 2, 3, 4]),
            [4, 3, 2, 1]
        ),
        "reverseInPlace failed."
    );

    const duplicateValues = [1, 1, 2, 2, 3];
    const uniqueLength = removeDuplicatesSorted(duplicateValues);

    assert(
        uniqueLength === 3,
        "removeDuplicatesSorted length failed."
    );

    assert(
        arraysEqual(
            duplicateValues.slice(0, uniqueLength),
            [1, 2, 3]
        ),
        "removeDuplicatesSorted content failed."
    );

    assert(
        maxContainerArea([1, 8, 6, 2, 5, 4, 8, 3, 7]) === 49,
        "maxContainerArea failed."
    );

    assert(
        maxContainerArea([1, 8, 6, 2, 5, 4, 8, 3, 7]) ===
        maxContainerAreaBruteForce([1, 8, 6, 2, 5, 4, 8, 3, 7]),
        "Container implementations disagree."
    );

    assert(
        JSON.stringify(threeSum([-1, 0, 1, 2, -1, -4])) ===
        JSON.stringify([[-1, -1, 2], [-1, 0, 1]]),
        "threeSum failed."
    );

    assert(
        JSON.stringify(threeSum([0, 0, 0, 0])) ===
        JSON.stringify([[0, 0, 0]]),
        "threeSum duplicate handling failed."
    );

    const partitionValues = [3, 5, 2, 8, 1, 7];
    const boundary = partitionAroundValue(partitionValues, 5);

    assert(
        partitionValues
            .slice(0, boundary)
            .every((value) => value < 5),
        "Partition left side failed."
    );

    assert(
        partitionValues
            .slice(boundary)
            .every((value) => value >= 5),
        "Partition right side failed."
    );

    const colors = [2, 0, 2, 1, 1, 0];
    dutchNationalFlag(colors);

    assert(
        arraysEqual(colors, [0, 0, 1, 1, 2, 2]),
        "Dutch National Flag failed."
    );

    assert(
        arraysEqual(
            sortedSquares([-7, -3, -1, 2, 4, 8]),
            [1, 4, 9, 16, 49, 64]
        ),
        "sortedSquares failed."
    );

    assert(
        validPalindromeAfterOneDeletion("abca"),
        "One-deletion palindrome failed."
    );

    assert(
        !validPalindromeAfterOneDeletion("abc"),
        "Invalid one-deletion palindrome failed."
    );

    assert(
        arraysEqual(
            mergeSortedArrays([1, 4, 7], [2, 3, 8, 9]),
            [1, 2, 3, 4, 7, 8, 9]
        ),
        "mergeSortedArrays failed."
    );

    let validationFailed = false;

    try {
        safePairSumSorted([1, 5, 3, 7], 8);
    } catch (error) {
        validationFailed = true;
    }

    assert(
        validationFailed,
        "Sorted-input validation failed."
    );

    console.log("All JavaScript tests passed.");
}

// -----------------------------------------------------------------------------
// 12. MAIN
// -----------------------------------------------------------------------------

function main() {
    printSection("DAY 15 — TWO POINTERS");

    console.log(
        [
            "Core patterns:",
            "1. Opposite-direction pointers",
            "2. Same-direction read/write pointers",
            "3. Sorted-array pair search",
            "4. Partitioning",
            "5. Nested outer loop + two-pointer search",
        ].join("\n")
    );

    demonstratePairSum();
    demonstrateOppositePointers();
    demonstrateSameDirectionPointers();
    demonstrateContainer();
    demonstrateThreeSum();
    demonstratePartitioning();
    demonstrateAdvancedVariations();

    printSection("VALIDATION AND DEBUGGING");

    console.log(
        "Validated pair sum:",
        safePairSumSorted([1, 3, 5, 7, 9], 10)
    );

    tracePairSum([1, 3, 4, 6, 8, 10], 14);

    verifyPairSum();
    runTests();

    printSection("COMPLEXITY GUIDE");

    console.log(`
Pair sum, sorted + two pointers: O(n) time, O(1) extra space
Reverse in place:                O(n) time, O(1) extra space
Remove duplicates:               O(n) time, O(1) extra space
Container problem:               O(n) time, O(1) extra space
Three-sum after sorting:         O(n^2) time, O(n) copy space
Sorted squares:                  O(n) time, O(n) result space

The defining advantage is not simply having two variables named
"left" and "right". The important property is that pointer movement
eliminates candidates using a valid invariant.
`);
}

main();
