"use strict";

/*
 * Day 22 — Palindromes
 *
 * This file complements the Python study implementation with JavaScript
 * examples covering:
 *   - character palindromes
 *   - two-pointer checking
 *   - valid palindromes
 *   - number palindromes
 *   - remove-one-character palindrome
 *   - substring palindromes
 *   - longest palindromic substring
 *   - dynamic programming
 *   - Manacher's algorithm
 *   - palindrome permutations
 *   - palindrome partitioning
 *   - testing and performance considerations
 *
 * The file requires no external npm packages.
 */


// ============================================================
// 1. BASIC CHARACTER PALINDROME
// ============================================================

function isCharacterPalindrome(text) {
    return text === [...text].reverse().join("");
}


// Explicit loop version demonstrates the underlying comparison process.
function isCharacterPalindromeLoop(text) {
    let left = 0;
    let right = text.length - 1;

    while (left < right) {
        if (text[left] !== text[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}


// ============================================================
// 2. TWO-POINTER PALINDROME
// ============================================================

function isTwoPointerPalindrome(text) {
    let left = 0;
    let right = text.length - 1;

    while (left < right) {
        if (text[left] !== text[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}


// ============================================================
// 3. VALID PALINDROME
// ============================================================

function isAsciiAlphaNumeric(character) {
    return /^[A-Za-z0-9]$/.test(character);
}


function isValidPalindrome(text) {
    /*
     * JavaScript string indexing works with UTF-16 code units.
     * For ordinary ASCII-oriented interview problems this is sufficient.
     * The normalization implementation below handles Unicode code points
     * more naturally through Array.from().
     */
    const characters = [...text]
        .filter((character) => /[\p{L}\p{N}]/u.test(character))
        .map((character) => character.toLocaleLowerCase());

    let left = 0;
    let right = characters.length - 1;

    while (left < right) {
        if (characters[left] !== characters[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}


function normalizeForPalindrome(text) {
    return [...text]
        .filter((character) => /[\p{L}\p{N}]/u.test(character))
        .map((character) => character.toLocaleLowerCase())
        .join("");
}


// ============================================================
// 4. NUMBER PALINDROME
// ============================================================

function isNumberPalindromeString(number) {
    if (!Number.isInteger(number)) {
        throw new TypeError("number must be an integer");
    }

    const value = String(number);
    return value === [...value].reverse().join("");
}


function isNumberPalindromeMath(number) {
    if (!Number.isSafeInteger(number)) {
        throw new RangeError(
            "number must be a JavaScript safe integer"
        );
    }

    if (number < 0) {
        return false;
    }

    if (number !== 0 && number % 10 === 0) {
        return false;
    }

    let remaining = number;
    let reversedHalf = 0;

    while (remaining > reversedHalf) {
        reversedHalf = reversedHalf * 10 + (remaining % 10);
        remaining = Math.floor(remaining / 10);
    }

    return (
        remaining === reversedHalf ||
        remaining === Math.floor(reversedHalf / 10)
    );
}


// ============================================================
// 5. REMOVE ONE CHARACTER
// ============================================================

function canBePalindromeAfterRemovingOne(text) {
    function rangeIsPalindrome(left, right) {
        while (left < right) {
            if (text[left] !== text[right]) {
                return false;
            }

            left++;
            right--;
        }

        return true;
    }

    let left = 0;
    let right = text.length - 1;

    while (left < right) {
        if (text[left] !== text[right]) {
            return (
                rangeIsPalindrome(left + 1, right) ||
                rangeIsPalindrome(left, right - 1)
            );
        }

        left++;
        right--;
    }

    return true;
}


// ============================================================
// 6. SUBSTRING PALINDROME
// ============================================================

function isSubstringPalindrome(text, start, end) {
    if (
        !Number.isInteger(start) ||
        !Number.isInteger(end) ||
        start < 0 ||
        end < start ||
        end > text.length
    ) {
        throw new RangeError("Invalid substring boundaries");
    }

    let left = start;
    let right = end - 1;

    while (left < right) {
        if (text[left] !== text[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}


// ============================================================
// 7. CENTER EXPANSION
// ============================================================

function expandAroundCenter(text, left, right) {
    while (
        left >= 0 &&
        right < text.length &&
        text[left] === text[right]
    ) {
        left--;
        right++;
    }

    return [left + 1, right];
}


function longestPalindromicSubstringCenter(text) {
    if (text.length === 0) {
        return "";
    }

    let bestStart = 0;
    let bestEnd = 1;

    for (let center = 0; center < text.length; center++) {
        let [start, end] = expandAroundCenter(
            text,
            center,
            center
        );

        if (end - start > bestEnd - bestStart) {
            bestStart = start;
            bestEnd = end;
        }

        [start, end] = expandAroundCenter(
            text,
            center,
            center + 1
        );

        if (end - start > bestEnd - bestStart) {
            bestStart = start;
            bestEnd = end;
        }
    }

    return text.slice(bestStart, bestEnd);
}


// ============================================================
// 8. DYNAMIC PROGRAMMING
// ============================================================

function longestPalindromicSubstringDP(text) {
    const n = text.length;

    if (n === 0) {
        return "";
    }

    const dp = Array.from(
        { length: n },
        () => Array(n).fill(false)
    );

    let bestStart = 0;
    let bestLength = 1;

    for (let index = 0; index < n; index++) {
        dp[index][index] = true;
    }

    for (let length = 2; length <= n; length++) {
        for (let left = 0; left + length <= n; left++) {
            const right = left + length - 1;

            if (
                text[left] === text[right] &&
                (length === 2 || dp[left + 1][right - 1])
            ) {
                dp[left][right] = true;

                if (length > bestLength) {
                    bestStart = left;
                    bestLength = length;
                }
            }
        }
    }

    return text.slice(
        bestStart,
        bestStart + bestLength
    );
}


// ============================================================
// 9. MANACHER'S ALGORITHM
// ============================================================

function longestPalindromicSubstringManacher(text) {
    if (text.length === 0) {
        return "";
    }

    /*
     * Sentinels prevent explicit boundary checks during expansion.
     * The # separators make odd/even palindromes uniform.
     */
    const transformed = `^#${[...text].join("#")}#$`;
    const radius = new Array(transformed.length).fill(0);

    let center = 0;
    let rightBoundary = 0;

    for (let index = 1; index < transformed.length - 1; index++) {
        const mirror = 2 * center - index;

        if (index < rightBoundary) {
            radius[index] = Math.min(
                rightBoundary - index,
                radius[mirror]
            );
        }

        while (
            transformed[index + 1 + radius[index]] ===
            transformed[index - 1 - radius[index]]
        ) {
            radius[index]++;
        }

        if (index + radius[index] > rightBoundary) {
            center = index;
            rightBoundary = index + radius[index];
        }
    }

    let bestCenter = 0;
    let bestRadius = 0;

    for (let index = 0; index < radius.length; index++) {
        if (radius[index] > bestRadius) {
            bestRadius = radius[index];
            bestCenter = index;
        }
    }

    const start = Math.floor(
        (bestCenter - bestRadius) / 2
    );

    return [...text]
        .slice(start, start + bestRadius)
        .join("");
}


// ============================================================
// 10. ALL PALINDROMIC SUBSTRINGS
// ============================================================

function allPalindromicSubstrings(text) {
    const result = [];

    for (let center = 0; center < text.length; center++) {
        let left = center;
        let right = center;

        while (
            left >= 0 &&
            right < text.length &&
            text[left] === text[right]
        ) {
            result.push(text.slice(left, right + 1));
            left--;
            right++;
        }

        left = center;
        right = center + 1;

        while (
            left >= 0 &&
            right < text.length &&
            text[left] === text[right]
        ) {
            result.push(text.slice(left, right + 1));
            left--;
            right++;
        }
    }

    return result;
}


// ============================================================
// 11. DISTINCT PALINDROMIC SUBSTRINGS
// ============================================================

function distinctPalindromicSubstrings(text) {
    return new Set(allPalindromicSubstrings(text));
}


// ============================================================
// 12. PALINDROME PERMUTATION
// ============================================================

function canRearrangeIntoPalindrome(text) {
    const frequency = new Map();

    for (const character of text) {
        frequency.set(
            character,
            (frequency.get(character) || 0) + 1
        );
    }

    let oddCount = 0;

    for (const count of frequency.values()) {
        if (count % 2 !== 0) {
            oddCount++;
        }
    }

    return oddCount <= 1;
}


// ============================================================
// 13. LONGEST PALINDROMIC SUBSEQUENCE
// ============================================================

function longestPalindromicSubsequenceLength(text) {
    const n = text.length;

    if (n === 0) {
        return 0;
    }

    const dp = Array.from(
        { length: n },
        () => Array(n).fill(0)
    );

    for (let index = 0; index < n; index++) {
        dp[index][index] = 1;
    }

    for (let length = 2; length <= n; length++) {
        for (let left = 0; left + length <= n; left++) {
            const right = left + length - 1;

            if (text[left] === text[right]) {
                dp[left][right] =
                    length === 2
                        ? 2
                        : dp[left + 1][right - 1] + 2;
            } else {
                dp[left][right] = Math.max(
                    dp[left + 1][right],
                    dp[left][right - 1]
                );
            }
        }
    }

    return dp[0][n - 1];
}


// ============================================================
// 14. PALINDROME PARTITIONING
// ============================================================

function palindromePartitioning(text) {
    const result = [];
    const current = [];

    function backtrack(start) {
        if (start === text.length) {
            result.push([...current]);
            return;
        }

        for (
            let end = start + 1;
            end <= text.length;
            end++
        ) {
            const candidate = text.slice(start, end);

            if (isCharacterPalindrome(candidate)) {
                current.push(candidate);
                backtrack(end);
                current.pop();
            }
        }
    }

    backtrack(0);
    return result;
}


// ============================================================
// 15. ASYNCHRONOUS BATCH ANALYSIS
// ============================================================

function analyzePalindromesAsync(texts) {
    /*
     * Promise.resolve() creates an asynchronous boundary without requiring
     * an external service. In a real application, each item could instead
     * come from a database, HTTP request, worker, or file operation.
     */
    return Promise.resolve(
        texts.map((text) => ({
            text,
            palindrome: isTwoPointerPalindrome(text),
            validPalindrome: isValidPalindrome(text),
            longest: longestPalindromicSubstringCenter(text)
        }))
    );
}


// ============================================================
// 16. VALIDATION
// ============================================================

function assertEqual(actual, expected, description) {
    if (actual !== expected) {
        throw new Error(
            `${description}: expected ${JSON.stringify(expected)}, ` +
            `got ${JSON.stringify(actual)}`
        );
    }
}


function runTests() {
    const tests = [
        [
            isCharacterPalindrome("racecar"),
            true,
            "racecar"
        ],
        [
            isCharacterPalindrome("hello"),
            false,
            "hello"
        ],
        [
            isTwoPointerPalindrome("abba"),
            true,
            "two-pointer abba"
        ],
        [
            isValidPalindrome(
                "A man, a plan, a canal: Panama"
            ),
            true,
            "valid palindrome"
        ],
        [
            isValidPalindrome("race a car"),
            false,
            "invalid palindrome"
        ],
        [
            isNumberPalindromeMath(121),
            true,
            "number 121"
        ],
        [
            isNumberPalindromeMath(123),
            false,
            "number 123"
        ],
        [
            isNumberPalindromeMath(-121),
            false,
            "negative number"
        ],
        [
            canBePalindromeAfterRemovingOne("abca"),
            true,
            "remove one"
        ],
        [
            canBePalindromeAfterRemovingOne("abc"),
            false,
            "cannot remove one"
        ],
        [
            longestPalindromicSubstringCenter("cbbd"),
            "bb",
            "center cbbd"
        ],
        [
            longestPalindromicSubstringDP("cbbd"),
            "bb",
            "DP cbbd"
        ],
        [
            longestPalindromicSubstringManacher("cbbd"),
            "bb",
            "Manacher cbbd"
        ],
        [
            canRearrangeIntoPalindrome("carrace"),
            true,
            "palindrome permutation"
        ],
        [
            canRearrangeIntoPalindrome("daily"),
            false,
            "non-palindrome permutation"
        ],
        [
            longestPalindromicSubsequenceLength("bbbab"),
            4,
            "LPS length"
        ]
    ];

    for (const [actual, expected, description] of tests) {
        assertEqual(actual, expected, description);
    }

    console.log(
        `All ${tests.length} JavaScript tests passed.`
    );
}


// ============================================================
// 17. EDGE CASES
// ============================================================

function demonstrateEdgeCases() {
    const examples = [
        "",
        "a",
        "aa",
        "ab",
        "abba",
        "abcba",
        "A",
        "Aa",
        "😊",
        "😊a😊"
    ];

    console.log("\nEdge cases:");

    for (const value of examples) {
        console.log({
            value,
            exact: isCharacterPalindrome(value),
            twoPointer: isTwoPointerPalindrome(value),
            valid: isValidPalindrome(value)
        });
    }
}


// ============================================================
// 18. PERFORMANCE DEMONSTRATION
// ============================================================

function benchmark() {
    const text =
        "abacabadabacaba".repeat(8);

    const algorithms = [
        [
            "center expansion",
            longestPalindromicSubstringCenter
        ],
        [
            "dynamic programming",
            longestPalindromicSubstringDP
        ],
        [
            "Manacher",
            longestPalindromicSubstringManacher
        ]
    ];

    console.log("\nPerformance comparison:");
    console.log(`Input length: ${text.length}`);

    for (const [name, algorithm] of algorithms) {
        const start = performance.now();
        const result = algorithm(text);
        const elapsed = performance.now() - start;

        console.log(
            `${name.padEnd(22)} ` +
            `${elapsed.toFixed(4).padStart(10)} ms ` +
            `length=${result.length}`
        );
    }
}


// ============================================================
// 19. APPLICATION-STYLE ANALYSIS
// ============================================================

function analyzeText(text, maximumLength = 1_000_000) {
    if (typeof text !== "string") {
        throw new TypeError("text must be a string");
    }

    if (text.length > maximumLength) {
        throw new RangeError(
            `text exceeds ${maximumLength} characters`
        );
    }

    return {
        length: [...text].length,
        exactPalindrome: isTwoPointerPalindrome(text),
        validPalindrome: isValidPalindrome(text),
        canRemoveOne: canBePalindromeAfterRemovingOne(text),
        longestPalindromicSubstring:
            longestPalindromicSubstringCenter(text)
    };
}


// ============================================================
// 20. MAIN EXECUTION
// ============================================================

async function main() {
    console.log("=".repeat(72));
    console.log("DAY 22 — PALINDROMES");
    console.log("=".repeat(72));

    console.log("\nBasic palindrome:");
    for (const text of ["racecar", "hello", "level", "abba"]) {
        console.log(
            `${JSON.stringify(text)} -> ` +
            isCharacterPalindromeLoop(text)
        );
    }

    console.log("\nValid palindrome:");
    for (const text of [
        "A man, a plan, a canal: Panama",
        "race a car",
        "No 'x' in Nixon"
    ]) {
        console.log(
            `${JSON.stringify(text)} -> ` +
            isValidPalindrome(text)
        );
    }

    console.log("\nNumber palindrome:");
    for (const number of [
        0,
        11,
        121,
        123,
        1221,
        -121,
        10
    ]) {
        console.log(
            `${number} -> ${isNumberPalindromeMath(number)}`
        );
    }

    console.log("\nRemove-one-character palindrome:");
    for (const text of ["abca", "abc", "deeee"]) {
        console.log(
            `${JSON.stringify(text)} -> ` +
            canBePalindromeAfterRemovingOne(text)
        );
    }

    console.log("\nLongest palindromic substrings:");

    for (const text of [
        "babad",
        "cbbd",
        "forgeeksskeegfor"
    ]) {
        console.log({
            text,
            center: longestPalindromicSubstringCenter(text),
            dynamicProgramming:
                longestPalindromicSubstringDP(text),
            manacher:
                longestPalindromicSubstringManacher(text)
        });
    }

    console.log("\nAll palindromic substrings of 'abba':");
    console.log(allPalindromicSubstrings("abba"));

    console.log("\nDistinct palindromic substrings of 'aaa':");
    console.log(
        [...distinctPalindromicSubstrings("aaa")]
    );

    console.log("\nPalindrome partitioning of 'aab':");
    console.log(palindromePartitioning("aab"));

    console.log("\nLongest palindromic subsequence:");
    console.log(
        `"bbbab" -> ${longestPalindromicSubsequenceLength("bbbab")}`
    );

    console.log("\nApplication-style analysis:");
    console.log(
        analyzeText("A man, a plan, a canal: Panama")
    );

    demonstrateEdgeCases();
    runTests();
    benchmark();

    console.log("\nAsynchronous batch analysis:");

    const results = await analyzePalindromesAsync([
        "racecar",
        "hello",
        "A man, a plan, a canal: Panama",
        "civic"
    ]);

    console.log(results);
}


if (require.main === module) {
    main().catch((error) => {
        console.error("Application error:", error.message);
        process.exitCode = 1;
    });
}
