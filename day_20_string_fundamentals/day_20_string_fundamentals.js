"use strict";

/*
 * Day 20 — String Fundamentals
 * =============================
 *
 * Topics:
 * - Characters
 * - Indexing
 * - Traversal
 * - Concatenation
 * - Comparison
 * - Conversion
 * - Case conversion
 *
 * Practice:
 * - Reverse string
 * - Count characters
 * - Remove spaces
 * - Change case
 * - Count vowels
 * - Find first unique character
 * - Count words
 *
 * The examples progress from basic JavaScript string operations to
 * validation, Unicode-aware traversal, frequency analysis, and a complete
 * text-analysis case study.
 */


// ---------------------------------------------------------------------------
// 1. Characters and strings
// ---------------------------------------------------------------------------

function demonstrateCharacters() {
    console.log("\n=== 1. Characters and strings ===");

    const character = "A";
    const word = "JavaScript";
    const sentence = "String fundamentals are important.";

    console.log("Character:", character);
    console.log("Word:", word);
    console.log("Sentence:", sentence);

    // JavaScript has no separate built-in char type.
    // A single character is represented by a string with one UTF-16 code unit.
    console.log("Character type:", typeof character);
    console.log("Character length:", character.length);
    console.log("Word length:", word.length);

    const unicodeText = "café भारत 日本";
    console.log("Unicode text:", unicodeText);
    console.log("UTF-16 code-unit length:", unicodeText.length);

    // Array.from() iterates Unicode code points more appropriately than
    // direct indexing for many Unicode characters.
    console.log("Code-point characters:", Array.from(unicodeText));
}


// ---------------------------------------------------------------------------
// 2. Indexing and slicing
// ---------------------------------------------------------------------------

function demonstrateIndexingAndSlicing() {
    console.log("\n=== 2. Indexing and slicing ===");

    const text = "JAVASCRIPT";

    console.log("Text:", text);
    console.log("Index 0:", text[0]);
    console.log("Index 1:", text[1]);
    console.log("Index 9:", text[9]);

    // JavaScript supports bracket indexing and at().
    console.log("Last character with at(-1):", text.at(-1));

    // slice() does not modify the original string.
    console.log("First four:", text.slice(0, 4));
    console.log("From index 4:", text.slice(4));
    console.log("Last three:", text.slice(-3));

    // Out-of-range indexing produces undefined rather than throwing.
    console.log("Out-of-range index:", text[100]);

    // Direct character assignment does not mutate a primitive string.
    let value = "hello";
    value[0] = "H";
    console.log("After attempted direct assignment:", value);
}


// ---------------------------------------------------------------------------
// 3. Traversal
// ---------------------------------------------------------------------------

function demonstrateTraversal() {
    console.log("\n=== 3. String traversal ===");

    const text = "Code";

    console.log("for...of traversal:");
    for (const character of text) {
        console.log(character);
    }

    console.log("Index-based traversal:");
    for (let index = 0; index < text.length; index += 1) {
        console.log(index, text[index]);
    }

    console.log("Array.from().forEach():");
    Array.from(text).forEach((character, index) => {
        console.log(index, character);
    });
}


// ---------------------------------------------------------------------------
// 4. Concatenation
// ---------------------------------------------------------------------------

function demonstrateConcatenation() {
    console.log("\n=== 4. Concatenation ===");

    const firstName = "Atul";
    const lastName = "Pandey";

    const usingPlus = firstName + " " + lastName;
    console.log("Using +:", usingPlus);

    const age = 25;
    const usingTemplateLiteral = `${usingPlus} is ${age} years old.`;
    console.log("Using template literal:", usingTemplateLiteral);

    const words = ["JavaScript", "strings", "are", "immutable"];
    console.log("Using join():", words.join(" "));

    console.log("Repetition:", "ha".repeat(3));
}


// ---------------------------------------------------------------------------
// 5. Comparison
// ---------------------------------------------------------------------------

function demonstrateComparison() {
    console.log("\n=== 5. String comparison ===");

    console.log('"apple" === "apple":', "apple" === "apple");
    console.log('"apple" === "Apple":', "apple" === "Apple");
    console.log('"apple" !== "orange":', "apple" !== "orange");

    // String relational operators use lexicographic comparison based on
    // UTF-16 code units.
    console.log('"apple" < "banana":', "apple" < "banana");
    console.log('"cat" > "car":', "cat" > "car");

    const first = "JavaScript";
    const second = "javascript";

    console.log("Case-sensitive equality:", first === second);
    console.log(
        "Case-insensitive equality:",
        first.toLocaleLowerCase() === second.toLocaleLowerCase()
    );
}


// ---------------------------------------------------------------------------
// 6. Conversion and case conversion
// ---------------------------------------------------------------------------

function demonstrateConversionAndCase() {
    console.log("\n=== 6. Conversion and case conversion ===");

    const number = 12345;
    const numberAsString = String(number);
    console.log("Number:", number);
    console.log("Converted to string:", numberAsString);

    const numericText = "987";
    const convertedNumber = Number(numericText);
    console.log("String:", numericText);
    console.log("Converted to number:", convertedNumber);

    const text = "jAvAsCrIpT programming";

    console.log("Original:", text);
    console.log("Uppercase:", text.toUpperCase());
    console.log("Lowercase:", text.toLowerCase());
    console.log(
        "Capitalized:",
        text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
    );
}


// ---------------------------------------------------------------------------
// 7. Practice functions
// ---------------------------------------------------------------------------

function reverseString(text) {
    return Array.from(text).reverse().join("");
}


function reverseStringManually(text) {
    const characters = Array.from(text);
    const reversed = [];

    for (let index = characters.length - 1; index >= 0; index -= 1) {
        reversed.push(characters[index]);
    }

    return reversed.join("");
}


function countCharacters(text) {
    // Array.from() counts Unicode code points more usefully than .length
    // for characters represented by surrogate pairs.
    return Array.from(text).length;
}


function countUtf16CodeUnits(text) {
    return text.length;
}


function characterFrequency(text, ignoreCase = false) {
    const source = ignoreCase ? text.toLocaleLowerCase() : text;
    const frequencies = new Map();

    for (const character of source) {
        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );
    }

    return Object.fromEntries(frequencies);
}


function removeSpaces(text) {
    // \s includes spaces, tabs, line breaks, and other whitespace.
    return text.replace(/\s/g, "");
}


function removeLiteralSpaces(text) {
    return text.replace(/ /g, "");
}


function changeCase(text, mode) {
    switch (mode) {
        case "upper":
            return text.toUpperCase();

        case "lower":
            return text.toLowerCase();

        case "capitalize":
            return text.length === 0
                ? text
                : text[0].toUpperCase() + text.slice(1).toLowerCase();

        case "title":
            return text.replace(
                /\S+/g,
                word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            );

        case "swapcase":
            return Array.from(text)
                .map(character => {
                    const upper = character.toUpperCase();
                    const lower = character.toLowerCase();

                    if (character === upper && character !== lower) {
                        return lower;
                    }

                    return upper;
                })
                .join("");

        default:
            throw new Error(
                "Unsupported case mode. Use upper, lower, capitalize, title, or swapcase."
            );
    }
}


function countVowels(text) {
    const vowels = new Set(["a", "e", "i", "o", "u"]);
    let count = 0;

    for (const character of text.toLocaleLowerCase()) {
        if (vowels.has(character)) {
            count += 1;
        }
    }

    return count;
}


function countVowelsAndConsonants(text) {
    const vowels = new Set(["a", "e", "i", "o", "u"]);
    let vowelCount = 0;
    let consonantCount = 0;

    for (const character of text.toLocaleLowerCase()) {
        if (!/^[a-z]$/.test(character)) {
            continue;
        }

        if (vowels.has(character)) {
            vowelCount += 1;
        } else {
            consonantCount += 1;
        }
    }

    return { vowelCount, consonantCount };
}


function firstUniqueCharacter(text) {
    const frequencies = new Map();

    for (const character of text) {
        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );
    }

    for (const character of text) {
        if (frequencies.get(character) === 1) {
            return character;
        }
    }

    return null;
}


function firstUniqueCharacterIgnoreCase(text) {
    const normalizedCharacters = Array.from(text, character =>
        character.toLocaleLowerCase()
    );

    const frequencies = new Map();

    for (const character of normalizedCharacters) {
        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );
    }

    for (let index = 0; index < normalizedCharacters.length; index += 1) {
        if (frequencies.get(normalizedCharacters[index]) === 1) {
            return Array.from(text)[index];
        }
    }

    return null;
}


function countWords(text) {
    const trimmed = text.trim();

    if (trimmed === "") {
        return 0;
    }

    return trimmed.split(/\s+/u).length;
}


function countWordsManually(text) {
    let count = 0;
    let insideWord = false;

    for (const character of text) {
        if (/\s/u.test(character)) {
            insideWord = false;
        } else if (!insideWord) {
            count += 1;
            insideWord = true;
        }
    }

    return count;
}


// ---------------------------------------------------------------------------
// 8. Validation and normalization
// ---------------------------------------------------------------------------

function validateNonEmpty(text) {
    if (typeof text !== "string") {
        throw new TypeError("Expected a string.");
    }

    if (text.trim().length === 0) {
        throw new Error("String must not be empty or whitespace-only.");
    }

    return text;
}


function normalizeWhitespace(text) {
    return text.trim().replace(/\s+/gu, " ");
}


function isPalindrome(text) {
    const normalized = Array.from(text.toLocaleLowerCase())
        .filter(character => /[\p{L}\p{N}]/u.test(character))
        .join("");

    return normalized === reverseString(normalized);
}


function safeNumberFromString(text) {
    if (typeof text !== "string") {
        return null;
    }

    const trimmed = text.trim();

    if (trimmed === "") {
        return null;
    }

    const number = Number(trimmed);

    return Number.isFinite(number) ? number : null;
}


// ---------------------------------------------------------------------------
// 9. Advanced analysis
// ---------------------------------------------------------------------------

function longestWord(text) {
    const words = text.trim() === "" ? [] : text.trim().split(/\s+/u);

    if (words.length === 0) {
        return "";
    }

    return words.reduce(
        (longest, word) => word.length > longest.length ? word : longest,
        ""
    );
}


function mostCommonCharacter(text, ignoreWhitespace = true) {
    const frequencies = new Map();

    for (const character of text) {
        if (ignoreWhitespace && /\s/u.test(character)) {
            continue;
        }

        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );
    }

    let mostCommon = null;
    let highestFrequency = 0;

    for (const [character, frequency] of frequencies) {
        if (frequency > highestFrequency) {
            mostCommon = character;
            highestFrequency = frequency;
        }
    }

    return mostCommon === null
        ? null
        : { character: mostCommon, count: highestFrequency };
}


function characterClasses(text) {
    const result = {
        letters: 0,
        digits: 0,
        whitespace: 0,
        punctuationOrSymbols: 0
    };

    for (const character of text) {
        if (/\p{L}/u.test(character)) {
            result.letters += 1;
        } else if (/\p{N}/u.test(character)) {
            result.digits += 1;
        } else if (/\s/u.test(character)) {
            result.whitespace += 1;
        } else {
            result.punctuationOrSymbols += 1;
        }
    }

    return result;
}


function findAllOccurrences(text, target) {
    if (target === "") {
        throw new Error("Target must not be empty.");
    }

    const positions = [];
    let start = 0;

    while (true) {
        const position = text.indexOf(target, start);

        if (position === -1) {
            break;
        }

        positions.push(position);
        start = position + 1;
    }

    return positions;
}


// ---------------------------------------------------------------------------
// 10. Text-analysis case study
// ---------------------------------------------------------------------------

class TextAnalyzer {
    constructor(text) {
        validateNonEmpty(text);
        this.text = text;
    }

    analyze() {
        const { vowelCount, consonantCount } =
            countVowelsAndConsonants(this.text);

        return {
            original: this.text,
            characterCount: countCharacters(this.text),
            utf16CodeUnitCount: countUtf16CodeUnits(this.text),
            characterCountWithoutSpaces: countCharacters(removeSpaces(this.text)),
            wordCount: countWords(this.text),
            vowelCount,
            consonantCount,
            firstUniqueCharacter: firstUniqueCharacter(this.text),
            longestWord: longestWord(this.text),
            mostCommonCharacter: mostCommonCharacter(this.text),
            palindrome: isPalindrome(this.text),
            normalized: normalizeWhitespace(this.text),
            characterClasses: characterClasses(this.text),
            frequencies: characterFrequency(this.text, true)
        };
    }
}


function printAnalysis(analysis) {
    console.log("\n=== Text analysis case study ===");
    console.log("Original:", analysis.original);
    console.log("Character count:", analysis.characterCount);
    console.log("UTF-16 code-unit count:", analysis.utf16CodeUnitCount);
    console.log(
        "Characters without spaces:",
        analysis.characterCountWithoutSpaces
    );
    console.log("Word count:", analysis.wordCount);
    console.log("Vowel count:", analysis.vowelCount);
    console.log("Consonant count:", analysis.consonantCount);
    console.log("First unique character:", analysis.firstUniqueCharacter);
    console.log("Longest word:", analysis.longestWord);
    console.log("Most common character:", analysis.mostCommonCharacter);
    console.log("Palindrome:", analysis.palindrome);
    console.log("Normalized:", analysis.normalized);
    console.log("Character classes:", analysis.characterClasses);
    console.log("Frequencies:", analysis.frequencies);
}


// ---------------------------------------------------------------------------
// 11. Tests
// ---------------------------------------------------------------------------

function runTests() {
    console.log("\n=== Practice tests ===");

    console.assert(reverseString("JavaScript") === "tpircSavaJ");
    console.assert(reverseString("") === "");
    console.assert(reverseStringManually("abc") === "cba");

    console.assert(countCharacters("hello") === 5);
    console.assert(countCharacters("") === 0);

    console.assert(removeSpaces("a b c") === "abc");
    console.assert(removeSpaces("a\tb\nc") === "abc");

    console.assert(changeCase("javascript", "upper") === "JAVASCRIPT");
    console.assert(changeCase("JAVASCRIPT", "lower") === "javascript");

    console.assert(countVowels("education") === 5);
    console.assert(countVowels("") === 0);

    console.assert(firstUniqueCharacter("swiss") === "w");
    console.assert(firstUniqueCharacter("aabb") === null);

    console.assert(countWords("one two three") === 3);
    console.assert(countWords("  one   two\tthree\n") === 3);
    console.assert(countWords("") === 0);

    console.assert(normalizeWhitespace("  JavaScript   is\tgreat ") ===
        "JavaScript is great");

    console.assert(isPalindrome("level"));
    console.assert(isPalindrome("A man, a plan, a canal: Panama"));
    console.assert(!isPalindrome("JavaScript"));

    const positions = findAllOccurrences("banana", "ana");
    console.assert(
        positions.length === 2 &&
        positions[0] === 1 &&
        positions[1] === 3
    );

    console.assert(safeNumberFromString("42") === 42);
    console.assert(safeNumberFromString("not-a-number") === null);

    console.log("All tests passed.");
}


// ---------------------------------------------------------------------------
// 12. Edge cases
// ---------------------------------------------------------------------------

function demonstrateEdgeCases() {
    console.log("\n=== Edge cases ===");

    const examples = [
        "",
        " ",
        "   ",
        "12345",
        "!@#$%",
        "A1 B2 C3",
        "café",
        "भारत",
        "hello\nworld",
        "hello\tworld",
        "😀 JavaScript"
    ];

    for (const text of examples) {
        console.log(JSON.stringify(text), "=>", {
            codePointLength: countCharacters(text),
            utf16Length: countUtf16CodeUnits(text),
            words: countWords(text),
            vowels: countVowels(text),
            classes: characterClasses(text)
        });
    }

    try {
        changeCase("hello", "unsupported");
    } catch (error) {
        console.log("Invalid case mode handled:", error.message);
    }

    try {
        validateNonEmpty("   ");
    } catch (error) {
        console.log("Empty-content validation handled:", error.message);
    }

    try {
        findAllOccurrences("abc", "");
    } catch (error) {
        console.log("Empty search target handled:", error.message);
    }
}


// ---------------------------------------------------------------------------
// 13. Performance principles
// ---------------------------------------------------------------------------

function demonstratePerformancePrinciples() {
    console.log("\n=== Performance considerations ===");

    const parts = Array.from(
        { length: 10 },
        (_, index) => `item-${index}`
    );

    const joined = parts.join("");

    let repeatedConcatenation = "";
    for (const part of parts) {
        repeatedConcatenation += part;
    }

    console.log("join() result:", joined);
    console.log("Repeated + result:", repeatedConcatenation);
    console.log("Results equal:", joined === repeatedConcatenation);

    console.log(
        "Frequency counting:",
        characterFrequency("banana")
    );
}


// ---------------------------------------------------------------------------
// 14. Main program
// ---------------------------------------------------------------------------

function main() {
    console.log("=".repeat(72));
    console.log("DAY 20 — STRING FUNDAMENTALS");
    console.log("=".repeat(72));

    demonstrateCharacters();
    demonstrateIndexingAndSlicing();
    demonstrateTraversal();
    demonstrateConcatenation();
    demonstrateComparison();
    demonstrateConversionAndCase();

    console.log("\n=== Practice problem demonstrations ===");

    const sample = "JavaScript String Fundamentals";

    console.log("Original:", sample);
    console.log("Reverse:", reverseString(sample));
    console.log("Manual reverse:", reverseStringManually(sample));
    console.log("Character count:", countCharacters(sample));
    console.log("Without spaces:", removeSpaces(sample));
    console.log("Uppercase:", changeCase(sample, "upper"));
    console.log("Lowercase:", changeCase(sample, "lower"));
    console.log("Vowels:", countVowels(sample));
    console.log(
        "First unique character:",
        firstUniqueCharacter(sample)
    );
    console.log("Word count:", countWords(sample));
    console.log(
        "Frequency:",
        characterFrequency(sample, true)
    );

    demonstratePerformancePrinciples();

    const analyzer = new TextAnalyzer(
        "JavaScript makes text processing flexible, expressive, and practical."
    );

    printAnalysis(analyzer.analyze());

    demonstrateEdgeCases();
    runTests();

    console.log("\n=== Study checklist ===");

    const checklist = [
        "Characters",
        "Indexing",
        "Traversal",
        "Concatenation",
        "Comparison",
        "Conversion",
        "Case conversion",
        "Reverse string",
        "Count characters",
        "Remove spaces",
        "Change case",
        "Count vowels",
        "First unique character",
        "Count words"
    ];

    for (const item of checklist) {
        console.log("[x]", item);
    }

    console.log("\nDay 20 string fundamentals completed.");
}


main();
