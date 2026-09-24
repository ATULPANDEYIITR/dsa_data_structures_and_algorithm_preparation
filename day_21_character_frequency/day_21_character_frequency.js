/*
 * Day 21 — Character Frequency
 * =============================
 *
 * Topics:
 * - Character counting
 * - Frequency objects and Map
 * - Frequency arrays
 * - Most frequent characters
 * - Duplicate and unique characters
 * - Frequency comparison
 * - Character grouping
 * - Unicode considerations
 * - Sliding-window algorithms
 * - Validation and testing
 *
 * This file uses standard JavaScript and can run in Node.js or a browser
 * console without external packages.
 */

// ============================================================================
// 1. BASIC CHARACTER COUNTING
// ============================================================================

function countCharactersObject(text) {
    /*
     * Object keys provide a simple frequency table.
     * Object.create(null) avoids inherited property names such as
     * "constructor" interfering with character keys.
     */
    validateText(text);

    const frequency = Object.create(null);

    for (const character of text) {
        frequency[character] = (frequency[character] || 0) + 1;
    }

    return frequency;
}


function countCharactersMap(text) {
    /*
     * Map is useful when keys can be arbitrary values or when explicit
     * Map operations are preferred over object properties.
     */
    validateText(text);

    const frequency = new Map();

    for (const character of text) {
        frequency.set(character, (frequency.get(character) || 0) + 1);
    }

    return frequency;
}


// ============================================================================
// 2. FREQUENCY ARRAY
// ============================================================================

function lowercaseFrequencyArray(text) {
    /*
     * For exactly 26 lowercase English letters, an array avoids hashing.
     *
     * 'a' -> 0
     * 'b' -> 1
     * ...
     * 'z' -> 25
     */
    validateText(text);

    const frequency = new Array(26).fill(0);

    for (const character of text) {
        if (character >= "a" && character <= "z") {
            const index = character.charCodeAt(0) - 97;
            frequency[index]++;
        }
    }

    return frequency;
}


function frequencyArrayToObject(frequency) {
    const result = Object.create(null);

    for (let index = 0; index < frequency.length; index++) {
        if (frequency[index] > 0) {
            result[String.fromCharCode(97 + index)] = frequency[index];
        }
    }

    return result;
}


// ============================================================================
// 3. NORMALIZATION
// ============================================================================

function normalizeLettersOnly(text) {
    validateText(text);

    return [...text]
        .filter(character => /^[A-Za-z]$/.test(character))
        .map(character => character.toLowerCase())
        .join("");
}


function normalizeUnicodeLetters(text) {
    validateText(text);

    /*
     * Unicode property escapes allow JavaScript to identify letters beyond
     * ASCII when the runtime supports modern ECMAScript.
     */
    return [...text]
        .filter(character => /^\p{L}$/u.test(character))
        .map(character => character.toLocaleLowerCase())
        .join("");
}


// ============================================================================
// 4. MOST FREQUENT CHARACTER
// ============================================================================

function mostFrequentCharacter(text) {
    validateText(text);

    if (text.length === 0) {
        return null;
    }

    const frequency = countCharactersObject(text);

    let bestCharacter = null;
    let bestCount = -1;

    /*
     * Iterating through the original text preserves first-occurrence
     * tie-breaking.
     */
    for (const character of text) {
        if (frequency[character] > bestCount) {
            bestCharacter = character;
            bestCount = frequency[character];
        }
    }

    return {
        character: bestCharacter,
        count: bestCount
    };
}


// ============================================================================
// 5. DUPLICATE AND UNIQUE CHARACTERS
// ============================================================================

function duplicateCharacters(text) {
    const frequency = countCharactersMap(text);
    const result = new Map();

    for (const [character, count] of frequency) {
        if (count > 1) {
            result.set(character, count);
        }
    }

    return result;
}


function uniqueCharacters(text) {
    const frequency = countCharactersMap(text);
    const result = new Map();

    for (const [character, count] of frequency) {
        if (count === 1) {
            result.set(character, count);
        }
    }

    return result;
}


function firstNonRepeatingCharacter(text) {
    const frequency = countCharactersMap(text);

    for (const character of text) {
        if (frequency.get(character) === 1) {
            return character;
        }
    }

    return null;
}


function firstRepeatingCharacter(text) {
    validateText(text);

    const seen = new Set();

    for (const character of text) {
        if (seen.has(character)) {
            return character;
        }

        seen.add(character);
    }

    return null;
}


// ============================================================================
// 6. FREQUENCY COMPARISON
// ============================================================================

function frequencyMapsEqual(textA, textB) {
    const first = countCharactersMap(textA);
    const second = countCharactersMap(textB);

    if (first.size !== second.size) {
        return false;
    }

    for (const [character, count] of first) {
        if (second.get(character) !== count) {
            return false;
        }
    }

    return true;
}


function areAnagrams(textA, textB) {
    const normalizedA = normalizeLettersOnly(textA);
    const normalizedB = normalizeLettersOnly(textB);

    return frequencyMapsEqual(normalizedA, normalizedB);
}


function frequencyDifference(textA, textB) {
    const result = countCharactersMap(textA);

    for (const character of textB) {
        result.set(character, (result.get(character) || 0) - 1);
    }

    /*
     * Remove zero entries so the result describes only actual differences.
     */
    for (const [character, count] of result) {
        if (count === 0) {
            result.delete(character);
        }
    }

    return result;
}


// ============================================================================
// 7. CHARACTER GROUPING
// ============================================================================

function groupCharactersByFrequency(text) {
    const frequency = countCharactersMap(text);
    const groups = new Map();

    for (const [character, count] of frequency) {
        if (!groups.has(count)) {
            groups.set(count, []);
        }

        groups.get(count).push(character);
    }

    for (const characters of groups.values()) {
        characters.sort();
    }

    return new Map(
        [...groups.entries()].sort((a, b) => a[0] - b[0])
    );
}


function charactersSortedByFrequency(text) {
    const frequency = countCharactersMap(text);

    return [...frequency.entries()].sort(
        (first, second) =>
            second[1] - first[1] ||
            first[0].localeCompare(second[0])
    );
}


// ============================================================================
// 8. UNICODE CODE-POINT CONSIDERATIONS
// ============================================================================

function unicodeCodePointFrequency(text) {
    /*
     * for...of iterates Unicode code points rather than UTF-16 code units.
     * This means an emoji such as 😀 is treated as one iteration element.
     *
     * It still does not fully solve grapheme-cluster counting. A human-
     * perceived character can consist of multiple code points.
     */
    return countCharactersMap(text);
}


// ============================================================================
// 9. SLIDING WINDOW: LONGEST UNIQUE SUBSTRING
// ============================================================================

function longestSubstringWithoutRepeatingCharacters(text) {
    validateText(text);

    const lastSeen = new Map();

    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    const characters = [...text];

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        if (lastSeen.has(character) && lastSeen.get(character) >= left) {
            left = lastSeen.get(character) + 1;
        }

        lastSeen.set(character, right);

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestLength = currentLength;
            bestStart = left;
        }
    }

    return characters.slice(bestStart, bestStart + bestLength).join("");
}


// ============================================================================
// 10. MINIMUM WINDOW WITH REQUIRED FREQUENCIES
// ============================================================================

function minimumWindowWithRequiredCharacters(text, required) {
    validateText(text);
    validateText(required);

    if (required.length === 0) {
        return "";
    }

    const requiredCounts = countCharactersMap(required);
    const windowCounts = new Map();

    let formed = 0;
    const requiredKinds = requiredCounts.size;

    let left = 0;
    let bestStart = 0;
    let bestLength = Infinity;

    const characters = [...text];

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        windowCounts.set(
            character,
            (windowCounts.get(character) || 0) + 1
        );

        if (
            requiredCounts.has(character) &&
            windowCounts.get(character) === requiredCounts.get(character)
        ) {
            formed++;
        }

        while (formed === requiredKinds && left <= right) {
            const currentLength = right - left + 1;

            if (currentLength < bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }

            const leftCharacter = characters[left];
            const newCount = windowCounts.get(leftCharacter) - 1;

            windowCounts.set(leftCharacter, newCount);

            if (
                requiredCounts.has(leftCharacter) &&
                newCount < requiredCounts.get(leftCharacter)
            ) {
                formed--;
            }

            left++;
        }
    }

    return bestLength === Infinity
        ? null
        : characters.slice(bestStart, bestStart + bestLength).join("");
}


// ============================================================================
// 11. ANAGRAM SIGNATURES AND GROUPING
// ============================================================================

function frequencySignature(text) {
    const frequency = countCharactersMap(text);

    return [...frequency.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([character, count]) => `${character}:${count}`)
        .join("|");
}


function groupAnagrams(words) {
    const groups = new Map();

    for (const word of words) {
        const signature = frequencySignature(word);

        if (!groups.has(signature)) {
            groups.set(signature, []);
        }

        groups.get(signature).push(word);
    }

    return groups;
}


// ============================================================================
// 12. VALIDATION
// ============================================================================

function validateText(value) {
    if (typeof value !== "string") {
        throw new TypeError("Expected a string.");
    }
}


// ============================================================================
// 13. DISPLAY HELPERS
// ============================================================================

function mapToObject(map) {
    return Object.fromEntries(map);
}


function displayFrequencyMap(map) {
    const object = mapToObject(map);

    for (const [character, count] of Object.entries(object)) {
        const displayCharacter =
            character === " "
                ? "<space>"
                : character === "\t"
                    ? "<tab>"
                    : character;

        console.log(`${JSON.stringify(displayCharacter).padEnd(12)} -> ${count}`);
    }
}


// ============================================================================
// 14. TESTING
// ============================================================================

function assertEqual(name, actual, expected) {
    const actualJSON = JSON.stringify(actual);
    const expectedJSON = JSON.stringify(expected);

    if (actualJSON !== expectedJSON) {
        throw new Error(
            `${name} failed: expected ${expectedJSON}, got ${actualJSON}`
        );
    }

    console.log(`PASS: ${name}`);
}


function runTests() {
    assertEqual(
        "basic counting",
        countCharactersObject("banana"),
        { b: 1, a: 3, n: 2 }
    );

    assertEqual(
        "empty string",
        countCharactersObject(""),
        {}
    );

    assertEqual(
        "most frequent",
        mostFrequentCharacter("swiss"),
        { character: "s", count: 3 }
    );

    assertEqual(
        "first non-repeating",
        firstNonRepeatingCharacter("swiss"),
        "w"
    );

    assertEqual(
        "first repeating",
        firstRepeatingCharacter("swiss"),
        "s"
    );

    assertEqual(
        "frequency comparison",
        frequencyMapsEqual("aabbcc", "ccbbaa"),
        true
    );

    assertEqual(
        "anagram comparison",
        areAnagrams("Dormitory", "Dirty room"),
        true
    );

    assertEqual(
        "frequency difference",
        mapToObject(frequencyDifference("aab", "ab")),
        { a: 1 }
    );

    assertEqual(
        "grouping",
        mapToObject(groupCharactersByFrequency("banana")),
        {
            1: ["b"],
            2: ["n"],
            3: ["a"]
        }
    );

    assertEqual(
        "longest unique substring",
        longestSubstringWithoutRepeatingCharacters("abcabcbb"),
        "abc"
    );

    assertEqual(
        "minimum window",
        minimumWindowWithRequiredCharacters("ADOBECODEBANC", "ABC"),
        "BANC"
    );

    try {
        countCharactersObject(123);
        throw new Error("Validation should have rejected a number.");
    } catch (error) {
        if (!(error instanceof TypeError)) {
            throw error;
        }

        console.log("PASS: input validation");
    }
}


// ============================================================================
// 15. MAIN DEMONSTRATION
// ============================================================================

function main() {
    console.log("=".repeat(72));
    console.log("DAY 21 — CHARACTER FREQUENCY");
    console.log("=".repeat(72));

    const text = "banana";

    console.log("\n1. Object frequency:");
    console.log(countCharactersObject(text));

    console.log("\n2. Map frequency:");
    displayFrequencyMap(countCharactersMap(text));

    console.log("\n3. Frequency array:");
    const array = lowercaseFrequencyArray(text);
    console.log(array);
    console.log(frequencyArrayToObject(array));

    console.log("\n4. Most frequent:");
    console.log(mostFrequentCharacter(text));

    console.log("\n5. Duplicate characters:");
    displayFrequencyMap(duplicateCharacters(text));

    console.log("\n6. Unique characters:");
    displayFrequencyMap(uniqueCharacters(text));

    console.log("\n7. First non-repeating:");
    console.log(firstNonRepeatingCharacter("swiss"));

    console.log("\n8. First repeating:");
    console.log(firstRepeatingCharacter("swiss"));

    console.log("\n9. Frequency comparison:");
    console.log(frequencyMapsEqual("listen", "silent"));

    console.log("\n10. Anagram comparison:");
    console.log(areAnagrams("The eyes", "They see"));

    console.log("\n11. Frequency difference:");
    displayFrequencyMap(frequencyDifference("aabbc", "abcc"));

    console.log("\n12. Grouped characters:");
    console.log(
        mapToObject(groupCharactersByFrequency(text))
    );

    console.log("\n13. Sorted by frequency:");
    console.log(charactersSortedByFrequency(text));

    console.log("\n14. Unicode code-point frequency:");
    displayFrequencyMap(unicodeCodePointFrequency("😀😀café"));

    console.log("\n15. Longest unique substring:");
    console.log(
        longestSubstringWithoutRepeatingCharacters("abcabcbb")
    );

    console.log("\n16. Minimum required-character window:");
    console.log(
        minimumWindowWithRequiredCharacters("ADOBECODEBANC", "ABC")
    );

    console.log("\n17. Anagram groups:");
    console.log(
        [...groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"]).values()]
    );

    console.log("\n18. Case and punctuation normalization:");
    console.log(normalizeLettersOnly("Hello, World! 123"));

    console.log("\n" + "=".repeat(72));
    console.log("TESTS");
    console.log("=".repeat(72));

    runTests();
}


if (typeof require !== "undefined" && require.main === module) {
    main();
}
