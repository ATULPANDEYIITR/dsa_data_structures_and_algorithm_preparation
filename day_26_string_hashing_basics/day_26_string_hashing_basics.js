/*
 * Day 26 — String Hashing Basics
 *
 * Self-contained JavaScript study file.
 *
 * Demonstrates:
 * - Basic hash representations
 * - Polynomial rolling hashes
 * - Prefix hashes
 * - O(1) substring hash queries
 * - Collision handling
 * - Double hashing
 * - Rabin-Karp search
 * - Duplicate substring detection
 * - Longest repeated substring
 * - Hash-table use cases
 * - Normalization
 * - Edge cases
 * - Performance and security considerations
 *
 * Run with:
 *   node day26_string_hashing.js
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. BASIC CHARACTER HASH
// -----------------------------------------------------------------------------

function characterSumHash(text) {
    /*
     * This intentionally weak hash demonstrates the central idea:
     * transform a string into a numeric representation.
     *
     * Because addition ignores character order:
     *   "abc" and "acb" collide.
     */
    let hash = 0;

    for (const character of text) {
        hash += character.codePointAt(0);
    }

    return hash;
}

function demonstrateBasicHashing() {
    console.log("\n=== 1. BASIC HASHING ===");

    for (const text of ["abc", "acb", "hello", "world", ""]) {
        console.log(JSON.stringify(text), "->", characterSumHash(text));
    }

    console.log(
        "Collision:",
        characterSumHash("abc") === characterSumHash("acb")
    );
}


// -----------------------------------------------------------------------------
// 2. SAFE MODULAR ARITHMETIC
// -----------------------------------------------------------------------------

/*
 * JavaScript Number uses IEEE-754 floating-point arithmetic.
 *
 * Ordinary Number arithmetic cannot exactly represent every integer above
 * Number.MAX_SAFE_INTEGER.
 *
 * For educational rolling hashes, BigInt gives exact integer arithmetic.
 */
function mod(value, modulus) {
    const result = value % modulus;
    return result >= 0n ? result : result + modulus;
}

function polynomialHash(text, base = 257n, modulus = 1000000007n) {
    if (base <= 0n) {
        throw new RangeError("base must be positive");
    }

    if (modulus <= 1n) {
        throw new RangeError("modulus must be greater than 1");
    }

    let hash = 0n;

    for (const character of text) {
        hash = mod(
            hash * base + BigInt(character.codePointAt(0)),
            modulus
        );
    }

    return hash;
}

function demonstratePolynomialHash() {
    console.log("\n=== 2. POLYNOMIAL HASH ===");

    for (const text of ["", "a", "abc", "hello", "Hello", "hello!"]) {
        console.log(
            JSON.stringify(text),
            "->",
            polynomialHash(text).toString()
        );
    }
}


// -----------------------------------------------------------------------------
// 3. ROLLING HASH
// -----------------------------------------------------------------------------

class RollingHash {
    /*
     * Prefix representation:
     *
     * prefix[i] = hash of text[0:i]
     *
     * power[i] = base^i mod modulus
     *
     * For substring [left, right):
     *
     *   prefix[right] - prefix[left] * base^(right-left)
     *
     * gives the substring hash modulo the modulus.
     */
    constructor(
        text,
        base = 911382323n,
        modulus = 972663749n
    ) {
        if (modulus <= 1n) {
            throw new RangeError("modulus must be greater than 1");
        }

        if (base <= 0n || base >= modulus) {
            throw new RangeError(
                "base must be positive and smaller than modulus"
            );
        }

        this.text = text;
        this.base = base;
        this.modulus = modulus;

        // Array.from works with Unicode code points rather than UTF-16 units.
        this.characters = Array.from(text);

        this.prefix = Array(this.characters.length + 1).fill(0n);
        this.power = Array(this.characters.length + 1).fill(1n);

        for (let i = 0; i < this.characters.length; i++) {
            const code = BigInt(this.characters[i].codePointAt(0));

            this.prefix[i + 1] = mod(
                this.prefix[i] * this.base + code,
                this.modulus
            );

            this.power[i + 1] = mod(
                this.power[i] * this.base,
                this.modulus
            );
        }
    }

    substringHash(left, right) {
        if (
            left < 0 ||
            right < left ||
            right > this.characters.length
        ) {
            throw new RangeError("invalid substring bounds");
        }

        return mod(
            this.prefix[right] -
            this.prefix[left] * this.power[right - left],
            this.modulus
        );
    }

    substring(left, right) {
        return this.characters.slice(left, right).join("");
    }

    equalSubstrings(
        firstLeft,
        firstRight,
        secondLeft,
        secondRight,
        verify = true
    ) {
        if (
            firstRight - firstLeft !==
            secondRight - secondLeft
        ) {
            return false;
        }

        if (
            this.substringHash(firstLeft, firstRight) !==
            this.substringHash(secondLeft, secondRight)
        ) {
            return false;
        }

        /*
         * A hash match is only a candidate match.
         * Verification removes collision-induced false positives.
         */
        if (verify) {
            return (
                this.substring(firstLeft, firstRight) ===
                this.substring(secondLeft, secondRight)
            );
        }

        return true;
    }
}

function demonstratePrefixHashing() {
    console.log("\n=== 3. PREFIX HASHING ===");

    const text = "abracadabra";
    const hasher = new RollingHash(text);

    console.log("Text:", text);
    console.log(
        "Hash of 'abra':",
        hasher.substringHash(0, 4).toString()
    );

    console.log(
        "Hash of second 'abra':",
        hasher.substringHash(7, 11).toString()
    );

    console.log(
        "Verified equality:",
        hasher.equalSubstrings(0, 4, 7, 11)
    );
}


// -----------------------------------------------------------------------------
// 4. DOUBLE HASH
// -----------------------------------------------------------------------------

class DoubleRollingHash {
    constructor(text) {
        this.text = text;
        this.first = new RollingHash(
            text,
            911382323n,
            972663749n
        );

        this.second = new RollingHash(
            text,
            97266353n,
            1000000007n
        );
    }

    substringHash(left, right) {
        return [
            this.first.substringHash(left, right),
            this.second.substringHash(left, right)
        ];
    }

    equalSubstrings(
        firstLeft,
        firstRight,
        secondLeft,
        secondRight,
        verify = true
    ) {
        if (
            firstRight - firstLeft !==
            secondRight - secondLeft
        ) {
            return false;
        }

        const firstHash = this.substringHash(firstLeft, firstRight);
        const secondHash = this.substringHash(secondLeft, secondRight);

        if (
            firstHash[0] !== secondHash[0] ||
            firstHash[1] !== secondHash[1]
        ) {
            return false;
        }

        if (verify) {
            return (
                this.text.slice(firstLeft, firstRight) ===
                this.text.slice(secondLeft, secondRight)
            );
        }

        return true;
    }
}

function demonstrateDoubleHashing() {
    console.log("\n=== 4. DOUBLE HASHING ===");

    const text = "the quick brown fox jumps over the lazy dog";
    const hasher = new DoubleRollingHash(text);

    const hash = hasher.substringHash(4, 9);

    console.log("Substring:", text.slice(4, 9));
    console.log(
        "Hash pair:",
        hash.map(value => value.toString())
    );
}


// -----------------------------------------------------------------------------
// 5. RABIN-KARP
// -----------------------------------------------------------------------------

function rabinKarpSearch(text, pattern) {
    /*
     * Rabin-Karp compares hashes of windows instead of repeatedly comparing
     * all pattern characters.
     *
     * The actual substring is checked after a hash match, so a collision
     * cannot incorrectly become a reported match.
     */
    if (pattern.length === 0) {
        return Array.from({ length: text.length + 1 }, (_, i) => i);
    }

    if (pattern.length > text.length) {
        return [];
    }

    const patternCharacters = Array.from(pattern);
    const textCharacters = Array.from(text);

    if (patternCharacters.length > textCharacters.length) {
        return [];
    }

    const hasher = new RollingHash(text);
    const patternHasher = new RollingHash(pattern);

    const patternHash = patternHasher.substringHash(
        0,
        patternCharacters.length
    );

    const matches = [];

    for (
        let start = 0;
        start + patternCharacters.length <= textCharacters.length;
        start++
    ) {
        const end = start + patternCharacters.length;
        const windowHash = hasher.substringHash(start, end);

        if (windowHash === patternHash) {
            if (
                textCharacters.slice(start, end).join("") ===
                pattern
            ) {
                matches.push(start);
            }
        }
    }

    return matches;
}

function demonstrateRabinKarp() {
    console.log("\n=== 5. RABIN-KARP SEARCH ===");

    const text = "abracadabra";

    for (const pattern of ["abra", "cad", "xyz", "", "a"]) {
        console.log(
            JSON.stringify(pattern),
            "->",
            rabinKarpSearch(text, pattern)
        );
    }
}


// -----------------------------------------------------------------------------
// 6. COLLISION DEMONSTRATION
// -----------------------------------------------------------------------------

function demonstrateCollision() {
    console.log("\n=== 6. COLLISION CONCEPT ===");

    const first = "abc";
    const second = "acb";

    console.log(
        `${first} -> ${characterSumHash(first)}`
    );

    console.log(
        `${second} -> ${characterSumHash(second)}`
    );

    console.log(
        "Different strings with equal hashes:",
        characterSumHash(first) === characterSumHash(second)
    );

    console.log(
        "Lesson: hash equality is not automatically string equality."
    );
}


// -----------------------------------------------------------------------------
// 7. DUPLICATE SUBSTRING DETECTION
// -----------------------------------------------------------------------------

function findDuplicateSubstring(text, length) {
    if (length < 0) {
        throw new RangeError("length cannot be negative");
    }

    const characters = Array.from(text);

    if (length === 0) {
        return [0, 0];
    }

    if (length > characters.length) {
        return null;
    }

    const hasher = new DoubleRollingHash(text);
    const seen = new Map();

    for (
        let start = 0;
        start + length <= characters.length;
        start++
    ) {
        const hash = hasher.substringHash(start, start + length);
        const key = `${hash[0].toString()}:${hash[1].toString()}`;

        if (!seen.has(key)) {
            seen.set(key, []);
        }

        for (const previousStart of seen.get(key)) {
            const previous = characters
                .slice(previousStart, previousStart + length)
                .join("");

            const current = characters
                .slice(start, start + length)
                .join("");

            if (previous === current) {
                return [previousStart, start];
            }
        }

        seen.get(key).push(start);
    }

    return null;
}

function demonstrateDuplicateSubstring() {
    console.log("\n=== 7. DUPLICATE SUBSTRINGS ===");

    const text = "banana";

    for (let length = 1; length <= text.length; length++) {
        const result = findDuplicateSubstring(text, length);

        if (result) {
            const [first, second] = result;
            console.log(
                `Length ${length}: '${text.slice(first, first + length)}' ` +
                `at ${first} and ${second}`
            );
        } else {
            console.log(`Length ${length}: no duplicate`);
        }
    }
}


// -----------------------------------------------------------------------------
// 8. LONGEST REPEATED SUBSTRING
// -----------------------------------------------------------------------------

function longestRepeatedSubstring(text) {
    const characters = Array.from(text);

    if (characters.length === 0) {
        return "";
    }

    const hasher = new DoubleRollingHash(text);

    function duplicateForLength(length) {
        const seen = new Map();

        for (
            let start = 0;
            start + length <= characters.length;
            start++
        ) {
            const hash = hasher.substringHash(start, start + length);
            const key = `${hash[0].toString()}:${hash[1].toString()}`;

            if (!seen.has(key)) {
                seen.set(key, []);
            }

            for (const previousStart of seen.get(key)) {
                const previous = characters
                    .slice(previousStart, previousStart + length)
                    .join("");

                const current = characters
                    .slice(start, start + length)
                    .join("");

                if (previous === current) {
                    return previous;
                }
            }

            seen.get(key).push(start);
        }

        return null;
    }

    let low = 1;
    let high = characters.length;
    let best = "";

    while (low <= high) {
        const middle = Math.floor((low + high) / 2);
        const duplicate = duplicateForLength(middle);

        if (duplicate !== null) {
            best = duplicate;
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }

    return best;
}

function demonstrateLongestRepeatedSubstring() {
    console.log("\n=== 8. LONGEST REPEATED SUBSTRING ===");

    for (const text of [
        "banana",
        "abracadabra",
        "aaaaa",
        "abcdef",
        "mississippi"
    ]) {
        console.log(
            JSON.stringify(text),
            "->",
            JSON.stringify(longestRepeatedSubstring(text))
        );
    }
}


// -----------------------------------------------------------------------------
// 9. HASH-TABLE USE CASE
// -----------------------------------------------------------------------------

function wordFrequency(sentence) {
    /*
     * JavaScript Map is the practical abstraction for frequency counting.
     * The runtime handles hashing and collision management internally.
     */
    const counts = new Map();

    const words = sentence
        .toLocaleLowerCase()
        .split(/\s+/)
        .map(word => word.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ""))
        .filter(Boolean);

    for (const word of words) {
        counts.set(word, (counts.get(word) ?? 0) + 1);
    }

    return counts;
}

function demonstrateHashTable() {
    console.log("\n=== 9. HASH TABLE APPLICATION ===");

    const sentence =
        "hashing makes lookup fast and hashing supports lookup";

    const frequencies = wordFrequency(sentence);

    for (const [word, count] of frequencies) {
        console.log(`${word}: ${count}`);
    }
}


// -----------------------------------------------------------------------------
// 10. NORMALIZATION
// -----------------------------------------------------------------------------

function normalizedHash(text) {
    /*
     * casefold-like normalization is not directly available as a universal
     * JavaScript String method. toLocaleLowerCase is used here for a simple
     * case-insensitive demonstration.
     */
    return polynomialHash(text.toLocaleLowerCase());
}

function demonstrateNormalization() {
    console.log("\n=== 10. NORMALIZATION ===");

    for (const text of ["Apple", "apple", "APPLE", "ApPlE"]) {
        console.log(
            text,
            "->",
            normalizedHash(text).toString()
        );
    }
}


// -----------------------------------------------------------------------------
// 11. ASSESSMENT: LONGEST COMMON SUBSTRING
// -----------------------------------------------------------------------------

function longestCommonSubstring(first, second) {
    /*
     * This uses dynamic programming rather than hashing.
     *
     * If first[i - 1] === second[j - 1], then the longest common substring
     * ending at these positions is one longer than the diagonal state.
     *
     * Time: O(n*m)
     * Space: O(m)
     */
    const firstCharacters = Array.from(first);
    const secondCharacters = Array.from(second);

    let previous = new Array(secondCharacters.length + 1).fill(0);
    let bestLength = 0;
    let bestEnd = 0;

    for (let i = 1; i <= firstCharacters.length; i++) {
        const current = new Array(secondCharacters.length + 1).fill(0);

        for (let j = 1; j <= secondCharacters.length; j++) {
            if (firstCharacters[i - 1] === secondCharacters[j - 1]) {
                current[j] = previous[j - 1] + 1;

                if (current[j] > bestLength) {
                    bestLength = current[j];
                    bestEnd = i;
                }
            }
        }

        previous = current;
    }

    return firstCharacters
        .slice(bestEnd - bestLength, bestEnd)
        .join("");
}


// -----------------------------------------------------------------------------
// 12. ASSESSMENT: DISTINCT SUBSTRINGS
// -----------------------------------------------------------------------------

function countDistinctSubstrings(text) {
    /*
     * This is a deliberately clear baseline implementation.
     *
     * It stores actual substring values in a Set.
     * Advanced data structures can solve this more efficiently.
     */
    const characters = Array.from(text);
    const distinct = new Set();

    for (let left = 0; left < characters.length; left++) {
        for (let right = left + 1; right <= characters.length; right++) {
            distinct.add(characters.slice(left, right).join(""));
        }
    }

    return distinct.size;
}

function runAssessment() {
    console.log("\n=== 11. MIXED ASSESSMENT ===");

    for (const text of ["ababa", "aaa", "abc", ""]) {
        console.log(
            `Distinct substrings of '${text}':`,
            countDistinctSubstrings(text)
        );
    }

    for (const [first, second] of [
        ["abcdef", "zcdemf"],
        ["abc", "xyz"],
        ["banana", "ananas"]
    ]) {
        console.log(
            `Longest common substring of '${first}' and '${second}':`,
            longestCommonSubstring(first, second)
        );
    }
}


// -----------------------------------------------------------------------------
// 13. ERROR HANDLING AND EDGE CASES
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    console.log("\n=== 12. EDGE CASES ===");

    const emptyHasher = new RollingHash("");

    console.log(
        "Empty-string hash:",
        emptyHasher.substringHash(0, 0).toString()
    );

    console.log(
        "Pattern longer than text:",
        rabinKarpSearch("abc", "abcdef")
    );

    console.log(
        "Empty pattern:",
        rabinKarpSearch("abc", "")
    );

    try {
        new RollingHash("abc").substringHash(-1, 2);
    } catch (error) {
        console.log(
            "Invalid bounds handled:",
            error instanceof Error ? error.message : String(error)
        );
    }
}


// -----------------------------------------------------------------------------
// 14. SECURITY NOTES
// -----------------------------------------------------------------------------

function demonstrateSecurityDistinction() {
    console.log("\n=== 13. SECURITY DISTINCTION ===");

    console.log(`
Algorithmic string hashing is designed primarily for speed.

Polynomial rolling hashes are useful for:
  - substring comparison
  - pattern searching
  - duplicate detection
  - string algorithms

They are not cryptographic password hashes.

Security-sensitive integrity or authentication systems require
cryptographic primitives designed for those purposes. Password storage
requires a password hashing/KDF design rather than a fast rolling hash.

A deterministic algorithmic hash should never be interpreted as proof that
two strings are equal unless collision handling and verification are part of
the design.
`);
}


// -----------------------------------------------------------------------------
// 15. TESTS
// -----------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    assert(
        polynomialHash("") === 0n,
        "empty polynomial hash should be zero"
    );

    assert(
        characterSumHash("abc") === characterSumHash("acb"),
        "character sum should demonstrate a collision"
    );

    const rolling = new RollingHash("abcdef");

    assert(
        rolling.substringHash(0, 3) ===
        polynomialHash(
            "abc",
            rolling.base,
            rolling.modulus
        ),
        "prefix substring hash"
    );

    assert(
        rolling.substringHash(2, 5) ===
        polynomialHash(
            "cde",
            rolling.base,
            rolling.modulus
        ),
        "middle substring hash"
    );

    assert(
        JSON.stringify(rabinKarpSearch("aaaaa", "aaa")) ===
        JSON.stringify([0, 1, 2]),
        "Rabin-Karp overlapping matches"
    );

    assert(
        JSON.stringify(rabinKarpSearch("abcdef", "xyz")) ===
        JSON.stringify([]),
        "Rabin-Karp missing pattern"
    );

    assert(
        longestRepeatedSubstring("aaaa") === "aaa",
        "longest repeated substring"
    );

    assert(
        longestCommonSubstring("abcdef", "zcdemf") === "cde",
        "longest common substring"
    );

    assert(
        countDistinctSubstrings("aaa") === 3,
        "distinct substring count"
    );

    console.log("\nAll JavaScript self-tests passed.");
}


// -----------------------------------------------------------------------------
// MAIN
// -----------------------------------------------------------------------------

function main() {
    demonstrateBasicHashing();
    demonstratePolynomialHash();
    demonstratePrefixHashing();
    demonstrateDoubleHashing();
    demonstrateRabinKarp();
    demonstrateCollision();
    demonstrateDuplicateSubstring();
    demonstrateLongestRepeatedSubstring();
    demonstrateHashTable();
    demonstrateNormalization();
    runAssessment();
    demonstrateEdgeCases();
    demonstrateSecurityDistinction();
    runTests();
}

main();
