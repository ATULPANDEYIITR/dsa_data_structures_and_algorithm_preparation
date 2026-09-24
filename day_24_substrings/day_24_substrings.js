/*
 * Day 24 — Substrings
 *
 * This file demonstrates substring generation, contiguous versus
 * non-contiguous sequences, substring counting, string searching,
 * sliding-window techniques, hashing, and advanced substring problems.
 *
 * Run:
 *     node day24_substrings.js
 */

"use strict";

// ============================================================================
// 1. BASIC SUBSTRING GENERATION
// ============================================================================

function allSubstrings(text, unique = false) {
    const result = [];

    for (let start = 0; start < text.length; start++) {
        for (let end = start + 1; end <= text.length; end++) {
            result.push(text.slice(start, end));
        }
    }

    return unique ? [...new Set(result)] : result;
}

function allSubstringsWithPositions(text) {
    const result = [];

    for (let start = 0; start < text.length; start++) {
        for (let end = start + 1; end <= text.length; end++) {
            result.push({
                start,
                end,
                substring: text.slice(start, end)
            });
        }
    }

    return result;
}

function countAllSubstrings(text) {
    const n = text.length;
    return (n * (n + 1)) / 2;
}

function countSubstringsOfLength(text, length) {
    if (length < 1 || length > text.length) {
        return 0;
    }

    return text.length - length + 1;
}

// ============================================================================
// 2. SUBSTRING VERSUS SUBSEQUENCE
// ============================================================================

function isSubstring(text, candidate) {
    return text.includes(candidate);
}

function isSubsequence(text, candidate) {
    let candidateIndex = 0;

    for (const character of text) {
        if (
            candidateIndex < candidate.length &&
            character === candidate[candidateIndex]
        ) {
            candidateIndex++;
        }
    }

    return candidateIndex === candidate.length;
}

// ============================================================================
// 3. BRUTE-FORCE SEARCH
// ============================================================================

function bruteForceSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    if (pattern.length > text.length) {
        return -1;
    }

    for (let start = 0; start <= text.length - pattern.length; start++) {
        let matched = true;

        for (let offset = 0; offset < pattern.length; offset++) {
            if (text[start + offset] !== pattern[offset]) {
                matched = false;
                break;
            }
        }

        if (matched) {
            return start;
        }
    }

    return -1;
}

function bruteForceSearchAll(text, pattern) {
    if (pattern.length === 0) {
        return Array.from({ length: text.length + 1 }, (_, index) => index);
    }

    const positions = [];

    for (let start = 0; start <= text.length - pattern.length; start++) {
        if (text.slice(start, start + pattern.length) === pattern) {
            positions.push(start);
        }
    }

    return positions;
}

// ============================================================================
// 4. KMP PREFIX FUNCTION
// ============================================================================

function prefixFunction(pattern) {
    const lps = new Array(pattern.length).fill(0);

    let length = 0;
    let index = 1;

    while (index < pattern.length) {
        if (pattern[index] === pattern[length]) {
            length++;
            lps[index] = length;
            index++;
        } else if (length > 0) {
            length = lps[length - 1];
        } else {
            lps[index] = 0;
            index++;
        }
    }

    return lps;
}

function kmpSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    const lps = prefixFunction(pattern);

    let textIndex = 0;
    let patternIndex = 0;

    while (textIndex < text.length) {
        if (text[textIndex] === pattern[patternIndex]) {
            textIndex++;
            patternIndex++;

            if (patternIndex === pattern.length) {
                return textIndex - patternIndex;
            }
        } else if (patternIndex > 0) {
            patternIndex = lps[patternIndex - 1];
        } else {
            textIndex++;
        }
    }

    return -1;
}

function kmpSearchAll(text, pattern) {
    if (pattern.length === 0) {
        return Array.from({ length: text.length + 1 }, (_, index) => index);
    }

    const lps = prefixFunction(pattern);
    const positions = [];

    let textIndex = 0;
    let patternIndex = 0;

    while (textIndex < text.length) {
        if (text[textIndex] === pattern[patternIndex]) {
            textIndex++;
            patternIndex++;

            if (patternIndex === pattern.length) {
                positions.push(textIndex - patternIndex);
                patternIndex = lps[patternIndex - 1];
            }
        } else if (patternIndex > 0) {
            patternIndex = lps[patternIndex - 1];
        } else {
            textIndex++;
        }
    }

    return positions;
}

// ============================================================================
// 5. RABIN-KARP
// ============================================================================

function rabinKarpSearch(
    text,
    pattern,
    base = 256,
    modulus = 1000000007
) {
    if (pattern.length === 0) {
        return 0;
    }

    if (pattern.length > text.length) {
        return -1;
    }

    const patternLength = pattern.length;
    let patternHash = 0;
    let windowHash = 0;
    let highestPower = 1;

    for (let index = 0; index < patternLength - 1; index++) {
        highestPower = (highestPower * base) % modulus;
    }

    for (let index = 0; index < patternLength; index++) {
        patternHash =
            (patternHash * base + pattern.charCodeAt(index)) % modulus;

        windowHash =
            (windowHash * base + text.charCodeAt(index)) % modulus;
    }

    for (
        let start = 0;
        start <= text.length - patternLength;
        start++
    ) {
        if (patternHash === windowHash) {
            if (
                text.slice(start, start + patternLength) ===
                pattern
            ) {
                return start;
            }
        }

        if (start < text.length - patternLength) {
            const outgoing =
                text.charCodeAt(start) * highestPower;

            windowHash =
                ((windowHash - outgoing) * base +
                    text.charCodeAt(start + patternLength)) %
                modulus;

            if (windowHash < 0) {
                windowHash += modulus;
            }
        }
    }

    return -1;
}

// ============================================================================
// 6. Z ALGORITHM
// ============================================================================

function zFunction(text) {
    const z = new Array(text.length).fill(0);

    if (text.length === 0) {
        return z;
    }

    z[0] = text.length;

    let left = 0;
    let right = 0;

    for (let index = 1; index < text.length; index++) {
        if (index <= right) {
            z[index] = Math.min(
                right - index + 1,
                z[index - left]
            );
        }

        while (
            index + z[index] < text.length &&
            text[z[index]] === text[index + z[index]]
        ) {
            z[index]++;
        }

        if (index + z[index] - 1 > right) {
            left = index;
            right = index + z[index] - 1;
        }
    }

    return z;
}

function zSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    const separator = "\u0000";
    const combined = pattern + separator + text;
    const z = zFunction(combined);

    for (
        let index = pattern.length + 1;
        index < combined.length;
        index++
    ) {
        if (z[index] >= pattern.length) {
            return index - pattern.length - 1;
        }
    }

    return -1;
}

// ============================================================================
// 7. OVERLAPPING AND NON-OVERLAPPING COUNTS
// ============================================================================

function countOverlappingOccurrences(text, pattern) {
    if (pattern.length === 0) {
        throw new Error("Pattern must not be empty.");
    }

    let count = 0;

    for (let start = 0; start <= text.length - pattern.length; start++) {
        if (text.startsWith(pattern, start)) {
            count++;
        }
    }

    return count;
}

function countNonOverlappingOccurrences(text, pattern) {
    if (pattern.length === 0) {
        throw new Error("Pattern must not be empty.");
    }

    let count = 0;
    let position = 0;

    while (position <= text.length - pattern.length) {
        if (text.startsWith(pattern, position)) {
            count++;
            position += pattern.length;
        } else {
            position++;
        }
    }

    return count;
}

// ============================================================================
// 8. SLIDING WINDOW: LONGEST UNIQUE SUBSTRING
// ============================================================================

function longestUniqueSubstring(text) {
    const lastSeen = new Map();

    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        if (
            lastSeen.has(character) &&
            lastSeen.get(character) >= left
        ) {
            left = lastSeen.get(character) + 1;
        }

        lastSeen.set(character, right);

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return text.slice(bestStart, bestStart + bestLength);
}

// ============================================================================
// 9. AT MOST K DISTINCT AND EXACTLY K DISTINCT
// ============================================================================

function countAtMostKDistinct(text, k) {
    if (k < 0) {
        return 0;
    }

    const frequency = new Map();

    let left = 0;
    let total = 0;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];
        frequency.set(
            character,
            (frequency.get(character) || 0) + 1
        );

        while (frequency.size > k) {
            const outgoing = text[left];
            const newCount = frequency.get(outgoing) - 1;

            if (newCount === 0) {
                frequency.delete(outgoing);
            } else {
                frequency.set(outgoing, newCount);
            }

            left++;
        }

        total += right - left + 1;
    }

    return total;
}

function countExactlyKDistinct(text, k) {
    if (k <= 0) {
        return 0;
    }

    return (
        countAtMostKDistinct(text, k) -
        countAtMostKDistinct(text, k - 1)
    );
}

// ============================================================================
// 10. MINIMUM WINDOW SUBSTRING
// ============================================================================

function minimumWindowSubstring(text, target) {
    if (!text || !target || target.length > text.length) {
        return "";
    }

    const required = new Map();

    for (const character of target) {
        required.set(
            character,
            (required.get(character) || 0) + 1
        );
    }

    let remaining = target.length;
    let left = 0;
    let bestStart = 0;
    let bestLength = Infinity;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        if (required.has(character)) {
            const count = required.get(character);

            if (count > 0) {
                remaining--;
            }

            required.set(character, count - 1);
        }

        while (remaining === 0) {
            const currentLength = right - left + 1;

            if (currentLength < bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }

            const outgoing = text[left];

            if (required.has(outgoing)) {
                const count = required.get(outgoing) + 1;
                required.set(outgoing, count);

                if (count > 0) {
                    remaining++;
                }
            }

            left++;
        }
    }

    return bestLength === Infinity
        ? ""
        : text.slice(bestStart, bestStart + bestLength);
}

// ============================================================================
// 11. LONGEST PALINDROMIC SUBSTRING
// ============================================================================

function longestPalindromicSubstring(text) {
    if (text.length < 2) {
        return text;
    }

    let bestStart = 0;
    let bestLength = 1;

    function expand(left, right) {
        while (
            left >= 0 &&
            right < text.length &&
            text[left] === text[right]
        ) {
            left--;
            right++;
        }

        return {
            start: left + 1,
            length: right - left - 1
        };
    }

    for (let center = 0; center < text.length; center++) {
        const odd = expand(center, center);

        if (odd.length > bestLength) {
            bestStart = odd.start;
            bestLength = odd.length;
        }

        const even = expand(center, center + 1);

        if (even.length > bestLength) {
            bestStart = even.start;
            bestLength = even.length;
        }
    }

    return text.slice(bestStart, bestStart + bestLength);
}

// ============================================================================
// 12. LONGEST COMMON SUBSTRING
// ============================================================================

function longestCommonSubstring(first, second) {
    if (!first || !second) {
        return "";
    }

    const previous = new Array(second.length + 1).fill(0);
    let bestLength = 0;
    let bestEnd = 0;

    for (let i = 1; i <= first.length; i++) {
        const current = new Array(second.length + 1).fill(0);

        for (let j = 1; j <= second.length; j++) {
            if (first[i - 1] === second[j - 1]) {
                current[j] = previous[j - 1] + 1;

                if (current[j] > bestLength) {
                    bestLength = current[j];
                    bestEnd = i;
                }
            }
        }

        for (let j = 0; j <= second.length; j++) {
            previous[j] = current[j];
        }
    }

    return first.slice(bestEnd - bestLength, bestEnd);
}

// ============================================================================
// 13. PREFIX MATCHING AND PRACTICAL VALIDATION
// ============================================================================

function longestCommonPrefix(values) {
    if (values.length === 0) {
        return "";
    }

    let prefix = values[0];

    for (let index = 1; index < values.length; index++) {
        while (!values[index].startsWith(prefix)) {
            prefix = prefix.slice(0, -1);

            if (prefix === "") {
                return "";
            }
        }
    }

    return prefix;
}

// ============================================================================
// 14. PRACTICAL LOG SEARCH
// ============================================================================

class LogSubstringAnalyzer {
    constructor(lines) {
        this.lines = [...lines];
    }

    findLinesContaining(pattern) {
        if (typeof pattern !== "string" || pattern.length === 0) {
            throw new Error("A non-empty search pattern is required.");
        }

        return this.lines.filter(line => line.includes(pattern));
    }

    countOccurrences(pattern) {
        return this.lines.reduce(
            (total, line) =>
                total + countOverlappingOccurrences(line, pattern),
            0
        );
    }

    searchWithKMP(pattern) {
        return this.lines.map(line => ({
            line,
            index: kmpSearch(line, pattern)
        }));
    }
}

// ============================================================================
// 15. ASSERTIONS
// ============================================================================

function runAssertions() {
    console.assert(
        JSON.stringify(allSubstrings("abc")) ===
        JSON.stringify(["a", "ab", "abc", "b", "bc", "c"])
    );

    console.assert(countAllSubstrings("abcde") === 15);
    console.assert(countSubstringsOfLength("abcde", 3) === 3);

    console.assert(isSubstring("abcdef", "bcd"));
    console.assert(isSubsequence("abcdef", "ace"));
    console.assert(!isSubsequence("abcdef", "aec"));

    console.assert(bruteForceSearch("hello", "ll") === 2);
    console.assert(kmpSearch("ABABDABACDABABCABAB", "ABABCABAB") === 10);
    console.assert(
        JSON.stringify(kmpSearchAll("aaaa", "aa")) ===
        JSON.stringify([0, 1, 2])
    );

    console.assert(rabinKarpSearch("hello world", "world") === 6);
    console.assert(zSearch("hello world", "world") === 6);

    console.assert(countOverlappingOccurrences("aaaa", "aa") === 3);
    console.assert(countNonOverlappingOccurrences("aaaa", "aa") === 2);

    console.assert(longestUniqueSubstring("abcabcbb") === "abc");
    console.assert(countExactlyKDistinct("pqpqs", 2) === 7);

    console.assert(
        minimumWindowSubstring("ADOBECODEBANC", "ABC") === "BANC"
    );

    console.assert(
        longestPalindromicSubstring("babad") === "bab" ||
        longestPalindromicSubstring("babad") === "aba"
    );

    console.assert(
        longestCommonSubstring("ABABC", "BABCA") === "BABC"
    );

    console.assert(
        longestCommonPrefix(["flower", "flow", "flight"]) === "fl"
    );

    console.log("All JavaScript assertions passed.");
}

// ============================================================================
// 16. MAIN DEMONSTRATION
// ============================================================================

function main() {
    console.log("=".repeat(78));
    console.log("DAY 24 — SUBSTRINGS");
    console.log("=".repeat(78));

    const text = "banana";

    console.log("\n1. Substring generation");
    console.log("Text:", text);
    console.log("All:", allSubstrings(text));
    console.log("Distinct:", allSubstrings(text, true));
    console.log(
        "Positions:",
        allSubstringsWithPositions("abc")
    );

    console.log("\n2. Contiguous versus non-contiguous");
    for (const candidate of ["ABC", "ACE", "AEC", "BCD"]) {
        console.log(
            candidate,
            "substring:",
            isSubstring("ABCDE", candidate),
            "subsequence:",
            isSubsequence("ABCDE", candidate)
        );
    }

    console.log("\n3. String searching");
    const searchText = "ABABDABACDABABCABAB";
    const searchPattern = "ABABCABAB";

    console.log(
        "Brute force:",
        bruteForceSearch(searchText, searchPattern)
    );
    console.log(
        "KMP:",
        kmpSearch(searchText, searchPattern)
    );
    console.log(
        "Rabin-Karp:",
        rabinKarpSearch(searchText, searchPattern)
    );
    console.log(
        "Z algorithm:",
        zSearch(searchText, searchPattern)
    );

    console.log("\n4. KMP prefix table");
    console.log(prefixFunction(searchPattern));

    console.log("\n5. Sliding window");
    console.log(
        "Longest unique:",
        longestUniqueSubstring("abcabcbb")
    );
    console.log(
        "Exactly two distinct:",
        countExactlyKDistinct("pqpqs", 2)
    );

    console.log("\n6. Advanced substring problems");
    console.log(
        "Minimum window:",
        minimumWindowSubstring("ADOBECODEBANC", "ABC")
    );
    console.log(
        "Longest palindrome:",
        longestPalindromicSubstring("forgeeksskeegfor")
    );
    console.log(
        "Longest common substring:",
        longestCommonSubstring("ABABC", "BABCA")
    );

    console.log("\n7. Practical log analysis");
    const analyzer = new LogSubstringAnalyzer([
        "INFO user login successful",
        "ERROR database connection failed",
        "INFO request completed",
        "ERROR timeout while connecting to database"
    ]);

    console.log(
        "Lines containing ERROR:",
        analyzer.findLinesContaining("ERROR")
    );

    console.log(
        "Total database occurrences:",
        analyzer.countOccurrences("database")
    );

    console.log(
        "KMP line search:",
        analyzer.searchWithKMP("connection")
    );

    console.log("\n8. Complexity observations");
    console.log("Brute-force search: worst-case O(nm)");
    console.log("KMP: O(n + m)");
    console.log("Rabin-Karp: average O(n + m), collision-dependent worst case");
    console.log("Z search: O(n + m)");
    console.log("Sliding-window unique substring: O(n)");
    console.log("Longest common substring DP: O(nm)");

    runAssertions();
}

main();
