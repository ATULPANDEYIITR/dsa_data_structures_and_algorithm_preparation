"use strict";

/*
 * Day 25 — String Sliding Window
 *
 * Comprehensive JavaScript study file covering:
 * - Sliding-window fundamentals
 * - Longest substring without repetition
 * - Character-frequency windows
 * - Minimum-window substring
 * - At-most-K-distinct-character problems
 * - Exactly-K-distinct-character problems
 * - Fixed-size windows
 * - Frequency constraints
 * - Anagram windows
 * - Error handling and validation
 * - Debugging and tracing
 * - Performance considerations
 *
 * Run with:
 *     node day25_string_sliding_window.js
 */


// ============================================================================
// 1. DISPLAY HELPERS
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


// ============================================================================
// 2. FIXED-SIZE SLIDING WINDOW
// ============================================================================

function fixedSizeWindowSums(values, k) {
    if (!Number.isInteger(k) || k <= 0) {
        throw new RangeError("k must be a positive integer.");
    }

    if (k > values.length) {
        return [];
    }

    const result = [];
    let currentSum = 0;

    for (let i = 0; i < k; i++) {
        currentSum += values[i];
    }

    result.push(currentSum);

    for (let right = k; right < values.length; right++) {
        currentSum -= values[right - k];
        currentSum += values[right];
        result.push(currentSum);
    }

    return result;
}


// ============================================================================
// 3. LONGEST SUBSTRING WITHOUT REPETITION
// ============================================================================

function longestSubstringWithoutRepetition(text) {
    /*
     * Map stores the most recent index of each character.
     *
     * If a duplicate is encountered at `right`, the left boundary can jump
     * directly beyond the previous occurrence instead of removing characters
     * one by one.
     *
     * The Math.max call prevents the left boundary from moving backward.
     *
     * JavaScript strings are UTF-16 sequences. Array.from(text) converts the
     * string into Unicode code points, making this implementation friendlier
     * to characters such as emoji than direct text[index] access.
     */

    const characters = Array.from(text);
    const lastSeen = new Map();

    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        if (lastSeen.has(character)) {
            left = Math.max(left, lastSeen.get(character) + 1);
        }

        lastSeen.set(character, right);

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        length: bestLength,
        substring: characters.slice(bestStart, bestStart + bestLength).join("")
    };
}


// ============================================================================
// 4. CHARACTER FREQUENCY MAP
// ============================================================================

function buildFrequencyMap(text) {
    const frequencies = new Map();

    for (const character of Array.from(text)) {
        frequencies.set(
            character,
            (frequencies.get(character) || 0) + 1
        );
    }

    return frequencies;
}

function mapToObject(map) {
    return Object.fromEntries(map.entries());
}


// ============================================================================
// 5. LONGEST SUBSTRING WITH AT MOST K DISTINCT
// ============================================================================

function longestSubstringAtMostKDistinct(text, k) {
    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer.");
    }

    if (k === 0 || text.length === 0) {
        return {
            length: 0,
            substring: ""
        };
    }

    const characters = Array.from(text);
    const frequencies = new Map();

    let left = 0;
    let distinct = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        if (!frequencies.has(character)) {
            frequencies.set(character, 0);
            distinct++;
        }

        frequencies.set(
            character,
            frequencies.get(character) + 1
        );

        while (distinct > k) {
            const outgoing = characters[left];
            const newFrequency = frequencies.get(outgoing) - 1;

            if (newFrequency === 0) {
                frequencies.delete(outgoing);
                distinct--;
            } else {
                frequencies.set(outgoing, newFrequency);
            }

            left++;
        }

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        length: bestLength,
        substring: characters
            .slice(bestStart, bestStart + bestLength)
            .join("")
    };
}


// ============================================================================
// 6. COUNT SUBSTRINGS WITH AT MOST K DISTINCT
// ============================================================================

function countSubstringsAtMostKDistinct(text, k) {
    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer.");
    }

    if (k === 0 || text.length === 0) {
        return 0;
    }

    const characters = Array.from(text);
    const frequencies = new Map();

    let left = 0;
    let distinct = 0;
    let count = 0;

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        if (!frequencies.has(character)) {
            frequencies.set(character, 0);
            distinct++;
        }

        frequencies.set(
            character,
            frequencies.get(character) + 1
        );

        while (distinct > k) {
            const outgoing = characters[left];
            const newFrequency = frequencies.get(outgoing) - 1;

            if (newFrequency === 0) {
                frequencies.delete(outgoing);
                distinct--;
            } else {
                frequencies.set(outgoing, newFrequency);
            }

            left++;
        }

        /*
         * Every start between left and right produces a valid substring
         * ending at right.
         */
        count += right - left + 1;
    }

    return count;
}


// ============================================================================
// 7. EXACTLY K DISTINCT
// ============================================================================

function countSubstringsExactlyKDistinct(text, k) {
    if (!Number.isInteger(k) || k <= 0) {
        return 0;
    }

    return (
        countSubstringsAtMostKDistinct(text, k) -
        countSubstringsAtMostKDistinct(text, k - 1)
    );
}

function longestSubstringExactlyKDistinct(text, k) {
    if (!Number.isInteger(k) || k <= 0) {
        return {
            length: 0,
            substring: ""
        };
    }

    const characters = Array.from(text);
    const frequencies = new Map();

    let left = 0;
    let distinct = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        if (!frequencies.has(character)) {
            frequencies.set(character, 0);
            distinct++;
        }

        frequencies.set(
            character,
            frequencies.get(character) + 1
        );

        while (distinct > k) {
            const outgoing = characters[left];
            const newFrequency = frequencies.get(outgoing) - 1;

            if (newFrequency === 0) {
                frequencies.delete(outgoing);
                distinct--;
            } else {
                frequencies.set(outgoing, newFrequency);
            }

            left++;
        }

        if (distinct === k) {
            const currentLength = right - left + 1;

            if (currentLength > bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }
        }
    }

    return {
        length: bestLength,
        substring: characters
            .slice(bestStart, bestStart + bestLength)
            .join("")
    };
}


// ============================================================================
// 8. MINIMUM WINDOW SUBSTRING
// ============================================================================

function minimumWindowSubstring(text, target) {
    /*
     * `required` describes what the target needs.
     * `window` describes what the current window contains.
     *
     * `satisfied` counts how many distinct required characters currently have
     * exactly enough copies in the window.
     *
     * Once all requirements are satisfied, the left boundary moves rightward
     * to make the valid window as small as possible.
     */

    if (text.length === 0 || target.length === 0) {
        return "";
    }

    const source = Array.from(text);
    const targetCharacters = Array.from(target);

    if (targetCharacters.length > source.length) {
        return "";
    }

    const required = buildFrequencyMap(target);
    const window = new Map();

    const requiredDistinct = required.size;

    let satisfied = 0;
    let left = 0;

    let bestStart = 0;
    let bestLength = Infinity;

    for (let right = 0; right < source.length; right++) {
        const character = source[right];

        window.set(
            character,
            (window.get(character) || 0) + 1
        );

        if (
            required.has(character) &&
            window.get(character) === required.get(character)
        ) {
            satisfied++;
        }

        while (satisfied === requiredDistinct) {
            const currentLength = right - left + 1;

            if (currentLength < bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }

            const outgoing = source[left];
            const newFrequency = window.get(outgoing) - 1;

            window.set(outgoing, newFrequency);

            if (
                required.has(outgoing) &&
                newFrequency < required.get(outgoing)
            ) {
                satisfied--;
            }

            left++;
        }
    }

    if (bestLength === Infinity) {
        return "";
    }

    return source
        .slice(bestStart, bestStart + bestLength)
        .join("");
}


// ============================================================================
// 9. ANAGRAM WINDOWS
// ============================================================================

function findAnagramStartIndices(text, pattern) {
    const source = Array.from(text);
    const target = Array.from(pattern);

    if (target.length === 0 || target.length > source.length) {
        return [];
    }

    const required = buildFrequencyMap(pattern);
    const window = new Map();

    const result = [];
    const k = target.length;

    let matchingCharacterKinds = 0;

    for (let right = 0; right < source.length; right++) {
        const incoming = source[right];
        const oldCount = window.get(incoming) || 0;
        const newCount = oldCount + 1;

        window.set(incoming, newCount);

        if (
            required.has(incoming) &&
            newCount === required.get(incoming)
        ) {
            matchingCharacterKinds++;
        }

        if (right >= k) {
            const outgoing = source[right - k];
            const outgoingOldCount = window.get(outgoing);
            const outgoingNewCount = outgoingOldCount - 1;

            if (
                required.has(outgoing) &&
                outgoingOldCount === required.get(outgoing)
            ) {
                matchingCharacterKinds--;
            }

            if (outgoingNewCount === 0) {
                window.delete(outgoing);
            } else {
                window.set(outgoing, outgoingNewCount);
            }
        }

        if (
            right >= k - 1 &&
            matchingCharacterKinds === required.size &&
            window.size === required.size
        ) {
            result.push(right - k + 1);
        }
    }

    return result;
}


// ============================================================================
// 10. LONGEST REPEATING CHARACTER REPLACEMENT
// ============================================================================

function longestRepeatingCharacterReplacement(text, k) {
    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer.");
    }

    const characters = Array.from(text);
    const frequencies = new Map();

    let left = 0;
    let highestFrequency = 0;

    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        const newFrequency = (frequencies.get(character) || 0) + 1;

        frequencies.set(character, newFrequency);
        highestFrequency = Math.max(
            highestFrequency,
            newFrequency
        );

        /*
         * Number of replacements required:
         *
         * window length - frequency of the most common character
         */
        while (
            (right - left + 1) - highestFrequency > k
        ) {
            const outgoing = characters[left];
            frequencies.set(
                outgoing,
                frequencies.get(outgoing) - 1
            );
            left++;
        }

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        length: bestLength,
        substring: characters
            .slice(bestStart, bestStart + bestLength)
            .join("")
    };
}


// ============================================================================
// 11. LONGEST BINARY WINDOW WITH AT MOST K ZEROS
// ============================================================================

function longestBinaryWindowAtMostKZeros(values, k) {
    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer.");
    }

    let left = 0;
    let zeroCount = 0;

    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < values.length; right++) {
        const value = values[right];

        if (value === 0) {
            zeroCount++;
        } else if (value !== 1) {
            throw new TypeError("The array must contain only 0 and 1.");
        }

        while (zeroCount > k) {
            if (values[left] === 0) {
                zeroCount--;
            }

            left++;
        }

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return {
        length: bestLength,
        values: values.slice(
            bestStart,
            bestStart + bestLength
        )
    };
}


// ============================================================================
// 12. DEBUG TRACE
// ============================================================================

function traceLongestUnique(text) {
    printSection("Sliding-Window Debug Trace");

    const characters = Array.from(text);
    const lastSeen = new Map();

    let left = 0;

    console.log(`Input: ${JSON.stringify(text)}`);

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        console.log(
            `\nRIGHT = ${right}, character = ${JSON.stringify(character)}`
        );

        if (lastSeen.has(character)) {
            const oldLeft = left;

            left = Math.max(
                left,
                lastSeen.get(character) + 1
            );

            console.log(
                `Duplicate found. LEFT: ${oldLeft} -> ${left}`
            );
        }

        lastSeen.set(character, right);

        console.log(
            `Window = [${left}, ${right}]`
        );

        console.log(
            `Current = ${characters
                .slice(left, right + 1)
                .join("")}`
        );
    }
}


// ============================================================================
// 13. ERROR-HANDLING EXAMPLES
// ============================================================================

function demonstrateValidation() {
    printSection("Validation and Failure Conditions");

    const invalidOperations = [
        () => longestSubstringAtMostKDistinct("abc", -1),
        () => fixedSizeWindowSums([1, 2, 3], 0),
        () => longestRepeatingCharacterReplacement("ABC", -2),
        () => longestBinaryWindowAtMostKZeros([1, 2, 0], 1)
    ];

    for (const operation of invalidOperations) {
        try {
            operation();
        } catch (error) {
            console.log(
                `${error.constructor.name}: ${error.message}`
            );
        }
    }
}


// ============================================================================
// 14. TESTS
// ============================================================================

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(
            `${message}\nExpected: ${expected}\nActual: ${actual}`
        );
    }
}

function runTests() {
    printSection("Automated Tests");

    assertEqual(
        longestSubstringWithoutRepetition("").length,
        0,
        "Empty string"
    );

    assertEqual(
        longestSubstringWithoutRepetition("abcabcbb").length,
        3,
        "abcabcbb"
    );

    assertEqual(
        longestSubstringWithoutRepetition("bbbbb").length,
        1,
        "bbbbb"
    );

    assertEqual(
        longestSubstringWithoutRepetition("pwwkew").length,
        3,
        "pwwkew"
    );

    assertEqual(
        longestSubstringWithoutRepetition("abba").length,
        2,
        "abba"
    );

    assertEqual(
        longestSubstringAtMostKDistinct("eceba", 2).length,
        3,
        "At most two distinct"
    );

    assertEqual(
        countSubstringsExactlyKDistinct("pqpqs", 2),
        7,
        "Exactly two distinct"
    );

    assertEqual(
        minimumWindowSubstring("ADOBECODEBANC", "ABC"),
        "BANC",
        "Minimum window"
    );

    assertEqual(
        minimumWindowSubstring("a", "aa"),
        "",
        "Impossible minimum window"
    );

    assertEqual(
        JSON.stringify(findAnagramStartIndices("cbaebabacd", "abc")),
        JSON.stringify([0, 6]),
        "Anagram indices"
    );

    assertEqual(
        longestRepeatingCharacterReplacement("AABABBA", 1).length,
        4,
        "Character replacement"
    );

    assertEqual(
        longestBinaryWindowAtMostKZeros(
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
            2
        ).length,
        6,
        "Binary window"
    );

    console.log("All tests passed.");
}


// ============================================================================
// 15. MAIN DEMONSTRATION
// ============================================================================

function main() {
    printSection("Day 25 — String Sliding Window");

    printSubsection("Fixed-Size Window");

    console.log(
        fixedSizeWindowSums([2, 1, 5, 1, 3, 2], 3)
    );

    printSubsection("Longest Substring Without Repetition");

    for (const text of [
        "",
        "a",
        "abcabcbb",
        "bbbbb",
        "pwwkew",
        "dvdf",
        "abba",
        "😀ab😀cd"
    ]) {
        console.log(
            JSON.stringify(text),
            "->",
            longestSubstringWithoutRepetition(text)
        );
    }

    printSubsection("Frequency Maps");

    console.log(
        mapToObject(buildFrequencyMap("aabccbb"))
    );

    printSubsection("At-Most-K Distinct");

    for (const [text, k] of [
        ["eceba", 2],
        ["aa", 1],
        ["aabbcc", 2],
        ["abcadcacacaca", 2]
    ]) {
        console.log(
            text,
            k,
            "->",
            longestSubstringAtMostKDistinct(text, k)
        );
    }

    printSubsection("Minimum Window");

    for (const [text, target] of [
        ["ADOBECODEBANC", "ABC"],
        ["a", "a"],
        ["a", "aa"],
        ["aa", "aa"],
        ["aaflslflsldkalskaaa", "aaa"],
        ["abc", "xyz"]
    ]) {
        console.log(
            JSON.stringify(text),
            JSON.stringify(target),
            "->",
            JSON.stringify(minimumWindowSubstring(text, target))
        );
    }

    printSubsection("Exactly-K Distinct");

    for (const [text, k] of [
        ["pqpqs", 2],
        ["a", 1],
        ["abc", 2],
        ["aabbcc", 2]
    ]) {
        console.log(
            `${text}, k=${k}`,
            "count=",
            countSubstringsExactlyKDistinct(text, k),
            "longest=",
            longestSubstringExactlyKDistinct(text, k)
        );
    }

    printSubsection("Anagram Windows");

    console.log(
        findAnagramStartIndices("cbaebabacd", "abc")
    );

    console.log(
        findAnagramStartIndices("abab", "ab")
    );

    printSubsection("Character Replacement");

    console.log(
        longestRepeatingCharacterReplacement("AABABBA", 1)
    );

    printSubsection("Binary Sliding Window");

    console.log(
        longestBinaryWindowAtMostKZeros(
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
            2
        )
    );

    traceLongestUnique("abcad");

    demonstrateValidation();

    runTests();

    printSection("Complexity Reference");

    console.table([
        {
            Problem: "Longest unique substring",
            Time: "O(n)",
            Space: "O(min(n, alphabet))"
        },
        {
            Problem: "At most K distinct",
            Time: "O(n)",
            Space: "O(min(n, alphabet))"
        },
        {
            Problem: "Minimum window",
            Time: "O(n + m)",
            Space: "O(distinct target)"
        },
        {
            Problem: "Exactly K distinct",
            Time: "O(n)",
            Space: "O(min(n, alphabet))"
        },
        {
            Problem: "Anagram windows",
            Time: "O(n)",
            Space: "O(distinct pattern)"
        }
    ]);
}

main();
