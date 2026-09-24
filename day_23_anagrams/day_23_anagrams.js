/*
 * Day 23 — Anagrams
 * ==================
 *
 * Comprehensive JavaScript study implementation covering:
 *
 * - Anagram definitions
 * - Sorting-based checking
 * - Frequency-map checking
 * - Map and object character counting
 * - Unicode considerations
 * - Normalization
 * - Grouping anagrams
 * - Anagram detection
 * - Sliding-window anagram search
 * - Frequency matching
 * - Streaming-style frequency updates
 * - Edge cases
 * - Validation
 * - Testing
 * - Performance comparisons
 *
 * The file uses standard JavaScript APIs only.
 */


"use strict";


// ============================================================================
// 1. OUTPUT HELPERS
// ============================================================================

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}


function printResult(label, value) {
    console.log(`${label.padEnd(42)}:`, value);
}


// ============================================================================
// 2. NORMALIZATION
// ============================================================================

function normalizeLettersOnly(text) {
    /*
     * Unicode-aware normalization:
     * \p{L} matches Unicode letters and \p{N} matches Unicode numbers.
     * casefolding is not a native JavaScript operation, so toLocaleLowerCase
     * is used as a practical lowercase normalization step.
     */
    return Array.from(text)
        .filter(character => /[\p{L}\p{N}]/u.test(character))
        .join("")
        .toLocaleLowerCase();
}


function normalizeAsciiLetters(text) {
    return Array.from(text)
        .filter(character => /[A-Za-z]/.test(character))
        .join("")
        .toLowerCase();
}


function demonstrateNormalization() {
    printSection("1. Normalization");

    const samples = [
        "Listen",
        "Rail Safety!",
        "Dormitory",
        "The Eyes",
        "A gentleman",
        "你好",
        "São Paulo"
    ];

    for (const sample of samples) {
        console.log(
            sample.padEnd(20),
            "-> Unicode:",
            normalizeLettersOnly(sample).padEnd(20),
            "| ASCII:",
            normalizeAsciiLetters(sample)
        );
    }
}


// ============================================================================
// 3. SORTING-BASED ANAGRAM CHECKING
// ============================================================================

function areAnagramsSorting(first, second, normalize = false) {
    if (normalize) {
        first = normalizeLettersOnly(first);
        second = normalizeLettersOnly(second);
    }

    if (first.length !== second.length) {
        return false;
    }

    /*
     * JavaScript strings do not have a native sorted-string operation.
     * Array.from handles Unicode code points more safely than split(""),
     * although grapheme clusters can still require more specialized handling.
     */
    return Array.from(first).sort().join("") ===
           Array.from(second).sort().join("");
}


function demonstrateSorting() {
    printSection("2. Sorting-Based Checking");

    const testCases = [
        ["listen", "silent"],
        ["triangle", "integral"],
        ["apple", "papel"],
        ["rat", "car"],
        ["", ""],
        ["a", "A"]
    ];

    for (const [first, second] of testCases) {
        printResult(
            `${JSON.stringify(first)} vs ${JSON.stringify(second)}`,
            areAnagramsSorting(first, second)
        );
    }

    printResult(
        "Dormitory vs Dirty room",
        areAnagramsSorting("Dormitory", "Dirty room", true)
    );

    printResult(
        "The eyes vs They see",
        areAnagramsSorting("The eyes", "They see", true)
    );
}


// ============================================================================
// 4. OBJECT FREQUENCY MAP
// ============================================================================

function characterFrequencyObject(text) {
    const frequencies = Object.create(null);

    for (const character of text) {
        frequencies[character] = (frequencies[character] || 0) + 1;
    }

    return frequencies;
}


function areAnagramsObject(first, second, normalize = false) {
    if (normalize) {
        first = normalizeLettersOnly(first);
        second = normalizeLettersOnly(second);
    }

    const firstCharacters = Array.from(first);
    const secondCharacters = Array.from(second);

    if (firstCharacters.length !== secondCharacters.length) {
        return false;
    }

    const frequencies = characterFrequencyObject(first);

    for (const character of second) {
        if (!frequencies[character]) {
            return false;
        }

        frequencies[character] -= 1;

        if (frequencies[character] === 0) {
            delete frequencies[character];
        }
    }

    return Object.keys(frequencies).length === 0;
}


// ============================================================================
// 5. MAP FREQUENCY IMPLEMENTATION
// ============================================================================

function characterFrequencyMap(text) {
    const frequencies = new Map();

    for (const character of text) {
        frequencies.set(character, (frequencies.get(character) || 0) + 1);
    }

    return frequencies;
}


function mapsEqual(first, second) {
    if (first.size !== second.size) {
        return false;
    }

    for (const [key, value] of first) {
        if (second.get(key) !== value) {
            return false;
        }
    }

    return true;
}


function areAnagramsMap(first, second, normalize = false) {
    if (normalize) {
        first = normalizeLettersOnly(first);
        second = normalizeLettersOnly(second);
    }

    if (Array.from(first).length !== Array.from(second).length) {
        return false;
    }

    return mapsEqual(
        characterFrequencyMap(first),
        characterFrequencyMap(second)
    );
}


function demonstrateFrequencyMaps() {
    printSection("3. Frequency Maps");

    const cases = [
        ["listen", "silent"],
        ["anagram", "nagaram"],
        ["hello", "world"],
        ["aabbcc", "abcabc"],
        ["aabb", "abab"],
        ["aab", "abb"]
    ];

    for (const [first, second] of cases) {
        console.log(
            `${JSON.stringify(first)} vs ${JSON.stringify(second)} ->`,
            "Object:",
            areAnagramsObject(first, second),
            "| Map:",
            areAnagramsMap(first, second)
        );
    }

    console.log(
        "mississippi:",
        Object.fromEntries(characterFrequencyMap("mississippi"))
    );
}


// ============================================================================
// 6. FIXED ASCII FREQUENCY ARRAY
// ============================================================================

function areAnagramsAsciiArray(first, second) {
    first = first.toLowerCase();
    second = second.toLowerCase();

    const firstCharacters = Array.from(first);
    const secondCharacters = Array.from(second);

    if (firstCharacters.length !== secondCharacters.length) {
        return false;
    }

    const frequencies = new Int32Array(26);

    for (const character of firstCharacters) {
        if (!/[a-z]/.test(character)) {
            throw new TypeError(
                `Unsupported character ${JSON.stringify(character)}; expected a-z.`
            );
        }

        frequencies[character.charCodeAt(0) - 97] += 1;
    }

    for (const character of secondCharacters) {
        if (!/[a-z]/.test(character)) {
            throw new TypeError(
                `Unsupported character ${JSON.stringify(character)}; expected a-z.`
            );
        }

        frequencies[character.charCodeAt(0) - 97] -= 1;
    }

    return frequencies.every(value => value === 0);
}


// ============================================================================
// 7. GROUP ANAGRAMS
// ============================================================================

function groupAnagramsBySorting(words) {
    const groups = new Map();

    for (const word of words) {
        const key = Array.from(word).sort().join("");

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(word);
    }

    return Array.from(groups.values());
}


function createAsciiFrequencyKey(word) {
    const frequencies = new Int32Array(26);

    for (const character of word.toLowerCase()) {
        if (!/[a-z]/.test(character)) {
            throw new TypeError(
                `Unsupported character ${JSON.stringify(character)}.`
            );
        }

        frequencies[character.charCodeAt(0) - 97] += 1;
    }

    return frequencies.join(",");
}


function groupAnagramsByFrequency(words) {
    const groups = new Map();

    for (const word of words) {
        const key = createAsciiFrequencyKey(word);

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(word);
    }

    return Array.from(groups.values());
}


function demonstrateGrouping() {
    printSection("4. Grouping Anagrams");

    const words = [
        "eat",
        "tea",
        "tan",
        "ate",
        "nat",
        "bat",
        "listen",
        "silent",
        "enlist"
    ];

    console.log("Sorting groups:");
    console.log(groupAnagramsBySorting(words));

    console.log("\nFrequency groups:");
    console.log(groupAnagramsByFrequency(words));
}


// ============================================================================
// 8. ANAGRAM PAIRS
// ============================================================================

function findAnagramPairs(words) {
    const groups = groupAnagramsBySorting(words);
    const pairs = [];

    for (const group of groups) {
        for (let firstIndex = 0; firstIndex < group.length; firstIndex++) {
            for (
                let secondIndex = firstIndex + 1;
                secondIndex < group.length;
                secondIndex++
            ) {
                pairs.push([
                    group[firstIndex],
                    group[secondIndex]
                ]);
            }
        }
    }

    return pairs;
}


// ============================================================================
// 9. SLIDING-WINDOW ANAGRAM SEARCH
// ============================================================================

function mapsHaveSameFrequencies(first, second) {
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


function findAnagramWindows(text, pattern) {
    const patternCharacters = Array.from(pattern);
    const textCharacters = Array.from(text);

    if (patternCharacters.length === 0) {
        return [];
    }

    if (patternCharacters.length > textCharacters.length) {
        return [];
    }

    const patternCounts = characterFrequencyMap(pattern);
    const windowCounts = new Map();
    const result = [];
    const windowSize = patternCharacters.length;

    for (let index = 0; index < windowSize; index++) {
        const character = textCharacters[index];
        windowCounts.set(
            character,
            (windowCounts.get(character) || 0) + 1
        );
    }

    if (mapsHaveSameFrequencies(windowCounts, patternCounts)) {
        result.push(0);
    }

    for (let right = windowSize; right < textCharacters.length; right++) {
        const enteringCharacter = textCharacters[right];
        const leavingCharacter = textCharacters[right - windowSize];

        windowCounts.set(
            enteringCharacter,
            (windowCounts.get(enteringCharacter) || 0) + 1
        );

        const leavingCount = windowCounts.get(leavingCharacter) - 1;

        if (leavingCount === 0) {
            windowCounts.delete(leavingCharacter);
        } else {
            windowCounts.set(leavingCharacter, leavingCount);
        }

        if (mapsHaveSameFrequencies(windowCounts, patternCounts)) {
            result.push(right - windowSize + 1);
        }
    }

    return result;
}


// ============================================================================
// 10. OPTIMIZED ASCII SLIDING WINDOW
// ============================================================================

function findAnagramWindowsOptimized(text, pattern) {
    text = text.toLowerCase();
    pattern = pattern.toLowerCase();

    const textCharacters = Array.from(text);
    const patternCharacters = Array.from(pattern);

    if (patternCharacters.length === 0) {
        return [];
    }

    if (patternCharacters.length > textCharacters.length) {
        return [];
    }

    for (const character of textCharacters) {
        if (!/[a-z]/.test(character)) {
            throw new TypeError(
                "Optimized implementation accepts ASCII letters only."
            );
        }
    }

    for (const character of patternCharacters) {
        if (!/[a-z]/.test(character)) {
            throw new TypeError(
                "Optimized implementation accepts ASCII letters only."
            );
        }
    }

    const patternCounts = new Int32Array(26);
    const windowCounts = new Int32Array(26);

    for (const character of patternCharacters) {
        patternCounts[character.charCodeAt(0) - 97]++;
    }

    for (let index = 0; index < patternCharacters.length; index++) {
        const character = textCharacters[index];
        windowCounts[character.charCodeAt(0) - 97]++;
    }

    let matches = 0;

    for (let index = 0; index < 26; index++) {
        if (patternCounts[index] === windowCounts[index]) {
            matches++;
        }
    }

    const result = [];
    const windowSize = patternCharacters.length;

    if (matches === 26) {
        result.push(0);
    }

    function update(index, delta) {
        const beforeEqual = patternCounts[index] === windowCounts[index];

        windowCounts[index] += delta;

        const afterEqual = patternCounts[index] === windowCounts[index];

        if (beforeEqual && !afterEqual) {
            matches--;
        } else if (!beforeEqual && afterEqual) {
            matches++;
        }
    }

    for (let right = windowSize; right < textCharacters.length; right++) {
        const enteringIndex =
            textCharacters[right].charCodeAt(0) - 97;

        const leavingIndex =
            textCharacters[right - windowSize].charCodeAt(0) - 97;

        update(enteringIndex, 1);
        update(leavingIndex, -1);

        if (matches === 26) {
            result.push(right - windowSize + 1);
        }
    }

    return result;
}


function demonstrateSlidingWindow() {
    printSection("5. Anagram Windows");

    const cases = [
        ["cbaebabacd", "abc"],
        ["abab", "ab"],
        ["baa", "aa"],
        ["abcdef", "xyz"],
        ["aaaaa", "aa"]
    ];

    for (const [text, pattern] of cases) {
        console.log(
            `text=${JSON.stringify(text)}, pattern=${JSON.stringify(pattern)} ->`,
            findAnagramWindows(text, pattern)
        );
    }

    console.log(
        "Optimized:",
        findAnagramWindowsOptimized("cbaebabacd", "abc")
    );
}


// ============================================================================
// 11. FREQUENCY DIFFERENCE
// ============================================================================

function frequencyDifference(first, second) {
    const difference = new Map();

    for (const character of first) {
        difference.set(
            character,
            (difference.get(character) || 0) + 1
        );
    }

    for (const character of second) {
        difference.set(
            character,
            (difference.get(character) || 0) - 1
        );
    }

    for (const [character, count] of difference) {
        if (count === 0) {
            difference.delete(character);
        }
    }

    return difference;
}


function containsPermutation(text, pattern) {
    return findAnagramWindows(text, pattern).length > 0;
}


// ============================================================================
// 12. REUSABLE FREQUENCY MAP CLASS
// ============================================================================

class FrequencyMap {
    constructor(values = []) {
        this.counts = new Map();

        for (const value of values) {
            this.add(value);
        }
    }

    add(value) {
        this.counts.set(
            value,
            (this.counts.get(value) || 0) + 1
        );
    }

    remove(value) {
        if (!this.counts.has(value)) {
            throw new Error(
                `Cannot remove absent value ${JSON.stringify(value)}.`
            );
        }

        const nextCount = this.counts.get(value) - 1;

        if (nextCount === 0) {
            this.counts.delete(value);
        } else {
            this.counts.set(value, nextCount);
        }
    }

    get(value) {
        return this.counts.get(value) || 0;
    }

    equals(other) {
        return mapsHaveSameFrequencies(this.counts, other.counts);
    }

    toObject() {
        return Object.fromEntries(this.counts);
    }
}


// ============================================================================
// 13. ANAGRAM INDEX
// ============================================================================

class AnagramIndex {
    constructor(words = []) {
        this.groups = new Map();

        for (const word of words) {
            this.add(word);
        }
    }

    createKey(word) {
        const normalized = normalizeLettersOnly(word);
        return Array.from(normalized).sort().join("");
    }

    add(word) {
        const key = this.createKey(word);

        if (!this.groups.has(key)) {
            this.groups.set(key, []);
        }

        this.groups.get(key).push(word);
    }

    find(word) {
        return this.groups.get(this.createKey(word)) || [];
    }
}


// ============================================================================
// 14. EDGE CASES
// ============================================================================

function demonstrateEdgeCases() {
    printSection("6. Edge Cases");

    const cases = [
        ["", ""],
        ["", "a"],
        ["a", ""],
        ["a", "a"],
        ["a", "A"],
        ["aa", "a"],
        ["abc", "abcd"],
        ["a b", "ab"],
        ["😊", "😊"],
        ["é", "e"],
        ["ß", "ss"]
    ];

    for (const [first, second] of cases) {
        console.log(
            JSON.stringify(first).padEnd(10),
            "vs",
            JSON.stringify(second).padEnd(10),
            "exact=",
            areAnagramsMap(first, second),
            "normalized=",
            areAnagramsMap(first, second, true)
        );
    }
}


// ============================================================================
// 15. TESTING
// ============================================================================

function runTests() {
    printSection("7. Automated Tests");

    const positiveCases = [
        ["listen", "silent"],
        ["triangle", "integral"],
        ["evil", "vile"],
        ["anagram", "nagaram"],
        ["aabbcc", "abcabc"],
        ["", ""]
    ];

    const negativeCases = [
        ["hello", "world"],
        ["abc", "abd"],
        ["a", "aa"],
        ["abc", "abcd"]
    ];

    for (const [first, second] of positiveCases) {
        console.assert(
            areAnagramsSorting(first, second),
            `Sorting failed: ${first}, ${second}`
        );

        console.assert(
            areAnagramsObject(first, second),
            `Object failed: ${first}, ${second}`
        );

        console.assert(
            areAnagramsMap(first, second),
            `Map failed: ${first}, ${second}`
        );
    }

    for (const [first, second] of negativeCases) {
        console.assert(
            !areAnagramsSorting(first, second),
            `Sorting negative case failed: ${first}, ${second}`
        );

        console.assert(
            !areAnagramsObject(first, second),
            `Object negative case failed: ${first}, ${second}`
        );

        console.assert(
            !areAnagramsMap(first, second),
            `Map negative case failed: ${first}, ${second}`
        );
    }

    console.assert(
        areAnagramsAsciiArray("listen", "silent"),
        "ASCII array positive test failed."
    );

    console.assert(
        !areAnagramsAsciiArray("listen", "silentx"),
        "ASCII array negative test failed."
    );

    console.assert(
        JSON.stringify(findAnagramWindows("cbaebabacd", "abc")) ===
        JSON.stringify([0, 6]),
        "Sliding-window test failed."
    );

    console.assert(
        JSON.stringify(findAnagramWindows("abab", "ab")) ===
        JSON.stringify([0, 1, 2]),
        "Repeated-window test failed."
    );

    console.assert(
        JSON.stringify(findAnagramWindows("", "a")) ===
        JSON.stringify([]),
        "Empty-text test failed."
    );

    console.assert(
        JSON.stringify(findAnagramWindows("abc", "")) ===
        JSON.stringify([]),
        "Empty-pattern test failed."
    );

    console.assert(
        JSON.stringify(findAnagramWindowsOptimized("cbaebabacd", "abc")) ===
        JSON.stringify([0, 6]),
        "Optimized sliding-window test failed."
    );

    console.log("All JavaScript assertions completed.");
}


// ============================================================================
// 16. ERROR HANDLING
// ============================================================================

function demonstrateErrors() {
    printSection("8. Error Handling");

    try {
        areAnagramsAsciiArray("hello!", "olleh!");
    } catch (error) {
        printResult("Expected ASCII validation error", error.message);
    }

    try {
        groupAnagramsByFrequency(["eat", "tea", "é"]);
    } catch (error) {
        printResult("Expected grouping validation error", error.message);
    }

    const frequencies = new FrequencyMap("abc");

    try {
        frequencies.remove("z");
    } catch (error) {
        printResult("Expected frequency-map error", error.message);
    }
}


// ============================================================================
// 17. PERFORMANCE BENCHMARK
// ============================================================================

function benchmarkMethods() {
    printSection("9. Performance Benchmark");

    const first = "abcdefghijklmnopqrstuvwxyz".repeat(2000);
    const second = Array.from(first).reverse().join("");

    const methods = [
        [
            "Sorting",
            () => areAnagramsSorting(first, second)
        ],
        [
            "Object frequency",
            () => areAnagramsObject(first, second)
        ],
        [
            "Map frequency",
            () => areAnagramsMap(first, second)
        ]
    ];

    for (const [name, method] of methods) {
        const start = performance.now();
        const result = method();
        const elapsed = performance.now() - start;

        console.log(
            `${String(name).padEnd(20)} result=${String(result).padEnd(6)} ` +
            `time=${elapsed.toFixed(4)} ms`
        );
    }
}


// ============================================================================
// 18. PRACTICAL CASE STUDY
// ============================================================================

function buildAnagramSignatures(values) {
    const result = new Map();

    for (const value of values) {
        const normalized = normalizeLettersOnly(value);
        const signature = Array.from(normalized).sort().join("");

        if (!result.has(signature)) {
            result.set(signature, []);
        }

        result.get(signature).push(value);
    }

    return result;
}


function demonstrateCaseStudy() {
    printSection("10. Practical Case Study: Text Record Matching");

    const records = [
        "Debit Card",
        "Credit Card",
        "Bad Credit",
        "Debitcard",
        "card debit",
        "Secure Login",
        "Login Secure"
    ];

    const signatures = buildAnagramSignatures(records);

    for (const [signature, values] of signatures) {
        if (values.length > 1) {
            console.log(`Signature ${JSON.stringify(signature)}:`);
            for (const value of values) {
                console.log(`  - ${value}`);
            }
        }
    }
}


// ============================================================================
// 19. COMPLEXITY
// ============================================================================

function demonstrateComplexity() {
    printSection("11. Complexity Reference");

    const complexities = {
        "Sorting-based pair check": "O(n log n) time, O(n) space",
        "Object frequency map": "O(n) average time, O(k) space",
        "Map frequency": "O(n) average time, O(k) space",
        "26-element array": "O(n) time, O(1) auxiliary space",
        "Grouping by sorting": "O(n × m log m)",
        "Grouping by fixed frequencies": "O(n × m)",
        "Naive pairwise detection": "O(n² × m)",
        "Sliding-window search": "O(n × k) with map comparison",
        "Optimized ASCII window": "O(n) time, O(1) auxiliary space"
    };

    for (const [technique, complexity] of Object.entries(complexities)) {
        console.log(`${technique.padEnd(42)}: ${complexity}`);
    }
}


// ============================================================================
// 20. MAIN
// ============================================================================

function main() {
    printSection("Day 23 — Anagrams");
    console.log(
        "Comprehensive executable study of sorting, frequency maps, " +
        "grouping, windows, and frequency matching."
    );

    demonstrateNormalization();
    demonstrateSorting();
    demonstrateFrequencyMaps();

    printSection("ASCII Array Demonstration");
    printResult(
        "'listen' and 'silent'",
        areAnagramsAsciiArray("listen", "silent")
    );
    printResult(
        "'rat' and 'car'",
        areAnagramsAsciiArray("rat", "car")
    );

    demonstrateGrouping();

    printSection("Anagram Pair Detection");
    const words = [
        "listen",
        "silent",
        "enlist",
        "stone",
        "tones",
        "apple"
    ];
    printResult("Pairs", findAnagramPairs(words));

    demonstrateSlidingWindow();

    printSection("Frequency Matching");
    printResult(
        "Difference of abbccc and abcc",
        Object.fromEntries(frequencyDifference("abbccc", "abcc"))
    );
    printResult(
        "Permutation exists",
        containsPermutation("oidbcaf", "abc")
    );

    printSection("FrequencyMap Class");
    const frequencyMap = new FrequencyMap("banana");
    printResult("Initial", frequencyMap.toObject());
    frequencyMap.remove("a");
    frequencyMap.add("x");
    printResult("After modification", frequencyMap.toObject());

    printSection("Anagram Index");
    const index = new AnagramIndex([
        "listen",
        "silent",
        "enlist",
        "stone",
        "tones",
        "python",
        "typhon"
    ]);

    for (const query of ["listen", "tones", "python", "unknown"]) {
        printResult(query, index.find(query));
    }

    demonstrateEdgeCases();
    demonstrateErrors();
    runTests();
    benchmarkMethods();
    demonstrateCaseStudy();
    demonstrateComplexity();

    printSection("Program Completed");
    console.log("All demonstrations and tests completed.");
}


main();
